# Source Types Reference

The 8 source types this skill can generate watchers for. Each includes technical access path, API requirements, cost, and reliability notes.

---

## 1. PODCASTS

**Access path:** RSS feeds (universal) + transcript sources

**How to find RSS feeds:**
- Apple Podcasts: search "Listen Notes RSS finder"
- Spotify: hides RSS — use Castos's RSS finder
- Direct: most podcast websites show an RSS icon in the footer

**Transcript sources (the two the generated watcher supports, in the order it tries them):**
1. Listen Notes API (needs a key on a paid plan that includes transcripts; not every episode has one)
2. Speech-to-text of the audio through the member's OpenAI key (off until `WHISPER_ENABLED=true`; billed per minute of audio; needs `ffmpeg` installed for audio files over 25 MB)

The member must turn on at least one. With neither, the watcher captures nothing and says so. Transcripts published inside the feed itself and Apple Podcasts transcripts are not read by the generated watcher.

**Cost estimate:** $3-5/month for 20 podcasts for scoring and summaries (using gpt-4o-mini for filtering). Speech-to-text is extra: the founder's figure was $0.006 a minute, about 36 cents for an hour-long episode. Check OpenAI's current price before turning it on for many shows.

**Reliability:** High (RSS is stable, has been since 2003)

**Code module pattern:** Use `feedparser` for RSS, multi-strategy transcript fetcher

---

## 2. YOUTUBE

**Access path:** YouTube Data API v3 + transcript scraping

**How to find channel IDs:**
- The watcher needs the channel ID, which starts with `UC`. A handle (`@channelname`) or a channel URL will not work in `sources.json`.
- Open the channel page, click "About", then "Share channel", then "Copy channel ID". Store that ID.

**Transcript sources:**
1. YouTube's auto-generated captions (free, available for 95%+ of videos)
2. Whisper fallback for videos without captions

**API requirements:**
- YouTube Data API v3 (free, 10,000 quota units/day)
- 1 channel video list = ~5 quota units
- Sufficient for monitoring 50+ channels

**Cost estimate:** $2-4/month for 10-20 channels

**Reliability:** High (Google API)

**Code module pattern:** Use `google-api-python-client` + `youtube-transcript-api`

---

## 3. TWITTER / X

**Access path:** X API v2 (paid) OR scraping (fragile)

**Two implementation paths:**

**Path A — Official API (recommended):**
- X API Basic tier: $100/month
- Gets you 50K tweets/month read access
- Stable, well-documented

**Path B — Twitter list RSS via third-party (risky):**
- Services like Nitter (often down) or RSSHub (self-hosted)
- Free but breaks frequently
- Only use if you accept fragility

**Cost estimate:** $100/month (API) OR free + fragile

**Reliability:** Medium-High (API) / Low (scraping)

**Recommendation in the skill:** Flag the cost upfront. If they balk at $100/month, suggest they pick a different source for now.

**Code module pattern:** Use `tweepy` for API, list-based filtering

---

## 4. NEWSLETTERS

**Access path:** Email forwarding to a dedicated address + IMAP fetching

**Setup pattern:**
1. Member creates a dedicated email (e.g., `kb@theirdomain.com`)
2. They forward Substack/Beehiiv subscriptions to that address
3. Watcher polls the IMAP inbox, extracts HTML email content, strips ads/footers
4. High-signal newsletters → Obsidian

**Cost estimate:** Free (just email forwarding) + ~$2/month LLM costs

**Reliability:** Very high (email is robust)

**Limitations:**
- Member has to actually set up forwarding (15 min one-time setup)
- Some newsletters use unusual formatting that strips imperfectly

**Code module pattern:** Use `imaplib` + `BeautifulSoup` for HTML cleanup

---

## 5. RSS / BLOGS

**Access path:** Direct RSS (universal)

**Simplest source type.** Most blogs and news sites have RSS feeds.

**How to find them:**
- Check the site footer or "Subscribe" page
- Try `[site]/feed`, `[site]/rss`, `[site]/atom.xml`
- Use a service like RSS.app to convert non-RSS sites

**Cost estimate:** $2-4/month for 30+ feeds

**Reliability:** Very high

**Code module pattern:** Use `feedparser`, full article fetch via `requests` + `BeautifulSoup`

---

## 6. REDDIT

**Access path:** Reddit API (free for read-only with rate limits)

**Configuration:**
- Member picks subreddits to monitor
- Filter by minimum upvotes (default: 100)
- Filter by minimum comments (default: 20)
- Time window (default: top posts of last 7 days)

**API requirements:**
- Reddit OAuth app (free, takes 5 minutes to set up)
- 60 requests/minute rate limit (plenty for personal use)

**Cost estimate:** Free + ~$2/month LLM costs

**Reliability:** High (Reddit API is stable)

**Code module pattern:** Use `praw` (Python Reddit API Wrapper)

---

## 7. ARXIV / RESEARCH PAPERS

**Access path:** arXiv API (free, no auth required)

**Configuration:**
- Topics: physics, cs.AI, cs.LG, q-fin, econ, etc.
- Authors: filter by specific researcher names
- Date range: last N days

**Cost estimate:** Free + ~$3-5/month LLM costs (papers are long; extraction is expensive)

**Reliability:** Very high (arXiv is a stable public service)

**Special considerations:**
- Papers are long → use gpt-4o-mini for filtering, gpt-4o for extraction
- PDFs need to be fetched and parsed (use `pypdf`)

**Code module pattern:** Use `arxiv` Python package + PDF text extraction

---

## 8. CUSTOM

When the member's source isn't in the 7 above, ask:

1. "What's the source? (give it a name)"
2. "How does the source make content accessible? (RSS, API, scraping, manual export?)"
3. "Does it require authentication or paid access?"

Based on answers, generate a custom module with:
- Best-fit fetching library
- Clear documentation of limitations
- Honest assessment of reliability

If the source requires anything truly custom (e.g., scraping a JavaScript-rendered site), flag the fragility honestly.

---

## Comparing Sources by Effort/Value

| Source | Setup Effort | Cost | Reliability | Signal Density |
|---|---|---|---|---|
| RSS/Blogs | 5 min | $2/mo | High | Medium |
| Podcasts | 15 min | $3-5/mo | High | High |
| YouTube | 30 min | $2-4/mo | High | Medium |
| Newsletters | 20 min | $2/mo | High | High |
| Reddit | 15 min | $2/mo | High | Variable |
| ArXiv | 10 min | $3-5/mo | High | Very High (if relevant) |
| Twitter | 30 min | $100/mo | Medium-High | Very High |
| Custom | 1-2 hrs | Varies | Varies | Varies |

**Recommended first watcher for most members:** Podcasts OR RSS/Blogs (best signal-to-effort ratio).
