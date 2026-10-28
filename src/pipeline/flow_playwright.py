"""Playwright transport using the same DOM commands/selectors as the extension."""
import atexit
import base64
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

from .bridge import BridgeError
from .common import ROOT, need


def is_flow_url(url):
    parsed = urlparse(url)
    return parsed.scheme == 'https' and parsed.hostname == 'labs.google' and '/flow' in parsed.path


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
        ''' + (ROOT / 'flow_extension/selectors.js').read_text() + '\n' + (
            ROOT / 'flow_extension/content.js').read_text() + '''
          return await new Promise(resolve => listener(msg, null, resolve));
        }'''

    def wait_connected(self, timeout=300):
        if self.context:
            return
        from playwright.sync_api import sync_playwright
        self.runtime = sync_playwright().start()
        try:
            cdp = self.cfg.get('cdp_url')
            if cdp:
                parsed = urlparse(cdp)
                need(parsed.hostname in ('localhost', '127.0.0.1', '::1'),
                     'CDP chỉ hỗ trợ browser localhost; không công khai cổng debug.')
                self.browser = self.runtime.chromium.connect_over_cdp(cdp)
                need(self.browser.contexts, 'Chrome CDP chưa có browser context.')
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
                    executable_path=self.cfg.get('executable_path') or shutil.which('chromium') or None,
                    **options)
                self.owned = True
            pages = [p for p in self.context.pages if is_flow_url(p.url)]
            url = self.project.cfg.get('flow_url', '')
            if url:
                need(is_flow_url(url), 'flow_url phải là URL HTTPS Google Flow tại labs.google.')
                self.page = next((p for p in pages if p.url.rstrip('/') == url.rstrip('/')), None)
                if not self.page:
                    self.page = self.context.new_page()
                    self.page.goto(url, wait_until='domcontentloaded')
            else:
                self.page = pages[0] if pages else self.context.new_page()
                if not pages:
                    self.page.goto('https://labs.google/fx/tools/flow', wait_until='domcontentloaded')
            if not self.cfg.get('headless', False):
                print('[flow] Đăng nhập Google và mở project trong browser vừa mở (giữ hồ sơ cho lần sau).')
                self.page.wait_for_function(
                    "() => location.hostname === 'labs.google' && location.pathname.includes('/flow') && "
                    "[...document.querySelectorAll('textarea,[contenteditable=true]')].some(e => e.offsetParent !== null)",
                    timeout=timeout * 1000)
        except BaseException as e:
            self.close()
            if isinstance(e, (SystemExit, KeyboardInterrupt)):
                raise
            raise BridgeError(
                'Không khởi động/kết nối được Playwright. Kiểm tra Chromium, màn hình (headless=false), '
                'proxy, profile đang bị khóa, hoặc CDP localhost. Chi tiết: ' + str(e)) from e
        atexit.register(self.close)

    def call(self, cmd, data=None, timeout=60):
        data = data or {}
        need(is_flow_url(self.page.url), 'Browser chưa ở Google Flow; đăng nhập và mở project rồi chạy lại.')
        try:
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
        if self.context and self.owned:
            self.context.close()
        self.context = None
        if self.runtime:
            self.runtime.stop()
            self.runtime = None


_instances = {}


def get_browser(project):
    if project.name not in _instances:
        _instances[project.name] = FlowBrowser(project)
    return _instances[project.name]
