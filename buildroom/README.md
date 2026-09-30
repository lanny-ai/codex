# Build Room — Skills Library

The Build Room's weekly automations as installable Claude Cowork skills, unified by the **Build Room Business File** — one member-owned document that every session reads at the start and updates at the end, so each week compounds on the last automatically instead of relying on the member to keep documents open beside them.

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
| `build-rollout-bundle.sh` | Packages the complete member install bundle (all skills + guides + blank file). |
| `build-universal-bundle.sh` | Packages `dist/BuildRoom_OS.zip`: one drag-and-drop folder for Claude Code (`.claude/skills/`), Codex (`.codex/skills/`), and Cowork (`cowork/*.skill`), with `CLAUDE.md`/`AGENTS.md`, optional global installers, the tools, and the Business File. Sources in `rollout/universal/`. |

## The skills (v1)

| Skill | Curriculum week | Writes | Requires |
|---|---|---|---|
| `buildroom-ideal-client-avatar` | Offer Clarity W1 | §2 | — |
| `buildroom-signature-offer` | Offer Clarity W2 | §3 | §2 |
| `buildroom-positioning-messaging` | Offer Clarity W3 | §4 | §2 §3 |
| `buildroom-offer-page-copy` | Offer Clarity W4 | §5 | §2 §3 §4 |
| `buildroom-funnel-map` | Automation & Funnels W1 | §6 | §1 (best with §2 §3) |
| `buildroom-lead-capture` | Automation & Funnels W3 (retrofit) | §7 | §6 |
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
| `buildroom-video-engine` | Elective (rebuilt from the May 20 session) | §1 tools, §13 row, §8 | — |
| `buildroom-boardroom` | Elective (the founder's C-Suite Boardroom plugin, rebuilt from the Jul 1 session; five persona files byte-identical) | §13 row, §8 | — |
| `buildroom-source-watcher` | Elective (the founder's Watcher Master generator, rebuilt from the Jun 17 session; generator skill and references byte-identical; Video-to-Vault skills included) | §1 tools, §13 row, §8 | — |
| `buildroom-obsidian` | Elective (the Obsidian + Claude Code month, rebuilt from the Jun 3/10/24 sessions and office hours) | §1 tools, §13 row, §8 | — |
| `buildroom-compass` | Anytime (the founder's Compass interview, rebuilt from the Jul 22 live test and the sessions that explain it) | §17, §13 row, §8 | — |
| `buildroom-agent-forge` | Elective (the founder's thirteen-element agent builder, rebuilt from the Jul 29 preview and bootcamp) | §13 row, §8 | — |
| `buildroom-brainstorm` | Anytime tool (with `rollout/Brainstorm_Board.html`) | §8, §13 last-brainstorm line | — |
| `buildroom-brainstorm-capture` | Anytime tool | §13 | — |

`buildroom-lead-capture` is the retrofit of the previously shipped skill: its three original references are byte-identical; only the SKILL.md gained the Business File protocol. `buildroom-os` is the front door — it reads the file, shows progress, and routes the member to exactly one next session. `buildroom-source-watcher` (the founder's Watcher Master, generator skill byte-identical) works standalone and, when a file is present, pre-fills its interests profile from it and writes a §1 tools line, one §13 row, and §8.

## Producing a new weekly skill

```bash
python3 generate-skill.py --step1 W1_Knowledge_Base.txt --step2 W1_Prompt_System.txt \
    --name buildroom-discovery-call --writes 9 --writes-label "Sales Conversations" --requires 2,3
```

The generator copies both curriculum files byte-for-byte into `references/`, parses the prompt titles, knowledge-base sections, and input-template fields, and writes a `SKILL.md` draft in the house pattern with every judgment point marked `TODO-REVIEW`. Then:

1. Resolve every `TODO-REVIEW` (the frontmatter description's trigger phrases matter most — that is what makes the skill fire).
2. For a new section number, register it: add the section to `templates/BUILDROOM_BUSINESS_FILE.md`, the spec's registry, and `buildroom-os/references/roadmap.md`.
3. `bash build-skills.sh` and test-drive the `.skill` in Cowork before shipping. Unresolved drafts are skipped with a warning, so a scaffold can never ship by accident.

This turns each remaining roadmap week into scaffold-and-review work: the writing that remains is exactly the writing that needs human judgment.

## Build

```bash
bash build-skills.sh            # emits dist/*.skill
bash build-rollout-bundle.sh    # emits dist/BuildRoom_OS_Complete_Install_Bundle.zip (skills + guides + blank file)
bash build-universal-bundle.sh  # emits dist/BuildRoom_OS.zip (Claude Code + Codex + Cowork, one folder)
```

Install each `.skill` in Claude Cowork via **Settings → Skills → Upload Skill**. Members bring their Business File to every session; a member without one gets it created in their first session.
