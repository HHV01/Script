"""Generate scene images without rewriting prompts. Run with --help for usage.

DOM order is a calibration assumption, not proof of prompt/result attribution.
Interrupted/timeout submissions are blocked on resume instead of blindly repeated.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit

for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# UI-specific selectors only. Unknown/ambiguous controls fail before submission.
SELECTORS = {
    "prompt": 'textarea:visible, [contenteditable="true"]:visible',
    "images": 'img[data-media-id], img[src*="flow-content"], '
              'img[src*="googleusercontent"], img[src*="/asb/"], '
              'img[src^="blob:"], img[src^="data:image/"]',
    "buttons": 'button:visible, [role="button"]:visible',
    "model_pattern": r"banana|nano|imagen",
    "settings_name": r"^(Cài đặt|Settings)$",
    "settings_icon": "tune",
    "image_heading": r"^(Chế độ mặc định của tính năng tạo hình ảnh|Image generation defaults|Default image generation settings)$",
    "save_name": r"^(Lưu|Save)$",
    "agent_name": r"^(Tác nhân|Agent)$",
    "direct_settings_name": r"^(Điều kiện kích hoạt cài đặt|Settings trigger)$",
    "send_name": r"^(Bắt đầu tạo|Start creating|Generate|Create)$",
}
POLL_SECONDS = 0.5
SETTLE_SECONDS = 2.0
SEND_GAP_SECONDS = 1.0
EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
REPO = Path(__file__).resolve().parents[1]


class FlowError(RuntimeError):
    pass


class PendingSubmission(FlowError):
    """No safe automatic retry after a possibly successful submission."""


def digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def atomic_json(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_scenes(path, fallback=False, first=None, last=None):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise FlowError("scenes.json phải là danh sách cảnh không rỗng.")
    ids, missing, scenes = set(), [], []
    for row in data:
        if not isinstance(row, dict) or type(row.get("id")) is not int or row["id"] < 1:
            raise FlowError("Mỗi cảnh cần id là số nguyên dương.")
        sid = row["id"]
        if sid in ids:
            raise FlowError(f"ID cảnh trùng: {sid}")
        ids.add(sid)
        prompt = row.get("image_prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            prompt = row.get("narration") if fallback else None
        if not isinstance(prompt, str) or not prompt.strip():
            missing.append(sid)
        else:
            scenes.append({"id": sid, "prompt": prompt})  # exact string, no normalization
    if missing:
        raise FlowError(f"Thiếu image_prompt (hoặc narration fallback hợp lệ): {missing}")
    selected = [s for s in scenes if (first is None or s["id"] >= first)
                and (last is None or s["id"] <= last)]
    if not selected:
        raise FlowError("Không có cảnh trong khoảng ID đã chọn.")
    return selected


@contextmanager
def output_lock(out):
    """OS lock released on process exit; retain lock file (no destructive cleanup)."""
    out.mkdir(parents=True, exist_ok=True)
    handle = (out / ".run.lock").open("a+b")
    locked = False
    try:
        if sys.platform == "win32":
            import msvcrt
            handle.seek(0, 2)
            if not handle.tell():
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        yield
    except OSError as error:
        if locked:
            raise
        raise FlowError("Không khóa được thư mục out; kiểm tra quyền hoặc worker đang dùng.") from error
    finally:
        if locked:
            if sys.platform == "win32":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()


class State:
    def __init__(self, out):
        self.out = out
        self.path = out / "state.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {
            "version": 1, "scenes": {}, "batches": [], "orphans": []}
        if self.data.get("version") != 1:
            raise FlowError("Phiên bản state không được hỗ trợ; giữ nguyên để đối chiếu.")

    def save(self):
        atomic_json(self.path, self.data)

    def remaining(self, scenes):
        remaining = []
        pending = [sid for sid, row in self.data["scenes"].items()
                   if row.get("status") in ("pending", "needs_review")]
        if pending:
            raise PendingSubmission(f"Out có lần gửi chưa xác định cho cảnh {pending}; đối chiếu gallery trước khi tiếp tục.")
        for scene in scenes:
            row = self.data["scenes"].get(str(scene["id"]), {})
            if row and row.get("prompt_sha256") != digest(scene["prompt"]):
                raise FlowError(f"Prompt cảnh {scene['id']} đã đổi; dùng out mới, không tái dùng state cũ.")
            if row.get("status") in ("pending", "needs_review"):
                raise PendingSubmission(f"Cảnh {scene['id']} có lần gửi chưa xác định. Đối chiếu gallery và state trước khi chạy tiếp; không tự gửi lại.")
            if row.get("status") == "done":
                path = (self.out / row["file"]).resolve()
                if not path.is_relative_to(self.out.resolve() / "images"):
                    raise FlowError("Đường dẫn ảnh trong state không hợp lệ.")
                if not path.is_file() or digest(path.read_bytes()) != row.get("sha256"):
                    raise FlowError(f"Ảnh done cảnh {scene['id']} thiếu/đã đổi; cần đối chiếu trước khi gen lại.")
                continue
            remaining.append(scene)
        return remaining

    def set_scene(self, scene, status, **fields):
        self.data["scenes"][str(scene["id"])] = {
            "prompt_sha256": digest(scene["prompt"]), "status": status, **fields}
        self.save()


class FlowDOM:
    def __init__(self, page):
        self.page = page

    def pause(self, seconds):
        self.page.wait_for_timeout(seconds * 1000)

    def snapshot(self):
        return self.page.locator(SELECTORS["images"]).evaluate_all("""images => {
            const seen = new Set(), results = [];
            for (const image of images) {
                const src = image.currentSrc || image.src;
                if (!src) continue;
                // Keep query as part of identity unless Flow provides a stable media ID.
                const key = image.dataset.mediaId ? 'media:' + image.dataset.mediaId : src;
                if (seen.has(key)) continue;
                seen.add(key);
                results.push({key, src, ready: image.complete &&
                    Math.min(image.naturalWidth, image.naturalHeight) >= 512});
            }
            return results;
        }""")

    def ensure_x1(self):
        """Confirm image section only; never touch the confirmation/video settings."""
        agent = self.page.get_by_role("button", name=re.compile(SELECTORS["agent_name"], re.I))
        if agent.count() == 1 and agent.get_attribute("aria-pressed") == "true":
            agent.click()
            self.page.wait_for_function("""pattern => [...document.querySelectorAll('button')].some(
                b => new RegExp(pattern,'i').test(b.innerText.trim()) && b.getAttribute('aria-pressed')==='false')""",
                arg=SELECTORS["agent_name"], timeout=5000)
        direct = self.page.get_by_role("button", name=re.compile(SELECTORS["direct_settings_name"], re.I))
        if direct.count() == 1:
            panels = self.page.locator('.cdk-overlay-pane:visible').filter(
                has=self.page.get_by_role('radio', name='x1', exact=True))
            if panels.count() == 0:
                direct.click()
                panels.wait_for(state='visible', timeout=5000)
            if panels.count() != 1:
                raise FlowError("Không xác định được panel tạo ảnh trực tiếp; chưa gửi prompt.")
            mode = panels.get_by_role('radio', name=re.compile(r'^(image\s*)?(Hình ảnh|Image)$', re.I))
            if mode.count() != 1:
                raise FlowError("Không xác định được chế độ ảnh trực tiếp; chưa gửi prompt.")
            if mode.get_attribute('aria-checked') != 'true':
                mode.click()
            ratio = panels.get_by_role('radio', name=re.compile(r'16:9$'))
            one = panels.get_by_role('radio', name='x1', exact=True)
            if ratio.count() != 1 or one.count() != 1:
                raise FlowError("Thiếu lựa chọn 16:9/x1 trong panel ảnh; chưa gửi prompt.")
            if ratio.get_attribute('aria-checked') != 'true':
                ratio.click()
            if one.get_attribute('aria-checked') != 'true':
                one.click()
            self.page.wait_for_function("""() => {
                const panel=[...document.querySelectorAll('.cdk-overlay-pane')].find(p=>p.getClientRects().length);
                return panel && [...panel.querySelectorAll('[role=radio]')].some(b=>
                    b.innerText.trim()==='x1' && b.getAttribute('aria-checked')==='true');
            }""", timeout=5000)
            self.page.keyboard.press('Escape')
            panels.wait_for(state='hidden', timeout=5000)
            summary = direct.inner_text()
            if not re.search(r'\bx1\b', summary) or not any(r in summary for r in ('16:9', 'crop_16_9')):
                raise FlowError("Cài đặt ảnh trực tiếp chưa lưu x1/16:9; chưa gửi prompt.")
            return
        script = """cfg => {
            const visible = el => el.getClientRects().length && !el.disabled;
            const heading = [...document.querySelectorAll('h1,h2,h3,h4,div,p,span,label')]
                .filter(visible).filter(el => new RegExp(cfg.image_heading, 'i').test(el.textContent.trim()));
            // Pick innermost exact heading, not wrappers carrying the same text.
            const h = heading.find(el => !heading.some(other => other !== el && el.contains(other)));
            const scopes = [];
            if (h) {
                // Some layouts put heading and choices in adjacent elements.
                if (h.nextElementSibling && !/^H[1-6]$/.test(h.nextElementSibling.tagName))
                    scopes.push(h.nextElementSibling);
                for (let el = h; el; el = el.parentElement) scopes.push(el);
            }
            for (const el of scopes) {
                const choices = [...el.querySelectorAll('button,[role="radio"],[role="tab"]')]
                    .filter(visible).filter(b => /^[x×][1-4]$/i.test(b.textContent.trim()));
                if (choices.length > 4) break;
                if (choices.length !== 4) continue;
                const one = choices.filter(b => /^[x×]1$/i.test(b.textContent.trim()));
                if (one.length !== 1) return 'ambiguous';
                const selected = b => ['aria-checked','aria-selected','aria-pressed'].some(a => b.getAttribute(a)==='true');
                if (!selected(one[0])) { one[0].click(); return 'selecting'; }
                if (choices.some(b => b !== one[0] && selected(b))) return 'ambiguous';
                return 'verified';
            }
            return 'missing';
        }"""
        status = self.page.evaluate(script, SELECTORS)
        if status == "missing":
            buttons = self.page.get_by_role("button", name=re.compile(SELECTORS["settings_name"], re.I))
            # Observed tune icon; do not open account settings with the same accessible name.
            buttons = buttons.filter(has_text=SELECTORS["settings_icon"])
            if buttons.count() != 1:
                raise FlowError("Không xác định được cài đặt x1. Kiểm tra DOM thật; chưa gửi prompt.")
            buttons.click()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = self.page.evaluate(script, SELECTORS)
            if status == "verified":
                break
            self.pause(0.1)
        else:
            raise FlowError("Chưa xác nhận x1 trong riêng mục ảnh; chưa gửi prompt.")
        saves = self.page.get_by_role("button", name=re.compile(SELECTORS["save_name"], re.I))
        if saves.count() != 1:
            raise FlowError("Không xác định được nút lưu x1; chưa gửi prompt.")
        saves.click()
        # Only wait for dialog close; do not reopen/reselect during an in-flight generation.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.page.evaluate(script, SELECTORS) == "missing":
                return
            self.pause(0.1)
        raise FlowError("Cài đặt x1 chưa đóng; chưa gửi prompt.")

    def prepare(self, prompt):
        self.ensure_x1()
        box = self.page.locator(SELECTORS["prompt"])
        if box.count() != 1:
            raise FlowError("Ô prompt thiếu hoặc không duy nhất; kiểm tra DOM, chỉnh SELECTORS.")
        box.click()
        self.page.keyboard.press("ControlOrMeta+A")
        self.page.keyboard.press("Delete")
        self.page.keyboard.insert_text(prompt)
        # Compare transport exactly, not prompt content/meaning. Never rewrite or trim.
        entered = box.evaluate("el => 'value' in el ? el.value : el.innerText")
        if entered != prompt:
            raise FlowError("Ô nhập không giữ nguyên chuỗi prompt; dừng trước gửi.")

    def submit(self):
        send = self.page.get_by_role('button', name=re.compile(SELECTORS['send_name'], re.I))
        if send.count() == 1:
            send.click(timeout=10000)
            self.wait_consumed()
            return
        buttons = self.page.locator(SELECTORS["buttons"])
        model = buttons.filter(has_text=re.compile(SELECTORS["model_pattern"], re.I))
        if model.count() > 1:
            raise FlowError("Nhiều nút model khớp; kiểm tra DOM trước khi gửi.")
        if model.count() == 1:
            # Resolve only an adjacent button under the same parent.
            button = model.locator("xpath=following-sibling::*[1][self::button or @role='button']")
            if button.count() == 1 and button.is_visible():
                button.click(timeout=10000)
                self.wait_consumed()
                return
        self.page.keyboard.press("Enter")
        self.wait_consumed()

    def wait_consumed(self):
        # Without an acknowledgement, Angular may read a later prompt from the same editor.
        self.page.wait_for_function("""() => {
            const editors=[...document.querySelectorAll('textarea,[contenteditable=true]')]
                .filter(e=>e.getClientRects().length);
            return editors.length===1 && ('value' in editors[0] ? editors[0].value : editors[0].innerText).trim()==='';
        }""", timeout=15000)

    def fetch(self, image):
        src = image["src"]
        if urlsplit(src).scheme in ("http", "https"):
            response = self.page.context.request.get(src, timeout=30000)
            try:
                if not response.ok:
                    raise FlowError(f"Tải ảnh thất bại HTTP {response.status}")
                return response.body(), response.headers.get("content-type", "").split(";")[0].lower()
            finally:
                response.dispose()
        if src.startswith(("blob:", "data:")):
            data = self.page.evaluate("""async src => {
                const response = await fetch(src);
                if (!response.ok) throw new Error('Image fetch failed');
                const blob = await response.blob();
                return await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onerror = reject;
                    reader.onload = () => resolve({mime: blob.type, b64: reader.result.split(',')[1]});
                    reader.readAsDataURL(blob);
                });
            }""", src)
            return base64.b64decode(data["b64"], validate=True), data["mime"].lower()
        raise FlowError("URL ảnh không được hỗ trợ.")


def wait_images(dom, baseline, expected, timeout):
    """Observe full new set, including unloaded tiles; reset settle on any change."""
    deadline, stable_since, previous = time.monotonic() + timeout, None, None
    observed = {}
    latest = []
    while time.monotonic() < deadline:
        latest = [image for image in dom.snapshot() if image["key"] not in baseline]
        observed.update((image["key"], image) for image in latest)
        signature = tuple((image["key"], image["ready"]) for image in latest)
        if signature != previous:
            previous, stable_since = signature, time.monotonic()
        if (len(latest) >= expected and all(image["ready"] for image in latest)
                and time.monotonic() - stable_since >= SETTLE_SECONDS):
            exact = len(latest) == expected and len(observed) == expected
            return latest, observed, "exact" if exact else "mismatch"
        dom.pause(POLL_SECONDS)
    return latest, observed, "timeout"


def save_image(dom, image, target_base):
    from PIL import Image
    body, mime = dom.fetch(image)
    extension = EXTENSIONS.get(mime)
    if not extension:
        raise FlowError("Content-type không phải PNG/JPEG/WEBP.")
    with Image.open(io.BytesIO(body)) as loaded:
        if min(loaded.size) < 512 or loaded.format != {".png": "PNG", ".jpg": "JPEG", ".webp": "WEBP"}[extension]:
            raise FlowError("Ảnh tải về thiếu kích thước hoặc sai định dạng MIME.")
        loaded.verify()
    path = target_base.with_suffix(extension)
    if path.exists():
        raise FlowError("Tệp đích đã tồn tại nhưng chưa có state done; giữ nguyên để đối chiếu.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".download")
    temporary.write_bytes(body)
    temporary.replace(path)
    return path, digest(body)


class Generator:
    def __init__(self, dom, state, batch=1, oldest_first=False, timeout=120):
        self.dom, self.state = dom, state
        self.batch, self.oldest_first, self.timeout = batch, oldest_first, timeout

    def quarantine(self, images, batch_id):
        for index, image in enumerate(images, 1):
            if not image["ready"]:
                continue
            row = {"batch": batch_id, "image_key_sha256": digest(image["key"])}
            try:
                path, sha = save_image(self.dom, image, self.state.out / "orphans" / f"batch_{batch_id:04d}_{index:03d}")
                row.update(file=path.relative_to(self.state.out).as_posix(), sha256=sha)
            except Exception as error:
                row["error"] = type(error).__name__
            self.state.data["orphans"].append(row)
        self.state.save()

    def group(self, scenes, attempt=0):
        baseline = {image["key"] for image in self.dom.snapshot()}
        batch_id = len(self.state.data["batches"]) + 1
        ledger = {"id": batch_id, "scene_ids": [s["id"] for s in scenes], "attempt": attempt,
                  "status": "preparing", "oldest_first": self.oldest_first}
        self.state.data["batches"].append(ledger)
        self.state.save()
        sent = []
        try:
            for scene in scenes:
                if sent:
                    self.dom.pause(SEND_GAP_SECONDS)
                self.dom.prepare(scene["prompt"])
                # Write BEFORE the click: a crash/timeout must not cause duplicate spend.
                self.state.set_scene(scene, "pending", batch=batch_id)
                sent.append(scene)
                self.dom.submit()
        except Exception as error:
            ledger.update(status="needs_review" if sent else "failed", error=type(error).__name__)
            for scene in scenes:
                self.state.set_scene(scene, "needs_review" if sent else "failed", error=type(error).__name__, batch=batch_id)
            self.state.save()
            if sent:
                raise PendingSubmission("Submit có thể đã thành công; dừng để đối chiếu, không tự gửi lại.") from error
            print(f"Chưa gửi cảnh {[s['id'] for s in scenes]}: " +
                  (str(error) if isinstance(error, FlowError) else type(error).__name__))
            return
        images, observed, result = wait_images(self.dom, baseline, len(scenes), self.timeout + 20 * (len(scenes) - 1))
        ledger["observed_count"] = len(observed)
        if result != "exact":
            self.quarantine(list(observed.values()), batch_id)
            # Undersupply/timeout may still be generating. Never mix late results with retries.
            uncertain = result == "timeout"
            ledger["status"] = "needs_review" if uncertain else "count_mismatch"
            for scene in scenes:
                self.state.set_scene(scene, "needs_review" if uncertain else "failed", batch=batch_id)
            self.state.save()
            if uncertain:
                raise PendingSubmission("Hết thời gian/thiếu ảnh; đã cách ly ảnh đọc được. Đối chiếu gallery trước khi retry.")
            if attempt < 2:
                for scene in scenes:
                    self.group([scene], attempt + 1)
            return
        ordered = images if self.oldest_first else list(reversed(images))
        try:
            for scene, image in zip(scenes, ordered):
                path, sha = save_image(self.dom, image, self.state.out / "images" / f"scene_{scene['id']:03d}")
                self.state.set_scene(scene, "done", file=path.relative_to(self.state.out).as_posix(), sha256=sha,
                                     batch=batch_id, mapping="DOM order; requires visual calibration")
        except Exception as error:
            ledger.update(status="download_failed", error=type(error).__name__)
            self.state.save()
            # Download failures retain pending state: never regenerate a successful submit.
            raise PendingSubmission("Tải/lưu ảnh lỗi sau submit; giữ state và kiểm gallery, không gen lại.") from error
        ledger["status"] = "done"
        self.state.save()

    def run(self, scenes):
        remaining = self.state.remaining(scenes)
        print(f"Bỏ qua {len(scenes) - len(remaining)} cảnh done; còn {len(remaining)} cảnh.")
        for start in range(0, len(remaining), self.batch):
            self.group(remaining[start:start + self.batch])
        return [s["id"] for s in scenes if self.state.data["scenes"].get(str(s["id"]), {}).get("status") != "done"]


def flow_url(value):
    parts = urlsplit(value)
    return parts.scheme == "https" and not parts.username and not parts.password and (
        parts.hostname in ("flow.google", "flow.google.com") or
        (parts.hostname == "labs.google" and "/flow" in parts.path))


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenes", type=Path)
    ap.add_argument("--url", required=True, help="URL Flow; không lưu vào state/log")
    ap.add_argument("--from", dest="first", type=int)
    ap.add_argument("--to", dest="last", type=int)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--oldest-first", action="store_true")
    ap.add_argument("--fallback-narration", action="store_true")
    ap.add_argument("--login", action="store_true", help="Chỉ đăng nhập thủ công, không gen")
    ap.add_argument("--cdp", help="CDP HTTP localhost, ví dụ http://localhost:9222")
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--profile", type=Path, default=Path.home() / ".flow_gen_profile")
    ap.add_argument("--timeout", type=float, default=120)
    return ap


def main(argv=None):
    started = time.monotonic()
    args = parser().parse_args(argv)
    failed, scenes = [], []
    try:
        if not flow_url(args.url):
            raise FlowError("--url phải là URL HTTPS Google Flow hợp lệ.")
        if args.batch < 1 or not math.isfinite(args.timeout) or args.timeout <= 0 or args.timeout > 3600:
            raise FlowError("--batch >= 1; --timeout trong khoảng (0, 3600].")
        if (args.first is not None and args.first < 1) or (args.last is not None and args.last < 1) or (
                args.first is not None and args.last is not None and args.first > args.last):
            raise FlowError("Khoảng --from/--to không hợp lệ.")
        profile = args.profile.expanduser().resolve()
        if profile.is_relative_to(REPO):
            raise FlowError("Profile phải nằm ngoài repo.")
        if args.cdp:
            cdp = urlsplit(args.cdp)
            if cdp.scheme != "http" or cdp.hostname not in ("localhost", "127.0.0.1", "::1") or cdp.username or cdp.password:
                raise FlowError("--cdp chỉ nhận HTTP localhost, không chứa thông tin đăng nhập.")
        if not args.login:
            if args.scenes is None:
                raise FlowError("Cần --scenes khi tạo ảnh.")
            scenes = load_scenes(args.scenes, args.fallback_narration, args.first, args.last)
            failed = [s["id"] for s in scenes]
        from playwright.sync_api import sync_playwright, Error
        with output_lock(args.out):
            state = State(args.out)
            project_hash = digest(args.url)
            if state.data.get("project_sha256", project_hash) != project_hash:
                raise FlowError("Out thuộc URL Flow khác; dùng thư mục out riêng.")
            state.data["project_sha256"] = project_hash
            state.save()
            remaining = state.remaining(scenes) if not args.login else []
            if not args.login and not remaining:
                failed = []
                print(f"Bỏ qua toàn bộ {len(scenes)} cảnh done; không mở browser.")
                return 0
            with sync_playwright() as runtime:
                context, owned = None, False
                try:
                    if args.cdp:
                        browser = runtime.chromium.connect_over_cdp(args.cdp)
                        if not browser.contexts:
                            raise FlowError("CDP không có browser context.")
                        context = browser.contexts[0]
                    else:
                        try:
                            context = runtime.chromium.launch_persistent_context(str(profile), channel="chrome", headless=False)
                        except Error as error:
                            if any(word in str(error).lower() for word in ("singleton", "profile in use", "user data directory is already in use")):
                                raise FlowError("Profile đang bận; đóng helper cũ, không xóa lock.") from None
                            print("Không mở được Chrome; thử Chromium (không thay đổi profile).")
                            context = runtime.chromium.launch_persistent_context(str(profile), headless=False)
                        owned = True
                    page = next((p for p in context.pages if p.url.rstrip("/") == args.url.rstrip("/")), None)
                    if page is None:
                        page = context.new_page()
                        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
                    if args.login:
                        input("Đăng nhập thủ công, mở project Flow. Nhấn Enter ở đây để đóng helper; không gen ảnh: ")
                        return 0
                    if not flow_url(page.url):
                        raise FlowError("Chưa ở Google Flow; chạy --login trước.")
                    failed = Generator(FlowDOM(page), state, args.batch, args.oldest_first, args.timeout).run(scenes)
                finally:
                    if owned and context:
                        context.close()
                    # For CDP only disconnect Playwright on exit; never close the user's Chrome.
        return 1 if failed else 0
    except (Exception, KeyboardInterrupt) as error:
        if isinstance(error, FlowError):
            print(f"Dừng: {error}", file=sys.stderr)
        else:
            # Browser/network exceptions may contain authenticated URLs or local profile paths.
            print(f"Dừng: {type(error).__name__}; kiểm tra đăng nhập/DOM/kết nối. Không tự retry submit.", file=sys.stderr)
        return 1
    finally:
        print(f"Tổng thời gian: {time.monotonic() - started:.1f}s; cảnh chưa hoàn thành/lỗi: {failed}")


if __name__ == "__main__":
    raise SystemExit(main())
