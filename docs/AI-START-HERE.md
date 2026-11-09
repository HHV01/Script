# AI mở repo: đọc trang này trước

## What If — project riêng theo chủ repo ngày 09/11/2026

Đọc [projects/What if/README.md](../projects/What%20if/README.md) và [HANDOFF.md](../projects/What%20if/kich-ban/HANDOFF.md) khi làm nội dung What If/Mây Mù. Kịch bản hiện tại là “Nếu AI hiện hóa đơn điện sau mỗi câu trả lời?”. Phần hướng Soi Sáng đang là đề xuất, chưa có ảnh thử/chốt; ba prompt thử A/C/E đã viết tại `projects/What if/hinh/prompts-test-ace.txt`, chưa tạo ảnh. Nghiên cứu YouTube và mẫu hình Soi Sáng đã chuyển vào `projects/What if/kich-ban/nghien-cuu/`, không còn ở `docs/research/`. Không áp hai bố cục bàn cờ tập 7 sang video này. Đường dẫn có khoảng trắng do chủ repo chỉ định, là hồ sơ biên tập; CLI cũ chưa hỗ trợ tên này. Không tự tạo project tên khác để lách đường dẫn.


## Tập 7 — đã dừng theo chủ repo ngày 09/11/2026

Chủ repo quyết định bỏ tập 7 và chuyển sang tập khác. Thư mục `projects/tap-07-cao-thu-van-di-sai` **không còn trên đĩa**; bản đã xoá nằm trong Thùng rác Windows. Trước khi xoá, trạng thái thực là 8/247 ảnh (`scene_001`–`scene_008`), voice 873,9 giây, kịch bản 3342 từ; không có video dựng và không đăng gì. Không dùng lại bố cục A/B bàn cờ của tập 7 cho nội dung khác nếu chủ repo chưa yêu cầu.

Module độc lập tại [flow_gen/README.md](../flow_gen/README.md) được thêm theo yêu cầu chủ repo; code cũ vẫn giữ. Module đã chạy thật cho tập 7 qua CDP với profile ngoài repo, x1/16:9; không suy rằng phiên còn đăng nhập hoặc worker đang chạy. Bước 5 ở phần hướng dẫn cũ dưới đây mô tả CLI cũ, không bắt agent dùng nó thay module mới. Bộ gửi mới giữ nguyên image_prompt; cấu hình tham chiếu không tự upload ảnh.

Dữ liệu tập và ảnh trong `projects/` đang bị Git bỏ qua; agent clone repo sẽ không có hồ sơ What If trên máy này.


1. Đọc `AGENTS.md`, `.studio/manager/OPERATIONS.md`, `config/channel-direction.yaml`, `config/team-operations.yaml`. Chỉ dẫn mới của chủ repo ưu tiên ghi chú cũ. Không giả định một agent khác đã duyệt nếu chưa có kết quả thực tế.
2. Dùng môi trường Python hiện có, chạy chẩn đoán **không tạo nội dung**:

   ```powershell
   .\.venv\Scripts\python.exe run.py doctor --json
   .\.venv\Scripts\python.exe run.py doctor memory-long-01 --json
   ```

   Nếu không có `.venv`, theo README để cài. Có thể thay tiền tố bằng `python` nếu đã chọn đúng môi trường. Đọc lỗi và đường dẫn trong JSON; không in secret để kiểm tra.
3. Đọc `projects/<tên>/project.yaml`, các đầu ra và trạng thái thực tế. Đối chiếu hash/phiếu khi có. Không coi tệp tồn tại là đạt chất lượng; không tạo lại cảnh, giọng hoặc project chỉ vì chưa biết cách tiếp tục.
4. Kiểm tra app/worker trước khi mở worker mới. Không tự bật lịch manager. Giữ `.env`, OAuth, `.flow-profile`, ảnh/giọng đã có và hồ sơ chống trùng. Không xóa profile khi gặp khóa hoặc lỗi đăng nhập.
5. Với Flow, dùng duy nhất luồng mặc định tại [FLOW.md](FLOW.md): Playwright + profile riêng `.flow-profile`, `flow open`, đăng nhập trực tiếp nếu cần, `flow check`, rồi mới `generate-one` khi được phép tiêu credit. Không bắt người dùng cài extension/CDP làm bước mặc định. Không lưu mật khẩu Google vào `.env`.
6. Chỉ tiếp tục bước còn thiếu hoặc lỗi. Lệnh `run --only <bước>` giới hạn một bước; `--from` chạy nhiều bước tiếp theo và có thể dùng API. `--force` có thể ghi đè dữ liệu. Không chạy toàn pipeline để xem trạng thái.
7. Mặc định không xuất bản. `run ... --upload` là thao tác xuất bản rõ ràng, chỉ sau các cổng nguồn/kịch bản/hình/tiếng/phụ đề và hash bản cuối. Kiểm tra ledger/YouTube nếu trạng thái upload chưa rõ; không tạo receipt giả hoặc đăng trùng.

## Hồ sơ bàn giao tối thiểu

Ghi executor thực tế, lệnh đã chạy, kết quả/tệp làm bằng chứng, phần chưa xác minh, lỗi còn lại và bước tiếp theo. Phân biệt chẩn đoán offline, giao diện Flow sẵn sàng, gửi prompt, tải ảnh đúng cảnh và duyệt ảnh: đây là các kết quả khác nhau. Không khẳng định chạy nền sau khi kết thúc nếu không có worker/lịch đã kiểm tra.

Định hướng hiện tại là khoa học đời thường, video dài 16:9, nhân vật `stick-orange` trên nền giấy kem. Không phục hồi Shorts/chủ đề hoặc mẫu hình đã bị bác từ lịch sử chat. Cấu hình trong repo và chỉ dẫn mới là nguồn hiện hành.

## Lưu tệp tập mới

Theo quy tắc chủ repo tại AGENTS.md: mỗi tập một thư mục `projects/tap-XX-ten-chu-de/`, bên trong `hinh/`, `video/`, `kich-ban/`; cấu hình/trạng thái ở gốc tập. Voice nằm trong `video/`. Chỉ giữ một bộ chính trong repo. Kiểm tương thích đường dẫn pipeline trước sản xuất; không rải tệp hoặc tạo bản sao ngoài repo.

## Chuyển động và nhịp câu (04/11/2026)

Đọc [LAYER-MOTION.md](LAYER-MOTION.md) khi làm tập 7 hoặc tập mới từ template. require_object_motion chặn zoom ảnh tĩnh thay animation; kế hoạch từng lớp phải bám đúng hash script/voice/cảnh. Mẫu không tiếng tập 7 là prototype cue thủ công, không phải sản phẩm đã đồng bộ hoặc đã qua duyệt giọng.
