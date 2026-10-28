"""Bước 5 — gửi toàn bộ image_prompt vào Google Flow qua extension, ghi lại ảnh nào thuộc cảnh nào."""
import random
import time

from .bridge import BridgeError, get_bridge
from .common import need
from .local_animation import is_local_scene


def require_flow_ready(info):
    """Chưa đăng nhập / chưa mở đúng project Flow -> dừng với hướng dẫn rõ ràng."""
    if info.get("promptBox"):
        return
    url = str(info.get("url") or "")
    if "accounts.google.com" in url or "/login" in url:
        reason = "Chưa đăng nhập Google Flow."
    else:
        reason = ("Chưa đăng nhập Google Flow hoặc chưa mở đúng project Flow "
                  "(không thấy ô nhập prompt).")
    raise SystemExit(
        reason + "\n"
        "→ Mở tab Google Flow trong Chrome, đăng nhập bằng tài khoản Google, mở đúng project rồi chạy lại.\n"
        "→ Nếu đã đăng nhập mà vẫn báo lỗi, kiểm tra selector promptBox trong flow_extension/selectors.js."
    )


def flow_info(b):
    try:
        return b.call("ping")
    except BridgeError as e:
        raise SystemExit(f"Không kết nối được Google Flow: {e}\n"
                         "→ Mở tab Google Flow trong Chrome rồi chạy lại.")


def connect(project, check=True):
    if project.settings["flow"].get("backend", "extension") == "playwright":
        from .flow_playwright import get_browser
        b = get_browser(project)
    else:
        b = get_bridge(project)
    url = project.cfg.get("flow_url")
    transport = "Playwright" if project.settings["flow"].get("backend") == "playwright" else f"extension cổng {b.port}"
    print(f"[flow] đang kết nối {transport}..."
          + (f" Mở: {url}" if url else " Hãy mở project Flow trong Chrome."))
    b.wait_connected()
    if check:
        require_flow_ready(flow_info(b))
    return b


def ping(project):
    b = connect(project, check=False)
    info = flow_info(b)
    require_flow_ready(info)
    print(f"[flow] kết nối OK — {info}")
    if not info.get("tiles"):
        print("[flow] ⚠ extension không thấy ảnh nào trong tab. Nếu project đã có ảnh, "
              "hãy chỉnh selector 'tileImg' trong flow_extension/selectors.js")


def run(project, force=False):
    all_scenes = project.load_scenes()
    scenes = [s for s in all_scenes if not is_local_scene(s)]
    if not scenes:
        print('[flow] Tất cả cảnh dùng animation cục bộ; không mở browser hoặc gọi tạo ảnh.')
        return
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
                project.save_scenes(all_scenes)       # lưu sau MỖI cảnh -> chạy lại sẽ tiếp tục từ chỗ dừng
                print(f"[flow] {n}/{len(todo)} cảnh {s['id']} ✓ ({len(tiles)} ảnh)")
                break
            except (BridgeError, SystemExit) as e:
                print(f"[flow] cảnh {s['id']} lỗi (lần {attempt + 1}): {e}")
                if attempt == cfg["retries"]:
                    print("[flow] dừng — chạy lại để tiếp tục từ cảnh này.")
                    raise SystemExit(f"Không tạo được ảnh cảnh {s['id']}: {e}")
        lo, hi = cfg["delay_seconds"]
        time.sleep(random.uniform(lo, hi))
    print("[flow] đã gen xong tất cả cảnh. Chạy bước 'collect' để kiểm tra và tải.")
