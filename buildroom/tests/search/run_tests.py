#!/usr/bin/env python3
"""Search & Answer Engine tests: the question map, the answer-page gate, schema and robots output, the
profile tracker (check, weekly, reviews, listings), the citation check, and consistency between the
scripts, the references, the template and the rollout docs.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/search/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, re, shutil, subprocess, tempfile  # noqa: E402
from datetime import date, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # buildroom/
SK = ROOT / "skills/buildroom-search-answer-engine"
S = SK / "scripts"
R = SK / "references"
FX = HERE / "fixtures"
PY = sys.executable
QM, AC, PT, CC, PB = S / "question_map.py", S / "answer_check.py", S / "profile_tracker.py", S / "citation_check.py", S / "publish.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:700]}" if detail and not ok else ""))


def run(args, cwd, ok_codes=(0,), env=None):
    e = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    e.update(env or {})
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, env=e)
    return p.returncode in ok_codes, p.stdout + p.stderr, p.returncode


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


def variant(src_text, replacements, cwd, name):
    t = src_text
    for a, b in replacements:
        assert a in t, f"fixture text missing: {a[:50]}"
        t = t.replace(a, b)
    (cwd / name).write_text(t)
    return name


# ---------------------------------------------------------------- question map

def question_map_tests(tmp):
    cwd = tmp / "qm"
    cwd.mkdir()
    ok, out, _ = run([PY, QM, "init", "--business", "Ruiz Advisory"], cwd)
    check("qm init creates folder and file", ok and (cwd / "search/questions.json").exists() and (cwd / "search/answers").is_dir(), out)
    ok, out, _ = run([PY, QM, "init"], cwd, ok_codes=(2,))
    check("qm init refuses to overwrite without --force", ok, out)
    ok, out, _ = run([PY, QM, "init", "--folder", "search-demo"], cwd)
    check("qm --folder works after the command too (Demo mode)", ok and (cwd / "search-demo/questions.json").exists(), out)
    ok, out, _ = run([PY, QM, "add", "What is a 13-week cash flow forecast?", "--intent", "definition", "--cluster", "cash-flow", "--rate", "4,5,3,5,3"], cwd)
    d = pj(out)
    check("qm add rates and scores (4,5,3,5,3 → 83)", ok and d.get("created") and d.get("score") == 83.0 and d["question"]["id"] == "Q-01", out)
    ok, out, _ = run([PY, QM, "add", "what is a 13 week cash flow forecast", "--intent", "definition"], cwd)
    d = pj(out)
    check("qm add detects a duplicate by words", ok and d.get("created") is False and "Q-01" in d.get("note", ""), out)
    ok, out, _ = run([PY, QM, "add", "How much does a bookkeeping clean-up cost?", "--intent", "cost", "--cluster", "pricing", "--rate", "5,5,4,5,2"], cwd)
    check("qm add second question scores 90", ok and pj(out).get("score") == 90.0, out)
    ok, out, _ = run([PY, QM, "add", "Bad rate", "--rate", "6,1,1,1,1"], cwd, ok_codes=(2,))
    check("qm add rejects a mark outside 1..5", ok, out)
    ok, out, _ = run([PY, QM, "add", "What do people in Boise wish they knew about bookkeepers? [hypothesis]", "--intent", "other", "--rate", "5,5,5,5,5", "--source", "Audience Insight [hypothesis]"], cwd)
    d = pj(out)
    check("qm add caps answerable for a [hypothesis] question so it cannot be chosen", ok and d["question"]["scores"]["answerable"] == 40 and "hypothesis" in d["question"]["notes"], out)
    ok, out, _ = run([PY, QM, "import", FX / "questions.txt", "--source", "inbox"], cwd)
    d = pj(out)
    check("qm import adds 3 and skips the duplicate", ok and len(d.get("added", [])) == 3 and len(d.get("skipped_duplicates", [])) == 1, out)
    data = json.loads((cwd / "search/questions.json").read_text())
    q_cash = next(q for q in data["questions"] if q["question"].startswith("How do I set up"))
    q_local = next(q for q in data["questions"] if q["question"].startswith("Do you work"))
    check("qm import reads cluster and intent after |", q_cash["cluster"] == "cash-flow" and q_cash["intent"] == "how-to" and q_local["intent"] == "local", json.dumps(q_cash))
    check("qm imported questions are unrated at 60", not q_cash["rated"] and q_cash["scores"]["answerable"] == 60)
    (cwd / "bom.txt").write_bytes("﻿How much is a service call? | pricing | compar\n".encode("utf-8"))
    ok, out, _ = run([PY, QM, "import", "bom.txt"], cwd)
    d = pj(out)
    check("qm import strips a BOM and reports a mistyped intent", ok and d["added"][0].endswith("How much is a service call?") and d["notes"], out)
    ok, out, _ = run([PY, QM, "next"], cwd)
    d = pj(out)
    check("qm next picks the highest score when no service question exists (the cost question, 90)", ok and d["next"]["id"] == "Q-02" and "highest score" in d["reason"], out)
    ok, out, _ = run([PY, QM, "add", "Bookkeeping clean-up", "--intent", "service", "--cluster", "clean-up", "--rate", "3,5,3,5,2"], cwd)
    ok, out, _ = run([PY, QM, "next"], cwd)
    d = pj(out)
    check("qm next picks the service page first once one is in the map", ok and d["next"]["intent"] == "service" and "service page comes first" in d["reason"], out)
    ok, out, _ = run([PY, QM, "next", "--intent", "how-to"], cwd, ok_codes=(0, 1))
    d = pj(out)
    check("qm next --intent restricts to that intent (how-to is unrated at 60, eligible)", d.get("ok") and d["next"]["intent"] == "how-to", out)
    ok, out, _ = run([PY, QM, "set", "Q-01", "--status", "published"], cwd, ok_codes=(2,))
    check("qm set published needs --url", ok, out)
    ok, out, _ = run([PY, QM, "set", "Q-01", "--status", "published", "--url", "https://example.com/answers/13-week"], cwd)
    d = pj(out)
    check("qm set published records url and date", ok and d["question"]["published_url"].endswith("13-week") and d["question"]["published_on"], out)
    ok, out, _ = run([PY, QM, "set", "Q-01", "--slug", "new-slug"], cwd, ok_codes=(2,))
    check("qm set refuses to re-slug a published question", ok, out)
    ok, out, _ = run([PY, QM, "set", q_cash["id"], "--rate", "4,4,4,5,3"], cwd)
    check("qm set --rate rates an imported question", ok and pj(out)["question"]["rated"], out)
    ok, out, _ = run([PY, QM, "set", "Q-02", "--status", "hold"], cwd)
    ok, out, _ = run([PY, QM, "list", "--status", "hold"], cwd)
    check("qm list filters by status", ok and pj(out)["count"] == 1, out)
    ok, out, _ = run([PY, QM, "md"], cwd)
    md = (cwd / "search/question-map.md").read_text()
    check("qm md writes the map with next, table and clusters", ok and "Next to answer" in md and "| Q-01 |" in md and "cash-flow" in md and "(unrated)" in md, md[:400])
    ok, out, _ = run([PY, QM, "set", "Q-02", "--status", "retired"], cwd)
    ok, out, _ = run([PY, QM, "md"], cwd)
    md = (cwd / "search/question-map.md").read_text()
    check("qm md lists retired questions separately", "## Retired" in md and md.index("## Retired") > md.index("## Ranked"), md[-300:])
    ok, out, _ = run([PY, QM, "score", "--top", "3"], cwd)
    d = pj(out)
    check("qm score ranks and exposes weights", ok and d["weights"]["demand"] == 0.25 and len(d["ranked"]) <= 3, out)
    ok, out, _ = run([PY, QM, "add", "How do I know whether my bookkeeper is doing a good job on the monthly close and what should I ask them each month?", "--intent", "diagnostic"], cwd)
    sl = pj(out)["question"]["slug"]
    check("qm long questions cut the slug at a hyphen", ok and not sl.endswith("-") and len(sl) <= 60 and "-" in sl, sl)
    return cwd


# ---------------------------------------------------------------- answer check

def answer_tests(tmp, qm_cwd):
    cwd = tmp / "ac"
    cwd.mkdir()
    shutil.copytree(qm_cwd / "search", cwd / "search")
    bf = FX / "business-file.md"
    fh = (FX / "good-first-hand.md").read_text()
    ev = (FX / "good-evidence.md").read_text()
    ok, out, _ = run([PY, AC, "check", FX / "good-first-hand.md", "--business-file", bf, "--site", "https://example.com", "--questions", "search/questions.json"], cwd)
    d = pj(out)
    check("ac good first-hand page passes every gate (byline, phone number and '20-minute call' are not claims)", ok and d.get("ok") and all(d["gates"].values()), out[:900])
    check("ac first-hand page: own markers counted, 1 source enough, 2 internal links", d.get("info", {}).get("sources") == 1 and d["info"]["marked_paragraphs"] >= 5 and d["info"]["internal_links"] >= 2, json.dumps(d.get("info")))
    ok, out, _ = run([PY, AC, "check", FX / "good-evidence.md", "--business-file", bf, "--site", "https://example.com", "--questions", "search/questions.json"], cwd)
    d = pj(out)
    check("ac good evidence page (regulated, reviewer, scope note, 3 sources, a cited statistic about owners) passes", ok and d.get("ok"), out[:900])
    check("ac evidence page detects financial hints (two or more) and the scope note", "financial" in d["info"]["regulated_hints"] and d["gates"]["scope_note"], json.dumps(d["info"]))
    ok, out, code = run([PY, AC, "check", FX / "bad-page.md", "--business-file", bf, "--site", "https://example.com"], cwd, ok_codes=(1,))
    d = pj(out)
    f = d.get("fails", {})
    expected = {"front_matter", "direct_answer", "sources", "claims_supported", "original_contribution", "headings", "author", "dates",
                "next_action", "internal_links", "never_say", "no_placeholders"}
    check("ac bad page exits 1 and fails the expected gates", code == 1 and expected <= set(f), f"missing: {expected - set(f)} · got: {sorted(f)}")
    check("ac bad page: the first retired line is read past the template's parenthetical and annotation", "never miss a tax deadline" in f.get("never_say", ""), f.get("never_say"))
    check("ac bad page: [your city] is caught as a placeholder", "[your city]" in f.get("no_placeholders", ""), f.get("no_placeholders"))
    check("ac bad page: dates gate (updated before published)", "before published" in f.get("dates", ""), f.get("dates"))
    check("ac bad page: long sentence warning", any("average sentence" in w for w in d.get("warns", [])), d.get("warns"))
    n = variant(fh, [("Receipts kept nowhere", "Receipts kept nowhere; we are not the cheapest bookkeeper in Boise")], cwd, "sub-bullet.md")
    ok, out, code = run([PY, AC, "check", n, "--business-file", bf, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac a retired line written as a sub-bullet is read", code == 1 and "cheapest bookkeeper" in pj(out)["fails"].get("never_say", ""), out[:300])
    n = variant(fh, [("Receipts kept nowhere", "Receipts kept nowhere, so we rebuild from real numbers")], cwd, "blank-fields.md")
    ok, out, _ = run([PY, AC, "check", n, "--business-file", FX / "business-file-blank.md", "--site", "https://example.com"], cwd)
    check("ac a blank never-say or retired field yields no phrases ('real numbers' passes)", ok and pj(out)["gates"]["never_say"], out[:300])
    n = variant(fh, [("kind: first-hand\n", "kind: first-hand              # evidence | first-hand | service\n"), ("status: ready\n", "status: ready                 # draft | ready | published\n")], cwd, "comments.md")
    ok, out, _ = run([PY, AC, "check", n, "--site", "https://example.com"], cwd)
    check("ac trailing # comments in the front matter are ignored", ok and pj(out)["gates"]["front_matter"], out[:300])
    n = variant(ev, [("This is general information for Idaho residents, not financial or tax advice, and reading it does not make you a client. For your own situation, talk to an accountant who knows it.\n\n", "")], cwd, "no-scope.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    d = pj(out)
    check("ac regulated page without a scope note fails scope_note", code == 1 and "scope_note" in d.get("fails", {}), out[:400])
    check("ac warns when no business file given", any("business-file" in w for w in d.get("warns", [])), d.get("warns"))
    n = variant(ev, [("reviewer: Sam Lee, CPA", "reviewer: none")], cwd, "no-reviewer.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac regulated page without a reviewer fails author", code == 1 and "reviewer" in pj(out).get("fails", {}).get("author", ""), out[:400])
    n = variant(ev, [("reviewer: Sam Lee, CPA", "reviewer: our clinical team")], cwd, "team-reviewer.md")
    ok, out, _ = run([PY, AC, "check", n, "--site", "https://example.com"], cwd)
    check("ac a team as reviewer warns", any("named person" in w for w in pj(out).get("warns", [])), out[:300])
    n = variant(fh, [("reviewer: none\n", "reviewer:\n")], cwd, "blank-reviewer.md")
    ok, out, _ = run([PY, AC, "check", n, "--site", "https://example.com"], cwd)
    check("ac a blank reviewer on an unregulated page is treated as none", ok, out[:300])
    n = variant(ev, [("id: Q-01", "id: Q-77")], cwd, "dup.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com", "--questions", "search/questions.json"], cwd, ok_codes=(1,))
    check("ac duplicate of a published question fails duplicate", code == 1 and "duplicate" in pj(out).get("fails", {}), out[:400])
    n = variant(fh, [("# How much does a bookkeeping clean-up cost for a small business?", "# Clean-up pricing")], cwd, "h1.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac an H1 that differs from the question fails h1", code == 1 and "h1" in pj(out).get("fails", {}), out[:300])
    n = variant(fh, [("## What doubles it?", "A new panel costs $3,100 and the cable another $900, as of 2026.\n\n## What doubles it?")], cwd, "year-exempt.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac a dollar figure with a year in the same paragraph still needs a marker", code == 1 and "claims_supported" in pj(out).get("fails", {}), out[:300])
    n = variant(fh, [("## What doubles it?", "Our clients cut their late fees by 30% after the clean-up [method].\n\n## What doubles it?")], cwd, "method-typical.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac a results claim marked [method] without the typical result fails typical_result", code == 1 and "typical_result" in pj(out).get("fails", {}), out[:300])
    n = variant(fh, [("## What doubles it?", "Clients who finish the clean-up save about $400 a month in late fees [own].\n\n## What doubles it?")], cwd, "own-typical.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac a results claim marked [own] without the typical result fails typical_result", code == 1 and "typical_result" in pj(out).get("fails", {}), out[:300])
    n = variant(fh, [("## What doubles it?", "We counted 38 clients in 2025 [own].\n\n## What doubles it?")], cwd, "count-not-claim.md")
    ok, out, _ = run([PY, AC, "check", n, "--site", "https://example.com"], cwd)
    check("ac a plain count of clients is not a results claim", ok and pj(out)["gates"]["typical_result"], out[:300])
    t = re.sub(r"## How we know.*?(?=## What we'd)", "", fh, flags=re.S)
    (cwd / "no-hwk.md").write_text(t)
    ok, out, code = run([PY, AC, "check", "no-hwk.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac first-hand page without How we know fails how_we_know", code == 1 and "how_we_know" in pj(out).get("fails", {}), out[:400])
    n = variant(fh, [("## What we'd check first", "## Sources (notes)"), ("## Sources\n", "## Sources list\n")], cwd, "no-view.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac 'How we know' alone does not satisfy original_contribution", code == 1 and "original_contribution" in pj(out).get("fails", {}), out[:300])
    n = variant(fh, [("original: Our own 2025 clean-up jobs, counted: the three things that decide the price and the one thing that doubles it.",
                      "original: ‹12 or more words of your own: what this page has that no other page has: your numbers, your rule, your example›")], cwd, "scaffold-left.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    d = pj(out)
    check("ac a scaffold placeholder left in `original` fails original_contribution and no_placeholders", code == 1 and "original_contribution" in d["fails"] and "no_placeholders" in d["fails"], out[:300])
    n = variant(fh, [("S1 | Small business bookkeeping survey | Example Institute | https://example.org/bookkeeping-survey", "S1 | ‹Title of the source› | ‹Publisher› | https://example.org/page")], cwd, "scaffold-source.md")
    ok, out, code = run([PY, AC, "check", n, "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac the scaffold's example source fails sources", code == 1 and "scaffold" in pj(out)["fails"].get("sources", ""), out[:300])
    (cwd / "schema-mismatch.md").write_text(ev + '\n```json\n{"@context":"https://schema.org","@type":"Article","headline":"Something else","author":{"@type":"Person","name":"Dana Ruiz"}}\n```\n')
    ok, out, code = run([PY, AC, "check", "schema-mismatch.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac mismatched schema headline fails schema_match", code == 1 and "schema_match" in pj(out).get("fails", {}), out[:400])
    (cwd / "faq-block.md").write_text(ev + '\n```json\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}\n```\n')
    ok, out, code = run([PY, AC, "check", "faq-block.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac a FAQPage block fails schema_match (retired)", code == 1 and "FAQPage" in pj(out)["fails"].get("schema_match", ""), out[:300])
    n = variant(fh, [("next_action: Book a 20-minute call | /contact", "next_action: Call Dana | tel:+15550100100"), ("*Next step:* [Book a 20-minute call](/contact)", "*Next step:* [Call Dana](tel:+15550100100) or [book a call](/contact)")], cwd, "tel.md")
    ok, out, _ = run([PY, AC, "check", n, "--site", "https://example.com"], cwd)
    check("ac a tel: next action passes", ok and pj(out)["gates"]["next_action"], out[:300])
    # new scaffolds
    ok, out, _ = run([PY, AC, "new", "How long does a clean-up take?", "--slug", "clean-up-time", "--author", "Dana Ruiz", "--credentials", "CPA", "--kind", "first-hand", "--id", "Q-05", "--cluster", "pricing"], cwd)
    f = cwd / "search/answers/clean-up-time.md"
    check("ac new writes a first-hand scaffold with How we know and sentinels", ok and f.exists() and "## How we know" in f.read_text() and "‹" in f.read_text(), out)
    ok, out, code = run([PY, AC, "check", f], cwd, ok_codes=(1,))
    d = pj(out)
    check("ac a fresh scaffold fails on placeholders, not on its own next-step line", code == 1 and "no_placeholders" in d["fails"] and "20-minute" not in d["fails"].get("claims_supported", ""), out[:400])
    ok, out, _ = run([PY, AC, "new", "Bookkeeping clean-up", "--kind", "service", "--author", "Dana Ruiz", "--credentials", "CPA"], cwd)
    f2 = cwd / "search/answers/bookkeeping-clean-up.md"
    t2 = f2.read_text()
    check("ac new --kind service: H1 is the service name and the four questions are the H2s", ok and "# Bookkeeping clean-up\n" in t2 and "## Who is it for?" in t2 and "## What does it cost?" in t2 and "## What happens first?" in t2, out)
    ok, out, _ = run([PY, AC, "new", "How long does a clean-up take?", "--slug", "clean-up-time", "--author", "Dana Ruiz"], cwd, ok_codes=(2,))
    check("ac new refuses to overwrite without --force", ok, out)
    ok, out, _ = run([PY, AC, "new", "Why do my lights dim when the furnace kicks on?", "--author", "Dana Ruiz"], cwd)
    check("ac new makes the same slug as the question map (stop words dropped)", ok and (cwd / "search/answers/lights-dim-furnace-kicks.md").exists(), out)
    sv = t2
    for a, b in [("‹12 or more words of your own: what this page has that no other page has: your numbers, your rule, your example›", "The three questions we ask before quoting and the one that decides the price, from our own jobs."),
                 ("  - S1 | ‹Title of the source› | ‹Publisher› | https://example.org/page | published 2026-01-15 | accessed", "  - S1 | Small business bookkeeping survey | Example Institute | https://example.org/bookkeeping-survey | published 2026-02-10 | accessed"),
                 ("‹Answer in two or three plain sentences, under 100 words: the number or the decision first, then the one condition that changes it.›", "A clean-up takes books that are months behind and makes them right, reconciled to the bank, ready for your tax preparer."),
                 ("‹Two or three plain sentences: what the service is and what it ends with.›", "We rebuild the books from the bank statements and hand back a clean file with every month reconciled."),
                 ("- ‹The person and the situation, in their words from §2.›", "- Owners who are three or more months behind and dread the tax deadline."),
                 ("- ‹Who it is not for.›", "- Not for a business that needs payroll run; we refer that out."),
                 ('‹A real price or range, or how the price is set, with [own]. "Contact us" gives engines nothing to quote.›', "Most clean-ups cost between $900 and $2,400 with us, depending on months behind and accounts involved [own]. See [weekly bookkeeping](/services/weekly-bookkeeping) for what comes after."),
                 ("‹The first step, how long it takes, what the client needs to bring.›", "A 20-minute call, then the last bank statement and the last tax return. We quote within two days."),
                 ("‹At least 40 words of your own: the rule you work by, the mistake you see most, one example from a real job.›", "Our rule is to price the gap between the bank and the last return, not the number of months behind. The mistake we see most is an owner paying a flat monthly fee for a clean-up that never ends. One client had 26 months behind and two entities; the gap was small and so was the price."),
                 ("- [S1] ‹Title of the source, Publisher, 2026.› https://example.org/page", "- [S1] Small business bookkeeping survey, Example Institute, 2026. https://example.org/bookkeeping-survey")]:
        assert a in sv, a[:40]
        sv = sv.replace(a, b)
    (cwd / "service-filled.md").write_text(sv)
    ok, out, _ = run([PY, AC, "check", "service-filled.md", "--site", "https://example.com"], cwd)
    check("ac a filled service page passes (sources optional, H1 = service name)", ok and pj(out)["ok"], out[:900])
    # schema output
    ok, out, _ = run([PY, AC, "schema", FX / "good-evidence.md", "--site", "https://example.com", "--org", "Ruiz Advisory", "--out", "schema.json"], cwd)
    sch = json.loads((cwd / "schema.json").read_text())
    types = [g["@type"] for g in sch["@graph"]]
    art = sch["@graph"][0]
    check("ac schema emits Article + BreadcrumbList and never FAQPage", ok and types == ["Article", "BreadcrumbList"], types)
    check("ac schema Article carries author, reviewer, dates, publisher, url, and a clean description", art["author"]["name"] == "Dana Ruiz" and art["reviewedBy"]["name"].startswith("Sam")
          and art["datePublished"] == "2026-11-10" and art["publisher"]["name"] == "Ruiz Advisory" and art["url"] == "https://example.com/answers/what-is-13-week-cash-flow-forecast"
          and "**" not in art["description"] and "[S1]" not in art["description"] and not art["description"].lower().startswith("short answer"), json.dumps(art)[:400])
    ok, out, _ = run([PY, AC, "schema", FX / "good-evidence.md", "--site", "https://example.com", "--path", "blog/cash-flow"], cwd)
    check("ac schema --path sets the page address", ok and json.loads(out)["@graph"][0]["url"] == "https://example.com/blog/cash-flow", out[:200])
    (cwd / "with-schema.md").write_text(ev + "\n```json\n" + json.dumps(sch) + "\n```\n")
    ok, out, _ = run([PY, AC, "check", "with-schema.md", "--site", "https://example.com"], cwd)
    check("ac a page with its own emitted schema passes schema_match", ok and pj(out)["gates"]["schema_match"], out[:300])
    # robots
    ok, out, _ = run([PY, AC, "robots", "--site", "https://example.com", "--block-training", "--out", "search/robots.txt"], cwd)
    rt = (cwd / "search/robots.txt").read_text()
    check("ac robots --out writes the file; search crawlers and Google-Extended allowed, training blocked when asked",
          ok and "User-agent: OAI-SearchBot\nAllow: /" in rt and "User-agent: Google-Extended\nAllow: /" in rt and "User-agent: GPTBot\nDisallow: /" in rt
          and "User-agent: Meta-WebIndexer\nAllow: /" in rt and rt.rstrip().endswith("https://example.com/sitemap.xml"), rt[:300])
    ok, out, _ = run([PY, AC, "robots"], cwd)
    check("ac robots default allows everything", ok and "Disallow" not in out, out[:200])
    (cwd / "blocked.txt").write_text("User-agent: GPTBot\nUser-agent: OAI-SearchBot\nUser-agent: PerplexityBot\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n\nUser-agent: *\nDisallow: /private/\nAllow: /\n")
    ok, out, code = run([PY, AC, "robots", "--check", "blocked.txt"], cwd, ok_codes=(1,))
    d = pj(out)
    check("ac robots --check names the blocked answer crawlers (a builder's 'block AI bots' switch)", code == 1 and set(d["blocked_search_crawlers"]) == {"OAI-SearchBot", "PerplexityBot"} and "GPTBot" in d["training_crawlers_blocked"], out[:300])
    ok, out, _ = run([PY, AC, "robots", "--check", "search/robots.txt"], cwd)
    check("ac robots --check passes the file it wrote", ok and pj(out)["ok"], out[:200])
    return cwd


# ---------------------------------------------------------------- profile tracker

def profile_tests(tmp):
    cwd = tmp / "pt"
    cwd.mkdir()
    desc = ("Ruiz Advisory keeps the books straight for small construction firms in Boise and the Treasure Valley. Weekly bookkeeping, "
            "clean-ups, a 13-week cash view, and year-end files your CPA will thank you for. In business since 2011. We guarantee a reply within a day.")
    ok, out, _ = run([PY, PT, "init", "--name", "Ruiz Advisory", "--type", "service-area"], cwd, ok_codes=(2,))
    check("pt init requires --legal-name", ok, out)
    ok, out, _ = run([PY, PT, "init", "--name", "Ruiz Advisory", "--legal-name", "Ruiz Advisory LLC", "--type", "service-area", "--category", "Accountant"], cwd)
    check("pt init writes profile.json with the service-area note", ok and (cwd / "search/profile.json").exists() and "hides its address" in out, out)
    ok, out, _ = run([PY, PT, "init", "--name", "X", "--legal-name", "X", "--type", "shop"], cwd, ok_codes=(2,))
    check("pt init rejects an unknown type", ok, out)
    ok, out, _ = run([PY, PT, "check"], cwd, ok_codes=(1,))
    d = pj(out)
    check("pt check on a bare profile: critical fail (not verified, eligibility unsure), score low", d.get("critical_fail") and d.get("score", 100) < 40, out[:300])
    ok, out, _ = run([PY, PT, "set", "reviews_rating=abc"], cwd, ok_codes=(2,))
    check("pt set rejects a non-number for a numeric field (exit 2, no traceback)", ok and "Traceback" not in out, out)
    ok, out, _ = run([PY, PT, "set", "photos_last=yesterday"], cwd, ok_codes=(2,))
    check("pt set rejects a non-date", ok, out)
    ok, out, _ = run([PY, PT, "set", "phone=call me"], cwd, ok_codes=(2,))
    check("pt set rejects a phone with fewer than ten digits", ok, out)
    ok, out, _ = run([PY, PT, "set", "website=example.com"], cwd, ok_codes=(2,))
    check("pt set rejects a website without http", ok, out)
    ok, out, _ = run([PY, PT, "set", "eligible=yes", "owner_verified=yes", "hours_set=yes", "phone=(555) 010-0100", "website=https://example.com",
                      "appointment_url=https://example.com/book", f"description={desc}", "secondary_categories=Bookkeeping service,Tax preparation",
                      "service_area=Boise, Meridian, Nampa", "review_link=https://g.page/r/example/review", "ask_method=text with consent", "ask_timing=same day",
                      "photos_count=12", "nap_address=12 N Main St, Suite 4"], cwd)
    check("pt set accepts plain, nested, list and boolean keys (and the word 'guarantee' in the description)", ok, out)
    ok, out, _ = run([PY, PT, "set", "nonsense=1"], cwd, ok_codes=(2,))
    check("pt set rejects an unknown key", ok, out)
    for name, d_ in (("Bookkeeping clean-up", "For owners whose books are months behind. We rebuild them and hand back a clean file."),
                     ("Weekly bookkeeping", "For firms with staff and suppliers. Books kept current every week."),
                     ("13-week cash view", "For owners who want to see the next quarter. Updated every Monday in twenty minutes.")):
        run([PY, PT, "service", "add", name, "--description", d_], cwd)
    ok, out, _ = run([PY, PT, "service", "add", "Weekly bookkeeping"], cwd, ok_codes=(2,))
    check("pt service add refuses a duplicate", ok, out)
    run([PY, PT, "log", "photo", "--n", "2"], cwd)
    run([PY, PT, "log", "post"], cwd)
    ok, out, _ = run([PY, PT, "log", "review-ask", "--n", "0"], cwd, ok_codes=(2,))
    check("pt log rejects --n 0", ok, out)
    ok, out, _ = run([PY, PT, "log", "review", "--rating", "5", "--note", "Mrs Smith loved it"], cwd, ok_codes=(2,))
    check("pt log refuses a note on a review entry (no names in the folder)", ok, out)
    ok, out, _ = run([PY, PT, "log", "review", "--rating", "6"], cwd, ok_codes=(2,))
    check("pt log rejects a rating outside 1..5", ok, out)
    for i in range(22):
        run([PY, PT, "log", "review", "--rating", "5", "--date", (date.today() - timedelta(days=4 * i)).isoformat(), "--replied"], cwd)
    run([PY, PT, "set", "reviews_rating=4.8"], cwd)
    for i in range(8):
        run([PY, PT, "log", "review-ask", "--n", "2", "--date", (date.today() - timedelta(days=3 * i)).isoformat()], cwd)
    ok, out, _ = run([PY, PT, "check", "--md"], cwd)
    d = pj(out)
    items = {i["key"]: i for i in d["items"]}
    check("pt check: complete profile scores high with no critical fail", ok and not d["critical_fail"] and d["score"] >= 85, f"score {d.get('score')} fix_first {d.get('fix_first')}")
    check("pt check: a photo and a post logged today count as recent (no '0 or 999' bug)", items["photos_recent"]["ok"] and items["post_recent"]["ok"], json.dumps([items["photos_recent"], items["post_recent"]]))
    check("pt check --md writes profile-check.md with fix-first and the groups", (cwd / "search/profile-check.md").exists() and "## Fix first" in (cwd / "search/profile-check.md").read_text() and "| rank |" in (cwd / "search/profile-check.md").read_text())
    check("pt check: reviews_steady passes (asks explain the reviews), reviews_recent and reviews_count pass", items["reviews_steady"]["ok"] and items["reviews_recent"]["ok"] and items["reviews_count"]["ok"])
    order = {"rank": 0, "reviews": 1, "convert": 2, "listings": 3}
    groups = [x["group"] for x in d["fix_first"]]
    check("pt check: listings_core fails with no listings yet, and fix_first is ordered rank → reviews → convert → listings", not items["listings_core"]["ok"] and groups == sorted(groups, key=lambda g: order[g]), d["fix_first"])
    check("pt check: no fix text steers the ask toward happy clients", not any("happy" in i["fix"] for i in d["items"]), [i["fix"] for i in d["items"] if "happy" in i["fix"]])
    for i in range(12):
        run([PY, PT, "log", "review", "--rating", "5", "--replied"], cwd)
    ok, out, _ = run([PY, PT, "check"], cwd)
    items = {i["key"]: i for i in pj(out)["items"]}
    check("pt check: 12 reviews in a week on 16 asks in 30 days is not a burst", items["reviews_steady"]["ok"], items["reviews_steady"])
    for i in range(12):
        run([PY, PT, "log", "review", "--rating", "5", "--replied"], cwd)
    ok, out, _ = run([PY, PT, "check"], cwd)
    items = {i["key"]: i for i in pj(out)["items"]}
    check("pt check: 24 reviews in a week on 16 asks is an unexplained spike", not items["reviews_steady"]["ok"], items["reviews_steady"])
    run([PY, PT, "set", "business=Ruiz Advisory Accountant Boise"], cwd)
    ok, out, code = run([PY, PT, "check"], cwd, ok_codes=(1,))
    d = pj(out)
    items = {i["key"]: i for i in d["items"]}
    check("pt check: a keyword-stuffed name is a critical fail (exit 1)", code == 1 and d["critical_fail"] and not items["real_name"]["ok"], items["real_name"])
    run([PY, PT, "set", "business=Ruiz Advisory"], cwd)
    cwd3 = tmp / "pt3"
    cwd3.mkdir()
    run([PY, PT, "init", "--name", "Best Accountant Near Boise", "--legal-name", "Best Accountant Near Boise", "--type", "service-area", "--category", "Accountant"], cwd3)
    ok, out, _ = run([PY, PT, "check"], cwd3, ok_codes=(1,))
    items = {i["key"]: i for i in pj(out)["items"]}
    check("pt check: a superlative or 'near <City>' in the name is flagged even when the legal name was typed the same way", not items["real_name"]["ok"], items["real_name"])
    run([PY, PT, "log", "review", "--rating", "4"], cwd)
    ok, out, _ = run([PY, PT, "weekly"], cwd)
    tasks = " ".join(pj(out)["tasks"])
    check("pt weekly starts with the open review and asks every client the same way", ok and tasks.startswith("Reply to 1 open review") and "every client" in tasks and "happy" not in tasks, tasks)
    check("pt weekly does not nag for the photo and post logged today", "Add one real photo" not in tasks and "Post one update" not in tasks, tasks)
    run([PY, PT, "log", "reply"], cwd)
    ok, out, _ = run([PY, PT, "weekly"], cwd)
    check("pt weekly drops the reply task once answered", "Reply to" not in " ".join(pj(out)["tasks"]), out)
    cwd4 = tmp / "pt4"
    cwd4.mkdir()
    run([PY, PT, "init", "--name", "Calm Harbor Counseling", "--legal-name", "Calm Harbor Counseling", "--type", "storefront", "--category", "Counselor"], cwd4)
    run([PY, PT, "set", "review_ask=no", "eligible=yes", "owner_verified=yes"], cwd4)
    ok, out, _ = run([PY, PT, "weekly"], cwd4)
    tasks = " ".join(pj(out)["tasks"])
    check("pt review_ask=no: weekly never asks clients for reviews", ok and "No review ask in this profession" in tasks and "Ask every client" not in tasks, tasks)
    ok, out, _ = run([PY, PT, "check"], cwd4, ok_codes=(0, 1))
    keys = {i["key"] for i in pj(out)["items"]}
    check("pt review_ask=no: check scores no ask items", "reviews_count" not in keys and "review_link" not in keys and "review_policy" in keys, keys)
    run([PY, PT, "listings", "add", "--site", "Bing Places", "--url", "https://bing.example/x", "--name", "Ruiz Advisory LLC", "--address", "12 North Main Street #4", "--phone", "+1 555-010-0100", "--status", "live"], cwd)
    run([PY, PT, "listings", "add", "--site", "Yelp", "--name", "Ruiz Advisory", "--address", "12 N Main St, Suite 4", "--phone", "(555) 010-0101", "--status", "live"], cwd)
    ok, out, code = run([PY, PT, "listings", "check"], cwd, ok_codes=(1,))
    d = pj(out)
    check("pt listings check normalises LLC/North/Street/Suite/+1 and flags the wrong phone only",
          code == 1 and len(d["mismatches"]) == 1 and d["mismatches"][0]["site"] == "Yelp" and d["mismatches"][0]["mismatch"] == ["phone"], out[:400])
    check("pt listings check: a listing added today is not stale, and the profile itself is not a 'missing listing'", not d["not_checked_90_days"] and "Google Business Profile" not in d["core_missing"] and "Apple Business" in d["core_missing"], d)
    ok, out, _ = run([PY, PT, "listings", "add", "--site", "Yelp", "--phone", "(555) 010-0100", "--name", "Ruiz Advisory", "--address", "12 N Main St, Suite 4"], cwd)
    ok, out, _ = run([PY, PT, "listings", "check"], cwd)
    check("pt listings add updates an existing site and check passes", ok and not pj(out)["mismatches"], out[:200])
    ok, out, _ = run([PY, PT, "report", "--md"], cwd)
    d = pj(out)
    check("pt report counts reviews, asks and the ask-to-review share and writes md", ok and d["reviews"]["asks_last_30_days"] == 16 and d["ask_to_review"] is not None and (cwd / "search/profile-report.md").exists(), out[:300])
    cwd2 = tmp / "pt2"
    cwd2.mkdir()
    ok, out, _ = run([PY, PT, "init", "--name", "Remote Coach Co", "--legal-name", "Remote Coach Co", "--type", "none"], cwd2)
    check("pt init --type none says to set the phone and website first", ok and "phone" in pj(out)["note"], out)
    run([PY, PT, "listings", "add", "--site", "Facebook page", "--name", "Remote Coach Co", "--phone", "(555) 010-0188", "--status", "live"], cwd2)
    ok, out, _ = run([PY, PT, "listings", "check"], cwd2)
    d = pj(out)
    check("pt type none: listings are the remote set (no Bing Places, Apple or Nextdoor) and an empty profile phone is not a mismatch",
          ok and not d["mismatches"] and "Bing Places" not in d["core_missing"] and "LinkedIn page" in d["core_missing"], d)
    ok, out, _ = run([PY, PT, "check", "--md"], cwd2)
    check("pt check with type none: no profile, listings named, md written", ok and pj(out).get("profile") == "none" and (cwd2 / "search/profile-check.md").exists(), out)
    ok, out, _ = run([PY, PT, "weekly"], cwd2)
    tasks = " ".join(pj(out)["tasks"])
    check("pt weekly with type none gives listing, page, mention and LinkedIn tasks", "listing" in tasks and "answer page" in tasks and "mention" in tasks and "LinkedIn" in tasks, tasks)
    ok, out, _ = run([PY, PT, "--folder", "elsewhere", "init", "--name", "A", "--legal-name", "A", "--type", "hybrid"], cwd2)
    check("pt --folder before the command works; hybrid note names both the address and a service area", ok and "service area" in pj(out)["note"] and (cwd2 / "elsewhere/profile.json").exists(), out)
    return cwd


# ---------------------------------------------------------------- citation check

def citation_tests(tmp, qm_cwd):
    cwd = tmp / "cc"
    cwd.mkdir()
    shutil.copytree(qm_cwd / "search", cwd / "search")
    ok, out, _ = run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "electrician", "--city", "Boise", "--audience", "small construction firms", "--month", "2026-11"], cwd)
    d = pj(out)
    data = json.loads((cwd / "search/checks/2026-11.json").read_text())
    kinds = [p["kind"] for p in data["prompts"]]
    check("cc plan: three engines by default, category then question then brand prompts, two wordings each", ok and d["engines"] == ["google-ai", "chatgpt", "perplexity"]
          and kinds.count("category") == 4 and kinds.count("brand") == 2 and kinds.count("question") >= 2 and all(p["a"] != p["b"] for p in data["prompts"]) and kinds[-1] == "brand", kinds)
    texts = " ".join(p["a"] + " " + p["b"] for p in data["prompts"])
    check("cc plan: a/an chosen by the first letter", "an electrician" in texts and " a electrician" not in texts, texts[:300])
    qs = [p for p in data["prompts"] if p["kind"] == "question"]
    check("cc plan: published questions first, then by score", qs[0]["status"] == "published" and all(qs[i]["score"] >= qs[i + 1]["score"] for i in range(1, len(qs) - 1)), [(q["status"], q["score"]) for q in qs])
    ok, out, _ = run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "electrician", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc plan refuses to rebuild a month without --force", ok, out)
    sys.path.insert(0, str(S))
    import importlib
    pp = importlib.import_module("citation_check").paraphrase
    samples = [pp("How much does it cost to replace an electrical panel?"), pp("Why do my lights dim when the furnace kicks on?"),
               pp("Business coach vs consultant: what's the difference?"), pp("How much does a bookkeeping clean-up cost for a small business?")]
    check("cc paraphrase: cost / why / vs forms read naturally",
          samples == ["What's the typical price to replace an electrical panel?", "What's the reason my lights dim when the furnace kicks on?",
                      "Business coach or consultant: which do I need?", "What's the typical price for a bookkeeping clean-up for a small business?"], samples)
    ok, out, _ = run([PY, CC, "reword", "P-01", "--b", "Which electrician in Boise would you call?", "--month", "2026-11"], cwd)
    check("cc reword replaces a wording", ok and pj(out)["prompt"]["b"].startswith("Which electrician"), out)
    ok, out, _ = run([PY, CC, "prompts", "--month", "2026-11"], cwd)
    md = (cwd / "search/checks/2026-11-prompts.md").read_text()
    check("cc prompts writes the checklist with the planned engines as columns", ok and "| google-ai | chatgpt | perplexity |" in md and "| P-01 |" in md, md[:400])
    ok, out, _ = run([PY, CC, "log", "P-99", "--engine", "chatgpt", "--result", "own", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects a prompt not in the plan", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "bing", "--result", "own", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects an unknown engine", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "chatgpt", "--result", "own", "--run", "0", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects --run 0", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "chatgpt", "--result", "own", "--date", "yesterday", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects a bad --date", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "gemini", "--result", "none", "--month", "2026-11"], cwd)
    check("cc log accepts an engine outside the plan's default three", ok, out)
    filled = []
    for line in md.splitlines():
        if line.startswith("| P-01 |"):
            line = line.rsplit("|", 4)[0] + "| profile/none | competitor | none |"
        elif line.startswith("| P-02 |"):
            line = line.rsplit("|", 4)[0] + "| none | competitor |  |"
        elif line.startswith("| P-05 |"):
            line = line.rsplit("|", 4)[0] + "| own | own/named | named |"
        elif line.startswith("| P-06 |"):
            line = line.rsplit("|", 4)[0] + "|  | banana |  |"
        filled.append(line)
    (cwd / "search/checks/2026-11-prompts.md").write_text("\n".join(filled))
    ok, out, _ = run([PY, CC, "log", "--from", "search/checks/2026-11-prompts.md", "--month", "2026-11"], cwd)
    d = pj(out)
    check("cc log --from reads the table (a/b cells), reports a bad word and keeps the rest", d.get("logged") == 10 and len(d.get("problems", [])) == 1 and "banana" in d["problems"][0], out[:400])
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "google-ai", "--result", "own", "--variant", "a", "--run", "1", "--month", "2026-11"], cwd)
    check("cc log replaces the same prompt/variant/run/engine entry", ok and pj(out)["results_so_far"] == 11, out)
    brand_id = [p["id"] for p in data["prompts"] if p["kind"] == "brand"][0]
    run([PY, CC, "log", brand_id, "--engine", "chatgpt", "--result", "none", "--month", "2026-11"], cwd)
    ok, out, _ = run([PY, CC, "report", "--month", "2026-11", "--md"], cwd)
    d = pj(out)
    g = d["by_engine"]["google-ai"]
    check("cc report: google-ai tried 3 customer prompts, seen 2", g["prompts_tried"] == 3 and g["prompts_seen"] == 2, json.dumps(g))
    check("cc report: headline share counts customer prompts only; a brand prompt that did not find the business is listed",
          d["prompts_tried"] == 3 and d["prompts_seen"] == 2 and d["share_seen"] == 0.67 and d["brand"]["tried"] == 1 and d["brand"]["seen"] == 0 and d["brand"]["not_found"] == [brand_id],
          json.dumps({k: d[k] for k in ("prompts_tried", "prompts_seen", "share_seen", "brand")}))
    check("cc report lists never-seen prompts and writes markdown with the engine table", {x["id"] for x in d["never_seen"]} == {"P-02"} and "| google-ai |" in (cwd / "search/checks/2026-11-report.md").read_text(), d["never_seen"])
    run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "electrician", "--city", "Boise", "--month", "2026-12"], cwd)
    run([PY, CC, "log", "P-01", "--engine", "chatgpt", "--result", "own", "--month", "2026-12"], cwd)
    ok, out, _ = run([PY, CC, "report", "--month", "2026-12"], cwd)
    d = pj(out)
    check("cc report compares with the previous month", ok and d.get("previous", {}).get("month") == "2026-11" and "change" in d, out[:300])
    cwd2 = tmp / "cc2"
    cwd2.mkdir()
    run([PY, QM, "init"], cwd2)
    for q in ("What does a business coach do?", "How much does business coaching cost?", "Should I hire a business coach or a consultant?"):
        run([PY, QM, "add", q, "--rate", "4,4,4,5,3"], cwd2)
    ok, out, _ = run([PY, CC, "plan", "--business", "Harbor Coaching", "--category", "business coach", "--audience", "owners of trades businesses", "--month", "2026-11"], cwd2)
    data = json.loads((cwd2 / "search/checks/2026-11.json").read_text())
    customer = [p for p in data["prompts"] if p["kind"] != "brand"]
    check("cc plan without --city: choose, cost, audience and remote prompts, 8+ customer prompts from three questions", ok and len(customer) >= 8 and any("remotely" in p["a"] for p in customer) and any("How do I choose a business coach?" == p["a"] for p in customer), [p["a"] for p in customer])
    ok, out, _ = run([PY, CC, "--folder", "search", "plan", "--business", "Harbor Coaching", "--category", "business coach", "--month", "2026-12", "--all-engines"], cwd2)
    check("cc plan --all-engines plans five engines; --folder before the command works", ok and len(pj(out)["engines"]) == 5, out)
    return cwd



# ---------------------------------------------------------------- publish (a local fake of the builders' APIs and a live site)

class _Fake(__import__("http.server").server.BaseHTTPRequestHandler):
    """WordPress pages API, IndexNow, Wix/Webflow/Shopify endpoints, and a small live site for verify."""
    seen = []
    key = "k" * 32
    page_html = ""
    robots = "User-agent: *\nAllow: /\n"
    noindex = False

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/wp-json/wp/v2/pages":
            return self._send(200, "[]")
        if path == f"/{self.key}.txt":
            return self._send(200, self.key, "text/plain")
        if path == "/robots.txt":
            return self._send(200, self.robots, "text/plain")
        if path == "/sitemap.xml":
            return self._send(200, '<?xml version="1.0"?><sitemapindex><sitemap><loc>http://127.0.0.1:%d/sitemap-pages.xml</loc></sitemap></sitemapindex>' % self.server.server_port, "application/xml")
        if path == "/sitemap-pages.xml":
            return self._send(200, '<urlset><url><loc>http://127.0.0.1:%d/answers/bookkeeping-clean-up-cost</loc></url></urlset>' % self.server.server_port, "application/xml")
        if path == "/answers/bookkeeping-clean-up-cost":
            meta = '<meta name="robots" content="noindex">' if self.noindex else ""
            return self._send(200, f'<html><head><title>Bookkeeping clean-up cost</title>{meta}<link rel="canonical" href="http://127.0.0.1:{self.server.server_port}/answers/bookkeeping-clean-up-cost"></head><body><h1>How much</h1><p>between $900 and $2,400 with us</p></body></html>', "text/html")
        return self._send(404, "{}")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        _Fake.seen.append({"path": self.path, "headers": dict(self.headers), "body": body})
        if self.path.startswith("/wp-json/wp/v2/pages"):
            if not self.headers.get("Authorization", "").startswith("Basic "):
                return self._send(401, '{"message":"no auth"}')
            return self._send(201, json.dumps({"id": 7, "link": f"http://127.0.0.1:{self.server.server_port}/{body.get('slug')}"}))
        if self.path == "/indexnow":
            if body.get("key") != self.key:
                return self._send(403, '{"error":"bad key"}')
            return self._send(202, "")
        if self.path.startswith("/blog/v3/draft-posts"):
            return self._send(200, json.dumps({"draftPost": {"id": "x", "url": {"url": f"http://127.0.0.1:{self.server.server_port}/post/{body['draftPost']['slug']}"}}}))
        if self.path.startswith("/v2/collections/"):
            return self._send(202, json.dumps({"id": "item1"}))
        if self.path.startswith("/admin/api/"):
            return self._send(201, json.dumps({"page": {"id": 1, "handle": body["page"]["handle"]}}))
        return self._send(404, "{}")


def publish_tests(tmp):
    import threading
    from http.server import HTTPServer
    srv = HTTPServer(("127.0.0.1", 0), _Fake)
    port = srv.server_port
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    env = {"BUILDROOM_TEST_ENDPOINT": base}
    cwd = tmp / "pb"
    (cwd / "search/answers").mkdir(parents=True)
    page = cwd / "search/answers/bookkeeping-clean-up-cost.md"
    page.write_text((FX / "good-first-hand.md").read_text())
    shutil.copy(FX / "questions.txt", cwd / "q.txt")
    run([PY, QM, "init"], cwd)
    run([PY, QM, "add", "What is a 13-week cash flow forecast?", "--intent", "definition", "--rate", "4,5,3,5,3"], cwd)
    run([PY, QM, "add", "How much does a bookkeeping clean-up cost for a small business?", "--intent", "cost", "--rate", "5,5,4,5,2"], cwd)
    # keys: names only, never values
    (cwd / ".env").write_text("WP_USER=dana\nWP_APP_PASSWORD=abcd efgh ijkl mnop\n# comment\nexport WIX_API_KEY='wixsecretvalue123'\n")
    ok, out, _ = run([PY, PB, "keys"], cwd)
    d = pj(out)
    check("pb keys lists set keys by name, unlocks wordpress, and never prints a value", ok and d["keys_set"] == ["WIX_API_KEY", "WP_APP_PASSWORD", "WP_USER"] and d["builders_unlocked"] == ["wordpress"]
          and "abcd" not in out and "wixsecret" not in out, out[:300])
    # render
    (cwd / "search/answers/bookkeeping-clean-up-cost.jsonld").write_text('{"@context":"https://schema.org","@type":"Article","headline":"Bookkeeping clean-up cost for a small business"}')
    ok, out, _ = run([PY, PB, "render", "search/answers/bookkeeping-clean-up-cost.md", "--site", "https://example.com", "--schema", "search/answers/bookkeeping-clean-up-cost.jsonld"], cwd)
    h = (cwd / "search/answers/bookkeeping-clean-up-cost.html").read_text()
    check("pb render writes HTML with title, description, canonical, schema, H1 and H2 ids", ok and "<title>Bookkeeping clean-up cost for a small business</title>" in h and 'rel="canonical" href="https://example.com/answers/bookkeeping-clean-up-cost"' in h
          and "application/ld+json" in h and "<h1>How much does a bookkeeping clean-up cost" in h and '<h2 id="what-doubles-it">' in h, h[:400])
    check("pb render strips [own]/[method], turns [S1] into a footnote link, and keeps the list and the next-step link", "[own]" not in h and "[method]" not in h
          and '<li id="source-1">' in h and "<ul><li>A second company" in h and '<a href="/contact">Book a 20-minute call</a>' in h, h[-600:])
    pc = (cwd / "search/answers/bookkeeping-clean-up-cost-paste.md").read_text()
    check("pb render writes the paste checklist with the address, title, H1 and the Search Console step", "answers/bookkeeping-clean-up-cost" in pc and "Request indexing" in pc and "H1" in pc, pc[:300])
    ok, out, _ = run([PY, PB, "render", FX / "bad-page.md"], cwd, ok_codes=(2,))
    check("pb render refuses a page whose status is still draft", ok, out)
    # table rendering
    tpage = cwd / "search/answers/t.md"
    tpage.write_text((FX / "good-evidence.md").read_text())
    run([PY, PB, "render", "search/answers/t.md"], cwd)
    th = (cwd / "search/answers/what-is-13-week-cash-flow-forecast.html").read_text()
    check("pb render turns a pipe table into a table with a header row", "<table><thead><tr><th>Row</th><th>What it holds</th></tr></thead>" in th and "<td>Cash in</td>" in th, th[:300])
    # wordpress publish against the fake, then dry-run masking
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "wordpress", "--site", base], cwd, env=env)
    d = pj(out)
    sent = [s for s in _Fake.seen if s["path"].startswith("/wp-json")]
    check("pb publish wordpress posts the page with Basic auth, slug, title and content, and returns the link",
          ok and d["ok"] and d["url"].endswith("/bookkeeping-clean-up-cost") and sent and sent[-1]["headers"]["Authorization"].startswith("Basic ")
          and sent[-1]["body"]["slug"] == "bookkeeping-clean-up-cost" and sent[-1]["body"]["status"] == "publish" and "<h2" in sent[-1]["body"]["content"], out[:400])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "wordpress", "--site", base, "--draft", "--dry-run"], cwd, env=env)
    check("pb publish --dry-run shows the request with the password masked and a draft status", ok and pj(out)["dry_run"] and "abcd efgh" not in out and "•••" in out and "draft" in out, out[:400])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "shopify", "--site", base], cwd, env=env, ok_codes=(2,))
    check("pb publish refuses a builder whose keys are missing, naming them, without printing any value", ok and "SHOPIFY_STORE" in out and "abcd" not in out, out[:200])
    (cwd / ".env").write_text("WP_USER=dana\nWP_APP_PASSWORD=abcd efgh ijkl mnop\nWIX_API_KEY=wixsecretvalue123\nWIX_SITE_ID=site1\nWEBFLOW_API_TOKEN=wf-token-value-1\nWEBFLOW_COLLECTION_ID=coll1\nSHOPIFY_STORE=shop.myshopify.com\nSHOPIFY_ACCESS_TOKEN=shpat_secretvalue\n")
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "wix", "--site", base, "--dry-run"], cwd, env=env)
    d = pj(out)
    body = d["request"]["body"]
    types = [n["type"] for n in body["draftPost"]["richContent"]["nodes"]]
    check("pb publish wix --dry-run builds rich content (paragraphs, headings, a bulleted list) and masks the key",
          ok and "PARAGRAPH" in types and "HEADING" in types and "BULLETED_LIST" in types and "wixsecret" not in out and d["request"]["headers"]["Authorization"] == "•••", out[:300])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "wix", "--site", base], cwd, env=env)
    check("pb publish wix posts a draft post and publishes it, returning the post url", ok and pj(out)["url"].endswith("/post/bookkeeping-clean-up-cost") and _Fake.seen[-1]["body"]["publish"] is True, out[:300])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "webflow", "--site", base], cwd, env=env)
    check("pb publish webflow posts a live CMS item with name, slug and post-body", ok and _Fake.seen[-1]["path"] == "/v2/collections/coll1/items/live" and _Fake.seen[-1]["body"]["fieldData"]["slug"] == "bookkeeping-clean-up-cost", out[:300])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "shopify", "--site", base], cwd, env=env)
    check("pb publish shopify posts a page with the handle and the access-token header", ok and _Fake.seen[-1]["path"].startswith("/admin/api/") and _Fake.seen[-1]["headers"].get("X-Shopify-Access-Token") == "shpat_secretvalue"
          and _Fake.seen[-1]["body"]["page"]["handle"] == "bookkeeping-clean-up-cost", out[:300])
    ok, out, _ = run([PY, PB, "publish", "search/answers/bookkeeping-clean-up-cost.md", "--builder", "manual", "--site", "https://example.com"], cwd)
    check("pb publish manual writes the HTML and the checklist and names the builders without an API", ok and "Squarespace" in pj(out)["note"] and (cwd / "search/answers/bookkeeping-clean-up-cost-paste.md").exists(), out[:300])
    # indexnow
    ok, out, _ = run([PY, PB, "indexnow", f"{base}/answers/bookkeeping-clean-up-cost"], cwd, env=env, ok_codes=(2,))
    check("pb indexnow without a key says to run indexnow-key", ok, out)
    (cwd / ".env").write_text((cwd / ".env").read_text() + f"INDEXNOW_KEY={_Fake.key}\n")
    ok, out, _ = run([PY, PB, "indexnow-key", "--site", base], cwd)
    d = pj(out)
    check("pb indexnow-key writes the key file to upload and names its address", ok and (cwd / d["key_file"]).exists() and d["upload_to"].endswith(f"/{_Fake.key}.txt"), out)
    ok, out, _ = run([PY, PB, "indexnow", f"{base}/answers/bookkeeping-clean-up-cost"], cwd, env=env)
    sent = [s for s in _Fake.seen if s["path"] == "/indexnow"][-1]["body"]
    check("pb indexnow checks the live key file, then posts host, key, keyLocation and urlList; 202 is accepted",
          ok and pj(out)["ok"] and sent["key"] == _Fake.key and sent["urlList"] == [f"{base}/answers/bookkeeping-clean-up-cost"] and sent["keyLocation"].endswith(".txt"), out[:300])
    (cwd / ".env").write_text((cwd / ".env").read_text().replace(_Fake.key, "wrongkey" + "0" * 24))
    ok, out, _ = run([PY, PB, "indexnow", f"{base}/answers/bookkeeping-clean-up-cost", "--skip-key-check"], cwd, env=env, ok_codes=(1,))
    check("pb indexnow reports a refused ping (403) as not ok", ok and not pj(out)["ok"], out[:200])
    # verify
    ok, out, _ = run([PY, PB, "verify", f"{base}/answers/bookkeeping-clean-up-cost", "--expect", "between $900 and $2,400"], cwd, env=env)
    d = pj(out)
    check("pb verify: live, H1, no noindex, canonical, title, expected text, crawlers allowed, in the sitemap index", ok and d["ok"] and all(d["checks"].values()), out[:500])
    _Fake.noindex = True
    _Fake.robots = "User-agent: OAI-SearchBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n"
    ok, out, _ = run([PY, PB, "verify", f"{base}/answers/bookkeeping-clean-up-cost"], cwd, env=env, ok_codes=(1,))
    d = pj(out)
    check("pb verify fails on noindex and on a blocked answer crawler, with plain notes", not d["ok"] and not d["checks"]["no_noindex"] and not d["checks"]["answer_crawlers_allowed"] and any("noindex" in n for n in d["notes"]) and any("OAI-SearchBot" in n for n in d["notes"]), out[:400])
    _Fake.noindex = False
    _Fake.robots = "User-agent: *\nAllow: /\n"
    ok, out, _ = run([PY, PB, "verify", f"{base}/answers/missing"], cwd, env=env, ok_codes=(1,))
    check("pb verify fails a page that is not live", not pj(out)["checks"]["live_200"], out[:200])
    check("pb verify names Google's route as the member's click, not an API", "Request indexing" in pj(out)["google"] and "no legitimate API" in pj(out)["google"])
    # record
    ok, out, _ = run([PY, PB, "record", "search/answers/bookkeeping-clean-up-cost.md", "--url", f"{base}/answers/bookkeeping-clean-up-cost", "--questions", "search/questions.json"], cwd)
    t = page.read_text()
    q = json.loads((cwd / "search/questions.json").read_text())["questions"]
    check("pb record sets status published and url in the page, and marks the question published", ok and "status: published" in t and f"url: {base}/answers/bookkeeping-clean-up-cost" in t
          and any(x["id"] == "Q-02" and x["status"] == "published" and x["published_url"].endswith("cost") for x in q), out[:300])
    check("pb no secret value reached a file the skill writes", not any(("abcd efgh" in p.read_text(errors="ignore")) for p in (cwd / "search").rglob("*") if p.is_file()))
    srv.shutdown()
    return cwd


# ---------------------------------------------------------------- consistency between scripts, references, template and docs

def consistency_tests():
    ac = (S / "answer_check.py").read_text()
    std = (R / "answer-standard.md").read_text()
    gate_names = re.findall(r'"([a-z_0-9]+)"', re.search(r"GATES = \((.*?)\)", ac, re.S).group(1))
    doc_gates = re.findall(r"^\| `([a-z_0-9]+)` \|", std, re.M)
    check("answer-standard.md gate table matches the script's gates", set(doc_gates) == set(gate_names), set(doc_gates) ^ set(gate_names))
    crawlers = re.findall(r'"([A-Za-z-]+)"', re.search(r"SEARCH_CRAWLERS = \((.*?)\)", ac, re.S).group(1))
    site = (R / "site-and-platforms.md").read_text()
    missing = [c for c in crawlers if c not in std or c not in site]
    check("search crawlers in the script appear in answer-standard.md and site-and-platforms.md", not missing, missing)
    sp_ = (R / "search-principles.md").read_text()
    check("Google-Extended is described as grounding, not harmless to block, in the standard and the principles",
          "Google-Extended" in std and "grounding" in std.split("Google-Extended")[1][:400] and "grounding" in sp_.split("Google-Extended")[1][:300])
    pt = (S / "profile_tracker.py").read_text()
    rl = (R / "reviews-and-listings.md").read_text()
    for const in ("CORE_LISTINGS", "CORE_LISTINGS_REMOTE"):
        core = re.findall(r'"([A-Za-z ]+)"', re.search(const + r" = \((.*?)\)", pt, re.S).group(1))
        missing = [c for c in core if c not in rl]
        check(f"{const} entries appear in reviews-and-listings.md", not missing, missing)
    for phrase in ("happy client", "if you were happy", "two to four asks a week", "two to four recent clients"):
        hits = [str(p.relative_to(SK)) for p in list(R.glob("*.md")) + [SK / "SKILL.md"] + list(S.glob("*.py")) if phrase in p.read_text().lower()]
        check(f"no gating language anywhere: '{phrase}'", not hits, hits)
    qm = (S / "question_map.py").read_text()
    w = dict(re.findall(r'"(\w+)": (0\.\d+)', re.search(r"WEIGHTS = \{(.*?)\}", qm).group(1)))
    check("question weights are the founder's (25/25/20/20/10)", w == {"demand": "0.25", "value": "0.25", "gap": "0.20", "answerable": "0.20", "fresh": "0.10"}, w)
    qmd = (R / "question-map.md").read_text()
    check("question-map.md states the weights and the service-first rule, with no fixed definition-first order", "demand 25%, value 25%, gap 20%, answerable 20%, freshness 10%" in qmd
          and "service" in qmd and "definition, how-to, then compare" not in qmd.lower())
    mm = (R / "measure-and-maintain.md").read_text()
    check("measure-and-maintain.md describes the lighter check (three engines by default, log --from)", "Gemini and Copilot" in mm and "--from" in mm and "ten prompts" in mm.lower())
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    sec = re.search(r"## 21\. Search & Answer Presence(.*?)\n---", tpl, re.S).group(1)
    fields = re.findall(r"- \*\*([^*]+)\*\*", sec)
    skill = (SK / "SKILL.md").read_text()
    phase7 = skill[skill.index("### Phase 7"):]
    missing = [f for f in fields if f.split(" (")[0].lower().replace("search folder:", "folder") not in phase7.lower()]
    check("§21 template fields are all named in SKILL.md Phase 7", not missing, missing)
    check("§21 header names the skill and its requirements", "Built by: Search & Answer Engine · Requires: §1, §2; best with §3, §4, §14, §18" in sec)
    copies = [p for p in (ROOT / "skills").glob("*/references/business-file-template.md")]
    bad = [str(p) for p in copies if p.read_text() != tpl]
    check(f"every skill's template copy matches the canonical template ({len(copies)} copies)", not bad, bad[:3])
    proto = (ROOT / "shared/business-file-protocol.md").read_text()
    check("the skill's protocol copy is byte-identical", (R / "business-file-protocol.md").read_text() == proto)
    for f in ("kern-framework.md", "halbert-writing-system.md"):
        check(f"{f} is byte-identical to the Copy Engine's", (R / f).read_bytes() == (ROOT / "skills/buildroom-copy-engine/references" / f).read_bytes())
    desc = re.search(r"description: \|\n((?:  .*\n)+)", skill).group(1)
    desc = " ".join(l.strip() for l in desc.splitlines())
    check("SKILL.md description is 200 to 1,024 characters with the trigger phrases the roadmap hands out",
          200 <= len(desc) <= 1024 and '"get found on Google,"' in desc and "search week" in desc.lower() and "what should i write about" in desc.lower(), len(desc))
    refs = set(re.findall(r"`references/([\w-]+\.md)`", skill))
    missing = [r for r in refs if not (R / r).exists()]
    check("every reference named in SKILL.md exists", not missing, missing)
    unlisted = [p.name for p in R.glob("*.md") if p.name not in refs and p.name != "business-file-template.md"]
    check("every reference file is named in SKILL.md", not unlisted, unlisted)
    missing = [s for s in ("question_map.py", "answer_check.py", "profile_tracker.py", "citation_check.py", "publish.py") if s not in skill]
    check("every script is named in SKILL.md", not missing, missing)
    check("SKILL.md: Profile, Reviews and Listings modes need §1 only; the time claim is about three hours", "§1 only" in skill and "about three hours" in skill)
    for term in ("llms.txt", "FAQ rich results", "Q&A", "star markup", "templated city pages"):
        check(f"search-principles.md names retired advice: {term}", term.lower() in sp_.lower())
    check("search-principles.md attributes the YouTube figures to Pew 2025 and the chatbot figures to Pew 2026", "Pew, February 2025" in sp_ and "Pew, February 2026" in sp_)
    check("the four-to-eight-week profile clock is hedged as unmeasured", "nobody has measured" in mm)
    sitep = (R / "site-and-platforms.md").read_text()
    check("site-and-platforms.md explains publishing by API vs paste, IndexNow, and that Google indexing is the member's click", "publish.py" in sitep and "IndexNow" in sitep and "Request indexing" in sitep and "no legitimate api" in sitep.lower())
    pbdoc = (S / "publish.py").read_text()
    check("publish.py never prints a key: every error and dry run goes through mask()", "mask(" in pbdoc and "print(env" not in pbdoc and 'print(key' not in pbdoc)
    cl2 = (ROOT / "rollout/universal/CLAUDE.md").read_text()
    check("CLAUDE.md names the publishing keys as .env keys", "WP_APP_PASSWORD" in cl2 and "INDEXNOW_KEY" in cl2)
    pp_ = (ROOT / "skills/buildroom-proof-engine/references/proof-playbook.md").read_text()
    check("the Proof Engine's placement table has a row for answer pages", "Answer pages" in pp_ and "Search & Answer Engine" in pp_)
    cl = (ROOT / "rollout/universal/CLAUDE.md").read_text()
    sh = (ROOT / "rollout/universal/START-HERE.md").read_text()
    check("CLAUDE.md and START-HERE count the sections as §1–§21 / twenty-one", "§1–§21" in cl and "twenty-one sections" in sh)
    hits = []
    for p in list(SK.rglob("*")) + list(HERE.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".py", ".txt", ".json"):
            t = p.read_text(errors="ignore")
            if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t):
                hits.append(f"{p.name}: an email address")
            if re.search(r"\b(sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{12,}|xox[bp]-)", t):
                hits.append(f"{p.name}: a key")
            if re.search(r"\bLanny\b|\bMorton\b", t):
                hits.append(f"{p.name}: the founder's name")
    check("confidentiality: no email addresses, keys or personal names in the skill, tests or fixtures", not hits, hits)
    for sc, cmds in ((QM, ("init", "add", "import", "score", "next", "set", "list", "md")), (AC, ("new", "check", "schema", "robots")),
                     (PT, ("init", "set", "service", "log", "check", "weekly", "listings", "report")), (CC, ("plan", "prompts", "reword", "log", "report")),
                     (PB, ("keys", "render", "publish", "indexnow-key", "indexnow", "verify", "record"))):
        doc = sc.read_text().split('"""')[1]
        missing = [c for c in cmds if f"{sc.name} {c}" not in doc]
        check(f"{sc.name} docstring shows every command", not missing, missing)


def main():
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="search-tests-"))
    try:
        qm_cwd = question_map_tests(tmp)
        answer_tests(tmp, qm_cwd)
        profile_tests(tmp)
        citation_tests(tmp, qm_cwd)
        publish_tests(tmp)
        consistency_tests()
    finally:
        if keep:
            print(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} passed")
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
