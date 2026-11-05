"""Menu cục bộ, không mở worker nền."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def main():
    while True:
        print('\nXƯỞNG VIDEO\n1. Mở xưởng\n2. Kiểm tra môi trường\n0. Thoát')
        choice = input('Chọn: ').strip()
        if choice == '0': return
        if choice in ('1', '2'):
            subprocess.run([sys.executable, str(ROOT/'run.py'), 'studio' if choice == '1' else 'doctor'], cwd=ROOT)
