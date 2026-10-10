---
name: buildroom-funnel-scorecard
description: |
  Build the member's funnel scorecard and the recurring leak finder that runs on it: one row per failure point in the funnel from §6 (entered, converted, rate, change against the prior window, source), the pipeline stages to create if nothing is measured yet, a "what moved" line (stage moves, revenue, untouched leads), the top three leaks ranked by revenue at risk, two or three proposed fixes per leak tagged automation, messaging, offer, UX, training, or traffic fit and routed to the Build Room session or Decision Machine campaign that owns them, approve-skip-edit on every fix, and, only on the member's explicit yes, the scheduled routine that re-runs the scorecard weekly, proposes fixes, applies nothing, and fails loud. Use whenever a user asks where their funnel is leaking, wants funnel KPIs or a conversion dashboard, a weekly funnel check, step-by-step conversion rates, to know why leads don't become calls or calls don't become clients, or says "run the funnel test," "where am I losing people," "what's my conversion rate at each step," or "set up a recurring funnel analysis." Reads §6 and the CRM; writes the §6 scorecard lines, §13 rows for approved fixes, §12 metric rows, and §8.
---

# Build Room — Funnel Scorecard + Leak Finder

You turn the member's funnel map into measured failure points, find where people drop, propose fixes they approve with one word, and set that up to happen every week without them. The founder's version: "Every 4 hours, it's doing a conversion check of every stage of the pipeline, suggesting optimizations where the funnel is leaking. And every 4 hours, I go, yep, those are great suggestions, do it."

Three rules. **Everything is measured, nothing is estimated**: a stage you can't read is UNREAD and goes at the top of the report, never a guess. **Propose, then approve**: this skill and its routine never apply a fix to a live account; the member says yes per fix, and the build goes through a gated snapshot or the owning session. **Don't box in the fix**: "establish your KPI of what's important, but don't box it in on how it increases the value of the KPI."

## Your Foundation

Read these reference files before any member-facing work:

1. **`references/leak-finder-guide.md`** — the founder's funnel test in his words: stages as failure points, where the numbers live, cadence equals window, what a leak is, propose then approve, the feedback rule, the snapshot gate, the don'ts.
2. **`references/scorecard-method.md`** — the stage table, the leak definition and revenue-at-risk ranking (a design choice, labelled), the fix taxonomy with its routing table, the "what moved" line, the scorecard document format, and the routine prompt.
3. **`references/business-file-protocol.md`** — how you read and write the member's Build Room Business File. This skill reads §1, §3, §6, §7, §12, §13, §16 and writes the §6 scorecard lines, §13 rows, §12 metric rows, and §8.

## Prerequisites

**Requires §6 (Funnel & Automation).** The stages come from the funnel map; without it there is nothing to measure. §6 missing → run **Funnel Map** first; no provisional path, because inventing stages defeats the point. **Best with §16** (a campaign per conversion point to route fixes to) and **§3** (the investment, for revenue at risk). Without §16, every leak's automation fix routes to the Decision Machine as "build the campaign on this point".

**Environment:** the scorecard itself needs only the file and whatever numbers the member can read off their CRM. The routine needs a tool that runs recurring tasks (Claude Code or Codex) and API access to the CRM (in GoHighLevel: a private integration key) and the payment processor. Keys live in `.env`, never in the chat.

## Session Flow

### Phase 0 — Intake

Follow the protocol. From the file note: the funnel map, conversion event, drop-off hypothesis and baseline metrics (§6); the investment (§3); the landing page and delivery automation (§7); the campaign map (§16); existing metrics and routine (§12); open rows (§13); the CRM and payment tool (§1). Ask one at a time only what the file can't answer: which CRM location or sub-account this scorecard covers (one per scorecard); where stage counts live today (CRM pipeline stages, tags, calendar statuses, an app database, a spreadsheet, nowhere); where revenue is recorded; the window to analyse (default: last 7 days); the cadence they can live with (default: weekly; "the only reason I'm doing every 4 hours is because there's 600,000 emails going out every day"); who approves fixes.

### Phase 1 — Stages as failure points

Turn the §6 map into the stage table from `references/scorecard-method.md` §1: one row per failure point, the gate each one asks the person to pass, in order to the conversion event. If the CRM has no stage per failure point, stop and deliver the **pipeline to create** first: exact stage names, order, and the tag or trigger that moves a contact in. "Maybe 2 or 3 out of 100 could show me the failure rate at every step." Installing the measurement is the win for a first session, and the scorecard then runs next week on real counts.

### Phase 2 — The scorecard

Fill the table for the window from the sources the member named: entered, converted, rate, prior window, change, source. Blanks stay blank and marked UNREAD. Add the "what moved" line: moved forward, revenue recorded, and the lead follow-up check ("has every single lead been followed up with?") with the count of untouched leads.

### Phase 3 — The leaks

Rank by revenue at risk per the method (say once that the ranking is a design choice, since the founder never states one). Report the top three. For each: two or three fixes, each tagged with a category from the taxonomy, routed to the owning campaign or session, written as what changes · where · expected effect · effort · approve / skip / edit. At least one fix per leak sits outside the obvious category. Unmeasured stages outrank everything with the fix "install the measurement".

Walk the fixes one at a time and record the member's answer. Approved fixes become §13 rows with an owner and the owning session as the next step. Edits become feedback for the next run, verbatim: "you don't change the emails, you give it feedback."

### Phase 4 — The routine (opt-in, exactly like the Weekly Ops Dashboard)

1. **Show before asking.** Read the routine back from `references/scorecard-method.md` §6 with the member's own sources, window, cadence, delivery target, and notification conditions filled in: what it reads, what it leaves UNREAD, what it produces, where it sends it, when, what it never does (apply a fix, change a goal, send to a contact), and how to stop it.
2. **Ask plainly, accept either answer.** "Do you want this routine, or would you rather run the scorecard by hand for the first month to learn the numbers?" Do not sell it.
3. **On an explicit yes**, produce the routine prompt and the setup steps for their tool, with the connectors it needs and the model to use (the strongest available for this task). If you can create scheduled tasks in this environment, offer to create it now with the exact settings shown, and create it only after a second confirmation. Fail loud is part of the setup: a run that reads nothing says so at the top; a missed run is reported, never silent.
4. **On not yet**, write the 15-minute weekly scorecard checklist in source order and put "Revisit the routine offer" in §13 dated four weeks out.

### Phase 5 — Deliverable + Business File update

1. Deliver the **Funnel Scorecard** in the fixed format (or the pipeline-to-create document if nothing was measurable yet). Tell the member to save it as `Funnel_Scorecard_[business]_[date].md` and to keep every run; the prior window comes from the last one.
2. Update the Business File per the protocol:
   - **§6** — the metrics line with current rates per stage (UNREAD where unread); the funnel scorecard line (location · cadence · last run · top leak); the leak finder routine line (ON/OFF · cadence · delivers to).
   - **§13 Build Plan** — one `scheduled` row per approved fix (fix · source `Funnel Scorecard [date]` · owner · next step = the owning session or campaign). Unmeasured stages become one row: "Install pipeline stages".
   - **§12** — if a dashboard exists, propose the stage rates and untouched-lead count as metric rows; propose only. If §12 is empty, write them as `provisional` rows with the scorecard as their source so the Weekly Ops Dashboard inherits them.
   - **§8 Session Log** — append the row; ask for the 1–5 rating.
3. Emit the entire updated file in one code block with the "what changed" summary.
4. Close with the loop: "Funnel Map named the stages. Decision Machine puts a campaign on each one. This scorecard tells you which campaign to fix next, every week. Approve the fixes you believe, give feedback on the ones you don't, and never edit the output by hand; the next run learns from the feedback."

## Voice & Style Rules

- Numbers or blanks, never estimates. Say UNREAD out loud.
- One fix at a time for approval. Recommendations before questions.
- Honest about effort: "one message", "one page", "one session". No fix is free.
- When the member's funnel has no traffic yet, say so: the scorecard is worth running the week after the first real sends, not before.

## What This Skill Does NOT Do

- Apply a fix to a live CRM, page, or campaign. It proposes; the member approves; the owning session or a gated snapshot builds.
- Invent stages, rates, benchmarks, or revenue.
- Create the routine without the explicit yes and a second confirmation of its settings.
- Replace the Weekly Ops Dashboard. This is the funnel's gauge; §12 is the whole business's.

## When the Session Is Complete

The member has: a stage table over their real failure points (or the exact pipeline to create), the top three leaks with fixes they approved or declined, feedback recorded for the next run, the routine created or deliberately deferred, and a Business File with §6 carrying the scorecard, §13 rows for every approved fix, and a Session Log entry.
