# The profile as a landing page

Every post, comment and DM sends people to the profile. It has about five seconds to say who the member helps, what changes for them, why the member is credible, and what to do next. LinkedIn says its feed now works out what each post is about and matches it to members' interests [LinkedIn, Mar 2026]; practitioners believe the headline and About are read the same way and set the topics the member is known for [practitioner; LinkedIn has not said so]. Either way it costs nothing to make the headline, About section and pillars say the same thing, and readers need that consistency anyway.

Build each element from the Business File, show it, let the member edit, then move on. One element per message.

## 1. Headline (up to 220 characters; the first ~60 show in comments and on mobile)

Answer three questions [practitioner: Justin Welsh]: who specifically, what specifically, what outcome. Put the words a buyer would search for in the first 60 characters. Never just a job title.

Formulas (pick one, fill from §2 and §3; offer two versions):
1. `I help [specific buyer] [achieve outcome] without [pain or risk] | [proof: years, clients, result]`
2. `[Role the buyer searches for] for [niche] | [named method] | [credibility marker]`
   e.g. "Fractional CFO for $5–20M family businesses | 22 years | 140+ owners advised"
3. `[Outcome] for [buyer] → [mechanism] | Author of [newsletter or book]`
4. `Ex-[recognisable credential] → now helping [buyer] [outcome]` (good for a 45–65 expert whose past role is itself proof)

Where the words come from: §2 sourced language first (or run **Audience Insight**); then type the candidate phrases into LinkedIn's search bar and see what it suggests and who ranks for them.

Check: would the ideal client recognise themselves in the first line? Is every number true and in the file? **Proof-light form** (no proof number the member can stand behind yet): use formula 2 or 4 with years or a credential that is plainly true, never a client count or result that is not in the file.

## 2. Banner (1584 × 396 px, 4:1; design at 2x)

One promise, one proof, one call to action, nothing else [practitioner: Welsh; Alić]:
- **Promise line:** the outcome for the buyer, from §3 or §4, under ten words.
- **Proof element:** "140+ owners advised", a book cover, a rating, years, a client-type list. Only what is true and in the file.
- **CTA:** matches the Featured item or the custom button ("Free diagnostic in Featured ↓").
- **Layout:** the round profile photo covers the bottom-left on desktop and moves on mobile. Keep text on the right half and centred vertically. `render_linkedin.mjs` marks the photo zone and checks nothing important sits in it.
- Brand colours and fonts from §18/§19 if they exist.

## 3. About section (up to 2,600 characters; about two lines show before "see more")

Structure [synthesis of Welsh, offer logic, Edelman 2025: 85% of buyers value "demonstrated understanding of their specific challenges"]:
1. **Lines 1–2, the hook:** the buyer's situation or pain in their words (from §2 sourced language), and the outcome the member produces.
2. **Who I work with, and who I don't.** Specificity signals expertise.
3. **The problem, reframed:** the member's point of view (from §4 villain and differentiator).
4. **How I help:** the named method in 3 to 5 steps (§3), and the formats (1:1, advisory, workshop). Only the offer elements that are settled: a guarantee, a number of places or a price that is still open in §3 or §13 stays out, and nothing on §18's never-say list goes in.
5. **Proof:** 3 to 5 outcome bullets with numbers, client types, years, all consented. A 45–65 expert leans hard here. Proof-light form: what is true today (years in the field, the work itself, the method's first results with permission), and say nothing rather than stretch.
6. **The human paragraph:** two or three lines on why the member does this (§17 Compass if present).
7. **One call to action:** the booking link, the diagnostic or the newsletter. A "DM me the word X" invitation is fine here; it is not comment-gating.

Written through Kern (short, one person to one person). No hashtags. No "passionate", "results-driven", "helping businesses grow".

## 4. Featured (one or two items, not a gallery)

Link only one or two destinations; featuring popular posts keeps people scrolling without ever acting [practitioner: Welsh]. Order:
1. **The conversion asset:** the booking page, a free diagnostic, or the lead magnet page (§7).
2. **A proof asset:** a case-study document or a client-result post (consented).
3. Optional: the newsletter.
Each with a custom thumbnail and a plain-English title. The renderer's `featured` layout (1200 × 627) sets the title alone, large, by default: Featured shows the thumbnail small, so a sub-line is optional and kept to a few words.

## 5. The button and the Services page: a real decision

Facts [LinkedIn Help a1484520, a569554; May 2025 change]:
- Since May 2025 a free profile cannot add a new website link to the top of the profile; existing ones stay until removed.
- The **custom button** ("Book an appointment", "View my services", "Visit my website") needs **Premium Business or Sales Navigator**, and **adding it replaces the Services section**.
- The **Services page** (Open to → Providing services) is free, lists services, and makes the member findable in services search.

Recommend:
- **Inbound comes from search** (people look up "executive coach Denver") → keep the Services page; put the booking link in Featured and Contact info.
- **Inbound comes from content** (people read posts, then visit) → the custom button, if the member already pays for Premium Business. Do not tell anyone to buy Premium only for the button.

Also in this step, a two-minute tidy: the **Services** list (up to ten; pick the ones a buyer would search, in their words), the **top Skills** (the five that match the pillars), and a **custom profile URL** (Edit public profile & URL → the member's name, no numbers).

## 6. Follow or Connect as the main button

Settings & Privacy → Visibility → Followers → "Make follow primary" [LinkedIn Help a528011]. Keep "Who can follow you" on Everyone.
- **Network under about 5,000, goal is conversations:** keep **Connect** primary. First-degree connections can be messaged and sent voice notes without InMail credits. [Build Room inference]
- **Inbound requests are unmanageable, goal is audience:** switch to **Follow** primary.

## 7. Trust signals

- **Verify identity** (free; Persona or CLEAR in the LinkedIn app). LinkedIn says verified members get up to 60% more profile views and up to 50% more post engagement. [LinkedIn's own "up to" figures]
- **A current photo:** face filling most of the frame, plain background, looks like the member on a video call. An old photo is a trust leak on the first call. LinkedIn says having a photo brings up to 21x more profile views. [LinkedIn, old and undated]
- **Experience entries** that carry outcomes, not duties, for the last two roles.
- **Recommendations:** two or three recent ones from clients, about results. Ask by hand.
- **Privacy page link** in Contact info (needed for GDPR first-contact notices; `account-safety.md`).

## Output

`linkedin/profile.md`: the headline (two versions, the member's pick marked), banner spec and the rendered `banner.png`, the About text, the Featured plan, the button/Services decision with the reason, the Follow/Connect choice, the trust-signal checklist. The member pastes each piece into LinkedIn by hand; the skill never edits the profile.
