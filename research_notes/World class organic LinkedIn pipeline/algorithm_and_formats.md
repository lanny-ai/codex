# LinkedIn feed distribution and format performance (2025–2026)

Research stream: how LinkedIn's feed distributes posts in 2025–2026, and which formats and habits earn reach and conversations.
Compiled 2026-10-16 for the Build Room OS organic LinkedIn pipeline skill.

> **How this was researched, and its limits (read first).**
> - Direct page fetching did not work in this session. Every fetch (linkedin.com, arxiv.org, searchengineland.com, ppc.land) failed: DNS lookups failed and the egress proxy refused the connections. **All evidence below comes from web-search result summaries and snippets, not from reading full pages.** A LinkedIn primary page that is "seen via search" has a known URL and quoted wording, but nobody has read the whole page.
> - The shared web-search budget ran out before I covered hooks and "see more" truncation, post length and white space, newsletters, articles, LinkedIn Live, reposts, tagging, and posting gaps. See "Gaps / not verified" at the end.
> - Labels used: **verified**: a LinkedIn or Microsoft primary source; I say whether I opened the page or only saw it via search. **data study**: a third-party dataset, with its sample. **practitioner claim / folklore**: who claims it.

---

## What matters most (10 lines)

1. **The feed is now interest-led, not network-led.** LinkedIn rebuilt feed retrieval and ranking around LLM embeddings plus a transformer "Generative Recommender" (announced 12 Mar 2026). Posts are matched to people by *topic*, so a consistent expert topic matters more than connection count. (Verified, seen via search.)
2. **Organic reach has fallen a lot for most creators.** Van der Blom 2026 reports about −60% reach for active creators over two years. AuthoredUp puts median personal-profile impressions at about 860 per post. Plan for small, relevant audiences, not virality. (Data studies.)
3. **Conversations are the currency.** LinkedIn reports comments +24% to +30% year on year. Since Aug 2026 it ranks comments per viewer and puts more live discussions into the feed. Substantive comments and author replies are the strongest lever a solo expert controls. (Verified, plus data.)
4. **Fake engagement is now actively suppressed.** Pods, automated or AI comment tools and "comment to agree" bait are detected. Their comments are removed from "Most Relevant" and their reach is limited, and accounts can be restricted. (Verified: LinkedIn newsroom 2026 and the VP of Product.)
5. **Documents (PDF carousels) and images are the best-performing formats on personal profiles.** AuthoredUp (3M+ posts): document 1.39x reach and 1.30x engagement, image 1.20x and 1.33x. Documents are under-used, at about 4.9% of posts. (Data study.)
6. **Video is being pushed by LinkedIn but underperforms for most profiles.** LinkedIn reports video uploads up 20%+ and watch time up 36%. Yet AuthoredUp finds video at 0.86x reach, with median video reach down 36% year on year. Socialinsider finds views per company-page video down 36%. (Contradiction, flagged.)
7. **Polls buy reach, not engagement.** 1.78x reach but 0.37x engagement (AuthoredUp). LinkedIn has said since 2022 that it shows fewer polls from strangers.
8. **External links carry a measurable but disputed cost.** LinkedIn says there is "no penalty if the post leads with value". Van der Blom measures −18.8% median reach for one link in the body. Metricool's 2025 study found link posts got *more* interactions. Treat links as a test variable, and favour value-first posts.
9. **Hashtags no longer add reach, and following hashtags is reportedly gone.** Topic consistency (2–3 core topics) is what drives interest-graph matching. (Practitioner and data claims.)
10. **Personal profiles beat company pages.** Metricool: personal profiles get a 63% higher engagement rate. Company-page posts reportedly reach about 1.6% of followers. Creator Mode was retired in 2024 and its tools went to everyone. Making Follow the primary profile button is a setting.

---

## 1. How the ranking system works now (2025–2026)

### 1.1 Architecture: LLM retrieval + Generative Recommender ranking
- **"Engineering the next generation of LinkedIn's Feed"**, LinkedIn Engineering Blog, by Hristo Danchev, **12 Mar 2026**. Secondary coverage describes it as replacing several separate retrieval pipelines with **one unified LLM-based dual-encoder retrieval model** (nearest-neighbour search over GPU embeddings, reported sub-50ms) and a **transformer-based Generative Recommender (GR)** for ranking. GR treats a member's feed history as an ordered sequence of **1,000+ past interactions**, uses causal attention, and runs on GPUs (earlier ranking ran on CPUs).
  - Status: **verified (LinkedIn primary exists; content seen only via secondary summaries)**. URL cited by secondary sources: https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed. Secondary sources: https://ppc.land/linkedin-rebuilds-its-feed-from-scratch-with-llms-and-gpu-powered-ranking/ ; https://searchengineland.com/linkedin-updates-feed-algorithm-llm-ranking-retrieval-471708 ; https://www.netinfluencer.com/linkedin-deploys-llm-based-feed-ranking-system-to-surface-content-beyond-members-networks/
  - Reported retrieval detail: turning engagement counts into percentile-bucket tokens gave a "30x" better correlation between popularity and embedding similarity, and **Recall@10 +15%**. Status: **unverified figures**, from secondary coverage of the Engineering blog and of the arXiv paper below.
- **LinkedIn newsroom: "How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content"**, https://news.linkedin.com/2026/ImprovingTheFeed, dated **12 Mar 2026** by secondary sources. It says the feed is moving to **"Generative Recommenders augmented with large language models"** to understand what a post is about and how a member's interests change over time. It also says LinkedIn will **reduce repetitive, low-substance posts and engagement bait, such as "comment to agree" prompts, and videos that don't match the post text**, and will train the feed to suppress pods and comment automation. Status: **verified (seen via search snippets, page not opened)**. Coverage: https://www.socialmediatoday.com/news/linkedin-updates-its-feed-algorithm/814638/ ; https://www.globaldatinginsights.com/featured/linkedin-deploys-ai-generative-to-boost-feed-relevance/
- **Research papers behind it** (LinkedIn authors on arXiv; these are research papers, not proof of what runs in production):
  - "Large Scale Retrieval for the LinkedIn Feed using Causal Language Models", arXiv 2510.14223 (Oct 2025). https://arxiv.org/pdf/2510.14223
  - "From Features to Transformers: Redefining Ranking for Scalable Impact" (LiGR), arXiv 2502.03417 (Feb 2025). It reports beating the prior production system using **only 7 features versus hundreds**. https://arxiv.org/pdf/2502.03417
  - "360Brew: A Decoder-only Foundation Model for Personalized Ranking and Recommendation", arXiv 2501.16450 (Jan 2025; v4 23 Aug 2025). A **150B-parameter** decoder-only model trained on LinkedIn first-party data (excluding EU users). It covers 30+ predictive tasks and replaces feature engineering with prompts that "verbalize member behaviors". https://arxiv.org/abs/2501.16450
- **CONTRADICTION / myth risk: "360Brew is the feed algorithm."** Many marketing blogs say so. A French analysis (https://lareclame.fr/linkedin-360brew-325321) says LinkedIn **never officially confirmed 360Brew is deployed in the feed**. Another analysis notes the **March 2026 engineering post does not use the name 360Brew**, and reports that a later arXiv version of the paper was withdrawn over a licensing and consent issue (https://media-all.in/en/blog/linkedin-360brew-ai-algorithm-explained/ ; search snippet only). The rollout timelines also conflict: "summer 2024 → 40–100% by fall 2025" versus "March 2026". **Practical reading:** the confirmed facts are the LLM retrieval, the GR ranking and the topic understanding. Do not cite "360Brew" in the skill as LinkedIn's confirmed feed model.
- **Signals LinkedIn names.** LinkedIn's Help Center says the feed uses your **profile (identity), the content you view, and how you interact**. It includes posts from outside your network ("suggested posts"). A blog quotes the Help article "How the Feed ranks content" as saying the feed considers **"hundreds of signals"**. Status: **verified (Help pages seen via search)**. https://linkedin.com/help/linkedin/answer/a1339724 ; https://www.linkedin.com/help/linkedin/answer/a1499047 ; quote via https://blog.recurpost.com/?p=34

### 1.2 Interest graph versus connection graph
- Van der Blom 2026 (as relayed by secondary sources) reports **connection-based distribution falling from 70% (2024) to 54% (2025) to 10% (2026)**, with the interest graph rising from 5% to 21% to 50%. Status: **data study (van der Blom 2026, 1.3M posts / ~50k creators; secondhand, method not visible)**. Source: https://melaniegoodmanlinkedinconsultant.substack.com/p/linkedin-algorithm-2026-reach-topic-authority (relays it); podcast: https://podcast.creatorscience.com/richard-van-der-blom-2/
- **Topic authority / "topic fingerprinting".** Van der Blom's 2026 framing is that LinkedIn went "from rewarding who you know to rewarding what you want to be known for". A specific claim: **sticking to 2–3 core topics for 90 days correlates with +27% reach and +41% topic-based follows**. Status: **practitioner and data claim (van der Blom, via secondary summary; not independently verified)**. Same sources as above. This is directionally consistent with LinkedIn's own statement that LLMs match posts to "professional interests" (verified, above).

### 1.3 Dwell time
- LinkedIn Engineering, **"Understanding dwell time to improve LinkedIn feed ranking"**, **12 May 2020**. It defines dwell time "on the feed", counted once at least half of an update is visible, and dwell time "after the click". Dwell was added to fight "click bounces". Status: **verified (old; seen via search)**. https://engineering.linkedin.com/blog/2020/understanding-feed-dwell-time
- The 2026 Generative Recommender reportedly uses past interactions **including dwell time** as part of the input sequence. Status: **secondary report** (Search Engine Land, Mar 2026). https://searchengineland.com/linkedin-updates-feed-algorithm-llm-ranking-retrieval-471708
- A 2024 Engineering post, "Leveraging Dwell Time to Improve Member Experiences on the LinkedIn Feed" ("Long Dwell" classifier), is cited by third parties. **I could not confirm it exists on a LinkedIn page.** Status: **unverified.**
- Specific dwell multipliers or thresholds circulating in blogs (for example "posts with X seconds dwell get Y% reach") have **no traceable LinkedIn source**. Status: **folklore.**

### 1.4 Comments versus reactions; comment depth; author replies
- **LinkedIn reports comment growth.** Microsoft FY25 Q4 (Jul 2025): "comments on LinkedIn rose over 30% and video uploads increased over 20% this year". FY26 Q1 (Oct 2025): LinkedIn CEO Ryan Roslansky cited **comments +24%**. Status: **verified (earnings statements, via secondary quotes)**. https://www.socialmediatoday.com/news/linkedin-reports-increase-in-post-comments-video-posts-microsoft-q1-2026/804353/
- LinkedIn VP of Product Gyanda Sachdeva (early 2026): **content sharing +15%, feed comments +24% year on year**. She advised posting from **your own first-hand expertise and experience**. Status: **verified (LinkedIn exec, via SMT)**. https://www.socialmediatoday.com/news/linkedin-shares-tips-on-how-to-boost-your-in-app-performance-in-2026/808448/
- **Aug 2026: comments ranked per viewer.** Comments are now ordered by relevance to *each viewer*, using professional interests, connections and engagement history. LinkedIn will also surface **more timely discussions in the feed** to pull members into replying. LinkedIn cited **time spent in comments +18% year on year (Q2)**. Status: **verified announcement, reported secondhand.** https://socialmediatoday.com/news/linkedin-updates-feed-display-to-drive-more-post-replies-and-comments/827394 ; https://almcorp.com/news/linkedin-comment-ranking-algorithm-update-august-2026/ ; https://www.lindseygamble.com/blog/linkedin-is-now-ranking-comments-based-on-relevance-and-personalization
  - Caveat raised by SMT coverage: part of the comment growth may be **automated / AI comments**.
- **Comment length.** The "comments of 15+ words count about 2x" claim is attributed variously to van der Blom, Just Connecting and Botdog. Status: **practitioner claim, unverified**, because no primary figure was found. A separate **LinkHub study of 657,722 comments (2026)** reports that the commenter's impressions jump at a length threshold (from 205 to 261 impressions). Status: **data study (vendor, 657,722 comments; threshold detail not seen)**. https://linkhub.gg/en/blog/longueur-commentaire-linkedin-impressions
- **Value of a comment for future distribution.** Van der Blom (2025) reportedly found that one comment raises the chance of seeing that creator's next post by **80%**, versus 40% for a reshare and 25% for a like. Status: **practitioner and data claim, secondhand** (via https://captureflow.ai/playbooks/richard-van-der-blom and the 2025 report recaps).
- **Author replies.** A 2025-report recap says posts where the author **responds within the first 30–60 minutes** get significantly more comments and reach. **No verified percentage lift** exists outside the paid report. Status: **practitioner claim (van der Blom, secondhand)**. https://melaniegoodmanlinkedinconsultant.substack.com/p/linkedin-algorithm-2026-reach-topic-authority
- Claims that saves or comments are weighted "Nx" over likes appear widely. **None trace to LinkedIn.** Status: **folklore.**

### 1.5 Engagement pods, automation and AI comments (policy)
- **LinkedIn newsroom 2026, "What We're Doing to Support Authentic Content and Conversations on LinkedIn"**: https://news.linkedin.com/2026/authentic-content-and-conversations. It defines automated comments as comments posted via a **browser extension, script, or third-party tool without human involvement**. If detected, comments may be **kept out of "Most Relevant"**, sometimes **limited to the commenter's own network**, and the member's account **may be restricted**. LinkedIn limits the reach of pods and inauthentic activity using technology plus human review. More than 100M members have at least one verification. Status: **verified (seen via search snippets; exact date not confirmed, likely Feb–Mar 2026)**.
- Gyanda Sachdeva (VP Product) said the goal is to make pods "entirely ineffective". LinkedIn is adding detection methods, flagging artificially boosted content and reducing its reach, and cracking down on comment-automation extensions. Status: **verified exec statement via SMT (article date not confirmed; French coverage 10 Nov 2025)**. https://www.socialmediatoday.com/news/linkedin-vows-to-take-action-against-engagement-pods-fake-engagement/804970/ ; https://siecledigital.fr/2025/11/10/faux-likes-faux-commentaires-linkedin-declare-la-guerre-aux-pods-dengagement-qui-manipulent-lalgorithme/ ; follow-up: https://www.socialmediatoday.com/news/linkedin-outlines-more-measures-to-combat-engagement-pods/812290/
- Reported: Lempod was removed from the Chrome Web Store. Status: **secondary claim** (autoposting.ai).
- Stats such as "pods = 97% reach drop" are **folklore with no primary source**, as noted by https://bossfeed.io/blog/linkedin-engagement-pods.
- Earlier baseline: LinkedIn (2022) said it does not promote engagement bait (posts asking for likes or reactions) and would show **fewer polls from people you don't know**. Status: **verified (old)**. https://blog.linkedin.com/2022/may/5/keeping-your-feed-relevant-and-productive ; https://www.socialmediatoday.com/news/linkedin-updates-feed-algorithm-to-downrank-engagement-baiting-posts-and-po/623313/
- Reported: AI-generated "slop" can be reported by members, and LinkedIn is refining its detection. Status: **secondary** (https://connectcx.ai/linkedin-expands-ai-content-controls-to-keep-professional-conversations-authentic/). The claim that "fully AI-generated posts get 2.8x less reach" is a **practitioner claim (2025 report recaps), unverified**.
- **Implication for the skill:** never automate comments or engagement. Human, substantive comments on target buyers' posts are both safe and favoured.

### 1.6 External links (post body versus comment)
- **LinkedIn:** a LinkedIn Sr. Director of Product Management said in Sep 2025 that there is **no algorithmic penalty for posts with links if the post leads with value**. Status: **LinkedIn statement, seen secondhand** via Matt Navarra on Threads, which links the original LinkedIn post urn:li:activity:7370869955623542785. https://www.threads.com/@mattnavarra/post/DOWa_61Cown/
- **Van der Blom 2026:** one external link in the body cuts **median reach by 18.8%**. Status: **data study (1.3M posts, secondhand)**.
- **Metricool 2025 (about 577k posts):** link posts got **+13.57% interactions and +4.90% views**. Status: **data study**. https://www.searchenginejournal.com/linkedin-study-finds-adding-links-boosts-engagement-by-13/544524/
- **Magicpost (data through Jun 2026):** link-preview *cards* roughly halve impressions, while a typed URL in the body was neutral until mid-May 2026. After that, a typed URL ran 21% below the same author's no-link posts and a link card 19% below. Status: **data study (vendor, sample not seen)**. https://magicpost.in/blog/linkedin-external-links-reach
- **Forbes (Jodie Cook, 30 Jul 2026):** "link penalty cutting your reach by 60%". Status: **practitioner claim**, and the methodology is contested. https://www.forbes.com/sites/jodiecook/2026/07/30/the-linkedin-link-penalty-cutting-your-reach-by-60/
- **Link in first comment:** claims that LinkedIn now suppresses link comments ("up to 80%"), and that commenting first on your own post limits reach, are **practitioner claims, unverified**. https://skalegrow.substack.com/p/does-linkedin-suppress-posts-with
- **CONTRADICTION flagged:** LinkedIn says no penalty. Van der Blom finds −19%, Forbes −60% and Metricool 2025 +13.6% interactions. Measurement differences explain part of this (reach versus interactions, link card versus typed URL, period). **Skill guidance:** keep most posts link-free and value-complete. When a link is needed, test it in the body versus the comment on your own account.

### 1.7 Editing after posting
- No LinkedIn statement found. The 2023 folklore says editing in the first 10 minutes costs 10–40% of impressions (https://www.hackernoon.com/linkedin-algorithm-2023-tips-and-tricks-you-must-know-to-go-viral), which is **folklore, no dataset**. 2026 vendor posts say minor edits carry no penalty, apart from a brief re-scan, and that editing keeps engagement while delete-and-repost resets it. Status: **practitioner claim**. https://linkedinpreview.com/blog/does-editing-a-linkedin-post-reduce-reach
- **Skill guidance:** fixing typos is fine. Avoid heavy rewrites, and never delete and repost to "reset".

### 1.8 Hashtags and tagging
- LinkedIn, in reply to Social Media Today: hashtags "can assist in discovery" but its algorithms "now consider a broader range of contextual cues". Status: **verified LinkedIn reply via SMT (date not visible)**. https://www.socialmediatoday.com/news/do-you-need-to-use-hashtags-on-linkedin/704535/
- Van der Blom: hashtags **give no additional reach boost**, where 3–10 hashtags used to help. Status: **practitioner and data claim, via SMT**. The ability to **follow hashtags was removed (late 2024 / early 2025)**, and the "Talks about" hashtags were dropped from profiles. Status: **secondary claims**. https://digitalworks.dk/en/artikler/hashtags-are-not-dead-on-linkedin-but-their-role-has-changed ; https://contentstudio.io/blog/linkedin-hashtags
- **Tagging people:** not researched (search budget). The common belief is to tag only people who will engage, because tagged non-responders are thought to hurt. **Folklore, unverified here.**

### 1.9 "Golden hour", posting time, frequency
- **"Golden hour" (first 60–90 min decides reach)** is a **creator-coined concept with no LinkedIn source**. Van der Blom's 2025 recaps say "most reach is decided in the first 60–90 minutes". A 2026 article argues the GR ranking scores relevance **continuously** rather than in a first-hour test. Status: **practitioner claim and folklore, contested.** https://contentin.io/blog/best-time-to-post-on-linkedin/
- **Metricool 2026:** **half of a post's impressions arrive in the first 48 hours**. That suggests a longer tail than "golden hour" implies. Status: **data study (673,658 posts / ~65k accounts, Jan–Feb 2025 vs 2026)**. https://newsletter.metricool.com/p/5-linkedin-stats-in-2026-you-probably-didn-t-see-coming
- **Best time to post:** all major studies agree on **Tue–Thu**, but the hours conflict. **Buffer (4.8M posts)** finds 3pm–8pm best, with Wed 4pm strongest. **Sprout Social** finds Tue 11am–5pm. **Hootsuite** finds Tue/Wed 8–9am. Status: **data studies (seen via aggregators)**. https://buffer.com/resources/best-time-to-post-on-linkedin/ ; https://frameos.studio/blog/best-time-to-post-on-linkedin. **Skill guidance:** pick weekday business hours in the *buyer's* time zone, then use your own analytics.
- **Frequency:** van der Blom 2025 recaps say **daily posting shows about −45% reach per post**, and **three PDF carousels in a row begin to reduce reach**. Status: **practitioner claim (secondhand)**. https://saleshigher.com/linkedin-algorithm/ ; https://captureflow.ai/playbooks/richard-van-der-blom. Metricool 2026: personal profiles average **3.05 posts/week** (company pages 2.34). Status: **data study**.
- **Gaps between posts / inactivity penalty:** **not researched (search budget)**.

---

## 2. Format performance (numbers and dates)

Engagement-rate formulas differ between studies (per impression, per follower, median versus mean). **Do not compare percentages across studies**, only the rankings within one study.

| Format | AuthoredUp (personal profiles, 3M+ posts, Mar 2025–Feb 2026), multiplier versus profile's own average | Socialinsider (company pages, 1.3M posts / 16,645 pages, 2025) engagement rate | Notes |
|---|---|---|---|
| Document / PDF carousel | **1.39x reach, 1.30x engagement**; median reach 1,198; only **4.9%** of posts; top 5% profiles 1.72x/1.63x | **7.00%** (top; +14% YoY). Q2 2026 update: 6.60% | Metricool 2026: carousels lead engagement, about 17x the interactions of images (Spanish page) |
| Image (single) | **1.20x reach, 1.33x engagement**; 57% of posts; 65% of saves | 5.30% | Best volume format |
| Multi-image | n/a | **6.45%** (2025); **6.90%** Q2 2026, which overtook documents | Company-page data |
| Text-only | 1.07x reach, **0.78x engagement** | 4.50% (lowest) | |
| Native video | **0.86x reach**, the only major format below average; median video reach **−36% YoY** | 6.00% (+7% YoY), but **views per video −36%** while pages doubled video output | See video section |
| Poll | **1.78x reach, 0.37x engagement** ("reach trap") | n/a | LinkedIn shows fewer polls from strangers (2022) |

Sources: AuthoredUp https://authoredup.com/blog/best-performing-content-on-linkedin ; https://authoredup.com/blog/linkedin-trends ; https://contentin.io/blog/linkedin-content-statistics/ . Socialinsider https://www.socialinsider.io/social-media-benchmarks/linkedin ; https://www.goextrovert.com/blog/linkedin-engagement-rate-benchmarks . Metricool https://metricool.com/press-release-linkedin-study-2026/ ; https://metricool.com/linkedin-trends/ . (All are **data studies**, seen via search snippets.)

**CONTRADICTION / attribution confusion:** the same multipliers (carousel 1.39x/1.30x, poll 1.78x/0.37x, video 0.86x) are attributed to **van der Blom's 2025 report** by some recap sites (https://expandi.io/blog/linkedin-algorithm/) and to **AuthoredUp** by others. The AuthoredUp attribution, with its Mar 2025–Feb 2026 window, is the more specific one. Cite AuthoredUp, and note the uncertainty. The AuthoredUp sample is also given as 967,450 posts on one page and 3M+ on others.

**Older or contradicting format data:**
- Buffer 2023 (1M+ posts) ranked **video 4.9% > photo 4.8% > document 4.2%**, so carousels came third. A later Buffer "State of Social Engagement" (52M+ posts, all platforms) puts carousels first on LinkedIn. Status: **data studies**. https://buffer.com/resources/linkedin-carousels/
- Metricool 2025 (577k posts) found carousels had the highest engagement rate (45.85%, by its own formula). Status: **data study**. https://www.searchenginejournal.com/linkedin-study-finds-adding-links-boosts-engagement-by-13/544524/
- **Net 2025–2026 picture:** documents and carousels have *risen* to the top in the 2025–2026 data. Some 2025 blogs predicted a "carousel decline", but the 2025–26 datasets do not show one. Only van der Blom's remark that "three in a row reduce reach" cautions against overuse.

### 2.1 Video: LinkedIn's push versus measured performance
- **LinkedIn / Microsoft (verified, via secondary quotes):** video watch time **+36% YoY** (late Oct 2024–Jan 2025), and video creation growing at twice the rate of other formats (Digiday, 2025: https://digiday.com/media/linkedins-video-push-appears-to-be-working-in-2025/). Video uploads **+20%+** (FY25 Q4, Jul 2025), then "three straight quarters of double-digit upload growth" (Oct 2025). A dedicated **vertical video feed** has been tested on mobile since **Mar 2024**.
- **LinkedIn 2026:** it is downranking "videos that don't match the post text" (verified, ImprovingTheFeed, Mar 2026).
- **Independent data:** AuthoredUp shows video at 0.86x reach and −36% YoY median reach on personal profiles. Socialinsider shows views per company-page video −36% (2024→2025). Metricool's 2026 headline says "video performance slips", while Metricool 2024→2025 shows video impressions +73% and views +52%. **CONTRADICTION between Metricool's two periods; probably supply growth outpacing demand.**
- **Vertical versus horizontal:** there is no rigorous organic study. One advertiser's data (LinkedIn Ads Show, May 2025, about $140k spend) found **16:9 beat 9:16 and 1:1 on view and completion rate by 2–4x** (https://b2linked.com/blog/ep160), which is **practitioner data, ads only**. The claim that vertical gets about 34% higher engagement is attributed to a "LinkedIn Creative Labs" report I **could not verify** (https://www.teleprompter.com/blog/linkedin-video-statistics).
- **Length and captions:** the usual 30–90s advice and the claim that captions lift completion have **no traceable dataset**. Status: **practitioner claims** (opus.pro, nealschaffer.com).
- **Skill guidance:** use video for trust and depth with existing followers (face, voice, explanation). Do not expect it to be a reach engine for a solo expert. Make sure the post text matches the video.

### 2.2 Newsletters, articles, LinkedIn Live, reposts
- **Not researched** (search budget exhausted). AuthoredUp has an "Articles vs Posts" page (https://authoredup.com/blog/linkedin-articles-vs-posts), which I did not read. Creator Mode's former tools (newsletters, Live) are available to all members since 2024 (see section 4).

---

## 3. Hooks and post structure
- **Not researched with sources in this session** (search budget exhausted). The commonly repeated "see more" truncation length, ideal post length and white-space data still need sourcing. AuthoredUp, Lempod-era studies and van der Blom are the likely sources.
- What *is* supported: LinkedIn penalises engagement-bait hooks ("comment to agree", "like if…") and text–video mismatch (verified, Mar 2026). It rewards first-hand expertise and substance (Sachdeva, 2026). The LLM ranking reads the *text* to infer topic, so the first lines should name the topic and the audience plainly. That last point is an **inference from the verified architecture, not a measured finding**.

---

## 4. Personal profiles versus company pages; Creator Mode and Follow
- **Metricool 2026 (673k posts):** personal profiles get a **63% higher engagement rate** than company pages, with similar impressions per post (817.67 versus 831.96). Company-page impressions per post fell **−10% YoY**, but clicks rose +5%. Status: **data study**. https://metricool.com/press-release-linkedin-study-2026/ ; https://www.netinfluencer.com/linkedin-engagement-shifts-toward-clicks-as-visible-metrics-decline-study-finds/
- **AuthoredUp 2026 benchmark:** median impressions per post are **860 for personal profiles** (top 5%: 8,400) versus **500 for company pages**. Status: **data study**. https://authoredup.com/blog/linkedin-metrics-to-track
- **RevBoss (Jan–Aug 2026):** median founder post **502 impressions**; founder accounts get 520 versus 244 per post on company pages. Status: **data study (vendor, sample not seen)**. https://www.revboss.com/founder-led-marketing-benchmarks
- **Ordinal:** a typical company-page post reaches about **1.6% of followers** (−15% versus late 2023). Status: **data study (vendor, sample not seen)**. https://www.tryordinal.com/blog/the-declining-reach-of-linkedin-company-pages
- **Refine Labs (date unknown):** personal profiles get about 3x the impressions and 5x the engagement of company pages. Status: **data study, relayed**.
- **Creator Mode:** LinkedIn **retired the Creator Mode toggle (Feb–Mar 2024)** and extended its tools (newsletters, Live, extra analytics) to all members. The "Talks about" hashtags were removed. LinkedIn statement via SMT: https://www.socialmediatoday.com/news/linkedins-removing-creator-mode-option/706585/ (**verified statement via secondary**). Ex-creator-mode accounts keep **Follow** as the primary button. Others can set Follow as primary in **Settings → Visibility**. Status: **secondary** (https://www.jvt.me/posts/2025/05/13/linkedin-enable-follows/). One source wrongly dates the retirement to "early 2025" (contentstudio), so **use 2024**.
- **Implication for solo experts:** post from the personal profile. A company page is optional, as a credibility asset only.

---

## 5. Overall reach trend
- **Van der Blom 2026** (7th edition, about 1.3M posts from H1 2026, about 50k creators): reach **−60% for active creators over two years**. Status: **data study (secondhand via podcast and summaries)**. https://podcast.creatorscience.com/richard-van-der-blom-2/ ; report page (not opened): https://sales.richardvanderblom.com/content-algorithm-playbook/
- **Van der Blom 2025** (about 1.8M posts; profile count cited as about 58k or about 400k in different recaps): reach **−47% (or about −50%)**, engagement −39% (or −25%), follower growth −42% (or −59%). **The recaps disagree on these numbers.** Status: **data study (secondhand)**. https://www.scribd.com/document/984921783 (chapter 1 copy, not opened) ; https://contentin.io/blog/linkedin-algorithm-2025-why-your-reach-dropped-how-to-win-in-2026/
- **Metricool 2026:** likes, comments and shares fell YoY, but total engagement rose about 14% through "invisible" interactions (clicks, carousel swipes, video views). Status: **data study**.
- **Tension with LinkedIn's numbers:** LinkedIn reports comments up 24–30% and comment time +18%, while creators report reach collapsing. These fit together if supply (more posters and video) grows faster than attention, and if distribution shifts from broad reach to narrow relevance. **That is my interpretation.**

---

## 6. Implications for the Build Room OS skill (derived, not sourced claims)
1. Pick **2–3 core topics** tied to the offer and stay on them for 90+ days, so the interest graph can classify the expert.
2. Default formats: **text+image** and **PDF documents** (1 to 2 a week, not three in a row). Use **video** for trust, not reach. Use **polls** rarely, and only for genuine market research.
3. Write for **comments, not likes**. Ask a real, specific question, with no "comment X to get Y" bait. Reply to every substantive comment quickly. Run a **daily commenting routine** of substantive 15+ word comments on target buyers' and peers' posts. This is an inference from the comment-ranking changes; the 15-word threshold itself is unverified.
4. **No pods, no automation, no AI auto-comments.** Detection and penalties are confirmed by LinkedIn.
5. Keep posts **link-free by default**. Measure your own results when a link is necessary.
6. Post **2–5 times a week**, Tue–Thu weighted, in buyer business hours. Don't post daily for its own sake.
7. Make **Follow** the primary profile button if the goal is audience, and keep **Connect** if the goal is 1:1 pipeline. That trade-off is a judgement call; there is no data on it.

---

## Gaps / not verified
- **Could not open any page**: page fetching failed and the proxy refused the connections. Everything above comes from search snippets. The LinkedIn Engineering post (12 Mar 2026), news.linkedin.com/2026/ImprovingTheFeed and news.linkedin.com/2026/authentic-content-and-conversations should be read in full to confirm the wording and dates.
- **Search budget exhausted** before I covered: hooks and the "see more" cut-off, post length, white space, newsletters, articles, LinkedIn Live, reposts, tagging, posting gaps and inactivity, Hootsuite's and Shield's own studies, and LinkedIn Creator guidance pages (linkedin.com/creators).
- **Unverified widely-repeated claims:** 360Brew running the feed; the 150B model being used in production; the 15-word comment threshold; reply-timing multipliers; dwell-time multipliers; "golden hour"; the vertical video +34%; the 97% pod reach drop; AI posts getting 2.8x less reach; the edit penalties.
- **Report access:** van der Blom's 2025 and 2026 reports are paid. All figures come from secondary recaps, which disagree on sample sizes and percentages.

---

## Source list
**LinkedIn / Microsoft primary (seen via search; pages not opened)**
- LinkedIn Engineering, "Engineering the next generation of LinkedIn's Feed", H. Danchev, 12 Mar 2026: https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed
- LinkedIn News, "How LinkedIn Is Improving the Feed…", ~12 Mar 2026: https://news.linkedin.com/2026/ImprovingTheFeed
- LinkedIn News, "What We're Doing to Support Authentic Content and Conversations on LinkedIn", 2026: https://news.linkedin.com/2026/authentic-content-and-conversations
- LinkedIn Engineering, "Understanding dwell time to improve LinkedIn feed ranking", 12 May 2020: https://engineering.linkedin.com/blog/2020/understanding-feed-dwell-time
- LinkedIn Blog, "Keeping your feed relevant and productive", 5 May 2022: https://blog.linkedin.com/2022/may/5/keeping-your-feed-relevant-and-productive
- LinkedIn Blog, "Mythbusting the Feed: How the Algorithm Works" (2022): https://www.linkedin.com/blog/member/product/mythbusting-the-feed-how-the-algorithm-works
- LinkedIn Help: https://linkedin.com/help/linkedin/answer/a1339724 ; https://www.linkedin.com/help/linkedin/answer/a1499047 ; https://www.linkedin.com/help/linkedin/answer/3068
- arXiv (LinkedIn authors): https://arxiv.org/abs/2501.16450 (360Brew, Jan–Aug 2025) ; https://arxiv.org/pdf/2502.03417 (LiGR, Feb 2025) ; https://arxiv.org/pdf/2510.14223 (LLM retrieval, Oct 2025)
- Microsoft FY26 earnings: https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q1

**Trade press reporting LinkedIn statements**
- SMT, comments/video growth (Oct 2025): https://www.socialmediatoday.com/news/linkedin-reports-increase-in-post-comments-video-posts-microsoft-q1-2026/804353/
- SMT, Sachdeva tips 2026: https://www.socialmediatoday.com/news/linkedin-shares-tips-on-how-to-boost-your-in-app-performance-in-2026/808448/
- SMT, pods: https://www.socialmediatoday.com/news/linkedin-vows-to-take-action-against-engagement-pods-fake-engagement/804970/ ; https://www.socialmediatoday.com/news/linkedin-outlines-more-measures-to-combat-engagement-pods/812290/
- SMT, feed algorithm update (Mar 2026): https://www.socialmediatoday.com/news/linkedin-updates-its-feed-algorithm/814638/
- SMT, comment display (Aug 2026): https://socialmediatoday.com/news/linkedin-updates-feed-display-to-drive-more-post-replies-and-comments/827394
- SMT, Creator Mode removal (2024): https://www.socialmediatoday.com/news/linkedins-removing-creator-mode-option/706585/
- SMT, hashtags: https://www.socialmediatoday.com/news/do-you-need-to-use-hashtags-on-linkedin/704535/
- Search Engine Land (Mar 2026): https://searchengineland.com/linkedin-updates-feed-algorithm-llm-ranking-retrieval-471708
- PPC Land (Mar 2026): https://ppc.land/linkedin-rebuilds-its-feed-from-scratch-with-llms-and-gpu-powered-ranking/
- Digiday (2025): https://digiday.com/media/linkedins-video-push-appears-to-be-working-in-2025/
- Siècle Digital (10 Nov 2025): https://siecledigital.fr/2025/11/10/faux-likes-faux-commentaires-linkedin-declare-la-guerre-aux-pods-dengagement-qui-manipulent-lalgorithme/
- Matt Navarra / Threads (Sep 2025), links statement: https://www.threads.com/@mattnavarra/post/DOWa_61Cown/
- Forbes, J. Cook (18 Mar 2026; 30 Jul 2026): https://www.forbes.com/sites/jodiecook/2026/03/18/linkedin-just-killed-engagement-pods-heres-what-to-do-instead/ ; https://www.forbes.com/sites/jodiecook/2026/07/30/the-linkedin-link-penalty-cutting-your-reach-by-60/

**Data studies**
- Van der Blom / Just Connecting, Algorithm Insights 2025 and 2026 (paid): https://richardvanderblom.com/ ; https://sales.richardvanderblom.com/content-algorithm-playbook/ ; podcast https://podcast.creatorscience.com/richard-van-der-blom-2/
- AuthoredUp (3M+ posts, Mar 2025–Feb 2026): https://authoredup.com/blog/best-performing-content-on-linkedin ; https://authoredup.com/blog/linkedin-trends ; https://authoredup.com/blog/linkedin-metrics-to-track
- Socialinsider (1.3M posts, 16,645 pages): https://www.socialinsider.io/social-media-benchmarks/linkedin
- Metricool 2026 (673,658 posts, ~65k accounts): https://metricool.com/press-release-linkedin-study-2026/ ; https://newsletter.metricool.com/p/5-linkedin-stats-in-2026-you-probably-didn-t-see-coming ; Metricool 2025 (577k posts) via https://www.searchenginejournal.com/linkedin-study-finds-adding-links-boosts-engagement-by-13/544524/
- Buffer (4.8M posts, best times; 2023 1M posts formats): https://buffer.com/resources/best-time-to-post-on-linkedin/ ; https://buffer.com/resources/linkedin-carousels/
- LinkHub (657,722 comments, 2026): https://linkhub.gg/en/blog/longueur-commentaire-linkedin-impressions
- Magicpost (links, through Jun 2026): https://magicpost.in/blog/linkedin-external-links-reach
- RevBoss (2026): https://www.revboss.com/founder-led-marketing-benchmarks
- Ordinal (company pages): https://www.tryordinal.com/blog/the-declining-reach-of-linkedin-company-pages

**Practitioner / secondary commentary used for claims or contradictions**
- https://lareclame.fr/linkedin-360brew-325321 ; https://media-all.in/en/blog/linkedin-360brew-ai-algorithm-explained/ ; https://melaniegoodmanlinkedinconsultant.substack.com/p/linkedin-algorithm-2026-reach-topic-authority ; https://captureflow.ai/playbooks/richard-van-der-blom ; https://saleshigher.com/linkedin-algorithm/ ; https://expandi.io/blog/linkedin-algorithm/ ; https://bossfeed.io/blog/linkedin-engagement-pods ; https://linkedinpreview.com/blog/does-editing-a-linkedin-post-reduce-reach ; https://www.hackernoon.com/linkedin-algorithm-2023-tips-and-tricks-you-must-know-to-go-viral ; https://b2linked.com/blog/ep160 ; https://www.teleprompter.com/blog/linkedin-video-statistics ; https://contentin.io/blog/best-time-to-post-on-linkedin/ ; https://digitalworks.dk/en/artikler/hashtags-are-not-dead-on-linkedin-but-their-role-has-changed ; https://www.jvt.me/posts/2025/05/13/linkedin-enable-follows/ ; https://skalegrow.substack.com/p/does-linkedin-suppress-posts-with
