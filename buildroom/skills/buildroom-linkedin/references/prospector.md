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
- `problem_words`: two to four phrases a client would use about the problem, taken from §2 Sourced language. Not the member's jargon.

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

- **Not connected yet:** a blank request by default. A note (`C2`, 200 characters on a free account) only for the best few, because free accounts get very few notes a month.
- **Already connected, or once they accept:** a first message (`DM`, under 400 characters).

What makes an opener work:

1. It names the thing the member noticed, in a few plain words.
2. It asks **one** question that is easy to answer and is about them.
3. It says nothing about what the member sells. No "I help", no link, no call, no price.
4. No compliment standing in for substance ("love your profile").
5. No detail that is not in the hook. No invented number, no "I saw you are struggling with".

Run `li_prospect.py check linkedin/prospects.json` (add `--premium` if they have it). It refuses a pitch, a link, flattery, a made-up number, an opener that does not mention the hook, a first message with no question or more than one, and a first message to someone who is not connected. Then the member reads each line, changes it into how they talk, and sends it by hand.

`li_prospect.py handoff linkedin/prospects.json` prints the `li_pipeline.py add` line for each person, so the daily list, the pacing guard and the follow-ups take over. A person who fits and has shown no signal is logged as `sig:fit`.

## 4. The conversation, one question at a time

When someone replies, the member pastes the reply and you help with the next message. The path has six stages. Each message has one job.

| Stage | The job of the message |
|---|---|
| **open** | Start a conversation about them. Nothing about the member. |
| **situation** | Understand how things are for them today. Facts first. |
| **problem** | Find out what is not working, in their words. Never name the problem for them. |
| **cost** | Let them say what it costs to leave it. Never tell them the cost. |
| **want** | Hear what they want instead, and why now. |
| **invite** | Ask whether a short call would be useful, with an easy way to say no. |

`li_prospect.py next --stage <stage> --exchanges <n>` prints the aim, how to ask, and two example shapes. They are shapes, not scripts: write the message about what this person actually said, in the member's voice.

Rules for every message:

- **One question.** Under 400 characters.
- **Use their words back to them.** If they said "chaos", say "chaos", not "operational inefficiency".
- **Listen before moving on.** If an answer is thin, ask them to say more before the next stage. Skip a stage only when they have already answered it unasked.
- **No pitch, link or price until the invitation,** unless they ask. If they ask what the member does, answer in one honest sentence and go back to their situation.
- **The invitation waits** for two or more real exchanges and for them to have described a problem themselves. It restates their problem in their words and makes no an easy answer. The booking link goes in the next message, after they say yes.
- **No promise of a result,** in any message. Nothing the member refuses to claim (§1), no retired line, no client result without permission.
- **Two follow-ups, then stop.** One that adds something, one that lets them off the hook. A "no" or "please don't contact me" is final: `li_pipeline.py forget`.

Check every drafted reply with `li_prospect.py say --stage <stage> --text "..." --exchanges <n>` (add `--they-asked` when they asked what the member does). Log what was sent with `li_pipeline.py touch` and each reply with `li_pipeline.py reply`.

When a call is booked, the **Sales Conversations** session ("Help me with my sales call") takes over.

## What to tell the member up front

- This is a few good conversations a week, done by hand. It is not a volume machine, and nothing here promises replies, calls or clients.
- Ten to twenty people in a sitting. Twenty requests a day and eighty a week is the most the pacing guard allows before it warns.
- The first message is never a pitch. If that feels slow, it is also why people answer.
