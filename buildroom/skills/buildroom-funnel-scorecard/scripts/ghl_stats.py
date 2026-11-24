#!/usr/bin/env python3
"""Funnel numbers from the member's own GoHighLevel sub-account: counts only, for the last 30 days (or --days).

  ghl_stats.py                  prints the counts, the rates that can be worked out, and what could not be read
  ghl_stats.py --days 30 --env .env

What it reads: how many contacts were added, how many form entries came in, how many appointments were booked and
how they ended (showed, no-show, cancelled), and how many deals were marked won. It asks GoHighLevel for totals and
statuses. It never prints, stores or sends a contact's name, email, phone or anything they wrote.

It changes nothing in the account and it writes no file. It sends nothing to Build Room: the session shows the member
the numbers, and only if the member has switched sharing on does the session pass "numbers" to buildroom_report.

The token comes from GHL_TOKEN and GHL_LOCATION_ID, in the environment or a .env file. It is never a command-line
argument and is never printed. A part the token is not allowed to read is reported as not read, never guessed.
It goes online to GoHighLevel's API (services.leadconnectorhq.com) and nowhere else. Standard library only.
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28"
MIN_FOR_RATE = 5          # a rate from fewer than this many is noise, so it is left out and said so
SCOPE_FOR = {"leads": "View Contacts", "form_entries": "View Forms", "appointments": "View Calendars and View Calendar Events",
             "deals_won": "View Opportunities"}


def read_env(path):
    out = {}
    p = Path(path)
    if p.is_file():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
            if m and not line.lstrip().startswith("#"):
                out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(f"{code}: {msg}")
        self.code, self.msg = code, msg


def call(base, token, method, path, body=None, tries=4):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(tries):
        req = urllib.request.Request(base + path, data=data, method=method, headers={
            "Authorization": "Bearer " + token, "Version": VERSION, "Accept": "application/json", "Content-Type": "application/json",
            "User-Agent": "BuildRoomOS-stats/1"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(2 + 3 * attempt)
                continue
            try:
                msg = json.loads(text).get("message", text)
            except ValueError:
                msg = text
            raise Refused(e.code, msg)
        except (urllib.error.URLError, OSError) as e:
            if attempt == tries - 1:
                raise Refused(0, f"could not reach GoHighLevel: {e}")
            time.sleep(2 + 3 * attempt)
    raise Refused(429, "GoHighLevel kept answering 'too busy'")


def not_allowed(e):
    return e.code in (401, 403) and "scope" in e.msg.lower()


def count_leads(base, token, loc, start, end):
    r = call(base, token, "POST", "/contacts/search", {"locationId": loc, "pageLimit": 1, "filters": [
        {"field": "dateAdded", "operator": "range", "value": {"gte": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "lte": end.strftime("%Y-%m-%dT%H:%M:%SZ")}}]})
    return int(r.get("total") or 0)


def count_forms(base, token, loc, start, end):
    q = urllib.parse.urlencode({"locationId": loc, "limit": 1, "startAt": start.strftime("%Y-%m-%d"), "endAt": end.strftime("%Y-%m-%d")})
    r = call(base, token, "GET", "/forms/submissions?" + q)
    return int((r.get("meta") or {}).get("total") or 0)


def count_appointments(base, token, loc, start, end):
    """{"booked", "showed", "no_show", "cancelled"} across every calendar. Only the status of each appointment is looked at."""
    cals = call(base, token, "GET", "/calendars/?" + urllib.parse.urlencode({"locationId": loc})).get("calendars") or []
    if not cals:
        return None                                  # no calendar here: bookings happen somewhere else, so zero would be a false number
    out = {"booked": 0, "showed": 0, "no_show": 0, "cancelled": 0}
    for c in cals:
        if not c.get("id"):
            continue
        q = urllib.parse.urlencode({"locationId": loc, "calendarId": c["id"], "startTime": int(start.timestamp() * 1000), "endTime": int(end.timestamp() * 1000)})
        for ev in call(base, token, "GET", "/calendars/events?" + q).get("events") or []:
            status = str(ev.get("appointmentStatus") or "").lower().replace("-", "").replace("_", "")
            if status == "invalid":
                continue
            out["booked"] += 1
            if status == "showed":
                out["showed"] += 1
            elif status == "noshow":
                out["no_show"] += 1
            elif status == "cancelled":
                out["cancelled"] += 1
    return out


def count_won(base, token, loc, start, end):
    q = urllib.parse.urlencode({"location_id": loc, "status": "won", "limit": 1, "date": start.strftime("%m-%d-%Y"), "endDate": end.strftime("%m-%d-%Y")})
    r = call(base, token, "GET", "/opportunities/search?" + q)
    return int((r.get("meta") or {}).get("total") or 0)


def rate(part, whole):
    return round(100.0 * part / whole, 1) if whole >= MIN_FOR_RATE and part <= whole else None


def gather(base, token, loc, days, now=None):
    end = now or datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    counts, missing = {}, []
    for key, fn in (("leads", count_leads), ("form_entries", count_forms), ("appointments", count_appointments), ("deals_won", count_won)):
        try:
            got = fn(base, token, loc, start, end)
            if got is None:
                missing.append({"what": key, "why": "this account has no calendar, so calls booked are not counted here. If the member books calls in another tool, ask them for the number"})
            else:
                counts[key] = got
        except Refused as e:
            if key == "leads" and e.code in (401, 403) and not not_allowed(e):
                raise                                       # the token itself is wrong: nothing else will work either
            missing.append({"what": key, "why": ("the token is not allowed to read this. Add " + SCOPE_FOR[key] + " to the integration") if not_allowed(e) else str(e)})
    appt = counts.get("appointments") or {}
    numbers, left_out = {}, []
    if days == 30:                                           # the shareable results are monthly; another window is for the member's eyes only
        if "leads" in counts:
            numbers["leads_month"] = counts["leads"]
        if appt:
            numbers["calls_booked_month"] = appt["booked"]
        if "deals_won" in counts:
            numbers["clients_won_month"] = counts["deals_won"]
        for name, part, whole, words in (
                ("booking_rate_pct", appt.get("booked"), counts.get("leads"), "calls booked out of new leads"),
                ("show_rate_pct", appt.get("showed"), (appt.get("showed", 0) + appt.get("no_show", 0)) if appt else None, "calls that happened out of calls that were due"),
                ("close_rate_pct", counts.get("deals_won"), appt.get("showed"), "deals won out of calls that happened")):
            if part is None or whole is None:
                continue
            r = rate(part, whole)
            if r is None:
                left_out.append(f"{name}: {words} is {part} of {whole}, too few to call a rate")
            else:
                numbers[name] = r
    return {"days": days, "from": start.strftime("%Y-%m-%d"), "to": end.strftime("%Y-%m-%d"), "counts": counts, "numbers": numbers,
            "rates_left_out": left_out, "not_read": missing}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--env", default=".env")
    a = ap.parse_args()
    if not 1 <= a.days <= 365:
        sys.exit("--days is a number from 1 to 365")
    env = read_env(a.env)
    token = os.environ.get("GHL_TOKEN") or env.get("GHL_TOKEN")
    loc = os.environ.get("GHL_LOCATION_ID") or env.get("GHL_LOCATION_ID")
    base = (os.environ.get("GHL_API_BASE") or env.get("GHL_API_BASE") or API).rstrip("/")
    if not token or not loc:
        sys.exit("No GoHighLevel connection found. This needs GHL_TOKEN and GHL_LOCATION_ID, in the environment or in the .env file "
                 f"({a.env}). The member adds them themselves; never ask them to paste a token into the chat.")
    try:
        out = gather(base, token, loc, a.days)
    except Refused as e:
        if e.code == 401:
            sys.exit("Stopped: GoHighLevel did not accept the token. It may have been rotated or deleted: the member makes a new one and saves it again.")
        if e.code == 403:
            sys.exit("Stopped: this token belongs to a different sub-account than GHL_LOCATION_ID names. Check both were taken from the same account.")
        sys.exit("Stopped: " + str(e))
    out["note"] = ("Counts only: no contact's name, email, phone or words were read into this. Nothing was changed in the account and nothing was sent anywhere. "
                   "Show the member these numbers. Pass \"numbers\" to buildroom_report only if they have switched sharing on."
                   + ("" if a.days == 30 else " A window other than 30 days is for the member's own eyes: it is not shared."))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
