# PROMPT MODEL SHEET VÀ NỀN: SUMER

Dùng để gen lại bản sạch từ ảnh concept. Mỗi lần gen một nhân vật, không gen cả nhóm trước.

## Style lock, dán đầu mọi prompt

```
2D cartoon historical documentary illustration, stylized big-head proportions, thick dark outlines, flat colors with two-tone shading, minimal detail, warm earthy palette of sand, ochre, brick red, lapis blue and olive, clean readable silhouette, no text, no watermark
```

## Negative prompt

```
text, letters, watermark, logo, signature, photorealistic, 3d render, anime, gradient shading, extra fingers, deformed hands, extra limbs, duplicate character, cropped head, inconsistent proportions, modern objects, shoes on Sumerians
```

## 1. Tích, sheet 4 góc

```
[style lock]. Character model sheet of Tích, a Vietnamese boy around ten, round face, big dark eyes, short messy black hair, yellow hoodie, dark blue jeans, white sneakers, small brown backpack, three heads tall. Full body, four views in a row: front, three-quarter, side, back. Neutral standing pose, arms relaxed, same height in all four views. Plain off-white background, even spacing, no text. 3:2
```

## 2. Tích, sheet biểu cảm

```
[style lock]. Expression sheet of the same boy: Tích, round face, big dark eyes, short messy black hair, yellow hoodie. Twelve headshots in a 4 by 3 grid: neutral, happy, curious, thinking, worried, sad, angry, determined, shocked, awe, exhausted, skeptical. Same head size and angle, plain off-white background, no text. 3:2
```

## 3. Nông Dân

```
[style lock]. Character model sheet of Nông Dân, a Sumerian farmer, adult man, three and a half heads tall, tan skin, thick black beard, black hair under a cream headband, plain cream tunic, bare feet, strong arms. Full body, four views in a row: front, three-quarter, side, back, neutral standing pose holding a hoe. Plain off-white background, no text. 3:2
```

## 4. Thư Lại

```
[style lock]. Character model sheet of Thư Lại, a Sumerian scribe, young adult, three and a half heads tall, tan skin, black hair in a topknot, cream tunic with blue trim, blue sash, bare feet. Full body, four views in a row: front, three-quarter, side, back, holding a clay tablet and a reed stylus. Plain off-white background, no text. 3:2
```

## 5. Vua Sumer

```
[style lock]. Character model sheet of Vua Sumer, a Sumerian king, adult man, three and a half heads tall, tan skin, thick black beard, tall blue and gold crown, blue robe with gold trim, gold armbands, white pleated skirt. Full body, four views in a row: front, three-quarter, side, back, holding a bull-head staff. Plain off-white background, no text. 3:2
```

## 6. Lineup kiểm tra tỉ lệ

```
[style lock]. Character lineup, four characters standing side by side on a plain off-white background, same eye level: Tích the boy in a yellow hoodie at three heads tall, Nông Dân the farmer at three and a half heads tall, Thư Lại the scribe at three and a half heads tall, Vua Sumer the king at three and a half heads tall. Tích reaches the adults' chest. Front view, neutral poses, no text. 16:9
```

Dùng ảnh này để kiểm tra, không dùng làm reference chính.

## 7. Sáu nền

Mỗi nền gen một lần, ở 16:9, không nhân vật. Sau đó gen thêm hai biến thể chiều và đêm bằng cách đổi phần ánh sáng.

**Cổng thành Uruk**

```
[style lock]. Mudbrick city gate of Uruk, two gate towers, dark archway, dust haze, date palms. Wide shot, no characters, no text, three depth layers, low contrast background, high noon. 16:9
```

**Ziggurat xa**

```
[style lock]. Stepped mudbrick ziggurat with a long ramp, sun-baked plaza, date palms. Wide shot, no characters, no text, three depth layers, low contrast background, low sun from the west. 16:9
```

**Kênh đào**

```
[style lock]. Straight irrigation canal, wet clay banks, reeds, date palms, thin morning mist. Wide shot, no characters, no text, three depth layers, low contrast background. 16:9
```

**Nhà bảng**

```
[style lock]. Scribal school interior, clay tablets stacked on low benches, oil lamp, mudbrick walls. Wide shot, no characters, no text, three depth layers, low contrast background, warm lamp light. 16:9
```

**Bến sông**

```
[style lock]. Muddy river dock, reed boats, cargo baskets, low wooden walkway, palm grove. Wide shot, no characters, no text, three depth layers, low contrast background, golden hour. 16:9
```

**Đồng muối**

```
[style lock]. Cracked salt-crusted field, dead palms, empty dry canal, pale sky. Wide shot, no characters, no text, three depth layers, low contrast background, flat overcast light. 16:9
```

## 8. Cách dùng sau khi gen

1. Cắt từng pose và từng biểu cảm thành file riêng, nền trắng.
2. Đặt tên `ch_tich_front.png`, `ch_tich_shocked.png`.
3. Dùng ảnh `front` làm reference chính cho mọi cảnh, ảnh biểu cảm chỉ để đối chiếu.
4. Nền đặt tên `bg_uruk-gate_noon.png`.
5. Không dùng ảnh sheet nguyên tấm làm reference, model sẽ bắt chước cả bố cục lưới.

## 9. QC sheet

- Bốn góc nhìn cùng một khuôn mặt, cùng chiều cao.
- Tích thấp hơn người lớn, chỉ tới ngực.
- Không có chữ, không có lưới tên.
- Tay đủ ngón, không dính đạo cụ.
- Trang phục đúng từng nhân vật.
- Nền trắng hoặc off-white, không có cảnh.
- Nét viền dày đồng đều, không gradient.
