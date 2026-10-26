"""Bước 3 — script.txt + timestamp voice -> scenes.json (mỗi cảnh có start/end khớp voice)."""
import json
import re
from difflib import SequenceMatcher

from .common import audio_duration, need
from .s1_script import split_sentences

CLAUSE_SPLIT = re.compile(r"(?<=[,;:—–])\s+")


def _norm(w):
    return re.sub(r"[\W_]+", "", w.lower())


def align_words(script_words, voice_words, total):
    """Gán (start, end) cho từng từ của script dựa trên timestamp của voice.
    Từ khớp thì lấy thẳng; từ không khớp được nội suy tuyến tính giữa hai mốc gần nhất."""
    a = [_norm(w) for w in script_words]
    b = [_norm(w["w"]) for w in voice_words]
    start = [None] * len(a)
    end = [None] * len(a)
    for blk in SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            start[blk.a + k] = voice_words[blk.b + k]["start"]
            end[blk.a + k] = voice_words[blk.b + k]["end"]
    need(any(s is not None for s in start), "Không khớp được từ nào giữa script và voice — kiểm tra voice có đúng script không.")
    i = 0
    while i < len(a):
        if start[i] is not None:
            i += 1
            continue
        j = i
        while j < len(a) and start[j] is None:
            j += 1
        t0 = end[i - 1] if i > 0 else 0.0
        t1 = start[j] if j < len(a) else total
        step = (t1 - t0) / (j - i)
        for k in range(i, j):
            start[k] = t0 + (k - i) * step
            end[k] = t0 + (k - i + 1) * step
        i = j
    return start, end


def build_units(sentences, start, end, max_seconds):
    """Mỗi câu là 1 unit; câu dài hơn max_seconds được tách theo dấu phẩy/chấm phẩy."""
    units, idx = [], 0
    for s in sentences:
        n = len(s.split())
        pieces = [s]
        if end[idx + n - 1] - start[idx] > max_seconds:
            pieces = [p for p in CLAUSE_SPLIT.split(s) if p.strip()]
        for p in pieces:
            m = len(p.split())
            units.append({"text": p.strip(), "i0": idx, "i1": idx + m})
            idx += m
    return units


def pack(units, start, end, min_s, max_s):
    scenes, cur = [], None
    for u in units:
        if cur is None:
            cur = dict(u)
            continue
        cur_dur = end[cur["i1"] - 1] - start[cur["i0"]]
        new_dur = end[u["i1"] - 1] - start[cur["i0"]]
        if cur_dur < min_s or new_dur <= max_s:
            cur["text"] += " " + u["text"]
            cur["i1"] = u["i1"]
        else:
            scenes.append(cur)
            cur = dict(u)
    if cur:
        scenes.append(cur)
    return scenes


def make_scenes(script_text, voice_words, total, min_s, max_s):
    sentences = split_sentences(script_text)
    flat = " ".join(sentences).split()
    start, end = align_words(flat, voice_words, total)
    packed = pack(build_units(sentences, start, end, max_s), start, end, min_s, max_s)
    scenes = []
    for k, p in enumerate(packed):
        s = 0.0 if k == 0 else start[p["i0"]]
        scenes.append({"id": k + 1, "text": p["text"], "start": round(s, 3)})
    for k, sc in enumerate(scenes):          # cảnh nối liền nhau, không hở tiếng
        sc["end"] = round(scenes[k + 1]["start"] if k + 1 < len(scenes) else total, 3)
    return scenes


def run(project, force=False):
    if project.scenes_file.exists() and not force:
        print("[scenes] đã có scenes.json — bỏ qua (--force sẽ XÓA prompt/ảnh đã gắn)")
        return
    need(project.script.exists() and project.voice and project.words.exists(),
         "Cần script.txt, voice.* và voice.words.json — chạy các bước trước.")
    words = json.loads(project.words.read_text(encoding="utf-8"))
    sc = project.settings["scenes"]
    scenes = make_scenes(project.script.read_text(encoding="utf-8"), words,
                         audio_duration(project.voice), sc["min_seconds"], sc["max_seconds"])
    project.save_scenes(scenes)
    durs = [s["end"] - s["start"] for s in scenes]
    print(f"[scenes] {len(scenes)} cảnh, dài {min(durs):.1f}–{max(durs):.1f}s (TB {sum(durs)/len(durs):.1f}s)")
