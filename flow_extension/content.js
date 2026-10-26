// Chạy trong tab Google Flow. Nhận lệnh từ background.js, thao tác DOM, trả kết quả.
const sleep = ms => new Promise(r => setTimeout(r, ms));
const visible = el => el && el.offsetParent !== null && !el.disabled;

function tileKey(img) {
  try { return new URL(img.src).pathname; } catch { return img.src; }
}
function tileMap() {
  const m = new Map();
  document.querySelectorAll(SEL.tileImg).forEach(img => {
    if (img.naturalWidth >= 200 || !img.complete) m.set(tileKey(img), img);   // bỏ icon/avatar nhỏ
  });
  return m;
}
const isBusy = () => SEL.busy.some(s => document.querySelector(s));

// --- Chỉ cho phép chế độ Image, không bao giờ tạo video ---
const IMAGE_RE = /image|hình ảnh|hinh anh|photo|still/i;
const VIDEO_RE = /video|clip|phim/i;
const _label = el => `${el.textContent || ''} ${el.getAttribute('aria-label') || ''} ${el.title || ''}`.toLowerCase();
const _active = el => el.getAttribute('aria-selected') === 'true' || el.getAttribute('aria-pressed') === 'true'
  || /(^|\s)(active|selected)(\s|$)/i.test(el.className || '');
const _controls = () => [...document.querySelectorAll('button, [role="tab"], [role="radio"], a')].filter(visible);

async function ensureImageMode() {
  if (SEL.imageMode) {
    const el = document.querySelector(SEL.imageMode);
    if (el && visible(el)) { el.click(); await sleep(500); }
  }
  const image = _controls().find(el => IMAGE_RE.test(_label(el)));
  if (image) { image.click(); await sleep(600); }
  const videoActive = _controls().some(el => VIDEO_RE.test(_label(el)) && _active(el));
  if (videoActive) {
    throw new Error('Flow đang ở chế độ Video và không chuyển được sang Image. '
      + 'Hãy chuyển sang Image/Hình ảnh thủ công, hoặc chỉnh SEL.imageMode trong flow_extension/selectors.js');
  }
}

function findPromptBox() {
  for (const s of SEL.promptBox) {
    const el = [...document.querySelectorAll(s)].find(visible);
    if (el) return el;
  }
  return null;
}

async function fillPrompt(el, text) {
  el.focus();
  if ('value' in el) {
    const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value')?.set;
    setter ? setter.call(el, text) : (el.value = text);
  } else {
    document.execCommand('selectAll', false, null);
    document.execCommand('insertText', false, text);
  }
  el.dispatchEvent(new InputEvent('input', { bubbles: true, composed: true, data: text, inputType: 'insertText' }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  await sleep(400);
}

function send(box) {
  const btn = SEL.sendButton(box);
  if (btn) { btn.click(); return; }
  box.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
}

async function submit({ prompt }, timeoutMs) {
  await ensureImageMode();                       // chỉ tạo ảnh, không tạo video
  const box = findPromptBox();
  if (!box) throw new Error('Không thấy ô nhập prompt (chỉnh SEL.promptBox)');
  const before = new Set(tileMap().keys());
  await fillPrompt(box, prompt);
  send(box);
  const t0 = Date.now();
  let last = -1, since = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    await sleep(1000);
    const fresh = [...tileMap().keys()].filter(k => !before.has(k));
    if (fresh.length !== last) { last = fresh.length; since = Date.now(); continue; }
    if (fresh.length && !isBusy() && Date.now() - since >= SEL.stableMs) return { tiles: fresh };
  }
  throw new Error('Hết thời gian chờ ảnh (kiểm tra SEL.tileImg / SEL.busy)');
}

async function tileSource(key) {
  const img = tileMap().get(key);
  if (!img) throw new Error('Không thấy ảnh ' + key + ' trong tab');
  // blob:/data: chỉ đọc được từ trang -> đọc ở đây; URL thường để background tải
  if (/^(blob|data):/.test(img.src)) {
    const blob = await (await fetch(img.src)).blob();
    const b64 = await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result.split(',')[1]); r.readAsDataURL(blob); });
    return { b64, mime: blob.type };
  }
  return { url: img.src };
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  (async () => {
    try {
      if (msg.cmd === 'ping') reply({ ok: true, data: { url: location.href, tiles: tileMap().size, promptBox: !!findPromptBox() } });
      else if (msg.cmd === 'list_tiles') reply({ ok: true, data: { keys: [...tileMap().keys()] } });
      else if (msg.cmd === 'submit') reply({ ok: true, data: await submit(msg.data, msg.timeoutMs) });
      else if (msg.cmd === 'tile_source') reply({ ok: true, data: await tileSource(msg.data.key) });
      else reply({ ok: false, error: 'lệnh không hỗ trợ: ' + msg.cmd });
    } catch (e) { reply({ ok: false, error: String(e.message || e) }); }
  })();
  return true;   // trả lời bất đồng bộ
});
