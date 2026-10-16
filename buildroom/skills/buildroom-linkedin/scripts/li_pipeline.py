#!/usr/bin/env python3
"""LinkedIn Engine pipeline: the member's own log of warm signals, messages and calls.

Local only. It never contacts LinkedIn, never sends anything, and stores only what the member
typed: name, LinkedIn URL, role and company as shown, the signal, notes, stage, dates. The member
does every action on LinkedIn by hand and tells this log what they did.

Usage (P = linkedin/pipeline.json; created on first use)
  li_pipeline.py add    P --name "Dana Ruiz" --url https://www.linkedin.com/in/danaruiz --role "COO" --company "Ruiz & Co"
                          --signal sig:commented-my-post --fit A [--link URL] [--note "..."] [--date YYYY-MM-DD]
  li_pipeline.py touch  P <id> --template D1 [--text "the message as sent"] [--note "..."] [--date ...]
                          C1 blank request · C2 request with note · C3 welcome · D1–D4 first DM · D5 call ask
                          D6 deepening · F1/F2 follow-ups · V1 voice note
  li_pipeline.py move   P <id> <stage> [--note "..."] [--value 12000] [--date ...]
  li_pipeline.py log-post P --url <post link> --pillar "Cash flow" --format image|carousel|text|video|poll [--date]
  li_pipeline.py log-comments P <n> [--date]          comments the member wrote on others' posts today
  li_pipeline.py today  P [--date]                    the daily list: follow-ups due, signals waiting, pace
  li_pipeline.py due    P [--retention] [--date]      follow-ups due (and records past their retention date)
  li_pipeline.py pace   P [--date]                    invitations this week, notes this month, warnings
  li_pipeline.py forget P <id>                        objection: delete the record, keep a suppression line
  li_pipeline.py week   P [--from YYYY-MM-DD]         counts for the weekly scorecard (JSON)
  li_pipeline.py import-connections P Connections.csv the member's own 1st-degree export: marks who is connected
  li_pipeline.py ghl-build P                          tags, fields and pipeline for ghl_push.py (JSON to stdout)
  li_pipeline.py list   P [--stage S]
  li_pipeline.py settings P [--premium yes|no] [--notes-limit N]

Standard library only. Exit code 2 on a refused action (suppressed person, unknown id, bad stage).
"""
import argparse, csv, datetime as dt, hashlib, json, os, re, sys, tempfile
from pathlib import Path

SCHEMA = "buildroom-linkedin/1"
STAGES = ["signal", "warming", "connected", "conversation", "qualified", "call-offered", "call-booked",
          "call-held", "proposal", "won", "lost", "nurture"]
SIGNALS = ["sig:commented-my-post", "sig:commented-peer-post", "sig:viewed-profile", "sig:new-role",
           "sig:posted-problem", "sig:inbound-connect", "sig:dm-inbound", "sig:event", "sig:referral"]
TEMPLATES = {"C1": "connection request (blank)", "C2": "connection request with note", "C3": "welcome after accepting",
             "D1": "first DM: commented on my post", "D2": "first DM: resource offer", "D3": "first DM: trigger event",
             "D4": "first DM: profile viewer", "D5": "call ask", "D6": "deepening question",
             "F1": "follow-up 1 (add value)", "F2": "follow-up 2 (permission to close)", "V1": "voice note"}
FIRST_DM = {"D1", "D2", "D3", "D4", "C3"}
INVITES = {"C1", "C2"}
FORMATS = ["text", "image", "carousel", "video", "poll", "newsletter", "article"]
# follow-up rhythm (days): after a first DM or the call ask, F1 in 4 days; after F1, F2 in 5 more; after F2, stop.
NEXT_AFTER = {"first": ("F1", 4), "F1": ("F2", 5), "F2": (None, 0), "invite": ("check accept / withdraw if pending", 21)}
RETENTION_DAYS = 365
WARN = {"invites_day": 20, "invites_week": 80, "notes_month_free": 5, "dms_session": 15}


def today(a=None):
    d = getattr(a, "date", None) if a else None
    return dt.date.fromisoformat(d) if d else dt.date.today()


def norm_url(u):
    u = (u or "").strip().lower().split("?")[0].rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", u)


def url_hash(u):
    return hashlib.sha256(norm_url(u).encode()).hexdigest()[:24]


def load(path):
    p = Path(path)
    if not p.exists():
        return {"schema": SCHEMA, "created": dt.date.today().isoformat(), "settings": {"premium": False, "notes_limit": WARN["notes_month_free"]},
                "basis": "legitimate interest: professional contact about services the person's public role suggests they may need; "
                         "only what they shared with me; deleted on request or after 12 months without interaction",
                "people": [], "suppressed": [], "posts": [], "comments": [], "next_id": 1}
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise SystemExit(f"{path} is not a LinkedIn Engine pipeline file")
    return data


def save(path, data):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".pipeline-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


def find(data, pid):
    for x in data["people"]:
        if str(x["id"]) == str(pid):
            return x
    refuse(f"no record {pid}")


def plus(d, n):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


def schedule(person, template, on):
    if template in INVITES:
        nxt, days = NEXT_AFTER["invite"]
    elif template in FIRST_DM or template == "D5":
        nxt, days = NEXT_AFTER["first"]
    elif template in ("F1", "F2"):
        nxt, days = NEXT_AFTER[template]
    else:
        return
    person["next_action"] = nxt
    person["next_date"] = plus(on, days) if nxt else None


# ---------------- commands ----------------

def cmd_add(data, a):
    if not a.url:
        refuse("a LinkedIn URL is needed (the member's own copy of it)")
    if url_hash(a.url) in {s["hash"] for s in data["suppressed"]}:
        refuse("this person asked not to be contacted; the record is suppressed")
    if any(norm_url(x["url"]) == norm_url(a.url) for x in data["people"]):
        refuse("already in the pipeline; use touch or move")
    if a.signal not in SIGNALS:
        refuse(f"signal must be one of {SIGNALS} (no signal, no DM: comment on their posts first)")
    on = today(a).isoformat()
    rec = {"id": data["next_id"], "name": a.name, "url": a.url.strip(), "role": a.role or "", "company": a.company or "",
           "signal": a.signal, "signal_link": a.link or "", "signal_date": on, "fit": a.fit, "stage": "signal",
           "stage_dates": {"signal": on}, "touches": [], "notes": [a.note] if a.note else [],
           "next_action": "connect or first DM within 48 h", "next_date": plus(on, 2), "last_interaction": on,
           "retention_until": plus(on, RETENTION_DAYS), "value": None}
    data["people"].append(rec); data["next_id"] += 1
    return {"added": rec["id"], "name": rec["name"], "next": rec["next_action"]}


def cmd_touch(data, a):
    p = find(data, a.id)
    t = a.template.upper()
    if t not in TEMPLATES:
        refuse(f"template must be one of {sorted(TEMPLATES)}")
    on = today(a).isoformat()
    warn = []
    if t == "C2" and a.text:
        lim = 300 if data["settings"].get("premium") else 200
        if len(a.text) > lim:
            refuse(f"connection note is {len(a.text)} characters; the limit is {lim}")
    if t in {"D1", "D2", "D3", "D4", "D5", "D6", "F1", "F2", "C3"} and a.text and len(a.text) > 400:
        warn.append(f"message is {len(a.text)} characters; under about 400 gets more replies")
    if t == "D5" and sum(1 for x in p["touches"] if x["template"] in FIRST_DM | {"D6"}) < 1 and p["stage"] not in ("conversation", "qualified"):
        warn.append("call ask before any real exchange: earn it with two or more replies first")
    p["touches"].append({"date": on, "template": t, **({"chars": len(a.text)} if a.text else {}), **({"note": a.note} if a.note else {})})
    p["last_interaction"] = on
    p["retention_until"] = plus(on, RETENTION_DAYS)
    if t in INVITES and STAGES.index(p["stage"]) < STAGES.index("warming"):
        p["stage"] = "warming"; p["stage_dates"]["warming"] = on
    if t == "D5" and STAGES.index(p["stage"]) < STAGES.index("call-offered"):
        p["stage"] = "call-offered"; p["stage_dates"]["call-offered"] = on
    schedule(p, t, on)
    if t == "F2":
        p["next_action"] = "nurture: comment on their posts; re-engage only on a new signal"
        p["next_date"] = None
    if a.note:
        p["notes"].append(a.note)
    return {"logged": t, "id": p["id"], "next": p["next_action"], "on": p["next_date"], **({"warnings": warn} if warn else {})}


def cmd_move(data, a):
    p = find(data, a.id)
    if a.stage not in STAGES:
        refuse(f"stage must be one of {STAGES}")
    on = today(a).isoformat()
    p["stage"] = a.stage; p["stage_dates"][a.stage] = on; p["last_interaction"] = on
    p["retention_until"] = plus(on, RETENTION_DAYS)
    if a.value is not None:
        p["value"] = a.value
    nxt = {"connected": ("first DM if there is a reason (C3/D1–D4)", 2), "conversation": ("learn the problem (D6)", 2),
           "qualified": ("the call ask (D5)", 1), "call-booked": ("prepare for the call", 0), "call-held": ("proposal or close", 2),
           "proposal": ("follow up on the proposal (§16)", 4), "won": (None, 0), "lost": (None, 0),
           "nurture": ("comment on their posts; re-engage on a new signal after 60–90 days", 75)}.get(a.stage)
    if nxt:
        p["next_action"] = nxt[0]; p["next_date"] = plus(on, nxt[1]) if nxt[0] else None
    if a.note:
        p["notes"].append(a.note)
    return {"moved": p["id"], "stage": a.stage, "next": p["next_action"]}


def cmd_log_post(data, a):
    if a.format not in FORMATS:
        refuse(f"format must be one of {FORMATS}")
    data["posts"].append({"date": today(a).isoformat(), "url": a.url or "", "pillar": a.pillar or "", "format": a.format})
    return {"posts_logged": len(data["posts"])}


def cmd_log_comments(data, a):
    data["comments"].append({"date": today(a).isoformat(), "n": int(a.n)})
    return {"comments_today": sum(c["n"] for c in data["comments"] if c["date"] == today(a).isoformat())}


def pace(data, on):
    week_ago = on - dt.timedelta(days=6)
    month = on.strftime("%Y-%m")
    inv_today = inv_week = notes_month = 0
    for p in data["people"]:
        for t in p["touches"]:
            d = dt.date.fromisoformat(t["date"])
            if t["template"] in INVITES:
                inv_week += week_ago <= d <= on
                inv_today += d == on
            if t["template"] == "C2" and t["date"].startswith(month):
                notes_month += 1
    warn = []
    if inv_today > WARN["invites_day"]:
        warn.append(f"{inv_today} connection requests today (keep under {WARN['invites_day']})")
    if inv_week > WARN["invites_week"]:
        warn.append(f"{inv_week} connection requests in 7 days (the reported weekly cap is about 100; stay under {WARN['invites_week']})")
    lim = data["settings"].get("notes_limit", WARN["notes_month_free"])
    if not data["settings"].get("premium") and notes_month > lim:
        warn.append(f"{notes_month} personalised notes this month (free accounts get about {lim}); send blank requests")
    pending = [p for p in data["people"] if p["stage"] == "warming" and any(t["template"] in INVITES for t in p["touches"])
               and (on - dt.date.fromisoformat(max(t["date"] for t in p["touches"] if t["template"] in INVITES))).days >= 21]
    if pending:
        warn.append(f"{len(pending)} invitation(s) pending 3+ weeks: withdraw them (this does not restore quota)")
    return {"invites_today": inv_today, "invites_7d": inv_week, "notes_this_month": notes_month, "warnings": warn}


def cmd_pace(data, a):
    return pace(data, today(a))


def due_list(data, on, retention=False):
    out = [{"id": p["id"], "name": p["name"], "stage": p["stage"], "next": p["next_action"], "date": p["next_date"]}
           for p in data["people"] if p.get("next_date") and dt.date.fromisoformat(p["next_date"]) <= on
           and p["stage"] not in ("won", "lost")]
    res = {"due": sorted(out, key=lambda x: x["date"])}
    if retention:
        res["past_retention"] = [{"id": p["id"], "name": p["name"], "last": p["last_interaction"]} for p in data["people"]
                                 if dt.date.fromisoformat(p["retention_until"]) <= on and p["stage"] not in ("won",)]
    return res


def cmd_due(data, a):
    return due_list(data, today(a), a.retention)


def cmd_today(data, a):
    on = today(a)
    d = due_list(data, on, retention=True)
    waiting = [{"id": p["id"], "name": p["name"], "signal": p["signal"], "since": p["signal_date"]}
               for p in data["people"] if p["stage"] == "signal" and not p["touches"]]
    c_today = sum(c["n"] for c in data["comments"] if c["date"] == on.isoformat())
    return {"date": on.isoformat(),
            "1_comment": f"{c_today} substantive comments logged today; aim for 5–10 on your watch list (tiers A and B)",
            "2_reply": "reply to comments on your own recent posts; open a second exchange with the ones that fit",
            "3_signals_waiting": waiting, "4_follow_ups_due": d["due"], "retention_review": d["past_retention"],
            "pace": pace(data, on)}


def cmd_forget(data, a):
    p = find(data, a.id)
    data["people"] = [x for x in data["people"] if x is not p]
    data["suppressed"].append({"hash": url_hash(p["url"]), "date": dt.date.today().isoformat()})
    return {"forgotten": a.id, "note": "record deleted; a one-way suppression hash is kept so they are never re-added"}


def week_counts(data, start):
    end = start + dt.timedelta(days=7)
    inside = lambda s: s and start <= dt.date.fromisoformat(s) < end
    c = {"from": start.isoformat(), "to": (end - dt.timedelta(days=1)).isoformat(),
         "posts": sum(1 for x in data["posts"] if inside(x["date"])),
         "posts_by_format": {}, "posts_by_pillar": {},
         "comments": sum(x["n"] for x in data["comments"] if inside(x["date"])),
         "invites": 0, "notes": 0, "accepted": 0, "dms_started": 0, "follow_ups": 0, "call_asks": 0,
         "replies": 0, "qualified": 0, "calls_booked": 0, "calls_held": 0, "proposals": 0, "won": 0, "won_value": 0,
         "signals": 0, "signals_by_type": {}}
    for x in data["posts"]:
        if inside(x["date"]):
            c["posts_by_format"][x["format"]] = c["posts_by_format"].get(x["format"], 0) + 1
            if x["pillar"]:
                c["posts_by_pillar"][x["pillar"]] = c["posts_by_pillar"].get(x["pillar"], 0) + 1
    for p in data["people"]:
        if inside(p["signal_date"]):
            c["signals"] += 1; c["signals_by_type"][p["signal"]] = c["signals_by_type"].get(p["signal"], 0) + 1
        for t in p["touches"]:
            if not inside(t["date"]):
                continue
            k = t["template"]
            c["invites"] += k in INVITES; c["notes"] += k == "C2"; c["dms_started"] += k in FIRST_DM
            c["follow_ups"] += k in ("F1", "F2"); c["call_asks"] += k == "D5"
        sd = p["stage_dates"]
        c["accepted"] += bool(inside(sd.get("connected")))
        c["replies"] += bool(inside(sd.get("conversation")))
        c["qualified"] += bool(inside(sd.get("qualified")))
        c["calls_booked"] += bool(inside(sd.get("call-booked")))
        c["calls_held"] += bool(inside(sd.get("call-held")))
        c["proposals"] += bool(inside(sd.get("proposal")))
        if inside(sd.get("won")):
            c["won"] += 1; c["won_value"] += p.get("value") or 0
    c["acceptance_rate"] = round(c["accepted"] / c["invites"], 3) if c["invites"] else None
    c["reply_rate"] = round(c["replies"] / c["dms_started"], 3) if c["dms_started"] else None
    return c


def cmd_week(data, a):
    if a.start:
        start = dt.date.fromisoformat(a.start)
    else:
        t = today(a); start = t - dt.timedelta(days=t.weekday())
    return week_counts(data, start)


def read_connections_csv(path):
    """LinkedIn's Connections.csv starts with a few 'Notes:' lines before the header row."""
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    for i, line in enumerate(lines):
        if re.match(r"\s*\"?first name\"?\s*,", line, re.I):
            return list(csv.DictReader(lines[i:]))
    raise SystemExit("no header row (First Name, Last Name, URL, ...) found in the connections file")


def cmd_import_connections(data, a):
    rows = read_connections_csv(a.csv)
    by_url = {norm_url(r.get("URL") or r.get("Url") or ""): r for r in rows}
    marked = []
    for p in data["people"]:
        r = by_url.get(norm_url(p["url"]))
        if r and STAGES.index(p["stage"]) < STAGES.index("connected"):
            on = today(a).isoformat()
            raw = (r.get("Connected On") or "").strip()
            for fmt in ("%d %b %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    on = dt.datetime.strptime(raw, fmt).date().isoformat(); break
                except ValueError:
                    pass
            p["stage"] = "connected"; p["stage_dates"]["connected"] = on; p["last_interaction"] = on
            p["next_action"] = "first DM if there is a reason (C3/D1–D4)"; p["next_date"] = plus(on, 2)
            marked.append(p["id"])
    return {"connections_in_file": len(rows), "pipeline_records_now_connected": marked,
            "note": "only people already in the pipeline were updated; the rest of the export is not stored"}


def cmd_ghl_build(data, a):
    return {"funnel": "LinkedIn Organic",
            "tags": ["src:linkedin-organic", *SIGNALS, "fit:A", "fit:B", "fit:C", "msg:d1", "msg:fu1", "msg:fu2", "nurture-90d"],
            "custom_fields": [{"name": "LinkedIn URL", "dataType": "TEXT"}, {"name": "First LinkedIn signal", "dataType": "DATE"},
                              {"name": "LinkedIn signal link", "dataType": "TEXT"}, {"name": "Offer discussed", "dataType": "TEXT"}],
            "pipeline": {"name": "LinkedIn Organic", "stages": ["Conversation", "Qualified", "Call offered", "Call booked",
                                                                "Call held", "Proposal", "Won", "Lost", "Nurture"]},
            "emails": [], "workflows": [],
            "launch_test": ["Add yourself as a test contact with tag src:linkedin-organic",
                            "Move the test contact through every stage of the LinkedIn Organic pipeline",
                            "Delete the test contact"]}


def cmd_list(data, a):
    return [{k: p[k] for k in ("id", "name", "company", "signal", "fit", "stage", "next_action", "next_date")}
            for p in data["people"] if not a.stage or p["stage"] == a.stage]


def cmd_settings(data, a):
    if a.premium:
        data["settings"]["premium"] = a.premium == "yes"
    if a.notes_limit is not None:
        data["settings"]["notes_limit"] = a.notes_limit
    return data["settings"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def mk(name, *extra):
        s = sub.add_parser(name); s.add_argument("path"); s.add_argument("--date"); return s
    s = mk("add")
    for f in ("name", "url", "signal"):
        s.add_argument("--" + f, required=True)
    s.add_argument("--role"); s.add_argument("--company"); s.add_argument("--link"); s.add_argument("--note")
    s.add_argument("--fit", choices=["A", "B", "C"], default="B")
    s = mk("touch"); s.add_argument("id"); s.add_argument("--template", required=True); s.add_argument("--text"); s.add_argument("--note")
    s = mk("move"); s.add_argument("id"); s.add_argument("stage"); s.add_argument("--note"); s.add_argument("--value", type=float)
    s = mk("log-post"); s.add_argument("--url"); s.add_argument("--pillar"); s.add_argument("--format", required=True)
    s = mk("log-comments"); s.add_argument("n", type=int)
    mk("today"); s = mk("due"); s.add_argument("--retention", action="store_true"); mk("pace")
    s = mk("forget"); s.add_argument("id")
    s = mk("week"); s.add_argument("--from", dest="start")
    s = mk("import-connections"); s.add_argument("csv")
    mk("ghl-build")
    s = mk("list"); s.add_argument("--stage")
    s = mk("settings"); s.add_argument("--premium", choices=["yes", "no"]); s.add_argument("--notes-limit", type=int)
    a = ap.parse_args(argv)
    data = load(a.path)
    fn = {"add": cmd_add, "touch": cmd_touch, "move": cmd_move, "log-post": cmd_log_post, "log-comments": cmd_log_comments,
          "today": cmd_today, "due": cmd_due, "pace": cmd_pace, "forget": cmd_forget, "week": cmd_week,
          "import-connections": cmd_import_connections, "ghl-build": cmd_ghl_build, "list": cmd_list,
          "settings": cmd_settings}[a.cmd]
    out = fn(data, a)
    if a.cmd not in ("today", "due", "pace", "week", "ghl-build", "list"):
        save(a.path, data)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
