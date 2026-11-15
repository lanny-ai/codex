# Finding stages

A stage is one real place the member could speak. This is the Gig Getter's core job, done with one hard rule: **every stage has a source.**

## The source rule
`speak_pipeline.py add` takes `--source` (the page the stage was found on, or "member knows it: how") and `--seen` (the date that page was looked at). Nothing is listed from memory. If you can't search the web or open a page in this session, say so plainly and work this way instead:
- give the member the exact searches to run (below);
- they paste what a page says;
- you read it, and add the stage with that page as the source.

A stage found on an aggregator is a lead to check on the host's own site, not a fact.

## Where to look, in this order
1. **Warm stages first.** Groups the member already belongs to, their clients' teams and trade groups, their church or club, a supplier's customer day, a friend's podcast. Ask: "Where are you already a member, and who do you know who runs a meeting?" These book fastest and need no vetting beyond common sense.
2. **Local stages they can drive to.** Service clubs, the chamber, the library, business networking groups, trade suppliers' events, community colleges, local meetups. Search each town in `regions`:
   - `"<town>" Rotary club speaker` · `"<town>" chamber of commerce "speaker" OR "presenter" proposal`
   - `"<town>" library "program proposal"` · `"<town>" "<the audience's trade>" association meeting`
3. **The audience's own associations.** Where the member's buyers gather: their trade association, its state chapter, its annual conference. Search:
   - `"<audience's trade>" association "call for speakers" OR "call for proposals" OR "call for presenters" <next year>`
   - then the state or regional chapter, which decides later and is easier to get into.
4. **Podcasts their buyers listen to**, when `formats` includes it. Check the show is still publishing and has guests before anything else; many are dormant or never take guests.
5. **Companies**, for a lunch-and-learn, when the member already has a client there who can introduce them.
6. **Online summits and guest webinars**, with care: read what the organiser asks of speakers (often an email to the member's list).

Speakers bureaus are out of scope. They take speakers who already have demand.

## What to read on the host's page, and record
- who chooses speakers (the role), and how they want to be approached (a form, an email);
- what they ask for (title, description, takeaways, bio);
- the length and format;
- the deadline, or when the next round opens (`--deadline`, `--recurring`);
- whether they pay (`--pays`), and usually they don't;
- what they allow from the stage (`--selling`): most forbid a sales presentation in writing;
- who is in the room, in the host's words (`--audience`), and how many if they say (`--size`).

Anything the page doesn't say stays `unknown`. Don't fill a gap with a guess; it becomes a question for the host.

## Lead times
- Local clubs fill their calendars weeks to a few months out.
- Libraries ask for two to nine months.
- Association calls for speakers usually open nine or ten months before the event and close six to eight months before. State and chapter events run four to six months.

So a member starting today is pitching local stages for the next few months and association stages for later next year. Put the association deadlines in the pipeline now; `speak_pipeline.py today` brings each one up two weeks before it closes.

## How many
Five vetted stages make a good first list. More than fifteen unpitched is a sign of looking instead of asking. The scorecard says so.

## Tools, and how far to trust them
- **The host's own website** is the only authority for dates, rules and who decides.
- **Call-for-speakers platforms and aggregators** (Sessionize, and email lists of open calls) are free to browse and lean toward technology events. Their deadlines are often unverified. Use them as leads.
- **Speaker directories and matching services** charge fees. There's no independent evidence they bring bookings to new speakers. Never quote a price; send the member to the vendor's page, and suggest they wait until they have given a few talks.
- **Podcast databases** are useful for one thing: checking a show is active and has guests.
- **Toastmasters** is practice and feedback, not a booking source. A fine suggestion for a nervous beginner.
