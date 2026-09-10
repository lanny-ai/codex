# Scheduled routines

Start with at most two. More than that and nobody trusts the output.

## Good first routines
- **Morning brief** (weekdays, 7:00 local): calendar, top unread email, anything due, one line each.
- **Inbox sweep** (twice daily): triage, draft replies into Drafts — never auto-send at first.
- **End-of-day recap**: what shipped, what is blocked, tomorrow's first move.

## How
- Claude Code: use the host's scheduled-trigger/cron facility (Routines), or `cron`/Task Scheduler invoking `claude -p "<prompt>"`.
- Codex: use the app's scheduled task feature.
- Always specify the operator's timezone explicitly.

## Rules
- The machine must be on for a local schedule. If 24/7 matters, use the cloud path instead and say so.
- Every routine writes to `logs/` with a timestamp.
- Every routine has a named pause phrase; put it in the handoff summary.
- A routine that fails twice in a row disables itself and reports rather than retrying blindly.
