import { test } from 'node:test';
import assert from 'node:assert';
import { parseBeats, mapImagesAZ, buildBeatTimeline } from './beat-timeline.mjs';

test('parseBeats parses standard format', () => {
  const txt = `Beat 1 | 0.0s | Ngày 24 tháng 11 năm 1971.\nBeat 2 | 2.4s | Sân bay quốc tế Portland.\n`;
  const b = parseBeats(txt);
  assert.equal(b.length, 2);
  assert.equal(b[0].beat, 1);
  assert.equal(b[0].time, 0.0);
  assert.ok(b[0].text.includes('1971'));
});

test('mapImagesAZ sorts case-insensitively', () => {
  const imgs = ['Z.jpg', 'a.png', 'M.jpg'];
  const m = mapImagesAZ(imgs);
  assert.deepEqual(m, ['a.png', 'M.jpg', 'Z.jpg']);
});

test('buildBeatTimeline uses A-Z order and frame-locks', () => {
  const beats = [
    { beat: 1, time: 0, text: 'Một hai ba bốn năm' },
    { beat: 2, time: 1, text: 'Một hai' },
    { beat: 3, time: 2, text: 'Cuối' },
  ];
  const images = ['b.jpg', 'A.jpg', 'c.jpg'];
  const tl = buildBeatTimeline({ beats, images, audioPath: null, fps: 30 });
  assert.equal(tl.images[0], 'A.jpg');
  assert.equal(tl.images[1], 'b.jpg');
  assert.equal(tl.images[2], 'c.jpg');
  assert.ok(Array.isArray(tl.clips));
  assert.equal(tl.clips.length, 3);
  assert.ok(tl.clips[0].start === 0);
  assert.ok(tl.clips[1].start >= tl.clips[0].start);
});
