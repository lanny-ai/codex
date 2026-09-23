# Build Room OS

This folder is a Build Room member's workspace. The Build Room (AI Momentum Labs) is a program of guided weekly builds for service businesses, coaches, consultants, and agencies. Thirteen skills live in this folder; every one of them reads and updates the member's **Business File**.

## The Business File

- Path: `./BUILDROOM_BUSINESS_FILE.md` in this folder. It is the member's single source of truth: avatar, offer, positioning, funnel, SOPs, role, training, weekly ops, build plan (§1–§13, with §8 Session Log last).
- **Read it at the start of every Build Room session** before asking the member anything. Pre-fill from it; ask only what is missing.
- **Write it back at the end of every session** per the skill's protocol (`references/business-file-protocol.md` inside each skill). When the protocol says "emit the full updated file in a code block," in this environment that means: also write the updated file to `./BUILDROOM_BUSINESS_FILE.md` directly, preserving every section you did not change byte-for-byte, and tell the member what changed.
- Member edits win. Never overwrite a hand edit silently. Never write a fact the member has not confirmed. Never invent a number.
- If the file is missing or blank, run the navigator's §1 intake to create it.

## Where to start

A member who says "set me up," "where do I start," or anything about the Build Room without naming a build gets the `buildroom-os` navigator. It reads the file and recommends exactly one next session with the phrase to start it.

## Skills in this folder

`buildroom-os` (navigator) · `buildroom-ideal-client-avatar` (§2) · `buildroom-signature-offer` (§3) · `buildroom-positioning-messaging` (§4) · `buildroom-offer-page-copy` (§5) · `buildroom-funnel-map` (§6) · `buildroom-lead-capture` (§7) · `buildroom-sop-creator` (§9) · `buildroom-hiring-kit` (§10) · `buildroom-training-docs` (§11) · `buildroom-ops-dashboard` (§12) · `buildroom-brainstorm` (§8, §13) · `buildroom-brainstorm-capture` (§13)

Each skill's `SKILL.md` is the orchestrator; its `references/` hold the curriculum (knowledge base, prompt system), the protocol, and the blank template. Follow the SKILL.md; it says which references to read first.

## Tools

`tools/Rent_Calculator.html`, `tools/Brainstorm_Board.html`, and `tools/BuildRoom_OS_Quick_Start.html` are browser pages for the member, not for you. If a member pastes a "BRAINSTORM BOARD EXPORT" block, that is input for `buildroom-brainstorm-capture`. If they paste a "## 9. Operations & SOPs" block from the Rent Calculator, merge it into the file as a provisional §9.

## Rules for this folder

- Do not restructure, rename, or "clean up" `BUILDROOM_BUSINESS_FILE.md`, the skills, or this file.
- Deliverables (an offer page, an SOP library, a training handbook, an ops pack) are saved as their own files next to the Business File, named as the skill instructs, and referenced from the file by name.
- One question at a time during intake. Never re-ask what the file already answers.
