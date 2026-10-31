# PLAN.md: finish Build Room OS (2026-10-31)

Planner output for GOAL.md. Builder works top to bottom, one milestone per sitting, and appends an entry to PROGRESS.md after every step. Never edit GOAL.md (one exception, recorded in M3: a grep literal that is itself a forbidden name).

## Approach

Six small milestones close the gap between STATE.md section 2 (everything green, PR #2 open as a clean draft) and GOAL.md's Definition of Done. No new technology: stdlib Python 3.11, bash, zip and unzip, curl, and `gh` at /usr/local/bin/gh (GitHub MCP tools as the fallback). Milestones 1 to 4 are source edits, each verified by greps with exact expected output and by the four test suites, each ending in its own commit so the repo is working after every sitting. Milestone 5 rebuilds the release zip exactly once, after every source edit is in, verifies the zip against its sources, runs the suites in the order launch, linkedin, search, media, launch, commits and pushes. Milestone 6 edits the PR body, marks the PR ready, merges with a merge commit, and confirms the raw `main` download link. Scope only goes down; everything in LATER.md stays out.

## Ground rules for every milestone

- Repo: /home/user/codex, branch `claude/new-session-1rmv4i`, HEAD at start `e7d355e` (= origin; `9326d24` plus the planning-files commit). Remote `origin` = https://github.com/lanny-ai/codex. Run every command from /home/user/codex.
- Scratch: /tmp/claude-0/-home-user-codex/650431e5-549c-52b2-b9b8-8dea9cc5f48e/scratchpad (called SCRATCH below). Nothing written there is committed.
- Planning files STATE.md, GOAL.md, LATER.md, PLAN.md, PROGRESS.md are tracked (the session's stop hook requires every file committed). STATE.md, GOAL.md, LATER.md, PORTFOLIO.md and NOTES.md carry names that must not reach main; M3 redacts them. PLAN.md and PROGRESS.md are committed with each milestone's commit. Always `git add` explicit paths, never `git add -A` or `git add .`.
- Commit command, every time:
  `git -c user.name="Claude" -c user.email="lanny@aimomentumlabs.com" commit -F SCRATCH/msg-mN.txt`
  where the message file ends with exactly these two trailers after a blank line:
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01GafcQSGHpsWJowL4fXkLgX`
  No model identifier in any subject or body outside those trailers. No em dashes in anything written for this finish (existing em dashes in files are left as they are).
- Push after every milestone's commit with `git push -u origin claude/new-session-1rmv4i`. Never push to any other branch. `main` changes only through the PR merge in M6.
- Suites: `python3 buildroom/tests/launch/run_tests.py` (expect `394/394 checks passed`, exit 0), `python3 buildroom/tests/linkedin/run_tests.py` (139/139), `python3 buildroom/tests/search/run_tests.py` (191/191), `python3 buildroom/tests/media/run_tests.py` (56/56; ffmpeg is at /usr/bin/ffmpeg). Check exit codes with `echo exit=$?`. Until M4 lands, the media suite leaves `__pycache__` folders behind, so in M1 to M3 run launch before media and afterwards run `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`.
- `buildroom/build-universal-bundle.sh` does `cd` to its own folder, then calls `build-skills.sh dist`, which copies `shared/business-file-protocol.md` and `templates/BUILDROOM_BUSINESS_FILE.md` into every one of the 32 skill folders, removes `__pycache__` under skills/, and writes `.skill` zips into `buildroom/dist/` (git-ignored). Run it from the repo root as `bash buildroom/build-universal-bundle.sh`; it writes `buildroom/dist/BuildRoom_OS.zip`. After any run of either script, check `git status --short` for changes you did not intend.
- Never two builders at once. The merge in M6 is the one irreversible step; everything before it must be green first.

## M1: wording and version fixes plus embedded-copy sync

Delivers: Definition of Done items 1 to 5 (except the NOTES.md line, which is M3) in the sources, the 32 embedded template copies synced, all suites green.

Files touched:
- buildroom/rollout/releases/README.md (line 10)
- buildroom/skills/buildroom-os/SKILL.md (line 29)
- buildroom/rollout/universal/CLAUDE.md (line 7; GOAL.md calls it line 3, the contents list is on line 7)
- buildroom/templates/BUILDROOM_BUSINESS_FILE.md (line 7)
- buildroom/BUSINESS-FILE-SPEC.md (line 75, the spec's own statement of the header)
- buildroom/rollout/Business_File_Viewer.html (line 340, the SAMPLE default)
- buildroom/rollout/Brainstorm_Board.html (line 128)
- buildroom/build-universal-bundle.sh (line 13)
- buildroom/README.md (line 48)
- buildroom/rollout/decks/2026-10-build-room-os-deck.md (line 181)
- buildroom/skills/*/references/business-file-template.md (32 files, written by build-skills.sh)

Edits, exact:
1. releases/README.md line 10: replace `raw/<branch>/` with `raw/main/`. Result: `Download link pattern: \`https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/<file>\`.`
2. buildroom-os/SKILL.md line 29: replace `§2–§7, §9–§12, and §14–§19` with `§2–§7, §9–§12, and §14–§21`. Nothing else on the line changes.
3. universal/CLAUDE.md line 7: replace `advertising, video (§1–§21` with `advertising, video, launches and events, proof, search and answer presence (§1–§21`. The search suite requires `§1–§21` to remain in this file.
4. templates/BUILDROOM_BUSINESS_FILE.md line 7: `**File version:** 1.0` becomes `**File version:** 1.6`.
5. BUSINESS-FILE-SPEC.md line 75: `The file carries \`File version: 1.0\` in its header.` becomes `The file carries \`File version: 1.6\` in its header (the spec version above).` Rest of the line unchanged.
6. Business_File_Viewer.html line 340: `**File version:** 1.0` becomes `**File version:** 1.6`.
7. Brainstorm_Board.html line 128: the `placeholder` attribute (the founder's first name and a second first name) becomes `placeholder="Alex, Sam"`.
8. build-universal-bundle.sh line 13: `two-page` becomes `six-page`.
9. buildroom/README.md line 48 (the `buildroom-search-answer-engine` row) currently ends `§13 rows, §8 |` with no Requires cell. Append ` §1 §2 (best §3 §4 §14 §18); Python 3 only, no packages, ffmpeg not needed |` so the row has four cells like its neighbours.
10. deck line 181: `twenty-six skills` becomes `thirty-two skills`. Line 68 ("twenty-six of them") stays; LATER.md parks the rest of the deck.
11. Sync: `bash buildroom/build-skills.sh` from the repo root. Expected: 32 lines `built dist/<skill>.skill (...)` and the final `Done.` line, exit 0. Then `git status --short` must list exactly the ten edited files above plus 32 `buildroom/skills/*/references/business-file-template.md` entries and nothing else (PROGRESS.md aside).

Acceptance checks:
- `grep -rn 'new-session-1rmv4i\|<branch>' buildroom --include=*.md` prints nothing.
- `grep -c '§14–§21' buildroom/skills/buildroom-os/SKILL.md` prints `1`; `grep -c '§14–§19' buildroom/skills/buildroom-os/SKILL.md` prints `0`.
- `grep -c 'search and answer presence (§1–§21' buildroom/rollout/universal/CLAUDE.md` prints `1`.
- `grep -rn 'File version' buildroom --include=*.md --include=*.html | grep -v test-run | grep -vc '1\.6'` prints `0` (every File version statement outside test-run says 1.6).
- `grep -c 'Alex, Sam' buildroom/rollout/Brainstorm_Board.html` prints `1`; a grep for the second first name over buildroom prints nothing.
- `grep -c 'six-page' buildroom/build-universal-bundle.sh` prints `1`; `grep -c 'two-page' buildroom/build-universal-bundle.sh` prints `0`.
- `sed -n 48p buildroom/README.md | awk -F'|' '{print NF-2}'` prints `4`.
- `grep -c 'thirty-two skills' buildroom/rollout/decks/2026-10-build-room-os-deck.md` prints `1`.
- `for f in buildroom/skills/*/references/business-file-template.md; do cmp -s "$f" buildroom/templates/BUILDROOM_BUSINESS_FILE.md || echo "DIFF $f"; done | wc -l` prints `0`, and `ls buildroom/skills/*/references/business-file-template.md | wc -l` prints `32`.
- `bash -n buildroom/build-universal-bundle.sh && echo ok` prints `ok`.
- Suites in the order launch, linkedin, search, media: 394/394, 139/139, 191/191, 56/56, each exit 0. Then remove `__pycache__` (see ground rules).

Commit: subject `Read-through fixes: progress view to §21, File version 1.6, neutral placeholder, six-page guide, counts and Requires cell`. Add the ten edited files, the 32 template copies by path (`git add buildroom/skills/*/references/business-file-template.md` plus the ten), and PROGRESS.md.

## M2: redact the research note

Delivers: Definition of Done item 6. File: `research_notes/World class event launches/lanny_vault_method.md` (tracked; 374 lines, 7,557 words; headings: one H1, six H2 at lines 11, 26, 240, 298, 335, 356, eight H3 at lines 28, 51, 74, 108, 119, 159, 191, 224). Sizing on 2026-10-31: 64 dollar figures, 102 number tokens of 100 or more that are not years, 179 backticked vault paths plus 2 `/home/user/brain` paths and 1 `knowledge/...` path, 44 parenthetical unbackticked citations, about 50 partner-identifying tokens. 204 of 374 lines need an edit. Section 3 (lines 240 to 295) and section 6 (lines 356 to 374) are almost entirely figures and paths. Edit by hand, section by section; do not run a blind search-and-replace over the file.

Redaction rule (apply all three):

R1 Figures. Every founder figure becomes a range word or a plain word, including figures under 100 when they count the founder's people or money: buyer counts, list sizes, registration and attendance counts, chat and session counts, strategy-session counts, revenue and booked figures, refund counts, the integrity-breach amount, frozen enrollment counts, lead cost, the planned and actual price ladders with every price, projections. Suggested words: "a one-dollar front-end product" for the $1 Build Brief price; "the core offer, high three figures" or "the core program price" for $997 and its monthly plan; "the high-ticket tier, four figures" for $3,000 and $9,000; "low five figures cash, mid five figures booked" for revenue; "under a thousand registered", "roughly a third showed up live", "about a hundred dollar-buyers", "about one in five of them bought the core offer", "a few dozen at the close", "a couple of thousand enrollments frozen", "a handful of refunds", "a paid member's five-figure result presented as a free-camp win", "a few thousand dollars in lead cost". Section 3 keeps its three tables and column headings; every Value cell is rewritten in words and every Source cell becomes `founder's notes`. Keep: years and dates (Jul 2026, Sep 18–20 2026, 2026-08-02), method counts (3-day, 5-day, 22 questions, 16 emails, 7 daily emails, 12-step, 13-step, 60-minute, 24 hours, minute blocks in the run of show), and percentages that state a lesson, rounded to a whole number and prefixed "about" where they were exact (39.2% becomes "about 40%"; "137% more" becomes "well over double"). No count of 100 or more may remain except years.

R2 Citations. Every backticked vault path (prefixes `PB/`, `K/`, `IT/`, `ZT/`, `FB/`, `memory/`, `knowledge/`, `/home/user/brain`) and every unbackticked reference to a vault document ("audit §0", "audit Appendix", "proof bank §F", "planning brief §5", "followup-redesign §7", "strategy page", "prep doc", "same file", transcript timestamps such as 00:43:32, "line ~92") becomes the two words `founder's notes`, at most once per sentence, in the parentheses where the citation stood. Line 3 becomes `Research notes for the Build Room OS "Event Launcher" skill. Source: the founder's private notes, which are not in this repository. Compiled 2026-10-17.` Line 5 (the path shorthand) is deleted. Section 6 keeps its heading and replaces the whole list with one paragraph: `The founder's private notes behind this file hold attendee, buyer, partner and staff names, list sizes, revenue ledgers, database paths and one credential. None of that was copied here, and the skill must not reproduce any of it. Use anonymized patterns only.`

R3 Names. Keep the founder (Lanny, Lanny Morton, AI Momentum Labs), the founder's own product and event names (Forever Free AI Boot Camp, Built for Freedom, Navigator, Compass, Architect, Build Brief, Build Lab, Build Room, Complete Year, 3-Day AI MBA), and published authors cited for a published concept (Russell Brunson, Alex Hormozi, Joe Sugarman; Vistaprint as a company). Remove every partner, former business partner, partner company, client, staff member and attendee name and every product name that identifies a partner, replacing with a role word: the promotion partner's personal name, company name, company abbreviation and the partner's product names (stage-selling, mentoring, wealth and "money blueprint" programs, the "forever free number") become "the promotion partner" and "the partner's stage-selling IP"; the two former seminar-business partners and their real-estate seminar brand become "two former seminar-business partners" and "his earlier real-estate seminar business"; the real-estate author becomes "a real-estate author's evergreen funnel"; the offer coach becomes "an offer coach"; the sales trainer becomes "a sales trainer's framework"; the client clinic becomes "a client's funnel"; the three remaining personal names disappear with their paths. Existing `[name removed]` markers stay. The builder reads STATE.md section 6 and the file itself for the exact names; they are not repeated here so that this plan can live on main.

Acceptance checks (F is the file path, quoted):
- `grep -cE '\$[0-9]' "$F"` prints `0`.
- `grep -oE '\b[0-9]{1,3}(,[0-9]{3})+\b|\b[1-9][0-9]{2,}\b' "$F" | grep -vE '^(19|20)[0-9]{2}$'` prints nothing.
- `grep -cE '`(PB|K|IT|ZT|FB|memory|knowledge)/|/home/user/brain' "$F"` prints `0`.
- `grep -cE 'audit (§|Appendix)|proof bank §|planning brief §|followup-redesign §|strategy page|prep doc|[0-9]{2}:[0-9]{2}:[0-9]{2}' "$F"` prints `0`.
- A case-insensitive grep for every partner, partner-company, partner-product, former-partner, author, coach, trainer, clinic and staff name listed in STATE.md section 6 and found in the file before editing prints `0`. The builder writes the exact pattern used into PROGRESS.md only as a count, never the names.
- `grep -c '^#' "$F"` prints `15` (headings unchanged); `grep -c "founder's notes" "$F"` prints a number of 40 or more.
- `grep -c $'\xe2\x80\x94' "$F"` is not larger than before the edit (no em dash added; record the before count in PROGRESS.md).
- The builder re-reads the whole file end to end once after editing and writes "re-read complete, no figure, path or partner name found" in PROGRESS.md.
- Launch suite still 394/394 (no suite reads this file; this is the smoke test).

Commit: subject `Redact the event-launch research note: figures to ranges, vault citations to founder's notes, partner names to roles`.

## M3: root README pointer, NOTES.md instructor line, names out of the planning files

Delivers: Definition of Done item 7 and the NOTES.md part of item 5, plus the name clean-up the committed planning files need.

Files touched: README.md (repo root), NOTES.md, STATE.md, GOAL.md (one grep literal), LATER.md, PORTFOLIO.md.

Edits, exact:
1. README.md: after line 3 (the first paragraph, ending `...for ChatGPT desktop and Codex.`) and its following blank line, insert this line and a blank line: `Build Room OS, the member toolkit for the Build Room (thirty-two skills for Claude Code and Codex), lives under [\`buildroom/\`](buildroom/README.md).` Lines 5 onward (the `## Install` heading) shift down by two.
2. NOTES.md line 19 becomes: `- Research behind the newest skills in \`research_notes/\` and \`reports/\` (confidential founder data removed; no third-party instructors are credited anywhere, by the owner's instruction).` NOTES.md line 30: the partner-company abbreviation before "admin password" becomes "a partner campaign's".
3. STATE.md: line 24, the instructor's full name becomes "the instructor's name"; line 52, the placeholder quote becomes `"[two first names]"` and the sentence about the second personal name is kept in words; line 56, the partner abbreviation becomes "partner campaign"; line 72, the placeholder quote becomes "the two first names"; line 74, the instructor's name becomes "the third-party instructor".
4. GOAL.md line 77: the two grep literals become `grep -rn '<second placeholder name>' buildroom` and `grep -rn '<instructor surname>' .` in words, with a note in PROGRESS.md that this is the one edit to GOAL.md after approval and that it changes no requirement.
5. LATER.md line 14 and PORTFOLIO.md line 16: the partner-company abbreviation becomes "a partner campaign's" / "the partner campaign note" so the sentences still read.

Acceptance checks:
- `sed -n '5p' README.md` prints the new Build Room OS line; `sed -n '7p' README.md` prints `## Install`; `grep -c 'buildroom/README.md' README.md` prints `1`.
- `sed -n '19p' NOTES.md` prints the new line exactly; `grep -c 'no third-party instructors are credited anywhere' NOTES.md` prints `1`.
- A case-insensitive grep over the whole tree (excluding .git) for the instructor's surname, the second placeholder first name, and the partner-company abbreviation as a whole word prints nothing. After the commit the same `git grep` against HEAD prints nothing.
- Launch suite 394/394.

Commit: subject `Root README points to buildroom/; planning notes state rules without third-party names`.

## M4: media suite leaves no __pycache__; order proof media then launch

Delivers: Definition of Done item 8. File touched: buildroom/tests/media/run_tests.py only.

Why: the launch suite's last check (run_tests.py line 1754) fails if any `__pycache__` exists under buildroom/. The media suite imports `mock_providers` (tests/media/) and `videolib` and `transcribe` (skills/buildroom-video-director/scripts/) in-process, which writes `.pyc` files, and its `sh()` helper (line 31) runs subprocesses with `env=None` or the `env` dict from line 42, neither of which sets PYTHONDONTWRITEBYTECODE.

Edits:
1. Replace line 11 (`import json, os, shutil, subprocess, sys, tempfile, threading`) with three lines, mirroring the launch suite's lines 10 to 12:
   `import sys`
   `sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ in the skill folders or here)`
   `import json, os, shutil, subprocess, tempfile, threading  # noqa: E402`
2. In `sh()`, before `subprocess.run`, add `env = {**(env or os.environ), "PYTHONDONTWRITEBYTECODE": "1"}` so every subprocess the suite starts carries it.
3. In the `env` dict at line 42, add the entry `"PYTHONDONTWRITEBYTECODE": "1"` (belt and braces).
4. Replace the `if __name__ == "__main__": sys.exit(main())` block at the end with:
   `if __name__ == "__main__":`
   `    try:`
   `        rc = main()`
   `    finally:`
   `        for d in ROOT.rglob("__pycache__"):`
   `            shutil.rmtree(d, ignore_errors=True)`
   `    sys.exit(rc)`

Acceptance checks:
- `python3 -c "import ast,sys; ast.parse(open('buildroom/tests/media/run_tests.py').read()); print('parses')"` prints `parses`.
- `grep -c 'dont_write_bytecode' buildroom/tests/media/run_tests.py` prints `1`; `grep -c 'PYTHONDONTWRITEBYTECODE' buildroom/tests/media/run_tests.py` prints `2`.
- `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +` (clean start), then `python3 buildroom/tests/media/run_tests.py; echo exit=$?` ends `56/56 checks passed` and `exit=0`, then `find buildroom -name __pycache__ | wc -l` prints `0`, then `python3 buildroom/tests/launch/run_tests.py; echo exit=$?` ends `394/394 checks passed` and `exit=0`. This is the order proof.
- `git status --short` lists only `buildroom/tests/media/run_tests.py` (and PROGRESS.md).

Commit: subject `Media tests leave no __pycache__: bytecode off in-process and in every subprocess, cleanup in finally`.

## M5: rebuild the zip, full suite run, commit, push

Delivers: Definition of Done item 9. Run only after M1 to M4 are committed; the zip is built once.

Files touched: buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip (replaced under the same name), buildroom/rollout/releases/README.md (one sentence appended to the 2026-10-28 row), buildroom/dist/BuildRoom_OS.zip (git-ignored, not committed).

Steps:
1. `git status --short` prints nothing. `find buildroom -name __pycache__ -type d -prune -exec rm -rf {} +`.
2. `bash buildroom/build-universal-bundle.sh` from the repo root. Expected: the line `built dist/BuildRoom_OS.zip (4.4M)` (size may differ slightly) followed by the sorted list of non-skill files in the zip (AGENTS.md, BUILDROOM_BUSINESS_FILE.md, BuildRoom_OS_Say_These_Words.pdf, CLAUDE.md, START-HERE.md, install.ps1, install.sh, tools/Brainstorm_Board.html, tools/BuildRoom_OS_Quick_Start.html, tools/Business_File_Viewer.html, tools/Rent_Calculator.html), exit 0.
3. `git status --short` still prints nothing (build-skills.sh re-copied identical files). If anything appears, stop and inspect before going on.
4. `cp buildroom/dist/BuildRoom_OS.zip buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`.
5. releases/README.md: append to the end of the 2026-10-28 row's "What changed" cell, before the closing ` |`: ` Rebuilt 2026-10-31 from the read-through fixes (progress view to §21, File version 1.6, neutral Brainstorm Board placeholder); contents otherwise unchanged.` (This README is not in the zip, so no second build.)
6. Verify the zip (ZIP is the committed path):
   - `cmp buildroom/dist/BuildRoom_OS.zip "$ZIP" && echo same` prints `same`.
   - `unzip -l "$ZIP" | grep -cE ' BuildRoom_OS/\.claude/skills/[^/]+/$'` prints `32`; the same with `\.codex` prints `32`; with `skills/[^/]+/$` and no dot prefix prints `32`.
   - `rm -rf SCRATCH/zipcheck && mkdir -p SCRATCH/zipcheck && unzip -q "$ZIP" -d SCRATCH/zipcheck`, then `diff -rq SCRATCH/zipcheck/BuildRoom_OS/skills buildroom/skills` prints nothing, `diff -rq SCRATCH/zipcheck/BuildRoom_OS/.claude/skills SCRATCH/zipcheck/BuildRoom_OS/skills` prints nothing, same for `.codex/skills`.
   - `cmp` each of these pairs, all silent: zipcheck CLAUDE.md and AGENTS.md against buildroom/rollout/universal/CLAUDE.md; START-HERE.md against buildroom/rollout/universal/START-HERE.md; BUILDROOM_BUSINESS_FILE.md against buildroom/templates/BUILDROOM_BUSINESS_FILE.md; BuildRoom_OS_Say_These_Words.pdf against buildroom/rollout/BuildRoom_OS_Say_These_Words.pdf; tools/*.html against buildroom/rollout/*.html (four files); install.sh and install.ps1 against buildroom/rollout/universal/.
   - `unzip -p "$ZIP" BuildRoom_OS/BUILDROOM_BUSINESS_FILE.md | sed -n 7p` prints `**File version:** 1.6`; `unzip -p "$ZIP" BuildRoom_OS/.claude/skills/buildroom-os/SKILL.md | grep -c '§14–§21'` prints `1`; `unzip -p "$ZIP" BuildRoom_OS/tools/Brainstorm_Board.html | grep -c 'Alex, Sam'` prints `1`; `unzip -l "$ZIP" | grep -c __pycache__` prints `0`.
7. Full suite run in this order, each exit 0: launch 394/394, linkedin 139/139, search 191/191, media 56/56, launch 394/394. `find buildroom -name __pycache__ | wc -l` prints `0`.
8. Final greps: `grep -rn 'new-session-1rmv4i\|<branch>' buildroom --include=*.md` nothing; the M3 name greps against the tree and against HEAD, nothing.
9. Commit: `git add buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip buildroom/rollout/releases/README.md PROGRESS.md`, subject `Release 2026-10-28 rebuilt from the read-through fixes; download pattern on main`.
10. Model-identifier check on the new commits: `git log 9326d24..HEAD --format='%s%n%b' | grep -v '^Co-Authored-By' | grep -ciE 'opus|fable|sonnet|haiku|claude-'` prints `0`.
11. Push: `git push -u origin claude/new-session-1rmv4i`. Then `git rev-parse HEAD origin/claude/new-session-1rmv4i` prints the same hash twice, and `gh api repos/lanny-ai/codex/pulls/2 --jq '.head.sha, .mergeable, .mergeable_state'` prints that hash, `true`, `clean` (re-query after a minute if `mergeable` is null while GitHub recomputes).

## M6: PR body, ready for review, merge, confirm the main link

Delivers: Definition of Done items 10, 11, 12. No repo files change except PROGRESS.md and SHIP.md. Everything goes through `gh api` REST calls; GraphQL is blocked from this session (`gh pr ready` and `gh pr merge` may fail for that reason), so use the routes below, with the GitHub MCP tools `update_pull_request` (draft: false) and `merge_pull_request` (merge_method: merge) as fallbacks.

Steps:
1. Preconditions: M5 pushed; `gh api repos/lanny-ai/codex/pulls/2 --jq '.state, .draft, .mergeable_state, .head.sha'` prints `open`, `true`, `clean`, and the local HEAD hash.
2. Save the body: `gh api repos/lanny-ai/codex/pulls/2 --jq .body > SCRATCH/pr-body-before.md` (374 lines, no CR characters; the title is 170 characters starting `Build Room: Business File system, thirty-two skills`). Copy to SCRATCH/pr-body-after.md and make exactly four edits with a small Python script in SCRATCH (not in the repo):
   a. Line 15: `## 3. Twenty-eight skills (` becomes `## 3. Thirty-two skills (`.
   b. Line 19 (the Electives line under heading 3): delete the token ` · \`buildroom-video-engine\`` so four electives remain.
   c. Line 110 (heading 17): replace the trailing parenthetical `(\`buildroom-video-engine\`)` with `(now the Video Director's volume mode, \`buildroom-video-director\`)`. Leave the rest of the heading, including its existing dash, untouched.
   d. Footer: the file ends with six lines: `---`, blank, the session URL, blank, `---`, `_Generated by [Claude Code](https://claude.ai/code)_`. Replace those six lines with five: `---`, blank, `🤖 Generated with [Claude Code](https://claude.com/claude-code)`, blank, `https://claude.ai/code/session_01GafcQSGHpsWJowL4fXkLgX`.
   Line 177 ("Still twenty-eight skills.") is section 24 history and stays.
3. Check the edit: `diff SCRATCH/pr-body-before.md SCRATCH/pr-body-after.md` shows exactly four hunks (lines 15, 19, 110, and the footer); `grep -c $'\xe2\x80\x94' SCRATCH/pr-body-after.md` prints `31` (same as before, no em dash added); `grep -ciE 'opus|fable|sonnet|haiku' SCRATCH/pr-body-after.md` prints `0`.
4. Build the JSON: `python3 -c 'import json,sys; json.dump({"body": open(sys.argv[1]).read()}, open(sys.argv[2], "w"))' SCRATCH/pr-body-after.md SCRATCH/pr-patch.json`. Apply: `gh api -X PATCH repos/lanny-ai/codex/pulls/2 --input SCRATCH/pr-patch.json --jq '.title, (.body|length)'`. Verify: `gh api repos/lanny-ai/codex/pulls/2 --jq .body | sed -n '15p;19p;110p'` shows the three edited lines, `gh api repos/lanny-ai/codex/pulls/2 --jq .body | tail -5` shows the new footer, and the title printed equals the title in step 2.
5. Mark ready: `gh api -X POST repos/lanny-ai/codex/pulls/2/ccr/ready_for_review`. Verify `gh api repos/lanny-ai/codex/pulls/2 --jq .draft` prints `false`. Fallback: MCP `update_pull_request` with owner lanny-ai, repo codex, pullNumber 2, draft false.
6. Final green check before the irreversible step: `gh api repos/lanny-ai/codex/pulls/2 --jq '.draft, .mergeable, .mergeable_state, .head.sha'` prints `false`, `true`, `clean`, local HEAD.
7. Merge with a merge commit: `gh api -X PUT repos/lanny-ai/codex/pulls/2/merge -f merge_method=merge -f sha=<local HEAD hash> -f commit_title='Merge pull request #2 from lanny-ai/claude/new-session-1rmv4i' --jq '.merged, .sha'` prints `true` and the merge commit hash. Fallback: MCP `merge_pull_request` with merge_method merge and expectedHeadSha set to the local HEAD. No model identifier in the merge title or message.
8. Verify the merge: `gh api repos/lanny-ai/codex/pulls/2 --jq '.merged, .merge_commit_sha'` prints `true` and the hash; `gh api repos/lanny-ai/codex/commits/<merge hash> --jq '.parents|length'` prints `2` (a true merge commit); `git fetch origin main && git log origin/main -1 --format='%H %P'` shows that hash with two parents.
9. Confirm the download: `curl -sIL https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip | grep -iE '^HTTP|^content-type|^content-length'` ends with `HTTP/2 200`, `content-type: application/zip`, and a content-length equal to `stat -c %s buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`. Then `curl -sL -o SCRATCH/main.zip <that URL> && cmp SCRATCH/main.zip buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip && echo same` prints `same`. Run the same `curl -sIL` check on the two guides: `https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/BuildRoom_OS_Say_These_Words.pdf` and `https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/whats-new/BuildRoom_OS_Whats_New_2026-10-28.pdf` (expect 200 and `application/pdf`).
10. Tell the owner, in PROGRESS.md and in the final reply: the zip link to post in the Members' area is `https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip`; the two guide links above; PR #2 merged into main as a merge commit (hash); the branch `claude/new-session-1rmv4i` is left in place (delete_branch_on_merge is off).

## Not in scope (copied from LATER.md)

- MEMBER-README.md into the zip (owner: START-HERE replaced it).
- CI for the four test suites (no `.github/` today; suites run by hand).
- `rollout/decks/` deck text and .pptx beyond the one skill-count fix; `brand/concepts/`; `docs/BUILDROOM-*.md`; `curriculum/` raw text: planning material that rides along, untouched.
- `generate-skill.py` scaffolding, unused since the early skills: remove or document later.
- Discovery Engine's optional certainty adapter (external API path): review whether it stays in a stdlib toolkit.
- Four unapplied test-run findings (one-offer schema, 25% pre-fill at session 3, protocol and curriculum contradiction, rating timing).
- `build-skills.sh` overwrites embedded copies silently except the media files; consider a check mode.
- 4.5 MB zip committed per release; consider GitHub Releases for the binaries.
- Founder's name in 15 skill reference files (reconstruction headers, product name, "Lanny's words"): owner's own name, kept; revisit if a white-label version is ever wanted.
- Vault credential clean-up (AddEvent key, partner campaign admin password) in the Obsidian vault: PORTFOLIO.md Next item 2, outside this repo.
- Weekly member hand-off of the 2026-10-28 zip and guides: PORTFOLIO.md Next item 1, follows the merge.
- Gamma deck status check (generation gen_QGa5LdoKmrazXjIWLqjbD was still pending at last look).
- Root README overhaul beyond the one pointer line; OS Cortex and Control Center plugin decisions (parked in PORTFOLIO.md to 2026-11-30).

## Definition of Done to milestone

| # | Definition of Done item | Milestone |
|---|---|---|
| 1 | Release README download pattern says `main` | M1 (edit), M5 (row note) |
| 2 | buildroom-os progress view lists §14–§21; universal CLAUDE.md names all 21 sections' topics | M1 |
| 3 | Template and Viewer say `File version: 1.6`; all 32 embedded copies match the template | M1 |
| 4 | Brainstorm Board placeholder holds neutral names | M1 |
| 5 | Bundle script header, buildroom README Requires cell, deck skill count and NOTES.md instructor line corrected | M1 (first three), M3 (NOTES.md) |
| 6 | Research note redacted as specified and re-read | M2 |
| 7 | Root README points to `buildroom/` | M3 |
| 8 | Media suite leaves no `__pycache__`; launch passes after media | M4 |
| 9 | 2026-10-28 zip rebuilt, matches sources, committed; all four suites green; branch pushed | M5 |
| 10 | PR #2 body headings and footer fixed; PR marked ready for review | M6 |
| 11 | PR #2 merged into `main` with a merge commit | M6 |
| 12 | Ship: the raw `main` download link returns the zip, and the owner is told the link to post | M6 |
