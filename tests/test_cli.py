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
from pipeline import doctor


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
