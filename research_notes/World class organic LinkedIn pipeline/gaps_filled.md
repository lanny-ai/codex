# Gaps filled: organic LinkedIn pipeline research (2026-10-16)

## How this was made (read first)
- **Every item below comes from web search results.** WebFetch failed on every host (DNS "ENOTFOUND"), and the proxy blocks linkedin.com. The search tool returns short extracts and summaries of pages, not full pages. A quote marked "(extract)" is wording the search tool showed from that page. Nobody has checked it against the live page.
- **Exceptions (files read in full):** two public GitHub repos were cloned and their files read directly (item 10). They are practitioner sources, not LinkedIn.
- **Evidence tags:**
  - **[LI]** = verified LinkedIn primary (LinkedIn newsroom, help or business page, seen as a search extract).
  - **[LI-via-press]** = a LinkedIn statement or exec quote as reported by press.
  - **[DATA n=…]** = a data study, with its sample size.
  - **[PRAC]** = practitioner or vendor claim.
  - **[UNVERIFIED]** = a source exists but conflicts with others or gives no method.
  - **[TRAINING]** = my prior knowledge, not confirmed in this session.
- About 105 searches were used. Where a date is a page's "seen" date rather than its publication date, it says so.

## Summary (10 lines)
1. **2026 feed changes, in order:**
   - 12 Mar 2026: Engineering post on LLM retrieval and Generative Recommender ranking.
   - Mar 2026: newsroom post "How LinkedIn Is Improving the Feed…", which covers pods, comment automation, engagement bait and an Interest Picker.
   - ~20 May 2026: "Keeping conversations real on LinkedIn" (Lorenzetti). Generic or AI posts and automated comments travel less beyond the first-degree network; LinkedIn reports 94% detection accuracy.
   - 30 Jul 2026: "Seems like AI slop" button.
   - ~9 Aug 2026: comments ranked per viewer.
2. **"See more" fold:** LinkedIn publishes no number. Planning figures are about 140 characters on mobile and about 210 on desktop, or about 3 lines. Line breaks move the fold.
3. **Length:** AuthoredUp (372k posts) finds the best engagement at about 1,300 to 2,500 characters. Ordinal (248k) peaks at 2,000 to 3,000. LigoSocial (134k) finds 2,400+ beats 600 to 900. The middle band (600 to 1,500) is weakest in two datasets.
4. **Frequency:** Buffer (2M posts, 94k accounts) shows per-post impressions rising with frequency, with 2 to 5 posts a week as the "sweet spot". LinkedIn's Sachdeva says 2 to 5 a week, and that "posting more than once a day won't hurt your total reach". The van der Blom 18-hour rule dates from 2023. Ordinal finds 2-week gaps had no engagement effect (small sample).
5. **Best times disagree:** Buffer 2026 (4.8M posts) says 3 to 8 pm, Wednesday first. Sprout 2026 says Tuesday to Thursday, roughly 11 am to 5 pm. Hootsuite says early morning Tuesday and Wednesday. Treat these as a test, not a rule.
6. **Formats:**
   - Newsletters: subscribers are auto-invited only on the first edition (help page).
   - Articles: about 0.65x the reach of text posts (AuthoredUp).
   - Polls: highest reach multiplier but lowest engagement.
   - Live: must be scheduled from 22 Jun 2026.
   - Video: not the reach leader in 2026 data.
7. **Practitioner systems:** Welsh's Content Matrix (themes x styles) is confirmed on his blog; the exact list of 8 styles is not confirmed. SLAY = Story, Lesson, Actionable, You (secondary only). Alić: "first three lines" and a "1-to-9" idea framework (secondary).
8. **DMs:** no Lavender LinkedIn-specific data exists publicly; its finding is from email (25 to 50 words gets +65% replies). Braun: poke the bear and the Trigger/Think/Third-party/Talk structure (secondary). Voice-note data is vendor-only. InMail credits per LinkedIn pages: Career 5, Business 15, All-in-One 30, Sales Navigator Core 50, Recruiter Lite 30.
9. **SSI:** LinkedIn's own page "From SSI to AI" says the score "no longer accurately reflects the modern sales environment". Users reported free and Premium access locked from about 27 Aug to 7 Sep 2026. No formal retirement notice exists.
10. **Exports:**
    - Creator analytics XLSX sheets are DISCOVERY, ENGAGEMENT, TOP POSTS, FOLLOWERS, DEMOGRAPHICS. Confirmed by one practitioner parser; LinkedIn does not document them. Column headers were not confirmed.
    - Connections.csv columns are First Name, Last Name, URL, Email Address, Company, Position, Connected On. The file has a "Notes:" preamble above the header.

---

## 1. LinkedIn's own 2026 feed announcements

| # | Title / URL | Date | Key wording (as quoted in extracts or coverage) | Tag |
|---|---|---|---|---|
| a | "Engineering the next generation of LinkedIn's Feed", LinkedIn Engineering Blog, H. Danchev. https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed | 12 Mar 2026 (per PPC Land, Herdl, ZenML) | One LLM-based retrieval system replaces "a fragmented set of independent retrieval pipelines". Ranking uses a "Generative Recommender" sequential transformer that reads a member's feed history as an ordered sequence (one summary says 1,000+ past interactions). Runs on H100 GPUs. Feed of "1.3 billion" members. Search Engine Land: the system "prioritizes topical relevance and engagement patterns, LinkedIn said"; embeddings update "within minutes" and retrieval takes "under 50 milliseconds". | [LI-via-press]; post itself not opened |
| b | "How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content". https://news.linkedin.com/2026/ImprovingTheFeed | Mar 2026 (SMT and SEL coverage in March; LinkedIn Community recap 1 Apr 2026) | (extract) Larger sequence models "known as Generative Recommenders, augmented with large language models (LLMs)". It says LinkedIn is "working to make engagement pods ineffective and curb comment automation or third party tools that create fake conversations". It is reducing recycled and engagement-bait posts. It is testing an **Interest Picker** at sign-up with topics like "Leadership," "Job Search Skills," "Career Growth". Per SEL, LinkedIn will show less content "designed purely to drive comments or clicks". | [LI] |
| c | "What We're Doing to Support Authentic Content and Conversations on LinkedIn". https://news.linkedin.com/2026/authentic-content-and-conversations | 2026 per URL; exact date not found (SMT follow-up dated 16 Feb 2026 suggests Feb 2026) | (extract) "We actively limit the reach of inauthentic activity, including engagement pods and automated comments", using "technology and human review". LinkedIn "removed groups" showing pod behaviour and contacted members suspected of pods or automation. Engagement pods "are not allowed"; automated comments "aren't allowed". It mentions 100M+ members with at least one verification. Sachdeva (via SMT, Nov 2025) defined automated comments as those posted via third-party scripts or plugins "without human review". | [LI] |
| d | "Keeping conversations real on LinkedIn", Laura Lorenzetti (VP, Executive Editor). https://news.linkedin.com/2026/keeping-conversations-real-on-linkedin | ~20 May 2026 (one French outlet; other outlets mention "May"). Unconfirmed. | (extract) "In our initial testing, we're correctly identifying generic content 94% of the time." It acts on "comments… created and posted at scale using automation tools" with little human involvement, and on "replies that only restate the original post". AI-looking content lacking a clear point of view will be "less likely to be widely distributed beyond a person's immediate network". AI is fine as long as posts "represent your voice and your perspectives". No false-positive rate has been published (TNW). | [LI] |
| e | "Seems like AI slop" option (see item 8) | 30 Jul 2026 | CPO Hari Srinivasan: flags train "a series of new and improved classifiers". Flagged content gets about 40% fewer views. LinkedIn blocks "hundreds of thousands" of automated comment attempts a day and "billions" of other automation attempts. The "Enhance your post" tool is replaced by a proofreader. | [LI-via-press] (Fortune 31 Jul 2026) |
| f | Comment ranking change. Reported by Social Media Today: https://socialmediatoday.com/news/linkedin-updates-feed-display-to-drive-more-post-replies-and-comments/827394 | ~9 Aug 2026 | Comments are ordered per viewer using "professional interests, connections and engagement activity". LinkedIn "will also surface more current, timely discussions in the feed". The stated driver is Q2 data: time spent in post comments +18% YoY against about 10% growth in overall consumption. **No LinkedIn newsroom post or on-record quote found.** | [LI-via-press] (single trade source; others cite SMT) |

Related: SMT "LinkedIn uses AI to improve feed relevance" (https://www.socialmediatoday.com/news/linkedin-uses-ai-to-improve-feed-relevance/819792/) quotes CTO Erran Berger. The aim is to read a member's activity "as part of a continuous professional journey" rather than through separate per-surface models. [LI-via-press]

**Implication for the skill:** distribution beyond the first-degree network now depends on (a) topical clarity and a consistent topic (LLM retrieval), (b) not looking generic or AI-written (classifier plus reader flags), and (c) real comments. Pods, automation and bait are named targets in LinkedIn's own posts.

---

## 2. Hooks and post structure

**"See more" fold**
- LinkedIn publishes no fold figure. All numbers are third-party. [PRAC]
- Common planning numbers: about **140 characters mobile, about 210 desktop**. Some sources say 150 on mobile or about 250 on desktop. Line breaks trigger the fold early, and one tool says it is set by "visual space", not a hard count. Sources: contentin.io/blog/linkedin-post-specs (8 Jun 2026); unilink.us/blog/linkedin-character-limits-2026; linkedinpreview.com/blog/linkedin-see-more-cutoff-2026. [PRAC]
- Jasmin Alić (quote page, secondhand): focus on "the first three lines of text, including spaces", because that is where LinkedIn cuts posts. https://rosetta.to/person/jasmin-alic [PRAC]
- Hard limits: posts 3,000 characters (LinkedIn help, per secondary). Comments 1,250 characters, with a fold at about 800 (2026 limits reference). [PRAC]
- **Skill rule:** keep the hook and its payoff within the first 140 characters, ideally 1 to 2 short lines. Preview on mobile.

**Post length (data studies)**
| Study | Sample | Finding | Tag |
|---|---|---|---|
| AuthoredUp. https://authoredup.com/blog/linkedin-character-limit | 372,126 personal posts, Sep 2025 to Feb 2026 | Median engagement peaks at **1,301 to 2,000 characters (2.61%)** and **2,001 to 2,500 (2.67%)**. Near 3,000 is still fine. A secondary summary says 1,301 to 2,500 characters get +27% engagement against posts under 400. | [DATA n=372k] |
| AuthoredUp (same page, newer data) | 709,195 posts, Jul 2025 to Jun 2026 | Best length by format: image posts 800 to 1,000 characters, video captions 1,000 to 1,200, carousel captions 800 to 1,000, polls 400 to 600. The gain from hitting these is only about 3 to 5%. | [DATA n=709k] |
| Ordinal. https://www.tryordinal.com/blog/linkedin-post-size | 248,275 posts, 2024 to 2026 | Best at **2,000 to 3,000 characters (1.33% engagement rate)**; weakest at 600 to 1,500. | [DATA n=248k] |
| LigoSocial. https://ligosocial.com/research/linkedin-post-length | 134,522 posts, Jan 2023 to Sep 2026, within-author comparison | Posts of 2,400+ characters get about +24% engagement against the same authors' 600 to 900 character posts. Under 150 characters gets -31%. | [DATA n=134k] |
| Buffer | not found | Optimal 1,300 to 1,900 characters. Seen only via ViralBrain; no Buffer primary found. | [UNVERIFIED] |
| Metricool 2026 | 673,658 posts, about 65k accounts | No length finding found in extracts. | n/a |
| Van der Blom | 1.8M posts (2025) | Length figures are not public in extracts. | n/a |

**Skill default:** for text posts, aim for about 1,300 to 2,500 characters (about 200 to 400 words). Short "one-liners" under 150 characters underperform. Do not sit in the 600 to 1,000 range by default.

**White space and formatting**
- Stan Store analysis (6 months of posts; sample not stated). In the 800 to 1,200 character band, posts with 41+ line breaks had **0.675%** engagement against **0.147%** with 1 to 5 breaks. A 1,000-character wall of text did worse than a shorter formatted post. https://stan.store/blog/linkedin-engagement/ [DATA, n not stated]
- AuthoredUp emoji data: **843,470 posts**. 0 to 1 emoji gives about +7% median engagement and +22% median reach; gains flatten after about 2. AuthoredUp calls line breaks "the biggest single move in our data" but published no number. https://authoredup.com/blog/linkedin-text-formatting [DATA n=843k] / [PRAC] for the line-break claim
- "3x engagement for formatted posts" (Cleverly) and "300%" figures cite no source. [UNVERIFIED]

**First-line (hook) patterns**
- AuthoredUp hook study, as reported by Ordinal: **309,614 posts, Dec 2025 to May 2026**. Median engagement by hook type:
  - **story 2.60%**
  - contrarian 2.31%
  - statement 2.27%
  - results 2.19%
  - **question 2.16% (last)**
  - Sources: https://www.tryordinal.com/blog/linkedin-hooks and a RedactAI German blog. [DATA n=310k, secondhand]
- Ordinal advice: hooks under about 10 words and under about 40 characters clear the fold. Turn questions into "a specific, unanswered claim". [PRAC]
- ConnectSafely (1,000+ posts): curiosity-gap and contrarian hooks reach 6.8% and 6.2%, "2.3x" other types. Averages, not medians, and a small sample. [DATA n≈1k, weak]
- Small-business benchmark (648 posts): question hooks 3.0%, problem-first 4.9%. https://boomp.net/research/social-media-hook-benchmarks-small-businesses [DATA n=648, weak]
- **Skill rule:** open with a specific scene, result or claim, not a question. Story openers have the best large-sample support.

---

## 3. Posting frequency, gaps, best times

**Frequency**
- Buffer, "How Often Should You Post on LinkedIn in 2026?" (J. Winternheimer). **2M+ posts, 94k+ accounts**, account-level controls. Against 1 post a week:
  - 2 to 5 posts a week: **+1,182 impressions per post**, +0.23 percentage points engagement rate.
  - 6 to 10 a week: about **+5,001**, +0.76 points (via Blog du Modérateur and Siècle Digital, 2 Sep 2025).
  - 11+ a week: about +16k (weakly sourced).
  - "2 to 5 times weekly… is the sweet spot"; "no ceiling", with diminishing returns.
  - https://buffer.com/resources/how-often-to-post-on-linkedin/ [DATA n=2M]
- LinkedIn, Gyanda Sachdeva (VP Product), 2026 tips via SMT:
  - "Aim to publish between 2-5 LinkedIn posts per week". Members who post twice a week see "up to 5x more profile views".
  - "**Posting more than once a day won't hurt your total reach**", but space out posts on very similar topics.
  - https://www.socialmediatoday.com/news/linkedin-shares-tips-on-how-to-boost-your-in-app-performance-in-2026/808448/ [LI-via-press]
- LinkedIn video tips (SMT): 2 to 5 posts a week, 2 of them video, is "a strong starting point". https://www.socialmediatoday.com/news/linkedin-shares-video-creation-tips-based-on-platform-trends/821050/ [LI-via-press]
- LinkedIn AI-chatbot optimisation tips (SMT, 12 Mar 2026): 2 to 3 posts a week. https://www.socialmediatoday.com/news/linkedin-shares-tips-on-optimizing-post-content-for-ai-chatbots/814635/ [LI-via-press]
- Shield Index, Feb 2026, about 50k posts: reach rate falls as monthly volume rises. For accounts with 5k to 10k followers, 1 to 3 posts a month had a 16.3% reach rate against 5.5% at 16+. https://theshieldindex.beehiiv.com/p/february-2026-how-posting-frequency-affects-linkedin-reach [DATA n≈50k; Shield closed May 2026]
- Van der Blom, secondhand: 3 to 5 posts a week gives the highest per-post reach; daily gives more total reach but less per post (2024, 10k+ posts). [UNVERIFIED]

**Posting twice within 24 hours**
- Van der Blom (2023 report, via Malay Mail and others):
  - 1 to 3 posts a week, at least 18 hours apart.
  - A new post within 18 hours of the previous one gives "-15%" growth to both.
  - Two posts within 18 hours give "-30%" across all three.
  - https://www.malaymail.com/news/life/2023/05/11/what-and-when-should-you-post-on-linkedin/68608 [DATA, 2023, secondhand]
- This **conflicts** with LinkedIn's 2026 statement ("won't hurt your total reach"). LinkedIn's statement is about *total* reach and the 2023 figure about *per-post* growth, so both can be true.
- **Skill rule:** one post a day at most, 2 to 5 a week, about 18 to 24 hours apart. This is a conservative default, not a penalty rule.

**Gaps and inactivity**
- Ordinal: weekly posters (n=278) had **1.85%** median engagement against **1.89%** for accounts with 2+ week gaps (n=2,793). "Essentially noise"; Ordinal itself calls the result directional. https://www.tryordinal.com/blog/linkedin-content-strategy [DATA, small]
- Vulse (about 263,900 posts): accounts posting 3+ times a week grew impressions **+32% over 12 months**; less frequent accounts fell 6%. Correlational. https://vulse.co/blog/linkedin-consistency-data-700-million-impressions [DATA n≈264k]
- Buffer guidance: "better to post three times a week every week than to post daily for two weeks and then go quiet". [PRAC/Buffer]
- No evidence was found that a short break causes a lasting penalty.

**Best days and times (2025 to 2026)**
| Source | Sample | Finding | Tag |
|---|---|---|---|
| Buffer 2026. https://buffer.com/resources/best-time-to-post-on-linkedin/ (dates shown: 5 Mar and 22 Jul 2026) | 4.8M posts | Peak **3 pm to 8 pm**, a shift from working hours in 2025. Top slots: Wed 4 pm, Fri 3 pm, Fri 4 pm. Days: Wed > Thu > Fri; Mon and Tue weakest. | [DATA n=4.8M] |
| Sprout Social 2026 (updated Mar 2026). https://sproutsocial.com/insights/best-times-to-post-on-linkedin/ | 2B engagements, 307k profiles | Tue 11 am to 5 pm, Wed 11 am to 4 pm, Thu 11 am and 1 to 5 pm, Mon 1 to 2 pm, Fri 11 am and 1 to 2 pm. Weekends weakest. | [DATA n=307k profiles] |
| Hootsuite. https://blog.hootsuite.com/best-time-to-post-on-linkedin/ ("2025 data") | 1M+ posts (secondary) | Tue and Wed 8 to 9 am. Other Hootsuite pages say 4 to 6 am Tue and Wed. Internally inconsistent. | [DATA, inconsistent] |
- **Skill rule:** start with Tue to Thu, late morning or after 3 pm in the member's audience time zone. Run a 4-week test, comparing medians.

---

## 4. Newsletters, articles, Live and events, reposts, polls

**Newsletters**
- Help page (extract): "By default, your connections and followers will be invited by notification to subscribe to your newsletter once the first article of your newsletter has been successfully published." https://www.linkedin.com/help/linkedin/answer/97507 [LI]
- Later editions notify existing subscribers only. LinkedIn does not re-invite people who ignored the first notification. https://linkedinpreview.com/blog/linkedin-newsletter-growth-2026 [PRAC]
- **Launch the first edition only when the network is at its largest and warmest.**
- Subscribers get an **in-app notification and an email** per edition. LinkedIn's guide is dated 29 Nov 2023. Push notification is claimed only by third parties. https://members.linkedin.com/content/dam/me/members/en-us/pdf/li4c-newsletters-microsite-doc-231129.pdf [LI]
- One edition per 24 hours. Eligibility "evaluated over time"; about 150 followers is cited. Criteria help page: https://www.linkedin.com/help/lms/answer/a522525 [LI / PRAC for 150]
- Newsletter analytics added email sends and open-rate estimates in Feb 2025. [PRAC, PPC Land]
- LinkedIn's newsletter promotion guide (18 Nov 2025): seven tactics. https://ppc.land/linkedin-outlines-seven-promotion-tactics-for-newsletter-subscriber-growth/ [LI-via-press]
- LinkedIn article tips (SMT, about 30 Mar 2026): "newsletter interest is growing". Share original data, make it skimmable with a recap, feature expert voices. https://www.socialmediatoday.com/news/linkedin-shares-tips-on-using-articles-to-enhance-engagement/816162/ [LI-via-press]
- No reliable 2026 subscriber-growth or open-rate benchmarks were found. The "500M subscriptions" and "3.5x conversion" claims are unsourced. [UNVERIFIED]

**Articles**
- AuthoredUp, Mar 2025 to Feb 2026, personal profiles: median reach for **articles 596** against **text 921** and image 1,031. Engagement multiplier 0.44x, the lowest. The headline "5x" overstates the gap shown in its own table (about 1.5x). https://authoredup.com/blog/linkedin-articles-vs-posts [DATA, part of the 3M-post set]
- LinkedIn says articles drive citations in AI chatbots. SMT reports a suggested article length of **800 to 1,200 words**. https://www.socialmediatoday.com/news/linkedin-shares-tips-on-optimizing-post-content-for-ai-chatbots/814635/ [LI-via-press]
- **Verdict for a solo expert:** articles and newsletters are a search and AI-citation asset and an email-like channel to subscribers, not a feed-reach play. One newsletter edition a month or fortnight, repurposed from posts, is enough.

**LinkedIn Live and events**
- **From 22 Jun 2026, all Live streams must be scheduled as an Event.** Announced 29 Mar 2026; applies globally. A stream can still be scheduled "minutes in advance". Tools like Restream and StreamYard need a scheduled event. https://www.socialmediatoday.com/news/linkedin-will-no-longer-allow-real-time-livestreams/816050/ ; https://ppc.land/linkedin-kills-spontaneous-live-streaming-from-june-22/ [LI-via-press]
- Eligibility, per third parties: 150+ followers or connections, account 30+ days old, policy compliance, no Premium needed. Check via Events, then Create, then Event format, then "LinkedIn Live". Live overview: https://www.linkedin.com/help/linkedin/answer/100224 [PRAC; help page not quoted]
- "7x reactions, 24x comments vs video" is a vendor citation of an old LinkedIn figure. [UNVERIFIED]
- **Verdict:** a monthly scheduled event or Live (Q&A, teardown) is optional, high effort and good for warm-audience conversion. It is not needed in the first 90 days.

**Reposts**
- Plain repost against repost with your thoughts: no LinkedIn 2026 data was found.
- "Plain reposts outperform commentary reposts by 12x (1.8M posts)" is unattributed; 1.8M matches van der Blom 2025, but this is unconfirmed. https://linkedgrow.ai/blog/how-to-repost-on-linkedin [UNVERIFIED]
- Vendors say a repost with thoughts is scored as a new post against your own baseline. [PRAC]
- **Skill rule:** prefer a substantive comment on the original, or a repost with 2 to 4 lines of original insight. Avoid frequent plain reposts.

**Polls**
- AuthoredUp: polls have the highest median reach multiplier (**1.78x**) but the lowest engagement (**0.37x**). https://authoredup.com/blog/linkedin-polls [DATA, 3M set]
- Ordinal: poll engagement **0.41%** against 2.43% for multi-image posts. https://www.tryordinal.com/blog/linkedin-poll-best-practices [DATA]
- LinkedIn (2022): fewer polls from people you don't know; more "helpful and relevant" polls from your network. https://blog.linkedin.com/2022/may/5/keeping-your-feed-relevant-and-productive [LI, 2022]. No 2026 LinkedIn poll statement was found.
- **Verdict:** at most one poll a month, used as a research tool, for example to find a pain point for the next post. Not for lead generation.

---

## 5. Video on LinkedIn in 2026

- **Video tab / vertical player.** Help page (extract): "tap Video in the navigation bar at the bottom of the page" to open the full-screen vertical video player. The video tab and carousel "aren't currently available on the desktop site". You can't post directly into the vertical feed; you post a video normally. https://www.linkedin.com/help/linkedin/answer/a6290168 [LI]
  - The feed was tested from Mar 2024 and on the web from Feb 2025 ("test and feedback mode"; TechCrunch). https://techcrunch.com/2025/02/04/linkedin-amps-up-vertical-video-tools-as-uploads-jump-36 [LI-via-press]
- **Captions.** Help (extract): the caption tool can add auto captions or let you review them. Auto-captions are supported in 10 languages. https://www.linkedin.com/help/linkedin/answer/a7486279 [LI]
  - Videos autoplay muted, so burn in or upload SRT captions. [PRAC]
- **Length.** LinkedIn gives no organic length guidance in any extract.
  - LinkedIn ads guidance: 15 to 30 seconds for awareness. [LI-via-press, secondary]
  - LinkedIn's video tips (SMT): grab attention in the first 3 seconds. https://www.socialmediatoday.com/news/linkedin-shares-video-creation-tips/744933/ [LI-via-press]
  - Practitioners: 30 to 90 seconds, vertical 9:16 at 1080x1920. [PRAC]
- **LinkedIn's video push (company figures):**
  - Video uploads +36% YoY and creation +100% (Feb 2025).
  - Watch time +36% (Q3 FY25).
  - Uploads +20% "as of July" (2025).
  - Paid video ads about +30% YoY (Q3 FY26).
  - Sources: https://news.linkedin.com/2025/Q3FY25_Earnings_Highlights ; https://news.linkedin.com/2026/Q3-Earnings-Highlights [LI]
- **BrandLink.** Started as the Wire Program; renamed BrandLink in May 2025 to include creators. Invite-only; 70+ publishers and creators; no disclosed revenue share.
  - Mar 2026: "Top Voices 360" sponsorship, Shows by LinkedIn, pre-roll ads with new publishers (TIME, Reuters Japan, NYSE…), and CTV buying via The Trade Desk.
  - https://news.linkedin.com/2026/how-linkedin-is-helping-b2b-marketers-reach-audiences-at-scale-w [LI]
  - A reported new ad unit "BrandWorks" (Jun 2026) is single-source. [UNVERIFIED]
  - **Not relevant to a solo expert** except as a signal that LinkedIn wants video inventory.
- **Per-post reach data (2026):**
  - Shield Index, Mar 2026, about 50k posts: median reach rate video **7%**, text 12%, carousel 11%; images lead. https://theshieldindex.beehiiv.com/p/march-2026-linkedin-reach-by-content-format [DATA n≈50k]
  - Ordinal, 215,824 posts: average impressions text **7,995**, video **6,830**, carousel 4,792. Median engagement carousel 2.44%, video 2.26%. https://www.tryordinal.com/blog/carousel-posts [DATA n=216k]
  - "Vertical video +34%" and "50 to 80% penalty for YouTube links" have no primary source. [UNVERIFIED]
- **Verdict:** video is not the reach leader. For a 45 to 65 solo expert, the case is trust: face, voice, proof. Suggested format: one 45 to 90 second vertical, captioned, talking-head video a week, maybe repurposed from a text post that did well.

---

## 6. Practitioner systems

**Justin Welsh**
- **Content Matrix.** Welsh's own blog (https://www.justinwelsh.me/blog/content-matrix) describes a spreadsheet with **themes (left column) x styles (top row)**. Each cell is a headline idea; "once he has his themes and styles, he can rapidly create content using his templates". [PRAC, author's own page, extract]
  - Styles named in extracts: actionable, motivational, analytical, contrarian, observation, X vs Y, listicle. Third-party skills say "8 formats". The commonly cited 8 (Actionable, Motivational, Analytical, Contrarian, Observation, X vs Y, Present vs Future, Listicle) are **not confirmed**; "Present vs Future" was not seen in any extract. [TRAINING / UNVERIFIED for the full list]
  - A secondary account of a "730-day content library": pick 5 to 7 styles, generate 75 to 100 ideas, track them in Notion with a 1 to 10 rating. [PRAC, secondary]
- **Content Operating System.** Sales page: "a multi-step system for creating a high-quality newsletter and 6-12 pieces of high-performance social media content each week". $79 (was $200). https://learn.justinwelsh.me/content [PRAC, primary sales page]
  - Secondary breakdowns: curate top posts, make templates, generate ideas, distribute. Newsletter first, then sliced into "spokes" (story, observation, contrarian, listicle, analysis) across LinkedIn and X. Old content is recycled every 60 to 90 days with new hooks. [PRAC, secondary]
- **LinkedIn Operating System.** About a 2-hour course, $150, 11k+ students (Starter Story). Sections: introduction, foundation, content creation, business workflow (Medium review). The exact posting cadence and comment routine in the course are **not public**. https://starterstory.com/stories/justin-welsh [PRAC]
- **Cadence.** "He posts once a day, early morning East coast time, every day" (Josh Spector's observation). He often edits posts after publishing to add a link (Spector's inference). His profile header and About section point to one product. https://joshspector.com/justin-welsh-linkedin-system/ [PRAC, observer]
  - Growth loop (video description): "find a lane, write in a clear format, engage in the comments". [PRAC, secondary]

**Lara Acosta: SLAY**
- **S = Story, L = Lesson, A = Actionable (advice), Y = You** (end by turning it to the reader, usually with a question). About 150 to 250 words; story opener 2 to 4 lines.
- Sources: https://cool-story.beehiiv.com/p/lara-acosta-slay-framework ; https://buldrr.com/linkedin-slay-framework-explained-step-by-step/ [PRAC, secondary; her own post was not found]

**Jasmin Alić**
- "Focus on the first three lines of text, including spaces" (quote page). https://rosetta.to/person/jasmin-alic [PRAC, secondhand]
- A "1-to-9 framework" to plan "100+ posts" without AI; its steps were not found. https://socialmediaconference.boussiasevents.gr/?p=5515 [PRAC]
- A three-step hook method; only step 1 was found ("break the main topic into several steps or aspects"). https://koerting-institute.com/?p=23882 [PRAC, German]
- Profile analysis: the recurring thread is his Bosnian origin and a failure-to-success story; about 2 in 5 posts are punchy standalone advice. https://magicpost.in/blog/who-is-jasmin-alic [PRAC, competitor site]
- Podcast themes: consistency, commenting "for everyone who engages", using DMs. https://groucast.podbean.com/e/jasmin-jay-alic/ [PRAC]

---

## 7. DMs

**Lavender**
- No LinkedIn-message dataset was found from Lavender. Its widely cited finding is from **email**: 28.3M emails; **25 to 50 words get 65% more replies** than the usual 125-word cold email. SMT presents this under a LinkedIn InMail heading. https://www.socialmediatoday.com/news/linkedin-shares-inmail-best-practices-to-help-maximize-your-response-rates/632108/ [DATA n=28.3M, email]
- Other Lavender findings:
  - "A single informative tone… reduces reply rates by 26%". [DATA, email, secondary]
  - Coaching checks the I-to-you ratio, reading level, mobile-friendliness and question placement. These are features, not published thresholds. [PRAC]
  - Benchmark 231,818 cold emails: A-graded emails got 4.3% replies against 3.4%. https://woodpecker.co/blog/lavender-ai/ [DATA, email]
  - Gated report: https://www.lavender.ai/blog/the-cold-email-benchmark-report
- LinkedIn's own message data:
  - Individually sent InMails do about 15% better than bulk sends (2016).
  - Under 400 characters gets +22% (see conversations_to_clients.md).
  - https://searchenginejournal.com/linkedin-data-reveals-what-type-of-inmail-gets-best-results/451007 [LI]
- **Skill rule:** first DM 25 to 60 words, about you not me, one low-pressure question, readable on mobile.

**Josh Braun**
- **Poke the bear:** "a neutral, non-pitchy question that shines a light on a problem the prospect might not even know they have". Example: "How are you ensuring your cold emails don't land in spam?" [PRAC, secondary]
- **4T message structure:** **Trigger** (a specific observed reason), **Think** (a neutral poke-the-bear question), **Third-party** (a peer who solved it, instead of self-praise), **Talk** (one small, specific, interest-based ask). One variant adds "Tell". https://www.11x.ai/guides/josh-braun-cold-outreach-method ; https://leadiq.com/blog/writing-a-great-cold-email-with-the-4t-template [PRAC, secondary]
- Philosophy:
  - "detaching from the outcome"
  - give prospects "genuine permission to say no"
  - "radically honest" so prospects don't feel "sold"
  - don't overcome objections, "align with it"
  - Sources: https://leanmarketing.com/podcast/sales-strategies-for-fewer-rejections-an-interview-with-josh-braun ; https://creatordb.app/creatorstats/joshbraunsales/ [PRAC]
- Call script: permission, problem, poke the bear, peel the onion, promise. https://blog.close.com/cold-calling-tips-linkedin/ [PRAC]
- No verbatim Braun LinkedIn DM was found.

**Voice notes**
- No independent study exists. Vendor claims:
  - SalesRobot: voice 59% against text 27%, with no sample size. https://www.salesrobot.co/blogs/linkedin-voice-video-messages
  - Notion anecdote: 50 replies from 125 voice notes (40%).
  - Tagged [PRAC/UNVERIFIED].
- Mechanics: voice messages up to 60 seconds, mobile app only (help a548233, in conversations_to_clients.md). [LI]
- **Skill rule:** use voice notes only after a reply, as a warm follow-up from the member's own phone. Never automated (the automated voice-note tools in the results conflict with User Agreement 8.2).

**Messaging limits and InMail (official)**
- Help "Send messages" (extract): "you can message your 1st-degree connections or LinkedIn Pages for free". Non-connections can be messaged if they are Premium with Open Profile, if you share a Group, or via InMail. **No numeric daily or weekly message cap is published.** https://www.linkedin.com/help/linkedin/answer/a554575 [LI]
- InMail credits, from LinkedIn plan pages and help:
  - **Premium Career 5/month**: https://premium.linkedin.com/careers/career
  - **Premium Business 15/month**: https://premium.linkedin.com/small-business/business
  - **Premium All-in-One 30/month**: https://premium.linkedin.com/small-business/all-in-one
  - **Sales Navigator Core 50/month** (also Advanced and Advanced Plus) and **Recruiter Lite 30/month**: help a543695, https://www.linkedin.com/help/linkedin/answer/a543695
  - Tagged [LI].
- Credit rules (help a541643, extract): a new allotment arrives "on the first day of your billing cycle"; no unlimited plan exists. Sales Navigator Core renews on the last day of the month. A credit returns if the recipient accepts, declines or replies within 90 days. The balance goes to zero on cancel. https://www.linkedin.com/help/linkedin/answer/a541643 [LI]
- Rollover caps (Career 15, Business 45, Sales Navigator 150) and 90-day expiry are third-party claims only. [PRAC]
- Free accounts get no InMail. Invitations: about 100 a week is widely cited, but LinkedIn publishes no number (see conversations_to_clients.md). [PRAC]
- Prices: Business $59.99/mo or $47.99/mo annual; Career $29.99 to $39.99. Third-party only; sources conflict. [PRAC]

---

## 8. Content credentials, AI content help, "Seems like AI slop"

- **Content credentials.** Help page "Content credentials" (extract): "Members can view the Content Credentials on all image and video content that has C2PA information attached."
  - Tapping the icon shows whether AI was used, the app or device, the creator, the issuer and the date.
  - The AI assertion "comes from the entity that created and signed the content credential".
  - "It's not yet possible to identify and label all AI-generated and modified content."
  - https://www.linkedin.com/help/linkedin/answer/a6282984 [LI]
  - Feed images and video first, then ads (Blog du Modérateur, 2024). The icon is widely called "Cr"; the help-page image is labelled C2PA. [PRAC for "Cr"]
- **AI-generated content.** Help page "Best practices for content created with the help of AI" (extract):
  - AI can help with "articulating ideas, refining language, or being more concise".
  - "review, edit, and approve" any AI-assisted content.
  - Respect IP and privacy.
  - Disclose when you relied heavily on AI unless that is obvious.
  - Content should reflect your own perspective.
  - The page now defines **"AI slop"** as low-effort, likely AI-generated content that "looks polished but lacks a clear point of view or substance" and that feels "generic, repetitive, or built mainly to grab attention" (paraphrase in extract).
  - https://www.linkedin.com/help/linkedin/answer/a1481496 [LI]
- **"Seems like AI slop" option:**
  - **30 Jul 2026**, first reported by 404 Media: https://404media.co/linkedin-introduces-a-seems-like-ai-slop-button
  - It sits in the post three-dot menu and hides the post. Message shown: "Thanks for letting us know. Your feedback helps improve the feed."
  - LinkedIn statement (CPO **Hari Srinivasan**, via Fortune, 31 Jul 2026):
    - flags train "a series of new and improved classifiers"
    - content classified as slop gets **about 40% fewer views**
    - LinkedIn blocks "hundreds of thousands" of automated slop comment attempts daily and "billions of other automation attempts" in recent months
    - "Enhance your post" is replaced by a voice-preserving proofreader
    - https://fortune.com/2026/07/31/linkedin-seems-like-ai-slop-button-billions-automated-comments-attempts/ [LI-via-press]
  - About 25 Aug 2026: over 1 million clicks in a few weeks. https://fortune.com/2026/08/25/1-million-people-clicked-linkedin-ai-slop/ [LI-via-press]
  - A private analytics notice for flagged posts is being tested; posters get a "nudge" (WSJ via others). [LI-via-press]
  - Whether the option applies to comments is unresolved (sources conflict). [UNVERIFIED]
  - Pangram: 41% of long-form and 30% of short-form posts likely AI. Third party, and a former 404 Media advertiser. [DATA, vendor]

---

## 9. Social Selling Index status (Sep to Oct 2026)

- **LinkedIn's own page.** "From SSI to AI", https://business.linkedin.com/sell/resources/SSI (extract):
  - "The SSI score no longer accurately reflects the modern sales environment"
  - "a high SSI score doesn't always represent the efficacy of a sales person or correlate with measurable sales outcomes"
  - It points sellers to AI features in Sales Navigator.
  - The page does not itself say "discontinued". [LI]
- **User reports of lock-out:**
  - LinkedScore: banner seen **27 Aug 2026**. By **7 Sep** the page showed access discontinued for accounts without Sales Navigator. **15 Sep:** the same lock-out on a Premium All-in-One account. The SSI landing page redirected to "From SSI to AI" by end of May 2026. https://www.linkedscore.app/blog/linkedin-ssi-discontinued ; https://www.linkedscore.app/blog/why-linkedin-discontinued-ssi [PRAC, dated observations]
  - LadyBugz: non-premium accounts saw a deprecation notice the week of 30 Aug 2026 ("SSI is becoming a Sales Navigator feature"). https://www.ladybugz.co.za/linkedin-ssi-going-premium-2026/ [PRAC]
  - John Espirian (Threads, 2 Sep 2026): "LinkedIn has officially discontinued the Social Selling Index (SSI) score for free and Premium users. I believe that Sales Navigator users can still access it." https://www.threads.com/@johnespirian/post/DcyEQQajioQ/ [PRAC]
  - SmartCompany (28 Oct 2025): LinkedIn "quietly killed" the trending SSI score. https://www.smartcompany.com.au/artificial-intelligence/linkedin-killed-trending-ssi-score-replaced-it-with-ai/ [press]
- Dissent: Aimfox and ContentIn (22 Jul 2026) still say the score is free. These pages predate the late-August change. [PRAC]
- **No help-centre retirement notice or release note was found.**
- **Skill rule:** do not use SSI as a KPI. If the member has Sales Navigator, treat SSI as optional at most.

---

## 10. Analytics export and Connections.csv (for parsing)

**Creator analytics XLSX: menu path**
- Help "Combined post analytics" a701208 (extract):
  - Click the **Me** icon, then **View Profile**.
  - Scroll to **Analytics**, then **Show all analytics**.
  - Click **[Number] Post impressions**.
  - Set the date-range dropdown ("Past 7 days" by default; 7 to 365 days) and the metric dropdown (Impressions or Engagements). These apply to the whole Posts tab.
  - **Export** (upper right) gives an **.XLSX** file.
  - Sources: https://www.linkedin.com/help/linkedin/answer/a701208 ; https://www.linkedin.com/help/learning/answer/a704175 [LI]
- The audience view exports too. Its date range applies to the New-followers graph and Top demographics, **not** to Total followers. Demographic toggles: Job title, Location, Industry, Seniority, Company size, Company. [LI]
- Single-post analytics can be exported separately: "View analytics" on the post, then Export. https://lindseygamble.com/blog/linkedin-introduces-exportable-single-post-analytics [PRAC]
- Guides that say the export "requires Creator Mode" or is a "CSV" are outdated or wrong. Creator Mode was removed in 2024, and LinkedIn says XLSX.

**XLSX sheet names**
- **DISCOVERY, ENGAGEMENT, TOP POSTS, FOLLOWERS, DEMOGRAPHICS.** Read directly in the cloned repo `charlie947/social-media-skills`, file skills/analytics-dashboard/SKILL.md:
  - "DISCOVERY: overall impressions and reach"
  - "ENGAGEMENT: daily impressions and engagements over time"
  - "TOP POSTS: top 50 posts, ranked by engagements and by impressions (two tables to merge)"
  - "FOLLOWERS: daily new followers plus total count"
  - "DEMOGRAPHICS: job titles, locations, industries, seniority, company size, top companies"
  - It also says to "Clean any messy headers" and de-duplicate.
  - https://github.com/charlie947/social-media-skills [PRAC: one parser author's observation; **LinkedIn does not document sheet names**]
- **Column headers: NOT confirmed** by any source this session. My prior knowledge of the layout follows. It is **[TRAINING]**; the parser must detect it, not assume it:
  - DISCOVERY: a small key/value block ("Overall Performance", date range, "Impressions", "Members reached").
  - ENGAGEMENT: columns `Date`, `Impressions`, `Engagements`.
  - TOP POSTS: a note row (about "Maximum of 50 posts"), then two side-by-side tables. Left: `Post URL`, `Post publish date`, `Engagements`. Right: `Post URL`, `Post publish date`, `Impressions`. There is a blank column between them, and the header starts a couple of rows down.
  - FOLLOWERS: a first row like "Total followers on <date>:" with the value, then `Date`, `New followers`.
  - DEMOGRAPHICS: `Top Demographics`, `Value`, `Percentage`.
  - Parser advice: find header rows by searching for "Post URL" or "Date" rather than fixed offsets; match case-insensitively; dates may be M/D/YYYY.

**"Get a copy of your data" Connections.csv**
- Path: **Me > Settings & Privacy > Data privacy > Get a copy of your data.** Connections-only arrives fast; the full archive takes up to about 24 hours (help a566336, already in rules_tools_measurement.md). Only 1st-degree connections can be exported. [LI]
- **Columns:** `First Name`, `Last Name`, `URL`, `Email Address`, `Company`, `Position`, `Connected On`.
  - Read directly in the cloned repo `tdimino/claude-code-minoan`, file skills/integration-automation/linkedin-export/references/linkedin-export-format.md. Also matched by linkedapi.io and usecarly.com guides.
  - https://github.com/tdimino/claude-code-minoan ; https://linkedapi.io/guides/export-linkedin-connections.md [PRAC, consistent across 3+ sources]
- Parsing gotchas:
  - The file **starts with preamble lines** ("Notes:" and a note about missing emails) above the header. The same repo's li_parse.py scans for the first multi-column line. Guides also say to delete those lines.
  - The file may have a **UTF-8 BOM**.
  - `Email Address` is mostly blank; it reflects each connection's own privacy setting.
  - `Company` and `Position` are current values at export time.
  - `Connected On` looks like **`17 Jan 2026`** (DD Mon YYYY). One guide says MM/DD/YYYY, so auto-detect.
  - [PRAC]
- Other archive files the skill may use (same repo; [PRAC]):
  - `messages.csv`: CONVERSATION ID, CONVERSATION TITLE, FROM, SENDER PROFILE URL, TO, DATE, SUBJECT, CONTENT, FOLDER
  - `Invitations.csv`: From, To, Sent At, Message, Direction
  - `Shares.csv`: Date, ShareLink, ShareCommentary, SharedUrl, MediaUrl. Post history with no performance numbers.

---

## Still open
- Full text of the five LinkedIn newsroom and engineering posts. Exact publication dates for "authentic-content-and-conversations" and "keeping-conversations-real".
- Any LinkedIn on-record statement on the August 2026 comment-ranking change.
- Actual XLSX column headers, checked against a real 2026 export. **Ask a member to export one and record it before shipping the parser.**
- Welsh's exact 8 styles; Alić's hook steps; Braun's own LinkedIn DM wording; any Lavender LinkedIn-specific data.
- Van der Blom 2026 (1.3M posts, H1 2026) figures on frequency, reposts and polls (paid report).

## Sources (accessed 2026-10-16 via search extracts unless noted)
**LinkedIn primary**
- https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed (12 Mar 2026; via coverage)
- https://news.linkedin.com/2026/ImprovingTheFeed (Mar 2026)
- https://news.linkedin.com/2026/authentic-content-and-conversations (2026)
- https://news.linkedin.com/2026/keeping-conversations-real-on-linkedin (~May 2026)
- https://news.linkedin.com/2026/how-linkedin-is-helping-b2b-marketers-reach-audiences-at-scale-w (Mar 2026)
- https://news.linkedin.com/2025/Q3FY25_Earnings_Highlights ; https://news.linkedin.com/2026/Q3-Earnings-Highlights
- https://business.linkedin.com/sell/resources/SSI ("From SSI to AI")
- Help: a701208, a704175 (analytics); a6282984 (content credentials); a1481496 (AI best practices); a6290168 (video tab); a7486279 (captions); 97507, a522525 (newsletters); 100224 (Live); a554575 (send messages); a541643, a543695 (InMail); a545596 (free vs Premium)
- premium.linkedin.com: careers/career, small-business/business, small-business/all-in-one
- https://members.linkedin.com/content/dam/me/members/en-us/pdf/li4c-newsletters-microsite-doc-231129.pdf (29 Nov 2023)
- https://blog.linkedin.com/2022/may/5/keeping-your-feed-relevant-and-productive (2022)

**Press reporting LinkedIn statements**
- PPC Land feed rebuild: https://ppc.land/linkedin-rebuilds-its-feed-from-scratch-with-llms-and-gpu-powered-ranking/ ; SEL: https://searchengineland.com/linkedin-updates-feed-algorithm-llm-ranking-retrieval-471708 ; Herdl; ZenML
- SMT: 819792 (Berger), 808448 (Sachdeva 2026 tips), 821050 (video tips), 744933 (video tips), 814635 (AI chatbot tips, 12 Mar 2026), 816162 (articles, ~30 Mar 2026), 816050 (Live scheduling), 827394 (comment ranking, ~9 Aug 2026), 804970 (pods, Nov 2025), 632108 (InMail/Lavender)
- Fortune 31 Jul 2026 and 25 Aug 2026; 404 Media (30 Jul 2026); TNW (slop crackdown); Campaign; Bloomberg Government (30 Jul 2026); TechRadar; Cybernews; Slashdot 31 Jul 2026
- Comment-ranking secondary: relevantaudience.com, almcorp.com, vulse.co, lindseygamble.com, kompozy.io
- TechCrunch 4 Feb 2025 (vertical video); SmartCompany 28 Oct 2025 (SSI)

**Data studies**
- AuthoredUp: linkedin-character-limit, linkedin-text-formatting, linkedin-polls, linkedin-articles-vs-posts (authoredup.com/blog/…)
- Ordinal: tryordinal.com/blog/linkedin-post-size, /linkedin-hooks, /linkedin-content-strategy, /carousel-posts, /linkedin-poll-best-practices
- LigoSocial: ligosocial.com/research/linkedin-post-length
- Buffer: buffer.com/resources/how-often-to-post-on-linkedin/ ; buffer.com/resources/best-time-to-post-on-linkedin/
- Sprout Social: sproutsocial.com/insights/best-times-to-post-on-linkedin/ ; Hootsuite: blog.hootsuite.com/best-time-to-post-on-linkedin/
- Shield Index: theshieldindex.beehiiv.com (Feb and Mar 2026) ; Vulse: vulse.co/blog/linkedin-consistency-data-700-million-impressions
- Stan Store: stan.store/blog/linkedin-engagement/ ; boomp.net hook benchmarks ; Lavender via SMT and woodpecker.co ; Van der Blom 2023 via malaymail.com

**Practitioner**
- justinwelsh.me/blog/content-matrix ; learn.justinwelsh.me/content ; joshspector.com/justin-welsh-linkedin-system/ ; starterstory.com/stories/justin-welsh ; Medium LinkedIn OS review
- cool-story.beehiiv.com/p/lara-acosta-slay-framework ; buldrr.com (SLAY)
- rosetta.to/person/jasmin-alic ; koerting-institute.com/?p=23882 ; magicpost.in/blog/who-is-jasmin-alic ; groucast.podbean.com/e/jasmin-jay-alic/
- 11x.ai Josh Braun guide ; leadiq.com 4T template ; blog.close.com cold-calling tips ; leanmarketing.com Braun interview
- salesrobot.co voice notes ; linkedscore.app SSI posts ; ladybugz.co.za ; threads.com/@johnespirian
- GitHub, read directly: github.com/charlie947/social-media-skills (skills/analytics-dashboard/SKILL.md) ; github.com/tdimino/claude-code-minoan (skills/integration-automation/linkedin-export/references/linkedin-export-format.md, scripts/li_parse.py)
- linkedapi.io/guides/export-linkedin-connections.md ; usecarly.com export guide ; contentin.io ; unilink.us ; linkedinpreview.com
