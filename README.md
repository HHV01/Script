# Xưởng video khoa học về chính bạn

Video dài ngang **16:9** về cơ thể, cảm giác, trí nhớ và hành vi; giọng hài thông minh kháy nhẹ, nhân vật `stick-orange`, nền giấy kem. Định hướng chuẩn: `config/channel-direction.yaml`. Tuân thủ [AGENTS.md](AGENTS.md); tên An, Minh, Mai, Gạo là nhãn công việc, không mặc định là người hay agent độc lập.

## Bắt đầu trên Windows

Mở PowerShell tại thư mục repo. Nếu đã có môi trường đang chạy, giữ lại; không ghi đè `.env`, OAuth hoặc profile Google Flow.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe run.py doctor --json
.\.venv\Scripts\python.exe run.py studio
```

Mở http://127.0.0.1:8787. Python 3.12 là ví dụ; nếu đã dùng Python tương thích thì dùng môi trường đó. Các lệnh sau dùng cùng Python trong `.venv`.

Để nối Flow, cài riêng Playwright; không cần tải mô hình giọng chỉ để mở trình duyệt:

```powershell
.\.venv\Scripts\python.exe -m pip install "playwright>=1.49,<2"
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe run.py doctor memory-long-01 --json
.\.venv\Scripts\python.exe run.py flow memory-long-01 --action open --timeout 60
```

Đăng nhập trong cửa sổ vừa mở, mở đúng project Flow, rồi lưu URL vào `flow_url` của project. **Chrome thường đã đăng nhập không đồng nghĩa profile Flow đã đăng nhập.** Quay lại terminal nhấn Enter để đóng helper, giải phóng profile trước lệnh tiếp theo.

- [Mở Flow, kiểm tra kết nối và thử một ảnh](docs/FLOW.md)
- [Bàn giao cho AI khác](docs/AI-START-HERE.md)
- [Quy trình sản xuất và kiểm duyệt](HUONG-DAN.md)

## Cấu hình và an toàn vận hành

Chỉ tạo `.env` từ `.env.example` khi chưa có. Key LLM/YouTube, OAuth và model phụ thuộc bước chạy; xem kết quả `doctor` và cấu hình trong `config/settings.yaml`. Cài toàn bộ pipeline bằng `pip install -r requirements.txt` khi cần sản xuất; VieNeu có thể tải model lần đầu. FFmpeg và ffprobe cần cho bước dựng/kiểm tra media.

`doctor` kiểm tra cục bộ, không tạo ảnh, không gọi provider để xác minh quota hoặc đăng nhập. `flow check` mở trình duyệt và kiểm tra giao diện, không gửi prompt. `flow generate-one` có thể tiêu credit Flow, chỉ dùng khi chủ động muốn thử tạo một cảnh.

Lệnh sản xuất mặc định không upload. `publish` chỉ chuẩn bị tiêu đề/mô tả/tag; xuất bản cần yêu cầu rõ bằng `run ... --upload`, OAuth và đầy đủ cổng duyệt. Không thử upload lại video đã có trong hồ sơ chống trùng. Một tệp hoặc bài kiểm thử đạt không chứng minh chất lượng nội dung hay độ hấp dẫn.

Không commit/chia sẻ `.env`, token hoặc `.flow-profile`. Đăng nhập có thể hết hạn. Chỉ một worker dùng profile tại một thời điểm; không bật lại queue/brief cũ khi bàn giao.

Trên Windows có thể nhấp đúp `START.cmd` để chọn mở xưởng, chẩn đoán, đăng nhập Flow, kiểm tra hoặc tạo đúng một cảnh. Menu dùng cùng CLI; không tự cài, không tự đăng video.
