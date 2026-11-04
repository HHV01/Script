import http.client
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio import server


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.projects = self.root/'projects'
        (self.projects/'_template').mkdir(parents=True)
        (self.projects/'_template/project.yaml').write_text('topic: test\nminutes: 8\n', encoding='utf-8')
        self.patches = [patch.object(server, 'ROOT', self.root), patch.object(server, 'PROJECTS', self.projects)]
        for p in self.patches:
            p.start()
        self.studio = server.Studio()

    def tearDown(self):
        self.studio.stop()
        deadline = time.monotonic()+8
        while self.studio.process is not None and time.monotonic()<deadline:
            time.sleep(.02)
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def create(self):
        return server.create_project({'name': 'history', 'topic': 'Dấu vết lịch sử', 'minutes': 8})

    def wait_status(self, status):
        deadline=time.monotonic()+6
        while time.monotonic()<deadline:
            if self.studio.snapshot()['status']==status:
                return self.studio.snapshot()
            time.sleep(.02)
        self.fail(f'Expected {status}, got {self.studio.snapshot()}')

    def test_create_preserves_existing_and_rejects_traversal(self):
        self.create()
        self.assertEqual(server.projects()[0]['topic'], 'Dấu vết lịch sử')
        with self.assertRaises(ValueError):
            self.create()
        for name in ('../outside', '/tmp/project', '_template', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                server.project_path(name)
        try:
            (self.projects/'link').symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest('symlink creation requires elevated privileges on this platform')
        with self.assertRaises(ValueError):
            server.project_path('link')

    def test_real_subprocess_events_and_nonzero_exit(self):
        self.create()
        (self.root/'run.py').write_text('''import json
print('@@STUDIO '+json.dumps({'stage':'scenes','status':'running'}), flush=True)
print('A diagnostic line', flush=True)
raise SystemExit(2)
''')
        self.studio.start('history','scenes',True)
        result=self.wait_status('failed')
        self.assertEqual(result['exit_code'],2)
        self.assertEqual(result['stages']['scenes'],'failed')
        self.assertIn('A diagnostic line',[l['text'] for l in result['logs']])
        persisted=json.loads((self.root/'.studio/last-run.json').read_text(encoding='utf-8'))
        self.assertEqual(persisted['status'],'failed')

    def test_stop_terminates_worker_and_rejects_concurrent_run(self):
        self.create()
        (self.root/'run.py').write_text('import time\nprint("Working",flush=True)\ntime.sleep(60)\n')
        self.studio.start('history')
        with self.assertRaises(ValueError):
            self.studio.start('history')
        self.studio.stop()
        self.assertEqual(self.wait_status('cancelled')['cancel_requested'],True)

    def test_completed_event_and_restart_interruption(self):
        self.create()
        (self.root/'run.py').write_text('''import json
for status in ['running','completed']:
 print('@@STUDIO '+json.dumps({'stage':'scenes','status':status}), flush=True)
''')
        self.studio.start('history','scenes',True)
        self.assertEqual(self.wait_status('completed')['stages']['scenes'],'completed')
        self.studio.state.update(status='running',stage='voice',stages={'voice':'running'})
        self.studio.save()
        restored=server.Studio()
        restored.restore()
        self.assertEqual(restored.snapshot()['status'],'interrupted')
        self.assertEqual(restored.snapshot()['stages']['voice'],'interrupted')

    def test_api_auth_origin_and_actual_creation(self):
        httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.handler(self.studio))
        thread=threading.Thread(target=httpd.serve_forever,daemon=True)
        thread.start()
        connection=http.client.HTTPConnection('127.0.0.1',httpd.server_port)
        try:
            connection.request('GET','/api/status')
            response=connection.getresponse()
            token=json.loads(response.read())['token']
            self.assertEqual(response.status,200)
            body=json.dumps({'name':'history','topic':'Lịch sử','minutes':8})
            connection.request('POST','/api/projects',body,{'Content-Type':'application/json'})
            response=connection.getresponse();response.read()
            self.assertEqual(response.status,403)
            headers={'X-Studio-Token':token,'Content-Type':'application/json','Origin':'https://other.test'}
            connection.request('POST','/api/projects',body,headers)
            response=connection.getresponse();response.read()
            self.assertEqual(response.status,403)
            headers.pop('Origin')
            connection.request('POST','/api/projects',body,headers)
            response=connection.getresponse();response.read()
            self.assertEqual(response.status,201)
            self.assertTrue((self.projects/'history/project.yaml').exists())
            connection.request('GET','/api/status',headers={'Host':'evil.example'})
            response=connection.getresponse();response.read()
            self.assertEqual(response.status,403)
        finally:
            connection.close()
            httpd.shutdown();httpd.server_close();thread.join()


if __name__=='__main__':
    unittest.main()
