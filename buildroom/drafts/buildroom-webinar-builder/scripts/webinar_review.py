#!/usr/bin/env python3
"""Webinar Builder review: the rehearsal and run scorecards, the diagnosis, and the evergreen gate.

Local only. Reads a Zoom transcript (.vtt, .srt or plain text), the saved chat (.txt) and the attendance report
(.csv) the member downloads. Counts and question text only: no attendee name is written to a scorecard.

Usage
  webinar_review.py review --kind rehearsal|run --transcript FILE [--spec webinar.json] [--chat chat.txt]
                           [--attendance attendees.csv] [--registered N] [--attended N] [--buyers N]
                           [--calls-booked N] [--log webinar.json] --out scorecard.md
      Writes the scorecard (each line PASS, WATCH or FIX) and the three fixes; prints JSON. With --kind run,
      --chat and --attendance add who stayed, chat by block and the questions not answered aloud; --log appends
      {date, version, kind, registered, attended, peak, at_offer, at_end, buyers, calls_booked} to the spec's runs.
  webinar_review.py diagnose --registered N --attended N --at-offer N [--buyers N] [--calls-booked N]
                             [--close checkout|call] [--price P]
      The first leak, in order show-up, stay to the offer, close, with the fix. Prints JSON.
  webinar_review.py evergreen-ready --spec webinar.json [--min-rate 0.02] [--min-calls-per-100 5]
      READY when a logged live run converted (exit 0), otherwise NOT YET with why (exit 1).

The lines used are starting points from the research behind the skill, not promises.
Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import argparse, csv, json, re  # noqa: E402
from datetime import date, datetime  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import webinar_check as wc  # noqa: E402

TS = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d{1,3}))?\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})")
TYPICAL = re.compile(r"\b(typical|typically|most clients|most people|on average|usually|results vary)\b", re.I)
ASK = re.compile(r"\?|\b(type|put|drop) (it |that |a |your |yes |1 |2 |one )?.{0,20}(in|into) the chat\b|\bin the chat\b", re.I)
STOP = set("about after again also because been before being could does doing from have here into just like make more "
           "most much only other over really should some still such than that their them then there these they this "
           "those very want what when where which while will with would your yours you".split())


def refuse(msg):
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(2)


# ---------------------------------------------------------------- readers

def read_transcript(path):
    """[(start_min, end_min, speaker, text)]; times None for a plain transcript."""
    try:
        raw = Path(path).read_text(errors="replace")
    except Exception as e:
        refuse(f"cannot read {path}: {e}")
    cues, cur = [], None
    for ln in raw.splitlines():
        m = TS.search(ln)
        if m:
            h, mi, s, _, h2, m2, s2 = m.groups()
            cur = [int(h) * 60 + int(mi) + int(s) / 60, int(h2) * 60 + int(m2) + int(s2) / 60, "", ""]
            cues.append(cur)
            continue
        t = ln.strip()
        if not t or t == "WEBVTT" or t.isdigit() or t.startswith("NOTE"):
            continue
        if cur is None:
            cues.append([None, None, "", t])
            cur = cues[-1] if False else None
            continue
        sp = re.match(r"^([^:]{1,40}):\s+(.*)", t)
        if sp and not cur[3]:
            cur[2], t = sp.group(1).strip(), sp.group(2)
        cur[3] = (cur[3] + " " + t).strip()
    return [tuple(c) for c in cues if c[3]]


def read_chat(path, start_hhmm=None):
    """[(minute, is_question, text)] from a Zoom chat .txt; clock times are made relative to the start."""
    try:
        raw = Path(path).read_text(errors="replace")
    except Exception as e:
        refuse(f"cannot read {path}: {e}")
    out, cur = [], None
    rx = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s+From\s+(.+?)(?:\s+to\s+.+?)?\s*:\s*(.*)$")
    for ln in raw.splitlines():
        m = rx.match(ln.strip())
        if m:
            h, mi, s, _who, text = m.groups()
            cur = [int(h) * 60 + int(mi) + int(s or 0) / 60, text.strip()]
            out.append(cur)
        elif cur is not None and ln.strip():
            cur[1] = (cur[1] + " " + ln.strip()).strip()
    if out and start_hhmm:
        sh, sm = (int(x) for x in start_hhmm.split(":"))
        base = sh * 60 + sm
        if out[0][0] >= base - 60:  # clock times, not elapsed
            for c in out:
                c[0] -= base
    return [(round(t, 2), "?" in tx, tx) for t, tx in out if tx]


def parse_dt(s):
    s = s.strip()
    for f in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %I:%M %p", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M",
              "%Y-%m-%d %H:%M", "%b %d, %Y %I:%M:%S %p", "%b %d, %Y %H:%M:%S"):
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    return None


def read_attendance(path, date_s, start_hhmm):
    """Per person, merged (join, leave) minutes from the start. People are keyed by email or name, never written."""
    try:
        text = Path(path).read_text(errors="replace")
    except Exception as e:
        refuse(f"cannot read {path}: {e}")
    lines = text.splitlines()
    hdr = next((i for i, ln in enumerate(lines) if re.search(r"join time", ln, re.I) and re.search(r"leave time", ln, re.I)), None)
    if hdr is None:
        refuse(f"{path}: no 'Join Time' and 'Leave Time' columns (export the attendee or participants report as CSV)")
    rows = list(csv.DictReader(lines[hdr:]))
    cols = rows[0].keys() if rows else []
    jc = next(c for c in cols if re.search(r"join time", c, re.I))
    lc = next(c for c in cols if re.search(r"leave time", c, re.I))
    kc = next((c for c in cols if re.search(r"email", c, re.I)), None) or next((c for c in cols if re.search(r"name", c, re.I)), None)
    sh, sm = (int(x) for x in start_hhmm.split(":"))
    t0 = datetime.combine(date.fromisoformat(date_s), datetime.min.time()).replace(hour=sh, minute=sm)
    people = {}
    for i, r in enumerate(rows):
        j, l = parse_dt(r.get(jc, "")), parse_dt(r.get(lc, ""))
        if not j or not l:
            continue
        k = (r.get(kc) or f"row{i}").strip().lower() if kc else f"row{i}"
        people.setdefault(k, []).append(((j - t0).total_seconds() / 60, (l - t0).total_seconds() / 60))
    return people


def present(people, minute):
    return sum(1 for iv in people.values() if any(a <= minute <= b for a, b in iv))


# ---------------------------------------------------------------- review

def cue_phrases(seg):
    out = []
    for x in wc.strings(seg.get("say"))[:2] + [sl.get("title", "") for sl in seg.get("slides") or []]:
        w = wc.norm(x).split()
        if len(w) >= 3 and "write" not in w:
            out.append(" ".join(w[:4]))
    return out


def find_block_starts(spec, cues):
    starts = {}
    if not spec or not cues or cues[0][0] is None:
        return starts
    for s in spec.get("segments") or []:
        for ph in cue_phrases(s):
            hit = next((c[0] for c in cues if ph in wc.norm(c[3])), None)
            if hit is not None:
                starts[s.get("id")] = round(hit, 1)
                break
    return starts


def offer_start(spec, cues, planned):
    if not cues or cues[0][0] is None:
        return None
    seg = next((s for s in (spec or {}).get("segments", []) if s.get("kind") == "offer"), None)
    phrases = cue_phrases(seg) if seg else []
    for c in cues:
        tx = wc.norm(c[3])
        if any(p in tx for p in phrases):
            return round(c[0], 1)
    floor = (planned or 0) * 0.5
    for c in cues:
        if c[0] >= floor and (wc.MONEY.search(c[3]) or re.search(r"how (i|we) can help|here'?s (the|my) offer", c[3], re.I)):
            return round(c[0], 1)
    return None


def plan_times(spec):
    st, t = {}, 0
    for s in spec.get("segments") or []:
        if s.get("kind") == "lobby":
            continue
        st[s.get("id")] = (t, t + s.get("min", 0), s)
        t += s.get("min", 0)
    return st, t


def review(a):
    spec = None
    if a.spec:
        try:
            spec = json.loads(Path(a.spec).read_text())
        except Exception as e:
            refuse(f"cannot read {a.spec}: {e}")
    cues = read_transcript(a.transcript)
    if not cues:
        refuse(f"{a.transcript}: no transcript text found")
    timed = cues[0][0] is not None
    planned_st, planned_len = plan_times(spec) if spec else ({}, None)
    L = (spec or {}).get("length_min") or planned_len
    host = str(((spec or {}).get("roles") or {}).get("host", "") or (spec or {}).get("presenter", "")).lower()
    speakers = {c[2] for c in cues if c[2]}
    host_sp = next((s for s in speakers if host and (s.lower() in host or host.split()[0] in s.lower())), None)
    hcues = [c for c in cues if not host_sp or c[2] == host_sp or not c[2]]
    lines, fixes = [], []

    def line(cid, verdict, detail, fix=None):
        lines.append({"id": cid, "verdict": verdict, "detail": detail})
        if verdict == "FIX" and fix:
            fixes.append((cid, fix))

    o_plan = next((v[0] for v in planned_st.values() if v[2].get("kind") == "offer"), None)
    o_act = offer_start(spec, cues, o_plan)
    end = round(max(c[1] for c in cues), 1) if timed else None
    if timed and o_plan is not None:
        if o_act is None:
            line("time_to_offer", "FIX", "the offer was not found in the transcript",
                 "Say the offer's opening line as written, so people know the offer has started")
        else:
            late = round(o_act - o_plan, 1)
            line("time_to_offer", "FIX" if late > 5 else "WATCH" if late > 2 else "PASS",
                 f"the offer started at minute {o_act} (planned {o_plan}; {late:+} min)",
                 f"Cut {late:g} minutes before the offer: shorten the story and the longest teaching block")
    if timed and L:
        over = round(end - L, 1)
        line("total_length", "FIX" if over > 2 else "WATCH" if over > 0 else "PASS", f"ran {end} minutes (planned {L})",
             f"Trim {over:g} minutes so it ends on time; this audience notices")
    if timed and spec:
        bs = find_block_starts(spec, cues)
        ids = [k for k in planned_st if k in bs]
        long = []
        for i, k in enumerate(ids):
            nxt = bs[ids[i + 1]] if i + 1 < len(ids) else (o_act if planned_st[k][2].get("kind") != "offer" and o_act else end)
            if nxt is None:
                continue
            act = round(nxt - bs[k], 1)
            pl = planned_st[k][1] - planned_st[k][0]
            if pl and act > pl * 1.5 and act - pl >= 2:
                long.append(f"{k} {act} min (planned {pl})")
        line("block_timings", "WATCH" if long else "PASS", "; ".join(long) or
             f"blocks found for {len(ids)} of {len(planned_st)} planned blocks, none far over")
    pre = [c for c in hcues if o_act is None or c[0] is None or c[0] < o_act]
    open_hits = [wc.OPEN_LOOP.search(c[3]).group(0) for c in pre if wc.OPEN_LOOP.search(c[3])]
    line("loops_open", "FIX" if open_hits else "PASS", ("deferred answers: " + "; ".join(sorted(set(open_hits))[:4]))
         if open_hits else "no answer deferred to the program", "Answer each block's question in the room, then bridge to the offer")
    unl = []
    for i, c in enumerate(pre):
        if (wc.MONEY.search(c[3]) or wc.PCT.search(c[3])) and wc.EARN.search(c[3]):
            near = " ".join(x[3] for x in pre[max(0, i - 2): i + 3])
            if not TYPICAL.search(near):
                unl.append(c[3][:70])
    line("unlabelled_proof", "FIX" if unl else "PASS", ("said without the typical result: " + " | ".join(unl[:3])) if unl
         else "every figure came with the typical result", "Say the typical result beside each figure, or drop the figure")
    sents = re.split(r"(?<=[.!?])\s+", " ".join(c[3] for c in hcues))
    longs = [s for s in sents if len(s.split()) > 45]
    script_ngrams = set()
    for s in (spec or {}).get("segments", []):
        for x in wc.strings(s.get("say")) + wc.strings(s.get("notes")):
            w = wc.norm(x).split()
            script_ngrams |= {" ".join(w[i:i + 8]) for i in range(len(w) - 7)}
    tw = wc.norm(" ".join(c[3] for c in hcues)).split()
    read = sum(1 for i in range(len(tw) - 7) if " ".join(tw[i:i + 8]) in script_ngrams)
    line("sounds_read", "WATCH" if len(longs) > 3 or read > 3 else "PASS",
         f"{len(longs)} very long sentences, {read} eight-word runs read word for word from the notes",
         "Speak from the prompts; break long sentences with a pause")
    asks = sum(1 for c in hcues if ASK.search(c[3]))
    need = sum(1 for v in planned_st.values() if v[2].get("kind") in ("agreement", "teach")) or 4
    line("interaction", "WATCH" if asks < need else "PASS", f"{asks} questions or chat prompts to the room (aim for {need}+)",
         "Ask the planned chat prompt in every block, out loud")
    if timed and o_act is not None:
        words = set()
        seg = next((s for s in (spec or {}).get("segments", []) if s.get("kind") == "offer"), None)
        for sl in (seg or {}).get("slides") or []:
            words |= {w for w in wc.norm(sl.get("title", "")).split() if len(w) > 4 and w not in STOP}
        n = sum(1 for c in hcues if c[0] >= o_act and (re.search(r"\blink\b|\bjoin\b|\bsign up\b|\bbook\b|\bapply\b", c[3], re.I)
                                                       or (words and words & set(wc.norm(c[3]).split()))))
        line("offer_said_three", "PASS" if n >= 3 else "WATCH", f"the offer or its link was asked for {n} times after it started",
             "Ask for it three times, with the link on screen and in the chat")
    every = " ".join(c[3] for c in cues)
    ref = [f"{k}: {rx.search(every).group(0)!r}" for k, rx in wc.REFUSED.items() if rx.search(every)]
    if (spec or {}).get("recorded") and wc.LIVE_CLAIM.search(every):
        ref.append("live_claim on a recording")
    line("refused_words", "FIX" if ref else "PASS", "; ".join(ref) or "nothing the honesty rules refuse was said",
         "Remove the line; say the honest version (honesty-rules.md)")

    res = {"ok": True, "kind": a.kind, "timed": timed, "offer_at": o_act, "length": end, "lines": lines}
    run = {"date": (spec or {}).get("date") or date.today().isoformat(), "version": (spec or {}).get("version", 1), "kind": a.kind}

    # ---- a live run: attendance, chat, numbers
    att_lines, chat_lines = [], []
    if a.kind == "run":
        people = read_attendance(a.attendance, spec["date"], spec["start"]) if a.attendance and spec else None
        if people:
            att = len(people)
            peak = max(present(people, m) for m in range(0, int((end or L or 60)) + 1))
            at2 = present(people, 2)
            ao = present(people, o_act) if o_act is not None else None
            ae = present(people, (end or L) - 1)
            run.update({"attended": att, "peak": peak, "at_offer": ao, "at_end": ae})
            att_lines.append(f"{att} people attended; {at2} there at minute 2, peak {peak} at once, "
                             f"{ao if ao is not None else '?'} when the offer started, {ae} at the end")
            for k, (s0, s1, sg) in planned_st.items():
                a0, a1 = present(people, s0), present(people, max(s0, s1 - 0.5))
                if a0:
                    att_lines.append(f"- {k} ({sg.get('title', '')[:40]}): {a0} → {a1} ({a1 - a0:+})")
            if att and ao is not None and ao / att < 0.5:
                fixes.append(("stay_to_offer", "Fewer than half were still there at the offer: tighten the first 30 minutes "
                                               "and start the offer earlier"))
        elif a.attended:
            run["attended"] = a.attended
        if a.chat:
            chat = read_chat(a.chat, (spec or {}).get("start"))
            per = {}
            for t, q, tx in chat:
                k = next((k for k, (s0, s1, _) in planned_st.items() if s0 <= t < s1), "outside")
                per[k] = per.get(k, 0) + 1
            chat_lines.append(f"{len(chat)} chat messages; by block: " + ", ".join(f"{k} {v}" for k, v in per.items()))
            unans = []
            for t, q, tx in chat:
                if not q:
                    continue
                kw = [w for w in wc.norm(tx).split() if len(w) > 4 and w not in STOP][:4]
                after = wc.norm(" ".join(c[3] for c in hcues if c[0] is None or c[0] >= t - 0.5))
                if kw and sum(1 for w in kw if w in after) < min(2, len(kw)):
                    unans.append(tx[:100])
            chat_lines.append(f"{sum(1 for x in chat if x[1])} questions asked; {len(unans)} not answered aloud")
            chat_lines += [f"  - \"{u}\"" for u in unans[:8]]
            if unans:
                fixes.append(("unanswered", f"Add {min(3, len(unans))} of the unanswered questions to the Q&A bank with an answer and a door"))
            if per:
                res["most_chat_block"] = max((k for k in per if k != "outside"), key=lambda k: per[k], default=None)
        for k in ("registered", "buyers", "calls_booked"):
            v = getattr(a, k)
            if v is not None:
                run[k] = v
        if run.get("attended") and run.get("registered"):
            res["show_up"] = round(run["attended"] / run["registered"], 3)
        if run.get("attended") and run.get("buyers") is not None:
            res["buy_rate"] = round(run["buyers"] / run["attended"], 3)
        res["run"] = run

    top = [f for f in fixes][:3]
    md = [f"# {'Rehearsal' if a.kind == 'rehearsal' else 'Run'} scorecard: {(spec or {}).get('title', a.transcript)}"
          f" (version {(spec or {}).get('version', 1)})", "",
          "| Line | Verdict | Detail |", "|---|---|---|"]
    md += [f"| `{x['id']}` | {x['verdict']} | {x['detail'].replace('|', '/')} |" for x in lines]
    if att_lines:
        md += ["", "## Who stayed", ""] + att_lines
    if chat_lines:
        md += ["", "## The chat (counts and questions only; no names)", ""] + chat_lines
    if a.kind == "run":
        md += ["", "## The numbers", "", ", ".join(f"{k} {v}" for k, v in run.items() if k not in ("date", "version", "kind"))]
    md += ["", "## The three fixes", ""] + [f"{i}. **{c}**: {f}" for i, (c, f) in enumerate(top, 1)]
    if not top:
        md.append("Nothing to fix urgently. Keep what worked, and run it again.")
    md += ["", "_Starting points from the research, not promises. Judge sales after the follow-up window closes._"]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(md) + "\n")
    res["fixes"] = [{"id": c, "fix": f} for c, f in top]
    res["written"] = a.out
    if a.log and a.kind == "run":
        try:
            sp = json.loads(Path(a.log).read_text())
            sp.setdefault("runs", []).append(run)
            Path(a.log).write_text(json.dumps(sp, indent=2, ensure_ascii=False) + "\n")
            res["logged"] = a.log
        except Exception as e:
            refuse(f"cannot log to {a.log}: {e}")
    print(json.dumps(res, indent=2))


# ---------------------------------------------------------------- diagnose and evergreen

def diagnose(a):
    if not a.registered or a.attended is None or a.at_offer is None:
        refuse("give --registered, --attended and --at-offer")
    show = a.attended / a.registered
    stay = a.at_offer / a.attended if a.attended else 0
    call = a.close == "call" or (a.price or 0) >= 2000
    rates = {"show_up": round(show, 3), "stay_to_offer": round(stay, 3)}
    if call:
        cp = (a.calls_booked or 0) * 100 / a.attended if a.attended else 0
        rates["calls_per_100_attendees"] = round(cp, 1)
        close_ok, close_line = cp >= 5, "about 5 calls booked per 100 attendees"
    else:
        br = (a.buyers or 0) / a.attended if a.attended else 0
        rates["buyers_per_attendee"] = round(br, 3)
        close_ok, close_line = br >= 0.01, "about 1–5% of attendees buying an offer under $2,000"
    if show < 0.33:
        leak, fix = "show_up", ("Fewer than a third came live. The fix is outside the talk: story emails before the invite, a "
                                "reminder 24 hours and 1 hour before (the best evidenced), check the spam folder, test the time "
                                "slot. The Event Launcher owns these.")
    elif stay < 0.5:
        leak, fix = "stay_to_offer", ("Fewer than half of the live room was there when the offer started. Tighten the first 30 "
                                      "minutes: a faster opening, a shorter story, the strongest block first, the offer earlier.")
    elif not close_ok:
        leak, fix = "close", ("People stayed but few bought or booked. Check the teaching for loops left open and a gap never "
                              "created, the transition, the unanswered objections (add them to the Q&A bank), the clarity of "
                              "the offer (the one-pager), and whether the follow-up went out.")
    else:
        leak, fix = None, "No leak below the starting lines. Protect what worked and run it again."
    print(json.dumps({"rates": rates, "first_leak": leak, "fix": fix,
                      "lines": {"show_up": "about a third to a half live", "stay_to_offer": "about half of the live room",
                                "close": close_line},
                      "note": "Starting points from the research, not promises. Judge after the follow-up window closes."}, indent=2))


def evergreen(a):
    try:
        spec = json.loads(Path(a.spec).read_text())
    except Exception as e:
        refuse(f"cannot read {a.spec}: {e}")
    runs = [r for r in spec.get("runs") or [] if r.get("kind") == "run"]
    why, ok = [], False
    for r in runs:
        att = r.get("attended") or 0
        if not att:
            continue
        if spec.get("close") == "call":
            cp = (r.get("calls_booked") or 0) * 100 / att
            if cp >= a.min_calls_per_100:
                ok = True
                why.append(f"{r.get('date')}: {cp:.1f} calls booked per 100 attendees")
        else:
            br = (r.get("buyers") or 0) / att
            if (r.get("buyers") or 0) > 0 and br >= a.min_rate:
                ok = True
                why.append(f"{r.get('date')}: {br:.1%} of attendees bought")
    if not runs:
        why = ["no live run logged yet (webinar_review.py review --kind run --log)"]
    elif not ok:
        why = [f"no logged live run reached {a.min_rate:.0%} buying" if spec.get("close") != "call" else
               f"no logged live run reached {a.min_calls_per_100} calls per 100 attendees"]
    print(json.dumps({"result": "READY" if ok else "NOT YET", "why": why,
                      "say": "A live run converted; a recorded version may be built, labelled as recorded." if ok else
                      "Run it live again first: a recording of a talk that did not convert live will not convert recorded."}))
    sys.exit(0 if ok else 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Webinar Builder review")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review")
    r.add_argument("--kind", required=True, choices=("rehearsal", "run"))
    r.add_argument("--transcript", required=True)
    r.add_argument("--spec")
    r.add_argument("--chat")
    r.add_argument("--attendance")
    for k in ("registered", "attended", "buyers", "calls-booked"):
        r.add_argument("--" + k, type=int)
    r.add_argument("--log")
    r.add_argument("--out", required=True)
    d = sub.add_parser("diagnose")
    for k in ("registered", "attended", "at-offer", "buyers", "calls-booked"):
        d.add_argument("--" + k, type=int)
    d.add_argument("--close", default="checkout", choices=("checkout", "call"))
    d.add_argument("--price", type=float)
    e = sub.add_parser("evergreen-ready")
    e.add_argument("--spec", required=True)
    e.add_argument("--min-rate", type=float, default=0.02)
    e.add_argument("--min-calls-per-100", type=float, default=5)
    a = ap.parse_args(argv)
    {"review": review, "diagnose": diagnose, "evergreen-ready": evergreen}[a.cmd](a)


if __name__ == "__main__":
    main()
