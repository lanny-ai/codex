# Vault Starter — the layout, the standing instructions, the templates, the routines

A starter shape for a member's vault, reconstructed from the structure of the founder's own vault after a summer of use and from what the June sessions taught. Structure and field names only. Everything here is a default the member may rename; the rules that matter are marked **keep**.

## 1. Layout

```
Brain/                          the vault, a plain folder on local disk (never OneDrive)
  CLAUDE.md                     standing instructions for Claude Code (AGENTS.md, identical, for Codex)
  BUILDROOM_BUSINESS_FILE.md    the member's Build Room Business File, if they keep it here (recommended)
  Command Center.md             the front door: what's live, what's next, where things are
  STATE.md                      current phase, NEXT ACTION, blockers, a dated log
  DECISIONS.md                  append-only: DECISION / WHY / REJECTED
  knowledge/                    the curated brain
    meetings/                   transcripts and notes, by program or client
    sources/                    external material: videos/, documents/, decks/
    entities/                   people, companies, tools (one note each)
    frameworks/                 named methods the member uses
    sops/                       the Operations Pack lives here once §9 exists
    prompts/                    reusable prompts and routines
  External/                     what watchers write; never edited by hand until promoted
  memory/                       session logs, tasks/open, tasks/done
  templates/                    the note templates below
  voice/brand-voice.md          the member's voice, once captured
  .claude/skills/               skills the member installs (the Build Room skills live here too)
  .scripts/                     scheduled routines, if any
```

**Keep:** external content in its own folder, tagged `external` and `unprocessed`, promoted by hand only. **Keep:** light, consistent frontmatter from day one. **Keep:** every note earns at least one inbound link, checked in the weekly sweep.

## 2. CLAUDE.md, the standing instructions

A starting point. `/init` will draft one; make sure these lines survive.

```
# This vault

This folder is my second brain and my Build Room workspace. Read it before you answer me.

## Rules
- Check my knowledge base first. Search knowledge/ before answering from general knowledge, and tell me which notes you used.
- My Business File is BUILDROOM_BUSINESS_FILE.md. Build Room sessions read it at the start and write it back at the end.
- Light frontmatter on every note you create: title, type, date, source, tags.
- Link generously, even to notes that don't exist yet. Never leave a new note with no links.
- External material goes under External/ (watchers) or knowledge/sources/ (things I asked for). Never edit my own notes to add external content.
- Quality gate: before filing anything, ask whether it is useful to what I'm building. Skip promo, filler, and hype.
- When I say "as my [CFO / copywriter / strategist]", answer in that role using the relevant notes as your knowledge.
- When I say "save", write a session log to memory/ with what we did and what's next.
- One output per ask. If I ask for three things, give me the first and stop.
- Don't code unless I ask you to build something. If I'm thinking, collaborate.
```

## 3. Templates (`templates/`)

`knowledge-note.md`
```
---
title:
type: note
domain:
date:
source:
tags: []
---
## TL;DR
## Notes
## Related
```

`transcript.md`
```
---
title:
type: transcript
transcript_source: meeting | video | podcast
date:
duration_minutes:
source:
status: inbox
tags: []
---
## TL;DR
## Notes
## Related
```

`entity.md`
```
---
title:
type: entity
entity_kind: person | company | tool
aliases: []
tags: []
---
```

`task.md`
```
---
title:
created:
assigned_to:
status: open
priority:
tags: []
---
## Acceptance criteria
## Plan
## Evidence
```

## 4. Day-one prompts

1. "Hi. I want you to help me get all my data into Obsidian. Ask me where it lives, one source at a time."
2. "Interview me about my business, one question at a time, and file what you learn as notes."
3. "I'm getting my Obsidian database going. Coach me: research the five best first steps for someone in my situation, then go do the first one."
4. "Here is my focus and here are my goals: [...]. Use them as the quality gate for everything you file."
5. "Write me a one-page cheat sheet of the commands I'll use most."
6. "Based on everything you know about my business, what are the five highest leveraged ways I can use this?"

## 5. Routines

| Routine | Words to say | Cadence |
|---|---|---|
| Morning briefing | "Look at my recent notes, open loops, and anything marked as a task or follow-up in my vault. Tell me my three top priorities today, what's waiting on me, and one thing I'm probably forgetting. Keep it short." | Daily, scheduled |
| Ask your brain | "Search my whole vault and answer this: [...]. Tell me which notes you used." | Daily, by hand |
| Frictionless capture | "Here's a rough, messy thought. File it properly." | Whenever |
| Weekly synthesis | "Review the notes I added or changed in the last 7 days. Surface the 3 most useful connections or patterns. Flag anything I left unfinished, and turn the single best insight into a short post in my voice." | Weekly, 20 minutes |
| Connection sweep | "Find the notes with no inbound links and connect them to what they belong with. Report what you linked." | Weekly |
| Gap finder | "Tell me what is thin or missing in my vault for [goal], then research the web to fill the single biggest gap." | Monthly |
| Save a command | "Save what you just did as a command called /[name] so I can run it with one word." | After any useful run |
| Watchers | see the Source Watcher elective | Weekly per source |

Scheduling is spoken: "run this every weekday at 7am." Confirm which mechanism the tool created (a scheduled task, cron, launchd) and where it logs.
