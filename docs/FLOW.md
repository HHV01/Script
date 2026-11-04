# Google Flow: một cách mở và tạo ảnh

Luồng mặc định: **Playwright mở browser có profile riêng `.flow-profile`**. Không cần extension hay cổng CDP. Browser có thể dùng Chrome đã cài, nhưng dữ liệu đăng nhập vẫn thuộc profile riêng, khác cửa sổ Chrome cá nhân.

Các ví dụ chạy từ gốc repo, dùng Python của môi trường đã cài theo README. Thay `memory-long-01` bằng tên project muốn thao tác; không thử tạo lại ảnh của project đã xong chỉ để kiểm tra kết nối.

## 1. Chẩn đoán cục bộ

```powershell
.\.venv\Scripts\python.exe run.py doctor memory-long-01 --json
```

Lệnh không gửi prompt, không xác minh tài khoản/quota từ xa. Xử lý lỗi môi trường/cấu hình trước. Cài Playwright nếu thiếu:

```powershell
.\.venv\Scripts\python.exe -m pip install "playwright>=1.49,<2"
.\.venv\Scripts\python.exe -m playwright install chromium
```

Trong `config/settings.yaml`, mặc định `flow.backend: playwright`, `headless: false`, `profile_dir: .flow-profile`, `cdp_url: ''`. Nếu `executable_path` trỏ tới Chrome không tồn tại, sửa sang đường dẫn Chrome đúng hoặc để chuỗi rỗng để tự tìm Chrome/Edge đã cài hoặc Chromium của Playwright. Không trỏ profile tới dữ liệu Chrome cá nhân đang mở.

## 2. Mở và đăng nhập

```powershell
.\.venv\Scripts\python.exe run.py flow memory-long-01 --action open --timeout 60
```

Trong cửa sổ helper vừa mở: đăng nhập Google nếu được hỏi, mở/tạo project Google Flow, chọn chế độ tạo ảnh. Helper tự lưu URL project sau khi bạn nhấn Enter; cũng có thể sửa `flow_url` trong `projects/memory-long-01/project.yaml`. URL phải thuộc Google Flow HTTPS; không dán URL trang đăng nhập OAuth. Quay lại terminal nhấn Enter để đóng helper và giải phóng profile trước lệnh tiếp theo. Có thể tăng timeout nếu cần thời gian đăng nhập.

Profile lưu phiên cục bộ để tái sử dụng; Google vẫn có thể yêu cầu đăng nhập/xác minh lại. Không lưu mật khẩu vào `.env`, không gửi profile hoặc cookie cho AI khác.

## 3. Kiểm tra trước khi dùng credit

```powershell
.\.venv\Scripts\python.exe run.py flow memory-long-01 --action check --timeout 60
```

Lệnh kiểm tra giao diện/prompt có sẵn, không gửi yêu cầu tạo ảnh. Kết nối thành công chưa chứng minh ảnh sẽ sinh đúng hay đủ credit. Nếu sai project, sửa `flow_url`; không tiếp tục vào project khác chỉ vì có ô prompt.

## 4. Chỉ thử một cảnh

Khi đã kiểm kịch bản, giọng, phân cảnh và prompt, chủ động yêu cầu thử một ảnh:

```powershell
.\.venv\Scripts\python.exe run.py flow ten_video --action generate-one --scene 1 --timeout 60
```

`generate-one` chỉ xử lý cảnh được chọn: giữ ảnh cục bộ đã có, ưu tiên khôi phục kết quả Flow đã nhận diện trước khi gửi mới. Khi phải gửi prompt, lệnh **có thể tiêu credit Flow**. Kiểm tra đầu ra và ảnh thực tế đúng cảnh trước khi chạy nhiều cảnh. Trạng thái job chưa rõ phải dừng để kiểm tra gallery; không lặp yêu cầu khi chưa rõ lần trước đã được gửi hay chưa. Chỉ dùng `--force` sau khi kiểm tra và chủ động chấp nhận gửi lại, không dùng như cách sửa lỗi mặc định. Một ảnh sinh ra không phải chứng nhận mỹ thuật, đúng nhân vật hoặc khớp lời đọc.

## Gỡ lỗi theo dấu hiệu

| Dấu hiệu | Xử lý |
|---|---|
| Yêu cầu đăng nhập | Dùng `flow open`, đăng nhập trong chính profile helper; Chrome cá nhân không thay thế được phiên này. |
| Trang chủ hoặc không có ô prompt | Mở đúng project/chế độ ảnh, lưu URL project, chạy lại `check`. |
| Profile bị khóa/browser đang dùng | Đóng helper/worker cũ sử dụng `.flow-profile`, kiểm tra đã dừng rồi mới mở lại; không xóa profile hay khóa một cách mù quáng. |
| Không tìm thấy browser | Kiểm tra `executable_path` hoặc cài Chromium bằng lệnh ở trên. |
| Không tìm thấy selector/nút tạo | Có thể Flow đổi giao diện/ngôn ngữ. Giữ lỗi và quan sát UI, sửa selector rồi kiểm tra lại; không gửi prompt liên tục. |
| Timeout/mạng/proxy | Kiểm tra kết nối Google, proxy của môi trường và quyền truy cập mạng. Tăng timeout chỉ khi biết trang đang tải; không chuyển tài khoản/provider âm thầm. |
| Đủ kết nối nhưng tạo lỗi/quota | Đọc lỗi thực tế trong Flow, không gọi là thành công; không retry hàng loạt. |

Chỉ một helper/worker sử dụng profile tại một thời điểm. Quy trình này là hướng dẫn thao tác; kiểm thử phần mềm không chứng minh tài khoản Flow thực tế đã đăng nhập hay tạo ảnh thành công.

## Số ảnh mặc định: x1 luôn luôn

Theo yêu cầu chủ repo, bộ điều khiển kiểm tra trước mỗi lần submit: mở Cài đặt tác nhân, tìm đúng mục **Chế độ mặc định của tính năng tạo hình ảnh**, chọn x1, xác nhận trạng thái radio, bấm Lưu và đợi bảng đóng. Dùng chung cho Playwright và extension qua `prepare_submit`. Không có tùy chọn x2–x4 trong pipeline. Nếu mục/điều khiển/trạng thái không xác định được thì chặn trước gửi. Không thay cài đặt xác nhận trước khi tạo hoặc mục video. Mỗi cảnh vẫn cần ảnh riêng theo storyboard; x1 là số biến thể mỗi lượt, không phải giảm số ảnh toàn video.

Đã kiểm thao tác lưu rồi mở lại trên Flow thật project sleep-long-03 ngày 03/11/2026, x1 vẫn được chọn; chưa gửi prompt thử gen. Bằng chứng: `projects/sleep-long-03/hinh/flow-x1-verified.json` và ảnh cạnh tệp. Fixture kiểm x4/x2 chuyển về x1, giữ video x4 và lựa chọn xác nhận; thiếu điều khiển thì không submit. Giao diện Flow đổi có thể cần cập nhật selector, không coi quy tắc này là bảo đảm Google luôn trả đúng số ảnh.

## Giảm thời gian chờ của bộ điều khiển (03/11/2026)

- Playwright không còn nghỉ cố định 3 giây và chụp/ghi trang sau mọi lần gửi. Muốn lưu chẩn đoán: đặt `flow.playwright.debug_artifacts: true`; tệp nằm trong thư mục ảnh của tập.
- Sau khi cuộn gallery, chờ hai khung layout thay vì nghỉ cố định 1,5 giây. Bộ đợi kiểm tra mỗi 250 ms, yêu cầu ảnh tải xong và danh sách khóa ổn định 1,5 giây; không coi placeholder là ảnh hoàn tất. Không quét toàn bộ DOM để tìm vùng cuộn ở mỗi vòng.
- `flow.delay_seconds` mặc định 1–2 giây, chỉ áp dụng giữa hai lần tạo mới; thời gian tải ảnh được tính vào khoảng nghỉ. Không nghỉ sau cảnh cuối hoặc giữa các lần chỉ tải lại ảnh đã có. Có thể tăng lại nếu phiên Flow cần khoảng nghỉ lớn hơn; không tự thử lại khi lỗi/quota/unusual activity.
- Nhật ký `flow-attempts/<id>.json` ghi `elapsed_seconds` và `operation` cho từng cảnh xử lý thành công. Đây là thời gian xử lý cục bộ cả tạo/tải/chờ, không phải phép đo riêng thời gian máy chủ Google. Với tập cấu trúc mới, nhật ký nằm trong `hinh/flow-attempts`; vẫn đọc nhật ký cũ ở gốc để không gửi trùng.

Vẫn tạo tuần tự trong một profile, vì bộ nhận diện hiện gắn ảnh mới trong gallery với lần gửi đang chờ. Gửi nhiều prompt song song bằng cơ chế này có thể gắn nhầm ảnh với cảnh. Các thay đổi trên giảm chờ phụ; không cam kết thời gian sinh ảnh của Google hay tổng thời gian một tập. Kiểm thử fixture không xác minh tốc độ hoặc giới hạn của Flow thật.

### Giữ nguyên độ phủ hình và nhịp lời — yêu cầu chủ repo 03/11/2026

Tối ưu thời gian tạo ảnh không được giảm số cảnh/ảnh, gộp nhiều ý, kéo dài cảnh hoặc đổi mốc cắt của storyboard đã khóa. Số ảnh theo số ý/câu và nhịp voice thực tế, không theo chỉ tiêu tiết kiệm lượt tạo. Bước Flow chỉ bổ sung thông tin ảnh; không sửa lời, mốc đầu/cuối hoặc chỉ số từ của cảnh. Chặn ID cảnh trùng và tile Flow gắn cho nhiều cảnh để tránh dùng nhầm một kết quả cho nhiều ý.

Kiểm thử hồi quy dùng 116 cảnh giả lập, yêu cầu 116 tile riêng và 116 file ảnh, đồng thời so nguyên vẹn trường storyboard đầu vào. Đây là kiểm cấu trúc, không xác minh ảnh thể hiện đúng ý hay nhịp dựng thành phẩm. Cổng storyboard theo voice, nguồn/hash và xem/nghe hình–tiếng vẫn cần được thực hiện; không dùng test phần mềm để ghi duyệt nội dung.

Nhật ký cảnh có `submit_wait_seconds` (gửi + đợi ảnh), `download_verify_seconds` và `cooldown_seconds`. Dùng số đo thật khi sản xuất để phân biệt Google gen chậm với tải ảnh hoặc chờ phụ. Không dùng thời gian fixture làm dự báo thời gian video thật.
