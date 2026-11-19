# Autopilot: the method

_Added 2026-11-19._

Autopilot runs Build Room sessions back to back without interviewing the member. It is only as good as what is already known, so the order matters: Deep Discovery first, then Autopilot.

## What a run covers

`scripts/autopilot.py` holds the list. Every Build Room tool is in one of four groups.

| Group | What happens | Tools |
|---|---|---|
| **Foundation** | drafted first, then reviewed by the member | Audience Insight (with web access), Ideal Client Avatar, Signature Offer, Positioning & Messaging |
| **Run** | drafted straight through after the review | Offer Deep Dive, Offer Page Copy, Funnel Map, Lead Capture, Sales Conversations, Decision Machine, Lead Gen Machine, LinkedIn Engine, Search & Answer Engine |
| **Needs you** | not run; listed with the reason and the sentence that starts it | Compass, Proof Engine, Funnel Scorecard, Weekly Ops Dashboard, Ad Studio, Video Director, Website Design Studio, Company Blueprint, SOP Creator, Hiring Ad + Interview Kit, Team Training Doc Builder, Webinar Builder, Event Launcher, AI Momentum Labs Book Builder, Speaking Engine, C-Suite Boardroom |
| **On request** | tools a member reaches for when needed | Build Room OS Navigator, Discovery Engine, Copy Engine, Brainstorm Session, Brainstorm Capture, Triage, Finish It, Build It, Agent Forge, Second Brain, Source Watcher, Continuity System |

A "needs you" tool is never run on a guess. Real numbers, a real client's permission, the member's own face, money on their accounts, and decisions about their own team are theirs.

## Sources, in order

When a session asks a question, answer it from the first of these that holds a real answer:

1. **What the member said in this run** (the decisions in Phase 1, and their review).
2. **The Business File.**
3. **The discovery ledger** (`discovery/ledger.json`): `confirmed` and `likely` findings, with their sources. `inferred` findings are guesses and are treated as drafts.
4. **The member's own files**, where the scope they agreed in Deep Discovery covers them. Do not read outside that scope. If there was no Deep Discovery, read only what the member points you to.
5. **Public pages**, where there is web access.

If none holds an answer, the answer is not known. See "When something is not known".

## Running a session without the member

For each step:

1. Start the session the normal way (its SKILL.md, then the references it tells you to read). Where subagents are available, run each session in its own subagent with a brief that names the session, the folder, the sources above and these rules; that keeps a long run from losing its place. Run them one at a time, in order, because each reads what the last one wrote.
2. Do everything the session's instructions say, with three changes:
   - **Every intake question is answered from the sources, not asked.** Keep a short list of which source answered each.
   - **Every "confirm with the member" step becomes a tag.** What the member already confirmed is `confirmed`. What came from their files or pages is `files`, with the source. What you wrote is `drafted`.
   - **The 1 to 5 rating question is skipped.** Write "not rated: autopilot" in the Session Log.
3. Save the session's full document where that session normally saves it. Put this line at the top of every document a run produces: `Draft by Autopilot on [date]. Lines marked [draft] were written for you and have not been confirmed.`
4. Mark drafted lines in the document itself with `[draft]`, and unknowns with `[needs you: what is missing]`.
5. Update the Business File sections that session owns, under the status rule below.
6. Record the step: `autopilot.py done <slug> --status drafted --outputs <files> --gaps "<what still needs them>"`.

## When something is not known

In this order:

1. **Leave it out** if the document works without it.
2. **Mark it** `[needs you: ...]` if the document needs it. A page with three marked blanks is useful. A page with three invented facts is harmful.
3. **Draft it and tag it** only for things that are judgement, not fact: a name for the avatar, a tagline, a positioning statement, the wording of a pitch. These are `drafted`.
4. **Block the step** if the session cannot produce anything honest without it: `--status blocked --note "<what is missing>"`. Then go on to the next step.

Never draft these. They are facts, and a wrong one does damage:

- prices, numbers, dates, counts and percentages
- client names, quotes, testimonials and results
- credentials, awards, press and years of experience
- guarantees and their terms
- anything that reads as a promise of an outcome

A client quote is only ever a real quote with its source. Words you imagine a client might say go in the Business File's **Hypothesis language**, never **Sourced language**, and never inside quotation marks in a draft.

## The review

After the foundation and before anything else, the member sees the Foundation Reveal and decides. `references/foundation-reveal.md` covers the page. The rules:

- Nothing in Phase 4 starts until `autopilot.py approve` has recorded the member's own words.
- "Looks fine, keep going" is a go-ahead. Silence, or your own judgement that it is good, is not.
- Every change they give is applied in their words and becomes `confirmed`.
- If they change who the client is, what the offer is, or the price, rerun the foundation sessions that depend on it before going on.

## Status rule for the Business File

- A section is `complete` only when every line in it is confirmed by the member or came from their own files and they reviewed it, and no drafted line remains.
- Otherwise it is `provisional`, by `Autopilot ([session name])`.
- Sections written in Phase 4 are always `provisional`. The member has not reviewed them.
- Content that was already in the file is kept. Fill gaps; do not rewrite a section the member built, unless they asked for it to be redone.
- Retired lines in §1 are never used, in any draft.

## What a run never does

- Publish a page, send an email, post, schedule, or connect an account.
- Spend money or generate paid media.
- Read files outside the scope the member agreed.
- Ask the member a question in Phase 2 or Phase 4.
- Promise a result, in its own voice or in a draft.

## If the run stops

`autopilot/run.json` is written after every step. "Run autopilot" in a new session reads it and carries on from the next step. Never start a second run over an unfinished one. If the member wants a fresh run, they move the `autopilot` folder aside first, and you say what that discards.

## The report

`autopilot.py report` lists what was drafted and where it is saved, what each draft still needs from the member, what could not be drafted and why, what was left out, and every "needs you" tool with its reason and the sentence that starts it. It ends with what to do first. Give the member the report as it is. Do not summarise it into something more flattering.
