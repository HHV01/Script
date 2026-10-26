"""Tiện ích dùng chung: đường dẫn, cấu hình, đọc/ghi scenes.json, ffprobe."""
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

# Windows: khi chạy qua pipe/redirect, stdout mặc định là cp1252 -> in tiếng Việt bị
# UnicodeEncodeError. Ép UTF-8 (chạy sớm vì mọi bước đều print tiếng Việt).
for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
PROJECTS = ROOT / "projects"


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deep_merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


class Project:
    def __init__(self, name):
        self.name = name
        self.dir = PROJECTS / name
        if not (self.dir / "project.yaml").exists():
            raise SystemExit(f"Không thấy {self.dir}/project.yaml — chạy: python run.py new {name}")
        self.cfg = load_yaml(self.dir / "project.yaml")
        self.settings = deep_merge(load_yaml(CONFIG / "settings.yaml"), self.cfg.get("settings"))
        self.style = load_yaml(CONFIG / "style.yaml")
        self.characters = {}
        for cid in self.cfg.get("characters", []):
            p = CONFIG / "characters" / f"{cid}.yaml"
            if not p.exists():
                raise SystemExit(f"Thiếu bible nhân vật: {p}")
            self.characters[cid] = load_yaml(p)

    # --- đường dẫn các file của project ---
    @property
    def script(self): return self.dir / "script.txt"
    @property
    def words(self): return self.dir / "voice.words.json"
    @property
    def scenes_file(self): return self.dir / "scenes.json"
    @property
    def images_dir(self): return self.dir / "images"
    @property
    def srt(self): return self.dir / "subtitles.srt"
    @property
    def final(self): return self.dir / "final.mp4"

    @property
    def voice(self):
        for ext in ("mp3", "wav", "m4a", "ogg"):
            p = self.dir / f"voice.{ext}"
            if p.exists():
                return p
        return None

    def load_scenes(self):
        if not self.scenes_file.exists():
            raise SystemExit("Chưa có scenes.json — chạy bước 'scenes' trước.")
        return json.loads(self.scenes_file.read_text(encoding="utf-8"))

    def save_scenes(self, scenes):
        tmp = self.scenes_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.scenes_file)  # ghi nguyên tử, tránh hỏng file khi bị ngắt giữa chừng

    def image_path(self, scene):
        """Đường dẫn ảnh đã tải của cảnh (None nếu chưa có)."""
        for p in self.images_dir.glob(f"{scene['id']:03d}.*"):
            return p
        return None


def audio_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def need(cond, msg):
    if not cond:
        raise SystemExit(msg)
