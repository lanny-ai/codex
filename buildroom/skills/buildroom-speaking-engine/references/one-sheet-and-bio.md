# The one-sheet and the bio

Hosts ask for two things: something to print in the programme (the bio) and one page that tells them who this is and what they'd be booking (the one-sheet). Both are drafted from the Business File and confirmed by the member.

## The bio
Three lengths, all in the third person, because hosts paste them as they are:
- **25 words** for an introduction read aloud.
- **50 words** for a flyer.
- **100 words** for a programme or the one-sheet (120 at most).

Each says what the member does and for whom, how long they have done it, one true thing that earns the room's trust, and one human detail in their own words. Draft from §1 (what they do), §17 (their story and voice) and §18 (proof they may use). Save all three in `speaking/bio.md`. Check each: `pitch_check.py check --file … --kind bio`.

Nothing in a bio is invented or rounded up. "Fourteen years as a bookkeeper" stays fourteen.

**The introduction.** Also write the 25 word version as a script the host can read to introduce the member, in large type. Hosts are grateful, and it stops them improvising.

## The one-sheet
`one_sheet.py template` writes `speaking/one-sheet/one-sheet.json`. Fill it from the confirmed drafts, then `one_sheet.py build`. It checks the content first and writes the page only when nothing is wrong.

| Field | What goes in |
|---|---|
| `name`, `tagline` | The member's name; one line on who they help and with what (fourteen words at most) |
| `bio` | The 100 word bio |
| `photo` | A real, recent photo of the member (a path). Optional. Never a generated or stock face |
| `talks` | One to three, by their number in `speak_pipeline.py talk list` |
| `audiences`, `formats` | Who they speak to; talk, workshop, panel, guest webinar |
| `credentials` | True and recorded ones only |
| `testimonials` | Each with its proof bank ID (`P-01`), the quote word for word, and an attribution. Leave empty when there are none |
| `contact` | An email address or a booking link, at least |
| `based_in`, `travels` | Where they are; how far they will go |

**Testimonials.** Only stories the Proof Engine recorded, with permission that covers a speaker sheet (`events` or `site` in its scope). A pending, unanswered, declined or withdrawn story is refused. An anonymous one is attributed as "a roofing contractor", never by name. With none, the page simply has no testimonial section; that is normal for a first one-sheet. After the first talk, ask the host for a line (`from-stage-to-clients.md`).

**The look.** When the member has a locked look (§22, `Design/System/tokens.css`), the page uses its colours and fonts. Otherwise it is plain and readable. Text is 18 pixels and up.

**To make the PDF:** open `one-sheet.html` in a browser, print, choose Save as PDF, Letter, no headers or footers. Read it once on a phone before sending.

## A video
Local clubs and associations don't ask for a reel. If a host does, a two minute clip of the member speaking to a real room, filmed on a phone, is enough. The **Video Director** can caption and trim it. Don't hold up the first pitches for a video.
