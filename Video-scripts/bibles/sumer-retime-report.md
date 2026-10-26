# CĂN LẠI MỐC BEAT THEO VO THỰC TẾ

## Nguồn

- File: `Voice_sumer_full.wav`
- Định dạng: WAV, mono, 24 kHz, 32-bit float
- Thời lượng: 1.255,05 giây = 20:55,05
- Lời sau khi cắt: 4.816 từ, khớp `sumer-script-clean.md`
- Nhận dạng: faster-whisper large-v3-turbo, word timestamps, tiếng Việt
- Bản gốc 4.845 từ, nhận dạng 4.799 từ, 177 khác biệt, độ khớp 96,35 phần trăm

## Kết quả

- 253 beat, tổng 1255,05 giây = 20:55,05
- Trung bình 4,96 giây một beat
- Ngắn nhất 0,58 giây, trung vị 5,00 giây, dài nhất 10,18 giây
- 5 beat dưới 1 giây, 21 beat dưới 2 giây, 52 beat dưới 3 giây

## Hồi

| Hồi | Beat | Bắt đầu | Kết thúc | Thời lượng |
|---|---|---|---|---|
| 0. Cold open | 1 đến 9 | 0:00 | 0:39 | 39,5 giây |
| 1. Vùng đất sai lầm | 10 đến 41 | 0:39 | 3:18 | 158,8 giây |
| 2. Dắt nước | 42 đến 68 | 3:18 | 5:30 | 131,8 giây |
| 3. Cỗ máy biến lúa thành người | 69 đến 103 | 5:30 | 8:08 | 158,1 giây |
| 4. Chữ bắt đầu bằng nợ | 104 đến 139 | 8:08 | 11:08 | 180,1 giây |
| 5. Thần, vua, bánh xe | 140 đến 173 | 11:08 | 14:08 | 180,1 giây |
| 6. Người không chấp nhận chết | 174 đến 201 | 14:08 | 16:31 | 142,8 giây |
| 7. Muối | 202 đến 224 | 16:31 | 18:35 | 124,5 giây |
| 8. Dấu vết còn lại | 225 đến 253 | 18:35 | 20:55 | 139,3 giây |

## Beat ngắn dưới 2 giây

| Beat | Bắt đầu | Thời lượng | Lời |
|---|---|---|---|
| 110 | 8:34 | 0,58 giây | Một danh sách. |
| 156 | 12:35 | 0,60 giây | Và bia. |
| 8 | 0:33 | 0,62 giây | Muối. |
| 24 | 1:54 | 0,88 giây | Là nước. |
| 151 | 12:11 | 0,97 giây | Để chở hàng, họ cần bánh xe. |
| 69 | 5:30 | 1,00 giây | Lúa. |
| 203 | 16:33 | 1,05 giây | Muối. |
| 196 | 16:07 | 1,20 giây | Ông còn thành phố. |
| 103 | 8:06 | 1,22 giây | Con số đó là nợ. |
| 201 | 16:30 | 1,24 giây | Người thứ hai thành công. |
| 65 | 5:15 | 1,32 giây | Nghe quen không? |
| 184 | 15:10 | 1,50 giây | Và ông bắt đầu sợ. |
| 244 | 20:10 | 1,56 giây | Và họ vẫn tiếp tục xây. |
| 125 | 9:55 | 1,58 giây | Và đó chính là điều đáng sợ. |
| 61 | 4:52 | 1,62 giây | Trung tâm đó là ngôi đền. |
| 121 | 9:29 | 1,64 giây | Chữ biến ký ức thành tài sản. |
| 41 | 3:16 | 1,78 giây | Nhưng chúng ta đang đi trước quá nhanh. Hãy quay lại với hai con sông. |
| 138 | 11:00 | 1,80 giây | Chữ là công nghệ cai trị đầu tiên. |
| 92 | 7:14 | 1,94 giây | Nhưng cỗ máy nào cũng có giá. |
| 82 | 6:24 | 1,96 giây | Hãy hình dung con số đó. |
| 227 | 18:44 | 1,98 giây | Nhưng đất sét đã nung thì thành đá. |

## Cụm đã cắt khỏi phụ đề

| Beat | Mốc beat | Cụm lời |
|---|---|---|
| 37 | 2:54 | Bạn xây lại lần nữa. |
| 41 | 3:16 | Hãy quay lại với hai con sông. |
| 50 | 3:56 | Bạn phải biết khi nào gieo. |
| 87 | 6:46 | một ngày công đáng bao nhiêu lúa |
| 151 | 12:11 | họ cần bánh xe. Bánh xe |

Năm cụm này có trong bản script gốc và `VO/sumer-vo-full.txt` nhưng không nghe thấy trong file WAV. Ngày 22/10/2026 đã cắt chúng khỏi `sumer-script-clean.md`, `sumer-beats.csv`, `sumer-beats.md` và `sumer-beats.txt` để phụ đề khớp audio. Beat 151 chỉ còn 0,97 giây vì câu bị thiếu trong audio.

## Ghi chú

- Mốc beat lấy theo thời điểm bắt đầu của từ đầu tiên trong beat. Beat trước giữ hình đến khi beat sau bắt đầu, nên khoảng nghỉ nằm ở cuối beat trước.
- Beat 8 và beat 203 rất ngắn. Nếu muốn giữ hình lâu hơn, gộp vào beat trước hoặc thêm 1 đến 2 giây ở hậu kỳ.
- Đã cập nhật `sumer-beats.md`, `sumer-beats.csv`, `sumer-beats.txt` và `sumer-image-prompts.csv`.
- Không đổi lời, hình, nhân vật, bối cảnh hay prompt ảnh.
