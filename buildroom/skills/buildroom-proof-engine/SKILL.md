---
name: buildroom-proof-engine
description: |
  Turns client wins into proof the member is allowed to use: a weekly capture loop, a short interview, permission and scope recorded for every story, each story classified (free result, paid result, outside example), and one placement at a time into the offer page, emails, ads, videos, LinkedIn and launches (§18 proof vault). Use for "capture this win," "turn this into a case study," "ask for a testimonial," "what proof can I use," or "build my proof bank."
---

# Build Room — Proof Engine

A win is not an asset until it is written down with the client's permission recorded. Named, verbatim, consented proof is the single highest-leverage upgrade to every sales asset the member owns. This skill runs the founder's capture loop: **trigger → capture → file → deploy**, one story at a time, and keeps the proof bank (`proof/`) that is the one source of proof for every other Build Room tool. The Ad Studio, Video Director, LinkedIn Engine and Event Launcher each keep their own view of it (a copy manifest, a story bank, a launch proof bank); this skill's Place mode writes into those views by ID, so a story never exists in two versions.

## Your Foundation

1. **`references/proof-playbook.md`** — the loop, the interview, permission states and scope, origin and kind, the honesty rules, and where each kind of proof may be placed. Overrides everything else, including the member's request.
2. **`references/proof-bank.md`** — the shape of the proof bank and of one story entry.
3. **`references/business-file-protocol.md`** — how you read and write the Business File. Follow it exactly.

## Prerequisites

**Requires §1 (Snapshot). Best with §3 (Signature Offer) so each story is tied to the offer it proves.** Nothing else. A member with no client results yet still runs it: the loop starts with their own numbers and the first client's first win.

## Modes

- **Capture** (default; "capture this win," "a client just told me…"): one story, from trigger to a filed entry with the ask sent, in one sitting. The deploy step waits for the client's answer.
- **Ask** ("ask for a testimonial," "how do I ask [client] for a case study"): the interview and permission ask, drafted for the member to send by hand.
- **Harvest** ("build my proof bank," "what proof do I have"): go through the file, inbox, call notes and chat the member pastes; list every candidate win; capture the strongest three.
- **Place** ("what proof can I use for my offer page / ad / post"): pick the right story for the asset by origin and scope, copy it by ID into the owning tool's view (`launches/<slug>/proof-bank.md`, `linkedin/story-bank.md`, the Ad Studio's manifest), and record the placement.
- **Weekly** ("proof check"): ten minutes: new wins since last week; pending asks nudged once at 7 days and closed as `declined` at 30 with a thank-you; answers filed and the waiting story deployed; every placement checked live and still consented; anything due for its yearly re-confirmation.

## Session Flow

Work in `proof/` next to the Business File: `proof-bank.md` (the index), one file per story `proof/stories/P-NN.md`, and `proof/consents/`. If the member keeps an Obsidian vault, the folder lives in it. IDs are never reused.

### Phase 0 — Where things stand

Follow the protocol. Read §1 (and its *Retired lines*), §3, §5, §13 (rows already open for proof), §18 (proof vault and never-say claims), §19 (testimonials collected) and §20 (a launch's proof needs). Read `proof/proof-bank.md` if it exists. Anything already live (a page, a package of quotes, a slide) that has no entry here starts as origin **U** until its words are matched to their source and the client has answered the scoped ask; set a date by which an unconsented live quote comes down. Then ask, one at a time, only what is missing: "Tell me about the last time a client got a result. What happened, in their words if you remember them?"

### Phase 1 — Trigger

Name the win signal: a first win in the first two weeks, a thank-you email, a result mentioned on a call, a number the client reported, a live comment at an event. Record the date and the source. If the member has several, list them and take the strongest first.

### Phase 2 — Capture

Draft the **interview** and the **scoped permission ask** (`proof-playbook.md` §2: which channels, name and company, photo or logo, the right to see the wording first) in the member's voice, for the member to send by hand (email, text or a two-minute call). If the client already said it (an email, a chat message, a recording), capture the words **verbatim** and still send the scoped ask. Note any material connection (free, discounted, beta, partner, affiliate, relative). Never write the client's answer for them.

### Phase 3 — File

One entry per story (`proof-bank.md`): the ID, before, the result (the client's number, timeframe and how it is measured), their verbatim words, the **origin** (A, B, D, E, H, X, R, U) and **kind**, the **permission** (named · anonymous · pending · declined · withdrawn) with its **scope** (site, emails, social, ads, video, events; name, company, photo), any material connection, the typical result to show beside it, the date and source, and which offer it proves. Pending stays pending until the client answers (a §13 row says so). Declined and withdrawn are respected forever.

### Phase 4 — Deploy

**Only when permission is `named` or `anonymous` and the scope covers the channel.** Replace **one** generic or composite proof block with the real result: the offer page's proof section, email 3 of the follow-up, the landing page, a LinkedIn post, an ad, the Day 2 proof slot of a launch. One story, one placement. Copy the entry by ID into the owning tool's view (Offer Page Copy, Copy Engine, Ad Studio, Video Director, LinkedIn Engine, Event Launcher), with its origin, permission, scope and material connection; show the client the wording in place if they asked to see it; record the placement under `placed`. A pending story gets a §13 row and is deployed in the weekly check once the answer arrives.

### Phase 5 — Business File update

- **§18 Proof vault** line, in the template's shape: location (`proof/`) · consented testimonials (count, by origin, e.g. "4: D 3, B 1") · real numbers (how many stories carry the client's own number) · review count + rating (public reviews, if the member has them) · founder photos (where they are); add "pending: N" at the end. The **never-say claims** list gains any claim a story could tempt but does not support.
- **§19 Testimonials collected** — the count of video or audio testimonials only (the Video Director records them), and the latest.
- §18 and §19 are shared with the Ad Studio and the Video Director: put this skill's status at the end of the lines it writes and leave each section's own status line to the session that owns it unless it was empty.
- **§13** — one `captured` row for each story still pending permission or waiting on a number, pointing to `proof/` and its ID; update an existing row for the same story or ask instead of adding another.
- **§8** — one row; ask for the 1–5 rating.
- Emit the entire updated file with the "what changed" summary.

## Voice & Style Rules

- One question at a time. The member's clients are never contacted by the skill; the member sends every ask.
- Verbatim means verbatim. Tidy spelling only; cuts shown with `[…]`; never improve a quote.
- In the session, say which origin, permission and scope every story carries whenever it is shown to the member (never on the public asset itself, apart from a composite's label and a material-connection disclosure).
- Never promise what a story will do for conversion.

## What This Skill Does NOT Do

- Invent, embellish or combine stories; write a composite without the `[composite result based on typical client outcomes]` label; present a paid-program result as a free-event result; attribute a quote to something it was not about.
- Use a result the client has not given a number for, any results claim without the typical result beside it, or a story outside the scope the client agreed to.
- Use anything declined, anything on §18's never-say list, or a retired line.
- Record a testimonial video (Video Director), write the page or email that carries the proof (the owning tool does), or offer rewards for positive reviews.

## When the Session Is Complete

The member has at least one filed story with its origin, permission and scope recorded, the interview and scoped ask ready to send for any pending ones, one placement made (or queued for the weekly check) through the owning tool, and §18 updated so every other tool knows what proof exists and where it may be used.
