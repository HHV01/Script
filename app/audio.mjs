// FFmpeg/ffprobe helpers cho voice + ảnh Flow. Không phụ thuộc thư viện ngoài.
import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {mkdtemp, readFile, rm, writeFile, mkdir} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

export function resolveTools(root) {
  const win = process.platform === 'win32';
  const ffmpegBundled = path.join(root, 'tools', 'ffmpeg', 'bin', win ? 'ffmpeg.exe' : 'ffmpeg');
  const ffprobeBundled = path.join(root, 'tools', 'ffmpeg', 'bin', win ? 'ffprobe.exe' : 'ffprobe');
  return {
    ffmpeg: existsSync(ffmpegBundled) ? ffmpegBundled : 'ffmpeg',
    ffprobe: existsSync(ffprobeBundled) ? ffprobeBundled : 'ffprobe',
  };
}

export function runTool(tool, args, {timeoutMs = 600000} = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(tool, args, {windowsHide: true});
    let out = '', err = '', killed = false;
    const timer = setTimeout(() => { killed = true; child.kill(); }, timeoutMs);
    child.stdout.on('data', d => { out += d; });
    child.stderr.on('data', d => { err = (err + d).slice(-16000); });
    child.on('error', e => { clearTimeout(timer); reject(e); });
    child.on('close', code => {
      clearTimeout(timer);
      if (killed) return reject(Object.assign(Error('FFmpeg quá thời gian.'), {status: 504}));
      if (code !== 0) return reject(Object.assign(Error(`FFmpeg lỗi ${code}: ${(err || out).slice(-500)}`), {status: 500}));
      resolve(out || err);
    });
  });
}

export async function probeMedia(tools, file) {
  const out = await runTool(tools.ffprobe, ['-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', file], {timeoutMs: 30000});
  const data = JSON.parse(out || '{}');
  const stream = (data.streams || []).find(s => s.codec_type === 'video') || (data.streams || []).find(s => s.codec_type === 'audio') || {};
  return {
    duration: Number(data.format?.duration || stream.duration || 0),
    width: Number(stream.width || 0),
    height: Number(stream.height || 0),
    codec: stream.codec_name || '',
    type: stream.codec_type || '',
  };
}

export async function probeDuration(tools, file) {
  return (await probeMedia(tools, file)).duration;
}

// Giải mã về mono float32 (mặc định 8 kHz) để dò ngắt nghỉ.
export async function decodeMono(tools, file, sampleRate = 8000) {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'video-studio-audio-'));
  try {
    const raw = path.join(dir, 'audio.f32');
    await runTool(tools.ffmpeg, ['-v', 'error', '-i', file, '-ac', '1', '-ar', String(sampleRate), '-f', 'f32le', '-y', raw], {timeoutMs: 300000});
    const bytes = await readFile(raw);
    const copy = Buffer.from(bytes);
    return new Float32Array(copy.buffer, copy.byteOffset, Math.floor(copy.byteLength / 4));
  } finally { await rm(dir, {recursive: true, force: true}); }
}

export async function toMp3(tools, input, output, bitrate = '192k') {
  await mkdir(path.dirname(output), {recursive: true});
  await runTool(tools.ffmpeg, ['-v', 'error', '-i', input, '-vn', '-codec:a', 'libmp3lame', '-b:a', bitrate, '-y', output], {timeoutMs: 600000});
  return output;
}

export async function concatAudio(tools, files, output) {
  if (!files.length) throw Error('Không có file voice để ghép.');
  const dir = await mkdtemp(path.join(os.tmpdir(), 'video-studio-concat-'));
  try {
    const list = path.join(dir, 'list.txt');
    const lines = files.map(file => `file '${path.resolve(file).replace(/'/g, "'\\''")}'`).join('\n');
    await writeFile(list, lines, 'utf8');
    await runTool(tools.ffmpeg, ['-v', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-y', output], {timeoutMs: 600000});
    return output;
  } finally { await rm(dir, {recursive: true, force: true}); }
}

export async function extractWaveform(tools, file, sampleRate = 8000) {
  return decodeMono(tools, file, sampleRate);
}
