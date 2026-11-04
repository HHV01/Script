"""Image-to-video adapter tests; fixture WEBP, no model/GPU/cloud generation."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import ai_animation as animation


class ExistingImageAnimation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'hinh').mkdir()
        self.source = self.root/'hinh/canh-001.png'
        Image.new('RGB', (256, 144), '#aa7733').save(self.source)
        self.output = self.root/'video/comfy-output'
        self.output.mkdir(parents=True)
        Image.new('RGB', (256, 144), 'red').save(self.output/'fixture.webp', save_all=True,
            append_images=[Image.new('RGB', (256, 144), 'blue')], duration=167, loop=0)
        self.project = SimpleNamespace(name='fixture-episode', dir=self.root, _nested=True,
                                       image_path=lambda scene: self.source)
        self.scene = {'id': 1, 'start': 0, 'end': 5}
        env = patch.dict(os.environ, {'COMFYUI_INPUT_DIR': str(self.root/'hinh/comfy-input'),
                                     'COMFYUI_OUTPUT_DIR': str(self.output)})
        env.start()
        self.addCleanup(env.stop)
        self.history = {'outputs': {'6': {'images': [
            {'filename': 'fixture.webp', 'subfolder': '', 'type': 'output'}]}}}

    def render(self, **kwargs):
        return animation.animate_scene(self.project, self.scene, width=256, height=144,
                                       frames=2, fps=6, **kwargs)

    def test_animates_existing_image_without_mutating_source_or_scene(self):
        original = hashlib.sha256(self.source.read_bytes()).hexdigest()
        with patch.object(animation, 'ready', return_value=True), \
             patch.object(animation, '_json', return_value={'prompt_id': 'fixture-job'}) as submit, \
             patch.object(animation, '_wait', return_value=self.history):
            relative = self.render()
        self.assertTrue((self.root/relative).is_file())
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), original)
        self.assertNotIn('animation_video', self.scene)
        self.assertFalse(list((self.root/'video/animation').glob('*.loop.mp4')))
        self.assertNotIn('qwerty', json.dumps(submit.call_args.args))
        receipt = json.loads((self.root/relative).with_suffix('.json').read_text())
        self.assertFalse(receipt['production_attached'])

    def test_resume_uses_original_prompt_id_without_resubmitting(self):
        with patch.object(animation, 'ready', return_value=True), \
             patch.object(animation, '_json', return_value={'prompt_id': 'fixture-job'}) as submit, \
             patch.object(animation, '_wait', return_value=self.history) as wait:
            self.render()
            self.render()
        submit.assert_called_once()
        self.assertEqual([call.args[0] for call in wait.call_args_list], ['fixture-job', 'fixture-job'])

    def test_short_clip_cannot_attach_by_reversing_or_looping(self):
        with patch.object(animation, 'ready', return_value=True), \
             patch.object(animation, '_json', return_value={'prompt_id': 'fixture-job'}), \
             patch.object(animation, '_wait', return_value=self.history):
            with self.assertRaisesRegex(SystemExit, 'chưa phủ'):
                self.render(attach=True)
        self.assertNotIn('animation_video', self.scene)
        self.assertTrue((self.root/'video/animation/canh-001-svd-preview.mp4').is_file())


if __name__ == '__main__':
    unittest.main()
