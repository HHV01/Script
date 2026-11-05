// Chạy trong tab Google Flow. Nhận lệnh từ background.js, thao tác DOM, trả kết quả.
const sleep = ms => new Promise(r => setTimeout(r, ms));
const visible = el => el && el.offsetParent !== null && !el.disabled;

function tileKey(img) {
  if (img.dataset.mediaId) return 'media:' + img.dataset.mediaId;
  try { return new URL(img.src).pathname; } catch { return img.src; }
}
function tileMap() {
  const m = new Map();
  const gallery = document.querySelectorAll('img[data-media-id]');
  (gallery.length ? gallery : document.querySelectorAll(SEL.tileImg)).forEach(img => {
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

function imageCountGroup() {
  // Scope by the image heading: the video section has another x1–x4 group.
  const heading = [...document.querySelectorAll('h1,h2,h3,h4,div,p,span,label')]
    .filter(visible).find(el => SEL.imageDefaultsHeading.test((el.textContent || '').trim()));
  for (let el = heading; el; el = el.parentElement) {
    const choices = [...el.querySelectorAll('button,[role="radio"],[role="tab"]')]
      .filter(visible).filter(b => /^[x×][1-4]$/i.test(b.textContent.trim()));
    if (choices.length === 4 && choices.filter(b => /^[x×]1$/i.test(b.textContent.trim())).length === 1)
      return choices;
    if (choices.length > 4) break;  // Never choose the first of image + video groups.
  }
  return null;
}

function countSelected(el) {
  return el.getAttribute('aria-checked') === 'true' || el.getAttribute('aria-selected') === 'true'
    || el.getAttribute('aria-pressed') === 'true';
}

async function ensureSingleImage() {
  let group = imageCountGroup();
  if (!group) {
    // Observed Flow agent settings button; do not click unrelated account settings.
    const buttons = _controls().filter(b => b.textContent.trim() === 'tune'
      && /cài đặt|settings/i.test(b.getAttribute('aria-label') || ''));
    if (buttons.length !== 1) throw new Error('Không xác định được cài đặt tạo ảnh để kiểm x1; chưa gửi prompt.');
    buttons[0].click();
    for (let i = 0; i < 30 && !group; i++) { await sleep(100); group = imageCountGroup(); }
  }
  if (!group) throw new Error('Không tìm được riêng nhóm số ảnh x1–x4; chưa gửi prompt.');
  const one = group.find(b => /^[x×]1$/i.test(b.textContent.trim()));
  if (!countSelected(one)) one.click();
  for (let i = 0; i < 20 && !countSelected(one); i++) await sleep(100);
  if (!countSelected(one) || group.some(b => b !== one && countSelected(b)))
    throw new Error('Chưa xác nhận được tạo ảnh x1; chặn gửi prompt.');
  const saves = _controls().filter(b => /^(lưu|save)$/i.test(b.textContent.trim()));
  if (saves.length !== 1) throw new Error('Không xác định được nút lưu x1; chưa gửi prompt.');
  saves[0].click();
  for (let i = 0; i < 30 && imageCountGroup(); i++) await sleep(100);
  if (imageCountGroup()) throw new Error('Cài đặt x1 chưa đóng/lưu xong; chặn gửi prompt.');
  return { image_count: 1, scope: 'image_defaults_only' };
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

function scrollToNewest(discoverContainers = false) {
  // Flow dùng virtual scroll: ảnh mới chỉ được render khi vùng lưới ở gần đầu.
  try { window.scrollTo(0, 0); } catch {}
  for (const el of document.querySelectorAll('main, mat-sidenav-content, [role="main"], .cdk-virtual-scroll-viewport')) {
    try { el.scrollTop = 0; } catch {}
  }
  // Discover custom scroll containers only during preparation, not every poll.
  if (!discoverContainers) return;
  for (const el of document.querySelectorAll('*')) {
    const style = getComputedStyle(el);
    if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 50) {
      try { el.scrollTop = 0; } catch {}
    }
  }
}

function clickElement(el) {
  // Một số nút Material/Angular không phản ứng với .click() đơn giản khi được gọi từ script.
  // Gửi đủ chuỗi sự kiện pointer/mouse để kích hoạt handler.
  for (const type of ['pointerover', 'pointerenter', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
    const EventCtor = type.startsWith('pointer') ? PointerEvent : MouseEvent;
    el.dispatchEvent(new EventCtor(type, { bubbles: true, cancelable: true, view: window, button: 0, buttons: 1, pointerId: 1, pointerType: 'mouse' }));
  }
}

function send(box) {
  const btn = SEL.sendButton(box);
  if (btn) { clickElement(btn); return; }
  box.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
}

async function prepareSubmit({ prompt, native_fill = false }) {
  await ensureImageMode();                       // chỉ tạo ảnh, không tạo video
  await ensureSingleImage();                     // required every submit, never x2/x3/x4
  let box = findPromptBox();
  for (let attempt = 0; !box && attempt < 20; attempt++) {
    await sleep(500);
    box = findPromptBox();
  }
  if (!box) throw new Error('Không thấy ô nhập prompt (chỉnh SEL.promptBox)');
  scrollToNewest(true);
  // Let virtual gallery layout settle before taking the baseline.
  await Promise.race([sleep(250),
    new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))]);
  const before = [...tileMap().keys()];
  if (!native_fill) await fillPrompt(box, prompt);
  return { before };
}

async function waitTiles({ before }, timeoutMs) {
  const previous = new Set(before);
  const t0 = Date.now();
  let signature = '', since = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    scrollToNewest();
    const fresh = [...tileMap().entries()].filter(([key]) => !previous.has(key));
    // A placeholder/new src is not a finished image. Check identity as well as count:
    // replacing one pending tile with another must restart the stability window.
    const current = JSON.stringify(fresh.map(([key]) => key).sort());
    if (current !== signature) { signature = current; since = Date.now(); }
    const ready = fresh.length && fresh.every(([, img]) =>
      img.complete && img.naturalWidth >= 200 && img.naturalHeight >= 128);
    if (ready && !isBusy() && Date.now() - since >= SEL.stableMs)
      return { tiles: fresh.map(([key]) => key) };
    await sleep(250);
  }
  throw new Error('Hết thời gian chờ ảnh (kiểm tra SEL.tileImg / SEL.busy)');
}

async function submit(data, timeoutMs) {
  const prepared = await prepareSubmit(data);
  send(findPromptBox());
  return await waitTiles(prepared, timeoutMs);
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
      else if (msg.cmd === 'prepare_submit') reply({ ok: true, data: await prepareSubmit(msg.data) });
      else if (msg.cmd === 'ensure_image_count') reply({ ok: true, data: await ensureSingleImage() });
      else if (msg.cmd === 'wait_tiles') reply({ ok: true, data: await waitTiles(msg.data, msg.timeoutMs) });
      else if (msg.cmd === 'tile_source') reply({ ok: true, data: await tileSource(msg.data.key) });
      else reply({ ok: false, error: 'lệnh không hỗ trợ: ' + msg.cmd });
    } catch (e) { reply({ ok: false, error: String(e.message || e) }); }
  })();
  return true;   // trả lời bất đồng bộ
});
