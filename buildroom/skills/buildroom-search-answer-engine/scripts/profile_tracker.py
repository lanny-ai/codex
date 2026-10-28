#!/usr/bin/env python3
"""Google Business Profile tracker, review loop and listings for the Search & Answer Engine.

Keeps `search/profile.json`: what the member's profile holds, a log of what they did
(photos, posts, review asks, reviews, replies) and their listings elsewhere. `check` scores the
profile against what moves rank and what moves conversion; `weekly` prints this week's
30-minute list; `listings check` finds name, address and phone mismatches.

Stdlib only. Run from the folder that holds the Business File (or the vault root):

  python3 profile_tracker.py init --name "Ruiz Advisory" --type service-area --category "Accountant" [--legal-name "..."]
  python3 profile_tracker.py set description="..." phone="(555) 010-0100" website=https://example.com hours_set=yes
  python3 profile_tracker.py service add "Bookkeeping clean-up" --description "..."
  python3 profile_tracker.py log photo --n 3 | post | review-ask --n 4 | review --rating 5 | reply --n 2 | update
  python3 profile_tracker.py check [--md]
  python3 profile_tracker.py weekly
  python3 profile_tracker.py listings add --site "Bing Places" --url ... --name "..." --address "..." --phone "..." --status live
  python3 profile_tracker.py listings check
  python3 profile_tracker.py report --md

Exit code 0 on success, 1 when `check` finds a critical item failing, 2 on a usage or data error.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True

TYPES = ("storefront", "service-area", "hybrid", "none")
LOG_TYPES = ("photo", "post", "review-ask", "review", "reply", "update", "qa-removed")
PROMO = re.compile(r"\b(sale|discount|% off|percent off|free consultation|call now|best in|#1|number one|cheapest|guarantee)\b|https?://|www\.", re.I)
LISTING_STATUSES = ("live", "claimed", "pending", "none", "wrong")
# Free listings worth having, in the order a solo owner should do them (local first). Apple Business replaced
# Apple Business Connect in April 2026; Yelp content is licensed to OpenAI (July 2026), so a complete Yelp page matters.
CORE_LISTINGS = ("Google Business Profile", "Bing Places", "Apple Business", "Yelp", "Facebook page", "Nextdoor", "Better Business Bureau")
BURST_DAYS, BURST_N = 7, 10   # Google pauses new reviews on a profile during a spike; never run a review blitz
TODAY = date.today


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def iso(d):
    return d.isoformat()


def parse_date(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def days_since(s):
    d = parse_date(s)
    return (TODAY() - d).days if d else None


def path(folder):
    return Path(folder) / "profile.json"


def load(folder):
    p = path(folder)
    if not p.exists():
        die(f"{p} not found; run `init` first")
    try:
        return json.loads(p.read_text(encoding="utf-8")), p
    except json.JSONDecodeError as e:
        die(f"{p} is not valid JSON: {e}")


def save(data, p):
    data["updated"] = iso(TODAY())
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def blank(name, btype, category, legal):
    return {
        "business": name, "legal_name": legal or name, "type": btype, "eligible": "unsure" if btype != "none" else "no",
        "owner_verified": False, "primary_category": category, "secondary_categories": [], "description": "",
        "services": [], "hours_set": False, "phone": "", "website": "", "appointment_url": "", "attributes": [],
        "opening_date": "", "service_area": "",
        "photos": {"count": 0, "last": ""}, "posts": {"last": ""},
        "reviews": {"count": 0, "rating": 0.0, "unanswered": 0, "oldest_unanswered_days": 0, "last_review": ""},
        "review_link": "", "ask_method": "", "ask_timing": "",
        "nap": {"name": name, "address": "", "phone": ""},
        "listings": [], "log": [], "created": iso(TODAY()), "updated": iso(TODAY()),
    }


def norm_phone(s):
    digits = re.sub(r"\D", "", s or "")
    return digits[-10:] if len(digits) >= 10 else digits


def norm_text(s):
    s = (s or "").lower()
    s = re.sub(r"\b(suite|ste|unit|apt|#)\s*", "#", s)
    s = re.sub(r"\b(street|st)\b", "st", s)
    s = re.sub(r"\b(avenue|ave)\b", "ave", s)
    s = re.sub(r"\b(road|rd)\b", "rd", s)
    s = re.sub(r"\b(drive|dr)\b", "dr", s)
    s = re.sub(r"\b(boulevard|blvd)\b", "blvd", s)
    s = re.sub(r"\b(north|n)\b", "n", s); s = re.sub(r"\b(south|s)\b", "s", s)
    s = re.sub(r"\b(east|e)\b", "e", s); s = re.sub(r"\b(west|w)\b", "w", s)
    s = re.sub(r"\b(llc|inc|ltd|co|corp)\b\.?", "", s)
    return re.sub(r"[^a-z0-9#]", "", s)


# ---------------------------------------------------------------- commands

def cmd_init(a):
    folder = Path(a.folder)
    folder.mkdir(parents=True, exist_ok=True)
    p = path(folder)
    if p.exists() and not a.force:
        die(f"{p} already exists (use --force to start over)")
    if a.type not in TYPES:
        die(f"--type must be one of {', '.join(TYPES)}")
    data = blank(a.name, a.type, a.category, a.legal_name)
    save(data, p)
    print(json.dumps({"ok": True, "file": str(p), "type": a.type,
                      "eligibility": ("A profile needs in-person contact with customers: at your place, or at theirs (service-area). "
                                      "A virtual office, a PO box or a fully remote practice is not eligible; set --type none and use listings instead.")
                      if a.type != "none" else "No profile: this business meets nobody in person, so the listings and the answer pages carry the load."},
                     indent=2))


BOOL_KEYS = {"hours_set", "owner_verified"}
LIST_KEYS = {"secondary_categories", "attributes"}
NESTED = {"photos_count": ("photos", "count"), "photos_last": ("photos", "last"), "posts_last": ("posts", "last"),
          "reviews_count": ("reviews", "count"), "reviews_rating": ("reviews", "rating"), "reviews_unanswered": ("reviews", "unanswered"),
          "reviews_oldest_unanswered_days": ("reviews", "oldest_unanswered_days"), "reviews_last": ("reviews", "last_review"),
          "nap_name": ("nap", "name"), "nap_address": ("nap", "address"), "nap_phone": ("nap", "phone")}


def cmd_set(a):
    data, p = load(a.folder)
    changed = {}
    for pair in a.pairs:
        if "=" not in pair:
            die(f"'{pair}' is not key=value")
        k, v = pair.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k in BOOL_KEYS:
            data[k] = v.lower() in ("1", "yes", "true", "y")
        elif k in LIST_KEYS:
            data[k] = [x.strip() for x in v.split(",") if x.strip()]
        elif k in NESTED:
            sec, key = NESTED[k]
            cur = data[sec].get(key)
            if isinstance(cur, bool):
                data[sec][key] = v.lower() in ("1", "yes", "true", "y")
            elif isinstance(cur, int):
                data[sec][key] = int(float(v))
            elif isinstance(cur, float):
                data[sec][key] = float(v)
            else:
                data[sec][key] = v
        elif k == "type":
            if v not in TYPES:
                die(f"type must be one of {', '.join(TYPES)}")
            data[k] = v
        elif k == "eligible":
            if v not in ("yes", "no", "unsure"):
                die("eligible must be yes, no or unsure")
            data[k] = v
        elif k in data and not isinstance(data[k], (dict, list)):
            data[k] = v
        else:
            die(f"unknown key '{k}'")
        changed[k] = v
    save(data, p)
    print(json.dumps({"ok": True, "changed": changed}, indent=2, ensure_ascii=False))


def cmd_service(a):
    data, p = load(a.folder)
    if a.action == "add":
        if any(s["name"].lower() == a.name.lower() for s in data["services"]):
            die(f"service '{a.name}' already listed")
        data["services"].append({"name": a.name, "description": a.description or ""})
    elif a.action == "remove":
        data["services"] = [s for s in data["services"] if s["name"].lower() != a.name.lower()]
    save(data, p)
    print(json.dumps({"ok": True, "services": data["services"]}, indent=2, ensure_ascii=False))


def cmd_log(a):
    data, p = load(a.folder)
    if a.type not in LOG_TYPES:
        die(f"type must be one of {', '.join(LOG_TYPES)}")
    when = a.date or iso(TODAY())
    if not parse_date(when):
        die("--date must be YYYY-MM-DD")
    n = max(1, a.n)
    entry = {"date": when, "type": a.type, "n": n, "note": a.note or ""}
    if a.type == "review":
        if a.rating is None or not 1 <= a.rating <= 5:
            die("a review needs --rating 1..5")
        entry["rating"] = a.rating
        data["reviews"]["count"] += n
        data["reviews"]["last_review"] = max(data["reviews"].get("last_review") or "", when)
        if not a.replied:
            data["reviews"]["unanswered"] += n
    if a.type == "reply":
        data["reviews"]["unanswered"] = max(0, data["reviews"]["unanswered"] - n)
        if data["reviews"]["unanswered"] == 0:
            data["reviews"]["oldest_unanswered_days"] = 0
    if a.type == "photo":
        data["photos"]["count"] += n
        data["photos"]["last"] = max(data["photos"].get("last") or "", when)
    if a.type == "post":
        data["posts"]["last"] = max(data["posts"].get("last") or "", when)
    data["log"].append(entry)
    save(data, p)
    print(json.dumps({"ok": True, "logged": entry}, indent=2, ensure_ascii=False))


def window(data, kind, days):
    since = TODAY() - timedelta(days=days)
    return sum(e.get("n", 1) for e in data["log"] if e["type"] == kind and (parse_date(e["date"]) or since) >= since)


def recent_ratings(data, days=90):
    since = TODAY() - timedelta(days=days)
    rs = [(e.get("rating"), e.get("n", 1)) for e in data["log"] if e["type"] == "review" and (parse_date(e["date"]) or since) >= since and e.get("rating")]
    tot = sum(n for _, n in rs)
    return (sum(r * n for r, n in rs) / tot) if tot else None, tot


def assess(data):
    """Return (items, score, critical_fail). Each item: key, group, ok, weight, note, fix."""
    items = []

    def item(key, group, ok, weight, note, fix=""):
        items.append({"key": key, "group": group, "ok": bool(ok), "weight": weight, "note": note, "fix": fix if not ok else ""})

    if data.get("type") == "none" or data.get("eligible") == "no":
        return items, None, False
    rv, ph = data["reviews"], data["photos"]
    name, legal = data.get("business", ""), data.get("legal_name", "")
    cat_words = set(re.findall(r"[a-z]+", (data.get("primary_category") or "").lower()))
    extra = set(re.findall(r"[a-z]+", name.lower())) - set(re.findall(r"[a-z]+", legal.lower()))
    stuffed = bool(extra & (cat_words | {"best", "near", "top", "cheap", "affordable"})) or bool(re.search(r"\b(in|near)\s+[A-Z]", name)) and name != legal
    # rank: what the 2026 ranking-factor survey puts first
    item("eligible", "rank", data.get("eligible") == "yes", 10, "the business meets customers in person (at your place or theirs)",
         "confirm eligibility; a virtual office or a remote practice gets suspended, use listings and answer pages instead")
    item("verified", "rank", data.get("owner_verified"), 6, "profile verified by the owner", "finish verification (video or postcard) before anything else")
    item("real_name", "rank", not stuffed, 8, "the name is the real-world name, no category or city added",
         "remove added words; a stuffed name is the top suspension cause and competitors report it")
    item("primary_category", "rank", bool(data.get("primary_category")), 10, "primary category set (the strongest ranking factor you control)",
         "pick the one category that matches the money service; secondary categories for the rest")
    item("secondary_categories", "rank", 1 <= len(data.get("secondary_categories", [])) <= 9, 3, "one to nine secondary categories", "add the services you actually sell as secondary categories")
    item("hours", "rank", data.get("hours_set"), 6, "hours set, and holiday hours kept current ('open now' is a filter and a ranking input)", "set hours, including holidays")
    item("service_area", "rank", data.get("type") != "service-area" or bool(data.get("service_area")), 3, "service area set for a service-area business", "list the towns or a radius you really serve (up to 20 areas)")
    # completeness and conversion
    desc = data.get("description", "")
    item("description", "convert", 250 <= len(desc) <= 750 and not PROMO.search(desc), 4,
         "description 250 to 750 characters, plain, no links or promotions",
         "write what you do, for whom, where, since when; no URLs, prices or 'best'")
    item("services", "convert", len(data.get("services", [])) >= 3 and all(s.get("description") for s in data["services"]), 5,
         "at least three services, each with a description", "add each service you sell with two sentences on who it is for")
    item("contact", "convert", bool(data.get("phone")) and bool(data.get("website")), 4, "phone and website set", "add the phone people can call and the site they can read")
    item("appointment", "convert", bool(data.get("appointment_url")), 3, "booking or appointment link set", "add the booking link (the same one the Decision Machine uses)")
    item("photos_count", "convert", ph.get("count", 0) >= 10, 3, "at least ten real photos (you, the team, the work, the place)", "add ten real photos; no stock")
    item("photos_recent", "convert", (days_since(ph.get("last")) or 999) <= 30, 3, "a new photo in the last 30 days", "add one real photo this week")
    item("post_recent", "convert", (days_since(data["posts"].get("last")) or 999) <= 14, 2, "a post in the last 14 days (does not move rank; shows you are open and real)", "post one update: a job done, a question answered, a date")
    # reviews: about a fifth of local-pack weight in 2026, and the thing customers filter on
    ds_review = days_since(rv.get("last_review"))
    item("reviews_count", "reviews", rv.get("count", 0) >= 20, 6, "twenty or more reviews (about half of consumers skip a business under twenty)", "run the ask after every job until you pass twenty")
    item("reviews_rating", "reviews", float(rv.get("rating") or 0) >= 4.5, 5, "rating 4.5 or higher (a third of consumers now require it)", "serve, then ask every happy client; never gate or incentivise")
    item("reviews_recent", "reviews", ds_review is not None and ds_review <= 90, 5, "a review in the last 90 days (three in four consumers want recent ones)", "ask this week")
    item("reviews_answered", "reviews", rv.get("unanswered", 0) == 0 and rv.get("oldest_unanswered_days", 0) <= 7, 5,
         "every review answered within seven days, each reply written for that review", "reply to each open review today, in your own words, no template")
    burst = window(data, "review", BURST_DAYS)
    item("reviews_steady", "reviews", burst < BURST_N, 4, f"no burst (fewer than {BURST_N} new reviews in {BURST_DAYS} days; Google pauses reviews during spikes)",
         "spread the asks out: a few a week, every week")
    item("review_link", "reviews", bool(data.get("review_link")) and bool(data.get("ask_method")), 3, "the review link and the ask method written down",
         "copy the 'get more reviews' link from the profile; decide how and when you ask")
    # listings
    live = {l["site"] for l in data.get("listings", []) if l.get("status") == "live"}
    core_done = [s for s in CORE_LISTINGS if s in live]
    item("listings_core", "listings", len(core_done) >= 4, 3, f"at least four of the core free listings live ({len(core_done)} of {len(CORE_LISTINGS)})",
         "claim Bing Places, Apple Business, Yelp and your Facebook page next")
    mism = listing_mismatches(data)
    item("listings_match", "listings", not mism, 3, "name, address and phone identical everywhere", "fix the mismatched listings (`listings check` names them)")

    weight = sum(i["weight"] for i in items)
    got = sum(i["weight"] for i in items if i["ok"])
    score = round(100 * got / weight) if weight else 0
    critical = any(not i["ok"] for i in items if i["key"] in ("eligible", "real_name", "primary_category", "verified"))
    return items, score, critical


def listing_mismatches(data):
    nap = data.get("nap", {})
    base = (norm_text(nap.get("name") or data.get("business")), norm_text(nap.get("address")), norm_phone(nap.get("phone") or data.get("phone")))
    out = []
    for l in data.get("listings", []):
        if l.get("status") not in ("live", "claimed"):
            continue
        probs = []
        if l.get("name") and norm_text(l["name"]) != base[0]:
            probs.append("name")
        if l.get("address") and base[1] and norm_text(l["address"]) != base[1]:
            probs.append("address")
        if l.get("phone") and norm_phone(l["phone"]) != base[2]:
            probs.append("phone")
        if probs:
            out.append({"site": l["site"], "mismatch": probs, "url": l.get("url", "")})
    return out


def cmd_check(a):
    data, _ = load(a.folder)
    items, score, critical = assess(data)
    if score is None:
        out = {"ok": True, "profile": "none", "note": "No Google Business Profile for this business (not eligible or type none). "
                                                      "Listings and answer pages do the work; run `listings check`."}
        print(json.dumps(out, indent=2))
        return
    fails = [i for i in items if not i["ok"]]
    out = {"ok": not critical, "score": score, "critical_fail": critical,
           "groups": {g: {"ok": sum(1 for i in items if i["group"] == g and i["ok"]), "of": sum(1 for i in items if i["group"] == g)} for g in ("rank", "convert", "reviews", "listings")},
           "fix_first": [{"item": i["key"], "fix": i["fix"]} for i in fails][:5], "items": items,
           "review_velocity_30d": window(data, "review", 30), "asks_30d": window(data, "review-ask", 30)}
    if a.md:
        md = render_check_md(data, items, score, critical)
        Path(a.folder, "profile-check.md").write_text(md, encoding="utf-8")
        out["wrote"] = str(Path(a.folder, "profile-check.md"))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    sys.exit(1 if critical else 0)


def render_check_md(data, items, score, critical):
    lines = [f"# Profile check · {data['business']}", "", f"Checked: {iso(TODAY())} · Score: {score}/100 · "
             f"{'HOLD: a critical item fails' if critical else 'OK to keep building'}", "",
             "| Group | Item | OK | What good looks like | Fix |", "|---|---|---|---|---|"]
    for i in items:
        lines.append(f"| {i['group']} | {i['key']} | {'yes' if i['ok'] else 'NO'} | {i['note']} | {i['fix']} |")
    lines += ["", "Rank items come from the 2026 local ranking-factor survey (category, name, proximity you cannot change, hours, reviews). "
              "Convert items do not move rank; they decide whether a person who sees you calls.", ""]
    return "\n".join(lines)


def cmd_weekly(a):
    data, _ = load(a.folder)
    tasks = []
    if data.get("type") == "none" or data.get("eligible") == "no":
        tasks.append("No profile: check one listing for accuracy and answer one question on the website instead.")
    else:
        rv, ph = data["reviews"], data["photos"]
        if rv.get("unanswered", 0):
            tasks.append(f"Reply to {rv['unanswered']} open review(s) first, each in your own words (5 min each).")
        asks = window(data, "review-ask", 7)
        if asks < 2:
            tasks.append("Ask two to four recent clients for a review, one at a time, the same day the work finished (10 min).")
        else:
            tasks.append(f"{asks} asks already this week; do not push more, keep it steady.")
        if (days_since(ph.get("last")) or 999) > 14:
            tasks.append("Add one real photo: a job, the team, the place (3 min).")
        if (days_since(data["posts"].get("last")) or 999) > 7:
            tasks.append("Post one update: a job done, a question you answered this week, a date (5 min).")
        if not data.get("hours_set"):
            tasks.append("Set your hours, including the next holiday (5 min).")
        stale = [s for s in data.get("services", []) if not s.get("description")]
        if stale:
            tasks.append(f"Write the description for {len(stale)} service(s) with none (5 min each).")
        if window(data, "update", 30) == 0:
            tasks.append("Open the profile and check name, category, hours and phone are still right; log `update` (3 min).")
    tasks.append("Check the website still loads on a phone and the booking link works (2 min).")
    print(json.dumps({"ok": True, "week_of": iso(TODAY()), "minutes": "about 30", "tasks": tasks}, indent=2, ensure_ascii=False))


def cmd_listings(a):
    data, p = load(a.folder)
    if a.action == "add":
        if a.status not in LISTING_STATUSES:
            die(f"--status must be one of {', '.join(LISTING_STATUSES)}")
        existing = next((l for l in data["listings"] if l["site"].lower() == a.site.lower()), None)
        entry = {"site": a.site, "url": a.url or "", "name": a.name or "", "address": a.address or "", "phone": a.phone or "",
                 "status": a.status, "checked": iso(TODAY())}
        if existing:
            existing.update(entry)
        else:
            data["listings"].append(entry)
        save(data, p)
        print(json.dumps({"ok": True, "listing": entry}, indent=2, ensure_ascii=False))
    elif a.action == "check":
        mism = listing_mismatches(data)
        live = {l["site"] for l in data["listings"] if l.get("status") == "live"}
        missing = [s for s in CORE_LISTINGS if s not in live and not (s == "Google Business Profile" and data.get("type") == "none")]
        stale = [l["site"] for l in data["listings"] if (days_since(l.get("checked")) or 999) > 90]
        print(json.dumps({"ok": not mism, "mismatches": mism, "core_missing": missing, "not_checked_90_days": stale,
                          "note": "Citations weigh little for rank now, but three of the top AI-visibility inputs are listing-type, "
                                  "and a wrong phone on a directory costs real calls."}, indent=2, ensure_ascii=False))
        sys.exit(1 if mism else 0)
    else:
        rows = data["listings"]
        print(json.dumps({"ok": True, "listings": rows}, indent=2, ensure_ascii=False))


def cmd_report(a):
    data, _ = load(a.folder)
    items, score, critical = assess(data)
    rating90, n90 = recent_ratings(data)
    rep = {"business": data["business"], "date": iso(TODAY()), "score": score, "critical_fail": critical,
           "reviews": {"count": data["reviews"]["count"], "rating": data["reviews"]["rating"], "last_30_days": window(data, "review", 30),
                       "asks_last_30_days": window(data, "review-ask", 30), "rating_last_90_days": round(rating90, 2) if rating90 else None,
                       "unanswered": data["reviews"]["unanswered"]},
           "photos_last_30_days": window(data, "photo", 30), "posts_last_30_days": window(data, "post", 30),
           "listings_live": sorted(l["site"] for l in data["listings"] if l.get("status") == "live"),
           "listing_mismatches": listing_mismatches(data)}
    asks = rep["reviews"]["asks_last_30_days"]
    rep["ask_to_review"] = round(rep["reviews"]["last_30_days"] / asks, 2) if asks else None
    if a.md:
        lines = [f"# Profile report · {data['business']} · {rep['date']}", "",
                 f"Score {score if score is not None else 'n/a'}/100" + (" · HOLD (critical item)" if critical else ""), "",
                 f"- Reviews: {rep['reviews']['count']} at {rep['reviews']['rating']} · {rep['reviews']['last_30_days']} new in 30 days from {asks} asks"
                 + (f" ({rep['ask_to_review']:.0%} of asks)" if rep["ask_to_review"] is not None else "") + f" · {rep['reviews']['unanswered']} unanswered",
                 f"- Photos added in 30 days: {rep['photos_last_30_days']} · Posts in 30 days: {rep['posts_last_30_days']}",
                 f"- Listings live: {', '.join(rep['listings_live']) or 'none'}",
                 f"- Listing mismatches: {len(rep['listing_mismatches'])}", ""]
        if items:
            lines += ["## Fix first", ""] + [f"- {i['key']}: {i['fix']}" for i in items if not i["ok"]][:5] + [""]
        out = Path(a.folder, "profile-report.md")
        out.write_text("\n".join(lines), encoding="utf-8")
        rep["wrote"] = str(out)
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default="search")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--name", required=True); s.add_argument("--type", default="service-area")
    s.add_argument("--category", default=""); s.add_argument("--legal-name", default=""); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_init)
    s = sub.add_parser("set"); s.add_argument("pairs", nargs="+"); s.set_defaults(f=cmd_set)
    s = sub.add_parser("service"); s.add_argument("action", choices=("add", "remove")); s.add_argument("name"); s.add_argument("--description", default=""); s.set_defaults(f=cmd_service)
    s = sub.add_parser("log"); s.add_argument("type"); s.add_argument("--n", type=int, default=1); s.add_argument("--rating", type=int, default=None)
    s.add_argument("--replied", action="store_true"); s.add_argument("--date", default=""); s.add_argument("--note", default=""); s.set_defaults(f=cmd_log)
    s = sub.add_parser("check"); s.add_argument("--md", action="store_true"); s.set_defaults(f=cmd_check)
    s = sub.add_parser("weekly"); s.set_defaults(f=cmd_weekly)
    s = sub.add_parser("listings"); s.add_argument("action", choices=("add", "check", "list")); s.add_argument("--site", default="")
    s.add_argument("--url", default=""); s.add_argument("--name", default=""); s.add_argument("--address", default=""); s.add_argument("--phone", default="")
    s.add_argument("--status", default="live"); s.set_defaults(f=cmd_listings)
    s = sub.add_parser("report"); s.add_argument("--md", action="store_true"); s.set_defaults(f=cmd_report)
    a = ap.parse_args(argv)
    if a.cmd == "listings" and a.action == "add" and not a.site:
        die("listings add needs --site")
    a.f(a)


if __name__ == "__main__":
    main()
