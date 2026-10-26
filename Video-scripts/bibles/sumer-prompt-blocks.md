# SUMER PROMPT BLOCKS: REUSABLE BUILDING BLOCKS

Bộ block dùng để ghép prompt ảnh cho mọi cảnh Sumer, không chỉ 253 beat hiện có. Giữ đúng thứ tự và đúng chữ để nhân vật không trôi.

## Công thức ghép prompt

```
[STYLE LOCK]. [CHARACTER BLOCK 1]. [CHARACTER BLOCK 2]. [SCENE]. Setting: [SETTING BLOCK]. Lighting: [LIGHTING BLOCK]. [CAMERA OR FRAMING]. [COMPOSITION]. [CUNEIFORM NOTE]. 16:9. [NEGATIVE TAIL].
```

- Cảnh một nhân vật: dùng 1 character block.
- Cảnh nhiều nhân vật: dùng nhiều character block, mỗi block một câu, giữ nguyên thứ tự.
- Cảnh không có nhân vật: bỏ phần character, giữ scene, setting, lighting, camera.
- Cảnh cận tay hoặc cận vật: thay camera bằng một câu framing riêng, chỉ tả phần nhìn thấy.
- Prompt dài trung bình 136 từ. Nếu model giới hạn độ dài, cắt phần composition trước, giữ style lock, character, scene, setting, lighting.

## 1. Style lock

```
2D cartoon historical documentary illustration, stylized big-head proportions, thick dark outlines, flat colors with two-tone shading, minimal detail, warm earthy palette of sand, ochre, brick red, lapis blue and olive, clean readable silhouette, 16:9, no text, no watermark
```

## 2. Negative tail ngắn, dán cuối prompt

```
16:9. No readable modern text, no watermark, no photorealistic rendering, no 3D render, no anime, no extra fingers, no deformed hands, no duplicate characters.
```

## 3. Negative prompt đầy đủ cho ô negative

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

Ghi chú: chữ hình nêm là họa tiết, không phải chữ đọc được. Không đưa `cuneiform` vào negative. Vì Tích mặc áo vàng, jeans, giày trắng và ba lô nâu trong mọi cảnh, không dùng negative có `modern objects, modern clothing, watches, paper, glass, plastic` cho cảnh có Tích. Beat 249 dùng negative hiện đại vì có đồng hồ.

## 4. Character blocks

Tích:

```
Tích, a Vietnamese boy around ten, round face, big dark eyes, short messy black hair, yellow hoodie, dark blue jeans, white sneakers, small brown backpack, three heads tall.
```

Nông Dân:

```
Nông Dân, a Sumerian farmer, adult man, three and a half heads tall, tan skin, thick black beard, black hair under a cream headband, plain cream tunic, bare feet, strong arms.
```

Thư Lại:

```
Thư Lại, a Sumerian scribe, young adult, three and a half heads tall, tan skin, black hair in a topknot, cream tunic with blue trim, blue sash, bare feet, a clay tablet in one hand.
```

Vua Sumer:

```
Vua Sumer, a Sumerian king, adult man, three and a half heads tall, tan skin, thick black beard, tall blue and gold crown, blue robe with gold trim, gold armbands, white pleated skirt, bull-head staff.
```

Sargon, biến thể của Vua, dùng cho beat 161, 164, 168:

```
Sargon, a Sumerian king, adult man, three and a half heads tall, tan skin, short black beard, copper crown, blue robe with copper trim, gold armbands, white pleated skirt, bull-head staff.
```

Ur-Nammu, biến thể của Vua, dùng cho beat 134:

```
Ur-Nammu, a Sumerian king, adult man, three and a half heads tall, tan skin, thick black beard, horned copper crown, blue robe with gold trim, gold armbands, white pleated skirt, bull-head staff.
```

Dân thường, dùng cho đám đông và vai một lần:

```
Sumerian townspeople in plain cream and brown tunics, bare feet, varied ages and hairstyles.
```

Tư tế:

```
A Sumerian priest, shaved head, small horned cap, white linen robe, lapis bead necklace.
```

Lính:

```
Sumerian soldiers, copper helmets, woven shields, spears, leather tunics.
```

Gilgamesh:

```
Gilgamesh, a young Uruk king, tall and muscular, black curly hair, short beard, gold headband, lion-skin cloak, bare chest, fleece kilt.
```

Enkidu:

```
Enkidu, a wild man, tall, long tangled black hair, thick beard, animal skin, bare feet.
```

Utnapishtim:

```
Utnapishtim, an old man, long white beard, plain undyed robe, deep-set eyes, no crown.
```

Humbaba:

```
Humbaba, a giant guardian with a lion face, coiled beard and brows, massive body, forest-green skin.
```

Bò thần:

```
The Bull of Heaven, a huge black bull with golden horns, red eyes, a copper collar.
```

Vợ Utnapishtim:

```
The wife of Utnapishtim, a middle-aged woman, hair in a bun, plain undyed robe.
```

Rawlinson:

```
Henry Rawlinson, a 19th-century British officer, red coat, dark cap, sideburns.
```

## 5. Setting blocks

Cổng thành:

```
a mudbrick city gate, two gate towers, dark archway, dust haze, date palms
```

Ziggurat:

```
stepped mudbrick ziggurat with a long ramp, sun-baked plaza, date palms
```

Kênh đào:

```
straight irrigation canal, wet clay banks, reeds, date palms, thin morning mist
```

Nhà bảng:

```
scribal school interior, clay tablets stacked on low benches, oil lamp, mudbrick walls
```

Bến sông:

```
muddy river dock, reed boats, cargo baskets, low wooden walkway, palm grove
```

Đồng muối:

```
cracked salt-crusted field, dead palms, empty dry canal, pale sky
```

Đồng bằng trống:

```
an empty flat floodplain, cracked mud, dry reeds, no trees, no stones, pale horizon
```

Ruộng lúa mạch:

```
a barley field with low mud banks, dry stalks, a flat horizon
```

Đầm lầy:

```
a marsh of tall reeds, still brown water, mudbanks, haze
```

Chợ:

```
a mudbrick market street, reed awnings, baskets of grain, pottery, no coins
```

Đền:

```
a mudbrick temple complex, gate, storerooms, small inner shrine, grain jars, oil lamps
```

Phòng ngai:

```
a mudbrick throne room, a low dais, woven hangings, oil lamps
```

Tường thành:

```
a mudbrick city wall with battlements, gate towers, dusty ground
```

Phế tích:

```
a low archaeological tell, broken mudbrick walls, dust, a dry plain
```

Bàn hiện đại của Tích:

```
a dark wooden desk by a window, a mechanical clock, papers, a clay tablet, cool daylight
```

Phòng nghiên cứu thế kỷ 19:

```
a 19th-century study with a wooden desk, oil lamp, books, papers, and a clay tablet, dust in the air
```

Không gian thần thoại:

```
a mythic space of deep blue night, golden light, long shadows, symbolic ground, no real architecture
```

Nền đồ họa:

```
a flat clay-colored graphic background with cuneiform marks and arrows, no characters
```

Hai con sông:

```
two broad muddy rivers, low reed banks, flat horizon, pale sky
```

Kho lúa:

```
a mudbrick grain store, sealed jars, sacks of barley, a low wooden counter, dust
```

Phố hẹp:

```
a narrow mudbrick street between low houses, dust, worn thresholds, no market stalls
```

Nhà nghèo:

```
a poor mudbrick house interior, a straw mat, a clay bowl, dim warm light
```

Vách đá Behistun:

```
a high rock cliff with carved reliefs and three columns of cuneiform, a narrow ledge, open sky
```

Công trường gạch bùn:

```
a half-built mudbrick wall, fresh bricks, straw, mud mortar, dusty ground
```

Sân trong:

```
a mudbrick courtyard with a low wall, a canal channel under construction, stacked fire bricks, a school bench, dusty ground
```

## 6. Lighting blocks

- Nắng gắt đầu phim: `high noon, short shadows, bleached sand, high contrast`
- Sương sớm: `thin morning mist, soft warm light`
- Giờ vàng: `golden hour, long shadows`
- Chiều muộn: `warm late afternoon, long shadows, dust in the air`
- Đèn dầu trong nhà: `warm oil-lamp light, deep brown shadows`
- Nhà nghèo: `warm dim interior light, deep shadows`
- Nắng chiều trên ziggurat và ngai: `low sun from the west, long shadows to the east, amber light`
- Vách đá: `late afternoon sun, long shadows, open sky`
- Không gian thần thoại: `deep blue night, golden firelight, long shadows`
- Đồng muối: `pale overcast light, low saturation, white ground`
- Lửa và tro: `firelight and smoke, dark orange glow, ash in the air`
- Phế tích: `golden hour over the ruins, long shadows`
- Nền đồ họa: `flat even light, no shadows`
- Bàn hiện đại: `cool daylight from a window, soft shadows`
- Phòng nghiên cứu: `warm oil-lamp light, deep brown shadows`

## 7. Camera và framing blocks

- `Wide establishing shot.`
- `Wide panoramic shot.`
- `Medium shot, waist up.`
- `Close-up, head and shoulders.`
- `Extreme close-up insert, only the hand and object are visible.`
- `Extreme close-up insert, only the object is visible.`
- `Top-down view.`
- `Low-angle shot.`

Framing đặc biệt, chỉ tả phần nhìn thấy:

```
Extreme close-up, only the scribe's hand and forearm are visible, the stylus and tablet filling the frame.
```

```
Close-up, only the king's hand, the scribe's hand, the tablet, and the cylinder seal are visible.
```

```
Close-up, only Gilgamesh's hand and forearm are visible, gripping the wall.
```

```
Close-up, only the boy's wrist and the watch are visible.
```

## 8. Composition blocks

Cảnh thường:

```
Three depth layers, clear silhouette, low-contrast background, clean lower third for subtitles.
```

Cận cảnh:

```
Clean readable silhouette, low-contrast background, clean lower third for subtitles.
```

Nền đồ họa:

```
Flat graphic composition, clear arrows, no characters.
```

Chữ hình nêm, thêm khi cảnh có bảng đất:

```
Cuneiform wedge marks are decorative texture, not readable modern text.
```

## 9. Ví dụ ghép một cảnh mới

Cảnh mới: Nông Dân đứng trước kho lúa, giơ tay che nắng.

```
2D cartoon historical documentary illustration, stylized big-head proportions, thick dark outlines, flat colors with two-tone shading, minimal detail, warm earthy palette of sand, ochre, brick red, lapis blue and olive, clean readable silhouette, 16:9, no text, no watermark. Nông Dân, a Sumerian farmer, adult man, three and a half heads tall, tan skin, thick black beard, black hair under a cream headband, plain cream tunic, bare feet, strong arms. The farmer stands in front of a full grain store, one hand shading his eyes, calm and tired. Setting: a mudbrick market street, reed awnings, baskets of grain, pottery, no coins. Lighting: golden hour, long shadows. Medium shot, waist up. Three depth layers, clear silhouette, low-contrast background, clean lower third for subtitles. 16:9. No readable modern text, no watermark, no photorealistic rendering, no 3D render, no anime, no extra fingers, no deformed hands, no duplicate characters.
```

## 10. Luật tái sử dụng

- Giữ nguyên 4 block gốc: Tích, Nông Dân, Thư Lại, Vua Sumer. Chỉ đổi scene, setting, lighting, camera.
- Không đổi mặt, tóc, mắt, tỉ lệ đầu của nhân vật định kỳ. Đổi thời đại thì đổi outfit, không đổi người.
- Tích cao 3 đầu, người lớn cao 3,5 đầu. Đầu Tích chỉ tới ngực người lớn.
- Tích mặc áo vàng xuyên suốt. Tích chỉ xuất hiện ở mở hồi, câu hỏi và kết, không đứng trong cảnh chết, chiến tranh, đám tang.
- Vua Sumer giữ mũ xanh vàng. Sargon và Ur-Nammu dùng chung model Vua, khác mũ và râu.
- Thần thoại dùng bảng màu xanh đêm và vàng lửa từ beat 179. Trước đó giữ ánh sáng lịch sử.
- Cảnh đông người lấy mô tả từ `sumer-roster.json`, không trộn identity dài của bible.
- Không để chữ hiện đại đọc được trong ảnh. Chữ hình nêm chỉ là họa tiết.
