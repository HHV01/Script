import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import dedupe, kenburns


class Motion(unittest.TestCase):
    def test_moves_alternate_and_zoom_is_bounded(self):
        for direction in ('in', 'out', 'left', 'right'):
            text = kenburns.motion_filter(0.1, direction, 90)
            self.assertIn('zoompan=', text)
            self.assertIn('d=90', text)
            self.assertIn('1920x1080', text)
        self.assertIn('1+0.1000*on/89', kenburns.motion_filter(0.1, 'in', 90))
        self.assertIn('1.1000-0.1000*on/89', kenburns.motion_filter(0.1, 'out', 90))

    def test_fade_longer_than_shortest_scene_is_rejected(self):
        with self.assertRaises(SystemExit):
            kenburns.render([Path('a.png'), Path('b.png')], Path('out.mp4'),
                            [1, 1], fade=1.0, log=lambda *_: None)

    def test_output_must_not_be_one_of_the_inputs(self):
        with self.assertRaises(SystemExit) as caught:
            kenburns.render([Path('a.png')], Path('a.png'), [2], log=lambda *_: None)
        self.assertIn('trùng', str(caught.exception))

    def test_partial_duration_list_is_an_error_not_a_silent_guess(self):
        with self.assertRaises(SystemExit) as caught:
            kenburns.resolve_durations([2, 5], 3)
        self.assertIn('3 giá trị', str(caught.exception))

    def test_one_duration_applies_to_every_image(self):
        self.assertEqual(kenburns.resolve_durations([4], 3), [4, 4, 4])
        self.assertEqual(kenburns.resolve_durations([], 2), [6.0, 6.0])

    def test_zero_duration_is_rejected(self):
        with self.assertRaises(SystemExit):
            kenburns.resolve_durations([0, 3], 2)

    def test_cli_help_builds_parser_without_percent_formatting_crash(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as caught:
            kenburns.main(['--help'])
        self.assertEqual(caught.exception.code, 0)


class Dedupe(unittest.TestCase):
    def test_normalization_ignores_case_and_punctuation(self):
        self.assertEqual(dedupe.normalize('  Bạn  GẬT đầu! '), 'bạn gật đầu')

    def test_similar_pairs_are_reported_without_editing(self):
        segments = [{'id': 1, 'text': 'Bạn gật đầu và tiếp tục làm việc.'},
                    {'id': 2, 'text': 'Bạn gật đầu rồi tiếp tục làm việc.'},
                    {'id': 3, 'text': 'Trời mưa rất to ngoài cửa sổ.'}]
        pairs = dedupe.find_similar(segments, 0.8)
        self.assertEqual([(p['a'], p['b']) for p in pairs], [(1, 2)])
        self.assertGreaterEqual(pairs[0]['ratio'], 0.8)

    def test_loads_scene_list_from_wrapped_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'scenes.json'
            path.write_text(json.dumps({'scenes': [
                {'id': 'a', 'narration': 'một'}, {'id': 'b', 'text': 'hai'}]}),
                encoding='utf-8')
            segments = dedupe.load_segments(path)
        self.assertEqual([s['id'] for s in segments], ['a', 'b'])

    def test_cli_json_report_never_deletes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'scenes.json'
            path.write_text(json.dumps([{'id': 1, 'text': 'xin chào'},
                                        {'id': 2, 'text': 'xin chào'}]), encoding='utf-8')
            before = path.read_text(encoding='utf-8')
            code = dedupe.main([str(path), '--json'])
            after = path.read_text(encoding='utf-8')
        self.assertEqual(code, 0)
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
