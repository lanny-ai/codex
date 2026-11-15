#!/usr/bin/env python3
"""Shared helpers for the Speaking Engine scripts: the speaking folder, safe reads and writes, dates,
and the text checks (figures, claims, banned lines). Standard library only. Not run directly.
"""
import json, os, re, sys, tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

SCHEMA = "buildroom-speaking/1"

# The intake: the seventeen questions, in the order they are asked. (key, question, helper)
QUESTIONS = [
    ("expertise", "What is your area of expertise?", "The thing people already come to you for. Say it the way you would to a neighbour."),
    ("audience", "Who is your ideal audience?", "The people who become your clients. Their work, their stage of life, what they are stuck on."),
    ("experience", "How much speaking have you done?", "Beginner, some, or a lot. A toast, a class, a church talk and a team meeting all count."),
    ("goal", "What do you most want from speaking?", "Clients, visibility, authority, a fee, or to share what you know. Pick the first one."),
    ("reach", "Local, national or international?", "Where you are willing to speak. Local first is the fastest start."),
    ("formats", "Which formats are you comfortable with?", "Talk, workshop, panel, webinar for someone else's audience, podcast guest, Q&A."),
    ("credentials", "What certifications, results or recognition do you have?", "Only what is true and you could show. Years in the work count."),
    ("hosts", "What kind of hosts do you want?", "Local groups, associations, conferences, companies, schools, non-profits, podcasts, online summits."),
    ("paid", "Paid, unpaid, or both?", "Unpaid stages in front of your buyers often bring more than a fee. Say what you need."),
    ("size", "What size of room suits you?", "Up to 50, 50 to 200, or more than 200."),
    ("regions", "Which regions or cities should we look in?", "Towns you can drive to, plus anywhere you travel anyway."),
    ("mode", "Virtual, in person, or both?", ""),
    ("platforms", "Where are you active online?", "LinkedIn, Facebook, YouTube, a newsletter. Hosts look."),
    ("topics", "What would you speak about?", "One to three talks. If you are not sure, say 'need help with topics'."),
    ("history", "Where have you spoken before?", "Industries, groups, events. 'Nowhere yet' is a fine answer."),
    ("targets", "Is there a specific event or group you want to get into?", "Name it, or say no."),
    ("availability", "When can you speak, and when can't you?", "Days, months, travel limits, health or family limits. All of it is private."),
]
QUESTION_KEYS = [q[0] for q in QUESTIONS]
CORE = ("expertise", "audience", "goal", "topics")
# Which Business File sections usually answer a question already.
FROM_FILE = {"expertise": "§1 / §3", "audience": "§2", "credentials": "§18 proof vault / §17", "goal": "§1 goals / §6",
             "platforms": "§14", "topics": "§3 / §4", "regions": "§1"}

KINDS = ("local", "association", "conference", "corporate", "podcast", "summit", "webinar", "other")
# Order matters: a stage only ever moves forward, except to dropped or declined.
STATUSES = ("found", "vetted", "pitched", "replied", "booked", "delivered", "followed_up", "declined", "dropped")
RED_FLAGS = {
    "pay_to_speak": "the speaker is asked to pay to speak, sponsor, or buy a package",
    "fee_to_apply": "there is a fee to apply or to be 'considered'",
    "selected_out_of_nowhere": "an unasked-for message says the member was 'selected' or 'nominated'",
    "award_for_sale": "an award, a 'top speaker' list or a feature that costs money",
    "no_past_events": "no sign the event has run before: no past agenda, photos, speakers or venue",
    "audience_unclear": "nobody will say who attends or how many",
    "pressure": "a decision is demanded in days, with a discount for deciding now",
    "ticket_quota": "the speaker must sell tickets or bring a set number of guests",
    "rights_grab": "the terms take all rights to the talk or the recording with nothing in return",
    "contact_unverifiable": "the organiser cannot be found anywhere but in their own message",
}


# ---------------------------------------------------------------- output and files
def emit(obj, code=0):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    sys.exit(code)


def refuse(msg, **extra):
    emit({"ok": False, "error": msg, **extra}, 1)


def read_text(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def read_json(path, default=None):
    """A JSON file holding an object. Keys the default has and the file lacks are filled in, so a
    hand-edited or half-written file refuses cleanly instead of crashing."""
    p = Path(path)
    if not p.exists():
        if default is not None:
            return json.loads(json.dumps(default))
        refuse(f"file not found: {p}")
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        refuse(f"{p.name} is not valid JSON: {e}")
    if not isinstance(d, dict):
        refuse(f"{p.name} should hold a JSON object; it holds something else")
    for k, v in (default or {}).items():
        if k not in d or (isinstance(v, (list, dict)) and not isinstance(d[k], type(v))):
            d[k] = json.loads(json.dumps(v))
    return d


def write_atomic(path, text):
    p = Path(path)
    if p.is_symlink() or (p.exists() and not p.is_file()):
        refuse(f"{p} is not an ordinary file, so it will not be replaced; choose another path")
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = (p.stat().st_mode & 0o777) if p.exists() else 0o644
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=p.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def write_json(path, data):
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def arg_text(text, text_file, what="--text"):
    """Words from the command line or, better, from a file: inside double quotes the shell eats
    dollar amounts ($2,500 becomes ,500)."""
    if text_file:
        f = Path(text_file)
        if not f.is_file():
            refuse(f"file not found: {text_file}")
        return read_text(f).strip()
    return (text or "").strip()


def eaten_dollars(text):
    return re.findall(r"(?<![\d$£€])[,]\d{3}\b", text)


def plain(text):
    """Curly quotes and apostrophes as straight ones, for matching."""
    return text.translate({0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"'})


def words(text):
    return len(re.findall(r"[^\W_][\w'’-]*", text))


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


# ---------------------------------------------------------------- dates
def today():
    return date.today()


def parse_date(s, what="date"):
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        refuse(f"{what} must be YYYY-MM-DD, not '{s}'")


def day(a):
    """The --today override (for tests and for logging something after the fact), or the real date."""
    return parse_date(a.today, "--today") if getattr(a, "today", None) else today()


# ---------------------------------------------------------------- the folder
def folder(a):
    """The speaking folder: --folder, or ./speaking beside the Business File."""
    return Path(getattr(a, "folder", None) or "speaking")


def load(a, create=False):
    f = folder(a)
    p = f / "pipeline.json"
    if not p.exists() and not create:
        refuse(f"no speaking folder at {f}; run: speak_pipeline.py init")
    return read_json(p, {"schema": SCHEMA, "created": str(today()), "profile": {}, "profile_ready": None,
                         "talks": [], "stages": [], "last_id": 0})


def save(a, data):
    data["updated"] = str(today())
    write_json(folder(a) / "pipeline.json", data)


def find_stage(data, sid):
    for s in data["stages"]:
        if str(s.get("id", "")).lower() == str(sid).lower():
            return s
    refuse(f"no stage {sid}; speak_pipeline.py list")


# ---------------------------------------------------------------- what the member supplied
def proof_text(f):
    """The proof bank's index and the stories the Proof Engine recorded, word for word."""
    proof = Path(f).resolve().parent / "proof"
    parts = []
    if (proof / "proof-bank.md").is_file():
        parts.append(read_text(proof / "proof-bank.md"))
    if (proof / "stories").is_dir():
        parts += [read_text(p) for p in sorted((proof / "stories").glob("*.md")) if p.is_file() and not p.is_symlink()]
    return "\n".join(parts)


def known_text(a, business_file=None):
    """What the member supplied: intake answers they gave or confirmed, the proof bank and the Business
    File. Drafts the session wrote (an unconfirmed answer, a talk, bio.md, talks.md) are not sources:
    a draft cannot vouch for itself."""
    f = folder(a)
    parts = []
    d = read_json(f / "pipeline.json", {"profile": {}, "talks": [], "stages": []})
    parts += [str(v.get("text", "")) for v in d["profile"].values() if isinstance(v, dict) and not v.get("draft")]
    parts.append(proof_text(f))
    if business_file and Path(business_file).is_file():
        parts.append(read_text(business_file))
    return "\n".join(parts)


CONTACT_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|(?<!\d)(?:\+?\d[\s().-]?){9,14}\d(?!\d)")


def no_contacts(**fields):
    """A person's email address or phone number does not go in the speaking folder."""
    for label, value in fields.items():
        if value and CONTACT_RE.search(str(value)):
            refuse(f"--{label.replace('_', '-')} holds an email address or a phone number. Those stay in the member's own "
                   "address book or CRM; here, give the role only (\"programme chair\")")


def finite(s):
    """A number for argparse: nan and inf are not amounts."""
    v = float(s)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("not a finite number")
    return v


def find_business_file(a):
    if getattr(a, "business_file", None):
        if not Path(a.business_file).is_file():
            emit({"ok": False, "error": f"file not found: {a.business_file}"}, 2)
        return a.business_file
    for cand in (Path("BUILDROOM_BUSINESS_FILE.md"), folder(a).resolve().parent / "BUILDROOM_BUSINESS_FILE.md"):
        if cand.is_file():
            return str(cand)
    return None


def banned_lines(business_file):
    """Retired lines (§1) and never-say claims (§18): quoted phrases or a ;-separated list, on the
    field's own line or on the indented bullets under it. A note in brackets is not an item."""
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
                q = re.search(r'"([^"]{4,})"', x)
                items.append(q.group(1) if q else re.sub(r"\s*\([^)]*\)\s*$", "", x.strip()).strip('"'))
        for x in items:
            x = re.sub(r"\s+", " ", x).strip(" .-*")
            if len(x) >= 6 and not x.startswith(("[", "(")) and x not in ("—", "none", "None yet"):
                out.append((kind, x))
    for line in plain(read_text(business_file)).splitlines():
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


# ---------------------------------------------------------------- reading the Business File
# What each question can be drafted from. The session writes the draft in the member's words; the
# member confirms it. Questions not listed here are only the member's to answer.
DRAFT_FROM = {
    "expertise": (1, 3), "audience": (2,), "goal": (1, 6), "credentials": (18, 17), "regions": (1,),
    "platforms": (14,), "topics": (3, 4), "hosts": (2, 14), "reach": (1,),
}
ONLY_MEMBER = ("experience", "formats", "paid", "size", "mode", "history", "targets", "availability")
# Sections the rest of the kit is drafted from: talks, bio, one-sheet, pitches.
KIT_FROM = {"talks": (3, 4, 2), "bio": (1, 17, 18), "one_sheet": (1, 3, 17, 18, 22), "pitches": (2, 4, 17)}


def file_sections(business_file):
    """{number: {"title", "status", "body"}} for each section of the Business File. The body keeps only
    lines that hold something: a field with nothing after its colon is still blank."""
    out = {}
    if not business_file or not Path(business_file).is_file():
        return out
    cur = None
    for line in read_text(business_file).splitlines():
        m = re.match(r"##\s+(\d+)\.\s+(.*)", line)
        if m:
            cur = int(m.group(1))
            out[cur] = {"title": m.group(2).strip(), "status": "", "lines": []}
            continue
        if cur is None or line.startswith("# "):
            continue
        st = re.search(r"\*\*Status:\*\*\s*([A-Za-z ]+?)\s*(?:·|$)", line)
        if st:
            out[cur]["status"] = st.group(1).strip().lower()
            continue
        t = line.strip()
        if not t or t.startswith(("_Built by", "---", "|---")):
            continue
        field = re.match(r"[-*]\s+\*\*[^*]+\*\*(?:\s*\([^)]*\))?\s*:?\s*(.*)", t)
        if field is not None and field.group(1).strip() in ("", "—", "-", "[ ]"):
            continue                                     # a blank field
        if re.fullmatch(r"\|[\s|]*\|", t):
            continue                                     # an empty table row
        out[cur]["lines"].append(t)
    for sec in out.values():
        sec["body"] = "\n".join(sec.pop("lines"))
        sec["filled"] = words(sec["body"]) >= 8 and sec["status"] != "not started"   # a blank template is not a source
    return out



MAG = r"(?:k|m|bn|thousand|million|billion)"
MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "bn": 1e9, "billion": 1e9}
NOUNS = (r"(?:clients|students|members|people|customers|businesses|companies|owners|audiences|attendees|events|"
         r"talks|stages|countries|cities|states|years|months|weeks|books|copies|subscribers|followers|listeners|"
         r"downloads|views|employees|teams|families|patients|women|men)")
NB = r"(?<![\d,.$£€/:-])"                     # a number starts here, not in the middle of one
UNITS = r"(?:minutes?|mins?|hours?|hrs?|days?|seconds?|am|pm|a\.m|p\.m|st|nd|rd|th|o'clock)\b"
NUMBER_RE = re.compile(rf"(?:[$£€][ ]?\d[\d,]*(?:\.\d+)?(?:[ ]?{MAG})?\b|{NB}\d[\d,]*(?:\.\d+)?[ ]?(?:%|percent\b)|"
                       rf"{NB}\d[\d,]*(?:\.\d+)?[ ]?{MAG}\b(?:[ ]{NOUNS})?|{NB}\d[\d,]*\+?[ ](?:[a-z-]+[ ]){{0,3}}?{NOUNS}\b|"
                       rf"{NB}\d[\d,]*\d\+?(?=[ ](?!{UNITS})[a-z]))", re.I)
SMALL = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
TENS = {"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
WORDNUM = {w: i + 1 for i, w in enumerate(SMALL.split())} | TENS
VAGUE_NUM = re.compile(r"\b(?:hundreds|thousands|dozens|millions|scores|countless) of(?: [a-z]+){0,2}|\b\d+(?:\.\d+)?x\b|"
                       rf"\b(?:{'|'.join(WORDNUM)}|a|several|a few|many)[ -](?:hundred|thousand|million|billion|dozen)\b(?: [a-z]+)?|"
                       r"\b(?:doubl|tripl|quadrupl)(?:ed?|ing|es)\b(?: [a-z]+){0,2}|"
                       r"\b(?:\d|six|seven|eight|nine)[- ]figures?\b", re.I)


def digits_for_words(text):
    """'Fourteen years' in the member's file vouches for '14 years' in a pitch."""
    return re.sub(rf"\b({'|'.join(WORDNUM)})\b", lambda m: f"{m.group(0)} {WORDNUM[m.group(1).lower()]}", text, flags=re.I)


def norm_num(s):
    return re.sub(r"[^\d.]", "", s).strip(".")


def number_sets(known):
    """What the member supplied, so '30 minutes' in their file does not clear '30 clients' in a pitch.
    Section numbers, dates and the file version are not the member's figures."""
    t = re.sub(r"(?m)^#{1,6}\s*\d+\.|§\s?\d+(?:\s?[-–]\s?\d+)?|\b\d{4}-\d{2}-\d{2}\b|^.*File version.*$", " ", known)
    t = digits_for_words(t)
    money = {norm_num(x) for x in re.findall(r"[$£€][ ]?(\d[\d,]*(?:\.\d+)?)", t)}
    bare = {norm_num(x) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", t)}
    mags = set()
    for n, u in re.findall(rf"(\d[\d,]*(?:\.\d+)?)\s?({MAG})\b", t, re.I):
        mags.add((norm_num(n), MULT[u.lower()]))
        bare.add(f"{float(norm_num(n)) * MULT[u.lower()]:.0f}")
    pct = {norm_num(n) for n in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s?(?:%|percent\b)", t, re.I)}
    things = {(norm_num(n), w.lower()) for n, w in re.findall(rf"{NB}(\d[\d,]*)\+?[ ](?:[a-z-]+[ ]){{0,3}}?({NOUNS})\b", t, re.I)}
    return {"bare": bare, "mag": mags, "pct": pct, "things": things, "money": money,
            "text": re.sub(r"\s+", " ", plain(t).lower())}


def unsourced_numbers(text, nums, allow=()):
    """Figures in the text that the member did not supply. `allow` is extra text whose figures are fine
    (the stage's own facts: its date, its audience size, the fee the host named)."""
    extra = number_sets(" ".join(allow)) if allow else None
    out = []
    text = re.sub(r"https?://\S+|[\w.+-]+@[\w-]+\.[\w.-]+", " ", text)          # a link or an address is not a claim
    text = re.sub(r"(?m)\b[A-Z]{2}[ ]\d{5}(?:-\d{4})?\b|\b\d{5}(?:-\d{4})?[ ]*$", " ", text)   # a ZIP code
    text = CONTACT_RE.sub(" ", text)
    for hit in sorted({m.group(0).strip() for m in NUMBER_RE.finditer(text)}):
        n = norm_num(re.match(r"[^\d]*(\d[\d,]*(?:\.\d+)?)", hit).group(1))
        mm = re.search(rf"\d\s?({MAG})\b", hit, re.I)

        def ok_in(s, strict_money=False):
            if re.search(r"%|percent", hit, re.I):
                return n in s["pct"]
            if mm:
                mult = MULT[mm.group(1).lower()]
                return (n, mult) in s["mag"] or f"{float(n) * mult:.0f}" in s["bare"]
            if hit[0] in "$£€":
                return n in (s["money"] if strict_money else s["bare"])     # the stage's head count is not a price
            last = hit.split()[-1].lower()
            if not re.fullmatch(NOUNS, last, re.I):
                return n in s["bare"]                  # a count of something unlisted: the number itself must be the member's
            return (n, last) in s["things"]
        if re.fullmatch(r"(?:19|20)\d\d", n) and "," not in hit.split()[0] and hit[0] not in "$£€":
            continue                                   # a year
        if re.fullmatch(r"[1-9]|10", n) and hit[0] not in "$£€" and not mm and not re.search(r"%|percent", hit, re.I):
            continue                                   # small everyday counts
        if ok_in(nums) or (extra and ok_in(extra, strict_money=True)):
            continue
        out.append(hit)
    for m in VAGUE_NUM.finditer(text):
        if not re.search(r"\b" + re.escape(re.sub(r"\s+", " ", m.group(0).lower())) + r"\b", nums["text"]):
            out.append(m.group(0))
    return sorted(set(out))


# Claims a host will check, and that a session must never write unless the member's own file says so.
CLAIMS = [
    (r"\baward[- ]winning\b", "award-winning"), (r"\bbest[- ]?selling\b", "best-selling"),
    (r"\bas seen (?:on|in)\b", "as seen on"), (r"\bfeatured (?:on|in|by)\b", "featured in"),
    (r"\bTEDx?\b", "TED"), (r"\binternational(?:ly)? (?:known|recognised|recognized|acclaimed|speaker)\b", "international speaker"),
    (r"\b(?:sought[- ]after|world[- ]class|world[- ]renowned|renowned|leading|top|premier|#1|number one)\s+(?:\w+\s){0,2}?(?:speaker|expert|authority|coach|consultant)\b", "top-speaker claim"),
    (r"\bkeynote speaker\b", "keynote speaker"), (r"\bcertified\b", "certified"),
    (r"\b(?:Fortune|Inc\.?)\s?\d+\b", "Fortune or Inc. list"), (r"\bstanding ovations?\b", "standing ovation"),
    (r"\bguarantee[ds]?\b", "guarantee"), (r"\bproven\b", "proven"),
    (r"\bbest[- ]?sellers?\b", "bestseller"), (r"\b(?:[A-Z][\w&-]+[ ]){1,4}of the Year\b", "an 'of the Year' title"),
    (r"\b(?:New York Times|Wall Street Journal|USA Today|Forbes|Inc\. Magazine|Entrepreneur Magazine|Oprah|CNN|BBC|NBC|CBS|ABC News|"
     r"Fox News|Harvard|Stanford|Yale|Oxford|Cambridge|MIT|Wharton)\b", "a famous name"),
    (r"\b(?:MBA|Ph\.?D\.?|CPA|CFP|CFA|M\.?D\.|J\.?D\.|Esq\.?|PMP|RN)(?![\w])", "letters after a name"),
    (r"\b(?:award|prize)[- ]?(?:winner|winning|nominated)\b|\bwinner of\b|\bhall of fame\b", "an award"),
]


def unsupported_claims(text, known):
    """Credential and status claims in the text that the member's own material does not contain."""
    low = re.sub(r"[\s-]+", " ", plain(known).lower())
    out = []
    for pat, label in CLAIMS:
        flags = 0 if label in ("TED", "an 'of the Year' title", "a famous name", "letters after a name") else re.I
        for m in re.finditer(pat, plain(text), flags):
            phrase = m.group(0)
            core = re.sub(r"[\s-]+", " ", phrase.lower()).strip()
            if not re.search(r"(?<![a-z0-9])" + re.escape(core) + r"(?![a-z0-9])", low):   # the phrase itself, as words
                out.append(f"{label} (\"{phrase}\")")
    return sorted(set(out))


PLACEHOLDER = re.compile(r"(?i:lorem ipsum)|\bTODO\b|\bTBD\b|\[[A-Z][A-Za-z _/'-]{2,}\]|\{[A-Za-z_ ]{2,}\}|\bXXX+\b|"
                         r"(?i:insert (?:name|event|date|topic|link) here)")
DASHES = ("—", "–")
