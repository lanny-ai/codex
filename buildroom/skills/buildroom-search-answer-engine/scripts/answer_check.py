#!/usr/bin/env python3
"""Answer-page gate, scaffold, schema and robots for the Search & Answer Engine.

An answer page is a markdown file in `search/answers/<slug>.md` with a front-matter block.
Nothing is published until `check` passes every hard gate (the founder's OS Cortex gates,
adapted for a page the member publishes by hand on their own site builder).

  python3 answer_check.py new "How much does X cost?" --slug how-much-x-cost --author "Dana Ruiz" --kind first-hand [--folder search]
  python3 answer_check.py check search/answers/how-much-x-cost.md [--business-file BUSINESS_FILE.md] [--site https://example.com] [--questions search/questions.json]
  python3 answer_check.py schema search/answers/how-much-x-cost.md --site https://example.com [--org "Ruiz Advisory"] [--out file.json]
  python3 answer_check.py robots [--block-training]

Page kinds: `evidence` (three or more outside sources) and `first-hand` (the member's own data or
experience, with a "How we know" section and at least one outside source). Every paragraph or
list item that carries a number or a results claim carries a marker: [S1] (a source), [own] (the
member's own counted data), or [method] (the member's own method, an opinion, not a fact).

Exit code 0 when every hard gate passes (warnings allowed), 1 when a gate fails, 2 on a usage error.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

sys.dont_write_bytecode = True

KINDS = ("evidence", "first-hand")
REGULATED = ("none", "financial", "legal", "medical", "mental-health", "insurance", "real-estate")
STATUSES = ("draft", "ready", "published", "needs-update")
DIRECT_ANSWER_WORDS = 100
MIN_SOURCES = {"evidence": 3, "first-hand": 1}
MIN_ORIGINAL_WORDS = 40
WORDS_LOW, WORDS_HIGH = 300, 2000
SENTENCE_WARN = 24
REQUIRED = ("id", "question", "title", "slug", "kind", "status", "author", "author_credentials", "reviewer", "published",
            "updated", "cluster", "original", "regulated", "next_action", "sources")
GATES = ("front_matter", "direct_answer", "sources", "claims_supported", "original_contribution", "headings", "author",
         "dates", "next_action", "internal_links", "scope_note", "never_say", "typical_result", "no_placeholders",
         "duplicate", "schema_match", "how_we_know")
# Search and answer crawlers (visibility) kept separate from model-training crawlers (a brand choice).
SEARCH_CRAWLERS = ("Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
                   "Claude-SearchBot", "Claude-User", "Applebot", "Amzn-SearchBot")
TRAINING_CRAWLERS = ("GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider",
                     "Amazonbot", "Meta-ExternalAgent")
REGULATED_HINTS = {
    "financial": r"\b(invest|retire|tax|401\(?k\)?|ira|portfolio|mortgage|loan|credit|debt|insurance premium|annuit)",
    "legal": r"\b(lawsuit|sue|liabil|contract|attorney|lawyer|court|divorce|custody|will|estate|llc)\b",
    "medical": r"\b(diagnos|symptom|treatment|dose|medication|surgery|therapy|chronic|pain|disease|injur)",
    "mental-health": r"\b(anxiety|depress|trauma|ptsd|counsel|therapist|suicid|addiction)",
    "insurance": r"\b(policy|premium|claim|deductible|coverage|underwrit)",
    "real-estate": r"\b(tenant|landlord|fair housing|zoning|appraisal|listing agent|buyer agent)",
}
SCOPE_PHRASES = re.compile(r"(general information|not (?:legal|medical|financial|tax|investment|health|professional|individual) advice|"
                           r"talk to (?:your|a) (?:doctor|lawyer|attorney|adviser|advisor|accountant|cpa|professional)|"
                           r"does not replace|is not a substitute)", re.I)
PLACEHOLDERS = re.compile(r"\b(TODO|TBD|TK|lorem ipsum|xxx+|insert .{0,20} here|\[your [^\]]+\]|\[name\]|\[city\])\b", re.I)
RESULT_WORDS = re.compile(r"\b(clients?|customers?|patients?|members?|students?|owners?|people|businesses|families|results?|saved|save|earned|earn|"
                          r"grew|grow|increased|increase|cut|reduced|reduce|doubled|tripled|booked|closed|won|lost)\b", re.I)
NUMBER = re.compile(r"(\$\s?\d|\d+(?:\.\d+)?\s?%|\b\d{2,}\b|\b\d\s?(?:x|times)\b)", re.I)
TYPICAL = re.compile(r"\b(typical|typically|most (?:clients|customers|patients|people|members|businesses)|on average|average|usual|usually|"
                     r"not everyone|results vary|range)\b", re.I)
MARKER = re.compile(r"\[(S\d+|own|method)\]")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)
INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def words(text):
    return len(re.findall(r"[A-Za-z0-9$%'’-]+", text))


# ---------------------------------------------------------------- front matter

def parse_front_matter(text):
    """A small YAML subset: `key: value` lines and `key:` followed by `  - item` lines."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fm, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        lm = re.match(r"^\s+-\s*(.*)$", line)
        if lm and key:
            fm.setdefault(key, [])
            if not isinstance(fm[key], list):
                fm[key] = [fm[key]] if fm[key] else []
            fm[key].append(lm.group(1).strip())
            continue
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            key = km.group(1).strip()
            val = km.group(2).strip()
            fm[key] = val if val else ""
            continue
    return fm, body


def parse_sources(fm):
    """`S1 | Title | Publisher | URL | published YYYY-MM-DD | accessed YYYY-MM-DD` (publisher/dates optional)."""
    raw = fm.get("sources") or []
    if isinstance(raw, str):
        raw = [raw] if raw else []
    out, problems = [], []
    for item in raw:
        parts = [p.strip() for p in item.split("|")]
        sid = parts[0] if parts else ""
        if not re.fullmatch(r"S\d+", sid):
            problems.append(f"source line does not start with an id like S1: '{item[:60]}'")
            continue
        url = next((p for p in parts[1:] if re.match(r"https?://", p)), "")
        title = parts[1] if len(parts) > 1 and not re.match(r"https?://", parts[1]) else ""
        dated = any(re.search(r"\b(20\d\d-\d\d-\d\d|20\d\d)\b", p) for p in parts[2:])
        if not url:
            problems.append(f"{sid} has no URL")
        if not title:
            problems.append(f"{sid} has no title")
        out.append({"id": sid, "title": title, "url": url, "dated": dated, "raw": item})
    return out, problems


# ---------------------------------------------------------------- body analysis

def split_sections(body):
    """Return (h1, [(heading, text)]) with the text before the first H2 under heading ''."""
    h1 = ""
    sections, cur, buf = [], "", []
    for line in body.splitlines():
        if line.startswith("# ") and not h1:
            h1 = line[2:].strip()
            continue
        if line.startswith("## "):
            sections.append((cur, "\n".join(buf)))
            cur, buf = line[3:].strip(), []
            continue
        buf.append(line)
    sections.append((cur, "\n".join(buf)))
    return h1, sections


def strip_code(text):
    return FENCE.sub("", text)


def sentences(text):
    text = re.sub(r"\s+", " ", strip_code(text))
    return [s.strip() for s in re.split(r"(?<=[.!?\]])\s+(?=[A-Z\"'(\[$])", text) if s.strip()]


def paragraphs(text):
    """Paragraphs and list items (each bullet or table row on its own), code fences removed."""
    out = []
    for block in re.split(r"\n\s*\n", strip_code(text)):
        lines = block.strip().splitlines()
        if not lines:
            continue
        if all(re.match(r"\s*([-*]|\d+\.|\|)", l) for l in lines):
            out += [l.strip() for l in lines if l.strip() and not re.match(r"\s*\|?\s*-{2,}", l)]
        else:
            out.append(" ".join(l.strip() for l in lines))
    return out


def first_paragraph(text):
    for para in re.split(r"\n\s*\n", text.strip()):
        p = para.strip()
        if p and not p.startswith(("#", "```", "|", "!", "<")):
            return p
    return ""


def load_business_file_lists(path):
    """§18 never-say claims and §1 retired lines, as lower-case phrases."""
    if not path:
        return [], []
    p = Path(path)
    if not p.exists():
        die(f"business file {p} not found")
    text = p.read_text(encoding="utf-8")
    never, retired = [], []

    def grab(label):
        m = re.search(r"\*\*" + re.escape(label) + r"[^*]*\*\*\s*:?\s*(.*)", text)
        if not m:
            return []
        line = m.group(1).strip()
        if line in ("", "—", "-"):
            return []
        return [x.strip(" .;·\"“”'‘’") for x in re.split(r"[;·]|\s\|\s|,\s(?=[A-Z\"“])", line) if len(x.strip(" .;·\"“”'‘’")) > 3]

    never = grab("Never-say claims")
    retired = grab("Retired lines")
    return [n.lower() for n in never], [r.lower() for r in retired]


# ---------------------------------------------------------------- check

def check_page(path, business_file=None, site=None, questions=None, require_internal=2):
    p = Path(path)
    if not p.exists():
        die(f"{p} not found")
    text = p.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text)
    fails, warns, info = {}, [], {}

    if fm is None:
        fails["front_matter"] = "no front-matter block (--- ... ---) at the top"
        return {"ok": False, "file": str(p), "fails": fails, "warns": warns, "info": info}

    missing = [k for k in REQUIRED if k not in fm or fm[k] in ("", [])]
    if fm.get("reviewer", None) == "none":
        missing = [m for m in missing if m != "reviewer"]
    if missing:
        fails["front_matter"] = "missing: " + ", ".join(missing)
    kind = fm.get("kind", "")
    if kind not in KINDS:
        fails["front_matter"] = (fails.get("front_matter", "") + f"; kind must be {' or '.join(KINDS)}").strip("; ")
    if fm.get("status") and fm["status"] not in STATUSES:
        fails["front_matter"] = (fails.get("front_matter", "") + f"; status must be one of {', '.join(STATUSES)}").strip("; ")
    regulated = fm.get("regulated", "none") or "none"
    if regulated not in REGULATED:
        fails["front_matter"] = (fails.get("front_matter", "") + f"; regulated must be one of {', '.join(REGULATED)}").strip("; ")

    h1, sections = split_sections(body)
    lead = sections[0][1] if sections else ""
    body_nocode = strip_code(body)
    info["words"] = words(body_nocode)
    info["h1"] = h1

    # direct answer: the first paragraph after the H1, at most 100 words, and not a heading or an image
    para = first_paragraph(lead)
    n = words(para)
    info["direct_answer_words"] = n
    if not h1:
        fails["direct_answer"] = "no H1 (the question) at the top of the body"
    elif not para:
        fails["direct_answer"] = "no paragraph before the first H2; the direct answer goes first"
    elif n > DIRECT_ANSWER_WORDS:
        fails["direct_answer"] = f"the first paragraph is {n} words; the direct answer must sit inside the first {DIRECT_ANSWER_WORDS}"
    elif n < 15:
        warns.append(f"direct answer is only {n} words; say the answer in a full sentence or two")
    if h1 and fm.get("question") and re.sub(r"\W", "", h1.lower()) != re.sub(r"\W", "", fm["question"].lower()):
        warns.append("the H1 and the front-matter question differ; use the question as the H1")

    # sources
    sources, problems = parse_sources(fm)
    unique_urls = {s["url"] for s in sources if s["url"]}
    need = MIN_SOURCES.get(kind, 3)
    if problems:
        fails["sources"] = "; ".join(problems)
    elif len(unique_urls) < need:
        fails["sources"] = f"{len(unique_urls)} source URL(s); a {kind or 'evidence'} page needs at least {need} unique"
    if any(not s["dated"] for s in sources):
        warns.append("a source has no date; add the publication or access date")
    own_domain = urlparse(site).netloc.lower().replace("www.", "") if site else ""
    if own_domain and any(own_domain in s["url"] for s in sources):
        warns.append("a source is the member's own site; that is first-hand data, mark it [own] and keep outside sources separate")
    info["sources"] = len(unique_urls)

    # claims ledger: every paragraph or list item with a number or a results claim, outside the Sources section,
    # carries at least one marker; every [S#] used exists in the front matter
    unsupported, unknown = [], []
    ids = {s["id"] for s in sources}
    for heading, sec in sections:
        if heading.lower().startswith(("sources", "about the author")):
            continue
        for para in paragraphs(sec):
            marks = MARKER.findall(para)
            has_number = bool(NUMBER.search(para))
            has_claim = has_number and bool(RESULT_WORDS.search(para))
            if has_number and not marks:
                if not has_claim and re.search(r"\b(20\d\d|step \d|\d+ (?:minute|hour|day|week|month|year)s?)\b", para, re.I):
                    continue   # a date, a step number or a plain duration is not a claim
                unsupported.append(para[:90])
            for m in marks:
                if m.startswith("S") and m not in ids:
                    unknown.append(m)
    if unsupported:
        fails["claims_supported"] = f"{len(unsupported)} sentence(s) with a number or result and no [S#]/[own]/[method] marker, e.g. '{unsupported[0]}'"
    if unknown:
        fails["claims_supported"] = (fails.get("claims_supported", "") + f"; unknown source marker(s): {', '.join(sorted(set(unknown)))}").strip("; ")
    info["marked_sentences"] = len(MARKER.findall(body_nocode))

    # original contribution: the front-matter line plus a section that holds it
    orig = fm.get("original", "")
    orig_words = words(orig) if isinstance(orig, str) else 0
    orig_sections = [s for h, s in sections if re.search(r"(what we|our (?:take|view|method|rule|approach|experience)|how we|what (?:we|i)'d|in our|what nobody)", h, re.I)]
    if orig_words < 12:
        fails["original_contribution"] = "front-matter `original` must say, in at least 12 words, what this page has that no other page has"
    elif not orig_sections or all(words(s) < MIN_ORIGINAL_WORDS for s in orig_sections):
        fails["original_contribution"] = (f"no section of at least {MIN_ORIGINAL_WORDS} words carrying the member's own view or method "
                                          "(a heading like 'What we'd check first', 'Our rule', 'How we handle this')")

    # headings
    h2s = [h for h, _ in sections if h and not h.lower().startswith("sources")]
    question_h2s = [h for h in h2s if h.rstrip().endswith("?")]
    if len(h2s) < 2:
        fails["headings"] = "fewer than two H2 sections"
    elif not question_h2s:
        warns.append("no H2 is a question; question-shaped headings are the ones engines quote")
    if any(words(s) > 350 for _, s in sections):
        warns.append("a section runs over 350 words; split it so each heading answers one thing")

    # author, reviewer, dates
    if not fm.get("author") or not fm.get("author_credentials"):
        fails["author"] = "author and author_credentials are required (who is answering, and why they can)"
    if regulated != "none" and fm.get("reviewer", "none") in ("", "none"):
        fails["author"] = (fails.get("author", "") + f"; a {regulated} page needs a named reviewer").strip("; ")
    for key in ("published", "updated"):
        v = fm.get(key, "")
        if not re.fullmatch(r"20\d\d-\d\d-\d\d", v or ""):
            fails["dates"] = f"{key} must be a date YYYY-MM-DD"
    if "dates" not in fails:
        try:
            pub, upd = date.fromisoformat(fm["published"]), date.fromisoformat(fm["updated"])
            if upd < pub:
                fails["dates"] = "updated is before published"
            elif (date.today() - upd).days > 365 and fm.get("status") == "published":
                warns.append("last updated over a year ago; re-check the facts and bump `updated`")
        except ValueError:
            fails["dates"] = "a date is not a real calendar date"
    if not re.search(r"(updated|last reviewed|reviewed on)\s*:?\s*20\d\d", body_nocode, re.I):
        warns.append("no visible 'Updated: <date>' line in the body; readers and engines both look for it")

    # next action
    na = fm.get("next_action", "")
    if not na or "|" not in na or not re.search(r"https?://|^/|\.html|mailto:", na.split("|", 1)[1].strip()):
        fails["next_action"] = "next_action must be `label | link` (one relevant next step with a working link)"
    elif not any(na.split("|", 1)[1].strip().split("?")[0] in INLINE_LINK.findall(body_nocode) for _ in [0]) and na.split("|", 1)[1].strip() not in body_nocode:
        warns.append("the next-action link does not appear in the body; put it at the end of the page")

    # internal links: relative links or links on the member's domain, anywhere in the body, not counting the sources
    source_urls = {s["url"] for s in sources if s["url"]}
    links = [l for l in INLINE_LINK.findall(body_nocode) if l not in source_urls]
    internal = [l for l in links if l.startswith("/") or (own_domain and own_domain in l)]
    info["internal_links"] = len(internal)
    if site and len(internal) < require_internal:
        fails["internal_links"] = f"{len(internal)} internal link(s); link to at least {require_internal} other pages on the site (a hub or related answer, and the offer or contact page)"
    elif not site and len(internal) < require_internal:
        warns.append(f"{len(internal)} internal link(s) found; pass --site to check them properly; aim for {require_internal} or more")

    # scope note for regulated topics
    detected = [k for k, rx in REGULATED_HINTS.items() if re.search(rx, body_nocode, re.I)]
    info["regulated_hints"] = detected
    if regulated != "none" and not SCOPE_PHRASES.search(body_nocode):
        fails["scope_note"] = f"a {regulated} page needs a visible scope note (general information, not advice; who to talk to)"
    elif regulated == "none" and detected:
        warns.append(f"the text touches {', '.join(detected)} topics; if the page is about one of them set `regulated` and add a scope note")

    # never-say claims and retired lines
    never, retired = load_business_file_lists(business_file)
    low = body_nocode.lower()
    hits = [n for n in never + retired if n and n in low]
    if hits:
        fails["never_say"] = "the page uses a never-say claim or a retired line: " + "; ".join(hits[:3])
    if business_file is None:
        warns.append("no --business-file given, so §18 never-say claims and §1 retired lines were not checked")

    # typical result beside any results claim
    bare = []
    for heading, sec in sections:
        if heading.lower().startswith(("sources", "how we know")):
            continue
        for para in paragraphs(sec):
            if NUMBER.search(para) and RESULT_WORDS.search(para) and re.search(r"\[(own|S\d+)\]", para) and not TYPICAL.search(para):
                bare.append(para[:80])
    if bare:
        fails["typical_result"] = f"{len(bare)} paragraph(s) make a results claim without saying what is typical, e.g. '{bare[0]}'"

    # placeholders
    ph = PLACEHOLDERS.findall(body_nocode) + ([] if isinstance(fm.get("original"), list) else PLACEHOLDERS.findall(str(fm.get("original", ""))))
    if ph:
        fails["no_placeholders"] = "placeholder text left in: " + ", ".join(sorted({x if isinstance(x, str) else x[0] for x in ph})[:4])

    # duplicate against the question map
    if questions:
        qp = Path(questions)
        if qp.exists():
            try:
                qs = json.loads(qp.read_text(encoding="utf-8")).get("questions", [])
            except json.JSONDecodeError:
                qs = []
            dup = [q for q in qs if q.get("status") == "published" and q.get("id") != fm.get("id")
                   and (q.get("slug") == fm.get("slug") or re.sub(r"\W", "", q.get("question", "").lower()) == re.sub(r"\W", "", fm.get("question", "").lower()))]
            if dup:
                fails["duplicate"] = f"already published as {dup[0]['id']} ({dup[0].get('published_url') or dup[0].get('slug')}); update that page instead"
            if fm.get("id") and not any(q.get("id") == fm.get("id") for q in qs):
                warns.append(f"{fm['id']} is not in the question map; add it so the map stays the one list")

    # schema block, if the page carries one
    for lang, block in FENCE.findall(body):
        if lang.lower() in ("json", "jsonld", "json-ld") and '"@type"' in block:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                fails["schema_match"] = f"the JSON-LD block does not parse: {e}"
                continue
            items = data.get("@graph", [data]) if isinstance(data, dict) else data
            for it in items:
                t = it.get("@type", "")
                if t in ("Article", "BlogPosting", "FAQPage", "WebPage") and it.get("headline") and it["headline"] != fm.get("title"):
                    fails["schema_match"] = "the schema headline differs from the page title"
                if t == "FAQPage":
                    qtexts = [e.get("name", "") for e in it.get("mainEntity", [])]
                    if any(q not in h2s and q != h1 for q in qtexts):
                        fails["schema_match"] = "a FAQPage question is not a visible heading on the page"
                if t in ("Article", "BlogPosting") and isinstance(it.get("author"), dict) and it["author"].get("name") and it["author"]["name"] != fm.get("author"):
                    fails["schema_match"] = "the schema author differs from the front-matter author"

    # first-hand pages: a "How we know" section
    if kind == "first-hand":
        hk = [s for h, s in sections if h.lower().startswith("how we know")]
        if not hk or words(hk[0]) < 30:
            fails["how_we_know"] = "a first-hand page needs a 'How we know' section (what was counted, over what period, how many)"
        if "[own]" not in body_nocode:
            warns.append("a first-hand page usually carries [own] markers on the member's own numbers")

    # length and readability (warnings)
    if info["words"] < WORDS_LOW:
        warns.append(f"{info['words']} words; most useful answer pages run {WORDS_LOW} to {WORDS_HIGH}")
    elif info["words"] > WORDS_HIGH:
        warns.append(f"{info['words']} words; over {WORDS_HIGH}, consider splitting into two answers")
    ss = sentences(body_nocode)
    if ss:
        avg = sum(words(s) for s in ss) / len(ss)
        info["avg_sentence_words"] = round(avg, 1)
        if avg > SENTENCE_WARN:
            warns.append(f"average sentence is {avg:.0f} words; shorter sentences are quoted more and read more easily")
    if not re.search(r"^\s*(\||[-*] |\d+\. )", body_nocode, re.M):
        warns.append("no list or table; a short list or table gives engines something to lift")

    ok = not fails
    return {"ok": ok, "file": str(p), "kind": kind, "gates": {g: (g not in fails) for g in GATES},
            "fails": fails, "warns": warns, "info": info,
            "verdict": "READY to publish (fix warnings if you can)" if ok else "HOLD: fix every failed gate, then run check again"}


# ---------------------------------------------------------------- new / schema / robots

TEMPLATE = """---
id: {qid}
question: {question}
title: {title}
slug: {slug}
kind: {kind}
status: draft
author: {author}
author_credentials: {credentials}
reviewer: none
published: {today}
updated: {today}
cluster: {cluster}
original: (12+ words: what this page has that no other page has: your own numbers, your rule, your method, your example)
regulated: none
next_action: Book a 20-minute call | /contact
sources:
  - S1 | Title of the source | Publisher | https://example.org/page | published 2026-01-15 | accessed {today}
---
# {question}

**Short answer:** (Answer the question in two or three plain sentences, under 100 words. Say the number or the decision first, then the one condition that changes it.)

Updated: {today}

## (A question-shaped heading: What decides the answer?)

(Each heading answers one thing. A sentence with a number or a result ends with [S1], [own] or [method].)

## (Another question: What does it cost / how long / what goes wrong?)

- (A short list or a small table gives engines something to lift.)
{how_we_know}
## What we'd check first

(At least 40 words of your own view: the rule you use, the mistake you see most, the example from your own work. This is the part no other page has.)

## Sources

- [S1] Title of the source, Publisher, 2026. https://example.org/page

*Next step:* [Book a 20-minute call](/contact)
"""

HOW_WE_KNOW = """
## How we know

(First-hand pages only: what you counted, over what period, how many clients or jobs, and what you did not count. Then the number with [own].)
"""


def cmd_new(a):
    folder = Path(a.folder)
    (folder / "answers").mkdir(parents=True, exist_ok=True)
    slug = a.slug or re.sub(r"[^a-z0-9]+", "-", a.question.lower()).strip("-")[:60]
    out = folder / "answers" / f"{slug}.md"
    if out.exists() and not a.force:
        die(f"{out} already exists (use --force to overwrite)")
    title = a.title or a.question.rstrip("?")
    out.write_text(TEMPLATE.format(qid=a.id or "Q-00", question=a.question, title=title, slug=slug, kind=a.kind, author=a.author,
                                   credentials=a.credentials or "(credentials: years, qualification, how many clients)",
                                   today=date.today().isoformat(), cluster=a.cluster or "general",
                                   how_we_know=HOW_WE_KNOW if a.kind == "first-hand" else ""), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(out), "next": f"fill it in, then: answer_check.py check {out}"}, indent=2))


def cmd_check(a):
    r = check_page(a.file, a.business_file, a.site, a.questions, a.internal_links)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["ok"] else 1)


def cmd_schema(a):
    p = Path(a.file)
    if not p.exists():
        die(f"{p} not found")
    fm, body = parse_front_matter(p.read_text(encoding="utf-8"))
    if fm is None:
        die("no front matter")
    site = a.site.rstrip("/")
    url = f"{site}/{a.path.strip('/')}" if a.path else f"{site}/answers/{fm.get('slug', '')}"
    h1, sections = split_sections(body)
    org = a.org or fm.get("organization", "") or ""
    person = {"@type": "Person", "name": fm.get("author", "")}
    if fm.get("author_credentials"):
        person["description"] = fm["author_credentials"]
    if a.author_url:
        person["url"] = a.author_url
    article = {
        "@type": "Article",
        "@id": url + "#article",
        "headline": fm.get("title", h1),
        "description": first_paragraph(sections[0][1] if sections else "")[:300],
        "url": url,
        "mainEntityOfPage": url,
        "datePublished": fm.get("published", ""),
        "dateModified": fm.get("updated", ""),
        "author": person,
        "inLanguage": "en",
    }
    if org:
        article["publisher"] = {"@type": "Organization", "name": org, "url": site}
    if fm.get("reviewer") and fm["reviewer"] != "none":
        article["reviewedBy"] = {"@type": "Person", "name": fm["reviewer"]}
    graph = [article, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site + "/"},
            {"@type": "ListItem", "position": 2, "name": "Answers", "item": site + "/answers/"},
            {"@type": "ListItem", "position": 3, "name": fm.get("title", h1), "item": url},
        ],
    }]
    # FAQPage only when asked (--faq): FAQ rich results ended for every site on 7 May 2026 and structured data does not
    # earn AI citations, so it is a harmless extra for the question-shaped headings, nothing more.
    faqs = []
    for h, s in sections:
        if h.endswith("?") and 0 < words(s) <= 120:
            ans = re.sub(r"\s+", " ", MARKER.sub("", strip_code(s))).strip()
            faqs.append({"@type": "Question", "name": h, "acceptedAnswer": {"@type": "Answer", "text": ans}})
    if faqs and a.faq:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faqs})
    data = {"@context": "https://schema.org", "@graph": graph}
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "wrote": a.out, "types": [g["@type"] for g in graph]}, indent=2))
    else:
        print(out)


def cmd_robots(a):
    lines = ["# Search and answer crawlers: allowed (these decide whether the site can be found and cited)"]
    for ua in SEARCH_CRAWLERS:
        lines += [f"User-agent: {ua}", "Allow: /", ""]
    lines.append("# Model-training crawlers: a separate brand choice. Blocking them does not affect search or answer visibility.")
    for ua in TRAINING_CRAWLERS:
        lines += [f"User-agent: {ua}", "Disallow: /" if a.block_training else "Allow: /", ""]
    lines += ["User-agent: *", "Allow: /", "", f"Sitemap: {a.site.rstrip('/')}/sitemap.xml" if a.site else "Sitemap: https://YOUR-DOMAIN/sitemap.xml"]
    print("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("question"); s.add_argument("--slug", default=""); s.add_argument("--title", default="")
    s.add_argument("--author", required=True); s.add_argument("--credentials", default=""); s.add_argument("--kind", default="evidence", choices=KINDS)
    s.add_argument("--id", default=""); s.add_argument("--cluster", default=""); s.add_argument("--folder", default="search")
    s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_new)
    s = sub.add_parser("check"); s.add_argument("file"); s.add_argument("--business-file", default=None); s.add_argument("--site", default="")
    s.add_argument("--questions", default=""); s.add_argument("--internal-links", type=int, default=2); s.set_defaults(f=cmd_check)
    s = sub.add_parser("schema"); s.add_argument("file"); s.add_argument("--site", required=True); s.add_argument("--path", default="")
    s.add_argument("--org", default=""); s.add_argument("--author-url", default=""); s.add_argument("--faq", action="store_true")
    s.add_argument("--out", default=""); s.set_defaults(f=cmd_schema)
    s = sub.add_parser("robots"); s.add_argument("--site", default=""); s.add_argument("--block-training", action="store_true"); s.set_defaults(f=cmd_robots)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
