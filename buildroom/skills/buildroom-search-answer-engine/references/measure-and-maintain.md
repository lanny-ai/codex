# Measure and maintain

## 1. What counts

Results that reach the bank, in this order: calls and direction requests from the profile (the profile's performance page); booked calls and form fills whose "how did you find us" answer was Google, Maps, a review, an AI answer or a video; Search Console clicks on the answer pages, and the generative-AI impressions line; Bing's AI citations; the monthly share of customer prompts where the business is named. Traffic and rankings are not results, and the skill never reports them as if they were.

Expectations, stated to the member before the first page: AI answers cut clicks on the queries they appear on (38 to 40% in a randomised experiment, more in vendor data), and a business cited inside the answer gets the clicks that remain; AI referrals are 1 to 4% of visits and convert well; a new page can be cited in ChatGPT or Perplexity within one to two weeks once Bing has it; the profile's calls and direction requests are usually the first thing to move, within a month or two, though nobody has measured this properly; and classic rankings take months with no reliable timeline.

## 2. The two free reports (monthly, ten minutes)

- **Search Console**: Performance, last 28 days vs the previous 28: clicks and impressions for the answer pages; the generative-AI report's impressions; queries at positions 5 to 20 with impressions and few clicks (the refresh list and the next questions). Pages: any "discovered, currently not indexed" answer page gets a request-indexing and an internal link.
- **Bing Webmaster Tools**: AI Performance: citations, cited pages, the grounding queries behind them (the questions Copilot actually sends), citation share against the sites it names.

GA4, if the member has it: the AI Assistant channel, and referrers chatgpt.com, perplexity.ai, copilot.microsoft.com, gemini.google.com. Most AI-sourced visits arrive with no referrer and land in Direct, so a rise in Direct alongside the other signals is part of the picture.

## 3. The monthly citation check (`citation_check.py`, about an hour, two with a second run)

Sized for an owner, not an agency: ten prompts, three engines, the member types what they saw into a checklist.

1. `citation_check.py plan --business … --category … [--city …] [--audience …]` builds ten prompts: category prompts ("who is a good [category] in [town]", "how do I choose", "how much does it cost"; without a town, the choose, cost, audience and remote forms), the top-scored questions from the map, and two brand prompts ("is [business] any good", "what does [business] do"), each with a second wording a customer might type (`reword P-NN --b …` fixes one the member would not say). `prompts` writes the checklist with a column per engine.
2. Logged out, or in a private window, the member (or the skill with the member watching) runs each wording on **Google's AI** (the AI Overview or AI Mode; note whether the profile shows in the local pack too), **ChatGPT** and **Perplexity**, and writes in the cell what came back: `own` (the website cited), `profile` (the Business Profile or Maps shown), `named` (named, no link), `directory` (a directory page about the business), `competitor` (someone else, not us), `none`; `profile/none` records wording a and b. **Gemini and Copilot** are a quarterly look (`plan --all-engines`), not a monthly one; this buyer is on Google first.
3. `log --from search/checks/YYYY-MM-prompts.md` reads the checklist. A second run on another day (a second copy of the row, or `--run 2`) catches the variation: the same business reappears only 40 to 50% of the time.
4. `report --md`: the share of customer prompts where the business was seen, by engine and by kind, consistency, who the competitors were, the prompts never seen (next month's work), and the brand prompts that did not find the business (a wrong fact to fix at its source this week). Brand prompts stay out of the headline share because they should always find the business. The trend over three months is the signal; one month is noise.

Category prompts are the ones that bring strangers and move slowest. Question prompts test the answer pages one by one.

## 4. Maintain (monthly, an hour)

- **Refresh one page**: the answer page sitting at Search Console positions 5 to 20 with the most impressions; re-read the sources, update the numbers, add what has been asked since, move `updated`. A date never moves without a change.
- **Prune or merge**: a page with no clicks and no citations after twelve months is merged into its hub or removed, with a redirect where the builder allows.
- **Listings**: `profile_tracker.py listings check`; fix any mismatch; add the next one on the list if fewer than five are live.
- **One mention** earned and logged.
- **Reviews**: `profile_tracker.py report --md`: asks, reviews, the ask-to-review share, unanswered, velocity; a month with no new review means the ask has stopped, not that clients are unhappy.
- **The map**: add the Search Console queries not yet in it; retire what has stopped being asked; rate anything unrated.
- **Yearly**: every published page re-read; every regulated page re-reviewed by its reviewer; the author line and credentials still true; the crawler settings still open.

## 5. The two clocks

Judge each thing at the right time. The profile and the review loop show first: the score and the review count at once, calls and direction requests usually within a month or two (nobody has measured this properly, so it is a rule of thumb, not a promise). The pages show in months: clicks at three months, citations at three to six, a category prompt naming the business when the listings, the mentions and the pages have all had time. A member who judges the pages at four weeks will stop; a member who judges the profile at six months has waited too long to fix it.
