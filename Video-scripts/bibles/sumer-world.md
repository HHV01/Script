# KHÔNG GIAN CHUNG: SUMER / URUK

Tài liệu này khóa thế giới, để 200 cảnh ghép lại vẫn là một thành phố.

## 1. Bản đồ chuẩn

Nhìn từ trên xuống, Uruk nằm trên một gò đất thấp, giữa đồng bằng phù sa.

```
                 BẮC
                  |
     kênh bắc     |     nhà bảng
          |       |       |
   TÂY ---+---- ZIGGURAT --+--- ĐÔNG
    sông  |       |         |    cổng thành
          |    đền gốc      |
     bến sông    |         |
               ruộng lúa mạch
                  |
                 NAM
```

Quy ước cố định:

- **Ziggurat ở trung tâm**, trên nền đất cao, nhìn thấy từ mọi hướng.
- **Sông ở phía tây**, chảy từ bắc xuống nam.
- **Cổng thành ở phía đông**, hai tháp đất, một cửa vòm.
- **Kênh chính chạy bắc nam**, rẽ nhánh về phía đông vào ruộng.
- **Ruộng lúa mạch ở phía nam**, ngoài tường thành.
- **Bến sông ở phía tây**, ngoài tường, có thuyền sậy.
- **Nhà bảng ở phía đông bắc ziggurat**, sát tường trong.
- **Đồng muối ở phía nam xa**, sau ruộng, nơi đất đã bỏ.

Khi máy nhìn về phía bắc: sông bên trái, cổng thành bên phải, ziggurat ở giữa. Giữ luật này trong mọi cảnh, trừ khi có lý do kể chuyện.

## 2. Sáu bối cảnh gốc

Mỗi bối cảnh làm một plate 16:9, không nhân vật, không chữ. Dùng lại, không gen mới mỗi cảnh.

| Mã | Tên | Mô tả | Dùng cho |
|---|---|---|---|
| `uruk-gate` | Cổng thành Uruk | Tường đất dày, hai tháp cổng, cửa vòm tối, bụi mù, chà là hai bên | Mở hồi, giới thiệu thành phố |
| `ziggurat-far` | Ziggurat nhìn xa | Tháp bậc thang 3 tầng, dốc nghiêng, nền đất nung, trời chiều | Quyền lực, thần linh |
| `canal-dawn` | Kênh đào | Kênh thẳng, bờ đất ướt, sậy, chà là, sương mỏng | Nước, lao động |
| `tablet-house` | Nhà bảng | Trong nhà, bảng đất xếp chồng, băng ghế thấp, đèn dầu | Chữ, nợ, trường học |
| `river-dock` | Bến sông | Thuyền sậy, giỏ hàng, cầu gỗ thấp, nắng chiều | Thương mại, giao lưu |
| `salt-flat` | Đồng muối | Đất nứt trắng, chà là chết, kênh khô, trời nhợt | Suy tàn |

Biến thể bắt buộc cho mỗi plate: **trưa, chiều, đêm**. Riêng `salt-flat` chỉ cần trưa trắng và chiều xám.

## 3. Bốn setup ánh sáng

| Mã | Tên | Đặc điểm | Dùng ở |
|---|---|---|---|
| `noon` | Trưa gắt | Nắng đứng, bóng ngắn, cát cháy trắng, tương phản cao | Hồi 1, 3 |
| `golden` | Chiều vàng | Nắng thấp từ phía tây, bóng dài về đông, cam và nâu | Hồi 4, 5, 6 |
| `fire` | Đêm lửa | Một nguồn sáng ấm, bóng nâu đậm, viền xanh lạnh | Hồi 6, 7 |
| `salt` | Trắng muối | Trời nhợt, gần như mất màu, tương phản thấp | Hồi 7, đầu hồi 8 |

Không tự phát minh setup thứ năm. Nếu cần khác, đổi bằng thời điểm trong ngày, không đổi hướng sáng.

## 4. Ba lớp cho mỗi nền

Mọi plate phải tách được ba lớp, nếu không thì không pan được:

- **Tiền cảnh:** sậy, chậu vỡ, đá, bụi cây, mép tường. Nét đậm, tối hơn.
- **Trung cảnh:** nơi nhân vật đứng. Đơn giản, ít chi tiết, chừa khoảng trống.
- **Hậu cảnh:** ziggurat, tường, chà là, trời. Nhạt hơn, ít tương phản.

Luật: hậu cảnh phải nhạt hơn nhân vật ít nhất một bậc. Nếu nền tranh mắt với mặt người, cảnh đó bỏ.

## 5. Vật liệu được phép

Gạch bùn, bùn trát, sậy, cói, gỗ chà là, nhựa bitum, thạch cao, đồng, vàng, bạc, lapis, carnelian, len, vải lanh, lúa mạch, đất sét.

Được phép xuất hiện: bánh xe gỗ, thuyền sậy, cày gỗ, cung, giáo, khiên đan, giỏ, vò, bảng đất sét, con dấu trụ.

## 6. Vật liệu cấm

Đá granite, đá cẩm thạch, sắt, kính cửa sổ, ngói, tiền xu, ngựa, lạc đà, giấy, mực, chữ Latinh, đồng hồ, kính mắt, bất kỳ vật dụng hiện đại nào.

Gạch nung chỉ xuất hiện từ giai đoạn Ur III trở đi, và chỉ ở công trình quan trọng. Nhà dân vẫn là gạch bùn.

## 7. Công thức prompt nền

```
[style lock của bible]
[địa điểm, mô tả ngắn gọn]
wide shot, no characters, no text
three depth layers, low contrast background
16:9
```

Ví dụ:

```
2D cartoon historical documentary illustration, stylized big-head proportions, thick dark outlines, flat colors with two-tone shading, minimal detail, warm earthy palette of sand, ochre, brick red, lapis blue and olive, clean readable silhouette, 16:9, no text, no watermark. Mudbrick city gate of Uruk, two gate towers, dark archway, dust haze, date palms, wide shot, no characters, no text, three depth layers, low contrast background.
```

## 8. Luật tái sử dụng

- Một plate dùng tối đa cho 20 cảnh, đổi góc bằng cách crop và pan, không gen lại.
- Cảnh ngoài trời dùng plate có sẵn. Chỉ gen mới khi kịch bản cần địa điểm chưa có.
- Mỗi plate đặt tên `bg_uruk-gate_noon.png`, `bg_uruk-gate_golden.png`.
- Ảnh nhân vật đặt tên `ch_tich_<pose>_<emotion>.png`.
- Cảnh hoàn chỉnh đặt tên `beat_001.png`, khớp số cảnh trong beat sheet.

## 9. Checklist 10 giây cho nền

- Ziggurat còn ở đúng hướng.
- Sông còn ở phía tây.
- Không có ngựa, lạc đà, tiền xu, kính, sắt.
- Không có chữ, biển hiệu, watermark.
- Ba lớp rõ, hậu cảnh nhạt hơn nhân vật.
- Còn khoảng trống cho phụ đề ở một phần ba dưới.
- Cùng palette với các nền còn lại.
