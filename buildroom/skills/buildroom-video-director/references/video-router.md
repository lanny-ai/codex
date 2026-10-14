# Video router: jobs, models, providers, spend

## Jobs to models

Model rosters and prices move every few months. These are the defaults as of October 2026 (from the Build Room advertising research, vendor-adjacent comparisons). Resolve the exact model ID on the provider at the time (`gen.py --probe`, the provider's model list); a family name here is not an API identifier.

| Job | Default family | Notes |
|---|---|---|
| B-roll scene, no people, from text | **Kling** (current version) or **Seedance** | Kling for cheap, plentiful variants; Seedance when the shot must match a reference frame |
| B-roll that must match a plate or a real photo (first frame) | **Seedance** (image-to-video) | Pass the first frame as a public https URL, or use the Higgsfield MCP to upload a local file |
| Consistent object or place across several shots | **Seedance** with the same references | One reference per role |
| Dialogue with lip sync, generated | **Veo** | Only for a non-person subject or a clearly secondary figure; never a generated presenter as the hero |
| The member's avatar twin | **HeyGen** (avatar the member created, voice the member recorded) | Scale variants only (new hooks on a proven script), written consent on file, never the first video, never a testimonial |
| Still plates, title backgrounds | **Nano Banana Pro** / **Seedream** | Through the Ad Studio's image route (same `gen.py`) |
| End cards, title cards, lower-thirds | **The renderer** (`render_static.mjs`) | Every word set from the manifest; never a model |
| Captions | **SubMagic** (polish) or the director's own burn | See `captions.md` |
| Sora | **Never** | Discontinued in 2026 |

## Providers

Higgsfield (default; MCP for interactive work, API through `gen.py`), Kie.ai (pay-as-you-go), HeyGen (twin), SubMagic (captions). fal.ai is not routed. Sign-up links, the disclosure, keys and probing: `provider-signup.md`.

## Live prices, never invented

Before each batch: read the per-second or per-job price for every model you will use from the provider, write `prices.json` with the source and date (`"per_second"` for video, `"per_job"` for a fixed price), run `gen.py --dry-run jobs.json --prices prices.json`, show the member every request and the total in the provider's own units, and authorise that total plus the repair allowance once (`ledger.py authorize`). Do not convert credits to dollars unless the provider publishes the rate.

## The ledger sequence (every paid call)

```sh
S=.claude/skills/buildroom-video-director/scripts     # or .codex/skills/…; resolve the real path
P=videos/2026-10-install-explainer/project.json
python3 $S/ledger.py init $P --cycle 2026-10
python3 $S/ledger.py gate $P --gate G0 --verdict pass --by producer --ref brief.md        # then G1 (beats), G2 (script)
python3 $S/ledger.py plan $P --asset-id BROLL-3 --provider kie --model <id> --prompt-ref broll/3.prompt.txt --kind broll
python3 $S/ledger.py plan $P --asset-id CAPTIONS-916 --provider submagic --model "<template>" --prompt-ref edit.json --kind captions
python3 $S/gen.py --dry-run jobs.json --prices prices.json                                  # show the member
python3 $S/ledger.py authorize $P --provider kie --cap 120 --units credits --note "member approved quote, session 2026-10-14"
python3 $S/gen.py jobs.json --project $P --prices prices.json
python3 $S/ledger.py ad $P --ad V1 --concept V1 --layout sales-explainer --spec edit.json --renders renders/V1_16x9.mp4 renders/V1_9x16.mp4 --assets BROLL-3
```

An avatar twin is planned with `--kind twin --consent-ref "<where the signed consent is>"`; the ledger and `gen.py` both refuse a twin without it. A job that times out is `unknown` until reconciled (`gen.py --resume`); never resubmit blind.

## Jobs file (video)

```json
{"provider": "kie", "jobs": [
 {"key": "2610.V1.broll3.r0", "asset_id": "BROLL-3", "kind": "video", "model": "<resolved id>",
  "prompt_file": "broll/3.prompt.txt", "aspect_ratio": "9:16", "duration": 5, "out": "broll/3.mp4"}]}
```

Generate at the tallest ratio you will deliver (9:16 for ads and shorts, 16:9 for long-form); the edit crops with a focus point for the others.
