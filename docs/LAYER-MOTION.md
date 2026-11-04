> Chủ repo đã làm rõ: ưu tiên animate trực tiếp từ ảnh đã gen. Mẫu nhân vật vẽ bằng mã của tập 7 là thử nghiệm cũ, không thay yêu cầu này. Luồng image-to-video hiện có tại docs/IMAGE-TO-VIDEO.md; kết quả local đầu tiên chưa đạt mỹ thuật.

# Dựng chuyển động theo lớp và nhịp câu

Cập nhật 04/11/2026. Executor: assistant hiện tại (Codex). Tham chiếu thị giác từ Browser Use, đoạn mở “Lý Do Mất Ngủ” 0:00–0:50 và “Tôi Ghét Hóa Học” 0:00–0:40. Chưa kiểm nghe audio của Tuna. Xem docs/research/tuna-gaming/observations.json.

## Phần đã triển khai

`src/pipeline/layer_motion.py` dựng các lớp image/text/stick_character. Keyframe theo giây cục bộ của cảnh điều khiển vị trí, kích thước, độ hiện, tay, mắt, miệng biểu cảm. Có linear/smooth/hold; hold cho đổi pose và hard cut. Miệng là biểu cảm, chưa phải lip-sync. Không lấy nhân vật/hình/giọng kênh tham chiếu làm tài sản đầu vào.

`scene.motion_plan` trỏ tới JSON trong thư mục tập. Trước dựng sản xuất, adapter bắt buộc scene_id và sources khớp chính xác script_sha256, voice_sha256, scene_sha256; hash cảnh tính từ id/text/start/end bằng scene_hash(). Thời lượng phải phủ cảnh trong sai số một frame. Timeline/source gates hiện hữu vẫn chạy trước adapter. Thay script/voice/mốc thì phải làm mới kế hoạch; không điền approved để lách.

`canvas_width/canvas_height` khai báo hệ tọa độ thiết kế; output 720p/1080p được scale cùng tỷ lệ, không đổi vị trí tương đối hoặc kéo méo aspect. Asset image chỉ được đọc từ trong thư mục tập. Keyframe cần opacity=0 từ đầu nếu muốn giấu lớp tới một cue sau đó; phải tự đặt cue rõ, không suy timestamp từ lời đọc.

`render.require_object_motion: true` được đặt cho tập 7 và template tập mới. Mỗi cảnh phải có motion_plan hoặc animation_video hiện hữu; ảnh tĩnh zoom không được tự coi là animation. Các tập cũ không bị tự chuyển/di chuyển. Số cảnh và nhịp storyboard không giảm. Kế hoạch chuyển động hiện cần tác giả lập cùng storyboard, chưa có bộ tự sinh rig/cutout cho mọi ảnh Flow.

## Mẫu cụ thể

- projects/tap-07-cao-thu-van-di-sai/kich-ban/build-motion-preview.py dựng lại sample.
- kich-ban/motion-preview-plan.json là prototype không voice, cue thủ công; cố ý không có bộ nguồn sản xuất để không được dùng nhầm.
- video/motion-preview-khong-tieng.mp4:12giây/1280×720/30fps/360frame, có di chuyển quân cờ, đổi tay/mặt, chữ reveal, hard cut cận/toàn.
- video/motion-preview-check.json: probe, hash, giải mã và khung hình đã kiểm. Mẫu này chưa chứng minh đồng bộ lời nói hoặc chất lượng ngang kênh tham chiếu.

## Nhịp giọng

`script.delivery_cues` là danh sách cue khớp nguyên văn duy nhất một câu: text, tempo 0.9–1.1, pause_after 0–1.2 giây, note. recording_plan() kiểm cue cũ/trùng và giữ nguyên lời; chính sách/plan hash hiện hữu bảo vệ nguồn. Câu cuối vẫn không chèn khoảng nghỉ cuối thừa.

`s2_voice.apply_tempo()` dùng FFmpeg atempo trên từng clip câu sau tổng hợp, rồi tính lại thời lượng/word interpolation/biên clip từ audio đã xử lý. Không lấy timestamp trước thay tốc độ để dựng. `note` chỉ lưu chỉ dẫn biên tập; provider chưa tự thực hiện ngữ điệu/nhấn chữ/cảm xúc từ note. Tempo và khoảng nghỉ không đồng nghĩa diễn xuất giọng đã tốt. Giữ preset Hải Đăng hiện hành; chưa tạo hoặc kiểm nghe voice tập 7.

## Đường dẫn và giới hạn tích hợp

Các property đầu ra mới và nhánh voice/render/timeline vừa sửa ưu tiên hinh/video/kich-ban cho tập nested; vẫn đọc legacy file đã tồn tại để không tự di chuyển tập đang chạy. Không coi lần sửa này là audit toàn bộ module cũ: nguồn/review/metadata khác còn cần đối chiếu trước sản xuất full episode mới. Chưa chạy toàn pipeline tập 7, chưa có full AV review, cổng model hoặc đăng tải.

Kiểm thử: fixture/synthetic audio/FakeVieneu/local FFmpeg. Không dùng kết quả test để ký đã nghe/duyệt sản phẩm. Bằng chứng cập nhật ở video/motion-preview-check.json.
