#!/usr/bin/env python3
"""Event Launcher run sheet: the clock-time run-of-show, the checklist for each role, and the checks.

Local only. It reads the member's own plan of segments and writes a markdown run sheet; it never touches
Zoom, the checkout or the CRM.

Usage
  run_sheet.py build --spec runsheet.json --out run-sheet.md
      Writes the run-of-show for each day with clock times, then a checklist per role (host, moderator
      with every link drop and its time, tech with the recording notice, the backup stream and the
      checkout open check before the pitch, closer), then the checks. Prints the checks as JSON.
      Exit 0 when every "must" check passes (PASS), 1 when one fails (FAIL; the sheet is still written),
      2 when the spec is refused (unreadable, an unknown segment kind, a bad time or length).

Checks (must unless marked should)
  recording_notice       a segment in the first 10 minutes of every day mentions the recording notice
  breaks_90              no stretch longer than 90 minutes without a break segment
  length_vs_end          the segments fit the day's planned "end" (when given)
  links_have_values      every link a segment names has a value in "links" (no blanks, TBD or placeholders)
  pitch_final_day        pitch and close segments only on the final day, unless "allow_early_pitch": true
  checkout_before_close  a checkout link exists and a checkout test segment comes before the first pitch/close
  roles_assigned         host, moderator and tech are named
  proof_day2 (should)    a multi-day event has a proof segment on Day 2 (belief Day 1, proof Day 2, ascension Day 3)
  backup_link (should)   a backup link (a "links" key containing "backup") for the stream or the checkout

runsheet.json
  {"title": "Cash Flow Bootcamp", "allow_early_pitch": false,
   "roles": {"host": "Dana", "moderator": "Sam", "tech": "Lee", "closer": "Dana"},
   "links": {"workbook": "https://...", "checkout": "https://...", "backup_stream": "https://..."},
   "days": [{"date": "2026-11-10", "start": "14:00", "end": "17:00", "tz": "America/Los_Angeles",
             "segments": [{"min": 5, "title": "Welcome and recording notice", "kind": "welcome", "owner": "host",
                           "links": ["workbook"], "notes": "..."}]}]}
  kinds: welcome teach build proof break qa pitch close recap. owner: a role (host, moderator, tech, closer)
  or the person's name. links: names from "links", or full URLs.

Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, json, re  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: E402

KINDS = ["welcome", "teach", "build", "proof", "break", "qa", "pitch", "close", "recap"]
ROLES = ["host", "moderator", "tech", "closer"]
SELLING = {"pitch", "close"}
BREAK_EVERY = 90
EMPTY = re.compile(r"^\s*(|tbd|tba|todo|xxx+|\?+|none|n/a)\s*$", re.I)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}|\[.*?\]|<.*?>")
SOURCES = {
    "Build Room founder method": "belief on Day 1, proof on Day 2, ascension on Day 3; one person watches chat and drops "
                                 "the links; test checkout on the close morning; recording notice at the start",
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


def load(path):
    p = Path(path)
    if not p.exists():
        refuse(f"no spec at {path}")
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        refuse(f"{path} is not readable JSON ({e})")
    if not isinstance(spec, dict) or not isinstance(spec.get("days"), list) or not spec["days"]:
        refuse("the spec needs \"days\": a list of {date, start, segments}")
    return spec


def clock(t0, minutes):
    t = t0 + dt.timedelta(minutes=minutes)
    extra = (t.date() - t0.date()).days
    return t.strftime("%H:%M") + (f" (+{extra}d)" if extra else "")


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
        segs, at = [], 0
        if not isinstance(d.get("segments"), list) or not d["segments"]:
            refuse(f"day {i}: needs a list of segments")
        for j, s in enumerate(d["segments"], 1):
            kind = str(s.get("kind", "")).lower()
            if kind not in KINDS:
                refuse(f"day {i} segment {j} ({s.get('title', '')!r}): kind must be one of {KINDS} (got {s.get('kind')!r})")
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
                     "checkout_test": d.get("checkout_test")})
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
    return links.get(name)


def is_checkout(name):
    return "checkout" in name.lower()


def run_checks(spec, days):
    roles = {k: v for k, v in (spec.get("roles") or {}).items()}
    links = {k: ("" if v is None else str(v)) for k, v in (spec.get("links") or {}).items()}
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

    long = []
    for d in days:
        run, since = 0, d["segments"][0]["at"] if d["segments"] else ""
        for s in d["segments"]:
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
                elif EMPTY.match(v) or PLACEHOLDER.search(v):
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

    co = [k for k in links if is_checkout(k)]
    problems = []
    sell_days = [d for d in days if any(s["kind"] in SELLING for s in d["segments"])]
    if sell_days and not co:
        problems.append("no checkout link in links (name one with 'checkout' in its key)")
    for d in sell_days:
        first = next(s for s in d["segments"] if s["kind"] in SELLING)
        tested = any(s["start_min"] < first["start_min"] and "checkout" in (s["title"] + " " + s["notes"]).lower()
                     for s in d["segments"])
        if d.get("checkout_test"):
            ct = dt.datetime.combine(d["date"], hhmm(d["checkout_test"], f"day {d['n']} checkout_test"))
            tested = tested or ct < first["t"]
        if not tested:
            problems.append(f"day {d['n']}: nothing tests the checkout before \"{first['title']}\" at {first['at']} (add a "
                            "segment such as 'Tech: checkout open check' before it, or \"checkout_test\": \"HH:MM\" on the day)")
    check("checkout_before_close", not problems, "the checkout is tested before the close" if not problems and sell_days
          else "no pitch or close segment" if not problems else "; ".join(problems))

    need = [r for r in ("host", "moderator", "tech") if not str(roles.get(r) or "").strip()]
    unknown = sorted({s["owner"] for d in days for s in d["segments"] if s["owner"] and not owner_role(s["owner"], roles)})
    check("roles_assigned", not need, ("host, moderator and tech are named" if not need else f"no {', '.join(need)} named in roles")
          + (f"; owners not in roles: {', '.join(unknown)}" if unknown else ""))

    if len(days) >= 2:
        ok = any(s["kind"] == "proof" for s in days[1]["segments"])
        check("proof_day2", ok, "Day 2 has a proof segment" if ok else
              "no proof segment on Day 2 (founder method: belief Day 1, proof Day 2, ascension Day 3)", "should")
    bk = [k for k in links if "backup" in k.lower()]
    check("backup_link", bool(bk) and all(links[k] and not EMPTY.match(links[k]) for k in bk),
          f"backup link(s): {', '.join(bk)}" if bk else "no backup link: add a backup stream or a second checkout link "
          "to links (a key containing 'backup')", "should")
    return checks


def checklists(spec, days):
    """{role: [item, ...]} in clock order; each item starts with the day and the time."""
    roles = spec.get("roles") or {}
    links = {k: ("" if v is None else str(v)) for k, v in (spec.get("links") or {}).items()}
    co = next((k for k in links if is_checkout(k)), None)
    bk = [k for k in links if "backup" in k.lower()]
    items = {r: [] for r in ROLES}
    def add(role, d, minute, text):
        items[role].append((d["n"], minute, len(items[role]), f"Day {d['n']} {clock(d['t0'], minute)} {text}"))
    for d in days:
        for s in d["segments"]:
            r = owner_role(s["owner"], roles) or "host"
            if r == "closer" and not roles.get("closer"):
                r = "host"
            add(r, d, s["start_min"], f"{s['title']} ({s['kind']}, until {s['until']})")
            selling = s["kind"] in SELLING and co
            for name in s["links"]:
                if selling and name == co:
                    continue                      # dropped below, as the price is shown and every 10 minutes
                add("moderator", d, s["start_min"], f"drop {name}: {link_value(name, links) or 'NO VALUE'}")
            if selling:
                for m in range(0, s["min"], 10):
                    add("moderator", d, s["start_min"] + m, f"drop {co}: {links[co] or 'NO VALUE'}"
                        + (" (again)" if m else " (as the price is shown)" if s["kind"] == "pitch" else ""))
        add("moderator", d, 0, "from the start, all session: watch chat, answer access questions, note unresolved blockers")
        add("tech", d, -15, f"open the room; start the recording at {d['t0'].strftime('%H:%M')} and confirm the recording "
            "notice shows and is said out loud")
        add("tech", d, -15, "backup stream ready: " + (", ".join(f"{k} {links[k] or 'NO VALUE'}" for k in bk)
                                                      if bk else "NOT SET (add a backup link)"))
        sell = next((s for s in d["segments"] if s["kind"] in SELLING), None)
        if sell:
            add("tech", d, sell["start_min"] - 10, f"checkout open check before \"{sell['title']}\" at {sell['at']}: open "
                f"{co or 'the checkout'} on a phone, test full pay, the payment plan and a coupon; keep the backup "
                "checkout ready")
            add("closer" if roles.get("closer") else "host", d, sell["start_min"],
                "the offer: price on screen, payment options, refund terms, the real deadline; Q&A after as objection handling")
    out = {r: [x[3] for x in sorted(v)] for r, v in items.items()}
    if not roles.get("closer"):
        out.pop("closer")
    return out


def render(spec, days, checks, lists, result):
    roles = spec.get("roles") or {}
    links = spec.get("links") or {}
    L = [f"# Run sheet: {spec.get('title', 'Live event')}", "",
         "Roles: " + " · ".join(f"{r} **{roles[r]}**" for r in ROLES if roles.get(r)), ""]
    for d in days:
        end = clock(d["t0"], d["total"])
        L += [f"## Day {d['n']} · {d['date'].strftime('%a')} {d['date']} · {d['t0'].strftime('%H:%M')}–{end}"
              + (f" {d['tz']}" if d["tz"] else "") + (f" (planned end {d['end'].strftime('%H:%M')})" if d["end"] else ""),
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
    checks = run_checks(spec, days)
    result = "PASS" if all(c["ok"] for c in checks if c["level"] == "must") else "FAIL"
    lists = checklists(spec, days)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(render(spec, days, checks, lists, result), encoding="utf-8")
    out = {"written": a.out, "result": result,
           "days": [{"day": d["n"], "date": d["date"].isoformat(), "start": d["t0"].strftime("%H:%M"),
                     "ends": clock(d["t0"], d["total"]), "minutes": d["total"]} for d in days],
           "checks": checks, "failed": [c["id"] for c in checks if not c["ok"] and c["level"] == "must"],
           "warnings": [c["id"] for c in checks if not c["ok"] and c["level"] == "should"],
           "checklists": lists, "sources": SOURCES}
    return out, 0 if result == "PASS" else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build"); s.add_argument("--spec", required=True); s.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out, code = {"build": cmd_build}[a.cmd](a)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
