# The blueprint folder

Everything lives in `blueprint/` beside the Business File (inside the member's Obsidian vault if they keep one).

```
blueprint/
  blueprint.json         the state: aim, functions, positions, measures, reviews. Written by the commands
  org-chart.md           the accountability chart, as a list and a diagram            (render)
  positions/
    pos-01-owner.md      one position contract per seat                               (render)
  kpis.md                the exact definition of every measure                        (render)
  scorecard.md           the latest number recorded for each measure                  (render)
```

- `blueprint.json` is the source. Never edit it by hand; use the commands, so the documents and the record agree.
- The four kinds of `.md` file are written by `render` and are rewritten each time it runs. If the member wants to change a contract, change the position (`position remove` then `position add`, or ask the session to), then `render` again. Notes the member wants to keep go in a separate file.
- No email address is accepted in any field. A position is held by a role name or a first name.
- Nothing here is sent anywhere. The member shares a contract with a team member themselves.

## What the Business File holds

§25 keeps the summary: the aim in a line, the functions and who covers each, the positions and who holds each, counts of measures, the first item on the hand-off list, the step and its next move, the review rhythm, and a link to this folder. The detail stays here.

## How it connects to the other tools

| Need | Tool | Business File |
|---|---|---|
| A procedure a contract names | SOP Creator | §9 |
| Filling a seat | Hiring Kit | §10 |
| Teaching a seat | Training Docs | §11 |
| The weekly view of the numbers | Ops Dashboard | §12 |
| What the owner wants from all this | Compass | §17 |
