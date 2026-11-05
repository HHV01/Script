# AI mở repo: đọc trang này trước

1. Đọc `AGENTS.md`, `.studio/manager/OPERATIONS.md`, `config/channel-direction.yaml`, `config/team-operations.yaml`. Chỉ dẫn mới của chủ repo ưu tiên ghi chú cũ. Không giả định một agent khác đã duyệt nếu chưa có kết quả thực tế.
2. Dùng môi trường Python hiện có, chạy chẩn đoán **không tạo nội dung**:

   ```powershell
   .\.venv\Scripts\python.exe run.py doctor --json
   .\.venv\Scripts\python.exe run.py doctor memory-long-01 --json
   ```

   Nếu không có `.venv`, theo README để cài. Có thể thay tiền tố bằng `python` nếu đã chọn đúng môi trường. Đọc lỗi và đường dẫn trong JSON; không in secret để kiểm tra.
3. Đọc `projects/<tên>/project.yaml`, các đầu ra và trạng thái thực tế. Đối chiếu hash/phiếu khi có. Không coi tệp tồn tại là đạt chất lượng; không tạo lại cảnh, giọng hoặc project chỉ vì chưa biết cách tiếp tục.
4. Kiểm tra app/worker trước khi mở worker mới; không tự bật lịch manager hoặc hàng đợi cũ.
5. Ảnh cung cấp thủ công trong `hinh/`, tên theo ID cảnh. Chạy `collect` để kiểm tệp cục bộ; code auto Flow đã gỡ. Giữ nguyên profile, ảnh và hồ sơ Flow cũ để đối chiếu.
6. Chỉ tiếp tục bước còn thiếu hoặc lỗi. Lệnh `run --only <bước>` giới hạn một bước; `--from` chạy nhiều bước tiếp theo và có thể dùng API. `--force` có thể ghi đè dữ liệu. Không chạy toàn pipeline để xem trạng thái.
7. Mặc định không xuất bản. `run ... --upload` là thao tác xuất bản rõ ràng, chỉ sau các cổng nguồn/kịch bản/hình/tiếng/phụ đề và hash bản cuối. Kiểm tra ledger/YouTube nếu trạng thái upload chưa rõ; không tạo receipt giả hoặc đăng trùng.

## Hồ sơ bàn giao tối thiểu

Ghi executor thực tế, lệnh đã chạy, kết quả/tệp làm bằng chứng, phần chưa xác minh, lỗi còn lại và bước tiếp theo. Phân biệt chẩn đoán offline, giao diện Flow sẵn sàng, gửi prompt, tải ảnh đúng cảnh và duyệt ảnh: đây là các kết quả khác nhau. Không khẳng định chạy nền sau khi kết thúc nếu không có worker/lịch đã kiểm tra.

Định hướng hiện tại là khoa học đời thường, video dài 16:9, nhân vật `stick-orange` trên nền giấy kem. Không phục hồi Shorts/chủ đề hoặc mẫu hình đã bị bác từ lịch sử chat. Cấu hình trong repo và chỉ dẫn mới là nguồn hiện hành.

## Lưu tệp tập mới

Theo quy tắc chủ repo tại AGENTS.md: mỗi tập một thư mục `projects/tap-XX-ten-chu-de/`, bên trong `hinh/`, `video/`, `kich-ban/`; cấu hình/trạng thái ở gốc tập. Voice nằm trong `video/`. Chỉ giữ một bộ chính trong repo. Kiểm tương thích đường dẫn pipeline trước sản xuất; không rải tệp hoặc tạo bản sao ngoài repo.

## Chuyển động và nhịp câu (04/11/2026)

Đọc [LAYER-MOTION.md](LAYER-MOTION.md) khi làm tập 7 hoặc tập mới từ template. require_object_motion chặn zoom ảnh tĩnh thay animation; kế hoạch từng lớp phải bám đúng hash script/voice/cảnh. Mẫu không tiếng tập 7 là prototype cue thủ công, không phải sản phẩm đã đồng bộ hoặc đã qua duyệt giọng.
