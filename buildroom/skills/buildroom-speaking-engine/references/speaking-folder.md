# The speaking folder

Everything sits in `speaking/` beside the Business File (which, when the member keeps an Obsidian vault, is the vault).

```
speaking/
  pipeline.json          the profile, the talks and every stage (speak_pipeline.py keeps it)
  profile.md             the seventeen answers, for the member to read
  talks.md               each talk: title, promise, takeaways, the 50 and 100 word descriptions
  bio.md                 the 25, 50 and 100 word bios and the introduction
  plan.md                the dated week-by-week plan (speak_pipeline.py plan)
  one-sheet/
    one-sheet.json       the content
    one-sheet.html       the page; print to PDF
  pitches/
    ST-003-1.txt         the pitch that was sent, then -2 and -3 for the follow-ups
    drafts/              pitches not yet sent
  forms/                 a call for speakers: the form's questions and the answers given
  notes/                 what a host said, their rules, the questions asked before the day
```

Names and email addresses of hosts stay in the member's own address book or CRM. The pipeline holds the role ("program chair") and the page the stage was found on.

## pipeline.json
```json
{"schema": "buildroom-speaking/1",
 "profile": {"audience": {"text": "…", "from": "§2", "draft": false, "confirmed": "2026-11-14"}},
 "profile_ready": "2026-11-14",
 "talks": [{"n": 1, "title": "…", "promise": "…", "takeaways": ["…", "…", "…"], "for": "…", "lengths": [20, 45]}],
 "stages": [{"id": "ST-001", "name": "…", "host": "…", "kind": "local", "source": "https://…", "seen": "2026-11-10",
             "audience": "…", "size": 40, "when": "", "recurring": "second Tuesday", "deadline": "",
             "contact_role": "program chair", "pays": "no", "selling": "not allowed", "status": "vetted",
             "vet": {"scores": {"audience": 5, "decider": 4, "timing": 3, "offer": 4}, "fit": 4.25, "flags": [],
                     "checked": "club site, past speakers"},
             "touches": [], "history": []}]}
```

## A stage's life
`found` → `vetted` → `pitched` → `replied` → `booked` → `delivered` → `followed_up`. From any point before delivery it can be `declined` (they said no) or `dropped` (the member's choice, with the reason kept so it isn't chased again).

- A stage needs a source to be **found**.
- It needs four fit scores, what was checked, and no unaccepted red flag to be **vetted**.
- It needs a talk on file to be **pitched**.
- Two follow-ups at most, a week apart.
- A "later" needs the date to ask again.

Never edit `pipeline.json` by hand; use the commands, so the history stays true.
`profile.md` is written from `pipeline.json` each time an answer changes; change an answer with `answer`, not in the file. `plan.md` is the member's: once it exists `plan` will not overwrite it without `--replace`, so ticks are kept. `bio.md` and `talks.md` are drafts the session writes. They are checked against the member's confirmed answers, the proof bank (`proof/proof-bank.md` and `proof/stories/`) and the Business File, and never count as a source themselves. No email address or phone number is accepted in any field: a contact's details stay in the member's address book or CRM.
