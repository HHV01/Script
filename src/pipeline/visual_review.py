"""Evidence-based manual visual gate; technical probes cannot judge art direction."""
import hashlib
import json

CRITERIA = ('hook', 'character', 'composition', 'mechanism', 'motion', 'continuity', 'mobile_readability')


def inspect_references(project):
    try:
        data = json.loads((project.dir / 'visual-references.json').read_text(encoding='utf-8'))
        refs = data.get('videos', [])
        channels = set()
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            if (ref.get('watched_video') is True and ref.get('url', '').startswith('https://www.youtube.com/')
                    and ref.get('channel') and ref.get('observations') and ref.get('adaptation')
                    and ref.get('avoid_copying')):
                observations = ref['observations']
                if isinstance(observations, list) and all(isinstance(o, dict)
                        and isinstance(o.get('at_seconds'), (int, float)) and o['at_seconds'] >= 0
                        and isinstance(o.get('observation'), str) and o['observation'].strip()
                        for o in observations):
                    channels.add(ref['channel'])
        if len(channels) < 2:
            return False, 'Cần video đã xem từ ít nhất hai kênh, nhận xét timestamp và cách học không sao chép.'
        return True, 'Có hồ sơ tham khảo thị giác đã xem từ ít nhất hai kênh.'
    except (OSError, ValueError, TypeError, AttributeError):
        return False, 'Thiếu hồ sơ visual-references.json; metadata API không thay việc xem video.'


def inspect(project):
    path = project.dir / 'visual-review.json'
    try:
        review = json.loads(path.read_text(encoding='utf-8'))
        with project.final.open('rb') as video:
            current = hashlib.file_digest(video, 'sha256').hexdigest()
        if review.get('video_sha256') != current:
            return False, 'Phiếu duyệt hình không khớp video hiện tại.'
        if not review.get('reviewer') or not review.get('watched_full_video') or not review.get('mobile_preview_checked'):
            return False, 'Cần xem toàn bộ video và kiểm tra ở kích thước điện thoại.'
        criteria = review.get('criteria', {})
        failed = []
        for key in CRITERIA:
            item = criteria.get(key, {})
            evidence = item.get('evidence')
            if (item.get('passed') is not True or not isinstance(evidence, list)
                    or not evidence or not all(isinstance(e, dict)
                        and isinstance(e.get('at_seconds'), (int, float))
                        and e['at_seconds'] >= 0 and isinstance(e.get('observation'), str)
                        and e['observation'].strip() for e in evidence)):
                failed.append(key)
        if review.get('blockers') or review.get('approved') is not True or failed:
            return False, 'Chưa đạt duyệt hình: ' + ', '.join(failed or review.get('blockers') or ['chưa duyệt'])
        return True, 'Đã duyệt hình với nhận xét theo mốc thời gian cho đủ 7 tiêu chí.'
    except (OSError, ValueError, TypeError, AttributeError):
        return False, 'Thiếu hoặc lỗi visual-review.json; không tự suy ra hình đẹp từ điểm kỹ thuật.'
