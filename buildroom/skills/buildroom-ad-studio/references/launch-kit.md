# The launch kit, the copy manifest and the small-budget test

## The ads folder

```
ads/2026-10/
  brief.md             G0: GET / WHO / TO / BY, metric, mandatories
  matrix.md            Phase 1 grid, entry points, covered cells
  concepts.md          Phase 2 concept table as approved
  copy-manifest.json   every approved word, per ad (below)
  specs/               one renderer spec per ad (C1-H1.json …)
  plates/              prompts (*.prompt.txt) and generated plates
  prices.json          live prices with source and date
  jobs.json            gen.py jobs
  project.json         the ledger
  renders/             <ad>_<ratio>.png, _safe.png overlays, reports
  review/              contact_sheet.html, checklist.md, reviewer verdicts
  kit/                 the upload-ready kit
ads/learning-library.csv   one row per ad per cycle, results filled in later
```

## The copy manifest (`copy-manifest.json`)

The single record of approved words. The renderer's specs must match it exactly; `review_pack.py sheet` flags any difference.

```json
{
 "cycle": "2026-10",
 "destination": "https://example.com/book",
 "budget": {"monthly": "$1,500", "test_share": "20%"},
 "concepts": [
  {"id": "C1", "angle": "No-shows are a follow-up problem", "angle_slug": "no-shows",
   "persona": "solo clinic owner", "awareness": "problem-aware", "mechanic": "confession",
   "route": "case-study", "layout": "photo-hook", "value_first": false, "proof_ids": ["P-03"],
   "hypothesis": "Owners who blame lead volume respond to a follow-up reframe; win = cost per qualified lead below the other two",
   "landing_headline": "Stop losing booked calls to silence"}
 ],
 "ads": [
  {"id": "C1-H1", "concept": "C1", "hook_tactic": "confession", "layout": "photo-hook",
   "copy": {"hook": "…", "sub": "…", "cta": "Book a 20-minute call"},
   "primary_text": "…", "headline": "…", "description": "…", "cta_button": "BOOK_NOW",
   "url": "https://example.com/book",
   "generated": [{"asset": "PLATE-C1", "provider": "higgsfield", "model": "<resolved id>"}],
   "people": [{"who": "founder", "consent": "§18 likeness consent 2026-10-14"}],
   "claims": [{"claim": "9 booked calls in the first month", "proof": "P-03"}],
   "ai_label": false}
 ]
}
```

`copy` uses the slot names of the ad's layout (see the renderer header). `cta_button` uses the platform's button names (BOOK_NOW, LEARN_MORE, SIGN_UP, APPLY_NOW, GET_QUOTE, DOWNLOAD, CONTACT_US).

## Naming

`YYMM_<concept>-<angle-slug>_<hook>-<tactic>_<layout>_<ratio>.png`, for example `2610_C1-no-shows_H1-confession_photo-hook_4x5.png`. Use the same name, without the ratio, as the ad name in Ads Manager. Every attribute can then be pivoted in reporting, and the learning library joins results to concepts by name.

## What the kit holds

Built by `review_pack.py kit`, only when the ledger says every ad passed G3 and G4 and was approved:

- `ads/` — every approved ad in every ratio, named as above.
- `ads.csv` — per ad: name, files, primary text, headline, description, CTA button, and the URL with UTM parameters (`utm_source=meta`, `utm_medium=paid_social`, `utm_campaign=YYMM_<concept>`, `utm_content=<ad name>`).
- `landing-headlines.md` — one angle-matched headline per concept for the landing page (message match). Each one that needs a page change becomes a §13 row.
- `test-plan.md` — the plan below, filled in.
- `disclosure-sheet.md` — per ad: generated imagery, real people and consent, AI label, claims and proof IDs, review verdicts (see `compliance.md`).
- The cycle's rows appended to `ads/learning-library.csv`.

A `--preview` kit (gates open) is labelled `NOT-READY.txt` and never enters the learning library. Never hand a preview to a member as upload-ready.

## The small-budget test plan

At $300–$3,000 a month, statistics are mostly out of reach, so the plan is honest about it:

- **Monthly cycle.** One brief, two or three genuinely different concepts, two or three hooks on each, 10–14 days.
- **About 20% of the budget** in Meta's creative testing tool (it reportedly takes 2–5 ads, equal split †) or one small sandbox ad set; the rest stays on what works. On a first cycle, put the remainder behind the concept with the strongest proof.
- **Judge on the account's own baseline** (the first cycle sets it), not internet benchmarks: click-through rate, cost per lead and **cost per qualified lead from the CRM**, using §18's counting rule. Instant forms produce more leads of lower quality; judge them on qualified rate.
- **Diagnose by layer.** Weak CTR with good engagement → the offer or CTA. Good CTR, weak conversion → the landing page (message match). Leads but few qualified → the angle attracts the wrong reader. Kill an angle only after two or three differently hooked executions of it fail.
- **Mix.** About 60–70% new concepts and 30–40% iteration at this volume (an inference, not a sourced figure), and 20–40% value-first ads with no ask over a quarter.
- **Fatigue by frequency against audience size,** not spend: a small local audience saturates fast. Refresh with a new hook or concept on the same brand platform, never a colour swap.

## The learning library

`ads/learning-library.csv`, one row per ad per cycle: cycle, ad name, concept, angle, persona, awareness, mechanic, hook tactic, layout, hypothesis, then spend, impressions, CTR, leads, qualified leads, cost per qualified lead, verdict, failed layer, next action. The kit writes the first ten columns; the member or the Funnel Scorecard fills the rest after the test. Next month's brief starts from it. That handoff, results back into the next brief, is the part even agency tools leave manual; it is the studio's edge.
