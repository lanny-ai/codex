# The service portfolio — QUEST, the three routes, the formats, the layouts

Build Room members sell a service, and the buyer is buying the person. The portfolio below replaces the e-commerce trio (callout diagram, review card, offer card) with formats built for that.

## QUEST — the persuasion sequence for services

Adapted from Michel Fortin's QUEST formula. **Qualify → Understand → Educate → Stimulate → Transition.**

- **Qualify** — name the situation so the right person says "that's me" and the wrong one scrolls on (§2 trigger; §18 wrong-fit).
- **Understand** — show you know the problem from the inside, in their words (§2 sourced language).
- **Educate** — the mechanism: what you actually do, and why it works when the alternative did not (§3, §4 differentiator).
- **Stimulate** — make the value concrete with a real number, a named result or a real deliverable. Never fear, shame or invented urgency.
- **Transition** — one next step the destination actually delivers.

A static carries QUEST across the picture, the words on it, the primary text and the landing page together. The visible ad must still make sense alone.

## The three routes (the default spread for three concepts)

| Route | What it is | Proof it needs | If the proof is missing |
|---|---|---|---|
| **Case study** | A real client's starting point, what was done, the result, with context | A consented client story with a real number and timeframe, by vault ID | **Blueprint — awaiting real proof**: the layout and the exact evidence to collect; never a placeholder quote. Or a clearly labelled process walkthrough |
| **Quiz / self-assessment** | "Which of these is you?" leading to a real quiz, scorecard or application | A real destination that delivers the assessment | Do not run it until the destination exists; route to Lead Capture |
| **Direct offer** | Scope, what is included, price if shown, terms, CTA | The real offer from §3 | Never invent a discount, deadline, bonus or guarantee |

The routes are a starting spread, not a quota. Three concepts can be three case studies with different personas if the vault is rich and the matrix says so.

## Formats that work for services

From the research: founder to camera with captions; the client testimonial in the client's own words; a screen recording or photo of the real deliverable; lo-fi statics (notes-app lists, "us vs them" tables, listicles, whiteboards). On LinkedIn: Thought Leader Ads promoting the founder's own post, and document ads with a lead form. This release builds the statics; founder video and testimonial video arrive with the video release.

**Ugly is allowed, fake is not.** Native, post-like formats often beat polished ones (practitioner evidence, not controlled tests). A lo-fi format never imitates a private message, a system notification, a platform alert or a fake button.

## The layouts the renderer builds

Every static is one of these layouts in `scripts/render_static.mjs`. Each renders at 1:1, 4:5 and 9:16, recomposed per ratio, with every word from the copy manifest.

| Layout | Use for | Picture layer | Slots |
|---|---|---|---|
| `photo-hook` | Founder-led, proof-led: a face or a real deliverable with one strong line | Member photo, client deliverable, or a generated plate with the member's photo inset | hook, sub, cta, brand |
| `split` | Case study, mechanism | Photo or plate on one side | hook, bullets (2–3 specifics), cta, brand |
| `quote-card` | A real testimonial, real words | Optional real photo of the client (with consent) | quote, attribution (name, role or town as consented), source line, rating only if real, cta |
| `stat` | One real number that carries the claim | Optional plate | number, label, source line, cta |
| `notes` | Lo-fi native: a list in a notes-app style | None | title, 3–6 lines, cta |
| `us-vs-them` | Lo-fi native: the old way vs this way | None | left label, right label, 3–5 rows, cta |
| `offer-card` | Direct offer | Optional photo or plate | offer name, included bullets, price (only if §3 allows showing it), terms line, cta |
| `quiz` | Self-assessment invitation | Optional plate | question, 3–4 lettered options, cta to the real quiz |

Every layout carries the brand kit: the locked colour, the type pair, the name or logo, and the founder's face where the layout has a picture slot and the brief calls for it.

## Value-first variants

20–40% of what a member runs over a quarter should be useful with no ask (a checklist, a mistake list, a myth vs fact), building the retargeting pool. The `notes` and `us-vs-them` layouts do this well with a soft CTA ("Save this"). Mark them `value-first` in the concept table so the test plan judges them on engagement and pool growth, not leads.
