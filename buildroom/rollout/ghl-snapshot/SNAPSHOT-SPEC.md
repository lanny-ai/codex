# Build Room GoHighLevel snapshot: build spec

_Version 1.0 · 2026-11-19 · for the person building the snapshot in GoHighLevel_

## What this is

GoHighLevel will not let anything outside it create funnel pages, forms, calendars or workflows. It will let the text inside them be changed from outside, through **custom values**.

So the snapshot is built once, by hand, with every piece of text as a custom value. A member loads the snapshot into their account one time. After that, Build Room OS fills in the custom values with the member's own copy, and the pages, emails and workflows fill in by themselves.

`placeholders.json` in this folder is the same list in a form Build Room OS reads. The two must always match. A test fails if they do not.

## Status: not yet proven

Nothing in this spec has been run against a real GoHighLevel account. Before any member touches it, the points under "To verify in a test account" must each be checked. If one fails, the spec changes before the snapshot is built further.

## Rules for the build

1. **Name every custom value exactly as its key.** The name `br_optin_headline` gives the merge tag `{{ custom_values.br_optin_headline }}`. GoHighLevel makes the key from the name, so a friendlier name would produce a different key. After creating the first one, check the key GoHighLevel shows.
2. **Put them all in one folder** named `Build Room OS`.
3. **Leave every value empty** in the snapshot, except `br_snapshot_version`, which is set to `1.0`.
4. **Never type copy into a page or an email.** If text should change per member, it is a custom value. If it should not (a section label such as "What you get"), type it in.
5. **One custom value per element.** Each bullet, each FAQ answer and each testimonial is its own element, so an empty one can be deleted without disturbing the rest.
6. **Optional sections stand alone.** Proof, guarantee, FAQ, urgency, "not for you" and payment terms each sit in their own section, so a member with nothing to put there removes one section and the page still reads well.
7. **Everything is saved as a draft.** Workflows are left in Draft. Pages are not connected to a domain. Nothing can send until the member turns it on.
8. **No SMS anywhere.** Text messages carry consent rules that differ by country. A member adds them later if they choose.

## What to build

### 1. Custom values

The 117 in the tables below, plus `br_snapshot_version`. Typing 117 names is slow. Once a test account and key exist, Build Room OS can create them all in the template account through the API, which also proves the API works.

### 2. One funnel: `BR Client Funnel`

Five steps, in this order.

| Step | Path | Purpose | Custom values used |
|---|---|---|---|
| Opt-in | `/start` | give the free resource in exchange for a name and email | all `br_optin_*`, `br_magnet_name` |
| Thank you | `/thanks` | confirm, say what happens next, offer the next step | all `br_thanks_*` |
| Offer | `/offer` | the full offer page | all `br_offer_*` |
| Book a call | `/book` | calendar to book the call | all `br_book_*`, `br_call_name`, `br_call_length` |
| Booked | `/booked` | confirm the booking and how to prepare | all `br_booked_*` |

Page layouts, top to bottom:

- **Opt-in:** headline, subheadline, hook, the "what you get" bullets, the form with its note above and trust line below, "who this is for", "who this is not for" (optional section), proof (optional section). The button text is `br_optin_button`.
- **Thank you:** headline, the "what happens next" steps, proof (optional section), the next step text with a button to `/offer` or `/book`.
- **Offer:** headline, subheadline, opening, problem, agitation (optional), solution, offer name and promise, how it runs, phases (optional section), deliverables, value and price with terms, guarantee (optional section), proof (optional section), FAQ (optional section), closing headline, button to `/book`, urgency (optional section).
- **Book a call:** headline, subheadline, "what to expect", then the calendar.
- **Booked:** headline, "how to prepare".

Footer on every page: `br_business_name`.

### 3. One form: `BR Opt-in Form`

First name and email only. On submit, go to `/thanks`.

### 4. One calendar: `BR Call`

Booking page is the `/book` step. On booking, go to `/booked`. The member sets their own hours and the real call length; a calendar's length cannot come from a custom value.

### 5. One pipeline: `BR Pipeline`

Stages, in order: `New Lead`, `Call Booked`, `Showed`, `No-Show`, `Offer Made`, `Won`, `Not Now`.

### 6. Tags

`br-new-lead`, `br-magnet-delivered`, `br-nurture-active`, `br-call-booked`, `br-showed`, `br-no-show`, `br-offer-made`, `br-client`, `br-not-now`, `br-stop`.

### 7. One custom field

`BR Source` (text): where the lead came from.

### 8. Fourteen email templates

Each template's subject is its `_subject` custom value and its body is its `_body` custom value followed by `br_signoff`. Where a `_preview` value exists it is the preview text.

| Template name | Keys |
|---|---|
| `BR 01 Delivery` | `br_em_delivery_*` |
| `BR 02 Nurture 1` to `BR 06 Nurture 5` | `br_em_nurture_1_*` to `br_em_nurture_5_*` |
| `BR 07 Booked` | `br_em_booked_*` |
| `BR 08 Reminder day before` | `br_em_remind_day_*` |
| `BR 09 Reminder one hour` | `br_em_remind_hour_*` |
| `BR 10 No-show 1`, `BR 11 No-show 2` | `br_em_noshow_1_*`, `br_em_noshow_2_*` |
| `BR 12 Follow-up 1` to `BR 14 Follow-up 3` | `br_em_followup_1_*` to `br_em_followup_3_*` |

### 9. Six workflows, all left in Draft

| Workflow | Trigger | Steps | Leaves when |
|---|---|---|---|
| `BR WF1 Opt-in and delivery` | `BR Opt-in Form` submitted | add `br-new-lead`; create opportunity in `New Lead`; send `BR 01 Delivery`; add `br-magnet-delivered`; add `br-nurture-active` | done |
| `BR WF2 Nurture` | tag `br-nurture-active` added | wait 1 day, `BR 02`; wait 2 days, `BR 03`; wait 2 days, `BR 04`; wait 3 days, `BR 05`; wait 3 days, `BR 06`; remove `br-nurture-active` | `br-call-booked`, `br-client` or `br-stop` is added |
| `BR WF3 Booked and reminders` | appointment booked on `BR Call` | add `br-call-booked`; move opportunity to `Call Booked`; send `BR 07`; wait until 1 day before, `BR 08`; wait until 1 hour before, `BR 09` | appointment cancelled |
| `BR WF4 No-show` | appointment status is no-show | add `br-no-show`; move to `No-Show`; send `BR 10`; wait 2 days, `BR 11` | a new appointment is booked, or `br-stop` |
| `BR WF5 After the call` | appointment status is showed | add `br-showed`; move to `Showed`; wait 1 day, `BR 12`; wait 3 days, `BR 13`; wait 4 days, `BR 14`; add `br-not-now`; move to `Not Now` | `br-client` or `br-stop` is added |
| `BR WF6 Stop rules` | contact replies to an email, or unsubscribes, or `br-client` is added | add `br-stop`; remove `br-nurture-active` | done |

A workflow step that would send an email whose body is empty must not send. Put an "if the body custom value is empty, skip" condition before each optional email (nurture 4 and 5, the one-hour reminder, no-show 2, follow-up 2 and 3).

## The custom values

"Must have" means Build Room OS will not fill the snapshot until it has that value. "Fact" means the value is only ever the member's confirmed word or something found in their own files. A fact is never drafted. If it is not known it is left empty and reported.

### Brand

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_business_name` | Business name (up to 80 characters) | Business File header | yes | yes |
| `br_owner_name` | Owner's full name (up to 80 characters) | Business File header | yes | yes |
| `br_owner_first_name` | Owner's first name, for email sign-offs (up to 40 characters) | Business File header | yes | yes |
| `br_signoff` | Email sign-off line (up to 120 characters) | §17 communication style, or drafted |  |  |

### Opt-in page

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_optin_headline` | Headline (up to 120 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_subheadline` | Subheadline (up to 200 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_hook` | Opening hook, two or three sentences (up to 500 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_bullet_1` | What you get, bullet 1 (up to 160 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_bullet_2` | What you get, bullet 2 (up to 160 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_bullet_3` | What you get, bullet 3 (up to 160 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_bullet_4` | What you get, bullet 4 (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_bullet_5` | What you get, bullet 5 (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_for_1` | Who this is for, line 1 (up to 160 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_for_2` | Who this is for, line 2 (up to 160 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_for_3` | Who this is for, line 3 (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_notfor_1` | Who this is not for, line 1 (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_notfor_2` | Who this is not for, line 2 (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_form_note` | Line above the form (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_optin_button` | Button text (up to 40 characters) | Lead Capture session (§7) | yes |  |
| `br_optin_proof` | Proof line: a real number or a real testimonial (up to 300 characters) | Lead Capture session (§7) |  | yes |
| `br_optin_trust` | Trust line under the button (up to 160 characters) | Lead Capture session (§7) |  |  |
| `br_magnet_name` | Name of the free resource (up to 100 characters) | Lead Capture session (§7) | yes |  |
| `br_magnet_url` | Link to the free resource | the member | yes | yes |

### Thank-you page

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_thanks_headline` | Confirmation headline (up to 120 characters) | Lead Capture session (§7) | yes |  |
| `br_thanks_next_1` | What happens next, step 1 (up to 200 characters) | Lead Capture session (§7) | yes |  |
| `br_thanks_next_2` | What happens next, step 2 (up to 200 characters) | Lead Capture session (§7) | yes |  |
| `br_thanks_next_3` | What happens next, step 3 (up to 200 characters) | Lead Capture session (§7) |  |  |
| `br_thanks_offer` | The next step offered (up to 300 characters) | Lead Capture session (§7) |  |  |
| `br_thanks_button` | Next step button text (up to 40 characters) | Lead Capture session (§7) |  |  |
| `br_thanks_proof` | One real testimonial or result (up to 300 characters) | Lead Capture session (§7) |  | yes |

### Offer page

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_offer_headline` | Headline (up to 140 characters) | Offer Page Copy session (§5) | yes |  |
| `br_offer_subheadline` | Subheadline (up to 220 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_opening` | Opening section (up to 2000 characters) | Offer Page Copy session (§5) | yes |  |
| `br_offer_problem` | The problem (up to 2500 characters) | Offer Page Copy session (§5) | yes |  |
| `br_offer_agitation` | What it costs to leave it (up to 2500 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_solution` | The way out (up to 2500 characters) | Offer Page Copy session (§5) | yes |  |
| `br_offer_name` | Offer name (up to 100 characters) | Signature Offer (§3) | yes | yes |
| `br_offer_promise` | The promise, one sentence (up to 260 characters) | Signature Offer (§3) | yes |  |
| `br_offer_structure` | How it runs: length and format (up to 200 characters) | Signature Offer (§3) |  | yes |
| `br_offer_phase_1` | Phase and its outcome 1 (up to 240 characters) | Signature Offer (§3) |  |  |
| `br_offer_phase_2` | Phase and its outcome 2 (up to 240 characters) | Signature Offer (§3) |  |  |
| `br_offer_phase_3` | Phase and its outcome 3 (up to 240 characters) | Signature Offer (§3) |  |  |
| `br_offer_phase_4` | Phase and its outcome 4 (up to 240 characters) | Signature Offer (§3) |  |  |
| `br_offer_deliverable_1` | Deliverable 1 (up to 200 characters) | Signature Offer (§3) | yes |  |
| `br_offer_deliverable_2` | Deliverable 2 (up to 200 characters) | Signature Offer (§3) | yes |  |
| `br_offer_deliverable_3` | Deliverable 3 (up to 200 characters) | Signature Offer (§3) |  |  |
| `br_offer_deliverable_4` | Deliverable 4 (up to 200 characters) | Signature Offer (§3) |  |  |
| `br_offer_deliverable_5` | Deliverable 5 (up to 200 characters) | Signature Offer (§3) |  |  |
| `br_offer_deliverable_6` | Deliverable 6 (up to 200 characters) | Signature Offer (§3) |  |  |
| `br_offer_value` | Value of everything included (up to 40 characters) | Signature Offer (§3) |  | yes |
| `br_offer_price` | Investment (up to 60 characters) | Signature Offer (§3) | yes | yes |
| `br_offer_price_terms` | Payment terms, if any (up to 160 characters) | Signature Offer (§3) |  | yes |
| `br_offer_guarantee` | Guarantee, exact wording (up to 800 characters) | Signature Offer (§3) |  | yes |
| `br_offer_proof_1` | Real testimonial or result 1 (up to 600 characters) | Offer Page Copy session (§5), from §3 and the Proof Engine |  | yes |
| `br_offer_proof_2` | Real testimonial or result 2 (up to 600 characters) | Offer Page Copy session (§5), from §3 and the Proof Engine |  | yes |
| `br_offer_proof_3` | Real testimonial or result 3 (up to 600 characters) | Offer Page Copy session (§5), from §3 and the Proof Engine |  | yes |
| `br_offer_faq_q1` | Question 1 (up to 200 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_a1` | Answer 1 (up to 800 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_q2` | Question 2 (up to 200 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_a2` | Answer 2 (up to 800 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_q3` | Question 3 (up to 200 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_a3` | Answer 3 (up to 800 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_q4` | Question 4 (up to 200 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_a4` | Answer 4 (up to 800 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_q5` | Question 5 (up to 200 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_faq_a5` | Answer 5 (up to 800 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_cta_headline` | Closing headline (up to 140 characters) | Offer Page Copy session (§5) |  |  |
| `br_offer_button` | Button text (up to 40 characters) | Offer Page Copy session (§5) | yes |  |
| `br_offer_urgency` | Why now: a real deadline or limit (up to 240 characters) | Signature Offer (§3) |  | yes |

### Booking page

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_book_headline` | Headline (up to 120 characters) | Sales Conversations session (§15) | yes |  |
| `br_book_subheadline` | Subheadline (up to 220 characters) | Sales Conversations session (§15) |  |  |
| `br_book_expect_1` | What to expect on the call 1 (up to 200 characters) | Sales Conversations session (§15) | yes |  |
| `br_book_expect_2` | What to expect on the call 2 (up to 200 characters) | Sales Conversations session (§15) | yes |  |
| `br_book_expect_3` | What to expect on the call 3 (up to 200 characters) | Sales Conversations session (§15) |  |  |
| `br_call_name` | What the call is called (up to 60 characters) | Sales Conversations session (§15) | yes |  |
| `br_call_length` | Length of the call (up to 30 characters) | the member | yes | yes |

### Booked page

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_booked_headline` | Confirmation headline (up to 120 characters) | Sales Conversations session (§15) | yes |  |
| `br_booked_prep_1` | How to prepare 1 (up to 200 characters) | Sales Conversations session (§15) | yes |  |
| `br_booked_prep_2` | How to prepare 2 (up to 200 characters) | Sales Conversations session (§15) |  |  |
| `br_booked_prep_3` | How to prepare 3 (up to 200 characters) | Sales Conversations session (§15) |  |  |

### Email: delivery

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_em_delivery_subject` | Delivery email: subject (up to 120 characters) | Lead Capture session (§7) | yes |  |
| `br_em_delivery_preview` | Delivery email: preview text (up to 140 characters) | Lead Capture session (§7) |  |  |
| `br_em_delivery_body` | Delivery email: body (up to 6000 characters) | Lead Capture session (§7) | yes |  |

### Emails: nurture

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_em_nurture_1_subject` | Nurture email 1: subject (up to 120 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_1_preview` | Nurture email 1: preview text (up to 140 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_1_body` | Nurture email 1: body (up to 6000 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_2_subject` | Nurture email 2: subject (up to 120 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_2_preview` | Nurture email 2: preview text (up to 140 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_2_body` | Nurture email 2: body (up to 6000 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_3_subject` | Nurture email 3: subject (up to 120 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_3_preview` | Nurture email 3: preview text (up to 140 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_3_body` | Nurture email 3: body (up to 6000 characters) | Funnel Map session (§6) | yes |  |
| `br_em_nurture_4_subject` | Nurture email 4: subject (up to 120 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_4_preview` | Nurture email 4: preview text (up to 140 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_4_body` | Nurture email 4: body (up to 6000 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_5_subject` | Nurture email 5: subject (up to 120 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_5_preview` | Nurture email 5: preview text (up to 140 characters) | Funnel Map session (§6) |  |  |
| `br_em_nurture_5_body` | Nurture email 5: body (up to 6000 characters) | Funnel Map session (§6) |  |  |

### Emails: booking

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_em_booked_subject` | Booking confirmation: subject (up to 120 characters) | Sales Conversations session (§15) | yes |  |
| `br_em_booked_body` | Booking confirmation: body (up to 6000 characters) | Sales Conversations session (§15) | yes |  |
| `br_em_remind_day_subject` | Reminder, the day before: subject (up to 120 characters) | Sales Conversations session (§15) | yes |  |
| `br_em_remind_day_body` | Reminder, the day before: body (up to 6000 characters) | Sales Conversations session (§15) | yes |  |
| `br_em_remind_hour_subject` | Reminder, one hour before: subject (up to 120 characters) | Sales Conversations session (§15) |  |  |
| `br_em_remind_hour_body` | Reminder, one hour before: body (up to 6000 characters) | Sales Conversations session (§15) |  |  |

### Emails: no-show

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_em_noshow_1_subject` | No-show email 1: subject (up to 120 characters) | Decision Machine session (§16) | yes |  |
| `br_em_noshow_1_body` | No-show email 1: body (up to 6000 characters) | Decision Machine session (§16) | yes |  |
| `br_em_noshow_2_subject` | No-show email 2: subject (up to 120 characters) | Decision Machine session (§16) |  |  |
| `br_em_noshow_2_body` | No-show email 2: body (up to 6000 characters) | Decision Machine session (§16) |  |  |

### Emails: follow-up

| Custom value (name and key) | What goes in it | Filled from | Must have | Fact |
|---|---|---|---|---|
| `br_em_followup_1_subject` | Follow-up after the call, email 1: subject (up to 120 characters) | Decision Machine session (§16) | yes |  |
| `br_em_followup_1_preview` | Follow-up after the call, email 1: preview text (up to 140 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_1_body` | Follow-up after the call, email 1: body (up to 6000 characters) | Decision Machine session (§16) | yes |  |
| `br_em_followup_2_subject` | Follow-up after the call, email 2: subject (up to 120 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_2_preview` | Follow-up after the call, email 2: preview text (up to 140 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_2_body` | Follow-up after the call, email 2: body (up to 6000 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_3_subject` | Follow-up after the call, email 3: subject (up to 120 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_3_preview` | Follow-up after the call, email 3: preview text (up to 140 characters) | Decision Machine session (§16) |  |  |
| `br_em_followup_3_body` | Follow-up after the call, email 3: body (up to 6000 characters) | Decision Machine session (§16) |  |  |

## What Build Room OS does with it

1. Reads `br_snapshot_version` from the member's account and stops if it is missing or does not match `placeholders.json`.
2. Shows the member a preview: every value, where it will appear, and what will be left empty.
3. Refuses to push if a "must have" value is missing, and says which session provides it.
4. Writes the values. It creates nothing else and publishes nothing.
5. Reports what was filled, what was left empty and which page section to remove for each empty optional value, and what the member has to do by hand: connect a domain, set calendar hours, turn the workflows on, run a test with their own email.

The values file is prepared on the member's computer by the Autopilot skill (`scripts/ghl_values.py`, described in its `references/ghl-values.md`): it checks every value against these rules and writes `custom_values.json`, `custom_values.csv` and a review sheet for the member. That step connects to nothing. Steps 1 and 4 above, reading the version from an account and writing the values into it, are not built yet.

## What is not in the snapshot

- Text messages
- Taking payment (order forms, checkout, invoices)
- A domain, or a connected sending address for email
- Ads, social posts and blog posts
- Anything for the tools Autopilot does not run

## To verify in a test account

Each of these is an assumption until checked. In order:

1. The API can create and update custom values with a private integration key for one sub-account, and which permission that key needs.
2. The merge tag for a value named `br_optin_headline` is exactly `{{ custom_values.br_optin_headline }}`.
3. A custom value works in each place this spec uses one: page headline and paragraph text, button text, a link address, an email subject, an email preview, an email body.
4. How long a custom value can be. The longest here is an email body of up to 6,000 characters.
5. How line breaks and simple formatting (paragraphs, bold, links) in a value appear on a page and in an email. This decides whether email bodies are stored as plain text or as HTML.
6. A snapshot carries its custom values, with their keys unchanged, into the account that loads it.
7. A workflow can test whether a custom value is empty.
8. Loading the snapshot a second time into an account that already has it does not create duplicates with different keys.

If 4 or 5 fails for email bodies, the fallback is already written: the existing `ghl_push.py` pushes whole email templates, and only the pages use custom values.

## Checking the snapshot before it is shared

- Fill every value with obviously fake text (`HEADLINE`, `BULLET 1`) and open each page and each email. Nothing typed by hand should be member-specific, and no merge tag should show as raw text.
- Empty every optional value and confirm each page still reads cleanly once its optional sections are removed.
- Submit the form with your own email with the workflows switched on in the template account: delivery arrives, tags apply, the opportunity appears, nurture starts, a booking stops it.
- Switch every workflow back to Draft, empty every value, set `br_snapshot_version`, then create the snapshot.

## Versions

Any change to a key, or a key added or removed, is a new version: change `br_snapshot_version` in the snapshot and `version` in `placeholders.json` together. A member on an older snapshot is told to load the new one before Build Room OS will fill it.
