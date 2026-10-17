# Test run — Funnel Scorecard + Leak Finder (dry run, 2026-10-02)

**Member simulated:** AI Momentum Labs (the founder's own business), using the real Business File from the vault (version 1.6, §6 written by the Funnel Map session on 2026-08-26, status provisional) and the GHL build spec that session produced.

**What this run could and couldn't do.** No GoHighLevel access exists in the environment that ran this; the private integration key lives in the founder's `.env` on his machine, where it belongs. So Phases 0, 1 and 3 ran in full on the file, Phase 2 produced the table with every count `UNREAD`, and Phase 4 produced the routine prompt without creating anything. The live pull is one paste on the founder's machine (section 7).

## 1. Phase 0 — intake from the file

- Funnel type: application funnel; single conversion event: **booked install call**.
- Map (§6): warm source (tagged) → offer page → booking page → thank-you → reminders → call → same-hour payment link → Pre-Flight; non-bookers → 5-email sequence; "thinking" → 3-email sequence; no-show → rebook flow.
- Drop-off hypothesis (§6): the decision stage, warm leads and prepared intakes going silent (documented 25-day stalls, an unsent payment link). Parallel ops leak: access-delivery failures churning paying customers.
- Baseline metrics (§6): booking rate, show-up rate, close rate all **unknown**, recorded honestly.
- Investment (§3): $10,000 core offer.
- CRM: GoHighLevel. Two accounts named by the founder: the AI Momentum Labs sub-account and the "Lanny at AI Momentum Labs" account. **One scorecard per location.** The Install Pipeline and the Babysitting Test funnel are specified for one location; the second account gets its own scorecard only if it has its own pipeline, otherwise it is a traffic source into the first.
- Window: last 7 days. Cadence: weekly (the founder's four-hourly cadence is his volume, not the default).

## 2. Phase 1 — stages as failure points

The §6 map mapped onto the spec's Install Pipeline (New Lead → Call Booked → Showed → Committed → Paid → Onboarding → Live), with the gate each stage asks the person to pass and where the count lives:

| # | Stage | Gate | Source |
|---|---|---|---|
| 1 | Warm source | submits the Babysitting Test / lands on the offer page | tag `warm-lead`, `src-*` |
| 2 | New Lead | books the install call | pipeline stage New Lead; tag `status-new-lead`; Install Call Sequence membership |
| 3 | Call Booked | shows up | pipeline stage Call Booked; calendar "Install Call" bookings; tag `install-call-booked` |
| 4 | Showed | commits | pipeline stage Showed; calendar status showed / no-show |
| 5 | Committed | pays | pipeline stage Committed (manual move) |
| 6 | Paid | onboarded (Pre-Flight booked, access delivered) | tag `client-paid`; payment record |
| 7 | Onboarding → Live | live | pipeline stages Onboarding, Live |

Three failure points in the map have no pipeline stage of their own and are read from tags, sequence membership, or calendar status: non-bookers (inside New Lead), "thinking" (between Showed and Committed, the 3-email sequence, not yet built per the spec), and no-shows (Call Booked minus Showed). That is normal and the method now says so.

## 3. Phase 2 — the scorecard

Every count is `UNREAD` in this run. The table above is the shape; the first live run fills it.

**What moved:** UNREAD. **Untouched leads:** UNREAD.

## 4. Phase 3 — the leaks (ranked, with the unmeasured rule applied)

**Leak 1 (outranks everything): the funnel is unmeasured.** §6 says every baseline is unknown, six weeks after the pipeline was specified.
- Fix A (automation): confirm the Install Pipeline exists in the sub-account with all seven stages and that WF-1 to WF-3 move opportunities between them; if not, create it from the spec. Owner: founder. Effort: one session.
- Fix B (UX): run the spec's five-step launch test so stage moves are proven, not assumed. Effort: one page.
- Fix C (automation): add a stage or tag for "thinking" so the biggest hypothesised leak can be counted at all. Owner: Decision Machine (§16). Effort: one message.

**Leak 2 (the §6 hypothesis): Showed → Committed, the decision stage.** Revenue at risk cannot be computed without counts; one lost committed prospect is one $10,000 investment, stated as illustration only.
- Fix A (automation): WF-3's same-hour payment link, verified by launch-test step 4; the documented unsent link is exactly this failure. Owner: Decision Machine campaign on Committed → Paid.
- Fix B (messaging): the 3-email "think about it" sequence (WF-4) is still "next week" in the spec. Build it. Owner: Decision Machine.
- Fix C (training): no install call ends without a next step booked on the call. Owner: Sales Conversations (§15).

**Leak 3 (the parallel ops leak): Paid → Onboarding, access-delivery failures.**
- Fix A (automation): WF-3 step 2's verified access delivery plus the 24-hour access check. Owner: Decision Machine.
- Fix B (UX): the 48-hour nudge and the 5-day personal-task reminder, as specified. Owner: Decision Machine.
- Fix C (training): an access-delivery SOP with an owner, so the failure has a name. Owner: SOP Creator (§9).

Approvals: none recorded; the founder was not present. Each fix stays approve / skip / edit.

## 5. Phase 4 — the routine (shown, not created)

Not created: no explicit yes, and no access to create it from here. The prompt, pre-filled:

```
You are the Funnel Scorecard routine for AI Momentum Labs. Run every Monday at 07:00.

Read: BUILDROOM_BUSINESS_FILE.md (§6 stages and baseline, §3 investment, §16 campaign map, §13 open fixes); then, for the AI Momentum Labs sub-account, the last 7 days of: Install Pipeline opportunities by stage; contacts tagged warm-lead, status-new-lead, install-call-booked, client-paid; Install Call calendar appointments with status (booked, showed, no-show); payments recorded. Use the GoHighLevel private integration key from .env; use the browser only if the API cannot read a number.

Never estimate. A stage you cannot read is UNREAD and goes at the top of the report.

Produce the Funnel Scorecard in the fixed format (stage table, what moved, top three leaks with two or three fixes each, routed to their owning campaign or session). Rank leaks by revenue at risk. Do not apply any fix. Do not change any goal. Do not send anything to a contact.

Deliver to feedback/funnel-scorecard/YYYY-MM-DD.md in the vault and add the top leak as one line under Today in Command Center.md. If a run finds nothing to read, say so loudly; a silent run is a failure. Notify the founder when: an untouched lead is older than 2 days; revenue in the window is zero; a stage rate fell by more than 10 points.

Carry forward the FEEDBACK FOR NEXT RUN section from the previous scorecard and apply it.
```

## 6. What this test proved, and what it didn't

**Proved.** The skill derives a correct stage table from a real §6 and a real build spec without inventing stages; the unmeasured-first rule fires when baselines are unknown and produces the right first fix; every leak's fixes resolve to an owning Build Room session or Decision Machine campaign; the "stages live in three places" case (tags, calendar, sequence) is handled; the two-account question has a rule.

**Not proved.** Live reads through the GHL API, the prior-window change, revenue at risk with real counts, the "what moved" line, the routine's fail-loud behaviour on a real schedule.

**Two findings applied to the skill.** A stage may be a pipeline stage, a tag, a calendar status, a sequence membership, or a payment event, with the source named per stage. One scorecard per CRM location; the intake asks which location first.

## 7. The live run, one paste

In Claude Code or Codex, opened on the vault folder, with the GHL private integration key in `.env`:

> Run the Funnel Scorecard for AI Momentum Labs on the Install Pipeline in the AI Momentum Labs sub-account, window last 7 days. Read every stage from the API; never estimate; mark anything unreadable UNREAD. Then check whether the "Lanny at AI Momentum Labs" account has its own pipeline; if it does, run a second scorecard for it, otherwise report it as a traffic source into the first. Save both under feedback/funnel-scorecard/. Do not apply any fix and do not create the routine; show me the routine and ask.
