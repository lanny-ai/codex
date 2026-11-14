#!/usr/bin/env python3
"""AI Momentum Labs Book Builder tests: settings and targets, the intake and its gate, sources and
permissions, the plan, approvals, the book record, the manuscript (status, context, editions, diff,
export), the issue register, test readers (simulated and human kept apart, thresholds, waiver), the
checks (every FIX made to fail once) and the gate, and consistency and wiring across the skill.

Local only: synthetic files in a temporary folder, no network.

Usage:  python3 buildroom/tests/book/run_tests.py [--keep]
Exit code 0 when every check passes.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import json, os, re, shutil, subprocess, tempfile, zipfile  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SK = ROOT / "skills/buildroom-book-builder"
S, R = SK / "scripts", SK / "references"
PY = sys.executable
PLAN, MS, ISS, RP, CHK = (S / n for n in ("book_plan.py", "manuscript.py", "issues.py", "reader_panel.py", "book_check.py"))
sys.path.insert(0, str(S))
import booklib as bl  # noqa: E402
import book_check as bc  # noqa: E402
RESULTS = []
EM = "—"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {str(detail)[:600]}" if detail and not ok else ""))


def run(args, cwd):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return p.returncode, p.stdout + p.stderr


def pj(out):
    try:
        return json.loads(out[out.index("{"):])
    except Exception:
        return {}


def ids(d):
    return {i["id"] for i in d.get("items", [])}


OPEN = ["When I began this work", "After that long winter", "Before my first client", "During that slow spring",
        "On the morning of the call", "Late in that same year", "Once the invoices were paid", "While the kettle boiled",
        "At the kitchen table", "Back in the old office", "Near the end of summer", "Over a second coffee"]
MID = ["I wrote down each problem I had solved for someone else", "she told me what her old job had taught her",
       "we looked hard at the price on the page", "I asked a stranger what he would pay for help",
       "the teacher read her own list out loud", "we chose one person to call that week",
       "I stopped building things nobody had asked for", "she drew the map on the back of an envelope",
       "we counted the hours she could really give", "I said plainly what I do for a living",
       "the first client asked a question I could answer", "we cut the offer down to one clear thing",
       "she rang a former colleague before lunch", "I kept the plan to a single page"]
TAIL = ["and the answer was better than I had feared", "which made the next step feel possible",
        "so the week ahead looked lighter than the last", "and nobody laughed the way she expected",
        "because the simple version was the one that worked", "though it took me a while to believe it",
        "and that small proof changed how we both talked", "so we wrote it down before the feeling passed",
        "which is the part most people rush straight past", "and the fear of asking shrank a little",
        "because a real person had finally said yes", "so the map began to look like a road",
        "and we agreed to try it again on Friday", "which told us more than any amount of planning"]


def prose(seed, n_words):
    """Varied, deterministic, plain prose: no two sections share a paragraph, paragraphs differ in length."""
    x = seed * 7919 + 13
    def nxt(n):
        nonlocal x
        x = (x * 1103515245 + 12345) % 2147483648
        return (x >> 8) % n
    out, w = [], 0
    while w < n_words:
        sents = []
        for k in range(3 + nxt(4)):
            m, t = MID[nxt(len(MID))], TAIL[nxt(len(TAIL))]
            sents.append(f"{OPEN[nxt(len(OPEN))]}, {m} {t}." if k % 2 == 0 else f"{m[0].upper()}{m[1:]}, {t[4:] if t.startswith('and ') else t}.")
        para = " ".join(sents)
        out.append(para)
        w += bl.words(para)
    return "\n\n".join(out)


def write_section(book, fname, title, body):
    (book / "manuscript").mkdir(parents=True, exist_ok=True)
    (book / "manuscript" / fname).write_text(f"=== SECTION: {title} ===\n\n{body}\n")


BRIEF = ("This chapter delivers one idea the reader can use at once. It uses a story from the author's own answers, "
         "teaches the steps of the Second Chapter Map in order, deals with the objection a careful reader would raise, "
         "and leaves a single clear takeaway for the reader to try before the next chapter begins.")


# ---------------------------------------------------------------- 1. settings and intake
def t_setup(tmp):
    B = tmp / "book" / "second-chapter"
    code, out = run([PY, PLAN, "status", "--book", B], tmp)
    check("a command on a book that does not exist is refused", code == 1)
    code, out = run([PY, PLAN, "init", "--book", B, "--author", "Ruth Adeyemi"], tmp)
    d = pj(out)
    check("init defaults to twelve chapters and about 62,000 words", code == 0 and d["settings"]["chapters"] == 12
          and d["settings"]["words"] == 62000, out)
    check("a default chapter targets words // chapters", d["targets"]["Chapter 1"] == 62000 // 12)
    check("the introduction and conclusion are half a chapter; About the Author is 250",
          d["targets"]["Introduction"] == (62000 // 12) // 2 and d["targets"]["About the Author"] == 250)
    check("init is safe to run twice", pj(run([PY, PLAN, "init", "--book", B], tmp)[1]).get("created") is False)
    code, out = run([PY, PLAN, "settings", "--book", B, "--chapters", "3", "--words", "3000", "--chapter-words", "2=1500"], tmp)
    d = pj(out)
    check("the member can set any chapter count and length", code == 0 and d["targets"]["Chapter 1"] == 1000
          and len([k for k in d["targets"] if k.startswith("Chapter")]) == 3)
    check("one chapter's length can be set on its own", d["targets"]["Chapter 2"] == 1500)
    code, out = run([PY, PLAN, "settings", "--book", B, "--chapter-words", "9=1000"], tmp)
    check("a length for a chapter that is not in the book is refused", code == 1)
    code, out = run([PY, PLAN, "settings", "--book", B, "--chapters", "0"], tmp)
    check("zero chapters is refused", code == 1)
    # intake
    d = pj(run([PY, PLAN, "intake", "--book", B], tmp)[1])
    check("the intake has the fifteen questions", d["of"] == 15 and len(d["missing"]) == 15)
    check("the intake says which Business File section may hold an answer",
          next(m for m in d["missing"] if m["key"] == "reader")["may_be_in_file"] == "§2")
    code, out = run([PY, PLAN, "answer", "--book", B, "--key", "nope", "--text", "x"], tmp)
    check("an unknown intake key is refused", code == 1)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "ready"], tmp)
    check("READY is refused with nothing answered", code == 1)
    ans = {"about": "A book for women leaving long careers who want paid work on their own terms.",
           "reader": "Ruth, 62, a retired principal who thinks she has nothing to sell.",
           "transformation": "Before: sure nobody would pay her. After: one paying client.",
           "story": "I sat at a kitchen table with a pile of unpaid invoices.",
           "work": "I have coached for 12 years and worked with 40 clients.",
           "method": "The Second Chapter Map: name what you know, pick your first client, price it, build your week.",
           "mistake": "Building a website before having a client.",
           "result": "A retired teacher went from no clients to six in a year."}
    for k, v in list(ans.items())[:7]:
        run([PY, PLAN, "answer", "--book", B, "--key", k, "--text", v, "--from", "§2" if k == "reader" else "member"], tmp)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "ready"], tmp)
    check("READY is refused under eight answers", code == 1 and "7 of 15" in out, out)
    run([PY, PLAN, "answer", "--book", B, "--key", "result", "--text", ans["result"]], tmp)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "ready"], tmp)
    check("READY is refused while a core question (voice) is unanswered", code == 1 and "voice" in out, out)
    run([PY, PLAN, "answer", "--book", B, "--key", "voice", "--text", "Plain and warm. Short sentences. I tell stories."], tmp)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "hold", "--gap", "no second story"], tmp)
    check("a HOLD must name the questions to ask", code == 1)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "hold", "--gap", "no second story",
                     "--question", "Tell me about a second client."], tmp)
    check("a HOLD records the gaps and questions", code == 0 and pj(out)["stage"]["status"] == "hold")
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "ready", "--gap", "still thin"], tmp)
    check("READY with open gaps is refused", code == 1)
    code, out = run([PY, PLAN, "intake-gate", "--book", B, "--verdict", "ready"], tmp)
    check("READY passes with nine answers and the core ones", code == 0)
    check("intake.md is written for the member", "## Who is this book for?" in (B / "intake.md").read_text())
    # sources
    code, out = run([PY, PLAN, "source", "--book", B, "add", "--title", "Podcast, March", "--kind", "transcript",
                     "--ref", "podcast.txt"], tmp)
    check("a source gets an ID", code == 0 and pj(out)["id"] == "S-001")
    (B / "sources" / "podcast.txt").write_text("On the podcast I said seventy percent of my clients start with one phone call. 70% in fact.")
    code, out = run([PY, PLAN, "source", "--book", B, "add", "--title", "The teacher's story", "--kind", "client"], tmp)
    check("a client source with no permission is marked not documented", pj(out)["source"]["permission"] == "not documented")
    code, out = run([PY, PLAN, "source", "--book", B, "add", "--title", "x", "--kind", "rumour"], tmp)
    check("an unknown source kind is refused", code == 1)
    return B


# ---------------------------------------------------------------- 2. plan, approvals, record
def t_plan(tmp, B):
    plan = {"title": "The Second Chapter", "subtitle": "Paid work on your own terms", "promise": "You finish with your first client.",
            "voice": "Plain and warm.", "thread": "Experience is an asset.", "conclusion": "Start with one call.",
            "chapters": [{"title": "Name What You Know", "idea": "You know more than you think", "brief": BRIEF,
                          "stories": ["the kitchen table"], "sources": ["S-001"]},
                         {"title": "Pick Your First Client", "idea": "One person", "brief": BRIEF, "stories": ["the Tuesday call"]},
                         {"title": "Price It", "idea": "A stranger pays", "brief": BRIEF, "stories": ["the teacher"], "sources": ["S-002"]}]}

    def put(p):
        (B / "plan.json").write_text(json.dumps(p))
        return run([PY, PLAN, "plan-check", "--book", B], tmp)
    bad = json.loads(json.dumps(plan)); bad["chapters"] = bad["chapters"][:2]
    code, out = put(bad)
    check("a plan with the wrong number of chapters is refused", code == 1 and "3" in out)
    bad = json.loads(json.dumps(plan)); bad["chapters"][1]["stories"] = ["The Kitchen Table"]
    code, out = put(bad)
    check("a story planned for two chapters is refused", code == 1 and "told once" in out)
    bad = json.loads(json.dumps(plan)); bad["chapters"][0]["brief"] = "Too short."
    check("a thin chapter brief is refused", put(bad)[0] == 1)
    bad = json.loads(json.dumps(plan)); bad["chapters"][0]["sources"] = ["S-009"]
    check("a source that is not in the packet is refused", put(bad)[0] == 1)
    bad = json.loads(json.dumps(plan)); bad["title"] = f"The Second Chapter {EM} Now"
    check("a dash in the title is refused", put(bad)[0] == 1)
    bad = json.loads(json.dumps(plan)); bad["promise"] = ""
    check("a plan with no promise is refused", put(bad)[0] == 1)
    code, out = put(plan)
    check("a good plan passes and writes plan.md", code == 0 and "## Chapter 2: Pick Your First Client" in (B / "plan.md").read_text(), out)
    code, out = run([PY, MS, "context", "--book", B, "--chapter", "1"], tmp)
    check("no chapter context before the member approves the outline", code == 1 and "approved" in out)
    code, out = run([PY, PLAN, "approve", "--book", B, "--what", "outline", "--by", "editor"], tmp)
    check("only the member approves the outline", code == 1)
    code, out = run([PY, PLAN, "approve", "--book", B, "--what", "outline", "--by", "member"], tmp)
    check("the member approves the outline", code == 0)
    code, out = run([PY, PLAN, "settings", "--book", B, "--chapters", "4"], tmp)
    check("changing the chapter count after approval asks for approval again", pj(out)["warnings"]
          and json.loads((B / "book.json").read_text())["stages"]["outline"]["status"] == "needs re-approval")
    run([PY, PLAN, "settings", "--book", B, "--chapters", "3"], tmp)
    run([PY, PLAN, "plan-check", "--book", B], tmp)
    run([PY, PLAN, "approve", "--book", B, "--what", "outline", "--by", "member"], tmp)
    # record
    run([PY, PLAN, "record", "--book", B, "add", "--kind", "framework", "--text", "Second Chapter Map"], tmp)
    run([PY, PLAN, "record", "--book", B, "add", "--kind", "story", "--text", "the kitchen table", "--chapter", "1"], tmp)
    code, out = run([PY, PLAN, "record", "--book", B, "add", "--kind", "story", "--text", "The kitchen table", "--chapter", "2"], tmp)
    check("recording a story already told warns", pj(out)["warnings"])
    code, out = run([PY, PLAN, "record", "--book", B, "add", "--kind", "summary", "--text", "x"], tmp)
    check("a summary needs its chapter", code == 1)
    run([PY, PLAN, "record", "--book", B, "add", "--kind", "summary", "--chapter", "1", "--text", "Established the Map and step one."], tmp)
    run([PY, PLAN, "record", "--book", B, "add", "--kind", "summary", "--chapter", "1", "--text", "Established the Map; step one in full."], tmp)
    d = pj(run([PY, PLAN, "record", "--book", B, "show"], tmp)[1])
    check("a chapter has one summary; a new one replaces it", len(d["record"]["summary"]) == 1)
    return plan


# ---------------------------------------------------------------- 3. manuscript
def t_manuscript(tmp, B):
    write_section(B, "00-title.md", "Title Page", "The Second Chapter\n\nby Ruth Adeyemi")
    write_section(B, "01-introduction.md", "Introduction", prose(1, 520))
    write_section(B, "ch-01.md", "Chapter 1: Name What You Know", prose(2, 1020))
    d = pj(run([PY, MS, "status", "--book", B], tmp)[1])
    row = {r["section"].split(":")[0]: r for r in d["sections"]}
    check("status measures the words in each section", row["Chapter 1"]["words"] > 1000 and row["Chapter 1"]["state"] == "written")
    check("status lists the sections still missing", "Conclusion" in d["missing"] and not d["complete"])
    d = pj(run([PY, MS, "context", "--book", B, "--chapter", "2"], tmp)[1])
    check("context gives the brief, the target and earlier summaries", d["target_words"] == 1500 and d["earlier_chapter_summaries"]
          and d["brief"]["title"] == "Pick Your First Client", d)
    check("context lists the stories already told", any("kitchen table" in s for s in d["stories_already_told"]))
    check("context gives the end of the previous section", prose(2, 1020)[-60:] in d["end_of_previous_section"])
    check("context names the next chapter", d["next_chapter"] == "Price It")
    write_section(B, "ch-02.md", "Chapter 2: Pick Your First Client", prose(3, 420))
    d = pj(run([PY, MS, "status", "--book", B], tmp)[1])
    check("a chapter under 60 percent of its target is thin", any(s.startswith("Chapter 2") for s in d["thin"]))
    d = pj(run([PY, MS, "context", "--book", B, "--chapter", "3"], tmp)[1])
    check("context warns when an earlier chapter has no summary", any("chapter 2" in w for w in d["warnings"]))
    write_section(B, "ch-02.md", "Chapter 2: Pick Your First Client", prose(3, 1520))
    write_section(B, "ch-03.md", "Chapter 3: Price It", prose(4, 1020))
    write_section(B, "90-conclusion.md", "Conclusion", prose(5, 520))
    write_section(B, "91-about.md", "About the Author", prose(6, 240))
    d = pj(run([PY, MS, "status", "--book", B], tmp)[1])
    check("status says complete when every section is written", d["complete"] and not d["missing"])
    check("the draft stage is marked done", json.loads((B / "book.json").read_text())["stages"]["draft"]["status"] == "done")
    code, out = run([PY, MS, "assemble", "--book", B], tmp)
    txt = (B / "manuscript.md").read_text()
    check("assemble writes one file in book order", code == 0 and txt.index("Introduction") < txt.index("Chapter 1")
          < txt.index("Chapter 3") < txt.index("Conclusion") < txt.index("About the Author"))
    code, out = run([PY, MS, "edition", "--book", B, "--label", "v1"], tmp)
    d = pj(out)
    idsfile = (B / "editions" / "v1" / "manuscript.ids.md").read_text()
    check("an edition is frozen with paragraph IDs", code == 0 and "[C02-P001]" in idsfile and "[IN-P001]" in idsfile)
    check("an edition has a checksum and a map", len(json.loads((B / "editions/v1/map.json").read_text())["paragraphs"]) == d["paragraphs"])
    code, out = run([PY, MS, "edition", "--book", B, "--label", "v1"], tmp)
    check("an edition is never overwritten", code == 1)
    write_section(B, "ch-03.md", "Chapter 3: Price It", prose(4, 1020) + "\n\nOne new paragraph, added for the second edition of the book.")
    run([PY, MS, "edition", "--book", B, "--label", "v2"], tmp)
    d = pj(run([PY, MS, "diff", "--book", B, "--from", "v1", "--to", "v2"], tmp)[1])
    check("diff names only the section that changed", d["changed_sections"] == 1 and d["changes"][0]["section"].startswith("Chapter 3"), d)
    out_docx = B / "manuscript.docx"
    code, out = run([PY, MS, "export", "--book", B, "--edition", "v2", "--docx", out_docx], tmp)
    with zipfile.ZipFile(out_docx) as z:
        doc = z.read("word/document.xml").decode()
        names = set(z.namelist())
    check("export writes a real .docx", code == 0 and {"[Content_Types].xml", "word/document.xml", "word/styles.xml"} <= names)
    check("the .docx has every section as a heading", doc.count('w:val="Heading1"') == 7)
    code, out = run([PY, MS, "diff", "--book", B, "--from", "v1", "--to", "v9"], tmp)
    check("a diff against a missing edition is refused", code == 1)


# ---------------------------------------------------------------- 4. the issue register
def t_issues(tmp, B):
    def add(*x):
        return run([PY, ISS, "add", "--book", B, *x], tmp)
    code, out = add("--severity", "P1", "--source", "memo", "--location", "Chapter 2", "--issue", "The steps are out of order",
                    "--evidence", "Step three is taught before step two", "--fix", "Reorder")
    check("an issue is added with an ID", code == 0 and pj(out)["id"] == "I-001")
    code, out = add("--severity", "P2", "--source", "human", "--location", "C03-P004", "--issue", "Repeats the opening", "--evidence", "same story")
    check("an issue from a real reader must name the reader code", code == 1)
    add("--severity", "P2", "--source", "human", "--location", "C03-P004", "--issue", "Repeats the opening", "--evidence", "same story",
        "--readers", "r-01,R-03")
    add("--severity", "P0", "--source", "facts", "--location", "C01-P002", "--issue", "A result with no source", "--evidence", "unverified")
    d = pj(run([PY, ISS, "summary", "--book", B], tmp)[1])
    check("the summary lists blocking issues", len(d["blocking"]) == 2 and d["open"] == {"P1": 1, "P2": 1, "P0": 1}, d)
    code, out = run([PY, ISS, "accept", "--book", B, "--id", "I-003", "--by", "member", "--reason", "fine"], tmp)
    check("a P0 cannot be accepted, only fixed", code == 1 and "fixed, not accepted" in out)
    code, out = run([PY, ISS, "accept", "--book", B, "--id", "I-002", "--by", "member", "--reason", "The callback is deliberate"], tmp)
    check("the member can accept a P2 with a reason", code == 0)
    code, out = run([PY, ISS, "resolve", "--book", B, "--id", "I-001", "--edition", "v7", "--note", "reordered"], tmp)
    check("a fix must name a real edition", code == 1)
    run([PY, ISS, "resolve", "--book", B, "--id", "I-001", "--edition", "v2", "--note", "reordered the steps"], tmp)
    d = pj(run([PY, ISS, "summary", "--book", B], tmp)[1])
    check("a fix is not resolved until it is verified", "I-001" in d["unverified"] and any("I-001" in b for b in d["blocking"]))
    run([PY, ISS, "verify", "--book", B, "--id", "I-001", "--result", "partial", "--edition", "v2"], tmp)
    d = pj(run([PY, ISS, "list", "--book", B, "--open", "--severity", "P1"], tmp)[1])
    check("a partial fix goes back to open", d["count"] == 1 and d["issues"][0]["status"] == "open")
    run([PY, ISS, "resolve", "--book", B, "--id", "I-001", "--edition", "v2", "--note", "reordered again"], tmp)
    run([PY, ISS, "verify", "--book", B, "--id", "I-001", "--result", "resolved", "--edition", "v2"], tmp)
    run([PY, ISS, "resolve", "--book", B, "--id", "I-003", "--edition", "v2", "--note", "cut the claim"], tmp)
    run([PY, ISS, "verify", "--book", B, "--id", "I-003", "--result", "resolved", "--edition", "v2"], tmp)
    d = pj(run([PY, ISS, "summary", "--book", B], tmp)[1])
    check("verified fixes close the blocking list", not d["blocking"] and not d["unverified"], d)
    code, out = run([PY, ISS, "verify", "--book", B, "--id", "I-099", "--result", "resolved", "--edition", "v2"], tmp)
    check("an unknown issue is refused", code == 1)


# ---------------------------------------------------------------- 5. readers
def t_readers(tmp, B):
    d = pj(run([PY, RP, "personas", "--book", B], tmp)[1])
    check("four default reader lenses", d["personas"] == ["beginner", "time-poor", "skeptic", "tried-and-failed"])
    code, out = run([PY, RP, "personas", "--book", B, "--add", "bad|only two"], tmp)
    check("a malformed persona is refused", code == 1)
    run([PY, RP, "personas", "--book", B, "--add", "Late Starter|a 62 year old leaving teaching|none|a first client|evenings only|doubts herself"], tmp)
    code, out = run([PY, RP, "brief", "--book", B, "--persona", "late-starter", "--edition", "v9"], tmp)
    check("a brief needs a frozen edition", code == 1)
    code, out = run([PY, RP, "brief", "--book", B, "--persona", "late-starter", "--edition", "v2"], tmp)
    brief = Path(pj(out)["brief"]).read_text()
    check("the simulation brief says it is not a real person", code == 0 and "not feedback from a real person" in brief)
    check("the brief points at the edition with paragraph IDs and nothing else", "manuscript.ids.md" in brief and "Read nothing else" in brief)
    check("the brief carries the book's promise and the author's reader", "first client" in brief and "retired principal" in brief)
    rep = B / "readers" / "round-1" / "sim" / "late-starter.md"
    rep.write_text("A reader report. " + "Chapter 2 lost me at C02-P003 because the steps came too fast. " * 12)
    code, out = run([PY, RP, "record-sim", "--book", B, "--persona", "late-starter", "--report", rep, "--clarity", "3",
                     "--relevance", "5", "--usefulness", "4"], tmp)
    check("a simulated report must be headed as simulated", code == 1 and "simulated" in out)
    rep.write_text("SIMULATED READER, not a real person.\n\n" + "Chapter 2 lost me at C02-P003 because the steps came too fast. " * 12)
    code, out = run([PY, RP, "record-sim", "--book", B, "--persona", "late-starter", "--report", rep, "--clarity", "6",
                     "--relevance", "5", "--usefulness", "4"], tmp)
    check("a score outside 1 to 5 is refused", code == 1)
    code, out = run([PY, RP, "record-sim", "--book", B, "--persona", "late-starter", "--report", rep, "--clarity", "5",
                     "--relevance", "5", "--usefulness", "5"], tmp)
    check("a simulated run is recorded", code == 0)
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("simulated readers alone never pass the round", not d["passed"] and d["human_readers"]["responded"] == 0
          and d["simulated_readers"]["runs"] == 1, d.get("checks"))
    check("simulated scores are reported apart from human ones", d["human_readers"]["median_clarity"] is None)
    code, out = run([PY, RP, "invite", "--book", B, "--roles", "target,friend"], tmp)
    check("an unknown reader role is refused", code == 1)
    d = pj(run([PY, RP, "invite", "--book", B, "--roles", "target,target,skeptic"], tmp)[1])
    check("readers get anonymous codes", d["codes"] == ["R-01", "R-02", "R-03"])
    check("a small panel is warned about", any("six to eight" in w for w in d["warnings"]) and any("subject-aware" in w for w in d["warnings"]))
    d = pj(run([PY, RP, "questionnaire", "--book", B, "--edition", "v2"], tmp)[1])
    q = Path(d["brief"]).read_text()
    check("the questionnaire asks for honest reactions and where they stopped",
          "honest reactions, not encouragement" in q and "naturally stop" in q)
    check("the questionnaire reminds the author not to lead readers", any("expect" in x for x in d["do_not"]))
    code, out = run([PY, RP, "record-human", "--book", B, "--code", "R-09", "--finished", "yes", "--promise-explained", "yes",
                     "--next-step", "yes", "--clarity", "4", "--usefulness", "4", "--recommend", "yes"], tmp)
    check("a reader who was not invited is refused", code == 1)

    def human(code_, fin, pe, ns, cl, us, extra=()):
        return run([PY, RP, "record-human", "--book", B, "--code", code_, "--finished", fin, "--promise-explained", pe,
                    "--next-step", ns, "--clarity", cl, "--usefulness", us, "--recommend", "yes", *extra], tmp)
    human("R-01", "yes", "yes", "yes", "5", "4")
    human("R-02", "no", "yes", "no", "3", "3", ("--stopped-at", "Chapter 2"))
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("two respondents are not enough", not d["checks"]["at least 3 real respondents, 2 of them target readers"])
    human("R-03", "yes", "yes", "yes", "4", "4")
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("the 80 percent threshold uses target readers only, with the count shown",
          d["human_readers"]["promise_and_next_step"] == "1 of 2 target readers"
          and not d["checks"]["80 percent of target readers explain the promise and the next step"], d["human_readers"])
    check("a reader who stopped early is reported, with where", d["human_readers"]["stopped_at"] == ["R-02: Chapter 2"])
    human("R-02", "yes", "yes", "yes", "4", "5")
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("the round passes when every threshold is met", d["passed"] and d["stage"] == "passed", d["checks"])
    md = (B / "readers" / "round-1" / "summary.md").read_text()
    check("the summary keeps real and simulated readers in separate sections",
          "## Real readers" in md and "## Simulated readers (an editorial diagnosis, not people)" in md)
    check("the summary says thresholds are not proof of sales", "not proof the book will sell" in md)
    run([PY, ISS, "add", "--book", B, "--severity", "P1", "--source", "human", "--location", "C02-P003", "--issue", "steps unusable",
         "--evidence", "two readers could not follow", "--readers", "R-01,R-02"], tmp)
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("an open P1 fails the round whatever the scores", not d["passed"] and d["blocking_issues"])
    code, out = run([PY, RP, "waive", "--book", B, "--by", "editor", "--reason", "x"], tmp)
    check("only the member can waive real readers", code == 1)
    run([PY, RP, "waive", "--book", B, "--by", "member", "--reason", "No readers available before the deadline"], tmp)
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("a waiver does not get past an open P1", d["stage"] == "not passed")
    run([PY, ISS, "resolve", "--book", B, "--id", "I-004", "--edition", "v2", "--note", "rewrote the steps"], tmp)
    run([PY, ISS, "verify", "--book", B, "--id", "I-004", "--result", "resolved", "--edition", "v2"], tmp)
    d = pj(run([PY, RP, "consolidate", "--book", B], tmp)[1])
    check("with the P1 fixed the round passes again", d["passed"])


# ---------------------------------------------------------------- 6. the checks and the gate
def t_checks(tmp, B):
    bf = tmp / "BUILDROOM_BUSINESS_FILE.md"
    bf.write_text('## 1. Business Snapshot\n- **Retired lines** (never reuse): "the lazy way to riches"\n\n'
                  '## 18. Advertising\n- **Never-say claims:** guaranteed income; cures anxiety\n')
    base = prose(2, 1020)

    def chapter(body, *extra):
        write_section(B, "ch-01.md", "Chapter 1: Name What You Know", body)
        code, out = run([PY, CHK, "chapter", "--book", B, "--section", "Chapter 1", *extra], tmp)
        return code, pj(out)
    code, d = chapter(base)
    check("a clean chapter passes", code == 0 and d["verdict"] == "CLEAN", d.get("items"))
    cases = [
        ("an em dash", base + f"\n\nShe waited {EM} then called.", "dashes"),
        ("an en dash", base + "\n\nPages 10–12 cover it.", "dashes"),
        ("placeholder text", base + "\n\n[INSERT STORY HERE] and TODO.", "placeholders"),
        ("a number the author did not give", base + "\n\nIn fact 87% of new consultants quit in the first year.", "unsourced_numbers"),
        ("a quotation from someone not in the sources", base + '\n\nAs Warren Buffett once said, "Price is what you pay and value is what you get."',
         "unsourced_quotes"),
        ("'studies show' with no source", base + "\n\nStudies show that people who write goals down achieve more.", "unattributed_authority"),
        ("a named client the author did not supply", base + "\n\nA client of mine, Sarah, doubled her income in a month.", "invented_client"),
    ]
    for label, body, cid in cases:
        code, d = chapter(body)
        check(f"FIX: {label}", code == 1 and cid in ids(d), [i["id"] for i in d.get("items", [])])
    code, d = chapter(base + "\n\nI have coached for 12 years and worked with 40 clients. About 70% start with one phone call.")
    check("numbers from the intake and the source packet pass", code == 0 and "unsourced_numbers" not in ids(d), d.get("items"))
    code, d = chapter(base + "\n\nThis is the lazy way to riches, with guaranteed income.", "--business-file", bf)
    msgs = " ".join(i["message"] for i in d["items"])
    check("FIX: a retired line and a never-say claim from the Business File", code == 1 and "lazy way to riches" in msgs
          and "guaranteed income" in msgs, msgs)
    code, d = chapter(base, "--business-file", tmp / "nope.md")
    check("a mistyped Business File path is an error", code == 2)
    slop = ("In today's fast-paced world, it's worth noting that this journey is a testament to the power of a robust, "
            "seamless and holistic landscape. Let's dive in. It's not a tactic, it's a mindset. The result? A pivotal, crucial "
            "and transformative tapestry. We delve into the realm of clarity, focus, and momentum. ")
    code, d = chapter(base + "\n\n" + slop * 3)
    tell = next((i for i in d["items"] if i["id"] == "ai_tells"), None)
    check("WATCH: AI-writing tells are named by kind", tell and "stock vocabulary" in tell["message"] and "stock phrases" in tell["message"], d.get("items"))
    check("AI tells are advice, not a block", tell and tell["level"] == "WATCH")
    code, d = chapter(base + "\n\n## A heading\n\n**Bold** text here.")
    check("WATCH: markdown in the prose", "markdown" in ids(d))
    code, d = chapter(prose(2, 300))
    check("WATCH: a thin chapter", "thin" in ids(d))
    hard = ("The operationalisation of interdisciplinary organisational methodologies necessitates considerable institutional "
            "deliberation regarding infrastructural prioritisation, notwithstanding contemporaneous administrative limitations. ") * 12
    code, d = chapter(base + "\n\n" + hard)
    check("WATCH: reading level above the book's setting", "reading_level" in ids(d))
    check("the Flesch-Kincaid grade is higher for dense prose", bl.reading_grade(hard) > bl.reading_grade(base) > 0)
    check("a section that does not exist is a usage error", run([PY, CHK, "chapter", "--book", B, "--section", "Chapter 9"], tmp)[0] == 2)
    # whole manuscript
    write_section(B, "ch-01.md", "Chapter 1: Name What You Know", base)
    code, out = run([PY, CHK, "check", "--book", B, "--business-file", bf], tmp)
    d = pj(out)
    check("the gate says FIX while stages are missing", code == 1 and {"stage_memo", "stage_sample", "stage_edit", "stage_review",
          "stage_facts", "stage_copyedit", "stage_regression"} <= ids(d), sorted(ids(d)))
    check("FIX: a planned client source with no documented permission", "permission" in ids(d))
    check("the gate report is written", "**FIX**" in (B / "check.md").read_text())
    check("the gate says what a script cannot judge", "cannot judge" in d["limits"])
    # repeated passage
    write_section(B, "ch-03.md", "Chapter 3: Price It", prose(4, 900) + "\n\n" + base.split("\n\n")[0])
    d = pj(run([PY, CHK, "check", "--book", B], tmp)[1])
    check("FIX: a passage repeated in two sections", "repeated_passage" in ids(d))
    write_section(B, "ch-03.md", "Chapter 3: Price It", prose(4, 1020))
    (B / "manuscript" / "90-conclusion.md").unlink()
    d = pj(run([PY, CHK, "check", "--book", B], tmp)[1])
    check("FIX: a planned section missing", any(i["id"] == "missing_section" and "Conclusion" in i["message"] for i in d["items"]))
    write_section(B, "90-conclusion.md", "Conclusion", prose(5, 520))
    # walk the stages to GO
    src = json.loads((B / "sources.json").read_text())
    src["sources"][1]["permission"] = "documented: signed release 2026-10-02"
    (B / "sources.json").write_text(json.dumps(src))
    code, out = run([PY, PLAN, "stage", "--book", B, "--name", "memo", "--status", "done"], tmp)
    check("a stage cannot be marked done without its report", code == 1)
    for name, f in (("memo", "edit/memo.md"), ("edit", "edit/changelog.md"), ("review", "review/developmental-review.md"),
                    ("facts", "review/claim-ledger.md"), ("copyedit", "review/copyedit.md"), ("regression", "review/regression.md")):
        (B / f).parent.mkdir(parents=True, exist_ok=True)
        (B / f).write_text(("A report with its findings, each tied to a paragraph ID and a severity. " * 6))
    code, out = run([PY, PLAN, "stage", "--book", B, "--name", "review", "--status", "done", "--by", "drafter"], tmp)
    check("the review cannot be done by the session that drafted the book", code == 1 and "independent" in out)
    code, out = run([PY, PLAN, "approve", "--book", B, "--what", "sample", "--by", "member"], tmp)
    check("the sample cannot be approved before it exists", code == 1)
    (B / "edit" / "sample.md").write_text("Original and edited sample chapter, side by side.")
    run([PY, PLAN, "approve", "--book", B, "--what", "sample", "--by", "member", "--feedback", "Keep my short sentences."], tmp)
    for name in ("memo", "edit", "facts", "copyedit"):
        run([PY, PLAN, "stage", "--book", B, "--name", name, "--status", "done"], tmp)
    run([PY, PLAN, "stage", "--book", B, "--name", "review", "--status", "done", "--by", "reviewer"], tmp)
    run([PY, MS, "edition", "--book", B, "--label", "final"], tmp)
    run([PY, PLAN, "stage", "--book", B, "--name", "regression", "--status", "done", "--by", "reviewer", "--edition", "final"], tmp)
    run([PY, RP, "consolidate", "--book", B], tmp)
    code, out = run([PY, CHK, "check", "--book", B, "--business-file", bf], tmp)
    d = pj(out)
    check("the gate says GO when every stage is done and nothing is open", code == 0 and d["verdict"] == "GO", d.get("items"))
    check("GO is recorded on the book", json.loads((B / "book.json").read_text())["stages"]["gate"]["status"] == "go")
    run([PY, ISS, "add", "--book", B, "--severity", "P0", "--source", "facts", "--location", "C02-P001", "--issue", "false claim",
         "--evidence", "contradicted by S-001"], tmp)
    d = pj(run([PY, CHK, "check", "--book", B], tmp)[1])
    check("a new P0 turns GO back to FIX", d["verdict"] == "FIX" and "open_issue" in ids(d))
    run([PY, ISS, "resolve", "--book", B, "--id", "I-005", "--edition", "final", "--note", "cut"], tmp)
    d = pj(run([PY, CHK, "check", "--book", B], tmp)[1])
    check("FIX: a fix nobody verified", "unverified_fixes" in ids(d))
    run([PY, ISS, "verify", "--book", B, "--id", "I-005", "--result", "resolved", "--edition", "final"], tmp)
    write_section(B, "91-about.md", "About the Author", prose(6, 240) + "\n\nOne more line.")
    d = pj(run([PY, CHK, "check", "--book", B], tmp)[1])
    check("editing after the final edition turns GO back to FIX", d["verdict"] == "FIX" and "changed_since_edition" in ids(d))
    st = pj(run([PY, PLAN, "status", "--book", B], tmp)[1])
    check("status shows every stage and the next one", st["stages"]["outline"] == "approved" and st["next"] == "gate", st)
    # unit checks on the tells and names
    check("the tells finder ignores plain prose", not bc.tells(base))
    check("banned lines read quoted and listed items", bc.banned_lines(bf) == [("retired lines", "the lazy way to riches"),
          ("never-say claims", "guaranteed income"), ("never-say claims", "cures anxiety")], bc.banned_lines(bf))
    check("sections parse with subheads kept", bl.parse_sections("=== SECTION: Chapter 1: A ===\n\n@@ Sub\n\nText.\n")[0][1] == ["@@ Sub", "Text."])
    check("section codes", bl.section_code("Chapter 12: X") == "C12" and bl.section_code("Introduction") == "IN")


# ---------------------------------------------------------------- 7. consistency and wiring
def t_consistency():
    skill = (SK / "SKILL.md").read_text()
    m = re.match(r"---\nname: (.+)\ndescription: \|\n  (.+?)\n---", skill, re.S)
    check("SKILL.md has the frontmatter", m and m.group(1) == "buildroom-book-builder")
    check("the description is under 1024 characters", m and len(m.group(2)) < 1024)
    check("the skill is titled AI Momentum Labs Book Builder", "AI Momentum Labs Book Builder" in skill)
    for f in sorted(R.glob("*.md")):
        check(f"SKILL.md names references/{f.name}", f.name in skill)
    for ref in set(re.findall(r"references/([\w.-]+\.md)", skill)):
        check(f"named reference exists: {ref}", (R / ref).exists())
    for f in ("book_plan.py", "manuscript.py", "issues.py", "reader_panel.py", "book_check.py"):
        check(f"SKILL.md uses scripts/{f}", f in skill)
    allt = skill + "".join(f.read_text() for f in R.glob("*.md"))
    check("twelve chapters is the default, and adjustable", "welve chapters" in skill and "settings" in skill
          and bl.DEFAULT_CHAPTERS == 12)
    check("the skill is manuscript only", "Manuscript only" in skill or "manuscript only" in skill)
    check("the ten review prompts are in the skill", all(re.search(rf"\bP{n}\b", allt + (S / "reader_panel.py").read_text()) for n in range(1, 11)))
    for phrase in ("You are a nonfiction commissioning editor", "You are an independent developmental editor",
                   "You are a skeptical evidence editor", "This is an AI simulation for editorial diagnosis",
                   "You are the editorial review coordinator", "Revise only the supplied section",
                   "You are an independent nonfiction copyeditor", "Compare the revised edition with the previous edition",
                   "You are a senior nonfiction book editor reading a complete manuscript", "You are a line editor"):
        check(f"prompt present: {phrase[:40]}", phrase in allt or phrase in (S / "reader_panel.py").read_text())
    own = "".join(p.read_text() for p in list(R.glob("*.md")) + list(S.glob("*.py")) + [SK / "SKILL.md"]
                  if p.name not in ("business-file-template.md", "business-file-protocol.md"))
    check("no partner voice or partner names in an author's own book",
          not re.search(r"brian ?tracy|canfield|author\.full_name|goal number|breakthrough number", own, re.I))
    check("no em or en dashes in the prompts", not any(c in t for c in bl.DASHES for t in re.findall(r"```text\n(.*?)```", allt, re.S)))
    check("no TODO-REVIEW markers", "TODO-REVIEW" not in allt)
    check("no credentials in the skill", not re.search(r"(sk-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9]{24,}|@aimomentumlabs)", own))
    check("the fifteen questions match the intake reference", all(q in (R / "intake.md").read_text() for _, q, _ in bl.QUESTIONS))
    tpl = (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
    check("the template has §23 Book", "## 23. Book" in tpl and "Built by: AI Momentum Labs Book Builder" in tpl)
    check("the template is version 1.9", "**File version:** 1.9" in tpl)
    check("the spec documents §23", "| 23 | Book |" in (ROOT / "BUSINESS-FILE-SPEC.md").read_text())
    check("the skill's template copy matches", (R / "business-file-template.md").read_bytes() == (ROOT / "templates/BUILDROOM_BUSINESS_FILE.md").read_bytes())
    check("the navigator's roadmap names the skill", "buildroom-book-builder" in (ROOT / "skills/buildroom-os/references/roadmap.md").read_text())
    check("the universal CLAUDE.md lists the skill and the book rule", "buildroom-book-builder" in (ROOT / "rollout/universal/CLAUDE.md").read_text()
          and "**Books:**" in (ROOT / "rollout/universal/CLAUDE.md").read_text())
    check("the viewer knows §23", '23:{t:"Book"' in (ROOT / "rollout/Business_File_Viewer.html").read_text())


def main():
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="book-tests-"))
    try:
        B = t_setup(tmp)
        t_plan(tmp, B)
        t_manuscript(tmp, B)
        t_issues(tmp, B)
        t_readers(tmp, B)
        t_checks(tmp, B)
        t_consistency()
    finally:
        if keep:
            print("kept", tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    bad = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
