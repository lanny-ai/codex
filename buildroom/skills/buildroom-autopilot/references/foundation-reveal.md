# The Foundation Reveal

The one stop in a run. The member sees their ideal client, their offer and their positioning on a single page and decides whether it is right. Done well, this is the moment they see their business said more clearly than they have said it themselves. Done carelessly, it is a page of confident guesses. The difference is specificity and honesty, not decoration.

## What makes it land

1. **Their clients' real words, first.** The quote wall is the strongest thing on the page. Fill it with real first-hand phrases from reviews, emails and transcripts, each with where it was found. Up to six. One real quote is worth showing. If there are none, the wall is left off; never fill it with lines you wrote. The page is private to the member, so a quote from a private call may appear here even when it could never be published.
2. **Specifics from their own files.** "Owns one clinic and still treats four days a week" beats "busy professional". Every specific that came from their files proves the work was done.
3. **Honest tags on every line, with the source in plain sight.** The four counts at the top (confirmed, from your files, drafted, left blank) tell the member how much is theirs and how much is yours. Where a line came from prints beside it, on screen, on a phone and on paper. A high drafted count is not a failure. Hiding it would be. Use the `source` on a drafted line for a caveat the member should see ("my wording; you skipped this question").
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
| `files` | found in their own current files or public pages. Never a finding the ledger marks stale, retired, inferred or unsettled. | required, and shown |
| `drafted` | written by you for them to check | optional note, shown |
| `reviewed` | a drafted line in a part the member marked "Looks right", set after the review. Also, from the start, a line of your wording the member said yes to in Deep Discovery (`guess_ok` in the ledger). | optional note, shown |

When the words are the member's but the choice to use them is yours (their own LinkedIn line as a tagline), tag it `files` and say so in the source: "your post of 2 June; using it as the tagline is my suggestion".

Top level: `business` (required), `date`, then three objects.

**`avatar`**: `name`, `profile`, `job_functional`, `job_emotional`, `job_identity`, `language` (a list of real client quotes; each needs a `source`; `drafted` is refused here), `pain_surface`, `pain_emotional`, `pain_identity`, `dream_90`, `dream_year`, `force_push`, `force_pull`, `force_anxiety`, `force_habit`, `trigger`, `objections_spoken` (list), `objections_unspoken` (list), `negative`.

**`offer`**: `name`, `promise`, `structure`, `phases` (list, in order, each "what happens: the outcome"), `deliverables` (list), `value`, `investment`, `guarantee`, `pitch`, `belief`, `urgency`.

**`positioning`**: `statement`, `value_prop`, `tagline`, `alternative`, `category`, `differentiator`, `villain`, `for_you` (list), `not_for_you` (list), `advantage`.

Leave out any field you cannot fill honestly. The page shows it under "Still open" and counts it at the top. Required before the page is worth showing: `avatar.profile`, `offer.promise`, and at least one of `positioning.statement`, `differentiator`, `alternative` or `value_prop`. A differentiator nobody can state honestly stays open.

**What the checker refuses in a drafted line:**

- `investment`, `value`, `guarantee` and `urgency` are facts. They are confirmed, from files, or left out.
- money, a percentage or a multiple that is not already in a confirmed or files line on the page
- the words guarantee, money back, refund, double or triple
- in `offer.promise`: any number or timeframe. A drafted promise may only restate the member's confirmed core result in a sentence. If there is no confirmed core result, there is no promise, and the offer session is blocked.
- a retired line, anywhere, when you pass `--business-file`
- a client quote whose source says only who, not where ("a client")

A decision of "none" is shown as itself: `guarantee` with the value `None`, tagged confirmed.

An avatar name, a tagline, a pitch and a positioning statement are judgement and may be drafted. `belief` and `urgency` come from a session the member runs later, so they are normally left open.

## Build it

```
python3 scripts/reveal.py check autopilot/foundation.json --business-file BUILDROOM_BUSINESS_FILE.md
python3 scripts/reveal.py build autopilot/foundation.json autopilot/Foundation_Reveal.html --business-file BUILDROOM_BUSINESS_FILE.md
```

`check` must pass first. The page is one file, works with no internet, and prints to a clean PDF. In a chat where the member cannot open a file, run `reveal.py text` and show that.

## Present it

Say very little. Something like:

> Your foundation is drafted. Open **autopilot/Foundation_Reveal.html** in your browser.
>
> It is three parts: who you serve, what you sell, and where you stand. Every line is tagged: yours, from your files, or drafted for you. Check the drafted ones hardest.
>
> At the bottom, mark each part "Looks right" or "Change this", tick **Go ahead** when you are ready for me to build the rest, press **Copy my review**, and paste it here. I will not go further until you say go.

Do not summarise the page in the chat, do not tell them it is good, and do not ask a question. Let them read it.

## After the review

- Apply each change in the member's words. Change that line's `basis` to `confirmed`. Where a comment fits no single line, change the lines it most plainly speaks to and say which you changed.
- A promise that is the member's own core result, word for word, keeps whatever number it holds ("closed by the 10th"). Give `--business-file` so the checker can see that. Any other drafted promise carries no number and no timeframe.
- The source prints beside every line, confirmed ones included, so "you told me in your review" and "from your Business File" do not look the same.
- In a part marked "Looks right", change every `drafted` line to `reviewed`. Leave `files` lines as they are. Nothing becomes `confirmed` because it was glanced at.
- A change that says what not to say goes to `autopilot.py decide --key never_claim` or `--key retired` as well.
- If who they serve, what they sell or the price changed, rerun what depends on it, rebuild the page and show it again.
- "Go ahead: yes" is a go-ahead for the page as changed. "Not yet" means rebuild and show it again. Record a go-ahead with `autopilot.py approve --words "..."`, in their words.
- Keep `foundation.json` and the page. They are the record of what was approved.
