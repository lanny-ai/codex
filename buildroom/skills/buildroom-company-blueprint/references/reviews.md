# Reviews: the cause before the person

A measure nobody looks at is decoration. A measure used to blame is worse. The review is short, regular, and curious.

## Rhythm

| How often | What |
|---|---|
| Weekly, fifteen minutes | The few numbers that move weekly; anything that crossed its trigger |
| Monthly | Every measure; one procedure that needs changing |
| Quarterly | The positions themselves: is each seat still the right shape? Do the leading measures actually move the results? |

A solo owner does this alone, and it still helps. With a team, the holder of the seat brings the number; the owner does not go and fetch it.

## Recording a number

`blueprint.py review --kpi KPI-03 --value 0.18` records what the member read off the source. The value is theirs. Never work one out from memory or fill a gap in the series.

## When a number crosses its trigger

The script prints six questions. Take them in order, and stop at the first one that explains it.

1. **Is the number right?** Check the source and the definition. A changed report or a miscounted month explains a lot of alarms.
2. **Is the target or trigger fair for this period?** A holiday week, a launch, a seasonal dip.
3. **Did the procedure work as written, or is the procedure the problem?** If people who follow it get the bad result, change the procedure.
4. **Was the person trained on it, and shown how?** Told is not trained.
5. **Did they have the time, tools and information?** A seat with twice the work it was designed for will miss.
6. **Only then: is it the person?** That is a conversation between two people. It is never a score, and it is never decided from this file.

Record the answer: `blueprint.py review --kpi KPI-03 --value 0.18 --cause system --note "the reply template was out of date"`. Causes: `data`, `target`, `system`, `training`, `resources`, `person`.

`--cause person` is refused unless `--ruled-out` says, in the member's words, what was checked first. This is deliberate. Most misses are one of the first five, and a business that reaches for the person first never fixes its systems.

## What to do with the cause

| Cause | Do |
|---|---|
| data | Fix the source or the definition. If the definition changes, replace the measure |
| target | Change the target or trigger, with its new basis |
| system | Change the procedure (**SOP Creator**) and tell everyone who runs it |
| training | Teach it again, watched (**Training Docs**) |
| resources | Give the seat time, a tool, or less to do |
| person | A private, specific conversation about what is expected and what would help. Anything beyond that is an employment matter (`honesty-and-legal.md`) |

## When the member is the one who missed

Usual, for a solo owner. Same six questions. The answer is very often "resources": one person, seven positions. That is what the hand-off ranking is for.
