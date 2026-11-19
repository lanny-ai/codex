#!/usr/bin/env python3
"""Autopilot run keeper: the plan, the order, the review gate and the final report.

  autopilot.py preflight BUSINESS_FILE.md        is there enough in the file to start?
  autopilot.py plan   --dir autopilot [--skip SLUG ...] [--no-web]
  autopilot.py next   --dir autopilot             the one step to run now
  autopilot.py done   --dir autopilot SLUG --status drafted|blocked|skipped [--outputs F ...] [--gaps TEXT ...] [--note TEXT]
  autopilot.py approve --dir autopilot --words "what the member said"
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
    ("offer-deep-dive", "Offer Deep Dive", "Make my offer a no-brainer", "auto", ""),
    ("offer-page-copy", "Offer Page Copy", "Write my offer page", "auto", ""),
    ("funnel-map", "Funnel Map", "Help me map my funnel", "auto", ""),
    ("lead-capture", "Lead Capture", "Help me build my opt-in page", "auto", ""),
    ("sales-script", "Sales Conversations", "Help me with my sales call", "auto", ""),
    ("decision-machine", "Decision Machine", "Build my follow-up system", "auto", ""),
    ("leadgen", "Lead Gen Machine", "Help me get more leads", "auto", ""),
    ("linkedin", "LinkedIn Engine", "Build my LinkedIn engine", "auto", ""),
    ("search-answer-engine", "Search & Answer Engine", "Get found on Google", "auto", ""),
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
STATUSES = ("drafted", "blocked", "skipped")
# The three a run cannot go on without. Audience Insight is helpful, not required.
MUST = ("ideal-client-avatar", "signature-offer", "positioning-messaging")
SNAPSHOT = ("What I do", "Who I serve", "Core result I deliver")


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def run_path(d):
    return Path(d) / "run.json"


def load(d):
    p = run_path(d)
    if not p.is_file():
        die(f"No run found in {d}. Start one with: autopilot.py plan --dir {d}")
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
    thin = [n for n in (2, 3, 4) if secs.get(n, ("", ""))[1] in ("", "not started")]
    print("\nReady to start." + (f" §{', §'.join(map(str, thin))} will be drafted from scratch, so expect more lines marked as drafted." if thin else ""))
    if not thin:
        print("§2 to §4 already have content. Autopilot will keep what is there and only fill gaps, unless the member says to redo them.")


def cmd_plan(a):
    if run_path(a.dir).is_file():
        die(f"A run already exists in {a.dir}. Use 'next' to carry on, or move that folder aside to start a new one.")
    bad = [s for s in a.skip if s not in TOOL or TOOL[s][3] not in ("foundation", "auto")]
    if bad:
        die("Cannot skip (not part of a run): " + ", ".join(bad))
    if set(a.skip) & set(MUST):
        die("The ideal client, the offer and the positioning cannot be skipped. Everything after is built on them.")
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
    run = {"started": date.today().isoformat(), "approved": None, "steps": steps}
    save(a.dir, run)
    print(f"Plan saved to {run_path(a.dir)}.\n")
    show(run)


def show(run):
    for stage, title in (("foundation", "First, the foundation (then you review it)"), ("auto", "Then, straight through")):
        print(title + ":")
        for s in run["steps"]:
            if s["stage"] == stage:
                print(f"  [{s['status']:>7}] {TOOL[s['slug']][1]}" + (f"  ({s['note']})" if s.get("note") else ""))
    print("Review: " + (f"approved {run['approved']['date']}" if run.get("approved") else "not yet"))


def pending(run, stage):
    return [s for s in run["steps"] if s["stage"] == stage and s["status"] == "pending"]


def cmd_next(a):
    run = load(a.dir)
    f = pending(run, "foundation")
    if f:
        s = f[0]
        print(f"NEXT  {TOOL[s['slug']][1]}  (buildroom-{s['slug']})  stage: foundation")
        return
    stuck = [s["slug"] for s in run["steps"] if s["slug"] in MUST and s["status"] != "drafted"]
    if stuck:
        print("STOP  The foundation is not complete: " + ", ".join(TOOL[s][1] for s in stuck)
              + ". Tell the member what is missing and ask for it. Do not go on without it.")
        sys.exit(4)
    if not run.get("approved"):
        print("REVIEW  The foundation is drafted. Build the Foundation Reveal, show it to the member, apply their changes, "
              "and record their go-ahead with 'approve'. Nothing else runs until then.")
        sys.exit(3)
    r = pending(run, "auto")
    if r:
        s = r[0]
        print(f"NEXT  {TOOL[s['slug']][1]}  (buildroom-{s['slug']})  stage: run")
        return
    print("DONE  Every step is finished. Run 'report' and give the member the review list.")


def cmd_done(a):
    run = load(a.dir)
    todo = pending(run, "foundation") or (pending(run, "auto") if run.get("approved") else [])
    if not todo:
        die("Nothing is waiting. If the foundation is drafted, the member has to review it first.")
    if todo[0]["slug"] != a.slug:
        die(f"Out of order. The step to finish now is {todo[0]['slug']}, not {a.slug}.")
    if a.status == "drafted" and not a.outputs:
        die("A drafted step must name what it produced (--outputs).")
    if a.status in ("blocked", "skipped") and not (a.note or "").strip():
        die(f"A {a.status} step must say why (--note).")
    if a.status == "skipped" and a.slug in MUST:
        die("The ideal client, the offer and the positioning cannot be skipped.")
    s = todo[0]
    s.update(status=a.status, outputs=a.outputs or [], gaps=a.gaps or [], note=(a.note or "").strip(), finished=date.today().isoformat())
    save(a.dir, run)
    print(f"Recorded: {TOOL[a.slug][1]} is {a.status}.")


def cmd_approve(a):
    run = load(a.dir)
    if pending(run, "foundation") or any(s["slug"] in MUST and s["status"] != "drafted" for s in run["steps"]):
        die("The foundation is not fully drafted yet, so there is nothing to approve.")
    words = (a.words or "").strip()
    if len(words) < 2:
        die("Record what the member actually said (--words). Their go-ahead is theirs to give.")
    run["approved"] = {"date": date.today().isoformat(), "words": words}
    save(a.dir, run)
    print("Recorded the member's go-ahead. The run can continue.")


def cmd_status(a):
    show(load(a.dir))


def cmd_report(a):
    run = load(a.dir)
    by = {st: [s for s in run["steps"] if s["status"] == st] for st in ("drafted", "blocked", "skipped", "pending")}
    out = ["# Your Autopilot run", "", f"Started {run['started']}."
           + (f" You approved the foundation on {run['approved']['date']}." if run.get("approved") else " The foundation has not been approved yet."), "",
           "Everything below is a draft for you to review. Nothing was published, sent or paid for.", ""]
    if by["drafted"]:
        out += ["## Drafted for you", ""]
        for s in by["drafted"]:
            out.append(f"### {TOOL[s['slug']][1]}")
            out += [f"- Saved as: {o}" for o in s.get("outputs", [])]
            out += [f"- Still needs you: {g}" for g in s.get("gaps", [])]
            if s.get("note"):
                out.append(f"- Note: {s['note']}")
            out.append("")
    if by["blocked"]:
        out += ["## Could not be drafted", ""] + [f"- **{TOOL[s['slug']][1]}:** {s['note']} To run it yourself, say “{TOOL[s['slug']][2]}”." for s in by["blocked"]] + [""]
    if by["skipped"]:
        out += ["## Left out", ""] + [f"- **{TOOL[s['slug']][1]}:** {s.get('note', '')}" for s in by["skipped"]] + [""]
    if by["pending"]:
        out += ["## Not reached yet", ""] + [f"- {TOOL[s['slug']][1]}" for s in by["pending"]] + ["", "Say “Run autopilot” to carry on from here.", ""]
    out += ["## Needs you, so it was not run", "", "These depend on something only you have. Each one is a session you start with one sentence.", ""]
    out += [f"- **{n}:** {why}. Say “{phrase}”." for _s, n, phrase, mode, why in TOOLS if mode == "needs_you"]
    out += ["", "## What to do first", "", "1. Read the drafts and fix anything that does not sound like you.",
            "2. Fill the lines marked as still needing you.", "3. Publish only what you have checked."]
    print("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight"); p.add_argument("file"); p.set_defaults(fn=cmd_preflight)
    p = sub.add_parser("plan"); p.add_argument("--dir", required=True); p.add_argument("--skip", nargs="*", default=[])
    p.add_argument("--no-web", action="store_true"); p.set_defaults(fn=cmd_plan)
    for name, fn in (("next", cmd_next), ("status", cmd_status), ("report", cmd_report)):
        p = sub.add_parser(name); p.add_argument("--dir", required=True); p.set_defaults(fn=fn)
    p = sub.add_parser("done"); p.add_argument("--dir", required=True); p.add_argument("slug"); p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--outputs", nargs="*"); p.add_argument("--gaps", nargs="*"); p.add_argument("--note"); p.set_defaults(fn=cmd_done)
    p = sub.add_parser("approve"); p.add_argument("--dir", required=True); p.add_argument("--words"); p.set_defaults(fn=cmd_approve)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
