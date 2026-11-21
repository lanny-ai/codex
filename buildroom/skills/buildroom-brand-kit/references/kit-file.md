# The kit file, the folder and the commands

## The folder

```
Design/
  Brand/
    kit.json              the kit as data (you write this)
    directions.json       create path only: the candidate brands
    directions.html       create path only: the board
    Brand Kit.html        the brand sheet (written by lock)
    logo/                 the member's logo files, or wordmark.svg, wordmark-on-dark.svg, mark.svg, mark-on-dark.svg
    fonts/                font files
  System/                 the locked Design System (written by lock)
    tokens.json  tokens.css  slides.json  design-system.md  fonts.md  tokens-v<N>.json
```

Paths inside `kit.json` are relative to the kit file.

## kit.json

```json
{
  "name": "Northline Bookkeeping",
  "source": "created",
  "direction": "Ledger",
  "audience": "50plus",
  "person": "Dana Whitfield",
  "palette": [
    {"name": "Ledger Ink", "hex": "#16211c", "role": "text and logo", "from": "the ledger pages you showed"},
    {"name": "Rule Red", "hex": "#b3261e", "role": "one button, one line"}
  ],
  "colors": {"bg": "#ffffff", "surface": "#f4f5f3", "ink": "#16211c", "muted": "#56605b",
             "accent": "#b3261e", "accent_ink": "#ffffff", "line": "#d5d9d6"},
  "reverse": {"accent": "#e0483f"},
  "fonts": {
    "head": {"family": "Bitter", "weight": 700, "fallback": "Georgia, serif",
             "files": [{"src": "fonts/Bitter-700.ttf", "weight": 700}], "license": "google"},
    "body": {"family": "Source Sans 3", "files": [{"src": "fonts/SourceSans3-400.ttf", "weight": 400},
             {"src": "fonts/SourceSans3-700.ttf", "weight": 700}], "license": "google"}
  },
  "logo": {"kind": "wordmark", "text": "Northline", "descriptor": "Bookkeeping", "tracking_em": -0.01,
           "mark": {"letters": "N", "shape": "square"}},
  "type": {"base_px": 18, "scale": 1.25},
  "shape": {"radius_px": 2},
  "photo": {"source": "own", "rules": "Dana's own photos; client photos only with consent on file."},
  "sample": {"headline": "Know what your business *really* made last month.",
             "body": "Monthly bookkeeping for owner-run trades firms.",
             "cta": "Book a 20-minute call", "person": "Dana Whitfield", "role": "Owner"},
  "dos": ["One red thing per page: the main button"],
  "donts": ["Nothing that looks like a bank"],
  "confirmed": {"colors": true, "fonts": true, "logo": true}
}
```

| Field | Notes |
|---|---|
| `source` | `uploaded` (their own kit), `website` (read from their site and confirmed) or `created` (made here) |
| `audience` | `50plus` (default; body text 18px or more) or `general` |
| `palette` | the brand's named colors. For an intake, exactly as given, with `from` |
| `colors` | the seven working colors: `bg` page, `surface` panels, `ink` text, `muted` quiet text, `accent` buttons and links, `accent_ink` text on the accent, `line` borders |
| `reverse.accent` | optional: the accent to use on the reverse ground when the main accent is too dark or too faint there |
| `fonts.*.license` | `google`, `ofl`, `apache`, `bought`, `system` or `unknown` |
| `logo.kind` | `files` (theirs: `on_light`, `on_dark`, `mark_on_light`, `mark_on_dark`), `wordmark` (set here) or `none` |
| `sample` | the member's own words, shown on the sheet. `headline` and `body` are needed for the "In use" section; asterisks mark the words the accent carries |
| `confirmed` | each must be `true` before a lock, and only after the member said yes |

## directions.json (create path)

```json
{"business": "Northline Bookkeeping", "audience": "50plus", "person": "Dana Whitfield",
 "sample": {"headline": "…", "body": "…", "cta": "…", "person": "…", "role": "…"},
 "directions": [
   {"name": "Ledger", "idea": "one sentence on why it suits this business", "from": "what in their answers it comes from",
    "palette": [...], "colors": {...}, "fonts": {...}, "logo": {...}, "shape": {...}, "reverse": {...}}
 ]}
```

Two to four directions. Each needs `name`, `idea` and `from`.

## Commands

| Command | What it does |
|---|---|
| `brandkit.py read FILE …` | Reports what is in logo, page, stylesheet and font files. Writes nothing. |
| `brandkit.py roles HEX … [--dark]` | Proposes the seven working colors from the brand's colors, and lists every one that is not literally theirs. |
| `brandkit.py fonts KIT.json` | Downloads the kit's Google Fonts as .ttf into `fonts/` and names them in the kit. Works on `directions.json` too. The only command that goes online. |
| `brandkit.py check KIT.json` | FIX lines stop a lock. LOOK lines are for you to read and the member to decide. |
| `brandkit.py board DIRECTIONS.json OUT.html` | The directions board. `--embed` makes one self-contained file. |
| `brandkit.py lock KIT.json --out Design/System` | Writes the Design System, the logo files (for a kit made here) and the brand sheet. Keeps the earlier system as `tokens-v<N>.json`. |
| `brandkit.py section --system Design/System` | Prints the Business File lines for §22 and §18. |
| `brandkit.py show --system Design/System` | The locked kit in brief. |
| `node brand_png.mjs Design/Brand/logo` | PNG copies of the logo files (needs Node and Playwright). |

## How the other sessions use the kit

`Design/System/tokens.json` is the one file they read. It carries the working colors, the typefaces and sizes, and a `brand` block:

```json
"brand": {"name": "…", "source": "created", "palette": [...],
          "logo": {"kind": "wordmark", "on_light": "../Brand/logo/wordmark.svg", "on_dark": "../Brand/logo/wordmark-on-dark.svg",
                   "mark_on_light": "../Brand/logo/mark.svg", "mark_on_dark": "../Brand/logo/mark-on-dark.svg"},
          "font_files": {"head": [{"src": "../Brand/fonts/Bitter-700.ttf", "weight": 700}], "body": [...]},
          "reverse": {"bg": "…", "ink": "…", "accent": "…", …},
          "sheet": "../Brand/Brand Kit.html"}
```

Paths in the `brand` block are relative to `Design/System/`.

| Session | Uses |
|---|---|
| **LinkedIn Engine** | Every image spec sets `"brand": "<path to Design/System/tokens.json>"`: the logo, colors and typefaces come from the kit, on the brand's own ground or the reverse. |
| **Website Design Studio** | Starts from the kit instead of a blank palette. Its lock keeps the `brand` block. |
| **Lead Capture, Offer Page Copy** | `tokens.css` in every page; the logo files in the header. |
| **Ad Studio, Video Director** | Colors, typefaces, logo and photo rules for the ad brand kit, end cards and captions. |
| **Webinar Builder** | `slides.json` flags for the deck. |
| **Proof Engine, Training Docs, one-pagers** | `tokens.css` and the logo for anything printed or shared. |

A session that finds §22 empty carries on as before and offers this session once: "Your posts and pages will look more like you with a brand kit. It takes about fifteen minutes. Say: set up my brand kit."
