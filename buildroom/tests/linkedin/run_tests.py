#!/usr/bin/env python3
"""LinkedIn Engine tests: pipeline rules, pacing, privacy, the scorecard reader and the renderer.

Local only: synthetic files, no network, no LinkedIn. The renderer checks run only when Node and
Playwright are available (NODE_PATH or a local node_modules).

Usage:  python3 buildroom/tests/linkedin/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-linkedin"
S = SK / "scripts"
sys.path.insert(0, str(HERE))
from xlsx_fixture import write_xlsx  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def run(args, cwd, ok_codes=(0,), env=None):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, env=env)
    return p.returncode in ok_codes, p.stdout + p.stderr


def pj(out):
    try:
        return json.loads(out[out.index("{") if out.lstrip().startswith("{") or "[" not in out[:2] else out.index("["):])
    except Exception:
        return {}


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="buildroom-linkedin-tests-"))
    py, L, SC = sys.executable, S / "li_pipeline.py", S / "li_scorecard.py"
    P = work / "linkedin/pipeline.json"

    # ---- shared copy-system references are byte-identical to the Copy Engine's ----
    for f in ("kern-framework.md", "halbert-writing-system.md"):
        a, b = SK / "references" / f, ROOT / "skills/buildroom-copy-engine/references" / f
        check(f"{f} identical to the Copy Engine's", a.exists() and a.read_bytes() == b.read_bytes())

    # ---- account-safety wording is present where the member reads it ----
    skill = (SK / "SKILL.md").read_text(encoding="utf-8")
    safety = (SK / "references/account-safety.md").read_text(encoding="utf-8")
    check("SKILL.md forbids acting on LinkedIn and bait", "at any volume" in skill and "engagement bait" in skill)
    check("account-safety lists never / may / by hand", all(h in safety for h in ("## The skill never", "## The skill may", "## The member does by hand")))

    # ---- pipeline: signals, suppression, limits, follow-up rhythm ----
    ok, out = run([py, L, "add", P, "--name", "Nobody", "--url", "https://www.linkedin.com/in/nobody", "--signal", "cold"], work, ok_codes=(2,))
    check("pipeline refuses a record with no warm signal", ok and "no signal, no DM" in out)
    ok, out = run([py, L, "add", P, "--name", "Dana Ruiz", "--url", "https://www.linkedin.com/in/danaruiz/", "--role", "COO",
                   "--company", "Ruiz & Co", "--signal", "sig:commented-my-post", "--fit", "A", "--date", "2026-10-12"], work)
    check("pipeline adds a warm signal", ok and '"added": 1' in out, out[-200:])
    ok, out = run([py, L, "add", P, "--name", "Dana again", "--url", "http://linkedin.com/in/DanaRuiz", "--signal", "sig:event"], work, ok_codes=(2,))
    check("pipeline refuses a duplicate (URL normalised)", ok and "already in the pipeline" in out)
    long_note = "x" * 230
    ok, out = run([py, L, "touch", P, "1", "--template", "C2", "--text", long_note, "--date", "2026-10-12"], work, ok_codes=(2,))
    check("connection note over 200 characters refused on a free account", ok and "limit is 200" in out)
    run([py, L, "settings", P, "--premium", "yes"], work)
    ok, out = run([py, L, "touch", P, "1", "--template", "C2", "--text", long_note, "--date", "2026-10-12"], work)
    check("Premium allows a 300-character note", ok and '"logged": "C2"' in out, out[-200:])
    run([py, L, "settings", P, "--premium", "no"], work)
    run([py, L, "move", P, "1", "connected", "--date", "2026-10-13"], work)
    ok, out = run([py, L, "touch", P, "1", "--template", "D1", "--date", "2026-10-13"], work)
    d = json.loads(out)
    check("first DM schedules follow-up 1 four days later", d.get("next") == "F1" and d.get("on") == "2026-10-17", out)
    ok, out = run([py, L, "touch", P, "1", "--template", "F1", "--date", "2026-10-17"], work)
    d = json.loads(out)
    check("follow-up 1 schedules follow-up 2 five days later", d.get("next") == "F2" and d.get("on") == "2026-10-22", out)
    ok, out = run([py, L, "touch", P, "1", "--template", "F2", "--date", "2026-10-22"], work)
    d = json.loads(out)
    check("after follow-up 2 the sequence stops (nurture)", d.get("on") is None and "nurture" in d.get("next", ""), out)
    ok, out = run([py, L, "touch", P, "1", "--template", "D5", "--date", "2026-10-22"], work)
    check("a call ask before a real exchange is warned", "earn it" in out, out[-300:])

    # pacing
    for i in range(2, 90):
        run([py, L, "add", P, "--name", f"P{i}", "--url", f"https://www.linkedin.com/in/p{i}", "--signal", "sig:viewed-profile", "--date", "2026-10-14"], work)
        run([py, L, "touch", P, str(i), "--template", "C2" if i < 9 else "C1", "--text", "Hi, good to connect." if i < 9 else None, "--date", "2026-10-14"] if i < 9 else
            [py, L, "touch", P, str(i), "--template", "C1", "--date", "2026-10-14"], work)
    ok, out = run([py, L, "pace", P, "--date", "2026-10-14"], work)
    pace = json.loads(out)
    w = " ".join(pace.get("warnings", []))
    check("pace warns above 20 requests a day and 80 a week", "today" in w and "7 days" in w, w)
    check("pace warns above the free monthly note allowance", "personalised notes" in w, w)
    ok, out = run([py, L, "pace", P, "--date", "2026-11-06"], work)
    check("pace flags invitations pending three weeks", "pending 3+ weeks" in out, out[-300:])

    # privacy
    ok, out = run([py, L, "forget", P, "2"], work)
    ok2, out2 = run([py, L, "add", P, "--name", "P2", "--url", "https://www.linkedin.com/in/p2/", "--signal", "sig:event"], work, ok_codes=(2,))
    data = json.loads(P.read_text())
    check("forget deletes the record and blocks re-adding", ok and ok2 and "suppressed" in out2 and not any(p["id"] == 2 for p in data["people"])
          and "p2" not in json.dumps(data["suppressed"]))
    ok, out = run([py, L, "due", P, "--retention", "--date", "2027-10-20"], work)
    check("records past 12 months are flagged for deletion", ok and len(json.loads(out).get("past_retention", [])) > 0)

    # connections import (LinkedIn's export starts with notes lines)
    (work / "Connections.csv").write_text(
        "Notes:\n\"When exporting your connection data, you may notice that some of the email addresses are missing.\"\n\n"
        "First Name,Last Name,URL,Email Address,Company,Position,Connected On\n"
        "P,Three,https://www.linkedin.com/in/p3,,Acme,CEO,15 Oct 2026\nSomeone,Else,https://www.linkedin.com/in/else,,X,Y,01 Jan 2020\n", encoding="utf-8")
    ok, out = run([py, L, "import-connections", P, "Connections.csv", "--date", "2026-10-16"], work)
    d = json.loads(out)
    data = json.loads(P.read_text())
    p3 = next(p for p in data["people"] if p["id"] == 3)
    check("connections import marks only pipeline people as connected, stores nobody else",
          d.get("connections_in_file") == 2 and d.get("pipeline_records_now_connected") == [3] and p3["stage_dates"].get("connected") == "2026-10-15"
          and "Someone" not in P.read_text(), out)

    # GoHighLevel build file is accepted by the Decision Machine's ghl_push.py
    ok, out = run([py, L, "ghl-build", P], work)
    (work / "ghl-build.json").write_text(out)
    gb = json.loads(out)
    check("ghl-build has the pipeline, tags and fields", gb["pipeline"]["name"] == "LinkedIn Organic" and "src:linkedin-organic" in gb["tags"] and gb["custom_fields"])
    gp = ROOT / "skills/buildroom-decision-machine/scripts/ghl_push.py"
    if gp.exists():
        env = {**os.environ, "GHL_API_KEY": "test", "GHL_LOCATION_ID": "loc"}
        ok, out = run([py, gp, "--dry-run", "ghl-build.json"], work, env=env)
        check("ghl_push.py --dry-run reads the LinkedIn build file", ok and "LinkedIn Organic" in out, out[-300:])

    # week counts
    run([py, L, "log-post", P, "--url", "https://www.linkedin.com/feed/update/urn:li:activity:1", "--pillar", "Cash flow", "--format", "carousel", "--date", "2026-10-13"], work)
    run([py, L, "log-comments", P, "12", "--date", "2026-10-13"], work)
    ok, out = run([py, L, "week", P, "--from", "2026-10-12"], work)
    wk = json.loads(out)
    check("week counts posts, comments, invites and DMs", wk["posts"] == 1 and wk["comments"] == 12 and wk["invites"] >= 80 and wk["dms_started"] == 1
          and wk["posts_by_format"] == {"carousel": 1}, json.dumps({k: wk[k] for k in ("posts", "comments", "invites", "dms_started")}))

    # ---- scorecard from a LinkedIn-shaped export ----
    write_xlsx(work / "export.xlsx", {
        "DISCOVERY": [["Overall Performance", "10/12/2026 - 10/18/2026"], ["Impressions", 5230], ["Members reached", 3110]],
        "ENGAGEMENT": [["Date", "Impressions", "Engagements"], ["10/11/2026", 900, 40], ["10/12/2026", 1200, 55], ["10/13/2026", 800, 30], ["10/19/2026", 999, 9]],
        "TOP POSTS": [["Maximum of 50 posts available to include in this list"], [], ["Post URL", "Post publish date", "Engagements", None, "Post URL", "Post publish date", "Impressions"],
                      ["https://www.linkedin.com/feed/update/urn:li:activity:1", "10/13/2026", 55, None, "https://www.linkedin.com/feed/update/urn:li:activity:1", "10/13/2026", 2100]],
        "FOLLOWERS": [["Total followers on 10/18/2026:", 1520], [], ["Date", "New followers"], ["10/12/2026", 4], ["10/14/2026", 6], ["10/30/2026", 99]],
    })
    sys.path.insert(0, str(S))
    import li_scorecard  # noqa: E402
    import datetime as dt
    m = li_scorecard.metrics_from_xlsx(work / "export.xlsx", dt.date(2026, 10, 12), dt.date(2026, 10, 19))
    check("scorecard sums the week's daily rows only", m["impressions"] == 2000 and m["engagements"] == 85, m)
    check("scorecard reads followers and members reached", m["new_followers"] == 10 and m["members_reached"] == 3110, m)
    check("scorecard finds the week's top post", m["top_posts"] and m["top_posts"][0]["impressions"] == 2100, m["top_posts"])
    (work / "manual.json").write_text(json.dumps({"profile_viewers": 41, "saves": 6, "sends": 2}))
    ok, out = run([py, SC, "week", "--pipeline", P, "--xlsx", "export.xlsx", "--manual", "manual.json", "--from", "2026-10-12", "--out", "cards"], work)
    md = (work / "cards/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("weekly scorecard written with inputs, outputs and diagnosis", ok and "## What you did" in md and "## Diagnosis" in md and "2,000" in md, out[-300:])
    check("diagnosis names the acceptance problem", "Acceptance under 30%" in md, md[-600:])
    ok, out = run([py, SC, "week", "--pipeline", P, "--from", "2026-10-19", "--out", "cards"], work)
    md2 = (work / "cards/2026-W43.md").read_text(encoding="utf-8") if ok else ""
    check("next week's scorecard shows last week and the trend", ok and "Four-week trend" in md2 and "No LinkedIn export this week" in md2)

    # ---- renderer (optional) ----
    if shutil.which("node"):
        brand = {"name": "Test Advisory", "bg": "#0f1424", "fg": "#f4f6fa", "accent": "#f97316", "muted": "#a9b2c6"}
        (work / "specs").mkdir()
        (work / "specs/banner.json").write_text(json.dumps({"id": "banner", "layout": "banner", "brand": brand,
            "copy": {"promise": "Cash you can count on, for family firms", "proof": "22 years · 140+ owners advised", "cta": "Free diagnostic in Featured"}}))
        (work / "specs/long.json").write_text(json.dumps({"id": "long", "layout": "banner", "brand": brand,
            "copy": {"promise": "word " * 120, "proof": "proof " * 30, "cta": "cta " * 30}}))
        (work / "specs/deck.json").write_text(json.dumps({"id": "deck", "layout": "carousel", "brand": brand, "copy": {"author": "Test · Advisor"},
            "slides": [{"kind": "hook", "title": "Five slides on cash", "sub": "A test deck"}, {"kind": "point", "n": 1, "title": "One", "body": "Body"},
                       {"kind": "list", "title": "List", "items": ["a", "b", "c"]}, {"kind": "quote", "quote": "A quote", "who": "Someone"},
                       {"kind": "cta", "title": "Want it?", "sub": "In Featured"}]}))
        ok, out = run(["node", S / "render_linkedin.mjs", "specs/banner.json", "specs/deck.json", "--out", "renders", "--overlay"], work, ok_codes=(0, 1, 2))
        if "Playwright not found" in out:
            print("SKIP  renderer (Playwright not installed here)")
        else:
            check("renderer: banner passes and writes the safe overlay", (work / "renders/banner.png").exists() and (work / "renders/banner_safe.png").exists()
                  and json.loads((work / "renders/banner.report.json").read_text())["result"] == "PASS", out[-300:])
            pdf = (work / "renders/deck.pdf").read_bytes() if (work / "renders/deck.pdf").exists() else b""
            check("renderer: carousel PDF has one page per slide", len(re.findall(rb"/Type\s*/Page[^s]", pdf)) == 5, out[-300:])
            ok, out = run(["node", S / "render_linkedin.mjs", "specs/long.json", "--out", "renders"], work, ok_codes=(1,))
            check("renderer: copy too long for the banner fails the fit check", ok and "text fits" in out, out[-300:])

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
