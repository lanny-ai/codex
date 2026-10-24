# Image direction — plates that don't look like slop

Adapted, provider-neutral, from the `create-ads-with-agents` skill's image direction (itself drawn from its author's CINEIMAGE v2.7 production principles); see `source-credit.md`. This file controls what a generated plate shows and how its prompt is written. The brief controls the message. A good plate makes the member's face, proof and next step easier to understand; it is never the point.

## Start with the commercial job

Before writing a prompt, record only what changes the result:

- **Purpose:** scene plate, object, physical-text plate, or repair.
- **Layout and slot:** which renderer layout, which ratio, and where the photo area sits. The plate is composed for that area, with quiet space where the words and the member's photo go.
- **The one message** the ad carries and what the picture must make easier to believe.
- **Hard constraints:** no people (default), no brands, no writing (unless physical text is the job), nothing that implies a claim the vault cannot back.
- **References** and the one role each is allowed to supply ("Reference A supplies the room layout only").

## People

Plates are **empty of people by default**. Say "No people" and extend it to windows, mirrors, screens and printed portraits that could sprout accidental occupants. The face in the ad is the member's real photo, composed by the renderer. A generated person may appear only as a clearly secondary background figure, never photoreal-hero, and the ad then carries the AI-imagery label (see `compliance.md`).

## Hierarchy and the spatial map

For a scene, give a compact left / centre / right map with foreground, midground and background, and mark the empty areas as **copy space** or **photo space** so the model does not fill them.

| Zone | Foreground | Midground | Background |
|---|---|---|---|
| Left | Edge of a desk | Closed laptop, one notebook | Window giving daylight |
| Centre | Clear desk surface (copy space) | — | Quiet wall |
| Right | — | Desk lamp, off | Bookshelf, out of focus |

Check gravity, contact shadows, scale, support and usable space. Count objects only where duplication is likely.

## Objects and deliverables

A plate of a printed report, planner or phone is a **mock-up**, not proof. Generic content only: no client names, no real data, no results, no dashboards showing numbers, no app ratings, no booked calendars. If the ad needs the real deliverable, photograph the real one.

## Camera and composition

State viewpoint, shot size, direction and camera height. Naturally proportioned objects, readable verticals, enough depth of field for the subject. No automatic ultra-wide, extreme bokeh, lens flare or "cinematic" crop. Replace "premium," "stunning," "8K," "cinematic" with visible decisions: where the light comes from, how big the subject is, where the quiet space is.

## Light and colour

Name the source, its side and quality, and where it falls off ("window light from frame left across the desk; the shelf behind stays darker"). Keep a broad readable middle: grey stays grey, off-white stays off-white, wood stays brown. A warm lamp warms only what is near it. **No orange-and-teal wash, no haze, no grain as a default.** If the member's brand colour should appear, place it on one real object (a mug, a folder), not as a colour cast.

## Physical text

When writing on a real surface is the job (a handwritten note, a whiteboard, a sticky note), give its carrier and the **exact words with line breaks**, and say "no other writing." Check every letter after generation. The CTA, any price and any URL still go in the renderer layer. A handwritten note is a format, never a fake customer note or signature.

## Prompt order

Plain production prose, in this order, only what applies: purpose and subject; the spatial map; camera; objects and materials; light; local colour; occupancy ("No people…"); exact physical text; a short list of likely failures to avoid. Keep workflow notes out of the prompt.

## Worked example (a service business)

**Purpose:** scene plate for a `photo-hook` 4:5 ad for a bookkeeping practice; the member's real headshot will be inset bottom-left; the hook sits in the top third.

```text
A calm small-office desk photographed at seated eye height from the front, for a vertical 4:5 advertisement. The top third of the frame is a plain warm-white wall with nothing on it, left empty for text. Across the middle, a pale oak desk runs edge to edge. On the right of the desk, one closed grey laptop and a single neat stack of paper receipts held by a black binder clip; on the left, a ceramic mug in deep green and a pencil lying parallel to the desk edge. The lower-left quarter of the desk surface is clear and uncluttered.

Soft morning window light comes from outside frame left, falling across the desk and fading toward the right; the wall stays evenly lit, with a gentle shadow under the laptop and the mug. Colours stay true: warm-white wall, natural oak, grey laptop, green mug, white paper. No colour cast.

No people, hands, faces or reflections of people anywhere, including on the laptop lid. No writing, logos, brand marks, screens showing content, or text on the receipts that can be read. Exactly one laptop, one mug, one stack of receipts.
```

**Acceptance checks:** top third quiet enough for three lines of type; lower-left clear for the headshot inset; no readable writing; no person or reflection; green mug carries the brand colour on one object; light falls from the left consistently.

## After generation

Inspect at full size and at phone size before the renderer uses it: subject and space as specified, no phantom text or logos, no warped objects, plausible contact and light, colours true, the photo and copy areas clear. A plate that fails is fixed at its prompt, once or twice, never by generating twenty and picking one.
