# Type and colour

## The numbers (the quality floor)

| Rule | 50+ audience (default) | General audience | Source |
|---|---|---|---|
| Body text | **18px or more** (19–20 is better) | 16px or more | [official] GOV.UK uses 19px; [data] NN/g on older readers; [practitioner] consensus |
| Smallest text anywhere | 14px | 14px | [practitioner] |
| Body line height | 1.5–1.6 | 1.5–1.6 | [official] WCAG 1.4.8 |
| Line length | 60–70 characters (`--measure: 64ch`) | 50–75 | [data] Baymard |
| Text contrast | **4.5:1** or more | 4.5:1 | [official] WCAG 2.2 1.4.3 |
| Large headings (24px+, or ~19px bold) | 3:1 minimum; aim for 4.5:1 | 3:1 | [official] WCAG 1.4.3 |
| Buttons and borders against the page | 3:1 | 3:1 | [official] WCAG 1.4.11 |
| Button height | **44–48px** | 44px | [official] WCAG 2.5.5 (AAA) / 2.5.8 (24px AA) |
| Motion | a reduced-motion setting, always | always | [official] WCAG 2.3.3, technique C39 |

`design_check.py` enforces the body size, the 12px floor and the 4.5:1 contrast as FIX items. The tweak bar warns live.

## The ten vetted font pairings

All are on Google Fonts, under the SIL Open Font License or Apache 2.0 [official, Google Fonts FAQ: commercial use and self-hosting allowed]. Check the licence tab on each family's page before locking; only Atkinson Hyperlegible Next was confirmed from source in this research.

| Pairing | Heading / body | Character |
|---|---|---|
| **Sturdy & Clear** | Young Serif / Atkinson Hyperlegible Next | warm, sturdy; the body face was built for low-vision reading. **The default for a 55+ audience.** |
| **Trusted Advisor** | Libre Franklin / Lora | confident headline, soft bookish body; advisors and authors |
| **Dependable** | Bitter / Source Sans 3 | friendly slab, practical; trades turned consultants |
| **Wide & Modern** | Archivo / Literata | wide, assertive headline over a very readable serif |
| **Editorial** | Epilogue / Newsreader | magazine feel, without the cream-and-italic cliché |
| **Approachable** | Zilla Slab / Karla | bold slab with personality; coaching brands |
| **Story-led** | Alegreya / Alegreya Sans | matched family, calligraphic warmth; wellness, story-led |
| **Energetic** | Bricolage Grotesque / Hanken Grotesk | characterful; getting popular, so use with restraint |
| **Sober Authority** | Merriweather / Fira Sans | serious; finance and legal |
| **Quiet Luxury** | Instrument Sans / Crimson Pro | crisp sans headlines over a classic text serif |

**Avoid as defaults** [practitioner]: Inter for everything; an italic display serif as the headline signature (Instrument Serif, Fraunces italic, Playfair italic); Space Grotesk on non-tech businesses; Poppins or Montserrat. Any of them is fine when the member's references call for it.

**Self-host the fonts.** In January 2022 a Munich court fined a site €100 for loading Google Fonts from Google's servers without consent, because visitors' IP addresses were passed to Google. The ruling is first-instance only, but self-hosting is faster anyway. `design_lock.py` writes `fonts.md` with where to get the files; `design_check.py` reminds the member (a WATCH) while the page still loads them from Google.

**Slides use a font every computer has** (Arial, Georgia, Verdana or Calibri), because a deck opens on other machines. `slides.json` names it.

## Building a palette

1. Start from the taste read: `taste_vault.py read` reports the background families, the accent families and the light/dark split of the references. The colours themselves are in each reference's `colours`; for JPEGs, look and name them with `react --colours`.
2. Pick **one dominant colour** (usually the background or a large colour field) and **one accent**. The accent does one job: the main button and links.
3. Fill in the other five: surface (a step off the background), ink (near-black, or near-white on dark), muted (a quieter ink, still 4.5:1), accent ink (the text on the accent), line (a soft border).
4. Check every pair: ink/bg, muted/bg, ink/surface, accent_ink/accent at 4.5:1, and accent/bg at 3:1. `tweakbar.py add` does this and fixes failures. `dslib.shade_to_contrast` gives the nearest passing shade.
5. Five palettes for the tweak bar: the chosen direction's own, two close variations, and two braver ones still drawn from the references.
6. A dark palette is the page's `[data-theme="dark"]` block, checked the same way.

Colour psychology ("blue means trust") is **folklore**. Colour comes from the member's references and their world.
