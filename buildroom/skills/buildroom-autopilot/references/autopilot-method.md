# Autopilot: the method

_Added 2026-11-19. Revised 2026-11-21 after three trial runs._

Autopilot runs Build Room sessions back to back without interviewing the member. It is only as good as what is already known, so the order matters: Deep Discovery first, then Autopilot. On a thin file a run mostly hands the member's own few sentences back in different shapes. Say that before the run, not after.

## What a run covers

`scripts/autopilot.py` holds the list. Every Build Room tool is in one of four groups.

| Group | What happens | Tools |
|---|---|---|
| **Foundation** | drafted first, then reviewed by the member | Audience Insight (with web access), Ideal Client Avatar, Signature Offer, Positioning & Messaging |
| **Run** | drafted straight through after the review | Offer Page Copy, Funnel Map, Lead Capture, Sales Conversations, Decision Machine, Lead Gen Machine |
| **Needs you** | not run; listed with the reason and the sentence that starts it | Offer Deep Dive, LinkedIn Engine, Search & Answer Engine, Compass, Proof Engine, Funnel Scorecard, Weekly Ops Dashboard, Ad Studio, Video Director, Website Design Studio, Company Blueprint, SOP Creator, Hiring Ad + Interview Kit, Team Training Doc Builder, Webinar Builder, Event Launcher, AI Momentum Labs Book Builder, Speaking Engine, C-Suite Boardroom |
| **On request** | tools a member reaches for when needed | Build Room OS Navigator, Discovery Engine, Copy Engine, Brainstorm Session, Brainstorm Capture, Triage, Finish It, Build It, Agent Forge, Second Brain, Source Watcher, Continuity System |

A "needs you" tool is never run on a guess. Real numbers, a real client's permission, the member's own face, money on their accounts, and decisions about their own team are theirs. Offer Deep Dive, LinkedIn and Search were tried in a run and came back half blank, so they are the member's to start.

## The never-draft list wins

A session's own instructions were written for a session with the member in the room. Some of them ask for things a run must not make up. **Where a session asks for anything on this list, the list wins: leave that part out and mark the gap.**

Never draft:

- prices, dollar values, price tiers, anchors, cost or return math
- numbers, dates, counts, percentages and timeframes
- client names, quotes, testimonials, results, "typical" results and composite stories
- words written "as if you had interviewed" clients, or "realistic" testimonial fragments
- credentials, awards, press, years of experience
- guarantees and their terms
- scores and ratings presented as findings
- anything that reads as a promise of an outcome

A client quote is only ever a real quote with its source. Words you imagine a client might say go in the Business File's **Hypothesis language**, never **Sourced language**, and never inside quotation marks in a draft.

`autopilot.py next` prints the **scope** for each session: what a run drafts there and what it leaves alone. Follow it. It also prints the member's **standing rules** (what they refuse to claim, lines never to use, the guarantee wording). Give those to every session and every subagent, word for word.

Stock material that does not fit the member is dropped, not adapted: an objection list written for business buyers is no use to a doula's clients.

## Sources, in order

When a session asks a question, answer it from the first of these that holds a real answer:

1. **What the member said in this run** (the Phase 1 decisions, and their review).
2. **The Business File.**
3. **The discovery ledger** (`discovery/ledger.json`): the member's own word, what two sources agree on, and their own current files once `files_current` is set. Not findings marked `stale`, `retired` or `inferred`, and not one side of a disagreement the member has not settled.
4. **The member's own files**, where the scope they agreed in Deep Discovery covers them. Do not read outside that scope. If there was no Deep Discovery, read only what the member points you to.
5. **Public pages**, where there is web access.

If none holds an answer, the answer is not known.

**Proof.** A client's words or result goes into anything a stranger could read only when permission is recorded as yes, in `discovery/Proof_Found.md` or the Business File. Otherwise the draft carries `[needs you: a result you have permission to use]`. Someone who asked not to be named is never named, anywhere.

## Running a session without the member

For each step `autopilot.py next` gives:

1. Start the session the normal way: its SKILL.md, then its prompt system. Read its other references only when the scope needs them. Where subagents are available, run each session in its own subagent with a brief that names the session, the folder, the scope, the standing rules, the sources above and these rules. Run them one at a time, in order, because each reads what the last one wrote.
2. Do what the session's instructions say, inside the scope, with these changes:
   - **Every intake question is answered from the sources, not asked.**
   - **Every "confirm with the member" step becomes a tag.** Their own word is confirmed. What came from their files or pages names the file or page. What you wrote is a draft.
   - **The never-draft list wins** over the session's prompts.
   - **The 1 to 5 rating question is skipped.**
   - **Nothing is built, published, sent or connected.** A session that ends in a CRM build or a page going live stops at the copy.
3. Save every document under `autopilot/drafts/`, named `NN_Session_Name.md` in run order. Nothing a run writes goes anywhere else, so a draft is never mistaken for the member's own file.
4. Start every document with: `Draft by Autopilot on [date]. Nothing here is published. Check it before you use it.` Then a short list, **What this draft still needs from you**. Then the draft.
5. In the draft itself:
   - an unknown is written where it belongs as `[needs you: what is missing]`;
   - a fact is used exactly as the member gave it, and listed at the end under **Facts used and where each came from**;
   - copy (a page, an email, a script) is written clean, without a tag on every sentence. It is all a draft; the line at the top says so. Tag a sentence only when it could be read as a fact about the member or their clients that nobody confirmed, and prefer cutting such a sentence to tagging it.
6. Record the step:
   - `--status drafted` when the session's main output is there and usable after an edit;
   - `--status partial` when a real part of it could not be drafted. Say what was and was not, in `--note`;
   - `--status blocked` when nothing honest could be produced. Say what is missing.
   - List what the draft still needs in `--gaps`, each as a short plain line. Word the same gap the same way every time (`A booking link`), so the report can add them up.

## When something is not known

In this order:

1. **Leave it out** if the document works without it.
2. **Mark it** `[needs you: ...]` if the document needs it. A page with three marked blanks is useful. A page with three invented facts is harmful.
3. **Draft it** only when it is judgement, not fact: a name for the avatar, a tagline, a positioning statement, the wording of a pitch.
4. **Record the step as partial or blocked** when most of the session's inputs are unknown. An honest "this could not be drafted" is a better result than a document of blanks listed as drafted.

For the three foundation sessions: if the avatar has no confirmed or file-based profile, or the offer has no confirmed promise or core result to restate, stop and tell the member what is missing. Do not go around it.

## The review

After the foundation and before anything else, the member sees the Foundation Reveal and decides. `references/foundation-reveal.md` covers the page. The rules:

- Nothing in Phase 4 starts until `autopilot.py approve` has recorded the member's own words.
- "Go ahead: yes" on the review, or "looks fine, keep going", is a go-ahead. Silence, or your own judgement that it is good, is not. "Looks right" on all three parts with no go-ahead means show them the page again.
- A line they change becomes theirs: apply it in their words and tag it confirmed.
- A part they mark "Looks right" changes its drafted lines to **reviewed**: a draft they approved as it stands. It is not their own words, so it never becomes confirmed, and later sessions still treat it as a draft that may be reworded.
- A change that says what **not** to say is recorded with `autopilot.py decide --key never_claim` (or `retired`), so every later session carries it.
- If they change who the client is, what the offer is, or the price, rerun the foundation sessions that depend on it, rebuild the page and show it again before recording a go-ahead.

## What a run writes into the Business File

The protocol says only member-confirmed content goes into the file. An Autopilot run is the one stated exception, and it is a narrow one.

- **Before the review:** nothing.
- **After the member approves the foundation:** §2, §3 and §4, from `foundation.json`. Every line that is not the member's own word carries its tag in the file: `[file: path]`, `[reviewed draft]` or `[draft]`. A later session that reads the file treats a tagged line as a starting point, never as a fact.
- **In Phase 4:** for each session, only the name of its document under `autopilot/drafts/` and the status. No drafted copy, no drafted fields.
- **Status:** every section a run touches is `provisional`, by `Autopilot`. A run never marks a section `complete`. The owning session does, or the member does.
- **§1:** a decision from Phase 1 fills an empty §1 field (price, tools, lead source). "None" is never written into Retired lines; when there are none, leave that line as it is.
- **§8:** one row for the whole run, with the readiness number, the sessions drafted and "not rated: autopilot".
- Content that was already in the file is kept. Fill gaps; do not rewrite a section the member built, unless they asked for it to be redone.
- Retired lines in §1 are never used, in any draft.
- Where you can write files, update the file in place and tell the member what changed. Do not print the whole file into the chat.

## What a run never does

- Publish a page, send an email, post, schedule, or connect an account.
- Spend money or generate paid media.
- Read files outside the scope the member agreed.
- Ask the member a question in Phase 2 or Phase 4.
- Promise a result, in its own voice or in a draft.

## If the run stops

`autopilot/run.json` is written after every step. "Run autopilot" in a new session reads it and carries on from the next step. Never start a second run over an unfinished one. If the member wants a fresh run, they move the `autopilot` folder aside first, and you say what that discards.

## The handover

Two things, both made by script from `run.json`:

- `autopilot.py report`: what was drafted and where it is saved, what was only partly drafted, what could not be drafted and why, what the member told you at the start, and every "needs you" tool with the sentence that starts it. It opens with **What to do first**: the gaps that come up in more than one draft, which are the few answers that improve the most.
- `handover.py build`: the same, as the **Your Build** page, with a link to each document and a checklist the member can tick.

Give the member both as they are. Do not summarise them into something more flattering.
