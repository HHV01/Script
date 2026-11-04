# Vẽ Khoa Học — nghiên cứu ngày 04/11/2026

Executor: assistant hiện tại (Codex). Dữ liệu công khai từ YouTube Data API; key chỉ gửi bằng header, không lưu vào tệp. Phạm vi hiện đã kiểm: metadata 30 video; nhìn trực tiếp montage 4 thumbnail; đọc 20 bình luận cấp đầu do API xếp theo relevance (gồm bình luận chủ kênh). Chưa xem/nghe toàn bộ video. Số liệu một mốc, không phải xu hướng hay bằng chứng nhân quả.

## Kết quả định lượng

Snapshot api-snapshot.json lúc 04:36 UTC (11:36 giờ Việt Nam). Kênh trả về 564 đăng ký, 30 video. Hai video dẫn đầu chiếm 73,39% tổng view cộng từ 30 bộ đếm video; 6 video liên quan cờ vua chiếm 86,44%. Trung vị 30 video là 1.789,5 lượt xem. Channel-level viewCount khác tổng video-level nên không dùng hai tổng như cùng một đại lượng; xem summary.json.

| Video | Ngày đăng | Thời lượng | View snapshot |
|---|---|---|---:|
| Vì sao bạn không thể thắng Magnus Carlsen trong 1 trận cờ vua? | 21/10/2026 | 1:53 | 127.405 |
| Cờ vua sẽ làm gì bộ não của bạn? | 28/10/2026 | 10:35 | 71.678 |
| Làm sao để thắng Magnus Carlsen trong 1 trận cờ vua? | 01/11/2026 | 2:36 | 19.358 |
| Toàn bộ lịch sử CỜ VUA trong 13 phút! | 03/11/2026 | 13:13 | 8.285 |
| Cờ vua có thực sự giúp bạn tăng IQ? | 31/10/2026 | 11:34 | 7.678 |
| Ngủ 8 tiếng là 1 lời nói dối? Lý do ngủ nhiều mà vẫn mệt! | 25/10/2026 | 16:31 | 1.441 |

Video mới ngày 04/11 có tuổi xuất bản rất ngắn, không coi view thấp lúc snapshot là thất bại. Không xếp hạng hiệu suất chỉ theo view/ngày vì đó vẫn là trung bình tích lũy.

## Quan sát và cách diễn giải

1. Cụm chủ đề: cờ vua kết hợp một nhân vật nổi tiếng, thách thức người xem và lợi ích nhận thức. View đang tập trung ở cụm này; chưa chứng minh vì thuật toán, sự kiện ngoài kênh, quảng cáo hay đường dẫn nào. Chuỗi xuất bản có thứ tự Magnus 21/10 → não bộ 28/10 → IQ 31/10 → thắng Magnus 01/11 → lịch sử 03/11. Có thể dùng như ví dụ về nhiều góc hỏi trong một cụm, không khẳng định ý đồ chủ kênh hoặc lưu lượng chuyển tiếp.

2. Tiêu đề: câu hỏi cụ thể, thường kéo người xem vào bằng “bạn”; gắn cờ với đối thủ nổi tiếng hoặc trí nhớ/IQ. Đây là lời mời tự liên hệ, có thể kiểm chứng bằng thử các cách đóng gói tương tự trên nội dung gốc. Không kết luận CTR cao vì thiếu impressions/CTR.

3. Thumbnail đã nhìn: hai ảnh cờ/nhận thức dùng nền trắng, nhân vật nét đen đầu lớn, bàn cờ, chữ đen có cụm đỏ “BỘ NÃO CỦA BẠN” hoặc “TĂNG IQ?”. Ảnh ngủ cũng cùng cách đóng gói, nhân vật buồn ngủ, cốc, đồng hồ 8H gạch đỏ, chữ “NGỦ 8 TIẾNG LÀ LỜI NÓI DỐI?”. Ảnh lịch sử dùng 6 ô thời kỳ, dòng lớn “LỊCH SỬ CỜ VUA”. Chữ/màu tạo phân cấp rõ và thể hiện câu hỏi chính; đây là nhận xét thị giác, không phép đo CTR. Ảnh ngủ có thiết kế tương tự mà view thấp hơn nhiều là lý do không quy toàn bộ kết quả cho style vẽ.

4. Mạch nội dung theo mô tả chương (chưa xác nhận bằng nghe/xem): video não bộ đặt nghiên cứu trí nhớ ở 0:00, so người mới/chuyên nghiệp 0:35, thế cờ ngẫu nhiên 1:03, rồi giải thích gom nhóm thông tin. Cấu trúc mô tả là câu đố → đối chiếu → khái niệm. Có tài liệu tham khảo công khai, nhưng chưa kiểm độ đúng của cách họ diễn giải từng nghiên cứu.

5. Mẫu bình luận: có người kể quá trình tự học, bàn về luyện tập/sai lầm; video Magnus có nhiều câu đùa tìm ngoại lệ và người phản đối lời tuyệt đối. Không xem phản đối là sự thật đã kiểm, không xem 20 bình luận là đại diện khán giả hoặc nguyên nhân gây view. Bằng chứng cho thấy lời mời tranh luận được một số người hưởng ứng; không đủ xác nhận tác động phân phối.

## Đề xuất áp dụng cho repo

- Giữ định hướng hiện hành; thử cụm câu hỏi quanh cùng trải nghiệm, thay vì đổi niche sau một snapshot của kênh khác.
- Chốt câu hỏi và hình thumbnail từ brief: một tình huống tự liên hệ, một mâu thuẫn rõ. Không sao chép nhân vật hoặc câu chữ kênh.
- Tập 6: có thể thử tiêu đề “Điện thoại ở trên bàn, sao túi bạn vẫn rung?” và ý thumbnail “MÁY Ở ĐÂY / AI RUNG?”. Đây là đề xuất chưa A/B test, chưa sửa kịch bản hoặc tạo thumbnail.
- Đưa tình huống túi trống vào 15–20 giây đầu, rồi sớm đưa một lời giải tạm đủ dùng; các giới hạn nguồn đặt sát luận điểm, tránh lặp lời tự bảo vệ khắp bài. Đây là hướng biên tập để thử, chưa là bằng chứng retention tăng.
- Mục tiêu thời lượng video của repo vẫn theo chủ repo khoảng 15 phút; mọi đoạn cần thêm câu hỏi, đối chiếu, cơ chế hoặc payoff. Metadata kênh này có video nhiều view cả 1:53 lẫn 10:35, không xác lập một thời lượng tối ưu duy nhất.
- Hình phải làm rõ ý: chủ thể/hành động hoặc trạng thái thay đổi theo từng câu/mệnh đề. Giữ số ảnh cần để phủ voice, x1 mỗi lượt Flow; tối ưu thao tác tạo, không kéo cảnh để giảm lượt.
- Đánh giá thực tế trên kênh mình bằng impressions/CTR, giữ chân 30 giây đầu và các điểm rơi khi có Analytics; không nhận tương quan snapshot là nguyên nhân.

## Bằng chứng và giới hạn

- api-snapshot.json: metadata và URL từng video.
- summary.json: cách cộng view và các giới hạn.
- comment-sample.json: mẫu bình luận theo relevance, chưa ẩn danh suy diễn người dùng.
- thumbnail-observations.jpg: 4 thumbnail đã nhìn, không phải khung hình video.

Không có Analytics nội bộ của kênh, chưa biết traffic source, tỷ lệ đăng ký theo video, nguồn trả phí, impressions, CTR hoặc retention. Không đánh giá chất lượng giọng/animation từ mô tả chương hoặc thumbnail. Không xác nhận độ đúng khoa học toàn bộ nội dung kênh.


## Bổ sung sau khi Browser Use trả kết quả

Công cụ Browser Use đã trả kết quả completed, run 9971cad8-c945-44d6-8f35-418ef2a59f3b. Công cụ báo quan sát liên tục phần hình video vSQXuflK_UQ từ 0:00 đến khoảng 1:26,5 và đọc panel transcript Vietnamese auto-generated. Assistant hiện tại nhận báo cáo của công cụ, không tự nhận đã trực tiếp xem hoặc nghe. Không có kiểm nghe audio hoặc xem toàn bộ 10:35.

Mốc hình công cụ ghi: 0:00 giới thiệu thí nghiệm năm 1973; 0:17,9 phân biệt ba trình độ người chơi; 0:40,9 người có kinh nghiệm và bàn cờ; 1:03,6 đổi sang thế cờ ngẫu nhiên; 1:26,5 hình cột thể hiện khoảng cách thu hẹp. Đây là các mốc quan sát, không phải toàn bộ lần cắt hình. Không tính thời lượng cảnh trung bình từ các mốc này.

Nhận xét biên tập từ phạm vi đã quan sát: phần mở đi vào một thí nghiệm và dùng thay đổi điều kiện để tạo câu hỏi tiếp; hình thể hiện người chơi, tình huống bàn cờ rồi kết quả so sánh. Có thể học cách để hình làm công việc giải thích ở từng bước. Chưa chứng minh nhờ vậy retention cao.

Công cụ cũng báo có liên kết giữa video não bộ, IQ, Magnus và lịch sử trong vùng mô tả mở rộng. Điều này bổ sung bằng chứng về đường dẫn xem tiếp công khai; chưa có số liệu người xem thực sự bấm liên kết.

Phạm vi báo cáo trước khi kết quả này về vẫn đúng tại thời điểm đó; từ bản bổ sung này đã có quan sát phần hình đầu video do công cụ thực hiện. Trạng thái chi tiết hiện hành ở browser-check-status.json.
