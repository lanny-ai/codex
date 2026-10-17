#!/usr/bin/env python3
"""Event Launcher plan: the reverse funnel (how many people a goal needs) and the backward timeline.

Local only. It never contacts Zoom, GoHighLevel, Stripe or anything else: it does arithmetic on the
numbers the member gives and on labelled benchmark ranges, and it writes dates. Every benchmark it uses
carries a source key (for example "Scale For Impact 2026" or "Build Room assumption") that is printed
with the result, with a one-line description under "sources".

Usage
  launch_plan.py math --goal-buyers N | --goal-cash X   (one or both; both: the larger buyer count wins)
                      --price P | --tiers "Name:price:share" ["Name:price:share" ...]
                      --list-size L --format bootcamp3|challenge5|workshop|webinar [--days N] [--paid-event]
                      [--history-reg-rate R] [--history-showup R] [--md [FILE]] [--out DIR]
      Reverse funnel in three scenarios (cautious / typical / strong):
        list → registrants → live Day 1 → day-over-day retention → final-day live → present at the close
        → saw the price → buyers.
      share in --tiers is the tier's share of buyers (0.7, 70 or 70%); shares must add up to 100%. The
      conversion band is set by the share-weighted average price. Rates (--history-*) take 0.12, 12 or 12%.
      Prints the needed registrants and list size per scenario, the expected buyers from --list-size, a
      verdict (reachable / stretch / not from this list alone: add partners/ads or lower the goal) and the
      single biggest lever. --md prints a markdown table instead of JSON (--md FILE writes it and prints
      the JSON). --out DIR writes (or updates) DIR/plan.json, which launch_tracker.py init --plan reads.

  launch_plan.py timeline --event-date YYYY-MM-DD --days N --tz IANA [--partners] [--paid-event]
                          [--cart-days 3] [--rush] [--out DIR] [--date YYYY-MM-DD]
      Backward schedule from Day 1: decide and test the offer, partner recruitment (--partners: 12 weeks
      out, 8 weeks minimum, Amber Spears' 90-day rule), proof bank, pages and checkout, the launch gate,
      invitations (about 14 days out; 21 for a paid event), reminders, the event days with their
      night-before recaps, the checkout test on the close morning, cart close, the replay window (about
      7 days), follow-up and the debrief. Each milestone has its date and weekday.
      Refused (exit 2) when Day 1 is closer than the plan's minimum (14 days; 21 paid; 8 weeks with
      --partners) unless --rush, which compresses the late milestones to today and says so.
      --out DIR writes DIR/plan.json (merged with math) and DIR/calendar.md. --date replays "today".

Standard library only. Exit code 2 on a refused action (bad or missing input, impossible date).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, json, math, os, re, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: E402

PLAN_SCHEMA = "buildroom-event-launcher/plan-1"
FORMATS = {"bootcamp3": 3, "challenge5": 5, "workshop": 1, "webinar": 1}
SCENARIOS = ("cautious", "typical", "strong")

SOURCES = {
    "ON24 2025": "ON24 Digital Engagement Benchmarks (2024–25 data): 57–60% of registrants attend, live and "
                 "on-demand counted together; B2B. An upper reference, not a small-list norm",
    "Livestorm 2026": "Livestorm 2026 Webinar Benchmark (2025 data, 33,786 sessions): 51.3% show-up; 49.6% of "
                      "registrations arrive in the final week and 15.3% on the day",
    "Scale For Impact 2026": "Scale For Impact webinar benchmarks (agency data, 114 webinars, $100M+ sales, course "
                             "creators): about 25% live show-up; attendee-to-buyer 8–15% at $97–497, 5–10% at "
                             "$500–1,500, 1–4% at $2,000+",
    "Pheedloop 2026": "Pheedloop Event Data Lab #05 (1,070+ in-person events): median no-show 28% free vs 17% paid",
    "HSH 2025": "Heart, Soul & Hustle paid bootcamp (practitioner self-report): 51.8% retained Day 1 to Day 5 "
                "(144 of 278), about 85% a day; 17.66–19.2% of paid participants bought the membership",
    "Build Room founder run Jul 2026": "Founder's free 3-day bootcamp, Jul 2026: 969 registered, 380 / 257 / 133 live, "
                                       "67 at the very end; Day-1 show-up 39.2%; 380 to 133 over two days is about "
                                       "59% a day; 56% of those who saw the price bought (23 of 41, after a $1 "
                                       "first purchase); about $25.6 cash and $54 booked per registrant",
    "Build Room founder runs 2025–26": "Founder's earlier free bootcamps: Day-1 show-up averaged about 33% of registrants",
    "Build Room founder rule of thumb": "Founder, Aug 2026 debrief: Day 2 is about 80% of Day 1 and Day 3 about 80% "
                                        "of Day 2 (his July data ran lower; the audit says earlier camps ran about "
                                        "50% Day 1 to Day 2)",
    "Build Room planning range 2026": "Derived planning range in the Build Room research (best practices 2026): free "
                                      "challenge Day 1 15–35% of registrants, free webinar to a warm list 30–45%, "
                                      "paid $27–97 event 50–70%; buyers about 15–20% of paid-event participants",
    "Build Room assumption": "No published benchmark exists for this step: a labelled Build Room planning "
                             "assumption. Replace it with your own numbers after one run",
    "Member history": "The member's own number from a past event (--history-reg-rate / --history-showup); "
                      "cautious and strong are 80% and 120% of it",
    "Amber Spears 2018": "Amber Spears, Flight Club Mar 2018: 'I need 90 days to recruit… the big people are "
                         "booked'; never launch an untested offer; recruit in waves, biggest first",
    "Build Room founder method": "Founder's method (vault notes): belief before the invite, proof on Day 2, a "
                                 "Day-1-night and Day-2-night email, test checkout on the close morning, replays "
                                 "about 7 days, follow-up by segment, a written debrief",
    "GHL help 2026": "HighLevel help: A2P 10DLC brand and campaign must be approved before US texting",
}


def rng(c, t, s, source, note=""):
    return {"cautious": c, "typical": t, "strong": s, "source": source, **({"note": note} if note else {})}


# Registration rate of the list: research found no benchmark (best practices 2026, Gaps).
REG_RATE = {
    "free": rng(.10, .20, .30, "Build Room assumption",
                "share of the member's own list that registers; the research planning band is 10–30% for a warm "
                "list. The founder's partner-list run was 0.61% of about 160,000 mostly cold names"),
    "paid": rng(.03, .06, .10, "Build Room assumption", "share of the list that buys a ticket"),
}
SHOW_UP = {
    ("free", "multi"): {"bootcamp3": [(.25, "Scale For Impact 2026"), (.33, "Build Room founder runs 2025–26"),
                                      (.39, "Build Room founder run Jul 2026")],
                        "challenge5": [(.15, "Build Room planning range 2026"), (.25, "Build Room planning range 2026"),
                                       (.35, "Build Room planning range 2026")]},
    ("free", "single"): [(.30, "Build Room planning range 2026"), (.38, "Build Room planning range 2026"),
                         (.45, "Build Room planning range 2026")],
    ("paid", None): [(.50, "Build Room planning range 2026"), (.60, "Build Room planning range 2026"),
                     (.70, "Pheedloop 2026")],
}
RETENTION = {   # share of yesterday's live attendees who come back live today
    "free": [(.59, "Build Room founder run Jul 2026"), (.70, "Build Room assumption"),
             (.80, "Build Room founder rule of thumb")],
    "paid": [(.70, "Build Room assumption"), (.85, "HSH 2025"), (.90, "Build Room assumption")],
}
STAY_TO_CLOSE = {   # share of the final day's live attendees still there when the offer is made
    "multi": [(.50, "Build Room founder run Jul 2026"), (.65, "Build Room assumption"), (.80, "Build Room assumption")],
    "single": [(.60, "Build Room assumption"), (.75, "Build Room assumption"), (.85, "Build Room assumption")],
}
# saw the price = present at the close × this (replay and cart emails show the offer to some who left early)
SAW_FACTOR = [(1.10, "Build Room assumption"), (1.25, "Build Room assumption"), (1.40, "Build Room assumption")]
SAW_NOTE = ("replay and cart emails show the price to some who missed the live close; this only happens when the "
            "follow-up is switched on (founder Jul 2026: 51 warm buyers never saw the offer)")
# conversion of those who saw the price, by price band (attendee-to-buyer, Scale For Impact 2026)
BANDS = [
    {"band": "under $500", "max": 500, "free": [.08, .115, .15], "paid": [.10, .15, .19],
     "source": "Scale For Impact 2026", "paid_source": "HSH 2025",
     "note": "Scale For Impact's lowest band is $97–497; offers under $97 use it too (Build Room assumption)"},
    {"band": "$500–1,999", "max": 2000, "free": [.05, .075, .10], "paid": [.05, .075, .10],
     "source": "Scale For Impact 2026", "paid_source": "Scale For Impact 2026",
     "note": "Scale For Impact measured $500–1,500; $1,500–1,999 is placed here (Build Room assumption)"},
    {"band": "$2,000 and up", "max": None, "free": [.01, .025, .04], "paid": [.01, .025, .04],
     "source": "Scale For Impact 2026", "paid_source": "Scale For Impact 2026",
     "note": "above about $2,000, send people to an application or a call rather than straight to checkout"},
]
LEVERS = {
    "registration": "Registrations: invite more of the list, earlier and more often (about half of registrations "
                    "land in the final week), add a partner wave, keep registration open through Day 1",
    "show_up": "Day-1 show-up: calendar file on the thank-you page, reminders the day before, the morning of and "
               "15 minutes before (email, and SMS with consent), pre-work that makes being live worth it",
    "retention": "Day-over-day retention: a Day-1-night and Day-2-night email with tomorrow's payoff, a cliffhanger "
                 "that only pays off live, reminder times verified in the recipient's time zone",
    "stay_to_close": "Staying to the close: say when the offer comes, keep the promised build for after it, keep the "
                     "session inside the planned length",
    "saw_price": "Seeing the price: switch on the follow-up that shows the offer to every attendee (replay with the "
                 "offer, cart emails) before the event starts",
    "conversion": "Conversion: checkout tested on a phone the morning of the close (payment plan, coupon), a plan "
                  "that doesn't punish, a real deadline, a clear 'which one are you' ladder, let ready buyers buy",
}


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


def parse_date(s, what="--date"):
    try:
        return dt.date.fromisoformat(str(s).strip())
    except (TypeError, ValueError):
        refuse(f"{what} must be a real date as YYYY-MM-DD (got {s!r})")


def today(a=None):
    d = getattr(a, "date", None) if a else None
    return parse_date(d) if d else dt.date.today()


def check_tz(name, what="--tz"):
    try:
        return ZoneInfo(str(name))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        refuse(f"{what} must be an IANA time zone such as America/New_York (got {name!r})")


def money(s, what):
    try:
        v = float(str(s).replace("$", "").replace(",", "").strip())
    except ValueError:
        refuse(f"{what} must be a number (got {s!r})")
    if v <= 0:
        refuse(f"{what} must be more than 0 (got {s!r})")
    return v


def rate(s, what):
    """0.12, 12 or 12% → 0.12."""
    try:
        v = float(str(s).replace("%", "").strip())
    except ValueError:
        refuse(f"{what} must be a rate such as 0.12 or 12% (got {s!r})")
    if v > 1:
        v /= 100
    if not 0 < v <= 1:
        refuse(f"{what} must be between 0 and 100% (got {s!r})")
    return v


def parse_tiers(items):
    tiers = []
    for t in items:
        parts = str(t).rsplit(":", 2)
        if len(parts) != 3 or not parts[0].strip():
            refuse(f"--tiers takes \"Name:price:share\" (got {t!r})")
        tiers.append({"name": parts[0].strip(), "price": money(parts[1], f"tier {parts[0]} price"),
                      "share": rate(parts[2], f"tier {parts[0]} share")})
    total = sum(x["share"] for x in tiers)
    if abs(total - 1) > .02:
        refuse(f"tier shares add up to {total:.0%}; they are each tier's share of buyers and must add up to 100%")
    for x in tiers:
        x["share"] = x["share"] / total
    return tiers


def band_for(price):
    return next(b for b in BANDS if b["max"] is None or price < b["max"])


def triple(vals, scenario):
    return vals[SCENARIOS.index(scenario)]


def rates_for(fmt, days, paid, price, hist_reg=None, hist_show=None):
    """{stage: {cautious, typical, strong, source(s)}} for the funnel steps of this event."""
    kind = "paid" if paid else "free"
    multi = days > 1
    out = {}
    if hist_reg:
        out["registration"] = rng(round(hist_reg * .8, 4), hist_reg, round(min(1, hist_reg * 1.2), 4), "Member history")
    else:
        out["registration"] = REG_RATE[kind]
    if hist_show:
        out["show_up"] = rng(round(hist_show * .8, 4), hist_show, round(min(1, hist_show * 1.2), 4), "Member history")
    else:
        if paid:
            vals = SHOW_UP[("paid", None)]
        elif multi:
            vals = SHOW_UP[("free", "multi")].get(fmt, SHOW_UP[("free", "multi")]["challenge5"])
        else:
            vals = SHOW_UP[("free", "single")]
        out["show_up"] = per_value(vals, "registrants who come live on Day 1" + (
            "; ON24 2025 and Livestorm 2026 report 50–60%, counted on wider definitions" if not paid and not multi else ""))
    if multi:
        out["retention"] = per_value(RETENTION[kind], f"each day's live share of the day before, applied {days - 1} times")
    out["stay_to_close"] = per_value(STAY_TO_CLOSE["multi" if multi else "single"],
                                     "final-day live attendees still there when the offer is made")
    out["saw_price"] = per_value(SAW_FACTOR, SAW_NOTE)
    b = band_for(price)
    src = b["paid_source"] if paid else b["source"]
    out["conversion"] = rng(*b[kind], src, f"{b['band']}: {b['note']}" + (
        "; paid-event participants convert higher (Build Room planning range 2026: 15–20%)" if paid and b["max"] == 500 else ""))
    out["conversion"]["band"] = b["band"]
    return out


def per_value(vals, note):
    srcs = [s for _, s in vals]
    r = rng(vals[0][0], vals[1][0], vals[2][0], srcs[1] if len(set(srcs)) == 1 else dict(zip(SCENARIOS, srcs)), note)
    return r


def chain(rates, days, scenario):
    """The stage multipliers for one scenario, in funnel order (registration first)."""
    g = {k: v[scenario] for k, v in rates.items()}
    return g


def reverse(buyers, g, days):
    """Needed counts (floats), working backwards from buyers."""
    saw = buyers / g["conversion"]
    present = saw / g["saw_price"]
    final_live = present / g["stay_to_close"]
    ret = g.get("retention", 1.0)
    day_live = [final_live / ret ** (days - 1 - i) for i in range(days)]
    regs = day_live[0] / g["show_up"]
    lst = regs / g["registration"]
    return {"buyers": buyers, "saw_price": saw, "present_at_close": present, "day_live": day_live,
            "registrants": regs, "list": lst}


def forward(list_size, g, days):
    regs = list_size * g["registration"]
    d1 = regs * g["show_up"]
    ret = g.get("retention", 1.0)
    day_live = [d1 * ret ** i for i in range(days)]
    present = day_live[-1] * g["stay_to_close"]
    saw = present * g["saw_price"]
    return {"registrants": regs, "day_live": day_live, "present_at_close": present, "saw_price": saw,
            "buyers": saw * g["conversion"]}


def ceil_all(d):
    return {k: ([math.ceil(round(x, 6)) for x in v] if isinstance(v, list) else math.ceil(round(v, 6))) for k, v in d.items()}


def round_all(d, n=1):
    return {k: ([round(x, n) for x in v] if isinstance(v, list) else round(v, n)) for k, v in d.items()}


def sources_used(obj):
    keys = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "source":
                    if isinstance(v, dict):
                        keys.update(v.values())
                    else:
                        keys.add(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return {k: SOURCES[k] for k in sorted(keys) if k in SOURCES}


def biggest_lever(rates, days):
    gains = {}
    for k, v in rates.items():
        if not v["typical"]:
            continue
        g = v["strong"] / v["typical"]
        if k == "retention":
            g = g ** (days - 1)
        gains[k] = g
    best = max(gains, key=lambda k: (gains[k], k))
    return {"stage": best, "gain_if_strong": round(gains[best], 2), "how": LEVERS[best],
            "all_gains": {k: round(v, 2) for k, v in sorted(gains.items(), key=lambda kv: -kv[1])},
            "note": "the stage whose move from typical to strong adds the most buyers, everything else held at typical"}


def verdict(list_size, needed):
    if list_size >= needed["typical"]["list"]:
        return "reachable"
    if list_size >= needed["strong"]["list"]:
        return "stretch"
    return "not from this list alone: add partners/ads or lower the goal"


def compute_math(goal_buyers=None, goal_cash=None, price=None, tiers=None, list_size=None, fmt="bootcamp3",
                 days=None, paid=False, hist_reg=None, hist_show=None):
    """The math result as a dict (also used by launch_tracker.py when no plan.json is given)."""
    if fmt not in FORMATS:
        refuse(f"--format must be one of {sorted(FORMATS)}")
    days = days or FORMATS[fmt]
    if days < 1:
        refuse("--days must be 1 or more")
    if tiers:
        avg = sum(t["price"] * t["share"] for t in tiers)
    elif price:
        avg = price
    else:
        refuse("a price is needed: --price P or --tiers \"Name:price:share\" (the price sets the conversion band)")
    if not goal_buyers and not goal_cash:
        refuse("a goal is needed: --goal-buyers N or --goal-cash X")
    from_cash = math.ceil(round(goal_cash / avg, 6)) if goal_cash else None
    buyers = max(x for x in (goal_buyers, from_cash) if x)
    binds = "goal-cash" if from_cash and (goal_buyers is None or from_cash > goal_buyers) else "goal-buyers"
    rates = rates_for(fmt, days, paid, avg, hist_reg, hist_show)
    scen, warnings = {}, []
    for s in SCENARIOS:
        g = chain(rates, days, s)
        need = reverse(buyers, g, days)
        row = {"rates": {k: v for k, v in g.items()}, "needed": ceil_all(need), "needed_exact": round_all(need)}
        if list_size:
            row["expected_from_list"] = round_all(forward(list_size, g, days))
        scen[s] = row
    out = {"inputs": {"goal_buyers": goal_buyers, "goal_cash": goal_cash, "price": price, "tiers": tiers,
                      "list_size": list_size, "format": fmt, "days": days, "paid_event": bool(paid),
                      "history_reg_rate": hist_reg, "history_showup": hist_show},
           "goal": {"buyers": buyers, "binding": binds, "average_price": round(avg, 2),
                    "booked_at_goal": round(buyers * avg, 2)},
           "price_band": rates["conversion"]["band"], "rates": rates, "scenarios": scen}
    if list_size:
        out["verdict"] = verdict(list_size, {s: scen[s]["needed"] for s in SCENARIOS})
    out["lever"] = biggest_lever(rates, days)
    if avg >= 2000:
        warnings.append("average price is $2,000 or more: direct checkout converts 1–4% (Scale For Impact 2026); plan "
                        "an application or a booked call as the close, and track call show and close rates")
    if rates["registration"]["source"] == "Build Room assumption":
        warnings.append("the registration rate of the list has no published benchmark: it is a Build Room assumption. "
                        "Give --history-reg-rate from a past event if you have one")
    if tiers and len({band_for(t['price'])['band'] for t in tiers}) > 1:
        warnings.append(f"tiers span more than one price band; the conversion band comes from the share-weighted "
                        f"average price (${avg:,.0f})")
    out["notes"] = ["saw the price can exceed present at the close: the replay and cart emails show the price to some "
                    "who left early",
                    "money is booked revenue at the average price; payment plans collect less cash up front"]
    if warnings:
        out["warnings"] = warnings
    out["sources"] = sources_used(out["rates"])
    return out


def pct(x):
    return f"{x * 100:.1f}%".replace(".0%", "%")


def math_md(r):
    d = r["inputs"]["days"]
    lines = [f"# Launch math: {r['goal']['buyers']} buyers at ${r['goal']['average_price']:,.0f} "
             f"({r['inputs']['format']}, {d} day{'s' if d > 1 else ''}, {'paid' if r['inputs']['paid_event'] else 'free'})", "",
             "| Stage | Cautious | Typical | Strong | Source |", "|---|---|---|---|---|"]
    def src(k):
        s = r["rates"][k]["source"]
        return " / ".join(dict.fromkeys(s.values())) if isinstance(s, dict) else s
    labels = [("registration", "Registration rate of list"), ("show_up", "Day-1 show-up"),
              ("retention", "Day-over-day retention"), ("stay_to_close", "Stay to the close"),
              ("saw_price", "Saw the price (× present)"), ("conversion", f"Conversion ({r['price_band']})")]
    for k, label in labels:
        if k in r["rates"]:
            v = r["rates"][k]
            fmtv = (lambda x: f"×{x:.2f}") if k == "saw_price" else pct
            lines.append(f"| {label} | {fmtv(v['cautious'])} | {fmtv(v['typical'])} | {fmtv(v['strong'])} | {src(k)} |")
    lines += ["", "| Needed | Cautious | Typical | Strong |", "|---|---|---|---|"]
    sc = r["scenarios"]
    rows = [("Buyers", "buyers"), ("Saw the price", "saw_price"), ("Present at the close", "present_at_close")]
    for label, k in rows:
        lines.append(f"| {label} | " + " | ".join(f"{sc[s]['needed'][k]:,}" for s in SCENARIOS) + " |")
    for i in range(d - 1, -1, -1):
        lines.append(f"| Live Day {i + 1} | " + " | ".join(f"{sc[s]['needed']['day_live'][i]:,}" for s in SCENARIOS) + " |")
    lines.append("| **Registrants** | " + " | ".join(f"**{sc[s]['needed']['registrants']:,}**" for s in SCENARIOS) + " |")
    lines.append("| **List size** | " + " | ".join(f"**{sc[s]['needed']['list']:,}**" for s in SCENARIOS) + " |")
    if r["inputs"]["list_size"]:
        lines.append(f"| Expected buyers from {r['inputs']['list_size']:,} | "
                     + " | ".join(f"{sc[s]['expected_from_list']['buyers']:.1f}" for s in SCENARIOS) + " |")
        lines += ["", f"**Verdict:** {r['verdict']}"]
    lines += ["", f"**Biggest lever:** {r['lever']['stage']} (×{r['lever']['gain_if_strong']} if it reaches strong). "
              f"{r['lever']['how']}."]
    for w in r.get("warnings", []):
        lines.append(f"- ⚠️ {w}")
    lines += ["", "Sources:"] + [f"- **{k}**: {v}" for k, v in r["sources"].items()]
    return "\n".join(lines) + "\n"


# ---------------- plan.json ----------------

def save_json(path, data):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".plan-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def update_plan(out_dir, key, value):
    p = Path(out_dir) / "plan.json"
    data = {"schema": PLAN_SCHEMA}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            refuse(f"{p} is not readable JSON ({e}); move it aside or fix it")
        if not isinstance(data, dict) or data.get("schema") != PLAN_SCHEMA:
            refuse(f"{p} exists and is not an Event Launcher plan file; choose another --out folder")
    data[key] = value
    save_json(p, data)
    return str(p)


# ---------------- timeline ----------------

def milestone_specs(days, partners, paid, cart_days):
    """(id, offset in days from Day 1, title, detail, source). Offsets for the event days are added later."""
    inv = -21 if paid else -14
    decide = -98 if partners else (-49 if paid else -42)
    m = [("decide", decide, "Decide and test the offer",
          "Decide the offer, the one belief and the format; test the offer with a pilot, past clients or a small "
          "paid beta before anyone promotes it", "Amber Spears 2018")]
    if partners:
        m += [("partner_recruit", -84, "Partner recruitment starts",
               "12 weeks out (8 weeks at the latest): own network first, then partners one-on-one biggest first, then "
               "ask each yes for an introduction; ask each what a good result looks like", "Amber Spears 2018"),
              ("partner_terms", -56, "Partner deals in writing",
               "Dates, what they promote, commission or swap, who owns the leads, what happens if it underperforms; "
               "partners disclose their commission", "Amber Spears 2018"),
              ("partner_kit", -28, "Partner kit out",
               "Two emails, two posts, tracking links, disclosure wording; copy names who teaches live",
               "Build Room founder method")]
    m += [("proof_bank", -28, "Proof bank classified",
           "Classify every story (free-event result / paid-program / outside), get consents, typical results only",
           "Build Room founder method"),
          ("a2p", -28, "SMS registration (if you will text)",
           "A2P 10DLC brand and campaign submitted; approval can take weeks", "GHL help 2026"),
          ("pages_built", inv - 7, "Pages and checkout built",
           "Registration and thank-you page with the calendar file, checkout with payment plan and refund terms, "
           "replay page, follow-up workflows drafted", "Build Room founder method"),
          ("belief_emails", inv - 7, "Belief emails start",
           "Three belief emails (opportunity, identity, mechanism) before the invitation; no offer yet",
           "Build Room founder method"),
          ("launch_gate", inv - 2, "Launch gate",
           "launch_tracker.py gate shows GO before the first invitation goes out", "Build Room founder method"),
          ("invites_start", inv, "Invitations start",
           "About 14 days out (21 for a paid event); keep promoting through Day 1: about half of registrations "
           "arrive in the final week and 15% on the day", "Livestorm 2026"),
          ("reminder_dry_run", -1, "Reminder dry run",
           "Send every reminder to a test contact in the recipient's time zone (event_ics.py reminders) and check "
           "the times; reminders fired hours early in the founder's July run", "Build Room founder run Jul 2026"),
          ("day_before", -1, "Day-before email", "How to prepare, the calendar file again, the one pre-work action",
           "Build Room founder method")]
    for k in range(1, days + 1):
        m.append((f"day{k}", k - 1, f"Day {k} live" + (" (close day)" if k == days else ""),
                  "Morning-of and 15-minute reminders; recording notice at the start", "Build Room founder method"))
        if k >= 2:
            m.append((f"day{k - 1}_night", k - 2, f"Day-{k - 1}-night recap",
                      f"Recap of Day {k - 1} plus the Day-{k} payoff; the founder's July run had none and lost people",
                      "Build Room founder run Jul 2026"))
    f = days - 1
    m += [("checkout_test", f, "Checkout test (close morning)",
           "Test every checkout path end to end on a phone: full pay, payment plan, coupon; backup link ready",
           "Build Room founder run Jul 2026"),
          ("replay_sent", f + 1, "Replay out and buyers onboarded",
           "Replay within hours; buyers get access and a welcome within 24 hours", "Build Room founder method"),
          ("cart_close", f + cart_days, "Cart closes",
           "A real deadline, the same for everyone (or honest per-person timers); no reopen", "Build Room founder method"),
          ("replay_closes", f + 7, "Replay window closes", "Replays run about 7 days", "Build Room founder method")]
    close = max(f + cart_days, f + 7)
    m += [("followup", f + cart_days + 1, "Follow-up by segment",
           "Attended and didn't buy, no-shows (send the tool, not the replay), bought: five emails over ten days, "
           "then stop", "Build Room founder method"),
          ("debrief", close + 2, "Debrief",
           "launch_tracker.py report, then launch_tracker.py obsidian to file the lessons", "Build Room founder method")]
    return m


def cmd_timeline(a):
    on = today(a)
    ev = parse_date(a.event_date, "--event-date")
    check_tz(a.tz)
    if a.days < 1:
        refuse("--days must be 1 or more")
    if a.cart_days < 0:
        refuse("--cart-days must be 0 or more")
    lead = (ev - on).days
    if lead < 0:
        refuse(f"--event-date {ev} is in the past (today is {on})")
    minimum = 56 if a.partners else (21 if a.paid_event else 14)
    why = ("8 weeks to recruit partners (Amber Spears: 90 days; big partners are booked months ahead)" if a.partners
           else "21 days for a paid event's ticket sales" if a.paid_event else "about 14 days of invitations")
    if lead < minimum and not a.rush:
        refuse(f"Day 1 ({ev}) is {lead} days away; this plan needs at least {minimum} days ({why}). Move the date, or "
               f"pass --rush to compress the plan (milestones before today move to today)")
    ms, warnings = [], []
    for mid, off, title, detail, src in milestone_specs(a.days, a.partners, a.paid_event, a.cart_days):
        d = ev + dt.timedelta(days=off)
        row = {"id": mid, "date": d.isoformat(), "weekday": d.strftime("%a"), "days_from_day1": off,
               "title": title, "detail": detail, "source": src}
        if d < on:
            row.update({"date": on.isoformat(), "weekday": on.strftime("%a"), "compressed": True, "planned": d.isoformat()})
        ms.append(row)
    comp = [m["id"] for m in ms if m.get("compressed")]
    if comp:
        warnings.append(f"compressed to today ({on}): {', '.join(comp)}; these were due earlier")
    if a.partners and lead < 84:
        warnings.append(f"partner recruitment has {lead} days, under the 12 weeks planned (Amber Spears' 90-day rule): "
                        "expect fewer and smaller partner slots")
    if lead < minimum:
        warnings.append(f"--rush: {lead} days is under the {minimum}-day minimum ({why})")
    for m in ms:
        if m["id"].startswith("day") and m["id"][3:].isdigit() and dt.date.fromisoformat(m["date"]).weekday() >= 5:
            warnings.append(f"{m['title']} falls on a {m['weekday']}: check your audience can make a weekend session")
    order = {m[0]: i for i, m in enumerate(milestone_specs(a.days, a.partners, a.paid_event, a.cart_days))}
    slot = lambda i: 0 if i in ("checkout_test", "reminder_dry_run") else 2 if i.endswith("_night") else 1   # morning / day / evening
    ms.sort(key=lambda m: (m["date"], m.get("planned", m["date"]), slot(m["id"]), order[m["id"]]))
    final = ev + dt.timedelta(days=a.days - 1)
    out = {"event_date": ev.isoformat(), "days": a.days, "tz": a.tz, "final_day": final.isoformat(),
           "cart_close": (final + dt.timedelta(days=a.cart_days)).isoformat(), "today": on.isoformat(),
           "lead_days": lead, "minimum_lead_days": minimum, "partners": bool(a.partners), "paid_event": bool(a.paid_event),
           "milestones": ms}
    if warnings:
        out["warnings"] = warnings
    out["sources"] = sources_used(ms)
    if a.out:
        out["written"] = [update_plan(a.out, "timeline", out)]
        cal = Path(a.out) / "calendar.md"
        cal.write_text(calendar_md(out), encoding="utf-8")
        out["written"].append(str(cal))
    return out


def calendar_md(t):
    ev = dt.date.fromisoformat(t["event_date"])
    lines = [f"# Launch calendar: Day 1 {ev.strftime('%a')} {ev} ({t['days']} day{'s' if t['days'] > 1 else ''}, {t['tz']})", ""]
    week = None
    for m in t["milestones"]:
        d = dt.date.fromisoformat(m["date"])
        monday = d - dt.timedelta(days=d.weekday())
        if monday != week:
            week = monday
            n = (ev - monday).days // 7
            label = ("after the event" if monday > ev else "event week" if (ev - monday).days < 7
                     else f"{n} week{'s' if n != 1 else ''} out")
            lines += ["", f"## Week of Mon {monday} ({label})", "", "| Date | Day | Milestone | What |", "|---|---|---|---|"]
        flag = f" ⚠️ compressed (planned {m['planned']})" if m.get("compressed") else ""
        lines.append(f"| {m['date']} | {m['weekday']} | **{m['title']}**{flag} | {m['detail']} |")
    for w in t.get("warnings", []):
        lines.append(f"\n- ⚠️ {w}")
    lines += ["", "Sources:"] + [f"- **{k}**: {v}" for k, v in t["sources"].items()]
    return "\n".join(lines) + "\n"


def cmd_math(a):
    tiers = parse_tiers(a.tiers) if a.tiers else None
    if tiers and a.price:
        refuse("pass --price or --tiers, not both")
    price = money(a.price, "--price") if a.price else None
    if a.goal_buyers is not None and a.goal_buyers < 1:
        refuse("--goal-buyers must be 1 or more")
    cash = money(a.goal_cash, "--goal-cash") if a.goal_cash else None
    if a.list_size is None or a.list_size < 1:
        refuse("--list-size must be 1 or more (the number of people on the member's own list)")
    r = compute_math(a.goal_buyers, cash, price, tiers, a.list_size, a.format, a.days, a.paid_event,
                     rate(a.history_reg_rate, "--history-reg-rate") if a.history_reg_rate else None,
                     rate(a.history_showup, "--history-showup") if a.history_showup else None)
    if a.out:
        r["written"] = [update_plan(a.out, "math", r)]
    if a.md:
        md = math_md(r)
        if a.md == "-":
            sys.stdout.write(md)
            return None
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(md, encoding="utf-8")
        r.setdefault("written", []).append(a.md)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("math")
    s.add_argument("--goal-buyers", type=int); s.add_argument("--goal-cash"); s.add_argument("--price")
    s.add_argument("--tiers", nargs="+"); s.add_argument("--list-size", type=int)
    s.add_argument("--format", required=True, choices=sorted(FORMATS)); s.add_argument("--days", type=int)
    s.add_argument("--paid-event", action="store_true")
    s.add_argument("--history-reg-rate"); s.add_argument("--history-showup")
    s.add_argument("--md", nargs="?", const="-"); s.add_argument("--out"); s.add_argument("--date")
    s = sub.add_parser("timeline")
    s.add_argument("--event-date", required=True); s.add_argument("--days", type=int, required=True)
    s.add_argument("--tz", required=True); s.add_argument("--partners", action="store_true")
    s.add_argument("--paid-event", action="store_true"); s.add_argument("--cart-days", type=int, default=3)
    s.add_argument("--rush", action="store_true"); s.add_argument("--out"); s.add_argument("--date")
    a = ap.parse_args(argv)
    today(a)
    out = {"math": cmd_math, "timeline": cmd_timeline}[a.cmd](a)
    if out is not None:
        print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
