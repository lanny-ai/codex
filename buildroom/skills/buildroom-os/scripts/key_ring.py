#!/usr/bin/env python3
"""Build Room Key Ring: the member's API keys, saved once on their own computer and never typed into the chat.

  key_ring.py add PROVIDER [--folder .] [--replace]   open a page in the member's browser where they paste the key, then wait
  key_ring.py wait                                     wait again (the page is still open)
  key_ring.py list [--folder .]                        what is on the key ring: names, dates, last four characters. Never a key
  key_ring.py link PROVIDER... [--folder .]            write keys already on the ring into this folder's .env
  key_ring.py check [PROVIDER...]                      ask each provider again whether its key still works
  key_ring.py remove PROVIDER --yes [--folder .]       take a key off the ring (and out of this folder's .env)
  key_ring.py catalog                                  the providers it knows: what each is for and where the key comes from
  key_ring.py stop                                     close the page

How it works. There is one key ring per computer: a private file in the member's home folder (~/.buildroom/keys.json).
`add` opens a page served from this computer to this computer only (127.0.0.1, random port, random token). The member
pastes the key there. The page's own server checks the key with the provider, saves it on the ring, and writes it into
the .env file of the working folder, which is where the Build Room tools look for it. The session only ever hears
"saved" or "not saved": no command here prints a key, and none takes a key as an argument.

Each waiting command prints one line of JSON and exits:
  {"event": "saved", "provider": "gohighlevel", "works": true, ...}     the key is on the ring and in the folder's .env
  {"event": "linked", ...}                                               it was already on the ring: the .env is filled
  {"event": "none"}                                                      nothing yet: run `key_ring.py wait` again
  {"event": "closed"}                                                    the page is gone and nothing was saved

Plainly: the keys are kept as ordinary text in two private files on this computer (the ring and each folder's .env).
That is as safe as the computer's own login. They are not sent to Build Room, and the only place a key goes online is
to the provider it belongs to, to check that it works. Standard library only.
"""
import argparse, http.server, json, os, re, secrets, subprocess, sys, tempfile, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser
from datetime import date
from pathlib import Path

DISCLOSURE = "This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you."
PAGE_MINUTES = 30
ENV_HEADER = "# Keys added by the Build Room Key Ring. Keep this file private: never share it or paste it anywhere."


def home_dir():
    return Path(os.environ.get("BUILDROOM_KEYRING_DIR") or (Path.home() / ".buildroom"))


def ring_file():
    return home_dir() / "keys.json"


def page_file():
    return home_dir() / "key-page.json"


def result_file():
    return home_dir() / "key-page-result.json"


# ---------------------------------------------------------------- checking a key with its provider
def fetch(url, headers):
    """(status, text). Status 0 means the provider could not be reached."""
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "BuildRoomOS-keyring/1", **headers})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read(4000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(4000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError) as e:
        return 0, str(getattr(e, "reason", e))


def api_base(env_name, default):
    return (os.environ.get(env_name) or default).rstrip("/")          # the override is for tests: it is read from the process, never from a .env


def unsure(code, who):
    if code == 0:
        return "unknown", f"{who} could not be reached just now, so the key was not checked."
    return "unknown", f"{who} answered in a way this check does not understand (HTTP {code}), so the key was not checked."


def check_gohighlevel(v):
    code, text = fetch(api_base("GHL_API_BASE", "https://services.leadconnectorhq.com") + "/locations/" + urllib.parse.quote(v["GHL_LOCATION_ID"], safe=""),
                       {"Authorization": "Bearer " + v["GHL_TOKEN"], "Version": "2021-07-28"})
    if code == 200:
        return "ok", "GoHighLevel accepted the token for this sub-account."
    low = text.lower()
    if code in (401, 403) and "scope" in low:
        return "ok", "GoHighLevel accepted the token, but the integration is missing the View Locations permission. Add it in the integration's settings; the token stays the same."
    if code == 401:
        return "rejected", "GoHighLevel did not accept this token. Copy it again from the integration (it is shown once, when the integration is made) or make a new one."
    if code in (400, 403, 404, 422):
        return "rejected", "This token does not belong to this Location ID. Take both from the same sub-account."
    return unsure(code, "GoHighLevel")


def simple_check(who, base_env, default, path, auth):
    """For providers whose API shape Build Room has not confirmed: a clear yes or a clear no counts, anything else is 'not checked'."""
    def run(v):
        code, _text = fetch(api_base(base_env, default) + path, auth(v))
        if code == 200:
            return "ok", f"{who} accepted the key."
        if code in (401, 403):
            return "rejected", f"{who} did not accept this key. Copy it again from your account, with no spaces before or after."
        return unsure(code, who)
    return run


PROVIDERS = {
    "gohighlevel": {
        "name": "GoHighLevel",
        "used_for": "Push a finished build into your sub-account in one go, and read your funnel numbers (how many leads, calls booked and deals won).",
        "cost": "Making a key is free. It comes with the GoHighLevel sub-account you already have.",
        "steps": [
            "Open your GoHighLevel sub-account and go to Settings, then Private Integrations.",
            "Create a new integration. Name it Build Room.",
            "Turn on these permissions: View Locations, View Custom Values, Edit Custom Values, View Contacts, View Forms, View Calendars, View Calendar Events, View Opportunities.",
            "Leave everything under Conversations off. Build Room never sends messages for you.",
            "Create it, then copy the token. GoHighLevel shows it once.",
            "Later, if a Build Room tool needs one more permission, it will name it. You add it to this same integration and the token stays the same.",
        ],
        "fields": [
            {"env": "GHL_TOKEN", "label": "Private integration token", "secret": True, "hint": "Starts with pit-", "prefix": "pit-",
             "also": ["GHL_API_KEY"]},                              # the Funnel Map and Decision Machine pushes read the same token under this name
            {"env": "GHL_LOCATION_ID", "label": "Location ID", "secret": False,
             "hint": "The code after /location/ in the address bar. You can paste the whole address and it will be picked out.",
             "extract": r"/location/([A-Za-z0-9]{6,40})"},
        ],
        "check": check_gohighlevel,
    },
    "kie": {
        "name": "Kie.ai",
        "used_for": "Make images and short video clips for your ads, videos and website.",
        "cost": "Pay as you go, with no subscription. Check the current prices on their site before you add credit.",
        "steps": ["Sign in to your Kie.ai account.", "Create an API key in your account settings.", "Copy it and paste it below."],
        "signup": {"affiliate": "https://kie.ai?ref=62126a8991d5546179db893d9bc15a7c", "plain": "https://kie.ai"},
        "fields": [{"env": "KIE_API_KEY", "label": "API key", "secret": True, "hint": ""}],
        "check": simple_check("Kie.ai", "KIE_API_BASE", "https://api.kie.ai", "/api/v1/chat/credit", lambda v: {"Authorization": "Bearer " + v["KIE_API_KEY"]}),
    },
    "higgsfield": {
        "name": "Higgsfield",
        "used_for": "Make image plates and video scenes for the Ad Studio and the Video Director.",
        "cost": "Check the current plans and prices on their site before you sign up.",
        "steps": ["Sign in to your Higgsfield account.", "Create an API key in your account settings. It comes as two parts: a key and a secret.", "Copy both and paste them below."],
        "signup": {"affiliate": "https://higgsfield.ai?fpr=lanny-756d90", "plain": "https://higgsfield.ai"},
        "fields": [{"env": "HIGGSFIELD_API_KEY", "label": "API key", "secret": True, "hint": ""},
                   {"env": "HIGGSFIELD_API_SECRET", "label": "API secret", "secret": True, "hint": ""}],
        "check": None,
    },
    "heygen": {
        "name": "HeyGen",
        "used_for": "Make extra versions of a video with your own avatar twin, once you have agreed to one.",
        "cost": "Check the current plans and prices on their site before you sign up.",
        "steps": ["Sign in to your HeyGen account.", "Create an API key in your account settings.", "Copy it and paste it below."],
        "signup": {"plain": "https://heygen.com"},
        "fields": [{"env": "HEYGEN_API_KEY", "label": "API key", "secret": True, "hint": ""}],
        "check": simple_check("HeyGen", "HEYGEN_API_BASE", "https://api.heygen.com", "/v2/user/remaining_quota", lambda v: {"X-Api-Key": v["HEYGEN_API_KEY"]}),
    },
    "submagic": {
        "name": "SubMagic",
        "used_for": "Add styled, word-accurate captions to a finished video.",
        "cost": "Check the current plans and prices on their site before you sign up.",
        "steps": ["Sign in to your SubMagic account.", "Create an API key in your account settings.", "Copy it and paste it below."],
        "signup": {"affiliate": "https://submagic.co/?via=harrison22", "plain": "https://submagic.co"},
        "fields": [{"env": "SUBMAGIC_API_KEY", "label": "API key", "secret": True, "hint": ""}],
        "check": None,
    },
}
ALIASES = {"ghl": "gohighlevel", "highlevel": "gohighlevel", "go-high-level": "gohighlevel", "kie.ai": "kie", "kieai": "kie"}


def provider(slug):
    s = ALIASES.get(str(slug).lower().strip(), str(slug).lower().strip())
    if s not in PROVIDERS:
        sys.exit(f"The Key Ring does not know '{slug}'. It knows: {', '.join(sorted(PROVIDERS))}. For any other key, the member adds a line to .env themselves.")
    return s


def run_check(slug, values):
    fn = PROVIDERS[slug]["check"]
    if not fn:
        return "unknown", f"Build Room has no safe way to check a {PROVIDERS[slug]['name']} key ahead of time. The first real use will show whether it works."
    try:
        state, detail = fn(values)
    except Exception as e:                                           # a check must never lose the member's key
        state, detail = "unknown", f"The check itself failed ({type(e).__name__}), so the key was not checked."
    for v in values.values():                                        # belt and braces: a provider's own words never carry the key out
        if v and len(v) >= 6:
            detail = detail.replace(v, "***")
    return state, detail


# ---------------------------------------------------------------- the ring and the folder's .env
def private_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-keyring-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_ring():
    try:
        ring = json.loads(ring_file().read_text(encoding="utf-8"))
        if isinstance(ring, dict) and isinstance(ring.get("keys"), dict):
            return ring
    except FileNotFoundError:
        pass
    except (OSError, ValueError):
        sys.exit(f"The key ring file cannot be read ({ring_file()}). It was not changed. The member can rename it out of the way and add their keys again.")
    return {"version": 1, "keys": {}}


def save_ring(ring):
    d = home_dir()
    d.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(d, 0o700)
    except OSError:
        pass
    private_write(ring_file(), json.dumps(ring, indent=1) + "\n")


def clean_values(slug, raw):
    """({ENV: value}, None) or (None, what is wrong). The message never repeats what was typed."""
    out = {}
    for f in PROVIDERS[slug]["fields"]:
        v = str((raw or {}).get(f["env"]) or "").strip().strip("'\"").strip()
        if f.get("extract"):
            m = re.search(f["extract"], v)
            if m:
                v = m.group(1)
        if not v:
            return None, f"{f['label']} is empty."
        if len(v) > 600 or re.search(r"\s", v) or not v.isprintable():
            return None, f"{f['label']} should be one unbroken piece of text, with no spaces or line breaks. Copy it again."
        if f.get("prefix") and not v.startswith(f["prefix"]):
            return None, f"{f['label']} should start with {f['prefix']}. Check you copied the right thing."
        out[f["env"]] = v
    return out, None


def env_line(name, value):
    return f"{name}={value}" if re.fullmatch(r"[A-Za-z0-9_\-./:+=@~]+", value) else name + '="' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def ignored(folder):
    """Make sure git will not pick the .env up. Returns True if .gitignore was changed. Touches nothing outside a git project."""
    folder = Path(folder)
    gi = folder / ".gitignore"
    in_git = any((p / ".git").exists() for p in [folder, *list(folder.parents)[:6]])
    if not gi.is_file() and not in_git:
        return False
    lines = gi.read_text(encoding="utf-8", errors="replace").splitlines() if gi.is_file() else []
    if any(ln.strip() in (".env", "/.env", "*.env", ".env*", ".env.*", "**/.env") for ln in lines):
        return False
    gi.write_text("\n".join(lines + [".env"]) + "\n", encoding="utf-8")
    return True


def write_env(folder, values, remove=()):
    """Set NAME=value lines in folder/.env, keeping every other line as it is. Returns whether .gitignore was changed."""
    folder = Path(folder)
    if not folder.is_dir():
        raise OSError(f"the folder does not exist: {folder}")
    env = folder / ".env"
    lines = env.read_text(encoding="utf-8", errors="replace").splitlines() if env.is_file() else []
    todo, kept = dict(values), []
    for ln in lines:
        m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", ln)
        name = m.group(1) if m and not ln.lstrip().startswith("#") else None
        if name in remove:
            continue
        if name in values:
            if name in todo:
                kept.append(env_line(name, todo.pop(name)))
            continue                                                 # a second line for the same name would shadow the new one
        kept.append(ln)
    if todo:
        if ENV_HEADER not in kept:
            if kept and kept[-1].strip():
                kept.append("")
            kept.append(ENV_HEADER)
        kept += [env_line(k, v) for k, v in todo.items()]
    if not kept and not env.is_file():
        return False
    private_write(env, "\n".join(kept) + "\n")
    return ignored(folder) if values else False


def env_names(folder):
    try:
        text = (Path(folder) / ".env").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return {m.group(1) for m in re.finditer(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\S", text, re.M)}


def mask(value, secret):
    if not secret:
        return value
    return "ends in " + value[-4:] if len(value) >= 12 else "saved"


def store(slug, values, state, detail, folder):
    """Put a key on the ring and into the folder's .env. Returns the event the session hears (no key in it)."""
    ring = load_ring()
    today = date.today().isoformat()
    ring["keys"][slug] = {"values": values, "saved": today, "checked": today if state != "unknown" else None,
                          "works": {"ok": True, "rejected": False}.get(state), "detail": detail}
    save_ring(ring)
    ev = {"event": "saved", "provider": slug, "works": ring["keys"][slug]["works"], "detail": detail, "names": sorted(values)}
    return fill(ev, folder, values)


def env_lines(slug, values):
    """The lines a folder's .env gets: each value under its own name and under any second name an older tool reads."""
    out = dict(values)
    for f in PROVIDERS[slug]["fields"]:
        for other in f.get("also", ()):
            if f["env"] in values:
                out[other] = values[f["env"]]
    return out


def fill(ev, folder, values):
    try:
        ev["gitignore_updated"] = write_env(folder, env_lines(ev["provider"], values))
        ev["env_file"] = str(Path(folder) / ".env")
    except OSError as e:
        ev["env_file"] = None
        ev["env_problem"] = f"The key is on the key ring, but the .env file in the working folder could not be written ({e}). Run: key_ring.py link {ev['provider']} --folder FOLDER"
    return ev


# ---------------------------------------------------------------- the page
PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Room Key Ring</title><style>
:root{--navy:#0b1020;--ink:#0f1424;--mute:#5b6478;--line:#d5dae6;--panel:#f5f6fa;--gold:#ffb547;--paper:#fff;--ok:#0f7a4d;--bad:#a4262c}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.55 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
header{background:var(--navy);color:#fff;padding:22px clamp(16px,5vw,48px)}
header h1{margin:0;font-size:24px;letter-spacing:-.01em}header p{margin:4px 0 0;color:#c9d0e0;font-size:16px}
main{max-width:720px;margin:0 auto;padding:28px clamp(16px,5vw,48px) 72px}
h2{font-size:20px;margin:32px 0 10px}p{margin:0 0 14px}ol{margin:0 0 14px;padding-left:24px}li{margin:0 0 8px}
.facts{background:var(--panel);border-radius:10px;padding:16px 20px;margin:0 0 8px}.facts p:last-child{margin:0}
.small{font-size:16px;color:var(--mute)}a{color:#12379b}
label{display:block;font-weight:600;margin:20px 0 6px}
.row{display:flex;gap:8px}input{flex:1;min-width:0;font:inherit;padding:13px 14px;border:2px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
input:focus,button:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
button{font:inherit;font-weight:600;border-radius:8px;border:2px solid var(--navy);padding:12px 20px;cursor:pointer;background:#fff;color:var(--navy)}
button.go{background:var(--navy);color:#fff;margin-top:26px;min-width:200px}button[disabled]{opacity:.55;cursor:default}
#msg{margin-top:22px;border-left:5px solid var(--line);background:var(--panel);padding:14px 18px;font-weight:600}
#msg.ok{border-color:var(--ok)}#msg.bad{border-color:var(--bad)}#msg[hidden],#anyway[hidden],form[hidden]{display:none}
#anyway{margin-top:12px}
</style></head><body>
<header><h1>Build Room Key Ring</h1><p>This page is on your own computer. Nothing you type here goes into the chat.</p></header>
<main><div id="app"></div>
<form id="f" autocomplete="off"><div id="fields"></div>
<button class="go" id="save" type="submit">Check and save</button></form>
<div id="msg" role="status" aria-live="polite" hidden></div>
<button id="anyway" type="button" hidden>Save it anyway</button>
<p class="small" style="margin-top:36px">Your key is saved in a private file on this computer and in the .env file of the folder you are working in. It is not sent to Build Room. It goes to __NAME__ only, to check that it works.</p>
</main><script>
const P = __DATA__, T = new URLSearchParams(location.search).get("t");
const $ = (t, a = {}, ...kids) => { const e = document.createElement(t); for (const k in a) k === "text" ? e.textContent = a[k] : e.setAttribute(k, a[k]); kids.forEach(k => e.append(k)); return e; };
const app = document.getElementById("app");
app.append($("h2", {text: "Add your " + P.name + " key", style: "margin-top:0;font-size:26px"}));
const facts = $("div", {class: "facts"}, $("p", {}, $("strong", {text: "What it is for. "}), P.used_for), $("p", {}, $("strong", {text: "What it costs. "}), P.cost));
app.append(facts);
if (P.have) app.append($("p", {text: "A " + P.name + " key is already saved on this computer (" + P.have + "). Saving a new one replaces it."}));
if (P.signup) {
  const p = $("p", {class: "small"});
  if (P.signup.affiliate) p.append("No account yet? ", $("a", {href: P.signup.affiliate, target: "_blank", rel: "noopener noreferrer", text: "Sign up for " + P.name}), ". " + P.disclosure + " Or go straight to ", $("a", {href: P.signup.plain, target: "_blank", rel: "noopener noreferrer", text: P.signup.plain.replace("https://", "")}), ".");
  else p.append("No account yet? Sign up at ", $("a", {href: P.signup.plain, target: "_blank", rel: "noopener noreferrer", text: P.signup.plain.replace("https://", "")}), ".");
  app.append(p);
}
app.append($("h2", {text: "Where the key comes from"}));
const ol = $("ol"); P.steps.forEach(s => ol.append($("li", {text: s}))); app.append(ol);
app.append($("h2", {text: "Paste it here"}));
const fields = document.getElementById("fields");
P.fields.forEach(f => {
  const inp = $("input", {id: f.env, name: f.env, type: f.secret ? "password" : "text", autocomplete: "off", autocapitalize: "off", spellcheck: "false", required: ""});
  const row = $("div", {class: "row"}, inp);
  if (f.secret) { const b = $("button", {type: "button", text: "Show", "aria-label": "Show or hide " + f.label}); b.onclick = () => { inp.type = inp.type === "password" ? "text" : "password"; b.textContent = inp.type === "password" ? "Show" : "Hide"; }; row.append(b); }
  fields.append($("label", {for: f.env, text: f.label}), row);
  if (f.hint) fields.append($("p", {class: "small", style: "margin:6px 0 0", text: f.hint}));
});
const msg = document.getElementById("msg"), save = document.getElementById("save"), anyway = document.getElementById("anyway"), form = document.getElementById("f");
function say(text, cls) { msg.hidden = false; msg.className = cls || ""; msg.textContent = text; }
async function send(force) {
  const values = {}; P.fields.forEach(f => values[f.env] = document.getElementById(f.env).value);
  save.disabled = true; anyway.hidden = true; say("Checking the key with " + P.name + "...");
  let r;
  try { r = await (await fetch("/save?t=" + encodeURIComponent(T), {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({values, anyway: !!force})})).json(); }
  catch (e) { save.disabled = false; return say("This page lost its connection to the Key Ring. Go back to your chat and ask to add the key again.", "bad"); }
  if (r.saved) {
    P.fields.forEach(f => document.getElementById(f.env).value = ""); form.hidden = true;
    say((r.works === true ? "Saved and working. " : r.works === false ? "Saved, although the check did not pass. " : "Saved. ") + r.detail + " You can close this tab and go back to your chat.", r.works === false ? "bad" : "ok");
  } else { save.disabled = false; say("Not saved. " + r.reason, "bad"); anyway.hidden = !r.can_force; }
}
form.addEventListener("submit", e => { e.preventDefault(); send(false); });
anyway.addEventListener("click", () => send(true));
</script></body></html>"""


def page_html(slug):
    p = PROVIDERS[slug]
    have = load_ring()["keys"].get(slug)
    secret = next((f["env"] for f in p["fields"] if f["secret"]), None)
    data = {"name": p["name"], "used_for": p["used_for"], "cost": p["cost"], "steps": p["steps"], "signup": p.get("signup"), "disclosure": DISCLOSURE,
            "fields": [{"env": f["env"], "label": f["label"], "secret": f["secret"], "hint": f["hint"]} for f in p["fields"]],
            "have": mask(have["values"].get(secret, ""), True) if have and secret else None}
    return PAGE.replace("__NAME__", p["name"]).replace("__DATA__", json.dumps(data).replace("</", "<\\/"))


def handler(slug, folder, token, done):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def _ok(self):
            """Only this computer, only with the token, only when the page itself is asking."""
            host = (self.headers.get("Host") or "").split(":")[0]
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            port = self.server.server_address[1]
            return (host in ("127.0.0.1", "localhost") and secrets.compare_digest((q.get("t") or [""])[0], token)
                    and self.headers.get("Origin") in (None, f"http://127.0.0.1:{port}", f"http://localhost:{port}"))

        def do_GET(self):
            route = urllib.parse.urlsplit(self.path).path
            if not self._ok():
                return self._send(403, b'{"error":"not allowed"}')
            if route == "/":
                return self._send(200, page_html(slug).encode("utf-8"), "text/html; charset=utf-8")
            if route == "/alive":
                return self._send(200, json.dumps({"provider": slug}).encode())
            self._send(404, b'{"error":"not found"}')

        def do_POST(self):
            route = urllib.parse.urlsplit(self.path).path
            try:
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}") if 0 <= n <= 20_000 else None
            except ValueError:
                body = None
            if not self._ok() or not isinstance(body, dict):
                return self._send(403, b'{"error":"not allowed"}')
            if route == "/stop":
                done.set()
                return self._send(200, b'{"ok":true}')
            if route != "/save":
                return self._send(404, b'{"error":"not found"}')
            values, wrong = clean_values(slug, body.get("values"))
            if wrong:
                return self._send(200, json.dumps({"saved": False, "reason": wrong, "can_force": False}).encode())
            state, detail = run_check(slug, values)
            if state == "rejected" and not body.get("anyway"):
                return self._send(200, json.dumps({"saved": False, "reason": detail, "can_force": True}).encode())
            try:
                ev = store(slug, values, state, detail, folder)
            except (OSError, SystemExit) as e:
                return self._send(200, json.dumps({"saved": False, "reason": f"The key ring file could not be written ({e}).", "can_force": False}).encode())
            private_write(result_file(), json.dumps(ev))
            self._send(200, json.dumps({"saved": True, "works": ev["works"], "detail": detail + (" " + ev["env_problem"] if ev.get("env_problem") else "")}).encode())
            done.set()
    return H


def serve(slug, folder):
    token, done = secrets.token_urlsafe(24), threading.Event()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler(slug, folder, token, done))
    home_dir().mkdir(parents=True, exist_ok=True)
    private_write(page_file(), json.dumps({"port": srv.server_address[1], "token": token, "pid": os.getpid(), "provider": slug}))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    done.wait(PAGE_MINUTES * 60)
    time.sleep(1.5)                                                  # let the page receive its answer
    srv.shutdown()
    try:
        if json.loads(page_file().read_text(encoding="utf-8")).get("token") == token:
            page_file().unlink()
    except (OSError, ValueError):
        pass


# ---------------------------------------------------------------- what the session runs
def running():
    try:
        s = json.loads(page_file().read_text(encoding="utf-8"))
        urllib.request.urlopen(f"http://127.0.0.1:{s['port']}/alive?t={s['token']}", timeout=3).read()
        return s
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        return None


def stop():
    s = running()
    if not s:
        return False
    try:
        urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{s['port']}/stop?t={s['token']}", data=b"{}", headers={"Content-Type": "application/json"}), timeout=5).read()
    except (OSError, urllib.error.URLError):
        pass
    for _ in range(40):
        if not running():
            break
        time.sleep(0.1)
    return True


def start(slug, folder):
    stop()
    try:
        result_file().unlink()
    except OSError:
        pass
    cmd = [sys.executable, str(Path(__file__).resolve()), "serve", slug, "--folder", str(folder)]
    kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kw["creationflags"] = 0x00000008 | 0x00000200                # detached, in its own group: it outlives this command
    else:
        kw["start_new_session"] = True
    subprocess.Popen(cmd, **kw)
    for _ in range(60):
        time.sleep(0.1)
        s = running()
        if s:
            return s
    sys.exit("The Key Ring page did not start. The member can add the key by hand instead: one line per key in the .env file of the working folder. Never ask them to paste it in the chat.")


def wait(timeout):
    end = time.time() + max(1, min(110, timeout))
    while True:
        try:
            ev = json.loads(result_file().read_text(encoding="utf-8"))
            result_file().unlink()
            return print(json.dumps(ev))
        except (OSError, ValueError):
            pass
        if not running():
            return print(json.dumps({"event": "closed", "note": "The Key Ring page is not open and nothing was saved. Run `key_ring.py add PROVIDER` to open it again."}))
        if time.time() >= end:
            return print(json.dumps({"event": "none", "note": "Nothing saved yet. The member may still be getting the key: run `key_ring.py wait` again."}))
        time.sleep(0.4)


def listing(folder):
    ring, here = load_ring(), env_names(folder)
    out = []
    for slug, k in sorted(ring["keys"].items()):
        p = PROVIDERS.get(slug)
        if not p:
            continue
        out.append({"provider": slug, "name": p["name"], "saved": k.get("saved"), "last_checked": k.get("checked"), "works": k.get("works"),
                    "keys": {f["env"]: mask(k["values"].get(f["env"], ""), f["secret"]) for f in p["fields"]},
                    "in_this_folder": all(f["env"] in here for f in p["fields"])})
    return {"key_ring": str(ring_file()), "folder": str(Path(folder).resolve()), "saved": out,
            "not_added_yet": [s for s in sorted(PROVIDERS) if s not in ring["keys"]],
            "note": "Show the member the names, dates and endings only. `works` null means the key has not been checked."}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("add", "wait", "list", "link", "check", "remove", "catalog", "stop", "serve"):
        p = sub.add_parser(name)
        if name in ("add", "remove", "serve"):
            p.add_argument("provider")
        if name in ("link", "check"):
            p.add_argument("providers", nargs="*" if name == "check" else "+")
        if name in ("add", "list", "link", "remove", "serve"):
            p.add_argument("--folder", default=".")
        if name in ("add", "wait"):
            p.add_argument("--timeout", type=int, default=100)
        if name == "add":
            p.add_argument("--replace", action="store_true", help="open the page even though a key is already saved")
            p.add_argument("--no-browser", action="store_true")
        if name == "remove":
            p.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    folder = Path(getattr(a, "folder", ".")).resolve()

    if a.cmd == "serve":
        return serve(provider(a.provider), folder)
    if a.cmd == "catalog":
        return print(json.dumps({"providers": [{"provider": s, "name": p["name"], "used_for": p["used_for"], "cost": p["cost"], "signup": p.get("signup"),
                                                "env_names": [n for f in p["fields"] for n in (f["env"], *f.get("also", ()))], "checked_on_save": bool(p["check"])} for s, p in sorted(PROVIDERS.items())],
                                 "disclosure": DISCLOSURE,
                                 "note": "When you offer an affiliate sign-up link, put the disclosure sentence right next to it, word for word, and offer the plain route too."}, indent=1))
    if a.cmd == "list":
        return print(json.dumps(listing(folder), indent=1))
    if a.cmd == "stop":
        return print("Stopped." if stop() else "Not running.")
    if a.cmd == "wait":
        return wait(a.timeout)

    if a.cmd == "add":
        slug = provider(a.provider)
        if not folder.is_dir():
            sys.exit(f"The folder does not exist: {folder}")
        have = load_ring()["keys"].get(slug)
        if have and not a.replace:
            ev = fill({"event": "linked", "provider": slug, "works": have.get("works"), "names": sorted(have["values"]),
                       "note": "This key was already on the computer's key ring, so nothing was asked. To change the key, run add with --replace."}, folder, have["values"])
            return print(json.dumps(ev))
        s = start(slug, folder)
        url = f"http://127.0.0.1:{s['port']}/?t={s['token']}"
        opened = False
        if not a.no_browser:
            try:
                opened = bool(webbrowser.open(url))
            except Exception:
                opened = False
        print(json.dumps({"page": url, "opened": opened, "note": "If the browser did not open, give the member this address to open on this computer. It works only here and only for the next 30 minutes."}), file=sys.stderr)
        return wait(a.timeout)

    ring = load_ring()
    if a.cmd == "link":
        out = []
        for slug in [provider(x) for x in a.providers]:
            k = ring["keys"].get(slug)
            if not k:
                out.append({"event": "missing", "provider": slug, "note": f"Not on the key ring yet. Run: key_ring.py add {slug}"})
            else:
                out.append(fill({"event": "linked", "provider": slug, "works": k.get("works"), "names": sorted(k["values"])}, folder, k["values"]))
        return print(json.dumps(out, indent=1))
    if a.cmd == "check":
        slugs = [provider(x) for x in a.providers] or sorted(s for s in ring["keys"] if s in PROVIDERS)
        out = []
        for slug in slugs:
            k = ring["keys"].get(slug)
            if not k:
                out.append({"provider": slug, "works": None, "detail": "Not on the key ring."})
                continue
            state, detail = run_check(slug, k["values"])
            if state != "unknown":
                k.update({"works": state == "ok", "checked": date.today().isoformat(), "detail": detail})
            out.append({"provider": slug, "works": {"ok": True, "rejected": False}.get(state), "detail": detail})
        save_ring(ring)
        return print(json.dumps(out, indent=1))
    if a.cmd == "remove":
        slug = provider(a.provider)
        if not a.yes:
            sys.exit(f"Removing takes the {PROVIDERS[slug]['name']} key off this computer's key ring and out of this folder's .env. It does not cancel the key at "
                     f"{PROVIDERS[slug]['name']}: the member does that in their account. Ask the member first, then run again with --yes.")
        names = [n for f in PROVIDERS[slug]["fields"] for n in (f["env"], *f.get("also", ()))]
        was = ring["keys"].pop(slug, None)
        save_ring(ring)
        try:
            write_env(folder, {}, remove=names)
        except OSError:
            pass
        return print(json.dumps({"event": "removed" if was else "not_there", "provider": slug, "names": names,
                                 "note": f"Other folders' .env files still hold the key until it is removed there. To make the key useless everywhere, the member deletes it in their {PROVIDERS[slug]['name']} account."}))


if __name__ == "__main__":
    main()
