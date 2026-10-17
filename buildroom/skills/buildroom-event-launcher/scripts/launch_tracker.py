#!/usr/bin/env python3
"""Event Launcher tracker: the launch ledger, the launch gate, the debrief and the Obsidian note.

Local only. It stores what the member tells it (counts, prices, gate answers) in one JSON file per
launch. It never contacts Zoom, GoHighLevel or Stripe, and import-csv keeps counts only: no names,
emails or phone numbers from the export are stored.

Usage
  The ledger is launches/<slug>/tracker.json under the current folder; init makes the slug YYYY-MM-<name>
  from the event date and the name (or --slug S). Pick a ledger with --slug S or --file P;
  with neither, the only tracker under ./launches/ is used (two or more: refused, name one). Only init
  creates a ledger; every other command refuses when it is missing. --date YYYY-MM-DD replays "today".

  launch_tracker.py init --name "Cash Flow Bootcamp" --format bootcamp3|challenge5|workshop|webinar --days N
                         --tz IANA --event-date YYYY-MM-DD --goal-buyers N --goal-cash X [--paid-event]
                         [--plan plan.json] [--slug S]
      --plan reads launch_plan.py's plan.json (the typical scenario is the plan). Without it the plan is
      the typical scenario of the Build Room benchmarks for this format, goal and average price.
  launch_tracker.py log-reg N [--source list|partner:NAME|ads|social] [--date]     new registrations
  launch_tracker.py log-day --day 1 --live N [--peak N] [--date]                  live attendees that day
  launch_tracker.py log-close --present N --saw-price N [--date]
      present: in the room when the offer was made; saw the price: everyone who saw it, live or later
  launch_tracker.py log-sale --tier NAME --price P --count N [--payment full|plan --booked TOTAL] [--date]
      full: cash and booked are price × count. plan: --price is what each buyer has paid so far (the
      first instalment) and --booked is the total contract value of these N sales (required).
  launch_tracker.py log-refund --tier NAME --count N --amount TOTAL [--booked-cancelled X] [--date]
      amount: cash refunded; --booked-cancelled: unpaid instalments cancelled with the refund
  launch_tracker.py import-csv FILE --map registered=TAG,day1=TAG,day2=TAG,present=TAG,saw_price=TAG
      counts rows of a CRM export (GoHighLevel contacts CSV) whose tags column holds each tag (TAG * counts
      every row) and sets those counts in the ledger. Only the counts and the file name are stored.
  launch_tracker.py gate [--set ITEM pass|fail|na ...] [--note "..."]
      the launch gate: GO only when every critical item is pass (or na with a note); otherwise HOLD with
      the list. --set can repeat; --note applies to the items set in the same call.
  launch_tracker.py report [--md FILE]
      funnel vs plan, day-over-day retention, conversion, cash vs booked, refunds, revenue per
      registrant, benchmark ranges with sources, the top three leaks ranked by buyers lost vs plan with a
      fix for each, and what to protect.
  launch_tracker.py obsidian --vault PATH [--force] [--no-obsidian-check] [--status S] [--lesson "..." ...]
      writes the debrief to <vault>/launches/YYYY-MM-<slug>.md (light frontmatter; the slug already
      starts with YYYY-MM) and adds one line to <vault>/launches/_index.md (created if missing). An existing note is never overwritten without
      --force. Refused when the vault folder is missing or has no .obsidian folder (--no-obsidian-check
      writes anyway, with a warning). --lesson (repeatable) is kept in the ledger, so a later --force
      rewrite keeps it.
  launch_tracker.py obsidian-read --vault PATH [--no-obsidian-check]
      lists past launch notes (frontmatter plus their Results and Lessons sections), newest first, so
      the plan can start from earlier lessons. Needs no tracker.

Gate items (references/launch-gate.md)
  critical  money: checkout_tested backup_checkout refund_policy payment_plan_terms
            follow-up: followup_on reminder_tz night_emails (na for a single-day event, set at init)
            truth: proof_classified earnings_claims partner_copy_true real_deadlines single_source
            sending: email_compliance partner_disclosure
  advisory  sms_compliance recording_notice testimonial_permission privacy_notice moderator_links
            first_win_timed live_tech_rehearsed refund_commissions chargeback_ready
  Re-run on the close morning: checkout_tested backup_checkout refund_policy payment_plan_terms followup_on.

Standard library only. Exit code 2 on a refused action (missing ledger, bad input, existing note).
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, csv, datetime as dt, json, os, re, tempfile, unicodedata  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import launch_plan  # noqa: E402

SCHEMA = "buildroom-event-launcher/1"
ROOT = "launches"
SRC_RE = re.compile(r"^(list|ads|social|import|partner:[\w .&'-]+)$", re.I)

SOURCES = dict(launch_plan.SOURCES)
SOURCES.update({
    "FTC 16 CFR 465": "FTC Consumer Reviews and Testimonials Rule (in force 21 Oct 2024): no fake or misleading "
                      "testimonials, civil penalties per violation",
    "FTC earnings claims": "FTC guidance: earnings claims must reflect typical results; 'results not typical' is no cure",
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
    "FTC Endorsement Guides 2023": "Affiliates and JV partners disclose any material connection (commission) clearly; "
                                   "the advertiser is responsible too",
    "Privacy notice": "GDPR / UK GDPR: state what is collected, why and the lawful basis at collection; consent is "
                      "never a pre-ticked box",
    "Card network rules 2026": "Visa VAMP: the US 'excessive' dispute ratio fell from 2.2% to 1.5% on 1 Apr 2026; "
                               "Mastercard ECM at 100 chargebacks and 1.5%",
})

# id, critical, group, what must be true, source (references/launch-gate.md holds the same list in prose)
GATE = [
    ("checkout_tested", True, "money", "Checkout tested end to end on a phone for every tier, the payment plan and the "
     "coupon or VIP checkbox (real card, then refunded); again on the close morning", "Build Room founder run Jul 2026"),
    ("backup_checkout", True, "money", "A second checkout path ready: a plain payment link per tier the moderator can drop "
     "in chat", "Build Room founder run Jul 2026"),
    ("refund_policy", True, "money", "Refund or guarantee terms shown before payment and accepted at checkout, in the same "
     "words as the sales page and the live close (one guarantee, not two)", "Refund disclosure"),
    ("payment_plan_terms", True, "money", "Payment plans are fixed-length and the total (payments × amount) is shown before "
     "checkout (na if there is no plan)", "Payment plan rules"),
    ("followup_on", True, "follow-up", "Every follow-up workflow switched ON (checked in the CRM) and tested with a test "
     "contact: confirmation, reminders, night-before, replay, no-show, cart, failed checkout, buyer welcome",
     "Build Room founder run Jul 2026"),
    ("reminder_tz", True, "follow-up", "Reminder send times verified in the recipient's time zone and the whole schedule "
     "dry-run 24 hours before Day 1 (GoHighLevel's 'Set Event Start Date' uses the account time zone)", "GHL help 2026"),
    ("night_emails", True, "follow-up", "A night-before email scheduled for every day after Day 1 (Day-1-night, Day-2-night…)",
     "Build Room founder run Jul 2026"),
    ("proof_classified", True, "truth", "Proof classified (free-event result / paid-program result / outside example) and "
     "every person's consent on file", "FTC 16 CFR 465"),
    ("earnings_claims", True, "truth", "Earnings claims are typical results, or there are none", "FTC earnings claims"),
    ("partner_copy_true", True, "truth", "Who teaches live is named in every invitation; partner and guest copy never "
     "implies someone will appear who won't", "Build Room founder run Jul 2026"),
    ("real_deadlines", True, "truth", "Deadlines are real and the same for everyone, or honest per-person timers: no "
     "resetting countdowns, no fake 'doors close', no 'live' label on a recording", "FTC dark patterns 2022"),
    ("single_source", True, "truth", "One source of truth (close.md) for prices, terms, dates, replay links and expiry",
     "Build Room founder method"),
    ("email_compliance", True, "sending", "CAN-SPAM footer (postal address), one-click unsubscribe plus a visible link; "
     "SPF, DKIM and DMARC aligned on a sending subdomain", "CAN-SPAM and bulk-sender rules"),
    ("partner_disclosure", True, "sending", "Partners disclose their commission in every promotion that pays them (na if "
     "no partners)", "FTC Endorsement Guides 2023"),
    ("sms_compliance", False, "consent", "SMS only with written consent (a separate, unchecked box) and an approved A2P "
     "10DLC brand and campaign, sent 9 a.m.–8 p.m. in the contact's zone; otherwise email only", "TCPA and A2P 10DLC"),
    ("recording_notice", False, "consent", "Recording announced on the registration page and at the start of each day; "
     "Zoom's recording notice on", "Recording consent"),
    ("testimonial_permission", False, "consent", "Written permission before reusing anyone's chat comment or live words as "
     "a testimonial", "FTC 16 CFR 465"),
    ("privacy_notice", False, "consent", "Privacy notice on the registration page (what, why; for EU/UK the lawful basis "
     "and a separate marketing consent)", "Privacy notice"),
    ("moderator_links", False, "live", "A moderator assigned, with every link they will drop and when, and a backup host "
     "link", "Build Room founder method"),
    ("first_win_timed", False, "live", "The first-win tool timed: the invitation states the measured time, not a guess",
     "Build Room founder run Jul 2026"),
    ("live_tech_rehearsed", False, "live", "Anything new (breakout rooms, a live app, polls) tried with five people first, "
     "or not used", "Build Room founder run Jul 2026"),
    ("refund_commissions", False, "money", "Refunds reverse partner commissions (GoHighLevel does not do it automatically)",
     "GHL help 2026"),
    ("chargeback_ready", False, "money", "Chargeback exposure understood: a clear refund path (Visa's US 'excessive' ratio "
     "is 1.5% from April 2026)", "Card network rules 2026"),
]
CLOSE_MORNING = ["checkout_tested", "backup_checkout", "refund_policy", "payment_plan_terms", "followup_on"]
GATE_IDS = [g[0] for g in GATE]

STAGE_FIX = {
    "registration": "Registrations short of plan: invite earlier and more often (about half of registrations land in "
                    "the final week), add a partner wave, keep registration open through Day 1",
    "show_up": "Day-1 show-up: calendar file on the thank-you page; reminders the day before, the morning of and 15 "
               "minutes before (SMS with consent); pre-work that makes being live worth it; a 'we're live' text at start",
    "retention": "Day {a}→{b} drop: a Day-{a}-night recap with the Day-{b} payoff, a cliffhanger that only pays off live, "
                 "reminder times checked in the recipient's time zone",
    "stay_to_close": "People left before the offer: say when it comes, keep the promised build for after it, keep the "
                     "session inside the planned length",
    "saw_price": "Attendees who never saw the price: switch on the follow-up that shows the offer to everyone who "
                 "attended (replay with the offer, cart emails); the founder lost about 28 sales this way",
    "conversion": "Price-viewers who didn't buy: test checkout on a phone the morning of the close (plan, coupon), a "
                  "payment plan that doesn't punish, a real deadline, a clear 'which one are you' ladder, let ready "
                  "buyers buy early",
}
STAGE_KEEP = {
    "registration": "keep the invitation sequence and the partner wave as they were",
    "show_up": "keep the reminder schedule, the calendar file and the pre-work exactly as they were",
    "retention": "keep the night-before recap and the payoff that only happens live",
    "stay_to_close": "keep the offer timing and the session length",
    "saw_price": "keep the follow-up that put the offer in front of everyone",
    "conversion": "keep the offer, the price ladder and the checkout as they were",
}


def refuse(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(2)


parse_date = launch_plan.parse_date


def today(a):
    return launch_plan.today(a)


def slugify(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "launch"


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
    return data


def tracker_path(a):
    if a.file:
        return Path(a.file)
    if getattr(a, "slug", None):
        return Path(ROOT) / slugify(a.slug) / "tracker.json"
    if a.cmd == "init":
        return Path(ROOT) / f"{parse_date(a.event_date, '--event-date').isoformat()[:7]}-{slugify(a.name)}" / "tracker.json"
    found = sorted(Path(ROOT).glob("*/tracker.json"))
    if len(found) == 1:
        return found[0]
    if not found:
        refuse(f"no launch tracker at ./{ROOT}/<slug>/tracker.json. Create one with: launch_tracker.py init --name ... "
               "(or pass --file / --slug if the ledger is elsewhere)")
    refuse(f"{len(found)} launch trackers under ./{ROOT}/ ({', '.join(p.parent.name for p in found)}): pass --slug")


def nonneg(n, what):
    if n is None or n < 0:
        refuse(f"{what} must be 0 or more")
    return n


# ---------------- plan ----------------

def plan_from_math(m, days):
    t = m["scenarios"]["typical"]
    rates = t["rates"]
    if m["inputs"]["days"] != days:
        return None
    need = launch_plan.reverse(m["goal"]["buyers"], rates, days)   # exact floats, so plan ratios are the plan's rates
    return {"registered": need["registrants"], "day_live": need["day_live"], "present": need["present_at_close"],
            "saw_price": need["saw_price"], "buyers": need["buyers"],
            "rates": {k: rates[k] for k in ("show_up", "retention", "stay_to_close", "saw_price", "conversion") if k in rates},
            "source_keys": sorted(launch_plan.sources_used(m["rates"]))}


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
    cash = launch_plan.money(a.goal_cash, "--goal-cash")
    warnings, plan, src = [], None, None
    if a.plan:
        pp = Path(a.plan)
        if not pp.exists():
            refuse(f"no plan at {a.plan}")
        try:
            pj = json.loads(pp.read_text(encoding="utf-8"))
        except ValueError as e:
            refuse(f"{a.plan} is not readable JSON ({e})")
        if pj.get("schema") != launch_plan.PLAN_SCHEMA:
            refuse(f"{a.plan} is not a launch_plan.py plan file")
        if pj.get("math"):
            if pj["math"]["inputs"].get("format") != a.format:
                warnings.append(f"the plan's math is for {pj['math']['inputs'].get('format')}, this launch is {a.format}")
            if pj["math"]["goal"]["buyers"] != a.goal_buyers:
                warnings.append(f"the plan was worked out for {pj['math']['goal']['buyers']} buyers, the goal here is {a.goal_buyers}")
            plan = plan_from_math(pj["math"], a.days)
            if plan is None:
                warnings.append(f"the plan's math is for {pj['math']['inputs']['days']} days, not {a.days}: the plan "
                                "here comes from the Build Room benchmarks instead")
            else:
                src = f"{a.plan} (typical scenario)"
        else:
            warnings.append(f"{a.plan} has no math section (run launch_plan.py math --out): the plan here comes from "
                            "the Build Room benchmarks")
        if pj.get("timeline") and pj["timeline"].get("event_date") != ev.isoformat():
            warnings.append(f"the plan's timeline is for Day 1 {pj['timeline']['event_date']}, not {ev}")
    if plan is None:
        m = launch_plan.compute_math(goal_buyers=a.goal_buyers, goal_cash=cash, price=cash / a.goal_buyers,
                                     fmt=a.format, days=a.days, paid=a.paid_event)
        plan = plan_from_math(m, a.days)
        src = "Build Room benchmarks (typical scenario; no plan.json)"
    gate = {g: {"status": "open"} for g in GATE_IDS}
    if a.days == 1:
        gate["night_emails"] = {"status": "na", "note": "single-day event", "date": today(a).isoformat()}
    data = {"schema": SCHEMA, "created": today(a).isoformat(), "name": a.name, "slug": path.parent.name,
            "format": a.format, "days": a.days, "tz": a.tz, "event_date": ev.isoformat(), "paid_event": bool(a.paid_event),
            "goal": {"buyers": a.goal_buyers, "cash": cash}, "plan": plan, "plan_source": src,
            "registrations": [], "days_live": {}, "close": None, "sales": [], "refunds": [], "imports": [], "gate": gate}
    out = {"created": str(path), "name": a.name, "slug": data["slug"], "plan_source": src,
           "plan": {k: (round(v) if isinstance(v, float) else [round(x) for x in v] if isinstance(v, list) else v)
                    for k, v in plan.items() if k not in ("rates", "source_keys")}}
    if warnings:
        out["warnings"] = warnings
    return data, out


def total_regs(data):
    return sum(r["n"] for r in data["registrations"])


def cmd_log_reg(data, a):
    nonneg(a.n, "N")
    src = a.source or "list"
    if not SRC_RE.match(src) or src.lower() == "import":
        refuse(f"--source must be list, ads, social or partner:NAME (got {src!r})")
    src = src.lower() if ":" not in src else "partner:" + src.split(":", 1)[1].strip()
    data["registrations"].append({"date": today(a).isoformat(), "n": a.n, "source": src})
    return {"logged": a.n, "source": src, "registered_total": total_regs(data)}


def cmd_log_day(data, a):
    if not 1 <= a.day <= data["days"]:
        refuse(f"--day must be between 1 and {data['days']} for this {data['days']}-day event")
    nonneg(a.live, "--live")
    if a.peak is not None:
        nonneg(a.peak, "--peak")
    on = a.date or (dt.date.fromisoformat(data["event_date"]) + dt.timedelta(days=a.day - 1)).isoformat()
    parse_date(on)
    key = str(a.day)
    replaced = key in data["days_live"]
    data["days_live"][key] = {"live": a.live, **({"peak": a.peak} if a.peak is not None else {}), "date": on}
    out = {"day": a.day, "live": a.live, **({"peak": a.peak} if a.peak is not None else {}), "replaced": replaced}
    warn = []
    regs = total_regs(data)
    if a.day == 1 and regs and a.live > regs:
        warn.append(f"Day 1 live ({a.live}) is more than the registrations logged ({regs}); log the registrations")
    prev = data["days_live"].get(str(a.day - 1))
    if prev and a.live > prev["live"]:
        warn.append(f"Day {a.day} ({a.live}) is higher than Day {a.day - 1} ({prev['live']}): fine if new people joined, "
                    "otherwise check which number is unique attendees and which is the peak")
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
    data["sales"].append({"date": today(a).isoformat(), "tier": a.tier, "price": price, "count": a.count,
                          "payment": a.payment, "cash": round(cash, 2), "booked": round(booked, 2)})
    return {"logged": a.count, "tier": a.tier, "payment": a.payment, "cash": round(cash, 2), "booked": round(booked, 2),
            "buyers_total": sum(s["count"] for s in data["sales"])}


def cmd_log_refund(data, a):
    nonneg(a.count, "--count")
    amount = launch_plan.money(a.amount, "--amount")
    cancelled = float(a.booked_cancelled or 0)
    if cancelled < 0:
        refuse("--booked-cancelled must be 0 or more")
    if a.tier not in {s["tier"] for s in data["sales"]}:
        refuse(f"no sales logged for tier {a.tier!r}; tiers logged: {sorted({s['tier'] for s in data['sales']})}")
    sold = sum(s["count"] for s in data["sales"] if s["tier"] == a.tier)
    refunded = sum(r["count"] for r in data["refunds"] if r["tier"] == a.tier)
    if refunded + a.count > sold:
        refuse(f"{refunded + a.count} refunds for {a.tier!r} but only {sold} sold")
    data["refunds"].append({"date": today(a).isoformat(), "tier": a.tier, "count": a.count, "amount": round(amount, 2),
                            "booked_cancelled": round(cancelled, 2)})
    return {"refund": a.count, "tier": a.tier, "amount": round(amount, 2), "booked_cancelled": round(cancelled, 2)}


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
    applied = {}
    if "registered" in counts:
        delta = counts["registered"] - total_regs(data)
        if delta:
            data["registrations"].append({"date": on, "n": delta, "source": "import"})
        applied["registered"] = {"total": counts["registered"], "change": delta}
    for k, v in counts.items():
        if k.startswith("day"):
            n = int(k[3:])
            data["days_live"][str(n)] = {"live": v, "date": (dt.date.fromisoformat(data["event_date"]) +
                                                             dt.timedelta(days=n - 1)).isoformat(), "imported": True}
            applied[k] = v
    if "present" in counts or "saw_price" in counts:
        c = data["close"] or {"present": 0, "saw_price": 0}
        c.update({k: counts[k] for k in ("present", "saw_price") if k in counts}); c["date"] = on
        data["close"] = c
        applied.update({k: counts[k] for k in ("present", "saw_price") if k in counts})
    data["imports"].append({"date": on, "file": p.name, "rows": len(rows), "map": mp, "counts": counts})
    return {"imported": p.name, "rows": len(rows), "counts": counts, "applied": applied,
            "stored": "counts and the file name only; no names, emails or phone numbers"}


# ---------------- gate ----------------

def gate_view(data):
    items, hold, adv = [], [], []
    for gid, crit, group, what, src in GATE:
        g = data["gate"].get(gid, {"status": "open"})
        items.append({"id": gid, "critical": crit, "group": group, "status": g["status"], "check": what, "source": src,
                      **({"note": g["note"]} if g.get("note") else {})})
        if crit and g["status"] not in ("pass", "na"):
            hold.append(f"{gid}: {what} ({g['status']})")
        elif not crit and g["status"] not in ("pass", "na"):
            adv.append(f"{gid}: {what} ({g['status']})")
    res = "GO" if not hold else "HOLD"
    out = {"result": res, "items": items}
    if hold:
        out["hold"] = hold
        out["say"] = (f"HOLD: {len(hold)} critical item{'s' if len(hold) > 1 else ''} not passed. Fix them before the first "
                      "invitation; the member may still choose to launch, knowing what each open item risks.")
    else:
        out["say"] = "GO: every critical item passes." + (" Advisory items still open." if adv else "")
    if adv:
        out["advisory_open"] = adv
    out["rerun_on_close_morning"] = CLOSE_MORNING
    out["sources"] = {k: SOURCES[k] for k in sorted({g[4] for g in GATE})}
    return out


def cmd_gate(data, a):
    changed = []
    for gid, status in a.set or []:
        if gid not in GATE_IDS:
            refuse(f"unknown gate item {gid!r}; items: {', '.join(GATE_IDS)}")
        status = status.lower()
        if status not in ("pass", "fail", "na"):
            refuse(f"gate status must be pass, fail or na (got {status!r})")
        crit = next(g[1] for g in GATE if g[0] == gid)
        if status == "na" and crit and not a.note:
            refuse(f"{gid} is critical: na needs --note saying why it does not apply")
        data["gate"][gid] = {"status": status, **({"note": a.note} if a.note else {}), "date": today(a).isoformat()}
        changed.append(gid)
    out = gate_view(data)
    if changed:
        out = {"set": changed, **out}
    return out


# ---------------- report ----------------

def ratio(a, b):
    return None if a is None or b in (None, 0) else a / b


def build_report(data):
    days = data["days"]
    plan = data.get("plan") or {}
    regs = total_regs(data) if data["registrations"] else None
    live = [data["days_live"].get(str(k), {}).get("live") for k in range(1, days + 1)]
    close = data.get("close") or {}
    present, saw = close.get("present"), close.get("saw_price")
    sold = sum(s["count"] for s in data["sales"])
    buyers = sold if data["sales"] else (0 if close else None)
    refunds_n = sum(r["count"] for r in data["refunds"])
    refunds_amt = sum(r["amount"] for r in data["refunds"])
    cancelled = sum(r.get("booked_cancelled", 0) for r in data["refunds"])
    cash = sum(s["cash"] for s in data["sales"]); booked = sum(s["booked"] for s in data["sales"])
    net_cash, net_booked = cash - refunds_amt, booked - refunds_amt - cancelled
    pl = [plan.get("registered")] + list(plan.get("day_live") or [None] * days) + [plan.get("present"), plan.get("saw_price"), plan.get("buyers")]
    act = [regs] + live + [present, saw, buyers]
    names = ["Registered"] + [f"Live Day {k}" for k in range(1, days + 1)] + ["Present at the close", "Saw the price", "Buyers"]
    funnel = [{"stage": n, "actual": x, "plan": None if p is None else round(p),
               "vs_plan": None if x is None or not p else round(x / p, 3)} for n, x, p in zip(names, act, pl)]
    # transitions: (key, kind, label, from index, to index)
    trans = [("registration", "registration", "Registrations vs plan", None, 0), ("show_up", "show_up", "Day-1 show-up", 0, 1)]
    for k in range(1, days):
        trans.append((f"retention_{k}_{k + 1}", "retention", f"Day {k} → Day {k + 1} retention", k, k + 1))
    n = len(act)
    trans += [("stay_to_close", "stay_to_close", "Stayed to the close", days, n - 3),
              ("saw_price", "saw_price", "Saw the price (× present)", n - 3, n - 2),
              ("conversion", "conversion", "Conversion of price-viewers", n - 2, n - 1)]
    rows = []
    for key, kind, label, i, j in trans:
        if i is None:
            a_, p_ = ratio(act[j], pl[j]), 1.0
        else:
            a_, p_ = ratio(act[j], act[i]), ratio(pl[j], pl[i])
        rows.append({"key": key, "kind": kind, "label": label, "actual": a_, "plan": p_})
    # leaks: buyers lost vs plan if this stage alone had hit plan (missing data = plan, so no blame)
    base = pl[0] or 0
    def model(override=None):
        b = base
        for r in rows:
            v = r["plan"] if (r["actual"] is None or r["plan"] is None) else r["actual"]
            if override and r["key"] == override:
                v = r["plan"]
            b *= v if v is not None else 1
        return b
    now = model()
    leaks, protect = [], []
    for r in rows:
        if r["actual"] is None or r["plan"] is None:
            continue
        if r["actual"] < r["plan"]:
            fix = STAGE_FIX[r["kind"]]
            if r["kind"] == "retention":
                a_, b_ = r["key"].split("_")[1:]
                fix = fix.format(a=a_, b=b_)
            leaks.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "plan": round(r["plan"], 4),
                          "shortfall": round(1 - r["actual"] / r["plan"], 3), "buyers_lost": round(model(r["key"]) - now, 1),
                          "fix": fix})
        else:
            protect.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "plan": round(r["plan"], 4),
                            "keep": STAGE_KEEP[r["kind"]]})
    leaks.sort(key=lambda x: (-x["buyers_lost"], -x["shortfall"], x["stage"]))
    protect.sort(key=lambda x: -(x["actual"] / x["plan"] if x["plan"] else 0))
    # benchmarks
    avg = (booked / sold) if sold else data["goal"]["cash"] / data["goal"]["buyers"]
    bench_rates = launch_plan.rates_for(data["format"], days, data.get("paid_event"), avg)
    bench = []
    for r in rows:
        k = "retention" if r["kind"] == "retention" else r["kind"]
        if k not in bench_rates or k in ("registration",) or r["actual"] is None:
            continue
        b = bench_rates[k]
        lo, hi = b["cautious"], b["strong"]
        status = "below range" if r["actual"] < lo else "above range" if r["actual"] > hi else "in range"
        src = b["source"]
        bench.append({"stage": r["key"], "label": r["label"], "actual": round(r["actual"], 4), "range": [lo, hi],
                      "typical": b["typical"], "status": status,
                      "source": " / ".join(dict.fromkeys(src.values())) if isinstance(src, dict) else src})
    per_reg = None if not regs else {"cash": round(net_cash / regs, 2), "booked": round(net_booked / regs, 2)}
    by_source = {}
    for r in data["registrations"]:
        by_source[r["source"]] = by_source.get(r["source"], 0) + r["n"]
    missing = [f["stage"] for f in funnel if f["actual"] is None]
    keys = set(plan.get("source_keys") or [])
    for b in bench:
        keys |= set(b["source"].split(" / "))
    return {
        "name": data["name"], "slug": data["slug"], "format": data["format"], "days": days, "event_date": data["event_date"],
        "tz": data["tz"], "paid_event": data.get("paid_event", False), "goal": data["goal"], "plan_source": data.get("plan_source"),
        "funnel": funnel,
        "retention": [{"from": k, "to": k + 1, "actual": None if ratio(live[k], live[k - 1]) is None else round(ratio(live[k], live[k - 1]), 4),
                       "plan": None if not plan.get("day_live") else round(ratio(pl[k + 1], pl[k]), 4)} for k in range(1, days)],
        "conversion": {"of_saw_price": None if ratio(buyers, saw) is None else round(ratio(buyers, saw), 4),
                       "of_registrants": None if ratio(buyers, regs) is None else round(ratio(buyers, regs), 4),
                       "of_day1": None if ratio(buyers, live[0]) is None else round(ratio(buyers, live[0]), 4)},
        "money": {"cash": round(cash, 2), "booked": round(booked, 2), "refunded": round(refunds_amt, 2),
                  "booked_cancelled": round(cancelled, 2), "net_cash": round(net_cash, 2), "net_booked": round(net_booked, 2),
                  "average_sale": round(avg, 2) if sold else None},
        "refunds": {"count": refunds_n, "amount": round(refunds_amt, 2),
                    "rate": None if not sold else round(refunds_n / sold, 4)},
        "buyers_net": None if buyers is None else buyers - refunds_n,
        "per_registrant": per_reg,
        "goal_progress": {"buyers": None if buyers is None else round((buyers - refunds_n) / data["goal"]["buyers"], 3),
                          "cash_booked": round(net_booked / data["goal"]["cash"], 3)},
        "registrations_by_source": by_source,
        "benchmarks": bench, "leaks": leaks[:3], "all_leaks": len(leaks), "protect": protect,
        "not_logged": missing,
        "sources": {k: SOURCES[k] for k in sorted(keys) if k in SOURCES},
    }


def fnum(x):
    return "–" if x is None else f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)


def fpct(x):
    return "–" if x is None else f"{x * 100:.1f}%"


def money_s(x):
    return f"${x:,.0f}"


def report_md(r, lessons=None, heading=True):
    L = []
    if heading:
        L += [f"# {r['name']}: launch debrief", ""]
    ev = dt.date.fromisoformat(r["event_date"])
    L += [f"{r['format']} · {r['days']} day{'s' if r['days'] > 1 else ''} from {ev.strftime('%a')} {ev} ({r['tz']}) · "
          f"{'paid' if r['paid_event'] else 'free'} event · goal {r['goal']['buyers']} buyers / {money_s(r['goal']['cash'])} · "
          f"plan: {r['plan_source']}", "", "## Results", "",
          "| Stage | Actual | Plan | vs plan |", "|---|---|---|---|"]
    for f in r["funnel"]:
        L.append(f"| {f['stage']} | {fnum(f['actual'])} | {fnum(f['plan'])} | {fpct(f['vs_plan'])} |")
    m = r["money"]
    L += ["", f"- Cash collected {money_s(m['cash'])} · booked {money_s(m['booked'])} · refunded {money_s(m['refunded'])} "
              f"({r['refunds']['count']} refund{'s' if r['refunds']['count'] != 1 else ''}"
              + (f", {fpct(r['refunds']['rate'])} of buyers" if r['refunds']['rate'] is not None else "") + ")"
              + f" · net cash {money_s(m['net_cash'])} · net booked {money_s(m['net_booked'])}"]
    if r["per_registrant"]:
        L.append(f"- Revenue per registrant: {money_s(r['per_registrant']['cash'])} cash / {money_s(r['per_registrant']['booked'])} "
                 "booked (no published benchmark: compare with your own last launch)")
    c = r["conversion"]
    L.append(f"- Conversion: {fpct(c['of_saw_price'])} of price-viewers · {fpct(c['of_day1'])} of Day-1 attendees · "
             f"{fpct(c['of_registrants'])} of registrants")
    if r["retention"]:
        L.append("- Day-over-day retention: " + " · ".join(
            f"D{x['from']}→D{x['to']} {fpct(x['actual'])} (plan {fpct(x['plan'])})" for x in r["retention"]))
    gp = r["goal_progress"]
    L.append(f"- Against the goal: {fpct(gp['buyers'])} of buyers (net of refunds), {fpct(gp['cash_booked'])} of the cash goal (net booked)")
    if r["registrations_by_source"]:
        L.append("- Registrations by source: " + ", ".join(f"{k} {v:,}" for k, v in r["registrations_by_source"].items()))
    if r["not_logged"]:
        L.append(f"- Not logged yet: {', '.join(r['not_logged'])}")
    if r["benchmarks"]:
        L += ["", "| Benchmark | Actual | Range | Status | Source |", "|---|---|---|---|---|"]
        for b in r["benchmarks"]:
            f = (lambda x: f"×{x:.2f}") if b["stage"] == "saw_price" else fpct
            L.append(f"| {b['label']} | {f(b['actual'])} | {f(b['range'][0])}–{f(b['range'][1])} | {b['status']} | {b['source']} |")
    L += ["", "## Leaks", ""]
    if r["leaks"]:
        for i, x in enumerate(r["leaks"], 1):
            L.append(f"{i}. **{x['label']}**: {fpct(x['actual'])} vs plan {fpct(x['plan'])} "
                     f"(about {x['buyers_lost']:.1f} buyers lost). Fix: {x['fix']}.")
    else:
        L.append("- No stage fell short of plan (or not enough is logged yet).")
    L += ["", "## Lessons", ""]
    L += [f"- Next time: {x['fix']}." for x in r["leaks"]] + [f"- {x}" for x in (lessons or [])]
    if not r["leaks"] and not lessons:
        L.append("- (add lessons with --lesson)")
    L += ["", "## What to protect", ""]
    L += [f"- **{x['label']}** beat plan ({fpct(x['actual'])} vs {fpct(x['plan'])}): {x['keep']}." for x in r["protect"]] or \
         ["- Nothing beat plan this time: protect what attendees said was most useful (chat, survey, replies)."]
    L += ["", "## Sources", ""] + [f"- **{k}**: {v}" for k, v in r["sources"].items()]
    return "\n".join(L) + "\n"


def cmd_report(data, a):
    r = build_report(data)
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(report_md(r, data.get("lessons")), encoding="utf-8")
        r["written"] = a.md
    return r


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


def cmd_obsidian(data, a):
    v, warn = vault_check(a)
    r = build_report(data)
    stem = data["slug"] if re.match(r"\d{4}-\d{2}-", data["slug"]) else f"{data['event_date'][:7]}-{data['slug']}"
    note = v / ROOT / f"{stem}.md"
    if note.exists() and not a.force:
        refuse(f"{note} already exists; pass --force to overwrite it")
    existed = note.exists()
    fm = ["---", f"title: {yq(data['name'] + ' launch debrief')}", "type: launch", f"date: {data['event_date']}",
          f"format: {data['format']}", "tags: [launch, event]", f"status: {a.status}", "source: buildroom-event-launcher", "---", ""]
    for x in a.lesson or []:
        if x not in data.setdefault("lessons", []):
            data["lessons"].append(x)
    body = report_md(r, data.get("lessons"))
    folder = Path(a._path).resolve().parent
    try:
        folder = folder.relative_to(v.resolve())
    except ValueError:
        pass
    body = body.replace("\n## Results", f"Launch folder: `{folder}`\n\n## Results", 1)
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("\n".join(fm) + body, encoding="utf-8")
    idx = v / ROOT / "_index.md"
    line = (f"- {data['event_date']} · [[{stem}]] · {data['name']} · {data['format']} · "
            f"{fnum((r['funnel'][0] or {}).get('actual'))} registered · {fnum(r['buyers_net'])} buyers (net of refunds) · "
            f"{money_s(r['money']['net_cash'])} cash")
    text = idx.read_text(encoding="utf-8") if idx.exists() else "# Launches\n\nOne line per launch, newest last.\n\n"
    lines = text.splitlines()
    hit = [i for i, x in enumerate(lines) if f"[[{stem}]]" in x]
    if hit:
        lines[hit[0]] = line
        lines = [x for i, x in enumerate(lines) if i not in hit[1:]]
        text = "\n".join(lines) + "\n"
    else:
        text = (text if text.endswith("\n") else text + "\n") + line + "\n"
    idx.write_text(text, encoding="utf-8")
    out = {"written": str(note), "overwrote": existed, "index": str(idx), "index_line": line,
           "index_updated": "replaced" if hit else "appended"}
    if warn:
        out["warnings"] = warn
    return out


def frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm = {}
    for ln in text[3:end].strip().splitlines():
        if ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"\'') for x in v[1:-1].split(",") if x.strip()]
        elif len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fm[k.strip()] = v
    return fm, text[end + 4:]


def section(body, name):
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1).strip() if m else None


def cmd_obsidian_read(a):
    v, warn = vault_check(a)
    notes = []
    for p in sorted((v / ROOT).glob("*.md")) if (v / ROOT).is_dir() else []:
        if p.name.startswith("_"):
            continue
        fm, body = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") != "launch":
            continue
        notes.append({"file": str(p), "frontmatter": fm, "results": section(body, "Results"),
                      "lessons": section(body, "Lessons"), "protect": section(body, "What to protect")})
    notes.sort(key=lambda n: str(n["frontmatter"].get("date", "")), reverse=True)
    out = {"vault": str(v), "launches": notes, "count": len(notes)}
    if not notes:
        out["note"] = f"no launch notes under {v / ROOT}"
    if warn:
        out["warnings"] = warn
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def mk(name):
        s = sub.add_parser(name)
        s.add_argument("--file"); s.add_argument("--slug"); s.add_argument("--date"); return s
    s = mk("init"); s.add_argument("--name", required=True)
    s.add_argument("--format", required=True, choices=sorted(launch_plan.FORMATS)); s.add_argument("--days", type=int, required=True)
    s.add_argument("--tz", required=True); s.add_argument("--event-date", required=True)
    s.add_argument("--goal-buyers", type=int, required=True); s.add_argument("--goal-cash", required=True)
    s.add_argument("--plan"); s.add_argument("--paid-event", action="store_true")
    s = mk("log-reg"); s.add_argument("n", type=int); s.add_argument("--source")
    s = mk("log-day"); s.add_argument("--day", type=int, required=True); s.add_argument("--live", type=int, required=True)
    s.add_argument("--peak", type=int)
    s = mk("log-close"); s.add_argument("--present", type=int, required=True); s.add_argument("--saw-price", type=int, required=True)
    s = mk("log-sale"); s.add_argument("--tier", required=True); s.add_argument("--price", required=True)
    s.add_argument("--count", type=int, required=True); s.add_argument("--payment", choices=["full", "plan"], default="full")
    s.add_argument("--booked")
    s = mk("log-refund"); s.add_argument("--tier", required=True); s.add_argument("--count", type=int, required=True)
    s.add_argument("--amount", required=True); s.add_argument("--booked-cancelled", type=float)
    s = mk("import-csv"); s.add_argument("csv"); s.add_argument("--map", nargs="+", required=True)
    s = mk("gate"); s.add_argument("--set", nargs=2, action="append", metavar=("ITEM", "STATUS")); s.add_argument("--note")
    s = mk("report"); s.add_argument("--md")
    s = mk("obsidian"); s.add_argument("--vault", required=True); s.add_argument("--force", action="store_true")
    s.add_argument("--no-obsidian-check", action="store_true"); s.add_argument("--status", default="debriefed")
    s.add_argument("--lesson", action="append")
    s = mk("obsidian-read"); s.add_argument("--vault", required=True); s.add_argument("--no-obsidian-check", action="store_true")
    a = ap.parse_args(argv)
    today(a)                                  # a bad --date is refused before anything is read or written
    if a.cmd == "obsidian-read":
        print(json.dumps(cmd_obsidian_read(a), indent=1, ensure_ascii=False)); return 0
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
          "log-refund": cmd_log_refund, "import-csv": cmd_import_csv, "gate": cmd_gate, "report": cmd_report,
          "obsidian": cmd_obsidian}[a.cmd]
    out = fn(data, a)
    if a.cmd in ("log-reg", "log-day", "log-close", "log-sale", "log-refund", "import-csv") or (a.cmd == "gate" and a.set) \
            or (a.cmd == "obsidian" and a.lesson):
        save(path, data)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
