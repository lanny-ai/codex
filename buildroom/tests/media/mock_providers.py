"""Local stand-in for the Kie.ai, Higgsfield, HeyGen and SubMagic request shapes, for tests only.

It answers the shapes gen.py and submagic.py are written for (themselves unverified against the
live services until --probe runs with real keys). Prompts containing "fail", "reject" or "explode"
trigger a provider failure, a 4xx rejection and a 5xx error. Run: python3 mock_providers.py PORT [MP4]"""
import json, sys, base64
from http.server import BaseHTTPRequestHandler, HTTPServer

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
MP4 = b"\x00\x00\x00\x18ftypmp42"
polls, seen = {}, []


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, obj, ctype="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        ctype = self.headers.get("Content-Type", "")
        body = json.loads(raw) if "json" in ctype and raw else {"_multipart_bytes": len(raw)}
        auth = self.headers.get("Authorization", "")
        seen.append({"path": self.path, "body": body})
        if self.path == "/api/v1/jobs/createTask":
            if auth != "Bearer testkey":
                return self.send(401, {"code": 401})
            p = body["input"]["prompt"]
            if "fail" in p:
                return self.send(200, {"code": 200, "data": {"taskId": "kfail"}})
            if "reject" in p:
                return self.send(422, {"code": 422, "msg": "bad aspect_ratio"})
            if "explode" in p:
                return self.send(503, {"code": 503})
            return self.send(200, {"code": 200, "data": {"taskId": "kv" if "duration" in body["input"] else "k1"}})
        if self.path == "/v2/video/generate":
            if self.headers.get("X-Api-Key") != "hgkey":
                return self.send(401, {})
            return self.send(200, {"data": {"video_id": "hg1"}})
        if self.path.startswith("/v1/projects"):
            if self.headers.get("x-api-key") != "sk-test":
                return self.send(401, {"error": "unauthorized"})
            if self.path == "/v1/projects/upload":
                return self.send(201, {"id": "sm-up-1", "status": "processing"})
            if self.path.endswith("/export"):
                return self.send(200, {"id": self.path.split("/")[3], "status": "exporting"})
            if "reject" in str(body.get("title", "")):
                return self.send(400, {"error": "videoUrl not reachable"})
            return self.send(201, {"id": "sm1", "status": "processing"})
        if auth != "Key hid:hsec":
            return self.send(401, {"detail": "unauthorized"})
        return self.send(200, {"request_id": "hv1" if "duration" in body else "h1", "status": "queued"})

    def do_GET(self):
        port = self.server.server_address[1]
        if self.path.startswith("/file/") and self.path.endswith(".mp4"):
            return self.send(200, MP4, "video/mp4")
        if self.path.startswith("/file/"):
            return self.send(200, PNG, "image/png")
        if self.path.startswith("/api/v1/chat/credit"):
            return self.send(200, {"code": 200, "data": 1234})
        if self.path.startswith("/v2/user/remaining_quota"):
            return self.send(200, {"data": {"remaining_quota": 600}})
        if self.path.startswith("/v1/video_status.get"):
            return self.send(200, {"data": {"status": "completed", "video_url": f"http://127.0.0.1:{port}/file/hg.mp4"}})
        if self.path.startswith("/v1/templates"):
            return self.send(200, {"templates": ["Sara", "Hormozi 2"]})
        if self.path.startswith("/v1/projects"):
            if self.headers.get("x-api-key") != "sk-test":
                return self.send(401, {})
            pid = self.path.split("/")[3].split("?")[0]
            polls[pid] = polls.get(pid, 0) + 1
            if polls[pid] < 2:
                return self.send(200, {"id": pid, "status": "processing"})
            return self.send(200, {"id": pid, "status": "completed", "downloadUrl": f"http://127.0.0.1:{port}/file/sm.mp4"})
        if self.path.startswith("/api/v1/jobs/recordInfo"):
            tid = self.path.split("=")[1]
            polls[tid] = polls.get(tid, 0) + 1
            if tid == "kfail":
                return self.send(200, {"data": {"state": "fail", "failMsg": "content policy"}})
            if polls[tid] < 2:
                return self.send(200, {"data": {"state": "generating"}})
            ext = "mp4" if tid == "kv" else "png"
            return self.send(200, {"data": {"state": "success", "resultJson": json.dumps({"resultUrls": [f"http://127.0.0.1:{port}/file/k.{ext}"]})}})
        if self.path.startswith("/requests/"):
            rid = self.path.split("/")[2]
            if rid == "h1":
                return self.send(200, {"status": "completed", "images": [{"url": f"http://127.0.0.1:{port}/file/h.png"}]})
            if rid == "hv1":
                return self.send(200, {"status": "completed", "video": {"url": f"http://127.0.0.1:{port}/file/h.mp4"}})
            return self.send(404, {"detail": "not found"})
        self.send(404, {})


def serve(port, mp4=None):
    global MP4
    if mp4:
        MP4 = mp4
    srv = HTTPServer(("127.0.0.1", port), H)
    return srv


if __name__ == "__main__":
    serve(int(sys.argv[1]), open(sys.argv[2], "rb").read() if len(sys.argv) > 2 else None).serve_forever()
