# The quality bar

A small business does not need a big brand. It needs a small one that is clearly chosen, the same everywhere, and easy to read. That is what "professional" means to a buyer, and it is what this session delivers.

## What makes a brand look machine-made

A tell is a default nobody chose. Any one of these is fine when the member's own brand or references call for it. It is a tell when it simply arrived.

| Tell | Do instead |
|---|---|
| Glows, blurred blobs, soft gradients, glass panels | Flat color. One field of the brand color beats any effect. |
| Gradient text, or a gradient across a logo | One solid color for a word that matters, or no emphasis at all. |
| Dot grids, rings, floating shapes, sparkles as decoration | Nothing. Space and type do the work. |
| A purple or purple-to-blue accent | A color from the member's world: their van, their door, their trade. |
| A cream page with a serif headline and a terracotta or sage accent | White, or a real color from their references. |
| Inter, Poppins, Montserrat or another default typeface as the headline | A pairing from `assets/font-pairs.json`, or the typeface their own brand already uses. |
| A drawn symbol from an image model (a swoosh, a leaf, a lightbulb, a shield) | The name set in type. A drawn symbol comes from a designer. |
| Pills, badges and small uppercase labels on everything | Size and space for hierarchy. A label only when it carries information. |
| Emoji as icons | No icon. |
| Five or six bright colors | One or two brand colors, one accent with one job. |
| A different look on every piece | The same logo position, the same two typefaces, the same accent, every time. |
| A logo with a shadow, an outline or a bevel | The flat logo on a plain ground. |
| A stock photo of a handshake, a laptop or a couple on a beach | The member's own photos, or no photo. |

## What makes it look professional

1. **Few parts.** One logo, one or two brand colors, two typefaces, one corner radius.
2. **One job per color.** The accent marks the main button and links, and the one word that matters. Nothing competes with it.
3. **Type with character, set plainly.** The heading face carries the personality. No effects on it.
4. **Generous space.** The clear space around the logo is a rule. Margins are wide.
5. **The same everywhere.** A stranger who has seen the post recognizes the page.
6. **Real things.** Their name, their words, their photos, their colors.

## The floor (these stop a lock)

| Rule | Value |
|---|---|
| Text on its background | 4.5:1 or more |
| Buttons and the accent against the page | 3:1 or more |
| Body text, readers aged 50 and over | 18px or more |
| Body text, general audience | 16px or more |
| Smallest text anywhere | 14px |
| A PNG logo | 600 pixels wide or more (1000 or more is better); a vector file is best |
| The wordmark in use | never under 120 pixels wide on screen, 25 mm in print |
| The small mark | readable at 24 pixels |

`brandkit.py check` measures the contrast pairs and the sizes. It cannot judge taste. You do that, with the list above.

## Your review before the member sees anything

Open the board or the sheet and answer each question honestly. If any answer is no, fix it first.

1. Could this be any other business in their field with the name swapped? If yes, it is not a direction yet.
2. Does every color, typeface and logo choice trace to something the member said or showed?
3. Is there any effect on the page (a glow, a gradient, a shadow)? Remove it.
4. Is the small mark still readable in the 24-pixel circle?
5. Does the logo work in one color on white and on the reverse ground?
6. Are the three directions really three ideas, or one idea in three colors?
7. Is every word on the page the member's own?

## What this session does not do

- It does not draw symbols, mascots or illustrations.
- It does not clear a name or a logo for trademark registration. Say once that a trademark professional does that.
- It does not hand-kern. The wordmark is set with even spacing and any pair you adjust in `logo.kern`. A designer can refine it later from the vector file.
- It does not produce print-ready color values (CMYK or Pantone). A printer or designer converts from the hex values on the brand sheet.
