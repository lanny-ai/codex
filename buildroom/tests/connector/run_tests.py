#!/usr/bin/env python3
"""Tests for the Build Room connector (pilot MCP server).

Usage:  python3 buildroom/tests/connector/run_tests.py
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, shutil, subprocess, tempfile, threading, urllib.error, urllib.request  # noqa: E402
from datetime import date, timedelta  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CON = ROOT / "connector"
sys.path.insert(0, str(CON))
import server  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    RESULTS.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"   [{detail}]"))


def members_cli(path, *args):
    return subprocess.run([sys.executable, "-B", str(CON / "members.py"), "--members", str(path), "--base-url", "https://example.test", *args],
                          capture_output=True, text=True)


def post(url, obj, key=None, raw=None):
    data = raw if raw is not None else json.dumps(obj).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    if key:
        req.add_header("Authorization", "Bearer " + key)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read()
            return r.status, (json.loads(body) if body else None), dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, (json.loads(body) if body else None), dict(e.headers)


def call(url, key, tool, args=None, mid=1):
    return post(url, {"jsonrpc": "2.0", "id": mid, "method": "tools/call", "params": {"name": tool, "arguments": args or {}}}, key)


def text(resp):
    return resp["result"]["content"][0]["text"], resp["result"]["isError"]


def main():
    tmp = Path(tempfile.mkdtemp(prefix="br-connector-"))
    mf, log = tmp / "members.json", tmp / "usage.jsonl"
    try:
        # ---- members.py ------------------------------------------------------------
        p = members_cli(mf, "add", "Pilot@Example.com", "--until", (date.today() + timedelta(days=30)).isoformat(), "--name", "Pat")
        key = next((w for w in p.stdout.split() if w.startswith("br_")), None)
        check("members add: prints a key once, with both connection forms", p.returncode == 0 and key and f"/mcp/{key}" in p.stdout and f"Bearer {key}" in p.stdout, p.stdout)
        stored = mf.read_text()
        check("members.json keeps only the key's sha256, never the key", key not in stored and server.key_hash(key) in stored)
        check("members.json is private to the owner (mode 600)", (mf.stat().st_mode & 0o077) == 0)
        check("email stored lower-case", '"pilot@example.com"' in stored)
        check("adding the same member twice is refused", members_cli(mf, "add", "pilot@example.com").returncode == 1)
        lapsed_key = next(w for w in members_cli(mf, "add", "gone@example.com").stdout.split() if w.startswith("br_"))
        members_cli(mf, "lapse", "gone@example.com")
        old_key = next(w for w in members_cli(mf, "add", "old@example.com", "--until", (date.today() - timedelta(days=30)).isoformat()).stdout.split() if w.startswith("br_"))
        grace_key = next(w for w in members_cli(mf, "add", "grace@example.com", "--until", (date.today() - timedelta(days=3)).isoformat()).stdout.split() if w.startswith("br_"))
        check("members list shows status without keys", "gone@example.com" in members_cli(mf, "list").stdout and "br_" not in members_cli(mf, "list").stdout)
        check("members.py rejects a bad date", members_cli(mf, "add", "x@example.com", "--until", "next week").returncode != 0)

        # ---- the server ---------------------------------------------------------------
        app = server.build_app(mf, ROOT / "skills", ROOT / "rollout/releases/README.md", log)
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(app))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{httpd.server_port}"
        url = base + "/mcp"

        s, r, h = post(url, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}}, key)
        check("initialize: 200, server info, tools capability, instructions", s == 200 and r["result"]["serverInfo"]["name"] == "buildroom"
              and "tools" in r["result"]["capabilities"] and "Business File" in r["result"]["instructions"], r)
        check("initialize: echoes a supported protocol version, issues a session id", r["result"]["protocolVersion"] == "2025-06-18" and h.get("Mcp-Session-Id"))
        s, r, _ = post(url, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}}, key)
        check("initialize: an unknown version gets the newest supported", r["result"]["protocolVersion"] == server.PROTOCOL_VERSIONS[0])
        s, r, _ = post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, key)
        check("notification: 202 with no body", s == 202 and r is None, s)
        s, r, _ = post(url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, key)
        names = [t["name"] for t in r["result"]["tools"]]
        check("tools/list: the five Build Room tools", names == ["buildroom_status", "buildroom_list_sessions", "buildroom_start_session", "buildroom_get_file", "buildroom_whats_new"], names)
        check("ping answers", post(url, {"jsonrpc": "2.0", "id": 3, "method": "ping"}, key)[1]["result"] == {})
        check("unknown method: JSON-RPC -32601", post(url, {"jsonrpc": "2.0", "id": 4, "method": "nope"}, key)[1]["error"]["code"] == -32601)

        # ---- access ---------------------------------------------------------------------
        check("no key: 401", post(url, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})[0] == 401)
        check("unknown key: 401 at connection time", post(url, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, "br_wrong")[0] == 401)
        t, err = text(call(url, key, "buildroom_status")[1])
        check("current member: status says current", not err and "current (pilot@example.com)" in t, t)
        s, r, _ = post(f"{url}/{key}", {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "buildroom_status", "arguments": {}}})
        check("key in the URL works (Claude desktop custom connectors)", s == 200 and not r["result"]["isError"])
        t, err = text(call(url, lapsed_key, "buildroom_start_session", {"skill": "buildroom-os"})[1])
        check("lapsed member: refused politely, told their files stay on their computer", err and "not current" in t and "stay on your computer" in t, t)
        check("lapsed member can still connect (so they see why)", post(url, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, lapsed_key)[0] == 200)
        t, err = text(call(url, old_key, "buildroom_list_sessions")[1])
        check("expired past the grace period: refused", err and "expired" in t, t)
        t, err = text(call(url, grace_key, "buildroom_list_sessions")[1])
        check("expired 3 days ago, inside the 7-day grace: allowed", not err, t)
        members_cli(mf, "reactivate", "gone@example.com")
        check("reactivate takes effect without a restart", not text(call(url, lapsed_key, "buildroom_status")[1])[1])
        new = next(w for w in members_cli(mf, "new-key", "pilot@example.com").stdout.split() if w.startswith("br_"))
        check("new-key: the old key stops at once, the new one works",
              post(url, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, key)[0] == 401 and not text(call(url, new, "buildroom_status")[1])[1])
        key = new

        # ---- content ----------------------------------------------------------------------
        t, err = text(call(url, key, "buildroom_list_sessions")[1])
        n_skills = len([d for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").exists()])
        check(f"list_sessions: all {n_skills} sessions with descriptions", t.count("\n- buildroom-") == n_skills and "buildroom-continuity:" in t, t[:200])
        t, err = text(call(url, key, "buildroom_start_session", {"skill": "buildroom-search-answer-engine"})[1])
        skill_md = (ROOT / "skills/buildroom-search-answer-engine/SKILL.md").read_text()
        check("start_session: the exact SKILL.md, then its file list", t.startswith(skill_md) and "references/answer-standard.md" in t and "scripts/publish.py" in t)
        check("start_session: says the Business File stays on the member's computer", "Business File on their computer only" in t)
        t, err = text(call(url, key, "buildroom_get_file", {"skill": "buildroom-search-answer-engine", "path": "references/answer-standard.md"})[1])
        check("get_file: a listed reference, byte for byte", t == (ROOT / "skills/buildroom-search-answer-engine/references/answer-standard.md").read_text())
        for bad in ("../../../etc/passwd", "references/../SKILL.md", "/etc/passwd", "references/nope.md", "SKILL.md", "references\\..\\x"):
            check(f"get_file refuses {bad!r}", text(call(url, key, "buildroom_get_file", {"skill": "buildroom-os", "path": bad})[1])[1])
        for bad in ("../skills", "buildroom-os/../x", "nope", "", None):
            check(f"start_session refuses skill {bad!r}", text(call(url, key, "buildroom_start_session", {"skill": bad})[1])[1])
        t, _ = text(call(url, key, "buildroom_whats_new")[1])
        check("whats_new: the newest release first", t.startswith("| `BuildRoom_OS_2026-11-14.zip`"), t[:60])
        check("unknown tool: JSON-RPC -32602", call(url, key, "buildroom_delete_everything")[1]["error"]["code"] == -32602)

        # ---- transport edge cases ---------------------------------------------------------
        import http.client
        def chunked(path, obj, chunks=3):
            body = json.dumps(obj).encode()
            c = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=10)
            step = max(1, len(body) // chunks)
            c.putrequest("POST", path)
            for k, v in (("Content-Type", "application/json"), ("Accept", "application/json, text/event-stream"),
                         ("Authorization", f"Bearer {key}"), ("Transfer-Encoding", "chunked")):
                c.putheader(k, v)
            c.endheaders()
            for i in range(0, len(body), step):
                part = body[i:i + step]
                c.send(f"{len(part):x}\r\n".encode() + part + b"\r\n")
            c.send(b"0\r\n\r\n")
            r = c.getresponse()
            data = r.read()
            c.close()
            return r.status, (json.loads(data) if data else None)
        s, r = chunked("/mcp", {"jsonrpc": "2.0", "id": 9, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        check("chunked request body (no Content-Length) is read: initialize 200", s == 200 and r["result"]["protocolVersion"] == "2025-03-26", (s, r))
        s, r = chunked("/mcp", {"jsonrpc": "2.0", "id": 10, "method": "tools/list"}, chunks=7)
        check("chunked tools/list in seven pieces: 200 with the tools", s == 200 and len(r["result"]["tools"]) == 5, s)
        s, r, h = post(url, {"jsonrpc": "2.0", "id": 11, "method": "tools/list"}, key)
        check("responses ask proxies not to compress or re-chunk them (no-transform, identity)",
              "no-transform" in h.get("Cache-Control", "") and h.get("Content-Encoding") == "identity"
              and h.get("Content-Length") == str(len(json.dumps(r).encode())), dict(h))
        s, r, _ = post(url, {"jsonrpc": "2.0", "id": 5, "result": {}}, key)
        check("a client's JSON-RPC reply (no method): 202, nothing sent back", s == 202 and r is None, s)
        check("GET /mcp: 405", urllib.request.urlopen(urllib.request.Request(base + "/health")).status == 200
              and post(base + "/nowhere", {}, key)[0] == 404)
        try:
            urllib.request.urlopen(url)
            got = 200
        except urllib.error.HTTPError as e:
            got = e.code
        check("GET /mcp answers 405 (no server-sent stream in the pilot)", got == 405, got)
        check("bad JSON: 400", post(url, None, key, raw=b"{nope")[0] == 400)
        check("batch: 400", post(url, [{"jsonrpc": "2.0", "id": 1, "method": "ping"}], key)[0] == 400)

        # ---- logs and secrets ---------------------------------------------------------------
        lines = log.read_text().splitlines()
        check("usage log: one line per tool call, with member, tool, skill, outcome",
              lines and all({"at", "member", "tool", "skill", "outcome"} <= set(json.loads(l)) for l in lines))
        check("usage log never holds an access key", "br_" not in log.read_text())
        httpd.shutdown()

        # ---- hosted mode: the list in a setting, usage to the host's logs ----------------
        exp = members_cli(mf, "export")
        check("members export: one line of JSON with hashes and no keys", exp.returncode == 0 and len(exp.stdout.strip().splitlines()) == 1
              and "br_" not in exp.stdout and json.loads(exp.stdout)["members"])
        import os, io, contextlib
        os.environ["BUILDROOM_MEMBERS_JSON"] = exp.stdout.strip()
        try:
            src_env = server.AllowlistSource(tmp / "does-not-exist.json")
            check("hosted: members read from BUILDROOM_MEMBERS_JSON when set", src_env.check(key)[0] and not src_env.check(old_key)[0])
            app2 = server.App(src_env, server.Content(ROOT / "skills", ROOT / "rollout/releases/README.md"), "stdout")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                app2.handle(key, {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "buildroom_status", "arguments": {}}})
            out = buf.getvalue()
            check("hosted: usage goes to the host's log as one line, never a key", out.startswith("usage {") and "br_" not in out, out)
        finally:
            del os.environ["BUILDROOM_MEMBERS_JSON"]
        rj = json.loads((ROOT.parent / "railway.json").read_text())
        check("railway.json: Dockerfile build, /health check, redeploys on skill changes",
              rj["build"]["builder"] == "DOCKERFILE" and rj["deploy"]["healthcheckPath"] == "/health" and "buildroom/skills/**" in rj["build"]["watchPatterns"])
        df = (CON / "Dockerfile").read_text()
        check("Dockerfile: copies only the connector, the skills and the release notes; runs as a non-root user",
              df.count("COPY ") == 3 and "join.py" in df and "USER connector" in df and "members.json" not in df)
        di = (ROOT.parent / ".dockerignore").read_text()
        check(".dockerignore: everything excluded except what the image needs", di.splitlines()[1] == "*" and "!buildroom/skills/**" in di)

        # ---- sign-up: instant for clear payers, admin approval for the rest ----------------
        import hashlib as _h
        data = tmp / "data"
        env_keep = {k: os.environ.get(k) for k in ("BUILDROOM_DATA_DIR", "BUILDROOM_JOIN_CODE", "BUILDROOM_JOIN_UNTIL", "BUILDROOM_PREAPPROVED", "BUILDROOM_ADMIN_KEY_SHA256")}
        admin_key = "admin-test-key-123"
        os.environ.update({"BUILDROOM_DATA_DIR": str(data), "BUILDROOM_JOIN_CODE": "ROOM-1111",
                           "BUILDROOM_JOIN_UNTIL": (date.today() + timedelta(days=1)).isoformat(),
                           "BUILDROOM_PREAPPROVED": json.dumps([_h.sha256(b"payer@example.com").hexdigest()]),
                           "BUILDROOM_ADMIN_KEY_SHA256": _h.sha256(admin_key.encode()).hexdigest()})
        try:
            app3 = server.build_app(mf, ROOT / "skills", ROOT / "rollout/releases/README.md", log)
            h3 = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(app3))
            threading.Thread(target=h3.serve_forever, daemon=True).start()
            b3 = f"http://127.0.0.1:{h3.server_port}"
            jn = lambda body: post(b3 + "/join", body)
            page = urllib.request.urlopen(b3 + "/join").read().decode()
            check("join page: served, asks for name, email and room code, no outside scripts",
                  "Room code" in page and 'id="email"' in page and "<script src" not in page)
            s, r, _ = jn({"name": "Pat Payer", "email": "  Payer@Example.com ", "code": "room-1111"})
            check("join: a pre-approved email gets a link at once (email and code case-insensitive)", s == 200 and r["state"] == "approved" and r["key"].startswith("br_"), r)
            k1 = r["key"]
            check("join: that link works on the connector", not text(call(b3 + "/mcp", k1, "buildroom_status")[1])[1])
            check("join: signups.json holds a key fingerprint, never the key", k1 not in (data / "signups.json").read_text())
            check("join: the pre-approved list holds no emails, only fingerprints", "payer@example.com" not in os.environ["BUILDROOM_PREAPPROVED"])
            s, r, _ = jn({"name": "Pat Payer", "email": "payer@example.com", "code": "ROOM-1111"})
            check("join again: a new link, and the old one stops", r["state"] == "approved" and r["key"] != k1
                  and post(b3 + "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, k1)[0] == 401)
            s, r, _ = jn({"name": "New Person", "email": "new@example.com", "code": "ROOM-1111"})
            check("join: an unknown email waits for approval, no key", r["state"] == "pending" and "key" not in r, r)
            check("join: waiting again stays pending, one request", jn({"name": "New Person", "email": "new@example.com", "code": "ROOM-1111"})[1]["state"] == "pending"
                  and len(json.loads((data / "signups.json").read_text())["requests"]) == 1)
            check("join: wrong room code refused", jn({"name": "X", "email": "x@example.com", "code": "NOPE"})[1]["state"] == "bad_code")
            check("join: bad email refused", jn({"name": "X", "email": "not-an-email", "code": "ROOM-1111"})[1]["state"] == "bad_email")
            check("join: someone already on the host list is told to use their own link", jn({"name": "Pilot", "email": "pilot@example.com", "code": "ROOM-1111"})[1]["state"] == "already")
            adm = lambda m, body=None: post(b3 + "/admin/api", body or {}, admin_key) if m == "POST" else None
            req = urllib.request.Request(b3 + "/admin/api", headers={"Authorization": "Bearer wrong"})
            try:
                urllib.request.urlopen(req); bad = 200
            except urllib.error.HTTPError as e:
                bad = e.code
            check("admin: a wrong admin key is refused", bad == 401)
            req = urllib.request.Request(b3 + "/admin/api", headers={"Authorization": "Bearer " + admin_key})
            listing = json.loads(urllib.request.urlopen(req).read())
            check("admin: lists the pending request and the signed-up member, never a key fingerprint",
                  [r["email"] for r in listing["requests"]] == ["new@example.com"] and listing["members"][0]["email"] == "payer@example.com"
                  and "key_sha256" not in json.dumps(listing))
            check("admin page: served, asks for the admin key", "Admin key" in urllib.request.urlopen(b3 + "/admin").read().decode())
            check("admin: approve", adm("POST", {"email": "new@example.com", "decision": "approve"})[1].get("ok"))
            s, r, _ = jn({"name": "New Person", "email": "new@example.com", "code": "ROOM-1111"})
            check("join after approval: the link is given", r["state"] == "approved" and r["key"].startswith("br_"), r)
            jn({"name": "Nope", "email": "nope@example.com", "code": "ROOM-1111"})
            adm("POST", {"email": "nope@example.com", "decision": "decline"})
            check("join after decline: told to contact the team, no key", jn({"name": "Nope", "email": "nope@example.com", "code": "ROOM-1111"})[1]["state"] == "declined")
            s, r, _ = adm("POST", {"email": "nope@example.com", "decision": "link"})
            check("admin: approve and get link gives a working link to send", r.get("key") and not text(call(b3 + "/mcp", r["key"], "buildroom_status")[1])[1])
            adm("POST", {"email": "payer@example.com", "decision": "lapse"})
            newest = json.loads((data / "signups.json").read_text())
            check("admin: stop access lapses the member", [m["status"] for m in newest["members"] if m["email"] == "payer@example.com"] == ["lapsed"])
            check("admin: an unknown decision is refused", adm("POST", {"email": "x@example.com", "decision": "delete"})[0] == 400)
            os.environ["BUILDROOM_JOIN_UNTIL"] = (date.today() - timedelta(days=2)).isoformat()
            check("join: closed after the last day", jn({"name": "Late", "email": "late@example.com", "code": "ROOM-1111"})[1]["state"] == "closed")
            del os.environ["BUILDROOM_JOIN_CODE"]
            check("join: closed when no room code is set", jn({"name": "Late", "email": "late@example.com", "code": ""})[1]["state"] == "closed")
            os.environ["BUILDROOM_JOIN_CODE"] = "ROOM-1111"; os.environ["BUILDROOM_JOIN_UNTIL"] = date.today().isoformat()
            for _ in range(40):
                s_last = jn({"name": "Spam", "email": "spam@example.com", "code": "WRONG"})[0]
            check("join: too many tries from one address are slowed down", s_last == 429)
            h3.shutdown()
        finally:
            for k, v in env_keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

        src = (CON / "server.py").read_text()
        check("server: no third-party imports (runs on any Python host)",
              all(m.strip().split(".")[0] in {"argparse", "hashlib", "hmac", "json", "os", "re", "secrets", "sys", "threading", "datetime", "http", "pathlib", "join"}
                  for l in src.splitlines() if l.startswith(("import ", "from "))
                  for m in (l.split()[1:2] if l.startswith("from ") else l.split("#")[0][7:].split(","))))
        check("server: the request log is silenced (paths can carry keys)", "def log_message" in src)
        check("server: membership source is swappable (allowlist now, GoHighLevel later)", "BUILDROOM_MEMBER_SOURCE" in src and "gohighlevel" in src)
        gi = (CON / ".gitignore").read_text()
        check(".gitignore keeps members.json and usage.jsonl out of git", "members.json" in gi and "usage.jsonl" in gi)
        check("no em dashes in the connector", not any("—" in p.read_text() for p in CON.glob("*") if p.is_file()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(RESULTS)
    print(f"\n{passed}/{len(RESULTS)} checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
