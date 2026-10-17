# Paid-Social Creative Practice 2025-2026 (Meta, YouTube, TikTok, LinkedIn), for Small Service Businesses

Research date: 2026-10-14. Labels used throughout:
- **[PLATFORM]**: published by Meta, Google/YouTube, TikTok or LinkedIn (or their commissioned research).
- **[PRACTITIONER]**: credible practitioner, agency or creative-analytics vendor (Jon Loomer, Motion, agency blogs). Often has a commercial interest.
- **[FOLKLORE / WEAK]**: widely repeated, but I found no primary source or only one vendor test.

Method note: the fetch tool could not resolve engineering.fb.com, about.fb.com, jonloomer.com or motionapp.com from this environment (DNS/proxy 403). Platform claims below therefore come from search-result snippets of the primary URLs plus trade press (eMarketer, MediaPost, Kantar). Where I saw only a snippet, I say so. Before publishing, the report writer should treat any number marked "snippet" as needing a check against the primary page.

---

## 1. Meta Andromeda, GEM, Advantage+: what Meta actually published, and what changed in 2025-2026

### Takeaway
Meta has officially published the *mechanics*: Andromeda is a retrieval stage (Dec 2024 engineering post), and GEM is a large foundation ranking model (Nov 2025 post, follow-up Aug 2026) that reported click and conversion lifts. Meta has **not** published (in anything I could find) a per-ad-set creative count, an "Entity ID" definition, or a similarity threshold. "Creative is the new targeting", "8-15 ads per ad set", "Entity ID" and "60% similarity score" are practitioner constructs or folklore built on top of the published mechanics. The well-supported practical point is directional: give the system several *conceptually* different ads (different angle, persona, format, hook), not cosmetic variants.

### Cited Findings
**Andromeda (retrieval), published Dec 2, 2024 [PLATFORM]**
- Meta's engineering blog (Dec 2, 2024) describes Andromeda as "Meta's proprietary machine learning (ML) system design for retrieval in ad recommendation." Retrieval is the first stage of the ads system and narrows "tens of millions of ad candidates into a few thousand relevant ad candidates." It runs on NVIDIA Grace Hopper and Meta MTIA hardware, with "over 100x improvement" in feature-extraction latency and throughput and over 3x end-to-end inference QPS (snippet) — [Meta Engineering, Dec 2024](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/); trade coverage: [MediaPost](https://www.mediapost.com/publications/article/401591)
- Widely repeated figures of "+6% recall" and "+8% ads quality on selected segments" are attributed to the Meta post by third parties. I could not confirm them against the primary text (fetch blocked) — [Adsuploader (secondary)](https://adsuploader.com/blog/meta-andromeda); [Influencer Marketing Hub (secondary)](https://influencermarketinghub.com/meta-andromeda-update-explained-how-meta-ads-work-now/)
- Meta frames Andromeda as tied to its Advantage+ automation push. The post's URL slug is literally "meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine." Third-party coverage says older retrieval relied on multiple independent models and heuristics that scaled poorly as the number of eligible ads grew, which includes the larger number of ads created by generative AI tools — [Meta Engineering](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/); [Influencer Marketing Hub](https://influencermarketinghub.com/meta-andromeda-update-explained-how-meta-ads-work-now/)
- Rollout timing: practitioner sources describe Andromeda as fully replacing the legacy ad-selection system with rollout completing around **October 2025**. That is a practitioner date, not a Meta-announced date [PRACTITIONER] — [The MTM Agency](https://themtmagency.com/blog/meta-andromeda-october-2025-update-why-creative-diversity-now-defines-ad-performance); [Segwise](https://segwise.ai/blog/meta-andromeda-update-creative-strategy-2026)

**GEM (ranking foundation model), published Nov 10, 2025, follow-up Aug 3, 2026 [PLATFORM]**
- Meta's engineering blog (Nov 10, 2025) describes GEM (Generative Ads Recommendation Model) as a foundation model that improves downstream ads-recommendation models through knowledge transfer, "the largest foundation model for recommendation systems (RecSys) in the industry," trained at LLM scale (snippet) — [Meta Engineering, Nov 2025](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/)
- Reported lifts: about 5% more conversions on Instagram and 3% on Facebook Feed (Q2 2025, per secondary coverage). Meta's Jan 2026 newsroom post reports a 3.5% lift in ad clicks on Facebook and more than a 1% gain in Instagram conversions in Q4 2025 (snippet) — [ByteByteGo (secondary)](https://blog.bytebytego.com/p/how-meta-built-a-new-ai-powered-ads); [Meta Newsroom, Jan 2026](https://about.fb.com/news/2026/01/2026-ai-drives-performance/)
- An Aug 3, 2026 engineering post says GEM now trains on several thousand latest-generation GPUs, with training FLOPs scaled 4x in 12 months and end-to-end training efficiency doubled to 20-25% MFU (snippet) — [Meta Engineering, Aug 2026](https://engineering.fb.com/2026/08/03/ml-applications/training-gem-at-llm-scale-meta-ads-recommendation-foundation-model/)

**Advantage+ campaigns and creative**
- In 2025 Meta consolidated Advantage+ into sales, app and leads campaign types. Jon Loomer has a dedicated explainer, but I saw only its title and URL, not its content — [Jon Loomer](https://www.jonloomer.com/advantage-plus-sales-app-leads-campaigns/)
- For Advantage+ leads, Meta's published averages (lower CPL, lower cost per qualified lead, higher quality-lead rate when CRM signals are sent) appear only in third-party blogs, which themselves warn that these are platform-reported averages [PLATFORM via secondary] — [Adspyder](https://adspyder.io/blog/improve-meta-lead-ads/)

**Creative diversification, "Entity ID", creatives per ad set**
- "Entity ID" is an industry shorthand for how Andromeda is believed to group near-identical ads. It is "an industry term (not official Meta)." Sources report that cosmetic changes (headline colour, a swapped word, background music) do not produce a distinct entity [PRACTITIONER] — [Chatterbuzz](https://www.chatterbuzzmedia.com/blog/meta-andromeda-creative-targeting/); [Adsuploader](https://adsuploader.com/blog/meta-andromeda)
- Anecdote: a practitioner reports that three ads shot in the same location were grouped into the same entity even though they targeted different buyers. This suggests visual setting carries weight in similarity [PRACTITIONER, anecdotal] — [Nikhil.pro](https://nikhil.pro/meta-ads-creative-similarity-explained/)
- **[FOLKLORE / WEAK]** "Meta confirmed a Creative Similarity Score above 60% triggers retrieval suppression." I found no Meta source; pages repeat it without attribution — [Chatterbuzz](https://www.chatterbuzzmedia.com/blog/meta-andromeda-creative-targeting/)
- **[FOLKLORE / WEAK]** "Meta recommends 8-15 creatives per ad set." The figure is sourced to "industry analysis from multiple agencies," not Meta. Other practitioner floors range from 6 to 25 per ad set or campaign — [Segwise](https://segwise.ai/blog/meta-andromeda-update-creative-strategy-2026); [Jetfuel](https://jetfuel.agency/metas-2026-algorithm-update-what-andromeda-changed-and-how-to-adapt-your-ads/); [1ClickReport](https://www.1clickreport.com/blog/meta-andromeda-update-2025-guide)
- **[WEAK, single agency test]** One ad set with 25 diverse creatives beat five ad sets of five creatives each: 17% more conversions at 16% lower cost — [cited in Segwise / Chatterbuzz roundups](https://segwise.ai/blog/meta-andromeda-update-creative-strategy-2026)
- Practitioner framing of concept vs variant: diversity means "fundamentally different narratives, hooks, and formats," not "five versions of the same ad with different background colors" [PRACTITIONER] — [Segwise](https://segwise.ai/blog/meta-andromeda-update-creative-strategy-2026); [Precis](https://www.precis.com/resources/meta-andromeda-and-creative-strategy-what-actually-changed-and-what-didnt)
- Motion has published talks titled "Andromeda demands this new ad structure" (Jan 2026) and "Andromeda 2.0 explained: how Meta's algorithm actually picks your winning ads" (Jul 2026). These show that practitioner discussion of an "Andromeda 2.0" phase continued into mid-2026. I saw titles only, not content — [Motion, Jan 2026](https://motionapp.com/library/talk/andromeda-demands-this-new-ad-structure-do-it-easily-with-motion/); [Motion, Jul 2026](https://motionapp.com/library/talk/andromeda-2-0-explained-how-meta-s-algorithm-actually-picks-your-winning-ads/)

### Inferences
- The mechanism Meta published (fast, high-capacity retrieval plus a stronger ranking model) is consistent with the practitioner conclusion that the system can match *different* creatives to *different* people. A distinct concept therefore acts like a targeting input, which is the logic behind "creative is the new targeting." The slogan is a practitioner paraphrase, not a quote I could attribute to a Meta document.
- For a small service business, the actionable version is: consolidate (fewer campaigns and ad sets, broad targeting), and make ad-set contents differ by *angle and persona* (for example: a founder talking head on pain point A, a client testimonial, a static "us vs them", a demo or screen recording), not by colour or copy tweaks. Exact counts are folklore. For a small budget, 3-6 genuinely distinct concepts per ad set is a defensible inference, because many ads get little spend at low budgets anyway.

### Gaps
- Could not read Meta's primary Andromeda/GEM posts in full or any Meta Blueprint/Business Help page on "creative diversification". Meta's official wording on recommended ad counts per ad set is still unverified. (I recall from prior knowledge that Meta Business Help recommends up to ~50 ads per ad set as a system limit and "diverse creative" generally, but I did not verify this in this session.)
- No primary Meta documentation found on how similar creatives are grouped or deduplicated.

---

## 2. Hooks (first 1-3 seconds), specs, safe zones, sound

### Takeaway
Platform guidance consistently says to front-load the brand or proposition and the hook in the opening seconds. TikTok says the content proposition goes in the first 3 seconds and the hook within 6. Google's ABCD framework (Attention, Branding, Connection, Direction) is the best-documented framework, but its "30% sales lift" is a *modelled likelihood* from a Google-commissioned Kantar study (2021), not observed sales. Specs: 9:16 vertical, captions burned in, sound designed-on, and Reels safe zones of roughly 14% top / 35% bottom / 6% sides. The strict "3-second rule" is a measurement convention (Meta counts a 3-second view, TikTok 2 seconds), not a law of attention.

### Cited Findings
- **[PLATFORM, Google/Kantar]** Google states that ads following the ABCDs "have been shown to yield 30% lift in short-term sales likelihood and 17% lift in long-term brand contribution." Source: Google/Kantar, "The Short & the Long of ABCDs Effectiveness," Global, Apr 2021, n=11,000 ads. Kantar scored the ads with its Link AI on 180 creative features. The lift is a *predicted* likelihood, not measured sales — [YouTube ABCDs](https://www.youtube.com/intl/en_ae/ads/abcds-of-effective-video-ads); [Kantar case study](https://www.kantar.com/industries/technology-and-telecoms/validating-googles-abcd-framework-with-the-power-of-artificial-intelligence)
- **[PLATFORM via secondary]** TikTok's creative guidance tells advertisers to introduce the content proposition in the first 3 seconds and to prioritise the hook in the first 6. It specifies 9:16 at 720p or above with sound on. Suggested In-Feed length is 5-60s, with 5-15s cited as optimal (secondary) — [Stackmatix](https://stackmatix.com/blog/tiktok-creative-best-practices-2026); [Selzee](https://selzee.com/blog/tiktok-ads-best-practices)
- **[PRACTITIONER]** Meta Reels safe zones: about 14% top, 35% bottom and 6% per side (1440x2560 canvas ≈ 358px top, 896px bottom, 86px sides). One source claims Meta unified Stories and Reels safe zones in March 2026 with a 20-35% bottom margin. Others say Stories needs 20% and Reels 35%. Keep the CTA and critical text out of the bottom band, because Meta's button and caption overlay cover it. Use the Ads Manager safe-zone overlay — [Billo](https://billo.app/blog/meta-ads-safe-zones); [House of Marketers](https://houseofmarketers.com/guide-to-safe-zones-tiktok-facebook-instagram-stories-reels/); [Adnova](https://adnova.ai/blogs/meta-ad-safe-zones-guide)
- **[PRACTITIONER / Motion]** Hook-rate (thumbstop) is defined as 3-second video views ÷ impressions on Meta. TikTok counts the hook at 2 seconds, so don't compare across platforms. Benchmarks vary by source: Motion (2025) gives <25% weak, 25-35% solid, >35% good. Aggregators put cold prospecting at 18-28% (median ~22%) and call 35-45% elite — [Motion Creative Benchmarks 2026](https://motionapp.com/thumbstop-pulse/creative-benchmarks-2026/); [Adsights](https://www.adsights.ai/resources/glossary/metrics/thumbstop-rate-tsr); [Sparkugc](https://www.sparkugc.com/resources/hook-rate-benchmarks-2026)
- **[PRACTITIONER / Motion]** Motion's hook-format data reports "hit rate" by hook tactic: offer-only 9.29%, confession 8.74%, curiosity 7.77%, bold claim 7.19%. Motion notes that context matters and some tactics have small samples — [Motion top hook formats](https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/top-hook-formats)
- **[FOLKLORE / WEAK]** "80%+ of users watch with sound off" is repeated in skills directories with no source. TikTok's guidance is explicitly sound-on — [Stackmatix](https://stackmatix.com/blog/tiktok-creative-best-practices-2026)
- **[FOLKLORE / WEAK]** "TikTok's algorithm scores ads on watch time within the opening window" is stated without a source — [Stackmatix](https://stackmatix.com/blog/tiktok-creative-best-practices-2026)

### Inferences
- For service businesses, the first 1-3 seconds should name the viewer or problem ("Coaches doing $10-30k/month...") or show a pattern interrupt (a result, screen or face mid-sentence). Use on-screen text that duplicates the spoken hook, because both sound-on and sound-off viewing exist. Under ABCD, include early branding (founder face or name, logo) and a single clear direction (CTA).
- Hook rate is a diagnostic, not a goal. A high hook rate with poor hold rate or CTR means the hook is mismatched to the body or offer.

### Gaps
- Could not access Meta's own Reels creative best-practice page or TikTok Creative Center pages directly. TikTok's exact current wording and any TikTok-published performance stats remain unverified.
- No independent replication of the ABCD 30% figure was found. It is a 2021 study and is older than the 2025-2026 window.

---

## 3. UGC, creator-style and "native" ads; Spark Ads; partnership ads; formats for services

### Takeaway
Meta's own (self-reported) data says partnership ads (creator plus brand handles) cut CPA by about 19% and lift CTR by about 13% versus business-as-usual ads. Meta expanded the tooling in 2025 (Partnership Ads Hub "All" tab, Facebook Partnership Ads API, optional brand handle). Spark Ads boost organic TikTok posts and keep their social proof. The "ugly ads" / native-looking school (Barry Hott) is credible practitioner consensus, but not controlled evidence. For services, the native equivalents are founder talking-heads, client testimonials, screen-share demos, and lo-fi static formats (notes-app, "us vs them", listicles).

### Cited Findings
- **[PLATFORM, self-reported]** Brands using partnership ads saw an average 19% reduction in CPA versus business-as-usual ads (Advertising Week New York 2025 update). Meta data also reports 13% higher CTR — [eMarketer](https://www.emarketer.com/content/meta-expands-partnership-ads-turn-creator-content-performance); [eMarketer](https://www.emarketer.com/content/meta-unveils-new-features-streamline-creator-partnerships); [Media Marketing](https://www.media-marketing.com/en/news/meta-builds-the-next-phase-of-advertising-through-ai-and-content-creators/)
- **[PLATFORM]** 2025 tooling: Partnership Ads Hub "All" tab (pulls in UGC, affiliate posts and brand mentions with creator metrics); Facebook Partnership Ads API to convert branded content or UGC at scale; brands can choose to show or hide their handle on partnership promotions — [eMarketer](https://www.emarketer.com/content/meta-unveils-new-features-streamline-creator-partnerships)
- **[PLATFORM, NewFronts May 2025]** Meta tested Reels Trending Ads (placed after popular creator Reels) and a Trends feature in Instagram Creator Marketplace. Meta cited a survey in which 53% of users say they're more likely to buy something promoted by a creator on Reels — [Media in Canada](https://mediaincanada.com/2025/05/09/newfronts-2025-meta); [Social Samosa](https://www.socialsamosa.com/news-2/meta-tests-new-ad-tools-brands-creators-across-insta-fb-threads-9050695)
- **[PLATFORM-adjacent]** Spark Ads mechanics: they use an organic post (the brand's or a creator's, via an authorisation code), engagement keeps accumulating on the post, the brand must hold commercial rights to the sound, and edits are locked once the post runs as a Spark Ad — [MiQ](https://creative.miqdigital.com/resources/tiktok-spark-ads)
- **[PRACTITIONER]** Barry Hott's "ugly ads" are described as ads that "break away from traditional aesthetics and instead focus on what resonates with consumers." A 2025 follower piece stresses the point is "meeting prospects where they're at," not making things deliberately ugly — [Northbeam](https://northbeam.io/post/unleashing-the-power-of-ugly-ads); [Alex Cooper, 2025](https://alexcooper.beehiiv.com/p/7-facebook-advertising-lessons-i-learned-from-barry-hott)
- **[PRACTITIONER]** Dara Denney's process starts with creative strategy research: customer journey before and after purchase, competitor analysis, review mining and past performance data (event pages from 2022-23) — [Motion](https://motionapp.com/events/creative-strategy-workflow-with-dara-denney)

### Inferences
- Service-business translation of "native": (1) founder or practitioner talking-head, selfie-framed, with captions; (2) client testimonial in their own words (or partnership ads run from a client or creator handle, where permitted); (3) screen-recording demos of the deliverable, such as a dashboard, a before/after audit, or a booking calendar; (4) static lo-fi formats like notes-app lists, tweet or Reddit screenshot style, "us vs them" tables and listicles. These are cheap to make and conceptually distinct, which also serves Andromeda-era diversification.
- Partnership ads with satisfied clients or micro-creators in the niche are the closest platform-endorsed lever for coaches and consultants. The 19% CPA figure is Meta's average and is not service-business-specific.

### Gaps
- No controlled, independent study found comparing polished and native creative for service businesses. Evidence is self-reported platform averages and practitioner experience.
- TikTok-published Spark Ads performance stats were not found in this session.
- Could not retrieve Savannah Sanchez or Foxwell Digital primary material in this session.

---

## 4. LinkedIn for B2B services: Thought Leader Ads, document ads, video, B2B Institute

### Takeaway
Thought Leader Ads (promoting an employee's or founder's personal post) are the consensus top-performing LinkedIn format among practitioners in 2025-2026. LinkedIn's own cited figure is about 2x CTR versus single-image ads with the same objective, and one agency reports 6.9x on its own dataset. Document ads are favoured for lower-funnel lead capture. Video is growing in spend share but has lower CTR. I did not retrieve B2B Institute research in this session.

### Cited Findings
- **[PLATFORM via secondary]** LinkedIn data cited by a 2026 guide: Thought Leader Ads see about 2x higher CTR on average than other single-image ads with the same objective — [ZenABM](https://zenabm.com/blog/linkedin-thought-leader-ads-ultimate-guide)
- **[PRACTITIONER, single agency dataset]** A 15-month B2B SaaS dataset shows Thought Leader Ads at ~4.65% CTR versus 0.68% for other formats, a 6.9x lift — [Factors.ai](https://www.factors.ai/blog/linkedin-ads-b2b-guide)
- **[PRACTITIONER, unclear methodology]** Benchmark ranges: Thought Leader Ads 2.0-5.0% CTR; document ads 1.2-2.5% CTR with CPL often 30-40% lower than other formats; video 0.8-1.8% CTR. One analysis reports video's share of spend grew from 11.9% to 16.6% — [Generateleads](https://generateleads.online/linkedin-ads-b2b-lead-generation-2026/); [Factors.ai](https://www.factors.ai/blog/why-is-linkedin-advertising-crucial-for-b2b-marketing); [Funnel.io](https://funnel.io/blog/linkedin-advertising-2026)
- **[PRACTITIONER]** Search Engine Land lists B2B LinkedIn tests to run in 2026, and Fractional Demand has a 2026 Thought Leader Ads playbook (titles seen, content not fetched) — [Search Engine Land](https://searchengineland.com/b2b-linkedin-ads-tests-run-471267); [Fractional Demand](https://fractionaldemand.com/resources/blog/thought-leader-ads-2026)

### Inferences
- For consultants and agencies selling B2B, the founder's own LinkedIn posts promoted as Thought Leader Ads are the obvious first format: native, personal, and consistent with the "talking-head founder" logic on Meta. Document ads (a checklist, teardown or framework PDF) with LinkedIn Lead Gen Forms suit lead capture.

### Gaps
- B2B Institute (LinkedIn) research, such as its 95-5 rule and brand-building guidance, was not retrieved. Do not cite B2B Institute figures from these notes.
- No LinkedIn-published 2025-2026 benchmarks were retrieved directly. All CTR and CPL figures are vendor-reported.

---

## 5. Creative testing methodology now

### Takeaway
Meta shipped a native **creative testing** feature in Ads Manager in 2025. It runs an A/B-style test of 2-5 new ads (some advertisers report 10) inside an existing ad set, with equal budget split, one variation per user, and results in Experiments. Meta suggests capping it at about 20% of budget. The practitioner pattern is separate concept testing (a sandbox or ABO test campaign, or Meta's tool), then graduating winners into a consolidated scaling campaign. Judge with a metric ladder: hook rate → hold rate → CTR → CPA / cost per qualified lead. Hit rates are low (practitioners estimate ~5% of creatives become winners), so volume of distinct concepts matters more than optimising variants.

### Cited Findings
- **[PLATFORM via practitioner reporting]** Meta's creative testing tool lets you test up to 5 ads (2-5 new test ads) within an existing ad set. Budget is split equally, each user sees one variation, and Meta does not optimise delivery toward specific ads during the test. It requires the Highest Volume bid strategy (no cost-per-result goal, bid cap or ROAS goal). Meta suggests capping the test at about 20% of campaign or ad set budget. You must create new ads (existing ads can't be tested). Results appear in Experiments — [Jon Loomer, Meta Creative Testing](https://www.jonloomer.com/meta-creative-testing/); [Jon Loomer QVT](https://www.jonloomer.com/qvt/creative-testing-feature/); [EasyInsights](https://easyinsights.ai/blog/metas-update-a-new-way-to-test-creatives-from-a-b-to-ai-led-optimization/)
- **[PRACTITIONER]** Jon Loomer reports some advertisers now see the limit raised to 10 ads ("or maybe 11"). Ambiguity remains about whether the original ad counts in the total — [Jon Loomer](https://www.jonloomer.com/qvt/meta-expanding-creative-testing-10-ads/)
- **[PRACTITIONER]** Hook-rate definitions and benchmarks: see Q2. Motion's 2026 Creative Benchmarks covers 550,000+ ads from 6,000+ advertisers, about $1.3B of Facebook/Instagram spend, Sept 2025-early Jan 2026 (secondary summary) — [Motion Creative Benchmarks 2026](https://motionapp.com/thumbstop-pulse/creative-benchmarks-2026/); [Adsights](https://www.adsights.ai/resources/guides/video-creative-metrics-benchmarks-2026-guide)
- **[PRACTITIONER]** "Only around 5% of creatives become winners, so the account that ships the most good ads wins" — [Taylor Sicard](https://taylorsicard.com/blog/meta-ads-creative-benchmarks-2026)
- **[PRACTITIONER]** For lead-gen, the in-platform lead number "will look great regardless." Judge quality in the CRM and feed qualified-lead or SQL signals back via CAPI / offline conversions — [Growthspree](https://www.growthspreeofficial.com/blogs/meta-advantage-plus-b2b.md); [Adspyder](https://adspyder.io/blog/improve-meta-lead-ads/)

### Inferences
- Small-budget testing protocol (inferred from the above, not a published standard): use Meta's creative testing tool, or a small ABO test ad set, with 3-5 *distinct concepts*. Give each concept enough spend to reach a decision on a leading metric. Practitioners commonly use about 1-2x target CPA per ad before killing on CPA, but this is a rule of thumb. Kill early on very weak hook rate (well under ~20-25% cold) or CTR. Move winners into the main consolidated campaign rather than duplicating.
- Dynamic creative / "flexible" ad formats let Meta mix assets, but they hide which concept won. Use them for scaling variety, not for learning.

### Gaps
- Could not verify Meta's own Business Help Center documentation of the creative testing tool (exact launch month in 2025, current ad limit).
- No primary material retrieved from Common Thread Collective, Foxwell Digital or Andrew Foxwell on their current concept-testing frameworks. Specific "kill/scale" thresholds attributed to them are unverified.
- No published, evidence-based budget-per-test standard was found. All figures are rules of thumb.

---

## 6. Creative fatigue: detection, refresh cadence, frequency

### Takeaway
No Meta-published refresh cadence exists that I could find. Practitioners agree on: watch leading signals (rising frequency, falling hook rate or CTR, rising CPM or CPA) rather than waiting for Meta's "creative fatigue" label. Refresh cadence scales with spend and audience size. A small-budget account (under $10k/month) can often run a concept for 6-12 weeks.

### Cited Findings
- **[PRACTITIONER]** Spend-tiered refresh guide: under $10K/month → 6-12 weeks per concept; $10-50K → 4-8 weeks; $50-250K → 2-6 weeks; over $250K or narrow retargeting → 1-3 weeks — [Succession Media](https://succession.media/guides/meta-creative-fatigue-how-many-creatives-to-test/)
- **[PRACTITIONER]** Frequency watch lines: cold prospecting around 2.5 (7-day); others use 3.5-4.0 paired with a CTR drop of 20% or more; retargeting tolerates about 5-7 — [Good Morning Co](https://goodmorningco.com/blog/what-is-creative-fatigue-meta-ads-frequency-thresholds); [Adsights](https://www.adsights.ai/blog/topics/creative-strategy/creative-fatigue-in-meta-ads-detection-and-management-strategies)
- **[PRACTITIONER]** Meta's in-platform "Creative Fatigue" label appears only after cost per result has risen sharply (described as doubling), so practitioners recommend monitoring leading indicators — [Adsights](https://www.adsights.ai/blog/topics/creative-strategy/creative-fatigue-in-meta-ads-detection-and-management-strategies)
- **[PRACTITIONER, vendor data]** An analysis of 2.9M inactive Meta ads (Jan 2025-Apr 2026) found a median run of 3 days, with only 5% running past 38 days. This mostly reflects advertisers killing losers fast, not fatigue of winners. An MHI analysis of 500+ DTC campaigns put average lifespan at 21-35 days — [Skaler](https://skaler.app/blog/creative-fatigue-meta-ads-2026); [MHI Growth Engine](https://mhigrowthengine.com/blog/reduce-creative-fatigue-meta-ads/)

### Inferences
- Small service businesses with narrow local or niche audiences reach high frequency faster even at low spend. Frequency relative to audience size matters more than spend alone.
- A practical refresh is a *new concept or new hook on a proven body*, not a colour swap. Cosmetic refreshes may be grouped as the same entity under Andromeda (see Q1).

### Gaps
- No Meta-published fatigue thresholds or refresh guidance found. All numbers are practitioner or vendor numbers, and their definitions disagree.

---

## 7. Ad-to-landing-page message match; lead form vs landing page; quiz funnels

### Takeaway
Message match is universally recommended, but evidence for it is mostly old case studies and vendor tests: the Moz/Conversion Rate Experts "212%" case and a ConversionLab dynamic-headline test (+31.4%). For service businesses on Meta, instant forms convert at higher rates, but lead quality is the trade-off. Meta's newer tools let you add qualifying questions and conditional logic, and optimise on downstream CRM signals. I found no rigorous evidence on quiz funnels.

### Cited Findings
- **[PRACTITIONER, secondary]** The classic Moz / Conversion Rate Experts case study reports a 212% conversion lift from fixing ad-to-page message match (seen only secondhand) — [Webtonic](https://www.webtonic.io/blog/message-match)
- **[PRACTITIONER, vendor test]** ConversionLab's dynamic headline matched to visitor search terms produced a 31.4% lift in trial sign-ups over 77 days (Campaign Monitor) — [Webtonic](https://www.webtonic.io/blog/message-match); [Racklify](https://racklify.com/encyclopedia/measuring-ad-to-landing-page-match-metrics-and-testing-methods/)
- **[PRACTITIONER, secondary]** Unbounce median landing-page conversion rate is cited as 6.6%, with top performers at 15-20%+. Sending paid traffic to a homepage instead of a matched page reportedly suppresses conversion 4-5x (Leadpages, secondary). "Each form field removed ≈10% lift" is unsourced folklore — [Foundry CRO](https://foundrycro.com/blog/landing-page-headline-benchmarks-2026/); [SaaS Hero](https://www.saashero.net/google-ppc/b2b-landing-page-cro-tips/)
- **[PRACTITIONER]** Instant forms "typically have a higher conversion rate than campaigns that capture leads off-platform, but the uptick in leads often comes at the expense of quality" (Aug 2024) — [3rd and Lamar](https://3rdandlamar.com/news/capitalize-on-these-recent-meta-ads-developments/)
- **[PRACTITIONER]** Jon Loomer argues that the low-quality reputation of instant forms rests on outdated assumptions, that both options have trade-offs, and that you should not choose on cost per lead alone — [Jon Loomer, Meta lead gen](https://www.jonloomer.com/meta-ads-lead-generation/)
- **[PLATFORM, vendor-published case]** A Meta-hosted case study: a martial-arts business used conditional logic and pre-filled details in instant forms and lifted lead-to-customer conversion 62% versus plain instant forms. Meta has also tested quality-lead optimisation for instant forms using website or CRM signals via CAPI or Pixel — [Meta (Workplace-hosted)](https://projecter.workplace.com/business/news/create-more-valuable-leads-than-ever-with-metas-instant-forms); [3rd and Lamar](https://3rdandlamar.com/news/capitalize-on-these-recent-meta-ads-developments/)

### Inferences
- Service-business default: if there is no CRM feedback loop yet, test an instant form with "higher intent" settings and 2-3 qualifying questions against a matched landing page. Judge on booked calls or qualified leads, not CPL. Once CRM or CAPI conversion events exist, optimise toward them.
- Message match for Meta means the landing headline repeats the ad's hook or angle. With 3-6 diverse concepts, this argues for a few angle-specific headlines (or dynamic headline swaps), not one generic page.
- Quiz funnels: practitioner-popular, but I found no credible evidence in this session.

### Gaps
- No controlled evidence on quiz funnels for service businesses.
- No 2025-2026 Meta documentation retrieved on how Advantage+ leads interacts with instant-form vs website-form choice.

---

## 8. Volume: new creatives per week for top spenders vs realistic small-business cadence

### Takeaway
Published figures on what top spenders ship weekly are thin and vendor-sourced. Practitioner guides scale testing volume with spend: about 1-2 new concepts per week under $5K/month, and 4-6 per week at $20K-$100K/month. For a small service business, a sustainable cadence is roughly 2-4 new distinct concepts per month, plus hook variants of winners. AI tooling (including Meta's own generative tools) is the stated reason retrieval had to scale.

### Cited Findings
- **[PRACTITIONER]** Testing volume guide: 1-2 new concepts weekly under $5K/month; 4-6 at $20K-$100K/month — [Succession Media](https://succession.media/guides/meta-creative-fatigue-how-many-creatives-to-test/)
- **[PRACTITIONER]** About 5% of creatives become winners, the basis for the "volume wins" argument — [Taylor Sicard](https://taylorsicard.com/blog/meta-ads-creative-benchmarks-2026)
- **[PRACTITIONER]** Motion's 2026 benchmarks report includes creative volume and hit-rate data by spend tier (550k+ ads, Sept 2025-Jan 2026). I could not retrieve the tier-specific numbers — [Motion](https://motionapp.com/thumbstop-pulse/creative-benchmarks-2026/); [Taylor Sicard summary](https://taylorsicard.com/blog/meta-ads-creative-benchmarks-2026)
- **[PRACTITIONER]** Design Pickle and others frame the Advantage+ / Andromeda era as needing a production system for steady creative output — [Design Pickle](https://designpickle.com/blog/produce-meta-ad-creative-advantage-plus-era)

### Inferences
- A realistic small-business engine: one founder filming session per month (e.g., 8-12 talking-head hooks and bodies) → 3-4 distinct concepts plus 2-3 hook variants each. Add 2-4 static concepts (testimonial quote cards, notes-app, us-vs-them) and 1-2 client testimonials or partnership ads per quarter. This matches the under-$5K tier guidance and the diversification logic.
- Exact counts ("you must launch 50 ads a week") are folklore for small accounts. At low budgets, extra ads mostly receive no spend.

### Gaps
- No primary data found on weekly creative output of top-spending advertisers, and no Foxwell, CTC or Motion tier figures were retrieved. This is a key gap for the report writer.

---

## Cross-cutting folklore list (flag in report)
- "Meta confirmed 60% creative similarity threshold" — no primary source.
- "Meta recommends 8-15 (or 10-15, 15-25) creatives per ad set" — agency figures, not Meta.
- "Entity ID" — an industry label, not Meta terminology.
- "3-second rule" — a metric convention (Meta's 3s view; TikTok's 2s), not a validated attention threshold. The Meta and TikTok guidance to front-load the proposition is real.
- "80%+ watch sound-off" — unsourced in current material; TikTok guidance is sound-on.
- "Each removed form field = +10% conversions" — unsourced.
- "ABCD = +30% sales" — a modelled *likelihood* from a 2021 Google-commissioned Kantar study, not observed sales.
- Partnership ads "-19% CPA" — real Meta claim but self-reported average.
