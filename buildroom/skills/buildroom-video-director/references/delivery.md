# Delivery: the videos manifest, the kit, the Business File

## The project folder

```
videos/2026-10-install-explainer/      (or ads/2026-10/video/ when the Ad Studio sent you)
  brief.md · beats.md · script.txt · storyboard.md · shoot-list.md
  footage/                 the member's takes and screen recordings
  broll/                   prompts (*.prompt.txt) and generated shots
  cards/                   end and title cards per ratio (render_static.mjs)
  brand/                   logo, fonts (TTF/OTF for captions), music and its licence
  edit.json · transcript.json · videos.json · prices.json · jobs.json
  project.json             the ledger
  renders/                 cuts, finals, voice stem, SRT, assembly report
  review/                  check JSONs, contact sheets, safe frames, checklist.md, reviewer verdicts
  kit/                     ready to publish
```

## `videos.json` (the manifest the kit reads)

```json
{"cycle": "2026-10",
 "videos": [
  {"id": "V1", "playbook": "sales", "slug": "install-call-explainer", "title": "How the Install Call works",
   "ratios": ["16x9", "9x16"],
   "platform_copy": {"title": "…", "caption": "…", "description": "…", "cta_button": "BOOK_NOW",
                     "url": "https://example.com/book", "utm_source": "youtube"},
   "thumbnail_at": 1.2,
   "generated": [{"asset": "BROLL-3", "provider": "kie", "model": "<resolved id>"}],
   "people": [{"who": "founder", "consent": "§19 likeness and voice, 2026-10-14"}],
   "claims": [{"claim": "first agent live and reporting within 14 days of the Pre-Flight call", "proof": "§3 guarantee, signed off 2026-10-14"}],
   "ai_label": false,
   "music": "Artlist track 'Morning Light', commercial licence #…"}]}
```

## Naming

`YYMM_<playbook>_<slug>_<id>_<ratio>.mp4`, for example `2610_sales_install-call-explainer_V1_16x9.mp4`. Use the same name, without the ratio, as the post or ad name, so results join back to the video.

## What the kit holds

`review_video.py kit` builds it only when the ledger says every video passed G3 and G4 and the member approved it:

- `videos/` every approved video in every ratio, named as above;
- `captions/` the SRT per video (for YouTube, LinkedIn and platforms that take a caption file);
- `thumbnails/` a frame per video (the member may replace it with a designed thumbnail from the renderer);
- `publish.csv` per file: title, caption, description, CTA, and the URL with UTM parameters;
- `disclosure-sheet.md`.

A `--preview` kit is labelled `NOT-READY.txt` and is never handed over as ready.

## The Business File

- **§19 Video** — playbooks run (with dates), footage and video library locations, the video brand kit (intro cue, end card, caption template or style, music source and licence), consent status (likeness, voice, twin), the content series (pillars, cadence, platform, volume mode), last delivered (title, playbook, date), results to watch.
- **Proof playbook** → a §18 proof vault entry per consented testimonial (P-ID, type, verbatim line, name as consented, source, date, consent).
- **Content playbook** → the §14 content line (platform, cadence, type, calendar location).
- **Sales playbook** → the §5 page reference (video embedded on the offer page) or §15 (the prospect video in the sales process).
- **Ad playbook** → the Ad Studio updates §18's current cycle.
- **§13** — a row for anything the video needs next: a landing variant, a reshoot, a testimonial to collect, a series episode.
- **§8** — the Session Log row with the member's 1–5 rating.
