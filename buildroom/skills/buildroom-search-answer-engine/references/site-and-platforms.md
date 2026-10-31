# The site and the builders: where each setting lives

Menu names change; say "look for" rather than quoting a path, and ask the member to share their screen or a screenshot when a setting cannot be found. Every builder claim here comes from third-party guides unless marked official.

## 1. The five things every site needs before the first answer page

1. **Google Search Console**, verified the easy way (the builder's own "connect to Google" button, or the HTML-tag method the console offers for one address; a full domain property needs a DNS record and can wait); the sitemap submitted. Free. Gives the Performance report, URL inspection ("request indexing") and, since 2026, the generative-AI impressions report.
2. **Bing Webmaster Tools**, verified (import the Search Console property to skip re-verification). Free. Gives the AI Performance report (Copilot citations and the queries behind them) and URL submission. ChatGPT's search runs its own crawler and blends other indexes, Bing among them; how much of its citing depends on Bing is disputed (one study said most, a replication said a quarter), so Bing verification is cheap insurance, not a guarantee.
3. **An About page and an author line**: who the member is, credentials, licence where relevant, a real photo, how long in business, where. Google's helpful-content guidance asks for it; a fabricated author profile is a named low-quality signal.
4. **One page per service**, each answering the question "what is this, who is it for, what does it cost or how does pricing work, what happens first". The strongest-supported page type for local organic and AI visibility.
5. **Crawlers allowed.** Search and answer crawlers (Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, Applebot, Amzn-SearchBot, Meta-WebIndexer) and Google-Extended (Gemini grounding) must not be blocked. **If the builder has a "block AI bots" or "block AI crawlers" switch, it is probably on, and it blocks the answer engines along with the training bots: turn it off.** Then open `yourdomain.com/robots.txt`, save it, and run `answer_check.py robots --check robots.txt`; it names any answer crawler still blocked. If the domain is behind Cloudflare, open its AI-crawl settings: new domains have blocked AI crawlers by default since July 2025 and categories were tightened in 2026; confirm search and user-fetch bots are allowed. Training crawlers are a separate choice; the default is to allow them. Never block Googlebot or Bingbot.

The builder handles the technical basics (the secure padlock, the phone layout, the sitemap, speed). The member's part: if a page feels slow on their own phone, say so; alt text on every image; headings in order; and the home page links to every service page, which is what gets a small site's pages found and indexed.

## 2. The builders

| Builder | Add a page with a custom address, headings, a list | Author line | Schema (JSON-LD) | robots.txt | Sitemap | Verify Search Console and Bing | IndexNow |
|---|---|---|---|---|---|---|---|
| **WordPress (self-hosted)** | native | theme or a free plugin (Rank Math, Yoast) | free plugin adds Article, Person, LocalBusiness | editable in the plugin | plugin, automatic | plugin fields or Site Kit | Rank Math "Instant Indexing", free |
| **WordPress.com** | native | plugin on paid plans | plugin on paid plans (reported all paid plans since April 2026; verify) | paid plan via plugin | automatic | settings or plugin | plugin |
| **Squarespace** | native | a text block under the title; a manual author page | site-wide "Code Injection" header, or the page's "Page Header Code Injection" | not editable; a "Crawlers" setting toggles search and AI crawlers (keep search on) | automatic at /sitemap.xml | meta tag in header injection | none native |
| **Wix** | native | manual | per-page "Advanced SEO" tab, JSON-LD only | editable in SEO tools (one guide disagrees) | automatic, pushed to Google on connect | built-in connect to Google; Bing via Webmaster Tools (custom domain needed) | native (Premium plans per Wix; one 2026 guide says all) |
| **GoHighLevel sites and funnels** | per page: title, description, custom path; headings in the builder | manual | paste into site- or page-level "Head Tracking Code" | no editor found; verify in the account | exists; submit manually; exclude thank-you pages | meta tag in head tracking code | none found |
| **Kajabi** | native per page or post | manual | "Header Page Scripts" is site-wide; per-page schema is hard | not editable; Kajabi says use noindex instead | automatic | meta tag in header scripts | none found |
| **Shopify** | pages and blog | blog author field | theme code | robots.txt.liquid (errors can cost all traffic; leave it alone) | automatic | meta tag in theme or DNS | third-party app |
| **Webflow** | native | CMS field | custom code in page or site head (paid plan) | site settings (paid plan) | automatic | meta tag in custom code | none found |
| **Google Sites** | limited addresses | manual | an embed that may not be read; skip | not editable | automatic | DNS | no |
| **Carrd** | one page with sections | manual | Pro "Head" embed, untested | Pro site files | third-party claim | Pro meta tags | no |

GoHighLevel warning: a funnel built before the custom domain was attached can stay indexed on the highlevel subdomain; set canonical and noindex on the duplicate.

Whatever the builder, the answer page needs only: a custom address, an H1 and H2s, a paragraph, a list or table, a link, an image with alt text and a date line. Every builder in the table can do that. Schema (`answer_check.py schema --path <the real path>`) and a robots file (`robots --out`) are optional extras; if the builder makes them hard, skip them and say so in `search/site.md`. The one setting that is not optional is the "block AI bots" switch, off.

## 3. Publishing and indexing, each time (`publish.py`)

**Getting the page onto the site.** Two routes, decided by the builder:

| Builder | Route | Keys in `.env` (never in the chat) |
|---|---|---|
| WordPress (self-hosted or a paid wordpress.com plan) | `publish.py publish <page> --builder wordpress --site https://…` creates or updates the page by slug | `WP_USER`, `WP_APP_PASSWORD` (an application password made under the user's profile, not the login password) |
| Webflow | `--builder webflow`: a live CMS item (fields name, slug, post-body, post-summary) | `WEBFLOW_API_TOKEN`, `WEBFLOW_COLLECTION_ID` |
| Shopify | `--builder shopify`: a page at /pages/<handle> | `SHOPIFY_STORE`, `SHOPIFY_ACCESS_TOKEN` |
| Wix | `--builder wix`: a blog post (the Blog API; a table becomes one line per row) | `WIX_API_KEY`, `WIX_SITE_ID` |
| Squarespace, Kajabi, GoHighLevel, Google Sites, Carrd | no page API: `publish.py render <page> --site … --schema …` writes the HTML and a ten-minute paste checklist; the member pastes | none |

`publish.py keys` says which builders the member's keys unlock, by key name only. `--dry-run` shows the request with every key masked; `--draft` publishes unpublished. The skill never drives a builder's login with a browser and never asks for a key in the chat.

**Getting it indexed.** Nobody submits a page "to AI"; the engines crawl it.

1. `publish.py verify <url>`: live, a title and an H1, no noindex, the canonical pointing at itself, the answer crawlers allowed in robots.txt, the page in the sitemap (sitemap indexes followed).
2. **Google** (and its AI Overviews and AI Mode, which use the same index): the sitemap, a link from the home page and the service page, and the member's click in Search Console → URL inspection → Request indexing. There is **no legitimate API** for requesting indexing of ordinary pages (Google's Indexing API is for job postings and live events only, and using it otherwise breaks the guidelines; the Search Console API can inspect a page but not request it), so this stays a click.
3. **Bing and Copilot**: `publish.py indexnow <url>`, once the IndexNow key file is on the site root (`publish.py indexnow-key` makes it; Wix and WordPress with Rank Math can host it; Squarespace cannot, so skip IndexNow there and submit the URL in Bing Webmaster Tools by hand). ChatGPT crawls on its own and leans partly on Bing's index, so this helps there too.
4. **Perplexity, Claude, Meta**: their own crawlers find a page that is linked and allowed; nothing to submit.
5. Link the new page from its hub or service page and from one older answer; make sure the home page links to every service page.
6. `publish.py record <page> --url … --questions search/questions.json`: the page and its question marked published with the address. Expect Bing within days, ChatGPT or Perplexity within one to two weeks, Google when it gets there.

## 4. Free tools, and their limits in 2026

Google Search Console and Bing Webmaster Tools (free, no limits that matter); Google Business Profile performance (in the profile); Google Trends; PageSpeed Insights (field data matters more than the lab score); Rich Results Test and the schema.org validator (still live); WAVE accessibility (one page at a time); AnswerThePublic, AlsoAsked and Ubersuggest (about three free searches a day each); Ahrefs Free (verified sites, a monthly crawl allowance); Semrush free (ten requests a day); ChatGPT, Perplexity, Gemini and Copilot free tiers (enough for the monthly check); Google Alerts (free; set one for the business name and one for the owner's name). Paid citation trackers start at about $29 a month and are not needed.

## 5. `search/site.md`

The record of the member's own site: builder, domain, who can edit, where the header code field is, Search Console and Bing verified (dates), sitemap address, robots or crawler setting, Cloudflare yes or no, the About page address, the service pages, and any workaround the builder needed. Written in Phase 0, updated whenever something changes, read by every later session so nobody rediscovers it.
