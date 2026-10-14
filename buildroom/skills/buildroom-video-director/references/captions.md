# Captions

Most people watch the first seconds on mute. Captions are part of the picture, not an accessory: every video ships with them burned in, plus an SRT for platforms that take one.

## Step 1 — the transcript

Transcribe the **voice stem** the edit wrote (`renders/<id>.voice.wav`), not the mix with music:

```sh
python3 scripts/transcribe.py renders/V1.voice.wav --out transcript.json --snap-to-script script.txt
```

- Engines, in order: `faster-whisper` (local, free: `pip install faster-whisper`), `whisper` (local), the OpenAI API (`OPENAI_API_KEY` in `.env`, paid, cheap).
- `--snap-to-script` keeps the real timings and puts the **approved words** in (names, numbers, curly quotes, brand words). Anything said that is not in the script is kept and listed: the reviewer must see every departure.
- No engine available: `--engine align --script script.txt` spreads the approved words over the detected speech. Timing is approximate and labelled so; the review marks the words and timing "unverified" and the member checks them by eye.

## Step 2a — SubMagic (the polish, when the member has it)

SubMagic sets animated, styled captions with word-level timing and handles emphasis well. Sign-up and disclosure: `provider-signup.md` (https://submagic.co/?via=harrison22, with the plain route). The member picks one template once; it goes in §19 and every video uses it.

```sh
python3 scripts/ledger.py plan project.json --asset-id CAPTIONS-V1-916 --provider submagic --model "<template>" --prompt-ref edit.json --kind captions
python3 scripts/submagic.py --dry-run --video renders/V1_9x16.cut.mp4 --template "<template>"
python3 scripts/submagic.py --project project.json --asset-id CAPTIONS-V1-916 --video renders/V1_9x16.cut.mp4 --out renders/V1_9x16.mp4 --template "<template>" --cost 1 --quote "SubMagic plan minutes"
```

Set `captions.mode` to `"submagic"` in `edit.json` so the assembly leaves a clean cut. One SubMagic job per ratio, or caption the tallest ratio and accept its layout in the others only if the platform crops cleanly. After it returns, check every name, number and brand word against the script on the contact sheet; SubMagic's word list (saved beside the video when returned) goes to the reviewer. No key, a failure, or a template that puts text in the unsafe zone: fall back to step 2b.

## Step 2b — the director's own captions

`captions.mode: "burn"` in `edit.json`, then assemble again. The script builds cues from the transcript:

- at most **two lines**, balanced, about 26 characters a line at 1080 wide (set `max_chars`);
- cues follow sentences and split at natural breaks (after a comma, before "and", "but", "to", "with"…); never a one- or two-word cue when the sentence can avoid it; a capitalised name stays on one line;
- each cue on screen at least **0.7 s**;
- set in the brand font (`fontsdir` with the font's **TTF or OTF** file; WOFF2 will not load in the caption renderer), at least **48 px**, white on a semi-opaque brand-dark box, **inside the safe zone** for each ratio, off the face.

## Rules for both

- Captions say exactly what is said, in the approved spelling. A changed number or name is a G4 issue, not a typo.
- Never cover the face, the product, the proof on screen, or the end card's call to action (end cards carry no captions: the voice has stopped).
- Emphasis (a highlighted word) only on the word that carries the line, once or twice a video.
