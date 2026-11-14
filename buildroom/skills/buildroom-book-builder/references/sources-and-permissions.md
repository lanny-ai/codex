# The source packet, and permissions

## The source packet
Everything the book may draw on, each item with an ID. A claim in the manuscript is supported only by something in here or in the intake. The manuscript is never its own source.

`book_plan.py source add --title "Podcast interview, March" --kind transcript --ref sources/podcast-march.txt`

| Kind | What it is | Permission |
|---|---|---|
| `own` | the author's own stories, talks, articles, frameworks | not needed |
| `transcript` | a recording of the author teaching or being interviewed | not needed for the author's own words; other people on the recording are third parties |
| `client` | a client's story or result | **must be documented**, or the story is anonymised so the person can't be recognised |
| `public` | a published study, book, article or quotation | cite it; see quoting below |

Put text files in `book/<slug>/sources/` so the checks can read them. For a client story, prefer one already in the Proof Engine's proof bank, with its class and permission.

## Permissions, in plain words (not legal advice; US basics only)
- **Client stories and identifiable people.** Get written permission. Changing a name doesn't protect the author if the person is still recognisable from the details. Being true isn't a defence against a privacy claim.
- **Record it:** `--permission "documented: signed release 2026-10-02"`. The gate blocks a planned client source with no documented permission.
- **Quoting other authors.** There's no safe word count. Short quotations for comment are usually fine; song lyrics and poetry need clearance even for a line; an epigraph is a quotation like any other. Every quotation needs its exact wording and source in the packet.
- **Criticism of a named person or company** can be defamation if it states something false as fact. Stick to what the author can document, or leave the name out.
- **Health, money and legal claims.** State them as the author's experience, not as advice or a promise. "Results may vary" doesn't cure an income claim. These chapters go to a qualified specialist for review; the skill never gives legal or medical clearance.
- **Testimonials.** The FTC's rule on fake reviews and testimonials (16 CFR 465, October 2024) covers AI-written ones. Never write a testimonial or a reader quote.

## The fact, source and permission audit
After the edit, an independent reader runs **P3** (`review-prompts.md`) over a frozen edition with the source packet. For every material factual claim, quotation, credential, number and identifiable third-party story it records the location, the claim, the supporting source and passage, a support status (SUPPORTED, CONTRADICTED, UNVERIFIED) and a permission status (DOCUMENTED, NOT DOCUMENTED, NOT APPLICABLE).

- Anything UNVERIFIED or CONTRADICTED becomes an issue. A materially false claim, or a permission breach, is P0.
- The fix is one of three: the author supplies the source, the claim is rewritten as the author's own view, or it's cut.
- Never fill an evidence gap with a plausible fact.
