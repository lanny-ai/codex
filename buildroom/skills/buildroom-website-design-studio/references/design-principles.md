# Design principles: what the skill believes, and why

Every claim carries a tag: **[founder's method]**, **[official]** (a standards body or the tool's own docs), **[data]** (a study or measured result), **[practitioner]** (people who do this for a living, in their own words) or **[folklore]** (repeated everywhere, traced nowhere). Say which kind a claim is when you use it with a member. The sources are in `research_notes/Website Design Studio/outside_research_2026.md` in the repository.

## 1. The five beliefs

1. **Show it, don't describe it** [practitioner; the workflow credited in `source-credit.md`]. People can't put taste into words, but they can point at what they like. A board of 5–15 screenshots gives Claude more to work from than a page of adjectives. So the session starts with the member's references, not with questions about "brand personality".
2. **A tell is a default nobody chose** [practitioner, the shared view of the open anti-slop skills]. A cream background isn't wrong. A cream background *because that's what comes out* is wrong. Every choice on the page has to trace back to the member's references, their business or their audience.
3. **Options before decisions** [practitioner]. Non-designers find it hard to say what they want and easy to react. Three very different takes, side by side, and the member's plain reactions ("too clean", "love the photo") do the articulating.
4. **Dials, not prompts** [practitioner]. Once a direction is chosen, fine-tuning by sliders and toggles is faster and more honest than fifty "make it a bit warmer" messages. The member can see a change in a second and undo it in one.
5. **Lock it, so it pays off everywhere** [Build Room]. A good page whose taste lives only in that page is a one-off. The Design System (`tokens.json`, `tokens.css`, `design-system.md`, `slides.json`) is read by every other skill that makes something visual. That's what stops a member's ads, slides and pages looking like three different businesses.

## 2. The page token contract

Every page this skill writes, and every page another skill writes from §22, uses these CSS variables on `:root`. Colours, fonts and sizes come only from them:

| Variable | What it is |
|---|---|
| `--c-bg`, `--c-surface`, `--c-ink`, `--c-muted`, `--c-accent`, `--c-accent-ink`, `--c-line` | page, panels, text, quiet text, accent (buttons, links), text on the accent, lines |
| `--font-head`, `--font-body`, `--w-head` | heading family, body family, heading weight |
| `--size-base`, `--scale`, `--measure`, `--leading` | body size in px, heading step ratio, line length in ch, line height |
| `--space`, `--radius`, `--shadow`, `--motion` | spacing unit, corner radius, shadow, motion multiplier (0 turns motion off) |

The page also uses these `data-` attributes on `<html>`, which the tweak bar switches. A page supports a toggle by having CSS for it, such as `[data-hero="stacked"] .hero { … }`:

`data-buttons` (solid · outline · pill) · `data-photo` (natural · warm · mono · rounded) · `data-hero` (split · stacked · full-photo) · `data-texture` (none · paper · grain) · `data-density` (airy · regular · compact) · `data-theme` (light · dark) · `data-eyebrows` and `data-head-italic` (off · on; both generic tells, so off by default).

`directions.py new` writes a starter page with all of this in place. A page with a `[data-theme="dark"]` block gets dark mode too.

## 3. What the evidence says about pages that work

- **The first screen does most of the work** [data, NN/g]: 57% of viewing time goes to the first screen and 74% to the first two. Say what it is, who it's for and the one action, before any scrolling.
- **One main action** [data, modest]: Unbounce's numbers show single-action pages converting a little better (13.5% vs 11.9%). The "266% more conversions" figure is **folklore**. Repeat the one action; don't offer three.
- **Real photos of real people get looked at; generic stock gets skipped** [data, NN/g]. There's no reliable figure for how much a founder photo lifts sales, so never promise one.
- **Speed matters** [data, Google/Deloitte]: 0.1s faster on mobile was linked to 8.4% more retail conversions. "53% leave after 3 seconds" couldn't be traced, so it's **folklore**. Keep photos to about 200 KB each.
- **Most visitors are on phones** [data]: about half to 60% of web traffic. Every direction is checked at phone width.
- **Older readers need bigger, darker text** [official + data]. GOV.UK uses 19px body text, and NN/g found small grey text a repeated barrier. "18px or more for seniors" is practitioner consensus, not a trial result. The skill's floor is **18px for a 50+ audience** (16px otherwise), with nothing under 14px.

## 4. Things the skill settles

- **Design or copy first?** The approved copy comes first, from Offer Page Copy or Lead Capture, so the directions are judged on the real words. If there's no approved copy, write a short honest draft from §2 and §3 and label it a draft. The design is never judged on lorem ipsum.
- **How many rounds?** Three rounds of three, at most. After that, pick the closest one and fine-tune it, saying what's still wrong in words. More rounds turn the session back into a slot machine.
- **Shuffle?** It stays, because members enjoy it. But it never turns on a generic tell and never drops text below the audience's minimum.
- **Bold or safe?** Spend the boldness on one memorable thing (a photograph, a typeface, a colour) and keep everything else quiet [practitioner].
- **Dark mode?** Offered when the page supports it, and checked for contrast like the light one. It's never forced on.

## 5. Folklore to correct when a member repeats it

- "Blue builds trust" and similar colour-psychology rules: **folklore**. Colour should come from the member's references and their world.
- "Red buttons convert best": **folklore**. Contrast with the page and being the only button of that colour are what matter.
- "Nobody scrolls": **folklore**. People do scroll, but most attention goes to the top (§3).
- "A page needs a video": not supported. A clear first screen does more.
