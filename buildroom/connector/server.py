#!/usr/bin/env python3
"""Build Room connector: a remote MCP server that serves Build Room OS to current members.

Pilot version. Standard library only, so it runs on any host with Python 3.9+.

    python3 server.py --port 8787 [--members members.json] [--skills ../skills]

Members connect once (Claude desktop / claude.ai custom connector, Claude Code, Codex) and always get
the latest sessions; nothing is zipped. Each request is checked against the membership source.
The member's Business File never leaves their computer: no tool asks for it or stores it.

Protocol: MCP over Streamable HTTP (JSON responses), JSON-RPC 2.0, POST /mcp.
Auth (pilot): a per-member access key, sent as "Authorization: Bearer <key>" (Claude Code, Codex)
or in the path, /mcp/<key> (Claude desktop custom connectors, which take a URL only).
"""
import argparse, hashlib, hmac, json, os, re, secrets, sys, threading
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import join  # noqa: E402  (sign-up and approvals, same folder)
import usage  # noqa: E402  (the host dashboard's numbers, same folder)
SERVER_NAME = "buildroom"
SERVER_VERSION = "0.1.0-pilot"
PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
GRACE_DAYS_DEFAULT = 7
MAX_BODY = 1_000_000
# Media for the public pages (the setup video and its poster). Kept on the data volume, never in the repository.
MEDIA_TYPES = {"setup.mp4": "video/mp4", "setup.jpg": "image/jpeg"}
MAX_MEDIA = 80_000_000


def media_path(name):
    d = os.environ.get("BUILDROOM_DATA_DIR")
    return Path(d) / "media" / name if d and name in MEDIA_TYPES else None
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
SAFE_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,120}$")


def key_hash(key):
    return hashlib.sha256(key.strip().encode()).hexdigest()


# ---------------------------------------------------------------------------- membership source
# One question, asked in one place: is the person behind this key a current member?
# Swap the source by writing another class with the same check() and setting BUILDROOM_MEMBER_SOURCE.

class AllowlistSource:
    """Pilot source: a members.json you control (see members.py). Keys are stored only as sha256."""

    name = "allowlist"

    def __init__(self, path, store=None):
        self.path = Path(path)
        self.store = store  # sign-up members (join.py), kept on the host's disk
        self._cache, self._mtime = {}, None

    def listed_emails(self):
        """Emails on the host's own list (not sign-ups)."""
        self._load()
        return {e.get("email", "") for e in self._cache.values()}

    def _load(self):
        env = os.environ.get("BUILDROOM_MEMBERS_JSON")
        if env:  # hosted pilot: the list lives in a host setting (hashes only), pasted from `members.py export`
            if env != getattr(self, "_env_seen", None):
                data = json.loads(env)
                self._cache = {e["key_sha256"]: e for e in data.get("members", [])}
                self._grace = int(data.get("grace_days", GRACE_DAYS_DEFAULT))
                self._env_seen = env
            return
        try:
            m = self.path.stat().st_mtime
        except FileNotFoundError:
            self._cache, self._mtime = {}, None
            return
        if m != self._mtime:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._cache = {e["key_sha256"]: e for e in data.get("members", [])}
            self._grace = int(data.get("grace_days", GRACE_DAYS_DEFAULT))
            self._mtime = m

    def check(self, key, today=None):
        """Return (allowed, member_or_None, reason)."""
        self._load()
        h = key_hash(key)
        member = None
        entries = list(self._cache.items())
        if self.store:
            entries += [(e["key_sha256"], e) for e in self.store.members()]
        for stored, entry in entries:
            if hmac.compare_digest(stored, h):
                member = entry
                break
        if not member:
            return False, None, "unknown"
        today = today or date.today()
        if member.get("status") != "active":
            return False, member, "not-current"
        until = member.get("current_until")
        if until:
            grace = getattr(self, "_grace", GRACE_DAYS_DEFAULT)
            if today > date.fromisoformat(until) + timedelta(days=grace):
                return False, member, "expired"
        return True, member, "ok"


class NotBuiltYet:
    def __init__(self, which):
        self.name = which

    def check(self, key, today=None):
        raise RuntimeError(f"The {self.name} membership source is not built yet; use allowlist for the pilot.")


def make_source(kind, members_path, store=None):
    if kind == "allowlist":
        return AllowlistSource(members_path, store)
    if kind in ("gohighlevel", "mightynetworks"):
        return NotBuiltYet(kind)
    raise SystemExit(f"Unknown BUILDROOM_MEMBER_SOURCE: {kind}")


# ---------------------------------------------------------------------------- content
class Content:
    def __init__(self, skills_dir, releases_readme):
        self.skills_dir = Path(skills_dir)
        self.releases_readme = Path(releases_readme)

    def skills(self):
        out = []
        for d in sorted(self.skills_dir.iterdir()):
            f = d / "SKILL.md"
            if d.is_dir() and f.exists() and SAFE_NAME.match(d.name):
                text = f.read_text(encoding="utf-8")
                m = re.search(r"description:\s*\|?\s*\n?\s*(.+?)\n---", text, re.S)
                desc = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
                out.append({"skill": d.name, "description": desc})
        return out

    def skill_dir(self, name):
        if not isinstance(name, str) or not SAFE_NAME.match(name):
            return None
        d = self.skills_dir / name
        return d if (d / "SKILL.md").exists() else None

    def files(self, d):
        out = []
        for sub in ("references", "scripts"):
            p = d / sub
            if p.is_dir():
                out += [f"{sub}/{f.name}" for f in sorted(p.iterdir()) if f.is_file() and SAFE_FILE.match(f.name)
                        and f.suffix in (".md", ".py", ".mjs", ".json", ".txt", ".csv")]
        return out

    def read_file(self, d, rel):
        if not isinstance(rel, str) or rel not in self.files(d):
            return None
        return (d / rel).read_text(encoding="utf-8")

    def whats_new(self):
        try:
            rows = [l for l in self.releases_readme.read_text(encoding="utf-8").splitlines() if l.startswith("| `BuildRoom_OS_")]
        except FileNotFoundError:
            rows = []
        return "\n".join(rows[:2]) or "No release notes found."


# ---------------------------------------------------------------------------- MCP tools
TOOLS = [
    {"name": "buildroom_status",
     "description": "Check the member's Build Room access and the connector version. Call this first if anything is refused.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "buildroom_list_sessions",
     "description": "List every Build Room session (skill) with what it does and the words that start it. Use it to route a member's request to the right session.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "buildroom_start_session",
     "description": "Load one Build Room session's full instructions (its SKILL.md) and the list of its reference files. Follow the instructions exactly as you would an installed skill. The member's Business File stays on their computer: read and write it there, never send it here.",
     "inputSchema": {"type": "object", "properties": {"skill": {"type": "string", "description": "The skill name from buildroom_list_sessions, e.g. buildroom-search-answer-engine"}},
                     "required": ["skill"], "additionalProperties": False}},
    {"name": "buildroom_get_file",
     "description": "Load one reference or script file of a Build Room session, when its instructions tell you to read it. Paths come from buildroom_start_session.",
     "inputSchema": {"type": "object", "properties": {"skill": {"type": "string"}, "path": {"type": "string", "description": "e.g. references/answer-standard.md"}},
                     "required": ["skill", "path"], "additionalProperties": False}},
    {"name": "buildroom_whats_new",
     "description": "What changed in the latest Build Room OS releases, in plain words.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
]

# Some clients (Codex among them) lean on the opening of this text, so the first 512 characters stand on their own.
INSTRUCTIONS = ("Build Room OS: the current version of every Build Room session. When the member names a goal or says a "
                "Build Room phrase, call buildroom_list_sessions, pick the one session that fits, call "
                "buildroom_start_session and follow it. Use these sessions instead of any local skill named buildroom-*, "
                "which is an older copy. The member's Business File (BUILDROOM_BUSINESS_FILE.md) stays on their computer: "
                "read and update it there, and never send it here. "
                "Load reference files with buildroom_get_file only when the instructions say to. "
                "Once per conversation, where you can read files, check for old local copies of the tools: folders named "
                "buildroom-* in .claude/skills, .codex/skills, .agents/skills or skills in the working folder, or in "
                ".claude/skills, .codex/skills or .agents/skills in the home folder. If you find any, load "
                "references/connector-cleanup.md from buildroom-os with buildroom_get_file and follow it: ask the member "
                "once, then move the old copies into a backup folder for them. Never delete them, and never touch the "
                "Business File. If there are none, say nothing about it.")

REFUSALS = {
    "unknown": "This Build Room access key is not recognised. Check the connector link or key you were given, or ask the Build Room team for a new one.",
    "not-current": "Your Build Room membership is not current, so new sessions are paused. Your Business File and everything you made stay on your computer. Contact the Build Room team to reactivate.",
    "expired": "Your Build Room access has expired, so new sessions are paused. Your Business File and everything you made stay on your computer. Contact the Build Room team to renew.",
}


def text_result(text, is_error=False):
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


class App:
    def __init__(self, source, content, log_path=None):
        self.source, self.content = source, content
        self.log_path = Path(log_path) if log_path else None
        self.lock = threading.Lock()

    def log(self, member, tool, outcome, skill=None):
        if not self.log_path:
            return
        rec = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "member": (member or {}).get("email", "?"),
               "tool": tool, "skill": skill, "outcome": outcome}
        line = json.dumps(rec)
        with self.lock:
            # A copy on the data volume feeds the host dashboard. It holds the same line and nothing more.
            usage.append(os.environ.get("BUILDROOM_DATA_DIR"), line)
            if str(self.log_path) == "stdout":
                print("usage " + line, flush=True)
            else:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")

    def call_tool(self, member, name, args):
        args = args or {}
        c = self.content
        if name == "buildroom_status":
            return text_result(f"Build Room access: current ({member.get('email')}). Connector {SERVER_VERSION}; "
                               f"{len(c.skills())} sessions available. Membership source: {self.source.name}. "
                               "These are the current versions. If older copies of the Build Room tools are saved on this "
                               "computer (folders named buildroom-*), follow references/connector-cleanup.md from "
                               "buildroom-os to move them aside for the member.")
        if name == "buildroom_list_sessions":
            lines = [f"- {s['skill']}: {s['description']}" for s in c.skills()]
            return text_result("Build Room sessions:\n" + "\n".join(lines) + "\n\nThese are the current versions. If a local skill with "
                               "one of these names is also installed (from the old zip), use this connector's version, and see "
                               "references/connector-cleanup.md in buildroom-os to move the old copies aside for the member.")
        if name == "buildroom_start_session":
            d = c.skill_dir(args.get("skill"))
            if not d:
                return text_result("No Build Room session by that name. Call buildroom_list_sessions for the names.", True)
            files = c.files(d)
            body = (d / "SKILL.md").read_text(encoding="utf-8")
            note = ("\n\n---\nFiles for this session (load with buildroom_get_file when the instructions say to):\n"
                    + ("\n".join(f"- {f}" for f in files) or "- none")
                    + "\n\nScripts named in these instructions run on the member's computer. If one is not already in "
                      "the member's Build Room folder, load it with buildroom_get_file and save it there before running it. "
                      "Read and write the member's Business File on their computer only.")
            return text_result(body + note)
        if name == "buildroom_get_file":
            d = c.skill_dir(args.get("skill"))
            text = c.read_file(d, args.get("path")) if d else None
            if text is None:
                return text_result("No such file for that session. Use a path listed by buildroom_start_session.", True)
            return text_result(text)
        if name == "buildroom_whats_new":
            return text_result(c.whats_new())
        return None

    def handle(self, key, msg):
        """Handle one JSON-RPC message. Returns (http_status, response_or_None)."""
        if isinstance(msg, dict) and msg.get("jsonrpc") == "2.0" and "method" not in msg and ("result" in msg or "error" in msg):
            return 202, None  # a client's reply to a server request: accepted, nothing to send back
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            return 400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
        mid, method = msg.get("id"), msg["method"]
        if mid is None:  # notification
            return 202, None
        ok = lambda r: (200, {"jsonrpc": "2.0", "id": mid, "result": r})
        err = lambda code, m: (200, {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": m}})
        if method == "initialize":
            want = (msg.get("params") or {}).get("protocolVersion")
            ver = want if want in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            return ok({"protocolVersion": ver, "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": SERVER_NAME, "title": "Build Room OS", "version": SERVER_VERSION},
                       "instructions": INSTRUCTIONS})
        if method == "ping":
            return ok({})
        if method == "tools/list":
            return ok({"tools": TOOLS})
        if method == "tools/call":
            params = msg.get("params") or {}
            name = params.get("name")
            if name not in {t["name"] for t in TOOLS}:
                return err(-32602, f"Unknown tool: {name}")
            allowed, member, reason = self.source.check(key)
            if not allowed:
                self.log(member, name, reason)
                return ok(text_result(REFUSALS[reason], True))
            result = self.call_tool(member, name, params.get("arguments"))
            self.log(member, name, "ok", (params.get("arguments") or {}).get("skill"))
            return ok(result)
        return err(-32601, f"Method not found: {method}")


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BuildRoomConnector/" + SERVER_VERSION

        def log_message(self, fmt, *a):  # never log paths: they can carry an access key
            pass

        def _key(self):
            auth = self.headers.get("Authorization", "")
            if auth.lower().startswith("bearer "):
                return auth[7:].strip()
            parts = self.path.split("?")[0].strip("/").split("/")
            if len(parts) == 2 and parts[0] == "mcp" and parts[1]:
                return parts[1]
            return None

        def _send(self, status, obj=None, extra=None):
            body = b"" if obj is None else json.dumps(obj).encode()
            self.send_response(status)
            if obj is not None:
                self.send_header("Content-Type", "application/json")
            # Ask proxies (Railway's edge compresses and chunks bodies when a client offers gzip or zstd) to pass the
            # response through as sent: plain JSON with its Content-Length, which every MCP client can read.
            self.send_header("Cache-Control", (extra or {}).pop("Cache-Control", "no-store") + ", no-transform")
            self.send_header("Content-Encoding", "identity")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def _is_mcp_path(self):
            p = self.path.split("?")[0].strip("/").split("/")
            return p[0] == "mcp" and len(p) <= 2

        def _page(self, html):
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _ip(self):
            return (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()

        def _read_body(self, limit):
            """The request body, or None when it is missing or over the limit. Reads a Content-Length body or a
            chunked one (some MCP clients and proxies send chunked bodies with no Content-Length)."""
            if "chunked" in self.headers.get("Transfer-Encoding", "").lower():
                out = b""
                while True:
                    line = self.rfile.readline(1024)
                    try:
                        size = int(line.split(b";")[0].strip() or b"0", 16)
                    except ValueError:
                        return None
                    if size == 0:
                        while self.rfile.readline(1024) not in (b"\r\n", b"\n", b""):
                            pass
                        break
                    if len(out) + size > limit:
                        return None
                    out += self.rfile.read(size)
                    self.rfile.readline(1024)
                return out or None
            try:
                n = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return None
            if n <= 0 or n > limit:
                return None
            return self.rfile.read(n)

        def _json_body(self):
            raw = self._read_body(20000)
            try:
                return json.loads(raw) if raw else {}
            except ValueError:
                return {}

        def _admin_key(self):
            a = self.headers.get("Authorization", "")
            return a[7:].strip() if a.lower().startswith("bearer ") else ""

        def do_GET(self):
            route = self.path.split("?")[0].rstrip("/")
            if route == "/join":
                return self._page(join.JOIN_PAGE)
            if route == "/start":
                # Step-by-step setup for a new member. The video block shows only once a video has been uploaded.
                try:
                    html = (HERE / "start.html").read_text(encoding="utf-8")
                except OSError:
                    return self._send(404, {"error": "not found"})
                mp4 = media_path("setup.mp4")
                if not (mp4 and mp4.is_file()):
                    html = re.sub(r"<!--video-->.*?<!--/video-->", "", html, flags=re.S)
                return self._page(html)
            if route.startswith("/media/"):
                return self._media(route[len("/media/"):])
            if route in ("", "/guide"):
                # The public Quick Start Guide: one file, so it is current the moment a release merges.
                try:
                    return self._page((HERE / "guide.html").read_text(encoding="utf-8"))
                except OSError:
                    return self._send(404, {"error": "not found"})
            if route == "/admin":
                return self._page(join.ADMIN_PAGE)
            if route == "/admin/api":
                status, obj = app.join.admin("GET", route, self._admin_key(), {})
                return self._send(status, obj, {"Cache-Control": "no-store"})
            if route == "/admin/dashboard":
                try:
                    return self._page((HERE / "dashboard.html").read_text(encoding="utf-8"))
                except OSError:
                    return self._send(404, {"error": "not found"})
            if route in ("/admin/usage", "/admin/digest"):
                status, obj = app.join.admin("GET", "/admin/usage", self._admin_key(), {})
                if status != 200:
                    return self._send(status, obj, {"Cache-Control": "no-store"})
                d = os.environ.get("BUILDROOM_DATA_DIR")
                out = usage.summarize(usage.read(d), obj["members"], app.content.skills())
                out["open"], out["pending"] = obj["open"], sum(1 for r in obj["requests"] if r.get("status") == "pending")
                if route == "/admin/digest":
                    out = usage.digest(out, out["pending"])
                return self._send(200, out, {"Cache-Control": "no-store"})
            if self.path.split("?")[0] == "/health":
                return self._send(200, {"ok": True, "version": SERVER_VERSION})
            if self._is_mcp_path():
                # A member who opens their link in a browser gets instructions, never the key back.
                # Claude and other MCP clients do not ask for HTML, and still get 405 (no server-sent stream).
                if "text/html" in self.headers.get("Accept", ""):
                    return self._page(join.LINK_PAGE)
                return self._send(405, extra={"Allow": "POST"})
            self._send(404, {"error": "not found"})

        def _media(self, name):
            """A public media file from the data volume, with byte ranges so a video can be scrubbed."""
            f = media_path(name)
            if not (f and f.is_file()):
                return self._send(404, {"error": "not found"})
            size = f.stat().st_size
            start, end, status = 0, size - 1, 200
            m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "").strip())
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
                else:
                    start = max(size - int(m.group(2)), 0)
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    return self.end_headers()
                status = 206
            self.send_response(status)
            self.send_header("Content-Type", MEDIA_TYPES[name])
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "public, max-age=3600, no-transform")
            self.send_header("Content-Length", str(end - start + 1))
            if status == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            left = end - start + 1
            try:
                with f.open("rb") as fh:
                    fh.seek(start)
                    while left > 0:
                        chunk = fh.read(min(262144, left))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_PUT(self):
            """The owner uploads the setup video or its poster: PUT /admin/media/<name> with the admin key."""
            route = self.path.split("?")[0].rstrip("/")
            name = route[len("/admin/media/"):] if route.startswith("/admin/media/") else None
            if name is None:
                return self._send(405, extra={"Allow": "POST"})
            if not app.join.admin_ok(self._admin_key()):
                return self._send(401, {"error": "admin key required"})
            f = media_path(name)
            try:
                n = int(self.headers.get("Content-Length", ""))
            except ValueError:
                n = -1
            if f is None or not 0 < n <= MAX_MEDIA:
                self.close_connection = True
                return self._send(400, {"error": "unknown file name, no data folder, or a body that is missing or too large"})
            f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_suffix(f.suffix + ".part")
            left = n
            with tmp.open("wb") as fh:
                while left > 0:
                    chunk = self.rfile.read(min(262144, left))
                    if not chunk:
                        break
                    fh.write(chunk)
                    left -= len(chunk)
            if left:
                tmp.unlink(missing_ok=True)
                self.close_connection = True
                return self._send(400, {"error": "upload cut short"})
            tmp.replace(f)
            return self._send(200, {"ok": True, "name": name, "bytes": n})

        def do_DELETE(self):
            self._send(405, extra={"Allow": "POST"})

        def do_POST(self):
            route = self.path.split("?")[0].rstrip("/")
            if route == "/join":
                body = self._json_body()
                status, obj = app.join.submit(self._ip(), body if isinstance(body, dict) else {})
                return self._send(status, obj, {"Cache-Control": "no-store"})
            if route == "/admin/api":
                body = self._json_body()
                status, obj = app.join.admin("POST", route, self._admin_key(), body if isinstance(body, dict) else {})
                return self._send(status, obj, {"Cache-Control": "no-store"})
            if not self._is_mcp_path():
                return self._send(404, {"error": "not found"})
            key = self._key()
            if not key:
                return self._send(401, {"error": "A Build Room access key is required."},
                                  {"WWW-Authenticate": 'Bearer realm="buildroom"'})
            raw = self._read_body(MAX_BODY)
            if not raw:
                return self._send(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Bad body"}})
            try:
                msg = json.loads(raw)
            except ValueError:
                return self._send(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
            if isinstance(msg, list):
                return self._send(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Batches are not supported"}})
            # An unrecognised key is turned away at once, so a mistyped link fails when it is added.
            # A known member who is not current can connect and is told why on each tool call.
            if app.source.check(key)[2] == "unknown":
                return self._send(401, {"error": REFUSALS["unknown"]}, {"WWW-Authenticate": 'Bearer realm="buildroom"'})
            status, resp = app.handle(key, msg)
            extra = {"Mcp-Session-Id": secrets.token_hex(16)} if msg.get("method") == "initialize" else None
            self._send(status, resp, extra)

    return Handler


def build_app(members, skills, releases, log):
    store = join.Store(os.environ.get("BUILDROOM_DATA_DIR"))
    source = make_source(os.environ.get("BUILDROOM_MEMBER_SOURCE", "allowlist"), members, store)
    app = App(source, Content(skills, releases), log)
    app.join = join.Join(store, source.listed_emails)
    return app


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build Room connector (MCP over Streamable HTTP)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8787)))
    ap.add_argument("--members", default=os.environ.get("BUILDROOM_MEMBERS", str(HERE / "members.json")))
    ap.add_argument("--skills", default=os.environ.get("BUILDROOM_SKILLS", str(HERE.parent / "skills")))
    ap.add_argument("--releases", default=str(HERE.parent / "rollout" / "releases" / "README.md"))
    ap.add_argument("--log", default=os.environ.get("BUILDROOM_USAGE_LOG", str(HERE / "usage.jsonl")))
    a = ap.parse_args(argv)
    app = build_app(a.members, a.skills, a.releases, a.log)
    httpd = ThreadingHTTPServer((a.host, a.port), make_handler(app))
    print(f"Build Room connector {SERVER_VERSION} on http://{a.host}:{httpd.server_port}/mcp", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
