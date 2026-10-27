# Script → Voice → Ảnh (Google Flow) → Video

Một lệnh, 7 bước. Mỗi bước đọc/ghi file trong `projects/<tên>/`, bước nào đã xong sẽ tự bỏ qua, bị ngắt giữa chừng thì chạy lại là tiếp tục.

> **Hướng dẫn từ đầu đến cuối:** [HUONG-DAN.md](HUONG-DAN.md) — quy trình 7 bước, phần voice chi tiết (giọng có sẵn, nhân bản giọng, timestamp), checklist kiểm tra và lỗi thường gặp.

```
bible nhân vật ─┐
chủ đề ─────────┴─► 1 script ─► script.txt ─► 2 voice ─► voice.wav (VieNeu) / voice.mp3 (manual) + voice.words.json
                                                              │
        3 scenes ◄────────────────────────────────────────────┘   (cắt cảnh theo câu + thời gian voice)
           │ scenes.json
           ▼
        4 prompts  (style + ngoại hình nhân vật cố định + nội dung cảnh)
           ▼
        5 generate ─► Google Flow (extension)  ─► gắn ảnh ↔ cảnh trong scenes.json
           ▼
        6 collect  ─► KIỂM TRA số ảnh = số prompt ─► (khớp mới) tải nguyên project vào images/
           ▼
        7 render   ─► final.mp4 (ảnh + voice + phụ đề kịch bản)
```

## Cài đặt
```
pip install -r requirements.txt     # gồm cả VieNeu-TTS; + cài ffmpeg và để trong PATH
# Có GPU NVIDIA: cài thêm bản torch CUDA trước khi cài vieneu (xem hướng dẫn của VieNeu-TTS) để voice nhanh hơn ~25 lần
cp .env.example .env                # điền OPENCODE_API_KEY (OpenCode Go: https://opencode.ai/console → API keys)
```
Extension: Chrome → `chrome://extensions` → bật Developer mode → *Load unpacked* → chọn thư mục `flow_extension/`.

> **Chỉ tạo ảnh**: pipeline/extension chỉ điền prompt và bấm tạo **ảnh** (Image/Hình ảnh), không bao giờ tạo video. Nếu Flow đang ở chế độ Video mà không chuyển được, extension sẽ báo lỗi thay vì tạo nhầm.

## Dùng
```
python run.py new tich_duc                 # tạo projects/tich_duc/
# sửa projects/tich_duc/project.yaml (chủ đề, nhân vật)
python run.py run tich_duc                 # chạy tất cả
python run.py run tich_duc --from prompts  # chạy từ một bước
python run.py run tich_duc --only ping     # kiểm tra extension ↔ tab Flow
```
- **Voice**: mặc định dùng [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) chạy local (Apache-2.0), cài bằng `pip install vieneu`, không cần API key. Đổi giọng ở `voice.vieneu.voice` (25 giọng có sẵn) hoặc đặt `ref_audio` để nhân bản giọng từ clip 3–8 giây. Mỗi câu được đọc riêng nên pipeline biết chính xác thời điểm từng câu, không cần whisper.
- **Dùng voice AI khác**: đặt `voice.provider: manual`, đưa `script.txt` qua dịch vụ của bạn, lưu thành `projects/<tên>/voice.mp3` rồi chạy lại (lúc này cần `pip install faster-whisper` để lấy timestamp).
- **Tự viết kịch bản**: bỏ sẵn `script.txt` vào project, bước 1 sẽ tự bỏ qua.

## Chỗ cần chỉnh
| File | Chỉnh gì |
|---|---|
| `config/characters/*.yaml` | Bible nhân vật: `vibe` (giọng kể) và `visual` (ngoại hình cố định, chèn vào mọi prompt) |
| `config/style.yaml` | Phong cách ảnh chung |
| `config/settings.yaml` | Model, độ dài cảnh, thời gian chờ, độ phân giải video |
| `config/prompts/*.md` | Prompt gửi LLM để viết kịch bản / mô tả cảnh |
| `flow_extension/selectors.js` | **Mọi** selector giao diện Flow nằm ở đây (gồm `imageMode` để ép chế độ chỉ tạo ảnh) |
| `flow_extension/config.js` | (tuỳ chọn) `BRIDGE_TOKEN` bảo vệ cầu nối localhost — phải khớp `config/settings.yaml` → `flow.token` |

## Kiểm tra
```
python -m unittest tests.test_core     # logic cắt cảnh, dedupe, kiểm tra khớp ảnh, bridge
python tests/e2e_fake.py               # chạy cả pipeline với extension giả + ffmpeg thật
```
