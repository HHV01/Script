Bạn là storyboard artist. Với mỗi cảnh bên dưới (kèm lời đọc), hãy mô tả MỘT hình ảnh minh họa duy nhất.

PHONG CÁCH CHUNG (đã được thêm tự động, đừng lặp lại): {style}

NHÂN VẬT CÓ THỂ XUẤT HIỆN:
{characters}

QUY TẮC:
- "scene_desc": 1-2 câu TIẾNG ANH, tả cụ thể chủ thể, hành động, bối cảnh, góc máy. Bám sát ý của lời đọc.
- Timestamp là khoảng lời đọc CHÍNH XÁC của cảnh hiện tại. Hành động/chủ thể chính phải minh họa mệnh đề đang được đọc ngay đầu khoảng đó; không minh họa câu trước hoặc báo trước câu sau. Không giữ cảnh cũ chỉ để đạt thời lượng tối thiểu. Timestamp từ nội suy không phải bằng chứng đã đồng bộ thực tế.
- "characters": danh sách id nhân vật xuất hiện trong ảnh (có thể rỗng []). KHÔNG mô tả ngoại hình nhân vật trong scene_desc, hệ thống sẽ tự thêm.
- Không yêu cầu chữ, logo, biểu ngữ trong ảnh. Không chèn tên kênh hoặc handle vào nội dung ảnh.
- Các cảnh liên tiếp cùng ý nên đổi góc máy/bố cục để không bị lặp ảnh.
- Mỗi cảnh có một hành động và cảm xúc đọc được trên điện thoại. Ưu tiên cận vật thể, tương tác tay/đạo cụ, ánh mắt và tư thế có mục đích; không lặp nhân vật đứng chỉ tay.
- Không tạo bố cục slide: tránh khung thẻ, tiêu đề trang và khoảng trống vô nghĩa. Đồ vật và nhân vật phải đủ lớn; chừa vùng phụ đề.
- Hình phải làm rõ đúng cơ chế đang nói; không thêm mũi tên, cắt lớp hay chi tiết máy móc sai chỉ để đẹp.
- Trả về DUY NHẤT một mảng JSON, đúng số phần tử và đúng id đã cho:
  [{{"id": 1, "scene_desc": "...", "characters": ["stick-orange"]}}, ...]

NGỮ CẢNH VIDEO: {topic}

CÁC CẢNH:
{scenes}
