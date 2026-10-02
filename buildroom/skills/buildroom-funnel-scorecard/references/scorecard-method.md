# Scorecard Method — tables, formulas, routing, and the routine prompt

Everything the session produces, in the shape it produces it. Design choices not stated by the founder are marked *(design choice)*.

## 1. The stage table

One row per failure point, in funnel order, read from the §6 funnel map. The conversion event from §6 is the last row that matters; anything after it (onboarded, retained, referred) is optional.

| # | Stage (failure point) | Gate (what the person must do) | Entered | Converted to next | Rate | Prior window | Change | Source |
|---|---|---|---|---|---|---|---|---|

Rules: a number that cannot be read from a source stays blank and is marked `UNREAD`; never estimated. Entered and converted are counts for the window; the rate is converted divided by entered. "Prior window" is the same window one period earlier. The source column names where the number came from (pipeline stage name, report, field) so the routine can read it next time.

If stages don't exist in the CRM yet, the first deliverable is the **pipeline to create**: one stage per failure point with the exact name, in order, and the tag or trigger that moves a contact into it. Nothing else can be measured until that exists.

## 2. The leak definition and ranking *(design choice)*

A leak is any stage whose rate fell against the prior window, or whose rate is the lowest in the table when there is no prior window.

Revenue at risk for a stage = (prior rate − current rate) × entered × value of one conversion downstream. Value downstream = the §3 investment × the product of the conversion rates between this stage and the conversion event. With no prior window, use (best plausible rate for this gate − current rate) and label the number provisional.

Rank leaks by revenue at risk. Report the top three. A stage with `UNREAD` counts is reported as "unmeasured", ranked above everything else, with the fix "install the measurement".

## 3. Fix taxonomy and routing

Every leak gets two or three proposed fixes, each tagged with a category and routed to the Build Room session or campaign that owns it. Never box in the fix space; include at least one fix outside the obvious category.

| Category | Looks like | Owned by |
|---|---|---|
| Automation | a touch, reminder, or campaign at the failure point; a missing campaign | Decision Machine (§16 campaign on this conversion point) |
| Messaging | the belief the stage asks the person to hold isn't installed; the page, email, or script says the wrong thing | Decision Machine (belief map), Offer Page Copy (§5), Lead Capture (§7), Sales Conversations (§15) |
| Offer | the gate asks for more than the value shown so far; price, guarantee, urgency | Offer Deep Dive (§3) |
| UX | friction at the gate: form length, page speed, confusing step, broken link | Lead Capture build steps; the launch test |
| Training | a human stage (call, proposal, onboarding) converting below its script | Sales Conversations (§15), Training Docs (§11) |
| Traffic fit | the stage converts fine, the people entering are the wrong people | Audience Insight (§2), Lead Gen Machine (§14) |

Each fix is written as: what changes · where (campaign, page, step) · expected effect on the stage rate · effort (one of: one message, one page, one session) · approve / skip / edit.

## 4. The "what moved" line

One line per run: contacts that moved to a later stage this window, revenue recorded this window, and the lead follow-up check: every lead that entered this window has had at least one touch, yes or no, with the count of untouched leads.

## 5. The Funnel Scorecard document

```
FUNNEL SCORECARD — [business] — window [dates] — run [date]
Couldn't read this run: [stages/sources, or "nothing"]

WHAT MOVED: [n] moved forward · $[x] recorded · untouched leads: [n]

STAGE TABLE
[table from §1]

TOP LEAKS (ranked by revenue at risk, a design choice)
1. [stage] — rate [x]% (was [y]%) — $[z] at risk
   Fix A (category) … approve / skip / edit
   Fix B (category) …
   Fix C (category) …
2. …
3. …

APPROVED THIS RUN: [list, or none]
FEEDBACK FOR NEXT RUN: [the member's corrections, verbatim]
```

Approved fixes become §13 rows. Nothing is applied to the live account by this document; the build happens through the owning session or a gated snapshot the member approves.

## 6. The routine prompt (created only on an explicit yes)

```
You are the Funnel Scorecard routine for [business]. Run every [cadence] at [time].

Read: BUILDROOM_BUSINESS_FILE.md (§6 stages and baseline, §3 investment, §16 campaign map, §13 open fixes); then the stage counts and revenue from [sources, by name], for the window [last N days]. Use the API; use the browser only if the API cannot read a number.

Never estimate. A stage you cannot read is UNREAD and goes at the top of the report.

Produce the Funnel Scorecard in the fixed format (stage table, what moved, top three leaks with two or three fixes each, routed to their owning campaign or session). Rank leaks by revenue at risk. Do not apply any fix. Do not change any goal. Do not send anything to a contact.

Deliver to [where]. If a run finds nothing to read, say so loudly; a silent run is a failure. Notify [who] when: an untouched lead is older than [n] days; revenue in the window is zero; a stage rate fell by more than [x] points.

Carry forward the FEEDBACK FOR NEXT RUN section from the previous scorecard and apply it.
```

Setup lines to give the member: where the recurring task is created in their tool, the cadence, the connectors it needs (CRM API, payment processor), where it writes, how to pause or delete it, and the model to use (the strongest available for this task).
