# Build Room OS — Start Here

You unzipped one folder. It works in **Claude Code**, **Codex**, and **Claude Cowork / claude.ai**. Pick your tool below. Two minutes each.

Keep this folder. Your Business File lives in it, and every session reads and updates that file, so the work compounds.

---

## Claude Code (terminal or desktop app)

**Fastest:** open a terminal in this folder and start Claude Code.

```
cd BuildRoom_OS
claude
```

The twenty-seven skills are picked up automatically from `.claude/skills/`. Say:

> I'm new to the Build Room — set me up.

**Want the skills in every project, not just this folder?** Run the installer once:

- Mac / Linux: `bash install.sh`
- Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File install.ps1`

It copies the skills into `~/.claude/skills/` and `~/.codex/skills/`. Nothing else is touched.

---

## Codex (OpenAI Codex CLI)

Open a terminal in this folder and start Codex.

```
cd BuildRoom_OS
codex
```

Skills are picked up automatically from `.codex/skills/`. Type `/skills` to see them, or `$buildroom-os` to start the navigator. Or just say:

> I'm new to the Build Room — set me up.

For every project: run the same installer as above. It also fills `~/.codex/skills/`.

---

## Claude Cowork / claude.ai

1. Settings → **Skills** → **Upload Skill**.
2. Upload every file in the `cowork/` folder (twenty-seven `.skill` files, any order).
3. Open a new session and say: **"I'm new to the Build Room — set me up."**

In Cowork, paste your Business File into the session when asked and save the updated copy it hands back. In Claude Code and Codex this happens automatically: the skills read and write `BUILDROOM_BUSINESS_FILE.md` in this folder.

---

## What's in the folder

| Path | What it is |
|---|---|
| `BUILDROOM_BUSINESS_FILE.md` | **Your** Business File. One file, seventeen sections, every session builds on it. Blank until your first session. |
| `BuildRoom_OS_Say_These_Words.pdf` | Print it, keep it by your computer: every trigger phrase, what it needs, what it writes. |
| `tools/BuildRoom_OS_Quick_Start.html` | Open in a browser: the visual guide to the program and every session's trigger phrase. |
| `tools/Rent_Calculator.html` | Open in a browser: what your undocumented processes cost you. Copies a §9 block into your file. |
| `tools/Business_File_Viewer.html` | Open in a browser: paste your Business File, see every section's status, your progress, the one session to run next, and your Build Plan. |
| `tools/Brainstorm_Board.html` | Open in a browser: frame, diverge, cluster, dot-vote, decide, then "Copy for Claude." |
| `skills/` | The twenty-seven skills, readable. `.claude/skills/` and `.codex/skills/` are identical copies the tools discover on their own. |
| `cowork/` | The same skills packaged for Cowork upload. |
| `CLAUDE.md`, `AGENTS.md` | Tell Claude Code and Codex what this folder is. Don't delete them. |

## The sessions

| Say this | You walk out with |
|---|---|
| "Help me build my ideal client avatar" | Your ICA and your clients' exact words |
| "Help me build my signature offer" | Deliverables, price, guarantee, pitch |
| "Help me position my business" | Your Messaging Bible |
| "Write my offer page" | A publication-ready offer page |
| "Help me map my funnel" | Funnel map, email sequence, build plan |
| "Help me build my opt-in page" | Landing page, lead magnet, delivery automation |
| "Build my follow-up system" | A campaign on every yes/no in your funnel, beliefs mapped, built and verified in your CRM |
| "Help me get more leads" | Warm network, cold outreach, referrals, content: one module per session |
| "Help me with my sales call" | Seven-stage script, objections, live role-play |
| "Find the words my clients actually use" | Sourced customer language and objections, into your file |
| "Make my offer a no-brainer" | Value stack, guarantee, urgency, the offer math |
| "Write me [an email, ad, page, letter]" | Finished copy from your file, Kern or Halbert voice |
| "Help me document my process" | SOPs with checklists and a Definition of Done |
| "Help me hire for this role" | Scorecard, job ad, structured interview kit |
| "Help me train my new hire" | Training handbook with checkouts and a 30-day calendar |
| "What numbers should I be watching every week?" | One-page dashboard, 30-minute weekly meeting, optional Monday routine |
| "Let's brainstorm" | A framed question, a voted board, outcomes with owners |
| "Capture what we decided" | Decision records, proto-SOPs, build briefs, Build Plan rows |
| "Set up the video engine" | The automated video pipeline installed in Claude Code (elective, costs money; it tells you how much first) |
| "Build me a source watcher" | A watcher for any source, filing filtered notes into your Obsidian vault (elective; some sources need a paid key, it says which) |
| "Set up my second brain" | An Obsidian vault with Claude Code inside it, your data on your own machine (elective; free app, subscription only) |
| "Make me an agent" | An agent definition from the founder's thirteen elements, installable as a skill or handed to a build (elective) |
| "Run discovery on this business" | The Magic Business Genie rebuilt: research first, confirm what's known, ask only the gaps, then the ten Genie outputs; own business, a client, or a prospect |
| "Where is my funnel leaking?" | Every failure point measured, the top leaks with fixes you approve, and a weekly routine that re-runs it (needs §6 and a week of traffic) |
| "Build my compass" | Who you are at a deep level, in a page and a half that ends in a Compass Statement; every session then sounds like you |
| "Convene the board" | Four executives who genuinely disagree and a chairperson who forces the call, about your business |
| "Where do I start?" | The navigator: where you are and the one thing to run next |

Run the first six in order the first time. The navigator keeps you on track.

## The one habit

Every session reads your Business File first and writes it back at the end. Never re-explain your business. If a session asks you something the file already answers, tell it to read the file.

---
Build Room · AI Momentum Labs
