# Build Room Program Map

The Build Room (AI Momentum Labs) is a monthly-theme, weekly-session program for service businesses, coaches, consultants, and agencies. Each session is a guided build with a Claude skill; every session reads and updates the member's **Build Room Business File**, so the work compounds.

## Sequences and sessions

### Foundation sequence — Offer Clarity & Positioning
Run in order. Everything else in the program stands on these.

| # | Session | Skill | Builds (file §) | Requires |
|---|---|---|---|---|
| 1 | Ideal Client Avatar | `buildroom-ideal-client-avatar` | §2 | — |
| 2 | Signature Offer | `buildroom-signature-offer` | §3 | §2 |
| 3 | Positioning & Messaging | `buildroom-positioning-messaging` | §4 | §2 §3 |
| 4 | Offer Page Copy | `buildroom-offer-page-copy` | §5 | §2 §3 §4 |

### Funnel sequence — Automation & Funnels
Run after the foundation (needs at least §2 and §3 to produce strong output).

| # | Session | Skill | Builds (file §) | Requires |
|---|---|---|---|---|
| 5 | Funnel Map & First Automation | `buildroom-funnel-map` | §6 | §1 (best with §2 §3) |
| 6 | Decision Machine (follow-up engine) | `buildroom-decision-machine` | §16 | §3 §6 (best with §2 §7) |
| 7 | Lead Capture System | `buildroom-lead-capture` | §7 | §6 |

### Lead Generation sequence — Lead Generation Engine
Run after the foundation (needs §1; every message gets sharper with §2 and §3). One skill, four modules, one session each, in order.

| # | Module | Skill | Builds (file §) | Requires |
|---|---|---|---|---|
| 1 | Warm Network Activation | `buildroom-leadgen` | §14 (provisional until all four run) | §1 (best with §2 §3) |
| 2 | The Outreach Machine | `buildroom-leadgen` | §14 | Module 1 |
| 3 | The Referral System | `buildroom-leadgen` | §14 | Module 1 |
| 4 | Content Lead Engine + Pipeline | `buildroom-leadgen` | §14 (complete) | Modules 1–3; reads §6 §7 |

### Sales sequence — Sales Conversations

| # | Session | Skill | Builds (file §) | Requires |
|---|---|---|---|---|
| 1 | Sales Conversations (script + role-play) | `buildroom-sales-script` | §15 | §3 (best with §2 §4) |

### Operations sequence — Operations & SOPs
Run after the foundation. Documents the business so it can be delegated.

| # | Session | Skill | Builds (file §) | Requires |
|---|---|---|---|---|
| 1 | SOP Creator System | `buildroom-sop-creator` | §9 | §1 |
| 2 | Hiring Ad + Interview Kit | `buildroom-hiring-kit` | §10 | §9 |
| 3 | Team Training Doc Builder | `buildroom-training-docs` | §11 | §9 §10 |
| 4 | Weekly Ops Dashboard | `buildroom-ops-dashboard` | §12 | §9 §11 |

### Anytime tools — Brainstorm to Build Plan
Not sequenced. Run whenever the member has an idea session to hold or one to capture.

| Session | Skill | Builds (file §) | Requires |
|---|---|---|---|
| Brainstorm Session (with the Brainstorm Board page) | `buildroom-brainstorm` | §13 (via Capture) | — (best with §1; uses §12 constraint and §13 parked items when present) |
| Brainstorm Capture | `buildroom-brainstorm-capture` | §13 | — |

Capture turns a raw brainstorm (board export, transcript, notes) into outcome records — proto-SOPs for process outcomes, build briefs for build outcomes — and Build Plan rows. A `captured` row with no next step for more than four weeks is a routing signal: recommend scheduling or parking it.

### Hardening passes and engines — run when the file says so
| Session | Skill | Writes | When to route here |
|---|---|---|---|
| Audience Insight | `buildroom-audience-insight` | §2 sourced language, pains, objections (with provenance) | §2 holds only `[hypothesis]` language, or the member has real client material they haven't used. Recommend before §5 or §7 ships. |
| Offer Deep Dive | `buildroom-offer-deep-dive` | §3 (belief, value stack, math, guarantee, urgency) | §3 is complete but sales are slow, price objections dominate, or the member is about to write the offer page. |
| Copy Engine | `buildroom-copy-engine` | §8 only (and a page status in §5/§7 on confirmation) | Any request to write or improve emails, ads, posts, pages, letters. Not a session; a tool that reads the whole file. |

### Electives
| Session | Skill | Notes |
|---|---|---|
| Video Engine | `buildroom-video-engine` | Install and run the automated video pipeline (Claude Code + HeyGen/Hedra + Pexels + fal.ai + FFmpeg + SubMagic). Elective with a money gate (~$100–325/mo); the durable lesson is Claude Code + APIs + a `.env` keys file. Reads §1/§2/§4; writes §1 tools, one §13 row, §8. |
| C-Suite Boardroom | `buildroom-boardroom` | The founder's C-Suite Boardroom: four executives who genuinely disagree plus a chairperson who forces the call. Reads the whole file as the board pack; writes one §13 row (the decision, with its flip condition as an open question) and §8. Route here for any decision the member is circling. |
| Source Watcher | `buildroom-source-watcher` | The founder's Watcher Master (Obsidian month, week 3): generates a watcher for any of eight source types with filters derived from the member's goals and hard-coded vault protection; the Video-to-Vault YouTube skills ride along. Standalone, or with a file: pre-fills interests from §1–§4/§12 and writes §1 tools, one §13 row, §8. Route here when the member wants their knowledge base to grow without them. |
| Second Brain | `buildroom-obsidian` | The Obsidian + Claude Code second brain (June month, weeks 1, 2 and 4): install, CLAUDE.md and templates, a gated first fill, routines and expert hats; the Business File moves into the vault root. Writes §1 tools, one §13 row, §8. Route here when a member says Claude keeps forgetting their business, or before any heavy knowledge work. |
| Compass | `buildroom-compass` (anytime, writes §17) | The founder's Compass: a one-question-at-a-time interview producing the personal clarity document (values, energy map, personality, zone of genius, blind spots, Compass Statement) into §17 Founder Compass. Requires nothing; redo when circumstances change. Route here first when a member says they feel misaligned, or before any copy session when §17 is empty. |

## Trigger phrases to hand the member

When routing, give the member the exact words to start the session:

- Ideal Client Avatar → "Help me build my ideal client avatar"
- Signature Offer → "Help me build my signature offer"
- Positioning & Messaging → "Help me position my business"
- Offer Page Copy → "Write my offer page"
- Funnel Map → "Help me map my funnel"
- Lead Capture → "Help me build my opt-in page"
- Decision Machine → "Build my follow-up system"
- SOP Creator → "Help me document my process"
- Hiring Kit → "Help me hire for this role"
- Training Docs → "Help me train my new hire"
- Ops Dashboard → "What numbers should I be watching every week?"
- Lead Gen Machine → "Help me get more leads" (the skill picks the module from §14)
- Sales Conversations → "Help me with my sales call"
- Audience Insight → "Find the words my clients actually use"
- Offer Deep Dive → "Make my offer a no-brainer"
- Copy Engine → "Write me [the piece]"
- Video Engine (elective) → "Set up the video engine"
- Compass (anytime) → "Build my compass"
- Second Brain (elective) → "Set up my second brain"
- Source Watcher (elective) → "Build me a source watcher"
- C-Suite Boardroom (elective) → "Convene the board"
- Brainstorm → "Let's brainstorm"
- Brainstorm Capture → "Capture what we decided"

## Themes on the 2026 roadmap (sessions arriving through the year)

Offer Clarity & Positioning · Lead Generation Engine · Sales Conversations · Content That Converts · Client Delivery Systems · Operations & SOPs · Automation & Funnels · Retention & Revenue Growth · Year-End Reset & 2027 Launch.

When a member asks for something no current skill covers (e.g. discovery call scripts, SOPs, retention), say it's on the roadmap, note it in their Session Log if they want, and route them to the most valuable session available *now* instead.

## Routing principles

1. **The file is the map.** Section statuses tell you exactly where the member is. Never make them re-explain their progress.
6. **Captured ideas are commitments waiting for a date.** If §13 has `captured` rows older than four weeks, mention it once: schedule it, park it, or ship it.
2. **One recommendation.** Members come confused; give them the single next session and why — not a menu.
3. **Goal-first routing.** "I want X" → find X's section, walk its `Requires` chain back to the first gap, and show the path: "Sales page needs avatar → offer → positioning. You have the avatar. Next: Signature Offer, then two sessions later you're writing the page."
4. **Hypothesis language is debt too.** If §2's sourced bank is empty and the member is heading for §5 or §7, route to Audience Insight first: a landing page built on guessed customer words ships guesses to real prospects.
4b. **Provisional debt counts as a gap.** A `provisional` section works, but flag it: the session that hardens it is usually worth running before building higher.
5. **Ship-state beats build-state.** If §5 or §7 says `draft` for weeks, the highest-value "next session" may be: publish what's built. Say so.
