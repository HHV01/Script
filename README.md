# Video Studio

Ứng dụng độc lập, trung lập để làm video từ kịch bản có sẵn. Không nạp nội dung, kênh hay nhân vật mẫu.

## Chạy
Bấm start_video_studio.bat hoặc npm start. Mở http://localhost:3211. Node.js 22 trở lên.

## Quy trình
1. Nhập kịch bản, thời lượng voice và nhịp cảnh; tự nhập phong cách/nhân vật nếu cần.
2. Chia cảnh bằng code, tạo prompt tiếng Việt theo lô 4 khi bấm nút. Lưu từng lô để tiếp tục nếu lỗi.
3. Tải voice để phân tích ngắt nghỉ tại trình duyệt hoặc nhập SRT; có thể căn ước lượng theo tổng số giây.
4. Nhập ảnh/clip cho từng cảnh rồi dựng MP4 1080p. Xuất prompt TXT/CSV và phụ đề SRT.

## Dữ liệu và công cụ
Dự án nằm trong .video-studio-data/workspace.json. Media và khóa API ở cùng kho riêng, được ignore. Không có kết nối đến repo hoặc dữ liệu của ứng dụng khác.
Clone mới: npm ci, cài FFmpeg/ffprobe trong PATH hoặc tools/ffmpeg/bin/. Trên máy này FFmpeg đã có. Cảnh HTML cần Chrome/Chromium; clip có sẵn có thể nhập trực tiếp. Không tự tạo ảnh hoặc voice.

## Test
npm test kiểm tra workflow trung lập, phủ lời kể, lô/resume, căn thời gian, server và dựng ảnh + voice thành MP4 thật khi có FFmpeg. Không gọi AI thật. Phân tích ngắt nghỉ có test âm thanh mô phỏng. AI thật và dựng HTML chưa được xác nhận trong đợt này.
