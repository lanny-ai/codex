#!/usr/bin/env python3
"""LinkedIn Engine pipeline: the member's own log of warm signals, messages and calls.

Local only. It never contacts LinkedIn, never sends anything, and stores only what the member
typed: name, LinkedIn URL, role and company as shown, the signal, notes, stage, dates. The member
does every action on LinkedIn by hand and tells this log what they did.

Usage
  P is the pipeline file. It is optional everywhere: the default is linkedin/pipeline.json in the
  current folder. Pass it right after the command (li_pipeline.py today linkedin/pipeline.json) or as
  --file P. Only settings (or init) creates the file; every other command refuses when it is missing.

  li_pipeline.py settings [P] [--premium yes|no] [--notes-limit N] [--pillars "Cash flow" "Pricing" ...] [--basis "..."]
                          creates the pipeline on first use and prints the lawful basis it records (edit with --basis)
  li_pipeline.py init     [P] [same options as settings]
  li_pipeline.py add    [P] --name "Dana Ruiz" --url https://www.linkedin.com/in/danaruiz --role "COO" --company "Ruiz & Co"
                          --signal sig:commented-my-post --fit A [--link URL] [--note "..."] [--date YYYY-MM-DD]
                          signals: sig:commented-my-post sig:commented-peer-post sig:viewed-profile sig:new-role
                          sig:posted-problem sig:inbound-connect sig:dm-inbound sig:event sig:referral sig:launch
  li_pipeline.py touch  [P] <id> --template D1 [--text "the message as sent"] [--note "..."] [--force-stage] [--date ...]
                          logs a message the member sent and schedules the next step.
                          C1 blank request · C2 request with note · C3 welcome · D1–D4 first DM · D5 call ask
                          D6 deepening · F1/F2 follow-ups · V1 voice note
                          --text is what the length checks read: a C2 note over 200 characters (300 on Premium) is
                          refused, and a DM over 400 is warned. Without --text there is no length check.
                          A D5 before they have replied is logged with a warning and does not move them to
                          call-offered (--force-stage moves them anyway).
  li_pipeline.py reply  [P] <id> [--note "..."] [--date ...]
                          they replied: logs the reply (two or more make a real conversation) and moves a
                          record that has not replied before to conversation
  li_pipeline.py move   [P] <id> <stage> [--note "..."] [--value 12000] [--date ...]
                          stages: signal warming connected conversation qualified call-offered call-booked
                          call-held proposal won lost nurture (each sets its own next action)
  li_pipeline.py log-post [P] --url <post link> --pillar "Cash flow" --format image|carousel|text|video|poll [--date]
                          --pillar must be one of the pillars stored with settings --pillars
  li_pipeline.py log-comments [P] <n> [--date]        comments the member wrote on others' posts today
  li_pipeline.py today  [P] [--date]                  the daily list: follow-ups due, signals waiting, pace
  li_pipeline.py due    [P] [--retention] [--date]    follow-ups due (and records past their retention date)
  li_pipeline.py pace   [P] [--date]                  invitations this week, notes this month, warnings
  li_pipeline.py forget [P] <id> [--date]             objection: delete the record, keep a suppression line
  li_pipeline.py week   [P] [--from YYYY-MM-DD] [--date]  counts for the weekly scorecard (JSON); default: the last
                          complete Monday–Sunday week before today (or before --date), the same as li_scorecard.py
  li_pipeline.py import-connections [P] Connections.csv  the member's own 1st-degree export: marks who is connected
  li_pipeline.py ghl-build [P] [--pipeline existing|separate] [--pipeline-name "Sales Pipeline"] [--stages "New Lead" ...]
                          [--tag-style hyphen|colon] [--source-tag src-linkedin]
                          tags, fields and pipeline for ghl_push.py (JSON to stdout; nothing is sent)
  li_pipeline.py list   [P] [--stage S]

Standard library only. Exit code 2 on a refused action (missing pipeline file, suppressed person,
unknown id, bad stage, unknown pillar).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, csv, datetime as dt, hashlib, json, os, re, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

SCHEMA = "buildroom-linkedin/1"
DEFAULT_PATH = "linkedin/pipeline.json"
STAGES = ["signal", "warming", "connected", "conversation", "qualified", "call-offered", "call-booked",
          "call-held", "proposal", "won", "lost", "nurture"]
SIGNALS = ["sig:commented-my-post", "sig:commented-peer-post", "sig:viewed-profile", "sig:new-role",
           "sig:posted-problem", "sig:inbound-connect", "sig:dm-inbound", "sig:event", "sig:referral", "sig:launch"]
TEMPLATES = {"C1": "connection request (blank)", "C2": "connection request with note", "C3": "welcome after accepting",
             "D1": "first DM: commented on my post", "D2": "first DM: resource offer", "D3": "first DM: trigger event",
             "D4": "first DM: profile viewer", "D5": "call ask", "D6": "deepening question",
             "F1": "follow-up 1 (add value)", "F2": "follow-up 2 (permission to close)", "V1": "voice note"}
FIRST_DM = {"D1", "D2", "D3", "D4", "C3"}
INVITES = {"C1", "C2"}
DIRECT = {"C3", "D1", "D2", "D3", "D4", "D5", "D6", "F1", "F2", "V1"}   # messages that need a connection (or InMail)
FORMATS = ["text", "image", "carousel", "video", "poll", "newsletter", "article"]
# follow-up rhythm (days): after a first DM or the call ask, F1 in 4 days; after F1, F2 in 5 more; after F2, stop.
NEXT_AFTER = {"first": ("F1", 4), "F1": ("F2", 5), "F2": (None, 0), "invite": ("check accept / withdraw if pending", 21),
              "sent": ("wait for reply; F1 if silent", 4)}
# the next action each stage sets when a record enters it (every stage has one; None clears it)
STAGE_NEXT = {"signal": ("connect or first DM within 48 h", 2), "warming": ("check accept / withdraw if pending", 21),
              "connected": ("first DM if there is a reason (C3/D1–D4)", 2), "conversation": ("learn the problem (D6)", 2),
              "qualified": ("the call ask (D5)", 1), "call-offered": ("F1 if no answer", 4),
              "call-booked": ("prepare for the call", 0), "call-held": ("proposal or close", 2),
              "proposal": ("follow up on the proposal (§16)", 4), "won": (None, 0), "lost": (None, 0),
              "nurture": ("comment on their posts; re-engage on a new signal after 60–90 days", 75)}
assert set(STAGE_NEXT) == set(STAGES)
RETENTION_DAYS = 365
# notes_month_free: LinkedIn's Help page says 5 (possibly stale); members in 2026 report 3, so the guard uses 3.
WARN = {"invites_day": 20, "invites_week": 80, "notes_month_free": 3, "dms_session": 15}
BASIS = ("legitimate interest: professional contact about services the person's public role suggests they may need; "
         "only what they shared with me; deleted on request or after 12 months without interaction")
BASIS_NOTE = ("This is the lawful basis recorded for everyone in this log. Read it once; if it does not describe how you "
              "work, change it with: li_pipeline.py settings --basis \"...\"")
GENERIC_STAGES = ["New Lead", "Call Booked", "Showed", "Committed", "Paid"]   # the Build Room CRM pipeline (Decision Machine)
SEPARATE_STAGES = ["Conversation", "Qualified", "Call offered", "Call booked", "Call held", "Proposal", "Won", "Lost", "Nurture"]


def today(a=None):
    d = getattr(a, "date", None) if a else None
    return dt.date.fromisoformat(d) if d else dt.date.today()


def last_full_week(on):
    """Monday of the last complete Monday–Sunday week before `on` (shared with li_scorecard.py)."""
    return on - dt.timedelta(days=on.weekday() + 7)


def norm_url(u):
    u = (u or "").strip().lower().split("?")[0].rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", u)


def url_hash(u):
    return hashlib.sha256(norm_url(u).encode()).hexdigest()[:24]


def new_pipeline(on=None):
    return {"schema": SCHEMA, "created": (on or dt.date.today()).isoformat(),
            "settings": {"premium": False, "notes_limit": WARN["notes_month_free"], "pillars": []},
            "basis": BASIS, "people": [], "suppressed": [], "posts": [], "comments": [], "next_id": 1}


def load(path, create=False, on=None):
    """The pipeline at `path`. A missing file raises FileNotFoundError unless create=True."""
    p = Path(path)
    if not p.exists():
        if create:
            return new_pipeline(on)
        raise FileNotFoundError(str(path))
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


def before(stage, other):
    return STAGES.index(stage) < STAGES.index(other)


def reached(p, stage):
    """True when the record has entered `stage` or any later stage of the main path (lost and nurture excluded)."""
    i = STAGES.index(stage)
    return any(k in STAGES and STAGES.index(k) >= i and k not in ("lost", "nurture") for k in p["stage_dates"])


def replies_of(p):
    """Dates of their replies. Older records without a reply log count entering conversation as one reply."""
    if "replies" in p:
        return list(p["replies"])
    c = p["stage_dates"].get("conversation")
    return [c] if c else []


def set_next(p, stage, on):
    nxt, days = STAGE_NEXT[stage]
    p["next_action"] = nxt
    p["next_date"] = plus(on, days) if nxt else None


def enter(p, stage, on):
    p["stage"] = stage; p["stage_dates"][stage] = on
    set_next(p, stage, on)


def schedule(person, template, on):
    if template in INVITES:
        nxt, days = NEXT_AFTER["invite"]
    elif template in FIRST_DM or template == "D5":
        nxt, days = NEXT_AFTER["first"]
    elif template in ("F1", "F2"):
        nxt, days = NEXT_AFTER[template]
    else:  # D6, V1 and any other message sent: the task is done; wait for their reply
        nxt, days = NEXT_AFTER["sent"]
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
    first = data["next_id"] == 1 and not data["people"]
    rec = {"id": data["next_id"], "name": a.name, "url": a.url.strip(), "role": a.role or "", "company": a.company or "",
           "signal": a.signal, "signal_link": a.link or "", "signal_date": on, "fit": a.fit, "stage": "signal",
           "stage_dates": {"signal": on}, "touches": [], "replies": [], "notes": [a.note] if a.note else [],
           "next_action": None, "next_date": None, "last_interaction": on,
           "retention_until": plus(on, RETENTION_DAYS), "value": None}
    set_next(rec, "signal", on)
    data["people"].append(rec); data["next_id"] += 1
    out = {"added": rec["id"], "name": rec["name"], "next": rec["next_action"]}
    if first:
        out.update({"lawful_basis": data.get("basis", BASIS), "note": BASIS_NOTE})
    return out


def limit_warnings(data, on):
    return pace(data, on, pending=False)["warnings"]


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
    if t in DIRECT and a.text and len(a.text) > 400:
        warn.append(f"message is {len(a.text)} characters; under about 400 gets more replies")
    if t in DIRECT and before(p["stage"], "connected") and p.get("signal") != "sig:dm-inbound":
        warn.append(f"not connected (stage {p['stage']}): this message needs a connection first, or InMail; "
                    "send a connection request (C1/C2) and wait for the accept")
    early_ask = t == "D5" and before(p["stage"], "conversation")
    if early_ask:
        warn.append("call ask before they have replied: earn it with two or more real exchanges first"
                    + ("" if a.force_stage else f"; logged, stage left at {p['stage']}"))
    p["touches"].append({"date": on, "template": t, **({"chars": len(a.text)} if a.text else {}), **({"note": a.note} if a.note else {})})
    p["last_interaction"] = on
    p["retention_until"] = plus(on, RETENTION_DAYS)
    if t in INVITES and before(p["stage"], "warming"):
        p["stage"] = "warming"; p["stage_dates"]["warming"] = on
    if t == "D5" and before(p["stage"], "call-offered") and (not early_ask or a.force_stage):
        p["stage"] = "call-offered"; p["stage_dates"]["call-offered"] = on
    schedule(p, t, on)
    if t == "F2":
        p["next_action"] = "nurture: comment on their posts; re-engage only on a new signal"
        p["next_date"] = None
    if a.note:
        p["notes"].append(a.note)
    if t in INVITES:
        warn += limit_warnings(data, dt.date.fromisoformat(on))
    return {"logged": t, "id": p["id"], "stage": p["stage"], "next": p["next_action"], "on": p["next_date"],
            **({"warnings": warn} if warn else {})}


def cmd_reply(data, a):
    p = find(data, a.id)
    on = today(a).isoformat()
    p["replies"] = replies_of(p) + [on]
    p["last_interaction"] = on
    p["retention_until"] = plus(on, RETENTION_DAYS)
    if before(p["stage"], "conversation") or p["stage"] in ("nurture", "lost"):
        enter(p, "conversation", on)
    else:
        hint = {"conversation": "D6, or move to qualified once problem, fit and timing are clear",
                "qualified": "the call ask (D5)", "call-offered": "book the call (move to call-booked) or answer their question"
                }.get(p["stage"], STAGE_NEXT[p["stage"]][0] or "reply")
        p["next_action"] = f"answer their reply: {hint}"; p["next_date"] = plus(on, 1)
    if a.note:
        p["notes"].append(a.note)
    n = len(p["replies"])
    return {"reply_logged": p["id"], "replies": n, "real_conversation": n >= 2, "stage": p["stage"], "next": p["next_action"]}


def cmd_move(data, a):
    p = find(data, a.id)
    if a.stage not in STAGES:
        refuse(f"stage must be one of {STAGES}")
    on = today(a).isoformat()
    if a.stage == "conversation":   # they replied: that reply counts once
        rs = replies_of(p)
        if on not in rs:
            p["replies"] = rs + [on]
    enter(p, a.stage, on)
    p["last_interaction"] = on
    p["retention_until"] = plus(on, RETENTION_DAYS)
    if a.value is not None:
        p["value"] = a.value
    if a.note:
        p["notes"].append(a.note)
    return {"moved": p["id"], "stage": a.stage, "next": p["next_action"], "on": p["next_date"]}


def match_pillar(pillars, name):
    key = " ".join((name or "").lower().split())
    return next((x for x in pillars if " ".join(x.lower().split()) == key), None)


def cmd_log_post(data, a):
    if a.format not in FORMATS:
        refuse(f"format must be one of {FORMATS}")
    pillars = data["settings"].get("pillars") or []
    pillar, warn = a.pillar or "", []
    if pillar and pillars:
        found = match_pillar(pillars, pillar)
        if not found:
            refuse(f"unknown pillar {pillar!r}; the pillars stored with settings are {pillars} "
                   "(fix the spelling, or add it: settings --pillars ...)")
        pillar = found
    elif pillar:
        warn.append("no pillars stored yet: set them once (settings --pillars \"...\" \"...\") so a typo cannot split the by-pillar counts")
    data["posts"].append({"date": today(a).isoformat(), "url": a.url or "", "pillar": pillar, "format": a.format})
    return {"posts_logged": len(data["posts"]), **({"pillar": pillar} if pillar else {}), **({"warnings": warn} if warn else {})}


def cmd_log_comments(data, a):
    data["comments"].append({"date": today(a).isoformat(), "n": int(a.n)})
    return {"comments_today": sum(c["n"] for c in data["comments"] if c["date"] == today(a).isoformat())}


def pace(data, on, pending=True):
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
        warn.append(f"{notes_month} personalised notes this month (free accounts get about {lim}; LinkedIn's possibly "
                    "stale Help page says 5); send blank requests (C1)")
    if pending:
        old = [p for p in data["people"] if p["stage"] == "warming" and any(t["template"] in INVITES for t in p["touches"])
               and (on - dt.date.fromisoformat(max(t["date"] for t in p["touches"] if t["template"] in INVITES))).days >= 21]
        if old:
            warn.append(f"{len(old)} invitation(s) pending 3+ weeks: withdraw them (this does not restore quota)")
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
    listed = {w["id"] for w in waiting}
    c_today = sum(c["n"] for c in data["comments"] if c["date"] == on.isoformat())
    return {"date": on.isoformat(),
            "1_comment": f"{c_today} substantive comments logged today; aim for 5–10 on your watch list (tiers A and B)",
            "2_reply": "reply to comments on your own recent posts; open a second exchange with the ones that fit",
            "3_signals_waiting": waiting, "4_follow_ups_due": [x for x in d["due"] if x["id"] not in listed],
            "retention_review": d["past_retention"], "pace": pace(data, on)}


def cmd_forget(data, a):
    p = find(data, a.id)
    data["people"] = [x for x in data["people"] if x is not p]
    data["suppressed"].append({"hash": url_hash(p["url"]), "date": today(a).isoformat()})
    return {"forgotten": a.id, "note": "record deleted; a one-way suppression hash is kept so they are never re-added"}


def week_counts(data, start):
    end = start + dt.timedelta(days=7)
    inside = lambda s: bool(s) and start <= dt.date.fromisoformat(s) < end
    c = {"from": start.isoformat(), "to": (end - dt.timedelta(days=1)).isoformat(),
         "posts": sum(1 for x in data["posts"] if inside(x["date"])),
         "posts_by_format": {}, "posts_by_pillar": {},
         "comments": sum(x["n"] for x in data["comments"] if inside(x["date"])),
         "invites": 0, "notes": 0, "invited": 0, "accepted": 0, "dms_started": 0, "dm_replied": 0, "follow_ups": 0,
         "call_asks": 0, "replies": 0, "conversations": 0, "qualified": 0, "calls_booked": 0, "calls_held": 0,
         "proposals": 0, "won": 0, "won_value": 0, "signals": 0, "signals_by_type": {}}
    for x in data["posts"]:
        if inside(x["date"]):
            c["posts_by_format"][x["format"]] = c["posts_by_format"].get(x["format"], 0) + 1
            if x["pillar"]:
                c["posts_by_pillar"][x["pillar"]] = c["posts_by_pillar"].get(x["pillar"], 0) + 1
    for p in data["people"]:
        if inside(p["signal_date"]):
            c["signals"] += 1; c["signals_by_type"][p["signal"]] = c["signals_by_type"].get(p["signal"], 0) + 1
        invited = dm_on = None
        for t in p["touches"]:
            if not inside(t["date"]):
                continue
            k = t["template"]
            c["invites"] += k in INVITES; c["notes"] += k == "C2"; c["dms_started"] += k in FIRST_DM
            c["follow_ups"] += k in ("F1", "F2"); c["call_asks"] += k == "D5"
            if k in INVITES and invited is None:
                invited = t["date"]
            if k in FIRST_DM and dm_on is None:
                dm_on = t["date"]
        # acceptance: the member's own requests sent this week (a cohort), accepted by any later date; inbound
        # requests the member accepted are not counted, so the rate cannot pass 100%
        if invited and p.get("signal") != "sig:inbound-connect":
            c["invited"] += 1; c["accepted"] += reached(p, "connected")
        rs = replies_of(p)
        if dm_on:
            c["dm_replied"] += any(r >= dm_on for r in rs) or reached(p, "conversation")
        in_week = [r for r in rs if inside(r)]
        c["replies"] += bool(in_week)
        sd = p["stage_dates"]
        # a real conversation: two or more replies from them, at least one this week (or qualified this week)
        c["conversations"] += bool((in_week and sum(1 for r in rs if r < end.isoformat()) >= 2) or inside(sd.get("qualified")))
        c["qualified"] += inside(sd.get("qualified"))
        c["calls_booked"] += inside(sd.get("call-booked"))
        c["calls_held"] += inside(sd.get("call-held"))
        c["proposals"] += inside(sd.get("proposal"))
        if inside(sd.get("won")):
            c["won"] += 1; c["won_value"] += p.get("value") or 0
    c["acceptance_rate"] = round(c["accepted"] / c["invited"], 3) if c["invited"] else None
    c["reply_rate"] = round(c["dm_replied"] / c["dms_started"], 3) if c["dms_started"] else None
    return c


def cmd_week(data, a):
    start = dt.date.fromisoformat(a.start) if a.start else last_full_week(today(a))
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
        if r and before(p["stage"], "connected"):
            on = today(a).isoformat()
            raw = (r.get("Connected On") or "").strip()
            for fmt in ("%d %b %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    on = dt.datetime.strptime(raw, fmt).date().isoformat(); break
                except ValueError:
                    pass
            enter(p, "connected", on); p["last_interaction"] = on
            marked.append(p["id"])
    return {"connections_in_file": len(rows), "pipeline_records_now_connected": marked,
            "note": "only people already in the pipeline were updated; the rest of the export is not stored"}


def tag(name, style):
    """Lower-case kebab-case with a family prefix (the Build Room convention: src-*, status-*), or family:value."""
    fam, _, val = name.lower().replace(":", "-", 1).partition("-")
    return f"{fam}:{val}" if style == "colon" else f"{fam}-{val}"


def map_stages(stages):
    """Each LinkedIn stage from qualified on → a stage of the member's existing pipeline (matched by name)."""
    low = [s.lower() for s in stages]
    pick = lambda *keys: next((stages[i] for i, s in enumerate(low) if any(k in s for k in keys)), None)
    m = {"conversation": "stays in the LinkedIn log until qualified"}
    m["qualified"] = m["call-offered"] = stages[0]
    last = stages[0]
    for li, keys in (("call-booked", ("book",)), ("call-held", ("show", "held", "attend", "complete")),
                     ("proposal", ("proposal", "commit", "offer")), ("won", ("won", "paid", "client", "closed"))):
        last = pick(*keys) or last
        m[li] = last
    m["lost"] = pick("lost") or "mark the opportunity Lost (status, not a stage)"
    m["nurture"] = pick("nurture") or "tag nurture-90d; leave the opportunity open or mark it Abandoned"
    return m


def cmd_ghl_build(data, a):
    style = a.tag_style
    src = (a.source_tag or ("src:linkedin" if style == "colon" else "src-linkedin")).lower()
    tags = [src, *[tag(s, style) for s in SIGNALS], *[tag(f"fit-{x}", style) for x in "abc"],
            *[tag(f"msg-{x}", style) for x in ("d1", "fu1", "fu2")], "nurture-90d"]
    out = {"funnel": "LinkedIn Organic", "tags": list(dict.fromkeys(tags)),
           "custom_fields": [{"name": "LinkedIn URL", "dataType": "TEXT"}, {"name": "First LinkedIn signal", "dataType": "DATE"},
                             {"name": "LinkedIn signal link", "dataType": "TEXT"}, {"name": "Offer discussed", "dataType": "TEXT"}],
           "pipeline_mode": a.pipeline, "emails": [], "workflows": []}
    if a.pipeline == "existing":
        stages = a.stages or GENERIC_STAGES
        name = a.pipeline_name or "Sales Pipeline"
        out["pipeline"] = {"name": name, "stages": stages}
        out["stage_map"] = map_stages(stages)
        out["note"] = (f"LinkedIn leads enter your existing pipeline '{name}' at '{stages[0]}' once qualified, tagged {src}, "
                       "so booked calls and wins stay in the numbers you already track. Pass --pipeline-name and --stages "
                       "with the exact names from Business File §6 (or --pipeline separate for a LinkedIn-only pipeline).")
        test_stages = [out["stage_map"][s] for s in ("qualified", "call-booked", "call-held", "won")]
    else:
        stages = a.stages or SEPARATE_STAGES
        name = a.pipeline_name or "LinkedIn Organic"
        out["pipeline"] = {"name": name, "stages": stages}
        test_stages = stages
    out["launch_test"] = [f"Add yourself as a test contact with tag {src}",
                          f"Move the test contact through {' → '.join(dict.fromkeys(test_stages))} in the {name} pipeline",
                          "Delete the test contact"]
    return out


def cmd_list(data, a):
    return [{k: p.get(k) for k in ("id", "name", "company", "signal", "fit", "stage", "next_action", "next_date")}
            for p in data["people"] if not a.stage or p["stage"] == a.stage]


def cmd_settings(data, a):
    s = data["settings"]
    if a.premium:
        s["premium"] = a.premium == "yes"
    if a.notes_limit is not None:
        s["notes_limit"] = a.notes_limit
    if a.pillars:
        s["pillars"] = [" ".join(x.split()) for x in a.pillars if x.strip()]
    if a.basis:
        data["basis"] = a.basis.strip()
    if getattr(a, "_created", False):
        return {"created": a._path, "settings": s, "lawful_basis": data["basis"], "note": BASIS_NOTE}
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def mk(name):
        s = sub.add_parser(name)
        s.add_argument("path", nargs="?", help=f"the pipeline file (default {DEFAULT_PATH})")
        s.add_argument("--file", help=f"the pipeline file (default {DEFAULT_PATH})")
        s.add_argument("--date"); return s
    s = mk("add")
    for f in ("name", "url", "signal"):
        s.add_argument("--" + f, required=True)
    s.add_argument("--role"); s.add_argument("--company"); s.add_argument("--link"); s.add_argument("--note")
    s.add_argument("--fit", choices=["A", "B", "C"], default="B")
    s = mk("touch"); s.add_argument("id"); s.add_argument("--template", required=True); s.add_argument("--text"); s.add_argument("--note")
    s.add_argument("--force-stage", action="store_true")
    s = mk("reply"); s.add_argument("id"); s.add_argument("--note")
    s = mk("move"); s.add_argument("id"); s.add_argument("stage"); s.add_argument("--note"); s.add_argument("--value", type=float)
    s = mk("log-post"); s.add_argument("--url"); s.add_argument("--pillar"); s.add_argument("--format", required=True)
    s = mk("log-comments"); s.add_argument("n", type=int)
    mk("today"); s = mk("due"); s.add_argument("--retention", action="store_true"); mk("pace")
    s = mk("forget"); s.add_argument("id")
    s = mk("week"); s.add_argument("--from", "--start", dest="start")
    s = mk("import-connections"); s.add_argument("csv")
    s = mk("ghl-build"); s.add_argument("--pipeline", choices=["existing", "separate"], default="existing")
    s.add_argument("--pipeline-name"); s.add_argument("--stages", nargs="+")
    s.add_argument("--tag-style", choices=["hyphen", "colon"], default="hyphen"); s.add_argument("--source-tag")
    s = mk("list"); s.add_argument("--stage")
    for name in ("settings", "init"):
        s = mk(name); s.add_argument("--premium", choices=["yes", "no"]); s.add_argument("--notes-limit", type=int)
        s.add_argument("--pillars", nargs="+"); s.add_argument("--basis")
    a = ap.parse_args(argv)
    if a.file and a.path and Path(a.file) != Path(a.path):
        refuse(f"two pipeline files given ({a.path} and --file {a.file}); pass one")
    path = a.file or a.path or DEFAULT_PATH
    a._path = str(path)
    creating = a.cmd in ("settings", "init")
    a._created = creating and not Path(path).exists()
    try:
        data = load(path, create=creating, on=today(a))
    except FileNotFoundError:
        refuse(f"no pipeline at {path}. Create it once with: li_pipeline.py settings {path} --premium yes|no "
               "(or init). If the member's pipeline is elsewhere, pass that path.")
    fn = {"add": cmd_add, "touch": cmd_touch, "reply": cmd_reply, "move": cmd_move, "log-post": cmd_log_post,
          "log-comments": cmd_log_comments, "today": cmd_today, "due": cmd_due, "pace": cmd_pace, "forget": cmd_forget,
          "week": cmd_week, "import-connections": cmd_import_connections, "ghl-build": cmd_ghl_build, "list": cmd_list,
          "settings": cmd_settings, "init": cmd_settings}[a.cmd]
    out = fn(data, a)
    if a.cmd not in ("today", "due", "pace", "week", "ghl-build", "list"):
        save(path, data)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
