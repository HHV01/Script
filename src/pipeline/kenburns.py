"""Slow zoom / pan (Ken Burns) and crossfade for a series of still images.

This is pacing, not animation: the source frame is never redrawn or reinterpreted.
Repo rule (docs/IMAGE-TO-VIDEO.md) says a full-frame zoom must not be reported as
"already animated". Use it for scenes that have no real motion clip.

Requires FFmpeg and ffprobe on PATH or in tools/ffmpeg/bin/.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
SIZE = (1920, 1080)


def ffmpeg_path(name='ffmpeg'):
    exe = ROOT/'tools/ffmpeg/bin'/(name + ('.exe' if sys.platform == 'win32' else ''))
    return str(exe) if exe.is_file() else shutil.which(name)


def find_images(target):
    path = Path(target)
    if path.is_dir():
        files = sorted(p for p in path.iterdir() if p.suffix.lower() in EXTS)
    else:
        files = [path]
    if not files:
        raise SystemExit(f'Không thấy ảnh nào trong {target}')
    return files


def motion_filter(zoom, direction, frames):
    """One alternating move per image so consecutive frames do not move the same way."""
    frames = max(2, int(frames))
    w, h = SIZE
    if direction == 'in':
        z = f'1+{zoom:.4f}*on/{frames - 1}'
        x, y = 'iw/2-(iw/zoom/2)', 'ih/2-(ih/zoom/2)'
    elif direction == 'out':
        z = f'{1 + zoom:.4f}-{zoom:.4f}*on/{frames - 1}'
        x, y = 'iw/2-(iw/zoom/2)', 'ih/2-(ih/zoom/2)'
    elif direction == 'left':
        z = f'{1 + zoom / 2:.4f}'
        x, y = f'(iw-iw/zoom)*on/{frames - 1}', 'ih/2-(ih/zoom/2)'
    else:  # right
        z = f'{1 + zoom / 2:.4f}'
        x, y = f'(iw-iw/zoom)*(1-on/{frames - 1})', 'ih/2-(ih/zoom/2)'
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={{fps}}")


def resolve_durations(durations, count):
    """One shared duration or exactly one per image; anything else is an error."""
    values = list(durations or [])
    if not values:
        return [6.0] * count
    if len(values) == 1:
        values = values * count
    elif len(values) != count:
        raise SystemExit(f'Cần 1 giá trị --duration dùng chung hoặc đúng {count} giá trị, '
                         f'nhận {len(values)}')
    if any(d <= 0 for d in values):
        raise SystemExit('Thời lượng mỗi cảnh phải lớn hơn 0')
    return values


def render(images, out, durations=None, fps=30, zoom=0.10, fade=0.6, size=SIZE, log=print):
    """Render stills to one MP4 with alternating slow moves and crossfades."""
    imgs = [Path(i) for i in images]
    out = Path(out)
    out_resolved = out.resolve()
    for img in imgs:
        if img.resolve() == out_resolved:
            raise SystemExit('Đầu ra trùng ảnh đầu vào; chọn tên tệp khác')
    ffmpeg = ffmpeg_path('ffmpeg')
    if not ffmpeg:
        raise SystemExit('Không có ffmpeg; cài vào PATH hoặc tools/ffmpeg/bin/')
    if len(imgs) == 1:
        fade = 0
    durations = resolve_durations(durations, len(imgs))
    if fade >= min(durations):
        raise SystemExit('Thời lượng fade phải nhỏ hơn cảnh ngắn nhất')
    moves = ['in', 'out', 'left', 'right']
    tmp = Path(tempfile.mkdtemp(prefix='kenburns-'))
    clips = []
    try:
        for i, (img, dur) in enumerate(zip(imgs, durations), 1):
            clip = tmp/f'{i:04d}.mp4'
            direction = moves[(i - 1) % len(moves)]
            frames = max(2, round(dur * fps))
            vf = motion_filter(zoom, direction, frames).format(fps=fps)
            cmd = [ffmpeg, '-y', '-loglevel', 'error', '-i', str(img), '-t', f'{dur}',
                   '-vf', vf, '-r', str(fps), '-pix_fmt', 'yuv420p',
                   '-c:v', 'libx264', '-preset', 'veryfast', str(clip)]
            subprocess.run(cmd, check=True)
            clips.append(clip)
            log(f'[kenburns] {i}/{len(imgs)} {img.name} {dur:.2f}s {direction}')
        if len(clips) == 1:
            shutil.move(str(clips[0]), str(out))
            return Path(out)
        args = [ffmpeg, '-y', '-loglevel', 'error']
        for clip in clips:
            args += ['-i', str(clip)]
        parts, offset, label = [], 0.0, '[0:v]'
        for i in range(1, len(clips)):
            offset += durations[i - 1] - fade
            nxt = f'[x{i}]'
            parts.append(f'{label}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{nxt}')
            label = nxt
        args += ['-filter_complex', ';'.join(parts), '-map', label,
                 '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', str(out)]
        subprocess.run(args, check=True)
        return Path(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('images', help='Thư mục ảnh hoặc một tệp ảnh')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--duration', type=float, nargs='*', default=[],
                    help='Giây cho từng ảnh; một số dùng chung, bỏ trống = 6')
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--zoom', type=float, default=0.10, help='Mức zoom tối đa, ví dụ 0.1 = 10 phần trăm')
    ap.add_argument('--fade', type=float, default=0.6)
    args = ap.parse_args(argv)
    images = find_images(args.images)
    out = render(images, args.out, args.duration, args.fps, args.zoom, args.fade)
    print(json.dumps({'out': str(out), 'images': len(images), 'kind': 'kenburns-pacing'},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
