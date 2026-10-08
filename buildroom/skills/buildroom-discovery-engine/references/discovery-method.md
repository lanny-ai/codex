# The Discovery Engine — method

_The Magic Business Genie rebuilt the way the founder said he would build it today, co-designed live with a member on 2026-10-07: "I would actually run deep research first. I would find out how many of these questions can we answer. Then we would do a confirm. And then what new information do we need that we don't have? And then it spits out the intake questions." Plus the member's addition: "run it through to establish certainty: do I have the right information, or what's your degree of certainty?"_

The old Genie asked a human 36 questions and then did the gold. The new one answers as many of the 36 as it can from research first, confirms them, asks only the rest, and then does the gold. Same questions. Same ten prompts. Far fewer questions asked of a person.

## The three subjects

The engine runs on one of three subjects. Decide which in Phase 0; it changes where the output goes.

| Subject | Who answers the gaps | Where it writes |
|---|---|---|
| **The member's own business** | the member, in session | the member's Business File: §1, §2 sourced bank, §3 and §4 provisional fields, §13 |
| **A client** (the member does client work) | the client, on a discovery call the member runs from the script | a separate client Business File in its own project folder; never the member's file |
| **A prospect** (business development) | nobody yet; the gaps become the first call's questions | a Prospect Brief; the member's §14 pipeline tracker gets one line |

## The pipeline

### 1. Research first

For the subject, run the research sweep. If a deep-research capability is available (a research skill or subagents), use it; otherwise search and fetch directly. The sweep covers what the 36 questions cover, grouped:

- **Identity and story** (Q1–Q6): founder, origin, stated mission, credentials, awards, press, podcast appearances.
- **Offer and price** (Q7–Q8, Q26): products, services, packages, public pricing, what the site sells.
- **Audience** (Q9, Q11–Q15): who the site and content address, demographics and psychographics as evidenced, geographies served and excluded.
- **Compliance** (Q16): regulated claims, disclaimers, licensing the industry requires.
- **Pains, solutions, objections, outcomes** (Q17–Q21): what the copy promises, FAQs, review language, complaints, testimonials.
- **Website and conversion path** (Q22–Q23, Q27): what a visitor finds, how to book, the lead magnet, the opt-in.
- **Brand and content** (Q24–Q25, Q28, Q33–Q34): voice, platforms, content types, cadence.
- **Competition and position** (Q29–Q30): who ranks beside them, how they differ.
- **Marketing goals and challenges** (Q31–Q32): what the public footprint reveals about what they are trying to do.
- **Proof** (Q35): testimonials, case studies, named results.

Every captured fact carries a source: `[web: URL]`, `[client]` for anything the member or client pasted, `[hypothesis]` for anything inferred. The Business File's provenance rule applies verbatim: nothing inferred is ever written as fact.

### 2. Score the questions

Build the **answer sheet**: all 36 questions, each in one of three states.

| State | Rule |
|---|---|
| **Answered** | a sourced fact answers the question directly; carries the source and a certainty rating |
| **Partial** | something is known but the question needs the subject to complete it |
| **Gap** | nothing reliable found |

Certainty is stated per answer, in words the subject can argue with: **confirmed** (two independent sources or the subject's own site states it plainly), **likely** (one good source), **inferred** (reasoned from evidence; marked `[hypothesis]`). If a certainty-scoring tool is available, use it and record its score; if not, the three words are the scale. Never hide uncertainty inside a confident sentence.

Questions that research cannot answer by nature (Q3 motivation, Q5 passion, Q24 mindset, Q36 anything else) are gaps by design and go straight to the script.

### 3. Confirm

Present the **answered** items to the subject one at a time in the subject's own order of importance, as statements, not questions: "Your core offer is X at $Y. Right?" Each gets confirmed, corrected, or struck. A correction becomes `[client]` provenance and replaces the sourced claim. This is the fastest part and it is where trust is built: the subject sees you did the work.

For a prospect, there is no one to confirm; the answered items become the **assumptions to verify** section of the Prospect Brief, each carried with its certainty.

### 4. The gap list and the scripted questions

Everything **partial** or **gap** becomes a question, in the Genie's original wording where it fits and tightened where the research changes what to ask (a partial question quotes what is already known: "Your site lists three packages; is there a pricing structure behind those, or custom quotes?").

- **Own business:** ask them now, one at a time, per the protocol.
- **Client:** produce the **Discovery Call Script**: the questions in interview order, grouped by theme, with the confirmed facts printed above each group so the member never asks what they already know. Target: under 15 questions and a 45-minute call. The founder's original method was to record the call; the transcript is the source for the answers, tagged `[client]`.
- **Prospect:** the same script becomes the **first-call question set**, plus the three most likely friction points the research surfaced, so the first conversation has somewhere to go.

### 5. The gold: the ten Genie prompts

Only once the answer sheet is complete (confirmed + gaps filled, or, for a prospect, assumptions stated), run the ten prompts from `genie-source.md` **one at a time, in order, each as its own output, pausing for "continue" after each**. The prompts are run exactly as written; the placeholders are filled from the answer sheet. The persona named in P6 is carried into P7–P10.

For a prospect, run P6–P10 only (persona, fears, specifics, twenty outcomes, master summary): the pitches (P1–P5) belong to the business owner, not to someone researching them.

### 6. Outputs

**For the member's own business:** the Discovery Brief (identity block, answer sheet with sources and certainty, confirmations, the ten outputs) saved as `Discovery_Brief_[business]_[date].md`; then the Business File update:
- **§1** every empty field the answer sheet fills, confirmed facts only.
- **§2** confirmed pains, objections, outcomes into the matching fields; every verbatim phrase from reviews, testimonials, or the client's pasted material into the **sourced** bank with its tag; P6's persona becomes the ICA draft only if §2 is empty, marked `provisional`, with P7–P9 content as **hypothesis** language. The Ideal Client Avatar session hardens it.
- **§3** offer name, price, deliverables, outcomes as found and confirmed; status `provisional` (the Signature Offer session owns §3).
- **§4** competitors and the USP as confirmed; `provisional`.
- **§13** one `captured` row per friction point the research surfaced, source `Discovery Engine [date]`.
- **§8** the session row.

**For a client:** the Discovery Brief plus the Discovery Call Script; after the call, the client's own Business File §1–§4 seeded from the transcript, in the client's project folder. The member's file gets only §8 and, if they choose, one §13 row ("client discovery: [client]").

**For a prospect:** the Prospect Brief (identity block, assumptions with certainty, the three friction points, the first-call questions, P6–P10) and one line in §14's pipeline tracker if §14 exists. Nothing else in the member's file.

## The two levels (from the co-design)

The member who proposed this frames the engagement it enables in two levels. The engine is level one. Level two is earned.

- **Level 1, remote.** Run the engine. Find the first two or three obvious friction areas. "Do a build with me" on one. See if it progresses.
- **Level 2, on site.** Come in and watch the business for a day. Rare, relationship-building, and "those are the ones you're gonna charge."

The engine should end its client-mode run by naming the two or three friction areas that a level-one build could start on, each routed to the Build Room session that would do it (a leaking follow-up → Decision Machine; no opt-in → Lead Capture; everything in the owner's head → SOP Creator).

## Rules

- Research before asking. Ask only what research cannot answer.
- Provenance on everything. The Business File's rule is the engine's rule.
- Certainty stated in plain words on every answered item.
- The ten prompts run verbatim, one at a time, after the sheet is complete, never before.
- A client's data never enters the member's own Business File.
- No research on a guessed identity. Phase 0 stops the run if the subject is ambiguous.
- Keys and credentials for any research API stay in the member's `.env`; never print them.
