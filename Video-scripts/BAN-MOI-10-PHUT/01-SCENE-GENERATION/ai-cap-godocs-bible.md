# VISUAL BIBLE: AI CẬP 10 PHÚT KIỂU GODOCS

## 1. STYLE LOCK

Dùng câu này ở cuối mỗi prompt:

> Cinematic historical documentary still, 16:9, shot on 35mm film, natural light, fine film grain, realistic textures, muted warm palette, no text.

Không dùng:

- cartoon, anime, comic, illustration, painting, collage
- 3D render, plastic skin, video game look
- text, letters, numbers, labels, watermark, logo
- modern machinery, cranes, trucks, iron tools
- camels in Old Kingdom scenes
- wheeled carts
- extra fingers, deformed faces, distorted hands

## 2. ERA LOCK

- Thời kỳ: Cổ Vương quốc Ai Cập, Vương triều thứ Tư, khoảng 2560 TCN.
- Địa điểm: cao nguyên Giza, thung lũng sông Nile, Tura, Aswan, Wadi el-Jarf.
- Kiến trúc: Đại kim tự tháp Giza, đá vôi, lớp phủ đá vôi trắng Tura, granite bên trong, đường dốc bằng đất và đá vụn, xe trượt gỗ, dây thừng.
- Dụng cụ: đồng, đá, gỗ, dây thừng. Không sắt.
- Trang phục: vải lanh trắng ngà, nâu đất, xanh lam nhạt. Chân đất hoặc sandal da đơn giản.
- Tóc: đầu cạo hoặc tóc đen ngắn. Không tóc giả kiểu hiện đại.
- Động vật: bò, cừu, dê, cá, chim. Không lạc đà.

## 3. PEOPLE LOCK

- Người lao động Ai Cập, thân hình gầy chắc, da rám nắng, tay chai.
- Không dùng một nhân vật cartoon cố định.
- Merer: nam khoảng 30 tuổi, mặt dài, mũi thẳng, mắt đen, râu ngắn hoặc không râu, đầu cạo, váy lanh, tay cầm bút sậy và papyrus. Nếu xuất hiện, ưu tiên góc sau hoặc góc nghiêng.
- Đám đông có nhiều lứa tuổi, nhưng trọng tâm là người trưởng thành trong độ tuổi lao động.
- Không thể hiện bạo lực máu me. Hình ảnh roi vọt chỉ dùng như một khoảnh khắc định kiến, không kéo dài.

## 4. CAMERA LOCK

- Wide establishing: toàn cảnh sa mạc, kim tự tháp, công trường.
- Low angle: góc thấp từ chân kim tự tháp nhìn lên.
- Aerial: bản đồ, dòng sông, tuyến vận chuyển.
- Macro: bàn tay, dụng cụ, vết đẽo, sợi dây, bánh mì, xương.
- Cross-section: mặt cắt kim tự tháp, hành lang, phòng vua.
- 3/4 view: công cụ, thuyền, xe trượt.
- Scale comparison: kim tự tháp với tòa nhà hiện đại, chỉ dùng một đến hai lần.

## 5. LIGHT LOCK

- Bình minh: vàng nhạt, sương mù, bóng dài.
- Nắng gắt: trắng vàng, tương phản mạnh, hơi nóng.
- Hoàng hôn: cam đỏ, bụi vàng.
- Đuốc: cam ấm, bóng tối sâu, bên trong lăng mộ.
- Blue hour: xanh đêm, kim tự tháp thành bóng đen.

## 6. PALETTE

- Cát: #C9A46A
- Đá vôi: #E6D8BC
- Đồng: #B26A3C
- Xanh Nile: #2E5E6E
- Xanh faience: #2E8B8B
- Vàng kim: #C9A227
- Bóng tối: #3A2A1E

## 7. REFERENCE IMAGES

Dùng tối đa 3 ảnh tham chiếu cho mỗi lần tạo:

1. Lookbook ánh sáng và màu: cao nguyên sa mạc lúc bình minh, đá vôi, bụi mù.
2. Địa hình Giza và sông Nile: kim tự tháp, cao nguyên, dải xanh của thung lũng.
3. Trang phục và dụng cụ: váy lanh, đầu cạo, búa đồng, đục đồng, xe trượt gỗ, dây thừng.

Không dùng ảnh tham chiếu có chữ, logo, nhân vật cartoon hoặc công cụ hiện đại.

## 8. TEXT VÀ SỐ LIỆU

- Không để AI sinh chữ trong ảnh.
- Mọi con số, địa danh, tiêu đề chương và nhãn bản đồ sẽ được thêm khi dựng video.
- Prompt luôn kết thúc bằng "no text".

## 9. QUY TẮC NHẤT QUÁN

- Mỗi prompt chỉ một ý hình ảnh.
- Giữ cùng palette và cùng chất liệu phim.
- Không đổi thời kỳ, không đổi kiến trúc, không thêm công nghệ hiện đại.
- Nếu một ảnh có người, kiểm tra tay, mặt, số ngón và trang phục.
- Nếu một ảnh có kim tự tháp, kiểm tra độ dốc, số mặt và vật liệu.
- Nếu một ảnh có bản đồ, kiểm tra hướng sông Nile và vị trí Giza, Tura, Aswan.
- Không tạo cả batch từ toàn bộ file txt. Mỗi lần một prompt.

## 10. GHI CHÚ CHO FLOW

- Tỉ lệ: 16:9.
- Một prompt cho một lần tạo.
- Dùng tối đa 3 ảnh tham chiếu.
- Lưu ảnh theo tên beat: `beat-001.png`, `beat-002.png`.
- Với bản thử: `test-01.png` đến `test-08.png`.
- Không dùng chế độ tạo hàng loạt từ file txt.
