"""Chạy thử toàn pipeline (trừ LLM/voice AI/Flow thật) bằng extension giả. Dùng để kiểm tra nhanh sau khi sửa code:
    python tests/e2e_fake.py
"""
import io, json, shutil, subprocess, sys, threading, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PIL import Image  # noqa: E402
from pipeline import s3_scenes, s5_generate, s6_collect, s7_render  # noqa: E402
from pipeline.common import PROJECTS, Project, audio_duration  # noqa: E402

NAME = "_e2e_tmp"
d = PROJECTS / NAME
shutil.rmtree(d, ignore_errors=True)
shutil.copytree(PROJECTS / "_template", d)
(d / "project.yaml").write_text(
    "topic: demo\ncharacters: [tich]\nsettings:\n  flow: {delay_seconds: [0, 0], retries: 0}\n  render: {width: 640, height: 360, fps: 24}\n",
    encoding="utf-8")
text = " ".join(f"Đây là câu số {i} của kịch bản thử nghiệm, nói về một chủ đề nào đó." for i in range(1, 9))
(d / "script.txt").write_text(text, encoding="utf-8")
words, t = [], 0.0
for w in text.split():
    words.append({"w": w, "start": round(t, 3), "end": round(t + 0.33, 3)}); t += 0.38
(d / "voice.words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=440:duration={t + 0.5}",
                str(d / "voice.mp3")], check=True)

p = Project(NAME)
s3_scenes.run(p)
scenes = p.load_scenes()
for s in scenes:
    s["image_prompt"] = f"prompt {s['id']}"
p.save_scenes(scenes)
print(f"{len(scenes)} cảnh, voice {audio_duration(p.voice):.1f}s")

base = "http://127.0.0.1:8765"
store = {}                                   # key -> png bytes, giả lập project Flow


def fake_extension():
    n = 0
    while True:
        try:
            c = json.loads(urllib.request.urlopen(base + "/next").read())
            if c["cmd"] == "idle":
                continue
            d_ = c["data"]
            if c["cmd"] == "submit":
                n += 1
                buf = io.BytesIO(); Image.new("RGB", (800, 450), ((n * 37) % 255, (n * 91) % 255, 160)).save(buf, "PNG")
                store[f"/img{n}"] = buf.getvalue(); out = {"tiles": [f"/img{n}"]}
            elif c["cmd"] == "list_tiles":
                out = {"keys": list(store)}
            elif c["cmd"] == "download":
                urllib.request.urlopen(urllib.request.Request(
                    f"{base}/upload?scene={d_['scene']}&ext=png", data=store[d_["key"]], method="POST")); out = {}
            else:
                out = {"url": "fake", "tiles": len(store)}
            res = {"id": c["id"], "ok": True, "data": out}
            urllib.request.urlopen(urllib.request.Request(base + "/result", data=json.dumps(res).encode(), method="POST"))
        except OSError:
            return


threading.Thread(target=fake_extension, daemon=True).start()
s5_generate.run(p)
s6_collect.run(p)
s7_render.run(p)
print("final.mp4:", f"{audio_duration(p.final):.2f}s", "(voice", f"{audio_duration(p.voice):.2f}s)")

# thử kịch bản lỗi: xóa 1 ảnh khỏi project Flow -> collect phải TỪ CHỐI tải
store.pop("/img3")
try:
    s6_collect.run(p, force=True)
    print("LỖI: lẽ ra phải từ chối"); sys.exit(1)
except SystemExit as e:
    print("OK, collect từ chối khi ảnh không khớp:", str(e)[:60])
import os
if not os.environ.get("KEEP"):
    shutil.rmtree(d)
