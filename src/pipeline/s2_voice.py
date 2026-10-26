"""Bước 2 — script.txt -> voice + voice.words.json (timestamp từng từ).

provider "vieneu"  : đọc bằng VieNeu-TTS chạy local (pip install vieneu). Vì mỗi câu được đọc riêng nên
                     biết CHÍNH XÁC thời điểm từng câu -> không cần whisper.
provider "manual"  : bạn tự đưa script.txt qua voice AI khác, lưu thành voice.mp3; timestamp lấy bằng whisper.
"""
import json
from pathlib import Path

from .common import audio_duration, need
from .s1_script import split_sentences

SAMPLE_RATES = {"v3turbo": 48000, "v3nano": 24000}


def word_timeline(sentences, durations, gap):
    """Từ thời lượng từng câu -> [{w,start,end}] cho từng từ (chia theo độ dài chữ trong câu)."""
    words, t = [], 0.0
    for s, dur in zip(sentences, durations):
        ws = s.split()
        total = sum(len(w) for w in ws) or 1
        cur = t
        for w in ws:
            d = dur * len(w) / total
            words.append({"w": w, "start": round(cur, 3), "end": round(cur + d, 3)})
            cur += d
        t += dur + gap
    return words


def synth_vieneu(project):
    import numpy as np
    try:
        from vieneu import Vieneu
    except ImportError:
        raise SystemExit("Chưa cài VieNeu-TTS: pip install vieneu   (GPU NVIDIA: xem README của VieNeu-TTS)")
    cfg = project.settings["voice"]["vieneu"]
    sr = SAMPLE_RATES.get(cfg["mode"], 48000)
    sentences = split_sentences(project.script.read_text(encoding="utf-8"))
    kwargs = {"mode": cfg["mode"]}
    if cfg.get("precision"):
        kwargs["precision"] = cfg["precision"]           # chỉ có tác dụng khi chạy CPU (ONNX)
    tts = Vieneu(**kwargs)
    voice = cfg["voice"]
    if cfg.get("ref_audio"):                              # nhân bản giọng từ clip 3-8 giây
        ref = Path(cfg["ref_audio"])
        ref = ref if ref.is_absolute() else project.dir / ref
        need(ref.exists(), f"Không thấy ref_audio: {ref}")
        voice = f"{project.name}_voice"
        tts.add_voice(voice, str(ref))
    print(f"[voice] VieNeu {cfg['mode']} — đang đọc {len(sentences)} câu bằng giọng '{voice}'...")
    audios = [np.asarray(a, dtype=np.float32).reshape(-1) for a in tts.infer_batch(sentences, voice=voice)]
    need(len(audios) == len(sentences), "VieNeu trả về số đoạn audio không khớp số câu")
    gap = cfg["gap_seconds"]
    silence = np.zeros(int(gap * sr), dtype=np.float32)
    parts = []
    for a in audios:
        parts += [a, silence]
    full = np.concatenate(parts[:-1])
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
    provider = project.settings["voice"]["provider"]
    if project.voice and project.words.exists() and not force:
        print(f"[voice] đã có {project.voice.name} + {project.words.name} — bỏ qua (--force để đọc lại)")
        return
    if provider == "vieneu":
        synth_vieneu(project)
    else:
        need(project.voice, f"Đưa script.txt qua voice AI rồi lưu thành {project.dir}/voice.mp3, sau đó chạy lại.")
        transcribe(project)
