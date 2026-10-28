# The review loop and the free listings

## 1. The review ask (the member sends it; the skill drafts it)

Every ask goes through the Kern framework (`kern-framework.md`): short, conversational, one request. Same words for every client. The skill drafts in the member's voice; the member sends by hand, or from their CRM with consent on file.

**Text (consent on file, business hours, STOP honoured):**

> Hi [first name], it's [member] from [business]. Thanks for having us out today. If you have a minute, a short Google review helps other [town] [households / owners] find us: [direct link]. Either way, thank you. Reply STOP to opt out.

**Email (physical address and an unsubscribe line at the foot):**

> Subject: Thank you, [first name]
>
> [First name], thank you for [the job, in five words]. If you have two minutes, would you leave us a Google review? It is the main way people in [town] decide who to call: [direct link]. Say whatever is true. Thank you again.
>
> [member], [business] · [address] · [unsubscribe]

**In person:** "If you were happy with today, a Google review is the biggest favour you could do us. Here's the card." The card carries the QR code to the standard review form, nothing pre-filled.

**Reminder, three to five days later, once:** "Hi [first name], just in case it slipped: [link]. No pressure at all."

Never: any gift, discount, draw entry or thank-you tied to the review; asking only the clients expected to be happy; a form that sorts happy from unhappy before the link; writing or suggesting words; asking staff, family or friends without a disclosure; more than one reminder; a burst of asks in one week. For a therapist or counsellor: no ask at all (`regulated-professions.md`).

## 2. The reply

Every review, within seven days, written for that review. Name the service, thank them, say one true thing about the job, sign with a first name. A one-star review gets the calmest reply on the profile: thank them, say what the process is to put it right, and take it offline ("call me on … and I'll sort it personally"). Never argue, never post details about the client or the job.

HIPAA-covered providers: never confirm the reviewer is a patient and never mention care, dates, insurance or cost, even if the reviewer did. The safe reply: "Thank you for taking the time to share this. We take every comment seriously; please contact our office at … so we can talk." Every reply the same shape, which is the one case where a near-template is the right answer.

## 3. Consented quotes go to the Proof Engine

A public review may be linked to from anywhere. Quoting it on the website, in an email, an ad or a post needs the reviewer's consent for that use; the Proof Engine runs that ask and files the words in `proof/` with origin, permission and scope. This skill records the count and rating in §18's proof-vault line and never copies review text onto a page itself.

## 4. The free listings (`profile_tracker.py listings`)

In order; stop after these unless the member's industry has an obvious directory of its own.

| Listing | Why | Note |
|---|---|---|
| Google Business Profile | Google's AI and the local pack | section above |
| Bing Places | feeds Bing Maps and Copilot; free; imports from Google | whether it feeds ChatGPT is disputed |
| Apple Business | feeds Apple Maps, Siri and Spotlight; free; launched April 2026 in place of Apple Business Connect | existing Connect listings were migrated |
| Yelp | licensed to OpenAI in July 2026; appears in ChatGPT's local answers, Apple Maps, Alexa and Bing | complete the page; never buy ads to "unlock" reviews; Yelp's own review rules forbid asking for reviews, so the ask stays on Google |
| Facebook page | the one other platform a majority of buyers over 65 use | hours, phone, website, the same name |
| Nextdoor, Better Business Bureau, the chamber of commerce | mentions the engines read; ChatGPT cited BBB in 39% of home-services answers in one test | free tiers; BBB accreditation is paid and not needed for the listing |
| One or two industry directories | Angi or Expertise for trades; Healthgrades-type for clinics; the state bar or professional body for advisers; the ICF or an association for coaches | the licensing-body page is the one ChatGPT trusts for trades |

Name, address and phone identical everywhere, down to "Suite" versus "#" (the tracker normalises the common variants and flags the rest). Check each listing once a quarter. Paid data-aggregator submissions are not supported by any 2026 evidence; do not pay.

## 5. Mentions: one a month

The 2026 ranking-factor survey puts being in other people's lists and mentions above anything the member can write themselves, for AI visibility. One email a month, in the member's words: to the local paper's or the chamber's "best of" roundup, an association newsletter, a podcast that interviews people like the member, a supplier's partner page, a neighbouring business's "we recommend" list. Ask to be listed or interviewed; offer one useful thing (a short answer, a number, a photo). Log it in `search/mentions.md` with the date and the result. The Borrowed Audience work, when it exists, grows from this line.
