import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import s6_collect
from pipeline.stages import STAGES

class LocalImages(unittest.TestCase):
    def test_missing_or_corrupt_image_blocks_without_saving_partial_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new('RGB', (16, 16)).save(root/'001.png')
            (root/'002.png').write_bytes(b'broken')
            scenes = [{'id': 1}, {'id': 2}]
            project = SimpleNamespace(images_dir=root, load_scenes=lambda:scenes,
                image_path=lambda s:root/f"{s['id']:03d}.png", save_scenes=Mock())
            with self.assertRaises(SystemExit): s6_collect.run(project)
            project.save_scenes.assert_not_called()
            self.assertNotIn('image', scenes[0])
            Image.new('RGB', (16, 16)).save(root/'002.png')
            s6_collect.run(project)
            project.save_scenes.assert_called_once_with(scenes)
            self.assertEqual(scenes[1]['image'], '002.png')
            (root/'002.png').unlink()
            with self.assertRaises(SystemExit): s6_collect.run(project)
    def test_pipeline_has_no_automatic_generation_stage(self):
        self.assertNotIn('generate', STAGES)
