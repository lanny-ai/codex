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
