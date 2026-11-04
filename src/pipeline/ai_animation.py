"""Animate scene images locally with ComfyUI + Stable Video Diffusion.

No API tokens or cloud credits are used: everything runs on the local GPU.
"""
import json
import hashlib
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageSequence

from .common import ROOT, need

COMFY = Path(os.environ.get("COMFYUI_DIR", r"C:\ComfyUI\ComfyUI_windows_portable\ComfyUI"))
SERVER = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
MODEL = os.environ.get("SVD_MODEL", "svd_xt.safetensors")


def _json(url, payload=None, timeout=60):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def ready():
    try:
        _json(SERVER + "/system_stats", timeout=5)
        return True
    except Exception:
        return False


def _workflow(image_name, prefix, width, height, frames, fps, motion, seed):
    return {
        "1": {"class_type": "ImageOnlyCheckpointLoader", "inputs": {"ckpt_name": MODEL}},
        "2": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "3": {"class_type": "SVD_img2vid_Conditioning", "inputs": {
            "clip_vision": ["1", 1], "init_image": ["2", 0], "vae": ["1", 2],
            "width": width, "height": height, "video_frames": frames,
            "motion_bucket_id": motion, "fps": fps, "augmentation_level": 0.0}},
        "7": {"class_type": "VideoLinearCFGGuidance", "inputs": {"model": ["1", 0], "min_cfg": 1.0}},
        "4": {"class_type": "KSampler", "inputs": {
            "model": ["7", 0], "positive": ["3", 0], "negative": ["3", 1], "latent_image": ["3", 2],
            "seed": seed, "steps": 20, "cfg": 2.5, "sampler_name": "euler",
            "scheduler": "karras", "denoise": 1.0}},
        "5": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["1", 2]}},
        "6": {"class_type": "SaveAnimatedWEBP", "inputs": {
            "images": ["5", 0], "filename_prefix": prefix, "fps": fps,
            "lossless": False, "quality": 92, "method": "default"}},
    }


def _wait(prompt_id, timeout=1800):
    started = time.time()
    while time.time() - started < timeout:
        history = _json(f"{SERVER}/history/{prompt_id}", timeout=30)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(3)
    raise TimeoutError("ComfyUI không trả kết quả trong thời gian chờ.")


def animate_scene(project, scene, width=1024, height=576, frames=25, fps=6,
                  motion=60, timeout=1800, attach=False):
    """Animate the existing source image; prototypes never replace production scenes."""
    need(ready(), "ComfyUI chưa chạy. Bật C:\\ComfyUI\\ComfyUI_windows_portable\\run_nvidia_gpu.bat trước.")
    source = project.image_path(scene)
    need(source and source.is_file(), f"Thiếu ảnh cảnh {scene['id']}")
    input_dir = Path(os.environ.get('COMFYUI_INPUT_DIR', str(COMFY / 'input')))
    input_dir.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    name = f"{project.name}_{scene['id']:03d}_{source_hash[:12]}{source.suffix.lower()}"
    shutil.copy2(source, input_dir / name)
    prefix = f"{project.name}/canh-{scene['id']:03d}"
    seed = 1000 + int(scene["id"])
    clips = project.dir / 'video' / 'animation' if getattr(project, '_nested', False) else project.dir / 'clips'
    clips.mkdir(parents=True, exist_ok=True)
    attempt = clips / f"canh-{scene['id']:03d}-svd-attempt.json"
    parameters = {'source_sha256': source_hash, 'model': MODEL, 'width': width,
                  'height': height, 'frames': frames, 'fps': fps, 'motion': motion, 'seed': seed}
    previous = json.loads(attempt.read_text(encoding='utf-8')) if attempt.exists() else None
    if previous:
        need(previous.get('parameters') == parameters,
             'Đã có lần animate cùng cảnh với nguồn/thông số khác; giữ hồ sơ cũ, không tự ghi đè.')
        need(previous.get('prompt_id'), 'Lần gửi animate trước chưa rõ; kiểm tra queue ComfyUI trước, không tự gửi lại.')
        prompt_id = previous['prompt_id']
    else:
        record = {'parameters': parameters, 'status': 'submitting', 'updated_at': time.time()}
        attempt.write_text(json.dumps(record, indent=2), encoding='utf-8')
        prompt_id = _json(SERVER + "/prompt", {"prompt": _workflow(name, prefix, width, height, frames, fps, motion, seed)})['prompt_id']
        record.update(prompt_id=prompt_id, status='queued')
        attempt.write_text(json.dumps(record, indent=2), encoding='utf-8')
    result = _wait(prompt_id, timeout)
    outputs = result.get("outputs", {})
    files = [img for node in outputs.values() for img in node.get("images", []) if img.get("type") == "output"]
    need(files, "ComfyUI không trả file animation.")
    found = files[-1]
    output_dir = Path(os.environ.get('COMFYUI_OUTPUT_DIR', str(COMFY / 'output')))
    webp = output_dir / found.get("subfolder", "") / found["filename"]
    need(webp.is_file(), f"Không thấy file ComfyUI: {webp}")
    clip = clips / f"canh-{scene['id']:03d}-svd-preview.mp4"
    # Some FFmpeg builds cannot decode animated WEBP. Decode its actual frames
    # with Pillow, then encode them at the requested generation fps; no looping.
    with Image.open(webp) as animation:
        source_width, source_height = animation.size
        pixels = b''.join(frame.convert('RGB').tobytes() for frame in ImageSequence.Iterator(animation))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                    '-s', f'{source_width}x{source_height}', '-r', str(fps), '-i', '-',
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps}",
                    "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)],
                   input=pixels, capture_output=True, check=True)
    receipt = {'executor': 'pipeline.ai_animation; local ComfyUI/SVD', 'source': str(source.relative_to(project.dir)),
               'source_sha256': source_hash, 'prompt_id': prompt_id, 'model': MODEL,
               'frames': frames, 'fps': fps, 'scope': 'Image-to-video prototype; not AV quality approval.',
               'production_attached': False, 'output': str(clip.relative_to(project.dir))}
    clip.with_suffix('.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    attempt.write_text(json.dumps({'parameters': parameters, 'prompt_id': prompt_id,
                                  'status': 'completed', 'updated_at': time.time()}, indent=2), encoding='utf-8')
    if attach:
        from .common import audio_duration
        need(audio_duration(clip) >= scene['end']-scene['start']-.05,
             'Clip chuyển động chưa phủ thời lượng cảnh; không tự đảo/loop để kéo dài. Giữ clip thử riêng.')
        scene['animation_video'] = str(clip.relative_to(project.dir)).replace('\\', '/')
        receipt['production_attached'] = True
        clip.with_suffix('.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    return str(clip.relative_to(project.dir)).replace('\\', '/')


def animate_project(project, only=None):
    scenes = project.load_scenes()
    todo = [s for s in scenes if not only or s["id"] in only]
    for s in todo:
        if s.get("animation_video") and (project.dir / s["animation_video"]).is_file():
            print(f"[animate] cảnh {s['id']} đã có clip — bỏ qua")
            continue
        print(f"[animate] cảnh {s['id']} ...")
        animate_scene(project, s, attach=True)
        project.save_scenes(scenes)
        print(f"[animate] cảnh {s['id']} xong -> {s['animation_video']}")
    print("[animate] hoàn tất. Chạy render để ghép video.")
