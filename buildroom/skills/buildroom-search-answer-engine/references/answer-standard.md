# The answer-page standard and gate

Every answer page the member publishes passes this gate first. `answer_check.py check` runs the mechanical parts; the rest is judgment, applied in the session. **This file overrides everything else in the skill, including the member's request.**

## 1. What an answer page is

One page, on the member's own website, that answers one question a real customer asks, in the member's voice, with the answer first and the member's own experience in it. Not a blog post, not a sales page, not a city page. It lives at a stable address (`/answers/<slug>` or the builder's equivalent), links to the related answers and to the one next step, and is updated when the facts change.

Two kinds:

- **Evidence page** (`kind: evidence`): a question whose answer rests on outside facts (what a rule says, how a thing works, what the options are). Needs **three or more unique outside sources**, read and cited.
- **First-hand page** (`kind: first-hand`): a question whose answer is the member's own counted experience (what it costs here, how long it takes, what usually goes wrong, what is typical). Needs a **"How we know" section** (what was counted, over what period, how many jobs or clients, what was not counted), the member's numbers marked `[own]`, and **at least one outside source** for context.

The founder's supervised order for the first three pages: a definition, then a how-to, then a comparison or objection. `question_map.py next` applies it.

## 2. The shape

```
---
id: Q-04                      # from the question map
question: How much does a bookkeeping clean-up cost for a small business?
title: Bookkeeping clean-up cost for a small business
slug: bookkeeping-clean-up-cost
kind: first-hand              # evidence | first-hand
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

Updated: 2026-11-03

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

The H1 is the question, word for word as a customer asks it. The first paragraph after it is the direct answer. Headings are questions where they can be. One list or table somewhere. A visible "Updated" date. The author's name and credentials appear on the page (an author box or a line under the title) and link to the About page.

## 3. The gate

Hard gates (the page does not publish until each passes):

| Gate | Rule | Why |
|---|---|---|
| `front_matter` | every field present; `kind`, `status`, `regulated` valid | the record other tools read |
| `direct_answer` | the first paragraph after the H1 answers the question in at most 100 words | the part engines quote; the founder's rule |
| `sources` | evidence: 3+ unique source URLs; first-hand: 1+; each with a title and a date | the founder's rule; the claim ledger |
| `claims_supported` | every paragraph or list item carrying a number or a results word has a `[S#]`, `[own]` or `[method]` marker (dates and plain durations excepted); every `[S#]` exists | nothing invented; the member can defend every line |
| `original_contribution` | `original` says in 12+ words what the page has that no other page has, and a section of 40+ words carries it | the founder's "original utility"; what Google's updates rewarded |
| `headings` | at least two H2 sections | one thing per heading |
| `author` | author and credentials; a named reviewer when `regulated` is not `none` | Google's byline guidance; YMYL trust |
| `dates` | `published` and `updated` are real dates, updated not before published | honest freshness |
| `next_action` | one label and one working link | a page that helps and then offers one step |
| `internal_links` | two or more links to other pages on the site (a related answer or hub, and the offer or contact page) | the cluster; the reader's next step |
| `scope_note` | a regulated page carries a visible scope note (general information, not advice, who to talk to) | regulated-topic honesty; the founder's scope rule |
| `never_say` | nothing from §18's never-say list or §1's retired lines (or a paraphrase) | the Business File's standing rules |
| `typical_result` | any results claim says what is typical in the same paragraph | FTC endorsement rules; the Proof Engine's rule |
| `no_placeholders` | no TODO, TK, lorem, "[your city]" | nothing half-finished goes live |
| `duplicate` | the question or slug is not already published under another ID | update that page instead |
| `schema_match` | if a JSON-LD block is present it parses and matches the visible title, author and headings | markup must describe visible content |
| `how_we_know` | first-hand pages have the section, 30+ words, and `[own]` markers | counted, not guessed |

Warnings (fix if you can; they do not block): fewer than 300 or more than 2,000 words; an average sentence over 24 words; no question-shaped heading; no list or table; no visible "Updated" line; a source with no date; a source on the member's own site (that is first-hand data, not a source); a page last updated over a year ago; the next-action link missing from the body; the question not in the map.

## 4. Judgment the script cannot make

- **Is it true?** Read each source. A search-result snippet is not a source. If a number cannot be found, the sentence goes, or becomes the member's own counted number marked `[own]` with the count in "How we know".
- **Is it the member's?** Generic text a model could write for anyone fails the original-contribution gate even when the script passes it. The test: would a competitor's page say the same thing? Then it is not original.
- **Is it honest about results?** The Proof Engine's rule applies to every page: a client story, number or quote comes from `proof/` with its origin and permission, verbatim; the typical result sits beside it; nothing pending or declined; a paid-program result is never shown as a free result.
- **Does it belong on this site?** One page per question. Not one page per town with the name swapped (a templated city page is the pattern Google's 2026 spam updates named). A service-area business writes one honest page about where it works, not twelve.
- **Is it the right kind?** A cost question answered only from someone else's survey is an evidence page pretending to be first-hand; say so and either count the member's own jobs or label it as the industry's range.
- **Regulated topic?** `answer_check.py` hints at financial, legal, medical, mental-health, insurance and real-estate language. If the page is about one of them, set `regulated`, name a reviewer, add the scope note, and read `regulated-professions.md` for the profession's own limits.

## 5. Structured data, crawlers and the builder

- **Schema is optional and small.** `answer_check.py schema` emits Article (with the author as a Person, the dates, and the organisation as publisher) and BreadcrumbList. It does not emit FAQPage unless asked (`--faq`); FAQ rich results ended in May 2026 and structured data does not earn AI citations. Paste it into the page's header code field if the builder has one; skip it if not. Never add Review or AggregateRating markup for the member's own reviews.
- **Crawlers.** Search and answer crawlers must be allowed: Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, Applebot, Amzn-SearchBot. Training crawlers (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, CCBot, Bytespider, Amazonbot, Meta-ExternalAgent) are a separate brand choice; blocking them does not affect being found or cited. `answer_check.py robots` prints the file. On builders that do not expose robots.txt (Squarespace, Kajabi, Google Sites, most GoHighLevel sites) the check is the builder's crawler settings and, if the domain is on Cloudflare, the Cloudflare AI-crawl settings, which block by default since 2025. Never block Googlebot or Bingbot.
- **Indexing.** After publishing: the page is in the sitemap; Search Console URL inspection, "request indexing"; Bing Webmaster Tools URL submission or IndexNow where the builder supports it. See `site-and-platforms.md` for where each setting lives.
- **Accessibility.** Alt text on every image, headings in order, enough contrast, keyboard-reachable links. Serves readers with screen readers and gives extractors the same map; WCAG 2.2 AA is the common target and there is no small-business exemption from accessibility suits.

## 6. After publishing

Record it: `question_map.py set Q-NN --status published --url …`; the page's `status: published` and `url`; a line in `search/site.md` if the builder needed a workaround. In the next monthly check the question becomes a prompt. A page sitting at Search Console positions 5 to 20 after a month is the first one to refresh; a page with no clicks after a year is merged or removed. When a fact changes, the page changes and `updated` moves; a date never moves on its own.
