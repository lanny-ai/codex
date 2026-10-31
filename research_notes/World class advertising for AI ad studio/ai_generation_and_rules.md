# AI-Generated Ad Creative in 2026: Tools, Quality, Consumer Response, Disclosure and Rights

Research date: 2026-10-14. Method: about 25 web searches. Direct page fetches failed for several primary domains (higgsfield.ai and paulweiss.com returned DNS errors in this environment), so many findings come from search-result summaries of the cited pages. Each finding carries a date and is labelled SHIPPED, ANNOUNCED, VENDOR CLAIM or SECONDARY (third-party blog, unverified) where that applies. Most sources on model quality and pricing are vendor-adjacent SEO blogs, so treat them as indicative only.

## 1. Generation models and platforms for ads (Higgsfield, Veo, Nano Banana, Seedance/Seedream, Kling, Runway, Sora, gpt-image, Midjourney)

### Takeaway
As of October 2026 no single video model wins on everything. Veo 3.1 is the most-cited choice for dialogue lip sync and native audio. Seedance 2.0/2.5 leads on multi-reference control and long single shots. Kling 3.0 is the value and length choice. For images, Nano Banana Pro is the usual pick for in-image text, and Seedream 4.5/5 is the cheaper option. Sora 2 is gone: the app closed April 2026 and the API was switched off September 24, 2026, so it should not be built on. Higgsfield is now a large aggregator ($5.4B valuation reported August 2026) with a hosted MCP server, a CLI that it recommends for Claude Code and Codex, and a pay-per-generation API reported launched September 17, 2026. That makes it a reasonable hub, but its credit pricing changes often and its model roster differs from source to source.

### Cited Findings
**Higgsfield (the hub)**
- What it is: a multi-model AI image and video platform. It reportedly raised $80M in January 2026 (an extension to its Series A) at a valuation above $1.3B, then a $400M Series B in August 2026 at a $5.4B valuation (Goldman Sachs, Intel, DST Global), announcing $700M in annualized revenue. Reported via Reuters and TechCrunch; numbers taken from secondary summaries — [Yahoo Finance](https://finance.yahoo.com/technology/ai/articles/higgsfield-hits-5-4-billion-061508226.html); [Wikipedia](https://en.wikipedia.org/wiki/Higgsfield_AI)
- Higgsfield reportedly told Bloomberg in September 2026 that its run rate had passed $1B. SECONDARY, unverified — [Okara blog](https://okara.ai/blog/how-higgsfield-grew). Total-funding figures conflict: GetLatka says about $188M and Tracxn says $538M — [GetLatka](https://getlatka.com/companies/higgsfield.ai); [Tracxn](https://tracxn.com/d/companies/higgsfield/__HOGu4TInAP4ifiKkUkJ2LqOJJnDsgiF12TQdX5qsv9Q/funding-and-investors)
- MCP server (SHIPPED, 2026): hosted at `https://mcp.higgsfield.ai/mcp`. Sign-in is by browser OAuth, with no API key. Setup example: `claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp`. Generations through MCP always deduct credits, even on plans marketed as "Unlimited" — [Creetr](https://creetr.com/blog/higgsfield-mcp); [techsy.io](https://techsy.io/en/blog/higgsfield-mcp-claude-code)
- One write-up describes the MCP tool surface as five tools (generate_image, generate_video, create_character, get_generation_status, list_characters) across seven models. Others list 30+ models, so the roster exposed through MCP may differ by date or plan — [Creetr](https://creetr.com/blog/higgsfield-mcp); [aituber.app](https://aituber.app/blog/higgsfield-mcp-video-generation/)
- CLI: Higgsfield's own CLI page reportedly recommends its CLI over the MCP connector for Claude Code and Codex users. Third-party guides say the CLI with long-lived API tokens suits automated pipelines better — [Higgsfield CLI](https://higgsfield.ai/cli); [claudefa.st](https://claudefa.st/blog/tools/mcp-extensions/higgsfield-mcp)
- Public API: reportedly launched September 17, 2026, pay as you go with no subscription. Listed rates: Seedance 2.5 $0.2057/s, Seedance 2.0 $0.1407/s, Kling 3.0 $0.084/s, Wan 3.0 $0.05/s. SECONDARY, needs checking against Higgsfield's pricing page — [Higgsfield API blog](https://higgsfield.ai/blog/higgsfield-api); [Layer3 Labs](https://www.layer3labs.io/guides/higgsfield-api)
- Hosted models (sources differ): Nano Banana Pro, Soul / Soul 2.0 (Higgsfield's own photoreal model), GPT Image 2, Seedream 4.x, FLUX, Reve, Kling O1, Veo 3.1, Kling 3.0/2.6/2.5 Turbo, Seedance 2.0, Wan 2.7, MiniMax Hailuo 02, and Sora 2 on older lists, which is now stale because Sora was shut down — [Creetr](https://creetr.com/blog/higgsfield-mcp); [claudefa.st](https://claudefa.st/blog/tools/mcp-extensions/higgsfield-mcp)
- Subscription credit pricing conflicts between sources:
  - Starter $19/270 credits, Plus $59 ($47 billed annually)/1,200, Ultra $129 ($99 billed annually)/3,000 — [Blotato](https://www.blotato.com/blog/higgsfield-pricing); [Krea](https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs)
  - Alternatively $15/200, $49/1,000, $129/3,000 — [Layer3 Labs](https://www.layer3labs.io/guides/higgsfield-api)
  - Starter reportedly includes only Seedance Fast and Mini. Seedance 2.0/2.5 need a higher tier — [Wireflow](https://www.wireflow.ai/blog/higgsfield-ai-pricing)
- Indicative credit costs per clip: Seedance 2.0 5s 720p ≈ 22 credits; Kling 3.0 720p ≈ 7 credits; Veo 3.1 Fast 4s ≈ 16 credits; Veo 3.1 4s ≈ 40 credits — [Wireflow](https://www.wireflow.ai/blog/higgsfield-ai-pricing)
- Free tier: one source says 150 credits/month (as of May 2026), and another says MCP needs an active paid plan. The two conflict — [miracamp](https://www.miracamp.com/learn/content-creation/claude-x-higgsfield-mcp-connector); [Creetr](https://creetr.com/blog/higgsfield-mcp)
- Commercial use (VENDOR CLAIM): Higgsfield marketing pages say outputs can be used in paid ads, client campaigns, ecommerce, packaging and print "without additional licensing". The same pages advise reviewing individual model terms for branded references, copyrighted material or third-party likenesses — [Higgsfield Claude image page](https://higgsfield.ai/claude-ai-image-generator); [Higgsfield Claude video page](https://higgsfield.ai/claude-ai-video-generator)

**Video models**
- Seedance 2.0 (ByteDance): SHIPPED February 2026.
  - It went viral with celebrity deepfakes (a Tom Cruise vs. Brad Pitt fight clip) and drew cease-and-desist letters from Disney ("virtual smash-and-grab of Disney's IP"), Paramount, WBD, Netflix, Sony and Universal. MPA CEO Charles Rivkin demanded ByteDance "immediately cease its infringing activity" — [TechCrunch, 2026-02-15](https://techcrunch.com/2026/02/15/hollywood-isnt-happy-about-the-new-seedance-2-0-video-generator/); [NBC News](https://www.nbcnews.com/tech/tech-news/seedance-2-bytedance-copyright-infringement-concerns-hollywood-rcna259173)
  - The API launch, planned for February 24, 2026, was delayed. ByteDance reportedly added guardrails: no real-face generation from uploaded images or reference video, and invisible C2PA watermarks (SECONDARY) — [Medium/Evolink](https://medium.com/@hi.evolink/the-seedance-2-0-copyright-crisis-a-developers-guide-to-what-happened-and-what-to-do-next-db2583af475e)
- Seedance 2.5: unveiled June 2026. Reported features are native 30-second single-shot clips, up to 50 reference inputs and 3D camera blockouts. The API is reported live — [TechTimes, 2026-06-24](https://www.techtimes.com/articles/318975/20260624/bytedance-seedance-25-native-30-second-ai-video-no-stitching-required.htm); [CineD](https://www.cined.com/bytedance-seedance-2-5-api-goes-live-30-second-single-shot-clips-50-reference-inputs-and-3d-camera-blockouts/)
- Reference inputs: Veo 3.1 reportedly accepts only 3 reference inputs and Kling 3.0 accepts 5, against Seedance's much larger multi-reference input (SECONDARY) — [CineD](https://www.cined.com/bytedance-seedance-2-5-api-goes-live-30-second-single-shot-clips-50-reference-inputs-and-3d-camera-blockouts/)
- Native audio and lip sync (all SECONDARY comparisons):
  - Veo 3.1 is the most-cited pick for reliable dialogue lip sync, at about 120 ms accuracy per one guide.
  - Seedance 2.0 is credited with stronger non-English lip sync and is top-rated on one blind audio-included arena.
  - Kling 3.0 Omni has native lip sync in five languages.
  - Arena rankings conflict: Seedance 2.0 is #1 on image-to-video in an Artificial Analysis-based ranking, while Kling 3.0 is #1 on another arena. Runway Gen-4.5 is called the leader by one source and sits outside the top 12 in another.
  - Sources: [3D AI Studio](https://www.3daistudio.com/blog/best-ai-video-generator-2026); [techsy.io arena ranking](https://techsy.io/en/blog/best-ai-video-models); [lushbinary](https://lushbinary.com/blog/ai-video-generation-sora-veo-kling-seedance-comparison/); [aifreeapi](https://www.aifreeapi.com/en/posts/seedance-2-vs-kling-3-vs-sora-2-vs-veo-3)
- Use-case consensus across the comparison blogs (SECONDARY):
  - Veo 3.1 or Runway Gen-4.5 for cinematic single shots and realism.
  - Kling 3.0 for length (up to 15s clips), multi-shot work and value.
  - Seedance 2.x for reference-driven control.
  - Source: [lushbinary](https://lushbinary.com/blog/ai-video-generation-sora-veo-kling-seedance-comparison/)
- OpenAI Sora 2: OpenAI announced the discontinuation on March 24, 2026 ("We've decided to discontinue Sora in the consumer app and API"). The app and sora.com closed April 26, 2026. Most sources give September 24, 2026 as the API shutdown date, with no migration target listed. A reported $1B Disney partnership was affected — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/openai-shuts-down-sora-ai-video-app-discontinued-after-six-months/); [invideo](https://invideo.io/blog/sora-ai-video-generator/); [Zilliz FAQ](https://zilliz.com/ai-faq/what-is-the-sora-shutdown-timeline)

**Image models**
- Nano Banana Pro (Gemini 3 Pro Image): announced November 20, 2025. Highlights were improved text rendering, multilingual text, up to 14 input images, localized edits and 2K/4K output. Third-party testers call it the text-rendering leader — [Luma learning hub](https://lumalabs.ai/learning-hub/luma-image-models-guide-nano-banana-seedream-gpt-image-1.5); [vidguru](https://www.vidguru.ai/blog/nano-banana-pro-vs-gpt-image-1-5-comparison.html)
- Seedream 4.5 (ByteDance): announced December 3, 2025, with 4K output.
  - Price: about $0.04/image against about $0.14 for Nano Banana Pro and GPT Image 1.5. One comparison says it tied Nano Banana Pro on most tests and won infographics.
  - Seedream 5.0 / 5 Pro now exist, and one source recommends 5 Pro for final ads and ecommerce hero images (SECONDARY).
  - Sources: [felloai](https://felloai.com/new-chinese-model-seedream-4-5-is-challenging-nano-banana-pro-and-gpt-in-ai-image-quality/); [wavespeed](https://wavespeed.ai/blog/posts/seedream-5-0-vs-nano-banana-pro-gpt-image-flux-klein-qwen-image-comparison-2026/); [rangy](https://rangy.ai/blog/seedream-5-pro-vs-nano-banana-pro-vs-gpt-image-2/)
- OpenAI gpt-image: GPT Image 1.5 is reportedly marked deprecated in OpenAI's model list and GPT Image 2 is the current model (SECONDARY). One blog says GPT Image 1.5 lost every head-to-head test against Nano Banana Pro — [rangy](https://rangy.ai/blog/seedream-5-pro-vs-nano-banana-pro-vs-gpt-image-2/); [vidguru](https://www.vidguru.ai/blog/nano-banana-pro-vs-gpt-image-1-5-comparison.html)
- Midjourney: paid subscribers get a broad contractual license. Unmodified outputs likely have no copyright protection, and Midjourney reportedly does not indemnify users against copyright claims. Disney and Universal sued Midjourney on June 11, 2025 (C.D. Cal.), DreamWorks later joined, and the case is in discovery as of about August 2026 (SECONDARY) — [terms.law](https://terms.law/2026/01/15/midjourney-commercial-use-rights-complete-2026-guide/); [rinzara tracker](https://rinzara.com/articles/ai-copyright-lawsuit-tracker-2026)

### Inferences
- For a Claude Code/Codex ad platform, Higgsfield's CLI or API looks like a better integration path than MCP for unattended pipelines, given its long-lived tokens, per-generation pricing and Higgsfield's own recommendation. MCP fits interactive sessions better.
- A sensible default routing, by ad use:
  - Static ads with text: Nano Banana Pro, or Seedream for volume and low cost. Then composite the final typography (see section 3).
  - Talking-head or dialogue video: Veo 3.1.
  - Product or brand consistency across shots: Seedance 2.x multi-reference.
  - Cheap variants and B-roll: Kling 3.0 or Wan.
  - Avoid any Sora dependency.
- Higgsfield's cost and tier structure has changed several times in 2026. The platform should read current credit costs at runtime rather than hard-coding them.
- Seedance's provenance controversy, together with the guardrails that block real faces from uploads, means a coach's own face cannot be assumed to work as a Seedance reference. Test it, or use avatar tools that have a consent flow.

### Gaps
- Could not fetch higgsfield.ai directly (DNS failure), so the exact current model roster, MCP tool list, API rate card and terms of service are unverified. Veo pricing per second via the API was not found.
- No independent primary sources found for these dates and specs: Kling 3.0 launch date, Veo 3.1 release date (background knowledge says it was announced around October 2025 with "Ingredients to Video" and Flow updates), Runway Gen-4/Gen-4.5 specs, Wan 3.0, and Nano Banana (Gemini 2.5 Flash Image, background knowledge says August 2025).
- No independent, non-vendor ad-specific quality benchmark was found. Arena leaderboards conflict.

## 2. AI UGC and avatar tools (HeyGen, Synthesia, Arcads, Creatify, Captions, MakeUGC)

### Takeaway
AI UGC/avatar ad tools are commercially big but supported almost entirely by vendor-reported traction. The evidence that they convert better than human creators is thin and unverified. Practitioners report sync drift, weak non-English output, and finished videos that still need manual editing. As of 2026 the main risks are legal (FTC fake-testimonial rule, New York synthetic-performer disclosure) and reputational, more than technical.

### Cited Findings
- Arcads reportedly has 6,000+ clients producing about 100,000 ad assets per month, and Creatify has passed $9M ARR. Both figures are VENDOR/SECONDARY and unverified — [Trends.vc](https://trends.vc/synthetic-ugc-ads-ai-actors-managed-agencies-creative-fatigue/)
- Strategy shift described in 2026 by an industry newsletter: "The first wave of AI UGC ads looked like AI UGC ads. The second wave looks like UGC." Same source: only 45% of consumers feel positive about AI ads while 82% of executives assume they do. The original survey was not located — [Trends.vc](https://trends.vc/synthetic-ugc-ads-ai-actors-managed-agencies-creative-fatigue/)
- Reported weaknesses (SECONDARY reviews):
  - Arcads: lip-sync drift on fast scripts and weaker results in non-English languages.
  - Creatify: users "consistently report needing to manually edit the final video" before running it as a paid ad.
  - HeyGen: Trustpilot about 2.5/5 on about 2,000 reviews, mostly billing complaints, against G2 4.8/5.
  - MakeUGC: 20+ actors and a "Good" realism rating, with no performance data.
  - Sources: [Atlabs comparison](https://www.atlabs.ai/blog/atlabs-ai-vs.-heygen-vs.-creatify-vs.-arcads-vs.-viralinn-which-ai-ugc-tool-is-actually-worth-paying-for-in-2026); [shhots](https://shhots.ai/blog/heygen-vs-arcads/); [adlibrary](https://adlibrary.com/posts/best-ai-ugc-video-tools-2026)
- New York synthetic performer law (effective June 9, 2026) requires conspicuous disclosure when an ad features an AI-generated human not based on a real identifiable person. That covers stock AI avatars of the kind these tools provide (see section 5) — [Honigman](https://www.honigman.com/the-matrix/understanding-new-yorks-synthetic-performer-disclosure-law-impacts-businesses-steps-compliant)
- The FTC Consumer Review Rule bans fake testimonials, including AI-generated ones that misrepresent a real customer experience. An AI actor reading a script presented as a customer's experience is the highest-risk use (see section 5) — [FTC final rule PDF](https://www.ftc.gov/system/files/ftc_gov/pdf/r311003consumerreviewstestimonialsfinalrulefrn.pdf)

### Inferences
- For coaches, consultants and local services, the safest avatar uses are:
  - The owner's own consented digital twin (HeyGen/Synthesia-style personal avatar) delivering the owner's own claims.
  - Clearly framed explainer or spokesperson formats.
- The riskiest uses are AI "customers" giving testimonials or results. These violate the FTC rule's substance even when a disclosure label is present, because the experience described is not real.
- Expect rising detection by consumers and platforms. "Looks like real UGC" is a compliance problem as well as a creative goal.

### Gaps
- No independent A/B or lift study comparing AI avatar UGC with human creator UGC was found.
- Synthesia and Captions policies, consent flows and pricing were not researched this session. Neither was HeyGen's consent and verification process for custom avatars.

## 3. Failure modes ("AI slop") and mitigation

### Takeaway
High-profile 2024–2025 failures (Coca-Cola twice, McDonald's Netherlands) show the same pattern: uncanny characters, continuity errors and a disjointed feel from stitching many generated clips together. Audiences call the result "soulless" regardless of how much labor went into it. NIQ found the only AI ad consumers did not spot was one heavily iterated by a professional. Mitigation therefore means fewer, controlled shots built from references, real typography composited in post, and human review before launch.

### Cited Findings
- McDonald's Netherlands posted a 45-second fully generative AI Christmas ad on December 6, 2025 and removed it on December 9, 2025 after backlash. Critics cited "uncanny AI-generated characters" and "disjointed visuals created by stitching together multiple generative clips". The agencies were TBWA\Neboko and The Sweetshop, whose CEO defended "thousands of generated takes" in a statement later taken down. McDonald's called the episode "an important learning" — [NBC News](https://www.nbcnews.com/world/europe/mcdonalds-ai-generated-christmas-advert-social-media-backlash-rcna248590); [The Drum](https://www.thedrum.com/news/the-most-terrible-ad-of-the-year-mcdonald-s-pulls-ai-ad); [eMarketer](https://www.emarketer.com/content/mcdonald-s-pulled-ai-ad-offers-lessons-on-what-audiences-will-won-t-accept)
- Coca-Cola's 2025 "Holidays Are Coming" AI remake (November 2025, made with Silverside and Secret Level) drew backlash for the second year running.
  - Reviewers called it an improvement on 2024 but "still soulless". Euronews noted "several continuity errors".
  - The WSJ reported about 100 people on the project, with five specialists generating tens of thousands of clips.
  - Sources: [Euronews, 2025-11-05](https://www.euronews.com/2025/11/05/real-magic-coca-colas-ai-generated-christmas-ad-sparks-widespread-backlash-again); [Forbes, 2025-11-04](https://www.forbes.com/sites/danidiplacido/2025/11/04/coca-cola-sparks-backlash-with-ai-generated-christmas-ad-again/); [Marketing AI Institute](https://www.marketingaiinstitute.com/blog/criticism-ai-coke-holiday-ad)
- NIQ (December 2024): consumers spontaneously identified most AI ads as AI. The only one not immediately flagged "was created by an advertising professional through considerable iterative editing" — [NIQ press release](https://nielseniq.com/global/en/news-center/2024/niq-research-uncovers-hidden-consumer-attitudes-toward-ai-generated-ads/)
- Text rendering: Nano Banana Pro is rated the in-image text leader, and Meta extended text generation to text inside image creative in mid-2026 (SECONDARY). Model text rendering has improved but is still benchmarked as a differentiator, meaning it is not yet reliable across models — [Luma guide](https://lumalabs.ai/learning-hub/luma-image-models-guide-nano-banana-seedream-gpt-image-1.5); [Benly](https://benly.ai/learn/meta-ads/advantage-plus-updates-2026)
- Meta's built-in controls: advertisers can preview AI-generated and enhanced variants before launch, toggle off individual enhancement types, and use a "Restricted Words" list. Meta has been testing a creative approval workflow (2026, SECONDARY) — [adsuploader](https://adsuploader.com/blog/advantage-plus-creative-enhancements); [Benly](https://benly.ai/learn/meta-ads/advantage-plus-updates-2026)
- Identity consistency tools: Higgsfield exposes `create_character` / `list_characters` through MCP. Seedance 2.5 accepts up to 50 references and Veo 3.1 up to 3 — [Creetr](https://creetr.com/blog/higgsfield-mcp); [CineD](https://www.cined.com/bytedance-seedance-2-5-api-goes-live-30-second-single-shot-clips-50-reference-inputs-and-3d-camera-blockouts/)

### Inferences
- A practical anti-slop checklist for the platform:
  1. Use reference images: a product photo and the owner's own photo or character sheet.
  2. Prefer short single shots, or native long single shots such as Seedance 2.5's 30s, over stitching many clips.
  3. Never rely on model-rendered text for prices, offers, URLs or legal copy. Composite real fonts in post.
  4. Run an automated QA pass on hands, faces, text and logo integrity, then require human sign-off.
  5. Avoid holiday and nostalgia themes that set up "soulless" comparisons.
  6. Favor stylized or clearly non-photoreal looks when photorealism adds risk.
- Seasonal, emotional brand films are the highest-risk format for backlash. Direct-response product and service ads for small businesses attract less scrutiny but face the same detection effects.

### Gaps
- No primary vendor documentation was retrieved on character sheets or reference workflows.
- No systematic error-rate data (hands, physics, text accuracy) per model was found.

## 4. Consumer and performance evidence

### Takeaway
The best independent evidence (NIQ's EEG and implicit-response study, December 2024) finds that AI ads are spotted readily and are rated more "annoying, boring, confusing". Memory encoding was weak even for high-quality AI ads, though brand association still worked. Academic evidence on disclosure labels is mixed: several 2025 experiments find lower authenticity, trust and purchase intent, especially for high-involvement products, while others find null effects. Platform-reported performance gains from AI-assisted creative are small to moderate and come from the vendors themselves.

### Cited Findings
- NIQ (released December 12, 2024, presented at CES 2025), using EEG and implicit measures:
  - Consumers perceived AI ads as "annoying," "boring," and "confusing".
  - Memory activation measured by EEG was weak for most AI ads, "even those perceived as 'high quality'".
  - Low-quality AI ads still communicated brand associations but were "cognitively taxing and distracting".
  - Effects were consistent across age groups, including Gen Z.
  - NIQ warns of a "negative halo" that could spread to the brand.
  - Sources: [NIQ](https://nielseniq.com/global/en/news-center/2024/niq-research-uncovers-hidden-consumer-attitudes-toward-ai-generated-ads/); [Marketing Dive](https://www.marketingdive.com/news/consumer-perceptions-generative-ai-in-marketing-openai-sora/735761/)
- EMARKETER/CivicScience poll (September 2024): 65% of US adults are at least somewhat uncomfortable with AI-generated ads — [eMarketer](https://www.emarketer.com/content/ai-s-too-close-comfort)
- Academic studies on disclosure labels:
  - Kučinskas (2025), two experiments: AI disclosure significantly reduces perceived authenticity, which mediates negative effects on purchase intention, brand image and brand trust — [ResearchGate](https://www.researchgate.net/publication/389674886_Revealing_AI_Involvement_in_Ad_Creation_Effects_on_Authenticity_Brand_Perceptions_and_Consumer_Intentions)
  - Israfilzade (Equilibrium / Economic Policy journal, December 2025), 2×2 design: labelled AI ads lowered trust and purchase intent, particularly for high-involvement products — [economic-policy.pl](https://economic-policy.pl/index.php/eq/article/view/4038)
  - Instagram travel-ad study (Computers in Human Behavior, 2026): disclosure alone had no significant main effect on credibility or purchase intention in one study, but disclosed AI posts lowered both in a second study — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0747563226001445)
  - A sensory-product study (International Journal of Applied AI in Business) found no significant decline in ad credibility or brand authenticity from an AI label — [ResearchGate](https://www.researchgate.net/publication/415127004_AI_Disclosure_in_Applied_Marketing_Practice_Effects_of_an_AI_Label_on_Advertising_Credibility_Brand_Authenticity_and_Purchase_Intention_for_a_Sensory_Experience_Product)
  - Proposed mechanism: disclosure activates persuasion knowledge (Bui 2025, Journal of Research in Interactive Marketing; abstract-level only) — [ResearchGate](https://www.researchgate.net/publication/395406060_Examining_the_effect_of_AI_advertising_involvement_disclosure_on_advertising_value_and_purchase_intentions)
  - Broader labelling research: AI labels reduce the perceived accuracy of content but have limited broader effects — [arXiv 2506.16202](https://arxiv.org/pdf/2506.16202)
- Brand backlash cases:
  - McDonald's Netherlands pulled its AI ad within 3 days (December 2025).
  - Coca-Cola drew criticism two years running (2024, 2025) but defended its ads and kept the approach.
  - Sources: [NBC News](https://www.nbcnews.com/world/europe/mcdonalds-ai-generated-christmas-advert-social-media-backlash-rcna248590); [Marketing AI Institute](https://www.marketingaiinstitute.com/blog/criticism-ai-coke-holiday-ad)
- Big brands remain "skittish" about AI-generated creative, and marketers say Meta's platform "isn't ready for full automation" (April 2026) — [Marketing Brew, 2026-04-07](https://www.marketingbrew.com/stories/2026/04/07/meta-ai-ad-creation)
- Meta-reported performance (VENDOR CLAIM): +2–3% conversions from background generation on Advantage+ catalog ads, +2% from video expansion on Reels, and +13% conversions from "related media" — [Meta Advantage+ Creative](https://www.facebook.com/business/ads/meta-advantage-plus/creative). A widely repeated "22% higher ROAS" for Advantage+ could not be traced to a Meta primary source — [Digital Applied](https://www.digitalapplied.com/blog/meta-ai-automated-ads-2026-marketing-guide)

### Inferences
- AI is safest and most measurable as a variant and asset multiplier: backgrounds, resizes, B-roll, iterations around a real human or a real product. Fully synthetic hero storytelling is where memory and backlash penalties show up.
- Disclosure effects depend on context. The penalty is largest for high-involvement purchases and authenticity-driven categories, which includes coaching and consulting where the buyer is buying the person. Making the real owner or practitioner visible probably offsets AI-production signals. This is an inference; no source tested it directly.
- Because disclosure is increasingly mandatory (EU, New York, platforms), the practical question is how to make disclosed AI ads good, not whether to disclose.

### Gaps
- Could not retrieve Kantar's AI-ad testing data, Toys "R" Us's Sora film reception (June 2024), Mango's AI-generated fashion models (July 2024), or Klarna's claimed AI marketing savings. Background knowledge: Klarna claimed about $10M/year in marketing savings in 2024 and Toys "R" Us premiered a Sora-made film at Cannes 2024 to mixed and negative reception. Both are unverified this session; get sources before citing.
- No independent study of AI ads specifically for small service businesses or local services was found.
- No study measuring outcomes when disclosure helps (e.g., "made with AI" as a novelty or transparency signal) was found.

## 5. Disclosure and legal rules

### Takeaway
As of October 2026, compliance has several layers:
1. **Platform labels.** Meta labels AI made with its own tools and C2PA-tagged third-party AI. Political and social-issue ads must self-disclose. YouTube creators must disclose realistic synthetic content. TikTok reads C2PA and restricts undisclosed significantly AI-modified ads.
2. **US FTC.** The Consumer Review Rule bans AI-generated fake reviews and testimonials. Penalties reach about $53K per violation, and enforcement began in late 2025 and 2026.
3. **New York (effective June 9, 2026).** Ads shown to New York audiences that feature synthetic performers must carry a disclosure.
4. **EU AI Act Article 50.** Deepfake and AI-content transparency duties have applied since August 2, 2026. Some machine-readable marking duties are deferred to December 2026 and February 2027.

### Cited Findings
**Meta**
- Political, social-issue and electoral ads (announced November 2023, effective early 2024):
  - Advertisers must disclose photorealistic images or video, or realistic-sounding audio, that were digitally created or altered. Examples: showing a real person saying or doing something they did not, depicting a realistic person or event that does not exist or did not happen, or altering footage of a real event.
  - Inconsequential edits are exempt.
  - Disclosed ads get a label that also appears in the Ad Library. Undisclosed ads are rejected, and repeated failures bring penalties.
  - Sources: [Meta Transparency Center](https://transparency.meta.com/policies/ad-standards/siep-advertising/siep); [NBC News](https://www.nbcnews.com/tech/tech-news/meta-require-political-advertisers-disclose-use-ai-rcna124109); [DT Next](https://www.dtnext.in/lifestyle/technology/meta-to-require-advertisers-to-disclose-ads-created-via-ai-on-political-issues-747076)
- Commercial ads: Meta labels ads created or significantly edited with its own generative tools (Background Generation, Image Generation), and minor edits such as resizing or color correction do not trigger a label. The label usually sits in the "About this ad" / three-dot menu. Ads with an AI-generated photorealistic person can show the label next to "Sponsored" — [Marketing Dive](https://www.marketingdive.com/news/sociable-meta-adds-updated-disclosure-tags-for-ai-generated-ads/824833/); [ContentGrip](https://www.contentgrip.com/meta-ai-ad-labels/)
- Third-party detection: Meta says it uses industry signals such as C2PA metadata to detect content from outside tools. One guide says auto-labelling of third-party-tool ads took effect June 1, 2026, while an older guide says Meta does not auto-label commercial third-party content. This CONFLICT is unresolved — [1clickreport](https://www.1clickreport.com/blog/meta-ad-policy-changes-2026-compliance-guide); [adamigo](https://www.adamigo.ai/blog/meta-ai-disclosure-rules-advertisers-know)

**YouTube and Google**
- YouTube (since March 18, 2024):
  - Creators must disclose realistic altered or synthetic content: realistic likeness or voice of a person, altered footage of real events or places, generated realistic scenes.
  - Clearly unrealistic or animated content, special effects and productivity uses (scripts, captions) are exempt.
  - The label appears in the description, or on the player itself for sensitive topics (health, finance, news, elections).
  - YouTube may apply labels proactively, and repeated non-disclosure risks content removal or YPP suspension.
  - Sources: [9to5Google](https://9to5google.com/2024/03/18/youtube-altered-content-disclosure/); [NBC News](https://www.nbcnews.com/tech/tech-news/youtube-says-will-require-creators-label-ai-content-rcna143937)
- Google Ads: reported to use SynthID on AI-generated assets in Performance Max / Google Ads, with a "How this ad was made" panel in My Ad Center (SECONDARY) — [ppc.land](https://ppc.land/youtube-unveils-new-tool-to-enhance-transparency-for-ai-altered-content); [82dash](https://blog.82dash.com/ai-ad-label-rules-meta-google-tiktok/)

**TikTok**
- TikTok became the first video platform to implement C2PA Content Credentials, auto-labelling AI content from other tools (May 2024) — [TikTok Newsroom](https://newsroom.tiktok.com/en-us/partnering-with-our-industry-to-advance-ai-transparency-and-literacy); [NBC News](https://www.nbcnews.com/tech/tech-news/tiktok-will-automatically-label-ai-generated-content-rcna151446)
- TikTok ad policy reportedly covers content "significantly modified by AI", and undisclosed AI content can be rejected or restricted (SECONDARY) — [82dash](https://blog.82dash.com/ai-ad-label-rules-meta-google-tiktok/); [Billo](https://billo.app/blog/ai-labeling/)

**FTC Consumer Review Rule**
- Rule: 16 CFR Part 465, published at 89 FR 68077 on August 22, 2024 and effective October 21, 2024 — [FTC final rule PDF](https://www.ftc.gov/system/files/ftc_gov/pdf/r311003consumerreviewstestimonialsfinalrulefrn.pdf); [Crowell](https://www.crowell.com/en/insights/client-alerts/keeping-it-real-ftc-targets-fake-reviews-in-first-consumer-review-rule)
- It prohibits:
  - Fake reviews and testimonials, including AI-generated ones and those by non-existent people or people without actual experience.
  - Buying positive or negative reviews.
  - Undisclosed insider reviews.
  - Review suppression.
  - Buying or selling fake social influence indicators.
  - Source: [FTC final rule PDF](https://www.ftc.gov/system/files/ftc_gov/pdf/r311003consumerreviewstestimonialsfinalrulefrn.pdf)
- Penalties: up to $53,088 per violation (2025 figure, reportedly unchanged for 2026) — [Legal500](https://www.legal500.com/intelligence/united-states/consumer-protection/five-stars-zero-tolerance-ftc-turns-up-enforcement-under-consumer-review-rule)
- Enforcement:
  - December 22, 2025: warning letters to 10 companies, posted April 2026. Six went to property managers, three to personal-injury law firms and one to an accounting firm, all small and local service businesses.
  - A final order on July 15, 2026 reportedly included a $4M judgment, suspended upon payment of $750K. Single source, so verify.
  - Sources: [DLA Piper, July 2026](https://www.dlapiper.com/en/insights/publications/2026/07/ftcs-2026-enforcement-approach-to-fake-reviews-takes-shape-takeaways-for-companies); [FoodNavigator, 2026-01-07](https://www.foodnavigator-usa.com/Article/2026/01/07/ftc-signals-crackdown-on-fake-reviews-and-testimonials/)

**New York synthetic performer law (S.8420A)**
- Status: signed December 11, 2025 (one source says January 29, 2026) and effective June 9, 2026. Described as the first US state AI advertising disclosure law.
- Scope:
  - Requires conspicuous disclosure when an ad includes a "synthetic performer", meaning an AI-created human not based on an identifiable real person.
  - Applies to ads distributed to New York audiences regardless of where the advertiser is.
  - Applies only where the advertiser has actual knowledge.
- Exemptions: audio-only ads, expressive works (films, games) where the ad use is consistent with the work, and AI used solely for translation of a human performer.
- Form: not specified (language, placement and size are left open).
- Penalties: $1,000 for the first violation and $5,000 for each subsequent one.
- A companion law strengthened post-mortem publicity rights.
- Sources: [Honigman](https://www.honigman.com/the-matrix/understanding-new-yorks-synthetic-performer-disclosure-law-impacts-businesses-steps-compliant); [Lowenstein](https://www.lowenstein.com/news-insights/publications/articles/new-york-legislation-requires-disclosure-on-ai-generated-performers-in-advertising-and-strengthens-post-mortem-publicity-rights-savare-sterba-tijani); [Skadden, January 2026](https://www.skadden.com/insights/publications/2026/01/two-newly-enacted-new-york-laws-will-regulate); [Ashurst Perkins Coie](https://www.ashurstperkinscoie.com/en/insights/new-york-requires-disclosure-of-synthetic-performers-in-ads/)
- Federal preemption: a White House Executive Order of December 11, 2025 seeks to pause state AI laws that conflict with federal policy. Its effect on the New York law is unknown — [Davis+Gilbert](https://www.dglaw.com/ai-legal-updates-synthetic-performer-transparency-state-federal-conflict/)

**EU AI Act Article 50**
- Timing: transparency obligations have applied since August 2, 2026. The Digital Omnibus (reported as Regulation (EU) 2026/1744) left Article 50 on its original date and mainly delayed high-risk obligations (Annex III to December 2, 2027) — [Legalithm](https://www.legalithm.com/en/blog/eu-ai-act-what-applies-2-august-2026); [artificialintelligenceact.eu](https://artificialintelligenceact.eu/transparency-rules-article-50/)
- Deferrals reported by Paul Weiss: December 2, 2026 for Article 50(2) marking and detection duties on generative systems already on the market, and February 2, 2027 for watermark-detection interoperability. Verify against the Official Journal — [Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content)
- Deployer duty under 50(4): deepfakes must be labelled so the label is "immediately recognisable without user interaction", is perceivable at first exposure and is embedded in the content where possible. Content published before August 2, 2026 need not be relabelled — [Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content)
- Code of Practice on Transparency of AI-generated Content:
  - Has a provider section (marking and detection) and a deployer section (labelling).
  - Voluntary, but recognised as an adequate way to demonstrate compliance.
  - The Commission finalised three EU icons for deployers.
  - Sources: [European Commission](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content); [Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content)

### Inferences
- Minimum compliance defaults for the platform:
  1. Never generate testimonials, reviews, "customer results" or AI people presented as real customers.
  2. Auto-add a visible "AI-generated" or "synthetic performer" disclosure whenever a photoreal AI human appears. This satisfies New York and EU 50(4), and fits Meta and YouTube expectations.
  3. Preserve C2PA metadata rather than stripping it.
  4. Block political and social-issue ads by default, or route them to platform self-disclosure.
  5. Log prompts, models and assets as an audit trail.
- The FTC's targets so far have been small local service firms (property managers, PI law firms, an accountant), which is exactly this platform's customer base.

### Gaps
- Could not fetch the current text of Meta's commercial-ad AI policy. Whether third-party AI is auto-labelled since June 2026 is unresolved.
- Google Ads political synthetic-content policy (background knowledge: disclosure required since November 2023) was not verified. TikTok's current ad-policy wording was not verified from the primary source.
- FTC Endorsement Guides (revised June 2023; background knowledge: they cover virtual influencers and require endorsers to be bona fide users) were not re-fetched this session.
- Other state laws (e.g., California political-ad AI disclosure, Tennessee's ELVIS Act on voice likeness) were not researched.
- The July 2026 FTC order details need verification.

## 6. Rights: commercial use, likeness and voice, copyright of AI outputs

### Takeaway
In the US, purely AI-generated output is not copyrightable. The Copyright Office's January 2025 Part 2 report says prompts alone are insufficient, and the Supreme Court declined Thaler on March 2, 2026. Human selection, arrangement and modification can be protected. Commercial use therefore rests on contract (each generator's terms), not ownership, and indemnity varies. Likeness and voice are the sharpest risks: Seedance 2.0's celebrity deepfakes drew studio cease-and-desists, New York strengthened post-mortem publicity rights, and Disney/Universal v. Midjourney is ongoing.

### Cited Findings
- USCO "Copyright and Artificial Intelligence, Part 2: Copyrightability" (January 2025):
  - Works entirely generated by AI are not copyrightable, and prompts alone do not give sufficient control over expressive elements.
  - Perceptible human-authored contributions, and creative selection, arrangement or modification of outputs, can be protected.
  - The report followed more than 10,000 public comments.
  - Sources: [Skadden, February 2025](https://skadden.com/insights/publications/2025/02/copyright-office-publishes-report); [Manatt](https://manatt.com/insights/newsletters/copyright-office-releases-new-report-on-copyrightability-of-ai-works)
- Thaler v. Perlmutter: certiorari denied March 2, 2026 (No. 25-449), leaving the 2025 D.C. Circuit ruling requiring human authorship in place. The case did not address how much human involvement is enough — [Mayer Brown, March 2026](https://www.mayerbrown.com/en/insights/publications/2026/03/supreme-court-denies-review-in-ai-authorship-case)
- Midjourney: the license is contractual. Raw outputs likely have no copyright protection, and Midjourney reportedly does not protect users from infringement claims. Disney/Universal (plus DreamWorks) v. Midjourney was filed June 11, 2025 and is in discovery as of mid-2026 — [terms.law, 2026-01-15](https://terms.law/2026/01/15/midjourney-commercial-use-rights-complete-2026-guide/); [Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/ce8eaa5f/ai-in-litigation-series-an-update-on-ai-copyright-cases-in-2026)
- Higgsfield claims commercial use including paid ads, but tells users to check per-model terms for branded references, copyrighted material and likenesses (VENDOR CLAIM) — [Higgsfield](https://higgsfield.ai/claude-ai-image-generator)
- Seedance 2.0 likeness and IP: studios' cease-and-desists and SAG-AFTRA support (February 2026), followed by reported guardrails blocking real-face generation from uploads — [TechCrunch](https://techcrunch.com/2026/02/15/hollywood-isnt-happy-about-the-new-seedance-2-0-video-generator/); [Medium/Evolink](https://medium.com/@hi.evolink/the-seedance-2-0-copyright-crisis-a-developers-guide-to-what-happened-and-what-to-do-next-db2583af475e)
- New York enacted strengthened post-mortem publicity rights alongside the synthetic performer law (December 2025) — [Lowenstein](https://www.lowenstein.com/news-insights/publications/articles/new-york-legislation-requires-disclosure-on-ai-generated-performers-in-advertising-and-strengthens-post-mortem-publicity-rights-savare-sterba-tijani)

### Inferences
- Clients cannot stop competitors copying raw AI ad visuals. Defensible assets are human-authored elements: copy, real photography, layout and compositing, and brand marks. The platform should keep a record of human creative contributions.
- Require written consent before cloning any person's face or voice, including the client's own staff. Block prompts naming celebrities, brands or characters.
- Prefer generators whose terms grant commercial rights and, where available, IP indemnity for enterprise or API tiers. Indemnity terms were not verified this session.

### Gaps
- Primary commercial-use and indemnity terms were not retrieved for Google (Gemini/Veo, including Google's generative AI indemnity), OpenAI, ByteDance (Seedance/Seedream via BytePlus), Kling, Runway, HeyGen or Synthesia.
- Voice-rights statutes (e.g., Tennessee ELVIS Act 2024, California AB 2602/1836 on digital replicas) were not researched this session.
- The USCO Part 2 report was read only through law-firm summaries. The primary PDF is at copyright.gov but was not fetched.
