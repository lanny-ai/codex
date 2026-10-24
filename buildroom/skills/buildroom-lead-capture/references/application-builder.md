# The application builder — a web application instead of a form

_Why this exists: a web form asks for a name and an email and promises nothing. An application qualifies the lead, sets the frame for the call, and produces answers the Decision Machine can tag and route. The founder built one by hand for his own install-call page and said the form "sucks" by comparison. This branch of Lead Capture builds the application as a small web app using the Build Lab's three-step loop (brainstorm → Pursue Goal → build), seeded from the Business File so the first brainstorm is three concrete ideas, not a blank prompt. Added 2026-10-10._

This runs in Claude Code or Codex, in the member's project folder, the same place the page itself is built and deployed. There is no hand-off; the session brainstorms, writes the Pursue Goal, and executes it.

## When to take this branch

Default to the application when any of these hold: the offer is over roughly $1,000, the conversion event in §6 is a booked call, the member has ever been burned by unqualified calls, or §2 has a negative avatar worth screening out. Default to the plain form when the lead magnet is a simple download and the funnel type is Lead, not Application. Ask once: "Form, or application?" with the recommendation stated.

## Step 1 — Three seeded ideas

Do not start with the library's brainstorm prompt cold. Read the file and propose three application concepts, each a different mechanism, each built from what the file already says:

| Idea source | What it becomes |
|---|---|
| §2 pain stack and buying trigger | the questions that make the person articulate their problem and its cost ("how many hours a week do you spend being your own assistant?") |
| §4 for-you / not-for-you lists, §2 negative avatar | the qualifying gates: the two or three answers that route someone out gracefully, with a soft alternative instead of a dead end |
| §3 offer, phases, guarantee | the frame the application sets: what the call is for, what happens in the first fourteen days, what they will be asked to commit to |
| §6 conversion event and sequence | where a completed application goes: the calendar for qualified, the sequence for not-yet, the tag for each |
| §7 lead magnet, if one exists | whether the application is the lead magnet's gate ("get your score, then apply") or a separate front door |

Present the three as a table: name, mechanism, the questions it asks (five to ten), the qualifying rule, what the applicant gets at the end (a score, a recommendation, a booking, a "not yet" with a resource), and why it fits this file. Recommend one. The member picks or edits. This is the brainstorm, already half done; the library's Prompt 1 then runs only on the chosen idea, to challenge assumptions and find edge cases, with the file as its context.

Three mechanisms that recur, as starting points, never as the only options:

- **The scored assessment.** Eight to ten questions that produce a number and a band (the founder's Babysitting Test). The score is the hook; the application is the booking that follows.
- **The fit application.** Five questions, two of them gates, straight to a calendar for those who pass and a nurture sequence for those who don't. Fastest to build.
- **The diagnostic interview.** A branching set that mirrors the sales call's discovery stage, so the call starts at stage three instead of stage one. Best for high-ticket, longest to build.

## Step 2 — The Pursue Goal

Use the library's Prompt 2 verbatim (below), fed with the chosen idea, the file's relevant sections, and these fixed requirements, which go into the Pursue Goal every time:

- One page, mobile first, no dependencies the member has to maintain. Static files plus one function for submission, or whatever the Build Room Pages path supports.
- Every answer is stored and sent: to the CRM as contact fields and tags (in GoHighLevel: contact custom fields plus one tag per band or gate outcome, via the API with the key from `.env`), and as a fallback email to the member.
- The qualifying rule is explicit in code and in the copy. A "not yet" is a page with a resource and the nurture opt-in, never a blank.
- Copy in the voice of §2's sourced language and §4's messaging; the Kern framework applies to the headline and the question framing.
- Deploys to the member's own domain through `deploy-pages.md`. The URL goes into §7.
- Success criteria the member can read: loads under two seconds, works on a phone, submission lands in the CRM with the right tags, the calendar step fires for qualified applicants, the "not yet" path fires for the rest.
- Keys in `.env`, never in the code, never printed.

## Step 3 — Build, review, test

1. **Build:** the library's Prompt 3 verbatim. The loop runs to the Definition of Done.
2. **Executive review:** the library's Prompt 12 verbatim. The ship gate: would customers understand it, does it feel premium, does it solve the problem.
3. **Customer panel:** the library's Prompt 13 (five-persona validation), optional but recommended for anything that gates a sale; it is written for a finished app and exercises the "not yet" path with the skeptical and low-confidence personas, which is where applications fail.
4. **Launch test:** one real submission per path (qualified, not yet), checked in the CRM: fields, tags, calendar, sequence.

## What it writes

- **§7 Application** line: `status (building / live) · URL · [N] questions · qualifying rule in one line · answers land in: CRM fields + tags [names]`.
- **§7 Landing page** status and URL if the application is the page.
- **§6** the trigger map gains the application's tags as entry points if §6 exists; say so, don't rewrite §6.
- **§13** one `shipped` row for the application, source `Lead Capture [date]`, produced: the URL.
- **§8** the session row.

Then the close: the application's tags are entry points for the Decision Machine; the Funnel Scorecard will read the application as a stage (started → completed → qualified → booked).

---

## The Codex Prompt Library prompts used here

_From the founder's "Codex Prompt Library" (AI Momentum Labs workflow, 2026). Reproduced verbatim so the loop runs the same way it does in the Build Lab. Prompts 1, 2, 3, 12, and 13 are used; the library has thirteen._

### Prompt 1: Brainstorm the Project

You are my senior product strategist, software architect, UX designer, business consultant, and AI engineer.

Help me brainstorm this project from every important angle before we begin building anything.

Ask thoughtful questions, challenge weak assumptions, suggest better approaches, identify missing features, uncover edge cases, and recommend the best overall solution.

Don't rush toward implementation.

Our objective is to completely think through the project before writing code.

When we've explored the project thoroughly, tell me we're ready to generate the Pursue Goal statement.

### Prompt 2: Generate the Pursue Goal

Based on everything we've discussed and brainstormed in this conversation, create a single Pursue Goal statement that I can use to have you **complete this project autonomously.**

Do not summarize our brainstorming.

Instead, convert everything into one comprehensive execution goal.

The Pursue Goal should:

- Clearly define the final business outcome.
- Include all important requirements.
- Include all major features.
- Include constraints.
- Include measurable success criteria.
- Make reasonable implementation decisions.
- Continue working until the project is fully complete.
- Test everything.
- Debug everything.
- Validate everything.
- Improve anything that needs improvement.
- Perform a final quality review.
- Only stop if a true external blocker prevents further progress.

Return only the finished Pursue Goal statement.

Organize it using:

- Goal
- Business Outcome
- Project Context
- Deliverables
- Functional Requirements
- Technical Requirements
- Constraints
- Autonomous Execution Instructions
- Validation
- Definition of Done

### Prompt 3: Start Building

Use the Pursue Goal you just created.

Execute it from beginning to end.

Do not stop after planning.

Do not stop after creating a prototype.

Continue building until every Definition of Done item has been satisfied.

Make reasonable technical decisions without asking for unnecessary approval.

Test continuously.

Debug continuously.

Improve continuously.

When finished, perform one final review of the entire project and fix anything you discover before declaring the project complete.

### Prompt 12: Executive Review

Pretend you are the CEO approving this project for release.

Review everything from a business perspective.

Ask yourself:

Would customers pay for this?

Would users understand it?

Would support requests be low?

Is onboarding intuitive?

Does it solve the intended problem?

Does it feel polished?

Does it reflect a premium product?

If not, improve it.

Only declare the project complete when you would confidently release it to paying customers.

### Prompt 13: Five-Persona Customer Validation Panel

Use the finished working application, the Pursue Goal, and everything established in this conversation. Create a five-persona customer panel and evaluate the application from the buyer's perspective.

**Phase 1: Identify the Customer.** Identify the application's primary customer avatar: situation, the problem they need solved, desired outcome, the event that causes them to look for a solution, current alternatives, technical confidence, buying authority, biggest questions and objections, the evidence they need before trusting the product, what would make them purchase, what would make them abandon, what success looks like. If the buyer and end user differ, identify both. Do not invent market research or present assumptions as facts; label assumptions that still require validation.

**Phase 2: Build Five Distinct Buyer Personas.** The Core Best-Fit Buyer; the Skeptical Proof-Seeker; the Busy, Time-Constrained Buyer; the Low-Confidence or Accessibility-Constrained Buyer; the Demanding Power User or Complex Buyer. Each with a distinct background, job to be done, motivation, desired outcome, buying trigger, technical comfort, device and usage context, accessibility considerations, budget concerns, objections, trust requirements, success criteria, abandonment triggers.

**Phase 3: Run Five Independent Customer Tests.** Test each persona independently; do not modify the application until all five are complete. Walk the full journey: first impression, value proposition, starting point, onboarding, primary workflow, instructions and terminology, entering information, recovering from mistakes, feedback and confirmation, help, the intended outcome, the commitment point, returning later, the persona's device. Use test data; no real purchases, messages, or irreversible actions. Record blockers; never invent an observation. For every finding: persona, journey step, action, expected, observed, evidence, simulated reaction, severity, confidence, recommended improvement.

**Phase 4: Collect Persona Feedback.** What they understood, what confused them, what felt valuable or irrelevant, what raised or lowered trust, likely abandonment point, questions before buying, missing features, biggest objection, the single most valuable improvement, buy / continue / recommend / abandon and why. Score 1 to 5: relevance, clarity, ease, trust, value, speed, accessibility, confidence, willingness to purchase, likelihood to recommend.

**Phase 5: Customer Evidence Coordinator.** Preserve raw findings; combine into one report separating directly observed evidence, strong inference, and simulated hypothesis. Identify problems affecting all, several, or one segment; contradictions; trust and purchase objections; accessibility barriers; onboarding and workflow friction; missing information; unmet needs; conversion and retention opportunities; strengths to preserve. Produce the opportunity matrix (priority, opportunity, evidence, personas, stage, impacts, severity, confidence, effort, action, acceptance criteria) and the fifteen-section coordinator report ending in a release recommendation.

**Phase 6: Improve and Re-Test.** Fix critical defects and high-impact, high-confidence problems within scope; no speculative features. Re-test affected journeys; one final core-workflow test across all five; before-and-after evidence; updated report. Do not call the product "customer validated" until confirmed with real customers; call it simulated five-persona validation.
