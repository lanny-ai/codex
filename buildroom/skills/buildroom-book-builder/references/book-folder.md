# The book folder

Everything sits in `book/<slug>/` beside the Business File (inside the member's Obsidian vault when they keep one).

```
book/<slug>/
  book.json            settings, stages, approvals, editions
  intake.json  intake.md         the fifteen answers
  sources.json  sources/         the source packet: S-001 …, with permissions; text files the checks can read
  plan.json  plan.md             the outline the member approved
  record.json                    the book record: terms, frameworks, names, stories told, promises, chapter summaries
  manuscript/
    00-title.md  01-introduction.md  ch-01.md … ch-12.md  90-conclusion.md  91-about.md
  manuscript.md                  the working copy assembled (manuscript.py assemble)
  editions/
    v1/  manuscript.md  manuscript.ids.md  map.json      frozen; never edited
    v2/  …
  edit/
    memo.md  styleguide.md  sample.md  changelog.md  issues.json
  review/
    developmental-review.md  claim-ledger.md  copyedit.md  regression.md
  readers/
    personas.json
    round-1/  round.json  reader-brief.md  summary.md  summary.json
              sim/<persona>.brief.md  sim/<persona>.md
              human/R-01.md …
  check.md             the last gate
  manuscript.docx      the export for the member
```

## book.json
```json
{"schema": "buildroom-book/1", "slug": "second-chapter", "author": "…", "working_title": "…",
 "settings": {"chapters": 12, "words": 62000, "chapter_words": {"4": 6000}, "grade_max": 9},
 "stages": {"intake": {"status": "ready", "date": "…"}, "outline": {"status": "approved"}, "…": {}},
 "approvals": [{"what": "outline", "by": "member", "date": "…"}],
 "editions": [{"label": "v1", "sha256": "…", "date": "…", "words": 61240}]}
```

Stages, in order: `intake` (ready) · `outline` (approved) · `draft` (done) · `memo` (done) · `sample` (approved) · `edit` (done) · `review` (done) · `facts` (done) · `readers` (passed, or waived) · `copyedit` (done) · `regression` (done) · `gate` (go).

## A section file
```
=== SECTION: Chapter 4: The First Client ===

Plain prose paragraphs, a blank line between them.

@@ A subhead on its own line

More prose.
```

## An edition
`manuscript.py edition --label v2` writes the text, a copy with a paragraph ID on every paragraph (`[C04-P012] …`) for reviewers, a map and a checksum. An edition is never overwritten. The gate certifies the latest edition only if the working manuscript still matches it.

## issues.json
One row per problem: `id`, `severity` (P0 to P3), `source` (memo, review, facts, simulated, human, copyedit, regression, author), `location`, `issue`, `evidence`, `fix`, `readers`, `depends`, `author_question`, `status` (open · fixed, not verified · resolved · accepted) and a history.
