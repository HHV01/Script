#!/usr/bin/env python3
"""Pipeline: bible nhân vật -> kịch bản -> voice -> phân cảnh -> prompt -> Google Flow -> kiểm tra/tải -> video.

  python run.py studio                         mở giao diện xưởng video khoa học
  python run.py new <tên>                       tạo project mới từ projects/_template
  python run.py run <tên>                       chạy toàn bộ các bước (bước nào đã xong sẽ tự bỏ qua)
  python run.py run <tên> --from prompts        chạy từ một bước trở đi
  python run.py run <tên> --only review         kiểm tra kịch bản trước khi thu
  python run.py run <tên> --only render         chỉ chạy một bước
  python run.py run <tên> --only publish        xuất tiêu đề, mô tả, tag theo niche
  python run.py run <tên> --only ping           kiểm tra kết nối browser với tab Flow
  thêm --force để làm lại bước đó
"""
import argparse
import json
import re
import shutil
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.stages import STAGES

# CLI help and offline diagnostics must work before optional dependencies import.
for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='replace')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new").add_argument("name")
    sub.add_parser("menu", help="Menu mở xưởng và Google Flow")
    studio = sub.add_parser("studio", help="Mở xưởng video khoa học và điều khiển pipeline")
    studio.add_argument("--port", type=int, default=8787)
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--from", dest="start", choices=STAGES)
    r.add_argument("--only", choices=[*STAGES, "ping"])
    r.add_argument("--force", action="store_true")
    r.add_argument("--upload", action="store_true", help="Yêu cầu upload rõ ràng sau khi các cổng đạt")
    doctor = sub.add_parser("doctor", help="Kiểm tra cục bộ; không mở browser hoặc tạo ảnh")
    doctor.add_argument("project", nargs="?")
    doctor.add_argument("--json", action="store_true", dest="as_json")
    flow = sub.add_parser("flow", help="Mở, kiểm tra, hoặc tạo đúng một cảnh Google Flow")
    flow.add_argument("project")
    flow.add_argument("--action", choices=['open','check','generate-one'], default='check')
    flow.add_argument("--timeout", type=int, default=60)
    flow.add_argument("--scene", type=int, default=1)
    flow.add_argument("--force", action="store_true", help="Tạo lại có chủ ý sau khi kiểm tra gallery")
    visual = sub.add_parser("research-visuals", help="Lấy mẫu video tham khảo để đối chiếu hình ảnh")
    visual.add_argument("--days", type=int, default=90)
    visual.add_argument("--results", type=int, default=5)
    visual.add_argument("--min-views", type=int, default=50000)
    visual.add_argument("--duration", choices=['short','medium','long','any'], default='medium')
    a = ap.parse_args()
    if a.cmd == "menu":
        from pipeline.launcher import main as menu_main
        menu_main()
        return
    if a.cmd == "doctor":
        from pipeline.doctor import main as doctor_main
        raise SystemExit(doctor_main(a.project, a.as_json))
    from pipeline.common import PROJECTS, Project, load_env
    load_env()
    name = getattr(a, 'name', None) or getattr(a, 'project', None)
    if name is not None:
        if (not re.fullmatch(r'[\w-]{1,64}', name) or name.startswith('_')
                or (PROJECTS/name).is_symlink() or (PROJECTS/name).resolve().parent != PROJECTS.resolve()):
            raise SystemExit('Tên dự án không hợp lệ; chỉ dùng chữ, số, gạch nối/gạch dưới, không đường dẫn.')
    if a.cmd == 'flow':
        from pipeline.flow_cli import run as flow_main
        from pipeline.bridge import BridgeError
        try:
            flow_main(Project(a.project), a.action, a.timeout, a.scene, a.force)
        except BridgeError as error:
            raise SystemExit(str(error)) from None
        return

    if a.cmd == "research-visuals":
        from pipeline.visual_benchmark import main as research_main
        research_main(["--days", str(a.days), "--results", str(a.results), "--min-views", str(a.min_views), "--duration", a.duration])
        return

    if a.cmd == "studio":
        from studio.server import main as studio_main
        studio_main(["--port", str(a.port)])
        return

    if a.cmd == "new":
        dst = PROJECTS / a.name
        if dst.exists():
            raise SystemExit(f"{dst} đã tồn tại")
        shutil.copytree(PROJECTS / "_template", dst)
        print(f"Đã tạo {dst}. Sửa project.yaml (chủ đề, nhân vật) rồi: python run.py run {a.name}")
        return

    project = Project(a.name)
    if a.only == "ping":
        import_module("pipeline.s5_generate").ping(project)
        return
    names = list(STAGES)
    if a.only:
        names = [a.only]
    elif a.start:
        names = names[names.index(a.start):]
    for n in names:
        print(f"\n=== {n} ===")
        print('@@STUDIO ' + json.dumps({'stage': n, 'status': 'running'}), flush=True)
        try:
            if n not in ('script', 'review', 'qc'):
                from pipeline.script_review import require_approval, digest
                from pipeline.common import need
                plan = require_approval(project)
                if plan and n != 'voice':
                    try:
                        source = json.loads((project.dir/'voice.source.json').read_text(encoding='utf-8'))
                    except (OSError, ValueError):
                        source = None
                    expected = {'script_sha256': digest(project.script.read_text(encoding='utf-8')),
                                'plan_sha256': digest(plan), 'voice_config_sha256': digest(project.settings['voice'])}
                    need(source == expected, 'Giọng đọc chưa khớp bản duyệt; chạy --from voice --force để tạo lại phần sau.')
            import_module(f"pipeline.{STAGES[n]}").run(project, a.force)
        except BaseException:
            print('@@STUDIO ' + json.dumps({'stage': n, 'status': 'failed'}), flush=True)
            raise
        print('@@STUDIO ' + json.dumps({'stage': n, 'status': 'completed'}), flush=True)
    if a.upload:
        from pipeline.common import need
        need(project.final.exists(), 'Chưa có final.mp4; không thể upload.')
        from pipeline.youtube_upload import upload
        upload(project)
    print("\nXong.")


if __name__ == "__main__":
    main()
