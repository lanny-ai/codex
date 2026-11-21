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

    rows = []
    for email in sorted(set(known) | set(per)):
        m, p = known.get(email, {}), per.get(email)
        top = max(p["skills"].items(), key=lambda kv: kv[1])[0] if p and p["skills"] else None
        rows.append({"email": email, "name": m.get("name") or "", "status": m.get("status") or ("active" if p else ""), "via": m.get("via") or ("host list" if p else ""),
                     "added": m.get("added"), "state": state(email, p),
                     "first_seen": p["first"].isoformat() if p else None, "last_seen": p["last"].isoformat() if p else None,
                     "last_session": p["last_start"].isoformat() if p and p["last_start"] else None,
                     "days_since_session": (now - p["last_start"]).days if p and p["last_start"] else None,
                     "sessions": p["starts"] if p else 0, "tools_used": len(p["skills"]) if p else 0, "top_tool": top,
                     "active_days_30": len([d for d in p["days"] if (now.date() - d).days < 30]) if p else 0})
    order = {"connected_not_started": 0, "gone_quiet": 1, "quiet": 2, "not_connected": 3, "active": 4, "stopped": 5}
    rows.sort(key=lambda r: (order[r["state"]], -(r["days_since_session"] or 0), r["email"]))

    tools = {s["skill"]: {"skill": s["skill"], "starts": 0, "members": set(), "last": None, "starts_30": 0} for s in skills}
    for at, r in recs:
        if r.get("outcome") == "ok" and r.get("tool") == START and r.get("skill") in tools:
            t = tools[r["skill"]]
            t["starts"] += 1
            t["members"].add(r["member"])
            t["last"] = at
            if (now - at).days < 30:
                t["starts_30"] += 1
    tool_rows = sorted(({"skill": t["skill"], "starts": t["starts"], "starts_30": t["starts_30"], "members": len(t["members"]),
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
