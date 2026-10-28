#!/usr/bin/env python3
"""Search & Answer Engine tests: the question map, the answer-page gate, schema and robots output, the
profile tracker (check, weekly, reviews, listings), the citation check, and consistency between the
scripts and the references.

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
QM, AC, PT, CC = S / "question_map.py", S / "answer_check.py", S / "profile_tracker.py", S / "citation_check.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:700]}" if detail and not ok else ""))


def run(args, cwd, ok_codes=(0,)):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    return p.returncode in ok_codes, p.stdout + p.stderr, p.returncode


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


# ---------------------------------------------------------------- question map

def question_map_tests(tmp):
    cwd = tmp / "qm"
    cwd.mkdir()
    ok, out, _ = run([PY, QM, "init", "--business", "Ruiz Advisory"], cwd)
    check("qm init creates folder and file", ok and (cwd / "search/questions.json").exists() and (cwd / "search/answers").is_dir(), out)
    ok, out, _ = run([PY, QM, "init"], cwd, ok_codes=(2,))
    check("qm init refuses to overwrite without --force", ok, out)
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
    ok, out, _ = run([PY, QM, "import", FX / "questions.txt", "--source", "inbox"], cwd)
    d = pj(out)
    check("qm import adds 3 and skips the duplicate", ok and len(d.get("added", [])) == 3 and len(d.get("skipped_duplicates", [])) == 1, out)
    data = json.loads((cwd / "search/questions.json").read_text())
    q_cash = next(q for q in data["questions"] if q["question"].startswith("How do I set up"))
    q_local = next(q for q in data["questions"] if q["question"].startswith("Do you work"))
    check("qm import reads cluster and intent after |", q_cash["cluster"] == "cash-flow" and q_cash["intent"] == "how-to" and q_local["intent"] == "local", json.dumps(q_cash))
    check("qm imported questions are unrated at 60", not q_cash["rated"] and q_cash["scores"]["answerable"] == 60)
    ok, out, _ = run([PY, QM, "next"], cwd)
    d = pj(out)
    check("qm next picks the definition question first (founder's order)", ok and d["next"]["id"] == "Q-01" and "definition" in d["reason"], out)
    ok, out, _ = run([PY, QM, "set", "Q-01", "--status", "published"], cwd, ok_codes=(2,))
    check("qm set published needs --url", ok, out)
    ok, out, _ = run([PY, QM, "set", "Q-01", "--status", "published", "--url", "https://example.com/answers/13-week"], cwd)
    d = pj(out)
    check("qm set published records url and date", ok and d["question"]["published_url"].endswith("13-week") and d["question"]["published_on"], out)
    ok, out, _ = run([PY, QM, "set", q_cash["id"], "--rate", "4,4,4,5,3"], cwd)
    check("qm set --rate rates an imported question", ok and pj(out)["question"]["rated"], out)
    ok, out, _ = run([PY, QM, "next"], cwd)
    d = pj(out)
    check("qm next picks the how-to second", ok and d["next"]["id"] == q_cash["id"] and "how-to" in d["reason"], out)
    ok, out, _ = run([PY, QM, "set", q_cash["id"], "--status", "published", "--url", "https://example.com/a/cash"], cwd)
    ok, out, _ = run([PY, QM, "next"], cwd)
    d = pj(out)
    check("qm next picks compare third when a compare question is rated", False if not ok else True, out)
    # the compare question is unrated (60, eligible) so it should be picked
    check("qm next third is the compare question", ok and d["next"]["question"].startswith("Bookkeeper vs"), out)
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
    return cwd


# ---------------------------------------------------------------- answer check

def answer_tests(tmp, qm_cwd):
    cwd = tmp / "ac"
    cwd.mkdir()
    shutil.copytree(qm_cwd / "search", cwd / "search")
    bf = FX / "business-file.md"
    ok, out, _ = run([PY, AC, "check", FX / "good-first-hand.md", "--business-file", bf, "--site", "https://example.com", "--questions", "search/questions.json"], cwd)
    d = pj(out)
    check("ac good first-hand page passes every gate", ok and d.get("ok") and all(d["gates"].values()), out[:900])
    check("ac first-hand page: own markers counted, 1 source enough", d.get("info", {}).get("sources") == 1 and d["info"]["marked_sentences"] >= 5, json.dumps(d.get("info")))
    ok, out, _ = run([PY, AC, "check", FX / "good-evidence.md", "--business-file", bf, "--site", "https://example.com", "--questions", "search/questions.json"], cwd)
    d = pj(out)
    check("ac good evidence page (regulated, reviewer, scope note, 3 sources) passes", ok and d.get("ok"), out[:900])
    check("ac evidence page detects financial hints and the scope note", "financial" in d["info"]["regulated_hints"] and d["gates"]["scope_note"], json.dumps(d["info"]))
    ok, out, code = run([PY, AC, "check", FX / "bad-page.md", "--business-file", bf, "--site", "https://example.com"], cwd, ok_codes=(1,))
    d = pj(out)
    f = d.get("fails", {})
    expected = {"front_matter", "direct_answer", "sources", "claims_supported", "original_contribution", "headings", "author", "dates",
                "next_action", "internal_links", "never_say", "no_placeholders"}
    check("ac bad page exits 1 and fails the expected gates", code == 1 and expected <= set(f), f"missing: {expected - set(f)} · got: {sorted(f)}")
    check("ac bad page: never-say and retired line both caught", "never miss a tax deadline" in f.get("never_say", "") , f.get("never_say"))
    check("ac bad page: dates gate (updated before published)", "before published" in f.get("dates", ""), f.get("dates"))
    check("ac bad page: long sentence warning", any("average sentence" in w for w in d.get("warns", [])), d.get("warns"))
    # regulated page without a scope note fails
    text = (FX / "good-evidence.md").read_text().replace("This is general information for Idaho residents, not financial or tax advice, and reading it does not make you a client. For your own situation, talk to an accountant who knows it.\n\n", "")
    (cwd / "no-scope.md").write_text(text)
    ok, out, code = run([PY, AC, "check", "no-scope.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    d = pj(out)
    check("ac regulated page without a scope note fails scope_note", code == 1 and "scope_note" in d.get("fails", {}), out[:400])
    check("ac warns when no business file given", any("business-file" in w for w in d.get("warns", [])), d.get("warns"))
    # regulated page without a reviewer fails author
    text2 = (FX / "good-evidence.md").read_text().replace("reviewer: Sam Lee, CPA", "reviewer: none")
    (cwd / "no-reviewer.md").write_text(text2)
    ok, out, code = run([PY, AC, "check", "no-reviewer.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac regulated page without a reviewer fails author", code == 1 and "reviewer" in pj(out).get("fails", {}).get("author", ""), out[:400])
    # duplicate against the map: publish Q-01 under a different id
    text3 = (FX / "good-evidence.md").read_text().replace("id: Q-01", "id: Q-77")
    (cwd / "dup.md").write_text(text3)
    ok, out, code = run([PY, AC, "check", "dup.md", "--site", "https://example.com", "--questions", "search/questions.json"], cwd, ok_codes=(1,))
    check("ac duplicate of a published question fails duplicate", code == 1 and "duplicate" in pj(out).get("fails", {}), out[:400])
    # results claim without typical
    text4 = (FX / "good-first-hand.md").read_text().replace("## What doubles it?", "Clients who finish the clean-up save about $400 a month in late fees [own].\n\n## What doubles it?")
    (cwd / "no-typical.md").write_text(text4)
    ok, out, code = run([PY, AC, "check", "no-typical.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac results claim without the typical result fails typical_result", code == 1 and "typical_result" in pj(out).get("fails", {}), out[:400])
    # first-hand page without How we know
    text5 = re.sub(r"## How we know.*?(?=## What we'd)", "", (FX / "good-first-hand.md").read_text(), flags=re.S)
    (cwd / "no-hwk.md").write_text(text5)
    ok, out, code = run([PY, AC, "check", "no-hwk.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac first-hand page without How we know fails how_we_know", code == 1 and "how_we_know" in pj(out).get("fails", {}), out[:400])
    # schema block that does not match the title fails schema_match
    text6 = (FX / "good-evidence.md").read_text() + '\n```json\n{"@context":"https://schema.org","@type":"Article","headline":"Something else","author":{"@type":"Person","name":"Dana Ruiz"}}\n```\n'
    (cwd / "schema-mismatch.md").write_text(text6)
    ok, out, code = run([PY, AC, "check", "schema-mismatch.md", "--site", "https://example.com"], cwd, ok_codes=(1,))
    check("ac mismatched schema headline fails schema_match", code == 1 and "schema_match" in pj(out).get("fails", {}), out[:400])
    # new scaffold
    ok, out, _ = run([PY, AC, "new", "How long does a clean-up take?", "--slug", "clean-up-time", "--author", "Dana Ruiz", "--credentials", "CPA", "--kind", "first-hand", "--id", "Q-05", "--cluster", "pricing"], cwd)
    f = cwd / "search/answers/clean-up-time.md"
    check("ac new writes a scaffold with front matter and How we know", ok and f.exists() and "## How we know" in f.read_text() and "kind: first-hand" in f.read_text(), out)
    ok, out, code = run([PY, AC, "check", f], cwd, ok_codes=(1,))
    check("ac a fresh scaffold fails the gate (nothing half-finished goes live)", code == 1, out[:300])
    ok, out, _ = run([PY, AC, "new", "How long does a clean-up take?", "--slug", "clean-up-time", "--author", "Dana Ruiz"], cwd, ok_codes=(2,))
    check("ac new refuses to overwrite without --force", ok, out)
    # schema output
    ok, out, _ = run([PY, AC, "schema", FX / "good-evidence.md", "--site", "https://example.com", "--org", "Ruiz Advisory", "--out", "schema.json"], cwd)
    sch = json.loads((cwd / "schema.json").read_text())
    types = [g["@type"] for g in sch["@graph"]]
    art = sch["@graph"][0]
    check("ac schema emits Article + BreadcrumbList, no FAQPage by default", ok and types == ["Article", "BreadcrumbList"], types)
    check("ac schema Article carries author, reviewer, dates, publisher, url", art["author"]["name"] == "Dana Ruiz" and art["reviewedBy"]["name"].startswith("Sam") and art["datePublished"] == "2026-11-10"
          and art["publisher"]["name"] == "Ruiz Advisory" and art["url"] == "https://example.com/answers/what-is-13-week-cash-flow-forecast", json.dumps(art)[:400])
    ok, out, _ = run([PY, AC, "schema", FX / "good-evidence.md", "--site", "https://example.com", "--faq"], cwd)
    sch = json.loads(out)
    faq = [g for g in sch["@graph"] if g["@type"] == "FAQPage"]
    check("ac schema --faq adds FAQPage from question headings with the markers stripped", faq and all(q["name"].endswith("?") for q in faq[0]["mainEntity"]) and "[S1]" not in json.dumps(faq), json.dumps(faq)[:300])
    # a page carrying that schema block passes schema_match
    text7 = (FX / "good-evidence.md").read_text() + "\n```json\n" + json.dumps(sch) + "\n```\n"
    (cwd / "with-schema.md").write_text(text7)
    ok, out, _ = run([PY, AC, "check", "with-schema.md", "--site", "https://example.com"], cwd)
    check("ac a page with its own emitted schema passes schema_match", ok and pj(out)["gates"]["schema_match"], out[:300])
    # robots
    ok, out, _ = run([PY, AC, "robots", "--site", "https://example.com", "--block-training"], cwd)
    check("ac robots allows search crawlers and blocks training when asked",
          ok and "User-agent: OAI-SearchBot\nAllow: /" in out and "User-agent: GPTBot\nDisallow: /" in out and "User-agent: Googlebot\nAllow: /" in out and out.rstrip().endswith("https://example.com/sitemap.xml"), out[:300])
    ok, out, _ = run([PY, AC, "robots"], cwd)
    check("ac robots default allows everything", ok and "Disallow" not in out, out[:200])
    return cwd


# ---------------------------------------------------------------- profile tracker

def profile_tests(tmp):
    cwd = tmp / "pt"
    cwd.mkdir()
    desc = ("Ruiz Advisory keeps the books straight for small construction firms in Boise and the Treasure Valley. Weekly bookkeeping, "
            "clean-ups, a 13-week cash view, and year-end files your CPA will thank you for. In business since 2011.")
    ok, out, _ = run([PY, PT, "init", "--name", "Ruiz Advisory", "--type", "service-area", "--category", "Accountant"], cwd)
    check("pt init writes profile.json with the eligibility note", ok and (cwd / "search/profile.json").exists() and "in-person" in out, out)
    ok, out, _ = run([PY, PT, "init", "--name", "X", "--type", "shop"], cwd, ok_codes=(2,))
    check("pt init rejects an unknown type", ok, out)
    ok, out, _ = run([PY, PT, "check"], cwd, ok_codes=(1,))
    d = pj(out)
    check("pt check on a bare profile: critical fail (not verified, eligibility unsure), score low", d.get("critical_fail") and d.get("score", 100) < 40, out[:300])
    ok, out, _ = run([PY, PT, "set", "eligible=yes", "owner_verified=yes", "hours_set=yes", "phone=(555) 010-0100", "website=https://example.com",
                      "appointment_url=https://example.com/book", f"description={desc}", "secondary_categories=Bookkeeping service,Tax preparation",
                      "service_area=Boise, Meridian, Nampa", "review_link=https://g.page/r/example/review", "ask_method=text with consent", "ask_timing=same day",
                      "photos_count=12", f"photos_last={date.today().isoformat()}", f"posts_last={date.today().isoformat()}", "nap_address=12 N Main St, Suite 4"], cwd)
    check("pt set accepts plain, nested, list and boolean keys", ok, out)
    ok, out, _ = run([PY, PT, "set", "nonsense=1"], cwd, ok_codes=(2,))
    check("pt set rejects an unknown key", ok, out)
    for name, d_ in (("Bookkeeping clean-up", "For owners whose books are months behind. We rebuild them and hand back a clean file."),
                     ("Weekly bookkeeping", "For firms with staff and suppliers. Books kept current every week."),
                     ("13-week cash view", "For owners who want to see the next quarter. Updated every Monday in twenty minutes.")):
        run([PY, PT, "service", "add", name, "--description", d_], cwd)
    ok, out, _ = run([PY, PT, "service", "add", "Weekly bookkeeping"], cwd, ok_codes=(2,))
    check("pt service add refuses a duplicate", ok, out)
    # reviews: 22 steady reviews over 90 days, answered
    for i in range(22):
        when = (date.today() - timedelta(days=4 * i)).isoformat()
        run([PY, PT, "log", "review", "--rating", "5", "--date", when, "--replied"], cwd)
    run([PY, PT, "set", "reviews_rating=4.8"], cwd)
    for i in range(8):
        run([PY, PT, "log", "review-ask", "--n", "2", "--date", (date.today() - timedelta(days=3 * i)).isoformat()], cwd)
    ok, out, _ = run([PY, PT, "check", "--md"], cwd)
    d = pj(out)
    check("pt check: complete profile scores high with no critical fail", ok and not d["critical_fail"] and d["score"] >= 85, f"score {d.get('score')} fix_first {d.get('fix_first')}")
    check("pt check --md writes profile-check.md with rank/convert groups", (cwd / "search/profile-check.md").exists() and "| rank |" in (cwd / "search/profile-check.md").read_text())
    items = {i["key"]: i for i in d["items"]}
    check("pt check: reviews_steady passes (no burst) and reviews_recent passes", items["reviews_steady"]["ok"] and items["reviews_recent"]["ok"] and items["reviews_count"]["ok"])
    check("pt check: listings_core fails with no listings yet", not items["listings_core"]["ok"])
    # a burst of reviews trips reviews_steady
    for i in range(10):
        run([PY, PT, "log", "review", "--rating", "5", "--replied"], cwd)
    ok, out, _ = run([PY, PT, "check"], cwd)
    items = {i["key"]: i for i in pj(out)["items"]}
    check("pt check: a burst of 10+ reviews in 7 days fails reviews_steady", not items["reviews_steady"]["ok"], items["reviews_steady"])
    # stuffed name is critical
    ok, out, _ = run([PY, PT, "set", "business=Ruiz Advisory Best Accountant Boise", "legal_name=Ruiz Advisory"], cwd)
    ok, out, code = run([PY, PT, "check"], cwd, ok_codes=(1,))
    d = pj(out)
    items = {i["key"]: i for i in d["items"]}
    check("pt check: a keyword-stuffed name is a critical fail (exit 1)", code == 1 and d["critical_fail"] and not items["real_name"]["ok"], items["real_name"])
    run([PY, PT, "set", "business=Ruiz Advisory"], cwd)
    # unanswered review drives weekly
    run([PY, PT, "log", "review", "--rating", "4"], cwd)
    ok, out, _ = run([PY, PT, "weekly"], cwd)
    tasks = " ".join(pj(out)["tasks"])
    check("pt weekly starts with the open review and keeps asks steady", ok and tasks.startswith("Reply to 1 open review") and "do not push more" in tasks, tasks)
    run([PY, PT, "log", "reply"], cwd)
    ok, out, _ = run([PY, PT, "weekly"], cwd)
    check("pt weekly drops the reply task once answered", "Reply to" not in " ".join(pj(out)["tasks"]), out)
    # listings
    run([PY, PT, "listings", "add", "--site", "Bing Places", "--url", "https://bing.example/x", "--name", "Ruiz Advisory LLC", "--address", "12 North Main Street #4", "--phone", "555-010-0100", "--status", "live"], cwd)
    run([PY, PT, "listings", "add", "--site", "Yelp", "--name", "Ruiz Advisory", "--address", "12 N Main St, Suite 4", "--phone", "(555) 010-0101", "--status", "live"], cwd)
    ok, out, code = run([PY, PT, "listings", "check"], cwd, ok_codes=(1,))
    d = pj(out)
    check("pt listings check normalises LLC/North/Street/Suite and flags the wrong phone only",
          code == 1 and len(d["mismatches"]) == 1 and d["mismatches"][0]["site"] == "Yelp" and d["mismatches"][0]["mismatch"] == ["phone"], out[:400])
    check("pt listings check names the core listings still missing", "Apple Business" in d["core_missing"] and "Bing Places" not in d["core_missing"], d["core_missing"])
    ok, out, _ = run([PY, PT, "listings", "add", "--site", "Yelp", "--phone", "(555) 010-0100", "--name", "Ruiz Advisory", "--address", "12 N Main St, Suite 4"], cwd)
    ok, out, _ = run([PY, PT, "listings", "check"], cwd)
    check("pt listings add updates an existing site and check passes", ok and not pj(out)["mismatches"], out[:200])
    ok, out, _ = run([PY, PT, "report", "--md"], cwd)
    d = pj(out)
    check("pt report counts reviews, asks and the ask-to-review share and writes md", ok and d["reviews"]["asks_last_30_days"] == 16 and d["ask_to_review"] is not None and (cwd / "search/profile-report.md").exists(), out[:300])
    # type none
    cwd2 = tmp / "pt2"
    cwd2.mkdir()
    run([PY, PT, "init", "--name", "Remote Coach Co", "--type", "none"], cwd2)
    ok, out, _ = run([PY, PT, "check"], cwd2)
    check("pt check with type none: no profile, listings and pages carry the load", ok and pj(out).get("profile") == "none", out)
    ok, out, _ = run([PY, PT, "weekly"], cwd2)
    check("pt weekly with type none gives a listings/answer task", "No profile" in pj(out)["tasks"][0], out)
    return cwd


# ---------------------------------------------------------------- citation check

def citation_tests(tmp, qm_cwd):
    cwd = tmp / "cc"
    cwd.mkdir()
    shutil.copytree(qm_cwd / "search", cwd / "search")
    ok, out, _ = run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "Bookkeeper", "--city", "Boise", "--audience", "small construction firms", "--month", "2026-11"], cwd)
    d = pj(out)
    data = json.loads((cwd / "search/checks/2026-11.json").read_text())
    kinds = [p["kind"] for p in data["prompts"]]
    check("cc plan builds category, brand and question prompts with two wordings", ok and d["prompts"] == len(data["prompts"]) and kinds.count("category") == 4 and kinds.count("brand") == 2
          and kinds.count("question") >= 2 and all(p["a"] != p["b"] for p in data["prompts"]), kinds)
    check("cc plan puts published questions first", data["prompts"][6]["status"] == "published", [p.get("status") for p in data["prompts"]])
    ok, out, _ = run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "Bookkeeper", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc plan refuses to rebuild a month without --force", ok, out)
    ok, out, _ = run([PY, CC, "prompts", "--month", "2026-11"], cwd)
    md = (cwd / "search/checks/2026-11-prompts.md").read_text()
    check("cc prompts writes the checklist with an engine column each", ok and "| google-ai |" in md and "| P-01 |" in md, md[:300])
    logs = [("P-01", "google-ai", "profile", "a", 1, ""), ("P-01", "google-ai", "none", "a", 2, ""), ("P-01", "chatgpt", "competitor", "a", 1, "Acme Books"),
            ("P-02", "chatgpt", "directory", "a", 1, ""), ("P-05", "chatgpt", "own", "a", 1, ""), ("P-05", "perplexity", "named", "b", 1, ""),
            ("P-03", "google-ai", "competitor", "a", 1, "Acme Books"), ("P-04", "gemini", "none", "a", 1, "")]
    for pr, eng, res, var, run_, comp in logs:
        args = [PY, CC, "log", pr, "--engine", eng, "--result", res, "--variant", var, "--run", str(run_), "--month", "2026-11"]
        if comp:
            args += ["--competitor", comp]
        ok, out, _ = run(args, cwd)
    ok, out, _ = run([PY, CC, "log", "P-99", "--engine", "chatgpt", "--result", "own", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects a prompt not in the plan", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "bing", "--result", "own", "--month", "2026-11"], cwd, ok_codes=(2,))
    check("cc log rejects an unknown engine", ok, out)
    ok, out, _ = run([PY, CC, "log", "P-01", "--engine", "google-ai", "--result", "own", "--variant", "a", "--run", "1", "--month", "2026-11"], cwd)
    check("cc log replaces the same prompt/variant/run/engine entry", ok and pj(out)["results_so_far"] == 8, out)
    ok, out, _ = run([PY, CC, "report", "--month", "2026-11", "--md"], cwd)
    d = pj(out)
    g = d["by_engine"]["google-ai"]
    check("cc report: google-ai tried 2 prompts, seen 1, consistency 1 of 3 runs", g["prompts_tried"] == 2 and g["prompts_seen"] == 1 and g["consistency"] == round(1 / 3, 2), json.dumps(g))
    check("cc report: overall share seen 3 of 5 prompts, competitors counted, never-seen listed", d["prompts_tried"] == 5 and d["prompts_seen"] == 3 and d["competitors"][0] == ["Acme Books", 2]
          and {x["id"] for x in d["never_seen"]} == {"P-03", "P-04"}, json.dumps({k: d[k] for k in ("prompts_tried", "prompts_seen", "competitors", "never_seen")}))
    check("cc report writes markdown with the engine table", (cwd / "search/checks/2026-11-report.md").exists() and "| google-ai |" in (cwd / "search/checks/2026-11-report.md").read_text())
    # next month compares
    run([PY, CC, "plan", "--business", "Ruiz Advisory", "--category", "Bookkeeper", "--city", "Boise", "--month", "2026-12"], cwd)
    run([PY, CC, "log", "P-01", "--engine", "chatgpt", "--result", "own", "--month", "2026-12"], cwd)
    ok, out, _ = run([PY, CC, "report", "--month", "2026-12"], cwd)
    d = pj(out)
    check("cc report compares with the previous month", ok and d.get("previous", {}).get("month") == "2026-11" and "change" in d, out[:300])
    return cwd


# ---------------------------------------------------------------- consistency between scripts, references, template and docs

def consistency_tests():
    ac = (S / "answer_check.py").read_text()
    std = (R / "answer-standard.md").read_text()
    gates = re.search(r"GATES = \((.*?)\)", ac, re.S).group(1)
    gate_names = re.findall(r'"([a-z_]+)"', gates)
    missing = [g for g in gate_names if f"`{g}`" not in std]
    check("gate names in answer_check.py all appear in answer-standard.md", not missing, missing)
    doc_gates = re.findall(r"^\| `([a-z_]+)` \|", std, re.M)
    check("answer-standard.md gate table matches the script's gates", set(doc_gates) == set(gate_names), set(doc_gates) ^ set(gate_names))
    crawlers = re.findall(r'"([A-Za-z-]+)"', re.search(r"SEARCH_CRAWLERS = \((.*?)\)", ac, re.S).group(1))
    site = (R / "site-and-platforms.md").read_text()
    missing = [c for c in crawlers if c not in std or c not in site]
    check("search crawlers in the script appear in answer-standard.md and site-and-platforms.md", not missing, missing)
    pt = (S / "profile_tracker.py").read_text()
    core = re.findall(r'"([A-Za-z ]+)"', re.search(r"CORE_LISTINGS = \((.*?)\)", pt, re.S).group(1))
    rl = (R / "reviews-and-listings.md").read_text()
    missing = [c for c in core if c not in rl]
    check("core listings in profile_tracker.py appear in reviews-and-listings.md", not missing, missing)
    qm = (S / "question_map.py").read_text()
    w = dict(re.findall(r'"(\w+)": (0\.\d+)', re.search(r"WEIGHTS = \{(.*?)\}", qm).group(1)))
    check("question weights are the founder's (25/25/20/20/10)", w == {"demand": "0.25", "value": "0.25", "gap": "0.20", "answerable": "0.20", "fresh": "0.10"}, w)
    qmd = (R / "question-map.md").read_text()
    check("question-map.md states the weights", "demand 25%, value 25%, gap 20%, answerable 20%, freshness 10%" in qmd)
    # §21 in the template, the skill's copy, and the SKILL.md phase 7 list
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
    # SKILL.md description budget and references
    desc = re.search(r"description: \|\n((?:  .*\n)+)", skill).group(1)
    desc = " ".join(l.strip() for l in desc.splitlines())
    check("SKILL.md description is 200 to 1,024 characters and leads with a trigger phrase list", 200 <= len(desc) <= 1024 and '"get found on Google,"' in desc, len(desc))
    refs = set(re.findall(r"`references/([\w-]+\.md)`", skill))
    missing = [r for r in refs if not (R / r).exists()]
    check("every reference named in SKILL.md exists", not missing, missing)
    unlisted = [p.name for p in R.glob("*.md") if p.name not in refs and p.name != "business-file-template.md"]
    check("every reference file is named in SKILL.md", not unlisted, unlisted)
    scripts = set(re.findall(r"`?(\w+\.py)`?", skill))
    missing = [s for s in ("question_map.py", "answer_check.py", "profile_tracker.py", "citation_check.py") if s not in scripts]
    check("every script is named in SKILL.md", not missing, missing)
    # retired advice named
    sp = (R / "search-principles.md").read_text()
    for term in ("llms.txt", "FAQ rich results", "Q&A", "star markup", "templated city pages"):
        check(f"search-principles.md names retired advice: {term}", term.lower() in sp.lower())
    # confidentiality: no emails, keys, or the founder's or any member's personal name in the skill, tests or fixtures
    hits = []
    for p in list(SK.rglob("*")) + list(HERE.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".py", ".txt", ".json"):
            t = p.read_text(errors="ignore")
            if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t) and "unsubscribe" not in p.name:
                hits.append(f"{p.name}: an email address")
            if re.search(r"\b(sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{12,}|xox[bp]-)", t):
                hits.append(f"{p.name}: a key")
            if re.search(r"\bLanny\b|\bMorton\b", t):
                hits.append(f"{p.name}: the founder's name")
    check("confidentiality: no email addresses, keys or personal names in the skill, tests or fixtures", not hits, hits)
    # the script docstrings describe their commands
    for sc, cmds in ((QM, ("init", "add", "import", "score", "next", "set", "list", "md")), (AC, ("new", "check", "schema", "robots")),
                     (PT, ("init", "set", "service", "log", "check", "weekly", "listings", "report")), (CC, ("plan", "log", "report", "prompts"))):
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
