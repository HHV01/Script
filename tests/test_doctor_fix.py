import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import doctor


def report(*checks):
    return {'checks': [dict(code=c, status=s, detail='', action=None) for c, s in checks],
            'ready_locally': True}


def ok_run(cmd, **kwargs):
    return SimpleNamespace(returncode=0, stdout='', stderr='')


class DoctorFix(unittest.TestCase):
    def test_no_missing_parts_runs_nothing(self):
        with patch('pipeline.doctor.subprocess.run') as run:
            self.assertEqual(doctor.fix(report(('dependency.yaml', 'pass'), ('ffmpeg', 'pass'),
                                               ('ffprobe', 'pass'), ('flow.browser', 'pass')), log=lambda *_: None), [])
        run.assert_not_called()

    def test_missing_dependency_installs_requirements_once(self):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return SimpleNamespace(returncode=0, stdout='', stderr='')

        with patch('pipeline.doctor.subprocess.run', fake_run):
            result = doctor.fix(report(('dependency.yaml', 'pass'), ('dependency.openai', 'warn'),
                                       ('ffmpeg', 'pass'), ('ffprobe', 'pass')), log=lambda *_: None)
        self.assertEqual(len(calls), 1)
        cmd, kwargs = calls[0]
        self.assertIn('-r', cmd)
        self.assertTrue(cmd[-1].endswith('requirements.txt'))
        self.assertTrue(kwargs.get('capture_output'))
        self.assertEqual(result[0]['step'], 'pip install')
        self.assertTrue(result[0]['ok'])

    def test_missing_browser_installs_chromium(self):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return SimpleNamespace(returncode=0, stdout='', stderr='')

        with patch('pipeline.doctor.subprocess.run', fake_run):
            doctor.fix(report(('dependency.yaml', 'pass'), ('flow.browser', 'fail'),
                              ('ffmpeg', 'pass'), ('ffprobe', 'pass')), log=lambda *_: None)
        self.assertEqual(calls, [[sys.executable, '-m', 'playwright', 'install', 'chromium']])

    def test_ffmpeg_is_reported_not_downloaded(self):
        with patch('pipeline.doctor.subprocess.run') as run:
            result = doctor.fix(report(('dependency.yaml', 'pass'), ('ffmpeg', 'warn'),
                                       ('ffprobe', 'warn')), log=lambda *_: None)
        run.assert_not_called()
        self.assertEqual(result, [dict(step='ffmpeg', ok=False,
                                       detail='Cài FFmpeg vào PATH hoặc đặt ffmpeg/ffprobe vào tools/ffmpeg/bin/')])

    def test_json_mode_keeps_stdout_parseable(self):
        with patch('pipeline.doctor.subprocess.run',
                   return_value=SimpleNamespace(returncode=0, stdout='pip says hi', stderr='warning')), \
             patch('pipeline.doctor.inspect',
                   side_effect=[report(('flow.browser', 'fail')), report(('flow.browser', 'pass'))]), \
             redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = doctor.main(None, as_json=True, do_fix=True)
        data = json.loads(out.getvalue())
        self.assertEqual(data['fix'][0]['step'], 'playwright install')
        self.assertIn('pip says hi', err.getvalue())
        self.assertNotIn('[fix]', out.getvalue())
        self.assertEqual(code, 0)  # lần kiểm tra lại đã pass và bước cài thành công

    def test_failed_fix_returns_nonzero(self):
        with patch('pipeline.doctor.subprocess.run',
                   return_value=SimpleNamespace(returncode=1, stdout='', stderr='boom')), \
             patch('pipeline.doctor.inspect',
                   return_value=report(('dependency.openai', 'warn'))), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = doctor.main(None, as_json=True, do_fix=True)
        self.assertEqual(code, 1)

    def test_successful_fix_and_clean_report_returns_zero(self):
        with patch('pipeline.doctor.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='', stderr='')), \
             patch('pipeline.doctor.inspect',
                   side_effect=[report(('dependency.openai', 'warn')), report(('dependency.openai', 'pass'))]), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = doctor.main(None, as_json=True, do_fix=True)
        self.assertEqual(code, 0)


if __name__ == '__main__':
    unittest.main()
