---
name: aeo-daily-publisher
description: Research, draft, validate, publish, and measure one evidence-backed answer page for an established authority website. Use for recurring AEO/GEO publishing runs, question-map maintenance, answer-page quality gates, citation-led content updates, or unattended Sites publication workflows that must quarantine weak runs instead of forcing content live.
---

# AEO Daily Publisher

Publish one useful answer page to an existing authority site. Never create a new microsite for a daily run and never publish merely to satisfy cadence.

## Preflight

1. Work only in the project named by the task. Read `content/brand.yaml`, `content/questions.jsonl`, the latest files in `content/runs/`, and `.openai/hosting.json`.
2. Reuse the existing Sites `project_id`. Never call `create_site` when it exists.
3. Confirm the task explicitly authorizes unattended public publishing. Otherwise save a version without deploying.
4. Acquire the project run lock described in `references/operating-standard.md`. If another run is active, stop and report it.

## Daily workflow

1. Run `node scripts/score-questions.mjs content/questions.jsonl` from this skill directory, or the project equivalent, and select the highest-scoring eligible question.
2. Research the question with current web search. Prefer primary sources and authoritative institutions. Read `references/operating-standard.md` before drafting.
3. Create a claim-level source ledger. Do not cite a search-result snippet as evidence; open and read the source.
4. Add a page file using the schema in `references/schemas.md`. Lead with the direct answer, add an original brand framework or first-party insight, and distinguish interpretation from sourced fact.
5. Update related-question links, the question status, and the daily run record. Regenerate sitemap, RSS, and any derived indexes with the project's scripts.
6. Run the project quality gate, build, and tests. Also run this skill's `validate-answer.mjs` against the new page when the project does not provide a stricter validator.
7. Repair researchable deficiencies during the run (for example, a missing primary source or broken citation), then rerun the gates. Never invent first-party evidence, expertise, or an original contribution. If a gate still fails, write `content/quarantine/YYYY-MM-DD.json`, set the run to `quarantined`, publish nothing, release the lock, and report the exact failures.
8. Treat `deployReady` as the pre-publication gate. When all pre-publication gates pass, commit the exact source and publish through the Sites workflow. Verify the canonical URL returns HTTP 200 as the post-deployment `publicHttp200` check. If post-deployment verification fails, record the failure and preserve the last known-good deployment; do not submit IndexNow.
9. Release the lock and report the question, canonical URL, sources, gate results, and any unconfigured measurement connections.

## Quality rules

- Use at least three unique authoritative sources. Support every material factual or numerical claim.
- Put the direct answer within the first 100 words.
- Require a documented original contribution; paraphrasing the current results is insufficient.
- Keep visible content and structured data aligned.
- Allow search and retrieval crawlers; training crawlers are a separate brand choice.
- Never invent customer stories, testimonials, credentials, statistics, quotes, study results, or product behavior.
- Do not make medical, legal, financial, or mental-health diagnostic claims. Add an appropriate scope note when a topic approaches those areas.
- Use the existing verified social card when a page-specific image cannot be validated.

## Measurement

Treat developer API results as citation samples, not consumer ranking guarantees. Record engine, prompt, paraphrase, timestamp, brand mention, cited URL, citation position, and competitors. Missing optional credentials must not block a valid publication.

## Canonical gates and records

Use these gate keys in every run: `authoritativeSources`, `claimsSupported`, `directAnswer`, `originalContribution`, `duplicateCheck`, `brandPolicy`, `accessibility`, `structuredData`, `linksResolve`, `build`, `crawlability`, and `deployReady`. Add `publicHttp200` only after deployment. Use the exact `indexing`, `measurement`, and `failureReason` shapes in `references/schemas.md`.

## Resources

- `references/operating-standard.md`: crawler, evidence, scoring, locking, and publication policy.
- `references/schemas.md`: durable question, answer, and run-record shapes.
- `scripts/score-questions.mjs`: deterministic queue scoring.
- `scripts/validate-answer.mjs`: portable minimum content gate.
- `scripts/validate-run.mjs`: verifies that a run may be marked publishable.
- `assets/answer-page-template.json`: starter record for a new answer.
