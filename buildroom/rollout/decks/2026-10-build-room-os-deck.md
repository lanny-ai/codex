# Build Room OS
## One file. Twenty-six skills. Every session reads it before asking you anything.
AI Momentum Labs · The Build Room · October 2026

---

# Why we changed the format

**The problem we had.** Every Build Room week shipped as a zip of prompts. Members re-explained their business, their avatar, their offer in every session. Claude had amnesia. Six of thirty-six roadmap slots were actually filled, zips didn't match what the roadmap advertised, and nothing carried forward from one week to the next.

**The decision.** Stop shipping prompts. Ship a system: one member-owned file that every session reads at the start and writes at the end, and a skill for every session that knows how to read it.

**The result.** A member's whole business becomes one document. Session four asks almost nothing because sessions one to three already wrote the answers.

---

# What Build Room OS is

Four parts, one folder:

1. **The Business File.** One markdown document the member owns. Seventeen sections, statuses, a session log. Member edits win.
2. **Twenty-six skills.** One per session. Each reads the file, asks only what the file can't answer, delivers a finished asset, writes its section back.
3. **Three browser tools.** The Business File Viewer, the Brainstorm Board, the Rent Calculator. No AI call needed.
4. **The production pipeline.** A generator that turns any week's curriculum into a skill, and build scripts that package it for Claude Code, Codex, and Cowork from one zip.

---

# The Business File

Seventeen sections, always in the same order, Session Log last:

§1 Snapshot · §2 Ideal Client Avatar · §3 Signature Offer · §4 Positioning · §5 Offer Page · §6 Funnel · §7 Lead Capture · §9 Operations & SOPs · §10 Team & Hiring · §11 Training · §12 Weekly Ops · §13 Build Plan · §14 Lead Generation · §15 Sales Conversations · §16 Follow-Up Engine · §17 Founder Compass · §8 Session Log

**Rules that matter.** Statuses: not started, provisional, complete. A 2,500-word ceiling. Provenance on every client quote: sourced language is tagged, hypothesis language is tagged, and no skill promotes a line without a source. Read before asking. Write before ending.

---

# How every session runs

1. **Read.** The skill reads the Business File and pre-fills everything it can.
2. **Ask only the gaps.** One question at a time, never something the file already answers.
3. **Build.** The week's curriculum, delivered as a finished asset the member saves.
4. **Write back.** The skill's section, a Session Log row, a 1-to-5 rating.
5. **Route.** The navigator names the one next session with its prerequisites met.

If a prerequisite section is missing, the skill says so and offers a provisional path, and the output stays marked provisional until the real session runs.

---

# The three browser tools

**Business File Viewer.** Paste the file, see the whole business on one screen: progress, every section's status, provenance flags, the Build Plan, and "run this next" with the exact words to say.

**Brainstorm Board.** Frame, diverge on a timer, cluster, dot-vote, decide, then copy the whole board into Claude in the exact shape the Capture skill reads.

**Rent Calculator.** The hours a process costs the owner every month, turned into the ranked document-these-first list that drops straight into §9.

---

# How to use it: install in two minutes

Download `BuildRoom_OS.zip` and unzip it. The folder is your workspace in all three tools.

**Claude Code.** Open a terminal in the folder, run `claude`. The skills are found automatically in `.claude/skills/`.

**Codex.** Open a terminal in the folder, run `codex`. Same skills, found in `.codex/skills/`.

**Cowork (claude.ai).** Settings → Skills → Upload Skill. Upload every file in the `cowork/` folder, twenty-six of them, any order.

Optional: run `install.sh` (Mac) or `install.ps1` (Windows) to copy the skills into your home directory so every project can use them.

---

# How to use it: your first session

1. Open the folder in your tool of choice.
2. Say: **"I'm new to the Build Room, set me up."**
3. The navigator creates your Business File from the blank template, fills §1 Snapshot from a five-minute interview, and tells you the one session to run next.
4. Your file lives at `BUILDROOM_BUSINESS_FILE.md` in the folder. In Claude Code and Codex the skills read and write it directly. In Cowork you paste it at the start and replace your copy with the updated one at the end.

If you already have a Compass, run **"Build my compass"** first so every later session sounds like you.

---

# How to use it: running any session

1. **Say the trigger phrase.** Every session has one. "Help me build my signature offer." "Write my offer page." "Help me document my process."
2. **Bring the file.** Claude Code and Codex find it in the folder. In Cowork, attach or paste it.
3. **Answer one question at a time.** The skill only asks what the file can't answer. If it asks something you already told it, the file is out of date; paste the latest one.
4. **Save the asset.** Every session ends with a finished document (an offer, a page, an SOP, a script). Save it with your business documents under the name the skill gives you.
5. **Keep the updated file.** The session emits the whole Business File with a "what changed" summary. Replace your saved copy. Your edits always win over the skill's.
6. **Rate it.** The 1-to-5 rating goes in the Session Log.

---

# How to use it: the order to run them

Run the sequences in order the first time. Each one feeds the next.

1. **Foundation, Offer Clarity.** Ideal Client Avatar → Signature Offer → Positioning & Messaging → Offer Page Copy.
2. **Funnel and Automation.** Funnel Map → Decision Machine → Lead Capture → Funnel Scorecard.
3. **Lead Generation.** Lead Gen Machine, four modules, one a week.
4. **Sales.** Sales Conversations.
5. **Operations.** SOP Creator → Hiring Kit → Training Docs → Weekly Ops Dashboard.

**Anytime.** Compass, Brainstorm, Brainstorm Capture, Copy Engine, the Boardroom. **Hardening passes** when the file says so: Audience Insight, Offer Deep Dive. **Electives** when you want them: Second Brain, Source Watcher, Agent Forge, Video Engine.

Not sure? Say **"Where do I start?"** and the navigator answers from your file.

---

# How to use it: when a session says something is missing

Every session states what it requires. If the section isn't there, you get two paths:

- **Run the missing session first.** Almost always the right move. The navigator names it.
- **Take the provisional path.** A short interview stands in for the missing section. The output gets marked `provisional` and the navigator keeps flagging it until the real session runs.

Provisional inputs propagate: a page written from a provisional avatar is a provisional page. The Viewer shows the debt so you can pay it down.

---

# How to use it: say these words

| Say | You get |
|---|---|
| "I'm new to the Build Room, set me up" | Your file, §1 filled, your next session |
| "Where do I start?" | The navigator's one next step |
| "Build my compass" | §17, so every session sounds like you |
| "Help me build my ideal client avatar" | §2 |
| "Help me build my signature offer" | §3 |
| "Help me position my business" | §4 |
| "Write my offer page" | §5, and a path to your own domain |
| "Help me map my funnel" | §6 |
| "Build my follow-up system" | §16, the Decision Machine |
| "Help me build my opt-in page" | §7 |
| "Where is my funnel leaking?" | The scorecard, the top leaks, approved fixes, an optional weekly routine |
| "Help me get more leads" | §14, one module at a time |
| "Help me with my sales call" | §15 |
| "Help me document my process" | §9, with the automation audit |
| "Help me hire for this role" | §10 |
| "Help me train my new hire" | §11 |
| "What numbers should I be watching every week?" | §12 |
| "Let's brainstorm" / "Capture what we decided" | §13 |
| "Convene the board" | A decision, argued four ways |
| "Write me the email" | Copy from your file, Kern or Halbert |
| "Set up my second brain" / "Build me a source watcher" / "Make me an agent" / "Set up the video engine" | The electives |

---

# How to use it: keep it alive

**Weekly.** One session, one asset, one updated file. Open the Viewer on Monday: it shows what's provisional, what's complete, and what to run next.

**Monthly.** Run the hardening passes the navigator flags: Audience Insight when §2 holds only hypothesis language, Offer Deep Dive when sales are slow, a Brainstorm when the Build Plan is empty or a captured row is over four weeks old.

**When circumstances change.** Redo the Compass. Re-run the session whose section changed; every downstream session picks it up.

**Keep the file in your vault.** If you run the Second Brain elective, the Business File moves into the vault root and Claude reads it there like everything else you know.

---

# How to use it: for facilitators

The run-of-show is a sixty-minute launch session:

1. Everyone installs the zip (ten minutes, one tool each).
2. Everyone runs "set me up" and gets a §1 and a next step (fifteen minutes).
3. Two live demos on a volunteer's file: one Foundation session start, one Viewer walk-through.
4. Homework: the next session the navigator named, before the next call.

Every new Build Room week becomes a skill the same day through the generator, so members never wait for a zip again.

---

# Build Room OS (navigator)
*The front door. Reads the file, shows progress, routes to exactly one next session.*

**Added.** New.
**How.** A progress view over every section, six routing rules (first gap with prerequisites met, harden provisional debt first, missing prerequisites named, ship-state nudges, everything complete means brainstorm), goal-first routing, and the trigger phrase to say.
**Why.** A member with twenty-six skills needs one place that tells them which to run. This is the only skill that never builds anything.

---

# Ideal Client Avatar (§2)
*The April Week 1 curriculum, wired to the file.*

**Improved.** From a prompt zip to a skill that writes §2.
**How.** Reads §1, runs the curriculum one question at a time, writes the avatar back. The language bank is now two banks: sourced (real client words, tagged with where they came from) and hypothesis (generated, tagged as such). The skill writes only real material into the sourced bank.
**Why.** The test run found the red finding: a verbatim bank that couldn't tell a client's words from the model's. Copy written from invented quotes is the fastest way to sound generic.

---

# Signature Offer (§3)
*April Week 2, wired to the file.*

**Improved.** Skill plus three new §3 fields.
**How.** Pre-fills from §2, runs the offer curriculum, writes the promise, structure, deliverables, value stack, guarantee, and now the one belief (sixteen words), real urgency, and the deep-dive document.
**Why.** The offer page, the sales script, the follow-up engine, and the lead magnet all read §3. If it's thin, everything downstream is thin. "If your offer sucks, none of it matters."

---

# Positioning & Messaging (§4)
*April Week 3, wired to the file.*

**Improved.** Skill that writes §4.
**How.** Reads §2 and §3, produces the competitive alternative, category, differentiator, positioning statement, value proposition, tagline, villain statement, for-you and not-for-you lists, the Messaging Bible.
**Why.** The offer page and every copy session pull the villain and the differentiator from here instead of asking again.

---

# Offer Page Copy (§5)
*April Week 4, the payoff session.*

**Improved.** Skill plus a deployment path.
**How.** Pre-fills nineteen of twenty-one inputs from §2, §3, §4 (measured in the test run), asks only for proof and a credibility anchor, assembles the page. New reference: publish to a branded subdomain on the member's own domain through Cloudflare Pages, token kept in a `.env` file, never a tool's URL. The ship nudge now offers to publish and record the URL.
**Why.** "The whole point is to put a page on a branded domain that's yours. Without that, this whole process is worthless."

---

# Funnel Map (§6)
*The Automation month, Week 1.*

**Improved.** Skill that writes §6.
**How.** Value ladder, funnel type and the single conversion event, the compact map, the biggest drop-off, the trigger map, the first build priority, the metrics. Reads §1, better with §2 and §3.
**Why.** The Decision Machine's campaign inventory and the Lead Capture build both read this map. It is the prerequisite for the whole automation sequence.

---

# Lead Capture (§7)
*The previously shipped skill, retrofitted.*

**Improved.** Its three original references are untouched; the orchestrator gained the file.
**How.** Reads §1, §2, §3, §6 to pre-fill the extraction report, reads §17 for voice before asking for a pasted Compass, writes §7. New: the deploy-pages reference and the one open decision it forces: GoHighLevel cannot receive pages, so a self-hosted opt-in page embeds a GHL form, or the opt-in stays in GHL.
**Why.** The first skill we shipped was the proof that a retrofit costs one file and keeps everything members already learned.

---

# Funnel Scorecard + Leak Finder (§6 lines, §13, §12)
*Automation & Funnels Week 4, from the founder's recurring funnel test (September 10 and 16 sessions).*

**Added.** The week the roadmap never had curriculum for.
**How.** A stage table over every failure point in the §6 map: entered, converted, rate, change against the prior window, source. Stages can live in a pipeline stage, a tag, a calendar status, a sequence, or a payment event. Nothing is estimated; unread stages are marked UNREAD and ranked first with the fix "install the measurement". A "what moved" line with the lead follow-up check. The top three leaks ranked by revenue at risk (a labelled design choice), two or three fixes each tagged automation, messaging, offer, UX, training, or traffic fit and routed to the Decision Machine campaign or Build Room session that owns them. Approve, skip, or edit each fix; feedback carries to the next run. One scorecard per CRM location. A weekly routine created only on an explicit yes, applying nothing, failing loud.
**Why.** "Every four hours it's doing a conversion check of every stage of the pipeline and suggesting optimizations where the funnel is leaking. And I go, yep, those are great suggestions, do it." Weekly is the default for everyone else. The Funnel Map names the stages, the Decision Machine puts a campaign on each, and this tells you which campaign to fix next.

---


# SOP Creator (§9)
*September Week 1. First new curriculum since April.*

**Added, then improved.** New knowledge base and prompt system; then the FDE audit folded in.
**How.** Triage by frequency, pain, and owner-lock; SIPOC capture by interview; SOPs written for the replacement; checklists with a pause point; a delegation pack. The Forward Deployed Engineer audit added: three scores that produce Go, No-go, or Partial; capture from the operator, never the document; every step mapped to six fields; exceptions dispositioned handle, flag, or route to a human; green, yellow, red gates with four safety questions; a golden dataset and staged rollout for anything automated.
**Why.** "You cannot automate what you have not mapped." §9 now carries an automation-candidates line that Agent Forge reads.

---

# Hiring Ad + Interview Kit (§10)
*September Week 2.*

**Added.** New curriculum.
**How.** The SOPs are the role definition. Scorecard, filter ad, screening call and paid work sample with a planted escalation gap, structured interview kit with 1-3-5 rubrics, references, decision matrix, offer, first week on the four-run ramp. Hard prerequisite on §9.
**Why.** Owners delay hiring because they can't say what the job is. The SOPs already say it.

---

# Team Training Doc Builder (§11)
*September Week 3.*

**Added.** New curriculum.
**How.** Training map, job breakdown sheets by interview (key points come only from the member), practice-built modules with a planted exception and explain-it-back, competence checkouts, escalation drills, a sign-off log, a letting-go plan, the 30-day calendar, a living FAQ. Prerequisite on §9; provisional path only for a missing §10.
**Why.** A hire who reads the SOP isn't trained. A hire who passes the checkout is.

---

# Weekly Ops Dashboard (§12)
*September Week 4. Closes the Operations month.*

**Added.** New curriculum.
**How.** Five to nine numbers read off the file, half leading, each with a goal, owner, two-minute source, and pair; a one-page dashboard for the member's tool; the 30-minute weekly meeting; the constraint named and argued against; and the scheduled-routine offer, shown in full and created only on an explicit yes. It prepares, never decides.
**Why.** The gauge on the machine: shows where the business is off before the bank balance does.

---

# Brainstorm Session (§8, §13) + the Brainstorm Board
*An anytime session with a browser page beside it.*

**Added.** New skill and tool.
**How.** Compressed double diamond: frame, timed diverge with nudges, cluster, dot-vote with per-person budgets, outcome cards with type, owner, first step, and why. The board runs in any browser at phone width and copies the whole session into Claude. Claude offers to prototype a small winner in the room, never imposes it.
**Why.** Ideas were living in whiteboard photos. Now they become owned, dated, typed records.

---

# Brainstorm Capture (§13 Build Plan)
*Turns any brainstorm, transcript, or notes into records.*

**Added.** New skill and a new section.
**How.** Decision records with the alternatives beaten, proto-SOPs in the SOP Creator's shape, build briefs cut to their smallest worthwhile version, experiment cards with a §12 metric, a parked table, open questions. At most three outcomes get a dated next step. Rule: extract, don't invent. The navigator flags captured rows older than four weeks.
**Why.** Tested against the real transcript of the session that produced the Rent Calculator: twelve candidates, zero invented facts. Claude proposed twelve things; the member accepted five. That gap is the point.

---

# Lead Gen Machine (§14)
*Tier A retrofit of the library skill.*

**Improved.** Four modules, one skill, wired to the file.
**How.** Warm network activation, the outreach machine, the referral system, content lead engine plus pipeline. Module references byte-identical to the source. Shared inputs pre-filled from §1 to §4, §6, §7. §14 stays provisional until all four modules have run.
**Why.** A full roadmap month from one retrofit, and the manual outreach sequences it produces are what the Decision Machine reads so it doesn't duplicate them.

---

# Sales Conversations (§15)
*Tier A retrofit of the Sales Coach.*

**Improved.** Wired to the file.
**How.** The seven-stage consultative script, the objection set, role-play mode. The one-question discovery became a read of §2, §3, §4. The member's last lost call decides which stage gets rebuilt.
**Why.** The script should already know the offer and the client. Now it does.

---

# Audience Insight (§2, with provenance)
*Tier A retrofit of the Audience Insight Playbook.*

**Improved.** Wired to the file; it closed the red finding.
**How.** Mines real customer language with sources and writes it into the sourced bank, every line tagged with where it came from. The roadmap gained a rule: hypothesis language is debt, so route here before the offer page or the landing page ships.
**Why.** Copy that quotes a real client converts. Copy that quotes a model's guess at a client sounds like everyone else.

---

# Offer Deep Dive (§3, hardening)
*Tier A retrofit of the Million-Dollar Offer Maker.*

**Improved.** Wired to the file.
**How.** Twelve questions, seven of them answered from the file; adds the one belief, the value stack, real urgency, and the deep-dive document to §3.
**Why.** Run it when §3 is complete but sales are slow, price objections dominate, or the offer page is about to be written.

---

# Copy Engine (§8 only)
*Tier A retrofit of Kern plus Halbert.*

**Improved.** One tool, two voices, reads the whole file.
**How.** Kern for short and conversational pieces, Halbert for long-form direct response. The fact sheet both demand is built from §2 to §7 and §17; hypothesis language is flagged in every draft's notes. Writes nothing but the log.
**Why.** "Write me the email" should never start from a blank brief when the file holds the avatar, the offer, the villain, and the voice.

---

# Decision Machine (§16 Follow-Up Engine)
*Tier B. Rebuilt from transcripts, then hardened from the vault.*

**Added.** The roadmap row that read "coming" is filled.
**How.** Reconstructed from four session transcripts: the three layers (control, belief, awareness), a campaign on every yes/no conversion point, the five beliefs, the seven-stage belief-to-story model, tag architecture, master controller, engagement tracker, the reactivation variant, a CRM build map an agent can run, and a verification checklist the member runs on every tag. Then hardened against the founder's Obsidian vault: the 2024 Keap build, the 2025 bootcamp, the 2026 GoHighLevel port, and the founder's own August build.
**Why.** "Seen" stopped being an inference: it's a completion tag applied when a campaign finishes. And one correction: the awareness ladder had been inverted; it runs most-aware first, then down a level with an education step.

---

# Video Engine (elective)
*Tier B, from the May 20 session.*

**Added.** Elective with a money gate.
**How.** Installs, configures, runs, and improves the automated video pipeline in Claude Code. States the cost before anyone signs up (roughly one hundred to one hundred fifty dollars a month at one video a day). The member brings the zip. Keys live in one `.env` file and are never printed. Writes only the §1 tools line, one §13 row, and §8.
**Why.** "Whether you use this process or not is irrelevant. The skill set of doing it is really powerful": Claude Code as the orchestrator, APIs as the superglue.

---

# Second Brain (elective)
*Tier C, the June Obsidian month.*

**Added.** From weeks 1, 2, 4 and the office hours.
**How.** Install Obsidian and Claude Code on the same local folder, write a CLAUDE.md with the rules that matter, templates, a first fill through quality gates, then the routines: morning briefing, ask-your-brain, weekly synthesis, connection sweep, expert hats, saved commands. The starter layout was reconstructed from the founder's own vault, field names only. The Business File moves into the vault root.
**Why.** "Obsidian is the memory. Claude Code is the mind." The vault becomes the Build Room workspace.

---

# Source Watcher (elective)
*Tier C, the June 17 session.*

**Added.** The founder's Watcher Master, byte-identical from the public repo.
**How.** Pick a source (podcasts, YouTube, newsletters, RSS, Reddit, and more), let AI write the filters from your goals, generate a runnable watcher that only ever writes to an external folder. The Video-to-Vault YouTube skills come along. Interests are pre-filled from the file; delivery lands in a project folder in Claude Code or Codex.
**Why.** "If you have a source, regardless of that source, you can build a tool to grab the knowledge from that source." The brain grows without you.

---

# C-Suite Boardroom (elective)
*Tier C, the July 1 session.*

**Added.** The founder's plugin, five persona files untouched.
**How.** CEO, CFO, CMO, CSO argue from four genuinely different agendas; a chairperson forces the call and names the one condition that would flip it; then the member cross-examines. New: the Business File is the board pack, so the debate is about the member's real offer, avatar, funnel, and numbers, and the decision lands in the Build Plan.
**Why.** "The knowledge base comes first. Without it, it's generic fluffy BS." Now the board reads the file before anyone speaks.

---

# Compass (§17 Founder Compass)
*Tier C, the July 22 live test.*

**Added.** A new session and a new section.
**How.** Five sections, one question at a time, a reflection after every answer, an insight after every section, then the Compass delivered as a narrative ending in the Compass Statement. Then the compass is held against the business in the file and the next session named. §17 holds the statement, values, personality pattern, zone of genius, spark and drain zones, blind spots, unique truth, and communication style.
**Why.** Three skills used to ask for a pasted Compass. Now every session reads the member's voice and constraints from the file.

---

# Agent Forge (elective)
*Tier C, the July 29 preview.*

**Added.** The thirteen elements as a skill; the hosted app never reached members.
**How.** Basics, outcome, identity, context, knowledge and sources, memory, tools, workflow, boundaries, escalation, verification, metrics, review. Three ways in: scratch with defaults from the file, a template, or a plain description. A scrub-and-rebuild path for anything downloaded from a stranger. Output: one agent definition that installs as a skill or hands off as a build brief. §9 Go and Partial automation candidates are the best input.
**Why.** "You don't need to know any of these thirteen. Claude knows all thirteen and can build them for you."

---

# What stayed a note, on purpose

**Buzz (August 12).** A third-party demo with no Build Room artifact, unstable vendor onboarding, and the founder off the stock app within two weeks. Recorded in the roadmap with the reason.

**The Agent Forge app.** Never reached members; its checklist became the skill.

**The Blueprint.** Not rebuilt. Its business model already lives in §2 to §4 and its plan in §13, which matches the September switch to Discover and Design.

---

# The production pipeline

- **generate-skill.py** scaffolds a skill from any week's two curriculum files; every judgment point is marked for review. Proven on ten pairs.
- **build-skills.sh** syncs the protocol and template into every skill and refuses to package anything with an unresolved review marker.
- **build-universal-bundle.sh** produces the one zip for Claude Code, Codex, and Cowork.
- Every transcript-derived reference quotes the founder with timestamps and marks every reconstruction as an inference. No member or client names anywhere in the repository.

---

# What the test run found

Run end to end with AI Momentum Labs as the member. Offer Page Copy pre-filled nineteen of twenty-one inputs. The filled file was 829 words against a 2,500-word ceiling.

**Closed.** The verbatim bank couldn't tell real quotes from generated ones. Sourced and hypothesis banks with provenance fixed it.

**Still open.** Pre-fill at session three is low. The schema assumes one offer per business. The "never invent facts" rule sits awkwardly beside the avatar curriculum's specificity principle. The rating is collected before the output is used.

---

# Where it goes next

1. Apply the four open test-run findings.
2. Migrate the founder's own Business File to the seventeen-section schema.
3. Reissue the published roadmap to match what was actually delivered.
4. Keep the rhythm: every new Build Room week becomes a skill the same day, through the generator.

**One file. Every session reads it before asking you anything.**