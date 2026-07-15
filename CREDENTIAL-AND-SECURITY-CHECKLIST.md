# Credential and security checklist

## Rules

- Use client-owned accounts and least-privilege scopes.
- Store secrets in environment or platform secret storage.
- Never place keys in prompts, Git, screenshots, run reports, or shared worksheets.
- Never reuse credentials between clients.
- Record connection status, never secret values.
- Rotate any credential accidentally exposed.

## Core setup

- [ ] ChatGPT desktop/Codex installed and signed in
- [ ] Sites plugin installed
- [ ] Client-owned Sites project created or selected
- [ ] Dedicated Git project created
- [ ] Branded domain configured
- [ ] Public access and HTTP 200 verified

## Feedback connections

- [ ] Google Search Console OAuth
- [ ] Bing Webmaster OAuth
- [ ] IndexNow key hosted
- [ ] GA4 OAuth and conversion events

## Optional citation sampling

- [ ] OpenAI API key and spending limit
- [ ] Anthropic API key and spending limit
- [ ] Perplexity API key and spending limit
- [ ] Gemini API key and spending limit

## Automation safety

- [ ] Three supervised runs passed
- [ ] Public auto-publishing explicitly authorized
- [ ] Failed gates quarantine instead of publishing
- [ ] Rollback owner named
- [ ] Schedule and timezone confirmed
- [ ] Computer uptime expectation understood
- [ ] Monthly key review and cost review scheduled
