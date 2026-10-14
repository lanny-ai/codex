# Typography, layout and the controlled type layer

Adapted from the `create-ads-with-agents` skill's typography and UI/UX reference (see `source-credit.md`) and fitted to `scripts/render_static.mjs`. Design for a distracted person on a phone: the situation or offer and the next step are understood before style is noticed.

## The rule

**The image model never sets a word.** Every headline, price, URL, term, CTA, quote and logo is placed by the renderer from the approved copy manifest, in the brand's real fonts. A plate may contain physical writing only when that writing is the photo's subject, and then it is checked letter by letter.

## Hierarchy

One dominant message, one proof focus, one CTA. Reading order by size, weight, contrast and space: hook → proof → CTA. Group price and terms together. Keep the brand asset (face, colour, name) in the first glance. If something important disappears at phone size, cut words; do not shrink them.

## The type system

- One display face for hooks, numbers and quotes; one body face for everything else; two or three weights. The brand kit names them (§18). Without a brand system, a strong serif display (Fraunces, Source Serif) with a clean sans body (Inter, Manrope, DM Sans) is a safe default. Check the font's licence before using it in ads.
- Fonts load from Google Fonts by name, or from local files given in the spec (`brand.font_files`): a single file, or a list of `{"src", "weight"}`. Local files are required for a licensed brand font and for any offline machine. The render report warns when a font fell back.
- Sentence case. Deliberate line breaks. No long all-caps passages, outline text, novelty 3D type or more than two families.
- Contrast: body text at least 4.5:1 and large text at least 3:1 against its background (WCAG 2.2 as a legibility benchmark, not a certification). The renderer reports text and CTA contrast for solid backgrounds; over photos, the scrim does the work and the reviewer checks by eye.

## Ratios and recomposition

| Ratio | Size | Where it runs | Safe zone kept clear by the renderer |
|---|---|---|---|
| 1:1 | 1080 × 1080 | Feed | 5.5% each side |
| 4:5 | 1080 × 1350 | Feed (the default for Meta feed) | 5% top and bottom, 5.5% sides |
| 9:16 | 1080 × 1920 | Stories and Reels | 14% top, 35% bottom, 6% sides (the Reels overlay, the strictest) |

The 9:16 bottom third is covered by the platform's caption and buttons in Reels; the renderer keeps every word above it and lets the picture or brand colour fill it. These margins are the commonly cited Reels zones (14/35/6) †; check them against Meta's current placement guide once per quarter and change `SAFE` in the renderer if they moved.

Each ratio is **recomposed**, not cropped: the layout moves the picture, the type scale and the stacking per ratio. The type shrinks to fit (down to a floor per slot); a slot at its floor is reported, and the fix is fewer words.

## The layouts

See the table in `service-portfolio.md`. The spec format is in the header of `scripts/render_static.mjs`. Picture placement per layout:

- `photo-hook` — full-bleed picture, a scrim dark behind the words and the CTA and clear in the middle so the picture reads; optional circular inset of the member's real photo next to the CTA.
- `split` — picture on the left 44% (1:1, 4:5) or the top 30% (9:16).
- `offer-card` — optional picture band across the top third.
- `quote-card`, `stat`, `quiz` — solid brand background; an optional plate sits behind a near-solid veil.
- `notes`, `us-vs-them` — no picture; the format is the picture.

## The AI label

When `ai_label` is true in the spec, the renderer sets "Includes AI-generated imagery" inside the safe zone, under the CTA, readable at phone size. Required when a generated person appears (New York, EU); recommended in the disclosure sheet for any generated plate. Never shrink it below the size the renderer sets, never hide it behind a platform overlay.

## No fake interface

The CTA is a labelled shape that matches the real button's action. No fake play buttons, close boxes, notifications, chat bubbles, checkboxes that look tappable, or system warnings. The `notes` layout's boxes are list marks on paper, not controls; the `quiz` options are lettered rows leading to a real quiz.

## Final checks (reviewer, on the exported files)

- First glance says the situation or the offer.
- Face, proof and words readable at phone size (about 360 px tall on the contact sheet).
- Every word matches the copy manifest; punctuation and symbols survived.
- Nothing important in the safe-zone margins (check the `_safe.png` overlays).
- Contrast holds over the actual picture.
- No stray text, logos or interface in the plate.
