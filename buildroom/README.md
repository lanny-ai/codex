# Build Room — Skills Library

The Build Room's weekly automations as installable Claude Code and Codex skills, unified by the **Build Room Business File** — one member-owned document that every session reads at the start and updates at the end, so each week compounds on the last automatically instead of relying on the member to keep documents open beside them.

Start with [`BUSINESS-FILE-SPEC.md`](BUSINESS-FILE-SPEC.md) for the design, rules for authoring new weekly skills, and the section registry.

## Contents

| Path | What it is |
|---|---|
| `BUSINESS-FILE-SPEC.md` | The Business File design: schema authority, statuses, versioning, authoring rules. |
| `templates/BUILDROOM_BUSINESS_FILE.md` | The blank file members start from. |
| `shared/business-file-protocol.md` | The behavioral contract every skill embeds (canonical copy). |
| `curriculum/` | Raw STEP1/STEP2 curriculum pairs authored here, before packaging. |
| `skills/` | Skill sources. Each `references/knowledge-base.md` and `references/prompt-system.md` is a byte-identical copy of the week's original STEP1/STEP2 files. |
| `build-skills.sh` | Packages every skill into an installable `.skill` (a zip). Refuses to package drafts with unresolved `TODO-REVIEW` markers. |
| `generate-skill.py` | Scaffolds a new weekly skill from a raw STEP1/STEP2 curriculum pair. |
| `rollout/` | Member-facing launch assets: Quick Start HTML, the Rent Calculator (September W1 giveaway; exports a §9 block), the Build Room OS one-pager, member README, facilitator run-of-show. |
| `build-universal-bundle.sh` | Packages `dist/BuildRoom_OS.zip`: one drag-and-drop folder for Claude Code (`.claude/skills/`) and Codex (`.codex/skills/`), with `CLAUDE.md`/`AGENTS.md`, optional global installers, the tools, and the Business File. Sources in `rollout/universal/`. |

## The skills (v1)

| Skill | Curriculum week | Writes | Requires |
|---|---|---|---|
| `buildroom-ideal-client-avatar` | Offer Clarity W1 | §2 | — |
| `buildroom-signature-offer` | Offer Clarity W2 | §3 | §2 |
| `buildroom-positioning-messaging` | Offer Clarity W3 | §4 | §2 §3 |
| `buildroom-offer-page-copy` | Offer Clarity W4 | §5 | §2 §3 §4 |
| `buildroom-funnel-map` | Automation & Funnels W1 (+ Traffic Strategy and Build it in GHL phases, 2026-10-10) | §6 (incl. traffic strategy and CRM build lines) | §1 (best with §2 §3) |
| `buildroom-lead-capture` | Automation & Funnels W3 (retrofit + application builder, 2026-10-10) | §7 (incl. application line) | §6 |
| `buildroom-os` | — (program navigator) | §1, §8 only | — |
| `buildroom-sop-creator` | Operations & SOPs W1 | §9 | §1 |
| `buildroom-hiring-kit` | Operations & SOPs W2 | §10 | §9 |
| `buildroom-training-docs` | Operations & SOPs W3 | §11 | §9 §10 |
| `buildroom-ops-dashboard` | Operations & SOPs W4 | §12 | §9 §11 |
| *(tool)* `rollout/Business_File_Viewer.html` | Anytime tool | reads the whole file, writes nothing | — |
| `buildroom-decision-machine` | Automation & Funnels W2 (rebuilt from the Apr 15/22, May 27, Aug 5 sessions) | §16 | §3 §6 |
| `buildroom-leadgen` | Lead Generation Engine (4 modules, retrofit of the Lead Gen Machine) | §14 | §1 (best §2 §3) |
| `buildroom-sales-script` | Sales Conversations (retrofit of the Sales Coach) | §15 | §3 (best §2 §4) |
| `buildroom-audience-insight` | Hardening pass (retrofit of the Audience Insight Playbook) | §2 sourced language, with provenance | §1 |
| `buildroom-offer-deep-dive` | Hardening pass (retrofit of the Million-Dollar Offer Maker) | §3 | best §3 §2 |
| `buildroom-copy-engine` | Copy tool (Kern + Halbert) | §8 only | best §2 §3 |
| `buildroom-ad-studio` | Advertising (2026-10-14): brief → matrix → three concepts → copy → statics in three ratios → review → launch kit; paid generation through the shared ledger | §18, §13 rows | §2 §3 (best §4 §7) |
| `buildroom-video-director` | Video (2026-10-14): one director, four playbooks (ad, content, sales, proof), real footage first, generated B-roll through the ledger, SubMagic or burned captions, separate review, kit; the Video Engine elective folded in as volume mode | §19; §18 proof vault, §14 content, §5/§15 references, §13 rows | §1 §2 (best §3 §4 §17) |
| `buildroom-boardroom` | Elective (the founder's C-Suite Boardroom plugin, rebuilt from the Jul 1 session; five persona files byte-identical) | §13 row, §8 | — |
| `buildroom-linkedin` | LinkedIn Engine (2026-10-16): organic LinkedIn pipeline built on October 2026 research (interest-based feed, formats, comment-first daily routine, warm-signal DMs, account safety); profile, pillars, voice-first posts, carousel and banner renderer, pipeline tracker, analytics scorecard; the member acts by hand | §14 LinkedIn lines, §13 rows, §8 | §1 §2 (best §3 §4 §5) |
| `buildroom-proof-engine` | Proof Engine (2026-10-24): the founder's case-study loop (trigger, capture, file, deploy), the 3-question interview, permission states, proof classes A–E/H/X/R/U, honesty rules, placement rules per tool | §18 proof vault and never-say, §19 testimonials count, §13 rows, §8 | §1 (best §3) |
| `buildroom-search-answer-engine` | Search & Answer Engine (2026-10-28): found and cited in Google, Maps, YouTube and AI answers without ads, on October 2026 research (five notes, one report) and the founder's OS Cortex AEO method; Business Profile scoring (rank vs buyer items), a rated question map, the answer-page gate (two page kinds, claim ledger, typical result, scope note), the review loop under Google's policy and the FTC rule, five free listings, YouTube briefs, a monthly citation check; five scripts (map, gate, profile, citation check, publish and index), 191 tests | §21, one §14 channel row, §18 review count, §13 rows, §8 | §1 §2 (best §3 §4 §14 §18); Python 3 only, no packages, ffmpeg not needed |
| `buildroom-event-launcher` | Event Launcher (2026-10-17): live launch events (3-day bootcamp, 5-day challenge, workshop, webinar, founding-member launch) on the founder's boot camp method, partner-launch practice and October 2026 research; launch math, belief-first emails, calendar files, run-of-show, the close, a launch gate, follow-up by stage, debrief to the member's Obsidian vault | §20, §13 rows, §8 | §1 §2 §3 (best §4 §6 §16 §17) |
| `buildroom-source-watcher` | Elective (the founder's Watcher Master generator, rebuilt from the Jun 17 session; generator skill and references byte-identical; Video-to-Vault skills included) | §1 tools, §13 row, §8 | — |
| `buildroom-obsidian` | Elective (the Obsidian + Claude Code month, rebuilt from the Jun 3/10/24 sessions and office hours) | §1 tools, §13 row, §8 | — |
| `buildroom-compass` | Anytime (the founder's Compass interview, rebuilt from the Jul 22 live test and the sessions that explain it) | §17, §13 row, §8 | — |
| `buildroom-agent-forge` | Elective (the founder's thirteen-element agent builder, rebuilt from the Jul 29 preview and bootcamp) | §13 row, §8 | — |
| `buildroom-discovery-engine` | The Magic Business Genie rebuilt: research first, confirm, scripted gaps, then the ten Genie prompts; own business, client, or prospect | §1–§4 provisional, §13; client file; prospect brief | — |
| `buildroom-funnel-scorecard` | Automation & Funnels W4 (the founder's recurring funnel test, from the Sep 10/16 sessions) | §6 lines, §13 rows, §12 rows | — |
| `buildroom-brainstorm` | Anytime tool (with `rollout/Brainstorm_Board.html`) | §8, §13 last-brainstorm line | — |
| `buildroom-brainstorm-capture` | Anytime tool | §13 | — |

`buildroom-lead-capture` is the retrofit of the previously shipped skill: its three original references are byte-identical; the SKILL.md gained the Business File protocol and, later, the application-builder branch (`references/application-builder.md`, the Build Lab loop with the founder's Codex Prompt Library prompts 1, 2, 3, 12, 13). `buildroom-os` is the front door — it reads the file, shows progress, and routes the member to exactly one next session. `buildroom-source-watcher` (the founder's Watcher Master, generator skill byte-identical) works standalone and, when a file is present, pre-fills its interests profile from it and writes a §1 tools line, one §13 row, and §8.

## Producing a new weekly skill

```bash
python3 generate-skill.py --step1 W1_Knowledge_Base.txt --step2 W1_Prompt_System.txt \
    --name buildroom-discovery-call --writes 9 --writes-label "Sales Conversations" --requires 2,3
```

The generator copies both curriculum files byte-for-byte into `references/`, parses the prompt titles, knowledge-base sections, and input-template fields, and writes a `SKILL.md` draft in the house pattern with every judgment point marked `TODO-REVIEW`. Then:

1. Resolve every `TODO-REVIEW` (the frontmatter description's trigger phrases matter most — that is what makes the skill fire).
2. For a new section number, register it: add the section to `templates/BUILDROOM_BUSINESS_FILE.md`, the spec's registry, and `buildroom-os/references/roadmap.md`.
3. `bash build-skills.sh` (syncs the protocol and template into every skill) and test-drive the skill in Claude Code or Codex before shipping. Unresolved drafts are skipped with a warning, so a scaffold can never ship by accident.

This turns each remaining roadmap week into scaffold-and-review work: the writing that remains is exactly the writing that needs human judgment.

## Build

```bash
bash build-skills.sh            # syncs protocol + template into every skill; emits dist/*.skill (zips, for inspection)
bash build-universal-bundle.sh  # emits dist/BuildRoom_OS.zip (Claude Code + Codex, one folder)
```

Members unzip `BuildRoom_OS.zip` and open Claude Code or Codex in the folder; the skills load on their own and read and write the Business File in place. A member without one gets it created in their first session. Cowork is not a supported path.
