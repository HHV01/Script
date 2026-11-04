import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from pipeline.visual_review import inspect, inspect_references, CRITERIA


class VisualGateTests(unittest.TestCase):
    def test_references_need_actual_viewing_and_two_channels(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.studio') as tmp:
            p = SimpleNamespace(dir=Path(tmp))
            self.assertFalse(inspect_references(p)[0])
            refs = [{'url': 'https://www.youtube.com/watch?v=example', 'channel': c,
                     'watched_video': True, 'adaptation': 'Use a closeup of the mechanism',
                     'avoid_copying': 'Do not copy character or scene artwork',
                     'observations': [{'at_seconds': 2, 'observation': 'Object fills frame'}]}
                    for c in ['one', 'two']]
            path = p.dir/'visual-references.json'
            path.write_text(json.dumps({'videos': refs}), encoding='utf-8')
            self.assertTrue(inspect_references(p)[0])
            refs[1]['watched_video'] = False
            path.write_text(json.dumps({'videos': refs}), encoding='utf-8')
            self.assertFalse(inspect_references(p)[0])

    def test_missing_stale_and_incomplete_reviews_block(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / ".studio") as tmp:
            p = SimpleNamespace(dir=Path(tmp), final=Path(tmp)/'final.mp4')
            p.final.write_bytes(b'video')
            self.assertFalse(inspect(p)[0])
            review = {'video_sha256': hashlib.sha256(b'video').hexdigest(),
                      'reviewer': 'Gạo', 'watched_full_video': True,
                      'mobile_preview_checked': True, 'approved': True, 'blockers': [],
                      'criteria': {k: {'passed': True, 'evidence': [
                          {'at_seconds': 1, 'observation': 'Observed action in frame'}]} for k in CRITERIA}}
            path = p.dir/'visual-review.json'
            path.write_text(json.dumps(review), encoding='utf-8')
            self.assertTrue(inspect(p)[0])
            review['criteria']['motion']['evidence'] = []
            path.write_text(json.dumps(review), encoding='utf-8')
            self.assertFalse(inspect(p)[0])
            p.final.write_bytes(b'changed')
            self.assertFalse(inspect(p)[0])
