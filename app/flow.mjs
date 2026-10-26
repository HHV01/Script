// Queue prompt cho Google Flow + kiểm chứng ảnh tải về trước khi cho ghép video.
import {buildScenePrompt, referencesFor, promptHash} from './bible.mjs';

const pad = (n) => String(n).padStart(3, '0');
const IMAGE_EXT = /\.(png|jpe?g|webp)$/i;

export function outputName(index) { return `beat-${pad(index)}.png`; }

export function parseBeatIndex(name) {
  const base = String(name || '').split(/[\\/]/).pop();
  const match = base.match(/(?:beat|scene|canh)[-_ ]?(\d{1,4})/i) || base.match(/^(\d{1,4})\.(?:png|jpe?g|webp)$/i);
  return match ? Number(match[1]) : null;
}

export function buildQueue({project, bible = project?.bible, maxReferences = 3} = {}) {
  if (!Array.isArray(project?.scenes) || !project.scenes.length) throw Error('Chưa có phân cảnh để tạo queue.');
  const items = project.scenes.map((scene, i) => {
    const index = Number(scene.index) || i + 1;
    const prompt = buildScenePrompt({bible, scene: {...scene, index}, project});
    if (!prompt) throw Error(`Cảnh ${index} không tạo được prompt.`);
    return {
      index,
      output: outputName(index),
      prompt,
      promptHash: promptHash(prompt),
      narration: String(scene.narration || '').trim(),
      characters: (scene.characters || []).map(String),
      background: String(scene.background || ''),
      references: bible ? referencesFor(bible, scene, {max: maxReferences}) : (scene.references || []).slice(0, maxReferences),
      duration: Number(scene.duration || 0),
    };
  });
  return {
    version: 1,
    createdAt: new Date().toISOString(),
    projectId: String(project.id || ''),
    projectName: String(project.name || ''),
    expected: items.length,
    items,
  };
}

export function queueToPromptBlocks(queue) {
  return queue.items.map(item => item.prompt.trim()).join('\n\n') + '\n';
}

export function csvCell(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function queueToCsv(queue) {
  const rows = [['index', 'output', 'duration', 'characters', 'background', 'prompt', 'narration', 'promptHash']];
  for (const item of queue.items) rows.push([item.index, item.output, item.duration, item.characters.join(' | '), item.background, item.prompt, item.narration, item.promptHash]);
  return rows.map(row => row.map(csvCell).join(',')).join('\n') + '\n';
}

export function verifyImages({queue, files = [], minWidth = 1280, minHeight = 720, aspect = 16 / 9, aspectTolerance = 0.02} = {}) {
  if (!queue?.items?.length) throw Error('Queue rỗng, không có gì để kiểm tra.');
  const expected = queue.expected || queue.items.length;
  const byIndex = new Map();
  const duplicates = [];
  const unknown = [];
  for (const file of files) {
    const index = Number(file.index) || parseBeatIndex(file.name);
    if (!index) { unknown.push({name: file.name, reason: 'Không đọc được số beat từ tên file.'}); continue; }
    const list = byIndex.get(index) || [];
    list.push(file);
    byIndex.set(index, list);
  }
  for (const [index, list] of byIndex) if (list.length > 1) duplicates.push({index, files: list.map(f => f.name)});
  const items = queue.items.map(item => {
    const list = byIndex.get(item.index) || [];
    const file = list[0];
    if (!file) return {index: item.index, output: item.output, status: 'missing', promptHash: item.promptHash};
    const width = Number(file.width || 0), height = Number(file.height || 0);
    const reasons = [];
    if (!IMAGE_EXT.test(file.name || '')) reasons.push('Không phải PNG/JPEG/WebP.');
    if (width && height) {
      if (width < minWidth || height < minHeight) reasons.push(`Độ phân giải ${width}×${height} nhỏ hơn ${minWidth}×${minHeight}.`);
      const ratio = width / height;
      if (Math.abs(ratio - aspect) > aspectTolerance) reasons.push(`Tỉ lệ ${ratio.toFixed(3)} không phải 16:9.`);
    } else reasons.push('Không đọc được kích thước ảnh.');
    if (file.promptHash && file.promptHash !== item.promptHash) reasons.push('Prompt hash không khớp (ảnh của prompt cũ).');
    return {
      index: item.index,
      output: item.output,
      status: reasons.length ? 'invalid' : 'ok',
      reasons,
      name: file.name,
      url: file.url || '',
      width, height,
      promptHash: item.promptHash,
    };
  });
  const missing = items.filter(i => i.status === 'missing').map(i => i.index);
  const invalid = items.filter(i => i.status === 'invalid').map(i => ({index: i.index, reasons: i.reasons}));
  const extra = [...byIndex.keys()].filter(index => !queue.items.some(item => item.index === index)).map(index => ({index, files: byIndex.get(index).map(f => f.name)}));
  const ok = missing.length === 0 && invalid.length === 0 && duplicates.length === 0 && unknown.length === 0 && extra.length === 0 && files.length === expected;
  return {
    ok,
    expected,
    received: files.length,
    summary: {ok: items.filter(i => i.status === 'ok').length, missing: missing.length, invalid: invalid.length, duplicates: duplicates.length, extra: extra.length, unknown: unknown.length},
    missing,
    invalid,
    duplicates,
    extra,
    unknown,
    items,
  };
}

export function applyImagesToScenes(project, verification) {
  const map = new Map((verification?.items || []).filter(i => i.status === 'ok' && i.url).map(i => [i.index, i]));
  const scenes = (project.scenes || []).map((scene, i) => {
    const index = Number(scene.index) || i + 1;
    const image = map.get(index);
    return image ? {...scene, image: image.url, imageWidth: image.width, imageHeight: image.height, imageSource: 'flow'} : scene;
  });
  return {...project, scenes};
}
