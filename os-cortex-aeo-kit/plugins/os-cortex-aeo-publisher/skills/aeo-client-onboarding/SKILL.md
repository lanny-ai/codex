---
name: aeo-client-onboarding
description: Configure a new client-specific AEO/GEO authority publisher, including brand intake, Sites authority hub, durable content files, quality gates, credentials, supervised runs, and a local schedule. Use when setting up the OS Cortex AEO Publisher for a new brand, computer, ChatGPT account, domain, or client workspace.
---

# AEO Client Onboarding

Create one isolated Git project for one brand. Never copy another client's domain, credentials, analytics IDs, Sites project ID, author identity, claims, or content.

## Preflight

1. Confirm ChatGPT desktop/Codex and the Sites plugin are installed and available.
2. Detect the operating system with `node scripts/detect-platform.mjs`.
3. Create or select a dedicated local Git project owned by the client.
4. Treat API keys and OAuth tokens as secrets. Never place them in prompts, Git, templates, screenshots, or run records.
5. Read `references/intake-and-launch.md` before interviewing the client.

## Onboarding workflow

1. Collect the minimum brand intake: canonical domain, audience, problems, offer, approved and prohibited claims, authors/reviewers, tone, CTA, source-of-truth URLs, and risk topics.
2. Copy the files under `assets/client-starter/` into the client project and replace every `REPLACE_ME` value. Run `node scripts/validate-brand-config.mjs <project>/content/brand.yaml`.
3. Use Sites to create one authority hub, or reuse the client's existing Sites project. Persist only its opaque `project_id` in `.openai/hosting.json`.
4. Add answer routes, topic indexes, author, About, methodology, citation-policy, corrections, sitemap, RSS, robots, canonical metadata, and visible structured data.
5. Configure the retrieval crawlers separately from model-training crawlers. Never promise rankings or indexing.
6. Run `node scripts/preflight-project.mjs <project>`. Repair all required failures before research begins.
7. Complete three supervised publications. Require the client to review brand fit, original contribution, evidence, CTA, and scope notes.
8. Establish the 25-question baseline. Developer APIs are citation samples, not consumer-app rankings.
9. Create the daily automation only after the three supervised runs pass. Use the schedule and timezone the client explicitly chooses. Default to supervised or saved-only publication when authorization is unclear.
10. Give the client the run report, credential-status report, rollback location, and instructions for pausing the automation.

## Guardrails

- One brand, one authority domain, one isolated Git history.
- No credential reuse across clients.
- No automatic publication before explicit authorization and three supervised passes.
- No invented experts, first-party observations, customer stories, claims, citations, or results.
- Quarantine any failed run; cadence never overrides quality.
- Keep medical, legal, financial, and diagnostic claims out of scope unless qualified review and policy explicitly permit them.
- The local computer and desktop app must be running for local schedules. Recommend a controlled server runner for required 24/7 availability.

## Resources

- `references/intake-and-launch.md`: intake questions, account boundaries, and acceptance sequence.
- `references/connection-matrix.md`: required and optional provider connections.
- `scripts/detect-platform.mjs`: cross-platform environment summary.
- `scripts/validate-brand-config.mjs`: rejects incomplete or placeholder brand configuration.
- `scripts/preflight-project.mjs`: verifies the client project before supervised publishing.
- `assets/client-starter/`: portable durable-file templates.
