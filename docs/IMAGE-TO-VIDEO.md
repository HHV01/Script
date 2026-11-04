# Animate từ ảnh đã gen

Ưu tiên hiện hành theo yêu cầu chủ repo: lấy đúng ảnh cảnh đã có, tạo chuyển động từ ảnh đó; không tự vẽ lại nhân vật để thay ảnh nguồn, không dùng zoom toàn ảnh làm bằng chứng đã animate.

Thử nghiệm thực tế đầu: projects/tap-04-vao-phong-lai-quen/hinh/canh-001.png → video/animation/canh-001-svd-preview.mp4. Local ComfyUI + svd_xt.safetensors,25frame,6fps,1024×576,không cloud credit. GPU là RTX3060. Đây là kết quả một lần sinh, chưa đạt mỹ thuật: xem phiếu cạnh clip. Không suy từ model chạy thành công thành nội dung đạt.

src/pipeline/ai_animation.py đã sửa: mặc định ngang16:9; tên/tệp theo tập/cảnh thay nhãn qwerty cũ; input/output Comfy có thể đặt qua COMFYUI_INPUT_DIR/COMFYUI_OUTPUT_DIR trong thư mục tập; prototype ở video/animation. Lưu prompt_id ngay sau submit, lần chạy tiếp dùng job cũ; trạng thái submit chưa rõ không tự gửi mới. Mã job này chỉ có ý nghĩa với đúng server/history còn giữ, không tạo lại mù khi history mất.

Comfy trả animated WEBP; dùng Pillow giải mã frame thật rồi encode MP4 vì FFmpeg cài trên máy có lỗi đọc animated WEBP. Không tự thêm frame, loop hoặc đảo clip cho đủ cảnh. attach=False mặc định giữ thử nghiệm riêng; attach=True phải có clip đủ dài mới gắn scene. Renderer cũng chặn clip ngắn thay vì loop cho phủ voice.

Chạy mẫu lại bằng kich-ban/thu-animate-anh-san.py chỉ khi worker đúng thư mục input/output sẵn sàng và còn history; kiểm hồ sơ chống lặp trước. Không mở worker trùng. Worker local đã mở cho lần thử phải đối chiếu queue rồi đóng khi xong; không khẳng định chạy nền sau khi kết thúc.

SVD hiện không có prompt điều khiển hành động cụ thể trong workflow này; không hứa nháy mắt/cử động tay chính xác theo voice. Chỉ dùng clip đã kiểm nội dung/nguồn/thời lượng, chưa approved từ metadata. Mẫu 4,17s không phủ được cảnh1 dài11,34s; cần kế hoạch hành động/nhịp voice phù hợp và kiểm thực tế trước sản xuất.
