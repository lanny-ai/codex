# NOTES.md: what this session knows about Build Room OS (written 2026-10-31 for Finish It)

## What it is

Build Room OS is the member toolkit for the Build Room, a program of guided weekly builds for service businesses, coaches, consultants and agencies run by AI Momentum Labs. Members are mostly owners aged 55 to 75 and non-technical. They unzip one folder, open Claude Code or Codex inside it, and say plain-English phrases ("Help me build my signature offer", "Get found on Google") to run skills. Every skill reads and updates one member-owned document, the Business File (`buildroom/templates/BUILDROOM_BUSINESS_FILE.md`, spec version 1.6, sections §1 to §21), following a shared protocol (`buildroom/shared/business-file-protocol.md`).

## Where it lives

- Everything is under `buildroom/` on branch `claude/new-session-1rmv4i`, which has been open as draft pull request #2 on lanny-ai/codex since August 2026 (103 commits, mergeable, no CI, no reviews, no comments). Main holds only the OS Cortex AEO Publisher plugin and the Control Center plugin.
- The PR description is the running changelog, sections 1 to 28, one per deliverable.
- Members get releases as dated zips in `buildroom/rollout/releases/` (current: `BuildRoom_OS_2026-10-28.zip`; previous: 2026-10-24). The README there gives the download pattern `https://github.com/lanny-ai/codex/raw/<branch>/buildroom/rollout/releases/<file>`, which today points at the branch. The owner posts the zip and the guides in the members' area (Mighty Networks) by hand.
- `buildroom/build-universal-bundle.sh` builds the zip (skills copied into `.claude/skills/` and `.codex/skills/`, tools, the Business File template, START-HERE, CLAUDE.md and AGENTS.md, the Say These Words PDF). `buildroom/build-skills.sh` syncs each skill's embedded copies of the protocol and template.

## What is done (all on the branch, all pushed)

- Thirty-two skills in `buildroom/skills/`, each with SKILL.md, references and, where needed, stdlib Python scripts. The newest: LinkedIn Engine (Oct 16), Event Launcher (Oct 17), Proof Engine (Oct 24), Search & Answer Engine (Oct 28, with a publish-and-index step added the same day).
- Test suites: `buildroom/tests/launch/run_tests.py` (394 checks), `buildroom/tests/linkedin/run_tests.py` (139), `buildroom/tests/search/run_tests.py` (191), `buildroom/tests/media/` (needs ffmpeg on PATH). All passed on 2026-10-28.
- Rollout material in `buildroom/rollout/`: the six-page Say These Words guide (HTML plus PDF), the eleven-page What's New guide for 2026-10-28 (`whats-new/`), Quick Start, One Pager, Business File Viewer, Brainstorm Board, Rent Calculator, MEMBER-README, FACILITATOR-RUN-OF-SHOW, `universal/` (START-HERE, CLAUDE.md, installers).
- Research behind the newest skills in `research_notes/` and `reports/` (confidential founder data removed; Amber Spears is never credited anywhere by the owner's instruction).
- PORTFOLIO.md (2026-10-31): Build Room OS is the one project being finished.

## What "finished" means (from the triage)

A last read-through, merge PR #2 to main, and the release links move off the branch. After that the weekly hand-off (posting the zip and guides) continues as the owner's routine.

## Open items the session knows about

- The release README's download pattern uses `<branch>`; once merged it should say `main`.
- The PR title and body were updated on 2026-10-28; the body ends with the required attribution footer.
- Two credentials sit in the owner's Obsidian vault (an AddEvent key, an HEI admin password); they are outside this repo and are the owner's to remove. Not part of this finish.
- The media test suite needs ffmpeg; the other three suites are stdlib only.
- Nothing in the repo may contain API keys, member or client names, or the founder's confidential numbers; the search, launch and LinkedIn suites include scans for this.

## Constraints the owner has set

- Develop only on `claude/new-session-1rmv4i`; never push to another branch without permission. Merging PR #2 into main is the finish, and is the owner's explicit decision from the triage.
- Commits carry the Claude attribution trailers; no model identifiers in commits or the PR.
- No keys in the repo; keys live in each member's `.env`, never printed.
- The brain repo (the owner's vault) is read-only when mounted; it is not mounted now.
