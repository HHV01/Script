"""Standalone runner: real browser on synthetic DOM, never Google/paid generation."""
import base64
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch, Mock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow_gen import generate_images as flow
from PIL import Image


def png(color="red"):
    buffer = io.BytesIO()
    Image.new("RGB", (512, 512), color).save(buffer, format="PNG")
    return buffer.getvalue()


class FakeDOM:
    def __init__(self, counts, newest_first=True):
        self.counts = iter(counts)
        self.images, self.prompts = [], []
        self.prepared = None
        self.newest_first = newest_first

    def snapshot(self):
        return list(self.images)

    def prepare(self, prompt):
        self.prepared = prompt

    def submit(self):
        self.prompts.append(self.prepared)
        for _ in range(next(self.counts)):
            item = {"key": str(len(self.images)), "src": "data:image/png;base64,fixture", "ready": True}
            if self.newest_first:
                self.images.insert(0, item)
            else:
                self.images.append(item)

    def fetch(self, image):
        return png(), "image/png"

    def pause(self, seconds):
        pass


class RunnerTests(unittest.TestCase):
    def scenes(self):
        return [{"id": i, "prompt": f"  cảnh {i}\nChữ Việt 🙂 'x' \\ /  "} for i in range(1, 4)]

    def test_validation_lists_missing_before_browser_and_preserves_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"scenes.json"
            rows = [{"id": 1, "image_prompt": "  á\n🙂  "}, {"id": 2, "narration": " nguyên văn "}]
            path.write_text(json.dumps(rows), encoding="utf-8")
            with self.assertRaisesRegex(flow.FlowError, r"\[2\]"):
                flow.load_scenes(path)
            self.assertEqual(flow.load_scenes(path, True)[1]["prompt"], " nguyên văn ")
            self.assertEqual(flow.load_scenes(path, True)[0]["prompt"], rows[0]["image_prompt"])
            with patch("playwright.sync_api.sync_playwright") as browser, redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                self.assertEqual(flow.main(["--scenes", str(path), "--url", "https://labs.google/fx/tools/flow"]), 1)
                browser.assert_not_called()

    def test_three_outputs_exact_prompts_resume_without_submission(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(flow, "SETTLE_SECONDS", 0):
            state = flow.State(Path(tmp))
            dom = FakeDOM([1, 1, 1])
            gen = flow.Generator(dom, state, batch=3)
            self.assertEqual(gen.run(self.scenes()), [])
            self.assertEqual(dom.prompts, [s["prompt"] for s in self.scenes()])
            self.assertEqual(sorted(p.name for p in (Path(tmp)/"images").iterdir()),
                             ["scene_001.png", "scene_002.png", "scene_003.png"])
            gen.run(self.scenes())
            self.assertEqual(len(dom.prompts), 3)
            changed = self.scenes()
            changed[0]["prompt"] += "changed"
            with self.assertRaises(flow.FlowError):
                gen.run(changed)

    def test_excess_images_quarantined_then_individual_retries(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(flow, "SETTLE_SECONDS", 0):
            dom = FakeDOM([2, 1, 1, 1, 1, 1])
            state = flow.State(Path(tmp))
            self.assertEqual(flow.Generator(dom, state, batch=3).run(self.scenes()), [])
            self.assertEqual(len(list((Path(tmp)/"orphans").glob("*.png"))), 4)
            self.assertEqual([b["scene_ids"] for b in state.data["batches"]], [[1,2,3],[1],[2],[3]])
            self.assertEqual(len(dom.prompts), 6)

    def test_retry_limit_is_two_and_failed_can_retry_next_run(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(flow, "SETTLE_SECONDS", 0):
            dom = FakeDOM([2, 2, 2, 1])
            state = flow.State(Path(tmp))
            gen = flow.Generator(dom, state)
            self.assertEqual(gen.run(self.scenes()[:1]), [1])
            self.assertEqual(len(dom.prompts), 3)
            self.assertEqual(gen.run(self.scenes()[:1]), [])

    def test_timeout_or_interrupted_submit_blocks_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = flow.State(Path(tmp))
            dom = FakeDOM([0])
            with self.assertRaises(flow.PendingSubmission):
                flow.Generator(dom, state, timeout=0.001).run(self.scenes()[:1])
            with self.assertRaises(flow.PendingSubmission):
                flow.Generator(dom, flow.State(Path(tmp))).run(self.scenes())
            self.assertEqual(len(dom.prompts), 1)

    def test_download_failure_never_regenerates_or_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(flow, "SETTLE_SECONDS", 0):
            state = flow.State(Path(tmp))
            dom = FakeDOM([1])
            dom.fetch = Mock(side_effect=OSError("network"))
            with self.assertRaises(flow.PendingSubmission):
                flow.Generator(dom, state).run(self.scenes()[:1])
            with self.assertRaises(flow.PendingSubmission):
                flow.Generator(dom, state).run(self.scenes()[:1])
            self.assertEqual(len(dom.prompts), 1)

    def test_mime_bytes_and_size_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            dom = FakeDOM([])
            dom.fetch = Mock(return_value=(png(), "image/jpeg"))
            with self.assertRaises(flow.FlowError):
                flow.save_image(dom, {}, Path(tmp)/"image")

    def test_late_extra_unloaded_image_prevents_premature_success(self):
        clock = [0.0]
        class Delayed:
            def snapshot(self):
                rows = [{"key":"first", "src":"data:first", "ready":True}]
                if clock[0] >= 1.5:
                    rows.append({"key":"late", "src":"data:late", "ready":clock[0] >= 2.5})
                return rows
            def pause(self, seconds):
                clock[0] += seconds
        with patch.object(flow.time, "monotonic", side_effect=lambda:clock[0]):
            images, observed, result = flow.wait_images(Delayed(), set(), 1, 10)
        self.assertEqual(result, "mismatch")
        self.assertEqual(len(observed), 2)
        self.assertGreaterEqual(clock[0], 4.5)

    def test_timeout_with_unstable_full_count_still_blocks_retry(self):
        clock = [0.0]
        class Delayed:
            def snapshot(self):
                return [{"key":"one", "src":"data:one", "ready":True}]
            def pause(self, seconds):
                clock[0] += seconds
        with patch.object(flow.time, "monotonic", side_effect=lambda:clock[0]):
            self.assertEqual(flow.wait_images(Delayed(), set(), 1, 1)[2], "timeout")

    def test_reject_duplicate_ids_and_invalid_ranges_or_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"scenes.json"
            path.write_text('[{"id":1,"image_prompt":"a"},{"id":1,"image_prompt":"b"}]',encoding="utf-8")
            with self.assertRaisesRegex(flow.FlowError, "trùng"):
                flow.load_scenes(path)
            with patch("playwright.sync_api.sync_playwright") as browser, redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                self.assertEqual(flow.main(["--url","https://labs.google/fx/tools/flow","--login","--profile",str(flow.REPO/"profile")]),1)
                self.assertEqual(flow.main(["--url","https://labs.google/fx/tools/flow","--from","3","--to","1"]),1)
                browser.assert_not_called()

    def test_all_done_cli_does_not_open_browser(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(flow, "SETTLE_SECONDS", 0):
            path = Path(tmp)/"scenes.json"
            rows = [{"id":s["id"], "image_prompt":s["prompt"]} for s in self.scenes()]
            path.write_text(json.dumps(rows), encoding="utf-8")
            out = Path(tmp)/"out"
            out.mkdir()
            flow.Generator(FakeDOM([1,1,1]), flow.State(out), batch=3).run(self.scenes())
            with patch("playwright.sync_api.sync_playwright") as browser:
                self.assertEqual(flow.main(["--scenes",str(path),"--out",str(out),"--url","https://labs.google/fx/tools/flow"]), 0)
                browser.assert_not_called()

    def test_login_chrome_fallback_and_cdp_ownership(self):
        from playwright.sync_api import Error
        url = "https://labs.google/fx/tools/flow/project/local-fixture"
        for cdp in (False, True):
            with self.subTest(cdp=cdp), tempfile.TemporaryDirectory() as tmp:
                runtime = MagicMock()
                context = Mock()
                context.pages = [Mock(url=url)]
                if cdp:
                    runtime.chromium.connect_over_cdp.return_value.contexts = [context]
                else:
                    runtime.chromium.launch_persistent_context.side_effect = [Error("not installed"),context]
                args = ["--url",url,"--login","--out",tmp]
                if cdp:
                    args += ["--cdp","http://localhost:9222"]
                with patch("playwright.sync_api.sync_playwright") as start, patch("builtins.input",return_value=""):
                    start.return_value.__enter__.return_value = runtime
                    self.assertEqual(flow.main(args),0)
                if cdp:
                    context.close.assert_not_called()
                    runtime.chromium.launch_persistent_context.assert_not_called()
                else:
                    calls = runtime.chromium.launch_persistent_context.call_args_list
                    self.assertEqual(calls[0].kwargs["channel"],"chrome")
                    self.assertNotIn("channel",calls[1].kwargs)
                    context.close.assert_called_once()
                self.assertNotIn(url,(Path(tmp)/"state.json").read_text(encoding="utf-8"))

    def test_busy_profile_does_not_fallback_or_clear_locks(self):
        from playwright.sync_api import Error
        with tempfile.TemporaryDirectory() as tmp:
            runtime = MagicMock()
            runtime.chromium.launch_persistent_context.side_effect = Error("ProcessSingleton profile in use")
            with patch("playwright.sync_api.sync_playwright") as start, redirect_stderr(io.StringIO()):
                start.return_value.__enter__.return_value = runtime
                self.assertEqual(flow.main(["--url","https://labs.google/fx/tools/flow","--login","--out",tmp]),1)
            self.assertEqual(runtime.chromium.launch_persistent_context.call_count,1)


HTML = '''<!doctype html><meta charset="utf-8">
<button aria-label="Settings" onclick="document.querySelector('#settings').hidden=false">tune</button>
<section id="settings" hidden><h2>Image generation defaults</h2><div id="image-count">
<button role="radio" aria-checked="false">x1</button><button role="radio" aria-checked="true">x2</button>
<button role="radio" aria-checked="false">x3</button><button role="radio" aria-checked="false">x4</button></div>
<h2>Video generation defaults</h2><div><button role="radio" aria-checked="false">x1</button>
<button role="radio" aria-checked="true">x2</button><button role="radio">x3</button><button role="radio">x4</button></div>
<button onclick="document.querySelector('#settings').hidden=true">Save</button></section>
<textarea></textarea><div><button>Nano Banana</button><button id="submit">Send</button></div><main></main>
<script>
window.submitted=[]; window.oldest=false; window.busyCount=0;
document.querySelectorAll('#image-count button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('#image-count button').forEach(c=>c.setAttribute('aria-checked',String(c===b)));
});
document.querySelector('#submit').onclick=()=>{
 const text=document.querySelector('textarea').value; submitted.push(text);
 setTimeout(()=>{document.querySelector('textarea').value='';},50);
 const index=submitted.length; const image=new Image(); image.dataset.mediaId=String(index);
 image.src=window.sourceImages[index-1];
 setTimeout(()=>{if(oldest)document.querySelector('main').append(image);else document.querySelector('main').prepend(image);},index*30);
};
</script>'''


class RealBrowserFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.runtime = sync_playwright().start()
        try:
            cls.browser = cls.runtime.chromium.launch(channel="chrome", headless=True)
        except Exception:
            try:
                cls.browser = cls.runtime.chromium.launch(headless=True)
            except Exception:
                cls.runtime.stop()
                raise unittest.SkipTest("No installed Chrome/Chromium for DOM fixture")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()

    def test_three_scene_batch_both_dom_directions_and_exact_text(self):
        for oldest in (False, True):
            with self.subTest(oldest=oldest), tempfile.TemporaryDirectory() as tmp:
                page = self.browser.new_page()
                try:
                    page.set_content(HTML)
                    colors = ["red", "green", "blue"]
                    sources = ["data:image/png;base64," + base64.b64encode(png(c)).decode() for c in colors]
                    # Exercise blob: and data: fetching in the browser.
                    page.evaluate("""async cfg => {
                        window.oldest=cfg.oldest; window.sourceImages=cfg.sources;
                        const blob=await (await fetch(sourceImages[1])).blob();
                        sourceImages[1]=URL.createObjectURL(blob);
                    }""", {"oldest":oldest,"sources":sources})
                    scenes = RunnerTests().scenes()
                    state = flow.State(Path(tmp))
                    gen = flow.Generator(flow.FlowDOM(page), state, batch=3, oldest_first=oldest, timeout=5)
                    self.assertEqual(gen.run(scenes), [])
                    self.assertEqual(page.evaluate("submitted"), [s["prompt"] for s in scenes])
                    for index, color in enumerate(colors, 1):
                        with Image.open(Path(tmp)/"images"/f"scene_{index:03d}.png") as image:
                            self.assertEqual(image.getpixel((0,0)), Image.new("RGB",(1,1),color).getpixel((0,0)))
                    gen.run(scenes)
                    self.assertEqual(page.evaluate("submitted.length"), 3)
                    self.assertEqual(page.locator('#image-count button[aria-checked="true"]').inner_text(), "x1")
                    self.assertEqual(page.locator('#settings > div').nth(1).locator('[aria-checked="true"]').inner_text(), "x2")
                finally:
                    page.close()

    def test_missing_settings_blocks_before_any_submit(self):
        page = self.browser.new_page()
        try:
            page.set_content('<textarea></textarea><button>Nano</button><button>Send</button>')
            with self.assertRaises(flow.FlowError):
                flow.FlowDOM(page).prepare("unchanged")
            self.assertEqual(page.locator('textarea').input_value(), "")
        finally:
            page.close()

    def test_observed_direct_mode_sets_x1_and_uses_explicit_send(self):
        page = self.browser.new_page()
        try:
            page.set_content('''<button id="agent" aria-pressed="true" onclick="this.setAttribute('aria-pressed','false')">Tác nhân</button>
<button id="settings" aria-label="Điều kiện kích hoạt cài đặt" onclick="document.querySelector('.cdk-overlay-pane').hidden=false">Nano Banana 2.1 crop_16_9 x2</button>
<div class="cdk-overlay-pane" hidden>
<button role="radio" aria-checked="true">image Hình ảnh</button><button role="radio" aria-checked="false">videocam Video</button>
<button role="radio" aria-checked="true">crop_16_9 16:9</button>
<div id="counts"><button role="radio" aria-checked="false">x1</button><button role="radio" aria-checked="true">x2</button><button role="radio">x3</button><button role="radio">x4</button></div></div>
<div contenteditable="true" role="textbox"></div>
<button aria-label="Bắt đầu tạo" id="send">arrow_forward</button>
<script>window.submitted=[];
document.querySelectorAll('#counts button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('#counts button').forEach(c=>c.setAttribute('aria-checked',String(c===b)));
 document.querySelector('#settings').innerText='Nano Banana 2.1 crop_16_9 '+b.innerText;
});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelector('.cdk-overlay-pane').hidden=true});
document.querySelector('#send').onclick=()=>{const editor=document.querySelector('[contenteditable]');submitted.push(editor.innerText);setTimeout(()=>editor.innerText='',100)};
</script>''')
            dom = flow.FlowDOM(page)
            prompt = "exact character and room description"
            dom.prepare(prompt)
            dom.submit()
            self.assertEqual(page.evaluate('submitted'),[prompt])
            self.assertEqual(page.locator('#agent').get_attribute('aria-pressed'),'false')
            self.assertIn('x1',page.locator('#settings').inner_text())
            self.assertEqual(page.get_by_role('textbox').inner_text(),'')
        finally:
            page.close()

    def test_http_image_download_uses_browser_cookie_and_real_mime(self):
        body = png("blue")
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                ok = self.headers.get("Cookie") == "fixture_session=local_test"
                self.send_response(200 if ok else 403)
                self.send_header("Content-Type","image/png")
                self.end_headers()
                self.wfile.write(body if ok else b"not authenticated")
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1",0),Handler)
        worker = threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        context = self.browser.new_context()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            context.add_cookies([{"name":"fixture_session","value":"local_test","url":origin}])
            page = context.new_page()
            with tempfile.TemporaryDirectory() as tmp:
                path, sha = flow.save_image(flow.FlowDOM(page), {"src":origin+"/fixture.png"},Path(tmp)/"image")
                self.assertEqual(path.suffix,".png")
                self.assertEqual(path.read_bytes(),body)
                self.assertEqual(sha,flow.digest(body))
        finally:
            context.close()
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
