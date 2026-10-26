# HƯỚNG DẪN PROMPT ẢNH: SUMER

State 5 đã xong. Mỗi beat có đúng một prompt ảnh, tổng 253 prompt, cách nhau bằng một dòng trống.

## Tệp

| Tệp | Nội dung |
|---|---|
| `sumer-image-prompts.txt` | 253 prompt, mỗi block là một beat, block 1 là beat 1 |
| `sumer-image-prompts.csv` | Bảng đối chiếu prompt, beat, mốc giờ, nhân vật, bối cảnh, máy, số từ |
| `sumer-prompt-blocks.md` | Block nhân vật, bối cảnh, ánh sáng, máy để ghép cảnh mới |
| `prompts-src/` | Generator và 3 tệp scene để sinh lại 253 prompt |
| `sumer-beats.md` | Bảng beat gốc, dùng để duyệt lời và hình |
| `sumer-script-clean.md` | Lời kể chuẩn cho phụ đề |

## Cách dùng file txt

1. Mở `sumer-image-prompts.txt`.
2. Mỗi block cách nhau bằng một dòng trống. Không thêm số beat vào prompt.
3. Block thứ nhất là beat 1, block thứ 253 là beat 253.
4. Copy nguyên một block cho một lần gen. Không copy cả file vào một lần gen.
5. Nếu tool có ô prompt và ô negative riêng, dán block vào prompt, dán negative trong `sumer-prompt-blocks.md` vào ô negative.
6. Nếu tool chỉ có một ô, giữ nguyên block. Negative ngắn đã nằm ở cuối mỗi prompt.

## Thông số

- Số prompt: 253.
- Tổng từ: 34.483.
- Trung bình: 136,3 từ một prompt.
- Ngắn nhất: 107 từ.
- Dài nhất: 207 từ.
- Tỉ lệ: 16:9.
- Độ phân giải đề xuất: 1920x1080, hoặc 2560x1440 nếu muốn crop và pan.
- 91 prompt có ghi chú chữ hình nêm. Chữ hình nêm là họa tiết, không phải chữ đọc được.

## Thứ tự sản xuất

1. Gen 4 model sheet theo `sumer-model-sheet-prompts.md`. Duyệt tỉ lệ và mặt trước.
2. Gen 6 nền theo cùng tệp. Duyệt màu, vật liệu, độ sâu.
3. Gen ảnh beat 1 đến 9 để kiểm tra style lock và Tích.
4. Gen theo từng hồi, không gen lộn xộn cả 253 ảnh.
5. Duyệt 20 ảnh đầu trước khi chạy tiếp. Nếu style trôi, dừng và khóa lại reference.
6. Ghép ảnh vào studio theo `sumer-beats.txt`, đối chiếu mốc giờ trong `sumer-image-prompts.csv`.

## Bảng hồi và prompt

| Hồi | Beat | Prompt | Nội dung |
|---|---|---|---|
| 0 | 1-9 | 1-9 | Mở đầu, đồng bằng trống, muối |
| 1 | 10-41 | 10-41 | Đất giữa hai sông, bùn, sậy, thành phố đầu tiên |
| 2 | 42-68 | 42-68 | Lũ, kênh, đền, tổ chức lao động |
| 3 | 69-103 | 69-103 | Lúa mạch, thặng dư, chợ, nợ, chiến tranh |
| 4 | 104-139 | 104-139 | Chữ, token, hợp đồng, trường học, luật |
| 5 | 140-173 | 140-173 | Ziggurat, vua, thương mại, bánh xe, bia, Sargon |
| 6 | 174-201 | 174-201 | Gilgamesh, thần thoại, cái chết, bức tường |
| 7 | 202-224 | 202-224 | Muối, đất chết, ngôn ngữ mất, thành phố bỏ |
| 8 | 225-253 | 225-253 | Bảng đất, khảo cổ, Rawlinson, kết |

## Luật nhân vật

- Tích cao 3 đầu. Người lớn cao 3,5 đầu. Đầu Tích chỉ tới ngực người lớn.
- Tích mặc áo vàng, quần jeans xanh, giày trắng, ba lô nâu trong mọi cảnh.
- Tích không già đi. Nông Dân và Thư Lại cũng không già đi. Họ là nguyên mẫu, không phải một người sống qua nhiều thế kỷ.
- Vua Sumer giữ mũ xanh vàng trong mọi cảnh. Không bỏ mũ.
- Sargon dùng model Vua, mũ đồng, râu ngắn. Beat 161, 164, 168.
- Ur-Nammu dùng model Vua, mũ đồng có sừng, râu dày. Beat 134.
- Gilgamesh, Enkidu, Utnapishtim, Humbaba, bò thần, vợ Utnapishtim và Rawlinson là thiết kế một lần. Không tái dùng sang cảnh khác nếu không có trong prompt.
- Người dân thường là vai một lần. Không gán mặt của 4 nhân vật chính cho đám đông.

## Luật bối cảnh

- Sáu plate gốc: cổng thành, ziggurat, kênh, nhà bảng, bến sông, đồng muối.
- Bối cảnh mở rộng: hai con sông, kho lúa, phố hẹp, nhà nghèo, vách đá, công trường gạch, sân trong, đồng bằng, ruộng, đầm lầy, chợ, đền, phòng ngai, tường thành, phế tích, bàn hiện đại, phòng nghiên cứu, không gian thần thoại, nền đồ họa.
- Vài beat dùng setting riêng trong prompt để tránh xung đột với hình: 3 và 10 dùng hai con sông, 73 dùng kho lúa, 93 và 218 và 222 dùng phố hẹp, 94 dùng nhà nghèo, 232 dùng vách đá, 244 dùng công trường, 245 dùng sân trong. Cột `set` trong `sumer-image-prompts.csv` là set hiệu dụng.
- Không có đá lớn, không có gỗ rừng, không có ngựa, không có tiền xu, không có giấy trong cảnh cổ đại.
- Gạch nung trong cảnh tường Gilgamesh là biểu tượng, không phải bằng chứng khảo cổ.
- Ánh sáng thần thoại bắt đầu từ beat 179. Beat 174 đến 178 vẫn là ánh sáng lịch sử.
- Bàn hiện đại của Tích là không gian khung, tách khỏi Uruk. Chỉ dùng cho beat 236, 237 và 250. Beat 249 dùng phế tích, nhưng đồng hồ vẫn là vật hiện đại của Tích.

## Cảnh nhiều nhân vật

Prompt đã ghi đủ identity cho từng người. Nếu model trộn mặt hoặc thiếu người, làm theo thứ tự sau:

1. Gen nền trước, không có nhân vật.
2. Gen từng nhân vật trên nền trong suốt, dùng đúng block trong `sumer-prompt-blocks.md`.
3. Ghép trong studio, giữ đúng tỉ lệ 3 đầu và 3,5 đầu.
4. Chỉ dùng prompt nhiều nhân vật khi model giữ được ít nhất 2 người rõ mặt.

Các beat dễ trộn mặt: 57, 84, 91, 96, 102, 132, 134, 145, 157, 164, 176, 179, 180, 181, 187, 193, 198, 209, 219, 246.

## Cảnh cận tay và cận vật

Một số beat có nhân vật trong bảng nhưng hình chỉ là tay hoặc vật. Prompt đã thay camera bằng framing riêng. Không thêm mặt vào các beat này:

- 4, 107: tay Thư Lại và bảng đất.
- 132: tay vua, tay thư lại, bảng và con dấu.
- 147: tay vua và cái bóng.
- 171: tay Thư Lại và bảng kê.
- 178: tay Gilgamesh siết tường.
- 188: tay vợ Utnapishtim.
- 193: tay Gilgamesh trên tường.
- 221: tường cháy, không người.
- 236, 249: cổ tay Tích và đồng hồ.

## Negative prompt

Cảnh cổ đại:

```
text, letters, watermark, logo, signature, photorealistic, 3d render, anime, gradient shading, extra fingers, deformed hands, extra limbs, duplicate character, cropped head, inconsistent proportions, modern objects, modern clothing, watches, paper, glass, plastic, coins, horses, Roman armor, Greek helmets, chibi, cute, pastel, soft focus
```

Cảnh cổ đại có Tích:

```
text, letters, watermark, logo, signature, photorealistic, 3d render, anime, gradient shading, extra fingers, deformed hands, extra limbs, duplicate character, cropped head, inconsistent proportions, coins, horses, Roman armor, Greek helmets, chibi, cute, pastel, soft focus
```

Cảnh khung hiện đại của Tích, cho phép đồng hồ, giấy, bút:

```
text, letters, watermark, logo, signature, photorealistic, 3d render, anime, gradient shading, extra fingers, deformed hands, extra limbs, duplicate character, cropped head, inconsistent proportions, Roman armor, Greek helmets, chibi, cute, pastel
```

Không đưa `cuneiform` vào negative. Chữ hình nêm là họa tiết hợp lệ.

Vì Tích mặc áo vàng, jeans, giày trắng và ba lô nâu trong mọi cảnh, không dùng negative có `modern objects, modern clothing, watches, paper, glass, plastic` cho cảnh có Tích. Beat 249 dùng negative hiện đại vì có đồng hồ, dù bối cảnh là phế tích.

## Kiểm tra trước khi gen hàng loạt

- Đã gen và duyệt 4 model sheet.
- Đã gen và duyệt 6 nền.
- Ảnh lineup cho thấy Tích thấp hơn người lớn đúng 0,5 đầu.
- Prompt 1 đến 9 giữ đúng style lock, không bị anime, không bị 3D.
- Không có chữ hiện đại đọc được trong ảnh cổ đại.
- Không có giày trên chân người Sumer.
- Vua Sumer vẫn đội mũ trong mọi cảnh.
- Tích vẫn mặc áo vàng trong mọi cảnh.
- Cảnh thần thoại từ beat 179 dùng xanh đêm và vàng lửa.
- Ảnh 16:9, không bị crop đầu.

## Lưu ý studio

- Beat 8 (0,62 giây) và beat 203 (1,05 giây) là beat một chữ. Giữ hình ít nhất 1,5 đến 2 giây, hoặc gộp vào beat trước nếu muốn nhịp chậm hơn.
- Beat 1 đến 9 là cold open, tổng 39,5 giây. Beat 1 dài 2,4 giây; có thể giữ thêm nếu muốn người xem kịp đọc bối cảnh.
- Beat 253 là ảnh kết. Giữ thêm 2 giây sau khi hết lời.
- Mốc giờ trong `sumer-image-prompts.csv` căn theo word timestamps của file VO thực tế `Voice_sumer_full.wav` (20:55.05). Không dùng mốc ước lượng trong script.

## Ghi chú kỹ thuật

- Prompt được sinh từ `sumer-beats.csv`, `sumer-prompt-blocks.md`, 4 bible và luật bối cảnh.
- Không dùng dấu gạch dài trong prompt, trong guide hoặc trong tên tệp.
- Generator và 3 tệp scene nằm trong `prompts-src/`.
- Chạy `node prompts-src/build-prompts.mjs` để sinh lại. Script đọc `sumer-beats.csv` trong `Summer` và ghi đầu ra vào `%TEMP%\opencode\prompts-out\`.
- Sau khi sinh lại, copy đè `sumer-image-prompts.txt` và `sumer-image-prompts.csv` vào `Summer`.
- Bản chính thức trong `Summer` là bản đã copy và kiểm tra.
