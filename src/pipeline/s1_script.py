"""Bước 1 — Bible nhân vật + chủ đề -> script.txt (lời đọc hoàn chỉnh, đã loại câu trùng)."""
import re
from difflib import SequenceMatcher

from . import llm
from .common import CONFIG, need

SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def norm(s):
    return re.sub(r"[\W_]+", " ", s.lower()).strip()


def dedupe(text, threshold=0.85):
    """Loại các câu trùng/na ná câu đã xuất hiện trước đó. Trả (text_mới, số_câu_bị_loại)."""
    kept, kept_norm, dropped = [], [], 0
    for s in split_sentences(text):
        n = norm(s)
        if any(SequenceMatcher(None, n, k).ratio() >= threshold for k in kept_norm[-400:]):
            dropped += 1
            continue
        kept.append(s)
        kept_norm.append(n)
    return " ".join(kept), dropped


def describe_characters(project):
    parts = []
    for c in project.characters.values():
        v = c.get("vibe", {})
        parts.append(f"- {c['name']} ({c.get('role', '')}): " + "; ".join(f"{k}: {val}" for k, val in v.items()))
    return "\n".join(parts)


def run(project, force=False):
    if project.script.exists() and not force:
        print(f"[script] đã có {project.script.name} — bỏ qua (dùng --force để viết lại)")
        return
    st = project.settings
    minutes = project.cfg.get("minutes", 8)
    template = (CONFIG / "prompts" / "script.md").read_text(encoding="utf-8")
    prompt = template.format(
        topic=project.cfg["topic"], minutes=minutes,
        words=minutes * st["script"]["words_per_minute"],
        characters=describe_characters(project))
    raw = llm.complete(st["llm"]["model"], prompt)
    text, dropped = dedupe(raw, st["script"]["dedupe_threshold"])
    need(text, "LLM trả về kịch bản rỗng")
    project.script.write_text(text + "\n", encoding="utf-8")
    print(f"[script] {len(text.split())} từ, loại {dropped} câu trùng -> {project.script.name}")
