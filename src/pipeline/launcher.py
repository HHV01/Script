"""Small terminal menu using the same public CLI, no hidden background worker."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    while True:
        print('\nXƯỞNG VIDEO — chọn thao tác')
        print('1. Mở xưởng\n2. Kiểm tra môi trường\n3. Mở Flow / đăng nhập\n4. Kiểm tra Flow\n5. Tạo một cảnh (có thể dùng credit)\n0. Thoát')
        choice = input('Chọn: ').strip()
        if choice == '0': return
        if choice not in ('1','2','3','4','5'): continue
        args = ['studio'] if choice == '1' else ['doctor'] if choice == '2' else None
        if args is None:
            projects = [p.name for p in sorted((ROOT/'projects').iterdir())
                        if p.is_dir() and not p.is_symlink() and not p.name.startswith('_') and (p/'project.yaml').is_file()]
            if not projects:
                print('Chưa có dự án. Tạo bằng: python run.py new ten_du_an')
                continue
            for i, name in enumerate(projects, 1): print(f'{i}. {name}')
            try:
                index = int(input('Số dự án: '))-1
                if not 0 <= index < len(projects): raise ValueError()
                name = projects[index]
                args = ['flow', name, '--action', {'3':'open','4':'check','5':'generate-one'}[choice]]
                if choice == '5':
                    scene = int(input('ID cảnh muốn tạo: '))
                    if scene < 1: raise ValueError()
                    args += ['--scene', str(scene)]
            except ValueError:
                print('Lựa chọn không hợp lệ.')
                continue
        subprocess.run([sys.executable, str(ROOT/'run.py'), *args], cwd=ROOT)
