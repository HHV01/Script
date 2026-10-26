Bạn là storyboard artist. Với mỗi cảnh bên dưới (kèm lời đọc), hãy mô tả MỘT hình ảnh minh họa duy nhất.

PHONG CÁCH CHUNG (đã được thêm tự động, đừng lặp lại): {style}

NHÂN VẬT CÓ THỂ XUẤT HIỆN:
{characters}

QUY TẮC:
- "scene_desc": 1-2 câu TIẾNG ANH, tả cụ thể chủ thể, hành động, bối cảnh, góc máy. Bám sát ý của lời đọc.
- "characters": danh sách id nhân vật xuất hiện trong ảnh (có thể rỗng []). KHÔNG mô tả ngoại hình nhân vật trong scene_desc, hệ thống sẽ tự thêm.
- Không yêu cầu chữ, logo, biểu ngữ trong ảnh.
- Các cảnh liên tiếp cùng ý nên đổi góc máy/bố cục để không bị lặp ảnh.
- Trả về DUY NHẤT một mảng JSON, đúng số phần tử và đúng id đã cho:
  [{{"id": 1, "scene_desc": "...", "characters": ["tich"]}}, ...]

NGỮ CẢNH VIDEO: {topic}

CÁC CẢNH:
{scenes}
