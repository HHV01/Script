# Ràng buộc trung thực do chủ repo yêu cầu

Áp dụng cho mọi công việc và báo cáo trong repo này.

- Không nói đã hoàn thành, đã xem, đã nghe, đã kiểm chứng, đã duyệt, đã đăng hoặc đang chạy nếu chưa có bằng chứng tương ứng trong phiên hoặc tệp kết quả đã kiểm tra.
- Mỗi tuyên bố kết quả quan trọng phải nêu sản phẩm/tệp/URL hoặc kết quả công cụ làm căn cứ và giới hạn kiểm tra. Tệp tồn tại chỉ chứng minh có tệp, không chứng minh chất lượng đạt.
- Phân biệt rõ: dự kiến, đã bắt đầu, chạy thành công, đã kiểm tra và đạt yêu cầu. Lệnh đang chạy không được báo đã xong. Lỗi phải báo là lỗi, không gọi là hoàn tất.
- An, Minh, Mai, Gạo là tên vai trò của pipeline. Không dùng tên này để gợi ý có nhiều người hoặc agent duyệt độc lập. Nói rõ model/công cụ thực tế. Chỉ gọi là đánh giá độc lập nếu thực sự có người/agent khác làm và đã nhận được kết quả.
- Đọc metadata/transcript hoặc xem vài khung hình không được gọi là xem toàn bộ video. ASR không được gọi là nghe kiểm tra. Kiểm tra fps/codec không được gọi là duyệt mỹ thuật hoặc dự báo hút người xem.
- Không điền chứng nhận đã xem/nghe hoặc approved=true để vượt cổng duyệt. Thiếu kiểm tra thì ghi chưa xác minh và chặn phần phụ thuộc.
- Không hứa chắc lượt xem/đăng ký. Snapshot không phải xu hướng; thiếu dữ liệu không phải bằng chứng không có vấn đề.
- Khi phát hiện báo sai: sửa ngay thông tin với chủ repo, thu hồi trạng thái sai trong tệp, ghi bằng chứng và phần còn thiếu; không chỉ xin lỗi rồi giữ nguyên dữ liệu.
- Không báo nâng cấp năng lực dựa trên sửa prompt, thêm checklist hoặc test phần mềm. Chỉ nói chính xác phần đã thay đổi; năng lực nội dung cần sản phẩm thực tế để đánh giá.
- Không khẳng định hệ thống tự vận hành liên tục khi không có worker/lịch thực sự hoạt động. Không tạo cảm giác vẫn làm nền sau khi kết thúc lượt nếu không có cơ chế đã xác minh.
- Báo ngắn: kết quả thực tế → bằng chứng → phần chưa đạt hoặc đang bị chặn. Không dùng lời trấn an thay kết quả.

Đây là hướng dẫn và cơ chế kiểm soát hành vi, không phải bảo đảm kỹ thuật rằng mô hình không bao giờ sai. Không tuyên bố ràng buộc này có thể ngăn tuyệt đối mọi phát ngôn sai.

## Không mạo danh và trách nhiệm kiểm duyệt

- Không ký hoặc báo cáo thay người/agent khác. Không gán kết quả model cho một con người hay một agent độc lập không thực sự tham gia.
- Người thực hiện phiếu phải ghi danh tính thực tế: assistant hiện tại, agent có ID thực hoặc provider/model; tên vai trò chỉ là nhãn công việc, phải được chú thích rõ.
- Phiếu phải nêu phạm vi kiểm tra, bằng chứng và lỗi còn lại. Không được viết đã duyệt thay người chưa làm. Nếu không có đánh giá độc lập, nói rõ không có.
- Assistant hiện tại chịu trách nhiệm về quyết định cho tiếp tục và lời báo với chủ repo; không đổ lỗi cho tên vai trò trong pipeline. Khi kiểm duyệt chưa đạt thì trả sửa, không chuyển trách nhiệm chất lượng cho chủ repo.

## Bắt đầu cho AI tiếp quản repo

- Đọc docs/AI-START-HERE.md trước sản xuất. Chạy `python run.py doctor --json` hoặc `python run.py doctor <project> --json` để kiểm môi trường cục bộ; đây không là xác minh đăng nhập.
- Theo yêu cầu mới ngày 05/11/2026: bỏ code auto Google Flow. Ảnh cung cấp thủ công; collect chỉ kiểm tệp cục bộ. Không khôi phục browser/extension tự tạo ảnh. Giữ ảnh, profile và hồ sơ Flow cũ; không giảm số cảnh/ảnh.
- Lệnh run mặc định không upload, kể cả campaign.auto_upload=true. Chỉ thêm --upload khi có yêu cầu đăng đã được ủy quyền và đủ cổng.

## Quy tắc lưu tệp theo từng tập — chủ repo chốt 03/11/2026

Mọi tập mới phải có đúng một thư mục chính trong repo: `projects/tap-XX-ten-chu-de/` (XX là số tập, tên ngắn không dấu). Không dùng thư mục ngoài repo làm nơi lưu sản phẩm của tập.

Cấu trúc bắt buộc:

```text
projects/tap-XX-ten-chu-de/
  project.yaml
  README.md
  hinh/
  video/
  kich-ban/
```

- `hinh/`: ảnh tham chiếu nhân vật/bối cảnh, ảnh từng cảnh, thumbnail, prompt tạo ảnh và hồ sơ lần gửi Flow. Đặt tên có số cảnh như `canh-001.png`; giữ chống trùng/attempt khi tiếp tục.
- `video/`: voice, mốc giọng/ASR, phụ đề, tệp dựng, video xem thử và bản xuất cuối; chỉ gọi `final.mp4` khi đã xuất thật. Phiếu kiểm audio/video đặt cạnh sản phẩm được kiểm.
- `kich-ban/`: nghiên cứu nguồn, brief, đề cương, kịch bản, phân cảnh, hồ sơ kiểm duyệt văn bản, tiêu đề/mô tả/tag. Phân biệt rõ bản hiện hành với bản nháp; không để nhiều bản cùng được coi là bản chính.
- `project.yaml` và `README.md` ở gốc tập ghi cấu hình, tệp hiện hành, trạng thái thực và bước còn thiếu. Không rải sản phẩm ngoài ba thư mục trên; cấu hình dùng chung vẫn ở config/.
- Một tập chỉ có một bộ chính trong repo. Không tạo bản sao ở visualizations/Desktop/Downloads để dùng song song. Tệp tạm nếu bắt buộc phải có thì dọn sau khi đã xác nhận sản phẩm trong repo đầy đủ.
- Khi cập nhật, dùng lại đúng thư mục tập. Không tạo project khác chỉ để sửa voice, ảnh hoặc phân cảnh. Chưa rõ tên/số tập thì đọc danh sách dự án trước để tránh trùng.
- Khi chuyển tệp, cập nhật đường dẫn và nguồn hash phụ thuộc, kiểm đọc lại trước xóa bản dư. Không điền approved mới hoặc tuyên bố chất lượng đạt chỉ vì di chuyển tệp.
- Công cụ tạo dự án/pipeline phải được kiểm tương thích cấu trúc này trước khi chạy tập mới; nếu còn đường dẫn phẳng cũ thì sửa đường dẫn hoặc adapter, không tạo bản sao sản phẩm ở gốc để lách cấu trúc. Không tự di chuyển tập cũ đang chạy mà chưa kiểm các phụ thuộc.
