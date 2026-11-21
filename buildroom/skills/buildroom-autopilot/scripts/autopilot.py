#!/usr/bin/env python3
"""Autopilot run keeper: the plan, the order, the review gate and the final report.

  autopilot.py preflight BUSINESS_FILE.md
  autopilot.py plan   --dir autopilot --readiness N|none [--thin-ok "the member's words"] [--skip SLUG ...] [--no-web]
  autopilot.py decide --dir autopilot --key KEY --value "the member's answer"
  autopilot.py next   --dir autopilot             the one step to run now, its scope and the standing rules
  autopilot.py done   --dir autopilot SLUG --status drafted|partial|blocked|skipped [--outputs F ...] [--gaps TEXT ...] [--note TEXT] [--redo]
  autopilot.py approve --dir autopilot --words "what the member said"
  autopilot.py leave-out --dir autopilot SLUG --words "what the member said"   drop a step whose input they lack
  autopilot.py status --dir autopilot
  autopilot.py report --dir autopilot             the review list, as markdown

It keeps one file, run.json, in the folder it is given. It runs no session itself, goes nowhere online,
and never publishes, sends or spends. Standard library only.
"""
import argparse, json, os, re, sys
from datetime import date
from pathlib import Path

# slug, name, the words that start it, mode, why
#   foundation  drafted first, then shown to the member for review
#   auto        drafted in the run, after the member approves the foundation
#   needs_you   left out on purpose, with the reason; listed as a next step
#   on_request  a tool the member reaches for when they need it; not part of a run
TOOLS = [
    ("audience-insight", "Audience Insight", "Find the words my clients actually use", "foundation", "public research; skipped when there is no web access"),
    ("ideal-client-avatar", "Ideal Client Avatar", "Help me build my ideal client avatar", "foundation", ""),
    ("signature-offer", "Signature Offer", "Help me build my signature offer", "foundation", ""),
    ("positioning-messaging", "Positioning & Messaging", "Help me position my business", "foundation", ""),
    ("offer-page-copy", "Offer Page Copy", "Write my offer page", "auto", ""),
    ("funnel-map", "Funnel Map", "Help me map my funnel", "auto", ""),
    ("lead-capture", "Lead Capture", "Help me build my opt-in page", "auto", ""),
    ("sales-script", "Sales Conversations", "Help me with my sales call", "auto", ""),
    ("decision-machine", "Decision Machine", "Build my follow-up system", "auto", ""),
    ("leadgen", "Lead Gen Machine", "Help me get more leads", "auto", ""),
    ("offer-deep-dive", "Offer Deep Dive", "Make my offer a no-brainer", "needs_you", "it is an interview where you do most of the talking, about value, guarantees and numbers that are yours to set"),
    ("linkedin", "LinkedIn Engine", "Build my LinkedIn engine", "needs_you", "it starts from your current profile, your own stories and what you want to be known for"),
    ("search-answer-engine", "Search & Answer Engine", "Get found on Google", "needs_you", "it starts from questions only you can answer about where and how you work, and a typical client result"),
    ("compass", "Compass", "Build my compass", "needs_you", "it is an interview about you that only you can answer"),
    ("proof-engine", "Proof Engine", "Capture this win", "needs_you", "it needs a real client win and that client's permission"),
    ("funnel-scorecard", "Funnel Scorecard", "Where is my funnel leaking?", "needs_you", "it needs your real numbers"),
    ("ops-dashboard", "Weekly Ops Dashboard", "What numbers should I be watching every week?", "needs_you", "it needs your real numbers"),
    ("ad-studio", "Ad Studio", "Make me ads", "needs_you", "it spends money on your accounts"),
    ("video-director", "Video Director", "Make me a video", "needs_you", "it uses your face and footage, and paid generation"),
    ("website-design-studio", "Website Design Studio", "Make my website look like me", "needs_you", "it starts from screenshots that you choose"),
    ("company-blueprint", "Company Blueprint", "Build my company blueprint", "needs_you", "it maps who does what in your business, which only you know"),
    ("sop-creator", "SOP Creator", "Help me document my processes", "needs_you", "it documents how you actually do the work"),
    ("hiring-kit", "Hiring Ad + Interview Kit", "Help me hire someone", "needs_you", "it starts from a hiring decision that is yours"),
    ("training-docs", "Team Training Doc Builder", "Help me train my new hire", "needs_you", "it needs your procedures and a hire to train"),
    ("webinar-builder", "Webinar Builder", "Build my webinar", "needs_you", "it needs your stories and a decision to run one"),
    ("event-launcher", "Event Launcher", "Plan my launch", "needs_you", "it needs a date and a decision to launch"),
    ("book-builder", "AI Momentum Labs Book Builder", "Write my book", "needs_you", "it is written from your own stories"),
    ("speaking-engine", "Speaking Engine", "Get me speaking gigs", "needs_you", "it needs your talk and where you are willing to speak"),
    ("boardroom", "C-Suite Boardroom", "Convene the board", "needs_you", "it needs a decision you bring"),
    ("os", "Build Room OS Navigator", "What should I work on next?", "on_request", ""),
    ("discovery-engine", "Discovery Engine", "Research my business first", "on_request", ""),
    ("autopilot", "Autopilot", "Run autopilot", "on_request", ""),
    ("copy-engine", "Copy Engine", "Write me ...", "on_request", ""),
    ("brainstorm", "Brainstorm Session", "Let's brainstorm", "on_request", ""),
    ("brainstorm-capture", "Brainstorm Capture", "Capture what we decided", "on_request", ""),
    ("triage", "Triage", "Triage my projects", "on_request", ""),
    ("finish-it", "Finish It", "Finish it", "on_request", ""),
    ("build-it", "Build It", "Build me an app", "on_request", ""),
    ("agent-forge", "Agent Forge", "Make me an agent", "on_request", ""),
    ("obsidian", "Second Brain", "Set up my second brain", "on_request", ""),
    ("source-watcher", "Source Watcher", "Build me a source watcher", "on_request", ""),
    ("continuity", "Continuity System", "Set up the continuity system for this project", "on_request", ""),
]
TOOL = {t[0]: t for t in TOOLS}

# What a run drafts in each session, and what it leaves for the member. Printed by `next`.
SCOPE = {
    "audience-insight": "Public research only: the words buyers use, each with its source. No interviews.",
    "ideal-client-avatar": "The avatar from what is known. Leave out anything that asks you to imagine clients: no invented complaints, no 'as if you interviewed 50', no testimonial fragments, no revenue or years figures, no imagined scenes (a typical Tuesday, thoughts at 11pm). Guessed phrases go under hypothesis language, never in quotation marks.",
    "signature-offer": "Document the offer as it stands: name, promise, how it runs, phases, deliverables, price, guarantee. Do not set dollar values per deliverable, price tiers, price anchors, cost-of-problem math or new guarantee options. Those are the member's, in Offer Deep Dive.",
    "positioning-messaging": "Positioning from the avatar and the offer. No claims about competitors you have not seen. Taglines and statements are drafts.",
    "offer-page-copy": "The full page as copy. No cost math, no value stack figures, no composite or 'typical' results. Proof only where permission is recorded as yes. Missing proof is a marked gap, not a made-up story.",
    "funnel-map": "The funnel map and the welcome email sequence. Do not write the opt-in page (Lead Capture does) and do not run any CRM build. If the member has no free resource, there is no opt-in and nobody to welcome: map how people reach them today and how a first call gets booked, write no email sequence, and record the step as partial. Follow-up after a call belongs to Decision Machine.",
    "lead-capture": "The opt-in page copy, the thank-you page and the delivery email. If the free resource does not exist, say so and outline what it would cover; do not write as if it exists. No CRM build, no web application.",
    "sales-script": "The call script and objection answers, using the guarantee wording exactly. No role-play.",
    "decision-machine": "The follow-up after a call and for a no-show only. The welcome sequence belongs to Funnel Map; do not write a second one. No tags built, no CRM build.",
    "leadgen": "One module only: the one that matches where the member most wants clients from. Record this step as partial and name the module.",
}
STATUSES = ("drafted", "partial", "blocked", "skipped")
DONE_OK = ("drafted", "partial")
# The three a run cannot go on without. Audience Insight is helpful, not required.
MUST = ("ideal-client-avatar", "signature-offer", "positioning-messaging")
SNAPSHOT = ("What I do", "Who I serve", "Core result I deliver")
READY_AT = 70
DRAFTS = "autopilot/drafts/"
# key: (what it is, whether every later session must be told)
# What a step leans on. When the member has said there is none, or was never asked, the step would come back
# mostly blank, so the member is offered the choice to leave it out before the straight run starts.
LEANS_ON = {
    "lead-capture": ("free_resource", "a free resource to offer"),
    "decision-machine": ("tools", "the tools you use for email and follow-up"),
    "leadgen": ("preferred_source", "where you most want new clients to come from"),
}
NONE = re.compile(r"\s*((none|no|nothing|n/?a|not yet)( yet| really)?[\s.!]*$|i don'?t (know|have)\b|don'?t (know|have)\b|skip\b)", re.I)
# Decisions that add up instead of replacing: a second answer never erases the first.
ADDS = ("never_claim", "retired")
DECISIONS = {
    "price": ("Price today", False),
    "guarantee": ("Guarantee, exact wording, or none", True),
    "typical_result": ("A typical client result", False),
    "never_claim": ("Never claim or promise", True),
    "retired": ("Lines never to use", True),
    "booking": ("How someone books or buys", False),
    "tools": ("Email, CRM, website and booking tools", False),
    "free_resource": ("Free resource to offer, or none yet", False),
    "goal_90": ("The one result wanted in the next 90 days", False),
    "preferred_source": ("Where they most want clients from", False),
    "deliverables": ("What a client receives", False),
    "credentials": ("Background and credentials", False),
}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def run_path(d):
    return Path(d) / "run.json"


def load(d):
    p = run_path(d)
    if not p.is_file():
        die(f"No run found in {d}. Start one with: autopilot.py plan --dir {d} --readiness <number or none>")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        die(f"run.json cannot be read ({e}). Do not start over; fix or restore the file.")


def save(d, run):
    p = run_path(d)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.part")
    tmp.write_text(json.dumps(run, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def sections(text):
    """{number: (title, status)} from a Business File."""
    out = {}
    for m in re.finditer(r"^## (\d+)\. (.+?)\s*$\n+(?:\*\*Status:\*\*\s*([a-z ]+?)\s*·)?", text, re.M):
        out[int(m.group(1))] = (m.group(2), (m.group(3) or "").strip())
    return out


def field(text, label):
    m = re.search(r"^- \*\*" + re.escape(label) + r"[^*]*:\*\*[ \t]*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return "" if v in ("", "—", "-") or re.fullmatch(r"\[.*\]", v) else v


def cmd_preflight(a):
    p = Path(a.file)
    if not p.is_file():
        die(f"No Business File at {p}. Say \"I'm new here. Help me get started.\" first.", 2)
    text = p.read_text(encoding="utf-8")
    secs = sections(text)
    missing = [l for l in SNAPSHOT if not field(text, l)]
    print("Business File sections that matter to a run:")
    for n in (1, 2, 3, 4):
        t, st = secs.get(n, ("missing", "missing"))
        print(f"  §{n} {t}: {st or 'not started'}")
    if missing:
        print("\nNot ready. The Business Snapshot is missing: " + ", ".join(missing) + ".")
        print('Run "Research my business first" (Deep Discovery), or answer the onboarding questions, then come back.')
        sys.exit(2)
    print("\nThe Business Snapshot is filled in, so a run can be planned.")
    print("This check does not say how much is known. If discovery/ledger.json exists, run the Discovery Engine's")
    print("`discover.py ready` on it and give its number to `plan --readiness`. If there is no ledger, say so: `--readiness none`.")
    thin = [n for n in (2, 3, 4) if secs.get(n, ("", ""))[1] in ("", "not started")]
    if thin:
        print(f"§{', §'.join(map(str, thin))} will be drafted from scratch.")
    else:
        print("§2 to §4 hold some content. A run keeps what is there and fills gaps, unless the member says to redo them.")


def cmd_plan(a):
    if run_path(a.dir).is_file():
        die(f"A run already exists in {a.dir}. Use 'next' to carry on, or move that folder aside to start a new one.")
    bad = [s for s in a.skip if s not in TOOL or TOOL[s][3] not in ("foundation", "auto")]
    if bad:
        die("Cannot skip (not part of a run): " + ", ".join(bad))
    if set(a.skip) & set(MUST):
        die("The ideal client, the offer and the positioning cannot be skipped. Everything after is built on them.")
    r = str(a.readiness).strip().lower()
    if r != "none" and not (r.isdigit() and 0 <= int(r) <= 100):
        die("--readiness is the number from the Discovery Engine's `discover.py ready` (0 to 100), or 'none' when there is no discovery ledger.")
    thin_ok = (a.thin_ok or "").strip()
    if (r == "none" or int(r) < READY_AT) and len(thin_ok) < 2:
        why = "There is no discovery ledger, so nobody knows how much is known." if r == "none" else f"Readiness is {r} out of 100, below {READY_AT}."
        die(why + " A run now would be mostly blanks and guesses. Tell the member, and offer: answer the questions Discovery still has "
            "(only if `discover.py ready` names some), run the one session it names by hand, or go ahead anyway. If they choose to go ahead, "
            "record their words with --thin-ok. Words that are not a clear choice to go ahead (\"I don't know\", \"skip that\") are not one.", 5)
    if thin_ok and NONE.match(thin_ok):
        die(f"“{thin_ok}” is not a choice to go ahead. Do not start a run on it.", 5)
    steps = []
    for slug, _n, _p, mode, _w in TOOLS:
        if mode not in ("foundation", "auto"):
            continue
        st = {"slug": slug, "stage": mode, "status": "pending"}
        if slug in a.skip:
            st.update(status="skipped", note="left out at the member's request")
        elif slug == "audience-insight" and a.no_web:
            st.update(status="skipped", note="no web access in this session")
        steps.append(st)
    run = {"started": date.today().isoformat(), "readiness": r, "thin_ok": thin_ok or None, "approved": None, "decisions": [], "steps": steps}
    save(a.dir, run)
    print(f"Plan saved to {run_path(a.dir)}.\n")
    show(run)


def show(run):
    r = run.get("readiness")
    print("Readiness: " + ("no discovery was run" if r == "none" else f"{r} out of 100")
          + (f" (the member chose to go ahead: “{run['thin_ok']}”)" if run.get("thin_ok") else ""))
    for stage, title in (("foundation", "First, the foundation (then you review it)"), ("auto", "Then, straight through")):
        print(title + ":")
        for s in run["steps"]:
            if s["stage"] == stage:
                print(f"  [{s['status']:>7}] {TOOL[s['slug']][1]}" + (f"  ({s['note']})" if s.get("note") else ""))
    print("Review: " + (f"approved {run['approved']['date']}" if run.get("approved") else "not yet"))


def pending(run, stage):
    return [s for s in run["steps"] if s["stage"] == stage and s["status"] == "pending"]


def standing(run):
    """What every session in the run must be told. These are the member's rules, in their words."""
    out = []
    for dct in run.get("decisions", []):
        if DECISIONS[dct["key"]][1] and not (dct["key"] in ADDS and NONE.match(dct["value"])):
            out.append(f"{DECISIONS[dct['key']][0]}: {dct['value']}")
    return out


def known(run):
    """Everything else the member said at the start, so each session works from it instead of leaving a blank."""
    return [f"{DECISIONS[x['key']][0]}: {x['value']}" for x in run.get("decisions", []) if not DECISIONS[x["key"]][1]]


def said(words):
    """The member's words in quotation marks, closed with one full stop however they ended."""
    w = str(words).strip()
    return f"“{w}”" + ("" if w[-1:] in ".!?" else ".")


def thin_steps(run):
    """Pending steps whose main input the member does not have yet."""
    dec = {x["key"]: x["value"] for x in run.get("decisions", [])}
    out = []
    for s in pending(run, "auto"):
        need = LEANS_ON.get(s["slug"])
        if need and (need[0] not in dec or NONE.match(dec[need[0]])):
            out.append((s["slug"], need[1]))
    return out


def cmd_decide(a):
    run = load(a.dir)
    if a.key not in DECISIONS:
        die("Unknown key. Use one of: " + ", ".join(DECISIONS))
    val = (a.value or "").strip()
    if not val:
        die("Record what the member actually said (--value). If they skipped the question, record nothing.")
    run.setdefault("decisions", [])
    before = [x["value"] for x in run["decisions"] if x["key"] == a.key]
    if a.key in ADDS and before and not NONE.match(before[0]) and before[0].lower() not in val.lower():
        val = before[0] if val.lower() in before[0].lower() else before[0].rstrip("; ") + "; " + val
    run["decisions"] = [x for x in run["decisions"] if x["key"] != a.key] + [{"key": a.key, "value": val, "date": date.today().isoformat()}]
    save(a.dir, run)
    print(f"Recorded: {DECISIONS[a.key][0]}." + (f" Now: {val}" if a.key in ADDS else ""))


def cmd_next(a):
    run = load(a.dir)

    def announce(s, stage):
        print(f"NEXT  {TOOL[s['slug']][1]}  (buildroom-{s['slug']})  stage: {stage}")
        print("SCOPE  " + SCOPE[s["slug"]])
        print(f"SAVE  every document under {DRAFTS}")
        for line in standing(run):
            print("RULE  " + line)
        for line in known(run):
            print("KNOWN  " + line)

    f = pending(run, "foundation")
    if f:
        return announce(f[0], "foundation")
    stuck = [s["slug"] for s in run["steps"] if s["slug"] in MUST and s["status"] not in DONE_OK]
    if stuck:
        print("STOP  The foundation is not complete: " + ", ".join(TOOL[s][1] for s in stuck)
              + ". Tell the member what is missing and ask for it. Do not go on without it.")
        sys.exit(4)
    if not run.get("approved"):
        part = [TOOL[s["slug"]][1] for s in run["steps"] if s["slug"] in MUST and s["status"] == "partial"]
        if len(part) >= 2:
            print(f"NOTE  {len(part)} of the 3 foundation sessions are only partly drafted ({', '.join(part)}). Say so when you show the page, "
                  "and offer the member the choice to stop here and run the Ideal Client Avatar session by hand instead of going on.")
        print("REVIEW  The foundation is drafted. Build the Foundation Reveal, show it to the member, apply their changes, "
              "and record their go-ahead with 'approve'. Nothing else runs until then.")
        sys.exit(3)
    r = pending(run, "auto")
    if r:
        return announce(r[0], "run")
    print("DONE  Every step is finished. Run 'report', build the Your Build page, and give both to the member.")


def cmd_done(a):
    run = load(a.dir)
    todo = pending(run, "foundation") or (pending(run, "auto") if run.get("approved") else [])
    if a.redo:
        # A step drafted again, for example after the member's review changed it. Its record is replaced.
        todo = [s for s in run["steps"] if s["slug"] == a.slug and s["status"] in DONE_OK + ("blocked",)]
        if not todo:
            die(f"--redo replaces the record of a step already finished. {a.slug} has not been finished.")
    if not todo:
        die("Nothing is waiting. If the foundation is drafted, the member has to review it first.")
    if todo[0]["slug"] != a.slug:
        die(f"Out of order. The step to finish now is {todo[0]['slug']}, not {a.slug}.")
    outs = [str(o).replace("\\", "/") for o in (a.outputs or [])]
    if a.status in DONE_OK and not outs:
        die(f"A {a.status} step must name what it produced (--outputs).")
    wrong = [o for o in outs if not o.startswith(DRAFTS) or ".." in o.split("/")]
    if wrong:
        die(f"A run saves every document under {DRAFTS} so drafts are never mistaken for the member's own files. Move: " + ", ".join(wrong))
    if a.status in ("partial", "blocked", "skipped") and not (a.note or "").strip():
        die(f"A {a.status} step must say why (--note)." + (" For partial: what was drafted and what was not." if a.status == "partial" else ""))
    if a.status == "skipped" and a.slug in MUST:
        die("The ideal client, the offer and the positioning cannot be skipped.")
    s = todo[0]
    s.update(status=a.status, outputs=outs, gaps=a.gaps or [], note=(a.note or "").strip(), finished=date.today().isoformat())
    save(a.dir, run)
    print(f"Recorded: {TOOL[a.slug][1]} is {a.status}.")


def cmd_approve(a):
    run = load(a.dir)
    if pending(run, "foundation") or any(s["slug"] in MUST and s["status"] not in DONE_OK for s in run["steps"]):
        die("The foundation is not fully drafted yet, so there is nothing to approve.")
    words = (a.words or "").strip()
    if len(words) < 2:
        die("Record what the member actually said (--words). Their go-ahead is theirs to give.")
    run["approved"] = {"date": date.today().isoformat(), "words": words}
    save(a.dir, run)
    print("Recorded the member's go-ahead. The run can continue.")
    thin = thin_steps(run)
    if thin:
        print("\nASK ONCE, before going on. These steps lean on something the member does not have yet and would come back mostly blank:")
        for slug, need in thin:
            print(f"  - {TOOL[slug][1]}: needs {need}")
        print("Ask the member whether to run them anyway or leave them out. To leave one out: "
              f"autopilot.py leave-out --dir {a.dir} SLUG --words \"what they said\". This is the last question of the run.")


def cmd_leave_out(a):
    run = load(a.dir)
    s = next((s for s in pending(run, "auto") if s["slug"] == a.slug), None)
    if not s:
        die(f"{a.slug} is not a step still waiting in the straight run. The ideal client, the offer and the positioning cannot be left out.")
    words = (a.words or "").strip()
    if len(words) < 2:
        die("Record what the member actually said (--words). Leaving a step out is their choice.")
    need = LEANS_ON.get(a.slug)
    s.update(status="skipped", note=f"left out at your request ({said(words).rstrip('.')})" + (f": it needs {need[1]}" if need else ""), finished=date.today().isoformat())
    save(a.dir, run)
    print(f"Recorded: {TOOL[a.slug][1]} is left out of this run. It is listed in the report with the sentence that starts it.")


def cmd_status(a):
    show(load(a.dir))


def rollup(run):
    """Gaps that come up in more than one draft, most repeated first: the few answers that unlock the most."""
    seen = {}
    for s in run["steps"]:
        for g in s.get("gaps") or []:
            k = re.sub(r"[^a-z0-9 ]", "", str(g).lower()).strip()
            if k:
                e = seen.setdefault(k, {"text": str(g), "in": []})
                if TOOL[s["slug"]][1] not in e["in"]:
                    e["in"].append(TOOL[s["slug"]][1])
    # Most repeated first. Ties keep the order they came up in, so a gap in the foundation leads.
    return sorted(seen.values(), key=lambda e: -len(e["in"]))


def cmd_report(a):
    run = load(a.dir)
    by = {st: [s for s in run["steps"] if s["status"] == st] for st in ("drafted", "partial", "blocked", "skipped", "pending")}
    r = run.get("readiness")
    out = ["# Your Autopilot run", "", f"Started {run['started']}. "
           + ("No discovery was run first." if r == "none" else f"Readiness when it started: {r} out of 100.")
           + (f" You chose to go ahead: {said(run['thin_ok'])}" if run.get("thin_ok") else ""),
           (f"You approved the foundation on {run['approved']['date']}: {said(run['approved']['words'])}" if run.get("approved") else "The foundation has not been approved yet."), "",
           "Everything below is a draft for you to review. Nothing was published, sent or paid for.", ""]
    top = rollup(run)
    if top:
        out += ["## What to do first", "", "These are asked for most across your drafts. Answering them improves several at once.", ""]
        out += [f"{i}. {e['text']}" + (f" (needed by {', '.join(e['in'])})" if len(e["in"]) > 1 else f" (needed by {e['in'][0]})") for i, e in enumerate(top[:5], 1)]
        out += ["", "Then read each draft, fix anything that does not sound like you, and publish only what you have checked.", ""]
    else:
        out += ["## What to do first", "", "1. Read the drafts and fix anything that does not sound like you.", "2. Publish only what you have checked.", ""]
    if run.get("decisions"):
        out += ["## What you told me", ""] + [f"- **{DECISIONS[x['key']][0]}:** {x['value']}" for x in run["decisions"]] + [""]
    for st, title in (("drafted", "Drafted for you"), ("partial", "Partly drafted")):
        if by[st]:
            out += [f"## {title}", ""]
            for s in by[st]:
                out.append(f"### {TOOL[s['slug']][1]}")
                out += [f"- Saved as: {o}" for o in s.get("outputs", [])]
                out += [f"- Still needs you: {g}" for g in s.get("gaps", [])]
                if s.get("note"):
                    out.append(f"- {'What was and was not drafted' if st == 'partial' else 'Note'}: {s['note']}")
                out.append("")
    if by["blocked"]:
        out += ["## Could not be drafted", ""] + [f"- **{TOOL[s['slug']][1]}:** {s['note']} To run it yourself, say “{TOOL[s['slug']][2]}”." for s in by["blocked"]] + [""]
    if by["skipped"]:
        out += ["## Left out", ""] + [f"- **{TOOL[s['slug']][1]}:** {s.get('note', '')}. To run it yourself later, say “{TOOL[s['slug']][2]}”." for s in by["skipped"]] + [""]
    if by["pending"]:
        out += ["## Not reached yet", ""] + [f"- {TOOL[s['slug']][1]}" for s in by["pending"]] + ["", "Say “Run autopilot” to carry on from here.", ""]
    out += ["## Needs you, so it was not run", "", "These depend on something only you have. Each one is a session you start with one sentence. Not all of them will fit your business; pick what does.", ""]
    out += [f"- **{n}:** {why}. Say “{phrase}”." for _s, n, phrase, mode, why in TOOLS if mode == "needs_you"]
    print("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight"); p.add_argument("file"); p.set_defaults(fn=cmd_preflight)
    p = sub.add_parser("plan"); p.add_argument("--dir", required=True); p.add_argument("--readiness", required=True)
    p.add_argument("--thin-ok"); p.add_argument("--skip", nargs="*", default=[]); p.add_argument("--no-web", action="store_true"); p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("decide"); p.add_argument("--dir", required=True); p.add_argument("--key", required=True); p.add_argument("--value"); p.set_defaults(fn=cmd_decide)
    for name, fn in (("next", cmd_next), ("status", cmd_status), ("report", cmd_report)):
        p = sub.add_parser(name); p.add_argument("--dir", required=True); p.set_defaults(fn=fn)
    p = sub.add_parser("done"); p.add_argument("--dir", required=True); p.add_argument("slug"); p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--outputs", nargs="*"); p.add_argument("--gaps", nargs="*"); p.add_argument("--note"); p.add_argument("--redo", action="store_true"); p.set_defaults(fn=cmd_done)
    p = sub.add_parser("leave-out"); p.add_argument("--dir", required=True); p.add_argument("slug"); p.add_argument("--words"); p.set_defaults(fn=cmd_leave_out)
    p = sub.add_parser("approve"); p.add_argument("--dir", required=True); p.add_argument("--words"); p.set_defaults(fn=cmd_approve)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
