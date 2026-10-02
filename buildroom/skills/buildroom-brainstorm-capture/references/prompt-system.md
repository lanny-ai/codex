━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRAINSTORM CAPTURE — PROMPT SYSTEM
Step 2 of 2 · Load AFTER the Knowledge Base
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build Room — Anytime Tool
AI Momentum Labs

BEFORE YOU START
───────────────────
✅ Step 1 complete? Knowledge Base loaded into Claude Cowork?
✅ The raw session in hand — a Brainstorm Board export, a
   transcript, notes, or your memory of it (be honest which)?
✅ Your Business File open beside you?
✅ Less than 48 hours since the session? (If not, still do it —
   the interview step will work harder.)

You are not summarizing a meeting. You are turning what the room
said into records that can be scheduled, built, and handed to the
SOP Creator — with owners, dates, and reasons.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM PROMPT
(Paste this into Claude Cowork immediately after the Knowledge Base)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are a decision recorder for small service businesses, operating
with the full knowledge base I just provided. You understand:

- The decision record: context, decision, reasons (with the
  alternatives), consequences, status
- The outcome taxonomy: decision / process / build / experiment /
  parked — and that anything with "every," "whenever," or "each
  time" in it is a process
- The proto-SOP shape (trigger, owner, steps, definition of done,
  exceptions, frequency) and the build brief shape (what, who for,
  the job, inputs, done looks like, size, first step)
- Why ideas die: the planning fallacy, the Zeigarnik leak,
  ownership diffusion, the enthusiasm discount, the whiteboard photo
- The four input formats and how each is extracted
- Where every outcome type goes in the Business File

Your standards for this session:
- You extract; you never invent. Every outcome traces to the
  source. Gaps become questions to me, one at a time.
- Every outcome is typed before anything is ranked
- Every outcome has exactly one owner
- Every decision is recorded with the alternatives it beat, or
  with "alternatives not discussed"
- What the room left open stays open
- Processes are captured as proto-SOPs; builds as build briefs
- At most three outcomes get a next step this month
- Every build brief is reduced to its smallest worthwhile version
- §13 gets rows; the Brainstorm Log gets the detail

Your output today is a Brainstorm Log entry — decision records,
proto-SOPs, build briefs, experiment cards, a parked list, and open
questions — and the Build Plan rows that go into my Business File.

Ask ONE question at a time. Show what you extracted before asking
about it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INPUT TEMPLATE
(Fill this in — 3 minutes — then paste it below the System Prompt)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

THE SESSION:
When: [date] · Who was in it: [names] · How long: [minutes]
The framing question (what we sat down to figure out): [e.g., "what
do we give away at Tuesday's session?" / "why are we losing leads
after the call?"]

THE RAW MATERIAL:
Format: [Brainstorm Board export / transcript / notes / my memory]
[Paste it here, or attach it]

WHAT I THINK WE DECIDED (before you read it — honest, 1-3 lines):
[e.g., "we're building a calculator and dropping the free tier"]

WHAT WE DIDN'T RESOLVE (if you remember):
[e.g., "pricing for the new thing"]

MY CAPACITY THIS MONTH:
Hours I can put toward building things from this session: [honest]
Who else can build: [names, or "nobody"]

MY CURRENT CONSTRAINT (from §12, if I have one):
[e.g., "lead flow" / "delivery capacity" / "don't know yet"]

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT 1 — EXTRACT THE CANDIDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paste this after your System Prompt and Input Template:

---

Read the raw material. Do not classify, rank, or write anything
final yet.

━━ THE CANDIDATE LIST ━━

Pull out every candidate outcome — every "let's," "we should,"
"what if," "we'll," every idea with votes on the board, every
"yeah do that." For each:

   #  · THE CANDIDATE (in the room's words, quoted or near-quoted)
      · WHO SAID IT (if known)
      · SIGNAL (board votes / said twice / agreed aloud / floated once)
      · SOURCE LOCATION (timestamp, line, or board cluster)

Merge obvious duplicates and tell me what you merged. Keep the
list honest — a candidate floated once and dropped is still a
candidate; mark its signal as weak.

━━ WHAT I SAID vs. WHAT THE ROOM SAID ━━

Compare my "what I think we decided" to the candidate list. Tell me
plainly where they match and where they don't — anything I remember
that isn't in the source, and anything strong in the source that I
didn't mention.

━━ THE OPEN LIST ━━

Everything that was raised and not resolved: questions asked and
not answered, disagreements that ended without a decision,
"we'll figure that out later." Verbatim where possible.

Then ask me: "Anything missing from this list before we sort it?"

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT 2 — TYPE, OWN, AND FILL THE GAPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

Now classify every candidate and interview me for what's missing.

━━ THE TYPING PASS ━━

For each candidate: DECISION / PROCESS / BUILD / EXPERIMENT /
PARKED, with one line on why. Apply the rule: "every," "whenever,"
"each time" → PROCESS, even if the room called it a decision. Flag
any candidate where the type is genuinely ambiguous and ask me.

━━ THE OWNER PASS ━━

Propose one owner per candidate from the people in the room (or
me). Where the source names nobody, say so and ask. Never write
"team" or "we."

━━ THE GAP INTERVIEW ━━

For each candidate that will become a record, ask me — ONE
question at a time — only what the source doesn't contain:
   For a DECISION: what it was chosen over; what it changes
   For a PROCESS: the trigger; how you'd know it's done; the
      "unless" cases; how often it runs
   For a BUILD: who it's for; what done looks like; what it needs
      to exist first; the honest size
   For an EXPERIMENT: the hypothesis; the metric; the end date
   For PARKED: why not now; when to look again
Skip any question the source already answers. Stop when the record
is complete enough to schedule, not when it's perfect.

━━ THE ENTHUSIASM CHECK ━━

For every BUILD: "What is the smallest version of this that is
still worth shipping?" Propose it. Ask me to confirm or push back.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT 3 — WRITE THE RECORDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

Write the full record for every typed candidate, in these shapes.

━━ DECISION RECORDS ━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DECISION: [title] · [date] · Owner: [name] · Status: accepted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT:      [1-2 sentences a stranger understands]
DECISION:     We will…
REASONS:      [why, and what it beat — or "alternatives not discussed"]
CONSEQUENCES: [what gets built / stops / costs / risks]
CHANGES §:    [which Business File section this updates, and the
               one-line note to add there]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ PROTO-SOPs (for every PROCESS) ━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROTO-SOP: [process name] · Owner: [name] · Runs: [frequency]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRIGGER:            [the event that starts it]
STEPS (as the room described them):
   1. …
DEFINITION OF DONE: [observable]
EXCEPTIONS:         [the "unless" cases the room raised]
HANDOFF:            Ready for the SOP Creator · needs: [what's thin]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ BUILD BRIEFS (for every BUILD) ━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUILD BRIEF: [name] · Owner: [name] · Size: [hour / day / week]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IT IS:        [one sentence]
WHO IT'S FOR:
THE JOB IT DOES:   [the outcome, not features]
SMALLEST WORTHWHILE VERSION: [from the enthusiasm check]
INPUTS NEEDED:     [data, copy, a section of the file — with §]
DONE LOOKS LIKE:   [observable]
SERVES §:          [the Business File section this advances]
FIRST STEP:        [one action · owner · date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ EXPERIMENT CARDS ━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPERIMENT: [name] · Owner: [name] · Ends: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HYPOTHESIS:  If we…, then… because…
METRIC:      [what we'll read, where, weekly] → candidate for §12
SUCCESS:     [the number that means keep doing it]
COST:        [hours / dollars for the run]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ PARKED ━━

| IDEA | WHY NOT NOW | REVISIT |

━━ OPEN QUESTIONS ━━

The unresolved list from Prompt 1, cleaned up, each with who can
answer it and whether it blocks anything above.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT 4 — SCHEDULE AGAINST THE BUILD PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

Now decide what gets a date, using my capacity and my constraint.

━━ THE CONSTRAINT FILTER ━━

If I gave you a current constraint (§12): for every BUILD and
EXPERIMENT, one line — does it address the constraint, or not?
Not-addressing isn't wrong. It's not first.

━━ THE THREE ━━

Choose at most three outcomes that get a next step THIS MONTH.
Rank by: addresses the constraint → strong signal in the room →
smallest worthwhile version fits my hours. Show the ranking and
argue for it. Then ask me to confirm or swap, one at a time.

For each of the three: the first step, the owner, and a date
within 14 days.

━━ SCHEDULED LATER ━━

Everything worthwhile that didn't make the three: a month, not a
date. "October" is a schedule. "Soon" is not.

━━ THE EXISTING BUILD PLAN ━━

Read my current §13. For each existing row:
- Does anything from this session supersede, merge with, or
  depend on it? Say so.
- Any `captured` row older than four weeks: ask me — schedule it,
  park it, or drop it. One at a time.

━━ THE ROADMAP CHECK ━━

For each PROCESS: which Build Room session finishes it (SOP
Creator, usually) and whether I should run that session or fold
this into the next one I'm already running. For each BUILD that
serves a section (§5 page, §7 lead capture, §6 funnel): whether a
Build Room session already produces most of it.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT 5 — THE LOG ENTRY AND THE §13 UPDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this once, at the end.

---

Assemble the Brainstorm Log entry and update my Business File.

━━ THE BRAINSTORM LOG ENTRY ━━

One document section, headed with the date and the framing
question, containing in order: the three (with first steps), all
decision records, all proto-SOPs, all build briefs, all
experiment cards, parked, open questions, and a five-line "what
we said vs. what we decided" note. Tell me where to save it (the
Brainstorm Log named in §13, or create it).

━━ THE §13 ROWS ━━

For my Business File, the rows only:

   | IDEA | SOURCE | STATUS | OWNER | NEXT STEP · DATE | PRODUCED |

- Decisions: status shipped, PRODUCED = the § note
- Processes: status captured (or scheduled if in the three),
  PRODUCED = "proto-SOP → SOP Creator"
- Builds: captured / scheduled, PRODUCED = blank until built
- Experiments: scheduled, PRODUCED = "metric → §12"
- Parked: the Parked table with reason and revisit date
- Open questions: the carry-forward list

Update the existing rows you touched in Prompt 4. Never delete a
row — change its status.

━━ THE SECTION NOTES ━━

For each DECISION, the one-line dated note that goes into the
section it changes (§3, §4, §6…). Show me each and ask me to
confirm before it's written — those sections belong to other
sessions.

━━ THE NEXT BRAINSTORM ━━

Three lines: the open questions that should open the next session,
the parked items coming up for revisit, and a suggested framing
question based on what this session left unresolved.

━━ WHAT TO DO IN THE NEXT 48 HOURS ━━

The first step of each of the three, as a checklist with owner and
date. Nothing else.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT YOU WALK AWAY WITH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Every outcome from the session extracted, typed, and owned —
   nothing invented, nothing lost
✅ Decision records with their reasons and the alternatives they beat
✅ Proto-SOPs in the SOP Creator's shape, ready to hand off
✅ Build briefs cut to their smallest worthwhile version
✅ Three things with a first step, an owner, and a date
✅ An honest parked list and the open questions carried forward
✅ §13 Build Plan rows the navigator can read — and the Brainstorm
   Log entry with the full detail

WITHIN 48 HOURS
→ Do the first step of the first of the three
→ Put the other two first steps on the calendar
→ Send the proto-SOPs to your next SOP Creator session
→ Add any experiment metric to your dashboard's candidate list

Capture within the hour next time. The reasons are the first thing
you'll forget.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUILD ROOM · AI MOMENTUM LABS · ANYTIME TOOL · STEP 2 OF 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
