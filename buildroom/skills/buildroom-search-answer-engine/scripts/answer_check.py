#!/usr/bin/env python3
"""Answer-page gate, scaffold, schema and robots for the Search & Answer Engine.

An answer page is a markdown file in `search/answers/<slug>.md` with a front-matter block.
Nothing is published until `check` passes every hard gate (the founder's OS Cortex gates,
adapted for a page the member publishes by hand on their own site builder).

  python3 answer_check.py new "How much does X cost?" --author "Dana Ruiz" --credentials "CPA, 14 years" --kind first-hand [--slug …] [--id Q-04] [--cluster pricing] [--folder search]
  python3 answer_check.py new "Bookkeeping clean-up" --kind service --author "Dana Ruiz" --credentials "…"
  python3 answer_check.py check search/answers/<slug>.md [--business-file BUSINESS_FILE.md] [--site https://example.com] [--questions search/questions.json]
  python3 answer_check.py schema search/answers/<slug>.md --site https://example.com [--path answers/slug] [--org "Ruiz Advisory"] [--out search/answers/<slug>.jsonld]
  python3 answer_check.py robots [--site https://example.com] [--block-training] [--out search/robots.txt]
  python3 answer_check.py robots --check robots.txt          # a pasted or downloaded robots.txt: which answer crawlers it blocks

Page kinds: `evidence` (three or more outside sources), `first-hand` (the member's own counted data,
with a "How we know" section and at least one outside source) and `service` (one page per service:
what it is, who it is for, what it costs, what happens first; sources optional). Every paragraph or
list item that carries a number or a results claim carries a marker: [S1] (a source), [own] (the
member's own counted data), or [method] (the member's own method or opinion, not a fact). Dates,
years, plain durations, step numbers and phone numbers do not need one.

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

KINDS = ("evidence", "first-hand", "service")
REGULATED = ("none", "financial", "legal", "medical", "mental-health", "insurance", "real-estate")
STATUSES = ("draft", "ready", "published", "needs-update")
DIRECT_ANSWER_WORDS = 100
MIN_SOURCES = {"evidence": 3, "first-hand": 1, "service": 0}
MIN_ORIGINAL_WORDS = 40
WORDS_LOW, WORDS_HIGH = 300, 2000
SENTENCE_WARN = 24
REQUIRED = ("id", "question", "title", "slug", "kind", "status", "author", "author_credentials", "published",
            "updated", "cluster", "original", "regulated", "next_action")
GATES = ("front_matter", "h1", "direct_answer", "sources", "claims_supported", "original_contribution", "headings", "author",
         "dates", "next_action", "internal_links", "scope_note", "never_say", "typical_result", "no_placeholders",
         "duplicate", "schema_match", "how_we_know")
# Search and answer crawlers (being found and cited). Google-Extended is kept out of both lists on purpose: it governs
# Gemini training AND grounding, so blocking it can stop the Gemini app from using the site; it stays allowed.
SEARCH_CRAWLERS = ("Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
                   "Claude-SearchBot", "Claude-User", "Applebot", "Amzn-SearchBot", "Meta-WebIndexer")
GROUNDING_CRAWLERS = ("Google-Extended",)
TRAINING_CRAWLERS = ("GPTBot", "ClaudeBot", "Applebot-Extended", "Bytespider", "Amazonbot", "Meta-ExternalAgent")
REGULATED_HINTS = {
    "financial": r"\b(invest(?:ing|ment)|retire(?:ment)?|tax(?:es)?\b|401\(?k\)?|\bira\b|portfolio|mortgage|loan|credit score|debt|annuit)",
    "legal": r"\b(lawsuit|\bsue\b|liabilit|attorney|lawyer|court|divorce|custody|last will|probate|estate plan|\bllc\b|contract (?:law|dispute))",
    "medical": r"\b(diagnos|symptom|treatment|dose|medication|surgery|chronic (?:pain|illness)|disease|injur)",
    "mental-health": r"\b(anxiety|depress|trauma|ptsd|counsel(?:ing|lor)|therapist|suicid|addiction)",
    "insurance": r"\b(premium|deductible|underwrit|insurance polic)",
    "real-estate": r"\b(tenant|landlord|fair housing|zoning|appraisal|listing agent|buyer'?s agent)",
}
SCOPE_PHRASES = re.compile(r"(general information|not (?:legal|medical|financial|tax|investment|health|professional|individual) advice|"
                           r"talk to (?:your|a) (?:doctor|lawyer|attorney|adviser|advisor|accountant|cpa|professional)|"
                           r"does not replace|is not a substitute)", re.I)
SENTINEL = "‹"   # every scaffold placeholder carries it; a page with one left in does not publish
PLACEHOLDER_WORDS = re.compile(r"\b(TODO|TBD|TK|lorem ipsum|xxx+|insert .{0,20} here)\b", re.I)
PLACEHOLDER_BRACKETS = re.compile(r"\[(?:your [^\]]+|name|city|town|business|date|number)\]", re.I)
PLACEHOLDER_SCAFFOLD = ("Title of the source", "example.org/page", "12 or more words of your own", "Answer in two or three plain sentences",
                        "A question-shaped heading", "Another question:", "A short list or a small table")
OUTCOME = re.compile(r"\b(saved?|earn(?:ed|s)?|grew|grow(?:s|th)?|increased?|cut|reduced?|doubled|tripled|booked|closed|won|lost|paid off|cleared|"
                     r"gained?|recovered|avoided)\b", re.I)
CLIENT_NOUNS = re.compile(r"\b(clients?|customers?|patients?|members?|students?|homeowners?|owners?)\b", re.I)
NUMBER = re.compile(r"(\$\s?\d|\d+(?:\.\d+)?\s?%|\b\d{2,}\b|\b\d\s?(?:x|times)\b)", re.I)
EXEMPT = [  # removed from a paragraph before looking for a number that needs a marker
    r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",        # phone numbers
    r"\b(19|20)\d\d\b",                                                 # years
    r"\b\d+[\s-](?:minute|hour|day|week|month|year)s?\b",               # plain durations
    r"\bstep \d+\b", r"\bpage \d+\b", r"\b\d{1,2}:\d\d\b",              # steps, pages, times of day
    r"\]\([^)]*\)",                                                     # link targets
    r"\[(?:S\d+|own|method)\]",                                         # the markers themselves
]
TYPICAL = re.compile(r"\b(typical|typically|most (?:clients|customers|patients|people|members|businesses|homeowners|owners|jobs)|on average|average|usual|usually|"
                     r"not everyone|results vary|range)\b", re.I)
MARKER = re.compile(r"\[(S\d+|own|method)\]")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)
INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
NEXT_LINK = re.compile(r"^(https?://|/|mailto:|tel:|sms:)")
STOP = {"a", "an", "the", "is", "are", "do", "does", "how", "what", "why", "when", "which", "can", "i", "my",
        "to", "for", "of", "in", "on", "and", "or", "it", "be", "should", "much", "with", "me", "you", "your"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def words(text):
    return len(re.findall(r"[A-Za-z0-9$%'’-]+", text))


def slugify(text, limit=60):
    """The same slug the question map makes, so a page and its question agree."""
    t = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    ws = [w for w in t.split() if w not in STOP] or t.split()
    slug = "-".join(ws)
    if len(slug) > limit:
        slug = slug[:limit].rsplit("-", 1)[0]
    return slug.strip("-") or "page"


def norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


# ---------------------------------------------------------------- front matter

def parse_front_matter(text):
    """A small YAML subset: `key: value` lines (a trailing ` # comment` is ignored) and `key:` with `  - item` lines."""
    m = re.match(r"^﻿?---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fm, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        line = re.sub(r"\s+#\s.*$", "", line)
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
            fm[key] = km.group(2).strip()
    return fm, body


def parse_sources(fm):
    """`S1 | Title | Publisher | URL | published YYYY-MM-DD | accessed YYYY-MM-DD` (publisher and dates optional)."""
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
        if SENTINEL in item or any(ph.lower() in item.lower() for ph in PLACEHOLDER_SCAFFOLD):
            problems.append(f"{sid} is still the scaffold's example source")
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


def is_furniture(para, fm):
    """A byline, a date line or the next-step line: not an answer and not a claim."""
    p = para.strip()
    if re.match(r"^(\*{0,2}By |\*?Updated|\*?Last reviewed|\*Next step|Next step|\*?Reviewed)", p, re.I):
        return True
    if fm.get("author") and p.startswith(fm["author"]):
        return True
    return False


def first_answer_paragraph(text, fm):
    paras = [p.strip() for p in re.split(r"\n\s*\n", strip_code(text).strip()) if p.strip()]
    for p in paras:
        if p.lower().startswith("**short answer"):
            return p
    for p in paras:
        if p.startswith(("#", "```", "|", "!", "<")) or is_furniture(p, fm):
            continue
        return p
    return ""


def unexempt(para):
    t = para
    for rx in EXEMPT:
        t = re.sub(rx, " ", t, flags=re.I)
    return t


def plain_text(md):
    t = re.sub(r"\*\*|__", "", md)
    t = MARKER.sub("", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def load_business_file_lists(path):
    """§18 never-say claims and §1 retired lines, as lower-case phrases. Reads the line after the label (the template's
    parenthetical hint stripped) and any sub-bullets beneath it, until the next field."""
    if not path:
        return [], []
    p = Path(path)
    if not p.exists():
        die(f"business file {p} not found")
    lines = p.read_text(encoding="utf-8").splitlines()

    def grab(label):
        out = []
        for i, line in enumerate(lines):
            m = re.match(r"^\s*-?\s*\*\*" + re.escape(label) + r"[^*]*\*\*[ \t]*(?:\([^)]*\))?[ \t]*:?[ \t]*(.*)$", line)
            if not m:
                continue
            head = re.sub(r"^\([^)]*\)\s*:?\s*", "", m.group(1).strip())
            items = [head] if head else []
            for nxt in lines[i + 1:]:
                if re.match(r"^\s+-\s*", nxt) and not re.match(r"^\s*-\s*\*\*", nxt):
                    items.append(re.sub(r"^\s+-\s*", "", nxt))
                else:
                    break
            for it in items:
                for piece in re.split(r"[;·]|\s\|\s|,\s(?=[A-Z\"“])", it):
                    piece = re.sub(r"\s*\([^)]*\)\s*$", "", piece)           # a trailing annotation
                    piece = piece.strip(" .;·\"“”'‘’-")
                    if len(piece) > 3 and piece not in ("—",):
                        out.append(piece.lower())
            break
        return out

    return grab("Never-say claims"), grab("Retired lines")


# ---------------------------------------------------------------- check

def check_page(path, business_file=None, site=None, questions=None, require_internal=2):
    p = Path(path)
    if not p.exists():
        die(f"{p} not found")
    text = p.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text)
    fails, warns, info = {}, [], {}

    def fail(gate, msg):
        fails[gate] = (fails.get(gate, "") + "; " + msg).strip("; ")

    if fm is None:
        fails["front_matter"] = "no front-matter block (--- ... ---) at the top"
        return {"ok": False, "file": str(p), "fails": fails, "warns": warns, "info": info}

    kind = fm.get("kind", "")
    regulated = fm.get("regulated", "none") or "none"
    if fm.get("reviewer", "") == "" and regulated == "none":
        fm["reviewer"] = "none"
    missing = [k for k in REQUIRED if k not in fm or fm[k] in ("", [])]
    if missing:
        fail("front_matter", "missing: " + ", ".join(missing))
    if kind not in KINDS:
        fail("front_matter", f"kind must be one of {', '.join(KINDS)}")
    if fm.get("status") and fm["status"] not in STATUSES:
        fail("front_matter", f"status must be one of {', '.join(STATUSES)}")
    if regulated not in REGULATED:
        fail("front_matter", f"regulated must be one of {', '.join(REGULATED)}")

    h1, sections = split_sections(body)
    lead = sections[0][1] if sections else ""
    body_nocode = strip_code(body)
    info["words"] = words(body_nocode)
    info["h1"] = h1

    # H1: the question word for word (a service page uses the service name as its title)
    if not h1:
        fail("h1", "no H1 at the top of the body")
    elif kind == "service":
        if fm.get("title") and norm(h1) != norm(fm["title"]):
            fail("h1", "a service page's H1 is the service name (the front-matter title)")
    elif fm.get("question") and norm(h1) != norm(fm["question"]):
        fail("h1", "the H1 must be the question word for word, as the front matter has it")

    # direct answer: the first real paragraph (bylines and date lines skipped), at most 100 words
    para = first_answer_paragraph(lead, fm)
    n = words(para)
    info["direct_answer_words"] = n
    if h1 and not para:
        fail("direct_answer", "no paragraph before the first H2; the direct answer goes first")
    elif n > DIRECT_ANSWER_WORDS:
        fail("direct_answer", f"the opening paragraph is {n} words; the direct answer must sit inside the first {DIRECT_ANSWER_WORDS}")
    elif para and n < 15:
        warns.append(f"direct answer is only {n} words; say the answer in a full sentence or two")

    # sources
    sources, problems = parse_sources(fm)
    unique_urls = {s["url"] for s in sources if s["url"]}
    need = MIN_SOURCES.get(kind, 3)
    if problems:
        fail("sources", "; ".join(problems))
    elif len(unique_urls) < need:
        fail("sources", f"{len(unique_urls)} source URL(s); a {kind or 'evidence'} page needs at least {need} unique")
    if any(not s["dated"] for s in sources):
        warns.append("a source has no date; add the publication or access date")
    own_domain = urlparse(site).netloc.lower().replace("www.", "") if site else ""
    if own_domain and any(own_domain in s["url"] for s in sources):
        warns.append("a source is the member's own site; that is first-hand data, mark it [own] and keep outside sources separate")
    info["sources"] = len(unique_urls)

    # claims ledger: every paragraph or list item with a number (after dates, durations, phones, steps and links are set
    # aside) carries at least one marker; every [S#] used exists in the front matter
    unsupported, unknown = [], []
    ids = {s["id"] for s in sources}
    for heading, sec in sections:
        if heading.lower().startswith(("sources", "about the author")):
            continue
        for para in paragraphs(sec):
            if is_furniture(para, fm):
                continue
            marks = MARKER.findall(para)
            if NUMBER.search(unexempt(para)) and not marks:
                unsupported.append(plain_text(para)[:90])
            for m in marks:
                if m.startswith("S") and m not in ids:
                    unknown.append(m)
    if unsupported:
        fail("claims_supported", f"{len(unsupported)} paragraph(s) with a number and no [S#]/[own]/[method] marker, e.g. '{unsupported[0]}'")
    if unknown:
        fail("claims_supported", f"unknown source marker(s): {', '.join(sorted(set(unknown)))}")
    info["marked_paragraphs"] = len(MARKER.findall(body_nocode))

    # original contribution: the front-matter line plus a section of the member's own view, distinct from "How we know"
    orig = fm.get("original", "")
    orig = orig if isinstance(orig, str) else " ".join(orig)
    view_sections = [s for h, s in sections if re.search(r"(what we|our (?:take|view|method|rule|approach|experience)|what (?:we|i)'d|in our|what nobody|"
                                                         r"the mistake|what to check)", h, re.I) and not h.lower().startswith("how we know")]
    if words(orig) < 12 or orig.lstrip().startswith("(") or SENTINEL in orig:
        fail("original_contribution", "front-matter `original` must say, in at least 12 words of the member's own, what this page has that no other page has")
    elif not view_sections or all(words(s) < MIN_ORIGINAL_WORDS for s in view_sections):
        fail("original_contribution", f"no section of at least {MIN_ORIGINAL_WORDS} words carrying the member's own view or rule "
                                      "(a heading like 'What we'd check first', 'Our rule', 'The mistake we see most'); 'How we know' does not count")

    # headings (the Sources section does not count)
    h2s = [h for h, _ in sections if h and not h.lower().startswith("sources")]
    if len(h2s) < 2:
        fail("headings", "fewer than two H2 sections")
    elif not any(h.rstrip().endswith("?") for h in h2s):
        warns.append("no H2 is a question; question-shaped headings are the ones engines quote")
    if any(words(s) > 350 for _, s in sections):
        warns.append("a section runs over 350 words; split it so each heading answers one thing")

    # author, reviewer, dates
    if not fm.get("author") or not fm.get("author_credentials"):
        fail("author", "author and author_credentials are required (who is answering, and why they can)")
    reviewer = fm.get("reviewer", "none") or "none"
    if regulated != "none":
        if reviewer == "none":
            fail("author", f"a {regulated} page needs a named reviewer")
        elif not re.search(r"[A-Z][a-z]+ [A-Z]", reviewer):
            warns.append("the reviewer should be a named person (first and last name), not a team")
    for key in ("published", "updated"):
        if not re.fullmatch(r"20\d\d-\d\d-\d\d", fm.get(key, "") or ""):
            fail("dates", f"{key} must be a date YYYY-MM-DD")
    if "dates" not in fails:
        try:
            pub, upd = date.fromisoformat(fm["published"]), date.fromisoformat(fm["updated"])
            if upd < pub:
                fail("dates", "updated is before published")
            elif (date.today() - upd).days > 365 and fm.get("status") in ("published", "needs-update"):
                warns.append("last updated over a year ago; re-check the facts and bump `updated`")
        except ValueError:
            fail("dates", "a date is not a real calendar date")
    if not re.search(r"(updated|last reviewed|reviewed on)\s*:?\s*20\d\d", body_nocode, re.I):
        warns.append("no visible 'Updated: <date>' line in the body; readers and engines both look for it")

    # next action
    na = fm.get("next_action", "")
    link = na.split("|", 1)[1].strip() if "|" in na else ""
    if not na or not link or not NEXT_LINK.match(link):
        fail("next_action", "next_action must be `label | link` (a page link, mailto:, tel: or sms:)")
    elif link not in body_nocode:
        warns.append("the next-action link does not appear in the body; put it at the end of the page")

    # internal links: relative links or links on the member's domain, anywhere in the body, not counting the sources
    source_urls = {s["url"] for s in sources if s["url"]}
    links = [l for l in INLINE_LINK.findall(body_nocode) if l not in source_urls]
    internal = [l for l in links if l.startswith("/") or (own_domain and own_domain in l)]
    info["internal_links"] = len(internal)
    if site and len(internal) < require_internal:
        fail("internal_links", f"{len(internal)} internal link(s); link to at least {require_internal} other pages on the site (the service or hub page, and the booking or contact page)")
    elif not site and len(internal) < require_internal:
        warns.append(f"{len(internal)} internal link(s) found; pass --site to check them properly; aim for {require_internal} or more")

    # scope note for regulated topics
    detected = [k for k, rx in REGULATED_HINTS.items() if len(re.findall(rx, body_nocode, re.I)) >= 2]
    info["regulated_hints"] = detected
    if regulated != "none" and not SCOPE_PHRASES.search(body_nocode):
        fail("scope_note", f"a {regulated} page needs a visible scope note (general information, not advice; who to talk to)")
    elif regulated == "none" and detected:
        warns.append(f"the text touches {', '.join(detected)} topics more than once; if the page is about one of them set `regulated` and add a scope note")

    # never-say claims and retired lines (exact phrases; a paraphrase is the session's judgment)
    never, retired = load_business_file_lists(business_file)
    low = re.sub(r"\s+", " ", body_nocode.lower())
    hits = [n for n in never + retired if n and n in low]
    if hits:
        fail("never_say", "the page uses a never-say claim or a retired line: " + "; ".join(hits[:3]))
    if business_file is None:
        warns.append("no --business-file given, so §18 never-say claims and §1 retired lines were not checked")

    # typical result beside any results claim (an outcome verb with a number or a client noun), whatever the marker
    bare = []
    for heading, sec in sections:
        if heading.lower().startswith("sources"):
            continue
        for para in paragraphs(sec):
            if is_furniture(para, fm):
                continue
            if OUTCOME.search(para) and (NUMBER.search(unexempt(para)) or CLIENT_NOUNS.search(para)) and MARKER.search(para) and not TYPICAL.search(para):
                bare.append(plain_text(para)[:80])
    if bare:
        fail("typical_result", f"{len(bare)} paragraph(s) make a results claim without saying what is typical, e.g. '{bare[0]}'")

    # placeholders
    ph = set(PLACEHOLDER_WORDS.findall(body_nocode)) | set(PLACEHOLDER_BRACKETS.findall(body_nocode))
    ph |= {s for s in PLACEHOLDER_SCAFFOLD if s.lower() in body_nocode.lower()}
    if SENTINEL in body_nocode or any(SENTINEL in str(v) for v in fm.values()):
        ph.add("‹…› scaffold text")
    if ph:
        fail("no_placeholders", "placeholder text left in: " + ", ".join(sorted(x if isinstance(x, str) else x[0] for x in ph)[:4]))

    # duplicate against the question map
    if questions:
        qp = Path(questions)
        if qp.exists():
            try:
                qs = json.loads(qp.read_text(encoding="utf-8")).get("questions", [])
            except json.JSONDecodeError:
                qs = []
            dup = [q for q in qs if q.get("status") == "published" and q.get("id") != fm.get("id")
                   and (q.get("slug") == fm.get("slug") or norm(q.get("question", "")) == norm(fm.get("question", "")))]
            if dup:
                fail("duplicate", f"already published as {dup[0]['id']} ({dup[0].get('published_url') or dup[0].get('slug')}); update that page instead")
            if fm.get("id") and not any(q.get("id") == fm.get("id") for q in qs):
                warns.append(f"{fm['id']} is not in the question map; add it so the map stays the one list")

    # schema block, if the page carries one
    for lang, block in FENCE.findall(body):
        if lang.lower() in ("json", "jsonld", "json-ld") and '"@type"' in block:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                fail("schema_match", f"the JSON-LD block does not parse: {e}")
                continue
            items = data.get("@graph", [data]) if isinstance(data, dict) else data
            for it in items:
                t = it.get("@type", "")
                if t in ("Article", "BlogPosting", "WebPage") and it.get("headline") and it["headline"] != fm.get("title"):
                    fail("schema_match", "the schema headline differs from the page title")
                if t == "FAQPage":
                    fail("schema_match", "FAQPage markup: FAQ rich results ended in May 2026 and the skill does not use it; remove the block")
                if t in ("Article", "BlogPosting") and isinstance(it.get("author"), dict) and it["author"].get("name") and it["author"]["name"] != fm.get("author"):
                    fail("schema_match", "the schema author differs from the front-matter author")

    # first-hand pages: a "How we know" section
    if kind == "first-hand":
        hk = [s for h, s in sections if h.lower().startswith("how we know")]
        if not hk or words(hk[0]) < 30:
            fail("how_we_know", "a first-hand page needs a 'How we know' section (what was counted, over what period, how many)")
        if "[own]" not in body_nocode:
            warns.append("a first-hand page usually carries [own] markers on the member's own numbers")
    if kind == "service":
        have = " ".join(h.lower() for h in h2s)
        missing_q = [w for w in ("who", "cost", "first") if w not in have]
        if missing_q:
            warns.append("a service page usually answers: what it is, who it is for, what it costs (or how pricing works), what happens first; "
                         f"missing: {', '.join(missing_q)}")

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
original: ‹12 or more words of your own: what this page has that no other page has: your numbers, your rule, your example›
regulated: none
next_action: Book a 20-minute call | /contact
sources:
  - S1 | ‹Title of the source› | ‹Publisher› | https://example.org/page | published 2026-01-15 | accessed {today}
---
# {h1}

**Short answer:** ‹Answer in two or three plain sentences, under 100 words: the number or the decision first, then the one condition that changes it.›

By {author}, {credentials}. Updated: {today}

{sections}
## Sources

- [S1] ‹Title of the source, Publisher, 2026.› https://example.org/page

*Next step:* [Book a 20-minute call](/contact)
"""

SECTIONS_QUESTION = """## ‹A question-shaped heading: what decides the answer?›

‹One thing per heading. A paragraph or list item with a number ends with [S1], [own] or [method].›

## ‹Another question: what does it cost, how long, what goes wrong?›

- ‹A short list or a small table gives engines something to lift.›
{how_we_know}
## What we'd check first

‹At least 40 words of your own view: the rule you use, the mistake you see most, the example from your own work. The part no other page has.›
"""

SECTIONS_SERVICE = """## What is it?

‹Two or three plain sentences: what the service is and what it ends with.›

## Who is it for?

- ‹The person and the situation, in their words from §2.›
- ‹Who it is not for.›

## What does it cost?

‹A real price or range, or how the price is set, with [own]. "Contact us" gives engines nothing to quote.›

## What happens first?

‹The first step, how long it takes, what the client needs to bring.›

## Our rule

‹At least 40 words of your own: the rule you work by, the mistake you see most, one example from a real job.›
"""

HOW_WE_KNOW = """
## How we know

‹First-hand pages: what you counted, over what period, how many clients or jobs, what you did not count. Then the number, with [own].›
"""


def cmd_new(a):
    folder = Path(a.folder)
    (folder / "answers").mkdir(parents=True, exist_ok=True)
    slug = a.slug or slugify(a.question)
    out = folder / "answers" / f"{slug}.md"
    if out.exists() and not a.force:
        die(f"{out} already exists (use --force to overwrite)")
    title = a.title or a.question.rstrip("?")
    if a.kind == "service":
        sections, h1 = SECTIONS_SERVICE, title
    else:
        sections, h1 = SECTIONS_QUESTION.format(how_we_know=HOW_WE_KNOW if a.kind == "first-hand" else ""), a.question
    out.write_text(TEMPLATE.format(qid=a.id or "Q-00", question=a.question, title=title, slug=slug, kind=a.kind, author=a.author,
                                   credentials=a.credentials or "‹credentials: years, qualification, how many clients›",
                                   today=date.today().isoformat(), cluster=a.cluster or "general", h1=h1, sections=sections), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(out), "next": f"replace every ‹…› with your own words, then: answer_check.py check {out}"}, indent=2, ensure_ascii=False))


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
    desc = plain_text(first_answer_paragraph(sections[0][1] if sections else "", fm))
    desc = re.sub(r"^Short answer:\s*", "", desc, flags=re.I)
    if len(desc) > 300:
        cut = desc[:300]
        desc = cut[:cut.rfind(". ") + 1] if ". " in cut else cut
    article = {
        "@type": "Article",
        "@id": url + "#article",
        "headline": fm.get("title", h1),
        "description": desc,
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
    data = {"@context": "https://schema.org", "@graph": graph}
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "wrote": a.out, "types": [g["@type"] for g in graph],
                          "note": "No FAQPage: FAQ rich results ended in May 2026 and structured data does not earn AI citations. "
                                  "Paste into the page's header code field if the builder has one; skip it if not."}, indent=2))
    else:
        print(out)


def parse_robots(text):
    """Return {user_agent_lower: [(rule, path), ...]}; a run of User-agent lines shares the rules that follow."""
    groups, current, open_run = {}, [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = [x.strip() for x in line.split(":", 1)]
        k = key.lower()
        if k == "user-agent":
            if not open_run:
                current = []
                open_run = True
            current.append(val.lower())
            groups.setdefault(val.lower(), [])
        elif k in ("allow", "disallow"):
            open_run = False
            for ua in current or ["*"]:
                groups.setdefault(ua, []).append((k, val))
        else:
            open_run = False
    return groups


def blocked_by(groups, agent):
    rules = groups.get(agent.lower())
    if rules is None:
        rules = groups.get("*", [])
    best = None
    for rule, path in rules:
        if rule == "disallow" and path == "":
            continue
        if path and "/".startswith(path):
            if best is None or len(path) > len(best[1]):
                best = (rule, path)
    return best is not None and best[0] == "disallow"


def cmd_robots(a):
    if a.check:
        src = Path(a.check)
        if not src.exists():
            die(f"{src} not found")
        groups = parse_robots(src.read_text(encoding="utf-8", errors="ignore"))
        blocked = [ua for ua in SEARCH_CRAWLERS + GROUNDING_CRAWLERS if blocked_by(groups, ua)]
        out = {"ok": not blocked, "blocked_search_crawlers": blocked,
               "training_crawlers_blocked": [ua for ua in TRAINING_CRAWLERS if blocked_by(groups, ua)],
               "note": ("These crawlers decide whether the site can be found and cited: turn off the builder's 'block AI bots' switch "
                        "or remove their Disallow lines, then check again." if blocked else "Search and answer crawlers are allowed.")}
        print(json.dumps(out, indent=2))
        sys.exit(0 if out["ok"] else 1)
    lines = ["# Search and answer crawlers: allowed (these decide whether the site can be found and cited)"]
    for ua in SEARCH_CRAWLERS:
        lines += [f"User-agent: {ua}", "Allow: /", ""]
    lines.append("# Google-Extended governs Gemini grounding as well as training; blocking it can stop the Gemini app using the site")
    for ua in GROUNDING_CRAWLERS:
        lines += [f"User-agent: {ua}", "Allow: /", ""]
    lines.append("# Model-training crawlers: a separate brand choice. Allowing them is the default; a business that wants to be known loses nothing.")
    for ua in TRAINING_CRAWLERS:
        lines += [f"User-agent: {ua}", "Disallow: /" if a.block_training else "Allow: /", ""]
    lines += ["User-agent: *", "Allow: /", "", f"Sitemap: {a.site.rstrip('/')}/sitemap.xml" if a.site else "Sitemap: https://YOUR-DOMAIN/sitemap.xml"]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(json.dumps({"ok": True, "wrote": a.out}, indent=2))
    else:
        print(text, end="")


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
    s.add_argument("--org", default=""); s.add_argument("--author-url", default=""); s.add_argument("--out", default=""); s.set_defaults(f=cmd_schema)
    s = sub.add_parser("robots"); s.add_argument("--site", default=""); s.add_argument("--block-training", action="store_true")
    s.add_argument("--out", default=""); s.add_argument("--check", default=""); s.set_defaults(f=cmd_robots)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
