# Step 6 — One routine, that's it

Set up **one**. Three routines on day one and they'll stop trusting all three.

## The one: the morning brief
Ask exactly one question:
> *"What time should your morning brief land? (most people say 7am)"*

Then set it and say:
> *"Done. Every weekday at [time] you'll get your day in five lines. To stop it, just say **pause my control center**."*

## Later additions (only when they ask)
- Inbox sweep, twice a day — drafts replies, never sends
- End-of-day recap — what shipped, what's stuck, tomorrow's first move
- Watchers — tell me when X happens

## How you set it up
Use the host's own scheduler (Routines in Claude Code, scheduled tasks in Codex), or `cron` / Task Scheduler running `claude -p "<prompt>"`. Always set their timezone explicitly. Never make them touch any of this.

## Rules
- A local schedule needs the computer on. If they said "no" in Step 2, use the cloud path and tell them plainly: *"This one runs in the cloud, so it works even with your laptop closed."*
- Every run writes to `logs/`.
- Anything that sends or publishes stays in ask-me-first mode until they've watched it work three times.
- A routine that fails twice in a row switches itself off and tells them, instead of failing quietly forever.
