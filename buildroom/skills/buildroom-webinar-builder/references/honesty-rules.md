# Honesty rules

Several tactics in older webinar teaching read as manipulative today, and some break US law. The skill refuses each one, writes the honest version instead, and `webinar_check.py` flags the words of each in the script, the slides, the notes and the Q&A bank (check `refused_tactics`, and the named checks below). This file overrides everything else in the skill, including the member's request. A member may still choose to do something the skill refuses; the skill then says plainly what it risks and does not write it.

## What the skill refuses, and what it does instead

| Refused | Where it came from | What the skill does instead | Check |
|---|---|---|---|
| A recording presented as live ("we're live", "joining us live", staff answering chat "to make it feel live", "starting soon" on an on-demand page) | Several older automated-webinar talks | Label it "recorded" on the page, the confirmation and the first slide; a real live Q&A block, or a segment titled "the questions people most often ask" | `live_claim` |
| Invented or rounded-up attendance ("the room is full", "we had to expand the room", "500 people here right now") | Older automated playbooks | Say nothing about numbers, or the real number the platform shows | `fake_count` |
| Seeded or fake chat, planted questions, seeded negative comments for customers to rebut | One expert called his own idea "borderline unethical" | A real moderator; chat prompts the presenter asks out loud; real questions read as asked | `seeded_chat` |
| Typed-in poll results ("98% of you said yes") | Older automated playbooks | A real poll and its real result, or no poll | `fake_poll` |
| A countdown that resets, a timer extended "for anyone who needs it", "this page is coming down" when it is not | Several talks | The Event Launcher's real deadline from `close.md`, kept for everyone, or no deadline on purpose with the end of the follow-up window stated | `fake_timer`, `deadline_real` |
| Threats about the replay ("if you leave now we'll edit that out", "this won't be in the replay") | One talk | A replay with a stated expiry; a real bonus for people who stay, stated plainly | `replay_threat` |
| Hidden low-contrast "embedded commands", double spaces, shaded words | One talk | Nothing hidden; large, high-contrast text (`older-audience.md`) | `hidden_text`, deck contrast |
| Earnings or performance figures without the typical result ("clients make $10,000 in 30 days") | Common | Only classified proof from the proof bank, with the typical result beside any number (classes B, D, H and E always carry it; X is an illustration and never proof); no "make $X" unless the member holds data on what a typical buyer achieves | `earnings_typical`, `proof_classified` |
| Scarcity that is not real ("only 3 spots left", "filling fast") | Common | The cap said as the cap, from `close.md` ("I take 12 people a cohort"); a live count of what is left comes only from the checkout, posted by the moderator when it is true | `fake_scarcity`, `offer_matches_close` |
| Reading buyers' full names aloud | One talk | First names only, with permission, or a simple "people are joining" | `buyer_names` (advisory) |
| Harsh disqualification ("if you're broke, go get a job") | One talk | A respectful "this is not for you if…" list and a free alternative | tone, reviewed by you |
| "It's not your fault" as the opener | Common and overused | Agree with where they are, then change the rules around it (Jason Fladlien's identity shift) | `not_your_fault` (advisory) |

## The rules behind them (United States; members elsewhere follow their own regulator as well)

- **Law: FTC Act Section 5** bans deceptive acts and practices. No FTC rule names "simulated live" webinars, but a false "live" claim, an invented attendee count or seeded chat is a material misrepresentation under Section 5.
- **Law: the Consumer Reviews and Testimonials Rule, 16 CFR 465**, in force since 21 October 2024 with civil penalties per violation: no fake or AI-generated testimonials, none that misrepresent the person's experience; testimonials from the member's own staff, family or managers disclose the connection (a spouse praising the program in the chat counts); and no buying or selling fake social-media indicators (an invented webinar head count is a Section 5 misrepresentation rather than a 465 one).
- **Guidance: the Endorsement Guides, 16 CFR 255** (revised July 2023): a testimonial showing atypical results implies they are typical; a material connection (a discount, a free place, a commission) is disclosed clearly.
- **Guidance: the FTC staff report on dark patterns** (September 2022): countdown timers that reset or vanish, and false scarcity, are deceptive.
- **Notices of Penalty Offenses** (2021) on earnings claims and on endorsements went to hundreds of businesses; for anyone who has received one, a repeat of the practice can carry civil penalties.
- **Law, and a proposal: the Business Opportunity Rule, 16 CFR 437.** The January 2025 proposal to extend it to business coaching and require substantiation of earnings claims is still only proposed as of late 2026; the existing law against unsubstantiated earnings claims already applies. Enforcement through 2024–2026 keeps targeting earnings claims in coaching and "AI income" programs.
- **Vacated: the FTC's "Click to Cancel" rule** (8 July 2025). ROSCA and state auto-renewal laws still apply to anything that renews; the Event Launcher's gate covers it.
- **Recording consent:** some US states require every party's consent to record; announce the recording on the registration page and at the start (`recording_notice`).

Members selling to the UK follow the Digital Markets, Competition and Consumers Act 2024 (fake urgency and fake reviews are banned outright, with fines from April 2025); the EU and Australia enforce the same practices.

This is not legal advice. Members in regulated sectors (finance, health, law, insurance) follow their regulator's marketing rules as well.

## The checks `webinar_check.py` runs

Critical (HOLD until each passes): `placeholders_filled`, `length_fits`, `offer_disclosed`, `objections_named`, `three_beliefs`, `loops_closed`, `offer_matches_close`, `deadline_real`, `proof_classified`, `earnings_typical`, `retired_lines`, `refused_tactics` (the codes above), `recording_notice`, `qa_bank_covers`, `moderator_named`, with `--page`: `page_discloses`, and with `--deck`: `deck_font_min` and `deck_contrast_min`.

Advisory (worth fixing, not a HOLD): `chat_prompts`, `offer_asks`, `deck_font_target`, `deck_contrast_target`, `deck_words`, `buyer_names`, `not_your_fault`, `story_length`, `offer_by_minute`.

The script catches words, not intent. You still read every block for the same things in other words: a paraphrase of a retired line, a "live" impression created without the word, a story that implies a result the proof bank does not hold.
