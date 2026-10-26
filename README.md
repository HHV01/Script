# Video Studio

Ứng dụng chạy local để sản xuất video: bible nhân vật → kịch bản → voice → phân cảnh → prompt ảnh → Google Flow → kiểm tra ảnh → ghép MP4 1080p.

Có hai luồng:

- **Studio** (`/`): 4 tab offline cũ — kịch bản, prompt, căn voice/SRT, ghép ảnh/clip. Không cần AI/API.
- **Pipeline AI** (`/pipeline.html`): luồng tự động mới, có AI text, VieNeu-TTS local, Flow Playwright và bước verify ảnh trước khi dựng.

## Yêu cầu

- Node.js 22 trở lên.
- FFmpeg/ffprobe: dùng `tools/ffmpeg/bin/` (Windows) hoặc FFmpeg trong `PATH`.
- Chrome hoặc Edge để dựng cảnh HTML và chạy Flow.
- VieNeu-TTS: Python 3.12 + `uv`; GPU NVIDIA là tùy chọn nhưng nhanh hơn nhiều. Máy đã test: RTX 3060 12 GB.

## Chạy nhanh

```bat
npm ci
tools\start-vieneu.bat
npm start
```

Mở:

- Studio: http://localhost:3211
- Pipeline AI: http://localhost:3211/pipeline.html

`tools\start-vieneu.bat` tạo venv ở `%LOCALAPPDATA%\VideoStudio\vieneu-venv` (ngoài OneDrive) và tải model VieNeu v3 Turbo ở lần chạy đầu. Server VieNeu mặc định ở `http://127.0.0.1:8000`.

## Cấu hình AI

AI dùng API OpenAI-compatible. Có thể cấu hình bằng `.env`:

```env
OPENAI_BASE_URL=http://localhost:20128/v1
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
```

Hoặc lưu trong Pipeline → Cài đặt (file `.video-studio-data/pipeline-settings.json`, quyền `0600`). Key chỉ nằm ở server, API `GET /api/pipeline/settings` chỉ trả `hasKey`, không trả key.

Nếu gateway local không kết nối được và có `GROQ_API_KEY`, app tự fallback sang Groq với model `openai/gpt-oss-120b`. Lưu ý: fallback này gửi nội dung kịch bản lên Groq.

## Pipeline AI — 6 bước

1. **Bible**
   - Import roster từ `Video-scripts/bibles/*.json` (ví dụ `sumer-roster.json`, `ve-voi-roster.json`).
   - Sửa nhân vật, bối cảnh, style lock, negative prompt, template prompt, ảnh tham chiếu.
   - Biến template: `{loi_ke}`, `{nhan_vat}`, `{boi_canh}`, `{style_lock}`, `{negative}`, `{chi_tiet}`, `{chu_the}`, `{quy_tac_nhan}`, `{so_canh}`, `{bat_dau}`, `{ket_thuc}`, `{thoi_luong}`. Bắt buộc có `{loi_ke}`.

2. **Kịch bản**
   - Nhập brief, thời lượng, giọng điệu, khán giả, dàn ý.
   - Bấm **Sinh bằng AI**, sửa bản nháp, rồi **Duyệt & dùng kịch bản**.
   - Xuất TXT chỉ có lời đọc, không header/timecode, để đưa qua TTS.

3. **Voice**
   - Chọn base URL, model, voice của VieNeu.
   - Clone giọng từ mẫu 3–8 giây (WAV/MP3/M4A/OGG/WebM), rồi dùng tên giọng đó.
   - Tạo voice cho toàn kịch bản; app chia nhỏ text, ghép các đoạn, chuyển MP3 và lưu vào assets.
   - `voiceSeconds` lấy từ ffprobe, dùng cho bước phân cảnh và render.

4. **Phân cảnh**
   - Chia câu thành cảnh theo nhịp tối đa/tối thiểu.
   - Căn mốc theo chỗ ngắt nghỉ thật của voice; nếu không đủ ngắt nghỉ thì fallback theo số từ.
   - Ghép prompt toàn bộ từ bible; sửa tay từng prompt nếu cần.
   - Xuất `queue.json`, `prompts.txt`, `queue.csv` cho Flow.

5. **Flow ảnh**
   - Nhập URL project Flow, profile Chrome, thư mục tải, thời gian chờ.
   - **Chạy tự động**: Playwright mở Chrome với profile đã đăng nhập, nhập prompt, bấm tạo, tải ảnh, lưu `beat-001.png`, `beat-002.png`… Adapter **chỉ chọn chế độ Image/Hình ảnh** và chỉ nhận file PNG/JPEG/WebP; không bấm Video/Clip và không tải video.
   - Lần đầu chạy nên để headed để đăng nhập Google. Nếu gặp login/captcha, job dừng với trạng thái `needs_login`.
   - Có thể bỏ qua automation: tải ảnh thủ công, đặt tên `beat-NNN.png`, rồi **Upload & kiểm tra**.

6. **Ghép video**
   - Chỉ cho dựng khi đủ ảnh, đủ prompt, tổng thời lượng cảnh khớp voice (sai số 0,5 giây).
   - Xuất MP4 1920×1080, 30 fps, audio AAC.
   - Giới hạn: 1–1.000 cảnh; mỗi cảnh 0,5–30 giây.

## Kiểm tra ảnh trước khi dựng

Một batch chỉ được chấp nhận khi:

- Đủ số ảnh bằng số prompt.
- Tên file đọc được số beat (`beat-001.png`, `beat_2.jpg`, `scene-3.webp`…).
- Không trùng số beat, không có file thừa, không có file không đọc được số.
- Định dạng PNG/JPEG/WebP.
- Tối thiểu 1280×720 và tỉ lệ 16:9 (sai số 2%).
- Với ảnh do Flow tự động tải: `promptHash` phải khớp prompt hiện tại, tránh dùng ảnh của prompt cũ.

Nếu chưa đạt, app không gắn ảnh vào cảnh và hiển thị bảng thiếu/lỗi/trùng/thừa.

## Bảo mật và dữ liệu

- `workspace.json`, assets, voice, render nằm trong `.video-studio-data/` (gitignore).
- Key AI nằm trong `.env` hoặc `.video-studio-data/pipeline-settings.json`; không lưu trong workspace và không gửi xuống client.
- Profile Chrome của Flow chứa cookie đăng nhập; mặc định nằm trong `.video-studio-data/flow/chrome-profile` và không được commit.
- `.env`, `tools/vieneu/`, `.video-studio-data-test/` đã được gitignore.

## Google Flow — lưu ý

Automation Flow là **thử nghiệm**:

- UI Flow thay đổi thường xuyên; selector mặc định có thể phải sửa trong Pipeline → Flow → Selector nâng cao.
- Tự động hoá có thể vi phạm điều khoản của Google và ảnh hưởng tài khoản; dùng có trách nhiệm.
- Không có cơ chế vượt captcha. Khi Flow yêu cầu xác minh, job dừng để người dùng xử lý.
- Flow có thể giới hạn credit/tốc độ; app chạy tuần tự và có resume theo `manifest.json`.
- Tải ảnh tham chiếu lên Flow có thể không hoạt động với mọi phiên bản UI.

## API chính

- `GET/PUT /api/pipeline/settings` — cấu hình AI/TTS/Flow (key được che).
- `GET /api/bibles`, `POST /api/bibles/import` — roster.
- `POST /api/ai/script` — sinh kịch bản.
- `GET /api/voice/status`, `POST /api/voice/synthesize`, `POST /api/voice/clone`.
- `POST /api/scenes/split` — chia cảnh theo voice.
- `POST /api/prompts/build`, `POST /api/flow/queue`.
- `POST /api/flow/verify`, `POST /api/flow/run`, `GET /api/flow/jobs/:id`.
- `POST /api/render`, `GET /api/renders/:id`, `GET /api/renders/:id/download` — luồng render cũ.

## Kiểm thử

```bat
npm test
```

Test gồm: prompt template cũ, căn voice, server, render MP4 thật (nếu có FFmpeg), bible/prompt builder, script parser, chia cảnh, queue Flow và verify ảnh.

## Giới hạn đã biết

- Chưa burn phụ đề vào video; SRT có thể xuất từ Studio nhưng Pipeline chưa ghép phụ đề.
- Chưa có nhạc nền/transition/thumbnail tự động trong Pipeline.
- TTS tối đa 120.000 ký tự/lần; voice tối đa 64 MB.
- Flow automation chưa được kiểm chứng trên mọi tài khoản/UI Flow.
- Fallback Groq gửi kịch bản lên cloud; muốn offline hoàn toàn thì dùng Studio 4 tab.

## Paper Collage Documentary (luồng cũ)

Giữ nguyên trong Studio: nhịp 2,5 giây, prompt ghép bằng code, Universal Video Prompt và 3 thumbnail mẫu. Luồng này không gọi AI và không tự gửi prompt lên dịch vụ ngoài.
