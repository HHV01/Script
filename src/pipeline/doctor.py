"""Offline diagnostics. Never opens a browser, sends prompts, or prints secrets."""
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def inspect(project_name=None):
    checks = []
    def add(code, status, detail, action=None):
        checks.append(dict(code=code, status=status, detail=detail, action=action))
    add('python', 'pass' if sys.version_info >= (3, 11) else 'fail',
        sys.version.split()[0], 'Dùng Python >=3.11 nếu phiên bản quá cũ.')
    for module in ('yaml', 'PIL', 'playwright', 'openai', 'vieneu'):
        found = importlib.util.find_spec(module) is not None
        add('dependency.'+module, 'pass' if found else ('fail' if module in ('yaml', 'PIL', 'playwright') else 'warn'),
            'Có module' if found else 'Thiếu module',
            f'{sys.executable} -m pip install -r requirements.txt' if not found else None)
    for binary in ('ffmpeg', 'ffprobe'):
        bundled = ROOT/'tools/ffmpeg/bin'/(binary+'.exe' if os.name == 'nt' else binary)
        found = bundled.is_file() or bool(shutil.which(binary))
        add(binary, 'pass' if found else 'warn', 'Tìm thấy' if found else 'Chưa thấy; cần cho dựng/kiểm media')
    cfg = {}
    try:
        import yaml
        cfg = yaml.safe_load((ROOT/'config/settings.yaml').read_text(encoding='utf-8')) or {}
        if project_name:
            if not re.fullmatch(r'[\w-]{1,64}', project_name) or project_name.startswith('_'):
                raise ValueError('Tên dự án không hợp lệ')
            path = ROOT/'projects'/project_name
            if path.is_symlink() or path.resolve().parent != (ROOT/'projects').resolve():
                raise ValueError('Đường dẫn dự án không hợp lệ')
            project = yaml.safe_load((path/'project.yaml').read_text(encoding='utf-8')) or {}
            # Only Flow configuration is needed here; never inspect credential values.
            flow = cfg.get('flow', {}).copy()
            override = project.get('settings', {}).get('flow', {})
            flow.update({k:v for k,v in override.items() if k != 'playwright'})
            flow['playwright'] = {**cfg.get('flow', {}).get('playwright', {}), **override.get('playwright', {})}
            cfg['flow'] = flow
            url = project.get('flow_url', '')
            from .flow_playwright import is_flow_url
            add('flow.project_url', 'pass' if url and is_flow_url(url) else 'warn',
                'Đã đặt URL Flow hợp lệ' if url and is_flow_url(url) else 'Chưa có URL project Flow hợp lệ',
                f'python run.py flow {project_name} --action open')
            for name in ('script.txt','scenes.json','prompts.txt'):
                add('project.'+name, 'pass' if (path/name).is_file() else 'warn',
                    'Có tệp' if (path/name).is_file() else 'Chưa có tệp; không tự tạo lại các bước trước')
        from .flow_playwright import FlowBrowser
        from types import SimpleNamespace
        browser = FlowBrowser(SimpleNamespace(settings=cfg))
        executable = browser._executable()
        if not executable and importlib.util.find_spec('playwright'):
            # Reading the managed executable location does not launch a browser.
            from playwright.sync_api import sync_playwright
            with sync_playwright() as runtime:
                executable = runtime.chromium.executable_path
        found = bool(executable and Path(executable).is_file())
        add('flow.browser', 'pass' if found else 'fail', 'Có Chrome/Edge/Chromium' if found else 'Chưa tìm thấy browser dùng được',
            None if found else 'python -m playwright install chromium')
        profile = Path(cfg.get('flow',{}).get('playwright',{}).get('profile_dir','.flow-profile'))
        if not profile.is_absolute(): profile = ROOT/profile
        add('flow.profile', 'pass' if profile.is_dir() else 'warn',
            'Có hồ sơ browser riêng; chưa xác minh đăng nhập' if profile.is_dir() else 'Hồ sơ riêng sẽ được tạo khi mở Flow')
    except (OSError, ValueError, TypeError, KeyError, ImportError) as error:
        add('configuration', 'fail', f'Không đọc được cấu hình ({type(error).__name__})', 'Kiểm tra YAML, tên dự án và dependencies.')
    add('flow.account', 'unknown', 'Chưa kiểm tra tài khoản, mạng hoặc selector trên Flow thật',
        f'python run.py flow {project_name or "TEN_DU_AN"} --action check --timeout 60')
    return {'scope':'offline checks only; not proof of login or successful generation',
            'project':project_name, 'ready_locally':not any(c['status']=='fail' for c in checks), 'checks':checks}


def main(project_name=None, as_json=False):
    report = inspect(project_name)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for check in report['checks']:
            print(f"[{check['status']}] {check['code']}: {check['detail']}")
            if check['action']: print('  → '+check['action'])
        print('Chẩn đoán cục bộ; không gửi prompt hoặc kiểm chứng đăng nhập Flow.')
    return 0 if report['ready_locally'] else 1
