# Anti-generic: the 2026 tells and what to do instead

These are Build Room's own rules, written from what practitioners and the open anti-slop design skills agree on (summarised in our words in `source-credit.md`). **A tell is a default nobody chose.** Any of these is fine when the member's references or business call for it; it's a tell when it just came out that way.

`design_check.py tells --page …` finds the eight marked ✱ automatically. The rest are for your own review of every direction before the member sees it.

## The tells

| Tell | What to do instead |
|---|---|
| ✱ **A headline ending in an italic word** ("Build your future *today*") | Let the words carry the emphasis. If one word matters, make the sentence end on it, in the same style. |
| ✱ **Small uppercase labels over most headings** ("FEATURES", "HOW IT WORKS") | Use hierarchy by size and space. Use a label only when it carries information, such as a step number in a real sequence. |
| ✱ **The default cream or beige background**, often with a serif headline and a terracotta, sage or olive accent | White, a true colour from the references, or a photograph. If cream really is in the references, keep it and change something else. |
| ✱ **Pill buttons everywhere** | Square or slightly rounded buttons that match the page's corners (`--radius`). |
| ✱ **Three equal feature cards in a row**, each with an icon tile | A numbered list for a real sequence, two columns with a photo, or one strong section per idea. |
| ✱ **Purple-to-blue gradients or blurred glow blobs** | Flat colour, a photo, or a texture from the references. |
| ✱ **Emoji as bullets or icons** | Plain bullets, numbers, or no marker at all. |
| ✱ **A "trusted by" line with no real logos** | Only real proof from the proof vault (§18): a consented testimonial, a real number with its source. Otherwise leave it out. This one is an honesty rule, not just a style rule. |
| A centred hero in Inter with a small pill badge above the headline ("✨ New") | Start with the most characteristic thing about the business: the founder, the place, the result. |
| The same section recipe repeated: label, headline, grey subtitle, button | Vary the rhythm: a photo section, a quote, a list, a plain paragraph. |
| Identical rounded cards with the same soft shadow, cards inside cards | Fewer boxes. Let space separate things. |
| Fade-up animation on every section, hover effects on every card | One deliberate motion moment, or none. Always a reduced-motion setting. |
| Grey text on coloured backgrounds | Text from `--c-ink` or `--c-accent-ink`, checked at 4.5:1. |
| Stock photos of smiling people at laptops, grey-haired couples on beaches | The member's own photos. Or a generated scene with no real person (`imagery.md`). |
| Invented details: fake addresses, round-number stats, "10,000+ happy clients" | Only facts from the Business File. `design_check.py` refuses a number that isn't in the File or the approved copy. |
| "01 / 02 / 03" numbering on things that aren't a sequence | Numbers only for steps people follow in order. |

## The positive rules

1. **Start from the member's world.** Their references, their field, their photos, their buyers' age. The hero opens with the most characteristic thing about the business, not a statistic and a gradient.
2. **One dominant colour, one accent, used for one job.** The accent marks the main button and links. Nothing else competes with it.
3. **Type carries the personality.** One vetted pairing from `type-and-colour.md`, two or three weights, a clear size scale.
4. **Hierarchy by size and space, not labels.**
5. **Spend boldness once.** One memorable element per page (a big photograph, an unusual typeface, a strong colour field). Everything else stays quiet.
6. **Real over placeholder.** Real copy, real photos, real proof. If something isn't ready, leave a gap the member can see, never a fake.
7. **The quality floor:** contrast of 4.5:1 or more, body text of 18px or more for a 50+ audience, nothing under 14px (the check blocks text under 12px and warns under 14px), buttons at least 44px tall, a visible focus ring, works on a 375px phone with at least 16px each side, a reduced-motion setting.

## The A/B, when the member is curious

If the member asks "does this rulebook actually matter?", build the same hero twice: once with these rules and once from a plain prompt with none. Show them side by side on the directions board (two cards). Run `design_check.py tells` on both and read out the difference. Do this only when asked; it uses a round.
