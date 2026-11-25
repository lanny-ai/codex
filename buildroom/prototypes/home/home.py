#!/usr/bin/env python3
"""Build Room Home (prototype): a home screen on the member's own computer that a Claude Code or Codex session listens to.

  home.py open  [--business-file FILE] [--timeout 100]   start the page if it is not running, open it in the browser,
                                                         then wait for the member to tap something
  home.py wait  [--timeout 100]                          wait again (the page is already open)
  home.py form  FORM.json [--timeout 100]                show a short form on the page and wait for the answers
  home.py say   "Brand Kit is running. Come back here when it is done."     put one line of status on the page
  home.py stop                                           close the page's server

Each waiting command prints one line of JSON and exits:
  {"event": "pick", "tool": "brand-kit", "say": "Set up my brand kit"}      the member tapped a tool
  {"event": "form", "id": "...", "answers": {...}}                           the member sent a form
  {"event": "none"}                                                          nothing yet: run `home.py wait` again
A wait is kept under two minutes on purpose, so it fits inside the time limit a session gives one command. The session
simply waits again; taps are queued by the page's server, so none is lost between waits.

The page is served from this computer to this computer only (127.0.0.1), on a random port, behind a random token.
Nothing goes online. It reads the Business File only to show which sections are done; it never changes it.
Do not use a form for a password or an API key: answers are printed into the session. Standard library only.
"""
import argparse, http.server, json, os, re, secrets, subprocess, sys, threading, time, urllib.error, urllib.request, webbrowser
from pathlib import Path

STATE = Path(".buildroom") / "home.json"
IDLE_HOURS = 8
# The prototype's tools: (slug, name, what the member says, Business File section, one line)
TOOLS = [
    ("os", "What next?", "What should I work on next?", None, "Your one next step"),
    ("ideal-client-avatar", "Ideal Client", "Help me build my ideal client avatar", 2, "Who you serve, in their words"),
    ("signature-offer", "Signature Offer", "Help me build my signature offer", 3, "What you sell and why it is worth it"),
    ("brand-kit", "Brand Kit", "Set up my brand kit", 22, "Your logo, colors and typefaces"),
    ("linkedin", "LinkedIn", "Write today's LinkedIn post", 14, "Today's post, ready to copy"),
    ("funnel-scorecard", "Funnel Scorecard", "Where is my funnel leaking?", None, "Where leads are being lost"),
]


def statuses(business_file):
    """{section number: status} from the Business File's own Status lines. Read-only."""
    out = {}
    try:
        text = Path(business_file).read_text(encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return out
    for m in re.finditer(r"^## (\d+)\. [^\n]*\n(?:[^\n]*\n){0,3}?\*\*Status:\*\* *([a-z ]+?) *(?:·|$)", text, re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Room</title><style>
:root{--navy:#0b1020;--ink:#0f1424;--mute:#5b6478;--line:#e2e6ef;--panel:#f5f6fa;--gold:#ffb547;--paper:#fff;--ok:#0f7a4d}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.5 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
header{background:var(--navy);color:#fff;padding:22px clamp(16px,5vw,48px)}
header h1{margin:0;font-size:24px;letter-spacing:-.01em}header p{margin:4px 0 0;color:#c9d0e0;font-size:16px}
main{max-width:980px;margin:0 auto;padding:28px clamp(16px,5vw,48px) 64px}
#status{border-left:5px solid var(--gold);background:var(--panel);padding:14px 18px;margin:0 0 28px;font-weight:600}
#status[hidden]{display:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:22px 16px}
.tool{appearance:none;border:0;background:none;padding:0;font:inherit;color:inherit;cursor:pointer;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px}
.tool .ic{width:104px;height:104px;border-radius:24px;background:var(--navy);color:#fff;display:grid;place-items:center;font-weight:800;font-size:34px;letter-spacing:-.02em;position:relative}
.tool:hover .ic,.tool:focus-visible .ic{outline:4px solid var(--gold);outline-offset:3px}
.tool .ic i{position:absolute;right:-6px;top:-6px;min-width:30px;height:30px;border-radius:15px;background:var(--ok);color:#fff;font:700 16px/30px system-ui;font-style:normal;border:3px solid #fff}
.tool b{font-size:18px;line-height:1.2}.tool span{font-size:15px;color:var(--mute);line-height:1.3}
.tool.sent .ic{background:var(--gold);color:var(--navy)}
h2{font-size:22px;margin:0 0 6px}p.sub{margin:0 0 22px;color:var(--mute)}
form label{display:block;font-weight:700;margin:20px 0 6px}form small{display:block;font-weight:400;color:var(--mute);margin-top:2px}
form input,form textarea,form select{width:100%;font:inherit;padding:14px;border:2px solid var(--line);border-radius:10px;color:var(--ink);background:#fff}
form textarea{min-height:110px}form input:focus,form textarea:focus,form select:focus{outline:3px solid var(--gold);border-color:var(--navy)}
.btn{margin-top:26px;background:var(--navy);color:#fff;border:0;border-radius:10px;padding:16px 28px;font:700 18px/1 system-ui;cursor:pointer;min-height:52px}
.btn.ghost{background:none;color:var(--navy);text-decoration:underline;padding:16px 12px}
#lost{background:#fdecea;border-left:5px solid #b3261e;padding:14px 18px;margin:0 0 28px}#lost[hidden]{display:none}
footer{max-width:980px;margin:0 auto;padding:0 clamp(16px,5vw,48px) 40px;color:var(--mute);font-size:15px}
</style></head><body>
<header><h1>Build Room</h1><p id="hello">Tap what you want to work on. Claude picks it up from here.</p></header>
<main>
  <div id="lost" hidden>This page has lost touch with your session. Go back to Claude or Codex and say <b>open my Build Room home</b>.</div>
  <div id="status" hidden></div>
  <section id="home"><div class="grid" id="grid"></div></section>
  <section id="formbox" hidden><h2 id="ftitle"></h2><p class="sub" id="fintro"></p><form id="f"></form></section>
</main>
<footer>This page runs on your own computer. Nothing on it is sent anywhere except to your own Claude or Codex session.</footer>
<script>
const T = new URLSearchParams(location.search).get("t");
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let shownForm = null, version = -1;
async function send(body) {
  const r = await fetch("/event?t=" + T, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  if (!r.ok) throw new Error("not sent");
}
function initials(n) { return n.replace(/[^A-Za-z? ]/g, "").split(" ").filter(Boolean).slice(0, 2).map(w => w[0]).join("").toUpperCase(); }
function draw(s) {
  $("status").hidden = !s.status; $("status").textContent = s.status || "";
  if (s.form) {
    if (shownForm !== s.form.id) {
      shownForm = s.form.id;
      $("ftitle").textContent = s.form.title || "A few questions"; $("fintro").textContent = s.form.intro || "";
      $("f").innerHTML = (s.form.fields || []).map(q => `<label for="q_${esc(q.id)}">${esc(q.label)}${q.hint ? `<small>${esc(q.hint)}</small>` : ""}</label>` +
        (q.type === "long" ? `<textarea id="q_${esc(q.id)}" name="${esc(q.id)}"></textarea>`
          : q.type === "choice" ? `<select id="q_${esc(q.id)}" name="${esc(q.id)}"><option value=""></option>${(q.options || []).map(o => `<option>${esc(o)}</option>`).join("")}</select>`
          : `<input id="q_${esc(q.id)}" name="${esc(q.id)}" type="text" autocomplete="off">`)).join("") +
        `<button class="btn" type="submit">Send to Claude</button><button class="btn ghost" type="button" id="skip">I would rather answer in the chat</button>`;
      $("skip").onclick = () => send({event: "form", id: s.form.id, skipped: true});
    }
    $("home").hidden = true; $("formbox").hidden = false;
  } else {
    shownForm = null; $("formbox").hidden = true; $("home").hidden = false;
    $("grid").innerHTML = s.tools.map(t => `<button class="tool" data-tool="${esc(t.slug)}" aria-label="${esc(t.name)}: ${esc(t.line)}${t.done ? ", done" : ""}">
      <span class="ic">${esc(initials(t.name))}${t.done ? '<i aria-hidden="true">✓</i>' : ""}</span><b>${esc(t.name)}</b><span>${esc(t.line)}</span></button>`).join("");
  }
}
$("grid").addEventListener("click", async e => {
  const b = e.target.closest("[data-tool]"); if (!b) return;
  try { await send({event: "pick", tool: b.dataset.tool}); b.classList.add("sent");
        $("status").hidden = false; $("status").textContent = "Sent. Go back to Claude or Codex: it is starting " + b.querySelector("b").textContent + "."; }
  catch { $("lost").hidden = false; }
});
$("f").addEventListener("submit", async e => {
  e.preventDefault();
  const answers = {}; new FormData($("f")).forEach((v, k) => { if (String(v).trim()) answers[k] = String(v).trim(); });
  try { await send({event: "form", id: shownForm, answers}); } catch { $("lost").hidden = false; }
});
async function poll() {
  try { const r = await fetch("/state?t=" + T + "&v=" + version); if (!r.ok) throw 0; const s = await r.json(); $("lost").hidden = true;
        if (s.version !== version) { version = s.version; draw(s); } }
  catch { $("lost").hidden = false; }
  setTimeout(poll, 1500);
}
poll();
</script></body></html>"""


# ---------------------------------------------------------------- the page's server
class Home:
    def __init__(self, token, business_file):
        self.token, self.business_file = token, business_file
        self.events, self.cv = [], threading.Condition()
        self.status, self.form, self.version = "", None, 0
        self.touched = time.time()

    def state(self):
        st = statuses(self.business_file)
        tools = [{"slug": s, "name": n, "line": line, "done": (st.get(sec) == "complete") if sec else False} for s, n, _say, sec, line in TOOLS]
        return {"version": self.version, "status": self.status, "form": self.form, "tools": tools}

    def bump(self):
        self.version += 1
        self.touched = time.time()


def handler(home):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body=b"", ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def _ok(self):
            """Only this computer, only with the token, only when the page itself is asking."""
            host = (self.headers.get("Host") or "").split(":")[0]
            q = dict(p.split("=", 1) for p in self.path.split("?", 1)[1].split("&") if "=" in p) if "?" in self.path else {}
            origin = self.headers.get("Origin")
            port = self.server.server_address[1]
            return (host in ("127.0.0.1", "localhost") and secrets.compare_digest(q.get("t", ""), home.token)
                    and origin in (None, f"http://127.0.0.1:{port}", f"http://localhost:{port}")), q

        def _json(self):
            try:
                n = int(self.headers.get("Content-Length") or 0)
                return json.loads(self.rfile.read(n) or b"{}") if 0 <= n <= 200_000 else None
            except ValueError:
                return None

        def do_GET(self):
            ok, q = self._ok()
            route = self.path.split("?")[0]
            if not ok:
                return self._send(403, b'{"error":"not allowed"}')
            if route == "/":
                return self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            if route == "/state":
                return self._send(200, json.dumps(home.state()).encode())
            if route == "/next":                                  # the session's wait: returns the oldest tap, or nothing after the timeout
                wait = max(0.0, min(110.0, float(q.get("wait", "100"))))
                with home.cv:
                    if not home.events:
                        home.cv.wait(wait)
                    ev = home.events.pop(0) if home.events else {"event": "none"}
                home.touched = time.time()
                return self._send(200, json.dumps(ev).encode())
            self._send(404, b'{"error":"not found"}')

        def do_POST(self):
            ok, _q = self._ok()
            route = self.path.split("?")[0]
            body = self._json()
            if not ok or body is None or not isinstance(body, dict):
                return self._send(403, b'{"error":"not allowed"}')
            if route == "/event":                                  # from the page: a tap or a sent form
                if body.get("event") == "pick":
                    tool = next((t for t in TOOLS if t[0] == body.get("tool")), None)
                    if not tool:
                        return self._send(400, b'{"error":"unknown tool"}')
                    ev = {"event": "pick", "tool": tool[0], "say": tool[2]}
                elif body.get("event") == "form" and home.form and body.get("id") == home.form["id"]:
                    allowed = {f["id"] for f in home.form["fields"]}
                    ans = {k: str(v)[:4000] for k, v in (body.get("answers") or {}).items() if k in allowed}
                    ev = {"event": "form", "id": home.form["id"], **({"skipped": True} if body.get("skipped") else {"answers": ans})}
                    home.form = None
                    home.status = "Sent. Go back to Claude or Codex."
                else:
                    return self._send(400, b'{"error":"not understood"}')
                with home.cv:
                    home.events.append(ev)
                    home.bump()
                    home.cv.notify_all()
                return self._send(200, b'{"ok":true}')
            if route == "/control":                                # from the session: a status line, a form, or stop
                if "status" in body:
                    home.status = str(body["status"])[:300]
                if "form" in body:
                    home.form = body["form"]
                    home.status = ""
                home.bump()
                if body.get("stop"):
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                return self._send(200, b'{"ok":true}')
            self._send(404, b'{"error":"not found"}')
    return H


def serve(business_file):
    token = secrets.token_urlsafe(24)
    home = Home(token, business_file)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler(home))
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"port": srv.server_address[1], "token": token, "pid": os.getpid()}), encoding="utf-8")
    try:
        os.chmod(STATE, 0o600)
    except OSError:
        pass

    def idle():
        while time.time() - home.touched < IDLE_HOURS * 3600:
            time.sleep(60)
        srv.shutdown()
    threading.Thread(target=idle, daemon=True).start()
    try:
        srv.serve_forever()
    finally:
        try:
            STATE.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------- what the session runs
def running():
    try:
        s = json.loads(STATE.read_text(encoding="utf-8"))
        urllib.request.urlopen(f"http://127.0.0.1:{s['port']}/state?t={s['token']}", timeout=3).read()
        return s
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        return None


def start(business_file):
    s = running()
    if s:
        return s, False
    cmd = [sys.executable, str(Path(__file__).resolve()), "serve", "--business-file", str(business_file or "")]
    kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kw["creationflags"] = 0x00000008 | 0x00000200            # detached, in its own group: it outlives this command
    else:
        kw["start_new_session"] = True
    subprocess.Popen(cmd, **kw)
    for _ in range(50):
        time.sleep(0.1)
        s = running()
        if s:
            return s, True
    sys.exit("The Build Room home page did not start. Carry on in the chat, and tell the member the page is not available.")


def control(s, body):
    req = urllib.request.Request(f"http://127.0.0.1:{s['port']}/control?t={s['token']}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=5).read()


def wait(s, timeout):
    try:
        raw = urllib.request.urlopen(f"http://127.0.0.1:{s['port']}/next?t={s['token']}&wait={timeout}", timeout=timeout + 10).read()
        print(raw.decode("utf-8"))
    except (OSError, urllib.error.URLError):
        print(json.dumps({"event": "closed", "note": "The home page is not running. Say so, and carry on in the chat or run: home.py open"}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("open", "wait", "form", "say", "stop", "serve"):
        p = sub.add_parser(name)
        if name in ("open", "serve"):
            p.add_argument("--business-file", default="BUILDROOM_BUSINESS_FILE.md")
        if name == "open":
            p.add_argument("--no-browser", action="store_true")
        if name in ("open", "wait", "form"):
            p.add_argument("--timeout", type=int, default=100)
        if name == "form":
            p.add_argument("file")
        if name == "say":
            p.add_argument("text")
    a = ap.parse_args()
    if a.cmd == "serve":
        return serve(a.business_file)
    if a.cmd == "open":
        s, fresh = start(a.business_file)
        url = f"http://127.0.0.1:{s['port']}/?t={s['token']}"
        if fresh and not a.no_browser:
            webbrowser.open(url)
        print(json.dumps({"page": url, "opened": bool(fresh and not a.no_browser)}), file=sys.stderr)
        return wait(s, max(1, min(110, a.timeout)))
    s = running()
    if not s:
        if a.cmd == "stop":
            return print("Not running.")
        sys.exit("The Build Room home page is not running. Run: home.py open")
    if a.cmd == "wait":
        return wait(s, max(1, min(110, a.timeout)))
    if a.cmd == "say":
        return control(s, {"status": a.text})
    if a.cmd == "stop":
        control(s, {"stop": True})
        return print("Stopped.")
    if a.cmd == "form":
        try:
            f = json.loads(Path(a.file).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.exit(f"Cannot read the form: {e}")
        fields = f.get("fields")
        if not isinstance(fields, list) or not 1 <= len(fields) <= 8 or not all(isinstance(q, dict) and re.fullmatch(r"[a-z0-9_]{1,40}", str(q.get("id", ""))) and q.get("label") for q in fields):
            sys.exit('A form has 1 to 8 fields, each {"id": "short_name", "label": "The question", "type": "short|long|choice", "hint": "...", "options": [...]}')
        if any(re.search(r"password|api[ _-]?key|token|secret|card number", str(q.get("label", "")) + str(q.get("id", "")), re.I) for q in fields):
            sys.exit("Never ask for a password, a key or a card number on a form: the answers are printed into the session. Keys go through the Key Ring.")
        control(s, {"form": {"id": f.get("id") or secrets.token_hex(4), "title": str(f.get("title", ""))[:120], "intro": str(f.get("intro", ""))[:400],
                             "fields": [{"id": q["id"], "label": str(q["label"])[:200], "hint": str(q.get("hint", ""))[:200],
                                         "type": q.get("type") if q.get("type") in ("short", "long", "choice") else "short",
                                         "options": [str(o)[:80] for o in (q.get("options") or [])][:12]} for q in fields]}})
        return wait(s, max(1, min(110, a.timeout)))


if __name__ == "__main__":
    main()
