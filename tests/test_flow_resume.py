import copy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import s5_generate as flow
from pipeline.bridge import BridgeError


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.scenes = [{'id': 1, 'image_prompt': 'one'}, {'id': 2, 'image_prompt': 'two'}]
        self.p = SimpleNamespace(dir=root, images_dir=root/'images', settings={'flow': {
            'retries': 5, 'submit_timeout': 1, 'pick': 'first', 'delay_seconds': [0, 0]}})
        self.p.images_dir.mkdir()
        self.p.load_scenes = lambda: copy.deepcopy(self.scenes)
        self.p.save_scenes = lambda scenes: setattr(self, 'scenes', copy.deepcopy(scenes))
        self.p.image_path = lambda s: next(self.p.images_dir.glob(f"{s['id']:03d}.*"), None)
        self.bridge = Mock()
        self.connection = patch.object(flow, 'connect', return_value=self.bridge)
        self.connect = self.connection.start()
        self.addCleanup(self.connection.stop)

    def image(self, sid):
        Image.new('RGB', (256, 256)).save(self.p.images_dir/f'{sid:03d}.png')

    def success(self, action, args, **kwargs):
        if action == 'submit':
            return {'tiles': [f"tile-{args['scene']}"]}
        self.image(args['scene'])
        return {}

    def test_local_image_skips_browser_without_tile_or_prompt(self):
        for s in self.scenes:
            self.image(s['id'])
            s.pop('image_prompt')
        flow.run(self.p)
        self.connect.assert_not_called()

    def test_known_tile_only_downloads(self):
        self.scenes[0]['tile_key'] = 'old'
        self.scenes[0].pop('image_prompt')
        self.bridge.call.side_effect = self.success
        flow.run(self.p, scene_ids=[1])
        self.assertEqual([c.args[0] for c in self.bridge.call.call_args_list], ['download'])

    def test_ambiguous_submit_persists_and_prevents_repeat(self):
        self.bridge.call.side_effect = BridgeError('timeout')
        with self.assertRaises(SystemExit):
            flow.run(self.p, scene_ids=[1])
        self.assertIn('unknown', flow.attempt_path(self.p, self.scenes[0]).read_text())
        self.bridge.reset_mock()
        with self.assertRaises(SystemExit):
            flow.run(self.p, scene_ids=[1])
        self.bridge.call.assert_not_called()

    def test_subset_saves_full_list(self):
        other = copy.deepcopy(self.scenes[1])
        self.bridge.call.side_effect = self.success
        flow.run(self.p, scene_ids=[1])
        self.assertEqual(len(self.scenes), 2)
        self.assertEqual(self.scenes[1], other)
        self.assertEqual(self.scenes[0]['tile_key'], 'tile-1')

    def test_download_failure_never_submits_again(self):
        self.bridge.call.side_effect = lambda action, args, **kw: ({'tiles': ['saved']} if action == 'submit' else (_ for _ in ()).throw(BridgeError('download timeout')))
        with self.assertRaises(SystemExit):
            flow.run(self.p, scene_ids=[1])
        self.assertEqual(self.scenes[0]['tile_key'], 'saved')
        self.bridge.reset_mock()
        self.bridge.call.side_effect = self.success
        flow.run(self.p, scene_ids=[1])
        self.assertEqual([c.args[0] for c in self.bridge.call.call_args_list], ['download'])

    def test_no_sleep_after_last_scene_or_download_only(self):
        self.scenes[0]['tile_key'] = 'old'
        self.bridge.call.side_effect = self.success
        self.p.settings['flow']['delay_seconds'] = [10, 10]
        with patch.object(flow.time, 'sleep') as sleep:
            flow.run(self.p)
        sleep.assert_not_called()
        result = __import__('json').loads(flow.attempt_path(self.p, self.scenes[0]).read_text())
        self.assertEqual(result['operation'], 'download_only')
        self.assertGreaterEqual(result['elapsed_seconds'], 0)

    def test_cooldown_only_between_new_submissions(self):
        self.bridge.call.side_effect = self.success
        self.p.settings['flow']['delay_seconds'] = [10, 10]
        with patch.object(flow.time, 'sleep') as sleep:
            flow.run(self.p)
        sleep.assert_called_once()
        self.assertGreater(sleep.call_args.args[0], 0)
        self.assertLessEqual(sleep.call_args.args[0], 10)

    def test_nested_project_preserves_legacy_ambiguous_ledger(self):
        self.p._nested = True
        legacy = self.p.dir / 'flow-attempts' / '001.json'
        legacy.parent.mkdir()
        legacy.write_text('{"status": "unknown"}')
        with self.assertRaises(SystemExit):
            flow.run(self.p, scene_ids=[1])
        self.connect.assert_not_called()
        self.assertEqual(flow.attempt_path(self.p, self.scenes[0]).parent,
                         self.p.images_dir / 'flow-attempts')

    def test_full_storyboard_keeps_all_116_images_and_timing(self):
        self.scenes = [{'id': i, 'image_prompt': f'scene {i}',
                        'text': f'narration {i}', 'start': (i-1)*7, 'end': i*7,
                        'word_start_index': i-1, 'word_end_index': i}
                       for i in range(1, 117)]
        original = copy.deepcopy(self.scenes)
        self.bridge.call.side_effect = self.success
        flow.run(self.p)
        self.assertEqual(len(self.scenes), 116)
        self.assertEqual(len({s['tile_key'] for s in self.scenes}), 116)
        self.assertEqual(len(list(self.p.images_dir.glob('*.png'))), 116)
        for before, after in zip(original, self.scenes):
            self.assertEqual(before, {key: after[key] for key in before})
        result = __import__('json').loads(flow.attempt_path(self.p, self.scenes[-1]).read_text())
        self.assertIn('submit_wait_seconds', result)
        self.assertIn('download_verify_seconds', result)

    def test_same_tile_cannot_cover_two_scenes(self):
        self.scenes[0]['tile_key'] = 'already-used'
        def duplicate(action, args, **kwargs):
            if action == 'submit':
                return {'tiles': ['already-used']}
            self.image(args['scene'])
            return {}
        self.bridge.call.side_effect = duplicate
        with self.assertRaisesRegex(SystemExit, 'gắn nhầm ảnh'):
            flow.run(self.p)
        self.assertNotIn('tile_key', self.scenes[1])
        self.assertFalse((self.p.images_dir/'002.png').exists())

    def test_duplicate_scene_ids_block_before_browser(self):
        self.scenes[1]['id'] = 1
        with self.assertRaisesRegex(SystemExit, 'ID cảnh trùng'):
            flow.run(self.p)
        self.connect.assert_not_called()

    def test_invalid_id_fails_before_browser(self):
        with self.assertRaises(SystemExit):
            flow.run(self.p, scene_ids=[999])
        self.connect.assert_not_called()

    def test_tiny_or_invalid_file_does_not_skip(self):
        Image.new('RGB', (10, 10)).save(self.p.images_dir/'001.png')
        self.bridge.call.side_effect = self.success
        flow.run(self.p, scene_ids=[1])
        self.assertEqual(self.bridge.call.call_args_list[0].args[0], 'submit')


if __name__ == '__main__':
    unittest.main()
