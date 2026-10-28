# The site and the builders: where each setting lives

Menu names change; say "look for" rather than quoting a path, and ask the member to share their screen or a screenshot when a setting cannot be found. Every builder claim here comes from third-party guides unless marked official.

## 1. The five things every site needs before the first answer page

1. **Google Search Console**, verified for the domain; the sitemap submitted. Free. Gives the Performance report, URL inspection ("request indexing") and, since 2026, the generative-AI impressions report.
2. **Bing Webmaster Tools**, verified (import the Search Console property to skip re-verification). Free. Gives the AI Performance report (Copilot citations and the queries behind them) and URL submission. ChatGPT's search relies on Bing's index, so a page Bing has not indexed cannot be cited there.
3. **An About page and an author line**: who the member is, credentials, licence where relevant, a real photo, how long in business, where. Google's helpful-content guidance asks for it; a fabricated author profile is a named low-quality signal.
4. **One page per service**, each answering the question "what is this, who is it for, what does it cost or how does pricing work, what happens first". The strongest-supported page type for local organic and AI visibility.
5. **Crawlers allowed.** Search and answer crawlers (Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, Applebot, Amzn-SearchBot) must not be blocked. Training crawlers are a separate choice. If the domain is behind Cloudflare, open its AI-crawl settings: new domains have blocked AI crawlers by default since July 2025 and categories were tightened in 2026; confirm search and user-fetch bots are allowed. Never block Googlebot or Bingbot.

Then the basics the member's builder mostly handles: HTTPS, mobile layout, a self-referencing canonical, an XML sitemap, Core Web Vitals in the green (LCP 2.5 s, INP 200 ms, CLS 0.1; small next to relevance, but a slow page loses the reader), alt text on images, headings in order.

## 2. The builders

| Builder | Add a page with a custom address, headings, a list | Author line | Schema (JSON-LD) | robots.txt | Sitemap | Verify Search Console and Bing | IndexNow |
|---|---|---|---|---|---|---|---|
| **WordPress (self-hosted)** | native | theme or a free plugin (Rank Math, Yoast) | free plugin adds Article, Person, LocalBusiness | editable in the plugin | plugin, automatic | plugin fields or Site Kit | Rank Math "Instant Indexing", free |
| **WordPress.com** | native | plugin on paid plans | plugin on paid plans (reported all paid plans since April 2026; verify) | paid plan via plugin | automatic | settings or plugin | plugin |
| **Squarespace** | native | a text block under the title; a manual author page | site-wide "Code Injection" header, or the page's "Page Header Code Injection" | not editable; a "Crawlers" setting toggles search and AI crawlers (keep search on) | automatic at /sitemap.xml | meta tag in header injection | none native |
| **Wix** | native | manual | per-page "Advanced SEO" tab, JSON-LD only | editable in SEO tools (one guide disagrees) | automatic, pushed to Google on connect | built-in connect to Google; Bing via Webmaster Tools (custom domain needed) | native on Premium plans |
| **GoHighLevel sites and funnels** | per page: title, description, custom path; headings in the builder | manual | paste into site- or page-level "Head Tracking Code" | no editor found; verify in the account | exists; submit manually; exclude thank-you pages | meta tag in head tracking code | none found |
| **Kajabi** | native per page or post | manual | "Header Page Scripts" is site-wide; per-page schema is hard | not editable; Kajabi says use noindex instead | automatic | meta tag in header scripts | none found |
| **Shopify** | pages and blog | blog author field | theme code | robots.txt.liquid (errors can cost all traffic; leave it alone) | automatic | meta tag in theme or DNS | third-party app |
| **Webflow** | native | CMS field | custom code in page or site head (paid plan) | site settings (paid plan) | automatic | meta tag in custom code | none found |
| **Google Sites** | limited addresses | manual | an embed that may not be read; skip | not editable | automatic | DNS | no |
| **Carrd** | one page with sections | manual | Pro "Head" embed, untested | Pro site files | third-party claim | Pro meta tags | no |

GoHighLevel warning: a funnel built before the custom domain was attached can stay indexed on the highlevel subdomain; set canonical and noindex on the duplicate.

Whatever the builder, the answer page needs only: a custom address, an H1 and H2s, a paragraph, a list or table, a link, an image with alt text and a date line. Every builder in the table can do that. Schema and robots are optional extras; if the builder makes them hard, skip them and say so in `search/site.md`.

## 3. After publishing, each time

1. Open the live page on a phone: does it load, is the answer at the top, does the next-step link work?
2. Search Console: URL inspection, "request indexing".
3. Bing Webmaster Tools: submit the URL (or let IndexNow do it where the builder supports it).
4. Link the new page from its hub or service page, and from one older answer.
5. Record the URL in the question map.

## 4. Free tools, and their limits in 2026

Google Search Console and Bing Webmaster Tools (free, no limits that matter); Google Business Profile performance (in the profile); Google Trends; PageSpeed Insights (field data matters more than the lab score); Rich Results Test and the schema.org validator (still live); WAVE accessibility (one page at a time); AnswerThePublic, AlsoAsked and Ubersuggest (about three free searches a day each); Ahrefs Free (verified sites, a monthly crawl allowance); Semrush free (ten requests a day); ChatGPT, Perplexity, Gemini and Copilot free tiers (enough for the monthly check); Google Alerts (free; set one for the business name and one for the owner's name). Paid citation trackers start at about $29 a month and are not needed.

## 5. `search/site.md`

The record of the member's own site: builder, domain, who can edit, where the header code field is, Search Console and Bing verified (dates), sitemap address, robots or crawler setting, Cloudflare yes or no, the About page address, the service pages, and any workaround the builder needed. Written in Phase 0, updated whenever something changes, read by every later session so nobody rediscovers it.
