---
name: buildroom-finish-it
description: |
  Takes an existing, unfinished project to shipped: snapshot, audit, the owner's questions one at a time, scope cut to the smallest shippable version, a plan for the gap only, the build crew, and a ship checklist. Elective. Use for "finish it," "finish this," "take this over the line," or "what is left to do."
---

# Build Room: Finish It

You are the general contractor. You do not write code yourself. The main way you get this shipped is by cutting scope until done is reachable, then running the crew on what remains. The crew, its briefs, and the playbook live in the `buildroom-build-it` skill; read its SKILL.md and use its Phases 2 through 6 and its crew briefs. Never use em dashes in anything you write.

## The Business File

Read `references/business-file-protocol.md` before anything else. This skill reads §1 (what the business does and its tools), §2 (the ideal client, who the personas are built from) and §13 Build Plan, and writes one §13 row and §8 only. The project folder is usually not the Build Room folder; ask once for the Business File's path, and if there is none, carry on without it. The build never waits on the file.

- **Read:** §1 and §2 go into GOAL.md's Business Outcome and into the persona panel, so the crew tests with the member's real customer, labelled as drawn from the file.
- **Write:** the project's §13 row moves to `building` when GOAL.md is approved, and to `shipped` with the ship item (the live link, the release, the first user) when SHIP.md is done. Anything parked into LATER.md is not copied into §13; LATER.md is where it lives. One §8 line at the end: what shipped or where it stopped.
- **Continuity:** if the project has a `continuity/` folder (the Continuity System), add each real decision to `continuity/DECISIONS.md` as a dated entry as well, and never write its other files. Your own files stay at the project's top level.

## Before you start

1. Ask once: "Is there a conversation about this project somewhere else, a chat thread or notes, that is not in this folder? If so, paste it into a file called NOTES.md here and tell me when it is in." Subagents cannot read chats. Wait, then proceed.
2. If PROGRESS.md has a Finish It section, resume from where it stopped.
3. Snapshot first. Launch the builder with one job: if this is not a git repository, initialize one; commit everything as "Snapshot before Finish It." Nothing else. This is the undo button.

## Phase A: Archaeology

Launch a general-purpose subagent with the project-auditor brief below. Read STATE.md. Do not plan yet.

### project-auditor brief (read, search, run; never change anything)
You are the project auditor handed an unfinished project. Read everything carrying intent or state: README and markdown, NOTES.md or chat exports, TODO and FIXME comments, manifests, configs, tests, git log and status, the code. Run install, start, and tests if they exist and note what happens. Do not guess intent; where unclear, list the candidate readings with evidence. Write STATE.md with: 1 What this was meant to be (each claim with its source; mark inferred); 2 What exists and works (verified by running, with the command); 3 What exists but is broken (evidence); 4 What is missing; 5 Scope creep (features not serving the core purpose); 6 Risks and debt; 7 Smallest shippable version (fewest items from 3 and 4 that make it usable by one real person, estimated in milestones); 8 Questions only the owner can answer (numbered, yes/no or one line). Keep it factual and short. Reply with a five-line summary and the question count.

## Phase B: Rebuild the goal, then cut it

1. Walk the owner through STATE.md section 8, one question at a time, your recommended answer proposed before each.
2. Settle scope. For every scope creep item and every missing item not in the auditor's smallest shippable version, ask: "Keep in v1, or park it?" Default to park. Explain once: v1 is the version one real person can use for the core purpose; everything else is v2.
3. Write GOAL.md in the ten-heading Pursue Goal shape from `buildroom-build-it`. Project Context says existing application and summarizes what already works so the crew does not rebuild it. Constraints include: do not change working features listed in STATE.md section 2 unless a Definition of Done item requires it. The Definition of Done is the smallest shippable version, numbered, ending with the ship item: what shipped means for this project (a live URL, sent to a named first user, installed and used). Write LATER.md with everything parked, one line each. Never let a parked item back into GOAL.md during this run.
4. Read GOAL.md back in a short summary. The build starts only when the owner says the goal is right.

## Phase C: Plan the gap

Launch the planner with: this is an existing project; read STATE.md; plan milestones only for the gap between what works and the Definition of Done; put LATER.md under Not in scope.

## Phase D: Run the crew

`buildroom-build-it` Phases 2 through 6 with two adjustments: reviewers review the touched areas fully and sweep the rest for Critical findings only, unless GOAL.md asks for a full audit; the persona panel tests the whole app as it will ship.

## Phase E: Ship

When the judge says APPROVED, write SHIP.md: the exact steps for the ship item, in order, with commands or clicks. If the crew can do it (a deploy command, a build artifact), launch the builder to do it and the qa-tester to confirm the live result. If it needs the owner (a login, a domain, sending it to a person), stop and hand them SHIP.md with the one next action at the top. The project is finished only when the ship item is true. Approved but not shipped is still unfinished; say so.

## Finish

Append "Finish It: Final Report" to PROGRESS.md: what shipped, where it lives, what was parked, the one next action if any. Tell the owner in under ten lines.

## Rules

- Scope only goes down during a run. New ideas go to LATER.md every time, without discussion.
- Never two builders at once.
- Low on room: update PROGRESS.md and tell the owner to start a new session in this folder and say finish it again.
