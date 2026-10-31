# Build Room OS — Test Run Findings

**Run:** 2026-08-29 · Member simulated = AI Momentum Labs (Lanny Morton)
**Sessions executed:** Build Room OS onboarding → Ideal Client Avatar → (fed into) Signature Offer, Offer Page Copy
**Source material:** Build Room curriculum, 2026 roadmap, product bundles, session cadence.
Obsidian vault and Zoom transcripts were unavailable — which surfaced Finding 1.

---

## What worked

- **The onboarding flow is fast and correct.** Six snapshot questions produced a usable §1 in minutes.
- **The payoff session delivers on the core promise.** Offer Page Copy pre-fills **19 of 21** input fields from a completed file. The "you never re-explain your business" claim holds where it matters most.
- **The file stays small.** A filled file with two sections complete came to **829 words** against a 2,500-word ceiling. Room for all nine months.
- **Prerequisite handling behaved correctly.** With §2 marked provisional, downstream sections correctly inherited the flag.

---

## Finding 1 — "Verbatim language bank" is the system's most dangerous field 🔴

The ICA prompt says *"Write as if you've interviewed 50 of them."* With no real customer data, what comes out is **plausible invented language**. But the Business File template labels §2's bank:

> *Verbatim language bank (5–10 exact phrases clients **actually said**)*

Nothing in the file distinguishes a real client quote from a model-generated one. Three sessions later, Offer Page Copy pulls those phrases as source material for headlines, and Lead Capture pushes them onto a live landing page — **synthetic language ships to real prospects, laundered through the file into looking like customer research.**

This is the single highest-severity issue found. It gets worse over time, not better, because provenance is lost the moment the session ends.

**Fix:** split the field in two — `Verbatim (sourced)` and `Hypothesis (AI-generated, unverified)` — and have the ICA session ask once: *"Do you have any real client emails, DMs, reviews, or call notes? Paste them and I'll mark these as sourced."* Downstream skills prefer sourced phrases and warn when only hypotheses exist.

## Finding 2 — Compounding is weak exactly where members first test it 🟠

Measured pre-fill coverage:

| Session | Fields pre-filled |
|---|---|
| Signature Offer (session 3) | **2 of 8 (25%)** |
| Offer Page Copy (session 4) | **19 of 21 (90%)** |

The member's *second* session — their first chance to feel the payoff — still asks 5 of 8 questions fresh (best result, typical result, engagement structure, why clients don't get results, price). The compounding only becomes obvious at session 4.

That's a retention risk: the habit ("bring the file every time") has to survive two unimpressive sessions before it pays off.

**Fix:** widen §1 to carry delivery facts the file already implies it knows — engagement structure, best result, typical result, price. Capture them during OS onboarding (it's 3 more questions) or opportunistically in any session. That lifts session 3 from 25% to ~75%.

## Finding 3 — The schema assumes one business, one offer 🟠

AI Momentum Labs runs **Build Room, Platinum Mastermind, Wealth Engine Live, and OS Cortex AEO Publisher**. §3 "Signature Offer" is singular, §2 ICA is singular, §5 Offer Page is singular.

Running the ICA session, the first real question was *"avatar for which product?"* — the file has nowhere to put the answer. Any member with a front-end and a high-ticket backend (i.e. most successful ones) hits this in month one. The current guidance ("two businesses? two files") is wrong here: it's one business with several offers sharing one snapshot.

**Fix:** make §2–§5 repeatable per offer — `§2.a ICA — Build Room`, `§3.a Offer — Build Room` — with §1 and §8 staying global. The navigator asks which track the member is working today.

## Finding 4 — No provenance anywhere in the file 🟡

Nothing records where a fact came from: member-stated, AI-inferred, or pulled from a document. By month six nobody remembers which numbers were guesses. I had to invent a §9 Provenance table during the test run because the file was unusable without one.

**Fix:** add a confidence marker per field, or minimally a `Source` column on the riskiest sections (§2 language bank, §3 pricing, §6 metrics).

## Finding 5 — The protocol and the curriculum contradict each other 🟡

`business-file-protocol.md` says:

> *"Never invent facts into the file. Only member-confirmed content goes in."*

The ICA knowledge base's Principle 1 says:

> *"A specific, vivid, slightly wrong ICA beats a vague, technically accurate one."*

Both are right in their own context, but a skill following both literally cannot act. In the test run the avatar "Dana" is entirely model-generated — correct per the curriculum, forbidden per the protocol.

**Fix:** amend the protocol to distinguish *invented facts about the business* (never) from *generated hypotheses about the market* (allowed, but flagged and confirmed).

## Finding 6 — The rating is collected at the wrong moment 🟡

The session asks for a 1–5 rating right after handing over the deliverable — peak satisfaction, before the member has used anything. That measures the experience of the session, not the value of the output.

**Fix:** move it to the *next* session's opening: *"Last time we built your ICA — did you actually use it? 1–5."* Same one question, real signal, and it doubles as a re-engagement hook.

---

## Recommended order

1. **Finding 1** (verbatim/hypothesis split) — highest severity, ships bad copy to real prospects.
2. **Finding 2** (widen §1) — biggest retention effect, smallest change.
3. **Finding 3** (per-offer sections) — structural; cheaper to fix before members have files.
4. Findings 4–6 — polish, batchable.

Findings 1, 2, 4, and 6 are edits to the template and protocol only — no skill rewrites. Finding 3 touches the schema and all seven skills' section references.
