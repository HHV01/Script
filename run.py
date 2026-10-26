#!/usr/bin/env python3
"""Pipeline: bible nhân vật -> kịch bản -> voice -> phân cảnh -> prompt -> Google Flow -> kiểm tra/tải -> video.

  python run.py new <tên>                       tạo project mới từ projects/_template
  python run.py run <tên>                       chạy toàn bộ các bước (bước nào đã xong sẽ tự bỏ qua)
  python run.py run <tên> --from prompts        chạy từ một bước trở đi
  python run.py run <tên> --only render         chỉ chạy một bước
  python run.py run <tên> --only ping           kiểm tra kết nối extension với tab Flow
  thêm --force để làm lại bước đó
"""
import argparse
import shutil
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pipeline.common import PROJECTS, Project, load_env  # noqa: E402

STAGES = {
    "script": "s1_script", "voice": "s2_voice", "scenes": "s3_scenes", "prompts": "s4_prompts",
    "generate": "s5_generate", "collect": "s6_collect", "render": "s7_render",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new").add_argument("name")
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--from", dest="start", choices=STAGES)
    r.add_argument("--only", choices=[*STAGES, "ping"])
    r.add_argument("--force", action="store_true")
    a = ap.parse_args()
    load_env()

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
        import_module(f"pipeline.{STAGES[n]}").run(project, a.force)
    print("\nXong.")


if __name__ == "__main__":
    main()
