"""Bước 2 — script.txt -> voice + voice.words.json (timestamp từng từ).

provider "vieneu"  : đọc bằng VieNeu-TTS chạy local (pip install vieneu). Vì mỗi câu được đọc riêng nên
                     biết CHÍNH XÁC thời điểm từng câu -> không cần whisper.
provider "manual"  : bạn tự đưa script.txt qua voice AI khác, lưu thành voice.mp3; timestamp lấy bằng whisper.
"""
import json
import sys
from pathlib import Path

from .common import audio_duration, need
from .s1_script import split_sentences
from .script_review import require_approval, digest, write_json

SAMPLE_RATES = {"v3turbo": 48000, "v3nano": 24000}


def preset_pairs(tts):
    """[(label, id)] giọng có sẵn của VieNeu; bỏ mục thiếu id."""
    try:
        pairs = tts.list_preset_voices() or []
    except Exception as e:
        raise SystemExit(f"Không đọc được danh sách giọng VieNeu: {e}")
    out = []
    for item in pairs:
        try:
            label, vid = item[0], item[1]
        except (TypeError, IndexError):
            continue
        vid = str(vid or "").strip()
        if vid:
            out.append((str(label or vid).strip(), vid))
    return out


def pick_voice(presets, raw):
    """Chọn id giọng từ số thứ tự hoặc tên. Trả None nếu không hợp lệ."""
    raw = str(raw or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        i = int(raw)
        return presets[i - 1][1] if 1 <= i <= len(presets) else None
    key = raw.casefold()
    for label, vid in presets:
        if key in (label.casefold(), vid.casefold()):
            return vid
    return None


def choose_voice(tts, ask=None):
    """Chưa cấu hình voice: liệt kê giọng có sẵn và hỏi chọn cho lần chạy này."""
    presets = preset_pairs(tts)
    if not presets:
        raise SystemExit("Chưa chọn voice và không đọc được danh sách giọng. "
                         "Đặt voice.vieneu.voice trong config/settings.yaml rồi chạy lại.")
    print("[voice] Chưa chọn voice. Các giọng có sẵn:")
    for i, (label, vid) in enumerate(presets, 1):
        extra = f" — {label}" if label and label != vid else ""
        print(f"  {i:2d}. {vid}{extra}")
    print("  (đặt voice.vieneu.voice trong config/settings.yaml hoặc project.yaml để lần sau không phải chọn)")
    if ask is None:
        if not sys.stdin.isatty():
            raise SystemExit("Chưa chọn voice. Đặt voice.vieneu.voice trong config/settings.yaml "
                             "(hoặc project.yaml) rồi chạy lại.")
        ask = input
    choice = pick_voice(presets, ask("Chọn số hoặc tên giọng: "))
    if not choice:
        raise SystemExit("Chưa chọn được voice hợp lệ. Chạy lại và chọn một số trong danh sách ở trên.")
    print(f"[voice] dùng giọng '{choice}' cho lần chạy này.")
    return choice


def word_timeline(sentences, durations, gap):
    """Từ thời lượng từng câu -> [{w,start,end}] cho từng từ (chia theo độ dài chữ trong câu)."""
    words, t = [], 0.0
    gaps = gap if isinstance(gap, list) else [gap] * len(sentences)
    for s, dur, pause in zip(sentences, durations, gaps):
        ws = s.split()
        total = sum(len(w) for w in ws) or 1
        cur = t
        for w in ws:
            d = dur * len(w) / total
            words.append({"w": w, "start": round(cur, 3), "end": round(cur + d, 3)})
            cur += d
        t += dur + pause
    return words


def synth_vieneu(project, plan=None):
    import numpy as np
    try:
        from vieneu import Vieneu
    except ImportError:
        raise SystemExit("Chưa cài VieNeu-TTS: pip install vieneu   (GPU NVIDIA: xem README của VieNeu-TTS)")
    cfg = project.settings["voice"]["vieneu"]
    sr = SAMPLE_RATES.get(cfg["mode"], 48000)
    sentences = [s["text"] for s in plan["segments"]] if plan else split_sentences(project.script.read_text(encoding="utf-8"))
    kwargs = {"mode": cfg["mode"]}
    if cfg.get("precision"):
        kwargs["precision"] = cfg["precision"]           # chỉ có tác dụng khi chạy CPU (ONNX)
    tts = Vieneu(**kwargs)
    voice = str(cfg.get("voice") or "").strip()
    if cfg.get("ref_audio"):                              # nhân bản giọng từ clip 3-8 giây
        ref = Path(cfg["ref_audio"])
        ref = ref if ref.is_absolute() else project.dir / ref
        need(ref.exists(), f"Không thấy ref_audio: {ref}")
        voice = f"{project.name}_voice"
        tts.add_voice(voice, str(ref))
    elif not voice:                                       # chưa chọn giọng -> hỏi người dùng
        voice = choose_voice(tts)
    print(f"[voice] VieNeu {cfg['mode']} — đang đọc {len(sentences)} câu bằng giọng '{voice}'...")
    audios = [np.asarray(a, dtype=np.float32).reshape(-1) for a in tts.infer_batch(sentences, voice=voice)]
    need(len(audios) == len(sentences), "VieNeu trả về số đoạn audio không khớp số câu")
    gap = [s["pause_after"] for s in plan["segments"]] if plan else [cfg["gap_seconds"]] * len(audios)
    parts = []
    for index, a in enumerate(audios):
        parts.append(a)
        if index < len(audios)-1:
            parts.append(np.zeros(int(gap[index] * sr), dtype=np.float32))
    full = np.concatenate(parts)
    for old in project.dir.glob("voice.*"):
        old.unlink()
    out = project.dir / "voice.wav"
    tts.save(full, str(out))
    words = word_timeline(sentences, [len(a) / sr for a in audios], gap)
    expected, actual = len(full) / sr, audio_duration(out)
    need(abs(expected - actual) < 1.0,
         f"Độ dài file voice ({actual:.1f}s) lệch tính toán ({expected:.1f}s) — sai sample rate? Kiểm tra voice.vieneu.mode")
    project.words.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    print(f"[voice] ✓ {out.name} {actual:.1f}s, timestamp chính xác theo câu -> {project.words.name}")


def transcribe(project):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit("Cần timestamp: pip install faster-whisper, hoặc tự tạo voice.words.json "
                         "dạng [{\"w\":\"từ\",\"start\":0.0,\"end\":0.4}, ...]")
    w = project.settings["voice"]["whisper"]
    model = WhisperModel(w["model"], compute_type="int8")
    segs, _ = model.transcribe(str(project.voice), language=w["language"], word_timestamps=True)
    words = [{"w": x.word.strip(), "start": round(x.start, 3), "end": round(x.end, 3)}
             for s in segs for x in s.words]
    project.words.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    print(f"[voice] {len(words)} từ có timestamp (whisper) -> {project.words.name}")


def run(project, force=False):
    need(project.script.exists(), "Chưa có script.txt — chạy bước 'script' trước.")
    plan = require_approval(project)
    source = {"script_sha256": digest(project.script.read_text(encoding="utf-8")),
              "plan_sha256": digest(plan), "voice_config_sha256": digest(project.settings["voice"])}
    provider = project.settings["voice"]["provider"]
    if project.voice and project.words.exists() and not force:
        if plan:
            try:
                previous = json.loads((project.dir / "voice.source.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                previous = None
            need(previous == source, "Giọng đọc cũ không khớp bản duyệt/kế hoạch thu. Chạy --from voice --force để tạo lại các bước sau (voice manual: thay file audio theo bản đã duyệt).")
        print(f"[voice] đã có {project.voice.name} + {project.words.name} — bỏ qua (--force để đọc lại)")
        return
    if provider == "vieneu":
        synth_vieneu(project, plan)
    else:
        need(project.voice, f"Đưa script.txt qua voice AI rồi lưu thành {project.dir}/voice.mp3, sau đó chạy lại.")
        transcribe(project)
    write_json(project.dir / "voice.source.json", source)
