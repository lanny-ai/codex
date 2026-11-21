# Autopilot: the method

_Added 2026-11-19. Revised 2026-11-21 after two rounds of trial runs._

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
- imagined scenes from a client's life (a typical Tuesday, what they think at 11pm, how long they have been in pain)
- credentials, awards, press, years of experience
- guarantees and their terms
- scores and ratings presented as findings
- anything that reads as a promise of an outcome. One stated exception: the offer's promise line may restate the core result the member gave, in plain words, with no number and no timeframe

A client quote is only ever a real quote with its source. Words you imagine a client might say go in the Business File's **Hypothesis language**, never **Sourced language**, and never inside quotation marks in a draft.

`autopilot.py next` prints the **scope** for each session: what a run drafts there and what it leaves alone. Follow it. It also prints the member's **standing rules** (what they refuse to claim, lines never to use, the guarantee wording). Give those to every session and every subagent, word for word. It also prints, as `KNOWN` lines, everything else the member told you at the start (price, booking, tools, free resource, where they want clients from), so no session leaves a blank for something already answered.

Stock material that does not fit the member is dropped, not adapted: an objection list written for business buyers is no use to a doula's clients.

## Sources, in order

When a session asks a question, answer it from the first of these that holds a real answer:

1. **What the member said in this run** (the Phase 1 decisions, and their review).
2. **The Business File.**
3. **The discovery ledger** (`discovery/ledger.json`): the member's own word, what two sources agree on, and their own current files once `files_current` is set. Not findings marked `stale`, `retired` or `inferred`, and not one side of a disagreement the member has not settled.
4. **The member's own files**, where the scope they agreed in Deep Discovery covers them. Do not read outside that scope. If there was no Deep Discovery, read only what the member points you to.
5. **Public pages**, where there is web access.

If none holds an answer, the answer is not known.

**Proof.** A client's words or result goes into anything a stranger could read only when permission is recorded as yes, in `discovery/Proof_Found.md` or the Business File. A public review is not a yes: a draft may point to where the reviews are, and may not reproduce one. Otherwise the draft carries `[needs you: a result you have permission to use]`. Someone who asked not to be named is never named, anywhere.

## Running a session without the member

For each step `autopilot.py next` gives:

1. Load only what the step needs. In a run this replaces a session's own "read everything first" instruction: read its SKILL.md and the one file that holds its prompts (`prompt-system.md` where there is one; where there is none, the SKILL.md's own flow; for Lead Gen, the one module file the scope names). Open `knowledge-base.md` or another reference only for the part being drafted. Where subagents are available, run each session in its own subagent with a brief that names the session, the folder, the scope, the standing rules, the sources above and these rules. Run them one at a time, in order, because each reads what the last one wrote.
2. Do what the session's instructions say, inside the scope, with these changes:
   - **Every intake question is answered from the sources, not asked.**
   - **Every "confirm with the member" step becomes a tag.** Their own word is confirmed. What came from their files or pages names the file or page. What you wrote is a draft.
   - **The never-draft list wins** over the session's prompts.
   - **A session rule that waits for the member** ("never proceed on an unconfirmed belief", "one message at a time, then stop") becomes a marked gap, and the session carries on.
   - **The 1 to 5 rating question is skipped.**
   - **Nothing is built, published, sent or connected.** A session that ends in a CRM build or a page going live stops at the copy.
3. Save every document under `autopilot/drafts/`, named `NN_Session_Name.md` in run order. NN counts the steps that produced a document, starting at 01; a skipped step takes no number. Nothing a run writes goes anywhere else, so a draft is never mistaken for the member's own file.
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

For the three foundation sessions, the test is what the sources hold, not how the draft reads:

- **Ideal Client Avatar** is `drafted` only when who they serve is the member's word **and** at least two of these come from the member or their current files: pains, dream state, objections, buying trigger, a client's own words. Otherwise it is `partial`.
- **Signature Offer** is `drafted` only when the core result is the member's word **and** what a client receives or how the work runs is known. Otherwise `partial`.
- **Positioning & Messaging** is `drafted` only when the alternative or what makes them different comes from the member or their files. Otherwise it is `partial`, and the page says the positioning is their own snapshot restated.
- If who they serve or the core result is not the member's word at all, the step is `blocked`: stop and tell the member what is missing. Do not go around it.

When two of the three are partial, `autopilot.py next` says so at the review. Tell the member plainly, and offer to stop there and run the Ideal Client Avatar session by hand. Going on is their choice.

## The review

After the foundation and before anything else, the member sees the Foundation Reveal and decides. `references/foundation-reveal.md` covers the page. The rules:

- Nothing in Phase 4 starts until `autopilot.py approve` has recorded the member's own words.
- "Go ahead: yes" on the review, or "looks fine, keep going", is a go-ahead. Silence, or your own judgement that it is good, is not. "Looks right" on all three parts with no go-ahead means show them the page again.
- A line they change becomes theirs: apply it in their words and tag it confirmed, on the page and in the draft document it came from, and record that step again with `--redo`. If the change they ask for is already there, say so and change nothing.
- A part they say nothing about stays drafted. Their go-ahead covers it; do not ask again. In a part they marked "Change this", the lines they did not mention stay drafted too.
- A part they mark "Looks right" changes its drafted lines to **reviewed**: a draft they approved as it stands. It is not their own words, so it never becomes confirmed, and later sessions still treat it as a draft that may be reworded.
- A change that says what **not** to say is recorded with `autopilot.py decide --key never_claim` (or `retired`), so every later session carries it.
- If they change who the client is to a different group, what the offer is, or the price, rerun the foundation sessions that depend on it, record each again with `autopilot.py done SLUG --redo`, rebuild the page and show it again before recording a go-ahead. Added detail about the same client (an age range, a town) is not a change of client: apply it and keep their go-ahead.
- **One last question, straight after the go-ahead.** `autopilot.py approve` lists any step whose main input the member does not have (an opt-in page with no free resource, follow-up with no tools named, lead generation with no preferred source). Ask once whether to run those anyway or leave them out, and record each one left out with `autopilot.py leave-out`. After that, no more questions.

## What a run writes into the Business File

The protocol says only member-confirmed content goes into the file. An Autopilot run is the one stated exception, and it is a narrow one.

- **Before the review:** nothing drafted. Two things the member has just told you go into §1 at once, because every session reads them there: a line they retire (Retired lines, in quotation marks, separated by semicolons) and what they refuse to claim (Never claim or promise). Phase 1 answers also fill empty §1 fields: price, tools, lead source, how someone books, background, a typical client result.
- **After the member approves the foundation:** §2, §3 and §4, from `foundation.json`. Every line that is not the member's own word carries its tag in the file: `[file: path]`, `[reviewed draft]` or `[draft]`. A later session that reads the file treats a tagged line as a starting point, never as a fact.
- **In Phase 4:** nothing is written into the sections those sessions own, and their status lines are left as they are. A section that holds only a file name reads as built to the next session, and it is not. The drafts are listed by name in the §8 row.
- **Status:** §2, §3 and §4 are `provisional`, by `Autopilot`. A run never marks a section `complete`. The owning session does, or the member does.
- **§1:** "None" is never written into Retired lines; when there are none, leave that line as it is.
- **§8:** one row for the whole run, with the readiness number, the name of every draft under `autopilot/drafts/`, which were only partly drafted, and "not rated: autopilot".
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

First the drafts are checked. `drafts.py check --dir autopilot` reads every draft against the member's retired lines, their guarantee, the figures that are actually known, the client words they have permission to use, and what they refuse to claim. It is the last line of defence, not the first: a session still writes carefully. A `FIX` is corrected in the draft. A `LOOK` is a sentence near something the member refuses to claim; read it and reword it if it comes close. The Your Build page will not build while a `FIX` remains.

Then two things, both made by script from `run.json`:

- `autopilot.py report`: what was drafted and where it is saved, what was only partly drafted, what could not be drafted and why, what the member told you at the start, and every "needs you" tool with the sentence that starts it. It opens with **What to do first**: the gaps that come up in more than one draft, which are the few answers that improve the most.
- `handover.py build`: the same, as the **Your Build** page, with a link to each document and a checklist the member can tick.

Give the member both as they are. Do not summarise them into something more flattering.
