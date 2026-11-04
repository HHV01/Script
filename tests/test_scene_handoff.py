import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import s3_scenes, s7_render

class SceneHandoff(unittest.TestCase):
    def test_short_sentences_switch_without_minimum_hold(self):
        text = 'Não lưu ký ức. Mèo ngủ.'
        words = [{'w': w, 'start': i * .3, 'end': (i+1)*.3} for i, w in enumerate(text.split())]
        scenes = s3_scenes.make_scenes(text, words, len(words)*.3, 8, 12)
        self.assertEqual(len(scenes), 2)
        self.assertEqual([s['text'] for s in scenes], ['Não lưu ký ức.', 'Mèo ngủ.'])
        self.assertEqual([(s['word_start_index'], s['word_end_index']) for s in scenes], [(0,4),(4,6)])
        self.assertEqual(scenes[0]['end'], scenes[1]['start'])
        self.assertEqual(scenes[0]['timing_basis'], 'provided_word_timestamps_unverified')

    def project(self, root):
        p = SimpleNamespace(dir=root, script=root/'script.txt', voice=root/'voice.wav',
                            words=root/'voice.words.json', scenes_file=root/'scenes.json',
                            settings={'scenes': {'min_seconds':8,'max_seconds':12}, 'voice': {'provider':'vieneu'}})
        p.script.write_text('Câu đầu. Câu sau.', encoding='utf-8')
        p.voice.write_bytes(b'fake voice bytes')
        p.words.write_text(json.dumps([{'w': w, 'start': i*.5, 'end': (i+1)*.5} for i,w in enumerate('Câu đầu. Câu sau.'.split())]), encoding='utf-8')
        p.save_scenes = lambda scenes: p.scenes_file.write_text(json.dumps(scenes), encoding='utf-8')
        return p

    def test_renderer_refuses_missing_handoff_before_touching_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.project(Path(tmp))
            p.scenes_file.write_text('[]', encoding='utf-8')
            p.final = p.dir/'final.mp4'
            p.final.write_bytes(b'existing published media')
            with patch.object(s7_render.shutil, 'which', return_value='ffmpeg'), patch.object(s7_render, 'ff') as render:
                with self.assertRaisesRegex(SystemExit, 'provenance'):
                    s7_render.run(p)
                render.assert_not_called()
            self.assertEqual(p.final.read_bytes(), b'existing published media')

    def test_stale_cache_blocked_without_mutating_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.project(Path(tmp))
            with patch.object(s3_scenes, 'audio_duration', return_value=2):
                s3_scenes.run(p)
            original = p.scenes_file.read_bytes()
            image = p.dir/'001.png'; image.write_bytes(b'keep image')
            s3_scenes.run(p)
            for target in (p.script, p.voice, p.words):
                prior = target.read_bytes(); target.write_bytes(prior+b' ')
                with self.assertRaisesRegex(SystemExit, 'provenance'):
                    s3_scenes.run(p)
                self.assertEqual(original, p.scenes_file.read_bytes())
                self.assertEqual(image.read_bytes(), b'keep image')
                target.write_bytes(prior)
            p.settings['scenes']['max_seconds'] = 10
            with self.assertRaises(SystemExit): s3_scenes.run(p)

    def test_missing_source_blocks_legacy_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.project(Path(tmp)); p.scenes_file.write_text('[]')
            with self.assertRaises(SystemExit): s3_scenes.run(p)
            self.assertEqual(p.scenes_file.read_text(), '[]')

if __name__ == '__main__': unittest.main()
