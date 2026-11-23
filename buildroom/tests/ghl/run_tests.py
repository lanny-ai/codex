#!/usr/bin/env python3
"""GoHighLevel snapshot: the build spec and the placeholder list Build Room OS reads must agree.

Usage:  python3 buildroom/tests/ghl/run_tests.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "rollout/ghl-snapshot"
SKA = ROOT / "skills/buildroom-autopilot"
sys.dont_write_bytecode = True
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def main():
    j = json.loads((D / "placeholders.json").read_text())
    spec = (D / "SNAPSHOT-SPEC.md").read_text()
    ps = j["placeholders"]
    keys = [p["key"] for p in ps]
    check("list: every key is unique, lower case, and starts with br_", len(keys) == len(set(keys)) and all(re.fullmatch(r"br_[a-z0-9_]+", k) for k in keys))
    check("list: every entry has a group, a label, a source and a known type",
          all(p.get("group") and p.get("label") and p.get("source") and p.get("type") in ("text", "long", "url", "email") and isinstance(p.get("required"), bool)
              and isinstance(p.get("fact"), bool) for p in ps))
    in_spec = set(re.findall(r"^\| `(br_[a-z0-9_]+)` \|", spec, re.M))
    check("spec and list name exactly the same custom values", in_spec == set(keys), f"only in spec {sorted(in_spec - set(keys))[:5]}, only in list {sorted(set(keys) - in_spec)[:5]}")
    check("spec states the same count as the list", f"The {len(ps)} in the tables below" in spec)
    check("spec and list carry the same version, and the version key is not a fillable value",
          f"_Version {j['version']} " in spec and j["version_key"] == "br_snapshot_version" and "br_snapshot_version" not in keys and f"set to `{j['version']}`" in spec)
    facts = {p["key"] for p in ps if p["fact"]}
    must_be_facts = {k for k in keys if re.search(r"price|value$|guarantee|urgency|proof|call_length|magnet_url|offer_structure|business_name|owner_", k)}
    check("list: prices, value, guarantee, urgency, proof, links and names are facts, never drafted", must_be_facts <= facts, sorted(must_be_facts - facts))
    check("list: no drafted-by-nature copy is locked as a fact", not any(re.search(r"headline|hook|bullet|button|faq|_body$|_subject$", k) for k in facts), sorted(facts))
    row = {m.group(1): (m.group(2).strip(), m.group(3).strip()) for m in re.finditer(r"^\| `(br_[a-z0-9_]+)` \|[^|]*\|[^|]*\| ([^|]*)\| ([^|]*)\|$", spec, re.M)}
    check("spec: the must-have and fact columns match the list", all(row[p["key"]] == ("yes" if p["required"] else "", "yes" if p["fact"] else "") for p in ps))
    check("list: required values come before optional ones in every numbered run",
          all(not (b["required"] and not a["required"]) for a, b in zip(ps, ps[1:])
              if re.sub(r"\d+$", "", a["key"]) == re.sub(r"\d+$", "", b["key"]) and a["key"] != b["key"]))
    emails = sorted({re.sub(r"_(subject|preview|body)$", "", k) for k in keys if k.startswith("br_em_")})
    check("list: every email has a subject and a body", len(emails) == 14 and all(e + "_subject" in keys and e + "_body" in keys for e in emails), emails)
    check("spec: fourteen templates and six workflows, all left in draft", "Fourteen email templates" in spec and "Six workflows, all left in Draft" in spec and spec.count("| `BR WF") == 6)
    check("spec: an empty optional email is never sent", "must not send" in spec)
    check("spec: no text messages, no payment, nothing published", "No SMS anywhere." in spec and "Taking payment" in spec and "publishes nothing" in spec)
    check("spec: says plainly that it is unproven and lists what to verify", "Nothing in this spec has been run against a real GoHighLevel account." in spec and spec.count("\n") > 100
          and len(re.findall(r"^\d\. ", spec[spec.index("## To verify in a test account"):spec.index("## Checking the snapshot")], re.M)) == 8)
    check("spec: a fact is never drafted, and blanks are reported", "A fact is never drafted." in spec and "left empty and reported" in spec)
    check("spec: Build Room OS refuses to push without the must-haves or a matching version", "Refuses to push if a \"must have\" value is missing" in spec and "stops if it is missing or does not match" in spec)
    check("spec: no long dashes", "—" not in spec and "–" not in spec)
    check("spec: no key, link or account detail of any member", not re.search(r"pit-[a-z0-9]|eyJ[A-Za-z0-9]|locationId=|@gmail|@yahoo", spec))
    # ---- the values file: from a finished Autopilot run to a file ready to load ------------------
    import subprocess, tempfile
    SKA = D.parent.parent / "skills/buildroom-autopilot"
    GV, AP = SKA / "scripts/ghl_values.py", SKA / "scripts/autopilot.py"
    run = lambda *a: (lambda p: (p.returncode, p.stdout + p.stderr))(subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True))  # noqa: E731
    check("values: the skill carries the same list the snapshot is built from", (SKA / "references/ghl-placeholders.json").read_text() == (D / "placeholders.json").read_text())
    code, out = run(GV, "template")
    check("values: the worksheet lists every value with its limit and whether it is a fact", code == 0 and all(k + ":" in out for k in keys) and "FACT: member or files only" in out and f"{len(ps)} custom values" in out)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        A = t / "autopilot"
        (A / "drafts").mkdir(parents=True)
        tpl = (D.parent.parent / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
        (t / "BUILDROOM_BUSINESS_FILE.md").write_text(tpl.replace("- **Current price / price range:**", "- **Current price / price range:** $4,800")
            .replace("separated by semicolons):", "separated by semicolons): “Featured in Ceramics Monthly”"))
        run(AP, "plan", "--dir", A, "--readiness", "80", "--no-web")
        run(AP, "decide", "--dir", A, "--key", "guarantee", "--value", "none")
        vf = t / "values.json"
        c, d_, f_ = (lambda v: {"v": v, "basis": "confirmed"}), (lambda v: {"v": v, "basis": "drafted"}), (lambda v: {"v": v, "basis": "files"})
        good = {"br_business_name": c("Kiln & Co"), "br_owner_name": c("Marcus Bell"), "br_owner_first_name": c("Marcus"), "br_optin_headline": d_("Classes that fill"),
                "br_offer_price": c("$4,800")} if "br_offer_price" in keys else {"br_business_name": c("Kiln & Co"), "br_optin_headline": d_("Classes that fill")}
        def chk(v):
            vf.write_text(json.dumps(v))
            return run(GV, "check", "--dir", A, vf)
        code, out = chk(good)
        check("values: honest values pass, and the must-haves still missing are listed", code == 0 and "0 to fix" in out and "Must-have values still missing" in out and "br_magnet_url" in out, out[-400:])
        fact_key = next(p["key"] for p in ps if p["fact"] and p["type"] == "text" and p["key"] not in good)
        check("values: a fact is never drafted", "this is a fact" in chk({**good, fact_key: d_("Something plausible")})[1])
        check("values: an unknown key, an empty value and a leftover blank are refused", all(x in chk({**good, "br_made_up": d_("x"), "br_optin_subheadline": d_(" "), "br_optin_hook": d_("Book here: [needs you: a booking link]")})[1]
              for x in ("not a value the snapshot has", "Leave a value out", "still carries a tag or a blank")))
        check("values: a value longer than its page element is refused", "the page element holds 120" in chk({**good, "br_optin_headline": d_("x" * 121)})[1])
        check("values: a link must be a full https link", "full https:// link" in chk({**good, "br_magnet_url": c("mysite.com/guide")})[1])
        out = chk({**good, "br_optin_hook": d_("As featured in Ceramics Monthly. Most studios add $12,000. Results guaranteed.")})[1]
        check("values: a retired line, a figure nobody confirmed and a guarantee the member does not have are refused", "retired" in out and "$12,000" in out and "offers a guarantee" in out, out)
        vf.write_text(json.dumps({**good, "br_optin_hook": d_("We double your enrollment.")}))
        code, out = run(GV, "export", "--dir", A, vf, t / "out")
        check("export: nothing is written while something must be fixed", code != 0 and not (t / "out").exists(), out)
        vf.write_text(json.dumps(good))
        code, out = run(GV, "export", "--dir", A, vf, t / "out")
        cv = json.loads((t / "out/custom_values.json").read_text())
        sheet = (t / "out/GHL_Values_Review.md").read_text()
        check("export: writes the values, a csv with merge tags, and a review sheet", code == 0 and cv["values"]["br_business_name"] == "Kiln & Co" and cv["snapshot_version"] == j["version"]
              and "{{ custom_values.br_optin_headline }}" in (t / "out/custom_values.csv").read_text())
        check("export: a file with a must-have missing says it is not complete", cv["complete"] is False and "must-have values are still missing" in sheet and "## Still needed from you" in sheet)
        check("export: the sheet tags every line and says nothing was sent", "drafted for you" in sheet and "· yours ·" in sheet and "Nothing has been sent to GoHighLevel" in sheet and "## Left empty" in sheet
              and "—" not in sheet and "–" not in sheet)
    gsrc = GV.read_text()
    check("values: standard library only, and it connects to nothing", not any(x in gsrc for x in ("requests", "urllib", "socket", "http.client", "subprocess")))
    gref = (SKA / "references/ghl-values.md").read_text()
    check("skill: only on request, after the handover, and nothing is sent", "Prepare my GoHighLevel values" in (SKA / "SKILL.md").read_text() and "It does not connect to GoHighLevel" in gref
          and "A fact is never drafted." in gref and "Never fill a must-have to make the file complete." in gref and "—" not in gref and "–" not in gref)
    check("spec: says which steps are built and which are not", "are not built yet" in spec and "ghl_values.py" in spec)
    import importlib.util
    _sp = importlib.util.spec_from_file_location("ghl_values_under_test", GV)
    gv_mod = importlib.util.module_from_spec(_sp)
    _sp.loader.exec_module(gv_mod)
    check("values: the ordinary word \"your\" is not mistaken for a blank, and a blank in capitals still is",
          not gv_mod.LEFTOVER.search("Know what your practice really made. Your scorecard is here.") and gv_mod.LEFTOVER.search("Call YOUR NAME today")
          and gv_mod.LEFTOVER.search("see YOUR-LINK") and gv_mod.LEFTOVER.search("{{contact.name}}") and gv_mod.LEFTOVER.search("tbd"))
    push_tests()
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


def push_tests():
    """The push, against a stand-in for GoHighLevel that runs on this computer. Nothing here goes online."""
    import http.server, os, subprocess, tempfile, threading
    PUSH = SKA / "scripts/ghl_push.py"
    state = {"values": {}, "n": 0, "calls": [], "lag": 0, "stale": None, "deny": None, "busy": 0}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

        def _go(self, method):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}") if method in ("POST", "PUT") else None
            state["calls"].append((method, self.path, self.headers.get("Authorization"), self.headers.get("Version")))
            if self.headers.get("Authorization") != "Bearer pit-test-token":
                return self._send(401, {"message": "Invalid Private Integration token", "statusCode": 401})
            if not self.path.startswith("/locations/LOC1234567890"):
                return self._send(403, {"message": "This location is not accessible from this token!", "statusCode": 403})
            if state["deny"] and method in state["deny"]:
                return self._send(403, {"message": "The token is not authorized for this scope.", "statusCode": 403})
            if state["busy"] and method != "GET":
                state["busy"] -= 1
                return self._send(429, {"message": "Too many requests"})
            if method == "GET" and self.path.endswith("/customValues"):
                if state["lag"] and state["stale"] is not None:      # the real list lags a write by a few seconds
                    state["lag"] -= 1
                    return self._send(200, {"customValues": state["stale"]})
                return self._send(200, {"customValues": list(state["values"].values())})
            if method == "GET":
                return self._send(200, {"location": {"id": "LOC1234567890", "name": "Test Account"}})
            if method == "POST":
                state["n"] += 1
                v = {"id": f"id{state['n']}", "name": body["name"], "value": body["value"]}
                state["values"][v["id"]] = v
                return self._send(201, {"customValue": v})
            if method == "PUT":
                vid = self.path.rsplit("/", 1)[1]
                state["values"][vid].update(value=body["value"])
                return self._send(200, {"customValue": state["values"][vid]})
            self._send(405, {"message": "no"})

        def do_GET(self): self._go("GET")
        def do_POST(self): self._go("POST")
        def do_PUT(self): self._go("PUT")
        def do_DELETE(self): self._go("DELETE")

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    with tempfile.TemporaryDirectory() as td:
        w = Path(td)
        (w / "ghl").mkdir()
        vals = {"br_business_name": "Test Vet Staffing", "br_optin_headline": "Know what your practice really made", "br_offer_price": "$4,500",
                "br_em_delivery_body": "Hello,\n\nHere it is.\n\nDana"}

        def write(values=vals, complete=True):
            (w / "ghl/custom_values.json").write_text(json.dumps({"snapshot_version": "1.0", "complete": complete, "values": values}))

        def run(*a, env_file=True, **env):
            if env_file:
                (w / ".env").write_text(f"# keys\nGHL_TOKEN='pit-test-token'\nGHL_LOCATION_ID=LOC1234567890\nGHL_API_BASE={base}\n")
            elif (w / ".env").exists():
                (w / ".env").unlink()
            e = {k: v for k, v in os.environ.items() if not k.startswith("GHL_")}
            r = subprocess.run([sys.executable, "-B", str(PUSH), *a, "--pause", "0"] if a[0] == "push" else [sys.executable, "-B", str(PUSH), *a],
                               capture_output=True, text=True, cwd=w, env={**e, "PYTHONDONTWRITEBYTECODE": "1", **env})
            return r.returncode, r.stdout + r.stderr
        write()
        code, out = run("plan", "ghl")
        check("push plan: reads the account, shows what would be added, and changes nothing", code == 0 and "Would create 4, update 0" in out and "Nothing was changed" in out
              and "Test Account" in out and not state["values"] and all(c[0] == "GET" for c in state["calls"]), out)
        check("push plan: an account with no Build Room values is flagged as probably having no snapshot", "snapshot is probably not loaded" in out)
        code, out = run("push", "ghl")
        check("push: without the member's go-ahead it shows the plan and writes nothing", code != 0 and "only after they have seen the plan and said go" in out and not state["values"], out)
        code, out = run("push", "ghl", "--yes")
        got = {v["name"]: v["value"] for v in state["values"].values()}
        check("push: every value is created under its own key, text and line breaks intact", code == 0 and got == vals and "4 written and confirmed" in out, out)
        rep = json.loads((w / "ghl/push_report.json").read_text())
        md = (w / "ghl/GHL_Push_Report.md").read_text()
        check("push: the report says what was written, what it did not do and what only the member can do", rep["created"] == list(vals) and not rep["failed"]
              and "did not publish a page, send an email or switch a workflow on" in md and "Send yourself a test" in md and "—" not in md and "–" not in md, rep)
        check("push: the token is sent only in the header and never written to the report or the screen", "pit-test-token" not in out + md + json.dumps(rep)
              and all(c[2] == "Bearer pit-test-token" and c[3] == "2021-07-28" for c in state["calls"]))
        state["values"]["x1"] = {"id": "x1", "name": "their_own_value", "value": "keep me"}
        state["values"]["x2"] = {"id": "x2", "name": "br_optin_button", "value": "Already here"}
        write({**vals, "br_optin_headline": "A new headline"})
        code, out = run("plan", "ghl")
        check("push plan: a changed value is shown old and new, and values not in the file are left alone", "Would create 0, update 1, leave 3" in out
              and "now:  Know what your practice really made" in out and "to:   A new headline" in out and "left exactly as they are" in out, out)
        state["stale"], state["lag"] = [dict(v) for v in state["values"].values()], 2
        code, out = run("push", "ghl", "--yes")
        now = {v["name"]: v["value"] for v in state["values"].values()}
        check("push: an update changes that value only; nothing is deleted and other values are untouched", code == 0 and now["br_optin_headline"] == "A new headline"
              and now["their_own_value"] == "keep me" and now["br_optin_button"] == "Already here" and len(now) == 6
              and not any(c[0] == "DELETE" for c in state["calls"]), out)
        check("push: the read-back waits out the account's lag instead of reporting a failure", "1 written and confirmed" in out and "0 not confirmed" in out, out)
        write(vals, complete=False)
        code, out = run("push", "ghl", "--yes")
        check("push: a file marked not complete is refused unless the member chooses a partial push", code != 0 and "not complete" in out and "--partial" in out, out)
        code, out = run("push", "ghl", "--yes", "--partial")
        check("push: a partial push goes through when chosen", code == 0, out)
        write({**vals, "br_made_up": "x"})
        code, out = run("plan", "ghl")
        check("push: a value that is not on the snapshot's list is refused before anything is read or written", code != 0 and "br_made_up: not a value the snapshot has" in out, out)
        write({**vals, "br_optin_headline": "Call [needs you] today"})
        code, out = run("plan", "ghl")
        check("push: a value still carrying a tag is refused", code != 0 and "still carries a tag" in out, out)
        write({**vals, "br_offer_price": "x" * 61})
        code, out = run("plan", "ghl")
        check("push: a value too long for its page element is refused", code != 0 and "61 characters" in out, out)
        write()
        code, out = run("plan", "ghl", GHL_TOKEN="pit-wrong")
        check("push: a rejected token is explained in plain words", code != 0 and "did not accept the token" in out and "pit-wrong" not in out, out)
        code, out = run("plan", "ghl", GHL_LOCATION_ID="OTHER123456789")
        check("push: a token for a different account is explained in plain words", code != 0 and "different sub-account" in out, out)
        code, out = run("plan", "ghl", env_file=False)
        check("push: with no connection saved it says what is needed, and never to paste a token into the chat", code != 0 and "GHL_TOKEN and GHL_LOCATION_ID" in out
              and "never ask them to paste a token into the chat" in out, out)
        write({**vals, "br_optin_headline": "Third headline"})
        state["deny"] = ("PUT", "POST")
        code, out = run("push", "ghl", "--yes")
        check("push: a token without permission to edit is reported, and the run stops instead of failing on every value", code != 0 and "needs View and Edit Custom Values" in out
              and "FAILED  br_optin_headline" in out, out)
        state["deny"], state["busy"] = None, 1
        code, out = run("push", "ghl", "--yes")
        check("push: a 'too busy' answer is retried, not reported as a failure", code == 0 and "1 written and confirmed" in out, out)
    srv.shutdown()
    psrc = PUSH.read_text()
    check("push: standard library only, it talks to GoHighLevel's API and nowhere else, and it never deletes", "requests" not in psrc and "subprocess" not in psrc
          and set(re.findall(r"https://([\w.]+)", psrc)) == {"services.leadconnectorhq.com"} and '"DELETE"' not in psrc)
    check("push: the token is never a command-line argument", "--token" not in psrc and "add_argument(\"token\"" not in psrc)
    sk = (SKA / "SKILL.md").read_text()
    gref = (SKA / "references/ghl-values.md").read_text()
    check("skill: the push is a separate step, on request, after the member has seen the plan, and the token never goes in the chat", "Push my build to GoHighLevel" in sk
          and "after they have seen the plan" in sk and "never ask for it in the chat" in sk and "Never ask a member to paste a token into the chat" in gref
          and "ghl_push.py plan" in gref and "It never deletes a value" in gref and "—" not in gref and "–" not in gref)
    spec = (ROOT / "rollout/ghl-snapshot/SNAPSHOT-SPEC.md").read_text()
    check("spec: the push is recorded as built and proven, and the snapshot as not built", "ghl_push.py" in spec and "proven against a live test sub-account" in spec and "are not built yet" in spec)


if __name__ == "__main__":
    main()
