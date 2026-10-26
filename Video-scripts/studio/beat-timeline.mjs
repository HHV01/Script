// Beat timeline builder: parse Beat timestamp txt, map images, build frame-locked timeline
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

export function parseBeats(txt) {
  const lines = String(txt || '').split(/\r?\n/);
  const beats = [];
  for (const l of lines) {
    const s = l.trim();
    if (!s) continue;
    const m = s.match(/^Beat\s+(\d+)\s*\|\s*([\d.]+)s?\s*\|\s*(.*)$/i);
    if (m) {
      beats.push({ beat: parseInt(m[1]), time: parseFloat(m[2]), text: m[3].trim() });
      continue;
    }
    const m2 = s.match(/^Beat\s+(\d+)\s+([\d.]+)s?\s+(.*)$/i);
    if (m2) {
      beats.push({ beat: parseInt(m2[1]), time: parseFloat(m2[2]), text: m2[3].trim() });
    }
  }
  return beats;
}

export function mapImagesAZ(images) {
  const list = (images || []).filter(Boolean).map((x) => String(x));
  list.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
  return list;
}

export function buildBeatTimeline({ beats, images, audioPath, fps = 30 }) {
  if (!Array.isArray(beats)) beats = [];
  if (!Array.isArray(images)) images = [];
  const imgList = mapImagesAZ(images);
  const totalAudio = getAudioDuration(audioPath) || 0;
  const totalWords = beats.reduce((n, b) => n + countWords(b.text || ''), 0) || 1;
  let clips = [];
  let t = 0;
  for (let i = 0; i < beats.length; i++) {
    const b = beats[i];
    let dur;
    if (i === beats.length - 1) {
      dur = Math.max(0, totalAudio - t);
    } else {
      const w = countWords(b.text || '');
      dur = (w / totalWords) * totalAudio;
    }
    if (dur < 0) dur = 0;
    const img = imgList.length ? imgList[Math.min(i, imgList.length - 1)] : null;
    clips.push({ type: 'image', src: img, start: +t.toFixed(6), duration: +dur.toFixed(6), text: b.text || '', beat: b.beat });
    t += dur;
  }
  if (clips.length && fps > 0) {
    const totalSec = clips.reduce((s, c) => s + c.duration, 0) || totalAudio;
    const totalF = Math.max(1, Math.round(totalSec * fps));
    let acc = 0;
    const dursF = [];
    for (let i = 0; i < clips.length; i++) {
      if (i === clips.length - 1) {
        dursF.push(Math.max(1, totalF - acc));
      } else {
        const df = Math.round((clips[i + 1].start - clips[i].start) * fps);
        dursF.push(Math.max(1, df));
        acc += dursF[i];
      }
    }
    let t2 = 0;
    clips = clips.map((c, i) => {
      const d2 = dursF[i] / fps;
      const nc = { ...c, start: +t2.toFixed(6), duration: +d2.toFixed(6) };
      t2 += d2;
      return nc;
    });
  }
  const total = +clips.reduce((s, c) => s + c.duration, 0).toFixed(6);
  return { fps, beats, images: imgList, audioPath: audioPath || null, total, clips };
}

function countWords(s) {
  if (!s) return 0;
  return s.trim().split(/\s+/).filter(Boolean).length;
}

function getAudioDuration(audioPath) {
  if (!audioPath || !fs.existsSync(audioPath)) return 0;
  const ff = resolveFfmpeg();
  if (!ff) return 0;
  const res = spawnSync(ff, ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', audioPath], { encoding: 'utf8' });
  if (res.status !== 0) return 0;
  const v = parseFloat(res.stdout.trim());
  return isFinite(v) ? v : 0;
}

function resolveFfmpeg() {
  const cwd = process.cwd();
  const candidates = [
    path.join(cwd, 'tools', 'ffmpeg', 'bin', 'ffmpeg.exe'),
    path.join(cwd, 'tools', 'ffmpeg', 'ffmpeg.exe'),
    'ffmpeg',
  ];
  for (const c of candidates) {
    try {
      if (c.includes(path.sep) && fs.existsSync(c)) return c;
    } catch {}
  }
  return 'ffmpeg';
}
