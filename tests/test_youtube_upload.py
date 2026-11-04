import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.pipeline.youtube_upload import upload


class UploadTests(unittest.TestCase):
    def test_expired_campaign_does_not_contact_youtube(self):
        project = SimpleNamespace(cfg={'campaign': {'auto_upload': True, 'ends_at': 1}})
        with patch('studio.channel.ChannelClient') as client:
            with self.assertRaises(SystemExit):
                upload(project)
            client.assert_not_called()

    def test_ledger_blocks_removed_project_without_contacting_youtube(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / '.studio/manager/publication-ledger.json'
            ledger.parent.mkdir(parents=True)
            ledger.write_text(json.dumps({'videos': [{'project': 'published-project', 'video_id': 'known-id'}]}), encoding='utf-8')
            project = SimpleNamespace(name='published-project', cfg={'campaign': {'auto_upload': True, 'ends_at': time.time()+60}})
            with patch('src.pipeline.youtube_upload.ROOT', root), patch('studio.channel.ChannelClient') as client:
                with self.assertRaisesRegex(SystemExit, 'không upload lại'):
                    upload(project)
                client.assert_not_called()

    def test_corrupt_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / '.studio/manager/publication-ledger.json'
            ledger.parent.mkdir(parents=True)
            ledger.write_text('{broken', encoding='utf-8')
            project = SimpleNamespace(name='new-project', cfg={'campaign': {'auto_upload': True, 'ends_at': time.time()+60}})
            with patch('src.pipeline.youtube_upload.ROOT', root), patch('studio.channel.ChannelClient') as client:
                with self.assertRaisesRegex(SystemExit, 'chống trùng'):
                    upload(project)
                client.assert_not_called()

    def test_read_only_token_never_uploads(self):
        with tempfile.TemporaryDirectory() as directory:
            token = Path(directory) / 'token.json'
            token.write_text(json.dumps({'scopes': ['youtube.readonly']}), encoding='utf-8')
            project = SimpleNamespace(cfg={'campaign': {'auto_upload': True, 'ends_at': time.time()+60}},
                                      final=Mock(is_file=lambda: True))
            with patch('src.pipeline.youtube_upload.require_approval'), \
                 patch('studio.channel.ChannelClient', return_value=SimpleNamespace(token_path=token)), \
                 patch('google.auth.transport.requests.AuthorizedSession') as session:
                with self.assertRaises(SystemExit):
                    upload(project)
                session.assert_not_called()
