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

## Cấu hình Paper Collage Documentary
Nguồn tham khảo do người dùng chọn: https://chat.deepseek.com/share/0j2vd5mzzydlm0q4ej (tài liệu PDF 8 trang trong cuộc trò chuyện).

Áp dụng phần sản xuất sau khi đã có kịch bản: bảng beat (phần 6), prompt ảnh (phần 7), Universal Video Prompt (phần 8), ba mẫu thumbnail (phần 9). Phần ý tưởng, viết lời dẫn và tạo voice trong tài liệu không chạy trong app. Không có API hoặc AI sinh nội dung.

- Dự án mới dùng cấu hình collage tiếng Việt: giấy báo/bản đồ cũ, ảnh cắt halftone, thớ giấy thật, điểm nhấn đỏ và vàng mù tạt tiết chế; camera/ánh sáng nhất quán.
- Nhịp mặc định 2,5 giây, ưu tiên dấu câu gần ranh giới, bảo toàn lời kể. Với voice thực tế, mốc vẫn cần căn theo file/SRT. Nếu kịch bản quá ít từ so với thời lượng, beat có thể dài hơn nhịp; xem cảnh báo thay vì giả sử đã khớp.
- Một chủ thể chính khoảng 70%, ít chi tiết hỗ trợ, nền tiết chế; chủ thể và chi tiết có ô nhập riêng cho từng beat. Không có AI tự hiểu hoặc tự chọn chủ thể.
- Nhãn ảnh mặc định không có, nếu nhập thì tối đa 4 từ. Thumbnail có tối đa hai cụm chữ, mỗi cụm tối đa 3 từ. Mô tả đối tượng lặp lại dùng ô nhân vật/vật thể nhất quán do người dùng nhập.
- Nút Nạp cấu hình không thay lời kể hoặc cảnh hiện có. Muốn dùng nhịp mới cho cảnh cũ, bấm chia lại, bản trước vẫn được lưu để phục hồi.
- Copy tất cả và TXT ảnh chỉ gồm prompt đầy đủ, mỗi prompt một đoạn, cách nhau đúng một dòng trống. Không thêm tiêu đề, số beat hoặc timecode. CSV và bảng beat giữ thông tin đối chiếu theo thứ tự.
- Prompt chuyển động dùng chung giữ bố cục ảnh cuối, camera khóa, ráp giấy 0-7 giây và giữ poster sống 7-10 giây. Prompt này chỉ được copy/xuất, không gọi công cụ sinh clip. Không kéo dài beat 2,5 giây thành 10 giây khi dựng.
- Ba thumbnail là mẫu bố cục ghép bằng code từ chủ thể/nhãn người dùng nhập. Không tạo ảnh, không tự bịa nội dung video.

Mô tả phong cách và prompt chuyển động được diễn giải bằng tiếng Việt để chỉnh sửa dễ dàng, không tuyên bố là bản chép nguyên văn tiếng Anh của tài liệu.

## Liên kết Google Flow
Ở bước 1, lưu liên kết dự án Flow riêng rồi dùng nút Mở dự án Flow. Link chỉ lưu trong dự án trên máy, không lưu vào mã nguồn. App không đọc cookie hoặc mật khẩu Google, không tự gửi prompt hay bấm tạo nội dung. Đây là liên kết mở dự án; tự điền/tự gửi hàng loạt từ app chưa được triển khai. Trong phiên hỗ trợ có thể thao tác Flow bằng trình duyệt đã đăng nhập, theo yêu cầu cụ thể của người dùng.
