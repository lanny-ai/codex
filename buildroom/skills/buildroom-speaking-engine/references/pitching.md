# Pitching a host

One stage, one talk, one ask. The member sends every message from their own address and fills in every form themselves; `speak_pipeline.py pitch` only records that they did.

Every draft passes `pitch_check.py check --file … --kind pitch --stage ST-003` before the member sees it as ready. Write with `kern-framework.md`: short, plain, the way the member talks. The patterns in that file are structure only; never borrow its figures or claims.

## The shape of a pitch (about 150 words)
1. **Their room, first.** One line that shows you read their page: who their members are and a problem those people have. Never open on the speaker.
2. **The talk, by its title**, and what the room leaves able to do. One sentence each.
3. **Why this speaker**, in one true line from the member's own facts. Years in the work is enough.
4. **The fit to their format:** the length they run, taken from their page. Say it is educational, with no sales pitch, when their rules ask for that.
5. **One question** they can answer in a line: "Would this suit one of your spring meetings?"
6. **An easy no:** "If it is not a fit this year, just say so."
7. **Name, business, a postal address and a link to the one-sheet.** No attachments in a first email.

## By kind of host
- **Local club or chamber (the program chair).** Short and neighbourly. Mention anyone the member knows there. Offer two or three dates. Unpaid is assumed; don't raise a fee.
- **Association or conference (a call for speakers).** There is no email: there is a form, scored by a committee against a rubric. Have the member paste the form's questions. Answer each from the talk on file: the title, the 50 or 100 word description, the three takeaways as learning objectives, the bio. Match the conference theme where one is published. No sales content anywhere; committees mark it down. Check each answer with `--kind talk` or `--kind bio`. When the organisers write back with questions, the member pastes them in and you answer from the same material.
- **A warm introduction.** The best pitch is two lines from someone the host knows. Draft the two lines for the member's contact to send, and a short note from the member to follow it.
- **Podcast.** Listen first, or read three episode descriptions, and say which one this builds on. Offer a topic for their listeners, not a biography. Producers block senders of templated pitches, so every one is written for that show. Never pay to be a guest without the member knowing that is what it is.
- **A company lunch-and-learn.** Go through the client who works there. Offer what their staff will be able to do afterwards.
- **An online summit or guest webinar.** Read what speakers must do (often an email to the member's own list) before offering.

## Follow-ups
- Two at most, a week apart. `speak_pipeline.py follow` refuses a third and refuses one sent too soon.
- Each is shorter than the last (about 70 words), adds one useful thing (a date that opened, a sentence on the talk), and keeps the easy no. Check with `--kind followup`.
- After two with no answer: `reply --outcome later --ask-again <date>` for a stage worth trying next season, or `drop`.
- When the date comes, `today` brings it back: one short note, recorded with `follow --id … --text-file …`, and then it is theirs to answer. A stage parked for later is not counted as an answer on the scorecard.
- Any pitch or follow-up sent in writing (email, a form, LinkedIn) is recorded with `--text-file`, and is refused if it does not pass `pitch_check.py`. Only a phone call or a conversation in person is recorded without text.

How many follow-ups, and how far apart, is practitioner opinion and practitioners disagree. There's no data on reply rates for speaker pitches. Never tell the member what rate to expect; their scorecard will show their own.

## The rules for cold email, in plain words (not legal advice)
- In the United States, the law on commercial email covers email to businesses too. A pitch whose purpose is to promote the member's services is a commercial message. The habits that keep it right: a truthful subject line and sender, the member's real postal address, a plain way to say "no more", and stopping when asked.
- **Other countries differ.** Canada asks for consent first, with narrow exceptions. The United Kingdom treats sole traders like individuals. If the host is outside the United States, say the rules differ and point the member to that country's regulator before anything is sent.
- A message through a host's own speaker form, or to an address the host published for speaker proposals, is the cleanest route. Use it when it exists.

## What never goes in a pitch
A figure, credential or client result that isn't in the member's own material; a testimonial that isn't in the proof bank; "award-winning", "best-selling", "keynote speaker" or "as seen on" unless it is true and recorded; a retired line; pressure; a fee demand to a stage that doesn't pay.
