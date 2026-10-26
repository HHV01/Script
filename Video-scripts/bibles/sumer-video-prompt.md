# PROMPT VIDEO DÙNG CHUNG: SUMER

State 6. Một prompt duy nhất cho toàn bộ 253 ảnh beat. Prompt giữ nguyên hình gốc, chỉ thêm chuyển động nhỏ để ảnh không đứng im.

## Nguyên tắc

- Ảnh beat là frame đầu tiên, không phải ảnh tham chiếu rời.
- Không đổi thiết kế nhân vật, tỉ lệ đầu, trang phục, mũ vua, màu, nét viền.
- Chỉ chuyển động nội tại: thở, chớp mắt, tay, vải, tóc, bụi, khói, nước, sậy, lửa.
- Camera khóa, hoặc đẩy vào rất chậm tối đa 3 phần trăm.
- Không lip sync. Lời kể là VO, miệng nhân vật đóng.
- Không thêm người, không thêm chi tiết, không đổi bối cảnh.
- Video 16:9, 24 fps, 5 giây. Cắt theo đúng độ dài beat.

## Prompt chính

Dán nguyên block này vào ô prompt của tool image to video. Chọn ảnh beat làm frame đầu.

```
Image to video. Use the supplied 2D cartoon illustration as the exact first frame. Preserve its composition, character designs, body proportions, thick dark outlines, flat colors, two-tone shading, and warm sand, ochre, brick red, lapis blue and olive palette. Add only restrained documentary motion: slow breathing, one blink, a small hand or head movement, cloth and hair shifting, dust drifting, smoke curling, water rippling, reeds swaying, flames flickering. Keep the camera locked. If the tool requires a camera move, use at most a three percent slow push in. Limited animation feel, long holds, no constant movement. No new characters, no extra limbs, no morphing, no style drift, no 3D, no photorealism, no anime shading, no lip sync, no talking, no mouth movement, no text, no watermark, no camera shake, no zoom out. 16:9, 24 fps, clean final frame.
```

## Bản dịch để hiểu

Không dán bản này vào tool.

Image to video. Dùng ảnh 2D cartoon được cung cấp làm frame đầu chính xác. Giữ nguyên bố cục, thiết kế nhân vật, tỉ lệ cơ thể, nét viền đậm, màu phẳng, hai tông bóng, và bảng màu cát, đất son, đỏ gạch, xanh lapis và ô liu. Chỉ thêm chuyển động tài liệu nhẹ: thở chậm, một lần chớp mắt, một cử động tay hoặc đầu nhỏ, vải và tóc lay, bụi bay, khói cuộn, nước gợn, sậy đung đưa, lửa nhấp nháy. Khóa camera. Nếu tool bắt buộc phải có chuyển động máy, đẩy vào rất chậm tối đa ba phần trăm. Cảm giác hoạt hình hạn chế, giữ hình lâu, không chuyển động liên tục. Không tạo nhân vật mới, không thêm tay chân, không biến dạng, không trôi style, không 3D, không tả thực, không anime, không lip sync, không nói, không cử động miệng, không chữ, không watermark, không rung camera, không zoom out. 16:9, 24 fps, frame cuối sạch.

## Negative prompt

Dán vào ô negative nếu tool có ô riêng. Nếu tool chỉ có một ô prompt, phần cuối prompt chính đã đủ.

```
style change, 3D render, photorealism, photorealistic, anime, detailed shading, gradient shading, new character, extra character, duplicate character, extra limbs, extra fingers, deformed hands, melted face, morphing, warping, changing costume, changing hair, changing crown, lip sync, talking, mouth movement, camera shake, fast zoom, zoom out, pan away, text, letters, subtitles, watermark, logo, flicker, frame interpolation artifacts, unrelated modern objects
```

## Cách dùng theo tool

| Tool | Chế độ | Thời lượng | Lưu ý |
|---|---|---|---|
| Veo | Image to video | 8 giây | Tắt audio, chọn 16:9, ưu tiên prompt adherence |
| Kling | Image to video | 5 hoặc 10 giây | Creativity thấp, camera fixed |
| Runway | Image to video | 5 hoặc 10 giây | Khóa camera, tắt audio |
| Hailuo | Image to video | 6 giây | Chọn 1080p, ưu tiên prompt adherence |
| Pika | Image to video | 5 giây | Motion thấp |

Tên tool và thông số có thể đổi. Nguyên tắc chung là chọn chế độ image to video, thời lượng dài hơn beat, motion thấp, camera khóa, audio tắt.

## Thời lượng

| Nhóm beat | Số beat | Cách gen | Cách cắt |
|---|---:|---|---|
| Dưới 2 giây | 21 | 5 giây | Cắt còn đúng beat, giữ frame cuối nếu cần |
| 2 đến 5 giây | 106 | 5 giây | Cắt đúng beat |
| 5 đến 8 giây | 109 | 10 giây | Cắt đúng beat |
| Trên 8 giây | 17 | 10 giây | Cắt đúng beat, beat 10,18 giây giữ thêm 0,18 giây |

Tổng 253 beat. 127 beat dùng clip 5 giây, 126 beat dùng clip 10 giây. Không gen clip ngắn hơn 5 giây vì hầu hết tool không cho.

## Đuôi chuyển động theo loại cảnh

Chỉ thêm nếu clip đầu bị đứng quá mức. Không thêm quá một đuôi cho một clip.

| Loại cảnh | Đuôi thêm | Beat ví dụ |
|---|---|---|
| Cận mặt nhân vật | one blink, tiny head tilt, mouth closed | 65, 125, 182, 184 |
| Toàn cảnh đông người | gentle parallax, people stay in place | 20, 37, 51 |
| Cận vật | dust drift, slow highlight travel, object shape fixed | 4, 7, 52, 236 |
| Bản đồ, đồ họa | arrows draw in slowly, layout fixed | 11, 21, 47, 50 |
| Nước, kênh | water ripples and flows, banks fixed | 16, 24, 42, 46 |
| Lửa, thần thoại | flames flicker, embers drift, faces fixed | 179, 180, 181, 184 |
| Khung hiện đại của Tích | clock hand moves slowly, page edge lifts, Tích stays still | 236, 237, 250 |

## Beat không nên animate mạnh

- Cận tay và cận vật: 4, 7, 52, 107, 132, 147, 171, 178, 188, 193, 221, 236, 249. Chỉ cho bụi, khói hoặc ánh sáng di chuyển. Không cho tay cử động nhiều.
- Bản đồ và đồ họa: 11, 21, 47, 50, 66, 110. Chỉ cho mũi tên vẽ chậm hoặc highlight chạy. Không cho chữ mới xuất hiện.
- Cảnh đông người: 20, 37, 51, 54, 57, 59, 96, 102, 132, 134, 145, 157, 164, 176, 179, 180, 181, 187, 193, 198, 209, 219, 246. Giữ người đứng yên, chỉ cho parallax nhẹ. Không cho mặt người đổi.
- Thần thoại: 179 đến 201. Chỉ cho lửa, khói, bụi và ánh sáng. Không cho biến hình, không cho mọc thêm đầu hoặc tay.
- Kết: 250 đến 253. Camera rất chậm, giữ Tích đứng yên, không cho thành phố mọc thêm.

## Quy trình

1. Gen ảnh beat 1 đến 9 và duyệt style trước.
2. Gen thử 5 clip: beat 1, 4, 65, 110, 179. Đây là 5 loại cảnh khó: toàn cảnh, cận vật, cận mặt, đồ họa, thần thoại.
3. Kiểm tra frame đầu, mặt, tay, mũ vua, áo Tích, chữ.
4. Chốt tool và thông số sau 5 clip thử.
5. Gen theo từng hồi, không gen lộn xộn cả 253 clip.
6. Đặt tên `beat-001.mp4` đến `beat-253.mp4`.
7. Cắt theo `sumer-beats.csv`. Phần dư để ở cuối beat trước.
8. Ghép với VO. Không dùng audio của clip.

## QC

- Frame đầu khớp ảnh gốc.
- Không có nhân vật mới.
- Tích vẫn áo vàng, jeans xanh, giày trắng, ba lô nâu.
- Vua vẫn đội mũ xanh vàng.
- Sargon và Ur-Nammu đúng mũ, đúng râu, không trộn với Vua.
- Tích cao 3 đầu, người lớn cao 3,5 đầu.
- Không thêm ngón tay, không thêm tay chân.
- Không có lip sync, miệng không mấp máy.
- Không có chữ đọc được, không watermark.
- Không trôi sang 3D, tả thực hoặc anime.
- Camera không rung, không zoom out, không pan quá xa.
- Clip cắt đúng mốc beat, frame cuối ổn định.
- Tỉ lệ 16:9, 24 fps.

## Cách rút gọn chi phí

Làm đủ 253 clip là tốn nhất. Có thể dùng chế độ hybrid:

- Animate 70 đến 90 beat khóa.
- Các beat còn lại dùng ảnh tĩnh, thêm pan hoặc zoom 2.5D trong studio.
- Beat khóa nên animate: mở hồi 1, 10, 42, 69, 104, 140, 174, 202, 225; kết 250, 253; cận mặt 65, 125, 182, 184; thần thoại 179, 180, 181; cao trào 87, 151, 221, 232.
- Beat một chữ 8 và 203 không cần animate. Giữ ảnh 1,5 đến 2 giây.

## Ghi chú kỹ thuật

- Prompt viết tiếng Anh vì hầu hết tool hiểu tiếng Anh tốt hơn.
- Nếu tool có motion strength, đặt 2/10 hoặc 0,2 đến 0,3.
- Nếu tool có camera control, chọn locked hoặc static.
- Nếu tool tự thêm âm thanh, tắt.
- Không dùng dấu gạch dài trong prompt hoặc trong tài liệu.
- Bản copy paste nằm trong `sumer-video-prompt.txt`.
