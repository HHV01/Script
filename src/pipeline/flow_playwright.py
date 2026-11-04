"""Playwright transport using the same DOM commands/selectors as the extension."""
import atexit
import base64
import os
import re
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse

from .bridge import BridgeError
from .common import ROOT, need


def is_flow_url(url):
    parsed = urlparse(url)
    return parsed.scheme == 'https' and (
        parsed.hostname in ('flow.google', 'flow.google.com') or
        (parsed.hostname == 'labs.google' and '/flow' in parsed.path))


class FlowBrowser:
    def __init__(self, project):
        self.project = project
        self.port = 'Playwright'
        self.runtime = self.context = self.browser = None
        self.owned = False
        cfg = project.settings['flow'].get('playwright', {})
        self.cfg = cfg
        self.script = '''async (msg) => {
          let listener;
          const chrome = {runtime: {onMessage: {addListener(fn) { listener = fn; }}}};
        ''' + (ROOT / 'flow_extension/selectors.js').read_text(encoding='utf-8') + '\n' + (
            ROOT / 'flow_extension/content.js').read_text(encoding='utf-8') + '''
          return await new Promise(resolve => listener(msg, null, resolve));
        }'''

    def _timeout_ms(self, name, default):
        try:
            value = float(self.cfg.get(name, default))
            if not 0 < value <= 3600:
                raise ValueError()
            return int(value * 1000)
        except (TypeError, ValueError):
            raise BridgeError(f'flow.playwright.{name} phải từ >0 đến 3600 giây.') from None

    def _executable(self):
        configured = self.cfg.get('executable_path')
        if configured:
            path = Path(os.path.expandvars(os.path.expanduser(configured)))
            if not path.is_absolute():
                path = ROOT / path
            if path.is_file():
                return str(path)
        candidates = []
        for base in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
            if os.environ.get(base):
                candidates.extend(Path(os.environ[base]) / suffix for suffix in (
                    'Google/Chrome/Application/chrome.exe', 'Microsoft/Edge/Application/msedge.exe'))
        candidates.extend(Path(path) for path in (
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'))
        for path in candidates:
            if path.is_file():
                return str(path)
        for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge'):
            found = shutil.which(name)
            if found:
                return found
        # None lets Playwright use its managed Chromium installation.
        return None

    def _wait_prompt(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            if is_flow_url(self.page.url):
                try:
                    response = self.page.evaluate(self.script, {'cmd': 'ping', 'data': {}})
                    if response.get('ok') and response.get('data', {}).get('promptBox'):
                        return
                except Exception:
                    # Navigation/login may replace the execution context.
                    pass
            if time.monotonic() >= deadline:
                if not is_flow_url(self.page.url):
                    raise BridgeError('Chưa đăng nhập Google Flow. Đăng nhập trong browser vừa mở, rồi chạy `python run.py flow <project> --action check` lại.')
                if '/project/' not in urlparse(self.page.url).path:
                    raise BridgeError('Flow đã mở nhưng chưa thấy ô prompt. Mở hoặc tạo project Flow, rồi chạy `python run.py flow <project> --action check` lại.')
                raise BridgeError('Project Flow chưa có ô prompt khớp selectors. Đợi trang tải xong; nếu vẫn lỗi, kiểm tra flow_extension/selectors.js (không gửi lệnh tạo ảnh).')
            self.page.wait_for_timeout(min(500, max(1, int((deadline - time.monotonic()) * 1000))))

    def wait_connected(self, timeout=300, wait_for_prompt=True):
        if self.context:
            if wait_for_prompt:
                self._wait_prompt(timeout)
            return
        try:
            from playwright.sync_api import sync_playwright
            self.runtime = sync_playwright().start()
            startup_ms = self._timeout_ms('startup_timeout', 60)
            navigation_ms = self._timeout_ms('navigation_timeout', 60)
            cdp = self.cfg.get('cdp_url')
            if cdp:
                parsed = urlparse(cdp)
                if parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
                    raise BridgeError('CDP chỉ hỗ trợ browser localhost; không công khai cổng debug.')
                self.browser = self.runtime.chromium.connect_over_cdp(cdp, timeout=startup_ms)
                if not self.browser.contexts:
                    raise BridgeError('Chrome CDP chưa có browser context.')
                self.context = self.browser.contexts[0]
            else:
                profile = Path(self.cfg.get('profile_dir', '.flow-profile'))
                if not profile.is_absolute():
                    profile = ROOT / profile
                profile.mkdir(parents=True, exist_ok=True, mode=0o700)
                proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
                options = {}
                if proxy and self.cfg.get('use_environment_proxy', True):
                    options['proxy'] = {'server': proxy, 'bypass': 'localhost,127.0.0.1,[::1]'}
                self.context = self.runtime.chromium.launch_persistent_context(
                    str(profile), headless=self.cfg.get('headless', False),
                    executable_path=self._executable(), timeout=startup_ms, **options)
                self.owned = True
            pages = [p for p in self.context.pages if is_flow_url(p.url)]
            url = self.project.cfg.get('flow_url', '')
            if url and not is_flow_url(url):
                raise BridgeError('flow_url phải là URL HTTPS Google Flow.')
            if url:
                self.page = next((p for p in pages if p.url.rstrip('/') == url.rstrip('/')), None)
            else:
                self.page = pages[0] if pages else None
            if not self.page:
                self.page = self.context.new_page()
                try:
                    self.page.goto(url or 'https://labs.google/fx/tools/flow',
                                   wait_until='domcontentloaded', timeout=navigation_ms)
                except Exception:
                    raise BridgeError('Trang Flow tải quá thời gian navigation_timeout. Kiểm tra mạng/proxy và mở lại; chưa xác nhận đăng nhập hay sẵn sàng tạo ảnh.') from None
            if wait_for_prompt:
                if not self.cfg.get('headless', False):
                    print('[flow] Đăng nhập Google và mở project trong browser vừa mở (giữ hồ sơ cho lần sau).')
                self._wait_prompt(timeout)
        except BaseException as e:
            self.close()
            if isinstance(e, (SystemExit, KeyboardInterrupt)):
                raise
            if isinstance(e, BridgeError):
                raise
            message = str(e).lower()
            if any(marker in message for marker in ('processsingleton', 'singletonlock', 'profile in use', 'user data directory is already in use')):
                detail = 'Hồ sơ Flow đang được browser khác dùng. Đóng cửa sổ dùng hồ sơ này rồi thử lại, hoặc đặt profile_dir riêng. Không xóa hồ sơ hay tệp khóa.'
            else:
                detail = 'Không khởi động/kết nối được browser Flow. Kiểm tra Chrome/Edge, mạng/proxy hoặc CDP localhost; nếu chưa có browser hãy chạy python -m playwright install chromium. Lỗi: ' + type(e).__name__
            # Do not echo raw browser errors: they can contain proxy credentials or CDP tokens.
            raise BridgeError(detail) from None
        atexit.register(self.close)

    def call(self, cmd, data=None, timeout=60):
        data = data or {}
        need(is_flow_url(self.page.url), 'Browser chưa ở Google Flow; đăng nhập và mở project rồi chạy lại.')
        try:
            if cmd == 'submit':
                prepared = self.page.evaluate(self.script, {'cmd': 'prepare_submit', 'data': {**data, 'native_fill': True}})
                if not prepared.get('ok'):
                    raise BridgeError(prepared.get('error', 'Cannot prepare Flow prompt'))
                # Use native editing so React/contenteditable state follows the
                # visible prompt after Flow switches into its conversation panel.
                self.page.locator('textarea:visible, [contenteditable=true]:visible').first.fill(data['prompt'])
                self.page.get_by_role('button', name=re.compile(
                    r'^(Bắt đầu tạo|Start creating|Generate|Create)$', re.I)).click(timeout=15000)
                # Diagnostics are opt-in; do not delay every image for a screenshot.
                if self.cfg.get('debug_artifacts', False):
                    directory = self.project.images_dir
                    directory.mkdir(parents=True, exist_ok=True)
                    self.page.screenshot(path=str(directory / 'flow-after-submit.png'))
                    (directory / 'flow-after-submit.txt').write_text(
                        self.page.locator('body').inner_text()[-6000:], encoding='utf-8')
                response = self.page.evaluate(self.script, {
                    'cmd': 'wait_tiles', 'data': prepared['data'], 'timeoutMs': timeout * 1000})
                if not response.get('ok'):
                    raise BridgeError(response.get('error', 'Flow generation failed'))
                return response.get('data', {})
            message = {'cmd': 'tile_source' if cmd == 'download' else cmd,
                       'data': data, 'timeoutMs': timeout * 1000}
            response = self.page.evaluate(self.script, message)
            if not response.get('ok'):
                raise BridgeError(response.get('error', 'Flow command failed'))
            result = response.get('data', {})
            if cmd == 'download':
                if result.get('b64'):
                    body = base64.b64decode(result['b64'], validate=True)
                    mime = result.get('mime', '')
                else:
                    download = self.context.request.get(result['url'], timeout=timeout * 1000)
                    if not download.ok:
                        raise BridgeError(f'Tải ảnh thất bại: HTTP {download.status}')
                    body, mime = download.body(), download.headers.get('content-type', '')
                ext = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}.get(mime.split(';')[0])
                if not ext or len(body) <= 1024:
                    raise BridgeError('Flow trả về dữ liệu không phải ảnh hợp lệ hoặc ảnh quá nhỏ.')
                directory = self.project.images_dir
                directory.mkdir(parents=True, exist_ok=True)
                scene = int(data['scene'])
                target = directory / f'{scene:03d}.{ext}'
                temporary = directory / f'{scene:03d}.download'
                temporary.write_bytes(body)
                temporary.replace(target)
                for old in directory.glob(f'{scene:03d}.*'):
                    if old != target:
                        old.unlink()
                return {'bytes': len(body)}
            return result
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f'Playwright {cmd}: {type(e).__name__}: {e}') from e

    def close(self):
        context, runtime = self.context, self.runtime
        owned = self.owned
        self.context = self.runtime = self.browser = None
        self.owned = False
        try:
            if context and owned:
                context.close()
        except Exception:
            pass  # A crashed browser must not hide the original connection error.
        finally:
            if runtime:
                try:
                    runtime.stop()
                except Exception:
                    pass


_instances = {}


def get_browser(project):
    if project.name not in _instances:
        _instances[project.name] = FlowBrowser(project)
    return _instances[project.name]
