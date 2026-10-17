#!/usr/bin/env python3
"""Event Launcher run sheet: the clock-time run-of-show, the checklist for each role, and the checks.

Local only. It reads the member's own plan of segments and writes a markdown run sheet; it never touches
Zoom, the checkout, the booking calendar or the CRM.

Usage
  run_sheet.py build --spec runsheet.json --out run-sheet.md [--event event.json]
      Writes the run-of-show for each day with clock times, then a checklist per role (host, moderator
      with every link drop and its time, tech with the recording notice, the backup stream and the
      money-path check before the pitch, closer), then the checks. Prints the checks as JSON.
      --event cross-checks the days, dates, start and end times and the time zone against event_ics.py's
      event.json (check event_match).
      Exit 0 when every "must" check passes (PASS), 1 when one fails (FAIL; the sheet is still written),
      2 when the spec is refused (unreadable, an unknown segment kind, a bad time or length).

Checks (must unless marked should)
  recording_notice       a segment in the first 10 minutes of every day mentions the recording notice
  first_build            Day 1 has a build segment starting within its first 30 minutes (20 is the founder's rule)
  breaks_90              no stretch longer than 90 minutes without a break segment
  length_vs_end          the segments fit the day's planned "end" (when given; lobby time not counted)
  links_have_values      every link a segment names has a value in "links" (no blanks, TBD or placeholders)
  pitch_final_day        pitch and close segments only on the final day, unless "allow_early_pitch": true
  checkout_before_close  a close link (kind checkout, booking or application) exists and a test of it comes
                         before the first pitch/close on each selling day
  roles_assigned         host, moderator and tech are named (a placeholder such as [moderator], TBD, TODO or
                         an empty value does not count)
  backup_link            a backup link (kind backup, or a key containing "backup") with a real value; a
                         must on any event with a pitch, otherwise should; a placeholder value always fails
  event_match            (with --event) the run sheet and event.json agree on days, dates, times and zone
  proof_day2 (should)    a multi-day event has a proof segment on Day 2 (belief Day 1, proof Day 2, ascension Day 3)
  lobby (should)         each day opens with a lobby segment before the start (people arriving, music, chat prompt)

runsheet.json
  {"title": "Cash Flow Bootcamp", "allow_early_pitch": false, "close": "checkout|call|both (optional)",
   "roles": {"host": "Dana", "moderator": "Sam", "tech": "Lee", "closer": "Dana"},
   "links": {"workbook": "https://...", "checkout": "https://...", "backup_stream": "https://...",
             "install_call": {"url": "https://...", "kind": "booking"}},
   "days": [{"date": "2026-11-10", "start": "14:00", "end": "17:00", "tz": "America/Los_Angeles",
             "segments": [{"min": 10, "title": "Lobby", "kind": "lobby"},
                          {"min": 5, "title": "Welcome and recording notice", "kind": "welcome", "owner": "host",
                           "links": ["workbook"], "notes": "..."}]}]}
  kinds: lobby welcome teach build proof break qa pitch close recap. Lobby segments come first and run
  before the start time. owner: a role (host, moderator, tech, closer) or the person's name. links: names
  from "links", or full URLs. A link is a URL, or {"url", "kind"} with kind checkout | booking |
  application | backup | other; without a kind, a key with a word starting checkout, book or call,
  or appl/apply is that kind (install_call, book_now, apply), and one with a backup word is a backup.
  The moderator drops close links (checkout, booking, application) only from the first pitch of the day
  onwards, and backup links only if the main link fails.

Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, json, re  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: E402

KINDS = ["lobby", "welcome", "teach", "build", "proof", "break", "qa", "pitch", "close", "recap"]
ROLES = ["host", "moderator", "tech", "closer"]
SELLING = {"pitch", "close"}
CLOSE_KINDS = {"checkout", "booking", "application"}
LINK_KINDS = CLOSE_KINDS | {"backup", "other"}
BREAK_EVERY = 90
FIRST_BUILD = (20, 30)
EMPTY = re.compile(r"^\s*(|tbd|tba|todo|xxx+|\?+|none|n/a)\s*$", re.I)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}|\[.*?\]|<.*?>|\btbd\b|\btodo\b|\btba\b", re.I)
SOURCES = {
    "Build Room founder method": "belief on Day 1, proof on Day 2, ascension on Day 3; everyone builds in the first "
                                 "20 minutes; one person watches chat and drops the links; test the money path on the "
                                 "close morning; recording notice at the start",
    "Build Room founder run Jul 2026": "checkout broke at peak intent at two camps in a row; in September nobody could "
                                       "buy (\"I built a door… and forgot to unlock it\")",
    "Zoom recording consent": "Zoom shows a recording consent notice; several US states need all-party consent, so "
                              "announce the recording at the start",
}


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


def hhmm(s, what):
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", str(s or ""))
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        refuse(f"{what} must be a time as HH:MM, 24-hour (got {s!r})")
    return dt.time(int(m.group(1)), int(m.group(2)))


def load(path, what="spec"):
    p = Path(path)
    if not p.exists():
        refuse(f"no {what} at {path}")
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        refuse(f"{path} is not readable JSON ({e})")
    if not isinstance(spec, dict) or not isinstance(spec.get("days"), list) or not spec["days"]:
        refuse(f"the {what} needs \"days\": a list of {{date, start, ...}}")
    return spec


def clock(t0, minutes):
    t = t0 + dt.timedelta(minutes=minutes)
    extra = (t.date() - t0.date()).days
    return t.strftime("%H:%M") + (f" ({extra:+d}d)" if extra else "")


def blank(v):
    v = "" if v is None else str(v)
    return bool(EMPTY.match(v) or PLACEHOLDER.search(v))


def norm_links(spec):
    """{name: {"url": str, "kind": str}}."""
    out = {}
    for k, v in (spec.get("links") or {}).items():
        if isinstance(v, dict):
            url, kind = ("" if v.get("url") is None else str(v.get("url"))), str(v.get("kind") or "").lower()
            if kind and kind not in LINK_KINDS:
                refuse(f"link {k!r}: kind must be one of {sorted(LINK_KINDS)} (got {kind!r})")
        else:
            url, kind = ("" if v is None else str(v)), ""
        if not kind:
            words = [x for x in re.split(r"[^a-z]+", k.lower()) if x]
            has = lambda *p: any(x.startswith(p) for x in words)
            kind = ("backup" if has("backup") else "checkout" if has("checkout") else
                    "booking" if has("book", "call") else "application" if has("appl", "apply") else "other")
        out[k] = {"url": url, "kind": kind}
    return out


def resolve(spec):
    """Days with absolute segment times; refuses bad kinds, lengths and times."""
    days = []
    for i, d in enumerate(spec["days"], 1):
        try:
            date = dt.date.fromisoformat(str(d.get("date", "")).strip())
        except ValueError:
            refuse(f"day {i}: date must be YYYY-MM-DD (got {d.get('date')!r})")
        if d.get("tz"):
            try:
                ZoneInfo(d["tz"])
            except (ZoneInfoNotFoundError, ValueError):
                refuse(f"day {i}: tz must be an IANA time zone (got {d['tz']!r})")
        t0 = dt.datetime.combine(date, hhmm(d.get("start"), f"day {i} start"))
        end = dt.datetime.combine(date, hhmm(d["end"], f"day {i} end")) if d.get("end") else None
        if end and end <= t0:
            end += dt.timedelta(days=1)
        if not isinstance(d.get("segments"), list) or not d["segments"]:
            refuse(f"day {i}: needs a list of segments")
        raw = d["segments"]
        lead = 0
        for s in raw:
            if str(s.get("kind", "")).lower() != "lobby":
                break
            lead += s.get("min") if isinstance(s.get("min"), int) else 0
        segs, at, content = [], -lead, False
        for j, s in enumerate(raw, 1):
            kind = str(s.get("kind", "")).lower()
            if kind not in KINDS:
                refuse(f"day {i} segment {j} ({s.get('title', '')!r}): kind must be one of {KINDS} (got {s.get('kind')!r})")
            if kind == "lobby" and content:
                refuse(f"day {i} segment {j} ({s.get('title', '')!r}): lobby segments come first, before the start")
            content = content or kind != "lobby"
            mins = s.get("min")
            if not isinstance(mins, int) or isinstance(mins, bool) or mins < 1:
                refuse(f"day {i} segment {j} ({s.get('title', '')!r}): min must be a whole number of minutes, 1 or more")
            lk = s.get("links") or []
            if isinstance(lk, str):
                lk = [lk]
            segs.append({"n": j, "start_min": at, "end_min": at + mins, "min": mins, "title": str(s.get("title", "")).strip(),
                         "kind": kind, "owner": str(s.get("owner", "")).strip(), "links": [str(x) for x in lk],
                         "notes": str(s.get("notes", "") or "").strip(),
                         "at": clock(t0, at), "until": clock(t0, at + mins), "t": t0 + dt.timedelta(minutes=at)})
            at += mins
        days.append({"n": i, "date": date, "t0": t0, "end": end, "tz": d.get("tz", ""), "segments": segs, "total": at,
                     "lobby": lead, "checkout_test": d.get("checkout_test")})
    for a, b in zip(days, days[1:]):
        if b["date"] <= a["date"]:
            refuse(f"days must be in date order: day {b['n']} ({b['date']}) is not after day {a['n']} ({a['date']})")
    return days


def owner_role(owner, roles):
    o = owner.lower()
    if o in ROLES:
        return o
    for r, name in roles.items():
        if name and str(name).strip().lower() == o:
            return r
    return None


def link_value(name, links):
    if re.match(r"https?://", name):
        return name
    return links[name]["url"] if name in links else None


def content(d):
    return [s for s in d["segments"] if s["kind"] != "lobby"]


def run_checks(spec, days, event=None):
    roles = {k: v for k, v in (spec.get("roles") or {}).items()}
    links = norm_links(spec)
    final = days[-1]["n"]
    checks = []
    def check(cid, ok, detail, level="must"):
        checks.append({"id": cid, "level": level, "ok": bool(ok), "detail": detail})

    miss = []
    for d in days:
        if not any(s["start_min"] < 10 and "recording" in (s["title"] + " " + s["notes"]).lower() for s in d["segments"]):
            miss.append(f"day {d['n']}")
    check("recording_notice", not miss, "every day opens with the recording notice" if not miss else
          f"no recording notice in the first 10 minutes on {', '.join(miss)}: add one to the opening segment "
          "(several US states need everyone's consent)")

    b1 = next((s for s in content(days[0]) if s["kind"] == "build"), None)
    ok = b1 is not None and b1["start_min"] <= FIRST_BUILD[1]
    check("first_build", ok,
          (f"Day 1 builds at {b1['at']} (minute {b1['start_min']})" + ("" if b1["start_min"] <= FIRST_BUILD[0] else
           f"; the founder's rule is within {FIRST_BUILD[0]} minutes") if ok else
           f"no build segment in Day 1's first {FIRST_BUILD[1]} minutes" + (f" (the first is at {b1['at']}, minute "
           f"{b1['start_min']})" if b1 else "") + f": everyone builds something within {FIRST_BUILD[0]}–{FIRST_BUILD[1]} "
           "minutes (founder method)"))

    long = []
    for d in days:
        segs = content(d)
        run, since = 0, segs[0]["at"] if segs else ""
        for s in segs:
            if s["kind"] == "break":
                run, since = 0, s["until"]; continue
            run += s["min"]
            if run > BREAK_EVERY:
                long.append(f"day {d['n']} from {since} to {s['until']} ({run} min, through \"{s['title']}\")")
                run, since = -10 ** 6, ""          # report each stretch once
    check("breaks_90", not long, f"a break at least every {BREAK_EVERY} minutes" if not long else
          f"over {BREAK_EVERY} minutes without a break: " + "; ".join(long))

    over, info = [], []
    for d in days:
        if d["end"]:
            planned = int((d["end"] - d["t0"]).total_seconds() // 60)
            if d["total"] > planned:
                over.append(f"day {d['n']} runs {d['total']} min, {d['total'] - planned} over the planned "
                            f"{d['t0'].strftime('%H:%M')}–{d['end'].strftime('%H:%M')} ({planned} min)")
            elif planned - d["total"] > 15:
                info.append(f"day {d['n']} ends {planned - d['total']} min early")
        else:
            info.append(f"day {d['n']} has no planned end; the segments end at {clock(d['t0'], d['total'])}")
    check("length_vs_end", not over, ("; ".join(over) if over else "every day fits its planned end")
          + (" (" + "; ".join(info) + ")" if info else ""))

    bad = []
    for d in days:
        for s in d["segments"]:
            for name in s["links"]:
                v = link_value(name, links)
                if v is None:
                    bad.append(f"day {d['n']} {s['at']} \"{s['title']}\" names link '{name}', which is not in links")
                elif blank(v):
                    bad.append(f"link '{name}' has no real value ({v!r}), used day {d['n']} {s['at']}")
    check("links_have_values", not bad, "every link has a value" if not bad else "; ".join(dict.fromkeys(bad)))

    early = [f"day {d['n']} {s['at']} \"{s['title']}\" ({s['kind']})" for d in days if d["n"] != final
             for s in d["segments"] if s["kind"] in SELLING]
    allow = bool(spec.get("allow_early_pitch"))
    check("pitch_final_day", not early or allow,
          ("pitch and close only on the final day" if not early else
           f"early pitch allowed by the spec: {'; '.join(early)}" if allow else
           f"pitch or close before the final day: {'; '.join(early)} (set \"allow_early_pitch\": true if that is the "
           "plan, for example a VIP offer on Day 1)"))

    co = [k for k, v in links.items() if v["kind"] in CLOSE_KINDS]
    kinds = sorted({links[k]["kind"] for k in co})
    problems = []
    sell_days = [d for d in days if any(s["kind"] in SELLING for s in d["segments"])]
    if sell_days and not co:
        problems.append("no close link in links (a checkout, booking or application link: name it with that word in "
                        "its key, or give it \"kind\")")
    words = ("checkout", "booking", "book", "application", "payment link")
    for d in sell_days:
        first = next(s for s in d["segments"] if s["kind"] in SELLING)
        tested = any(s["start_min"] < first["start_min"] and any(w in (s["title"] + " " + s["notes"]).lower() for w in words)
                     for s in d["segments"])
        if d.get("checkout_test"):
            ct = dt.datetime.combine(d["date"], hhmm(d["checkout_test"], f"day {d['n']} checkout_test"))
            tested = tested or ct < first["t"]
        if not tested:
            problems.append(f"day {d['n']}: nothing tests the {'/'.join(kinds) or 'checkout'} link before \"{first['title']}\" "
                            f"at {first['at']} (add a segment such as 'Tech: checkout open check' or 'Tech: booking link "
                            "check' before it, or \"checkout_test\": \"HH:MM\" on the day)")
    check("checkout_before_close", not problems, (f"the {'/'.join(kinds)} link is tested before the close"
                                                   if not problems and sell_days else
                                                   "no pitch or close segment" if not problems else "; ".join(problems)))

    need = [r for r in ("host", "moderator", "tech") if blank(roles.get(r))]
    unknown = sorted({s["owner"] for d in days for s in d["segments"] if s["owner"] and not owner_role(s["owner"], roles)})
    check("roles_assigned", not need, ("host, moderator and tech are named" if not need else
                                       f"no real name for {', '.join(need)} in roles (empty, TBD, TODO or a placeholder)")
          + (f"; owners not in roles: {', '.join(unknown)}" if unknown else ""))

    bk = [k for k, v in links.items() if v["kind"] == "backup"]
    fake = [k for k in bk if blank(links[k]["url"])]
    level = "must" if sell_days or fake else "should"
    check("backup_link", bool(bk) and not fake,
          (f"backup link(s): {', '.join(bk)}" if bk and not fake else
           f"backup link(s) without a real value: {', '.join(fake)}" if fake else
           "no backup link: add a backup stream and a second checkout or booking link to links (kind backup, or a key "
           "containing 'backup')"), level)

    if event is not None:
        mism = event_mismatches(event, days)
        check("event_match", not mism, "run sheet and event.json agree on days, dates, times and zone" if not mism
              else "run sheet and event.json disagree: " + "; ".join(mism))

    if len(days) >= 2:
        ok = any(s["kind"] == "proof" for s in days[1]["segments"])
        check("proof_day2", ok, "Day 2 has a proof segment" if ok else
              "no proof segment on Day 2 (founder method: belief Day 1, proof Day 2, ascension Day 3)", "should")
    nolobby = [f"day {d['n']}" for d in days if not d["lobby"]]
    check("lobby", not nolobby, "every day opens with a lobby before the start" if not nolobby else
          f"no lobby segment on {', '.join(nolobby)}: add a short lobby (kind lobby) before the start so early arrivals "
          "have something to do", "should")
    return checks


def event_mismatches(ev, days):
    out = []
    ed = ev.get("days") or []
    if len(ed) != len(days):
        out.append(f"{len(days)} day(s) here, {len(ed)} in event.json")
    for d, e in zip(days, ed):
        n = d["n"]
        if str(e.get("date", "")).strip() != d["date"].isoformat():
            out.append(f"day {n} date {d['date']} vs {e.get('date')}")
        if e.get("start") and hhmm(e["start"], f"event day {n} start") != d["t0"].time():
            out.append(f"day {n} start {d['t0'].strftime('%H:%M')} vs {e['start']}")
        if e.get("end") and d["end"] and hhmm(e["end"], f"event day {n} end") != d["end"].time():
            out.append(f"day {n} end {d['end'].strftime('%H:%M')} vs {e['end']}")
        if d["tz"] and ev.get("tz") and d["tz"] != ev["tz"]:
            out.append(f"day {n} tz {d['tz']} vs {ev['tz']}")
    return out


def checklists(spec, days):
    """{role: [item, ...]} in clock order; each item starts with the day and the time."""
    roles = spec.get("roles") or {}
    links = norm_links(spec)
    close_links = [k for k, v in links.items() if v["kind"] in CLOSE_KINDS]
    co = close_links[0] if close_links else None
    bk = [k for k, v in links.items() if v["kind"] == "backup"]
    items = {r: [] for r in ROLES}
    url = lambda k: link_value(k, links) or "NO VALUE"
    def add(role, d, minute, text):
        items[role].append((d["n"], minute, len(items[role]), f"Day {d['n']} {clock(d['t0'], minute)} {text}"))
    for d in days:
        sell = next((s for s in d["segments"] if s["kind"] in SELLING), None)
        for s in d["segments"]:
            r = owner_role(s["owner"], roles) or "host"
            if r == "closer" and blank(roles.get("closer")):
                r = "host"
            add(r, d, s["start_min"], f"{s['title']} ({s['kind']}, until {s['until']})")
            selling = s["kind"] in SELLING and co
            for name in s["links"]:
                kind = links[name]["kind"] if name in links else "other"
                if selling and name == co:
                    continue                      # dropped below, as the price is shown and every 10 minutes
                if kind == "backup":
                    continue                      # backups only if the main link fails (below)
                if kind in CLOSE_KINDS and (not sell or s["start_min"] < sell["start_min"]):
                    add("moderator", d, s["start_min"], f"hold {name}: not before the pitch"
                        + (f" at {sell['at']}" if sell else " (no pitch today)"))
                    continue
                add("moderator", d, s["start_min"], f"drop {name}: {url(name)}")
            if selling:
                for m in range(0, s["min"], 10):
                    add("moderator", d, s["start_min"] + m, f"drop {co}: {url(co)}"
                        + (" (again)" if m else " (as the price is shown)" if s["kind"] == "pitch" else ""))
        if sell and bk:
            add("moderator", d, sell["start_min"], "if a link fails: drop the backup "
                + ", ".join(f"{k} {url(k)}" for k in bk) + " (only then)")
        add("moderator", d, 0, "from the start, all session: watch chat, answer access questions, note unresolved blockers")
        open_at = min(-15, -d["lobby"] - 5)
        add("tech", d, open_at, f"open the room; start the recording at {d['t0'].strftime('%H:%M')} and confirm the recording "
            "notice shows and is said out loud")
        add("tech", d, open_at, "backup stream ready: " + (", ".join(f"{k} {url(k)}" for k in bk)
                                                           if bk else "NOT SET (add a backup link)"))
        if sell:
            add("tech", d, sell["start_min"] - 10, f"{'checkout' if not co or links[co]['kind'] == 'checkout' else links[co]['kind']} "
                f"open check before \"{sell['title']}\" at {sell['at']}: open {co or 'the checkout'} on a phone, test "
                "every path (full pay, the payment plan, a coupon; or the booking form and its confirmation); keep the "
                "backup link ready")
            add("closer" if not blank(roles.get("closer")) else "host", d, sell["start_min"],
                "the offer: price on screen, payment options, refund terms, the real deadline; Q&A after as objection handling")
    out = {r: [x[3] for x in sorted(v)] for r, v in items.items()}
    if blank(roles.get("closer")):
        out.pop("closer")
    return out


def render(spec, days, checks, lists, result):
    roles = spec.get("roles") or {}
    links = norm_links(spec)
    L = [f"# Run sheet: {spec.get('title', 'Live event')}", "",
         "Roles: " + " · ".join(f"{r} **{roles[r]}**" for r in ROLES if roles.get(r)), ""]
    for d in days:
        end = clock(d["t0"], d["total"])
        L += [f"## Day {d['n']} · {d['date'].strftime('%a')} {d['date']} · {d['t0'].strftime('%H:%M')}–{end}"
              + (f" {d['tz']}" if d["tz"] else "") + (f" (planned end {d['end'].strftime('%H:%M')})" if d["end"] else "")
              + (f" · lobby from {clock(d['t0'], -d['lobby'])}" if d["lobby"] else ""),
              "", "| Time | Min | Kind | Segment | Owner | Links | Notes |", "|---|---|---|---|---|---|---|"]
        for s in d["segments"]:
            who = s["owner"] or "host"
            name = roles.get(who.lower()) if who.lower() in ROLES else None
            ln = ", ".join(f"[{x}]({link_value(x, links)})" if link_value(x, links) else f"{x} (no value)" for x in s["links"])
            L.append(f"| {s['at']} | {s['min']} | {s['kind']} | {s['title']} | {who}{f' ({name})' if name else ''} | {ln} | "
                     f"{s['notes'].replace('|', '/')} |")
        L.append("")
    L.append("## Checklists by role")
    for r, items in lists.items():
        L += ["", f"### {r.capitalize()}" + (f" ({roles[r]})" if roles.get(r) else ""), ""]
        L += [f"- [ ] {x}" for x in items] or ["- (nothing assigned)"]
    L += ["", f"## Checks: {result}", ""]
    for c in checks:
        mark = "✅" if c["ok"] else ("❌" if c["level"] == "must" else "⚠️")
        L.append(f"- {mark} **{c['id']}** ({c['level']}): {c['detail']}")
    L += ["", "Sources:"] + [f"- **{k}**: {v}" for k, v in SOURCES.items()]
    return "\n".join(L) + "\n"


def cmd_build(a):
    spec = load(a.spec)
    days = resolve(spec)
    event = load(a.event, "event spec") if a.event else None
    checks = run_checks(spec, days, event)
    result = "PASS" if all(c["ok"] for c in checks if c["level"] == "must") else "FAIL"
    lists = checklists(spec, days)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(render(spec, days, checks, lists, result), encoding="utf-8")
    out = {"written": a.out, "result": result,
           "days": [{"day": d["n"], "date": d["date"].isoformat(), "start": d["t0"].strftime("%H:%M"),
                     "ends": clock(d["t0"], d["total"]), "minutes": d["total"], "lobby_minutes": d["lobby"]} for d in days],
           "checks": checks, "failed": [c["id"] for c in checks if not c["ok"] and c["level"] == "must"],
           "warnings": [c["id"] for c in checks if not c["ok"] and c["level"] == "should"],
           "checklists": lists, "sources": SOURCES}
    return out, 0 if result == "PASS" else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build"); s.add_argument("--spec", required=True); s.add_argument("--out", required=True)
    s.add_argument("--event")
    a = ap.parse_args(argv)
    out, code = {"build": cmd_build}[a.cmd](a)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
