import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from pipeline import qc


class SubtitleTests(unittest.TestCase):
    def test_parse_srt_reads_cues(self):
        text = ('1\n00:00:00,000 --> 00:00:01,500\nXin chào\n\n'
                '2\n00:00:01,500 --> 00:00:03,000\nDòng một\nDòng hai\n')
        cues = qc.parse_srt(text)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]['text'], 'Xin chào')
        self.assertEqual(len(cues[1]['lines']), 2)
        self.assertAlmostEqual(cues[1]['end'], 3.0)


class CTATailTests(unittest.TestCase):
    def inspect(self, scenes):
        project = SimpleNamespace(load_scenes=lambda: scenes, image_path=lambda scene: None)
        return qc.inspect_cta(project, {'duration': 100, 'tail_db': -20}, {'description': ''})

    def test_invitation_before_goodbye_is_found(self):
        result = self.inspect([{'text': 'Hãy đăng ký kênh.', 'start': 85, 'end': 96},
                               {'text': 'Hẹn gặp lại.', 'start': 96, 'end': 100}])
        self.assertTrue(result['scene_has_cta'])

    def test_old_invitation_outside_tail_is_not_found(self):
        result = self.inspect([{'text': 'Hãy đăng ký kênh.', 'start': 0, 'end': 5},
                               {'text': 'Hẹn gặp lại.', 'start': 96, 'end': 100}])
        self.assertFalse(result['scene_has_cta'])


class TitleTests(unittest.TestCase):
    def test_good_title_scores_high(self):
        result = qc.score_title('Vì sao bàn phím không xếp theo A, B, C? | Sự thật về QWERTY',
                                'vì sao bàn phím không xếp theo ABC')
        self.assertGreaterEqual(result['score'], 75)
        self.assertEqual(result['issues'], [])

    def test_clickbait_and_caps_are_penalised(self):
        result = qc.score_title('SỐC!!! BẠN SẼ KHÔNG TIN NỔI BÍ MẬT KINH HOÀNG NÀY')
        self.assertLess(result['score'], 60)
        self.assertTrue(any('giật tít' in issue for issue in result['issues']))

    def test_overlong_title_is_blocked(self):
        result = qc.score_title('A' * 130)
        self.assertLess(result['score'], 60)
        self.assertTrue(any('100' in issue for issue in result['issues']))

    def test_topic_keyword_is_rewarded(self):
        matched = qc.score_title('Sự thật về bàn phím QWERTY', 'bàn phím QWERTY')
        missing = qc.score_title('Sự thật về một vật dụng quen thuộc', 'bàn phím QWERTY')
        self.assertGreater(matched['score'], missing['score'])


class MetadataTests(unittest.TestCase):
    def test_description_needs_cta_without_shorts_requirement(self):
        result = qc.score_description('Một đoạn mô tả ngắn.', 'bàn phím')
        self.assertTrue(any('đăng ký' in issue for issue in result['issues']))
        self.assertFalse(any('#shorts' in issue for issue in result['issues']))

    def test_tags_over_limit_are_flagged(self):
        result = qc.score_tags(['một đoạn tag rất dài số ' + str(i) for i in range(30)], 'tag')
        self.assertTrue(any('500' in issue for issue in result['issues']))

    def test_duplicate_tags_are_flagged(self):
        result = qc.score_tags(['bàn phím', 'Bàn Phím'] + ['khác ' + str(i) for i in range(9)], 'bàn phím')
        self.assertTrue(any('trùng' in issue for issue in result['issues']))

    def test_fix_metadata_adds_cta_without_shorts(self):
        meta = {'title': 'Tiêu đề', 'description': 'Mô tả ngắn.', 'tags': ['a', 'A', 'b']}
        fixed, changes = qc.fix_metadata(meta, 'tiêu đề')
        self.assertNotIn('#shorts', fixed['description'])
        self.assertIn('Đăng ký', fixed['description'])
        self.assertEqual(fixed['tags'], ['a', 'b'])
        self.assertTrue(changes)

    def test_fix_metadata_is_idempotent(self):
        meta = {'title': 'Tiêu đề', 'description': 'Mô tả.\n\nĐăng ký kênh nhé.\n\n#shorts', 'tags': ['a']}
        fixed, changes = qc.fix_metadata(meta, 'tiêu đề')
        self.assertEqual(fixed['description'].count('#shorts'), 1)
        self.assertEqual(fixed['description'].count('Đăng ký'), 1)
        self.assertEqual(changes, [])



class LongFormTests(unittest.TestCase):
    def evaluate(self, width=1920, height=1080, duration=904, audio='aac', visual=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = root / 'final.mp4'
            final.write_bytes(b'test fixture, not a playable video')
            (root / 'publish.json').write_text(json.dumps({
                'title': 'Vì sao bạn không nhớ những năm đầu đời của mình?',
                'description': 'Trí nhớ và những năm đầu đời. ' * 12 + 'Đăng ký kênh nhé.',
                'tags': ['trí nhớ khoa học ' + str(i) for i in range(10)],
            }), encoding='utf-8')
            project = SimpleNamespace(dir=root, final=final, cfg={'topic': 'trí nhớ'}, settings={})
            media = dict(width=width, height=height, duration=duration, fps=30,
                         audio_codec=audio, mean_db=-20, peak_db=-2, head_db=-20,
                         tail_db=-20, black_spans=[])
            subs = dict(issues=[], cues=100, max_chars=45)
            cta = dict(scene_has_cta=True, end_card_ratio_ok=True,
                       description_has_cta=True, scene_text='Đăng ký kênh',
                       end_card_visible=True, end_card_distance=0)
            with patch.object(qc, 'inspect_media', return_value=media), \
                 patch.object(qc, 'inspect_subtitles', return_value=subs), \
                 patch.object(qc, 'inspect_cta', return_value=cta), \
                 patch('pipeline.visual_review.inspect', return_value=(visual, 'fixture')), \
                 patch('pipeline.visual_review.inspect_references', return_value=(False, 'missing references')):
                return qc.evaluate(project)

    def check_status(self, report, key):
        return next(c['status'] for c in report['checks'] if c['id'] == key)

    def test_long_horizontal_accepted_by_format_and_duration(self):
        report = self.evaluate()
        self.assertEqual(self.check_status(report, 'format'), qc.PASS)
        self.assertEqual(self.check_status(report, 'duration'), qc.PASS)
        # Format changes must not waive missing manual research evidence.
        self.assertEqual(self.check_status(report, 'visual_references'), qc.FAIL)
        self.assertFalse(report['approved'])

    def test_vertical_rejected(self):
        self.assertEqual(self.check_status(self.evaluate(1080, 1920), 'format'), qc.FAIL)

    def test_short_and_overlong_rejected(self):
        for duration in (59, 3601):
            self.assertEqual(self.check_status(self.evaluate(duration=duration), 'duration'), qc.FAIL)

    def test_audio_and_visual_gates_retained(self):
        report = self.evaluate(audio=None, visual=False)
        self.assertEqual(self.check_status(report, 'audio'), qc.FAIL)
        self.assertEqual(self.check_status(report, 'visual'), qc.FAIL)
        self.assertFalse(report['approved'])

    def test_custom_duration_bounds(self):
        project = SimpleNamespace(settings={'qc': {'min_duration_seconds': 240, 'max_duration_seconds': 1800}})
        self.assertEqual(qc.duration_bounds(project), (240, 1800))

    def test_invalid_duration_bounds_fail_closed(self):
        for low, high in ((0, 3600), (120, 60), (60, float('inf')), (True, 3600), ('60', 3600), (60, 43201)):
            with self.subTest(low=low, high=high), self.assertRaises(SystemExit):
                qc.duration_bounds(SimpleNamespace(settings={'qc': {
                    'min_duration_seconds': low, 'max_duration_seconds': high}}))

    def test_end_card_must_be_landscape(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / 'card.png'
            project = SimpleNamespace(load_scenes=lambda: [{'text': 'Đăng ký kênh'}],
                                      image_path=lambda scene: card)
            for size, expected in (((1920, 1080), True), ((1080, 1920), False)):
                Image.new('RGB', size).save(card)
                result = qc.inspect_cta(project, {'duration': 0, 'tail_db': -20}, {'description': 'Đăng ký kênh'})
                self.assertEqual(result['end_card_ratio_ok'], expected)

if __name__ == '__main__':
    unittest.main()
