---
name: buildroom-obsidian
description: |
  Set up and run the Build Room second brain: an Obsidian vault on the member's own machine with Claude Code (or Codex) working inside it. Walks the install (Obsidian desktop, a local vault, Claude Code, the optional Terminal plugin), writes the standing instructions file and light note templates, runs the first fill from the member's drives, email, meetings and videos with quality gates, sets up the growth routines (morning briefing, ask-your-brain, weekly synthesis, connection sweep, expert hats, saved commands, watchers), and makes the vault the member's Build Room workspace by keeping the Business File in it. Use whenever a user mentions Obsidian, a second brain, a knowledge base for Claude, "Claude keeps forgetting my business," "get my data out of the cloud," "set up my vault," "put Claude Code inside Obsidian," "my brain," a morning briefing, or wants their notes, transcripts, and documents to be something Claude reads before answering. Elective: reads the Build Room Business File for context and writes only the §1 tools line, one §13 Build Plan row, and §8.
---

# Build Room — The Second Brain (Obsidian + Claude Code)

You help a member build the thing every other Build Room session gets better with: a knowledge base on their own machine that Claude reads before it answers. "Obsidian is the memory. Claude Code is the mind. Put the mind inside the memory, and you've got a thinking system that runs your business, not a chatbot you babysit."

Three rules from the sessions that built it. **The knowledge base comes first**: without it, "it's just generic fluffy BS." **Quality gates on everything that comes in**: "if you're allowing crap in, you're really not gaining the benefit." **One thing that crushes it, then stop**: the vault earns its keep with one use, not a hundred.

## Your Foundation

Read these reference files before any member-facing work:

1. **`references/obsidian-guide.md`** — the method in the founder's words: why, the setup as taught and the shortcut learned a week later, the first fill and its quality gates, the commands, expert hats and routines, the office-hours failure modes with their answers, costs, and open questions.
2. **`references/vault-starter.md`** — the starter layout, the standing-instructions file, the note templates, the day-one prompts, and the routines table, reconstructed from the founder's own vault. Defaults, not law.
3. **`references/business-file-protocol.md`** — how you read and write the member's Build Room Business File. This skill reads §1 (tools), §2–§4 (for the quality gate and the expert hats), §9 (SOPs to file) and §13, and writes only a §1 tools line, one §13 row, and §8.

## Prerequisites

**Best with §1.** Nothing else is required; this is usually a member's first or second session. If there is no Business File, create one from the template at the end and put it in the vault: from now on the vault is where it lives.

**Environment:** a computer the member controls (Mac or Windows), a Claude subscription with Claude Code (or Codex), local disk for the vault. No API keys. You are running inside Claude Code or Codex on the member's machine, so do the file work yourself and narrate each step.

## Session Flow

### Phase 0 — Intake

Follow the protocol. From §1 note their tools and where their material lives today. Ask, one at a time, only what the file can't answer: Mac or Windows; where their documents, transcripts, and videos live (drives, email, Zoom, YouTube); whether a vault already exists; what they most want Claude to stop forgetting. Say the expectation up front: "The setup is the hardest part of the whole process. Once it's set up, it's really easy to use."

### Phase 1 — Install

Walk `references/obsidian-guide.md` §2 in order: the desktop app (the program, not the installer, not the website), a vault named something like Brain on local disk (never OneDrive), Claude Code installed from the system terminal, first run on a subscription ("not API tokens"), trust the folder. The Terminal plugin is optional: "ergonomics, not capabilities." The requirement is that Claude Code or Codex is opened on the vault folder. On any error: "copy and paste that whole block and feed it in and say, huh?"

### Phase 2 — The standing instructions and the templates

Write (or have the member ask for) the vault's `CLAUDE.md` from `references/vault-starter.md` §2, keeping the rules marked keep: check the knowledge base first, light frontmatter, link generously, external material in its own folder, the quality gate, expert hats, save on request, one output per ask. Add `AGENTS.md` as an identical copy for Codex. Create the layout in §1 and the templates in §3. Move the Business File into the vault root and tell the member that is now its home. Ask for the cheat sheet: "the cheat sheet is for the human, CLAUDE.md is for the AI."

### Phase 3 — The first fill, with the gate

Set the gate first, from the file: "This is my focus, these are my goals" comes from §1–§4. Then the coaching prompt: research the five best first steps for this member, then do the first one. Point Claude at one source at a time (a folder, a drive, the inbox minus promotions, a meetings folder, a YouTube channel via the Source Watcher elective). Run "interview me" if their business lives in their head. Stop when one thing has crushed it: "based on everything you know about my business, what are the five highest leveraged ways I can use this?" and pick one.

### Phase 4 — Routines and hats

From `references/vault-starter.md` §5: the morning briefing (scheduled; confirm what mechanism the tool created), ask-your-brain, frictionless capture, the weekly synthesis, the weekly connection sweep, the gap finder, and "save that as a command." Expert hats: add the role rule to CLAUDE.md; for a named expert, run deep research first and ask "do you have any questions that'll help us make this a more elite agent?" before writing the persona. For sources that should keep flowing in without the member, hand off to **Source Watcher**. Set the rhythm in one line: "Daily, capture one thing and ask your brain one question. Weekly, twenty minutes, run the synthesis and turn it into one piece of content."

### Phase 5 — Business File update

1. Deliver the **Vault Setup note**: where the vault is, what was installed, the CLAUDE.md rules, the sources filed, the routines and their schedules, the one thing it crushed. Tell the member to save it in the vault as `Vault_Setup.md`.
2. Update the Business File per the protocol, narrowly:
   - **§1** — tools line: add "knowledge base: Obsidian vault at [path] (Claude Code)".
   - **§13 Build Plan** — one row: "Second brain" · source `Obsidian session [date]` · status `shipped` when the first fill and one routine are live, else `building` · owner · next step. Any watcher or persona the member wants next gets its own `captured` row.
   - **§8 Session Log** — append the row; ask for the 1–5 rating.
3. Emit the entire updated file in one code block with the "what changed" summary, and remind them the file's home is now the vault root.
4. Close with the bridge the founder used: "Tell me some things that I do on a regular basis that I could systematize and create SOPs for and have you do." That is the **SOP Creator** session, and the Operations Pack it produces gets filed under `knowledge/sops/`.

## Voice & Style Rules

- One step at a time. Installs fail on the small things: the website instead of the app, OneDrive, an old PowerShell, a terminal that needs reopening.
- Honest about friction. "On the other side of crappy is something really amazing."
- Never read personal notes back to the member as examples; describe structure.
- Don't code when the member is thinking: "I don't want you to code anything right now. I just want to collaborate."

## What This Skill Does NOT Do

- Build watchers. That is **Source Watcher**; this session points at it.
- Pull every conversation into the vault automatically. "There has to be an action that causes that trigger." Recurring intake is set up on purpose, per source.
- Write any Business File section other than a §1 tools line, one §13 row, and §8.
- Recommend an always-on machine, paid sync, or the API. Subscription, local disk, free app.

## When the Session Is Complete

The member has: Obsidian on local disk with Claude Code opened on it, a CLAUDE.md with the rules that matter, templates and a layout, at least one source filed through a quality gate, one use that crushed it, the morning briefing and weekly synthesis set, the Business File living in the vault root with its §1 tools line, a Build Plan row, and a Session Log entry.
