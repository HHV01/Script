"""Bước 5 — gửi toàn bộ image_prompt vào Google Flow qua extension, ghi lại ảnh nào thuộc cảnh nào."""
import random
import time

from .bridge import BridgeError, get_bridge
from .common import need


def connect(project):
    b = get_bridge(project)
    url = project.cfg.get("flow_url")
    print(f"[flow] đang đợi extension kết nối cổng {b.port}..."
          + (f" Mở: {url}" if url else " Hãy mở project Flow trong Chrome."))
    b.wait_connected()
    return b


def ping(project):
    b = connect(project)
    info = b.call("ping")
    print(f"[flow] kết nối OK — {info}")
    if not info.get("tiles"):
        print("[flow] ⚠ extension không thấy ảnh nào trong tab. Nếu project đã có ảnh, "
              "hãy chỉnh selector 'tileImg' trong flow_extension/selectors.js")


def run(project, force=False):
    scenes = project.load_scenes()
    need(all(s.get("image_prompt") for s in scenes), "Có cảnh chưa có image_prompt — chạy bước 'prompts'.")
    cfg = project.settings["flow"]
    b = connect(project)
    todo = [s for s in scenes if force or not s.get("tile_key")]
    print(f"[flow] cần gen {len(todo)}/{len(scenes)} cảnh")
    for n, s in enumerate(todo, 1):
        for attempt in range(cfg["retries"] + 1):
            try:
                r = b.call("submit", {"scene": s["id"], "prompt": s["image_prompt"]},
                           timeout=cfg["submit_timeout"] + 30)
                tiles = r["tiles"]
                need(tiles, "không có ảnh mới")
                s["tile_candidates"] = tiles
                s["tile_key"] = tiles[0] if cfg["pick"] == "first" else tiles[-1]
                project.save_scenes(scenes)       # lưu sau MỖI cảnh -> chạy lại sẽ tiếp tục từ chỗ dừng
                print(f"[flow] {n}/{len(todo)} cảnh {s['id']} ✓ ({len(tiles)} ảnh)")
                break
            except (BridgeError, SystemExit) as e:
                print(f"[flow] cảnh {s['id']} lỗi (lần {attempt + 1}): {e}")
                if attempt == cfg["retries"]:
                    print("[flow] dừng — chạy lại để tiếp tục từ cảnh này.")
                    return
        lo, hi = cfg["delay_seconds"]
        time.sleep(random.uniform(lo, hi))
    print("[flow] đã gen xong tất cả cảnh. Chạy bước 'collect' để kiểm tra và tải.")
