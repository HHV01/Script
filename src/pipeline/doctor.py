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
    for module in ('yaml', 'PIL', 'openai', 'vieneu'):
        found = importlib.util.find_spec(module) is not None
        add('dependency.'+module, 'pass' if found else ('fail' if module in ('yaml', 'PIL') else 'warn'),
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
            for name in ('script.txt','scenes.json','prompts.txt'):
                add('project.'+name, 'pass' if (path/name).is_file() else 'warn',
                    'Có tệp' if (path/name).is_file() else 'Chưa có tệp; không tự tạo lại các bước trước')
    except (OSError, ValueError, TypeError, KeyError, ImportError) as error:
        add('configuration', 'fail', f'Không đọc được cấu hình ({type(error).__name__})', 'Kiểm tra YAML, tên dự án và dependencies.')
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
        print('Chẩn đoán cục bộ; không gọi dịch vụ tạo nội dung.')
    return 0 if report['ready_locally'] else 1
