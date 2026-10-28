"""Real browser/DOM test against an intercepted fixture; no Google account required."""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline.flow_playwright import FlowBrowser, is_flow_url
from pipeline import s5_generate, s6_collect


class FlowURLs(unittest.TestCase):
    def test_only_flow_urls(self):
        self.assertTrue(is_flow_url('https://labs.google/fx/tools/flow/project/example'))
        self.assertFalse(is_flow_url('https://labs.google.evil.test/flow'))
        self.assertFalse(is_flow_url('https://accounts.google.com/login'))


@unittest.skipUnless(importlib.util.find_spec('playwright') and shutil.which('chromium'), 'Requires Playwright and Chromium')
class BrowserTransport(unittest.TestCase):
    def test_generate_collect_and_fail_closed_on_login(self):
        from playwright.sync_api import sync_playwright
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory, sync_playwright() as runtime:
            context = runtime.chromium.launch_persistent_context(
                str(Path(directory)/'profile'), executable_path=shutil.which('chromium'), headless=True)
            try:
                page = context.new_page()
                page.route('**/*', lambda route: route.fulfill(content_type='text/html', body='''
                    <button aria-pressed="true">Image</button><textarea></textarea>
                    <script>document.querySelector('textarea').onkeydown = e => {
                      if (e.key !== 'Enter') return;
                      const canvas = document.createElement('canvas'); canvas.width=400; canvas.height=300;
                      const c=canvas.getContext('2d'), pixels=c.createImageData(400,300);
                      for(let i=0;i<pixels.data.length;i+=4) {
                        pixels.data[i]=Math.random()*255; pixels.data[i+1]=Math.random()*255;
                        pixels.data[i+2]=Math.random()*255; pixels.data[i+3]=255;
                      }
                      c.putImageData(pixels,0,0);
                      canvas.toBlob(blob => { const img=new Image(); img.src=URL.createObjectURL(blob); document.body.append(img); });
                    };</script>'''))
                page.goto('https://labs.google/fx/tools/flow/project/test')
                p = SimpleNamespace(name='test', cfg={}, images_dir=Path(directory)/'images',
                    settings={'flow': {'backend': 'playwright', 'playwright': {}, 'retries': 0,
                                      'submit_timeout': 15, 'pick': 'first', 'delay_seconds': [0, 0]}})
                scenes = [{'id': 1, 'image_prompt': 'Ancient Rome'}]
                p.load_scenes = lambda: json.loads(json.dumps(scenes))
                def save(updated): scenes[:] = updated
                p.save_scenes = save
                p.image_path = lambda scene: next(p.images_dir.glob(f"{scene['id']:03d}.*"), None)
                adapter = FlowBrowser(p)
                adapter.context, adapter.page = context, page
                self.assertTrue(adapter.call('ping')['promptBox'])
                with patch('pipeline.flow_playwright.get_browser', return_value=adapter):
                    s5_generate.run(p)
                    self.assertIn('tile_key', scenes[0])
                    s6_collect.run(p)
                image = p.image_path(scenes[0])
                with Image.open(image) as downloaded:
                    self.assertEqual(downloaded.size, (400, 300))
                self.assertEqual(adapter.call('list_tiles')['keys'], [scenes[0]['tile_key']])
                page.goto('https://accounts.google.com/login')
                with self.assertRaises(SystemExit):
                    adapter.call('submit', {'prompt': 'Must not submit'})
            finally:
                context.close()


if __name__ == '__main__':
    unittest.main()
