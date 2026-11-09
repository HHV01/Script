# Tạo ảnh Flow từ scenes.json

Module độc lập, không cần extension, không đọc lại cấu hình nhân vật/phong cách. Nó gửi nguyên văn `image_prompt`, không gọi LLM hoặc viết lại prompt. Code Flow cũ được giữ theo lựa chọn chủ repo ngày 05/11/2026; module này chưa thay các nút/lệnh cũ trong Studio.

## Cài và chuẩn bị

Tại gốc repo, dùng Python của môi trường đang hoạt động:

```powershell
python -m pip install "playwright>=1.49,<2" "pillow>=10"
python -m playwright install chromium
python -m flow_gen.generate_images --help
```

Chrome được thử trước (`channel="chrome"`), sau đó Chromium nếu không mở được. Profile mặc định là `Path.home()/".flow_gen_profile"`, ngoài repo. `--profile` cũng bắt buộc ngoài repo. Không dùng profile Chrome cá nhân đang mở; không sao chép cookie, lưu mật khẩu hoặc xóa lock để ép chạy.

```powershell
$flowUrl = Read-Host "URL project Google Flow"
python -m flow_gen.generate_images --url "$flowUrl" --login
```

Đăng nhập/chọn project trong cửa sổ đó, nhấn Enter trong terminal để đóng helper. `--login` không tạo ảnh. URL không được lưu trong code/state; không commit lịch sử terminal có URL riêng tư.

Nếu Google không cho đăng nhập trong browser do Playwright mở, có thể dùng Chrome đã được bạn mở với remote debugging và profile riêng ngoài repo, sau đó thêm `--cdp http://localhost:9222`. Không mở CDP ra mạng công cộng. Module chỉ ngắt kết nối khi kết thúc, không đóng Chrome CDP của bạn. CDP không tự giải quyết việc đăng nhập hoặc cấp quyền tài khoản.

## Dữ liệu đầu vào

```json
[
  {"id": 1, "start": 0.0, "end": 8.0, "narration": "Lời đọc cảnh một", "image_prompt": "Prompt hoàn chỉnh, giữ nguyên từng ký tự"},
  {"id": 2, "start": 8.0, "end": 16.0, "narration": "Lời đọc cảnh hai", "image_prompt": "Prompt hoàn chỉnh của cảnh hai"},
  {"id": 3, "start": 16.0, "end": 24.0, "narration": "Lời đọc cảnh ba", "image_prompt": "Prompt hoàn chỉnh của cảnh ba"}
]
```

Các mốc trên chỉ minh họa định dạng, không phải đề xuất đổi nhịp cảnh của tập hiện có. ID phải nguyên dương, duy nhất. Thứ tự gửi theo danh sách đầu vào, `--from/--to` lọc theo ID. Thiếu prompt sẽ báo ID và dừng trước khi mở browser. Chỉ khi bật `--fallback-narration`, cảnh thiếu prompt mới dùng nguyên văn `narration`. Module không tự chuyển trường `text` hoặc thay đổi dữ liệu cảnh.

`scenes-plan.json` có thể truyền bằng `--scenes` nếu nội dung là danh sách đúng định dạng trên. Không hỗ trợ tự chuyển đối tượng bọc `{ "scenes": [...] }`; hãy cung cấp một tệp đầu vào danh sách riêng trong thư mục tập, không sửa storyboard đang dùng chỉ để lách cổng.

## Hiệu chỉnh ba cảnh trước sản xuất

Đặt Flow ở **tạo ảnh, x1, 16:9**. Module chọn/xác nhận x1 trong riêng mục ảnh và lưu trước mỗi lần gửi; không đổi lựa chọn xác nhận tạo nội dung hoặc hàng x1 của video. Không xác định được nhóm x1 sẽ dừng.

Giao diện Flow quan sát ngày 05/11/2026 có nút **Tác nhân** bật/tắt. Module tắt nút này khi `aria-pressed=true`, dùng chế độ ảnh trực tiếp và kiểm x1/16:9 ở panel của chính chế độ đó. Cài đặt x1 của Tác nhân và của tạo ảnh trực tiếp là hai trạng thái khác nhau. Nút gửi có nhãn `Bắt đầu tạo`; sau click phải chờ ô nhập được xóa để xác nhận Flow đã nhận prompt, tránh nhập đè khi giao diện còn xử lý prompt trước.

Ví dụ đường dẫn trong tập đã có đủ prompt:

```powershell
$scenes = "projects/tap-XX-ten-chu-de/kich-ban/scenes.json"
$calibration = "projects/tap-XX-ten-chu-de/hinh/flow-calibration"
python -m flow_gen.generate_images --scenes "$scenes" --url "$flowUrl" --from 1 --to 3 --batch 3 --out "$calibration"
```

Mở ba ảnh, đối chiếu nội dung với từng prompt. Mặc định giả định Flow đặt ảnh mới nhất ở đầu danh sách DOM, nên đảo thứ tự để ghép với thứ tự gửi. Nếu Flow chèn ảnh mới ở cuối, dùng `--oldest-first` và **một thư mục hiệu chỉnh mới**, tránh ghi đè kết quả cũ.

**Giới hạn quan trọng:** Flow có thể sắp theo thời điểm hoàn thành, đổi thứ tự DOM hoặc ảo hóa gallery. Đếm đủ ảnh và cờ thứ tự không chứng minh ảnh thuộc đúng prompt. Chỉ dùng batch >1 sau khi hiệu chỉnh bằng mắt trên chính giao diện đang dùng. Khi không chắc, dùng mặc định `--batch 1`, không đoán gán cảnh.

Khi hiệu chỉnh đạt, chạy với thư mục sản xuất riêng; không tái dùng state hiệu chỉnh vì sẽ bỏ qua các cảnh đã done:

```powershell
python -m flow_gen.generate_images --scenes "$scenes" --url "$flowUrl" --out "projects/tap-XX-ten-chu-de/hinh/flow-gen" --batch 1
```

Nếu muốn dùng lại đúng thư mục `out` hiệu chỉnh, cần kiểm tra và **xác nhận trước khi xóa** `out/state.json` cùng `out/images/`; module không cung cấp lệnh tự xóa/reset. Việc dùng thư mục mới sẽ tạo ảnh mới, có thể tiêu thêm credit. Không giảm số cảnh/ảnh để tiết kiệm lượt.

## Đầu ra và chạy tiếp

Mặc định ghi `out/` tại thư mục chạy lệnh; với tập trong repo, luôn dùng `--out` bên trong `hinh/` của tập như ví dụ trên.

```text
out/
  state.json
  .run.lock
  images/scene_001.png      # hoặc .jpg/.webp theo MIME thật
  orphans/batch_0001_001.png
```

- Poll mỗi 0,5 giây; ảnh phải load xong, cạnh nhỏ nhất ≥512px. Timeout mặc định 120 giây/lô một cảnh, cộng 20 giây mỗi cảnh thêm (`--timeout` đổi phần cơ sở).
- Gửi cách nhau khoảng 1 giây, sau đó chờ tập ảnh mới ổn định thêm 2 giây. Không chờ cố định 25–28 giây/cảnh.
- HTTP(S) tải qua `page.context.request`; blob/data đọc trong trang. Kiểm MIME, định dạng ảnh và kích thước trước khi lưu.
- Thừa ảnh sau ổn định: cách ly vào `orphans/`, retry từng cảnh tối đa hai lần. Ảnh lạ không được gán ngẫu nhiên cho cảnh.
- Thiếu ảnh, timeout, ngắt sau submit hoặc lỗi tải: trạng thái `pending/needs_review` chặn chạy tiếp, kể cả đổi khoảng ID. **Không tự retry submit chưa rõ kết quả.** Đây là giới hạn có chủ ý so với yêu cầu retry mọi lỗi số lượng: ảnh đến muộn có thể bị gán nhầm hoặc tạo trùng. Giữ gallery/state, đối chiếu tay trước khi tiếp tục.
- `failed` trước submit hoặc sau số lượng thừa ổn định được thử lại ở lần chạy kế tiếp. `done` chỉ bỏ qua khi file và hash còn khớp. Đổi prompt/URL hoặc thiếu ảnh done sẽ chặn tái dùng state.
- State chỉ lưu hash prompt/URL, tên file, trạng thái; không lưu cookie, token hoặc URL tải có chữ ký. Không coi `done` là duyệt nội dung.

Không chạy hai worker dùng chung out/profile. Lock file được giữ, khóa hệ điều hành tự giải phóng khi tiến trình kết thúc; không xóa lock khi worker còn chạy.

Tên `scene_001` là đầu ra riêng của module. Renderer cũ chưa tự đọc tên này; việc tích hợp ghép theo `scene_ID`, thêm zoom/pan/fade và đổi thời lượng cảnh **chưa thực hiện** theo mục 3.4. Không chạy render cũ rồi giả định các ảnh này đã được nhận đúng.

## Khi Flow đổi giao diện

Các selector nằm ở `SELECTORS` đầu `generate_images.py`. Không xác định được ô nhập/cài đặt sẽ dừng trước gửi. Mở Flow thật bằng `--login` hoặc CDP, dùng DevTools kiểm DOM, rồi chỉnh selector theo phần tử đã quan sát; không thử click các nút đoán mò. Không lưu HTML có token/cookie vào repo.

Chỉ kiểm thử trang giả lập không chứng minh selector hoạt động trên Flow thật. Bộ test có kiểm tra nhập nguyên văn Unicode/xuống dòng/khoảng trắng, hai hướng DOM, batch ba ảnh màu khác nhau, ảnh lạ, retry, resume và x1 ảnh độc lập với x1 video.

```powershell
python -m py_compile flow_gen/generate_images.py
python -m unittest discover -s tests -p test_flow_gen.py -v
```

Tham chiếu API chính thức: [profile và CDP](https://playwright.dev/python/docs/api/class-browsertype), [keyboard.insert_text](https://playwright.dev/python/docs/api/class-keyboard#keyboard-insert-text), [cookie của APIRequestContext](https://playwright.dev/python/docs/api/class-apirequestcontext).
