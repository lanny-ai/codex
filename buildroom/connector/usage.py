"""Usage summary for the host dashboard, and the signals that let Build Room OS get better with use.

The connector writes one line per tool call: when, which member, which tool, which session, and whether it
worked. Nothing a member typed and nothing from their Business File is ever recorded. This module turns
those lines into what the host needs: who is active, who connected but never started, who has gone quiet,
and which sessions are used.

Three further signals, all of them numbers or short fixed labels, never text a member wrote:
  1. how a session ended (finished, or stopped at which step);
  2. how many things its checks asked to fix, by kind;
  3. results a member chose to share (calls booked, opt-in rate and the like), only from the list in METRICS,
     and only after that member switched sharing on.
A report that carries anything else is refused whole, so nothing free-form can ride along.
"""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ACTIVE_DAYS, QUIET_DAYS = 7, 21
START = "buildroom_start_session"
REPORT = "buildroom_report"
MAX_LOG_BYTES = 25_000_000
MIN_GROUP = 5            # a combined figure is shown to members only when at least this many members are behind it
FRESH_DAYS = 90          # a shared result older than this no longer counts
SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
# The only results a member can share: name -> (lowest, highest, what it is). Whole numbers or one decimal; no text.
METRICS = {
    "linkedin_posts_week": (0, 30, "LinkedIn posts published in a week"),
    "linkedin_comments_week": (0, 500, "comments left on other people's LinkedIn posts in a week"),
    "linkedin_conversations_week": (0, 300, "LinkedIn conversations started in a week"),
    "linkedin_calls_booked_week": (0, 100, "calls booked from LinkedIn in a week"),
    "leads_month": (0, 100000, "new leads in a month"),
    "calls_booked_month": (0, 2000, "sales calls booked in a month"),
    "clients_won_month": (0, 500, "new clients in a month"),
    "optin_rate_pct": (0, 100, "share of page visitors who opted in, in percent"),
    "booking_rate_pct": (0, 100, "share of leads who booked a call, in percent"),
    "show_rate_pct": (0, 100, "share of booked calls that happened, in percent"),
    "close_rate_pct": (0, 100, "share of calls that became clients, in percent"),
    "speaking_pitches_month": (0, 500, "speaking pitches sent in a month"),
    "speaking_bookings_month": (0, 100, "speaking engagements booked in a month"),
    "reviews_new_month": (0, 1000, "new public reviews in a month"),
    "answer_pages_month": (0, 100, "answer pages published in a month"),
}


def clean_report(args, skills):
    """(record fields, None) for a well-formed session report, or (None, why it is refused).
    Everything is a fixed label or a number. Any unknown field, any free text, refuses the whole report."""
    if not isinstance(args, dict):
        return None, "the report must be an object"
    extra = set(args) - {"skill", "event", "step", "fix", "look", "kinds", "numbers"}
    if extra:
        return None, "unknown field(s): " + ", ".join(sorted(map(str, extra))[:5]) + ". A report carries labels and numbers only"
    if args.get("skill") not in skills:
        return None, "skill must be a session name from buildroom_list_sessions"
    if args.get("event") not in ("finished", "stopped"):
        return None, 'event must be "finished" or "stopped"'
    out = {"skill": args["skill"], "event": args["event"]}
    step = args.get("step")
    if step is not None:
        if not isinstance(step, str) or not SLUG.fullmatch(step):
            return None, 'step is a short label such as "phase-2": lower-case letters, digits and hyphens, at most 40'
        out["step"] = step
    for k in ("fix", "look"):
        v = args.get(k)
        if v is not None:
            if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 9999:
                return None, f"{k} is a whole number from 0 to 9999"
            out[k] = v
    kinds = args.get("kinds")
    if kinds is not None:
        if not isinstance(kinds, dict) or len(kinds) > 30:
            return None, "kinds is an object of at most 30 short labels, each with a count"
        for k, v in kinds.items():
            if not isinstance(k, str) or not SLUG.fullmatch(k) or isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 9999:
                return None, 'each kind is a short label (the word before the colon of a FIX line, such as "colors") with a whole-number count'
        out["kinds"] = dict(kinds)
    nums = args.get("numbers")
    if nums is not None:
        if not isinstance(nums, dict) or not nums:
            return None, "numbers is an object of results the member chose to share"
        for k, v in nums.items():
            if k not in METRICS:
                return None, f"{k!r} is not a result that can be shared. The list: " + ", ".join(METRICS)
            lo, hi, _ = METRICS[k]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
                return None, f"{k} must be a number from {lo} to {hi}"
        out["numbers"] = {k: round(float(v), 1) for k, v in nums.items()}
    return out, None


def sharing_path(data_dir):
    return Path(data_dir) / "sharing.json" if data_dir else None


def sharing_read(data_dir):
    p = sharing_path(data_dir)
    try:
        d = json.loads(p.read_text(encoding="utf-8")) if p and p.is_file() else {}
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def sharing_set(data_dir, email, on, now=None):
    p = sharing_path(data_dir)
    if not p:
        return False
    d = sharing_read(data_dir)
    d[email] = {"on": bool(on), "at": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")}
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(d), encoding="utf-8")
        tmp.replace(p)
        return True
    except OSError:
        return False


def _middle(values):
    v = sorted(values)
    n = len(v)
    med = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    return round(med, 1), round(v[n // 4], 1), round(v[(3 * n) // 4 if n > 1 else 0], 1)


def shared_results(records, sharing, now=None):
    """{metric: [each sharing member's latest value]} from reports in the last FRESH_DAYS. A member who has since
    switched sharing off is left out, including what they shared before."""
    now = now or datetime.now(timezone.utc)
    latest = {}
    for r in records:
        at = _when(r.get("at"))
        if r.get("tool") != REPORT or r.get("outcome") != "ok" or not isinstance(r.get("numbers"), dict) or not at or (now - at).days > FRESH_DAYS:
            continue
        if not (sharing.get(r["member"]) or {}).get("on"):
            continue
        for k, v in r["numbers"].items():
            if k in METRICS and isinstance(v, (int, float)) and (k not in latest.setdefault(r["member"], {}) or latest[r["member"]][k][0] < at):
                latest[r["member"]][k] = (at, v)
    out = {}
    for vals in latest.values():
        for k, (_at, v) in vals.items():
            out.setdefault(k, []).append(v)
    return out


def benchmarks(records, sharing, now=None):
    """What members may see: one combined line per result, and only where MIN_GROUP or more members are behind it."""
    rows = []
    for k, vals in sorted(shared_results(records, sharing, now).items()):
        if len(vals) >= MIN_GROUP:
            med, lo, hi = _middle(vals)
            rows.append({"metric": k, "what": METRICS[k][2], "members": len(vals), "middle": med, "from": lo, "to": hi})
    return rows


def insights(records, sharing, skills, now=None):
    """For the host: how sessions end, what the checks keep catching, and the results members shared."""
    now = now or datetime.now(timezone.utc)
    per = {s["skill"]: {"skill": s["skill"], "starts": 0, "finished": 0, "stopped": 0, "steps": {}, "fix": 0, "look": 0, "reports": 0} for s in skills}
    kinds = {}
    for r in records:
        at = _when(r.get("at"))
        if r.get("outcome") != "ok" or r.get("skill") not in per or not at or (now - at).days > FRESH_DAYS:
            continue
        p = per[r["skill"]]
        if r.get("tool") == START:
            p["starts"] += 1
        elif r.get("tool") == REPORT:
            p["reports"] += 1
            p[r.get("event") if r.get("event") in ("finished", "stopped") else "stopped"] += 1
            if r.get("event") == "stopped" and r.get("step"):
                p["steps"][r["step"]] = p["steps"].get(r["step"], 0) + 1
            p["fix"] += r.get("fix") or 0
            p["look"] += r.get("look") or 0
            for k, v in (r.get("kinds") or {}).items():
                e = kinds.setdefault((r["skill"], k), 0)
                kinds[(r["skill"], k)] = e + v
    tools = []
    for p in per.values():
        if not (p["starts"] or p["reports"]):
            continue
        tools.append({"skill": p["skill"], "starts": p["starts"], "finished": p["finished"], "stopped": p["stopped"],
                      "finish_rate": round(p["finished"] / p["starts"], 2) if p["starts"] and p["reports"] else None,
                      "stopped_at": sorted(p["steps"].items(), key=lambda kv: -kv[1])[:3],
                      "fixes_per_report": round(p["fix"] / p["reports"], 1) if p["reports"] else None})
    tools.sort(key=lambda t: (-(t["stopped"]), -(t["starts"]), t["skill"]))
    caught = [{"skill": s, "kind": k, "count": n} for (s, k), n in sorted(kinds.items(), key=lambda kv: -kv[1])[:12]]
    shared = []
    for k, vals in sorted(shared_results(records, sharing, now).items()):
        med, lo, hi = _middle(vals)
        shared.append({"metric": k, "what": METRICS[k][2], "members": len(vals), "middle": med, "from": lo, "to": hi, "shown_to_members": len(vals) >= MIN_GROUP})
    return {"window_days": FRESH_DAYS, "tools": tools, "caught": caught, "shared": shared,
            "sharing_on": sum(1 for v in sharing.values() if (v or {}).get("on")), "min_group": MIN_GROUP}


def log_path(data_dir):
    return Path(data_dir) / "usage.jsonl" if data_dir else None


def append(data_dir, line):
    """Keep a copy of a usage line on the data volume. Never raises: a full disk must not break a session."""
    p = log_path(data_dir)
    if not p:
        return
    try:
        if p.exists() and p.stat().st_size > MAX_LOG_BYTES:
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def read(data_dir):
    p = log_path(data_dir)
    out = []
    if not (p and p.is_file()):
        return out
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict) and r.get("at") and r.get("member"):
                    out.append(r)
    except OSError:
        pass
    return out


def _when(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def summarize(records, members, skills, now=None):
    """records: usage lines. members: [{email, name, status, added, via}]. skills: [{skill, description}]."""
    now = now or datetime.now(timezone.utc)
    recs = sorted(((_when(r["at"]), r) for r in records if _when(r.get("at"))), key=lambda x: x[0])
    since = recs[0][0] if recs else None
    known = {m["email"]: m for m in members if m.get("email")}
    per = {}
    for at, r in recs:
        if r.get("outcome") != "ok":
            continue
        p = per.setdefault(r["member"], {"first": at, "last": at, "calls": 0, "starts": 0, "last_start": None, "skills": {}, "days": set()})
        p["last"], p["calls"] = at, p["calls"] + 1
        p["days"].add(at.date())
        if r.get("tool") == START and r.get("skill"):
            p["starts"] += 1
            p["last_start"] = at
            p["skills"][r["skill"]] = p["skills"].get(r["skill"], 0) + 1

    def state(email, p):
        if known.get(email, {}).get("status") not in (None, "active"):
            return "stopped"
        if not p:
            return "not_connected"
        if not p["starts"]:
            return "connected_not_started"
        idle = (now - p["last_start"]).days
        return "active" if idle <= ACTIVE_DAYS else "quiet" if idle <= QUIET_DAYS else "gone_quiet"

    week = {}
    for at, r in recs:
        if r.get("outcome") == "ok" and r.get("tool") == START and (now - at).days < 7:
            week[r["member"]] = week.get(r["member"], 0) + 1
    rows = []
    for email in sorted(set(known) | set(per)):
        m, p = known.get(email, {}), per.get(email)
        top = max(p["skills"].items(), key=lambda kv: kv[1])[0] if p and p["skills"] else None
        rows.append({"email": email, "name": m.get("name") or "", "status": m.get("status") or ("active" if p else ""), "via": m.get("via") or ("host list" if p else ""),
                     "added": m.get("added"), "state": state(email, p),
                     "first_seen": p["first"].isoformat() if p else None, "last_seen": p["last"].isoformat() if p else None,
                     "last_session": p["last_start"].isoformat() if p and p["last_start"] else None,
                     "days_since_session": (now - p["last_start"]).days if p and p["last_start"] else None,
                     "sessions": p["starts"] if p else 0, "sessions_7": week.get(email, 0), "tools_used": len(p["skills"]) if p else 0, "top_tool": top,
                     "active_days_30": len([d for d in p["days"] if (now.date() - d).days < 30]) if p else 0})
    order = {"connected_not_started": 0, "gone_quiet": 1, "quiet": 2, "not_connected": 3, "active": 4, "stopped": 5}
    rows.sort(key=lambda r: (order[r["state"]], -(r["days_since_session"] or 0), r["email"]))

    tools = {s["skill"]: {"skill": s["skill"], "starts": 0, "members": set(), "last": None, "starts_30": 0, "starts_7": 0} for s in skills}
    for at, r in recs:
        if r.get("outcome") == "ok" and r.get("tool") == START and r.get("skill") in tools:
            t = tools[r["skill"]]
            t["starts"] += 1
            t["members"].add(r["member"])
            t["last"] = at
            if (now - at).days < 30:
                t["starts_30"] += 1
            if (now - at).days < 7:
                t["starts_7"] += 1
    tool_rows = sorted(({"skill": t["skill"], "starts": t["starts"], "starts_30": t["starts_30"], "starts_7": t["starts_7"], "members": len(t["members"]),
                         "last": t["last"].isoformat() if t["last"] else None} for t in tools.values()), key=lambda t: (-t["starts"], t["skill"]))

    days = [(now.date() - timedelta(days=i)) for i in range(29, -1, -1)]
    by_day = {d: {"members": set(), "sessions": 0} for d in days}
    for at, r in recs:
        if r.get("outcome") == "ok" and at.date() in by_day:
            by_day[at.date()]["members"].add(r["member"])
            if r.get("tool") == START:
                by_day[at.date()]["sessions"] += 1
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    refused = sum(1 for _at, r in recs if r.get("outcome") not in ("ok",) and (now - _at).days < 30)
    return {"now": now.isoformat(timespec="seconds"), "tracking_since": since.isoformat() if since else None,
            "counts": counts, "members": rows, "tools": tool_rows, "refused_30": refused,
            "daily": [{"date": d.isoformat(), "members": len(by_day[d]["members"]), "sessions": by_day[d]["sessions"]} for d in days],
            "thresholds": {"active_days": ACTIVE_DAYS, "quiet_days": QUIET_DAYS}}


NOTES = {
    "connected_not_started": "You are connected to Build Room OS, which is the hard part. The first thing to say to Claude is: I'm new here. Help me get started. "
                             "It takes about ten minutes. Want to do it together on a quick call?",
    "gone_quiet": "I noticed it has been a few weeks since your last Build Room session. What got in the way? Reply with one line and I will point you to the one session worth doing next.",
    "quiet": "It has been a little while since your last session. If you are not sure what to do next, say this to Claude: What should I work on next?",
    "not_connected": "Your Build Room OS link is ready and has not been used yet. Setup takes about five minutes, step by step, here: https://guide.aimomentumlabs.com/start",
}


def digest(summary, pending=0):
    """The week in plain text, for the host. Names and email addresses only: nothing a member typed is in the log."""
    def days_ago(iso):
        d = _when(iso) if iso else None
        return (_when(summary["now"]) - d).days if d else None

    def who(r):
        return (r["name"] + " " if r["name"] else "") + f"<{r['email']}>"

    rows = summary["members"]
    c = summary["counts"]
    live = [r for r in rows if r["state"] != "stopped"]
    this_week = [r for r in live if r["sessions_7"]]
    first_timers = [r for r in live if r["sessions"] and r["sessions"] == r["sessions_7"]]
    new = [r for r in live if r["first_seen"] and days_ago(r["first_seen"]) is not None and days_ago(r["first_seen"]) < 7]
    out = [f"Build Room OS: your week, as of {summary['now'][:10]}", ""]
    if not summary["tracking_since"]:
        out += ["No activity has been recorded yet. Counting starts with the first session a member runs after the dashboard went live.", ""]
    else:
        tracked = days_ago(summary["tracking_since"])
        if tracked is not None and tracked < 7:
            out += [f"Activity has only been counted for {tracked + 1} day(s), since {summary['tracking_since'][:10]}, so this is a partial week.", ""]
    out += ["THE WEEK IN NUMBERS",
            f"- {len(this_week)} of {len(live)} members ran at least one session ({sum(r['sessions_7'] for r in live)} sessions in all)",
            f"- {len(new)} connected for the first time",
            f"- {len(first_timers)} ran their first session ever",
            f"- {pending} sign-up request(s) waiting for your decision" if pending else "- No sign-up requests waiting",
            ""]
    used = [t for t in summary["tools"] if t["starts_7"]]
    if used:
        out += ["MOST USED THIS WEEK"] + [f"- {t['skill'].replace('buildroom-', '')}: {t['starts_7']}" for t in sorted(used, key=lambda t: -t["starts_7"])[:5]] + [""]
    for state, title, detail in (
            ("connected_not_started", "CONNECTED BUT NEVER RAN A SESSION", lambda r: f"connected {days_ago(r['first_seen'])} day(s) ago"),
            ("gone_quiet", f"GONE QUIET (no session in over {QUIET_DAYS} days)", lambda r: f"last session {r['days_since_session']} days ago"),
            ("quiet", f"SLOWING DOWN (no session in over {ACTIVE_DAYS} days)", lambda r: f"last session {r['days_since_session']} days ago"),
            ("not_connected", "HAVE A LINK, NEVER CONNECTED", lambda r: "no activity recorded")):
        group = [r for r in rows if r["state"] == state]
        if not group:
            continue
        out += [f"{title}: {len(group)}"] + [f"- {who(r)}, {detail(r)}" for r in group[:25]]
        if len(group) > 25:
            out.append(f"- and {len(group) - 25} more, on the dashboard")
        out += ["A note you could send: " + NOTES[state], ""]
    if first_timers:
        out += ["WORTH A CONGRATULATIONS: ran their first session this week"] + [f"- {who(r)}" for r in first_timers[:25]] + [""]
    ins = summary.get("insights") or {}
    stuck = [t for t in ins.get("tools", []) if t["stopped"]][:3]
    if stuck:
        out += [f"WHERE SESSIONS STOP (last {ins['window_days']} days)"]
        out += [f"- {t['skill'].replace('buildroom-', '')}: stopped {t['stopped']} time(s)" + (", most often at " + t["stopped_at"][0][0] if t["stopped_at"] else "") for t in stuck] + [""]
    if ins.get("caught"):
        out += ["WHAT THE CHECKS KEEP CATCHING"] + [f"- {c['skill'].replace('buildroom-', '')}: {c['kind']} ({c['count']})" for c in ins["caught"][:5]] + [""]
    if ins.get("shared"):
        out += [f"RESULTS MEMBERS CHOSE TO SHARE ({ins['sharing_on']} sharing)"]
        out += [f"- {x['what']}: middle {x['middle']:g}, from {x['members']} member(s)" for x in ins["shared"][:8]] + [""]
    out += ["Everything above counts sessions started, not results, apart from the results members chose to share. Nothing a member typed is recorded.",
            "Full dashboard: https://guide.aimomentumlabs.com/admin/dashboard"]
    subject = f"Build Room OS weekly: {len(this_week)} active, {c.get('connected_not_started', 0) + c.get('gone_quiet', 0)} to check in on"
    return {"subject": subject, "text": "\n".join(out)}
