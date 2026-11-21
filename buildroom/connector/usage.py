"""Usage summary for the host dashboard.

The connector writes one line per tool call: when, which member, which tool, which session, and whether it
worked. Nothing a member typed and nothing from their Business File is ever recorded. This module turns
those lines into what the host needs: who is active, who connected but never started, who has gone quiet,
and which sessions are used.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ACTIVE_DAYS, QUIET_DAYS = 7, 21
START = "buildroom_start_session"
MAX_LOG_BYTES = 25_000_000


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
    out += ["Everything above counts sessions started, not results. Nothing a member typed is recorded.", "Full dashboard: https://guide.aimomentumlabs.com/admin/dashboard"]
    subject = f"Build Room OS weekly: {len(this_week)} active, {c.get('connected_not_started', 0) + c.get('gone_quiet', 0)} to check in on"
    return {"subject": subject, "text": "\n".join(out)}
