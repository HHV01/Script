# Đối chiếu phần hình ảnh — Dấu Vết Văn Minh

Ngày lập: 28/10/2026 (giờ Việt Nam).

## Phạm vi và tình trạng dữ liệu

Đã đọc mã tạo prompt, cắt cảnh, render và kịch bản Giza chủ kênh đã duyệt.
Chưa xem được video/thumbnail YouTube trực tiếp trong phiên này: truy cập trang công khai bị proxy
trả 403, chưa có YOUTUBE_API_KEY hoặc phiên OAuth. Vì vậy không có bảng niche nhiều view đã xác minh,
không có nhận định rằng một kênh cụ thể đang dùng các thủ pháp dưới đây.
Những hướng hình ảnh và nhịp dựng dưới đây là phương án cần thử, không phải kết quả nghiên cứu đối thủ.

## Những điểm nhìn thấy trong repo

| Hiện trạng | Hệ quả cần kiểm tra khi xem video | Hướng cải thiện |
|---|---|---|
| config/style.yaml ép mọi ảnh thành flat vector, đồng thời loại photorealism | Không có lựa chọn thể hiện khác nhau cho tái dựng, bản đồ, hiện vật và sơ đồ | Giữ một nhận diện màu thống nhất, nhưng cho từng cảnh chọn loại hình theo việc cần giải thích |
| Prompt chỉ cần scene_desc và characters | Thiếu hồ sơ thời đại, địa điểm, đạo cụ, ánh sáng và liên tục thị giác | Storyboard ghi era/location/shot_type/focal_subject/continuity trước khi gửi Flow |
| Nhân vật tich mặc vest hiện đại có thể được ghép vào cảnh cổ đại | Người dẫn minh họa dễ bị hiểu là người có thật trong bối cảnh | Chỉ xuất hiện trong đoạn dẫn/giải thích có chủ đích, tách khỏi cảnh tái dựng lịch sử |
| Mỗi cảnh có một ảnh, thời lượng thường 4–8 giây | Nhịp đều dễ giống slideshow, chưa phục vụ đoạn cần giải thích chi tiết | Cho phép cảnh giữ lâu để đọc sơ đồ và cảnh cắt nhanh hơn khi tạo chuỗi hành động |
| s7_render.py luôn zoom vào giữa với cùng công thức | Chủ thể nằm lệch có thể bị cắt; ảnh chuyển động giống nhau | Chọn hold/push/pull/pan theo vị trí chủ thể và mục đích cảnh, có vùng an toàn phụ đề |
| Thu ảnh hiện chỉ kiểm số lượng, liên kết và dung lượng | Không phát hiện hình sai thời đại, méo, trùng bố cục hay không khớp lời | Thêm bước xem contact sheet/duyệt ảnh thực tế trước render; lỗi nào sửa đúng cảnh đó |
| Gói publish chỉ gợi ý thumbnail bằng chữ | Chưa tạo và kiểm độ đọc thumbnail thực tế | Thử 2–3 bố cục thumbnail khác nhau, so độ rõ trên điện thoại; thử nghiệm trên YouTube khi có dữ liệu |

Không có video thành phẩm thật được cung cấp để xác nhận các hệ quả ở cột giữa đã xảy ra.
Đây là các giới hạn quan sát được trong cách triển khai, không phải đánh giá CTR của kênh.

## Phương án cho chính kịch bản Giza

| Đoạn kể | Hình cần làm rõ điều gì? | Gợi ý hình | Chuyển động/nhịp đề xuất |
|---|---|---|---|
| Mở trên cao nguyên, người khai thác và xếp đá | Quy mô công việc con người | Toàn cảnh công trường tái dựng → cận tay/dây kéo → người nhỏ bên khối đá | Thay cỡ cảnh theo từng hành động; không dùng cùng một toàn cảnh cho cả mở đầu |
| Câu hỏi người Ai Cập đã xây như thế nào | Một câu hỏi trung tâm | Góc thấp từ chân công trình, có người để thể hiện tỷ lệ | Giữ ngắn một nhịp trước khi chuyển manh mối |
| Nhật ký Merer | Bằng chứng ghi chép và công việc thường ngày | Ảnh tư liệu giấy cói có nguồn/giấy phép phù hợp; nếu không có, minh họa việc ghi chép và nói rõ tái dựng | Cận chi tiết có chọn lọc; không tạo giấy cói AI rồi gọi là hiện vật thật |
| Chở đá Tura về Giza | Địa lý và vận chuyển đường thủy | Bản đồ dựa địa lý thật, nhãn Tura/Giza/Nile; xen cảnh thuyền chở đá tái dựng | Pan dọc tuyến đường; nhãn và tuyến vẽ bằng công cụ đồ họa, tránh để AI viết sai địa danh |
| Đá Tura khác đá tại Giza và granite Aswan | Phân biệt chức năng/vật liệu | Ba chi tiết vật liệu và sơ đồ phần công trình liên quan | Cận cảnh/đối chiếu trực tiếp, không chỉ minh họa kim tự tháp tổng quát |
| Các khả năng đường dốc và Hatnub | Phân biệt manh mối với kết luận | Sơ đồ các giả thuyết riêng; vị trí Hatnub tách khỏi Giza | Giữ đủ thời gian nhìn; biểu thị đây là mô hình giả thuyết, không khẳng định phương án đã được chứng minh |
| Công nhân, bánh mì, bia, dây thừng, quản lý | Hệ thống tổ chức lao động | Chuỗi cảnh nghề cụ thể, trang phục/công cụ nhất quán theo thời đại | Xen toàn → trung → cận, tránh chỉ đổi góc cùng một đoàn kéo đá |
| Công cụ và vật liệu mài | Cơ chế dễ hiểu | Sơ đồ cận đồng + vật liệu mài + đá | Chuyển động theo thao tác, không thêm máy móc hiện đại vào cảnh tái dựng |
| Định hướng bốn cạnh | Quan sát và đo đạc | Hình nhìn từ trên xuống, bốn phương và mô hình quan sát | Overlay rõ, giữ hình khi giải thích; không đánh dấu một giả thuyết là phương pháp chắc chắn |
| Muon, khoảng rỗng 2017 và hành lang 2023 | Cơ chế đo và hai cấu trúc khác nhau | Mặt cắt/sơ đồ khoa học có nguồn, phân biệt cấu trúc bằng màu/vị trí có kiểm chứng | Giữ sơ đồ và lần lượt nhấn từng khu vực; không dựng “căn phòng chứa kho báu” không có bằng chứng |
| Kết luận | Con người và khả năng phối hợp | Quay lại cảnh lao động hoặc công trình trong ánh sáng kết thúc | Nhịp chậm lại, để câu hỏi bình luận có khoảng thở |

## Ba hướng thumbnail nên thử cho Giza

1. **Quy mô con người:** một khối đá lớn, vài người nhỏ, kim tự tháp làm bối cảnh. Một chủ thể rõ,
   không nhồi hàng chục chi tiết. Gợi ý chữ ngắn: “AI ĐÃ XÂY?”.
2. **Manh mối Merer:** giấy cói thật có nguồn và công trình đối chiếu; không tạo hiện vật giả làm bằng chứng.
   Gợi ý chữ: “DẤU VẾT MERER”.
3. **Điều còn chưa rõ:** mặt cắt có nguồn với khu vực đo được nhấn màu; thể hiện là sơ đồ,
   không dựng đồ vật chưa tìm thấy trong khoảng rỗng. Gợi ý chữ: “KHOẢNG RỖNG NÀY?”.

Đây là concept thử nghiệm. Chưa có thumbnail được tạo, chưa có CTR để chọn phương án thắng.
CTR liên quan đến đóng gói và nguồn phân phối; thời lượng xem liên quan trải nghiệm cả video.
Không dùng view tích lũy để kết luận riêng hình ảnh gây ra thành công.

## Lấy mẫu thực tế sau khi kết nối

```bash
python run.py research-visuals --days 90 --results 5 --min-views 50000 --duration medium
```

Bốn nhóm tìm kiếm là Ai Cập/kim tự tháp, đế chế, thành phố cổ mất tích và bản đồ lịch sử.
Đây là các ứng viên phù hợp kênh, chưa phải bốn niche nhiều view được xác minh.
`medium` theo YouTube là 4–20 phút; đổi `long` khi cần đối chiếu video dài hơn.
Mỗi lượt mặc định có 4 search.list, khoảng 400 quota units cộng lượt đọc chi tiết.

Tệp `.studio/visual-benchmark/latest.json` và `latest.md` có ngày lấy, ngày đăng,
view/like/comment, link video, thumbnail gốc, điều kiện lấy mẫu và giới hạn. Ngưỡng 50 nghìn là
một lựa chọn lọc, không là chứng cứ rằng niche đó đang tốt nhất. Thay đổi ngưỡng nếu mẫu quá ít.

API chỉ cung cấp metadata và URL thumbnail. Phải thật sự xem hình/video và ghi timestamp
trước khi kết luận họ dùng bố cục, màu sắc, cỡ cảnh, bản đồ, nhịp cắt hoặc chuyển động như thế nào.
Trường visual_observations để null cho tới khi có quan sát thật. Chỉ dùng làm tham khảo, không sao chép ảnh của kênh khác.
