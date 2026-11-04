"""Biên tập viên kênh: chấm điểm tiêu đề/mô tả/tag và kiểm tra video trước khi đăng.

Chạy hoàn toàn cục bộ (không gọi API, không tốn token). Kết quả ghi ra
publish-review.json (máy đọc) + publish-review.md (người đọc) và
video-quality.json (cổng chặn upload).
"""
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .branding import contains_brand
from .common import need

CTA_RE = re.compile(r'(đăng\s*k[ýí]|subscribe|theo\s*dõi\s*kênh|bấm\s*chuông|nhấn\s*chuông)', re.IGNORECASE)
CLICKBAIT = ('sốc', 'kinh hoàng', 'bạn sẽ không tin', 'chết người', 'không thể tin nổi',
             'gây sốt', 'cực hot', '100%', 'bí ẩn nhất')
CURIOSITY_RE = re.compile(r'(vì sao|tại sao|thế nào|ra sao|sự thật|bí mật|cơ thể|trí nhớ)', re.IGNORECASE)
SRT_TIME = re.compile(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)')

PASS, WARN, FAIL = 'pass', 'warn', 'fail'
ICON = {PASS: '✅', WARN: '⚠️', FAIL: '❌'}
TESTER = {'name': 'pipeline.qc (kiểm tra tự động)',
          'role': 'Thông số kỹ thuật và hồ sơ kiểm duyệt; không xem/nghe video'}


def _run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')


def _probe(path):
    result = _run(['ffprobe', '-v', 'error', '-print_format', 'json',
                   '-show_streams', '-show_format', str(path)])
    need(result.returncode == 0, f'ffprobe lỗi: {result.stderr[-300:]}')
    return json.loads(result.stdout or '{}')


def _volume(path, start=None, duration=None):
    """mean/max volume (dB) của toàn video hoặc một đoạn."""
    args = ['ffmpeg', '-hide_banner', '-nostats']
    if start is not None:
        args += ['-ss', f'{start:.2f}']
    args += ['-i', str(path)]
    if duration is not None:
        args += ['-t', f'{duration:.2f}']
    args += ['-vn', '-af', 'volumedetect', '-f', 'null', '-']
    result = _run(args)
    mean = re.search(r'mean_volume:\s*(-?[\d.]+) dB', result.stderr or '')
    peak = re.search(r'max_volume:\s*(-?[\d.]+) dB', result.stderr or '')
    return (float(mean.group(1)) if mean else None,
            float(peak.group(1)) if peak else None)


def _black_seconds(path, threshold=0.5):
    result = _run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-an',
                   '-vf', 'blackdetect=d=0.4:pix_th=0.10', '-f', 'null', '-'])
    spans = re.findall(r'black_start:([\d.]+)\s+black_end:([\d.]+)', result.stderr or '')
    return [round(float(end) - float(start), 2) for start, end in spans if float(end) - float(start) >= threshold]


def inspect_media(project):
    """Thông số kỹ thuật + độ to tiếng của video cuối."""
    path = project.final
    need(path.is_file(), 'Chưa có final.mp4 — chạy bước render trước.')
    probe = _probe(path)
    streams = probe.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    duration = float(probe.get('format', {}).get('duration') or 0)
    fps = 0.0
    if video and video.get('avg_frame_rate', '0/1') != '0/0':
        num, _, den = video['avg_frame_rate'].partition('/')
        fps = round(float(num) / float(den or 1), 2)
    mean, peak = _volume(path)
    head, _ = _volume(path, 0, 3)
    tail, _ = _volume(path, max(0.0, duration - 2.5), 2.5)
    return {
        'duration': round(duration, 2),
        'width': int(video.get('width') or 0) if video else 0,
        'height': int(video.get('height') or 0) if video else 0,
        'fps': fps,
        'video_codec': (video or {}).get('codec_name'),
        'audio_codec': (audio or {}).get('codec_name'),
        'audio_channels': (audio or {}).get('channels'),
        'bitrate_mbps': round(float(probe.get('format', {}).get('bit_rate') or 0) / 1e6, 2),
        'size_mb': round(path.stat().st_size / 1e6, 2),
        'mean_db': mean, 'peak_db': peak,
        'head_db': head, 'tail_db': tail,
        'black_spans': _black_seconds(path),
    }


def parse_srt(text):
    cues = []
    for block in re.split(r'\n\s*\n', (text or '').strip()):
        match = SRT_TIME.search(block)
        if not match:
            continue
        body = block[match.end():].strip('\n')
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
        cues.append({
            'start': h1 * 3600 + m1 * 60 + s1 + ms1 / 1000,
            'end': h2 * 3600 + m2 * 60 + s2 + ms2 / 1000,
            'lines': lines,
            'text': ' '.join(lines),
        })
    return cues


def inspect_subtitles(project, media):
    path = project.srt
    if not path.is_file():
        return {'exists': False, 'cues': 0, 'issues': ['Không có subtitles.srt']}
    cues = parse_srt(path.read_text(encoding='utf-8'))
    # Số ký tự vừa một dòng phụ thuộc cỡ chữ thật; đo theo khung 1080 và font đang dùng.
    font = float(project.settings.get('render', {}).get('subtitle_font_size') or 8)
    per_line = max(18, round((media['width'] or 1080) / (font * 3.4)))
    issues = []
    for index, cue in enumerate(cues, 1):
        if len(cue['lines']) > 2:
            issues.append(f'Câu {index}: {len(cue["lines"])} dòng (tối đa 2)')
        wrapped = 0
        for line in cue['lines']:
            wrapped += max(1, math.ceil(len(line) / per_line))
        if wrapped > 2:
            issues.append(f'Câu {index}: {len(cue["text"])} ký tự, sẽ chiếm {wrapped} dòng (tối đa 2)')
        if cue['start'] < 0 or cue['end'] <= cue['start']:
            issues.append(f'Câu {index}: mốc thời gian sai')
    if cues and media['duration'] and cues[-1]['end'] > media['duration'] + 1:
        issues.append(f'Phụ đề kết thúc {cues[-1]["end"]:.1f}s, dài hơn video {media["duration"]:.1f}s')
    margin = project.settings.get('render', {}).get('subtitle_margin_bottom')
    if margin is None or float(margin) < 15:
        issues.append(f'Lề dưới phụ đề {margin} quá sát mép (tối thiểu 15)')
    return {'exists': True, 'cues': len(cues), 'issues': issues, 'chars_per_line': per_line,
            'last_cue_end': round(cues[-1]['end'], 2) if cues else 0,
            'max_chars': max((len(c['text']) for c in cues), default=0)}


def _signature(path, size=16):
    """average-hash đơn giản để so khung hình cuối với thẻ kết."""
    from PIL import Image
    with Image.open(path) as image:
        grey = image.convert('L').resize((size, size))
        pixels = list(grey.getdata())
    avg = sum(pixels) / len(pixels)
    return [1 if pixel >= avg else 0 for pixel in pixels]


def _last_frame(path, at):
    import tempfile
    target = Path(tempfile.gettempdir()) / 'qc_last_frame.png'
    _run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max(0.0, at):.2f}',
          '-i', str(path), '-frames:v', '1', str(target)])
    return target if target.is_file() else None


def inspect_cta(project, media, meta):
    scenes = project.load_scenes()
    last = scenes[-1] if scenes else {}
    # The spoken invitation may precede a short goodbye scene.
    # Match script text in the final 30s; audio presence below is not speech recognition.
    tail_start = max(0.0, media['duration'] - 30)
    scene_text = ' '.join((scene.get('text') or '').strip() for scene in scenes
                          if float(scene.get('end', 0)) > tail_start)
    card = project.image_path(last) if last else None
    card_ok = bool(card and card.is_file())
    card_size = None
    if card_ok:
        from PIL import Image
        with Image.open(card) as image:
            card_size = image.size
    description = meta.get('description', '')
    shown = None
    if card_ok and media['duration'] > 1:
        frame = _last_frame(project.final, media['duration'] - 1)
        if frame:
            shown = sum(a != b for a, b in zip(_signature(frame), _signature(card)))
    return {
        'scene_has_cta': bool(CTA_RE.search(scene_text)),
        'scene_text': scene_text,
        'end_card': str(card) if card_ok else None,
        'end_card_ratio_ok': bool(card_size and abs(card_size[0] / card_size[1] - 16 / 9) < 0.02),
        'end_card_visible': shown is not None and shown <= 90,
        'end_card_distance': shown,
        'cta_audio_db': media['tail_db'],
        'description_has_cta': bool(CTA_RE.search(description)),
    }


def score_title(title, topic=''):
    """Chấm quy tắc biên tập tiêu đề; không dự báo lượt xem."""
    value = (title or '').strip()
    if not value:
        return {'score': 0, 'issues': ['Tiêu đề rỗng'], 'tips': []}
    score, issues, tips = 45, [], []
    length = len(value)
    if length > 100:
        score -= 45
        issues.append(f'Dài {length} ký tự, YouTube cắt ở 100')
    elif length < 25:
        score -= 25
        issues.append(f'Chỉ {length} ký tự, quá ngắn để gợi tò mò')
    elif 40 <= length <= 70:
        score += 18
    else:
        score -= 8
        tips.append(f'Dài {length} ký tự; khoảng 40–70 là đẹp trên điện thoại')
    if contains_brand(value):
        score -= 30
        issues.append('Chứa tên kênh trong tiêu đề')
    if CURIOSITY_RE.search(value):
        score += 8
    else:
        tips.append('Thêm câu hỏi/mở vòng ("Vì sao…", "Sự thật về…") để tăng tò mò')
    if re.search(r'\d', value):
        score += 3
    lowered = value.lower()
    for word in CLICKBAIT:
        if word in lowered:
            score -= 20
            issues.append(f'Có từ giật tít "{word}"')
    words = value.split()
    caps = sum(1 for word in words if len(word) > 2 and word.isupper())
    if caps and caps >= max(2, len(words) // 2):
        score -= 12
        issues.append('Quá nhiều chữ in hoa')
    if sum(1 for char in value if ord(char) > 0x2500) > 2:
        score -= 10
        tips.append('Bớt emoji/ký tự lạ, tiêu đề tiếng Việt dễ đọc hơn')
    keywords = [w for w in re.findall(r'\w+', (topic or '').lower()) if len(w) > 3]
    if keywords:
        hit = sum(1 for word in keywords if word in lowered)
        if hit >= 2:
            score += 6
        elif hit == 1:
            score += 2
        else:
            score -= 8
            tips.append('Đưa từ khóa chính của chủ đề vào nửa đầu tiêu đề')
    return {'score': max(0, min(100, score)), 'issues': issues, 'tips': tips}


def score_description(description, topic=''):
    value = (description or '').strip()
    score, issues, tips = 100, [], []
    if len(value) < 200:
        score -= 30
        issues.append(f'Mô tả chỉ {len(value)} ký tự; nên 300–1200 để đủ ngữ cảnh + từ khóa')
    elif len(value) > 1800:
        score -= 10
        tips.append('Mô tả dài; dồn nội dung chính và từ khóa vào các câu đầu')
    if contains_brand(value):
        score -= 25
        issues.append('Mô tả chứa tên kênh')
    if not CTA_RE.search(value):
        score -= 25
        issues.append('Thiếu câu kêu gọi đăng ký kênh')
    tags = re.findall(r'(?<!\w)#[\wÀ-ỹ]+', value)
    if len(tags) < 3:
        score -= 10
        tips.append('Có thể thêm hashtag đúng chủ đề khoa học của video')
    elif len(tags) > 15:
        score -= 10
        issues.append(f'{len(tags)} hashtag; YouTube bỏ qua toàn bộ nếu quá 15')
    keywords = [w for w in re.findall(r'\w+', (topic or '').lower()) if len(w) > 3]
    if keywords and not any(word in value.lower() for word in keywords):
        score -= 8
        tips.append('Câu đầu nên chứa từ khóa chính của chủ đề')
    return {'score': max(0, min(100, score)), 'issues': issues, 'tips': tips}


def score_tags(tags, topic=''):
    items = [str(tag).strip() for tag in (tags or []) if str(tag).strip()]
    score, issues, tips = 100, [], []
    if len(items) < 8:
        score -= 30
        issues.append(f'Chỉ {len(items)} tag; nên 10–15 để phủ nhiều truy vấn')
    if len(items) > 20:
        score -= 10
        issues.append(f'{len(items)} tag, dễ loãng; 10–15 là đủ')
    lowered = [tag.lower() for tag in items]
    if len(set(lowered)) != len(lowered):
        score -= 15
        issues.append('Có tag trùng nhau')
    total = len(','.join(items))
    if total > 500:
        score -= 25
        issues.append(f'Tổng {total} ký tự, vượt giới hạn 500 của YouTube')
    short = [tag for tag in items if len(tag) < 3]
    if short:
        score -= 10
        issues.append(f'Tag quá ngắn: {", ".join(short[:3])}')
    keywords = [w for w in re.findall(r'\w+', (topic or '').lower()) if len(w) > 3]
    if keywords and not any(any(word in tag.lower() for word in keywords) for tag in items):
        score -= 10
        tips.append('Phải có ít nhất 1 tag chứa từ khóa chính của chủ đề')
    if not any(len(tag.split()) >= 3 for tag in items):
        tips.append('Thêm 1–2 tag dài (3–4 từ) mô tả đúng nội dung để bắt tìm kiếm dài')
    return {'score': max(0, min(100, score)), 'issues': issues, 'tips': tips, 'total_chars': total}


def suggest_titles(meta, topic=''):
    """Xếp hạng tiêu đề hiện tại + các phương án, trả về danh sách giảm dần."""
    candidates = [meta.get('title', '')] + [t for t in meta.get('title_alternatives', []) if t]
    ranked, seen = [], set()
    for title in candidates:
        if title in seen:
            continue
        seen.add(title)
        ranked.append({'title': title, **score_title(title, topic)})
    return sorted(ranked, key=lambda item: item['score'], reverse=True)


def fix_metadata(meta, topic=''):
    """Sửa những lỗi an toàn (không đổi ý nghĩa) rồi trả về (meta, thay_đổi)."""
    changes = []
    description = (meta.get('description') or '').strip()
    if not CTA_RE.search(description):
        description = (description + '\n\nĐăng ký kênh để xem thêm các video khoa học đời thường.').strip()
        changes.append('Thêm câu kêu gọi đăng ký vào mô tả')
    meta['description'] = description
    title = (meta.get('title') or '').strip()
    if len(title) > 100:
        meta['title'] = title[:97].rstrip() + '…'
        changes.append('Cắt tiêu đề về 100 ký tự')
    tags, seen = [], set()
    for tag in meta.get('tags') or []:
        tag = str(tag).strip()
        if not tag or tag.lower() in seen:
            continue
        seen.add(tag.lower())
        tags.append(tag)
    kept, total = [], 0
    for tag in tags:
        extra = len(tag) + (1 if kept else 0)
        if total + extra > 500:
            break
        kept.append(tag)
        total += extra
    if kept != (meta.get('tags') or []):
        meta['tags'] = kept
        changes.append('Bỏ tag trùng / vượt 500 ký tự')
    if not meta.get('title_recommendation'):
        best = suggest_titles(meta, topic)[0]
        current = score_title(meta.get('title', ''), topic)['score']
        if best['score'] >= current + 8:
            meta['title_recommendation'] = best['title']
            changes.append(f'Đề xuất tiêu đề mạnh hơn: {best["title"]}')
    return meta, changes


def _check(cid, label, status, detail):
    return {'id': cid, 'label': label, 'status': status, 'detail': detail}


def duration_bounds(project):
    """Long-form policy in seconds; reject malformed or inverted configuration."""
    config = project.settings.get('qc', {})
    need(isinstance(config, dict), 'qc phải là cấu hình dạng mapping.')
    low = config.get('min_duration_seconds', 60)
    high = config.get('max_duration_seconds', 3600)
    valid = lambda v: (not isinstance(v, bool) and isinstance(v, (int, float))
                       and math.isfinite(v))
    need(valid(low) and valid(high) and 60 <= low <= high <= 43200,
         'Giới hạn QC phải là số hữu hạn: 60 ≤ min_duration_seconds ≤ max_duration_seconds ≤ 43200.')
    return low, high


def evaluate(project):
    """Toàn bộ checklist trước khi đăng; không ghi file."""
    need(project.final.is_file(), 'Chưa có final.mp4 — chạy bước render trước.')
    meta_path = project.dir / 'publish.json'
    need(meta_path.is_file(), 'Chưa có publish.json — chạy bước publish trước.')
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    topic = project.cfg.get('topic', '')
    media = inspect_media(project)
    subs = inspect_subtitles(project, media)
    cta = inspect_cta(project, media, meta)
    checks = []

    width, height = media['width'], media['height']
    landscape = width and height and abs(width / height - 16 / 9) < 0.02
    checks.append(_check('format', 'Khung ngang 16:9 cho video dài',
                         PASS if landscape and height >= 720 else FAIL,
                         f'{width}×{height}'))
    duration = media['duration']
    low, high = duration_bounds(project)
    checks.append(_check('duration', 'Độ dài hợp lệ cho video dài',
                         PASS if low <= duration <= high else FAIL,
                         f'{duration:.1f}s (giới hạn {low:g}–{high:g}s)'))
    checks.append(_check('fps', 'Khung hình mượt', PASS if media['fps'] >= 24 else WARN,
                         f'{media["fps"]} fps'))
    audio_ok = bool(media['audio_codec']) and (media['mean_db'] is None or media['mean_db'] > -45)
    checks.append(_check('audio', 'Có tiếng, không im lặng',
                         PASS if audio_ok else FAIL,
                         f'{media["audio_codec"] or "không có audio"}, mean {media["mean_db"]} dB'))
    if media['peak_db'] is not None:
        clipped = media['peak_db'] > -0.1
        checks.append(_check('clipping', 'Không bị vỡ tiếng', WARN if clipped else PASS,
                             f'đỉnh {media["peak_db"]} dB'))
    head_ok = media['head_db'] is None or media['head_db'] > -45
    checks.append(_check('hook_audio', '3 giây đầu có giọng nói (hook)', PASS if head_ok else FAIL,
                         f'{media["head_db"]} dB'))
    checks.append(_check('black', 'Không có khung hình đen bất thường',
                         PASS if not media['black_spans'] else FAIL,
                         'không có' if not media['black_spans'] else f'{media["black_spans"]}'))

    subs_ok = subs['issues'] == []
    checks.append(_check('subtitles', 'Phụ đề vừa khung, không che chủ thể',
                         PASS if subs_ok else FAIL,
                         '; '.join(subs['issues']) if subs['issues'] else
                         f'{subs["cues"]} câu, dài nhất {subs["max_chars"]} ký tự (tối đa 2 dòng)'))

    cta_ok = cta['scene_has_cta'] and cta['end_card_ratio_ok'] and cta['description_has_cta']
    cta_detail = []
    if not cta['scene_has_cta']:
        cta_detail.append('cảnh cuối chưa có lời kêu gọi đăng ký')
    if not cta['end_card_ratio_ok']:
        cta_detail.append('thẻ kết 16:9 thiếu hoặc sai tỉ lệ')
    if not cta['description_has_cta']:
        cta_detail.append('mô tả thiếu câu kêu gọi')
    checks.append(_check('cta', 'Có phần khuyến khích đăng ký kênh',
                         PASS if cta_ok else FAIL,
                         '; '.join(cta_detail) if cta_detail else cta['scene_text'][:70]))
    tail_ok = media['tail_db'] is None or media['tail_db'] > -45
    checks.append(_check('cta_audio', 'CTA được đọc thành tiếng ở cuối video',
                         PASS if tail_ok else WARN, f'{media["tail_db"]} dB'))
    checks.append(_check('cta_card', 'Thẻ kết hiện đúng ở cuối video',
                         PASS if cta['end_card_visible'] else WARN,
                         'khớp thẻ kết' if cta['end_card_visible']
                         else f'khác thẻ kết {cta["end_card_distance"]}/256'))

    title = score_title(meta.get('title', ''), topic)
    checks.append(_check('title', 'Tiêu đề hấp dẫn, đúng giới hạn',
                         PASS if title['score'] >= 75 else FAIL,
                         f'{title["score"]}/100' + (f' — {"; ".join(title["issues"])}' if title['issues'] else '')))
    desc = score_description(meta.get('description', ''), topic)
    checks.append(_check('description', 'Mô tả có hook, từ khóa, CTA',
                         PASS if desc['score'] >= 75 else FAIL,
                         f'{desc["score"]}/100' + (f' — {"; ".join(desc["issues"])}' if desc['issues'] else '')))
    tags = score_tags(meta.get('tags'), topic)
    checks.append(_check('tags', 'Tag đủ phủ, không vượt 500 ký tự',
                         PASS if tags['score'] >= 75 else FAIL,
                         f'{tags["score"]}/100, {len(meta.get("tags") or [])} tag/{tags["total_chars"]} ký tự'
                         + (f' — {"; ".join(tags["issues"])}' if tags['issues'] else '')))
    branded = [field for field in ('title', 'description', 'tags')
               if contains_brand(json.dumps(meta.get(field, ''), ensure_ascii=False))]
    checks.append(_check('brand', 'Không lộ tên kênh trong nội dung công khai',
                         PASS if not branded else FAIL,
                         'sạch' if not branded else 'lộ tên kênh trong: ' + ', '.join(branded)))

    weights = {'format': 10, 'duration': 5, 'audio': 10, 'hook_audio': 5, 'black': 5,
               'subtitles': 15, 'cta': 15, 'title': 15, 'description': 10, 'tags': 10}
    score, total = 0, 0
    for check in checks:
        weight = weights.get(check['id'])
        if not weight:
            continue
        total += weight
        factor = {PASS: 1.0, WARN: 0.6, FAIL: 0.0}[check['status']]
        score += weight * factor
    score = round(score / total * 100) if total else 0
    from .visual_review import inspect as inspect_visual
    visual_ok, visual_detail = inspect_visual(project)
    checks.append(_check('visual', 'Chất lượng hình ảnh và trải nghiệm xem',
                         PASS if visual_ok else FAIL, visual_detail))
    from .visual_review import inspect_references
    references_ok, references_detail = inspect_references(project)
    checks.append(_check('visual_references', 'Nghiên cứu video tham khảo thực tế',
                         PASS if references_ok else FAIL, references_detail))
    blockers = [c for c in checks if c['status'] == FAIL]
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'score': score,
        'technical_score': score,
        'visual_approved': visual_ok,
        'approved': not blockers and score >= 80,
        'checks': checks,
        'blockers': [f'{c["label"]}: {c["detail"]}' for c in blockers],
        'media': media,
        'subtitles': subs,
        'cta': cta,
        'title': title,
        'description': desc,
        'tags': tags,
        'suggested_titles': suggest_titles(meta, topic),
    }


def _markdown(project, report, changes):
    media = report['media']
    stamp = datetime.fromisoformat(report['generated_at']).astimezone().strftime('%d/%m/%Y %H:%M')
    lines = [f'# Phiếu kiểm thử — {project.name}', '',
             f'**{TESTER["name"]} · {TESTER["role"]}** — kiểm lúc {stamp}', '',
             f'**Điểm kỹ thuật: {report["score"]}/100 (không chấm độ hấp dẫn) — '
             f'{"ĐẠT, cho phép đăng" if report["approved"] else "CHƯA ĐẠT, chặn đăng"}**', '',
             f'- Video: {media["width"]}×{media["height"]}, {media["duration"]}s, '
             f'{media["fps"]} fps, {media["size_mb"]} MB',
             f'- Tiếng: {media["audio_codec"]} {media["audio_channels"]} kênh, '
             f'trung bình {media["mean_db"]} dB, đỉnh {media["peak_db"]} dB', '',
             '## Checklist', '']
    for check in report['checks']:
        lines.append(f'- {ICON[check["status"]]} **{check["label"]}** — {check["detail"]}')
    if report['blockers']:
        lines += ['', '## Phải sửa trước khi đăng', '']
        lines += [f'{i}. {item}' for i, item in enumerate(report['blockers'], 1)]
    lines += ['', '## Tiêu đề', '']
    for item in report['suggested_titles'][:4]:
        mark = '→' if item['title'] == report['current_title'] else ' '
        lines.append(f'{mark} **{item["score"]}/100** — {item["title"]}')
        for tip in item['tips']:
            lines.append(f'  - {tip}')
    lines += ['', '## Góp ý mô tả / tag', '']
    for tip in report['description']['tips'] + report['tags']['tips']:
        lines.append(f'- {tip}')
    if changes:
        lines += ['', '## Đã tự sửa', ''] + [f'- {item}' for item in changes]
    lines += ['', '---', f'_{TESTER["name"]} · {TESTER["role"]} · xác nhận lúc {stamp}_', '']
    return '\n'.join(lines)


def run(project, force=False):
    """Chấm điểm + tự sửa lỗi an toàn + ghi báo cáo và cổng chất lượng."""
    meta_path = project.dir / 'publish.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    current_title = meta.get('title', '')
    meta, changes = fix_metadata(meta, project.cfg.get('topic', ''))
    if changes:
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    report = evaluate(project)
    report['current_title'] = current_title
    report['auto_fixes'] = changes
    report['tester'] = dict(TESTER)
    report['verdict'] = 'ĐẠT' if report['approved'] else 'CHƯA ĐẠT'

    import hashlib
    with project.final.open('rb') as video:
        digest = hashlib.file_digest(video, 'sha256').hexdigest()
    (project.dir / 'publish-review.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    (project.dir / 'publish-review.md').write_text(_markdown(project, report, changes), encoding='utf-8')
    (project.dir / 'video-quality.json').write_text(json.dumps({
        'approved': report['approved'],
        'score': report['score'],
        'video_sha256': digest,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'duration': report['media']['duration'],
        'width': report['media']['width'],
        'height': report['media']['height'],
        'has_audio': bool(report['media']['audio_codec']),
        'blockers': report['blockers'],
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'[qc] {TESTER["name"]} ({TESTER["role"]}): kỹ thuật {report["score"]}/100 — '
          f'{"ĐẠT" if report["approved"] else "CHƯA ĐẠT"}')
    for check in report['checks']:
        print(f'[qc] {ICON[check["status"]]} {check["label"]}: {check["detail"]}')
    if changes:
        print('[qc] tự sửa: ' + '; '.join(changes))
    if not report['approved']:
        print('[qc] chặn đăng: ' + '; '.join(report['blockers']))
    print(f'[qc] báo cáo: {project.dir / "publish-review.md"}')
    return report
