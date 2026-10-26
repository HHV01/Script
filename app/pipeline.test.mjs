import test from 'node:test';
import assert from 'node:assert/strict';
import {importRoster, normalizeBible, buildScenePrompt, matchCharacters, promptHash, tidyPrompt} from './bible.mjs';
import {parseScriptResponse, normalizeNarration, scriptToTxt, buildScriptMessages, estimateWords} from './script-builder.mjs';
import {chunkText} from './providers.mjs';
import {groupSentences, splitScenesFromVoice} from './split.mjs';
import {buildQueue, queueToPromptBlocks, verifyImages, parseBeatIndex, applyImagesToScenes} from './flow.mjs';

const roster = {
  main: 'Tích',
  characters: [
    {name: 'Tích', role: 'Người dẫn chuyện', description: 'Tích, a Vietnamese boy, yellow hoodie.'},
    {name: 'Nông Dân', role: 'Nông dân Sumer', description: 'Nông Dân, a Sumerian farmer, cream tunic.'},
  ],
  backgrounds: [
    {name: 'Cổng thành Uruk', description: 'mudbrick city gate of Uruk, date palms'},
    {name: 'Nhà bảng', description: 'scribal school interior, clay tablets'},
  ],
};

const bible = importRoster(roster, {name: 'Sumer test', source: 'test.json'});

function sampleProject() {
  return {
    id: 'p1', name: 'Sumer', title: 'Sumer', bible,
    scenes: [
      {index: 1, narration: 'Tích đi qua cổng thành Uruk.', duration: 3},
      {index: 2, narration: 'Nông Dân đang gặt lúa.', duration: 3},
      {index: 3, narration: 'Cả hai bước vào nhà bảng.', duration: 4},
    ],
  };
}

test('importRoster tao bible chuan va giu nhan vat/boi canh', () => {
  assert.equal(bible.main, 'Tích');
  assert.equal(bible.characters.length, 2);
  assert.equal(bible.backgrounds.length, 2);
  assert.equal(bible.sceneRules.maxSeconds, 8);
  assert.match(bible.promptTemplate, /\{loi_ke\}/);
});

test('buildScenePrompt ghep dung nhan vat, boi canh, style va negative', () => {
  const custom = normalizeBible({
    ...bible,
    styleLock: 'flat cartoon, 16:9',
    negative: 'no text, no watermark',
  });
  const prompt = buildScenePrompt({bible: custom, scene: {index: 2, narration: 'Tích đi qua cổng thành Uruk.', duration: 3, start: 3, end: 6}});
  assert.match(prompt, /flat cartoon, 16:9/);
  assert.match(prompt, /Tích, a Vietnamese boy/);
  assert.match(prompt, /mudbrick city gate of Uruk/);
  assert.match(prompt, /Tích đi qua cổng thành Uruk/);
  assert.match(prompt, /no text, no watermark/);
  assert.equal(prompt.trim(), prompt);
  assert.equal(promptHash(prompt), promptHash(buildScenePrompt({bible: custom, scene: {index: 2, narration: 'Tích đi qua cổng thành Uruk.', duration: 3, start: 3, end: 6}})));
});

test('buildScenePrompt bao loi khi template thieu {loi_ke} hoac co bien la', () => {
  assert.throws(() => buildScenePrompt({bible: {...bible, promptTemplate: 'Chỉ style'}, scene: {narration: 'x'}}), /loi_ke/);
  assert.throws(() => buildScenePrompt({bible: {...bible, promptTemplate: '{loi_ke} {khong_co}'}, scene: {narration: 'x'}}), /khong_co/);
});

test('matchCharacters khong phu thuoc dau tieng Viet', () => {
  const found = matchCharacters(bible, 'tich di qua cong thanh uruk');
  assert.equal(found[0].name, 'Tích');
  const found2 = matchCharacters(bible, 'NGUOI NONG DAN');
  assert.equal(found2[0].name, 'Nông Dân');
});

test('tidyPrompt xoa dong nhan rong', () => {
  assert.equal(tidyPrompt('A\n\nBối cảnh:\n\nB'), 'A\n\nB');
});

test('parseScriptResponse doc JSON, fenced JSON va text thuong', () => {
  assert.deepEqual(parseScriptResponse('{"title":"Sumer","narration":"Một ngày ở Sumer."}').narration, 'Một ngày ở Sumer.');
  assert.equal(parseScriptResponse('```json\n{"title":"A","narration":"B"}\n```').title, 'A');
  const plain = parseScriptResponse('Mở đầu\n\nĐây là lời đọc.');
  assert.match(plain.narration, /Đây là lời đọc/);
  assert.equal(plain.warnings.length, 1);
});

test('normalizeNarration bo markdown va nhan cam', () => {
  const text = normalizeNarration('## Mở đầu\n**Đây** là *lời* đọc.\n\n- Ý một\n- Ý hai');
  assert.equal(text.includes('#'), false);
  assert.equal(text.includes('**'), false);
  assert.match(text, /Đây là lời đọc/);
});

test('scriptToTxt chi xuat loi doc', () => {
  assert.equal(scriptToTxt({narration: '  Một ngày.  '}), 'Một ngày.\n');
  assert.throws(() => scriptToTxt({narration: ''}), /Chưa có kịch bản/);
});

test('buildScriptMessages co du thong tin bible va do dai', () => {
  const messages = buildScriptMessages({bible, brief: 'Một ngày ở Sumer', targetMinutes: 10});
  assert.equal(messages.length, 2);
  assert.match(messages[0].content, /JSON/);
  assert.match(messages[1].content, /Một ngày ở Sumer/);
  assert.match(messages[1].content, /Tích/);
  assert.equal(estimateWords(10), 1400);
});

test('chunkText chia theo cau va gioi han ky tu', () => {
  const text = Array.from({length: 20}, (_, i) => `Đây là câu số ${i}.`).join(' ');
  const chunks = chunkText(text, 60);
  assert.ok(chunks.length > 1);
  assert.ok(chunks.every(c => c.length <= 60));
  assert.equal(chunks.join(' ').replace(/\s+/g, ' '), text.replace(/\s+/g, ' '));
});

test('groupSentences gom cau theo thoi luong voice', () => {
  const groups = groupSentences('Câu một. Câu hai. Câu ba. Câu bốn.', {duration: 12, maxSeconds: 8, minSeconds: 2.5});
  assert.ok(groups.length >= 2);
  assert.equal(groups.map(g => g.narration).join(' ').replace(/\s+/g, ' '), 'Câu một. Câu hai. Câu ba. Câu bốn.');
  assert.ok(groups.every(g => g.estimatedSeconds <= 10.1));
});

test('splitScenesFromVoice fallback theo so tu van giu tong thoi luong', () => {
  const result = splitScenesFromVoice({narration: 'Câu một. Câu hai. Câu ba. Câu bốn.', duration: 12, maxSeconds: 8, minSeconds: 2.5});
  assert.equal(result.timingSource, 'words');
  assert.ok(result.scenes.length >= 2);
  const sum = result.scenes.reduce((n, s) => n + s.duration, 0);
  assert.ok(Math.abs(sum - 12) < 0.05, `sum=${sum}`);
  assert.equal(result.scenes.at(-1).end, 12);
});

test('buildQueue tao prompt + hash + output dung thu tu', () => {
  const queue = buildQueue({project: sampleProject()});
  assert.equal(queue.expected, 3);
  assert.equal(queue.items[0].output, 'beat-001.png');
  assert.equal(queue.items[1].index, 2);
  assert.match(queue.items[0].prompt, /Tích/);
  assert.match(queue.items[2].prompt, /nhà bảng/);
  assert.equal(queue.items[0].promptHash.length, 64);
  const blocks = queueToPromptBlocks(queue);
  assert.equal(blocks.trim().split(/\n\n/).length, 3);
});

test('parseBeatIndex doc nhieu kieu ten', () => {
  assert.equal(parseBeatIndex('beat-001.png'), 1);
  assert.equal(parseBeatIndex('beat_12.jpg'), 12);
  assert.equal(parseBeatIndex('scene-3.webp'), 3);
  assert.equal(parseBeatIndex('7.png'), 7);
  assert.equal(parseBeatIndex('random.png'), null);
});

test('verifyImages dat khi du so, dung ti le va hash', () => {
  const project = sampleProject();
  const queue = buildQueue({project});
  const files = queue.items.map(item => ({name: item.output, url: `/api/assets/${'a'.repeat(64)}.png`, width: 1920, height: 1080, promptHash: item.promptHash}));
  const result = verifyImages({queue, files});
  assert.equal(result.ok, true);
  assert.equal(result.summary.ok, 3);
  const next = applyImagesToScenes(project, result);
  assert.equal(next.scenes.every(s => s.image?.startsWith('/api/assets/')), true);
});

test('verifyImages bat thieu, trung, sai ti le, hash cu va file thua', () => {
  const project = sampleProject();
  const queue = buildQueue({project});
  const files = queue.items.slice(0, 2).map(item => ({name: item.output, url: `/api/assets/${'b'.repeat(64)}.png`, width: 1920, height: 1080, promptHash: item.promptHash}));
  let result = verifyImages({queue, files});
  assert.equal(result.ok, false);
  assert.deepEqual(result.missing, [3]);

  result = verifyImages({queue, files: [...files, {...files[0]}, {...files[1], name: 'beat-003.png', width: 1000, height: 1000, promptHash: queue.items[2].promptHash}, {name: 'beat-099.png', width: 1920, height: 1080}]});
  assert.equal(result.ok, false);
  assert.equal(result.duplicates.length, 1);
  assert.equal(result.extra.length, 1);
  assert.equal(result.invalid.length, 1);
  assert.match(result.invalid[0].reasons.join(' '), /16:9|Độ phân giải/);

  const badHash = queue.items.map((item, i) => ({name: item.output, url: files[i % files.length].url, width: 1920, height: 1080, promptHash: 'x'.repeat(64)}));
  result = verifyImages({queue, files: badHash});
  assert.equal(result.ok, false);
  assert.equal(result.invalid.length, 3);
  assert.match(result.invalid[0].reasons.join(' '), /Prompt hash/);
});
