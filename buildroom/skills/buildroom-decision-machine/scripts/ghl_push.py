#!/usr/bin/env python3
"""GHL push: put a Build Room funnel build into GoHighLevel, as far as the API allows.

What the API does (pushed by this script)      What it does not do (left to the browser build)
  tags                                            workflows and their steps
  custom fields                                   calendars
  email templates (builder)  [endpoint unverified]  pipeline/stage creation  [read-only here]
  pipeline + stage check (read)                   publishing a workflow

The browser build sheet this script prints is what the agent follows in Claude Code or
Codex with a browser (Claude in Chrome or Playwright) to build the workflows, then the
launch test proves it. Nothing here sends a message to a contact.

Usage
  ghl_push.py --dry-run build.json           print every request it would make; call nothing
  ghl_push.py --probe                        one GET on the location to confirm key, location id, scopes
  ghl_push.py build.json [--out report.json] push tags, fields, templates; check pipeline; print the build sheet

Environment (the member's .env; never printed)
  GHL_API_KEY        private integration key for the sub-account
  GHL_LOCATION_ID    the sub-account (location) id
  GHL_API_BASE       default https://services.leadconnectorhq.com
  GHL_API_VERSION    default 2021-07-28

build.json
  {
   "funnel": "Install Call funnel",
   "tags": ["warm-lead", "status-new-lead", "install-call-booked"],
   "custom_fields": [{"name": "Babysitting score", "dataType": "NUMERICAL"}, ...],
   "pipeline": {"name": "Install Pipeline", "stages": ["New Lead", "Call Booked", "Showed", "Committed", "Paid"]},
   "emails": [{"name": "Install Call Sequence 01 Welcome", "subject": "...", "html": "<p>...</p>",
               "day": 0, "send_at": "immediately"}, ...],
   "workflows": [{"name": "WF-1 Babysitting Test Opt-In",
                  "trigger": "Form submitted: Babysitting Test",
                  "steps": ["Add tag warm-lead", "Add tag status-new-lead", "Wait 1 day",
                            "Send email: Install Call Sequence 01 Welcome", "Wait 2 days", "..."],
                  "exit": "Remove from workflow when tag install-call-booked is added"}],
   "launch_test": ["Submit the form with your own email", "Confirm tags applied", "..."]
  }

Schema status (2026-10-10). Tags and custom fields follow the documented v2 shapes
(POST /locations/{id}/tags {name}; POST /locations/{id}/customFields {name, dataType, ...}).
The email builder create endpoint (POST /emails/builder) is reported, not confirmed from this
build sandbox: its request shape lives in EMAIL_SHAPE below; --probe tells you which calls
succeeded and the vendor's error text names any field to fix. Pipelines are read with
GET /opportunities/pipelines?locationId=; missing stages are reported for the browser build.
"""
import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

BASE_DEFAULT = "https://services.leadconnectorhq.com"
VERSION_DEFAULT = "2021-07-28"

# Email builder shape: UNVERIFIED. Adjust after --probe if the vendor error names a field.
EMAIL_SHAPE = {"path": "/emails/builder", "type": "html",
               "f_location": "locationId", "f_title": "title", "f_type": "type",
               "f_html": "dnd" , "f_subject": "subject"}


def env():
    key = os.environ.get("GHL_API_KEY"); loc = os.environ.get("GHL_LOCATION_ID")
    if not key or not loc:
        sys.exit("GHL_API_KEY and GHL_LOCATION_ID must be set (keep them in .env). Nothing was pushed.")
    return key, loc, os.environ.get("GHL_API_BASE", BASE_DEFAULT).rstrip("/"), os.environ.get("GHL_API_VERSION", VERSION_DEFAULT)


def call(method, url, key, version, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}", "Version": version,
                                          "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:1500]}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, {"error": f"could not reach {url}: {getattr(e, 'reason', e)}"}


# ---------- request builders ----------
def req_tags(loc, tags):
    return [("POST", f"/locations/{loc}/tags", {"name": t}) for t in tags]

def req_fields(loc, fields):
    out = []
    for f in fields:
        body = {"name": f["name"], "dataType": f.get("dataType", "TEXT")}
        for k in ("placeholder", "options", "position", "model"):
            if k in f: body[k] = f[k]
        out.append(("POST", f"/locations/{loc}/customFields", body))
    return out

def req_emails(loc, emails):
    S = EMAIL_SHAPE; out = []
    for e in emails:
        body = {S["f_location"]: loc, S["f_title"]: e["name"], S["f_type"]: S["type"],
                S["f_subject"]: e.get("subject", ""), S["f_html"]: e.get("html", "")}
        out.append(("POST", S["path"], body))
    return out

def req_pipeline_read(loc):
    return [("GET", f"/opportunities/pipelines?locationId={urllib.parse.quote(loc)}", None)]


def build_sheet(b, pipeline_report=None):
    L = []
    L.append(f"BROWSER BUILD SHEET — {b.get('funnel','funnel')}")
    L.append("Build in GoHighLevel in this order. Names are exact; the launch test checks them.")
    if pipeline_report:
        L.append(""); L.append("PIPELINE"); L += [f"  {x}" for x in pipeline_report]
    for w in b.get("workflows", []):
        L.append(""); L.append(f"WORKFLOW: {w['name']}")
        L.append(f"  Trigger: {w.get('trigger','(set the trigger)')}")
        for i, s in enumerate(w.get("steps", []), 1):
            L.append(f"  {i:>2}. {s}")
        if w.get("exit"): L.append(f"  Exit: {w['exit']}")
        L.append("  Publish the workflow (Draft never fires).")
    if b.get("launch_test"):
        L.append(""); L.append("LAUNCH TEST (one real pass per path, with your own contact)")
        for i, t in enumerate(b["launch_test"], 1): L.append(f"  {i}. {t}")
    L.append(""); L.append("Record in §6 CRM build: tags/fields pushed · workflows built · launch test passed · date.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", nargs="?")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out"); ap.add_argument("--skip-emails", action="store_true", help="push tags/fields only")
    a = ap.parse_args()

    if a.probe:
        key, loc, base, ver = env()
        st, r = call("GET", f"{base}/locations/{loc}", key, ver)
        print(json.dumps({"GET /locations/{id}": {"status": st, "ok": st == 200,
                          "name": (r.get("location") or {}).get("name") if st == 200 else None,
                          "error": r.get("error")}}, indent=2))
        st2, r2 = call("GET", f"{base}/locations/{loc}/tags", key, ver)
        print(json.dumps({"GET /locations/{id}/tags": {"status": st2, "count": len(r2.get("tags", [])) if st2 == 200 else None,
                          "error": r2.get("error")}}, indent=2))
        st3, r3 = call("GET", f"{base}{EMAIL_SHAPE['path']}?locationId={urllib.parse.quote(loc)}&limit=1", key, ver)
        print(json.dumps({"GET " + EMAIL_SHAPE['path']: {"status": st3, "error": r3.get("error"),
                          "note": "200 means the email builder endpoint and scope exist; a 401/403 means add the emails scope to the private integration; a 404 means fix EMAIL_SHAPE.path"}}, indent=2))
        print("Nothing was created.", file=sys.stderr)
        return

    if not a.build: ap.error("build.json is required unless --probe")
    b = json.load(open(a.build, encoding="utf-8"))
    loc = os.environ.get("GHL_LOCATION_ID", "LOCATION_ID")
    plan = req_tags(loc, b.get("tags", [])) + req_fields(loc, b.get("custom_fields", []))
    if not a.skip_emails: plan += req_emails(loc, b.get("emails", []))
    plan += req_pipeline_read(loc)

    if a.dry_run:
        print(json.dumps([{"method": m, "path": p, "body": body} for m, p, body in plan], indent=2))
        print(); print(build_sheet(b)); return

    key, loc, base, ver = env()
    report = {"funnel": b.get("funnel"), "created": [], "skipped": [], "failed": [], "pipeline": []}
    # existing tags/fields so the push is idempotent
    st, r = call("GET", f"{base}/locations/{loc}/tags", key, ver)
    have_tags = {t.get("name", "").lower() for t in r.get("tags", [])} if st == 200 else set()
    st, r = call("GET", f"{base}/locations/{loc}/customFields", key, ver)
    have_fields = {f.get("name", "").lower() for f in r.get("customFields", [])} if st == 200 else set()

    for m, p, body in plan:
        if m == "GET":
            st, r = call(m, f"{base}{p}", key, ver)
            if st == 200:
                want = b.get("pipeline") or {}
                pipes = r.get("pipelines", [])
                match = next((x for x in pipes if x.get("name", "").lower() == want.get("name", "").lower()), None) if want else None
                if not want:
                    report["pipeline"].append("no pipeline requested")
                elif not match:
                    report["pipeline"].append(f"CREATE pipeline '{want['name']}' with stages: " + " → ".join(want.get("stages", [])))
                else:
                    have = [s.get("name") for s in match.get("stages", [])]
                    missing = [s for s in want.get("stages", []) if s not in have]
                    report["pipeline"].append(f"pipeline '{want['name']}' exists (id {match.get('id')}); stages present: {have}")
                    if missing: report["pipeline"].append("ADD stages: " + ", ".join(missing))
            else:
                report["pipeline"].append(f"could not read pipelines (HTTP {st}): {r.get('error')}")
            continue
        name = body.get("name") or body.get(EMAIL_SHAPE["f_title"])
        kind = "tag" if p.endswith("/tags") else ("field" if p.endswith("/customFields") else "email")
        if kind == "tag" and name.lower() in have_tags: report["skipped"].append(f"tag {name} (exists)"); continue
        if kind == "field" and name.lower() in have_fields: report["skipped"].append(f"field {name} (exists)"); continue
        st, r = call(m, f"{base}{p}", key, ver, body)
        if 200 <= st < 300: report["created"].append(f"{kind} {name}")
        else: report["failed"].append({"kind": kind, "name": name, "status": st, "error": r.get("error")})

    sheet = build_sheet(b, report["pipeline"])
    report["browser_build_sheet"] = sheet
    text = json.dumps(report, indent=2)
    if a.out: open(a.out, "w", encoding="utf-8").write(text)
    print(f"created {len(report['created'])} · skipped {len(report['skipped'])} · failed {len(report['failed'])}")
    for f in report["failed"]: print("  FAILED", f["kind"], f["name"], "HTTP", f["status"], (f["error"] or "")[:200])
    print(); print(sheet)
    if report["failed"] and any(f["kind"] == "email" for f in report["failed"]):
        print("\nEmail template pushes failed: fix EMAIL_SHAPE at the top of ghl_push.py from the vendor's error text, "
              "or rerun with --skip-emails and paste the emails into the workflow steps in the browser build.", file=sys.stderr)


if __name__ == "__main__":
    main()
