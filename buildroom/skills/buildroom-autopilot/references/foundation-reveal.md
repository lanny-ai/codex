# The Foundation Reveal

The one stop in a run. The member sees their ideal client, their offer and their positioning on a single page and decides whether it is right. Done well, this is the moment they see their business said more clearly than they have said it themselves. Done carelessly, it is a page of confident guesses. The difference is specificity and honesty, not decoration.

## What makes it land

1. **Their clients' real words, first.** The quote wall is the strongest thing on the page. Fill it with real phrases from reviews, emails and transcripts, each with its source. Four to six. If there are none, the wall is left off; never fill it with lines you wrote.
2. **Specifics from their own files.** "Owns one clinic and still treats four days a week" beats "busy professional". Every specific that came from their files proves the work was done.
3. **Honest tags on every line.** The three counts at the top (confirmed, from your files, drafted) tell the member how much is theirs and how much is yours. A high drafted count is not a failure. Hiding it would be.
4. **Their offer in one sentence they would say out loud.** The promise is the largest text on the page. Write it plain. If it would not survive being said to a client across a table, rewrite it.
5. **Short lines.** One or two sentences per field. The full documents hold the detail.
6. **Blanks left blank.** The page lists what is still open. That list makes everything else on the page more believable.

## The file

Write `autopilot/foundation.json`. Every value is an object:

```json
{"v": "the text", "basis": "confirmed", "source": "where it came from"}
```

| basis | Means | source |
|---|---|---|
| `confirmed` | the member said it, in this run or in their Business File | optional |
| `files` | found in their own files or public pages | required |
| `drafted` | written by you for them to check | optional note |

Top level: `business` (required), `date`, then three objects.

**`avatar`**: `name`, `profile`, `job_functional`, `job_emotional`, `job_identity`, `language` (a list of real client quotes; each needs a `source`; `drafted` is refused here), `pain_surface`, `pain_emotional`, `pain_identity`, `dream_90`, `dream_year`, `force_push`, `force_pull`, `force_anxiety`, `force_habit`, `trigger`, `objections_spoken` (list), `objections_unspoken` (list), `negative`.

**`offer`**: `name`, `promise`, `structure`, `phases` (list, in order, each "what happens: the outcome"), `deliverables` (list), `value`, `investment`, `guarantee`, `pitch`, `belief`, `urgency`.

**`positioning`**: `statement`, `value_prop`, `tagline`, `alternative`, `category`, `differentiator`, `villain`, `for_you` (list), `not_for_you` (list), `advantage`.

Leave out any field you cannot fill honestly. The page shows it under "Still open". Three are required before the page is worth showing: `avatar.profile`, `offer.promise`, `positioning.differentiator`.

Facts are never `drafted`: `investment`, `value`, `guarantee`, `urgency` and anything with a number or a date must be `confirmed` or `files`, or left out. An avatar name, a tagline, a pitch and a positioning statement are judgement and may be drafted.

## Build it

```
python3 scripts/reveal.py check autopilot/foundation.json
python3 scripts/reveal.py build autopilot/foundation.json autopilot/Foundation_Reveal.html
```

`check` must pass first. The page is one file, works with no internet, and prints to a clean PDF. In a chat where the member cannot open a file, run `reveal.py text` and show that.

## Present it

Say very little. Something like:

> Your foundation is drafted. Open **autopilot/Foundation_Reveal.html** in your browser.
>
> It is three parts: who you serve, what you sell, and where you stand. Every line is tagged: yours, from your files, or drafted for you. Check the drafted ones hardest.
>
> At the bottom, mark each part "Looks right" or "Change this", press **Copy my review**, and paste it here. I will not go further until you say go.

Do not summarise the page in the chat, do not tell them it is good, and do not ask a question. Let them read it.

## After the review

- Apply each change in the member's words. Change that line's `basis` to `confirmed`.
- If who they serve, what they sell or the price changed, rerun what depends on it, rebuild the page and show it again.
- When they say go, record their words with `autopilot.py approve --words "..."`.
- Keep `foundation.json` and the page. They are the record of what was approved.
