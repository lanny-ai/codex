#!/usr/bin/env python3
"""Google Business Profile tracker, review loop and listings for the Search & Answer Engine.

Keeps `search/profile.json`: what the member's profile holds, a log of what they did
(photos, posts, review asks, reviews, replies) and their listings elsewhere. `check` scores the
profile against what moves rank and what moves the buyer; `weekly` prints this week's
30-minute list; `listings check` finds name, address and phone mismatches.

Stdlib only. Run from the folder that holds the Business File (or the vault root). `--folder`
may go before or after the command:

  python3 profile_tracker.py init --name "Ruiz Advisory" --legal-name "Ruiz Advisory LLC" --type service-area --category "Accountant"
  python3 profile_tracker.py init --name "Harbor Coaching" --legal-name "Harbor Coaching" --type none        # no in-person contact: no profile
  python3 profile_tracker.py set eligible=yes owner_verified=yes hours_set=yes phone="(555) 010-0100" website=https://example.com
  python3 profile_tracker.py set review_ask=no            # a profession whose code bars asking clients (therapists, counsellors)
  python3 profile_tracker.py service add "Bookkeeping clean-up" --description "..."
  python3 profile_tracker.py log photo --n 3 | post | review-ask --n 4 | review --rating 5 [--replied] | reply --n 2 | update
  python3 profile_tracker.py check [--md]
  python3 profile_tracker.py weekly
  python3 profile_tracker.py listings add --site "Bing Places" --url ... --name "..." --address "..." --phone "..." --status live
  python3 profile_tracker.py listings check
  python3 profile_tracker.py report --md

Keep names and details out of this file: `log review` takes a rating and a date, nothing else
(a reviewer's name or a client's details never go in `profile.json`).

Exit code 0 on success, 1 when `check` finds a critical item failing or `listings check` finds a mismatch,
2 on a usage or data error.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True

TYPES = ("storefront", "service-area", "hybrid", "none")
LOG_TYPES = ("photo", "post", "review-ask", "review", "reply", "update")
PROMO = re.compile(r"\b(sale|discount|% off|percent off|call now|best in|#1|number one|cheapest|lowest price)\b|https?://|www\.", re.I)
LISTING_STATUSES = ("live", "claimed", "pending", "none", "wrong")
# Free listings worth having, in the order a solo owner should do them. Apple Business replaced Apple Business Connect in
# April 2026 (one vendor source for the date); Yelp's listing data is licensed to OpenAI (July 2026), so a complete Yelp page matters.
CORE_LISTINGS = ("Bing Places", "Apple Business", "Yelp", "Facebook page", "Nextdoor", "Better Business Bureau")
CORE_LISTINGS_REMOTE = ("Facebook page", "LinkedIn page", "Better Business Bureau", "Professional body directory")
BURST_DAYS, BURST_N = 7, 10   # a spike the member's own asks do not explain looks like spam to Google, which pauses reviews
GROUP_ORDER = {"rank": 0, "reviews": 1, "convert": 2, "listings": 3}
CRITICAL = ("eligible", "verified", "real_name", "primary_category")
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


def within(s, n):
    """True when the date is a real date no more than n days ago (today counts)."""
    d = days_since(s)
    return d is not None and 0 <= d <= n


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
        "business": name, "legal_name": legal, "type": btype, "eligible": "unsure" if btype != "none" else "no",
        "review_ask": "yes", "owner_verified": False, "primary_category": category, "secondary_categories": [], "description": "",
        "services": [], "hours_set": False, "phone": "", "website": "", "appointment_url": "", "attributes": [],
        "opening_date": "", "service_area": "",
        "photos": {"count": 0, "last": ""}, "posts": {"last": ""},
        "reviews": {"count": 0, "rating": 0.0, "unanswered": 0, "oldest_unanswered_days": 0, "last_review": ""},
        "review_link": "", "ask_method": "", "ask_timing": "",
        "nap": {"name": name, "address": "", "phone": ""},
        "listings": [], "log": [], "created": iso(TODAY()), "updated": iso(TODAY()),
    }


def norm_phone(s):
    return re.sub(r"\D", "", s or "")


def phones_match(a, b):
    da, db = norm_phone(a), norm_phone(b)
    if not da or not db:
        return True
    if len(da) >= 11 and len(db) >= 11:
        return da == db
    return da[-10:] == db[-10:]


def norm_text(s):
    s = (s or "").lower()
    s = re.sub(r"\b(suite|ste|unit|apt|#)\s*", "#", s)
    for long, short in (("street", "st"), ("avenue", "ave"), ("road", "rd"), ("drive", "dr"), ("boulevard", "blvd"),
                        ("north", "n"), ("south", "s"), ("east", "e"), ("west", "w")):
        s = re.sub(rf"\b{long}\b", short, s)
    s = re.sub(r"\b(llc|inc|ltd|co|corp)\b\.?", "", s)
    return re.sub(r"[^a-z0-9#]", "", s)


def stuffed_name(name, legal, category):
    """Words in the shown name that are not in the legal name and look like a category, a superlative or a place."""
    name_words = re.findall(r"[a-z]+", name.lower())
    legal_words = set(re.findall(r"[a-z]+", (legal or "").lower()))
    extra = [w for w in name_words if w not in legal_words]
    cat_words = set(re.findall(r"[a-z]+", (category or "").lower())) - {"and", "of", "the", "services", "service"}
    flags = {"best", "near", "top", "cheap", "cheapest", "affordable", "local", "licensed", "emergency", "24", "hour"}
    if any(w in flags for w in name_words) or any(w in cat_words for w in extra):
        return True
    return bool(re.search(r"\b(in|near|of)\s+[A-Z][a-z]+", name)) and norm_text(name) != norm_text(legal or "")


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
    notes = {
        "storefront": "A storefront profile shows the address; keep hours, holiday hours and the primary category current.",
        "service-area": "A service-area business hides its address and lists the areas it serves (up to 20). A home address shown, a PO box or a virtual office gets the profile suspended.",
        "hybrid": "A hybrid business (customers come to you AND you go to them) shows the address and lists a service area; set both.",
        "none": "No profile: this business meets nobody in person, so Google would suspend one. Listings (Facebook, LinkedIn, BBB, the professional body), the answer pages, LinkedIn and mentions carry the load. Set the phone and website first (`set phone=… website=…`) so the listings can be checked against them.",
    }
    print(json.dumps({"ok": True, "file": str(p), "type": a.type, "note": notes[a.type],
                      "next": "set eligible=yes once in-person contact is confirmed; the name here must be the one on signage and invoices"}, indent=2))


BOOL_KEYS = {"hours_set", "owner_verified"}
LIST_KEYS = {"secondary_categories", "attributes"}
DATE_KEYS = {"opening_date", "photos_last", "posts_last", "reviews_last"}
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
        k, v = k.strip(), v.strip()
        if k in DATE_KEYS and v and not parse_date(v):
            die(f"{k} must be a date YYYY-MM-DD")
        if k == "phone" and v and len(norm_phone(v)) < 10:
            die("phone needs at least ten digits")
        if k in ("website", "appointment_url", "review_link") and v and not re.match(r"https?://", v):
            die(f"{k} must start with http:// or https://")
        if k in BOOL_KEYS:
            data[k] = v.lower() in ("1", "yes", "true", "y")
        elif k in LIST_KEYS:
            data[k] = [x.strip() for x in v.split(",") if x.strip()]
        elif k in NESTED:
            sec, key = NESTED[k]
            cur = data[sec].get(key)
            try:
                if isinstance(cur, bool):
                    data[sec][key] = v.lower() in ("1", "yes", "true", "y")
                elif isinstance(cur, int):
                    data[sec][key] = int(float(v))
                elif isinstance(cur, float):
                    data[sec][key] = float(v)
                else:
                    data[sec][key] = v
            except ValueError:
                die(f"{k} must be a number")
        elif k == "type":
            if v not in TYPES:
                die(f"type must be one of {', '.join(TYPES)}")
            data[k] = v
        elif k == "eligible":
            if v not in ("yes", "no", "unsure"):
                die("eligible must be yes, no or unsure")
            data[k] = v
        elif k == "review_ask":
            if v not in ("yes", "no"):
                die("review_ask must be yes or no")
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
    if a.n < 1:
        die("--n must be 1 or more")
    if a.type == "review" and a.note:
        die("no notes on a review entry: names and details stay out of this file; log the rating and the date only")
    entry = {"date": when, "type": a.type, "n": a.n, "note": a.note or ""}
    if a.type == "review":
        if a.rating is None or not 1 <= a.rating <= 5:
            die("a review needs --rating 1..5")
        entry["rating"] = a.rating
        data["reviews"]["count"] += a.n
        data["reviews"]["last_review"] = max(data["reviews"].get("last_review") or "", when)
        if not a.replied:
            data["reviews"]["unanswered"] += a.n
    if a.type == "reply":
        data["reviews"]["unanswered"] = max(0, data["reviews"]["unanswered"] - a.n)
        if data["reviews"]["unanswered"] == 0:
            data["reviews"]["oldest_unanswered_days"] = 0
    if a.type == "photo":
        data["photos"]["count"] += a.n
        data["photos"]["last"] = max(data["photos"].get("last") or "", when)
    if a.type == "post":
        data["posts"]["last"] = max(data["posts"].get("last") or "", when)
    data["log"].append(entry)
    save(data, p)
    print(json.dumps({"ok": True, "logged": entry}, indent=2, ensure_ascii=False))


def window(data, kind, days):
    since = TODAY() - timedelta(days=days)
    return sum(e.get("n", 1) for e in data["log"] if e["type"] == kind and parse_date(e["date"]) and parse_date(e["date"]) >= since)


def recent_ratings(data, days=90):
    since = TODAY() - timedelta(days=days)
    rs = [(e.get("rating"), e.get("n", 1)) for e in data["log"]
          if e["type"] == "review" and parse_date(e["date"]) and parse_date(e["date"]) >= since and e.get("rating")]
    tot = sum(n for _, n in rs)
    return (sum(r * n for r, n in rs) / tot) if tot else None, tot


def no_profile(data):
    return data.get("type") == "none" or data.get("eligible") == "no"


def core_for(data):
    return CORE_LISTINGS_REMOTE if data.get("type") == "none" else CORE_LISTINGS


def assess(data):
    """Return (items, score, critical_fail). Each item: key, group, ok, weight, note, fix."""
    items = []

    def item(key, group, ok, weight, note, fix=""):
        items.append({"key": key, "group": group, "ok": bool(ok), "weight": weight, "note": note, "fix": fix if not ok else ""})

    if no_profile(data):
        return items, None, False
    rv, ph = data["reviews"], data["photos"]
    ask = data.get("review_ask", "yes") == "yes"
    # rank: what the 2026 ranking-factor survey puts first
    item("eligible", "rank", data.get("eligible") == "yes", 10, "the business meets customers in person (at your place or theirs)",
         "confirm eligibility (`set eligible=yes`); a virtual office or a remote practice gets suspended, use listings and answer pages instead")
    item("verified", "rank", data.get("owner_verified"), 6, "profile verified by the owner", "finish verification (video is the usual route) before anything else")
    item("real_name", "rank", not stuffed_name(data.get("business", ""), data.get("legal_name", ""), data.get("primary_category", "")), 8,
         "the name is the real-world name from signage and invoices, no category, place or superlative added",
         "remove the added words; a stuffed name is a leading suspension cause and competitors report it")
    item("primary_category", "rank", bool(data.get("primary_category")), 10, "primary category set (the strongest ranking factor you control)",
         "pick the one category that matches the money service; secondary categories for the rest")
    item("secondary_categories", "rank", len(data.get("secondary_categories", [])) <= 9, 2, "up to nine secondary categories, for services actually sold",
         "trim to the services you really sell")
    item("hours", "rank", data.get("hours_set"), 6, "hours set, and holiday hours kept current ('open now' is a filter and a ranking input)", "set hours, including holidays")
    item("service_area", "rank", data.get("type") == "storefront" or bool(data.get("service_area")), 3,
         "service area set (service-area and hybrid businesses)", "list the towns or a radius you really serve (up to 20 areas)")
    # reviews: about a fifth of local-pack weight in 2026, and the thing customers filter on
    ds_review = days_since(rv.get("last_review"))
    if ask:
        item("reviews_count", "reviews", rv.get("count", 0) >= 20, 6, "twenty or more reviews (about half of consumers skip a business under twenty)",
             "ask every client the same way, the day the work finishes, until you pass twenty")
        item("reviews_rating", "reviews", float(rv.get("rating") or 0) >= 4.5, 5, "rating 4.5 or higher (a third of consumers now require it)",
             "keep serving well; ask every client the same way; never gate or incentivise")
        item("reviews_recent", "reviews", ds_review is not None and ds_review <= 90, 5, "a review in the last 90 days (three in four consumers want recent ones)", "ask this week")
        item("review_link", "reviews", bool(data.get("review_link")) and bool(data.get("ask_method")), 3, "the review link and the ask method written down",
             "copy the 'get more reviews' link from the profile; decide how you ask (`set review_link=… ask_method=…`)")
    else:
        item("review_policy", "reviews", True, 3, "no review ask in this profession; unsolicited reviews stay up; replies never confirm a care relationship")
    item("reviews_answered", "reviews", rv.get("unanswered", 0) == 0 and rv.get("oldest_unanswered_days", 0) <= 7, 5,
         "every review answered within seven days, each reply written for that review", "reply to each open review today, in your own words, no template")
    burst = window(data, "review", BURST_DAYS)
    item("reviews_steady", "reviews", not (burst >= BURST_N and burst > window(data, "review-ask", 30)), 2,
         f"no unexplained spike ({BURST_N}+ reviews in {BURST_DAYS} days that your own asks do not account for; Google pauses reviews during spikes)",
         "log your asks; if the reviews are real and asked for, nothing to fix; if not, do not buy or swap reviews")
    # buyer items: completeness and conversion (they do not move rank)
    desc = data.get("description", "")
    item("description", "convert", 200 <= len(desc) <= 750 and not PROMO.search(desc), 4,
         "description 200 to 750 characters, plain, no links or promotions",
         "write what you do, for whom, where, since when; no URLs, prices or 'best'")
    item("services", "convert", len(data.get("services", [])) >= 3 and all(s.get("description") for s in data["services"]), 5,
         "at least three services, each with a description (Ask Maps reads these)", "add each service you sell with two sentences on who it is for")
    item("contact", "convert", bool(data.get("phone")) and bool(data.get("website")), 4, "phone and website set", "add the phone people can call and the site they can read")
    item("appointment", "convert", bool(data.get("appointment_url")), 3, "booking or appointment link set", "add the booking link (the same one the Decision Machine uses)")
    item("photos_count", "convert", ph.get("count", 0) >= 10, 3, "at least ten real photos (you, the team, the work, the place)", "add ten real photos; no stock")
    item("photos_recent", "convert", within(ph.get("last"), 30), 3, "a new real photo in the last 30 days (aim for every two weeks)", "add one real photo this week")
    item("post_recent", "convert", within(data["posts"].get("last"), 14), 2, "a post in the last 14 days (does not move rank; shows you are open and real)",
         "post one update: a job done, a question answered, a date")
    # listings
    live = {l["site"] for l in data.get("listings", []) if l.get("status") == "live"}
    core = core_for(data)
    core_done = [s for s in core if s in live]
    item("listings_core", "listings", len(core_done) >= 4, 3, f"at least four of the core free listings live ({len(core_done)} of {len(core)}: {', '.join(core)})",
         "claim the next listing on the list")
    item("listings_match", "listings", not listing_mismatches(data), 3, "name, address and phone identical everywhere", "fix the mismatched listings (`listings check` names them)")

    weight = sum(i["weight"] for i in items)
    got = sum(i["weight"] for i in items if i["ok"])
    score = round(100 * got / weight) if weight else 0
    critical = any(not i["ok"] for i in items if i["key"] in CRITICAL)
    return items, score, critical


def fix_order(items):
    fails = [i for i in items if not i["ok"]]
    return sorted(fails, key=lambda i: (0 if i["key"] in CRITICAL else 1, GROUP_ORDER[i["group"]], -i["weight"]))


def listing_mismatches(data):
    nap = data.get("nap", {})
    base_name = norm_text(nap.get("name") or data.get("business"))
    base_addr = norm_text(nap.get("address"))
    base_phone = nap.get("phone") or data.get("phone")
    out = []
    for l in data.get("listings", []):
        if l.get("status") not in ("live", "claimed"):
            continue
        probs = []
        if l.get("name") and base_name and norm_text(l["name"]) != base_name:
            probs.append("name")
        if l.get("address") and base_addr and norm_text(l["address"]) != base_addr:
            probs.append("address")
        if l.get("phone") and base_phone and not phones_match(l["phone"], base_phone):
            probs.append("phone")
        if probs:
            out.append({"site": l["site"], "mismatch": probs, "url": l.get("url", "")})
    return out


def cmd_check(a):
    data, _ = load(a.folder)
    items, score, critical = assess(data)
    if score is None:
        out = {"ok": True, "profile": "none",
               "note": "No Google Business Profile for this business (no in-person contact). Listings, the answer pages, LinkedIn and mentions do the work; "
                       "run `listings check` and `weekly`.",
               "listings_live": sorted(l["site"] for l in data["listings"] if l.get("status") == "live"),
               "core_missing": [s for s in core_for(data) if s not in {l["site"] for l in data["listings"] if l.get("status") == "live"}]}
        if a.md:
            Path(a.folder, "profile-check.md").write_text(f"# Profile check · {data['business']}\n\nChecked: {iso(TODAY())} · No Google Business Profile "
                                                          f"(no in-person contact).\n\nListings live: {', '.join(out['listings_live']) or 'none'} · "
                                                          f"still to claim: {', '.join(out['core_missing']) or 'none'}\n", encoding="utf-8")
            out["wrote"] = str(Path(a.folder, "profile-check.md"))
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    out = {"ok": not critical, "score": score, "critical_fail": critical,
           "groups": {g: {"ok": sum(1 for i in items if i["group"] == g and i["ok"]), "of": sum(1 for i in items if i["group"] == g)} for g in GROUP_ORDER},
           "fix_first": [{"item": i["key"], "group": i["group"], "fix": i["fix"]} for i in fix_order(items)][:5], "items": items,
           "review_velocity_30d": window(data, "review", 30), "asks_30d": window(data, "review-ask", 30)}
    if a.md:
        Path(a.folder, "profile-check.md").write_text(render_check_md(data, items, score, critical), encoding="utf-8")
        out["wrote"] = str(Path(a.folder, "profile-check.md"))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    sys.exit(1 if critical else 0)


def render_check_md(data, items, score, critical):
    lines = [f"# Profile check · {data['business']}", "", f"Checked: {iso(TODAY())} · Score: {score}/100 · "
             f"{'HOLD: a critical item fails' if critical else 'OK to keep building'}", "", "## Fix first", ""]
    lines += [f"- {i['key']} ({i['group']}): {i['fix']}" for i in fix_order(items)[:5]] or ["- nothing: every item passes"]
    lines += ["", "| Group | Item | OK | What good looks like | Fix |", "|---|---|---|---|---|"]
    for i in sorted(items, key=lambda i: GROUP_ORDER[i["group"]]):
        lines.append(f"| {i['group']} | {i['key']} | {'yes' if i['ok'] else 'NO'} | {i['note']} | {i['fix']} |")
    lines += ["", "Rank items come from the 2026 local ranking-factor survey (category, name, hours, service area, reviews; proximity you cannot change). "
              "Convert items do not move rank; they decide whether a person who sees you calls.", ""]
    return "\n".join(lines)


def cmd_weekly(a):
    data, _ = load(a.folder)
    tasks = []
    if no_profile(data):
        live = {l["site"] for l in data["listings"] if l.get("status") == "live"}
        missing = [s for s in core_for(data) if s not in live]
        if missing:
            tasks.append(f"Claim or check one listing: {missing[0]} (15 min).")
        else:
            tasks.append("Check one listing for accuracy (5 min).")
        tasks.append("Draft the next answer page from the question map (the week's main work).")
        tasks.append("Ask for one mention: a roundup, an association, a podcast, a partner page (20 min).")
        tasks.append("LinkedIn Engine day: the 20-minute routine, if the LinkedIn Engine is set up.")
    else:
        rv, ph = data["reviews"], data["photos"]
        if rv.get("unanswered", 0):
            tasks.append(f"Reply to {rv['unanswered']} open review(s) first, each in your own words (5 min each).")
        if data.get("review_ask", "yes") == "yes":
            asks = window(data, "review-ask", 7)
            tasks.append("Ask every client whose job finished this week, the same words, the same day; if that is more than you can send by hand, "
                         "the CRM sends it with consent on file (10 min). Log the asks." + (f" ({asks} logged so far this week.)" if asks else ""))
        else:
            tasks.append("No review ask in this profession. Leave unsolicited reviews up; reply without confirming a care relationship.")
        if not within(ph.get("last"), 14):
            tasks.append("Add one real photo: a job, the team, the place (3 min).")
        if not within(data["posts"].get("last"), 7):
            tasks.append("Post one update: a job done, a question you answered this week, a date (5 min).")
        if not data.get("hours_set"):
            tasks.append("Set your hours, including the next holiday (5 min).")
        stale = [s for s in data.get("services", []) if not s.get("description")]
        if stale:
            tasks.append(f"Write the description for {len(stale)} service(s) with none (5 min each).")
        if window(data, "update", 30) == 0:
            tasks.append("Open the profile and check name, category, hours and phone are still right; log `update` (3 min).")
    tasks.append("Check the website still loads on a phone and the booking link works (2 min).")
    print(json.dumps({"ok": True, "week_of": iso(TODAY()), "minutes": "about 30 for the profile; the page is the rest of the week's time", "tasks": tasks},
                     indent=2, ensure_ascii=False))


def cmd_listings(a):
    data, p = load(a.folder)
    if a.action == "add":
        if not a.site:
            die("listings add needs --site")
        if a.status not in LISTING_STATUSES:
            die(f"--status must be one of {', '.join(LISTING_STATUSES)}")
        if a.phone and len(norm_phone(a.phone)) < 10:
            die("--phone needs at least ten digits")
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
        missing = [s for s in core_for(data) if s not in live]
        stale = [l["site"] for l in data["listings"] if not within(l.get("checked"), 90)]
        base_missing = [k for k in ("phone", "address") if not (data.get("nap", {}).get(k) or (data.get("phone") if k == "phone" else ""))]
        out = {"ok": not mism, "mismatches": mism, "core_missing": missing, "not_checked_90_days": stale,
               "note": "Citations weigh little for rank now, but three of the top AI-visibility inputs are listing-type, and a wrong phone on a directory costs real calls."}
        if base_missing and data.get("type") != "none":
            out["note"] = f"Set the profile's own {' and '.join(base_missing)} first (`set …`) so listings can be compared. " + out["note"]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        sys.exit(1 if mism else 0)
    else:
        print(json.dumps({"ok": True, "listings": data["listings"]}, indent=2, ensure_ascii=False))


def cmd_report(a):
    data, _ = load(a.folder)
    items, score, critical = assess(data)
    rating90, n90 = recent_ratings(data)
    rep = {"business": data["business"], "date": iso(TODAY()), "profile": "none" if score is None else "yes", "score": score, "critical_fail": critical,
           "reviews": {"count": data["reviews"]["count"], "rating": data["reviews"]["rating"], "last_30_days": window(data, "review", 30),
                       "asks_last_30_days": window(data, "review-ask", 30), "rating_last_90_days": round(rating90, 2) if rating90 else None,
                       "unanswered": data["reviews"]["unanswered"]},
           "photos_last_30_days": window(data, "photo", 30), "posts_last_30_days": window(data, "post", 30),
           "listings_live": sorted(l["site"] for l in data["listings"] if l.get("status") == "live"),
           "listing_mismatches": listing_mismatches(data)}
    asks = rep["reviews"]["asks_last_30_days"]
    rep["ask_to_review"] = round(rep["reviews"]["last_30_days"] / asks, 2) if asks else None
    if a.md:
        head = "No Google Business Profile (no in-person contact)" if score is None else f"Score {score}/100" + (" · HOLD (critical item)" if critical else "")
        lines = [f"# Profile report · {data['business']} · {rep['date']}", "", head, ""]
        if score is not None:
            lines += [f"- Reviews: {rep['reviews']['count']} at {rep['reviews']['rating']} · {rep['reviews']['last_30_days']} new in 30 days from {asks} asks"
                      + (f" ({rep['ask_to_review']:.0%} of asks)" if rep["ask_to_review"] is not None else "") + f" · {rep['reviews']['unanswered']} unanswered",
                      f"- Photos added in 30 days: {rep['photos_last_30_days']} · Posts in 30 days: {rep['posts_last_30_days']}"]
        lines += [f"- Listings live: {', '.join(rep['listings_live']) or 'none'}", f"- Listing mismatches: {len(rep['listing_mismatches'])}", ""]
        if items:
            lines += ["## Fix first", ""] + [f"- {i['key']}: {i['fix']}" for i in fix_order(items)[:5]] + [""]
        out = Path(a.folder, "profile-report.md")
        out.write_text("\n".join(lines), encoding="utf-8")
        rep["wrote"] = str(out)
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default="search")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, f):
        s = sub.add_parser(name)
        s.add_argument("--folder", dest="folder_sub", default=None)
        s.set_defaults(f=f)
        return s
    s = sp("init", cmd_init); s.add_argument("--name", required=True); s.add_argument("--legal-name", required=True); s.add_argument("--type", default="service-area")
    s.add_argument("--category", default=""); s.add_argument("--force", action="store_true")
    s = sp("set", cmd_set); s.add_argument("pairs", nargs="+")
    s = sp("service", cmd_service); s.add_argument("action", choices=("add", "remove")); s.add_argument("name"); s.add_argument("--description", default="")
    s = sp("log", cmd_log); s.add_argument("type"); s.add_argument("--n", type=int, default=1); s.add_argument("--rating", type=int, default=None)
    s.add_argument("--replied", action="store_true"); s.add_argument("--date", default=""); s.add_argument("--note", default="")
    s = sp("check", cmd_check); s.add_argument("--md", action="store_true")
    sp("weekly", cmd_weekly)
    s = sp("listings", cmd_listings); s.add_argument("action", choices=("add", "check", "list")); s.add_argument("--site", default="")
    s.add_argument("--url", default=""); s.add_argument("--name", default=""); s.add_argument("--address", default=""); s.add_argument("--phone", default="")
    s.add_argument("--status", default="live")
    s = sp("report", cmd_report); s.add_argument("--md", action="store_true")
    a = ap.parse_args(argv)
    if getattr(a, "folder_sub", None):
        a.folder = a.folder_sub
    a.f(a)


if __name__ == "__main__":
    main()
