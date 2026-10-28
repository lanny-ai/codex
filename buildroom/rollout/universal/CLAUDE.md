# Build Room OS

This folder is a Build Room member's workspace. The Build Room (AI Momentum Labs) is a program of guided weekly builds for service businesses, coaches, consultants, and agencies. Thirty-two skills live in this folder; every one of them reads and updates the member's **Business File**.

## The Business File

- Path: `./BUILDROOM_BUSINESS_FILE.md` in this folder. It is the member's single source of truth: avatar, offer, positioning, funnel, SOPs, role, training, weekly ops, build plan, lead gen engine, sales conversations, follow-up engine, founder compass, advertising, video (§1–§21, with §8 Session Log last).
- **Read it at the start of every Build Room session** before asking the member anything. Pre-fill from it; ask only what is missing.
- **Write it back at the end of every session** per the skill's protocol (`references/business-file-protocol.md` inside each skill). When the protocol says "emit the full updated file in a code block," in this environment that means: also write the updated file to `./BUILDROOM_BUSINESS_FILE.md` directly, preserving every section you did not change byte-for-byte, and tell the member what changed.
- Member edits win. Never overwrite a hand edit silently. Never write a fact the member has not confirmed. Never invent a number.
- If the file is missing or blank, run the navigator's §1 intake to create it.

## Where to start

A member who says "set me up," "where do I start," or anything about the Build Room without naming a build gets the `buildroom-os` navigator. It reads the file and recommends exactly one next session with the phrase to start it.

## Skills in this folder

`buildroom-os` (navigator) · `buildroom-ideal-client-avatar` (§2) · `buildroom-signature-offer` (§3) · `buildroom-positioning-messaging` (§4) · `buildroom-offer-page-copy` (§5) · `buildroom-funnel-map` (§6) · `buildroom-lead-capture` (§7) · `buildroom-sop-creator` (§9) · `buildroom-hiring-kit` (§10) · `buildroom-training-docs` (§11) · `buildroom-ops-dashboard` (§12) · `buildroom-decision-machine` (§16) · `buildroom-leadgen` (§14) · `buildroom-sales-script` (§15) · `buildroom-audience-insight` (§2 sourced language) · `buildroom-offer-deep-dive` (§3) · `buildroom-copy-engine` (§8 only) · `buildroom-brainstorm` (§8, §13) · `buildroom-brainstorm-capture` (§13) · `buildroom-compass` (§17) · `buildroom-ad-studio` (§18, §13; ads folder `ads/YYYY-MM/`) · `buildroom-video-director` (§19; §18 proof vault, §14, §5/§15 references; videos folder `videos/`) · `buildroom-linkedin` (§14 LinkedIn lines, §13, §8; folder `linkedin/`) · `buildroom-event-launcher` (§20, §13, §8; folder `launches/`; reads and writes launch notes in the member's Obsidian vault) · `buildroom-proof-engine` (§18 proof vault, §19 testimonials count, §13, §8; folder `proof/`) · `buildroom-search-answer-engine` (§21; one §14 channel row; §18 review count and rating) · `buildroom-discovery-engine` (§1–§4 provisional, §13; client file; prospect brief) · `buildroom-funnel-scorecard` (§6 scorecard lines, §13, §12) · `buildroom-obsidian`, `buildroom-source-watcher`, `buildroom-boardroom`, `buildroom-agent-forge` (electives: at most a §1 tools line, one §13 row, §8)

Each skill's `SKILL.md` is the orchestrator; its `references/` hold the curriculum (knowledge base, prompt system), the protocol, and the blank template. Follow the SKILL.md; it says which references to read first.

## Tools

`tools/Rent_Calculator.html`, `tools/Brainstorm_Board.html`, `tools/Business_File_Viewer.html`, and `tools/BuildRoom_OS_Quick_Start.html` are browser pages for the member, not for you. If a member pastes a "BRAINSTORM BOARD EXPORT" block, that is input for `buildroom-brainstorm-capture`. If they paste a "## 9. Operations & SOPs" block from the Rent Calculator, merge it into the file as a provisional §9.

## Rules for this folder

- Do not restructure, rename, or "clean up" `BUILDROOM_BUSINESS_FILE.md`, the skills, or this file.
- Deliverables (an offer page, an SOP library, a training handbook, an ops pack) are saved as their own files next to the Business File, named as the skill instructs, and referenced from the file by name.
- One question at a time during intake. Never re-ask what the file already answers.
- **Every email, SMS, ad, page, or letter any skill writes for the member's customers goes through the Kern framework (short, conversational pieces) or the Halbert writing system (long-form, story, proof), from the `references/` of the skill you are in or from `buildroom-copy-engine/references/`. One piece per output, approved before the next. Never write a sequence in one message. Never quote hypothesis-tagged language as a client's words.**
- **Ads:** a member who wants ads made (concepts, images, a kit to upload) gets `buildroom-ad-studio`; a single ad's words only, the Copy Engine. No ad ever shows a generated testimonial, result, rating or customer, or a photoreal AI person as its hero; every word on an ad image is set by the renderer, never by an image model; no paid generation outside the Ad Studio's ledger and cap.
- **Video:** any video (ad, content, sales, testimonial) goes through `buildroom-video-director`. Real footage of the member first; generated footage never plays the member, a customer or a result; an avatar twin only with written consent on file; captions match the approved words; the member watches every final with sound before it ships.
- **LinkedIn:** anything for LinkedIn (profile, posts, carousels, comments, connection requests, DMs, the weekly scorecard) goes through `buildroom-linkedin`. The member does every action on LinkedIn by hand; never automate, scrape, use pods or engagement bait, and never send a message for them.
- **Launch events:** any challenge, bootcamp, workshop, webinar or launch goes through `buildroom-event-launcher`. Nothing goes to registrants until its launch gate passes (checkout tested, follow-up workflows on, reminders timed in the attendee's time zone, proof classified and consented, deadlines real); no fake countdowns, no earnings claims beyond typical results, and partner copy never implies someone will appear who won't.
- **Proof:** every client story, number or quote any skill uses comes from the proof bank (`proof/`, kept by `buildroom-proof-engine`) with its class and permission; verbatim only, nothing pending or declined, composites labelled, paid-program results never presented as free-event results.
- **Search and answers:** anything about being found on Google, Maps, YouTube or in AI answers goes through `buildroom-search-answer-engine`: the Business Profile before pages; one honest answer page a week through its gate (the answer first, a claim ledger, the member's own view, the typical result beside any claim); reviews asked the same way from everyone, never incentivised, never gated; nothing retired recommended (Q&A seeding, FAQ schema, llms.txt, star markup, templated city pages); never a page built for a machine.
- **Retired lines:** anything listed under §1 *Retired lines* in the Business File is never used again, in any output, by any skill.
- **Keys** (`GHL_API_KEY`, `HIGGSFIELD_API_KEY`, `KIE_API_KEY`, `SUBMAGIC_API_KEY`, `HEYGEN_API_KEY`, the publishing keys `WP_APP_PASSWORD`, `WEBFLOW_API_TOKEN`, `SHOPIFY_ACCESS_TOKEN`, `WIX_API_KEY`, `INDEXNOW_KEY` and the like) live in `.env` in this folder. Never print them, never ask the member to paste them in chat.
