import fs from 'node:fs';
import path from 'node:path';
import { scenesA } from './scenes-a.mjs';
import { scenesB } from './scenes-b.mjs';
import { scenesC } from './scenes-c.mjs';

const scenes = { ...scenesA, ...scenesB, ...scenesC };

const STYLE = '2D cartoon historical documentary illustration, stylized big-head proportions, thick dark outlines, flat colors with two-tone shading, minimal detail, warm earthy palette of sand, ochre, brick red, lapis blue and olive, clean readable silhouette, 16:9, no text, no watermark.';

const CHARS = {
  T: 'Tích, a Vietnamese boy around ten, round face, big dark eyes, short messy black hair, yellow hoodie, dark blue jeans, white sneakers, small brown backpack, three heads tall.',
  N: 'Nông Dân, a Sumerian farmer, adult man, three and a half heads tall, tan skin, thick black beard, black hair under a cream headband, plain cream tunic, bare feet, strong arms.',
  S: 'Thư Lại, a Sumerian scribe, young adult, three and a half heads tall, tan skin, black hair in a topknot, cream tunic with blue trim, blue sash, bare feet, a clay tablet in one hand.',
  V: 'Vua Sumer, a Sumerian king, adult man, three and a half heads tall, tan skin, thick black beard, tall blue and gold crown, blue robe with gold trim, gold armbands, white pleated skirt, bull-head staff.',
  E: 'Sumerian townspeople in plain cream and brown tunics, bare feet, varied ages and hairstyles.',
  P: 'A Sumerian priest, shaved head, small horned cap, white linen robe, lapis bead necklace.',
  X: 'Sumerian soldiers, copper helmets, woven shields, spears, leather tunics.',
  G: 'Gilgamesh, a young Uruk king, tall and muscular, black curly hair, short beard, gold headband, lion-skin cloak, bare chest, fleece kilt.',
  K: 'Enkidu, a wild man, tall, long tangled black hair, thick beard, animal skin, bare feet.',
  U: 'Utnapishtim, an old man, long white beard, plain undyed robe, deep-set eyes, no crown.',
  H: 'Humbaba, a giant guardian with a lion face, coiled beard and brows, massive body, forest-green skin.',
  B: 'The Bull of Heaven, a huge black bull with golden horns, red eyes, a copper collar.',
  F: 'The wife of Utnapishtim, a middle-aged woman, hair in a bun, plain undyed robe.',
  R: 'Henry Rawlinson, a 19th-century British officer, red coat, dark cap, sideburns.'
};

const SARGON = 'Sargon, a Sumerian king, adult man, three and a half heads tall, tan skin, short black beard, copper crown, blue robe with copper trim, gold armbands, white pleated skirt, bull-head staff.';
const UR_NAMMU = 'Ur-Nammu, a Sumerian king, adult man, three and a half heads tall, tan skin, thick black beard, horned copper crown, blue robe with gold trim, gold armbands, white pleated skirt, bull-head staff.';

const charOverrides = {
  134: { V: UR_NAMMU },
  161: { V: SARGON },
  164: { V: SARGON },
  168: { V: SARGON }
};

// Object-focused beats: the character is present only as a hand or a symbol.
const dropChar = new Set([166, 172, 221, 231, 239]);

const framing = {
  4: "Extreme close-up, only the scribe's hand and forearm are visible, the stylus and tablet filling the frame.",
  52: "Close-up, the worker's face and pointing hand, the silt behind.",
  94: "Close-up, the sick child and the mother's hands, flies in the foreground.",
  107: "Extreme close-up, only the scribe's hand, the stylus, and the clay envelope are visible.",
  120: "Close-up, the child's face and the creditor's hand on the tablet, the tablet between them.",
  132: "Close-up, only the king's hand, the scribe's hand, the tablet, and the cylinder seal are visible.",
  147: "Close-up, only the king's hand and forearm are visible, his shadow huge on the wall.",
  171: "Extreme close-up, only the scribe's hand and the tablet are visible.",
  178: "Close-up, only Gilgamesh's hand and forearm are visible, gripping the wall.",
  188: "Close-up, only the woman's hand, sleeve, and bangle are visible.",
  193: "Close-up, only the king's hand and forearm are visible against the wall, the boatman soft in the background.",
  221: "Close-up of the burning wall and falling embers, no characters, the city soft in the background.",
  236: "Close-up, only the boy's wrist and the watch are visible.",
  249: "Extreme close-up, only the boy's wrist, the watch, and a little dust are visible."
};

const SETS = {
  gate: 'a mudbrick city gate, two gate towers, dark archway, dust haze, date palms',
  zig: 'stepped mudbrick ziggurat with a long ramp, sun-baked plaza, date palms',
  canal: 'straight irrigation canal, wet clay banks, reeds, date palms, thin morning mist',
  tablet: 'scribal school interior, clay tablets stacked on low benches, oil lamp, mudbrick walls',
  dock: 'muddy river dock, reed boats, cargo baskets, low wooden walkway, palm grove',
  salt: 'cracked salt-crusted field, dead palms, empty dry canal, pale sky',
  plain: 'an empty flat floodplain, cracked mud, dry reeds, no trees, no stones, pale horizon',
  field: 'a barley field with low mud banks, dry stalks, a flat horizon',
  marsh: 'a marsh of tall reeds, still brown water, mudbanks, haze',
  market: 'a mudbrick market street, reed awnings, baskets of grain, pottery, no coins',
  temple: 'a mudbrick temple complex, gate, storerooms, small inner shrine, grain jars, oil lamps',
  throne: 'a mudbrick throne room, a low dais, woven hangings, oil lamps',
  wall: 'a mudbrick city wall with battlements, gate towers, dusty ground',
  ruins: 'a low archaeological tell, broken mudbrick walls, dust, a dry plain',
  modern: 'a dark wooden desk by a window, a mechanical clock, papers, a clay tablet, cool daylight',
  study: 'a 19th-century study with a wooden desk, oil lamp, books, papers, and a clay tablet, dust in the air',
  myth: 'a mythic space of deep blue night, golden light, long shadows, symbolic ground, no real architecture',
  abstract: 'a flat clay-colored graphic background with cuneiform marks and arrows, no characters',
  rivers: 'two broad muddy rivers, low reed banks, flat horizon, pale sky',
  storehouse: 'a mudbrick grain store, sealed jars, sacks of barley, a low wooden counter, dust',
  street: 'a narrow mudbrick street between low houses, dust, worn thresholds, no market stalls',
  house: 'a poor mudbrick house interior, a straw mat, a clay bowl, dim warm light',
  cliff: 'a high rock cliff with carved reliefs and three columns of cuneiform, a narrow ledge, open sky',
  construction: 'a half-built mudbrick wall, fresh bricks, straw, mud mortar, dusty ground',
  courtyard: 'a mudbrick courtyard with a low wall, a canal channel under construction, stacked fire bricks, a school bench, dusty ground'
};

const settingOverrides = {
  3: 'rivers',
  10: 'rivers',
  73: 'storehouse',
  93: 'street',
  94: 'house',
  218: 'street',
  222: 'street',
  232: 'cliff',
  244: 'construction',
  245: 'courtyard'
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cur = '';
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    if (quoted) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          cur += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        cur += c;
      }
    } else if (c === '"') {
      quoted = true;
    } else if (c === ',') {
      row.push(cur);
      cur = '';
    } else if (c === '\n') {
      row.push(cur);
      rows.push(row);
      row = [];
      cur = '';
    } else if (c !== '\r') {
      cur += c;
    }
  }
  if (cur.length || row.length) {
    row.push(cur);
    rows.push(row);
  }
  return rows.filter(r => r.some(v => String(v).trim() !== ''));
}

function q(value) {
  const s = String(value ?? '');
  return `"${s.replace(/"/g, '""')}"`;
}

function lighting(beat, set) {
  if (set === 'modern') return 'cool daylight from a window, soft shadows';
  if (set === 'myth') return 'deep blue night, golden firelight, long shadows';
  if (set === 'salt') return 'pale overcast light, low saturation, white ground';
  if (set === 'abstract') return 'flat even light, no shadows';
  if (set === 'study') return 'warm oil-lamp light, deep brown shadows';
  if (set === 'house') return 'warm dim interior light, deep shadows';
  if (set === 'cliff') return 'late afternoon sun, long shadows, open sky';
  if (beat === 216 || beat === 221 || beat === 228) return 'firelight and smoke, dark orange glow, ash in the air';
  if (beat === 227 || beat === 229) return 'firelight and ash, warm orange against cold ruins';
  if (beat === 111) return 'bright daylight, warm dust';
  if (set === 'tablet' && beat >= 225) return 'soft daylight, dust motes, low contrast';
  if (set === 'tablet') return 'warm oil-lamp light, deep brown shadows';
  if (set === 'zig' || set === 'throne') return 'low sun from the west, long shadows to the east, amber light';
  if (beat <= 41) return 'high noon, short shadows, bleached sand, high contrast';
  if (beat <= 68) return 'thin morning mist, soft warm light';
  if (beat <= 103) return 'golden hour, long shadows';
  if (beat <= 139) return 'warm late afternoon, long shadows, dust in the air';
  if (beat <= 173) return 'golden hour, long shadows';
  if (beat >= 179 && beat <= 201) return 'deep blue night, golden firelight, long shadows';
  if (beat >= 174 && beat <= 178) return 'late afternoon sun, long shadows, dusty air';
  if (beat <= 224) return 'pale overcast light, low saturation';
  return 'golden hour over the ruins, long shadows';
}

function camera(cam, hasChar) {
  if (cam === 'wide') return 'Wide establishing shot.';
  if (cam === 'medium') return hasChar ? 'Medium shot, waist up.' : 'Medium shot of the scene.';
  if (cam === 'close') return hasChar ? 'Close-up, head and shoulders.' : 'Close-up of the object.';
  if (cam === 'insert') return hasChar ? 'Extreme close-up insert, only the hand and object are visible.' : 'Extreme close-up insert, only the object is visible.';
  if (cam === 'top') return 'Top-down view.';
  if (cam === 'low') return 'Low-angle shot.';
  if (cam === 'pan') return 'Wide panoramic shot.';
  return 'Wide shot.';
}

function composition(set, cam) {
  if (set === 'abstract') return 'Flat graphic composition, clear arrows, no characters.';
  if (cam === 'insert' || cam === 'close') return 'Clean readable silhouette, low-contrast background, clean lower third for subtitles.';
  return 'Three depth layers, clear silhouette, low-contrast background, clean lower third for subtitles.';
}

const csvPath = path.join(process.env.USERPROFILE, 'OneDrive - VNTT', 'Desktop', 'Summer', 'sumer-beats.csv');
const raw = fs.readFileSync(csvPath, 'utf8').replace(/^\uFEFF/, '');
const [header, ...data] = parseCsv(raw);
const beats = data.map(row => Object.fromEntries(header.map((h, i) => [h, row[i] ?? ''])));

const prompts = [];
const manifest = [];
const missing = [];

for (let n = 1; n <= 253; n += 1) {
  if (!scenes[n]) missing.push(n);
}
if (missing.length) throw new Error(`Missing scenes: ${missing.join(', ')}`);

for (const row of beats) {
  const beat = Number(row.beat);
  const scene = scenes[beat];
  if (!scene) throw new Error(`No scene for beat ${beat}`);
  const rawChar = String(row.char || '').trim();
  const codes = (!dropChar.has(beat) && rawChar && rawChar !== '-')
    ? rawChar.split('+').map(s => s.trim()).filter(Boolean)
    : [];
  const blocks = codes.map(code => {
    const block = charOverrides[beat]?.[code] || CHARS[code];
    if (!block) throw new Error(`Unknown character code "${code}" at beat ${beat}`);
    return block;
  });
  const hasChar = blocks.length > 0;
  const charText = blocks.join(' ');
  const rawSet = String(row.set || '').trim();
  const set = settingOverrides[beat] || rawSet;
  const setting = SETS[set];
  if (!setting) throw new Error(`Unknown set "${set}" at beat ${beat}`);
  const cam = String(row.camera || '').trim();
  const frame = framing[beat] || camera(cam, hasChar);
  const light = lighting(beat, set);
  const comp = composition(set, cam);
  const cuneiform = /tablet|cuneiform|wedge|ledger|clay document/i.test(scene) || set === 'tablet' || set === 'abstract'
    ? ' Cuneiform wedge marks are decorative texture, not readable modern text.'
    : '';
  const prompt = `${STYLE} ${charText}${charText ? ' ' : ''}${scene} Setting: ${setting}. Lighting: ${light}. ${frame} ${comp}${cuneiform} 16:9. No readable modern text, no watermark, no photorealistic rendering, no 3D render, no anime, no extra fingers, no deformed hands, no duplicate characters.`
    .replace(/\s+/g, ' ')
    .trim();
  prompts.push(prompt);
  manifest.push({
    prompt_no: prompts.length,
    beat,
    start_tc: row.start_tc,
    duration_s: row.duration_s,
    char: rawChar || '-',
    set,
    camera: cam,
    words: prompt.split(/\s+/).length,
    scene_start: scene.slice(0, 90)
  });
}

if (prompts.length !== 253) throw new Error(`Expected 253 prompts, got ${prompts.length}`);
if (beats.length !== 253) throw new Error(`Expected 253 beats, got ${beats.length}`);

const outDir = path.join(process.env.TEMP, 'opencode', 'prompts-out');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'sumer-image-prompts.txt'), prompts.join('\n\n') + '\n', 'utf8');

const manifestHeader = ['prompt_no', 'beat', 'start_tc', 'duration_s', 'char', 'set', 'camera', 'words', 'scene_start'];
const manifestLines = [manifestHeader.join(',')];
for (const m of manifest) {
  manifestLines.push(manifestHeader.map(k => q(m[k])).join(','));
}
fs.writeFileSync(path.join(outDir, 'sumer-image-prompts.csv'), manifestLines.join('\n') + '\n', 'utf8');

const totalWords = prompts.reduce((sum, p) => sum + p.split(/\s+/).length, 0);
console.log(`prompts: ${prompts.length}`);
console.log(`beats: ${beats.length}`);
console.log(`total prompt words: ${totalWords}`);
console.log(`average prompt words: ${(totalWords / prompts.length).toFixed(1)}`);
console.log(`first: ${prompts[0].slice(0, 220)}...`);
console.log(`last: ${prompts[prompts.length - 1].slice(0, 220)}...`);
console.log(`unique chars: ${[...new Set(manifest.map(m => m.char))].join(' | ')}`);
console.log(`unique sets: ${[...new Set(manifest.map(m => m.set))].join(' | ')}`);
