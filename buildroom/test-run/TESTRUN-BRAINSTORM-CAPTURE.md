# Brainstorm Capture — Test Run on a Real Brainstorm

**Run:** 2026-09-16 · Skill under test: `buildroom-brainstorm-capture` (prompts 1–5, executed against the source below)
**Source:** the actual exchange in this build session on 2026-09-09 that produced the Rent Calculator — a transcript, not a board export, and not memory.
**Member:** Lanny Morton (AI Momentum Labs). The member was not present for this run, so every gap-interview question is recorded as **open** rather than answered. That is the skill's rule ("extract, don't invent") being tested under the hardest condition.

---

## Input template (as the source supports it)

- **When:** 2026-09-09 · **Who:** Lanny, Claude · **How long:** ~26 minutes wall-clock across five turns
- **Framing question (reconstructed from the first message):** "What can we give away in today's Build Room session, in 26 minutes, that's genuinely useful?"
- **Format:** transcript
- **What the member said was decided:** not stated up front — the source is the brainstorm itself
- **Capacity / constraint:** not in source → open

## Prompt 1 — Extract the candidates

| # | Candidate (room's words) | Who | Signal | Source |
|---|---|---|---|---|
| 1 | "something really amazing we could do in Build Room today… give away in 26 minutes" | Lanny | framing, not an idea | msg 1 |
| 2 | The Rent Calculator: one-page tool, list processes, score Freq/Pain/Lock/Variance, hours + dollar rent, ranked document-first list, CTA to SOP Creator | Claude | built and accepted ("Go", "Build it now") | msg 2 |
| 3 | Run-of-show for the room: screen-share, members do theirs on phones, "Who's over 40 hours a month?" | Claude | proposed, not explicitly accepted | msg 2 |
| 4 | The giveaway stack: calculator link + sop-creator.skill + STEP1/STEP2 pair | Claude | proposed, not explicitly accepted | msg 2 |
| 5 | Yearly rent number next to monthly | Claude | accepted ("Go") | msg 3 → 4 |
| 6 | "Copy my result" shareable line for the chat | Claude | accepted ("Go") | msg 3 → 4 |
| 7 | Enter-to-add-row | Claude | accepted ("Go") | msg 3 → 4 |
| 8 | "Copy as §9 starter" — feed the Business File so SOP Creator pre-fills triage | Claude | accepted ("Build it now") | msg 3 → 5 |
| 9 | Owner-lock honesty check (Gerber's line at >70% Lock 4–5) | Claude | floated once, not decided | msg 3 |
| 10 | "Bring the transcript" mode — pre-seed examples from Zoom Office Hours once re-authed | Claude | floated once, blocked on Zoom auth | msg 3 |
| 11 | Commit the calculator to the repo and bundle | Claude → Lanny | accepted ("Add it to the repo and the PR") | msg 5 → 6 |
| 12 | Name a specific member struggle on screen from Zoom transcripts | Claude | offered, no answer | msg 2 |

Merged: none (each is distinct). Weak-signal items kept: 9, 10, 12.

**What the member said vs. what the room said:** the member gave four words of direction ("Go", "Build it now", "Add it to the repo and the PR") and one open prompt ("How can we make this better?"). Everything else was proposed by Claude and accepted by the member. The capture must not treat Claude's proposals as the member's decisions unless the member said yes — items 3, 4, 9, 10, 12 were never accepted.

**Open list (verbatim where possible):**
- "if there was a specific member struggle you wanted named on screen, tell me" — no answer
- Whether the run-of-show (item 3) was used in the room — unknown
- Whether the giveaway stack (item 4) went out as proposed — unknown

## Prompt 2 — Type, own, fill the gaps

| # | Type | Why | Owner |
|---|---|---|---|
| 2 | **build** | a thing to make | Lanny (accepted), built by Claude |
| 3 | **process** | "run it in the session" — repeats every live session where a tool is shown | *open* — no owner named |
| 4 | **decision** | a choice about what goes out | Lanny (implicit) — *alternatives not discussed* |
| 5, 6, 7 | **build** (increments of 2) | merged into the build brief as v2 | Lanny |
| 8 | **build** | increment; also creates a process (room → file → SOP Creator) | Lanny |
| 9 | **parked** | floated, not decided | — |
| 10 | **parked** | blocked on Zoom re-auth | — |
| 11 | **decision** | where the source of truth lives | Lanny |
| 12 | open question | never answered | — |

**Gap interview — questions the skill would ask, recorded as open because the member wasn't present:**
1. (build 2) Who is it for beyond the live room — every member, or only Operations-month attendees?
2. (build 2) What does "done" look like now that v3 shipped — is it done, or is 9 still wanted?
3. (process 3) Does every live session that shows a tool follow this pattern? Who owns running it?
4. (decision 4) Was the stack sent as proposed? What was it chosen over?
5. (parked 9, 10) Revisit dates?
6. Capacity this month and the current constraint (§12 not yet built for AI Momentum Labs).

**Enthusiasm check on build 2:** the smallest worthwhile version was v1 (scores → rent → ranked list). v2 and v3 were scoped by the member's "Go" and "Build it now" — an explicit choice to exceed the smallest version, recorded as such.

## Prompt 3 — Records

**DECISION: The giveaway stack goes out with the calculator** · 2026-09-09 · Owner: Lanny · Status: accepted (implicit)
CONTEXT: A live session in 26 minutes with nothing prepared. DECISION: Give away the Rent Calculator link + the SOP Creator skill + its STEP1/STEP2 pair. REASONS: alternatives not discussed. CONSEQUENCES: the calculator becomes a member-facing tool and needs a home in the bundle (→ decision below). CHANGES §: none yet (§9 for AI Momentum Labs is not built).

**DECISION: The repo is the source of truth for the calculator** · 2026-09-09 · Owner: Lanny · Status: accepted
CONTEXT: The page lived in scratchpad; the artifact link is the hosted copy. DECISION: commit to `buildroom/rollout/` and package in the bundle. REASONS: ships with the bundle; the artifact link is private by default (confirmed later when a member got a 404). CONSEQUENCES: bundle rebuilds include it; two copies to keep in sync. CHANGES §: none.

**BUILD BRIEF: The Rent Calculator** · Owner: Lanny · Size: hour (v1) → shipped v3
WHAT IT IS: a one-page tool that shows what undocumented processes cost in hours and dollars. WHO IT'S FOR: Build Room members in the Operations month. THE JOB: make the SOP Creator's hook visible and hand the member into it with their triage already done. SMALLEST WORTHWHILE VERSION: v1 (scores, rent, ranked list, CTA). INPUTS: the SOP Creator's priority formula and the §9 schema. DONE LOOKS LIKE: a member's ranked list drops into their Business File without retyping — **met by v3**. SERVES §: §9. FIRST STEP: shipped; the next honest first step is "put it in front of one real member and record what they did" — *owner and date open*.

**PROTO-SOP: Showing a tool in a live session** · Owner: *open* · Runs: every live session with a giveaway tool
TRIGGER: a session where a tool is demoed. STEPS (as proposed): 1. screen-share, put in your own real numbers; 2. everyone does theirs on a phone; 3. ask the room for the number; 4. name the session that solves it. DEFINITION OF DONE: members have pasted their result in the chat. EXCEPTIONS: none discussed. HANDOFF: ready for the SOP Creator · needs: confirmation it was actually run, and an owner.

**PARKED**
| Idea | Why not now | Revisit |
|---|---|---|
| Owner-lock honesty check (Gerber line) | floated, not decided; three-minute build | *open* |
| "Bring the transcript" mode | blocked on Zoom re-auth | when Zoom is re-authorized |

**OPEN QUESTIONS:** the six gap-interview questions above, plus "was a specific member struggle named on screen?"

## Prompt 4 — Schedule

No constraint available (§12 not built for this member) → constraint filter skipped and *said so*. Capacity unknown → the three are proposed, not confirmed:

1. **Put the Rent Calculator in front of one member and record what happened** — owner *open*, within 14 days. (Build → its real first step.)
2. **Decide the parked owner-lock check** — three minutes to build, worth a yes/no. Owner Lanny.
3. **Confirm or drop the live-session proto-SOP** — if it was run, it goes to the SOP Creator; if not, park it.

Scheduled later: "Bring the transcript" mode — the month Zoom is re-authorized.

Existing §13: none (section created this run). Roadmap check: the proto-SOP belongs in the SOP Creator; the build serves §9 and is already in the bundle.

## Prompt 5 — §13 rows (as they would be written)

| IDEA | SOURCE | STATUS | OWNER | NEXT STEP · DATE | PRODUCED |
|---|---|---|---|---|---|
| Rent Calculator (v3) | Brainstorm 2026-09-09 | shipped | Lanny | Put it in front of one member · *date open* | `rollout/Rent_Calculator.html`, in bundle |
| Giveaway stack: calculator + SOP skill + pair | Brainstorm 2026-09-09 | shipped | Lanny | — | decision record |
| Repo is source of truth for the calculator | Brainstorm 2026-09-09 | shipped | Lanny | — | decision record |
| Live-session tool demo process | Brainstorm 2026-09-09 | captured | *open* | Confirm it was run · then SOP Creator | proto-SOP |
| Owner-lock honesty check | Brainstorm 2026-09-09 | parked | — | Decide yes/no · *date open* | — |
| "Bring the transcript" mode | Brainstorm 2026-09-09 | parked | — | Revisit when Zoom re-authed | — |

---

## Findings

**Worked**
- **The extraction rule held under the hardest input.** With the member absent, the skill produced zero invented facts: every owner, date, and reason it couldn't source is marked open. Six of six gap questions stayed open. That is the behavior the knowledge base demands.
- **The taxonomy caught the disguised process.** "Run it in the session" was proposed as advice and would have been lost; typing it as a process surfaced a real SOP candidate.
- **The said-vs-decided comparison is the most valuable output.** It made explicit that Claude proposed twelve things and the member accepted five. A capture that treated all twelve as decisions would have written seven fictions into §13.

**Findings to act on**
1. 🟠 **Facilitator-proposed vs. member-decided needs its own column.** When Claude (or any facilitator) is in the room, the candidate table should carry `proposed by / accepted by`. The prompt system has "who said it"; it should also have "who said yes." Small change to Prompt 1.
2. 🟠 **A shipped build's "first step" flips to validation.** The brief's FIRST STEP field reads as "start building." For anything already built, the skill should ask for the validation step (one real user, one observation) instead. Add one line to Prompt 3's build brief: *if already built → first step is the validation.*
3. 🟡 **No §12 means the constraint filter silently drops.** The skill said so here, which is correct, but Prompt 4 should offer the fallback: "rank by the roadmap's current month instead." One sentence.
4. 🟡 **The board export covers the gap the transcript couldn't.** Every open owner and date above would have been filled in the board's Decide step during the session. The board is not a nice-to-have for Capture; it is what makes Capture cheap. The member README should say that.
5. 🟡 **Twelve candidates from a five-turn exchange is the right density.** A 60-minute room will produce 30–50. Prompt 1's table stays readable to about 40 rows; beyond that the skill should extract per cluster. Note for when a real board export arrives.

None of these are applied yet. Findings 1–3 are one-line prompt edits; they belong in the next revision after the member has run the loop once on a real board.
