// Sinh kịch bản bằng AI (OpenAI-compatible) + chuẩn hoá thành TXT sạch cho TTS.
// Phần gọi mạng nằm ở providers.mjs; file này thuần và test được offline.
import {sentences} from './bible.mjs';

export function estimateWords(minutes, wpm = 140) {
  const value = Number(minutes);
  if (!Number.isFinite(value) || value <= 0) throw Error('Thời lượng kịch bản phải lớn hơn 0 phút.');
  return Math.round(value * Number(wpm || 140));
}

export function buildScriptMessages({bible, brief, targetMinutes = 10, tone = 'kể chuyện lịch sử', audience = 'người xem phổ thông', wpm = 140, outline = ''} = {}) {
  const words = estimateWords(targetMinutes, wpm);
  const characters = (bible?.characters || []).map(c => `- ${c.name}${c.role ? ` (${c.role})` : ''}: ${c.description || ''}`).join('\n') || '- Không có bible nhân vật; chỉ dùng nhân vật/vật thể xuất hiện trong brief.';
  const backgrounds = (bible?.backgrounds || []).map(b => `- ${b.name}: ${b.description || ''}`).join('\n') || '- Không có.';
  const system = [
    'Bạn là biên tập viên kịch bản video documentary tiếng Việt.',
    'Chỉ viết lời đọc (voice-over), không viết tiêu đề phụ, không đánh số cảnh, không timecode, không ghi chú đạo diễn.',
    'Giữ đúng dữ kiện trong brief và bible; không bịa thêm số liệu, người, địa danh hoặc trích dẫn.',
    'Câu ngắn, rõ, có nhịp; mỗi đoạn 2-4 câu; mở bằng hook, kết bằng câu chốt.',
    'Không dùng markdown, không dùng ký tự trang trí, không dùng emoji.',
    `Độ dài mục tiêu khoảng ${words} từ (${targetMinutes} phút, ~${wpm} từ/phút).`,
    'Trả về JSON hợp lệ duy nhất, không kèm markdown, dạng: {"title":"...","narration":"..."}',
  ].join('\n');
  const user = [
    `Chủ đề/brief: ${String(brief || '').trim()}`,
    `Giọng điệu: ${tone}`,
    `Khán giả: ${audience}`,
    outline ? `Dàn ý bắt buộc:\n${outline}` : '',
    `Bible nhân vật:\n${characters}`,
    `Bối cảnh:\n${backgrounds}`,
    bible?.styleLock ? `Style lock hình ảnh (chỉ để tham khảo, không đưa vào lời đọc):\n${bible.styleLock}` : '',
    'Yêu cầu: narration là văn bản liền mạch, không có tiêu đề bên trong, không có bullet, không có nhãn như "Mở đầu" hay "Phần 2".',
  ].filter(Boolean).join('\n\n');
  return [{role: 'system', content: system}, {role: 'user', content: user}];
}

function stripFence(text) {
  const value = String(text || '').trim();
  const match = value.match(/^```(?:json|markdown|text)?\s*([\s\S]*?)\s*```$/i);
  return (match ? match[1] : value).trim();
}

export function parseScriptResponse(text) {
  const raw = stripFence(text);
  if (!raw) throw Error('AI trả về nội dung rỗng.');
  try {
    const json = JSON.parse(raw);
    const narration = normalizeNarration(json.narration || json.script || json.text || '');
    if (!narration) throw Error('JSON không có narration.');
    return {title: String(json.title || '').trim() || 'Kịch bản mới', narration, warnings: []};
  } catch (error) {
    if (error instanceof SyntaxError) {
      const narration = normalizeNarration(raw);
      if (!narration) throw Error('Không đọc được kịch bản AI trả về.');
      return {title: 'Kịch bản mới', narration, warnings: ['AI không trả JSON; đã dùng toàn bộ văn bản làm narration.']};
    }
    throw error;
  }
}

export function normalizeNarration(text) {
  return String(text || '')
    .replace(/\r\n?/g, '\n')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_`~]/g, '')
    .replace(/^\s*(?:[-•]|\d+[.)])\s+/gm, '')
    .replace(/^\s*(?:mở đầu|kết bài|phần\s+\d+|cảnh\s+\d+)\s*[:：-]\s*/gim, '')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export function scriptToTxt(project) {
  const narration = normalizeNarration(project?.narration || project?.script?.narration || '');
  if (!narration) throw Error('Chưa có kịch bản để xuất TXT.');
  return narration + '\n';
}

export function scriptToSrt(project, {maxCueSeconds = 7, width = 42} = {}) {
  const cues = [];
  let cursor = 0;
  const total = Number(project?.voiceSeconds) || 0;
  const list = sentences(normalizeNarration(project?.narration || ''));
  if (!list.length) throw Error('Chưa có kịch bản để tạo SRT.');
  const words = list.map(s => s.split(/\s+/).filter(Boolean).length);
  const all = words.reduce((n, w) => n + w, 0) || 1;
  const secondsPerWord = total > 0 ? total / all : 60 / 140;
  for (const [index, text] of list.entries()) {
    const duration = Math.max(0.8, words[index] * secondsPerWord);
    const parts = Math.max(1, Math.ceil(duration / maxCueSeconds));
    const partDuration = duration / parts;
    const tokens = text.split(/\s+/).filter(Boolean);
    const perPart = Math.ceil(tokens.length / parts);
    for (let part = 0; part < parts; part += 1) {
      const chunk = tokens.slice(part * perPart, (part + 1) * perPart).join(' ');
      if (!chunk) continue;
      const start = cursor;
      const end = part === parts - 1 ? cursor + partDuration : cursor + partDuration;
      cues.push({start, end, text: wrap(chunk, width)});
      cursor = end;
    }
  }
  return cues;
}

function wrap(text, width) {
  const words = String(text).split(/\s+/).filter(Boolean);
  const lines = [''];
  for (const word of words) {
    const last = lines[lines.length - 1];
    if (!last) lines[lines.length - 1] = word;
    else if ((last + ' ' + word).length <= width) lines[lines.length - 1] = last + ' ' + word;
    else if (lines.length < 2) lines.push(word);
    else lines[lines.length - 1] += ' ' + word;
  }
  return lines.join('\n');
}

export function scriptStats(project) {
  const narration = normalizeNarration(project?.narration || '');
  const words = narration.split(/\s+/).filter(Boolean).length;
  return {words, sentences: sentences(narration).length, characters: narration.length, minutesAt140: Number((words / 140).toFixed(2))};
}
