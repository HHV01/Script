"""Kiểm tra bước voice bằng VieNeu giả (không tải model thật)."""
import json, shutil, sys, types, unittest, wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pipeline import s2_voice, s3_scenes
from pipeline.common import PROJECTS, Project, audio_duration


class FakeVieneu:
    """Giả lập API trong README của VieNeu: infer_batch(texts, voice=) -> list[np.float32], save(audio, path)."""
    def __init__(self, **kw): self.kw = kw
    def add_voice(self, name, path): self.voice_added = (name, path)
    def list_preset_voices(self): return [("Mai Anh", "Mai Anh"), ("⭐ Hải Đăng", "Hải Đăng")]
    def infer_batch(self, texts, voice=None):
        return [np.sin(np.linspace(0, 200, int(48000 * (0.05 * len(t))))).astype(np.float32) for t in texts]
    def save(self, audio, path):
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
            w.writeframes((audio * 32767).astype("<i2").tobytes())


class VieneuStep(unittest.TestCase):
    def setUp(self):
        sys.modules["vieneu"] = types.SimpleNamespace(Vieneu=FakeVieneu)
        self.d = PROJECTS / "_t_vieneu"
        shutil.rmtree(self.d, ignore_errors=True)
        shutil.copytree(PROJECTS / "_template", self.d)
        (self.d / "script.txt").write_text(
            "Đây là câu thứ nhất của kịch bản. Câu thứ hai dài hơn một chút, có dấu phẩy. Câu cuối cùng?", encoding="utf-8")
        self.p = Project("_t_vieneu")
        self.p.settings["review"]["enabled"] = False  # unit tests isolate the voice engine; review gate tested separately

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)
        sys.modules.pop("vieneu", None)

    def test_voice_and_timestamps_are_consistent(self):
        s2_voice.run(self.p)
        words = json.loads(self.p.words.read_text(encoding="utf-8"))
        self.assertEqual(" ".join(w["w"] for w in words).split(), self.p.script.read_text(encoding="utf-8").split())
        self.assertTrue(all(a["end"] <= b["start"] + 1e-6 for a, b in zip(words, words[1:])))   # tăng dần
        total = audio_duration(self.p.voice)
        self.assertAlmostEqual(words[-1]["end"], total, delta=0.05)                              # khớp độ dài file
        scenes = s3_scenes.make_scenes(self.p.script.read_text(encoding="utf-8"), words, total, 1, 4)
        self.assertEqual(scenes[-1]["end"], round(total, 3))

    def test_second_run_is_skipped(self):
        s2_voice.run(self.p)
        t = self.p.voice.stat().st_mtime_ns
        s2_voice.run(self.p)
        self.assertEqual(self.p.voice.stat().st_mtime_ns, t)

    def test_pick_voice_by_number_or_name(self):
        presets = [("Mai Anh", "Mai Anh"), ("⭐ Hải Đăng", "Hải Đăng")]
        self.assertEqual(s2_voice.pick_voice(presets, "2"), "Hải Đăng")
        self.assertEqual(s2_voice.pick_voice(presets, "hải đăng"), "Hải Đăng")
        self.assertEqual(s2_voice.pick_voice(presets, "Mai Anh"), "Mai Anh")
        self.assertIsNone(s2_voice.pick_voice(presets, "99"))
        self.assertIsNone(s2_voice.pick_voice(presets, ""))

    def test_missing_voice_asks_user_to_choose(self):
        self.assertEqual(s2_voice.choose_voice(FakeVieneu(), ask=lambda _: "2"), "Hải Đăng")
        with self.assertRaises(SystemExit) as e:
            s2_voice.choose_voice(FakeVieneu(), ask=lambda _: "")
        self.assertIn("Chưa chọn", str(e.exception))

    def test_wrong_sample_rate_is_caught(self):
        class BadSR(FakeVieneu):
            def save(self, audio, path):
                with wave.open(path, "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)   # lưu sai sample rate
                    w.writeframes((audio * 32767).astype("<i2").tobytes())
        sys.modules["vieneu"] = types.SimpleNamespace(Vieneu=BadSR)
        with self.assertRaises(SystemExit):
            s2_voice.run(self.p)


if __name__ == "__main__":
    unittest.main()
