# OS Cortex AEO Systems

This repository is the install source for **OS Cortex AEO Publisher**, a governed authority-publishing workflow for ChatGPT desktop and Codex.

## Install

Install and sign in to ChatGPT desktop/Codex, then run:

```bash
codex plugin marketplace add lanny-ai/codex --ref main
```

Restart ChatGPT desktop, open **Plugins**, choose **OS Cortex AEO Systems**, and install **OS Cortex AEO Publisher**.

Start a new task with:

```text
Use $aeo-client-onboarding to set up my brand. Do not publish yet.
```

See [START-HERE.md](START-HERE.md) for Mac and Windows workshop instructions, security boundaries, and the supervised rollout sequence.

## Safety model

- Each member uses their own ChatGPT account, computer, website project, and credentials.
- Three supervised publications are required before enabling automatic public publishing.
- A failed evidence, brand, citation, accessibility, build, or crawlability gate quarantines the run.
- No API keys, OAuth tokens, or client content belong in this repository.

Version: 1.0.0
