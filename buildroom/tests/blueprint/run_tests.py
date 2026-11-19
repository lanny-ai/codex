#!/usr/bin/env python3
"""Company Blueprint tests: the aim gate, functions, position contracts, measures, the check, the hand-off
ranking, the five-step read, reviews, the rendered documents, and the wiring into Build Room OS.

Local only: synthetic files, no network.

Usage:  python3 buildroom/tests/blueprint/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SK = ROOT / "skills/buildroom-company-blueprint"
BP = SK / "scripts/blueprint.py"
PY = sys.executable
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:400]}" if detail and not ok else ""))


def run(args, cwd):
    p = subprocess.run([PY, str(BP)] + [str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except Exception:
        d = {"_raw": p.stdout + p.stderr}
    return p.returncode, d


FILE = """# Build Room Business File

**File version:** 1.11

## 1. Business Snapshot

**Status:** complete · **Updated:** 2026-10-01 · **By:** Ideal Client Avatar

- **Business:** Ledger Lane, pricing help for bookkeeping firm owners in Ohio
- **Goals:** a calm practice that runs three days a week by next year

## 3. Signature Offer

**Status:** complete · **Updated:** 2026-10-02 · **By:** Signature Offer

- **Offer:** the Value Pricing Sprint, six weeks to move one service from hourly to a fixed price

## 9. Standard Operating Procedures

**Status:** in progress · **Updated:** 2026-10-05 · **By:** SOP Creator

- **SOPs written:** New enquiry reply; Client onboarding; Monthly invoicing run for every active client

## 17. Founder Compass

**Status:** complete · **Updated:** 2026-10-06 · **By:** Compass

- **What I want:** to work three days a week, keep the teaching, and stop doing sales calls and invoices myself

## 8. Session Log
"""
ACC = ["Every new enquiry gets a reply within one working day", "Every discovery call ends with a written next step",
       "Every proposal sent is followed up twice"]


def setup(work, name, aim=True):
    w = work / name
    w.mkdir()
    (w / "BUILDROOM_BUSINESS_FILE.md").write_text(FILE, encoding="utf-8")
    run(["init"], w)
    if aim:
        for k in ("primary_aim", "objective", "owner_role"):
            run(["aim", "--key", k, "--text", "Three days a week, keep the teaching, hand off sales and invoices"], w)
    return w


def fn(w, key, name, hours=None, only=None, doc=None, by="owner"):
    args = ["function", "add", "--key", key, "--name", name, "--covered-by", by]
    for flag, v in (("--hours", hours), ("--teachable", only), ("--documented", doc)):
        if v is not None:
            args += [flag, v]
    return run(args, w)


def position(w, title, function, reports="none", held="owner", mission=None, acc=None, may=("Book calls and send the standard proposal",),
             appr=("Any discount or change to the offer",), extra=()):
    args = ["position", "add", "--title", title, "--function", function, "--reports-to", reports, "--held-by", held,
            "--mission", mission or f"Make sure the {function} work produces the result the business promises its clients"]
    for a in (acc if acc is not None else ACC):
        args += ["--accountability", a]
    for m in may:
        args += ["--may", m]
    for m in appr:
        args += ["--needs-approval", m]
    return run(args + list(extra), w)


def kpi(w, pos="POS-02", name="Enquiry to client rate", extra=(), rate=True, formula="clients won divided by enquiries qualified"):
    args = ["kpi", "add", "--position", pos, "--name", name, "--purpose", "Shows whether calls turn into clients", "--kind", "lagging",
            "--formula", formula, "--source", "the CRM monthly report", "--period", "month"]
    if rate:
        args += ["--numerator", "clients who paid in the month", "--denominator", "enquiries marked qualified in the month"]
    return run(args + list(extra), w)


def full(work, name):
    w = setup(work, name)
    fn(w, "sales", "Sales", 8, 4, 4)            # teachable 4: someone trained could
    fn(w, "delivery", "Delivery", 20, 2, 4)     # teachable 2: close to owner-only
    fn(w, "finance", "Finance and admin", 3, 5, 1)
    position(w, "Owner", "delivery", appr=(), acc=["Every client engagement finishes on the agreed date",
                                                  "Every client gets a written summary at the end", "The quarterly plan is written each quarter"])
    position(w, "Sales Lead", "sales", reports="POS-01", extra=("--sop", "New enquiry reply", "--gets-from", "Qualified enquiries from Marketing",
                                                                "--gives-to", "A signed agreement to Delivery"))
    position(w, "Bookkeeper", "finance", reports="POS-01", acc=["Every invoice goes out within two working days of the work",
                                                                "Every bill is paid by its due date", "The books are ready for the accountant each month"])
    kpi(w, "POS-01", "Engagements finished on the agreed date", rate=False, formula="count of engagements finished on or before the agreed date")
    kpi(w, "POS-02", extra=("--baseline", "0.2", "--baseline-basis", "CRM, July to September", "--target", "0.3", "--target-basis", "member decision",
                            "--direction", "up", "--trigger-below", "0.15"))
    kpi(w, "POS-03", "Invoices sent within two days", rate=False, formula="count of invoices sent within two working days")
    return w


def aim_tests(work):
    w = setup(work, "aim", aim=False)
    code, d = run(["prefill"], w)
    drafted = {x["key"] for x in d.get("draft_from_file", [])}
    check("prefill: aim questions are drafted from filled sections", {"primary_aim", "objective", "owner_role"} <= drafted, d)
    check("prefill: what is already built is shown", len(d.get("already_built", {}).get("sops", [])) == 1, d.get("already_built"))
    check("prefill: hours, baselines and targets are never drafted", "never drafted" in d.get("rule", ""))
    blank = work / "blank"
    blank.mkdir()
    shutil.copy(ROOT / "templates/BUILDROOM_BUSINESS_FILE.md", blank / "BUILDROOM_BUSINESS_FILE.md")
    run(["init"], blank)
    code, d = run(["prefill"], blank)
    check("prefill: a blank template offers no drafts", d.get("draft_from_file") == [] and len(d.get("ask_the_member", [])) == 3, d)
    code, d = run(["aim", "--key", "primary_aim", "--text", "Work three days a week and keep the teaching", "--from", "§17"], w)
    check("aim: an answer drawn from a section is a draft", d.get("draft") is True, d)
    code, d = run(["aim", "--key", "nonsense", "--text", "x"], w)
    check("aim: an unknown key is refused", code == 1, d)
    for k in ("objective", "owner_role"):
        run(["aim", "--key", k, "--text", "the member said this"], w)
    code, d = run(["check"], w)
    check("check: an unconfirmed draft is a FIX", any("not confirmed" in x for x in d.get("fix", [])), d)
    code, d = run(["confirm", "--all", "--by", "claude"], w)
    check("confirm: only the member confirms", code == 1, d)
    code, d = run(["confirm", "--all", "--by", "member"], w)
    check("confirm: the member's confirmation clears the draft", d.get("confirmed") == ["primary_aim"] and not d.get("still_draft"), d)


def structure_tests(work):
    w = setup(work, "structure")
    code, d = fn(w, "sales", "Sales")
    check("function: an owner-covered function with no hours asks for the member's number", any("their number" in x for x in d.get("warnings", [])), d)
    code, d = fn(w, "sales", "Sales", 8, 2, 4)
    check("function: adding it again updates it", d.get("updated") is True and d.get("functions") == 1, d)
    code, d = fn(w, "delivery", "Delivery", 20, 9, 2)
    check("function: a score outside 1 to 5 is refused", code == 1, d)
    code, d = run(["function", "add", "--key", "x", "--name", "X", "--covered-by", "sam@example.com"], w)
    check("function: an email address is refused", code == 1 and "email" in d.get("error", ""), d)
    fn(w, "delivery", "Delivery", 20, 4, 2)
    code, d = position(w, "Owner", "nowhere")
    check("position: the function must be on file", code == 1, d)
    code, d = position(w, "Owner", "delivery", mission="Help with delivery")
    check("position: a vague mission is refused", code == 1 and "mission" in d.get("error", ""), d)
    code, d = position(w, "Owner", "delivery", acc=ACC[:2])
    check("position: fewer than three accountabilities is refused", code == 1 and "three to seven" in d.get("error", ""), d)
    code, d = position(w, "Owner", "delivery", acc=ACC * 3)
    check("position: more than seven accountabilities is refused", code == 1, d)
    code, d = position(w, "Owner", "delivery", acc=ACC[:2] + ["Help with follow up as needed"])
    check("position: a task or vague line is refused and named", code == 1 and "Help with follow up" in d.get("error", ""), d)
    code, d = position(w, "Owner", "delivery", may=())
    check("position: a seat needs something it may decide alone", code == 1, d)
    code, d = position(w, "Owner", "delivery", appr=())
    check("position: the top seat needs no approval line", d.get("id") == "POS-01", d)
    check("position: no linked procedure is warned", any("no SOP" in x for x in d.get("warnings", [])), d)
    code, d = position(w, "Second Top", "sales")
    check("position: a second top seat is refused", code == 1 and "reports-to" in d.get("error", ""), d)
    code, d = position(w, "Sales Lead", "sales", reports="POS-01", appr=())
    check("position: a seat below the top needs an approval line", code == 1, d)
    code, d = position(w, "Sales Lead", "sales", reports="POS-01", extra=("--sop", "New enquiry reply", "--sop", "Proposal follow up"))
    check("position: a procedure missing from §9 is named", d.get("id") == "POS-02" and any("Proposal follow up" in x and "New enquiry reply" not in x
                                                                                        for x in d.get("warnings", [])), d)
    code, d = position(w, "Sales Lead", "sales", reports="POS-01")
    check("position: a duplicate title is refused", code == 1, d)
    code, d = position(w, "Dash Seat", "sales", reports="POS-01", mission="Turn enquiries into clients — the ones who are a good fit for us")
    check("position: an em dash is refused", code == 1 and "dash" in d.get("error", ""), d)
    code, d = run(["position", "remove", "--id", "POS-01"], w)
    check("position: a seat others report to cannot be removed", code == 1, d)


def kpi_tests(work):
    w = setup(work, "kpi")
    fn(w, "sales", "Sales", 8, 2, 4)
    position(w, "Owner", "sales", appr=())
    code, d = kpi(w, "POS-09")
    check("kpi: the position must exist", code == 1, d)
    code, d = kpi(w, "POS-01", rate=False, formula="clients won / enquiries qualified")
    check("kpi: a rate needs both halves defined", code == 1 and "numerator" in d.get("error", ""), d)
    code, d = kpi(w, "POS-01", extra=("--baseline", "0.2"))
    check("kpi: a baseline needs where it was read from", code == 1 and "baseline-basis" in d.get("error", ""), d)
    code, d = kpi(w, "POS-01", extra=("--target", "0.3"))
    check("kpi: a target needs a basis", code == 1 and "target-basis" in d.get("error", ""), d)
    code, d = kpi(w, "POS-01", extra=("--target", "0.3", "--target-basis", "industry average", "--direction", "up"))
    check("kpi: an industry average is not a basis", code == 1, d)
    code, d = kpi(w, "POS-01", extra=("--target", "0.3", "--target-basis", "member decision"))
    check("kpi: a target needs a direction", code == 1 and "direction" in d.get("error", ""), d)
    code, d = kpi(w, "POS-01", extra=("--target", "nan", "--target-basis", "member decision", "--direction", "up"))
    check("kpi: nan is refused", code != 0, d)
    code, d = kpi(w, "POS-01")
    check("kpi: with no baseline it is recorded as not measured yet", d.get("id") == "KPI-01" and any("not measured yet" in x for x in d.get("warnings", [])), d)
    check("kpi: no trigger is warned", any("no trigger" in x for x in d.get("warnings", [])), d)
    code, d = kpi(w, "POS-01", "Emails sent", rate=False, formula="count of emails sent in the week")
    check("kpi: an activity count is warned", any("activity, not a result" in x for x in d.get("warnings", [])), d)
    code, d = kpi(w, "POS-01", "Screen time", rate=False, formula="hours of screen time logged by the app")
    check("kpi: a measure of a person being watched is refused", code == 1 and "watched" in d.get("error", ""), d)
    for i in range(3):
        kpi(w, "POS-01", f"Measure number {i}", rate=False, formula="count of things finished in the month")
    code, d = kpi(w, "POS-01", "A sixth", rate=False, formula="count of things finished in the month")
    check("kpi: a sixth measure on one position is refused", code == 1 and "five" in d.get("error", ""), d)
    code, d = run(["kpi", "remove", "--id", "KPI-02"], w)
    check("kpi: a measure can be removed", d.get("removed") == "KPI-02", d)
    data = json.loads((w / "blueprint/blueprint.json").read_text())
    check("kpi: no baseline or target was written that the member did not give",
          all(k["baseline"] is None and k["target"] is None for k in data["kpis"]))


def whole_tests(work):
    w = setup(work, "gaps")
    fn(w, "sales", "Sales", 8, 2, 4)
    fn(w, "delivery", "Delivery", 20, 4, 2)
    code, d = run(["check"], w)
    check("check: fewer than three functions is a FIX", any("fewer than three" in x for x in d.get("fix", [])), d)
    fn(w, "finance", "Finance and admin")
    position(w, "Owner", "delivery", appr=())
    code, d = run(["check"], w)
    fx = " | ".join(d.get("fix", []))
    check("check: a function nobody answers for is a FIX", "nobody is accountable for Sales" in fx and "Finance and admin" in fx and code == 1, d)
    check("check: a position with no measure is a FIX", "POS-01 Owner has no measure" in fx, d)
    check("check: it says what a script cannot tell", "cannot tell" in d.get("limits", ""))
    code, d = run(["handoff"], w)
    check("handoff: a function without the member's numbers is not ranked", d.get("not_ranked") == ["Finance and admin"], d)
    code, d = run(["maturity"], w)
    check("maturity: step 1 while most functions have no position", d.get("level") == 1 and "not an industry standard" in d.get("note", ""), d)

    w = full(work, "full")
    code, d = run(["check"], w)
    check("check: a complete blueprint is GO", code == 0 and d.get("verdict") == "GO", d)
    check("check: the owner holding every seat is noted, not failed", any("holds all 3" in x for x in d.get("watch", [])), d)
    code, d = run(["handoff"], w)
    rank = [r["key"] for r in d.get("rank", [])]
    check("handoff: teachable, written-down work ranks above more hours of owner-only work", rank == ["delivery", "sales", "finance"]
          and [x["score"] for x in d["rank"]] == [6.4, 5.1, 0.6] and d.get("hours_named") == 31, d)
    steps = {r["key"]: r["first_step"] for r in d.get("rank", [])}
    check("handoff: undocumented work is written down first", "write it down first" in steps["finance"], steps)
    check("handoff: work only the owner can do is questioned, not handed off", "owner-only" in steps["delivery"], steps)
    check("handoff: documented, teachable work is ready", "ready to hand off" in steps["sales"], steps)
    check("handoff: it says it does not predict", "does not predict" in d.get("note", ""))
    code, d = run(["maturity"], w)
    check("maturity: step 3 when the check is GO and nothing is reviewed", d.get("level") == 3, d)

    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.1", "--today", "2026-10-05"], w)
    check("review: a crossed trigger prints the six questions, person last", d.get("trigger_crossed") is True and len(d.get("look_into_it", [])) == 6
          and d["look_into_it"][-1].startswith("Only then"), d)
    check("review: no decision about a job is made from the file", "No decision about a person" in d.get("note", ""))
    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.1", "--cause", "person"], w)
    check("review: 'person' is refused until the other causes are ruled out", code == 1 and "ruled out" in d.get("error", ""), d)
    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.1", "--cause", "person", "--ruled-out",
                   "the report was checked, the target was met last quarter, the procedure was followed, training was done",
                   "--today", "2026-10-05"], w)
    check("review: 'person' is accepted once the others are ruled out in words", code == 0, d)
    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.1", "--cause", "laziness"], w)
    check("review: an unknown cause is refused", code == 1, d)
    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.25", "--today", "2026-11-09"], w)
    check("review: a number inside the trigger raises nothing", d.get("trigger_crossed") is False and "look_into_it" not in d, d)
    check("review: it is shown against the member's target", "target of 0.3" in d.get("against_target", ""), d)
    for day in ("2026-10-12", "2026-10-19"):
        run(["review", "--kpi", "KPI-02", "--value", "0.25", "--today", day], w)
    code, d = run(["review", "--kpi", "KPI-02", "--value", "0.25", "--today", "2031-01-01"], w)
    check("review: a date in the future is refused", code == 1 and "future" in d.get("error", ""), d)
    code, d = run(["maturity", "--today", "2026-11-10"], w)
    check("maturity: step 4 after four weeks of reviews", d.get("level") == 4, d)
    code, d = run(["position", "hold", "--id", "POS-02", "--held-by", "sales assistant", "--today", "2026-11-10"], w)
    check("hold: handing a seat to someone else is recorded", d.get("handed_off") is True, d)
    data = json.loads((w / "blueprint/blueprint.json").read_text())
    check("hold: the function is now covered by the new holder", next(f for f in data["functions"] if f["key"] == "sales")["covered_by"] == "sales assistant")
    for n in range(4):
        run(["review", "--kpi", "KPI-02", "--value", "0.28", "--today", "2026-11-11"], w)
    code, d = run(["maturity", "--today", "2026-11-15"], w)
    check("maturity: four reviews on one day do not make step 5", d.get("level") == 4, d)
    # step 5 needs four different weeks after the hand-off; those weeks have not happened yet, so the file is dated back by hand
    data = json.loads((w / "blueprint/blueprint.json").read_text())
    data["handed"][0]["date"] = "2026-10-01"
    (w / "blueprint/blueprint.json").write_text(json.dumps(data), encoding="utf-8")
    code, d = run(["maturity", "--today", "2026-11-15"], w)
    check("maturity: step 5 once a handed-off seat has reviews in four different weeks", d.get("level") == 5 and d["evidence"]["positions_handed_off_and_reviewed"] == ["POS-02"], d)

    code, d = run(["render", "--today", "2026-11-15"], w)
    bp = w / "blueprint"
    check("render: the chart, contracts, definitions and scorecard are written", code == 0 and (bp / "org-chart.md").exists() and (bp / "kpis.md").exists()
          and (bp / "scorecard.md").exists() and len(list((bp / "positions").glob("*.md"))) == 3, d)
    con = (bp / "positions/pos-02-sales-lead.md").read_text(encoding="utf-8")
    check("render: the contract says it is not an employment contract", "not an employment contract" in con)
    check("render: the contract carries mission, results, authority, procedures and signatures",
          all(x in con for x in ("## Why this position exists", ACC[0], "## What it may decide alone", "New enquiry reply", "Holder: ____")))
    check("render: the measure shows its baseline with its source and its target with its basis",
          "0.2 (CRM, July to September)" in con and "0.3 (member decision)" in con and "below 0.15" in con)
    own = (bp / "positions/pos-01-owner.md").read_text(encoding="utf-8")
    check("render: an unmeasured baseline is printed as not measured yet", "not measured yet" in own and "not set" in own)
    chart = (bp / "org-chart.md").read_text(encoding="utf-8")
    check("render: the chart shows who reports to whom and who holds each seat", "  - **Sales Lead** (POS-02)" in chart and "held by sales assistant" in chart
          and "POS01 --> POS02" in chart)
    sc = (bp / "scorecard.md").read_text(encoding="utf-8")
    check("render: the scorecard shows the latest recorded number", "| Sales Lead | Enquiry to client rate | 0.28 | 2026-11-11 | 0.3 | no |" in sc, sc)
    allmd = con + own + chart + sc + (bp / "kpis.md").read_text(encoding="utf-8")
    check("render: no em or en dash in any document", "—" not in allmd and "–" not in allmd)
    code, d = run(["report"], w)
    check("report: counts of what is on file, and not a forecast", d["counts"]["positions"] == 3 and d["counts"]["handed_off"] == 1
          and d["counts"]["kpis_not_measured_yet"] == 2 and "forecast" in d.get("note", ""), d)

    (bp / "blueprint.json").write_text('{"positions":[{"id":"POS-01"}],"kpis":[{}],"functions":[{}]}', encoding="utf-8")
    for cmd in ("check", "handoff", "maturity", "render", "report"):
        code, d = run([cmd], w)
        check(f"a hand-edited blueprint.json gives no traceback in {cmd}", "_raw" not in d, d)
    (bp / "blueprint.json").write_text("{ nope", encoding="utf-8")
    code, d = run(["report"], w)
    check("a broken blueprint.json refuses cleanly", code == 1 and "not valid JSON" in d.get("error", ""), d)


def review_tests(work):
    """Regressions from the independent review."""
    w = setup(work, "rev")
    fn(w, "sales", "Sales", 6, 5, 4)
    fn(w, "delivery", "Delivery", 20, 1, 4)
    fn(w, "finance", "Finance and admin", 3, 3, 3, by="the owner's assistant")
    code, d = run(["handoff"], w)
    rows = {r["key"]: r for r in d.get("rank", [])}
    check("review: work anyone trained could do is ready; work only the owner can do is questioned",
          "ready to hand off" in rows["sales"]["first_step"] and "owner-only" in rows["delivery"]["first_step"], d)
    check("review: 'the owner's assistant' is not ranked as the owner", "finance" not in rows and any("Finance" in x for x in d.get("covered_by_someone_else", [])), d)
    position(w, "Owner", "delivery", appr=())
    # vague lines
    for mission in ("Helping out with the general operations stuff wherever it is wanted", "a b c d e f g h"):
        code, d = position(w, "Ops", "sales", reports="POS-01", mission=mission)
        check(f"review: a vague or empty mission is refused: {mission[:30]}", code == 1, d)
    for bad in (["Helps with sales and things when asked to", ACC[0], ACC[1]], [ACC[0], ACC[0], ACC[1]], ["a b c d e f", ACC[0], ACC[1]],
                ["Works 40 hours a week for a salary agreed each year", ACC[0], ACC[1]],
                ["Employment may be terminated with two weeks notice given", ACC[0], ACC[1]]):
        code, d = position(w, "Ops", "sales", reports="POS-01", acc=bad)
        check(f"review: a vague, repeated or employment-term accountability is refused: {bad[0][:34]}", code == 1, d)
    good = ["Support requests get a reply within one working day", "Help desk tickets are closed within two working days",
            "Handle every refund request within two working days of receipt", "Do not let any invoice go unpaid past thirty days",
            "Invoices sent within two days"]
    code, d = position(w, "Client Care Lead", "sales", reports="POS-01", acc=good)
    check("review: specific lines that begin with support, help desk, handle or do are accepted", d.get("id") == "POS-02", d)
    # measures
    code, d = kpi(w, "POS-02", "New clients per month", rate=False, formula="count of clients who paid for the first time in the month")
    check("review: a count named 'per month' is not treated as a rate", code == 0, d)
    code, d = kpi(w, "POS-02", "Late tickets", rate=False, formula="count of tickets closed on/after the eleventh day")
    check("review: 'on/after' is not a rate", code == 0, d)
    code, d = kpi(w, "POS-02", "Win share", rate=False, formula="clients won divided by enquiries")
    check("review: 'divided by' is a rate and needs both halves", code == 1 and "numerator" in d.get("error", ""), d)
    for name, formula, extra in (("Activity", "count of key strokes logged by the monitoring tool", ()),
                                 ("Active minutes", "minutes the screen recording shows them active", ()),
                                 ("Presence", "minutes present divided by minutes scheduled", ("--numerator", "keystrokes and screenshots and gps tracking",
                                                                                          "--denominator", "web cam minutes"))):
        code, d = kpi(w, "POS-02", name, rate=False, formula=formula, extra=extra)
        check(f"review: a reworded watching-people measure is refused: {name}", code == 1 and "watched" in d.get("error", ""), d)
    for basis in ("industry average for bookkeepers", "a guess", "x"):
        code, d = kpi(w, "POS-02", "Reply time", rate=False, formula="average working hours from enquiry to first reply",
                      extra=("--baseline", "12", "--baseline-basis", basis))
        check(f"review: a baseline from '{basis}' is refused", code == 1, d)
    for flag, bad in (("--value", "abc"), ("--value", "nan")):
        code, d = run(["review", "--kpi", "KPI-01", flag, bad], w)
        check(f"review: a bad {flag} is refused as JSON", code == 1 and "_raw" not in d, d)
    # contacts, labels
    code, d = run(["aim", "--key", "objective", "--text", "Grow to ten clients, call me on 555-123-4567 or sam@example.com"], w)
    check("review: contact details in an aim answer are refused", code == 1, d)
    code, d = run(["position", "hold", "--id", "POS-02", "--held-by", "Sam, 07700 900123"], w)
    check("review: a phone number in held-by is refused", code == 1, d)
    code, d = run(["review", "--kpi", "KPI-01", "--value", "3", "--note", "Sam is useless, I rate him 2 out of 10"], w)
    check("review: a note that labels or rates a person is refused", code == 1 and "no person is scored" in d.get("error", ""), d)
    for ro in ("a a a a a a a a", "nothing was checked at all, Sam is just lazy"):
        code, d = run(["review", "--kpi", "KPI-01", "--value", "3", "--cause", "person", "--ruled-out", ro], w)
        check(f"review: 'person' with an empty ruling-out is refused: {ro[:20]}", code == 1, d)
    check("review: nothing with an @ or a rating reached the file", "@" not in (w / "blueprint/blueprint.json").read_text())
    code, d = position(w, "Dash", "sales", reports="POS-01", mission="Turn enquiries into clients ― the ones who are a good fit for us")
    check("review: a horizontal bar is refused like a dash", code == 1, d)
    code, d = position(w, "T" * 300, "sales", reports="POS-01")
    check("review: an overlong title is refused", code == 1 and "characters" in d.get("error", ""), d)
    code, d = position(w, "A | B", "sales", reports="POS-01")
    check("review: a table-breaking character is refused", code == 1, d)
    # position set keeps the measures
    code, d = run(["position", "set", "--id", "POS-02", "--mission", "Make sure every client question is answered well and quickly by the team"], w)
    data = json.loads((w / "blueprint/blueprint.json").read_text())
    check("review: a position can be changed and keeps its measures", d.get("version") == 2 and sum(1 for k in data["kpis"] if k["position"] == "POS-02") == 2, d)
    code, d = run(["position", "set", "--id", "POS-01", "--reports-to", "POS-02"], w)
    check("review: a reporting loop is refused", code == 1 and "loop" in d.get("error", ""), d)
    code, d = run(["position", "hold", "--id", "POS-02", "--held-by", "assistant to the owner"], w)
    check("review: 'assistant to the owner' is a hand-off", d.get("handed_off") is True, d)
    run(["position", "hold", "--id", "POS-02", "--held-by", "owner"], w)
    code, d = run(["report"], w)
    check("review: a seat taken back is no longer counted as handed off", d["counts"]["handed_off"] == 0, d)
    # check does not pass junk
    j = setup(work, "junk", aim=False)
    for k in ("primary_aim", "objective", "owner_role"):
        code, d = run(["aim", "--key", k, "--text", "."], j)
    check("review: an aim of '.' is refused", code == 1, d)
    # render never writes over the member's edits
    r = full(work, "render2")
    run(["render"], r)
    con = r / "blueprint/positions/pos-02-sales-lead.md"
    con.write_text(con.read_text() + "\nMy own note.\n", encoding="utf-8")
    code, d = run(["render"], r)
    check("review: render stops when a contract was edited by hand", code == 1 and "pos-02-sales-lead.md" in d.get("error", "") and "My own note." in con.read_text(), d)
    code, d = run(["render", "--replace"], r)
    check("review: render --replace writes over it", code == 0 and "My own note." not in con.read_text(), d)
    run(["position", "remove", "--id", "POS-03"], r)
    code, d = run(["render"], r)
    check("review: a removed position's contract is listed as left from before", d.get("left_from_before") == ["positions/pos-03-bookkeeper.md"], d)
    data = json.loads((r / "blueprint/blueprint.json").read_text())
    data["kpis"][1]["baseline_basis"] = ""
    data["kpis"][1]["target_basis"] = ""
    (r / "blueprint/blueprint.json").write_text(json.dumps(data), encoding="utf-8")
    code, d = run(["check"], r)
    fx = " | ".join(d.get("fix", []))
    check("review: a hand-edited baseline or target with no basis is a FIX", "nowhere it was read from" in fx and "no basis" in fx, d)
    run(["render", "--replace"], r)
    con_t = con.read_text()
    check("review: and it is not printed as a baseline or a target", "not measured yet" in con_t and "| not set |" in con_t and "0.2 (" not in con_t, con_t[-900:])
    data["positions"] = "oops"
    (r / "blueprint/blueprint.json").write_text(json.dumps(data), encoding="utf-8")
    code, d = run(["report"], r)
    check("review: a wrong-typed list refuses and is not reset", code == 1 and "Nothing was changed" in d.get("error", "")
          and json.loads((r / "blueprint/blueprint.json").read_text())["positions"] == "oops", d)
    (work / "afile").write_text("x", encoding="utf-8")
    code, d = run(["init", "--folder", "afile"], work)
    check("review: init on a path that is a file refuses cleanly", code == 1 and "_raw" not in d, d)
    # prefill: a template with only placeholders is not a source, whatever its status says
    b = work / "placeholders"
    b.mkdir()
    (b / "BUILDROOM_BUSINESS_FILE.md").write_text((ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text(encoding="utf-8")
                                                  .replace("**Status:** not started", "**Status:** in progress"), encoding="utf-8")
    run(["init"], b)
    code, d = run(["prefill"], b)
    check("review: placeholder-only sections are not offered as drafts", d.get("draft_from_file") == [], d.get("draft_from_file"))
    # the Business File beside the folder wins over the one in the current directory
    other = work / "elsewhere"
    other.mkdir()
    (other / "BUILDROOM_BUSINESS_FILE.md").write_text(FILE.replace("New enquiry reply", "Something else entirely"), encoding="utf-8")
    r2 = full(work, "beside")
    code, d = run(["check", "--folder", str(r2 / "blueprint")], other)
    check("review: SOP links are checked against the Business File beside the folder", not any("New enquiry reply" in x for x in d.get("watch", [])), d)


def wiring_tests():
    rd = lambda p: (ROOT / p).read_text(encoding="utf-8")  # noqa: E731
    skill = rd("skills/buildroom-company-blueprint/SKILL.md")
    refs = {p.name for p in (SK / "references").glob("*.md")}
    named = set(re.findall(r"references/([a-z0-9-]+\.md)", skill))
    check("skill: every reference SKILL.md names exists", named <= refs, named - refs)
    check("skill: every reference file is named in SKILL.md", refs <= named, refs - named)
    fm = skill.split("---")[1]
    check("skill: the description is within the 1024-character limit", len(re.search(r"description: \|\n(.*)", fm, re.S).group(1).strip()) <= 1024)
    others = skill + "".join(p.read_text(encoding="utf-8") for p in (SK / "references").glob("*.md") if p.name != "source-credit.md")
    check("skill: the programme and its author are named only in source-credit.md", not re.search(r"Gerber|E-Myth|EMyth", others))
    check("skill: source-credit says it is not affiliated or endorsed", "not affiliated" in rd("skills/buildroom-company-blueprint/references/source-credit.md"))
    measures = rd("skills/buildroom-company-blueprint/references/measures.md")
    check("skill: the starter ideas carry no percentages", "%" not in measures.split("## Starter ideas")[1])
    tpl = rd("templates/BUILDROOM_BUSINESS_FILE.md")
    check("template: §25 sits after §24 and before the session log", tpl.find("## 24. Speaking") < tpl.find("## 25. Company Blueprint") < tpl.find("## 8. Session Log"))
    check("template: version 1.11", "**File version:** 1.11" in tpl)
    check("template: the skill's copy matches", rd("skills/buildroom-company-blueprint/references/business-file-template.md") == tpl)
    spec = rd("BUSINESS-FILE-SPEC.md")
    check("spec: §25 is registered at version 1.11", "| 25 | Company Blueprint | Company Blueprint |" in spec and "**Version 1.11" in spec)
    check("viewer: §25 is in the section map", '25:{t:"Company Blueprint"' in rd("rollout/Business_File_Viewer.html"))
    road = rd("skills/buildroom-os/references/roadmap.md")
    check("roadmap: a section and trigger phrases", "### Systems — Company Blueprint" in road and '- Company Blueprint → "Build my company blueprint"' in road)
    check("navigator: the progress view runs to §25", "§14–§25" in rd("skills/buildroom-os/SKILL.md"))
    cl, sh = rd("rollout/universal/CLAUDE.md"), rd("rollout/universal/START-HERE.md")
    check("CLAUDE.md: the skill, the range and the rule", "`buildroom-company-blueprint` (§25" in cl and "§1–§25" in cl
          and "- **Company blueprint:**" in cl and "Forty-two skills" in cl)
    check("START-HERE: forty-two skills, twenty-five sections", "forty-two skills" in sh and "twenty-five sections" in sh)
    for doc in ("README.md", "rollout/MEMBER-README.md"):
        check(f"{doc}: lists the skill", "`buildroom-company-blueprint`" in rd(doc))
    check("Quick Start: the phrase is there", "Build my company blueprint" in rd("rollout/BuildRoom_OS_Quick_Start.html"))
    check("protocol: forty-two sessions", "42 standalone sessions" in rd("shared/business-file-protocol.md"))
    skills = [p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()]
    check("there are forty-two skills", len(skills) == 42, len(skills))
    check("no __pycache__ written into the skill folder", not list(SK.rglob("__pycache__")))


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="blueprint-tests-"))
    aim_tests(work)
    structure_tests(work)
    kpi_tests(work)
    whole_tests(work)
    review_tests(work)
    wiring_tests()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
