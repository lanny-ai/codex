# Build Room — Skills Library

The Build Room's weekly automations as installable Claude Cowork skills, unified by the **Build Room Business File** — one member-owned document that every session reads at the start and updates at the end, so each week compounds on the last automatically instead of relying on the member to keep documents open beside them.

Start with [`BUSINESS-FILE-SPEC.md`](BUSINESS-FILE-SPEC.md) for the design, rules for authoring new weekly skills, and the section registry.

## Contents

| Path | What it is |
|---|---|
| `BUSINESS-FILE-SPEC.md` | The Business File design: schema authority, statuses, versioning, authoring rules. |
| `templates/BUILDROOM_BUSINESS_FILE.md` | The blank file members start from. |
| `shared/business-file-protocol.md` | The behavioral contract every skill embeds (canonical copy). |
| `skills/` | Skill sources. Each `references/knowledge-base.md` and `references/prompt-system.md` is a byte-identical copy of the week's original STEP1/STEP2 files. |
| `build-skills.sh` | Packages every skill into an installable `.skill` (a zip). |

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

`buildroom-lead-capture` is the retrofit of the previously shipped skill: its three original references are byte-identical; only the SKILL.md gained the Business File protocol. `buildroom-os` is the front door — it reads the file, shows progress, and routes the member to exactly one next session. `buildroom-source-watcher` (Obsidian tooling) remains standalone by design and does not touch the file.

## Build

```bash
bash build-skills.sh          # emits dist/*.skill
```

Install each `.skill` in Claude Cowork via **Settings → Skills → Upload Skill**. Members bring their Business File to every session; a member without one gets it created in their first session.
