# SHIP.md: Build Room OS shipped (2026-10-31)

## What shipped

- PR #2 merged into `main` with a merge commit, `f2221e4c9e321354267f7700f7652904abb404d9` (parents `1d80d57` on main and `6185057` on the branch). 32 skills, four test suites, the 2026-10-28 release.
- The release zip downloads from main and is byte-identical to the committed file (4,524,207 bytes, `application/zip`).

## Links to post in the Members' area

- Toolkit: https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/releases/BuildRoom_OS_2026-10-28.zip
- Say These Words guide (six pages): https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/BuildRoom_OS_Say_These_Words.pdf
- What's New 2026-10-28 (eleven pages): https://github.com/lanny-ai/codex/raw/main/buildroom/rollout/whats-new/BuildRoom_OS_Whats_New_2026-10-28.pdf

All three return HTTP 200 from main as of 2026-10-31.

## Checklist

1. Release README download pattern says `main`: done.
2. buildroom-os progress view lists §14–§21; universal CLAUDE.md names all 21 sections' topics: done.
3. Template, spec and Viewer say `File version: 1.6`; 32 embedded copies match: done.
4. Brainstorm Board placeholder holds neutral names: done.
5. Bundle script header, buildroom README Requires cell, deck count, NOTES.md instructor line: done.
6. Research note redacted (figures to ranges, vault citations to founder's notes, third parties to roles) and re-read: done.
7. Root README points to `buildroom/`: done.
8. Media suite leaves no `__pycache__`; launch passes after media: done.
9. Zip rebuilt from the fixed sources, verified against them, committed; suites 394, 139, 191, 56 green; pushed: done.
10. PR #2 body headings fixed (the footer is normalized by the server); PR marked ready: done.
11. PR #2 merged into main with a merge commit: done.
12. Raw main link returns the zip; owner told the links above: done.

## Review and panel verdicts

- Reviewer: FAIL on two Critical findings in the planning files (figures quoted as the "before" side of the redaction); both fixed in commit `8653848`, then clean.
- Persona panel on the shipped zip: SHIP, no Critical or High problem. Medium and Low items are parked in LATER.md.

## Owner decisions still open (parked, not blocking)

- Event Launcher `source-credit.md` and SKILL.md credit two real-estate seminar trainers by name as a deliberate source credit; the research note anonymizes them. Keep or remove.
- Two provider-signup reference files carry a Kie.ai sign-up link with a referral code. Keep or remove.
- The branch `claude/new-session-1rmv4i` is left in place; delete it on GitHub when convenient.

## What happens next

The weekly hand-off is the owner's routine: post the three links above in the Members' area. The next release rebuilds the zip under a new date with `bash buildroom/build-universal-bundle.sh` and adds a row to `buildroom/rollout/releases/README.md`. Everything parked is in LATER.md; the next project is chosen in PORTFOLIO.md.
