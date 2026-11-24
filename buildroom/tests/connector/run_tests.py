#!/usr/bin/env python3
"""Tests for the Build Room connector (pilot MCP server).

Usage:  python3 buildroom/tests/connector/run_tests.py
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, shutil, subprocess, tempfile, threading, urllib.error, urllib.request  # noqa: E402
from datetime import date, datetime, timedelta, timezone  # noqa: E402
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
        check("tools/list: the eight Build Room tools", names == ["buildroom_status", "buildroom_list_sessions", "buildroom_start_session", "buildroom_get_file", "buildroom_whats_new",
                                                                  "buildroom_report", "buildroom_sharing", "buildroom_benchmarks"], names)
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
        check("whats_new: the newest release first", t.startswith("| `BuildRoom_OS_2026-11-21.zip`") and "Autopilot" in t and "Interview me about my business" in t and "BuildRoom_OS_2026-11-19.zip" in t, t[:60])
        check("unknown tool: JSON-RPC -32602", call(url, key, "buildroom_delete_everything")[1]["error"]["code"] == -32602)

        # ---- the flywheel: how sessions end, what the checks catch, and results a member chose to share ----
        import usage as U
        R = lambda **a: text(call(url, key, "buildroom_report", a)[1])  # noqa: E731
        t, bad = R(skill="buildroom-brand-kit", event="finished", step="phase-4", fix=3, look=5, kinds={"colors": 2, "logo": 1})
        last = json.loads(log.read_text().strip().splitlines()[-1])
        check("report: how a session ended is recorded as labels and counts", not bad and "Recorded" in t and last["tool"] == "buildroom_report" and last["outcome"] == "ok"
              and last["event"] == "finished" and last["step"] == "phase-4" and last["fix"] == 3 and last["kinds"] == {"colors": 2, "logo": 1} and "numbers" not in last, last)
        n_before = len(log.read_text().splitlines())
        for name, a in (("free text in a new field", dict(skill="buildroom-brand-kit", event="finished", note="Dana said her price is $1,450")),
                        ("a sentence as the step", dict(skill="buildroom-brand-kit", event="stopped", step="she wants to think about it")),
                        ("a sentence as a kind", dict(skill="buildroom-brand-kit", event="finished", kinds={"Dana Whitfield's logo": 1})),
                        ("text where a count belongs", dict(skill="buildroom-brand-kit", event="finished", fix="three")),
                        ("an unknown session", dict(skill="buildroom-nope", event="finished")),
                        ("an unknown ending", dict(skill="buildroom-brand-kit", event="won a client"))):
            t, bad = R(**a)
            check(f"report refuses {name}, and stores none of it", bad and "Not recorded" in t)
        tail = "\n".join(log.read_text().splitlines()[n_before:])
        check("report: a refused report leaves no trace of what it carried", "Dana" not in tail and "1,450" not in tail and "think about it" not in tail and '"outcome": "refused"' in tail, tail[:300])
        t, bad = R(skill="buildroom-linkedin", event="finished", numbers={"linkedin_calls_booked_week": 2})
        check("report: results are refused until the member has switched sharing on, and the session is told exactly what to say", bad and "has not switched sharing on" in t
              and "only numbers from a fixed list" in t and "Never their words" in t and "five or more members" in t, t)
        t, _ = text(call(url, key, "buildroom_sharing", {"share": "status"})[1])
        check("sharing: off until the member says yes", "Sharing results is OFF" in t)
        check("sharing: a made-up setting is refused", text(call(url, key, "buildroom_sharing", {"share": "always"})[1])[1])
        t, _ = text(call(url, key, "buildroom_sharing", {"share": "on"})[1])
        t2, bad2 = R(skill="buildroom-linkedin", event="finished", numbers={"linkedin_calls_booked_week": 2, "optin_rate_pct": 31.26})
        last = json.loads(log.read_text().strip().splitlines()[-1])
        check("sharing: once on, a result from the list is recorded as a number", "Sharing results is ON" in t and not bad2 and last["numbers"] == {"linkedin_calls_booked_week": 2.0, "optin_rate_pct": 31.3}, last)
        check("report: a result that is not on the list is refused, and so is one out of range", R(skill="buildroom-linkedin", event="finished", numbers={"revenue_dollars": 90000})[1]
              and R(skill="buildroom-linkedin", event="finished", numbers={"optin_rate_pct": 140})[1] and R(skill="buildroom-linkedin", event="finished", numbers={"clients_won_month": "many"})[1])
        t, _ = text(call(url, key, "buildroom_sharing", {"share": "off"})[1])
        check("sharing: switching it off works, and results are refused again", "Sharing results is OFF" in t and R(skill="buildroom-linkedin", event="finished", numbers={"clients_won_month": 1})[1])
        t, bad = text(call(url, key, "buildroom_benchmarks")[1])
        check("benchmarks: with too few members there is nothing to show, and the session is told not to fill the gap", not bad and "nothing to show yet" in t and "at least 5 members" in t
              and "do not fill the gap" in t, t)
        # combined figures, worked out from records
        now = datetime.now(timezone.utc)
        mk = lambda who, days, **nums: {"at": (now - timedelta(days=days)).isoformat(), "member": who, "tool": "buildroom_report", "skill": "buildroom-linkedin", "outcome": "ok", "event": "finished", "numbers": nums}  # noqa: E731
        recs = [mk(f"m{i}@example.com", 3, calls_booked_month=v, close_rate_pct=20 + i) for i, v in enumerate((2, 4, 6, 8, 30))]
        recs += [mk("m0@example.com", 1, calls_booked_month=3), mk("old@example.com", 200, calls_booked_month=99), mk("off@example.com", 2, calls_booked_month=50),
                 mk("solo@example.com", 2, show_rate_pct=80)]
        on = {f"m{i}@example.com": {"on": True} for i in range(5)}
        on.update({"old@example.com": {"on": True}, "off@example.com": {"on": False}, "solo@example.com": {"on": True}})
        bm = {b["metric"]: b for b in U.benchmarks(recs, on, now)}
        check("benchmarks: the middle member's figure, from each member's latest number only", bm["calls_booked_month"]["members"] == 5 and bm["calls_booked_month"]["middle"] == 6
              and bm["calls_booked_month"]["from"] == 4 and bm["calls_booked_month"]["to"] == 8, bm.get("calls_booked_month"))
        check("benchmarks: a result with fewer than five members behind it is never shown to members", "show_rate_pct" not in bm and "close_rate_pct" in bm)
        check("benchmarks: a member who switched sharing off, and a number too old to count, are left out", 50 not in U.shared_results(recs, on, now)["calls_booked_month"]
              and 99 not in U.shared_results(recs, on, now)["calls_booked_month"])
        on4 = dict(on); on4["m4@example.com"] = {"on": False}
        check("benchmarks: when a member switches off and the group falls under five, the figure disappears", "calls_booked_month" not in {b["metric"] for b in U.benchmarks(recs, on4, now)})
        sk = [{"skill": "buildroom-linkedin"}, {"skill": "buildroom-brand-kit"}]
        ev = lambda tool, skill, days=1, **x: {"at": (now - timedelta(days=days)).isoformat(), "member": "a@example.com", "tool": tool, "skill": skill, "outcome": "ok", **x}  # noqa: E731
        ins = U.insights([ev("buildroom_start_session", "buildroom-brand-kit") for _ in range(4)]
                         + [ev("buildroom_report", "buildroom-brand-kit", event="stopped", step="phase-2", fix=4, kinds={"logo": 3, "colors": 1}),
                            ev("buildroom_report", "buildroom-brand-kit", event="stopped", step="phase-2", fix=2, kinds={"logo": 2}),
                            ev("buildroom_report", "buildroom-brand-kit", event="finished", step="phase-4", fix=0)] + recs, on, sk, now)
        bk = next(x for x in ins["tools"] if x["skill"] == "buildroom-brand-kit")
        check("insights: the host sees where sessions stop and what the checks keep catching", bk["starts"] == 4 and bk["finished"] == 1 and bk["stopped"] == 2 and bk["stopped_at"][0] == ("phase-2", 2)
              and bk["finish_rate"] == 0.25 and bk["fixes_per_report"] == 2.0 and ins["caught"][0] == {"skill": "buildroom-brand-kit", "kind": "logo", "count": 5}, (bk, ins["caught"][:2]))
        solo = next(x for x in ins["shared"] if x["metric"] == "show_rate_pct")
        check("insights: the host sees every shared result with how many members are behind it, marked when members cannot see it", solo["members"] == 1 and solo["shown_to_members"] is False
              and next(x for x in ins["shared"] if x["metric"] == "calls_booked_month")["shown_to_members"] is True and ins["sharing_on"] == 7)
        check("the list of results holds numbers only: rates, counts, nothing about money or people", all(isinstance(v[0], int) and isinstance(v[1], int) for v in U.METRICS.values())
              and not any(w in k for k in U.METRICS for w in ("revenue", "dollar", "price", "name", "email")))
        inst = server.INSTRUCTIONS
        check("instructions: the first 512 characters still stand on their own, and reporting is labels and numbers only", "buildroom_start_session" in inst[:512]
              and "buildroom_report once" in inst and "never a word the member wrote" in inst and "only if the member has said yes" in inst)
        t, _ = text(call(url, key, "buildroom_start_session", {"skill": "buildroom-os"})[1])
        check("start_session: every session is told to report how it ended", "call buildroom_report once (labels and numbers only)" in t)
        sp = (ROOT / "connector/start.html").read_text()
        dh = (ROOT / "connector/dashboard.html").read_text()
        check("start page: members are told what is recorded, what never is, and how to switch sharing off", "What Build Room OS records, and what it never does" in sp
              and "Stop sharing my results" in sp and "five or more members" in sp and "not a forecast" in sp and "\u2014" not in sp)
        check("dashboard: where sessions stop, what the checks catch, and shared results", all(x in dh for x in ("Where sessions stop", "What the checks keep catching", "Results members chose to share", "not a forecast")))

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
        check("chunked tools/list in seven pieces: 200 with the tools", s == 200 and len(r["result"]["tools"]) == 8, s)
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
        # a member who opens their link in a browser gets instructions, and the key is not echoed
        page = urllib.request.urlopen(urllib.request.Request(base + "/mcp/" + key, headers={"Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}))
        html = page.read().decode()
        check("a link opened in a browser shows how to add it to Claude", page.status == 200 and "goes into Claude, not your browser" in html
              and "Add custom connector" in html and "No sign in" in html, html[:200])
        check("that page never echoes the key and is not cached", key not in html and page.headers.get("Cache-Control") == "no-store"
              and page.headers.get("Referrer-Policy") == "no-referrer")
        page = urllib.request.urlopen(urllib.request.Request(base + "/mcp/not-a-real-key", headers={"Accept": "text/html"}))
        check("the page is the same for any key, so it reveals nothing about who is a member", page.read().decode() == html)
        try:
            urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "text/event-stream"}))
            got = 200
        except urllib.error.HTTPError as e:
            got = e.code
        check("an MCP client asking for a stream still gets 405", got == 405, got)
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
              df.count("COPY ") == 3 and "join.py" in df and "guide.html" in df and "start.html" in df and "usage.py" in df and "dashboard.html" in df and all(f"example-{n}.html" in df for n in ("review", "build", "onepage", "offer-page", "sales-script", "referrals")) and "USER connector" in df and "members.json" not in df)
        di = (ROOT.parent / ".dockerignore").read_text()
        check(".dockerignore: everything excluded except what the image needs", di.splitlines()[1] == "*" and "!buildroom/skills/**" in di and "!buildroom/connector/guide.html" in di)

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
            # ---- the public Quick Start Guide ---------------------------------------------------
            import re as _re
            gp = urllib.request.urlopen(b3 + "/guide")
            guide = gp.read().decode()
            check("guide: served at /guide and at the bare address", gp.status == 200 and "Quick Start Guide" in guide
                  and urllib.request.urlopen(b3 + "/").read().decode() == guide)
            slugs = set(_re.findall(r'^ \["[a-z]+","([a-z-]+)",', guide, _re.M))
            on_disk = {d.name[len("buildroom-"):] for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").exists()}
            check("guide: lists every tool in the release, and nothing that is not in it", slugs == on_disk,
                  f"missing {sorted(on_disk - slugs)}, extra {sorted(slugs - on_disk)}")
            check("guide: has the Export as PDF button and a print layout", 'id="pdf"' in guide and "window.print()" in guide and "@media print" in guide)
            check("guide: more commands for the book, speaking, blueprint and design tools",
                  all(c in guide for c in ("Write the next chapter", "Find me places to speak", "Make my org chart", "Set up my taste vault")))
            check("guide: self-contained (no outside scripts, styles, fonts or images)",
                  not _re.search(r'(src|href)="(https?:)?//', guide) and "@import" not in guide and not _re.search(r"url\(\s*['\"]?(https?:|//|data:)", guide))
            # ---- the Start Here page and its setup video ------------------------------------
            sp = urllib.request.urlopen(b3 + "/start").read().decode()
            # ---- the finished example ------------------------------------------------------------
            ex = {}
            for n in ("review", "build", "onepage", "offer-page", "sales-script", "referrals"):
                r = urllib.request.urlopen(b3 + "/example/" + n)
                ex[n] = r.read().decode()
            check("example: every page is served and says plainly that the business is made up", all("everyone named here are made up" in h and 'href="/guide#example"' in h for h in ex.values()))
            check("example: self-contained, and its links stay on the site", all(not _re.search(r'(src|href)="https?:', h) and "@import" not in h for h in ex.values())
                  and all(l.startswith("/example/") or l == "/guide#example" for h in ex.values() for l in _re.findall(r'href="([^"#][^"]*)"', h)), [l for h in ex.values() for l in _re.findall(r'href="([^"#][^"]*)"', h)][:8])
            check("example: the build page links to the review page and the three drafts", all(f'href="/example/{n}"' in ex["build"] for n in ("review", "offer-page", "sales-script", "referrals")))
            check("example: the review page tags its lines and the drafts show their blanks", "Drafted, approved by you" in ex["review"] and "From your files" in ex["review"] and "Needs you:" in ex["offer-page"])
            check("example: the one page shows her words and three drafted ways to say it", "in your own words." in ex["onepage"] and ex["onepage"].count("Drafted for you") == 3)
            check("example: no key, room code or real address, and no promise of results", not any(_re.search(r"BUILD-\d|br_[A-Za-z0-9]{8}|/mcp/|@gmail|@aimomentum", h) for h in ex.values())
                  and not any(_re.search(r"guaranteed results|you will (get|make|earn)", h, _re.I) for h in ex.values()))
            try:
                urllib.request.urlopen(b3 + "/example/../server.py"); bad = True
            except urllib.error.HTTPError:
                bad = False
            try:
                urllib.request.urlopen(b3 + "/example/secret"); bad2 = True
            except urllib.error.HTTPError:
                bad2 = False
            check("example: only the listed pages are served", not bad and not bad2)
            check("guide: shows a finished example before asking for anything", 'id="example"' in guide and "See what you get" in guide and guide.count('href="/example/') == 6
                  and "An example shows the work, not a result" in guide)
            check("guide: has a clear call to action to the Start Here page", guide.count('href="/start"') >= 2 and "Brand new?" in guide)
            check("start: served, with the first sentence and all three ways to connect",
                  "I'm new here. Help me get started." in sp and "Add custom connector" in sp
                  and "claude mcp add --transport http buildroom" in sp and 'codex mcp add buildroom --url' in sp and "Streamable HTTP" in sp)
            check("start: explains the Business File and links back to the guide and the join page",
                  "BUILDROOM_BUSINESS_FILE.md" in sp and 'href="/guide"' in sp and 'href="/join"' in sp)
            check("start: tells existing members to run Autopilot, with research as an optional first step",
                  'id="autopilot"' in sp and ">Run autopilot<" in sp and ">Research my business first<" in sp and "Optional, about 15 minutes." in sp
                  and "Nothing is published, sent or paid for." in sp and "does not run in a regular chat" in sp and 'href="#autopilot"' in sp)
            check("start: no video block until a video is uploaded", "<video" not in sp)
            check("start: self-contained, no room code or key, no long dashes",
                  not _re.search(r'(src|href)="(https?:)?//', sp) and not _re.search(r"BUILD-\d|ROOM-\d|br_[A-Za-z0-9]", sp)
                  and "\u2014" not in sp and "\u2013" not in sp)
            def put(name, body, k=None):
                rq = urllib.request.Request(b3 + "/admin/media/" + name, data=body, method="PUT")
                if k:
                    rq.add_header("Authorization", "Bearer " + k)
                try:
                    return urllib.request.urlopen(rq).status
                except urllib.error.HTTPError as e:
                    return e.code
            clip = bytes(range(256)) * 40
            check("media: upload refused without the admin key", put("setup.mp4", clip) == 401 and put("setup.mp4", clip, "wrong") == 401)
            check("media: only the two known file names are accepted", put("../signups.json", clip, admin_key) == 400 and put("x.mp4", clip, admin_key) == 400)
            check("media: the owner can upload the video", put("setup.mp4", clip, admin_key) == 200 and (data / "media" / "setup.mp4").read_bytes() == clip)
            mr = urllib.request.urlopen(b3 + "/media/setup.mp4")
            check("media: served whole with its type and Accept-Ranges", mr.read() == clip and mr.headers["Content-Type"] == "video/mp4" and mr.headers["Accept-Ranges"] == "bytes")
            rq = urllib.request.Request(b3 + "/media/setup.mp4", headers={"Range": "bytes=100-199"})
            mr = urllib.request.urlopen(rq)
            check("media: a byte range gets 206 and exactly those bytes", mr.status == 206 and mr.read() == clip[100:200] and mr.headers["Content-Range"] == f"bytes 100-199/{len(clip)}")
            mr = urllib.request.urlopen(urllib.request.Request(b3 + "/media/setup.mp4", headers={"Range": "bytes=-10"}))
            check("media: a suffix range gets the last bytes", mr.status == 206 and mr.read() == clip[-10:])
            def code(u, h=None):
                try:
                    return urllib.request.urlopen(urllib.request.Request(b3 + u, headers=h or {})).status
                except urllib.error.HTTPError as e:
                    return e.code
            check("media: a range past the end gets 416; other files are not served", code("/media/setup.mp4", {"Range": "bytes=999999-"}) == 416
                  and code("/media/signups.json") == 404 and code("/media/setup.jpg") == 404)
            check("start: the video block appears once the video is there", "<video" in urllib.request.urlopen(b3 + "/start").read().decode())
            # ---- the host dashboard ---------------------------------------------------------------
            import usage as _u
            from datetime import datetime as _dt, timezone as _tz, timedelta as _td
            now = _dt(2026, 11, 21, 12, 0, tzinfo=_tz.utc)
            L = lambda days, who, tool="buildroom_start_session", skill="buildroom-os", outcome="ok": {  # noqa: E731
                "at": (now - _td(days=days)).isoformat(), "member": who, "tool": tool, "skill": skill, "outcome": outcome}
            recs = [L(1, "a@x.com"), L(2, "a@x.com", skill="buildroom-autopilot"), L(2, "a@x.com", skill="buildroom-autopilot"),
                    L(10, "q@x.com"), L(40, "g@x.com"), L(3, "c@x.com", "buildroom_status", None), L(3, "c@x.com", "buildroom_list_sessions", None),
                    L(1, "h@x.com"), L(1, "s@x.com"), L(1, "bad@x.com", outcome="unknown")]
            mem = [{"email": e, "name": e[0].upper(), "status": "active", "added": "2026-11-01", "via": "instant"} for e in ("a@x.com", "q@x.com", "g@x.com", "c@x.com", "n@x.com")]
            mem.append({"email": "s@x.com", "name": "S", "status": "lapsed", "added": "2026-11-01", "via": "instant"})
            sk = [{"skill": "buildroom-os", "description": ""}, {"skill": "buildroom-autopilot", "description": ""}, {"skill": "buildroom-compass", "description": ""}]
            su = _u.summarize(recs, mem, sk, now)
            st = {m["email"]: m["state"] for m in su["members"]}
            check("dashboard: each member lands in the right state", st == {"a@x.com": "active", "q@x.com": "quiet", "g@x.com": "gone_quiet",
                  "c@x.com": "connected_not_started", "n@x.com": "not_connected", "s@x.com": "stopped", "h@x.com": "active"}, st)
            check("dashboard: people to check in on come first, longest wait first", [m["email"] for m in su["members"]][:3] == ["c@x.com", "g@x.com", "q@x.com"])
            ma = next(m for m in su["members"] if m["email"] == "a@x.com")
            check("dashboard: sessions, tools tried and the most used tool are counted", ma["sessions"] == 3 and ma["tools_used"] == 2 and ma["top_tool"] == "buildroom-autopilot" and ma["days_since_session"] == 1)
            check("dashboard: someone on the host list shows up from their activity alone", next(m for m in su["members"] if m["email"] == "h@x.com")["via"] == "host list")
            check("dashboard: a refused call never counts as activity", "bad@x.com" not in st and su["refused_30"] == 1)
            tl = {x["skill"]: x for x in su["tools"]}
            check("dashboard: tools ranked by sessions, unused tools listed with none", su["tools"][0]["skill"] == "buildroom-os" and tl["buildroom-os"]["starts"] == 5
                  and tl["buildroom-os"]["starts_30"] == 4 and tl["buildroom-autopilot"]["members"] == 1 and tl["buildroom-compass"]["starts"] == 0 and tl["buildroom-compass"]["last"] is None)
            check("dashboard: thirty days of activity, and it says when counting began", len(su["daily"]) == 30 and su["daily"][-2]["members"] == 3 and su["tracking_since"].startswith("2026-10-12"))
            dg = _u.digest(su, 2)
            dt = dg["text"]
            check("digest: the week in numbers, counting only sessions started", "2 of 6 members ran at least one session (4 sessions in all)" in dt and "2 sign-up request(s) waiting" in dt, dt[:500])
            check("digest: each group to check in on is named, with a note to send", "CONNECTED BUT NEVER RAN A SESSION: 1" in dt and "C <c@x.com>, connected 3 day(s) ago" in dt
                  and "GONE QUIET (no session in over 21 days): 1" in dt and "G <g@x.com>, last session 40 days ago" in dt and "HAVE A LINK, NEVER CONNECTED: 1" in dt and dt.count("A note you could send:") == 4)
            check("digest: first sessions are called out, stopped members are not chased", "WORTH A CONGRATULATIONS" in dt and "<h@x.com>" in dt.split("WORTH A CONGRATULATIONS")[1] and "s@x.com" not in dt.split("WORTH A CONGRATULATIONS")[0])
            check("digest: the subject line carries the two numbers that matter", dg["subject"] == "Build Room OS weekly: 2 active, 2 to check in on")
            check("digest: says what it counts, promises nothing, no long dashes", "counts sessions started, not results" in dt and "\u2014" not in dt and "\u2013" not in dt)
            check("digest: with nothing recorded it says so", "No activity has been recorded yet" in _u.digest(_u.summarize([], mem, sk, now))["text"])
            check("dashboard: no activity at all is handled", _u.summarize([], mem, sk, now)["tracking_since"] is None and _u.summarize([], [], [], now)["members"] == [])
            (data / "usage.jsonl").write_text("not json\n" + json.dumps(recs[0]) + "\n{\"at\": 1}\n")
            check("dashboard: damaged lines in the stored log are skipped", len(_u.read(str(data))) == 1 and _u.read(None) == [])
            (data / "usage.jsonl").unlink()
            check("guide: holds no room code, access key or member link", not _re.search(r"BUILD-\d|ROOM-\d|br_[A-Za-z0-9]|/mcp/", guide))
            check("guide: no dashes that read as AI, and no promise of results",
                  "\u2014" not in guide and "\u2013" not in guide and not _re.search(r"guarantee[ds]? (results|leads|revenue|clients)", guide, _re.I))
            s, r, _ = jn({"name": "Pat Payer", "email": "  Payer@Example.com ", "code": "room-1111"})
            check("join: a pre-approved email gets a link at once (email and code case-insensitive)", s == 200 and r["state"] == "approved" and r["key"].startswith("br_"), r)
            k1 = r["key"]
            check("join: that link works on the connector", not text(call(b3 + "/mcp", k1, "buildroom_status")[1])[1])
            check("join: signups.json holds a key fingerprint, never the key", k1 not in (data / "signups.json").read_text())
            check("join: the pre-approved list holds no emails, only fingerprints", "payer@example.com" not in os.environ["BUILDROOM_PREAPPROVED"])
            s, r, _ = jn({"name": "Pat Payer", "email": "payer@example.com", "code": "ROOM-1111"})
            check("join again: a returning member is asked first; no new link, and the old one keeps working",
                  r["state"] == "have_link" and "key" not in r and "switch your old one off" in r["message"]
                  and post(b3 + "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, k1)[0] == 200, r)
            check("join again: 'replace' must be exactly true", jn({"name": "Pat Payer", "email": "payer@example.com", "code": "ROOM-1111",
                                                                   "replace": "yes"})[1]["state"] == "have_link")
            s, r, _ = jn({"name": "Pat Payer", "email": "payer@example.com", "code": "ROOM-1111", "replace": True})
            check("join again, asking for a new link: a new one, and the old one stops", r["state"] == "approved" and r["key"] != k1
                  and "old one no longer works" in r["message"]
                  and post(b3 + "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, k1)[0] == 401, r)
            check("join page: offers a new link only behind a button", "Give me a new link" in page and "replace:replace===true" in page)
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
            def ucode(k=None):
                rq = urllib.request.Request(b3 + "/admin/usage", headers={"Authorization": "Bearer " + k} if k else {})
                try:
                    r = urllib.request.urlopen(rq)
                    return r.status, json.loads(r.read())
                except urllib.error.HTTPError as e:
                    return e.code, None
            check("dashboard: the numbers need the admin key", ucode()[0] == 401 and ucode("wrong")[0] == 401)
            def dcode(k=None):
                rq = urllib.request.Request(b3 + "/admin/digest", headers={"Authorization": "Bearer " + k} if k else {})
                try:
                    r = urllib.request.urlopen(rq)
                    return r.status, json.loads(r.read())
                except urllib.error.HTTPError as e:
                    return e.code, None
            check("digest: needs the admin key, and comes back as a subject and plain text", dcode()[0] == 401 and dcode(admin_key)[0] == 200
                  and set(dcode(admin_key)[1]) == {"subject", "text"} and "THE WEEK IN NUMBERS" in dcode(admin_key)[1]["text"])
            dkey = post(b3 + "/admin/api", {"email": "dash@example.com", "decision": "link"}, admin_key)[1].get("key")
            call(b3 + "/mcp", dkey, "buildroom_status")
            call(b3 + "/mcp", dkey, "buildroom_start_session", {"skill": "buildroom-os"})
            s, du = ucode(admin_key)
            me = next((m for m in (du or {}).get("members", []) if m["email"] == "dash@example.com"), {})
            check("dashboard: a member's real session shows up for the host", s == 200 and me.get("state") == "active" and me.get("sessions") == 1 and me.get("top_tool") == "buildroom-os", me)
            stored = (data / "usage.jsonl").read_text()
            check("dashboard: the stored log holds the member, tool and outcome, and never a key", "dash@example.com" in stored and "buildroom_start_session" in stored and "br_" not in stored)
            dp = urllib.request.urlopen(b3 + "/admin/dashboard")
            dh = dp.read().decode()
            check("dashboard: the page is served, asks for the admin key, and holds no member data itself", dp.status == 200 and 'id="k" type="password"' in dh
                  and "dash@example.com" not in dh and "noindex" in dh and not _re.search(r'(src|href)="(https?:)?//', dh))
            check("dashboard: says what is and is not recorded", "Nothing a member types and nothing from their Business File is ever stored here." in dh)
            check("dashboard: linked from the approvals page", 'href="/admin/dashboard"' in urllib.request.urlopen(b3 + "/admin").read().decode())
            check("dashboard: the week in words is one press away", 'id="dg"' in dh and "/admin/digest" in dh)
            check("dashboard: no long dashes", "\u2014" not in dh and "\u2013" not in dh)
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
            s, r, _ = jn({"name": "Pat Payer", "email": "payer@example.com", "code": "ROOM-1111", "replace": True})
            check("join: access the team stopped does not come back by signing up again, even when pre-approved",
                  r["state"] == "declined" and "key" not in r, r)
            s, r, _ = jn({"name": "New Person", "email": "new@example.com", "code": "ROOM-1111"})
            check("join: an approved member who comes back is asked first too", r["state"] == "have_link" and "key" not in r, r)
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
        check("usage: standard library only", all(l.split()[1].split(".")[0] in {"json", "re", "datetime", "pathlib"}
              for l in (CON / "usage.py").read_text().splitlines() if l.startswith(("import ", "from "))))
        check("server: no third-party imports (runs on any Python host)",
              all(m.strip().split(".")[0] in {"argparse", "hashlib", "hmac", "json", "os", "re", "secrets", "sys", "threading", "datetime", "http", "pathlib", "join", "usage"}
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
