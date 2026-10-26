// TOÀN BỘ chỗ phụ thuộc vào giao diện Google Flow nằm ở file này.
// Khi Flow đổi UI, chỉ cần sửa ở đây rồi chạy: python run.py run <project> --only ping
const SEL = {
  // Ô nhập prompt: lấy phần tử đầu tiên đang hiển thị khớp một trong các selector
  promptBox: ['textarea', 'div[contenteditable="true"]'],

  // Ảnh kết quả trong project. Mỗi ảnh được định danh bằng pathname của src (bỏ query token).
  // ⚠ CHƯA kiểm chứng với Flow thật — hãy xem ping báo bao nhiêu ảnh rồi chỉnh cho khớp.
  tileImg: 'img[src*="flow-content"], img[src*="googleusercontent"], img[src^="blob:"]',

  // Dấu hiệu Flow đang vẽ (nếu thấy phần tử này thì coi là chưa xong)
  busy: ['[role="progressbar"]', 'mat-progress-bar', 'mat-spinner'],

  // Chế độ tạo ảnh: pipeline CHỈ tạo ảnh, không bao giờ tạo video.
  // imageMode: selector tuỳ chọn để chỉ thẳng nút "Image/Hình ảnh". Bỏ trống để tự tìm theo chữ.
  imageMode: '',

  // Nút gửi: hàm trả về button (hoặc null). Mặc định: nút nằm ngay sau nút chọn model (Banana/Nano),
  // nếu không thấy thì gửi bằng phím Enter.
  sendButton(box) {
    const btns = [...document.querySelectorAll('button, div[role="button"]')].filter(b => b.offsetParent !== null);
    const model = btns.find(b => /banana|nano/i.test(b.innerText || ''));
    if (model) {
      const sibs = [...(model.parentElement?.querySelectorAll('button') || [])];
      const i = sibs.indexOf(model);
      if (i >= 0 && sibs[i + 1]) return sibs[i + 1];
    }
    return null;
  },

  stableMs: 4000,        // ảnh phải ổn định (không thêm/bớt) chừng này ms mới coi là xong
};
