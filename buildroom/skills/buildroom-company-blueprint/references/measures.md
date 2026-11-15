# Measures

A measure is a number that tells the member whether a seat is producing what it is there for. Most businesses track too many and look at none. One to three per position to start; the script stops at five.

## Choosing

Start from the position's accountabilities and ask: "If this were going well, what would you see?" Then:

1. **Prefer the result.** Clients won, sessions delivered on time, invoices paid. These are lagging measures: they say what happened.
2. **Add one early sign** only if the member believes it moves the result: calls held, proposals sent. These are leading measures. Treat the link as a guess and check it against their own numbers after a quarter.
3. **Be wary of activity counts.** Emails sent, calls made, posts published, hours logged. They are easy to count and easy to hit without anything improving. The script warns; keep one only beside the result it is meant to produce.
4. **Ask what it will make people do.** A measure of speed alone invites sloppy work. Pair it with one of quality.

## An exact definition

Two people working it out must get the same number. `blueprint.py kpi add` asks for:

| Field | Flag | Example |
|---|---|---|
| Name | `--name` | Enquiry to client rate |
| Why it matters | `--purpose` | Shows whether calls turn into clients |
| Kind | `--kind` | lagging |
| How it is worked out | `--formula` | clients won divided by enquiries qualified |
| What counts on top | `--numerator` | clients who paid in the month |
| What counts underneath | `--denominator` | enquiries marked qualified in the month |
| Where the number comes from | `--source` | the CRM's monthly report |
| How often | `--period` | month |

A rate without both halves defined is refused. Settle the awkward cases now: does a client who paid in instalments count once? Does an enquiry from last month that closes this month count here or there?

## Baseline

The baseline is the number today, read off the member's records, with where it was read: `--baseline 0.2 --baseline-basis "CRM, July to September"`.

If nobody has measured it, give neither. It is recorded as "not measured yet", and the first job is to count it for a full period. Never estimate a baseline. A guessed starting point makes every later number meaningless.

## Target

A target is optional and comes with its basis:

| Basis | Meaning |
|---|---|
| `member history` | They have done it before |
| `member decision` | They have decided this is what good looks like |
| `contract or law` | A client contract or a rule requires it |

There is no fourth basis. An industry average is not one: it mixes businesses with different definitions, and a session cannot check it. If the member asks "what is a good number?", say that honestly and ask what theirs has been.

Set `--direction up` or `down` so it is clear which way is better.

## Trigger

A trigger is the number at which someone looks into it: `--trigger-below 0.15` or `--trigger-above 5`. It is not a pass mark. It exists so a bad month is noticed in that month.

## Starter ideas, by kind of business

Ideas to consider. None comes with a number, and none is right for every business.

| Business | Results worth looking at | Early signs some owners watch |
|---|---|---|
| Coaching and consulting | New clients · clients who renew · sessions delivered on the agreed date | Discovery calls held · proposals sent |
| Agencies and done-for-you services | Projects delivered on time · work sent back for changes · clients kept past a renewal | Briefs received complete · days from signing to start |
| Local and home services | Jobs finished right first time · estimates that become jobs · return visits | Enquiries answered the same day |
| Clinics and practices | Appointments kept · follow-ups completed · patients who return | Reminders sent before appointments |
| Courses and memberships | Members who stay · lessons completed · questions answered within the member's own standard | New trials started |
| Any business, money side | Invoices paid on time · cash in the bank at month end · gross margin | Invoices sent within the member's own standard |

For clinics and anything involving care: a number never outranks a professional's judgement or a client's safety, and no measure should reward selling treatment.

## Common mistakes

- **A target with no baseline.** Nobody knows how far away it is.
- **Fifteen measures.** Nobody looks at any of them.
- **Measuring what is easy.** The CRM counts emails, so emails get measured.
- **Changing the definition quietly.** If the definition changes, remove the measure and add a new one, so the old numbers are not compared with the new.
- **Using one number to judge a person.** See `reviews.md`.
