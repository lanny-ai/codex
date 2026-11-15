#!/usr/bin/env python3
"""Speaking Engine tests: the profile gate, sourced stages, vetting, the pitch check, the pipeline, the
scorecard, the one-sheet, and the places the skill is wired into Build Room OS.

Local only: synthetic files, no network. Nothing is sent anywhere.

Usage:  python3 buildroom/tests/speaking/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-speaking-engine"
S = SK / "scripts"
P, C, O = S / "speak_pipeline.py", S / "pitch_check.py", S / "one_sheet.py"
PY = sys.executable
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:400]}" if detail and not ok else ""))


def run(script, args, cwd):
    p = subprocess.run([PY, str(script)] + [str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except Exception:
        d = {"_raw": p.stdout + p.stderr}
    return p.returncode, d


FILE = """# Build Room Business File

**File version:** 1.10

## 1. Business Snapshot

**Status:** complete · **Updated:** 2026-10-01 · **By:** Ideal Client Avatar

- **Business:** Ledger Lane, pricing help for bookkeeping firm owners in Ohio
- **Goals:** 12 new clients for the pricing program this year
- **Retired lines:** "work smarter not harder"

## 2. Ideal Client Avatar

**Status:** complete · **Updated:** 2026-10-01 · **By:** Ideal Client Avatar

- **Who:** owners of bookkeeping firms with two to five staff who bill by the hour and are worn out
- **Pain stack:** every new client means more hours; they cannot raise prices without losing people

## 3. Signature Offer

**Status:** provisional · **Updated:** 2026-10-02 · **By:** Signature Offer

- **Offer:** the Value Pricing Sprint, six weeks to move one service from hourly to a fixed price
- **Phase 1:** price one service → outcome: a written price the owner can say out loud

## 18. Advertising

**Status:** complete · **Updated:** 2026-10-03 · **By:** Proof Engine

- **Proof vault:** 14 years as a bookkeeper; 31 firm owners through the sprint
- **Never-say claims:** "double your income"

## 8. Session Log
"""

PITCH = """Hello Dana,

Your members at the Ohio Bookkeepers Association keep hearing that hourly billing caps their income. I have a 20 minute talk, Stop Billing By The Hour, where each owner leaves with a price for one service.

Would it fit one of your lunches next spring? If it is not a fit this year, just say so.

Pat
"""
BAD = ("My name is Pat, an award-winning keynote speaker who has helped 500 firms grow 300%. [Your Name] — act now! "
       "\"Pat changed my whole business in a week, truly amazing\"\n")


def setup(work, name, ready=True):
    w = work / name
    w.mkdir()
    (w / "BUILDROOM_BUSINESS_FILE.md").write_text(FILE, encoding="utf-8")
    run(P, ["init", "--today", "2026-11-02"], w)
    if ready:
        for k, t in [("expertise", "I help bookkeepers price by value"), ("audience", "owners of small bookkeeping firms"),
                     ("goal", "clients for my pricing program"), ("topics", "value pricing for bookkeepers"),
                     ("regions", "Columbus and Dayton, Ohio")]:
            run(P, ["answer", "--key", k, "--text", t], w)
        run(P, ["ready"], w)
        run(P, ["talk", "add", "--title", "Stop Billing By The Hour", "--promise", "Leave with a price for one service",
                "--takeaway", "why hours cap income", "--takeaway", "the three price anchors", "--takeaway", "one price, said out loud",
                "--for", "bookkeeping firm owners", "--length", "20,45"], w)
    return w


def add_stage(w, name="Ohio Bookkeepers Lunch", host="Ohio Bookkeepers Association", kind="association",
              source="https://example.org/events", extra=()):
    return run(P, ["add", "--name", name, "--host", host, "--kind", kind, "--source", source, "--seen", "2026-11-01",
                   "--audience", "bookkeeping firm owners", "--size", "40", "--pays", "no", *extra], w)


def vet(w, sid, *extra, scores=(5, 4, 4, 3)):
    a, d, o, t = scores
    return run(P, ["vet", "--id", sid, "--audience", a, "--decider", d, "--offer", o, "--timing", t, "--checked", "site read 2026-11-01", *extra], w)


def profile_tests(work):
    w = setup(work, "profile", ready=False)
    code, d = run(P, ["intake"], w)
    check("intake: seventeen questions, four of them core", d.get("of") == 17 and d.get("core_missing") == ["expertise", "audience", "goal", "topics"], d)
    code, d = run(P, ["prefill"], w)
    drafted = {x["key"] for x in d.get("draft_from_file", [])}
    check("prefill: drafts come from filled sections of the Business File", {"expertise", "audience", "topics"} <= drafted, drafted)
    check("prefill: a provisional section is named as provisional", "§3" in d.get("provisional_sections", []), d.get("provisional_sections"))
    check("prefill: what only the member knows is asked, not drafted",
          {"experience", "paid", "availability"} <= {x["key"] for x in d.get("ask_the_member", [])})
    check("prefill: the rule against filling gaps is stated", "never fill a gap" in d.get("rule", ""))
    blank = work / "blank"
    blank.mkdir()
    shutil.copy(ROOT / "templates/BUILDROOM_BUSINESS_FILE.md", blank / "BUILDROOM_BUSINESS_FILE.md")
    run(P, ["init"], blank)
    code, d = run(P, ["prefill"], blank)
    check("prefill: a blank template offers no drafts", d.get("draft_from_file") == [] and len(d.get("ask_the_member", [])) == 17, d.get("draft_from_file"))
    code, d = run(P, ["answer", "--key", "expertise", "--text", "I help bookkeepers price by value", "--draft", "--from", "§3"], w)
    check("answer: a draft from the file is marked as a draft", d.get("draft") is True, d)
    for k, t in [("audience", "owners of small bookkeeping firms"), ("goal", "clients"), ("topics", "value pricing"), ("regions", "Columbus, Ohio")]:
        run(P, ["answer", "--key", k, "--text", t], w)
    code, d = run(P, ["ready"], w)
    check("ready: refuses while a draft is unconfirmed", code == 1 and "expertise" in json.dumps(d), d)
    code, d = run(P, ["confirm", "--all", "--by", "claude"], w)
    check("confirm: only the member confirms a draft", code == 1 and "member" in d.get("error", ""), d)
    code, d = run(P, ["confirm", "--all", "--by", "member"], w)
    check("confirm: the member's confirmation clears the draft", d.get("confirmed") == ["expertise"] and d.get("still_draft") == [], d)
    code, d = run(P, ["ready"], w)
    check("ready: passes once the core answers and a place are in", code == 0 and d.get("ready") is True, d)
    w2 = setup(work, "noplace", ready=False)
    for k in ("expertise", "audience", "goal", "topics"):
        run(P, ["answer", "--key", k, "--text", "something real about " + k], w2)
    code, d = run(P, ["ready"], w2)
    check("ready: refuses with nowhere to look", code == 1 and "where" in d.get("error", ""), d)
    code, d = add_stage(w2)
    check("add: refuses before the profile is ready", code == 1 and "not ready" in d.get("error", ""), d)
    code, d = run(P, ["answer", "--key", "nonsense", "--text", "x"], w2)
    check("answer: an unknown key is refused", code != 0, d)


def stage_tests(work):
    w = setup(work, "stages")
    code, d = add_stage(w, source="made it up")
    check("add: a stage without a real source is refused", code == 1 and "never list one from memory" in d.get("error", ""), d)
    code, d = run(P, ["add", "--name", "X", "--host", "Y", "--kind", "association", "--source", "https://example.org", "--seen", "2026-11-01"], w)
    check("add: a stage needs a name, a host and an audience", code == 1 and "--audience" in d.get("error", ""), d)
    code, d = add_stage(w)
    check("add: a sourced stage is added as found", d.get("id") == "ST-001" and d.get("status") == "found", d)
    check("add: the privacy note keeps contact names out of the file", "only the role" in d.get("privacy", ""), d)
    code, d = add_stage(w, name="Global Leaders Summit", host="GLS Events", kind="conference", source="member knows it: an email they received")
    check("add: 'member knows it' is an accepted source", d.get("id") == "ST-002", d)
    code, d = run(P, ["pitch", "--id", "ST-001", "--channel", "email"], w)
    check("pitch: refused before vetting", code == 1 and "not been vetted" in d.get("error", ""), d)
    code, d = vet(w, "ST-001")
    check("vet: fit is the weighted score out of 5", d.get("fit") == 4.25 and d.get("pitchable") is True, d)
    code, d = vet(w, "ST-002", "--flag", "pay_to_speak", scores=(1, 1, 1, 1))
    check("vet: a red flag makes a stage not pitchable", d.get("pitchable") is False and "pay_to_speak" in json.dumps(d.get("flags")), d)
    code, d = run(P, ["pitch", "--id", "ST-002", "--channel", "email"], w)
    check("pitch: refused for a flagged stage", code == 1, d)
    code, d = vet(w, "ST-002", "--flag", "pay_to_speak", "--accept-risk", "--by", "claude", scores=(1, 1, 1, 1))
    check("vet: only the member accepts a red flag", code == 1, d)
    code, d = vet(w, "ST-002", "--flag", "not_a_flag", scores=(1, 1, 1, 1))
    check("vet: an unknown flag is refused", code == 1, d)
    code, d = run(P, ["flags"], w)
    check("flags: ten red flags, pay-to-speak first", len(d.get("red_flags", {})) == 10 and list(d["red_flags"])[0] == "pay_to_speak", d)
    code, d = run(P, ["rank"], w)
    check("rank: best fit first, and it says it does not predict", d["stages"][0]["id"] == "ST-001" and "does not predict" in d.get("note", ""), d)
    code, d = run(P, ["drop", "--id", "ST-002", "--reason", "pay to speak"], w)
    code, d = run(P, ["list", "--status", "dropped"], w)
    check("drop: a dropped stage is kept on the list as dropped", d.get("count") == 1 and d["stages"][0]["id"] == "ST-002", d)
    data = json.loads((w / "speaking/pipeline.json").read_text())
    blob = json.dumps(data)
    check("pipeline: no email address is stored", not re.search(r"[\w.+-]+@[\w-]+\.\w+", blob))


def check_tests(work):
    w = setup(work, "check")
    add_stage(w)
    vet(w, "ST-001")
    (w / "p.txt").write_text(PITCH, encoding="utf-8")
    (w / "bad.txt").write_text(BAD, encoding="utf-8")
    code, d = run(C, ["check", "--file", "p.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    check("check: a plain pitch in the member's own facts is CLEAN", code == 0 and d.get("verdict") == "CLEAN" and d.get("watch") == 0, d)
    check("check: it says what a script cannot tell", "cannot tell" in d.get("limits", ""))
    code, d = run(C, ["check", "--file", "bad.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    ids = {i["id"] for i in d.get("items", [])}
    for want in ("placeholders", "dashes", "unsourced_numbers", "unsupported_claims", "unsourced_quote", "pressure", "no_ask", "not_about_them", "no_talk"):
        check(f"check: a bad pitch is caught for {want}", want in ids, ids)
    msg = next((i["message"] for i in d.get("items", []) if i["id"] == "unsourced_numbers"), "")
    check("check: '500 firms' and '300%' are both named", "500 firms" in msg and "300%" in msg, msg)
    check("check: FIX exits 1", code == 1)
    (w / "own.txt").write_text("Dana, I have spent 14 years as a bookkeeper and taken 31 firm owners through this. Would Stop Billing By The Hour "
                               "suit the Ohio Bookkeepers Association? If it is not a fit, just say so.\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "own.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    check("check: the member's own figures from the Business File pass", code == 0, d)
    (w / "stagefact.txt").write_text("Dana, your 40 members at the Ohio Bookkeepers Association would each leave Stop Billing By The Hour with a price. "
                                     "Would it fit? If it is not a fit, just say so.\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "stagefact.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    check("check: the stage's own audience size is allowed", code == 0, d)
    (w / "banned.txt").write_text("Dana, the Ohio Bookkeepers Association could work smarter not harder with Stop Billing By The Hour. "
                                  "Would it fit? If it is not a fit, just say so.\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "banned.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    check("check: a retired line from the Business File is a FIX", "banned_line" in {i["id"] for i in d.get("items", [])}, d)
    (w / "self.txt").write_text("Hi Dana, my name is Pat and I would like to speak at the Ohio Bookkeepers Association on Stop Billing By The Hour. "
                                "I attached my sheet. Would that work?\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "self.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    ids = {i["id"] for i in d.get("items", [])}
    check("check: opening on the speaker, an attachment and no easy no are WATCH items", {"opens_on_speaker", "attachment", "no_easy_no"} <= ids and code == 0, d)
    (w / "long.txt").write_text(("The Ohio Bookkeepers Association matters. " * 60) + "Stop Billing By The Hour? If not, just say so.\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "long.txt", "--kind", "pitch", "--stage", "ST-001"], w)
    check("check: a pitch far too long is a FIX", "too_long" in {i["id"] for i in d.get("items", [])}, d)
    code, d = run(C, ["check", "--file", "nope.txt", "--kind", "pitch"], w)
    check("check: a missing file is a usage error", code == 2, d)
    code, d = run(C, ["check", "--file", "p.txt", "--kind", "pitch", "--stage", "ST-099"], w)
    check("check: an unknown stage is a usage error", code == 2, d)
    (w / "bio.txt").write_text("Pat is a certified, best-selling author featured in Forbes.\n", encoding="utf-8")
    code, d = run(C, ["check", "--file", "bio.txt", "--kind", "bio"], w)
    check("check: status claims the member never made are a FIX in a bio", code == 1 and "unsupported_claims" in {i["id"] for i in d.get("items", [])}, d)
    # a filed pitch must pass the same check
    code, d = run(P, ["pitch", "--id", "ST-001", "--channel", "email", "--text-file", "bad.txt", "--today", "2026-11-03"], w)
    check("pitch: a message that fails the check is not filed", code == 1 and "pitch_check" in d.get("error", ""), d)
    check("pitch: nothing was written for the refused pitch", not (w / "speaking/pitches/ST-001-1.txt").exists())
    code, d = run(P, ["pitch", "--id", "ST-001", "--channel", "email", "--text-file", "p.txt", "--today", "2026-11-03"], w)
    check("pitch: a clean pitch is filed and the follow-up dated a week out", d.get("status") == "pitched" and d.get("follow_up_due") == "2026-11-10"
          and (w / "speaking/pitches/ST-001-1.txt").exists(), d)
    check("pitch: it says the member sends it themselves", "sends it themselves" in d.get("note", ""))
    code, d = run(P, ["follow", "--id", "ST-001", "--text-file", "bad.txt", "--today", "2026-11-10"], w)
    check("follow: a follow-up that fails the check is not filed", code == 1, d)


def pipeline_tests(work):
    w = setup(work, "pipe")
    add_stage(w)
    vet(w, "ST-001")
    run(P, ["pitch", "--id", "ST-001", "--channel", "email", "--today", "2026-11-03"], w)
    code, d = run(P, ["pitch", "--id", "ST-001", "--channel", "email", "--today", "2026-11-03"], w)
    check("pitch: a second first pitch is refused", code == 1 and "follow" in d.get("error", ""), d)
    code, d = run(P, ["follow", "--id", "ST-001", "--today", "2026-11-05"], w)
    check("follow: refused inside seven days", code == 1 and "wait 7" in d.get("error", ""), d)
    code, d = run(P, ["today", "--today", "2026-11-10"], w)
    check("today: the follow-up comes due on its day", any(x.get("id") == "ST-001" for x in d.get("due", [])), d)
    code, d = run(P, ["follow", "--id", "ST-001", "--today", "2026-11-10"], w)
    check("follow: the first follow-up is recorded", d.get("touch") == 2 and d.get("follow_ups_left") == 1, d)
    code, d = run(P, ["follow", "--id", "ST-001", "--today", "2026-11-17"], w)
    check("follow: the second is the last", d.get("follow_ups_left") == 0, d)
    code, d = run(P, ["follow", "--id", "ST-001", "--today", "2026-11-24"], w)
    check("follow: a third follow-up is refused", code == 1 and "pestering" in d.get("error", ""), d)
    code, d = run(P, ["reply", "--id", "ST-001", "--outcome", "later"], w)
    check("reply: 'later' needs a date", code == 1 and "--ask-again" in d.get("error", ""), d)
    code, d = run(P, ["reply", "--id", "ST-001", "--outcome", "yes", "--today", "2026-11-26"], w)
    check("reply: a yes points to getting terms in writing", "in writing" in d.get("next", ""), d)
    code, d = run(P, ["book", "--id", "ST-001", "--when", "2027-03-10", "--today", "2026-11-26"], w)
    check("book: warns when no terms are recorded and hands the full talk to the Webinar Builder",
          d.get("status") == "booked" and any("in writing" in x for x in d.get("warnings", [])) and "Webinar Builder" in d.get("next", ""), d)
    code, d = run(P, ["deliver", "--id", "ST-001", "--attended", "38", "--leads", "9", "--today", "2027-03-10"], w)
    check("deliver: leads are counted, never estimated", "never estimated" in d.get("note", ""), d)
    code, d = run(P, ["after", "--id", "ST-001", "--clients", "2", "--thanked", "--today", "2027-03-20"], w)
    check("after: what is still owed to the host is listed", len(d.get("still_to_do", [])) == 2, d)
    code, d = run(P, ["debrief", "--id", "ST-001", "--well", "the pricing exercise", "--improve", "ran long", "--confidence", "7", "--today", "2027-03-11"], w)
    check("debrief: one change is carried to next time", d.get("next_time") == "ran long", d)
    code, d = run(P, ["goal", "--talks-per-month", "2", "--clients-per-quarter", "3"], w)
    check("goal: a target is not a forecast", "not a forecast" in d.get("note", ""), d)
    code, d = run(P, ["report", "--today", "2027-03-21"], w)
    fs = d.get("from_the_stage", {})
    check("report: the counts are the member's own", fs.get("talks_given") == 1 and fs.get("people_in_rooms") == 38 and fs.get("leads") == 9 and fs.get("clients") == 2, d)
    check("report: no rate is judged from under ten pitches", "too few to judge" in d.get("read", "") and d.get("weakest_step") == "", d)
    check("report: a rate is shown with its two numbers", d.get("replies") == "1 of 1 pitches answered", d)
    check("report: the change from the last debrief is read back", "ran long" in d.get("change_next_time", ""), d)
    check("report: progress is shown against the member's goal", "the goal is 2 a month" in d.get("against_the_goal", {}).get("talks", ""), d)
    code, d = run(P, ["plan", "--weeks", "12", "--start", "2026-11-04"], w)
    check("plan: starts on the next Monday and promises no booking", d["weeks"][0]["monday"] == "2026-11-09" and "does not promise" in d.get("note", "")
          and (w / "speaking/plan.md").exists(), d)
    code, d = run(P, ["plan", "--weeks", "2"], w)
    check("plan: four to twenty-six weeks", code == 1, d)
    (w / "speaking/pipeline.json").write_text("{ not json", encoding="utf-8")
    code, d = run(P, ["list"], w)
    check("pipeline: a broken file refuses cleanly", code != 0 and "not valid JSON" in d.get("error", ""), d)


def sheet_tests(work):
    w = setup(work, "sheet")
    code, d = run(O, ["template"], w)
    tp = w / "speaking/one-sheet/one-sheet.json"
    check("one-sheet: the template is written", tp.exists(), d)
    code, d = run(O, ["build"], w)
    check("one-sheet: an empty sheet is not built", code == 1 and d.get("written") is False and "no bio" in d.get("fix", []), d)
    good = {"name": "Pat Rivers", "tagline": "Pricing help for bookkeeping firm owners",
            "bio": "Pat Rivers has spent 14 years as a bookkeeper and has taken 31 firm owners through the Value Pricing Sprint.",
            "audiences": ["bookkeeping firm owners"], "formats": ["talk", "workshop"], "credentials": ["14 years as a bookkeeper"],
            "talks": [1], "testimonials": [], "contact": {"email": "", "booking_link": "https://example.com/book"}, "based_in": "Columbus, Ohio"}
    tp.write_text(json.dumps(good), encoding="utf-8")
    code, d = run(O, ["build"], w)
    out = next(iter((w / "speaking/one-sheet").glob("*.html")), None)
    check("one-sheet: a sheet from the member's own facts is built", code == 0 and d.get("written") and out is not None, d)
    html = out.read_text(encoding="utf-8") if out else ""
    check("one-sheet: the talk and its takeaways are on the page", "Stop Billing By The Hour" in html and "the three price anchors" in html)
    bad = dict(good, bio="Pat Rivers is an award-winning speaker who has helped 900 companies.")
    tp.write_text(json.dumps(bad), encoding="utf-8")
    code, d = run(O, ["build"], w)
    fx = " | ".join(d.get("fix", []))
    check("one-sheet: an invented figure and an invented award are refused", code == 1 and "900 companies" in fx and "award-winning" in fx, d)
    q = dict(good, testimonials=[{"proof_id": "", "quote": "Best talk we ever had", "attribution": "Dana"}])
    tp.write_text(json.dumps(q), encoding="utf-8")
    code, d = run(O, ["build"], w)
    check("one-sheet: a testimonial without a proof bank ID is refused", code == 1 and "proof bank ID" in " ".join(d.get("fix", [])), d)
    q = dict(good, testimonials=[{"proof_id": "P-07", "quote": "Best talk we ever had", "attribution": "Dana"}])
    tp.write_text(json.dumps(q), encoding="utf-8")
    code, d = run(O, ["build"], w)
    check("one-sheet: a proof ID that is not in the bank is refused", code == 1 and "P-07" in " ".join(d.get("fix", [])), d)
    long_bio = dict(good, bio="Pat Rivers helps bookkeeping firm owners. " * 30)
    tp.write_text(json.dumps(long_bio), encoding="utf-8")
    code, d = run(O, ["build"], w)
    check("one-sheet: a bio over 120 words is refused", code == 1 and "120 at most" in " ".join(d.get("fix", [])), d)


def wiring_tests():
    rd = lambda p: (ROOT / p).read_text(encoding="utf-8")  # noqa: E731
    skill = rd("skills/buildroom-speaking-engine/SKILL.md")
    refs = {p.name for p in (SK / "references").glob("*.md")}
    named = set(re.findall(r"references/([a-z0-9-]+\.md)", skill))
    check("skill: every reference SKILL.md names exists", named <= refs, named - refs)
    check("skill: every reference file is named in SKILL.md", refs <= named, refs - named)
    for script in ("speak_pipeline.py", "pitch_check.py", "one_sheet.py"):
        check(f"skill: SKILL.md names {script}", script in skill)
    fm = skill.split("---")[1]
    check("skill: the description is within the 1024-character limit", len(re.search(r"description: \|\n(.*)", fm, re.S).group(1).strip()) <= 1024)
    check("skill: the course's author is credited only in source-credit.md",
          "Tracy" not in "".join(p.read_text(encoding="utf-8") for p in (SK / "references").glob("*.md")
                                 if p.name not in ("source-credit.md",)) and "Tracy" not in skill)
    check("skill: the engine never sends for the member", "sends every message themselves" in skill)
    tpl = rd("templates/BUILDROOM_BUSINESS_FILE.md")
    check("template: §24 Speaking sits before the session log", 0 < tpl.find("## 24. Speaking") < tpl.find("## 8. Session Log"))
    check("template: version 1.10", "**File version:** 1.10" in tpl)
    check("template: the skill's copy matches", rd("skills/buildroom-speaking-engine/references/business-file-template.md") == tpl)
    spec = rd("BUSINESS-FILE-SPEC.md")
    check("spec: §24 is registered at version 1.10", "| 24 | Speaking | Speaking Engine |" in spec and "**Version 1.10" in spec)
    check("viewer: §24 is in the section map", '24:{t:"Speaking"' in rd("rollout/Business_File_Viewer.html"))
    road = rd("skills/buildroom-os/references/roadmap.md")
    check("roadmap: the Speaking Engine has a section and trigger phrases", "### Speaking — Speaking Engine" in road and '- Speaking Engine → "Get me speaking gigs"' in road)
    check("navigator: the progress view runs to §24", "§14–§24" in rd("skills/buildroom-os/SKILL.md"))
    cl, sh = rd("rollout/universal/CLAUDE.md"), rd("rollout/universal/START-HERE.md")
    check("CLAUDE.md: the skill, the range and the speaking rule", "`buildroom-speaking-engine` (§24" in cl and "§1–§24" in cl and "- **Speaking:**" in cl and "Forty skills" in cl)
    check("START-HERE: forty skills, twenty-four sections", "forty skills" in sh and "twenty-four sections" in sh)
    for doc in ("README.md", "rollout/MEMBER-README.md"):
        check(f"{doc}: lists the skill", "`buildroom-speaking-engine`" in rd(doc))
    check("Quick Start: the phrase is there", "Get me speaking gigs" in rd("rollout/BuildRoom_OS_Quick_Start.html"))
    check("protocol: forty sessions", "40 standalone sessions" in rd("shared/business-file-protocol.md"))
    skills = [p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()]
    check("there are forty skills", len(skills) == 40, len(skills))
    caches = [str(x) for x in SK.rglob("__pycache__")]
    check("no __pycache__ written into the skill folder", not caches, caches)


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="speaking-tests-"))
    profile_tests(work)
    stage_tests(work)
    check_tests(work)
    pipeline_tests(work)
    sheet_tests(work)
    wiring_tests()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
