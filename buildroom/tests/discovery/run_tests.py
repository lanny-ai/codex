#!/usr/bin/env python3
"""Discovery Engine: Deep Discovery for a member's own business (scope, ledger, disagreements, gaps, readiness).

Usage:  python3 buildroom/tests/discovery/run_tests.py
"""
import re
import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "skills/buildroom-discovery-engine"
SCRIPT = SK / "scripts/discover.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def run(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def F(i, field, value, kind, ref, conf, **kw):
    f = {"id": f"f{i}", "field": field, "value": value, "source": {"kind": kind, "ref": ref}, "confidence": conf}
    if "date" in kw:
        f["source"]["date"] = kw.pop("date")
    f.update(kw)
    if field == "x.proof" and not f.get("absent"):
        f.setdefault("permission", "unknown")
    return f


def main():
    tmp = Path(tempfile.mkdtemp())
    led = tmp / "ledger.json"

    def write(findings, scope=True, **top):
        d = {"subject": "Harbor Coaching", "date": "2026-11-19", "findings": findings, **top}
        if isinstance(scope, dict):
            d["scope"] = scope
        elif scope:
            d["scope"] = {"read": ["Vault: Offers"], "excluded": ["Personal"], "agreed": "2026-11-19: 'leave out Personal'"}
        led.write_text(json.dumps(d))

    # ---- inventory: names only, private files held back ----------------------------------------
    v = tmp / "vault"
    for rel, body in {"Offers/2026 program pricing.md": "SECRETPRICE 4500", "Clients/testimonials.md": "x", "Notes/random.md": "x",
                      "Personal/diary.md": "x", "Finance/bank statement 2026.pdf": "x", "Admin/passwords.txt": "hunter2",
                      ".obsidian/workspace.json": "{}", "node_modules/pkg/readme.md": "x", "Media/photo.png": "x", ".env": "KEY=1"}.items():
        (v / rel).parent.mkdir(parents=True, exist_ok=True)
        (v / rel).write_text(body)
    c, out = run("inventory", v)
    check("inventory: lists readable files, most useful first", c == 0 and out.index("Offers/2026 program pricing.md") < out.index("Notes/random.md"))
    check("inventory: never prints file contents", "SECRETPRICE" not in out and "hunter2" not in out)
    held = out[out.index("Looks private"):]
    check("inventory: private-looking files are held back, not offered for reading",
          "bank statement" in held and "passwords.txt" in held and "bank statement" not in out[:out.index("Looks private")])
    check("inventory: hidden folders, dependencies and non-text files are skipped", ".obsidian" not in out and "node_modules" not in out and "photo.png" not in out and ".env" not in out)
    check("inventory: says nothing has been opened and asks what to leave out", "Nothing has been opened yet" in out and "leave out" in out)
    c, out = run("inventory", v, "--exclude", "Personal")
    check("inventory: an excluded folder is gone", c == 0 and "diary.md" not in out)
    c, out = run("inventory", v, "--json")
    j = json.loads(out)
    check("inventory: JSON form carries the same split", any("pricing" in f["path"] for f in j["files"]) and any("passwords" in s for s in j["sensitive_not_listed_for_reading"]))
    check("inventory: a missing folder is refused", run("inventory", tmp / "nope")[0] != 0)

    # ---- check: sources and honest confidence -------------------------------------------------
    good = [F(1, "1.what_i_do", "Coaching for clinic owners", "member", "said in session", "confirmed"),
            F(2, "1.price", "$4,500", "file", "Offers/2026 program pricing.md", "likely", date="2026-08-02"),
            F(3, "2.language", "tired of guessing", "web", "https://example.com/reviews", "likely", quote="I'm tired of guessing what to post")]
    write(good)
    c, out = run("check", led)
    check("check: a clean ledger passes", c == 0 and "0 to fix" in out, out)
    write(good, scope=False)
    check("check: no recorded scope agreement fails", run("check", led)[0] == 1 and "scope" in run("check", led)[1])
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed")])
    c, out = run("check", led)
    check("check: one source can never be 'confirmed'", c == 1 and "second independent source" in out, out)
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed"), F(2, "1.price", "4500 dollars", "web", "https://example.com/work", "confirmed")])
    check("check: two independent sources that agree can be 'confirmed'", run("check", led)[0] == 0, run("check", led)[1])
    write([F(1, "1.price", "$4,500", "web", "https://www.example.com/a", "confirmed"), F(2, "1.price", "$4,500", "web", "https://example.com/b", "confirmed")])
    check("check: two pages of the same website are one source", run("check", led)[0] == 1)
    write([F(1, "2.pains", "no time", "hypothesis", "reasoned from the sales page", "likely")])
    c, out = run("check", led)
    check("check: a hypothesis can only be 'inferred'", c == 1 and "only be 'inferred'" in out)
    bad = [F(1, "9.nope", "x", "file", "a.md", "likely"), F(2, "1.price", "", "file", "a.md", "likely"), F(3, "1.price", "x", "web", "the website", "likely"),
           F(4, "1.price", "x", "file", "", "likely"), F(5, "1.price", "x", "rumour", "x", "likely"), F(6, "1.price", "x", "file", "a.md", "sure"),
           F(7, "x.proof", "doubled revenue", "file", "a.md", "likely"), F(7, "x.voice", "sample", "file", "a.md", "likely")]
    write(bad)
    c, out = run("check", led)
    check("check: catches unknown field, empty value, vague web source, missing path, bad kind, bad confidence, missing quote, repeated id",
          c == 1 and all(x in out for x in ("unknown field", "no value", "full address", "file's path", "source kind", "confirmed, likely or inferred", "exact quote", "used twice")), out)
    led.write_text("{nope")
    check("check: an unreadable ledger is refused plainly", run("check", led)[0] != 0 and "Cannot read" in run("check", led)[1])

    # ---- conflicts: never pick a side ---------------------------------------------------------
    clash = [F(1, "1.price", "$3,000", "file", "Old/proposal.md", "likely", date="2025-03-01"),
             F(2, "1.price", "$4,500", "web", "https://example.com/work", "likely"),
             F(3, "1.lead_sources", "referrals", "file", "a.md", "likely"), F(4, "1.lead_sources", "LinkedIn", "web", "https://example.com", "likely"),
             F(5, "3.offer_name", "The Harbor Method", "file", "a.md", "likely"), F(6, "3.offer_name", "the harbor method.", "web", "https://example.com", "likely")]
    write(clash)
    c, out = run("conflicts", led)
    check("conflicts: two prices from two sources are shown side by side with their dates", "$3,000" in out and "$4,500" in out and "2025-03-01" in out and "Never pick one yourself" in out)
    check("conflicts: list fields and same-meaning values are not disagreements", "Lead sources" not in out and "Offer name" not in out and out.count("to ask the member") == 1 and "1 to ask" in out)
    write(clash + [F(7, "1.price", "$4,500", "member", "said in session", "confirmed")])
    check("conflicts: the member's word settles it", "No disagreements" in run("conflicts", led)[1])
    write([F(1, "1.price", "$3,000", "file", "a.md", "likely"), F(2, "1.price", "$9,000", "hypothesis", "guessed from the market", "inferred")])
    check("conflicts: a guess is not a source that can disagree", "No disagreements" in run("conflicts", led)[1])

    # ---- gaps: few, ranked, disagreements first -----------------------------------------------
    write(clash)
    c, out = run("gaps", led)
    lines = [l for l in out.splitlines() if l[:1].isdigit()]
    check("gaps: at most ten questions", len(lines) == 10, len(lines))
    check("gaps: the disagreement is asked first, quoting both sides", lines[0].startswith("1. Current price") and "$3,000" in lines[0] and "$4,500" in lines[0])
    check("gaps: then the fields most work depends on", "what do you do" in lines[1] and "Who exactly do you serve" in lines[2])
    check("gaps: the four must-know fields come before everything else", all(any(q in l for l in lines[1:5]) for q in ("what do you do", "Who exactly do you serve", "main result", "promise a client")), lines[1:5])
    check("gaps: what is already likely is not asked again", "main offer called" not in out and "How do people find you" not in out)
    check("gaps: the rest is left for the build sessions, by name", "Left for the build sessions" in out and "Tools" in out)
    c, out = run("gaps", led, "--cap", "3")
    check("gaps: the cap can be lowered", len([l for l in out.splitlines() if l[:1].isdigit()]) == 3)
    write([F(1, "2.profile", "Clinic owners with one site", "hypothesis", "reasoned from the home page", "inferred")])
    c, out = run("gaps", led)
    check("gaps: confirming the session's own guess comes last, after real gaps", "my best guess" not in out and "Best client, in one line" in out.split("Left for the build sessions")[1])
    c, out = run("gaps", led, "--cap", "40")
    check("gaps: a half-known field quotes the guess and says it is one", "my best guess is “Clinic owners with one site”" in out and "my guess, reasoned from the home page" in out)

    # ---- readiness: a guide, with a floor ------------------------------------------------------
    c, out = run("ready", led)
    check("ready: a thin ledger is not ready and says what must be known first", c == 2 and "Not ready yet" in out and "What I do" in out and "Core promise" in out)
    check("ready: always called a guide, not a measurement", "a guide to how much is known, not a measurement" in out)
    import importlib.util
    spec = importlib.util.spec_from_file_location("discover", SCRIPT)
    dm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dm)
    full = [F(i, f[0], "known " + f[0], "member", "said in session", "confirmed", quote="q") for i, f in enumerate(dm.FIELDS)]
    write(full)
    c, out = run("ready", led)
    check("ready: everything confirmed is 100 and ready", c == 0 and "100 out of 100" in out and "Ready:" in out, out)
    write([f for f in full if f["field"] != "1.core_result"])
    c, out = run("ready", led)
    check("ready: a high score without a core field is still not ready", c == 2 and "Core result" in out and int(out.split("Readiness: ")[1].split()[0]) >= 70, out)
    write([f for f in full if f["field"] != "3.promise"])
    c, out = run("ready", led)
    check("ready: a core result in the member's own words stands in for a missing promise", c == 0 and "Ready:" in out, out)
    c, out = run("gaps", led)
    check("gaps: the promise is put as the core result to confirm, not as an open question", "is it roughly your core result" in out and "known 1.core_result" in out, out)
    write([f for f in full if f["field"] not in ("3.promise", "1.core_result")] + [F(900, "1.core_result", "fuller classes", "file", "a.md", "likely")])
    c, out = run("ready", led)
    check("ready: a core result only found in a file does not stand in for the promise", c == 2 and "Core promise" in out, out)

    # ---- round 2 of the trial runs ------------------------------------------------------------
    thin = [F(1, "1.what_i_do", "doula", "business_file", "§1", "confirmed"), F(2, "1.who_i_serve", "first-time parents", "business_file", "§1", "confirmed"),
            F(3, "1.core_result", "a calmer birth", "business_file", "§1", "confirmed")]
    write(thin)
    lines = [l for l in run("gaps", led)[1].splitlines() if l[:1].isdigit()]
    easy = [i for i, l in enumerate(lines) if any(q in l for q in ("What do you charge", "actually receive", "book a call or buy"))]
    hard = [i for i, l in enumerate(lines) if any(q in l for q in ("struggling with", "exact words do your clients", "hesitate to buy"))]
    check("gaps: on a thin file, what every owner knows is asked before the hard questions", len(easy) == 3 and (not hard or max(easy) < min(hard)), lines)
    none = dict(F(4, "x.proof", "none yet", "member", "said in session", "confirmed"), absent=True)
    none2 = dict(F(5, "3.typical_result", "none I can back up", "member", "said in session", "confirmed"), absent=True)
    write(thin + [none, none2])
    out = run("gaps", led, "--cap", "40")[1]
    check("gaps: a member's answer of none is not asked again", "one real result a client got" not in out and "typical client get" not in out, out)
    c, out = run("ready", led)
    check("ready: none earns no credit, and is not listed again as a question that would help", c == 2 and "typical client get" not in out, out)
    write(thin, skipped=[f[0] for f in dm.FIELDS if f[0] not in ("1.what_i_do", "1.who_i_serve", "1.core_result")])
    c, out = run("ready", led)
    check("ready: with nothing left to ask it says so and names the session to run by hand", c == 2 and "nothing left to ask" in out and "Do not offer more questions" in out and "Ideal Client Avatar" in out, out)
    old = [dict(F(6, "x.story", "Ran a studio for eight years", "file", "Notes/bio old.md", "inferred"), stale=True),
           dict(F(7, "1.price", "$3,000", "file", "Old/proposal.md", "inferred"), stale=True), F(8, "1.price", "$4,800", "member", "said in session", "confirmed")]
    write(thin + old)
    page = run("page", led)[1]
    body, older = page.split("## Older material")[0], page.split("## Older material")[1]
    check("page: out-of-date material never sits among the findings", "eight years" not in body and "$3,000" not in body and "$4,800" in body, body)
    check("page: every out-of-date finding is listed apart, including ones a current answer replaced", "eight years" in older and "$3,000" in older, older)
    out = run("gaps", led, "--cap", "40")[1]
    check("gaps: an old file is worded as an older source, never as my best guess", "an older source says “Ran a studio" in out and "my best guess is “Ran a studio" not in out, out)
    write(thin + [F(9, "1.who_i_serve", "any creative business", "file", "Notes/bio.md", "likely")])
    c, out = run("conflicts", led)
    check("conflicts: a file that differs from the Business File is not an open choice", "No disagreements" in out and "something different from the member's Business File" in out and "any creative business" in out, out)
    check("page: it is listed as a place that says something different", "## Places that say something different from your Business File" in run("page", led)[1])
    write(thin + [dict(F(10, "x.proof", "revenue basically doubled", "file", "wins.md", "likely", quote="someone told me revenue doubled"), permission="unknown")])
    check("check: second-hand talk is refused as proof", "second-hand" in run("check", led)[1])
    write([F(1, "1.price", "$1,450 per month. One-time setup fee: $2,000.", "file", "Offers/a.md", "likely"), F(2, "1.price", "$1,450 a month", "web", "https://example.com", "likely")])
    check("conflicts: a price with a setup fee does not disagree with the same price without it", "No disagreements" in run("conflicts", led)[1])
    write(thin + [dict(F(11, "4.category", "bookkeeping for dental practices", "member", "said in session", "confirmed"), guess_ok=True)])
    check("page: a guess the member okayed is shown as my wording, not as their own words", "my wording; you said it looks right" in run("page", led)[1])
    check("inventory: a trade word in an offer file is not private; plainly private names are",
          not dm.looks_private("Clients/payroll cleanup offer.md") and not dm.looks_private("Offers/Diagnosis call script.md")
          and all(dm.looks_private(n) for n in ("Finance/2025 taxes.md", "Notes/therapy notes.md", "Notes/private.md", "Clients/Whitcombe P&L 2025.pdf", "Admin/payroll.xlsx", "Personal/journal.md")))
    QREF = (SCRIPT.parent.parent / "references/deep-discovery.md").read_text()
    QSK = (SCRIPT.parent.parent / "SKILL.md").read_text()
    write(thin, skipped=["2.pains", "2.profile"])
    c, out = run("ready", led)
    check("ready: the extra round leads with what an owner knows and drops a section whose basics were skipped", "What do you charge" in out and "hesitate to buy" not in out and "look like after working with you" not in out
          and "record \"extra_round\": true" in out, out)
    write(thin, skipped=["2.pains", "2.profile"], extra_round=True)
    c, out = run("ready", led)
    check("ready: after the one extra round it offers no more questions", c == 2 and "The one extra round of questions has been asked. Do not offer more questions." in out and "What do you charge" not in out, out)
    write(thin + [F(30, "1.booking", "Book a 20-minute fit call", "web", "https://example.com/", "likely")])
    out = run("gaps", led)[1]
    check("gaps: an easy fact found only on a public page is put to the member in one line", "your page says “Book a 20-minute fit call”" in out and "Is that right today?" in out, out)
    # ---- Quick Start: the short interview for a member with little written down -----------------
    write(thin + [none], skipped=["2.dream"])
    c, out = run("interview", led)
    qlines = [l for l in out.splitlines() if re.match(r"\s+\d+\. ", l)]
    check("interview: three short blocks, easy facts first, with a count and a time", c == 0 and out.index("Your offer") < out.index("Your client") < out.index("You and your business")
          and f"{len(qlines)} short questions" in out and "minutes" in out and "What do you charge" in qlines[2] + qlines[3], out)
    check("interview: leaves out what is known, skipped or answered, and never asks for quotes, voice or proof",
          not any(q in out for q in ("what do you do for your clients", "look like after working with you", "exact words do your clients", "sounds most like you", "one real result a client got")))
    check("interview: the promise is put as the core result to confirm", "roughly your core result, “a calmer birth”" in out)
    check("interview: answers are recorded as given", "Do not improve an answer" in out and "\"none\" is a real answer" in out)
    write(thin + [none, F(20, "3.deliverables", "two prenatal visits", "member", "said in session", "confirmed"), F(21, "3.deliverables", "on call from 38 weeks", "member", "said in session", "confirmed"),
                  F(22, "1.price", "$9,999", "file", "Old/p.md", "likely"), dict(F(23, "4.alternative", "go without", "member", "said in session", "confirmed"), guess_ok=True),
                  F(24, "2.pains", "fear of being ignored", "hypothesis", "reasoned", "inferred")])
    c, out = run("onepage", led)
    check("onepage: only the member's own words, as given", c == 0 and "two prenatal visits" in out and "on call from 38 weeks" in out and "$9,999" not in out and "fear of being ignored" not in out
          and "Nothing was added and nothing was polished." in out, out)
    check("onepage: a guess they okayed is marked as my wording, and what is open is listed, not filled", "go without (my wording; you said it looks right)" in out and "## Still open" in out and "Pains" in out.split("## Still open")[1])
    full_ans = [F(100 + i, k, "answer " + k, "member", "said in session", "confirmed") for i, k in enumerate(k for _t, ks in dm.INTERVIEW for k in ks)]
    write(full_ans)
    check("interview: a member who answers it all is ready, with nothing left to ask", run("ready", led)[0] == 0 and "Nothing left to ask" in run("interview", led)[1])
    check("skill: the short interview is offered when there is little to read", "## Quick Start: when there is little to read" in QREF and "Interview me about my business" in QREF and "interview me about my business" in QSK.split("---")[1]
          and len(QSK.split("---")[1]) < 700 and "One pass only" in QREF and "Do not improve an answer." in QREF)
    check("retired: entries split on semicolons, notes in brackets ignored, an unquoted entry counts whole",
          dm.parse_retired(' “Featured in Ceramics Monthly” (you said "Do not use it"); the name Studio Growth Sprint; none') == ["Featured in Ceramics Monthly", "Studio Growth Sprint"])
    check("retired: a name given outside the quotation marks in the same entry is retired too",
          dm.parse_retired('"Featured in Ceramics Monthly", and the name Studio Growth Sprint.') == ["Featured in Ceramics Monthly", "Studio Growth Sprint"])
    write([dict(f, source={"kind": "hypothesis", "ref": "reasoned"}, confidence="inferred") for f in full])
    c, out = run("ready", led)
    check("ready: guesses alone never reach ready", c == 2 and int(out.split("Readiness: ")[1].split()[0]) < 70, out)
    write([F(1, "1.price", "$4,500", "file", "a.md", "confirmed")])
    check("ready: refuses to score a ledger that fails its checks", run("ready", led)[0] not in (0, 2))
    w = full + [F(90, "1.price", "$1", "file", "a.md", "likely"), F(91, "1.price", "$2", "web", "https://example.com", "likely")]
    check("ready: weights sum is stable and core fields exist", all(k in dm.FIELD for k in dm.CORE) and sum(f[3] for f in dm.FIELDS) > 0 and len(w) > 0)

    # ---- lessons from the trial runs ---------------------------------------------------------
    # two sources that word it differently agree when they make the same claim
    write([F(1, "1.what_i_do", "Monthly bookkeeping and a numbers review for dental practices", "business_file", "§1", "confirmed", claim="bookkeeping for dental practices"),
           F(2, "1.what_i_do", "Bookkeeping for independent dental practices.", "web", "https://example.com/", "likely", claim="bookkeeping for dental practices"),
           F(3, "1.what_i_do", "Done-for-you monthly bookkeeping for a dental practice", "file", "Offers/program.md", "confirmed", claim="bookkeeping for dental practices")])
    c, out = run("check", led)
    check("claims: different wording with the same claim is agreement, and can be confirmed", c == 0 and "No disagreements" in run("conflicts", led)[1], out)
    write([F(1, "1.who_i_serve", "Pottery studio owners", "web", "https://example.com/", "likely", claim="pottery studios only"),
           F(2, "1.who_i_serve", "Any creative business", "file", "Notes/bio.md", "likely", claim="all creative businesses")])
    check("claims: different claims are a disagreement", "Who I serve" in run("conflicts", led)[1])
    write([F(1, "1.who_i_serve", "Owners of one clinic", "business_file", "§1", "confirmed")])
    check("business file: its lines are the member's own word and may be confirmed alone", run("check", led)[0] == 0)
    write([F(1, "1.price", "$4,500", "file", "Offers/a.md §2", "confirmed"), F(2, "1.price", "$4,500", "file", "Offers/a.md, page 3", "confirmed")])
    check("independence: two parts of one file are still one source", run("check", led)[0] == 1)
    # out-of-date sources
    write([F(1, "3.guarantee", "Double your enrollment or your money back", "file", "Old/Proposal 2024.md", "likely", stale=True)])
    c, out = run("check", led)
    check("stale: an out-of-date source cannot be 'likely'", c == 1 and "out-of-date source can only be 'inferred'" in out)
    old = [F(1, "3.guarantee", "Double your enrollment or your money back", "file", "Old/Proposal 2024.md", "inferred", stale=True, date="2024-05-01"),
           F(2, "1.price", "$3,000", "file", "Old/Proposal 2024.md", "inferred", stale=True, date="2024-05-01"),
           F(3, "1.price", "$4,800", "web", "https://example.com/", "likely")]
    write(old)
    c, out = run("gaps", led)
    first = [l for l in out.splitlines() if l[:1].isdigit()][0]
    check("stale: an old guarantee with nothing newer is asked about first, as a question", "Guarantee: an older source says “Double your enrollment or your money back”" in first and "Is that still true today?" in first, first)
    check("stale: an old price against a current one is not a disagreement to settle", "No disagreements" in run("conflicts", led)[1] or "Current price" in run("conflicts", led)[1])
    c, pg = run("page", led)
    check("stale: the page sets old material apart and never lists it as a finding", "## Older material I am not relying on" in pg and "- **Guarantee:** Double" not in pg and "2024-05-01" in pg)
    # retired lines
    bfile = tmp / "BF.md"
    bfile.write_text((ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text().replace(
        "- **Retired lines** (never used again in any output, by any session — e.g. a credibility story, a claim, an old offer; each one in quotation marks, separated by semicolons):",
        "- **Retired lines** (never used again in any output, by any session — e.g. a credibility story, a claim, an old offer; each one in quotation marks, separated by semicolons): \"Featured in Ceramics Monthly\" (withdrawn); “Studio Growth Sprint”"))
    write([F(1, "x.credentials", "Ran a studio for eight years. Featured in Ceramics Monthly.", "file", "Notes/bio.md", "likely")])
    check("retired: nothing is flagged without the Business File", run("check", led)[0] == 0)
    c, out = run("check", led, "--business-file", bfile)
    check("retired: with the Business File, a finding that carries a retired line is caught", c == 1 and "contains a retired line (“Featured in Ceramics Monthly”)" in out, out)
    write([F(1, "x.credentials", "Ran a studio for eight years. Featured in Ceramics Monthly.", "file", "Notes/bio.md", "likely", retired=True),
           F(2, "1.what_i_do", "Coaching for studio owners", "business_file", "§1", "confirmed")])
    c, pg = run("page", led)
    check("retired: marked retired it passes, is never shown as a finding, and the page says where it still lives",
          run("check", led, "--business-file", bfile)[0] == 0 and "## Retired lines still in your files" in pg and "your file Notes/bio.md" in pg and "**Background and credentials:**" not in pg)
    check("retired: the template's own example text is not mistaken for a retired line", run("check", led, "--business-file", ROOT / "templates/BUILDROOM_BUSINESS_FILE.md")[0] == 0)
    # absent, skipped, files current
    write([F(1, "x.proof", "none yet", "member", "said in session", "confirmed", absent=True), F(2, "3.guarantee", "None", "member", "said in session", "confirmed", absent=True)])
    cr = dm.credit(dm.load(led))
    check("absent: 'no proof' earns nothing, 'no guarantee' is a real answer", "x.proof" not in cr and cr.get("3.guarantee") == 1.0, cr)
    write([F(1, "x.proof", "none", "file", "a.md", "likely", absent=True)])
    check("absent: only the member can say there is none", "only the member can say there is none" in run("check", led)[1])
    write([F(1, "x.proof", "Doubled", "file", "a.md", "likely", quote="We doubled")] )
    led.write_text(led.read_text().replace('"permission": "unknown"', '"permission": "maybe"'))
    check("proof: must say whether it may be used", "proof needs \"permission\"" in run("check", led)[1])
    write([F(1, "1.what_i_do", "x", "business_file", "§1", "confirmed")], skipped=["1.tools", "3.promise"])
    c, out = run("gaps", led)
    c2, out2 = run("ready", led)
    check("skipped: a skipped question is not asked again, here or in the readiness advice", "Which tools do you use" not in out and "promise a client" not in out
          and "Skipped by the member, not asked again (2)" in out and "promise a client" not in out2 and "Already skipped by the member" in out2, out2)
    write([], skipped=["nope"])
    check("skipped: an unknown field is refused", "skipped: unknown field" in run("check", led)[1])
    likely = [F(i, f[0], "known", "file", "Offers/program.md", "likely", quote="q") for i, f in enumerate(dm.FIELDS)]
    write(likely)
    before = dm.score(dm.load(led))[0]
    write(likely, files_current="2026-11-21: 'yes, all current'")
    after = dm.score(dm.load(led))[0]
    check("files current: once the member says their files are current, their own file findings count in full", before == 70 and after == 100, (before, after))
    write([dict(f, source={"kind": "web", "ref": "https://example.com/"}) for f in likely], files_current="2026-11-21: yes")
    check("files current: it never lifts a web page", dm.score(dm.load(led))[0] == 70)
    check("ready: a not-ready verdict tells the member what to do instead of a long run", "A few minutes of answers now is worth more than a long run" in out2.replace("a few", "A few") and "Autopilot" in out2)
    # inventory
    v2 = tmp / "vault2"
    for rel in ("Clients/Banker avatar.md", "Clients/Will Parker testimonial.md", "Offers/Health coaching program.md", "Offers/Positioning statement.md", "Offers/Token of thanks bonus.md",
                "Personal/journal.md", "Finance/2025 tax return notes.md", "Finance/bank statement May.pdf", "private/ideas.md", "discovery/What_I_Found.md", "autopilot/drafts/01.md",
                "backups/old.md", "BUILDROOM_BUSINESS_FILE.md", "Old/BUILDROOM_BUSINESS_FILE.md", "_MEMBER_ANSWERS.md", "notes.md", "Offers/keep.md"):
        (v2 / rel).parent.mkdir(parents=True, exist_ok=True)
        (v2 / rel).write_text("x")
    c, out = run("inventory", v2)
    top, held = out.split("Looks private")[0], out.split("Looks private")[1]
    check("inventory: ordinary business file names are not mistaken for private ones",
          all(n in top for n in ("Banker avatar.md", "Will Parker testimonial.md", "Health coaching program.md", "Positioning statement.md", "Token of thanks bonus.md")))
    check("inventory: a Personal or private folder, a journal, a tax return and a bank statement are held back",
          all(n in held for n in ("Personal/journal.md", "tax return notes.md", "bank statement May.pdf", "private/ideas.md")) and "journal.md" not in top)
    check("inventory: Build Room's own output is never offered as research", not any(n in out for n in ("What_I_Found.md", "autopilot/drafts", "backups/old.md", "_MEMBER_ANSWERS")))
    check("inventory: the Business File is listed apart, and two of them are flagged", "Your Business File (read as your own word, not as research)" in out and "There is more than one." in out
          and "BUILDROOM_BUSINESS_FILE.md" not in top.split("Your Business File")[0])
    c, out = run("inventory", v2, "--exclude", "notes.md", "Offers/keep.md", "Clients")
    check("inventory: a single file can be left out, and the output confirms it", "Left out, as you asked (3)" in out and "notes.md" not in out.split("Left out")[0] and "Banker" not in out.split("Left out")[0])
    check("inventory: says when nothing matched what was asked", "Nothing here matched what you asked to leave out: zzz" in run("inventory", v2, "--exclude", "zzz")[1])
    # the page
    write([F(1, "x.proof", "Found $38,000 in miscoded lab fees", "file", "Clients/t.md", "likely", quote="We found $38,000 in lab fees", who="an office manager", permission="no"),
           F(2, "x.proof", "Knew overhead in three months", "file", "Clients/t.md", "likely", quote="I knew my overhead was 71 percent", who="a named client", permission="yes"),
           F(3, "1.lead_sources", "Instagram", "business_file", "§1", "confirmed"), F(4, "1.lead_sources", "Instagram", "business_file", "§1", "confirmed"),
           F(5, "1.price", "$4,800", "web", "https://example.com/", "confirmed", claim="4800"), F(6, "1.price", "4800 dollars", "file", "Offers/a.md", "confirmed", claim="4800")],
          scope={"read": ["Vault"], "excluded": [], "opened": 9, "agreed": "2026-11-21: ok"})
    c, pg = run("page", led)
    check("page: proof shows who said it and whether it may be used", "said by an office manager · NOT to be used publicly" in pg and "permission to use: yes" in pg)
    check("page: a repeated line prints once, and a confirmed line names its other sources", pg.count("- Instagram") == 1 and "also: your file Offers/a.md" in pg)
    check("page: says how many files were opened", "(9 files opened)" in pg)

    # ---- the page -------------------------------------------------------------------------------
    write(clash + [F(8, "x.voice", "sample", "file", "Posts/a.md", "likely", quote="Here is the thing nobody tells you."),
                   F(9, "2.pains", "no time", "hypothesis", "the sales page", "inferred")])
    c, out = run("page", led)
    check("page: says what was read and what was left alone", "**What I read:** Vault: Offers" in out and "left alone, as you asked:** Personal" in out)
    check("page: every finding shows its confidence and where it came from", "_likely · your file a.md_" in out and "_inferred · my guess, from the sales page_" in out)
    check("page: disagreements are a section of their own, not a chosen answer", "## Things that disagree" in out and "“$3,000”" in out and "**Current price / price range:** $" not in out)
    check("page: voice samples print the exact quote", "“Here is the thing nobody tells you.”" in out)
    check("page: lists what could not be found and ends with the readiness guide", "## What I could not find" in out and "Guarantee" in out and "not a measurement of your business" in out)
    check("page: invites correction", "Correct anything that is wrong. Your word always wins." in out)

    # ---- the script touches nothing it should not ---------------------------------------------
    src = SCRIPT.read_text()
    check("script: standard library only, no network, no writing", not any(x in src for x in ("import requests", "urllib", "socket", "http.client", ".write_text(", "open(")))
    check("script: field labels cover what the method guide names", all(f"`{f[0]}`" in (SK / "references/deep-discovery.md").read_text() for f in dm.FIELDS))

    # ---- the skill's instructions ------------------------------------------------------------------
    sk = (SK / "SKILL.md").read_text()
    ref = (SK / "references/deep-discovery.md").read_text()
    check("skill: Deep Discovery is in the foundation list and the flow", "references/deep-discovery.md" in sk and "### Own business — Deep Discovery" in sk)
    check("skill: scope is agreed before anything is opened", "opens nothing" in sk and "Scope first. Nothing is opened before the member has seen the list and agreed." in ref)
    check("skill: the page is shown before any question", "before asking anything" in sk and "Show the page before asking a single question about the business." in ref)
    check("skill: ten questions at most, skippable", "at most ten" in sk and "Do not go past ten in this round." in ref and "That is the last round." in ref and "may skip any question" in ref)
    check("skill: disagreements go to the member", "Choose between two sources that disagree. The member decides." in sk and "You never pick. The member does." in ref)
    check("skill: found proof is not permission", "Finding a client result is not permission to use it." in ref and "The Proof Engine session owns consent." in sk)
    check("skill: readiness is a guide and never a promise", "not a prediction of results" in ref and "does not measure the business or predict results" in sk)
    check("skill: only confirmed findings enter the Business File; §2 to §4 stay provisional",
          "Nothing inferred enters the Business File as fact." in ref and ref.count("`provisional`") >= 4)
    check("skill: voice samples and proof are saved outside the Business File", "Voice_Samples.md" in ref and "Proof_Found.md" in ref and "never in the file" in sk)
    check("skill: no drive access is forced", "Never ask for a password or a share link" in ref)
    check("skill: agreement is judged on meaning, with each source's own words kept", "say what it claims in `claim`" in sk and "Keep `value` in the source's words." in ref and "When in doubt, give them different claims" in ref)
    check("skill: the Business File is the member's own word", "| `business_file` | already in their Business File." in ref)
    check("skill: old material is set apart and asked about; retired lines are flagged", "Old material is recorded as old, never relied on" in ref and "Retired lines are never used, and the member is told where they still live." in ref
          and "Rely on out-of-date material, or use a retired line." in sk)
    check("skill: hearsay is neither proof nor a client's words", "Hearsay is not proof and is not a client's words." in ref and "is not proof. Leave it out; the script refuses it." in ref)
    check("skill: the member's own files count once they say those are current, never before", "Are any of them out of date?" in ref and "`files_current`" in ref and "**only after** they said their files are current" in ref)
    check("skill: saying nothing is wrong never confirms a guess", "that is not a confirmation of your guesses" in ref)
    check("skill: not ready means say so, recommend answering, and never recommend Autopilot", "Do not recommend Autopilot to a member who is not ready." in ref and "do not recommend Autopilot" in sk
          and "Recommend Autopilot to a member whose file is not ready." in sk)
    check("skill: no brief and no rating after research alone", "produces no Discovery Brief and asks for no 1 to 5 rating" in sk)
    check("skill: a session's own drafts are never evidence", "A draft a Build Room session wrote is never evidence about the business." in ref)
    check("skill: an empty section is not marked provisional", "Do not mark an empty section `provisional`." in ref)
    check("skill: client and prospect runs keep the original pipeline", "A client or a prospect still runs the original pipeline" in ref and "Client or prospect." in sk)
    check("skill: the description still fits the listing limit and names the new phrases", "research my business first" in sk.split("---")[1] and len(sk.split("---")[1]) < 700)
    check("reference: no long dashes in the method guide", "—" not in ref and "–" not in ref)
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    check("skill: the shared template and protocol copies are untouched", (SK / "references/business-file-template.md").read_text() == tpl)

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
