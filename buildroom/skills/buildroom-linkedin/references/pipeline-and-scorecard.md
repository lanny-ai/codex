# The pipeline and the weekly scorecard

What gets counted gets better. The member's own log is the source of truth, kept on their computer by `scripts/li_pipeline.py`, with numbers from LinkedIn's own exports read by `scripts/li_scorecard.py`. LinkedIn's Social Selling Index is not used: LinkedIn's own page now says it "no longer accurately reflects the modern sales environment", members reported losing free and Premium access between late August and 7 September 2026, and it measured activity, not clients.

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

`li_pipeline.py` commands (run from the folder that holds the Business File; the pipeline file defaults to `linkedin/pipeline.json`, or pass `--file P`; `li_pipeline.py --help` and the script's header list every option):
```
settings [--premium yes|no] [--notes-limit N] [--pillars "A" "B"] [--basis "..."]   # creates the pipeline (only settings or init does)
add      --name --url --role --company --signal sig:commented-my-post --fit A [--connected] [--link URL] [--note "..."]
connect  <id>                                   # they are a 1st-degree connection now (or C3 / import-connections)
touch    <id> --template C2|D1|… --text "the message as sent" [--note "..."]   # logs a message the member sent; schedules the next step
                                                # --text is what the length checks read (C2 note 200/300, DM 400)
reply    <id> [--note "..."]                    # they replied; two or more replies make a real conversation
move     <id> <stage> [--value N] [--note "..."]
log-post --url <post link> --pillar "<one of the stored pillars>" --format image|carousel|text|video|poll
log-comments <n>                                # substantive comments written today
log-requests <n>                                # blank requests to people not in the pipeline (counted for pace, no names kept)
today                                           # the daily list: follow-ups due, signals waiting, pacing
due      [--retention]                          # follow-ups due; records past retention
pace                                            # invitations this week, notes this month, warnings
forget   <id>                                   # objection: delete, keep a one-line suppression
week     [--from YYYY-MM-DD]                    # counts for the last complete Monday–Sunday week
import-connections Connections.csv              # the member's own 1st-degree export: marks who is connected
ghl-build [--pipeline existing|separate] [--pipeline-name "..."] [--stages "..." ...]   # the CRM plan, JSON
list
```
Every command takes `--date YYYY-MM-DD` to log something on the day it happened. An early call ask (D5 before they have replied) is logged with a warning and does not move the stage; a DM to someone not yet connected is warned.

## 3. Handing off to GoHighLevel (§6)

Once a conversation reaches `qualified`, it belongs in the CRM too:
- **Pipeline:** read §6's CRM build line and ask the member for their sales pipeline's name and stages. Default: the member's **existing** sales pipeline, so the Funnel Scorecard sees one set of booked calls and wins (`li_pipeline.py ghl-build --pipeline existing --pipeline-name "<their pipeline>" --stages "<its stages in order>" > linkedin/ghl-build.json`); the script prints the stage map and any LinkedIn stage it could not place, and the member confirms the map before anything is pushed; LinkedIn records join it from `qualified` onward, lost is a status and nurture a tag. Only if the member wants LinkedIn tracked apart, `--pipeline separate` ("LinkedIn Organic", stages 4 to 10 above). The file is in the format the Decision Machine's `ghl_push.py` reads: it pushes the tags and fields from the member's `.env` key (`--dry-run` first) and reports any stages to create in the browser (the GoHighLevel API cannot create pipelines).
- **Tags:** lower case, in the Build Room's `src-*` style: `src-linkedin`, the signal tag (`sig-commented-my-post`…), `fit-a|b|c`, `msg-d1|fu1|fu2`, `nurture-90d` (`--tag-style colon` if the member's CRM already uses `src:`).
- **Fields:** LinkedIn URL, first signal date, offer discussed.
- The booking itself runs through the §6 calendar and its reminders. Logged by the member; never synced by scraping or extensions.

## 4. The weekly scorecard (15 minutes, same day each week)

**Inputs the member controls** (from the pipeline log): posts published (and pillar, format) · substantive comments on others' posts · connection requests sent · warm-signal DMs started · follow-ups sent.

**Outputs** (from the log and LinkedIn's export):
- From LinkedIn's creator analytics export (`.xlsx`: Me → View profile → Analytics → Show all analytics → Post impressions → choose a range that **covers the Monday to Sunday just ended** → Export; save it in `linkedin/exports/`. LinkedIn offers ranges from 7 to 365 days; the simplest habit is to make **Monday the scorecard day** and export "past 7 days" then, and if the member's account offers a custom range, set it to that Monday to Sunday. The scorecard reads the export's own date range and refuses one that does not cover the week, because an export taken mid-week mixes two weeks; daily figures are summed for the week, and LinkedIn's period totals are used only when the range is exactly the week. [Build Room; check the menu on the live site, LinkedIn moves it]). Its sheets are DISCOVERY, ENGAGEMENT, TOP POSTS, FOLLOWERS and DEMOGRAPHICS; LinkedIn does not document the columns, so the reader finds them by name, and `li_scorecard.py inspect` shows what a new export contains. TOP POSTS is LinkedIn's sample of the top 50 posts (two tables, by engagements and by impressions), merged by post link: use it to see what worked, not as totals.
- Typed by the member (LinkedIn shows them but does not export them): profile viewers this week, saves and sends on the week's posts, profile views and followers gained from each post.
- From the pipeline: acceptance rate (of the member's own requests sent that week), people who replied and the reply rate on first DMs, real conversations (two or more replies, logged with `reply`), calls booked, calls held, proposals, clients won and value.

`li_scorecard.py week --xlsx linkedin/exports/<export>.xlsx --manual linkedin/manual.json` (pipeline defaults to `linkedin/pipeline.json`; `--date` replays a past week) writes `linkedin/scorecards/YYYY-Www.md`: the numbers, last week beside them, a four-week trend, and the diagnosis (`conversation-engine.md` §8) applied to the numbers.

### Starter targets (a Build Room proposal, not research; recalibrate after four weeks)

| Weekly | Months 1–3 | Established |
|---|---|---|
| Posts | 3 | 3 |
| Substantive comments on others' posts | 25 (5 a weekday) | 25–50 |
| **Warm signals answered within 48 hours** | all | all |
| Profile viewers | rising week on week | rising or steady |
| Connection requests (warm signals, then tier A accounts after a week or two of comments) | no target; a warning above 50 | no target; a warning above 50 |
| Acceptance (the requests sent two weeks earlier, so they have had time) | ≥ 40% | ≥ 50% |
| Warm-signal DMs started | no target: it follows the signals | no target |
| Reply rate on warm DMs | ≥ 25% | ≥ 30% |
| Real conversations (two or more replies) | 3–5 | 8–12 |
| Calls booked | 1–2 | 3–5 |

Volume is never the target: the posts and comments create the signals, and the measure is that none is left unanswered. The scorecard shows at most three things below target and names the first as the one change for the week.

**`linkedin/manual.json`** (typed by the member each week; other keys are ignored with a warning): `profile_viewers`, `saves`, `sends`, `followers_from_posts`, `profile_views_from_posts`.

Published cold-outreach benchmarks are a floor, not a target: about 28.5% acceptance and 10.4% replies (Expandi, 13.2M attempts), 1.3% of connected prospects booking a meeting (Belkins). Warm, hand-written, signal-led outreach should do far better; the member's own four-week numbers replace these.

## 5. The two clocks (say them at the start)

- **Warm outbound:** an established expert can have conversations and calls in weeks 1 to 4.
- **Content inbound:** months; 3 to 6+ months of consistent posting and commenting before inbound is dependable. Judge the content by its leading numbers (profile viewers, followers from posts, saves, comments from the right people) until then.

## 6. The monthly look back

Once a month, from four scorecards: which pillar and format brought the right people (profile viewers and conversations, not likes), which signal type converted best, which DM template got replies. Keep what worked; drop one thing that did not. Record the decision in §14 and a §13 row if something needs building (a lead magnet, a case study to collect, a newsletter).
