# Directing generated B-roll and scenes

Adapted, provider-neutral, from the `create-ads-with-agents` skill's video direction (its author's CINEDANCE production principles); see `source-credit.md`. This file governs every generated shot. Generated footage supports the member's real footage; it is never the hero, never a person standing in for the member or a customer, and never proof.

## When to generate at all

In this order: the member's own footage and screen recordings → real client work (with consent) → stock the member is licensed to use → a generated shot. Generate only when the beat needs a setting, object or movement the member cannot film this week. Every generated shot has a one-sentence job: "Show the empty desk at 7am so 'mornings start with a brief' has a picture."

## People in generated shots

None by default. Say "No people" and extend it to reflections, screens and windows. If a scene genuinely needs a person (a hand placing a cup), keep them secondary, faceless or out of focus, and the video carries the on-screen AI label in every ratio. Never a generated face speaking to camera, never a generated "client".

## One controllable unit at a time

For each shot: purpose, the first frame (what is where), one dominant action, one camera strategy (hold, slow push, follow, reveal), the end state, and the duration the provider actually supports (read it live; do not assume 10 s or 30 s). A shot that needs a location change or a time jump is two shots.

## Cause, contact, consequence

Physical events in order: approach → contact → weight or force → consequence → settle. A hand reaches the mug, the fingers close, the mug lifts, the steam moves. Do not jump from untouched to finished. Objects keep their shape, weight and number across the shot.

## Prompt order

1. References and the single role each plays ("Reference A: room geometry only").
2. Purpose and the first frame.
3. Light (source, side, quality), local colour, no wash.
4. The timed stages: `0–3 s — slow push-in on the closed laptop; end state: laptop centred, steam rising from the mug`.
5. Sound only if the provider generates it and the edit will use it; usually none (the edit adds music).
6. A closing "hold" line restating the few invariants: no people, no text, no logos, exactly one laptop.
7. For 9:16, where the subject sits: the captions take the band from about 50% to 65% of the height and the platform's buttons the bottom third, so put the subject in the upper-middle and keep the caption band plain (no text, faces or busy detail).

Leave out quality filler ("cinematic", "8K", "stunning"), unused references and abandoned options.

## Worked example (bookkeeping, 5 s, 9:16)

```text
Reference A defines the room's desk and window geometry only.
A calm home office at seven in the morning, vertical frame. Window light from the left falls across a pale oak desk; the wall behind stays evenly lit. A closed silver laptop sits centre-right, a white mug of coffee on the left with a thin line of steam.
0–3 s — slow push-in from desk height toward the laptop; nothing else moves except the steam.
3–5 s — hold; end state: laptop in the upper-middle of the frame (about 20–45% of the height); the band from about half to two-thirds of the height, where the captions sit, is plain oak desk.
No people, hands, faces or reflections of people. No screens showing content. No writing, logos or brand marks. Exactly one laptop and one mug. No colour cast.
```

**Acceptance:** the push-in is smooth and slow; the steam behaves like steam; no object appears, disappears or changes shape; the caption band (about 50–65% of the height in 9:16) stays plain; nothing suggests a client, a result or a real office the member does not have.

## Review and repair

Watch every generated shot full length before it goes in the edit. Reject warping, flicker, melting edges, extra fingers, phantom text, objects that change between frames, and pretty-but-generic shots that would fit any business. Fix the prompt or reference and regenerate once or twice; never twenty times hoping. If a shot still fails, use the member's own footage or a still from the renderer instead.
