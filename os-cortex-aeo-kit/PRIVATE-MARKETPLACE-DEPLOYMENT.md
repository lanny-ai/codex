# Private marketplace deployment

The ZIP works for live teaching and local installation. The durable distribution repository is `https://github.com/lanny-ai/codex`.

## Recommended repository model

- Repository: `lanny-ai/codex`
- Current access: public
- One tagged release for each tested version
- No API keys, OAuth tokens, client projects, or client content
- Members receive repository access plus the Mac or Windows installer instruction

After the package contents are committed at the repository root, members register it directly:

```bash
codex plugin marketplace add lanny-ai/codex --ref main
```

They then restart ChatGPT desktop and install **OS Cortex AEO Publisher** from the **OS Cortex AEO Systems** marketplace.

Keep the repository public if frictionless Build Room distribution is intentional. Make it private if access is a paid-member benefit; private installation then depends on each member having GitHub access and working Git credentials.

Before announcing the repository, verify that `.agents/plugins/marketplace.json`, `plugins/os-cortex-aeo-publisher/.codex-plugin/plugin.json`, and both bundled skills are present on `main`. The repository currently contains only its starter README, so the marketplace is not installable until this package is committed.

## Two editions

**OS Cortex Client Edition**

- Guided onboarding by your team
- Domain and data connections
- Three supervised publications
- Daily automation enabled after acceptance
- Ongoing measurement and optimization

**Build Room / Platinum Member Edition**

- Self-serve plugin and teaching materials
- Supervised publication default
- Optional office-hours support
- Automatic public publishing enabled only after the member completes acceptance

Workspace sharing is not the right primary channel for independent accounts. A Git-backed marketplace keeps installation consistent across unrelated personal and business ChatGPT accounts.
