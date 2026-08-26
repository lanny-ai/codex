# Build Room Business File — Specification

**Version 1.0 · 2026-08-26**

## Why this exists

The Build Room's compounding promise ("every ZIP builds on the last") is currently enforced by member discipline: each week's prompt system opens with a checklist — *"ICA Document from Week 1 open beside you?"* — and the member is the integration layer. If they lose a document, skip a week, or paste a stale version, the compounding breaks silently.

The Business File moves that discipline into the skills. It is **one markdown document per member** that every Build Room skill reads at session start and updates at session end. By month three, a session opens already knowing the member's ICA, offer, positioning, price, and metrics — and asks only what is genuinely new.

## Design principles

1. **One file, member-owned, plain markdown.** No app, no database, no lock-in. It lives with the member's documents; they can read and edit every line.
2. **Distillation, not archive.** The file carries decisions and key verbatims (~2,500-word ceiling). Full deliverables live in their own documents, referenced by name. This keeps the file paste-able into any session forever.
3. **The schema is the curriculum's own dependency graph.** Section fields were derived directly from the April W4 input template — the week that consumes everything W1–W3 produced — plus each week's own input template. The proof of correctness: April W4 can pre-fill its entire input template from a completed file.
4. **Statuses make trust visible.** Every section carries `not started / provisional / complete` with a date and the skill that wrote it. Work built on a provisional foundation inherits the flag, so members always know which outputs are load-bearing.
5. **Member edits are authoritative.** Skills never overwrite hand edits silently and never write unconfirmed facts.

## The artifacts

| File | Role |
|---|---|
| `templates/BUILDROOM_BUSINESS_FILE.md` | The blank file members start from. Canonical schema. |
| `shared/business-file-protocol.md` | The behavioral contract every skill embeds (read/write/conflict/size rules). |
| `skills/*/references/business-file-{template,protocol}.md` | Per-skill embedded copies (skills are standalone installers; `build-skills.sh` syncs them from the canonical sources). |

## Section registry (v1.0)

| § | Section | Written by | Requires |
|---|---|---|---|
| 1 | Business Snapshot | any session (opportunistic) | — |
| 2 | Ideal Client Avatar | Ideal Client Avatar | — |
| 3 | Signature Offer | Signature Offer | §2 |
| 4 | Positioning & Messaging | Positioning & Messaging | §2, §3 |
| 5 | Offer Page | Offer Page Copy | §2, §3, §4 |
| 6 | Funnel & Automation | Funnel Map | §1 (better with §2, §3) |
| 7 | Lead Capture | Lead Capture | §6 |
| 8 | Session Log | every session (append-only) | — |

Future months extend the registry by **adding sections** (e.g. §9 Sales Conversations, §10 Content System) — never by restructuring existing ones. A skill built against v1.0 must still parse a v1.x file.

## Rules for authoring new Build Room skills

Every new weekly skill MUST:

1. Ship `business-file-protocol.md` and `business-file-template.md` in its `references/` and follow the protocol verbatim.
2. Declare its prerequisites (by section number) in its SKILL.md and implement the two-path fallback (run prerequisite / provisional interview).
3. Map its input template onto file sections: pre-fill what exists, confirm once, ask only the gaps.
4. End by emitting the full updated file + a Session Log row with the member's 1–5 rating.
5. Keep its writes inside its registered sections plus §1 and §8.

## Versioning

The file carries `File version: 1.0` in its header. Additive changes (new sections, new fields) bump the minor version and require no migration. Skills treat unknown sections as opaque and preserve them byte-for-byte on rewrite — this is what lets a member's file move safely between skill generations.
