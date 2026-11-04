"""Bước 7 — ghép ảnh + voice + kịch bản thành final.mp4 bằng ffmpeg."""
import re
import json
import shutil
import math
import subprocess

from .common import need, audio_duration
from .branding import contains_brand


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def _split_cues(text, limit):
    """Chia lời đọc thành cue ngắn để phụ đề không phủ kín khung hình."""
    text = " ".join(text.split())
    if not text:
        return []
    parts = re.split(r'(?<=[.!?;])\s+', text)
    cues = []
    for part in parts:
        if len(part) <= limit:
            cues.append(part)
            continue
        subparts = re.split(r'(?<=[,:])\s+', part)
        buf = ""
        for sp in subparts:
            if len(sp) > limit:
                for w in sp.split():
                    if not buf:
                        buf = w
                    elif len(buf) + 1 + len(w) <= limit:
                        buf += " " + w
                    else:
                        cues.append(buf)
                        buf = w
            elif not buf:
                buf = sp
            elif len(buf) + 1 + len(sp) <= limit:
                buf += " " + sp
            else:
                cues.append(buf)
                buf = sp
        if buf:
            cues.append(buf)
    return cues


def write_srt(scenes, path, width=80):
    out = []
    index = 1
    for s in scenes:
        cues = _split_cues(s["text"], width) or [s["text"]]
        total = sum(len(c) for c in cues) or 1
        start = s["start"]
        span = s["end"] - s["start"]
        for i, cue in enumerate(cues):
            end = s["end"] if i == len(cues) - 1 else start + span * len(cue) / total
            out.append(f'{index}\n{srt_time(start)} --> {srt_time(end)}\n{cue}\n')
            start = end
            index += 1
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
    # Refuse stale agent handoffs before touching images, cache, or final video.
    from .s3_scenes import validate_source
    from .timeline_review import inspect as inspect_timeline
    validate_source(project)
    timing = inspect_timeline(project)
    report_dir = project.dir / 'kich-ban' if getattr(project, '_nested', False) else project.dir
    (report_dir / 'timing-review.json').write_text(
        json.dumps(timing, ensure_ascii=False, indent=2), encoding='utf-8')
    need(timing['approved'], 'Bàn giao hình–giọng chưa đạt: ' + '; '.join(timing['blockers'][:3]))
    scenes = project.load_scenes()
    need(not any(contains_brand(s.get('text', '')) for s in scenes), 'Lời phụ đề còn tên kênh; sửa kịch bản và tạo lại scenes trước khi render.')
    imgs = [project.image_path(s) for s in scenes]
    def motion_clip(scene):
        rel = scene.get("animation_video")
        if not rel:
            return None
        path = project.dir / rel
        return path if path.is_file() else None
    need(all(img or motion_clip(s) or s.get('motion_plan') for s, img in zip(scenes, imgs)),
         f"Thiếu ảnh cảnh {[s['id'] for s, p in zip(scenes, imgs) if not p and not motion_clip(s) and not s.get('motion_plan')]} — chạy bước 'collect'.")
    need(project.voice, "Thiếu voice.*")
    r = project.settings["render"]
    if r.get('require_object_motion', False):
        missing = [s['id'] for s in scenes if not s.get('motion_plan') and not motion_clip(s)]
        need(not missing, f"Cảnh {missing} chưa có chuyển động từng lớp/clip hành động; không dùng zoom ảnh tĩnh để thay animation.")
    W, H, fps = r["width"], r["height"], r["fps"]
    duration = audio_duration(project.voice)
    counts = frame_counts(scenes, fps)
    need(counts, "Chưa có cảnh để render")
    # Hold the last image through the entire narration, including a fractional final frame.
    counts[-1] += max(0, math.ceil(duration * fps) - sum(counts))
    media_dir = project.dir / 'video' if getattr(project, '_nested', False) else project.dir
    clips = media_dir / "_clips"
    clips.mkdir(exist_ok=True)
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    names = []
    for s, img, frames in zip(scenes, imgs, counts):
        out = clips / f"{s['id']:03d}.mp4"
        names.append(out.name)
        if s.get('motion_plan'):
            # Bind/validate every time, before the legacy existence-only cache.
            from .layer_motion import render_scene
            render_scene(project, s, out, W, H, fps, frames)
            print(f"[render] chuyển động từng lớp cảnh {s['id']}/{len(scenes)}")
            continue
        if out.exists() and not force:
            continue
        clip = motion_clip(s)
        if clip:
            need(audio_duration(clip) >= frames/fps-1/fps,
                 f"Clip cảnh {s['id']} chưa phủ lời đọc; không tự loop/đảo chuyển động để kéo dài.")
            ff(project, ["-i", str(clip), "-vf", f"{fit},fps={fps},format=yuv420p",
                         "-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "fast", str(out)])
            print(f"[render] clip chuyển động cảnh {s['id']}/{len(scenes)}")
            continue
        if r["ken_burns"]:
            # 2.5D motion: zoom + drift + a very slight rotation so ảnh tĩnh vẫn "sống".
            z_in = s["id"] % 2 == 1
            zexpr = (f"min(1.0+0.0009*on,1.16)" if z_in
                     else f"max(1.16-0.0009*on,1.0)")
            xexpr = "iw/2-(iw/zoom/2)+sin(on/45)*iw*0.018"
            yexpr = "ih/2-(ih/zoom/2)+cos(on/60)*ih*0.012"
            vf = (f"{fit},scale={W * 2}:{H * 2},zoompan=z='{zexpr}':d={frames}"
                  f":x='{xexpr}':y='{yexpr}':s={W}x{H}:fps={fps},"
                  f"rotate='0.0025*sin(2*PI*t/6)':ow=iw:oh=ih:fillcolor=#f5ecd8,format=yuv420p")
            ff(project, ["-i", str(img), "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", str(out)])
        else:
            ff(project, ["-loop", "1", "-i", str(img), "-vf", f"{fit},fps={fps},format=yuv420p",
                         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", str(out)])
        print(f"[render] cảnh {s['id']}/{len(scenes)}")
    (clips / "list.txt").write_text("".join(f"file '{n}'\n" for n in names), encoding="utf-8")
    ff(project, ["-f", "concat", "-safe", "0", "-i", str(clips / 'list.txt'), "-c", "copy", str(clips / 'video.mp4')])
    write_srt(scenes, project.srt)
    burn = r["burn_subtitles"]
    font_size = int(r.get("subtitle_font_size", 10))
    margin = int(r.get("subtitle_margin_bottom", 8))
    need(1 <= font_size <= 72 and 0 <= margin <= 200, "Cấu hình phụ đề không hợp lệ")
    subtitle_path = project.srt.relative_to(project.dir).as_posix()
    vcodec = ["-vf", f"subtitles='{subtitle_path}':force_style='FontName=Arial,FontSize={font_size},Alignment=2,Outline=1,Shadow=0,MarginV={margin}'",
              "-c:v", "libx264", "-preset", "fast"] if burn else ["-c:v", "copy"]
    ff(project, ["-i", str(clips / 'video.mp4'), "-i", str(project.voice), *vcodec,
                 "-c:a", "aac", "-b:a", "192k", "-map", "0:v:0", "-map", "1:a:0", "-t", str(duration), "-shortest", str(project.final)])
    shutil.rmtree(clips)
    print(f"[render] ✓ {project.final}")
