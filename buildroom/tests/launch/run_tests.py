#!/usr/bin/env python3
"""Event Launcher tests: the plan math and timeline, the calendar file and reminders, the run sheet,
the launch tracker (gate, report, leaks) and the Obsidian debrief.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/launch/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folder or here)
import json, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-event-launcher"
S = SK / "scripts"
FX = HERE / "fixtures"
PY = sys.executable
PLAN, ICS, RUN, TRK = S / "launch_plan.py", S / "event_ics.py", S / "run_sheet.py", S / "launch_tracker.py"

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:600]}" if detail and not ok else ""))


def run(args, cwd, ok_codes=(0,)):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    return p.returncode in ok_codes, p.stdout + p.stderr, p.returncode


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


# ---------------------------------------------------------------- launch_plan.py

def plan_tests(work):
    w = work / "plan"; w.mkdir()
    base = ["math", "--goal-buyers", "20", "--price", "997", "--format", "bootcamp3"]

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000"], w)
    d = pj(out); sc = d.get("scenarios", {})
    lists = [sc.get(s, {}).get("needed", {}).get("list") for s in ("cautious", "typical", "strong")]
    check("math: three scenarios, the cautious one needs the biggest list", ok and lists[0] > lists[1] > lists[2] > 0, lists)
    t = sc.get("typical", {}).get("needed", {})
    check("math: typical reverse funnel runs list → registrants → Day 1–3 → close → saw price → buyers",
          t.get("buyers") == 20 and t.get("list") > t.get("registrants") > t["day_live"][0] > t["day_live"][2]
          > t.get("present_at_close") > 0 and t.get("saw_price") > t.get("present_at_close") and len(t["day_live"]) == 3, t)
    check("math: typical needs about 2,030 registrants and 10,149 names at $997 for a free 3-day bootcamp",
          t.get("registrants") == 2030 and t.get("list") == 10149, t)
    check("math: price band $500–1,999 from Scale For Impact 2026", d.get("price_band") == "$500–1,999"
          and d["rates"]["conversion"]["source"] == "Scale For Impact 2026" and d["rates"]["conversion"]["typical"] == .075, d.get("rates", {}).get("conversion"))
    srcs = d.get("sources", {})
    check("math: every benchmark prints its source key with a description",
          {"Build Room assumption", "Scale For Impact 2026", "Build Room founder run Jul 2026", "Build Room founder rule of thumb"} <= set(srcs)
          and all(srcs.values()), sorted(srcs))
    check("math: the registration rate is labelled a Build Room assumption and warned",
          d["rates"]["registration"]["source"] == "Build Room assumption"
          and any("no published benchmark" in x for x in d.get("warnings", [])), d.get("warnings"))
    check("math: 5,000 names for 20 buyers at $997 is a stretch", d.get("verdict") == "stretch", d.get("verdict"))
    check("math: expected buyers from the list per scenario", all("expected_from_list" in sc[s] for s in sc)
          and 9 < sc["typical"]["expected_from_list"]["buyers"] < 11, sc.get("typical", {}).get("expected_from_list"))
    check("math: the biggest lever is named with how to move it; assumption-only stages are left out",
          d.get("lever", {}).get("stage") == "conversion" and "checkout" in d["lever"]["how"]
          and "registration" not in d["lever"]["all_gains"] and "saw_price" not in d["lever"]["all_gains"]
          and "registration, saw_price" in d["lever"]["note"], d.get("lever"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "20000"], w)
    check("math: a big enough list is reachable", pj(out).get("verdict") == "reachable", pj(out).get("verdict"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "800"], w)
    check("math: a small list is 'not from this list alone'",
          pj(out).get("verdict") == "not from this list alone: add partners/ads or lower the goal", pj(out).get("verdict"))

    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "20", "--price", "997", "--format", "bootcamp3", "--list-size", "5000",
                      "--history-reg-rate", "12%", "--history-showup", "0.45"], w)
    d = pj(out)
    check("math: member history replaces the assumptions (cautious 80%, strong 120%)",
          d["rates"]["registration"]["source"] == "Member history" and d["rates"]["registration"]["typical"] == .12
          and d["rates"]["show_up"]["typical"] == .45 and abs(d["rates"]["show_up"]["cautious"] - .36) < 1e-9
          and "Member history" in d["sources"] and not any("no published benchmark" in x for x in d.get("warnings", [])), d.get("rates"))
    check("math: with history, registration joins the lever comparison", "registration" in d["lever"]["all_gains"]
          and d["lever"]["all_gains"]["registration"] == 1.2, d.get("lever"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "20", "--price", "297", "--format", "challenge5", "--list-size", "5000"], w)
    check("math: a 5-day challenge's biggest lever is day-over-day retention (applied four times)",
          pj(out).get("lever", {}).get("stage") == "retention", pj(out).get("lever"))

    ok, out, _ = run([PY, PLAN, "math", "--goal-cash", "30000", "--tiers", "Core:997:70", "VIP:2997:30%",
                      "--list-size", "3000", "--format", "challenge5"], w)
    d = pj(out)
    check("math: --goal-cash with --tiers: buyers from the share-weighted price ($1,597 → 19 buyers)",
          ok and d["goal"]["average_price"] == 1597 and d["goal"]["buyers"] == 19 and d["goal"]["binding"] == "goal-cash"
          and len(d["scenarios"]["typical"]["needed"]["day_live"]) == 5 and "retention" in d["rates"], d.get("goal"))
    check("math: tiers across price bands are warned", any("more than one price band" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--goal-cash", "20000", "--price", "997", "--list-size", "3000",
                      "--format", "webinar"], w)
    d = pj(out)
    check("math: both goals given, the larger buyer count wins; a webinar has no retention step",
          d["goal"]["buyers"] == 21 and "retention" not in d["rates"] and len(d["scenarios"]["typical"]["needed"]["day_live"]) == 1, d.get("goal"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "4500", "--list-size", "3000", "--format", "workshop"], w)
    d = pj(out)
    check("math: $2,000+ uses the 1–4% band and warns to close by application or call",
          d["rates"]["conversion"]["cautious"] == .01 and any("application" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "30", "--price", "47", "--list-size", "3000", "--format", "workshop",
                      "--paid-event"], w)
    d = pj(out)
    check("math: --paid-event uses paid show-up and the HSH-backed conversion", d["rates"]["show_up"]["typical"] == .60
          and d["rates"]["conversion"]["source"] == "HSH 2025" and d["rates"]["registration"]["typical"] == .06, d.get("rates"))

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--md"], w)
    check("math --md prints a markdown table with sources", ok and out.startswith("# Launch math") and "| **List size** |" in out
          and "Scale For Impact 2026" in out and "**Verdict:** stretch" in out, out[:300])
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--md", "math.md", "--out", "planA"], w)
    check("math --md FILE writes it and still prints JSON; --out writes plan.json", ok and (w / "math.md").exists()
          and pj(out).get("verdict") == "stretch" and json.loads((w / "planA/plan.json").read_text())["math"]["goal"]["buyers"] == 20, out[-300:])

    for args, needle, label in [
        (["math", "--price", "997", "--format", "bootcamp3", "--list-size", "100"], "a goal is needed", "no goal"),
        (["math", "--goal-buyers", "10", "--format", "bootcamp3", "--list-size", "100"], "a price is needed", "no price"),
        (["math", "--goal-buyers", "10", "--tiers", "A:100:50", "B:200:30", "--format", "bootcamp3", "--list-size", "100"],
         "must add up to 100%", "tier shares not 100%"),
        (["math", "--goal-buyers", "10", "--tiers", "A-100-50", "--format", "bootcamp3", "--list-size", "100"], "Name:price:share", "bad tier"),
        (["math", "--goal-buyers", "10", "--price", "997", "--format", "bootcamp3"], "--list-size", "no list size"),
        (["math", "--goal-buyers", "10", "--price", "-5", "--format", "bootcamp3", "--list-size", "100"], "more than 0", "negative price"),
        (["math", "--goal-buyers", "10", "--price", "997", "--format", "bootcamp3", "--list-size", "100", "--history-showup", "140"],
         "between 0 and 100%", "rate over 100%"),
    ]:
        ok, out, _ = run([PY, PLAN, *args], w, ok_codes=(2,))
        check(f"math refuses: {label} (exit 2)", ok and needle in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "10", "--price", "997", "--format", "bootcamp9", "--list-size", "100"], w, ok_codes=(2,))
    check("math refuses an unknown format", ok and "invalid choice" in out, out[-200:])

    # timeline
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "America/New_York",
                      "--date", "2026-10-17", "--out", "planA"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("timeline: milestones in date order with weekday names", ok and [m["date"] for m in d["milestones"]] == sorted(m["date"] for m in d["milestones"])
          and ms["day1"]["weekday"] == "Tue" and ms["day1"]["date"] == "2026-12-01", [(m["date"], m["id"]) for m in d.get("milestones", [])][:6])
    check("timeline: invitations start 14 days out, the gate 2 days before them",
          ms["invites_start"]["date"] == "2026-11-17" and ms["launch_gate"]["date"] == "2026-11-15" and ms["invites_start"]["source"] == "Livestorm 2026", ms.get("invites_start"))
    check("timeline: night-before recaps for days 2+ on the evening before", ms["day1_night"]["date"] == "2026-12-01"
          and ms["day2_night"]["date"] == "2026-12-02" and "day3_night" not in ms, sorted(ms))
    check("timeline: checkout test on the close morning, before the close-day session",
          ms["checkout_test"]["date"] == "2026-12-03" and d["milestones"].index(ms["checkout_test"]) < d["milestones"].index(ms["day3"]))
    check("timeline: cart closes 3 days after the final day; replay window about 7 days; debrief after both",
          ms["cart_close"]["date"] == "2026-12-06" and ms["replay_closes"]["date"] == "2026-12-10" and ms["debrief"]["date"] == "2026-12-12"
          and d["cart_close"] == "2026-12-06", (ms["cart_close"]["date"], ms["replay_closes"]["date"], ms["debrief"]["date"]))
    check("timeline: no partner milestones without --partners", "partner_recruit" not in ms and not d.get("warnings"), d.get("warnings"))
    plan = json.loads((w / "planA/plan.json").read_text())
    cal = (w / "planA/calendar.md").read_text()
    check("timeline --out merges into plan.json (math kept) and writes calendar.md",
          "math" in plan and plan["timeline"]["event_date"] == "2026-12-01" and "## Week of Mon" in cal and "| 2026-11-17 | Tue | **Invitations start**" in cal, cal[:300])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2027-02-01", "--days", "5", "--tz", "Europe/London",
                      "--partners", "--date", "2026-10-17"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("timeline --partners: recruitment 12 weeks out (Amber Spears' 90-day rule), deals in writing, partner kit",
          ms.get("partner_recruit", {}).get("date") == "2026-11-09" and ms["partner_recruit"]["source"] == "Amber Spears 2018"
          and "partner_terms" in ms and "partner_kit" in ms and "Amber Spears 2018" in pj(out)["sources"], ms.get("partner_recruit"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-21", "--days", "3", "--tz", "America/Chicago",
                      "--partners", "--date", "2026-10-17"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("timeline --partners at 9 weeks: recruitment starts today, flagged compressed and warned",
          ok and ms["partner_recruit"].get("compressed") and ms["partner_recruit"]["date"] == "2026-10-17"
          and any("90-day" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-25", "--days", "3", "--tz", "America/Chicago",
                      "--partners", "--date", "2026-10-17"], w, ok_codes=(2,))
    check("timeline --partners refuses under 8 weeks", ok and "at least 56 days" in out, out[-300:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-25", "--days", "3", "--tz", "America/Chicago",
                      "--date", "2026-10-17"], w, ok_codes=(2,))
    check("timeline refuses an event 8 days out without --rush (needs 14)", ok and "8 days away" in out and "--rush" in out, out[-300:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-25", "--days", "3", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--rush"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("timeline --rush compresses the late milestones to today and says so",
          ok and ms["invites_start"].get("compressed") and ms["invites_start"]["date"] == "2026-10-17"
          and ms["invites_start"]["planned"] == "2026-10-11" and any("--rush" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--paid-event"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("timeline --paid-event: ticket sales open 21 days out", ms["invites_start"]["date"] == "2026-10-30", ms.get("invites_start"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "Mars/Olympus",
                      "--date", "2026-10-17"], w, ok_codes=(2,))
    check("timeline refuses an unknown time zone", ok and "IANA" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-01", "--days", "1", "--tz", "UTC", "--date", "2026-10-17", "--rush"], w, ok_codes=(2,))
    check("timeline refuses a past date even with --rush", ok and "in the past" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-13-01", "--days", "1", "--tz", "UTC"], w, ok_codes=(2,))
    check("timeline refuses a bad date", ok and "YYYY-MM-DD" in out, out[-200:])
    (w / "foreign").mkdir(); (w / "foreign/plan.json").write_text('{"something": "else"}')
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "UTC", "--date", "2026-10-17",
                      "--out", "foreign"], w, ok_codes=(2,))
    check("--out refuses to overwrite a plan.json that is not ours", ok and "not an Event Launcher plan" in out, out[-200:])
    return w / "planA/plan.json"


# ---------------------------------------------------------------- event_ics.py

def unfold(raw):
    return re.sub(rb"\r\n[ \t]", b"", raw).decode("utf-8").split("\r\n")


def ics_tests(work):
    w = work / "ics"; w.mkdir()
    shutil.copy(FX / "event.json", w / "event.json")
    ok, out, _ = run([PY, ICS, "build", "--spec", "event.json", "--out", "event.ics", "--date", "2026-10-17"], w)
    d = pj(out)
    raw = (w / "event.ics").read_bytes()
    phys = raw.split(b"\r\n")
    check("build: writes the file and prints one event per day", ok and len(d.get("events", [])) == 3, out[-300:])
    check("ICS: every line ends in CRLF (no bare LF)", raw.endswith(b"\r\n") and not re.search(rb"(?<!\r)\n", raw))
    check("ICS: no physical line over 75 octets", all(len(x) <= 75 for x in phys), max(len(x) for x in phys))
    check("ICS: long lines are folded (continuation lines start with a space)", any(x.startswith(b" ") for x in phys))
    lines = unfold(raw)
    check("ICS: folding never splits a UTF-8 character (unfolded text decodes, emoji intact)",
          any("🎉" in x and "Ümlauts" in x for x in lines))
    check("ICS: one VCALENDAR with VERSION 2.0, PRODID and three VEVENTs",
          lines[0] == "BEGIN:VCALENDAR" and "VERSION:2.0" in lines and any(x.startswith("PRODID:") for x in lines)
          and lines.count("BEGIN:VEVENT") == 3 and lines.count("END:VEVENT") == 3 and lines[-2] == "END:VCALENDAR")
    check("ICS: times in UTC (14:00 Los Angeles on 10 Nov 2026 is 22:00Z, PST)",
          "DTSTART:20261110T220000Z" in lines and "DTEND:20261111T010000Z" in lines and "DTEND:20261113T011500Z" in lines
          and not any(x.startswith("DTSTART;TZID") for x in lines))
    check("ICS: DTSTAMP (replayed with --date) and SEQUENCE on every event",
          lines.count("DTSTAMP:20261017T000000Z") == 3 and lines.count("SEQUENCE:0") == 3)
    check("ICS: commas and semicolons escaped in SUMMARY", "SUMMARY:Cash Flow Bootcamp\\, Live\\; 3 Days - Day 1" in lines, [x for x in lines if x.startswith("SUMMARY")])
    desc = next(x for x in lines if x.startswith("DESCRIPTION:Bring"))
    check("ICS: newlines escaped as \\n and commas/semicolons in DESCRIPTION", "numbers\\, a laptop\\; no slides.\\nDay by day" in desc
          and "\n" not in desc, desc[:120])
    check("ICS: a day's own title and description are used", "SUMMARY:Cash Flow Bootcamp - Day 3 (close day)" in lines
          and any(x.startswith("DESCRIPTION:Day 2: proof") for x in lines))
    check("ICS: a 15-minute display alarm per event", lines.count("TRIGGER:-PT15M") == 3 and lines.count("ACTION:DISPLAY") == 3)
    uids = [x for x in lines if x.startswith("UID:")]
    check("ICS: a unique UID per day", len(set(uids)) == 3 and all(u.endswith("@buildroom-event-launcher") for u in uids), uids)
    check("ICS: organizer and URL carried", any(x.startswith("ORGANIZER;CN=Dana Ruiz:mailto:dana@example.com") for x in lines)
          and "URL:https://zoom.us/j/1234567890?pwd=abc" in lines)
    spec = json.loads((w / "event.json").read_text()); spec["days"][0]["start"] = "15:00"
    (w / "moved.json").write_text(json.dumps(spec))
    run([PY, ICS, "build", "--spec", "moved.json", "--out", "moved.ics", "--date", "2026-10-18"], w)
    uids2 = [x for x in unfold((w / "moved.ics").read_bytes()) if x.startswith("UID:")]
    check("ICS: UIDs are stable across a rebuild with a changed time (updates replace, not duplicate)", uids == uids2, (uids, uids2))
    e1 = d["events"][0]
    check("links: Google uses render?action=TEMPLATE with UTC dates", e1["google"].startswith("https://calendar.google.com/calendar/render?action=TEMPLATE")
          and "&dates=20261110T220000Z/20261111T010000Z" in e1["google"] and "text=Cash%20Flow%20Bootcamp%2C%20Live%3B" in e1["google"], e1["google"][:200])
    check("links: Outlook (live and 365) deeplink compose with startdt/enddt in Z",
          e1["outlook"].startswith("https://outlook.live.com/calendar/deeplink/compose?path=/calendar/action/compose&rru=addevent")
          and "startdt=2026-11-10T22:00:00Z&enddt=2026-11-11T01:00:00Z" in e1["outlook"]
          and e1["outlook_365"].startswith("https://outlook.office.com/calendar/deeplink/compose"), e1["outlook"][:200])
    check("build: no warnings for a clean spec inside 07:00–21:00 and without DST", not d.get("warnings"), d.get("warnings"))

    # round trip
    ok, out, code = run([PY, ICS, "check", "event.ics"], w)
    c = pj(out)
    check("check: the built file round-trips clean (exit 0)", ok and c.get("ok") and not c.get("problems"), c.get("problems"))
    check("check: round trip gives back the UTC times and the unescaped text",
          [e["start_utc"] for e in c.get("events", [])] == ["2026-11-10T22:00:00Z", "2026-11-11T22:00:00Z", "2026-11-12T22:00:00Z"]
          and c["events"][0]["summary"] == "Cash Flow Bootcamp, Live; 3 Days - Day 1"
          and c["events"][0]["description"].startswith("Bring your numbers, a laptop; no slides.\nDay by day")
          and "🎉" in c["events"][0]["description"], c.get("events", [{}])[0])

    # placeholder join link
    spec = json.loads((w / "event.json").read_text()); spec["join_url"] = "{{contact.zoom_link}}"
    (w / "merge.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "build", "--spec", "merge.json", "--out", "merge.ics"], w)
    d = pj(out); ml = unfold((w / "merge.ics").read_bytes())
    check("merge-field join link kept verbatim, warned, and no URL property", ok and "LOCATION:{{contact.zoom_link}}" in ml
          and not any(x.startswith("URL:") for x in ml) and any("cannot carry a per-contact link" in x for x in d.get("warnings", []))
          and "{{contact.zoom_link}}" in d["events"][0]["google"] and "{{contact.zoom_link}}" in d["events"][0]["outlook"], d.get("warnings"))

    # DST and odd hours
    spec = json.loads((w / "event.json").read_text())
    spec["days"] = [{"date": "2026-10-30", "start": "14:00", "end": "17:00"}, {"date": "2026-10-31", "start": "14:00", "end": "17:00"},
                    {"date": "2026-11-02", "start": "06:30", "end": "09:30"}]
    (w / "dst.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "build", "--spec", "dst.json", "--out", "dst.ics"], w)
    ws = pj(out).get("warnings", [])
    check("DST: a clock change between days 2 and 3 is warned (US DST ends 1 Nov 2026)",
          ok and any("daylight saving changes between day 2" in x and "UTC-07 → UTC-08" in x for x in ws), ws)
    check("DST: day 3 is 14:30Z after the change", "DTSTART:20261102T143000Z" in unfold((w / "dst.ics").read_bytes()))
    check("a start outside 07:00–21:00 local is warned", any("06:30 is outside 07:00–21:00" in x for x in ws), ws)
    spec["days"] = [{"date": "2026-03-08", "start": "02:30", "end": "04:00"}]
    (w / "gap.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "build", "--spec", "gap.json", "--out", "gap.ics"], w, ok_codes=(2,))
    check("refuses a local time that does not exist (spring forward gap)", ok and "does not exist" in out, out[-200:])

    for mut, needle, label in [
        (lambda s: s["days"][0].update(end="13:00"), "is not after the start", "end before start"),
        (lambda s: s.update(tz="Pacific/Atlantis"), "IANA", "bad tz"),
        (lambda s: s["days"].reverse(), "date order", "days out of order"),
        (lambda s: s["days"][0].update(start="2pm"), "HH:MM", "bad time"),
        (lambda s: s.pop("days"), "the spec needs", "no days"),
    ]:
        spec = json.loads((FX / "event.json").read_text()); mut(spec)
        (w / "bad.json").write_text(json.dumps(spec))
        ok, out, _ = run([PY, ICS, "build", "--spec", "bad.json", "--out", "bad.ics"], w, ok_codes=(2,))
        check(f"build refuses: {label} (exit 2)", ok and needle in out and not (w / "bad.ics").exists(), out[-200:])

    # check on a broken file
    broken = ("BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20261110T140000\nDTEND;TZID=America/New_York:20261110T170000\n"
              "SUMMARY:Bootcamp, Day 1\nDESCRIPTION:" + "x" * 90 + "\nEND:VEVENT\nBEGIN:VEVENT\nUID:same\nDTSTAMP:20261017T000000\n"
              "DTSTART:20261111T220000Z\nDTEND:20261111T210000Z\nEND:VEVENT\nBEGIN:VEVENT\nUID:same\nDTSTAMP:20261017T000000Z\n"
              "DTSTART:20261112T220000Z\nDTEND:20261113T010000Z\nBEGIN:VALARM\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\nEND:VCALENDAR\n")
    (w / "broken.ics").write_bytes(broken.encode())
    ok, out, code = run([PY, ICS, "check", "broken.ics"], w, ok_codes=(1,))
    probs = " | ".join(pj(out).get("problems", []))
    for needle, label in [("bare LF", "bare LF"), ("longer than 75 octets", "unfolded long line"), ("no PRODID", "missing PRODID"),
                          ("has no UID", "missing UID"), ("has no DTSTAMP", "missing DTSTAMP"), ("floating time", "floating time"),
                          ("no VTIMEZONE", "TZID without VTIMEZONE"), ("unescaped ','", "unescaped comma"),
                          ("must be a UTC time", "DTSTAMP not UTC"), ("DTEND is not after DTSTART", "end before start"),
                          ("UID same is used by 2", "duplicate UID"), ("VALARM at line", "alarm without TRIGGER")]:
        check(f"check finds: {label}", ok and needle in probs, probs[:400])
    ok, out, _ = run([PY, ICS, "check", "nope.ics"], w, ok_codes=(2,))
    check("check refuses a missing file (exit 2)", ok and "no file" in out)

    # reminders
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "event.json", "--recipient-tz", "America/Los_Angeles", "America/New_York",
                      "Europe/London"], w)
    r = pj(out); sends = {s["id"]: s for s in r.get("sends", [])}
    check("reminders: day before Day 1, morning of and 15 minutes before each day, live now",
          ok and "day1-day_before" in sends and all(f"day{k}-{x}" in sends for k in (1, 2, 3) for x in ("morning_of", "15_min", "live_now"))
          and "day2-day_before" not in sends, sorted(sends))
    check("reminders: the night-before recap for days 2 and 3 only (founder lesson)",
          "day2-night_before_recap" in sends and "day3-night_before_recap" in sends and "day1-night_before_recap" not in sends
          and sends["day2-night_before_recap"]["local"].startswith("2026-11-10 18:00"), sends.get("day2-night_before_recap"))
    check("reminders: the close-day morning says the offer is today", "offer is today" in sends["day3-morning_of"]["purpose"]
          and "offer" not in sends["day1-morning_of"]["purpose"])
    s15 = sends["day1-15_min"]
    check("reminders: local and UTC time for each send (15 min before 14:00 PST is 21:45Z)",
          s15["local"].startswith("2026-11-10 13:45 PST") and s15["utc"] == "2026-11-10T21:45:00Z", s15)
    check("reminders: sends sorted by UTC time", [s["utc"] for s in r["sends"]] == sorted(s["utc"] for s in r["sends"]))
    mo = sends["day1-morning_of"]
    rec = {x["tz"]: x for x in mo["recipients"]}
    check("reminders: an 08:00 Los Angeles SMS is 11:00 New York (fine) and 16:00 London (fine)",
          rec["America/New_York"]["local"].startswith("2026-11-10 11:00") and "sms_flag" not in rec["America/New_York"]
          and "sms_flag" not in rec["Europe/London"], rec)
    check("reminders: 08:00 is flagged caution in the host zone (outside the 09:00–20:00 safe window)",
          "caution" in rec["America/Los_Angeles"].get("sms_flag", ""), rec["America/Los_Angeles"])
    lv = {x["tz"]: x for x in sends["day1-live_now"]["recipients"]}
    check("reminders: a 14:00 PT 'live now' SMS lands at 22:00 in London: flagged as TCPA quiet hours",
          "TCPA" in lv["Europe/London"].get("sms_flag", "") and any("Europe/London" in f and "live_now" in f for f in r["sms_flags"]), lv["Europe/London"])
    check("reminders: recaps are email only", sends["day2-night_before_recap"]["channels"] == ["email"]
          and sends["day1-15_min"]["channels"] == ["email", "sms"])
    check("reminders: warns that GHL 'Set Event Start Date' uses the account time zone",
          any("Set Event Start Date" in x and "account time zone" in x for x in r.get("warnings", []))
          and "GHL help 2026" in r.get("sources", {}) and "TCPA 47 CFR 64.1200" in r.get("sources", {}), r.get("warnings"))
    spec = json.loads((w / "event.json").read_text()); spec["tz"] = "America/New_York"
    (w / "ny.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "ny.json", "--recipient-tz", "America/Los_Angeles"], w)
    mo = {s["id"]: s for s in pj(out)["sends"]}["day1-morning_of"]["recipients"][0]
    check("reminders: an 08:00 New York SMS is 05:00 in Los Angeles: flagged outside 08:00–21:00",
          mo["local"].startswith("2026-11-10 05:00") and "outside 08:00–21:00" in mo.get("sms_flag", ""), mo)
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "event.json", "--recipient-tz", "Nowhere/City"], w, ok_codes=(2,))
    check("reminders refuses an unknown recipient time zone", ok and "IANA" in out)


# ---------------------------------------------------------------- run_sheet.py

def runsheet_tests(work):
    w = work / "rs"; w.mkdir()
    shutil.copy(FX / "runsheet.json", w / "runsheet.json")
    ok, out, code = run([PY, RUN, "build", "--spec", "runsheet.json", "--out", "run-sheet.md"], w)
    d = pj(out); md = (w / "run-sheet.md").read_text() if (w / "run-sheet.md").exists() else ""
    check("run sheet: a clean spec PASSes every check (exit 0)", ok and d.get("result") == "PASS"
          and all(c["ok"] for c in d["checks"]), [c for c in d.get("checks", []) if not c["ok"]])
    check("run sheet: clock-time run-of-show per day", "## Day 1 · Tue 2026-11-10 · 14:00–17:00 America/Los_Angeles" in md
          and "| 14:05 | 40 | teach | The one belief" in md and "| 15:40 | 30 | pitch | The offer |" in md, md[:500])
    mod = d["checklists"]["moderator"]
    check("run sheet: moderator gets every link drop with its time",
          "Day 1 14:00 drop workbook: https://example.com/workbook" in mod and "Day 2 15:35 drop workbook: https://example.com/workbook" in mod
          and "Day 3 16:30 drop replay: https://example.com/replay" in mod, mod)
    check("run sheet: the checkout link is dropped as the price is shown and every 10 minutes of the pitch",
          "Day 3 15:40 drop checkout: https://example.com/checkout (as the price is shown)" in mod
          and "Day 3 16:00 drop checkout: https://example.com/checkout (again)" in mod
          and sum("15:40 drop checkout" in x for x in mod) == 1, mod)
    tech = d["checklists"]["tech"]
    check("run sheet: tech has the recording notice, the backup stream and the checkout check before the pitch",
          any("13:45 open the room" in x and "recording notice" in x for x in tech)
          and any("backup stream ready: backup_stream https://example.com/backup-room" in x for x in tech)
          and any(x.startswith("Day 3 15:30 checkout open check before \"The offer\"") for x in tech), tech)
    check("run sheet: checklists are in clock order", tech.index(next(x for x in tech if x.startswith("Day 3 13:45")))
          < tech.index(next(x for x in tech if x.startswith("Day 3 15:30"))))
    check("run sheet: closer gets the pitch and close", any("The offer (pitch" in x for x in d["checklists"].get("closer", []))
          and "### Closer (Dana)" in md)
    check("run sheet: the markdown has the checks and sources", "## Checks: PASS" in md and "✅ **breaks_90**" in md and "Sources:" in md)

    bad = json.loads((FX / "runsheet.json").read_text())
    bad["links"]["workbook"] = "TBD"
    bad["links"].pop("backup_stream")
    bad["roles"].pop("moderator")
    d1 = bad["days"][0]["segments"]
    d1[0]["title"] = "Welcome"                               # no recording notice on day 1
    d1.insert(3, {"min": 20, "title": "Early VIP offer", "kind": "pitch", "owner": "host"})   # pitch on day 1, and 105 min without a break
    bad["days"][1]["segments"][1]["kind"] = "teach"          # no proof on day 2
    bad["days"][2]["segments"][2] = {"min": 5, "title": "Stretch", "kind": "break", "owner": "tech"}   # no checkout test
    bad["days"][2]["segments"].append({"min": 30, "title": "Bonus Q&A", "kind": "qa", "owner": "host", "links": ["nolink"]})
    (w / "bad.json").write_text(json.dumps(bad))
    ok, out, code = run([PY, RUN, "build", "--spec", "bad.json", "--out", "bad.md"], w, ok_codes=(1,))
    d = pj(out); ch = {c["id"]: c for c in d.get("checks", [])}
    check("run sheet: a broken spec FAILs (exit 1) and still writes the sheet", ok and d.get("result") == "FAIL" and (w / "bad.md").exists(), out[-300:])
    check("check: recording notice missing on day 1", not ch["recording_notice"]["ok"] and "day 1" in ch["recording_notice"]["detail"], ch["recording_notice"])
    check("check: over 90 minutes without a break", not ch["breaks_90"]["ok"] and "day 1 from 14:00" in ch["breaks_90"]["detail"], ch["breaks_90"])
    check("check: total length over the planned end", not ch["length_vs_end"]["ok"] and "day 1 runs 200 min, 20 over" in ch["length_vs_end"]["detail"]
          and "day 3 runs 220 min" in ch["length_vs_end"]["detail"], ch["length_vs_end"])
    check("check: a link without a value and a link not in links", not ch["links_have_values"]["ok"]
          and "'workbook' has no real value" in ch["links_have_values"]["detail"] and "'nolink', which is not in links" in ch["links_have_values"]["detail"], ch["links_have_values"])
    check("check: pitch before the final day", not ch["pitch_final_day"]["ok"] and "Early VIP offer" in ch["pitch_final_day"]["detail"], ch["pitch_final_day"])
    check("check: checkout not tested before the close", not ch["checkout_before_close"]["ok"] and "day 3" in ch["checkout_before_close"]["detail"]
          and "day 1" in ch["checkout_before_close"]["detail"], ch["checkout_before_close"])
    check("check: moderator not named", not ch["roles_assigned"]["ok"] and "moderator" in ch["roles_assigned"]["detail"], ch["roles_assigned"])
    check("check (should): no proof on Day 2 and no backup link are warnings",
          not ch["proof_day2"]["ok"] and ch["proof_day2"]["level"] == "should" and not ch["backup_link"]["ok"]
          and set(d["warnings"]) == {"proof_day2", "backup_link"}, d.get("warnings"))
    bad["allow_early_pitch"] = True
    bad["days"][0]["checkout_test"] = "14:30"
    (w / "early.json").write_text(json.dumps(bad))
    ok, out, code = run([PY, RUN, "build", "--spec", "early.json", "--out", "early.md"], w, ok_codes=(1,))
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("allow_early_pitch passes the pitch check; checkout_test HH:MM counts as the test on that day",
          ch["pitch_final_day"]["ok"] and "early pitch allowed" in ch["pitch_final_day"]["detail"]
          and "day 1" not in ch["checkout_before_close"]["detail"] and "day 3" in ch["checkout_before_close"]["detail"], ch)
    bad = json.loads((FX / "runsheet.json").read_text()); bad["days"][0]["segments"][1]["kind"] = "lecture"
    (w / "kind.json").write_text(json.dumps(bad))
    ok, out, _ = run([PY, RUN, "build", "--spec", "kind.json", "--out", "kind.md"], w, ok_codes=(2,))
    check("run sheet refuses an unknown segment kind (exit 2)", ok and "kind must be one of" in out and not (w / "kind.md").exists(), out[-200:])
    bad = json.loads((FX / "runsheet.json").read_text()); bad["days"][0]["segments"][1]["min"] = 0
    (w / "min.json").write_text(json.dumps(bad))
    ok, out, _ = run([PY, RUN, "build", "--spec", "min.json", "--out", "min.md"], w, ok_codes=(2,))
    check("run sheet refuses a segment of 0 minutes", ok and "whole number of minutes" in out)


# ---------------------------------------------------------------- launch_tracker.py

def tracker_tests(work, plan_json):
    w = work / "trk"; w.mkdir()
    T = lambda *a, codes=(0,): run([PY, TRK, *a], w, ok_codes=codes)
    ok, out, _ = T("report", codes=(2,))
    check("tracker: refuses when no ledger exists (path named, nothing created)", ok and "no launch tracker at ./launches/<slug>/tracker.json" in out
          and not (w / "launches").exists(), out[-300:])
    ok, out, _ = T("log-reg", "10", "--slug", "nope", codes=(2,))
    check("tracker: --slug for a missing ledger is refused with its path", ok and "launches/nope/tracker.json" in out, out[-200:])
    init = ["init", "--name", "Cash Flow Bootcamp", "--format", "bootcamp3", "--days", "3", "--tz", "America/Los_Angeles",
            "--event-date", "2026-11-10", "--goal-buyers", "20", "--goal-cash", "19940", "--date", "2026-10-17"]
    ok, out, _ = T(*init, "--plan", plan_json)
    P = w / "launches/2026-11-cash-flow-bootcamp/tracker.json"
    d = pj(out)
    check("init: creates launches/YYYY-MM-<name>/tracker.json from the event date and name, with the plan from plan.json",
          ok and P.exists() and d.get("slug") == "2026-11-cash-flow-bootcamp" and "typical scenario" in d.get("plan_source", "")
          and str(plan_json) in d["plan_source"] and d["plan"]["registered"] == 2030, out[-300:])
    ok, out, _ = T(*init, codes=(2,))
    check("init: refuses to overwrite an existing ledger", ok and "already exists" in out)
    ok, out, _ = T("log-reg", "600", "--source", "list", "--date", "2026-10-30")
    check("log-reg: logs with a source; the only ledger is found without --slug", ok and pj(out).get("registered_total") == 600, out[-200:])
    T("log-reg", "250", "--source", "partner:Jo Smith", "--date", "2026-11-02")
    T("log-reg", "150", "--source", "social", "--date", "2026-11-09")
    ok, out, _ = T("log-reg", "5", "--source", "carrier-pigeon", codes=(2,))
    check("log-reg: refuses an unknown source", ok and "partner:NAME" in out)
    ok, out, _ = T("log-reg", "-5", codes=(2,))
    check("log-reg: refuses a negative count", ok and "0 or more" in out)
    ok, out, _ = T("log-day", "--day", "1", "--live", "200", "--peak", "170")
    T("log-day", "--day", "2", "--live", "150"); T("log-day", "--day", "3", "--live", "120")
    data = json.loads(P.read_text())
    check("log-day: dates default to the event day; peak kept", ok and data["days_live"]["1"] == {"live": 200, "peak": 170, "date": "2026-11-10"}
          and data["days_live"]["3"]["date"] == "2026-11-12", data["days_live"])
    ok, out, _ = T("log-day", "--day", "4", "--live", "10", codes=(2,))
    check("log-day: refuses a day outside the event", ok and "between 1 and 3" in out)
    ok, out, _ = T("log-close", "--present", "90", "--saw-price", "110")
    check("log-close: present and saw the price", ok and json.loads(P.read_text())["close"]["saw_price"] == 110)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "997", "--count", "6")
    check("log-sale: full pay books price × count", ok and pj(out).get("cash") == 5982 and pj(out).get("booked") == 5982, out[-200:])
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "137", "--count", "2", "--payment", "plan", codes=(2,))
    check("log-sale: a payment plan without --booked is refused", ok and "--booked TOTAL" in out)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "137", "--count", "2", "--payment", "plan", "--booked", "200", codes=(2,))
    check("log-sale: booked below the cash collected is refused", ok and "less than the cash" in out)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "137", "--count", "2", "--payment", "plan", "--booked", "3288")
    check("log-sale: a payment plan books the contract value", ok and pj(out).get("cash") == 274 and pj(out).get("booked") == 3288)
    ok, out, _ = T("log-refund", "--tier", "VIP", "--count", "1", "--amount", "997", codes=(2,))
    check("log-refund: refuses a tier with no sales", ok and "no sales logged" in out)
    ok, out, _ = T("log-refund", "--tier", "Core", "--count", "9", "--amount", "997", codes=(2,))
    check("log-refund: refuses more refunds than sales", ok and "only 8 sold" in out)
    ok, out, _ = T("log-refund", "--tier", "Core", "--count", "1", "--amount", "997")
    check("log-refund: logged", ok and pj(out).get("amount") == 997)

    # gate
    ok, out, _ = T("gate")
    g = pj(out); crit = [i["id"] for i in g.get("items", []) if i["critical"]]
    check("gate: HOLD at first, listing every critical item", ok and g.get("result") == "HOLD" and len(g.get("hold", [])) == len(crit) == 14, g.get("hold"))
    check("gate: 23 fixed items, 9 advisory, matching references/launch-gate.md", len(g["items"]) == 23
          and {i["id"] for i in g["items"] if not i["critical"]} == {"sms_compliance", "recording_notice", "testimonial_permission",
          "privacy_notice", "moderator_links", "first_win_timed", "live_tech_rehearsed", "refund_commissions", "chargeback_ready"}
          and g.get("rerun_on_close_morning", [None])[0] == "checkout_tested", [i["id"] for i in g["items"]])
    gate_md = (SK / "references/launch-gate.md").read_text() if (SK / "references/launch-gate.md").exists() else ""
    check("gate: the reference names the same critical / advisory split", "## Critical items" in gate_md and "## Advisory items" in gate_md
          and "SMS only with written consent" in gate_md.split("## Advisory items")[1]
          and "second checkout path" in gate_md.split("## Advisory items")[0], gate_md[:200])
    ok, out, _ = T("gate", "--set", "partner_disclosure", "na", codes=(2,))
    check("gate: na on a critical item needs --note", ok and "needs --note" in out)
    ok, out, _ = T("gate", "--set", "teleport_ready", "pass", codes=(2,))
    check("gate: refuses an unknown item", ok and "unknown gate item" in out)
    ok, out, _ = T("gate", "--set", "checkout_tested", "maybe", codes=(2,))
    check("gate: refuses an unknown status", ok and "pass, fail or na" in out)
    sets = []
    for c in crit:
        if c != "checkout_tested":
            sets += ["--set", c, "pass"]
    ok, out, _ = T("gate", *sets, "--set", "checkout_tested", "fail", "--set", "moderator_links", "fail")
    g = pj(out)
    check("gate: one critical fail still HOLDs, naming it", g.get("result") == "HOLD" and len(g["hold"]) == 1 and g["hold"][0].startswith("checkout_tested"), g.get("hold"))
    ok, out, _ = T("gate", "--set", "checkout_tested", "pass", "--set", "partner_disclosure", "na", "--note", "no partners this launch")
    g = pj(out)
    check("gate: GO when every critical item passes (or is na with a note); advisory fails do not block",
          g.get("result") == "GO" and any(x.startswith("moderator_links") for x in g.get("advisory_open", []))
          and next(i for i in g["items"] if i["id"] == "partner_disclosure").get("note") == "no partners this launch", g)
    ok, out, _ = T("gate", "--set", "sms_compliance", "na")
    check("gate: an advisory item may be na without a note", ok and pj(out).get("result") == "GO")

    # report
    ok, out, _ = T("report", "--md", "debrief.md")
    r = pj(out); f = {x["stage"]: x for x in r.get("funnel", [])}
    check("report: funnel vs plan from registered to buyers", ok and f["Registered"]["actual"] == 1000 and f["Registered"]["plan"] == 2030
          and f["Live Day 3"]["actual"] == 120 and f["Saw the price"]["actual"] == 110 and f["Buyers"]["actual"] == 8
          and [x["stage"] for x in r["funnel"]] == ["Registered", "Live Day 1", "Live Day 2", "Live Day 3", "Present at the close",
                                                    "Saw the price", "Buyers"], r.get("funnel"))
    check("report: day-over-day retention", [x["actual"] for x in r["retention"]] == [.75, .8] and r["retention"][0]["plan"] == .7, r.get("retention"))
    check("report: conversion of price-viewers and of registrants", r["conversion"]["of_saw_price"] == round(8 / 110, 4)
          and r["conversion"]["of_registrants"] == .008, r.get("conversion"))
    check("report: cash vs booked, net of refunds", r["money"] == {"cash": 6256.0, "booked": 9270.0, "refunded": 997.0, "booked_cancelled": 0.0,
                                                                   "net_cash": 5259.0, "net_booked": 8273.0, "average_sale": 1158.75}, r.get("money"))
    check("report: refunds and revenue per registrant", r["refunds"]["count"] == 1 and r["refunds"]["rate"] == .125
          and r["per_registrant"] == {"cash": 5.26, "booked": 8.27}, r.get("per_registrant"))
    lk = [x["stage"] for x in r["leaks"]]
    check("report: top three leaks ranked by buyers lost vs plan", lk == ["registration", "show_up", "conversion"]
          and r["leaks"][0]["buyers_lost"] > r["leaks"][1]["buyers_lost"] > r["leaks"][2]["buyers_lost"] and all(x["fix"] for x in r["leaks"]), r.get("leaks"))
    check("report: what to protect lists the stages that beat plan", {x["stage"] for x in r["protect"]} == {"retention_1_2", "retention_2_3", "stay_to_close"} and r["all_leaks"] == 4
          and all(x["keep"] for x in r["protect"]), r.get("protect"))
    bm = {b["stage"]: b for b in r["benchmarks"]}
    check("report: benchmark ranges with sources (Day-1 show-up 20% is below the 25–39% range)",
          bm["show_up"]["status"] == "below range" and "Scale For Impact 2026" in bm["show_up"]["source"]
          and bm["conversion"]["status"] == "in range" and "Scale For Impact 2026" in r["sources"], bm.get("show_up"))
    check("report: registrations by source", r["registrations_by_source"] == {"list": 600, "partner:Jo Smith": 250, "social": 150}, r.get("registrations_by_source"))
    md = (w / "debrief.md").read_text()
    check("report --md writes the debrief", "## Results" in md and "## Leaks" in md and "1. **Registrations vs plan**" in md
          and "## What to protect" in md and "## Sources" in md, md[:400])

    # leak ranking moves with the data: a conversion collapse becomes the top leak
    w2 = work / "trk2"; w2.mkdir()
    T2 = lambda *a, codes=(0,): run([PY, TRK, *a], w2, ok_codes=codes)
    T2("init", "--name", "Pricing Webinar", "--format", "webinar", "--days", "1", "--tz", "Europe/London", "--event-date", "2026-11-20",
       "--goal-buyers", "10", "--goal-cash", "9970", "--date", "2026-10-17")
    T2("log-reg", "500"); T2("log-day", "--day", "1", "--live", "200"); T2("log-close", "--present", "160", "--saw-price", "200")
    T2("log-sale", "--tier", "Core", "--price", "997", "--count", "1")
    ok, out, _ = T2("report")
    r = pj(out)
    check("leaks: a conversion collapse ranks first; benchmarks-only plan when no plan.json",
          r["leaks"][0]["stage"] == "conversion" and r["plan_source"].startswith("Build Room benchmarks")
          and r["leaks"][0]["buyers_lost"] > 10, r.get("leaks"))
    g = pj(T2("gate")[1])
    check("gate: night_emails is na for a single-day event", next(i for i in g["items"] if i["id"] == "night_emails")["status"] == "na")
    ok, out, _ = run([PY, TRK, "init", "--name", "Second", "--format", "webinar", "--days", "1", "--tz", "UTC", "--event-date", "2026-12-01",
                      "--goal-buyers", "1", "--goal-cash", "100"], w2)
    ok, out, _ = T2("report", codes=(2,))
    check("tracker: with two ledgers and no --slug the command is refused, naming them", ok and "pass --slug" in out
          and "2026-11-pricing-webinar" in out and "2026-12-second" in out, out[-200:])

    # import-csv: counts only
    w3 = work / "trk3"; w3.mkdir()
    run([PY, TRK, "init", "--name", "CSV Camp", "--format", "bootcamp3", "--days", "3", "--tz", "UTC", "--event-date", "2026-11-10",
         "--goal-buyers", "5", "--goal-cash", "5000"], w3)
    run([PY, TRK, "log-reg", "2"], w3)
    ok, out, _ = run([PY, TRK, "import-csv", FX / "crm_export.csv", "--map",
                      "registered=bootcamp-registered,day1=bootcamp-day1", "day2=bootcamp-day2,day3=bootcamp-day3",
                      "present=bootcamp-present,saw_price=bootcamp-saw-price"], w3)
    d = pj(out)
    check("import-csv: counts rows per tag (case-insensitive, comma or semicolon separated)", ok and d.get("counts") == {
        "registered": 5, "day1": 4, "day2": 2, "day3": 1, "present": 1, "saw_price": 2} and d["rows"] == 6, d.get("counts"))
    data = json.loads((w3 / "launches/2026-11-csv-camp/tracker.json").read_text())
    text = (w3 / "launches/2026-11-csv-camp/tracker.json").read_text()
    check("import-csv: sets the ledger (registrations topped up to the export's total)", sum(x["n"] for x in data["registrations"]) == 5
          and data["days_live"]["2"]["live"] == 2 and data["close"] == {"present": 1, "saw_price": 2, "date": data["close"]["date"]})
    check("import-csv: no names, emails or phone numbers stored", not any(x in text for x in ("Alice", "Zephyrine", "alice@", "+1555", "Mossbright")))
    ok, out, _ = run([PY, TRK, "import-csv", FX / "crm_export.csv", "--map", "registered=*"], w3)
    check("import-csv: * counts every row", pj(out).get("counts") == {"registered": 6})
    ok, out, _ = run([PY, TRK, "import-csv", FX / "crm_export.csv", "--map", "buyers=paid"], w3, ok_codes=(2,))
    check("import-csv: refuses an unknown field", ok and "not one of" in out)
    (w3 / "notags.csv").write_text("Name,Email\nA,a@x.com\n")
    ok, out, _ = run([PY, TRK, "import-csv", "notags.csv", "--map", "registered=x"], w3, ok_codes=(2,))
    check("import-csv: refuses an export without a tags column", ok and "no tags column" in out)
    return w


# ---------------------------------------------------------------- obsidian

def obsidian_tests(work, w):
    T = lambda *a, codes=(0,): run([PY, TRK, *a], w, ok_codes=codes)
    ok, out, _ = T("obsidian", "--vault", "novault", codes=(2,))
    check("obsidian: refuses a vault path that does not exist", ok and "no vault folder" in out)
    (w / "plainfolder").mkdir()
    ok, out, _ = T("obsidian", "--vault", "plainfolder", codes=(2,))
    check("obsidian: refuses a folder without .obsidian", ok and "no .obsidian folder" in out and not (w / "plainfolder/launches").exists())
    ok, out, _ = T("obsidian", "--vault", "plainfolder", "--no-obsidian-check")
    check("obsidian: --no-obsidian-check writes with a warning", ok and any(".obsidian" in x for x in pj(out).get("warnings", []))
          and (w / "plainfolder/launches/2026-11-cash-flow-bootcamp.md").exists())
    V = w / "vault"; (V / ".obsidian").mkdir(parents=True)
    ok, out, _ = T("obsidian", "--vault", "vault", "--lesson", "Book partner podcasts a month earlier")
    note = V / "launches/2026-11-cash-flow-bootcamp.md"
    text = note.read_text() if note.exists() else ""
    check("obsidian: writes launches/YYYY-MM-<slug>.md with light frontmatter", ok and text.startswith(
        "---\ntitle: Cash Flow Bootcamp launch debrief\ntype: launch\ndate: 2026-11-10\nformat: bootcamp3\ntags: [launch, event]\nstatus: debriefed\n"), text[:300])
    check("obsidian: the note has Results, Leaks, Lessons (with --lesson) and What to protect, and names the launch folder",
          all(h in text for h in ("## Results", "## Leaks", "## Lessons", "## What to protect")) and "- Book partner podcasts a month earlier" in text
          and "Launch folder: `" in text and "launches/2026-11-cash-flow-bootcamp`" in text)
    check("obsidian: no founder revenue figures in the member's note", not any(x in text for x in ("$24,831", "$52,705", "25.6", "$54")))
    idx = (V / "launches/_index.md").read_text()
    check("obsidian: creates _index.md with one line for the launch", idx.startswith("# Launches") and idx.count("[[2026-11-cash-flow-bootcamp]]") == 1
          and "1,000 registered · 7 buyers (net of refunds) · $5,259 cash" in idx, idx)
    before = note.read_text()
    ok, out, _ = T("obsidian", "--vault", "vault", codes=(2,))
    check("obsidian: never overwrites an existing note without --force", ok and "--force" in out and note.read_text() == before)
    T("log-sale", "--tier", "VIP", "--price", "2997", "--count", "1")
    ok, out, _ = T("obsidian", "--vault", "vault", "--force", "--status", "final")
    idx = (V / "launches/_index.md").read_text()
    check("obsidian --force: overwrites the note and replaces (not duplicates) its index line",
          ok and pj(out).get("overwrote") and pj(out).get("index_updated") == "replaced" and idx.count("[[2026-11-cash-flow-bootcamp]]") == 1
          and "8 buyers" in idx and "status: final" in note.read_text() and "- Book partner podcasts a month earlier" in note.read_text(), idx)
    (V / "launches/_index.md").write_text(idx + "- 2026-07-27 · [[2026-07-old-camp]] · Old camp\n")
    (V / "launches/2026-07-old-camp.md").write_text("---\ntitle: \"Old camp: July\"\ntype: launch\ndate: 2026-07-27\nformat: bootcamp3\n"
                                                   "tags: [launch, event]\nstatus: final\n---\n# Old camp\n\n## Results\n\n- 969 registered\n\n"
                                                   "## Lessons\n\n- Schedule the Day-1-night email\n\n## Other\n\nx\n")
    (V / "launches/random-note.md").write_text("---\ntype: idea\n---\nnot a launch\n")
    ok, out, _ = T("obsidian-read", "--vault", "vault")
    d = pj(out); ls = d.get("launches", [])
    check("obsidian-read: lists launch notes newest first (non-launch notes and the index skipped)",
          ok and d.get("count") == 2 and [x["frontmatter"]["date"] for x in ls] == ["2026-11-10", "2026-07-27"], [x.get("file") for x in ls])
    check("obsidian-read: frontmatter parsed (quoted title, tag list)", ls[1]["frontmatter"]["title"] == "Old camp: July"
          and ls[1]["frontmatter"]["tags"] == ["launch", "event"], ls[1]["frontmatter"] if len(ls) > 1 else ls)
    check("obsidian-read: returns the Results and Lessons sections", ls[1]["results"] == "- 969 registered"
          and ls[1]["lessons"] == "- Schedule the Day-1-night email" and "| Registered |" in ls[0]["results"]
          and "Book partner podcasts" in ls[0]["lessons"], ls[1] if len(ls) > 1 else ls)
    ok, out, _ = T("obsidian-read", "--vault", "plainfolder", codes=(2,))
    check("obsidian-read: refuses a folder without .obsidian too", ok and "no .obsidian folder" in out)


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="buildroom-launch-tests-"))
    for f in ("launch_plan.py", "event_ics.py", "run_sheet.py", "launch_tracker.py"):
        src = (S / f).read_text(encoding="utf-8")
        check(f"{f}: stdlib only, no bytecode, documented usage", "sys.dont_write_bytecode = True" in src and '"""' in src
              and "Usage" in src and not re.search(r"^\s*(import|from)\s+(requests|urllib3|httpx|socket|http\.client)\b", src, re.M))
        ok, out, _ = run([PY, S / f, "--help"], work)
        check(f"{f} --help prints the usage", ok and "Usage" in out)
    plan_json = plan_tests(work)
    ics_tests(work)
    runsheet_tests(work)
    w = tracker_tests(work, plan_json)
    obsidian_tests(work, w)

    caches = [str(x) for x in list(SK.rglob("__pycache__")) + list(HERE.rglob("__pycache__"))]
    check("no __pycache__ written into the skill folder or the tests", not caches, caches)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
