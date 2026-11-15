# Vetting a stage

No stage is pitched until it has been vetted. Two questions: is it a good fit, and is it a bad deal?

`speak_pipeline.py vet --id ST-003 --audience 4 --decider 3 --timing 5 --offer 4 --checked "club site, last year's speaker list"`

## Fit, four scores from 1 to 5
| Score | The question | 5 looks like | 1 looks like |
|---|---|---|---|
| `--audience` (counts three times) | Are the member's buyers in the room? | The host's page describes the member's ideal client | A general public audience with no reason to hire them |
| `--decider` (twice) | Is it clear who chooses speakers and how to ask? | A named role and a form or address on the host's page | Nobody can tell who decides |
| `--offer` (twice) | Is there room to offer something useful afterwards? | The host allows a free resource or a sign-up sheet | Any follow-up is forbidden |
| `--timing` (once) | Does the date or deadline work? | Open now, a date the member can make | Closed for a year |

Score from what the host's page says, and say which scores are guesses. An audience score of 2 or less gets a warning: a full room of the wrong people brings no clients.

`--checked` is required: say what was looked at. A stage is never vetted from its own invitation alone.

## The red flags
`speak_pipeline.py flags` lists them. Add each that applies with `--flag`.

| Flag | What it is |
|---|---|
| `pay_to_speak` | The speaker is asked to pay to speak, to sponsor, or to buy a package |
| `fee_to_apply` | A fee to apply or to be "considered" |
| `selected_out_of_nowhere` | An unasked-for message says the member was "selected" or "nominated" |
| `award_for_sale` | An award, a "top speaker" list or a feature that costs money |
| `no_past_events` | No sign the event has run before: no past agenda, photos, speakers or venue |
| `audience_unclear` | Nobody will say who attends or how many |
| `pressure` | A decision is demanded in days, with a discount for deciding now |
| `ticket_quota` | The speaker must sell tickets or bring a set number of guests |
| `rights_grab` | The terms take all rights to the talk or the recording with nothing in return |
| `contact_unverifiable` | The organiser can't be found anywhere but in their own message |

A flagged stage can't be pitched. Tell the member in plain words what the flag means. Then one of two things:
- **Drop it** (`speak_pipeline.py drop --id … --reason "…"`), which is right most of the time.
- **The member accepts it**, knowing what it is: `--accept-risk --by member --reason "…"`. Only the member can. A paid, sponsored slot is an honest thing when it is called that; the question is whether the room is worth the money, and nobody can promise it will be.
- **A flag stands until it is cleared.** Vetting again without naming it does not remove it. If a closer look shows it does not apply: `vet … --unflag pay_to_speak --reason "what was checked"`. A flag raised on a stage that was already vetted takes it back to `found`, so it cannot be pitched.

## The checks to teach the member
Seven questions for any offer that arrives unasked:
1. Did I apply for this?
2. Who pays whom?
3. Is the fee stated at the start, or near the end?
4. Can I find last year's event, its venue and its speakers somewhere other than their own message?
5. Does the contact match the organisation's own website? (Write to the address on that site, not the one in the email.)
6. Is there pressure to decide today?
7. Is income or exposure "guaranteed"?

Older professionals are a known target for paid "who's who" directories and vanity awards. A real honour doesn't send an invoice.

## What you can't do
You can list the warning signs. You can't declare an offer safe, and you must never say a regulator has warned about a specific event or company unless the member shows you the page.
