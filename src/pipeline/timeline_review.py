"""Deterministic pre-render timing gate; never certifies listening or visual meaning.

storyboard-timing.json binds the source hashes and an actual executor to beats.
Each scene needs a beat with scene_id, unique anchor_text, visual_subject,
visual_action, at_seconds (spoken anchor), and visual_at_seconds (planned cue).
Timing provenance is voice.timing.json (legacy voice.words.metadata.json also
read): timing_kind=measured or sentence_boundaries_word_interpolation, executor,
script_sha256, voice_sha256, words_sha256. The latter permits anchors only at
validated segments' starts (word_end_index is exclusive), not interpolated
inner words. Unknown/synthetic provenance blocks. This is a planning gate,
not proof that rendered imagery conveys the declared meaning.
The current renderer executes scene cuts only: visual_at_seconds must match
the scene start within one frame; a declared inner-scene cue is not playback.
"""
import hashlib
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path

from .common import audio_duration


def _hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _tokens(text):
    return re.findall(r'\w+', unicodedata.normalize('NFC', str(text)).casefold())


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def inspect(project):
    """Return structural approval only; no files are modified."""
    base = Path(project.dir)
    blockers, warnings, evidence = [], [], {}
    result = {'approved': False, 'blockers': blockers, 'warnings': warnings, 'evidence': evidence}
    try:
        script_path = Path(getattr(project, 'script', base / 'script.txt'))
        scenes_path = Path(getattr(project, 'scenes_file', base / 'scenes.json'))
        words_path = Path(getattr(project, 'words', base / 'voice.words.json'))
        script = script_path.read_text(encoding='utf-8-sig')
        scenes = project.load_scenes() if hasattr(project, 'load_scenes') else json.loads(scenes_path.read_text(encoding='utf-8-sig'))
        raw_words = json.loads(words_path.read_text(encoding='utf-8-sig'))
        words = raw_words.get('words') if isinstance(raw_words, dict) else raw_words
        if not isinstance(scenes, list) or not scenes or not isinstance(words, list) or not words:
            raise ValueError('scenes and words must be nonempty lists')
        voice = getattr(project, 'voice', None)
        if voice is None:
            voice = next((base / f'voice.{ext}' for ext in ('mp3', 'wav', 'm4a', 'ogg')
                          if (base / f'voice.{ext}').is_file()), None)
        if voice is None:
            raise ValueError('voice file missing')
        hashes = {'script_sha256': _hash(script_path), 'voice_sha256': _hash(Path(voice)),
                  'scenes_sha256': _hash(scenes_path)}
        evidence['hashes'] = hashes
        duration = audio_duration(voice)
        fps = getattr(project, 'settings', {}).get('render', {}).get('fps', 30)
        frame = 1 / float(fps)
        if not _number(duration) or duration <= 0 or not math.isfinite(frame) or frame <= 0:
            raise ValueError('invalid duration or frame rate')
        evidence['voice_duration_seconds'] = duration
        words_hash = _hash(words_path)
        meta_path = Path(voice).parent / 'voice.timing.json'
        if not meta_path.exists():
            meta_path = base / 'voice.words.metadata.json'
        meta = json.loads(meta_path.read_text(encoding='utf-8-sig')) if meta_path.exists() else {}
        kind = meta.get('timing_kind', raw_words.get('timing_kind', 'unknown') if isinstance(raw_words, dict) else 'unknown')
        evidence['word_timing_kind'] = kind
        segment_kind = kind == 'sentence_boundaries_word_interpolation'
        if kind != 'measured' and not segment_kind:
            blockers.append(f'Word timings are {kind}; reliable anchor provenance required, not proof of listening.')
        elif not str(meta.get('executor', '')).strip():
            blockers.append('Timing provenance requires executor.')
        if kind == 'measured' or segment_kind:
            if any(meta.get(key) != value for key, value in
                   {'script_sha256': hashes['script_sha256'], 'voice_sha256': hashes['voice_sha256'],
                    'words_sha256': words_hash}.items()):
                blockers.append('Timing provenance hashes stale or missing.')
        evidence['timing_precision'] = ('Generated sentence boundaries only; inner words interpolated, not measured.'
                                        if segment_kind else 'Declared word timing; not a listening attestation.')
        script_tokens = _tokens(script)
        timed_tokens, token_times = [], []
        previous_end = 0.0
        for index, word in enumerate(words):
            start, end = word.get('start'), word.get('end')
            if not _number(start) or not _number(end) or start < 0 or end < start or start < previous_end - .001:
                raise ValueError(f'Invalid/overlapping word timing at index {index}')
            if end > duration + frame:
                blockers.append(f'Word {index} exceeds voice duration.')
            previous_end = end
            tokens = _tokens(word.get('w', word.get('word', '')))
            timed_tokens.extend(tokens)
            token_times.extend([(start, end)] * len(tokens))
        if timed_tokens != script_tokens:
            blockers.append('Word text does not exactly cover script tokens in sequence.')
        if abs(previous_end - duration) > frame:
            blockers.append('Last word end differs from voice duration by more than one frame.')
        segment_starts = {}
        if segment_kind:
            covered_words, last_segment_end = 0, 0.0
            for segment in meta.get('segments', []):
                first, last = segment.get('word_start_index'), segment.get('word_end_index')
                start, end = segment.get('start'), segment.get('end')
                # word_end_index is exclusive, following Python slice convention.
                if (not isinstance(first, int) or not isinstance(last, int) or
                        first != covered_words or not first < last <= len(words) or
                        not _number(start) or not _number(end) or start < last_segment_end - .001 or end <= start or
                        abs(start - words[first]['start']) > .001 or abs(end - words[last-1]['end']) > .001 or
                        _tokens(segment.get('text', '')) != [t for word in words[first:last]
                                                            for t in _tokens(word.get('w', word.get('word', '')))]):
                    raise ValueError('Invalid sentence boundary segment coverage/timing')
                token_index = sum(len(_tokens(word.get('w', word.get('word', '')))) for word in words[:first])
                segment_starts[token_index] = start
                covered_words, last_segment_end = last, end
            if covered_words != len(words):
                blockers.append('Sentence boundary segments must cover every word.')
        ranges, cursor, previous_end, ids = {}, 0, 0.0, set()
        for scene in scenes:
            sid = str(scene.get('id'))
            if sid in ids:
                raise ValueError(f'Duplicate scene id {sid}')
            ids.add(sid)
            start, end = scene.get('start'), scene.get('end')
            if not _number(start) or not _number(end) or end <= start or abs(start - previous_end) > frame:
                raise ValueError(f'Invalid scene timing/gap/overlap at {sid}')
            previous_end = end
            tokens = _tokens(scene.get('text', ''))
            if not tokens or script_tokens[cursor:cursor + len(tokens)] != tokens:
                blockers.append(f'Scene {sid} text is not contiguous script coverage at token {cursor}.')
            ranges[sid] = (cursor, tokens, start, end)
            if token_times and cursor < len(token_times) and abs(start - token_times[cursor][0]) > .35:
                blockers.append(f'Scene {sid} boundary differs from spoken first word by more than .35s.')
            sentences = len(re.findall(r'[.!?]+(?:\s|$)', scene.get('text', '')))
            if end - start >= 8 and sentences > 1:
                warnings.append(f'Scene {sid}: {end-start:.2f}s / {sentences} sentences; review multiple visual ideas manually.')
            cursor += len(tokens)
        if cursor != len(script_tokens):
            blockers.append('Scenes do not cover the complete script.')
        if abs(previous_end - duration) > frame:
            blockers.append('Scene duration differs from voice by more than one frame.')
        manifest_path = base / 'storyboard-timing.json'
        if not manifest_path.exists():
            blockers.append('Missing storyboard-timing.json; no verified semantic cue plan.')
        else:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
            if any(manifest.get(key) != value for key, value in hashes.items()):
                blockers.append('Storyboard timing hashes stale or missing.')
            if not str(manifest.get('executor', '')).strip():
                blockers.append('Storyboard timing executor missing.')
            seen = set()
            for beat in manifest.get('beats', []):
                sid = str(beat.get('scene_id'))
                if sid not in ranges:
                    blockers.append(f'Unknown beat scene {sid}.')
                    continue
                seen.add(sid)
                offset, tokens, start, end = ranges[sid]
                anchor = _tokens(beat.get('anchor_text', ''))
                matches = [i for i in range(len(tokens) - len(anchor) + 1)
                           if anchor and tokens[i:i + len(anchor)] == anchor]
                if len(matches) != 1 or offset + matches[0] >= len(token_times):
                    blockers.append(f'Scene {sid} anchor missing or not unique.')
                    continue
                actual = token_times[offset + matches[0]][0]
                if segment_kind and offset + matches[0] not in segment_starts:
                    blockers.append(f'Scene {sid} anchor is inside interpolated words; use exact sentence start or measured alignment.')
                spoken, visual = beat.get('at_seconds'), beat.get('visual_at_seconds')
                if not _number(spoken) or abs(spoken - actual) > .35:
                    blockers.append(f'Scene {sid} spoken cue differs from measured anchor.')
                if not _number(visual) or visual < max(start, actual - .5) - .001 or visual > min(end, actual + .35) + .001:
                    blockers.append(f'Scene {sid} visual cue is late/early or outside scene.')
                if not _number(visual) or abs(visual - start) > frame:
                    blockers.append(f'Scene {sid} visual cue is not an executed scene cut; within-scene cues unsupported.')
                if not all(str(beat.get(key, '')).strip() for key in ('visual_subject', 'visual_action')):
                    blockers.append(f'Scene {sid} visual subject/action missing.')
            if seen != ids:
                blockers.append('Every scene requires at least one anchored visual beat.')
        evidence['scope'] = 'Token coverage, declared provenance and planned cue timing only; no semantic or rendered audio/visual approval.'
        evidence['scene_count'] = len(scenes)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ArithmeticError,
            subprocess.SubprocessError) as error:
        blockers.append(f'Timeline inspection failed: {error}')
    result['approved'] = not blockers
    return result
