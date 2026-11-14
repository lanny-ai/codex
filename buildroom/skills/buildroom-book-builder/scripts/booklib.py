#!/usr/bin/env python3
"""Shared helpers for the AI Momentum Labs Book Builder scripts: the book folder, section files,
paragraphs and IDs, word counts, text checks and safe writes. Standard library only.
Imported by the other scripts; not run directly.
"""
import json, os, re, sys, tempfile
from datetime import date
from pathlib import Path

DEFAULT_CHAPTERS = 13
DEFAULT_WORDS = 62000
ABOUT_WORDS = 250
MARKER_RE = re.compile(r"^=== SECTION: (.+?) ===\s*$")
DASHES = ("—", "–")           # em dash, en dash: never in the manuscript
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
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        refuse(f"file not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        refuse(f"{p.name} is not valid JSON: {e}")


def write_atomic(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=p.suffix)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, p)


def write_json(path, data):
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "book"


def today():
    return str(date.today())


# ---------------------------------------------------------------- the book
def load_book(book):
    p = Path(book) / "book.json"
    if not p.exists():
        refuse(f"no book at {book}; run book_plan.py init first")
    return read_json(p)


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


def section_code(title):
    t = title.strip()
    m = re.match(r"Chapter (\d+)\b", t)
    if m:
        return f"C{int(m.group(1)):02d}"
    return {"title page": "TP", "dedication": "DE", "introduction": "IN", "conclusion": "CO",
            "about the author": "AB"}.get(t.lower(), "X" + re.sub(r"[^A-Z]", "", t.upper())[:3])


def section_key(title):
    """'Chapter 3: The Gap' -> 'Chapter 3'; front and back matter keep their title."""
    m = re.match(r"(Chapter \d+)\b", title.strip())
    return m.group(1) if m else title.strip()


def order_key(title):
    t = title.strip().lower()
    m = re.match(r"chapter (\d+)", t)
    if m:
        return (2, int(m.group(1)))
    return {"title page": (0, 0), "dedication": (0, 1), "introduction": (1, 0), "conclusion": (3, 0),
            "about the author": (4, 0)}.get(t, (5, 0))


def parse_sections(text):
    """[(title, [paragraph, ...])] from text that uses === SECTION: Title === markers."""
    out, cur, buf = [], None, []

    def flush():
        if cur is not None:
            paras = [re.sub(r"[ \t]+\n", "\n", p).strip() for p in re.split(r"\n\s*\n", "\n".join(buf))]
            out.append((cur, [p for p in paras if p]))
    for line in text.replace("\r\n", "\n").split("\n"):
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


def read_manuscript(book):
    """Every section file in manuscript/, in book order. A file may hold one section or several."""
    secs = []
    d = manuscript_dir(book)
    if d.is_dir():
        for f in sorted(d.glob("*.md")) + sorted(d.glob("*.txt")):
            for title, paras in parse_sections(read_text(f)):
                secs.append({"title": title, "paras": paras, "file": f.name})
    secs.sort(key=lambda s: order_key(s["title"]))
    return secs


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text))


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
    ws = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
    ss = sentences(text)
    if len(ws) < 100 or not ss:
        return None
    syl = sum(syllables(w) for w in ws)
    return round(0.39 * len(ws) / len(ss) + 11.8 * syl / len(ws) - 15.59, 1)


def shingles(text, k=8):
    ws = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(ws[i:i + k]) for i in range(max(0, len(ws) - k + 1))}


def norm_num(s):
    return re.sub(r"[^\d.]", "", s).strip(".").replace(",", "")
