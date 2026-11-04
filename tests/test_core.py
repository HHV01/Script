import json, shutil, subprocess, sys, tempfile, threading, time, unittest, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pipeline import s1_script, s3_scenes, s5_generate, s6_collect, s7_render, s4_prompts
from pipeline.bridge import Bridge, BridgeError

SCRIPT = ("Một quyết định sai lầm có thể xóa sổ cả một đế chế. Hãy nhìn vào nước Đức năm 1871, nơi mọi quyền lực tập trung vào một người. "
          "Khi người đó bị sa thải, cỗ máy tê liệt. Một quyết định sai lầm có thể xóa sổ cả một đế chế! "
          "Bài học là gì? Hệ thống phải bền hơn con người.")


def fake_words(text, per=0.4):
    out, t = [], 0.0
    for w in text.split():
        out.append({"w": w, "start": round(t, 3), "end": round(t + per - 0.05, 3)})
        t += per
    return out


class Core(unittest.TestCase):
    def test_dedupe_removes_repeated_sentence(self):
        text, dropped = s1_script.dedupe(SCRIPT)
        self.assertEqual(dropped, 1)
        self.assertEqual(text.count("xóa sổ cả một đế chế"), 1)

    def test_scenes_cover_audio_and_follow_sentences(self):
        text, _ = s1_script.dedupe(SCRIPT)
        words = fake_words(text)
        total = words[-1]["end"] + 0.1
        scenes = s3_scenes.make_scenes(text, words, total, 4, 8)
        self.assertEqual(scenes[0]["start"], 0)
        self.assertEqual(scenes[-1]["end"], round(total, 3))
        for a, b in zip(scenes, scenes[1:]):
            self.assertEqual(a["end"], b["start"])          # không hở tiếng
        self.assertEqual(" ".join(s["text"] for s in scenes).split(), text.split())  # không mất/dư chữ
        self.assertTrue(all(s["text"].rstrip()[-1] in ".!?,;:" for s in scenes))     # không cắt giữa câu/ý

    def test_alignment_survives_voice_mismatch(self):
        text, _ = s1_script.dedupe(SCRIPT)
        words = fake_words(text)
        del words[5:8]                       # whisper nghe thiếu vài từ
        words[10]["w"] = "sai"               # nghe sai 1 từ
        scenes = s3_scenes.make_scenes(text, words, words[-1]["end"] + 0.1, 4, 8)
        self.assertGreaterEqual(len(scenes), 2)

    def test_long_sentence_is_split_by_clause(self):
        text = "Câu này rất dài, " + "có nhiều ý nối tiếp nhau, " * 6 + "rồi mới kết thúc."
        words = fake_words(text, 0.5)
        scenes = s3_scenes.make_scenes(text, words, words[-1]["end"], 4, 8)
        self.assertTrue(all(s["end"] - s["start"] <= 9 for s in scenes))
        self.assertGreater(len(scenes), 1)

    def test_compose_prompt_injects_character_visual(self):
        style = {"prefix": "STYLE", "suffix": "SUF", "avoid": "bad"}
        p = s4_prompts.compose(style, {"stick-orange": {"visual": "ORANGE LOOKS"}}, "sits at a desk.", ["stick-orange"])
        self.assertEqual(p, "STYLE. ORANGE LOOKS. sits at a desk. SUF. Avoid: bad")
        self.assertNotIn("ORANGE", s4_prompts.compose(style, {"stick-orange": {"visual": "ORANGE LOOKS"}}, "a gear", []))

    def test_validate_prompts_detects_missing_and_empty(self):
        batch = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.assertEqual(s4_prompts.validate(batch, [{"id": 1, "scene_desc": "x"}, {"id": 2, "scene_desc": " "}]), [2, 3])

    def test_collect_check(self):
        sc = [{"id": i, "tile_key": f"/t{i}"} for i in (1, 2, 3)]
        self.assertEqual(s6_collect.check(sc, ["/t1", "/t2", "/t3", "/old"]), [])
        self.assertTrue(s6_collect.check(sc[:2] + [{"id": 3}], ["/t1", "/t2"]))                 # thiếu ảnh
        self.assertTrue(s6_collect.check(sc[:2] + [{"id": 3, "tile_key": "/t1"}], ["/t1", "/t2"]))  # trùng ảnh
        self.assertTrue(s6_collect.check(sc, ["/t1", "/t2"]))                                    # ảnh bị xóa khỏi Flow

    def test_flow_login_is_reported(self):
        with self.assertRaises(SystemExit) as e:
            s5_generate.require_flow_ready(
                {"url": "https://accounts.google.com/v3/signin/identifier", "promptBox": False})
        self.assertIn("đăng nhập", str(e.exception).lower())
        with self.assertRaises(SystemExit):
            s5_generate.require_flow_ready(
                {"url": "https://labs.google/fx/tools/flow/project/abc", "promptBox": False})
        s5_generate.require_flow_ready(
            {"url": "https://labs.google/fx/tools/flow/project/abc", "promptBox": True})

    def test_frame_counts_do_not_drift(self):
        scenes = [{"start": i * 6.37, "end": (i + 1) * 6.37} for i in range(140)]
        self.assertEqual(sum(s7_render.frame_counts(scenes, 30)), round(140 * 6.37 * 30))

    def test_bridge_roundtrip_and_upload(self):
        tmp = Path(tempfile.mkdtemp())
        b = Bridge(18765, tmp / "images")
        b.start()
        base = "http://127.0.0.1:18765"

        def fake_extension():
            while True:
              try:
                c = json.loads(urllib.request.urlopen(base + "/next").read())
                if c["cmd"] == "idle":
                    continue
                if c["cmd"] == "submit":
                    res = {"id": c["id"], "ok": True, "data": {"tiles": [f"/img{c['data']['scene']}"]}}
                elif c["cmd"] == "download":
                    req = urllib.request.Request(f"{base}/upload?scene={c['data']['scene']}&ext=png", data=b"x" * 2000, method="POST")
                    urllib.request.urlopen(req)
                    res = {"id": c["id"], "ok": True, "data": {}}
                else:
                    res = {"id": c["id"], "ok": False, "error": "boom"}
                urllib.request.urlopen(urllib.request.Request(base + "/result", data=json.dumps(res).encode(), method="POST"))
              except OSError:
                return
        threading.Thread(target=fake_extension, daemon=True).start()
        b.wait_connected(10)
        self.assertEqual(b.call("submit", {"scene": 7, "prompt": "p"})["tiles"], ["/img7"])
        b.call("download", {"scene": 7, "key": "/img7"})
        self.assertTrue((tmp / "images" / "007.png").exists())
        with self.assertRaises(BridgeError):
            b.call("nope")
        b.stop(); shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
