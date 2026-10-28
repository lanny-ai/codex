# Be the business the answer names: a complete profile first, one honest page a week second, and other people's lists third

Research report for the Build Room Search & Answer Engine, 2026-10-28. Sources: five research notes in `research_notes/Search and Answer Engine/` (answer engines and crawlers; Google guidance and page patterns; Google Business Profile and local; world-class playbooks and benchmarks; rules, platforms and tools) and the founder's own OS Cortex AEO Publisher, read from this repository.

## No web page was read in full, and the strongest numbers are vendor numbers

The research environment could not open any web page: direct fetches failed on DNS for every host tried. Every claim below rests on **search-engine extracts** of the source, including Google's own documentation, the FTC's rule and the ranking-factor survey. Where two extracts disagree, both figures are given and the claim is listed at the end for checking before anyone quotes it.

Three more limits matter.

- **Nearly every citation study is run by a company that sells visibility tools.** Ahrefs, Semrush, BrightLocal, Steady Demand, Seer, Profound, Yext, Local Falcon and the rest use different prompt panels, time windows and denominators. The direction of their findings agrees far more than the numbers do. Only three sources here are independent: Pew Research, the Agarwal and Sen randomised experiment, and the BrightLocal consumer survey (a survey of buyers, not of tool data).
- **No source measures a one-owner service business over time.** Case studies with hard numbers (a roofer, a clinic, an electrician) are agency claims without baselines.
- **The answer engines move monthly.** Four of the things older guides still recommend were switched off in the last year: Business Profile Q&A (December 2025), FAQ rich results (May 2026), the one-to-one text-consent rule (vacated January 2025) and Apple Business Connect (replaced April 2026). Anything in this report dated before November 2025 should be re-checked before it is taught.

Strength is tagged in words: **official** (a platform's or regulator's own page, via extract), **independent** (a study by someone not selling the thing measured), **vendor** (a tool company's own data), **practitioner** (an agency's test or opinion), **founder's own** (the OS Cortex method), **folklore** (repeated everywhere, sourced nowhere).

## For a buyer aged 55 to 75, Google and YouTube still decide, and the Business Profile is where Google's AI looks first

Three findings set the order of work for this audience, and they point the same way.

**The buyers are on Google and YouTube, not yet in ChatGPT.** Pew (February 2026): 77% of Americans 65 and over, and 58% of those 50 to 64, have never used a chatbot; 86% of adults 50 to 64 use YouTube, and a majority of those over 65 do [independent]. ChatGPT use is rising in every age band, so the engines are not ignored here, but the first dollar of effort goes where this buyer already is.

**On Google's AI surfaces, local answers cite the Business Profile before the website.** Steady Demand's August 2026 snapshot of 7,990 local-service searches: AI Mode sent about 80% of its local citations to Google Maps and Business Profile pages and about 20% to business websites; AI Overviews sent about 73% to the business's own site [vendor, one agency, one snapshot]. BrightLocal's 200,000-search study puts the Business Profile at 28.5% of all AI citations and dominant on Google's surfaces, with Yelp dominant in ChatGPT's local answers, where the Business Profile does not appear at all [vendor]. The practical reading is not in dispute between them: for Google's AI, a complete and accurate profile is the first citation target; the website is the main source for AI Overviews and for every non-Google engine.

**Reviews are now a ranking input and the buyer's filter.** The 2026 Local Search Ranking Factors survey (47 practitioners, 187 factors, published November 2025) puts the primary category, proximity and the real business name at the top of the local pack, with hours ("open now") a new entry at number five and review signals risen to about a fifth of pack weight, while citations fell to about 6 to 7% [practitioner survey, figures from secondary summaries]. On the buyer's side, BrightLocal's February 2026 survey of 1,002 US adults: 31% will only use a business rated 4.5 or higher (17% a year earlier), 47% skip a business with fewer than 20 reviews, 74% want a review from the last three months, and 80% favour a business that replies to every review, though half are put off by a templated reply [independent survey].

Add one more: **third-party corroboration beats the business's own words in AI answers.** The same ranking-factor survey's new AI-visibility column rates being in expert-curated lists, a strong presence on review and directory sites, and unstructured mentions highest; a dedicated page per service ranked first for local organic and second for AI visibility [practitioner survey]. Ahrefs' correlation across 75,000 brands: branded web mentions correlate about 0.66 with AI visibility, backlinks about 0.22 [vendor, correlation]. For "best X" lists in professional services, neutral third-party lists took about 81% of citations and self-published ones about 19% (Wix Studio, 75,000 answers) [vendor].

So the order for a Build Room member is: (1) the Google Business Profile, complete and reviewed; (2) one page per service and one honest answer page a week on the member's own site; (3) the free listings the engines actually read, and one new third-party mention a month; (4) one long-form YouTube answer video every few weeks for Google's AI surfaces; and only then (5) anything aimed at ChatGPT specifically.

## What Google itself says: it is still SEO, and there is nothing special to add

Google's "AI features and your website" page and its May 2026 guide to optimising for generative AI features say the same thing in several ways: there are no additional requirements to appear in AI Overviews or AI Mode, no special files (Search ignores llms.txt), no special markup, no need to break content into small pieces; a page must be indexed and eligible for a snippet; build unique, non-commodity content that a model could not easily produce; "it is still SEO" [official, via extracts; one date conflict, 15 May or 15 June]. The helpful-content page, revised October 2026, defines main content, names effort, originality, skill and accuracy as what raters assess, warns that fabricated author profiles signal a low-quality page, and strongly encourages accurate bylines [official via trade press; wording to verify].

Two things that older advice still pushes have been measured and found empty.

- **Structured data does not earn AI citations.** Ahrefs' controlled test (May 2026; 1,885 pages that added JSON-LD against about 4,000 controls) found no change in AI Mode or ChatGPT citations and a small, statistically significant 4.6% fall in AI Overview citations; a companion test found AI retrieval reads the visible HTML and ignores JSON-LD [vendor, controlled]. Google says structured data is not required for AI features [official]. FAQ rich results stopped for everyone on 7 May 2026; HowTo went in 2023; self-serving star markup has not shown stars since 2019 [official]. What remains worth a few minutes: Organization, LocalBusiness with address and hours, a Person entry for the author, Article with dates, and breadcrumbs, because they help Google understand who the business is. Nothing more.
- **llms.txt is ignored.** Google says Search does not use it; no other engine confirms reading it; in one study 97% of such files got zero AI-crawler requests in a month [official plus independent].

What Google's own extracts and the citation studies do support, taken together:

| Practice | Evidence | Strength |
|---|---|---|
| Answer in the first lines | 44% of verified ChatGPT citations came from the first 30% of the page (18,012 citations); Google asks for the answer up front | practitioner data; official (general) |
| One page per service, each written for a real question | Ranked first for local organic and second for AI visibility in the 2026 survey | practitioner survey |
| State the number on cost and time questions | For "how much" and "how long" questions, cited pages stated a figure outright (INSIDEA, 2,667 answers, small sample) | vendor, small |
| Keep pages updated, not re-dated | 75% of cited pages were updated within a year and over a quarter were first published two or more years ago (Seer, 47,097 citations); Google warns against changing dates without substantive change | vendor; official |
| Short sections under question-shaped headings, with a list or table | Recommended everywhere; vendor multipliers unverified; a six-model experiment found relevance dominates and formatting adds little once relevance is equal | practitioner |
| A named author with real credentials and an About page | Google's self-assessment questions; the fake-author warning | official |
| Length to the question, not a word count | Spearman about 0.04 between length and AI Overview citations (Ahrefs); longer helped ChatGPT (SE Ranking) | vendor, conflicting |
| Cover the topic as a cluster | Only 38% of AI Overview citations now come from the top 10 organic results (Ahrefs, March 2026; BrightEdge says 17%) | vendor |

The skill's answer-page standard follows this: question as the H1, the direct answer in the first 100 words, question-shaped H2s, one list or table, a dated "Updated" line, a named author with credentials, the member's own view in a section of its own, sources listed, and no structured data beyond the five basic types.

## The founder's method transfers almost whole: evidence first, original utility, a gate before anything publishes

The OS Cortex AEO Publisher (the founder's governed publishing system for ChatGPT desktop and Codex, merged to this repository in September 2026) rests on four principles: AEO is a system, not a content trick; evidence first, with a citation ledger for every factual claim; original utility on every page (first-hand expertise, a framework, data or an example no competing page has); and nothing publishes after a failed gate [founder's own]. Its gates are at least three authoritative sources, the direct answer inside the first 100 words, a documented original contribution, no invented stories, testimonials, credentials or statistics, and a scope note whenever a topic approaches medical, legal, financial or mental-health advice. Its question scoring weights demand 25%, business relevance 25%, citation gap 20%, evidence 20% and freshness 10%, and the first three pages are published by hand in a fixed order: a definition, a how-to, then a comparison or objection.

Everything in that list survives contact with the 2026 research. The research adds what the OS Cortex material did not cover: the Business Profile, reviews, listings, YouTube, the website builders a non-technical owner actually uses, and the rules for regulated professions. Two things change in the port. The daily cadence becomes weekly, because a solo owner aged 55 to 75 can give two to five hours a week, not an unattended daily run. And developer-API measurement becomes a manual monthly check in the free consumer apps, because that is what the member can do and what the buyer sees.

One founder rule gets a second source. OS Cortex requires three outside sources on every page. The research shows that first-hand pages (the member's own prices, their own counted results, their own method) are what AI answers cite for cost and "what is typical" questions, and that Google rewards experience. So the skill has two page kinds: an **evidence** page (three or more outside sources) and a **first-hand** page (the member's own data, with a "How we know" section saying what was counted, and at least one outside source). Both carry a claim ledger.

## The Business Profile: category and real name first, then reviews, then the things that convert

The 2026 survey and the controlled tests agree on a split that most guides blur: some profile work moves rank, most of it moves conversion, and the two should be done in that order.

**Moves rank:** the primary category (the strongest factor the owner controls); the real-world name, nothing added (keyword-stuffed names hold two to five times more top-three positions in Whitespark's own correlation, and are the top suspension cause; the correlation is not permission) [vendor correlation; official policy]; hours and holiday hours ("open now" is now a filter and an input); the address or, for a service-area business, the hidden address and a true service area; and reviews, by rating, count and recency.

**Moves conversion, not rank:** photos and posts. Sterling Sky's controlled tests found no pack movement from photos or from nine weeks of weekly posts (441 keywords); the average post is seen fewer than 20 times in its seven-day life [practitioner tests]. They still matter: a profile with real photos of the owner, the team and the work, and a recent post, looks open and real to a buyer deciding whom to call. Google's own suggested cadence is one post a week [official via secondary]. The skill asks for one real photo every two weeks and one post every one to two weeks, and says plainly that these are for the buyer, not the ranking.

**Eligibility is the first question, not the last.** A profile is for businesses that meet customers in person: at the business's own place, or at the customer's (a service-area business, address hidden). A virtual office, a PO box, a coworking desk without signage and reception, or a fully remote coach or consultant is not eligible, and such profiles were a large share of 2026 suspensions [official via explainers; a suspension wave in April 2026 is reported by agencies selling reinstatement and is unverified]. The skill asks the eligibility question before anything else and routes a remote business to listings and answer pages instead.

**What Google removed and added in the last year** [official via corroborated reports]: Q&A is gone (API 3 November 2025, public section from 3 December 2025); messaging and call history ended in July 2024; AI review summaries appear on listings; social links are auto-added; Gemini "Ask Maps" launched 12 March 2026 and answers from profile fields, website content and reviews, with no way for an owner to write its answers. The replacement for Q&A seeding is complete services on the profile and the answer pages on the website, which Ask Maps draws on. Video verification is now the usual route.

**Reviews: a steady habit, never a burst.** Google's Maps blog (16 April 2026) says it now pauses new reviews on a profile during a spam spike and shows a warning banner; in July 2026 it confirmed pausing reviews on affected profiles while investigating disappearing reviews [official]. So the review loop is a few asks a week, every week, the same way for every client, the same day the work finishes, with one reminder a few days later. Top-three benchmarks vary wildly by category and study (medians from about 20 reviews for home health care to about 350 for dentists at 4.8 to 4.9 stars in Local Falcon's 50 million results; BrightLocal's older mixed sample averaged 47 at 4.47) [vendor, contradictory]. The usable rule: benchmark against the lowest-review business that sits consistently in the top three for the member's own town and category.

## Reviews are now a federal matter, and Google is stricter than the law

The FTC's Consumer Reviews and Testimonials Rule (16 CFR 465) has been in force since 21 October 2024 and is being enforced: warning letters went out in December 2025 and at least two cases cited the rule by July 2026; the civil penalty is reported at about $53,000 per violation [official via law-firm summaries; the exact figure to verify]. It bans fake or AI-written reviews, incentives conditioned on sentiment, undisclosed insider reviews (owner, staff, family), company-run review sites posing as independent, review suppression (legal threats, or showing only the good ones while claiming to show all) and fake social indicators. "Gating" (asking only the customers expected to be happy, or routing unhappy ones to a private form) is treated as suppression and is a plain breach of Google's policy, which also bans **any** incentive for a review, positive or negative, and (per 2026 vendor reports of policy additions) staff quotas and asking customers to name an employee [official policy; additions vendor-reported].

The skill's review rules therefore are: ask everyone, the same way; never offer anything for a review; never write a review for a client; never ask staff or family without disclosure; reply to every review in the member's own words within a week; flag fake reviews through the profile's tool, then the appeal, then the community forum; never threaten a reviewer. Email asks fall under CAN-SPAM (address and opt-out); text asks still need prior written consent despite the vacated one-to-one rule, so consent is collected at booking and texts go in business hours [official via practitioner].

**Regulated professions carry their own limits, and the skill names them** (a summary, not legal advice; the member checks their regulator):

- **Financial advisers (SEC Marketing Rule).** Testimonials and endorsements only with clear, prominent, non-hyperlinked disclosures of client status, compensation and conflicts; the SEC's December 2025 risk alert named online reviews and buried disclosures as recurring failures [official via counsel]. Showing Google reviews on the website needs compliance sign-off.
- **Lawyers.** No "specialist" or "certified" without the named certification; no "best" (Texas); past-results disclaimers; some states require pre-filing of ads (Florida, Texas) [official rule text via counsel].
- **Medical, dental, HIPAA-covered.** Never confirm a reviewer is a patient or mention treatment in a reply, even if the patient said it first (OCR settlements of $10,000 and $50,000) [official enforcement].
- **Therapists and counsellors.** APA 5.05 and ACA C.3.b bar soliciting testimonials from current (APA) and former (ACA) clients: no review asks to clients at all; credential pages and colleague endorsements instead [professional codes].
- **Real estate.** Fair-housing language rules apply to every page and post: describe the property, never the occupant [official via practitioner].
- **Insurance.** Testimonials must be genuine, current and applicable to the policy; no payout or "lowest rate" claims; some states require disclosure of paid spokespeople [state orders].

And for everyone writing on a health, legal or money topic: a visible scope note (general information for residents of a named state, not advice, no client relationship formed), the author's credentials and licence, a reviewer line, and a reviewed-on date. Google's raters put trust first on these topics; nothing official says the note itself ranks, and nothing in the research suggests leaving it out.

No US law requires a small business to label AI-assisted web copy: Colorado's act was repealed and replaced (narrower, effective 2027, aimed at automated decisions), Utah's duty is about AI interacting with consumers, and California's SB 942 binds AI providers [official via counsel]. YouTube does require disclosure of realistic synthetic content and auto-labels it since May 2026 [official]. The honesty rules apply regardless: the FTC's Section 5 actions against AI claims continued through 2026 (Air AI, Cox Media) [official via counsel].

## Where to be listed: five free listings, then stop

Citations now weigh about 6 to 7% of local pack rank and citation consistency sits 28th among factors; the practitioner consensus is "maintenance, not strategy" [practitioner survey]. For AI answers they matter more, because the engines read directories: in home-services tests ChatGPT cited BBB in 39% of answers and licensing sites in 25%; Yelp data appeared in the grounding of 96% of ChatGPT local runs in one August 2026 test, though another found Yelp in only 0.6% of citations [vendor, contradictory]. Yelp licensed its reviews, photos and business details to OpenAI in July 2026 (non-exclusive; Yelp data already feeds Apple Maps, Alexa and Bing) [official via Yelp's SEC filing], which makes a complete, reviewed Yelp page an AI asset for a US local service business.

The free listings worth an owner's time, in order: Google Business Profile; Bing Places (feeds Copilot; imports from Google); Apple Business (launched 14 April 2026, free, replacing Apple Business Connect; feeds Apple Maps and Siri); Yelp; the Facebook page; then Nextdoor, the Better Business Bureau, the chamber of commerce, and one or two industry directories (Angi or Expertise for trades; Healthgrades-type for clinics; the state bar or professional body for advisers) [official for Apple and Bing; practitioner for the list]. Name, address and phone identical everywhere; paying a data aggregator is not supported by any 2026 evidence [vendor opinion].

For a fully remote coach or consultant there is no profile to build. LinkedIn is the most-cited domain for professional questions across engines; named individuals and single-niche positioning predict citation in advisory categories; only 4% of 1,700 B2B firms were cited for any vertical they claimed [vendor, methods unclear]. The play is the LinkedIn Engine, a strong personal site with one page per service, professional-body directories, and other people's lists.

## YouTube is a search engine for this audience, and Google's AI quotes it

Google's AI surfaces cite YouTube heavily, ChatGPT almost never: 36% of Google AI answers versus 2.1% of ChatGPT's in one 83,835-citation study, with other studies putting YouTube's share of AI Overview citations anywhere from 4.7% to 23% by metric [vendor, wide range]. Relevance to the question, not view count, predicts whether a video is cited (near-zero correlation with views); long-form is about 94% of citations; Google's AI Overviews deep-link to a timestamp in roughly half of their YouTube citations, so chapters behave like sub-headings [vendor]. Shorts skew young (viewers over 55 are about 15% of Shorts viewers) [vendor].

The skill's YouTube rule is simple and hands production to the Video Director: one long-form answer video (five to twelve minutes) every two to four weeks; the title is the customer's question; the answer in the first 30 seconds; chapters named as sub-questions; a corrected transcript; the description repeats the question, the answer and a link to the matching answer page.

## Measuring: two free reports and a two-hour manual check a month

Google Search Console's generative-AI report (announced 3 June 2026, global by September) shows impressions where the site appeared in AI Overviews or AI Mode, combined, with no clicks, queries or positions; it comes with a toggle to opt out of AI features, which a business that wants customers should leave off [official]. Bing Webmaster Tools' AI Performance report (February 2026, extended June 2026) shows citations in Copilot and Bing AI with the grounding queries, intents, topics and citation share, free for a verified site, and is the richer of the two [official via secondary]. IndexNow speeds Bing indexing and therefore Copilot; its benefit to ChatGPT is inferred, not confirmed by OpenAI [practitioner]. In GA4, AI referrals appear by referrer, with a native "AI Assistant" channel since 13 May 2026; about 70% of AI-sourced visits arrive with no referrer and land in Direct [vendor; GA4 change official].

None of that tells a member whether the buyer's own question finds them. The practitioner synthesis, which the skill adopts: 10 to 15 customer-style prompts (never the business name alone), two wordings each, run logged out on Google's AI, ChatGPT, Perplexity, Gemini and Copilot, two or three times over different days, because the same business reappears only 40 to 50% of the time (Steady Demand's "grounding drift"; BrightLocal's re-run test); log who was cited, including competitors; add two brand prompts to catch wrong facts (in one small audit only 5 of 18 brand queries returned correct, current details). About two hours a month, and the trend over three months is the signal, not one month's number. The founder's 25-question, two-paraphrase baseline is the same idea at agency scale.

Paid trackers start at about $29 a month (Otterly Lite, 15 prompts) and run to several hundred; free one-off graders exist from Semrush, Ahrefs, HubSpot and Mangools [vendor pricing, to verify]. None is required.

## What to expect, and what counts as a result

Expectations have to be honest, because the numbers that get quoted are the dramatic ones.

- **AI answers cut clicks.** The randomised field experiment (Agarwal and Sen, January to February 2026, about 1,065 US desktop users; not yet peer reviewed) found AI Overviews cut organic clicks by 38 to 40% on the queries that trigger them; Ahrefs measured a 58% fall at position one over two years; Seer saw organic click-through on AI-Overview queries fall to 1.3% in December 2025 and recover to about 2.4% by February 2026, with brands cited inside the overview getting about 35% more clicks [independent; vendor]. About 68% of US Google searches ended without a click in early 2026 (SparkToro and Similarweb, partly a panel change) [vendor and independent-ish].
- **AI referrals are small and good.** Around 1 to 4% of visits; small-business sites' AI share rose from 0.4% to 1.7% in 19 months, the fastest of any vertical (Previsible, 166 GA4 properties); ChatGPT is 92% of standalone-assistant referrals; AI visits convert better than organic in most datasets, by anything from 1.2 to 20 times [vendor].
- **Time to be seen.** A new page can be cited in ChatGPT or Perplexity within one to two weeks if Bing has indexed it (medians of 4 to 11 days in vendor studies); profile changes show in four to eight weeks; classic ranking timelines of three to six months are folklore, repeated without data [vendor; folklore].

So the results the skill counts are the ones that reach the bank: calls and direction requests from the profile, booked calls and form fills attributed by asking "how did you find us", Search Console clicks on the answer pages and the AI-impressions line, Bing citations, and the monthly share of customer prompts where the business is named. Not traffic, not rankings.

## The weekly routine a 55 to 75-year-old owner can keep

DIY guides converge on two to five hours a week; the Business Profile alone takes 30 to 60 minutes [practitioner]. The skill's routine, built for about two and a half hours:

1. **Reviews and the profile, 30 minutes:** reply to any open review; ask two to four recent clients, one at a time; one real photo; one post; check hours and the booking link.
2. **One honest page, about ninety minutes to two hours:** the next question from the map, written by the member with the skill, through the gate, published on the builder, submitted to both consoles.
3. **One mention, 20 minutes:** one email to a local roundup, chamber, association, podcast or directory that lists businesses like theirs.
4. **Monthly, two hours more:** the citation check; refresh one page sitting at Search Console positions 5 to 20; confirm the five listings; prune or merge a page with no clicks after a year.

The anti-patterns that got sites and profiles hit in 2025 and 2026, which the skill refuses to build: templated city pages where only the place name changes; doorway pages; pages produced at volume for rankings (Google ran four spam updates in 2026 enforcing scaled-content and expired-domain abuse, and its own head of Search called it "AI slop") [official]; keyword-stuffed profile names; review gating, incentives or bursts; fake author profiles; self-serving star markup expecting stars; any claim about a result without what is typical beside it.

## Claims to verify before anyone quotes them

| Claim | Why |
|---|---|
| Share of searches showing an AI Overview | 13% to 88% depending on the panel; say "about a fifth of real-user searches, roughly half of commercial samples" and name the panel |
| Top-10 overlap of AI Overview citations | 38% (Ahrefs) vs 17% (BrightEdge) |
| Whitespark 2026 weights | GBP about 32%, reviews about 20%, citations 6 to 7%: all from secondary summaries |
| Top-three review benchmarks | Local Falcon medians 20 to 346 at 4.8 to 4.9 vs BrightLocal 47 at 4.47 |
| Yelp in ChatGPT local answers | 95.8% of grounding (Steady Demand) vs 0.6% of citations (home-services study) |
| YouTube share of AI Overview citations | 4.7% to 36% by metric |
| Bing's share of ChatGPT citations | 87% vs 27% |
| FTC penalty per violation | $51,700 to $53,088 in counsel summaries |
| April 2026 Google review-policy additions (staff quotas, employee names) and the suspension wave | Vendor and agency reports only; no Google announcement found |
| Date of Google's generative-AI guide | 15 May or 15 June 2026 |
| Helpful-content page revision, 1 October 2026 | Wording of the fake-author paragraph seen only in trade press |
| Cloudflare's September 2026 default-block scope | New domains only vs all free-tier sites |
| GoHighLevel robots.txt and sitemap controls; Google Sites reading embedded JSON-LD | Not confirmed by the platforms |
| AlsoAsked, AnswerThePublic, Ubersuggest free limits | 3 a day most reported; contested |
| ACA code revision (September 2026) numbering; FINRA 2210 testimonial wording | Professional-body pages not read |
| Apple Business launch date (14 April 2026) and auto-migration | One vendor source |

## What this means for the skill

1. Phase 0 asks eligibility and the regulated-profession question before anything else, and reads §1, §2, §3, §4, §14, §18 and §19, plus the proof bank.
2. The profile comes first for any business that meets customers in person; the website's one-page-per-service and the answer pages come second; listings third; YouTube fourth; ChatGPT-specific work last.
3. The answer-page gate ports the founder's gates and adds the typical-result rule, the never-say list, a scope note for regulated topics and two page kinds.
4. Reviews follow Google's policy (stricter than the FTC's) and the professional codes, with the therapists' ban on client solicitation built in; consented quotes hand to the Proof Engine.
5. Structured data is limited to five types and described as optional; llms.txt, FAQ schema, Q&A seeding and star markup are named as retired so members stop reading old advice.
6. Measurement is the two free reports plus the monthly manual check; results are counted in calls, bookings and "how did you find us", never in traffic alone.
7. Every number in the references carries its strength tag, and the list above travels with the skill as "unverified until checked live".
