#!/usr/bin/env python3
"""AI Momentum Labs Book Builder: the book's folder, settings, intake, sources, plan, book record and stages.

A book lives in book/<slug>/ beside the member's Business File (inside their Obsidian vault when
they keep one). Twelve chapters and about 62,000 words are the defaults; the member can change
the chapter count, the total, or any one chapter's length at any time.

Usage
  book_plan.py init     --book book/<slug> [--author "Name"] [--working-title "…"] [--chapters 12] [--words 62000]
  book_plan.py settings --book B [--chapters N] [--words N] [--chapter-words 4=6000 9=3000] [--grade-max 9]
  book_plan.py intake   --book B                         which of the 15 questions are answered, and where the rest may be
  book_plan.py answer   --book B --key reader --text '…' | --text-file path [--from "§2"] [--append]
                        (keys: book_plan.py intake lists them. Use single quotes or a file: inside double quotes
                        the shell eats dollar amounts. --append adds a follow-up answer instead of replacing.)
  book_plan.py intake-gate --book B --verdict ready|hold [--gap "…"]... [--question "…"]... --by editor
  book_plan.py source   --book B add --title "…" --kind own|client|public|transcript [--ref path-or-url]
                                     [--permission "documented: signed release 2026-10-02" | "not needed"]
  book_plan.py source   --book B scan [--vault path] [--query "words"] [--limit 25]
                        notes in the member's Obsidian vault that look relevant; adds nothing by itself
  book_plan.py source   --book B list | remove --id S-003 | set --id S-003 --permission "documented: …"
  book_plan.py plan-check --book B                       validates plan.json and writes plan.md
  book_plan.py approve  --book B --what outline|sample --by member [--note "…"] [--feedback "…"]
  book_plan.py record   --book B add --kind term|framework|name|story|promise|summary --text "…" [--chapter N]
  book_plan.py record   --book B show [--upto N]         the book record: what earlier chapters established
  book_plan.py record   --book B remove --kind story --text "…"      (a story that was cut)
  book_plan.py stage    --book B --name memo|edit|review|facts|copyedit|regression --status done|in progress
                                 [--evidence path-in-the-book] [--by editor|reviewer] [--edition label] [--note "…"]
                        (review, facts, copyedit and regression need --by reviewer; regression needs --edition.
                        --book may be left out when there is one book under book/.)
  book_plan.py status   --book B
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import booklib as bl  # noqa: E402

CORE = ("about", "reader", "transformation", "method", "voice")
MIN_ANSWERS = 8
SOURCE_KINDS = ("own", "client", "public", "transcript")
RECORD_KINDS = ("term", "framework", "name", "story", "promise", "summary")
EVIDENCE_STAGES = {"memo": "edit/memo.md", "edit": "edit/changelog.md", "review": "review/developmental-review.md",
                   "facts": "review/claim-ledger.md", "copyedit": "review/copyedit.md",
                   "regression": "review/regression.md"}
INDEPENDENT = ("review", "facts", "copyedit", "regression")   # never done by the session that drafted or edited


def cmd_init(a):
    book = Path(a.book)
    if (book / "book.json").exists():
        return {"ok": True, "created": False, **status(bl.load_book(book), book)}
    if a.chapters < 1 or a.words < 1000:
        bl.refuse("--chapters must be at least 1 and --words at least 1000")
    data = {"schema": "buildroom-book/1", "slug": book.name, "created": bl.today(), "author": a.author or "",
            "working_title": a.working_title or "",
            "settings": {"chapters": a.chapters, "words": a.words, "chapter_words": {}, "grade_max": 9},
            "stages": {}, "approvals": [], "editions": []}
    for d in ("manuscript", "sources", "edit", "review", "readers", "editions"):
        (book / d).mkdir(parents=True, exist_ok=True)
    bl.write_json(book / "intake.json", {"answers": {}})
    bl.write_json(book / "sources.json", {"sources": []})
    bl.write_json(book / "record.json", {"entries": []})
    bl.save_book(book, data)
    return {"ok": True, "created": True, "book": str(book), "settings": data["settings"], "targets": bl.targets(data)}


def cmd_settings(a):
    data = bl.load_book(a.book)
    s = data["settings"]
    changed = []
    if a.chapters is not None:
        if a.chapters < 1:
            bl.refuse("--chapters must be at least 1")
        s["chapters"] = a.chapters
        s["chapter_words"] = {k: v for k, v in s["chapter_words"].items() if int(k) <= a.chapters}
        changed.append("chapters")
    if a.words is not None:
        if a.words < 1000:
            bl.refuse("--words must be at least 1000")
        s["words"] = a.words
        changed.append("words")
    for item in a.chapter_words or []:
        m = re.fullmatch(r"(\d+)=(\d+)", item)
        if not m or not 1 <= int(m.group(1)) <= s["chapters"] or int(m.group(2)) < 200:
            bl.refuse(f"--chapter-words takes N=words for a chapter in the book, at least 200 words: {item}")
        s["chapter_words"][m.group(1)] = int(m.group(2))
        changed.append(f"chapter {m.group(1)}")
    if a.grade_max is not None:
        if not 3 <= a.grade_max <= 18:
            bl.refuse("--grade-max is a school grade from 3 to 18 (9 is the default)")
        s["grade_max"] = a.grade_max
        changed.append("grade_max")
    warn = []
    if changed and bl.stage(data, "outline").get("status") == "approved" and ("chapters" in changed):
        bl.set_stage(data, "outline", "needs re-approval", note="chapter count changed after approval")
        warn.append("the chapter count changed after the outline was approved: update plan.json and approve it again")
    bl.save_book(a.book, data)
    return {"ok": True, "changed": changed, "settings": s, "targets": bl.targets(data), "warnings": warn}


def intake_state(book):
    ans = bl.read_json(Path(book) / "intake.json", {"answers": {}})["answers"]
    rows = []
    for key, q, helper in bl.QUESTIONS:
        t = (ans.get(key) or {}).get("text", "").strip()
        rows.append({"key": key, "question": q, "helper": helper, "answered": bool(t),
                     "from": (ans.get(key) or {}).get("from", ""), "may_be_in_file": bl.FROM_FILE.get(key, "")})
    return ans, rows


def cmd_intake(a):
    bl.load_book(a.book)
    ans, rows = intake_state(a.book)
    done = [r["key"] for r in rows if r["answered"]]
    return {"ok": True, "answered": len(done), "of": len(rows), "missing": [r for r in rows if not r["answered"]],
            "core_missing": [k for k in CORE if k not in done],
            "enough_to_review": len(done) >= MIN_ANSWERS and all(k in done for k in CORE)}


def cmd_answer(a):
    bl.load_book(a.book)
    if a.key not in bl.QUESTION_KEYS:
        bl.refuse(f"unknown key {a.key}; keys: {', '.join(bl.QUESTION_KEYS)}")
    text = bl.arg_text(a.text, a.text_file)
    if not text:
        bl.refuse("the answer is empty (--text '…' or --text-file path)")
    p = Path(a.book) / "intake.json"
    d = bl.read_json(p, {"answers": {}})
    old = (d["answers"].get(a.key) or {}).get("text", "")
    if a.append and old:
        text = old + "\n\n" + text
    d["answers"][a.key] = {"text": text, "from": getattr(a, "from") or "member", "date": bl.today()}
    bl.write_json(p, d)
    md = ["# Author intake", ""]
    for key, q, _ in bl.QUESTIONS:
        t = (d["answers"].get(key) or {}).get("text", "")
        md += [f"## {q}", "", t or "_not answered yet_", ""]
    bl.write_atomic(Path(a.book) / "intake.md", "\n".join(md))
    warn = []
    if old and not a.append:
        warn.append("this replaced the earlier answer; use --append to add a follow-up answer to it instead")
    if bl.eaten_dollars(text):
        warn.append("this answer has a figure that starts with a comma (" + ", ".join(bl.eaten_dollars(text)[:3]) + "): the "
                    "shell probably swallowed a dollar amount. Put the answer in a file and use --text-file")
    return {"ok": True, "key": a.key, "answered": sum(1 for k in bl.QUESTION_KEYS if (d["answers"].get(k) or {}).get("text")),
            "warnings": warn}


def cmd_intake_gate(a):
    data = bl.load_book(a.book)
    ans, rows = intake_state(a.book)
    done = [r["key"] for r in rows if r["answered"]]
    if a.verdict == "ready":
        missing_core = [k for k in CORE if k not in done]
        if len(done) < MIN_ANSWERS or missing_core:
            bl.refuse(f"not enough to outline: {len(done)} of 15 answered"
                      + (f"; still needed: {', '.join(missing_core)}" if missing_core else f"; at least {MIN_ANSWERS} are needed"))
        if a.gap:
            bl.refuse("READY with open gaps is a HOLD: ask the follow-up questions first, or drop the gaps you can live with")
        bl.set_stage(data, "intake", "ready", by=a.by, gaps=[], questions=[])
    else:
        if not a.question:
            bl.refuse("a HOLD names the exact questions to ask the author (--question)")
        bl.set_stage(data, "intake", "hold", by=a.by, gaps=a.gap, questions=a.question[:7])
    bl.save_book(a.book, data)
    return {"ok": True, "verdict": a.verdict.upper(), "stage": data["stages"]["intake"]}


SCAN_SKIP = {"book", "backups", "node_modules", "templates", "attachments", "dist"}
SCAN_STOP = set("about after again their there these those which while would could should being because before between "
                "people thing things every other really through where still little always never might first".split())


def scan_vault(book, vault, query, limit):
    """Notes in the member's vault (or any folder of their own writing) that look relevant to this book, ranked
    by how many of the book's own words they share. Read-only: nothing is added until the member says so."""
    root = Path(vault).resolve()
    if not root.is_dir():
        bl.refuse(f"no folder at {vault}")
    ans = bl.read_json(Path(book) / "intake.json", {"answers": {}})["answers"]
    plan = bl.read_json(Path(book) / "plan.json", {"chapters": []})
    seed = " ".join((ans.get(k) or {}).get("text", "") for k in ("about", "reader", "method", "mistake", "myth", "lessons"))
    seed += " " + str(plan.get("title", "")) + " " + " ".join(str(c.get("title", "")) + " " + str(c.get("idea", ""))
                                                               for c in plan.get("chapters") or [] if isinstance(c, dict))
    keys = {w for w in re.findall(r"[a-z][a-z'-]{4,}", (seed + " " + (query or "")).lower()) if w not in SCAN_STOP}
    if not keys:
        bl.refuse("nothing to match on yet: answer the intake first, or give --query \"words about the book\"")
    have = {str(s.get("ref", "")) for s in bl.read_json(Path(book) / "sources.json", {"sources": []})["sources"]}
    book_dir = Path(book).resolve()
    rows, seen = [], 0
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(root)
        if not f.is_file() or f.suffix.lower() not in (".md", ".txt") or any(p.startswith(".") or p.lower() in SCAN_SKIP for p in rel.parts[:-1]):
            continue
        if book_dir in f.resolve().parents or f.name.startswith("BUILDROOM_BUSINESS_FILE") or f.stat().st_size > 2_000_000:
            continue
        seen += 1
        text = bl.read_text(f)
        n = bl.words(text)
        if n < 150:
            continue
        low = set(re.findall(r"[a-z][a-z'-]{4,}", text.lower()))
        hit = sorted(keys & low)
        if len(hit) < 3:
            continue
        head = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")), f.stem)
        rows.append({"path": str(f), "title": head[:80], "words": n, "matches": len(hit), "matched": hit[:8],
                     "already_a_source": str(f) in have or str(rel) in have})
    rows.sort(key=lambda r: (-r["matches"], -r["words"]))
    return {"ok": True, "vault": str(root), "notes_read": seen, "candidates": rows[:limit], "more": max(0, len(rows) - limit),
            "next": "read the list to the member; for each note they choose: book_plan.py source add --title \"…\" --kind "
                    "own|transcript|client|public --ref \"<path>\". The checks then read the note where it sits.",
            "care": "a match on words is not a judgment: the member decides what is theirs to use. Notes about clients "
                    "are client sources and need permission; notes copied from other authors are public sources, quoted "
                    "and credited, never passed off as the author's own."}


def cmd_source(a):
    bl.load_book(a.book)
    p = Path(a.book) / "sources.json"
    d = bl.read_json(p, {"sources": []})
    if a.action == "list":
        return {"ok": True, "sources": d["sources"]}
    if a.action == "scan":
        return scan_vault(a.book, a.vault or ".", a.query, a.limit)
    if a.action in ("remove", "set"):
        src = next((x for x in d["sources"] if str(x.get("id", "")).lower() == (a.id or "").lower()), None)
        if not src:
            bl.refuse(f"no source {a.id}; book_plan.py source list")
        if a.action == "remove":
            plan = bl.read_json(Path(a.book) / "plan.json", {"chapters": []})
            used = [i for i, c in enumerate(plan.get("chapters") or [], 1) if isinstance(c, dict) and src["id"] in (c.get("sources") or [])]
            if used:
                bl.refuse(f"{src['id']} is planned for chapter(s) {', '.join(map(str, used))}; take it out of plan.json first")
            d["sources"].remove(src)
        else:
            if not (a.permission or a.title or a.ref):
                bl.refuse("source set changes --permission, --title or --ref")
            src.update({k: v.strip() for k, v in (("permission", a.permission), ("title", a.title), ("ref", a.ref)) if v})
        bl.write_json(p, d)
        return {"ok": True, "id": src["id"], "action": a.action, "source": src}
    if not a.title or a.kind not in SOURCE_KINDS:
        bl.refuse(f"source add needs --title and --kind ({', '.join(SOURCE_KINDS)})")
    perm = (a.permission or "").strip()
    if a.kind == "client" and not perm:
        perm = "not documented"
    nums = [int(m.group(1)) for m in (re.fullmatch(r"S-(\d+)", str(x.get("id", ""))) for x in d["sources"]) if m]
    sid = f"S-{max(nums + [int(d.get('last_id', 0))], default=0) + 1:03d}"
    d["last_id"] = int(sid[2:])
    d["sources"].append({"id": sid, "title": a.title.strip(), "kind": a.kind, "ref": a.ref or "",
                         "permission": perm or ("not needed" if a.kind in ("own", "transcript") else "not documented"),
                         "added": bl.today()})
    bl.write_json(p, d)
    return {"ok": True, "id": sid, "source": d["sources"][-1]}


def check_plan(book, data):
    plan = bl.read_json(Path(book) / "plan.json")
    problems, warnings = [], []
    if not isinstance(plan.get("chapters") or [], list) or any(not isinstance(c, dict) for c in plan.get("chapters") or []):
        bl.refuse("plan.json: 'chapters' is a list of chapter objects (see references/outline.md)")
    for k in ("title", "promise", "voice", "thread", "conclusion"):
        if not str(plan.get(k, "")).strip():
            problems.append(f"plan.json has no {k}")
    chs = plan.get("chapters") or []
    want = int(data["settings"]["chapters"])
    if len(chs) != want:
        problems.append(f"the plan has {len(chs)} chapters; the book is set to {want} "
                        f"(change the plan, or book_plan.py settings --chapters {len(chs)})")
    titles = [str(c.get("title", "")).strip() for c in chs]
    if any(not t for t in titles):
        problems.append("a chapter has no title")
    if len(set(t.lower() for t in titles)) != len(titles):
        problems.append("two chapters share a title")
    srcs = {s["id"]: s for s in bl.read_json(Path(book) / "sources.json", {"sources": []})["sources"]}
    sids = set(srcs)
    seen = {}
    for i, c in enumerate(chs, 1):
        if c.get("n") not in (None, i):
            problems.append(f"chapter {i} is numbered {c.get('n')}")
        if bl.words(str(c.get("brief", ""))) < 40:
            problems.append(f"chapter {i}: the brief is under 40 words; it needs the one idea, the story or example, "
                            "the steps it teaches and the takeaway")
        if not str(c.get("idea", "")).strip():
            warnings.append(f"chapter {i}: no one-line idea")
        for st in c.get("stories") or []:
            key = st.strip().lower()
            if key in seen:
                problems.append(f"the story '{st}' is planned for chapters {seen[key]} and {i}; a story is told once")
            seen[key] = i
        for s in c.get("sources") or []:
            if s not in sids:
                problems.append(f"chapter {i} names {s}, which is not in sources.json")
            elif srcs[s].get("kind") == "client" and not str(srcs[s].get("permission", "")).lower().startswith(
                    ("documented", "anonymised", "anonymized")):
                warnings.append(f"chapter {i} draws on {s}, a client story with no documented permission yet: get it "
                                "(or anonymise the story) before the chapter is drafted; the gate will block it")
    dash = [k for k in ("title", "subtitle", "promise") if bl.dash_count(str(plan.get(k, "")))]
    dash += [f"chapter {i} title" for i, t in enumerate(titles, 1) if bl.dash_count(t)]
    if dash:
        problems.append("em or en dashes (or a double hyphen) in: " + ", ".join(dash))
    if chs and not any(c.get("stories") for c in chs):
        warnings.append("no chapter names a story from the author's own material")
    return plan, problems, warnings


def cmd_plan_check(a):
    data = bl.load_book(a.book)
    plan, problems, warnings = check_plan(a.book, data)
    t = bl.targets(data)
    md = [f"# {plan.get('title', '')}", "", plan.get("subtitle", ""), "", f"**Promise:** {plan.get('promise', '')}", "",
          f"**Voice:** {plan.get('voice', '')}", "", f"**Thread:** {plan.get('thread', '')}", ""]
    for i, c in enumerate(plan.get("chapters") or [], 1):
        md += [f"## Chapter {i}: {c.get('title', '')}", "", f"_About {t.get(f'Chapter {i}', 0):,} words._", "",
               c.get("brief", ""), ""]
        if c.get("stories"):
            md += ["Stories: " + "; ".join(c["stories"]), ""]
    md += ["## Conclusion", "", plan.get("conclusion", ""), ""]
    bl.write_atomic(Path(a.book) / "plan.md", "\n".join(md))
    ost = bl.stage(data, "outline")
    changed = ost.get("status") == "approved" and ost.get("sha256") and ost["sha256"] != bl.file_sha(Path(a.book) / "plan.json")
    if changed:
        bl.set_stage(data, "outline", "needs re-approval", note="plan.json changed after the member approved it")
        warnings.append("the plan changed after the member approved it: show them the change and approve again")
        bl.save_book(a.book, data)
    elif not problems and ost.get("status") in ("not started", "needs re-approval"):
        bl.set_stage(data, "outline", "ready for approval")
        bl.save_book(a.book, data)
    return {"ok": not problems, "problems": problems, "warnings": warnings, "chapters": len(plan.get("chapters") or []),
            "plan_md": str(Path(a.book) / "plan.md"), "targets": t}


def cmd_approve(a):
    data = bl.load_book(a.book)
    if a.by != "member":
        bl.refuse("only the member approves the outline and the sample chapter (--by member)")
    if a.what == "outline":
        _, problems, _ = check_plan(a.book, data)
        if problems:
            bl.refuse("the plan has problems; fix them before approval", problems=problems)
        if bl.stage(data, "intake").get("status") != "ready":
            bl.refuse("the intake gate has not said READY (book_plan.py intake-gate)")
        bl.set_stage(data, "outline", "approved", by="member", note=a.note or "",
                     sha256=bl.file_sha(Path(a.book) / "plan.json"))
    else:
        sample = Path(a.book) / "edit" / "sample.md"
        if not sample.is_file() or bl.words(bl.read_text(sample)) < 30:
            bl.refuse("no edited sample chapter at edit/sample.md (the original and the edit, side by side)")
        if bl.stage(data, "outline").get("status") != "approved":
            bl.refuse("the outline is not approved, so there is no agreed book to edit a sample of")
        if bl.stage(data, "memo").get("status") != "done":
            bl.refuse("the developmental memo comes first: the sample chapter is edited to the memo and the style guide "
                      "(book_plan.py stage --name memo --status done)")
        bl.set_stage(data, "sample", "approved", by="member", note=a.note or "", feedback=a.feedback or "",
                     sha256=bl.file_sha(sample))
    data["approvals"].append({"what": a.what, "by": "member", "date": bl.today(), "note": a.note or "",
                              "feedback": a.feedback or ""})
    bl.save_book(a.book, data)
    return {"ok": True, "approved": a.what, "feedback": a.feedback or ""}


def cmd_record(a):
    bl.load_book(a.book)
    p = Path(a.book) / "record.json"
    d = bl.read_json(p, {"entries": []})
    if a.action == "show":
        ents = [e for e in d["entries"] if a.upto is None or e.get("chapter") is None or e["chapter"] <= a.upto]
        by = {}
        for e in ents:
            by.setdefault(e["kind"], []).append(e)
        return {"ok": True, "entries": len(ents), "record": by}
    if a.action == "remove":
        keep = [e for e in d["entries"] if not (e["kind"] == a.kind and e["text"].strip().lower() == (a.text or "").strip().lower())]
        if len(keep) == len(d["entries"]):
            bl.refuse(f"no {a.kind} entry with exactly that text; book_plan.py record show")
        d["entries"] = keep
        bl.write_json(p, d)
        return {"ok": True, "entries": len(keep), "removed": a.text}
    a.text = bl.arg_text(a.text, a.text_file)
    if a.kind not in RECORD_KINDS or not a.text:
        bl.refuse(f"record add needs --kind ({', '.join(RECORD_KINDS)}) and --text (or --text-file)")
    if a.kind == "summary" and a.chapter is None:
        bl.refuse("a summary belongs to a chapter (--chapter N)")
    if a.kind == "summary":
        d["entries"] = [e for e in d["entries"] if not (e["kind"] == "summary" and e.get("chapter") == a.chapter)]
    warn = []
    if a.kind == "story":
        for e in d["entries"]:
            if e["kind"] == "story" and e["text"].strip().lower() == a.text.strip().lower() and e.get("chapter") != a.chapter:
                warn.append(f"this story is already recorded for chapter {e.get('chapter')}")
        plan = bl.read_json(Path(a.book) / "plan.json", {"chapters": []})
        for n, c in enumerate(plan.get("chapters") or [], 1):
            if isinstance(c, dict) and n != a.chapter and a.text.strip().lower() in [str(x).strip().lower() for x in c.get("stories") or []]:
                warn.append(f"the plan gives this story to chapter {n}; a story is told once, so change the plan or the chapter")
    d["entries"].append({"kind": a.kind, "text": a.text.strip(), "chapter": a.chapter, "date": bl.today()})
    bl.write_json(p, d)
    return {"ok": True, "entries": len(d["entries"]), "warnings": warn}


def cmd_stage(a):
    data = bl.load_book(a.book)
    if a.name not in EVIDENCE_STAGES:
        bl.refuse(f"--name is one of {', '.join(EVIDENCE_STAGES)}; the intake, outline, sample, readers and gate "
                  "stages have their own commands")
    root = Path(a.book).resolve()
    ev = (root / (a.evidence or EVIDENCE_STAGES[a.name])).resolve()
    if root != ev and root not in ev.parents:
        bl.refuse(f"the {a.name} report lives inside the book folder (the default is {EVIDENCE_STAGES[a.name]})")
    rel = ev.relative_to(root)
    if rel.parts and rel.parts[0] in ("manuscript", "editions", "sources"):
        bl.refuse(f"{rel} is the book itself, not a report on it; the {a.name} report goes in {EVIDENCE_STAGES[a.name]}")
    labels = [e["label"] for e in data.get("editions", [])]
    if a.status == "done":
        if not ev.is_file() or bl.words(bl.read_text(ev)) < 30:
            bl.refuse(f"{a.name} cannot be marked done without its report at {rel} (at least a few lines)")
        if a.name == "memo" and not (root / "edit" / "styleguide.md").is_file():
            bl.refuse("the memo comes with a style guide: write edit/styleguide.md (see references/editing.md)")
        prev = bl.stage(data, a.name)
        if a.name == "regression" and prev.get("report_sha") == bl.file_sha(ev) and prev.get("edition") \
                and prev["edition"] != bl.slugify(a.edition or ""):
            bl.refuse(f"review/regression.md is the report on edition {prev['edition']}, unchanged. The regression check "
                      f"is run again on edition {a.edition} and the report rewritten before it is marked done")
        if a.name in INDEPENDENT and a.by in ("editor", "drafter"):
            bl.refuse(f"the {a.name} is done by an independent reader that did not draft or edit the book: run it in a "
                      "separate session or subagent and record it with --by reviewer")
        if a.edition and bl.slugify(a.edition) not in labels:
            bl.refuse(f"no edition {a.edition}; freeze it first (manuscript.py edition)")
        if a.name == "regression" and not a.edition:
            bl.refuse("the regression check names the edition it read (--edition <label>): it is run on the final "
                      "frozen edition, and the gate checks that nothing changed after it")
    bl.set_stage(data, a.name, a.status, by=a.by, evidence=str(rel) if ev.exists() else "",
                 note=a.note or "", edition=bl.slugify(a.edition) if a.edition else "",
                 report_sha=bl.file_sha(ev) if ev.is_file() else "")
    bl.save_book(a.book, data)
    return {"ok": True, "stage": a.name, **data["stages"][a.name]}


def status(data, book):
    st = {n: bl.stage(data, n).get("status", "not started") for n in bl.STAGES}
    nxt = next((n for n in bl.STAGES if st[n] not in ("ready", "approved", "done", "passed", "waived", "go")), None)
    return {"book": str(book), "title": data.get("working_title", ""), "settings": data["settings"], "stages": st,
            "next": nxt, "editions": [e["label"] for e in data.get("editions", [])]}


def cmd_status(a):
    data = bl.load_book(a.book)
    return {"ok": True, **status(data, a.book)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--book")
        return x
    x = p("init"); x.add_argument("--author"); x.add_argument("--working-title")
    x.add_argument("--chapters", type=int, default=bl.DEFAULT_CHAPTERS); x.add_argument("--words", type=int, default=bl.DEFAULT_WORDS)
    x = p("settings"); x.add_argument("--chapters", type=int); x.add_argument("--words", type=int)
    x.add_argument("--chapter-words", nargs="*"); x.add_argument("--grade-max", type=float)
    p("intake")
    x = p("answer"); x.add_argument("--key", required=True); x.add_argument("--text"); x.add_argument("--text-file")
    x.add_argument("--from"); x.add_argument("--append", action="store_true")
    x = p("intake-gate"); x.add_argument("--verdict", choices=["ready", "hold"], required=True)
    x.add_argument("--gap", action="append", default=[]); x.add_argument("--question", action="append", default=[])
    x.add_argument("--by", default="editor")
    x = p("source"); x.add_argument("action", choices=["add", "list", "remove", "set", "scan"]); x.add_argument("--title")
    x.add_argument("--vault"); x.add_argument("--query"); x.add_argument("--limit", type=int, default=25)
    x.add_argument("--kind"); x.add_argument("--ref"); x.add_argument("--permission"); x.add_argument("--id")
    p("plan-check")
    x = p("approve"); x.add_argument("--what", choices=["outline", "sample"], required=True); x.add_argument("--by", required=True)
    x.add_argument("--note"); x.add_argument("--feedback")
    x = p("record"); x.add_argument("action", choices=["add", "show", "remove"]); x.add_argument("--kind"); x.add_argument("--text")
    x.add_argument("--text-file")
    x.add_argument("--chapter", type=int); x.add_argument("--upto", type=int)
    x = p("stage"); x.add_argument("--name", required=True); x.add_argument("--status", choices=["done", "in progress"], required=True)
    x.add_argument("--evidence"); x.add_argument("--by", default="editor"); x.add_argument("--note"); x.add_argument("--edition")
    p("status")
    a = ap.parse_args()
    if a.cmd != "init" or not a.book:
        a.book = bl.find_book(a.book)
    out = globals()["cmd_" + a.cmd.replace("-", "_")](a)
    bl.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
