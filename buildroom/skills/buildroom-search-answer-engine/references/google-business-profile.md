# The Google Business Profile

For any business that meets customers in person, the profile is the first thing Google's AI cites for a local question and the first thing a buyer sees. `profile_tracker.py` keeps `search/profile.json`, scores it (`check`), prints the week's 30-minute list (`weekly`) and tracks reviews and listings. This file is the judgment behind the score.

## 1. Eligibility comes first

A profile is for a business that makes **in-person contact** with customers: at its own premises (a storefront, an office with signage and hours), or at the customer's (a service-area business: a plumber, a mobile clinician, an adviser who visits, a coach who meets clients in person; the address is hidden and the service area shown, up to 20 areas), or both (a hybrid: the address shown and a service area listed; set both).

Not eligible: an online-only business; a virtual office, PO box or mailbox store; a coworking desk without signage, staff and customer reception during hours; a coach or consultant who only ever meets clients on video. Such profiles get suspended, and reinstatement is slow and uncertain. Ask the question first. A remote business runs this skill without a profile: `profile_tracker.py init --type none`, then listings and answer pages carry the load, and the LinkedIn Engine does the rest.

## 2. What moves rank (do these first)

| Item | What good looks like | Why |
|---|---|---|
| Primary category | the one category that matches the service that makes the money | the strongest ranking factor the owner controls (2026 survey) |
| Business name | the real-world name, exactly as on signage, invoices and the website (`--legal-name`); nothing added | added words are a policy breach and a leading suspension cause, even though they correlate with rank |
| Secondary categories | up to nine, for the services actually sold (none is fine for a one-service business) | relevance for the other searches |
| Hours | set, with holiday hours kept current | "open now" is a filter and a ranking input |
| Address or service area | a real address, or (service-area) hidden with a true service area | wrong or fake addresses get profiles removed |
| Reviews | rating, count and recency; see section 4 | about a fifth of local-pack weight; the buyer's filter |
| Verification | owner-verified (video is reported as the usual route now); then `set eligible=yes` so the tracker stops holding | nothing shows until it is |

## 3. What moves the buyer (do these every week, and say what they are for)

Photos and posts do not move rank in controlled tests. They decide whether a person who sees the profile calls.

- **Description**, 250 to 750 characters: what the business does, for whom, where, since when. No links, prices, promotions, "best" or "#1".
- **Services**, three or more, each with two sentences on who it is for. Gemini's Ask Maps answers from these fields; this is the replacement for the old Q&A.
- **Phone, website, booking link** (the same booking link the Decision Machine uses). Google added WhatsApp as a contact option per some 2026 reports; messaging and call history ended in 2024.
- **Photos**: ten or more real photos (the owner, the team, the work, the place, the van); no stock; one new real photo every two weeks or so.
- **Posts**: one a week or two, a job done, a question answered this week, a date. Google suggests one a week. Under 20 people will see each; the ones who do are deciding.
- **Attributes** that are true (women-owned, veteran-owned, wheelchair access, appointment required).
- **Opening date**, social links (Google auto-adds some since 2025; check they are right).

Removed, do not look for: Q&A (gone since December 2025), messaging, call history. Not worth time: keyword-stuffing the description, the name, or the services.

## 4. Reviews

The rules, in order of who enforces them:

1. **Google's policy** (stricter than the law): no incentive of any kind for a review, positive or negative; no review gating (asking only the happy ones, routing the unhappy to a private form); no reviews from owners, staff or swapped between businesses; no kiosks or on-site pressure; no staff quotas and no asking customers to name an employee (2026 additions, vendor-reported). Breach means hidden reviews, a block on new reviews, a public warning banner on the profile, or suspension.
2. **The FTC Consumer Reviews and Testimonials Rule** (16 CFR 465, in force since October 2024, enforced since late 2025, about $53,000 per violation): no fake or AI-written reviews, no incentives conditioned on a good review, no undisclosed insider reviews, no suppression (threats, or showing only the good ones while claiming to show all).
3. **The member's profession** (`regulated-professions.md`): therapists and counsellors may not ask clients for reviews at all; HIPAA-covered providers never confirm a reviewer is a patient; financial advisers need compliance sign-off before showing reviews on the site; lawyers and insurance agents have their own wording limits.

The ask, in practice (`reviews-and-listings.md` has the words): **every client, the same words, the same day the work finishes, whatever they thought of it** (vendors see the best response inside a few hours); the direct review link or a QR card that opens the standard form (never a page that pre-selects stars or pre-fills words); one reminder three to five days later. If that is more clients than the owner can message by hand, the CRM sends the same words to every completed job with consent on file; the one thing never done is choosing whom to ask. Google pauses new reviews on a profile during a spike its own asks do not explain, so the tracker flags reviews arriving faster than the logged asks, never a busy week of real asks. By text only with written consent collected at booking, in business hours, with STOP honoured; by email with an address and an opt-out. A profession whose code bars asking clients (therapists, counsellors): `set review_ask=no`, and the tracker drops every ask item.

Replies: every review, within seven days, in the owner's own words, naming the service, never arguing, never a template (half of buyers are put off by one). A fake or policy-breaking review: flag it in the profile's review tool, wait three days, file the one appeal with evidence, then the Business Profile community forum; never reply with a threat.

Benchmarks are category-specific and the studies disagree (medians of about 20 to 350 reviews at 4.8 to 4.9 stars for the top three in one 50-million-result study; 47 at 4.47 in an older mixed sample). Use the member's own town: find the lowest-review business consistently in the top three for the category, and that count is the first target. The buyer's thresholds are clearer: 4.5 stars, 20 reviews, one in the last three months, every review answered.

## 5. The weekly 30 minutes (`profile_tracker.py weekly`)

1. Reply to any open review (five minutes each).
2. Ask every client whose job finished this week, the same words (ten minutes; the CRM when there are more). Log the asks: `log review-ask --n 3`.
3. One real photo (three minutes). One post (five minutes). Log them.
4. Check hours, phone, booking link and any Google-suggested edits (three minutes); log `update` once a month.
5. Quarterly: categories, services, service area, attributes, listings (`listings check`).

## 6. Suspension

Common causes in 2026: a service-area business showing its home address; the profile address not matching the website; added words in the name; a PO box or virtual office; a category that does not match; duplicates; many rapid edits; fake engagement. If it happens: fix the cause first (restore the real name, hide the address, correct the area), then one appeal with a business licence or utility bill, signage and vehicle photos and a matching website; never create a second profile. Expect days to weeks.

## 7. What the profile cannot do

It cannot answer a question the buyer asks before they know whom to call; the answer pages do that. It cannot be cited by ChatGPT, which does not read it (Yelp and Bing Places do that job there). And it cannot make a business with no reviews look chosen; the review loop does that, one honest ask at a time.
