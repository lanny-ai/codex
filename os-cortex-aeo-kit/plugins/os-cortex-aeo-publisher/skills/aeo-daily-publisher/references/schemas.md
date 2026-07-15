# Durable schemas

## Question queue record

Required fields: `id`, `question`, `slug`, `cluster`, `intent`, `source`, `demand`, `businessValue`, `citationGap`, `evidence`, `freshness`, and `status`. Scores are integers from 0–100. Status is `queued`, `researching`, `published`, `quarantined`, or `retired`.

## Answer record

Required fields: `slug`, `question`, `title`, `description`, `summary`, `publishedAt`, `updatedAt`, `author`, `reviewer`, `cluster`, `originalInsight`, `sections`, `claims`, `sources`, `relatedSlugs`, and `cta`.

- `sections`: objects with `heading` and `paragraphs`, plus optional `steps`, `table`, or `callout`.
- `claims`: objects with `text` and one or more supporting `sourceIds`; brand-framework statements may use `kind: "original-framework"` and an empty source list.
- `sources`: objects with `id`, `title`, `publisher`, `url`, `publishedAt`, `accessedAt`, and `supports`.
- `cta`: object with `label`, `href`, and `description`.

## Run record

Required fields: `runId`, `date`, `questionId`, `status`, `startedAt`, `completedAt`, `gates`, `sources`, `publishedUrl`, `indexing`, `measurement`, and `failureReason`. Status is `passed`, `published`, or `quarantined`. Every gate is a named boolean. `publishedUrl` must be null unless all gates passed.

Use these pre-publication gate keys: `authoritativeSources`, `claimsSupported`, `directAnswer`, `originalContribution`, `duplicateCheck`, `brandPolicy`, `accessibility`, `structuredData`, `linksResolve`, `build`, `crawlability`, and `deployReady`. After deployment add `publicHttp200`.

- `indexing`: `{ "indexNow": "submitted" | "skipped" | "failed", "googleSitemap": "configured" | "pending-oauth" | "verified", "bingSitemap": "configured" | "pending-oauth" | "verified" }`
- `measurement`: `{ "openai": "sampled" | "ready" | "missing-credential" | "skipped", "claude": ..., "perplexity": ..., "gemini": ..., "ga4": "connected" | "pending-oauth" | "skipped" }`
- `failureReason`: `null` for passed/published runs, otherwise `{ "stage": "preflight" | "research" | "validation" | "build" | "deployment" | "verification", "codes": ["machine-readable-code"], "detail": "concise human-readable explanation" }`

Quarantined records live at `content/quarantine/YYYY-MM-DD.json`; the audit run record remains in `content/runs/YYYY-MM-DD.json`.
