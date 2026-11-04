# Bàn giao biên tập khoa học — 30/10/2026

Executor thực tế: agent `/root/science_editorial`. Đây là cập nhật hướng dẫn biên tập, không phải chứng nhận sản phẩm đã đạt hoặc nâng cấp năng lực đã được chứng minh.

## Định hướng chủ repo vừa xác nhận

Khoa học cơ thể, cảm giác và hành vi đời thường; kể bằng hài thông minh, kháy nhẹ tình huống. Giữ stick-orange, không gian giấy kem và bối cảnh hiện tại. Ưu tiên long ngang 16:9. Phê duyệt định hướng không thay thế duyệt từng kịch bản, nguồn hoặc video.

## Hợp đồng đầu vào và đầu ra

Đầu vào cần có câu hỏi trung tâm, người xem giả định, phạm vi giải thích và research_sources đã đọc. Thiếu nguồn thì ghi thiếu và trả nghiên cứu, không điền nguồn chưa kiểm tra. Đầu ra là dàn ý có chuỗi giải thích, kịch bản, bản đồ luận điểm–nguồn, giới hạn bằng chứng và yêu cầu minh họa. Chưa đạt thì trả sửa; không tự điền approved.

## Bố cục long

1. Mở bằng một tình huống cụ thể và nghịch lý; không lặp cùng ý qua nhiều ví dụ.
2. Chốt một câu hỏi, làm rõ khái niệm người xem dễ nhầm.
3. Xây các phần theo quan hệ: quan sát nào cần giải thích → bằng chứng nào giải quyết được → phần nào còn chưa biết. Chỉ dùng quan hệ nhân quả khi nguồn cho phép.
4. Mỗi phần có một ý mới, ví dụ có thể vẽ và câu nối sang phần tiếp. Hài phục vụ hiểu ý; ẩn dụ không được biến thành cơ chế thật.
5. Đặt giới hạn cạnh kết luận, không giấu toàn bộ ở cuối: nghiên cứu trên ai, phương pháp gì, có chỉ là tương quan hay giả thuyết không.
6. Payoff trả lời câu hỏi mở và quay lại tình huống đầu; bỏ đoạn thừa, kết luận lặp hoặc CTA làm đứt nhịp.

Không chẩn đoán người xem, suy tính cách hoặc trí thông minh từ thói quen, hay quy kết theo giới, tuổi, vùng miền. Chủ đề có yếu tố bệnh lý cần phân biệt kiến thức chung với đánh giá cá nhân; không bịa hướng dẫn điều trị.

## Ví dụ phạm vi với memory-long-01

Tôi chỉ đọc phần mở đầu của `projects/memory-long-01/script.txt` trong lượt này. Câu hỏi “học được nhiều điều lúc bé nhưng vì sao không nhớ trải nghiệm ấy” có thể dùng làm trục bố cục: tình huống nghe kể chuyện tuổi thơ → phân biệt học kỹ năng với nhớ sự kiện → các cơ chế có nguồn và giới hạn → quay lại chuyện bức ảnh. Đây là đề xuất tổ chức ý, không xác minh cơ chế hay duyệt kịch bản hiện có. Tránh kéo dài phần mở bằng nhiều câu hỏi/ví dụ cùng chứng minh rằng nhân vật không nhớ.

## Kiểm tra đã thực hiện và còn thiếu

Đã đọc AGENTS.md, channel-direction.yaml, profile biên tập cũ, bộ nạp style_context và các assertion tương thích liên quan; đã đọc đoạn mở đầu kịch bản trên. Giữ các trường channel/reference/approval_scope/voice/structure/historical_care/narration/length để không đổi giao diện bộ nạp. Mẫu reference cũ chỉ còn là dữ liệu nhịp kể, không phải tài liệu khoa học hoặc phê duyệt nội dung.

Chưa đọc toàn bộ kịch bản, chưa kiểm nguồn khoa học, chưa xem/nghe video, chưa kiểm mỹ thuật, chưa có đánh giá độc lập sản phẩm trong nhiệm vụ này. Không gọi API sản xuất, render hay uploader. Kiểm tra cấu hình chỉ chứng minh khả năng đọc và những nội dung hướng dẫn hiện có, không chứng minh video thu hút hoặc đúng khoa học.
