import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import layer_motion as motion
from pipeline.script_review import recording_plan
from pipeline.s2_voice import apply_tempo, word_timeline
from pipeline import s7_render


class LayerMotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        Image.new('RGBA', (12, 12), 'red').save(self.root/'piece.png')
        self.plan = {'duration': .4, 'background': '#ffffff', 'layers': [
            {'id': 'piece', 'kind': 'image', 'asset': 'piece.png', 'keyframes': [
                {'at': 0, 'ease': 'linear', 'props': {'x': 5, 'y': 25}},
                {'at': .4, 'props': {'x': 85, 'y': 25}}]}]}

    def test_object_moves_but_background_stays_fixed(self):
        original = copy.deepcopy(self.plan)
        painter = motion.Painter(self.plan, self.root, 128, 72)
        a, b = painter.frame(0), painter.frame(.4)
        self.assertEqual(a.getpixel((8, 28)), (255, 0, 0))
        self.assertEqual(b.getpixel((8, 28)), (255, 255, 255))
        self.assertEqual(b.getpixel((88, 28)), (255, 0, 0))
        self.assertEqual(a.getpixel((127, 0)), b.getpixel((127, 0)))
        self.assertEqual(original, self.plan)

    def test_real_render_keeps_declared_frame_count_and_has_no_audio(self):
        output = self.root/'preview.mp4'
        motion.render_plan(self.plan, self.root, output, 128, 72, 10)
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(output)],
                               capture_output=True, text=True, check=True)
        streams = json.loads(probe.stdout)['streams']
        self.assertEqual(len(streams), 1)
        self.assertEqual(streams[0]['codec_type'], 'video')
        self.assertEqual(int(streams[0]['nb_frames']), 4)

    def test_design_canvas_scales_consistently_for_larger_export(self):
        self.plan.update(canvas_width=128, canvas_height=72)
        frame = motion.Painter(self.plan, self.root, 256, 144).frame(0)
        self.assertEqual(frame.getpixel((16, 56)), (255, 0, 0))
        self.assertEqual(frame.size, (256, 144))
        with self.assertRaisesRegex(ValueError, 'aspect ratio'):
            motion.Painter(self.plan, self.root, 128, 128)

    def test_stale_voice_blocks_production_before_encoder(self):
        (self.root/'script.txt').write_text('A sentence.', encoding='utf-8')
        (self.root/'voice.wav').write_bytes(b'voice-version-one')
        scene = {'id': 1, 'text': 'A sentence.', 'start': 0, 'end': .4, 'motion_plan': 'plan.json'}
        self.plan.update(scene_id=1, sources={'script_sha256': motion.sha(self.root/'script.txt'),
                                            'voice_sha256': motion.sha(self.root/'voice.wav'),
                                            'scene_sha256': motion.scene_hash(scene)})
        (self.root/'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')
        project = SimpleNamespace(dir=self.root, script=self.root/'script.txt', voice=self.root/'voice.wav')
        (self.root/'voice.wav').write_bytes(b'voice-version-two')
        with patch.object(motion, 'render_plan') as render:
            with self.assertRaisesRegex(ValueError, 'stale'):
                motion.render_scene(project, scene, self.root/'out.mp4', 128, 72, 10, 4)
            render.assert_not_called()

    def test_prototype_cannot_be_used_as_voice_bound_scene(self):
        (self.root/'script.txt').write_text('A sentence.', encoding='utf-8')
        (self.root/'voice.wav').write_bytes(b'voice')
        (self.root/'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')
        project = SimpleNamespace(dir=self.root, script=self.root/'script.txt', voice=self.root/'voice.wav')
        scene = {'id': 1, 'text': 'A sentence.', 'start': 0, 'end': .4, 'motion_plan': 'plan.json'}
        with self.assertRaisesRegex(ValueError, 'provenance'):
            motion.render_scene(project, scene, self.root/'out.mp4', 128, 72, 10, 4)

    def test_invalid_event_and_external_asset_rejected(self):
        self.plan['layers'][0]['keyframes'][1]['at'] = .8
        with self.assertRaises(ValueError):
            motion.validate(self.plan)
        with self.assertRaises(ValueError):
            motion.local_path(self.root, '../outside.png')

    def test_required_object_motion_blocks_static_fallback_before_encoder(self):
        project = SimpleNamespace(dir=self.root, voice=self.root/'voice.wav',
                                  settings={'render': {'require_object_motion': True}})
        project.load_scenes = lambda: [{'id': 1, 'text': 'Fixture.', 'start': 0, 'end': .4}]
        project.image_path = lambda scene: self.root/'piece.png'
        # Source/timing guards have separate tests; this fixture isolates the
        # stricter animation requirement, not a production quality approval.
        with patch('pipeline.s3_scenes.validate_source'), \
             patch('pipeline.timeline_review.inspect', return_value={'approved': True, 'blockers': []}), \
             patch.object(s7_render, 'ff') as encoder:
            with self.assertRaisesRegex(SystemExit, 'không dùng zoom'):
                s7_render.run(project)
            encoder.assert_not_called()


class DeliveryTests(unittest.TestCase):
    def test_exact_cue_changes_pace_pause_without_changing_words(self):
        text = 'Câu hỏi đầu? Câu trả lời sau.'
        plan = recording_plan(text, {'delivery_cues': [
            {'text': 'Câu hỏi đầu?', 'tempo': .96, 'pause_after': .48}]})
        self.assertEqual(plan['segments'][0]['tempo'], .96)
        self.assertEqual(plan['segments'][0]['pause_after'], .48)
        self.assertEqual(plan['segments'][-1]['pause_after'], 0)
        self.assertEqual(' '.join(s['text'] for s in plan['segments']), text)

    def test_stale_or_ambiguous_cue_blocks(self):
        for text, anchor in [('Câu mới.', 'Câu cũ.'), ('Lặp lại. Lặp lại.', 'Lặp lại.')]:
            with self.assertRaises(SystemExit):
                recording_plan(text, {'delivery_cues': [{'text': anchor, 'tempo': 1.04}]})

    def test_audio_tempo_uses_new_duration_for_timestamps(self):
        sr = 48000
        audio = np.sin(np.arange(sr*2)*2*np.pi*220/sr).astype(np.float32)
        changed = apply_tempo(audio, sr, 1.08)
        duration = len(changed)/sr
        self.assertAlmostEqual(duration, 2/1.08, delta=.04)
        words = word_timeline(['Một câu.'], [duration], [0])
        self.assertAlmostEqual(words[-1]['end'], duration, delta=.001)


if __name__ == '__main__':
    unittest.main()
