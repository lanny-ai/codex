#!/usr/bin/env python3
"""Event Launcher tests: the plan math and timeline, the calendar file and reminders, the run sheet,
the launch tracker (gate, pace, report, leaks, calls) and the Obsidian debrief.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/launch/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folder or here)
import hashlib, json, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-event-launcher"
S = SK / "scripts"
FX = HERE / "fixtures"
PY = sys.executable
PLAN, ICS, RUN, TRK = S / "launch_plan.py", S / "event_ics.py", S / "run_sheet.py", S / "launch_tracker.py"

# sha256[:16] of lower-case tokens that must never appear in the scripts, tests or fixtures (partner and staff
# names, the founder's list sizes and revenue figures). Hashed so this file does not carry them either.
FORBIDDEN = {'065fddbeaf0fc34f', '23c838ecd20edd5f', '3f2e23b2ee1991da', '7ca7b9cc82c9d0f4', '8602542c83be5936',
             '8a24c46499644add', '8d9bb76e99d5fa40', 'a5ae32a693f69037', 'b1efc77a39364d74', 'bef64bca7f1ac38e',
             'c3c8204aec16162a', 'cb0b20f98ee49533', 'cde2a74b37de9199', 'ce443c6c565fd26b', 'cecfdbfdbebbe96d',
             'f1c36001d0d18f0b', 'f660691d95cdfa87', 'f9d1af62d004d4da'}
BIG_OK = {"33,786"}                         # numbers of 10,000 or more allowed in the scripts (Livestorm's sessions)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:600]}" if detail and not ok else ""))


def run(args, cwd, ok_codes=(0,)):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    return p.returncode in ok_codes, p.stdout + p.stderr, p.returncode


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


# ---------------------------------------------------------------- confidentiality (B3)

SHARED_COPIES = {"kern-framework.md", "halbert-writing-system.md"}     # byte-identical copies shared with other skills
# the founder's registration rate (any spelling) and his payment split; built here so this file does not carry them
FOUNDER_RATE = re.compile(r"(?<![\d.])0\.6\d?\s?%|(?<![\d.])0\.006\d?(?!\d)")
FOUNDER_SPLIT = re.compile(r"(?<!\d)13\s*[×x*]\s*\$?997|(?<!\d)8\s*[×x*]\s*12\s*[×x*]|\$1" + r"37(?![\d,])")
FOUNDER_REG = hashlib.sha256(b"9" + b"69").hexdigest()[:16]          # the run's registration count


def doc_files():
    return [SK / "SKILL.md"] + sorted(f for f in (SK / "references").glob("*.md") if f.name not in SHARED_COPIES)


def confidentiality_tests():
    code = sorted(S.glob("*.py")) + [HERE / "run_tests.py"] + sorted(f for f in FX.rglob("*") if f.is_file())
    hits, big, rate_hits, split_hits, reg_hits = [], [], [], [], []
    for f in code + doc_files():
        text = f.read_text(encoding="utf-8").lower()
        name = str(f.relative_to(ROOT))
        toks = set(re.findall(r"[a-z]+|\d[\d,]*\d|\d", text))
        for tok in toks:
            if hashlib.sha256(tok.encode()).hexdigest()[:16] in FORBIDDEN:
                hits.append(f"{name}: a confidential token")
        if f.name != "run_tests.py":
            rate_hits += [f"{name}: {m}" for m in FOUNDER_RATE.findall(text)]
            split_hits += [f"{name}: {m}" for m in FOUNDER_SPLIT.findall(text)]
        if f in code and any(hashlib.sha256(t.encode()).hexdigest()[:16] == FOUNDER_REG for t in toks):
            reg_hits.append(name)
        if f.parent == S:
            for n in re.findall(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d,])|(?<![\d.])\d{5,}(?![\d.])", text):
                if int(n.replace(",", "")) >= 10000 and n not in BIG_OK:
                    big.append(f"{f.name}: {n}")
    check("B3: no partner/staff names, list sizes or revenue figures in the scripts, tests and fixtures",
          not [h for h in hits if not h.endswith(".md: a confidential token")], hits)
    check("X1: no partner/staff names, list sizes or revenue figures in SKILL.md and references/ (shared Kern and "
          "Halbert copies excepted)", not [h for h in hits if ".md:" in h], [h for h in hits if ".md:" in h])
    check("X1: the founder's registration rate appears nowhere (scripts, tests, fixtures, SKILL.md, references)",
          not rate_hits, rate_hits)
    check("X1: the founder's payment split (13/8, the instalment) appears nowhere", not split_hits, split_hits)
    check("X1: the scripts, tests and fixtures never print the founder's registration count", not reg_hits, reg_hits)
    check("B3: no number of 10,000 or more in the scripts except labelled benchmark sample sizes", not big, big)
    src = (S / "launch_plan.py").read_text(encoding="utf-8")
    check("X1: the founder's partner-sent list is described without a rate or a size",
          "A large partner-sent, mostly cold list registers far lower" in src
          and "21 program buyers after a $1 first step" in src, "")


# ---------------------------------------------------------------- launch_plan.py

def plan_tests(work):
    w = work / "plan"; w.mkdir()
    base = ["math", "--goal-buyers", "20", "--price", "997", "--format", "bootcamp3"]

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000"], w)
    d = pj(out); t = d.get("typical", {}); need = t.get("needed_for_goal", {})
    check("math: one typical path, no compounded scenarios", ok and "typical" in d and "scenarios" not in d, sorted(d))
    check("math: typical reverse funnel runs list → registrants → Day 1–3 → close → saw price → buyers",
          need.get("buyers") == 20 and need.get("list") > need.get("registrants") > need["day_live"][0] > need["day_live"][2]
          > need.get("present_at_close") > 0 and len(need["day_live"]) == 3, need)
    check("math: typical needs 2,204 registrants and 11,017 names at $997 for a free 3-day bootcamp (ceil)",
          need.get("registrants") == 2204 and need.get("list") == 11017, need)
    check("X11: free event to a warm list: show-up 30/38/45 (the docs' band); retention cautious 50% (audit), strong 80%",
          [d["rates"]["show_up"][k] for k in ("cautious", "typical", "strong")] == [.30, .38, .45]
          and [d["rates"]["retention"][k] for k in ("cautious", "typical", "strong")] == [.50, .70, .80]
          and d["rates"]["retention"]["source"]["cautious"] == "Build Room founder audit 2026"
          and "Build Room founder audit 2026" in d["sources"], d["rates"].get("retention"))
    check("M17: saw the price = present × 1.0 by default (no replay uplift assumed)",
          d["rates"]["saw_price"]["typical"] == 1.0 and need["saw_price"] == need["present_at_close"]
          and "conversion bands apply to those who saw the price" in d["rates"]["saw_price"]["note"], d["rates"]["saw_price"])
    check("M17: the conversion label says it applies to those who saw the price",
          "applies to those who saw the price" in d["rates"]["conversion"]["note"]
          and any("apply to those who saw the price" in x for x in d["notes"]), d["rates"]["conversion"])
    check("math: price band $500–1,999 from Scale For Impact 2026", d.get("price_band") == "$500–1,999"
          and d["rates"]["conversion"]["source"] == "Scale For Impact 2026" and d["rates"]["conversion"]["typical"] == .075,
          d.get("rates", {}).get("conversion"))
    srcs = d.get("sources", {})
    check("math: every benchmark prints its source key with a description",
          {"Build Room assumption", "Scale For Impact 2026", "Build Room founder run Jul 2026", "Build Room founder rule of thumb"} <= set(srcs)
          and all(srcs.values()), sorted(srcs))
    check("math: the registration rate is labelled a Build Room assumption and warned",
          d["rates"]["registration"]["source"] == "Build Room assumption"
          and any("no published benchmark" in x for x in d.get("warnings", [])), d.get("warnings"))
    ex = t.get("expected_from_list", {})
    check("M6: expected from the list kept apart from needed for the goal", 9.0 < ex.get("buyers", 0) < 9.2
          and ex.get("registrants") == 1000 and t["expected_registrants_range"] == {"cautious": 500, "typical": 1000, "strong": 1500}, ex)
    check("M15: verdict from the typical path's share of the goal (9.1 of 20 = 45% → not from this list alone)",
          d.get("verdict") == "not from this list alone: add partners/ads or lower the goal"
          and d["verdict_detail"]["share_of_goal"] == .454, d.get("verdict_detail"))
    sens = d.get("sensitivity", {})
    check("M14: single-stage sensitivity: each stage alone at cautious and strong, others typical",
          set(sens) == {"registration", "show_up", "retention", "stay_to_close", "conversion"}
          and abs(sens["show_up"]["cautious"]["expected_buyers"] - 7.17) < .02
          and abs(sens["conversion"]["strong"]["expected_buyers"] - 12.10) < .02
          and sens["registration"]["assumption_only"] and not sens["show_up"]["assumption_only"], sens.get("show_up"))
    lv = d.get("lever", {})
    check("M14: biggest lever = largest buyer swing on real ranges; assumption-only stages left out (retention, now "
          "that its cautious value is the audit's 50%)",
          lv.get("stage") == "retention" and abs(lv["buyer_swing"] - 7.23) < .02 and "registration" not in lv["all_swings"]
          and "registration" in lv["note"] and list(lv["all_swings"]) == ["retention", "conversion", "stay_to_close", "show_up"], lv)
    lw = pj(run([PY, PLAN, "math", "--goal-buyers", "20", "--price", "997", "--format", "webinar", "--list-size", "5000"], w)[1])["lever"]
    check("M14/X5: the conversion lever is generic to the close and never assumes a deadline",
          lw.get("stage") == "conversion" and "coupon" not in lw.get("how", "") and "money path" in lw.get("how", "")
          and "an honest deadline only if one is true" in lw["how"] and "a real deadline" not in lw["how"], lw.get("how"))
    fr = d.get("founder_reference", {})
    check("M25/X11: founder figures reconciled: 21 program buyers after a $1 first step; 56% of 41 who saw the price "
          "after a $1 first step (follow-up analysis), its own source; no registration rate",
          fr["program_buyers"]["value"] == 21 and fr["saw_price_conversion"]["value"] == .56
          and fr["saw_price_conversion"]["counts"] == "23 of 41"
          and fr["saw_price_conversion"]["what"] == "of 41 people who saw the price after a $1 first step (follow-up analysis)"
          and fr["saw_price_conversion"]["source"] == "Build Room founder follow-up analysis Jul 2026"
          and "21 program buyers after a $1 first step" in srcs["Build Room founder run Jul 2026"]
          and "registered" not in srcs["Build Room founder run Jul 2026"] and "registration" not in json.dumps(fr["program_buyers"])
          and "23 of 41" not in srcs["Build Room founder run Jul 2026"]
          and "23 of 41" in srcs["Build Room founder follow-up analysis Jul 2026"], fr)

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "10000"], w)
    check("M15: 10,000 names → 18.2 of 20 (91%) is a stretch", pj(out).get("verdict") == "stretch", pj(out).get("verdict_detail"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "20000"], w)
    check("math: a big enough list is reachable", pj(out).get("verdict") == "reachable", pj(out).get("verdict"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "800"], w)
    check("math: a small list is 'not from this list alone'",
          pj(out).get("verdict") == "not from this list alone: add partners/ads or lower the goal", pj(out).get("verdict"))

    # B1/X3: rate parsing: "%" is a percent; no "%" must be a fraction strictly between 0 and 1
    for raw, want in (("0.5%", .005), ("1%", .01), ("0.5", .5), ("0.35", .35), ("12%", .12), ("100%", 1.0), ("2%", .02)):
        ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--history-reg-rate", raw], w)
        got = pj(out).get("rates", {}).get("registration", {}).get("typical")
        check(f"X3: rate {raw!r} → {want}", ok and got is not None and abs(got - want) < 1e-12, got)
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "10000", "--format", "bootcamp3", "--list-size",
                      "2000", "--close", "call", "--history-reg-rate", "0.5%"], w)
    eb = pj(out)["typical"]["expected_from_list"]["registrants"]
    check("B1: 0.5% of 2,000 is 10 registrants, not 1,000", abs(eb - 10) < .01, eb)
    for raw in ("1", "35", "140", "1.5", "0", "-5%", "101%", "0%", "abc", "nan"):
        ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", f"--history-showup={raw}"], w, ok_codes=(2,))
        check(f"X3: rate {raw!r} refused, asking for \"35%\" or \"0.35\"", ok and '\\"35%\\"' in out and '\\"0.35\\"' in out,
              out[-250:])
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--history-reg-rate", "70%", "--history-showup", "95%",
                      "--history-conversion", "45%"], w)
    ws = pj(out).get("warnings", [])
    check("X3: implausibly high history rates are warned (registration >60%, show-up >90%, conversion >40%)",
          ok and any("--history-reg-rate 70%" in x and "unusually high" in x for x in ws)
          and any("--history-showup 95%" in x for x in ws) and any("--history-conversion 45%" in x for x in ws), ws)

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--history-reg-rate", "12%", "--history-showup", "0.45"], w)
    d = pj(out)
    check("math: member history replaces the assumptions (cautious 80%, strong 120%)",
          d["rates"]["registration"]["source"] == "Member history" and d["rates"]["registration"]["typical"] == .12
          and d["rates"]["show_up"]["typical"] == .45 and abs(d["rates"]["show_up"]["cautious"] - .36) < 1e-9
          and "Member history" in d["sources"] and not any("no published benchmark" in x for x in d.get("warnings", [])), d.get("rates"))
    check("math: with history, registration joins the lever comparison", "registration" in d["lever"]["all_swings"], d.get("lever"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--history-retention", "67.6%", "--history-stay", "50.4%",
                      "--history-conversion", "9%"], w)
    d = pj(out)
    check("M16: --history-retention, --history-stay and --history-conversion replace their stages",
          ok and d["rates"]["retention"]["typical"] == .676 and d["rates"]["stay_to_close"]["typical"] == .504
          and d["rates"]["conversion"]["typical"] == .09 and all(d["rates"][k]["source"] == "Member history"
                                                                for k in ("retention", "stay_to_close", "conversion"))
          and d["inputs"]["history"] == {"retention": .676, "stay_to_close": .504, "conversion": .09}, d.get("inputs"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "10000", "--format", "bootcamp3", "--list-size", "2000",
                      "--close", "call", "--history-booked", "15%", "--history-held", "80%", "--history-closed", "0.2"], w)
    d = pj(out)
    check("M16: call history flags (--history-booked/-held/-closed)", ok and d["rates"]["booked"]["typical"] == .15
          and d["rates"]["held"]["typical"] == .8 and d["rates"]["closed"]["typical"] == .2
          and all(d["rates"][k]["source"] == "Member history" for k in ("booked", "held", "closed"))
          and not d["sensitivity"]["held"]["assumption_only"], d.get("rates", {}).get("held"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "20", "--price", "297", "--format", "challenge5", "--list-size", "5000"], w)
    check("math: a 5-day challenge's biggest lever is day-over-day retention (applied four times)",
          pj(out).get("lever", {}).get("stage") == "retention", pj(out).get("lever"))

    # B2: call close
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "10000", "--format", "bootcamp3", "--list-size", "2000",
                      "--close", "call"], w)
    d = pj(out); n = d["typical"]["needed_for_goal"]
    check("B2: --close call: saw the offer → booked (10–20%) → held (70–80%) → closed (10–25%), labelled",
          ok and "conversion" not in d["rates"] and d["rates"]["booked"]["cautious"] == .10 and d["rates"]["booked"]["strong"] == .20
          and d["rates"]["held"]["typical"] == .75 and d["rates"]["held"]["source"] == "Build Room assumption"
          and d["rates"]["closed"]["cautious"] == .10 and d["rates"]["closed"]["strong"] == .25
          and d["rates"]["closed"]["source"] == "Webinar call rates (vendor, weak)"
          and "Webinar call rates (vendor, weak)" in d["sources"], d.get("rates"))
    check("B2: the call path needs booked, held and closed counts", n["calls_closed"] == 5 and n["calls_held"] == 29
          and n["calls_booked"] == 39 and abs(d["typical"]["per_viewer"]["buy"] - .15 * .75 * .175) < 1e-6, n)
    check("B2: call close lever and warnings speak of calls", d["lever"]["stage"] in ("booked", "closed", "retention", "stay_to_close", "show_up")
          and any("call-close rates are weak evidence" in x for x in d.get("warnings", []))
          and d["sensitivity"]["held"]["assumption_only"], d.get("lever"))

    # M1: tiers, one door at a time
    ok, out, _ = run([PY, PLAN, "math", "--goal-cash", "30000", "--tiers", "Core:997:70", "VIP:2997:30%",
                      "--list-size", "3000", "--format", "challenge5"], w)
    d = pj(out)
    check("M1: --goal-cash with --tiers: each tier at its own band (Core 7.5%, VIP 2.5%) → $1,247 average, 25 buyers",
          ok and d["goal"]["average_price"] == 1247 and d["goal"]["buyers"] == 25 and d["goal"]["binding"] == "goal-cash"
          and [x["band"] for x in d["tiers"]] == ["$500–1,999", "$2,000 and up"]
          and len(d["typical"]["needed_for_goal"]["day_live"]) == 5 and "retention" in d["rates"], d.get("goal"))
    check("M1: tiers across bands show a mixed band and the $2,000 checkout warning",
          d.get("price_band", "").startswith("mixed") and any("--close call" in x for x in d.get("warnings", [])), d.get("warnings"))
    one = pj(run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "10000", "--list-size", "2000", "--format", "bootcamp3"], w)[1])
    two = pj(run([PY, PLAN, "math", "--goal-buyers", "5", "--tiers", "Lab:997:80", "Top:10000:20", "--list-size", "2000",
                  "--format", "bootcamp3"], w)[1])
    b1, b2 = one["typical"]["expected_from_list"]["buyers"], two["typical"]["expected_from_list"]["buyers"]
    check("M1: adding a $997 door to a $10,000 offer adds buyers (no longer the weighted-average band)",
          b2 > 2 * b1 and two["tiers"][0]["expected_buyers"] > two["tiers"][1]["expected_buyers"], (b1, b2))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--tiers", "Lab:997:80", "Top:10000:20", "--list-size", "2000",
                      "--format", "bootcamp3", "--close", "both"], w)
    d = pj(out)
    check("B2/M1: --close both sends the $10,000 tier to a call and the $997 tier to checkout",
          ok and [x["channel"] for x in d["tiers"]] == ["checkout", "call"] and "booked" in d["rates"] and "conversion" in d["rates"]
          and "checkout_buyers" in d["typical"]["needed_for_goal"], d.get("tiers"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--tiers", "Lab:997:80:call", "Top:10000:20", "--list-size", "2000",
                      "--format", "bootcamp3", "--close", "checkout"], w)
    check("math: a tier can name its own close (:call)", [x["channel"] for x in pj(out).get("tiers", [])] == ["call", "checkout"], out[-300:])

    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--goal-cash", "20000", "--price", "997", "--list-size", "3000",
                      "--format", "webinar"], w)
    d = pj(out)
    check("math: both goals given, the larger buyer count wins; a webinar has no retention step",
          d["goal"]["buyers"] == 21 and "retention" not in d["rates"] and len(d["typical"]["needed_for_goal"]["day_live"]) == 1, d.get("goal"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "4500", "--list-size", "3000", "--format", "workshop"], w)
    d = pj(out)
    check("math: $2,000+ at checkout uses the 1–4% band and suggests --close call",
          d["rates"]["conversion"]["cautious"] == .01 and any("--close call" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "30", "--price", "47", "--list-size", "3000", "--format", "workshop",
                      "--paid-event"], w)
    d = pj(out)
    check("math: --paid-event uses paid show-up and the HSH-backed conversion", d["rates"]["show_up"]["typical"] == .60
          and d["rates"]["conversion"]["source"] == "HSH 2025" and d["rates"]["registration"]["typical"] == .06, d.get("rates"))
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--replay-uplift", "1.25"], w)
    d = pj(out)
    check("M17: --replay-uplift is an optional, labelled assumption (cautious 1.0, typical as given)",
          ok and d["rates"]["saw_price"]["cautious"] == 1.0 and d["rates"]["saw_price"]["typical"] == 1.25
          and d["rates"]["saw_price"]["source"] == "Build Room assumption" and "--replay-uplift" in d["rates"]["saw_price"]["note"]
          and d["typical"]["needed_for_goal"]["registrants"] < 2204, d["rates"]["saw_price"])
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--replay-uplift", "3"], w, ok_codes=(2,))
    check("M17: --replay-uplift outside 1.0–2.0 is refused", ok and "between 1.0 and 2.0" in out, out[-200:])

    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--md"], w)
    check("math --md prints the typical path, the sensitivity, the verdict and sources", ok and out.startswith("# Launch math")
          and "## Typical path" in out and "## Sensitivity (one stage at a time)" in out and "| List | 11,017 | 5,000 |" in out
          and "Conversion of those who saw the price" in out and "Scale For Impact 2026" in out
          and "**Verdict:** not from this list alone" in out and "Cautious | Typical | Strong" in out, out[:600])
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--md", "math.md", "--out", "planA"], w)
    check("math --md FILE writes it and still prints JSON; --out writes plan.json", ok and (w / "math.md").exists()
          and pj(out).get("verdict", "").startswith("not from") and json.loads((w / "planA/plan.json").read_text())["math"]["goal"]["buyers"] == 20, out[-300:])
    ok, out, _ = run([PY, PLAN, *base, "--list-size", "5000", "--out", "2026-11-cash-flow-bootcamp"], w)
    check("m31: --out takes a launch slug and writes launches/<slug>/plan.json", ok
          and (w / "launches/2026-11-cash-flow-bootcamp/plan.json").exists()
          and pj(out).get("folder") == "launches/2026-11-cash-flow-bootcamp", out[-300:])

    for args, needle, label in [
        (["math", "--price", "997", "--format", "bootcamp3", "--list-size", "100"], "a goal is needed", "no goal"),
        (["math", "--goal-buyers", "10", "--format", "bootcamp3", "--list-size", "100"], "a price is needed", "no price"),
        (["math", "--goal-buyers", "10", "--tiers", "A:100:50", "B:200:30", "--format", "bootcamp3", "--list-size", "100"],
         "must add up to 100%", "tier shares not 100%"),
        (["math", "--goal-buyers", "10", "--tiers", "A-100-50", "--format", "bootcamp3", "--list-size", "100"], "Name:price:share", "bad tier"),
        (["math", "--goal-buyers", "10", "--price", "997", "--format", "bootcamp3"], "--list-size", "no list size"),
        (["math", "--goal-buyers", "10", "--price", "-5", "--format", "bootcamp3", "--list-size", "100"], "more than 0", "negative price"),
    ]:
        ok, out, _ = run([PY, PLAN, *args], w, ok_codes=(2,))
        check(f"math refuses: {label} (exit 2)", ok and needle in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "10", "--price", "997", "--format", "bootcamp9", "--list-size", "100"], w, ok_codes=(2,))
    check("math refuses an unknown format", ok and "invalid choice" in out, out[-200:])

    # timeline
    TL = ["timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "America/New_York", "--date", "2026-10-17"]
    ok, out, _ = run([PY, PLAN, *TL, "--cart-days", "3", "--out", "planA"], w)
    d = pj(out); ml = d.get("milestones", []); ms = {m["id"]: m for m in ml}
    pos = {m["id"]: i for i, m in enumerate(ml)}
    check("timeline: milestones in date order with weekday names", ok and [m["date"] for m in ml] == sorted(m["date"] for m in ml)
          and ms["day1"]["weekday"] == "Tue" and ms["day1"]["date"] == "2026-12-01", [(m["date"], m["id"]) for m in ml][:6])
    check("X4: gate_pre_invite comes before the first send of any kind (the belief emails)",
          ms["gate_pre_invite"]["date"] == "2026-11-08" and ms["belief_1"]["date"] == "2026-11-10"
          and "launch_gate" not in ms and "--stage pre_invite" in ms["gate_pre_invite"]["detail"]
          and all(pos["gate_pre_invite"] < pos[m["id"]] for m in ml if m["kind"] == "send"), ms["gate_pre_invite"])
    check("X4: gate_day_before on Day 1 −1 (after the reminder dry run, before the day-before email); gate_close_morning "
          "before the close-day session; gate_cart before cart_1",
          ms["gate_day_before"]["date"] == "2026-11-30" and pos["reminder_dry_run"] < pos["gate_day_before"] < pos["day_before"]
          and "night email" in ms["gate_day_before"]["detail"]
          and ms["gate_close_morning"]["date"] == "2026-12-03" and pos["gate_close_morning"] < pos["day3"]
          and "close_morning_gate" not in ms and ms["gate_cart"]["date"] == "2026-12-04" and pos["gate_cart"] < pos["cart_1"]
          and "--stage cart" in ms["gate_cart"]["detail"], [(m["id"], m["date"]) for m in ml if m["id"].startswith("gate")])
    inv = [ms[f"invite_{k}"]["date"] for k in range(1, 8)]
    check("M8: seven dated invitations from 14 days out, the last three days daily (Livestorm)",
          inv == ["2026-11-17", "2026-11-20", "2026-11-23", "2026-11-26", "2026-11-28", "2026-11-29", "2026-11-30"]
          and ms["invite_1"]["source"] == "Livestorm 2026" and "invite_8" not in ms, inv)
    check("M8: the default sequence has a dated row per email (belief ×3, confirmation, pre-work, day-before, mornings, "
          "nights, close-morning, cart)",
          all(k in ms for k in ("belief_1", "belief_2", "belief_3", "first_win_emails", "confirmation", "prework", "day_before",
                                "day1_morning", "day2_morning", "day3_morning", "cart_1", "cart_2", "cart_3"))
          and ms["day3_morning"]["title"] == "Close-morning email" and ms["confirmation"]["date"] == "2026-11-17", sorted(ms))
    check("M8: first-win tool built, timed and promoted before the invitations",
          ms["first_win_build"]["date"] == "2026-10-27" and ms["first_win_timed"]["date"] == "2026-11-03"
          and ms["first_win_emails"]["date"] == "2026-11-13" and pos["first_win_emails"] < pos["invite_1"], ms.get("first_win_build"))
    check("X8: sending_domain 28 days before the first list email (compressed to today here, and warned); no SMS "
          "milestone without --sms",
          ms["sending_domain"].get("compressed") and ms["sending_domain"]["planned"] == "2026-10-13"
          and "SPF, DKIM and DMARC" in ms["sending_domain"]["detail"] and "2–4 weeks" in ms["sending_domain"]["detail"]
          and "sms_registration" not in ms and "a2p" not in ms
          and any(x.startswith("sending domain: under 28 days") for x in d.get("warnings", [])), ms["sending_domain"])
    check("timeline: night-before recaps on the evening of each day before the last", ms["day1_night"]["date"] == "2026-12-01"
          and ms["day2_night"]["date"] == "2026-12-02" and "day3_night" not in ms, sorted(ms))
    check("M7: follow-up starts the night of Day 1 (no-shows, 'come live tomorrow'), failed checkouts the same day",
          ms["followup_noshow"]["date"] == "2026-12-01" and ms["followup_failed"]["date"] == "2026-12-03"
          and pos["followup_noshow"] < pos["day2"] and "tomorrow" in ms["followup_noshow"]["detail"], ms.get("followup_noshow"))
    check("minor: non-buyer follow-up starts after the last cart email (the day after the cart closes), not with cart_1",
          ms["followup_nonbuyers"]["date"] == "2026-12-07" and pos["cart_3"] < pos["followup_nonbuyers"]
          and "after the cart closes" in ms["followup_nonbuyers"]["title"], ms.get("followup_nonbuyers"))
    check("minor: a mid-cart live Q&A in a cart of 3 days", ms.get("cart_live_qa", {}).get("date") == "2026-12-05"
          and ms["cart_live_qa"]["kind"] == "event", ms.get("cart_live_qa"))
    check("M7: the replay window never outlives the deadline (cart closes 3 days after; replay closes then too)",
          ms["cart_close"]["date"] == "2026-12-06" and ms["replay_closes"]["date"] == "2026-12-06" and d["cart_close"] == "2026-12-06"
          and d["deadline_date"] == "2026-12-06" and d["cart_days"] == 3, (ms["cart_close"]["date"], ms["replay_closes"]["date"]))
    check("S1: follow-up ends 10 days after the close, nurture_resume +11, debrief +12, next_cohort_or_evergreen_decision +14",
          ms["followup_end"]["date"] == "2026-12-16" and ms["nurture_resume"]["date"] == "2026-12-17"
          and ms["debrief"]["date"] == "2026-12-18" and ms["next_cohort_or_evergreen_decision"]["date"] == "2026-12-20"
          and "evergreen" in ms["next_cohort_or_evergreen_decision"]["detail"], [(k, ms[k]["date"]) for k in
          ("followup_end", "nurture_resume", "debrief", "next_cohort_or_evergreen_decision") if k in ms])
    check("m19/X12: US (from America/New_York): Thanksgiving, Black Friday weekend and Cyber Monday flagged on the invitations",
          d["country"] == "US" and ms["invite_4"].get("holiday") == "Thanksgiving" and ms["invite_5"].get("holiday") == "Black Friday weekend"
          and ms["invite_7"].get("holiday") == "Cyber Monday" and ms["invite_3"].get("holiday") == "Thanksgiving week"
          and any("Thanksgiving" in x and "Invitation 4" in x for x in d.get("warnings", []))
          and "US federal holidays" in d["sources"], d.get("warnings"))
    check("m19: weekend sends are flagged", ms["invite_5"].get("weekend") and ms["invite_6"].get("weekend")
          and any(x.startswith("sends on a weekend") and "invite_5 Sat" in x for x in d.get("warnings", []))
          and not ms["invite_4"].get("weekend"), d.get("warnings"))
    check("m19: a federal holiday on another send is listed (Veterans Day)", ms["belief_2"].get("holiday") == "Veterans Day"
          and any("belief_2 2026-11-11 (Veterans Day)" in x for x in d.get("warnings", [])))
    plan = json.loads((w / "planA/plan.json").read_text())
    cal = (w / "planA/calendar.md").read_text()
    weeks = re.findall(r"## Week of Mon (\S+)", cal)
    check("timeline --out merges into plan.json (math kept) and writes calendar.md with every week",
          "math" in plan and plan["timeline"]["event_date"] == "2026-12-01" and "| 2026-11-17 | Tue | **Invitation 1 of 7**" in cal
          and len(weeks) == 10 and weeks[0] == "2026-10-12" and weeks[-1] == "2026-12-14", weeks)

    # X5: no default deadline
    ok, out, _ = run([PY, PLAN, *TL], w, ok_codes=(2,))
    check("X5: timeline without --cart-days, --deadline-date or --no-deadline is refused (no default deadline)",
          ok and "There is no default deadline" in out and "--no-deadline" in out, out[-300:])
    ok, out, _ = run([PY, PLAN, *TL, "--cart-days", "3", "--no-deadline"], w, ok_codes=(2,))
    check("X5: --cart-days with --no-deadline is refused", ok and "give one of" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, *TL, "--deadline-date", "2026-12-05"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("X5: --deadline-date sets the cart close (2 days after the final day; no mid-cart Q&A for 2 days? one at f+1)",
          ok and d["cart_close"] == "2026-12-05" and d["cart_days"] == 2 and ms["cart_close"]["date"] == "2026-12-05"
          and "cart_3" not in ms and ms["cart_live_qa"]["date"] == "2026-12-04", d.get("cart_close"))
    ok, out, _ = run([PY, PLAN, *TL, "--deadline-date", "2026-12-02"], w, ok_codes=(2,))
    check("X5: a --deadline-date before the final day is refused", ok and "before the final day" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, *TL, "--no-deadline", "--invites", "5"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("M7/X5: --no-deadline: no cart close and no cart emails; replay runs its 7 days; follow-up has a stated end; an "
          "optional office hour; nothing says 'deadline' except to say there is none",
          ok and "cart_close" not in ms and not any(k.startswith("cart_") for k in ms) and d["cart_close"] is None
          and d["deadline"] is False and ms["replay_closes"]["date"] == "2026-12-10" and ms["followup_end"]["date"] == "2026-12-13"
          and "office_hour" in ms and ms["followup_nonbuyers"]["date"] == "2026-12-04"
          and not any("real deadline" in m["detail"] for m in ms.values())
          and any("--no-deadline" in x for x in d.get("warnings", [])), sorted(ms))
    check("M8: --invites 5 lays out five invitations", [ms[f"invite_{k}"]["date"] for k in range(1, 6)] ==
          ["2026-11-17", "2026-11-23", "2026-11-28", "2026-11-29", "2026-11-30"] and "invite_6" not in ms, sorted(ms))

    # S2 waitlist, X8 sms, call close
    ok, out, _ = run([PY, PLAN, *TL, "--cart-days", "3", "--waitlist", "--sms", "--close", "call"], w)
    d = pj(out); ml = d.get("milestones", []); ms = {m["id"]: m for m in ml}; pos = {m["id"]: i for i, m in enumerate(ml)}
    check("S2: --waitlist: a hand-raiser before the invitations, the waitlist invited first, and its offer first at cart open",
          ok and ms["waitlist_open"]["date"] == "2026-11-15" and pos["waitlist_open"] < pos["invite_1"]
          and ms["waitlist_invite"]["date"] == "2026-11-16" and ms["waitlist_offer"]["date"] == "2026-12-03"
          and pos["waitlist_offer"] < pos["day3"] and d["waitlist"] is True, [(k, ms[k]["date"]) for k in ms if "wait" in k])
    check("X8: --sms adds sms_registration (A2P 10DLC) weeks ahead", ms.get("sms_registration", {}).get("planned") == "2026-10-20"
          or ms.get("sms_registration", {}).get("date") == "2026-10-20" and "A2P 10DLC" in ms["sms_registration"]["detail"]
          and d["sms"] is True, ms.get("sms_registration"))
    check("minor: a call close adds calls_held_48h (+2) and call_noshow_followup (same day, from the first calls)",
          ms.get("calls_held_48h", {}).get("date") == "2026-12-05" and ms.get("call_noshow_followup", {}).get("date") == "2026-12-04"
          and "48 hours" in ms["calls_held_48h"]["detail"], [(k, ms[k]["date"]) for k in ms if "call" in k])

    # X12: holidays by country
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-28", "--days", "2", "--tz", "Europe/London",
                      "--date", "2026-10-17", "--cart-days", "2"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("X12: Europe/London → UK: Day 1 on Mon 28 Dec 2026 is the Boxing Day substitute bank holiday; Christmas and "
          "late December flagged; no Thanksgiving",
          ok and d["country"] == "UK" and ms["day1"].get("holiday") == "Boxing Day (substitute day)"
          and ms["invite_5"].get("holiday") == "Christmas Day" and ms["day2"].get("holiday") == "late December (holiday season)"
          and ms["day2"].get("holiday_soft") and not any("Thanksgiving" in str(m.get("holiday")) for m in ms.values())
          and "UK bank holidays" in d["sources"] and "Holiday soft flags" in d["sources"]
          and "US federal holidays" not in d["sources"], [(k, m.get("holiday")) for k, m in ms.items() if m.get("holiday")])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "Europe/Berlin",
                      "--date", "2026-10-17", "--cart-days", "3"], w)
    d = pj(out)
    check("X12: Europe/Berlin → none: no Thanksgiving or Cyber Monday warnings for a Berlin host",
          ok and d["country"] == "none" and not any(m.get("holiday") for m in d["milestones"])
          and not any("Thanksgiving" in x or "Cyber Monday" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "Europe/Berlin",
                      "--date", "2026-10-17", "--cart-days", "3", "--country", "US"], w)
    check("X12: --country US overrides the zone", pj(out).get("country") == "US"
          and any(m.get("holiday") == "Thanksgiving" for m in pj(out)["milestones"]))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2027-03-31", "--days", "1", "--tz", "Europe/Dublin",
                      "--date", "2026-10-17", "--cart-days", "1"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("X12: Europe/Dublin → IE: St Patrick's Day and Easter Monday (computed: 29 Mar 2027); the Easter weekend is a "
          "soft flag", pj(out).get("country") == "IE" and ms["invite_1"].get("holiday") == "St Patrick's Day"
          and ms["invite_6"].get("holiday") == "Easter Monday" and ms["invite_4"].get("holiday") == "Easter weekend"
          and ms["invite_4"].get("holiday_soft")
          and "Ireland public holidays" in pj(out)["sources"], [(k, m.get("holiday")) for k, m in ms.items() if m.get("holiday")])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2027-04-27", "--days", "1", "--tz", "Australia/Sydney",
                      "--date", "2026-10-17", "--cart-days", "1"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("X12: Australia/Sydney → AU: Anzac Day flagged", pj(out).get("country") == "AU"
          and ms["invite_6"].get("holiday") == "Anzac Day", [(k, m.get("holiday")) for k, m in ms.items() if m.get("holiday")])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2027-07-02", "--days", "1", "--tz", "America/Toronto",
                      "--date", "2026-10-17", "--cart-days", "1"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("X12: America/Toronto → CA: Canada Day flagged, no US Independence Day", pj(out).get("country") == "CA"
          and ms["invite_7"].get("holiday") == "Canada Day" and not any(m.get("holiday") == "Independence Day" for m in ms.values()),
          [(k, m.get("holiday")) for k, m in ms.items() if m.get("holiday")])
    import importlib.util
    spec_ = importlib.util.spec_from_file_location("lp_for_tests", PLAN)
    lp = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(lp)
    import datetime as _dt
    easters = [lp.easter(y) for y in (2026, 2027, 2028)]
    uk = {y: lp.uk_holidays(y) for y in (2026, 2027, 2028)}
    check("X12: Easter computed for 2026–2028 (5 Apr 2026, 28 Mar 2027, 16 Apr 2028); UK Good Friday and Easter Monday follow",
          easters == [_dt.date(2026, 4, 5), _dt.date(2027, 3, 28), _dt.date(2028, 4, 16)]
          and uk[2027][_dt.date(2027, 3, 26)] == "Good Friday" and uk[2028][_dt.date(2028, 4, 17)] == "Easter Monday"
          and uk[2027][_dt.date(2027, 12, 27)] == "Christmas Day (substitute day)"
          and uk[2027][_dt.date(2027, 12, 28)] == "Boxing Day (substitute day)", easters)
    check("X12: country defaults from the zone", [lp.default_country(z) for z in ("America/Chicago", "America/Vancouver",
          "Europe/London", "Europe/Dublin", "Australia/Perth", "Europe/Berlin", "America/Mexico_City", "Pacific/Honolulu")]
          == ["US", "CA", "UK", "IE", "AU", "none", "none", "US"])

    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2027-02-01", "--days", "5", "--tz", "Europe/London",
                      "--partners", "--date", "2026-10-17", "--cart-days", "3", "--out", "planP"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("timeline --partners: recruitment 12 weeks out (partners book months ahead), deals in writing, partner kit",
          ms.get("partner_recruit", {}).get("date") == "2026-11-09" and ms["partner_recruit"]["source"] == "Launch practice: partners"
          and "partner_terms" in ms and "partner_kit" in ms and "Launch practice: partners" in pj(out)["sources"], ms.get("partner_recruit"))
    calp = (w / "planP/calendar.md").read_text()
    check("m18: calendar.md shows empty weeks too", "(no milestones this week)" in calp, calp[:400])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-21", "--days", "3", "--tz", "America/Chicago",
                      "--partners", "--date", "2026-10-17", "--cart-days", "3"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("timeline --partners at 9 weeks: recruitment starts today, flagged compressed and warned",
          ok and ms["partner_recruit"].get("compressed") and ms["partner_recruit"]["date"] == "2026-10-17"
          and any("months ahead" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-25", "--days", "3", "--tz", "America/Chicago",
                      "--partners", "--date", "2026-10-17", "--cart-days", "3"], w, ok_codes=(2,))
    check("timeline --partners refuses under 8 weeks", ok and "at least 56 days" in out, out[-300:])

    # X8: minimum lead 21 days; --rush compresses proportionally, at most 2 list sends a day
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-06", "--days", "3", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--cart-days", "3"], w, ok_codes=(2,))
    check("X8: timeline refuses an event 20 days out without --rush (needs 21)", ok and "20 days away" in out
          and "at least 21 days" in out and "--rush" in out, out[-300:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-07", "--days", "3", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--cart-days", "3"], w)
    d = pj(out); ms = {m["id"]: m for m in d.get("milestones", [])}
    check("X8: 21 days out is accepted; every list email keeps its planned date; earlier tasks move to today",
          ok and not any(m.get("compressed") for m in d["milestones"] if m["kind"] == "send")
          and ms["belief_1"]["date"] == "2026-10-17" and ms["decide"].get("compressed") and d["rush"] is False, d.get("warnings"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-25", "--days", "3", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--rush", "--cart-days", "3"], w)
    d = pj(out); ml = d.get("milestones", []); ms = {m["id"]: m for m in ml}; pos = {m["id"]: i for i, m in enumerate(ml)}
    per_day = {}
    for m in ml:
        if m["kind"] == "send" and m["id"].startswith(("belief_", "invite_", "first_win_emails", "waitlist_open")):
            per_day[m["date"]] = per_day.get(m["date"], 0) + 1
    first_list = min(pos[k] for k in ms if k.startswith(("belief_", "invite_")))
    check("X8: --rush (8 days): compressed proportionally, flagged with the planned date, never more than 2 list sends "
          "a day, the gate before the first list send, the confirmation live from the first invitation",
          ok and ms["invite_1"].get("compressed") and ms["invite_1"]["planned"] == "2026-10-11"
          and "2026-10-17" <= ms["invite_1"]["date"] < "2026-10-25" and max(per_day.values()) <= 2
          and pos["gate_pre_invite"] < first_list and ms["confirmation"]["date"] == ms["invite_1"]["date"]
          and [ms[f"invite_{k}"]["date"] for k in range(1, 8)] == sorted(ms[f"invite_{k}"]["date"] for k in range(1, 8))
          and any(x.startswith("--rush:") and "compressed proportionally" in x for x in d.get("warnings", []))
          and d["rush"] is True, (per_day, d.get("warnings")))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-18", "--days", "1", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--rush", "--no-deadline"], w)
    d = pj(out); ml = d.get("milestones", [])
    per_day = {}
    for m in ml:
        if m["kind"] == "send" and m["id"].startswith(("belief_", "invite_", "first_win_emails")):
            per_day[m["date"]] = per_day.get(m["date"], 0) + 1
    check("X8: --rush with one day left: belief and tool emails are dropped first and listed, 2 list sends a day at most",
          ok and max(per_day.values()) <= 2 and {"belief_1", "belief_2", "belief_3", "first_win_emails"} <= set(d.get("dropped", []))
          and any("left out" in x for x in d.get("warnings", [])) and "invite_1" in {m["id"] for m in ml}
          and "invite_7" in {m["id"] for m in ml}, (per_day, d.get("dropped")))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--paid-event", "--cart-days", "2"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("timeline --paid-event: ticket sales open 21 days out; one-day no-show text offers the replay, not 'tomorrow'",
          ms["invite_1"]["date"] == "2026-10-30" and "day1_night" not in ms and "tomorrow" not in ms["followup_noshow"]["detail"]
          and "replay" in ms["followup_noshow"]["detail"], ms.get("invite_1"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-10", "--days", "1", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--paid-event", "--cart-days", "2"], w, ok_codes=(2,))
    check("X8: a paid event needs 28 days without --rush", ok and "at least 28 days" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--format", "roundtable", "--cart-days", "2"], w)
    ms = {m["id"]: m for m in pj(out).get("milestones", [])}
    check("S4: --format roundtable: one day, personal invitations", ok and ms["invite_1"]["title"].startswith("Personal invitation")
          and "hand-picked" in ms["invite_1"]["detail"], ms.get("invite_1"))
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "2", "--tz", "America/Chicago",
                      "--date", "2026-10-17", "--format", "roundtable", "--cart-days", "2"], w, ok_codes=(2,))
    check("S4: a roundtable is one day", ok and "one-day session" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "Mars/Olympus",
                      "--date", "2026-10-17", "--cart-days", "2"], w, ok_codes=(2,))
    check("timeline refuses an unknown time zone", ok and "IANA" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-11-20", "--days", "1", "--tz", "UTC", "--date", "2026-10-17",
                      "--cart-days", "2", "--country", "FR"], w, ok_codes=(2,))
    check("X12: an unknown --country is refused", ok and "--country must be one of" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-10-01", "--days", "1", "--tz", "UTC", "--date", "2026-10-17",
                      "--rush", "--cart-days", "2"], w, ok_codes=(2,))
    check("timeline refuses a past date even with --rush", ok and "in the past" in out, out[-200:])
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-13-01", "--days", "1", "--tz", "UTC", "--cart-days", "2"], w,
                     ok_codes=(2,))
    check("timeline refuses a bad date", ok and "YYYY-MM-DD" in out, out[-200:])
    (w / "foreign").mkdir(); (w / "foreign/plan.json").write_text('{"something": "else"}')
    ok, out, _ = run([PY, PLAN, "timeline", "--event-date", "2026-12-01", "--days", "3", "--tz", "UTC", "--date", "2026-10-17",
                      "--cart-days", "3", "--out", "foreign"], w, ok_codes=(2,))
    check("--out refuses to overwrite a plan.json that is not ours", ok and "not an Event Launcher plan" in out, out[-200:])
    # a plan for the tracker tests: same event as the ledger (2026-11-10)
    run([PY, PLAN, *base, "--list-size", "5000", "--out", "planT"], w)
    run([PY, PLAN, "timeline", "--event-date", "2026-11-10", "--days", "3", "--tz", "America/Los_Angeles", "--date", "2026-10-17",
         "--rush", "--cart-days", "3", "--out", "planT"], w)
    return w / "planT/plan.json"


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
    d2 = next((x for x in lines if x.startswith("DESCRIPTION:Day 2: proof")), "")
    check("m5: a day's own description is added to the shared one (shared text kept)", "SUMMARY:Cash Flow Bootcamp - Day 3 (close day)" in lines
          and "Day 2: proof\\, then your first sale plan\\n\\nBring your numbers" in d2, d2[:200])
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
    check("M13: a real join URL is fully encoded in the links (its ? and = never end the parameter)",
          "location=https%3A%2F%2Fzoom.us%2Fj%2F1234567890%3Fpwd%3Dabc" in e1["google"]
          and "location=https%3A%2F%2Fzoom.us%2Fj%2F1234567890%3Fpwd%3Dabc" in e1["outlook"], e1["google"][-200:])
    check("build: no warnings for a clean spec inside 07:00–21:00 and without DST", not d.get("warnings"), d.get("warnings"))
    ok, out, _ = run([PY, ICS, "build", "--spec", "event.json", "--out", "event2.ics", "--recipient-tz", "Europe/London",
                      "America/New_York"], w)
    ws = pj(out).get("warnings", [])
    check("m7: build --recipient-tz warns a session outside 07:00–22:00 in a recipient zone (London 22:00–01:00)",
          ok and any("Europe/London" in x and "outside 07:00–22:00" in x for x in ws) and not any("New_York" in x for x in ws), ws)

    # round trip
    ok, out, code = run([PY, ICS, "check", "event.ics"], w)
    c = pj(out)
    check("check: the built file round-trips clean (exit 0)", ok and c.get("ok") and not c.get("problems"), c.get("problems"))
    check("check: round trip gives back the UTC times and the unescaped text",
          [e["start_utc"] for e in c.get("events", [])] == ["2026-11-10T22:00:00Z", "2026-11-11T22:00:00Z", "2026-11-12T22:00:00Z"]
          and c["events"][0]["summary"] == "Cash Flow Bootcamp, Live; 3 Days - Day 1"
          and c["events"][0]["description"].startswith("Bring your numbers, a laptop; no slides.\nDay by day")
          and "🎉" in c["events"][0]["description"], c.get("events", [{}])[0])

    # merge-field join link (M13)
    spec = json.loads((w / "event.json").read_text()); spec["join_url"] = "{{contact.zoom_link}}"
    (w / "merge.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "build", "--spec", "merge.json", "--out", "merge.ics"], w)
    d = pj(out); text = (w / "merge.ics").read_bytes().decode()
    ml = unfold((w / "merge.ics").read_bytes())
    links_all = " ".join(e[k] for e in d.get("events", []) for k in ("google", "outlook", "outlook_365"))
    check("M13: a merge-field join link stays out of the .ics and the add-links; the registration page is the location",
          ok and "{{" not in text and "{{" not in links_all and "contact.zoom" not in links_all
          and "LOCATION:https://example.com/register" in ml and not any(x.startswith("URL:") for x in ml)
          and "location=https%3A%2F%2Fexample.com%2Fregister" in d["events"][0]["google"]
          and "join link is in your confirmation email" in d["events"][0]["google"].replace("%20", " ")
          and any("kept out of the .ics file and the add-links" in x for x in d.get("warnings", [])), d.get("warnings"))
    spec.pop("registration_url")
    (w / "merge2.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "build", "--spec", "merge2.json", "--out", "merge2.ics"], w)
    ml = unfold((w / "merge2.ics").read_bytes())
    check("M13: with no registration_url the location is left empty and the warning asks for one",
          ok and not any(x.startswith("LOCATION") for x in ml) and any("registration_url" in x for x in pj(out).get("warnings", [])))

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

    # reminders (the fixture lists SMS sends explicitly)
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "event.json", "--recipient-tz", "America/Los_Angeles", "America/New_York",
                      "Europe/London"], w)
    r = pj(out); sends = {s["id"]: s for s in r.get("sends", [])}
    check("reminders: day before Day 1, morning of, 15 minutes before and live for each day",
          ok and "day_before" in sends and all(f"day{k}_{x}" in sends for k in (1, 2, 3) for x in ("morning", "15min", "live")),
          sorted(sends))
    check("m8: ids match the timeline (day_before, dayN_morning, dayN_night, dayN_replay, prework)",
          {"prework", "day_before", "day1_night", "day2_night", "day1_replay", "day3_replay"} <= set(sends) and "day3_night" not in sends
          and sends["day1_night"]["local"].startswith("2026-11-10 18:00"), sorted(sends))
    check("m8: a pre-work nudge 3 days before and a replay 2 hours after each day (offer on the close day)",
          sends["prework"]["local"].startswith("2026-11-07 14:00") and sends["day1_replay"]["local"].startswith("2026-11-10 19:00")
          and sends["day3_replay"]["local"].startswith("2026-11-12 19:15") and "offer" in sends["day3_replay"]["purpose"]
          and sends["day1_replay"]["channels"] == ["email"], sends.get("prework"))
    check("reminders: the close-day morning says the offer is today", "offer is today" in sends["day3_morning"]["purpose"]
          and "offer" not in sends["day1_morning"]["purpose"])
    s15 = sends["day1_15min"]
    check("reminders: local and UTC time for each send (15 min before 14:00 PST is 21:45Z)",
          s15["local"].startswith("2026-11-10 13:45 PST") and s15["utc"] == "2026-11-10T21:45:00Z", s15)
    check("reminders: sends sorted by UTC time", [s["utc"] for s in r["sends"]] == sorted(s["utc"] for s in r["sends"]))
    mo = sends["day1_morning"]
    rec = {x["tz"]: x for x in mo["recipients"]}
    check("reminders: an 08:00 Los Angeles SMS is 11:00 New York (fine) and 16:00 London (fine)",
          rec["America/New_York"]["local"].startswith("2026-11-10 11:00") and "sms_flag" not in rec["America/New_York"]
          and "sms_flag" not in rec["Europe/London"], rec)
    check("reminders: 08:00 is flagged caution in the host zone (outside the 09:00–20:00 safe window)",
          "caution" in rec["America/Los_Angeles"].get("sms_flag", ""), rec["America/Los_Angeles"])
    lv = {x["tz"]: x for x in sends["day1_live"]["recipients"]}
    check("m6: a 22:00 London SMS is labelled UK PECR/ICO guidance with no statutory hours, not TCPA",
          "UK PECR/ICO guidance; no statutory hours" in lv["Europe/London"].get("sms_flag", "")
          and "TCPA" not in lv["Europe/London"].get("sms_flag", "") and "UK PECR/ICO" in r.get("sources", {})
          and any("Europe/London" in f and "day1_live" in f for f in r["sms_flags"]), lv["Europe/London"])
    check("reminders: recaps and replays are email only; listed sends are email and SMS",
          sends["day1_night"]["channels"] == ["email"] and sends["day1_15min"]["channels"] == ["email", "sms"]
          and r["sms"] is True and "A2P 10DLC" in r.get("sms_caveat", ""))
    check("m7: reminders warn a session outside 07:00–22:00 in a recipient zone",
          any("Europe/London" in x and "outside 07:00–22:00" in x for x in r.get("warnings", [])), r.get("warnings"))
    check("reminders: warns that GHL 'Set Event Start Date' uses the account time zone",
          any("Set Event Start Date" in x and "account time zone" in x for x in r.get("warnings", []))
          and "GHL help 2026" in r.get("sources", {}) and "TCPA 47 CFR 64.1200" in r.get("sources", {}), r.get("warnings"))
    spec = json.loads((w / "event.json").read_text()); spec["tz"] = "America/New_York"
    (w / "ny.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "ny.json", "--recipient-tz", "America/Los_Angeles"], w)
    mo = {s["id"]: s for s in pj(out)["sends"]}["day1_morning"]["recipients"][0]
    check("reminders: an 08:00 New York SMS is 05:00 in Los Angeles: flagged TCPA outside 08:00–21:00",
          mo["local"].startswith("2026-11-10 05:00") and "outside 08:00–21:00" in mo.get("sms_flag", "") and "TCPA" in mo["sms_flag"], mo)
    spec = json.loads((w / "event.json").read_text()); spec["reminders"].pop("sms")
    (w / "nosms.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "nosms.json", "--recipient-tz", "Europe/London"], w)
    r = pj(out)
    check("M2: no sms key → every send is email only, no SMS flags, no caveat",
          ok and all(s["channels"] == ["email"] for s in r["sends"]) and not r["sms_flags"] and r["sms"] is False
          and "sms_caveat" not in r and "email only" in r.get("channels_note", ""), [s["channels"] for s in r.get("sends", [])][:3])
    spec["reminders"]["sms"] = True
    (w / "smstrue.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "smstrue.json"], w)
    r = pj(out); sends = {s["id"]: s for s in r.get("sends", [])}
    check("M2: \"sms\": true turns on SMS for day-before, morning, 15 min and live, and prints the consent/A2P caveat",
          ok and sends["day_before"]["channels"] == ["email", "sms"] and sends["day1_night"]["channels"] == ["email"]
          and "written consent" in r.get("sms_caveat", ""), r.get("sms_caveat"))
    spec["reminders"]["sms"] = ["day_before", "day1_morning", "day2_15min"]
    (w / "smsids.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "smsids.json"], w)
    sends = {s["id"]: s for s in pj(out).get("sends", [])}
    check("minor: reminders.sms also takes send ids (day1_morning → every morning email)", ok
          and sends["day2_morning"]["channels"] == ["email", "sms"] and sends["day3_15min"]["channels"] == ["email", "sms"]
          and sends["day1_live"]["channels"] == ["email"], out[-300:])
    spec["reminders"]["sms"] = ["day9_banana"]
    (w / "smsbad.json").write_text(json.dumps(spec))
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "smsbad.json"], w, ok_codes=(2,))
    check("reminders.sms refuses an unknown send", ok and "unknown sends" in out)
    ok, out, _ = run([PY, ICS, "reminders", "--spec", "event.json", "--recipient-tz", "Nowhere/City"], w, ok_codes=(2,))
    check("reminders refuses an unknown recipient time zone", ok and "IANA" in out)


# ---------------------------------------------------------------- run_sheet.py

def runsheet_tests(work):
    w = work / "rs"; w.mkdir()
    shutil.copy(FX / "runsheet.json", w / "runsheet.json")
    shutil.copy(FX / "event.json", w / "event.json")
    ok, out, code = run([PY, RUN, "build", "--spec", "runsheet.json", "--out", "run-sheet.md", "--event", "event.json"], w)
    d = pj(out); md = (w / "run-sheet.md").read_text() if (w / "run-sheet.md").exists() else ""
    ch = {c["id"]: c for c in d.get("checks", [])}
    check("run sheet: a clean spec PASSes every check (exit 0)", ok and d.get("result") == "PASS"
          and all(c["ok"] for c in d["checks"]), [c for c in d.get("checks", []) if not c["ok"]])
    check("m17: --event cross-checks days, dates, times and zone (event_match passes)", ch.get("event_match", {}).get("ok"), ch.get("event_match"))
    check("m16: first_build passes when Day 1 builds within 20 minutes; lobby passes", ch["first_build"]["ok"]
          and "minute 5" in ch["first_build"]["detail"] and ch["lobby"]["ok"], ch.get("first_build"))
    check("run sheet: clock-time run-of-show per day, lobby before the start",
          "## Day 1 · Tue 2026-11-10 · 14:00–16:35 America/Los_Angeles (planned end 17:00) · lobby from 13:50" in md
          and "| 13:50 | 10 | lobby |" in md and "| 14:20 | 40 | teach | The one belief" in md and "| 15:40 | 30 | pitch | The offer |" in md, md[:700])
    mod = d["checklists"]["moderator"]
    check("run sheet: moderator gets every link drop with its time",
          "Day 1 14:00 drop workbook: https://example.com/workbook" in mod and "Day 2 15:35 drop workbook: https://example.com/workbook" in mod
          and "Day 3 16:30 drop replay: https://example.com/replay" in mod, mod)
    check("run sheet: the checkout link is dropped as the price is shown and every 10 minutes of the pitch",
          "Day 3 15:40 drop checkout: https://example.com/checkout (as the price is shown)" in mod
          and "Day 3 16:00 drop checkout: https://example.com/checkout (again)" in mod
          and sum("15:40 drop checkout" in x for x in mod) == 1, mod)
    check("m15: backup links are never dropped on a schedule, only if the main link fails",
          not any("drop backup_stream" in x for x in mod) and any("if a link fails: drop the backup backup_stream" in x for x in mod), mod)
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
    d1[1]["title"] = "Welcome"                               # no recording notice on day 1
    d1.insert(4, {"min": 35, "title": "Early VIP offer", "kind": "pitch", "owner": "host"})   # pitch on day 1, 95 min without a break
    bad["days"][1]["segments"][2]["kind"] = "teach"          # no proof on day 2
    bad["days"][2]["segments"][3] = {"min": 5, "title": "Stretch", "kind": "break", "owner": "tech"}   # no checkout test
    bad["days"][2]["segments"].append({"min": 30, "title": "Bonus Q&A", "kind": "qa", "owner": "host", "links": ["nolink"]})
    (w / "bad.json").write_text(json.dumps(bad))
    ok, out, code = run([PY, RUN, "build", "--spec", "bad.json", "--out", "bad.md"], w, ok_codes=(1,))
    d = pj(out); ch = {c["id"]: c for c in d.get("checks", [])}
    check("run sheet: a broken spec FAILs (exit 1) and still writes the sheet", ok and d.get("result") == "FAIL" and (w / "bad.md").exists(), out[-300:])
    check("check: recording notice missing on day 1", not ch["recording_notice"]["ok"] and "day 1" in ch["recording_notice"]["detail"], ch["recording_notice"])
    check("check: over 90 minutes without a break", not ch["breaks_90"]["ok"] and "day 1 from 14:00" in ch["breaks_90"]["detail"], ch["breaks_90"])
    check("check: total length over the planned end", not ch["length_vs_end"]["ok"] and "day 1 runs 190 min, 10 over" in ch["length_vs_end"]["detail"]
          and "day 3 runs 220 min" in ch["length_vs_end"]["detail"], ch["length_vs_end"])
    check("check: a link without a value and a link not in links", not ch["links_have_values"]["ok"]
          and "'workbook' has no real value" in ch["links_have_values"]["detail"] and "'nolink', which is not in links" in ch["links_have_values"]["detail"], ch["links_have_values"])
    check("check: pitch before the final day", not ch["pitch_final_day"]["ok"] and "Early VIP offer" in ch["pitch_final_day"]["detail"], ch["pitch_final_day"])
    check("check: checkout not tested before the close", not ch["checkout_before_close"]["ok"] and "day 3" in ch["checkout_before_close"]["detail"]
          and "day 1" in ch["checkout_before_close"]["detail"], ch["checkout_before_close"])
    check("check: moderator not named", not ch["roles_assigned"]["ok"] and "moderator" in ch["roles_assigned"]["detail"], ch["roles_assigned"])
    check("M22: no backup link on an event with a pitch is a must FAIL", not ch["backup_link"]["ok"] and ch["backup_link"]["level"] == "must"
          and "backup_link" in d["failed"], ch["backup_link"])
    check("check (should): no proof on Day 2 is a warning", not ch["proof_day2"]["ok"] and ch["proof_day2"]["level"] == "should"
          and set(d["warnings"]) == {"proof_day2"}, d.get("warnings"))
    bad["allow_early_pitch"] = True
    bad["days"][0]["checkout_test"] = "14:30"
    (w / "early.json").write_text(json.dumps(bad))
    ok, out, code = run([PY, RUN, "build", "--spec", "early.json", "--out", "early.md"], w, ok_codes=(1,))
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("allow_early_pitch passes the pitch check; checkout_test HH:MM counts as the test on that day",
          ch["pitch_final_day"]["ok"] and "early pitch allowed" in ch["pitch_final_day"]["detail"]
          and "day 1" not in ch["checkout_before_close"]["detail"] and "day 3" in ch["checkout_before_close"]["detail"], ch)

    # M22: placeholders in roles and backup links
    sp = json.loads((FX / "runsheet.json").read_text())
    sp["roles"]["moderator"] = "[member would answer: moderator]"
    sp["links"]["backup_checkout"] = "TODO"
    (w / "ph.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "ph.json", "--out", "ph.md"], w, ok_codes=(1,))
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("M22: a placeholder moderator and a TODO backup link FAIL", ok and not ch["roles_assigned"]["ok"]
          and "moderator" in ch["roles_assigned"]["detail"] and not ch["backup_link"]["ok"] and "backup_checkout" in ch["backup_link"]["detail"]
          and {"roles_assigned", "backup_link"} <= set(pj(out)["failed"]), ch.get("roles_assigned"))
    for v in ("", "TBD", "[name]"):
        sp = json.loads((FX / "runsheet.json").read_text()); sp["roles"]["tech"] = v
        (w / "ph2.json").write_text(json.dumps(sp))
        ok, out, _ = run([PY, RUN, "build", "--spec", "ph2.json", "--out", "ph2.md"], w, ok_codes=(1,))
        check(f"M22: tech {v!r} is not a name", ok and "roles_assigned" in pj(out).get("failed", []), out[-200:])

    # B2: a booking link closes the event
    sp = json.loads((FX / "runsheet.json").read_text())
    sp["links"].pop("checkout")
    sp["links"]["install_call"] = {"url": "https://example.com/book", "kind": "booking"}
    for seg in sp["days"][2]["segments"]:
        if seg.get("links") == ["checkout"]:
            seg["links"] = ["install_call"]
        if seg["title"].startswith("Tech: checkout"):
            seg["title"] = "Tech: booking link check"
    sp["days"][2]["segments"][1]["links"] = ["install_call"]          # named before the pitch
    (w / "call.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "call.json", "--out", "call.md"], w)
    d = pj(out); ch = {c["id"]: c for c in d.get("checks", [])}; mod = d.get("checklists", {}).get("moderator", [])
    check("B2: a link of kind booking satisfies the close checks with a booking-link test", ok and d.get("result") == "PASS"
          and ch["checkout_before_close"]["ok"] and "booking" in ch["checkout_before_close"]["detail"], ch.get("checkout_before_close"))
    check("m15: a booking link named before the pitch is held, then dropped from the pitch onwards",
          any("Day 3 13:00" not in x and "hold install_call: not before the pitch at 15:40" in x for x in mod)
          and "Day 3 15:40 drop install_call: https://example.com/book (as the price is shown)" in mod, mod)
    sp["links"]["install_call"]["kind"] = "nonsense"
    (w / "kindbad.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "kindbad.json", "--out", "kindbad.md"], w, ok_codes=(2,))
    check("run sheet refuses an unknown link kind", ok and "kind must be one of" in out, out[-200:])

    # m16: first build too late; no lobby
    sp = json.loads((FX / "runsheet.json").read_text())
    s1 = sp["days"][0]["segments"]
    s1.pop(0)                                                 # no lobby on day 1
    s1[1], s1[2] = s1[2], s1[1]                               # teach first, build at minute 45
    (w / "late.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "late.json", "--out", "late.md"], w, ok_codes=(1,))
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("m16: no build in Day 1's first 30 minutes FAILs first_build; a missing lobby is a should warning",
          ok and not ch["first_build"]["ok"] and "minute 45" in ch["first_build"]["detail"]
          and not ch["lobby"]["ok"] and ch["lobby"]["level"] == "should" and "day 1" in ch["lobby"]["detail"], ch.get("first_build"))
    sp = json.loads((FX / "runsheet.json").read_text())
    sp["days"][0]["segments"].append({"min": 5, "title": "Late lobby", "kind": "lobby"})
    (w / "lob.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "lob.json", "--out", "lob.md"], w, ok_codes=(2,))
    check("run sheet refuses a lobby segment after the start", ok and "lobby segments come first" in out, out[-200:])

    # m17: event.json mismatch
    ev = json.loads((FX / "event.json").read_text()); ev["days"][1]["start"] = "15:00"; ev["tz"] = "America/Denver"
    (w / "ev2.json").write_text(json.dumps(ev))
    ok, out, _ = run([PY, RUN, "build", "--spec", "runsheet.json", "--out", "x.md", "--event", "ev2.json"], w, ok_codes=(1,))
    ch = {c["id"]: c for c in pj(out).get("checks", [])}
    check("m17: a start time or zone that differs from event.json FAILs event_match", ok and not ch["event_match"]["ok"]
          and "day 2 start 14:00 vs 15:00" in ch["event_match"]["detail"] and "America/Denver" in ch["event_match"]["detail"], ch.get("event_match"))

    bad = json.loads((FX / "runsheet.json").read_text()); bad["days"][0]["segments"][2]["kind"] = "lecture"
    (w / "kind.json").write_text(json.dumps(bad))
    ok, out, _ = run([PY, RUN, "build", "--spec", "kind.json", "--out", "kind.md"], w, ok_codes=(2,))
    check("run sheet refuses an unknown segment kind (exit 2)", ok and "kind must be one of" in out and not (w / "kind.md").exists(), out[-200:])
    bad = json.loads((FX / "runsheet.json").read_text()); bad["days"][0]["segments"][2]["min"] = 0
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
    ok, out, _ = T("slug", "--name", "Cash Flow: Bootcamp!", "--event-date", "2026-11-10")
    check("m31: slug prints the slug and folder without creating anything", ok and pj(out).get("slug") == "2026-11-cash-flow-bootcamp"
          and pj(out)["folder"] == "launches/2026-11-cash-flow-bootcamp" and not (w / "launches").exists(), out[-300:])
    init = ["init", "--name", "Cash Flow Bootcamp", "--format", "bootcamp3", "--days", "3", "--tz", "America/Los_Angeles",
            "--event-date", "2026-11-10", "--goal-buyers", "20", "--goal-cash", "19940", "--date", "2026-10-17"]
    ok, out, _ = T(*init, "--plan", plan_json)
    P = w / "launches/2026-11-cash-flow-bootcamp/tracker.json"
    d = pj(out)
    check("init: creates launches/YYYY-MM-<name>/tracker.json with the plan from plan.json, printing slug and folder",
          ok and P.exists() and d.get("slug") == "2026-11-cash-flow-bootcamp" and d.get("folder") == "launches/2026-11-cash-flow-bootcamp"
          and "typical path" in d.get("plan_source", "") and str(plan_json) in d["plan_source"], out[-400:])
    check("M6/m13: the plan stores needed_for_goal (ceil, as in launch_plan) and expected_from_list separately",
          d["plan"]["needed_for_goal"]["registrants"] == 2204 and d["plan"]["expected_from_list"]["registrants"] == 1000
          and d["plan"]["needed_for_goal"]["list"] == 11017 and d["close_mode"] == "checkout" and "email only" in d["sms"], d.get("plan"))
    data = json.loads(P.read_text())
    check("M6: the plan's first invitation date is kept for pacing (timeline for the same Day 1)",
          data["plan"].get("invites_start") == "2026-10-27" and data["plan"]["expected_registrants_range"]["cautious"] == 500,
          data["plan"].get("invites_start"))
    ok, out, _ = T(*init, codes=(2,))
    check("init: refuses to overwrite an existing ledger", ok and "already exists" in out)
    ok, out, _ = T("log-reg", "600", "--source", "list", "--date", "2026-10-30")
    check("log-reg: logs with a source; the only ledger is found without --slug", ok and pj(out).get("registered_total") == 600, out[-200:])
    T("log-reg", "200", "--source", "partner:Jo Smith", "--date", "2026-11-02")
    ok, out, _ = T("log-reg", "50", "--source", "email:invite-3", "--date", "2026-11-02")
    check("M20: --source email:<id> accepted", ok and pj(out).get("source") == "email:invite-3", out[-200:])
    ok, out, _ = T("log-reg", "150", "--source", "segment:Past buyers", "--date", "2026-11-09")
    check("M20: --source segment:<name> accepted", ok and pj(out).get("source") == "segment:Past buyers", out[-200:])
    ok, out, _ = T("log-reg", "5", "--source", "carrier-pigeon", codes=(2,))
    check("log-reg: refuses an unknown source", ok and "email:ID" in out and "segment:NAME" in out)
    ok, out, _ = T("log-reg", "-5", codes=(2,))
    check("log-reg: refuses a negative count", ok and "0 or more" in out)

    # pace (M6)
    ok, out, _ = T("pace", "--date", "2026-11-03")
    p = pj(out)
    check("M6: pace: 850 by 3 Nov against the Livestorm-shaped curve (50.4% due, 504 expected) is ahead",
          ok and p.get("registered_to_date") == 850 and abs(p["curve_share_to_date"] - .504) < 1e-6
          and p["expected_to_date"]["typical"] == 504 and p["status"] == "ahead" and not p["below_cautious"]
          and "Livestorm" in p["window"]["curve"], p)
    ok, out, _ = T("pace", "--date", "2026-10-29")
    p = pj(out)
    check("M6: pace: nothing logged by 29 Oct is behind and below the cautious curve", ok and p["status"] == "behind"
          and p["below_cautious"] and p["registered_to_date"] == 0, p)
    ok, out, _ = T("pace", "--date", "2026-11-09")
    p = pj(out)
    check("M6: pace: the day before Day 1, 84.7% of registrations are due (15.3% come on the day)",
          abs(p["curve_share_to_date"] - .847) < 1e-6 and p["needed_for_goal_to_date"] == round(2204 * .847, 1), p)

    ok, out, _ = T("log-day", "--day", "1", "--live", "200", "--peak", "170", "--source-count", "partner:Jo Smith=60")
    T("log-day", "--day", "2", "--live", "150"); T("log-day", "--day", "3", "--live", "120", "--peak", "95")
    data = json.loads(P.read_text())
    check("X7: --live is unique attendees (the benchmarks' definition), --peak stored separately, attendees by source "
          "kept; dates default to the event day",
          ok and pj(out).get("counted_as") == "unique attendees (Zoom participant report)"
          and data["days_live"]["1"] == {"live": 200, "peak": 170, "by_source": {"partner:Jo Smith": 60}, "date": "2026-11-10"}
          and data["days_live"]["2"] == {"live": 150, "date": "2026-11-11"} and data["days_live"]["3"]["peak"] == 95
          and data["live_definition"] == "unique", data["days_live"])
    ok, out, _ = T("log-day", "--day", "3", "--live", "120", "--peak", "130", "--date", "2026-11-12")
    check("X7: a peak above the unique count is warned", ok and any("--peak (130) is above the unique" in x
                                                                    for x in pj(out).get("warnings", [])), out[-300:])
    T("log-day", "--day", "3", "--live", "120", "--peak", "95")
    ok, out, _ = T("log-day", "--day", "4", "--live", "10", codes=(2,))
    check("log-day: refuses a day outside the event", ok and "between 1 and 3" in out)
    ok, out, _ = T("log-day", "--day", "1", "--live", "10", "--source-count", "partner:Jo=40", codes=(2,))
    check("S6: attendees by source cannot add up to more than the unique attendees", ok and "more than the 10" in out, out[-200:])
    ok, out, _ = run([PY, TRK, "log-day", "--help"], w)
    check("X7: log-day help says --live is unique attendees and --peak is the peak concurrent count",
          "unique attendees that day" in out and "peak concurrent count" in out, out[-600:])
    ok, out, _ = T("log-close", "--present", "90", "--saw-price", "110")
    check("log-close: present and saw the price", ok and json.loads(P.read_text())["close"]["saw_price"] == 110)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "997", "--count", "5")
    check("log-sale: full pay books price × count", ok and pj(out).get("cash") == 4985 and pj(out).get("booked") == 4985, out[-200:])
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "997", "--count", "1", "--source", "partner:jo smith")
    check("S6: log-sale --source partner:NAME attributes the sale", ok and pj(out).get("source") == "partner:jo smith", out[-200:])
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "150", "--count", "2", "--payment", "plan", codes=(2,))
    check("log-sale: a payment plan without --booked is refused", ok and "--booked TOTAL" in out)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "150", "--count", "2", "--payment", "plan", "--booked", "200", codes=(2,))
    check("log-sale: booked below the cash collected is refused", ok and "less than the cash" in out)
    ok, out, _ = T("log-sale", "--tier", "Core", "--price", "150", "--count", "2", "--payment", "plan", "--booked", "3600")
    check("log-sale: a payment plan books the contract value", ok and pj(out).get("cash") == 300 and pj(out).get("booked") == 3600)
    ok, out, _ = T("log-refund", "--tier", "VIP", "--count", "1", "--amount", "997", codes=(2,))
    check("log-refund: refuses a tier with no sales", ok and "no sales logged" in out)
    ok, out, _ = T("log-refund", "--tier", "Core", "--count", "9", "--amount", "997", codes=(2,))
    check("log-refund: refuses more refunds than sales", ok and "only 8 sold" in out)
    ok, out, _ = T("log-refund", "--tier", "Core", "--count", "1", "--amount", "25000", codes=(2,))
    check("m9: a refund larger than the cash collected for the tier is refused", ok and "more than the cash collected" in out, out[-200:])
    ok, out, _ = T("log-refund", "--tier", "Core", "--count", "1", "--amount", "997", "--source", "partner:Jo Smith")
    check("log-refund: logged (with its partner source)", ok and pj(out).get("amount") == 997 and pj(out).get("source") == "partner:Jo Smith")
    ok, out, _ = T("partner", "--name", "Jo Smith", "--rate", "30%")
    check("S6: partner --name N --rate R stores the commission rate", ok and pj(out).get("commission_rate") == .3
          and json.loads(P.read_text())["partners"]["Jo Smith"]["commission_rate"] == .3, out[-200:])
    ok, out, _ = T("partner", "--name", "Jo Smith", "--commission-rate", "30", codes=(2,))
    check("S6/X3: a bare 30 as a commission rate is refused (30% or 0.3)", ok and '\\"30%\\"' not in out and "0.35" in out, out[-200:])

    # gate (X4: four stages; X10: critical consent items; notes on critical passes)
    ok, out, _ = T("gate")
    g = pj(out); crit = [i["id"] for i in g.get("items", []) if i["critical"]]; st = g.get("stages", {})
    check("X4: gate with no stage shows every item with GO/HOLD per stage, HOLD at first, next stage pre_invite",
          ok and g.get("result") == "HOLD" and g.get("next_stage") == "pre_invite"
          and list(st) == ["pre_invite", "day_before", "close_morning", "cart"] and all(v["result"] == "HOLD" for v in st.values())
          and "Run gate --stage pre_invite" in g.get("say", ""), g.get("stages"))
    pre = ["registration_path_tested", "email_compliance", "partner_disclosure", "partner_copy_true", "single_source",
           "proof_classified", "earnings_claims", "claims_substantiated", "retired_lines", "real_deadlines", "refund_policy",
           "payment_plan_terms", "renewal_terms", "recording_notice", "sms_compliance", "privacy_notice", "first_win_timed"]
    check("X4: stage items: pre_invite (sending, truth, terms, consent), day_before (reminders, night emails, follow-up, "
          "replay release, the money path, moderator, live tech), close_morning (money and follow-up), cart (proof and "
          "chat-quote consents, claims, deadline)",
          st["pre_invite"]["items"] == pre
          and st["day_before"]["items"] == ["reminder_tz", "night_emails", "followup_on", "replay_release", "checkout_tested",
                                            "backup_checkout", "moderator_links", "live_tech_rehearsed"]
          and st["close_morning"]["items"] == ["refund_policy", "payment_plan_terms", "renewal_terms", "followup_on",
                                               "checkout_tested", "backup_checkout", "chargeback_ready"]
          and st["cart"]["items"] == ["proof_classified", "earnings_claims", "claims_substantiated", "real_deadlines",
                                      "testimonial_permission", "refund_commissions"], {k: v["items"] for k, v in st.items()})
    check("X10: recording_notice, replay_release and testimonial_permission are critical; sms_compliance is na (email "
          "only) and not critical when no SMS is planned; 21 critical items in a checkout close",
          {"recording_notice", "replay_release", "testimonial_permission", "renewal_terms", "retired_lines",
           "claims_substantiated", "registration_path_tested"} <= set(crit) and "sms_compliance" not in crit
          and len(crit) == 21 and next(i for i in g["items"] if i["id"] == "sms_compliance")["status"] == "na"
          and "email only" in g["sms"] and "booking_tested" not in crit, crit)
    check("gate: 28 items in a checkout close, 7 advisory", len(g["items"]) == 28
          and {i["id"] for i in g["items"] if not i["critical"]} == {"sms_compliance", "privacy_notice", "moderator_links",
          "first_win_timed", "live_tech_rehearsed", "refund_commissions", "chargeback_ready"}
          and g.get("close_morning_items") == st["close_morning"]["items"], [i["id"] for i in g["items"]])
    gate_md = (SK / "references/launch-gate.md").read_text() if (SK / "references/launch-gate.md").exists() else ""
    crit_md, adv_md = (gate_md.split("## Advisory items") + [""])[:2] if "## Advisory items" in gate_md else (gate_md, "")
    always = {i["id"] for i in g["items"] if i["critical"]} | {"booking_tested", "backup_booking"}
    wrong = [x for x in always if f"[{x}]" not in crit_md] + \
            [i["id"] for i in g["items"] if not i["critical"] and i["id"] != "sms_compliance" and f"[{i['id']}]" not in adv_md]
    check("gate: launch-gate.md names every item in the section matching its critical / advisory status "
          "(sms_compliance conditionally critical, under Critical)", "## Critical items" in gate_md and not wrong
          and "[sms_compliance]" in crit_md and "SMS only with written consent" in crit_md
          and all(f"**{x}**" in gate_md for x in ("pre_invite", "day_before", "close_morning", "cart")), wrong)
    ok, out, _ = T("gate", "--stage", "pre_invite")
    g = pj(out)
    check("X4: gate --stage pre_invite shows and judges only that stage's items", ok and g.get("stage") == "pre_invite"
          and [i["id"] for i in g["items"]] == pre and g["result"] == "HOLD" and len(g["hold"]) == 14, g.get("hold"))
    ok, out, _ = T("gate", "--set", "partner_disclosure", "na", codes=(2,))
    check("gate: na on a critical item needs a note", ok and "needs a note" in out)
    ok, out, _ = T("gate", "--set", "email_compliance", "pass", codes=(2,))
    check("X10: pass on a critical item needs a note (what was tested, by whom, on what device)", ok
          and "pass needs a note" in out and json.loads(P.read_text())["gate"]["email_compliance"]["status"] == "open")
    ok, out, _ = T("gate", "--set", "teleport_ready", "pass", codes=(2,))
    check("gate: refuses an unknown item", ok and "unknown gate item" in out)
    ok, out, _ = T("gate", "--set", "checkout_tested", "maybe", codes=(2,))
    check("M5: refuses an unknown status (pass, fail, na or open)", ok and "pass, fail, na or open" in out)
    ok, out, _ = T("gate", "--set", "booking_tested", "pass", "x", codes=(2,))
    check("B2: a call-close item is refused on a checkout ledger", ok and "not a gate item for a checkout close" in out)
    ok, out, _ = T("gate", "--stage", "cart", "--set", "reminder_tz", "pass", "x", codes=(2,))
    check("X4: an item cannot be recorded at a stage that does not judge it", ok and "not judged at cart" in out, out[-200:])
    ok, out, _ = T("gate", "--set", "refund_policy", "pass", "a", "--set", "email_compliance", "pass", "--note", "x", codes=(2,))
    check("M5: one --note for two items is refused (each item gets its own note)", ok and "exactly one --set" in out)
    sets = []
    for c in pre:
        if c not in ("partner_disclosure", "renewal_terms", "sms_compliance", "privacy_notice", "first_win_timed",
                     "proof_classified"):
            sets += ["--set", c, "pass", f"{c} checked by Dana on her phone"]
    ok, out, _ = T("gate", "--stage", "pre_invite", *sets, "--set", "proof_classified", "fail", "two stories lack consent",
                   "--set", "renewal_terms", "na", "one-off price; nothing renews", "--set", "first_win_timed", "fail",
                   "--date", "2026-10-25")
    g = pj(out); items = {i["id"]: i for i in g.get("items", [])}
    check("M5/X4: per-item notes, stage and tested_at are stored and shown; one critical fail still HOLDs, naming it",
          g.get("result") == "HOLD" and len(g["hold"]) == 2 and g["hold"][0].startswith("partner_disclosure")
          and any(x.startswith("proof_classified") and "two stories lack consent" in x and "tested 2026-10-25" in x
                  and "at pre_invite" in x for x in g["hold"])
          and items["renewal_terms"]["note"] == "one-off price; nothing renews" and items["refund_policy"]["recorded_stage"] == "pre_invite"
          and items["refund_policy"]["tested_at"] == "2026-10-25" and any(x.startswith("first_win_timed") for x in g.get("advisory_open", [])),
          g.get("hold"))
    ok, out, _ = T("gate", "--set", "proof_classified", "pass", "consents on file for every story",
                   "--set", "partner_disclosure", "na", "no partners this launch", "--date", "2026-10-25")
    g = pj(out)
    check("X4: GO at pre_invite when every critical item passes (or is na with a note); advisory fails do not block; "
          "--set without --stage records the item's first open stage",
          g.get("stages", {}).get("pre_invite", {}).get("result") == "GO" and g["next_stage"] == "day_before"
          and g["set"] == ["proof_classified (pre_invite)", "partner_disclosure (pre_invite)"]
          and "first_win_timed" in g["stages"]["pre_invite"].get("advisory_open", []), g.get("stages", {}).get("pre_invite"))
    ok, out, _ = T("gate", "--reset", "single_source")
    g = pj(out)
    check("M5: --reset puts an item back to open (and pre_invite back to HOLD)", ok and g["stages"]["pre_invite"]["result"] == "HOLD"
          and g["stages"]["pre_invite"]["hold"] == ["single_source"], g.get("stages", {}).get("pre_invite"))
    T("gate", "--set", "single_source", "pass", "close.md is the one source", "--date", "2026-10-25")
    sets = []
    for c in ("reminder_tz", "followup_on", "checkout_tested", "backup_checkout"):
        sets += ["--set", c, "pass", f"{c}: dry run with a test contact"]
    ok, out, _ = T("gate", "--stage", "day_before", *sets, "--set", "night_emails", "pass", "both written and scheduled",
                   "--date", "2026-11-09")
    g = pj(out)
    check("X4/X10: day_before HOLDs on replay_release (critical: people on camera agreed, or are cut)",
          g.get("result") == "HOLD" and [x.split(":")[0] for x in g["hold"]] == ["replay_release"], g.get("hold"))
    ok, out, _ = T("gate", "--stage", "day_before", "--set", "replay_release", "pass", "registration terms + on-air notice; "
                   "blur anyone who objects", "--date", "2026-11-09")
    check("X4: day_before GO", pj(out).get("result") == "GO", pj(out).get("hold"))
    ok, out, _ = T("gate", "--stage", "close_morning", "--date", "2026-11-12")
    cm = pj(out)
    check("M5/X4: gate --stage close_morning: passes from earlier stages or days do not count on the close morning",
          ok and cm.get("result") == "HOLD" and cm["close_morning"] == "2026-11-12"
          and any(x.startswith("checkout_tested") and "re-check it at close_morning" in x for x in cm["hold"])
          and any(x.startswith("refund_policy") for x in cm["hold"])
          and not any(x.startswith("renewal_terms") for x in cm["hold"])
          and [i["id"] for i in cm["items"]] == ["refund_policy", "payment_plan_terms", "renewal_terms", "followup_on",
                                                 "checkout_tested", "backup_checkout", "chargeback_ready"], cm.get("hold"))
    sets = []
    for c in ("checkout_tested", "backup_checkout", "refund_policy", "payment_plan_terms", "followup_on"):
        sets += ["--set", c, "pass", f"{c} re-tested on a phone this morning"]
    ok, out, _ = T("gate", "--close-morning", *sets, "--date", "2026-11-11")
    ok2, out2, _ = T("gate", "--close-morning", "--date", "2026-11-12")
    check("M5: a close_morning pass dated the day before does not count", pj(out2).get("result") == "HOLD"
          and any("not on the close morning (2026-11-12)" in x for x in pj(out2).get("hold", [])), pj(out2).get("hold"))
    ok, out, _ = T("gate", "--close-morning", *sets, "--date", "2026-11-12")
    cm = pj(out)
    check("M5: GO for the close once each money/follow-up item passed that morning (na counts); --close-morning is "
          "--stage close_morning", ok and cm.get("stage") == "close_morning" and cm.get("result") == "GO"
          and all(i["ok_for_stage"] for i in cm["items"] if i["critical"]), cm.get("hold"))
    ok, out, _ = T("gate", "--stage", "cart", "--date", "2026-11-13")
    ct = pj(out)
    check("X4: the cart stage re-checks proof, claims and the deadline, and needs chat-quote consent (testimonial_permission)",
          ct.get("result") == "HOLD" and [x.split(":")[0] for x in ct["hold"]] == ["proof_classified", "earnings_claims",
          "claims_substantiated", "real_deadlines", "testimonial_permission"]
          and "re-check it at cart" in ct["hold"][0], ct.get("hold"))
    sets = []
    for c in ("proof_classified", "earnings_claims", "claims_substantiated", "real_deadlines", "testimonial_permission"):
        sets += ["--set", c, "pass", f"{c}: every cart email checked"]
    ok, out, _ = T("gate", "--stage", "cart", *sets, "--date", "2026-11-13")
    ok, out, _ = T("gate", "--date", "2026-11-13")
    g = pj(out)
    check("X4: every stage GO → gate GO; entries keep a short history", g.get("result") == "GO"
          and all(v["result"] == "GO" for v in g["stages"].values())
          and json.loads(P.read_text())["gate"]["proof_classified"]["history"][-1]["stage"] == "pre_invite", g.get("stages"))
    ok, out, _ = T("gate", "--set", "privacy_notice", "na")
    check("gate: an advisory item may be na without a note", ok and pj(out).get("result") == "GO")

    # report
    ok, out, _ = T("report")
    r = pj(out); f = {x["stage"]: x for x in r.get("funnel", [])}
    check("report: funnel from registered to buyers with expected and needed columns",
          ok and f["Registered"]["actual"] == 1000 and f["Registered"]["expected"] == 1000 and f["Registered"]["needed_for_goal"] == 2204
          and f["Live Day 3"]["actual"] == 120 and f["Saw the price"]["actual"] == 110 and f["Buyers"]["actual"] == 8
          and [x["stage"] for x in r["funnel"]] == ["Registered", "Live Day 1", "Live Day 2", "Live Day 3", "Present at the close",
                                                    "Saw the price", "Buyers"] and r["judged_against"] == "expected from the list", r.get("funnel"))
    check("X7: the report names its live definition (unique attendees) and keeps the peak apart",
          r["live_definition"] == "unique attendees (Zoom participant report)" and r["peak_concurrent"] == {"1": 170, "3": 95},
          r.get("peak_concurrent"))
    check("report: day-over-day retention (unique attendees)", [x["actual"] for x in r["retention"]] == [.75, .8]
          and r["retention"][0]["plan"] == .7, r.get("retention"))
    check("report: conversion of those who saw the price and of registrants", r["conversion"]["of_saw_price"] == round(8 / 110, 4)
          and r["conversion"]["of_registrants"] == .008 and r["conversion"]["label"] == "of those who saw the price", r.get("conversion"))
    check("report: cash vs booked, net of refunds", r["money"] == {"cash": 6282.0, "booked": 9582.0, "refunded": 997.0,
                                                                   "booked_cancelled": 0.0, "net_cash": 5285.0, "net_booked": 8585.0,
                                                                   "average_sale": 1197.75}, r.get("money"))
    check("report: refunds and revenue per registrant", r["refunds"]["count"] == 1 and r["refunds"]["rate"] == .125
          and abs(r["per_registrant"]["booked"] - 8.585) < .006 and abs(r["per_registrant"]["cash"] - 5.285) < .006,
          r.get("per_registrant"))
    pt = r.get("partners", {})
    check("S6: the report has a partner table: registrations, Day-1 attendees, buyers, cash, refunds, net cash and the "
          "commission due on net cash (names matched case-insensitively)",
          list(pt) == ["Jo Smith"] and pt["Jo Smith"] == {"registrations": 200, "attendees_day1": 60, "buyers": 1, "cash": 997.0,
          "refunds": 1, "refunded": 997.0, "net_cash": 0.0, "show_up": .3, "commission_rate": .3, "commission_due": 0.0}, pt)
    lk = [x["stage"] for x in r["leaks"]]
    check("M6: leaks are ranked against the expected path, so registrations (on the expected 1,000) are not leak #1",
          lk == ["show_up", "conversion"] and r["leaks"][0]["buyers_lost"] > r["leaks"][1]["buyers_lost"]
          and all(x["fix"] for x in r["leaks"]) and "registration" not in lk, r.get("leaks"))
    gg = r.get("goal_gap", {})
    check("M6: the goal shortfall is shown separately (9.1 expected of 20)", gg.get("expected_buyers_from_list") == 9.1
          and gg["gap_the_plan_showed"] == 10.9 and gg["actual_buyers_net"] == 7, gg)
    check("m11: what to protect lists stages that beat plan, never an assumption-only stage (saw the price)",
          {x["stage"] for x in r["protect"]} == {"retention_1_2", "retention_2_3", "stay_to_close"} and r["all_leaks"] == 2
          and all(x["keep"] for x in r["protect"]), r.get("protect"))
    bm = {b["stage"]: b for b in r["benchmarks"]}
    check("report: benchmark ranges with sources (Day-1 show-up 20% is below the 30–45% range)",
          bm["show_up"]["status"] == "below range" and bm["show_up"]["range"] == [.30, .45]
          and "Build Room planning range 2026" in bm["show_up"]["source"]
          and bm["conversion"]["status"] == "in range" and "Scale For Impact 2026" in r["sources"], bm.get("show_up"))
    check("M20: registrations by source and by source type", r["registrations_by_source"] == {"list": 600, "partner:Jo Smith": 200,
          "email:invite-3": 50, "segment:Past buyers": 150} and r["registrations_by_source_type"] == {"list": 600, "partner": 200,
          "email": 50, "segment": 150}, r.get("registrations_by_source"))
    ok, out, _ = T("report", "--md")
    dn = w / "launches/2026-11-cash-flow-bootcamp/debrief-numbers.md"
    md = dn.read_text() if dn.exists() else ""
    check("m10/X9: report --md writes debrief-numbers.md in the launch folder by default, between start and end markers",
          ok and pj(out).get("written") == str(dn.relative_to(w))
          and "## Results" in md and "## Leaks" in md and "1. **Day-1 show-up**" in md and "## What to protect" in md and "## Sources" in md
          and "Goal gap:" in md and md.startswith("<!-- written by launch_tracker.py report")
          and md.rstrip().endswith("-->") and "| Jo Smith | 200 | 60 | 1 |" in md and "Live counts are unique attendees" in md, md[:400])
    check("m11: lessons are the member's own, not the leak fixes repeated", "Next time:" not in md
          and "(add the member's own lessons" in md, md.split("## Lessons")[-1][:200])
    (w / "launches/2026-11-cash-flow-bootcamp/debrief.md").write_text("# Debrief\n\n## Feedback as a gift\n\nhand-written\n")
    for target, extra in (("launches/2026-11-cash-flow-bootcamp/debrief.md", []), ("launches/2026-11-cash-flow-bootcamp/debrief.md", ["--force"]),
                          ("Debrief.md", ["--force"])):
        ok, out, _ = T("report", "--md", target, *extra, codes=(2,))
        check(f"X9: report --md never writes a file named debrief.md ({target} {' '.join(extra)})".rstrip(),
              ok and "never writes debrief.md" in out
              and "hand-written" in (w / "launches/2026-11-cash-flow-bootcamp/debrief.md").read_text(), out[-200:])
    (w / "notes.md").write_text("# Notes\n\nhand-written\n")
    ok, out, _ = T("report", "--md", "notes.md", codes=(2,))
    check("m10: report --md refuses to overwrite a file the report did not write", ok and "not written by the report" in out
          and "hand-written" in (w / "notes.md").read_text())
    ok, out, _ = T("report", "--md")
    check("m10: report --md rewrites its own file", ok)
    dn.write_text(dn.read_text() + "\n## Feedback as a gift\n\nadded by the member\n")
    ok, out, _ = T("report", "--md", codes=(2,))
    check("X9: text added after the report's end marker stops a re-run (the member's words are kept)",
          ok and "text added after the report's end marker" in out and "added by the member" in dn.read_text(), out[-200:])
    ok, out, _ = T("report", "--md", "--force")
    check("m10: --force overwrites a file that is not debrief.md", ok and "added by the member" not in dn.read_text())
    ok, out, _ = T("report", "--md", "notes.md", "--force")
    check("m10: --force overwrites another hand-written file", ok and "hand-written" not in (w / "notes.md").read_text())

    # m12: report benchmarks use the plan's member history
    wh = work / "trkh"; wh.mkdir()
    run([PY, PLAN, "math", "--goal-buyers", "20", "--price", "997", "--format", "bootcamp3", "--list-size", "5000",
         "--history-showup", "39%", "--out", "ph"], wh)
    run([PY, TRK, "init", "--name", "Hist Camp", "--format", "bootcamp3", "--days", "3", "--tz", "UTC", "--event-date", "2026-11-10",
         "--goal-buyers", "20", "--goal-cash", "19940", "--plan", "ph/plan.json"], wh)
    run([PY, TRK, "log-reg", "1000"], wh); run([PY, TRK, "log-day", "--day", "1", "--live", "350"], wh)
    r = pj(run([PY, TRK, "report"], wh)[1])
    bm = {b["stage"]: b for b in r.get("benchmarks", [])}
    check("m12: report benchmarks use the plan's member history (show-up range 31.2–46.8%, not 25–39%)",
          bm.get("show_up", {}).get("range") == [.312, .468] and bm["show_up"]["source"] == "Member history"
          and bm["show_up"]["status"] == "in range" and r["benchmarks_from_history"] == ["show_up"], bm.get("show_up"))

    # leak ranking moves with the data: a conversion collapse becomes the top leak
    w2 = work / "trk2"; w2.mkdir()
    T2 = lambda *a, codes=(0,): run([PY, TRK, *a], w2, ok_codes=codes)
    ok, out, _ = T2("init", "--name", "Pricing Webinar", "--format", "webinar", "--days", "1", "--tz", "Europe/London",
                    "--event-date", "2026-11-20", "--goal-buyers", "10", "--goal-cash", "9970", "--date", "2026-10-17")
    check("M6: init without a list size warns that leaks are judged against the goal", any("no list size" in x for x in pj(out).get("warnings", [])))
    T2("log-reg", "500"); T2("log-day", "--day", "1", "--live", "200"); T2("log-close", "--present", "160", "--saw-price", "200")
    T2("log-sale", "--tier", "Core", "--price", "997", "--count", "1")
    ok, out, _ = T2("report")
    r = pj(out)
    check("leaks: a conversion collapse ranks first; benchmarks-only plan when no plan.json",
          r["leaks"][0]["stage"] == "conversion" and r["plan_source"].startswith("Build Room benchmarks")
          and r["leaks"][0]["buyers_lost"] > 10 and r["judged_against"] == "needed for the goal", r.get("leaks"))
    g = pj(T2("gate")[1])
    check("gate: night_emails is na for a single-day event", next(i for i in g["items"] if i["id"] == "night_emails")["status"] == "na")
    ok, out, _ = run([PY, TRK, "init", "--name", "Second", "--format", "webinar", "--days", "1", "--tz", "UTC", "--event-date", "2026-12-01",
                      "--goal-buyers", "1", "--goal-cash", "100", "--test"], w2)
    check("M23: init --test marks the ledger as test data", ok and pj(out).get("test") is True
          and json.loads((w2 / "launches/2026-12-second/tracker.json").read_text())["test"] is True, out[-200:])
    ok, out, _ = T2("report", "--date", "2026-11-01")
    lg = pj(out).get("ledger", {})
    check("minor: with two ledgers and no --slug, the nearest upcoming event's ledger is used, and the output says which",
          ok and pj(out).get("slug") == "2026-11-pricing-webinar" and lg.get("used") == "2026-11-pricing-webinar"
          and "nearest upcoming" in lg.get("why", "") and lg.get("others") == ["2026-12-second"] and "--slug" in lg["note"], lg)
    ok, out, _ = T2("report", "--date", "2026-11-25")
    check("minor: between the two, the next one (2026-12-second) is the nearest upcoming",
          ok and pj(out).get("ledger", {}).get("used") == "2026-12-second", pj(out).get("ledger"))
    ok, out, _ = T2("report", "--date", "2027-01-15")
    check("minor: after both, the most recent past event's ledger is used",
          ok and pj(out).get("ledger", {}).get("used") == "2026-12-second"
          and "most recent past" in pj(out)["ledger"]["why"], pj(out).get("ledger"))
    ok, out, _ = T2("report", "--slug", "2026-12-second", "--md")
    tm = (w2 / "launches/2026-12-second/debrief-numbers.md").read_text()
    check("M23: a test ledger's report says TEST", ok and pj(out).get("test") is True and "# TEST · Second" in tm
          and "TEST / synthetic data" in tm, tm[:200])

    # B2: a call close in the tracker
    w4 = work / "trk4"; w4.mkdir()
    T4 = lambda *a, codes=(0,): run([PY, TRK, *a], w4, ok_codes=codes)
    ok, out, _ = T4("init", "--name", "Install Camp", "--format", "bootcamp3", "--days", "3", "--tz", "America/New_York",
                    "--event-date", "2026-12-08", "--goal-buyers", "5", "--goal-cash", "50000", "--close", "call", "--list-size", "2000")
    d = pj(out)
    check("B2: init --close call stores the close mode and an expected call path", ok and d["close_mode"] == "call"
          and "calls_booked" in d["plan"]["expected_from_list"], d.get("plan"))
    g = pj(T4("gate")[1]); ids = [i["id"] for i in g.get("items", [])]
    check("B2: a call close gates the booking path and a backup booking link instead of the checkout",
          "booking_tested" in ids and "backup_booking" in ids and "checkout_tested" not in ids and "backup_checkout" not in ids
          and g["close_morning_items"] == ["refund_policy", "payment_plan_terms", "renewal_terms", "followup_on",
                                           "booking_tested", "backup_booking", "chargeback_ready"]
          and g["stages"]["day_before"]["items"][4:6] == ["booking_tested", "backup_booking"]
          and "booking" in next(i for i in g["items"] if i["id"] == "booking_tested")["check"].lower(), ids)
    T4("log-reg", "400"); T4("log-day", "--day", "1", "--live", "130"); T4("log-day", "--day", "2", "--live", "90")
    T4("log-day", "--day", "3", "--live", "65"); T4("log-close", "--present", "40", "--saw-price", "42")
    ok, out, _ = T4("log-calls", "--booked", "6", "--held", "5", "--closed", "1", "--value", "10000", "--date", "2026-12-12")
    check("B2: log-calls records booked, held and closed with the value closed", ok and pj(out)["totals"] == {"booked": 6, "held": 5, "closed": 1}
          and pj(out)["show_rate"] == .8333 and pj(out)["close_rate"] == .2, out[-300:])
    ok, out, _ = T4("log-calls", "--booked", "0", "--held", "3", "--closed", "0", codes=(2,))
    check("B2: log-calls refuses more calls held than booked", ok and "more than calls booked" in out)
    ok, out, _ = T4("log-calls", "--booked", "1", "--held", "1", "--closed", "1", codes=(2,))
    check("B2: log-calls needs --value when deals closed", ok and "--value X is needed" in out)
    ok, out, _ = T4("log-sale", "--tier", "Call close", "--price", "10000", "--count", "1", "--via", "call")
    check("B2: log-sale --via call adds cash only", ok and pj(out)["buyers_total"] == 1 and "cash only" in pj(out).get("note", ""))
    r = pj(T4("report")[1]); f = {x["stage"]: x for x in r.get("funnel", [])}
    check("B2: the report shows calls booked, held and closed in the funnel and as rates",
          f["Calls booked"]["actual"] == 6 and f["Calls held"]["actual"] == 5 and f["Calls closed"]["actual"] == 1
          and f["Buyers"]["actual"] == 1 and r["calls"]["show_rate"] == .8333 and r["calls"]["close_rate"] == .2
          and r["calls"]["booked_of_saw_price"] == round(6 / 42, 4) and r["money"]["cash"] == 10000 and r["money"]["booked"] == 10000, r.get("calls"))
    stages = {x["stage"] for x in r["leaks"]} | {x["stage"] for x in r["protect"]} | {b["stage"] for b in r["benchmarks"]}
    check("B2: call stages are judged in leaks/protect and benchmarks", {"booked", "held", "closed"} & stages
          and any(b["stage"] == "closed" and b["source"] == "Webinar call rates (vendor, weak)" for b in r["benchmarks"]), sorted(stages))
    ok, out, _ = T4("log-refund", "--tier", "Call close", "--count", "1", "--amount", "10000")
    check("m9: a call deal's cash can be refunded up to what was collected", ok, out[-200:])

    # import-csv: counts only, merge, never negative (M4)
    w3 = work / "trk3"; w3.mkdir()
    T3 = lambda *a, codes=(0,): run([PY, TRK, *a], w3, ok_codes=codes)
    T3("init", "--name", "CSV Camp", "--format", "bootcamp3", "--days", "3", "--tz", "UTC", "--event-date", "2026-11-10",
       "--goal-buyers", "5", "--goal-cash", "5000")
    T3("log-reg", "2"); T3("log-day", "--day", "1", "--live", "4", "--peak", "3")
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "registered=bootcamp-registered,day1=bootcamp-day1",
                    "day2=bootcamp-day2,day3=bootcamp-day3", "present=bootcamp-present,saw_price=bootcamp-saw-price")
    d = pj(out)
    LP = w3 / "launches/2026-11-csv-camp/tracker.json"
    check("import-csv: counts rows per tag (case-insensitive, comma or semicolon separated)", ok and d.get("counts") == {
        "registered": 5, "day1": 4, "day2": 2, "day3": 1, "present": 1, "saw_price": 2} and d["rows"] == 6, d.get("counts"))
    data = json.loads(LP.read_text())
    text = LP.read_text()
    check("M4/X7: a top-up adds one positive import entry; equal counts change nothing; a day's other fields are kept "
          "(the imported day count is unique contacts, the same field as log-day --live)",
          [x["n"] for x in data["registrations"]] == [2, 3] and data["days_live"]["1"]["peak"] == 3
          and data["days_live"]["1"]["live"] == 4
          and data["days_live"]["2"]["live"] == 2 and data["close"] == {"present": 1, "saw_price": 2, "date": data["close"]["date"]})
    check("M4: a before/after table is printed", "| registered | 2 | 5 |" in d.get("table", "") and "| day2 | – | 2 |" in d["table"], d.get("table"))
    check("import-csv: no names, emails or phone numbers stored", not any(x in text for x in ("Alice", "Zephyrine", "alice@", "+1555", "Mossbright")))
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "registered=bootcamp-day3,day1=bootcamp-day3", codes=(2,))
    check("M4: a partial export that would lower logged counts is refused, nothing changed",
          ok and "would overwrite logged numbers" in out and "registered: logged 5, export 1" in out
          and json.loads(LP.read_text()) == data, out[-300:])
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "present=*", "--replace")
    after = json.loads(LP.read_text())
    check("M4: --replace overwrites only the mapped field (present), saw_price kept",
          ok and after["close"]["present"] == 6 and after["close"]["saw_price"] == 2, after["close"])
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "registered=bootcamp-day3", "--replace")
    after = json.loads(LP.read_text())
    check("M4: --replace never writes a negative delta: registrations become one import entry",
          ok and after["registrations"][-1]["n"] == 1 and all(x["n"] >= 0 for x in after["registrations"])
          and sum(x["n"] for x in after["registrations"]) == 1, after["registrations"])
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "registered=*")
    check("import-csv: * counts every row", pj(out).get("counts") == {"registered": 6})
    ok, out, _ = T3("import-csv", FX / "crm_export.csv", "--map", "buyers=paid", codes=(2,))
    check("import-csv: refuses an unknown field", ok and "not one of" in out)
    (w3 / "notags.csv").write_text("Name,Email\nA,a@x.com\n")
    ok, out, _ = T3("import-csv", "notags.csv", "--map", "registered=x", codes=(2,))
    check("import-csv: refuses an export without a tags column", ok and "no tags column" in out)
    return w, w2


# ---------------------------------------------------------------- obsidian

def obsidian_tests(work, w, w2):
    T = lambda *a, codes=(0,): run([PY, TRK, *a], w, ok_codes=codes)
    ok, out, _ = T("obsidian", "--vault", "novault", codes=(2,))
    check("obsidian: refuses a vault path that does not exist", ok and "no vault folder" in out)
    (w / "plainfolder").mkdir()
    ok, out, _ = T("obsidian", "--vault", "plainfolder", codes=(2,))
    check("obsidian: refuses a folder without .obsidian", ok and "no .obsidian folder" in out and not (w / "plainfolder/launches").exists())
    ok, out, _ = T("obsidian", "--vault", "plainfolder", "--no-obsidian-check")
    check("obsidian: --no-obsidian-check writes with a warning", ok and any(".obsidian" in x for x in pj(out).get("warnings", []))
          and (w / "plainfolder/launches/2026-11-cash-flow-bootcamp.md").exists())
    V = w / "vault"; (V / ".obsidian").mkdir(parents=True); (V / "launches").mkdir()
    (V / "launches/2026-07-old-camp.md").write_text("---\ntitle: \"Old camp: July\"\ntype: launch\ndate: 2026-07-27\nformat: bootcamp3\n"
                                                   "tags: [launch, event]\nstatus: final\n---\n# Old camp\n\n## Results\n\n- 212 registered\n\n"
                                                   "## Lessons\n\n- Schedule the Day-1-night email\n\n## Other\n\nx\n")
    ok, out, _ = T("obsidian", "--vault", "vault", "--lesson", "Book partner podcasts a month earlier")
    note = V / "launches/2026-11-cash-flow-bootcamp.md"
    text = note.read_text() if note.exists() else ""
    check("obsidian: writes launches/YYYY-MM-<slug>.md with light frontmatter", ok and text.startswith(
        "---\ntitle: Cash Flow Bootcamp launch debrief\ntype: launch\ndate: 2026-11-10\nformat: bootcamp3\nclose: checkout\n"
        "tags: [launch, event]\nstatus: debriefed\n"), text[:300])
    check("obsidian: the note has Results, Leaks, Lessons (with --lesson) and What to protect, and names the launch folder",
          all(h in text for h in ("## Results", "## Leaks", "## Lessons", "## What to protect")) and "- Book partner podcasts a month earlier" in text
          and "Launch folder: `" in text and "launches/2026-11-cash-flow-bootcamp` (outside the vault)" in text, text[:900])
    r = pj(T("report")[1])
    allowed = {f"${x:,.0f}" for x in list(r["money"].values()) + [r["goal"]["cash"]] + list(r["per_registrant"].values()) if x is not None}
    dollars = set(re.findall(r"\$[\d,]+(?:\.\d+)?", text))
    check("obsidian: every money figure in the member's note comes from this ledger (no founder figures)",
          dollars and dollars <= allowed | {"$2,000", "$97", "$497", "$500", "$1,500", "$100", "$27", "$1"}, dollars - allowed)
    idx = (V / "launches/_index.md").read_text()
    check("m14: _index.md has one line for the launch and back-fills older launch notes",
          idx.startswith("# Launches") and idx.count("[[2026-11-cash-flow-bootcamp]]") == 1
          and "1,000 registered · 7 buyers (net of refunds) · $5,285 cash" in idx
          and "[[2026-07-old-camp]] · Old camp: July · bootcamp3 · back-filled from the note" in idx
          and idx.index("2026-07-old-camp") < idx.index("2026-11-cash-flow-bootcamp")
          and pj(out).get("index_backfilled") == ["2026-07-old-camp"], idx)
    before = note.read_text()
    ok, out, _ = T("obsidian", "--vault", "vault", codes=(2,))
    check("obsidian: never overwrites an existing note without --force", ok and "--force" in out and note.read_text() == before)
    T("log-sale", "--tier", "VIP", "--price", "2997", "--count", "1")
    ok, out, _ = T("obsidian", "--vault", "vault", "--force", "--status", "final")
    idx = (V / "launches/_index.md").read_text()
    check("obsidian --force: overwrites the note and replaces (not duplicates) its index line",
          ok and pj(out).get("overwrote") and pj(out).get("index_updated") == "replaced" and idx.count("[[2026-11-cash-flow-bootcamp]]") == 1
          and idx.count("[[2026-07-old-camp]]") == 1
          and "8 buyers" in idx and "status: final" in note.read_text() and "- Book partner podcasts a month earlier" in note.read_text(), idx)
    # member-style notes (M3)
    (V / "launches/2026-09-built-for-freedom-intensive.md").write_text(
        "---\ntitle: Built for Freedom\ntype: launch\ndate: 2026-09-18\n---\n# Built for Freedom\n\n## Numbers\n\n- 105 opened the offer\n\n"
        "## What broke\n\n- the checkout was closed\n\n## Keep\n\n- the prep doc\n")
    (V / "launches/2026-03-spring-webinar.md").write_text("# Spring webinar\n\nNo headings we know, just a paragraph about it.\n")
    (V / "launches/random-note.md").write_text("---\ntype: idea\n---\nnot a launch\n")
    (V / "knowledge").mkdir()
    (V / "knowledge/evergreen-audit.md").write_text("---\ntype: strategy\ntags: [audit, launch]\ndate: 2026-08-02\n---\n"
                                                    "# Audit\n\n### Lessons learned (ranked)\n\n- follow-up stayed in draft\n")
    (V / "knowledge/unrelated.md").write_text("---\ntype: strategy\n---\n# Launch of a rocket\n")
    wf = V / "launches/2026-11-cash-flow-bootcamp-work"; (wf / "emails").mkdir(parents=True)
    (wf / "tracker.json").write_text("{}"); (wf / "emails/06-invite-1-launch-day.md").write_text("---\ntags: [launch]\n---\ndraft\n")
    ok, out, _ = T("obsidian-read", "--vault", "vault")
    d = pj(out); ls = d.get("launches", []); by = {Path(x["file"]).stem: x for x in ls}
    check("M3: obsidian-read finds notes by type, tags or launch-like file names; skips ideas, unrelated notes and work folders",
          ok and set(by) == {"2026-11-cash-flow-bootcamp", "2026-09-built-for-freedom-intensive", "2026-07-old-camp",
                             "2026-03-spring-webinar", "evergreen-audit"}, sorted(by))
    check("obsidian-read: newest first, frontmatter parsed (quoted title, tag list)",
          [x["frontmatter"].get("date") for x in ls][:3] == ["2026-11-10", "2026-09-18", "2026-08-02"]
          and by["2026-07-old-camp"]["frontmatter"]["title"] == "Old camp: July"
          and by["2026-07-old-camp"]["frontmatter"]["tags"] == ["launch", "event"], [x["frontmatter"].get("date") for x in ls])
    check("obsidian-read: returns the Results and Lessons sections", by["2026-07-old-camp"]["results"] == "- 212 registered"
          and by["2026-07-old-camp"]["lessons"] == "- Schedule the Day-1-night email"
          and "| Registered |" in by["2026-11-cash-flow-bootcamp"]["results"]
          and "Book partner podcasts" in by["2026-11-cash-flow-bootcamp"]["lessons"], by.get("2026-07-old-camp"))
    bf = by["2026-09-built-for-freedom-intensive"]
    check("M3: the member's own headings are read (Numbers, What broke, Keep; Lessons learned at any level)",
          bf["results"] == "- 105 opened the offer" and bf["lessons"] == "- the checkout was closed" and bf["protect"] == "- the prep doc"
          and by["evergreen-audit"]["lessons"] == "- follow-up stayed in draft" and by["evergreen-audit"]["found_in"] == "vault", bf)
    check("M3: a note with no known heading gets a warning and its body, not silent nulls",
          "No headings we know" in by["2026-03-spring-webinar"].get("body_excerpt", "")
          and any("2026-03-spring-webinar" in x and "no Results" in x for x in d.get("warnings", [])), d.get("warnings"))
    E = w / "emptyvault"; (E / ".obsidian").mkdir(parents=True)
    ok, out, _ = T("obsidian-read", "--vault", "emptyvault")
    d = pj(out)
    check("M3: nothing found → a warning listing where it looked", ok and d["count"] == 0
          and any("Looked in:" in x and "launches/ (missing)" in x for x in d.get("warnings", [])) and len(d["looked_in"]) == 2, d)
    ok, out, _ = T("obsidian-read", "--vault", "plainfolder", codes=(2,))
    check("obsidian-read: refuses a folder without .obsidian too", ok and "no .obsidian folder" in out)

    # M23: test ledgers are labelled and skipped
    V2 = w2 / "vault"; (V2 / ".obsidian").mkdir(parents=True)
    T2 = lambda *a, codes=(0,): run([PY, TRK, *a], w2, ok_codes=codes)
    ok, out, _ = T2("obsidian", "--vault", "vault", "--slug", "2026-12-second")
    tn = (V2 / "launches/2026-12-second.md").read_text()
    check("M23: a test ledger's Obsidian note is labelled TEST and carries test: true", ok and pj(out)["test"] is True
          and "title: TEST · Second launch debrief" in tn and "\ntest: true\n" in tn and "tags: [launch, event, test]" in tn, tn[:300])
    ok, out, _ = T2("obsidian", "--vault", "vault", "--slug", "2026-11-pricing-webinar")
    idx = (V2 / "launches/_index.md").read_text()
    check("m14: singular buyer in the index line", "· 1 buyer (net of refunds)" in idx and "TEST · Second" in idx, idx)
    ok, out, _ = T2("obsidian-read", "--vault", "vault")
    d = pj(out)
    check("M23: obsidian-read skips test notes (and says so)", ok and [Path(x["file"]).stem for x in d["launches"]] == ["2026-11-pricing-webinar"]
          and any("2026-12-second" in x for x in d.get("skipped_test_notes", [])), d.get("skipped_test_notes"))
    ok, out, _ = T2("obsidian-read", "--vault", "vault", "--include-test")
    check("M23: --include-test lists them", pj(out).get("count") == 2)

    # m14: a launch folder inside the vault becomes a wikilink
    V3 = work / "vault3"; (V3 / ".obsidian").mkdir(parents=True)
    run([PY, TRK, "init", "--name", "Inside Camp", "--format", "webinar", "--days", "1", "--tz", "UTC", "--event-date", "2026-12-01",
         "--goal-buyers", "2", "--goal-cash", "2000"], V3)
    (V3 / "launches/2026-12-inside-camp/plan.md").write_text("# plan\n")
    ok, out, _ = run([PY, TRK, "obsidian", "--vault", "."], V3)
    tn = (V3 / "launches/2026-12-inside-camp.md").read_text()
    check("m14: the launch folder line is a [[wikilink]] when the folder is in the vault",
          ok and "Launch folder: [[launches/2026-12-inside-camp/plan|launches/2026-12-inside-camp]]" in tn, tn[:500])


# ---------------------------------------------------------------- review fixes (X2, X5, X6, X10, S3, S4, sessions, index)

def vault_fixture_tests(work):
    V = work / "realvault"
    shutil.copytree(FX / "vault", V)
    (V / ".obsidian").mkdir()
    ok, out, _ = run([PY, TRK, "obsidian-read", "--vault", "realvault"], work)
    d = pj(out); ls = d.get("launches", []); by = {Path(x["file"]).name: x for x in ls}
    names = [Path(x["file"]).name for x in ls]
    check("X2: a realistic vault: the member's own debriefs are found (YAML block-list tags, type: audit, type: prep, "
          "a 'Retro' and a 'Launch review' with no frontmatter, launches/), newest first, undated last",
          ok and names == ["Prep for autumn camp.md", "2026-05 Launch review.md", "2026-03 Spring Workshop Debrief.md",
                           "2025-11 Webinar postmortem.md", "2025-07 summer camp.md", "July Bootcamp Retro.md"], names)
    skipped = {Path(x["file"]).name: x["why"] for x in d.get("skipped", [])}
    leaked = [x["file"] for x in ls if any(w in x["file"] for w in ("Templates", "Sources", "Clients", "External", "Clippings",
                                                                   "Readwise", "event-planning", "Acme", "template"))]
    check("X2: templates (folder '99 Templates', a {{title}} note), imported material (External, Sources/Flight Club "
          "transcript, Readwise author, Clippings source URL), client notes (Clients/, type: client) and a partial tag "
          "match (event-planning) are left out",
          not leaked and skipped.get("Debrief template copy.md", "").startswith("template")
          and "type: client" in skipped.get("Acme debrief.md", "") and "author: Dana Ruiz" in skipped.get("Podcast debrief notes.md", ""),
          (leaked, skipped))
    sp = by["2026-03 Spring Workshop Debrief.md"]
    check("X2: headings matched case-insensitively by the words they contain ('Key lessons', 'Wins', 'What I'd change'), "
          "and ### sub-headings stay inside their section", sp["frontmatter"]["tags"] == ["launch", "debrief"]
          and sp["lessons"].startswith("- Reminders went out") and "### Emails\n- Fewer invites" in sp["lessons"]
          and "### Close\n- Payment plan too expensive." in sp["lessons"] and sp["protect"] == "- 41% show-up on a list of 900."
          and sp["missing"] == ["results"], sp)
    lr = by["2026-05 Launch review.md"]
    check("X2: '## RESULTS', '### Leaks' (with its '#### Detail') and '### What worked' at deeper levels",
          lr["results"] == "- 300 registered, 96 live" and lr["lessons"] == "- reminders late\n#### Detail\n- 3 hours early on Day 2"
          and lr["protect"] == "- the live demo" and lr["date"] == "2026-05", lr)
    pm = by["2025-11 Webinar postmortem.md"]
    check("X2: type: audit with 'Lessons learned'", pm["results"].startswith("120 registered") and pm["lessons"] == "Run it twice.", pm)
    rt = by["July Bootcamp Retro.md"]
    check("X2: no frontmatter, found by its name; email addresses and phone numbers are redacted",
          rt["date"] is None and rt["results"].startswith("- 220 registered") and "[email removed]" in rt["lessons"]
          and "[phone removed]" in rt["lessons"] and "@" not in json.dumps(d) and "010-2234" not in json.dumps(d), rt["lessons"])
    check("X2: a note without a known heading returns a redacted body excerpt and a warning",
          "waitlist first" in by["Prep for autumn camp.md"].get("body_excerpt", "")
          and any("Prep for autumn camp" in x for x in d.get("warnings", [])), d.get("warnings"))
    ok, out, _ = run([PY, TRK, "obsidian-read", "--vault", "realvault", "--author", "Dana Ruiz"], work)
    names2 = [Path(x["file"]).name for x in pj(out).get("launches", [])]
    check("X2: --author NAME keeps the member's own authored note ('Takeaways' read as lessons)",
          "Podcast debrief notes.md" in names2 and next(x for x in pj(out)["launches"] if x["file"].endswith("Podcast debrief notes.md"))
          ["lessons"] == "- Book podcast slots earlier.", names2)

    # the index: the member's lines are never re-sorted; only marked lines are updated
    w = work / "idxw"; w.mkdir()
    T = lambda *a, codes=(0,): run([PY, TRK, *a], w, ok_codes=codes)
    T("init", "--name", "Index Camp", "--format", "webinar", "--days", "1", "--tz", "UTC", "--event-date", "2026-08-10",
      "--goal-buyers", "2", "--goal-cash", "2000")
    T("log-reg", "40")
    before = (V / "launches/_index.md").read_text()
    ok, out, _ = T("obsidian", "--vault", str(V))
    idx = (V / "launches/_index.md").read_text()
    mine = [x for x in before.splitlines() if x.strip()]
    check("minor: _index.md keeps every line the member wrote, in their order; the script's line is appended with a "
          "hidden marker", ok and idx.startswith(before.rstrip("\n")) and [x for x in idx.splitlines() if x in mine] == mine
          and idx.rstrip().endswith("<!-- launch_tracker -->") and "[[2026-08-index-camp]]" in idx.splitlines()[-1]
          and idx.count("[[2025-07 summer camp]]") == 1, idx)
    T("log-reg", "10")
    ok, out, _ = T("obsidian", "--vault", str(V), "--force")
    idx2 = (V / "launches/_index.md").read_text()
    check("minor: a re-run updates only its own marked line, in place", ok and idx2.count("[[2026-08-index-camp]]") == 1
          and "50 registered" in idx2 and idx2.splitlines()[:len(mine) + 1] == idx.splitlines()[:len(mine) + 1]
          and pj(out).get("index_updated") == "replaced", idx2)


def review_fix_tests(work):
    w = work / "fix"; w.mkdir()
    # S3: paid event economics
    ok, out, _ = run([PY, PLAN, "math", "--goal-cash", "30000", "--price", "497", "--list-size", "800", "--format", "workshop",
                      "--paid-event", "--ticket-price", "47", "--vip-price", "197"], w)
    d = pj(out); er = d.get("event_revenue", {})
    check("S3: --ticket-price and --vip-price model ticket and VIP cash (VIP at the labelled 4–15% range, typical 8%) and "
          "count it toward the cash goal",
          ok and er["ticket_price"] == 47 and er["vip_rate"]["typical"] == .08 and er["vip_rate"]["source"] == "VIP upgrade range (practitioner)"
          and abs(er["expected_from_list"]["ticket_cash"] - 48 * 47) < .01 and abs(er["expected_from_list"]["vip_cash"] - 48 * .08 * 197) < .01
          and d["goal"]["buyers"] == 22 and d["goal"]["cash_at_goal_with_event_revenue"] >= 30000
          and "VIP upgrade range (practitioner)" in d["sources"], er)
    ok, out, _ = run([PY, PLAN, "math", "--goal-cash", "30000", "--price", "497", "--list-size", "800", "--format", "workshop",
                      "--paid-event", "--ticket-price", "47", "--vip-price", "197", "--vip-rate", "5%", "--md"], w)
    check("S3: --vip-rate replaces the default; --md shows the event revenue table", ok and "## Event revenue (tickets and VIP)" in out
          and "VIP rate 4% / 5% / 6% of registrants (Member history)" in out, out[-500:])
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "5", "--price", "497", "--list-size", "800", "--format", "workshop",
                      "--ticket-price", "47"], w, ok_codes=(2,))
    check("S3: --ticket-price needs --paid-event", ok and "needs --paid-event" in out, out[-200:])
    # S4: roundtable
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "2", "--price", "25000", "--list-size", "40", "--format", "roundtable",
                      "--close", "call"], w)
    d = pj(out)
    check("S4: --format roundtable: one day, personal-invitation rates labelled Build Room assumption (not webinar rates), "
          "no lever from assumptions, a warning to ask the member's own close rate",
          ok and d["inputs"]["days"] == 1 and d["rates"]["registration"]["typical"] == .35 and d["rates"]["show_up"]["typical"] == .80
          and d["rates"]["booked"]["typical"] == .50 and d["rates"]["closed"]["typical"] == .30
          and all(d["rates"][k]["source"] == "Build Room assumption" for k in ("registration", "show_up", "booked", "held", "closed"))
          and "personal" in d["rates"]["registration"]["note"] and d["lever"]["stage"] is None
          and any(x.startswith("roundtable:") and "--history-closed" in x for x in d.get("warnings", [])), d.get("rates"))
    cold = pj(run([PY, PLAN, "math", "--goal-buyers", "2", "--price", "25000", "--list-size", "40", "--format", "webinar",
                   "--close", "call"], w)[1])
    check("S4: a roundtable to 40 hand-picked people expects more buyers than webinar rates would",
          d["typical"]["expected_from_list"]["buyers"] > 5 * cold["typical"]["expected_from_list"]["buyers"],
          (d["typical"]["expected_from_list"]["buyers"], cold["typical"]["expected_from_list"]["buyers"]))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "2", "--price", "25000", "--list-size", "400", "--format", "roundtable",
                      "--close", "call"], w)
    check("S4: a roundtable list over about 300 (or a room over 20) is warned", any("8–20" in x for x in pj(out).get("warnings", [])))
    ok, out, _ = run([PY, PLAN, "math", "--goal-buyers", "2", "--price", "25000", "--list-size", "40", "--format", "roundtable",
                      "--days", "2"], w, ok_codes=(2,))
    check("S4: a two-day roundtable is refused", ok and "one-day" in out)

    # S3 tracker: log-tickets; S6 log-calls --source; X10 sms
    T = lambda *a, codes=(0,): run([PY, TRK, *a], w, ok_codes=codes)
    ok, out, _ = T("init", "--name", "Paid Workshop", "--format", "workshop", "--days", "1", "--tz", "UTC",
                   "--event-date", "2026-12-05", "--goal-buyers", "5", "--goal-cash", "2500", "--paid-event", "--close", "both",
                   "--sms", "--date", "2026-10-17")
    check("X10: init --sms makes sms_compliance a critical gate item", ok and "planned" in pj(out).get("sms", ""))
    g = pj(T("gate", "--stage", "pre_invite")[1])
    sms = next(i for i in g["items"] if i["id"] == "sms_compliance")
    check("X10: with SMS planned, sms_compliance is critical and open (HOLD until consent and A2P are tested)",
          sms["critical"] and sms["status"] == "open" and any(x.startswith("sms_compliance") for x in g["hold"]), sms)
    ok, out, _ = T("log-tickets", "--count", "60", "--price", "47", "--vip-count", "6", "--vip-price", "197", "--source", "partner:Ann")
    T("log-reg", "60", "--source", "partner:Ann"); T("log-day", "--day", "1", "--live", "40", "--source-count", "partner:Ann=40")
    T("log-close", "--present", "30", "--saw-price", "30")
    T("log-sale", "--tier", "Core", "--price", "497", "--count", "3")
    ok, out2, _ = T("log-calls", "--booked", "4", "--held", "3", "--closed", "1", "--value", "3000", "--source", "partner:ann")
    T("log-sale", "--tier", "Call close", "--price", "3000", "--count", "1", "--via", "call", "--source", "partner:Ann")
    T("log-refund", "--tier", "Tickets", "--count", "1", "--amount", "47", "--source", "partner:Ann")
    T("partner", "--name", "Ann", "--commission-rate", "0.4")
    r = pj(T("report")[1]); m = r.get("money", {})
    check("S3: log-tickets logs tickets and VIP upgrades: in cash and booked, never buyers of the offer; tickets refundable",
          ok and m["ticket_cash"] == 2820 and m["vip_cash"] == 1182 and m["tickets"] == 60 and m["vip_upgrades"] == 6
          and m["cash"] == 2820 + 1182 + 1491 + 3000 and r["funnel"][-1]["actual"] == 4 and m["average_sale"] == round((1491 + 3000) / 4, 2)
          and r["refunds"]["count"] == 0 and m["refunded"] == 47, m)
    pa = r.get("partners", {}).get("Ann", {})
    check("S6: partner attribution across tickets, calls and refunds (names matched case-insensitively), commission on net cash",
          pj(out2).get("logged") and pa.get("registrations") == 60 and pa["attendees_day1"] == 40 and pa["buyers"] == 1
          and pa["cash"] == 2820 + 1182 + 3000 and pa["refunded"] == 47 and pa["commission_rate"] == .4
          and pa["commission_due"] == round((2820 + 1182 + 3000 - 47) * .4, 2), pa)
    # X10: SMS planned later through the launch folder's event.json
    w2 = work / "fix2"; w2.mkdir()
    T2 = lambda *a, codes=(0,): run([PY, TRK, *a], w2, ok_codes=codes)
    T2("init", "--name", "Email Camp", "--format", "webinar", "--days", "1", "--tz", "UTC", "--event-date", "2026-12-05",
       "--goal-buyers", "2", "--goal-cash", "2000")
    g = pj(T2("gate")[1])
    check("X10: email only: sms_compliance is na and not critical", "email only" in g["sms"]
          and not next(i for i in g["items"] if i["id"] == "sms_compliance")["critical"])
    ev = json.loads((FX / "event.json").read_text())
    (w2 / "launches/2026-12-email-camp/event.json").write_text(json.dumps(ev))
    g = pj(T2("gate")[1])
    sms = next(i for i in g["items"] if i["id"] == "sms_compliance")
    check("X10: when the launch folder's event.json turns SMS on, sms_compliance becomes critical and open again",
          "planned" in g["sms"] and sms["critical"] and sms["status"] == "open" and "sms_compliance" in g["stages"]["pre_invite"]["hold"], sms)
    # old ledgers: --live used to be the peak
    old = json.loads((w2 / "launches/2026-12-email-camp/tracker.json").read_text())
    old.pop("live_definition"); old["days_live"] = {"1": {"live": 50, "unique": 64, "date": "2026-12-05"}}
    (w2 / "launches/2026-12-email-camp/tracker.json").write_text(json.dumps(old))
    r = pj(T2("report")[1])
    check("X7: an older ledger's day (peak in live, unique alongside) is read as unique 64 with peak 50",
          r["funnel"][1]["actual"] == 64 and r["peak_concurrent"] == {"1": 50}, r.get("funnel"))

    # X6 and X5: run sheet link kinds and deadline wording
    sp = json.loads((FX / "runsheet.json").read_text())
    sp["links"].update({"zoom_call": "https://zoom.us/j/1", "booklet": "https://example.com/booklet.pdf",
                        "book_call": "https://example.com/book", "Buy": "https://example.com/buy"})
    pitch = next(s for s in sp["days"][2]["segments"] if s["kind"] == "pitch")
    pitch["links"] = ["checkout", "book_call", "zoom_call"]
    (w / "kinds.json").write_text(json.dumps(sp))
    ok, out, _ = run([PY, RUN, "build", "--spec", "kinds.json", "--out", "kinds.md"], w)
    d = pj(out); lk = d.get("links", {}); mod = d.get("checklists", {}).get("moderator", []); tech = d["checklists"]["tech"]
    closer = " ".join(d["checklists"].get("closer", []))
    check("X6: link kinds come only from an explicit kind or an exact key (book_call → booking, Buy → checkout); zoom_call "
          "and booklet stay other",
          ok and lk["zoom_call"]["kind"] == "other" and lk["booklet"]["kind"] == "other" and lk["book_call"]["kind"] == "booking"
          and lk["Buy"]["kind"] == "checkout" and lk["checkout"]["kind"] == "checkout", lk)
    check("X6: the moderator repeats every close link the pitch names, every 10 minutes; a zoom link is dropped once, as "
          "an ordinary link", "Day 3 15:40 drop checkout: https://example.com/checkout (as the price is shown)" in mod
          and "Day 3 15:40 drop book_call: https://example.com/book (as the price is shown)" in mod
          and "Day 3 16:00 drop book_call: https://example.com/book (again)" in mod
          and sum("drop zoom_call" in x for x in mod) == 1 and not any("hold zoom_call" in x for x in mod), mod)
    check("X6: the tech opens every close link, never the zoom link, as the money check",
          any("open checkout, book_call, Buy on a phone" in x for x in tech) and not any("open zoom_call" in x for x in tech), tech)
    lkc = next(c for c in d["checks"] if c["id"] == "link_kinds")
    check("X6: a key that looks like a close link but has no kind is a should warning (zoom_call)", not lkc["ok"]
          and lkc["level"] == "should" and "zoom_call" in lkc["detail"] and "booklet" not in lkc["detail"], lkc)
    check("X5: with no deadline anywhere, the closer is told there is none (no 'real deadline' line)",
          "no deadline: say when follow-up ends" in closer and "real deadline" not in closer and d["deadline"] is None, closer)
    sp["deadline"] = "2026-11-15 23:59 America/Los_Angeles"
    (w / "kinds2.json").write_text(json.dumps(sp))
    d = pj(run([PY, RUN, "build", "--spec", "kinds2.json", "--out", "kinds2.md"], w)[1])
    check("X5: a deadline in runsheet.json is named at the close", "the deadline (2026-11-15 23:59 America/Los_Angeles)"
          in " ".join(d["checklists"]["closer"]))
    (w / "pl").mkdir(); (w / "pl/plan.json").write_text(json.dumps({"schema": "buildroom-event-launcher/plan-1",
                                                                       "timeline": {"deadline": True, "cart_close": "2026-11-15"}}))
    d = pj(run([PY, RUN, "build", "--spec", "kinds.json", "--out", "kinds3.md", "--plan", "pl"], w)[1])
    check("X5: or the plan's cart close (--plan)", "the deadline (the cart closes 2026-11-15)" in " ".join(d["checklists"]["closer"]))

    # X5 and sessions in event_ics
    ev = json.loads((FX / "event.json").read_text())
    (w / "ev.json").write_text(json.dumps(ev))
    r = pj(run([PY, ICS, "reminders", "--spec", "ev.json"], w)[1])
    rp = {s["id"]: s for s in r["sends"]}["day3_replay"]["purpose"]
    check("X5: the close-day replay names no deadline unless there is one", "the deadline:" not in rp and "real deadline" not in rp
          and "no deadline: say when follow-up ends" in rp and r["deadline"] is None, rp)
    r = pj(run([PY, ICS, "reminders", "--spec", "ev.json", "--plan", "pl/plan.json"], w)[1])
    check("X5: with the plan's cart close, the replay names it", "the deadline: the cart closes 2026-11-15" in
          {s["id"]: s for s in r["sends"]}["day3_replay"]["purpose"])
    ev["days"][1] = {"date": "2026-11-11", "sessions": [{"start": "09:00", "end": "11:00", "title": "Day 2 (Europe-friendly)"},
                                                        {"start": "14:00", "end": "17:00"}]}
    (w / "two.json").write_text(json.dumps(ev))
    ok, out, _ = run([PY, ICS, "build", "--spec", "two.json", "--out", "two.ics", "--date", "2026-10-17"], w)
    d = pj(out); ev_ = d.get("events", [])
    okc, outc, _ = run([PY, ICS, "check", "two.ics"], w)
    check("minor: two sessions on one day: two VEVENTs with their own UIDs, the file checks clean",
          ok and len(ev_) == 4 and [e["day"] for e in ev_] == [1, 2, 2, 3] and ev_[1]["summary"] == "Day 2 (Europe-friendly)"
          and ev_[2]["summary"].endswith("Day 2 (session 2)") and ev_[2]["uid"].endswith("-day2-s2@buildroom-event-launcher")
          and ev_[1]["uid"].endswith("-day2@buildroom-event-launcher") and okc and pj(outc).get("ok"), [e.get("summary") for e in ev_])
    r = pj(run([PY, ICS, "reminders", "--spec", "two.json"], w)[1]); ids = {s["id"]: s for s in r.get("sends", [])}
    check("minor: reminders for a second session (dayN_15min_s2, dayN_live_s2); the night recap and replay follow the "
          "day's last session", {"day2_15min", "day2_live", "day2_15min_s2", "day2_live_s2"} <= set(ids)
          and ids["day2_live"]["local"].startswith("2026-11-11 09:00") and ids["day2_live_s2"]["local"].startswith("2026-11-11 14:00")
          and ids["day2_replay"]["local"].startswith("2026-11-11 19:00") and ids["day2_night"]["local"].startswith("2026-11-11 18:00"),
          sorted(ids))
    ev["days"][1]["sessions"][1]["start"] = "10:30"
    (w / "overlap.json").write_text(json.dumps(ev))
    ok, out, _ = run([PY, ICS, "build", "--spec", "overlap.json", "--out", "overlap.ics"], w, ok_codes=(2,))
    check("minor: overlapping sessions are refused", ok and "without overlapping" in out, out[-200:])
    rs = json.loads((FX / "runsheet.json").read_text()); rs["days"][1]["start"] = "09:00"; rs["days"][1]["end"] = "12:00"
    (w / "rs2.json").write_text(json.dumps(rs))
    ok, out, _ = run([PY, RUN, "build", "--spec", "rs2.json", "--out", "rs2.md", "--event", "two.json"], w, ok_codes=(0, 1))
    em = next(c for c in pj(out)["checks"] if c["id"] == "event_match")
    check("minor: the run sheet matches a day against any of its sessions (start matches session 1; end 12:00 vs 11:00 flagged)",
          "day 2 start" not in em["detail"] and "day 2 end 12:00 vs 11:00" in em["detail"], em)


def main():
    keep = "--keep" in sys.argv
    work = Path(tempfile.mkdtemp(prefix="buildroom-launch-tests-"))
    for f in ("launch_plan.py", "event_ics.py", "run_sheet.py", "launch_tracker.py"):
        src = (S / f).read_text(encoding="utf-8")
        head = src.split('"""', 2)[2]
        first_import = re.search(r"^import (?!sys\b).*$", head, re.M)
        check(f"{f}: stdlib only, no bytecode before other imports (m30), documented usage",
              "sys.dont_write_bytecode = True" in src and '"""' in src and first_import
              and head.index("sys.dont_write_bytecode = True") < first_import.start()
              and "Usage" in src and not re.search(r"^\s*(import|from)\s+(requests|urllib3|httpx|socket|http\.client)\b", src, re.M))
        ok, out, _ = run([PY, S / f, "--help"], work)
        check(f"{f} --help prints the usage", ok and "Usage" in out)
    confidentiality_tests()
    plan_json = plan_tests(work)
    ics_tests(work)
    runsheet_tests(work)
    w, w2 = tracker_tests(work, plan_json)
    obsidian_tests(work, w, w2)
    vault_fixture_tests(work)
    review_fix_tests(work)

    caches = [str(x) for x in list(ROOT.rglob("__pycache__"))]
    check("no __pycache__ anywhere under buildroom/", not caches, caches)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed" + (f" · work dir kept: {work}" if keep else ""))
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
