# Cách vận hành agent — hình theo lời đọc

## Trách nhiệm thực tế
Assistant điều phối /root chịu trách nhiệm nhận sản phẩm, đọc kết quả, tích hợp và quyết định. An/Minh/Mai/Gạo là nhãn vai trò; app manager không phải bốn agent thường trực. Các task agent thật có ID, phạm vi tệp, đầu ra và kết quả kiểm tra tại agent-workflow-update-2026-10-30.json. Không ghi hoàn thành khi chỉ gửi việc, không ký thay agent.

## Chuỗi bàn giao bắt buộc
1. Nghiên cứu trả bảng luận điểm–nguồn–giới hạn, biên tập trả kịch bản và câu chuyển ý. Điều phối kiểm tra trước giao thu.
2. Khóa bản voice. VieNeu lưu voice.timing.json: hash script/audio/words và biên từng clip câu; từ bên trong là nội suy, không phải đo âm vị hay nghe kiểm tra.
3. Storyboard dựa trên voice đã khóa. Mỗi câu/mệnh đề là đơn vị mặc định; không giữ một ảnh8–12giây chỉ để đạt thời lượng tối thiểu. Người làm hình có thể đề xuất gộp cùng ý nhưng phải ghi cue thực tế và kiểm lại, không dùng legacy_pack như cách né kiểm duyệt.
4. Tác vụ mỹ thuật nhận nguyên văn câu đang đọc và khoảng thời gian. Trả chủ thể/hành động/câu neo; hình không minh họa câu trước hoặc câu sau. Cảnh mở, đổi khái niệm và cơ chế phải có mẫu đồng bộ trước làm toàn bộ.
5. Trước render: scenes.source.json phải khớp script/voice/word timing/settings. storyboard-timing.json phải có executor, hash script/voice/scenes và beats cho từng cảnh; mỗi beat ghi scene_id,anchor_text,visual_subject,visual_action,at_seconds,visual_at_seconds. Dựng hiện chỉ cắt ở đầu cảnh nên visual_at_seconds phải bằng scene.start trong1frame; không chấp nhận cue tưởng tượng giữa một ảnh tĩnh. Sai hash, thiếu cue hoặc hình đến trễ ngoài giới hạn thì chặn. Với từ nội suy chỉ được neo vào đầu clip câu có nguồn; muốn neo giữa câu cần căn chỉnh từ âm thanh thực tế.
6. QA trải nghiệm: công cụ/agent thực sự có thể xem/nghe phải đối chiếu lời đang nói với hình, ghi timestamp lỗi và trả sửa; kiểm mốc kế hoạch không thay kiểm bản dựng. Phụ đề cũng phải theo lời đọc, không chỉ chia thời lượng theo số chữ. Thiếu khả năng nghe/xem thì báo giới hạn và chặn chứng nhận đạt.

## Không làm trong lượt này
Không sửa lại audio/ảnh/final.mp4 hiện tại, không đổi trạng thái video YouTube, không tự điền phiếu approved. Dự án cũ thiếu hồ sơ nguồn timing hiện bị cổng mới chặn; cần bàn giao đúng và kiểm thực tế trước bất kỳ lần dựng sửa nào. Không tạo metadata ngược để cho qua.
