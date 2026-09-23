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
| 6 | Decision Machine (follow-up sequence) | *coming — not yet a Business File skill* | — | §6 |
| 7 | Lead Capture System | `buildroom-lead-capture` | §7 | §6 |

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

### Electives
| Session | Skill | Notes |
|---|---|---|
| Source Watcher Generator | `buildroom-source-watcher` | Obsidian knowledge-base tooling. Standalone — does not read or write the Business File. |

## Trigger phrases to hand the member

When routing, give the member the exact words to start the session:

- Ideal Client Avatar → "Help me build my ideal client avatar"
- Signature Offer → "Help me build my signature offer"
- Positioning & Messaging → "Help me position my business"
- Offer Page Copy → "Write my offer page"
- Funnel Map → "Help me map my funnel"
- Lead Capture → "Help me build my opt-in page"
- SOP Creator → "Help me document my process"
- Hiring Kit → "Help me hire for this role"
- Training Docs → "Help me train my new hire"
- Ops Dashboard → "What numbers should I be watching every week?"
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
4. **Provisional debt counts as a gap.** A `provisional` section works, but flag it: the session that hardens it is usually worth running before building higher.
5. **Ship-state beats build-state.** If §5 or §7 says `draft` for weeks, the highest-value "next session" may be: publish what's built. Say so.
