#!/usr/bin/env python3
"""Event Launcher plan: the reverse funnel (how many people a goal needs) and the backward timeline.

Local only. It never contacts Zoom, GoHighLevel, Stripe or anything else: it does arithmetic on the
numbers the member gives and on labelled benchmark ranges, and it writes dates. Every benchmark it uses
carries a source key (for example "Scale For Impact 2026" or "Build Room assumption") that is printed
with the result, with a one-line description under "sources".

Usage
  launch_plan.py math --goal-buyers N | --goal-cash X   (one or both; both: the larger buyer count wins)
                      --price P | --tiers "Name:price:share[:checkout|call]" [...]
                      --list-size L --format bootcamp3|challenge5|workshop|webinar|roundtable [--days N]
                      [--paid-event [--ticket-price T]] [--vip-price V [--vip-rate R]]
                      [--close checkout|call|both] [--replay-uplift X]
                      [--history-reg-rate R] [--history-showup R] [--history-retention R] [--history-stay R]
                      [--history-conversion R] [--history-booked R] [--history-held R] [--history-closed R]
                      [--md [FILE]] [--out DIR|SLUG]
      The typical path, worked backwards from the goal and forwards from the list:
        list → registrants → live Day 1 → day-over-day retention → final-day live → present at the close
        → saw the price → buyers                                              (--close checkout)
        … → saw the offer → calls booked (or applications) → calls held → closed  (--close call)
      One definition for the last step: the conversion bands (and the booking rate) apply to the people
      who SAW THE PRICE (the offer). "Saw the price" is present at the close × 1.0 unless --replay-uplift X
      (an optional Build Room assumption, for example 1.25, counting replay and cart-email viewers).
      --close call uses labelled ranges: 10–20% of those who saw the offer book (vendor/agency, weak),
      about 70–80% of booked calls are held (Build Room assumption), 10–25% of held calls close
      (vendor/agency, weak). --close both: tiers of $2,000 and up close on a call, the rest at checkout
      (or say so per tier with :checkout / :call).
      --format roundtable: an invite-only session (one day) for a few hand-picked people from a small warm
      list, closing on individual calls. --list-size is the number of people invited personally. Every rate
      is a Build Room assumption for personal invitations (not cold webinar rates), said as one.
      --tiers: each door is modelled on its own. share is the share of those who saw the offer who weigh
      that door (0.7, 70 or 70%; shares add up to 100%, which catches a slip); each tier converts at the
      band for ITS price (or the call chain), and buyers and money are summed. A cash goal is turned into
      buyers at the typical mix's average price (less the event's own ticket and VIP cash, below).
      Rates (--history-*, --vip-rate) follow one rule: a value ending in % is a percent ("2%" = 0.02,
      "0.5%" = 0.005); a value with no % must be a fraction strictly between 0 and 1 ("0.35" = 35%).
      Anything else (a bare 1, 35 or 0) is refused with a request for "35%" or "0.35". An unusually high
      history rate (registration over 60%, show-up over 90%, conversion over 40%) is warned.
      Member history (--history-*) replaces a benchmark stage; its cautious and strong are 80% and 120%.
      Paid event: --ticket-price T counts ticket cash (every registrant bought a ticket); --vip-price V
      counts a VIP upgrade bought by a share of registrants (--vip-rate R; default the labelled practitioner
      range 4–15%, typical 8%). Ticket and VIP cash are reported under "event_revenue" and count toward a
      --goal-cash goal.
      Prints the typical path (needed for the goal and expected from --list-size), a single-stage
      sensitivity (each stage alone at its cautious and its strong value, everything else typical), the
      verdict from the typical path's share of the goal (100% and up reachable; 60–99% stretch; under 60%
      not from this list alone) and the biggest lever: the stage with the largest buyer swing between its
      cautious and strong value (stages resting only on a Build Room assumption are left out).
      --md prints a markdown table instead of JSON (--md FILE writes it and prints the JSON). --out DIR
      writes (or updates) DIR/plan.json, which launch_tracker.py init --plan reads. --out also takes a
      launch slug (YYYY-MM-name): it writes to launches/<slug>/ (see launch_tracker.py slug).

  launch_plan.py timeline --event-date YYYY-MM-DD --days N --tz IANA
                          (--cart-days N | --deadline-date YYYY-MM-DD | --no-deadline)
                          [--partners] [--paid-event] [--invites 5|7] [--close checkout|call|both]
                          [--format F] [--sms] [--waitlist] [--country US|UK|CA|AU|IE|none]
                          [--rush] [--out DIR|SLUG] [--date YYYY-MM-DD]
      Backward schedule from Day 1. The deadline is never assumed: give --cart-days N (the cart closes N
      days after the final day), --deadline-date (the cart-close date) or --no-deadline; with none of
      them the timeline is refused.
      Milestones: sending_domain (a sending subdomain with SPF, DKIM and DMARC set up and warmed 2–4 weeks,
      28 days before the first list email), decide (the offer tested), partner recruitment (--partners: 12
      weeks out, 8 weeks minimum, Amber Spears' 90-day rule), sms_registration (--sms: A2P 10DLC, weeks
      ahead), the first-win tool (build, time it, promote it), proof bank, pages, then the four gate stages
      (launch_tracker.py gate --stage): gate_pre_invite before the first belief email, gate_day_before on
      Day 1 −1, gate_close_morning on the close morning, gate_cart before the first cart (or follow-up)
      email. One dated row per email of the default sequence: belief ×3, first-win tool emails, invitations
      ×7 (or ×5 with --invites 5), confirmation, pre-work, day-before, each day's morning email, a
      night-before recap for every day after Day 1, each day's replay, the cart emails, a mid-cart live Q&A
      (cart of 2 days or more) and the cart close (none with --no-deadline: an optional office hour
      instead). Follow-up: no-shows from the night of Day 1 (one-day event: the replay), failed checkouts
      the same day, non-buyers after the cart closes (after the last cart email), follow-up ends 10 days
      after the close; nurture_resume (+11) and next_cohort_or_evergreen_decision (+14 days after the close),
      the debrief (+12). --close call|both adds calls_held_48h and call_noshow_followup. --waitlist adds
      waitlist_open (a hand-raiser email before the invitations), waitlist_invite (the waitlist is invited
      first) and waitlist_offer (the waitlist hears the offer first when the cart opens). --format roundtable
      (one day) turns the invitations into personal invitations.
      Holidays: --country picks the public holidays flagged (default from --tz: US or Canadian zones → US
      or CA, Europe/London → UK, Europe/Dublin → IE, Australia/* → AU, anything else none). Thanksgiving
      week and Black Friday–Cyber Monday are flagged for US only; late December (24–31 Dec) and the Easter
      weekend are soft flags for every country. Sends and events on a weekend or a flagged day are listed.
      Lead time: refused (exit 2) when Day 1 is closer than 21 days (28 for a paid event, 8 weeks with
      --partners) unless --rush. --rush compresses the plan proportionally into the days left (the last
      three days keep their dates), never puts more than 2 list sends on one day (belief and tool emails
      are dropped first when they cannot fit, and listed), and flags every moved row (compressed, planned).
      Without --rush, tasks planned before today move to today and are flagged.
      --out writes plan.json (merged with math) and calendar.md (every week, empty ones too).
      --date replays "today".

Standard library only. Exit code 2 on a refused action (bad or missing input, impossible date).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, json, math, os, re, tempfile, unicodedata  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: E402

PLAN_SCHEMA = "buildroom-event-launcher/plan-1"
FORMATS = {"bootcamp3": 3, "challenge5": 5, "workshop": 1, "webinar": 1, "roundtable": 1}
SCENARIOS = ("cautious", "typical", "strong")
CLOSE_MODES = ("checkout", "call", "both")
CALL_PRICE = 2000          # --close both: tiers at or above this close on a call
ROOT = "launches"
SLUG_RE = re.compile(r"^\d{4}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")

SOURCES = {
    "ON24 2025": "ON24 Digital Engagement Benchmarks (2024–25 data): 57–60% of registrants attend, live and "
                 "on-demand counted together; B2B. An upper reference, not a small-list norm",
    "Livestorm 2026": "Livestorm 2026 Webinar Benchmark (2025 data, 33,786 sessions): 51.3% show-up; 49.6% of "
                      "registrations arrive in the final week and 15.3% on the day",
    "Scale For Impact 2026": "Scale For Impact webinar benchmarks (agency data, 114 webinars, $100M+ sales, course "
                             "creators): about 25% live show-up; attendee-to-buyer 8–15% at $97–497, 5–10% at "
                             "$500–1,500, 1–4% at $2,000+",
    "Pheedloop 2026 (in-person events)": "Pheedloop Event Data Lab #05 (1,070+ IN-PERSON events): median no-show 28% "
                                         "free vs 17% paid; in-person data, used for virtual paid events only as an "
                                         "upper reference",
    "HSH 2025": "Heart, Soul & Hustle paid bootcamp (practitioner self-report): 51.8% retained Day 1 to Day 5 "
                "(144 of 278), about 85% a day; 17.66–19.2% of paid participants bought the membership",
    "Build Room founder run Jul 2026": "Founder's free 3-day bootcamp, Jul 2026: 380 / 257 / 133 live on Days 1–3 "
                                       "(Day 1→2 67.6%, Day 2→3 51.8%), 67 at the very end (stay to the close about "
                                       "50%); Day-1 show-up 39.2% of registrants; 21 program buyers after a $1 first "
                                       "step",
    "Build Room founder follow-up analysis Jul 2026": "Founder's follow-up analysis of the same run: 56% of 41 people "
                                                      "who saw the price after a $1 first step bought (23 of 41, "
                                                      "follow-up analysis). A different count from the 21 program "
                                                      "buyers, and not a live-close conversion",
    "Build Room founder audit 2026": "Founder's 2026 audit of his earlier free bootcamps: about 50% of Day-1 attendees "
                                     "came back live on Day 2",
    "Build Room founder runs 2025–26": "Founder's earlier free bootcamps: Day-1 show-up averaged about 33% of registrants",
    "Build Room founder rule of thumb": "Founder, Aug 2026 debrief: Day 2 is about 80% of Day 1 and Day 3 about 80% "
                                        "of Day 2 (his July data ran lower; the audit says earlier camps ran about "
                                        "50% Day 1 to Day 2)",
    "Build Room planning range 2026": "Derived planning range in the Build Room research (best practices 2026): free "
                                      "challenge Day 1 15–35% of registrants, free webinar to a warm list 30–45%, "
                                      "paid $27–97 event 50–70%; buyers about 15–20% of paid-event participants",
    "Webinar call rates (vendor, weak)": "Vendor and agency blogs (best practices 2026, weak evidence): 10–20% of "
                                         "webinar attendees book a call; 10–25% of held calls close",
    "Build Room assumption": "No published benchmark exists for this step: a labelled Build Room planning "
                             "assumption. Replace it with your own numbers after one run",
    "Member history": "The member's own number from a past event (--history-*); cautious and strong are 80% and "
                      "120% of it",
    "Amber Spears 2018": "Amber Spears, Flight Club Mar 2018: 'I need 90 days to recruit… the big people are "
                         "booked'; never launch an untested offer; recruit in waves, biggest first",
    "Build Room founder method": "Founder's method (vault notes): belief before the invite, a first-win tool before "
                                 "the event, proof on Day 2, a night-before email for every day after Day 1, test "
                                 "the money path on the close morning, replays about 7 days, follow-up by segment "
                                 "from the night of Day 1, a written debrief",
    "GHL help 2026": "HighLevel help: A2P 10DLC brand and campaign must be approved before US texting",
    "US federal holidays": "US federal holidays (5 U.S.C. 6103; observed on the Friday or Monday when they fall on "
                           "a weekend), plus Thanksgiving week and Black Friday–Cyber Monday, when inboxes are full",
    "UK bank holidays": "UK bank holidays (England and Wales, GOV.UK), with the substitute weekday when one falls on "
                        "a weekend; computed, Easter included",
    "Ireland public holidays": "Irish public holidays (citizensinformation.ie), with the following weekday when one "
                               "falls on a weekend; computed, Easter Monday included",
    "Canada public holidays": "Canadian federal statutory holidays plus Family Day and the Civic Holiday (most "
                              "provinces); provinces differ, so check yours; computed, Good Friday included",
    "Australia public holidays": "Australian national public holidays plus the King's Birthday (most states), with "
                                 "substitute weekdays; states differ, so check yours; computed, Easter included",
    "Holiday soft flags": "Late December (24–31 Dec) and the Easter weekend (Good Friday to Easter Monday): many "
                          "people are away or offline whatever the country (Build Room assumption)",
    "Bulk-sender rules 2024": "Gmail, Yahoo and Microsoft bulk-sender rules: SPF, DKIM and DMARC aligned, one-click "
                              "unsubscribe; a new sending domain is warmed up gradually over 2–4 weeks (deliverability "
                              "practice) before a large send",
    "VIP upgrade range (practitioner)": "Practitioner figures for a VIP or upgrade at a multi-day event: 4–15% of "
                                        "registrants (Brunson secondhand 3.84%; Scale For Impact model); weak evidence",
}

# The founder's Jul 2026 figures, reconciled (they measure different things; never mix them):
FOUNDER_REFERENCE = {
    "program_buyers": {"value": 21, "what": "21 program buyers after a $1 first step",
                       "source": "Build Room founder run Jul 2026"},
    "saw_price_conversion": {"value": 0.56, "counts": "23 of 41",
                             "what": "of 41 people who saw the price after a $1 first step (follow-up analysis)",
                             "source": "Build Room founder follow-up analysis Jul 2026"},
    "show_up": {"value": 0.392, "what": "Day-1 show-up of registrants", "source": "Build Room founder run Jul 2026"},
    "retention": {"value": [0.676, 0.518], "what": "Day 1→2 and Day 2→3 live retention",
                  "source": "Build Room founder run Jul 2026"},
    "note": "a reference, not a benchmark: the 56% follows a $1 first step and is not a live-close rate; the "
            "run's registration rate is not given (his list came through a partner)",
}


def rng(c, t, s, source, note=""):
    return {"cautious": c, "typical": t, "strong": s, "source": source, **({"note": note} if note else {})}


# Registration rate of the list: research found no benchmark (best practices 2026, Gaps).
REG_RATE = {
    "free": rng(.10, .20, .30, "Build Room assumption",
                "share of the member's own list that registers; the research planning band is 10–30% for a warm "
                "list. A large partner-sent, mostly cold list registers far lower (founder's experience)"),
    "paid": rng(.03, .06, .10, "Build Room assumption", "share of the list that buys a ticket"),
}
SHOW_UP = {   # free event to a warm list 30/38/45 (references/launch-math.md); free challenge 15–35%
    ("free", "multi"): {"bootcamp3": [(.30, "Build Room planning range 2026"), (.38, "Build Room planning range 2026"),
                                      (.45, "Build Room planning range 2026")],
                        "challenge5": [(.15, "Build Room planning range 2026"), (.25, "Build Room planning range 2026"),
                                       (.35, "Build Room planning range 2026")]},
    ("free", "single"): [(.30, "Build Room planning range 2026"), (.38, "Build Room planning range 2026"),
                         (.45, "Build Room planning range 2026")],
    ("paid", None): [(.50, "Build Room planning range 2026"), (.60, "Build Room planning range 2026"),
                     (.70, "Pheedloop 2026 (in-person events)")],
}
SHOW_UP_NOTE = {"bootcamp3": "; the founder's own free bootcamps ran about 33% (earlier runs) and 39% (Jul 2026), inside "
                             "this band (Scale For Impact reports about 25% for creator funnels)"}
RETENTION = {   # share of yesterday's live attendees who come back live today
    "free": [(.50, "Build Room founder audit 2026"), (.70, "Build Room assumption"),
             (.80, "Build Room founder rule of thumb")],
    "paid": [(.70, "Build Room assumption"), (.85, "HSH 2025"), (.90, "Build Room assumption")],
}
STAY_TO_CLOSE = {   # share of the final day's live attendees still there when the offer is made
    "multi": [(.50, "Build Room founder run Jul 2026"), (.65, "Build Room assumption"), (.80, "Build Room assumption")],
    "single": [(.60, "Build Room assumption"), (.75, "Build Room assumption"), (.85, "Build Room assumption")],
}
SAW_NOTE = ("saw the price = present at the close × this. Off (×1.0) unless --replay-uplift: the conversion bands "
            "apply to those who saw the price, and replay or cart-email viewers are only counted when the member "
            "says the follow-up that shows them the offer will run (founder Jul 2026: some $1 buyers never saw the "
            "offer because the follow-up stayed in draft)")
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
CALL_RATES = {
    "booked": rng(.10, .15, .20, "Webinar call rates (vendor, weak)",
                  "of those who saw the offer, the share who book a call or send an application"),
    "held": rng(.70, .75, .80, "Build Room assumption", "of booked calls, the share that happen (show rate, about 70–80%)"),
    "closed": rng(.10, .175, .25, "Webinar call rates (vendor, weak)", "of held calls, the share that buy"),
}
LEVERS = {
    "registration": "Registrations: invite more of the list, earlier and more often (about half of registrations "
                    "land in the final week), add a partner wave, keep registration open through Day 1",
    "show_up": "Day-1 show-up: calendar file on the thank-you page, reminders the day before, the morning of and "
               "15 minutes before (email; SMS only with consent), pre-work that makes being live worth it",
    "retention": "Day-over-day retention: a night-before email for every day after Day 1 with tomorrow's payoff, "
                 "a cliffhanger that only pays off live, reminder times verified in the recipient's time zone",
    "stay_to_close": "Staying to the close: say when the offer comes, keep the promised build for after it, keep the "
                     "session inside the planned length",
    "saw_price": "Seeing the offer: switch on the follow-up that shows the offer to every attendee (replay with the "
                 "offer, follow-up emails) before the event starts",
    "conversion": "Conversion at checkout: the money path tested on a phone the morning of the close, an honest "
                  "deadline only if one is true, a clear 'which one are you' ladder, let ready buyers buy",
    "booked": "Calls booked: make the call or application the one next step at the offer, booking link on screen "
              "and in chat from the pitch onwards, someone in chat helping people book live",
    "held": "Calls held: book within 48 hours, a confirmation and a reminder the day before and the hour before, a "
            "short pre-call form that makes the call worth keeping",
    "closed": "Calls closed: one clear offer and price on the call, the same script every call, the payment link "
              "sent within the hour after a yes, a real start date",
}
STAGE_LABELS = [("registration", "Registration rate of list"), ("show_up", "Day-1 show-up"),
                ("retention", "Day-over-day retention"), ("stay_to_close", "Stay to the close"),
                ("saw_price", "Saw the price (× present)"), ("conversion", "Conversion of those who saw the price"),
                ("booked", "Booked a call (of those who saw the offer)"), ("held", "Calls held (of booked)"),
                ("closed", "Calls closed (of held)")]
# --format roundtable: personal invitations to a few hand-picked people; every rate is a labelled assumption
ROUNDTABLE = {
    "registration": rng(.20, .35, .50, "Build Room assumption",
                        "roundtable: share of the people invited personally who accept (personal-invitation rate, not "
                        "a webinar registration rate)"),
    "show_up": rng(.70, .80, .90, "Build Room assumption", "roundtable: share of those who accepted who attend"),
    "stay_to_close": rng(.85, .90, .95, "Build Room assumption", "roundtable: share still there when the offer is made"),
    "conversion": [.10, .20, .30],
    "booked": rng(.30, .50, .70, "Build Room assumption", "roundtable: share of attendees who book an individual call"),
    "held": rng(.80, .85, .90, "Build Room assumption", "roundtable: share of booked calls that happen"),
    "closed": rng(.20, .30, .40, "Build Room assumption",
                  "roundtable: share of held calls that buy; ask the member's own close rate on calls first "
                  "(--history-closed)"),
}
VIP_RATE = (.04, .08, .15)
PLAUSIBLE = {"reg": (.60, "registration over 60% of the list"), "show": (.90, "show-up over 90% of registrants"),
             "conversion": (.40, "conversion over 40% of those who saw the price")}
HISTORY_FLAGS = {"reg": "registration", "show": "show_up", "retention": "retention", "stay": "stay_to_close",
                 "conversion": "conversion", "booked": "booked", "held": "held", "closed": "closed"}


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
    """One unambiguous rule: a trailing % is a percent ('2%' → 0.02, '0.5%' → 0.005, '100%' → 1.0); a value with
    no % must be a fraction strictly between 0 and 1 ('0.35' → 0.35). Anything else is refused."""
    raw = str(s).strip()
    ask = f"write it as a percent with the sign (\"35%\") or as a fraction between 0 and 1 (\"0.35\")"
    pct_sign = raw.endswith("%")
    try:
        v = float(raw[:-1].strip() if pct_sign else raw)
    except ValueError:
        refuse(f"{what} must be a rate (got {s!r}): {ask}")
    if v != v:                                            # NaN
        refuse(f"{what} must be a rate (got {s!r}): {ask}")
    if pct_sign:
        v /= 100
        if not 0 < v <= 1:
            refuse(f"{what} must be more than 0% and at most 100% (got {s!r}): {ask}")
    elif not 0 < v < 1:
        refuse(f"{what} {s!r} is ambiguous or out of range: a value without % must be a fraction strictly between 0 "
               f"and 1; {ask}")
    return round(v, 10)


def share(s, what):
    """A tier share: '70%' or a fraction ('0.7', '1' = all of it), or a bare whole percent ('70'). Shares must add
    up to 100%, which catches a slip either way."""
    raw = str(s).strip()
    try:
        v = float(raw[:-1].strip() if raw.endswith("%") else raw)
    except ValueError:
        refuse(f"{what} must be a share such as 0.7 or 70% (got {s!r})")
    if raw.endswith("%") or v > 1:
        v /= 100
    if not 0 < v <= 1:
        refuse(f"{what} must be more than 0 and at most 100% (got {s!r})")
    return round(v, 10)


def slugify(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "launch"


def launch_slug(name, event_date):
    return f"{parse_date(event_date, '--event-date').isoformat()[:7]}-{slugify(name)}"


def out_dir(value):
    """--out DIR, or a launch slug (YYYY-MM-name) → launches/<slug>."""
    p = Path(value)
    if not p.exists() and SLUG_RE.match(str(value)):
        return Path(ROOT) / str(value)
    return p


def parse_tiers(items):
    tiers = []
    for t in items:
        raw = str(t)
        channel = None
        head, _, last = raw.rpartition(":")
        if last.strip().lower() in ("checkout", "call") and head:
            channel, raw = last.strip().lower(), head
        parts = raw.rsplit(":", 2)
        if len(parts) != 3 or not parts[0].strip():
            refuse(f"--tiers takes \"Name:price:share\" or \"Name:price:share:checkout|call\" (got {t!r})")
        tiers.append({"name": parts[0].strip(), "price": money(parts[1], f"tier {parts[0]} price"),
                      "share": share(parts[2], f"tier {parts[0]} share"), **({"channel": channel} if channel else {})})
    total = sum(x["share"] for x in tiers)
    if abs(total - 1) > .02:
        refuse(f"tier shares add up to {total:.0%}; each is the share of those who saw the offer who weigh that door, "
               "and they must add up to 100%")
    for x in tiers:
        x["share"] = x["share"] / total
    return tiers


def band_for(price):
    return next(b for b in BANDS if b["max"] is None or price < b["max"])


def per_value(vals, note):
    srcs = [s for _, s in vals]
    return rng(vals[0][0], vals[1][0], vals[2][0], srcs[1] if len(set(srcs)) == 1 else dict(zip(SCENARIOS, srcs)), note)


def hist_rng(v, note):
    return rng(round(v * .8, 4), v, round(min(1, v * 1.2), 4), "Member history", note)


def assign_channels(tiers, close):
    for t in tiers:
        if not t.get("channel"):
            t["channel"] = close if close in ("checkout", "call") else ("call" if t["price"] >= CALL_PRICE else "checkout")
    return tiers


def rates_for(fmt, days, paid, tiers, history=None, replay_uplift=None):
    """{stage: {cautious, typical, strong, source(s)}} for the funnel steps of this event. Sets each checkout
    tier's own "band" and "band_rates" (the conversion band for its price)."""
    history = {k: v for k, v in (history or {}).items() if v}
    kind = "paid" if paid else "free"
    multi = days > 1
    rt = fmt == "roundtable"
    out = {}
    out["registration"] = hist_rng(history["reg"], "share of the list that registered last time") \
        if "reg" in history else dict(ROUNDTABLE["registration"]) if rt else REG_RATE[kind]
    if "show" in history:
        out["show_up"] = hist_rng(history["show"], "registrants who came live on Day 1 last time")
    elif rt:
        out["show_up"] = dict(ROUNDTABLE["show_up"])
    else:
        if paid:
            vals = SHOW_UP[("paid", None)]
        elif multi:
            vals = SHOW_UP[("free", "multi")].get(fmt, SHOW_UP[("free", "multi")]["challenge5"])
        else:
            vals = SHOW_UP[("free", "single")]
        out["show_up"] = per_value(vals, "registrants who come live on Day 1 (unique attendees)" + (
            "; ON24 2025 and Livestorm 2026 report 50–60%, counted on wider definitions" if not paid and not multi else "")
            + ("" if paid or not multi else SHOW_UP_NOTE.get(fmt, "")))
    if multi:
        out["retention"] = hist_rng(history["retention"], f"day-over-day retention last time, applied {days - 1} times") \
            if "retention" in history else \
            per_value(RETENTION[kind], f"each day's live share of the day before, applied {days - 1} times")
    out["stay_to_close"] = hist_rng(history["stay"], "final-day live attendees still there at the offer last time") \
        if "stay" in history else dict(ROUNDTABLE["stay_to_close"]) if rt else per_value(STAY_TO_CLOSE["multi" if multi else "single"],
                                            "final-day live attendees still there when the offer is made")
    if replay_uplift:
        out["saw_price"] = rng(1.0, replay_uplift, replay_uplift, "Build Room assumption",
                               f"--replay-uplift {replay_uplift}: an optional assumption that the replay and follow-up "
                               "show the price to some who missed the live close; cautious leaves it out. " + SAW_NOTE)
    else:
        out["saw_price"] = rng(1.0, 1.0, 1.0, "Build Room assumption", SAW_NOTE)
    co = [t for t in tiers if t["channel"] == "checkout"]
    if co:
        s_co = sum(t["share"] for t in co)
        for t in co:
            b = band_for(t["price"])
            t["band"] = "roundtable (personal invitation)" if rt else b["band"]
            t["band_rates"] = None if "conversion" in history else dict(zip(SCENARIOS, ROUNDTABLE["conversion"] if rt
                                                                            else b[kind]))
        if "conversion" in history:
            out["conversion"] = hist_rng(history["conversion"], "of those who saw the price, the share who bought last "
                                         "time (applied to every checkout tier)")
            out["conversion"]["band"] = "member history"
        elif rt:
            out["conversion"] = rng(*ROUNDTABLE["conversion"], "Build Room assumption",
                                    "applies to those who saw the price. roundtable: personal-invitation assumption for "
                                    "a small hand-picked room, not a webinar band")
            out["conversion"]["band"] = "roundtable (personal invitation)"
        else:
            bands = list(dict.fromkeys(t["band"] for t in co))
            blend = {s: sum(t["share"] * t["band_rates"][s] for t in co) / s_co for s in SCENARIOS}
            b = band_for(co[0]["price"]) if len(bands) == 1 else None
            src = (b["paid_source"] if paid else b["source"]) if b else "Scale For Impact 2026"
            note = (f"{b['band']}: {b['note']}" if b else "each checkout tier converts at the band for its own price "
                    "(" + ", ".join(f"{t['name']} {t['band']}" for t in co) + "); this row is their share-weighted blend")
            if paid and b and b["max"] == 500:
                note += "; paid-event participants convert higher (Build Room planning range 2026: 15–20%)"
            out["conversion"] = rng(round(blend["cautious"], 6), round(blend["typical"], 6), round(blend["strong"], 6),
                                    src, "applies to those who saw the price. " + note)
            out["conversion"]["band"] = bands[0] if len(bands) == 1 else "mixed: " + " + ".join(bands)
    if any(t["channel"] == "call" for t in tiers):
        for k in ("booked", "held", "closed"):
            out[k] = hist_rng(history[k], CALL_RATES[k]["note"] + " (last time)") if k in history else \
                dict(ROUNDTABLE[k]) if rt else dict(CALL_RATES[k])
    return out


def g_for(rates, tiers, pick=None):
    """Numeric stage values for one path: pick maps a stage to a scenario (default typical for every stage)."""
    pick = pick or {}
    sc = lambda k: pick.get(k, "typical")
    g = {k: rates[k][sc(k)] for k in rates}
    per = []
    for t in tiers:
        if t["channel"] == "checkout":
            r = g["conversion"] if not t.get("band_rates") else t["band_rates"][sc("conversion")]
        else:
            r = g["booked"] * g["held"] * g["closed"]
        per.append(t["share"] * r)
    g["_per_tier"] = per
    g["_buy"] = sum(per)
    g["_value"] = sum(p * t["price"] for p, t in zip(per, tiers))
    g["_checkout"] = sum(p for p, t in zip(per, tiers) if t["channel"] == "checkout")
    g["_call_share"] = sum(t["share"] for t in tiers if t["channel"] == "call")
    return g


def _tail(saw, g, tiers, out):
    if g["_call_share"]:
        out["calls_booked"] = saw * g["_call_share"] * g["booked"]
        out["calls_held"] = out["calls_booked"] * g["held"]
        out["calls_closed"] = out["calls_held"] * g["closed"]
    if g["_call_share"] and g["_checkout"]:
        out["checkout_buyers"] = saw * g["_checkout"]
    out["buyers_by_tier"] = {t["name"]: saw * p for t, p in zip(tiers, g["_per_tier"])}
    out["booked_value"] = saw * g["_value"]
    return out


def reverse(buyers, g, days, tiers):
    """Needed counts (floats), working backwards from buyers."""
    saw = buyers / g["_buy"]
    present = saw / g["saw_price"]
    final_live = present / g["stay_to_close"]
    ret = g.get("retention", 1.0)
    day_live = [final_live / ret ** (days - 1 - i) for i in range(days)]
    regs = day_live[0] / g["show_up"]
    out = {"list": regs / g["registration"], "registrants": regs, "day_live": day_live, "present_at_close": present,
           "saw_price": saw, "buyers": buyers}
    return _tail(saw, g, tiers, out)


def forward(list_size, g, days, tiers):
    regs = list_size * g["registration"]
    d1 = regs * g["show_up"]
    ret = g.get("retention", 1.0)
    day_live = [d1 * ret ** i for i in range(days)]
    present = day_live[-1] * g["stay_to_close"]
    saw = present * g["saw_price"]
    out = {"registrants": regs, "day_live": day_live, "present_at_close": present, "saw_price": saw,
           "buyers": saw * g["_buy"]}
    return _tail(saw, g, tiers, out)


def _map(d, fn):
    return {k: ({kk: fn(vv) for kk, vv in v.items()} if isinstance(v, dict) else [fn(x) for x in v]
                if isinstance(v, list) else fn(v)) for k, v in d.items()}


def ceil_all(d):
    """Needed counts: always rounded up (the same rule in launch_tracker.py)."""
    return _map(d, lambda x: math.ceil(round(x, 6)))


def round_all(d, n=2):
    return _map(d, lambda x: round(x, n))


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


def assumption_only(v):
    src = v["source"]
    return set(src.values() if isinstance(src, dict) else [src]) == {"Build Room assumption"}


def sensitivity(rates, tiers, days, buyers, base_list):
    """Each stage alone at its cautious and its strong value, everything else typical."""
    out = {}
    for k, _ in STAGE_LABELS:
        if k not in rates or rates[k]["cautious"] == rates[k]["strong"]:
            continue
        row = {}
        for s in ("cautious", "strong"):
            g = g_for(rates, tiers, {k: s})
            row[s] = {"rate": rates[k][s], "expected_buyers": round(forward(base_list, g, days, tiers)["buyers"], 2),
                      "list_needed": math.ceil(round(reverse(buyers, g, days, tiers)["list"], 6))}
        row["buyer_swing"] = round(row["strong"]["expected_buyers"] - row["cautious"]["expected_buyers"], 2)
        row["assumption_only"] = assumption_only(rates[k])
        out[k] = row
    return out


def biggest_lever(sens, close):
    real = {k: v for k, v in sens.items() if not v["assumption_only"]}
    skipped = [k for k, v in sens.items() if v["assumption_only"]]
    if not real:
        return {"stage": None, "how": "every stage rests on an assumption: run once and use your own numbers",
                "note": "left out: " + ", ".join(skipped)}
    best = max(real, key=lambda k: (real[k]["buyer_swing"], k))
    return {"stage": best, "buyer_swing": real[best]["buyer_swing"], "how": LEVERS[best],
            "all_swings": {k: v["buyer_swing"] for k, v in sorted(real.items(), key=lambda kv: -kv[1]["buyer_swing"])},
            "close": close,
            "note": "the stage whose real range (cautious to strong, others typical) moves expected buyers the most; "
                    "stages resting only on a Build Room assumption are left out (their range is uncertainty, not "
                    "leverage): " + (", ".join(skipped) or "none")}


def verdict(expected_buyers, goal_buyers):
    share = expected_buyers / goal_buyers
    v = ("reachable" if share >= 1 else "stretch" if share >= .6 else
         "not from this list alone: add partners/ads or lower the goal")
    return v, round(share, 3)


def event_cash_rates(ticket_price, vip_price, vip_rate):
    """{"vip_rate": rng or None, "per_registrant": cash per registrant at the typical VIP rate}."""
    vr = None
    if vip_price:
        vr = (rng(round(vip_rate * .8, 4), vip_rate, round(min(1, vip_rate * 1.2), 4), "Member history",
                  "--vip-rate: share of registrants who buy the VIP upgrade") if vip_rate else
              rng(*VIP_RATE, "VIP upgrade range (practitioner)", "share of registrants who buy the VIP upgrade "
                  "(default: the practitioner range 4–15%, typical 8%; weak evidence)"))
    per = (ticket_price or 0) + (vr["typical"] * vip_price if vr else 0)
    return vr, per


def event_counts(regs, ticket_price, vip_price, vr):
    out = {}
    if ticket_price:
        out.update({"tickets": regs, "ticket_cash": regs * ticket_price})
    if vr:
        out.update({"vip_buyers": regs * vr["typical"], "vip_cash": regs * vr["typical"] * vip_price})
    out["event_cash"] = out.get("ticket_cash", 0) + out.get("vip_cash", 0)
    return out


def compute_math(goal_buyers=None, goal_cash=None, price=None, tiers=None, list_size=None, fmt="bootcamp3",
                 days=None, paid=False, history=None, close="checkout", replay_uplift=None, ticket_price=None,
                 vip_price=None, vip_rate=None):
    """The math result as a dict (also used by launch_tracker.py when no plan.json is given)."""
    if fmt not in FORMATS:
        refuse(f"--format must be one of {sorted(FORMATS)}")
    if close not in CLOSE_MODES:
        refuse(f"--close must be one of {list(CLOSE_MODES)}")
    days = days or FORMATS[fmt]
    if days < 1:
        refuse("--days must be 1 or more")
    if fmt == "roundtable" and days != 1:
        refuse("--format roundtable is a one-day session (--days 1)")
    if ticket_price and not paid:
        refuse("--ticket-price needs --paid-event (a free event sells no tickets)")
    if vip_rate and not vip_price:
        refuse("--vip-rate needs --vip-price (the price of the VIP upgrade)")
    if not tiers and not price:
        refuse("a price is needed: --price P or --tiers \"Name:price:share\" (the price sets the conversion band)")
    if not goal_buyers and not goal_cash:
        refuse("a goal is needed: --goal-buyers N or --goal-cash X")
    if replay_uplift is not None and not 1 <= replay_uplift <= 2:
        refuse("--replay-uplift must be between 1.0 and 2.0 (1.25 counts a quarter more viewers than were present)")
    tiers = assign_channels([dict(t) for t in tiers] if tiers else [{"name": "Offer", "price": price, "share": 1.0}], close)
    history = {k: v for k, v in (history or {}).items() if v}
    rates = rates_for(fmt, days, paid, tiers, history, replay_uplift)
    g = g_for(rates, tiers)
    avg = g["_value"] / g["_buy"]
    vr, ev_per_reg = event_cash_rates(ticket_price, vip_price, vip_rate)
    regs_per_buyer = reverse(1, g, days, tiers)["registrants"]
    per_buyer_cash = avg + ev_per_reg * regs_per_buyer       # offer money plus the event's own cash, per buyer
    from_cash = math.ceil(round(goal_cash / per_buyer_cash, 6)) if goal_cash else None
    buyers = max(x for x in (goal_buyers, from_cash) if x)
    binds = "goal-cash" if from_cash and (goal_buyers is None or from_cash > goal_buyers) else "goal-buyers"
    need = reverse(buyers, g, days, tiers)
    typical = {"rates": {k: v for k, v in g.items() if not k.startswith("_")},
               "per_viewer": {"buy": round(g["_buy"], 6), "checkout": round(g["_checkout"], 6),
                              "booked": round(g["_call_share"] * g.get("booked", 0), 6)},
               "needed_for_goal": ceil_all(need), "needed_exact": round_all(need)}
    warnings = []
    base_list = list_size or need["list"]
    if list_size:
        typical["expected_from_list"] = round_all(forward(list_size, g, days, tiers))
        typical["expected_registrants_range"] = {s: round(list_size * rates["registration"][s], 1) for s in SCENARIOS}
    out = {"inputs": {"goal_buyers": goal_buyers, "goal_cash": goal_cash, "price": price,
                      "tiers": [{k: t[k] for k in ("name", "price", "share", "channel")} for t in tiers] if len(tiers) > 1
                      or tiers[0]["name"] != "Offer" else None,
                      "list_size": list_size, "format": fmt, "days": days, "paid_event": bool(paid), "close": close,
                      "replay_uplift": replay_uplift,
                      "history": {HISTORY_FLAGS[k]: v for k, v in history.items()}},
           "goal": {"buyers": buyers, "binding": binds, "average_price": round(avg, 2),
                    "booked_at_goal": round(buyers * avg, 2),
                    **({"cash_at_goal_with_event_revenue": round(buyers * avg + ev_per_reg * need["registrants"], 2)}
                       if ev_per_reg else {})},
           "price_band": rates["conversion"]["band"] if "conversion" in rates else "call close",
           "tiers": [{"name": t["name"], "price": t["price"], "share": round(t["share"], 4), "channel": t["channel"],
                      **({"band": t["band"]} if t.get("band") else {}),
                      "typical_rate_of_viewers": round(p / t["share"], 6),
                      "needed_buyers": round(need["buyers_by_tier"][t["name"]], 2),
                      **({"expected_buyers": typical["expected_from_list"]["buyers_by_tier"][t["name"]]} if list_size else {})}
                     for t, p in zip(tiers, g["_per_tier"])],
           "rates": rates, "typical": typical}
    if ticket_price or vip_price:
        er = {"ticket_price": ticket_price, "vip_price": vip_price, "vip_rate": vr,
              "needed_for_goal": round_all(event_counts(need["registrants"], ticket_price, vip_price, vr)),
              "note": "every registrant of a paid event bought a ticket; VIP buyers are a share of registrants; this "
                      "cash counts toward --goal-cash"}
        if list_size:
            er["expected_from_list"] = round_all(event_counts(typical["expected_from_list"]["registrants"],
                                                              ticket_price, vip_price, vr))
            er["expected_cash_total"] = round(typical["expected_from_list"]["booked_value"]
                                              + er["expected_from_list"]["event_cash"], 2)
        out["event_revenue"] = er
    elif paid:
        warnings.append("--paid-event without --ticket-price: ticket cash is not counted; give --ticket-price T")
    if fmt == "roundtable":
        warnings.append("roundtable: every rate is a Build Room assumption for personal invitations to a small warm "
                        "list, not a webinar benchmark (vendor webinar call rates understate warm, referred prospects). "
                        "Ask the member's own close rate on calls first and give it as --history-closed")
        if list_size and list_size > 300:
            warnings.append(f"roundtable with --list-size {list_size}: a roundtable invites 8–20 hand-picked people "
                            "from a list under about 300; --list-size is the number you will invite personally")
        if list_size and typical["expected_from_list"]["day_live"][0] > 20:
            warnings.append(f"roundtable: about {typical['expected_from_list']['day_live'][0]:.0f} attendees expected, "
                            "more than the 8–20 a roundtable holds: invite fewer, or run two rooms")
    for k, (lim, what) in PLAUSIBLE.items():
        if k in history and history[k] > lim:
            warnings.append(f"--history-{ {'reg': 'reg-rate', 'show': 'showup'}.get(k, k)} {history[k]:.0%} is "
                            f"unusually high ({what}): check it was a rate, not a count, and written as \"35%\" or "
                            "\"0.35\"")
    sens = sensitivity(rates, tiers, days, buyers, base_list)
    out["sensitivity"] = sens
    out["sensitivity_note"] = ("each stage alone at its cautious and strong value, every other stage typical; "
                               + ("expected buyers from --list-size" if list_size else
                                  "expected buyers from the list the typical path needs"))
    if list_size:
        v, share = verdict(typical["expected_from_list"]["buyers"], buyers)
        out["verdict"] = v
        out["verdict_detail"] = {"expected_buyers_typical": typical["expected_from_list"]["buyers"], "goal_buyers": buyers,
                                 "share_of_goal": share,
                                 "rule": "typical expected buyers ÷ goal: 100% and up reachable, 60–99% stretch, under "
                                         "60% not from this list alone"}
    out["lever"] = biggest_lever(sens, close)
    if any(t["channel"] == "checkout" and t["price"] >= CALL_PRICE for t in tiers):
        warnings.append("a checkout tier costs $2,000 or more: direct checkout converts 1–4% (Scale For Impact 2026); "
                        "consider --close call (or :call on that tier) and track calls booked, held and closed")
    if rates["registration"]["source"] == "Build Room assumption":
        warnings.append("the registration rate of the list has no published benchmark: it is a Build Room assumption. "
                        "Give --history-reg-rate from a past event if you have one")
    if "booked" in rates:
        warnings.append("call-close rates are weak evidence (vendor/agency blogs) and the show rate is a Build Room "
                        "assumption: give --history-booked / --history-held / --history-closed after one run")
    out["notes"] = ["conversion (and booking) rates apply to those who saw the price; saw the price is present at the "
                    "close × " + (f"{replay_uplift} (--replay-uplift, an assumption)" if replay_uplift else
                                  "1.0 (no replay uplift assumed)"),
                    "money is booked revenue at each tier's price; payment plans collect less cash up front"]
    if len(tiers) > 1:
        out["notes"].append("tiers are modelled one door at a time: each converts at its own band (or the call chain) "
                            "on its share of those who saw the offer; a cash goal uses the typical mix's average price")
    out["founder_reference"] = FOUNDER_REFERENCE
    if warnings:
        out["warnings"] = warnings
    out["sources"] = sources_used({"r": out["rates"], "v": vr} if vr else out["rates"])
    for x in ("Build Room founder run Jul 2026", "Build Room founder follow-up analysis Jul 2026"):
        out["sources"][x] = SOURCES[x]
    return out


def pct(x):
    return (f"{x * 100:.2f}%" if 0 < x < .01 else f"{x * 100:.1f}%").replace(".0%", "%")


def num(x):
    """Counts for display: whole numbers with commas, small expected counts with two decimals."""
    return f"{x:,}" if isinstance(x, int) else f"{x:,.2f}" if abs(x) < 10 else f"{x:,.1f}"


def math_md(r):
    d = r["inputs"]["days"]
    lines = [f"# Launch math: {r['goal']['buyers']} buyers at ${r['goal']['average_price']:,.0f} average "
             f"({r['inputs']['format']}, {d} day{'s' if d > 1 else ''}, {'paid' if r['inputs']['paid_event'] else 'free'}, "
             f"close: {r['inputs']['close']})", "",
             "| Stage | Cautious | Typical | Strong | Source |", "|---|---|---|---|---|"]
    def src(k):
        s = r["rates"][k]["source"]
        return " / ".join(dict.fromkeys(s.values())) if isinstance(s, dict) else s
    for k, label in STAGE_LABELS:
        if k in r["rates"]:
            v = r["rates"][k]
            fmtv = (lambda x: f"×{x:.2f}") if k == "saw_price" else pct
            if k == "conversion":
                label += f" ({r['rates'][k].get('band')})"
            lines.append(f"| {label} | {fmtv(v['cautious'])} | {fmtv(v['typical'])} | {fmtv(v['strong'])} | {src(k)} |")
    t = r["typical"]
    need, exp = t["needed_for_goal"], t.get("expected_from_list")
    lines += ["", "## Typical path", "", "| Count | Needed for the goal | Expected from the list |", "|---|---|---|"]
    rows = [("List", "list"), ("Registrants", "registrants")] + [(f"Live Day {i + 1}", ("day_live", i)) for i in range(d)] + \
           [("Present at the close", "present_at_close"), ("Saw the price", "saw_price"), ("Calls booked", "calls_booked"),
            ("Calls held", "calls_held"), ("Calls closed", "calls_closed"), ("Checkout buyers", "checkout_buyers"),
            ("**Buyers**", "buyers")]
    def get(src_, k):
        if not src_:
            return None
        return src_[k[0]][k[1]] if isinstance(k, tuple) else src_.get(k)
    for label, k in rows:
        n = get(need, k)
        e = r["inputs"]["list_size"] if (k == "list" and exp) else get(exp, k)
        if n is None and e is None:
            continue
        lines.append(f"| {label} | {'–' if n is None else num(n)} | {'–' if e is None else num(e)} |")
    if len(r["tiers"]) > 1:
        lines += ["", "| Tier | Price | Share of viewers | Close | Typical rate | Needed buyers | Expected buyers |",
                  "|---|---|---|---|---|---|---|"]
        for x in r["tiers"]:
            lines.append(f"| {x['name']} | ${x['price']:,.0f} | {pct(x['share'])} | {x['channel']} | "
                         f"{pct(x['typical_rate_of_viewers'])} | {num(x['needed_buyers'])} | "
                         f"{num(x['expected_buyers']) if 'expected_buyers' in x else '–'} |")
    lines += ["", "## Sensitivity (one stage at a time)", "", f"_{r['sensitivity_note']}_", "",
              "| Stage | Cautious → buyers | Strong → buyers | Swing |", "|---|---|---|---|"]
    lab = dict(STAGE_LABELS)
    for k, v in r["sensitivity"].items():
        f = (lambda x: f"×{x:.2f}") if k == "saw_price" else pct
        lines.append(f"| {lab[k]}{' (assumption)' if v['assumption_only'] else ''} | {f(v['cautious']['rate'])} → "
                     f"{num(v['cautious']['expected_buyers'])} | {f(v['strong']['rate'])} → {num(v['strong']['expected_buyers'])} | "
                     f"{num(v['buyer_swing'])} |")
    er = r.get("event_revenue")
    if er:
        lines += ["", "## Event revenue (tickets and VIP)", "", "| | Needed for the goal | Expected from the list |", "|---|---|---|"]
        exp_er = er.get("expected_from_list") or {}
        for k, label in (("tickets", "Tickets"), ("ticket_cash", "Ticket cash"), ("vip_buyers", "VIP buyers"),
                         ("vip_cash", "VIP cash"), ("event_cash", "**Event cash**")):
            if k in er["needed_for_goal"]:
                f = (lambda x: f"${x:,.0f}") if "cash" in k else num
                lines.append(f"| {label} | {f(er['needed_for_goal'][k])} | {f(exp_er[k]) if k in exp_er else '–'} |")
        if er.get("vip_rate"):
            v = er["vip_rate"]
            lines.append(f"\nVIP rate {pct(v['cautious'])} / {pct(v['typical'])} / {pct(v['strong'])} of registrants "
                         f"({v['source']})")
    if r.get("verdict"):
        vd = r["verdict_detail"]
        lines += ["", f"**Verdict:** {r['verdict']} (the typical path gives {num(vd['expected_buyers_typical'])} of "
                      f"{vd['goal_buyers']} buyers, {pct(vd['share_of_goal'])} of the goal)"]
    lv = r["lever"]
    if lv.get("stage"):
        lines += ["", f"**Biggest lever:** {lab[lv['stage']]} (swing of {num(lv['buyer_swing'])} buyers between its cautious "
                      f"and strong value). {lv['how']}."]
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


def update_plan(folder, key, value):
    p = Path(folder) / "plan.json"
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


# ---------------- holidays ----------------

COUNTRIES = ("US", "UK", "CA", "AU", "IE", "none")
COUNTRY_SOURCE = {"US": "US federal holidays", "UK": "UK bank holidays", "CA": "Canada public holidays",
                  "AU": "Australia public holidays", "IE": "Ireland public holidays"}
US_TZ = {"America/New_York", "America/Detroit", "America/Chicago", "America/Menominee", "America/Denver",
         "America/Boise", "America/Phoenix", "America/Los_Angeles", "America/Anchorage", "America/Juneau",
         "America/Sitka", "America/Metlakatla", "America/Yakutat", "America/Nome", "America/Adak",
         "Pacific/Honolulu", "America/Puerto_Rico"}
CA_TZ = {"America/Toronto", "America/Montreal", "America/Vancouver", "America/Edmonton", "America/Winnipeg",
         "America/Regina", "America/Halifax", "America/St_Johns", "America/Moncton", "America/Glace_Bay",
         "America/Goose_Bay", "America/Whitehorse", "America/Yellowknife", "America/Iqaluit", "America/Dawson",
         "America/Dawson_Creek", "America/Fort_Nelson", "America/Creston", "America/Cambridge_Bay",
         "America/Rankin_Inlet", "America/Resolute", "America/Swift_Current", "America/Atikokan", "America/Nipigon",
         "America/Thunder_Bay", "America/Rainy_River", "America/Inuvik", "America/Pangnirtung", "America/Blanc-Sablon"}
UK_TZ = {"Europe/London", "Europe/Belfast", "Europe/Guernsey", "Europe/Jersey", "Europe/Isle_of_Man", "GB"}


def default_country(tz):
    tz = str(tz)
    if tz in US_TZ or tz.startswith(("US/", "America/Indiana/", "America/Kentucky/", "America/North_Dakota/")):
        return "US"
    if tz in CA_TZ or tz.startswith("Canada/"):
        return "CA"
    if tz in UK_TZ:
        return "UK"
    if tz in ("Europe/Dublin", "Eire"):
        return "IE"
    if tz.startswith("Australia/"):
        return "AU"
    return "none"


def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def last_weekday(y, m, wd):
    d = dt.date(y, m + 1, 1) - dt.timedelta(days=1) if m < 12 else dt.date(y, 12, 31)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def easter(y):
    """Easter Sunday (Gregorian; the anonymous algorithm)."""
    a, (b, c) = y % 19, divmod(y, 100)
    d, e = divmod(b, 4)
    g = (b - (b + 8) // 25 + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mo, day = divmod(h + l_ - 7 * m + 114, 31)
    return dt.date(y, mo, day + 1)


def with_substitutes(h, names):
    """Add a substitute weekday for each named fixed-date holiday that falls on a weekend (UK, IE, AU, CA style):
    the next weekday that is not already a holiday."""
    for day, name in sorted((d, n) for d, n in h.items() if n in names):
        if day.weekday() >= 5:
            s = day + dt.timedelta(days=7 - day.weekday())
            while s in h or s.weekday() >= 5:
                s += dt.timedelta(days=1)
            h[s] = f"{name} (substitute day)"
    return h


def us_holidays(year):
    """{date: name}: US federal holidays (with the observed weekday), Thanksgiving week, Black Friday–Cyber Monday."""
    fixed = {(1, 1): "New Year's Day", (6, 19): "Juneteenth", (7, 4): "Independence Day", (11, 11): "Veterans Day",
             (12, 25): "Christmas Day"}
    h = {}
    for (m, d), name in fixed.items():
        day = dt.date(year, m, d)
        h[day] = name
        if day.weekday() == 5:
            h.setdefault(day - dt.timedelta(days=1), f"{name} (observed)")
        elif day.weekday() == 6:
            h.setdefault(day + dt.timedelta(days=1), f"{name} (observed)")
    h[nth_weekday(year, 1, 0, 3)] = "Martin Luther King Jr. Day"
    h[nth_weekday(year, 2, 0, 3)] = "Presidents' Day"
    h[last_weekday(year, 5, 0)] = "Memorial Day"
    h[nth_weekday(year, 9, 0, 1)] = "Labor Day"
    h[nth_weekday(year, 10, 0, 2)] = "Columbus Day"
    tg = nth_weekday(year, 11, 3, 4)
    h[tg] = "Thanksgiving"
    for i in range(-3, 4):
        h.setdefault(tg + dt.timedelta(days=i), "Thanksgiving week")
    for i, name in ((1, "Black Friday"), (2, "Black Friday weekend"), (3, "Black Friday weekend"), (4, "Cyber Monday")):
        h[tg + dt.timedelta(days=i)] = name
    return h


def uk_holidays(year):
    e = easter(year)
    h = {dt.date(year, 1, 1): "New Year's Day", e - dt.timedelta(days=2): "Good Friday",
         e + dt.timedelta(days=1): "Easter Monday", nth_weekday(year, 5, 0, 1): "Early May bank holiday",
         last_weekday(year, 5, 0): "Spring bank holiday", last_weekday(year, 8, 0): "Summer bank holiday",
         dt.date(year, 12, 25): "Christmas Day", dt.date(year, 12, 26): "Boxing Day"}
    return with_substitutes(h, {"New Year's Day", "Christmas Day", "Boxing Day"})


def ie_holidays(year):
    feb1 = dt.date(year, 2, 1)
    h = {dt.date(year, 1, 1): "New Year's Day",
         (feb1 if feb1.weekday() == 4 else nth_weekday(year, 2, 0, 1)): "St Brigid's Day",
         dt.date(year, 3, 17): "St Patrick's Day", easter(year) + dt.timedelta(days=1): "Easter Monday",
         nth_weekday(year, 5, 0, 1): "May bank holiday", nth_weekday(year, 6, 0, 1): "June bank holiday",
         nth_weekday(year, 8, 0, 1): "August bank holiday", last_weekday(year, 10, 0): "October bank holiday",
         dt.date(year, 12, 25): "Christmas Day", dt.date(year, 12, 26): "St Stephen's Day"}
    return with_substitutes(h, {"New Year's Day", "St Patrick's Day", "Christmas Day", "St Stephen's Day"})


def ca_holidays(year):
    v = dt.date(year, 5, 24)
    while v.weekday() != 0:
        v -= dt.timedelta(days=1)
    jul1 = dt.date(year, 7, 1)
    h = {dt.date(year, 1, 1): "New Year's Day", nth_weekday(year, 2, 0, 3): "Family Day (most provinces)",
         easter(year) - dt.timedelta(days=2): "Good Friday", v: "Victoria Day",
         (jul1 + dt.timedelta(days=1) if jul1.weekday() == 6 else jul1): "Canada Day",
         nth_weekday(year, 8, 0, 1): "Civic Holiday (most provinces)", nth_weekday(year, 9, 0, 1): "Labour Day",
         dt.date(year, 9, 30): "National Day for Truth and Reconciliation (federal)",
         nth_weekday(year, 10, 0, 2): "Thanksgiving (Canada)", dt.date(year, 11, 11): "Remembrance Day (most provinces)",
         dt.date(year, 12, 25): "Christmas Day", dt.date(year, 12, 26): "Boxing Day"}
    return with_substitutes(h, {"New Year's Day", "Christmas Day", "Boxing Day"})


def au_holidays(year):
    e = easter(year)
    jan26 = dt.date(year, 1, 26)
    h = {dt.date(year, 1, 1): "New Year's Day",
         (jan26 + dt.timedelta(days=7 - jan26.weekday()) if jan26.weekday() >= 5 else jan26): "Australia Day",
         e - dt.timedelta(days=2): "Good Friday", e - dt.timedelta(days=1): "Easter Saturday",
         e + dt.timedelta(days=1): "Easter Monday", dt.date(year, 4, 25): "Anzac Day",
         nth_weekday(year, 6, 0, 2): "King's Birthday (most states)",
         dt.date(year, 12, 25): "Christmas Day", dt.date(year, 12, 26): "Boxing Day"}
    return with_substitutes(h, {"New Year's Day", "Christmas Day", "Boxing Day"})


HOLIDAYS = {"US": us_holidays, "UK": uk_holidays, "CA": ca_holidays, "AU": au_holidays, "IE": ie_holidays}


def soft_flag(d):
    """Soft flags for every country: late December and the Easter weekend (Good Friday to Easter Monday)."""
    if d.month == 12 and d.day >= 24:
        return "late December (holiday season)"
    e = easter(d.year)
    if e - dt.timedelta(days=2) <= d <= e + dt.timedelta(days=1):
        return "Easter weekend"
    return None


def holiday(d, country="US"):
    """(name, soft): a public holiday of the country (soft False), else a soft flag (soft True), else (None, False)."""
    fn = HOLIDAYS.get(country)
    name = fn(d.year).get(d) if fn else None
    if name:
        return name, False
    s = soft_flag(d)
    return (s, True) if s else (None, False)


# ---------------- timeline ----------------

INVITE_OFFSETS = {(False, 7): [-14, -11, -8, -5, -3, -2, -1], (False, 5): [-14, -8, -3, -2, -1],
                  (True, 7): [-21, -17, -13, -9, -5, -2, -1], (True, 5): [-21, -12, -5, -2, -1]}
LIST_SEND_IDS = ("belief_", "invite_", "first_win_emails", "waitlist_open")
RUSH_DROP_ORDER = ["belief_3", "belief_2", "waitlist_open", "first_win_emails", "belief_1"]
MAX_LIST_SENDS_A_DAY = 2


def is_list_send(mid):
    return mid.startswith(LIST_SEND_IDS)


def milestone_specs(days, partners, paid, cart_days, invites=7, deadline=True, close="checkout", sms=False,
                    waitlist=False, fmt=None):
    """(id, offset in days from Day 1, slot 0 morning / 1 day / 2 evening, kind task|send|event, title, detail,
    source)."""
    inv = INVITE_OFFSETS[(bool(paid), invites)]
    i0 = inv[0]
    first_send = i0 - 7                                  # belief_1: the first email to the list
    decide = -98 if partners else (-49 if paid else -42)
    path = {"checkout": "checkout", "call": "booking path", "both": "checkout and booking path"}[close]
    rt = fmt == "roundtable"
    m = [("sending_domain", first_send - 28, 1, "task", "Sending domain set up and warming",
          "Set up and verify a sending subdomain (SPF, DKIM and DMARC aligned, one-click unsubscribe) at least 28 "
          "days before the first launch email, and warm it up for 2–4 weeks with your most engaged contacts. Skip "
          "if the list already sends well from a warmed domain", "Bulk-sender rules 2024"),
         ("decide", decide, 1, "task", "Decide and test the offer",
          "Decide the offer, the one belief, the format, the close (checkout or call) and the deadline (a real one, "
          "or none on purpose); test the offer with a pilot, past clients or a small paid beta before anyone "
          "promotes it", "Amber Spears 2018")]
    if partners:
        m += [("partner_recruit", -84, 1, "task", "Partner recruitment starts",
               "12 weeks out (8 weeks at the latest): own network first, then partners one-on-one biggest first, then "
               "ask each yes for an introduction; ask each what a good result looks like", "Amber Spears 2018"),
              ("partner_terms", -56, 1, "task", "Partner deals in writing",
               "Dates, what they promote, commission or swap, who owns the leads, what happens if it underperforms; "
               "partners disclose their commission", "Amber Spears 2018"),
              ("partner_kit", i0 - 14, 1, "task", "Partner kit out",
               "Two emails, two posts, tracking links, disclosure wording; copy names who teaches live",
               "Build Room founder method")]
    if sms:
        m.append(("sms_registration", i0 - 28, 1, "task", "SMS registration (A2P 10DLC) submitted",
                  "A2P 10DLC brand and campaign submitted now: approval can take weeks, and GoHighLevel will not send "
                  "US texts without it. The registration form gets a separate, unchecked SMS consent box",
                  "GHL help 2026"))
    m += [("first_win_build", i0 - 21, 1, "task", "First-win tool built",
           "The free tool or pre-work that gives a first win before the event (and fills the invitation sequence)",
           "Build Room founder method"),
          ("first_win_timed", i0 - 14, 1, "task", "First-win tool timed",
           "Three people use it while you time them; the emails state the measured time, not a guess",
           "Build Room founder method"),
          ("proof_bank", i0 - 14, 1, "task", "Proof bank classified",
           "Classify every story (free-event result / paid-program / outside), get consents, typical results only",
           "Build Room founder method"),
          ("pages_built", i0 - 11, 1, "task", "Pages and money path built",
           f"Registration and thank-you page with the calendar file, the {path} with its terms, replay page, "
           "follow-up workflows drafted", "Build Room founder method"),
          ("gate_pre_invite", i0 - 9, 0, "task", "Gate: pre_invite (before the first belief email)",
           "launch_tracker.py gate --stage pre_invite shows GO before the first email of any kind: sending, truth, "
           "one source of truth, partners, terms, the registration path tested", "Build Room founder method")]
    if waitlist:
        m.append(("waitlist_open", i0 - 2, 1, "send", "Waitlist: hand-raiser email",
                  "A short 'put your hand up' email before the invitations: people who want first word on the offer "
                  "join the waitlist (log them: log-reg N --source segment:waitlist)", "Build Room founder method"))
    for n, off in enumerate((i0 - 7, i0 - 6, i0 - 5), 1):
        m.append((f"belief_{n}", off, 1, "send", f"Belief email {n} of 3",
                  ("opportunity", "identity", "mechanism")[n - 1] + " belief; no offer yet", "Build Room founder method"))
    m.append(("first_win_emails", i0 - 4, 1, "send", "First-win tool emails start",
              f"The tool phase: one email a day from {-(i0 - 4)} to {-(i0 - 1)} days out, the tool as the only call to "
              "action", "Build Room founder method"))
    m.append(("confirmation", i0, 0, "send", "Confirmation email live",
              "Sent on registration from the first invitation: the calendar file, the date in a few zones, the pre-work",
              "Build Room founder method"))
    if waitlist:
        m.append(("waitlist_invite", i0 - 1, 1, "send", "Waitlist invited first",
                  "The waitlist gets the invitation a day before everyone else", "Build Room founder method"))
    word = "Personal invitation" if rt else "Invitation"
    for n, off in enumerate(inv, 1):
        m.append((f"invite_{n}", off, 1, "send", f"{word} {n} of {len(inv)}",
                  ("A personal note or message to each hand-picked person, then a reminder to those who have not "
                   "answered" if rt else
                   ("About 14 days out (21 for a paid event); " if n == 1 else "") +
                   "keep promoting through Day 1: about half of registrations arrive in the final week and 15% on the "
                   "day"), "Livestorm 2026"))
    m += [("prework", -3, 1, "send", "Pre-work nudge",
           "To registrants: the one pre-work action and why being live matters", "Build Room founder method"),
          ("reminder_dry_run", -1, 0, "task", "Reminder dry run",
           "Send every reminder to a test contact in the recipient's time zone (event_ics.py reminders) and check "
           "the times; reminders fired hours early in the founder's July run", "Build Room founder run Jul 2026"),
          ("gate_day_before", -1, 0, "task", "Gate: day_before (24 hours before Day 1)",
           "launch_tracker.py gate --stage day_before: the reminder dry run done, every night email pre-written and "
           "scheduled, the moderator's links, the live tech, the checkout or booking path tested end to end, the "
           "replay release", "Build Room founder method"),
          ("day_before", -1, 1, "send", "Day-before email", "How to prepare, the calendar file again, the one pre-work action",
           "Build Room founder method")]
    f = days - 1
    for k in range(1, days + 1):
        last = k == days
        m.append((f"day{k}_morning", k - 1, 0, "send", "Close-morning email" if last and days > 1 else f"Day {k} morning email",
                  "Today's promise, the start time in a few zones, the link" + ("; the offer is today" if last else ""),
                  "Build Room founder method"))
        m.append((f"day{k}", k - 1, 1, "event", f"Day {k} live" + (" (close day)" if last else ""),
                  "15-minute and 'we're live' reminders; recording notice at the start", "Build Room founder method"))
        if k < days:
            m.append((f"day{k}_night", k - 1, 2, "send", f"Day-{k}-night recap",
                      f"Recap of Day {k} plus the Day-{k + 1} payoff, pre-written before Day 1 (at most a two-line edit "
                      "on the night); the founder's July run had none and lost people", "Build Room founder run Jul 2026"))
        m.append((f"day{k}_replay", k - 1, 2, "send", f"Day {k} replay out",
                  "Replay within 1–3 hours of the end" + ("; buyers get access and a welcome within 24 hours" if last else ""),
                  "Build Room founder method"))
    m.append(("followup_noshow", 0, 2, "send", "No-show follow-up starts (night of Day 1)",
              "Registrants who missed Day 1: the Day-1 replay or the tool, and why to come live tomorrow" if days > 1 else
              "Registrants who missed the session: the replay with the offer, and one next step",
              "Build Room founder method"))
    if waitlist:
        m.append(("waitlist_offer", f, 0, "send", "Waitlist hears the offer first (cart opens)",
                  "The waitlist gets the offer first when the cart opens, with what they get for being early (only if "
                  "it is true)", "Build Room founder method"))
    m += [("gate_close_morning", f, 0, "task", "Gate: close_morning",
           f"launch_tracker.py gate --stage close_morning: the {path}, backup link, terms and follow-up re-tested "
           "today on a phone", "Build Room founder run Jul 2026"),
          ("followup_failed", f, 2, "send", "Failed-checkout / unbooked follow-up (same day)",
           "Anyone who started the checkout or booking and did not finish: a personal note and the backup link",
           "Build Room founder method"),
          ("gate_cart", f + 1, 0, "task", "Gate: cart (before the cart and follow-up emails)",
           "launch_tracker.py gate --stage cart: proof and chat-quote consents re-checked for the cart and follow-up "
           "emails, claims typical, the deadline real (or none)", "Build Room founder method")]
    if close in ("call", "both"):
        m += [("call_noshow_followup", f + 1, 2, "send", "Call no-shows followed up the same day",
               "From the first calls on: a personal note and a rebooking link to every no-show, the same day",
               "Build Room founder method"),
              ("calls_held_48h", f + 2, 1, "task", "Calls booked at the event held within 48 hours",
               "Every call booked at the close is held within 48 hours (confirmation, reminders the day before and the "
               "hour before); log-calls as they happen", "Build Room founder method")]
    end_replay = f + 7
    c = f
    if deadline:
        cd = max(cart_days, 0)
        c = f + cd
        for n in range(1, cd + 1):
            m.append((f"cart_{n}", f + n, 1, "send", f"Cart email {n} of {cd}" + (" (three sends on the final day)" if n == cd else ""),
                      "The offer, the real deadline, answers to the main objections", "Build Room founder method"))
        if cd >= 2:
            m.append(("cart_live_qa", f + (cd + 1) // 2, 1, "event", "Mid-cart live Q&A",
                      "A live Q&A or office hour for people deciding, with the close replay cut to the offer section",
                      "Build Room founder method"))
        m.append(("cart_close", c, 2, "task", "Cart closes",
                  "A real deadline, the same for everyone (or honest per-person timers); no reopen", "Build Room founder method"))
        end_replay = min(end_replay, c)
    else:
        m.append(("office_hour", f + 3, 1, "event", "Live office hour (optional)",
                  "A live office hour for people deciding, if you can; no countdown, no 'last chance'",
                  "Build Room founder method"))
    m.append(("followup_nonbuyers", c + 1, 1, "send",
              "Non-buyer follow-up starts (after the cart closes)" if deadline else "Non-buyer follow-up starts (day after the close)",
              "Attended and didn't buy, by segment, after the last cart email: five emails over ten days, then stop",
              "Build Room founder method"))
    m.append(("replay_closes", end_replay, 2, "task", "Replay window closes",
              "Replays run about 7 days and never past the deadline (or the replay page says the offer has closed)",
              "Build Room founder method"))
    m.append(("followup_end", c + 10, 1, "send", "Follow-up ends",
              "The last email says so ('I'll stop asking about this'), then stop" + ("" if deadline else
                                                                                     "; no deadline means no fake one"),
              "Build Room founder method"))
    m.append(("nurture_resume", c + 11, 1, "task", "Non-buyers back into regular nurture",
              "Non-buyers return to the regular newsletter, not silence; the people who said 'not now' get the next "
              "cohort date", "Build Room founder method"))
    m.append(("debrief", c + 12, 1, "task", "Debrief",
              "launch_tracker.py report --md (debrief-numbers.md), the member's debrief.md, then launch_tracker.py "
              "obsidian to file the lessons", "Build Room founder method"))
    m.append(("next_cohort_or_evergreen_decision", c + 14, 1, "task", "Decide: next cohort, evergreen or pause",
              "Two weeks after the close: run it again as a next live cohort, turn it into an evergreen version only "
              "once a live run converted well (expect about half the live rate), or pause", "Build Room founder method"))
    return m


def rush_layout(specs, lead):
    """--rush: offsets compressed proportionally into the days left (the last three days keep their dates), then
    list sends spaced at most MAX_LIST_SENDS_A_DAY a day (Day 1 included). Returns ({id: offset}, dropped ids)."""
    off = {s[0]: s[1] for s in specs}
    pre = [o for o in off.values() if o < 0]
    earliest = min(pre) if pre else 0
    if -earliest <= lead:
        return off, []
    k = min(3, lead)
    lo, hi = -lead, -k - 1
    for mid, o in list(off.items()):
        if o >= -k:
            continue
        src = (-k - 1) - earliest
        off[mid] = lo if hi < lo or src <= 0 else lo + round((o - earliest) * (hi - lo) / src)
    order = {s[0]: i for i, s in enumerate(specs)}
    slot = {s[0]: s[2] for s in specs}
    sends = sorted([m for m in off if is_list_send(m)], key=lambda m: (off[m], slot[m], order[m]))
    days_open = list(range(-lead, 1))
    cap = MAX_LIST_SENDS_A_DAY * len(days_open)
    dropped = []
    drops = RUSH_DROP_ORDER + [m for m in sends if m.startswith("invite_")][1:-1]
    for m in drops:
        if len(sends) <= cap:
            break
        if m in sends:
            sends.remove(m); dropped.append(m); off.pop(m)
    slots = [d for d in days_open for _ in range(MAX_LIST_SENDS_A_DAY)]
    idx = -1
    for i, m in enumerate(sends):
        want = next((j for j, d in enumerate(slots) if d >= off[m]), len(slots) - 1)
        j = min(max(idx + 1, want), len(slots) - (len(sends) - i))
        off[m], idx = slots[j], j
    if "invite_1" in off and "confirmation" in off:
        off["confirmation"] = off["invite_1"]          # live from the first invitation, as planned
    return off, dropped


def cmd_timeline(a):
    on = today(a)
    ev = parse_date(a.event_date, "--event-date")
    check_tz(a.tz)
    if a.days < 1:
        refuse("--days must be 1 or more")
    if a.format and a.format not in FORMATS:
        refuse(f"--format must be one of {sorted(FORMATS)}")
    if a.format == "roundtable" and a.days != 1:
        refuse("--format roundtable is a one-day session (--days 1)")
    final = ev + dt.timedelta(days=a.days - 1)
    given = [x for x in ("--cart-days" if a.cart_days is not None else None,
                         "--deadline-date" if a.deadline_date else None, "--no-deadline" if a.no_deadline else None) if x]
    if not given:
        refuse("say how the cart closes: --cart-days N (the cart closes N days after the final day), --deadline-date "
               "YYYY-MM-DD, or --no-deadline (no deadline, chosen on purpose). There is no default deadline")
    if len(given) > 1:
        refuse(f"give one of --cart-days, --deadline-date or --no-deadline (got {', '.join(given)})")
    cart_days = a.cart_days
    if a.deadline_date:
        dd = parse_date(a.deadline_date, "--deadline-date")
        cart_days = (dd - final).days
        if cart_days < 0:
            refuse(f"--deadline-date {dd} is before the final day ({final})")
    if cart_days is not None and cart_days < 0:
        refuse("--cart-days must be 0 or more")
    country = a.country or default_country(a.tz)
    if country not in COUNTRIES:
        refuse(f"--country must be one of {', '.join(COUNTRIES)} (got {a.country!r})")
    lead = (ev - on).days
    if lead < 0:
        refuse(f"--event-date {ev} is in the past (today is {on})")
    minimum = 56 if a.partners else (28 if a.paid_event else 21)
    why = ("8 weeks to recruit partners (Amber Spears: 90 days; big partners are booked months ahead)" if a.partners
           else "28 days for a paid event's ticket sales and the belief emails before them" if a.paid_event
           else "21 days: three belief emails, the first-win tool emails and about 14 days of invitations")
    if lead < minimum and not a.rush:
        refuse(f"Day 1 ({ev}) is {lead} days away; this plan needs at least {minimum} days ({why}). Move the date, or "
               f"pass --rush to compress the plan (at most {MAX_LIST_SENDS_A_DAY} list sends a day; belief and tool "
               "emails dropped first)")
    deadline = not a.no_deadline
    specs = milestone_specs(a.days, a.partners, a.paid_event, cart_days or 0, a.invites, deadline, a.close, a.sms,
                            a.waitlist, a.format)
    offsets, dropped = rush_layout(specs, lead) if lead < minimum else ({s[0]: s[1] for s in specs}, [])
    ms, warnings = [], []
    soft_used, hard_used = False, False
    for mid, off0, slot, kind, title, detail, src in specs:
        if mid in dropped:
            continue
        off = offsets[mid]
        d = ev + dt.timedelta(days=off)
        planned = ev + dt.timedelta(days=off0)
        row = {"id": mid, "date": d.isoformat(), "weekday": d.strftime("%a"), "days_from_day1": off, "kind": kind,
               "title": title, "detail": detail, "source": src}
        if d < on:
            d = on
            row.update({"date": on.isoformat(), "weekday": on.strftime("%a"), "days_from_day1": -lead})
        if d != planned:
            row.update({"compressed": True, "planned": planned.isoformat()})
        if kind in ("send", "event"):
            h, soft = holiday(d, country)
            if h:
                row["holiday"] = h
                if soft:
                    row["holiday_soft"] = True
                soft_used, hard_used = soft_used or soft, hard_used or not soft
            if d.weekday() >= 5:
                row["weekend"] = True
        ms.append(row)
    comp = [m["id"] for m in ms if m.get("compressed")]
    if comp and lead < minimum:
        warnings.append(f"--rush: {lead} days is under the {minimum}-day minimum ({why}); compressed proportionally "
                        f"(planned dates kept on each row): {', '.join(comp)}")
    elif comp:
        warnings.append(f"compressed to today ({on}): {', '.join(comp)}; these were due earlier")
    if dropped:
        warnings.append(f"--rush: not enough days for every list email at {MAX_LIST_SENDS_A_DAY} a day; left out: "
                        f"{', '.join(dropped)}")
    per_day = {}
    for m in ms:
        if m["kind"] == "send" and is_list_send(m["id"]):
            per_day.setdefault(m["date"], []).append(m["id"])
    crowded = {d: v for d, v in per_day.items() if len(v) > MAX_LIST_SENDS_A_DAY}
    if crowded:
        warnings.append("more than two list sends on one day: " + "; ".join(f"{d}: {', '.join(v)}" for d, v in crowded.items()))
    sd = next((m for m in ms if m["id"] == "sending_domain"), None)
    if sd and sd.get("compressed"):
        first = next((m["date"] for m in ms if is_list_send(m["id"])), None)
        warnings.append(f"sending domain: under 28 days before the first list email ({first}). If the list does not "
                        "already send well from a warmed domain, warm one now (2–4 weeks) or expect the spam folder")
    if a.sms:
        sr = next((m for m in ms if m["id"] == "sms_registration"), None)
        if sr and sr.get("compressed"):
            warnings.append("sms_registration: A2P 10DLC approval can take weeks; until it is approved, send email only")
    if a.partners and lead < 84:
        warnings.append(f"partner recruitment has {lead} days, under the 12 weeks planned (Amber Spears' 90-day rule): "
                        "expect fewer and smaller partner slots")
    for m in ms:
        if m["kind"] == "event" and m.get("weekend"):
            warnings.append(f"{m['title']} falls on a {m['weekday']}: check your audience can make a weekend session")
    hol = [m for m in ms if m.get("holiday") and (m["kind"] == "event" or m["id"].startswith("invite_"))]
    for m in hol:
        warnings.append(f"{m['title']} ({m['date']}) falls on {m['holiday']}: inboxes are full and people are away; "
                        "move it or expect less")
    other_hol = [m for m in ms if m.get("holiday") and m not in hol]
    if other_hol:
        warnings.append("other sends on a holiday: " + ", ".join(f"{m['id']} {m['date']} ({m['holiday']})" for m in other_hol))
    wk = [m for m in ms if m["kind"] == "send" and m.get("weekend")]
    if wk:
        warnings.append("sends on a weekend (opens are usually lower; fine if your audience reads then): "
                        + ", ".join(f"{m['id']} {m['weekday']} {m['date']}" for m in wk))
    if not deadline:
        warnings.append("--no-deadline: no cart close is planned; the follow-up ends on a stated day instead. An honest "
                        "deadline (a start date, a cohort, a price change) usually helps the close")
    order = {s[0]: i for i, s in enumerate(specs)}
    slots = {s[0]: s[2] for s in specs}
    ms.sort(key=lambda m: (m["date"], slots[m["id"]], m.get("planned", m["date"]), order[m["id"]]))
    cart_close = (final + dt.timedelta(days=cart_days)).isoformat() if deadline else None
    out = {"event_date": ev.isoformat(), "days": a.days, "tz": a.tz, "final_day": final.isoformat(),
           "deadline": deadline, "cart_close": cart_close, "deadline_date": cart_close,
           "cart_days": cart_days if deadline else None, "invites": a.invites, "close": a.close,
           "format": a.format, "sms": bool(a.sms), "waitlist": bool(a.waitlist), "country": country,
           "today": on.isoformat(), "lead_days": lead, "minimum_lead_days": minimum, "rush": lead < minimum,
           "partners": bool(a.partners), "paid_event": bool(a.paid_event), "milestones": ms}
    if dropped:
        out["dropped"] = dropped
    if warnings:
        out["warnings"] = warnings
    out["sources"] = sources_used(ms)
    if hard_used and country in COUNTRY_SOURCE:
        out["sources"][COUNTRY_SOURCE[country]] = SOURCES[COUNTRY_SOURCE[country]]
    if soft_used:
        out["sources"]["Holiday soft flags"] = SOURCES["Holiday soft flags"]
    if a.out:
        folder = out_dir(a.out)
        out["folder"] = str(folder)
        out["written"] = [update_plan(folder, "timeline", out)]
        cal = folder / "calendar.md"
        cal.write_text(calendar_md(out), encoding="utf-8")
        out["written"].append(str(cal))
    return out


def calendar_md(t):
    ev = dt.date.fromisoformat(t["event_date"])
    lines = [f"# Launch calendar: Day 1 {ev.strftime('%a')} {ev} ({t['days']} day{'s' if t['days'] > 1 else ''}, {t['tz']})", ""]
    by_week = {}
    for m in t["milestones"]:
        d = dt.date.fromisoformat(m["date"])
        by_week.setdefault(d - dt.timedelta(days=d.weekday()), []).append(m)
    first, last = min(by_week), max(by_week)
    monday = first
    while monday <= last:
        n = (ev - monday).days // 7
        label = ("after the event" if monday > ev else "event week" if (ev - monday).days < 7
                 else f"{n} week{'s' if n != 1 else ''} out")
        lines += ["", f"## Week of Mon {monday} ({label})", "", "| Date | Day | Milestone | What |", "|---|---|---|---|"]
        rows = by_week.get(monday, [])
        if not rows:
            lines.append("| – | – | (no milestones this week) | keep promoting and answering replies |")
        for m in rows:
            flag = f" ⚠️ compressed (planned {m['planned']})" if m.get("compressed") else ""
            flag += f" ⚠️ {m['holiday']}" if m.get("holiday") else ""
            flag += " (weekend)" if m.get("weekend") else ""
            lines.append(f"| {m['date']} | {m['weekday']} | **{m['title']}**{flag} | {m['detail']} |")
        monday += dt.timedelta(days=7)
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
    hist = {k: rate(getattr(a, f"history_{k.replace('-', '_')}"), f"--history-{k}")
            for k in ("reg-rate", "showup", "retention", "stay", "conversion", "booked", "held", "closed")
            if getattr(a, f"history_{k.replace('-', '_')}")}
    hist = {{"reg-rate": "reg", "showup": "show"}.get(k, k): v for k, v in hist.items()}
    uplift = None
    if a.replay_uplift is not None:
        try:
            uplift = float(a.replay_uplift)
        except ValueError:
            refuse(f"--replay-uplift must be a number such as 1.25 (got {a.replay_uplift!r})")
    ticket = money(a.ticket_price, "--ticket-price") if a.ticket_price else None
    vip = money(a.vip_price, "--vip-price") if a.vip_price else None
    vrate = rate(a.vip_rate, "--vip-rate") if a.vip_rate else None
    r = compute_math(a.goal_buyers, cash, price, tiers, a.list_size, a.format, a.days, a.paid_event, hist, a.close, uplift,
                     ticket, vip, vrate)
    if a.out:
        folder = out_dir(a.out)
        r["folder"] = str(folder)
        r["written"] = [update_plan(folder, "math", r)]
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
    s.add_argument("--ticket-price"); s.add_argument("--vip-price"); s.add_argument("--vip-rate")
    s.add_argument("--close", choices=CLOSE_MODES, default="checkout"); s.add_argument("--replay-uplift")
    for k in ("reg-rate", "showup", "retention", "stay", "conversion", "booked", "held", "closed"):
        s.add_argument(f"--history-{k}")
    s.add_argument("--md", nargs="?", const="-"); s.add_argument("--out"); s.add_argument("--date")
    s = sub.add_parser("timeline")
    s.add_argument("--event-date", required=True); s.add_argument("--days", type=int, required=True)
    s.add_argument("--tz", required=True); s.add_argument("--partners", action="store_true")
    s.add_argument("--paid-event", action="store_true"); s.add_argument("--cart-days", type=int)
    s.add_argument("--deadline-date"); s.add_argument("--no-deadline", action="store_true")
    s.add_argument("--invites", type=int, choices=[5, 7], default=7)
    s.add_argument("--close", choices=CLOSE_MODES, default="checkout"); s.add_argument("--format")
    s.add_argument("--sms", action="store_true", help="texts are planned: adds sms_registration (A2P 10DLC)")
    s.add_argument("--waitlist", action="store_true", help="adds the waitlist milestones")
    s.add_argument("--country", help="US, UK, CA, AU, IE or none (default from --tz)")
    s.add_argument("--rush", action="store_true"); s.add_argument("--out"); s.add_argument("--date")
    a = ap.parse_args(argv)
    today(a)
    out = {"math": cmd_math, "timeline": cmd_timeline}[a.cmd](a)
    if out is not None:
        print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
