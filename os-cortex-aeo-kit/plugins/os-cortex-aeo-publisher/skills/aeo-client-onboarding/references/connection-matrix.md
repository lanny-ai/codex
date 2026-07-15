# Connection matrix

| Connection | Purpose | Launch requirement |
|---|---|---|
| ChatGPT desktop/Codex | Local implementation and scheduled runs | Required |
| Sites plugin | Build, publish, deploy, and verify the authority site | Required |
| Web research | Current question and primary-source research | Required |
| Domain DNS | Branded canonical hostname | Required for branded launch |
| Google Search Console OAuth | Queries, indexing status, and sitemap verification | Recommended after site launch |
| Bing Webmaster OAuth | Bing/Copilot signals and crawl diagnostics | Recommended after site launch |
| IndexNow key | Notify participating search engines | Recommended |
| GA4 OAuth | AI referrals, engagement, and conversions | Recommended |
| OpenAI API key | Directional citation sampling | Optional |
| Anthropic API key | Claude citation sampling | Optional |
| Perplexity API key | Perplexity citation sampling | Optional |
| Gemini API key | Gemini grounded-answer sampling | Optional |

Never store credentials in Git-backed files. Record only `connected`, `pending-oauth`, `missing-credential`, `skipped`, or an equivalent non-secret status.
