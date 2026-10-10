# Podcast Watcher for Obsidian

Automated podcast monitoring → transcript pulling → LLM importance filtering → auto-expanding Obsidian knowledge base.

Built for Build Room members on Week 3 of the Obsidian KB month.

## What This Does

You give it a list of podcast RSS feeds.
It checks for new episodes on a schedule.
It pulls or generates transcripts.
It scores each episode for importance against YOUR specific interests.
High-signal episodes get added to your Obsidian vault with summaries, key insights, and timestamps.

You stop "trying to remember what Tim Ferriss said" and start having it permanently captured.

## How It Works (Architecture)

```
┌─────────────────────┐
│ Your podcast list   │  (feeds.json — RSS URLs)
│ (RSS feeds)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Feed checker       │  (runs daily via cron/scheduler)
│  (new episodes?)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Transcript fetcher │  (Apple Podcasts API, Listen Notes,
│                     │   or Whisper transcription fallback)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLM importance     │  (scored against your interests.md)
│  filter             │  (1-10 scale, threshold: 7+)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Knowledge extractor│  (summary + insights + quotes
│                     │   + topics + linked concepts)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Obsidian writer    │  (creates note in vault with
│                     │   YAML frontmatter + tags + links)
└─────────────────────┘
```

## What You Get

Every monitored podcast episode becomes (potentially) a structured Obsidian note like this:

```markdown
---
title: "How Naval Thinks About Wealth"
podcast: "The Tim Ferriss Show"
host: "Tim Ferriss"
guest: "Naval Ravikant"
date: 2026-05-15
importance_score: 9
duration: 92 minutes
url: https://...
tags: [wealth, decision-making, leverage, founder-mindset]
---

## Why This Matters For You
[LLM-generated paragraph explaining relevance to YOUR interests]

## Key Insights
- Insight 1 (with timestamp [00:14:23])
- Insight 2 (with timestamp [00:31:45])
- Insight 3 (with timestamp [00:47:02])

## Best Quotes
> "Quote here..." [00:18:30]

## Topics Discussed
- Topic 1 → [[linked concept]]
- Topic 2 → [[linked concept]]

## Action Items / Things To Explore
- [ ] Investigate X
- [ ] Read Y
```

## Setup (5 Steps)

### 1. Install dependencies
```bash
pip install feedparser openai python-dotenv requests pyyaml
```

### 2. Configure your feeds
Edit `config/feeds.json` with podcast RSS URLs.

### 3. Define your interests
Edit `config/interests.md` with what matters to you (this drives importance scoring).

### 4. Set environment variables
Create `.env`:
```
OPENAI_API_KEY=sk-...
OBSIDIAN_VAULT_PATH=/path/to/your/vault
IMPORTANCE_THRESHOLD=7
```

### 5. Run on schedule
```bash
# Manually
python watcher.py

# Or via cron (daily at 6am)
0 6 * * * cd /path/to/podcast-watcher && python watcher.py
```

## File Structure

```
podcast-watcher/
├── README.md                  ← you are here
├── watcher.py                 ← main script
├── config/
│   ├── feeds.json             ← your podcast RSS feeds
│   └── interests.md           ← your interest profile (drives filtering)
├── modules/
│   ├── feed_checker.py        ← detects new episodes
│   ├── transcript_fetcher.py  ← gets transcripts
│   ├── importance_filter.py   ← LLM scoring
│   ├── knowledge_extractor.py ← structured extraction
│   └── obsidian_writer.py     ← writes notes to vault
├── data/
│   └── seen_episodes.json     ← tracks what you've already processed
├── .env.example
└── requirements.txt
```

## Finding RSS Feeds

Most podcasts publish their RSS feed publicly:
- **Apple Podcasts**: Use `https://feed.podbean.com/[show-name]/feed.xml` patterns or paste the Apple URL into a feed finder
- **Spotify**: Spotify hides RSS feeds — use Castos's RSS finder or search "[podcast name] RSS feed"
- **Direct**: Look at the podcast's website footer; most show an RSS icon
- **Listen Notes**: Search any podcast at listennotes.com and find the RSS feed in the show metadata

## Cost Estimate

For monitoring 20 podcasts at ~3 episodes/week:
- ~60 episodes/week to check (not all transcribed)
- ~10-15 high-signal episodes that get full extraction
- ~$3-5/month in OpenAI API costs (using gpt-4o-mini for filtering, gpt-4o for extraction)
- Transcript costs: free if Apple/Listen Notes has them; $0.006/min if Whisper fallback

## Customization Hooks

Once it's running, easy customizations:
- Change `IMPORTANCE_THRESHOLD` to be more/less selective
- Adjust the LLM prompts in `modules/importance_filter.py` for different scoring criteria
- Add custom YAML frontmatter fields in `modules/obsidian_writer.py`
- Filter by guest name, topic keywords, or episode length
- Add Slack/email notifications when high-importance episodes are added

## What This Connects To

This is Week 3 of the Obsidian KB month:
- **Week 1**: Obsidian.md installation and vault setup
- **Week 2**: YouTube watcher (automated YouTube monitoring + LLM importance filtering)
- **Week 3**: Podcast watcher (this) — same architecture, different source
- **Week 4**: Optimization (better tagging, linking, querying)

The architecture is identical to Week 2's YouTube watcher — only the input source differs. If you understood Week 2, you understand 90% of this.
