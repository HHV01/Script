# PACK SUMER: 2D CARTOON HISTORICAL DOCUMENTARY

Bộ này thay cho hướng Vẽ Vời trước đó. Bốn nhân vật, một thế giới, một style lock.

## Thứ tự dùng

1. Nạp 4 bible nhân vật vào kênh.
2. Nạp `sumer-roster.json` để có nhân vật phụ và bối cảnh.
3. Đọc `sumer-world.md` để khóa bản đồ, ánh sáng, vật liệu.
4. Gen model sheet theo `sumer-model-sheet-prompts.md`.
5. Gen nền theo 6 plate trong cùng tệp.
6. Gen giọng theo `VO/00-HUONG-DAN-VO.md`, dùng `VO/vo-01.txt` đến `VO/vo-09.txt`.
7. Dùng `sumer-script-clean.md` cho phụ đề và mô tả video.
8. Dùng `sumer-beats.md` để dựng, rồi sinh prompt từng cảnh.
9. Gen ảnh theo `sumer-image-prompts.txt`, mỗi block một beat. Đọc `00-HUONG-DAN-PROMPT-ANH.md` trước khi gen.
10. Dùng `sumer-prompt-blocks.md` khi cần ghép cảnh mới ngoài 253 beat.
11. Dùng `sumer-video-prompt.md` để animate ảnh beat. Bản copy paste nằm trong `sumer-video-prompt.txt`.
12. Dùng `sumer-thumbnail-prompts.md` để làm thumbnail. Bản copy paste nằm trong `sumer-thumbnail-prompts.txt`.
13. Đọc `sumer-flow-workflow.md` trước khi gen ảnh và video trong Google Flow.

## Tệp

| Tệp | Vai trò |
|---|---|
| `sumer-tich-bible.txt` | Nhân vật chính, người dẫn chuyện, 3 đầu |
| `sumer-nong-dan-bible.txt` | Nông dân, 3,5 đầu |
| `sumer-thu-lai-bible.txt` | Thư lại, 3,5 đầu |
| `sumer-vua-bible.txt` | Vua, giữ mũ xanh vàng |
| `sumer-roster.json` | Mô tả 4 nhân vật, 6 bối cảnh, 4 setup sáng |
| `sumer-world.md` | Bản đồ Uruk, luật hướng máy, vật liệu cấm |
| `sumer-model-sheet-prompts.md` | Prompt gen sheet và nền |
| `sumer-script-30p.md` | Kịch bản đầy đủ, 4.942 từ, bản đọc ước tính 30 phút |
| `sumer-script-clean.md` | Lời kể sạch, 4.816 từ, dùng cho phụ đề và đối chiếu beat |
| `sumer-beats.md` | Bảng beat 253 dòng, đủ lời và hướng hình |
| `sumer-beats.csv` | Dữ liệu beat, mốc giây chính xác |
| `sumer-beats.txt` | Bản nhập studio, mỗi dòng một beat |
| `sumer-image-prompts.txt` | 253 prompt ảnh, mỗi beat một block, cách nhau dòng trống |
| `sumer-image-prompts.csv` | Đối chiếu prompt, beat, mốc giờ, nhân vật, bối cảnh |
| `sumer-prompt-blocks.md` | Block nhân vật, bối cảnh, ánh sáng để ghép cảnh mới |
| `00-HUONG-DAN-PROMPT-ANH.md` | Hướng dẫn gen ảnh, negative, QC |
| `sumer-video-prompt.md` | Prompt video dùng chung, negative, thời lượng, QC |
| `sumer-video-prompt.txt` | Bản copy paste prompt video |
| `sumer-thumbnail-prompts.md` | 8 prompt thumbnail, tiêu đề, chữ hậu kỳ, QC |
| `sumer-thumbnail-prompts.txt` | Bản copy paste 8 prompt thumbnail |
| `sumer-youtube-package.md` | Tiêu đề, thumbnail, mô tả, tag và checklist đăng YouTube |
| `sumer-youtube-package.txt` | Bản copy paste tiêu đề, mô tả và tag |
| `sumer-flow-workflow.md` | Quy trình gen ảnh và video trong Google Flow |
| `prompts-flow/` | 9 file prompt theo hồi, chỉ dẫn tác nhân, reference map |
| `prompts-src/` | Generator và 3 tệp scene để sinh lại prompt |
| `sumer-draft.mp4` | Video nháp 20:30, 1920x1080, 253 slot ảnh, 7 ảnh bổ sung, nhịp đều |
| `sumer-bo-sung-review.mp4` | Cắt 38 giây, 7 beat bổ sung kèm voice |
| `sumer-video-timeline.csv` | Mốc beat gốc đã scale, dùng để tham chiếu |
| `sumer-video-timeline-deu.csv` | Mốc đổi ảnh đã làm đều, dùng cho video hiện tại |
| `sumer-image-mapping-final.csv` | Ánh xạ 247 ảnh Flow vào 253 beat, 236 ảnh được dùng |
| `sumer-video-report.md` | Ghi chú ghép video, 7 ảnh bổ sung và bản đều |
| `_cu/sumer-draft-v1.mp4` | Bản nháp trước khi bổ sung 7 ảnh |
| `_cu/sumer-draft-v2.mp4` | Bản có 7 ảnh nhưng nhịp chưa đều |
| `VO/` | 9 đoạn VO ElevenLabs; voice cuối `Voice_finally.wav` dài 20:30.80 |

## Ghi chú thời lượng

Voice cuối `Voice_finally.wav` dài 20:30.80. Video nháp dùng timeline scale 0,98028 từ beat gốc 20:55.05. Beat gốc vẫn giữ trong `sumer-beats.csv`. Mốc đổi ảnh hiện tại dùng `sumer-video-timeline-deu.csv`, đã làm đều bằng trung bình trượt 5 beat. Xem `sumer-video-report.md`.

## Luật kỹ thuật

- Style lock trong 4 bible phải giống hệt nhau. Đã kiểm tra, cả 4 trùng.
- `character-bible.mjs` chỉ đọc một nhân vật mỗi tệp, nên tách 4 tệp.
- Cảnh đông người lấy mô tả từ roster, không lấy identity từ bible. Vì vậy mô tả trong roster phải trùng khớp identity. Đã đồng bộ.
- Không sửa nhãn thẻ sau khi đã có cảnh, vì tag sinh từ nhãn.

## Ghi chú

`_cu/sumer-scenes.md` thuộc hướng cũ, không dùng cho bộ này.
