# Taking in a brand the member already has

The rule: **record it exactly, check it, fill only the gaps, and say what you added.** You are not improving their brand. You are making it usable by every session.

## What to ask for

Ask once, and take whatever comes:

"Send me whatever you have: logo files (any format), a brand guide if a designer gave you one, your color codes, the names of your fonts, or just your website address. If all you have is the logo on your website, that is fine."

Put files in `Design/Brand/`: logos in `logo/`, fonts in `fonts/`, anything else (a guide PDF) at the top.

## Reading each kind of thing

Run `brandkit.py read <files>` on everything. It writes nothing.

| They gave you | What to do |
|---|---|
| **A vector logo (.svg)** | The best case. `read` lists its colors, and says if it carries live text or wraps a picture. Those colors are the brand colors. |
| **A PNG logo** | `read` gives its size, whether the background is transparent, and its main colors. Under 600 pixels wide is too small: ask for the original. |
| **A JPEG logo** | Usable on its own background only. Open it, name the colors by eye, and ask for an SVG or a transparent PNG. |
| **A .ai, .eps or .psd file** | Cannot be placed on a page. Ask the member or their designer to export an SVG and a PNG. |
| **A brand guide (PDF)** | Read it yourself. Take the color values, typeface names, logo rules and any "never do" lines word for word. Guides outrank everything else. |
| **Color codes in a message** | Record them as given. If they gave names ("our navy"), keep the names. |
| **Only a website** | Save the page or its stylesheet and run `read` on it: it lists colors and typefaces by how often they are used. The most-used dark color is usually text, the most-used saturated color the accent. Confirm every one with the member; set `"source": "website"`. |
| **A Design System from the Website Design Studio** | `read Design/System/tokens.json`. Keep its colors and typefaces; add the logo, the palette names and the brand sheet. |

## The palette, then the working colors

1. `palette` holds the brand's own colors exactly as given: name, hex, role, and where each came from ("brand guide, page 2", "the logo file", "your website header").
2. `brandkit.py roles <hex> <hex> …` proposes the seven working colors every page needs (page, panel, text, quiet text, accent, text on the accent, lines). Add `--dark` if their brand lives on a dark ground.
3. It lists everything that is **not literally theirs** under `not_the_brands_own`. Typical cases, and what to say:
   - A near-black for text: "Your navy is the logo color. For long text I am using a darker shade of it so it is easy to read."
   - A brand color too faint for a button on white: "Your yellow stays in the brand for highlights and large areas. Buttons use the navy, because yellow on white is hard to see."
   - Panel, quiet text and line shades: "Three quiet shades worked out from your colors, for panels and borders."
4. If `check` reports a contrast FIX, take the shade it suggests for the text role and leave the brand color itself in `palette` untouched.

## Typefaces

- Named in a guide: use them.
- Not known: `read` on the logo SVG or the website often names them. Otherwise ask, or describe what you see ("a serif with strong slabs") and offer the closest pairing in `assets/font-pairs.json` as a stand-in, clearly called a stand-in.
- A Google Font: `brandkit.py fonts Design/Brand/kit.json` downloads the files and sets the license to `google`.
- A font they bought: ask for the files and set `"license": "bought"`. They confirm the license covers web pages and social images.
- A font that came with their computer (Georgia, Arial): `"license": "system"`. It needs no files.
- Never leave the license as `unknown` without telling the member what that means.

## The logo

Name each file by the ground it is made for:

```json
"logo": {"kind": "files", "on_light": "logo/acme.svg", "on_dark": "logo/acme-white.svg",
         "mark_on_light": "logo/acme-mark.svg", "mark_on_dark": "logo/acme-mark-white.svg"}
```

`check` reports what is missing. Tell the member in plain words and give them the sentence to send their designer:

- **No version for dark backgrounds:** "Please send the logo in white, or reversed, for dark backgrounds, as an SVG."
- **No small mark:** "Please send a square version for profile pictures, as an SVG."
- **Too small or no transparent background:** "Please send the original vector file, or a transparent PNG at least 1000 pixels wide."

Until the missing file arrives, the kit still locks. Wherever the missing version would go, the business name is set in the heading typeface, and the brand sheet says so. You never recolor, redraw, trace or regenerate their logo to fill the gap.

If the member has no small mark and does not want to ask a designer, you may offer a typed mark for profile pictures only (one to three letters in their heading typeface on their brand color). That is a new thing, so show it and get a yes; it is added as a wordmark kit with their own colors and typeface and `"source": "uploaded"` stays.

## What to tell the member at the end

Three short lists, before they confirm:

1. **Exactly yours:** the logo files, these colors, these typefaces.
2. **Added by me:** each working shade and why.
3. **Missing:** what to ask their designer for, with the sentence to send.
