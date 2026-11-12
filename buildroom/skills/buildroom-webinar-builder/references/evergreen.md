# A recorded (evergreen) version, honestly

## When it unlocks

Only after a live run has converted. `webinar_review.py evergreen-ready --spec webinar/webinar.json` reads the runs logged in `webinar.json` and says READY when at least one live run has buyers (or calls booked) and a rate at or above the member's target (`--min-rate`, default 2% of live attendees buying; for a call close, `--min-calls-per-100`, default 5). Otherwise it says NOT YET and why. The member may override; the skill says plainly that a recording of a talk that did not convert live will not convert recorded.

## What changes

- **Labelled as recorded, everywhere**: the registration page, the confirmation, the first slide ("Recorded"), the opening line ("This is a recording of a session I ran live"). `webinar.json` gets `"recorded": true`, and the check fails any "live" claim (`live_claim`).
- **The Q&A**: either a real live Q&A block on a schedule (a weekly 30-minute live Q&A people can join, said so on the page), or a segment titled "The questions people most often ask", answered from the bank. Never questions read as if they were live.
- **The schedule is honest**: on-demand ("watch now") or a real schedule; never "starting soon" on a recording that starts whenever someone clicks.
- **The replay page has a real expiry**: a per-person window from a tool that tracks it, stated on the page ("available for 72 hours after you register"), and kept. No countdown that resets on reload.
- **The deadline**, if any, is the Event Launcher's real one from `close.md`, or none. A per-person deadline is honest only if each person's clock is real and disclosed.
- **The chat**: off, or a real person answering, said so. No replayed chat presented as live.
- **The offer** is re-checked against `close.md` before each new cohort, because prices and doors change.

## Then

`webinar_check.py check` again with `recorded: true`; the Event Launcher plans the evergreen sequence (`follow-up-and-debrief.md`); review the numbers monthly with `webinar_review.py diagnose`, and run it live again when it slips.
