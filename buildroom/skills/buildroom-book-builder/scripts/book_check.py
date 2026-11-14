#!/usr/bin/env python3
"""AI Momentum Labs Book Builder: the checks, and the gate before a manuscript is called ready.

  book_check.py chapter --book B --section "Chapter 3" [--business-file BUILDROOM_BUSINESS_FILE.md]
                        one section, right after it is drafted or edited
  book_check.py check   --book B [--business-file BUILDROOM_BUSINESS_FILE.md] [--out check.md]
                        the whole manuscript and every stage: GO or a FIX list

FIX items block the manuscript; WATCH items are advice. What a script can check is narrow: it reads
text and records. It cannot tell whether a claim is true, a story is the author's, or the book is
good. Those are the fact audit, the independent review and the readers, and the gate checks that
each one happened and that nothing they found is still open.

  FIX   a dash (em, en or a double hyphen; titles and subheads count) · a planned section missing or
        empty · a section in the folder twice, a chapter past the chapter count, or text in no section ·
        placeholder text · hidden control characters · a passage repeated in two sections · a figure that
        is in neither the author's intake, the sources, nor the Business File (percentages and
        "million" figures must match as such; spelled-out statistics count) · a quotation credited to
        a full name that is not in the sources · "studies show" with no source · a named client the
        author did not supply · any client source without documented permission or anonymising · a
        retired line or never-say claim from the Business File · and, for the gate: a stage not done,
        the outline or sample changed after the member approved it, an open P0 or P1 issue, a fix
        nobody verified, a manuscript that changed after the last edition was frozen, an edition
        edited in place, or a regression check that read an older edition than the latest
  WATCH a thin or overlong section · AI-writing tells above their density · chapters that open or
        close the same way · reading level above the book's setting · markdown in the prose · a
        framework name spelled two ways · a section that is not in the plan · readers waived · a memo
        with no issues recorded
Exit 0 on GO (or a clean chapter), 1 on FIX, 2 on a usage error. JSON on stdout.
"""
import argparse, hashlib, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import booklib as bl  # noqa: E402
import issues as iss  # noqa: E402
import manuscript as ms  # noqa: E402

# ---------------------------------------------------------------- AI-writing tells (density, never a verdict)
VOCAB = r"\b(delv(?:e|es|ing|ed)|tapestry|intricac(?:y|ies)|intricate|pivotal|underscor(?:e|es|ed|ing)|foster(?:s|ed|ing)?|" \
        r"testament|crucial|showcas(?:e|es|ed|ing)|leverag(?:e|es|ed|ing)|unlock(?:s|ed|ing)?|revolutioniz(?:e|es|ed|ing)|" \
        r"future-proof|game-?changer|robust|seamless(?:ly)?|holistic|realm|beacon|landscape|journey|transformative|" \
        r"empower(?:s|ed|ing)?|elevate(?:s|d)?|harness(?:es|ed|ing)?|myriad|plethora|multifaceted)\b"
PHRASES = [
    r"in today's (?:fast-paced|digital|modern|ever-changing)", r"in an era of", r"in a world where",
    r"(?:stands|serves) as a testament", r"plays? an? (?:vital|significant|crucial|key|pivotal) role",
    r"underscores? the importance", r"lasting impact", r"it(?:'s| is) (?:important|worth) (?:to note|noting)",
    r"let's (?:dive in|unpack|explore|delve)", r"navigat(?:e|ing) the complexit", r"when it comes to", r"at its core",
    r"at the end of the day", r"here's the (?:thing|kicker|truth)", r"^in (?:conclusion|summary)\b", r"whether you're an? ",
    r"imagine a world", r"picture this", r"more than just an?", r"isn't merely", r"the truth is", r"the reality is",
    r"it's no secret", r"needless to say", r"as we(?:'ll| will) see", r"as (?:mentioned|discussed) earlier",
    r"now that we(?:'ve| have) covered", r"take it to the next level", r"the power of", r"a deep dive",
]
PATTERNS = {
    "it's not X, it's Y": r"\b(?:it|this|that)(?:'s| is|'s) not (?:just |only |about )?[^.?!]{3,60}[.,;] (?:it|this|that)(?:'s| is) ",
    "this isn't about X. It's about Y": r"isn't (?:just |really )?about [^.?!]{3,60}\. It's about",
    "not just X but Y": r"\bnot (?:just|only|merely) [^.?!]{3,80}\bbut(?: also)?\b",
    "the colon reveal": r"\bThe (?:result|answer|truth|problem|solution|secret|catch|lesson|point)\? ",
    "trailing participle": r", (?:highlighting|underscoring|reflecting|ensuring|showcasing|emphasizing|demonstrating|illustrating|"
                           r"creating|making|allowing|enabling|leading to|paving the way)\b",
    "sincerity markers": r"\b(?:truly|genuinely|honestly|incredibly|absolutely|undoubtedly)\b",
    "stacked hedges": r"\b(?:can|may|might|could) (?:often|sometimes|potentially|possibly) (?:potentially|possibly|help|be)\b",
}
TRIPLE = re.compile(r"\b[\w'-]+, [\w'-]+(?: [\w'-]+)?,? and [\w'-]+")
AUTHORITY = re.compile(r"\b(?:(?:studies|research|surveys?|experts?|scientists|science|data|statistics) (?:show|shows|suggest|"
                       r"suggests|agree|indicate|indicates|prove|proves|have shown|has shown|have found|has found|found|"
                       r"confirm|confirms|say|says)|a (?:recent|new|famous|landmark) (?:study|survey) (?:found|shows|showed|"
                       r"suggests)|according to (?:research|studies|experts|scientists|the data|statistics)|"
                       r"research (?:from|by|at) \w+(?: \w+)? (?:found|finds|shows|showed|suggests|proves))\b", re.I)
OWN_EVIDENCE = re.compile(r"\b(?:my|our|my own|our own|the author's)\s+$", re.I)
PLACEHOLDER = re.compile(r"(?i:lorem ipsum)|(?i:\[write:)|\bTODO\b|\bTBD\b|\[[A-Z][A-Z _/'-]{3,}\]|\bXXX+\b|"
                         r"(?i:insert (?:story|example|name|quote|statistic) here)")
MAG = r"(?:k|m|bn|thousand|million|billion)"
NOUNS = (r"(?:clients|students|members|people|customers|businesses|companies|readers|patients|employees|sales|"
         r"subscribers|followers|countries|cities|studies|participants|respondents|years|months|weeks|days|hours|"
         r"pounds|dollars|times|owners|women|men|families|teams)")
NUMBER_RE = re.compile(rf"(?:[$£€]\s?\d[\d,]*(?:\.\d+)?(?:\s?{MAG})?\b|\b\d[\d,]*(?:\.\d+)?\s?(?:%|percent\b)|"
                       rf"\b\d[\d,]*(?:\.\d+)?\s?{MAG}\b(?:\s{NOUNS})?|\b\d[\d,]*\+?\s(?:[a-z-]+\s)?{NOUNS}\b)", re.I)
NUM_WORD = (r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|"
            r"seventy|eighty|ninety|hundred)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?")
SPELLED_STAT = re.compile(rf"\b(?:{NUM_WORD} percent|{NUM_WORD} (?:in|out of)(?: every)? {NUM_WORD}|"
                          r"(?:half|a third|two thirds|two-thirds|a quarter|three quarters|three-quarters) "
                          r"of (?:all |the )?(?:[a-z]+ )?" + NOUNS + r")\b", re.I)
# Everyday figures of speech that are not claims about the world.
IDIOM_NUM = re.compile(r"^(?:100\s?(?:%|percent)|24 hours|7 days|30 days|60 days|90 days|365 days|12 months|52 weeks)$", re.I)
NAME = r"((?:[A-Z][A-Za-zÀ-ÿ'-]+ ){1,3}[A-Z][A-Za-zÀ-ÿ'-]+)"
SAID = (r"(?:said|says|wrote|writes|observed|observes|noted|notes|argued|argues|warned|warns|quipped|put it|puts it|"
        r"reminds us|reminded us|taught|teaches)")
QUOTED = r'"(?P<q>[^"]{12,400})"'
NAMED = NAME.replace("(", "(?P<n>", 1)
QUOTE_ATTR = [re.compile(x) for x in (
    rf'{QUOTED},?\s+(?:once |famously )?{SAID}\s+(?:the\s+)?(?:[a-z]+\s){{0,3}}?{NAMED}',
    rf'{QUOTED},?\s+{NAMED}\s+(?:once |famously )?{SAID}\b',
    rf'(?:[Aa]s|[Aa]ccording to|[Ii]n the words of)\s+{NAMED}(?:\s+(?:once\s+|famously\s+)?{SAID})?,?\s+{QUOTED}',
    rf'{NAMED}\s+(?:once\s+|famously\s+)?{SAID},?\s+{QUOTED}')]
PEOPLE = r"(?i:clients?|customers?|students?|patients?|members?)"
CLIENT_NAME = re.compile(rf"\b{PEOPLE}(?: of mine| I worked with| I coached)?,?\s+(?:like |such as |named |called )?([A-Z][a-z]{{2,}})\b")
# "a roofer named Tom" · "Tessa, a painter I coached"
PERSON_NAMED = re.compile(r"\b(?i:a|an|the|one|my|another) (?:[a-z]+ ){1,2}named ([A-Z][a-z]{2,})\b")
PERSON_COACHED = re.compile(r"\b([A-Z][a-z]{2,}), an? (?:[a-z-]+ ){1,3}I (?:coached|worked with|helped|trained|mentored|advised)\b")
VAGUE_NUM = re.compile(r"\b(?:(?:hundreds|thousands|dozens|millions|scores) of(?: [a-z]+){0,2}|\d+(?:\.\d+)?x\b|"
                       r"(?:a )?(?:quarter of a|half a) (?:million|billion)(?: dollars)?|several (?:national |international )?awards)", re.I)
MARKDOWN = re.compile(r"^(?:#{1,6} |\* |- |\d+\. |> )|\*\*[^*]+\*\*|__[^_]+__", re.M)
STOPNAMES = {"The", "This", "That", "When", "Then", "What", "Chapter", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday", "January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December", "And", "But", "She", "He", "They", "Her", "His", "Who", "Let", "For", "As",
             "Later", "Finally", "Once", "So", "Now", "Yet", "Still", "Today", "Yesterday", "Afterwards", "Eventually",
             "Suddenly", "My", "Our", "Your", "If", "In", "On", "At", "After", "Before", "One", "Years", "Dr", "Mr", "Mrs", "Ms"}


def norm_quote(t):
    return re.sub(r"\s+", " ", bl.plain_quotes(t).lower()).strip(" .,!?;:")


def attributed_names(text, known_norm=None):
    """People a quotation is credited to by full name. A single first name is the author's own dialogue. With
    known_norm (everything the author supplied, normalised), a quotation passes only when its exact wording is
    there: a known name with invented words is still an invented quotation."""
    out = []
    for rx in QUOTE_ATTR:
        for m in rx.finditer(text):
            toks = m.group("n").split()
            while toks and toks[0].strip(".") in STOPNAMES:
                toks = toks[1:]
            if len(toks) < 2:
                continue
            if known_norm is not None and norm_quote(m.group("q")) in known_norm:
                continue
            if " ".join(toks) not in out:
                out.append(" ".join(toks))
    return out


def named_people(text):
    """First names attached to a client, a trade or 'someone I coached'. A stated pseudonym ('a client I'll call
    Ray') is the documented way to anonymise, so it is left to the fact audit."""
    out = set()
    for rx in (CLIENT_NAME, PERSON_NAMED, PERSON_COACHED):
        for m in rx.finditer(text):
            if m.group(1) not in STOPNAMES:
                out.add(m.group(1))
    return out


MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "bn": 1e9, "billion": 1e9}


def supplied_text(known):
    """The author's material with the things that only look like figures taken out: section references,
    dates and the file version."""
    t = re.sub(r"§\s?\d+(?:\s?[-–]\s?\d+)?", " ", known)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", t)
    return "\n".join(line for line in t.splitlines() if "File version" not in line and not line.lstrip().startswith("**Requires"))


def number_sets(known):
    """What the author supplied: bare numbers (for money), (number, magnitude) pairs, percentages, and
    (number, thing) pairs, so '30 minutes' in the intake does not clear '30 clients' in the book."""
    known = supplied_text(known)
    bare = {bl.norm_num(x) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", known)}
    mags = set()
    for n, u in re.findall(rf"(\d[\d,]*(?:\.\d+)?)\s?({MAG})\b", known, re.I):
        n = bl.norm_num(n)
        mags.add((n, MULT[u.lower()]))
        bare.add(f"{float(n) * MULT[u.lower()]:.0f}")
    pct = {bl.norm_num(n) for n in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s?(?:%|percent\b)", known, re.I)}
    things = {(bl.norm_num(n), w.lower()) for n, w in re.findall(rf"\b(\d[\d,]*)\+?\s(?:[a-z-]+\s)?({NOUNS})\b", known, re.I)}
    return {"bare": bare, "mag": mags, "pct": pct, "things": things, "text": norm_quote(known)}


def unsourced_numbers(text, nums):
    out = []
    for hit in sorted({m.group(0).strip() for m in NUMBER_RE.finditer(text)}):
        if IDIOM_NUM.match(hit):
            continue
        n = bl.norm_num(re.match(r"[^\d]*(\d[\d,]*(?:\.\d+)?)", hit).group(1))
        mm = re.search(rf"\d\s?({MAG})\b", hit, re.I)
        if re.search(r"%|percent", hit, re.I):
            ok = n in nums["pct"]
        elif mm:
            mult = MULT[mm.group(1).lower()]
            ok = (n, mult) in nums["mag"] or f"{float(n) * mult:.0f}" in nums["bare"]
        elif hit[0] in "$£€":
            ok = n in nums["bare"]
        elif re.fullmatch(r"(?:19|20)\d\d", n) and "," not in hit.split()[0]:
            ok = True                                  # a year, not a count
        elif re.fullmatch(r"[1-9]|10", n):
            ok = True                                  # small everyday counts
        else:
            ok = (n, hit.split()[-1].lower()) in nums["things"]
        if not ok:
            out.append(hit)
    for rx in (SPELLED_STAT, VAGUE_NUM):
        for m in rx.finditer(text):
            if norm_quote(m.group(0)) not in nums["text"]:
                out.append(m.group(0))
    return sorted(set(out))



STAGE_CMD = {
    "intake": "book_plan.py intake, answer what is missing, then book_plan.py intake-gate --verdict ready",
    "outline": "read plan.md to the member, then book_plan.py approve --what outline --by member",
    "memo": "write edit/memo.md and edit/styleguide.md, then book_plan.py stage --name memo --status done",
    "sample": "show the member edit/sample.md, then book_plan.py approve --what sample --by member",
    "edit": "finish the line edit and edit/changelog.md, then book_plan.py stage --name edit --status done",
    "review": "an independent reader runs P2, then book_plan.py stage --name review --status done --by reviewer --edition <label>",
    "facts": "an independent reader runs P3, then book_plan.py stage --name facts --status done --by reviewer --edition <label>",
    "copyedit": "an independent reader runs P8, then book_plan.py stage --name copyedit --status done --by reviewer --edition <label>",
    "regression": "an independent reader runs P9 on the final edition, then book_plan.py stage --name regression --status done "
                  "--by reviewer --edition <final>"}


def known_text(book, business_file):
    """Everything the author supplied: the intake, readable local sources, and the Business File."""
    parts = []
    ans = bl.read_json(Path(book) / "intake.json", {"answers": {}})["answers"]
    parts += [(v or {}).get("text", "") for v in ans.values()]
    for s in bl.read_json(Path(book) / "sources.json", {"sources": []})["sources"]:
        parts.append(s.get("title", ""))
        ref = s.get("ref") or ""
        for cand in (Path(book) / ref, Path(book) / "sources" / ref, Path(ref)):
            if ref and cand.is_file() and cand.suffix.lower() in (".md", ".txt", ".vtt", ".srt", ".json", ".csv"):
                parts.append(bl.read_text(cand))
                break
    src_dir = Path(book) / "sources"
    if src_dir.is_dir():
        for f in src_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".md", ".txt", ".vtt", ".srt"):
                parts.append(bl.read_text(f))
    if business_file:
        parts.append(bl.read_text(business_file))
    plan = bl.read_json(Path(book) / "plan.json", {})
    author = bl.read_json(Path(book) / "book.json", {}).get("author", "")
    return "\n".join(parts) + "\n" + author + "\n" + str(plan.get("title", ""))


def banned_lines(business_file):
    """Retired lines (§1) and never-say claims (§18) from the Business File. Items are quoted phrases, or
    a list split on ; (or on commas when there is only one line of them), on the same line or on the
    indented bullet lines under it. A leading hint in brackets is not an item."""
    if not business_file:
        return []
    out, kind, bodies = [], None, []

    def flush():
        if kind is None:
            return
        items = []
        for line in bodies:
            parts = re.split(r"[;·|]", line)
            if len(parts) == 1 and len(bodies) == 1:
                quoted = re.findall(r'"([^"]{4,})"', line)
                parts = quoted if len(quoted) > 1 else (line.split(",") if "," in line and '"' not in line else parts)
            for x in parts:
                q = re.search(r'"([^"]{4,})"', x)      # a quoted phrase is the item; a note after it is not
                items.append(q.group(1) if q else re.sub(r"\s*\([^)]*\)\s*$", "", x.strip()).strip('"'))
        for x in items:
            x = re.sub(r"\s+", " ", x).strip(" .-*")
            if len(x) >= 6 and not x.startswith(("[", "(")) and x not in ("—", "none", "None yet"):
                out.append((kind, x))
    for line in bl.plain_quotes(bl.read_text(business_file)).splitlines():
        m = re.search(r"\*\*(Retired lines|Never-say claims)[^*]*\*\*\s*:?\s*(.*)", line, re.I)
        if m:
            flush()
            kind = m.group(1).lower()
            body = re.sub(r"^\([^)]*\)\s*:?\s*", "", m.group(2).strip())
            bodies = [body] if body else []
        elif kind is not None and re.match(r"\s+[-*] \S", line) and "**" not in line:
            bodies.append(re.sub(r"^\s+[-*] ", "", line))
        elif kind is not None:
            flush()
            kind, bodies = None, []
    flush()
    return out


def tells(text):
    """Density of AI-writing tells in one section. Returns (notes, score)."""
    text = bl.plain_quotes(text)
    n = max(1, bl.words(text))
    per_k = lambda c: c * 1000 / n  # noqa: E731
    notes = []
    vocab = re.findall(VOCAB, text, re.I)
    if per_k(len(vocab)) >= 2 and len(vocab) >= 3:
        top = sorted({v.lower() for v in vocab})[:6]
        notes.append(f"stock vocabulary {len(vocab)} times ({', '.join(top)})")
    hits = []
    for pat in PHRASES:
        hits += [m.group(0).lower() for m in re.finditer(pat, text, re.I | re.M)]
    if hits:
        notes.append(f"stock phrases {len(hits)} ({'; '.join(sorted(set(hits))[:5])})")
    for name, pat in PATTERNS.items():
        c = len(re.findall(pat, text))
        limit = 3 if name in ("sincerity markers", "trailing participle") else 1.2
        if c >= 2 and per_k(c) >= limit:
            notes.append(f"'{name}' {c} times")
    t = len(TRIPLE.findall(text))
    if t >= 4 and n / t < 300:
        notes.append(f"three-item lists {t} times (about one every {n // t} words)")
    paras = [p for p in re.split(r"\n\s*\n", text) if bl.words(p) >= 30]
    if len(paras) >= 8:
        short = sum(1 for p in paras if bl.words(bl.sentences(p)[-1]) <= 8)
        if short / len(paras) >= 0.5:
            notes.append(f"{short} of {len(paras)} paragraphs end on a short punchy line")
        lens = [len(bl.sentences(p)) for p in paras]
        mean = sum(lens) / len(lens)
        var = sum((x - mean) ** 2 for x in lens) / len(lens)
        if mean >= 2 and var < 0.6:
            notes.append("paragraphs are all about the same length")
    q = len(re.findall(r"\?\s+(?:The answer|It's|It is|Because|Simple|Yes|No)[\s,.:]", text))
    if q >= 3 and per_k(q) >= 1:
        notes.append(f"a question answered at once {q} times")
    return notes


def check_section(sec, known, known_nums, banned, grade_max, target):
    items = []

    def add(level, cid, msg, fix=""):
        items.append({"level": level, "id": cid, "section": sec["title"], "message": msg, "fix": fix})
    text = bl.plain_quotes("\n\n".join(p for p in sec["paras"] if not bl.is_subhead(p)))
    heads = bl.plain_quotes("\n".join([sec["title"]] + [p[3:] for p in sec["paras"] if bl.is_subhead(p)]))
    n = bl.words(text)
    if n == 0:
        add("FIX", "empty", "the section has no text", "write it, or take it out of the plan")
        return items, n
    d = bl.dash_count(text) + bl.dash_count(heads)
    if d:
        add("FIX", "dashes", f"{d} dash(es): an em or en dash, or a double hyphen used as one (titles and subheads count)",
            "use a period, a comma or a colon")
    if bl.CONTROL.search(text + heads):
        add("FIX", "control_characters", "hidden control characters (often a soft line break pasted from Word)",
            "retype the line; they break the Word export")
    ph = sorted({m.group(0) for m in PLACEHOLDER.finditer(text + "\n" + heads)})
    if ph:
        add("FIX", "placeholders", "placeholder text: " + ", ".join(ph[:5]), "write it from the author's material, or ask the author")
    unknown = unsourced_numbers(text, known_nums)
    if unknown:
        add("FIX", "unsourced_numbers", "figures the author did not give: " + ", ".join(unknown[:8])
            + (f" (+{len(unknown) - 8} more)" if len(unknown) > 8 else ""),
            "take them out, or add the source to the intake or the source packet first")
    names = attributed_names(text, known_nums["text"])
    if names:
        add("FIX", "unsourced_quotes", "quotations attributed to people who are not in the author's sources: "
            + ", ".join(sorted(set(names))[:6]), "put the exact wording and where it comes from in the source packet, or cut "
            "the quotation; a real name with words the author cannot source is still an invented quotation")
    auth = sorted({m.group(0).lower() for m in AUTHORITY.finditer(text) if not OWN_EVIDENCE.search(text[max(0, m.start() - 14):m.start()])})
    if auth:
        add("FIX", "unattributed_authority", "claims leaning on unnamed evidence: " + ", ".join(auth[:5]),
            "name the study or source from the source packet, or say it as the author's own view")
    cl = sorted(x for x in named_people(text) if not re.search(r"\b" + re.escape(x) + r"\b", known))
    if cl:
        add("FIX", "invented_client", "named clients the author did not supply: " + ", ".join(cl[:6]),
            "use only people from the author's own material; add the story to the intake or the sources first, or "
            "say plainly that the name is changed (\"a client I'll call Ray\")")
    low = text.lower()
    for kind, line in banned:
        if re.sub(r"\s+", " ", line.lower()) in re.sub(r"\s+", " ", low):
            add("FIX", "banned_line", f"{kind} in the Business File: \"{line[:70]}\"", "take it out")
    if MARKDOWN.search(text):
        add("WATCH", "markdown", "markdown marks in the prose", "plain prose; a subhead is a line starting '@@ '")
    if target:
        if n < target * ms.THIN:
            add("WATCH", "thin", f"{n:,} words against a target of about {target:,}",
                "ask the author for the missing story, example or step; do not pad")
        elif n > target * 1.6:
            add("WATCH", "long", f"{n:,} words against a target of about {target:,}", "cut repetition, or split the chapter")
    g = bl.reading_grade(text)
    if g is not None and grade_max and g > grade_max:
        add("WATCH", "reading_level", f"reading grade {g} (the book is set to {grade_max:g} or below)",
            "shorter sentences and plainer words")
    t = tells(text)
    if t:
        add("WATCH", "ai_tells", "; ".join(t), "rewrite in the author's own words (voice.md); these are densities, not a verdict")
    return items, n


def duplicates(secs):
    out, seen = [], {}
    for sid, s in enumerate(secs):
        for i, p in enumerate(s["paras"], 1):
            if bl.words(p) < 40:
                continue
            sh = bl.shingles(p)
            for (ot, otitle, oi), osh in seen.items():
                if ot != sid and sh and len(sh & osh) / len(sh) >= 0.5:
                    out.append(f"{bl.section_code(s['title'])}-P{i:03d} repeats {bl.section_code(otitle)}-P{oi:03d}")
                    break
            seen[(sid, s["title"], i)] = sh
    return out


def openings(secs):
    notes = []
    chs = [s for s in secs if s["title"].lower().startswith("chapter") and s["paras"]]
    if len(chs) < 3:
        return notes
    first = [next((p for p in s["paras"] if not bl.is_subhead(p)), "") for s in chs]
    last = [next((p for p in reversed(s["paras"]) if not bl.is_subhead(p)), "") for s in chs]
    for label, paras in (("open", first), ("close", last)):
        keys = {}
        for s, p in zip(chs, paras):
            k = " ".join(re.findall(r"[a-z']+", p.lower())[:3])
            keys.setdefault(k, []).append(bl.section_key(s["title"]))
        for k, where in keys.items():
            if k and len(where) >= 3:
                notes.append(f"{len(where)} chapters {label} with \"{k} …\" ({', '.join(where[:5])})")
    qs = [bl.section_key(s["title"]) for s, p in zip(chs, first) if bl.sentences(p) and bl.sentences(p)[0].endswith("?")]
    if len(qs) >= max(3, len(chs) // 2 + 1):
        notes.append(f"{len(qs)} of {len(chs)} chapters open with a question")
    im = [bl.section_key(s["title"]) for s, p in zip(chs, first) if re.match(r"(imagine|picture)\b", p, re.I)]
    if len(im) >= 3:
        notes.append(f"{len(im)} chapters open with \"Imagine\" or \"Picture\"")
    return notes


def run(a, only=None):
    data = bl.load_book(a.book)
    if a.business_file and not Path(a.business_file).is_file():
        return {"ok": False, "error": f"file not found: {a.business_file}"}, 2
    if not a.business_file:
        for cand in (Path("BUILDROOM_BUSINESS_FILE.md"), Path(a.book).resolve().parents[1] / "BUILDROOM_BUSINESS_FILE.md"):
            if cand.is_file():
                a.business_file = str(cand)
                break
    known = known_text(a.book, a.business_file)
    known_nums = number_sets(known)
    banned = banned_lines(a.business_file)
    t = bl.targets(data)
    secs = bl.read_manuscript(a.book)
    items = []
    if only:
        secs_to_check = [s for s in secs if bl.section_key(s["title"]).lower() == bl.section_key(only).lower()]
        if not secs_to_check:
            return {"ok": False, "error": f"no section '{only}' in manuscript/"}, 2
    else:
        secs_to_check = secs
    counts = {}
    for s in secs_to_check:
        it, n = check_section(s, known, known_nums, banned, data["settings"].get("grade_max"), t.get(bl.section_key(s["title"])))
        items += it
        counts[s["title"]] = n

    def add(level, cid, msg, fix=""):
        items.append({"level": level, "id": cid, "section": "", "message": msg, "fix": fix})
    if not only:
        st = ms.status(data, a.book)
        for sec in st["missing"]:
            if sec != "Title Page":
                add("FIX", "missing_section", f"{sec} is missing or empty", "write it, or change the chapter count")
        for dup in duplicates(secs)[:10]:
            add("FIX", "repeated_passage", dup, "tell it once; a one-line callback is fine")
        for note in openings(secs):
            add("WATCH", "same_shape", note, "vary how chapters open and close")
        rec = bl.read_json(Path(a.book) / "record.json", {"entries": []})["entries"]
        full = "\n".join("\n".join(s["paras"]) for s in secs)
        for e in rec:
            if e["kind"] in ("framework", "term") and len(e["text"]) >= 4:
                toks = [re.escape(x) for x in re.split(r"[\s-]+", e["text"].strip()) if x]
                body = full
                for o in rec:
                    if o is not e and o["kind"] in ("framework", "term") and len(o["text"]) > len(e["text"]) \
                            and e["text"].lower() in o["text"].lower():
                        body = re.sub(re.escape(o["text"]), " ", body, flags=re.I)
                found = set(re.findall(r"(?<![\w-])" + r"[\s-]+".join(toks) + r"(?![\w-])", body, re.I))
                forms = {f for f in found if f != f.lower()} if e["text"] != e["text"].lower() else found
                if not found:
                    forms = set()
                if len(forms) > 1:
                    add("WATCH", "inconsistent_name", f"\"{e['text']}\" is written {len(forms)} ways: {', '.join(sorted(forms)[:4])}",
                        "one spelling and capitalisation, as the author gave it")
                elif not found:
                    add("WATCH", "unused_name", f"\"{e['text']}\" is in the book record but never appears", "")
        plan = bl.read_json(Path(a.book) / "plan.json", {"chapters": []})
        srcs = {s["id"]: s for s in bl.read_json(Path(a.book) / "sources.json", {"sources": []})["sources"]}
        used = {sid for c in plan.get("chapters") or [] if isinstance(c, dict) for sid in c.get("sources") or []}
        for sid, s in sorted(srcs.items()):
            if s.get("kind") == "client" and not str(s.get("permission", "")).lower().startswith(("documented", "anonymised", "anonymized")):
                add("FIX", "permission", f"{sid} ({s.get('title', '')}) is a client story with no documented permission"
                    + ("" if sid in used else " (not in the plan, but it is in the source packet)"),
                    "get the client's permission in writing and record it (permission 'documented: …'), anonymise the story "
                    "so they cannot be recognised ('anonymised: …'), or take the source out")
        for cid, msg in bl.manuscript_problems(a.book, int(data["settings"]["chapters"])):
            add("FIX", cid, msg, "one file per section, each starting with its '=== SECTION: Title ===' line; move old "
                "drafts out of manuscript/")
        for extra in st["unplanned"]:
            if not bl.CHAPTER_RE.match(extra):
                add("WATCH", "unplanned_section", f"\"{extra}\" is in the manuscript but not in the plan",
                    "fine for a foreword, dedication or appendix; otherwise take it out of manuscript/")
        for what, fname, label in (("outline", "plan.json", "the outline"), ("sample", "edit/sample.md", "the sample chapter edit")):
            stg = bl.stage(data, what)
            f = Path(a.book) / fname
            if stg.get("status") == "approved" and stg.get("sha256") and (not f.is_file() or bl.file_sha(f) != stg["sha256"]):
                add("FIX", "changed_since_approval", f"{label} changed after the member approved it",
                    f"show the member the change and approve again (book_plan.py approve --what {what} --by member)")
        # ---- the stages
        need = [("intake", ("ready",), "the intake gate has not said READY"),
                ("outline", ("approved",), "the member has not approved the outline"),
                ("memo", ("done",), "no developmental memo and style guide"),
                ("sample", ("approved",), "the member has not approved the sample chapter edit"),
                ("edit", ("done",), "the line edit of every section is not done"),
                ("review", ("done",), "no independent developmental review"),
                ("facts", ("done",), "no source, fact and permission audit"),
                ("copyedit", ("done",), "no independent consistency and copyedit pass"),
                ("regression", ("done",), "no regression check of the revisions")]
        for name, okv, msg in need:
            if bl.stage(data, name).get("status") not in okv:
                add("FIX", "stage_" + name, msg, STAGE_CMD[name])
        rs = bl.stage(data, "readers").get("status")
        if rs == "waived":
            add("WATCH", "readers_waived", f"the member went ahead with {bl.stage(data, 'readers').get('humans', 0)} real "
                "test reader(s), fewer than the round needs",
                "simulated readers are a diagnosis, not evidence; real readers are still worth recruiting")
        elif rs != "passed":
            add("FIX", "stage_readers", "the reader round has not passed (or been waived by the member)",
                "reader_panel.py consolidate; fix what readers found; run a second round on the weak sections")
        reg = iss.summary(bl.read_json(iss.path(a.book), {"issues": []}))
        if not a.business_file:
            add("WATCH", "no_business_file", "no Business File was found, so retired lines and never-say claims were not checked",
                "run again with --business-file BUILDROOM_BUSINESS_FILE.md")
        for b in reg["blocking"]:
            add("FIX", "open_issue", b, "fix it in the manuscript, freeze an edition, issues.py resolve, then verify")
        if reg["unverified"]:
            add("FIX", "unverified_fixes", "fixed, waiting for the regression check to confirm: " + ", ".join(reg["unverified"][:12]),
                "the independent regression check (P9) confirms each one: issues.py verify --id … --result … --edition <final>")
        open_low = sum(v for k, v in reg["open"].items() if k in ("P2", "P3"))
        if open_low:
            add("WATCH", "open_minor", f"{open_low} open P2 or P3 issue(s)", "fix them, or the member accepts each with a reason")
        if bl.stage(data, "memo").get("status") == "done" and not reg["by_source"].get("memo"):
            add("WATCH", "memo_no_issues", "the memo is done but none of its changes is in the issue register",
                "a memo that names a problem is not a fix: add its three changes as issues")
        eds = data.get("editions") or []
        cur = hashlib.sha256(ms.assemble(secs).encode()).hexdigest() if secs else ""
        if not eds:
            add("FIX", "no_edition", "no edition has been frozen", "manuscript.py edition --label final")
        elif eds[-1]["sha256"] != cur:
            add("FIX", "changed_since_edition", f"the manuscript changed after edition {eds[-1]['label']} was frozen",
                "freeze the final edition, then run the regression check and this gate on it")
        else:
            ed_file = Path(a.book) / "editions" / eds[-1]["label"] / "manuscript.md"
            if not ed_file.is_file() or hashlib.sha256(bl.read_text(ed_file).encode()).hexdigest() != eds[-1]["sha256"]:
                add("FIX", "edition_altered", f"the frozen edition {eds[-1]['label']} is missing or was edited after it was frozen",
                    "an edition is never edited; freeze a new one from manuscript/")
            reg_ed = bl.stage(data, "regression").get("edition") or ""
            reg_ed = bl.slugify(reg_ed) if reg_ed else ""
            if bl.stage(data, "regression").get("status") == "done" and reg_ed != eds[-1]["label"]:
                add("FIX", "regression_edition", f"the regression check read edition {reg_ed or '(none named)'}, not the latest "
                    f"one ({eds[-1]['label']}); text changed since has not been checked",
                    "run the regression check on the latest edition (book_plan.py stage --name regression --status done "
                    f"--by reviewer --edition {eds[-1]['label']})")
            for name in ("review", "facts", "copyedit"):
                e2 = bl.stage(data, name).get("edition") or ""
                if e2 and bl.slugify(e2) not in [e["label"] for e in eds]:
                    add("WATCH", "stage_edition", f"the {name} names edition {e2}, which does not exist", "")
    fixes = [i for i in items if i["level"] == "FIX"]
    verdict = "GO" if not fixes else "FIX"
    out = {"ok": verdict == "GO", "verdict": verdict if not only else ("CLEAN" if not fixes else "FIX"),
           "scope": only or "whole manuscript", "fix": len(fixes), "watch": len(items) - len(fixes),
           "words": counts if only else sum(counts.values()), "items": items, "checked": bl.today(),
           "business_file": a.business_file or "", "banned_lines_checked": [x for _, x in banned],
           "limits": "a script reads text and records; it cannot judge truth, the author's voice or whether the book is good"}
    if not only:
        bl.set_stage(data, "gate", "go" if verdict == "GO" else "fix", fix=len(fixes),
                     edition=(data.get("editions") or [{}])[-1].get("label", ""))
        bl.save_book(a.book, data)
        dest = Path(a.out) if a.out else Path(a.book) / "check.md"
        md = [f"# Manuscript check", "", f"**{verdict}** · {bl.today()} · {sum(counts.values()):,} words measured"
              + (f" · edition {data['editions'][-1]['label']}" if data.get("editions") else ""), ""]
        for lvl in ("FIX", "WATCH"):
            rows = [i for i in items if i["level"] == lvl]
            if rows:
                md += [f"## {lvl} ({len(rows)})", ""]
                md += [f"- **{i['id']}**" + (f" ({i['section']})" if i["section"] else "") + f": {i['message']}"
                       + (f". Fix: {i['fix']}" if i["fix"] else "") for i in rows]
                md.append("")
        md.append("This check reads text and records. Truth, voice and quality are judged by the fact audit, the review and the readers.")
        bl.write_atomic(dest, "\n".join(md) + "\n")
        out["report"] = str(dest)
    return out, 0 if not fixes else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("chapter"); c.add_argument("--book"); c.add_argument("--section", required=True)
    c.add_argument("--business-file")
    c = sub.add_parser("check"); c.add_argument("--book"); c.add_argument("--business-file"); c.add_argument("--out")
    a = ap.parse_args()
    a.book = bl.find_book(a.book)
    out, code = run(a, only=a.section if a.cmd == "chapter" else None)
    bl.emit(out, code)


if __name__ == "__main__":
    main()
