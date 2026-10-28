"""Bước 7 — ghép ảnh + voice + kịch bản thành final.mp4 bằng ffmpeg."""
import shutil
import math
import subprocess
import textwrap

from .common import need, audio_duration
from .branding import contains_brand
from .local_animation import is_local_scene, render as render_animation


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(scenes, path, width=80):
    out = []
    for s in scenes:
        text = "\n".join(textwrap.wrap(s["text"], width))
        out.append(f'{s["id"]}\n{srt_time(s["start"])} --> {srt_time(s["end"])}\n{text}\n')
    path.write_text("\n".join(out), encoding="utf-8")


def frame_counts(scenes, fps):
    """Số frame mỗi cảnh, tính theo mốc tích lũy để tổng không bị lệch so với voice."""
    counts, prev = [], 0
    for s in scenes:
        cur = round(s["end"] * fps)
        counts.append(max(1, cur - prev))
        prev = cur
    return counts


def ff(project, args):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], cwd=project.dir, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg lỗi:\n{r.stderr[-1500:]}")


def run(project, force=False):
    need(shutil.which("ffmpeg"), "Chưa cài ffmpeg (cần có trong PATH).")
    scenes = project.load_scenes()
    need(not any(contains_brand(s.get('text', '')) for s in scenes), 'Lời phụ đề còn tên kênh; sửa kịch bản và tạo lại scenes trước khi render.')
    imgs = [project.image_path(s) for s in scenes]
    need(all(img or is_local_scene(s) for s, img in zip(scenes, imgs)), f"Thiếu ảnh cảnh {[s['id'] for s, p in zip(scenes, imgs) if not p and not is_local_scene(s)]} — chạy bước 'collect'.")
    need(project.voice, "Thiếu voice.*")
    r = project.settings["render"]
    W, H, fps = r["width"], r["height"], r["fps"]
    duration = audio_duration(project.voice)
    counts = frame_counts(scenes, fps)
    need(counts, "Chưa có cảnh để render")
    # Hold the last image through the entire narration, including a fractional final frame.
    counts[-1] += max(0, math.ceil(duration * fps) - sum(counts))
    clips = project.dir / "_clips"
    clips.mkdir(exist_ok=True)
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    names = []
    for s, img, frames in zip(scenes, imgs, counts):
        out = clips / f"{s['id']:03d}.mp4"
        names.append(out.name)
        if out.exists() and not force:
            continue
        if is_local_scene(s):
            render_animation(s['animation']['preset'], out, frames/fps, W, H, fps, frames=frames)
            print(f"[render] animation cục bộ cảnh {s['id']}/{len(scenes)}")
            continue
        if r["ken_burns"]:
            vf = (f"{fit},scale={W * 2}:{H * 2},zoompan=z='min(zoom+0.0005,1.1)':d={frames}"
                  f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps},format=yuv420p")
            ff(project, ["-i", str(img), "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", str(out)])
        else:
            ff(project, ["-loop", "1", "-i", str(img), "-vf", f"{fit},fps={fps},format=yuv420p",
                         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", str(out)])
        print(f"[render] cảnh {s['id']}/{len(scenes)}")
    (clips / "list.txt").write_text("".join(f"file '{n}'\n" for n in names), encoding="utf-8")
    ff(project, ["-f", "concat", "-safe", "0", "-i", "_clips/list.txt", "-c", "copy", "_clips/video.mp4"])
    write_srt(scenes, project.srt)
    burn = r["burn_subtitles"]
    font_size = int(r.get("subtitle_font_size", 10))
    margin = int(r.get("subtitle_margin_bottom", 8))
    need(1 <= font_size <= 72 and 0 <= margin <= 200, "Cấu hình phụ đề không hợp lệ")
    vcodec = ["-vf", f"subtitles=subtitles.srt:force_style='FontName=Arial,FontSize={font_size},Alignment=2,Outline=1,Shadow=0,MarginV={margin}'",
              "-c:v", "libx264", "-preset", "fast"] if burn else ["-c:v", "copy"]
    ff(project, ["-i", "_clips/video.mp4", "-i", project.voice.name, *vcodec,
                 "-c:a", "aac", "-b:a", "192k", "-map", "0:v:0", "-map", "1:a:0", "-t", str(duration), "-shortest", project.final.name])
    shutil.rmtree(clips)
    print(f"[render] ✓ {project.final}")
