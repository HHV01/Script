"""Bounded campaign upload; preserve an uncertain attempt instead of duplicating uploads."""
import json
import hashlib
import time
from pathlib import Path

from .common import ROOT, need, load_yaml, CONFIG
from .script_review import require_approval, digest, write_json

UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'


def upload(project):
    from studio.channel import ChannelClient, request_json
    from google.auth.transport.requests import AuthorizedSession

    campaign = project.cfg.get('campaign', {})
    need(campaign.get('auto_upload') is True, 'Chưa bật quyền đăng tự động cho dự án.')
    need(time.time() < float(campaign.get('ends_at', 0)), 'Chiến dịch đã hết hạn; không đăng thêm.')
    # Retain project-level duplicate protection even after legacy folders are removed.
    ledger_path = ROOT / '.studio/manager/publication-ledger.json'
    if ledger_path.exists():
        try:
            ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
            videos = ledger['videos']
            if not isinstance(videos, list) or any(not isinstance(v, dict) for v in videos):
                raise ValueError('invalid publication list')
        except (OSError, ValueError, KeyError, TypeError):
            raise SystemExit('Hồ sơ chống trùng không đọc được; dừng upload để đối soát.')
        existing = next((v for v in videos if v.get('project') == getattr(project, 'name', None)
                         and v.get('project') and v.get('video_id')), None)
        need(not existing, 'Dự án đã có trong hồ sơ video đã đăng; không upload lại.')
    require_approval(project)
    need(project.final.is_file(), 'Chưa có video hoàn chỉnh.')
    client = ChannelClient(ROOT / '.studio/manager')
    stored = json.loads(client.token_path.read_text(encoding='utf-8'))
    need(UPLOAD_SCOPE in stored.get('scopes', []),
         'Cần kết nối chủ kênh lại một lần để cấp thêm quyền upload.')
    quality_path = project.dir / 'video-quality.json'
    from . import qc
    report = qc.run(project)
    need(report['approved'], 'Kiểm duyệt chưa đạt: ' + '; '.join(report['blockers'][:3]))
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    with project.final.open('rb') as video:
        video_hash = hashlib.file_digest(video, 'sha256').hexdigest()
    need(quality.get('approved') is True and quality.get('video_sha256') == video_hash,
         'Phiếu kiểm tra thành phẩm chưa đạt hoặc không khớp video hiện tại.')
    credentials = client.credentials()
    headers = {'Authorization': 'Bearer ' + credentials.token}
    owned = request_json('https://www.googleapis.com/youtube/v3/channels',
                         {'part': 'id,statistics', 'mine': 'true'}, headers).get('items', [])
    expected = campaign.get('channel_id')
    need(expected and len(owned) == 1 and owned[0]['id'] == expected,
         'Tài khoản upload không khớp kênh chiến dịch.')
    subscribers = owned[0].get('statistics', {}).get('subscriberCount')
    need(subscribers is not None, 'Không đọc được số đăng ký để kiểm tra mục tiêu.')
    need(int(subscribers) < int(campaign['target_subscribers']), 'Đã đạt mục tiêu; không đăng thêm.')
    receipt = project.dir / 'youtube-upload.json'
    if receipt.exists():
        previous = json.loads(receipt.read_text(encoding='utf-8'))
        need(previous.get('status') == 'uploaded',
             'Lượt upload trước chưa xác định kết quả; cần đối chiếu Studio trước khi thử lại.')
        print('[upload] Đã đăng: https://www.youtube.com/watch?v=' + previous['video_id'])
        return previous
    metadata = json.loads((project.dir / 'publish.json').read_text(encoding='utf-8'))
    # A local receipt alone cannot detect uploads made by another worker or tool.
    channel_info = request_json('https://www.googleapis.com/youtube/v3/channels',
        {'part': 'contentDetails', 'id': expected}, headers).get('items', [])
    need(channel_info, 'Không đối chiếu được danh sách video để chống đăng trùng.')
    playlist = channel_info[0]['contentDetails']['relatedPlaylists']['uploads']
    recent = request_json('https://www.googleapis.com/youtube/v3/playlistItems',
        {'part': 'snippet', 'playlistId': playlist, 'maxResults': 50}, headers).get('items', [])
    normalized = lambda title: ' '.join(title.casefold().split())
    duplicates = [v for v in recent if normalized(v['snippet']['title']) == normalized(metadata['title'])]
    need(not duplicates, 'Kênh đã có video cùng tiêu đề; đối chiếu bản đã đăng trước khi tạo upload mới.')
    disclosure = metadata.get('production_disclosure') or 'Hình minh họa tái dựng bằng AI; giọng đọc tổng hợp. Các cảnh là minh họa, không phải phim tư liệu.'
    description = metadata['description'][:4700] + '\n\n' + disclosure
    payload = {'snippet': {'title': metadata['title'], 'description': description,
                           'tags': metadata['tags'], 'categoryId': '27', 'defaultLanguage': 'vi'},
               'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False,
                          'containsSyntheticMedia': True}}
    session = AuthorizedSession(credentials)
    response = session.post('https://www.googleapis.com/upload/youtube/v3/videos',
        params={'uploadType': 'resumable', 'part': 'snippet,status'}, json=payload,
        headers={'X-Upload-Content-Type': 'video/mp4',
                 'X-Upload-Content-Length': str(project.final.stat().st_size)}, timeout=60)
    need(response.ok and response.headers.get('Location'),
         f'Không khởi tạo được upload: HTTP {response.status_code}.')
    write_json(receipt, {'status': 'uploading', 'started_at': time.time(),
                        'script_sha256': digest(project.script.read_text(encoding='utf-8'))})
    with project.final.open('rb') as video:
        result = session.put(response.headers['Location'], data=video,
            headers={'Content-Type': 'video/mp4', 'Content-Length': str(project.final.stat().st_size)}, timeout=600)
    need(result.ok, f'Upload HTTP {result.status_code}; giữ phiếu upload để tránh đăng trùng.')
    body = result.json()
    need(body.get('id'), 'Upload chưa trả video ID; cần đối chiếu Studio.')
    saved = {'status': 'uploaded', 'video_id': body['id'], 'uploaded_at': time.time(),
             'visibility': body.get('status', {}).get('privacyStatus', 'unknown')}
    write_json(receipt, saved)
    print('[upload] https://www.youtube.com/watch?v=' + body['id'] + ' · ' + saved['visibility'])
    return saved
