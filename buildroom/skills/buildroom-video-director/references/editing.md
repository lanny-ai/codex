# The edit

`scripts/assemble_video.py` builds every ratio from one edit decision list (`edit.json`). The format is in the script's header; this file is how to use it well.

## Tools

ffmpeg is required: macOS `brew install ffmpeg` · Windows `winget install ffmpeg` · any OS `pip install imageio-ffmpeg` (the scripts find it), or set `FFMPEG` to the binary. Node and Playwright render the end and title cards (`npm i playwright` and `npx playwright install chromium` in the project folder, or `CHROME_PATH`).

## The edit decision list

- **clips** — the spine, in order: A-roll takes (the member speaking), B-roll that stands alone, cards. Each with `in`/`out` on the source and a `focus` point ("50% 35%" keeps the eyes in frame when a vertical take is cropped to 4:5 or a horizontal one to 9:16).
- **cutaways** — B-roll laid **over** continuous voice: `at` (seconds on the timeline) and `dur`. This is how the director makes L and J cuts: the voice carries on while the picture shows what is being said. Use them to cover a jump between takes, to show the thing named, and to reset attention every few seconds in an ad. Options:
  - `at_word` / `until_word` instead of `at` / `dur`: start on the first word of a phrase and end after the last word of another, read from `transcript.json` (with `lead` and `tail` in seconds to start early or hold late). Use these whenever the cutaway illustrates a phrase, so it stays in sync after a re-cut.
  - a still (PNG or JPG) instead of a video, for a card shown over the voice: a guarantee, a price, a step list.
  - `at_join: 1` starts the cutaway at the join before clip 1, less `join_lead` (default 0.1 s) (so a hook take plays whole on the face, whatever the transcript says); `cover_join: 2` stretches it to at least 0.3 s past the join before clip 2. Every join between two takes must sit under a cutaway or be listed in `deliberate_jumps` (clip indexes); the edit report and the review flag any other.
  - `hide_captions: true` when the cutaway carries its own words (a guarantee card): the captions stop for its length so the two never stack.
- **framing per clip** — `focus` ("50% 35%"), `zoom` (1.0 = cover; 1.1 tightens), and `fit: "pad"` to show the whole frame on a brand-dark background instead of cropping it (screen recordings in 9:16: a cropped screen loses its width and becomes unreadable). The edit report also warns when a padded clip is shrunk below 0.7× (a horizontal screen in 9:16 becomes unreadable: record a phone version and use `src` with `{ratio}`, e.g. `footage/screen_{ratio}.mp4`), and when a source is shorter than the edit asks for. It warns when a clip is enlarged more than 5% (`enlarged 1.78×`); a soft, enlarged frame is a G3 issue, so reshoot vertically, pad, or choose a tighter crop on purpose.
- **brand_cue** — the logo or name on screen from 0 s for about 2 s (top-left, inside the safe zone), or `{"type": "face"}` when the member's face opens the first frame and is the brand.
- **end card** — the last clip: `cards/end_{ratio}.png`, rendered per ratio with `render_static.mjs` (layout `end-card`: the ask as the headline, the URL, the button label, the member's photo inset if wanted), held at least 2.5 s.
- **music** — licensed or generated-with-licence only, about −20 dB under the voice, ducked automatically when the voice speaks. No music under a testimonial unless very low.
- **captions** — `burn` (the director's), `submagic`, or `none`; see `captions.md`. Burned captions stop before the end card on their own.
- **placeholder** — `true` while any footage or voice is a stand-in (a dry run, a rough cut before the shoot). The review then reports loudness, first word, dead air and cuts as unverified rather than as passes.
- **loudness** — −14 LUFS integrated for social (the default), true peak −1 dBTP. For YouTube long-form −14 also works; for podcast-style audio −16.

## The cut

1. Pick the best take of each line (voice first, then face, then framing).
2. Trim every breath and filler before the first word and after the last.
3. Hook first: the video starts on the first word or the first movement, never on silence.
4. Cover take-to-take jumps with a cutaway rather than a visible jump; a deliberate jump cut is fine in a fast founder video. Every boundary between two A-roll takes either has a cutaway over it or is listed in the storyboard as a deliberate jump.
5. Read the pacing: dead air over about 1.2 s inside the speech gets cut.
6. End on the ask: the last line, then the end card.

## Ratios and safe zones

| Ratio | Size | Where | Kept clear |
|---|---|---|---|
| 9:16 | 1080×1920 | Reels, Stories, TikTok, Shorts | 14% top, 35% bottom, 6% sides (Reels interface) |
| 4:5 | 1080×1350 | Feed | 5% top, 8% bottom |
| 1:1 | 1080×1080 | Feed, LinkedIn | ~6% |
| 16:9 | 1920×1080 | YouTube, sales pages, LinkedIn | 6% top, 10% bottom |

These margins are the commonly cited platform zones; check them against each platform's current guide once a quarter and change `SAFE` in `videolib.py` if they moved.

## Output

H.264 High, yuv420p, the edit's frame rate, AAC 48 kHz stereo, faststart. The script writes a clean cut (`_cut.mp4`), the voice alone (`.voice.wav`, for transcription), the captioned final (`.mp4`), an SRT, and `<id>.assemble.json` with every command, input checksum, duration and loudness. Every ratio must land within 0.1 s of the edit's duration.
