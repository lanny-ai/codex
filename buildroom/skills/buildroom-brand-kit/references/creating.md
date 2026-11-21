# Building a brand from nothing

The member has a name and a business, and no look. You are going to give them a small, real identity in one session: a logo set in type, a tight palette, two typefaces, and proof that it works in use. The work is choosing, not decorating.

## 1. The brief

Read §1 to §4 and §17 first. Then ask only what the Business File does not answer, one question at a time, in plain words:

1. "If a stranger saw your page for three seconds, what three words should come to mind?"
2. "What must you never look like?" (a bank, a tech startup, a discount shop)
3. "Name two or three businesses, in any field, whose look you like. What exactly do you like about each?"
4. "Where will people see your brand most: LinkedIn, your website, a van, printed proposals?"
5. "Do you have photos of yourself at work that you like?"

Never ask them to describe their taste in design words, and never ask for a favorite color. If they offer one, ask where it comes from.

If you can read web pages, look at up to three competitors they name. Note each one's ground, accent and typeface style in a line. The directions must not look like them.

Then write the brief back in four lines and get a yes: who it is for, the three words, what it must not be, where it lives. Save it as `Design/Brand/brief.md`.

## 2. Where a direction comes from

A direction is an idea about this business, not a color scheme. Find it in what they said:

- **Their world.** The tools, places and objects of their trade and their clients' trades: a ledger, a workshop sign, a brass door plate, a harbor chart.
- **Their manner.** Blunt, careful, warm, exacting.
- **Their buyer's age and eyes.** Readers over 50 need size and contrast before anything else.
- **What they admire,** and specifically what about it.

Color comes from that world. "Blue means trust" is folklore; the color of their van is a fact.

Give each direction a short name, one sentence on why it suits this business, and one line on what it comes from. If you cannot write the second line truthfully, drop the direction.

## 3. Three that are really different

Each direction settles four things. Any two directions must differ on at least two of them (`brandkit.py board` refuses otherwise):

| Axis | Range |
|---|---|
| **Ground** | white · a true color from their world · dark |
| **Accent** | a different hue family in each, or one direction with no bright accent at all |
| **Heading typeface** | serif · slab · wide sans · a calm sans, from `assets/font-pairs.json` |
| **Logo treatment** | as typed, capitals, or lowercase · name alone or with the small mark · the mark on a square, a circle, or bare |

A useful spread: one quiet and classic, one sturdy and plain-spoken, one darker or bolder. Never three colorways of one layout.

## 4. Color

- One or two brand colors. One accent with one job. A third strong color only with a named role ("highlights on dark only").
- Fill all seven working colors (`kit-file.md`). `brandkit.py roles` gives a checked starting set from one or two hex values.
- Name the brand colors in the member's language ("Van Green", "Ledger Ink"). Names make a palette theirs and make it easy to brief.
- Avoid the defaults listed in `quality-bar.md` unless their own references call for them. `board` and `check` print a LOOK for a cream page, a purple accent and a default typeface.
- Check the reverse ground. If the accent fails on the dark ground, the kit can name a brand color for it: `"reverse": {"accent": "#f2c230"}`.

## 5. Typefaces

- Choose a pairing from `assets/font-pairs.json`. Each has a note on its character and who it suits. "Sturdy & Clear" is the default for readers over 55.
- The heading face is also the logo face, so judge it by how the business name looks in it. Some names have awkward letter pairs in some faces; try the name before you commit.
- `brandkit.py fonts` downloads the files. The logo needs the .ttf file to be drawn as vector shapes.
- Two typefaces only. Weights: one for headings, regular and bold for text.

## 6. The logo

The logo is the business name, set in the heading typeface and drawn as real vector outlines by the script.

```json
"logo": {"kind": "wordmark", "text": "Northline", "descriptor": "Bookkeeping",
         "case": "as-typed", "tracking_em": -0.01, "layout": "text",
         "mark": {"letters": "N", "shape": "square"}}
```

- **text** is the real name, or the short form the member actually uses. Never an invented name. A long name ("Harbor & Pine Financial Planning") usually sets the short form large with the rest as the `descriptor`. The descriptor is the rest of the name and nothing else: `check` refuses a tagline, a year or a claim there.
- **case:** `as-typed`, `upper` or `lower`. Capitals want a little positive tracking (0.02 to 0.06). Large lowercase and mixed case want zero or slightly negative (-0.02 to 0).
- **kern:** if two letters sit badly, adjust that pair: `"kern": {"AV": -0.06}` (in em).
- **layout:** `text` (name alone) or `mark-text` (the small mark to the left).
- **mark:** one to three letters for profile pictures and browser tabs. `shape`: `square` (takes the kit's corner radius), `circle`, or `none` (bare letters in the accent color).
- Look at the mark in the 24-pixel circle on the board. If it is not readable, use fewer letters or a heavier weight.

What you do not do: generate a symbol, an icon or a picture with an image model; add a tagline the member did not write; add effects. If the member wants a drawn symbol, the brand sheet carries a brief for a designer, and the wordmark stands as the logo until then. Say once that many respected firms use a wordmark alone.

## 7. The board

1. Write `Design/Brand/directions.json` (`kit-file.md`). The `sample` is the member's own headline and one sentence from the Business File (§3 or §4), their booking line as the button text, and their name and role. Mark the one or two words that carry the headline with asterisks: `"Know what your business *really* made last month."`
2. `brandkit.py fonts Design/Brand/directions.json`
3. `brandkit.py board Design/Brand/directions.json Design/Brand/directions.html`
4. Run the review in `quality-bar.md`. Then open the board with the member.

Each direction shows the logo on its own ground and reversed, the named colors, the typefaces on their own words, the small mark at three sizes, a LinkedIn post image both ways, the top of a web page, and an email signature.

## 8. The choice

Ask for reactions, not verdicts: "Which one would you be proud to hand to a client? Which one is not you? Anything you would take from one and put in another?"

- A clear pick: write `kit.json` from it.
- A mix: make it, show a two-direction board (the mix and the nearest original) with `brandkit.py board … --mix`, and ask again.
- None: ask what is wrong with each in their words, go back to the brief, and make three new ones. At most three rounds in total. If nothing lands after three, stop and say that a short session with a designer is the right next step; give them the brief you wrote.

Then go to Phase 3 in the skill: confirm, write the do and do-not lines, lock.
