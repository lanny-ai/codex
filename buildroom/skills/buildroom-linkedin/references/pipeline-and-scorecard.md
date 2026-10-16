# The pipeline and the weekly scorecard

What gets counted gets better. The member's own log is the source of truth, kept on their computer by `scripts/li_pipeline.py`, with numbers from LinkedIn's own exports read by `scripts/li_scorecard.py`. LinkedIn's Social Selling Index is not used: it was reportedly switched off for accounts without Sales Navigator in September 2026, and it measured activity, not clients.

## 1. Stages

| # | Stage | Enters when | Next action |
|---|---|---|---|
| 1 | `signal` | A warm signal is logged (`conversation-engine.md` §5) | Connect or first DM within 48 h |
| 2 | `warming` | Commenting on their posts; connection request sent | Wait for accept; keep commenting |
| 3 | `connected` | Accepted | First DM if there is a reason |
| 4 | `conversation` | They replied | Learn the problem; D6 |
| 5 | `qualified` | Problem, fit and timing confirmed in the DMs | D5, the call ask |
| 6 | `call-offered` | The ask was made | F1/F2 if no answer |
| 7 | `call-booked` | They booked (the §6 calendar takes over: reminders, context card) | Prepare |
| 8 | `call-held` | The call happened | Proposal or not |
| 9 | `proposal` | Proposal sent | Follow up per §16 |
| 10 | `won` / `lost` / `nurture` | Decided | Nurture: comment on their posts; re-engage on a new signal after 60 to 90 days |

## 2. What to log (and only this)

Name · LinkedIn URL · role and company as they show them · the signal (tag and a link to the post or comment) · ideal-client fit (A/B/C) · stage · touches (date, template used: C2, D1…F2, V1) · next action and date · notes the member typed · lawful basis (`legitimate-interest`) · objection flag · retention date. Nothing copied from the profile beyond role and company.

`li_pipeline.py` commands:
```
add      --name --url --role --company --signal sig:commented-my-post --fit A [--link URL] [--note "..."]
touch    <id> --template D1 [--note "..."]      # logs a message the member sent; schedules the follow-up
move     <id> <stage> [--note "..."]
today                                           # the daily list: follow-ups due, signals waiting, pacing
due      [--retention]                          # follow-ups due; records past retention
pace                                            # invitations this week, notes this month, warnings
forget   <id>                                   # objection: delete, keep a one-line suppression
week     [--from YYYY-MM-DD]                    # this week's counts for the scorecard
import-connections Connections.csv              # the member's own 1st-degree export: marks who is connected
```

## 3. Handing off to GoHighLevel (§6)

Once a conversation reaches `qualified`, it belongs in the CRM too:
- **Pipeline:** "LinkedIn Organic" with stages 4 to 10 above. `li_pipeline.py ghl-build > linkedin/ghl-build.json` writes the tags, custom fields and pipeline in the format the Decision Machine's `ghl_push.py` reads: it pushes the tags and fields from the member's `.env` key and reports the stages to create in the browser (the GoHighLevel API cannot create pipelines).
- **Tags:** `src:linkedin-organic`, the signal tag, `fit:A|B|C`, `msg:d1|fu1|fu2`, `nurture-90d`.
- **Fields:** LinkedIn URL, first signal date, offer discussed.
- The booking itself runs through the §6 calendar and its reminders. Logged by the member; never synced by scraping or extensions.

## 4. The weekly scorecard (15 minutes, same day each week)

**Inputs the member controls** (from the pipeline log): posts published (and pillar, format) · substantive comments on others' posts · connection requests sent · warm-signal DMs started · follow-ups sent.

**Outputs** (from the log and LinkedIn's export):
- From LinkedIn's creator analytics export (`.xlsx`, Analytics → Export, 7 days): impressions, members reached, engagements, new followers; per post: impressions, reactions, comments, reposts.
- Typed by the member (LinkedIn shows them but does not export them): profile viewers this week, saves and sends on the week's posts, profile views and followers gained from each post.
- From the pipeline: acceptance rate, replies and reply rate, conversations (two or more exchanges each way), calls booked, calls held, proposals, clients won and value.

`li_scorecard.py week --xlsx <export> --pipeline linkedin/pipeline.json --manual manual.json` writes `linkedin/scorecards/YYYY-Www.md`: the numbers, last week beside them, a four-week trend, and the diagnosis (`conversation-engine.md` §8) applied to the numbers.

### Starter targets (a Build Room proposal, not research; recalibrate after four weeks)

| Weekly | Months 1–3 | Established |
|---|---|---|
| Posts | 3 | 3 |
| Substantive comments on others' posts | 25–50 | 25–50 |
| Profile viewers | rising week on week | rising or steady |
| Connection requests (warm first) | 30–60 | 50–80 |
| Acceptance | ≥ 40% | ≥ 50% |
| Warm-signal DMs started | 10–15 | 15–25 |
| Reply rate on warm DMs | ≥ 25% | ≥ 30% |
| Real conversations | 3–5 | 8–12 |
| Calls booked | 1–2 | 3–5 |

Published cold-outreach benchmarks are a floor, not a target: about 28.5% acceptance and 10.4% replies (Expandi, 13.2M attempts), 1.3% of connected prospects booking a meeting (Belkins). Warm, hand-written, signal-led outreach should do far better; the member's own four-week numbers replace these.

## 5. The two clocks (say them at the start)

- **Warm outbound:** an established expert can have conversations and calls in weeks 1 to 4.
- **Content inbound:** months; 3 to 6+ months of consistent posting and commenting before inbound is dependable. Judge the content by its leading numbers (profile viewers, followers from posts, saves, comments from the right people) until then.

## 6. The monthly look back

Once a month, from four scorecards: which pillar and format brought the right people (profile viewers and conversations, not likes), which signal type converted best, which DM template got replies. Keep what worked; drop one thing that did not. Record the decision in §14 and a §13 row if something needs building (a lead magnet, a case study to collect, a newsletter).
