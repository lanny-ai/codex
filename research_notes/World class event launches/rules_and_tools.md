# Event Launcher: Rules and Tools (research notes)

Prepared 2026-10-17 for the Build Room OS "Event Launcher" skill (challenge, bootcamp, workshop, webinar run by a small service business, coach or consultant on GHL + Zoom + Stripe + email + SMS).

**Method and confidence note (read first).** WebFetch could not reach any page in this session (DNS failure, and the egress proxy refuses non-developer hosts such as ftc.gov, fcc.gov, federalregister.gov, docs.stripe.com, support.google.com). Every claim below comes from WebSearch result extracts of the cited page, run on 2026-10-17, unless marked otherwise. The only full pages read were two community-maintained GitHub docs on calendar link formats (fetched with curl from raw.githubusercontent.com). Treat figures marked "(verify)" as needing a direct check before they go into member-facing copy. "Accessed" date is 2026-10-17 for every source; publication dates are given where the source showed one.

---

## What matters most (10 lines)

1. **Earnings claims are the biggest risk for coach launches.** The FTC treats "results not typical" disclaimers as no cure; claims must reflect what a typical buyer achieves, with substantiation. The Jan 2025 proposal to extend the Business Opportunity Rule to "business coaching" is still *not final* (S1, S2, S3).
2. **Fake or "should have known" fake testimonials now carry civil penalties** under 16 CFR 465 (in force 21 Oct 2024); FTC sent warning letters Dec 2025 citing up to $53,088 per violation (S5, S6). 2026 penalty amounts were not inflation-adjusted, so 2025 levels apply (S8).
3. **JV partners and affiliates must disclose their commission**; the advertiser is also responsible (Endorsement Guides revised June 2023) (S9, S10).
4. **Federal "click to cancel" is dead for now** (8th Cir. vacated 8 Jul 2025; new ANPRM 13 Mar 2026, comments closed 13 Apr 2026), but ROSCA and state laws like California's ARL (amended, effective 1 Jul 2025) still require clear terms, express consent and easy online cancellation for memberships (S11-S14).
5. **Fake countdown timers and fake "doors close" claims are deceptive** in the US (FTC dark patterns report), UK (DMCC Act Sch. 20 banned practice 7, CMA fines up to 10% of global turnover), EU (sweeps) and Australia (ACCC penalties for resetting timers) (S15-S20). GHL's "recurring" timer that restarts is exactly the pattern regulators cite.
6. **Email: CAN-SPAM** (postal address, working opt-out honored within 10 business days, up to $53,088 per email) plus **Gmail/Yahoo/Microsoft bulk rules** (SPF + DKIM + DMARC aligned, RFC 8058 one-click unsubscribe, spam rate under 0.3%, aim under 0.1%). Gmail began ramping enforcement in Nov 2025; Outlook has sent non-compliant mail to Junk since 5 May 2025 (S21-S27).
7. **SMS: the FCC one-to-one consent rule was vacated (11th Cir., Jan 2025) and removed from the CFR (Aug 2025)**, but prior express written consent for marketing texts, DNC rules for texts, 8 a.m.-9 p.m. local-time limits (stricter in some states), and STOP within 10 business days all still apply. The "revoke-all" rule was revised again in Sept 2026 (S28-S33).
8. **GHL will not send US SMS without approved A2P 10DLC Brand + Campaign**, with a compliant opt-in form (separate, unchecked, optional SMS boxes) and a public privacy policy that includes the "no sharing of mobile data" clause (S34-S36).
9. **Zoom: use Webinars (not Meetings) for 100+ attendees, Q&A, panelists, practice session and registration emails**; on Pro/Business accounts under 100 licenses the recording-consent disclaimer is always on. Record with notice, and get written permission before reusing chat comments as testimonials (S40-S46, S10).
10. **Payment plans in Stripe should be fixed-length subscription schedules (end_behavior: cancel; `iterations` was removed in API 2025-09-30)**, with terms-of-service acceptance in Checkout and a written refund policy that is disclosed before payment and honored (S55-S59, S60).

---

## 1. Rules

### 1.1 FTC: earnings claims (US)

- **Status of rulemaking.** On 13 Jan 2025 the FTC (3-2 vote) proposed (a) amending the Business Opportunity Rule (16 CFR 437) to add "money-making opportunities", defined as any business coaching or investment opportunity requiring payment (MLMs excluded), and (b) a separate Earnings Claim Rule for MLMs. Covered sellers would need to substantiate earnings claims and provide the substantiation on request. Disclosure-document duties would stay limited to current "business opportunities". (S1, S2; NPRM PDF S2b)
- **Not final as of 2026-10-17.** No final rule or withdrawal found. One secondary tracker says the proposal was never published in the Federal Register and that the Unified Agenda lists RIN 3084-AB70 at pre-rule stage (S4, verify on reginfo.gov). Treat it as "proposed, stalled".
- **What applies today (Section 5 FTC Act + existing guidance).** FTC business guidance: a "results not typical" or "results are not guaranteed" line is not enough; earnings claims should reflect what the typical person is likely to achieve, net of expenses; a few outliers do not substantiate a claim (S3). A June 2026 FTC business blog post repeats "back up those earnings claims" (S3b).
- **Existing Business Opportunity Rule** already covers sellers of work-at-home / business opportunities that meet its definition (disclosure document, earnings claim statement). Most coaching offers fall outside the current definition, which is why the 2025 proposal targeted coaching (S2, S2c).
- **Practical line for the skill:** no income or revenue numbers in event copy, slides or testimonials unless the member holds data showing typical results, and the typical result is stated next to any outlier.

### 1.2 FTC: Consumer Reviews and Testimonials Rule (16 CFR 465)

- Final rule announced Aug 2024; effective **21 Oct 2024** (S5, S5b).
- Bans: fake consumer reviews or testimonials (including by people who do not exist or never used the service), buying reviews tied to a sentiment, undisclosed insider reviews, company-controlled "independent" review sites, review suppression, and fake social-media indicators. For buying or spreading fake testimonials, the standard is "knew or should have known" (S5, S5b).
- **Penalties:** civil penalties per violation. The Dec 2025 warning letters to 10 companies cite **up to $53,088 per violation** (S6, S6b). The FTC said on 15 Sep 2026 it would make no 2026 inflation adjustment and keep the 2025 levels (S8).
- FTC Q&A: incentives for reviews are allowed only if not conditioned on sentiment; hosts need not investigate every review, but must act on red flags (S7).

### 1.3 FTC: Endorsement Guides (16 CFR 255): affiliates and JV partners

- Revised guides announced **29 Jun 2023** (published in the Federal Register 26 Jul 2023); defined "clear and conspicuous", said platform disclosure tools may be inadequate, and broadened "endorsement" (S9).
- Any material connection (commission, free product, reciprocal promotion) must be disclosed clearly by the endorser; the advertiser can be liable too. The "results not typical" safe harbor has been gone since 2009; testimonials implying typical results need substantiation or a clear statement of what people generally achieve (S9b, S10).
- FAQ: you can feature customer comments in ads; if the customer had no expectation of a benefit beforehand, no disclosure is needed, but sponsored or incentivised comments need a disclosure. No safe harbor (S10).

### 1.4 Negative option / "click to cancel" (memberships, payment plans, continuity)

- FTC's amended Negative Option Rule ("click to cancel") was **vacated in full by the 8th Circuit on 8 Jul 2025**, days before it took effect, on procedural grounds (missing preliminary regulatory analysis) (S11, S11b).
- FTC restarted with an **ANPRM published 13 Mar 2026** (91 FR 12318, doc 2026-04952, RIN 3084-AB54); **comments closed 13 Apr 2026**; no draft text; no proposed rule found as of today (S12, S12b).
- **Still in force:** ROSCA (online negative options must disclose all material terms before taking billing info, get express informed consent, and give a simple way to stop charges); the 2010-era Negative Option Rule; FTC enforcement policy statement (2021) saying cancellation should be at least as easy as sign-up; FTC v. Amazon Prime case (S13).
- **State law:** California ARL as amended by AB 2863, effective **1 Jul 2025**: express affirmative consent, cancel online in the same medium used to sign up, annual reminder, keep consent records 3 years (S14, law-firm summaries; verify statute).
- **Payment plans:** a fixed-count installment plan is not a negative option in the usual sense, but if it can roll into an ongoing membership, or a trial converts to paid, ROSCA-style disclosure and consent apply. (Inference from S13; not stated in a source.)

### 1.5 Fake scarcity and countdown timers

- **US:** FTC staff report "Bringing Dark Patterns to Light" (14 Sep 2022) lists "baseless countdown timers" (reset or vanish at zero), false low stock and false high demand as deceptive design (S15). Enforcement is under Section 5 / ROSCA.
- **UK:** DMCC Act 2024 Schedule 20 banned practice 7: falsely stating a product is available only for a very limited time; practice 13 covers fake reviews (S16). The CMA's direct enforcement began April 2025; it can fine up to **10% of global turnover** (S17). The CMA update of 14 Oct 2026 lists misleading time-limited offers as a focus area, alongside drip pricing and fake reviews; it has fined over £11.8m across 20 investigations (S17b).
- **EU:** Commission sweep (Jan 2023) found 42 of 399 shops used fake timers; March 2026 sales-events sweep found 18% used pressure selling (scarcity or timers), more than half of them misleading. A Digital Fairness Act proposal targeting dark patterns is planned for Q4 2026 (not yet published) (S18, S19).
- **Australia:** ACCC penalties against James Lane ($19,800) and Vuly ($39,600) for timers that reset or outlasted the real sale end; April 2026 Black Friday sweep found misleading timers. A general unfair-trading-practices ban is before Parliament; if passed, it applies from July 2027 (S20).
- **Rule for the skill:** a deadline must be real. If cart close is Friday 23:59 ET, it closes then for everyone (or per-person evergreen deadlines are real and enforced, see Deadline Funnel). No reopen "by popular demand" unless that is genuinely unplanned, and no timer that restarts on refresh.

### 1.6 Refund policy disclosure

- FTC guidance: use "satisfaction guaranteed" / "money-back guarantee" only if you will refund in full for any reason; disclose any material conditions (for example a 30-day limit) in the ad; failure to honor guarantees has been prosecuted (S21a). TSR also requires disclosure of refund terms if a refund policy is mentioned in a telemarketing pitch (S21a).
- In Stripe Checkout, require acceptance of terms that contain the refund policy (S59).
- UK/EU: consumers buying online services generally have a 14-day cancellation right unless they expressly ask for the service to start in the cancellation period and acknowledge losing it (general knowledge, **not verified in this session**; see Gaps).

### 1.7 Email

**CAN-SPAM (US).** Accurate headers and subject; identify ads; a valid physical postal address; a clear opt-out that works for at least 30 days after sending and is honored within **10 business days**, with no fee or extra data beyond the email address; liability for both the advertiser and the sender; **up to $53,088 per email** (FTC compliance guide, 2025 figure) (S22, S22b).

**Gmail (bulk = 5,000+/day to personal Gmail).** SPF and DKIM, DMARC (at least p=none) aligned with From; TLS; valid PTR; RFC 5322 format; RFC 8058 one-click List-Unsubscribe (marketing mail; honor within 48 hours); user-reported spam rate below 0.3%, recommended below 0.1%. FAQ: enforcement began ramping up in **November 2025**; auth and format failures get temporary or permanent rejections; spam rate above 0.3% removes mitigation eligibility until 7 days below it. One-click missing is not an automatic reject but drives spam reports (S23, S24).

**Yahoo.** SPF + DKIM, DMARC p=none or stricter with alignment, one-click unsubscribe (RFC 8058 POST recommended) plus a visible body link, honor in 2 days, complaint rate under 0.3%; one-click enforcement began June 2024; Yahoo publishes no volume threshold (S25).

**Microsoft Outlook.com (consumer: outlook.com, hotmail.com, live.com).** Senders of 5,000+ messages to Microsoft consumer services from one From domain must pass SPF and DKIM and publish aligned DMARC (p=none minimum). From **5 May 2025** non-compliant mail went to Junk; outright rejection (550 5.7.515) is "date to be announced"; reports of 5.7.515 rejections exist. Does not cover Microsoft 365 business mailboxes (S26, S26b, S27).

**GHL specifics.** Set up a dedicated sending subdomain per sub-account (shared domain = shared reputation); DMARC needed above 5,000/day; From domain must match the sending domain's root; Gmail/Yahoo From addresses will not work; new sub-accounts ramp up over 7 days (then 25,000/day shared, 550,000/day dedicated); warm up a new subdomain over 2-4 weeks (S37).

### 1.8 SMS (US)

- **Consent.** Marketing texts sent with an autodialer need *prior express written consent* (signed, clear, identifies the seller). The FCC's one-to-one consent rule (single seller per consent) was **vacated by the 11th Cir. on 24 Jan 2025** (Insurance Marketing Coalition v. FCC); the mandate issued 30 Apr 2025, and the FCC removed the text from 47 CFR 64.1200(f)(9) (DA 25-621, 14 Jul 2025, published 29 Aug 2025, 90 FR 42137) (S28, S29). Carriers and CTIA still expect consent to be specific to the brand in practice (see GHL rules below).
- **DNC for texts.** The FCC's Dec 2023 order codified that National DNC protections cover marketing texts to wireless numbers (S30).
- **Quiet hours.** Federal: no telephone solicitations before 8 a.m. or after 9 p.m. in the recipient's local time (47 CFR 64.1200(c)(1)) (S31). Some states are stricter: Florida (FTSA) is commonly reported as 8 a.m.-8 p.m., but sources conflict (S31b, verify). Safe default for the skill: send texts only 9 a.m.-8 p.m. in the *contact's* timezone.
- **STOP / revocation.** STOP, QUIT, END, REVOKE, OPT OUT, CANCEL, UNSUBSCRIBE are revocation per se; honor within **10 business days**; one confirmation text allowed (no marketing; presumed fine if sent within 5 minutes) (S32). "Revoke-all" (STOP to one message type stops all): delayed to 31 Jan 2027 (Jan 2026 order), then revised in a Sept 2026 order to let callers apply a revocation to the category it targeted; takes effect 30 days after Federal Register publication, not yet published as of latest source (S33; law-firm summaries, verify).
- **CTIA (carrier) rules.** Standard STOP wording, honor natural-language opt-outs, one final confirmation, HELP reply with program name and contact (S38).

**GHL A2P 10DLC.** Brand (who) and Campaign (what, why, how consent is collected) must both be approved before sending. Opt-in form: separate checkboxes for marketing and non-marketing SMS, unchecked, optional (you may not require SMS consent to submit). Privacy policy and terms must be public and linked in the form footer; the policy must say mobile data is not shared with third parties/affiliates for marketing; no wording about selling leads. Business name, website, policies and checkbox text must match the brand record. Pre-built widget flow can generate compliant policies, but then the widget must be the only SMS opt-in on the site. Canadian 10DLC numbers texting US recipients also need A2P (S34, S35, S36). GHL auto-sets DND on STOP/UNSUBSCRIBE etc. and can append "Reply STOP to unsubscribe"; workflow Time Window settings defer SMS/email outside allowed hours (S39).

### 1.9 Recording, chat comments and privacy

- **Recording consent (US).** Federal law and most states are one-party consent, but several states require all-party consent for confidential communications, including video calls. California Penal Code 632 is the main example (civil damages under 637.2). Commonly cited all-party states: CA, FL, IL, MD, MA, MT, NH, PA, WA (list from search summary, **verify**) (S40). A live webinar with a visible recording notice and consent prompt covers this in practice.
- **Zoom controls.** On Basic, Pro, Business and Free Trial accounts with fewer than 100 licenses, the recording consent disclaimer is on by default and cannot be turned off or reworded (only the voice prompt can be disabled). Guests always see it. Admins can require explicit consent, with camera and mic held off until accepted (S41, S41b).
- **Chat comments as testimonials.** A chat message is personal data and, once used in marketing, an endorsement. Get express permission (a form or reply "yes"), use the exact words, don't imply typical results (S10), and never edit them into a fake (S5). Written release is good practice; no source found that makes it federally mandatory (see Gaps).
- **GDPR / UK GDPR for registrants.** Pick a lawful basis (consent or legitimate interests) and state it in the privacy notice at collection (Art. 13); contract does not cover marketing; consent must be free, specific, informed and unambiguous (no pre-ticked boxes); marketing email is governed separately by ePrivacy/PECR (S47, S48). UK: DUAA 2025 raised PECR fines to £17.5m or 4% of turnover and added a charity soft opt-in; ICO says all stages are in force by 19 Jun 2026 (S49, S50). US hosting: the EU-US Data Privacy Framework survived the General Court (3 Sep 2025); appeal C-703/25 P is pending at the CJEU (S51).
- **Canada (CASL).** Consent (express opt-in; no pre-checked boxes; implied consent only in listed relationships), sender identification, unsubscribe that works for 60 days and is honored within 10 business days; keep consent records (S52).
- **Australia (Spam Act).** Consent, accurate sender ID (legal name or ABN), unsubscribe honored within 5 working days and working for 30 days; ACMA treats sends after 5 days as sending without consent (S53).

---

## 2. Tools (2026 capabilities, limits, pricing)

### 2.1 Zoom

| Product | What it is for | Capacity | Key features | Price (verify live) |
|---|---|---|---|---|
| Meetings (Workplace Pro / Business) | Small interactive workshops, breakouts | Pro 100, Business 300; Large Meeting add-on 500/1,000 (support article also lists 3,000/5,000) | Registration needs a paid plan and a licensed host; auto or manual approval; confirmation email (reminder emails not confirmed for Meetings); polls; Q&A only Business+ | see zoom.us/pricing |
| Webinars | One-to-many launch webinars | 500 to 10,000 standard; up to 100,000 with approval; 1M single-use (US) | Panelists, Q&A, up to 50 polls, practice session, registration with unique join links, reminder and follow-up emails, post-webinar survey | $89/mo monthly or $66.67/mo annual (base tier); Webinars Plus $99; Events $149 (pricing page about 5 months old) |
| Webinars Plus (formerly "Sessions") | Branded single-session or recurring events with ticketing | as purchased; pay-per-attendee option | Event hub, paid ticket types, recurring sessions | as above |
| Events | Multi-day / multi-session conferences, bootcamps | as purchased; PPA overage $2.50 per attendee; PPA cap 50,000 (conflicts with 100,000 elsewhere) | Multi-session, concurrent tracks, exhibitors, custom ticket types | as above |

Sources: S42, S43, S44, S45, S46. Cloud recording on Pro is 10 GB per licensed user, pooled at account level; at the limit, new cloud recording stops (S46b). Converting a webinar to a meeting loses Q&A, webinar emails and surveys (S44).

**Fit for the Event Launcher:** 5-day challenge or bootcamp with breakouts = Meetings (+ Large Meeting add-on if over 300). Sales webinar or masterclass = Webinars. Paid multi-day event with tickets = Webinars Plus or Events.

### 2.2 Alternatives (vendor pages; prices conflict across snapshots, so verify)

- **WebinarJam / EverWebinar:** Starter $49 (100 attendees), Basic $99 (500), Professional $299 (2,000), Enterprise $499 (5,000) per month; annual $39/$79/$229/$379; EverWebinar included from Basic; $1 14-day trial (S61).
- **Demio:** Starter 50 attendees about $45/mo annual; Growth/Premium priced per host, rooms of 150-3,000; up to 10,000 on Premium/Unlimited; pricing page metadata old (S62).
- **Livestorm:** Free (30 attendees, 20 min); Pro priced by attendee credit from $3.00 per attendee (Sept 2026), up to 3,000 live attendees, 4-hour sessions; hosts and no-shows free (S63).
- **StreamYard:** On-Air webinars; Professional $39/mo annual (250 viewers), Premium $79 (1,000), Growth $239 (10,000); 2026 blog shows different prices (S64).
- **Riverside:** Webinar plan $99/mo ($79 annual) is the tier with registration, Q&A, polls, email reminders; up to 10,000 attendees on Business (S65).
- **YouTube Live:** free; mobile streaming needs 50+ subscribers, a verified channel, and up to 24 hours to enable; channels under 1,000 subscribers may have viewer limits on mobile streams (S66). No registration or CRM capture, so pair with a GHL opt-in.
- **Skool:** native calls and live streams in Hobby ($9) and Pro ($99) with "unlimited live calls"; member caps not officially documented (S67).
- **Circle:** live stream attendees 100 / 200 / 500 on Professional $89, Business $199, Scale $419; live room participants 15 / 20 / 50; monthly live-hour caps; 8-hour max session (S68).
- **GHL native webinars:** see 2.3.

### 2.3 GoHighLevel (HighLevel)

- **Plans:** Starter $97/mo (3 sub-accounts), Unlimited $297, Agency Pro $497; telecom and AI are usage-billed on top (S69).
- **Webinars (native):** Live, On-Demand and Recurring webinar types under Sites; registration and broadcast page templates; workflows for confirmations and reminders; built-in video analytics; a native Live Streaming Engine (chat, reactions, recording, external encoder) (S70, S70b). **No native Zoom Webinar registration sync**: a Feb 2026 feature request says you still need Zapier/Make (S70c, user feedback). WebinarKit has a GHL integration.
- **Calendars:** Class Booking calendars (one host, seat limit per slot, up to 9,999); Event calendars (no assigned user, static meeting link only; dynamic Zoom links not supported). Dynamic Zoom links work only on certain calendar types, and GHL's own articles disagree on which (S71). Put the link in the meeting location and use `{{appointment.meeting_location}}` in reminders.
- **Countdown timers:** Marketing > Countdown Timers with Active and Expired links; fixed, recurring (restarts each cycle) and dynamic per-contact timers; email timers are animated images that clients can cache, Apple Mail can freeze them (option to hide), and you can only edit a timer before it has gone out in an email (S72). **Compliance flag:** a recurring timer that restarts on the same offer is the "baseless countdown timer" regulators cite (S15, S18, S20); use fixed or dynamic timers tied to a real deadline only.
- **Payments:** order forms sell one-time and recurring products; set "number of payments" on a recurring product to make an installment plan; invoice payment plans with auto-pay; BNPL (Klarna/Affirm/Afterpay) on order forms only for one-time products via Stripe (S73).
- **Affiliate Manager:** pay-per-lead or pay-per-sale, flat/percent/recurring/multi-tier; tracks Stripe sales but **does not automatically reverse commissions on refunds**; payouts generated on the 1st, NET-7 to NET-90; PayPal auto payouts or manual; W-9/W-8 prompts (S74). Affiliates still need their own FTC disclosure (S9, S10).
- **Communities:** groups, channels, paid groups, community Events with reminders, Go Live / Live Room native sessions (S75).
- **Messaging costs:** US/Canada SMS about $0.00747 per segment plus carrier fees (AT&T $0.0035, T-Mobile $0.0045, Verizon $0.0050 from 1 Oct 2026), multiplied per segment; 10DLC fees passed through (S76).
- **Known quirks:** the "Set Event Start Date" workflow action uses the *account* timezone even when the workflow is set to contact timezone (S77); timers in email cache; Zoom webinar sync needs a third-party connector; affiliate commissions don't reverse on refunds; drip/bulk sends use the account timezone time window (S39, S77).

### 2.4 Add-to-calendar (.ics, Google, Outlook, Apple)

- **RFC 5545 essentials:** each VEVENT needs UID and DTSTAMP (DTSTAMP in UTC). Times are either UTC (`DTSTART:20261105T170000Z`) or local with a timezone reference (`DTSTART;TZID=America/New_York:20261105T120000`); a TZID reference must have a matching VTIMEZONE block with STANDARD/DAYLIGHT sub-components (DTSTART, TZOFFSETFROM, TZOFFSETTO) (S78). METHOD:PUBLISH for a plain download was not confirmed in search (see Gaps).
- **Practical choice:** for a single live session, UTC with `Z` is the most robust (no VTIMEZONE needed; every client converts to local time). Use TZID + VTIMEZONE only for recurring series that must follow DST (daily challenge calls across a DST change). (Inference from S78.)
- **Google link:** `https://calendar.google.com/calendar/render?action=TEMPLATE&text=...&dates=YYYYMMDDTHHmmSSZ/YYYYMMDDTHHmmSSZ&details=...&location=...` Both halves must end in Z for UTC; omit Z and add `ctz=America/New_York` for local time; all-day uses `YYYYMMDD/YYYYMMDD` (end = next day). Prefer `render` (works on Android). Community doc, last checked 2026-08-19 (S79, full page read).
- **Outlook link:** no official docs. `https://outlook.live.com/calendar/deeplink/compose?path=/calendar/action/compose&rru=addevent&startdt=2026-11-05T17:00:00Z&enddt=...&subject=...&body=...&location=...` (consumer) or `outlook.office.com/...` (Microsoft 365). Omitting Z reads the time in the user's timezone. Server accepts about 31,000 characters, but keep under about 2,000 for email clients (S80, full page read; S81 forum reports that the mobile web view may break).
- **Apple Calendar:** no URL scheme; serve a `.ics` file (`Content-Type: text/calendar`).
- **What breaks:** local times without TZID or Z ("floating" times show the same clock time in every zone); TZID with no VTIMEZONE in strict clients; GHL "Set Event Start Date" using account timezone (S77); email timers cached; Outlook mobile web links; long `details` URLs truncated by email clients; reused UIDs make updates overwrite the wrong event; one-day all-day events need end = next day.

### 2.5 Stripe and deadlines

- **Installment plan:** create a Subscription Schedule with phases and `end_behavior: cancel`; Stripe then sets the subscription's `cancel_at` in the last phase. The `iterations` parameter was **removed** (changelog 2025-09-30 "clover"); use `duration` (`interval`, `interval_count`) instead. Test the payment count in test mode (S55, S56). If a payment is disputed, the subscription is released from the schedule and cancelled (S55).
- **Subscriptions with an end date:** `cancel_at` on the Subscription; `cancel_at` also accepts `min_period_end` / `max_period_end` in flexible billing mode (2025-07-30) (S57). Whether Checkout `subscription_data` accepts `cancel_at` was not confirmed (see Gaps).
- **Checkout terms:** `consent_collection[terms_of_service]=required` adds a required checkbox linking to the Terms URL in your public business details; custom wording via `custom_text[terms_of_service_acceptance][message]`; acceptance shows in `consent.terms_of_service` on `checkout.session.completed`. Also works on Payment Links (updatable via API from 2026-07-29) (S59).
- **Refunds:** customer sees the credit in about 5-10 business days (a quick refund may appear as a reversal); Stripe processing fees are not returned (S58). US pricing 2.9% + 30c domestic cards; $15 per dispute received (not returned), plus $15 if you respond manually (S60, verify page date).
- **Honest per-person deadlines:** Deadline Funnel gives each lead a unique deadline synced across email timers and pages, with redirect after expiry; plans from about $39/mo annual (1,000 leads/mo) up to $159; older snapshot $49/$99/$199 monthly (S82). GHL dynamic timers can do per-contact countdowns natively, but cannot be shared across platforms (S72).

---

## 3. Checklist (small-business launch)

Each line: what to do, then (source).

**Claims and proof**
- [ ] No income, revenue or "replace your salary" claims unless you hold data on typical results; state the typical result next to any outlier; never rely on "results not typical". (S3, S10)
- [ ] Every testimonial is from a real customer, in their own words, with permission on file; no testimonials written by staff, AI or "composites". (S5, S7, S10)
- [ ] Don't offer rewards for reviews that depend on them being positive; don't hide negative reviews on your own site. (S5, S7)
- [ ] Affiliates and JV partners put a clear disclosure ("I earn a commission if you buy") in every promo, near the link, not only in a footer. (S9, S10)

**Scarcity, pricing, refunds**
- [ ] Every deadline, bonus expiry and seat limit is real and enforced; no timers that restart on reload; no fake reopen. (S15, S16, S18, S20)
- [ ] Use GHL fixed or dynamic timers only; don't use a recurring timer on the same offer. (S72, S15)
- [ ] Show the total price, payment-plan total and number of payments before checkout; no surprise fees. (S13, S17b)
- [ ] Refund or guarantee terms (window, conditions) are on the sales page and accepted at checkout; honor them promptly. (S21a, S59)
- [ ] If anything renews (membership, continuity, trial-to-paid): disclose terms before billing, get express consent (no pre-ticked box), and offer online cancellation as easy as sign-up; send annual reminders for California customers. (S13, S14)

**Email**
- [ ] Dedicated sending subdomain in GHL with SPF, DKIM and DMARC (at least p=none) aligned to the From domain; warm up 2-4 weeks before a big launch. (S23, S25, S26, S37)
- [ ] One-click unsubscribe header plus visible link; postal address in footer; honor opt-outs in 2 days (Gmail/Yahoo standard; legal max 10 business days). (S22, S23, S25)
- [ ] Watch Postmaster Tools; keep the spam rate under 0.1% and never at 0.3%. (S23, S24)

**SMS**
- [ ] A2P 10DLC Brand and Campaign approved before the launch window (allow weeks for review). (S34, S35)
- [ ] Opt-in form: separate unchecked optional SMS checkboxes naming your business; privacy policy with the no-sharing clause; terms linked. (S34, S36)
- [ ] Texts only 9 a.m.-8 p.m. in the contact's local time (covers the federal 8-9 rule and stricter states); set the GHL workflow Time Window and contact-timezone setting. (S31, S31b, S39)
- [ ] STOP and its synonyms trigger DND immediately; one confirmation text only; scrub against DNC for any non-consented numbers. (S30, S32, S38, S39)

**Live event**
- [ ] Recording announced on the registration page and at the start; Zoom consent disclaimer on; no recording of breakout rooms without telling people. (S40, S41)
- [ ] Before reusing a chat comment or live shout-out as a testimonial, get the person's written OK and keep it in the CRM. (S10, S47)
- [ ] Registration page privacy notice states what you collect, why, lawful basis (EU/UK), and how to unsubscribe; separate consent box for marketing for EU/UK/Canada registrants. (S47, S48, S52)
- [ ] Calendar links: UTC (Z) times for single sessions; test Google, Outlook and .ics on desktop and phone. (S78, S79, S80)

**Money**
- [ ] Payment plans are fixed-length (Stripe schedule `end_behavior: cancel` or GHL "number of payments"); tested in test mode. (S55, S56, S73)
- [ ] Refunds reverse affiliate commissions manually in GHL (not automatic). (S74)

---

## Gaps (not verified in this session)

1. **No page was fully read** except the two GitHub calendar docs; everything else is from search extracts of the cited pages. Re-verify penalty amounts, prices and dates directly before publishing to members.
2. Earnings-claims rule: whether the Jan 2025 NPRM was ever published in the Federal Register and its current Unified Agenda stage (reginfo.gov RIN 3084-AB04 / AB70).
3. FCC Sept 2026 revoke-all revision: exact adoption date (sources say 9 Sep vs 30 Sep 2026) and Federal Register publication/effective date.
4. Florida (and other state) texting quiet hours: statute text not checked (8 p.m. vs 9 p.m. conflict).
5. All-party recording consent state list: from search summary, not a primary source.
6. Whether a written release is legally required to use chat comments in ads (state right-of-publicity laws not researched).
7. UK/EU 14-day cancellation right for online events/coaching (Consumer Contracts Regulations / Consumer Rights Directive) and the "service started" waiver: not researched.
8. Microsoft Outlook: official date for full 550 5.7.515 rejection not found.
9. Zoom: whether Meetings (not Webinars) send reminder emails; live per-capacity prices for 500/1,000 Webinars tiers.
10. GHL: whether order forms support the invoice installment feature; which calendar types support dynamic Zoom links (GHL articles conflict); whether a native Zoom Webinar registration sync shipped after Feb 2026.
11. Stripe: whether Checkout `subscription_data` accepts `cancel_at`; dispute evidence deadlines.
12. RFC 5545 METHOD:PUBLISH and Outlook/Apple behavior with VTIMEZONE: not confirmed via search.
13. Deadline Funnel current dated pricing; Demio pricing page age (about 4 years per metadata).
14. Canada Competition Act (drip pricing / urgency) and Australian unfair-trading bill passage: not checked.

---

## Sources (all accessed 2026-10-17 via WebSearch extract unless noted)

**FTC / US rules**
- S1. FTC press release, "FTC Proposes Rule Changes and New Rule to Deter Deceptive Earnings Claims...", 13 Jan 2025. https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-proposes-rule-changes-new-rule-deter-deceptive-earnings-claims-multilevel-marketers-money-making
- S2. FTC, 16 CFR 437 Business Opportunity Rule NPRM page. https://www.ftc.gov/legal-library/browse/federal-register-notices/16-cfr-437-business-opportunity-rule-notice-proposed-rulemaking-0 ; S2b NPRM PDF https://www.ftc.gov/system/files/ftc_gov/pdf/r511993bizoppnprm01132025.pdf ; S2c FTC "Selling a Work-at-Home or Other Business Opportunity?" https://www.ftc.gov/business-guidance/resources/selling-work-home-or-other-business-opportunity-revised-rule-may-apply-you-1
- S3. FTC, Business Guidance Concerning Multi-Level Marketing. https://www.ftc.gov/business-guidance/resources/business-guidance-concerning-multi-level-marketing ; FTC blog Jan 2025 https://www.ftc.gov/business-guidance/blog/2025/01/concerned-about-deceptive-earnings-claims-sos-ftc-we-want-your-feedback ; S3b FTC blog June 2026 "Back up those earnings claims" https://www.ftc.gov/business-guidance/blog/2026/06/back-those-earnings-claims-other-lessons-ftcs-labor-task-force-work
- S4. MMOL database, rule status (secondary). https://mmoldatabase.com/the-rules.html
- S5. FTC press release, final rule banning fake reviews and testimonials, Aug 2024. https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials ; S5b final rule FRN https://www.ftc.gov/system/files/ftc_gov/pdf/r311003consumerreviewstestimonialsfinalrulefrn.pdf
- S6. FTC press release, warning letters to 10 companies, Dec 2025. https://www.ftc.gov/news-events/news/press-releases/2025/12/ftc-warns-10-companies-about-possible-violations-agencys-new-consumer-review-rule ; S6b letter template https://www.ftc.gov/system/files/ftc_gov/pdf/2025-Fake-Review-Warning-Template.pdf
- S7. FTC, Consumer Reviews and Testimonials Rule Q&A. https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers
- S8. Federal Register, FTC "Civil Penalty Inflation Adjustments" (no 2026 adjustment), 15 Sep 2026. https://www.federalregister.gov/documents/2026/09/15/2026-18853/civil-penalty-inflation-adjustments ; FTC 2025 amounts press release, Feb 2025 https://www.ftc.gov/news-events/news/press-releases/2025/02/ftc-publishes-inflation-adjusted-civil-penalty-amounts-2025
- S9. FTC press release, updated Endorsement Guides, 29 Jun 2023. https://www.ftc.gov/news-events/news/press-releases/2023/06/federal-trade-commission-announces-updated-advertising-guides-combat-deceptive-reviews-endorsements ; S9b 2009 guides announcement https://www.ftc.gov/news-events/news/press-releases/2009/10/ftc-publishes-final-guides-governing-endorsements-testimonials
- S10. FTC, "FTC's Endorsement Guides: What People Are Asking". https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- S11. Fenwick, "Eighth Circuit Vacates FTC's Click-To-Cancel Rule", Jul 2025. https://www.fenwick.com/insights/publications/eighth-circuit-vacates-ftcs-click-to-cancel-rule ; S11b Benesch https://www.beneschlaw.com/publication/eighth-circuit-cancels-ftcs-click-to-cancel-rule/
- S12. Federal Register, "Rule Concerning the Use of Prenotification Negative Option Plans" ANPRM, 13 Mar 2026. https://www.federalregister.gov/documents/2026/03/13/2026-04952/rule-concerning-the-use-of-prenotification-negative-option-plans ; S12b FTC blog Mar 2026 https://www.ftc.gov/business-guidance/blog/2026/03/do-you-have-thoughts-negative-option-related-regulations-share-them-ftc ; Cooley 19 Mar 2026 https://www.cooley.com/news/insight/2026/2026-03-19-ftc-issues-new-advance-notice-of-proposed-rulemaking-on-negative-option-marketing
- S13. ROSCA text https://www.ftc.gov/system/files/documents/statutes/restore-online-shoppers-confidence-act/online-shoppers-enrolled.pdf ; FTC Enforcement Policy Statement on Negative Option Marketing, Oct 2021 https://www.ftc.gov/system/files/documents/public_statements/1598063/negative_option_policy_statement-10-22-2021-tobureau.pdf ; FTC Negative Option Rule page https://www.ftc.gov/legal-library/browse/rules/negative-option-rule
- S14. Barnes & Thornburg, "California Expands Automatic Renewal Law", 2025. https://btlaw.com/en/insights/alerts/2025/california-expands-automatic-renewal-law-new-requirements-now-in-effect ; WSGR https://wsgr.com/en/insights/california-amends-automatic-renewal-law-again.html
- S15. FTC staff report "Bringing Dark Patterns to Light", 14 Sep 2022. https://www.ftc.gov/system/files/ftc_gov/pdf/P214800+Dark+Patterns+Report+9.14.2022+-+FINAL.pdf
- S21a. FTC Businessperson's Guide to Federal Warranty Law https://www.ftc.gov/business-guidance/resources/businesspersons-guide-federal-warranty-law ; Complying with the Telemarketing Sales Rule https://www.ftc.gov/business-guidance/resources/complying-telemarketing-sales-rule ; FTC Policy Statement on Deception (1983) https://www.ftc.gov/system/files/documents/public_statements/410531/831014deceptionstmt.pdf

**UK / EU / Australia / Canada**
- S16. DMCC Act 2024 Schedule 20. https://www.legislation.gov.uk/ukpga/2024/13/schedule/20 ; CMA207 Unfair commercial practices guidance (18 Nov 2025) https://www.gov.uk/government/publications/unfair-commercial-practices-cma207/unfair-commercial-practices ; CMA208 fake reviews guidance https://assets.publishing.service.gov.uk/media/67eeb64fe9c76fa33048c790/CMA208_-_Fake_reviews_guidance.pdf
- S17. CMA news, new consumer regime in force (Apr 2025). https://www.gov.uk/government/news/cma-to-boost-consumer-and-business-confidence-as-new-consumer-protection-regime-comes-into-force ; S17b CMA blog "Direct consumer enforcement: 18 months on", 14 Oct 2026 https://competitionandmarkets.blog.gov.uk/2026/10/14/direct-consumer-enforcement-18-months-on/ ; AA drip pricing fine https://www.gov.uk/government/news/cma-orders-the-aa-and-bsm-driving-schools-to-refund-learner-drivers-over-drip-pricing
- S18. European Commission, Sweeps page. https://commission.europa.eu/topics/consumers/consumer-rights-and-complaints/enforcement-consumer-protection/sweeps_en ; EC news "EU check reveals misleading sales practices online", 26 Mar 2026 https://commission.europa.eu/news-and-media/news/eu-check-reveals-misleading-sales-practices-online-2026-03-26_en
- S19. European Parliament Legislative Train, Digital Fairness Act. https://www.europarl.europa.eu/legislative-train/theme-protecting-our-democracy-upholding-our-values/file-digital-fairness-act
- S20. ACCC, James Lane and Vuly penalties. https://www.accc.gov.au/media-release/james-lane-and-vuly-pay-penalties-for-allegedly-making-misleading-representations-during-last-year%E2%80%99s-black-friday-sales ; ACCC 2026-27 priorities speech https://www.accc.gov.au/about-us/news/speeches/acccs-compliance-and-enforcement-priorities-update-2026-27-address ; ACCC Black Friday investigations https://www.accc.gov.au/media-release/accc-investigating-retailers-making-concerning-black-friday-claims
- S47. EDPB SME guide, "Process personal data lawfully". https://www.edpb.europa.eu/sme/be-compliant/process-personal-data-lawfully_en ; EC legal grounds https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/legal-grounds-processing-data_en
- S48. EDPB consent summary, April 2026. https://www.edpb.europa.eu/system/files/2026-04/edpb-summary-consent_en.pdf ; EDPB Guidelines 05/2020 on consent https://www.edpb.europa.eu/system/files/documents/files/file1/edpb_guidelines_202005_consent_en.pdf
- S49. ICO, DUAA summary: privacy and electronic communications. https://ico.org.uk/about-the-ico/what-we-do/legislation-we-cover/data-use-and-access-act-2025/the-data-use-and-access-act-2025-duaa-summary-of-the-changes/privacy-and-electronic-communications/ ; ICO electronic mail marketing guidance https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/
- S50. ICO statement on DUAA commencement, Feb 2026. https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/02/statement-on-the-commencement-of-the-data-use-and-access-act-duaa/ ; ICO "One year on", Jun 2026 https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/06/one-year-on-marking-the-12-month-commencement-of-the-data-use-and-access-act/
- S51. WilmerHale, "European Court of Justice to Review Challenge to EU-U.S. DPF", 1 Dec 2025. https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework
- S52. CRTC CASL FAQ. https://crtc.gc.ca/eng/com500/faq500.htm ; CRTC implied consent guidance https://crtc.gc.ca/eng/com500/guide.htm
- S53. ACMA "Avoid sending spam". https://www.acma.gov.au/avoid-sending-spam ; ACMA unsubscribe fact sheet (May 2024) https://www.acma.gov.au/sites/default/files/2024-05/Fact%20sheet%20-%20email%20and%20SMS%20unsubscribe%20rules.pdf

**Email**
- S22. FTC, CAN-SPAM Act: A Compliance Guide for Business. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; S22b FTC blog "Candid answers to CAN-SPAM questions" (2015) https://www.ftc.gov/business-guidance/blog/2015/08/candid-answers-can-spam-questions
- S23. Gmail Help, Email sender guidelines. https://support.google.com/mail/answer/81126?hl=en
- S24. Gmail Help, Email sender guidelines FAQ. https://support.google.com/mail/answer/14229414?hl=en
- S25. Yahoo Sender Hub, Best Practices and FAQs. https://senders.yahooinc.com/best-practices/ ; https://senders.yahooinc.com/faqs/
- S26. Microsoft Tech Community, "Strengthening Email Ecosystem: Outlook's New Requirements for High-Volume Senders" (Apr 2025). https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%e2%80%99s-new-requirements-for-high%e2%80%90volume-senders/4399730 ; S26b Microsoft Support "Fix NDR error 550 5.7.515" https://support.microsoft.com/en-us/outlook/fix-ndr-error-550-5-7-515-in-outlook-com
- S27. Mailgun, Microsoft sender requirements (secondary). https://www.mailgun.com/blog/deliverability/microsoft-sender-requirements/

**SMS / FCC**
- S28. Kelley Drye, "Eleventh Circuit Vacates TCPA 1:1 Consent Rule", Jan 2025. https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/eleventh-circuit-vacates-tcpa-11-consent-rule ; MoFo https://mofo.com/resources/insights/250130-eleventh-circuit-vacates-fcc-s-tcpa-one-to-one-consent-rule
- S29. FCC, "FCC Removes One-to-One Consent Rule Nullified by Court Decision". https://www.fcc.gov/document/fcc-removes-one-one-consent-rule-nullified-court-decision ; DA 25-621 https://docs.fcc.gov/public/attachments/DA-25-621A1.pdf ; Federal Register 29 Aug 2025 https://www.federalregister.gov/documents/2025/08/29/2025-16641/delete-delete-delete-targeting-and-eliminating-unlawful-text-messages-rules-and-regulations
- S30. FCC 23-107 Second Report and Order (Dec 2023). https://docs.fcc.gov/public/attachments/FCC-23-107A1.pdf ; FCC fact sheet 22 Nov 2023 https://docs.fcc.gov/public/attachments/DOC-398661A1.pdf
- S31. 47 CFR 64.1200 (Cornell LII). https://www.law.cornell.edu/cfr/text/47/64.1200 ; S31b state calling hours (secondary, conflicting) https://www.kixie.com/sales-blog/telemarketing-laws-by-state-2026/ ; https://www.leadgen-economy.com/blog/telemarketing-calling-hours-by-state/
- S32. FCC 24-24 Report and Order on revocation of consent (Feb 2024). https://docs.fcc.gov/public/attachments/FCC-24-24A1.pdf
- S33. Burr & Forman, revoke-all delayed to 31 Jan 2027. https://www.burr.com/telephone-consumer-protection-act/the-fcc-delays-effective-date-of-tcpa-revoke-all-rule-until-january-31-2027 ; Troutman Pepper Locke, Sept 2026 revision https://www.troutman.com/insights/fcc-revises-tcpa-revocation-of-consent-rules-that-were-set-to-go-into-effect-in-january/ ; Cullen and Dykman https://www.cullenllp.com/blog/fcc-substantially-revises-tcpa-consent-revocation-rules-set-to-take-effect-january-2027/
- S38. CTIA Messaging Principles and Best Practices (May 2023). https://api.ctia.org/wp-content/uploads/2023/05/230523-CTIA-Messaging-Principles-and-Best-Practices-FINAL.pdf ; CTIA Short Code Monitoring Handbook v1.9 https://api.ctia.org/wp-content/uploads/2024/01/CTIA-Short-Code-Monitoring-Handbook-v1.9-FINAL.pdf

**GoHighLevel**
- S34. HighLevel, "How to get your phone number A2P approved in 2026". https://help.gohighlevel.com/support/solutions/articles/155000007237-how-to-get-your-phone-number-a2p-approved-in-2026
- S35. HighLevel, A2P 10DLC Campaign Registration Guide. https://help.gohighlevel.com/support/solutions/articles/155000004539-campaign-registration-step-by-step-guide-and-faqs ; Brand registration https://help.gohighlevel.com/support/solutions/articles/155000008140-registering-your-a2p-brand
- S36. HighLevel, A2P campaign approval best practices. https://help.gohighlevel.com/support/solutions/articles/48001229784-a2p-10dlc-campaign-approval-best-practices ; Canadian 10DLC https://help.gohighlevel.com/support/solutions/articles/155000004915-updated-messaging-policies-for-canadian-10dlc-numbers-a2p-registration-requirements
- S37. HighLevel, Google/Yahoo sender requirements. https://help.gohighlevel.com/support/solutions/articles/155000001634-achieving-compliance-meeting-google-and-yahoo-s-email-sender-requirements-in-2024 ; Email sending guide / warm up https://help.gohighlevel.com/support/solutions/articles/155000001021-email-sending-guide-email-best-practices-email-warm-up ; DMARC https://help.gohighlevel.com/support/solutions/articles/48001224630-email-authentication-dmarc
- S39. HighLevel, SMS compliance settings https://help.gohighlevel.com/support/solutions/articles/155000004684-how-to-configure-sms-compliance-settings ; DND https://help.gohighlevel.com/support/solutions/articles/48001214849-how-to-use-do-not-disturb-dnd- ; Workflow settings (Time Window) https://help.gohighlevel.com/support/solutions/articles/48001239875-workflow-settings-overview ; Drip mode https://help.gohighlevel.com/support/solutions/articles/155000006472-new-drip-mode-architecture-for-bulk-actions
- S69. HighLevel pricing. https://www.gohighlevel.com/pricing
- S70. HighLevel, Complete Guide to Creating Webinars. https://help.gohighlevel.com/support/solutions/articles/155000006062-complete-guide-to-creating-webinars-in-highlevel ; Recurring webinar settings (Jan 2026) https://help.gohighlevel.com/support/solutions/articles/155000006462-recurring-webinar-settings ; S70b Live Streaming and Video Calling https://help.gohighlevel.com/support/solutions/articles/155000006672-live-streaming-and-video-calling ; S70c Ideas board, Zoom webinar integration request https://ideas.gohighlevel.com/scheduling-calendar/p/integrate-with-zoom-webinars-to-register-attendees-without-needing-zapier
- S71. HighLevel, Class Booking calendar https://help.gohighlevel.com/support/solutions/articles/155000003554-how-to-create-a-class-booking-calendar-seats-capacity-availability-explained- ; Event calendars https://help.gohighlevel.com/support/solutions/articles/155000007517-how-to-create-event-calendars ; Zoom integration for calendar bookings https://help.gohighlevel.com/support/solutions/articles/48001179593-zoom-integration-for-users-calendar-bookings
- S72. HighLevel, Countdown Timer: redirection https://help.gohighlevel.com/support/solutions/articles/155000003532-help-guide-redirection-links-in-countdown-timer ; Recurring timer https://help.gohighlevel.com/support/solutions/articles/155000003114-how-to-create-a-recurring-timer- ; Dynamic timer https://help.gohighlevel.com/support/solutions/articles/155000004582-sync-your-countdown-dynamic-timer-for-emails-websites ; Apple Mail https://help.gohighlevel.com/support/solutions/articles/155000005616-hiding-countdown-timers-in-apple-mail
- S73. HighLevel, Selling products on order forms https://help.gohighlevel.com/support/solutions/articles/155000000559-selling-products-on-order-forms-with-available-payment-providers ; Invoice payment plans https://help.gohighlevel.com/support/solutions/articles/155000003164-how-to-add-payment-plans-to-your-invoices- ; BNPL https://help.gohighlevel.com/support/solutions/articles/155000003224-how-to-use-bnpl-in-order-forms-and-payment-links
- S74. HighLevel, Affiliate payouts and commissions https://help.gohighlevel.com/support/solutions/articles/155000003655-how-to-manage-affiliate-payouts-and-commissions ; How the Affiliate Manager works https://help.gohighlevel.com/support/solutions/articles/155000003637-how-does-the-affiliate-manager-work-
- S75. HighLevel, Communities setup https://help.gohighlevel.com/support/solutions/articles/155000000280-how-to-setup-customize-and-manage-your-communities ; Community Events https://help.gohighlevel.com/support/solutions/articles/155000004111-community-events
- S76. HighLevel, LC Phone pricing guide https://help.gohighlevel.com/support/solutions/articles/48001223556-phone-system-pricing-billing-guide ; Carrier fee update 1 Oct 2026 https://ideas.gohighlevel.com/changelog/carrier-fee-pricing-update-effective-october-1-2026
- S77. HighLevel, Set Event Start Date action https://help.gohighlevel.com/support/solutions/articles/48001202723-workflow-action-set-event-start-date ; Wait action https://help.gohighlevel.com/support/solutions/articles/155000002470-workflow-action-wait

**Zoom**
- S40. Reporters Committee, California recording guide https://www.rcfp.org/reporters-recording-guide/california/ ; Justia 50-state survey https://justia.com/50-state-surveys/recording-phone-calls-and-conversations
- S41. Zoom Support, Customizing the recording consent disclaimer https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0068402 ; S41b Modifying recording notification prompts https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0068228
- S42. Zoom, Events and Webinars pricing https://zoom.us/pricing/events ; Zoom Webinars product page https://www.zoom.com/en/products/webinars/
- S43. Zoom Support, Getting started with Zoom Webinars https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0064444 ; Events PPA plan https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0063714
- S44. Zoom Support, Comparing meeting and webinar licenses https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0062404 ; Converting meetings and webinars https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067900 ; Zoom blog Webinar vs Meeting https://www.zoom.com/en/blog/when-to-use-meetings-vs-webinars/
- S45. Zoom Support, Comparing Zoom Events and Webinars Plus event types https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065305 ; Large Meeting license https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065116 ; Zoom Workplace pricing https://zoom.us/pricing
- S46. Zoom Support, Scheduling a meeting with registration https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065026 ; S46b Cloud recording storage capacity https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067670

**Calendar**
- S78. RFC 5545 (IETF). https://datatracker.ietf.org/doc/html/rfc5545 ; icalendar.org Time Zone Component https://icalendar.org/iCalendar-RFC-5545/3-6-5-time-zone-component.html
- S79. InteractionDesignFoundation, add-event-to-calendar-docs, google.md (community; last checked by authors 2026-08-19). Full page read via raw.githubusercontent.com. https://github.com/InteractionDesignFoundation/add-event-to-calendar-docs/blob/master/services/google.md
- S80. Same repo, outlook-web.md (community; last checked 2026-08-19). Full page read. https://github.com/InteractionDesignFoundation/add-event-to-calendar-docs/blob/master/services/outlook-web.md
- S81. Microsoft Tech Community thread on Outlook deeplink compose (May 2023). https://techcommunity.microsoft.com/discussions/outlookgeneral/httpsoutlook-office-comcalendar0deeplinkcompose---fails-to-load-and-redirect/3816442

**Stripe and deadlines**
- S55. Stripe Docs, Subscription schedules. https://docs.stripe.com/billing/subscriptions/subscription-schedules
- S56. Stripe changelog, "Removes iterations parameter for subscription schedules" (2025-09-30 clover). https://docs.stripe.com/changelog/clover/2025-09-30/remove-iterations
- S57. Stripe Docs, Cancel subscriptions https://docs.stripe.com/billing/subscriptions/cancel ; changelog cancel_at enums (2025-07-30) https://docs.stripe.com/changelog/basil/2025-07-30/cancel-at-enums
- S58. Stripe Support, Where is my customer's refund? https://support.stripe.com/questions/where-is-my-customers-refund ; Understanding fees for refunded payments https://support.stripe.com/questions/understanding-fees-for-refunded-payments ; Stripe Docs refunds https://docs.stripe.com/refunds
- S59. Stripe Docs, Customize text and policies (Checkout) https://docs.stripe.com/payments/checkout/customization/policies ; Payment Links changelog 2026-07-29 https://docs.stripe.com/changelog/dahlia/2026-07-29/payment-links-update-endpoint-new-parameters
- S60. Stripe pricing https://stripe.com/pricing ; How disputes work https://docs.stripe.com/disputes/how-disputes-work
- S82. Deadline Funnel pricing https://www.deadlinefunnel.com/pricing ; home https://www.deadlinefunnel.com/

**Webinar alternatives**
- S61. WebinarJam pricing https://webinarjam.com/pricing/
- S62. Demio pricing https://www.demio.com/pricing
- S63. Livestorm, free webinar software / comparisons (Sept 2026) https://livestorm.co/free-webinar-software ; https://livestorm.co/webinar-software-comparison/livestorm-vs-zoom
- S64. StreamYard pricing https://streamyard.com/pricing
- S65. Riverside pricing https://riverside.com/pricing
- S66. YouTube Help, Create a live stream on mobile https://support.google.com/youtube/answer/9228390?hl=en&co=GENIE.Platform%3DAndroid
- S67. Skool pricing https://www.skool.com/pricing
- S68. Circle pricing https://circle.so/pricing ; Circle live limits https://help.circle.so/p/live-and-events/live-management/view-and-increase-the-live-limits-of-your-community-plan
