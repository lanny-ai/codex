# Agent definition — the shape every Agent Forge output takes

One markdown file. It installs as a skill (`SKILL.md` in `.claude/skills/<name>/` or `.codex/skills/<name>/`) when the workflow is something a session runs on request, or as an agent brief handed to a build session when it must run on its own. Fill every element; "none" is an answer, "TBD" is not.

```
---
name: <kebab-case-name>
description: |
  <one paragraph: what it does, the outcome it produces, when to use it, trigger phrases>
---

# <Agent name>

**Department / owner:** <who is accountable>
**Outcome:** <the one result this agent exists to produce> · **Done means:** <observable finish condition>

## Identity
<role and voice in two sentences; how it sounds; who it speaks to>

## Context
<the operating mode: planner or problem-solver, proactive or on request; the situation it runs in; what it assumes>

## Knowledge and sources
- Reads: <files, folders, sections of the Business File, a vault folder; nothing else>
- Does not read: <what is explicitly out of scope>

## Memory
<what persists between runs and where (a log file, a §13 row, a CRM field); what is forgotten>

## Tools
<the exact tools, connectors, or commands it may use; nothing more>

## Workflow
1. <step: input → action → output>
2. ...
n. <hand-off: where the output goes and who sees it>

## Boundaries
- Never: <sends, spends, deletes, publishes, contacts a customer, edits the member's own notes ...>
- Only: <folders, accounts, lists it may touch>

## Escalation
<the conditions that stop the agent and bring a human in; who; how they are notified>

## Verification
<the checks the agent runs on its own output before it counts as done; what it does when a check fails>

## Metrics
<three numbers at most; where they are recorded; who reads them and when>

## Review
- Stage: shadow → approve-each → autonomous (current: <stage>)
- Reviewed by <owner> on <date>; next review <date>
```
