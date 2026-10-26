# PACK NHÂN VẬT VÀ PROMPT — phong cách Vẽ Vời

Bộ này để một nhân vật duy nhất đi xuyên suốt cả kênh lịch sử, đổi thời kỳ bằng trang phục và bối cảnh, không đổi mặt, không đổi nét.

## 1. Trong thư mục này có gì

| Tệp | Dùng để |
|---|---|
| `ve-voi-bible.txt` | Dán vào ô "Nhân vật chủ đạo" của studio. Chứa style lock, identity, thẻ biểu cảm, dáng, trang phục, đạo cụ |
| `ve-voi-roster.json` | Nhân vật phụ và bối cảnh, thêm vào roster của kênh |
| `ve-voi-samples.md` | Prompt mẫu đã ghép đúng thứ tự composer |
| `sumer-scenes.md` | 12 cảnh mẫu cho video Sumer, kèm lời kể và ghi chú |
| `ve-voi-prompt-pack.md` | Tệp này, quy trình và luật |

## 2. Đưa vào studio, 3 bước

1. Mở kênh, vào ô nhân vật chủ đạo, dán nguyên văn `ve-voi-bible.txt`.
2. Thêm `Bắp`, `Bà Then`, `Sói`, `Lugal` và các bối cảnh từ `ve-voi-roster.json`.
3. Đặt `promptLanguage = 'en'` và để `visualStyle` trống.

Vì sao để `visualStyle` trống: composer lấy style của bible. Nếu điền, nó ghi đè và bạn mất style lock. Chỉ điền khi muốn đổi style cho cả kênh.

Vì sao `promptLanguage = 'en'`: chế độ `vi` sẽ dịch nhãn thẻ sang tiếng Việt trước khi gửi model ảnh. Model ảnh hiểu tiếng Anh tốt hơn hẳn, nhất là các từ như "kaunakes", "cuneiform", "halftone".

## 3. Ba lớp khóa nhất quán

**Lớp 1, văn bản.** Style lock và identity lặp y nguyên trong mọi prompt. Không diễn giải lại, không rút gọn, không đổi dấu câu. Trôi nhân vật gần như luôn đến từ việc người viết tự mô tả lại nhân vật bằng từ khác.

**Lớp 2, ảnh tham chiếu.** Gen một bảng tham chiếu trước khi làm video: 4 góc nhìn, 8 biểu cảm, nền trắng. Lưu `refs/co_sheet.png`. Mỗi lần gen ảnh, đính kèm ảnh này làm reference. Midjourney dùng `--cref`, Seedream hoặc Nano Banana dùng ảnh tham chiếu, Flux dùng Kontext hoặc IP-Adapter.

**Lớp 3, tệp.** Bible là tài sản của kênh. Sửa thì tạo phiên bản mới, ví dụ `ve-voi-bible-v2.txt`, và chỉ đổi giữa các dự án. Đổi giữa dự án sẽ làm cảnh đã ghép lệch với cảnh mới.

## 4. Vì sao prompt ngắn mà vẫn giữ nhân vật

Composer ghép theo thứ tự cố định:

```
style lock
identity (nguyên văn, khoảng 45 từ)
Outfit, chỉ in khi khác default
Expression
Pose
Prop
Setting, tối đa 12 từ
Camera
Extra graphics
```

Mỗi cảnh chỉ tốn thêm khoảng 25 đến 35 từ cho thẻ. Một video 100 cảnh rơi vào khoảng 9k đến 11k token, phần lớn là identity lặp lại, và phần lặp đó được prompt cache tính giá rẻ.

Điều quan trọng: AI không được tự viết prompt. Nó chỉ chọn thẻ từ menu. Người viết prompt là code. Đây là lý do hệ thống không trôi.

## 5. Chọn thẻ cho từng cảnh

| Tình huống trong lời kể | Expression | Pose | Prop |
|---|---|---|---|
| Phát hiện điều mới | awe, curious | leaning-in, pointing | vật vừa phát hiện |
| Giải thích cơ chế | neutral, smug | presenting, holding-object-up | mô hình, bảng |
| Nguy hiểm | terrified, shocked | running, hiding-behind-rock | giáo, đuốc |
| Lao động | exhausted, neutral | digging, carrying-load | xẻng, giỏ |
| Ghi chép, tri thức | curious, proud | writing, sitting-cross-legged | bảng đất sét, bút sậy |
| Quyền lực | proud, smug | arms-crossed, standing | vương miện, con dấu |
| Châm biếm, hài | deadpan, skeptical | shrugging, facepalm | bất kỳ |
| Kết bài, đọng lại | neutral, deadpan | standing, arms-crossed | không cần |

Luật nhỏ: mỗi cảnh chỉ một biểu cảm chính, một đạo cụ chính. Hai đạo cụ trở lên là model bắt đầu vẽ sai tay.

## 6. Câu bối cảnh, luật 12 từ

Tối đa 12 từ, chỉ tả nơi chốn và ánh sáng, không tả lại nhân vật.

Đúng: `mudbrick city wall, dust haze, low sun`
Sai: `a skinny caveman with spiky hair standing at a mudbrick wall`

Studio sẽ cảnh báo nếu câu bối cảnh chứa từ về ngoại hình hoặc màu sắc. Đó là cảnh báo thật, không phải nhiễu.

## 7. Negative prompt

Dùng cho tool có ô negative, hoặc thêm cuối prompt nếu tool không có ô riêng:

```
text, letters, watermark, logo, signature, photorealistic, 3d render, anime,
extra fingers, deformed hands, extra limbs, duplicate character, cropped head,
modern clothing, shoes, glasses, blurry, low contrast, muddy colors
```

Không đưa `no text` vào negative nếu bạn cần chữ trong ảnh thumbnail. Chữ thumbnail nên thêm ở editor, không để AI vẽ.

## 8. Thumbnail

Công thức ăn khách của kênh tham chiếu: một nhân vật phản ứng mạnh ở trái, một vật thể phóng đại ở phải, chữ vàng viền đen ở trên.

- Khung 1280x720, chừa 15% lề trên cho chữ.
- Nhân vật chiếm 35 đến 45% chiều ngang, mặt hướng về vật thể.
- Vật thể chiếm 30 đến 40%, to hơn thực tế, có chi tiết lạ để gây tò mò.
- Một mũi tên đỏ hoặc vòng tròn đỏ chỉ đúng chi tiết đáng chú ý.
- Chữ 3 đến 5 từ, vàng, viền đen dày, hơi nghiêng, mỗi từ một cỡ.
- Ảnh phải đọc được khi thu nhỏ còn 20%.

Prompt nền, chưa có chữ:

```
[style lock] + [identity] + Expression: shocked + Pose: pointing +
Prop: [vật thể] + Setting: plain warm backdrop + Camera: medium +
empty space at the top third for a title, high contrast, 16:9
```

## 9. Quy trình một video

1. Chốt lời kể, chia cảnh theo nhịp thở của người kể, không chia theo câu.
2. AI chọn thẻ cho từng cảnh từ menu bible.
3. Gen 2 biến thể mỗi cảnh, đính kèm ảnh tham chiếu.
4. QC 10 giây mỗi ảnh, chọn ảnh đạt.
5. Đặt tên `beat_001.png`, `beat_002.png`, đúng số cảnh.
6. Dựng: ảnh tĩnh, pan hoặc zoom nhẹ 3 đến 5%, cắt theo nhịp lời kể.
7. Thêm chữ, mũi tên, khoanh đỏ ở editor. Không bao giờ để AI vẽ chữ.
8. Xuất, kiểm tra lại một lượt ở màn hình điện thoại.

## 10. QC 10 giây mỗi ảnh

- Mắt to tròn, hai mắt cùng hướng.
- Tóc đúng silhouette, không bị mũ che.
- Leopard wrap còn ở vai trái.
- Vòng cổ còn thấy.
- Bàn tay đủ 5 ngón, không dính vào đạo cụ.
- Không có chữ, không có watermark.
- Không lẫn chất liệu 3D, anime, hay ảnh thật.
- Còn khoảng trống cho phụ đề dưới đáy.

Ảnh sai một mục trong danh sách này thì bỏ, đừng sửa bằng prompt. Sửa bằng cách gen lại với cùng thẻ, rẻ hơn.

## 11. Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| Mặt đổi sau 20 ảnh | Không đính ảnh tham chiếu | Luôn kèm `co_sheet.png` |
| Nhân vật bị mô tả hai lần | Viết ngoại hình vào setting | Chỉ tả bối cảnh, dưới 12 từ |
| Prompt phình to | Thêm câu dẫn, trạng từ | Chỉ dùng thẻ, để composer ghép |
| Cảnh cũ hỏng sau khi sửa bible | Đổi nhãn thẻ | Tag sinh từ nhãn, đổi nhãn là đổi tag |
| Style lẫn lộn | Điền `visualStyle` đè lên bible | Để trống |
| Chữ trong ảnh bị sai | Để AI vẽ chữ | Thêm chữ ở editor |

## 12. Mở rộng sang thời kỳ khác

Không tạo nhân vật mới cho mỗi thời kỳ. Chỉ thêm ba thứ vào bible hiện có:

- Một outfit, ví dụ `egypt-scribe`, `roman-legionary`.
- Ba đến năm prop của thời kỳ đó.
- Ba đến năm background.

Nhân vật giữ nguyên mặt, tóc, mắt, vòng cổ. Đây là thứ tạo cảm giác "kênh có nhân vật riêng" chứ không phải "kênh ghép ảnh AI".

Sumer đã có sẵn trong bản này: `sumer-worker`, `sumer-scribe`, `sumer-narrator`, cùng 10 prop và 7 bối cảnh.
