"""Read-only channel data and owner Analytics with local OAuth credentials."""
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/yt-analytics.readonly',
          'https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube']


class ChannelError(ValueError):
    pass


def request_json(url, params=None, headers=None):
    if params:
        url += '?' + urlencode(params)
    try:
        with urlopen(Request(url, headers=headers or {}), timeout=30) as response:
            return json.load(response)
    except HTTPError as e:
        raise ChannelError(f'YouTube HTTP {e.code}: kiểm tra quyền kênh, API đã bật và hạn mức.') from None
    except (URLError, TimeoutError, ValueError):
        raise ChannelError('Không đọc được YouTube; kiểm tra kết nối mạng hoặc phản hồi API.') from None


def write_private(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix('.tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as output:
        output.write(content)
    os.chmod(temp, 0o600)
    temp.replace(path)


class ChannelClient:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.pending = None

    @property
    def token_path(self):
        return self.directory / 'google-token.json'

    def readiness(self):
        return {'api_key': bool(os.environ.get('YOUTUBE_API_KEY')),
                'llm_key': bool(os.environ.get('OPENCODE_API_KEY')),
                'oauth_client': bool(os.environ.get('GOOGLE_OAUTH_CLIENT_FILE') and
                                     Path(os.environ['GOOGLE_OAUTH_CLIENT_FILE']).is_file()),
                'owner_connected': self.token_path.is_file()}

    def authorize(self, port):
        client = os.environ.get('GOOGLE_OAUTH_CLIENT_FILE')
        if not client or not Path(client).is_file():
            raise ChannelError('Đặt GOOGLE_OAUTH_CLIENT_FILE tới file OAuth Client loại Desktop trong máy này. Không nhập nội dung file vào chat.')
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(client, scopes=SCOPES, autogenerate_code_verifier=True)
        flow.redirect_uri = f'http://127.0.0.1:{port}/oauth/callback'
        url, state = flow.authorization_url(access_type='offline', prompt='consent')
        self.pending = {'flow': flow, 'state': state, 'expires': time.time()+600}
        return url

    def finish_authorization(self, code, state):
        pending = self.pending
        if not pending or pending['expires'] < time.time() or not secrets.compare_digest(pending['state'], state):
            raise ChannelError('Phiên kết nối đã hết hạn hoặc không hợp lệ. Hãy kết nối lại.')
        self.pending = None
        if not code:
            raise ChannelError('Bạn chưa cấp quyền Google. Có thể kết nối lại khi sẵn sàng.')
        try:
            # State was verified above. Token exchange remains HTTPS with TLS verification.
            pending['flow'].fetch_token(code=code)
            credentials = pending['flow'].credentials
            if credentials.granted_scopes and not set(SCOPES).issubset(credentials.granted_scopes):
                raise ChannelError('Cần cho phép đọc YouTube, Analytics và upload cho chiến dịch tự vận hành.')
            write_private(self.token_path, credentials.to_json())
        except ChannelError:
            raise
        except Exception:
            raise ChannelError('Không hoàn tất OAuth. Kiểm tra ứng dụng Google, tài khoản và quyền được cấp.') from None

    def credentials(self):
        if not self.token_path.exists():
            return None
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request as GoogleRequest
        try:
            # Refresh only scopes actually granted. Newly requested scopes belong
            # to the next consent flow and must not invalidate existing access.
            credentials = Credentials.from_authorized_user_file(str(self.token_path))
            if not credentials.valid:
                if not credentials.refresh_token:
                    raise ChannelError('Cần kết nối lại tài khoản chủ kênh.')
                credentials.refresh(GoogleRequest())
                write_private(self.token_path, credentials.to_json())
            return credentials
        except ChannelError:
            raise
        except Exception:
            raise ChannelError('Phiên Google không còn dùng được. Hãy kết nối lại tài khoản chủ kênh.') from None

    def disconnect(self):
        # Removes local access; users can additionally revoke app access in their Google account.
        self.token_path.unlink(missing_ok=True)
        self.pending = None

    def collect(self, settings):
        key = os.environ.get('YOUTUBE_API_KEY')
        credentials = self.credentials()
        if not key and not credentials:
            raise ChannelError('Cần YOUTUBE_API_KEY hoặc kết nối chủ kênh để đọc số liệu thật.')
        headers = {'Authorization': f'Bearer {credentials.token}'} if credentials else {'X-Goog-Api-Key': key}
        def data(resource, params):
            return request_json('https://www.googleapis.com/youtube/v3/'+resource, params, headers)
        channel_data = data('channels', {'part': 'snippet,statistics,contentDetails',
                                        'forHandle': settings['channel_handle']})
        channels = channel_data.get('items', [])
        if not channels:
            raise ChannelError('Không tìm thấy kênh; kiểm tra channel_handle.')
        channel = channels[0]
        if credentials:
            owned = data('channels', {'part': 'id', 'mine': 'true'}).get('items', [])
            if channel['id'] not in {v['id'] for v in owned}:
                raise ChannelError('Tài khoản OAuth không phải chủ kênh đang cấu hình. Chọn đúng kênh/Brand Account rồi kết nối lại.')
        uploads = channel.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        ids, pages, next_page = [], 0, None
        while uploads and pages < 2:
            params = {'part': 'contentDetails', 'playlistId': uploads, 'maxResults': 50}
            if next_page:
                params['pageToken'] = next_page
            page = data('playlistItems', params)
            ids.extend(v['contentDetails']['videoId'] for v in page.get('items', []))
            pages += 1
            next_page = page.get('nextPageToken')
            if not next_page:
                break
        videos = []
        for offset in range(0, len(ids), 50):
            detail = data('videos', {'part': 'snippet,statistics,contentDetails', 'id': ','.join(ids[offset:offset+50])})
            for video in detail.get('items', []):
                snippet = video.get('snippet', {})
                videos.append({'id': video['id'], 'title': snippet.get('title', ''),
                               'published_at': snippet.get('publishedAt'), 'tags': snippet.get('tags', []),
                               'statistics': video.get('statistics', {}),
                               'duration': video.get('contentDetails', {}).get('duration')})
        competitors = []
        for niche in settings['niche_seeds'][:3]:
            found = data('search', {'part': 'snippet', 'type': 'video', 'q': niche,
                                   'maxResults': 5, 'relevanceLanguage': 'vi', 'regionCode': 'VN'})
            related_ids = [v['id']['videoId'] for v in found.get('items', []) if v.get('id', {}).get('videoId')]
            if related_ids:
                related = data('videos', {'part': 'snippet,statistics', 'id': ','.join(related_ids)})
                for v in related.get('items', []):
                    sn = v.get('snippet', {})
                    if sn.get('channelId') != channel['id']:
                        competitors.append({'id': v['id'], 'title': sn.get('title', ''), 'niche_query': niche,
                                            'published_at': sn.get('publishedAt'), 'statistics': v.get('statistics', {})})
        # Preserve unique sources; public search is a sample, never called a trend measurement.
        competitors = list({v['id']: v for v in competitors}.values())
        analytics = {'status': 'not_connected', 'ctr': None,
                     'note': 'Kết nối chủ kênh để xem lượt xem theo kỳ, thời lượng xem và nguồn truy cập. CTR chưa được tích hợp.'}
        if credentials:
            end = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()-timedelta(days=2)
            start = end-timedelta(days=27)
            base = {'ids': 'channel=='+channel['id'], 'startDate': start.isoformat(), 'endDate': end.isoformat()}
            metrics = 'views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost'
            def analytics_query(extra):
                return request_json('https://youtubeanalytics.googleapis.com/v2/reports', {**base, **extra}, headers)
            try:
                summary = analytics_query({'metrics': metrics})
                by_video = analytics_query({'metrics': 'views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage',
                                             'dimensions': 'video', 'sort': '-views', 'maxResults': 20})
                traffic = analytics_query({'metrics': 'views,estimatedMinutesWatched', 'dimensions': 'insightTrafficSourceType'})
                analytics = {'status': 'ok', 'start': start.isoformat(), 'end': end.isoformat(),
                             'summary': table_rows(summary), 'videos': table_rows(by_video),
                             'traffic': table_rows(traffic), 'ctr': None,
                             'note': 'Kỳ 28 ngày kết thúc trước hôm nay 2 ngày để giảm dữ liệu chưa hoàn tất. CTR chưa được tích hợp.'}
            except ChannelError as error:
                analytics = {'status': 'error', 'note': str(error), 'ctr': None}
        return {'channel': {'id': channel['id'], 'title': channel.get('snippet', {}).get('title', ''),
                            'statistics': channel.get('statistics', {})},
                'videos': videos, 'videos_truncated': bool(next_page), 'competitors': competitors, 'analytics': analytics}


def table_rows(data):
    columns = [c['name'] for c in data.get('columnHeaders', [])]
    return [dict(zip(columns, row)) for row in data.get('rows', [])]
