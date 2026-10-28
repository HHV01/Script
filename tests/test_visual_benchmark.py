import copy
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import visual_benchmark as benchmark


class VisualBenchmarkTests(unittest.TestCase):
    def test_dated_sources_unknown_metrics_and_unobserved_visuals(self):
        now=datetime(2026,10,28,tzinfo=timezone.utc)
        calls=[]
        def request(url,params,headers):
            calls.append((url,params,headers))
            if url.endswith('/search'):
                return {'items':[{'id':{'videoId':'one'}},{'id':{'videoId':'hidden'}}]}
            return {'items':[
                {'id':'one','snippet':{'title':'History','publishedAt':'2026-10-20T00:00:00Z','channelTitle':'Example',
                                     'thumbnails':{'high':{'url':'https://i.ytimg.com/vi/one/hqdefault.jpg'}}},
                 'statistics':{'viewCount':'100000'},'contentDetails':{'duration':'PT8M'}},
                {'id':'hidden','snippet':{'title':'Unknown view'},'statistics':{}}]}
        with patch.dict(os.environ,{'YOUTUBE_API_KEY':'not-real'}),patch.object(benchmark,'load_env'), \
             patch.object(benchmark,'request_json',side_effect=request):
            report=benchmark.collect(now=now)
        self.assertEqual(len(calls),5)
        self.assertEqual(len(report['videos']),2)
        self.assertEqual(report['groups'][0]['count'],1)
        self.assertIsNone(report['videos'][0]['visual_observations'])
        self.assertIsNone(report['videos'][0]['view_change'])
        self.assertIsNone(report['videos'][1]['views'])
        self.assertTrue(all('not-real' not in url for url,_,_ in calls))
        self.assertEqual(calls[0][1]['videoDuration'],'medium')
        self.assertIn('publishedAfter',calls[0][1])
        self.assertIn('i.ytimg.com',benchmark.markdown(report))
        self.assertIn('chưa thực hiện',benchmark.markdown(report))

    def test_missing_key_does_not_return_made_up_rankings(self):
        with patch.dict(os.environ,{},clear=True),patch.object(benchmark,'load_env'),self.assertRaises(ValueError):
            benchmark.collect()

    def test_two_snapshots_compute_actual_change_without_calling_it_ctr(self):
        now=datetime(2026,10,28,tzinfo=timezone.utc)
        def request(url,params,headers):
            if url.endswith('/search'):
                return {'items':[{'id':{'videoId':'one'}}]}
            return {'items':[{'id':'one','snippet':{'publishedAt':'2026-10-20T00:00:00Z'},'statistics':{'viewCount':'1000'}}]}
        with patch.dict(os.environ,{'YOUTUBE_API_KEY':'not-real'}),patch.object(benchmark,'load_env'), \
             patch.object(benchmark,'request_json',side_effect=request):
            previous=benchmark.collect(now=now)
            previous['videos'][0]['views']=800
            report=benchmark.collect(now=now+timedelta(hours=24),previous=previous)
        self.assertEqual(report['videos'][0]['view_change'],200)
        self.assertEqual(report['videos'][0]['observation_hours'],24)
        self.assertNotIn('ctr',report['videos'][0])


if __name__=='__main__':
    unittest.main()
