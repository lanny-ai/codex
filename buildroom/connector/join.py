"""Build Room connector: self-serve sign-up with instant access for clear payers and admin approval for the rest.

    /join   the member page: name, email and the room code announced at the live session
    /admin  the owner page: pending requests, approve or decline, a link to send by hand

Settings (host variables):
    BUILDROOM_DATA_DIR            folder that survives restarts (a Railway volume), holds signups.json
    BUILDROOM_JOIN_CODE           the room code; sign-up is closed when it is not set
    BUILDROOM_JOIN_UNTIL          last day sign-up is open (YYYY-MM-DD, UTC); closed after it
    BUILDROOM_PREAPPROVED         JSON list of sha256(lowercase email) for instant access; no emails are stored
    BUILDROOM_ADMIN_KEY_SHA256    sha256 of the owner's admin key
Standard library only.
"""
import hashlib, hmac, json, os, re, secrets, threading, time
from datetime import date, datetime, timezone
from pathlib import Path

EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[A-Za-z]{2,24}$")


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def norm_email(e):
    return (e or "").strip().lower()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    """signups.json: members created by sign-up (key fingerprints only) and access requests."""

    def __init__(self, data_dir):
        self.path = Path(data_dir) / "signups.json" if data_dir else None
        self.lock = threading.Lock()
        self._mem = {"members": [], "requests": []}

    def load(self):
        if not self.path:
            return self._mem
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"members": [], "requests": []}

    def save(self, data):
        if not self.path:
            self._mem = data
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    def members(self):
        return list(self.load().get("members", []))

    def issue_key(self, email, name, via):
        """Create the member, or give an existing sign-up member a new key (the old one stops)."""
        key = "br_" + secrets.token_urlsafe(24)
        with self.lock:
            d = self.load()
            m = next((x for x in d["members"] if x["email"] == email), None)
            if m:
                m["key_sha256"], m["status"], m["rotated"] = sha(key), "active", now()
            else:
                d["members"].append({"email": email, "name": name, "key_sha256": sha(key), "status": "active",
                                     "current_until": None, "added": date.today().isoformat(), "via": via})
            self.save(d)
        return key

    def request(self, email, name):
        with self.lock:
            d = self.load()
            r = next((x for x in d["requests"] if x["email"] == email), None)
            if not r:
                r = {"email": email, "name": name, "at": now(), "status": "pending"}
                d["requests"].append(r)
                self.save(d)
            return dict(r)

    def decide(self, email, decision):
        with self.lock:
            d = self.load()
            r = next((x for x in d["requests"] if x["email"] == email), None)
            if decision in ("approve", "decline"):
                if not r:
                    return None
                r["status"], r["decided"] = ("approved" if decision == "approve" else "declined"), now()
            elif decision == "lapse":
                m = next((x for x in d["members"] if x["email"] == email), None)
                if not m:
                    return None
                m["status"] = "lapsed"
            self.save(d)
            return True


class Join:
    def __init__(self, store, existing_emails):
        self.store = store
        self.existing_emails = existing_emails  # callable: emails already on the host's member list
        self.hits = {}

    # -- settings, read each time so a host change applies at once
    def code(self):
        return os.environ.get("BUILDROOM_JOIN_CODE", "").strip()

    def open_now(self):
        if not self.code():
            return False
        until = os.environ.get("BUILDROOM_JOIN_UNTIL", "").strip()
        return not until or datetime.now(timezone.utc).date() <= date.fromisoformat(until)

    def preapproved(self, email):
        try:
            return sha(email) in set(json.loads(os.environ.get("BUILDROOM_PREAPPROVED", "[]")))
        except ValueError:
            return False

    def admin_ok(self, key):
        want = os.environ.get("BUILDROOM_ADMIN_KEY_SHA256", "")
        return bool(want and key) and hmac.compare_digest(sha(key), want)

    def limited(self, ip, limit=30, window=600):
        t = time.time()
        q = [x for x in self.hits.get(ip, []) if t - x < window]
        q.append(t)
        self.hits[ip] = q
        return len(q) > limit

    def submit(self, ip, body):
        """Returns (http_status, json)."""
        if self.limited(ip):
            return 429, {"state": "slow_down", "message": "Too many tries. Wait ten minutes and try again."}
        if not self.open_now():
            return 403, {"state": "closed", "message": "Sign-up is closed. Ask the Build Room team for your link."}
        name = (body.get("name") or "").strip()[:80]
        email = norm_email(body.get("email"))
        code = (body.get("code") or "").strip().upper()
        if not hmac.compare_digest(code, self.code().upper()):
            return 400, {"state": "bad_code", "message": "That room code is not right. Check it with the host and try again."}
        if not EMAIL.match(email):
            return 400, {"state": "bad_email", "message": "Please enter the email you use for the Build Room."}
        if email in self.existing_emails():
            return 200, {"state": "already", "message": "You already have a personal link from the Build Room team. Use that one, or ask the team for a new one."}
        if any(m["email"] == email and m.get("status") == "active" for m in self.store.members()) or self.preapproved(email):
            return 200, {"state": "approved", "key": self.store.issue_key(email, name, "instant"),
                         "message": "You're in. Here is your personal link."}
        r = self.store.request(email, name)
        if r["status"] == "approved":
            return 200, {"state": "approved", "key": self.store.issue_key(email, name, "approved"),
                         "message": "You're approved. Here is your personal link."}
        if r["status"] == "declined":
            return 200, {"state": "declined", "message": "We couldn't match this email to a current membership. Please contact the Build Room team."}
        return 200, {"state": "pending", "message": "Thanks. The Build Room team will check your membership. Come back to this page in a little while and enter the same email to get your link."}

    def admin(self, method, path, key, body):
        if not self.admin_ok(key):
            return 401, {"error": "Admin key required."}
        if method == "GET":
            d = self.store.load()
            return 200, {"open": self.open_now(), "until": os.environ.get("BUILDROOM_JOIN_UNTIL"),
                         "requests": d.get("requests", []),
                         "members": [{k: m.get(k) for k in ("email", "name", "status", "added", "via")} for m in d.get("members", [])]}
        email, decision = norm_email(body.get("email")), body.get("decision")
        if decision == "link":
            name = next((r["name"] for r in self.store.load().get("requests", []) if r["email"] == email), "")
            self.store.decide(email, "approve")
            return 200, {"key": self.store.issue_key(email, name, "admin")}
        if decision not in ("approve", "decline", "lapse") or not self.store.decide(email, decision):
            return 400, {"error": "Nothing to change for that email."}
        return 200, {"ok": True}


STYLE = """<style>
:root{--bg:#f7f5f0;--card:#fff;--ink:#16202c;--soft:#4a5563;--line:#d9d4c7;--accent:#c2410c;--ok:#166534;--okbg:#e8f5ec;--wait:#854d0e;--waitbg:#fdf3dc}
@media (prefers-color-scheme:dark){:root{--bg:#14181f;--card:#1d232c;--ink:#eef0f3;--soft:#b8c0cc;--line:#333b47;--accent:#fb923c;--ok:#86efac;--okbg:#173322;--wait:#fcd34d;--waitbg:#3a2f12}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:19px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:640px;margin:0 auto;padding:28px 16px 60px}h1{font-size:30px;line-height:1.2;margin:0 0 6px}p.lede{color:var(--soft);margin:0 0 22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin:0 0 18px}
label{display:block;font-weight:600;margin:14px 0 6px}input{width:100%;font:inherit;padding:12px 14px;border:2px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)}
input:focus{outline:3px solid var(--accent);outline-offset:1px}
button{font:inherit;font-weight:700;padding:13px 20px;border-radius:10px;border:0;background:var(--accent);color:#fff;cursor:pointer;margin-top:18px;min-height:48px}
button.ghost{background:transparent;color:var(--ink);border:2px solid var(--line);margin:4px 6px 0 0;padding:8px 14px;min-height:40px;font-size:16px}
.ok{background:var(--okbg);color:var(--ok)}.wait{background:var(--waitbg);color:var(--wait)}.msg{border-radius:10px;padding:14px 16px;margin-top:16px;font-weight:600}
.link{word-break:break-all;font:16px/1.4 ui-monospace,Menlo,monospace;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px;margin:10px 0}
ol li{margin:6px 0}table{width:100%;border-collapse:collapse;font-size:16px}td,th{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
.small{font-size:15px;color:var(--soft)}
</style>"""

JOIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Room OS: get your link</title>""" + STYLE + """</head><body><main>
<h1>Get your Build Room OS link</h1><p class="lede">One personal link connects Claude to every Build Room session.</p>
<div class="card" id="formcard"><form id="f">
<label for="name">Your name</label><input id="name" autocomplete="name" required>
<label for="email">The email you use for the Build Room</label><input id="email" type="email" autocomplete="email" required>
<label for="code">Room code (from the host)</label><input id="code" autocapitalize="characters" required>
<button type="submit">Get my link</button></form><div id="out" role="status" aria-live="polite"></div></div>
<div class="card" id="steps" hidden><h2 style="margin-top:0">Your personal link</h2><p class="small">Keep it to yourself: it is yours alone.</p>
<div class="link" id="link"></div><button class="ghost" id="copy" type="button">Copy link</button>
<h2>Set it up in Claude desktop</h2><ol><li>Open Claude, then <b>Settings</b>, then <b>Connectors</b>.</li><li>Click <b>Add custom connector</b>.</li>
<li>Name it <b>Build Room OS</b> and paste your link.</li><li>Click <b>Add</b>.</li><li>Start a new chat, open the tools menu under the message box, and switch <b>Build Room OS</b> on.</li>
<li>Type: <b>What Build Room sessions do I have?</b></li></ol>
<p class="small">Claude Code instead: <span class="link" id="cc"></span></p></div>
<script>
const $=id=>document.getElementById(id);
$('f').addEventListener('submit',async e=>{e.preventDefault();const out=$('out');out.className='msg';out.textContent='Checking...';
try{const r=await fetch('/join',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:$('name').value,email:$('email').value,code:$('code').value})});
const j=await r.json();out.textContent=j.message||'Something went wrong.';out.className='msg '+(j.state==='approved'?'ok':'wait');
if(j.key){const url=location.origin+'/mcp/'+j.key;$('link').textContent=url;$('cc').textContent='claude mcp add --transport http buildroom '+location.origin+'/mcp --header "Authorization: Bearer '+j.key+'"';$('steps').hidden=false;$('steps').scrollIntoView({behavior:'smooth'});}}
catch(err){out.textContent='Could not reach the Build Room server. Try again in a moment.';out.className='msg wait';}});
$('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('link').textContent);$('copy').textContent='Copied';}catch(e){}});
</script></main></body></html>"""

ADMIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Room OS: approvals</title>""" + STYLE + """</head><body><main style="max-width:900px">
<h1>Build Room OS approvals</h1><p class="lede" id="state">Enter your admin key.</p>
<div class="card" id="login"><label for="k">Admin key</label><input id="k" type="password" autocomplete="off"><button id="go" type="button">Open</button></div>
<div class="card" id="reqs" hidden><h2 style="margin-top:0">Waiting for approval</h2><div id="pending"></div><h2>Decided</h2><div id="done"></div></div>
<div class="card" id="mems" hidden><h2 style="margin-top:0">Signed up</h2><div id="members"></div></div>
<div class="card" id="sent" hidden><h2 style="margin-top:0">Link to send</h2><div class="link" id="sendlink"></div></div>
<script>
const $=id=>document.getElementById(id);let KEY='';try{KEY=sessionStorage.getItem('brk')||''}catch(e){}
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(method,body){const r=await fetch('/admin/api',{method,headers:{'Authorization':'Bearer '+KEY,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});return [r.status,await r.json()];}
function row(r,btns){return '<tr><td><b>'+esc(r.name)+'</b><br><span class="small">'+esc(r.email)+'</span></td><td class="small">'+esc((r.at||r.added||'').slice(0,16).replace('T',' '))+'<br>'+esc(r.status||'')+(r.via?' ('+esc(r.via)+')':'')+'</td><td>'+btns+'</td></tr>';}
function b(email,d,label){return '<button class="ghost" data-e="'+esc(email)+'" data-d="'+d+'">'+label+'</button>';}
async function load(){const [s,j]=await api('GET');if(s!==200){$('state').textContent='That admin key is not right.';$('login').hidden=false;return;}
try{sessionStorage.setItem('brk',KEY)}catch(e){}$('login').hidden=true;$('reqs').hidden=false;$('mems').hidden=false;
$('state').textContent='Sign-up is '+(j.open?'open':'closed')+(j.until?' (until '+j.until+', UTC)':'')+'. Approved people get their link when they come back to the sign-up page, or send them one with "Approve and get link".';
const p=j.requests.filter(r=>r.status==='pending'),d=j.requests.filter(r=>r.status!=='pending');
$('pending').innerHTML=p.length?'<table>'+p.map(r=>row(r,b(r.email,'approve','Approve')+b(r.email,'link','Approve and get link')+b(r.email,'decline','Decline'))).join('')+'</table>':'<p class="small">No one waiting.</p>';
$('done').innerHTML=d.length?'<table>'+d.map(r=>row(r,r.status==='declined'?b(r.email,'approve','Approve instead'):'')).join('')+'</table>':'<p class="small">None yet.</p>';
$('members').innerHTML=j.members.length?'<table>'+j.members.map(m=>row(m,m.status==='active'?b(m.email,'lapse','Stop access'):'')).join('')+'</table>':'<p class="small">No one yet.</p>';}
document.addEventListener('click',async e=>{const t=e.target;if(!t.dataset||!t.dataset.d)return;if(t.dataset.d!=='approve'&&!confirm(t.textContent+' for '+t.dataset.e+'?'))return;
const [s,j]=await api('POST',{email:t.dataset.e,decision:t.dataset.d});if(j.key){$('sendlink').textContent=location.origin+'/mcp/'+j.key;$('sent').hidden=false;}load();});
$('go').addEventListener('click',()=>{KEY=$('k').value.trim();load();});if(KEY)load();
</script></main></body></html>"""
