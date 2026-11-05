import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import doctor, flow_cli


class FlowHelpers(unittest.TestCase):
    def test_check_never_generates_and_releases_profile(self):
        browser = Mock()
        browser.call.return_value = {'promptBox': True}
        project = SimpleNamespace(settings={'flow': {'backend':'playwright'}})
        with patch.object(flow_cli, 'FlowBrowser', return_value=browser), redirect_stdout(io.StringIO()):
            flow_cli.run(project, action='check', timeout=9)
        self.assertEqual(browser.call.call_args_list[0].args, ('ping',))
        browser.close.assert_called_once()
        browser.wait_connected.assert_any_call(timeout=9, wait_for_prompt=True)

    def test_open_saves_only_valid_project_url_and_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path/'project.yaml').write_text('topic: demo\n', encoding='utf-8')
            browser = Mock()
            browser.context.pages = [SimpleNamespace(url='https://accounts.google.com/login'),
                                     SimpleNamespace(url='https://flow.google.com/project/demo?private=value')]
            project = SimpleNamespace(dir=path, settings={'flow': {'backend':'playwright'}})
            with patch.object(flow_cli, 'FlowBrowser', return_value=browser), patch('builtins.input', return_value=''), redirect_stdout(io.StringIO()):
                flow_cli.run(project, action='open')
            saved = (path/'project.yaml').read_text(encoding='utf-8')
            self.assertIn('https://flow.google.com/project/demo', saved)
            self.assertNotIn('private', saved)
            browser.call.assert_not_called()
            browser.close.assert_called_once()

    def test_generate_one_checks_approval_before_browser_or_generation(self):
        project = SimpleNamespace(settings={'flow': {'backend':'playwright'}})
        with patch('pipeline.script_review.require_approval', side_effect=SystemExit('blocked')), patch('pipeline.s5_generate.run') as generate:
            with self.assertRaises(SystemExit):
                flow_cli.run(project, action='generate-one')
            generate.assert_not_called()

    def test_offline_doctor_does_not_disclose_env_or_claim_login(self):
        with patch.dict('os.environ', {'GROQ_API_KEY':'never-print-this'}), patch('pipeline.flow_playwright.FlowBrowser._executable', return_value=sys.executable):
            result = doctor.inspect()
        text = json.dumps(result)
        self.assertNotIn('never-print-this', text)
        self.assertEqual(next(x for x in result['checks'] if x['code']=='flow.account')['status'], 'unknown')


class ExplicitUpload(unittest.TestCase):
    def test_single_stage_does_not_upload_even_when_campaign_flag_is_set(self):
        import run as cli
        project = SimpleNamespace(cfg={'campaign': {'auto_upload':True}}, final=Mock(exists=lambda:True))
        with patch.object(sys, 'argv', ['run.py','run','memory-long-01','--only','publish']), \
             patch('pipeline.common.Project', return_value=project), \
             patch('pipeline.script_review.require_approval', return_value=None), \
             patch.object(cli, 'import_module', return_value=Mock()), \
             patch('pipeline.youtube_upload.upload') as upload, redirect_stdout(io.StringIO()):
            cli.main()
        upload.assert_not_called()

    def test_cli_rejects_parent_traversal_before_project_loading(self):
        import run as cli
        with patch.object(sys, 'argv', ['run.py','new','../escape']), patch('pipeline.common.Project') as project:
            with self.assertRaises(SystemExit):
                cli.main()
            project.assert_not_called()
