#!/usr/bin/env python3
"""Event Launcher calendar files and reminder times: the .ics, the add-to-calendar links, the reminder clock.

Local only. It writes a calendar file and prints links and times; it never sends a reminder, never
touches Zoom or GoHighLevel. The member pastes the links and sets the workflows in their own tools.

Usage
  event_ics.py build --spec event.json --out event.ics [--date YYYY-MM-DD]
      An RFC 5545 VCALENDAR with one VEVENT per day: times in UTC (Z), a stable UID per day (from the
      title and organizer, or "uid_seed"; it survives a time change, so bump "sequence" when you resend a
      changed file), DTSTAMP (--date replays it as that day 00:00Z), SEQUENCE, a display alarm, escaped
      text and 75-octet folded CRLF lines. Prints a Google Calendar and two Outlook add-links per day.
      Refused (exit 2): unknown time zone, an end not after its start, days not in date order, a local
      time that does not exist (clocks spring forward). Warned: daylight saving changes between days, any
      time outside 07:00–21:00 local, a merge-field join link such as {{contact.zoom_link}} (kept verbatim:
      a static .ics file cannot carry a per-contact link).
  event_ics.py reminders --spec event.json [--recipient-tz IANA ...]
      The reminder schedule: the day before Day 1, the morning of each day, 15 minutes before, "we're
      live" at the start, and a night-before recap ahead of Day 2 onwards. Each send has its host-local
      and UTC time and its local time in every recipient time zone (default: the event's own). SMS sends
      outside 08:00–21:00 in a recipient zone are flagged (federal TCPA quiet hours, 47 CFR 64.1200);
      08:00–09:00 and 20:00–21:00 are flagged as caution (the safe default is 09:00–20:00; some states
      are stricter).
  event_ics.py check event.ics
      Parses and validates an .ics: CRLF line endings, 75-octet lines, BEGIN/END nesting, VERSION and
      PRODID, UID and DTSTAMP on every event, DTSTAMP in UTC, DTSTART/DTEND in UTC or with a TZID that has
      a VTIMEZONE (floating times flagged), end after start, unique UIDs, escaped commas and semicolons in
      text, alarms with ACTION and TRIGGER. Exit 0 when clean, 1 when it found problems, 2 when unreadable.

event.json
  {"title": "Cash Flow Bootcamp", "organizer": "Dana Ruiz", "organizer_email": "dana@example.com",
   "tz": "America/Los_Angeles", "join_url": "https://zoom.us/j/123" or "{{contact.zoom_link}}",
   "alarm_minutes": 15, "description": "shown on every day", "sequence": 0, "uid_seed": "optional",
   "days": [{"date": "2026-11-10", "start": "14:00", "end": "17:00", "title": "optional", "description": "optional"}],
   "reminders": {"morning_time": "08:00", "recap_after_end_minutes": 60,
                 "sms": ["day_before", "morning_of", "15_min", "live_now"]}}

Standard library only (zoneinfo for time zones).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, hashlib, json, re  # noqa: E402
from pathlib import Path  # noqa: E402
from urllib.parse import quote  # noqa: E402
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: E402

UTC = dt.timezone.utc
PRODID = "-//Build Room//Event Launcher//EN"
PLACEHOLDER = re.compile(r"\{\{.*?\}\}")
DAY_HOURS = (dt.time(7, 0), dt.time(21, 0))
SMS_FEDERAL = (dt.time(8, 0), dt.time(21, 0))    # 47 CFR 64.1200(c)(1): not before 8 a.m. or after 9 p.m. local
SMS_SAFE = (dt.time(9, 0), dt.time(20, 0))       # research safe default (stricter states)
REMINDER_KINDS = ["day_before", "morning_of", "night_before_recap", "15_min", "live_now"]
DEFAULT_SMS = ["day_before", "morning_of", "15_min", "live_now"]
SOURCES = {
    "RFC 5545": "iCalendar: CRLF lines folded at 75 octets, UID and DTSTAMP on every VEVENT, UTC times end in Z, "
                "a TZID needs a matching VTIMEZONE",
    "TCPA 47 CFR 64.1200": "no telephone solicitations (texts included) before 8 a.m. or after 9 p.m. in the "
                           "recipient's local time; some states are stricter (Florida is reported as 8 p.m.)",
    "GHL help 2026": "HighLevel's 'Set Event Start Date' workflow action uses the account time zone even when the "
                     "workflow is set to the contact's time zone",
    "Build Room founder run Jul 2026": "the Day 2 'we're live' email fired about 4 hours early, twice; there was no "
                                       "Day-1-night or Day-2-night email; Day 3 opened at 82 people",
    "Calendar link docs 2026": "Google: calendar.google.com/calendar/render?action=TEMPLATE&dates=…Z/…Z; Outlook: "
                               "outlook.live.com (or outlook.office.com)/calendar/deeplink/compose?…&startdt=…Z; keep "
                               "links under about 2,000 characters for email clients",
}


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


def zone(name, what):
    try:
        return ZoneInfo(str(name))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        refuse(f"{what} must be an IANA time zone such as America/New_York (got {name!r})")


def hhmm(s, what):
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", str(s or ""))
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        refuse(f"{what} must be a time as HH:MM, 24-hour (got {s!r})")
    return dt.time(int(m.group(1)), int(m.group(2)))


def load_spec(path):
    p = Path(path)
    if not p.exists():
        refuse(f"no spec at {path}")
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        refuse(f"{path} is not readable JSON ({e})")
    if not isinstance(spec, dict):
        refuse(f"{path} must hold a JSON object")
    for k in ("title", "tz", "days"):
        if not spec.get(k):
            refuse(f"the spec needs \"{k}\"")
    if not isinstance(spec["days"], list):
        refuse("\"days\" must be a list of {date, start, end}")
    return spec


def localize(day, t, tz, what, warnings):
    """An aware local datetime; refuses a wall time that does not exist, warns on an ambiguous one."""
    naive = dt.datetime.combine(day, t)
    aware = naive.replace(tzinfo=tz)
    back = aware.astimezone(UTC).astimezone(tz)
    if back.replace(tzinfo=None) != naive:
        refuse(f"{what} {day} {t.strftime('%H:%M')} does not exist in {tz.key} (the clocks spring forward); pick another time")
    if aware.replace(fold=1).utcoffset() != aware.utcoffset():
        warnings.append(f"{what} {day} {t.strftime('%H:%M')} happens twice in {tz.key} (the clocks fall back); the first one is used")
    return aware


def resolve_days(spec):
    """[{n, date, start, end (aware local), start_utc, end_utc, summary, description}] plus warnings."""
    tz = zone(spec["tz"], "\"tz\"")
    warnings, days, prev = [], [], None
    for i, d in enumerate(spec["days"], 1):
        if not isinstance(d, dict):
            refuse(f"day {i} must be an object with date, start and end")
        try:
            date = dt.date.fromisoformat(str(d.get("date", "")).strip())
        except ValueError:
            refuse(f"day {i}: date must be YYYY-MM-DD (got {d.get('date')!r})")
        st, en = hhmm(d.get("start"), f"day {i} start"), hhmm(d.get("end"), f"day {i} end")
        if en <= st:
            refuse(f"day {i} ({date}): the end {en.strftime('%H:%M')} is not after the start {st.strftime('%H:%M')}")
        if prev and date <= prev:
            refuse(f"days must be in date order, one session a day: day {i} ({date}) is not after day {i - 1} ({prev})")
        prev = date
        s, e = localize(date, st, tz, f"day {i} start", warnings), localize(date, en, tz, f"day {i} end", warnings)
        for label, t in (("start", st), ("end", en)):
            if t < DAY_HOURS[0] or t > DAY_HOURS[1]:
                warnings.append(f"day {i} {label} {t.strftime('%H:%M')} is outside 07:00–21:00 in {tz.key}: check the "
                                "time suits your audience (and their zones)")
        n = len(spec["days"])
        summary = d.get("title") or (f"{spec['title']} - Day {i}" if n > 1 else spec["title"])
        days.append({"n": i, "date": date, "start": s, "end": e, "start_utc": s.astimezone(UTC), "end_utc": e.astimezone(UTC),
                     "summary": summary, "description": d.get("description") or spec.get("description") or ""})
    if not days:
        refuse("\"days\" is empty")
    for a, b in zip(days, days[1:]):
        if a["start"].utcoffset() != b["start"].utcoffset():
            off = lambda t: "UTC" + t.strftime("%z")[:3] + (":" + t.strftime("%z")[3:] if t.strftime("%z")[3:] != "00" else "")
            warnings.append(f"daylight saving changes between day {a['n']} ({a['date']}) and day {b['n']} ({b['date']}) in "
                            f"{tz.key} ({off(a['start'])} → {off(b['start'])}): the same clock time there is a different "
                            "UTC time, so people in zones that change on another date (or not at all) see the session "
                            "move by an hour; give the time in their zones in the reminders")
    return tz, days, warnings


# ---------------- writing ----------------

def esc(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n"))


def param(v):
    v = str(v).replace('"', "'")
    return f'"{v}"' if re.search(r"[,;:]", v) else v


def fold(line):
    """75-octet folding (RFC 5545 3.1), never splitting a UTF-8 character; returns CRLF-joined bytes."""
    b = line.encode("utf-8")
    out, limit = [], 75
    while len(b) > limit:
        cut = limit
        while cut > 0 and (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut]); b = b[cut:]
        limit = 74          # continuation lines start with a space
    out.append(b)
    return b"\r\n ".join(out) + b"\r\n"


def utc_stamp(t):
    return t.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def uid_for(spec, n):
    seed = spec.get("uid_seed") or f"{spec['title']}|{spec.get('organizer') if isinstance(spec.get('organizer'), str) else (spec.get('organizer') or {}).get('name', '')}"
    return f"{hashlib.sha1(seed.encode('utf-8')).hexdigest()[:16]}-day{n}@buildroom-event-launcher"


def organizer(spec):
    o = spec.get("organizer")
    if isinstance(o, dict):
        return o.get("name") or "", o.get("email") or spec.get("organizer_email") or ""
    return o or "", spec.get("organizer_email") or ""


def full_description(spec, d):
    name, _ = organizer(spec)
    parts = [d["description"]] if d["description"] else []
    if spec.get("join_url"):
        parts.append(f"Join: {spec['join_url']}")
    if name:
        parts.append(f"Host: {name}")
    return "\n\n".join(parts)


def qkeep(s, safe=""):
    """URL-encode, but keep merge fields such as {{contact.zoom_link}} verbatim so the CRM can fill them."""
    out, last = [], 0
    for m in PLACEHOLDER.finditer(s):
        out.append(quote(s[last:m.start()], safe=safe)); out.append(m.group(0)); last = m.end()
    out.append(quote(s[last:], safe=safe))
    return "".join(out)


def links(spec, d):
    desc = full_description(spec, d)
    loc = spec.get("location") or spec.get("join_url") or ""
    s, e = utc_stamp(d["start_utc"]), utc_stamp(d["end_utc"])
    g = ("https://calendar.google.com/calendar/render?action=TEMPLATE"
         f"&text={qkeep(d['summary'])}&dates={s}/{e}&details={qkeep(desc)}&location={qkeep(loc)}")
    iso = lambda t: t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    tail = (f"/calendar/deeplink/compose?path=/calendar/action/compose&rru=addevent"
            f"&startdt={iso(d['start_utc'])}&enddt={iso(d['end_utc'])}&subject={qkeep(d['summary'])}"
            f"&body={qkeep(desc)}&location={qkeep(loc)}")
    return {"google": g, "outlook": "https://outlook.live.com" + tail, "outlook_365": "https://outlook.office.com" + tail}


def ics_bytes(spec, days, stamp):
    name, email = organizer(spec)
    alarm = int(spec.get("alarm_minutes", 15))
    seq = int(spec.get("sequence", 0))
    loc = spec.get("location") or spec.get("join_url") or ""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{PRODID}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             f"X-WR-CALNAME:{esc(spec['title'])}"]
    for d in days:
        lines += ["BEGIN:VEVENT", f"UID:{uid_for(spec, d['n'])}", f"DTSTAMP:{stamp}", f"SEQUENCE:{seq}",
                  f"DTSTART:{utc_stamp(d['start_utc'])}", f"DTEND:{utc_stamp(d['end_utc'])}",
                  f"SUMMARY:{esc(d['summary'])}"]
        desc = full_description(spec, d)
        if desc:
            lines.append(f"DESCRIPTION:{esc(desc)}")
        if loc:
            lines.append(f"LOCATION:{esc(loc)}")
        if re.match(r"https?://", spec.get("join_url") or "") and not PLACEHOLDER.search(spec["join_url"]):
            lines.append(f"URL:{spec['join_url']}")
        if email:
            lines.append(f"ORGANIZER;CN={param(name or email)}:mailto:{email}")
        lines += ["STATUS:CONFIRMED", "TRANSP:OPAQUE"]
        if alarm >= 0:
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(d['summary'])} starts in {alarm} minutes",
                      f"TRIGGER:-PT{alarm}M", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return b"".join(fold(x) for x in lines)


def common_warnings(spec):
    w = []
    j = spec.get("join_url") or ""
    if not j:
        w.append("no join_url: the calendar entries have no link to the session; add it, or send it in the reminders")
    elif PLACEHOLDER.search(j):
        w.append(f"join_url {j} is a merge field: it is written verbatim. A static .ics file is the same for everyone and "
                 "cannot carry a per-contact link, so attach a file with the shared link (or none) and send each "
                 "person's own link in the email or SMS, where the CRM fills the field")
    return w


def cmd_build(a):
    spec = load_spec(a.spec)
    tz, days, warnings = resolve_days(spec)
    warnings = common_warnings(spec) + warnings
    try:
        alarm = int(spec.get("alarm_minutes", 15))
        int(spec.get("sequence", 0))
    except (TypeError, ValueError):
        refuse("\"alarm_minutes\" and \"sequence\" must be whole numbers")
    if a.date:
        try:
            stamp = dt.date.fromisoformat(a.date).strftime("%Y%m%dT000000Z")
        except ValueError:
            refuse(f"--date must be YYYY-MM-DD (got {a.date!r})")
    else:
        stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    data = ics_bytes(spec, days, stamp)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_bytes(data)
    events = []
    for d in days:
        ln = links(spec, d)
        for k, v in ln.items():
            if len(v) > 2000:
                warnings.append(f"day {d['n']} {k} link is {len(v)} characters; some email clients cut links over about "
                                "2,000: shorten the description")
        events.append({"day": d["n"], "summary": d["summary"], "uid": uid_for(spec, d["n"]),
                       "start_local": d["start"].strftime("%Y-%m-%d %H:%M %Z (%a)"),
                       "end_local": d["end"].strftime("%Y-%m-%d %H:%M %Z"),
                       "start_utc": d["start_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "end_utc": d["end_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"), **ln})
    out = {"written": a.out, "tz": tz.key, "alarm_minutes": alarm, "events": events,
           "note": "test the file and each link on desktop and phone (Google, Outlook, Apple) before it goes out",
           "sources": {k: SOURCES[k] for k in ("RFC 5545", "Calendar link docs 2026")}}
    if warnings:
        out["warnings"] = warnings
    return out, 0


# ---------------- reminders ----------------

def window_flag(t, window):
    return t < window[0] or t >= window[1]


def cmd_reminders(a):
    spec = load_spec(a.spec)
    tz, days, warnings = resolve_days(spec)
    cfg = spec.get("reminders") or {}
    morning = hhmm(cfg.get("morning_time", "08:00"), "reminders.morning_time")
    recap_after = int(cfg.get("recap_after_end_minutes", 60))
    sms = cfg.get("sms", DEFAULT_SMS)
    bad = [k for k in sms if k not in REMINDER_KINDS]
    if bad:
        refuse(f"reminders.sms lists unknown sends {bad}; choose from {REMINDER_KINDS}")
    zones = [zone(z, "--recipient-tz") for z in (a.recipient_tz or [spec["tz"]])]
    sends = []
    def add(kind, day, when, purpose, note=None):
        sends.append({"kind": kind, "day": day["n"], "when": when, "purpose": purpose, **({"note": note} if note else {})})
    for d in days:
        if d["n"] == 1:
            add("day_before", d, d["start"] - dt.timedelta(days=1),
                "how to prepare, the calendar file, the one pre-work action; same clock time as the start")
        m = localize(d["date"], morning, tz, "reminders.morning_time", warnings)
        if m <= d["start"] - dt.timedelta(minutes=30):
            add("morning_of", d, m, f"today is Day {d['n']}: what happens, the start time in a few zones, the link")
        else:
            warnings.append(f"day {d['n']}: the morning reminder ({morning.strftime('%H:%M')}) is not at least 30 minutes "
                            "before the start, so it is left out; the 15-minute reminder covers it")
        if d["n"] >= 2:
            prev = days[d["n"] - 2]
            add("night_before_recap", d, prev["end"] + dt.timedelta(minutes=recap_after),
                f"Day-{prev['n']}-night recap and the Day-{d['n']} payoff (founder lesson: without it people drift away)")
        add("15_min", d, d["start"] - dt.timedelta(minutes=15), "starting in 15 minutes, with the link")
        add("live_now", d, d["start"], "we're live now, with the link")
    sends.sort(key=lambda s: (s["when"].astimezone(UTC), REMINDER_KINDS.index(s["kind"])))
    flags, out = [], []
    for s in sends:
        ch = ["email"] + (["sms"] if s["kind"] in sms else [])
        u = s["when"].astimezone(UTC)
        rec = []
        for z in zones:
            lt = u.astimezone(z)
            r = {"tz": z.key, "local": lt.strftime("%Y-%m-%d %H:%M (%a)")}
            if "sms" in ch:
                if window_flag(lt.time(), SMS_FEDERAL):
                    r["sms_flag"] = "outside 08:00–21:00 local: federal TCPA quiet hours; do not text this zone then"
                elif window_flag(lt.time(), SMS_SAFE):
                    r["sms_flag"] = "caution: outside the 09:00–20:00 safe window (some states are stricter)"
                if "sms_flag" in r:
                    flags.append(f"{s['kind']} day {s['day']} SMS at {r['local']} {z.key}: {r['sms_flag']}")
            if s["kind"] == "morning_of" and lt.date() != s["when"].date():
                r["note"] = f"arrives on {lt.date()} in this zone, not the event's morning"
            rec.append(r)
        out.append({"id": f"day{s['day']}-{s['kind']}", "kind": s["kind"], "day": s["day"], "channels": ch,
                    "local": s["when"].strftime("%Y-%m-%d %H:%M %Z (%a)"), "utc": u.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "purpose": s["purpose"], "recipients": rec})
    warnings += [
        f"GoHighLevel: 'Set Event Start Date' uses the account time zone, even in a workflow set to the contact's time "
        f"zone. Set the account time zone to {tz.key} (or build the waits from the UTC times above) and dry-run every "
        "send with a test contact 24 hours before",
        "reminders that fire hours early lose the room (founder Jul 2026: the Day 2 'we're live' email fired about 4 "
        "hours early, twice); check each send's UTC time in the workflow, not just the clock time",
    ]
    res = {"tz": tz.key, "recipient_tz": [z.key for z in zones], "sends": out, "sms_flags": flags, "warnings": warnings,
           "sources": {k: SOURCES[k] for k in ("TCPA 47 CFR 64.1200", "GHL help 2026", "Build Room founder run Jul 2026")}}
    return res, 0


# ---------------- check ----------------

TEXT_PROPS = {"SUMMARY", "DESCRIPTION", "LOCATION", "COMMENT", "X-WR-CALNAME"}
STAMP_RE = re.compile(r"^\d{8}T\d{6}Z$")


def split_line(line):
    """name, {params}, value of an unfolded content line (colons inside quoted params are skipped)."""
    inq, cut = False, None
    for i, ch in enumerate(line):
        if ch == '"':
            inq = not inq
        elif ch == ":" and not inq:
            cut = i; break
    if cut is None:
        return None
    head, value = line[:cut], line[cut + 1:]
    parts = re.findall(r'(?:[^;"]|"[^"]*")+', head)
    name = parts[0].upper() if parts else ""
    params = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1); params[k.upper()] = v.strip('"')
    return name, params, value


def bad_escapes(value):
    i, out = 0, []
    while i < len(value):
        ch = value[i]
        if ch == "\\":
            if i + 1 >= len(value) or value[i + 1] not in "\\;,nN":
                out.append("a backslash not followed by \\ ; , or n")
            i += 2; continue
        if ch in ",;":
            out.append(f"an unescaped '{ch}'")
        i += 1
    return sorted(set(out))


def unesc(value):
    return re.sub(r"\\([\\;,nN])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), value)


def parse_time(value, params, tzids):
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        return dt.datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC), "date"
    m = re.fullmatch(r"(\d{8}T\d{6})(Z?)", value)
    if not m:
        return None, "bad"
    t = dt.datetime.strptime(m.group(1), "%Y%m%dT%H%M%S")
    if m.group(2):
        return t.replace(tzinfo=UTC), "utc"
    if "TZID" in params:
        try:
            return t.replace(tzinfo=ZoneInfo(params["TZID"])), "tzid"
        except (ZoneInfoNotFoundError, ValueError):
            return None, "tzid"
    return t, "floating"


def cmd_check(a):
    p = Path(a.ics)
    if not p.exists():
        refuse(f"no file at {a.ics}")
    raw = p.read_bytes()
    problems, warnings = [], []
    if re.search(rb"(?<!\r)\n", raw):
        problems.append("bare LF line endings: RFC 5545 needs CRLF (\\r\\n) at the end of every line")
    if raw and not raw.endswith(b"\n"):
        problems.append("the last line has no line ending")
    phys = re.split(rb"\r?\n", raw)
    if phys and phys[-1] == b"":
        phys = phys[:-1]
    long = [i + 1 for i, x in enumerate(phys) if len(x) > 75]
    if long:
        problems.append(f"{len(long)} line(s) longer than 75 octets (not folded): line {', '.join(map(str, long[:5]))}"
                        + (" …" if len(long) > 5 else ""))
    logical = []
    for x in phys:
        if x[:1] in (b" ", b"\t") and logical:
            logical[-1] += x[1:]
        else:
            logical.append(x)
    try:
        lines = [x.decode("utf-8") for x in logical]
    except UnicodeDecodeError:
        refuse(f"{a.ics} is not UTF-8 text (a fold may have split a character)")
    if not lines or lines[0].strip().upper() != "BEGIN:VCALENDAR":
        refuse(f"{a.ics} does not start with BEGIN:VCALENDAR")
    stack, comps, cur, tzids = [], [], None, set()
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        sp = split_line(line)
        if not sp:
            problems.append(f"line {n}: not a content line (no ':'): {line[:40]!r}"); continue
        name, params, value = sp
        if name == "BEGIN":
            stack.append(value.upper())
            if value.upper() in ("VEVENT", "VTIMEZONE", "VALARM", "VCALENDAR"):
                cur = {"type": value.upper(), "props": {}, "line": n, "parent": cur}
                comps.append(cur)
            continue
        if name == "END":
            if not stack or stack[-1] != value.upper():
                problems.append(f"line {n}: END:{value} does not match BEGIN:{stack[-1] if stack else '(none)'}")
            else:
                stack.pop()
                if cur and cur["type"] == value.upper():
                    cur = cur["parent"]
            continue
        if cur is None:
            problems.append(f"line {n}: {name} outside any component"); continue
        cur["props"].setdefault(name, []).append((params, value, n))
        if name == "TZID" and cur["type"] == "VTIMEZONE":
            tzids.add(value)
        if name in TEXT_PROPS:
            for b in bad_escapes(value):
                problems.append(f"line {n}: {name} has {b} (escape commas and semicolons in text as \\, and \\;)")
    if stack:
        problems.append(f"unclosed component(s): {', '.join(stack)}")
    cal = next((c for c in comps if c["type"] == "VCALENDAR"), None)
    if cal:
        for req in ("VERSION", "PRODID"):
            if req not in cal["props"]:
                problems.append(f"VCALENDAR has no {req}")
        if cal["props"].get("VERSION", [({}, "2.0", 0)])[0][1] != "2.0":
            problems.append("VERSION must be 2.0")
    events, uids = [], {}
    for c in comps:
        pr = c["props"]
        if c["type"] == "VALARM":
            for req in ("ACTION", "TRIGGER"):
                if req not in pr:
                    problems.append(f"VALARM at line {c['line']} has no {req}")
        if c["type"] != "VEVENT":
            continue
        label = f"VEVENT at line {c['line']}"
        for req in ("UID", "DTSTAMP", "DTSTART"):
            if req not in pr:
                problems.append(f"{label} has no {req}")
        if "UID" in pr:
            uids.setdefault(pr["UID"][0][1], []).append(c["line"])
        if "DTSTAMP" in pr and not STAMP_RE.match(pr["DTSTAMP"][0][1]):
            problems.append(f"{label}: DTSTAMP must be a UTC time ending in Z (got {pr['DTSTAMP'][0][1]})")
        times = {}
        for k in ("DTSTART", "DTEND"):
            if k not in pr:
                continue
            params, value, ln = pr[k][0]
            t, kind = parse_time(value, params, tzids)
            if kind == "bad":
                problems.append(f"line {ln}: {k} {value!r} is not a date-time")
            elif kind == "floating":
                problems.append(f"line {ln}: {k} {value} is a floating time (no Z, no TZID): it shows the same clock "
                                "time in every zone; use UTC with Z")
            elif kind == "tzid":
                if params.get("TZID") not in tzids:
                    problems.append(f"line {ln}: {k} uses TZID={params.get('TZID')} but the file has no VTIMEZONE for it")
                if t is None:
                    warnings.append(f"line {ln}: TZID {params.get('TZID')} is not an IANA name this checker knows")
            times[k] = t
        if times.get("DTSTART") and times.get("DTEND") and times["DTEND"] <= times["DTSTART"]:
            problems.append(f"{label}: DTEND is not after DTSTART")
        if "DTEND" not in pr and "DURATION" not in pr:
            warnings.append(f"{label} has no DTEND or DURATION")
        st = times.get("DTSTART")
        events.append({"uid": pr.get("UID", [({}, None, 0)])[0][1], "summary": unesc(pr.get("SUMMARY", [({}, "", 0)])[0][1]),
                       "description": unesc(pr.get("DESCRIPTION", [({}, "", 0)])[0][1]),
                       "start_utc": st.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if st and st.tzinfo else None,
                       "end_utc": times["DTEND"].astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                       if times.get("DTEND") and times["DTEND"].tzinfo else None})
    for u, where in uids.items():
        if len(where) > 1:
            problems.append(f"UID {u} is used by {len(where)} events: each day needs its own UID or updates overwrite the wrong one")
    if not events:
        problems.append("no VEVENT in the file")
    res = {"file": a.ics, "ok": not problems, "events": events, "problems": problems,
           "sources": {"RFC 5545": SOURCES["RFC 5545"]}}
    if warnings:
        res["warnings"] = warnings
    return res, (0 if not problems else 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build"); s.add_argument("--spec", required=True); s.add_argument("--out", required=True)
    s.add_argument("--date")
    s = sub.add_parser("reminders"); s.add_argument("--spec", required=True); s.add_argument("--recipient-tz", nargs="+")
    s = sub.add_parser("check"); s.add_argument("ics")
    a = ap.parse_args(argv)
    out, code = {"build": cmd_build, "reminders": cmd_reminders, "check": cmd_check}[a.cmd](a)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
