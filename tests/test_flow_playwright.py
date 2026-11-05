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
        self.assertTrue(is_flow_url('https://flow.google.com/?pli=1'))
        self.assertTrue(is_flow_url('https://flow.google/project/example'))
        self.assertFalse(is_flow_url('https://flow.google.com.evil.test/'))
        self.assertFalse(is_flow_url('http://flow.google.com/'))


@unittest.skipUnless(importlib.util.find_spec('playwright'), 'Requires Playwright')
class BrowserTransport(unittest.TestCase):
    def test_generate_collect_and_fail_closed_on_login(self):
        from playwright.sync_api import sync_playwright
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory, sync_playwright() as runtime:
            adapter_config = SimpleNamespace(settings={'flow': {'playwright': {}}})
            executable = FlowBrowser(adapter_config)._executable() or runtime.chromium.executable_path
            if not Path(executable).is_file():
                self.skipTest('No Chrome/Edge/managed Chromium installed')
            context = runtime.chromium.launch_persistent_context(
                str(Path(directory)/'profile'), executable_path=executable, headless=True, timeout=20000)
            try:
                page = context.new_page()
                page.route('**/*', lambda route: route.fulfill(content_type='text/html', body='''
                    <meta charset="utf-8"><button aria-pressed="true">Image</button><textarea></textarea><button aria-label="Bắt đầu tạo">Generate still</button>
                    <button aria-label="Cài đặt" onclick="document.getElementById('settings').hidden=false">tune</button>
                    <section id="settings" hidden>
                      <input id="confirmation" type="checkbox" checked>
                      <section id="image-defaults"><h3>Chế độ mặc định của tính năng tạo hình ảnh</h3>
                        <button role="radio" aria-checked="false">x1</button><button role="radio" aria-checked="false">x2</button>
                        <button role="radio" aria-checked="false">x3</button><button role="radio" aria-checked="true">x4</button>
                      </section>
                      <section id="video-defaults"><h3>Chế độ mặc định của tính năng tạo video</h3>
                        <button role="radio" aria-checked="false">x1</button><button role="radio" aria-checked="false">x2</button>
                        <button role="radio" aria-checked="false">x3</button><button role="radio" aria-checked="true">x4</button>
                      </section>
                      <button onclick="document.getElementById('settings').hidden=true">Lưu</button>
                    </section>
                    <script>document.querySelectorAll('#image-defaults button').forEach(b=>b.onclick=()=>{
                      document.querySelectorAll('#image-defaults button').forEach(x=>x.setAttribute('aria-checked',String(x===b)));
                    });</script>
                    <script>document.querySelector('[aria-label="Bắt đầu tạo"]').onclick = e => {
                      if (!e.isTrusted) return;
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
                    self.assertEqual(page.locator('#image-defaults [aria-checked=true]').inner_text(), 'x1')
                    self.assertEqual(page.locator('#video-defaults [aria-checked=true]').inner_text(), 'x4')
                    self.assertTrue(page.locator('#confirmation').is_checked())
                    # Recheck on every submission: a later user change back to x2
                    # must be corrected again without editing video/confirmation.
                    page.evaluate("""() => {
                      document.querySelectorAll('#image-defaults button').forEach(b =>
                        b.setAttribute('aria-checked', String(b.textContent==='x2')));
                    }""")
                    self.assertEqual(adapter.call('ensure_image_count')['image_count'], 1)
                    self.assertEqual(page.locator('#image-defaults [aria-checked=true]').inner_text(), 'x1')
                    s6_collect.run(p)
                image = p.image_path(scenes[0])
                with Image.open(image) as downloaded:
                    self.assertEqual(downloaded.size, (400, 300))
                # A new gallery placeholder must not count as a finished result.
                before = adapter.call('list_tiles')['keys']
                page.evaluate("""() => {
                    const img = new Image(); img.dataset.mediaId = 'pending';
                    img.src = '/pending-image'; document.body.append(img);
                }""")
                with self.assertRaisesRegex(Exception, 'Hết thời gian'):
                    adapter.call('wait_tiles', {'before': before}, timeout=2)
                page.evaluate("document.querySelector('[data-media-id=pending]').remove()")
                self.assertEqual(adapter.call('list_tiles')['keys'], [scenes[0]['tile_key']])
                # Unknown controls fail before sending a new generation.
                page.get_by_role('button', name='Cài đặt', exact=True).evaluate('(el)=>el.remove()')
                with self.assertRaisesRegex(Exception, 'kiểm x1'):
                    adapter.call('submit', {'prompt': 'must not generate'})
                self.assertEqual(adapter.call('list_tiles')['keys'], [scenes[0]['tile_key']])
                page.goto('https://accounts.google.com/login')
                with self.assertRaises(SystemExit):
                    adapter.call('submit', {'prompt': 'Must not submit'})
            finally:
                context.close()


if __name__ == '__main__':
    unittest.main()
