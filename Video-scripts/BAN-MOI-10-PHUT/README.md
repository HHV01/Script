# AI CẬP 10 PHÚT KIỂU GODOCS

Phiên bản mới: phim tài liệu 10 đến 11 phút, ngôi thứ ba, hình ảnh cinematic, bản đồ và sơ đồ.

Thư mục này nằm trong `Desktop\Video Studio\Video-scripts`, đặt riêng một chỗ để dễ phân biệt:

- Bản mới: `C:\Users\VNTT\OneDrive - VNTT\Desktop\Video Studio\Video-scripts\BAN-MOI-10-PHUT`
- Bản cũ 25:08: `C:\Users\VNTT\OneDrive - VNTT\Ai-Cap-Production`
- File cũ trên Desktop: `C:\Users\VNTT\OneDrive - VNTT\Desktop\Ai-Cap`

Các file cũ vẫn giữ nguyên, không bị thay đổi và không trộn với bản mới.

## ĐỌC NHANH

Ba file quan trọng nhất:

1. `00-SCRIPT/voice-script-full.txt`: toàn bộ lời đọc, không có tiêu đề hay tiêu đề chương, dùng để thu VO.
2. `02-VIDEO-ASSEMBLY/phan-canh-theo-chuong.md`: tổng quan 9 chương, nhịp phim và hướng hình ảnh.
3. `02-VIDEO-ASSEMBLY/phan-canh-98-beat.md`: bảng phân cảnh chi tiết 98 beat, có thời gian, lời kể, mô tả ảnh và tên file.

## TRẠNG THÁI

- Kịch bản: đã viết, đang chờ duyệt.
- Lời đọc full: đã tách riêng, đúng 1.367 từ.
- Phân cảnh: đã có 98 beat, tính ở 132 từ/phút.
- Tổng quan chương: đã có.
- Visual bible: đã có.
- Prompt thử: đã có 8 prompt cho đoạn mở đầu.
- Ảnh: chưa tạo.
- VO: chưa thu.
- Video: chưa dựng.

## CẤU TRÚC

```
00-SCRIPT
  voice-script-full.txt          Lời đọc full, không tiêu đề, dùng để thu VO
  ai-cap-godocs-script.txt       Kịch bản đầy đủ, có tiêu đề và tiêu đề chương
  ai-cap-godocs-treatment.md     Treatment, thông số, ghi chú sản xuất

01-SCENE-GENERATION
  ai-cap-godocs-bible.md         Visual bible, style, màu, ánh sáng, negative rules
  flow-test-01.txt               8 prompt thử cho đoạn mở đầu
  TEST-01-README.md              Tiêu chí đạt và không đạt của 8 ảnh thử

02-VIDEO-ASSEMBLY
  phan-canh-theo-chuong.md       Tổng quan 9 chương và hướng hình ảnh
  phan-canh-98-beat.md           Bảng phân cảnh chi tiết 98 beat
  phan-canh-98-beat.csv          Bản CSV để chỉnh hàng loạt
```

## THÔNG SỐ

- 1.367 từ được đọc.
- 98 beat.
- 9 chương.
- 10:21 ở 132 từ/phút.
- 10:31 ở 130 từ/phút.
- 10:07 ở 135 từ/phút.
- 16:9.
- Một ảnh cho mỗi beat.
- Không animation.
- Không có người kể xuất hiện.

## BƯỚC TIẾP THEO

1. Đọc `00-SCRIPT/voice-script-full.txt` để duyệt lời đọc.
2. Mở `01-SCENE-GENERATION/flow-test-01.txt`.
3. Tạo 8 ảnh thử, mỗi lần một prompt, tỉ lệ 16:9.
4. Lưu thành `test-01.png` đến `test-08.png`.
5. Đối chiếu với `01-SCENE-GENERATION/TEST-01-README.md`.
6. Nếu 3 ảnh neo đạt (test-01, test-02, test-08), chốt style và làm prompt cho toàn bộ 98 beat.
7. Thu VO mới ở 130 đến 135 từ/phút, lưu WAV.
8. Chỉnh `phan-canh-98-beat.csv` theo VO thật.
9. Dựng video, làm thumbnail và gói YouTube.

## LƯU Ý

- Không tạo batch từ toàn bộ file txt. Mỗi lần một prompt.
- Không để AI sinh chữ trong ảnh.
- Không dùng cartoon, anime, 3D render.
- Không dùng sắt, cần cẩu, xe tải, lạc đà hoặc xe kéo bánh trong cảnh Cổ Vương quốc.
- Không dùng em dash hoặc en dash trong tài liệu.
- Không dùng lại VO cũ 25:08 vì tốc độ đọc khác hoàn toàn.
