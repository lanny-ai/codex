# Slides, speaker notes and the moderator sheet

## 1. The deck

`slide_builder.py build --spec webinar/webinar.json --out webinar/slides.pptx [--theme light|dark] [--accent RRGGBB] [--font "Arial"]`

- One slide per entry in each block's `slides` list: `{"title": "…", "lines": ["…", "…"], "kind": "title|statement|list|quote|offer|chat|link"}`. A block with no slides gets one title slide with the block's name.
- Defaults: 16:9, title 44pt, body 32pt (never below 28pt), Arial, near-black on white (`light`) or white on near-black (`dark`), the accent colour only for titles and links and only when it passes 4.5:1 against the background (otherwise refused with the contrast it measured).
- The lower right quarter is kept clear for the presenter's video.
- Each slide's speaker notes are the block's notes for that slide (`notes`), or the block's `say` prompts.
- The first slide carries the title, the presenter's name and, for a recorded version, the word "Recorded" in the subtitle. The offer slides carry the doors and prices exactly as `close.md` has them (the check compares them).
- The file opens in PowerPoint, Keynote and Google Slides (File, Import). The member may restyle it; run `inspect` on their version before going live.

`slide_builder.py inspect webinar/slides.pptx` reads any .pptx and reports, per slide: the smallest type size, the lowest contrast between text and the slide background (when both colours are set in the file), the word count, and the slides that break the rules. `webinar_check.py --deck` uses the same reader.

What the reader can and cannot see: it reads sizes and colours written in the slides. Text whose colour comes only from a theme or a picture background is reported as "colour not set in the slide" and you check it by eye.

## 2. Speaker notes (`speaker-notes.md`)

Per block: the clock time it starts, the minutes, the job of the block in one line, the prompts (three to six, a few words each), the chat prompt, the proof story by ID and class with the typical result, the loop's question and its answer, and the time call ("you should be at minute 20 now"). In PowerPoint's presenter view, the same prompts sit under each slide.

## 3. The moderator sheet (`moderator-sheet.md`)

For the person running the chat: the lobby welcome and when to post it; every chat prompt and when the presenter will ask it; every link, when to drop it and how often (the offer link and the one-pager from the start of the offer, then every few minutes through the Q&A; the backup payment link only if the main one fails); the questions from the bank to bring forward; the time calls to send the presenter (10 minutes before the offer, 10 minutes left, 2 minutes left); the recording and captions reminders; what to do if the presenter's connection drops (the backup host link from `runsheet.json`).

## 4. The script (`script.md`)

The whole hour in one file: clock times, each block's job, the prompts, slides by title, the chat prompts, proof by ID, the offer lines as `close.md` has them, the Q&A bank by objection. It is for rehearsal and for the Event Launcher's run sheet, not for reading aloud.
