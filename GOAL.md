# GOAL.md: finish Build Room OS (2026-10-31)

## Goal

Take Build Room OS from an open draft pull request to merged on `main`, with the release download link pointing at `main`, the 2026-10-28 release zip matching its sources, the public repo free of founder figures and extra personal names, and the test suites passing in any order.

## Business Outcome

Members download the toolkit from a link that never changes again. The owner's weekly hand-off (post the zip and the two guides) continues from `main` instead of a working branch. The repository can be read by anyone without exposing the founder's confidential numbers.

## Project Context

Existing application. Everything below already works and must not be rebuilt (STATE.md section 2):

- 32 skills under `buildroom/skills/`, each with SKILL.md, references and stdlib Python scripts where needed. Embedded copies of the Business File protocol and template are byte-identical to `buildroom/shared/` and `buildroom/templates/` (32 of 32).
- Four test suites, all green on 2026-10-31: launch 394, LinkedIn 139, search 191, media 56 (media needs ffmpeg).
- Release `buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`, built by `buildroom/build-universal-bundle.sh`, byte-identical to `buildroom/dist/BuildRoom_OS.zip`, contents matching HEAD.
- Rollout material under `buildroom/rollout/`: Say These Words guide (6 pages), What's New 2026-10-28 (11 pages), START-HERE, universal CLAUDE.md and AGENTS.md, Viewer, Brainstorm Board, Rent Calculator, installers.
- PR #2 on lanny-ai/codex: open, draft, base `main`, head `9326d24`, mergeable with no conflicts, 105 commits. `main` carries one commit the branch lacks (`1d80d57`, Control Center plugin); the merge-tree is clean.
- The repo is public. The root README describes OS Cortex AEO Publisher only.

## Deliverables

1. Read-through fixes on the branch (one or two commits).
2. The 2026-10-28 zip rebuilt from the fixed sources and recommitted under the same name.
3. A redacted `research_notes/World class event launches/lanny_vault_method.md`.
4. PR #2 body with corrected headings and the current attribution footer, marked ready for review.
5. PR #2 merged into `main` with a merge commit.
6. A confirmed download from `https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`.

## Functional Requirements

Owner decisions from STATE.md section 8, all settled on 2026-10-31:

- Q1 merge commit. Q2 fix and rebuild the zip now. Q3 template header reads `File version: 1.6` (Viewer default too). Q4 redact founder figures and vault paths. Q5 neutral placeholder names on the Brainstorm Board. Q6 commit trailers are exempt from the no-model-identifier rule. Q7 remove the instructor's name from NOTES.md, keep the rule in neutral words. Q8 one root README line pointing to `buildroom/`. Q9 START-HERE replaced MEMBER-README; zip contents unchanged. Q10 and Q12 fix the PR body headings and footer. Q11 keep `buildroom/test-run/`. Q13 fix the test-order dependency before merge.

Edits, in detail:

- `buildroom/rollout/releases/README.md`: the download pattern uses `main` in place of `<branch>`.
- `buildroom/skills/buildroom-os/SKILL.md`, Case 1 progress view: the checklist covers §2–§7, §9–§12 and §14–§21.
- `buildroom/rollout/universal/CLAUDE.md` line 3: the list of the file's contents ends with proof and search-and-answer presence so it matches "§1–§21".
- `buildroom/templates/BUILDROOM_BUSINESS_FILE.md` header and the example header, and `buildroom/rollout/Business_File_Viewer.html` default: `File version: 1.6`. Then sync the 32 embedded template copies with `buildroom/build-skills.sh` (or `cp`), and confirm with `cmp`.
- `buildroom/rollout/Brainstorm_Board.html` line 128: placeholder becomes two neutral first names, for example `Alex, Sam`.
- `buildroom/build-universal-bundle.sh` header: "two-page" becomes "six-page". `buildroom/README.md`: the Search & Answer Engine row gets its Requires cell (Python 3, no packages; ffmpeg not needed). `buildroom/rollout/decks/2026-10-build-room-os-deck.md`: "twenty-six skills" becomes "thirty-two skills".
- `NOTES.md` line 19: reword to "no third-party instructors are credited anywhere" so no instructor's name appears.
- `research_notes/World class event launches/lanny_vault_method.md`: replace every founder figure with a range or a word (buyer counts, list sizes, registration and attendance counts, revenue and booked figures, refund counts, the integrity-breach amounts, frozen enrollment counts, lead cost, the planned and actual price ladders with their prices); remove every vault file path citation (the backticked `PB/`, `K/`, `IT/`, `ZT/`, `FB/`, `memory/`, audit section references) and replace with "founder's notes"; keep the method, the lesson headings and the generic direct-response material. No partner, staff, attendee or client name remains. The prices in the Say These Words and What's New guides are not touched (they contain none).
- Root `README.md`: one line, after the first paragraph, saying Build Room OS lives under `buildroom/` with a link to `buildroom/README.md`.
- Test-order dependency: `buildroom/tests/media/run_tests.py` must leave no `__pycache__` under `buildroom/` when it exits (set `PYTHONDONTWRITEBYTECODE=1` in the env of every subprocess it starts, and remove any `__pycache__` it still created in a `finally`). Verify by running media then launch.
- PR #2 body: heading 3 reads "Thirty-two skills" (or the count the heading's own text gives, corrected), heading 17 names Video Director in place of `buildroom-video-engine`; footer replaced by the current attribution block. Title unchanged. The body is edited with `gh api -X PATCH repos/lanny-ai/codex/pulls/2 --input <json>` from a file in the scratchpad.

## Technical Requirements

- Python 3 stdlib only in `buildroom/`; no new dependencies.
- The zip is rebuilt with `buildroom/build-universal-bundle.sh` from the repo root (it writes `buildroom/dist/BuildRoom_OS.zip`), then copied over `buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`. After the build, `diff -rq` of the zip's `skills/` against `buildroom/skills/` is empty and `cmp` of the zip's CLAUDE.md, template and PDF against their sources passes.
- Commits use `git -c user.name="Claude" -c user.email="lanny@aimomentumlabs.com" commit` and end with the two attribution trailers in use on this branch. No model identifier anywhere in commit subjects, bodies, the PR title or body, code or comments; the trailers are exempt.
- Push with `git push -u origin claude/new-session-1rmv4i`. Never push to any other branch. The merge into `main` happens through the PR (merge commit), not by a local push to `main`.
- `gh` is at `/usr/local/bin/gh` and authenticated; GitHub MCP tools are the alternative.

## Constraints

- Do not change working features listed in STATE.md section 2 unless a Definition of Done item requires it.
- Scope only goes down. Anything in LATER.md stays out.
- No API keys, tokens, member or client names, or the founder's confidential numbers anywhere in the repo. Test accounts and sandbox data only; no real purchases, messages or deletions; no secrets in code.
- Never two builders at once. Never em dashes in files written for this finish.
- The merge is the one irreversible step. It is the owner's decision from the triage and is authorized; everything before it is confirmed green first.
- The owner's Obsidian vault is not mounted and is out of scope.

## Autonomous Execution Instructions

Work milestone by milestone from PLAN.md. After every edit batch run the four suites (`python3 buildroom/tests/launch/run_tests.py`, `linkedin`, `search`, `media`, then launch again after media to prove the order fix). Rebuild the zip only once, after every source edit is done. Re-read the redacted research note end to end and grep it for `\$[0-9]`, four-digit counts and the path prefixes before calling it done. Record each step in PROGRESS.md. Stop only for a true external blocker (for example GitHub refusing the merge) and say exactly what is needed.

## Validation

- All four suites exit 0, in the order launch, linkedin, search, media, launch.
- `unzip -l` of the release shows 32 skill folders under both `.claude/skills/` and `.codex/skills/`; `cmp` of the committed zip against `buildroom/dist/BuildRoom_OS.zip` is silent.
- `grep -rn 'new-session-1rmv4i\|<branch>' buildroom --include=*.md` returns nothing.
- `grep -rn 'Haley' buildroom` and `grep -rn 'Amber' .` return nothing (excluding `.git`).
- The redacted note has no dollar figure, no count above 99, and no backticked vault path.
- `gh api repos/lanny-ai/codex/pulls/2` shows `draft: false` before the merge and `merged: true` after.
- `curl -sIL https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip` ends in a 200 with a zip content type.

## Definition of Done

1. Release README download pattern says `main`.
2. buildroom-os progress view lists §14–§21; universal CLAUDE.md line 3 names all 21 sections' topics.
3. Template and Viewer say `File version: 1.6`; all 32 embedded copies match the template.
4. Brainstorm Board placeholder holds neutral names.
5. Bundle script header, buildroom README Requires cell, deck skill count and NOTES.md instructor line corrected.
6. Research note redacted as specified and re-read.
7. Root README points to `buildroom/`.
8. Media suite leaves no `__pycache__`; launch passes after media.
9. 2026-10-28 zip rebuilt, matches sources, committed; all four suites green; branch pushed.
10. PR #2 body headings and footer fixed; PR marked ready for review.
11. PR #2 merged into `main` with a merge commit.
12. Ship: the raw `main` download link returns the zip, and the owner is told the link to post in the Members' area.
