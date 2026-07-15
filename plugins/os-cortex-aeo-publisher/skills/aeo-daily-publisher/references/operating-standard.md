# Operating standard

## Question scoring

Score eligible questions from 0–100 using demand 25%, business relevance 25%, citation gap 20%, evidence availability 20%, and freshness 10%. Exclude published, quarantined, duplicate, off-brand, and insufficient-evidence questions.

## Evidence

- Prefer original research, government sources, standards bodies, universities, and first-party product documentation.
- Open each source and record its title, publisher, URL, publication or update date, access date, and the claims it supports.
- Require three unique authoritative sources. A page may use secondary context in addition to, but not instead of, primary evidence.
- Keep quotations short, exact, attributed, and necessary. Prefer paraphrase with citation.
- Label the brand's own framework as an original method rather than external fact.

## Crawlability

Allow `OAI-SearchBot`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Googlebot`, and `bingbot`. Keep GPTBot and ClaudeBot policy independent because they are associated with model-development crawling rather than search visibility. Pages must be public, indexable, canonical, textual, linked internally, included in the XML sitemap and RSS feed, and return HTTP 200.

## Run lock

Use `content/.aeo-run.lock` with the run date, task identifier, and start timestamp. Do not overwrite a lock newer than two hours. A stale lock may be replaced only after confirming no matching process or active scheduled run exists. Always remove the lock on success, quarantine, or handled failure.

## Publication gate

All of these must pass: schema, direct answer, source minimum, claim coverage, original contribution, duplicate check, brand policy, citation reachability, structured-data match, accessibility, internal links, build, tests, sitemap membership, and public HTTP verification. A failed gate quarantines the run; cadence never overrides quality.

## External services

Google Search Console, Bing Webmaster, IndexNow, GA4, and answer-engine APIs improve measurement but do not determine whether a high-quality page may be published. Log missing connections explicitly. Never expose API keys in files, logs, prompts, or reports.
