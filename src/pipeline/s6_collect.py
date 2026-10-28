"""Bước 6 — KIỂM TRA số ảnh khớp số prompt, chỉ khi khớp mới tải nguyên project về images/."""
from .common import need
from .local_animation import is_local_scene
from .s5_generate import connect


def check(scenes, live_keys):
    """Đối chiếu scenes.json với ảnh thật đang có trong project Flow. Trả về danh sách lỗi (rỗng = khớp)."""
    errors = []
    no_tile = [s["id"] for s in scenes if not s.get("tile_key")]
    if no_tile:
        errors.append(f"cảnh chưa có ảnh: {no_tile}")
    keys = [s["tile_key"] for s in scenes if s.get("tile_key")]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        owners = [s["id"] for s in scenes if s.get("tile_key") in dup]
        errors.append(f"nhiều cảnh trỏ cùng 1 ảnh (cảnh {owners})")
    gone = [s["id"] for s in scenes if s.get("tile_key") and s["tile_key"] not in set(live_keys)]
    if gone:
        errors.append(f"ảnh của cảnh {gone} không còn trong project Flow (đã bị xóa?)")
    if len(keys) != len(scenes):
        errors.append(f"số ảnh {len(keys)} ≠ số prompt {len(scenes)}")
    return errors


def run(project, force=False):
    all_scenes = project.load_scenes()
    scenes = [s for s in all_scenes if not is_local_scene(s)]
    if not scenes:
        print('[collect] Cảnh animation cục bộ không cần tải ảnh.')
        return
    b = connect(project)
    live = b.call("list_tiles", timeout=60)["keys"]
    errors = check(scenes, live)
    extra = len(set(live) - {s.get("tile_key") for s in scenes} - {k for s in scenes for k in s.get("tile_candidates", [])})
    print(f"[collect] prompt: {len(scenes)} | ảnh đã gắn: {sum(1 for s in scenes if s.get('tile_key'))} | "
          f"ảnh trong project Flow: {len(live)} (ngoài kịch bản: {extra})")
    if errors:
        for e in errors:
            print(f"[collect] ✗ {e}")
        raise SystemExit("KHÔNG TẢI. Sửa các lỗi trên (thường chỉ cần chạy lại bước 'generate') rồi chạy lại 'collect'.")
    print("[collect] ✓ số ảnh khớp số prompt — bắt đầu tải")
    for n, s in enumerate(scenes, 1):
        p = project.image_path(s)
        if p and p.stat().st_size > 1024 and not force:
            continue
        b.call("download", {"scene": s["id"], "key": s["tile_key"]}, timeout=120)
        print(f"[collect] {n}/{len(scenes)} cảnh {s['id']}")
    bad = [s["id"] for s in scenes if not (project.image_path(s) and project.image_path(s).stat().st_size > 1024)]
    need(not bad, f"Tải xong nhưng thiếu/hỏng file ảnh cảnh {bad} — chạy lại 'collect'.")
    for s in scenes:
        s["image"] = project.image_path(s).name
    project.save_scenes(all_scenes)
    print(f"[collect] ✓ đã tải đủ {len(scenes)}/{len(scenes)} ảnh vào {project.images_dir}")
