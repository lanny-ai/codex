# The conversation engine: attention → conversation → call

Posts earn attention; conversations earn clients. This is the daily routine that turns the first into the second, by hand, about 20 minutes a day. Every message below is a draft the member edits and sends themselves (`account-safety.md`).

## 1. The daily 20 minutes

| Minutes | What | Output |
|---|---|---|
| 0–10 | **Comment** on 5 to 10 posts from the watch list (below), substantively | Comments the member writes, logged as "commented" |
| 10–13 | **Reply** to comments on the member's own recent posts; open a second exchange with the fitting ones | Warm signals logged |
| 13–17 | **Act on warm signals:** connection requests and first DMs to people who signalled (commented, viewed and fit, new role, inbound request) | `li_pipeline.py signal` / `touch` |
| 17–20 | **Follow-ups due today** (`li_pipeline.py due`) | Follow-ups sent or closed |

`li_pipeline.py today` prints this list from the member's own log. On a busy day: comments and follow-ups only.

## 2. The watch list (whose posts to comment on)

Three tiers, named by the member, kept in `linkedin/watch-list.md` (names and profile links the member chose; no scraping):
- **Tier A, 10 to 20 ideal clients.** Comment before any DM; it warms the relationship and shows the member's thinking.
- **Tier B, 10 to 20 peers and complementary experts** whose audience is the member's buyer (an accountant for a CFO, a lawyer for an M&A advisor). Their comment sections are where buyers already are.
- **Tier C, 3 to 5 larger voices in the niche**, for reach.
Turn on the notification bell for tiers A and B so their posts surface. Commenting on off-topic posts teaches the feed the wrong topic [practitioner: van der Blom]; stay inside the pillars.

## 3. What a good comment is

LinkedIn has said commenting regularly can triple profile views (reported secondhand), and automated or excessive comments are limited [LinkedIn Help a524166]. Two to four sentences, one specific idea, never "Great post!", never a pitch.

- **K1, add a layer** [practitioner: Welsh's formula]: "[Specific line from the post] is the part most people skip. With [client type] the version that bites is [concrete example or number]. Do you see [X] or [Y] more often?"
- **K2, respectful nuance** [practitioner: Alić]: "Agree on [point]. One nuance from [N] years doing [X]: it flips when [condition]. We saw that with a [client type] who [brief result]."
- **K3, mini-framework:** "Three things that made this work for my clients: 1) … 2) … 3) …. Number 2 is the one people underrate."
- **K4, reply on your own post, open a second exchange:** "Thanks [Name]. When you hit [their issue], what did you try first?"
- Comment within the first few hours of a post when you can. Write each one; the skill may suggest an angle from the member's story bank, never the finished comment pasted blind.

## 4. Connection requests

**Who, in order** [built on LinkedIn's 2022 InMail data: recent activity +45%, profile viewed +78%, shared connection +45%]:
1. People who engaged with the member's posts
2. People who viewed the profile and fit the ideal client
3. Tier A accounts the member has commented on for a week or two
4. Peers and referral partners
5. Event and community co-members
6. Cold ideal-client profiles (last)

**Note or no note:** five datasets agree a note does not raise acceptance; two show it lifts replies (8.2% versus 5.3%, Belkins 2026). Free accounts get about 5 personalised notes a month, 200 characters each. So: **blank requests by default; save notes for tiers 1 and 2, citing the signal.**
- **C2, signal note** (≤200 characters): "Hi [Name], enjoyed your comment on [Person]'s post about [topic], especially [specific]. I work on the same problem with [client type]. Good to be connected."
- **C3, welcoming an inbound request that fits** (as a DM after accepting, only with a real reason): "Thanks for connecting, [Name]. Saw you're [role] at [company]. What's taking most of your attention right now on [area]? No agenda, I like knowing who's here."
Withdraw requests still pending after three weeks (withdrawing does not restore the weekly quota).

## 5. Warm signals (the only reasons to start a DM)

| Signal | Tag | Source the member sees |
|---|---|---|
| Commented on the member's post | `sig:commented-my-post` | Notifications |
| Commented on a peer's post about the member's problem | `sig:commented-peer-post` | The thread |
| Viewed the profile and fits | `sig:viewed-profile` | "Who viewed your profile" (free: last 90 days, a few names) |
| New role in the last 90 days | `sig:new-role` | Their profile or notification |
| Posted about the problem the member solves | `sig:posted-problem` | Feed |
| Sent the member a connection request | `sig:inbound-connect` | Invitations |
| DM'd the member first | `sig:dm-inbound` | Messages |
| Same event or community | `sig:event` | Event page |

No signal, no DM. Cold strangers get a comment first.

## 6. DMs: conversation first, call when earned

Under about 400 characters [LinkedIn Talent data], about them, easy to say no to [practitioner: Josh Braun], one question. Message within 24 to 48 hours of the signal.

**Opening (engagement → conversation)**
- **D1, commented on my post:** "Hi [Name], thanks for your comment on my [topic] post. You mentioned [their point]. Is that something you're dealing with at [company] now, or more an observation?"
- **D2, engaged with the topic, offer the resource here (instead of comment-gating):** "[Name], noticed you've been in a few threads on [problem]. I put together a short [checklist] on [specific outcome]. Want me to send it?"
- **D3, trigger event:** "Congrats on the [new role], [Name]. In the first 90 days most [role]s I work with run into [specific problem]. On your radar yet, or too early?"
- **D4, profile viewer who fits:** "Hi [Name], saw you stopped by my profile, appreciate it. Anything around [topic] you're working through? Happy to point you to something useful."

**Deepening**
- **D6, when the pain is unclear** [practitioner: Braun's "poke the bear"]: "Out of curiosity, how are you handling [problem] today? Most [client type] I talk to either [A] or [B], and both have trade-offs."

**The call ask, only after two or more real exchanges** [practitioner: Morgan J. Ingram, "sell the meeting, not the product"; Braun, permission to say no]
- **D5:** "Sounds like [their problem, in their words]. I've helped [similar client] with exactly that. Would a 20-minute call to map your options be useful? If not, no problem, happy to keep swapping notes here."
- The link: the member's §6 booking calendar. Log "call offered", then "call booked" when it lands.

**Follow-ups: two, then stop** [data: Expandi H2 2026, 3-message sequences 9.8% versus 5.0% for 5+]
- **F1, day 3 to 5, add value (never "just bumping this"):** "[Name], one more thought on [topic]: [one-line insight or a relevant post]. No need to reply if it's not timely."
- **F2, day 7 to 10, permission to close:** "Haven't heard back, so I'll assume [topic] isn't a priority right now. Totally fine. If that changes, just reply here."
- Then nurture: keep commenting on their posts; re-engage only on a new signal, no sooner than 60 to 90 days.

**Voice notes** (mobile app, 1st-degree connections only, up to one minute [LinkedIn Help a548233]): as the second touch after someone replied, or for a strong warm signal. Under 45 seconds: their name and the signal (10 s), one insight tied to their situation (20 to 30 s), one easy question. Never as a cold first touch; never an AI voice clone.

Every DM draft goes through Kern, uses the member's voice, and is edited by the member before sending. The skill never sends.

## 7. Sales Navigator: when it is worth it

Core costs about $119.99 a month ($89.99 a month billed yearly) in October 2026 [LinkedIn pricing page; an older LinkedIn page still shows $99.99]. Worth it when the member posts consistently, has a defined ideal-client list, does the daily routine, and has hit the free account's monthly search limit; it pays for itself with one extra client a year. Useful parts: saved searches with alerts (job changes, recent posts), lead lists, 50 InMails a month. Not yet if the member is not posting or has no clear ideal client. Free alternatives: notification bells on tier A and B, "Who viewed your profile", a manual warm list in the pipeline, Google alerts for client triggers.

## 8. Diagnosis (weekly, from the scorecard)

| Symptom | Likely cause | Fix |
|---|---|---|
| Few profile views | Too few or weak comments; posts off-pillar | More substantive comments on tiers A and B; tighten pillars |
| Views up, few accepts or follows | Profile not converting | Headline and banner (profile playbook) |
| Accepts, no replies | Messages too long, about the member, or no signal referenced | Shorter, signal-first, one question |
| Replies, no calls | No clear next step, or asked too early | D5 only after two exchanges; make the call low-stakes |
| Calls, no clients | Offer or sales conversation | Route to **Sales Conversations** ("Help me with my sales call") or **Offer Deep Dive** |
