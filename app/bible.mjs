// Bible nhân vật/bối cảnh + ghép prompt theo bible.
// Hàm thuần, không I/O, không gọi AI — dùng được ở server và test.
import {createHash} from 'node:crypto';

export const DEFAULT_BIBLE_TEMPLATE = `{style_lock}

Nhân vật (giữ nhất quán): {nhan_vat}
Bối cảnh: {boi_canh}
Hành động: {loi_ke}
Chi tiết: {chi_tiet}

Tránh: {negative}`;

export const DEFAULT_SCENE_RULES = {minSeconds: 2.5, maxSeconds: 8};

const slug = (value) => String(value || '')
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd')
  .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'item';

export const normalizeForMatch = (value) => String(value || '')
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd')
  .toLowerCase().replace(/\s+/g, ' ').trim();

function asList(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function normalizeCharacter(item, index) {
  if (typeof item === 'string') return {id: `char-${index + 1}`, name: item.trim(), role: '', description: item.trim(), refImages: []};
  const name = String(item?.name || item?.id || `Nhân vật ${index + 1}`).trim();
  return {
    id: item?.id ? slug(item.id) : slug(name),
    name,
    role: String(item?.role || '').trim(),
    description: String(item?.description || item?.prompt || '').trim(),
    refImages: asList(item?.refImages || item?.references).map(String).filter(Boolean).slice(0, 3),
  };
}

function normalizeBackground(item, index) {
  if (typeof item === 'string') return {id: `bg-${index + 1}`, name: item.trim(), description: item.trim(), refImages: []};
  const name = String(item?.name || item?.id || `Bối cảnh ${index + 1}`).trim();
  return {
    id: item?.id ? slug(item.id) : slug(name),
    name,
    description: String(item?.description || item?.prompt || '').trim(),
    refImages: asList(item?.refImages || item?.references).map(String).filter(Boolean).slice(0, 3),
  };
}

export function normalizeBible(input = {}) {
  const characters = asList(input.characters).map(normalizeCharacter).filter(c => c.name);
  const backgrounds = asList(input.backgrounds).map(normalizeBackground).filter(b => b.name);
  const main = String(input.main || '').trim();
  const mainCharacter = characters.find(c => normalizeForMatch(c.name) === normalizeForMatch(main)) || characters[0] || null;
  const rules = {...DEFAULT_SCENE_RULES, ...(input.sceneRules || {})};
  const minSeconds = Number(rules.minSeconds);
  const maxSeconds = Number(rules.maxSeconds);
  if (!Number.isFinite(minSeconds) || minSeconds < 0.5) throw Error('sceneRules.minSeconds phải từ 0,5 giây.');
  if (!Number.isFinite(maxSeconds) || maxSeconds <= minSeconds || maxSeconds > 30) throw Error('sceneRules.maxSeconds phải lớn hơn minSeconds và tối đa 30 giây.');
  return {
    id: input.id ? slug(input.id) : (input.name ? slug(input.name) : 'bible'),
    name: String(input.name || 'Bible mới').trim(),
    main: mainCharacter?.name || main,
    styleLock: String(input.styleLock || input.style || '').trim(),
    negative: String(input.negative || '').trim(),
    promptTemplate: String(input.promptTemplate || DEFAULT_BIBLE_TEMPLATE),
    characters,
    backgrounds,
    styleRefImages: asList(input.styleRefImages || input.references).map(String).filter(Boolean).slice(0, 3),
    collections: {
      bibles: String(input.collections?.bibles || 'BIBLES'),
      backgrounds: String(input.collections?.backgrounds || 'BACKGROUNDS'),
      beats: String(input.collections?.beats || 'BEATS'),
    },
    sceneRules: {minSeconds, maxSeconds},
    source: input.source ? String(input.source) : '',
  };
}

// Import roster dạng Video-scripts/bibles/*-roster.json.
export function importRoster(roster, {name = 'Bible import', source = ''} = {}) {
  if (!roster || typeof roster !== 'object') throw Error('Roster không hợp lệ.');
  return normalizeBible({
    name: roster.name || name,
    main: roster.main,
    characters: roster.characters,
    backgrounds: roster.backgrounds,
    styleLock: roster.styleLock || roster.style || '',
    negative: roster.negative || '',
    promptTemplate: roster.promptTemplate,
    styleRefImages: roster.styleRefImages || roster.references,
    collections: roster.collections,
    sceneRules: roster.sceneRules,
    source,
  });
}

// Tách câu đơn giản, giữ dấu câu; dùng cho script builder và chia cảnh.
export function sentences(text) {
  return String(text || '')
    .replace(/\r\n?/g, '\n')
    .split(/(?<=[.?!…:。？！])\s+|\n+/u)
    .map(s => s.trim())
    .filter(Boolean);
}

export function matchCharacters(bible, narration) {
  const haystack = ` ${normalizeForMatch(narration)} `;
  const list = bible?.characters || [];
  // Ưu tiên khớp tên đầy đủ để tránh vai trò chung ("người dẫn chuyện") khớp nhầm.
  const byName = list.filter(character => {
    const name = normalizeForMatch(character.name);
    return name && (haystack.includes(` ${name} `) || haystack.includes(name));
  });
  if (byName.length) return byName.slice(0, 2);
  const byRole = list.filter(character => {
    const role = normalizeForMatch(character.role);
    return role.length >= 6 && haystack.includes(role);
  });
  if (byRole.length) return byRole.slice(0, 2);
  if (bible?.main) {
    const main = list.find(c => normalizeForMatch(c.name) === normalizeForMatch(bible.main));
    if (main) return [main];
  }
  return [];
}

export function matchBackground(bible, narration) {
  const haystack = ` ${normalizeForMatch(narration)} `;
  const list = bible?.backgrounds || [];
  const byName = list.find(bg => {
    const name = normalizeForMatch(bg.name);
    return name && (haystack.includes(` ${name} `) || haystack.includes(name));
  });
  if (byName) return byName;
  // Fallback: từ khoá riêng trong tên, bỏ từ quá ngắn/trùng nghĩa.
  const stop = new Set(['cong', 'thanh', 'nha', 'cua', 'khu', 'vung', 'ben', 'tren', 'duoi']);
  return list.find(bg => normalizeForMatch(bg.name).split(/\s+/).some(word => word.length >= 4 && !stop.has(word) && haystack.includes(word))) || null;
}

export function uniqueRefs(values) {
  const seen = new Set();
  const out = [];
  for (const value of values.flat()) {
    const text = String(value || '').trim();
    if (!text || seen.has(text)) continue;
    seen.add(text);
    out.push(text);
  }
  return out;
}

export function referencesFor(bible, scene, {max = 3} = {}) {
  const matched = (scene?.characters?.length ? scene.characters : matchCharacters(bible, scene?.narration))
    .map(name => (bible.characters || []).find(c => normalizeForMatch(c.name) === normalizeForMatch(name)) || {refImages: []});
  const background = (bible.backgrounds || []).find(bg => normalizeForMatch(bg.name) === normalizeForMatch(scene?.background))
    || matchBackground(bible, scene?.narration);
  return uniqueRefs([
    matched.flatMap(c => c.refImages || []),
    background?.refImages || [],
    bible.styleRefImages || [],
  ]).slice(0, max);
}

function render(template, values) {
  return String(template || '').replace(/\{([\p{L}\w]+)\}/gu, (_, key) => {
    if (!Object.hasOwn(values, key)) throw Error(`Không hỗ trợ biến {${key}} trong mẫu prompt bible.`);
    return String(values[key] ?? '');
  });
}

// Xoá dòng nhãn rỗng kiểu "Bối cảnh:" và gộp dòng trống.
export function tidyPrompt(text) {
  return String(text || '')
    .split('\n')
    .filter(line => !/^[^:\n]{1,60}:\s*$/.test(line))
    .join('\n')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export function buildScenePrompt({bible, scene, project = {}}) {
  const normalized = normalizeBible(bible || {});
  const matched = scene?.characters?.length
    ? scene.characters.map(name => (normalized.characters || []).find(c => normalizeForMatch(c.name) === normalizeForMatch(name))).filter(Boolean)
    : matchCharacters(normalized, scene?.narration);
  const background = (normalized.backgrounds || []).find(bg => normalizeForMatch(bg.name) === normalizeForMatch(scene?.background))
    || matchBackground(normalized, scene?.narration);
  const values = {
    loi_ke: String(scene?.narration || '').trim(),
    nhan_vat: matched.map(c => c.description || c.name).join(' | ') || project.character || '',
    boi_canh: background?.description || background?.name || '',
    style_lock: normalized.styleLock || project.style || '',
    negative: normalized.negative || '',
    chi_tiet: String(scene?.support || '').trim() || 'Chỉ giữ chi tiết có trong lời kể, không thêm người hoặc vật thể không có trong kịch bản',
    phong_cach: normalized.styleLock || project.style || '',
    so_canh: Number(scene?.index || 0),
    bat_dau: Number(scene?.start || 0).toFixed(1),
    ket_thuc: Number(scene?.end || 0).toFixed(1),
    thoi_luong: Number(Number(scene?.duration || 0).toFixed(2)),
    chu_the: String(scene?.subject || '').trim() || String(scene?.narration || '').trim(),
    quy_tac_nhan: String(scene?.label || '').trim() ? `Chỉ một nhãn ngắn: "${String(scene.label).trim()}". Không có chữ khác.` : 'Không chèn chữ, nhãn hoặc watermark.',
  };
  const template = normalized.promptTemplate;
  if (!template.includes('{loi_ke}')) throw Error('Mẫu prompt bible cần có {loi_ke}.');
  return tidyPrompt(render(template, values));
}

export function promptHash(prompt) {
  return createHash('sha256').update(String(prompt || '')).digest('hex');
}

export function bibleSummary(bible) {
  const normalized = normalizeBible(bible || {});
  return {
    name: normalized.name,
    main: normalized.main,
    characters: normalized.characters.length,
    backgrounds: normalized.backgrounds.length,
    styleLock: Boolean(normalized.styleLock),
    negative: Boolean(normalized.negative),
  };
}
