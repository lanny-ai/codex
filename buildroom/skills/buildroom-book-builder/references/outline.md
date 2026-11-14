# The outline

## The prompt
The outline is planned from the author's intake and source packet with this prompt. `{words}` and `{chapters}` come from the book's settings (twelve chapters and about 62,000 words unless the member changed them).

```text
You are a world-class nonfiction book collaborator working from an author questionnaire. The author has answered an intake questionnaire. You are
planning their complete, full-length, publish-ready nonfiction book, about {words} words in
{chapters} chapters, written in THEIR voice as described in their answers.

Produce the book plan and nothing else, in exactly this plain-text format:

TITLE: <the title>
SUBTITLE: <the subtitle>
PROMISE: <one sentence, the transformation the reader gets>
VOICE: <three or four sentences describing how this author talks, drawn from their answers: pace,
humor, favorite words, what they refuse to say>
THREAD: <two or three sentences: the single argument the whole book makes, and the story from
the author's life that the book keeps returning to>
CHAPTER 1: <title>
BRIEF: <four to six sentences: the one idea this chapter delivers, the story or example from the
author's answers it uses, the framework or steps it teaches, and the takeaway the reader leaves
with. Name the author's exact framework names and phrases where they gave them.>
CHAPTER 2: <title>
BRIEF: ...
(continue through CHAPTER {chapters})
CONCLUSION: <three sentences: how the book lands, and the first action the reader takes>

Rules: build a real arc, not a list of tips: early chapters establish the problem and the
author's story, the middle chapters teach the method step by step, the late chapters handle
objections, mistakes, and what changes when it works. Spread the author's stories across the
chapters so none repeats. Do not invent credentials, clients, or numbers the author did not
give. Never use em dashes or en dashes.

AUTHOR: {author}

AUTHOR INTAKE:
{intake}
```

## Then put it in plan.json
`book/<slug>/plan.json`:

```json
{"title": "…", "subtitle": "…", "promise": "…", "voice": "…", "thread": "…", "conclusion": "…",
 "chapters": [{"title": "…", "idea": "the one idea, in a line", "brief": "four to six sentences",
               "stories": ["the phone call from the bank"], "sources": ["S-002"]}]}
```

- `stories` names each story from the author's material the chapter uses. A story is told once; `plan-check` refuses a story planned for two chapters.
- `sources` lists the source-packet IDs the chapter draws on.
- `book_plan.py plan-check` validates it and writes `plan.md` for the member to read.

## Check the arc before a word is written
- Early chapters set up the problem and the author's story. Middle chapters teach the method step by step. Late chapters handle objections, mistakes and what changes when it works.
- Does each chapter earn the next? Would a reader notice if one were removed?
- Is anything said twice? Is a step of the method missing?
- If the intake is too thin to fill a chapter, cut the chapter or ask the author. Never stretch thin material across more chapters.

## The member approves it
The engine this skill comes from has no outline approval. This skill adds one, because a weak outline makes a weak book whatever the prose is like.

Show the member `plan.md`: the title and subtitle, the promise, and one line per chapter. They change what they want. Then:

`book_plan.py approve --what outline --by member`

No chapter is drafted before this.

## Changing the shape
The member can change the number of chapters, the total length, or one chapter's length at any time:

`book_plan.py settings --chapters 9 --words 40000 --chapter-words 4=6000`

A change to the chapter count after approval sends the outline back for approval.
