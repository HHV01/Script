// Pipeline AI UI: bible → script → voice → scenes → Flow → render.
// Trang riêng để không làm thay đổi luồng 4 tab hiện có của Studio.
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
const fmtSeconds = (value) => {
  const seconds = Number(value) || 0;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60), s = Math.round(seconds % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
};
const DEFAULT_TEMPLATE = `{style_lock}\n\nNhân vật (giữ nhất quán): {nhan_vat}\nBối cảnh: {boi_canh}\nHành động: {loi_ke}\nChi tiết: {chi_tiet}\n\nTránh: {negative}`;

let workspace = null;
let project = null;
let settings = null;
let currentStep = 'bible';
let busy = false;
let lastQueue = null;
let lastFlowFiles = [];
let flowPolling = false;

function setStatus(text, kind = '') {
  const el = $('#status');
  el.textContent = text || '';
  el.className = text ? `show ${kind}` : '';
  clearTimeout(setStatus.timer);
  if (text && kind !== 'error') setStatus.timer = setTimeout(() => { el.className = ''; el.textContent = ''; }, 7000);
}
function log(text, kind = '') {
  const el = $('#log');
  el.classList.add('show');
  const p = document.createElement('p');
  p.className = kind;
  p.textContent = text;
  el.append(p);
  while (el.children.length > 12) el.firstElementChild.remove();
  el.scrollTop = el.scrollHeight;
}
function setSaveStatus(text) { $('#save-status').textContent = text; }

async function api(path, {method = 'GET', body} = {}) {
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers['x-video-request'] = '1';
  const response = await fetch(path, {method, headers, body: body === undefined ? undefined : JSON.stringify(body)});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw Error(data.error || `Lỗi ${response.status}`);
  return data;
}

async function save({quiet = false} = {}) {
  if (!workspace) return;
  if (!quiet) setSaveStatus('Đang lưu…');
  const data = await api('/api/state', {method: 'PUT', body: {revision: workspace.revision, projects: workspace.projects}});
  workspace.revision = data.revision;
  workspace.projects = data.projects;
  project = workspace.projects.find(p => p.id === project?.id) || project;
  setSaveStatus('Đã lưu ' + new Date().toLocaleTimeString('vi-VN'));
  if (!quiet) setStatus('Đã lưu dự án.', 'ok');
}

function createProject() {
  return {
    id: crypto.randomUUID?.() || `p-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title: 'Dự án mới',
    narration: '',
    voiceSeconds: 0,
    clipSeconds: 8,
    scenes: [],
    bible: null,
    script: {},
    flow: {},
    createdAt: new Date().toISOString(),
  };
}

function ensureBible() {
  project.bible ||= {
    name: project.title || 'Bible mới', main: '', styleLock: '', negative: '',
    promptTemplate: DEFAULT_TEMPLATE, characters: [], backgrounds: [], styleRefImages: [],
    collections: {bibles: 'BIBLES', backgrounds: 'BACKGROUNDS', beats: 'BEATS'},
    sceneRules: {minSeconds: 2.5, maxSeconds: 8},
  };
  project.bible.characters ||= [];
  project.bible.backgrounds ||= [];
  project.bible.sceneRules ||= {minSeconds: 2.5, maxSeconds: 8};
  return project.bible;
}

function ensureScript() {
  project.script ||= {};
  return project.script;
}

function adoptProject(next) {
  if (!next) return;
  const index = workspace.projects.findIndex(p => p.id === next.id);
  if (index >= 0) workspace.projects[index] = next;
  else workspace.projects.push(next);
  project = next;
}

function projectTitle() { return project?.title || project?.name || 'Dự án'; }

function refreshProjectSelect() {
  const select = $('#project-select');
  select.innerHTML = workspace.projects.map(p => `<option value="${esc(p.id)}">${esc(p.title || p.name || 'Chưa đặt tên')}</option>`).join('');
  select.value = project?.id || '';
}

function renderBible() {
  const bible = ensureBible();
  $('#bible-name').value = bible.name || '';
  $('#bible-main').value = bible.main || '';
  $('#bible-style').value = bible.styleLock || '';
  $('#bible-negative').value = bible.negative || '';
  $('#bible-template').value = bible.promptTemplate || DEFAULT_TEMPLATE;
  $('#bible-max-seconds').value = bible.sceneRules?.maxSeconds ?? 8;
  $('#bible-min-seconds').value = bible.sceneRules?.minSeconds ?? 2.5;
  $('#bible-main-list').innerHTML = bible.characters.map(c => `<option value="${esc(c.name)}"></option>`).join('');
  $('#bible-summary').textContent = `${bible.characters.length} nhân vật · ${bible.backgrounds.length} bối cảnh`;
  renderCharacters();
  renderBackgrounds();
}

function renderCharacters() {
  const list = ensureBible().characters;
  $('#characters').innerHTML = list.map((character, index) => `
    <div class="editor-row" data-kind="character" data-index="${index}">
      <div class="row three">
        <label>Tên<input data-key="name" type="text" value="${esc(character.name)}"></label>
        <label>Vai trò<input data-key="role" type="text" value="${esc(character.role || '')}"></label>
        <label>Ảnh tham chiếu (URL, cách nhau dấu phẩy)<input data-key="refImages" type="text" value="${esc((character.refImages || []).join(', '))}"></label>
      </div>
      <label>Mô tả khóa ngoại hình<textarea data-key="description" rows="2">${esc(character.description || '')}</textarea></label>
      <div class="editor-actions"><button type="button" data-remove-character="${index}">Xoá</button></div>
    </div>`).join('') || '<p class="muted">Chưa có nhân vật. Import bible hoặc thêm mới.</p>';
}

function renderBackgrounds() {
  const list = ensureBible().backgrounds;
  $('#backgrounds').innerHTML = list.map((background, index) => `
    <div class="editor-row" data-kind="background" data-index="${index}">
      <div class="row">
        <label>Tên<input data-key="name" type="text" value="${esc(background.name)}"></label>
        <label>Ảnh tham chiếu (URL, cách nhau dấu phẩy)<input data-key="refImages" type="text" value="${esc((background.refImages || []).join(', '))}"></label>
      </div>
      <label>Mô tả<textarea data-key="description" rows="2">${esc(background.description || '')}</textarea></label>
      <div class="editor-actions"><button type="button" data-remove-background="${index}">Xoá</button></div>
    </div>`).join('') || '<p class="muted">Chưa có bối cảnh.</p>';
}

function scriptStats() {
  const text = $('#script-narration').value.trim();
  const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
  return `${words} từ · ~${(words / 140).toFixed(1)} phút`;
}

function renderScript() {
  const script = ensureScript();
  $('#script-brief').value = script.brief || '';
  $('#script-minutes').value = script.targetMinutes || 10;
  $('#script-tone').value = script.tone || 'kể chuyện lịch sử';
  $('#script-audience').value = script.audience || 'người xem phổ thông';
  $('#script-outline').value = script.outline || '';
  $('#script-title').value = script.title || project.title || '';
  $('#script-narration').value = script.draft || project.narration || '';
  $('#script-stats').textContent = scriptStats();
  $('#script-status').textContent = project.narration ? 'Kịch bản đã duyệt' : 'Chưa duyệt';
  $('#script-ai-note').textContent = settings?.ai?.baseUrl
    ? `AI: ${settings.ai.model || '?'} @ ${settings.ai.baseUrl}${settings.ai.groqFallback ? ' · fallback Groq' : ''}`
    : 'Chưa cấu hình AI.';
}

function renderVoice() {
  $('#tts-base').value = settings?.tts?.baseUrl || 'http://127.0.0.1:8000/v1';
  $('#tts-model').value = settings?.tts?.model || 'vieneu-v3-turbo';
  $('#tts-voice').value = settings?.tts?.voice || 'Mai Anh';
  $('#voice-duration').textContent = project.voiceSeconds ? fmtSeconds(project.voiceSeconds) : 'Chưa có voice';
  const audio = $('#voice-audio');
  if (project.voiceData) {
    audio.src = project.voiceData;
    audio.hidden = false;
  } else {
    audio.removeAttribute('src');
    audio.hidden = true;
  }
}

function renderScenes() {
  const scenes = project.scenes || [];
  const clip = project.clipSeconds || ensureBible().sceneRules?.maxSeconds || 8;
  $('#clip-seconds').value = clip;
  $('#min-seconds').value = ensureBible().sceneRules?.minSeconds || 2.5;
  const withPrompt = scenes.filter(s => s.prompt?.trim()).length;
  const withImage = scenes.filter(s => s.image).length;
  $('#scene-summary').textContent = `${scenes.length} cảnh · ${withPrompt} prompt · ${withImage} ảnh`;
  const missingImage = scenes.length - withImage;
  const warning = $('#scene-warning');
  if (scenes.length && missingImage > 0) {
    warning.hidden = false;
    warning.textContent = `Còn ${missingImage} cảnh chưa có ảnh. Chỉ dựng video khi đã kiểm tra đủ ảnh.`;
  } else {
    warning.hidden = true;
    warning.textContent = '';
  }
  $('#scenes').innerHTML = scenes.map((scene, index) => {
    const image = scene.image
      ? `<img src="${esc(scene.image)}" alt="Ảnh cảnh ${Number(scene.index) || index + 1}" loading="lazy">`
      : '<span class="muted">—</span>';
    return `<tr data-scene-row="${index}">
      <td>${Number(scene.index) || index + 1}</td>
      <td>${Number(scene.duration || 0).toFixed(2)}s</td>
      <td class="narration">${esc(scene.narration || '')}</td>
      <td class="prompt"><textarea data-scene="${index}" data-key="prompt" rows="3" placeholder="Chưa có prompt">${esc(scene.prompt || '')}</textarea></td>
      <td class="image-cell">${image}</td>
    </tr>`;
  }).join('') || '<tr><td colspan="5" class="muted">Chưa có cảnh. Tạo voice rồi bấm Chia cảnh.</td></tr>';
  $('#prompt-status').textContent = scenes.length ? `${withPrompt}/${scenes.length} cảnh có prompt` : '';
}

function flowSettings() {
  const flow = settings?.flow || {};
  return {
    projectUrl: project.flow?.projectUrl || flow.projectUrl || '',
    profileDir: flow.profileDir || '',
    downloadDir: flow.downloadDir || '',
    generateDelayMs: flow.generateDelayMs || 60000,
    headless: Boolean(flow.headless),
    selectors: flow.selectors || {},
  };
}

function renderFlow() {
  const flow = flowSettings();
  $('#flow-url').value = flow.projectUrl;
  $('#flow-profile').value = flow.profileDir;
  $('#flow-download').value = flow.downloadDir;
  $('#flow-delay').value = flow.generateDelayMs;
  $('#flow-headless').checked = flow.headless;
  $('#sel-prompt').value = flow.selectors.prompt || '';
  $('#sel-generate').value = flow.selectors.generate || '';
  $('#sel-image').value = flow.selectors.image || '';
  $('#sel-download').value = flow.selectors.download || '';
  $('#sel-refadd').value = flow.selectors.referenceAdd || '';
  $('#sel-refinput').value = flow.selectors.referenceInput || '';
  $('#sel-imagemode').value = flow.selectors.imageMode || '';
  const open = $('#flow-open');
  if (flow.projectUrl) { open.href = flow.projectUrl; open.hidden = false; } else open.hidden = true;
  renderFlowResult(project.flow?.verification || null);
}

function renderRender() {
  const scenes = project.scenes || [];
  const images = scenes.filter(s => s.image).length;
  const prompts = scenes.filter(s => s.prompt?.trim()).length;
  const seconds = scenes.reduce((sum, s) => sum + Number(s.duration || 0), 0);
  $('#render-summary').innerHTML = `
    <div>Cảnh<strong>${scenes.length}</strong></div>
    <div>Ảnh đã gắn<strong>${images}/${scenes.length}</strong></div>
    <div>Prompt<strong>${prompts}/${scenes.length}</strong></div>
    <div>Tổng thời lượng<strong>${fmtSeconds(seconds)}</strong></div>
    <div>Voice<strong>${project.voiceSeconds ? fmtSeconds(project.voiceSeconds) : '—'}</strong></div>`;
  const result = project.renderResult;
  const href = result?.url || (project.renderJobDone ? `/api/renders/${project.renderJobDone}/download` : '');
  $('#render-result').innerHTML = result && href
    ? `<a href="${esc(href)}" download>${esc(result.fileName || 'video.mp4')}</a><span class="muted">${result.sizeBytes ? (result.sizeBytes / 1024 / 1024).toFixed(1) + ' MB' : ''}</span>`
    : '';
  if (!result && project.renderJobId) {
    $('#render-status').textContent = 'Video đang dựng hoặc chưa hoàn tất.';
  }
}

function renderAll() {
  refreshProjectSelect();
  renderBible();
  renderScript();
  renderVoice();
  renderScenes();
  renderFlow();
  renderRender();
  showStep(currentStep);
}

function showStep(name) {
  currentStep = name;
  $$('.step').forEach(section => section.classList.toggle('active', section.id === `step-${name}`));
  $$('#steps button').forEach(button => button.classList.toggle('active', button.dataset.step === name));
}

async function selectProject(id) {
  if (!workspace) return;
  if (project?.id === id) { renderAll(); return; }
  try { await save({quiet: true}); } catch (error) { log(`Không lưu được dự án trước khi chuyển: ${error.message}`, 'error'); }
  project = workspace.projects.find(p => p.id === id) || workspace.projects[0];
  localStorage.setItem('pipeline.project', project?.id || '');
  renderAll();
}

async function run(label, fn) {
  if (busy) { log('Đang chạy tác vụ khác, chờ xong đã.', 'error'); return; }
  busy = true;
  setStatus(label);
  try { return await fn(); }
  catch (error) { log(error.message, 'error'); setStatus(error.message, 'error'); }
  finally { busy = false; }
}

async function loadBibleList() {
  try {
    const data = await api('/api/bibles');
    $('#bible-import').innerHTML = data.files.length
      ? data.files.map(file => `<option value="${esc(file.file)}">${esc(file.name)} (${file.file})</option>`).join('')
      : '<option value="">Không có roster JSON</option>';
  } catch (error) { log(`Không đọc được danh sách bible: ${error.message}`, 'error'); }
}

async function refreshVoiceStatus(showToast = true) {
  try {
    const data = await api('/api/voice/status');
    if (data.ok) {
      const voices = (data.voices || []).map(v => v.name || v.id || v.voice).filter(Boolean);
      $('#voice-options').innerHTML = voices.map(name => `<option value="${esc(name)}"></option>`).join('');
      $('#tts-status').textContent = `Online · ${voices.length} giọng`;
      if (showToast) setStatus(`VieNeu online tại ${data.baseUrl}.`, 'ok');
    } else {
      $('#tts-status').textContent = 'Offline';
      if (showToast) setStatus(data.hint || data.error || 'VieNeu chưa chạy.', 'error');
    }
  } catch (error) {
    $('#tts-status').textContent = 'Không kiểm tra được';
    if (showToast) setStatus(error.message, 'error');
  }
}

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(Error('Không đọc được file.'));
    reader.readAsDataURL(file);
  });
}

async function imageDimensions(file) {
  try {
    const bitmap = await createImageBitmap(file);
    const size = {width: bitmap.width, height: bitmap.height};
    bitmap.close();
    return size;
  } catch { return {width: 0, height: 0}; }
}

function downloadText(filename, text, mime = 'text/plain;charset=utf-8') {
  const blob = new Blob([text], {type: mime});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

function renderFlowResult(verification) {
  const box = $('#flow-result');
  if (!verification) { box.innerHTML = '<p class="muted">Chưa kiểm tra.</p>'; return; }
  const summary = verification.summary || {};
  const ok = verification.ok;
  const rows = [];
  for (const item of verification.items || []) {
    if (item.status === 'ok') continue;
    rows.push(`<tr><td>${item.index}</td><td>${esc(item.output)}</td><td>${item.status}</td><td>${esc((item.reasons || []).join(' '))}</td></tr>`);
  }
  const dupes = (verification.duplicates || []).map(d => `<tr><td>${d.index}</td><td>trùng</td><td>duplicate</td><td>${esc((d.files || []).join(', '))}</td></tr>`).join('');
  const extras = (verification.extra || []).map(e => `<tr><td>${e.index}</td><td>thừa</td><td>extra</td><td>${esc((e.files || []).join(', '))}</td></tr>`).join('');
  box.innerHTML = `
    <p class="${ok ? 'ok' : 'error'}"><strong>${ok ? 'Đạt' : 'Chưa đạt'}</strong> · nhận ${verification.received}/${verification.expected} ảnh · ok ${summary.ok || 0} · thiếu ${summary.missing || 0} · lỗi ${summary.invalid || 0} · trùng ${summary.duplicates || 0} · thừa ${summary.extra || 0}</p>
    ${rows.length || dupes || extras ? `<div class="table-wrap"><table><thead><tr><th>#</th><th>File</th><th>Trạng thái</th><th>Lý do</th></tr></thead><tbody>${rows.join('')}${dupes}${extras}</tbody></table></div>` : ''}`;
}

async function verifyFiles(files, source = 'manual') {
  if (!files.length) throw Error('Chưa có ảnh để kiểm tra.');
  lastFlowFiles = files;
  setStatus(`Đang kiểm tra ${files.length} ảnh…`);
  const data = await api('/api/flow/verify', {method: 'POST', body: {project, files}});
  renderFlowResult(data.verification);
  const nextProject = {...data.project, flow: {
    ...(data.project.flow || project.flow || {}),
    verification: data.verification,
    expected: data.verification.expected,
    received: data.verification.received,
    verifiedAt: new Date().toISOString(),
    source,
  }};
  adoptProject(nextProject);
  await save({quiet: true});
  renderFlowResult(data.verification);
  if (data.verification.ok) {
    renderAll();
    setStatus('Ảnh khớp đủ. Có thể sang bước Ghép video.', 'ok');
    showStep('render');
  } else {
    renderScenes();
    setStatus('Ảnh chưa đạt kiểm tra. Xem bảng lỗi bên dưới.', 'error');
  }
  return data;
}

async function pollFlowJob(id) {
  if (flowPolling) return;
  flowPolling = true;
  $('#flow-progress').hidden = false;
  try {
    for (;;) {
      const job = await api(`/api/flow/jobs/${id}`);
      const total = Number(job.total) || 1;
      const done = Number(job.done) || 0;
      $('#flow-bar').style.width = `${Math.min(100, Math.round(done / total * 100))}%`;
      $('#flow-message').textContent = job.message || '';
      if (job.status === 'running') { await sleep(2000); continue; }
      if (job.status === 'done') {
        $('#flow-message').textContent = job.message || 'Đã tải xong.';
        if (job.files?.length) await verifyFiles(job.files, 'flow');
        break;
      }
      if (job.status === 'needs_login') {
        setStatus(job.message || 'Cần đăng nhập Flow.', 'error');
        $('#flow-message').textContent = `${job.message || ''} Đăng nhập trong cửa sổ Chrome đang mở rồi bấm Chạy tự động lại.`;
        break;
      }
      throw Error(job.message || 'Job Flow thất bại.');
    }
  } finally { flowPolling = false; }
}

function bind() {
  $('#project-select').addEventListener('change', event => selectProject(event.target.value));
  $('#new-project').addEventListener('click', () => run('Đang tạo dự án…', async () => {
    const created = createProject();
    workspace.projects.push(created);
    await save({quiet: true});
    project = workspace.projects.find(p => p.id === created.id) || created;
    localStorage.setItem('pipeline.project', project.id);
    currentStep = 'bible';
    renderAll();
    setStatus('Đã tạo dự án mới.', 'ok');
  }));
  $('#save').addEventListener('click', () => run('Đang lưu…', async () => { await save(); }));
  $$('#steps button').forEach(button => button.addEventListener('click', () => showStep(button.dataset.step)));

  // Bible fields
  $('#bible-name').addEventListener('input', e => { ensureBible().name = e.target.value; });
  $('#bible-main').addEventListener('input', e => { ensureBible().main = e.target.value; });
  $('#bible-style').addEventListener('input', e => { ensureBible().styleLock = e.target.value; });
  $('#bible-negative').addEventListener('input', e => { ensureBible().negative = e.target.value; });
  $('#bible-template').addEventListener('input', e => { ensureBible().promptTemplate = e.target.value; });
  $('#bible-max-seconds').addEventListener('input', e => { ensureBible().sceneRules.maxSeconds = Number(e.target.value) || 8; });
  $('#bible-min-seconds').addEventListener('input', e => { ensureBible().sceneRules.minSeconds = Number(e.target.value) || 2.5; });

  $('#characters').addEventListener('input', event => {
    const row = event.target.closest('[data-kind="character"]');
    if (!row) return;
    const item = ensureBible().characters[Number(row.dataset.index)];
    if (!item) return;
    const key = event.target.dataset.key;
    if (key === 'refImages') item.refImages = event.target.value.split(/[\n,]+/).map(s => s.trim()).filter(Boolean).slice(0, 3);
    else item[key] = event.target.value;
  });
  $('#characters').addEventListener('click', event => {
    const index = event.target.dataset.removeCharacter;
    if (index === undefined) return;
    ensureBible().characters.splice(Number(index), 1);
    renderBible();
  });
  $('#backgrounds').addEventListener('input', event => {
    const row = event.target.closest('[data-kind="background"]');
    if (!row) return;
    const item = ensureBible().backgrounds[Number(row.dataset.index)];
    if (!item) return;
    const key = event.target.dataset.key;
    if (key === 'refImages') item.refImages = event.target.value.split(/[\n,]+/).map(s => s.trim()).filter(Boolean).slice(0, 3);
    else item[key] = event.target.value;
  });
  $('#backgrounds').addEventListener('click', event => {
    const index = event.target.dataset.removeBackground;
    if (index === undefined) return;
    ensureBible().backgrounds.splice(Number(index), 1);
    renderBible();
  });
  $('#add-character').addEventListener('click', () => {
    ensureBible().characters.push({name: 'Nhân vật mới', role: '', description: '', refImages: []});
    renderBible();
  });
  $('#add-background').addEventListener('click', () => {
    ensureBible().backgrounds.push({name: 'Bối cảnh mới', description: '', refImages: []});
    renderBible();
  });
  $('#bible-import-btn').addEventListener('click', () => run('Đang import bible…', async () => {
    const file = $('#bible-import').value;
    if (!file) throw Error('Chọn file roster JSON.');
    const data = await api('/api/bibles/import', {method: 'POST', body: {file}});
    project.bible = data.bible;
    renderBible();
    await save({quiet: true});
    setStatus(`Đã import ${data.bible.name}.`, 'ok');
  }));
  $('#save-bible').addEventListener('click', () => run('Đang lưu bible…', async () => {
    ensureBible();
    await save();
    renderBible();
  }));

  // Script
  $('#script-brief').addEventListener('input', e => { ensureScript().brief = e.target.value; });
  $('#script-minutes').addEventListener('input', e => { ensureScript().targetMinutes = Number(e.target.value) || 10; });
  $('#script-tone').addEventListener('input', e => { ensureScript().tone = e.target.value; });
  $('#script-audience').addEventListener('input', e => { ensureScript().audience = e.target.value; });
  $('#script-outline').addEventListener('input', e => { ensureScript().outline = e.target.value; });
  $('#script-title').addEventListener('input', e => { ensureScript().title = e.target.value; });
  $('#script-narration').addEventListener('input', e => { ensureScript().draft = e.target.value; $('#script-stats').textContent = scriptStats(); });
  $('#ai-script').addEventListener('click', () => run('AI đang viết kịch bản…', async () => {
    const script = ensureScript();
    if (!script.brief?.trim()) throw Error('Nhập brief/chủ đề trước.');
    const body = {
      bible: project.bible,
      brief: script.brief,
      targetMinutes: Number(script.targetMinutes) || 10,
      tone: script.tone || 'kể chuyện lịch sử',
      audience: script.audience || 'người xem phổ thông',
      outline: script.outline || '',
    };
    const data = await api('/api/ai/script', {method: 'POST', body});
    script.title = data.title;
    script.draft = data.narration;
    script.generatedAt = new Date().toISOString();
    $('#script-title').value = data.title;
    $('#script-narration').value = data.narration;
    $('#script-stats').textContent = scriptStats();
    await save({quiet: true});
    setStatus(`AI đã viết ${data.stats?.words || 0} từ. Duyệt hoặc sửa trước khi dùng.`, 'ok');
  }));
  $('#approve-script').addEventListener('click', () => run('Đang duyệt kịch bản…', async () => {
    const narration = $('#script-narration').value.trim();
    if (!narration) throw Error('Chưa có lời đọc.');
    project.title = $('#script-title').value.trim() || project.title;
    project.narration = narration;
    project.script = {...ensureScript(), draft: narration, approvedAt: new Date().toISOString()};
    await save({quiet: true});
    renderScript();
    refreshProjectSelect();
    setStatus('Đã duyệt kịch bản. Sang bước Voice.', 'ok');
    showStep('voice');
  }));
  $('#export-script').addEventListener('click', () => {
    const narration = $('#script-narration').value.trim();
    if (!narration) { setStatus('Chưa có kịch bản để xuất.', 'error'); return; }
    downloadText(`${projectTitle().replace(/[^\p{L}\p{N}]+/gu, '-') || 'kich-ban'}.txt`, narration + '\n');
  });

  // Voice
  $('#save-tts').addEventListener('click', () => run('Đang lưu cài đặt voice…', async () => {
    await api('/api/pipeline/settings', {method: 'PUT', body: {tts: {baseUrl: $('#tts-base').value.trim(), model: $('#tts-model').value.trim(), voice: $('#tts-voice').value.trim()}}});
    settings = await api('/api/pipeline/settings');
    setStatus('Đã lưu cài đặt VieNeu.', 'ok');
  }));
  $('#test-tts').addEventListener('click', () => run('Đang kiểm tra VieNeu…', async () => { await refreshVoiceStatus(true); }));
  $('#clone-voice').addEventListener('click', () => run('Đang clone giọng…', async () => {
    const file = $('#clone-file').files[0];
    if (!file) throw Error('Chọn file mẫu giọng.');
    const name = $('#clone-name').value.trim();
    if (!name) throw Error('Nhập tên giọng.');
    const dataUrl = await fileToDataURL(file);
    await api('/api/voice/clone', {method: 'POST', body: {name, dataUrl}});
    $('#tts-voice').value = name;
    await api('/api/pipeline/settings', {method: 'PUT', body: {tts: {voice: name}}});
    settings = await api('/api/pipeline/settings');
    await refreshVoiceStatus(false);
    setStatus(`Đã clone giọng ${name}. Chọn giọng này và tạo voice.`, 'ok');
  }));
  $('#make-voice').addEventListener('click', () => run('VieNeu đang tạo voice… (có thể vài phút)', async () => {
    const text = project.narration || $('#script-narration').value.trim();
    if (!text) throw Error('Chưa có kịch bản đã duyệt.');
    if (!project.narration) project.narration = text;
    const voice = $('#tts-voice').value.trim();
    const data = await api('/api/voice/synthesize', {method: 'POST', body: {text, voice}});
    project.voiceData = data.url;
    project.voiceSeconds = data.duration;
    project.voiceFile = {name: 'voice.mp3', ext: 'mp3'};
    project.voiceProvider = 'vieneu';
    project.voiceModel = data.voice;
    await save({quiet: true});
    renderVoice();
    setStatus(`Đã tạo voice ${fmtSeconds(data.duration)} (${data.chunks} đoạn). Sang Phân cảnh.`, 'ok');
    showStep('scenes');
  }));

  // Scenes
  $('#split-scenes').addEventListener('click', () => run('Đang chia cảnh theo voice…', async () => {
    if (!project.narration) throw Error('Chưa có kịch bản đã duyệt.');
    if (!project.voiceData) throw Error('Chưa có voice. Tạo voice trước.');
    const data = await api('/api/scenes/split', {method: 'POST', body: {
      narration: project.narration,
      voiceUrl: project.voiceData,
      voiceSeconds: project.voiceSeconds,
      clipSeconds: Number($('#clip-seconds').value) || 8,
      minSeconds: Number($('#min-seconds').value) || 2.5,
    }});
    project.scenes = data.scenes;
    project.clipSeconds = Number($('#clip-seconds').value) || 8;
    project.voiceSeconds = data.voiceSeconds;
    project.scenesTiming = data.timingSource;
    project.scenesMatched = data.matchedPauses;
    await save({quiet: true});
    renderScenes();
    if (data.timingSource === 'words') log('Voice ít ngắt nghỉ; mốc cảnh là ước lượng theo số từ.', 'error');
    setStatus(`Đã chia ${data.scenes.length} cảnh (${data.timingSource}, khớp ${data.matchedPauses} ngắt).`, 'ok');
  }));
  $('#build-prompts').addEventListener('click', () => run('Đang ghép prompt…', async () => {
    if (!project.scenes?.length) throw Error('Chia cảnh trước.');
    if (!project.bible) throw Error('Import hoặc tạo bible trước để prompt bám nhân vật.');
    const data = await api('/api/prompts/build', {method: 'POST', body: {project}});
    adoptProject(data.project);
    lastQueue = data.queue;
    await save({quiet: true});
    renderScenes();
    setStatus(`Đã ghép ${data.count} prompt. Kiểm tra lại trước khi xuất queue.`, 'ok');
  }));
  $('#export-queue').addEventListener('click', () => run('Đang xuất queue Flow…', async () => {
    if (!project.scenes?.length) throw Error('Chia cảnh trước.');
    const data = await api('/api/flow/queue', {method: 'POST', body: {project}});
    adoptProject(data.project);
    lastQueue = data.queue;
    await save({quiet: true});
    $('#flow-links').innerHTML = `
      <a href="${esc(data.files.prompts)}" target="_blank" rel="noopener noreferrer">prompts.txt</a>
      <a href="${esc(data.files.csv)}" target="_blank" rel="noopener noreferrer">queue.csv</a>
      <a href="${esc(data.files.queue)}" target="_blank" rel="noopener noreferrer">queue.json</a>`;
    setStatus(`Đã xuất queue ${data.queue.items.length} prompt.`, 'ok');
    showStep('flow');
  }));
  $('#scenes').addEventListener('input', event => {
    if (event.target.dataset.scene === undefined || event.target.dataset.key !== 'prompt') return;
    const scene = project.scenes[Number(event.target.dataset.scene)];
    if (!scene) return;
    scene.prompt = event.target.value;
    scene.promptMode = 'manual';
  });

  // Flow settings + queue + run
  $('#flow-save').addEventListener('click', () => run('Đang lưu cài đặt Flow…', async () => {
    const flow = {
      projectUrl: $('#flow-url').value.trim(),
      profileDir: $('#flow-profile').value.trim(),
      downloadDir: $('#flow-download').value.trim(),
      generateDelayMs: Number($('#flow-delay').value) || 60000,
      headless: $('#flow-headless').checked,
      selectors: {
        prompt: $('#sel-prompt').value.trim(),
        generate: $('#sel-generate').value.trim(),
        image: $('#sel-image').value.trim(),
        download: $('#sel-download').value.trim(),
        referenceAdd: $('#sel-refadd').value.trim(),
        referenceInput: $('#sel-refinput').value.trim(),
        imageMode: $('#sel-imagemode').value.trim(),
      },
    };
    project.flow = {...(project.flow || {}), projectUrl: flow.projectUrl};
    settings = await api('/api/pipeline/settings', {method: 'PUT', body: {flow}});
    await save({quiet: true});
    renderFlow();
    setStatus('Đã lưu cài đặt Flow.', 'ok');
  }));
  $('#flow-queue').addEventListener('click', () => run('Đang xuất queue…', async () => {
    const data = await api('/api/flow/queue', {method: 'POST', body: {project}});
    adoptProject(data.project);
    lastQueue = data.queue;
    await save({quiet: true});
    $('#flow-links').innerHTML = `
      <a href="${esc(data.files.prompts)}" target="_blank" rel="noopener noreferrer">prompts.txt</a>
      <a href="${esc(data.files.csv)}" target="_blank" rel="noopener noreferrer">queue.csv</a>
      <a href="${esc(data.files.queue)}" target="_blank" rel="noopener noreferrer">queue.json</a>`;
    setStatus(`Queue ${data.queue.items.length} prompt đã sẵn sàng.`, 'ok');
  }));
  $('#flow-run').addEventListener('click', () => run('Đang chạy Google Flow…', async () => {
    if (!project.scenes?.length) throw Error('Chưa có cảnh.');
    const url = $('#flow-url').value.trim();
    if (!url) throw Error('Nhập URL project Flow.');
    project.flow = {...(project.flow || {}), projectUrl: url};
    const data = await api('/api/flow/run', {method: 'POST', body: {project, projectUrl: url, downloadDir: $('#flow-download').value.trim(), profileDir: $('#flow-profile').value.trim(), headless: $('#flow-headless').checked, generateDelayMs: Number($('#flow-delay').value) || 60000}});
    project.flow = {...(project.flow || {}), lastJobId: data.id};
    await save({quiet: true});
    setStatus(`Đã bắt đầu job Flow ${data.total} ảnh.`);
    $('#flow-message').textContent = 'Đang mở Chrome…';
    await pollFlowJob(data.id);
  }));
  $('#flow-import').addEventListener('click', () => run('Đang upload ảnh…', async () => {
    const files = [...($('#flow-files').files || [])];
    if (!files.length) throw Error('Chọn ảnh đã tải.');
    const out = [];
    for (const [index, file] of files.entries()) {
      $('#import-status').textContent = `Đang upload ${index + 1}/${files.length}: ${file.name}`;
      const dataUrl = await fileToDataURL(file);
      const asset = await api('/api/assets', {method: 'POST', body: {data: dataUrl}});
      const dims = await imageDimensions(file);
      out.push({name: file.name, url: asset.url, ...dims});
    }
    $('#import-status').textContent = `Đã upload ${out.length} ảnh. Đang kiểm tra…`;
    await verifyFiles(out, 'manual');
    $('#import-status').textContent = `Đã upload ${out.length} ảnh.`;
  }));

  // Render
  $('#render').addEventListener('click', () => run('Đang dựng video…', async () => {
    const scenes = project.scenes || [];
    if (!scenes.length) throw Error('Chưa có cảnh.');
    if (!project.voiceData) throw Error('Chưa có voice.');
    if (scenes.length > 1000) throw Error('Tối đa 1.000 cảnh mỗi video.');
    const missing = scenes.filter(s => !s.image);
    if (missing.length) throw Error(`Còn ${missing.length} cảnh chưa có ảnh. Kiểm tra Flow trước khi dựng.`);
    const sum = scenes.reduce((n, s) => n + Number(s.duration || 0), 0);
    if (Math.abs(sum - Number(project.voiceSeconds)) > 0.5) throw Error(`Tổng cảnh lệch voice ${(sum - Number(project.voiceSeconds)).toFixed(2)} giây. Chia lại cảnh.`);
    if (scenes.some(s => Number(s.duration) > 30 || Number(s.duration) < 0.5)) throw Error('Có cảnh ngoài 0,5–30 giây.');
    if (!project.renderJobId) {
      const job = await api('/api/render', {method: 'POST', body: {
        name: projectTitle(),
        scenes: scenes.map(s => ({duration: s.duration, kind: s.kind || 'image', image: s.image, clip: s.clip, html: s.html})),
        voice: project.voiceData,
        voiceExt: project.voiceFile?.ext || 'mp3',
      }});
      project.renderJobId = job.id;
      await save({quiet: true});
    }
    $('#render-progress').hidden = false;
    for (;;) {
      const job = await api(`/api/renders/${project.renderJobId}`);
      const progress = job.progress || {};
      $('#render-bar').style.width = `${Math.min(100, Math.round((progress.completed || 0) / Math.max(1, progress.total || scenes.length) * 100))}%`;
      $('#render-status').textContent = job.status === 'running' ? `Đang dựng ${progress.completed || 0}/${progress.total || scenes.length} cảnh…` : (job.message || '');
      if (job.status === 'done') {
        project.renderResult = job.result;
        project.renderJobDone = job.id;
        delete project.renderJobId;
        await save({quiet: true});
        renderRender();
        setStatus('Dựng video xong.', 'ok');
        break;
      }
      if (job.status === 'error') {
        delete project.renderJobId;
        await save({quiet: true});
        throw Error(job.error || 'Dựng video lỗi.');
      }
      await sleep(2000);
    }
  }));
}

async function init() {
  try {
    bind();
    workspace = await api('/api/state');
    settings = await api('/api/pipeline/settings');
    const savedId = localStorage.getItem('pipeline.project');
    project = workspace.projects.find(p => p.id === savedId) || workspace.projects[0] || null;
    if (!project) {
      project = createProject();
      workspace.projects.push(project);
      await save({quiet: true});
    }
    localStorage.setItem('pipeline.project', project.id);
    project.script ||= {};
    project.flow ||= {};
    ensureBible();
    await loadBibleList();
    renderAll();
    refreshVoiceStatus(false);
  } catch (error) {
    setStatus(error.message, 'error');
    log(error.message, 'error');
  }
}

init();
