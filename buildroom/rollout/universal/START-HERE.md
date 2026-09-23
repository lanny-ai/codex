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

The thirteen skills are picked up automatically from `.claude/skills/`. Say:

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
2. Upload every file in the `cowork/` folder (thirteen `.skill` files, any order).
3. Open a new session and say: **"I'm new to the Build Room — set me up."**

In Cowork, paste your Business File into the session when asked and save the updated copy it hands back. In Claude Code and Codex this happens automatically: the skills read and write `BUILDROOM_BUSINESS_FILE.md` in this folder.

---

## What's in the folder

| Path | What it is |
|---|---|
| `BUILDROOM_BUSINESS_FILE.md` | **Your** Business File. One file, thirteen sections, every session builds on it. Blank until your first session. |
| `tools/BuildRoom_OS_Quick_Start.html` | Open in a browser: the visual guide to the program and every session's trigger phrase. |
| `tools/Rent_Calculator.html` | Open in a browser: what your undocumented processes cost you. Copies a §9 block into your file. |
| `tools/Brainstorm_Board.html` | Open in a browser: frame, diverge, cluster, dot-vote, decide, then "Copy for Claude." |
| `skills/` | The thirteen skills, readable. `.claude/skills/` and `.codex/skills/` are identical copies the tools discover on their own. |
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
| "Help me document my process" | SOPs with checklists and a Definition of Done |
| "Help me hire for this role" | Scorecard, job ad, structured interview kit |
| "Help me train my new hire" | Training handbook with checkouts and a 30-day calendar |
| "What numbers should I be watching every week?" | One-page dashboard, 30-minute weekly meeting, optional Monday routine |
| "Let's brainstorm" | A framed question, a voted board, outcomes with owners |
| "Capture what we decided" | Decision records, proto-SOPs, build briefs, Build Plan rows |
| "Where do I start?" | The navigator: where you are and the one thing to run next |

Run the first six in order the first time. The navigator keeps you on track.

## The one habit

Every session reads your Business File first and writes it back at the end. Never re-explain your business. If a session asks you something the file already answers, tell it to read the file.

---
Build Room · AI Momentum Labs
