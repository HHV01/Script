"""Bounded public YouTube research. API key is sent in a header, never logged."""
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .common import load_env


def research(project):
    cfg = project.settings.get('youtube', {})
    if not cfg.get('research', False):
        return {'status': 'disabled', 'videos': []}
    load_env()
    key = os.environ.get('YOUTUBE_API_KEY')
    if not key:
        raise SystemExit('Bật youtube.research cần YOUTUBE_API_KEY trong môi trường hoặc .env (không commit).')

    def get(resource, params):
        req = Request('https://www.googleapis.com/youtube/v3/' + resource + '?' + urlencode(params),
                      headers={'X-Goog-Api-Key': key})
        try:
            with urlopen(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as e:
            raise SystemExit(f'YouTube API HTTP {e.code}: kiểm tra Data API v3, hạn mức và quyền API key.') from None
        except (URLError, TimeoutError):
            raise SystemExit('Không kết nối được YouTube API; kiểm tra mạng và thử lại.') from None

    own_channel = None
    handle = cfg.get('channel_handle', '').strip()
    if handle:
        channel_data = get('channels', {'part': 'snippet,statistics,contentDetails', 'forHandle': handle})
        channels = channel_data.get('items', [])
        if not channels:
            raise SystemExit('Không tìm thấy channel_handle; kiểm tra handle YouTube trong cấu hình.')
        channel = channels[0]
        uploads = channel.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        recent = []
        if uploads:
            entries = get('playlistItems', {'part': 'contentDetails', 'playlistId': uploads, 'maxResults': 10})
            recent_ids = [v['contentDetails']['videoId'] for v in entries.get('items', [])]
            if recent_ids:
                recent = get('videos', {'part': 'snippet,statistics,contentDetails', 'id': ','.join(recent_ids)}).get('items', [])
        own_channel = {'id': channel['id'], 'title': channel.get('snippet', {}).get('title', ''),
                       'statistics': channel.get('statistics', {}),
                       'recent_videos': [{'id': v['id'], 'title': v.get('snippet', {}).get('title', ''),
                           'published_at': v.get('snippet', {}).get('publishedAt', ''),
                           'statistics': v.get('statistics', {})} for v in recent]}

    query = f"{project.cfg.get('niche', '')} {project.cfg['topic']}".strip()
    results = get('search', {'part': 'snippet', 'type': 'video', 'q': query,
                            'maxResults': max(1, min(10, int(cfg.get('max_results', 5)))),
                            'regionCode': cfg.get('region', 'VN'),
                            'relevanceLanguage': cfg.get('language', 'vi')})
    ids = [v['id']['videoId'] for v in results.get('items', []) if v.get('id', {}).get('videoId')]
    if not ids:
        return {'status': 'ok', 'query': query, 'channel': own_channel, 'videos': []}
    details = get('videos', {'part': 'snippet,statistics,contentDetails', 'id': ','.join(ids)})
    videos = []
    for v in details.get('items', []):
        sn = v.get('snippet', {})
        videos.append({'id': v['id'], 'title': sn.get('title', ''),
                       'published_at': sn.get('publishedAt', ''),
                       'tags': sn.get('tags', []), 'statistics': v.get('statistics', {}),
                       'duration': v.get('contentDetails', {}).get('duration')})
    return {'status': 'ok', 'query': query, 'videos': videos, 'channel': own_channel,
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'limitations': 'Dữ liệu công khai không cung cấp CTR hay retention; lượt xem không chứng minh quan hệ nhân quả.'}


def review_research(project, force=False, now=None):
    """Dated recent-upload samples; never equate lifetime views/day with a trend."""
    import hashlib
    import math
    from datetime import datetime, timedelta, timezone
    cfg = project.settings.get('review', {})
    now = now or datetime.now(timezone.utc)
    window = max(1, min(90, int(cfg.get('recent_days', 30))))
    ttl = max(1, min(72, float(cfg.get('research_max_age_hours', 24))))
    query = ' '.join(str(project.cfg.get('topic', '')).split())[:180]
    niche = ' '.join(str(project.cfg.get('niche', project.cfg.get('topic', 'lịch sử'))).split())[:180]
    context = {'topic': query, 'niche': niche, 'days': window}
    key_hash = hashlib.sha256(json.dumps(context, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    path = project.dir / 'review_research.json'
    previous = None
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding='utf-8'))
            stamp = datetime.fromisoformat(previous['collected_at'])
            hours = (now-stamp).total_seconds()/3600
            if not force and previous.get('context_hash') == key_hash and 0 <= hours < ttl:
                return previous
        except (ValueError, KeyError, TypeError):
            previous = None
    load_env()
    key = os.environ.get('YOUTUBE_API_KEY')
    if not key:
        raise SystemExit('Duyệt kịch bản cần YOUTUBE_API_KEY để cập nhật mẫu video gần đây. Đặt key trong môi trường hoặc .env.')

    def get(resource, params):
        req = Request('https://www.googleapis.com/youtube/v3/'+resource+'?'+urlencode(params),
                      headers={'X-Goog-Api-Key': key})
        try:
            with urlopen(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            raise SystemExit(f'YouTube duyệt kịch bản HTTP {error.code}: kiểm tra API key, hạn mức và mạng.') from None
        except (URLError, TimeoutError, ValueError):
            raise SystemExit('Không cập nhật được dữ liệu YouTube để duyệt kịch bản; thử lại sau khi kiểm tra mạng.') from None
    since = (now-timedelta(days=window)).isoformat().replace('+00:00', 'Z')
    ids, samples = [], []
    for q, order in ((query, 'date'), (niche, 'viewCount')):
        found = get('search', {'part': 'snippet', 'type': 'video', 'q': q, 'order': order,
                               'publishedAfter': since, 'maxResults': 5, 'regionCode': 'VN', 'relevanceLanguage': 'vi'})
        batch = [v['id']['videoId'] for v in found.get('items', []) if v.get('id', {}).get('videoId')]
        samples.append({'query': q, 'order': order, 'video_ids': batch})
        ids.extend(batch)
    videos = []
    unique = list(dict.fromkeys(ids))
    old = {v['id']: v for v in (previous or {}).get('videos', [])} if (previous or {}).get('context_hash') == key_hash else {}
    elapsed = None
    if old:
        try:
            elapsed = (now-datetime.fromisoformat(previous['collected_at'])).total_seconds()/3600
        except (ValueError, KeyError):
            pass
    if unique:
        details = get('videos', {'part': 'snippet,statistics,contentDetails', 'id': ','.join(unique)})
        for v in details.get('items', []):
            sn, stats = v.get('snippet', {}), v.get('statistics', {})
            def integer(value):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return None
            views = integer(stats.get('viewCount'))
            age = None
            try:
                age = max(1, (now-datetime.fromisoformat(sn['publishedAt'].replace('Z', '+00:00'))).total_seconds()/3600)
            except (KeyError, ValueError, TypeError):
                pass
            baseline = old.get(v['id'], {}).get('views')
            videos.append({'id': v['id'], 'title': sn.get('title', ''), 'published_at': sn.get('publishedAt'),
                           'channel': sn.get('channelTitle', ''), 'views': views,
                           'likes': integer(stats.get('likeCount')), 'comments': integer(stats.get('commentCount')),
                           'duration': v.get('contentDetails', {}).get('duration'),
                           'views_per_day_since_publish': round(views/age*24, 2) if views is not None and age else None,
                           'view_change': views-baseline if elapsed and elapsed>0 and views is not None and baseline is not None else None,
                           'observation_hours': elapsed if elapsed and elapsed>0 and baseline is not None else None})
    result = {'context_hash': key_hash, 'collected_at': now.isoformat(),
              'expires_at': (now+timedelta(hours=ttl)).isoformat(), 'published_after': since,
              'samples': samples, 'videos': videos,
              'limits': 'Mẫu video mới trong cửa sổ thời gian, không phải bảng xu hướng toàn YouTube. '
                        'Views/ngày là trung bình từ ngày đăng; chỉ view_change có hai mốc mới là thay đổi quan sát. '
                        'Không có CTR, không xác minh sự kiện lịch sử hoặc phát hiện khảo cổ mới từ tiêu đề video.'}
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)
    return result
