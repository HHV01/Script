import copy
import io
import json
import os
import shutil
import sys
import types
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import script_review as review, youtube, s2_voice
from pipeline.common import PROJECTS, Project, audio_duration

TEXT = 'Thành cổ lưu lại câu chuyện của một nền văn minh.\n\nChúng ta hãy tìm hiểu những dấu vết còn lại.'


def evidence():
    now = datetime.now(timezone.utc)
    return {'collected_at': now.isoformat(), 'expires_at': (now+timedelta(hours=24)).isoformat(),
            'videos': [{'id': 'recent', 'title': 'Dấu vết lịch sử', 'views': 100}], 'limits': 'Mẫu tham khảo'}


def verdict(approved=True):
    return {'approved': approved, 'scores': {k: 8 for k in review.DIMENSIONS},
            'summary': 'Hook có câu hỏi rõ; cần nghe kiểm tra giọng tổng hợp.',
            'narration_notes': 'Đọc chậm vừa, nhấn vào dấu vết; nghỉ khi chuyển đoạn.',
            'issues': [] if approved else [{'severity':'major','fix':'Mở bằng câu hỏi cụ thể hơn.'}],
            'historical_flags': [], 'audience_evidence_ids':['recent']}


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.name = 'review-test-'+uuid.uuid4().hex[:10]
        self.dir = PROJECTS/self.name
        shutil.copytree(PROJECTS/'_template', self.dir)
        self.project = Project(self.name)
        self.project.settings['review']['max_revisions'] = 1
        self.project.cfg['minutes'] = .12  # short synthetic narration, not an eight-minute production script
        self.project.script.write_text(TEXT,encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def approve(self):
        with patch.object(youtube,'review_research',return_value=evidence()), \
             patch.object(review.llm,'complete',return_value=json.dumps(verdict())):
            review.run(self.project)

    def test_unreviewed_and_changed_script_cannot_record(self):
        with self.assertRaises(SystemExit):
            s2_voice.run(self.project)
        self.approve()
        self.assertIsNotNone(review.require_approval(self.project))
        self.project.script.write_text(TEXT+' Nội dung khác.',encoding='utf-8')
        with self.assertRaises(SystemExit):
            s2_voice.run(self.project)

    def test_approval_cached_only_while_inputs_fresh(self):
        self.approve()
        with patch.object(youtube,'review_research',side_effect=AssertionError('Must not fetch')):
            review.run(self.project)
        report=review.read_approval(self.project)
        report['research_expires_at']=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
        review.write_json(self.dir/'script.review.json',report)
        with self.assertRaises(SystemExit):
            review.require_approval(self.project)
        self.assertEqual(review.review_summary(self.dir)['status'],'stale')

    def test_rewrite_is_reviewed_again_then_approved_and_backed_up(self):
        rewritten='Một thành cổ có thể kể điều gì?\n\nHãy cùng khám phá những dấu vết còn lại.'
        with patch.object(youtube,'review_research',return_value=evidence()), \
             patch.object(review.llm,'complete',side_effect=[json.dumps(verdict(False)),rewritten,json.dumps(verdict())]) as complete:
            review.run(self.project)
        self.assertEqual(complete.call_count,3)
        self.assertEqual(self.project.script.read_text(),rewritten)
        self.assertEqual((self.dir/'script.before_review.txt').read_text(),TEXT)
        self.assertEqual(len(review.read_approval(self.project)['history']),2)
        self.assertEqual(' '.join(s['text'] for s in review.require_approval(self.project)['segments']).split(),rewritten.split())

    def test_failed_revisions_do_not_overwrite_original_or_old_audio(self):
        old=self.dir/'voice.wav';old.write_bytes(b'preserve-old-audio')
        with patch.object(youtube,'review_research',return_value=evidence()), \
             patch.object(review.llm,'complete',side_effect=[json.dumps(verdict(False)),TEXT,json.dumps(verdict(False))]), \
             self.assertRaises(SystemExit):
            review.run(self.project)
        self.assertEqual(self.project.script.read_text(),TEXT)
        self.assertEqual(old.read_bytes(),b'preserve-old-audio')
        self.assertEqual(review.read_approval(self.project)['status'],'blocked')

    def test_unsupported_new_claim_and_invented_audience_source_block(self):
        self.project.settings['review']['max_revisions']=0
        for change in ({'historical_flags':[{'claim':'Một phát hiện mới','status':'needs_source'}]},
                       {'audience_evidence_ids':['invented']}):
            value=verdict();value.update(change)
            with patch.object(youtube,'review_research',return_value=evidence()), \
                 patch.object(review.llm,'complete',return_value=json.dumps(value)), self.assertRaises(SystemExit):
                review.run(self.project,force=True)
            with self.assertRaises(SystemExit):
                review.require_approval(self.project)

    def test_short_script_is_blocked_even_if_model_approves(self):
        self.project.cfg['minutes']=8
        self.project.settings['review']['max_revisions']=0
        with patch.object(youtube,'review_research',return_value=evidence()), \
             patch.object(review.llm,'complete',return_value=json.dumps(verdict())), self.assertRaises(SystemExit):
            review.run(self.project)
        self.assertTrue(any('Độ dài' in reason for reason in review.read_approval(self.project)['blockers']))

    def test_plan_tampering_and_legacy_audio_cannot_skip_gate(self):
        self.approve()
        (self.dir/'voice.wav').write_bytes(b'existing')
        self.project.words.write_text('[]')
        with self.assertRaises(SystemExit):
            s2_voice.run(self.project)
        plan=review.require_approval(self.project)
        plan['segments'][0]['pause_after']=9
        review.write_json(self.dir/'recording_plan.json',plan)
        with self.assertRaises(SystemExit):
            review.require_approval(self.project)

    def test_tts_consumes_approved_segments_and_variable_pauses(self):
        from test_vieneu import FakeVieneu
        self.approve()
        with patch.dict(sys.modules,{'vieneu':types.SimpleNamespace(Vieneu=FakeVieneu)}):
            s2_voice.run(self.project)
        words=json.loads(self.project.words.read_text())
        plan=review.require_approval(self.project)
        boundary=len(plan['segments'][0]['text'].split())
        self.assertAlmostEqual(words[boundary]['start']-words[boundary-1]['end'],.65,delta=.01)
        self.assertAlmostEqual(words[-1]['end'],audio_duration(self.project.voice),delta=.05)
        self.assertEqual(' '.join(w['w'] for w in words).split(),TEXT.split())
        self.assertTrue((self.dir/'voice.source.json').exists())

    def test_failed_refresh_invalidates_previous_approval(self):
        self.approve()
        with patch.object(youtube,'review_research',side_effect=SystemExit('offline')), self.assertRaises(SystemExit):
            review.run(self.project,force=True)
        with self.assertRaises(SystemExit):
            review.require_approval(self.project)


class ApprovedStyleTests(unittest.TestCase):
    def test_dedupe_preserves_paragraphs_for_recording_rhythm(self):
        from pipeline.s1_script import dedupe
        text='Họ khai thác đá.\n\nHọ đưa đá đến công trường.\n\nCâu này đã bị lặp. Câu này đã bị lặp.'
        cleaned,dropped=dedupe(text)
        self.assertEqual(dropped,1)
        self.assertEqual(len(cleaned.split('\n\n')),3)
        self.assertIn('Họ đưa đá đến công trường.',cleaned)

    def test_owner_reference_guides_style_without_becoming_fact_source(self):
        from pipeline.editorial import style_context
        style=style_context()
        self.assertEqual(style['measured']['whitespace_units'],3032)
        self.assertEqual(style['measured']['sentences'],182)
        self.assertEqual(style['measured']['max_sentence_units'],48)
        self.assertIn('không',style['approval_scope'])
        self.assertTrue(any('không' in item for item in style['historical_care']))
        self.assertTrue(style['excerpts'])
        self.assertLess(sum(len(x) for x in style['excerpts']),6000)


class RecentYouTubeTests(unittest.TestCase):
    def test_recent_queries_cache_and_two_observation_delta(self):
        import tempfile
        from types import SimpleNamespace
        from urllib.parse import urlparse,parse_qs
        with tempfile.TemporaryDirectory() as directory:
            p=SimpleNamespace(dir=Path(directory),cfg={'topic':'La Mã','niche':'Lịch sử'},settings={'review':{}})
            now=datetime.now(timezone.utc)
            calls=[]
            views=[100]
            def get(req,timeout):
                calls.append(req)
                if '/search?' in req.full_url:
                    result={'items':[{'id':{'videoId':'x'}}]}
                else:
                    result={'items':[{'id':'x','snippet':{'title':'Lịch sử','publishedAt':(now-timedelta(days=2)).isoformat()},'statistics':{'viewCount':str(views[0])}}]}
                return io.BytesIO(json.dumps(result).encode())
            with patch.dict(os.environ,{'YOUTUBE_API_KEY':'not-a-real-key'}),patch.object(youtube,'load_env'),patch.object(youtube,'urlopen',side_effect=get):
                first=youtube.review_research(p,now=now)
                self.assertIsNone(first['videos'][0]['view_change'])
                cached=youtube.review_research(p,now=now+timedelta(hours=1))
                self.assertEqual(cached['collected_at'],first['collected_at'])
                self.assertEqual(len(calls),3)
                views[0]=160
                newer=youtube.review_research(p,force=True,now=now+timedelta(hours=2))
                self.assertEqual(newer['videos'][0]['view_change'],60)
                self.assertEqual(newer['videos'][0]['observation_hours'],2)
            self.assertIn('publishedAfter',parse_qs(urlparse(calls[0].full_url).query))
            self.assertTrue(all('not-a-real-key' not in r.full_url for r in calls))

    def test_missing_key_is_a_blocker_not_fake_trend_data(self):
        import tempfile
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{},clear=True),patch.object(youtube,'load_env'):
            p=SimpleNamespace(dir=Path(directory),cfg={'topic':'Lịch sử'},settings={})
            with self.assertRaises(SystemExit):
                youtube.review_research(p)
            self.assertFalse((p.dir/'review_research.json').exists())


if __name__=='__main__':
    unittest.main()
