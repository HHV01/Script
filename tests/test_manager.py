import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from studio.manager import ChannelManager, summarize, validate_plan
from studio.channel import ChannelClient, ChannelError, SCOPES, table_rows


def dataset():
    return {'channel': {'id': 'ours', 'title': 'Dấu Vết Văn Minh',
                        'statistics': {'viewCount': '1200', 'subscriberCount': '100', 'videoCount': '1'}},
            'videos': [{'id': 'a', 'title': 'Kim tự tháp Ai Cập', 'published_at': '2026-10-01T00:00:00Z',
                        'statistics': {'viewCount': '1200'}}],
            'competitors': [{'id': 'b', 'title': 'La Mã cổ đại', 'statistics': {'viewCount': '2000'}}],
            'videos_truncated': False, 'analytics': {'status': 'not_connected', 'ctr': None, 'note': 'Cần OAuth'}}


def plan():
    return {'assessment': 'Kênh có nội dung nền văn minh; mẫu nhỏ, chưa thể kết luận xu hướng.',
            'actions': ['Kiểm chứng sử liệu và thử hook rõ giá trị.'],
            'briefs': [{'topic': 'Hệ thống dẫn nước La Mã đã thay đổi đô thị ra sao?', 'niche': 'Kỹ thuật các nền văn minh',
                        'category': 'civilizations', 'hook': 'Một thành phố cổ lấy nước như thế nào?',
                        'rationale': 'Video b là tín hiệu tham khảo cùng lĩnh vực, không chứng minh tăng view.',
                        'outline': 'Bối cảnh, kỹ thuật, đời sống, dấu vết còn lại.', 'evidence_video_ids': ['b']}]}


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root/'projects').mkdir()
        self.run = {'status': 'idle', 'project': None}
        self.studio = SimpleNamespace(snapshot=lambda: copy.deepcopy(self.run), start=Mock())
        self.created = []
        def create(body):
            path = self.root/'projects'/body['name']
            path.mkdir()
            (path/'project.yaml').write_text(json.dumps(body), encoding='utf-8')
            self.created.append(body)
            return body['name']
        self.manager = ChannelManager(self.studio, self.root, create)
        self.manager.settings['auto_dispatch'] = False

    def tearDown(self):
        self.manager.close()
        self.tmp.cleanup()

    def analyze(self):
        with patch.object(self.manager.client, 'collect', return_value=dataset()), \
             patch('studio.manager.llm.complete', return_value=json.dumps(plan())):
            self.manager._analyze(dict(self.manager.settings))

    def test_report_deltas_keep_unknown_distinct_from_zero(self):
        first = summarize(dataset(), now=datetime(2026,10,28,tzinfo=timezone.utc))
        self.assertIsNone(first['delta_since_snapshot']['viewCount'])
        previous = {**dataset(), 'collected_at': 'earlier'}
        previous['channel']['statistics']['viewCount'] = '1000'
        current = summarize(dataset(), previous)
        self.assertEqual(current['delta_since_snapshot']['viewCount'],200)
        self.assertEqual(current['baseline_at'],'earlier')
        previous['channel']['id'] = 'different'
        self.assertIsNone(summarize(dataset(),previous)['delta_since_snapshot']['viewCount'])

    def test_plan_rejects_duplicate_fake_evidence_and_wrong_category(self):
        validate_plan(plan(), ['Kim tự tháp Ai Cập'], {'a','b'})
        for change in ({'topic': 'Kim tự tháp Ai Cập'}, {'evidence_video_ids':['invented']}, {'category':'crypto'}):
            value=plan();value['briefs'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_plan(value,['Kim tự tháp Ai Cập'],{'a','b'})

    def test_handoff_is_idempotent_and_transfers_brief(self):
        self.analyze()
        report=self.manager.snapshot()['report']
        brief=report['briefs'][0]
        name=self.manager.delegate(brief['id'])
        self.assertEqual(self.manager.delegate(brief['id']),name)
        self.assertEqual(self.studio.start.call_count,1)
        self.assertEqual(len(self.created),1)
        import yaml
        cfg=yaml.safe_load((self.root/'projects'/name/'project.yaml').read_text())
        self.assertEqual(cfg['production_brief']['outline'],brief['outline'])
        self.assertEqual(cfg['production_brief']['source_report'],report['id'])
        self.assertTrue((self.manager.directory/'report.md').exists())
        self.assertEqual(len(list((self.manager.directory/'reports').glob('*.json'))),1)

    def test_busy_worker_queues_without_starting_then_dispatches(self):
        self.analyze();self.run['status']='running'
        brief=self.manager.state['report']['briefs'][0]
        self.assertIsNone(self.manager.delegate(brief['id']))
        self.studio.start.assert_not_called()
        with self.assertRaises(ValueError):
            self.manager.analyze()
        self.run['status']='completed'
        with self.manager.lock:
            self.manager._dispatch_pending()
        self.studio.start.assert_called_once()
        self.assertIsNone(self.manager.state['pending_brief'])

    def test_llm_failure_keeps_real_channel_report_without_fabricated_briefs(self):
        with patch.object(self.manager.client,'collect',return_value=dataset()), \
             patch('studio.manager.llm.complete',side_effect=RuntimeError('secret text')):
            self.manager._analyze(dict(self.manager.settings))
        state=self.manager.snapshot()
        self.assertEqual(state['report']['channel']['statistics']['viewCount'],'1200')
        self.assertEqual(state['report']['briefs'],[])
        self.assertNotIn('secret text',json.dumps(state))

    def test_due_schedule_automatically_assigns_only_one_video(self):
        self.manager.settings.update(enabled=True, auto_dispatch=True)
        with patch.object(self.manager.client, 'collect', return_value=dataset()) as collect, \
             patch('studio.manager.llm.complete', return_value=json.dumps(plan())):
            self.manager.tick()
            self.manager.thread.join(timeout=5)
            self.assertFalse(self.manager.thread.is_alive())
            self.manager.tick()
            self.assertEqual(collect.call_count,1)
        self.studio.start.assert_called_once()
        self.assertEqual(len(self.created),1)
        self.assertGreater(self.manager.state['next_run_at'],0)

    def test_settings_and_pending_queue_survive_restart(self):
        self.manager.configure({'enabled':True,'interval_hours':12,'auto_dispatch':False})
        restored=ChannelManager(self.studio,self.root,self.manager.create_project)
        self.assertTrue(restored.settings['enabled'])
        self.assertEqual(restored.settings['interval_hours'],12)
        with self.assertRaises(ValueError):
            self.manager.configure({'interval_hours':0})


class ChannelTests(unittest.TestCase):
    def test_oauth_state_and_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            client=ChannelClient(directory)
            with self.assertRaises(ChannelError):
                client.finish_authorization('code','wrong-state')
            self.assertTrue(all(scope.endswith('readonly') for scope in SCOPES))
            client_file=Path(directory)/'client.json'
            client_file.write_text(json.dumps({'installed': {'client_id':'test.apps.googleusercontent.com',
                'client_secret':'test-not-real','auth_uri':'https://accounts.google.com/o/oauth2/auth',
                'token_uri':'https://oauth2.googleapis.com/token','redirect_uris':['http://localhost']}}))
            with patch.dict(os.environ,{'GOOGLE_OAUTH_CLIENT_FILE':str(client_file)}):
                url=client.authorize(8787)
            from urllib.parse import urlparse,parse_qs
            query=parse_qs(urlparse(url).query)
            self.assertEqual(query['redirect_uri'],['http://127.0.0.1:8787/oauth/callback'])
            self.assertIn('code_challenge',query)
            with self.assertRaises(ChannelError):
                client.finish_authorization('code','wrong-state')
            self.assertFalse(client.token_path.exists())

    def test_oauth_token_saved_privately_and_disconnect_removes_it(self):
        import stat,time
        with tempfile.TemporaryDirectory() as directory:
            client=ChannelClient(directory)
            flow=SimpleNamespace(fetch_token=Mock(),credentials=SimpleNamespace(
                granted_scopes=SCOPES,to_json=lambda: json.dumps({'token':'not-real'})))
            client.pending={'flow':flow,'state':'expected','expires':time.time()+30}
            client.finish_authorization('authorized-code','expected')
            flow.fetch_token.assert_called_once_with(code='authorized-code')
            self.assertEqual(stat.S_IMODE(client.token_path.stat().st_mode),0o600)
            self.assertNotIn('not-real',json.dumps(client.readiness()))
            client.disconnect()
            self.assertFalse(client.token_path.exists())

    def test_owner_mismatch_stops_before_analytics(self):
        with tempfile.TemporaryDirectory() as directory:
            client=ChannelClient(directory)
            with patch.object(client,'credentials',return_value=SimpleNamespace(token='not-a-real-token')), \
                 patch('studio.channel.request_json',side_effect=[{'items':[{'id':'ours'}]}, {'items':[{'id':'other'}]}]) as request:
                with self.assertRaises(ChannelError):
                    client.collect({'channel_handle':'@test','niche_seeds':[]})
            self.assertEqual(request.call_count,2)

    def test_public_report_does_not_invent_analytics_or_put_key_in_url(self):
        calls=[]
        def request(url, params, headers):
            calls.append((url,params,headers))
            if url.endswith('/channels'):
                return {'items':[{'id':'ours','snippet':{'title':'Our channel'},'statistics':{'viewCount':'100'},
                                  'contentDetails':{'relatedPlaylists':{'uploads':'uploads'}}}]}
            if url.endswith('/playlistItems'):
                return {'items':[{'contentDetails':{'videoId':'a'}}]}
            return {'items':[{'id':'a','snippet':{'title':'History'},'statistics':{'viewCount':'100'}}]}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ,{'YOUTUBE_API_KEY':'not-real'}), \
             patch('studio.channel.request_json',side_effect=request):
            result=ChannelClient(directory).collect({'channel_handle':'@test','niche_seeds':[]})
        self.assertEqual(result['analytics']['status'],'not_connected')
        self.assertIsNone(result['analytics']['ctr'])
        self.assertTrue(all('not-real' not in url for url,_,_ in calls))
        self.assertTrue(all(headers.get('X-Goog-Api-Key')=='not-real' for _,_,headers in calls))

    def test_analytics_reads_period_and_traffic_without_claiming_ctr(self):
        self.assertEqual(table_rows({'columnHeaders':[{'name':'views'}],'rows':[[12]]}),[{'views':12}])
        responses=[{'items':[{'id':'ours','statistics':{}}]}, {'items':[{'id':'ours'}]},
                   {'columnHeaders':[{'name':'views'}],'rows':[[10]]},
                   {'columnHeaders':[],'rows':[]},{'columnHeaders':[],'rows':[]}]
        with tempfile.TemporaryDirectory() as directory:
            client=ChannelClient(directory)
            with patch.object(client,'credentials',return_value=SimpleNamespace(token='not-real')), \
                 patch('studio.channel.request_json',side_effect=responses) as request:
                result=client.collect({'channel_handle':'@test','niche_seeds':[]})
            self.assertEqual(result['analytics']['summary'],[{'views':10}])
            self.assertEqual(result['analytics']['status'],'ok')
            self.assertIsNone(result['analytics']['ctr'])
            self.assertEqual(request.call_args_list[-1].args[1]['dimensions'],'insightTrafficSourceType')


if __name__=='__main__':
    unittest.main()
