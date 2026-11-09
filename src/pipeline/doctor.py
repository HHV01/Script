"""Offline diagnostics. Never opens a browser, sends prompts, or prints secrets."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
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


def fix(report, log=None):
    """Install what can be installed offline. Never touches .env, profiles or projects.

    Only pip packages and the Playwright browser are installed automatically; FFmpeg is a
    system binary, so the command prints guidance instead of downloading a build.
    Progress and installer output go to stderr so `--json` stays parseable on stdout.
    """
    emit = log or (lambda message: print(message, file=sys.stderr, flush=True))
    steps = []
    missing_deps = sorted({c['code'].split('.', 1)[1] for c in report['checks']
                           if c['status'] in ('fail', 'warn') and c['code'].startswith('dependency.')})
    if missing_deps:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')]
        steps.append(('pip install', cmd))
    browser_missing = any(c['code'] == 'flow.browser' and c['status'] == 'fail'
                          for c in report['checks'])
    if browser_missing:
        steps.append(('playwright install', [sys.executable, '-m', 'playwright', 'install', 'chromium']))
    results = []
    for label, cmd in steps:
        emit(f'[fix] {label}: {" ".join(cmd)}')
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        except OSError as error:
            results.append(dict(step=label, ok=False, detail=type(error).__name__))
            continue
        for stream in (proc.stdout, proc.stderr):
            if stream and stream.strip():
                emit(stream.rstrip())
        results.append(dict(step=label, ok=proc.returncode == 0, detail=f'exit {proc.returncode}'))
    ffmpeg_missing = [c['code'] for c in report['checks']
                      if c['code'] in ('ffmpeg', 'ffprobe') and c['status'] != 'pass']
    if ffmpeg_missing:
        results.append(dict(step='ffmpeg', ok=False,
                            detail='Cài FFmpeg vào PATH hoặc đặt ffmpeg/ffprobe vào tools/ffmpeg/bin/'))
    return results


def main(project_name=None, as_json=False, do_fix=False):
    report = inspect(project_name)
    if do_fix:
        fixed = fix(report)
        report = inspect(project_name)
        report['fix'] = fixed
        if not as_json:
            for item in fixed:
                print(f"[fix] {item['step']}: {'xong' if item['ok'] else 'cần làm tay'} - {item['detail']}")
            if not fixed:
                print('[fix] Không có gì để cài tự động.')
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for check in report['checks']:
            print(f"[{check['status']}] {check['code']}: {check['detail']}")
            if check['action']: print('  → '+check['action'])
        print('Chẩn đoán cục bộ; không gửi prompt hoặc kiểm chứng đăng nhập Flow.')
    fix_ok = all(item['ok'] for item in report.get('fix', []))
    return 0 if report['ready_locally'] and fix_ok else 1
