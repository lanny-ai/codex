# The answer-page standard and gate

Every answer page the member publishes passes this gate first. `answer_check.py check` runs the mechanical parts; the rest is judgment, applied in the session. **This file overrides everything else in the skill, including the member's request.**

## 1. What an answer page is

One page, on the member's own website, that answers one question a real customer asks, in the member's voice, with the answer first and the member's own experience in it. Not a blog post, not a sales page, not a city page. It lives at a stable address (`/answers/<slug>` or the builder's equivalent), links to the related answers and to the one next step, and is updated when the facts change.

Three kinds:

- **Service page** (`kind: service`): one page per service, the best-supported page type for local search and AI answers. The H1 is the service name; the H2s answer what it is, who it is for, what it costs (a real price or range, or how pricing works, with `[own]`), what happens first; an "Our rule" section carries the member's own view. Outside sources optional. The first page written when none exists.
- **Evidence page** (`kind: evidence`): a question whose answer rests on outside facts (what a rule says, how a thing works, what the options are). Needs **three or more unique outside sources**, read and cited.
- **First-hand page** (`kind: first-hand`): a question whose answer is the member's own counted experience (what it costs here, how long it takes, what usually goes wrong, what is typical). Needs a **"How we know" section** (what was counted, over what period, how many jobs or clients, what was not counted), the member's numbers marked `[own]`, and **at least one outside source** for context.

The first three pages are made by hand with the member before any routine, as the founder's rollout does; `question_map.py next` puts the service page first when none is published and then the highest score, so the member's highest-intent question (cost, how to choose, versus, is it worth it) comes before a definition.

## 2. The shape

```
---
id: Q-04                      # from the question map
question: How much does a bookkeeping clean-up cost for a small business?
title: Bookkeeping clean-up cost for a small business
slug: bookkeeping-clean-up-cost
kind: first-hand              # evidence | first-hand | service (a trailing # comment is ignored)
status: draft                 # draft | ready | published | needs-update
author: Dana Ruiz
author_credentials: CPA, 14 years, about 120 small-business clients
reviewer: none                # a named reviewer is required when regulated is not none
published: 2026-11-03
updated: 2026-11-03
cluster: pricing
original: Our own 2025 clean-up jobs, counted: the three things that decide the price and the one that doubles it.
regulated: none               # none | financial | legal | medical | mental-health | insurance | real-estate
next_action: Book a 20-minute call | /contact
sources:
  - S1 | Title | Publisher | https://… | published 2026-02-10 | accessed 2026-11-01
---
# How much does a bookkeeping clean-up cost for a small business?

**Short answer:** two or three plain sentences, under 100 words: the number or the decision first, then the one condition that changes it.

By Dana Ruiz, CPA, 14 years. Updated: 2026-11-03

## What decides the price?
(one thing per heading; a paragraph or list item with a number or a result carries [S1], [own] or [method])

## How long does it take?
- a short list or a small table

## How we know
(first-hand pages: what was counted, over what period, how many, what was left out)

## What we'd check first
(at least 40 words of the member's own rule, mistake seen most, or example; the part no other page has)

## Sources
- [S1] Title, Publisher, 2026. https://…

*Next step:* [Book a 20-minute call](/contact)
```

The H1 is the question, word for word as a customer asks it (a service page: the service name). The first real paragraph after it is the direct answer; a byline or a date line is skipped. Headings are questions where they can be. One list or table somewhere. A visible "Updated" date. The author's name and credentials appear on the page (a line under the short answer, as above, or an author box) and link to the About page.

## 3. The gate

Hard gates (the page does not publish until each passes):

| Gate | Rule | Why |
|---|---|---|
| `front_matter` | every field present; `kind`, `status`, `regulated` valid; a trailing `# comment` is ignored | the record other tools read |
| `h1` | the H1 is the question word for word (a service page: the service name) | what the engines match against |
| `direct_answer` | the first real paragraph after the H1 (a byline or date line is skipped) answers the question in at most 100 words | the part engines quote; the founder's rule |
| `sources` | evidence: 3+ unique source URLs; first-hand: 1+; service: optional; each with a title and a date; the scaffold's example source does not count | the founder's rule; the claim ledger |
| `claims_supported` | every paragraph or list item carrying a number has a `[S#]`, `[own]` or `[method]` marker; years, plain durations ("20-minute"), step numbers, phone numbers and link targets are set aside first, so a dollar figure next to a year still needs its marker; every `[S#]` exists | nothing invented; the member can defend every line |
| `original_contribution` | `original` says in 12+ words of the member's own what the page has that no other page has, and a section of 40+ words carries the member's view or rule ("How we know" does not count) | the founder's "original utility"; what Google's updates rewarded |
| `headings` | at least two H2 sections | one thing per heading |
| `author` | author and credentials; a named person as reviewer when `regulated` is not `none` (a blank reviewer on an unregulated page means none) | Google's byline guidance; YMYL trust |
| `dates` | `published` and `updated` are real dates, updated not before published | honest freshness |
| `next_action` | one label and one working link (a page, `mailto:`, `tel:` or `sms:`) | a page that helps and then offers one step |
| `internal_links` | two or more links to other pages on the site (a related answer or hub, and the offer or contact page) | the cluster; the reader's next step |
| `scope_note` | a regulated page carries a visible scope note (general information, not advice, who to talk to) | regulated-topic honesty; the founder's scope rule |
| `never_say` | nothing from §18's never-say list or §1's retired lines, read from the Business File in the template's own shape (the label line and any sub-bullets); the script matches exact phrases, a paraphrase is the session's judgment | the Business File's standing rules |
| `typical_result` | any results claim (an outcome such as saved, cut, grew, booked, with a number or a client noun), whatever its marker, says what is typical in the same paragraph; a plain count ("38 clients in 2025") is not a claim | FTC endorsement rules; the Proof Engine's rule |
| `no_placeholders` | no TODO, TK, lorem, `[your city]`, and none of the scaffold's `‹…›` text | nothing half-finished goes live |
| `duplicate` | the question or slug is not already published under another ID | update that page instead |
| `schema_match` | if a JSON-LD block is present it parses and matches the visible title and author; a FAQPage block fails (retired) | markup must describe visible content |
| `how_we_know` | first-hand pages have the section, 30+ words, and `[own]` markers; a service page gets a warning when it skips who, cost or what happens first | counted, not guessed |

Warnings (fix if you can; they do not block): fewer than 300 or more than 2,000 words; an average sentence over 24 words; no question-shaped heading; no list or table; no visible "Updated" line; a source with no date; a source on the member's own site (that is first-hand data, not a source); a page last updated over a year ago; the next-action link missing from the body; the question not in the map.

## 4. Judgment the script cannot make

- **Is it true?** Read each source. A search-result snippet is not a source. If a number cannot be found, the sentence goes, or becomes the member's own counted number marked `[own]` with the count in "How we know".
- **Is it the member's?** Generic text a model could write for anyone fails the original-contribution gate even when the script passes it. The test: would a competitor's page say the same thing? Then it is not original.
- **Is it honest about results?** The Proof Engine's rule applies to every page: a client story, number or quote comes from `proof/` with its origin and permission, verbatim, copied in by ID (the Proof Engine's placement table has a row for answer pages); the typical result sits beside it; nothing pending or declined; a paid-program result is never shown as a free result.
- **Does it paraphrase a retired line?** The script matches exact phrases; "we'll beat any quote" for a retired "we beat any quote" is the session's catch.
- **Does it belong on this site?** One page per question. Not one page per town with the name swapped (a templated city page is the pattern Google's 2026 spam updates named). A service-area business writes one honest page about where it works, not twelve.
- **Is it the right kind?** A cost question answered only from someone else's survey is an evidence page pretending to be first-hand; say so and either count the member's own jobs or label it as the industry's range.
- **Regulated topic?** `answer_check.py` hints at financial, legal, medical, mental-health, insurance and real-estate language. If the page is about one of them, set `regulated`, name a reviewer, add the scope note, and read `regulated-professions.md` for the profession's own limits.

## 5. Structured data, crawlers and the builder

- **Schema is optional and small.** `answer_check.py schema --site … --path <the page's real path> --out search/answers/<slug>.jsonld` emits Article (with the author as a Person, the dates, and the organisation as publisher) and BreadcrumbList, nothing else: FAQ rich results ended in May 2026, structured data does not earn AI citations, and a FAQPage block fails the gate. Paste it into the page's header code field if the builder has one; skip it if not. Never add Review or AggregateRating markup for the member's own reviews.
- **Crawlers.** Search and answer crawlers must be allowed: Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, Applebot, Amzn-SearchBot, Meta-WebIndexer. **Google-Extended** governs Gemini training and grounding: blocking it can stop the Gemini app using the site, so it stays allowed. Training crawlers (GPTBot, ClaudeBot, Applebot-Extended, Bytespider, Amazonbot, Meta-ExternalAgent) are a separate brand choice; the default is to allow them, because a business that wants to be known loses nothing, and blocking them does not affect being found or cited. The likeliest way a member blocks the answer engines is a builder's **"block AI bots" switch** (Squarespace, Kajabi, Wix and others have one): it is often on by default and it blocks OAI-SearchBot, PerplexityBot and ChatGPT-User along with the training bots. Turn it off, then open `yourdomain.com/robots.txt`, save it, and run `answer_check.py robots --check robots.txt`, which names any answer crawler still blocked. If the domain is on Cloudflare, its AI-crawl settings block by default since 2025; check them too. `answer_check.py robots --out search/robots.txt` writes the file for builders that take one. ChatGPT-User and Perplexity-User fetch pages for a person on request and may not honour robots.txt; that is expected. Never block Googlebot or Bingbot.
- **Indexing.** After publishing: the page is in the sitemap; Search Console URL inspection, "request indexing"; Bing Webmaster Tools URL submission or IndexNow where the builder supports it. See `site-and-platforms.md` for where each setting lives.
- **Accessibility.** Alt text on every image, headings in order, enough contrast, keyboard-reachable links. Serves readers with screen readers and gives extractors the same map; WCAG 2.2 AA is the common target and there is no small-business exemption from accessibility suits.

## 6. After publishing

Record it: `question_map.py set Q-NN --status published --url …`; the page's `status: published` and `url`; a line in `search/site.md` if the builder needed a workaround. In the next monthly check the question becomes a prompt. A page sitting at Search Console positions 5 to 20 after a month is the first one to refresh; a page with no clicks after a year is merged or removed. When a fact changes, the page changes and `updated` moves; a date never moves on its own.
