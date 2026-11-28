#!/usr/bin/env python3
"""The Key Ring: a key is pasted on a local page, checked, saved on the computer's ring and written into the folder's .env,
and no command ever prints it. Providers are played by a stand-in server; nothing here goes online.

Usage:  python3 buildroom/tests/keyring/run_tests.py
"""
import ast, http.server, json, os, stat, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/buildroom-os/scripts/key_ring.py"
RESULTS = []
GOOD, NOSCOPE, ROTATED = "pit-good-0000-1111-2222-aaaabbbbcccc", "pit-noscope-0000-1111-2222-ddddeeee", "pit-rotated-0000-1111-2222-ffff9999"
KIE_GOOD, LOC = "kie-live-1234567890abcdef", "LocGood123"
SECRETS = (GOOD, NOSCOPE, ROTATED, KIE_GOOD, "hf-key-123456789012", "hf-secret-123456789012", "pit-bad-0000-0000-0000-000000000000")
SEEN = []                     # everything any command printed
DEAD = set()                  # tokens the stand-in has "rotated"


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


class Provider(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        tok = (self.headers.get("Authorization") or "").replace("Bearer ", "")
        code, body = 404, {"message": "not found"}
        if self.path.startswith("/locations/"):
            loc = self.path.split("/")[2]
            if tok in DEAD or tok not in (GOOD, NOSCOPE, ROTATED):
                code, body = 401, {"message": "Invalid JWT"}
            elif tok == NOSCOPE:
                code, body = 401, {"message": "The token is not authorized for this scope."}
            elif loc == "LocBroken":
                code, body = 500, {"message": "boom " + tok}
            elif loc != LOC:
                code, body = 403, {"message": "The token does not have access to this location."}
            else:
                code, body = 200, {"location": {"id": loc, "name": "Stand-in Co"}}
        elif self.path == "/api/v1/chat/credit":
            code, body = (200, {"data": 5}) if tok == KIE_GOOD else (401, {"msg": "no"})
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def run(ring, cwd, *args, base=None):
    env = dict(os.environ, BUILDROOM_KEYRING_DIR=str(ring), GHL_API_BASE=base or "", KIE_API_BASE=base or "")
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=env, cwd=str(cwd), timeout=60)
    SEEN.append(p.stdout + p.stderr)
    return p.returncode, p.stdout, p.stderr


def page(ring):
    s = json.loads((ring / "key-page.json").read_text())
    return s["port"], s["token"]


def get(port, path, headers=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), dict(e.headers)


def post(port, token, values, anyway=False, headers=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/save?t={token}", data=json.dumps({"values": values, "anyway": anyway}).encode(),
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            text = r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, {}
    SEEN.append(text)
    return 200, json.loads(text)


def open_page(ring, cwd, base, *args):
    rc, out, err = run(ring, cwd, "add", *args, "--no-browser", "--timeout", "1", base=base)
    return rc, out, err


def gone(ring):
    for _ in range(60):
        if not (ring / "key-page.json").exists():
            return True
        time.sleep(0.1)
    return False


def main():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    tmp = Path(tempfile.mkdtemp())
    ring, a, b, plain = tmp / "ring", tmp / "work-a", tmp / "work-b", tmp / "plain"
    for d in (a, b, plain):
        d.mkdir()
    (a / ".git").mkdir()
    (a / ".env").write_text("OTHER=keepme\nGHL_TOKEN=old-one\nexport GHL_TOKEN=older\n# a note\n")

    # ---- the catalog
    rc, out, _ = run(ring, a, "catalog")
    cat = json.loads(out)
    slugs = [p["provider"] for p in cat["providers"]]
    check("catalog lists the five providers", rc == 0 and slugs == ["gohighlevel", "heygen", "higgsfield", "kie", "submagic"], str(slugs))
    check("catalog carries the disclosure sentence word for word", cat["disclosure"] == "This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you.")
    check("every affiliate link has a plain route beside it", all("plain" in p["signup"] for p in cat["providers"] if p.get("signup")))
    check("GoHighLevel fills both names the tools read", cat["providers"][0]["env_names"] == ["GHL_TOKEN", "GHL_API_KEY", "GHL_LOCATION_ID"])
    rc, _, err = run(ring, a, "add", "stripe")
    check("an unknown provider is refused, with the list", rc != 0 and "gohighlevel" in err)
    rc, out, _ = run(ring, a, "list")
    check("an empty ring lists nothing", rc == 0 and json.loads(out)["saved"] == [] and not (ring / "keys.json").exists())

    # ---- the page
    rc, out, err = open_page(ring, a, base, "gohighlevel")
    first = json.loads(err.strip().splitlines()[-1]) if err.strip() else {}
    check("add opens a page on this computer only", rc == 0 and first.get("page", "").startswith("http://127.0.0.1:") and "?t=" in first["page"], err)
    check("add says nothing was saved yet", json.loads(out)["event"] == "none", out)
    port, token = page(ring)
    check("no token, no page", get(port, "/")[0] == 403 and get(port, "/?t=wrong")[0] == 403)
    check("another site's name is refused", get(port, f"/?t={token}", {"Host": "evil.example"})[0] == 403)
    code, html, hdr = get(port, f"/?t={token}")
    check("the page loads with the token", code == 200 and "Add your" in html and "Private Integrations" in html)
    check("the page cannot load or send anything elsewhere", "default-src 'none'" in hdr.get("Content-Security-Policy", "") and hdr.get("Cache-Control") == "no-store")
    check("the key box hides what is typed", 'f.secret ? "password"' in html)
    check("the page tells the member to leave messaging off", "Conversations off" in html)
    check("another site cannot post a key", post(port, token, {"GHL_TOKEN": GOOD, "GHL_LOCATION_ID": LOC}, headers={"Origin": "https://evil.example"})[0] == 403)

    _, r = post(port, token, {"GHL_TOKEN": "", "GHL_LOCATION_ID": LOC})
    check("an empty box is not saved", r == {"saved": False, "reason": "Private integration token is empty.", "can_force": False}, str(r))
    _, r = post(port, token, {"GHL_TOKEN": "sk-something-else-entirely", "GHL_LOCATION_ID": LOC})
    check("the wrong kind of key is caught before it is sent anywhere", not r["saved"] and "pit-" in r["reason"] and not r["can_force"])
    _, r = post(port, token, {"GHL_TOKEN": "pit-two words here", "GHL_LOCATION_ID": LOC})
    check("a key with a space in it is not saved", not r["saved"] and "no spaces" in r["reason"])
    _, r = post(port, token, {"GHL_TOKEN": "pit-bad-0000-0000-0000-000000000000", "GHL_LOCATION_ID": LOC})
    check("a token the provider refuses is not saved", not r["saved"] and r["can_force"] and "did not accept" in r["reason"], str(r))
    _, r = post(port, token, {"GHL_TOKEN": GOOD, "GHL_LOCATION_ID": "SomeOtherPlace"})
    check("a token from another sub-account is not saved", not r["saved"] and "does not belong" in r["reason"], str(r))
    check("nothing is on the ring after refusals", not (ring / "keys.json").exists())
    rc, out, _ = run(ring, a, "wait", "--timeout", "1")
    check("wait still says nothing saved", json.loads(out)["event"] == "none")

    _, r = post(port, token, {"GHL_TOKEN": f"  {GOOD}\n", "GHL_LOCATION_ID": f"https://app.gohighlevel.com/v2/location/{LOC}/settings/private-integrations"})
    check("a good key is saved, with the location picked out of a pasted address", r.get("saved") and r.get("works") is True, str(r))
    rc, out, _ = run(ring, a, "wait", "--timeout", "5")
    ev = json.loads(out)
    check("the session hears saved, with names only", ev["event"] == "saved" and ev["works"] is True and ev["names"] == ["GHL_LOCATION_ID", "GHL_TOKEN"], out)
    check("the page closes itself after a save", gone(ring))
    rc, out, _ = run(ring, a, "wait", "--timeout", "1")
    check("a second wait says the page is closed", json.loads(out)["event"] == "closed")

    saved = json.loads((ring / "keys.json").read_text())
    check("the ring holds the key and the location", saved["keys"]["gohighlevel"]["values"] == {"GHL_TOKEN": GOOD, "GHL_LOCATION_ID": LOC})
    if os.name != "nt":
        check("the ring and the .env are private files", stat.S_IMODE((ring / "keys.json").stat().st_mode) == 0o600 and stat.S_IMODE((a / ".env").stat().st_mode) == 0o600
              and stat.S_IMODE(ring.stat().st_mode) == 0o700)
    env = (a / ".env").read_text().splitlines()
    check("the .env keeps the member's other lines", env[0] == "OTHER=keepme" and "# a note" in env)
    check("the old key lines are replaced, not doubled", [ln for ln in env if "GHL_TOKEN" in ln] == [f"GHL_TOKEN={GOOD}"], str(env))
    check("the .env has every name the tools read", f"GHL_API_KEY={GOOD}" in env and f"GHL_LOCATION_ID={LOC}" in env)
    check("git is told to leave the .env alone", (a / ".gitignore").read_text().splitlines() == [".env"] and ev["gitignore_updated"] is True)

    # ---- a second folder, the list, the check
    rc, out, err = run(ring, plain, "add", "ghl", base=base)
    ev = json.loads(out)
    check("a key already on the ring fills a new folder without asking again", ev["event"] == "linked" and not (ring / "key-page.json").exists() and f"GHL_TOKEN={GOOD}" in (plain / ".env").read_text(), out)
    check("no .gitignore is made outside a git project", not (plain / ".gitignore").exists() and ev["gitignore_updated"] is False)
    rc, out, _ = run(ring, b, "list")
    li = json.loads(out)
    check("list shows the ending, never the key", li["saved"][0]["keys"] == {"GHL_TOKEN": "ends in " + GOOD[-4:], "GHL_LOCATION_ID": LOC} and li["saved"][0]["in_this_folder"] is False, out)
    check("list names what is not added yet", li["not_added_yet"] == ["heygen", "higgsfield", "kie", "submagic"])
    rc, out, _ = run(ring, b, "link", "gohighlevel", "kie")
    lk = json.loads(out)
    check("link fills what is on the ring and names what is missing", [x["event"] for x in lk] == ["linked", "missing"] and f"GHL_LOCATION_ID={LOC}" in (b / ".env").read_text())
    rc, out, _ = run(ring, b, "check", base=base)
    check("check says the key still works", json.loads(out)[0]["works"] is True, out)
    DEAD.add(GOOD)
    rc, out, _ = run(ring, b, "check", "gohighlevel", base=base)
    check("check notices a rotated key", json.loads(out)[0]["works"] is False and json.loads((ring / "keys.json").read_text())["keys"]["gohighlevel"]["works"] is False, out)
    rc, out, _ = run(ring, b, "check", base="http://127.0.0.1:9")
    check("an unreachable provider is 'not checked', and the last answer is kept", json.loads(out)[0]["works"] is None and json.loads((ring / "keys.json").read_text())["keys"]["gohighlevel"]["works"] is False, out)

    # ---- replacing, saving anyway, a provider that answers oddly
    rc, out, err = open_page(ring, a, base, "gohighlevel", "--replace")
    port, token = page(ring)
    check("the page says a key is already saved, by its ending only", "ends in " + GOOD[-4:] in get(port, f"/?t={token}")[1] and GOOD not in get(port, f"/?t={token}")[1])
    _, r = post(port, token, {"GHL_TOKEN": NOSCOPE, "GHL_LOCATION_ID": LOC})
    check("a token missing one permission is saved, and the page says which", r.get("saved") and r["works"] is True and "View Locations" in r["detail"], str(r))
    gone(ring)
    run(ring, a, "wait", "--timeout", "2")
    open_page(ring, a, base, "gohighlevel", "--replace")
    port, token = page(ring)
    _, r = post(port, token, {"GHL_TOKEN": ROTATED, "GHL_LOCATION_ID": "LocBroken"})
    check("an odd answer from the provider saves the key as not checked", r.get("saved") and r["works"] is None and ROTATED not in r["detail"], str(r))
    gone(ring)
    run(ring, a, "wait", "--timeout", "2")
    DEAD.add(ROTATED)
    open_page(ring, a, base, "gohighlevel", "--replace")
    port, token = page(ring)
    _, r = post(port, token, {"GHL_TOKEN": ROTATED, "GHL_LOCATION_ID": LOC}, anyway=True)
    check("the member can save a refused key anyway, marked as not working", r.get("saved") and r["works"] is False, str(r))
    gone(ring)
    rc, out, _ = run(ring, a, "wait", "--timeout", "2")
    check("the session hears that it does not work", json.loads(out)["works"] is False)

    # ---- the other providers
    open_page(ring, b, base, "kie")
    port, token = page(ring)
    html = get(port, f"/?t={token}")[1]
    check("an affiliate link sits next to its disclosure and a plain route", "kie.ai?ref=" in html and "P.disclosure" in html and '"plain": "https://kie.ai"' in html)
    _, r = post(port, token, {"KIE_API_KEY": "kie-wrong-1234567890"})
    check("a refused Kie.ai key is not saved", not r["saved"] and r["can_force"])
    _, r = post(port, token, {"KIE_API_KEY": KIE_GOOD})
    check("a good Kie.ai key is saved", r.get("saved") and r["works"] is True)
    gone(ring)
    check("the second key joins the same .env", f"KIE_API_KEY={KIE_GOOD}" in (b / ".env").read_text() and f"GHL_LOCATION_ID={LOC}" in (b / ".env").read_text())
    open_page(ring, b, base, "higgsfield")
    port, token = page(ring)
    _, r = post(port, token, {"HIGGSFIELD_API_KEY": "hf-key-123456789012", "HIGGSFIELD_API_SECRET": ""})
    check("a two-part key needs both parts", not r["saved"] and "API secret is empty" in r["reason"])
    _, r = post(port, token, {"HIGGSFIELD_API_KEY": "hf-key-123456789012", "HIGGSFIELD_API_SECRET": "hf-secret-123456789012"})
    check("a provider with no safe check is saved as not checked, and says so", r.get("saved") and r["works"] is None and "no safe way" in r["detail"], str(r))
    gone(ring)
    open_page(ring, b, base, "heygen")
    rc, out, _ = run(ring, b, "stop")
    check("stop closes the page", "Stopped" in out and gone(ring))
    rc, out, _ = run(ring, b, "wait", "--timeout", "1")
    check("a closed page with nothing saved says so", json.loads(out)["event"] == "closed")

    # ---- the provider's own tools, for Claude Code and Codex
    fake, chome, log = tmp / "bin", tmp / "codex-home", tmp / "claude-calls.txt"
    fake.mkdir(); chome.mkdir()
    (fake / "claude").write_text(f"#!/bin/sh\necho \"$@\" >> {log}\nexit 0\n")
    (fake / "claude").chmod(0o755)
    (chome / "config.toml").write_text('model = "x"\n\n[mcp_servers.other]\nurl = "https://example.com/mcp"\n')

    def tool(*args, path=True):
        env = dict(os.environ, BUILDROOM_KEYRING_DIR=str(ring), CODEX_HOME=str(chome), PATH=(str(fake) + os.pathsep if path else "") + "/usr/bin:/bin")
        p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=env, cwd=str(b), timeout=60)
        SEEN.append(p.stdout + p.stderr)
        return p.returncode, p.stdout, p.stderr
    rc, out, _ = tool("connect", "kie")
    check("a provider with no live tools cannot be connected", rc != 0)
    rc, out, _ = tool("connect", "ghl")
    res = {r["client"]: r for r in json.loads(out)["results"]}
    calls = log.read_text() if log.exists() else ""
    check("connect adds GoHighLevel's tools to Claude Code for this folder only", res["claude"]["ok"] and "add --transport http --scope local gohighlevel https://services.leadconnectorhq.com/mcp/" in calls
          and "locationId: " + LOC in calls, calls[:200])
    cfg = (chome / "config.toml").read_text()
    try:
        import tomllib
        parsed = tomllib.loads(cfg)["mcp_servers"]
    except ImportError:
        parsed = None
    check("connect adds it to Codex's config and keeps what was there", res["codex"]["ok"] and "[mcp_servers.other]" in cfg and "[mcp_servers.gohighlevel]" in cfg
          and (parsed is None or (parsed["gohighlevel"]["http_headers"]["locationId"] == LOC and parsed["other"]["url"] == "https://example.com/mcp")), cfg[:300])
    check("connect says the Codex route is not yet confirmed", "not been confirmed" in res["codex"]["detail"])
    if os.name != "nt":
        check("Codex's config becomes a private file once it holds a key", stat.S_IMODE((chome / "config.toml").stat().st_mode) == 0o600)
    tool("connect", "ghl", "--to", "codex")
    check("connecting twice does not double the entry", (chome / "config.toml").read_text().count("[mcp_servers.gohighlevel]") == 1)
    rc, out, _ = tool("connect", "ghl", "--to", "claude", path=False)
    check("no claude command is reported, not an error", rc == 0 and json.loads(out)["results"][0]["ok"] is False and "not found" in json.loads(out)["results"][0]["detail"])
    rc, out, _ = tool("disconnect", "ghl")
    check("disconnect removes it from both and leaves the member's own servers", "gohighlevel" not in (chome / "config.toml").read_text() and "[mcp_servers.other]" in (chome / "config.toml").read_text()
          and "remove gohighlevel --scope local" in log.read_text())
    (chome / "config.toml").write_text('[mcp_servers.gohighlevel]\nurl = "https://mine.example/mcp"\n')
    rc, out, _ = tool("connect", "ghl", "--to", "codex")
    check("a server of the same name the member added themselves is left alone", json.loads(out)["results"][0]["ok"] is False and "mine.example" in (chome / "config.toml").read_text())
    SEEN.append(log.read_text().replace(json.loads((ring / "keys.json").read_text())["keys"]["gohighlevel"]["values"]["GHL_TOKEN"], ""))

    # ---- removing
    rc, _, err = run(ring, b, "remove", "kie")
    check("remove asks first", rc != 0 and "--yes" in err and "kie" in json.loads((ring / "keys.json").read_text())["keys"])
    rc, out, _ = run(ring, b, "remove", "kie", "--yes")
    benv = (b / ".env").read_text()
    check("remove takes the key off the ring and out of this folder", json.loads(out)["event"] == "removed" and "kie" not in json.loads((ring / "keys.json").read_text())["keys"]
          and "KIE_API_KEY" not in benv and "GHL_LOCATION_ID" in benv and "HIGGSFIELD_API_KEY" in benv)
    rc, out, _ = run(ring, b, "remove", "ghl", "--yes")
    check("removing GoHighLevel clears both of its names", "GHL_API_KEY" not in (b / ".env").read_text() and "GHL_TOKEN" not in (b / ".env").read_text())

    # ---- damage
    (ring / "keys.json").write_text("{ not json")
    rc, _, err = run(ring, b, "list")
    check("a damaged ring file is reported and left alone", rc != 0 and "cannot be read" in err and (ring / "keys.json").read_text() == "{ not json")

    # ---- nothing ever printed a key
    everything = "\n".join(SEEN)
    check("no command and no page answer ever carried a key", not any(s in everything for s in SECRETS), str([s[:8] for s in SECRETS if s in everything]))
    src = SCRIPT.read_text(encoding="utf-8")
    std = {"shutil", "argparse", "http", "json", "os", "re", "secrets", "subprocess", "sys", "tempfile", "threading", "time", "urllib", "webbrowser", "datetime", "pathlib"}
    used = {n.name.split(".")[0] for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Import) for n in node.names} | \
           {node.module.split(".")[0] for node in ast.walk(ast.parse(src)) if isinstance(node, ast.ImportFrom)}
    check("standard library only", used <= std, str(used - std))
    check("no key is ever a command-line argument", "--token" not in src and "--key" not in src)
    check("no dashes or British spelling in what the member reads", "—" not in src and "–" not in src and "colour" not in src)

    srv.shutdown()
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
