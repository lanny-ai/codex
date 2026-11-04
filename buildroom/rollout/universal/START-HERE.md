# Build Room OS — Start Here

You unzipped one folder. It works in **Claude Code** and **Codex**. Pick your tool below. Two minutes each.

Keep this folder. Your Business File lives in it, and every session reads and updates that file, so the work compounds.

---

## Claude Code (terminal or desktop app)

**Fastest:** open a terminal in this folder and start Claude Code.

```
cd BuildRoom_OS
claude
```

The thirty-six skills are picked up automatically from `.claude/skills/`. Say:

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

## Your Business File

The skills read and write `BUILDROOM_BUSINESS_FILE.md` in this folder automatically. You never paste it; you never re-explain your business.

---

## What's in the folder

| Path | What it is |
|---|---|
| `BUILDROOM_BUSINESS_FILE.md` | **Your** Business File. One file, twenty-one sections, every session builds on it. Your first session creates it from `templates/`. |
| `templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md` | The blank Business File the first session copies. Releases carry only this blank copy, never a file named like yours, so an update cannot replace your file. |
| `update.sh`, `update.ps1` | Install a new release into this folder safely (see Updating below). |
| `BuildRoom_OS_Say_These_Words.pdf` | Print it, keep it by your computer: every trigger phrase, what it needs, what it writes. |
| `tools/BuildRoom_OS_Quick_Start.html` | Open in a browser: the visual guide to the program and every session's trigger phrase. |
| `tools/Rent_Calculator.html` | Open in a browser: what your undocumented processes cost you. Copies a §9 block into your file. |
| `tools/Business_File_Viewer.html` | Open in a browser: paste your Business File, see every section's status, your progress, the one session to run next, and your Build Plan. |
| `tools/Brainstorm_Board.html` | Open in a browser: frame, diverge, cluster, dot-vote, decide, then "Copy for Claude." |
| `skills/` | The thirty-six skills, readable. `.claude/skills/` and `.codex/skills/` are identical copies the tools discover on their own. |
| `CLAUDE.md`, `AGENTS.md` | Tell Claude Code and Codex what this folder is. Don't delete them. |

## Updating to a new release

Your Business File and everything you made stay exactly as they are. Do it this way, not by unzipping over this folder:

1. Unzip the new release somewhere else, for example your Downloads folder.
2. Run its update script and give it the path of **this** folder (drag the folder into the terminal window to paste its path):
   - Mac / Linux: `bash ~/Downloads/BuildRoom_OS/update.sh "/path/to/this/BuildRoom_OS"`
   - Windows: `powershell -ExecutionPolicy Bypass -File "$HOME\Downloads\BuildRoom_OS\update.ps1" "C:\path\to\this\BuildRoom_OS"`
3. It replaces only the Build Room skills, tools and instructions, saves everything it replaces in `backups/`, checks your Business File is unchanged byte for byte, and says so.

Or open Claude Code in this folder and say: "Update Build Room OS from my Downloads folder." It runs the same script.

## The sessions

| Say this | You walk out with |
|---|---|
| "Help me build my ideal client avatar" | Your ICA and your clients' exact words |
| "Help me build my signature offer" | Deliverables, price, guarantee, pitch |
| "Help me position my business" | Your Messaging Bible |
| "Write my offer page" | A publication-ready offer page |
| "Help me map my funnel" | A traffic strategy proposed from your file, the funnel map, emails written one at a time, built in GoHighLevel and launch-tested |
| "Help me build my opt-in page" | Landing page or a built web application that qualifies leads, lead magnet, delivery automation |
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
| "Make me ads" | Three different ad concepts from your file, copy one ad at a time, finished image ads in three sizes, reviewed, with a kit ready to upload |
| "Make me a video" (ad, content, sales video, or "help me get a client testimonial video") | A directed video around your real face and footage: script, shoot list, edit, captions, review, ready to publish |
| "Build my LinkedIn engine" (or "write my LinkedIn posts", "who should I message on LinkedIn today", "how is my LinkedIn doing") | A profile that converts, three posts a week in your own words, carousels, a 20-minute daily conversation routine, a pipeline and a weekly scorecard; you post and send everything yourself |
| "Plan my launch" (or "help me run a challenge", "I want to do a 3-day bootcamp", "is my launch ready", "how did my launch do") | A live event that sells: the launch math, the format, the one belief, invitation and reminder emails, the calendar file, the run-of-show, the close, a launch gate that catches a broken checkout before your audience does, follow-up by where each person stopped, and a debrief saved to your Obsidian vault |
| "Capture this win" (or "ask for a testimonial", "build my proof bank", "what proof can I use") | Client wins turned into proof you're allowed to use: a 3-question interview, permission recorded for every story, and one placement at a time into your page, emails, ads, posts and launches |
| "Get found on Google" (or "fix my Google Business Profile", "get more Google reviews", "answer this question on my website", "am I showing up in ChatGPT") | Found and cited without ads: your Google Business Profile scored and fixed, one honest answer page a week on your own website through a gate, a review ask you send the same way to everyone, five free listings, and a monthly check of whether Google's AI, ChatGPT, Perplexity, Gemini and Copilot name you |
| "Build me a source watcher" | A watcher for any source, filing filtered notes into your Obsidian vault (elective; some sources need a paid key, it says which) |
| "Set up my second brain" | An Obsidian vault with Claude Code inside it, your data on your own machine (elective; free app, subscription only) |
| "Make me an agent" | An agent definition from the founder's thirteen elements, installable as a skill or handed to a build (elective) |
| "Triage my projects" (or "what should I finish", "help me choose") | The one project to finish next and the rest parked with a revisit date, in PORTFOLIO.md and your Build Plan (elective) |
| "Finish it" (or "what is left to do", "take this over the line") | An unfinished project audited, cut to the smallest shippable version, built and tested by a crew, and shipped with a checklist; say it inside the project's folder (elective) |
| "Build me an app" (or "build it", "pursue goal") | A new app or tool from an idea: a brainstorm, one written goal you approve, then a crew that builds, tests, reviews and documents it (elective) |
| "Set up the continuity system for this project" (or "pick up where we left off", "hand off cleanly") | Any long project kept resumable across new threads and between Claude and Codex: three small files in the project's own folder; your Business File is only read, never changed (elective; from community member Jenn) |
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
