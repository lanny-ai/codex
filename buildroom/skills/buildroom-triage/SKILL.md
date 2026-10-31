---
name: buildroom-triage
description: |
  Picks the one unfinished project to finish next and parks the rest with a revisit date, in PORTFOLIO.md and the Business File's §13 Build Plan. Elective. Use for "triage my projects," "what should I finish," "help me choose," or "I have too many projects."
---

# Build Room: Triage

The owner has more started projects than finished ones. Your job is one decision: which single project gets finished next. Not a ranking of all of them, not a roadmap. One. Never use em dashes in anything you write.

## The Business File

Read `references/business-file-protocol.md` before anything else. This skill reads §1 (what the business does) and §13 Build Plan, and writes §13 and §8 only. The member's Business File lives in their Build Room folder; if this session is opened somewhere else, ask once for its path, and if there is none, carry on without it. The decision never waits on the file.

- **Read:** every §13 *Ideas & builds* row with status `scheduled` or `building` is a candidate, alongside any project folders the member points you at. §13 *Parked* rows past their revisit date are candidates too.
- **Write, once the member says yes:** the chosen project's §13 row moves to `building` with next step "say finish it in its folder"; every other candidate goes to §13 *Parked* with why and a revisit date 30 days out; anything the member calls dead is removed from §13 and named in the §8 line. One §8 Session Log line: "Triage: finishing <project>; parked <n>." PORTFOLIO.md is written as below either way.

## Gather the list

Ask for the list of unfinished projects, or, if the owner points you at a parent folder or a set of repos, scan it: one line per project with name, last modified date, and whether it has a README, tests, or git history. Do not audit each project in depth; that is finish-it's job.

## Score each one, briefly

One line per project with four quick calls on a 1 to 3 scale, proposed by you and corrected by the owner:

- Closeness: how near to a shippable v1. 3 means a few milestones away.
- Value: would finishing it produce revenue, an owned asset, or a result to show. 3 means directly.
- Pull: does the owner still want it. 3 means they lit up talking about it.
- Cost of leaving it: what breaks or bleeds if it stays unfinished. 3 means actively bleeding.

Sum them. Ties go to closeness.

## Decide

Present the top one with two sentences of reasoning and the runner-up in one sentence. Ask: "Finish this one?" If the owner picks something else, fine; the point is a single yes.

## Write it down

Write PORTFOLIO.md:

- Finishing now: the one project, the date, and the words to start: open the folder and say finish it.
- Next: at most two.
- Parked: everything else, one line each with a revisit date 30 days out. Parked is not killed; it is scheduled to be reconsidered.
- Killed: anything the owner says is dead. One line, no guilt.

## Rules

- One project leaves this session marked finishing now. Never two.
- Do not start finish-it inside this session. End with the single next action and stop.
- If the owner adds a new project during triage, write it under Parked with today's date and move on.
