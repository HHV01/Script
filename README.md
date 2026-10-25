# Video Studio

App riêng: nhập kịch bản có sẵn → tạo prompt → căn voice/SRT → nhập hình → dựng MP4.

## Chạy
Bấm **start_video_studio.bat** hoặc chạy **npm start**, mở http://localhost:3211. Cần Node.js 22 trở lên.
Repo, dữ liệu và cấu hình AI riêng; chạy được khi repo Video cũ không mở.

## Sử dụng
1. Tạo video mới và dán đúng bản lời kể đã dùng để thu voice.
2. Chọn phong cách và bible nhân vật nếu cần, tạo prompt bằng tiếng Việt.
3. Căn thời lượng voice hoặc nhập SRT. Căn theo số từ chỉ là ước lượng; SRT cho mốc từng câu.
4. Duyệt prompt, nhập ảnh/clip theo số cảnh.
5. Dựng MP4 1080p, xuất SRT/CSV/JSON.

**Chép dự án từ Tích Studio** tạo ID mới và sao chép media, không sửa bản gốc. VIDEO_SOURCE_DIR trong .env trỏ tới kho Studio cũ trên máy này. Bỏ đường dẫn này không ảnh hưởng tạo dự án mới.

## Dữ liệu và phạm vi
- .video-studio-data/: dữ liệu, media, bản dựng và khóa AI riêng, được ignore.
- .env: cấu hình riêng trên máy, được ignore. Khóa AI đã dùng được chép riêng; không mang khóa YouTube.
- Không chép lịch sử Git, công cụ lượt xem, profile trình duyệt hay outputs cũ.
- Dùng các module nghiệp vụ sao chép từ Studio để giữ hành vi nhân vật, chia cảnh và xuất prompt. Một số hàm nền dùng chung vẫn có trong mã; giao diện chỉ tập trung sản xuất video.
- Wan cần ComfyUI/model. Nhận diện audio local cần Python/Whisper; nhập SRT không cần Python.

## Cài từ clone
Chạy **npm ci**. Cài FFmpeg/ffprobe vào PATH hoặc tools/ffmpeg/bin/. Chrome/Chromium cần cho cảnh HTML. Công cụ lớn, dữ liệu và khóa không được commit.

## Kiểm tra
- **npm test**: nghiệp vụ, prompt, voice/SRT, nhân vật, dịch, HTTP và quản lý job; không gọi AI thật.
- **npm run test:app**: test app riêng.
- **npm run test:render**: dựng thật, cần FFmpeg/Chrome. Cảnh HTML đã gặp timeout trên máy hiện tại, chưa xác nhận đạt.
- UI Chrome tự động bật bằng VIDEO_TEST_UI=1; giao diện đã được thử trực tiếp khi tách app.

Nguồn tách: Video, nhánh fix/review-2026-10 tại 319e21f và các thay đổi ứng dụng hiện có trên máy. Không sao chép lịch sử Git cũ.
