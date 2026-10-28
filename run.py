#!/usr/bin/env python3
"""Pipeline: bible nhân vật -> kịch bản -> voice -> phân cảnh -> prompt -> Google Flow -> kiểm tra/tải -> video.

  python run.py studio                         mở giao diện xưởng phim 3D
  python run.py new <tên>                       tạo project mới từ projects/_template
  python run.py run <tên>                       chạy toàn bộ các bước (bước nào đã xong sẽ tự bỏ qua)
  python run.py run <tên> --from prompts        chạy từ một bước trở đi
  python run.py run <tên> --only review         Mai duyệt kịch bản trước khi thu
  python run.py run <tên> --only render         chỉ chạy một bước
  python run.py run <tên> --only publish        xuất tiêu đề, mô tả, tag theo niche
  python run.py run <tên> --only ping           kiểm tra kết nối extension với tab Flow
  thêm --force để làm lại bước đó
"""
import argparse
import json
import shutil
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pipeline.common import PROJECTS, Project, load_env  # noqa: E402

from pipeline.stages import STAGES


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new").add_argument("name")
    studio = sub.add_parser("studio", help="Mở xưởng phim 3D và điều khiển pipeline")
    studio.add_argument("--port", type=int, default=8787)
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--from", dest="start", choices=STAGES)
    r.add_argument("--only", choices=[*STAGES, "ping"])
    r.add_argument("--force", action="store_true")
    visual = sub.add_parser("research-visuals", help="Lấy mẫu video lịch sử có view cao để đối chiếu hình ảnh")
    visual.add_argument("--days", type=int, default=90)
    visual.add_argument("--results", type=int, default=5)
    visual.add_argument("--min-views", type=int, default=50000)
    visual.add_argument("--duration", choices=['short','medium','long','any'], default='medium')
    animation = sub.add_parser("animate", help="Xuất animation cục bộ, không gọi API")
    animation.add_argument("--preset", choices=['stone_transport','stone_ramp','giza_cinematic'], default='stone_transport')
    animation.add_argument("--output", required=True)
    animation.add_argument("--duration", type=float, default=8)
    animation.add_argument("--width", type=int, default=960)
    animation.add_argument("--height", type=int, default=540)
    animation.add_argument("--fps", type=int, default=24)
    animation.add_argument("--sound", action="store_true")
    source_animation = sub.add_parser("animate-babylon", help="Dựng đoạn hợp đồng Babylon từ video nguồn, giữ lời đọc")
    source_animation.add_argument("--input", required=True)
    source_animation.add_argument("--output", required=True)
    a = ap.parse_args()
    load_env()

    if a.cmd == "animate-babylon":
        from pipeline.source_animation import main as source_main
        source_main(["--input", a.input, "--output", a.output])
        return

    if a.cmd == "animate":
        from pipeline.local_animation import main as animation_main
        animation_main(["--preset", a.preset, "--output", a.output, "--duration", str(a.duration), "--width", str(a.width), "--height", str(a.height), "--fps", str(a.fps)]+(["--sound"] if a.sound else []))
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
            if n not in ('script', 'review'):
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
    print("\nXong.")


if __name__ == "__main__":
    main()
