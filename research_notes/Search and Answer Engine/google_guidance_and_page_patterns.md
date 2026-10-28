# Google and Bing content guidance, and page-level practices that still matter (as of 2026-10-28)

Scope: small service businesses publishing answer pages on an existing site; emphasis on Nov 2025 to Oct 2026. Method: every claim rests on web-search extracts; no primary page was fetched in full. Strength tags: **[official]** = Google/Microsoft/W3C/DOJ documentation or blog; **[vendor data]** = an SEO tool company's own dataset; **[independent data]** = study not selling the thing measured; **[practitioner]** = experienced opinion; **[folklore]** = widely repeated, unsourced.

## 1. Google Search Central guidance in 2026

**Helpful, people-first content.** Google's "Creating helpful, reliable, people-first content" page remains the core document. Trade press reports it was revised with a last-updated date of 1 Oct 2026: it now defines "main content," lists four attributes raters assess (effort, originality, talent/skill, accuracy), and adds a warning that fabricated author profiles (AI headshots, invented names, false credentials) signal a low-quality page. Google "strongly encourages" accurate bylines "where readers might expect it." **[official, via secondary reporting: ppc.land, relevantaudience.com]** A consultant's reading is that bylines are not a ranking factor, only something readers value. **[practitioner: Marie Haynes]** The self-assessment questions still include "is this written by someone who demonstrably knows the topic" and "is there background about the author or site, e.g. an About page or author page," plus "are you changing dates to make pages seem fresh when content has not substantially changed." **[official, wording from third-party reproductions; verify live page]**

**AI-generated content.** Google's Feb 2023 statement still governs: "appropriate use of AI or automation is not against our guidelines"; using automation "with the primary purpose of manipulating ranking" violates spam policies. **[official: developers.google.com 2023 blog]** The March 2024 spam policies (scaled content abuse, site reputation abuse, expired domain abuse) are unchanged in category; 2026 added no new spam categories. **[official policy; practitioner summaries]** Scaled content abuse covers "many pages made for rankings, not readers," regardless of whether AI, humans or scraping produced them. Expired domain abuse targets reuse of a domain in a way that does not match its original purpose, not expired domains per se. **[practitioner: dynadot, seo-kreativ]** Site reputation abuse: since Nov 2024, "no amount of first-party involvement" exempts third-party content; enforcement was still manual actions as of early 2025, with algorithmic enforcement "planned." Google said the March and June 2026 spam updates did not target site reputation abuse. **[official via Search Engine Land / SERoundtable; 2026 status unconfirmed]** Practical read: none of these bite a one-owner service site unless it mass-produces pages or hosts others' content for rankings.

**Core and spam updates, Nov 2025 to Oct 2026 (confirmed dates).** December 2025 broad core update (18-day rollout). Google added documentation in Dec 2025 confirming it also ships smaller, unannounced core updates. March 2026 core update: 27 Mar to 8 Apr. May 2026 core update: 21 May to 2 Jun. Spam updates: 24-25 Mar, 24-26 Jun, 18-21 Aug, 24 Sep to 8 Oct 2026 (Google called the last one "nothing specifically new"). **[official via SERoundtable, Search Engine Land, SEJ]**

**What the 2026 core updates rewarded or hit.** Google published no winners/losers and repeated that owners need do nothing special. Third-party analyses (Sistrix-based and agency data) broadly agree that originators, first-party brand sites, niche authority sites and first-hand content gained, while aggregators, thin affiliate comparison pages and unreviewed AI content lost. Forums/UGC is contradictory: some say Reddit-style content lost in both updates, others list forums among March winners; May reports say forums dropped and some very authoritative domains (NYT, Nature, NIH) also lost. Vendor percentages conflict; do not quote them. **[vendor data / practitioner; contradictory]** Danny Sullivan's small-independent-site statements ("incremental, no big small-site update"; Google "denies brand bias") date from 2024-2025; nothing from 2026 found. **[official, older]**

**Google's own advice about AI features.** "AI features and your website": "There are no additional requirements to appear in AI Overviews or AI Mode, nor other special optimizations necessary"; no new machine-readable files or markup; "no special schema.org structured data that you need to add"; pages must be indexed and snippet-eligible. nosnippet, data-nosnippet, max-snippet and noindex also limit AI features; Google-Extended governs Gemini training/grounding only, not AI Overviews. **[official]** On 15 May 2026 Google published "Optimizing your website for generative AI features": it "is still SEO"; build unique, non-commodity content that is not what "a generative AI model could easily produce"; Search ignores llms.txt; "no requirement to break content into tiny pieces"; structured data not required but useful for rich results; includes local-business guidance and a forward look at agents. **[official; details from snippets and secondary coverage]**

**Dates and freshness.** Google's "Influence your byline dates" page: a byline date is Google's own estimate; show one clear visible date, keep it consistent with structured data (datePublished / dateModified), avoid future dates; no guarantee the date is shown. Give a fresh date only when content "has been substantially changed." **[official]**

## 2. Structured data in 2026

**What has been removed.** 2023: FAQ rich results limited to government/health sites; HowTo deprecated (never returned). 12 Jun 2025: Course Info, Claim Review, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing retired (Book Actions was announced then kept; docs for five types removed 9 Sep 2025). Nov 2025: Practice Problem deprecated, Search Console support gone Jan 2026. **7 May 2026: FAQ rich results stopped appearing for everyone**; FAQ reports and Rich Results Test support removed June 2026, API support ending Aug 2026. FAQPage markup stays valid and harmless. Google says rankings are unaffected. **[official via Search Central updates log and SEJ]**

**Still worth adding for a service business** (rich-result eligibility and entity clarity, not AI citations): Organization (logo, contact, sameAs); LocalBusiness and subtypes (address, hours, geo, areaServed); Person for the owner/author, linked from Article.author; Article/BlogPosting with author, datePublished, dateModified; BreadcrumbList; VideoObject if you host video. Service schema has no Google rich result and is low priority. Markup must describe content visible on the page. **[official docs; practitioner]**

**Self-serving review rule (unchanged since Sep 2019).** Review/AggregateRating on LocalBusiness or Organization (and subtypes) for the business's own reviews is "self-serving" and will not show stars, including via third-party widgets; review properties are "only recommended for sites that capture reviews about other local businesses." No manual action results; you need not remove it, it simply does not display. Reviews of a product you sell, marked up on a Product, can still qualify. **[official]**

**Does structured data influence AI Overviews or LLM citations?** The strongest evidence says no. Ahrefs (May 2026) tracked 1,885 pages that added JSON-LD against ~4,000 controls: AI Mode and ChatGPT changes were indistinguishable from zero; AI Overviews citations fell 4.6% relative to controls (statistically significant, small). Caveat: the sample was already-cited pages. A companion test found AI retrieval reads visible HTML and ignores JSON-LD. An earlier Ahrefs correlation (cited pages ~3x more likely to carry JSON-LD) did not hold as causation. **[vendor data, controlled]** Contradicting claims of 60-70% lifts from "attribute-rich schema" come from small vendor samples with no visible method. **[folklore]** One arXiv paper argues structured data helps in systems that parse it (Google, Bing) but not flat-text retrievers. **[independent, theoretical]** Geeky Tech found ChatGPT-cited B2B pages had higher schema rates than AIO-only ones (correlation). **[vendor data]**

## 3. Page patterns that get cited

- **Answer first.** One analysis puts 44.2% of LLM citations in the first 30% of page content; the "first 100 words after a heading" rule is vendor advice with no method. **[vendor data / practitioner]**
- **Length.** Ahrefs: Spearman ~0.04 between word count and AI Overview citations across 174,048 pages; cited pages average ~1,282 words. SE Ranking (129k domains): pages over 2,900 words earned 59% more ChatGPT citations than pages under 800, probably because they cover more subtopics. Geeky Tech B2B median: 2,151 words, 27 headings. Net: write to the question, not a word count. **[vendor data; differs by engine]**
- **Headings, lists, tables.** Consistently recommended; vendor stats (68.7% of cited pages use strict hierarchy; 2.8x; tables extracted 43% more accurately) are unverified. A 252,000-trial experiment across six models reportedly found topical relevance and list position dominate, with formatting adding little once relevance is equal. **[vendor data / practitioner; directional]**
- **Page types.** Wix Studio AI Search Lab (75,000 answers, 1M+ citations; ChatGPT, AI Mode, Perplexity; Mar 2026): listicles 21.9%, articles 16.7%, product pages 13.7%; intent predicts page type better than industry. For professional-services "best X" lists, neutral third-party listicles took ~81% of citations vs ~19% for self-promotional ones. DeltaV (25,337 citations) found the same ordering. **[vendor data, two converging sources]**
- **"How much does X cost."** INSIDEA (49 buyer questions, 4 models, 2,667 answers, Sep-Oct 2026): for "how much/how long" questions, answers cited pages that state a number or timeline outright; lists were only 6.6%. Practitioners add: "contact us for pricing" pages give AI nothing to quote; put plain-text prices or ranges and a last-updated date. **[vendor data, small sample; practitioner]**
- **Original data, first-hand experience, named author.** Claims of 3-10x for original research, 156% for proprietary data and 89% for credentialed bylines come from marketing sites with no visible method. **[folklore-adjacent]** Zyppy's May 2026 meta-analysis (23 factors): brand web mentions correlate 0.664 with AI Overview visibility, the strongest factor. **[vendor data]** Muck Rack: earned media ~84% of AI citations, paid 0.3%. **[vendor data]**
- **Rankings and clusters.** Ahrefs: only 37.9% of AI Overview citations now come from the top 10 organic results (down from 76% in mid-2025); 31% come from beyond position 100. Practitioners read this as "cover the cluster, not one head term." **[vendor data; practitioner inference]**
- **Freshness.** Ahrefs (17M citations, Jul 2025): AI-cited URLs average 1,064 days old vs 1,432 for organic (25.7% fresher), but AI Overviews cite slightly older content than organic; the author advises new quality pages over constant re-dating. **[vendor data]**
- **AI-written text.** Ahrefs reports AI Overviews cite AI-generated content at least as often as human writing. **[vendor data]**

## 4. Site basics

- **Core Web Vitals.** Thresholds unchanged: LCP 2.5 s, INP 200 ms, CLS 0.1, at the 75th percentile of real-user (field) data; INP replaced FID in March 2024. Claims that the March 2026 core update cut INP to 150 ms or LCP to 2.0 s appear only on SEO blogs with no Google source; treat as false until shown otherwise. Google's position: CWV are one of several page-experience signals, small next to relevance. **[official thresholds; vendor conflict flagged]**
- **Mobile and HTTPS.** Mobile-first indexing is complete; HTTPS has been a lightweight ranking signal since 2014 and is table stakes. **[official, long-standing; not re-searched]**
- **Canonical, sitemap, robots.** Self-referencing canonical, one XML sitemap submitted to both consoles, robots.txt that does not block CSS/JS or pages you want cited. Kajabi's docs say use noindex, not robots.txt, to block. **[official]**
- **Indexing speed for small sites.** No official timeline. "Discovered, currently not indexed" on a small or new site can last weeks to months; URL Inspection "Request indexing" helps for a few pages; home-page internal links and a clean sitemap matter most; "Crawled, not indexed" signals a quality or duplication issue. **[practitioner; anecdotal]**
- **Search Console essentials.** Verify the domain property; submit the sitemap; watch Page indexing, Performance (AI-features visibility and branded-query filters rolled out slowly in 2026) and Manual actions. **[official; rollout reports from SERoundtable]**
- **Bing Webmaster Tools and IndexNow.** Free; import a verified Search Console property to skip re-verification. Since Feb 2026 an "AI Performance" report shows citations in Copilot and Bing AI summaries (Microsoft: not traffic or clicks). Bing and Copilot share one crawling/indexing/ranking foundation, so an unindexed page cannot be cited. IndexNow (Oct 2026 participants: Bing, Yandex, Seznam, Naver, Yep, Internet Archive, Amazon; not Google) pushes new/changed URLs but "does not guarantee immediate indexing." No first-party OpenAI statement ties Bing indexing to ChatGPT visibility. **[official (Microsoft) via vendor summaries; practitioner]**
- **Accessibility basics.** Alt text, heading order, landmarks, contrast and keyboard access serve screen readers and give extractors the same structural map; the LLM-side benefit is plausible but untested (vendor "280%" lifts have no source). **[practitioner]**
- **Builders.** Wix: per-page JSON-LD in Advanced SEO (about 7,000 chars per block, up to 5 blocks), auto sitemap, editable robots.txt, default LocalBusiness/blog markup; author pages not covered. Squarespace: auto sitemap; schema only via Code Injection (site-wide header) or per-page code; auto markup only for products, posts, organization; author bio via profile plus a manual author page. WordPress: everything possible; native author archives are thin, so a plugin or manual Person schema is needed. GoHighLevel: no schema builder, manual JSON-LD in per-page header tracking; robots.txt at domain level; auto sitemap unconfirmed. Kajabi: Header Page Scripts is site-wide (except checkout); code editor on higher plans; per-post JSON-LD hard without third-party tools; auto sitemap reported by a third party; no author-page support found. **[official docs for Wix/Kajabi; practitioner for the rest; gaps]**

## 5. Accessibility and legal basics

- **Lawsuit trend.** Seyfarth Shaw counted ~3,117 federal website accessibility suits in 2025 (of 8,667 ADA Title III filings); counts above 5,000 include state courts. H1 2026 federal filings reported at ~5,006, up 9%. About 68% of defendants earn under $50M; 45% of 2025 federal cases hit previously sued companies; e-commerce dominates; overlay widgets do not prevent suits (25.6% of Q1 2026 suits named sites with a widget). Settlements reported at $5,000-$20,000. No small-business exemption under Title III; the Disabled Access Credit may help businesses with 30 or fewer employees or $1M or less revenue. **[independent data (law-firm counts) via vendor summaries]**
- **Standard.** No federal technical standard for private sites; courts and settlements converge on WCAG 2.1 AA, with 2.2 AA the safer target. WCAG 2.2 added nine criteria; the AA ones are Focus Not Obscured (Minimum), Dragging Movements, Target Size (Minimum, 24x24 CSS px), Accessible Authentication (Minimum); Consistent Help and Redundant Entry are Level A; Focus Appearance is AAA. **[official (W3C) via secondary]**
- **DOJ Title II.** 20 Apr 2026 interim final rule extended government deadlines to Apr 2027 (large) and 2028 (small); irrelevant to private businesses except as a signal of direction. HHS Section 504 web rule still May 2026 for HHS-funded entities. **[official via law-firm alerts]**
- **European Accessibility Act (28 Jun 2025).** Applies to services offered into the EU, with a microenterprise exemption; technical benchmark is EN 301 549 (WCAG 2.1 AA). Relevant to a US coach or consultant only if actively selling to EU consumers. **[official via secondary; get legal advice]**

## Contradictions flagged
1. Forum/UGC direction in 2026 core updates. 2. INP 150 ms / LCP 2.0 s claims vs unchanged official thresholds. 3. Schema and AI citations: Ahrefs controlled test (no lift) vs vendor "60%+ lift" claims. 4. Length: Ahrefs (no relation, AIO) vs SE Ranking (longer wins, ChatGPT). 5. ADA lawsuit counts (federal only vs with state filings).

## Claims to verify against primary pages
- Current wording of the helpful-content page (1 Oct 2026 revision), including the fake-author paragraph.
- FAQ removal dates (7 May, June, August 2026) on the FAQPage doc and updates log.
- The May 2026 AI guide's local-business section.
- Whether site reputation abuse enforcement went algorithmic in 2026.
- Bing AI Performance report launch date and scope.
- GoHighLevel and Kajabi sitemap and author-page capability in 2026.
- Seyfarth 2025 and H1 2026 counts from the firm's own report.

## Sources
- Google, AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Google, Guide to optimizing for generative AI features (May 2026): https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google blog, A new resource for optimizing for generative AI (May 2026): https://developers.google.com/search/blog/2026/05/a-new-resource-for-optimizing
- Google blog, Succeeding in AI search (May 2025): https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search
- Google, Creating helpful, reliable, people-first content: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google, Guidance about AI-generated content (Feb 2023): https://developers.google.com/search/blog/2023/02/google-search-and-ai-content
- Google, Documentation updates log: https://developers.google.com/search/updates
- Google, Core updates doc: https://developers.google.com/search/docs/appearance/core-updates
- Google, Byline dates: https://developers.google.com/search/docs/appearance/publication-dates
- Google, Review snippet: https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- Google, LocalBusiness: https://developers.google.com/search/docs/appearance/structured-data/local-business
- Google, Organization: https://developers.google.com/search/docs/appearance/structured-data/organization
- Google, FAQPage: https://developers.google.com/search/docs/appearance/structured-data/faqpage
- Google blog, Making review rich results more helpful (2019): https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful
- ppc.land, fake author profiles (Oct 2026): https://ppc.land/google-says-fake-author-profiles-signal-a-low-quality-page/
- relevantaudience.com, helpful content update: https://www.relevantaudience.com/seo/google-helpful-content-main-content-effort-originality-fake-authors/
- Search Engine Land, smaller unannounced core updates (Dec 2025): https://searchengineland.com/google-confirms-it-releases-smaller-core-updates-it-does-not-announce-465947
- GSQi, December 2025 core update analysis: https://www.gsqi.com/marketing-blog/google-december-2025-broad-core-update-analysis-findings/
- SERoundtable, September 2026 spam update done: https://www.seroundtable.com/google-september-2026-spam-update-done-42235.html
- SERoundtable, August 2026 spam update done: https://www.seroundtable.com/google-august-2026-spam-update-done-41906.html
- SERoundtable, June 2026 spam update done: https://www.seroundtable.com/google-june-2026-spam-update-done-41580.html
- SEJ, Google algorithm history: https://www.searchenginejournal.com/google-algorithm-history/
- Search Engine Land, site reputation abuse first-party clarification: https://searchengineland.com/?p=448432
- SERoundtable, site reputation abuse not algorithmic yet: https://www.seroundtable.com/google-site-reputation-abuse-policy-not-algorithmic-yet-37443.html
- seo-kreativ.de, March 2026 spam update: https://www.seo-kreativ.de/en/blog/google-march-2026-spam-update/
- Dynadot, expired domains after 2026 spam update: https://www.dynadot.com/blog/expired-domains-google-spam-update
- SEJ, Google drops FAQ rich results (May 2026): https://www.searchenginejournal.com/google-drops-faq-rich-results/574429/
- relevantaudience.com, structured data removals: https://www.relevantaudience.com/seo/google-removes-structured-data-2025-guide-for-websites/
- Ahrefs, schema and AI citations (May 2026): https://ahrefs.com/blog/schema-ai-citations/
- Ahrefs, 38% of AIO citations from top 10: https://ahrefs.com/blog/ai-overview-citations-top-10/
- Ahrefs, how to rank in AI Overviews: https://ahrefs.com/blog/how-to-rank-in-ai-overviews/
- Ahrefs, short vs long content in AIO: https://ahrefs.com/blog/short-vs-long-content-in-ai-overviews/
- Ahrefs, fresher content study (Jul 2025): https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/
- Ahrefs, AIO cites AI-generated content: https://ahrefs.com/blog/ai-overviews-cite-ai-generated-content-more-than-human-writing/
- Ground News / Search Engine Land on Wix Studio AI Search Lab study (Mar 2026): https://ground.news/article/ai-citations-favor-listicles-articles-product-pages-study-search-engine-land
- INSIDEA, which pages AI answers cite (Oct 2026): https://insidea.com/blog/seo/aeo/what-ai-answers-cite-study
- Geeky Tech, AI citation study 2026: https://www.geekytech.co.uk/resources-tools/ai-citation-study-2026/
- Passionfruit, citation rate by content length: https://www.getpassionfruit.com/blog/ai-citation-rate-by-content-length-does-longer-content-get-cited-more
- Digital Applied, 1,000 AI Overviews study: https://www.digitalapplied.com/blog/we-analyzed-1000-ai-overviews-citation-pattern-study
- Everything-PR, six 2026 citation studies: https://everything-pr.com/how-ai-engines-cite-the-web-the-six-studies-that-define-the-2026-evidence-base
- Semrush on Google's generative AI guide: https://www.semrush.com/blog/google-publishes-generative-ai-search-guide/
- metadigital.co.nz, Core Web Vitals 2026: https://www.metadigital.co.nz/core-web-vitals-in-2026-what-they-measure-and-whats-actually-worth-fixing/
- eseospace, Core Web Vitals in 2026: https://eseospace.com/blog/core-web-vitals-in-2026-what-changed-what-still-matters-and-how-to-pass/
- Ahrefs, discovered currently not indexed: https://ahrefs.com/blog/discovered-currently-not-indexed/
- SERoundtable, new Search Console features delayed (Feb 2026): https://www.seroundtable.com/new-google-search-console-features-delayed-40924.html
- Lilach Bullock, Bing Webmaster Tools AI Performance report: https://www.lilachbullock.com/bing-webmaster-tools/
- eseospace, Bing Webmaster Tools and IndexNow: https://eseospace.com/blog/bing-webmaster-tools-indexnow-ai-search/
- Wikipedia, IndexNow: https://en.wikipedia.org/wiki/IndexNow
- Wix, SEO guide: https://www.wix.com/seo/learn/wix-seo-guide
- jsonschemaapp, Wix schema guide: https://jsonschemaapp.com/blog/how-to-add-wix-schema-markup-to-improve-seo-and-ai-understanding/
- martalebre.com, Squarespace schema: https://martalebre.com/blog/squarespace-schema-markup
- GoHighLevel, technical SEO guide: https://www.gohighlevel.com/post/a-practical-guide-to-technical-seo-for-gohighlevel-websites
- e2msolutions, GoHighLevel technical SEO gaps: https://www.e2msolutions.com/blog/technical-seo-gohighlevel/
- Kajabi docs, add custom code to pages: https://docs.kajabi.com/articles/website/pages/add-custom-code-to-pages
- Kajabi help, block AI bots: https://help.kajabi.com/hc/en-us/articles/360037001614
- AIOSEO, E-E-A-T for WordPress: https://aioseo.com/eeat-seo/
- Level Access, web accessibility lawsuits trends: https://www.levelaccess.com/blog/2024-u-s-web-accessibility-litigation-key-trends-and-strategies-for-mitigating-risk/
- web-accessibility-checker.com, lawsuit statistics 2026: https://web-accessibility-checker.com/en/blog/accessibility-lawsuits-statistics-2026
- CompliaScan, ADA website lawsuits 2026: https://compliascan.com/blog/ada-website-lawsuits-2026
- TestParty, WCAG 2.2 for US companies 2026: https://testparty.ai/blog/wcag-2-2-us-companies-2026
- dev.to, WCAG 2.2 nine new criteria: https://dev.to/accesscheck/wcag-22-the-9-new-success-criteria-explained-with-real-examples-549f
- Plante Moran, DOJ extends Title II deadlines (Apr 2026): https://plantemoran.com/explore-our-thinking/insight/2026/04/doj-extends-ada-title-ii-web-accessibility-compliance-deadlines
- Duane Morris, DOJ extension alert: https://www.duanemorris.com/alerts/doj_extends_ada_title_ii_digital_accessibility_deadlines_one_year_0426.html
- EqualWeb, WCAG 2.2 and EAA: https://www.equalweb.com/platform/standards/wcag-2-2.html
