# The tweak bar

## What it is

A panel on the right of the chosen page (a bottom sheet on a phone) with sliders and toggles. It changes only the page token contract (`design-principles.md` §2), so whatever the member lands on can be locked exactly. It runs in the browser with no build step and sends nothing anywhere.

## Putting it in

1. Write `palettes.json` first: **five named palettes** drawn from the taste read and the chosen direction. Name them in the member's world ("Sage", "Harbour", "Dusk", "Linen", "Ink"), not "Palette 1". Each one has all seven colours:

   ```json
   [{"name": "Sage", "bg": "#ffffff", "surface": "#eef3f0", "ink": "#16211c", "muted": "#43524a",
     "accent": "#1f5c46", "accent_ink": "#ffffff", "line": "#cdd8d2"}]
   ```

2. `tweakbar.py add --page Design/landing-page/page/index.html --palettes Design/landing-page/palettes.json --open`
   - `--open` starts the panel open; it doesn't open the browser. Open the page yourself (Claude Code: `open page/index.html` on a Mac, `start` on Windows).
   - The page's own colours come first as "As built".
   - A palette that fails contrast is fixed, and the change is reported in `palette_fixes`. Tell the member what changed.
   - The fonts come from the ten vetted pairs (`assets/font-pairs.json`). In the preview they load from Google Fonts; the final page self-hosts them (`fonts.md`).
   - Only controls the page supports appear. `unsupported` lists the rest; add CSS for a toggle if the member wants it.
3. Open the page in the browser and click **Tweaks** (bottom right). In Claude.ai or Cowork, show the page as an artifact.

## The controls

**Starter set (about twelve, shown first):** colour palette · font pairing · text size (never below the audience minimum) · heading weight · corner roundness · spacing · shadow depth · buttons (solid, outline, pill) · motion (off, gentle, lively) · light or dark · photo treatment · top of the page (split, stacked, full photo) · background (none, paper, grain).

**Show advanced:** heading size steps · line spacing · line length · density · each of the seven colours one by one · the two generic tells (small labels over headings, italic last word), which are off unless the member turns them on knowing what they are.

**Built in:**
- **Shuffle** tries a random combination. It never turns a generic tell on and never drops below the minimum text size.
- **Reset** goes back to the page as built.
- **Save this look** names the current settings, keeps them in this browser, and shows them to copy or download. A look saved in dark mode stays dark: the light colours are saved with it, and the page opens dark.

Each slider shows its value ("21px"). The palette and font menus start on "As built" until the member picks one. On a wide screen the page moves left while the panel is open, so nothing hides behind it.

**Live warnings** sit at the top of the panel:
- text, quiet text and button text under 4.5:1
- the accent under 3:1 against the page
- text under the audience minimum
- a generic tell switched on

## The session rhythm

1. Let the member play. Suggest two or three moves: "try the Harbour palette", "try the bigger text", "try the photo full width".
2. Ask them to save 1–3 looks they like.
3. They click **Copy** and paste the settings into the chat, or **Download** (it saves `tweaks-export.json` to their Downloads folder).
4. `tweakbar.py save --tweaks Design/landing-page/tweaks.json --from <the pasted or downloaded file>`. If they pasted into the chat, write the text to a file first. The save refuses anything that isn't a contract variable, a colour or a known toggle value.
5. Compare the saved looks with the member, one line each. Then mark the final one: `tweakbar.py final --tweaks … --name "Look 2"`.
6. `tweakbar.py apply --page … --tweaks …` writes the look into the page and takes the bar out. Then go to the lock.

## When something isn't on the bar

A change the bar can't make, such as "move the testimonial up" or "a different photo", is a small edit to the page by hand. Make it, then re-run `tweakbar.py add` so the bar shows the new page. Say plainly which changes are hand edits.
