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
                       r"suggests)|according to (?:research|studies|experts|scientists|the data|statistics))\b", re.I)
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
                          r"(?:half|a third|two thirds|two-thirds|a quarter|three quarters|three-quarters|most|the majority) "
                          r"of (?:all |the )?(?:[a-z]+ )?" + NOUNS + r")\b", re.I)
# Everyday figures of speech that are not claims about the world.
IDIOM_NUM = re.compile(r"^(?:100\s?(?:%|percent)|24 hours|7 days|30 days|60 days|90 days|365 days|12 months|52 weeks)$", re.I)
NAME = r"((?:[A-Z][A-Za-zÀ-ÿ'-]+ ){1,3}[A-Z][A-Za-zÀ-ÿ'-]+)"
SAID = (r"(?:said|says|wrote|writes|observed|observes|noted|notes|argued|argues|warned|warns|quipped|put it|puts it|"
        r"reminds us|reminded us|taught|teaches)")
QUOTE_ATTR = re.compile(
    rf'(?:"[^"]{{12,400}}",?\s+(?:once |famously )?{SAID}\s+(?:the\s+)?(?:[a-z]+\s){{0,3}}?{NAME}|'
    rf'"[^"]{{12,400}}",?\s+{NAME}\s+(?:once |famously )?{SAID}\b|'
    rf'(?:[Aa]s|[Aa]ccording to)\s+{NAME}(?:\s+(?:once\s+|famously\s+)?{SAID})?,?\s+"|'
    rf'{NAME}\s+(?:once\s+|famously\s+)?{SAID},?\s+")')
CLIENT_NAME = re.compile(r"\b(?i:clients?|customers?|students?|patients?|members?)(?: of mine| I worked with| I coached)?,?\s+"
                         r"(?:like |such as |named |called |I'll call |we'll call )?([A-Z][a-z]{2,})\b")
MARKDOWN = re.compile(r"^(?:#{1,6} |\* |- |\d+\. |> )|\*\*[^*]+\*\*|__[^_]+__", re.M)
STOPNAMES = {"The", "This", "That", "When", "Then", "What", "Chapter", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday", "January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December", "And", "But", "She", "He", "They", "Her", "His", "Who", "Let", "For", "As",
             "Later", "Finally", "Once", "So", "Now", "Yet", "Still", "Today", "Yesterday", "Afterwards", "Eventually",
             "Suddenly", "My", "Our", "Your", "If", "In", "On", "At", "After", "Before", "One", "Years", "Dr", "Mr", "Mrs", "Ms"}


def attributed_names(text):
    """People a quotation is credited to. A single first name is the author's own dialogue; a full name is a claim."""
    out = []
    for m in QUOTE_ATTR.finditer(text):
        toks = next((g for g in m.groups() if g), "").split()
        while toks and toks[0].strip(".") in STOPNAMES:
            toks = toks[1:]
        if len(toks) >= 2:
            out.append(" ".join(toks))
    return out


def number_sets(known):
    """What the author supplied, as three sets: bare numbers, (number, magnitude) pairs and percentages."""
    mag = {"k": "thousand", "m": "million", "bn": "billion"}
    bare = {bl.norm_num(x) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", known)}
    mags = {(bl.norm_num(n), mag.get(u.lower(), u.lower())) for n, u in re.findall(rf"(\d[\d,]*(?:\.\d+)?)\s?({MAG})\b", known, re.I)}
    pct = {bl.norm_num(n) for n in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s?(?:%|percent\b)", known, re.I)}
    return {"bare": bare, "mag": mags, "pct": pct, "text": bl.plain_quotes(known).lower()}


def unsourced_numbers(text, nums):
    mag = {"k": "thousand", "m": "million", "bn": "billion"}
    out = []
    for hit in sorted({m.group(0).strip() for m in NUMBER_RE.finditer(text)}):
        if IDIOM_NUM.match(hit):
            continue
        n = bl.norm_num(re.match(r"[^\d]*(\d[\d,]*(?:\.\d+)?)", hit).group(1))
        mm = re.search(rf"\d\s?({MAG})\b", hit, re.I)
        money = hit[0] in "$£€"
        if re.search(r"%|percent", hit, re.I):
            ok = n in nums["pct"]
        elif mm:
            ok = (n, mag.get(mm.group(1).lower(), mm.group(1).lower())) in nums["mag"]
        elif money:
            ok = n in nums["bare"]
        elif re.fullmatch(r"(?:19|20)\d\d", n) and "," not in hit.split()[0]:
            ok = True                                  # a year, not a count
        else:
            ok = n in nums["bare"] or re.fullmatch(r"[1-9]|10", n) is not None
        if not ok:
            out.append(hit)
    for m in SPELLED_STAT.finditer(text):
        if m.group(0).lower() not in nums["text"]:
            out.append(m.group(0))
    return sorted(set(out))



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
            quoted = re.findall(r'"([^"]{4,})"', line)
            items += quoted or re.split(r"[;·|]", line)
        if len(bodies) == 1 and len(items) == 1 and "," in items[0] and '"' not in bodies[0]:
            items = items[0].split(",")
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
        add("FIX", "unsourced_numbers", "numbers the author did not give: " + ", ".join(unknown[:8]),
            "take them out, or add the source to the intake or the source packet first")
    names = [x for x in attributed_names(text) if x.lower() not in known_nums["text"]]
    if names:
        add("FIX", "unsourced_quotes", "quotations attributed to people who are not in the author's sources: "
            + ", ".join(sorted(set(names))[:6]), "add the source (with the exact wording) or cut the quotation")
    auth = sorted({m.group(0).lower() for m in AUTHORITY.finditer(text) if not OWN_EVIDENCE.search(text[max(0, m.start() - 14):m.start()])})
    if auth:
        add("FIX", "unattributed_authority", "claims leaning on unnamed evidence: " + ", ".join(auth[:5]),
            "name the study or source from the source packet, or say it as the author's own view")
    cl = sorted({m.group(1) for m in CLIENT_NAME.finditer(text) if m.group(1) not in STOPNAMES
                 and not re.search(r"\b" + re.escape(m.group(1)) + r"\b", known)})
    if cl:
        add("FIX", "invented_client", "named clients the author did not supply: " + ", ".join(cl[:6]),
            "use only the author's own stories; never invent a person")
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
                forms = set(re.findall(r"(?<![\w-])" + r"[\s-]+".join(toks) + r"(?![\w-])", full, re.I))
                if len(forms) > 1:
                    add("WATCH", "inconsistent_name", f"\"{e['text']}\" is written {len(forms)} ways: {', '.join(sorted(forms)[:4])}",
                        "one spelling and capitalisation, as the author gave it")
                elif not forms:
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
                add("FIX", "stage_" + name, msg, "see the Session Flow for this stage")
        rs = bl.stage(data, "readers").get("status")
        if rs == "waived":
            add("WATCH", "readers_waived", f"the member went ahead with {bl.stage(data, 'readers').get('humans', 0)} real "
                "test reader(s), fewer than the round needs",
                "simulated readers are a diagnosis, not evidence; real readers are still worth recruiting")
        elif rs != "passed":
            add("FIX", "stage_readers", "the reader round has not passed (or been waived by the member)",
                "reader_panel.py consolidate; fix what readers found; run a second round on the weak sections")
        reg = iss.summary(bl.read_json(iss.path(a.book), {"issues": []}))
        for b in reg["blocking"]:
            add("FIX", "open_issue", b, "fix it in the manuscript, freeze an edition, verify")
        if reg["unverified"]:
            add("FIX", "unverified_fixes", "fixed but not verified: " + ", ".join(reg["unverified"][:12]),
                "the regression check confirms each one (issues.py verify)")
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
            reg_ed = bl.slugify(bl.stage(data, "regression").get("edition") or "")
            if bl.stage(data, "regression").get("status") == "done" and reg_ed != eds[-1]["label"]:
                add("FIX", "regression_edition", f"the regression check read edition {reg_ed or '(none named)'}, not the latest "
                    f"one ({eds[-1]['label']}); text changed since has not been checked",
                    "run the regression check on the latest edition (book_plan.py stage --name regression --status done "
                    f"--by reviewer --edition {eds[-1]['label']})")
            for name in ("review", "facts", "copyedit"):
                e2 = bl.slugify(bl.stage(data, name).get("edition") or "")
                if e2 and e2 not in [e["label"] for e in eds]:
                    add("WATCH", "stage_edition", f"the {name} names edition {e2}, which does not exist", "")
    fixes = [i for i in items if i["level"] == "FIX"]
    verdict = "GO" if not fixes else "FIX"
    out = {"ok": verdict == "GO", "verdict": verdict if not only else ("CLEAN" if not fixes else "FIX"),
           "scope": only or "whole manuscript", "fix": len(fixes), "watch": len(items) - len(fixes),
           "words": counts if only else sum(counts.values()), "items": items, "checked": bl.today(),
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
    c = sub.add_parser("chapter"); c.add_argument("--book", required=True); c.add_argument("--section", required=True)
    c.add_argument("--business-file")
    c = sub.add_parser("check"); c.add_argument("--book", required=True); c.add_argument("--business-file"); c.add_argument("--out")
    a = ap.parse_args()
    out, code = run(a, only=a.section if a.cmd == "chapter" else None)
    bl.emit(out, code)


if __name__ == "__main__":
    main()
