# Running the room

The member hosts. This skill writes the run-of-show, the moderator's sheet and the nightly notes, and keeps the room honest.

## 1. The run-of-show

`runsheet.json` holds each day's segments (minutes, title, kind, owner, links); `python3 <skill>/scripts/run_sheet.py build --spec launches/<slug>/runsheet.json --out launches/<slug>/run-sheet.md` turns it into clock times, per-role checklists and checks (a recording notice at the start of each day, a break at least every 90 minutes, proof on Day 2, the pitch only on the final day unless planned otherwise, every link with a value, checkout tested before the close).

A founder Day 3 run-of-show, as a shape to adapt [founder]: warm open (5 min) → finish the build promised the day before (20) → the emotional peak (7) → the promised deliverable (18) → a deep dive (25) → the biggest live demonstration (35) → the offer (30) → the close (20) → Q&A as objection handling.

## 2. Roles

- **Host**: teaches, builds live, closes. Never introduces themselves cold; the moderator or a short intro video does it. [founder's seminar rule: an emcee edifies the speaker]
- **Moderator** (essential from about 30 attendees): welcomes by name, drops every link at the planned times (and again), answers access problems, flags questions and wins for the host, drops the second checkout link if the main one fails.
- **Tech** (can be the moderator for small events): recording on with notice, backup host link, the checkout tested before the close, the replay posted the same day.
- **Closer or concierge** (for call-based offers): books calls from the chat and the application during the close.
Name each person on the run sheet; the founder's debrief faulted himself for not introducing his ops lead properly to the room. [founder]

## 3. The first hour

- "The event doesn't start at the start time, it starts in the lobby": music, a welcome slide, the moderator greeting people by name as they arrive. [founder's seminar years]
- Bring everyone in at once with energy; say who it is for; name the one belief.
- **Everyone builds or decides something in the first 20 minutes**, using the first-win tool they finished before. [founder]
- "You'll get confused, that's okay": pre-empt confusion, because a confused mind says no. [founder]
- Read the room's pre-work back to them in aggregate ("308 of you named integrity as a core value"). [founder]

## 4. Proof on Day 2, done honestly

The proof bank (`launches/<slug>/proof-bank.md`) classifies every story before it is used [founder]:
- **A** free-event result (what this event's attendees achieved);
- **B** free-event result with money;
- **C** a freedom or impact story;
- **D** a paid-program result (never presented as what the free event produces);
- **E** an outside example (someone else's public result);
- **U** uncertain (not used until confirmed);
- **H** the host's own counts and results ("308 of you finished the tool"; the host's own business numbers, with the typical result beside them);
- **X** a composite or illustration already in the member's file (never presented as proof, always labelled as an example);
- **R** retired (on the §1 list, or a paraphrase of something on it): never used.

Each entry: the person's own words, the class, the consent on file (and date), and where it may be used. On Day 2, a past success tells their own story live, introduced honestly: "this is not a testimonial… I want you to see what it looks like to take this and execute." [founder] Earnings figures carry the typical result next to them, or are not used. A featured attendee agrees in writing first.

## 5. Chat and naming

Mine the chat for builds and names to call on (with permission to say their name). Use "screenshot this one" to mark value. Celebrate wins in the room. Read out the people who came back on Days 2 and 3. [founder]

## 6. Radical transparency

The founder tells the room when he is using a persuasion technique: "Anytime I'm manipulating you, or doing something… I'm gonna tell you about it." [founder] It earns trust in an AI-wary room. The skill writes these moments into the run sheet where they fit (the stack, the deadline, the guarantee).

## 7. AI in the room

AI can make the recap (the founder's AI-made Day 3 recap from the Day 1–2 transcripts was his best single asset of the year), personalise outputs, answer FAQs in chat and draft the night email. The host shows up live, and anything AI-made is said to be AI-made. Never an AI version of a person who has not agreed, never a synthetic testimonial. [founder; research on AI trust]

## 8. Live tech

Anything new (breakout rooms, a live app, polls, music) is tried with five people before the event or not used: untried breakout rooms cost the founder about 45 minutes. Host apps on cloud infrastructure, not office internet. Keep a backup host link and a plain payment link ready. [founder]

## 9. Each night

1. Log the day: `launch_tracker.py log-day --day N --live <the peak number live at once>`.
2. Draft the night-after email (tomorrow's promise; "tomorrow is the one" before the final day).
3. Fix one thing for tomorrow (a link, a segment, a timing).
4. Update the proof bank with anything that happened today and the consents gathered.
