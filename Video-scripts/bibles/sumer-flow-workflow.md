# QUY TRÌNH GOOGLE FLOW: SUMER

Flow hiện có cả Image (Nano Banana) và Video (Veo 3.1). Dùng đúng tab cho từng bước.

Nếu chỉ gen ảnh: đọc mục 1, 2, 7 và 9. Bỏ qua mục 3, 4 và 8. Không cần prompt video, không cần cắt clip.

## 1. Chuẩn bị trong Flow

Tạo một project tên `SUMER`.

Tạo 3 Collection:

- `SUMER - BIBLES`: 4 model sheet và ảnh style lock.
- `SUMER - BACKGROUNDS`: 6 nền.
- `SUMER - BEATS`: 253 ảnh beat.

Sau đó:

1. Gen 4 model sheet theo `sumer-model-sheet-prompts.md`.
2. Gen 6 nền theo cùng tệp.
3. Chọn ảnh beat 1 đã duyệt làm style reference.
4. Lưu tất cả vào đúng Collection.

## 2. Gen ảnh beat

1. Chọn tab Image.
2. Chọn tỉ lệ 16:9.
3. Mở `sumer-image-prompts.txt`.
4. Copy đúng một block. Block 1 là beat 1, block 253 là beat 253.
5. Dán vào ô prompt.
6. Thêm reference:
   - 1 ảnh model sheet của nhân vật chính.
   - 1 ảnh nền tương ứng.
   - 1 ảnh style lock.
7. Tối đa 3 reference. Không nhồi 4 đến 5 ảnh.
8. Gen.
9. Kiểm tra 10 điểm QC bên dưới.
10. Dùng lasso hoặc edit để sửa tay, mắt, mũ, vật nhỏ.
11. Lưu tên `beat-001`, `beat-002`, đến `beat-253`.

Chỉ duyệt 20 ảnh đầu thật kỹ. Nếu 20 ảnh đầu trôi style, dừng lại và khóa reference.

## 3. Gen video

1. Chọn ảnh beat đã duyệt.
2. Chọn Frames to Video hoặc Ingredients to Video.
3. Dán prompt trong `sumer-video-prompt.txt`.
4. Chọn 16:9, 8 giây, audio off.
5. Chọn camera locked hoặc static.
6. Gen 5 clip test: beat 1, 4, 65, 110, 179.
7. Duyệt mặt, tay, mũ, áo, chữ.
8. Nếu ổn, chạy theo từng hồi.

Không dán prompt ảnh vào tab Video. Tab Video chỉ nhận prompt chuyển động.

## 4. Cắt clip

- Beat dưới 5 giây: gen 5 giây, cắt đúng beat.
- Beat từ 5 đến 8 giây: gen 10 giây, cắt đúng beat.
- Beat trên 8 giây: gen 10 giây, cắt đúng beat.
- Beat 10,18 giây: giữ thêm 0,18 giây ở cuối.
- Phần dư để ở cuối beat trước, không cắt giữa câu.

## 5. Lỗi Flow hay gặp

- Dán cả file 253 block: Flow chỉ ra một ảnh.
- Chọn Video cho prompt ảnh: ra clip méo hoặc không đúng bố cục.
- Đưa quá nhiều reference: mặt nhân vật bị trộn.
- Không có model sheet: Tích đổi mặt qua từng ảnh.
- Để Flow tự viết chữ: chữ rác, sai dấu.
- Xuất 16:9 nhưng bị crop: kiểm tra lại khung trước khi lưu.
- Video có audio: tắt hoặc mute, vì tiếng do VO riêng.
- Video tự zoom hoặc pan: chọn camera static.

## 6. Mẹo dùng Flow

- Dùng `@` để gọi asset trong library.
- Chia Collection theo hồi để dễ tìm.
- Ảnh gen miễn phí, video tốn credit. Duyệt ảnh thật kỹ trước khi animate.
- Giữ một ảnh style lock duy nhất cho cả 253 beat.
- Không dùng ảnh beat làm thumbnail. Thumbnail cần cận hơn và tương phản mạnh hơn.
- Nếu một ảnh chỉ sai một chi tiết, dùng lasso để sửa thay vì gen lại từ đầu.
- Lưu lại prompt đã sửa nếu muốn tái dùng cho beat tương tự.

## 7. QC ảnh

- Đúng 16:9, không crop đầu.
- Tích cao 3 đầu, người lớn cao 3,5 đầu.
- Tích vẫn áo vàng, jeans xanh, giày trắng, ba lô nâu.
- Vua vẫn mũ xanh vàng.
- Không thêm ngón tay, không thêm tay chân.
- Mặt không bị trộn giữa các nhân vật.
- Không có chữ đọc được, không watermark.
- Không trôi sang 3D, tả thực hoặc anime.
- Bối cảnh đúng plate, không có đá lớn, gỗ rừng, ngựa, tiền xu.
- Có khoảng trống cho phụ đề ở 1/3 dưới.

## 8. QC video

- Frame đầu khớp ảnh gốc.
- Không có nhân vật mới.
- Không đổi áo, tóc, mũ.
- Không lip sync, miệng không mấp máy.
- Không rung camera, không zoom out.
- Không có chữ hoặc watermark.
- Cắt đúng mốc beat.
- Frame cuối ổn định để giữ hình.

## 9. Thứ tự chạy

1. 4 model sheet.
2. 6 nền.
3. 20 ảnh beat đầu.
4. Duyệt style.
5. 233 ảnh còn lại, theo từng hồi.
6. 5 clip test.
7. Video theo từng hồi.
8. Ghép VO và phụ đề.
9. Thumbnail.
