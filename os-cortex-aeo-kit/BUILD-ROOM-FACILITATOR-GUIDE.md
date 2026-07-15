# Build Room facilitator guide

## Session outcome

By the end of the session, members should understand the AEO publishing loop, install the plugin, begin brand onboarding, and know why quality gates—not content volume—make unattended publishing safe.

## Recommended 60-minute run of show

### 0–8 minutes — Reframe AEO

- AEO is not a formatting trick or a daily-content quota.
- The system earns discoverability through relevant questions, original information, extractable answers, visible evidence, crawlability, and external authority.
- The unit of production is one useful answer page on one authority domain.

### 8–18 minutes — Show the system

Walk through the loop: question data → scoring → research → claim ledger → draft → gates → publish → index → measure → learn.

Emphasize that a failed gate produces no publication.

### 18–28 minutes — Demonstrate the installed example

Show:

1. The answer hub.
2. A direct answer in the opening paragraph.
3. Original contribution and sources.
4. Methodology, author, citations, corrections, sitemap, RSS, and robots.
5. A successful run report and a quarantined-run example.

### 28–40 minutes — Install together

- Mac members run `bash install-mac.sh`.
- Windows members run the PowerShell installer.
- Everyone restarts ChatGPT desktop, installs the plugin, and opens a new task.
- Prompt: `Use $aeo-client-onboarding to set up my brand.`

### 40–52 minutes — Complete intake

Members define their audience, urgent questions, offer, CTA, approved claims, prohibited claims, author, reviewer, domain, and source-of-truth URLs.

Do not collect or display credentials during the group session.

### 52–60 minutes — Commit to the launch sequence

- Complete three supervised publications.
- Review brand fit and evidence before enabling automation.
- Connect Search Console and analytics after the branded site is live.
- Observe the first 14 unattended runs.

## Live-demo prompts

1. `Use $aeo-client-onboarding to explain what information you need from me before creating anything.`
2. `Create my brand configuration, but do not publish yet.`
3. `Score my initial question map and explain the top candidate.`
4. `Run a simulated quality gate on a draft with only two sources.`
5. `Show me the exact report I receive when a run is quarantined.`

## Common questions

**Does this guarantee ChatGPT rankings?** No. It improves the foundations that answer engines can retrieve and cite, then measures directional citation signals.

**Does it create a new website every day?** No. It adds one strong page to one authority domain.

**Can it publish without review immediately?** The member edition should not. Complete three supervised runs first.

**Do members need every API?** No. Sites and research are the core. Search, analytics, and model APIs add feedback and measurement.

**Can it run when the computer is off?** Not as a local automation. Required 24/7 uptime should move to a controlled server runner.
