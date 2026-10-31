#!/usr/bin/env python3
"""Event Launcher tracker: the launch ledger, the staged launch gate, pacing, the debrief and the Obsidian note.

Local only. It stores what the member tells it (counts, prices, gate answers) in one JSON file per
launch. It never contacts Zoom, GoHighLevel or Stripe, and import-csv keeps counts only: no names,
emails or phone numbers from the export are stored. Sources such as partner:NAME, email:ID or
segment:NAME are the member's own labels (a short code or a first name is enough); they are stored
in the ledger and printed in the debrief and the Obsidian note, so use a code when a partner should
not be named in the vault.

Usage
  The ledger is launches/<slug>/tracker.json under the current folder; init makes the slug YYYY-MM-<name>
  from the event date and the name (or --slug S). Pick a ledger with --slug S or --file P; with neither,
  the only tracker under ./launches/ is used; with several, the one whose event is the nearest upcoming
  (or running), else the most recent past, and the output says which ("ledger"). Only init creates a
  ledger; every other command refuses when it is missing. --date YYYY-MM-DD replays "today".

  launch_tracker.py slug --name "Cash Flow Bootcamp" --event-date YYYY-MM-DD
      prints the slug and the launch folder init will use, without creating anything (so plan.json can be
      written there first: launch_plan.py math --out <slug>).
  launch_tracker.py init --name "Cash Flow Bootcamp" --format bootcamp3|challenge5|workshop|webinar|roundtable
                         --days N --tz IANA --event-date YYYY-MM-DD --goal-buyers N --goal-cash X [--paid-event]
                         [--close checkout|call|both] [--list-size L] [--plan plan.json] [--sms]
                         [--event event.json] [--slug S] [--test]
      --plan reads launch_plan.py's plan.json: the typical path is the plan. It stores what the goal NEEDS
      (needed_for_goal) and what the list should give (expected_from_list) separately; leaks are judged
      against the expected path and the goal gap is shown on its own. Without --plan the plan is the
      typical path of the Build Room benchmarks (with --list-size for an expected path). --close (default:
      the plan's close, else checkout) picks the gate's money items and the funnel's close stages.
      SMS is planned when --sms is given, the plan's timeline was made with --sms, or event.json (--event,
      or the launch folder's event.json) sets reminders.sms; then sms_compliance is a critical gate item,
      otherwise it is na ("email only"). --test marks the ledger as test/synthetic data: report and the
      Obsidian note say TEST, and obsidian-read skips it. Prints the slug and the folder.
  launch_tracker.py log-reg N [--source list|ads|social|partner:NAME|email:ID|segment:NAME] [--date]
  launch_tracker.py log-day --day 1 --live N [--peak N] [--source-count SOURCE=N ...] [--date]
      --live is the UNIQUE attendees that day (the Zoom participant report, one row per person), the
      same definition as the show-up and retention benchmarks and as import-csv. --peak (optional) is the
      peak concurrent count, stored separately for reference. Show-up, retention and stay to the close are
      measured on unique attendees. --source-count partner:Jo=40 (repeatable) records attendees by source.
  launch_tracker.py log-close --present N --saw-price N [--date]
      present: in the room when the offer was made; saw the price: everyone who saw it, live or later
  launch_tracker.py log-sale --tier NAME --price P --count N [--payment full|plan --booked TOTAL] [--via checkout|call]
                             [--source SOURCE] [--date]
      full: cash and booked are price × count. plan: --price is what each buyer has paid so far (the
      first instalment) and --booked is the total contract value of these N sales (required).
      --via call: cash collected on deals closed on a call; it adds cash only (buyers and booked value of
      call deals come from log-calls). --source partner:NAME attributes the sale to a partner.
  launch_tracker.py log-calls --booked N --held N --closed N --value X [--tier NAME] [--source SOURCE] [--date]
      calls (or applications) booked, held and closed since the last entry; --value is the booked value of
      the deals closed. Totals must keep closed ≤ held ≤ booked.
  launch_tracker.py log-refund --tier NAME --count N --amount TOTAL [--booked-cancelled X] [--source SOURCE] [--date]
      amount: cash refunded (never more than the cash collected for that tier, less earlier refunds);
      --booked-cancelled: unpaid instalments cancelled with the refund
  launch_tracker.py log-tickets --count N --price T [--vip-count N --vip-price V] [--source SOURCE] [--date]
      a paid event's tickets (tier "Tickets") and VIP upgrades (tier "VIP upgrade"): cash and booked, never
      counted as buyers of the offer; log-refund --tier Tickets refunds them.
  launch_tracker.py partner --name NAME --rate R      (--commission-rate R is the same flag)
      the commission rate for partner:NAME ("30%" or 0.3); the report shows, per partner, registrations,
      attendees (if logged by source), buyers, cash, refunds and the commission due on net cash, paid after
      the refund window.
  launch_tracker.py import-csv FILE --map registered=TAG,day1=TAG,day2=TAG,present=TAG,saw_price=TAG [--replace]
      counts rows of a CRM export (GoHighLevel contacts CSV) whose tags column holds each tag (TAG * counts
      every row). A day count is unique tagged contacts, the same definition as log-day --live. Only the
      mapped fields change. A count that would lower or overwrite a logged number different from it is
      refused unless --replace (then registrations become one "import" entry, never a negative one; a
      day's other fields are kept). Prints a before/after table. Only counts and the file name are stored.
  launch_tracker.py gate [--stage pre_invite|day_before|close_morning|cart] [--set ITEM pass|fail|na|open "note" ...]
                         [--reset ITEM ...] [--close-morning]
      the launch gate in four stages: pre_invite (before the first email of any kind), day_before (24 hours
      before Day 1), close_morning (the money and follow-up, that morning) and cart (before the cart and
      follow-up emails). --stage S shows and judges only that stage's items; without --stage every item is
      shown with GO/HOLD per stage. A stage is GO when each of its critical items passes (or is na with a
      note). A critical item set to pass or na needs a note (what was tested, by whom, on what device).
      Each entry records its stage and tested_at. An item judged again at a later stage (the terms at
      close_morning, proof and claims at cart) needs a pass recorded at that stage; close_morning passes
      must be dated today (or --date). --set without --stage records the item's first stage not yet
      passed. --reset ITEM puts an item back to open. --close-morning is --stage close_morning.
  launch_tracker.py pace [--date]
      registrations to date against the expected path's pacing curve across the invitation window (from
      the plan's first invitation, else 14 days out; 21 for a paid event) to Day 1. The curve has the
      Livestorm 2026 shape: 15.3% of registrations on the day, 49.6% in the final week (the day included),
      the rest spread evenly over the earlier days. Says ahead (≥110%), on pace or behind (<90%), and
      whether it is below the cautious registration rate's curve.
  launch_tracker.py report [--md [FILE]] [--force]
      funnel against the expected path (and what the goal needed), day-over-day retention, the close
      stages (checkout conversion; calls booked, held and closed), cash vs booked (tickets and VIP
      included), refunds, revenue per registrant, registrations by source, partners, benchmark ranges with
      sources (the plan's member history when it had one), the top three leaks ranked by buyers lost
      against the expected path with a fix for each, the goal gap, and what to protect. --md writes the
      markdown to the launch folder's debrief-numbers.md (or FILE) between start and end markers. It never
      writes a file named debrief.md (the member's own debrief), and never overwrites a file it did not
      write, or one with text added outside its markers, without --force.
  launch_tracker.py obsidian --vault PATH [--force] [--no-obsidian-check] [--status S] [--lesson "..." ...]
      writes the debrief to <vault>/launches/YYYY-MM-<slug>.md (light frontmatter; the slug already
      starts with YYYY-MM) and adds one line to <vault>/launches/_index.md (created if missing, and
      back-filled with older launch notes it lacks). The index lines it writes end in a hidden marker
      (<!-- launch_tracker -->); it updates only those, appends new ones at the end and never re-sorts or
      changes a line the member wrote. An existing note is never overwritten without --force. Refused when
      the vault folder is missing or has no .obsidian folder (--no-obsidian-check writes anyway, with a
      warning). --lesson (repeatable) is kept in the ledger, so a later --force rewrite keeps it. A test
      ledger's note says TEST and carries test: true.
  launch_tracker.py obsidian-read --vault PATH [--no-obsidian-check] [--include-test] [--author NAME ...]
      lists the member's past launch notes, newest first (frontmatter date, else a date in the file name;
      undated last), so the plan can start from earlier lessons. A note counts when its frontmatter type is
      launch, debrief, event, audit, retro, review, post-mortem or prep; when its tags (inline [a, b],
      a YAML block list or a comma list; whole tags only) hold launch, debrief, event, retro, post-mortem
      or audit; when its file name or title says debrief, retro, post-mortem, launch review or audit
      (anywhere in the vault, frontmatter or not); or, directly in launches/, when its file name looks like
      a launch. Left out: templates (a folder named templates, Templates or "99 Templates", or a note
      holding {{date}} / {{title}}), imported material (External, Sources, Readwise, Clippings,
      transcripts, Flight Club and similar folders; a note whose frontmatter type is source, transcript,
      clipping, reference or podcast, or whose source/url points to a web page, or whose author/speaker is
      someone other than --author), client notes (type: client, a client tag, or a clients/ folder), work
      folders inside launches/ and test notes. Headings are matched case-insensitively at any level by the
      words they contain: results (Results, Numbers, Metrics, Scoreboard, Funnel, Outcome), lessons
      (Lessons, Key lessons, Lessons learned, What broke, What went wrong, Leaks, Takeaways, Next time,
      What I'd change), protect (What to protect, Protect, What worked, What went well, Wins, Keep). A
      section runs to the next heading of the same or a higher level, so ### sub-headings stay inside it.
      Email addresses and phone numbers are redacted from everything returned. Warns, naming where it
      looked, when nothing is found or a note has none of those headings (it then returns the start of
      the body, redacted). Needs no tracker.

Gate items (references/launch-gate.md); C critical, A advisory; stage first, then any later re-check
  pre_invite     C registration_path_tested email_compliance partner_disclosure partner_copy_true single_source
                   proof_classified (+cart) earnings_claims (+cart) claims_substantiated (+cart) retired_lines
                   real_deadlines (+cart) refund_policy (+close_morning) payment_plan_terms (+close_morning)
                   renewal_terms (+close_morning) recording_notice sms_compliance (critical when SMS is planned,
                   else na)
                 A privacy_notice first_win_timed
  day_before     C reminder_tz night_emails (na for a single-day event) followup_on (+close_morning)
                   replay_release (na with a note when there is no replay) checkout_tested backup_checkout
                   (checkout/both; +close_morning) booking_tested backup_booking (call/both; +close_morning)
                 A moderator_links live_tech_rehearsed
  close_morning  C the money path for the close mode, refund_policy payment_plan_terms renewal_terms followup_on
                 A chargeback_ready
  cart           C testimonial_permission, and the re-checks of proof_classified earnings_claims
                   claims_substantiated real_deadlines
                 A refund_commissions

Standard library only. Exit code 2 on a refused action (missing ledger, bad input, existing note).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, csv, datetime as dt, json, math, os, re, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import launch_plan  # noqa: E402

SCHEMA = "buildroom-event-launcher/1"
ROOT = "launches"
SRC_RE = re.compile(r"^(list|ads|social|import|partner:[\w .&'-]+|email:[\w.@-]+|segment:[\w .&'-]+)$", re.I)
CLOSE_MODES = launch_plan.CLOSE_MODES
MARKER = "<!-- written by launch_tracker.py report: re-running the report replaces this file -->"
END_MARKER = "<!-- end of launch_tracker.py report: anything below this line stops the report from overwriting -->"
INDEX_MARK = "<!-- launch_tracker -->"
LIVE_DEF = "unique attendees (Zoom participant report)"
STATUSES = ("open", "pass", "fail", "na")

SOURCES = dict(launch_plan.SOURCES)
SOURCES.update({
    "FTC 16 CFR 465": "FTC Consumer Reviews and Testimonials Rule (in force 21 Oct 2024): no fake or misleading "
                      "testimonials, civil penalties per violation",
    "FTC earnings claims": "FTC guidance: earnings claims must reflect typical results; 'results not typical' is no cure",
    "FTC substantiation": "FTC Act §5 and the FTC's substantiation policy: objective performance claims (time saved, "
                          "results, speed) need a reasonable basis before they are made",
    "FTC dark patterns 2022": "FTC staff report 'Bringing Dark Patterns to Light': baseless countdown timers are "
                              "deceptive; the UK DMCC Act bans false time limits",
    "CAN-SPAM and bulk-sender rules": "CAN-SPAM: postal address, working opt-out honoured within 10 business days; "
                                      "Gmail/Yahoo/Microsoft: SPF, DKIM, DMARC aligned, one-click unsubscribe",
    "TCPA and A2P 10DLC": "Marketing texts need prior express written consent and 8 a.m.–9 p.m. local sends; "
                          "GoHighLevel will not send US SMS without an approved A2P 10DLC brand and campaign",
    "Recording consent": "Several US states need everyone's consent to record; announce it and keep Zoom's notice on",
    "Refund disclosure": "FTC: disclose refund terms before payment and honour them; Stripe Checkout can require "
                         "terms acceptance",
    "Payment plan rules": "ROSCA and state auto-renewal laws: show all terms before billing; Stripe subscription "
                          "schedules end a fixed plan (end_behavior: cancel)",
    "Auto-renewal rules": "ROSCA and state automatic-renewal laws: renewal terms clear and conspicuous before "
                          "billing, express informed consent, a simple way to cancel (online if it was sold online)",
    "Business File protocol": "The member's Business File: §1 Retired lines and §18 Never-say bind every word, "
                              "paraphrases included",
    "FTC Endorsement Guides 2023": "Affiliates and JV partners disclose any material connection (commission) clearly; "
                                   "the advertiser is responsible too",
    "Privacy notice": "GDPR / UK GDPR: state what is collected, why and the lawful basis at collection; consent is "
                      "never a pre-ticked box",
    "Card network rules 2026": "Visa VAMP: the US 'excessive' dispute ratio fell from 2.2% to 1.5% on 1 Apr 2026; "
                               "Mastercard ECM at 100 chargebacks and 1.5%",
})

ALL = set(CLOSE_MODES)
CHECKOUT, CALL = {"checkout", "both"}, {"call", "both"}
STAGES = ("pre_invite", "day_before", "close_morning", "cart")
STAGE_WHEN = {"pre_invite": "before the first email of any kind", "day_before": "24 hours before Day 1",
              "close_morning": "the morning of the close, on a phone", "cart": "before the cart and follow-up emails"}
PI, DB, CM, CA = STAGES
# id, critical, group, what must be true, source, close modes it applies to, stages (first stage, then re-checks).
# references/launch-gate.md holds the same list in prose. sms_compliance is critical only when SMS is planned.
GATE = [
    ("registration_path_tested", True, "sending", "Registration page, thank-you page (with the calendar file) and the "
     "confirmation email tested end to end with a test contact on a phone", "Build Room founder method", ALL, (PI,)),
    ("email_compliance", True, "sending", "CAN-SPAM footer (postal address), one-click unsubscribe plus a visible link; "
     "SPF, DKIM and DMARC aligned on a sending subdomain", "CAN-SPAM and bulk-sender rules", ALL, (PI,)),
    ("partner_disclosure", True, "sending", "Partners disclose their commission in every promotion that pays them (na if "
     "no partners)", "FTC Endorsement Guides 2023", ALL, (PI,)),
    ("partner_copy_true", True, "truth", "Who teaches live is named in every invitation; partner and guest copy never "
     "implies someone will appear who won't", "Build Room founder run Jul 2026", ALL, (PI,)),
    ("single_source", True, "truth", "One source of truth (close.md) for prices, terms, dates, replay links and expiry",
     "Build Room founder method", ALL, (PI,)),
    ("proof_classified", True, "truth", "Proof classified (free-event result / paid-program result / outside example) and "
     "every person's consent on file; at the cart stage, again for every story and quote the cart and follow-up "
     "emails use", "FTC 16 CFR 465", ALL, (PI, CA)),
    ("earnings_claims", True, "truth", "Earnings claims are typical results, or there are none", "FTC earnings claims", ALL,
     (PI, CA)),
    ("claims_substantiated", True, "truth", "Non-earnings performance claims (time saved, results, speed: 'save 20+ hours "
     "a week') are typical and backed by evidence, or removed", "FTC substantiation", ALL, (PI, CA)),
    ("retired_lines", True, "truth", "Every email, page and slide checked against the Business File's §1 Retired lines "
     "(paraphrases included) and §18 Never-say claims", "Business File protocol", ALL, (PI,)),
    ("real_deadlines", True, "truth", "Deadlines are real and the same for everyone, or honest per-person timers, or "
     "there is none: no resetting countdowns, no fake 'doors close', no 'live' label on a recording",
     "FTC dark patterns 2022", ALL, (PI, CA)),
    ("refund_policy", True, "money", "Refund or guarantee terms shown before payment and accepted at checkout, in the same "
     "words as the sales page and the live close (one guarantee, not two)", "Refund disclosure", ALL, (PI, CM)),
    ("payment_plan_terms", True, "money", "Payment plans are fixed-length and the total (payments × amount) is shown before "
     "checkout (na if there is no plan)", "Payment plan rules", ALL, (PI, CM)),
    ("renewal_terms", True, "money", "Anything that renews (subscription, membership, annual plan) has its renewal terms "
     "disclosed before payment, express consent to them, and online cancellation as easy as sign-up (na with a note "
     "when nothing renews)", "Auto-renewal rules", ALL, (PI, CM)),
    ("recording_notice", True, "consent", "Recording announced on the registration page and at the start of each day; "
     "Zoom's recording notice on", "Recording consent", ALL, (PI,)),
    ("sms_compliance", True, "consent", "SMS only with written consent (a separate, unchecked box) and an approved A2P "
     "10DLC brand and campaign, sent 9 a.m.–8 p.m. in the contact's zone (critical when SMS is planned; na when the "
     "launch is email only)", "TCPA and A2P 10DLC", ALL, (PI,)),
    ("privacy_notice", False, "consent", "Privacy notice on the registration page (what, why; for EU/UK the lawful basis "
     "and a separate marketing consent)", "Privacy notice", ALL, (PI,)),
    ("first_win_timed", False, "live", "The first-win tool timed: the invitation states the measured time, not a guess",
     "Build Room founder run Jul 2026", ALL, (PI,)),
    ("reminder_tz", True, "follow-up", "Reminder send times verified in the recipient's time zone and the whole schedule "
     "dry-run 24 hours before Day 1 (GoHighLevel's 'Set Event Start Date' uses the account time zone)", "GHL help 2026",
     ALL, (DB,)),
    ("night_emails", True, "follow-up", "A night-before email pre-written and scheduled for every day after Day 1 "
     "(Day-1-night, Day-2-night…)", "Build Room founder run Jul 2026", ALL, (DB,)),
    ("followup_on", True, "follow-up", "Every follow-up workflow switched ON (checked in the CRM) and tested with a test "
     "contact: confirmation, reminders, night-before, replay, no-show, cart, failed checkout, buyer welcome",
     "Build Room founder run Jul 2026", ALL, (DB, CM)),
    ("replay_release", True, "consent", "People shown on camera or named in the replay agreed (registration terms and the "
     "on-air notice), or are cut, blurred or unnamed before it goes out (na with a note when there is no replay)",
     "Recording consent", ALL, (DB,)),
    ("checkout_tested", True, "money", "Checkout tested end to end on a phone for every tier, the payment plan and the "
     "coupon or VIP checkbox (real card, then refunded); again on the close morning", "Build Room founder run Jul 2026",
     CHECKOUT, (DB, CM)),
    ("backup_checkout", True, "money", "A second checkout path ready: a plain payment link per tier the moderator can drop "
     "in chat", "Build Room founder run Jul 2026", CHECKOUT, (DB, CM)),
    ("booking_tested", True, "money", "Booking path tested end to end on a phone: the booking or application link, the "
     "calendar or form, the confirmation and reminder, and the payment link sent within the hour after a yes; again on "
     "the close morning", "Build Room founder run Jul 2026", CALL, (DB, CM)),
    ("backup_booking", True, "money", "A backup booking link (a second calendar or application form, or a direct "
     "contact) the moderator can drop in chat", "Build Room founder run Jul 2026", CALL, (DB, CM)),
    ("moderator_links", False, "live", "A moderator assigned, with every link they will drop and when, and a backup host "
     "link", "Build Room founder method", ALL, (DB,)),
    ("live_tech_rehearsed", False, "live", "Anything new (breakout rooms, a live app, polls) tried with five people first, "
     "or not used", "Build Room founder run Jul 2026", ALL, (DB,)),
    ("chargeback_ready", False, "money", "Chargeback exposure understood: a clear refund path (Visa's US 'excessive' ratio "
     "is 1.5% from April 2026)", "Card network rules 2026", ALL, (CM,)),
    ("testimonial_permission", True, "consent", "Written permission before reusing anyone's chat comment or live words as "
     "a testimonial in the cart and follow-up emails (na with a note when none are quoted)", "FTC 16 CFR 465", ALL, (CA,)),
    ("refund_commissions", False, "money", "Refunds reverse partner commissions (GoHighLevel does not do it automatically)",
     "GHL help 2026", ALL, (CA,)),
]
GATE_BY_ID = {g[0]: g for g in GATE}


def gate_ids(mode):
    return [g[0] for g in GATE if mode in g[5]]


def stage_ids(mode, stage):
    return [g[0] for g in GATE if mode in g[5] and stage in g[6]]


def close_morning_ids(mode):
    return stage_ids(mode, CM)


STAGE_FIX = {
    "registration": "Registrations short of the expected path: invite earlier and more often (about half of "
                    "registrations land in the final week), add a partner wave, keep registration open through Day 1",
    "show_up": "Day-1 show-up: calendar file on the thank-you page; reminders the day before, the morning of and 15 "
               "minutes before (SMS only with consent); pre-work that makes being live worth it",
    "retention": "Day {a}→{b} drop: a Day-{a}-night recap with the Day-{b} payoff, a cliffhanger that only pays off live, "
                 "reminder times checked in the recipient's time zone",
    "stay_to_close": "People left before the offer: say when it comes, keep the promised build for after it, keep the "
                     "session inside the planned length",
    "saw_price": "Attendees who never saw the price: switch on the follow-up that shows the offer to everyone who "
                 "attended (replay with the offer, follow-up emails); the founder's July run lost sales this way",
    "conversion": "Price-viewers who didn't buy: test the checkout on a phone the morning of the close, an honest "
                  "deadline only if one is true, a clear 'which one are you' ladder, let ready buyers buy early",
    "booked": "Few calls booked: make the call the one next step at the offer, the booking link on screen and in chat "
              "from the pitch onwards, someone in chat booking people live",
    "held": "Booked calls that didn't happen: book within 48 hours, a confirmation and reminders, a short pre-call form, "
            "a personal note to each no-show the same day",
    "closed": "Held calls that didn't buy: one clear offer and price on the call, the same script every call, the "
              "payment link within the hour after a yes, a real start date",
}
STAGE_KEEP = {
    "registration": "keep the invitation sequence and the partner wave as they were",
    "show_up": "keep the reminder schedule, the calendar file and the pre-work exactly as they were",
    "retention": "keep the night-before recap and the payoff that only happens live",
    "stay_to_close": "keep the offer timing and the session length",
    "saw_price": "keep the follow-up that put the offer in front of everyone",
    "conversion": "keep the offer, the price ladder and the checkout as they were",
    "booked": "keep the call-to-action at the offer and the live booking help",
    "held": "keep the confirmation and reminder flow for calls",
    "closed": "keep the call script and the same-hour payment link",
}
LIVESTORM_DAY = .153
LIVESTORM_WEEK = .496      # the final week, the day included


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


parse_date = launch_plan.parse_date
slugify = launch_plan.slugify


def today(a):
    return launch_plan.today(a)


def plural(n, word, many=None):
    return f"{launch_fmt(n)} {word if n == 1 else (many or word + 's')}"


def launch_fmt(x):
    return "–" if x is None else f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)


def save(path, data):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tracker-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def load(path):
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        refuse(f"{path} is not readable JSON ({e}); restore it from a backup or fix it by hand")
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        refuse(f"{path} is not an Event Launcher tracker file")
    data.setdefault("close_mode", "checkout")
    data.setdefault("calls", [])
    data.setdefault("partners", {})
    older = "sms" not in data                             # ledgers written before SMS was tracked
    data.setdefault("sms", False)
    if data.get("live_definition") != "unique":           # ledgers written when --live was the peak count
        for e in (data.get("days_live") or {}).values():
            if "unique" in e:
                e["peak"], e["live"] = e["live"], e.pop("unique")
            elif not e.get("imported"):
                e["definition"] = "peak concurrent (older ledger)"
        data["live_definition"] = "unique"
    gate = data.setdefault("gate", {})
    for gid in gate_ids(data["close_mode"]):
        gate.setdefault(gid, {"status": "open"})
    if older and gate.get("sms_compliance", {}).get("status") == "open":
        gate["sms_compliance"] = {"status": "na", "note": "email only: no SMS planned", "auto": True}
    plan = data.get("plan") or {}
    if plan and "needed" not in plan and "registered" in plan:          # ledgers written before plan v2
        data["plan"] = {"needed": {"registrants": plan["registered"], "day_live": plan.get("day_live"),
                                   "present_at_close": plan.get("present"), "saw_price": plan.get("saw_price"),
                                   "buyers": plan.get("buyers")},
                        "expected": None, "rates": plan.get("rates") or {},
                        "per_viewer": {"checkout": (plan.get("rates") or {}).get("conversion"), "booked": 0},
                        "source_keys": plan.get("source_keys") or [], "assumption_only": []}
    return data


def tracker_path(a):
    if a.file:
        return Path(a.file)
    if getattr(a, "slug", None):
        return Path(ROOT) / slugify(a.slug) / "tracker.json"
    if a.cmd == "init":
        return Path(ROOT) / launch_plan.launch_slug(a.name, a.event_date) / "tracker.json"
    found = sorted(Path(ROOT).glob("*/tracker.json"))
    if len(found) == 1:
        return found[0]
    if not found:
        refuse(f"no launch tracker at ./{ROOT}/<slug>/tracker.json. Create one with: launch_tracker.py init --name ... "
               "(or pass --file / --slug if the ledger is elsewhere)")
    on = today(a)
    dated = []
    for p in found:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            start = dt.date.fromisoformat(d["event_date"])
            end = start + dt.timedelta(days=int(d.get("days", 1)) - 1)
        except (ValueError, KeyError, TypeError, OSError, UnicodeDecodeError):
            continue
        dated.append((p, start, end))
    if not dated:
        refuse(f"{len(found)} launch trackers under ./{ROOT}/ and none readable: pass --slug")
    upcoming = sorted((x for x in dated if x[2] >= on), key=lambda x: (x[1], str(x[0])))
    past = sorted((x for x in dated if x[2] < on), key=lambda x: (x[2], str(x[0])), reverse=True)
    pick = (upcoming or past)[0]
    a._ledger_note = {"used": pick[0].parent.name, "event_date": pick[1].isoformat(),
                      "why": ("the nearest upcoming (or running) event" if upcoming else "the most recent past event")
                      + f" of {len(found)} ledgers under ./{ROOT}/",
                      "others": [p.parent.name for p in found if p != pick[0]],
                      "note": "pass --slug to use another"}
    return pick[0]


def nonneg(n, what):
    if n is None or n < 0:
        refuse(f"{what} must be 0 or more")
    return n


def stamp(a):
    """tested_at: the --date replayed (date only), else now to the minute."""
    return a.date if getattr(a, "date", None) else dt.datetime.now().isoformat(timespec="minutes")


# ---------------- plan ----------------

def plan_from_math(m, days, timeline=None):
    if m["inputs"]["days"] != days or "typical" not in m:
        return None
    t = m["typical"]
    plan = {"close": m["inputs"].get("close", "checkout"), "goal_buyers": m["goal"]["buyers"],
            "needed": t["needed_for_goal"], "expected": t.get("expected_from_list"),
            "expected_registrants_range": t.get("expected_registrants_range"),
            "list_size": m["inputs"].get("list_size"),
            "rates": {k: v for k, v in t["rates"].items()}, "per_viewer": t["per_viewer"],
            "history": m["inputs"].get("history") or {},
            "assumption_only": [k for k, v in m["rates"].items() if launch_plan.assumption_only(v)],
            "tiers": m.get("tiers"),
            "source_keys": sorted(launch_plan.sources_used(m["rates"]))}
    if timeline:
        inv = next((x for x in timeline.get("milestones", []) if x["id"] in ("invite_1", "invites_start")), None)
        if inv:
            plan["invites_start"] = inv["date"]
    return plan


def event_sms(path):
    """True when an event.json sets reminders.sms (true or a non-empty list)."""
    try:
        ev = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    v = ((ev or {}).get("reminders") or {}).get("sms") if isinstance(ev, dict) else None
    return bool(v) and v is not False


def sms_planned(data, path=None):
    """(planned, why): SMS is planned by init --sms (or the plan or event.json at init), or by the launch folder's
    event.json now."""
    if data.get("sms"):
        return True, data.get("sms_why") or "init --sms"
    if path:
        ev = Path(path).parent / "event.json"
        if ev.exists() and event_sms(ev):
            return True, f"{ev} sets reminders.sms"
    return False, "email only"


def parse_source(src, what="--source", allow_import=False):
    src = src or "list"
    if not SRC_RE.match(src) or (src.lower() == "import" and not allow_import):
        refuse(f"{what} must be list, ads, social, partner:NAME, email:ID or segment:NAME (got {src!r})")
    if ":" in src:
        k, v = src.split(":", 1)
        return f"{k.lower()}:{v.strip()}"
    return src.lower()


def cmd_slug(a):
    s = launch_plan.launch_slug(a.name, a.event_date)
    folder = Path(ROOT) / s
    return {"slug": s, "folder": str(folder), "tracker": str(folder / "tracker.json"), "exists": folder.exists(),
            "note": "nothing was created; launch_plan.py math/timeline --out " + s + " writes plan.json there"}


def cmd_init(path, a):
    if path.exists():
        refuse(f"a tracker already exists at {path}; use it, or pass --slug for a new launch")
    if a.format not in launch_plan.FORMATS:
        refuse(f"--format must be one of {sorted(launch_plan.FORMATS)}")
    if a.days < 1:
        refuse("--days must be 1 or more")
    launch_plan.check_tz(a.tz)
    ev = parse_date(a.event_date, "--event-date")
    if a.goal_buyers < 1:
        refuse("--goal-buyers must be 1 or more")
    if a.list_size is not None and a.list_size < 1:
        refuse("--list-size must be 1 or more")
    cash = launch_plan.money(a.goal_cash, "--goal-cash")
    warnings, plan, src, pj = [], None, None, {}
    if a.plan:
        pp = Path(a.plan)
        if pp.is_dir():
            pp = pp / "plan.json"
        if not pp.exists():
            refuse(f"no plan at {a.plan}")
        try:
            pj = json.loads(pp.read_text(encoding="utf-8"))
        except ValueError as e:
            refuse(f"{a.plan} is not readable JSON ({e})")
        if pj.get("schema") != launch_plan.PLAN_SCHEMA:
            refuse(f"{a.plan} is not a launch_plan.py plan file")
        if pj.get("math"):
            mi = pj["math"]["inputs"]
            if mi.get("format") != a.format:
                warnings.append(f"the plan's math is for {mi.get('format')}, this launch is {a.format}")
            if pj["math"]["goal"]["buyers"] != a.goal_buyers:
                warnings.append(f"the plan was worked out for {pj['math']['goal']['buyers']} buyers, the goal here is {a.goal_buyers}")
            if a.close and mi.get("close", "checkout") != a.close:
                warnings.append(f"the plan's close is {mi.get('close', 'checkout')}, --close here is {a.close}")
            tl = pj.get("timeline") if (pj.get("timeline") or {}).get("event_date") == ev.isoformat() else None
            plan = plan_from_math(pj["math"], a.days, tl)
            if plan is None:
                warnings.append(f"the plan's math is for {mi['days']} days (or an older plan file), not {a.days}: the "
                                "plan here comes from the Build Room benchmarks instead")
            else:
                src = f"{a.plan} (typical path)"
        else:
            warnings.append(f"{a.plan} has no math section (run launch_plan.py math --out): the plan here comes from "
                            "the Build Room benchmarks")
        if pj.get("timeline") and pj["timeline"].get("event_date") != ev.isoformat():
            warnings.append(f"the plan's timeline is for Day 1 {pj['timeline']['event_date']}, not {ev}")
    mode = a.close or (plan or {}).get("close") or "checkout"
    sms_why = "init --sms" if a.sms else None
    if not sms_why and a.plan and (pj.get("timeline") or {}).get("sms"):
        sms_why = f"{a.plan}: timeline made with --sms"
    ev_path = Path(a.event) if a.event else path.parent / "event.json"
    if a.event and not ev_path.exists():
        refuse(f"no event spec at {a.event}")
    if not sms_why and ev_path.exists() and event_sms(ev_path):
        sms_why = f"{ev_path} sets reminders.sms"
    if plan is None:
        m = launch_plan.compute_math(goal_buyers=a.goal_buyers, goal_cash=cash, price=cash / a.goal_buyers,
                                     list_size=a.list_size, fmt=a.format, days=a.days, paid=a.paid_event, close=mode)
        plan = plan_from_math(m, a.days)
        src = "Build Room benchmarks (typical path; no plan.json)"
    if not plan.get("expected"):
        warnings.append("no list size: there is no expected path, so leaks are judged against what the goal needs "
                        "(pass --list-size, or a plan.json made with --list-size)")
    gate = {g: {"status": "open"} for g in gate_ids(mode)}
    if a.days == 1:
        gate["night_emails"] = {"status": "na", "note": "single-day event", "date": today(a).isoformat(),
                                "tested_at": today(a).isoformat(), "stage": DB}
    if not sms_why:
        gate["sms_compliance"] = {"status": "na", "note": "email only: no SMS planned", "auto": True,
                                  "date": today(a).isoformat(), "stage": PI}
    data = {"schema": SCHEMA, "created": today(a).isoformat(), "name": a.name, "slug": path.parent.name,
            "format": a.format, "days": a.days, "tz": a.tz, "event_date": ev.isoformat(), "paid_event": bool(a.paid_event),
            "close_mode": mode, "test": bool(a.test), "live_definition": "unique", "sms": bool(sms_why),
            **({"sms_why": sms_why} if sms_why else {}), "partners": {},
            "goal": {"buyers": a.goal_buyers, "cash": cash}, "plan": plan, "plan_source": src,
            "registrations": [], "days_live": {}, "close": None, "sales": [], "calls": [], "refunds": [], "imports": [],
            "gate": gate}
    show = lambda d, f: None if not d else {k: (f(v) if isinstance(v, (int, float)) else [f(x) for x in v]
                                               if isinstance(v, list) else v) for k, v in d.items()
                                            if not isinstance(v, dict)}
    out = {"created": str(path), "name": a.name, "slug": data["slug"], "folder": str(path.parent), "close_mode": mode,
           "test": bool(a.test), "plan_source": src,
           "sms": ("planned: sms_compliance is a critical gate item (" + sms_why + ")") if sms_why else
                  "email only: sms_compliance is na (init --sms if texts are planned)",
           "plan": {"needed_for_goal": show(plan["needed"], lambda x: math.ceil(round(x, 6))),
                    "expected_from_list": show(plan.get("expected"), lambda x: round(x, 1))}}
    if a.test:
        out["note"] = "TEST ledger: report and the Obsidian note are labelled TEST, and obsidian-read skips it"
    if warnings:
        out["warnings"] = warnings
    return data, out


def total_regs(data, until=None):
    return sum(r["n"] for r in data["registrations"] if until is None or r["date"] <= until)


def cmd_log_reg(data, a):
    nonneg(a.n, "N")
    src = parse_source(a.source)
    data["registrations"].append({"date": today(a).isoformat(), "n": a.n, "source": src})
    return {"logged": a.n, "source": src, "registered_total": total_regs(data)}


def cmd_log_day(data, a):
    if not 1 <= a.day <= data["days"]:
        refuse(f"--day must be between 1 and {data['days']} for this {data['days']}-day event")
    nonneg(a.live, "--live")
    if a.peak is not None:
        nonneg(a.peak, "--peak")
    by_source = {}
    for item in a.source_count or []:
        if "=" not in item:
            refuse(f"--source-count takes SOURCE=N, for example partner:Jo=40 (got {item!r})")
        k, v = item.rsplit("=", 1)
        try:
            n = int(v)
        except ValueError:
            refuse(f"--source-count {item!r}: N must be a whole number")
        by_source[parse_source(k.strip(), "--source-count")] = nonneg(n, "--source-count N")
    if sum(by_source.values()) > a.live:
        refuse(f"--source-count adds up to {sum(by_source.values())}, more than the {a.live} unique attendees (--live)")
    on = a.date or (dt.date.fromisoformat(data["event_date"]) + dt.timedelta(days=a.day - 1)).isoformat()
    parse_date(on)
    key = str(a.day)
    replaced = key in data["days_live"]
    entry = {"live": a.live, **({"peak": a.peak} if a.peak is not None else {}),
             **({"by_source": by_source} if by_source else {}), "date": on}
    data["days_live"][key] = entry
    out = {"day": a.day, "live": a.live, "counted_as": LIVE_DEF, **({"peak": a.peak} if a.peak is not None else {}),
           **({"by_source": by_source} if by_source else {}), "replaced": replaced}
    warn = []
    regs = total_regs(data)
    if a.day == 1 and regs and a.live > regs:
        warn.append(f"Day 1 live ({a.live}) is more than the registrations logged ({regs}); log the registrations")
    prev = data["days_live"].get(str(a.day - 1))
    if prev and a.live > prev["live"]:
        warn.append(f"Day {a.day} ({a.live}) is higher than Day {a.day - 1} ({prev['live']}): fine if new people joined, "
                    "otherwise check both are unique attendees")
    if a.peak is not None and a.peak > a.live:
        warn.append(f"--peak ({a.peak}) is above the unique attendees ({a.live}); the peak at once is usually lower: "
                    "check --live is the unique count from the Zoom report")
    if warn:
        out["warnings"] = warn
    return out


def cmd_log_close(data, a):
    nonneg(a.present, "--present"); nonneg(a.saw_price, "--saw-price")
    data["close"] = {"present": a.present, "saw_price": a.saw_price, "date": today(a).isoformat()}
    out = {"present": a.present, "saw_price": a.saw_price}
    last = data["days_live"].get(str(data["days"]))
    if last and a.present > last["live"]:
        out["warnings"] = [f"present at the close ({a.present}) is more than the final day's live count ({last['live']})"]
    return out


def cmd_log_sale(data, a):
    nonneg(a.count, "--count")
    price = launch_plan.money(a.price, "--price")
    cash = price * a.count
    if a.payment == "plan":
        if a.booked is None:
            refuse("--payment plan needs --booked TOTAL: the total contract value of these sales")
        booked = launch_plan.money(a.booked, "--booked")
        if booked < cash:
            refuse(f"--booked ({booked:,.2f}) is less than the cash already collected ({cash:,.2f})")
    else:
        if a.booked is not None and abs(launch_plan.money(a.booked, "--booked") - cash) > .005:
            refuse("--booked is for payment plans; a full payment books price × count")
        booked = cash
    if a.tier in TICKET_TIERS:
        refuse(f"tier {a.tier!r} is kept for log-tickets; name the offer's tier something else")
    src = parse_source(a.source) if a.source else None
    data["sales"].append({"date": today(a).isoformat(), "tier": a.tier, "price": price, "count": a.count,
                          "payment": a.payment, "via": a.via, "cash": round(cash, 2), "booked": round(booked, 2),
                          **({"source": src} if src else {})})
    out = {"logged": a.count, "tier": a.tier, "payment": a.payment, "via": a.via, "cash": round(cash, 2),
           "booked": round(booked, 2), "buyers_total": buyers_total(data), **({"source": src} if src else {})}
    if a.via == "call":
        out["note"] = "cash only: buyers and booked value of call deals come from log-calls"
    return out


def call_totals(data):
    if not data.get("calls"):
        return None
    t = {k: sum(c[k] for c in data["calls"]) for k in ("booked", "held", "closed")}
    t["value"] = round(sum(c["value"] for c in data["calls"]), 2)
    return t


TICKET_TIERS = ("Tickets", "VIP upgrade")


def offer_sales(data):
    return [x for x in data["sales"] if x.get("via", "checkout") != "ticket"]


def checkout_buyers(data):
    s = [x for x in data["sales"] if x.get("via", "checkout") == "checkout"]
    return sum(x["count"] for x in s) if s else None


def buyers_total(data):
    co, ct = checkout_buyers(data), call_totals(data)
    if co is None and ct is None:
        return None
    return (co or 0) + (ct["closed"] if ct else 0)


def cmd_log_calls(data, a):
    for k in ("booked", "held", "closed"):
        nonneg(getattr(a, k), f"--{k}")
    if a.closed and a.value is None:
        refuse("--value X is needed: the booked value of the deals closed on these calls")
    value = 0.0
    if a.value is not None:
        try:
            value = float(str(a.value).replace("$", "").replace(",", ""))
        except ValueError:
            refuse(f"--value must be a number (got {a.value!r})")
        if value < 0 or (a.closed and value == 0):
            refuse("--value must be more than 0 when deals closed (0 or more otherwise)")
    prev = call_totals(data) or {"booked": 0, "held": 0, "closed": 0}
    t = {k: prev[k] + getattr(a, k) for k in ("booked", "held", "closed")}
    if t["held"] > t["booked"]:
        refuse(f"calls held in total ({t['held']}) would be more than calls booked ({t['booked']})")
    if t["closed"] > t["held"]:
        refuse(f"calls closed in total ({t['closed']}) would be more than calls held ({t['held']})")
    src = parse_source(a.source) if a.source else None
    data["calls"].append({"date": today(a).isoformat(), "tier": a.tier, "booked": a.booked, "held": a.held,
                          "closed": a.closed, "value": round(value, 2), **({"source": src} if src else {})})
    out = {"logged": {"booked": a.booked, "held": a.held, "closed": a.closed, "value": round(value, 2)}, "tier": a.tier,
           "totals": t, "show_rate": None if not t["booked"] else round(t["held"] / t["booked"], 4),
           "close_rate": None if not t["held"] else round(t["closed"] / t["held"], 4)}
    if data.get("close_mode") == "checkout":
        out["warnings"] = ["this ledger's close mode is checkout: the report shows call stages only for call or both"]
    return out


def cmd_log_refund(data, a):
    nonneg(a.count, "--count")
    amount = launch_plan.money(a.amount, "--amount")
    cancelled = float(a.booked_cancelled or 0)
    if cancelled < 0:
        refuse("--booked-cancelled must be 0 or more")
    call_tiers = {c["tier"] for c in data.get("calls", []) if c["closed"]}
    tiers = {s["tier"] for s in data["sales"]} | call_tiers
    if a.tier not in tiers:
        refuse(f"no sales logged for tier {a.tier!r}; tiers logged: {sorted(tiers)}")
    sold = sum(s["count"] for s in data["sales"] if s["tier"] == a.tier and s.get("via", "checkout") != "call") + \
        sum(c["closed"] for c in data.get("calls", []) if c["tier"] == a.tier)
    refunded = sum(r["count"] for r in data["refunds"] if r["tier"] == a.tier)
    if refunded + a.count > sold:
        refuse(f"{refunded + a.count} refunds for {a.tier!r} but only {sold} sold")
    collected = sum(s["cash"] for s in data["sales"] if s["tier"] == a.tier)
    already = sum(r["amount"] for r in data["refunds"] if r["tier"] == a.tier)
    if amount > collected - already + .005:
        refuse(f"--amount {amount:,.2f} is more than the cash collected for {a.tier!r} ({collected:,.2f}) less earlier "
               f"refunds ({already:,.2f}); log the cash first (log-sale) or refund what was paid")
    src = parse_source(a.source) if a.source else None
    data["refunds"].append({"date": today(a).isoformat(), "tier": a.tier, "count": a.count, "amount": round(amount, 2),
                            "booked_cancelled": round(cancelled, 2), **({"source": src} if src else {})})
    return {"refund": a.count, "tier": a.tier, "amount": round(amount, 2), "booked_cancelled": round(cancelled, 2),
            **({"source": src} if src else {})}


def cmd_log_tickets(data, a):
    nonneg(a.count, "--count")
    price = launch_plan.money(a.price, "--price")
    src = parse_source(a.source) if a.source else None
    if (a.vip_count is None) != (a.vip_price is None):
        refuse("--vip-count and --vip-price go together")
    rows = [("Tickets", price, a.count)]
    if a.vip_count is not None:
        rows.append(("VIP upgrade", launch_plan.money(a.vip_price, "--vip-price"), nonneg(a.vip_count, "--vip-count")))
    out = {"logged": []}
    for tier, p_, n in rows:
        cash = round(p_ * n, 2)
        data["sales"].append({"date": today(a).isoformat(), "tier": tier, "price": p_, "count": n, "payment": "full",
                              "via": "ticket", "cash": cash, "booked": cash, **({"source": src} if src else {})})
        out["logged"].append({"tier": tier, "count": n, "price": p_, "cash": cash})
    if not data.get("paid_event") and price:
        out["warnings"] = ["this ledger is a free event (init without --paid-event); tickets are logged anyway"]
    out["tickets_total"] = sum(x["count"] for x in data["sales"] if x["tier"] == "Tickets")
    out["note"] = "ticket and VIP cash count in the report's cash and booked, never as buyers of the offer"
    return out


def cmd_partner(data, a):
    r = launch_plan.rate(a.rate, "--rate")
    name = a.name.strip()
    if not name or not SRC_RE.match(f"partner:{name}"):
        refuse(f"--name must be the NAME used in --source partner:NAME (got {a.name!r})")
    key = next((k for k in data["partners"] if k.casefold() == name.casefold()), name)
    data["partners"][key] = {"commission_rate": r, "set": today(a).isoformat()}
    seen = {s.split(":", 1)[1] for s in sources_seen(data) if s.startswith("partner:")}
    out = {"partner": key, "commission_rate": r,
           "note": "commission is worked out on net cash (after refunds) in the report; pay it after the refund window"}
    if not any(x.casefold() == key.casefold() for x in seen):
        out["warnings"] = [f"nothing is logged yet with --source partner:{key}"]
    return out


def sources_seen(data):
    out = {r["source"] for r in data["registrations"]}
    for k in ("sales", "calls", "refunds"):
        out |= {x["source"] for x in data.get(k, []) if x.get("source")}
    for e in data["days_live"].values():
        out |= set((e.get("by_source") or {}))
    return out


def parse_map(items, days):
    allowed = {"registered", "present", "saw_price"} | {f"day{k}" for k in range(1, days + 1)}
    out = {}
    for item in items:
        for pair in str(item).split(","):
            if not pair.strip():
                continue
            if "=" not in pair:
                refuse(f"--map takes field=TAG pairs (got {pair!r})")
            k, v = (x.strip() for x in pair.split("=", 1))
            if k not in allowed:
                refuse(f"--map field {k!r} is not one of {sorted(allowed)}")
            if not v:
                refuse(f"--map {k}= needs a tag (or * for every row)")
            out[k] = v
    if not out:
        refuse("--map needs at least one field=TAG pair")
    return out


def cmd_import_csv(data, a):
    p = Path(a.csv)
    if not p.exists():
        refuse(f"no file at {a.csv}")
    mp = parse_map(a.map, data["days"])
    try:
        with p.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except (UnicodeDecodeError, csv.Error) as e:
        refuse(f"{a.csv} is not a readable CSV ({e})")
    if not rows:
        refuse(f"{a.csv} has no rows")
    tagcol = next((c for c in rows[0] if c and "tag" in c.lower()), None)
    if not tagcol and any(v != "*" for v in mp.values()):
        refuse(f"{a.csv} has no tags column (looked for a header containing 'tag'): export the contacts with their tags")
    def tags(r):
        return {t.strip().lower() for t in re.split(r"[,;|]", r.get(tagcol) or "") if t.strip()}
    counts = {k: (len(rows) if v == "*" else sum(1 for r in rows if v.lower() in tags(r))) for k, v in mp.items()}
    on = today(a).isoformat()
    close = data.get("close") or {}
    before = {}
    if "registered" in counts:
        before["registered"] = total_regs(data) if data["registrations"] else None
    for k in counts:
        if k.startswith("day"):
            before[k] = (data["days_live"].get(k[3:]) or {}).get("live")
        elif k in ("present", "saw_price"):
            before[k] = close.get(k)
    conflicts = []
    for k, n in counts.items():
        b = before.get(k)
        if b is None or b == n:
            continue
        if k == "registered" and n > b:
            continue                                        # a top-up: the export holds more than was logged
        conflicts.append(f"{k}: logged {b}, export {n}")
    if conflicts and not a.replace:
        refuse("the export would overwrite logged numbers (" + "; ".join(conflicts) + "). Nothing was changed. Check the "
               "export is complete (a partial export holds fewer contacts), or pass --replace to use the export's counts")
    changes = []
    if "registered" in counts:
        n, b = counts["registered"], before["registered"] or 0
        if n > b:                                           # a top-up: one positive "import" entry
            data["registrations"].append({"date": on, "n": n - b, "source": "import"})
        elif n < b:                                         # only with --replace: replace, never a negative entry
            data.setdefault("replaced_registrations", []).append({"date": on, "entries": data["registrations"]})
            data["registrations"] = [{"date": on, "n": n, "source": "import"}]
        changes.append({"field": "registered", "before": before["registered"], "after": n})
    for k, v in counts.items():
        if k.startswith("day"):
            n = int(k[3:])
            cur = dict(data["days_live"].get(str(n)) or {})
            cur.update({"live": v, "imported": True})
            cur.setdefault("date", (dt.date.fromisoformat(data["event_date"]) + dt.timedelta(days=n - 1)).isoformat())
            data["days_live"][str(n)] = cur
            changes.append({"field": k, "before": before[k], "after": v})
    if "present" in counts or "saw_price" in counts:
        c = dict(data["close"] or {})
        for k in ("present", "saw_price"):
            if k in counts:
                c[k] = counts[k]
                changes.append({"field": k, "before": before[k], "after": counts[k]})
        c["date"] = on
        data["close"] = c
    data["imports"].append({"date": on, "file": p.name, "rows": len(rows), "map": mp, "counts": counts,
                            "replace": bool(a.replace)})
    return {"imported": p.name, "rows": len(rows), "counts": counts, "changes": changes,
            "table": "\n".join(["| Field | Before | After |", "|---|---|---|"] +
                               [f"| {c['field']} | {launch_fmt(c['before'])} | {launch_fmt(c['after'])} |" for c in changes]),
            **({"replaced": conflicts} if conflicts else {}),
            "stored": "counts and the file name only; no names, emails or phone numbers"}


# ---------------- gate ----------------

def is_critical(gid, data, path=None):
    if gid == "sms_compliance":
        return sms_planned(data, path)[0]
    return GATE_BY_ID[gid][1]


def entry_for(data, gid, path=None):
    g = dict(data["gate"].get(gid) or {"status": "open"})
    if gid == "sms_compliance" and g.get("auto") and sms_planned(data, path)[0]:
        g = {"status": "open", "note": "SMS is planned now: test consent and A2P approval"}
    return g


def stage_of(g, gid):
    """The stage an entry was recorded at (older entries: the item's first stage)."""
    return g.get("stage") or GATE_BY_ID[gid][6][0]


def satisfied(gid, g, stage, day):
    """(ok, why not): does this entry count for this stage?"""
    if g["status"] == "na":
        return True, ""
    if g["status"] != "pass":
        return False, g["status"]
    stages = GATE_BY_ID[gid][6]
    rec = stage_of(g, gid)
    if stage != stages[0] and STAGES.index(rec) < STAGES.index(stage):
        return False, f"passed at {rec}; re-check it at {stage} (gate --stage {stage} --set {gid} pass \"note\")"
    if stage == CM and str(g.get("tested_at") or "")[:10] != day:
        return False, f"passed on {str(g.get('tested_at') or '?')[:10]}, not on the close morning ({day}): re-test that morning"
    return True, ""


def item_line(gid, what, g, why=""):
    extra = [g["status"]]
    if g.get("tested_at"):
        extra.append(f"tested {g['tested_at']}")
    if g.get("stage"):
        extra.append(f"at {g['stage']}")
    if g.get("note"):
        extra.append(f"note: {g['note']}")
    if why and why != g["status"]:
        extra.append(why)
    return f"{gid}: {what} ({'; '.join(extra)})"


def close_day(data):
    return (dt.date.fromisoformat(data["event_date"]) + dt.timedelta(days=int(data["days"]) - 1)).isoformat()


def stage_view(data, stage, today_, path=None):
    """One stage. close_morning passes count only when dated the close day (the event's final day)."""
    mode = data.get("close_mode", "checkout")
    day = close_day(data) if stage == CM else today_
    items, hold, adv = [], [], []
    for gid in stage_ids(mode, stage):
        _, _, group, what, src, _, stages = GATE_BY_ID[gid]
        g = entry_for(data, gid, path)
        crit = is_critical(gid, data, path)
        ok, why = satisfied(gid, g, stage, day)
        items.append({"id": gid, "critical": crit, "group": group, "status": g["status"], "ok_for_stage": ok,
                      "check": what, "source": src, "stages": list(stages), "recorded_stage": g.get("stage"),
                      "tested_at": g.get("tested_at") or g.get("date"), **({"note": g["note"]} if g.get("note") else {}),
                      **({"why": why} if not ok else {})})
        if not ok:
            (hold if crit else adv).append(item_line(gid, what, g, why))
    out = {"stage": stage, "when": STAGE_WHEN[stage], "result": "GO" if not hold else "HOLD", "close_mode": mode,
           "items": items}
    if stage == CM:
        out["close_morning"] = day
        if today_ != day:
            out["note"] = (f"today is {today_}; the close morning is {day} (the final day): passes count only when "
                           "tested that morning")
    if hold:
        out["hold"] = hold
        out["say"] = (f"HOLD at {stage}: {len(hold)} critical item{'s' if len(hold) > 1 else ''} not passed. Fix "
                      f"{'them' if len(hold) > 1 else 'it'} {STAGE_WHEN[stage]}; the member may still choose to go "
                      "ahead, knowing what each open item risks.")
    else:
        out["say"] = f"GO at {stage}: every critical item passes." + (" Advisory items still open." if adv else "")
    if adv:
        out["advisory_open"] = adv
    return out


def gate_view(data, day, path=None):
    mode = data.get("close_mode", "checkout")
    per = {s: stage_view(data, s, day, path) for s in STAGES}
    items = []
    for gid in gate_ids(mode):
        g = entry_for(data, gid, path)
        _, _, group, what, src, _, stages = GATE_BY_ID[gid]
        items.append({"id": gid, "critical": is_critical(gid, data, path), "group": group, "status": g["status"],
                      "stages": list(stages), "recorded_stage": g.get("stage"), "check": what, "source": src,
                      "tested_at": g.get("tested_at") or g.get("date"), **({"note": g["note"]} if g.get("note") else {})})
    nxt = next((s for s in STAGES if per[s]["result"] == "HOLD"), None)
    out = {"result": "GO" if nxt is None else "HOLD", "close_mode": mode,
           "stages": {s: {"result": v["result"], "when": v["when"],
                          "items": [i["id"] for i in v["items"]],
                          **({"hold": [x.split(":", 1)[0] for x in v["hold"]]} if v.get("hold") else {}),
                          **({"advisory_open": [x.split(":", 1)[0] for x in v["advisory_open"]]}
                             if v.get("advisory_open") else {})} for s, v in per.items()},
           "next_stage": nxt, "items": items}
    out["say"] = ("GO: every stage passes." if nxt is None else
                  f"Next: {nxt} ({STAGE_WHEN[nxt]}) is HOLD on {', '.join(out['stages'][nxt].get('hold', []))}. "
                  f"Run gate --stage {nxt} to work through it.")
    planned, why = sms_planned(data, path)
    out["sms"] = ("planned (" + why + "): sms_compliance is critical") if planned else "email only: sms_compliance is na"
    out["close_morning_items"] = close_morning_ids(mode)
    out["sources"] = {k: SOURCES[k] for k in sorted({g[4] for g in GATE if mode in g[5]})}
    return out


def cmd_gate(data, a):
    mode = data.get("close_mode", "checkout")
    ids = gate_ids(mode)
    stage = CM if a.close_morning else a.stage
    if a.close_morning and a.stage and a.stage != CM:
        refuse("--close-morning is --stage close_morning; give one of them")
    if stage and stage not in STAGES:
        refuse(f"--stage must be one of {', '.join(STAGES)} (got {stage!r})")
    day = today(a).isoformat()
    path = getattr(a, "_path", None)
    changed = []
    sets = a.set or []
    if a.note and len(sets) != 1:
        refuse("--note works with exactly one --set; give each item its own note as --set ITEM STATUS \"note\"")
    for spec in sets:
        if len(spec) not in (2, 3):
            refuse(f"--set takes ITEM STATUS [\"note\"] (got {' '.join(spec)!r})")
        gid, status = spec[0], spec[1].lower()
        note = spec[2] if len(spec) == 3 else a.note
        if gid not in GATE_BY_ID:
            refuse(f"unknown gate item {gid!r}; items: {', '.join(ids)}")
        if gid not in ids:
            refuse(f"{gid} is not a gate item for a {mode} close; items: {', '.join(ids)}")
        if status not in STATUSES:
            refuse(f"gate status must be pass, fail, na or open (got {status!r})")
        stages = GATE_BY_ID[gid][6]
        if stage and stage not in stages:
            refuse(f"{gid} is not judged at {stage}; its stages: {', '.join(stages)}")
        crit = is_critical(gid, data, path)
        if status == "na" and crit and not note:
            refuse(f"{gid} is critical: na needs a note saying why it does not apply (--set {gid} na \"why\")")
        if status == "pass" and crit and not note:
            refuse(f"{gid} is critical: pass needs a note saying what was tested, by whom, on what device "
                   f"(--set {gid} pass \"Dana, iPhone, live card then refunded\")")
        rec = stage
        if not rec:
            cur = entry_for(data, gid, path)
            rec = next((s for s in stages if not satisfied(gid, cur, s, close_day(data) if s == CM else day)[0]),
                       stages[-1])
        prev = data["gate"].get(gid)
        entry = {"status": status, **({"note": note} if note else {}), "date": day, "stage": rec}
        if status != "open":
            entry["tested_at"] = stamp(a)
        if prev and prev.get("status") != "open":
            entry["history"] = (prev.get("history") or [])[-4:] + [{k: v for k, v in prev.items() if k != "history"}]
        data["gate"][gid] = entry
        changed.append(f"{gid} ({rec})")
    for gid in a.reset or []:
        if gid not in ids:
            refuse(f"unknown gate item {gid!r} for a {mode} close; items: {', '.join(ids)}")
        data["gate"][gid] = {"status": "open", "date": day, "reset": True}
        changed.append(gid)
    out = stage_view(data, stage, day, path) if stage else gate_view(data, day, path)
    if changed:
        out = {"set": changed, **out}
    return out


# ---------------- report ----------------

def ratio(a, b):
    return None if a is None or b in (None, 0) else a / b


def r4(x):
    return None if x is None else round(x, 4)


def plan_history(plan):
    inv = {v: k for k, v in launch_plan.HISTORY_FLAGS.items()}
    return {inv[k]: v for k, v in (plan.get("history") or {}).items() if k in inv}


def build_report(data):
    days, mode = data["days"], data.get("close_mode", "checkout")
    plan = data.get("plan") or {}
    exp, need = plan.get("expected"), plan.get("needed") or {}
    ref = exp or need                                       # the path leaks are judged against
    ref_name = "expected from the list" if exp else "needed for the goal"
    pr = plan.get("rates") or {}
    pv = plan.get("per_viewer") or {}
    regs = total_regs(data) if data["registrations"] else None
    live = [data["days_live"].get(str(k), {}).get("live") for k in range(1, days + 1)]
    close = data.get("close") or {}
    present, saw = close.get("present"), close.get("saw_price")
    calls = call_totals(data)
    co_buyers = checkout_buyers(data)
    if co_buyers is None and close and mode != "call":
        co_buyers = 0
    buyers = buyers_total(data)
    if buyers is None and close:
        buyers = 0
    offer_refunds = [r for r in data["refunds"] if r["tier"] not in TICKET_TIERS]
    refunds_n = sum(r["count"] for r in offer_refunds)
    refunds_amt = sum(r["amount"] for r in data["refunds"])
    cancelled = sum(r.get("booked_cancelled", 0) for r in data["refunds"])
    cash = sum(s["cash"] for s in data["sales"])
    booked = sum(s["booked"] for s in data["sales"] if s.get("via", "checkout") != "call") + (calls["value"] if calls else 0)
    ticket_rows = [s for s in data["sales"] if s.get("via") == "ticket"]
    ticket_cash = sum(s["cash"] for s in ticket_rows if s["tier"] == "Tickets")
    vip_cash = sum(s["cash"] for s in ticket_rows if s["tier"] == "VIP upgrade")
    offer_booked = booked - ticket_cash - vip_cash
    net_cash, net_booked = cash - refunds_amt, booked - refunds_amt - cancelled
    # funnel: (label, actual, plan key)
    stages = [("Registered", regs, "registrants")] + [(f"Live Day {k}", live[k - 1], ("day_live", k - 1)) for k in range(1, days + 1)] + \
             [("Present at the close", present, "present_at_close"), ("Saw the price", saw, "saw_price")]
    if mode in ("call", "both"):
        stages += [("Calls booked", calls and calls["booked"], "calls_booked"), ("Calls held", calls and calls["held"], "calls_held"),
                   ("Calls closed", calls and calls["closed"], "calls_closed")]
    if mode == "both":
        stages.append(("Checkout buyers", co_buyers, "checkout_buyers"))
    stages.append(("Buyers", buyers, "buyers"))
    def pget(d, k):
        if not d:
            return None
        return (d.get(k[0]) or [None] * days)[k[1]] if isinstance(k, tuple) else d.get(k)
    funnel = []
    for label, x, k in stages:
        e, n = pget(exp, k), pget(need, k)
        funnel.append({"stage": label, "actual": x, "expected": None if e is None else round(e, 1),
                       "needed_for_goal": None if n is None else math.ceil(round(n, 6)),
                       "vs_expected": None if x is None or not e else round(x / e, 3),
                       "vs_needed": None if x is None or not n else round(x / n, 3)})
    # rows of the leak model: (key, kind, label, actual, plan)
    rows = [("registration", "registration", f"Registrations vs {ref_name}", ratio(regs, pget(ref, "registrants")), 1.0),
            ("show_up", "show_up", "Day-1 show-up", ratio(live[0], regs), pr.get("show_up"))]
    for k in range(1, days):
        rows.append((f"retention_{k}_{k + 1}", "retention", f"Day {k} → Day {k + 1} retention", ratio(live[k], live[k - 1]),
                     pr.get("retention")))
    rows += [("stay_to_close", "stay_to_close", "Stayed to the close", ratio(present, live[-1]), pr.get("stay_to_close")),
             ("saw_price", "saw_price", "Saw the price (× present)", ratio(saw, present), pr.get("saw_price"))]
    if mode in ("checkout", "both"):
        rows.append(("conversion", "conversion", "Checkout conversion of price-viewers", ratio(co_buyers, saw),
                     pv.get("checkout", pr.get("conversion"))))
    if mode in ("call", "both"):
        rows += [("booked", "booked", "Calls booked (of those who saw the offer)", ratio(calls and calls["booked"], saw),
                  pv.get("booked")),
                 ("held", "held", "Calls held (show rate)", ratio(calls and calls["held"], calls and calls["booked"]), pr.get("held")),
                 ("closed", "closed", "Calls closed (of held)", ratio(calls and calls["closed"], calls and calls["held"]),
                  pr.get("closed"))]
    rows = [{"key": k, "kind": kind, "label": label, "actual": a_, "plan": p_} for k, kind, label, a_, p_ in rows]
    base = pget(ref, "registrants") or 0
    tail_keys = {"conversion", "booked", "held", "closed"}
    def model(override=None):
        v = {}
        for r in rows:
            x = r["plan"] if (r["actual"] is None or r["plan"] is None or r["key"] == override) else r["actual"]
            v[r["key"]] = 1.0 if x is None else x
        b = base
        for r in rows:
            if r["key"] not in tail_keys:
                b *= v[r["key"]]
        tail = (v.get("conversion", 0) if "conversion" in v else 0) + \
               (v["booked"] * v["held"] * v["closed"] if "booked" in v else 0)
        return b * tail
    now = model()
    assumption = set(plan.get("assumption_only") or [])
    leaks, protect = [], []
    for r in rows:
        if r["actual"] is None or r["plan"] is None:
            continue
        kind = r["kind"]
        if r["actual"] < r["plan"]:
            fix = STAGE_FIX[kind]
            if kind == "retention":
                a_, b_ = r["key"].split("_")[1:]
                fix = fix.format(a=a_, b=b_)
            leaks.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "plan": round(r["plan"], 4),
                          "shortfall": round(1 - r["actual"] / r["plan"], 3), "buyers_lost": round(model(r["key"]) - now, 1),
                          "fix": fix, **({"plan_is_assumption": True} if kind in assumption else {})})
        elif kind not in assumption and r["actual"] > r["plan"]:
            protect.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "plan": round(r["plan"], 4),
                            "keep": STAGE_KEEP[kind]})
    leaks.sort(key=lambda x: (-x["buyers_lost"], -x["shortfall"], x["stage"]))
    protect.sort(key=lambda x: -(x["actual"] / x["plan"] if x["plan"] else 0))
    # benchmarks (the plan's member history when it had one)
    sold_price = (offer_booked / buyers) if buyers else data["goal"]["cash"] / data["goal"]["buyers"]
    tiers = [{"name": "checkout", "price": sold_price, "share": 1.0, "channel": "checkout"}] if mode == "checkout" else \
        [{"name": "call", "price": sold_price, "share": 1.0, "channel": "call"}] if mode == "call" else \
        [{"name": "checkout", "price": min(sold_price, launch_plan.CALL_PRICE - 1), "share": .5, "channel": "checkout"},
         {"name": "call", "price": sold_price, "share": .5, "channel": "call"}]
    hist = plan_history(plan)
    bench_rates = launch_plan.rates_for(data["format"], days, data.get("paid_event"), tiers, hist)
    bench = []
    for r in rows:
        k = r["kind"]
        if k not in bench_rates or k == "registration" or r["actual"] is None:
            continue
        if mode == "both" and k in ("conversion", "booked"):
            continue                                        # split between two doors: no single benchmark
        b = bench_rates[k]
        lo, hi = b["cautious"], b["strong"]
        status = "below range" if r["actual"] < lo else "above range" if r["actual"] > hi else "in range"
        src = b["source"]
        bench.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "range": [lo, hi],
                      "typical": b["typical"], "status": status,
                      "source": " / ".join(dict.fromkeys(src.values())) if isinstance(src, dict) else src})
    per_reg = None if not regs else {"cash": round(net_cash / regs, 2), "booked": round(net_booked / regs, 2)}
    by_source, by_type = {}, {}
    for r in data["registrations"]:
        by_source[r["source"]] = by_source.get(r["source"], 0) + r["n"]
        t = r["source"].split(":", 1)[0]
        by_type[t] = by_type.get(t, 0) + r["n"]
    missing = [f["stage"] for f in funnel if f["actual"] is None]
    keys = set(plan.get("source_keys") or [])
    for b in bench:
        keys |= set(b["source"].split(" / "))
    exp_buyers = (exp or {}).get("buyers")
    goal_b = data["goal"]["buyers"]
    buyers_net = None if buyers is None else buyers - refunds_n
    goal_gap = {"goal_buyers": goal_b, "expected_buyers_from_list": None if exp_buyers is None else round(exp_buyers, 1),
                "gap_the_plan_showed": None if exp_buyers is None else round(goal_b - exp_buyers, 1),
                "actual_buyers_net": buyers_net,
                "actual_vs_goal": None if buyers_net is None else round(buyers_net / goal_b, 3),
                "actual_vs_expected": None if buyers_net is None or not exp_buyers else round(buyers_net / exp_buyers, 3),
                "note": "leaks are ranked against the expected path; the goal gap is shown here on its own" if exp else
                        "no expected path (no list size): leaks are ranked against what the goal needs"}
    return {
        "name": data["name"], "slug": data["slug"], "test": bool(data.get("test")), "format": data["format"], "days": days,
        "event_date": data["event_date"], "tz": data["tz"], "paid_event": data.get("paid_event", False), "close_mode": mode,
        "goal": data["goal"], "plan_source": data.get("plan_source"), "judged_against": ref_name,
        "funnel": funnel,
        "retention": [{"from": k, "to": k + 1, "actual": r4(ratio(live[k], live[k - 1])), "plan": r4(pr.get("retention"))}
                      for k in range(1, days)],
        "conversion": {"label": "of those who saw the price", "of_saw_price": r4(ratio(buyers, saw)),
                       "checkout_of_saw_price": r4(ratio(co_buyers, saw)) if mode == "both" else None,
                       "of_registrants": r4(ratio(buyers, regs)), "of_day1": r4(ratio(buyers, live[0]))},
        "calls": None if mode == "checkout" else {
            **(calls or {"booked": None, "held": None, "closed": None, "value": None}),
            "booked_of_saw_price": r4(ratio(calls and calls["booked"], saw)),
            "show_rate": r4(ratio(calls and calls["held"], calls and calls["booked"])),
            "close_rate": r4(ratio(calls and calls["closed"], calls and calls["held"]))},
        "money": {"cash": round(cash, 2), "booked": round(booked, 2), "refunded": round(refunds_amt, 2),
                  "booked_cancelled": round(cancelled, 2), "net_cash": round(net_cash, 2), "net_booked": round(net_booked, 2),
                  "average_sale": round(sold_price, 2) if buyers else None,
                  **({"ticket_cash": round(ticket_cash, 2), "vip_cash": round(vip_cash, 2),
                      "tickets": sum(s["count"] for s in ticket_rows if s["tier"] == "Tickets"),
                      "vip_upgrades": sum(s["count"] for s in ticket_rows if s["tier"] == "VIP upgrade")}
                     if ticket_rows else {})},
        "live_definition": LIVE_DEF,
        "peak_concurrent": {str(k): data["days_live"][str(k)]["peak"] for k in range(1, days + 1)
                            if "peak" in data["days_live"].get(str(k), {})},
        "partners": partner_table(data),
        "refunds": {"count": refunds_n, "amount": round(refunds_amt, 2),
                    "rate": None if not buyers else round(refunds_n / buyers, 4)},
        "buyers_net": buyers_net,
        "per_registrant": per_reg,
        "goal_progress": {"buyers": None if buyers_net is None else round(buyers_net / goal_b, 3),
                          "cash_booked": round(net_booked / data["goal"]["cash"], 3)},
        "goal_gap": goal_gap,
        "registrations_by_source": by_source, "registrations_by_source_type": by_type,
        "benchmarks": bench, "benchmarks_from_history": sorted(plan.get("history") or {}),
        "leaks": leaks[:3], "all_leaks": len(leaks), "protect": protect,
        "lessons": list(data.get("lessons") or []),
        "not_logged": missing,
        "sources": {k: SOURCES[k] for k in sorted(keys) if k in SOURCES},
    }


def partner_table(data):
    """Per partner (partner:NAME sources): registrations, Day-1 attendees (if logged by source), buyers, cash,
    refunds, net cash and the commission due on net cash at the rate set with `partner`."""
    names = {}
    def key(src):
        n = src.split(":", 1)[1]
        return names.setdefault(n.casefold(), n)
    rows = {}
    def row(src):
        k = key(src)
        return rows.setdefault(k, {"registrations": 0, "attendees_day1": None, "buyers": 0, "cash": 0.0,
                                   "refunds": 0, "refunded": 0.0})
    for r in data["registrations"]:
        if r["source"].startswith("partner:"):
            row(r["source"])["registrations"] += r["n"]
    d1 = (data["days_live"].get("1") or {}).get("by_source") or {}
    for src, n in d1.items():
        if src.startswith("partner:"):
            row(src)["attendees_day1"] = n
    for s_ in data["sales"]:
        src = s_.get("source") or ""
        if src.startswith("partner:"):
            x = row(src)
            x["cash"] += s_["cash"]
            if s_.get("via", "checkout") == "checkout":
                x["buyers"] += s_["count"]
    for c in data.get("calls", []):
        src = c.get("source") or ""
        if src.startswith("partner:"):
            row(src)["buyers"] += c["closed"]
    for r in data["refunds"]:
        src = r.get("source") or ""
        if src.startswith("partner:"):
            x = row(src)
            x["refunds"] += r["count"]; x["refunded"] += r["amount"]
    rates = {}
    for pname, v in (data.get("partners") or {}).items():
        rates[pname.casefold()] = v.get("commission_rate")
        row("partner:" + pname)
    for name, x in rows.items():
        x["net_cash"] = round(x["cash"] - x["refunded"], 2)
        x["cash"], x["refunded"] = round(x["cash"], 2), round(x["refunded"], 2)
        x["show_up"] = None if not x["registrations"] or x["attendees_day1"] is None else \
            round(x["attendees_day1"] / x["registrations"], 4)
        r = rates.get(name.casefold())
        x["commission_rate"] = r
        x["commission_due"] = None if r is None else round(max(x["net_cash"], 0) * r, 2)
    return rows


def fnum(x):
    return launch_fmt(x)


def fpct(x):
    return "–" if x is None else f"{x * 100:.1f}%"


def money_s(x):
    return f"${x:,.0f}"


def report_md(r, heading=True):
    L = []
    test = r.get("test")
    if heading:
        L += [f"# {'TEST · ' if test else ''}{r['name']}: launch debrief", ""]
    if test:
        L += ["> **TEST / synthetic data.** Not a real launch: do not use these numbers as history.", ""]
    ev = dt.date.fromisoformat(r["event_date"])
    L += [f"{r['format']} · {r['days']} day{'s' if r['days'] > 1 else ''} from {ev.strftime('%a')} {ev} ({r['tz']}) · "
          f"{'paid' if r['paid_event'] else 'free'} event · close: {r['close_mode']} · goal {plural(r['goal']['buyers'], 'buyer')} / "
          f"{money_s(r['goal']['cash'])} · plan: {r['plan_source']}", "", "## Results", "",
          "| Stage | Actual | Expected from the list | vs expected | Needed for the goal |", "|---|---|---|---|---|"]
    for f in r["funnel"]:
        L.append(f"| {f['stage']} | {fnum(f['actual'])} | {fnum(f['expected'])} | {fpct(f['vs_expected'])} | "
                 f"{fnum(f['needed_for_goal'])} |")
    m = r["money"]
    L += ["", f"- Cash collected {money_s(m['cash'])} · booked {money_s(m['booked'])} · refunded {money_s(m['refunded'])} "
              f"({plural(r['refunds']['count'], 'refund')}"
              + (f", {fpct(r['refunds']['rate'])} of buyers" if r['refunds']['rate'] is not None else "") + ")"
              + f" · net cash {money_s(m['net_cash'])} · net booked {money_s(m['net_booked'])}"]
    if m.get("ticket_cash") is not None:
        L.append(f"- Event revenue (in the cash above): {plural(m['tickets'], 'ticket')} {money_s(m['ticket_cash'])}"
                 + (f" · {plural(m['vip_upgrades'], 'VIP upgrade')} {money_s(m['vip_cash'])}" if m.get("vip_upgrades") else ""))
    L.append(f"- Live counts are {r['live_definition']}"
             + (" · peak at once: " + ", ".join(f"Day {k} {v:,}" for k, v in r["peak_concurrent"].items())
                if r.get("peak_concurrent") else ""))
    if r["per_registrant"]:
        L.append(f"- Revenue per registrant: {money_s(r['per_registrant']['cash'])} cash / {money_s(r['per_registrant']['booked'])} "
                 "booked (no published benchmark: compare with your own last launch)")
    c = r["conversion"]
    L.append(f"- Conversion of those who saw the price: {fpct(c['of_saw_price'])} · {fpct(c['of_day1'])} of Day-1 attendees · "
             f"{fpct(c['of_registrants'])} of registrants")
    if r["calls"]:
        k = r["calls"]
        L.append(f"- Calls: {fnum(k['booked'])} booked ({fpct(k['booked_of_saw_price'])} of those who saw the offer) · "
                 f"{fnum(k['held'])} held (show rate {fpct(k['show_rate'])}) · {fnum(k['closed'])} closed (close rate "
                 f"{fpct(k['close_rate'])})" + (f" · {money_s(k['value'])} booked on calls" if k.get("value") else ""))
    if r["retention"]:
        L.append("- Day-over-day retention: " + " · ".join(
            f"D{x['from']}→D{x['to']} {fpct(x['actual'])} (plan {fpct(x['plan'])})" for x in r["retention"]))
    gp, gg = r["goal_progress"], r["goal_gap"]
    L.append(f"- Against the goal: {fpct(gp['buyers'])} of buyers (net of refunds), {fpct(gp['cash_booked'])} of the cash goal (net booked)")
    if gg["expected_buyers_from_list"] is not None:
        L.append(f"- Goal gap: the list was expected to give about {gg['expected_buyers_from_list']:.1f} of the "
                 f"{gg['goal_buyers']} buyers the goal needs (a gap of {gg['gap_the_plan_showed']:.1f} the plan already "
                 "showed); leaks below are measured against the expected path")
    if r["registrations_by_source"]:
        L.append("- Registrations by source: " + ", ".join(f"{k} {v:,}" for k, v in r["registrations_by_source"].items()))
    if r["not_logged"]:
        L.append(f"- Not logged yet: {', '.join(r['not_logged'])}")
    if r["benchmarks"]:
        L += ["", "| Benchmark | Actual | Range | Status | Source |", "|---|---|---|---|---|"]
        for b in r["benchmarks"]:
            f = (lambda x: f"×{x:.2f}") if b["stage"] == "saw_price" else fpct
            L.append(f"| {b['label']} | {f(b['actual'])} | {f(b['range'][0])}–{f(b['range'][1])} | {b['status']} | {b['source']} |")
    if r.get("partners"):
        L += ["", "| Partner | Registered | Day-1 live | Buyers | Cash | Refunds | Net cash | Commission due |",
              "|---|---|---|---|---|---|---|---|"]
        for name, x in r["partners"].items():
            L.append(f"| {name} | {fnum(x['registrations'])} | {fnum(x['attendees_day1'])} | {fnum(x['buyers'])} | "
                     f"{money_s(x['cash'])} | {x['refunds']} ({money_s(x['refunded'])}) | {money_s(x['net_cash'])} | "
                     + (f"{money_s(x['commission_due'])} at {fpct(x['commission_rate'])}" if x["commission_rate"] is not None
                        else "rate not set (partner --name … --rate R)") + " |")
        L.append("\nCommission is on net cash; pay it after the refund window closes.")
    L += ["", "## Leaks", ""]
    if r["leaks"]:
        for i, x in enumerate(r["leaks"], 1):
            L.append(f"{i}. **{x['label']}**: {fpct(x['actual'])} vs plan {fpct(x['plan'])} "
                     f"(about {x['buyers_lost']:.1f} buyers lost)"
                     + (" (the plan for this stage is a Build Room assumption)" if x.get("plan_is_assumption") else "")
                     + f". Fix: {x['fix']}.")
    else:
        L.append("- No stage fell short of plan (or not enough is logged yet).")
    L += ["", "## Lessons", ""]
    L += [f"- {x}" for x in r.get("lessons") or []] or ["- (add the member's own lessons with obsidian --lesson \"...\")"]
    L += ["", "## What to protect", ""]
    L += [f"- **{x['label']}** beat plan ({fpct(x['actual'])} vs {fpct(x['plan'])}): {x['keep']}." for x in r["protect"]] or \
         ["- Nothing measured beat plan this time: protect what attendees said was most useful (chat, survey, replies)."]
    L += ["", "## Sources", ""] + [f"- **{k}**: {v}" for k, v in r["sources"].items()]
    return "\n".join(L) + "\n"


def cmd_report(data, a):
    r = build_report(data)
    if a.md is not None:
        target = Path(a.md) if a.md else Path(a._path).parent / "debrief-numbers.md"
        if target.name.lower() == "debrief.md":
            refuse(f"{target} is the member's own debrief: the report never writes debrief.md. Use the default "
                   "(report --md writes debrief-numbers.md in the launch folder) or another FILE")
        if target.exists() and not a.force:
            text = target.read_text(encoding="utf-8", errors="replace")
            if not text.startswith(MARKER):
                refuse(f"{target} exists and was not written by the report (it may hold hand-written notes); choose "
                       "another FILE, or pass --force to overwrite it")
            if END_MARKER in text and text.split(END_MARKER, 1)[1].strip():
                refuse(f"{target} has text added after the report's end marker; move it to debrief.md (or pass "
                       "--force to overwrite it)")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(MARKER + "\n" + report_md(r) + "\n" + END_MARKER + "\n", encoding="utf-8")
        r["written"] = str(target)
    return r


# ---------------- pace ----------------

def curve_share(start, day1, on):
    """Cumulative share of registrations expected by the end of `on` (Livestorm 2026 shape)."""
    n = (day1 - start).days                          # registration days before Day 1
    if on < start:
        return 0.0
    if on >= day1:
        return 1.0
    daily = {}
    week = [day1 - dt.timedelta(days=i) for i in range(1, 7) if day1 - dt.timedelta(days=i) >= start]
    early = [start + dt.timedelta(days=i) for i in range(n) if start + dt.timedelta(days=i) not in week]
    if early:
        for d in week:
            daily[d] = (LIVESTORM_WEEK - LIVESTORM_DAY) / len(week)
        for d in early:
            daily[d] = (1 - LIVESTORM_WEEK) / len(early)
    else:
        for d in week:
            daily[d] = (1 - LIVESTORM_DAY) / len(week)
    return round(sum(v for d, v in daily.items() if d <= on), 6)


def cmd_pace(data, a):
    plan = data.get("plan") or {}
    day1 = dt.date.fromisoformat(data["event_date"])
    on = today(a)
    start = plan.get("invites_start")
    start = dt.date.fromisoformat(start) if start else day1 - dt.timedelta(days=21 if data.get("paid_event") else 14)
    share = curve_share(start, day1, on)
    got = total_regs(data, on.isoformat())
    exp = (plan.get("expected") or {}).get("registrants")
    rngs = plan.get("expected_registrants_range") or {}
    need = (plan.get("needed") or {}).get("registrants")
    out = {"date": on.isoformat(), "window": {"start": start.isoformat(), "day1": day1.isoformat(),
                                              "curve": "Livestorm 2026: 15.3% on the day, 49.6% in the final week "
                                                       "(the day included), the rest evenly before"},
           "curve_share_to_date": share, "registered_to_date": got,
           "needed_for_goal_to_date": None if not need else round(need * share, 1)}
    target = exp if exp else need
    if exp:
        out["expected_to_date"] = {s: round(v * share, 1) for s, v in rngs.items()} if rngs else {"typical": round(exp * share, 1)}
        out["expected_to_date"]["typical"] = round(exp * share, 1)
    if not target:
        out["status"] = "no plan to pace against"
        return out
    if share == 0:
        out["status"] = "before the invitation window"
        out["say"] = f"Invitations start {start}; nothing is expected yet."
        return out
    pct_ = got / (target * share)
    out["vs_curve"] = round(pct_, 3)
    out["status"] = "ahead" if pct_ >= 1.10 else "behind" if pct_ < .90 else "on pace"
    caut = rngs.get("cautious")
    out["below_cautious"] = bool(caut and got < caut * share)
    what = "the expected path" if exp else "what the goal needs (no expected path)"
    out["say"] = (f"{got:,} registrations by {on}: {out['status']} ({pct_:.0%} of {what} for this date, "
                  f"{share:.0%} of the window's registrations due by now)"
                  + ("; below the cautious curve: act now (more invitations, a partner wave, a reminder to the list)"
                     if out["below_cautious"] else ""))
    out["source"] = {"Livestorm 2026": SOURCES["Livestorm 2026"]}
    return out


# ---------------- obsidian ----------------

def vault_check(a):
    v = Path(a.vault).expanduser()
    if not v.is_dir():
        refuse(f"no vault folder at {a.vault}")
    warn = []
    if not (v / ".obsidian").is_dir():
        if not a.no_obsidian_check:
            refuse(f"{a.vault} has no .obsidian folder, so it does not look like an Obsidian vault. Pass the vault's "
                   "root folder, or --no-obsidian-check to write there anyway")
        warn.append(f"{a.vault} has no .obsidian folder; written anyway (--no-obsidian-check)")
    return v, warn


def yq(s):
    s = str(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"' if re.search(r'[:#\[\]{},"\']|^\s|\s$', s) else s


def index_line(date, stem, name, fmt, extra=""):
    return f"- {date} · [[{stem}]] · {name} · {fmt}" + (f" · {extra}" if extra else "")


def cmd_obsidian(data, a):
    v, warn = vault_check(a)
    for x in a.lesson or []:
        if x not in data.setdefault("lessons", []):
            data["lessons"].append(x)
    r = build_report(data)
    test = bool(data.get("test"))
    stem = data["slug"] if re.match(r"\d{4}-\d{2}-", data["slug"]) else f"{data['event_date'][:7]}-{data['slug']}"
    note = v / ROOT / f"{stem}.md"
    if note.exists() and not a.force:
        refuse(f"{note} already exists; pass --force to overwrite it")
    existed = note.exists()
    title = ("TEST · " if test else "") + data["name"] + " launch debrief"
    fm = ["---", f"title: {yq(title)}", "type: launch", f"date: {data['event_date']}",
          f"format: {data['format']}", f"close: {data.get('close_mode', 'checkout')}",
          "tags: [launch, event" + (", test" if test else "") + "]", f"status: {a.status}"] + \
         (["test: true"] if test else []) + ["source: buildroom-event-launcher", "---", ""]
    body = report_md(r)
    folder = Path(a._path).resolve().parent
    link = None
    try:
        rel = folder.relative_to(v.resolve())
        for cand in ("plan.md", "calendar.md", "debrief-numbers.md", "debrief.md"):
            if (folder / cand).exists():
                link = f"[[{(rel / cand).with_suffix('').as_posix()}|{rel.as_posix()}]]"
                break
        shown = link or f"`{rel.as_posix()}`"
    except ValueError:
        shown = f"`{folder}` (outside the vault)"
    body = body.replace("\n## Results", f"Launch folder: {shown}\n\n## Results", 1)
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("\n".join(fm) + body, encoding="utf-8")
    idx = v / ROOT / "_index.md"
    regs = (r["funnel"][0] or {}).get("actual")
    line = index_line(data["event_date"], stem, ("TEST · " if test else "") + data["name"], data["format"],
                      f"{fnum(regs)} registered · "
                      + (plural(r['buyers_net'], 'buyer') if r['buyers_net'] is not None else '– buyers')
                      + f" (net of refunds) · {money_s(r['money']['net_cash'])} cash")
    text = idx.read_text(encoding="utf-8") if idx.exists() else "# Launches\n\nOne line per launch, newest last.\n"
    lines = text.splitlines()
    ours = lambda x, s_: f"[[{s_}]]" in x and (INDEX_MARK in x or x.startswith(f"- ") and f" · [[{s_}]] · " in x
                                               and re.match(r"- (\d{4}-\d{2}-\d{2}|\?) · \[\[", x))
    marked = line + " " + INDEX_MARK
    hit = [i for i, x in enumerate(lines) if ours(x, stem)]
    if hit:
        lines[hit[0]] = marked                       # only a line this script wrote is updated, in place
        lines = [x for i, x in enumerate(lines) if i not in hit[1:]]
    backfilled, new_lines = [], []
    for n in find_launch_notes(v, include_test=True)[0]:
        s_ = Path(n["file"]).stem
        if n["found_in"] != "launches":
            continue
        if s_ == stem or any(f"[[{s_}]]" in x for x in lines):
            continue
        fmn = n["frontmatter"]
        new_lines.append(index_line(fmn.get("date", "?"), s_, ("TEST · " if is_test(fmn) else "") + str(fmn.get("title", s_)),
                                    fmn.get("format", "?"), "back-filled from the note") + " " + INDEX_MARK)
        backfilled.append(s_)
    if not hit:
        new_lines.append(marked)
    if new_lines:                                    # appended at the end, the new lines in date order among themselves
        while lines and not lines[-1].strip():
            lines.pop()
        lines += [""] if lines and not lines[-1].startswith("- ") else []
        lines += sorted(new_lines, key=lambda x: x[2:12])
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = {"written": str(note), "overwrote": existed, "test": test, "index": str(idx), "index_line": line,
           "index_updated": "replaced" if hit else "appended", "index_backfilled": backfilled}
    if warn:
        out["warnings"] = warn
    return out


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return v


def frontmatter(text):
    """(dict, body). Handles key: value, quoted values, inline lists [a, b] and YAML block lists (key: then
    '  - item' lines). Keys are lower-cased."""
    if not text.startswith("---"):
        return {}, text
    end = re.search(r"^---\s*$", text[3:], re.M)
    if not end:
        return {}, text
    block, body = text[3:3 + end.start()], text[3 + end.end():]
    fm, cur = {}, None
    for ln in block.splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s*(.*)$", ln)
        if m and cur is not None:
            if not isinstance(fm.get(cur), list):
                fm[cur] = []
            if m.group(1).strip():
                fm[cur].append(_scalar(m.group(1)))
            continue
        if ":" not in ln or ln[:1] in " \t":
            continue
        k, v = ln.split(":", 1)
        cur, v = k.strip().lower(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            fm[cur] = [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
        elif v == "":
            fm[cur] = ""
        else:
            fm[cur] = _scalar(v)
    return fm, body.lstrip("\n")


HEADINGS = {   # matched as whole words anywhere in the heading, case-insensitively, at any level
    "protect": ("what to protect", "protect", "what worked", "worked well", "what went well", "went well", "wins",
                "keep", "keepers"),
    "lessons": ("lesson", "lessons", "what broke", "what went wrong", "what didn't work", "what did not work",
                "what didnt work", "leaks", "leak", "takeaways", "what we learned", "what i learned", "next time",
                "what i'd change", "what id change", "what to change", "mistakes", "fixes"),
    "results": ("results", "result", "numbers", "the numbers", "metrics", "scoreboard", "funnel", "outcome",
                "outcomes", "stats", "kpis"),
}
NAME_RE = re.compile(r"launch|event|boot-?camp|camp|webinar|challenge|workshop|intensive|debrief", re.I)
DEBRIEF_NAME_RE = re.compile(r"(?<![a-z])(debrief|retro|retrospective|post[- ]?mortem|launch review|audit)(?![a-z])", re.I)
TYPES = {"launch", "debrief", "event", "audit", "retro", "retrospective", "review", "post-mortem", "postmortem", "prep"}
TAGS = {"launch", "launches", "debrief", "event", "retro", "retrospective", "post-mortem", "postmortem", "audit"}
FOREIGN_TYPES = {"source", "sources", "transcript", "clipping", "clippings", "reference", "podcast", "article", "book",
                 "highlight", "highlights", "literature", "client", "clients"}
FOREIGN_TAGS = {"clippings", "clipping", "readwise", "transcript", "podcast", "source", "client", "clients",
                "flight-club", "reference"}
SKIP_DIRS = {".obsidian", ".trash", ".git", "external", "sources", "source", "readwise", "clippings", "clipping",
             "transcripts", "transcript", "flight-club", "flight club", "imports", "imported", "import", "kindle",
             "highlights", "web clips", "webclips", "snipd", "omnivore", "references", "clients", "client"}
TEMPLATE_DIR = re.compile(r"^[\d\s._-]*_?templates?$", re.I)
TEMPLATE_TEXT = re.compile(r"\{\{\s*(date|title|time)\b[^}]*\}\}|<%\s*tp\.", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().-]{6,}\d(?![\w/])")


def redact(text):
    if not isinstance(text, str):
        return text
    text = EMAIL_RE.sub("[email removed]", text)
    def ph(m):
        x = m.group(0)
        digits = re.sub(r"\D", "", x)
        if re.search(r"\d{4}-\d{2}-\d{2}", x) or not 9 <= len(digits) <= 15:
            return x
        if not (x.startswith("+") or re.search(r"[\s().-]", x)):
            return x
        return "[phone removed]"
    return PHONE_RE.sub(ph, text)


def tag_tokens(fm):
    raw = fm.get("tags", fm.get("tag", ""))
    items = raw if isinstance(raw, list) else re.split(r"[,\s]+", str(raw))
    out = set()
    for x in items:
        x = str(x).strip().strip("#").lower()
        if x:
            out.add(x)
            out.update(p for p in x.split("/") if p)
    return out


def is_test(fm):
    return str(fm.get("test")).lower() == "true" or "test" in tag_tokens(fm)


def fm_match(fm):
    return str(fm.get("type", "")).strip().lower() in TYPES or bool(tag_tokens(fm) & TAGS)


def foreign(fm, authors):
    """Why a note is imported material or a client note (None when it is the member's own)."""
    t = str(fm.get("type", "")).strip().lower()
    if t in FOREIGN_TYPES:
        return f"type: {t}"
    bad = tag_tokens(fm) & FOREIGN_TAGS
    if bad:
        return "tag " + ", ".join(sorted(bad))
    for k in ("source", "url", "link", "source_url"):
        v = str(fm.get(k, "") or "")
        if re.match(r"(https?://|www\.)", v):
            return f"{k}: {v[:60]}"
    for k in ("author", "speaker", "host", "creator"):
        v = fm.get(k)
        vals = v if isinstance(v, list) else [v] if v else []
        others = [str(x) for x in vals if str(x).strip("[] ").lower() not in {a.lower() for a in authors} | {"me", "self"}]
        if others:
            return f"{k}: {', '.join(others)[:60]} (pass --author NAME if that is the member)"
    return None


def norm_heading(t):
    t = t.lower().replace("’", "'")
    t = re.sub(r"[^a-z' ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def heading_kind(title):
    t = norm_heading(title)
    for k, names in HEADINGS.items():
        if any(re.search(r"(?<![a-z'])" + re.escape(n) + r"(?![a-z])", t) for n in names):
            return k
    return None


def sections(body):
    """{results, lessons, protect}: the text under every matching heading (any level, case-insensitive, by the words
    it contains), running to the next heading of the same or a higher level, so ### sub-headings stay inside."""
    out = {k: [] for k in HEADINGS}
    lines = body.splitlines()
    heads, fence = [], False
    for i, ln in enumerate(lines):
        if ln.strip().startswith(("```", "~~~")):
            fence = not fence
        if fence:
            continue
        m = re.match(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$", ln)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    skip_until = -1
    for n, (i, level, title) in enumerate(heads):
        if i < skip_until:
            continue
        k = heading_kind(title)
        if not k:
            continue
        end = next((j for j, lv, _ in heads[n + 1:] if lv <= level), len(lines))
        txt = "\n".join(lines[i + 1:end]).strip()
        if txt:
            out[k].append(txt)
        skip_until = end
    return {k: ("\n\n".join(v) if v else None) for k, v in out.items()}


def first_title(fm, body, p):
    if fm.get("title"):
        return str(fm["title"])
    m = re.search(r"^#[ \t]+(.+?)\s*$", body, re.M)
    return m.group(1) if m else p.stem


def note_date(fm, p):
    d = str(fm.get("date", "") or "")
    m = re.match(r"(\d{4}-\d{2}(?:-\d{2})?)", d)
    if m:
        return m.group(1)
    m = re.search(r"(?<!\d)(\d{4}-\d{2}(?:-\d{2})?)(?!\d)", p.stem)
    return m.group(1) if m else None


def find_launch_notes(v, include_test=False, authors=()):
    """(notes, looked_in, skipped) — the member's own launch notes: launches/ first, then the whole vault."""
    looked, notes, seen, skipped = [], [], set(), []
    def add(p, where):
        rel = p.relative_to(v)
        if any(x.lower() in SKIP_DIRS or TEMPLATE_DIR.match(x) for x in rel.parts[:-1]):
            return
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return
        fm, body = frontmatter(text)
        title = first_title(fm, body, p)
        top = p.parent == v / ROOT
        named = bool(DEBRIEF_NAME_RE.search(p.stem) or DEBRIEF_NAME_RE.search(title))
        if not (fm_match(fm) or named or (where == "launches" and top and NAME_RE.search(p.stem))):
            return
        if TEMPLATE_TEXT.search(text):
            skipped.append({"file": str(p), "why": "template ({{date}} / {{title}} placeholders)"}); return
        why = foreign(fm, authors)
        if why:
            skipped.append({"file": str(p), "why": "not the member's own note: " + why}); return
        if is_test(fm) and not include_test:
            skipped.append({"file": str(p), "why": "test note"}); return
        seen.add(p.resolve())
        notes.append({"file": str(p), "found_in": where, "frontmatter": fm, "body": body, "title": title,
                      "date": note_date(fm, p)})
    ld = v / ROOT
    if ld.is_dir():
        looked.append(f"{ld}/ (frontmatter type or tags, a debrief-like or launch-like file name)")
        work = {d.resolve() for d in ld.rglob("*") if d.is_dir() and ((d / "tracker.json").exists() or (d / "plan.json").exists())}
        for p in sorted(ld.rglob("*.md")):
            if p.name.startswith("_") or any(w in p.resolve().parents for w in work):
                continue
            add(p, "launches")
    else:
        looked.append(f"{ld}/ (missing)")
    looked.append(f"{v}/ (every other note: frontmatter type or tags, or a debrief, retro, post-mortem, launch review "
                  "or audit file name or title; skipped: templates, External, Sources, Readwise, Clippings, "
                  "transcripts, clients and other imported material)")
    for p in sorted(v.rglob("*.md")):
        rel = p.relative_to(v)
        if rel.parts[0] == ROOT or p.resolve() in seen:
            continue
        add(p, "vault")
    return notes, looked, skipped


def cmd_obsidian_read(a):
    v, warn = vault_check(a)
    found, looked, skipped = find_launch_notes(v, a.include_test, a.author or ())
    notes = []
    for n in found:
        s = {k: redact(x) for k, x in sections(n["body"]).items()}
        row = {"file": n["file"], "found_in": n["found_in"], "title": redact(n["title"]), "date": n["date"],
               "frontmatter": {k: ([redact(x) for x in val] if isinstance(val, list) else redact(val))
                               for k, val in n["frontmatter"].items()}, **s}
        if not any(s.values()):
            row["body_excerpt"] = redact(n["body"].strip()[:1500])
            warn.append(f"{n['file']}: no Results / Lessons / What to protect heading (or a variant such as Numbers, "
                        "Key lessons, What broke, Wins, Keep): read body_excerpt and summarise it with the member")
        else:
            miss = [k for k, x in s.items() if not x]
            if miss:
                row["missing"] = miss
        notes.append(row)
    notes.sort(key=lambda n: (n["date"] is not None, n["date"] or "", n["file"]), reverse=True)
    out = {"vault": str(v), "launches": notes, "count": len(notes), "looked_in": looked,
           "order": "newest first by frontmatter date, else a date in the file name; undated last",
           "redacted": "email addresses and phone numbers are removed from everything returned"}
    if skipped:
        out["skipped"] = skipped
        out["skipped_test_notes"] = [x["file"] for x in skipped if x["why"] == "test note"]
    if not notes:
        warn.append("no launch notes found. Looked in: " + "; ".join(looked) + ". Ask the member where past launch "
                    "notes or debriefs live, and offer to write a summary note for an old launch (with their yes)")
    if warn:
        out["warnings"] = warn
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def mk(name):
        s = sub.add_parser(name)
        s.add_argument("--file"); s.add_argument("--slug"); s.add_argument("--date"); return s
    s = sub.add_parser("slug"); s.add_argument("--name", required=True); s.add_argument("--event-date", required=True)
    s.add_argument("--date")
    s = mk("init"); s.add_argument("--name", required=True)
    s.add_argument("--format", required=True, choices=sorted(launch_plan.FORMATS)); s.add_argument("--days", type=int, required=True)
    s.add_argument("--tz", required=True); s.add_argument("--event-date", required=True)
    s.add_argument("--goal-buyers", type=int, required=True); s.add_argument("--goal-cash", required=True)
    s.add_argument("--plan"); s.add_argument("--paid-event", action="store_true")
    s.add_argument("--close", choices=CLOSE_MODES); s.add_argument("--list-size", type=int)
    s.add_argument("--test", action="store_true", help="mark the ledger as test/synthetic data")
    s.add_argument("--sms", action="store_true", help="texts are planned: sms_compliance becomes a critical gate item")
    s.add_argument("--event", help="event.json: its reminders.sms marks SMS as planned")
    s = mk("log-reg"); s.add_argument("n", type=int); s.add_argument("--source")
    s = mk("log-day"); s.add_argument("--day", type=int, required=True)
    s.add_argument("--live", "--unique", dest="live", type=int, required=True,
                   help="unique attendees that day (the Zoom participant report; the show-up and retention benchmarks "
                        "and import-csv use this definition)")
    s.add_argument("--peak", type=int, help="peak concurrent count that day (stored separately, for reference)")
    s.add_argument("--source-count", action="append", metavar="SOURCE=N",
                   help="attendees by source, for example partner:Jo=40 (repeatable)")
    s = mk("log-close"); s.add_argument("--present", type=int, required=True); s.add_argument("--saw-price", type=int, required=True)
    s = mk("log-sale"); s.add_argument("--tier", required=True); s.add_argument("--price", required=True)
    s.add_argument("--count", type=int, required=True); s.add_argument("--payment", choices=["full", "plan"], default="full")
    s.add_argument("--booked"); s.add_argument("--via", choices=["checkout", "call"], default="checkout")
    s.add_argument("--source", help="partner:NAME (or another source) for partner attribution")
    s = mk("log-calls"); s.add_argument("--booked", type=int, required=True); s.add_argument("--held", type=int, required=True)
    s.add_argument("--closed", type=int, required=True); s.add_argument("--value"); s.add_argument("--tier", default="Call close")
    s.add_argument("--source")
    s = mk("log-refund"); s.add_argument("--tier", required=True); s.add_argument("--count", type=int, required=True)
    s.add_argument("--amount", required=True); s.add_argument("--booked-cancelled", type=float); s.add_argument("--source")
    s = mk("log-tickets"); s.add_argument("--count", type=int, required=True); s.add_argument("--price", required=True)
    s.add_argument("--vip-count", type=int); s.add_argument("--vip-price"); s.add_argument("--source")
    s = mk("partner"); s.add_argument("--name", required=True)
    s.add_argument("--rate", "--commission-rate", dest="rate", required=True, help="commission rate, '30%' or 0.3")
    s = mk("import-csv"); s.add_argument("csv"); s.add_argument("--map", nargs="+", required=True)
    s.add_argument("--replace", action="store_true")
    s = mk("gate"); s.add_argument("--set", nargs="+", action="append", metavar="ITEM STATUS [NOTE]")
    s.add_argument("--note"); s.add_argument("--reset", action="append", metavar="ITEM")
    s.add_argument("--close-morning", action="store_true", help="the same as --stage close_morning")
    s.add_argument("--stage", choices=STAGES)
    s = mk("pace")
    s = mk("report"); s.add_argument("--md", nargs="?", const=""); s.add_argument("--force", action="store_true")
    s = mk("obsidian"); s.add_argument("--vault", required=True); s.add_argument("--force", action="store_true")
    s.add_argument("--no-obsidian-check", action="store_true"); s.add_argument("--status", default="debriefed")
    s.add_argument("--lesson", action="append")
    s = mk("obsidian-read"); s.add_argument("--vault", required=True); s.add_argument("--no-obsidian-check", action="store_true")
    s.add_argument("--include-test", action="store_true")
    s.add_argument("--author", action="append", help="the member's own name, so notes with author: NAME count")
    a = ap.parse_args(argv)
    today(a)                                  # a bad --date is refused before anything is read or written
    if a.cmd == "obsidian-read":
        print(json.dumps(cmd_obsidian_read(a), indent=1, ensure_ascii=False)); return 0
    if a.cmd == "slug":
        print(json.dumps(cmd_slug(a), indent=1, ensure_ascii=False)); return 0
    path = tracker_path(a)
    a._path = str(path)
    if a.cmd == "init":
        data, out = cmd_init(path, a)
        save(path, data)
        print(json.dumps(out, indent=1, ensure_ascii=False)); return 0
    if not path.exists():
        refuse(f"no launch tracker at {path}. Create it with: launch_tracker.py init --name ... (or pass the right "
               "--file / --slug)")
    data = load(path)
    fn = {"log-reg": cmd_log_reg, "log-day": cmd_log_day, "log-close": cmd_log_close, "log-sale": cmd_log_sale,
          "log-calls": cmd_log_calls, "log-refund": cmd_log_refund, "import-csv": cmd_import_csv, "gate": cmd_gate,
          "pace": cmd_pace, "report": cmd_report, "obsidian": cmd_obsidian, "log-tickets": cmd_log_tickets,
          "partner": cmd_partner}[a.cmd]
    out = fn(data, a)
    if getattr(a, "_ledger_note", None):
        out = {"ledger": a._ledger_note, **out}
    if a.cmd in ("log-reg", "log-day", "log-close", "log-sale", "log-calls", "log-refund", "import-csv", "log-tickets",
                 "partner") \
            or (a.cmd == "gate" and (a.set or a.reset)) or (a.cmd == "obsidian" and a.lesson):
        save(path, data)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
