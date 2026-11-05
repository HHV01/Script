"""Local dashboard with a real subprocess worker and bounded status history."""
import argparse
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from pipeline.common import PROJECTS, load_yaml, load_env
from pipeline.script_review import review_summary

from pipeline.stages import STAGES as STAGE_MODULES
STAGES = list(STAGE_MODULES)
LABELS = ['Biên kịch', 'Duyệt kịch bản', 'Phòng thu', 'Phân cảnh', 'Mỹ thuật', 'Kiểm ảnh', 'Dựng phim', 'Xuất bản', 'Kiểm thử']
NAME = re.compile(r'^[\w-]{1,64}$', re.UNICODE)
STATIC = Path(__file__).parent / 'static'


def project_path(name):
    if not isinstance(name, str) or not NAME.fullmatch(name) or name.startswith('_'):
        raise ValueError('Tên project chỉ gồm chữ, số, dấu gạch; không bắt đầu bằng _.')
    path = PROJECTS / name
    if path.resolve().parent != PROJECTS.resolve() or path.is_symlink():
        raise ValueError('Đường dẫn project không hợp lệ.')
    return path


def qc_summary(p):
    """Phiếu của nhân viên kiểm thử, đọc từ publish-review.json."""
    fallback = {'status': 'not_tested', 'tester': {'name': 'Gạo', 'role': 'Nhân viên kiểm thử'}}
    report_path = p / 'publish-review.json'
    if not report_path.is_file():
        return fallback
    try:
        report = json.loads(report_path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return fallback
    checks = report.get('checks') or []
    passed = sum(1 for check in checks if check.get('status') == 'pass')
    warned = sum(1 for check in checks if check.get('status') == 'warn')
    failed = sum(1 for check in checks if check.get('status') == 'fail')
    stale = False
    video = p / 'final.mp4'
    try:
        tested = datetime.fromisoformat(report['generated_at']).timestamp()
        stale = video.is_file() and video.stat().st_mtime > tested + 1
    except (KeyError, ValueError, OSError):
        pass
    status = 'stale' if stale else ('approved' if report.get('approved') else 'blocked')
    parts = [f'{passed}/{len(checks)} mục đạt']
    if warned:
        parts.append(f'{warned} cảnh báo')
    if failed:
        parts.append(f'{failed} chưa đạt')
    if stale:
        parts.append('video đã thay đổi sau lần kiểm')
    return {'status': status, 'score': report.get('score'),
            'tester': report.get('tester') or fallback['tester'],
            'tested_at': report.get('generated_at'), 'summary': ', '.join(parts),
            'checks': [{'label': c.get('label'), 'status': c.get('status'), 'detail': c.get('detail')}
                       for c in checks],
            'blockers': report.get('blockers') or []}


def projects():
    items = []
    for p in sorted(PROJECTS.iterdir()):
        if not p.is_dir() or p.name.startswith('_') or not NAME.fullmatch(p.name) or p.is_symlink():
            continue
        config = p / 'project.yaml'
        if config.is_file():
            try:
                cfg = load_yaml(config)
                items.append({'name': p.name, 'topic': cfg.get('topic', p.name),
                              'niche': cfg.get('niche', ''), 'minutes': cfg.get('minutes', 15),
                              'video': (p/'final.mp4').is_file(), 'metadata': (p/'publish.json').is_file(),
                              'review': review_summary(p), 'testing': qc_summary(p)})
            except Exception:
                items.append({'name': p.name, 'topic': 'Không đọc được project.yaml', 'invalid': True})
    return items


class Studio:
    def __init__(self):
        load_env()
        self.lock = threading.RLock()
        self.process = None
        self.state = self.empty()
        self.token = secrets.token_urlsafe(32)
        from .manager import ChannelManager
        self.manager = ChannelManager(self, ROOT, create_project)

    @staticmethod
    def empty():
        return {'project': None, 'status': 'idle', 'stage': None, 'stages': {}, 'logs': [],
                'started_at': None, 'finished_at': None, 'exit_code': None, 'cancel_requested': False}

    def snapshot(self):
        with self.lock:
            return json.loads(json.dumps(self.state))

    def save(self):
        directory = ROOT / '.studio'
        directory.mkdir(exist_ok=True)
        target = directory / 'last-run.json'
        # Unique scratch files and short retries tolerate Windows file-indexer locks.
        temp = target.with_name(f'{target.name}.{secrets.token_hex(6)}.tmp')
        try:
            temp.write_text(json.dumps(self.state, ensure_ascii=False), encoding='utf-8')
            for attempt in range(6):
                try:
                    temp.replace(target)
                    break
                except PermissionError:
                    if attempt == 5:
                        raise
                    time.sleep(0.03 * (attempt + 1))
        finally:
            temp.unlink(missing_ok=True)

    def restore(self):
        target = ROOT / '.studio/last-run.json'
        if target.exists():
            try:
                state = json.loads(target.read_text(encoding='utf-8'))
                if state.get('status') in ('running', 'stopping'):
                    state['status'] = 'interrupted'
                    if state.get('stage'):
                        state['stages'][state['stage']] = 'interrupted'
                self.state = state
            except (ValueError, OSError, KeyError, TypeError):
                pass

    def start(self, name, stage=None, only=False):
        path = project_path(name)
        if not (path/'project.yaml').is_file():
            raise ValueError('Project không tồn tại.')
        if stage is not None and stage not in STAGES:
            raise ValueError('Bước không hợp lệ.')
        with self.lock:
            if self.state['status'] in ('running', 'stopping'):
                raise ValueError('Đang có công việc chạy. Hãy đợi hoặc dừng trước.')
            command = [sys.executable, '-u', str(ROOT/'run.py'), 'run', name]
            if stage:
                command += ['--only' if only else '--from', stage]
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                       errors='replace', **({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
                                       if os.name == 'nt' else {'start_new_session': True}))
            self.process = process
            self.state = self.empty()
            self.state.update(project=name, status='running', started_at=time.time())
            self.save()
            threading.Thread(target=self.consume, args=(process,), daemon=True).start()

    def consume(self, process):
        for line in process.stdout:
            with self.lock:
                line = line.rstrip()
                if line.startswith('@@STUDIO '):
                    try:
                        event = json.loads(line[len('@@STUDIO '):])
                        stage, status = event['stage'], event['status']
                        if stage in STAGES and status in ('running', 'completed', 'failed'):
                            self.state['stage'] = stage
                            self.state['stages'][stage] = status
                    except (ValueError, KeyError, TypeError):
                        pass
                elif line:
                    # Never serve API key values that a third-party exception may echo.
                    for name in ('OPENCODE_API_KEY', 'YOUTUBE_API_KEY'):
                        value = os.environ.get(name)
                        if value:
                            line = line.replace(value, '[ẩn API key]')
                    line = re.sub(r'(?i)((?:api[_-]?key|token|authorization)[=:]\s*)[^\s&]+', r'\1[ẩn]', line)
                    self.state['logs'].append({'time': time.time(), 'text': line[:2000]})
                    self.state['logs'] = self.state['logs'][-200:]
                self.save()
        code = process.wait()
        process.stdout.close()
        with self.lock:
            self.state['exit_code'] = code
            self.state['finished_at'] = time.time()
            self.state['status'] = ('cancelled' if self.state['cancel_requested'] else
                                    'completed' if code == 0 else 'failed')
            stage = self.state['stage']
            if stage and self.state['stages'].get(stage) == 'running':
                self.state['stages'][stage] = self.state['status']
            self.process = None
            self.save()

    def stop(self):
        with self.lock:
            if not self.process or self.process.poll() is not None:
                return
            self.state.update(status='stopping', cancel_requested=True)
            process = self.process
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            self.save()
        def finish():
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        threading.Thread(target=finish, daemon=True).start()


def create_project(body):
    import shutil
    import yaml
    path = project_path(body.get('name'))
    topic = str(body.get('topic', '')).strip()
    niche = str(body.get('niche', '')).strip()
    minutes = body.get('minutes', 15)
    if not topic or len(topic) > 1000 or len(niche) > 1000:
        raise ValueError('Nhập chủ đề (tối đa 1000 ký tự).')
    if isinstance(minutes, bool) or not isinstance(minutes, int) or not 1 <= minutes <= 60:
        raise ValueError('Thời lượng mục tiêu từ 1 đến 60 phút.')
    if path.exists():
        raise ValueError('Tên project đã tồn tại; hãy chọn tên khác.')
    cfg = load_yaml(PROJECTS/'_template/project.yaml')
    cfg.update(topic=topic, minutes=minutes)
    if niche:
        cfg['niche'] = niche
    # mkdir is exclusive so two requests cannot overwrite an existing project.
    path.mkdir()
    try:
        shutil.copytree(PROJECTS/'_template', path, dirs_exist_ok=True)
        (path/'project.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding='utf-8')
    except Exception:
        shutil.rmtree(path)
        raise
    return path.name


def handler(studio):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, data, code=200, content_type='application/json; charset=utf-8'):
            body = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, (dict, list)) else data
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def trusted_host(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def do_GET(self):
            if not self.trusted_host():
                return self.send({'error': 'Chỉ truy cập qua localhost.'}, 403)
            path = urlparse(self.path).path
            if path == '/api/status':
                return self.send({'run': studio.snapshot(), 'projects': projects(), 'token': studio.token, 'manager': studio.manager.snapshot()})
            if path == '/oauth/callback':
                query = parse_qs(urlparse(self.path).query)
                try:
                    studio.manager.client.finish_authorization(query.get('code', [''])[0], query.get('state', [''])[0])
                    message = 'Đã kết nối quyền đọc kênh. Đóng tab này, trở lại xưởng và cập nhật báo cáo.'
                except ValueError as error:
                    message = str(error)
                import html
                return self.send(('<!doctype html><meta charset="utf-8"><meta name="referrer" content="no-referrer"><title>Kết nối kênh</title><p>'+html.escape(message)+'</p>').encode(), content_type='text/html; charset=utf-8')
            if path in ('/manager/report.json', '/manager/report.md'):
                file = studio.manager.directory/path.rsplit('/',1)[-1]
                if not file.is_file():
                    return self.send({'error': 'Chưa có báo cáo.'}, 404)
                return self.send(file.read_bytes(), content_type='application/json' if path.endswith('.json') else 'text/markdown; charset=utf-8')
            if path == '/':
                return self.send((STATIC/'index.html').read_bytes(), content_type='text/html; charset=utf-8')
            if path in ('/app.js', '/style.css'):
                return self.send((STATIC/path[1:]).read_bytes(), content_type=(
                    'application/javascript; charset=utf-8' if path.endswith('.js') else 'text/css; charset=utf-8'))
            if path.startswith('/artifacts/'):
                parts = path.split('/')
                if len(parts) != 4 or parts[3] not in ('final.mp4', 'subtitles.srt', 'publish.json', 'publish.txt', 'script.review.json', 'recording_plan.json', 'recording_script.md', 'script.txt'):
                    return self.send({'error': 'Không tìm thấy file.'}, 404)
                try:
                    file = project_path(unquote(parts[2])) / parts[3]
                    if file.is_symlink() or not file.is_file():
                        raise ValueError('File chưa sẵn sàng.')
                    types = {'mp4': 'video/mp4', 'srt': 'application/x-subrip', 'json': 'application/json', 'txt': 'text/plain; charset=utf-8', 'md': 'text/markdown; charset=utf-8'}
                    # Stream large videos instead of loading them into memory.
                    self.send_response(200)
                    self.send_header('Content-Type', types[file.suffix[1:]])
                    self.send_header('Content-Length', str(file.stat().st_size))
                    self.send_header('Content-Disposition', f'attachment; filename="{parts[3]}"')
                    self.end_headers()
                    import shutil
                    with file.open('rb') as source:
                        shutil.copyfileobj(source, self.wfile)
                except (ValueError, OSError):
                    self.send({'error': 'File chưa sẵn sàng.'}, 404)
                return
            self.send({'error': 'Không tìm thấy.'}, 404)

        def do_POST(self):
            origin = self.headers.get('Origin')
            expected_origin = f"http://{self.headers.get('Host')}"
            if not self.trusted_host() or (origin and origin != expected_origin) or not secrets.compare_digest(
                    self.headers.get('X-Studio-Token', ''), studio.token):
                return self.send({'error': 'Phiên không hợp lệ; tải lại trang.'}, 403)
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 16384:
                    raise ValueError('Yêu cầu quá lớn hoặc rỗng.')
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError('Yêu cầu không hợp lệ.')
                path = urlparse(self.path).path
                if path == '/api/run':
                    studio.start(body.get('project'), body.get('stage'), body.get('only') is True)
                elif path == '/api/stop':
                    studio.stop()
                elif path == '/api/manager/analyze':
                    studio.manager.analyze()
                elif path == '/api/manager/settings':
                    studio.manager.configure(body)
                elif path == '/api/manager/delegate':
                    return self.send({'project': studio.manager.delegate(body.get('brief_id'))})
                elif path == '/api/manager/connect':
                    return self.send({'url': studio.manager.client.authorize(self.server.server_port)})
                elif path == '/api/manager/disconnect':
                    studio.manager.client.disconnect()
                elif path == '/api/projects':
                    return self.send({'name': create_project(body)}, 201)
                else:
                    return self.send({'error': 'Không tìm thấy.'}, 404)
                self.send({'ok': True})
            except (ValueError, TypeError) as e:
                self.send({'error': str(e)}, 400)
            except OSError:
                self.send({'error': 'Không thể thực hiện thao tác; kiểm tra quyền thư mục hoặc tiến trình.'}, 500)
    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description='Xưởng video Dấu Vết Văn Minh')
    parser.add_argument('--port', type=int, default=8787)
    args = parser.parse_args(argv)
    studio = Studio()
    studio.restore()
    studio.manager.start_scheduler()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(studio))
    print(f'Xưởng video đang chạy tại cổng {args.port} trên localhost. Ctrl+C để tắt.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        studio.manager.close()
        studio.stop()
        server.server_close()


if __name__ == '__main__':
    main()
