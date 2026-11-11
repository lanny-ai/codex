# The talk

## 1. The default: a live 60-minute webinar

`webinar_plan.py outline --format live60` writes this minute map into `webinar.json`. Minutes are from the start time; the lobby opens 5 minutes before and is not counted.

| Minutes | Block (`id`) | Job |
|---|---|---|
| −5 to 0 | Lobby (`lobby`) | A welcome slide, music, the moderator greeting people by name as they arrive, one easy chat prompt ("type where you're joining from") |
| 0–3 | The agreement frame (`agreement`) | Two or three questions the room says yes to, in the avatar's own words from §2 ("Have you ever…?"). The recording notice and "captions are on: click CC". A chat prompt in the first minute. (Jason Fladlien's agreement frame, softened: what they will be able to do by the end) |
| 3–7 | The promise and the agenda (`promise`) | What they will leave with; the three things they will learn; "what we are not covering today" (three to five real objections, each answered in a sentence as it is set aside); the plain statement that there will be an offer at the end, and how long it runs |
| 7–12 | The story (`story`) | The member's own story: where they were, an honest admission, the turning point, resolved quickly, ending on the big idea. Not a list of credentials |
| 12–20 | Teaching block 1 (`teach1`) | Belief 1 (see §2) |
| 20–28 | Teaching block 2 (`teach2`) | Belief 2 |
| 28–36 | Teaching block 3 (`teach3`) | Belief 3 |
| 36–40 | The transition (`transition`) | "So that's how to go from where you are to where you want to be. If you'd like help doing it, here's how I can help." A trial close before any price: "Would it help to have someone walk you through this?" (Frank Kern's "summary plus and if") |
| 40–50 | The offer (`offer`) | Built only from `close.md`: the doors (no more than three), who each is for, what each saves them, the guarantee as signed off, the real deadline or none, the payment plan with its total. Asked for three times, the link on screen and in the chat; the moderator drops `offer-summary.md` (Mitch Carson's three asks) |
| 50–58 | Q&A as objection handling (`qa`) | The scripted bank first (time, money, confidence, the spouse; `qa-and-objections.md`), then live questions, each answer routed back to the right door |
| 58–60 | The close (`close`) | A takeaway close ("this may or may not be for you"), the link once more, thank them, and stop on time. Don't talk past the close |

Rules for the whole hour:
- **The strongest teaching comes before minute 30.** Watch time falls off after that (`webinar-principles.md` §2).
- **The offer starts by about minute 40** (check `offer_by_minute`). In a 60-minute talk, an offer that starts after minute 45 leaves no time for questions.
- **One chat prompt per block**, easy to answer, and the presenter asks it out loud. For this audience: few, simple, never a test.
- **Nothing new on the day.** No breakout rooms, polls or apps the member has not tried with five people first.

## 2. Each teaching block

Each block is about 8 minutes and does five things, in this order:
1. **Name the false belief** in the room's words ("Most people think you need… to…").
2. **Confirm what they suspect.** Admit a fault of the member's own industry where it is true. (Michael Stevenson's "whistleblower" frame, used honestly)
3. **Teach the true belief with the first step.** Something they can do this week. Not the member's whole system: the first step, done well. (Fladlien)
4. **Show it.** One proof story from the proof bank, cited by ID and class (`P-02 · B`), with the typical result beside any number; or a live demonstration; or the member's own example (class H). A paid-program result is introduced as one.
5. **Close the loop.** Answer the block's own question in a sentence ("So, do you need…? No. You need…"), then a chat prompt ("Type 1 if you've done this, 2 if not yet").

In `webinar.json`, each block carries `loop: {question, answer}`; the check fails a block with either one empty, or with "I'll cover that inside the program" style lines that leave it open.

## 3. Other formats

`webinar_plan.py formats` lists them; `outline --format <name>` writes each minute map.

| Format (`--format`) | When it fits | Shape |
|---|---|---|
| **Three-lesson broadcast** (`broadcast3`) | The member teaches well and wants a tight, fast session; or a repeatable weekly broadcast | 60 minutes: opener with promise and offer disclosed (8), story resolved quickly (6), three lessons of 8 minutes each with a case study and an objection handled inside it, the offer at minute 38 (12), Q&A (10). (After Mike Koenigs' livecast arc) |
| **Interview webinar** (`interview`) | A client or partner with a real result, consented, who is comfortable on camera | 60 minutes: the member hosts and frames, the guest tells their story in three parts (before, the turning point, after) with the member drawing out the method; the member makes the offer, never the guest. The guest's words are proof: an ID and class from the proof bank, and their consent covers `events` and the recording |
| **Paid web class** (`paidclass`) | A small list, or a buyer who values a paid seat; $27–$97 at the door | 90 minutes: three teaching blocks of 15 minutes, a 12-minute hands-on build, then a short offer. Full value delivered for the ticket, whether or not they buy. (After Dharma Rose's paid trial class) |
| **A bootcamp day** (`bootcamp --day 1|2|3`) | The founder's own three-day format, planned with the Event Launcher | Day 1 belief and a first build in the first 20 minutes; Day 2 proof and the method in action; Day 3 the offer. Each day is its own `webinar.json` (`--day N`); the Event Launcher's run sheet joins them |
| **Call close** (`--close call` on any format) | Offers of about $2,000 and up, or anything that needs a conversation | The offer block becomes the invitation to book a call or apply: who the call is for, what happens on it, what it is not (not a pitch). The link is the booking or application link from `close.md` |

## 4. Writing it in the member's voice

- Prompts, not paragraphs. Each block's `say` is three to six short lines the member speaks from, not a script to read.
- One person, not "you guys". Talk to the one viewer in the avatar (§2).
- Stories with a damaging admission are more believable than credentials. The founder's origin story is deliberately unflattering so his credentials do not sound like bragging.
- The founder tells the room when he uses a persuasion technique. Where it fits (the stack, the deadline, the guarantee), the notes say so: "I'm going to tell you why I'm doing this."
- Retired lines and never-say claims are off limits in every block, including the story.
