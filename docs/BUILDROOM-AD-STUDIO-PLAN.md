# Build Room Ad Studio — the plan

_Prepared 2026-10-14 for the founder. Inputs: the `create-ads-with-agents` skill (Higgsfield edition, v2.1.2), the Meta Ads Client Brief template, the research report `reports/World class advertising for AI ad studio.md` (five research streams, about 6,900 words), the founder's own vault material, and how Build Room OS already works. Every number below that comes from the research is a search-summary figure, not checked against the primary document; the report lists which ones to verify before they go in front of members._

---

## 1. The thesis

**The incredible ads are the ones with a true, specific idea, a real face and real proof, run in a loop that learns. Generation is the cheap part.**

Three findings decide the design:

1. **Creative is the biggest lever an advertiser controls.** Vendor sales-effect studies put creative quality at about 47 to 49% of advertising-driven sales lift, more than reach, targeting and recency combined. Marketers guess 19%.
2. **Meta's delivery system now rewards distinct concepts, not volume.** Andromeda (retrieval) and GEM (ranking) can only match different people to different ads if the ads are genuinely different ideas. Practitioners report near-duplicates get grouped as one ad. "Creative is the new targeting" is the accurate part of the folklore; "8 to 15 creatives per ad set," "60% similarity threshold" and "Entity ID" are not Meta's.
3. **People detect AI ads and remember them poorly, and the law now targets the studio's exact customers.** NIQ's EEG study: consumers flagged most AI ads unprompted, called them "annoying, boring, confusing," and showed weak memory even for good ones. The FTC's 2024 rule bans AI-generated testimonials at up to about $53K per violation, and its first warning letters went to property managers, injury law firms and an accountant. New York (June 2026) requires on-screen disclosure of AI-generated people in ads; the EU AI Act's Article 50 applies from August 2026.

So the Ad Studio does the strategist's job with machine discipline, and uses generation to **multiply executions around the member's real face, real work and real proof**. It never invents the story, the customer, or the result.

That is also the line between this and the uploaded skill, which is excellent on rigor but built for e-commerce products and locked to Higgsfield. Build Room members sell themselves.

---

## 2. What to keep from the uploaded skill

The `create-ads-with-agents` skill is the most rigorous ad workflow I have seen in a skill file. These parts carry over almost verbatim (credited, adapted, not copied wholesale):

| Keep | Why it matters |
|---|---|
| **Audience first, always.** Purchase situation, desired progress, current alternative, hesitation, poor fit, before any ad is written | It is the Business File's own philosophy. Here it is mostly *read* from §2 instead of researched from scratch |
| **Evidence registry with claim status** (observed, user-provided, inferred, proposed, unsupported) | It is our provenance rule, extended to every claim an ad makes, including what the *picture* implies |
| **Specialist roles:** producer, buyer researcher, ad and funnel analyst, strategist, director, generation operator, evidence and rights reviewer, and a **separate Realism and Anti-Slop Reviewer** who never sees the author's praise | Independent review is the single biggest quality lever in the file |
| **Concept family vs variant**, with the fact / guidance / hypothesis split for anything said about Meta | Matches the research exactly and kills folklore at the door |
| **QUEST for services** (Qualify, Understand, Educate, Stimulate, Transition) and the three service routes: **quiz, case study, direct offer** | Built for exactly our members |
| **The missing-review rule:** no review means a labelled "awaiting authentic review" blueprint, never a placeholder quote | FTC rule, enforced structurally |
| **Image and video direction:** commercial job first, clean midtones, product identity locked to references, cause → contact → consequence in every action, one controllable unit at a time | This is what stops slop |
| **Typography finished in a controlled layer**, not rendered by the model | Kills garbled prices and URLs |
| **Paid-job ledger:** reserve a job key, mark submitting, record the returned ID, reconcile uncertain jobs before any retry, at most two repair passes per asset | Your September 16 warning: "you can spend a lot of money really fast by accident" |
| **Stops at creative delivery.** No launching, budgets or Ads Manager changes | Right default; see section 9 for the optional upload |

## 3. What to change

| Change | From the uploaded skill | In Build Room Ad Studio | Why |
|---|---|---|---|
| **The subject** | E-commerce products; the portfolio is Callout Diagram, Review Card, Offer Card | Service businesses; the portfolio is **founder-led, proof-led, and offer-led**, with QUEST, quizzes and case studies first-class | Members sell themselves, not SKUs |
| **The hero** | Generated people and products | **The member's real face and real work**, filmed on a phone from a shot list; AI makes the scenes, B-roll, statics, resizes and hook variants around them | NIQ, System1/Orlando Wood (real people, faces, place, dialogue build memory), high-involvement purchase, FTC, New York law |
| **Provider** | Higgsfield only, three locked models | **Provider router.** Higgsfield by default (MCP for interactive, its CLI or pay-per-generation API for pipelines), fal.ai pay-as-you-go as the no-subscription path (members of the Video Engine already have the key), HeyGen for a consented founder twin. Models chosen per job, read live with live prices | Prices and rosters changed repeatedly in 2026; Sora was shut down; a hard lock breaks the day a model moves |
| **Audience research** | Researched fresh each assignment | **Read from the Business File.** §2 sourced language, objections and triggers; §4 villain and differentiator; §17 voice. Fresh research only where the file is thin, and it routes to Audience Insight or the Discovery Engine instead of duplicating them | Read before asking; never redo what the file holds |
| **Concept presentation** | No concept stage; generate straight from strategy | **One short concept table** (the angle in one phrase per concept, why it differs, the hook) before anything paid is generated | A coach must recognise themselves in the angle before money is spent; one approval, not a gauntlet |
| **The brief** | A separate client brief document | **§18 Advertising** in the Business File holds only what the file doesn't (see section 6). Everything else pre-fills | One file |

---

## 4. The member experience

Trigger: **"Make me ads"** (also "build my ads," "I need Facebook ads," "my ads aren't working").

1. **The Ad Brief, mostly pre-filled.** The session reads §1–§7, §14, §17 and shows a one-screen brief in the GET / WHO / TO / BY shape: who the ad is for and what they think now, what we want them to do, and the single proposition that gets them there. It asks only the §18 gaps, one at a time: budget, margin per sale, claims the ads must never make, the proof vault, past results. Gate G0: one audience, one proposition that passes Hegarty's three tests (rational sense, emotional sense, works as a rough press ad), one success metric.
2. **The matrix.** A small grid of persona × awareness stage (Schwartz) × angle, built from §2's triggers and objections, showing which cells this month's concepts will cover. Category entry points from Ehrenberg-Bass become the situations ("the week before a launch," "after the second no-show this month").
3. **Three concepts, genuinely different.** Each one a unified picture-plus-words idea (the Bernbach pair), differing from the others on angle, persona, mechanic, format or setting. Each comes with three hooks by tactic (offer, confession, curiosity, bold claim, problem call-out). The member sees one table and picks or edits. Gate G1, scored on the Cannes Direct weights: idea 30, strategy 20, execution 20, predicted impact 30.
4. **Copy, one piece at a time.** Through the Kern framework for short and the Halbert system for long, as every other skill now does. Every line passes Harry Dry's three tests: can I visualise it, can I falsify it, could nobody else say it. Emotion opens, reason closes. Gate G2.
5. **The shoot list.** For founder-led and proof-led concepts: a ten-minute phone shoot plan with exact lines, framing, light and three takes of each hook. The member films; the studio does everything else. Monthly, not weekly.
6. **Production.** Statics: the studio generates the photographic layer, then composes real typography, price, CTA and brand marks in a deterministic HTML renderer, so text is never model-rendered. Videos: the member's A-roll, generated B-roll and scenes, burned-in captions, brand cue in the first two seconds, CTA hold, exported 9:16, 4:5 and 1:1 inside platform safe zones. Every paid job goes through the ledger with a quote first.
7. **Review.** A separate reviewer agent inspects the actual exported files, full video with sound, against the brief and the references. Gate G3 (craft) and Gate G4 (compliance). Pass, revise, or unverified, with the frame or timestamp and the smallest fix.
8. **The launch kit.** Named files ready to upload (structured names so every attribute pivots in reporting), the primary text and headline per ad, the matched landing-page headline per angle, the test plan, and a disclosure sheet. The member uploads, or (later) the studio uploads them paused.
9. **The learning loop.** Two weeks later: "How did my ads do?" The Funnel Scorecard reads results; the studio diagnoses by layer and drafts next month's brief.

## 5. The quality gates (where "incredible" lives)

| Gate | Passes only when | Grounding |
|---|---|---|
| **G0 Brief** | One audience, one proposition passing Hegarty's three tests, one success metric, mandatories from §18 | IPA *Better Briefs*; GET/WHO/TO/BY |
| **G1 Concept** | Angle stated in one phrase; survives a change of format; a reviewer would call the insight non-obvious; differs from the last ten tested on at least one axis; scored idea 30 / strategy 20 / execution 20 / impact 30 | D&AD ("inspiring, brilliantly executed, fit for purpose"); Cannes Direct; Andromeda diversity logic |
| **G2 Copy** | Every line visualisable, falsifiable, ownable; a number or named result in place of every adjective; hook states the situation or benefit inside three seconds; length set by awareness stage | Harry Dry; Hopkins; Upworthy's 105,000 randomized headline tests; Schwartz |
| **G3 Craft** | Distinctive brand asset early; reads on mute; safe zones clear; no model-rendered price or URL; faces, hands, product, continuity intact; a real human present unless a lo-fi static; action completes; CTA holds | System1 early branding; TikTok/Kantar (about 90% of recall impact in the first 6 seconds); the uploaded skill's anti-slop checklist |
| **G4 Compliance** | No synthetic testimonial, result, rating or customer; every quote traced to the proof vault with consent; AI-person disclosure applied; C2PA metadata kept; never-say claims absent; political and social-issue ads blocked; likeness consent on file; audit log written | FTC 16 CFR 465; New York synthetic performer law; EU AI Act Art. 50; Meta SIEP policy |

Then **the member approves every ad**. No gate can be skipped by a "looks good," and none of them is a numerical beauty score.

## 6. The new Business File section: §18 Advertising

Your client brief template asks for eight sections. Six already live in the file. §18 holds the rest, and nothing that is already elsewhere:

- **Budget** (amount · period) and **margin per sale before advertising.** The margin decides whether paid traffic can work, and connects to the Traffic Strategy price gates.
- **Claims the ads must never make** and **who the offer is wrong for.** The compliance guardrail every ad is checked against.
- **Proof vault** (location): consented testimonials with source and date, real numbers, review count and rating, founder photos and footage, client work.
- **Brand kit:** the one to three distinctive assets locked for repetition (face, colour, name, line, shape), scored on Romaniuk's fame × uniqueness grid. Stays fixed for months; only executions rotate.
- **Platforms and accounts:** Meta ad account ready yes/no, LinkedIn for B2B members, who approves.
- **Past results** (campaign · dates · spend · leads · qualified leads · counting rule).
- **Learning library** (location) and **current cycle** (month · concepts in test · winner · next brief).

## 7. The architecture

One skill, `buildroom-ad-studio`, in the house pattern: a SKILL.md orchestrator, references, and scripts.

**References** (adapted from the uploaded skill plus the research):

| File | Holds |
|---|---|
| `ad-principles.md` | The rulebook: the classic traditions mapped to the feed, the effectiveness evidence, the four conflict resolutions (default to direct response with brand cues in every ad; emotion opens, reason closes; awareness sets length; clear beats clever; when traditions disagree, test both) |
| `service-portfolio.md` | QUEST; the formats for services: founder to camera, client testimonial (real only), deliverable demo, quiz, case study, offer card, lo-fi statics (notes app, "us vs them," listicle, whiteboard); LinkedIn Thought Leader and document ads for B2B |
| `concept-matrix.md` | Angle → mechanic → hook → format; persona × awareness; hook tactics with Motion's hit rates as priors, not rankings |
| `image-direction.md`, `video-direction.md`, `typography.md` | Adapted from the uploaded skill; "Higgsfield only" removed, provider-neutral |
| `generation-router.md` | Jobs to models: in-image text → Nano Banana Pro; volume statics → Seedream; dialogue and lip sync → Veo 3.1; consistent character or product across shots → Seedance 2.5; cheap B-roll → Kling 3.0; founder twin → HeyGen with consent; never Sora. Live catalog and price check before every batch |
| `compliance.md` | FTC, New York, EU, Meta, YouTube, TikTok, rights and likeness; the disclosure sheet |
| `testing-and-learning.md` | The small-budget loop below; metric diagnosis by layer; fatigue rules |
| `business-file-protocol.md` | As every skill |

**Scripts:**

| Script | Does |
|---|---|
| `gen.py` | Provider adapter (Higgsfield API or CLI, fal.ai, HeyGen): `--dry-run` shows every request and its price, `--probe` confirms keys and models, real runs go through the ledger. Same pattern as the GHL push and the certainty adapter |
| `ledger.py` | Adapted from the uploaded `workflow_state.py`: reserve, submitting, record, reconcile, spend cap from §18, two-repair ceiling |
| `render_static.mjs` | Deterministic static compositor in Chromium: generated photo + real fonts + exact copy + brand kit + safe-zone overlay check, exports every ratio |
| `assemble_video.py` | ffmpeg: A-roll + B-roll, burned captions, brand cue in the first two seconds, CTA hold, loudness, exports per ratio |
| `review_pack.py` | Contact sheets, safe-zone overlays, OCR text check against the copy manifest, for the reviewer agent |
| `ad_library.md` + browser route | Meta Ad Library scan of local and niche competitors, via the browser the member already has; observed patterns are hypotheses, never "proven winners" |

**Provider sign-up links.** The router's setup step, and the member docs that explain it, send a member without an account to these links. Each one carries the disclosure beside it, in the same words everywhere: *"This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you."* The setup step never hides the plain sign-up route; a member who already has an account just adds their key to `.env`.

| Provider | Link | Status |
|---|---|---|
| Higgsfield | `https://higgsfield.ai?fpr=lanny-756d90` | Ready. Program pays recurring commission for 12 months through Impact.com; new sign-ups may see a time-limited discount. Confirm current terms before quoting a percentage to members |
| fal.ai | Pending | Waiting on the link |
| Kie.ai | `https://kie.ai?ref=62126a8991d5546179db893d9bc15a7c` | Ready. Pay-as-you-go credit aggregator (Veo, Seedance, Wan, Nano Banana and others), no subscription; reviews report failed jobs aren't charged. A candidate cheap route in the router alongside fal.ai. Commission terms not found publicly; confirm before quoting |
| HeyGen | None | Plain sign-up link only |

## 8. The testing and learning loop for small budgets

Statistical testing is mostly out of reach at $300 to $3,000 a month, so the loop is honest about it:

- **Monthly cycle, not weekly.** One brief, two or three genuinely different concepts, two or three hooks on the strongest, 10 to 14 days, about 20% of budget in Meta's creative testing tool or a small sandbox ad set.
- **Judge on the account's own baseline,** not internet benchmarks (they conflict: "good" hook rate is quoted anywhere from 18 to 40%). Hook rate, hold rate, CTR, and **cost per qualified lead from the CRM**, never the platform's lead count alone.
- **Diagnose by layer:** weak hook rate → the opening; good hook, weak hold → the body; good hold, weak CTR → the offer or CTA; good CTR, weak conversion → the landing page. Kill an angle only after two or three differently hooked executions of it fail.
- **About 60 to 70% new concepts, 30 to 40% iteration** at this volume (an inference; big accounts run closer to 90/10), and 20 to 40% of variants as value-first content with no ask, building the retargeting pool most buyers need because they are out of market at any moment.
- **Fatigue by frequency relative to audience size,** not spend: a narrow local audience saturates fast. Refresh with a new hook or concept on the same brand platform, never a colour swap.
- **The learning library** logs each concept's hypothesis, name ID, spend, metrics, verdict, the failed layer and the next action, and drafts next month's brief. The report flags this handoff as the gap even leading agency tools leave manual. It is the studio's edge.

This plugs into what exists: the **Funnel Scorecard** reads the ad results as stages; the **Decision Machine** catches every lead the ads produce; the **Traffic Strategy** decides whether paid traffic is even on (price gates, measurement first); the **landing page and application** come from Offer Page Copy and Lead Capture, and the studio writes the angle-matched headline for each.

## 9. Build it in three phases

| Phase | Ships | Done when |
|---|---|---|
| **1 · Statics and the brain** (first) | The skill, §18, the brief, matrix, concepts, copy, gates G0–G4, the reviewer agent, `render_static.mjs`, `gen.py` and `ledger.py` for images only, the launch kit and disclosure sheet | One real member's file produces three distinct static concepts, each with three hooks, in three ratios, through every gate, with a dry run and a live run on your own account |
| **2 · Video** | The shoot list, `assemble_video.py`, video routes in the router, HeyGen twin with consent, full-media review | A founder-led and a proof-led video assembled from real phone footage plus generated B-roll pass G3 on full playback with sound |
| **3 · The loop** | Ad Library scan, results intake through the Funnel Scorecard, metric diagnosis, the learning library, the auto-drafted next brief, fatigue monitor | A second monthly cycle is briefed from the first cycle's logged results with no re-entry |
| **4 · Optional upload** | Upload approved ads to Meta **paused**, through the Marketing API with the member's token in `.env` | Only if you want it; the uploaded skill deliberately stops at delivery, and so does this plan until you decide |

## 10. Decisions for you

1. **Provider.** Recommended: Higgsfield as the default hub with fal.ai as the pay-as-you-go path, both behind one router with live prices and a monthly spend cap in §18. Kie.ai is a second pay-as-you-go option the router can price against fal.ai per job. Every sign-up goes through your affiliate links with the disclosure beside them (section 7). The alternative is the uploaded skill's hard lock to Higgsfield and its three models.
2. **Generated people.** Recommended: no photoreal AI people as heroes, ever; AI people only as clearly secondary background figures, auto-disclosed. The founder twin only with written consent. The alternative is allowing AI presenters with disclosure, which the evidence says costs trust exactly where members sell.
3. **Upload.** Recommended: stop at an upload-ready kit in phase 1 to 3. Decide on paused upload after phase 3.
4. **Attribution of the uploaded skill.** Its workflow and direction references are substantial original work. If it came from someone else, confirm we may adapt it, and credit it in the references as we did for the Codex Prompt Library and the Genie.
5. **The first test member.** Recommended: AI Momentum Labs itself, your Install Call funnel, the same way the Funnel Scorecard dry run used your §6.

## 11. Verify before it reaches members

The research could not fetch most primary pages. Before any of these appear in member-facing material, check them against the source: the NCSolutions creative share (47% / 49%), Field's creativity multiplier (12x falling below 4x), the Binet & Field category splits, Meta's creative testing tool limits and the 20% budget suggestion, Higgsfield's API prices, the New York law's signing date, the EU Article 50 deferrals, whether Meta auto-labels third-party AI ads, and the Higgsfield, fal.ai and Kie.ai affiliate terms and Kie.ai's per-model prices. The full list with sources is at the top of the research report.
