# The Design folder: where everything lives

Everything sits in the member's Obsidian vault, beside the Business File:

```
<vault>/
  BUILDROOM_BUSINESS_FILE.md
  .env                                  KIE_API_KEY (never printed)
  Design/
    Taste Vault/
      inbox/                            the member drops screenshots here
      collections/<name>/T-001.png …    filed by taste_vault.py sort
      taste.json                        the references, reactions, direction feedback, the confirmed read
      Taste Vault.md                    the Obsidian note (embeds every reference)
      contact-sheet.html                the same, as a page
    landing-page/                       one folder per design project (the slug of the deliverable)
      design.json                       deliverable, audience, rounds, directions, the pick
      directions/r1-field-guide/index.html (+ img/)
      directions-round-1.html           the side-by-side board
      palettes.json                     the five palettes for the tweak bar
      page/index.html (+ img/)          the chosen page, tuned, then final
      page-before-<date>/               an earlier pick, kept
      tweaks.json                       the saved looks and the final one
      images.json                       where every picture came from
      images/                           prompts, jobs.json, prices.json, project.json (the media ledger)
      check.md                          the last go-live check
    System/
      tokens.json  tokens.css  slides.json  design-system.md  fonts.md  tokens-v1.json …
```

If the member has no Obsidian vault and declines to set one up, use a `Design/` folder beside the Business File. The layout is the same; pass that folder's parent as `--vault`.

## taste.json

```json
{"schema": "buildroom-taste/1", "created": "2026-11-13",
 "refs": [{"id": "T-001", "file": "collections/heroes/T-001.png", "original_name": "Screenshot 2026-11-12.png",
           "collection": "heroes", "kind": "gallery|niche|own|other", "source": "https://…", "added": "2026-11-13",
           "word": "calm", "likes": "big photo", "dislikes": "busy footer", "colours": ["#1f3b2d", "#f4efe6"],
           "sha256": "…"}],
 "direction_feedback": [{"date": "…", "direction": "Field Guide", "round": 1, "text": "love the photo, hate the green"}],
 "read": ["big real photos", "one bold colour", "no textures"], "read_confirmed": "2026-11-13"}
```

## design.json

```json
{"schema": "buildroom-design-project/1", "project": "landing-page", "deliverable": "landing page",
 "audience": "50plus|general", "copy": "path to the approved copy", "cap_rounds": 3,
 "rounds": [{"n": 1, "started": "…", "directions": [{"name": "Field Guide", "slug": "field-guide", "idea": "…",
             "for": "…", "refs": ["T-001", "T-004"], "dir": "directions/r1-field-guide"}]}],
 "picked": {"name": "Field Guide", "slug": "field-guide", "round": 1, "date": "…", "mix": "", "note": ""}}
```

## tweaks.json

```json
{"schema": "buildroom-tweaks/1", "final": "Look 2", "final_date": "…",
 "presets": [{"name": "Look 2", "palette": "Harbour", "fonts": "Sturdy & Clear",
              "vars": {"--c-bg": "#ffffff", "--size-base": "20px", "…": "…"},
              "attrs": {"data-hero": "stacked", "data-buttons": "solid"}, "saved": "…"}]}
```

## tokens.json

`schema`, `name`, `look`, `locked`, `version`, `audience`, `color` (the seven), `dark` (any of the seven), `font` (`head`/`body` with family, fallback, weights; `pair`; `licence`), `type` (`base_px`, `scale`, `measure_ch`, `line_height`), `space.unit_px`, `radius_px`, `shadow`, `motion`, `buttons`, `photo`, `hero`, `texture`, `density`, `eyebrows`, `head_italic`, `imagery` (`source`, `rules`), `dos`, `donts`, `refs`, and the raw `vars` and `attrs`.

## images.json

See `imagery.md`.
