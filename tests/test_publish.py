import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import s8_publish, youtube


def metadata():
    return {'title': 'Dấu vết một đế chế', 'description': 'Câu chuyện lịch sử.',
            'tags': ['lịch sử', 'văn minh'], 'title_alternatives': ['A', 'B', 'C'],
            'thumbnail_ideas': ['Bản đồ', 'Di tích', 'Hiện vật'],
            'retention_recommendations': ['Mở bằng câu hỏi lịch sử được giải đáp trong video.']}


class PublishTests(unittest.TestCase):
    def test_rejects_bad_metadata(self):
        for change in ({'title': 'x' * 101}, {'tags': ['x' * 501]}, {'description': ''},
                       {'tags': 'lịch sử'}, {'thumbnail_ideas': []}):
            with self.subTest(change=change), self.assertRaises(SystemExit):
                s8_publish.validate({**metadata(), **change})

    def test_package_cache_invalidates_when_script_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            (d / 'final.mp4').write_bytes(b'video')
            (d / 'script.txt').write_text('Kịch bản lịch sử', encoding='utf-8')
            p = SimpleNamespace(dir=d, final=d/'final.mp4', script=d/'script.txt', scenes_file=d/'scenes.json',
                                cfg={'topic': 'La Mã', 'niche': 'Lịch sử'},
                                settings={'llm': {'model': 'test'}})
            with patch.object(s8_publish, 'audio_duration', return_value=60), \
                 patch.object(s8_publish.youtube, 'research', return_value={'status': 'disabled', 'videos': []}), \
                 patch.object(s8_publish.llm, 'complete', return_value=json.dumps(metadata())) as complete:
                s8_publish.run(p)
                s8_publish.run(p)
                self.assertEqual(complete.call_count, 1)
                p.script.write_text('Nội dung mới', encoding='utf-8')
                s8_publish.run(p)
                self.assertEqual(complete.call_count, 2)
                self.assertEqual(json.loads((d/'publish.json').read_text())['niche'], 'Lịch sử')
                self.assertIn('Tags:', (d/'publish.txt').read_text())

    def test_youtube_disabled_and_missing_key(self):
        p = SimpleNamespace(settings={'youtube': {'research': False}})
        self.assertEqual(youtube.research(p)['status'], 'disabled')
        p.settings['youtube']['research'] = True
        with patch.dict(os.environ, {}, clear=True), patch.object(youtube, 'load_env'), self.assertRaises(SystemExit):
            youtube.research(p)

    def test_youtube_channel_and_competitor_research_uses_header(self):
        responses = [
            {'items': [{'id': 'channel', 'snippet': {'title': 'Dấu Vết Văn Minh'},
                        'contentDetails': {'relatedPlaylists': {'uploads': 'uploads'}}}]},
            {'items': [{'contentDetails': {'videoId': 'own'}}]},
            {'items': [{'id': 'own', 'snippet': {'title': 'Video kênh'}, 'statistics': {'viewCount': '20'}}]},
            {'items': [{'id': {'videoId': 'other'}}]},
            {'items': [{'id': 'other', 'snippet': {'title': 'Đế chế'}, 'statistics': {'viewCount': '40'}}]},
        ]
        import io
        requests = []
        def open_request(req, timeout):
            requests.append(req)
            return io.BytesIO(json.dumps(responses.pop(0)).encode())
        p = SimpleNamespace(cfg={'topic': 'La Mã', 'niche': 'Lịch sử'}, settings={
            'youtube': {'research': True, 'channel_handle': '@LsDấuVếtVănMinh'}})
        with patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test-secret'}), \
             patch.object(youtube, 'urlopen', side_effect=open_request), patch.object(youtube, 'load_env'):
            result = youtube.research(p)
        self.assertEqual(result['channel']['recent_videos'][0]['id'], 'own')
        self.assertEqual(result['videos'][0]['id'], 'other')
        self.assertEqual(len(requests), 5)
        for req in requests:
            self.assertNotIn('test-secret', req.full_url)
            self.assertEqual(req.get_header('X-goog-api-key'), 'test-secret')


if __name__ == '__main__':
    unittest.main()
