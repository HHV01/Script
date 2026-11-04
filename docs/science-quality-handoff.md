# Bàn giao kiểm soát chất lượng — khoa học về chính bạn

Ngày kiểm tra: 30/10/2026, giờ Việt Nam. Executor: agent `/root/science_quality_handoff`, thực hiện tác vụ đọc cấu hình/mã/tệp và viết báo cáo cho assistant điều phối. Đây là kiểm tra cấu hình độc lập với agent biên tập, **không phải duyệt nội dung thành phẩm**. Không sử dụng An/Minh/Mai/Gạo như danh tính con người hoặc bên duyệt độc lập.

## Quyết định của chủ repo

Chủ repo đã chốt niche khoa học cơ thể/cảm giác/hành vi, bối cảnh và hình thức nhân vật hiện tại. Giữ `config/characters/stick-orange.yaml`: nét than hơi lệch, nền giấy kem, đầu trắng ngà, mắt chấm lớn, thân oval cam-nâu, dấu vuông san hô ngực trái; khung ngang 16:9. Không yêu cầu chủ repo duyệt lại lựa chọn đã chốt. Sự đồng ý về hướng hình ảnh không thay việc kiểm tra từng video.

Giọng kể: tò mò, hài thông minh và kháy nhẹ tình huống/tự trào; cơ chế khoa học phải đúng dù bỏ câu hài. Không chẩn đoán khán giả, không lấy câu đùa làm kết luận khoa học.

## Hiện trạng kiểm tra được

- `projects/memory-long-01/project.yaml` có đề tài ký ức đầu đời, `minutes: 15`, nhân vật `stick-orange`, `review.enabled: false`; không có `research_sources` trong tệp đã đọc. Mục audience 18–34 là mục tiêu/giả thuyết, chưa phải nhân khẩu học được xác nhận.
- Danh sách tệp có `final.mp4`, `voice.wav`, `subtitles.srt`, `script.txt`, `scenes.json`, ảnh `001.png`–`083.png`, thumbnail và `publish.json`. Không tìm thấy phiếu nguồn, `script.review.json`, `visual-review.json`, `visual-references.json`, `video-quality.json` hoặc receipt YouTube trong danh sách dự án tại lần kiểm tra này. Tồn tại tệp không chứng minh chất lượng.
- Phần đầu kịch bản đã đọc có tình huống ảnh tuổi thơ, người mẹ nhớ nhưng nhân vật không nhớ; chưa đọc toàn bộ để kết luận cấu trúc hoặc đúng khoa học. Cảnh đầu trong JSON khai báo ảnh tĩnh và prompt đúng thiết kế nhân vật, không chứng minh ảnh thực tế nhất quán hoặc có animation.
- Theo thông tin bàn giao của assistant điều phối, API đã xác nhận [JYvoaZ7fl64](https://www.youtube.com/watch?v=JYvoaZ7fl64) public/processed lúc 16:00 ngày 30/10. Agent này không gọi lại API và chưa xác định người/công cụ upload. Không đăng lại, không tự xóa hoặc đổi trạng thái video.
- `src/pipeline/qc.py` vẫn kiểm khung 9:16, thời lượng 15–180 giây và tỷ lệ thẻ kết 9:16; không phù hợp video ngang dài. `src/pipeline/visual_review.py` đã có gate hash cùng 7 tiêu chí hình ảnh và tham khảo từ hai kênh, nhưng kiểm tra hồ sơ không chứng minh lời xác nhận là thật.
- `src/pipeline/script_review.py:require_approval` cho phép bỏ kiểm khi `review.enabled: false`; uploader gọi hàm này rồi QC. Do đó cần xử lý việc bỏ gate nguồn/kịch bản cho dự án thuộc niche mới, không chỉ sửa tỷ lệ video.

## Ưu tiên giao việc tiếp theo

1. **Khóa chống trùng cho video đã đăng:** điều phối đối chiếu API/Studio và ghi hồ sơ đối soát với video ID, thời điểm, phạm vi kiểm tra và executor thực tế; không dựng receipt như thể pipeline này đã upload. Giữ nguyên các receipt cũ. Chưa xác định uploader thì ghi rõ chưa xác định.
2. **Kiểm nguồn và lời kể hiện tại:** agent nghiên cứu lập bảng claim → nguồn đã mở/đọc → đoạn hỗ trợ → giới hạn → câu cần sửa. Agent biên tập đọc toàn bộ kịch bản theo cấu trúc dưới đây. Trả lỗi cụ thể thay vì tự điền duyệt. Đánh giá hậu kiểm video đã public không có nghĩa đã qua gate trước xuất bản.
3. **Sửa hỗ trợ long ở lần triển khai riêng:** loại nội dung rõ ràng (`short`/`long`), tỷ lệ và độ dài lấy từ cấu hình định dạng có ràng buộc; 16:9 long không bị áp 180 giây hoặc thẻ kết dọc. Giữ gate nguồn, script hash, hình ảnh và audio/subtitle; không bỏ gate để cho video này qua. Kiểm thử có ý nghĩa: long ngang hợp lệ được nhận về định dạng, ngang sai cấu hình bị chặn, video dọc bị chặn theo chính sách long-only, phiếu thiếu/sai hash vẫn chặn. Báo cáo này chưa sửa code hoặc chạy test.
4. **Hậu kiểm thành phẩm thực tế:** xem toàn bộ video, nghe toàn bộ lời kể, kiểm phụ đề và hình trên màn hình nhỏ; ghi timestamp lỗi và giới hạn công cụ. Nếu executor không thể xem/nghe thì giữ trạng thái chưa xác minh và giao công cụ/người/agent có khả năng thực tế; không chuyển nghĩa vụ kiểm duyệt thường nhật sang chủ repo.
5. **Video mới:** chỉ giao sản xuất sau brief có nguồn và kịch bản đạt. Giữ nhân vật/bối cảnh đã chốt; không kéo đủ 15 phút. Theo dõi hiệu suất thật để chọn đề tài, không cam kết lượt xem hoặc đăng ký.

## Tiêu chí tiếp nhận theo công đoạn

| Công đoạn | Bằng chứng cần có | Trả sửa/chặn khi |
|---|---|---|
| Nghiên cứu khoa học | Nguồn nghiên cứu gốc hoặc cơ quan chuyên môn đã đọc; năm, mẫu/đối tượng, điều kiện, mức chắc chắn; mapping các claim quan trọng | Chỉ có snippet/video đối thủ; suy từ chuột sang người mà không chú thích; biến giả thuyết thành sự thật; thiếu nguồn cho số liệu/cơ chế |
| Biên tập kịch bản | Một câu hỏi chính; hook tình huống → nghịch lý → giải thích theo bước → ví dụ/giới hạn → kết trả câu hỏi; claim gắn nguồn; script hash và executor | Lặp ý để kéo phút, nhiều mở bài, thiếu lời giải, ngụ ý trí nhớ biến mất tuyệt đối hoặc một cơ chế duy nhất khi nguồn không đủ; hài làm sai ý |
| Hình và storyboard | Continuity nhân vật/đạo cụ/màu/tỷ lệ; mỗi cảnh có ý và hành động; sơ đồ cơ chế đúng; timestamp bằng chứng cho hook, character, composition, mechanism, motion, continuity, mobile readability | Ảnh lệch mẫu đã chốt, lỗi tay/chân, minh họa sai cơ chế, nhiều cảnh chỉ lặp biểu cảm, chữ nhỏ/che chủ thể; gọi pan/zoom ảnh tĩnh là animation nhân vật |
| Tiếng | Nghe thực tế toàn bộ, ghi lỗi phát âm/tên khoa học, ngắt nhịp, mất/cắt/lặp câu, nhạc lấn; probe kỹ thuật chỉ là hỗ trợ | Chỉ ASR hoặc metadata; chưa nghe; lời đọc khác bản đã kiểm; mất tiếng/vỡ tiếng; chưa kiểm danh từ và đơn vị |
| Phụ đề | Đối chiếu với lời đọc thực tế, dấu tiếng Việt, ngắt dòng và timing; kiểm trên kích thước điện thoại và các cảnh dễ che nội dung | Tràn khung, đọc không kịp, sai nghĩa khoa học, trễ/sớm lặp lại; chỉ thấy SRT tồn tại |
| Đóng gói và phát hành | Tiêu đề/thumbnail đúng nội dung, nguồn mô tả, không hứa sai; phiếu theo SHA256 final; đối soát chống trùng; receipt và public/processed được xác nhận | `approved` không có kiểm tra thực tế, hash lệch, upload chưa rõ kết quả, đã có cùng video; điểm kỹ thuật bị gọi là duyệt hấp dẫn |

Riêng chủ đề ký ức đầu đời: phải tách học kỹ năng/nhận biết với ký ức tự truyện, tránh nói trẻ nhỏ không tạo ký ức; xem xét nguồn về phát triển mã hóa/truy hồi, ngôn ngữ và ảnh hưởng kể lại mà không ép tất cả thành một cơ chế. Đây là danh sách câu hỏi kiểm nguồn, chưa phải kết luận đã được nguồn xác nhận.

## Trách nhiệm và giới hạn

Assistant điều phối chịu trách nhiệm quyết định cho tiếp tục và báo cáo chủ repo. Mỗi agent ghi ID thực, tệp đã đọc, thời điểm/phạm vi, lỗi còn lại và trạng thái `chưa kiểm`/`trả sửa`/`đạt` đúng bằng chứng. Chỉ gọi có đánh giá độc lập khi đã nhận báo cáo thực tế. Không ký thay nhau.

Lần này **không** xem ảnh, phát video, nghe audio, chạy ffprobe/full QC, kiểm nguồn bên ngoài, gọi API, sửa cấu hình sản xuất, sửa phiếu approved hoặc upload. Không có chứng nhận chất lượng thành phẩm trong báo cáo này. Đây là bàn giao việc và tiêu chí tiếp nhận; chưa phải bằng chứng năng lực nội dung đã được nâng cấp.

## Cập nhật sau dọn repo30/10
QC đã chuyển long-only16:9, giới hạn mặc định60–3600giây, thẻ kết ngang; yêu cầu #shorts đã gỡ. Thiết lập review của memory đã bật để chặn tái dùng khi thiếu phiếu. Các phát hiện trên là lịch sử lần rà trước, không phải trạng thái mã hiện tại. Chưa có chứng nhận xem/nghe thành phẩm.
