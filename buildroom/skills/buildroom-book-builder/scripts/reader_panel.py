#!/usr/bin/env python3
"""AI Momentum Labs Book Builder: test readers, simulated and real, never mixed.

Simulated readers are an editorial diagnosis: one independent run per persona, each in a fresh
session that sees only its persona, the book's promise and a frozen edition. Real readers are
people, recruited by the author, given the same brief and questionnaire, known here only by an
anonymous code. Their scores are never pooled with simulations, and a simulation is never counted
as a person, quoted as a testimonial or used as market evidence.

Usage
  reader_panel.py personas     --book B [--add "id|role|experience|goal|constraints|skepticism"]...
  reader_panel.py brief        --book B --persona beginner --edition v1 [--round 1]     writes the simulation brief
  reader_panel.py record-sim   --book B --persona beginner --report path.md --clarity 3 --relevance 4 --usefulness 3 [--round 1]
  reader_panel.py invite       --book B --roles target,target,target,target,skeptic,expert [--round 1]
  reader_panel.py questionnaire --book B --edition v1 [--round 1] [--days 14]            the brief and questions to send
  reader_panel.py record-human --book B --code R-01 --finished yes|no [--stopped-at "Chapter 4"]
                               --promise-explained yes|no --next-step yes|no --clarity 4 --usefulness 5
                               --recommend yes|no [--notes path.md] [--round 1]
  reader_panel.py consolidate  --book B [--round 1]      counts, medians and the thresholds, humans and simulations apart
  reader_panel.py waive        --book B --by member --reason "…" [--round 1]            going ahead without enough real readers
Thresholds (decision aids, not proof the book will sell): no open P0 or P1 issue; at least 80 percent of
target-reader respondents can explain the promise and the next step without coaching; median clarity and
median practical usefulness at least 4 of 5; at least 3 real respondents, 2 of them target readers.
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, statistics, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import booklib as bl  # noqa: E402
import issues as iss  # noqa: E402

DEFAULT_PERSONAS = [
    {"id": "beginner", "role": "a close match to the intended reader, new to the subject",
     "experience": "has the problem the book solves; has read little or nothing on it",
     "goal": "wants the result the book promises", "constraints": "reads in the evening, a chapter at a time",
     "skepticism": "open, but will stop if a step is unclear"},
    {"id": "time-poor", "role": "a busy practitioner who fits the intended reader",
     "experience": "some experience; has tried the obvious things", "goal": "wants what to do on Monday",
     "constraints": "skims; reads openings and steps, skips stories that run long",
     "skepticism": "impatient with repetition and warm-up"},
    {"id": "skeptic", "role": "an experienced reader who has read the well-known books on this subject",
     "experience": "years in the field", "goal": "wants something they have not heard before",
     "constraints": "compares every claim with what they already know",
     "skepticism": "high; doubts any result without evidence"},
    {"id": "tried-and-failed", "role": "a reader who has tried to solve this more than once and failed",
     "experience": "has bought courses or books that did not work for them", "goal": "wants to know why this time is different",
     "constraints": "tired, a little defensive", "skepticism": "expects to be blamed or oversold"},
]
ROLES = ("target", "skeptic", "expert")
MIN_HUMANS, MIN_TARGET, PASS_SHARE, PASS_MEDIAN = 3, 2, 0.8, 4

P4 = """This is an AI simulation for editorial diagnosis, not feedback from a real person.
Simulate only the supplied reader persona. Do not invent actual reading sessions, purchases or results.
Assess the supplied manuscript without seeing other simulated readers' reviews.
At each chapter, record: what this persona would likely understand, confusing prerequisites, unsupported
claims, likely stop points, actionable next step, and exact passages causing friction.
Score clarity, relevance and practical usefulness from 1 to 5 with evidence, not flattery.
Separate text-based observations from predictions about behavior.
End with the three revisions most likely to help this persona and the questions real readers must answer.
Do not generate testimonials or claim market validation. Disclose incomplete manuscript coverage.
Cite the paragraph IDs (for example C03-P012) for every passage you mention.
"""

P5 = """Thank you for testing this draft. We need honest reactions, not encouragement.
Please read naturally and independently. Do not force yourself to finish.
Mark the chapter and paragraph wherever you become confused, skeptical, bored, or especially engaged.
Please do not share the review copy. Avoid including anyone else's private information in your feedback.

Before reading: What would you hope to learn from this title and description?

After each chapter:
1. In your own words, what was the main point?
2. What could you do differently because of it?
3. Where did you need an explanation or example that was missing?
4. What felt repetitive, implausible, or unnecessary?
5. Where did you naturally stop, skim, or want to stop?
6. Rate clarity and practical usefulness from 1 to 5, and explain your ratings.

After reading, or after choosing to stop:
1. What promise did you think this book made? Did it deliver?
2. Who would benefit most, and who would not?
3. Which three passages or ideas should definitely stay?
4. Which three things should be cut or improved first?
5. Try one exercise or process if appropriate. What did you actually do, and where did you get stuck?
6. What important question remains unanswered?
7. Would you recommend the book? Why or why not?
8. Did anything appear inaccurate, inappropriate to share, or unsafe?
Please give chapter/paragraph locations wherever possible. You are not being asked for a public review.
"""


def rdir(book, rnd):
    return Path(book) / "readers" / f"round-{rnd}"


def load_round(book, rnd):
    return bl.read_json(rdir(book, rnd) / "round.json", {"round": rnd, "simulated": [], "humans": [], "waiver": None})


def save_round(book, rnd, d):
    bl.write_json(rdir(book, rnd) / "round.json", d)


def yes(v):
    return str(v).lower() in ("yes", "y", "true", "1")


def cmd_personas(a):
    bl.load_book(a.book)
    p = Path(a.book) / "readers" / "personas.json"
    d = bl.read_json(p, {"personas": [dict(x) for x in DEFAULT_PERSONAS]})
    for item in a.add or []:
        parts = [x.strip() for x in item.split("|")]
        if len(parts) != 6 or not all(parts):
            bl.refuse('--add takes "id|role|experience|goal|constraints|skepticism"')
        d["personas"] = [x for x in d["personas"] if x["id"] != bl.slugify(parts[0])]
        d["personas"].append(dict(zip(("id", "role", "experience", "goal", "constraints", "skepticism"),
                                      [bl.slugify(parts[0])] + parts[1:])))
    bl.write_json(p, d)
    return {"ok": True, "personas": [x["id"] for x in d["personas"]],
            "note": "editorial lenses, not demographic stereotypes; fit each to the reader in the intake before running it"}


def cmd_brief(a):
    bl.load_book(a.book)
    per = bl.read_json(Path(a.book) / "readers" / "personas.json", {"personas": DEFAULT_PERSONAS})["personas"]
    p = next((x for x in per if x["id"] == a.persona), None)
    if not p:
        bl.refuse(f"no persona {a.persona}; have: {', '.join(x['id'] for x in per)}")
    ed = Path(a.book) / "editions" / bl.slugify(a.edition) / "manuscript.ids.md"
    if not ed.exists():
        bl.refuse(f"no edition {a.edition}; freeze one first (manuscript.py edition)")
    plan = bl.read_json(Path(a.book) / "plan.json", {})
    intake = bl.read_json(Path(a.book) / "intake.json", {"answers": {}})["answers"]
    reader = (intake.get("reader") or {}).get("text", "")
    out = rdir(a.book, a.round) / "sim" / f"{a.persona}.brief.md"
    body = (P4 + "\nPERSONA:\n" + "\n".join(f"- {k}: {p[k]}" for k in ("role", "experience", "goal", "constraints", "skepticism"))
            + (f"\n- the author's intended reader, for fit: {reader}" if reader else "")
            + f"\n\nBOOK PROMISE:\n{plan.get('promise', '(see the title page)')}\n\nMANUSCRIPT:\nRead the whole file at "
            + f"{ed} (edition {bl.slugify(a.edition)}). Read nothing else in the book folder.\n\n"
            + f"Write your report to {rdir(a.book, a.round) / 'sim' / (a.persona + '.md')}. Head it "
            + "\"SIMULATED READER, not a real person\".\n")
    bl.write_atomic(out, body)
    return {"ok": True, "brief": str(out), "run": "one fresh session or subagent per persona, given only this brief",
            "report_to": str(rdir(a.book, a.round) / "sim" / f"{a.persona}.md")}


def score(v, name):
    if v is None or not 1 <= v <= 5:
        bl.refuse(f"--{name} is a whole number from 1 to 5")
    return v


def cmd_record_sim(a):
    bl.load_book(a.book)
    rep = Path(a.report)
    if not rep.is_file() or bl.words(bl.read_text(rep)) < 80:
        bl.refuse(f"no simulated-reader report at {rep} (or it is only a few lines)")
    if "simulat" not in bl.read_text(rep)[:400].lower():
        bl.refuse('the report must say at the top that it is a simulated reader, not a real person')
    d = load_round(a.book, a.round)
    d["simulated"] = [x for x in d["simulated"] if x["persona"] != a.persona]
    d["simulated"].append({"persona": a.persona, "report": str(rep), "clarity": score(a.clarity, "clarity"),
                           "relevance": score(a.relevance, "relevance"), "usefulness": score(a.usefulness, "usefulness"),
                           "date": bl.today()})
    save_round(a.book, a.round, d)
    return {"ok": True, "simulated_readers": len(d["simulated"])}


def cmd_invite(a):
    bl.load_book(a.book)
    roles = [r.strip().lower() for r in a.roles.split(",") if r.strip()]
    if not roles or any(r not in ROLES for r in roles):
        bl.refuse(f"--roles is a comma list of {', '.join(ROLES)}")
    d = load_round(a.book, a.round)
    start = len(d["humans"])
    for i, r in enumerate(roles, start + 1):
        d["humans"].append({"code": f"R-{i:02d}", "role": r, "status": "invited", "invited": bl.today()})
    save_round(a.book, a.round, d)
    allr = [h["role"] for h in d["humans"]]
    warn = []
    if allr.count("target") < 4:
        warn.append("fewer than four close matches to the intended reader")
    if "skeptic" not in allr:
        warn.append("no thoughtful skeptic")
    if "expert" not in allr:
        warn.append("no subject-aware reviewer (they check accuracy, separately from enjoyment)")
    if len(allr) < 6:
        warn.append("six to eight real readers is the target")
    return {"ok": True, "codes": [h["code"] for h in d["humans"][start:]], "panel": allr, "warnings": warn,
            "privacy": "keep names and contact details outside the book folder; only the codes go in here"}


def cmd_questionnaire(a):
    bl.load_book(a.book)
    ed = Path(a.book) / "editions" / bl.slugify(a.edition) / "manuscript.md"
    if not ed.exists():
        bl.refuse(f"no edition {a.edition}; freeze one first (manuscript.py edition)")
    plan = bl.read_json(Path(a.book) / "plan.json", {})
    out = rdir(a.book, a.round) / "reader-brief.md"
    head = (f"# Test-reader brief\n\n**Working title:** {plan.get('title', '')}\n\n**What it is about:** "
            f"{plan.get('promise', '')}\n\n**Please reply within {a.days} days.** You can stop early: telling us where "
            "and why you stopped is as useful as finishing.\n\n")
    bl.write_atomic(out, head + P5)
    return {"ok": True, "brief": str(out), "send_with": str(ed),
            "do_not": ["tell readers what you expect them to find", "share other readers' reactions",
                       "explain a confusing passage before their first feedback", "ask whether they loved it"]}


def cmd_record_human(a):
    bl.load_book(a.book)
    d = load_round(a.book, a.round)
    h = next((x for x in d["humans"] if x["code"].lower() == a.code.lower()), None)
    if not h:
        bl.refuse(f"no reader {a.code} in round {a.round}; invite them first")
    if a.notes and not Path(a.notes).is_file():
        bl.refuse(f"notes file not found: {a.notes}")
    h.update({"status": "responded", "responded": bl.today(), "finished": yes(a.finished),
              "stopped_at": a.stopped_at or "", "promise_explained": yes(a.promise_explained),
              "next_step": yes(a.next_step), "clarity": score(a.clarity, "clarity"),
              "usefulness": score(a.usefulness, "usefulness"), "recommend": yes(a.recommend), "notes": a.notes or ""})
    save_round(a.book, a.round, d)
    return {"ok": True, "code": h["code"], "responded": sum(1 for x in d["humans"] if x["status"] == "responded"),
            "invited": len(d["humans"]), "next": "add each problem they raised: issues.py add --source human --readers "
            + h["code"]}


def consolidate(book, rnd):
    d = load_round(book, rnd)
    resp = [h for h in d["humans"] if h["status"] == "responded"]
    target = [h for h in resp if h["role"] == "target"]
    both = [h for h in target if h["promise_explained"] and h["next_step"]]
    reg = iss.summary(bl.read_json(iss.path(book), {"issues": []}))
    med = lambda k: statistics.median([h[k] for h in resp]) if resp else None  # noqa: E731
    enough = len(resp) >= MIN_HUMANS and len(target) >= MIN_TARGET
    checks = {
        "no open P0 or P1 issue": not reg["blocking"],
        "at least 3 real respondents, 2 of them target readers": enough,
        "80 percent of target readers explain the promise and the next step": bool(target) and len(both) / len(target) >= PASS_SHARE,
        "median clarity at least 4": med("clarity") is not None and med("clarity") >= PASS_MEDIAN,
        "median practical usefulness at least 4": med("usefulness") is not None and med("usefulness") >= PASS_MEDIAN,
    }
    human = {"invited": len(d["humans"]), "responded": len(resp), "no_response": len(d["humans"]) - len(resp),
             "target_respondents": len(target),
             "promise_and_next_step": f"{len(both)} of {len(target)} target readers",
             "finished": f"{sum(1 for h in resp if h['finished'])} of {len(resp)}",
             "stopped_at": [f"{h['code']}: {h['stopped_at']}" for h in resp if not h["finished"] and h["stopped_at"]],
             "median_clarity": med("clarity"), "median_usefulness": med("usefulness"),
             "would_recommend": f"{sum(1 for h in resp if h['recommend'])} of {len(resp)}"}
    sim = {"runs": len(d["simulated"]), "personas": [s["persona"] for s in d["simulated"]],
           "scores": {s["persona"]: {k: s[k] for k in ("clarity", "relevance", "usefulness")} for s in d["simulated"]},
           "note": "simulated readers are an editorial diagnosis, not people; these scores are not added to the human ones"}
    passed = all(checks.values())
    return d, {"round": rnd, "human_readers": human, "simulated_readers": sim, "checks": checks, "passed": passed,
               "blocking_issues": reg["blocking"], "open_issues": reg["open"], "waiver": d.get("waiver")}


def cmd_consolidate(a):
    data = bl.load_book(a.book)
    d, s = consolidate(a.book, a.round)
    h, sim = s["human_readers"], s["simulated_readers"]
    md = [f"# Reader round {a.round}", "", f"**{'PASSED' if s['passed'] else 'NOT PASSED'}** · {bl.today()}", "",
          "## Real readers", "",
          f"- Invited {h['invited']}, responded {h['responded']} ({h['no_response']} no response); "
          f"{h['target_respondents']} target readers responded.",
          f"- Explained the promise and the next step without coaching: {h['promise_and_next_step']}.",
          f"- Finished: {h['finished']}." + (f" Stopped at: {'; '.join(h['stopped_at'])}." if h["stopped_at"] else ""),
          f"- Median clarity {h['median_clarity']}, median practical usefulness {h['median_usefulness']} (of 5).",
          f"- Would recommend: {h['would_recommend']}.", "",
          "## Simulated readers (an editorial diagnosis, not people)", "",
          f"- {sim['runs']} independent runs: {', '.join(sim['personas']) or 'none'}.",
          *[f"- {p}: clarity {v['clarity']}, relevance {v['relevance']}, usefulness {v['usefulness']}" for p, v in sim["scores"].items()],
          "", "## Thresholds", "", *[f"- {'pass' if ok else 'NOT MET'}: {name}" for name, ok in s["checks"].items()], ""]
    if s["blocking_issues"]:
        md += ["## Blocking issues", "", *[f"- {x}" for x in s["blocking_issues"]], ""]
    md += ["These thresholds help an editorial decision. They are not proof the book will sell."]
    bl.write_atomic(rdir(a.book, a.round) / "summary.md", "\n".join(md) + "\n")
    bl.write_json(rdir(a.book, a.round) / "summary.json", s)
    status = "passed" if s["passed"] else ("waived" if d.get("waiver") and not s["blocking_issues"] else "not passed")
    bl.set_stage(data, "readers", status, round=a.round, humans=h["responded"], simulated=sim["runs"])
    bl.save_book(a.book, data)
    return {"ok": True, **s, "stage": status, "summary": str(rdir(a.book, a.round) / "summary.md")}


def cmd_waive(a):
    bl.load_book(a.book)
    if a.by != "member" or not a.reason.strip():
        bl.refuse("only the member can go ahead without enough real readers, and the reason is recorded")
    d = load_round(a.book, a.round)
    d["waiver"] = {"by": "member", "reason": a.reason.strip(), "date": bl.today()}
    save_round(a.book, a.round, d)
    return {"ok": True, "waiver": d["waiver"], "note": "open P0 and P1 issues still block; run consolidate again"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--book", required=True)
        x.add_argument("--round", type=int, default=1)
        return x
    x = p("personas"); x.add_argument("--add", action="append")
    x = p("brief"); x.add_argument("--persona", required=True); x.add_argument("--edition", required=True)
    x = p("record-sim"); x.add_argument("--persona", required=True); x.add_argument("--report", required=True)
    for k in ("clarity", "relevance", "usefulness"):
        x.add_argument("--" + k, type=int, required=True)
    x = p("invite"); x.add_argument("--roles", required=True)
    x = p("questionnaire"); x.add_argument("--edition", required=True); x.add_argument("--days", type=int, default=14)
    x = p("record-human"); x.add_argument("--code", required=True); x.add_argument("--finished", required=True)
    x.add_argument("--stopped-at"); x.add_argument("--promise-explained", required=True); x.add_argument("--next-step", required=True)
    x.add_argument("--clarity", type=int, required=True); x.add_argument("--usefulness", type=int, required=True)
    x.add_argument("--recommend", required=True); x.add_argument("--notes")
    p("consolidate")
    x = p("waive"); x.add_argument("--by", required=True); x.add_argument("--reason", required=True)
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd.replace("-", "_")](a)
    bl.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
