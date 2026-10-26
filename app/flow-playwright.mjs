// Google Flow automation bằng Playwright + profile Chrome đã đăng nhập.
// Đây là adapter tách rời: lỗi selector/UI Flow không làm hỏng phần còn lại của app.
// Lần đầu chạy headed để đăng nhập; profile được giữ lại cho các lần sau.
import {existsSync} from 'node:fs';
import {mkdir, readFile, writeFile, stat, rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {chromium} from 'playwright-core';

const IMAGE_EXT = /\.(png|jpe?g|webp)$/i;

function chromeExecutable() {
  const candidates = [
    process.env.CHROME_PATH,
    path.join(os.homedir(), 'AppData', 'Local', 'ms-playwright', 'chromium-1248', 'chrome-win64', 'chrome.exe'),
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  ].filter(Boolean);
  return candidates.find(file => { try { return existsSync(file); } catch { return false; } }) || null;
}

function imageKind(bytes) {
  if (bytes.length >= 8 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) return {ext: 'png', mime: 'image/png'};
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return {ext: 'jpg', mime: 'image/jpeg'};
  if (bytes.length >= 12 && bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP') return {ext: 'webp', mime: 'image/webp'};
  return null;
}

function mimeFromName(name) {
  return /\.png$/i.test(name) ? 'image/png' : /\.webp$/i.test(name) ? 'image/webp' : 'image/jpeg';
}

async function writeImage(fileBase, bytes) {
  const kind = imageKind(bytes);
  if (!kind) throw Error('File tải về không phải ảnh PNG/JPEG/WebP.');
  const file = `${fileBase}.${kind.ext}`;
  await writeFile(file, bytes);
  return {file, name: path.basename(file), mime: kind.mime};
}

async function readAssetUrl(assets, url) {
  if (!url || !String(url).startsWith('/api/assets/')) return null;
  try { const asset = assets.info(url); if (existsSync(asset.file)) return asset.file; } catch { /* ignore */ }
  return null;
}

async function fillPrompt(page, selector, text) {
  const locator = page.locator(selector).first();
  await locator.waitFor({state: 'visible', timeout: 25000});
  try {
    await locator.fill(text, {timeout: 10000});
  } catch {
    await locator.click({timeout: 10000});
    await page.keyboard.press('Control+A');
    await page.keyboard.insertText(text);
  }
  await page.waitForTimeout(400);
}

async function clickByIcon(page, {icons = [], labels = []}) {
  return page.evaluate(({icons, labels}) => {
    const visible = (el) => el && el.offsetParent !== null && !el.disabled;
    const buttons = [...document.querySelectorAll('button, [role="button"]')].filter(visible);
    const hit = buttons.reverse().find(btn => {
      const icon = [...btn.querySelectorAll('mat-icon, svg, i')].map(n => (n.textContent || '').trim().toLowerCase()).join(' ');
      const text = `${btn.textContent || ''} ${btn.getAttribute('aria-label') || ''} ${btn.title || ''}`.toLowerCase();
      return icons.some(name => icon.includes(name)) || labels.some(name => text.includes(name));
    });
    if (hit) { hit.click(); return true; }
    return false;
  }, {icons, labels});
}

// Chỉ cho phép Flow ở chế độ tạo ảnh. Không bao giờ bấm Video/Clip.
async function ensureImageMode(page, selectors) {
  const explicit = String(selectors.imageMode || '').trim();
  let result = {clicked: false, videoActive: false};
  if (explicit) {
    const locator = page.locator(explicit).first();
    if (await locator.count()) {
      await locator.click({timeout: 8000}).catch(() => {});
      await page.waitForTimeout(700);
      result = {clicked: true, videoActive: false};
    }
  }
  if (!result.clicked) {
    result = await page.evaluate(() => {
      const visible = (el) => el && el.offsetParent !== null;
      const label = (el) => `${el.textContent || ''} ${el.getAttribute('aria-label') || ''} ${el.title || ''}`.toLowerCase();
      const controls = [...document.querySelectorAll('button, [role="tab"], [role="radio"], a')].filter(visible);
      const image = controls.find(el => /image|hình ảnh|hinh anh|photo|still/i.test(label(el)));
      const video = controls.find(el => /video|clip|phim/i.test(label(el)));
      const active = (el) => Boolean(el && (el.getAttribute('aria-selected') === 'true' || el.getAttribute('aria-pressed') === 'true' || /(^|\s)(active|selected)(\s|$)/i.test(el.className || '')));
      if (image) { image.click(); return {clicked: true, videoActive: active(video)}; }
      return {clicked: false, videoActive: active(video)};
    });
    await page.waitForTimeout(700);
  }
  const videoStillActive = await page.evaluate(() => {
    const visible = (el) => el && el.offsetParent !== null;
    const label = (el) => `${el.textContent || ''} ${el.getAttribute('aria-label') || ''} ${el.title || ''}`.toLowerCase();
    const active = (el) => Boolean(el && (el.getAttribute('aria-selected') === 'true' || el.getAttribute('aria-pressed') === 'true' || /(^|\s)(active|selected)(\s|$)/i.test(el.className || '')));
    return [...document.querySelectorAll('button, [role="tab"], [role="radio"], a')]
      .filter(visible)
      .some(el => /video|clip|phim/i.test(label(el)) && active(el));
  });
  if (videoStillActive) {
    throw Object.assign(Error('Flow vẫn đang ở chế độ Video. Hãy chuyển sang Image/Hình ảnh thủ công hoặc nhập selector "Nút chọn chế độ Image".'), {code: 'IMAGE_MODE'});
  }
  if (!result.clicked && result.videoActive) {
    throw Object.assign(Error('Flow đang ở chế độ Video và không tìm thấy nút Image. Chuyển sang Image thủ công hoặc nhập selector "Nút Image" trong cài đặt Flow.'), {code: 'IMAGE_MODE'});
  }
  return result.clicked;
}

async function imageSources(page, selector) {
  try {
    return await page.evaluate((sel) => [...document.querySelectorAll(sel)].map(img => img.currentSrc || img.src || '').filter(Boolean), selector);
  } catch { return []; }
}

async function waitForNewImage(page, selector, before, timeoutMs) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    await page.waitForTimeout(1200);
    const next = await imageSources(page, selector);
    const fresh = next.find(src => !before.includes(src));
    if (fresh) return fresh;
    if (next.length > before.length) return next.at(-1);
  }
  return '';
}

async function fetchBlob(page, src) {
  if (!src) return null;
  if (src.startsWith('data:')) {
    const base64 = src.split(',')[1] || '';
    return Buffer.from(base64, 'base64');
  }
  if (src.startsWith('blob:')) {
    return page.evaluate(async (url) => {
      const response = await fetch(url);
      const buffer = await response.arrayBuffer();
      return btoa(String.fromCharCode(...new Uint8Array(buffer)));
    }, src).then(base64 => Buffer.from(base64, 'base64')).catch(() => null);
  }
  try { return page.context().request.get(src).then(r => r.ok() ? r.body() : null); } catch { return null; }
}

async function waitForDownload(downloads, beforeCount, timeoutMs) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (downloads.length > beforeCount) return downloads.at(-1);
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  return null;
}

async function saveImage({page, download, base, beforeImages, selector}) {
  let bytes = null;
  if (download) {
    try { bytes = await readFile(await download.path()); } catch { bytes = null; }
    if (!bytes) {
      const temp = path.join(os.tmpdir(), `flow-${Date.now()}-${download.suggestedFilename()}`);
      try {
        await download.saveAs(temp);
        bytes = await readFile(temp);
      } catch { /* ignore */ }
      finally { try { await rm(temp, {force: true}); } catch { /* ignore */ } }
    }
  }
  if (!bytes) {
    const after = await imageSources(page, selector);
    const fresh = after.find(src => !beforeImages.includes(src)) || after.at(-1);
    bytes = await fetchBlob(page, fresh);
  }
  if (!bytes?.length) {
    // Fallback cuối: chụp chính phần tử ảnh mới nhất (chất lượng thấp hơn bản gốc).
    try {
      const locator = page.locator(selector).last();
      if (await locator.count()) bytes = await locator.screenshot({type: 'png'});
    } catch { /* ignore */ }
  }
  if (!bytes?.length) throw Error('Không tải được ảnh Flow (download/ảnh/blob đều thất bại).');
  return writeImage(base, bytes);
}

async function importReference(assets, page, selectors, urls) {
  const files = [];
  for (const url of urls.slice(0, 3)) {
    const file = await readAssetUrl(assets, url);
    if (file) files.push(file);
  }
  if (!files.length) return false;
  try {
    if (selectors.referenceAdd) {
      const add = page.locator(selectors.referenceAdd).first();
      if (await add.count()) await add.click({timeout: 5000}).catch(() => {});
    }
    const input = page.locator(selectors.referenceInput || 'input[type="file"]').first();
    if (!await input.count()) return false;
    await input.setInputFiles(files.slice(0, 3), {timeout: 15000});
    await page.waitForTimeout(800);
    return true;
  } catch { return false; }
}

export async function runFlow({root, projectUrl, queue, downloadDir, profileDir, headless = false, selectors = {}, generateDelayMs = 60000, onProgress = () => {}, assets}) {
  if (!projectUrl) throw Error('Chưa có URL project Google Flow.');
  if (!queue?.items?.length) throw Error('Queue rỗng.');
  await mkdir(downloadDir, {recursive: true});
  await mkdir(profileDir, {recursive: true});
  const manifestFile = path.join(downloadDir, 'manifest.json');
  let manifest = {};
  try { manifest = JSON.parse(await readFile(manifestFile, 'utf8')); } catch { manifest = {}; }
  const exe = chromeExecutable();
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: Boolean(headless),
    executablePath: exe || undefined,
    channel: exe ? undefined : 'chrome',
    acceptDownloads: true,
    downloadsPath: downloadDir,
    viewport: null,
    args: ['--start-maximized'],
  });
  const page = context.pages()[0] || await context.newPage();
  const downloads = [];
  page.on('download', download => downloads.push(download));
  const timeout = Math.max(45000, Number(generateDelayMs) || 60000) + 90000;
  const files = [];
  let done = 0;
  try {
    await page.goto(projectUrl, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForTimeout(2500);
    if (/accounts\.google\.com|\/login/i.test(page.url())) throw Object.assign(Error('Cần đăng nhập Google Flow trong cửa sổ vừa mở, sau đó chạy lại.'), {code: 'NEEDS_LOGIN'});
    const bodyText = (await page.locator('body').innerText().catch(() => '')).toLowerCase();
    if (/captcha|unusual traffic|xác minh bạn là người/i.test(bodyText)) throw Object.assign(Error('Google Flow đang yêu cầu xác minh/captcha. Mở trình duyệt và xử lý thủ công, rồi chạy tiếp.'), {code: 'NEEDS_LOGIN'});
    const promptInput = page.locator(selectors.prompt || 'textarea, div[contenteditable="true"]').first();
    if (!await promptInput.count()) throw Object.assign(Error('Không thấy ô prompt của Flow. Đăng nhập lại hoặc cập nhật selector trong cài đặt.'), {code: 'NEEDS_LOGIN'});
    const imageMode = await ensureImageMode(page, selectors);
    onProgress({done, current: 0, message: imageMode ? 'Đã chọn chế độ Image (chỉ tạo ảnh).' : 'Không thấy nút Image; chỉ tải ảnh, không tạo video.', files});

    for (const item of queue.items) {
      const existing = manifest[item.index];
      if (existing?.name) {
        const candidate = path.join(downloadDir, existing.name);
        try {
          const info = await stat(candidate);
          if (info.size > 0 && existing.promptHash === item.promptHash) {
            let assetUrl = existing.url || '';
            if (assets) {
              try {
                const bytes = await readFile(candidate);
                const asset = await assets.putBuffer(bytes, existing.mime || mimeFromName(existing.name));
                assetUrl = asset.url;
              } catch { /* giữ URL cũ nếu có */ }
            }
            files.push({...existing, index: item.index, url: assetUrl});
            done++;
            onProgress({done, current: item.index, message: `Bỏ qua beat ${item.index} (đã có).`, files});
            continue;
          }
        } catch { /* file mất, tạo lại */ }
      }
      onProgress({done, current: item.index, message: `Beat ${item.index}/${queue.expected}: nhập prompt…`, files});
      await fillPrompt(page, selectors.prompt, item.prompt);
      if (item.references?.length) await importReference(assets, page, selectors, item.references);
      const before = await imageSources(page, selectors.image || 'img');
      let clicked = false;
      if (selectors.generate) {
        const loc = page.locator(selectors.generate).first();
        if (await loc.count()) { await loc.click({timeout: 10000}).catch(() => {}); clicked = true; }
      }
      if (!clicked) clicked = await clickByIcon(page, {icons: ['arrow_upward', 'send', 'auto_awesome'], labels: ['tạo', 'generate', 'create']});
      if (!clicked) await page.keyboard.press('Enter');
      onProgress({done, current: item.index, message: `Beat ${item.index}/${queue.expected}: đang tạo ảnh…`, files});
      await waitForNewImage(page, selectors.image || 'img', before, timeout);
      onProgress({done, current: item.index, message: `Beat ${item.index}/${queue.expected}: tải ảnh…`, files});
      const beforeDownloads = downloads.length;
      const downloadClicked = await clickByIcon(page, {icons: ['download', 'file_download'], labels: ['tải', 'download']});
      const download = downloadClicked ? await waitForDownload(downloads, beforeDownloads, 20000) : null;
      const saved = await saveImage({page, download, base: path.join(downloadDir, `beat-${String(item.index).padStart(3, '0')}`), beforeImages: before, selector: selectors.image || 'img'});
      let assetUrl = '';
      if (assets) {
        const bytes = await readFile(saved.file);
        const asset = await assets.putBuffer(bytes, saved.mime);
        assetUrl = asset.url;
      }
      manifest[item.index] = {index: item.index, name: saved.name, mime: saved.mime, url: assetUrl, promptHash: item.promptHash, savedAt: new Date().toISOString()};
      await writeFile(manifestFile, JSON.stringify(manifest, null, 2), {mode: 0o600});
      files.push(manifest[item.index]);
      done++;
      onProgress({done, current: item.index, message: `Đã lưu beat ${item.index} (${saved.name}).`, files});
    }
    return {files, manifest, downloadDir};
  } finally {
    await context.close().catch(() => {});
  }
}
