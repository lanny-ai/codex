---
name: audience-insight-playbook
description: >-
  Mine the voice of the customer for any niche and turn it into a marketing
  playbook — ranked pain points, an exact-words swipe file, an objection table,
  a content idea pipeline, and a lead-spotting guide, all with cited sources.
  Use this whenever the user wants audience research, customer/market research,
  "voice of customer" insight, pain-point mining, messaging or positioning
  research, content ideas for a niche, prospect/lead research, or wants to
  understand what their target customers complain about and how they talk. Also
  trigger when someone asks to research a subreddit, forum, or community to find
  customer language and content angles, or says things like "what do my
  customers care about", "find me content ideas for X", "what objections do
  buyers have", or "research the [industry] market for me". Works for any
  business, niche, product, or service.
---

# Audience Insight Playbook

## What this skill does and why

Great marketing is built on the customer's own words — their pains, the exact
phrases they use, the objections in their head, and the questions they keep
asking. This skill turns scattered web research into one structured, cited
playbook a marketer can act on immediately: write ads, build offers, plan
content, and find ready-to-buy prospects.

The job is not to dump search results. It is to **synthesize** raw voice-of-
customer material into a decision-ready document, ranked by how directly each
insight maps to what the user sells.

## Step 1 — Get the three inputs you need

You need three things before researching. Pull them from the conversation if
they're already there; otherwise ask in a single message (don't interrogate one
question at a time):

1. **The niche / industry** — e.g. "AI marketing agency", "Pilates studios",
   "B2B SaaS for accountants".
2. **What they sell** — the product or service, so insights can be ranked by
   relevance to the offer.
3. **The target customer** — who buys (e.g. "local service businesses", "SMB
   owners broadly", "enterprise marketing leaders"). This decides which
   communities and search angles matter.

If the user says "you decide" on any of these, infer a sensible default from
context, state your assumption plainly, and proceed — don't stall.

## Step 2 — Know your source constraints (important)

Reddit is the classic place for this research, but **Reddit is blocked across
automated tools** (it blocks Anthropic's crawler, and the browsing tool blocks
the domain). Don't burn time retrying it. Two honest paths:

- **Default — accessible sources.** Mine the same voice-of-customer material
  from sources that *are* reachable: industry blogs, Quora threads, agency/
  practitioner post-mortems, review sites, and recent data/stat reports. Always
  pass `blocked_domains: ["reddit.com"]` to web search so results don't error.
- **If the user wants real Reddit data**, tell them the workaround: they paste
  in thread text or comments, and you analyze it. They grab; you synthesize.

Be upfront about which path you're on so the user trusts the output.

## Step 3 — Run the research sweep

Search across these six angles. Run them in parallel where possible. Adapt the
wording to the user's niche and customer — the angles are the constant, the
keywords change.

1. **Demand pain** — why this audience struggles with the core problem the offer
   solves (e.g. "why [audience] struggle to get [outcome] 2025/2026").
2. **Operational pain** — the costly, concrete, often-quantified failures
   (response times, missed opportunities, wasted spend). These are gold because
   they come with dollar figures and emotion.
3. **Objections / distrust** — what makes this audience hesitate to buy the
   category of thing the user sells; search for complaints about competitors,
   bad experiences, "wasted money on [category]". Quora and review sites are
   strong here.
4. **Category trends / shifts** — what's newly changing in the space that
   creates urgency (new tech, new buyer behavior). Search the current year.
5. **FAQs / skepticism** — the questions and doubts buyers voice about the
   solution ("is [solution] worth it", "common questions about [category]").
6. **Buying-signal language** — the exact phrases people use when actively
   looking to buy, for the lead-spotting section.

Capture real statistics with their numbers, and capture verbatim phrases — those
are the most valuable raw material. Keep every source URL for citation.

## Step 4 — Build the playbook (output format)

Save a Markdown file named `<Niche>_Audience_Playbook.md` to the outputs
directory using this exact structure. Then present it with the file-sharing
tool. Keep prose tight; this is a working document, not an essay.

```markdown
# [Business/Niche] — Audience Insights & Content Playbook
*Prepared [date] · Target audience: [customer] · Use case: audience research, content, lead spotting*

## A quick note on method
[1–3 sentences: which sources were used, and — if relevant — that Reddit was
unreachable so accessible voice-of-customer sources were substituted.]

## 1. Voice of the customer: the pain points that drive buying
[3–6 pains, RANKED by how directly each maps to what the user sells. For each:
a one-line headline in the customer's framing, then the evidence — concrete
stats with numbers, and what the pain feels like. Flag the single strongest
wedge for this offer.]

## 2. Their exact words (swipe file)
[8–12 near-verbatim phrases the audience uses, ready to drop into ads/emails/
landing pages. Short bullets, quotation marks.]

## 3. Objections to disarm
[A table: Objection | What's underneath it | Reframe to use. 4–6 rows.]

## 4. Content idea pipeline
[Mapped to the pains above. Group into: short-form hooks, long-form/blog/video
titles, email subject lines, and 1–2 lead-magnet ideas. Aim for ~15 ideas.]

## 5. Lead-spotting playbook
[Buying-signal search phrases, what a hot prospect sounds like (specific
problem + already tried something + urgency), where to look for this audience,
and how to engage (be useful first, soft CTA). If live community access was
blocked, frame this as a do-it-yourself guide the user runs on platforms they
can access.]

## 6. Sources
[Grouped by theme, as markdown links. Every claim/stat traceable to a source.]
```

See `references/example_playbook.md` for a fully worked example in the AI-
marketing-agency niche — match its depth and tone.

## Step 5 — Offer the natural next steps

After delivering, briefly offer the high-leverage follow-ons (pick what fits):
turn the content ideas into a scheduled generator, build the lead-magnet
(e.g. a calculator) for real, or analyze real community threads the user pastes
in. Don't over-explain — one or two concrete offers.

## Quality bar

- **Ranked, not listed.** Pains and ideas ordered by buying relevance, with the
  strongest wedge called out. A flat list is a failure.
- **Real numbers and real phrases.** Vague "customers want more leads" is weak;
  "85% who reach voicemail never call back" is strong. Always prefer the
  specific, cited, quantified version.
- **Cited.** Every stat traces to a linked source. No invented statistics — if
  research didn't surface a number, say so rather than fabricate one.
- **Actionable.** A marketer should be able to write an ad or pick a prospect
  straight from the doc without more work.
