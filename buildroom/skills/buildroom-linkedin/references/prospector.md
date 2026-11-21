# The Prospector: from your ideal client to a conversation

_Added 2026-11-21._

The rest of the LinkedIn Engine waits for people to show a signal. The Prospector goes and finds the people who fit the member's ideal client, helps the member open with something real about each one, and then guides the conversation one question at a time until a call is earned.

The helper is `scripts/li_prospect.py`. Like everything in this skill it stays off LinkedIn: the member runs the searches, opens the profiles and sends every message themselves. `account-safety.md` applies in full.

## What it will not do, and why

- **It does not search LinkedIn, read search results, or read profiles through a browser,** including through a browser extension or computer use, even at a slow pace and even in the member's own logged-in browser. LinkedIn's terms ban automated methods of reading its pages as well as sending, and they have no "at human speed" exception. An account restricted for this is not given back. A member who asks for it is told this once, plainly.
- **It does not copy profile text or keep lists of people.** It keeps what the pipeline keeps: name, public link, role and company as shown, and one line in the member's words on what they noticed.
- **It does not send anything.**

What that leaves is the part that actually wins replies: choosing the right twenty people and saying something true to each.

## 1. The search plan, from the ideal client

Read §2 (Ideal Client) and §1. Write `linkedin/prospect-plan.json`:

- `titles`: one to eight job titles the ideal client uses about themselves. Their words, not the member's ("Owner", "Practice owner", not "decision maker").
- `keywords` or `industries`: what narrows a title to this client ("dental").
- `exclude`: who shares the title and is not a client ("student", "recruiter", "consultant").
- `locations`, `company_size`, `seniority`: only what §2 actually says. Leave out what it does not.
- `problem_words`: two to four short phrases (two to four words each) a client would type about the problem, taken from §2 Sourced language. Not the member's jargon, and not a whole sentence, which finds nothing.
- `partners`: optional. What the people who already serve the same client call themselves (for a bookkeeper to dentists: "CPA", "dental consultant"). `network` lists these connections separately, as people who could refer the member.

If §2 is thin, say so and ask the two things that matter (what do they call themselves, and where are they) before writing the plan. Do not guess a niche.

Run `li_prospect.py searches linkedin/prospect-plan.json`. It prints the searches in the order to run them:

1. **Their own network first** (`li_prospect.py network PLAN Connections.csv`): people already connected who match. They accepted the member once; they answer far more often than strangers.
2. **LinkedIn search**, with the exact string to paste and the filters to set.
3. **People talking about the problem this week** (a Posts search). Someone who posted about the problem is worth ten who only match a title.
4. **Sales Navigator filters**, only for a member who already has it. Never tell a member to buy it for this.

## 2. Twenty people, looked at properly

The member opens each promising profile themselves and tells you, for each person worth approaching:

- name, public link, role and company as shown;
- **one real thing they noticed** (the hook): a post, a comment, a new role, something they launched, a line in their About, something shared (a town, a past employer). One line in the member's own words, with the link when it is a post or a comment.

Write these to `linkedin/prospects.json`, twenty at most. For each one give:

- **fit** A, B or C, and **why**, resting on what the profile shows (the role, the company, the hook). A fit is something you can see, not a feeling.
- If nothing real was noticed, the hook kind is `none`. That person gets a blank request and no opener. Never invent something to personalise.

## 3. The opening line

One per person, written from the hook and nothing else.

- **Not connected yet:** a blank request, after a comment where there is a post to comment on. A note (`C2`, 200 characters on a free account) only for the best three, because free accounts get very few notes a month. The first message is written now and held: mark it `"after_accept": true`, and it goes only once they accept.
- **Already connected:** a first message (`DM`, under 400 characters).

This is the one rule for someone found by searching, here and in `conversation-engine.md`: a comment or a request first, never a message to a stranger.

What makes an opener work:

1. It names the thing the member noticed, in a few plain words.
2. It asks **one** question that is easy to answer and is about them.
3. It says nothing about what the member sells. No "I help", no link, no call, no price.
4. No compliment standing in for substance ("love your profile").
5. No detail that is not in the hook. No invented number, no "I saw you are struggling with".

Before the first run, ask once whether their LinkedIn is free or Premium, and whether they have a booking link. Run `li_prospect.py check linkedin/prospects.json --business-file BUILDROOM_BUSINESS_FILE.md --pipeline linkedin/pipeline.json` (add `--premium` if they have it; leave `--pipeline` off until the pipeline exists). It refuses a pitch, a link, flattery, a made-up number, an opener that does not mention the hook, a first message with no question or more than one, and a first message to someone who is not connected. It also refuses a promise of a result ("I can cut your overhead"), a problem assumed about them that they did not state, anything close to what the member refuses to claim, and anyone who has asked not to be contacted.

**The check is a net, not a judge.** It reads for known patterns. It cannot tell whether a line is true, kind or in the member's voice, and a promise put in unusual words can pass. If the member asks for a line that promises a result, say no once and say why: it is the fastest way to be ignored, and it is a claim they would have to stand behind. Then the member reads each line, changes it into how they talk, and sends it by hand.

`li_prospect.py handoff linkedin/prospects.json` prints the `li_pipeline.py add` line for each A and B fit (a C is left out; say so to the member), so the daily list, the pacing guard and the follow-ups take over. A person who fits and has shown no signal is logged as `sig:fit`.

### Comment first, then connect

Someone who fits but has shown no signal is a stranger, and a stranger gets a comment before a request. When the hook is a post (theirs, or one they commented on):

1. The member tells you what the post says, in a line or two.
2. Draft a comment of two to four sentences that adds one specific idea to it. No praise opener, no pitch, no "message me", no client result, at most one question.
3. `li_prospect.py comment --post "<what the post says>" --text "<the comment>"` checks it. The member edits it and posts it.
4. The blank request, or the note, goes a day or two later. They have now seen the member's name next to something useful.

### The daily page

By hand does not have to mean slow. Each day, write `linkedin/today.json` from `li_pipeline.py today` and the prospect file: the few people to act on, what to do for each (comment, request, note, message, reply, follow-up, invite), what was noticed or what they last said, and the words. Then:

`li_today.py build linkedin/today.json linkedin/Today.html --pipeline linkedin/pipeline.json`

It refuses to build while any line would fail the checks above, when there are more than twenty requests or fifteen messages in the day, or when someone on the list asked not to be contacted. The page gives each person one card: a button that opens their profile or the post, the words with a Copy button, a line on exactly what to press, and a tick. The member opens it, works down it, and tells you who is done. It sends nothing and opens nothing by itself.

## 4. The conversation, one question at a time

When someone replies, the member pastes the reply and you help with the next message. The path has seven stages. Each message has one job.

| Stage | The job of the message |
|---|---|
| **open** | Start a conversation about them. Nothing about the member. |
| **situation** | Understand how things are for them today. Facts first. |
| **problem** | Find out what is not working, in their words. Never name the problem for them. |
| **cost** | Let them say what it costs to leave it. Never tell them the cost. |
| **want** | Hear what they want instead, and why now. |
| **invite** | Ask whether a short call would be useful, with an easy way to say no. |
| **booked** | They said yes. Give the link or two times, answer what they asked, and stop. |

`li_prospect.py next --stage <stage> --exchanges <n>` prints the aim, how to ask, and two example shapes. They are shapes, not scripts: write the message about what this person actually said, in the member's voice.

Rules for every message:

- **One question.** Under 400 characters.
- **Use their words back to them.** If they said "chaos", say "chaos", not "operational inefficiency".
- **Fewer messages is better.** Seven stages is the most, not the target. Most real conversations cover two or three in one reply; move as fast as they do.
- **Listen before moving on.** If an answer is thin, ask them to say more before the next stage. Skip a stage only when they have already answered it unasked.
- **No pitch, link or price until the invitation,** unless they ask. If they ask what the member does, answer in one honest sentence and go back to their situation.
- **The invitation waits** for two or more real exchanges and for them to have described a problem themselves. It restates their problem in their words and makes no an easy answer. The booking link goes in the next message, after they say yes.
- **No promise of a result,** in any message. Nothing the member refuses to claim (§1), no retired line, no client result without permission.
- **Two follow-ups, then stop.** One that adds something, one that lets them off the hook. A "no" or "please don't contact me" is final: `li_pipeline.py forget`.

Check every drafted reply with `li_prospect.py say --stage <stage> --text "..." --exchanges <n>` (add `--they-asked` when they asked what the member does). Log what was sent with `li_pipeline.py touch` and each reply with `li_pipeline.py reply`.

### When the reply is not the one you hoped for

Most replies are not a neat answer to the question. Run `li_prospect.py reply --text "<what they wrote>"`. It names the kind of reply and the honest way to answer it:

| They write | What to do |
|---|---|
| "Not interested", "please stop" | It is over. No reply, or one line. `li_pipeline.py forget`. Never ask why. |
| "What do you charge?" | Answer it straight, in one sentence, with the member's real price. Then one question, or the call if it is earned. Never dodge. |
| "What is this about?", "Are you selling something?" | One honest sentence on what the member does and why they asked. Never deny it. |
| "Send me some info" | One specific thing, and a question that makes it useful. Never a brochure and a wait. |
| "We already have someone" | Respect it; one genuine question about how that is going. If it is fine, wish them well. |
| "Not right now" | Take it at face value, ask when, log the date, and leave them alone until then. |
| "Do I know you?", "How did you find me?" | Say plainly how. |
| "Talk to my office manager" | Thank them, ask if you may use their name. The member adds that person by hand, as a referral. |

A price given because they asked is checked with `li_prospect.py say ... --they-asked`, and it is the member's real price from their Business File, said in one sentence. If they have no booking link, offer two times.

If someone says stop, `li_pipeline.py forget` removes them from the pipeline. Take them out of `prospects.json` and `today.json` as well; `check --pipeline` and the daily page both refuse anyone on the stop list.

### Before the call

When a call is booked, write what was actually sent and received to `linkedin/conversations/<name>.json` and run `li_prospect.py brief` on it. It prints one page for the member to read before the call: what they first noticed, then the person's own words, word for word, under their situation, what is not working, what it costs them and what they want; the questions the person asked; and what has not been covered yet, so the member asks on the call and does not assume. Save it as `linkedin/briefs/<name>.md`. It is private: a prospect's messages are for that call, never for a post or a page.

Then the **Sales Conversations** session ("Help me with my sales call") takes over, starting from that brief.

## What to tell the member up front

- This is a few good conversations a week, done by hand. It is not a volume machine, and nothing here promises replies, calls or clients.
- Ten to twenty people in a sitting. Twenty requests a day and eighty a week is the most the pacing guard allows before it warns.
- The first message is never a pitch. If that feels slow, it is also why people answer.
