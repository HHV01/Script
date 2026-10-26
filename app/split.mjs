// Chia cảnh theo lời kể + voice thật: gom câu thành cảnh, rồi căn mốc theo chỗ ngắt nghỉ.
// Hàm thuần (trừ decodeMono) — test được với mảng mẫu giả.
import {sentences} from './bible.mjs';
import {detectPauses, alignScenes} from './public/voice-align.mjs';

const END_PUNCT = /[.!?…:;。？！]/u;

export function estimateSceneDurations(scenes, totalSeconds) {
  const words = scenes.map(s => String(s.narration || '').split(/\s+/).filter(Boolean).length);
  const all = words.reduce((n, w) => n + w, 0) || 1;
  const rate = totalSeconds > 0 ? totalSeconds / all : 60 / 150;
  return words.map(w => Math.max(0.4, w * rate));
}

export function groupSentences(text, {duration = 0, maxSeconds = 8, minSeconds = 2.5, wpm = 150} = {}) {
  const list = sentences(text);
  if (!list.length) throw Error('Kịch bản không có câu nào để chia cảnh.');
  const max = Math.max(0.5, Math.min(Number(maxSeconds) || 8, 30));
  const min = Math.max(0.5, Math.min(Number(minSeconds) || 2.5, max));
  const words = list.map(s => s.split(/\s+/).filter(Boolean).length);
  const totalWords = words.reduce((n, w) => n + w, 0) || 1;
  const rate = duration > 0 ? duration / totalWords : 60 / Math.max(60, Number(wpm) || 150);
  const groups = [];
  let current = {sentences: [], words: 0, seconds: 0};
  const flush = () => {
    if (!current.sentences.length) return;
    groups.push(current);
    current = {sentences: [], words: 0, seconds: 0};
  };
  for (const [index, sentence] of list.entries()) {
    const seconds = words[index] * rate;
    if (current.sentences.length && current.seconds + seconds > max) flush();
    current.sentences.push(sentence);
    current.words += words[index];
    current.seconds += seconds;
    if (current.seconds >= max * 0.92) flush();
  }
  flush();
  // Gộp cảnh quá ngắn vào cảnh trước (trừ khi chỉ có 1 cảnh).
  for (let i = groups.length - 1; i > 0; i--) {
    if (groups[i].seconds < min && groups[i - 1].seconds + groups[i].seconds <= max * 1.25) {
      groups[i - 1].sentences.push(...groups[i].sentences);
      groups[i - 1].words += groups[i].words;
      groups[i - 1].seconds += groups[i].seconds;
      groups.splice(i, 1);
    }
  }
  return groups.map((group, index) => ({
    index: index + 1,
    narration: group.sentences.join(' '),
    words: group.words,
    estimatedSeconds: Number(group.seconds.toFixed(2)),
    anchorable: END_PUNCT.test(group.sentences.at(-1) || ''),
  }));
}

export function splitScenesFromVoice({narration, samples, sampleRate = 8000, duration = 0, maxSeconds = 8, minSeconds = 2.5, wpm = 150, minPauseMs = 250} = {}) {
  const groups = groupSentences(narration, {duration, maxSeconds, minSeconds, wpm});
  const detected = samples?.length
    ? detectPauses(samples, sampleRate, {minPauseMs})
    : {pauses: [], duration: duration || 0, speechStart: 0, speechEnd: duration || 0};
  const voiceDuration = Math.max(0.5, Number(duration) || Number(detected.duration) || 0.5);
  const speechStart = Math.max(0, Number(detected.speechStart) || 0);
  const speechEnd = Math.max(speechStart + 0.1, Number(detected.speechEnd) || Number(duration) || speechStart + 0.1);
  const aligned = samples?.length
    ? alignScenes(groups.map(g => g.words), {pauses: detected.pauses, speechStart, speechEnd}, {anchorable: groups.map(g => g.anchorable)})
    : {ends: null, matched: 0, total: groups.length - 1};
  let ends = aligned.ends;
  let timingSource = ends ? 'pauses' : 'words';
  if (!ends) {
    // Fallback: chia theo số từ trên tổng thời lượng voice.
    const totalWords = groups.reduce((n, g) => n + g.words, 0) || 1;
    let cursor = 0;
    ends = groups.map(g => { cursor += g.words / totalWords * (speechEnd - speechStart); return speechStart + cursor; });
  }
  // Ép mốc tăng dần, cảnh cuối đúng bằng thời lượng voice (gồm cả lặng đầu/cuối).
  let previous = 0;
  ends = ends.map((end, index) => {
    const clamped = index === ends.length - 1 ? voiceDuration : Math.max(previous + 0.4, Number(end) || previous + 0.4);
    previous = clamped;
    return clamped;
  });
  const scenes = groups.map((group, index) => {
    const start = index === 0 ? 0 : Number(ends[index - 1].toFixed(3));
    const end = Number(ends[index].toFixed(3));
    return {
      index: group.index,
      label: `Cảnh ${group.index}`,
      narration: group.narration,
      start,
      end,
      duration: Number(Math.max(0.4, end - start).toFixed(3)),
      words: group.words,
      timing_source: timingSource,
      matched_pauses: aligned.matched,
    };
  });
  return {
    scenes,
    duration: Number(voiceDuration.toFixed(3)),
    matchedPauses: aligned.matched,
    totalAnchors: aligned.total,
    timingSource,
  };
}
