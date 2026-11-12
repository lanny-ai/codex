#!/usr/bin/env python3
"""Webinar Builder tests: the outline and render, the run-sheet hand-off to the Event Launcher, the offer
one-pager, the slide builder and inspector, the go-live check (every critical item made to fail once), the
rehearsal and run reviews, the diagnosis, the evergreen gate, and consistency and privacy across the skill.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/webinar/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import copy, json, re, shutil, subprocess, tempfile, zipfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-webinar-builder"
if not SK.exists():
    SK = ROOT / "drafts/buildroom-webinar-builder"
S, R, FX = SK / "scripts", SK / "references", HERE / "fixtures"
PY = sys.executable
PLAN, SLIDES, CHECK, REVIEW = S / "webinar_plan.py", S / "slide_builder.py", S / "webinar_check.py", S / "webinar_review.py"
RUNSHEET = ROOT / "skills/buildroom-event-launcher/scripts/run_sheet.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:600]}" if detail and not ok else ""))


def run(args, cwd):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    return p.returncode, p.stdout + p.stderr


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


FIXTURE = json.loads((FX / "webinar.json").read_text())


def seg(w, sid):
    return next(s for s in w["segments"] if s["id"] == sid)


# ---------------------------------------------------------------- plan

def plan_tests(tmp):
    cwd = tmp / "plan"
    cwd.mkdir()
    rc, out = run([PY, PLAN, "formats"], cwd)
    f = pj(out)
    check("formats: five formats listed", rc == 0 and set(f) == {"live60", "broadcast3", "interview", "paidclass", "bootcamp"}, out)
    for fmt, extra in (("live60", []), ("broadcast3", []), ("interview", []), ("paidclass", []), ("paidclass", ["--length", "120"]),
                       ("bootcamp", ["--day", "1"]), ("bootcamp", ["--day", "2"]), ("bootcamp", ["--day", "3", "--length", "180"])):
        o = cwd / f"{fmt}{''.join(extra)}.json"
        rc, out = run([PY, PLAN, "outline", "--format", fmt, "--title", "T", "--date", "2026-12-03", "--start", "14:00",
                       "--tz", "America/Los_Angeles", "--out", o] + extra, cwd)
        w = json.loads(o.read_text()) if o.exists() else {}
        body = [s for s in w.get("segments", []) if s["kind"] != "lobby"]
        tot = sum(s["min"] for s in body)
        check(f"outline {fmt} {' '.join(extra)}: minutes add up to the length and end on the close or a recap",
              rc == 0 and tot == w["length_min"] and body[-1]["kind"] in ("close", "recap", "qa"), (rc, tot, w.get("length_min")))
        teach = [s for s in body if s["kind"] == "teach"]
        check(f"outline {fmt} {' '.join(extra)}: three teaching blocks, each with a belief and a loop",
              len(teach) == 3 and all(s.get("loop") and s.get("belief") in (1, 2, 3) for s in teach))
    w = json.loads((cwd / "live60.json").read_text())
    st, t = {}, 0
    for s in w["segments"]:
        if s["kind"] != "lobby":
            st[s["id"]] = t
            t += s["min"]
    check("live60: the offer starts at minute 40 and the Q&A runs to 58", st["offer"] == 40 and st["qa"] == 50 and st["close"] == 58, st)
    check("live60: the lobby runs before the start and is not counted", w["segments"][0]["kind"] == "lobby" and t == 60)
    check("outline: the qa bank starts with time, money, confidence and the spouse",
          [q["objection"] for q in w["qa_bank"]] == ["time", "money", "confidence", "spouse"])
    check("outline: placeholders mark what is left to write", "[write:" in json.dumps(w))
    check("outline --close call: the offer block invites a booking",
          run([PY, PLAN, "outline", "--format", "live60", "--title", "T", "--date", "2026-12-03", "--start", "14:00", "--tz", "UTC",
               "--close", "call", "--out", cwd / "call.json"], cwd)[0] == 0
          and seg(json.loads((cwd / "call.json").read_text()), "offer")["links"] == ["booking"])
    for bad, why in ((["--format", "nope"], "format"), (["--date", "12/03/2026"], "date"), (["--start", "2pm"], "start"),
                     (["--day", "2"], "--day without bootcamp")):
        args = {"--format": "live60", "--title": "T", "--date": "2026-12-03", "--start": "14:00", "--tz": "UTC", "--out": str(cwd / "x.json")}
        args.update(dict(zip(bad[::2], bad[1::2])))
        rc, out = run([PY, PLAN, "outline"] + [x for kv in args.items() for x in kv], cwd)
        check(f"outline refuses a bad {why}", rc == 2 and not pj(out).get("ok", True), out)
    launch = cwd / "launches/2026-12-price"
    rc, out = run([PY, PLAN, "outline", "--format", "live60", "--title", "T", "--date", "2026-12-03", "--start", "14:00",
                   "--tz", "UTC", "--launch", launch], cwd)
    check("outline --launch writes launches/<slug>/webinar/webinar.json", rc == 0 and (launch / "webinar/webinar.json").exists(), out)
    rc, out = run([PY, PLAN, "outline", "--format", "live60", "--title", "T2", "--date", "2026-12-03", "--start", "14:00",
                   "--tz", "UTC", "--launch", launch], cwd)
    check("outline refuses to overwrite a talk without --force", rc == 1 and json.loads((launch / "webinar/webinar.json").read_text())["title"] == "T")
    rc, _ = run([PY, PLAN, "outline", "--format", "bootcamp", "--day", "2", "--title", "C", "--date", "2026-12-04", "--start", "10:00",
                 "--tz", "UTC", "--launch", launch], cwd)
    check("outline bootcamp --day 2 --launch writes webinar/day-2/", rc == 0 and (launch / "webinar/day-2/webinar.json").exists())

    # render
    sp = cwd / "fx/webinar.json"
    sp.parent.mkdir()
    shutil.copy(FX / "webinar.json", sp)
    rs = cwd / "fx/runsheet.json"
    rc, out = run([PY, PLAN, "render", "--spec", sp, "--runsheet", rs, "--close", FX / "close.md"], cwd)
    r = pj(out)
    names = ("script.md", "speaker-notes.md", "moderator-sheet.md", "qa-bank.md")
    check("render writes the script, notes, moderator sheet and Q&A bank", rc == 0 and all((sp.parent / n).exists() for n in names), out)
    check("render: a finished talk has no placeholders left", r.get("placeholders_left") == 0 and r.get("offer_at_min") == 40, r)
    sc = (sp.parent / "script.md").read_text()
    check("script.md: plain clock times with the zone (2:40 p.m. offer, 2:58 p.m. close, Pacific)",
          "## 2:40 p.m.–2:50 p.m. · The offer" in sc and "2:58 p.m.–3:00 p.m." in sc and "Pacific" in sc, sc[:300])
    check("script.md: proof by ID and class with the typical result", "P-02 · class B · typical:" in sc)
    check("script.md: each loop's question and answer", "Do you need more clients? → No." in sc)
    mod = (sp.parent / "moderator-sheet.md").read_text()
    check("moderator sheet: time calls 10 minutes before the offer, 10 and 2 minutes left",
          "2:30 p.m.: \"10 minutes to the offer\"" in mod and "2:50 p.m.: \"10 minutes left\"" in mod and "2:58 p.m." in mod, mod[-600:])
    check("moderator sheet: the setup list, co-host, and the bank's questions to bring forward",
          "## Setup list" in mod and "co-host" in mod and "I need to talk to my husband first (spouse)" in mod)
    check("moderator sheet: offer links only from the offer, never during the trial close",
          not re.search(r"Transition[^\n]*example\.com/checkout", mod) and re.search(r"The offer\*\*:[^\n]*example\.com/checkout", mod))
    check("moderator sheet: the backup link is for a failed checkout only", "only if the main link fails" in mod)
    check("moderator sheet: never type a count, a poll result or a question not asked", "Never type an attendee count" in mod)
    notes = (sp.parent / "speaker-notes.md").read_text()
    check("speaker notes: prompts, the minute to be at, and the loop", "you should be at minute 12" in notes and "Close the loop:" in notes)
    qa = (sp.parent / "qa-bank.md").read_text()
    check("qa-bank.md: each objection with its door", qa.count("**Door:**") == 4 and "## Spouse" in qa)
    rsj = json.loads(rs.read_text())
    day = rsj["days"][0]
    check("runsheet: one webinar day with the lobby, a checkout test 30 minutes before, roles and links merged",
          len(rsj["days"]) == 1 and day["webinar"] and day["checkout_test"] == "13:30" and day["segments"][0]["kind"] == "lobby"
          and rsj["roles"]["moderator"] == "Sam Ruiz" and "checkout" in rsj["links"], day)
    check("runsheet: kinds map to the Event Launcher's (the transition teaches; only the offer is a pitch)",
          [s["kind"] for s in day["segments"]][6:10] == ["teach", "teach", "pitch", "qa"], [s["kind"] for s in day["segments"]])
    check("runsheet: the real deadline from close.md", rsj.get("deadline", "").startswith("enrolment closes January 9"), rsj.get("deadline"))
    check("runsheet: prompts joined as sentences", ". " in day["segments"][2]["notes"])
    rc, out = run([PY, RUNSHEET, "build", "--spec", rs, "--out", cwd / "fx/run-sheet.md"], cwd)
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("run_sheet.py accepts the webinar day: recording notice, roles, backup and checkout test pass",
          rc in (0, 1) and all(ch.get(k, {}).get("ok") for k in ("recording_notice", "roles_assigned", "backup_link",
                                                                  "checkout_before_close", "links_have_values")), out[-500:])
    check("run_sheet.py: first build is a should (not a must) for a single webinar day",
          ch.get("first_build", {}).get("level") == "should", ch.get("first_build"))
    run([PY, PLAN, "render", "--spec", sp, "--runsheet", rs, "--close", FX / "close.md"], cwd)
    check("render again replaces the same day instead of adding one", len(json.loads(rs.read_text())["days"]) == 1)
    # placeholders from a first render are replaced once the member fills them in
    w0 = copy.deepcopy(FIXTURE)
    w0["roles"]["moderator"] = "[write: moderator's name]"
    (cwd / "fx/w0.json").write_text(json.dumps(w0))
    rs2 = cwd / "fx/rs2.json"
    run([PY, PLAN, "render", "--spec", cwd / "fx/w0.json", "--out-dir", cwd / "fx/o0", "--runsheet", rs2], cwd)
    rc, out = run([PY, PLAN, "render", "--spec", sp, "--out-dir", cwd / "fx/o1", "--runsheet", rs2], cwd)
    check("render: a placeholder role in runsheet.json is replaced by the filled-in one",
          json.loads(rs2.read_text())["roles"]["moderator"] == "Sam Ruiz", rs2.read_text()[:300])
    w1 = copy.deepcopy(FIXTURE)
    w1["roles"]["moderator"] = "Lee Park"
    (cwd / "fx/w1.json").write_text(json.dumps(w1))
    rc, out = run([PY, PLAN, "render", "--spec", cwd / "fx/w1.json", "--out-dir", cwd / "fx/o2", "--runsheet", rs2], cwd)
    check("render: a real role that differs is kept and reported as a conflict",
          json.loads(rs2.read_text())["roles"]["moderator"] == "Sam Ruiz" and pj(out).get("conflicts"), out)
    el = cwd / "fx/el.json"
    el.write_text(json.dumps({"title": "Camp", "days": [{"date": "2026-12-03", "start": "10:00", "segments": [{"min": 5, "title": "x", "kind": "teach"}]}]}))
    rc, out = run([PY, PLAN, "render", "--spec", sp, "--out-dir", cwd / "fx/o3", "--runsheet", el], cwd)
    check("render refuses to replace a day the Event Launcher wrote, without --force",
          rc == 1 and json.loads(el.read_text())["days"][0]["start"] == "10:00", out)
    rc, _ = run([PY, PLAN, "render", "--spec", sp, "--out-dir", cwd / "fx/o3", "--runsheet", el, "--force"], cwd)
    check("render --force replaces it", rc == 0 and json.loads(el.read_text())["days"][0].get("webinar"))
    bad = cwd / "fx/bad.json"
    w2 = copy.deepcopy(FIXTURE)
    w2["segments"][3]["kind"] = "sermon"
    bad.write_text(json.dumps(w2))
    check("render refuses an unknown segment kind", run([PY, PLAN, "render", "--spec", bad], cwd)[0] == 2)

    # offer summary
    rc, out = run([PY, PLAN, "offer-summary", "--close", FX / "close.md", "--out", cwd / "offer-summary.md"], cwd)
    osu = (cwd / "offer-summary.md").read_text() if (cwd / "offer-summary.md").exists() else ""
    check("offer-summary: prices, plan total, guarantee and deadline copied word for word",
          rc == 0 and "$1,997 in full, or 4 payments of $549 ($2,196 total)" in osu and "enrolment closes January 9" in osu, osu)
    check("offer-summary: the moderator-only backup link is left out", "example.com/pay" not in osu and "Backup" not in osu)
    check("offer-summary: internal wording left out (close mode, sign-off note)", "Close mode" not in osu and "signed off" not in osu, osu)
    multi = cwd / "close-multi.md"
    multi.write_text("- **Close mode:** checkout\n- Done-with-you: $3,997, or 3 payments of $1,399 ($4,197 total) · checkout and backup on the sheet\n"
                     "- Internal audit package: $4,500\n- Backup payment link (moderator only): https://x\n")
    rc, out = run([PY, PLAN, "offer-summary", "--close", multi, "--out", cwd / "o3.md"], cwd)
    o3 = (cwd / "o3.md").read_text() if (cwd / "o3.md").exists() else ""
    check("offer-summary keeps a door whose line merely mentions a backup, and the internal-sounding package",
          rc == 0 and "$3,997" in o3 and "$4,500" in o3 and "https://x" not in o3, (out, o3))
    att = cwd / "close-att.md"
    att.write_text("Close mode: checkout\n\n## For attendees\n\n- The Program: $997\n\n## Notes\n\n- Backup: https://x\n")
    run([PY, PLAN, "offer-summary", "--close", att, "--out", cwd / "o4.md"], cwd)
    o4 = (cwd / "o4.md").read_text()
    check("offer-summary uses a \"## For attendees\" section when close.md has one", "$997" in o4 and "Close mode" not in o4 and "Notes" not in o4, o4)
    pend = cwd / "close-pending.md"
    pend.write_text((FX / "close.md").read_text().replace("signed off 2026-11-20", "PENDING"))
    rc, out = run([PY, PLAN, "offer-summary", "--close", pend, "--out", cwd / "o2.md"], cwd)
    check("offer-summary refuses while close.md has a PENDING element", rc == 1 and not (cwd / "o2.md").exists(), out)


# ---------------------------------------------------------------- slides

def slide_tests(tmp):
    cwd = tmp / "slides"
    cwd.mkdir()
    rc, out = run([PY, SLIDES, "build", "--spec", FX / "webinar.json", "--out", cwd / "deck.pptx"], cwd)
    r = pj(out)
    n_expected = 1 + sum(max(1, len(s.get("slides") or [])) for s in FIXTURE["segments"] if s["kind"] != "lobby")
    check("build: one slide per planned slide plus the title slide", rc == 0 and r.get("slides") == n_expected, (r, n_expected))
    check("build: type at 32pt or more, contrast above 7:1, no problems", r.get("smallest_pt", 0) >= 32 and r.get("lowest_contrast", 0) >= 7
          and r.get("must_problems") == 0 and r.get("should_problems") == 0, r)
    z = zipfile.ZipFile(cwd / "deck.pptx")
    names = set(z.namelist())
    ct = z.read("[Content_Types].xml").decode()
    parts = [n for n in names if n.endswith(".xml") and not n.startswith("[") and "_rels" not in n]
    check("package: every part has a content type", all(f"/{n}" in ct or n.startswith("docProps/") and f"/{n}" in ct for n in parts),
          [n for n in parts if f"/{n}" not in ct])
    missing = []
    for rel in (n for n in names if n.endswith(".rels")):
        base = rel.replace("_rels/", "").rsplit(".rels", 1)[0]
        folder = base.rsplit("/", 1)[0] if "/" in base else ""
        for tgt in re.findall(r'Target="([^"]+)"', z.read(rel).decode()):
            p = "/".join(x for x in (folder + "/" + tgt).split("/") if x)
            parts_ = []
            for seg_ in p.split("/"):
                if seg_ == "..":
                    parts_.pop()
                else:
                    parts_.append(seg_)
            if "/".join(parts_) not in names:
                missing.append((rel, tgt))
    check("package: every relationship target exists", not missing, missing[:3])
    check("package: one notes slide per slide", len([n for n in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)]) == n_expected)
    n5 = z.read("ppt/notesSlides/notesSlide5.xml").decode()
    check("speaker notes land in the slide's notes (prompts, the chat ask)", "Most people think more clients" in n5 and "Ask:" in n5, n5[-400:])
    bad_pos = []
    for n in names:
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", n):
            for x, y, w, h in re.findall(r'<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', z.read(n).decode()):
                x, y, w, h = map(int, (x, y, w, h))
                if w and x + w > 12192000 * 2 / 3 and y + h > 6858000 / 2:
                    bad_pos.append(n)
    check("the lower right of every slide stays clear for the presenter's video", not bad_pos, bad_pos[:3])
    rc, out = run([PY, SLIDES, "inspect", cwd / "deck.pptx"], cwd)
    check("inspect: the built deck passes (exit 0)", rc == 0 and "0 must" in out, out)
    rc, out = run([PY, SLIDES, "build", "--spec", FX / "webinar.json", "--out", cwd / "d.pptx", "--accent", "FFDD00"], cwd)
    check("build refuses an accent colour under 4.5:1 and says why", rc == 2 and "4.5:1" in out and not (cwd / "d.pptx").exists(), out)
    rc, out = run([PY, SLIDES, "build", "--spec", FX / "webinar.json", "--out", cwd / "dark.pptx", "--theme", "dark", "--accent", "7CC4FF"], cwd)
    check("dark theme with a light accent passes", rc == 0 and pj(out).get("must_problems") == 0, out)
    rc, out = run([PY, SLIDES, "build", "--spec", FX / "webinar.json", "--out", cwd / "s.pptx", "--body-pt", "24"], cwd)
    check("build refuses body type under 28pt", rc == 2, out)
    rec = copy.deepcopy(FIXTURE)
    rec["recorded"] = True
    (cwd / "rec.json").write_text(json.dumps(rec))
    run([PY, SLIDES, "build", "--spec", cwd / "rec.json", "--out", cwd / "rec.pptx"], cwd)
    check("a recorded version says \"Recorded\" on the first slide",
          "Recorded" in zipfile.ZipFile(cwd / "rec.pptx").read("ppt/slides/slide1.xml").decode())
    sys.path.insert(0, str(S))
    import slide_builder as sb
    shapes = [sb.textbox(2, "Title", 0, 0, 5000000, 900000, [("Small and faint", 18, "BBBBBB", True, False)]),
              sb.textbox(3, "Body", 0, 1000000, 5000000, 3000000,
                         [(" ".join(["word"] * 40), 30, "333333", False, False)])]
    sb.write_pptx(cwd / "poor.pptx", [(shapes, "FFFFFF", "n")], "Arial", "Poor")
    rep = sb.inspect(cwd / "poor.pptx")
    probs = [p["what"] for p in rep["slides"][0]["problems"]]
    check("inspect flags type under 24pt, contrast under 4.5:1 and more than 25 words",
          rep["must"] == 2 and any("18pt" in p for p in probs) and any("contrast" in p for p in probs) and any("words" in p for p in probs), probs)
    rc, _ = run([PY, SLIDES, "inspect", cwd / "poor.pptx"], cwd)
    check("inspect exits 1 on a must-level problem", rc == 1)
    raw = sb.slide_xml([sb.textbox(2, "Body", 0, 0, 100, 100, [("x", 30, "000000", False, False)]).replace(' sz="3000"', "")
                        .replace('<a:solidFill><a:srgbClr val="000000"/></a:solidFill>', "")], "FFFFFF")
    sb.write_pptx(cwd / "u0.pptx", [([], "FFFFFF", "")], "Arial", "U")
    with zipfile.ZipFile(cwd / "u0.pptx") as zi, zipfile.ZipFile(cwd / "unset.pptx", "w") as zo:
        for n in zi.namelist():
            zo.writestr(n, raw if n == "ppt/slides/slide1.xml" else zi.read(n))
    rep = sb.inspect(cwd / "unset.pptx")
    check("inspect lists text whose size or colour is inherited as \"check by eye\"",
          any(p["level"] == "note" for p in rep["slides"][0]["problems"]))
    (cwd / "nope.pptx").write_text("not a zip")
    check("inspect: an unreadable file exits 2", run([PY, SLIDES, "inspect", cwd / "nope.pptx"], cwd)[0] == 2)
    check("contrast(): black on white is 21:1, mid grey on white about 4.5:1",
          sb.contrast("000000", "FFFFFF") == 21.0 and 4.4 < sb.contrast("767676", "FFFFFF") < 4.6)


# ---------------------------------------------------------------- the check

def check_tests(tmp):
    cwd = tmp / "check"
    cwd.mkdir()
    for f in ("close.md", "proof-bank.md", "business-file.md", "registration-page.md"):
        shutil.copy(FX / f, cwd / f)
    run([PY, SLIDES, "build", "--spec", FX / "webinar.json", "--out", cwd / "deck.pptx"], cwd)
    base = ["--close", "close.md", "--proof", "proof-bank.md", "--business-file", "business-file.md"]
    rc, out = run([PY, CHECK, "check", "--spec", FX / "webinar.json", "--deck", "deck.pptx", "--page", "registration-page.md",
                   "--out", "check.md"] + base, cwd)
    r = pj(out)
    check("the finished sample webinar says GO (exit 0)", rc == 0 and r.get("result") == "GO", [i for i in r.get("items", []) if not i["ok"]])
    check("check.md is written with every item", (cwd / "check.md").exists() and "| `offer_matches_close` | critical | PASS" in (cwd / "check.md").read_text())
    ids = {i["id"] for i in r.get("items", [])}
    hr = (R / "honesty-rules.md").read_text()
    crit = set(re.findall(r"`(\w+)`", hr.split("Critical (HOLD until each passes):")[1].split("Advisory")[0]))
    adv = set(re.findall(r"`(\w+)`", hr.split("Advisory (worth fixing, not a HOLD):")[1].split("\n\n")[0]))
    check("honesty-rules.md lists exactly the checks the script runs", ids == crit | adv, (ids ^ (crit | adv)))

    def variant(name, mutate, close=None, extra=(), expect_id=None, expect_ok=False, level="critical"):
        w = copy.deepcopy(FIXTURE)
        mutate(w)
        p = cwd / f"{name}.json"
        p.write_text(json.dumps(w))
        args = list(base)
        if close is not None:
            (cwd / f"{name}-close.md").write_text(close)
            args[1] = f"{name}-close.md"
        rc, out = run([PY, CHECK, "check", "--spec", p] + args + list(extra), cwd)
        res = pj(out)
        it = next((i for i in res.get("items", []) if i["id"] == expect_id), None)
        good = it is not None and it["ok"] == expect_ok and it["level"] == level
        if not expect_ok and level == "critical":
            good = good and rc == 1 and res.get("result") == "HOLD"
        check(f"check: {name} → {expect_id} {'passes' if expect_ok else 'fails'}", good, (rc, it))

    def say(sid, line):
        return lambda w: seg(w, sid)["say"].append(line)

    cl = (FX / "close.md").read_text()
    variant("a placeholder left", lambda w: seg(w, "teach3").update(notes="[write: the example]"), expect_id="placeholders_filled")
    variant("blocks over the length", lambda w: seg(w, "story").update(min=12), expect_id="length_fits")
    variant("no hard stop at the end", lambda w: w["segments"].pop(), expect_id="length_fits")
    variant("the agenda never mentions the offer",
            lambda w: seg(w, "promise").update(say=["Three things today"], title="The promise and the agenda"), expect_id="offer_disclosed")
    variant("two objections on the agenda", lambda w: w.update(not_covering=w["not_covering"][:2]), expect_id="objections_named")
    variant("two beliefs", lambda w: w["beliefs"].pop(), expect_id="three_beliefs")
    variant("a teaching block with no loop answer", lambda w: seg(w, "teach2")["loop"].update(answer=""), expect_id="loops_closed")
    variant("a loop deferred to the program", say("teach1", "I cover that inside the program"), expect_id="loops_closed")
    variant("a price not in close.md", say("offer", "Or the VIP door at $2,497"), expect_id="offer_matches_close")
    variant("a price only on a slide", lambda w: seg(w, "offer")["slides"][0]["lines"].append("Was $3,000"), expect_id="offer_matches_close")
    variant("close.md still PENDING", lambda w: None, close=cl.replace("signed off 2026-11-20", "PENDING"), expect_id="offer_matches_close")
    variant("a k-suffixed figure matches when close.md says it", say("offer", "That's a $2k decision"),
            close=cl + "\n- $2,000 is the price of the old workshop\n", expect_id="offer_matches_close", expect_ok=True)
    w_nc = copy.deepcopy(FIXTURE)
    (cwd / "nc.json").write_text(json.dumps(w_nc))
    rc, out = run([PY, CHECK, "check", "--spec", cwd / "nc.json", "--proof", "proof-bank.md", "--business-file", "business-file.md"], cwd)
    check("check without --close holds on offer_matches_close", rc == 1 and "offer_matches_close" in pj(out).get("critical_open", []))
    variant("a deadline in the talk but none in close.md", lambda w: None,
            close=re.sub(r"- \*\*Deadline:\*\*.*\n", "- Deadline: none; follow-up ends January 20\n", cl), expect_id="deadline_real")
    variant("an unconfirmed (U) story", lambda w: seg(w, "teach3").update(proof=[{"id": "P-03", "class": "U"}]), expect_id="proof_classified")
    variant("a paid-program story not introduced as one", lambda w: seg(w, "teach2")["proof"][0].pop("label"), expect_id="proof_classified")
    variant("a money story without the typical result", lambda w: seg(w, "teach1")["proof"][0].pop("typical"), expect_id="proof_classified")
    variant("a story not in the proof bank", lambda w: seg(w, "teach3").update(proof=[{"id": "P-09", "class": "A"}]), expect_id="proof_classified")
    variant("a story whose class differs from the bank", lambda w: seg(w, "teach1")["proof"][0].update(**{"class": "A"}),
            expect_id="proof_classified")
    variant("a story whose scope leaves out events", lambda w: seg(w, "teach3").update(proof=[{"id": "P-04", "class": "B", "typical": "x"}]),
            expect_id="proof_classified")
    variant("a guest block with no proof ID",
            lambda w: w["segments"].insert(4, {"id": "guest", "kind": "guest", "title": "Guest", "min": 1, "say": ["Meet Jo"]}) or
            seg(w, "story").update(min=4), expect_id="proof_classified")
    variant("an earnings figure in teaching without the typical result",
            say("teach3", "One client made $40,000 more last year"), close=cl + "\n- $40,000 (not a price)\n", expect_id="earnings_typical")
    variant("a growth percentage without the typical result", say("story", "My income doubled, up 100% in a year"), expect_id="earnings_typical")
    variant("a retired line, even with other punctuation", say("teach1", "Stop leaving money on the table!"), expect_id="retired_lines")
    variant("a retired line without quotes", say("teach2", "You could double your rates in thirty days"), expect_id="retired_lines")
    variant("a never-say claim", say("teach3", "This is guaranteed income"), expect_id="retired_lines")
    variant("a never-say claim from a comma-separated list", say("teach3", "and get six figures in six weeks"),
            expect_id="retired_lines")
    variant("a retired line with a contraction", say("teach1", "Stop leavin' money... no: stop leaving money on the table"),
            expect_id="retired_lines")
    rc, out = run([PY, CHECK, "check", "--spec", FX / "webinar.json", "--close", "close.md", "--proof", "proof-bank.md"], cwd)
    check("check without --business-file holds on retired_lines", rc == 1 and "retired_lines" in pj(out).get("critical_open", []))
    for code, line in (("fake_count", "There are 400 people here right now"), ("fake_count", "The room is full today"),
                       ("seeded_chat", "Sam will seed the chat with a few questions"), ("fake_poll", "98% of you said yes"),
                       ("fake_timer", "This page is coming down tonight"), ("fake_timer", "I'll extend the timer for you"),
                       ("replay_threat", "If you leave now, you'll miss it; we'll edit that out"),
                       ("hidden_text", "Use embedded commands in grey"), ("fake_scarcity", "Only 3 spots left")):
        variant(f"refused: {line}", say("transition", line), expect_id="refused_tactics")
    capped = cl + "\n- **Places:** 20 places, because Dana coaches each one\n"
    variant("the cap said as the cap passes", say("offer", "I cap it at 20 places so I can coach each one"),
            close=capped, expect_id="refused_tactics", expect_ok=True)
    variant("the cap said as the cap matches close.md", say("offer", "I cap it at 20 places"), close=capped,
            expect_id="offer_matches_close", expect_ok=True)
    variant("\"only 3 left\" is refused even with a real cap (the moderator gives the live count)",
            say("offer", "Only 3 spots left of the 20"), close=capped, expect_id="refused_tactics")
    variant("a place count not in close.md", say("offer", "There are 15 places"), close=capped, expect_id="offer_matches_close")
    # review findings: forms of money, dates, payments, deadlines
    for line in ("It's 1,497 dollars", "That's 2497 USD", "Or £1,497 in the UK", "About fifteen hundred dollars"):
        variant(f"a price in another form: {line}", say("offer", line), expect_id="offer_matches_close")
    variant("a price from close.md said in a teaching block", say("teach2", "It's $1,997, by the way"), expect_id="offer_matches_close")
    variant("a date not in close.md", say("offer", "Enrolment closes January 31"), expect_id="offer_matches_close")
    variant("a payment count not in close.md", say("offer", "Or 6 payments"), expect_id="offer_matches_close")
    variant("the member's own figure in the story is not a price", say("story", "I charged $40 an hour back then"),
            expect_id="offer_matches_close", expect_ok=True)
    variant("an earnings promise in the promise line", lambda w: w.update(promise="Earn 30% more revenue this year"),
            expect_id="earnings_typical")
    nodl = re.sub(r"- \*\*Deadline:\*\*.*\n", "- **Deadline:** none; follow-up ends January 20\n", cl)
    variant("no deadline: \"the replay is available until December 10\" is honest",
            lambda w: (seg(w, "offer").update(say=[x for x in seg(w, "offer")["say"] if "closes" not in x]),
                       w["qa_bank"][3].update(answer="Good. Show him the one-pager and talk it over."),
                       say("close", "The replay is available until December 10")(w)),
            close=nodl, expect_id="deadline_real", expect_ok=True)
    variant("a close.md saying \"Enrolment closes …\" counts as a deadline", lambda w: None,
            close=cl.replace("- **Deadline:** enrolment closes", "- Enrolment closes"), expect_id="deadline_real", expect_ok=True)
    variant("\"no deadline extensions\" elsewhere is not \"no deadline\"", lambda w: None,
            close=cl + "\n- Note: no deadline extensions for anyone\n", expect_id="deadline_real", expect_ok=True)
    variant("\"doors close this Sunday\" when close.md has a date", say("offer", "Doors close this Sunday"), expect_id="deadline_real")
    variant("PENDING in lower case still holds", lambda w: None, close=cl.replace("signed off 2026-11-20", "pending sign-off"),
            expect_id="offer_matches_close")
    variant("PENDING inside an HTML comment does not hold", lambda w: None, close=cl + "\n<!-- PENDING note to self -->\n",
            expect_id="offer_matches_close", expect_ok=True)
    variant("\"300 people\" about past clients is not a head count", say("story", "I've worked with 300 people on exactly this"),
            expect_id="refused_tactics", expect_ok=True)
    variant("a real bonus for staying is not a replay threat", say("qa", "If you leave early, you'll miss the bonus checklist"),
            expect_id="refused_tactics", expect_ok=True)
    variant("an illustration (X) is not proof", lambda w: seg(w, "teach3").update(proof=[{"id": "P-01", "class": "X"}]),
            expect_id="proof_classified")
    variant("the host's own figures (H) need the typical result",
            lambda w: seg(w, "teach3").update(proof=[{"id": "P-05", "class": "H"}]), expect_id="proof_classified")
    variant("a recording that says it is live",
            lambda w: (w.update(recorded=True), seg(w, "agreement")["say"].append("This is a recording of a session I ran live"),
                       say("teach1", "We're live right now")(w)), expect_id="refused_tactics")
    variant("a recorded version that never says so",
            lambda w: w.update(recorded=True, title="How to Price"), expect_id="recording_notice")
    variant("a recorded version that says so", lambda w: (w.update(recorded=True),
                                                           seg(w, "agreement")["say"].insert(0, "This is a recording of a session I ran live")),
            expect_id="recording_notice", expect_ok=True)
    variant("no recording notice in the first minutes", lambda w: seg(w, "agreement").update(notes="Captions are on"),
            expect_id="recording_notice")
    (cwd / "page-bad.md").write_text("Join my free class on pricing. Thursday, December 3.")
    variant("a registration page that never mentions the offer or the recording", lambda w: None,
            extra=("--page", "page-bad.md"), expect_id="page_discloses")
    variant("no written answer for the spouse", lambda w: w["qa_bank"].pop(), expect_id="qa_bank_covers")
    variant("a placeholder answer does not count", lambda w: w["qa_bank"][0].update(answer="[write: answer]"), expect_id="qa_bank_covers")
    variant("the presenter as moderator", lambda w: w["roles"].update(moderator="Dana Ruiz"), expect_id="moderator_named")
    variant("no moderator named", lambda w: w["roles"].update(moderator="[moderator]"), expect_id="moderator_named")
    variant("an opening with no chat prompt", lambda w: seg(w, "agreement").update(chat_prompt=""), expect_id="chat_prompts", level="advisory")
    variant("the offer asked for once", lambda w: seg(w, "offer").update(asks=1), expect_id="offer_asks", level="advisory")
    variant("a long story", lambda w: (seg(w, "story").update(min=13), seg(w, "teach1").update(min=3), seg(w, "teach2").update(min=3)),
            expect_id="story_length", level="advisory")
    variant("\"it's not your fault\"", say("story", "And it's not your fault"), expect_id="not_your_fault", level="advisory")
    poor = cwd / "poor.pptx"
    sys.path.insert(0, str(S))
    import slide_builder as sb
    sb.write_pptx(poor, [([sb.textbox(2, "Body", 0, 0, 5000000, 900000, [("Tiny", 16, "CCCCCC", False, False)])], "FFFFFF", "")], "Arial", "P")
    rc, out = run([PY, CHECK, "check", "--spec", FX / "webinar.json", "--deck", poor] + base, cwd)
    open_ = pj(out).get("critical_open", [])
    check("a deck with 16pt pale type holds on deck_font_min and deck_contrast_min",
          rc == 1 and "deck_font_min" in open_ and "deck_contrast_min" in open_, open_)
    (cwd / "broken.json").write_text("{")
    check("check: an unreadable spec exits 2", run([PY, CHECK, "check", "--spec", cwd / "broken.json"], cwd)[0] == 2)


# ---------------------------------------------------------------- review

def review_tests(tmp):
    cwd = tmp / "review"
    cwd.mkdir()
    rc, out = run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", FX / "rehearsal.vtt", "--spec", FX / "webinar.json",
                   "--out", cwd / "rehearsal-1.md"], cwd)
    r = pj(out)
    v = {x["id"]: x for x in r.get("lines", [])}
    check("rehearsal: the late offer is a FIX (minute 47 against 40)", v.get("time_to_offer", {}).get("verdict") == "FIX"
          and "minute 47" in v["time_to_offer"]["detail"], v.get("time_to_offer"))
    check("rehearsal: running over is a FIX", v.get("total_length", {}).get("verdict") == "FIX")
    check("rehearsal: a deferred answer is a FIX", v.get("loops_open", {}).get("verdict") == "FIX")
    check("rehearsal: a dollar result said without the typical result is a FIX", v.get("unlabelled_proof", {}).get("verdict") == "FIX",
          v.get("unlabelled_proof"))
    check("rehearsal: long blocks are watched", v.get("block_timings", {}).get("verdict") == "WATCH" and "teach1" in v["block_timings"]["detail"])
    check("rehearsal: the offer asked for three times passes", v.get("offer_said_three", {}).get("verdict") == "PASS")
    check("rehearsal: nothing refused was said", v.get("refused_words", {}).get("verdict") == "PASS")
    check("rehearsal: three fixes, the late offer first", [f["id"] for f in r.get("fixes", [])][:1] == ["time_to_offer"] and len(r["fixes"]) == 3)
    md = (cwd / "rehearsal-1.md").read_text()
    check("rehearsal scorecard written with the three fixes", "## The three fixes" in md and "| `time_to_offer` | FIX |" in md)
    vt = (FX / "rehearsal.vtt").read_text().replace("We'll get to that in the program, it's all inside the program really.",
                                                     "Ninety-eight percent of you said yes. Only 3 spots left.")
    (cwd / "bad.vtt").write_text(vt.replace("Only 3 spots left.", "98% of you said yes, and only 3 spots left."))
    r2 = pj(run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", cwd / "bad.vtt", "--spec", FX / "webinar.json",
                 "--out", cwd / "r2.md"], cwd)[1])
    rw = next(x for x in r2["lines"] if x["id"] == "refused_words")
    check("rehearsal: refused words said aloud are a FIX", rw["verdict"] == "FIX" and "fake_poll" in rw["detail"] and "fake_scarcity" in rw["detail"], rw)
    (cwd / "plain.txt").write_text("Hello everyone. We'll get to that in the program. Type yes in the chat.\nThank you.")
    rc, out = run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", cwd / "plain.txt", "--out", cwd / "r3.md"], cwd)
    r3 = pj(out)
    check("a plain transcript (no timings) is reviewed without the timing lines", rc == 0 and r3.get("timed") is False
          and "time_to_offer" not in {x["id"] for x in r3["lines"]} and any(x["id"] == "loops_open" and x["verdict"] == "FIX" for x in r3["lines"]), out)
    sp = cwd / "webinar.json"
    shutil.copy(FX / "webinar.json", sp)
    rc, out = run([PY, REVIEW, "review", "--kind", "run", "--transcript", FX / "rehearsal.vtt", "--spec", sp, "--chat", FX / "chat.txt",
                   "--attendance", FX / "attendance.csv", "--registered", "12", "--buyers", "1", "--log", sp, "--out", cwd / "run-1.md"], cwd)
    r = pj(out)
    run_ = r.get("run", {})
    check("run: four unique attendees (one rejoined), three still there at the offer",
          run_.get("attended") == 4 and run_.get("at_offer") == 3 and run_.get("peak") == 4, run_)
    check("run: show-up and buy rates", r.get("show_up") == round(4 / 12, 3) and r.get("buy_rate") == 0.25, r)
    md = (cwd / "run-1.md").read_text()
    check("run scorecard: who stayed by block, and the chat by block",
          "## Who stayed" in md and "- teach2" in md and "5 chat messages" in md, md[:500])
    check("run scorecard: questions not answered aloud are listed", "3 questions asked; 3 not answered aloud" in md)
    check("run scorecard: no attendee names or emails", not re.search(r"Pat|Kim Ode|Lou Grant|Ana Ruiz|@example\.com", md), md)
    check("run --log appends the run to webinar.json", json.loads(sp.read_text())["runs"][-1]["attended"] == 4)
    rc, out = run([PY, REVIEW, "review", "--kind", "run", "--transcript", FX / "rehearsal.vtt", "--spec", FX / "webinar.json",
                   "--attendance", FX / "attendance-webinar.csv", "--out", cwd / "run-w.md"], cwd)
    check("Zoom Webinar attendee report: only the Attendee section, rejoins merged, no-shows left out (2 people)",
          rc == 0 and pj(out).get("run", {}).get("attended") == 2, out[-400:])
    rc, out = run([PY, REVIEW, "review", "--kind", "run", "--transcript", FX / "rehearsal.vtt", "--spec", FX / "webinar.json",
                   "--attendance", FX / "attendance-guests.csv", "--out", cwd / "run-g.md"], cwd)
    check("Meetings participants report: guests with blank emails keyed by name, the host left out (2 people)",
          rc == 0 and pj(out).get("run", {}).get("attended") == 2, out[-400:])
    (cwd / "chat2.txt").write_text("14:15:02 From Jo Bell to Everyone:\n\tJo here, can you email me at jo@example.com or call 555 123 4567?\n")
    rc, out = run([PY, REVIEW, "review", "--kind", "run", "--transcript", FX / "rehearsal.vtt", "--spec", FX / "webinar.json",
                   "--chat", cwd / "chat2.txt", "--out", cwd / "run-c.md"], cwd)
    c2 = (cwd / "run-c.md").read_text()
    check("unanswered chat questions are quoted without the asker's name, email or number",
          "Jo" not in c2 and "jo@example.com" not in c2 and "555" not in c2 and "[email]" in c2, c2[-300:])
    short = (FX / "rehearsal.vtt").read_text()
    short = re.sub(r"\b00:(\d\d:\d\d\.\d{3})", r"\1", short)
    (cwd / "short.vtt").write_text(short)
    r5 = pj(run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", cwd / "short.vtt", "--spec", FX / "webinar.json",
                 "--out", cwd / "r5.md"], cwd)[1])
    check("short VTT timestamps (mm:ss.mmm, from Otter or Descript) are read as timed",
          r5.get("timed") is True and any(x["id"] == "time_to_offer" for x in r5["lines"]), r5.get("timed"))
    (cwd / "untimed.vtt").write_text("WEBVTT\n\nHello everyone, welcome.\n")
    r6 = pj(run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", cwd / "untimed.vtt", "--out", cwd / "r6.md"], cwd)[1])
    check("a .vtt with no readable timings says so", "warning" in r6, r6)
    w9 = copy.deepcopy(FIXTURE)
    seg(w9, "promise")["say"].insert(0, "At the end I'll tell you about The Pricing Program")
    (cwd / "w9.json").write_text(json.dumps(w9))
    r7 = pj(run([PY, REVIEW, "review", "--kind", "rehearsal", "--transcript", FX / "rehearsal.vtt", "--spec", cwd / "w9.json",
                 "--out", cwd / "r7.md"], cwd)[1])
    check("naming the offer on the agenda does not count as the offer starting (the dry-run bug)",
          r7.get("offer_at") == 47.0 and next(x for x in r7["lines"] if x["id"] == "loops_open")["verdict"] == "FIX", r7.get("offer_at"))
    rc, out = run([PY, REVIEW, "evergreen-ready", "--spec", sp], cwd)
    check("evergreen-ready: READY after a live run that converted", rc == 0 and pj(out).get("result") == "READY", out)
    rc, out = run([PY, REVIEW, "evergreen-ready", "--spec", FX / "webinar.json"], cwd)
    check("evergreen-ready: NOT YET with no live run logged", rc == 1 and pj(out).get("result") == "NOT YET")
    w = json.loads(sp.read_text())
    w["runs"][-1]["buyers"] = 0
    sp.write_text(json.dumps(w))
    check("evergreen-ready: NOT YET when no one bought", run([PY, REVIEW, "evergreen-ready", "--spec", sp], cwd)[0] == 1)
    w["close"] = "call"
    w["runs"][-1]["calls_booked"] = 1
    sp.write_text(json.dumps(w))
    check("evergreen-ready (call close): READY at 25 calls per 100 attendees", run([PY, REVIEW, "evergreen-ready", "--spec", sp], cwd)[0] == 0)

    def diag(*a):
        return pj(run([PY, REVIEW, "diagnose"] + [str(x) for x in a], cwd)[1])
    check("diagnose: show-up first when under a third came live",
          diag("--registered", 100, "--attended", 25, "--at-offer", 20, "--buyers", 0)["first_leak"] == "show_up")
    check("diagnose: stay-to-offer next", diag("--registered", 100, "--attended", 40, "--at-offer", 15, "--buyers", 2)["first_leak"] == "stay_to_offer")
    check("diagnose: then the close", diag("--registered", 100, "--attended", 40, "--at-offer", 30, "--buyers", 0)["first_leak"] == "close")
    check("diagnose: no leak above the lines", diag("--registered", 100, "--attended", 40, "--at-offer", 30, "--buyers", 2)["first_leak"] is None)
    d = diag("--registered", 100, "--attended", 40, "--at-offer", 30, "--calls-booked", 1, "--close", "call")
    check("diagnose (call close): calls per 100 attendees", d["first_leak"] == "close" and d["rates"]["calls_per_100_attendees"] == 2.5, d)
    check("diagnose (price $2,500): judged on calls", "calls_per_100_attendees" in diag("--registered", 100, "--attended", 40,
                                                                                         "--at-offer", 30, "--calls-booked", 3, "--price", 2500)["rates"])
    check("diagnose says the lines are starting points, not promises", "not promises" in diag("--registered", 10, "--attended", 5, "--at-offer", 4)["note"])


# ---------------------------------------------------------------- consistency and privacy

def consistency_tests():
    sk = (SK / "SKILL.md").read_text()
    m = re.match(r"---\nname: (\S+)\ndescription: \|\n(.*?)\n---\n", sk, re.S)
    check("SKILL.md front matter: name matches the folder", m and m.group(1) == SK.name)
    desc = m.group(2) if m else ""
    for phrase in ("build my webinar", "rehearse my webinar", "how did my webinar go", "why didn't my webinar sell",
                   "make my webinar evergreen", "write my webinar title and registration page"):
        check(f"description triggers on \"{phrase}\"", phrase in desc.lower())
    refs = set(re.findall(r"`references/([\w.-]+\.md)`", sk))
    check("every reference SKILL.md names exists", refs and all((R / r).exists() for r in refs), [r for r in refs if not (R / r).exists()])
    on_disk = {p.name for p in R.glob("*.md")} - {"business-file-template.md"}  # named by the protocol
    check("every reference on disk is named in SKILL.md", on_disk <= refs, on_disk - refs)
    scripts = set(re.findall(r"`?(\w+\.py)\b", sk)) - {"launch_tracker.py", "run_sheet.py"}
    check("every script SKILL.md names exists", scripts and all((S / x).exists() for x in scripts), scripts)
    for f in ("kern-framework.md", "halbert-writing-system.md"):
        check(f"{f} is byte-identical to the Copy Engine's", (R / f).read_bytes() == (ROOT / "skills/buildroom-copy-engine/references" / f).read_bytes())
    check("business-file-protocol.md matches the shared copy", (R / "business-file-protocol.md").read_bytes() == (ROOT / "shared/business-file-protocol.md").read_bytes())
    check("business-file-template.md matches the template", (R / "business-file-template.md").read_bytes() == (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_bytes())
    folder = (R / "webinar-folder.md").read_text()
    kinds = re.search(r"Segment `kind`: (.*?)\. Lobby", folder).group(1)
    sys.path.insert(0, str(S))
    import webinar_plan as wp
    check("webinar-folder.md lists the same segment kinds as webinar_plan.py", set(re.findall(r"`(\w+)`", kinds)) == set(wp.KINDS))
    check("webinar-folder.md lists the same formats as webinar_plan.py",
          set(re.findall(r"`(\w+)`", folder.split("- `format`:")[1].split("\n")[0])) == set(wp.FORMATS))
    check("talk-structures.md minute map matches the live60 outline (offer 40–50)", "| 40–50 | The offer (`offer`)" in (R / "talk-structures.md").read_text())
    # the skill never writes a price
    check("SKILL.md says prices come only from close.md", "never invents or changes a price" in sk)
    # privacy: no partner material, client or attendee names, founder figures, credentials
    banned = re.compile(r"brian ?tracy|canfield|\bhei\b|forever.free|jesse|karen martel|nathalie|dahl|briantracyai|"
                        r"2,181|105 people|\b308\b|lanny@|@aimomentumlabs|/home/user/brain|zoom-transcripts|password", re.I)
    hits = [f"{p.relative_to(ROOT)}: {banned.search(p.read_text()).group(0)}" for p in SK.rglob("*")
            if p.is_file() and p.suffix in (".md", ".py") and p.name not in ("kern-framework.md", "halbert-writing-system.md",
                                                                             "business-file-template.md", "business-file-protocol.md")
            and banned.search(p.read_text())]
    check("no partner names, client or attendee names, founder figures, vault paths or credentials in the skill", not hits, hits)
    notes = ROOT.parent / "research_notes/Webinar Builder"
    nh = [p.name for p in notes.glob("*.md") if banned.search(p.read_text())]
    check("the research notes carry no names, vault paths or founder figures", not nh, nh)
    for p in S.glob("*.py"):
        src = p.read_text()
        imports = set(re.findall(r"^\s*(?:import|from) ([\w.]+)", src, re.M))
        third = imports - {"sys", "argparse", "json", "re", "zipfile", "csv", "copy", "pathlib", "datetime", "xml.sax.saxutils",
                           "slide_builder", "webinar_check"}
        check(f"{p.name}: standard library only", not third, third)
        check(f"{p.name}: no network calls", not re.search(r"urllib|http\.client|socket|requests", src))


def main():
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="webinar-tests-"))
    try:
        plan_tests(tmp)
        slide_tests(tmp)
        check_tests(tmp)
        review_tests(tmp)
        consistency_tests()
    finally:
        for p in S.glob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)
        if keep:
            print(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    n = sum(ok for _, ok in RESULTS)
    print(f"\n{n}/{len(RESULTS)} checks passed")
    sys.exit(0 if n == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
