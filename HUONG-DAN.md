# Làm một video hoàn chỉnh từ đầu đến cuối

Tài liệu này ghi lại **toàn bộ quy trình** biến một chủ đề thành video 1080p có lời đọc, phụ đề và ảnh minh họa: từ bible nhân vật, viết kịch bản, **tạo voice**, chia cảnh theo đúng thời lượng voice, sinh prompt, tạo ảnh bằng Google Flow, kiểm tra ảnh rồi dựng MP4.

Đây là tài liệu quy trình, **không kèm kịch bản, ảnh, voice hay dữ liệu của bất kỳ dự án nào**. Mọi thứ bạn tạo ra nằm trong `projects/<tên>/` và đã được gitignore.

```
bible nhân vật ─┐
chủ đề ─────────┴─► 1 script ─► script.txt ─► 2 voice ─► voice.wav + voice.words.json
                                                              │
        3 scenes ◄────────────────────────────────────────────┘   (cắt cảnh theo câu + mốc thời gian voice)
           │ scenes.json
           ▼
        4 prompts  (style + ngoại hình nhân vật cố định + nội dung cảnh)
           ▼
        5 generate ─► Google Flow (extension) ─► gắn ảnh ↔ cảnh
           ▼
        6 collect  ─► kiểm tra số ảnh = số prompt ─► tải ảnh về images/
           ▼
        7 render   ─► final.mp4 (ảnh + voice + phụ đề)
```

---

## 0. Chuẩn bị môi trường

### Cần có

| Thứ | Ghi chú |
|---|---|
| Python 3.10+ | Đã test với 3.12 |
| FFmpeg + ffprobe | Phải có trong `PATH`; dùng để đo voice, cắt frame, ghép video |
| Chrome | Để chạy extension điều khiển Google Flow |
| GPU NVIDIA (tuỳ chọn) | Voice nhanh hơn nhiều lần; CPU vẫn chạy được |
| Tài khoản Google Flow | Tự đăng nhập trong Chrome; pipeline không lưu mật khẩu |

### Cài đặt

```bash
git clone https://github.com/HHV01/Script.git
cd Script

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Nếu có GPU NVIDIA, cài bản PyTorch CUDA **trước** khi cài `vieneu` (xem hướng dẫn của VieNeu-TTS), sau đó:

```bash
pip install vieneu
```

Chạy thử:

```bash
ffmpeg -version
python run.py --help
```

### Cấu hình AI viết kịch bản

```bash
cp .env.example .env
```

Mở `.env`, điền key lấy tại <https://opencode.ai/console> → API keys:

```env
OPENCODE_API_KEY=...
```

Model mặc định nằm ở `config/settings.yaml` → `llm.model` (`deepseek-v4-pro`). Có thể đổi sang model OpenCode Go khác.

> Voice **không dùng key**. VieNeu-TTS chạy hoàn toàn trên máy bạn.

### Nạp extension điều khiển Flow

1. Mở Chrome → `chrome://extensions`
2. Bật **Developer mode**
3. **Load unpacked** → chọn thư mục `flow_extension/`
4. Mở sẵn một project Google Flow trong tab Chrome

Extension chỉ điền prompt và bấm tạo **ảnh**. Nó không bao giờ bấm tạo Video/Clip.

---

## 1. Tạo project và bible nhân vật

### Tạo project

```bash
python run.py new ten_video
```

Lệnh này sao chép `projects/_template/` thành `projects/ten_video/`. Mở `projects/ten_video/project.yaml`:

```yaml
topic: "Chủ đề video của bạn"
minutes: 8
characters: [tich]
flow_url: ""
```

- `minutes`: độ dài mục tiêu, dùng để tính số từ kịch bản.
- `characters`: danh sách id trong `config/characters/`.
- `flow_url`: dán URL project Flow đã tạo sẵn (để trống nếu tự mở tay).

### Bible nhân vật

Mỗi nhân vật là một file `config/characters/<id>.yaml`:

```yaml
id: tich
name: Tích
role: Người dẫn chuyện

vibe:                     # dùng khi viết kịch bản
  tone: "tò mò, điềm tĩnh, hơi hài hước"
  pov: "ngôi thứ nhất số nhiều khi dẫn dắt"
  hook: "mở bằng câu hỏi gây tò mò trong 10 giây đầu"
  ending: "kết bằng câu hỏi để người xem bình luận"
  avoid: "lặp ý, sáo rỗng, câu quá 35 từ"

visual: "Tich, a young man with short black hair, round glasses, wearing a navy blue vest over a white shirt, slim build"
```

`visual` là phần quan trọng nhất để nhân vật **giống nhau giữa các cảnh**: nó được chèn nguyên văn vào mọi prompt ảnh có nhân vật đó. Hãy viết bằng tiếng Anh, cụ thể (tuổi, tóc, kính, trang phục, dáng người), tránh từ mơ hồ.

---

## 2. Viết kịch bản

Chỉ chạy bước 1:

```bash
python run.py run ten_video --only script
```

Pipeline đọc `config/prompts/script.md`, ghép chủ đề + độ dài + vibe nhân vật rồi gọi LLM. Sau đó:

- Ước lượng độ dài theo `script.words_per_minute` (mặc định **160 từ/phút** cho tiếng Việt).
- Loại các câu trùng/na ná nhau theo `script.dedupe_threshold` (mặc định **0.85**).
- Ghi `projects/ten_video/script.txt` — chỉ có lời đọc, không tiêu đề, không timecode.

**Bắt buộc đọc lại và sửa tay** trước khi làm voice. Kiểm tra:

- Mở đầu có hook trong 10 giây đầu chưa?
- Có câu nào sai sự kiện/số liệu không?
- Câu có quá dài để đọc thành tiếng không? (nên dưới 25–30 từ)
- Có đoạn nào lặp ý không?

Sửa trực tiếp `script.txt` rồi chạy tiếp bước voice. Nếu muốn LLM viết lại từ đầu:

```bash
python run.py run ten_video --only script --force
```

> Tự viết kịch bản? Chỉ cần bỏ `script.txt` vào thư mục project, bước 1 sẽ tự bỏ qua.

---

## 3. Voice — phần được tích hợp sẵn

Đây là bước biến `script.txt` thành file đọc hoàn chỉnh kèm mốc thời gian từng từ. Có hai chế độ.

### 3.1. VieNeu-TTS chạy local (mặc định, khuyến nghị)

`config/settings.yaml`:

```yaml
voice:
  provider: vieneu
  vieneu:
    mode: v3turbo        # v3turbo: 48 kHz, chất lượng cao | v3nano: máy yếu, nhẹ hơn
    voice: "Hải Đăng"    # tên giọng có sẵn
    ref_audio: ""        # clip 3–8 giây để nhân bản giọng (tuỳ chọn)
    precision: null      # CPU có VNNI: int8 để nhanh hơn; không chắc thì để null
    gap_seconds: 0.3     # khoảng lặng giữa các câu
```

Chạy:

```bash
python run.py run ten_video --only voice
```

Lần đầu sẽ tải model (vài GB) và có thể mất vài phút. Các lần sau chỉ còn thời gian đọc.

#### Danh sách giọng có sẵn

```bash
python -c "from vieneu import Vieneu; print(Vieneu().list_preset_voices())"
```

Chọn một tên trong danh sách rồi điền vào `voice.vieneu.voice`. Có thể ghi đè riêng cho từng video trong `project.yaml`:

```yaml
settings:
  voice:
    vieneu:
      voice: "Mai Anh"
```

#### Nhân bản giọng từ mẫu 3–8 giây

1. Đặt file mẫu vào thư mục project, ví dụ `projects/ten_video/giong-mau.wav`.
2. Trong `project.yaml`:

```yaml
settings:
  voice:
    vieneu:
      ref_audio: "giong-mau.wav"   # đường dẫn tương đối tính từ thư mục project
```

3. Chạy lại bước voice:

```bash
python run.py run ten_video --only voice --force
```

Pipeline sẽ đăng ký giọng mới với tên `<tên_project>_voice` rồi dùng giọng đó cho toàn bộ kịch bản.

**Mẫu giọng tốt:**

- 3–8 giây, **một người nói**, không nhạc nền, không tạp âm.
- Nói tự nhiên, cùng tốc độ và cảm xúc với video.
- Ưu tiên WAV 48 kHz; MP3/M4A/OGG vẫn được.
- Không cắt giữa từ; để thêm 0,2–0,5 giây im lặng hai đầu.

#### File đầu ra

| File | Nội dung |
|---|---|
| `voice.wav` | Toàn bộ lời đọc, đã ghép các câu, chèn khoảng lặng `gap_seconds` |
| `voice.words.json` | Mốc `start`/`end` của từng từ, dùng cho bước chia cảnh và phụ đề |

Điểm mạnh của cách tích hợp này: **mỗi câu được đọc riêng**, nên pipeline biết **chính xác** thời điểm bắt đầu/kết thúc của từng câu. Không cần Whisper, không có sai số nhận dạng. Trong mỗi câu, thời gian từng từ được chia theo độ dài chữ — đủ tốt để đặt phụ đề, nhưng mốc cấp câu mới là mốc chính xác.

#### Chỉnh nhịp đọc

- `gap_seconds` lớn hơn → nghỉ lâu hơn giữa các câu, video chậm rãi hơn.
- Chọn giọng khác → tốc độ/nhấn nhá khác.
- Câu ngắn hơn trong `script.txt` → nhịp tự nhiên hơn, dễ cắt cảnh hơn.
- `v3turbo` cho chất lượng tốt nhất; `v3nano` chỉ nên dùng khi máy quá yếu.

Sau khi sửa `script.txt`, phải chạy lại voice với `--force`, nếu không pipeline sẽ bỏ qua vì đã thấy `voice.wav` + `voice.words.json`.

### 3.2. Dùng voice AI khác (manual)

Nếu bạn muốn dùng ElevenLabs, Azure, hoặc dịch vụ khác:

```yaml
voice:
  provider: manual
  whisper:
    model: small
    language: vi
```

1. Đưa `script.txt` qua dịch vụ đó.
2. Lưu file kết quả thành `projects/ten_video/voice.mp3` (hoặc `.wav`, `.m4a`, `.ogg`).
3. Cài Whisper để lấy timestamp:

```bash
pip install faster-whisper
```

4. Chạy:

```bash
python run.py run ten_video --only voice
```

Lúc này `voice.words.json` được tạo bằng `faster-whisper` với `word_timestamps=True`. Chất lượng căn cảnh phụ thuộc vào độ chính xác nhận dạng; nếu voice không khớp script, bước chia cảnh sẽ báo lỗi.

### 3.3. Lỗi voice thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `Chưa cài VieNeu-TTS` | `pip install vieneu` trong đúng môi trường ảo |
| Độ dài file lệch tính toán | Sai `mode`/sample rate — kiểm tra `voice.vieneu.mode` |
| Voice chạy quá chậm | Cài PyTorch CUDA đúng phiên bản; kiểm tra `torch.cuda.is_available()` |
| Giọng clone không giống | Mẫu dài hơn 8 giây, có nhạc/tạp âm, hoặc nhiều người nói |
| Muốn đổi giọng nhưng bị bỏ qua | Thêm `--force` để đọc lại từ đầu |
| Máy hết RAM | Dùng `v3nano`, chia script thành nhiều project nhỏ |

Voice chạy local nên **không gửi kịch bản lên cloud** và không tốn phí theo ký tự.

---

## 4. Chia cảnh theo voice

```bash
python run.py run ten_video --only scenes
```

Cách hoạt động:

1. Tách `script.txt` thành từng câu.
2. Khớp từng từ của script với `voice.words.json` (so khớp mờ, từ không khớp được nội suy tuyến tính).
3. Mỗi câu là một đơn vị; câu dài hơn `max_seconds` bị tách theo dấu phẩy/chấm phẩy.
4. Gộp/tách để mỗi cảnh nằm trong khoảng `min_seconds`–`max_seconds`.
5. Ghi `scenes.json`, các cảnh **nối liền nhau, không hở tiếng**:

```json
[
  { "id": 1, "text": "Lời đọc của cảnh 1", "start": 0.0, "end": 6.42 },
  { "id": 2, "text": "Lời đọc của cảnh 2", "start": 6.42, "end": 12.18 }
]
```

Mặc định trong `config/settings.yaml`:

```yaml
scenes:
  min_seconds: 4     # ngắn hơn sẽ gộp câu sau
  max_seconds: 8     # dài hơn sẽ tách theo dấu phẩy
```

Video kể chuyện thường dùng 4–8 giây/cảnh. Muốn nhịp nhanh hơn (video ngắn, TikTok) có thể giảm còn 2,5–5 giây; video lịch sử/chậm rãi có thể 6–10 giây.

> Chạy lại bước này với `--force` sẽ tạo `scenes.json` mới và **mất liên kết prompt/ảnh đã gắn**. Chỉ làm khi thật sự muốn chia lại từ đầu.

---

## 5. Sinh prompt ảnh

```bash
python run.py run ten_video --only prompts
```

Mỗi cảnh được gửi LLM (theo lô `prompts.batch_size`, mặc định 20) để sinh:

- `scene_desc`: 1–2 câu tiếng Anh tả chủ thể, hành động, bối cảnh, góc máy.
- `characters`: id nhân vật xuất hiện trong ảnh.

Prompt cuối cùng được ghép theo thứ tự:

```
style.prefix + visual của từng nhân vật + scene_desc + style.suffix + avoid
```

Ví dụ `config/style.yaml`:

```yaml
aspect_ratio: "16:9"
prefix: "Flat vector illustration, clean bold outlines, warm muted palette, cinematic composition"
suffix: "no text, no captions, no watermark"
avoid: "photorealism, blurry, extra fingers, distorted face, text overlay"
```

Muốn đổi phong cách cả kênh thì sửa `config/style.yaml`, rồi chạy lại bước prompt với `--force`. Muốn sửa riêng một cảnh thì sửa `image_prompt` trong `scenes.json`.

Kết quả phụ: `prompts.txt` để bạn đọc lại toàn bộ prompt theo số cảnh.

---

## 6. Tạo ảnh bằng Google Flow

### Kết nối

1. Mở project Flow trong Chrome (tab đã đăng nhập).
2. Kiểm tra extension ↔ tab:

```bash
python run.py run ten_video --only ping
```

Kết quả tốt: `kết nối OK` và số `tiles` (ảnh đang có trong project Flow). Nếu `tiles = 0` dù project đã có ảnh, chỉnh selector `tileImg` trong `flow_extension/selectors.js`.

Cấu hình trong `config/settings.yaml`:

```yaml
flow:
  port: 8765
  token: ""                 # đặt token nếu muốn chặn trang lạ gọi vào localhost
  delay_seconds: [3, 8]     # nghỉ ngẫu nhiên giữa 2 prompt
  retries: 2
  submit_timeout: 180       # tối đa chờ 1 ảnh
  pick: first               # 1 prompt ra nhiều ảnh: lấy ảnh đầu
```

### Chạy

```bash
python run.py run ten_video --only generate
```

Pipeline gửi từng prompt, chờ ảnh ổn định, rồi lưu `tile_key` của ảnh vào `scenes.json` **sau mỗi cảnh**. Bị ngắt giữa chừng? Chạy lại lệnh trên, nó tiếp tục từ cảnh chưa có ảnh.

Lưu ý:

- **Chỉ tạo ảnh.** Nếu Flow đang ở chế độ Video mà extension không chuyển được, nó báo lỗi thay vì tạo video.
- Flow đổi giao diện thường xuyên. Mọi selector nằm ở `flow_extension/selectors.js`; sửa xong chạy lại `--only ping`.
- Không có cơ chế vượt captcha. Nếu Flow yêu cầu xác minh, xử lý tay rồi chạy lại.
- Tự động hóa có thể vi phạm điều khoản của Google; dùng có trách nhiệm và tự cân nhắc rủi ro tài khoản.
- Có thể bỏ qua bước này: tạo ảnh thủ công, đặt tên `001.png`, `002.png`… vào `projects/ten_video/images/`, rồi chuyển thẳng sang render.

---

## 7. Kiểm tra và tải ảnh

```bash
python run.py run ten_video --only collect
```

Bước này **không tải bừa**. Nó chỉ tải khi tất cả điều kiện sau đúng:

- Mỗi cảnh có `tile_key`.
- Không có hai cảnh trỏ cùng một ảnh.
- Không có cảnh trỏ ảnh đã bị xóa khỏi Flow.
- Số ảnh đã gắn = số prompt (số cảnh).

Nếu sai, pipeline in rõ cảnh nào lỗi và **dừng**, không ghi đè ảnh cũ. Sửa bằng cách chạy lại `generate` (thường là đủ), rồi `collect`.

Khi khớp, ảnh được tải về `projects/ten_video/images/001.png`, `002.png`… và `scenes.json` được cập nhật trường `image`.

---

## 8. Dựng video

```bash
python run.py run ten_video --only render
```

Đầu ra:

- `final.mp4` — 1920×1080, 30 fps, H.264 + AAC 192 kbps.
- `subtitles.srt` — phụ đề theo từng cảnh (luôn xuất, kể cả khi không burn).

Cấu hình trong `config/settings.yaml`:

```yaml
render:
  width: 1920
  height: 1080
  fps: 30
  ken_burns: true          # zoom nhẹ mỗi cảnh cho đỡ tĩnh
  burn_subtitles: true     # in phụ đề lên video
```

Cách dựng: mỗi ảnh được scale/crop về 16:9, tạo clip đúng số frame theo mốc thời gian voice (tính tích lũy để tổng không lệch), ghép nối, rồi ghép với voice. Tổng thời lượng video khớp chính xác với voice.

Muốn bản không phụ đề (để tự thêm trong CapCut/Premiere):

```yaml
render:
  burn_subtitles: false
```

---

## 9. Kiểm tra trước khi xuất bản

- [ ] Nghe lại toàn bộ voice: không mất chữ, không phát âm sai tên riêng.
- [ ] Ảnh đúng cảnh, nhân vật giống nhau, không có chữ/watermark lạ.
- [ ] Không có ảnh bị crop mất mặt/chủ thể.
- [ ] Phụ đề hiện đúng chỗ, không che mặt, không quá 2 dòng.
- [ ] Độ dài video đúng mục tiêu; hook nằm trong 10 giây đầu.
- [ ] Tiêu đề, mô tả, thumbnail (làm ngoài pipeline).
- [ ] Kiểm tra lại bản quyền ảnh/voice/nhạc nếu có dùng tài nguyên ngoài.

---

## Lệnh hay dùng

```bash
python run.py new ten_video                  # tạo project
python run.py run ten_video                  # chạy tất cả, bước xong tự bỏ qua
python run.py run ten_video --from scenes    # chạy từ bước scenes trở đi
python run.py run ten_video --only voice     # chỉ chạy voice
python run.py run ten_video --only ping      # kiểm tra extension ↔ Flow
python run.py run ten_video --only render --force   # dựng lại video
```

Thứ tự các bước: `script → voice → scenes → prompts → generate → collect → render`.

## Cấu trúc một project

```
projects/ten_video/
├── project.yaml          # chủ đề, độ dài, nhân vật, ghi đè settings
├── script.txt            # lời đọc đã duyệt
├── voice.wav             # voice hoàn chỉnh (VieNeu)
├── voice.words.json      # mốc thời gian từng từ
├── scenes.json           # cảnh + prompt + liên kết ảnh
├── prompts.txt           # danh sách prompt để đọc lại
├── images/               # 001.png, 002.png, ...
├── subtitles.srt
└── final.mp4
```

`projects/*` đã được gitignore (trừ `_template`), nên kịch bản, voice và ảnh của bạn không bị đẩy lên GitHub.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân / cách xử lý |
|---|---|
| `Extension chưa kết nối` | Chưa nạp extension, chưa mở tab Flow, hoặc sai `flow.port` |
| `tiles = 0` | Selector `tileImg` không khớp UI Flow hiện tại |
| `Có cảnh chưa có image_prompt` | Chạy `--only prompts` trước `generate` |
| `KHÔNG TẢI` ở bước collect | Thiếu ảnh/trùng ảnh/ảnh bị xóa — chạy lại `generate` |
| Voice lệch vài giây | Kiểm tra `mode` và sample rate; xóa `voice.*` rồi chạy `--force` |
| `ffmpeg` không tìm thấy | Cài FFmpeg và thêm vào `PATH`, mở lại terminal |
| Lỗi font khi burn phụ đề | Dùng font có trong hệ thống; sửa `FontName` trong `s7_render.py` |

## Thời gian tham khảo (video 8 phút)

| Bước | Thời gian |
|---|---|
| Viết + sửa kịch bản | 5–15 phút |
| Voice (GPU) | 3–10 phút |
| Voice (CPU) | 20–60 phút |
| Chia cảnh + prompt | 1–3 phút |
| Tạo ảnh trên Flow | 20–60 phút (tuỳ số cảnh và credit) |
| Kiểm tra + tải ảnh | 1–5 phút |
| Render | 5–15 phút |

## Ghi chú

- Pipeline chỉ tạo **ảnh**, không tạo video bằng AI; chuyển động đến từ Ken Burns khi render.
- Voice và phần lớn bước chạy local; chỉ bước viết kịch bản/prompt gọi LLM.
- Không commit `.env`, `projects/*`, token bridge hay profile Chrome.
- Đây là quy trình tham khảo, không phải sản phẩm hoàn chỉnh cho mọi loại video. Hãy chỉnh `config/` theo kênh của bạn.
