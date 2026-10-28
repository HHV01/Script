# Xưởng video lịch sử

Giao diện xưởng phim với ba vai trò: **An** quản lý và tìm đề tài, **Minh** sản xuất,
**Mai** duyệt kịch bản trước khi thu. Có pipeline tạo video, Google Flow qua Playwright,
nghiên cứu YouTube và các mẫu animation chạy bằng CPU.

## Xem video mẫu ngay sau khi tải repo

Mở `previews/babylon-17s/babylon_animation_17s.mp4` bằng trình phát video trên máy.
Hoặc mở `previews/babylon-17s/index.html` bằng Chrome/Edge. Không cần cài Python để xem mẫu.
Video dài 17 giây, giữ lời đọc của đoạn nguồn 00:09,56–00:26,56, không chèn tên kênh.

## Cài trên máy cá nhân

Khuyến nghị Python **3.12**, FFmpeg/ffprobe và Chrome/Chromium.
Mở terminal tại thư mục repo vừa giải nén. Máy có FFmpeg cần kiểm tra được:

```text
ffmpeg -version
ffprobe -version
```

Windows có thể cài FFmpeg bằng `winget install --id Gyan.FFmpeg -e`, sau đó mở terminal mới.
macOS có thể dùng `brew install ffmpeg`. Linux dùng trình quản lý gói hệ thống.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe run.py studio
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-local.txt
.venv/bin/python run.py studio
```

Mở **http://127.0.0.1:8787** trên chính máy đang chạy Python. Đổi cổng bằng `studio --port 8790`.
`requirements-local.txt` đủ cho giao diện và animation cục bộ; chưa cài mô hình đọc giọng,
Playwright hoặc SDK phục vụ các bước AI/API. Muốn chạy đầy đủ:

```bash
# Dùng Python trong .venv; Windows thay bằng .\.venv\Scripts\python.exe
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

Đã kiểm tra trên Linux/Python 3.12 trong môi trường cloud. Windows/macOS có hướng dẫn cài,
chưa được kiểm tra thực tế trên các hệ điều hành đó. Phiên Google đăng nhập trên máy này không
được chia sẻ sang máy khác.

## Giao diện và quy trình

```text
An: đọc số liệu → đề xuất đề tài → giao xuống Minh

1 script    Viết bản nháp theo chủ đề, niche và phong cách mẫu
2 review    Mai lấy dữ liệu gần đây, duyệt; yêu cầu sửa nếu chưa đạt
3 voice     Thu giọng theo kế hoạch câu/đoạn và khoảng nghỉ đã duyệt
4 scenes    Chia cảnh theo thời gian lời đọc
5 prompts   Viết prompt cho cảnh cần ảnh; bỏ qua animation cục bộ
6 generate  Tạo ảnh trên Google Flow
7 collect   Kiểm tra và tải ảnh; bỏ qua animation cục bộ
8 render    Ghép ảnh/animation + giọng + phụ đề nhỏ sát đáy
9 publish   Xuất tiêu đề, mô tả, tag và gợi ý thumbnail; không tự upload
```

Tạo/chọn dự án trong giao diện, chọn **Giao việc cho Minh**. Có thể chọn bước bắt đầu,
chỉ chạy một công đoạn, dừng và chạy tiếp. Nhân vật di chuyển theo sự kiện từ tiến trình thật;
phần trăm là số công đoạn hoàn tất, không là dự báo thời gian. Nhật ký giữ 200 dòng.
Chỉ chạy một worker sản xuất cùng lúc. Dashboard theo dõi các job do chính nó khởi chạy;
không tự phát hiện CLI chạy ở nơi khác. Khi server khởi động lại, job dang dở được đánh dấu gián đoạn.
File bàn giao có thể là kết quả của lần chạy trước. Ctrl+C tắt server và dừng worker của nó.

Lệnh CLI, dùng Python của môi trường đã cài:

```bash
python run.py new ten_project
python run.py run ten_project
python run.py run ten_project --only review
python run.py run ten_project --from prompts
python run.py run ten_project --only render --force
python run.py run ten_project --only publish --force
```

Project lưu trong `projects/<tên>/`, cấu hình ban đầu ở `projects/_template/project.yaml`.
Chỉnh `topic`, `niche`, `audience`, `minutes` và `flow_url`. Trong project, khóa `settings`
ghi đè cấu hình chung tại `config/settings.yaml`.

## API key và dữ liệu riêng

Sao chép `.env.example` thành `.env` rồi điền trên máy của bạn:

- `OPENCODE_API_KEY`: viết kịch bản, duyệt, prompt ảnh, đề tài và metadata.
- `YOUTUBE_API_KEY`: YouTube Data API v3, dữ liệu công khai/nghiên cứu.
- `GOOGLE_OAUTH_CLIENT_FILE`: đường dẫn file OAuth Desktop, chỉ cần Analytics chủ kênh.

Không đưa key hoặc file đăng nhập lên Git. `.env`, `.venv/`, `.studio/`, `.flow-profile/`
và project sinh ra đều được bỏ qua. Repo không có phiên đăng nhập hoặc API key điền sẵn.

## Google Flow qua Playwright

Mặc định `flow.backend: playwright`, không cần nạp extension. Chạy:

```bash
python run.py run ten_project --only ping
```

Đăng nhập Google trong browser vừa mở, vào đúng project. Hồ sơ cục bộ nằm trong `.flow-profile/`.
Lần đầu cần giao diện, nên giữ `flow.playwright.headless: false`.
Có thể đặt `flow.playwright.executable_path` tới Chrome đã cài trên máy, hoặc dùng browser
Playwright sau lệnh cài Chromium bên trên. Máy cloud không có display cần desktop/browser tương ứng.

Kết nối browser đã đăng nhập: mở Chrome với profile riêng và CDP chỉ ở localhost:

```text
chrome --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir=<profile-rieng>
```

Dùng đường dẫn executable Chrome thực tế trên máy nếu lệnh `chrome` chưa có trong PATH;
đặt `flow.playwright.cdp_url: http://127.0.0.1:9222`. Browser và Python phải ở cùng máy.
Không công khai cổng debug. `flow.backend: extension` giữ cách kết nối cũ.
Selector dùng chung tại `flow_extension/selectors.js`; UI Flow thay đổi có thể cần sửa selector.
Chưa kiểm chứng đăng nhập/tạo ảnh với Google Flow thật trong phiên phát triển này.
Không tự vượt CAPTCHA hoặc xác minh tài khoản.

## Mai duyệt kịch bản

Mặc định mỗi tiêu chí phải đạt 7/10: hook, mạch kể, cẩn trọng lịch sử, đúng niche,
dễ đọc và sức cuốn hút. Còn lỗi major/blocker, khẳng định đang chờ nguồn hoặc độ dài
chưa phù hợp thì chưa thu giọng. Tối đa 2 lượt sửa rồi duyệt lại. Điểm là nhận xét AI,
không dự đoán CTR hay bảo đảm tăng view.

Mẫu chủ kênh đã duyệt nằm tại `config/editorial/examples/giza.approved.txt`, hướng phong cách
ở `config/editorial/profile.yaml`. Học cách dẫn cảnh, chuyển ý và nhịp đoạn; không sao chép
câu hoặc dùng mẫu làm nguồn kiểm chứng sử liệu. Bản gốc giữ để tham chiếu; đầu ra mới không chèn tên kênh.

YouTube được lấy bằng hai search.list, cửa sổ mặc định 30 ngày, cache 24 giờ;
khoảng 200 search quota units/lượt lấy mới cộng đọc metadata. Không xem tiêu đề video là bằng chứng
về một phát hiện lịch sử. Có thể cung cấp `research_sources` trong project với tên tài liệu,
URL và đoạn trích thực sự đã đọc. Hệ thống chưa tự tải/kiểm chứng độc lập toàn văn các tài liệu đó.

Các tệp duyệt/thu: `script.review.json`, `review_research.json`, `script.revision-N.txt`,
`recording_plan.json`, `recording_script.md`, `voice.source.json`. Bản được duyệt mới thay `script.txt`;
giữ bản trước tại `script.before_review.txt`. Kịch bản, yêu cầu hoặc kế hoạch đổi/hết hạn sẽ bị chặn.
Sau khi sửa và duyệt lại, nếu audio cũ không khớp:

```bash
python run.py run ten_project --only review
python run.py run ten_project --from voice --force
```

Lệnh sau tái tạo các bước sau, có thể tốn quota/chi phí. Voice manual cần thay audio theo bản mới.
`settings.review.enabled: false` là lựa chọn chủ động tắt gate cho offline/legacy, không là Mai đã duyệt.
TTS áp dụng câu/đoạn và khoảng nghỉ trong kế hoạch; hướng dẫn nhấn nhá không tự điều khiển được
mọi biểu cảm của giọng. Vẫn cần nghe kiểm tra audio đầu ra. Voice thật cần tải mô hình VieNeu;
việc tổng hợp bằng mô hình thật chưa được xác nhận trong môi trường phát triển này.

## An quản lý kênh

Đọc tối đa 100 video mới của kênh và ba nhóm tìm kiếm (khoảng 300 search quota units/lượt),
đối chiếu chủ đề rồi đề xuất 1–5 đề tài lịch sử có hook, dàn ý và id video tham khảo.
Chống giao trùng đề tài; xếp hàng khi Minh bận. Tự giao tối đa một đề tài ưu tiên mỗi báo cáo.
Đề bài được ghi vào `production_brief` trong project mới.

Trong “Lịch tự động & kết nối”, bật lịch 6–168 giờ, chọn thời lượng và URL project Flow.
Lịch ban đầu tắt và chỉ chạy khi server đang mở. Tự giao áp dụng cả lượt phân tích thủ công
và lượt theo lịch; tên nút thể hiện điều này. Lượt đọc dữ liệu lỗi thử lại sau một giờ.
Báo cáo có thể tải Markdown/JSON. Dữ liệu công khai là view tích lũy/subscriber có thể làm tròn;
chênh lệch snapshot không mặc định là số liệu 28 ngày. Không có baseline sẽ để trống.

### OAuth Analytics chỉ đọc

1. Bật YouTube Data API v3 và YouTube Analytics API trong Google Cloud.
2. Tạo OAuth Client loại Desktop app; nếu app Testing, thêm tài khoản vào Test users.
3. Lưu JSON tại đường dẫn riêng, ví dụ `.studio/oauth-client.json`, rồi đặt đường dẫn tuyệt đối
   vào `GOOGLE_OAUTH_CLIENT_FILE` trong `.env`.
4. Khởi động lại studio, chọn “Kết nối chủ kênh”, đăng nhập đúng kênh/Brand Account.
5. Chọn phân tích để lấy báo cáo mới.

Quyền `youtube.readonly` và `yt-analytics.readonly`, kiểm tra chủ tài khoản khớp kênh cấu hình.
Token giữ cục bộ tại `.studio/manager/google-token.json`; không đưa token vào báo cáo/giao diện.
Gỡ kết nối xóa token cục bộ; thu hồi quyền hoàn toàn qua tài khoản Google. App Testing có thể hết hạn token.
Analytics gồm lượt xem 28 ngày, phút xem, thời lượng xem trung bình, phần trăm được xem trung bình,
subscriber tăng/giảm và nguồn truy cập. Kỳ kết thúc trước hôm nay 2 ngày. **CTR chưa được tích hợp.**
OAuth/API thật chưa được kiểm chứng khi chưa cung cấp thông tin xác thực.

## Animation cục bộ, ít dùng token

```bash
python run.py animate --preset stone_transport --output transport.mp4 --duration 8
python run.py animate --preset stone_ramp --output ramp.mp4 --duration 8
python run.py animate --preset giza_cinematic --output giza.mp4 --duration 12 --sound
```

Dựng bằng Pillow/FFmpeg, không gọi AI/API. Mặc định 960×540/24fps, tối đa 2 luồng CPU,
không giữ toàn bộ frame trong RAM. Thêm `--width 1920 --height 1080 --fps 30` để xuất lớn hơn.
`--sound` tạo âm thanh nền cục bộ cho clip riêng. Clip pipeline vẫn dùng giọng đọc project.

Gắn `"animation": {"preset": "stone_transport"}` vào một cảnh trong `scenes.json` để dùng animation.
Giữ id/text/start/end. Prompts/generate/collect bỏ qua cảnh đó. Render ghép được ảnh và animation.
Đổi preset cần `--only render --force` nếu còn clip cache từ lần bị ngắt. Tạo lại scenes sẽ xóa
đánh dấu thủ công, cần gắn lại. Các preset là minh họa/low-poly, không phải tái dựng khảo cổ chính xác.

Mẫu riêng từ video Babylon của người dùng:

```bash
python run.py animate-babylon --input short_babylon_khong_ten_kenh.mp4 --output babylon.mp4
```

Dùng đoạn 00:09,56–00:26,56, 720×1280/25fps, giữ giọng đọc nguồn, thêm mô phỏng bọc đất sét,
khắc và lăn con dấu. Cần chính video nguồn tương ứng; file nguồn không kèm repo, bản xuất mẫu đã kèm
trong `previews/`. Timestamp/phụ đề/vùng crop không tự áp dụng cho video bất kỳ.
Nhân vật/bàn tay trong ảnh gốc chưa được hoạt họa toàn thân.

## Nghiên cứu hình ảnh

```bash
python run.py research-visuals --days 90 --results 5 --min-views 50000 --duration medium
```

Cần YOUTUBE_API_KEY; lấy bốn nhóm tìm kiếm cùng niche, khoảng 400 search quota units/lượt
cộng metadata. Lưu số liệu/link/thumbnail gốc ở `.studio/visual-benchmark/`.
Đây là mẫu chọn theo viewCount, không phải xếp hạng toàn YouTube. `visual_observations` để null
cho tới khi thực sự xem hình/video. Chưa có kết luận đối thủ từ quan sát trực tiếp.
Xem [phương án hình ảnh Giza](docs/research/visual-direction-giza.md).

## Kiểm tra và lưu ý

Cài dependencies đầy đủ và FFmpeg trước khi chạy:

```bash
python -m unittest discover -s tests -v
python tests/e2e_fake.py
```

Browser tests dùng Chromium thật với trang giả lập, có thể skip nếu thiếu browser.
YouTube/LLM/voice tests dùng phản hồi hoặc engine giả; không xác nhận key hoặc mô hình thật.
FFmpeg render và worker/subprocess được kiểm tra thực tế. Không có bảo đảm tăng view.

Chi tiết luồng gốc và xử lý lỗi cũ: [HUONG-DAN.md](HUONG-DAN.md). README này mô tả các bước mới.
Nếu dùng cloud hạn chế mạng, cần áp dụng các domain tương ứng Google/YouTube/OpenCode/Hugging Face.
Giao diện ở localhost không tự trở thành đường dẫn công khai. Không chia sẻ `.env`, `.studio/`
hoặc profile browser khi đóng gói project.
