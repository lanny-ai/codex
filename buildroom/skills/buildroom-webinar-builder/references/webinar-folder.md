# The webinar folder: what each file is

`launches/<slug>/webinar/`, inside the Event Launcher's launch folder (inside the member's Obsidian vault when they keep one). `webinar_plan.py outline --launch launches/<slug>` creates it, and creates the launch folder too when the Event Launcher has not. A bootcamp keeps one subfolder per day: `webinar/day-1/`, `webinar/day-2/`, `webinar/day-3/`. Each script's `--help` gives every option.

| File | Made by | What it holds |
|---|---|---|
| `webinar.json` | `webinar_plan.py outline`, then you, block by block | The whole talk (shape below). The one file every other file is rendered from |
| `script.md` | `webinar_plan.py render` | Clock times, every block's job, prompts, slides, chat prompts, proof by ID, the offer lines, the Q&A by objection |
| `speaker-notes.md` | `webinar_plan.py render` | Per block: start time, minutes, prompts, chat prompt, proof, the loop, the time call |
| `moderator-sheet.md` | `webinar_plan.py render` | Lobby welcome, chat prompts with times, every link drop and when, questions to bring forward, time calls, the setup list, what to do if the host drops |
| `qa-bank.md` | `webinar_plan.py render` | The scripted Q&A by objection, each answer with its door |
| `slides.pptx` | `slide_builder.py build` | The deck, with the speaker notes in each slide's notes |
| `registration-page.md` | You, through Kern | The page words (`registration-page.md`) |
| `offer-summary.md` | `webinar_plan.py offer-summary --close launches/<slug>/close.md --out launches/<slug>/webinar/offer-summary.md` | The "what's on offer" one-pager, copied from `close.md` |
| `check.md` | `webinar_check.py check --out` | The go-live check, GO or HOLD, item by item |
| `rehearsals/rehearsal-N.md` | `webinar_review.py review --kind rehearsal` | The rehearsal scorecard and the three fixes |
| `runs/run-N.md` | `webinar_review.py review --kind run` | The run scorecard: who stayed, the chat, the numbers, what landed, the three fixes |

The offer itself (`close.md`), the one belief (`belief.md`), the proof bank (`proof-bank.md`) and the run sheet (`runsheet.json`) stay in the launch folder, owned by the Event Launcher. This skill reads them. With `render --runsheet`, it adds the webinar as a day in `runsheet.json` (marked `"webinar"`), fills only blank or placeholder roles and links, and never replaces a day the Event Launcher wrote without `--force`.

## `close.md`, as the scripts read it

One reader (`read_close` in `webinar_check.py`) serves every command that opens `close.md`: `render --close`, `offer-summary`, `check` and `lint`. The shape it expects is a plain list, one element per line, each line starting with its name:

```
- **Close mode:** checkout
- **Door 1: The Pricing Program** for owners ready to raise one price. $1,997 in full, or 4 payments of $549 ($2,196 total). Checkout: https://…
- Backup payment link (moderator only): https://…
- **Guarantee (signed off 2026-11-20):** …
- **Deadline:** enrolment closes January 9, 2027 at midnight Pacific, because the cohort starts January 12.
- **Cohort start:** January 12, 2027
- **Replay:** available until December 10, 2026
```

- **Two other shapes are read the same way.** A heading with its value on the next line that is not blank (`## Deadline`, then `January 9, 2027 at midnight Pacific`), and a table with two columns, the element and its value (`| Deadline | January 9, 2027 |`; a header row such as `| Element | Value |` is skipped). A table with any other number of columns is refused, because nothing says which column holds the value.
- **What it must hold.** A Close mode (`checkout`, `call` or `both`); a Deadline; and the offer itself: for `checkout` or `both` at least one price, for `call` at least one door that says what the call is. The deadline is the element named Deadline, Enrolment closes, Cart closes or Doors close. With no deadline, write `- **Deadline:** none; follow-up ends <date>` (a line starting "No deadline" is read as none too). Written twice with different answers, the close mode or the deadline is refused.
- **A file that does not read is refused, by every command, with the same message**: what could not be read, and the expected shape. `render --close` and `offer-summary` write nothing (exit 1); `check` fails `offer_matches_close` with that reason instead of comparing, and `deadline_real` says it was not checked.
- **Run `webinar_check.py lint --close launches/<slug>/close.md` right after `close.md` is written or changed**, and before `render`, `offer-summary` or `check`. It prints each element it read in plain words, marks the ones kept off the one-pager, and shows what attendees would get. Exit 0 when the file reads correctly (PENDING elements are listed, not refused), 1 with the reason when it would not.
- **The one-pager never carries internal lines.** It leaves out the Close mode, anything named Backup, Signed off or Sign-off, Notes (also Internal notes, Moderator notes), everything under a heading with one of those names, and any line marked "moderator only" or "(internal)"; a sign-off note in brackets after a name ("Guarantee (signed off 2026-11-20)") is removed and the rest of the line kept. Everything else is copied word for word; a table row is written as a line. When `close.md` has a `## For attendees` part, only that part is copied, with the same lines left out. If a line that would be published still mixes the two (a backup link inside a door's line, a sign-off in the middle of a sentence), or the `## For attendees` part is empty, `offer-summary` refuses and names the line: put the internal note on a line of its own, or the attendee wording under `## For attendees`.
- **The check compares** `webinar.json`'s `close` with the Close mode (a mismatch fails `offer_matches_close`), and every price, payment count and place count. Dates are compared where the offer is stated: the title and promise, the `promise`, `transition`, `offer`, `qa` and `close` blocks, the Q&A bank, the registration page and the deck. A date said in the story or a teaching block (the member's own history, on its slide too) is not compared.
- PENDING anywhere in it holds the check and the one-pager until the member settles it; `render --close` leaves the run sheet's deadline as it was and says so (`deadline_note`) while the deadline is PENDING.

## The proof bank, as the check reads it

Cite stories by the Proof Engine's IDs. The check reads the launch's `proof-bank.md` in either layout:

```
| ID | Origin | Kind | Permission | Scope | Result (one line) | Proves | Placed |
|---|---|---|---|---|---|---|---|
| P-01 | D | result | named | site, emails, events | A price sheet in five weeks | Pricing Program | Day 2 |
```

or one heading per story:

```
## P-01 A price sheet in five weeks
- Class: D
- Permission: named
- Scope: site, emails, events
```

Columns are found by their header names, in any order. A story used on a webinar needs `events` in its scope.

## `webinar.json`

```json
{
  "title": "How to Price Your Services Without Guessing",
  "presenter": "Dana Ruiz",
  "version": 1,
  "format": "live60",
  "date": "2026-12-03", "start": "14:00", "tz": "America/Los_Angeles",
  "length_min": 60, "lobby_min": 5,
  "recorded": false,
  "close": "checkout",
  "big_idea": "…",
  "promise": "…",
  "beliefs": [{"false": "…", "true": "…"}, {"false": "…", "true": "…"}, {"false": "…", "true": "…"}],
  "not_covering": ["…", "…", "…"],
  "offer_disclosed": true,
  "roles": {"host": "Dana Ruiz", "moderator": "Sam Ruiz", "tech": "Sam Ruiz"},
  "links": {"checkout": "https://…", "backup_checkout": "https://…", "offer_summary": "https://…"},
  "segments": [
    {"id": "teach1", "kind": "teach", "title": "You don't need more clients to earn more", "min": 8,
     "belief": 1,
     "say": ["Most people think…", "Here's what I found…", "Try this this week…"],
     "chat_prompt": "Type 1 if you've raised a price this year, 2 if not yet",
     "proof": [{"id": "P-02", "class": "B", "typical": "Most clients raise one price within a month."}],
     "loop": {"question": "Do you need more clients?", "answer": "No. You need one price that pays you properly."},
     "slides": [{"title": "More clients isn't the answer", "lines": ["One price that pays you properly"], "notes": "Pause here."}],
     "notes": "…",
     "links": []}
  ],
  "qa_bank": [{"objection": "time", "question": "…", "answer": "…", "door": "…"}],
  "runs": []
}
```

- `format`: `live60`, `broadcast3`, `interview`, `paidclass`, `bootcamp` (with `"day": 1|2|3`).
- `close`: `checkout`, `call` or `both`, matching `close.md`.
- `recorded`: `true` only for the evergreen version (`evergreen.md`).
- Segment `kind`: `lobby`, `agreement`, `promise`, `story`, `teach`, `guest`, `build`, `proof`, `break`, `transition`, `offer`, `qa`, `close`, `recap`. Lobby minutes run before the start time and are not counted in `length_min`.
- Every `teach` block carries `belief` (1–3) and `loop`. Proof is cited by the proof bank's ID and class only (`{"id", "class", "typical", "label"}`); the words stay in the proof bank. A paid-program result (class D) carries `"label": "paid-program result"` and is introduced as one; a money or paid-program result (B or D) carries `typical`.
- The `offer` block carries `asks` (how many times the offer is asked for; three is the aim).
- Money appears only in the `offer`, `qa` and `close` blocks, copied from `close.md`; `webinar_check.py` compares every figure.
- Placeholders written by `outline` look like `[write: …]`; the check fails any left.
- `runs` is appended by `webinar_review.py review --log`: `{date, version, kind, registered, attended, peak, at_offer, at_end, buyers, calls_booked}`.
