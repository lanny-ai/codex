#!/usr/bin/env python3
"""LinkedIn Engine tests: pipeline rules, pacing, privacy, the scorecard reader and the renderer.

Local only: synthetic files, no network, no LinkedIn. The renderer checks run only when Node and
Playwright are available (NODE_PATH or a local node_modules).

Usage:  python3 buildroom/tests/linkedin/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folder or here)
import datetime as dt, json, os, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

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


def behaviour_tests(work, py, L, SC, li_scorecard):
    """The dry run's fixes: each on its own small pipeline so the counts are exact."""
    w = work / "b"; w.mkdir()
    Q = w / "linkedin/pipeline.json"
    run([py, L, "settings", "--date", "2026-10-01"], w)            # default path, from the current folder
    def add(name, signal="sig:commented-my-post", date="2026-10-05"):
        ok, out = run([py, L, "add", "--name", name, "--url", f"https://www.linkedin.com/in/{name.lower()}", "--signal", signal, "--date", date], w)
        return pj(out).get("added")
    def touch(i, t, date, *extra):
        ok, out = run([py, L, "touch", str(i), "--template", t, "--date", date, *extra], w)
        return pj(out)
    def move(i, stage, date):
        ok, out = run([py, L, "move", str(i), stage, "--date", date], w)
        return pj(out)
    def week(start):
        ok, out = run([py, L, "week", "--from", start], w)
        return pj(out)

    a = add("Launcher", "sig:launch")
    check("sig:launch is a warm signal", a == 1)

    # D6 (and V1) close the task: today stops asking for a message already sent
    move(a, "connected", "2026-10-05"); touch(a, "D1", "2026-10-05"); move(a, "conversation", "2026-10-06")
    d = touch(a, "D6", "2026-10-07")
    ok, out = run([py, L, "today", "--date", "2026-10-09"], w)
    check("D6 clears the next action (waits for the reply, F1 if silent)", d.get("next") == "wait for reply; F1 if silent"
          and d.get("on") == "2026-10-11" and '"Launcher"' not in out, json.dumps(d))
    d = touch(a, "V1", "2026-10-08")
    check("V1 clears the next action too", d.get("next") == "wait for reply; F1 if silent", json.dumps(d))

    # move: every stage sets its own next action
    b = add("Mover")
    nxt = {s: move(b, s, "2026-10-06") for s in ("signal", "warming", "connected", "conversation", "qualified", "call-offered",
                                                  "call-booked", "call-held", "proposal", "nurture", "won")}
    check("move: call-offered says F1 if no answer, not D5", nxt["call-offered"]["next"] == "F1 if no answer" and nxt["call-offered"]["on"] == "2026-10-10", nxt["call-offered"])
    check("move: signal, warming and nurture have their own next action; won clears it",
          nxt["signal"]["next"].startswith("connect") and nxt["warming"]["next"].startswith("check accept")
          and nxt["nurture"]["next"].startswith("comment") and nxt["won"]["next"] is None and nxt["won"]["on"] is None, nxt)

    # real conversations: two or more replies; Replies counted separately
    c = add("Talker")
    move(c, "connected", "2026-10-12"); touch(c, "D1", "2026-10-12"); move(c, "conversation", "2026-10-13")
    wk1 = week("2026-10-12")
    ok, out = run([py, L, "reply", str(c), "--date", "2026-10-14"], w)
    wk2 = week("2026-10-12")
    check("one reply is a reply, not a real conversation", wk1["replies"] == 1 and wk1["conversations"] == 0, json.dumps({k: wk1[k] for k in ("replies", "conversations")}))
    check("a second reply makes a real conversation", pj(out).get("real_conversation") is True and wk2["conversations"] == 1 and wk2["replies"] == 1,
          json.dumps({k: wk2[k] for k in ("replies", "conversations")}))
    check("reply rate counts this week's first DMs that got a reply", wk2["reply_rate"] == 1.0, wk2.get("reply_rate"))

    # acceptance: the member's own requests in the window, accepted by any later date; inbound requests never count
    e1 = add("Early", "sig:viewed-profile", "2026-10-12"); touch(e1, "C1", "2026-10-12"); move(e1, "connected", "2026-10-20")
    e2 = add("Inbound", "sig:inbound-connect", "2026-10-19"); move(e2, "connected", "2026-10-19")
    e3 = add("Pending", "sig:viewed-profile", "2026-10-19"); touch(e3, "C1", "2026-10-19")
    w42, w43 = week("2026-10-12"), week("2026-10-19")
    check("acceptance is a cohort of the week's own requests (never above 100%)",
          w42["invited"] == 1 and w42["acceptance_rate"] == 1.0 and w43["invited"] == 1 and w43["acceptance_rate"] == 0.0,
          json.dumps({"w42": [w42["invited"], w42["accepted"], w42["acceptance_rate"]], "w43": [w43["invited"], w43["accepted"], w43["acceptance_rate"]]}))

    # DMs to someone not connected warn; an early D5 is logged without moving the stage
    f = add("Stranger")
    d = touch(f, "D5", "2026-10-06")
    ws = " ".join(d.get("warnings", []))
    data = json.loads(Q.read_text())
    check("DM to someone not connected is warned", "not connected" in ws, ws)
    check("early D5 warns and does not advance to call-offered", "earn it" in ws and d.get("stage") == "signal"
          and next(p for p in data["people"] if p["id"] == f)["stage"] == "signal", json.dumps(d))
    d = touch(f, "D5", "2026-10-07", "--force-stage")
    check("--force-stage moves an early D5 to call-offered", d.get("stage") == "call-offered", json.dumps(d))

    # the free-account note limit (3) is warned at the moment of sending the 4th
    outs = []
    for k in range(4):
        i = add(f"Noted{k}", "sig:viewed-profile", "2026-10-20")
        outs.append(touch(i, "C2", "2026-10-20", "--text", "Hi, enjoyed your comment."))
    check("touch warns at the 4th personalised note of the month (free account)",
          not any("personalised notes" in x for x in outs[2].get("warnings", [])) and any("4 personalised notes" in x for x in outs[3].get("warnings", [])),
          json.dumps(outs[3]))

    # today lists a person once
    g = add("Waiting", date="2026-10-20")
    ok, out = run([py, L, "today", "--date", "2026-10-23"], w)
    t = pj(out)
    check("today does not list the same person twice", any(x["id"] == g for x in t["3_signals_waiting"])
          and not any(x["id"] == g for x in t["4_follow_ups_due"]), json.dumps(t)[:400])

    # pillars: validated against settings
    ok, out = run([py, L, "log-post", "--format", "text", "--pillar", "Anything", "--date", "2026-10-13"], w)
    check("log-post without stored pillars warns", ok and "no pillars stored" in out, out[-300:])
    run([py, L, "settings", "--pillars", "Cash flow", "Pricing"], w)
    ok, out = run([py, L, "log-post", "--format", "text", "--pillar", "cash  flow", "--date", "2026-10-13"], w)
    ok2, out2 = run([py, L, "log-post", "--format", "text", "--pillar", "Cashflow", "--date", "2026-10-13"], w, ok_codes=(2,))
    check("log-post accepts a stored pillar (case and spacing ignored)", ok and '"pillar": "Cash flow"' in out, out[-300:])
    check("log-post refuses an unknown pillar and lists the valid ones", ok2 and "unknown pillar" in out2 and "Pricing" in out2, out2[-300:])

    # both scripts default to the same week: the last complete Monday–Sunday
    ok, out = run([py, L, "week", "--date", "2026-10-21"], w)
    ok2, out2 = run([py, SC, "week", "--date", "2026-10-21", "--out", "cards"], w)
    check("li_pipeline week and li_scorecard week default to the same last complete week",
          pj(out).get("from") == "2026-10-12" and (w / "cards/2026-W42.md").exists(), out[-200:] + out2[-200:])

    # scorecard: the export's own range must be the week
    write_xlsx(w / "late.xlsx", {"DISCOVERY": [["Overall Performance", "10/16/2026 - 10/22/2026"], ["Impressions", 900], ["Members reached", 1698]],
                                 "ENGAGEMENT": [["Date", "Impressions", "Engagements"], ["10/16/2026", 100, 4], ["10/17/2026", 120, 4], ["10/18/2026", 130, 5]]})
    ok, out = run([py, SC, "week", "--xlsx", "late.xlsx", "--from", "2026-10-12", "--out", "late"], w, ok_codes=(2,))
    check("scorecard refuses an export whose range is not the week", ok and "REFUSED" in out and "2026-10-16 to 2026-10-22" in out
          and not (w / "late/2026-W42.md").exists(), out[-300:])
    ok, out = run([py, SC, "week", "--xlsx", "late.xlsx", "--from", "2026-10-12", "--out", "late", "--allow-mismatch"], w)
    md = (w / "late/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("--allow-mismatch writes the card with the mismatch shown and no whole-period reach", "does not match" in md
          and "| Members reached | — |" in md, md[:600])
    write_xlsx(w / "odd.xlsx", {"DISCOVERY": [["Overall Performance", "10/12/2026 - 10/18/2026"], ["Impressions", 350], ["Members reached", 1698]],
                                "ENGAGEMENT": [["Date", "Impressions"], ["10/16/2026", 100], ["10/17/2026", 120], ["10/18/2026", 130]],
                                "FOLLOWERS": [["Date", "New followers"], ["10/12/2026", 4]]})
    ok, out = run([py, SC, "week", "--xlsx", "odd.xlsx", "--from", "2026-10-12", "--out", "odd"], w)
    md = (w / "odd/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("members reached above impressions is flagged as impossible", "impossible numbers" in md.lower(), md[:600])
    kv = li_scorecard.kv_pairs(li_scorecard.read_xlsx(w / "odd.xlsx"))
    check("summary pairs skip daily date rows", "" not in kv and not any(re.match(r"^\d", k) for k in kv) and "members reached" in kv, kv)

    # a missing pipeline file is warned on the scorecard
    ok, out = run([py, SC, "week", "--pipeline", "nope.json", "--from", "2026-10-12", "--out", "nope"], w)
    md = (w / "nope/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("scorecard warns when the pipeline file is missing", "WARNING" in out and "No pipeline file at nope.json" in md, out[-300:])

    # diagnosis follows the targets; rates are formatted by key
    base = {"posts": 3, "comments": 30, "invites": 20, "acceptance_rate": .5, "dms_started": 12, "reply_rate": .3,
            "conversations": 4, "calls_booked": 1, "calls_held": 0, "won": 0, "proposals": 0}
    ok_notes = li_scorecard.diagnose(base, None, {}, None)
    short = li_scorecard.diagnose({**base, "invites": 8, "dms_started": 2, "conversations": 1, "acceptance_rate": .38}, None, {}, None)
    check("diagnosis says On track only when every target is met", len(ok_notes) == 1 and ok_notes[0].startswith("On track"), ok_notes)
    check("diagnosis flags each shortfall against the targets", not any(n.startswith("On track") for n in short)
          and any("8 connection requests against 15–30" in n for n in short) and any("2 warm-signal DMs" in n for n in short)
          and any("1 real conversations" in n for n in short) and any("Acceptance 38%" in n for n in short), short)
    hot = li_scorecard.diagnose({**base, "invites": 60}, None, {}, None)
    check("diagnosis warns above 50 requests a week", any("above 50" in n for n in hot), hot)
    check("rates formatted as percentages by key", li_scorecard.fmt(1.0, "acceptance_rate") == "100%" and li_scorecard.fmt(0.0, "reply_rate") == "0%"
          and li_scorecard.fmt(0.385, "acceptance_rate") == "38%" and li_scorecard.fmt(1.0) == "1")
    ok, out = run([py, SC, "week", "--from", "2026-10-12", "--out", "pct"], w)
    md = (w / "pct/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("scorecard shows a 100% acceptance as 100%", "| Acceptance (this week's requests) | 100% ✅" in md, md[:900])


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

    # ---- pipeline file: created only by settings/init; a wrong path is refused, never a silent empty pipeline ----
    ok, out = run([py, L, "today", work / "typo.json"], work, ok_codes=(2,))
    check("missing pipeline file refused with the path named", ok and "no pipeline at" in out and "typo.json" in out
          and not (work / "typo.json").exists(), out[-300:])
    ok, out = run([py, L, "add", "--name", "X", "--url", "https://www.linkedin.com/in/x", "--signal", "sig:event"], work, ok_codes=(2,))
    check("add refuses when the default pipeline does not exist yet", ok and "no pipeline at linkedin/pipeline.json" in out
          and not P.exists(), out[-300:])
    ok, out = run([py, L, "settings", P, "--premium", "no", "--date", "2026-10-01"], work)
    d = pj(out)
    check("settings creates the pipeline and prints the lawful basis", ok and P.exists() and d.get("created") and "legitimate interest" in d.get("lawful_basis", "")
          and json.loads(P.read_text())["created"] == "2026-10-01", out[-300:])
    check("free-account notes limit defaults to 3", d.get("settings", {}).get("notes_limit") == 3, out[-300:])

    # ---- pipeline: signals, suppression, limits, follow-up rhythm ----
    ok, out = run([py, L, "add", P, "--name", "Nobody", "--url", "https://www.linkedin.com/in/nobody", "--signal", "cold"], work, ok_codes=(2,))
    check("pipeline refuses a record with no warm signal", ok and "no signal, no DM" in out)
    ok, out = run([py, L, "add", P, "--name", "Dana Ruiz", "--url", "https://www.linkedin.com/in/danaruiz/", "--role", "COO",
                   "--company", "Ruiz & Co", "--signal", "sig:commented-my-post", "--fit", "A", "--date", "2026-10-12"], work)
    check("pipeline adds a warm signal", ok and '"added": 1' in out, out[-200:])
    check("the first record shows the lawful basis", "lawful_basis" in out, out[-300:])
    ok, out = run([py, L, "list"], work)
    check("default path: linkedin/pipeline.json from the current folder", ok and '"Dana Ruiz"' in out, out[-300:])
    ok, out = run([py, L, "list", "--file", P], work)
    check("--file names the pipeline too", ok and '"Dana Ruiz"' in out, out[-300:])
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
    ok, out = run([py, L, "forget", P, "2", "--date", "2026-10-15"], work)
    ok2, out2 = run([py, L, "add", P, "--name", "P2", "--url", "https://www.linkedin.com/in/p2/", "--signal", "sig:event"], work, ok_codes=(2,))
    data = json.loads(P.read_text())
    check("forget deletes the record and blocks re-adding", ok and ok2 and "suppressed" in out2 and not any(p["id"] == 2 for p in data["people"])
          and "p2" not in json.dumps(data["suppressed"]))
    check("forget honours --date", data["suppressed"][-1]["date"] == "2026-10-15", data["suppressed"])
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
    gb = json.loads(out)
    check("ghl-build: tags lower-case, src-linkedin in the Build Room style", all(t == t.lower() for t in gb["tags"]) and "src-linkedin" in gb["tags"]
          and "fit-a" in gb["tags"] and "sig-commented-my-post" in gb["tags"] and gb["custom_fields"], gb["tags"])
    check("ghl-build: existing pipeline by default, no second Call booked / Won",
          gb["pipeline_mode"] == "existing" and gb["pipeline"]["stages"] == ["New Lead", "Call Booked", "Showed", "Committed", "Paid"]
          and gb["stage_map"]["call-booked"] == "Call Booked" and gb["stage_map"]["won"] == "Paid" and "Won" not in gb["pipeline"]["stages"], gb)
    ok, out = run([py, L, "ghl-build", P, "--pipeline-name", "Install Pipeline", "--stages", "New Lead", "Install Call Booked", "Showed", "Paid"], work)
    gb = json.loads(out)
    check("ghl-build: --stages maps onto the member's own stage names", gb["pipeline"]["name"] == "Install Pipeline"
          and gb["stage_map"]["call-booked"] == "Install Call Booked" and gb["stage_map"]["proposal"] == "Showed" and gb["stage_map"]["qualified"] == "New Lead", gb)
    ok, out = run([py, L, "ghl-build", P, "--tag-style", "colon"], work)
    check("ghl-build: --tag-style colon", "src:linkedin" in json.loads(out)["tags"] and "fit:a" in json.loads(out)["tags"], out[-300:])
    ok, out = run([py, L, "ghl-build", P, "--pipeline", "separate"], work)
    (work / "ghl-build.json").write_text(out)
    gb = json.loads(out)
    check("ghl-build: --pipeline separate gives the LinkedIn Organic pipeline", gb["pipeline"]["name"] == "LinkedIn Organic" and "Won" in gb["pipeline"]["stages"])
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
        "DISCOVERY": [["Overall Performance", "10/12/2026 - 10/18/2026"], ["Impressions", 2000], ["Members reached", 1110]],
        "ENGAGEMENT": [["Date", "Impressions", "Engagements"], ["10/11/2026", 900, 40], ["10/12/2026", 1200, 55], ["10/13/2026", 800, 30], ["10/19/2026", 999, 9]],
        "TOP POSTS": [["Maximum of 50 posts available to include in this list"], [], ["Post URL", "Post publish date", "Engagements", None, "Post URL", "Post publish date", "Impressions"],
                      ["https://www.linkedin.com/feed/update/urn:li:activity:1", "10/13/2026", 55, None, "https://www.linkedin.com/feed/update/urn:li:activity:2", "10/14/2026", 2100],
                      ["https://www.linkedin.com/feed/update/urn:li:activity:2", "10/14/2026", 30, None, "https://www.linkedin.com/feed/update/urn:li:activity:1", "10/13/2026", 900]],
        "FOLLOWERS": [["Total followers on 10/18/2026:", 1520], [], ["Date", "New followers"], ["10/12/2026", 4], ["10/14/2026", 6], ["10/30/2026", 99]],
    })
    sys.path.insert(0, str(S))
    import li_scorecard  # noqa: E402
    m = li_scorecard.metrics_from_xlsx(work / "export.xlsx", dt.date(2026, 10, 12), dt.date(2026, 10, 19))
    check("scorecard sums the week's daily rows only", m["impressions"] == 2000 and m["engagements"] == 85, m)
    check("scorecard reads followers and members reached", m["new_followers"] == 10 and m["members_reached"] == 1110, m)
    check("scorecard reads the export's own date range", m["period"] == ["2026-10-12", "2026-10-18"] and m["period_matches"], m)
    tp = {p["url"][-1]: p for p in m["top_posts"]}
    check("scorecard merges TOP POSTS' two tables by post link", tp.get("1", {}).get("engagements") == 55 and tp.get("1", {}).get("impressions") == 900
          and tp.get("2", {}).get("impressions") == 2100 and m["top_posts"][0]["url"].endswith("2"), m["top_posts"])
    (work / "manual.json").write_text(json.dumps({"profile_viewers": 41, "saves": 6, "sends": 2}))
    ok, out = run([py, SC, "week", "--pipeline", P, "--xlsx", "export.xlsx", "--manual", "manual.json", "--from", "2026-10-12", "--out", "cards"], work)
    md = (work / "cards/2026-W42.md").read_text(encoding="utf-8") if ok else ""
    check("weekly scorecard written with inputs, outputs and diagnosis", ok and "## What you did" in md and "## Diagnosis" in md and "2,000" in md, out[-300:])
    check("diagnosis names the acceptance problem", "Acceptance under 30%" in md, md[-600:])
    ok, out = run([py, SC, "week", "--pipeline", P, "--from", "2026-10-19", "--out", "cards"], work)
    md2 = (work / "cards/2026-W43.md").read_text(encoding="utf-8") if ok else ""
    check("next week's scorecard shows last week and the trend", ok and "Four-week trend" in md2 and "No LinkedIn export this week" in md2)
    check("four-week trend includes this week", "| 2026-W42 |" in md and "| 2026-W43 |" in md2 and "| 2026-W42 |" in md2, md2[-800:])
    check("scorecard labels: Replies and Real conversations (2+ replies)", "Real conversations (2+ replies)" in md and "Replies (people who replied)" in md)

    behaviour_tests(work, py, L, SC, li_scorecard)

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
            nofont = {**brand, "display_font": "Missing Display", "body_font": "Missing Body",
                      "font_files": {"display": [{"src": "../brand/fonts/nope-700.woff2", "weight": 700}], "body": [{"src": "../brand/fonts/nope.woff2"}]}}
            (work / "specs/nofont.json").write_text(json.dumps({"id": "nofont", "layout": "card", "brand": nofont,
                "copy": {"kicker": "Cash", "headline": "A short headline", "author": "Test · Advisor"}}))
            ok, out = run(["node", S / "render_linkedin.mjs", "specs/nofont.json", "--out", "renders"], work, ok_codes=(1,))
            check("renderer: brand fonts that did not load FAIL the check", ok and "brand fonts loaded" in out and "Missing Display" in out, out[-400:])
            (work / "specs/feat.json").write_text(json.dumps({"id": "feat", "layout": "featured", "brand": {**brand, "muted": "#2a3145"},
                "copy": {"kicker": "Free", "headline": "The cash checklist", "sub": "A long sub-line nobody can read at thumbnail size"}}))
            (work / "specs/card.json").write_text(json.dumps({"id": "card", "layout": "card", "brand": brand,
                "copy": {"kicker": "Cash", "headline": "Most owners check cash monthly. Check it weekly.", "sub": "Three numbers, ten minutes, every Monday.", "author": "Test · Advisor"}}))
            (work / "specs/deck2.json").write_text(json.dumps({"id": "deck2", "layout": "carousel", "brand": brand, "copy": {"author": "Test", "swipe": "Weiter"},
                "slides": [{"kind": "hook", "title": "Hook"}, {"kind": "point", "n": "", "title": "No numeral"}, {"kind": "cta", "title": "End"}]}))
            ok, out = run(["node", S / "render_linkedin.mjs", "specs/feat.json", "specs/card.json", "specs/deck2.json", "--out", "renders"], work, ok_codes=(0, 1))
            fr = json.loads((work / "renders/feat.report.json").read_text()) if (work / "renders/feat.report.json").exists() else {}
            check("renderer: featured is title-only by default (sub left off, with a note)", any("sub-line is left off" in x for x in fr.get("warnings", [])), fr)
            check("renderer: muted colour contrast is checked against the background", any("muted #2a3145" in x and "below 3:1" in x for x in fr.get("warnings", [])), fr)
            cr = json.loads((work / "renders/card.report.json").read_text()) if (work / "renders/card.report.json").exists() else {}
            check("renderer: card with author line inside the fit box passes", cr.get("result") == "PASS", cr)
            dr = json.loads((work / "renders/deck2.report.json").read_text()) if (work / "renders/deck2.report.json").exists() else {}
            check("renderer: carousel with a spec swipe hint and n: \"\" renders", dr.get("result") == "PASS" and len(dr.get("files", [])) == 4, dr)
            longtmp = work / ("long-temporary-directory-" + "x" * 60)
            longtmp.mkdir()
            ok, out = run(["node", S / "render_linkedin.mjs", "specs/banner.json", "--out", "renders-longtmp"], work, ok_codes=(0, 1, 2),
                          env={**os.environ, "TMPDIR": str(longtmp)})
            check("renderer: works when TMPDIR is a long path", (work / "renders-longtmp/banner.png").exists(), out[-300:])

    caches = [str(x) for x in SK.rglob("__pycache__")]
    check("no __pycache__ written into the skill folder", not caches, caches)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
