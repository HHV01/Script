import {spawn} from 'node:child_process';import os from 'node:os';import path from 'node:path';import {existsSync} from 'node:fs';import {mkdir,readFile,writeFile,rename,readdir,stat,rm,copyFile} from 'node:fs/promises';import {createHash,randomUUID} from 'node:crypto';import {wanAvailable,generateWanClip} from './wan-client.mjs';import {stageHtml,validateHtmlScene} from './html-scenes.mjs';
export function createRenderer({root,dataRoot,assets}){
const failure=(message,status=400)=>Object.assign(Error(message),{status});
let chromiumPromise;function loadChromium(){return chromiumPromise ||=import('playwright-core').then(m=>m.chromium);}
const ffmpegBundled = path.join(root, 'tools', 'ffmpeg', 'bin', process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg');
const ffprobeBundled = path.join(root, 'tools', 'ffmpeg', 'bin', process.platform === 'win32' ? 'ffprobe.exe' : 'ffprobe');
// Ưu tiên ffmpeg kèm repo (Windows); máy khác dùng ffmpeg/ffprobe trong PATH.
const ffmpegBin = existsSync(ffmpegBundled) ? ffmpegBundled : 'ffmpeg';
const ffprobeBin = existsSync(ffprobeBundled) ? ffprobeBundled : 'ffprobe';
let ffmpegOkCache = null;
async function ffmpegAvailable() {
  if (ffmpegOkCache !== null) return ffmpegOkCache;
  try { await runTool(ffmpegBin, ['-version'], 10000); await runTool(ffprobeBin, ['-version'], 10000); ffmpegOkCache = true; }
  catch { ffmpegOkCache = false; }
  return ffmpegOkCache;
}
let ffmpegVersionCache = null;
function runTool(tool, args, timeoutMs = 300000) {
  return new Promise((resolve, reject) => {
    const child = spawn(tool, args, { windowsHide: true });
    let out = '', err = '';
    let killed = false;
    const timer = setTimeout(() => { killed = true; child.kill(); }, timeoutMs);
    child.stdout.on('data', d => { out += d; });
    child.stderr.on('data', d => { err = (err + d).slice(-16000); });
    child.on('error', e => { clearTimeout(timer); reject(e); });
    child.on('close', code => {
      clearTimeout(timer);
      if (killed) return reject(Object.assign(new Error('FFmpeg quá thời gian. Giảm số cảnh hoặc độ phân giải.'), { status: 504 }));
      if (code !== 0) return reject(Object.assign(new Error(`FFmpeg lỗi ${code}: ${(err || out).slice(-400)}`), { status: 500 }));
      resolve(out || err);
    });
  });
}
async function ffmpegVersion() {
  if (ffmpegVersionCache !== null) return ffmpegVersionCache;
  try {
    const v = await runTool(ffmpegBin, ['-version'], 10000);
    ffmpegVersionCache = String(v).split('\n')[0].slice(0, 120);
  } catch { ffmpegVersionCache = ''; }
  return ffmpegVersionCache;
}
let chromePathCache = null;
function htmlExecutable() {
  if (chromePathCache !== null) return chromePathCache;
  const candidates = [
    process.env.CHROME_PATH,
    path.join(os.homedir(), 'AppData', 'Local', 'ms-playwright', 'chromium-1248', 'chrome-win64', 'chrome.exe'),
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  ].filter(Boolean);
  chromePathCache = candidates.find(f => { try { return existsSync(f); } catch { return false; } }) || null;
  return chromePathCache;
}
// Ghi cảnh chữ/số liệu thành clip: Chromium offline ghi hình đúng duration,
// rồi ép về chuẩn dựng chung (mặc định 1920x1080/30fps) như mọi đoạn khác.
async function renderHtmlSegment(html, duration, tmp, { width = 1920, height = 1080 } = {}) {
  const exe = htmlExecutable();
  if (!exe) throw failure('Studio chưa thấy Chromium/Chrome để dựng cảnh HTML. Cài Chrome hoặc Playwright chromium.', 501);
  const checked = validateHtmlScene({ html, duration });
  const seg = path.join(tmp, `html-${randomUUID()}.mp4`);
  const dir = path.join(tmp, `html-rec-${randomUUID()}`);
  await mkdir(dir, { recursive: true });
  let browser;
  try {
    browser = await (await loadChromium()).launch({ executablePath: exe, headless:true, timeout:20000 });
    const ctx = await browser.newContext({ viewport: { width, height }, recordVideo: { dir, size: { width, height } } });
    const page = await ctx.newPage();
    await page.route('**/*', route => {
      const u = route.request().url();
      return /^https?:/i.test(u) ? route.abort() : route.continue();
    });
    await page.setContent(stageHtml(checked.html, { width, height }), { waitUntil: 'load' });
    try { await page.evaluate(() => document.fonts?.ready, null, { timeout: 10000 }); } catch {}
    await page.waitForTimeout(Math.round(checked.duration * 1000));
    await ctx.close();
    let webm = null;
    try { const vp = await page.video().path(); if (vp && existsSync(vp)) webm = vp; } catch {}
    if (!webm) {
      const files = (await readdir(dir)).filter(f => f.endsWith('.webm'));
      if (files.length) webm = path.join(dir, files[0]);
    }
    if (!webm) throw failure('Không ghi được clip HTML.');
    await runTool(ffmpegBin, ['-y', '-i', webm, '-r', '30', '-vf', `scale=${width}:${height}:force_original_aspect_ratio=increase,crop=${width}:${height},setsar=1,fps=30`, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', '-t', String(checked.duration), seg], 180000);
    return { file: seg };
  } finally {
    await browser?.close().catch(() => {});
  }
}
function parseRenderDataURL(dataURL, prefixes, maxBytes, label) {
  if (typeof dataURL !== 'string' || !dataURL.startsWith('data:')) throw failure(`${label} phải là data URL.`);
  const m = dataURL.match(/^data:([^;,]+)(?:;charset=[^;,]+)?;base64,(.*)$/);
  if (!m) throw failure(`${label} không đúng định dạng base64.`);
  if (!prefixes.some(p => m[1] === p || m[1].startsWith(p))) throw failure(`${label} sai định dạng (nhận ${m[1]}).`);
  const bytes = Buffer.from(m[2], 'base64');
  if (!bytes.length) throw failure(`${label} rỗng.`);
  if (bytes.length > maxBytes) throw failure(`${label} vượt ${(maxBytes / 1024 / 1024).toFixed(0)} MB. Giảm kích thước file.`);
  return { mime: m[1], bytes };
}
function resolveRenderInput(value, prefixes, maxBytes, label, prefix) {
  // Ảnh/voice có thể là data URL hoặc file đã lưu qua /api/assets (scene.image, voiceData).
  if (typeof value === 'string' && value.startsWith('/api/assets/')) {
    const asset = assets.read(value, prefix);
    if (asset.bytes.length > maxBytes) throw failure(`${label} vượt ${(maxBytes / 1024 / 1024).toFixed(0)} MB. Giảm kích thước file.`);
    return { mime: asset.mime, bytes: asset.bytes };
  }
  return parseRenderDataURL(value, prefixes, maxBytes, label);
}
async function probeSeconds(file) {
  const out = await runTool(ffprobeBin, ['-v', 'error', '-print_format', 'json', '-show_format', file], 30000);
  const seconds = Number(JSON.parse(out).format?.duration);
  if (!Number.isFinite(seconds) || seconds <= 0) throw failure('Không đọc được thời lượng file âm thanh.');
  return seconds;
}
// Dựng MP4 từ ảnh từng cảnh + voice: mỗi ảnh giữ đúng duration ở khung hình
// chuẩn (mặc định 1920x1080),
// nối lại rồi mux voice (aac), cắt theo bên ngắn hơn (-shortest).
// Wan cho cảnh cần nhân vật cử động: chạy lần lượt trên GPU, duyệt động tác
// bằng mắt sau khi có clip. Cảnh thường dùng ảnh để tiết kiệm thời gian.
async function generateWanScene(w) {
  const motion = String(w?.motionPrompt || '').trim();
  if (!motion) throw failure('Nhập mô tả chuyển động cho cảnh Wan.');
  if (motion.length > 2000) throw failure('Mô tả chuyển động tối đa 2000 ký tự.');
  if (w?.image == null) throw failure('Cảnh Wan cần ảnh khởi đầu. Nhập ảnh cảnh trước.');
  const img = resolveRenderInput(w.image, ['image/png', 'image/jpeg', 'image/webp'], 12 * 1024 * 1024, 'Ảnh khởi đầu', 'data:image');
  const duration = w?.durationSeconds == null ? 2 : Number(w.durationSeconds);
  const width = w?.width == null ? 640 : Number(w.width);
  const height = w?.height == null ? 352 : Number(w.height);
  if (!(await wanAvailable())) throw failure('Chưa nối được ComfyUI Wan ở 127.0.0.1:8188. Mở ComfyUI (node Wan22ImageToVideoLatent + model wan2.2) rồi thử lại.', 503);
  const clip = await generateWanClip({ imageBytes: img.bytes, imageExt: img.mime.includes('png') ? 'png' : 'jpg', positive: motion, negative: w?.negative, width, height, durationSeconds: duration });
  const stored = await assets.put(`data:video/mp4;base64,${clip.bytes.toString('base64')}`);
  return { url: stored.url, duration: clip.duration, width: clip.width, height: clip.height, fps: clip.fps, frames: clip.frames };
}
function validateRenderRequest(b) {
  if(!Array.isArray(b?.scenes)||!b.scenes.length||b.scenes.length>1000)throw failure('Cần 1–1000 cảnh để dựng.');
  if((b.width!=null&&Number(b.width)!==1920)||(b.height!=null&&Number(b.height)!==1080))throw failure('Video luôn xuất 1920 × 1080 (1080p).');
  if(!b.voice)throw failure('Thiếu voice để ghép.');
  b.scenes.forEach((s,i)=>{
    const kind=s?.kind||s?.buildKind||'image';
    if(!['image','html','wan'].includes(kind))throw failure(`Cảnh ${i+1} sai loại dựng.`);
    if(kind==='html'){try{validateHtmlScene({html:s?.html??s?.htmlSnippet,duration:s?.duration});}catch(e){throw failure(e.message);}}
    else {
      if(!Number.isFinite(Number(s.duration))||Number(s.duration)<0.5||Number(s.duration)>30)throw failure(`Cảnh ${i+1} cần thời lượng 0,5–30 giây.`);
      if(kind==='image'?!s.image:!s.clip)throw failure(`Cảnh ${i+1} thiếu nội dung; cần nhập đủ để giữ khớp voice.`);
    }
  });
}
async function renderVideo(b, progress = () => {}) {
  if ((b?.width != null && Number(b.width)!==1920) || (b?.height != null && Number(b.height)!==1080)) throw failure('Video luôn xuất 1920 × 1080 (1080p).');
  const scenes = b?.scenes;
  if (!Array.isArray(scenes) || !scenes.length || scenes.length > 1000) throw failure('Cần 1–1000 cảnh để dựng.');
  const parsed = scenes.map((s, i) => {
    const kind = s?.kind || s?.buildKind || 'image';
    if (!['image', 'html', 'wan'].includes(kind)) throw failure(`Cảnh ${i + 1} sai loại dựng (chọn image, html hoặc wan).`);
    if (kind === 'html') {
      let checked;
      try {
        checked = validateHtmlScene({ html: s?.html ?? s?.htmlSnippet, duration: s?.duration });
      } catch (e) {
        throw Object.assign(new Error(e.message), { status: 400 });
      }
      return { kind, duration: checked.duration, html: checked.html, dropped: false };
    }
    const duration = Number(s?.duration);
    if (!Number.isFinite(duration) || duration < 0.5 || duration > 30) throw failure(`Cảnh ${i + 1} cần thời lượng 0,5–30 giây.`);
    if (kind === 'wan') {
      const raw = s?.clip ?? null;
      // Không bỏ cảnh: thiếu clip sẽ làm lệch voice.
      if (raw == null) throw failure(`Cảnh ${i + 1} thiếu nội dung; cần nhập đủ trước khi dựng để giữ khớp voice.`);
      return { kind, duration, clip: raw, dropped: false };
    }
    const raw = s?.image ?? null;
    // Không bỏ cảnh thiếu ảnh.
    if (raw == null) throw failure(`Cảnh ${i + 1} thiếu nội dung; cần nhập đủ trước khi dựng để giữ khớp voice.`);
    return { kind, duration, img: raw, dropped: false };
  });
  if (b?.voice == null) throw failure('Thiếu voice để ghép.');
  const voice = resolveRenderInput(b.voice, ['audio/'], 64 * 1024 * 1024, 'Voice', 'data:audio');
  const rendered = parsed.filter(s => !s.dropped);
  if (!rendered.length) throw failure('Chưa có nội dung cảnh nào. Nhập ảnh/HTML/clip từng cảnh trước khi dựng.');
  const VW = 1920, VH = 1080;
  if (!(await ffmpegAvailable())) throw failure('Studio chưa thấy ffmpeg. Cần tools/ffmpeg/bin/ffmpeg.exe và ffprobe (Windows) hoặc ffmpeg trong PATH.', 501);
  const name = String(b?.name || 'video').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9-_]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40) || 'video';
  const tmp = path.join(os.tmpdir(), `video-render-${randomUUID()}`);
  await mkdir(tmp, { recursive: true });
  const SEG_VF = `scale=${VW}:${VH}:force_original_aspect_ratio=increase,crop=${VW}:${VH},setsar=1,fps=30`;
  try {
    const voiceExt = String(b?.voiceExt || 'mp3').toLowerCase().replace(/[^a-z0-9]+/g, '').slice(0, 8) || 'mp3';
    const voiceFile = path.join(tmp, `voice.${voiceExt}`);
    await writeFile(voiceFile, voice.bytes);
    const voiceSeconds = await probeSeconds(voiceFile);
    const scenesSeconds = parsed.reduce((n,s)=>n+s.duration,0);
    if(Math.abs(scenesSeconds-voiceSeconds)>0.5) throw failure(`Tổng cảnh lệch voice ${(scenesSeconds-voiceSeconds).toFixed(2)} giây; cần căn lại trước khi dựng.`);
    const cacheRoot=path.join(dataRoot,'render-cache');
    await mkdir(cacheRoot,{recursive:true});
    // Round cumulative boundaries, not each scene independently, to avoid drift on long videos.
    let seconds=0,frames=0;
    for(const scene of rendered){seconds+=scene.duration;const next=Math.round(seconds*30);scene.duration=(next-frames)/30;frames=next;}
    const segFiles = [];
    let cacheHits=0;
    for (const original of rendered) {
      const s={...original};
      if(s.kind==='image')s.img=resolveRenderInput(s.img,['image/png','image/jpeg','image/webp'],6*1024*1024,'Ảnh cảnh','data:image');
      if(s.kind==='wan')s.clip=resolveRenderInput(s.clip,['video/'],50*1024*1024,'Clip cảnh','data:video');
      const seg = path.join(tmp, `seg${segFiles.length}.mp4`);
      const hash=createHash('sha256').update('1080p-v1-crf18-fast-30fps').update(await ffmpegVersion()).update(String(s.duration)).update(s.kind).update(s.html || s.img?.bytes || s.clip?.bytes).digest('hex');
      const cached=path.join(cacheRoot,hash+'.mp4');
      if(existsSync(cached)){await copyFile(cached,seg);cacheHits++;segFiles.push(seg);progress({completed:segFiles.length,total:rendered.length,cacheHits});continue;}
      if (s.kind === 'html') {
        const made = await renderHtmlSegment(s.html, s.duration, tmp, { width: VW, height: VH });
        await rename(made.file, seg);
      } else if (s.kind === 'wan') {
        const clipFile = path.join(tmp, `wan${segFiles.length}.mp4`);
        await writeFile(clipFile, s.clip.bytes);
        await runTool(ffmpegBin, ['-y', '-stream_loop', '-1', '-t', String(s.duration), '-i', clipFile, '-vf', SEG_VF, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', '-r', '30', seg], 300000);
      } else {
        const ext = s.img.mime.includes('png') ? 'png' : s.img.mime.includes('webp') ? 'webp' : 'jpg';
        const imgFile = path.join(tmp, `s${segFiles.length}.${ext}`);
        await writeFile(imgFile, s.img.bytes);
        await runTool(ffmpegBin, ['-y', '-loop', '1', '-t', String(s.duration), '-i', imgFile, '-vf', SEG_VF, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', '-r', '30', seg], 300000);
      }
      const cacheTemp=cached+'.'+randomUUID()+'.tmp';
      await copyFile(seg,cacheTemp);await rename(cacheTemp,cached);
      segFiles.push(seg);progress({completed:segFiles.length,total:rendered.length,cacheHits});
    }
    const listFile = path.join(tmp, 'list.txt');
    await writeFile(listFile, segFiles.map(f => `file '${f.replace(/'/g, "'\\''")}'`).join('\n'));
    const videoOnly = path.join(tmp, 'video.mp4');
    await runTool(ffmpegBin, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', videoOnly], 300000);
    const outFile = path.join(tmp, 'out.mp4');
    await runTool(ffmpegBin, ['-y', '-i', videoOnly, '-i', voiceFile, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outFile], 300000);
    const probeOut = await runTool(ffprobeBin, ['-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', outFile], 30000);
    const probe = JSON.parse(probeOut);
    const duration = Number(probe.format?.duration);
    const videoStream=probe.streams.find(s=>s.codec_type==='video');
    if(videoStream?.width!==1920 || videoStream?.height!==1080 || Math.abs(duration-voiceSeconds)>0.5) throw failure('Bản dựng không đạt kiểm tra 1080p hoặc thời lượng.',500);
    const sizeBytes=(await stat(outFile)).size;
    const saved=path.join(dataRoot,'renders',randomUUID()+'.mp4');
    await mkdir(path.dirname(saved),{recursive:true});await copyFile(outFile,saved);
    const fileName = `${name}.mp4`;
    const kinds = { image: 0, html: 0, wan: 0 };
    for (const s of rendered) kinds[s.kind] += 1;
    return { fileName, file: saved, sizeBytes, cacheHits, scenesSeconds, voiceSeconds, scenesRendered: rendered.length, droppedScenes: parsed.length - rendered.length, kinds, size: { width: VW, height: VH }, probe: { duration } };
  } finally {
    await rm(tmp, { recursive: true, force: true });
  }
}

return {renderVideo,validateRenderRequest,ffmpegAvailable,ffmpegVersion,htmlExecutable,generateWanScene};
}
