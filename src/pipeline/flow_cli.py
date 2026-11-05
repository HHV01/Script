"""Explicit Flow helper. Opening/checking never generates or uploads anything."""
from pathlib import Path
import yaml

from .common import need
from .flow_playwright import FlowBrowser, is_flow_url


def run(project, action='check', timeout=60, scene=1, force=False):
    need(1 <= timeout <= 3600, 'Timeout phải từ1 đến3600giây.')
    need(project.settings['flow'].get('backend') == 'playwright',
         'Helper này dùng flow.backend: playwright; không cần extension/CDP.')
    if action == 'generate-one':
        from .script_review import require_approval
        from .s3_scenes import validate_source
        from .s5_generate import run as generate
        require_approval(project)
        validate_source(project)
        project.settings['flow'].setdefault('playwright', {})['readiness_timeout'] = timeout
        generate(project, force=force, scene_ids=[scene])
        print('[flow] Đã xử lý một cảnh; không chạy dựng hoặc uploader.')
        return
    browser = FlowBrowser(project)
    try:
        browser.wait_connected(timeout=timeout, wait_for_prompt=False)
        if action == 'open':
            print('[flow] Đăng nhập trong browser này, mở/tạo project. Hồ sơ riêng được giữ cục bộ.')
            print('[flow] Khi xong, quay lại đây nhấn Enter để lưu URL project và đóng helper, giải phóng profile.')
            input()
            # The user may have opened a new Flow tab during login.
            pages = [p for p in browser.context.pages if is_flow_url(p.url) and '/project/' in p.url.split('?')[0]]
            if pages:
                url = pages[-1].url.split('?')[0].split('#')[0]
                path = Path(project.dir)/'project.yaml'
                cfg = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
                cfg['flow_url'] = url
                path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding='utf-8')
                print('[flow] Đã lưu URL project; không lưu mật khẩu vào .env.')
            else:
                print('[flow] Chưa thấy URL project; lần sau mở lại và chọn project trước khi Enter.')
        else:
            browser.wait_connected(timeout=timeout, wait_for_prompt=True)
            info = browser.call('ping')
            need(info.get('promptBox'), 'Chưa thấy ô nhập prompt; chưa sẵn sàng tạo ảnh.')
            print('[flow] Đã thấy ô prompt trong phiên này. Chưa gửi prompt hoặc tạo ảnh.')
    except (KeyboardInterrupt, EOFError):
        print('[flow] Đóng helper; đăng nhập chỉ được giữ nếu browser đã lưu phiên thành công.')
    finally:
        browser.close()
