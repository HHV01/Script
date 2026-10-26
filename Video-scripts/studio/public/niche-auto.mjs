// Chạy tự động toàn bộ luồng tìm ngách từ kênh tham khảo tới 20 chủ đề.
// Người dùng chỉ nhập kênh (và góc kể nếu muốn); các bước còn lại tự làm:
// chọn khuôn đề xuất, kiểm tra kho (tự ghi nhận ngoại lệ khi chưa đủ 3 kênh
// cùng khuôn), chia nhóm, chọn nhóm tốt nhất, gõ thử 1–3 câu và chốt 20 chủ đề.
// Chỉ dừng khi thiếu dữ liệu thật hoặc cổng không đạt — không hỏi lại từng bước.

const DEFAULT_ANGLE = 'Đi sâu vào nguyên nhân, bối cảnh và hệ quả của từng chủ đề, kể bằng ví dụ cụ thể.';
const passed = (flow, stage) =>
  flow?.[stage]?.passed === true || (stage === 'shelf' && flow?.shelf?.overridden === true);

export async function runNicheAuto({ getSurvey, act, save = async () => {}, onProgress = () => {} }) {
  const survey = () => getSurvey();
  if (!survey()) throw Error('Không tìm thấy khảo sát.');
  const flow = () => survey().nicheFlow || {};
  const step = text => onProgress(text);

  // 1. Thị trường / ngôn ngữ / định dạng
  if (!passed(flow(), 'field')) {
    step('1/6 · Lưu thị trường, ngôn ngữ và định dạng…');
    await act('field', {
      market: survey().market || 'US',
      language: survey().language || 'en',
      format: survey().format || 'long',
    });
  }

  // 2. Khuôn tiêu đề — tự lấy ứng viên đề xuất, tự lấy gợi ý góc kể đầu tiên.
  if (!passed(flow(), 'template')) {
    step('2/6 · Đọc kênh tham khảo và chọn khuôn…');
    if (!String(survey().leadChannel || '').trim()) throw Error('Nhập kênh tham khảo trước khi chạy tự động.');
    if ((survey().nicheMode || 'import') !== 'live' && survey().completeImport !== true)
      throw Error('Với kho nhập, xác nhận kho đủ video và 20 tiêu đề mới nhất trước khi chạy tự động.');
    // Nếu chưa có góc kể, truyền góc mặc định ngay để server lưu vào nicheFlow.template.angle
    const angleForTemplate = String(survey().angle || '').trim() || DEFAULT_ANGLE;
    const template = await act('template', {
      mode: survey().nicheMode || 'import',
      channel: survey().leadChannel,
      angle: angleForTemplate,
      confirmComplete: survey().completeImport === true,
      suggestAngles: !String(survey().angle || '').trim(),
    });
    if (!template.passed) throw Error('Kênh tham khảo không lặp khuôn ở hơn nửa số tiêu đề mới nhất. Đổi kênh tham khảo rồi chạy lại.');
  }
  // Đảm bảo góc kể đã lưu trên server (nếu server trả về angle rỗng do suggestAngles=true chưa kịp trả gợi ý).
  if (!String(flow().template?.angle || '').trim()) {
    step('2/6 · Lưu góc kể mặc định lên server…');
    await act('template', { angle: DEFAULT_ANGLE, suggestAngles: false });
  }

  // 3. Kho kênh — chưa đủ 3 kênh cùng khuôn thì tự ghi nhận ngoại lệ và đi tiếp.
  if (!passed(flow(), 'shelf')) {
    step('3/6 · Kiểm tra kho kênh…');
    let shelf = await act('shelf', {
      mode: survey().nicheMode || 'import',
      confirmComplete: survey().completeImport === true,
      extraChannels: String(survey().extraChannelsText || '').split('\n').map(x => x.trim()).filter(Boolean),
    });
    if (!shelf?.passed) {
      const same = (shelf?.channels || []).filter(c => c.sameTemplate === true).length;
      if (!same) throw Error('Kho chưa có kênh nào cùng khuôn. Đổi kênh tham khảo hoặc thêm kênh cùng khuôn rồi chạy lại.');
      step(`3/6 · Chưa đủ 3 kênh chuẩn — tự tiếp tục với ${same} kênh cùng khuôn…`);
      await act('shelf', { override: true });
    }
  }

  // 4. Chia nhóm và tự chọn nhóm tốt nhất (server đã tính suggestedGroup).
  let groups = flow().groups;
  if (!groups?.passed) {
    step('4/6 · Chia nhóm chủ đề bằng AI…');
    groups = await act('groups', {});
    if (!groups?.passed) {
      const count = groups?.count != null ? ` (hiện ${groups.count} nhóm)` : '';
      throw Error(`AI chưa chia được 4–7 nhóm hợp lệ${count}. Bấm Chia nhóm lại để thử; nếu vẫn lỗi, dán nhóm JSON ở phần nâng cao.`);
    }
  }
  if (!flow().groups?.chosen) {
    const groupId = flow().groups?.suggestedGroup || flow().groups?.groups?.find(g => g.id !== 'unclassified')?.id;
    if (!groupId) throw Error('Không có nhóm hợp lệ để chọn. Chia nhóm lại giúp mình nhé.');
    step('4/6 · Chọn nhóm tốt nhất…');
    await act('groups', { groupId });
  }

  // 5. Gõ thử bằng chính câu gợi ý của nhóm đã chọn (1–3 câu).
  if (!passed(flow(), 'probe')) {
    const mode = survey().nicheMode === 'live' ? 'live' : (survey().probeMode || 'import');
    if (mode !== 'live') throw Error('Đang ở chế độ nhập mẫu: dán 1–3 mẫu lượt xem ở bước Kiểm tra nhu cầu rồi bấm kiểm tra. Chạy tự động chỉ đo được bằng YouTube Data API.');
    const queries = (flow().groups?.suggestedQueries || []).map(x => String(x).trim()).filter(Boolean).slice(0, 3);
    if (!queries.length) throw Error('Nhóm đã chọn không dựng được câu gõ thử nào. Chọn nhóm khác rồi chạy lại.');
    step(`5/6 · Kiểm tra nhu cầu trên YouTube (${queries.length} câu)…`);
    const probe = await act('probe', { mode: 'live', queries });
    if (!probe?.passed) throw Error(`Nhu cầu chưa đạt (trung vị ${probe?.medianHits ?? '—'}/20, cần 11/20). Thử nhóm khác hoặc đổi kênh tham khảo.`);
  }

  // 6. 20 chủ đề
  if (!passed(flow(), 'topics')) {
    step('6/6 · Đề xuất 20 chủ đề…');
    const topics = await act('topics', {});
    if (!topics?.passed) throw Error(`Chưa gom đủ 20 chủ đề${topics?.errors?.[0] ? ' — ' + topics.errors[0] : ''}. Chạy lại bước này để AI đề xuất thêm.`);
  }

  step('Xong · 20 chủ đề đã sẵn sàng.');
  return flow();
}
