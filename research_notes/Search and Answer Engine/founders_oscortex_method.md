# The founder's own method: OS Cortex AEO Publisher (read from the repo, 2026-10-28)

Source: the `plugins/os-cortex-aeo-publisher` plugin on `main` (PR #1, merged 2026-09-30), its two skills (`aeo-client-onboarding`, `aeo-daily-publisher`), `references/operating-standard.md`, `references/schemas.md`, the three scripts, and the deck `OS-Cortex-AEO-Build-Room.pptx` at the repo root. Strength: **founder's own**. The Obsidian vault was not mounted in this container, so no vault notes were read for this topic.

## What it is

A governed, evidence-gated answer-publishing system for ChatGPT desktop and Codex, with the OpenAI Sites plugin as the host. One authority domain, one answer page per daily run, nothing published after a failed gate. Sold in two editions: a client edition (white-glove setup, three supervised publications, optional governance retainer) and a Build Room / Platinum edition (self-install from a private marketplace, workshop-led first run).

## The principles (deck slides 2–4)

1. **AEO is a system, not a content trick.** One authority domain; a growing answer library on the client's established site; "compounding topical depth beats disposable microsites."
2. **Evidence first.** Start with the question and primary sources; every factual or numerical claim carries a visible citation ledger.
3. **Original utility.** Every page adds first-hand expertise, a framework, data, examples or a tool that competing pages do not have. Paraphrasing the current results is insufficient.
4. **The daily loop: discover → research → build → verify.** Expand the question map from real demand, search data, objections, comparisons and citation gaps; three or more authoritative sources, each claim mapped before drafting; one direct, extractable answer page with internal links, schema and a next action; publish only after the gates pass.
5. **Unattended does not mean ungoverned.** Weak runs are quarantined.

## The gates (operating standard and schemas)

Pre-publication gate keys, every one a named boolean: `authoritativeSources`, `claimsSupported`, `directAnswer`, `originalContribution`, `duplicateCheck`, `brandPolicy`, `accessibility`, `structuredData`, `linksResolve`, `build`, `crawlability`, `deployReady`; after deployment `publicHttp200`.

Content rules: at least three unique authoritative sources; the direct answer inside the first 100 words; a documented original contribution (20+ words of `originalInsight`); visible content and structured data aligned; never invent customer stories, testimonials, credentials, statistics, quotes, study results or product behaviour; no medical, legal, financial or mental-health diagnostic claims, with a scope note when a topic approaches them; short, exact, attributed quotations, paraphrase preferred.

Evidence rules: prefer original research, government sources, standards bodies, universities and first-party documentation; open each source and record title, publisher, URL, publication or update date, access date and the claims it supports; a page may use secondary context in addition to, never instead of, primary evidence; the brand's own framework is labelled as an original method rather than external fact.

Question scoring (0–100): demand 25%, business relevance 25%, citation gap 20%, evidence availability 20%, freshness 10%; questions with evidence under 60 are not eligible; published, quarantined, duplicate, off-brand and insufficient-evidence questions are excluded. Status: queued, researching, published, quarantined, retired.

Crawlability: allow `OAI-SearchBot`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Googlebot`, `bingbot`; keep `GPTBot` and `ClaudeBot` policy separate because they are training crawlers; pages public, indexable, canonical, textual, linked internally, in the XML sitemap and RSS feed, returning HTTP 200.

Measurement: Google Search Console, Bing Webmaster, IndexNow, GA4 and answer-engine developer APIs "improve measurement but do not determine whether a high-quality page may be published"; API results are "citation samples, not consumer ranking guarantees"; record engine, prompt, paraphrase, timestamp, brand mention, cited URL, citation position and competitors; a 25-question baseline with two paraphrases each.

## Onboarding and rollout (intake-and-launch.md, deck slides 7–9)

Required intake: legal and public brand name; canonical domain and answer-hub path; audience, urgent problems and transformations; offer and one primary CTA; approved claims with source-of-truth URLs; prohibited claims, regulated topics and escalation rules; a named author and a qualified reviewer; tone, corrections contact and citation policy; who owns the site, analytics, Search Console, Bing and APIs; explicit publishing authorisation and a rollback owner.

Acceptance sequence: dry-run preflight → supervised publication 1 (a definition or foundational question) → 2 (a practical how-to) → 3 (a comparison, objection or diagnostic) → the 25-question baseline → the schedule only after every hard gate passes → observe 14 unattended runs, targeting 95% operational success, zero unsupported claims, zero publications after a failed gate. Member edition default: saved-only or supervised publication until the first three pages pass.

Account isolation: the client owns the account, site, domain, Git project, OAuth grants, analytics, keys and billing; the agency gets only the access needed for delivery.

## What transfers to a Build Room skill, and what does not

Transfers directly: the four principles; the question map and its scoring weights; the three-source and first-100-words rules; the original-contribution rule; the claim ledger; the scope note for regulated topics; the author-and-reviewer pair; the supervised-first rollout (three pages by hand before any routine); the crawler policy split (search crawlers vs training crawlers); the measurement baseline of prompts with paraphrases; "never invent" as a hard gate.

Does not transfer as-is: the ChatGPT/Codex/Sites hosting, the run lock, the JSON answer records and `.mjs` validators (the member's page lives on their own site builder, written in markdown first), the daily cadence (a solo owner aged 55–75 publishes weekly or fortnightly, not daily), developer-API measurement (replaced by a manual monthly prompt check in the free consumer apps), and the agency delivery model.

Gaps the OS Cortex material does not cover and the Build Room skill must: Google Business Profile and local search; review solicitation; listings and citations; YouTube; the member's own Business File (§2 language, §3 offer, §18 proof) as the first source of questions and evidence; the Proof Engine as the source of first-party stories; website-builder mechanics for non-technical owners.
