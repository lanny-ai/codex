# Rehearse, review, rewrite

The founder's best final day was rewritten with AI after a day that did not land, and he tells members to record everything and ask where it went wrong. This makes it a step, with a scorecard, every time.

## Getting the files from Zoom

In Zoom settings, Recording: turn on cloud recording, **Create audio transcript** and **Save chat messages**. After the run, from Recordings, download the **Audio Transcript (.vtt)** and the **chat (.txt)** promptly: some accounts delete recordings after 30 days. For attendance, Reports, Usage (Meetings) or Webinars, Attendee report, export as CSV. With a local recording, any transcription tool that writes .vtt or .srt works; a plain text transcript works too but gives no timings.

## 1. Rehearsal ("rehearse my webinar")

The member records one full run-through with the moderator present, as if live, then:

`webinar_review.py review --kind rehearsal --transcript rehearsal.vtt --spec webinar/webinar.json --out webinar/rehearsals/rehearsal-N.md`

The scorecard (each line PASS, WATCH or FIX):
- **Time to the offer** against the plan (`offer` block start); FIX when more than 5 minutes late.
- **Total length** against the planned length; FIX when it runs over.
- **Block timings**: each block's actual minutes against planned, found by the block's cue words (its first prompt and slide titles); WATCH when a block runs 50% over.
- **Loops left open**: phrases that defer the answer ("we'll get to that", "I cover that in the program", "that's for another day") inside a teaching block.
- **Unlabelled proof**: money or percentage figures said without "typical" or "most clients" nearby.
- **Sounds read**: long runs of the script's own sentences word for word, and very long sentences without a pause.
- **Interaction**: how many times the presenter asked the room something; WATCH under one per block.
- **The offer said three times**: mentions of the door names or the link in the offer and Q&A blocks.
- **Refused words**: anything `honesty-rules.md` refuses, said aloud.

Then **the three fixes**: the three biggest FIX lines, each with the exact change to the block (approved one at a time). A second rehearsal is worth it when the first ran more than 10 minutes over or the offer started late.

## 2. A live run ("how did my webinar go")

`webinar_review.py review --kind run --transcript run.vtt --chat chat.txt --attendance attendees.csv --spec webinar/webinar.json --registered N --buyers N [--calls-booked N] --log webinar/webinar.json --out webinar/runs/run-N.md`

Everything in the rehearsal scorecard, plus:
- **Who stayed**: live at the start, the peak, still there when the offer started, still there at the end (from the attendance report's join and leave times). Drop-off by block, so the member sees which block lost people.
- **The chat**: messages per block, the questions asked (lines with a question), and which ones were not answered aloud. Counts and the questions' words only; **no attendee names are written** to the scorecard.
- **The numbers**: registered, attended, at the offer, bought or booked; the rates; against `plan.json` when there is one.
- **What landed**: the blocks with the most chat and the fewest leavers.

`--log` appends the run's numbers (date, version, registered, attended, at the offer, buyers, calls booked) to `webinar.json` `runs`, which `evergreen-ready` reads.

Then **the next version**, drafted for approval one block at a time: the three biggest fixes, then smaller ones. On approval, bump `version`, re-render, re-check, rebuild the deck.

## 3. Diagnosis ("why didn't my webinar sell")

`webinar_review.py diagnose --registered N --attended N --at-offer N --buyers N [--calls-booked N] [--close checkout|call]`

In order, and fix the first leak first:
1. **Show-up**: live attendance below about a third of registrants. The fix is outside the talk: the Event Launcher's story emails before the invite, reminders at 24 hours and 1 hour before (the 1-hour one is the best evidenced), the spam folder, the time slot.
2. **Stay to the offer**: fewer than about half of the live attendees still there when the offer starts. The fix is the first 30 minutes: a faster agreement frame, a shorter story, the strongest block first, the offer starting earlier.
3. **Close**: below about 1–5% of attendees buying for an offer under $2,000 (or few calls booked per 100 attendees for a call close). The fix is the teaching (loops left open, no gap created), the transition, unanswered objections (the Q&A bank), the offer's clarity (the one-pager), and whether the follow-up went out.

These lines are starting points from the research (`webinar-principles.md`), not promises; say so. Judge after the follow-up window closes, because most buyers buy afterwards.
