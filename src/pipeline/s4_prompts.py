"""Bước 4 — mỗi cảnh -> image_prompt hoàn chỉnh (style + ngoại hình nhân vật cố định + nội dung cảnh)."""
from . import llm
from .common import CONFIG, need
from .local_animation import is_local_scene
from .branding import contains_brand


def compose(style, characters, scene_desc, char_ids):
    parts = [style["prefix"]]
    parts += [characters[c]["visual"] for c in char_ids if c in characters]
    parts.append(scene_desc.strip().rstrip("."))
    parts.append(style["suffix"])
    out = ". ".join(p.strip().rstrip(".") for p in parts if p)
    if style.get("avoid"):
        out += f". Avoid: {style['avoid']}"
    return out


def _characters_text(characters):
    return "\n".join(f"- {cid}: {c['name']} — {c.get('role', '')}" for cid, c in characters.items())


def _ask(project, batch):
    template = (CONFIG / "prompts" / "scene_prompts.md").read_text(encoding="utf-8")
    prompt = template.format(
        style=project.style["prefix"], characters=_characters_text(project.characters),
        topic=project.cfg["topic"],
        scenes="\n".join(f'{s["id"]}. {s["text"]}' for s in batch))
    return llm.extract_json(llm.complete(project.settings["llm"]["model"], prompt))


def validate(batch, result):
    """Phải đủ đúng id, scene_desc không rỗng. Trả về danh sách lỗi."""
    errs = []
    got = {r.get("id"): r for r in result if isinstance(r, dict)}
    for s in batch:
        r = got.get(s["id"])
        if not r or not str(r.get("scene_desc", "")).strip() or contains_brand(str(r.get("scene_desc", ""))):
            errs.append(s["id"])
    return errs


def run(project, force=False):
    scenes = project.load_scenes()
    image_scenes = [s for s in scenes if not is_local_scene(s)]
    todo = [s for s in image_scenes if force or not s.get("image_prompt")]
    if not todo:
        print("[prompts] không có cảnh cần gọi LLM (animation cục bộ hoặc prompt đã có) — bỏ qua")
        return
    size = project.settings["prompts"]["batch_size"]
    for i in range(0, len(todo), size):
        batch = todo[i:i + size]
        for attempt in (1, 2):
            result = _ask(project, batch)
            bad = validate(batch, result)
            if not bad:
                break
            print(f"[prompts] thiếu/rỗng cảnh {bad}, thử lại ({attempt}/2)")
        need(not bad, f"LLM không trả đủ prompt cho cảnh {bad}")
        got = {r["id"]: r for r in result}
        for s in batch:
            r = got[s["id"]]
            s["scene_desc"] = r["scene_desc"]
            s["characters"] = [c for c in r.get("characters", []) if c in project.characters]
            s["image_prompt"] = compose(project.style, project.characters, r["scene_desc"], s["characters"])
        project.save_scenes(scenes)
        print(f"[prompts] {min(i + size, len(todo))}/{len(todo)}")
    missing = [s["id"] for s in image_scenes if not s.get("image_prompt")]
    need(not missing, f"Còn cảnh chưa có prompt: {missing}")
    (project.dir / "prompts.txt").write_text(
        "\n".join(f'{s["id"]:03d}\t{s["image_prompt"]}' for s in image_scenes), encoding="utf-8")
    print(f"[prompts] đủ {len(scenes)}/{len(scenes)} prompt -> prompts.txt (để bạn đọc lại)")
