# Hướng dẫn sản xuất video dài khoa học

Định hướng chuẩn: `config/channel-direction.yaml`. Nhân vật chuẩn: `config/characters/stick-orange.yaml`. Bối cảnh đời thường/nền giấy kem, nét vẽ thống nhất, khung ngang 16:9. Không kéo dài video chỉ để đủ số phút.

## 0. Kiểm tra trước khi chạy

Đọc [hướng dẫn bàn giao AI](docs/AI-START-HERE.md), sau đó chạy `python run.py doctor ten_video --json` với project có thật (hoặc bỏ tên để kiểm tra môi trường). Đây là chẩn đoán offline, không tạo nội dung và không xác minh tài khoản/quota. Dùng cùng Python của môi trường đã cài theo README.

## 1. Chuẩn bị project và nguồn

```text
python run.py new ten_video
```

Sửa `projects/ten_video/project.yaml`: `topic`, `niche`, `audience`, `minutes`, `characters` và các ghi đè `settings`. Dùng nhân vật `stick-orange`; độ dài là mục tiêu biên tập, không phải thời lượng đã đo.

Đọc nguồn nghiên cứu hoặc cơ quan chuyên môn, lưu `research_sources` với URL, tên tài liệu, phần thực sự đã đọc và giới hạn kết luận. Không dùng tiêu đề video hoặc câu trả lời model làm nguồn khoa học. Chốt dàn ý trước sản xuất: tình huống mở → câu hỏi/nghịch lý → cơ chế theo từng ý → ví dụ/giới hạn → trả lời và kết.

## 2. Viết và duyệt kịch bản

```text
python run.py run ten_video --only script
python run.py run ten_video --only review
```

`script.txt` là lời đọc. Hồ sơ review và kế hoạch thu phải khớp bản kịch bản hiện tại. Đọc cấu trúc và kiểm chứng nguồn thực tế; điểm model không thay kiểm chứng. Hài đến từ liên tưởng đời thường rồi quay lại giải thích, không bịa cơ chế để gây cười. Tắt `review.enabled` không có nghĩa đã duyệt.

## 3. Thu giọng và chia cảnh

```text
python run.py run ten_video --only voice
python run.py run ten_video --only scenes
```

VieNeu chạy cục bộ theo `voice.vieneu` trong settings; lần đầu có thể cần tải model. Chọn giọng có sẵn bằng `voice`, hoặc mẫu giọng có quyền sử dụng qua `ref_audio`. Chế độ `manual` nhận audio cung cấp riêng và dùng nhận dạng để căn thời gian.

`voice.words.json` hỗ trợ căn cảnh/phụ đề; mốc từ có thể được ước lượng hoặc nhận dạng, không chứng minh từng chữ đã đọc đúng. Phải nghe thực tế. Sau sửa kịch bản, duyệt lại và tạo lại phần phụ thuộc. Không giữ phiếu hoặc audio của bản cũ để vượt kiểm tra.

Chạy `scenes --force` tạo lại phân cảnh và có thể mất liên kết prompt/ảnh; sao lưu phần biên tập cần giữ trước khi thực hiện.

## 4. Hình ảnh và tính liên tục

```text
python run.py run ten_video --only prompts
python run.py run ten_video --only collect
```

Kiểm tra `prompts.txt` và `scenes.json`: cùng nhân vật, màu sắc, không gian; mỗi cảnh minh họa đúng một ý/cơ chế. Ảnh phải đủ rõ cho khung 16:9 và màn hình điện thoại.

Tạo ảnh bên ngoài, lưu vào `hinh/canh-001.png`, `hinh/canh-002.png`… rồi chạy `collect` để kiểm ảnh cục bộ. Code auto Flow đã gỡ.

Có thể cung cấp ảnh thủ công rồi gắn đường dẫn tương ứng trong cảnh. Không lấy một ảnh bất kỳ trong thư viện làm kết quả cảnh. Hậu kiểm liên kết cảnh–ảnh và xem nội dung thực tế. Zoom/crop ảnh tĩnh không đồng nghĩa hoạt hình nhân vật.

## 5. Dựng và metadata

```text
python run.py run ten_video --only render
python run.py run ten_video --only publish
```

Cấu hình `render` quyết định kích thước, fps, phụ đề và chuyển động ảnh; chuẩn hiện tại là 1920×1080. Đầu ra gồm `final.mp4`, `subtitles.srt` và metadata xuất bản. Kiểm tra kích thước/thời lượng/codec chỉ là kiểm tra kỹ thuật, không chứng minh mỹ thuật, lời đọc hay phụ đề đạt.

**Xuất bản cần yêu cầu rõ:** lệnh sản xuất mặc định không upload, kể cả khi project có cấu hình auto-upload cũ. `publish` chỉ chuẩn bị metadata. Chỉ thêm `--upload` khi thực sự muốn xuất bản và các cổng đã đạt. `--from` chạy tất cả bước tiếp sau; `--force` có thể ghi đè và gọi API tốn phí.

## 6. Kiểm tra và xuất bản

```text
python run.py run ten_video --only qc
```

Trước uploader cần kiểm nguồn, kịch bản, hình, tiếng và phụ đề trên đúng bản cuối. Hồ sơ nêu executor thật, thời điểm, phạm vi, lỗi còn lại và SHA256. `visual-review.json` phải có quan sát theo mốc thời gian; `visual-references.json` ghi quan sát video tham khảo thực sự đã xem, không sao chép.

Không tạo chứng nhận đã xem/nghe khi chỉ đọc transcript, ASR hoặc xem vài khung hình. Không tự sửa cờ duyệt để vượt cổng. Nếu QC còn quy tắc định dạng/thời lượng cũ thì sửa và kiểm thử hỗ trợ long trước, giữ chặn upload trong lúc chưa tương thích.

`publish.json` là nội dung chuẩn bị đăng. Upload cần đúng quyền OAuth, đúng kênh và đủ gate. Sau upload đối chiếu biên nhận, URL, processing status và privacy status. Kết quả chưa rõ phải kiểm tra Studio trước khi thử lại; không xóa receipt hoặc hồ sơ chống trùng.

## Vận hành và xử lý lỗi

Chỉ một worker sản xuất; không tự bật lại hàng đợi/brief cũ. Mở studio theo README, xem trạng thái worker thực tế. App đang mở không có nghĩa lịch đang bật hoặc tác vụ đang chạy.

- Thiếu provider/key hoặc hết quota: ghi lỗi, không gọi là hoàn tất và không tự chuyển provider có phí ngoài cấu hình.
- Thiếu FFmpeg: kiểm tra PATH hoặc cài FFmpeg/ffprobe rồi mở lại terminal.
- Thiếu ảnh/ảnh trùng/sai cảnh: sửa liên kết hoặc tạo lại cảnh lỗi, không dựng thay bằng ảnh không liên quan.
- Voice hay phụ đề sai: sửa và tạo lại các phần phụ thuộc, thu hồi phiếu của bản trước.
- Không đủ dữ liệu hiệu suất: ghi chưa đủ dữ liệu; không quy kết nguyên nhân hoặc hứa tăng trưởng.

Không chia sẻ `.env`, token OAuth hoặc profile browser khi bàn giao. Giữ lịch sử xuất bản và bằng chứng kiểm duyệt cần thiết ngay cả khi dọn tài nguyên thử nghiệm.
