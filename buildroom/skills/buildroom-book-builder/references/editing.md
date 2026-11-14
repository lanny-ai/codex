# Editing: the memo, the sample chapter, then every section

The order is fixed. Each step feeds the next.

## 1. Developmental memo and style guide
Read the complete manuscript and the intake. Produce two files with this prompt:

```text
You are a senior nonfiction book editor reading a complete manuscript. Produce, in this
order with these markers:

@@MEMO@@
A developmental memo (400 to 700 words) to the author: what works, structural issues, gaps,
repetition across chapters, pacing, and the three changes that most improve the book.

@@STYLEGUIDE@@
A compact style guide (120 to 200 words) a line editor will follow for every chapter: the
author's voice markers to preserve, recurring phrases to keep, tics to trim, and anything
to keep consistent across chapters (names, numbers, framework labels). Never use em dashes.
```

Save them as `edit/memo.md` and `edit/styleguide.md`.

**A memo that names a problem is not a fix.** Add each of the memo's changes to the issue register straight away:

`issues.py add --source memo --severity P1|P2 --location "<section or paragraph>" --issue "…" --evidence "…" --fix "…"`

Then `book_plan.py stage --name memo --status done`. The gate warns when a memo is marked done and none of its changes is in the register.

## 2. Edit one sample chapter, and ask the author
Edit Chapter 1 only, with the section-edit prompt below and the style guide. Save the original and the edit side by side in `edit/sample.md`, with the change notes.

Show the member both, and ask three things:
- Does it sound like you?
- Are your facts and stories intact?
- Is the teaching clearer without your ideas being replaced?

The member approves, or asks for changes and says what. Their feedback goes into every later edit:

`book_plan.py approve --what sample --by member --feedback "…"`

Nothing else is edited until the member approves the sample.

## 3. Edit every remaining section
One section at a time, with the style guide and the member's feedback on the sample:

```text
You are a line editor. You receive ONE section of a nonfiction manuscript plus the
book's style guide. Return the edited section only, with the exact same "=== SECTION: ... ==="
first line, then the edited prose. Preserve the author's voice, stories, numbers, names, and
any line starting with "@@ " (a subhead; keep it verbatim on its own line). Fix clarity,
rhythm, repetition, weak openings and closings. Stay within 10 percent of the original
length. Do not add facts. Never use em dashes or en dashes. Plain prose, blank lines between
paragraphs, no markdown.
After the section, add one line: @@CHANGES@@ followed by 1 to 4 short notes of what you
changed (one line each, prefixed with the section title).
```

Input for each section:

```text
STYLE GUIDE:
[edit/styleguide.md]

AUTHOR FEEDBACK ON THE SAMPLE CHAPTER (honor this everywhere):
[the member's feedback]

SECTION:
=== SECTION: [title] ===

[the section's paragraphs]
```

Rules the engine enforces, kept here:
- An edit shorter than 60 percent of the original is rejected and the original kept, with a note.
- The section marker stays exactly as it was.
- No facts are added. Stories, names and numbers are preserved.
- The edit stays within about 10 percent of the original length. `manuscript.py status` measures it.

After each section: `book_check.py chapter --section "Chapter N"`, and one line in `edit/changelog.md`. When all are done: `book_plan.py stage --name edit --status done`, then freeze an edition (`manuscript.py edition --label v2`).

## 4. Fix what the memo found
The line edit is not a structural rewrite. The memo's structural changes (a chapter in the wrong place, a missing example, a repeated story) are made on purpose, one issue at a time, with the controlled-revision prompt in `review-prompts.md` (P7). Each fix is recorded with `issues.py resolve`, and the regression check confirms it later.

## The order of all revisions
1. Factual and permission problems.
2. The book's argument and chapter order.
3. Missing explanations, examples and steps, from the author's verified material only.
4. Duplication and pacing.
5. Line edit for voice and clarity.
6. Copyedit: names, framework labels, grammar, internal references.
7. Recheck every changed claim and every chapter that depends on it.
8. Update the change log, and send the author only the questions that are needed.
