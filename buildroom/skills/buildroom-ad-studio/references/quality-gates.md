# Quality gates, the reviewer, and release

Five gates, then the member. A gate returns **pass**, **revise** or **unverified**, with the artifact, the region or line, the defect, its consequence and the smallest fix. "Looks good," "10/10" and "looks AI" are not verdicts. No numerical beauty score, no predicted conversion rate. A script that checks structure (the ledger, the renderer's overflow check, the review pack) checks structure, not truth or quality.

## G0 — Brief (Phase 0)

Passes only when:
- **One audience** in one situation (from §2, sourced words preferred).
- **One proposition** (BY) that passes Hegarty's three tests: makes rational sense; makes emotional sense; could work as a rough press ad on its own.
- **One success metric**, defined: cost per qualified lead or booked call, with the counting rule (what makes a lead qualified, where it is counted).
- **Mandatories** recorded: brand kit, never-say claims, wrong-fit audience, platform, required disclosures, destination (live or proposed).

Fails on: two audiences, a proposition that is a tagline, a metric that is platform lead count alone.

## G1 — Concept (Phase 2)

Each concept passes only when:
- The **angle fits in one phrase** and is reused, not reinvented, across its hooks.
- It **survives a change of format** (it would work as a quote card, a notes list or a founder video).
- A reviewer would call the **insight non-obvious** for this market.
- It **differs from the other concepts this cycle, and from the last ten tested** (from §18 / the learning library), on at least one of persona, angle, mechanic, format, setting. Same angle with a new colour or headline is a variant, not a concept.
- Its **proof exists in the vault** by ID, or it is labelled a blueprint.

Then score the survivors on the Cannes Direct weights: **idea 30, strategy 20, execution 20, predicted impact 30**, each with one sentence of reasoning. The score ranks; it does not certify.

## G2 — Copy (Phase 3)

Every line passes:
- **Harry Dry's three tests:** Can I visualise it? Can I falsify it? Could nobody else say it?
- **A number or a named result** in place of every adjective ("booked 11 calls in 9 days," not "amazing results").
- **The hook** states the situation or the benefit in the first line or first glance.
- **Length set by awareness** (see `concept-matrix.md`).
- **Emotion opens, reason closes.**
- **Sourced language** for any line in the customer's voice; any hypothesis-tagged phrase flagged under the ad, never presented as a client's words.
- The Kern or Halbert checks from those references (no em dashes in Kern pieces, one CTA, one reader). A quotation is never restyled: it keeps its exact words and punctuation.
- **Message match:** the landing headline repeats the ad's angle.
- **Every hook names its subject** ("We install your AI workforce," not "We install it").
- **Typography in the words themselves:** curly quotes and apostrophes (’ “ ”), a non-breaking space where a number and its unit must not split ("30 minutes"), answer bands that do not overlap ("2 to 5", "6 to 10").
- **Guarantees word for word** and approximations with their qualifier (see `compliance.md` 4a, 4b).

## G3 — Craft (Phase 6, on the actual exported files)

- A **distinctive brand asset** reads in the first glance.
- The ad **reads on mute** and at phone size: hook, offer and CTA legible without zoom.
- **Safe zones clear** for each ratio (the renderer's report, then the eye).
- **No word on bare picture:** every line sits on the scrim or a solid panel, judged against the real plate, not the placeholder.
- **Legible at phone size in every ratio,** 9:16 included: no body text below the renderer's 30 px floor; if a slot sits at the floor, cut words.
- **No model-rendered price, URL, terms or headline.** Every word matches the copy manifest exactly.
- People: the face is the member's real photo, identity intact; no generated person as the hero; any generated background figure is clearly secondary and disclosed.
- Plates: plausible light, contact, scale and materials; no waxy surfaces, impossible geometry, phantom text, warped hands, stray logos; local colour kept (no orange/teal wash).
- Hierarchy: one dominant message, one proof focus, one CTA; contrast at least 4.5:1 for body text and 3:1 for large text.
- The three ratios are **recomposed**, not cropped blindly.

## G4 — Compliance (Phase 6)

See `compliance.md`. Passes only when:
- No synthetic testimonial, review, rating, result, customer or endorsement; every quote and number traced to the proof vault with source and consent.
- Every claim, including what the **picture implies**, is supported or removed.
- Never-say claims absent; wrong-fit audience not targeted by the copy.
- AI disclosure applied where required; provenance metadata (C2PA) of generated plates not stripped.
- Likeness consent on file for any real person shown.
- No political, election or social-issue content.
- The disclosure sheet entry for the ad is written; the ledger and copy manifest form the audit log.

## The separate reviewer

Required for G3 and G4. Give the reviewer, in a fresh context: the brief, the copy manifest, the proof vault references, the actual exported files (full resolution, plus the contact sheet at phone size), the plates and their prompts, and this file plus `compliance.md`. Do **not** pass your opinion of the work or the verdict you hope for.

The reviewer returns, per ad: G3 verdict, G4 verdict, and for each issue the file, region, defect, consequence, severity and smallest repair; plus what it could not inspect. A reviewer that saw only prompts or thumbnails cannot pass anything.

Where the host has no subagents, run a labelled fresh-context review pass: re-read only the inputs above, review, and say in the record that the review was not independent.

## Repairs

Fix the smallest layer that fixes the defect: copy, then layout, then the plate. Never regenerate a plate to fix a word. A wrong plate is fixed at its prompt or reference, once, before anything is built on it. At most **two repair passes per ad** by default (the member can change this); keep the count in the ledger across resumptions. When the cap or budget is reached, deliver what passed and name exactly what did not.

## Release states

- `briefed` — G0 passed.
- `concepted` — G1 passed, member picked.
- `copy_approved` — G2 passed, member approved each ad's copy.
- `rendered` — every file exists, renderer checks pass.
- `reviewed` — G3 and G4 pass on every file in the kit, recorded by the reviewer.
- `approved` — the member approved each ad.
- `kit_ready` — the launch kit is built.
- `partial` / `blocked` — useful work exists; the exact missing piece is named.

None of these means "will convert." Only the member's own results, read honestly, say that.
