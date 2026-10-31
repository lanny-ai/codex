# Answer engines and crawlers: how sources get chosen, crawled and measured

Research notes, compiled 2026-10-28. Scope: what is true now, with emphasis on Nov 2025 to Oct 2026. Audience for the eventual skill: owners (55 to 75, non-technical) of small service businesses.

**Method note.** Every finding rests on web-search extracts. Direct fetches of developers.google.com and developers.openai.com failed (hosts not resolvable here), so no official page was read in full; "platform/official" means the claim was attributed to the platform's own page or blog in an extract. Tags: **platform/official**, **vendor data**, **independent data**, **practitioner**, **folklore**.

---

## 1. Google AI Overviews (AIO) and AI Mode

**How sources are chosen**
- Google Search Central's "AI features and your website" page: AIO and AI Mode *may* use "query fan-out" (multiple related searches across subtopics and data sources, then combined); the two features may use different models so their links vary; AIO shows only when judged additive and "often don't trigger"; no special optimisation, new files (including llms.txt) or AI-specific markup are needed. Blogs date a substantive update to 15 May or 15 June 2026 (conflict). — developers.google.com/search/docs/appearance/ai-features. **platform/official** via extracts.
- Overlap with classic top 10 has collapsed. Ahrefs (Mar 2026; 863,000 keywords, ~4M AIO URLs): 38% of cited pages also rank top 10 for the query, down from 76% in mid-2025; 36% ranked outside the top 100. Ahrefs credits fan-out and warns its detection improved between studies. BrightEdge (Feb 2026, different panel): ~17%. — SEJ; Contently. **vendor data**. Verify: 38% vs 17%.
- Within-page position matters: Kevin Indig, 18,012 verified ChatGPT citations, 44.2% came from the first 30% of the document. Cross-engine overlap is tiny: in 3.7M citations across ChatGPT, Perplexity and AIO, 91% appeared in only one engine. — Growth Memo 2026. **practitioner / vendor data**.
- No extract gave a primary Google statement on passage-level selection; treat it as inferred from fan-out, not documented.

**Share of queries showing AIO** (numbers disagree badly; definitions differ)
- Semrush, 21 Oct 2026: 88% of a fixed panel of 400 US commercial keywords showed an AIO in Aug 2026, up from 45.75% in Sep 2025 (panel, not prevalence). **vendor data**. Comscore via Quartz: 39.4% of US desktop searches, Jun 2026, up from 25.8%. **independent data**. BrightEdge: ~48 to 50% of US queries, Q1 2026. Semrush's older all-query figure: 13.14% (Mar 2025). Bullock (300 small-business marketing searches): 93%. **practitioner, small sample**.
- Verify: the share ranges 13% to 88% by panel; always name the panel.

**Click-through effects**
- Pew Research, 22 Jul 2025 (900 US adults, 68,879 searches): users clicked a result 8% of the time with an AI summary vs 15% without; 1% of summary visits clicked a cited source; 26% vs 16% ended the session. Google called the query set skewed. **independent data**.
- Seer Interactive (Sep 2025): organic CTR 1.76% to 0.61% when AIO present, partly recovering to ~2.4% by Feb 2026. BrightEdge 12-month view: impressions +49%, clicks about minus 30%. Indig think-aloud: in ~75% of AI Mode sessions users never left the pane. **vendor data**.
- Google (Q1 and Q2 2026 earnings): AI features drive record Search usage; AI Mode queries ~3x longer; no AI Mode share disclosed. — blog.google. **platform/official**.

**Local-intent behaviour (important for this audience)**
- Steady Demand (Aug 2026; single snapshot; 7,990 US local-service searches; 86,645 citations in eight source types): AI Mode sent 79.8% of local-intent citations (of 40,883) to Google Maps / Business Profile URLs and 19.7% to business websites; AIO sent 73.5% (of 3,869) to the business's own site. Only ~13.7% URL overlap between AIO and AI Mode. Local-SEO agency; no other study classifies AI Mode local citations this way. Its "Grounding Drift" follow-up: identical repeated prompts overlapped only ~40%. **vendor data**.
- BrightLocal 2026 Local AI Visibility Study (200,085 localized searches; 1,355 businesses, US/UK/AU; 1.9M citations across ChatGPT, AI Mode, AIO): Google Business Profile is 28.5% of all citations and dominates Google's AI surfaces; Yelp dominates ChatGPT, where GBP is absent; business websites are 93% of *unique* domains cited but third-party sites are cited more *often*; ~50% crossover between Google Maps picks and AI chat; the same business reappears ~50% of the time on re-runs. **vendor data**.
- Search Engine Journal roundup: AI Mode self-citations (links to Google's own results) rose from 7% to 21% of AI Mode citations. **practitioner**.
- Practical read: for Google's AI surfaces a complete, accurate Google Business Profile is the primary citation target; the website is secondary but still the main source for AIO and for non-Google engines.

**Controls and Google-Extended**
- Google-Extended governs Gemini training and grounding only; Google says it does not affect Search inclusion or ranking, and blocking it does not remove a site from AIO or AI Mode (Googlebot surfaces). — ppc.land; Marie Haynes. **platform/official via extracts**.
- New in 2026: a Search Console toggle (announced ~2 Jun, global ~1 Sep 2026) opts a site out of appearing in and grounding AIO, AI Mode and Discover AI while staying in classic Search; the Gemini app is excluded. Snippet controls still work. — 9to5Google; SERoundtable. **platform/official via secondary**. Small businesses should stay opted in.

---

## 2. ChatGPT, Perplexity, Copilot, Claude, Gemini: what each cites

**Caveat first.** Every citation study below is vendor-run, with different prompt panels, time windows and denominators (share of all citations vs share of top-10 domains vs share of answers containing a domain). Numbers are directional. Domains leading one study are mid-table in another.

- **ChatGPT.** Wikipedia is consistently prominent: 47.9% of top-10 source share (Profound / Discovered Labs), 29.7% of its top 1,000 cited pages with brand homepages 23.8% (Ahrefs), 13.15% of US citations with Reddit 11.97% (5W Citation Source Audit Q1 2026). Semrush (325K prompts): LinkedIn in 14.3% of ChatGPT Search responses. Ahrefs (15,000 prompts): only 12% of URLs cited by ChatGPT, Gemini and Copilot rank in Google's top 10. Index: OpenAI runs its own index via OAI-SearchBot, blends third-party providers (Microsoft named on its help page); Seer's 2025 claim that 87% of citations matched Bing top-10 (100 queries) was contradicted by a 400-query replication reporting 27%, and another analysis found Bing top-3 matched citations only 6.8 to 7.8% of the time. **vendor data / practitioner**. Claim to verify: Bing share of ChatGPT citations (87% vs 27%).
- **ChatGPT, local.** Sources disagree on the feed: Yelp (licensing deal; Yelp data in 95.8% of local responses in one Aug 2026 test), Foursquare Places (one source), Bing index as fallback, Google Maps only indirectly. SOCi: ChatGPT recommended 1.2% of brand locations (Gemini 11%, Perplexity 7.4%); details accurate for 68.3%. Yext Oct 2025: OpenAI leaned on listings 48.7%, Gemini on websites 52.1%, Perplexity spread across MapQuest, TripAdvisor etc.; MapQuest the top non-Google directory. Yext Jul 2026 (155.5M citations, 1,623 brands): 80% of citations went to listings or websites; when a query names a service, AI cites the service page over the location page. **vendor data**.
- **Perplexity.** Reddit leads nearly every study (Surfer Sep 2026: 18.9% of top-50 citations; Evertune Mar 2026: 17.3% of all; Profound: 46.7% of top-10 share; Tinuiti: 24%), LinkedIn second, then review and directory sites; ~67% of citations fall outside the top-20 domains (Evertune). Recency bias: Seer found 65% of cited pages updated within a year; "82% within 30 days" and "3.2x" claims are unverified. Only ~11% of domains are cited by both ChatGPT and Perplexity. **vendor data**.
- **Copilot / Bing.** Retrieves from Bing's index; Bing Places is the local equivalent of GBP. Yozigo (232,838 answers, Jun to Sep 2026): ~3.8 domains per answer vs 9.5 ChatGPT, 9.3 Perplexity, 3.5 Gemini. No reliable study of Copilot and small local businesses. **vendor data**.
- **Gemini (app).** Grounded on Google Search; Seer: 78% of cited pages updated within a year (highest); Yext: favoured brand websites (52.1%). Inside Google AIO, Semrush (126M prompts, Jan to Apr 2026): YouTube 83.2M citations, Reddit 35.8M, Wikipedia 32.4M; AI Mode: YouTube 25.9M, Facebook 22.8M, Reddit 17.7M; YouTube's AI Mode share rose ~18% to ~24% Jan to Jun 2026. **vendor data**.
- **Claude.** Web search inferred (2025) to run on Brave Search (Willison's result matching; Brave on Anthropic's subprocessor list); no published selection rules; no Claude-specific 2026 citation study beyond 5W's five-engine report. **independent inference**.
- **Freshness (cross-engine).** Seer Interactive 2026 (7,683 pages, 47,097 citations, ChatGPT/Gemini/Perplexity, Mar to Jun 2026): 75% of cited pages updated within a year, 88% within two; over a quarter were first published 2+ years ago, so maintained updates, not new publishing, drive it. Ahrefs (~17M citations): AI-cited content ~25.7% fresher than organic top 10; AIO's cited pages ~16 days *older*. The "13-week rule" and "4.3x" figures trace to talks, not datasets. **vendor data; folklore for multipliers**.
- **Aggregate indexes.** Everything-PR / 5W Citation Source Index 2026 (680M+ citations from six studies): Reddit in ~40% of answers; journalism 27% of citations (49% for time-sensitive queries). Ahrefs Jul 2026 mentions index: YouTube first, Reddit second, Wikipedia seventh. 5W "State of AI Search 2026" (62 pages, five engines, free) has the fullest disclosed method found. Semrush "ghost citations" (with Indig): 62% of citations produce no brand mention in the answer text. **vendor data**.

---

## 3. Crawlers, robots.txt, Cloudflare, llms.txt, IndexNow

**Three families per vendor** (search, user-fetch, training), each needing its own robots.txt line:

| Vendor | Search index | User-triggered fetch | Training |
|---|---|---|---|
| OpenAI | OAI-SearchBot (controls ChatGPT search inclusion) | ChatGPT-User (OpenAI says robots may not apply) | GPTBot |
| Anthropic | Claude-SearchBot | Claude-User (blocking reduces user-directed visibility) | ClaudeBot (old tokens anthropic-ai, Claude-Web are dead) |
| Perplexity | PerplexityBot (not used for training) | Perplexity-User ("generally does not follow robots.txt") | none declared |
| Google | Googlebot (also feeds AIO/AI Mode) | n/a | Google-Extended (Gemini training/grounding only) |
| Microsoft | Bingbot (feeds Copilot) | n/a | n/a |
| Apple | Applebot | n/a | Applebot-Extended (token, not a bot) |
| Amazon | Amzn-SearchBot (Alexa/Rufus search, no training) | n/a | Amazonbot |
| Meta | Meta-WebIndexer (Meta AI search; volume rose sharply Jul to Aug 2026) | Meta-ExternalFetcher | Meta-ExternalAgent |
| ByteDance | n/a | n/a | Bytespider (no docs; widely reported to ignore robots.txt) |

Sources: OpenAI bots page, Anthropic help article 8896518, Perplexity crawler docs (via extracts); Anagram, Contadu, TechnologyChecker lists 2026. **platform/official via extracts; vendor lists for Amazon/Meta/ByteDance**. OpenAI and Perplexity publish IP JSON files; Anthropic's is disputed. Cloudflare reported Aug 2025 that Perplexity used undeclared crawlers to evade blocks. **independent data**.

**What a small service business should allow:** Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Applebot, Amzn-SearchBot. Training bots (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, Amazonbot, Meta-ExternalAgent, Bytespider) do not affect being cited; a business that wants to be known loses nothing by allowing them. TechnologyChecker (Sep 2026, Cloudflare network): publishers now typically "block training bots and allow answering bots". **practitioner consensus**.

**Cloudflare.** 1 Jul 2025: new domains block AI crawlers by default; Pay Per Crawl beta. 1 Jul 2026: one switch replaced by three categories (AI Crawler/training, AI Agent, mixed-use), on Free plans too. 15 Sep 2026: training and agent crawlers blocked by default on ad-supported pages; search crawlers still allowed; Pay Per Crawl becoming "Pay Per Use". Scope (new domains only vs all free-tier sites) differs between reports; Cloudflare's 2026 post was not retrieved. Radar crawl-to-refer ratios (Jul 2026): Anthropic ~1,917:1, OpenAI ~251:1, Google ~4.7:1; Q1 figures elsewhere differ sharply. — Cloudflare blog Jul 2025; Help Net Security; eWeek. **platform/official (2025), secondary (2026)**. Action: open the Cloudflare dashboard AI-crawl settings and confirm search and user-fetch bots are allowed.

**llms.txt.** Google states Search does not use it (guide updated Jun 2026; Illyes Jul 2025; Mueller likened it to meta keywords and noted bots were not requesting it; Mueller Jun 2026 said its intended use is on-site agents, not discovery). No OpenAI, Anthropic, Perplexity or Meta statement that production answer systems read it. Adoption ~10% of 300,000 domains (SE Ranking) but 97% of files got zero AI-crawler requests in a study month; ~400 of 500M AI-bot visits touched one. Verdict: harmless, ignored; do not spend owner time on it. **platform/official plus independent data**.

**IndexNow.** Confirmed to speed Bing indexing, which feeds Copilot; benefit to ChatGPT is inferred (via Bing partnership) and not confirmed by OpenAI. Cheap to enable (many CMS plugins). — eseospace; geotoolbox. **practitioner**.

---

## 4. Measurement

**Google Search Console.** "Search Generative AI performance reports" announced 3 Jun 2026, UK subset first, global by ~1 Sep 2026. Shows *impressions* where the site's URLs appeared in AIO or AI Mode (combined, not split), by page, country, device, date; data from 18 May 2026; no clicks, queries or positions (clicks stay blended in the normal Performance report). Beta; companion opt-out toggle. — Search Central blog; ppc.land. **platform/official**.

**Bing Webmaster Tools.** AI Performance report, public preview 10 Feb 2026: total citations, cited pages, timeline, grounding queries (the sub-queries Copilot sends to Bing, not user text), across Copilot, Bing AI summaries and unnamed partners. Jun 2026 added Intents, Topics, Citation Share and Compare. No clicks. Free for verified sites; richer than Google's. — Search Engine Land; Momentic. **platform/official via secondary**.

**Free and cheap checks**
- Free one-off graders (no card): Semrush AI Search Visibility Checker (no Claude or Perplexity), Ahrefs AI Visibility Checker (six engines incl. AIO and AI Mode), HubSpot AI Search Grader (three engines, fixed prompts), Mangools AI Search Grader. Snapshots only. **vendor tools**.
- Paid entry points (verify at checkout): Otterly Lite $29/mo (15 prompts, 4 engines); Peec ~$80 to 95/mo (50 prompts, 3 engines); Profound Starter $99/mo annual (ChatGPT only; 7-day trial), Growth $399; Semrush AI Visibility Toolkit $99/mo per domain (25 prompts; base-plan requirement disputed); Ahrefs Brand Radar quoted at $199, $398 or $699/mo on top of an Ahrefs plan. No permanent free tier. **vendor pricing via secondary**.
- Referral traffic: GA4 by referrer (chatgpt.com, perplexity.ai, copilot.microsoft.com, gemini.google.com, claude.ai); AIO and AI Mode clicks appear as ordinary Google organic. **practitioner**.

**A sensible monthly manual check (synthesis of practitioner guides)**
- 10 to 15 customer-style prompts (never the business name): "best [service] near [town]", "who can help me with [problem] in [area]", plus two paraphrases each, run logged-out or in a fresh chat on ChatGPT, Google AI Mode, Perplexity and Copilot (Gemini and Claude if time allows). Record: appears yes/no, position among the 3 to 5 named businesses, description accuracy, sources cited. Add one entity prompt ("What is [business]?") to catch wrong facts (Bullock: 5 of 18 queries returned correct, current details). Run each prompt two or three times, since the same business reappears only ~40 to 50% of the time (Steady Demand, BrightLocal). Log in a spreadsheet beside Search Console AI impressions and Bing citations. About 30 prompts x 4 engines x 2 to 3 runs, roughly two hours a month. **practitioner**.

---

## Claims to verify (sources disagree)
1. Top-10 overlap of AIO citations: 38% (Ahrefs) vs ~17% (BrightEdge).
2. Share of queries with AIO: 13% to 88% depending on panel and device.
3. Bing's share of ChatGPT citations: 87% vs 27%.
4. Reddit's share of Perplexity citations: 17% to 47% (different denominators).
5. Cloudflare Sep 2026 default scope: new domains only vs all free-tier sites.
6. Cloudflare Radar crawl-to-refer ratios: Anthropic 1,917:1 (Jul) vs 20,583:1 (Q1).
7. Date of Google's AI-guide update: 15 May vs 15 June 2026.
8. ChatGPT local data feed: Yelp vs Foursquare vs Bing.
9. Ahrefs Brand Radar and Semrush AI toolkit prices and prerequisites.
10. Whether Anthropic publishes crawler IP ranges.

## Sources
- Google Search Central, AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Google Search Central blog, generative AI performance reports (3 Jun 2026): https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- 9to5Google, opt-out of AI Mode and Overviews (2 Jun 2026): https://9to5google.com/2026/06/02/google-ai-mode-overviews-opt-out/
- Google Q2 2026 earnings remarks: https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2026/
- Search Engine Journal, AIO citations from top-ranking pages drop: https://www.searchenginejournal.com/google-ai-overview-citations-from-top-ranking-pages-drop-sharply/568637/
- Contently, Jun 2026 AIO citations: https://contently.com/2026/06/11/google-ai-overview-citations/
- ppc.land, Semrush 88% AIO on commercial keywords (Oct 2026): https://ppc.land/google-ai-overviews-now-hit-88-of-tracked-commercial-keywords-semrush-finds/
- Quartz, Comscore zero-click and AIO share: https://qz.com/google-zero-click-searches-rate
- Pew Research coverage (Jul 2025): https://www.seroundtable.com/pew-google-ai-overviews-39808.html
- Seer Interactive, content recency and AI visibility 2026: https://www.seerinteractive.com/insights/study-content-recencys-impact-on-ai-visibility-in-2026
- Steady Demand local citations (via Hartzer): https://hartzer.it.com/steady-demand-local-citations-2026/
- Peekl, AI Mode guide citing Steady Demand: https://peekl.io/ai-visibility/guides/what-is-google-ai-mode
- BrightLocal local AI visibility study: https://www.brightlocal.com/research/local-ai-visibility-study/
- Yext research hub and July 2026 briefs: https://www.yext.com/research/ ; https://www.yext.com/research/articles/ai-page-citations-specific-intents-need-specific-pages/
- Lilach Bullock, AI visibility audit: https://www.lilachbullock.com/ai-visibility-audit-small-business/
- Kevin Indig, how AI picks sources: https://www.growth-memo.com/p/the-science-of-how-ai-picks-its-sources
- Semrush ghost citations study: https://www.semrush.com/blog/the-ghost-citations-study/
- Semrush YouTube/AI visibility 2026 (secondary): https://www.artificialstudio.ai/blog/ai-search-youtube-video-seo-semrush-report
- 5W, State of AI Citations / Source Audit Q1 2026: https://www.5wpr.com/research/state-of-ai-citations-2026/ ; https://www.5wpr.com/research/citation-source-audit-q1-2026/
- Everything-PR / 5W Citation Source Index 2026: https://everything-pr.com/ai-platform-citation-source-index-2026
- Profound citations trend report: https://www.tryprofound.com/resources/white-papers/ai-citations-trend-report
- Tinuiti, AI citation patterns 2026: https://tinuiti.com/blog/search/ai-citations/
- Surfer, most-cited domains in Perplexity (Sep 2026): https://surferseo.com/blog/most-cited-domains-perplexity/
- Yozigo, engine citation comparison: https://www.yozigo.ai/blogs/chatgpt-vs-perplexity-vs-gemini-citations-2026
- OpenAI crawler overview: https://developers.openai.com/api/docs/bots
- Anthropic crawler help article: https://support.anthropic.com/en/articles/8896518
- Perplexity crawler docs: https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- Marie Haynes, Google-Extended: https://www.mariehaynes.com/should-you-use-google-extended-in-robots-txt/
- Anagram, AI crawler user-agent list 2026: https://www.anagram.ai/blog/ai-crawler-user-agent-list-2026-14-bots-and-robotstxt-tokens-to-know
- TechnologyChecker, robots.txt across Cloudflare network (Sep 2026): https://technologychecker.io/blog/robots-txt-ai-crawlers-blocking-report
- Cloudflare, Content Independence Day (Jul 2025): https://blog.cloudflare.com/content-independence-day-no-ai-crawl-without-compensation/
- Help Net Security, Cloudflare crawler categories (Jul 2026): https://www.helpnetsecurity.com/2026/07/02/cloudflare-ai-crawler-controls/
- eWeek, Cloudflare Sep 2026 deadline: https://www.eweek.com/news/cloudflare-ai-crawler-controls/
- Crawl-to-refer ratios Jul 2026 (secondary): https://ecorpit.com/ai-crawler-crawl-to-referral-ratio-2026-geo-decision/
- llms.txt adoption data: https://aisaasradar.com/article/llms-txt-adoption-data-2026 ; https://www.getpassionfruit.com/blog/should-i-create-an-llms.txt-file-google-s-2026-guidance-explained
- IndexNow and ChatGPT, confirmed vs not: https://eseospace.com/blog/bing-webmaster-tools-indexnow-ai-search/
- Search Engine Land, Bing AI Performance report: https://searchengineland.com/bing-webmaster-tools-testing-new-ai-performance-report-468039
- Momentic, Bing AI Performance report: https://momenticmarketing.com/blog/bing-wmt-ai-performance-report
- Claude and Brave Search (TechCrunch via aggregator): https://www.ainews.com/p/anthropic-reportedly-using-brave-search-to-power-claude-s-web-results
- Tool pricing comparisons: https://www.get-ryze.ai/blog/ai-visibility-tools-pricing-compared-2026 ; https://www.seo-stuff.com/compare/ai-visibility-tools
- Free checkers compared: https://www.layer3labs.io/comparisons/free-ai-visibility-checkers
- DIY audit method: https://omnionlinestrategies.com/blog/how-to-check-if-your-business-appears-in-chatgpt ; https://llmpulse.ai/blog/ai-visibility-audit-guide/
