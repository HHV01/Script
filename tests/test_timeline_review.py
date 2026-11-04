import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.timeline_review import inspect


class TimelineReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.studio')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = SimpleNamespace(dir=self.base, settings={'video': {'fps': 30}})
        self.write('script.txt', 'Một hai. Ba bốn.')
        self.write('voice.wav', b'audio')
        self.write('voice.words.json', [{'w': w, 'start': i, 'end': i + 1}
                                       for i, w in enumerate(['Một', 'hai.', 'Ba', 'bốn.'])])
        self.write('scenes.json', [{'id': 1, 'text': 'Một hai.', 'start': 0, 'end': 2},
                                   {'id': 2, 'text': 'Ba bốn.', 'start': 2, 'end': 4}])
        self.manifest = {f'{name}_sha256': hashlib.sha256((self.base / file).read_bytes()).hexdigest()
                         for name, file in [('script', 'script.txt'), ('voice', 'voice.wav'), ('scenes', 'scenes.json')]}
        self.manifest.update(executor='test fixture only', beats=[
            {'scene_id': 1, 'anchor_text': 'Một', 'visual_subject': 'number', 'visual_action': 'appears',
             'at_seconds': 0, 'visual_at_seconds': 0},
            {'scene_id': 2, 'anchor_text': 'Ba', 'visual_subject': 'number', 'visual_action': 'appears',
             'at_seconds': 2, 'visual_at_seconds': 2}])
        self.write('storyboard-timing.json', self.manifest)
        self.metadata = {key: self.manifest[key] for key in ('script_sha256', 'voice_sha256')}
        self.metadata.update(timing_kind='measured', executor='test fixture only',
                             words_sha256=hashlib.sha256((self.base / 'voice.words.json').read_bytes()).hexdigest())
        self.write('voice.words.metadata.json', self.metadata)

    def write(self, file, value):
        if isinstance(value, bytes):
            (self.base / file).write_bytes(value)
        else:
            (self.base / file).write_text(value if isinstance(value, str) else json.dumps(value), encoding='utf-8')

    def run_gate(self):
        with patch('pipeline.timeline_review.audio_duration', return_value=4):
            return inspect(self.project)

    def test_valid_fixture_is_structural_only(self):
        result = self.run_gate()
        self.assertTrue(result['approved'], result)
        self.assertIn('no semantic', result['evidence']['scope'])

    def test_missing_manifest(self):
        (self.base / 'storyboard-timing.json').unlink()
        self.assertFalse(self.run_gate()['approved'])

    def test_stale_manifest(self):
        self.write('voice.wav', b'changed')
        self.assertTrue(any('stale' in b for b in self.run_gate()['blockers']))

    def test_wrong_anchor_and_lag(self):
        for field, value in [('anchor_text', 'không có'), ('visual_at_seconds', 2.5), ('at_seconds', 3)]:
            with self.subTest(field=field):
                beat = self.manifest['beats'][1]
                before = beat[field]
                beat[field] = value
                self.write('storyboard-timing.json', self.manifest)
                self.assertFalse(self.run_gate()['approved'])
                beat[field] = before

    def test_unknown_and_synthetic_provenance_block(self):
        (self.base / 'voice.words.metadata.json').unlink()
        self.assertEqual(self.run_gate()['evidence']['word_timing_kind'], 'unknown')
        self.assertFalse(self.run_gate()['approved'])
        self.write('voice.words.metadata.json', {'timing_kind': 'synthetic'})
        self.assertFalse(self.run_gate()['approved'])

    def test_word_overlap_and_scene_sequence_block(self):
        self.write('voice.words.json', [{'w': 'Một', 'start': 0, 'end': 2},
                                       {'w': 'hai', 'start': 1, 'end': 3}])
        self.assertFalse(self.run_gate()['approved'])
        self.write('scenes.json', [{'id': 1, 'text': 'Ba bốn.', 'start': 0, 'end': 4}])
        self.assertFalse(self.run_gate()['approved'])

    def test_nonfinite_times_block(self):
        self.manifest['beats'][0]['visual_at_seconds'] = float('nan')
        self.write('storyboard-timing.json', self.manifest)
        self.assertFalse(self.run_gate()['approved'])

    def test_sentence_provenance_accepts_only_boundary_anchor(self):
        self.metadata.update(timing_kind='sentence_boundaries_word_interpolation', segments=[
            {'text': 'Một hai.', 'start': 0, 'end': 2, 'word_start_index': 0, 'word_end_index': 2},
            {'text': 'Ba bốn.', 'start': 2, 'end': 4, 'word_start_index': 2, 'word_end_index': 4}])
        self.write('voice.timing.json', self.metadata)
        self.assertTrue(self.run_gate()['approved'])
        self.manifest['beats'][1].update(anchor_text='bốn', at_seconds=3, visual_at_seconds=3)
        self.write('storyboard-timing.json', self.manifest)
        self.assertTrue(any('interpolated' in b for b in self.run_gate()['blockers']))

    def test_declared_inner_scene_cue_is_not_renderer_playback(self):
        self.manifest['beats'][1].update(anchor_text='bốn', at_seconds=3, visual_at_seconds=3)
        self.write('storyboard-timing.json', self.manifest)
        result = self.run_gate()
        self.assertFalse(result['approved'])
        self.assertTrue(any('within-scene cues unsupported' in b for b in result['blockers']))


if __name__ == '__main__':
    unittest.main()
