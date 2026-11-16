# The talk a host can book

A host books a specific talk for a specific room. This skill settles the outline: what goes on a flyer, a form and a one-sheet. Writing the whole talk, minute by minute with slides, is the **Webinar Builder's** job ("Build my webinar"); send the member there once a date is booked.

## Every talk has a job
Before the title, settle one sentence: **who is in the room, and what is the one thing they should do afterwards?** For most members that one thing is a conversation: ask for the checklist, book a call, come and talk at the end. Plan the talk backwards from it. A talk with no job is pleasant and brings nobody.

## One talk that stretches
The member needs one talk, not a catalogue. Build it so it stretches like an accordion: the same spine at 20 minutes for a lunch meeting, 45 for a breakout and 90 for a workshop, with more examples and exercises as the slot grows. Start with the short one; hosts who liked it ask for the longer one.

## What a talk on file holds
`speak_pipeline.py talk add --title "…" --promise "…" --takeaway "…" --takeaway "…" --takeaway "…" --for "…" --length 20,45`
To take a talk off file: `speak_pipeline.py talk remove --n 2` (not once it has been pitched; the record of what was offered stays). To change one, remove it and add it again.

- **Title:** twelve words at most, plain, about the room's problem, not the speaker. No dashes. "Cash Before Profit: Three Numbers Every Trades Owner Should Read" beats "Unlocking Financial Mastery".
- **Promise:** one sentence on what the room leaves able to do. "You'll leave able to read three numbers that tell you where the cash went."
- **Three takeaways:** each a thing the audience can do or decide, starting with a verb. Association forms call these learning objectives and score them, so write them to be scored: "Read a 13-week cash view", not "Understand cash flow".
- **Who it is for:** the audience in the host's words.
- **Lengths:** the lengths the member can give it at. Local clubs run about 20 minutes plus questions; breakouts 45 to 60. One talk, cut to fit, is better than three talks.

One talk is enough to start. Three at most.

## When the member says "need help with topics"
Draft from the Business File first, then ask only what it doesn't answer, one question at a time:
1. What do you know better than almost anyone in the room would? (§1, §3)
2. What do people already ask your advice on, every time? (§2, §4)
3. Which of those do you care about enough to talk on for years?
4. What mistake do you see so often you could spot it from across the room? (§4 common enemy, if there)
5. Which story do you find yourself telling to explain it? (§17)

Then offer **three** candidate talks, each as a title, a promise and three takeaways, built only from what they said. They pick one, change the words until it sounds like them, and it goes on file. Never suggest a topic the member has no experience in because it is fashionable.

## Building the outline
A simple build that works for a first-time speaker. This skill takes it as far as the outline; the Webinar Builder writes it out.
1. **Fifteen down to five.** List every point the member could make. Keep the five the room most needs, in the order they would do them. For a 20 minute talk, three.
2. **Each point in four sentences:** the point, why it is true, an example, the point again.
3. **A fact, then a story.** Alternate something to know with something that happened: a client situation told with permission, or the member's own.
4. **The opening and the close are written out word for word** and learned. Everything between is spoken from notes.
5. **The close is the job:** the one thing to do next, said once and plainly, in whatever form the host allows.

## The description hosts print
For each talk write two versions, from the talk on file, in the third person:
- **50 words** for a newsletter or a flyer.
- **100 words** for a programme or a form.

Each says who it is for, the problem, what they leave with, and one line on why this speaker. No sales language: committees mark it down and many hosts forbid it. Check each with `pitch_check.py check --kind talk`.

## Fitting the talk to a host
Never send the same description everywhere without reading the host's page. Change:
- the example to their members' trade or situation;
- the length to their slot;
- the takeaways' wording to their theme, where an association has published one.

The substance stays the member's own. Hosts complain most about canned talks and about a sales pitch dressed as a talk.

## Rehearsal
Before the first pitch goes out, the member says the talk aloud once, timed, even from notes. A talk that has never been spoken isn't ready to be offered. For a booked date, the Webinar Builder's rehearsal scorecard does this properly.
