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

## Themes on the 2026 roadmap (sessions arriving through the year)

Offer Clarity & Positioning · Lead Generation Engine · Sales Conversations · Content That Converts · Client Delivery Systems · Operations & SOPs · Automation & Funnels · Retention & Revenue Growth · Year-End Reset & 2027 Launch.

When a member asks for something no current skill covers (e.g. discovery call scripts, SOPs, retention), say it's on the roadmap, note it in their Session Log if they want, and route them to the most valuable session available *now* instead.

## Routing principles

1. **The file is the map.** Section statuses tell you exactly where the member is. Never make them re-explain their progress.
2. **One recommendation.** Members come confused; give them the single next session and why — not a menu.
3. **Goal-first routing.** "I want X" → find X's section, walk its `Requires` chain back to the first gap, and show the path: "Sales page needs avatar → offer → positioning. You have the avatar. Next: Signature Offer, then two sessions later you're writing the page."
4. **Provisional debt counts as a gap.** A `provisional` section works, but flag it: the session that hardens it is usually worth running before building higher.
5. **Ship-state beats build-state.** If §5 or §7 says `draft` for weeks, the highest-value "next session" may be: publish what's built. Say so.
