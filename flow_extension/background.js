// Service worker: hỏi pipeline Python lấy lệnh -> chuyển cho tab Flow -> báo kết quả / tải ảnh lên.
importScripts('config.js');   // nạp BRIDGE_TOKEN (nếu có)
const SERVER = 'http://127.0.0.1:8765';
const EXT = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp' };
const authHeaders = () => (typeof BRIDGE_TOKEN === 'string' && BRIDGE_TOKEN ? { 'X-Bridge-Token': BRIDGE_TOKEN } : {});

async function flowTab() {
  const tabs = await chrome.tabs.query({ url: ['https://labs.google/*', 'https://flow.google/*'] });
  if (!tabs.length) throw new Error('Không có tab Google Flow đang mở');
  return tabs.find(t => t.active) || tabs[0];
}
const toTab = async (tab, msg) => {
  const r = await chrome.tabs.sendMessage(tab.id, msg);
  if (!r.ok) throw new Error(r.error);
  return r.data;
};
const b64ToBytes = b64 => Uint8Array.from(atob(b64), c => c.charCodeAt(0));

async function download(tab, { scene, key }) {
  const src = await toTab(tab, { cmd: 'tile_source', data: { key } });
  let bytes, mime;
  if (src.b64) { bytes = b64ToBytes(src.b64); mime = src.mime; }
  else { const r = await fetch(src.url); if (!r.ok) throw new Error('tải ảnh lỗi HTTP ' + r.status); mime = r.headers.get('content-type') || 'image/png'; bytes = await r.arrayBuffer(); }
  const ext = EXT[mime.split(';')[0]] || 'png';
  const up = await fetch(`${SERVER}/upload?scene=${scene}&ext=${ext}`, { method: 'POST', headers: authHeaders(), body: bytes });
  if (!up.ok) throw new Error('upload lỗi');
  return { bytes: bytes.byteLength };
}

async function handle(c) {
  const tab = await flowTab();
  switch (c.cmd) {
    case 'ping': case 'list_tiles': return toTab(tab, { cmd: c.cmd });
    case 'submit': return toTab(tab, { cmd: 'submit', data: c.data, timeoutMs: 180000 });
    case 'download': return download(tab, c.data);
    default: throw new Error('lệnh không hỗ trợ: ' + c.cmd);
  }
}

async function loop() {
  for (;;) {
    try {
      const c = await (await fetch(`${SERVER}/next`, { headers: authHeaders() })).json();
      if (c.cmd === 'idle') continue;
      let res;
      try { res = { id: c.id, ok: true, data: await handle(c) }; }
      catch (e) { res = { id: c.id, ok: false, error: String(e.message || e) }; }
      await fetch(`${SERVER}/result`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(res) });
    } catch { await new Promise(r => setTimeout(r, 2000)); }   // server Python chưa chạy -> thử lại
  }
}

// MV3 service worker bị Chrome tắt khi rảnh: alarm đánh thức để vòng lặp luôn sống
chrome.alarms?.create('keepalive', { periodInMinutes: 0.4 });
chrome.alarms?.onAlarm.addListener(() => {});
loop();
