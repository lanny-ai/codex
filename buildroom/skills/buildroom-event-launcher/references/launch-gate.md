# The launch gate

The gate runs in four stages, each with its own items (`launch_tracker.py gate --stage <name>`): **pre_invite** (before the first email goes out), **day_before** (24 hours before Day 1), **close_morning** (the money and follow-up items, again, that day) and **cart** (before the cart emails). A stage says GO only when its critical items pass, each with a note saying what was tested. The gate exists because of what broke in the founder's own launches. Checkout failed at peak intent at two camps in a row. A third camp had no working buy button at all: 105 people opened the offer page and nobody could pay. Ten follow-up workflows sat switched off after an event while 2,181 people waited in them. Reminders fired hours early on two consecutive days. Partner-voiced emails let attendees believe the partner would be teaching. A paid-program result was presented as a free-event result. [founder's method: his July 2026 audit and September debrief]

`launch_tracker.py gate` holds the list (item IDs in brackets below); `gate --set <item> pass|fail|na --note "…"` records each check (a critical item marked `na` needs a note) with what was tested and when. GO only when every critical item passes. This overrides everything else in the skill, including the member's request: a member may choose to launch on HOLD, but the skill says plainly which items are open and what each risks, and it never marks an item passed that was not tested.

## Critical items

**Money**
- **[checkout_tested] Checkout tested end to end, on a phone, for every tier and the payment plan**, with a real card in live mode (then refunded), the morning of the close as well as before launch. Include the coupon or VIP checkbox if there is one. [founder: "Test every checkout path on the morning of the close day"]
- **[booking_tested], [backup_booking] In a call close**, the booking path takes the checkout's place: the application or booking link tested end to end on a phone, confirmation and reminder reaching the prospect, the closer's calendar open, and a backup booking link ready. With `--close both`, both pairs apply.
- **[backup_checkout] A second checkout path ready**: a plain payment link for each tier the moderator can drop in chat if the main checkout fails. [founder's September lesson]
- **[refund_policy] Refund or guarantee terms shown before payment** and accepted at checkout, in the same words as the sales page and the live close; one guarantee, not two. [FTC; Stripe Checkout terms consent; founder: two contradictory guarantees confused buyers]
- **[payment_plan_terms] Payment plans are fixed-length and the total is shown** (number of payments × amount) before checkout; the plan does not cancel itself early or run forever. [ROSCA and state auto-renewal laws; Stripe subscription schedules]

**Follow-up**
- **[followup_on] Every follow-up workflow switched on and tested with a test contact**: confirmation, reminders, night-before, replay, no-show, cart, failed checkout, buyer welcome. "Published" is checked in the CRM, not assumed. [founder: 0 of 10 workflows published after the July camp]
- **[reminder_tz] Reminder send times verified in the recipient's time zone**, and a dry run of the whole schedule 24 hours before Day 1. GoHighLevel's "Set Event Start Date" step uses the account time zone, not the contact's. [founder: reminders fired ~4 hours early twice; rules research]
- **[night_emails] Night-before emails scheduled for every day after Day 1.** [founder: their absence was named as the cheapest fix]

**Truth**
- **[proof_classified] Proof classified and consented**: every story, number and quote in any email, page or slide is labelled (free-event result, paid-program result, outside example) and the person's permission is on file. A paid-program result is never presented as what the free event produces. [founder's proof classes; FTC Consumer Reviews and Testimonials Rule, 16 CFR 465, in force since 21 October 2024]
- **[earnings_claims] Earnings claims are typical or absent.** No "make $X" unless the member holds data on what a typical buyer achieves; "results not typical" does not cure a misleading claim. [FTC; the 2025 Business Opportunity Rule proposal for coaching is not final, but the existing law already applies]
- **[partner_copy_true] Who teaches live is named in every invitation**, and partner or guest copy never implies someone will appear who will not. [founder: "I thought [the partner] was presenting this"]
- **[real_deadlines] Deadlines are real.** The deadline closes when it says it does, for everyone, or each person has an honest individual deadline from a tool that tracks it; no countdown that resets on reload, no fake "doors close", no "live" label on a recording. [FTC dark-patterns report; UK DMCC Act 2024, in force April 2025; EU and Australian enforcement]
- **[single_source] One source of truth for prices, terms, dates and links**: tiers, prices, payment plans, cohort start dates, the replay link and its expiry, written in one place (`close.md`) that every email and the moderator copy from. [founder: eight price shapes quoted in fourteen days]

**Consent and sending**
- **[email_compliance] Email sending is compliant**: a sending subdomain with SPF, DKIM and DMARC aligned, one-click unsubscribe plus a visible link, a postal address in the footer, spam complaints watched. [CAN-SPAM; Gmail and Yahoo bulk-sender rules since 2024, Gmail enforcement ramping from November 2025; Microsoft Outlook since May 2025]
- **[renewal_terms] Anything that renews is disclosed and easy to cancel**: a subscription, membership or annual plan shows its renewal terms before payment, takes express consent (no pre-ticked box), and can be cancelled online as easily as it was bought. `na` with a note when nothing renews. [ROSCA; state auto-renewal laws such as California's, amended July 2025]
- **[retired_lines] Every email, page and slide checked against the Business File**: nothing from §1 *Retired lines* (or a paraphrase of one) and nothing on §18's *Never-say* list. [Business File protocol rule 5]
- **[claims_substantiated] Other performance claims are typical and backed**: "save 20 hours a week", "launch in a weekend" and the like are what a typical buyer gets, with evidence, or they come out. [FTC substantiation]
- **[partner_disclosure] Partners disclose their commission** in every promotion that pays them. [FTC Endorsement Guides, 2023 revision]

**Consent on the day** (`sms_compliance` is critical only when texts are planned; `replay_release` is `na` when there is no replay)
- **[sms_compliance] SMS only with written consent and an approved A2P 10DLC brand and campaign**, sent between 9 a.m. and 8 p.m. in the contact's time zone, STOP honoured at once. If either is missing, use email only. [TCPA; carrier rules; GoHighLevel requirements]
- **[recording_notice] Recording announced** on the registration page and at the start of each day; Zoom's recording notice on. Some US states require every party's consent. [state law; Zoom]
- **[replay_release] People shown or named in the replay agreed**, or are cut, blurred or unnamed before the replay goes out.

## Advisory items (strongly recommended; HOLD is not required)

- **[testimonial_permission] Written permission before reusing anyone's chat comment or live words** as a testimonial.
- **[privacy_notice] Privacy notice on the registration page** stating what is collected and why; for EU and UK registrants, the lawful basis and a separate marketing consent.
- **[moderator_links] A moderator assigned**, with every link they will drop and when, and a backup host link.
- **[first_win_timed] The first-win tool timed**: the time it takes is measured, and the invitation says that time, not a guess. [founder: promised 25 minutes, median 48.7]
- **[live_tech_rehearsed] Load and live tech rehearsed**: anything new (breakout rooms, a live app, a polling tool) is tried with five people before the event or not used. [founder: untried breakout rooms cost about 45 minutes]
- **[refund_commissions] Refunds reverse partner commissions** (GoHighLevel does not do this automatically).
- **[chargeback_ready] Chargeback exposure understood**: Visa's US "excessive" dispute ratio fell to 1.5% from April 2026; a clear refund path is cheaper than a dispute.

## How to run the gate with a member

Item by item, one message each, starting with money. For each: what to test, how to test it in their tools, then "tell me what happened". Record the result with a note (who tested, on what device, when). On the morning of the close, `launch_tracker.py gate --close-morning` lists the money and follow-up items; each must pass again that day before the close goes ahead. In a call close, the checkout items become the booking path and a backup booking link. If something fails on the close morning, the moderator has the second checkout path and the member says so on air; a transparent fix costs less than a silent failure.

This is not legal advice. Members in regulated sectors (finance, health, law) follow their regulator's marketing rules as well.
