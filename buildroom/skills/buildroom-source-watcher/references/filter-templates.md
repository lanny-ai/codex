# Filter Templates Reference

8 pre-built filter templates that determine what kind of content the watcher captures. Each template adjusts the LLM scoring prompt to look for specific signals.

The template gets injected into the `importance_filter.py` module at generation time.

---

## Template 1 — TACTICAL ONLY

**Captures:** Step-by-step how-to content, specific tactics, executable instructions.

**Rejects:** Inspirational content, philosophy, biography, hot takes.

**LLM prompt injection:**
```
Score HIGH (7-10) only when the content contains:
- Specific step-by-step instructions
- Tactics that can be executed within 24 hours
- Concrete tools, scripts, or methods named with enough detail to act on
- "Here's exactly how I did X" with reproducible specifics

Score LOW (1-3) when content is:
- Inspirational without tactical depth
- Philosophy or general wisdom without actionable steps
- Biographical or "my journey" stories without extractable tactics
```

**Best for:** Operators, builders, and members who want execution-ready material.

---

## Template 2 — FRAMEWORKS ONLY

**Captures:** Mental models, conceptual frameworks, decision-making structures.

**Rejects:** Tactical execution, news, gossip.

**LLM prompt injection:**
```
Score HIGH (7-10) only when the content contains:
- Named mental models or frameworks
- Decision-making structures or heuristics
- Conceptual lenses for understanding a domain
- Multi-part models with clear components

Score LOW (1-3) when content is:
- Tactical execution without underlying framework
- News, events, or one-off stories
- Surface-level observations without conceptual structure
```

**Best for:** Strategists, thinkers, and members building mental models.

---

## Template 3 — CASE STUDIES WITH NUMBERS

**Captures:** Specific results with dollar amounts, percentages, time periods.

**Rejects:** Vague success stories, motivational content, opinion.

**LLM prompt injection:**
```
Score HIGH (7-10) only when the content contains:
- Specific dollar amounts, percentages, or quantified results
- Detailed case studies with start state, action taken, end state
- Quantified before/after comparisons
- Named businesses with verifiable numbers

Score LOW (1-3) when content is:
- Vague success language without specifics ("I scaled my business," "huge growth")
- Inspirational stories without numbers
- Motivational content
- Opinion without supporting data
```

**Best for:** Marketing operators, performance-driven members, proof-stack builders.

---

## Template 4 — COUNTER-CONVENTIONAL

**Captures:** Insights that challenge mainstream thinking in the domain.

**Rejects:** Conventional wisdom, mainstream advice, restated common knowledge.

**LLM prompt injection:**
```
Score HIGH (7-10) only when the content contains:
- Claims that contradict mainstream consensus in the domain
- "Everyone says X but actually Y" structure
- Reframes or contrarian takes backed by reasoning or proof
- Counter-intuitive findings supported by evidence

Score LOW (1-3) when content is:
- Restated conventional wisdom
- Generic advice everyone in the field has heard
- Surface-level "be different" without substance
- Contrarian tone without contrarian content
```

**Best for:** Members building distinctive thinking, contrarians, positioning-focused founders.

---

## Template 5 — LONG-FORM DEEP DIVES

**Captures:** Deep, substantive content with sustained reasoning. Usually long episodes/articles.

**Rejects:** Short hits, surface skims, quick takes.

**LLM prompt injection:**
```
Score HIGH (7-10) only when the content contains:
- Sustained reasoning over a single topic for extended duration
- Multi-layered analysis with depth
- 60+ minute conversations or 3000+ word articles
- Complex topics handled with appropriate complexity

Additionally, automatically deprioritize:
- Content under 30 minutes (podcasts) or 800 words (articles)
- Format-driven content (top 10 lists, quick tips)
- Multi-topic episodes that skim each
```

**Best for:** Members who want substance over volume; researchers; deep thinkers.

---

## Template 6 — HIGH-PROFILE PEOPLE

**Captures:** Content featuring specific named experts the member cares about.

**Rejects:** Content without the named people.

**LLM prompt injection (parameterized):**
```
The member specifically wants content featuring these people:
[INSERT MEMBER'S TARGET PEOPLE LIST]

Score HIGH (7-10) only when:
- The content prominently features one or more of these named people
- The named person delivers substantive insights (not just a quick mention)
- The named person is the source/speaker, not just a reference

Score LOW (1-3) when:
- The named person is only mentioned briefly
- The content is about a different topic entirely
```

**Best for:** Members tracking specific thought leaders, operators, or experts.

**Setup note:** Ask the member for their list of target people during Phase 4.

---

## Template 7 — INDUSTRY SPECIFIC

**Captures:** Content about a specific industry or niche the member operates in.

**Rejects:** Cross-industry generic content.

**LLM prompt injection (parameterized):**
```
The member specifically wants content about this industry/niche:
[INSERT MEMBER'S INDUSTRY]

Score HIGH (7-10) only when:
- The content directly addresses this industry/niche
- Insights are applicable to operators in this space
- Industry-specific case studies, players, or dynamics are discussed

Score LOW (1-3) when:
- Content is generic business advice not specific to this industry
- Cross-industry insights without industry-specific application
- Adjacent industries that don't apply
```

**Best for:** Members in specific verticals (real estate, SaaS, ecommerce, coaching, etc.).

---

## Template 8 — CUSTOM BLEND

When the member picks this, walk them through 4 adjustable knobs:

### Knob 1: Relevance Threshold (1-10)
"How strict should the relevance bar be? 7 = highly relevant. 5 = somewhat relevant. 3 = anything tangential."

### Knob 2: Specificity Preference (concrete vs. abstract)
"Do you prefer concrete tactics (10) or abstract concepts (1) or balanced (5)?"

### Knob 3: Novelty Bias (1-10)
"How much should the watcher prefer NEW ideas vs. ideas you already know well? 10 = only new. 1 = capture everything."

### Knob 4: Depth Preference (1-10)
"Should the watcher prefer deep dives (10) or quick hits (1)?"

Based on their answers, generate a custom filter prompt.

---

## Combining Templates

If the member picks multiple templates (e.g., "Tactical Only" + "Industry Specific"), combine the LLM prompt injections with AND logic:

```
The content must satisfy BOTH:
1. [Tactical criteria]
2. [Industry-specific criteria]

Only score 7+ when content passes both filters.
```

---

## How Templates Get Injected

In `importance_filter.py`, the system prompt for the LLM scorer includes:

```python
FILTER_TEMPLATE = """
[INSERTED TEMPLATE TEXT HERE]
"""

INTERESTS = """
[USER'S interests.md FILE CONTENT HERE]
"""

# Combined into the LLM system prompt
system_prompt = f"""You are an importance filter for {USER}'s knowledge base.

THEIR INTERESTS:
{INTERESTS}

THEIR FILTER PREFERENCE:
{FILTER_TEMPLATE}

Score the content 1-10. Be strict. Most content should score 3-6.
Reserve 7+ for content that genuinely matches both their interests AND the filter preference.
"""
```

This makes the filter behavior fully customized per member without rewriting code.
