# Video Studio

Ứng dụng chạy trên máy: nhập kịch bản → chia cảnh → ghép prompt bằng mẫu → căn voice/SRT → ghép ảnh/clip thành video. Không gọi AI, không cần API key.

## Chạy
Bấm start_video_studio.bat hoặc npm start. Mở http://localhost:3211. Cần Node.js 22 trở lên.

## Các bước
1. Nhập kịch bản, thời lượng voice, nhịp cảnh và mẫu prompt.
2. Bấm Chia cảnh bằng code. Mỗi cảnh nhận một phần lời kể, prompt được ghép ngay từ mẫu. Có thể sửa từng prompt hoặc áp lại mẫu cho riêng một cảnh.
3. Tải voice để căn ngắt nghỉ trong trình duyệt, nhập SRT, hoặc căn ước lượng theo tổng thời lượng.
4. Nhập ảnh/clip theo số cảnh, bấm Dựng MP4 1080p. Xuất TXT/CSV/SRT/JSON khi cần.

## Mẫu prompt
Các biến hỗ trợ: {loi_ke}, {phong_cach}, {nhan_vat}, {so_canh}, {bat_dau}, {ket_thuc}, {thoi_luong}. Mẫu bắt buộc có {loi_ke}. Code thay biến nguyên văn; không sáng tạo hình ảnh hay suy luận nội dung.

Ví dụ: Minh họa: {loi_ke}. Phong cách {phong_cach}, nhân vật {nhan_vat}, khung 16:9, không chèn chữ.

Đổi mẫu chung chỉ cập nhật prompt ghép bằng code, giữ prompt đã sửa tay. Nút Áp mẫu cho cảnh này thay prompt của riêng cảnh được chọn. Khi căn thời gian, biến mốc thời gian của prompt ghép bằng code được cập nhật.

## Dữ liệu và công cụ
Dữ liệu/media nằm trong .video-studio-data/, không đưa vào Git. App không đọc khóa, cấu hình AI hoặc dữ liệu kênh. File ảnh/clip và voice do người dùng cung cấp; app tự nối theo thời lượng cảnh bằng FFmpeg. Clone mới: npm ci, cài FFmpeg/ffprobe trong PATH hoặc tools/ffmpeg/bin/. Cảnh HTML cần Chrome.

## Kiểm thử
npm test: mẫu prompt, giữ sửa tay, phủ lời kể, căn voice, server và dựng MP4 thật khi có FFmpeg. Không gọi dịch vụ AI.
