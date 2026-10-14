# Build Room Video Director — decisions and status

_Built 2026-10-14 from the Pursue Goal "Build Room OS Video Director". Companion to `docs/BUILDROOM-AD-STUDIO-PLAN.md`._

## What shipped

**`buildroom-video-director`** — one director, four playbooks:

| Playbook | Job | Shape | Judged by | Writes |
|---|---|---|---|---|
| **Ad** | Paid video from an Ad Studio concept | 15–45 s · 9:16, 4:5 · three hook openings on one body | Cost per qualified lead | §19; the studio writes §18 |
| **Content** | Value-first shorts and long-form, series, repurposing, volume mode | 30–90 s · 9:16; 4–12 min · 16:9 | Watch time, follows, keyword CTA | §19, §14 content line |
| **Sales** | Sales video, offer explainer, personalised prospect video | 60 s–15 min · 16:9, 9:16 | Booked calls, deals | §19, §5 or §15 reference |
| **Proof** | Consented client testimonial interviews and clips | 2–5 min + 20–40 s clips | Testimonials collected | §19, §18 proof vault entries |

One flow for all four: brief (G0) → beats (G1) → script one piece at a time through Kern/Halbert (G2) → storyboard → ten-minute phone shoot list → footage intake → B-roll plan, quote, ledger → the edit → captions → machine checks + separate reviewer (G3/G4) → the member watches every final → kit → Business File.

**Scripts** (`skills/buildroom-video-director/scripts/`): `assemble_video.py`, `transcribe.py`, `submagic.py`, `review_video.py`, `videolib.py`; plus the shared `ledger.py`, `gen.py`, `render_static.mjs`.

**Shared media toolkit** (`buildroom/shared/media/`): the ledger, the generation adapter (Higgsfield and Kie.ai images and video, HeyGen twins with consent), the static renderer (now with `end-card`, `title-card` and 16:9), and `provider-signup.md` (Higgsfield, Kie.ai and SubMagic affiliate links with the disclosure). `build-skills.sh` copies them into both media skills and fails the build if a skill-side copy was edited instead of the shared source.

**Business File 1.3:** §19 Video; §1 *Retired lines*, bound into the shared protocol so a retired line is never used again by any skill.

**Tests:** `buildroom/tests/media/run_tests.py` (51 checks): ledger rules, generation and SubMagic against a local mock of all four providers, assembly, alignment and captions on synthetic media, review with planted defects and placeholder media, word-timed cutaways and caption-hiding cards, per-placement kits and the AI-label refusal, caption rules, the renderer. No network, no keys, no spend.

## Decisions made

1. **One director, playbooks, not separate skills.** The parts that decide quality (story, script, shoot list, edit, captions, review, ledger) are the same for every video; separate skills would duplicate and drift.
2. **The Video Engine elective is retired into volume mode.** Its money gate, `.env` recipe, zip install, scheduling and keyword-CTA lessons live in `references/volume-mode.md`; "Set up the video engine" routes to the director. The skill count stays at twenty-eight.
3. **Ad Studio phase 2 is the director's ad playbook.** The studio keeps strategy, concepts, copy and gates G0–G2 and hands video concepts to the director, which uses the studio's ledger and returns reviewed videos into the studio's kit.
4. **Real footage first.** Generated video is B-roll and scenes with no people; never a generated hero, customer or result. An avatar twin (HeyGen) only with written consent, for scale variants of a proven script, never a testimonial or a first video. The ledger and the adapter both refuse a twin without a consent reference.
5. **SubMagic is the caption polish; the director's own burned captions are the fallback.** Burned captions use libass with the brand's TTF/OTF font, at most two balanced lines, phrase-aware breaks, no widows, each cue at least 0.7 s, inside the safe zone.
6. **Transcription:** faster-whisper, whisper or the OpenAI API, then `--snap-to-script` so captions carry the approved wording. Without a speech engine, a labelled approximate alignment; the review then marks words and timing unverified.
7. **The voice stem** (the voice alone, before music) is written by the edit and is what gets transcribed and checked for dead air.
8. **Loudness −14 LUFS integrated, true peak ≤ −1 dBTP**, two-pass. **Safe zones** per ratio, 9:16 following the Reels interface (14% / 35% / 6%).
9. **ffmpeg from the member's system or `pip install imageio-ffmpeg`;** ffprobe optional (the scripts parse ffmpeg when it is absent).
10. **Review honesty:** the machine checks what it can measure; the reviewer works from frames, transcripts and measurements; motion, pacing and feel are always marked unverified and the member watches every final with sound.
11. **Retired lines:** a credibility line the founder asked never to use again is removed from the Ad Studio dry run and listed under §1 *Retired lines* in the founder's migrated Business File (kept out of this repo); no example uses it.
12. **fal.ai is not routed; Sora is never used.** The Video Engine zip's own pipeline may still call fal.ai; the Build Room routes do not.

## What the first review changed

An independent reviewer failed every gate on the first dry run and found seven tooling flaws. Fixed in the tools, so every member benefits:

- **No false passes.** An edit marked `placeholder`, or a transcript aligned from the script, has its loudness, first word, dead air and cuts reported as unverified, never as passes.
- **Checks that look at the result.** Captions are checked against the end card (none may run onto it) and against the top of the safe zone as well as the bottom; safe-zone frames are taken at 0.5 s, the middle and the end card.
- **Captions.** One box around each caption; a cue never spans two sentences; a line never ends on "the", "a", "to", "your"…; a number stays with its unit; line length per ratio (about 26 characters for 1080-wide, 40 for 16:9); captions stop before the end card and hide under cards that carry their own words (a guarantee).
- **The edit.** Cutaways timed to words (`at_word` / `until_word`) so they stay in sync after a re-cut; stills as cutaways (guarantee cards); `fit: "pad"` for screen recordings in 9:16; `zoom`; a warning when a clip is enlarged more than 5%.
- **Gates.** G2 (the approved words, guarantees included) passes only `--by member`, except in demo mode.
- **The kit.** One publish row per placement with its own ask and UTM; thumbnails from the uncaptioned cut; refuses a generated person without the AI label; flags approximate captions under "Before upload". The SubMagic template is the member's choice and required.
- **Rules.** The ad playbook needs one opening per approved hook on the same body; a booking ask never goes to people who already booked (cut a placement version); generated B-roll keeps the caption band clear; a session inserts a missing Business File section from the template rather than writing around it.

## Unverified until checked live

- **Provider request shapes** for Higgsfield (image and video), Kie.ai (createTask image and video), HeyGen (v2 generate, status) and SubMagic (project create, upload, status, export): written from public descriptions; the docs were unreachable from the build environment. Each lives in one config block; `gen.py --probe` and `submagic.py --probe` confirm them with real keys.
- **Live prices** and current model IDs per provider.
- **Safe-zone margins** per platform (check quarterly).
- **One box per caption** needs libass 0.17 or later (any ffmpeg from 2023 on); older builds set `box_style: "lines"`. Tested here on ffmpeg 7.0.2.
- **Motion, pacing and feel** of every real video (the member watches).
- **Founder items:** the §3 guarantee wording sign-off, likeness and voice consent (§19), live-page checks (the Babysitting Test's email capture, WF-1).
