"""Cầu nối giữa Python và extension Chrome trong tab Google Flow (chỉ chạy trên 127.0.0.1).

Extension (flow_extension/background.js) hỏi GET /next để nhận lệnh, làm việc trong tab Flow,
rồi POST /result. Ảnh được extension POST thẳng lên /upload?scene=<id>&ext=<png|jpg|webp>.
"""
import json
import queue
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class BridgeError(Exception):
    pass


class Bridge:
    def __init__(self, port, images_dir, token=None):
        self.port, self.images_dir, self.token = port, images_dir, token
        self.cmds = queue.Queue()
        self.pending = {}          # id -> {"event": Event, "result": dict}
        self.last_seen = 0.0
        self.server = None

    # ---------- phía Python ----------
    def start(self):
        bridge = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a): pass

            def _send(self, obj, code=200):
                body = json.dumps(obj).encode()
                self.send_response(code)
                for k, v in (("Content-Type", "application/json"), ("Content-Length", str(len(body))),
                             ("Access-Control-Allow-Origin", "*"),
                             ("Access-Control-Allow-Private-Network", "true")):
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):
                self.send_response(204)
                for k, v in (("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Headers", "*"),
                             ("Access-Control-Allow-Methods", "GET,POST"),
                             ("Access-Control-Allow-Private-Network", "true")):
                    self.send_header(k, v)
                self.end_headers()

            def _authorized(self):
                if not bridge.token:
                    return True
                return self.headers.get("X-Bridge-Token") == bridge.token

            def do_GET(self):
                if not self._authorized():
                    self._send({"error": "unauthorized"}, 403)
                    return
                if urlparse(self.path).path == "/next":
                    bridge.last_seen = time.time()
                    try:
                        self._send(bridge.cmds.get(timeout=20))
                    except queue.Empty:
                        self._send({"cmd": "idle"})
                else:
                    self._send({"error": "not found"}, 404)

            def do_POST(self):
                if not self._authorized():
                    self._send({"error": "unauthorized"}, 403)
                    return
                u = urlparse(self.path)
                n = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(n)
                if u.path == "/result":
                    r = json.loads(body)
                    slot = bridge.pending.get(r["id"])
                    if slot:
                        slot["result"] = r
                        slot["event"].set()
                    self._send({"ok": True})
                elif u.path == "/upload":
                    q = parse_qs(u.query)
                    scene, ext = int(q["scene"][0]), q.get("ext", ["png"])[0]
                    bridge.images_dir.mkdir(parents=True, exist_ok=True)
                    for old in bridge.images_dir.glob(f"{scene:03d}.*"):
                        old.unlink()
                    (bridge.images_dir / f"{scene:03d}.{ext}").write_bytes(body)
                    self._send({"ok": True, "bytes": len(body)})
                else:
                    self._send({"error": "not found"}, 404)

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self):
        if self.server:
            self.server.shutdown()

    def connected(self):
        return time.time() - self.last_seen < 30

    def wait_connected(self, timeout=300):
        t0 = time.time()
        while not self.connected():
            if time.time() - t0 > timeout:
                raise BridgeError("Extension chưa kết nối. Mở tab Google Flow trong Chrome đã nạp flow_extension/.")
            time.sleep(0.5)

    def call(self, cmd, data=None, timeout=60):
        cid = uuid.uuid4().hex
        slot = {"event": threading.Event(), "result": None}
        self.pending[cid] = slot
        self.cmds.put({"id": cid, "cmd": cmd, "data": data or {}})
        ok = slot["event"].wait(timeout)
        self.pending.pop(cid, None)
        if not ok:
            raise BridgeError(f"Hết thời gian chờ lệnh '{cmd}'")
        r = slot["result"]
        if not r.get("ok"):
            raise BridgeError(r.get("error", "lỗi không rõ"))
        return r.get("data", {})


_instance = {}


def get_bridge(project):
    """Mỗi tiến trình dùng chung 1 bridge cho cả bước generate và collect."""
    key = project.name
    if key not in _instance:
        b = Bridge(project.settings["flow"]["port"], project.images_dir, project.settings["flow"].get("token"))
        b.start()
        _instance[key] = b
    return _instance[key]
