# Xưởng video khoa học đời thường

Công cụ Python và giao diện web cục bộ để làm video tiếng Việt về cơ thể, cảm giác, trí nhớ và hành vi. Luồng hiện có: kịch bản → duyệt văn bản → giọng đọc → phân cảnh → prompt → ảnh cung cấp thủ công → dựng → metadata và kiểm tra.

Định hướng hiện tại: video ngang **16:9**, nhân vật `stick-orange`, nền giấy kem. Xem [cấu hình định hướng](config/channel-direction.yaml) và [quy tắc repo](AGENTS.md). Đây là công cụ hỗ trợ sản xuất; chạy xong một bước không đồng nghĩa nội dung đã được xem, nghe hoặc duyệt chất lượng.

## Cài đặt trên Windows

Mở PowerShell trong thư mục repo. Cần Python tương thích với các thư viện sẽ dùng; lệnh dưới dùng Python 3.12. Giữ môi trường đang hoạt động nếu đã có.

```powershell
git clone https://github.com/HHV01/Script.git
cd Script
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe run.py doctor --json
.\.venv\Scripts\python.exe run.py studio
```

Mở [giao diện xưởng](http://127.0.0.1:8787). `requirements-local.txt` chỉ cài thư viện cho giao diện cục bộ, không gồm toàn bộ công cụ tạo nội dung. Có thể nhấp đúp `START.cmd` để mở menu; menu không tự cài thư viện và không tự đăng video.

Khi cần sản xuất, cài thêm trong cùng môi trường:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

- **LLM:** provider và model theo `src/pipeline/llm.py`, `config/settings.yaml`; cấu hình key tương ứng trong `.env`. Cấu hình mặc định dùng OpenCode, không phải tài khoản ChatGPT.
- **Voice:** mặc định VieNeu `v3turbo`, giọng Hải Đăng. Lần đầu có thể tải model; tốc độ phụ thuộc máy. Chế độ audio thủ công cần thêm `faster-whisper` để căn lời đọc.
- **Media:** cần FFmpeg và ffprobe trong PATH hoặc `tools/ffmpeg/bin/`.

Chỉ tạo `.env` từ [.env.example](.env.example) nếu chưa có; không ghi đè key đang dùng. `YOUTUBE_API_KEY` dùng cho nghiên cứu dữ liệu công khai; quyền Analytics/upload dùng OAuth riêng. `doctor` kiểm tra môi trường cục bộ, không xác minh đăng nhập, quota hoặc quyền truy cập provider.

## Tạo và lưu một tập

Bản Git chỉ chứa mã nguồn, cấu hình, tài liệu và template. Các tập thực tế trong `projects/` đang được `.gitignore` loại trừ, nên clone repo không mang theo ảnh, voice hay video đã làm trên máy khác.

Ví dụ tạo tập mới, đổi số và tên để không trùng tập hiện có:

```powershell
.\.venv\Scripts\python.exe run.py new tap-08-ten-chu-de
.\.venv\Scripts\python.exe run.py doctor tap-08-ten-chu-de --json
```

Lệnh `new` sao chép template. Sửa `project.yaml` để điền chủ đề, đối tượng, thời lượng mục tiêu, nguồn; thêm `README.md` ghi bản hiện hành, trạng thái thực và việc còn thiếu. Mỗi tập có một thư mục chính:

```text
projects/tap-08-ten-chu-de/
  project.yaml
  README.md
  hinh/       # ảnh, prompt và nguồn ảnh
  video/      # voice, mốc giọng, phụ đề, clip và bản xuất
  kich-ban/   # nguồn, kịch bản, phân cảnh, phiếu và metadata
```

Không tạo bản song song ngoài repo. Một số tập cũ còn bố cục phẳng; mã có hỗ trợ đọc đường dẫn cũ, không tự di chuyển chúng khi chưa kiểm phụ thuộc.

## Chạy từng bước

Các lệnh sau là ví dụ thao tác, không phải chứng nhận các cổng đầu vào đã đạt:

```powershell
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only script
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only review
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only voice
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only scenes
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only prompts
```

Kiểm nguồn và nội dung văn bản trước khi thu; nghe voice và đối chiếu phân cảnh trước khi tạo ảnh. Model review, ASR và mốc từ không thay thế kiểm tra nghe/xem thực tế. Công cụ tạo và ghép voice không tự cung cấp khả năng nghe âm thanh cho assistant đang điều khiển repo.

`--only` giới hạn một bước; `--from` chạy bước đó và các bước sau. `run` không có hai tùy chọn này sẽ chạy cả luồng. `--force` có thể ghi đè kết quả hoặc gọi dịch vụ có phí; không dùng để thử trạng thái.

## Cung cấp ảnh thủ công

Code auto Google Flow, extension và Playwright đã được gỡ. Tạo ảnh bằng công cụ bên ngoài, đặt từng ảnh vào `hinh/` theo ID cảnh: `canh-001.png`, `canh-002.png`… (cũng hỗ trợ `001.png`). Giữ đủ ảnh để phủ đúng nhịp video.

Chạy `python run.py run tap-08-ten-chu-de --only collect` bằng Python của môi trường đã cài. Bước này chỉ kiểm ảnh cục bộ và ghi tên ảnh vào phân cảnh; thiếu/hỏng sẽ dừng, không tự tạo hoặc tải ảnh. Profile và hồ sơ Flow cũ được giữ để đối chiếu.

## Chuyển động, dựng và xuất bản

Ưu tiên hiện hành là animate từ đúng ảnh cảnh đã tạo. Adapter ComfyUI/SVD là thử nghiệm riêng, cần cài worker/model; không nằm trong cài đặt cơ bản và không tự chạy thành công chỉ bằng lệnh `render`. Mẫu SVD đầu tiên bị đánh giá chưa đạt do biến dạng mặt/tay. Xem [image-to-video](docs/IMAGE-TO-VIDEO.md).

Template bật `render.require_object_motion: true`, nên renderer chặn việc dùng ảnh tĩnh làm phương án thay thế khi thiếu chuyển động phù hợp. Phần dựng theo lớp là prototype khác; xem [giới hạn và điều kiện dùng](docs/LAYER-MOTION.md). Cần chuẩn bị đầu vào chuyển động hợp lệ và kiểm nội dung trước khi dựng.

```powershell
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only render
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only publish
.\.venv\Scripts\python.exe run.py run tap-08-ten-chu-de --only qc
```

`publish` chuẩn bị tiêu đề, mô tả và tag. **Lệnh sản xuất mặc định không upload**, kể cả cấu hình auto-upload cũ. Chỉ thêm `--upload` khi đã có yêu cầu đăng rõ ràng, OAuth đúng kênh và đủ các cổng kiểm duyệt. Kiểm tra hồ sơ upload nếu kết quả chưa rõ để tránh đăng trùng.

FFprobe, kiểm thử phần mềm và tệp xuất tồn tại chỉ chứng minh phần kỹ thuật tương ứng; không chứng minh giọng đọc, hình ảnh hoặc nội dung hấp dẫn. Không hứa lượt xem/đăng ký.

## Tài liệu và kiểm thử

- [Quy trình sản xuất, kiểm duyệt](HUONG-DAN.md)
- [AI tiếp quản repo](docs/AI-START-HERE.md)
- [Quy tắc trung thực và lưu tệp](AGENTS.md)

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Một số bài kiểm thử cần FFmpeg, trình duyệt hoặc kết nối server cục bộ. Kết quả test không chứng nhận nội dung của từng tập.

Không commit/chia sẻ `.env`, token OAuth hoặc `.flow-profile`. Manager mặc định tắt; mở giao diện không đồng nghĩa đã có worker hoặc lịch tự vận hành.
