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
