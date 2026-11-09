"""Report near-duplicate narration segments before image generation.

Deleting scenes is an editorial decision, so this module never edits or removes
anything. It prints pairs above a similarity threshold for the owner to review.
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

TEXT_KEYS = ('narration', 'text', 'script', 'loi_dan', 'loi', 'content', 'noi_dung')
ID_KEYS = ('id', 'scene', 'scene_id', 'so', 'stt')
MAX_PAIRS = 200


def normalize(text):
    text = unicodedata.normalize('NFC', str(text)).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def load_segments(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, dict):
        for key in ('scenes', 'items', 'segments', 'data'):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            raise SystemExit('Không tìm thấy danh sách cảnh trong JSON')
    if not isinstance(data, list):
        raise SystemExit('JSON phải là danh sách cảnh')
    segments = []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict):
            raise SystemExit(f'Phần tử {index} không phải object')
        text = next((item[k] for k in TEXT_KEYS if item.get(k)), None)
        if not text:
            continue
        ident = next((item[k] for k in ID_KEYS if item.get(k) is not None), index)
        segments.append({'id': ident, 'text': str(text)})
    return segments


def find_similar(segments, threshold=0.85):
    prepared = [(s['id'], normalize(s['text']), s['text']) for s in segments]
    pairs = []
    for i in range(len(prepared)):
        for j in range(i + 1, len(prepared)):
            a, b = prepared[i][1], prepared[j][1]
            if not a or not b:
                continue
            ratio = SequenceMatcher(None, a, b).ratio()
            if ratio >= threshold:
                pairs.append({'a': prepared[i][0], 'b': prepared[j][0],
                              'ratio': round(ratio, 4),
                              'a_text': prepared[i][2][:160],
                              'b_text': prepared[j][2][:160]})
    pairs.sort(key=lambda p: p['ratio'], reverse=True)
    return pairs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scenes', help='JSON cảnh có trường narration/text/script và id')
    ap.add_argument('--threshold', type=float, default=0.85)
    ap.add_argument('--json', action='store_true', dest='as_json')
    args = ap.parse_args(argv)
    segments = load_segments(args.scenes)
    if len(segments) > 2000:
        print(f'[dedupe] {len(segments)} cảnh: so sánh toàn bộ sẽ chậm, cân nhắc lọc trước.',
              file=sys.stderr)
    pairs = find_similar(segments, args.threshold)
    report = {'scenes': len(segments), 'threshold': args.threshold,
              'duplicate_pairs': len(pairs), 'pairs': pairs[:MAX_PAIRS],
              'truncated': len(pairs) > MAX_PAIRS,
              'note': 'Chỉ báo cáo; không tự xoá hay sửa cảnh.'}
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    print(f"[dedupe] {len(segments)} cảnh, ngưỡng {args.threshold:.2f}, "
          f"{len(pairs)} cặp giống")
    for p in pairs[:MAX_PAIRS]:
        print(f"  {p['a']} ~ {p['b']}  {p['ratio']:.2f}")
        print(f"     {p['a_text']}")
        print(f"     {p['b_text']}")
    if not pairs:
        print('  Không có cặp nào vượt ngưỡng.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
