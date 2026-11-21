#!/usr/bin/env python3
"""Deep Discovery helper: the findings ledger for a member's own business.

It never reads the contents of a member's files and never goes online. It lists file names so the member
can agree what gets read, then checks, compares and prints what the session wrote into the ledger.

  discover.py inventory FOLDER [--exclude NAME ...] [--max N] [--json]
  discover.py check LEDGER.json [--business-file FILE]   every finding has a source and an honest confidence
  discover.py conflicts LEDGER.json      findings that disagree with each other
  discover.py gaps LEDGER.json [--cap N] the few questions worth asking, most important first
  discover.py ready LEDGER.json          readiness score: a guide, not a measurement
  discover.py page LEDGER.json           the "What I found" page, as markdown
  discover.py interview LEDGER.json      Quick Start: the short interview for a member with little written down
  discover.py onepage LEDGER.json        Quick Start: "Your business on one page", in the member's own words

Standard library only.
"""
import argparse, json, os, re, sys, time
from pathlib import Path

# key, Business File section, label, weight (how much later work leans on it), list?, the question to ask
FIELDS = [
    ("1.what_i_do", 1, "What I do", 10, False, "In a sentence or two, what do you do for your clients?"),
    ("1.who_i_serve", 1, "Who I serve", 10, False, "Who exactly do you serve? Name the niche and the kind of person or business."),
    ("1.core_result", 1, "Core result I deliver", 9, False, "What is the main result a client gets from working with you?"),
    ("1.price", 1, "Current price / price range", 8, False, "What do you charge today? A price or a range is fine."),
    ("1.lead_sources", 1, "Lead sources today", 5, True, "How do people find you today?"),
    ("1.tools", 1, "Tools", 4, True, "Which tools do you use for email, your CRM, your website and booking calls?"),
    ("1.booking", 1, "How someone books or buys", 6, False, "When someone is ready, how do they book a call or buy? A link is ideal."),
    ("2.profile", 2, "Best client, in one line", 9, False, "Describe your best client in one line: who they are and the situation they are in."),
    ("2.pains", 2, "Pains", 9, True, "What is your best client struggling with when they come to you?"),
    ("2.dream", 2, "Dream state", 7, False, "What does your client want life or business to look like after working with you?"),
    ("2.trigger", 2, "Buying trigger", 6, False, "What usually happens that makes a client decide to act now?"),
    ("2.objections", 2, "Objections", 7, True, "What do people say, or think, when they hesitate to buy?"),
    ("2.negative", 2, "Who I do not serve", 4, False, "Who do you turn away, and why?"),
    ("2.language", 2, "Client words (exact phrases)", 8, True, "What exact words do your clients use to describe the problem? A phrase or two is enough."),
    ("3.offer_name", 3, "Offer name", 6, False, "What is your main offer called?"),
    ("3.promise", 3, "Core promise", 9, False, "What do you promise a client, in one sentence?"),
    ("3.structure", 3, "How the engagement runs", 7, False, "How long does the work run, in what format, and when does it start and end?"),
    ("3.deliverables", 3, "Deliverables", 7, True, "What does a client actually receive?"),
    ("3.guarantee", 3, "Guarantee", 7, False, "Do you offer a guarantee? If so, what is the exact wording?"),
    ("3.typical_result", 3, "A typical client result", 7, False, "What result does a typical client get? Your honest middle case, not your best one."),
    ("4.alternative", 4, "What clients would do without me", 6, False, "If you did not exist, what would your best client do instead?"),
    ("4.category", 4, "Market category", 5, False, "What would a client call the kind of thing you sell?"),
    ("4.differentiator", 4, "What makes me different", 8, False, "What do you do differently from the others your clients could choose?"),
    ("x.story", 0, "Origin story", 5, False, "Why did you start this business?"),
    ("x.credentials", 0, "Background and credentials", 6, True, "What training, experience or track record should a client know about?"),
    ("x.voice", 0, "Voice samples (my own writing or talking)", 7, True, "Can you point me to something you wrote or said that sounds most like you?"),
    ("x.proof", 0, "Proof (real client results)", 8, True, "What is one real result a client got? Numbers if you have them."),
]
FIELD = {f[0]: f for f in FIELDS}
SECTIONS = {1: "Business Snapshot", 2: "Ideal Client", 3: "Offer", 4: "Positioning", 0: "Voice, proof and story"}
KINDS = ("file", "web", "business_file", "member", "hypothesis")
CONF = {"confirmed": 1.0, "likely": 0.7, "inferred": 0.25}
# The member's own word: said in this session, or already in their Business File.
OWN = ("member", "business_file")
# Fields that must be at least "likely" before a straight run through the build sessions is worth offering.
CORE = ("1.what_i_do", "1.who_i_serve", "1.core_result", "3.promise")
# A wrong answer here does real damage, so an old or unsure one is always put to the member.
FACTS = ("1.price", "3.guarantee", "3.typical_result", "3.offer_name", "3.structure")
# Things every owner knows off the top of their head. Asked before the hard ones, so a member with little
# written down gets to answer something early instead of skipping eight questions in a row.
EASY = ("1.price", "3.deliverables", "1.booking", "3.guarantee", "3.structure", "x.credentials", "3.offer_name")
# Next easiest: no research needed, just what the owner already knows about their own business.
SIMPLE = ("1.lead_sources", "1.tools", "3.typical_result", "2.negative", "x.story")
HEARSAY = re.compile(r"\b(someone (told|said)|i heard|heard that|apparently|supposedly|never saw|second[- ]?hand|word is|rumou?r)\b", re.I)
# "None" is a real answer for a guarantee. It is not evidence of proof, a voice or client words.
NO_CREDIT_WHEN_ABSENT = ("x.proof", "x.voice", "2.language", "x.credentials", "3.typical_result")
NEEDS_QUOTE = ("2.language", "x.voice", "x.proof")
READY_AT = 70
# Quick Start: three short blocks, the easy facts first. Client words, voice and proof are not asked for here;
# they are found, not recalled.
INTERVIEW = [
    ("Your offer", ("1.what_i_do", "1.who_i_serve", "1.core_result", "3.offer_name", "3.deliverables", "3.structure", "1.price", "3.guarantee", "1.booking")),
    ("Your client", ("2.profile", "2.pains", "2.dream", "2.trigger", "2.objections", "2.negative")),
    ("You and your business", ("x.credentials", "x.story", "1.lead_sources", "1.tools", "3.promise", "4.alternative", "3.typical_result")),
]

READABLE = {".md", ".markdown", ".txt", ".docx", ".doc", ".pdf", ".rtf", ".csv", ".html", ".htm", ".pptx", ".vtt", ".srt"}
SKIP_DIRS = {"node_modules", "__pycache__", "venv",
             # what Build Room sessions write: never research material
             "backups", "discovery", "autopilot"}
BUSINESS_FILE = "BUILDROOM_BUSINESS_FILE.md"
SENSITIVE = re.compile(
    r"(passw|secret|credential|\.env\b|api[-_ ]?key|access[-_ ]?token|"
    r"\btax(es)?\b|\b1040\b|\bw-?2\b|bank[-_ ]statement|account[-_ ]statement|\bp ?(&|and) ?l\b|profit[-_ ]and[-_ ]loss|"
    r"passport|\bssn\b|social[-_ ]security|medical[-_ ]record|health[-_ ]record|therapy|pay[-_ ]?stub|"
    r"divorce|custody|last[-_ ]will|license[-_ ]?scan|\bid[-_ ]?card|"
    r"(^|[\\/])(personal|private)([\\/]|$)|\bprivate\b|diary)", re.I)
# Words that are private in one file name and the member's trade in another ("payroll cleanup offer").
SENSITIVE_SOFT = re.compile(r"diagnosis|payroll|salary|journal", re.I)
MARKETING = re.compile(r"offer|script|sales|program|page|copy|webinar|proposal|post|email|blog", re.I)


def looks_private(rel):
    return bool(SENSITIVE.search(rel)) or bool(SENSITIVE_SOFT.search(rel) and not MARKETING.search(rel))


RELEVANT = [(r"offer|program|package|pricing|price|proposal|sales[-_ ]?page", 5), (r"client|customer|avatar|\bica\b|audience|\bpersonas?\b", 5),
            (r"testimonial|review|case[-_ ]?stud|result|\bwins?\b", 5), (r"about|\bbio\b|story|mission|values|compass", 4),
            (r"transcript|\bcalls?\b|interview|podcast|webinar|\btalk\b|speech|voice[-_ ]?memo", 4),
            (r"position|messag|brand|voice|copy|email|newsletter|\bposts?\b|\bdm\b", 3),
            (r"funnel|\bleads?\b|marketing|\bplan\b|strategy", 2), (r"\bsop\b|process|onboard|\bfaq\b", 2)]


def norm(v):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s$%.]", " ", str(v).lower())).strip(" .")


def numbers(v):
    return sorted({n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", str(v))})


def claim(field, f):
    """What a finding says, for comparing. The session may give a short `claim`; two findings with the same
    claim agree even when each source words it differently. Prices compare on their numbers."""
    if f.get("claim"):
        return "c:" + norm(f["claim"])
    if field == "1.price" and numbers(f.get("value")):
        return "n:" + ",".join(numbers(f["value"]))
    return "v:" + norm(f.get("value"))


def price_overlap(a, b):
    """One source giving the price and another giving the same price plus a fee is one answer with more detail."""
    if a.get("claim") or b.get("claim"):
        return False
    x, y = set(numbers(a.get("value"))), set(numbers(b.get("value")))
    return bool(x and y) and (x <= y or y <= x)


def kind(f):
    return f["source"].get("kind") if isinstance(f.get("source"), dict) else None


def origin(src):
    """What counts as one independent source: a website (by host) or one file, whatever part of it is cited."""
    ref = str(src.get("ref", "")).strip().lower()
    k = src.get("kind")
    if k == "web":
        m = re.match(r"https?://([^/]+)", ref)
        return "web:" + (m.group(1)[4:] if m and m.group(1).startswith("www.") else m.group(1) if m else ref)
    if k == "business_file":
        return "business_file"
    if k == "file":
        m = re.match(r"(.+?\.[a-z0-9]{1,5})(?=$|[\s,:;#(§])", ref)
        return "file:" + (m.group(1) if m else ref)
    return f"{k}:{ref}"


def load(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the ledger: {e}")
    if not isinstance(d, dict) or not isinstance(d.get("findings"), list):
        sys.exit('The ledger must be an object with a "findings" list.')
    return d


def retired_lines(business_file):
    """The quoted lines under §1 Retired lines in a Business File."""
    try:
        text = Path(business_file).read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"Cannot read the Business File: {e}")
    m = re.search(r"^- \*\*Retired lines(?::\*\*|\*\*(?:\s*\([^)]*\))?:?)(.*)$", text, re.M)
    return parse_retired(m.group(1)) if m else []


def parse_retired(line):
    """Entries are separated by semicolons. A note in brackets is not part of the line. Within an entry the
    quoted words are the retired line; an entry with no quotation marks is retired as a whole."""
    out = []
    for entry in re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", line).split(";"):
        quoted = re.findall(r"[\"“]([^\"”]{4,})[\"”]", entry)
        if not quoted:
            bare = re.sub(r"^(the )?(name|phrase|line|words?|claim|offer|tagline)\s+", "", entry.strip(" .—-"), flags=re.I).strip()
            quoted = [bare] if len(bare) >= 4 and not re.match(r"(none|n/?a|nothing)\b", bare, re.I) else []
        out += [x.strip() for x in quoted if not x.strip().lower().startswith("e.g")]
    return out


def usable(f):
    """A finding that may speak for the business: well formed, not retired."""
    return isinstance(f, dict) and f.get("field") in FIELD and isinstance(f.get("source"), dict) and f.get("confidence") in CONF and not f.get("retired")


def problems(d, retired=()):
    out, seen = [], set()
    fs = d["findings"]
    for i, f in enumerate(fs):
        tag = f"finding {f.get('id', i + 1) if isinstance(f, dict) else i + 1}"
        if not isinstance(f, dict):
            out.append(f"{tag}: not an object")
            continue
        if f.get("id") in seen:
            out.append(f"{tag}: id used twice")
        seen.add(f.get("id"))
        field = f.get("field")
        if field not in FIELD:
            out.append(f"{tag}: unknown field {field!r}")
        if not str(f.get("value", "")).strip():
            out.append(f"{tag}: no value")
        src = f.get("source") if isinstance(f.get("source"), dict) else {}
        k, ref = src.get("kind"), str(src.get("ref", "")).strip()
        if k not in KINDS:
            out.append(f"{tag}: source kind must be one of {', '.join(KINDS)}")
        elif k == "web" and not re.match(r"https?://\S+\.\S+", ref):
            out.append(f"{tag}: a web source needs its full address")
        elif k == "file" and not ref:
            out.append(f"{tag}: a file source needs the file's path")
        elif k == "hypothesis" and not ref:
            out.append(f"{tag}: a hypothesis needs a note on what it was reasoned from")
        conf = f.get("confidence")
        if conf not in CONF:
            out.append(f"{tag}: confidence must be confirmed, likely or inferred")
        elif k == "hypothesis" and conf != "inferred":
            out.append(f"{tag}: a hypothesis can only be 'inferred'")
        elif f.get("stale") and conf != "inferred":
            out.append(f"{tag}: an out-of-date source can only be 'inferred' until the member says it still holds")
        elif conf == "confirmed" and k in ("file", "web"):
            others = {origin(g["source"]) for g in fs if g is not f and usable(g) and g.get("field") == field and not g.get("stale")
                      and kind(g) in ("file", "web") + OWN and claim(field, g) == claim(field, f)} - {origin(src)}
            if not others:
                out.append(f"{tag}: 'confirmed' needs the member's word or a second independent source; one source is 'likely'")
        if field in NEEDS_QUOTE and k in ("file", "web") and not f.get("absent") and not str(f.get("quote", "")).strip():
            out.append(f"{tag}: client words, voice samples and proof need the exact quote")
        if f.get("guess_ok") and k != "member":
            out.append(f"{tag}: \"guess_ok\" marks a guess of yours the member said yes to, so its source kind is member")
        if f.get("absent") and k not in OWN:
            out.append(f"{tag}: only the member can say there is none")
        if field == "x.proof" and not f.get("absent") and f.get("permission") not in ("yes", "no", "unknown"):
            out.append(f"{tag}: proof needs \"permission\": yes, no or unknown")
        if field == "x.proof" and not f.get("absent") and HEARSAY.search(" ".join(str(f.get(x, "")) for x in ("value", "quote", "note"))):
            out.append(f"{tag}: this reads as second-hand (someone heard or was told). That is not proof. Leave it out, or cite where the client said it themselves")
        if not f.get("retired"):
            for line in retired:
                if norm(line) and norm(line) in norm(str(f.get("value", "")) + " " + str(f.get("quote", ""))):
                    out.append(f"{tag}: contains a retired line (“{line}”). Mark it \"retired\": true so it is never used, and the page will say where it still lives")
    scope = d.get("scope")
    if not (isinstance(scope, dict) and isinstance(scope.get("agreed"), str) and scope["agreed"].strip()):
        out.append('scope: record when the member agreed what could be read ("scope": {"agreed": "date and what they said"})')
    for s in d.get("skipped") or []:
        if s not in FIELD:
            out.append(f"skipped: unknown field {s!r}")
    return out


def by_field(d):
    out = {}
    for f in d["findings"]:
        if usable(f):
            out.setdefault(f["field"], []).append(f)
    return out


def find_conflicts(d, business_file_side=False):
    """Single-answer fields where real, current sources disagree and the member has not settled it.
    The Business File is the member's own word, so a file that differs from it is not an open choice:
    with business_file_side those are returned instead, to be shown as places that say something different."""
    out = []
    for key, fs in by_field(d).items():
        if FIELD[key][4]:
            continue
        if any(kind(f) == "member" for f in fs):
            continue
        # An out-of-date source does not argue with a current one. It is set apart on the page instead.
        real = [f for f in fs if kind(f) in ("file", "web", "business_file") and not f.get("absent") and not f.get("stale")]
        if any(kind(f) == "business_file" for f in real) != bool(business_file_side):
            continue
        groups = []
        for f in real:
            for g in groups:
                if claim(key, g[0]) == claim(key, f) or (key == "1.price" and price_overlap(g[0], f)):
                    g.append(f)
                    break
            else:
                groups.append([f])
        if len(groups) > 1:
            out.append((key, groups))
    return out


def best(fs):
    """The strongest finding for a field: the member's word first, then confidence, and a current source over an old one."""
    return max(fs, key=lambda f: (kind(f) == "member", kind(f) == "business_file", not f.get("stale"), CONF.get(f.get("confidence"), 0)))


def files_current(d):
    """The member looked at the page and said their own files are still right."""
    fc = d.get("files_current")
    return isinstance(fc, str) and bool(fc.strip())


def credit(d):
    conflicted = {k for k, _ in find_conflicts(d)}
    out = {}
    for key, fs in by_field(d).items():
        b = best(fs)
        if b.get("absent") and key in NO_CREDIT_WHEN_ABSENT:
            continue
        c = CONF[b["confidence"]]
        if kind(b) in OWN:
            c = 1.0
        elif kind(b) == "file" and b["confidence"] == "likely" and not b.get("stale") and files_current(d):
            c = 1.0
        out[key] = min(c, CONF["inferred"]) if key in conflicted else c
    return out


def stale_facts(d):
    """Old findings on fields where a wrong answer does damage, with nothing current to replace them."""
    out = []
    for key, fs in by_field(d).items():
        if key in FACTS and all(f.get("stale") for f in fs):
            out.append((key, best(fs)))
    return out


def src_text(f):
    s = f.get("source", {})
    k, ref = s.get("kind"), str(s.get("ref", ""))
    when = f" ({s['date']})" if s.get("date") else ""
    if k == "member" and f.get("guess_ok"):
        return "my wording; you said it looks right"
    if k == "hypothesis":
        return "my guess, " + (ref if re.match(r"(from|reasoned|based)\b", ref, re.I) else "from " + ref)
    return {"member": "you told me", "business_file": "your Business File" + (f", {ref}" if ref else ""), "web": ref + when,
            "file": f"your file {ref}{when}"}.get(k, ref)


def answered_none(fs):
    """The member already said there is none. That is an answer, whether or not it earns credit."""
    return any(f.get("absent") and kind(f) in OWN for f in fs)


def gap_list(d, cap):
    """The questions worth asking: disagreements and old facts first, then the core, then what every owner
    knows, then the rest by how much later work leans on it."""
    cr, bf = credit(d), by_field(d)
    conflicted = dict(find_conflicts(d))
    skipped = set(d.get("skipped") or [])
    stale = dict(stale_facts(d))
    rows = []
    for key, _sec, label, weight, _multi, question in FIELDS:
        if key in skipped:
            continue
        if key in conflicted:
            opts = " or ".join(f"“{g[0]['value']}” ({src_text(g[0])})" for g in conflicted[key])
            rows.append((0, -weight, key, f"{label}: I found {opts}. Which is right today?"))
        elif key in stale:
            b = stale[key]
            rows.append((1, -weight, key, f"{label}: an older source says “{b['value']}” ({src_text(b)}). Is that still true today?"))
        elif cr.get(key, 0) < CONF["likely"]:
            if answered_none(bf.get(key, [])):
                continue
            known = [f for f in bf.get(key, []) if not f.get("absent")]
            rank = 2 if key in CORE else 3 if key in EASY else 4 if key in SIMPLE else 5 if key in FACTS or not known else 6
            # A member who skipped two questions in a section will skip the harder ones there too. Ask those last.
            if rank >= 5 and sum(1 for k in skipped if FIELD.get(k, (0, None))[1] == _sec) >= 2:
                rank = 7
            core = best(bf["1.core_result"]) if cr.get("1.core_result", 0) >= 1 else None
            if key == "3.promise" and not known and core:
                rows.append((rank, -weight, key, f"Core promise: is it roughly your core result, “{core['value']}”? Say yes, or put it in your own words."))
            elif known and best(known).get("stale"):
                b = best(known)
                rows.append((rank, -weight, key, f"{label}: an older source says “{b['value']}” ({src_text(b)}). Does that still hold? If not: {question}"))
            elif known:
                b = best(known)
                rows.append((rank, -weight, key, f"{label}: my best guess is “{b['value']}” ({src_text(b)}). Is that right? If not: {question}"))
            else:
                rows.append((rank, -weight, key, question))
    rows.sort()
    return rows[:cap], rows[cap:]


def score(d):
    cr = credit(d)
    total = sum(f[3] for f in FIELDS)
    pct = round(100 * sum(f[3] * cr.get(f[0], 0) for f in FIELDS) / total)
    weak = [FIELD[k][2] for k in CORE if cr.get(k, 0) < CONF["likely"]]
    # A promise can be drafted as a plain restatement of a core result the member has given in their own words.
    if cr.get("1.core_result", 0) >= 1 and FIELD["3.promise"][2] in weak:
        weak.remove(FIELD["3.promise"][2])
    return pct, weak


def cmd_inventory(a):
    root = Path(a.folder).expanduser()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    excl = {e.lower().strip("/").replace("\\", "/") for e in a.exclude}
    rows, skipped, sensitive, business_files, left_out = [], 0, [], [], []
    for dp, dns, fns in os.walk(root):
        rel_dir = Path(dp).relative_to(root)
        keep = []
        for x in dns:
            rel = str(rel_dir / x).replace("\\", "/").lower()
            if x.lower() in excl or rel in excl:
                left_out.append(str(rel_dir / x) + "/")
            elif not x.startswith((".", "_")) and x.lower() not in SKIP_DIRS:
                keep.append(x)
        dns[:] = keep
        for fn in fns:
            p = Path(dp) / fn
            rel = str(p.relative_to(root))
            if fn.lower() in excl or rel.replace("\\", "/").lower() in excl:
                left_out.append(rel)
                continue
            if fn == BUSINESS_FILE:
                business_files.append(rel)
                continue
            if fn.startswith((".", "_")) or p.suffix.lower() not in READABLE or p.is_symlink():
                skipped += 1
                continue
            if looks_private(rel):
                sensitive.append(rel)
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            rel_score = sum(w for pat, w in RELEVANT if re.search(pat, rel, re.I))
            rows.append({"path": rel, "kb": round(st.st_size / 1024, 1), "modified": time.strftime("%Y-%m-%d", time.localtime(st.st_mtime)),
                         "relevance": rel_score})
    rows.sort(key=lambda r: (-r["relevance"], -int(r["modified"].replace("-", "")), r["path"]))
    shown = rows[:a.max]
    if a.json:
        print(json.dumps({"folder": str(root), "files": shown, "more": len(rows) - len(shown), "business_files": sorted(business_files),
                          "left_out_as_asked": sorted(left_out), "sensitive_not_listed_for_reading": sorted(sensitive), "other_files_skipped": skipped}, indent=1))
        return
    print(f"Folder: {root}\nFiles I could read: {len(rows)} (showing {len(shown)}, most useful first). Nothing has been opened yet.\n")
    for r in shown:
        print(f"  {r['modified']}  {r['kb']:>8} KB  {r['path']}")
    if len(rows) > len(shown):
        print(f"\n  ... and {len(rows) - len(shown)} more.")
    if business_files:
        print("\nYour Business File (read as your own word, not as research): " + "; ".join(sorted(business_files)))
        if len(business_files) > 1:
            print("  There is more than one. Ask the member which is current before going on.")
    if left_out:
        print(f"\nLeft out, as you asked ({len(left_out)}):")
        for s in sorted(left_out):
            print(f"  {s}")
    elif a.exclude:
        print("\nNothing here matched what you asked to leave out: " + ", ".join(a.exclude))
    if sensitive:
        print(f"\nLooks private, so I will NOT read these unless you tell me to ({len(sensitive)}):")
        for s in sorted(sensitive)[:25]:
            print(f"  {s}")
    print(f"\nOther files skipped (hidden, Build Room's own output, or a type I do not read): {skipped}")
    print("Tell me any folder or file to leave out before I read anything.")


def cmd_check(a):
    d = load(a.ledger)
    probs = problems(d, retired_lines(a.business_file) if a.business_file else ())
    for p in probs:
        print("FIX  " + p)
    print(f"{len(d['findings'])} findings, {len(probs)} to fix.")
    sys.exit(1 if probs else 0)


def cmd_conflicts(a):
    d = load(a.ledger)
    cs = find_conflicts(d)
    side = find_conflicts(d, business_file_side=True)
    if not cs:
        print("No disagreements between sources.")
    for key, groups in cs:
        print(f"{FIELD[key][2]}:")
        for g in groups:
            print(f"  “{g[0]['value']}”  from " + "; ".join(src_text(f) for f in g))
    if cs:
        print(f"\n{len(cs)} to ask the member about. Never pick one yourself.")
        if any(not f.get("claim") for _k, groups in cs for g in groups for f in g):
            print("If two of these say the same thing in different words, give both findings the same short \"claim\" and run this again.")
    if side:
        print("\nThese places say something different from the member's Business File. The Business File stands; the page lists them so the member can fix the old place or correct the file:")
        for key, groups in side:
            for g in groups:
                if not any(kind(f) == "business_file" for f in g):
                    print(f"  {FIELD[key][2]}: “{g[0]['value']}”  in " + "; ".join(src_text(f) for f in g))


def cmd_gaps(a):
    d = load(a.ledger)
    ask, later = gap_list(d, a.cap)
    skipped = [FIELD[s][2] for s in d.get("skipped") or [] if s in FIELD]
    if not ask:
        print("Nothing to ask. Every field has at least a likely answer" + (", apart from the ones the member skipped." if skipped else "."))
    else:
        print(f"Ask these {len(ask)}, in this order, one at a time. The member may skip any; record a skip in the ledger's \"skipped\" list.\n")
        for i, (_, _, _key, q) in enumerate(ask, 1):
            print(f"{i}. {q}")
    if later:
        print(f"\nLeft for the build sessions, not asked now ({len(later)}): " + ", ".join(FIELD[k][2] for _, _, k, _ in later))
    if skipped:
        print(f"\nSkipped by the member, not asked again ({len(skipped)}): " + ", ".join(skipped))


def cmd_ready(a):
    d = load(a.ledger)
    probs = problems(d)
    if probs:
        sys.exit(f"The ledger has {len(probs)} thing(s) to fix first. Run: discover.py check")
    pct, weak = score(d)
    ready = pct >= READY_AT and not weak
    print(f"Readiness: {pct} out of 100. This is a guide to how much is known, not a measurement of the business.")
    if ready:
        print("Ready: enough is known for the build sessions to start from facts instead of a blank page.")
    else:
        print("Not ready yet for a straight run through the build sessions (Autopilot). A run now would be mostly blanks and guesses.")
        if weak:
            print("These must be known first: " + ", ".join(weak) + ".")
        cr = credit(d)
        # In the extra round, leave out the questions in a section where the member already skipped the basics.
        ask = [r for r in gap_list(d, 40)[0] if r[0] < 7][:5]
        skipped = [FIELD[s][2] for s in d.get("skipped") or [] if s in FIELD and cr.get(s, 0) < CONF["likely"]]
        if ask and d.get("extra_round"):
            print("The one extra round of questions has been asked. Do not offer more questions.")
            ask = []
        if ask:
            print("Answering these would help most. Ask them once, as one more round, record \"extra_round\": true in the ledger, and then stop asking:")
            for _, _, _key, q in ask:
                print(f"  - {q}")
        elif not d.get("extra_round"):
            print("There is nothing left to ask that the member has not already answered or skipped. Do not offer more questions.")
        if skipped:
            print("Already skipped by the member: " + ", ".join(skipped) + ". Those stay open until they choose to answer.")
        if weak and set(weak) & set(skipped):
            print("A skipped question is among the ones that must be known. No more asking gets past that; the session that works it out with the member does.")
        client_open = sum(1 for k in ("2.profile", "2.pains", "2.dream", "2.objections", "2.language") if cr.get(k, 0) < CONF["likely"])
        by_hand = "Ideal Client Avatar (“Help me build my ideal client avatar”)" if client_open >= 3 else "Signature Offer (“Help me build my signature offer”)"
        print("Tell the member plainly: " + ("a few minutes of answers now is worth more than a long run. " if ask else "")
              + f"The session to run by hand next is {by_hand}. Going ahead with Autopilot anyway is theirs to choose, not yours to recommend.")
    sys.exit(0 if ready else 2)


def cmd_interview(a):
    d = load(a.ledger)
    cr, bf = credit(d), by_field(d)
    skipped = set(d.get("skipped") or [])
    core = best(bf["1.core_result"]) if cr.get("1.core_result", 0) >= 1 else None
    total, out = 0, []
    for title, keys in INTERVIEW:
        qs = []
        for key in keys:
            if key in skipped or cr.get(key, 0) >= CONF["likely"] or answered_none(bf.get(key, [])):
                continue
            if key == "3.promise" and core:
                qs.append(f"Is your promise to a client roughly your core result, “{core['value']}”? Say yes, or put it in your own words.")
            else:
                qs.append(FIELD[key][5])
        if qs:
            out += [f"\n{title} ({len(qs)}):"] + [f"  {total + i}. {q}" for i, q in enumerate(qs, 1)]
            total += len(qs)
    if not total:
        print("Nothing left to ask. Run: discover.py onepage, then discover.py ready.")
        return
    print(f"Quick Start interview: {total} short questions, about {max(5, round(total * 0.7))} minutes. One at a time, in this order.")
    print("Tell the member first: any question can be skipped, a short answer is fine, and \"none\" is a real answer.")
    print("\n".join(out))
    print("\nRecord each answer as a member finding in their own words. A skip goes in \"skipped\"; \"none\" is recorded with \"absent\": true.")
    print("Do not improve an answer, and do not ask a follow-up unless the answer cannot be understood.")


def cmd_onepage(a):
    d = load(a.ledger)
    probs = problems(d)
    if probs:
        sys.exit(f"The ledger has {len(probs)} thing(s) to fix first. Run: discover.py check")
    bf = by_field(d)
    out = [f"# {d.get('subject') or 'Your business'} on one page", "", "Every line here is in your own words, as you gave it. Nothing was added and nothing was polished.", ""]
    shown = set()
    for title, keys in INTERVIEW:
        lines = []
        for key in keys:
            own = [f for f in bf.get(key, []) if kind(f) in OWN and not f.get("stale")]
            if not own:
                continue
            shown.add(key)
            label = FIELD[key][2]
            vals = [f["value"] + (" (my wording; you said it looks right)" if f.get("guess_ok") else "") for f in own] if FIELD[key][4] else [best(own)["value"] + (" (my wording; you said it looks right)" if best(own).get("guess_ok") else "")]
            vals = list(dict.fromkeys(vals))
            lines += [f"- **{label}:** {vals[0]}"] if len(vals) == 1 else [f"- **{label}:**"] + [f"  - {v}" for v in vals]
        if lines:
            out += [f"## {title}", ""] + lines + [""]
    skipped = set(d.get("skipped") or [])
    todo = [FIELD[k][2] for _t, keys in INTERVIEW for k in keys if k not in shown]
    if todo:
        out += ["## Still open", "", ", ".join(todo) + ".", "", "These are yours to answer when you are ready. Nothing was guessed to fill them.", ""]
    pct, weak = score(d)
    out += ["## How ready this is", "", f"{pct} out of 100. A guide to how much is known, not a measurement of your business."
            + (f" Still needed first: {', '.join(weak)}." if weak else "")]
    print("\n".join(out))


def cmd_page(a):
    d = load(a.ledger)
    bf, conflicted = by_field(d), dict(find_conflicts(d))
    stale = dict(stale_facts(d))
    pct, weak = score(d)
    out = [f"# What I found about {d.get('subject') or 'your business'}", ""]
    if d.get("date"):
        out += [f"_Researched {d['date']}. Correct anything that is wrong. Your word always wins._", ""]
    scope = d.get("scope") or {}
    if scope.get("read"):
        out += ["**What I read:** " + "; ".join(map(str, scope["read"])) + (f" ({scope['opened']} file{'' if str(scope['opened']) == '1' else 's'} opened)" if scope.get("opened") else ""), ""]
    if scope.get("excluded"):
        out += ["**What I left alone, as you asked:** " + "; ".join(map(str, scope["excluded"])), ""]
    for sec in (1, 2, 3, 4, 0):
        lines = []
        for key, s, label, _w, multi, _q in FIELDS:
            if s != sec or key not in bf or key in conflicted:
                continue
            # Out-of-date material never sits among the findings. It is listed apart, below.
            fs = sorted((f for f in bf[key] if not f.get("stale")), key=lambda f: -CONF.get(f.get("confidence"), 0))
            if not fs:
                continue
            if not multi:
                b = best(fs)
                also = sorted({src_text(f) for f in fs if f is not b and claim(key, f) == claim(key, b) and not f.get("stale")} - {src_text(b)})
                lines.append(f"- **{label}:** {b['value']}  \n  _{b.get('confidence')} · {src_text(b)}" + (f" · also: {'; '.join(also)}" if also else "") + "_")
                continue
            lines.append(f"- **{label}:**")
            seen = set()
            for f in fs:
                if (claim(key, f), origin(f["source"])) in seen:
                    continue
                seen.add((claim(key, f), origin(f["source"])))
                quoted = f.get("quote") and key in NEEDS_QUOTE
                text = f"“{f['quote']}”" if quoted else f["value"]
                extra = []
                if f.get("who"):
                    extra.append(f"said by {f['who']}")
                if key == "x.proof" and not f.get("absent"):
                    extra.append({"yes": "permission to use: yes", "no": "NOT to be used publicly", "unknown": "permission to use: not known"}[f.get("permission", "unknown")])
                lines.append(f"  - {text}  \n    _{f.get('confidence')} · {src_text(f)}" + (" · " + " · ".join(extra) if extra else "") + "_")
        if lines:
            out += [f"## {SECTIONS[sec]}", ""] + lines + [""]
    if conflicted:
        out += ["## Things that disagree", "", "Your sources say different things here. Tell me which is right today.", ""]
        for key, groups in conflicted.items():
            out.append(f"- **{FIELD[key][2]}:** " + " **or** ".join(f"“{g[0]['value']}” ({'; '.join(src_text(f) for f in g)})" for g in groups))
        out.append("")
    differs = find_conflicts(d, business_file_side=True)
    if differs:
        out += ["## Places that say something different from your Business File", "", "I am going by your Business File. If one of these is the right one, tell me and I will correct the file.", ""]
        for key, groups in differs:
            out += [f"- **{FIELD[key][2]}:** “{g[0]['value']}” ({'; '.join(src_text(f) for f in g)})" for g in groups if not any(kind(f) == "business_file" for f in g)]
        out.append("")
    old = [f for fs in bf.values() for f in fs if f.get("stale")]
    if old:
        out += ["## Older material I am not relying on", "", "These came from sources that look out of date, so I have set them aside. Nothing here is used unless you tell me it still holds.", ""]
        seen = set()
        for f in old:
            line = f"- **{FIELD[f['field']][2]}:** “{f.get('quote') or f['value']}” ({src_text(f)})" + (" I will ask you about this one." if f["field"] in stale else "")
            if line not in seen:
                out.append(line)
                seen.add(line)
        out.append("")
    gone = [f for f in d["findings"] if isinstance(f, dict) and f.get("retired") and isinstance(f.get("source"), dict)]
    if gone:
        out += ["## Retired lines still in your files", "", "You told us never to use these. They are still written in the places below, so you may want to remove them there.", ""]
        out += [f"- “{f.get('quote') or f.get('value')}” ({src_text(f)})" for f in gone] + [""]
    skipped = set(d.get("skipped") or [])
    current = {k for k, fs in bf.items() if any(not f.get("stale") for f in fs)}
    missing = [f[2] for f in FIELDS if f[0] not in current and f[0] not in skipped]
    if missing:
        out += ["## What I could not find", "", ", ".join(missing) + ".", ""]
    passed = [f[2] for f in FIELDS if f[0] not in current and f[0] in skipped]
    if passed:
        out += ["## What you chose to skip for now", "", ", ".join(passed) + ".", ""]
    out += ["## How ready this is", "", f"{pct} out of 100. A guide to how much is known, not a measurement of your business."
            + (f" Still needed first: {', '.join(weak)}." if weak else "")]
    print("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory")
    p.add_argument("folder")
    p.add_argument("--exclude", nargs="*", default=[])
    p.add_argument("--max", type=int, default=60)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_inventory)
    p = sub.add_parser("check")
    p.add_argument("ledger")
    p.add_argument("--business-file")
    p.set_defaults(fn=cmd_check)
    for name, fn in (("conflicts", cmd_conflicts), ("ready", cmd_ready), ("page", cmd_page), ("interview", cmd_interview), ("onepage", cmd_onepage)):
        p = sub.add_parser(name)
        p.add_argument("ledger")
        p.set_defaults(fn=fn)
    p = sub.add_parser("gaps")
    p.add_argument("ledger")
    p.add_argument("--cap", type=int, default=10)
    p.set_defaults(fn=cmd_gaps)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
