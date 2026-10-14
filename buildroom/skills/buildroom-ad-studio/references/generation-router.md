# Generation router — jobs, models, providers, setup

Read before Phase 4. This release generates **still images only**: plates (scenes, settings, objects, deliverable mock-ups) that the renderer composes with the member's real photos and the approved words. Video routes arrive with the video release.

## The order of preference (before any money is spent)

1. **Real asset** from the proof vault: the member's photo, a client deliverable, a real screenshot. Free, true, and the most memorable.
2. **Lo-fi layout** the renderer builds with no picture at all (`notes`, `us-vs-them`, `quote-card` without photo, `stat`, `offer-card`).
3. **A generated plate**, only when the concept needs a setting or object the member cannot photograph this week.

## Jobs to models (still images)

| Job | Default model family | Notes |
|---|---|---|
| Scene or setting plate, no people (an office at dusk, a clinic front desk, a kitchen table with a planner) | **Nano Banana Pro** | Strongest prompt adherence and composition control in 2026 comparisons; empty of people by default |
| Object or deliverable mock-up (a printed report, a planner, a phone showing a generic screen) | **Nano Banana Pro** | Never a real client's data; never a fake dashboard with results |
| Physical text on a real surface (a handwritten note, a whiteboard) where the writing is part of the photo | **Nano Banana Pro** | Exact words specified; checked letter by letter; the CTA and any price still go in the renderer layer |
| Cheaper volume plates (three settings for three hooks) | **Seedream** (current version on the provider) | Reported at roughly a third of the price per image †; check the live price |
| Member's real photo placed into a generated setting | **Renderer first** (photo framed or inset over the plate, no generation). Generative edit only with written likeness consent and a reason | An identity-altering edit of a real person is a likeness use; record consent, preserve identity, disclose as AI-edited |
| Prices, URLs, terms, headlines, CTAs, logos | **Never a model** | The renderer sets every word |
| A photoreal person as the hero | **Not offered** | Founder decision: real faces only |
| Video (B-roll, founder twin, talking head) | **Video Director** | `buildroom-video-director` produces every video; the Ad Studio hands it the concept |
| Sora | **Never** | Discontinued in 2026 |

Model names and versions move every few months. Resolve the exact model ID on the provider at the time (`gen.py --probe` and the provider's model list); a family name in this table is not an API identifier.

## The providers

| Provider | Why | How it is reached | Billing | Keys in `.env` |
|---|---|---|---|---|
| **Higgsfield** (default) | One account for Nano Banana Pro, Seedream and the video models the next release uses; a hosted MCP for interactive sessions; a pay-per-generation API for scripts | **Interactive:** the Higgsfield MCP (`https://mcp.higgsfield.ai/mcp`), connected once in Claude Code or Codex; it handles sign-in and uploads. **Scripted:** `scripts/gen.py --provider higgsfield` | Credits on the member's plan; the MCP deducts credits even on "Unlimited" plans † | `HIGGSFIELD_API_KEY`, `HIGGSFIELD_API_SECRET` |
| **Kie.ai** | Pay-as-you-go credits for many models, no subscription; for members who generate a few plates a month | `scripts/gen.py --provider kie` | Prepaid credits; reviews report failed jobs are not charged † | `KIE_API_KEY` |

fal.ai is not routed in the Ad Studio (founder decision, October 2026). Members of the Video Engine elective may already hold a fal.ai key; it is not used here.

HeyGen (founder twin, with consent) arrives with the video release.

## The setup step (first time only, Phase 4)

Say it plainly, one step at a time:

1. "Your ads need N generated pictures this month; the rest use your photos and layouts. To make those, you need an account with one picture service. I recommend **Higgsfield**; if you'd rather pay only for what you use, **Kie.ai**."
2. If they have no account, give the sign-up link and the disclosure exactly as `provider-signup.md` sets them out, with the plain route next to it.
3. Keys: follow `provider-signup.md` (the key goes in `.env`, never in chat; `--probe` once).
4. Interactive Higgsfield: offer to connect the MCP instead (`claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp` in Claude Code; the Codex equivalent in its MCP settings). Sign-in happens in the browser.
5. Renderer: Node and Chromium. `npm i playwright` once in the ads folder and `npx playwright install chromium`, or set `CHROME_PATH` to an installed Chrome or Edge.
6. Record the provider, the monthly cap (in the provider's own units) and likeness consent in §18.

## Live prices, never invented

Before each batch:

1. Read the current per-image price for each model you will use from the provider's pricing page or account, and write `prices.json`:
   ```json
   {"checked_at": "2026-10-14", "source": "kie.ai pricing page",
    "kie": {"nano-banana-pro": {"per_image": 18, "unit": "credits"}},
    "higgsfield": {}}
   ```
2. `gen.py --dry-run jobs.json --prices prices.json` shows each request and the total **in the provider's own units**. Do not convert credits to dollars unless the provider publishes the rate; if it does, quote the dollar figure with its source.
3. The member authorises the total plus the repair allowance once, as a cap in those units. The ledger refuses anything above it.

## Provider shapes

`gen.py` keeps each provider's request and response shape in one config block (`PROVIDERS`). The shapes were written from the providers' public descriptions in October 2026 and could not be checked against live docs from the build environment. `--probe` makes one harmless authenticated call per provider and prints what came back; if a field name is wrong, fix it in `PROVIDERS` once. Nothing else changes.
