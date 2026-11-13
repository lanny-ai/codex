# The three directions: making three takes that are really different

## What "very different" means

Three directions that differ only in colour are one direction three times. Make each one differ on **at least three** of these:

1. **Structure of the first screen:** photo beside the words · words over a full photo · words alone, very large · a quote first · the founder first.
2. **Type:** a different vetted pairing from `type-and-colour.md` for each.
3. **Colour logic:** light and airy · one strong colour field · dark and rich · black and white with one accent.
4. **Density:** airy and slow · regular · compact and information-rich.
5. **Imagery:** big photography · small framed photos · texture or illustration · no images, all type.
6. **Shape:** sharp corners and rules · soft corners · no boxes at all.

Each direction also draws on **at least three** taste-vault references (`--refs T-001,T-004,T-009`), and no two directions lean on the same main reference.

## Twelve archetypes to start from

Pick three that fit the member's references and audience. Then change them so each one is the member's own, not the archetype.

| Archetype | First screen | Suits |
|---|---|---|
| **Field Guide** | clear photo beside a plain headline; sturdy serif | practical coaches, trades turned consultants |
| **Kitchen Table** | warm, personal; the founder's photo large; a letter-like opening | relationship-led coaching, retirement, wellness |
| **Front Page** | editorial; big type; a strong standfirst; no photo above the fold | authors, speakers, thought leaders |
| **Quiet Studio** | lots of white; one accent; small framed photos | premium advisors, designers, therapists |
| **Bold Field** | one strong colour field behind the words (use `--c-surface` or `--c-accent` for the field, with `--c-ink` or `--c-accent-ink` on it, checked) | energetic offers, workshops, events |
| **Evening** | dark and rich; light text; one warm accent | high-end retreats, masterminds |
| **The Plan** | a clear numbered sequence early; the method shown | process-led services, consultants |
| **Portrait** | the founder full-height; the words in a column beside | personal brands |
| **Place** | a landscape or location photo across the top | local or place-based services, retreats |
| **Plainspoken** | type only; very large, very clear; almost no decoration | sceptical buyers, finance, legal |
| **Scrapbook** | layered photos, notes and textures, tidy underneath | creative and craft businesses |
| **Clinic** | calm, very clear; generous spacing; strong contrast | health-adjacent, older audiences who want reassurance |

## How to write each page

1. `directions.py new --project Design/landing-page --name "Field Guide" --idea "…" --for "…" --refs T-001,T-004,T-009 --vault <vault>` writes the starter on the token contract (`design-principles.md` §2). With `--vault`, it refuses a reference that isn't in the taste vault. It warns when a direction names fewer than three references or shares its main reference with another. A fourth direction in a round is refused; replace one with `directions.py remove --name …`.
2. Write the whole page in that `index.html`. Use one file, with CSS inside, using only the contract variables. Put local images in an `img/` folder next to it.
3. Use the **approved copy** word for word: headline, sub, sections, the one action. Don't rewrite copy in this skill. If a line is too long for a direction, say so and ask; the Copy Engine or Offer Page Copy owns the words.
4. Put the member's own photos in where they exist. Generate only what's missing, through `imagery.md`, and only after the member approves the image list and cost.
5. Add CSS for the toggles the direction can sensibly support (hero layout, buttons, photo treatment, density, dark mode). The tweak bar shows only what the page supports.
6. Before showing it, read it against `anti-generic.md`. `directions.py board` prints the tells it finds; fix any you didn't choose on purpose.
7. Make the page work at 375px wide: one column, at least 16px of space each side, images `max-width: 100%`, buttons at least 44px tall with labels that fit on one line. The first screen on a phone must show the headline, not only a photo.
8. Look at it in every toggle combination you built CSS for, especially dark mode with each hero layout: the check reads the page as built, not every combination.

## Showing them

- `directions.py board --project Design/landing-page` writes `directions-round-1.html`. Open it in the browser. In Claude.ai or Cowork, `--inline` makes one self-contained file to show as an artifact.
- Introduce each one in a single line: its name, its idea, who it would appeal to. Then ask one question: "What do you like and not like about each one? Plain words are perfect."
- Log each reaction: `taste_vault.py feedback --vault <vault> --direction "Field Guide" --text "love the photo, hate the green"`. The next round reads these.
- Then offer the three paths:
  - **Pick one:** `directions.py pick --name …`, then on to the tweak bar.
  - **Three more like #2:** the next round (`--round 2`, started on purpose: it's one of three), each a different variation of the winner. Change structure and type, not just colour.
  - **Mix:** "the hero of #1 with the colours of #3". Write one new direction that does exactly that, then pick it with `--mix "…"`.
- After round 3, the cap: "We've got as far as rounds can take us. Let's pick the closest one and fine-tune it with the sliders."

## Deliverables other than a landing page

The landing page is the default. If the member chooses otherwise:
- **Opt-in or thank-you page:** the same flow; shorter pages, one action.
- **Sales page:** the same flow; the directions show the top third and one proof section, not the whole long page.
- **Webinar slides:** the directions are three title slides plus one content slide each, shown as HTML at 16:9. The lock writes `slides.json` for the Webinar Builder's `slide_builder.py`.
- **One-pager:** the directions are A4/Letter portrait HTML pages; print to PDF to check.
