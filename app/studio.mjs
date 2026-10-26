// API cho pipeline: bible, kịch bản AI, VieNeu-TTS, chia cảnh, prompt, Flow, verify.
// Key chỉ nằm ở server (pipeline-settings.json hoặc .env), không trả xuống client.
import {readFile, writeFile, mkdir, readdir, stat, rm} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {importRoster, normalizeBible, buildScenePrompt, promptHash} from './bible.mjs';
import {buildScriptMessages, parseScriptResponse, scriptStats} from './script-builder.mjs';
import {createAiClient, createVieneuClient, chunkText} from './providers.mjs';
import {resolveTools, probeMedia, probeDuration, decodeMono, concatAudio, toMp3} from './audio.mjs';
import {splitScenesFromVoice} from './split.mjs';
import {buildQueue, queueToPromptBlocks, queueToCsv, verifyImages, applyImagesToScenes} from './flow.mjs';

const fail = (message, status = 400) => Object.assign(Error(message), {status});
const safeSegment = (value) => String(value || 'project').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80) || 'project';
const trimSlash = (value) => String(value || '').replace(/\/+$/, '');

// Lấy code fence đầu tiên trong một mục markdown (dùng cho prompt pack cũ).
function extractFence(markdown, headingPattern) {
  const lines = String(markdown || '').split(/\r?\n/);
  const start = lines.findIndex(line => /^##\s+/.test(line) && headingPattern.test(line));
  if (start < 0) return '';
  let open = -1;
  for (let i = start + 1; i < lines.length; i++) {
    if (/^##\s+/.test(lines[i])) break;
    if (/^```/.test(lines[i].trim())) {
      if (open < 0) open = i;
      else return lines.slice(open + 1, i).join('\n').trim();
    }
  }
  return '';
}

const DEFAULT_SELECTORS = {
  prompt: 'textarea[placeholder*="tạo" i], input[placeholder*="tạo" i], [placeholder*="Bạn muốn tạo" i], textarea, div[contenteditable="true"], [role="textbox"]',
  generate: '',
  image: 'img[src*="googleusercontent"], img[src^="blob:"], img[src^="https://"]',
  download: '',
  referenceAdd: '',
  referenceInput: 'input[type="file"]',
  imageMode: '',
};

const DEFAULT_SETTINGS = {
  ai: {baseUrl: '', model: 'gpt-4o-mini', apiKey: ''},
  tts: {baseUrl: 'http://127.0.0.1:8000/v1', model: 'vieneu-v3-turbo', voice: 'Mai Anh', apiKey: ''},
  flow: {projectUrl: '', profileDir: '', downloadDir: '', headless: false, generateDelayMs: 60000, selectors: DEFAULT_SELECTORS},
};

function mergeSettings(base, patch = {}) {
  const next = {
    ...base,
    ai: {...base.ai, ...(patch.ai || {})},
    tts: {...base.tts, ...(patch.tts || {})},
    flow: {...base.flow, ...(patch.flow || {}), selectors: {...base.flow.selectors, ...(patch.flow?.selectors || {})}},
  };
  for (const group of ['ai', 'tts']) {
    if (patch[group] && Object.hasOwn(patch[group], 'apiKey')) {
      if (patch[group].apiKey === null || patch[group].apiKey === '') next[group].apiKey = '';
      else next[group].apiKey = String(patch[group].apiKey);
    }
  }
  return next;
}

async function mapLimit(items, limit, fn) {
  const out = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (cursor < items.length) {
      const index = cursor++;
      out[index] = await fn(items[index], index);
    }
  }
  await Promise.all(Array.from({length: Math.max(1, Math.min(limit, items.length))}, worker));
  return out;
}

export function createStudio({root, dataRoot, assets, json}) {
  const settingsPath = path.join(dataRoot, 'pipeline-settings.json');
  const biblesRoot = path.join(root, 'Video-scripts', 'bibles');
  const tools = resolveTools(root);
  const flowJobs = new Map();
  let settings = null;

  async function loadSettings() {
    if (settings) return settings;
    try {
      if (existsSync(path.join(root, '.env'))) process.loadEnvFile(path.join(root, '.env'));
    } catch { /* .env lỗi không được chặn app */ }
    let stored = {};
    try { stored = JSON.parse(await readFile(settingsPath, 'utf8')); }
    catch (error) { if (error.code !== 'ENOENT') throw Error('Không đọc được pipeline-settings.json; giữ file gốc để phục hồi.'); }
    settings = mergeSettings(DEFAULT_SETTINGS, stored);
    if (!settings.ai.baseUrl && process.env.OPENAI_BASE_URL) settings.ai.baseUrl = process.env.OPENAI_BASE_URL;
    if (!settings.ai.model && process.env.OPENAI_MODEL) settings.ai.model = process.env.OPENAI_MODEL;
    if (!settings.ai.apiKey && process.env.OPENAI_API_KEY) settings.ai.apiKey = process.env.OPENAI_API_KEY;
    if (!settings.tts.baseUrl && process.env.VIENEU_BASE_URL) settings.tts.baseUrl = process.env.VIENEU_BASE_URL;
    if (!settings.tts.apiKey && process.env.VIENEU_API_KEY) settings.tts.apiKey = process.env.VIENEU_API_KEY;
    return settings;
  }

  async function saveSettings(patch) {
    const current = await loadSettings();
    settings = mergeSettings(current, patch);
    await mkdir(dataRoot, {recursive: true});
    const temp = path.join(dataRoot, randomUUID() + '.tmp');
    await writeFile(temp, JSON.stringify(settings, null, 2), {mode: 0o600});
    const {rename} = await import('node:fs/promises');
    await rename(temp, settingsPath);
    return settings;
  }

  async function publicSettings() {
    const current = await loadSettings();
    return {
      ai: {baseUrl: current.ai.baseUrl, model: current.ai.model, hasKey: Boolean(current.ai.apiKey), keySource: current.ai.apiKey ? (existsSync(path.join(root, '.env')) && process.env.OPENAI_API_KEY === current.ai.apiKey ? 'env' : 'settings') : 'none', groqFallback: Boolean(process.env.GROQ_API_KEY)},
      tts: {baseUrl: current.tts.baseUrl, model: current.tts.model, voice: current.tts.voice, hasKey: Boolean(current.tts.apiKey)},
      flow: {
        projectUrl: current.flow.projectUrl, profileDir: current.flow.profileDir, downloadDir: current.flow.downloadDir,
        headless: Boolean(current.flow.headless), generateDelayMs: Number(current.flow.generateDelayMs) || 60000, selectors: current.flow.selectors,
      },
    };
  }

  async function aiClient() {
    const current = await loadSettings();
    if (!current.ai.baseUrl) throw fail('Chưa cấu hình AI base URL (ví dụ http://localhost:20128/v1).', 400);
    if (!current.ai.apiKey && !/localhost|127\.0\.0\.1|0\.0\.0\.0/i.test(current.ai.baseUrl)) {
      throw fail('Chưa có API key cho AI từ xa. Lưu key trong Pipeline → Cài đặt.', 400);
    }
    return createAiClient({baseUrl: current.ai.baseUrl, apiKey: current.ai.apiKey, model: current.ai.model});
  }

  async function ttsClient() {
    const current = await loadSettings();
    return createVieneuClient({baseUrl: current.tts.baseUrl, apiKey: current.tts.apiKey, model: current.tts.model});
  }

  async function listBibles() {
    if (!existsSync(biblesRoot)) return [];
    const files = await readdir(biblesRoot);
    const out = [];
    for (const name of files) {
      if (!/\.json$/i.test(name)) continue;
      const full = path.join(biblesRoot, name);
      const info = await stat(full);
      if (info.size > 4 * 1024 * 1024) continue;
      try {
        const data = JSON.parse(await readFile(full, 'utf8'));
        if (!Array.isArray(data.characters) && !Array.isArray(data.backgrounds)) continue;
        out.push({file: name, size: info.size, modified: info.mtime.toISOString(), name: data.name || name.replace(/\.json$/i, '')});
      } catch { /* bỏ file json không hợp lệ */ }
    }
    return out.sort((a, b) => a.name.localeCompare(b.name, 'vi'));
  }

  async function importBible(file) {
    const name = path.basename(String(file || ''));
    if (!/\.json$/i.test(name)) throw fail('Chỉ import file roster JSON.');
    const full = path.resolve(biblesRoot, name);
    if (!full.startsWith(path.resolve(biblesRoot) + path.sep)) throw fail('Đường dẫn bible không hợp lệ.', 403);
    let data;
    try { data = JSON.parse(await readFile(full, 'utf8')); } catch (error) { if (error.code === 'ENOENT') throw fail('Không tìm thấy file bible.', 404); throw fail('File bible không phải JSON hợp lệ.'); }
    const bible = importRoster(data, {name: data.name || name.replace(/\.json$/i, ''), source: name});
    if (!bible.styleLock || !bible.negative) {
      const base = name.replace(/-roster\.json$/i, '').replace(/\.json$/i, '');
      for (const candidate of [`${base}-prompt-blocks.md`, `${base}-prompt-pack.md`, `${base}-world.md`]) {
        const md = path.resolve(biblesRoot, candidate);
        if (!md.startsWith(path.resolve(biblesRoot) + path.sep) || !existsSync(md)) continue;
        const markdown = await readFile(md, 'utf8').catch(() => '');
        if (!markdown) continue;
        if (!bible.styleLock) bible.styleLock = extractFence(markdown, /style\s*lock/i) || '';
        if (!bible.negative) bible.negative = extractFence(markdown, /negative\s*prompt.*(đầy đủ|day du|full)/i)
          || extractFence(markdown, /negative/i) || '';
        if (bible.styleLock && bible.negative) break;
      }
    }
    return bible;
  }

  async function synthesizeVoice({text, voice, speed}) {
    const current = await loadSettings();
    const input = String(text || '').trim();
    if (!input) throw fail('Chưa có nội dung để đọc.');
    if (input.length > 120000) throw fail('Kịch bản quá dài cho một lần tạo voice (tối đa 120.000 ký tự). Hãy chia dự án.', 413);
    const chunks = chunkText(input, 6000);
    const dir = path.join(dataRoot, 'tmp', `tts-${randomUUID()}`);
    await mkdir(dir, {recursive: true});
    try {
      const client = createVieneuClient({baseUrl: current.tts.baseUrl, apiKey: current.tts.apiKey, model: current.tts.model});
      const files = [];
      for (const [index, chunk] of chunks.entries()) {
        const {bytes, mime} = await client.speech({text: chunk, voice: voice || current.tts.voice, responseFormat: 'wav'});
        const ext = mime === 'audio/wav' ? 'wav' : 'bin';
        const file = path.join(dir, `chunk-${String(index + 1).padStart(3, '0')}.${ext}`);
        await writeFile(file, bytes);
        files.push(file);
      }
      const joined = path.join(dir, 'full.wav');
      if (files.length === 1) {
        await import('node:fs/promises').then(({copyFile}) => copyFile(files[0], joined));
      } else {
        await concatAudio(tools, files, joined);
      }
      const mp3 = path.join(dir, 'voice.mp3');
      await toMp3(tools, joined, mp3);
      const bytes = await readFile(mp3);
      if (bytes.length > 64 * 1024 * 1024) throw fail('Voice vượt 64 MB. Giảm thời lượng hoặc chia dự án.', 413);
      const asset = await assets.putBuffer(bytes, 'audio/mpeg');
      const duration = await probeDuration(tools, mp3);
      return {url: asset.url, duration: Number(duration.toFixed(3)), bytes: asset.bytes, chunks: chunks.length, voice: voice || current.tts.voice};
    } finally {
      await rm(dir, {recursive: true, force: true});
    }
  }

  async function cloneVoice({name, dataUrl, denoise = true}) {
    const match = String(dataUrl || '').match(/^data:(audio\/[a-z0-9.+-]+);base64,([A-Za-z0-9+/]+={0,2})$/i);
    if (!match) throw fail('File mẫu giọng phải là audio (wav/mp3/m4a/ogg/webm).');
    const mime = match[1].toLowerCase();
    const extMap = {'audio/wav': 'wav', 'audio/x-wav': 'wav', 'audio/mpeg': 'mp3', 'audio/mp3': 'mp3', 'audio/mp4': 'm4a', 'audio/m4a': 'm4a', 'audio/ogg': 'ogg', 'audio/webm': 'webm'};
    const ext = extMap[mime];
    if (!ext) throw fail('Định dạng mẫu giọng chưa hỗ trợ. Dùng WAV/MP3/M4A/OGG/WebM.');
    const bytes = Buffer.from(match[2], 'base64');
    if (!bytes.length || bytes.length > 20 * 1024 * 1024) throw fail('Mẫu giọng phải từ 1 byte đến 20 MB.', 413);
    const current = await loadSettings();
    const client = createVieneuClient({baseUrl: current.tts.baseUrl, apiKey: current.tts.apiKey, model: current.tts.model});
    return client.cloneVoice({name, bytes, filename: `reference.${ext}`, denoise});
  }

  async function splitScenes(input) {
    const narration = String(input?.narration || '').trim();
    if (!narration) throw fail('Chưa có kịch bản để chia cảnh.');
    if (!/^\/api\/assets\/[a-f0-9]{64}\.(mp3|wav|m4a|ogg|webm|aac|flac)$/.test(String(input?.voiceUrl || ''))) throw fail('Voice phải là file đã lưu trong app.');
    const asset = assets.info(input.voiceUrl);
    const duration = Number(input.voiceSeconds) || await probeDuration(tools, asset.file);
    if (!duration) throw fail('Không đọc được thời lượng voice.');
    const samples = await decodeMono(tools, asset.file, 8000);
    const result = splitScenesFromVoice({
      narration, samples, sampleRate: 8000, duration,
      maxSeconds: Number(input.clipSeconds) || 8,
      minSeconds: Number(input.minSeconds) || 2.5,
      wpm: Number(input.wpm) || 150,
    });
    return {...result, voiceSeconds: Number(duration.toFixed(3))};
  }

  function buildProjectQueue(project) {
    if (!project || typeof project !== 'object') throw fail('Thiếu dự án.');
    const bible = project.bible ? normalizeBible(project.bible) : null;
    const queue = buildQueue({project, bible});
    const scenes = project.scenes.map((scene, i) => {
      const item = queue.items.find(x => x.index === (Number(scene.index) || i + 1));
      return item ? {...scene, prompt: item.prompt, promptHash: item.promptHash} : scene;
    });
    return {queue, scenes};
  }

  async function flowVerify(input) {
    const project = input?.project;
    const queue = input?.queue || buildProjectQueue(project).queue;
    const files = Array.isArray(input?.files) ? input.files : [];
    if (files.length > 2000) throw fail('Tối đa 2.000 ảnh mỗi lần kiểm tra.', 413);
    const enriched = await mapLimit(files, 8, async file => {
      const name = String(file?.name || '');
      const url = String(file?.url || '');
      if (!/^\/api\/assets\/[a-f0-9]{64}\.(png|jpg|webp)$/.test(url)) throw fail(`Ảnh ${name || '?'} không phải asset hợp lệ.`);
      let width = Number(file?.width) || 0, height = Number(file?.height) || 0;
      if (!width || !height) {
        const media = await probeMedia(tools, assets.info(url).file);
        width = media.width; height = media.height;
      }
      return {name, url, width, height, promptHash: file?.promptHash || ''};
    });
    const verification = verifyImages({queue, files: enriched});
    const nextProject = verification.ok ? applyImagesToScenes(project, verification) : project;
    return {verification, project: nextProject, queue};
  }

  async function route(req, res, url, body) {
    const pathname = url.pathname;
    if (!pathname.startsWith('/api/pipeline') && !pathname.startsWith('/api/bibles') && !pathname.startsWith('/api/ai/') && !pathname.startsWith('/api/voice/') && !pathname.startsWith('/api/scenes/') && !pathname.startsWith('/api/prompts/') && !pathname.startsWith('/api/flow/')) return false;

    if (pathname === '/api/pipeline/settings' && req.method === 'GET') return json(res, 200, await publicSettings());
    if (pathname === '/api/pipeline/settings' && req.method === 'PUT') {
      const input = await body(req);
      await saveSettings(input);
      return json(res, 200, await publicSettings());
    }
    if (pathname === '/api/bibles' && req.method === 'GET') return json(res, 200, {root: 'Video-scripts/bibles', files: await listBibles()});
    if (pathname === '/api/bibles/import' && req.method === 'POST') return json(res, 200, {bible: await importBible((await body(req)).file)});

    if (pathname === '/api/ai/script' && req.method === 'POST') {
      const input = await body(req);
      const current = await loadSettings();
      const client = await aiClient();
      const bible = input.bible ? normalizeBible(input.bible) : null;
      const messages = buildScriptMessages({bible, brief: input.brief, targetMinutes: input.targetMinutes, tone: input.tone, audience: input.audience, wpm: input.wpm, outline: input.outline});
      const options = {temperature: Number(input.temperature) || 0.7, maxTokens: Number(input.maxTokens) || 8000};
      let raw;
      let provider = {baseUrl: current.ai.baseUrl, model: current.ai.model, fallback: false};
      try {
        raw = await client.chat(messages, options);
      } catch (error) {
        if ([502, 504].includes(error.status) && process.env.GROQ_API_KEY) {
          const fallback = createAiClient({baseUrl: 'https://api.groq.com/openai/v1', apiKey: process.env.GROQ_API_KEY, model: 'openai/gpt-oss-120b'});
          raw = await fallback.chat(messages, options);
          provider = {baseUrl: 'https://api.groq.com/openai/v1', model: 'openai/gpt-oss-120b', fallback: true};
        } else throw error;
      }
      const parsed = parseScriptResponse(raw);
      return json(res, 200, {...parsed, stats: scriptStats({narration: parsed.narration}), provider});
    }

    if (pathname === '/api/voice/status' && req.method === 'GET') {
      const current = await loadSettings();
      const client = createVieneuClient({baseUrl: current.tts.baseUrl, apiKey: current.tts.apiKey, model: current.tts.model});
      try {
        const health = await client.health();
        let voices = [];
        try { voices = await client.voices(); } catch { /* health vẫn ok */ }
        return json(res, 200, {ok: true, baseUrl: current.tts.baseUrl, health, voices});
      } catch (error) {
        return json(res, 200, {ok: false, baseUrl: current.tts.baseUrl, error: error.message, hint: 'Chạy tools\\start-vieneu.bat (hoặc uv run python -m apps.openai_speech trong tools/vieneu).'});
      }
    }
    if (pathname === '/api/voice/synthesize' && req.method === 'POST') {
      const input = await body(req);
      return json(res, 200, await synthesizeVoice({text: input.text, voice: input.voice, speed: input.speed}));
    }
    if (pathname === '/api/voice/clone' && req.method === 'POST') {
      const input = await body(req);
      return json(res, 200, await cloneVoice({name: input.name, dataUrl: input.dataUrl, denoise: input.denoise !== false}));
    }
    if (pathname === '/api/scenes/split' && req.method === 'POST') return json(res, 200, await splitScenes(await body(req)));
    if (pathname === '/api/prompts/build' && req.method === 'POST') {
      const input = await body(req);
      const {queue, scenes} = buildProjectQueue(input.project);
      return json(res, 200, {queue, project: {...input.project, scenes}, count: queue.items.length});
    }

    if (pathname === '/api/flow/queue' && req.method === 'POST') {
      const input = await body(req);
      const {queue, scenes} = buildProjectQueue(input.project);
      const safe = safeSegment(input.project?.id || input.project?.name);
      const dir = path.join(dataRoot, 'flow', safe);
      await mkdir(dir, {recursive: true});
      await writeFile(path.join(dir, 'queue.json'), JSON.stringify(queue, null, 2), {mode: 0o600});
      await writeFile(path.join(dir, 'prompts.txt'), queueToPromptBlocks(queue), {mode: 0o600});
      await writeFile(path.join(dir, 'queue.csv'), queueToCsv(queue), {mode: 0o600});
      const nextProject = {...input.project, scenes, flow: {...(input.project.flow || {}), queueFile: `flow/${safe}/queue.json`, expected: queue.items.length, updatedAt: new Date().toISOString()}};
      return json(res, 200, {queue, project: nextProject, files: {queue: `/api/flow/files/${safe}/queue.json`, prompts: `/api/flow/files/${safe}/prompts.txt`, csv: `/api/flow/files/${safe}/queue.csv`}});
    }
    if (pathname === '/api/flow/verify' && req.method === 'POST') return json(res, 200, await flowVerify(await body(req)));

    if (pathname === '/api/flow/run' && req.method === 'POST') {
      const input = await body(req);
      if (!input?.project) throw fail('Thiếu dự án.');
      const current = await loadSettings();
      const projectUrl = input.projectUrl || current.flow.projectUrl;
      if (!projectUrl) throw fail('Chưa có URL project Google Flow. Nhập trong Pipeline → Flow.');
      const queue = input.queue || buildProjectQueue(input.project).queue;
      const id = randomUUID();
      const job = {id, status: 'running', createdAt: new Date().toISOString(), total: queue.items.length, done: 0, current: 0, message: 'Đang khởi động trình duyệt…', errors: []};
      flowJobs.set(id, job);
      (async () => {
        try {
          const {runFlow} = await import('./flow-playwright.mjs');
          const safe = safeSegment(input.project.id || input.project.name);
          const downloadDir = input.downloadDir || current.flow.downloadDir || path.join(dataRoot, 'flow', safe, 'images');
          await mkdir(downloadDir, {recursive: true});
          const result = await runFlow({
            root, projectUrl, queue, downloadDir,
            profileDir: input.profileDir || current.flow.profileDir || path.join(dataRoot, 'flow', 'chrome-profile'),
            headless: Boolean(input.headless ?? current.flow.headless),
            selectors: {...current.flow.selectors, ...(input.selectors || {})},
            generateDelayMs: Number(input.generateDelayMs || current.flow.generateDelayMs) || 60000,
            onProgress: update => Object.assign(job, update),
            assets,
          });
          Object.assign(job, {status: 'done', message: `Đã tải ${job.done}/${job.total} ảnh.`, files: result.files, finishedAt: new Date().toISOString()});
        } catch (error) {
          Object.assign(job, {status: error.code === 'NEEDS_LOGIN' ? 'needs_login' : 'failed', message: error.message, finishedAt: new Date().toISOString(), code: error.code || ''});
        }
      })();
      return json(res, 202, job);
    }
    const jobMatch = pathname.match(/^\/api\/flow\/jobs\/([a-f0-9-]{36})$/);
    if (jobMatch && req.method === 'GET') {
      const job = flowJobs.get(jobMatch[1]);
      if (!job) throw fail('Không tìm thấy job Flow.', 404);
      return json(res, 200, job);
    }
    const fileMatch = pathname.match(/^\/api\/flow\/files\/([a-z0-9_-]{1,80})\/(queue\.json|prompts\.txt|queue\.csv)$/);
    if (fileMatch && req.method === 'GET') {
      const file = path.join(dataRoot, 'flow', fileMatch[1], fileMatch[2]);
      const text = await readFile(file, 'utf8');
      res.writeHead(200, {'Content-Type': fileMatch[2].endsWith('.json') ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8', 'Cache-Control': 'no-store'});
      return res.end(text);
    }
    return false;
  }

  return {route, loadSettings, publicSettings, saveSettings, listBibles, importBible, synthesizeVoice, cloneVoice, splitScenes, buildProjectQueue, flowVerify};
}
