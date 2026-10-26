// Client OpenAI-compatible (chat) và VieNeu-TTS (speech + clone).
// Không log key; lỗi trả về thông điệp ngắn, không kèm header.

const trimSlash = (value) => String(value || '').replace(/\/+$/, '');

function joinV1(baseUrl, path) {
  const base = trimSlash(baseUrl);
  if (!base) throw Error('Thiếu địa chỉ API.');
  return `${base}${base.endsWith('/v1') ? '' : '/v1'}${path}`;
}

async function readJson(response) {
  const text = await response.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {raw: text.slice(0, 500)}; }
}

function upstreamError(response, data, label) {
  const message = data?.error?.message || data?.error || data?.message || data?.detail || data?.raw || response.statusText;
  return Object.assign(Error(`${label} lỗi ${response.status}: ${String(message).slice(0, 300)}`), {status: response.status >= 500 ? 502 : 400});
}

async function withTimeout(timeoutMs, fn) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fn(controller.signal); }
  catch (error) {
    if (error.name === 'AbortError') throw Object.assign(Error('Máy chủ AI phản hồi quá lâu.'), {status: 504});
    throw error;
  } finally { clearTimeout(timer); }
}

async function fetchUpstream(fetchImpl, url, options, label) {
  try { return await fetchImpl(url, options); }
  catch (error) {
    throw Object.assign(Error(`Không kết nối được ${label} tại ${url}. Kiểm tra server/gateway đã chạy chưa.`), {status: 502, cause: error});
  }
}

export function createAiClient({baseUrl, apiKey = '', model = 'gpt-4o-mini', fetchImpl = fetch} = {}) {
  const url = joinV1(baseUrl, '/chat/completions');
  return {
    model,
    async chat(messages, {temperature = 0.7, maxTokens = 8000, timeoutMs = 240000} = {}) {
      const headers = {'Content-Type': 'application/json'};
      if (apiKey) headers.Authorization = `Bearer ${apiKey}`;
      const response = await withTimeout(timeoutMs, signal => fetchUpstream(fetchImpl, url, {
        method: 'POST', headers, signal,
        body: JSON.stringify({model, messages, temperature, max_tokens: maxTokens, stream: false}),
      }, 'AI'));
      const data = await readJson(response);
      if (!response.ok) throw upstreamError(response, data, 'AI');
      const content = data?.choices?.[0]?.message?.content;
      if (!content) throw Error('AI không trả nội dung.');
      return String(content);
    },
  };
}

export function vieneuRoot(baseUrl) {
  const base = trimSlash(baseUrl || 'http://127.0.0.1:8000/v1');
  return base.endsWith('/v1') ? base.slice(0, -3) : base;
}

export function createVieneuClient({baseUrl = 'http://127.0.0.1:8000/v1', apiKey = '', model = 'vieneu-v3-turbo', fetchImpl = fetch} = {}) {
  const base = trimSlash(baseUrl);
  const speechUrl = joinV1(base, '/audio/speech');
  const headers = (extra = {}) => {
    const out = {...extra};
    if (apiKey) out.Authorization = `Bearer ${apiKey}`;
    return out;
  };
  return {
    baseUrl: base,
    model,
    async health() {
      const response = await withTimeout(5000, signal => fetchUpstream(fetchImpl, `${vieneuRoot(base)}/health`, {signal}, 'VieNeu'));
      const data = await readJson(response);
      if (!response.ok) throw upstreamError(response, data, 'VieNeu');
      return data;
    },
    async voices() {
      const response = await withTimeout(10000, signal => fetchUpstream(fetchImpl, joinV1(base, '/voices'), {headers: headers(), signal}, 'VieNeu'));
      const data = await readJson(response);
      if (!response.ok) throw upstreamError(response, data, 'VieNeu');
      return data?.data || [];
    },
    async speech({text, voice, responseFormat = 'wav', sampleRate = 48000, timeoutMs = 600000} = {}) {
      const input = String(text || '').trim();
      if (!input) throw Error('Thiếu nội dung cần đọc.');
      const response = await withTimeout(timeoutMs, signal => fetchUpstream(fetchImpl, speechUrl, {
        method: 'POST', headers: headers({'Content-Type': 'application/json'}), signal,
        body: JSON.stringify({model, input, voice: voice || undefined, response_format: responseFormat, sample_rate: sampleRate, stream_format: 'audio'}),
      }, 'VieNeu'));
      if (!response.ok) throw upstreamError(response, await readJson(response), 'VieNeu');
      const bytes = Buffer.from(await response.arrayBuffer());
      if (!bytes.length) throw Error('VieNeu trả file rỗng.');
      return {bytes, mime: responseFormat === 'wav' ? 'audio/wav' : 'audio/pcm'};
    },
    async cloneVoice({name, bytes, filename = 'reference.wav', denoise = true, description = '', timeoutMs = 120000} = {}) {
      if (!/^[\p{L}\p{N}][\p{L}\p{N} ._-]{0,63}$/u.test(String(name || ''))) throw Error('Tên giọng 1-64 ký tự, không có ký tự đặc biệt.');
      if (!bytes?.length) throw Error('Thiếu file mẫu giọng.');
      const form = new FormData();
      form.append('name', String(name));
      form.append('denoise', String(Boolean(denoise)));
      form.append('description', String(description || '').slice(0, 64));
      form.append('file', new Blob([bytes]), filename);
      const response = await withTimeout(timeoutMs, signal => fetchUpstream(fetchImpl, joinV1(base, '/voices'), {
        method: 'POST', headers: headers(), body: form, signal,
      }, 'VieNeu'));
      const data = await readJson(response);
      if (!response.ok) throw upstreamError(response, data, 'VieNeu');
      return data;
    },
  };
}

export function chunkText(text, maxChars = 8000) {
  const input = String(text || '').trim();
  if (!input) return [];
  const chunks = [];
  let current = '';
  const parts = input.split(/(?<=[.?!…:;])\s+|\n{2,}/u).filter(Boolean);
  for (const part of parts) {
    const next = current ? `${current} ${part}` : part;
    if (next.length > maxChars && current) { chunks.push(current.trim()); current = part; }
    else current = next;
  }
  if (current.trim()) chunks.push(current.trim());
  // Câu quá dài vẫn có thể vượt giới hạn; cắt cứng để không bị API từ chối.
  return chunks.flatMap(chunk => {
    if (chunk.length <= maxChars) return [chunk];
    const out = [];
    for (let i = 0; i < chunk.length; i += maxChars) out.push(chunk.slice(i, i + maxChars));
    return out;
  });
}
