# Account safety: what this skill never does, what it may do, what the member does by hand

The member's LinkedIn account is a business asset built over years. A restricted account costs more than any post earns. Read this before any session and hold to it even when the member asks otherwise; explain why, once, in plain words.

The rules below come from LinkedIn's User Agreement (section 8.2, "Don'ts"), the Help Center pages on prohibited software (a1341387), account restrictions (a1340522), spam (a1338787) and comments (a524166), the Professional Community Policies, and LinkedIn's 2026 feed announcements. LinkedIn's own pages were read through search extracts in October 2026; re-check the live wording before quoting it to a member (`linkedin-principles.md`, "Evidence and dates").

## The skill never

1. **Touches LinkedIn on the member's behalf.** No logging in, clicking, typing, sending or posting inside linkedin.com or the LinkedIn apps: no browser automation, no computer use, no Playwright or Selenium on LinkedIn, no extensions, no reuse of cookies or sessions. Section 8.2 bans "bots or other unauthorized automated methods" that add contacts, send messages, or create, comment on, like or share posts. It has no volume exception: "just one" or "at safe limits" is still a violation.
2. **Sends anything for the member:** connection requests, DMs, comments, reactions, reposts.
3. **Scrapes or bulk-copies** profiles, search results, the list of people who commented or reacted, follower lists or data about people who are not 1st-degree connections, and never calls unofficial "LinkedIn data" APIs or enrichment services.
4. **Organises, joins, recommends or simulates engagement pods,** comment swaps, "CFBR" rings, prearranged likes or reshares, or bought followers. LinkedIn says it detects these, removes their comments from "Most relevant", limits their reach and may restrict the accounts.
5. **Helps get around limits:** rotating accounts, withdrawing invitations to "reset" (it does not reset), a virtual assistant logged in as the member, several profiles.
6. **Writes engagement bait:** "comment YES", "like if you agree", reaction polls, "comment KEYWORD and I'll send it". LinkedIn's spam policy limits content "designed to artificially increase engagement", its 2026 feed update reduces "comment to agree" prompts, and one 684,000-post study found keyword-gated posts lost about half their reach from late July 2026.
7. **Publishes generic AI text.** Every draft is built from the member's own stories, numbers and opinions, carries the label "draft, edit before posting", and is edited by the member. LinkedIn asks members to "review, edit, and approve" AI-assisted content; since July 2026 readers can flag posts as "Seems like AI slop", and LinkedIn reports flagged posts get fewer views.
8. **Strips or hides AI labels** (Content Credentials on images and video) or tells the member to.
9. **Stores data the prospect did not knowingly give the member:** no profile photos, no copied profile text, no personal emails or phone numbers they did not share.

## The skill may (off LinkedIn, on the member's computer)

- Draft posts, hooks, carousels, comments, connection notes and DMs from the member's own material.
- Keep queues and calendars: the post backlog, today's comment list (accounts the member named), DM follow-ups due, a content calendar.
- Keep a local pipeline (`scripts/li_pipeline.py`) with the source signal, stage, next action, consent and objection flags and a retention date.
- Read the member's own exports: the creator analytics `.xlsx` and the Connections `.csv` (`scripts/li_scorecard.py`).
- Render the banner and carousels (`scripts/render_linkedin.mjs`).
- Warn on pace (below).
- Nothing through any LinkedIn API. LinkedIn's own scheduler does everything a solo expert needs; a member who asks about posting through a developer app is told it is possible under LinkedIn's terms but not something this skill does.

## The member does by hand

- Publishing (paste into LinkedIn, or LinkedIn's own scheduler, which takes posts from 10 minutes to 3 months ahead).
- Every connection request, DM, comment, reaction and repost.
- The final edit of every draft.
- Choosing whom to contact, after looking at the profile themselves.
- Exporting analytics and data from LinkedIn settings, and telling the skill "posted", "sent", "accepted", "replied".
- Replying personally to every comment and DM.

## Pacing guard (warn, never block the member's own judgment)

LinkedIn publishes no invitation number. When the weekly limit is hit, invitations stop for a week and cannot be restored.

| Thing | Warn above | Why |
|---|---|---|
| Connection requests | 20 a day or 80 a week | Commonly reported cap is about 100 a week; leave room |
| Personalised connection notes (free account) | 3 a month | LinkedIn Help says 5 a month on free accounts, but 2026 member reports say 3 and the page may be stale: warn from the fourth; Premium unlimited |
| Connection note length | 200 characters (300 if the member confirms Premium) | Free-account limit |
| Pending invitations | Withdraw after about 3 weeks | About 91% of eventual accepters accept within 2 weeks (Belkins 2026); withdrawing does not restore quota |
| DMs in one sitting | 15 | A human pace; the real limit is reply quality |
| Comments | No hard number; 5 thoughtful ones a day, 10 with more time | LinkedIn may limit "excessive comment creation" |

`li_pipeline.py pace` reports these from the member's own log.

## Prospect data (GDPR and good manners)

A solo expert who keeps a prospect list is a data controller. Keep it small and honest:
- **Basis:** legitimate interests, written down once in a short note (who, why, what you keep). The pipeline file starts with a standard note; show it to the member when the first record is added and let them edit it.
- **What to keep:** name, LinkedIn URL, role and company as the person shows them, the signal (with the post link), notes the member typed, stage, next action, dates. Nothing else.
- **First contact:** before the first message to anyone in the EU or UK, check a privacy notice exists (if not, a §13 row, and hold EU/UK messages until it does). Link a short privacy page from the profile (Contact info or Featured), or add one line to the first message when emailing. In the EU and UK the person must be told who you are and why you hold their details at first contact (GDPR Article 14).
- **Objections:** "please don't contact me" ends it. `li_pipeline.py forget <id>` deletes the record and keeps only a suppression line so they are never contacted again.
- **Retention:** cold records with no interaction for 12 months are flagged for deletion (`li_pipeline.py due --retention`).
- **Security:** the pipeline file stays on the member's computer; do not sync it to shared folders.

This is not legal advice. Members in regulated sectors (financial advice, health, law) follow their regulator's rules on marketing and testimonials as well.
