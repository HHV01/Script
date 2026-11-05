"""Connection-only mocks; never opens a browser or contacts Google."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline.flow_playwright import FlowBrowser
from pipeline.bridge import BridgeError


class ConnectionTests(unittest.TestCase):
    def make(self, cfg=None):
        return FlowBrowser(SimpleNamespace(cfg={}, settings={'flow': {'playwright': cfg or {}}}))

    def runtime(self):
        runtime = MagicMock()
        context = runtime.chromium.launch_persistent_context.return_value
        context.pages = []
        page = context.new_page.return_value
        page.url = 'https://labs.google/fx/tools/flow/project/demo'
        page.evaluate.return_value = {'ok': True, 'data': {'promptBox': True}}
        return runtime, context, page

    def test_login_open_skips_prompt_and_configures_timeouts(self):
        runtime, context, page = self.runtime()
        adapter = self.make({'headless': True, 'startup_timeout': 12, 'navigation_timeout': 7})
        with patch('playwright.sync_api.sync_playwright') as factory, patch.object(adapter, '_executable', return_value=None):
            factory.return_value.start.return_value = runtime
            adapter.wait_connected(wait_for_prompt=False)
        self.assertEqual(runtime.chromium.launch_persistent_context.call_args.kwargs['timeout'], 12000)
        self.assertEqual(page.goto.call_args.kwargs['timeout'], 7000)
        page.evaluate.assert_not_called()
        adapter.close()

    def test_headless_default_checks_actual_ping(self):
        runtime, context, page = self.runtime()
        adapter = self.make({'headless': True})
        with patch('playwright.sync_api.sync_playwright') as factory:
            factory.return_value.start.return_value = runtime
            adapter.wait_connected()
        self.assertEqual(page.evaluate.call_args.args[1]['cmd'], 'ping')
        adapter.close()

    def test_navigation_timeout_does_not_claim_readiness(self):
        runtime, context, page = self.runtime()
        page.goto.side_effect = TimeoutError('secret URL')
        adapter = self.make()
        with patch('playwright.sync_api.sync_playwright') as factory:
            factory.return_value.start.return_value = runtime
            with self.assertRaisesRegex(BridgeError, 'navigation_timeout') as error:
                adapter.wait_connected(wait_for_prompt=False)
        self.assertNotIn('secret', str(error.exception))
        page.evaluate.assert_not_called()
        context.close.assert_called_once()

    def test_profile_lock_is_actionable_without_raw_credentials(self):
        runtime, _, _ = self.runtime()
        runtime.chromium.launch_persistent_context.side_effect = RuntimeError('ProcessSingleton https://user:secret@proxy')
        adapter = self.make()
        with patch('playwright.sync_api.sync_playwright') as factory:
            factory.return_value.start.return_value = runtime
            with self.assertRaisesRegex(BridgeError, 'Không xóa') as error:
                adapter.wait_connected()
        self.assertNotIn('secret', str(error.exception))

    def test_missing_executable_falls_back_to_managed_browser(self):
        adapter = self.make({'executable_path': '__not_installed__.exe'})
        with patch('pipeline.flow_playwright.Path.is_file', return_value=False), patch('pipeline.flow_playwright.shutil.which', return_value=None):
            self.assertIsNone(adapter._executable())

    def test_prompt_timeout_distinguishes_login_project_and_selector(self):
        for url, expected in [('https://accounts.google.com/', 'Chưa đăng nhập'),
                              ('https://labs.google/fx/tools/flow', 'chưa thấy ô prompt'),
                              ('https://labs.google/fx/tools/flow/project/demo', 'selectors')]:
            adapter = self.make()
            adapter.page = MagicMock()
            adapter.page.url = url
            adapter.page.evaluate.return_value = {'ok': True, 'data': {'promptBox': False}}
            with self.assertRaisesRegex(BridgeError, expected):
                adapter._wait_prompt(0)

    def test_invalid_timeout_rejected(self):
        for value in (0, -1, 'wrong', 3601):
            with self.assertRaises(BridgeError):
                self.make({'startup_timeout': value})._timeout_ms('startup_timeout', 60)


if __name__ == '__main__':
    unittest.main()
