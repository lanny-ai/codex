# PROGRESS.md: finish Build Room OS

Started 2026-10-31. Phase A audit (STATE.md), Phase B goal (GOAL.md, LATER.md) and Phase C plan (PLAN.md) done. The builder appends one entry per milestone below.

## 2026-10-31, M1: wording and version fixes plus embedded-copy sync

Job: PLAN.md M1. Branch `claude/new-session-1rmv4i`, HEAD at start `4e8f6bf` (ground rules say `e7d355e`; one planning-files commit had landed since). PLAN.md carried a pending edit on lines 49 and 60 (a second first name removed from the plan text); it rides in this commit.

What changed (one line each, text confirmed with sed before editing):
1. `buildroom/rollout/releases/README.md` line 10: `raw/<branch>/` to `raw/main/`.
2. `buildroom/skills/buildroom-os/SKILL.md` line 29: progress view checklist `§14–§19` to `§14–§21`.
3. `buildroom/rollout/universal/CLAUDE.md` line 7: contents list now ends `advertising, video, launches and events, proof, search and answer presence (§1–§21`.
4. `buildroom/templates/BUILDROOM_BUSINESS_FILE.md` line 7: `**File version:** 1.6`.
5. `buildroom/BUSINESS-FILE-SPEC.md` line 75: `File version: 1.6` in its header (the spec version above).
6. `buildroom/rollout/Business_File_Viewer.html` line 340 (SAMPLE default): `**File version:** 1.6`.
7. `buildroom/rollout/Brainstorm_Board.html` line 128: `placeholder="Alex, Sam"`.
8. `buildroom/build-universal-bundle.sh` line 13: `two-page` to `six-page`.
9. `buildroom/README.md` line 48: Search & Answer Engine row gets its Requires cell (`§1 §2 (best §3 §4 §14 §18); Python 3 only, no packages, ffmpeg not needed`).
10. `buildroom/rollout/decks/2026-10-build-room-os-deck.md` line 181: `thirty-two skills`. Line 68 left as is per the plan.
11. Sync: `bash buildroom/build-skills.sh` from the repo root, 32 `built dist/<skill>.skill` lines plus `Done.`, exit 0. The 32 `buildroom/skills/*/references/business-file-template.md` copies picked up the 1.6 header. `git status --short` after the sync: 43 entries, the ten edited files, the 32 template copies and PLAN.md, nothing else.

Acceptance checks (expected, then actual):
- `grep -rn 'new-session-1rmv4i\|<branch>' buildroom --include=*.md`: expect nothing; actual nothing.
- `grep -c '§14–§21' buildroom/skills/buildroom-os/SKILL.md`: expect 1; actual 1. `grep -c '§14–§19' ...`: expect 0; actual 0.
- `grep -c 'search and answer presence (§1–§21' buildroom/rollout/universal/CLAUDE.md`: expect 1; actual 1.
- `grep -rn 'File version' buildroom --include=*.md --include=*.html | grep -v test-run | grep -vc '1\.6'`: expect 0; actual 0.
- `grep -c 'Alex, Sam' buildroom/rollout/Brainstorm_Board.html`: expect 1; actual 1. Grep for the second first name over buildroom: expect nothing; actual nothing.
- `grep -c 'six-page' buildroom/build-universal-bundle.sh`: expect 1; actual 1. `grep -c 'two-page' ...`: expect 0; actual 0.
- `sed -n 48p buildroom/README.md | awk -F'|' '{print NF-2}'`: expect 4; actual 4.
- `grep -c 'thirty-two skills' buildroom/rollout/decks/2026-10-build-room-os-deck.md`: expect 1; actual 1.
- cmp loop of the 32 embedded copies against the template, `| wc -l`: expect 0; actual 0. `ls ... | wc -l`: expect 32; actual 32.
- `bash -n buildroom/build-universal-bundle.sh && echo ok`: expect ok; actual ok.
- Em dash guard: `git diff -U0` removed lines carry 2 em dashes, added lines carry 2 (the pre-existing ones on SKILL.md line 29 and SPEC line 75); none added.

Suites, in order, after `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`:
- `python3 buildroom/tests/launch/run_tests.py`: 394/394 checks passed, exit 0.
- `python3 buildroom/tests/linkedin/run_tests.py`: 139/139 checks passed, exit 0.
- `python3 buildroom/tests/search/run_tests.py`: 191/191 passed, exit 0.
- `python3 buildroom/tests/media/run_tests.py`: 56/56 checks passed, exit 0.
- Then the `__pycache__` removal from the ground rules; `find buildroom -name __pycache__ | wc -l` prints 0.

Deferred: nothing from M1. The zip is not rebuilt here (M5). NOTES.md line 19 is M3. The media suite's `__pycache__` fix is M4.

## 2026-10-31, M2: redact the research note

Job: PLAN.md M2. Branch `claude/new-session-1rmv4i`, HEAD at start `fd41fe2`, working tree clean. File: `research_notes/World class event launches/lanny_vault_method.md`, read in full (374 lines, 7,557 words) before editing, then rewritten by hand section by section into a scratch copy and installed over the original (no blind search-and-replace). After: 356 lines, 7,511 words. The line count dropped by 18: the path-shorthand line and its blank (2), and the section 6 list of 17 bullets replaced by the one specified paragraph (16).

What changed:
- R1 figures: every founder figure is now a range word or plain word (list sizes, registrations, show-up counts, chat and session counts, buyer counts, revenue, lead cost, the planned and actual price ladders, the intensive's seat prices, refunds, frozen enrollments, projections, the integrity-breach amount). Exact percentages that state a lesson are rounded and prefixed "about"; the two plan-penalty percentages became "half again and well over double". Figures inside quotations are replaced in square brackets. Method counts, dates, years and run-of-show minute blocks are kept. Section 3 keeps its three tables and column headings; every Value cell is in words and every Source cell is `founder's notes`; two Label cells that said "prep doc" now say "the founder's notes" / "app log".
- R2 citations: line 3 is the specified sentence; the path-shorthand line is deleted; every backticked vault path, transcript timestamp, line reference, "audit §", "proof bank §", "planning brief §", "followup-redesign §", "strategy page", "prep doc", "same file" and "Sep 20 transcript" citation is `founder's notes`, at most once per sentence. Internal cross-references to this file's own sections (see §3, §4, §5) are kept. Section 6 keeps its heading and carries the one specified paragraph.
- R3 names: the promotion partner (personal name, company, two company abbreviations, product and program names, signature concepts), the two former seminar-business partners and their brand (including its two-letter abbreviation and the file-path abbreviation), the colleague's evergreen scripts, the real-estate author, the offer coach, the sales trainer, the client clinic, the three remaining personal names in paths, and the live access code are replaced by role words ("the promotion partner", "the partner's stage-selling IP", "two former seminar-business partners", "his earlier real-estate seminar business", "a real-estate author's evergreen funnel", "an offer coach", "a sales trainer's framework", "a client's funnel", "the live access code"). Kept: Lanny, Lanny Morton, AI Momentum Labs, the founder's own product and event names, Russell Brunson, Alex Hormozi, Joe Sugarman, Vistaprint. Existing `[name removed]` markers stay. Section 5's partner row loses the two partner catchphrases that were partner wording. One extra trim under the same rule: the founder's "personal health/AA disclosures" phrase in section 5 is now "personal disclosures".
- Headings: all 15 heading lines unchanged.

Acceptance checks (F = the file; expected, then actual):
- `grep -cE '\$[0-9]' "$F"`: expect 0; actual 0.
- `grep -oE '\b[0-9]{1,3}(,[0-9]{3})+\b|\b[1-9][0-9]{2,}\b' "$F" | grep -vE '^(19|20)[0-9]{2}$'`: expect nothing; actual nothing (0 lines).
- `grep -cE '`(PB|K|IT|ZT|FB|memory|knowledge)/|/home/user/brain' "$F"`: expect 0; actual 0.
- `grep -cE 'audit (§|Appendix)|proof bank §|planning brief §|followup-redesign §|strategy page|prep doc|[0-9]{2}:[0-9]{2}:[0-9]{2}' "$F"`: expect 0; actual 0.
- Names: case-insensitive `grep -ciE` with a pattern of 34 alternatives (first names, surnames, company names and abbreviations, product and program names, the access code, the second placeholder first name from STATE.md section 6, all whole-word where short), built from the names found in the file before editing and in STATE.md section 6; against the original file the same pattern matches 34 distinct tokens: expect 0; actual 0. The former seminar brand's two-letter abbreviation is also an English word, so it was checked case-sensitively as a whole word: the only hits are the words "SHOW-UP" and "FOLLOW UP" in two unchanged H3 headings; excluding those, 0.
- `grep -c '^#' "$F"`: expect 15; actual 15. `grep -c "founder's notes" "$F"`: expect 40 or more; actual 178.
- Em dash lines, `grep -c $'\xe2\x80\x94' "$F"`: before 9; after 8 (one line lost its em dash with the figure it sat in; none added).
- Re-read complete, no figure, path or partner name found.
- `git status --short` before commit: only the research note and PROGRESS.md.

Suite: `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`, then `python3 buildroom/tests/launch/run_tests.py`: 394/394 checks passed, exit 0.

Deferred: nothing from M2. The planning files' own names are M3.

## 2026-10-31, M3: root README pointer, NOTES.md instructor line, names out of the planning files

Job: PLAN.md M3. Branch `claude/new-session-1rmv4i`, HEAD at start `d01e12e`, working tree clean. Files: README.md (root), NOTES.md, STATE.md, GOAL.md, LATER.md, PORTFOLIO.md. Every target line was confirmed with sed before editing, and every occurrence of the three names was located first with a case-insensitive grep over the whole tree excluding .git (the instructor's surname, the second placeholder first name as a whole word, the partner-company abbreviation as a whole word). Edits were applied with exact one-per-line string replacements that assert the old text is present once.

What changed (10 hit lines edited plus one insertion; no name is repeated here):
1. README.md: the Build Room OS pointer line and a blank line inserted after the first paragraph's blank (new lines 5 and 6); `## Install` moved from line 5 to line 7.
2. NOTES.md line 19: now the specified sentence ("no third-party instructors are credited anywhere, by the owner's instruction"). NOTES.md line 30: the partner abbreviation before "admin password" is now "a partner campaign's".
3. STATE.md line 24: the instructor's quoted full name is now "The instructor's name" (sentence start). Line 52: the placeholder quote is now `"[two first names]"` and the parenthesis reads "(the second of them is a personal name, not the founder's)". Line 56: "partner campaign password". Line 72: "Keep the two first names as the Brainstorm Board placeholder?". Line 74: "single mention of the third-party instructor (the rule)".
4. GOAL.md line 77: the two grep literals are now `grep -rn '<second placeholder name>' buildroom` and `grep -rn '<instructor surname>' .`. This is the one edit to GOAL.md after approval; it changes no requirement, only the spelling of two literals that were themselves forbidden names.
5. LATER.md line 14: "(AddEvent key, a partner campaign's admin password)". PORTFOLIO.md line 16: "the testimonial admin password from the partner campaign note".
6. Not edited: five CSS hits in `buildroom/rollout/BuildRoom_OS_Say_These_Words.html` for a colour token (`--<colour>`) whose spelling matches the instructor's first name. It is a colour, not a credit, and is not the surname; the acceptance grep is for the surname.

Acceptance checks (expected, then actual):
- `sed -n '5p' README.md`: expect the Build Room OS line; actual `Build Room OS, the member toolkit for the Build Room (thirty-two skills for Claude Code and Codex), lives under [`buildroom/`](buildroom/README.md).`
- `sed -n '7p' README.md`: expect `## Install`; actual `## Install`. `grep -c 'buildroom/README.md' README.md`: expect 1; actual 1.
- `sed -n '19p' NOTES.md`: expect the specified line; actual matches it exactly. `grep -c 'no third-party instructors are credited anywhere' NOTES.md`: expect 1; actual 1.
- `grep -rniE '<surname>' . --exclude-dir=.git`, `grep -rniE '\b<placeholder name>\b' . --exclude-dir=.git`, `grep -rniE '\b<abbreviation>\b' . --exclude-dir=.git`: expect nothing from each; actual nothing from each (before editing: 3, 3 and 4 hit lines respectively, 10 distinct lines in all).
- `git grep -niE` for the same three patterns against HEAD after the commit: expect nothing; actual nothing from each (run on the M3 commit, then once more on the amended commit that folded this line in before the push).
- Em dash guard: `git diff -U0` removed lines carry 0 em dashes, added lines carry 0.
- Trailing newlines: the diff shows no "No newline at end of file" marker on any of the six files.
- `git status --short` before commit: README.md, NOTES.md, STATE.md, GOAL.md, LATER.md, PORTFOLIO.md and PROGRESS.md only.

Suite: `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`, then `python3 buildroom/tests/launch/run_tests.py`: 394/394 checks passed, exit 0. Sweep again afterwards; `find buildroom -name __pycache__ | wc -l` prints 0.

Deferred: nothing from M3. The media suite's `__pycache__` fix is M4; the zip rebuild is M5.

## 2026-10-31, M4: media suite leaves no __pycache__; order proof media then launch

Job: PLAN.md M4. Branch `claude/new-session-1rmv4i`, HEAD at start `452135d`, working tree clean. File: `buildroom/tests/media/run_tests.py` only. Each target spot was confirmed with sed and grep before editing (line 11 import line, `sh()` at line 31 with `env=None` passed straight to `subprocess.run`, the `env` dict at lines 42 to 45, the two-line `__main__` block at lines 305 to 306), and the four edits were applied as exact replacements that assert the old text is present once. `ROOT` in this file is `HERE.parents[1]`, which is `buildroom/` (HERE is `buildroom/tests/media`), so `ROOT.rglob("__pycache__")` covers the whole toolkit including `skills/buildroom-video-director/scripts/` and `tests/media/`; no other variable was needed. The launch suite's lines 10 to 12 were read and mirrored for edit 1.

What changed (306 lines before, 311 after):
1. Lines 11 to 13: `import sys`, then `sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folders or here)`, then the remaining imports (`json, os, shutil, subprocess, tempfile, threading`) with `# noqa: E402`. The in-process imports of `mock_providers`, `videolib` and `transcribe` no longer write `.pyc` files.
2. `sh()`: new first line `env = {**(env or os.environ), "PYTHONDONTWRITEBYTECODE": "1"}` before `subprocess.run`, so every subprocess the suite starts (ledger, gen, assemble, transcribe, review, submagic, node renderer) carries it whether the caller passed an env or not.
3. The `env` dict in `main()`: added `"PYTHONDONTWRITEBYTECODE": "1"` after `"FFMPEG": ffmpeg_bin()` (belt and braces).
4. `__main__` block: `try: rc = main()` / `finally:` remove every `__pycache__` under `ROOT` with `shutil.rmtree(d, ignore_errors=True)` / `sys.exit(rc)`. Behaviour of the suite is otherwise unchanged: same checks, same output lines, same exit code.

Acceptance checks (expected, then actual):
- `python3 -c "import ast,sys; ast.parse(open('buildroom/tests/media/run_tests.py').read()); print('parses')"`: expect `parses`; actual `parses`.
- `grep -c 'dont_write_bytecode' buildroom/tests/media/run_tests.py`: expect 1; actual 1. `grep -c 'PYTHONDONTWRITEBYTECODE' buildroom/tests/media/run_tests.py`: expect 2; actual 2.
- Order proof: `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`, `find buildroom -name __pycache__ | wc -l` prints 0 (clean start); `python3 buildroom/tests/media/run_tests.py; echo exit=$?` ends `56/56 checks passed` and `exit=0`, 0 FAIL lines; `find buildroom -name __pycache__ | wc -l` prints 0 (expect 0); then `python3 buildroom/tests/launch/run_tests.py; echo exit=$?` ends `394/394 checks passed` and `exit=0`. Before M4 this order failed the launch suite's last check.
- Em dash guard: `git diff -U0` added and removed lines carry 0 em dashes.
- `git status --short` before commit: ` M buildroom/tests/media/run_tests.py` only, then PROGRESS.md once this entry was written.

Suites (run after the order proof, nothing else moved):
- `python3 buildroom/tests/search/run_tests.py`: 191/191 passed, exit 0.
- `python3 buildroom/tests/linkedin/run_tests.py`: 139/139 checks passed, exit 0.
- `find buildroom -name __pycache__ | wc -l` afterwards: 0. The ground-rules sweep after the media suite is no longer needed.

Deferred: nothing from M4. The zip rebuild and full-suite run are M5.
