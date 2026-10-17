# The launch folder: what each file is

`launches/YYYY-MM-<name>/`, created by `launch_tracker.py init` (`launch_tracker.py slug --name … --event-date …` prints the name first). Inside the member's Obsidian vault when they keep one. Each script's `--help` gives every option.

| File | Made by | Shape |
|---|---|---|
| `plan.json` | `launch_plan.py math --out <slug>` and `timeline --out <slug>` (both merge into it) | The goal, the close mode, the typical path (rates, what the goal needs, what the list should give), the single-stage sensitivity, the verdict and lever, the timeline milestones (each with a date, a kind: task, send or event, and holiday or weekend flags) |
| `plan.md` | You | One screen: goal, math summary, format and dates, the offer at the close, what this session produces |
| `calendar.md` | `launch_plan.py timeline --out` | Every week from now to the debrief, every send dated |
| `belief.md` | You | The one belief, its three supports (opportunity, identity, mechanism), each in the buyer's words, and the false belief each replaces |
| `close.md` | You | The one source of truth: close mode (checkout, call, both); the doors (name, who it is for, price, payment plan with its total, checkout or booking link, backup link); the small first step if any; the deadline and why it is real, or "no deadline, window ends <date>"; the guarantee as signed off (or PENDING); cohort or install start; replay link and expiry. Every open element marked PENDING |
| `emails/NN-<job>.md` | You, one at a time | Front matter: `send` (date and time with zone), `segment`, `job`, `status` (draft, approved, scheduled, sent). Then the subject, the preview line, the body, and a facts list (every claim and where it comes from, with the proof class) |
| `proof-bank.md` | You | One entry per story: the person's own words, the class (A, B, C, D, E, H, X, R, U; `run-the-room.md` §4), the consent and its date, where it may be used |
| `event.json` | You | `title`, `organizer`, `organizer_email`, `tz`, `join_url` (a real link, or a merge field, which is then kept out of the calendar file), `registration_url`, `alarm_minutes`, `description` (shared; a day's own description is added to it), `days` [{`date`, `start`, `end`, optional `title`, `description`}], `reminders` {`morning_time`, `recap_after_end_minutes`, `sms`: false by default, true, or a list of send IDs}, optional `replay_after_end_minutes`, `prework_days_before` |
| `event.ics` | `event_ics.py build --spec event.json --out event.ics` | One event per day, UTC times; check with `event_ics.py check event.ics` |
| `runsheet.json` | You | `title`, `allow_early_pitch`, `roles` {host, moderator, tech, closer}, `links` {name: url, or {url, kind: checkout, booking, application, backup, other}}, `days` [{`date`, `start`, `end`, `tz`, `segments` [{`min`, `title`, `kind`: lobby, welcome, teach, build, proof, break, qa, pitch, close, recap, `owner`, optional `links`, `notes`}]}] |
| `run-sheet.md` | `run_sheet.py build --spec runsheet.json --event event.json --out run-sheet.md` | Clock times, role checklists, the checks (first build in the first 20–30 minutes, proof on Day 2, a break every 90 minutes, the backup link, the close links only from the pitch) |
| `tracker.json` | `launch_tracker.py` | Registrations by source, each day's peak live count, the close, sales and calls, refunds, the gate with each item's status, note and test date. Counts only; no names |
| `debrief-numbers.md` | `launch_tracker.py report --md` | The funnel against what the list should have given and against the goal, the leaks, what to protect |
| `debrief.md` | You, with the member | The two-pass debrief, the three leaks and fixes, what to protect, lessons; then `launch_tracker.py obsidian --vault …` |

A tracker made for a demo or a practice run uses `init --test`, so its numbers are labelled TEST and never read as history.
