# Drafting

## One chapter at a time
The engine drafts three chapters per pass. In a session with the member, draft **one chapter at a time** and let them read it. They may ask for two or three in a row once they trust the voice.

Before each chapter, load the context:

`manuscript.py context --book book/<slug> --chapter N`

It returns:
- the chapter's brief and its word target
- the book's promise, voice and thread
- the book record so far: the terms, framework names and people already introduced, and the promises made to the reader
- the stories already told, so none is told twice
- a summary of every earlier chapter
- the last paragraphs of the previous section

The engine gives a drafting pass only the last 1,500 characters of what came before. The summaries and the book record replace that, and they're what stops repetition and contradiction across chapters.

## The prompt

```text
You are a world-class nonfiction book collaborator working from an author questionnaire. You are writing one part of the author's complete,
full-length nonfiction book, in THEIR voice as described in the plan and their answers. The whole book runs about {words} words in {chapters} chapters; other
parts are written in other passes, so write ONLY the sections asked for below, in full, and stop.

THIS PASS: write {assignment}.
Each chapter runs about {chapter_words} words, and not less than that: long enough to teach the idea properly, with
the story, the steps, the examples, and the objections a reader would raise. Do not summarize
what other chapters will cover and do not repeat what earlier chapters already taught; a
one-line callback is fine.

Format: start every section with a line exactly like
=== SECTION: Chapter N: Title ===
using the chapter numbers and titles from the plan (for the front and back matter use
=== SECTION: Title Page ===, === SECTION: Introduction ===, === SECTION: Conclusion ===,
=== SECTION: About the Author ===). Plain prose, no markdown, blank lines between paragraphs.
Subheadings inside a chapter are allowed as a short line on its own. Every chapter delivers a
usable idea, a story from the author's answers where one exists, and a clear takeaway.
Do not invent credentials, clients, or numbers the author did not give. Never use em dashes or
en dashes. Use the author's exact framework names and phrases where they gave them.

BOOK PLAN:
{plan}

WHAT THE READER HAS ALREADY READ (the last lines of the previous section, for continuity):
{previous}

AUTHOR INTAKE:
{intake}
```

For this skill, `{assignment}` is one chapter ("Chapter 4, complete"), `{chapter_words}` is that chapter's target, and `{previous}` is the context above.

## Format
- Each section file starts with its marker line: `=== SECTION: Chapter 4: Title ===`. Front and back matter use `Title Page`, `Introduction`, `Conclusion`, `About the Author`.
- Plain prose, blank lines between paragraphs, no markdown. A subhead is a line on its own starting `@@ `.
- Save as `manuscript/ch-04.md` (`00-title.md`, `01-introduction.md`, `90-conclusion.md`, `91-about.md`).
- Never an em dash or an en dash.

## Length is measured, not assumed
A chapter's target is the book's words divided by its chapters, unless the member set that chapter's length. The introduction and the conclusion are about half a chapter each, and About the Author about 250 words.

`manuscript.py status` reports the words actually written against each target. A chapter under 60 percent of its target is "thin". The fix for a thin chapter is more of the author's material (a story, an example, a step), so ask for it. Never pad.

## After each chapter
1. `book_check.py chapter --book … --section "Chapter N"`: fix every FIX before showing the member.
2. Show the member. Their changes win.
3. Update the book record:
   - `book_plan.py record add --kind summary --chapter N --text "what this chapter established, in three or four lines"`
   - `--kind story` for each story told, `--kind framework` or `--kind term` for each new name, `--kind promise` for anything promised for a later chapter.

## Order
Title Page and Introduction, then the chapters in order, then the Conclusion and About the Author. When every planned section is written, freeze the first edition: `manuscript.py edition --label v1`.
