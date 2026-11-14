# Intake: fifteen questions, most of them already answered

## The questions
One at a time, with the helper line. `book_plan.py intake` lists which are still open.

| Key | Question | Helper | Often already in the Business File |
|---|---|---|---|
| `about` | What is your book about, in one or two sentences? | The version you'd say out loud if someone asked at dinner. Don't polish it. | |
| `reader` | Who is this book for? Describe one real person who needs it. | Their situation, what they're struggling with, what they want. A real client or a real friend is perfect. | §2 |
| `transformation` | What is the single biggest transformation your reader gets from this book? | Where are they before, where are they after. One line each. | §3 |
| `story` | What is your story? Why are you the person to write this? | The moment you learned this the hard way. The turning point. Be specific about what happened. | §17 |
| `work` | What do you do, and how long have you been doing it? | Your work, your role, your background. Plain facts. | §1 |
| `method` | Walk me through your method or framework, step by step. | If you have names for the steps, use them. If you don't, describe what you do first, second, third. | §3, §4 |
| `mistake` | What is the biggest mistake people make in your area, and what do you tell them instead? | The thing you find yourself explaining over and over. | §4 |
| `result` | Tell me about a result. Someone you helped, what changed for them. | No names needed. What they came in with, what you did, what happened. | §18 proof vault |
| `myth` | What do people believe about your topic that is flat wrong? | The myth you'd love to kill. | §4 |
| `lessons` | What are 3 to 5 lessons that cost you years to learn? | One line each is fine. These become chapter seeds. | |
| `feel` | How do you want the reader to feel when they finish? | And what do you want them to do the next morning? | |
| `voice` | Describe your voice. How do you talk when you're teaching? | Blunt or gentle? Funny or serious? Stories or lists? Name a writer or speaker you sound like, if one comes to mind. | §17 |
| `titles` | Working title ideas, if any. | Give me a few, or say "you pick." | |
| `next_step` | What do you want the reader to do after the last page? | Book a call, join something, try one exercise, email you. The book ends by pointing there. | §3, §6 |
| `must_include` | Anything else the book must include? | A story, a quote, a client type, a warning. Anything you'd regret leaving out. | |

## How to run it
1. Read the Business File first. For each question a section already answers, write the answer in the member's words and **confirm it in one line** ("From your file: your reader is …. Still right for the book?"). Record it with `book_plan.py answer --key reader --text "…" --from "§2"`.
2. Ask the rest one at a time, with the helper. Let them talk; long, messy answers are the raw material. Record each as given.
3. Ask for sources as you go: transcripts of them teaching, talks, articles, client stories from the proof bank. Add each to the source packet (`sources-and-permissions.md`).

## The sufficiency gate
Eight answered questions is the engine's technical minimum. It isn't enough to know the material can carry a book. So before outlining, run **P1** (`review-prompts.md`) on the intake and the source packet. It labels the reader, the transformation, the method, the voice, the evidence and the exclusions as supported, unclear or missing, and returns up to seven follow-up questions.

- **HOLD:** ask the follow-up questions, one at a time. Record: `book_plan.py intake-gate --verdict hold --gap "…" --question "…"`.
- **READY TO OUTLINE:** `book_plan.py intake-gate --verdict ready`. The script refuses READY with fewer than eight answers, with a core question unanswered (about, reader, transformation, method, voice), or with gaps still listed.

If an answer is unknown, it stays unknown. Never answer a follow-up question for the author.

## The book's settings
Thirteen chapters and about 62,000 words unless the member says otherwise. Ask once, plainly: "Thirteen chapters of about 4,800 words is the default. Do you want it shorter, longer, or a different number of chapters?" Then `book_plan.py settings --chapters N --words N`. A modest intake suits a shorter book: say so.
