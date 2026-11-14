#!/usr/bin/env python3
"""Shared helpers for the AI Momentum Labs Book Builder scripts: the book folder, section files,
paragraphs and IDs, word counts, text checks and safe writes. Standard library only.
Imported by the other scripts; not run directly.
"""
import json, os, re, sys, tempfile
from datetime import date
from pathlib import Path

DEFAULT_CHAPTERS = 12
DEFAULT_WORDS = 62000
ABOUT_WORDS = 250
MARKER_RE = re.compile(r"^\s*===\s*SECTION\s*:\s*(.+?)\s*===\s*$", re.I)
# em dash, en dash, figure dash, horizontal bar, minus sign: never in the manuscript (a hyphen is fine)
DASHES = ("\u2014", "\u2013", "\u2012", "\u2015", "\u2212")
DOUBLE_HYPHEN = re.compile(r"(?<!-)--+(?!-)")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def dash_count(text):
    """Dashes that are not allowed: the Unicode dashes and a double hyphen used as one."""
    return sum(text.count(c) for c in DASHES) + len(DOUBLE_HYPHEN.findall(text))


def plain_quotes(text):
    """Curly quotes and apostrophes as straight ones, for matching only."""
    return text.translate({0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"'})
STAGES = ("intake", "outline", "draft", "memo", "sample", "edit", "review", "facts", "readers", "copyedit",
          "regression", "gate")

QUESTIONS = [
    ("about", "What is your book about, in one or two sentences?",
     "The version you'd say out loud if someone asked at dinner. Don't polish it."),
    ("reader", "Who is this book for? Describe one real person who needs it.",
     "Their situation, what they're struggling with, what they want. A real client or a real friend is perfect."),
    ("transformation", "What is the single biggest transformation your reader gets from this book?",
     "Where are they before, where are they after. One line each."),
    ("story", "What is your story? Why are you the person to write this?",
     "The moment you learned this the hard way. The turning point. Be specific about what happened."),
    ("work", "What do you do, and how long have you been doing it?", "Your work, your role, your background. Plain facts."),
    ("method", "Walk me through your method or framework, step by step.",
     "If you have names for the steps, use them. If you don't, describe what you do first, second, third."),
    ("mistake", "What is the biggest mistake people make in your area, and what do you tell them instead?",
     "The thing you find yourself explaining over and over."),
    ("result", "Tell me about a result. Someone you helped, what changed for them.",
     "No names needed. What they came in with, what you did, what happened."),
    ("myth", "What do people believe about your topic that is flat wrong?", "The myth you'd love to kill."),
    ("lessons", "What are 3 to 5 lessons that cost you years to learn?", "One line each is fine. These become chapter seeds."),
    ("feel", "How do you want the reader to feel when they finish?", "And what do you want them to do the next morning?"),
    ("voice", "Describe your voice. How do you talk when you're teaching?",
     "Blunt or gentle? Funny or serious? Stories or lists? Name a writer or speaker you sound like, if one comes to mind."),
    ("titles", "Working title ideas, if any.", "Give me a few, or say 'you pick.'"),
    ("next_step", "What do you want the reader to do after the last page?",
     "Book a call, join something, try one exercise, email you. The book ends by pointing there."),
    ("must_include", "Anything else the book must include?",
     "A story, a quote, a client type, a warning. Anything you'd regret leaving out."),
]
QUESTION_KEYS = [q[0] for q in QUESTIONS]
# Which Business File sections usually answer a question already (the session confirms, never re-asks).
FROM_FILE = {"reader": "§2", "transformation": "§3", "story": "§17", "work": "§1", "method": "§3 / §4",
             "mistake": "§4", "result": "§18 proof vault", "myth": "§4", "voice": "§17", "next_step": "§3 / §6"}


# ---------------------------------------------------------------- files
def emit(obj, code=0):
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
    """A JSON file. With a dict default, the file must hold an object, and any key the default has
    that the file lacks is filled in, so a hand-edited or half-written file refuses cleanly."""
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        refuse(f"file not found: {p}")
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        refuse(f"{p.name} is not valid JSON: {e}")
    if isinstance(default, dict) or default is None:
        if not isinstance(d, dict):
            refuse(f"{p.name} should hold a JSON object ({{…}}); it holds something else")
        for k, v in (default or {}).items():
            if k not in d or (isinstance(v, (list, dict)) and not isinstance(d[k], type(v))):
                d[k] = v
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


def file_sha(path):
    """A checksum of a text file that ignores line endings and trailing spaces, for approvals."""
    import hashlib
    body = "\n".join(line.rstrip() for line in norm_newlines(read_text(path)).split("\n")).strip()
    return hashlib.sha256(body.encode()).hexdigest()


def find_book(book):
    """--book may be left out when the working folder has exactly one book under book/."""
    if book:
        return book
    found = sorted(p.parent for p in Path("book").glob("*/book.json") if p.parent.name != "demo")
    if len(found) == 1:
        return str(found[0])
    refuse("say which book: --book book/<slug>" + (f" (found: {', '.join(str(f) for f in found)})" if found else
                                                    " (no book here yet; book_plan.py init --book book/<slug>)"))


def arg_text(text, text_file, what="--text"):
    """Words from the command line, or from a file. A file is the safe way to pass anything the member
    said: inside double quotes the shell eats dollar amounts ($212,000 becomes 12,000)."""
    if text_file:
        f = Path(text_file)
        if not f.is_file():
            refuse(f"file not found: {text_file}")
        return read_text(f).strip()
    return (text or "").strip()


def eaten_dollars(text):
    """A sign that the shell swallowed a dollar amount: a stray ',100' or a number that starts with a comma."""
    return re.findall(r"(?<![\d$£€])[,]\d{3}\b", text)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "book"


def today():
    return str(date.today())


# ---------------------------------------------------------------- the book
def load_book(book):
    p = Path(book) / "book.json"
    if not p.exists():
        refuse(f"no book at {book}; run book_plan.py init first")
    d = read_json(p, {"settings": {}, "stages": {}, "approvals": [], "editions": []})
    st = d["settings"]
    try:
        st["chapters"] = max(1, int(st.get("chapters", DEFAULT_CHAPTERS)))
        st["words"] = max(1000, int(st.get("words", DEFAULT_WORDS)))
    except (TypeError, ValueError):
        refuse("book.json: settings.chapters and settings.words must be whole numbers")
    if not isinstance(st.get("chapter_words"), dict):
        st["chapter_words"] = {}
    return d


def save_book(book, data):
    data["updated"] = today()
    write_json(Path(book) / "book.json", data)


def stage(data, name):
    return data.setdefault("stages", {}).setdefault(name, {"status": "not started"})


def set_stage(data, name, status, **extra):
    s = stage(data, name)
    s.update({"status": status, "date": today(), **extra})
    return s


def targets(data):
    """Word targets from the settings: a chapter is words // chapters, the introduction and the
    conclusion about half a chapter each, About the Author about 250. Per-chapter overrides win."""
    ch, words = int(data["settings"]["chapters"]), int(data["settings"]["words"])
    per = words // ch
    over = data["settings"].get("chapter_words") or {}
    out = {"Introduction": per // 2, "Conclusion": per // 2, "About the Author": ABOUT_WORDS}
    for n in range(1, ch + 1):
        out[f"Chapter {n}"] = int(over.get(str(n), per))
    return out


FRONT_BACK = {"title page": ("TP", (0, 0)), "dedication": ("DE", (0, 1)), "foreword": ("FW", (0, 2)),
              "preface": ("PR", (0, 3)), "introduction": ("IN", (1, 0)), "conclusion": ("CO", (3, 0)),
              "acknowledgments": ("AK", (3, 8)), "acknowledgements": ("AK", (3, 8)), "about the author": ("AB", (4, 0))}
CHAPTER_RE = re.compile(r"chapter\s+(\d+)\b", re.I)


def section_code(title):
    """The short code used in paragraph IDs: C03, IN, CO … Any other section gets X plus its own
    letters and digits, so 'Appendix A' and 'Appendix B' never share IDs."""
    t = title.strip()
    m = CHAPTER_RE.match(t)
    if m:
        return f"C{int(m.group(1)):02d}"
    if t.lower() in FRONT_BACK:
        return FRONT_BACK[t.lower()][0]
    return "X" + (re.sub(r"[^A-Z0-9]", "", t.upper())[:12] or "X")


def section_key(title):
    """'Chapter 3: The Gap' -> 'Chapter 3'; front and back matter keep their title."""
    t = title.strip()
    m = CHAPTER_RE.match(t)
    if m:
        return f"Chapter {int(m.group(1))}"
    return next((k.title().replace(" The ", " the ") for k in FRONT_BACK if k == t.lower()), t)


def order_key(title):
    """Book order. A section this skill has no place for (an appendix, say) goes after the conclusion."""
    t = title.strip().lower()
    m = CHAPTER_RE.match(t)
    if m:
        return (2, int(m.group(1)))
    return FRONT_BACK[t][1] if t in FRONT_BACK else (3, 5)


def norm_newlines(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def stray_text(text):
    """Words in a section file that sit before the first marker (or in a file with no marker at all).
    Such text is in no section, so it would be left out of every check, edition and export."""
    lines = []
    for line in norm_newlines(text).split("\n"):
        if MARKER_RE.match(line):
            break
        lines.append(line)
    return words("\n".join(lines))


def parse_sections(text):
    """[(title, [paragraph, ...])] from text that uses === SECTION: Title === markers."""
    out, cur, buf = [], None, []

    def flush():
        if cur is not None:
            paras = [re.sub(r"[ \t]+\n", "\n", p).strip() for p in re.split(r"\n\s*\n", "\n".join(buf))]
            out.append((cur, [p for p in paras if p]))
    for line in norm_newlines(text).split("\n"):
        m = MARKER_RE.match(line)
        if m:
            flush()
            cur, buf = m.group(1).strip(), []
        elif cur is not None:
            buf.append(line)
    flush()
    return out


def manuscript_dir(book):
    return Path(book) / "manuscript"


def manuscript_files(book):
    d = manuscript_dir(book)
    return (sorted(d.glob("*.md")) + sorted(d.glob("*.txt"))) if d.is_dir() else []


def read_manuscript(book):
    """Every section file in manuscript/, in book order. A file may hold one section or several."""
    secs = []
    for f in manuscript_files(book):
        for title, paras in parse_sections(read_text(f)):
            secs.append({"title": title, "paras": paras, "file": f.name})
    secs.sort(key=lambda s: order_key(s["title"]))
    return secs


def manuscript_problems(book, chapters):
    """Things that would put the wrong text in an edition: a section twice, a chapter past the
    book's chapter count, and text that is in no section. [(id, message)]"""
    out, seen = [], {}
    for f in manuscript_files(book):
        n = stray_text(read_text(f))
        if n:
            out.append(("stray_text", f"manuscript/{f.name} has {n} words before its first '=== SECTION: … ===' line "
                        "(or has no such line), so that text is in no section"))
    for s in read_manuscript(book):
        k = section_key(s["title"])
        if k in seen:
            out.append(("duplicate_section", f"{k} is in the manuscript twice (manuscript/{seen[k]} and manuscript/{s['file']})"))
        seen.setdefault(k, s["file"])
        m = CHAPTER_RE.match(k)
        if m and int(m.group(1)) > chapters:
            out.append(("extra_chapter", f"{k} (manuscript/{s['file']}) is past the book's {chapters} chapters"))
    return out


WORD_RE = re.compile(r"[^\W_][\w'’-]*")


def words(text):
    return len(WORD_RE.findall(text))


def section_words(sec):
    return sum(words(p) for p in sec["paras"] if not p.startswith("@@ "))


def is_subhead(p):
    return p.startswith("@@ ")


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)


def reading_grade(text):
    """Flesch-Kincaid grade level, or None for very short text."""
    ws = re.findall(r"[^\W\d_][\w'’-]*", text)
    ss = sentences(text)
    if len(ws) < 100 or not ss:
        return None
    syl = sum(syllables(w) for w in ws)
    return round(0.39 * len(ws) / len(ss) + 11.8 * syl / len(ws) - 15.59, 1)


def shingles(text, k=8):
    ws = re.findall(r"[^\W_][\w']*", plain_quotes(text).lower())
    return {" ".join(ws[i:i + k]) for i in range(max(0, len(ws) - k + 1))}


def norm_num(s):
    return re.sub(r"[^\d.]", "", s).strip(".").replace(",", "")
