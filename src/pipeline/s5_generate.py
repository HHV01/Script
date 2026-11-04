"""Bước 5 — tạo/tải ảnh Flow, lưu từng cảnh để tiếp tục không gửi trùng."""
import random
import time
import json
from pathlib import Path
from PIL import Image

from .bridge import BridgeError, get_bridge
from .common import need


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
    b.wait_connected(timeout=project.settings["flow"].get("playwright", {}).get("readiness_timeout", 60))
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


def valid_local_image(project, scene):
    """File decoding and dimensions only; this is not an artistic review."""
    path = project.image_path(scene)
    if not path:
        return False
    try:
        with Image.open(path) as image:
            if min(image.size) < 128:
                return False
            image.verify()
        return True
    except (OSError, ValueError, SyntaxError):
        return False


def attempt_path(project, scene):
    return (project.images_dir if getattr(project, '_nested', False) else Path(getattr(project, 'dir', project.images_dir.parent))) / 'flow-attempts' / f"{scene['id']:03d}.json"


def save_attempt(project, scene, status):
    path = attempt_path(project, scene)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'scene_id': scene['id'], 'status': status,
                                     'updated_at': time.time()}, indent=2), encoding='utf-8')
    temporary.replace(path)


def run(project, force=False, scene_ids=None):
    all_scenes = project.load_scenes()
    scenes = all_scenes
    ids = [scene['id'] for scene in all_scenes]
    need(len(ids) == len(set(ids)), 'Storyboard có ID cảnh trùng; dừng để tránh ghi đè ảnh.')
    known_tiles = {}
    for scene in all_scenes:
        key = scene.get('tile_key')
        if key:
            need(key not in known_tiles, 'Một tile Flow đang gắn với nhiều cảnh; cần đối chiếu gallery, không dùng lại ảnh để giảm lượt tạo.')
            known_tiles[key] = scene['id']
    if scene_ids is not None:
        selected = set(scene_ids)
        missing = selected - {s['id'] for s in all_scenes}
        need(not missing, f"Không có cảnh ID: {sorted(missing)}")
        scenes = [s for s in all_scenes if s['id'] in selected]
    if not scenes:
        print('[flow] Không có cảnh cần tạo ảnh.')
        return
    todo = [s for s in scenes if force or not valid_local_image(project, s)]
    if not todo:
        print('[flow] Ảnh cục bộ đã đọc được; không mở trình duyệt hoặc tạo lại.')
        return
    for scene in todo:
        if force or scene.get('tile_key'):
            continue
        path = attempt_path(project, scene)
        legacy = Path(getattr(project, 'dir', project.images_dir.parent)) / 'flow-attempts' / path.name
        if not path.exists() and legacy.exists():
            path = legacy
        if path.exists():
            try:
                status = json.loads(path.read_text(encoding='utf-8')).get('status')
            except (ValueError, OSError):
                status = 'unknown'
            need(status not in ('submitting', 'unknown', 'tile_saved', 'downloaded'),
                 f"Cảnh {scene['id']} đã gửi nhưng kết quả chưa rõ. Kiểm tra gallery Flow và gắn tile_key; "
                 "chỉ dùng --force sau khi đã kiểm tra để chủ động tạo lại.")
    need(all(s.get('image_prompt') for s in todo if force or not s.get('tile_key')),
         "Có cảnh chưa có image_prompt — chạy bước 'prompts'.")
    cfg = project.settings["flow"]
    b = connect(project)
    print(f"[flow] cần gen {len(todo)}/{len(scenes)} cảnh")
    last_submit_finished = None
    for n, s in enumerate(todo, 1):
        started = time.monotonic()
        submitted = False
        submit_seconds = download_seconds = cooldown_seconds = 0.0
        if force or not s.get('tile_key'):
            if last_submit_finished is not None:
                lo, hi = cfg['delay_seconds']
                remaining = random.uniform(lo, hi) - (time.monotonic() - last_submit_finished)
                if remaining > 0:
                    time.sleep(remaining)
                    cooldown_seconds = remaining
            save_attempt(project, s, 'submitting')
            submitted = True
            try:
                submit_started = time.monotonic()
                r = b.call("submit", {"scene": s["id"], "prompt": s["image_prompt"]},
                           timeout=cfg["submit_timeout"] + 30)
                last_submit_finished = time.monotonic()
                submit_seconds = last_submit_finished - submit_started
                tiles = r["tiles"]
                need(tiles, "không có ảnh mới")
                chosen = tiles[0] if cfg["pick"] == "first" else tiles[-1]
                need(chosen not in known_tiles or known_tiles[chosen] == s['id'],
                     f"Tile trả về cho cảnh {s['id']} đã thuộc cảnh khác; dừng để tránh gắn nhầm ảnh.")
                old_key = s.get('tile_key')
                if old_key:
                    known_tiles.pop(old_key, None)
                known_tiles[chosen] = s['id']
                s["tile_candidates"] = tiles
                s["tile_key"] = chosen
                project.save_scenes(all_scenes)       # lưu sau MỖI cảnh -> chạy lại sẽ tiếp tục từ chỗ dừng
            except (BridgeError, SystemExit) as e:
                save_attempt(project, s, 'unknown')
                raise SystemExit(f"Cảnh {s['id']}: kết quả gửi chưa rõ; không tự gửi lại. Kiểm tra gallery Flow. {e}")
            save_attempt(project, s, 'tile_saved')
        # A known tile must only be downloaded again, never resubmitted on failure.
        try:
            download_started = time.monotonic()
            b.call('download', {'scene': s['id'], 'key': s['tile_key']}, timeout=120)
            need(valid_local_image(project, s), f"Ảnh cảnh {s['id']} chưa tải được hoặc không giải mã được.")
        except (BridgeError, SystemExit) as e:
            raise SystemExit(f"Không tải được cảnh {s['id']}; đã giữ tile_key, chạy lại chỉ tải ảnh. {e}")
        download_seconds = time.monotonic() - download_started
        s['image'] = project.image_path(s).name
        project.save_scenes(all_scenes)
        save_attempt(project, s, 'downloaded')
        print(f"[flow] {n}/{len(todo)} cảnh {s['id']} đã tải và kiểm tra file")
        # Store measured wall time, not a prediction of Google generation speed.
        path = attempt_path(project, s)
        attempt = json.loads(path.read_text(encoding='utf-8'))
        attempt.update(elapsed_seconds=round(time.monotonic() - started, 3),
                       operation='generate_download' if submitted else 'download_only',
                       submit_wait_seconds=round(submit_seconds, 3),
                       download_verify_seconds=round(download_seconds, 3),
                       cooldown_seconds=round(cooldown_seconds, 3))
        path.write_text(json.dumps(attempt, indent=2), encoding='utf-8')
        print(f"[flow] cảnh {s['id']}: {attempt['elapsed_seconds']:.1f}s ({attempt['operation']})")
    print("[flow] Đã tải và kiểm tra file các cảnh được chọn; chưa duyệt nội dung hình hoặc đồng bộ video.")
