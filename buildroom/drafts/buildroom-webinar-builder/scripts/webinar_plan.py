#!/usr/bin/env python3
"""Webinar Builder plan: the timed outline, the rendered script, notes, moderator sheet and Q&A bank, the
Event Launcher run-sheet day, and the "what's on offer" one-pager.

Local only. It reads and writes the member's own files; it never touches Zoom, the checkout or the CRM.

Usage
  webinar_plan.py formats
      Lists the formats and their minute maps.
  webinar_plan.py outline --format live60|broadcast3|interview|paidclass|bootcamp [--day 1|2|3]
                          --title "…" [--presenter "…"] --date YYYY-MM-DD --start HH:MM --tz Area/City
                          [--close checkout|call|both] [--length MIN] (--launch launches/<slug> | --out FILE) [--force]
      Writes webinar.json with the minute map and every block marked [write: …]. --launch writes
      <launch>/webinar/webinar.json (a bootcamp day: <launch>/webinar/day-N/webinar.json), creating the folders.
      Refuses to overwrite an existing file without --force. --length scales the teaching blocks (paidclass,
      bootcamp); live60, broadcast3 and interview are 60 minutes.
  webinar_plan.py render --spec webinar.json [--out-dir DIR] [--runsheet runsheet.json]
      Writes script.md, speaker-notes.md, moderator-sheet.md and qa-bank.md next to the spec (or in --out-dir).
      --runsheet writes the webinar as a day in the Event Launcher's runsheet.json (created if missing; the
      day with the same date is replaced), with the lobby, the recording notice, a checkout test 30 minutes
      before the start and the roles and links merged in, so run_sheet.py build checks it with the launch.
      Prints a JSON summary. Exit 0, or 2 when the spec is refused (unreadable, an unknown kind, a bad time).
  webinar_plan.py offer-summary --close close.md --out offer-summary.md [--title "…"]
      The "what's on offer" one-pager, copied from close.md word for word: backup links and notes marked
      "moderator only" are left out. Refuses (exit 1) while close.md still has a PENDING element.

Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import argparse, json, re  # noqa: E402
from datetime import date, datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

KINDS = ("lobby", "agreement", "promise", "story", "teach", "guest", "build", "proof", "break", "transition",
         "offer", "qa", "close", "recap")
# Event Launcher run_sheet.py kinds: lobby welcome teach build proof break qa pitch close recap
RUNSHEET_KIND = {"lobby": "lobby", "agreement": "welcome", "promise": "welcome", "story": "teach", "teach": "teach",
                 "guest": "proof", "build": "build", "proof": "proof", "break": "break", "transition": "pitch",
                 "offer": "pitch", "qa": "qa", "close": "close", "recap": "recap"}
W = "[write: {}]"


def seg(i, kind, title, m, **kw):
    s = {"id": i, "kind": kind, "title": title, "min": m, "say": [W.format("three to six short prompts")],
         "chat_prompt": W.format("one easy chat prompt") if kind not in ("lobby", "break") else "",
         "slides": [], "notes": ""}
    s.update(kw)
    return s


def teach(i, n, m, title="Teaching block {}"):
    return seg(i, "teach", title.format(n), m, belief=n,
               loop={"question": W.format(f"the question block {n} answers"),
                     "answer": W.format("the answer, in one sentence")},
               proof=[])


def lobby():
    return seg("lobby", "lobby", "Lobby: welcome slide, music, the moderator greets people", 5,
               say=["Welcome people by name as they arrive"], chat_prompt="Type where you're joining from")


def agreement(m=3):
    return seg("agreement", "agreement", "The agreement frame, recording notice and captions", m,
               notes="Recording notice: this session is recorded. Captions are on: click CC at the bottom of Zoom.")


def promise(m=4):
    return seg("promise", "promise", "The promise, the agenda, what we are not covering, and the offer at the end", m)


def offer_seg(m, close):
    title = ("The invitation to book a call" if close == "call" else
             "The offer" if close == "checkout" else "The offer and the call option")
    return seg("offer", "offer", title, m, asks=3, links=["checkout" if close != "call" else "booking"])


def qa(m):
    return seg("qa", "qa", "Q&A as objection handling", m)


def close_seg(m=2):
    return seg("close", "close", "The takeaway close and the hard stop", m)


def fmt_live60(close, length, day):
    return 60, [lobby(), agreement(3), promise(4), seg("story", "story", "The story, ending on the big idea", 5),
                teach("teach1", 1, 8), teach("teach2", 2, 8), teach("teach3", 3, 8),
                seg("transition", "transition", "The transition and the trial close", 4),
                offer_seg(10, close), qa(8), close_seg(2)]


def fmt_broadcast3(close, length, day):
    return 60, [lobby(), agreement(3), promise(5), seg("story", "story", "The story, resolved quickly", 6),
                teach("teach1", 1, 8, "Lesson {}"), teach("teach2", 2, 8, "Lesson {}"),
                teach("teach3", 3, 8, "Lesson {}"), offer_seg(12, close), qa(8), close_seg(2)]


def fmt_interview(close, length, day):
    return 60, [lobby(), agreement(3), promise(4), seg("guest", "guest", "Introducing the guest (consented, proof ID)", 3,
                                                        proof=[]),
                teach("teach1", 1, 8, "Interview part {}: before"), teach("teach2", 2, 8, "Interview part {}: the turning point"),
                teach("teach3", 3, 8, "Interview part {}: after, and the method"),
                seg("transition", "transition", "The transition (the member, not the guest)", 4),
                offer_seg(10, close), qa(10), close_seg(2)]


def fmt_paidclass(close, length, day):
    L = length or 90
    t = max(8, (L - 45) // 3)
    rest = L - (3 + 5 + 5 + 3 * t + 12 + 4 + 2)
    off = max(6, rest - max(4, rest // 2))
    q = max(4, rest - off)
    return L, [lobby(), agreement(3), promise(5), seg("story", "story", "The story", 5),
               teach("teach1", 1, t), teach("teach2", 2, t), teach("teach3", 3, t),
               seg("build", "build", "Hands-on: everyone builds the first step", 12),
               seg("transition", "transition", "The transition", 4), offer_seg(off, close), qa(q), close_seg(2)]


def fmt_bootcamp(close, length, day):
    d = day or 1
    L = length or 150
    if d == 1:
        segs = [lobby(), agreement(5), promise(5), seg("build", "build", "First build: everyone uses the first-win tool", 15),
                seg("story", "story", "The story", 10), teach("teach1", 1, 25), seg("break", "break", "Break", 10),
                teach("teach2", 2, 25), teach("teach3", 3, 25), seg("recap", "recap", "Recap and tomorrow's cliffhanger", 10)]
    elif d == 2:
        segs = [lobby(), agreement(5), promise(5), seg("recap", "recap", "Paying off yesterday's cliffhanger", 10),
                teach("teach1", 1, 25), seg("proof", "proof", "Proof: a past success tells their own story (consented)", 15, proof=[]),
                seg("break", "break", "Break", 10), teach("teach2", 2, 25), teach("teach3", 3, 25),
                seg("recap2", "recap", "Recap and tomorrow's promise", 10)]
    else:
        segs = [lobby(), agreement(5), promise(5), seg("build", "build", "Finishing the build promised yesterday", 20),
                teach("teach1", 1, 15), teach("teach2", 2, 15), seg("break", "break", "Break", 10), teach("teach3", 3, 15),
                seg("transition", "transition", "The transition", 5), offer_seg(20, close), qa(15), close_seg(5)]
    used = sum(s["min"] for s in segs if s["kind"] != "lobby")
    if used < L:
        if d == 3:
            next(s for s in segs if s["kind"] == "qa")["min"] += L - used
        else:
            segs.insert(len(segs) - 1, qa(L - used))
    return L, segs


FORMATS = {
    "live60": ("A live 60-minute webinar (the default)", fmt_live60),
    "broadcast3": ("A three-lesson broadcast, offer at minute 38", fmt_broadcast3),
    "interview": ("An interview webinar with a consented guest", fmt_interview),
    "paidclass": ("A paid web class, 90 minutes by default (--length)", fmt_paidclass),
    "bootcamp": ("One bootcamp day (--day 1|2|3), 150 minutes by default (--length)", fmt_bootcamp),
}


def refuse(msg, code=2):
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(code)


def hhmm(s, what="start"):
    m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", str(s or ""))
    if not m:
        refuse(f"{what} must be HH:MM (24-hour), got {s!r}")
    return int(m.group(1)), int(m.group(2))


def cmd_formats(a):
    out = {}
    for k, (desc, fn) in FORMATS.items():
        L, segs = fn("checkout", None, 1)
        out[k] = {"what": desc, "length_min": L, "blocks": [f"{s['id']} {s['min']}m" for s in segs]}
    print(json.dumps(out, indent=2))


def cmd_outline(a):
    if a.format not in FORMATS:
        refuse(f"--format must be one of {sorted(FORMATS)}")
    try:
        date.fromisoformat(a.date)
    except Exception:
        refuse(f"--date must be YYYY-MM-DD, got {a.date!r}")
    hhmm(a.start)
    if a.day and a.format != "bootcamp":
        refuse("--day is only for --format bootcamp")
    L, segs = FORMATS[a.format][1](a.close, a.length, a.day)
    spec = {"title": a.title, "presenter": a.presenter or W.format("presenter's name"), "version": 1,
            "format": a.format, "date": a.date, "start": a.start, "tz": a.tz, "length_min": L, "lobby_min": 5,
            "recorded": False, "close": a.close,
            "big_idea": W.format("the one big idea, from §4 or belief.md"),
            "promise": W.format("what they will leave with, one sentence"),
            "beliefs": [{"false": W.format(f"false belief {i}, in the room's words"),
                         "true": W.format(f"true belief {i}")} for i in (1, 2, 3)],
            "not_covering": [W.format("objection set aside, answered in a sentence") for _ in range(3)],
            "offer_disclosed": True,
            "roles": {"host": a.presenter or W.format("host"), "moderator": W.format("moderator's name"),
                      "tech": W.format("who runs the tech")},
            "links": {}, "segments": segs,
            "qa_bank": [{"objection": o, "question": W.format(f"the {o} question in the room's words"),
                         "answer": W.format("three to five sentences in the member's words"),
                         "door": W.format("which door from close.md")} for o in ("time", "money", "confidence", "spouse")],
            "runs": []}
    if a.day:
        spec["day"] = a.day
    if a.launch:
        out = Path(a.launch) / "webinar" / (f"day-{a.day}" if a.day else "") / "webinar.json"
    elif a.out:
        out = Path(a.out)
    else:
        refuse("give --launch launches/<slug> or --out FILE")
    if out.exists() and not a.force:
        refuse(f"{out} exists; pass --force to replace it (the old talk is lost)", 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "written": str(out), "format": a.format, "length_min": L,
                      "blocks": [s["id"] for s in segs]}))


def load_spec(path):
    try:
        spec = json.loads(Path(path).read_text())
    except Exception as e:
        refuse(f"cannot read {path}: {e}")
    if not isinstance(spec.get("segments"), list) or not spec["segments"]:
        refuse("the spec has no segments")
    hhmm(spec.get("start"))
    try:
        date.fromisoformat(str(spec.get("date")))
    except Exception:
        refuse(f"date must be YYYY-MM-DD, got {spec.get('date')!r}")
    for s in spec["segments"]:
        if s.get("kind") not in KINDS:
            refuse(f"segment {s.get('id')!r}: unknown kind {s.get('kind')!r} (kinds: {', '.join(KINDS)})")
        if not isinstance(s.get("min"), (int, float)) or s["min"] <= 0:
            refuse(f"segment {s.get('id')!r}: min must be a positive number of minutes")
    return spec


def timed(spec):
    """Each segment with start/end minutes from the start time (lobby negative) and clock times."""
    h, m = hhmm(spec["start"])
    t0 = datetime.combine(date.fromisoformat(spec["date"]), datetime.min.time()).replace(hour=h, minute=m)
    lob = [s for s in spec["segments"] if s["kind"] == "lobby"]
    rest = [s for s in spec["segments"] if s["kind"] != "lobby"]
    out, t = [], -sum(s["min"] for s in lob)
    for s in lob + rest:
        a = dict(s)
        a["start_min"], a["end_min"] = t, t + s["min"]
        a["at"] = (t0 + timedelta(minutes=t)).strftime("%H:%M")
        a["until"] = (t0 + timedelta(minutes=t + s["min"])).strftime("%H:%M")
        out.append(a)
        t += s["min"]
    return out, t0


def lines(x):
    if not x:
        return []
    return x if isinstance(x, list) else [x]


def proof_txt(p):
    t = f"{p.get('id', '?')} · class {p.get('class', '?')}"
    if p.get("typical"):
        t += f" · typical: {p['typical']}"
    return t


def render_script(spec, segs):
    o = [f"# {spec.get('title')} (version {spec.get('version', 1)})", "",
         f"{spec.get('date')} · {spec.get('start')} {spec.get('tz', '')} · {spec.get('length_min')} minutes · "
         f"{'RECORDED' if spec.get('recorded') else 'live'} · presenter: {spec.get('presenter')} · "
         f"moderator: {(spec.get('roles') or {}).get('moderator', '')}", "",
         f"**Big idea:** {spec.get('big_idea', '')}", "", f"**Promise:** {spec.get('promise', '')}", "", "**Beliefs**"]
    for i, b in enumerate(spec.get("beliefs") or [], 1):
        o.append(f"{i}. From \"{b.get('false', '')}\" to \"{b.get('true', '')}\"")
    o += ["", "**Not covering today (answered in passing):** " + "; ".join(spec.get("not_covering") or []), ""]
    for s in segs:
        o.append(f"## {s['at']}–{s['until']} · {s['title']} ({s['min']} min)")
        for x in lines(s.get("say")):
            o.append(f"- {x}")
        if s.get("chat_prompt"):
            o.append(f"- **Chat:** {s['chat_prompt']}")
        for p in s.get("proof") or []:
            o.append(f"- **Proof:** {proof_txt(p)}")
        if s.get("loop"):
            o.append(f"- **Loop:** {s['loop'].get('question', '')} → {s['loop'].get('answer', '')}")
        for sl in s.get("slides") or []:
            o.append(f"- Slide: {sl.get('title', '')}" + (" — " + " / ".join(lines(sl.get("lines"))) if sl.get("lines") else ""))
        if s.get("notes"):
            o.append(f"- Notes: {s['notes']}")
        o.append("")
    o += ["## Q&A bank", ""]
    for q in spec.get("qa_bank") or []:
        o.append(f"- **{q.get('objection', '')}**: {q.get('question', '')} → {q.get('answer', '')} (door: {q.get('door', '')})")
    return "\n".join(o) + "\n"


def render_notes(spec, segs):
    o = [f"# Speaker notes: {spec.get('title')}", "", "Prompts, not a script. Talk to one person.", ""]
    for s in segs:
        if s["kind"] == "lobby":
            continue
        o.append(f"## {s['at']} · {s['title']} · {s['min']} min (you should be at minute {s['start_min']})")
        for x in lines(s.get("say")):
            o.append(f"- {x}")
        if s.get("chat_prompt"):
            o.append(f"- Ask: {s['chat_prompt']}")
        for p in s.get("proof") or []:
            o.append(f"- Proof {proof_txt(p)}")
        if s.get("loop"):
            o.append(f"- Close the loop: {s['loop'].get('answer', '')}")
        if s.get("notes"):
            o.append(f"- {s['notes']}")
        o.append("")
    return "\n".join(o) + "\n"


def link_url(v):
    return v.get("url", "") if isinstance(v, dict) else str(v)


def render_moderator(spec, segs, t0):
    roles = spec.get("roles") or {}
    links = spec.get("links") or {}
    L = spec.get("length_min", 60)
    off = next((s for s in segs if s["kind"] == "offer"), None)
    o = [f"# Moderator sheet: {spec.get('title')}", "",
         f"Moderator: {roles.get('moderator', '')} · Host: {roles.get('host', '')} · Tech: {roles.get('tech', '')}", "",
         "## Before", "- The test call the day before: join from a computer and a phone, share slides, record, captions, "
         "every link opened on a phone.",
         "- 30 minutes before: open the offer link and the backup link on a phone; both work.",
         "- Recording on with the audio transcript; captions on; save chat on.", "",
         "## During"]
    for s in segs:
        bits = []
        if s.get("chat_prompt"):
            bits.append(f"the presenter asks: \"{s['chat_prompt']}\"; answer kindly and bring forward good replies")
        if s["kind"] == "lobby":
            bits.append("greet people by first name as they arrive; post: \"Welcome! Captions: click CC. "
                        "The session is recorded.\"")
        if s["kind"] == "agreement":
            bits.append("post where the CC (captions) button is, and that the session is recorded")
        if s["kind"] == "offer":
            bits.append("from the first ask: post the offer link and the one-pager, then again every few minutes "
                        "through the Q&A")
        if s["kind"] == "qa":
            bits.append("bring forward the questions from the bank first, then live ones; first names only if "
                        "the person is happy with it")
        for ln in s.get("links") or []:
            if ln in links:
                bits.append(f"link `{ln}`: {link_url(links[ln])}")
        if bits:
            o.append(f"- **{s['at']} · {s['title']}**: " + "; ".join(bits))
    o += ["", "## Time calls to send the presenter"]
    if off:
        o.append(f"- {(t0 + timedelta(minutes=off['start_min'] - 10)).strftime('%H:%M')}: \"10 minutes to the offer\"")
    o.append(f"- {(t0 + timedelta(minutes=L - 10)).strftime('%H:%M')}: \"10 minutes left\"")
    o.append(f"- {(t0 + timedelta(minutes=L - 2)).strftime('%H:%M')}: \"2 minutes, wrap up\"")
    o += ["", "## Links"]
    for k, v in links.items():
        note = " (only if the main link fails)" if "backup" in k else ""
        o.append(f"- `{k}`: {link_url(v)}{note}")
    o += ["", "## If something breaks",
          "- The presenter's connection drops: post \"We'll be right back\"; the host rejoins; use the backup host link.",
          "- The checkout fails: post the backup payment link and tell the presenter so they can say it on air.",
          "- Never type an attendee count, a poll result or a question that was not asked."]
    return "\n".join(o) + "\n"


def render_qa(spec):
    o = [f"# Q&A bank: {spec.get('title')}", "", "Each answer ends by pointing to the right door.", ""]
    for q in spec.get("qa_bank") or []:
        o += [f"## {str(q.get('objection', '')).capitalize()}", f"**They ask:** {q.get('question', '')}", "",
              f"**You say:** {q.get('answer', '')}", "", f"**Door:** {q.get('door', '')}", ""]
    return "\n".join(o) + "\n"


def runsheet_day(spec, segs, t0):
    L = spec.get("length_min", 60)
    day = {"date": spec["date"], "start": spec["start"], "end": (t0 + timedelta(minutes=L)).strftime("%H:%M"),
           "tz": spec.get("tz", ""), "webinar": spec.get("title"),
           "checkout_test": (t0 - timedelta(minutes=30)).strftime("%H:%M"), "segments": []}
    for s in segs:
        notes = " ".join(lines(s.get("say")))
        if s["kind"] == "agreement":
            notes = (s.get("notes") or "Recording notice. Captions on.") + " " + notes
        e = {"min": s["min"], "title": s["title"], "kind": RUNSHEET_KIND[s["kind"]], "notes": notes.strip()}
        if s["kind"] in ("agreement", "promise", "story", "teach", "transition", "offer", "close", "qa", "guest"):
            e["owner"] = "host"
        if s["kind"] == "lobby":
            e["owner"] = "moderator"
        if s.get("links"):
            e["links"] = [x for x in s["links"] if x in (spec.get("links") or {})]
        day["segments"].append(e)
    return day


def cmd_render(a):
    spec = load_spec(a.spec)
    segs, t0 = timed(spec)
    out = Path(a.out_dir) if a.out_dir else Path(a.spec).parent
    out.mkdir(parents=True, exist_ok=True)
    files = {"script.md": render_script(spec, segs), "speaker-notes.md": render_notes(spec, segs),
             "moderator-sheet.md": render_moderator(spec, segs, t0), "qa-bank.md": render_qa(spec)}
    for n, t in files.items():
        (out / n).write_text(t)
    summary = {"ok": True, "written": [str(out / n) for n in files],
               "length_planned": spec.get("length_min"),
               "length_blocks": sum(s["min"] for s in spec["segments"] if s["kind"] != "lobby"),
               "offer_at_min": next((s["start_min"] for s in segs if s["kind"] == "offer"), None),
               "placeholders_left": sum(t.count("[write:") for t in files.values())}
    if a.runsheet:
        rp = Path(a.runsheet)
        rs = {}
        if rp.exists():
            try:
                rs = json.loads(rp.read_text())
            except Exception as e:
                refuse(f"cannot read {rp}: {e}")
        rs.setdefault("title", spec.get("title"))
        rs.setdefault("allow_early_pitch", False)
        rs.setdefault("close", spec.get("close", "checkout"))
        roles = rs.setdefault("roles", {})
        for k, v in (spec.get("roles") or {}).items():
            roles.setdefault(k, v)
        roles.setdefault("closer", (spec.get("roles") or {}).get("host", ""))
        lk = rs.setdefault("links", {})
        for k, v in (spec.get("links") or {}).items():
            lk.setdefault(k, v)
        day = runsheet_day(spec, segs, t0)
        days = [d for d in rs.get("days", []) if d.get("date") != spec["date"]]
        days.append(day)
        rs["days"] = sorted(days, key=lambda d: (d.get("date", ""), d.get("start", "")))
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(rs, indent=2, ensure_ascii=False) + "\n")
        summary["runsheet"] = str(rp)
    print(json.dumps(summary))


def cmd_offer_summary(a):
    try:
        text = Path(a.close).read_text()
    except Exception as e:
        refuse(f"cannot read {a.close}: {e}")
    pend = [ln.strip() for ln in text.splitlines() if re.search(r"\bPENDING\b", ln)]
    if pend:
        print(json.dumps({"ok": False, "pending": pend,
                          "say": "close.md still has PENDING elements; settle them with the member first."}))
        sys.exit(1)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    keep = []
    for ln in text.splitlines():
        low = ln.lower()
        if "backup" in low or "moderator only" in low or "internal" in low:
            continue
        if re.match(r"^\s*#\s", ln):
            continue
        keep.append(ln.rstrip())
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(keep)).strip()
    title = a.title or "What's on offer"
    out = (f"# {title}\n\n{body}\n\n---\n_Every price, payment plan, guarantee and date here is copied from the launch's "
           f"close.md on {date.today().isoformat()}. If anything here differs from what you heard, this page is right; "
           f"ask us._\n")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(out)
    print(json.dumps({"ok": True, "written": a.out, "lines": len(keep)}))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Webinar Builder: outline, render, run-sheet day, offer one-pager")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("formats")
    o = sub.add_parser("outline")
    o.add_argument("--format", required=True)
    o.add_argument("--day", type=int, choices=(1, 2, 3))
    o.add_argument("--title", required=True)
    o.add_argument("--presenter")
    o.add_argument("--date", required=True)
    o.add_argument("--start", required=True)
    o.add_argument("--tz", required=True)
    o.add_argument("--close", default="checkout", choices=("checkout", "call", "both"))
    o.add_argument("--length", type=int)
    o.add_argument("--launch")
    o.add_argument("--out")
    o.add_argument("--force", action="store_true")
    r = sub.add_parser("render")
    r.add_argument("--spec", required=True)
    r.add_argument("--out-dir")
    r.add_argument("--runsheet")
    s = sub.add_parser("offer-summary")
    s.add_argument("--close", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--title")
    a = ap.parse_args(argv)
    {"formats": cmd_formats, "outline": cmd_outline, "render": cmd_render, "offer-summary": cmd_offer_summary}[a.cmd](a)


if __name__ == "__main__":
    main()
