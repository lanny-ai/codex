# Review: gates G3 and G4 for video

The brief (G0), the beats (G1) and the script (G2) were approved before anything was shot. G3 (craft) and G4 (compliance) are judged on the **exported files**, by someone who did not make them, and then the member watches every final with sound. A verdict is pass, revise or unverified, with a timestamp, the defect, its consequence and the smallest fix. "Looks good" and scores out of ten are not verdicts.

## Step 1 — the machine checks (`review_video.py check`)

Per final file: size, codec, frame rate, audio format; duration within 0.1 s of the edit; loudness −14 LUFS ±1 and true peak ≤ −1 dBTP; brand cue by 2 s; first spoken word by 1 s (ads) or 2 s; end card held ≥ 2.5 s; spoken words against the approved script, word for word (when a speech engine made the transcript); captions ≥ 48 px, ≤ 2 lines, inside the safe zone, each ≥ 0.7 s; dead air over 1.2 s; cuts per minute; a one-frame-a-second contact sheet and a safe-zone overlay frame. A failed machine check is fixed before the reviewer sees the file.

## Step 2 — the separate reviewer

Give a fresh reviewer (a subagent with a clean brief; where the host has none, a labelled fresh-context pass): the finals, the contact sheets and safe-zone frames, the approved script, the transcript, the copy and claims list, the proof vault references, this file and `video-compliance.md`. Do not say what verdict you hope for.

**G3 craft:**
- The first two seconds: a clear situation, question or face; the brand on screen.
- Every beat adds something; the hook pays off; nothing is generic filler that would fit any business.
- The member's face and voice are real and clear; no generated person is the hero; generated B-roll is plausible (no warping, flicker, melting edges, phantom text or changing objects) and shows what is being said.
- Captions accurate, readable, off faces, in the safe zone; on-screen text matches the manifest.
- Sound: the voice is clear over music; no clipping, hum or room echo that hurts understanding.
- The ask is clear, matches the destination, and holds long enough to act on.

**G4 compliance:** see `video-compliance.md`. Every claim and number traced to proof; guarantees word for word; no synthetic testimonial, customer or result; consent on file for every recognisable person and every cloned voice or face; the AI label where a generated person appears; music licensed; the destination keeps the promise.

## What a machine and a reviewer cannot verify

Say it plainly in every review:

- **Motion, pacing, performance and feel.** The reviewer works from frames, transcripts and measurements. The member watches the full cut at normal speed with sound before approving, every time.
- **Words, when the transcript was aligned from the script** (no speech engine): a departure from the script cannot show. Listen, or transcribe with an engine.
- **Captions set by SubMagic** are checked from frames and SubMagic's word list, not read back by OCR.

## Repairs

Smallest layer first: captions, then the edit (a different take, a trim, a cutaway), then a generated shot, then a reshoot. Never regenerate a shot to fix a word. At most two repair passes per video by default; the ledger counts them. A repaired file is reviewed again (the ledger resets G3 and G4 when the files change).

## Release states

`briefed` (G0) · `beats approved` (G1) · `script approved` (G2) · `shot` (footage in) · `cut` · `captioned` · `reviewed` (G3 and G4 pass) · `approved` (the member watched and approved) · `kit ready`. Or `partial` / `blocked`, naming exactly what is missing. None of these means "will perform." The member's own results say that.
