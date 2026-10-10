# The certainty adapter (optional)

_From the 2026-10-07 co-design: "You could do the deep research, run it through: do I have the right information, or not? What's your degree of certainty?" Both tools the member named exist. Jev is TypeSafe AI's decision model (early access since September 2026). OpenAI's Decisions API entered public beta on October 6, 2026 on a model reported as gpt-6-luna. Each takes a question with a finite set of allowed answers plus context and returns an answer with a calibrated probability. They write no prose. That makes them right for exactly two steps of this engine and wrong for the rest._

## What it changes

Without a key, Phase 2 rates every answered item in three words: **confirmed / likely / inferred**, judged by the model doing the research. With a key, `scripts/certainty.py` asks a decision model one yes/no question per item: *does the evidence directly and reliably answer this question?* The probability that comes back sets the state and the word:

| probability | state | certainty word |
|---|---|---|
| ≥ 0.8 (threshold, adjustable) | answered | confirmed |
| 0.5 – 0.8 | partial | likely |
| < 0.5 | gap | inferred |

Phase 0 gets the same treatment when the subject is ambiguous: one choice question over the candidate sites and profiles, with "none-of-the-above" always included. If the top candidate's probability is under the threshold, the run stops and asks, as the rule already says. Now there is a number behind it.

The research, the confirmation conversation, the scripted call, and the ten Genie prompts do not touch the adapter. A decision model cannot write a Shark Tank pitch.

## How to run it

1. The member puts a key in their `.env`: `JEV_API_KEY` or `OPENAI_API_KEY`. Never paste a key into the chat; never write one into the Business File or any deliverable.
2. Build the answer sheet as JSON (the script's docstring shows the shape: subject, items with id / question / evidence lines carrying their `[web: URL]` or `[client]` tags, optional identity candidates).
3. First time only: `python3 scripts/certainty.py --probe --provider jev` (or `openai`). One tiny call. It prints the parsed result and the raw response.
4. Then: `python3 scripts/certainty.py sheet.json --out scored.json`. Read the states back into the answer sheet and show the member the probabilities next to each item.

`--dry-run sheet.json` prints both request bodies and calls nothing. Use it to show a member what will be sent before they decide to spend anything.

## Schema status, honestly

- **Jev:** the request shape (`model`, `state`, `questions` keyed by id with `type` and `instructions`; `choice` options with name and description; `noul` criteria) and the response shape (`result.answers` keyed by id) come from the vendor's public README. The probe confirms it.
- **OpenAI:** the endpoint (`POST /v1/decisions`), the model id, and the three question types (predicate, choice, score) are reported by secondary sources; the exact field names were not readable from the sandbox that built this. They live in one dictionary at the top of the script, `OPENAI_SHAPE`. If the probe fails or returns nothing parsed, the vendor's error names the field; fix the dictionary once.

Pricing, as reported and unverified: OpenAI around ten cents per million input tokens with no output charge; Jev in the same range. Thirty-six predicate questions over a research brief is a fraction of a cent. Say so to the member; it is not a reason to skip the dry run.

## The limit to respect

The research paper on Jev reports accuracy near 0.96 where human annotators agreed and near 0.71 where they split. A decision model is weakest exactly where a human would hesitate. Keep the threshold conservative, keep uncertain items in the gap list, and keep the confirmation phase: the subject still gets the last word on every answered item.
