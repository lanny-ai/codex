# Built for owners and rooms aged 55 to 75

Nothing in the research behind this skill addresses this age group directly, so these choices are the skill's own, built on WCAG 2.2 and the W3C's notes on older users. They apply on both sides of the screen: the member presenting, and an audience that is often the same age, on a laptop or tablet with reading glasses.

## The room

- **Slides a 70-year-old can read from across the room.** One idea a slide; at most about 25 words; titles at 40pt or more, body text at 28pt or more (university accessibility guides set 24pt and 32pt as floors; older eyes on a laptop need more). Sans serif. Contrast at least 4.5:1, aiming for 7:1 (WCAG 2.2 SC 1.4.3 is 4.5:1; contrast sensitivity falls sharply with age, per the W3C's older-users notes). Nothing in the lower right corner, where the presenter's video sits. `slide_builder.py` builds to these numbers and `webinar_check.py` measures them.
- **Captions on, and said.** Zoom's automatic captions are free on every account: turn them on and tell people where the CC button is in the first three minutes. Required for live media under WCAG 2.2 SC 1.2.4.
- **Say aloud what is on screen** when pointing at it, and post every link in the chat as well as on screen.
- **Simple chat prompts.** "Type yes" or "type 1 or 2", never a question that needs typing a paragraph. Explain once where the chat is.
- **Join from anything.** Many in this audience use a tablet. The confirmation says how to join on a computer, a tablet and a phone, and that they can phone in for audio.
- **Time zones in plain words.** "2 p.m. Pacific, 5 p.m. Eastern", with a short table; never a time without its zone.

## The presenter

- **Notes, not a script.** Speaker notes are prompts of a few words, so the member talks rather than reads. The rehearsal scorecard flags passages that sound read.
- **A moderator for every live run.** A spouse, an assistant or a member of the cohort handles the chat, drops the links, watches the time and calls "ten minutes left". The skill writes their sheet (`moderator-sheet.md`). The presenter does not do tech and teach at once.
- **The tech is chosen for them.** Zoom, or the tool already named in §1, with a step-by-step setup list and a test call the day before (`tools-and-setup.md`). Nothing new on the day.
- **One rehearsal, recorded.** It is the cheapest way to find the long story, the late offer and the slide nobody can read.
- **A comfortable length.** Sixty minutes, with a hard stop. A member who has more to say runs a second webinar or a bootcamp, not a longer one.

## The registration page

Reassurance lifts trust with cautious buyers [founder's research notes]: what it is, how long it runs, that it is live (or recorded, said plainly), that there will be an offer at the end, that nobody will call unless they ask, that it is recorded and the replay is available until a stated date, and how to join on any device.
