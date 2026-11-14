#!/usr/bin/env python3
"""Webinar Builder check: the gate before a webinar goes live. GO only when every critical item passes.

Local only. Reads the member's webinar.json, the launch's close.md and proof bank, the Business File, the
registration page words and the deck.

Usage
  webinar_check.py check --spec webinar.json [--close close.md] [--proof proof-bank.md]
                         [--business-file BUILDROOM_BUSINESS_FILE.md] [--page registration-page.md]
                         [--deck slides.pptx] [--out check.md]
      Prints JSON {result: GO|HOLD, items: [{id, level, ok, detail}]}; --out also writes check.md.
      Exit 0 GO, 1 HOLD, 2 when the spec cannot be read.

Critical: placeholders_filled length_fits offer_disclosed objections_named three_beliefs loops_closed
          offer_matches_close deadline_real proof_classified earnings_typical retired_lines refused_tactics
          recording_notice qa_bank_covers moderator_named, with --page page_discloses, and with --deck
          deck_font_min deck_contrast_min
Advisory: chat_prompts offer_asks story_length offer_by_minute not_your_fault buyer_names, and with --deck
          deck_font_target deck_contrast_target deck_words

close.md is read for: every money figure ($, US$, £, €, "dollars", "USD"), dates written as a month and a day,
"N payments", the number of places ("Places: 12" or "12 places"), the deadline (a line starting "Deadline",
"Enrolment closes", "Enrollment closes", "Cart closes" or "Doors close"; "none" or "no deadline" there means
none), and PENDING anywhere outside an HTML comment.

The proof bank is read as a table with a header row naming ID, Origin (or Class), Permission and Scope, or as
one heading per story ("## P-02 …") with "Class:" (or "Origin:"), "Permission:" (or "Consent:") and "Scope:"
lines under it. Every story the talk cites must be found there with its class and permission.

The script catches words, not intent: a person still reads every block for the same things said another way
(references/honesty-rules.md).

Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402
import argparse, json, re, zipfile  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slide_builder  # noqa: E402

PLACEHOLDER = re.compile(r"\[write:|\bTBD\b|\bTODO\b|\bXXX\b|\{\{.*?\}\}")
MONEY = re.compile(r"(?:US\$|\$|£|€)\s?(\d[\d,]*(?:\.\d{1,2})?)\s*(k|K|m|M|thousand|million)?\b|"
                   r"\b(\d[\d,]*(?:\.\d{1,2})?)\s*(?:dollars|usd|pounds|euros|gbp|eur)\b", re.I)
MONEY_WORDS = re.compile(r"\b(hundred|thousand|million)\s+(dollars|pounds|euros|bucks)\b", re.I)
MONTHS = "january february march april may june july august september october november december".split()
DATE = re.compile(r"\b(" + "|".join(m + "|" + m[:3] for m in MONTHS) + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b", re.I)
PAYMENTS = re.compile(r"\b(\d{1,2}|two|three|four|five|six|twelve)\s+(?:monthly\s+)?(?:payments|instal?ments)\b", re.I)
PLACES = re.compile(r"\b(\d{1,4})\s+(?:places|spots|seats|spaces)\b|\b(?:places|spots|seats|spaces)\s*[:=]\s*(\d{1,4})\b", re.I)
WORDNUM = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "twelve": "12"}
OPEN_LOOP = re.compile(r"(we'?ll get to that|i cover that (in|inside)|more on that (in|inside|later)|that'?s for another "
                       r"(day|time)|you'?ll (learn|get) that (when|once|inside)|i can'?t (go into|cover) that (today|here)|"
                       r"(it'?s|that'?s) (all )?(in|inside) the (program|course|membership|circle|group))", re.I)
DEADLINE = re.compile(r"\b(midnight|deadline|expires?|expiring|doors? close|cart closes?|enrol?l?ment closes|closes (tonight|"
                      r"tomorrow|at|on|this|friday|saturday|sunday|monday|january|february|march|april|may|june|july|august|"
                      r"september|october|november|december)|ends (tonight|tomorrow|at|on)|last chance|until (tonight|midnight))\b",
                      re.I)
HONEST_WINDOW = re.compile(r"\b(replay|recording)\b[^.]{0,40}\b(expires?|available until|until)\b|\b(window|follow-?up)\b[^.]{0,30}"
                           r"\bends?\b|\bavailable until\b", re.I)
RELATIVE_DAY = re.compile(r"\b(tonight|tomorrow|this (friday|saturday|sunday|monday|tuesday|wednesday|thursday|weekend))\b", re.I)
EARN = re.compile(r"\b(made|make|makes|earn(ed|s)?|revenue|income|profit|grew|increase[sd]?|doubled|tripled|more money)\b", re.I)
PCT = re.compile(r"\b\d{1,3}(\.\d)?\s?%")
REFUSED = {
    "fake_count": re.compile(r"room is (full|packed)|expand(ed)? the room|\b\d[\d,]* (people|of you) (are )?(here|watching|live|"
                             r"with us|in the room|on (the|this) (call|webinar|zoom))( (right )?now| tonight| today)?\b|record "
                             r"(attendance|turnout)|hundreds of (people|you) (are )?(here|live|watching)", re.I),
    "seeded_chat": re.compile(r"seed(ed|ing)? (the )?chat|plant(ed)? (a |some )?(question|comment)s?|fake (comment|question|"
                              r"attendee)s?|pretend(ing)? to be an? (attendee|customer|buyer)", re.I),
    "fake_poll": re.compile(r"\b\d{1,3}% (of you )?(said|voted|answered|chose|picked)\b|poll results? (show|say)s? \d", re.I),
    "fake_timer": re.compile(r"timer (resets|restarts)|reset(s|ting)? the (timer|countdown)|extend(ing)? the (timer|countdown)|"
                             r"page (is )?coming down|(this|the) (video|page|offer|class) (will be|is being|is) taken down|"
                             r"evergreen (timer|countdown)", re.I),
    "replay_threat": re.compile(r"edit (that|this|it) out|won'?t be (in|on) the replay|not be in the replay|(cut|remove)[^.]{0,20}"
                                r"from the replay", re.I),
    "hidden_text": re.compile(r"embedded commands?|hidden (text|message|command)s?|low[- ]contrast (text|words)", re.I),
    "fake_scarcity": re.compile(r"only \d+ (spots?|seats?|places?|spaces?) (are )?(left|remaining)|\d+ (spots?|seats?|places?|"
                                r"spaces?) (are )?(left|remaining)|(spots|seats|places) are (almost|nearly) gone|filling (up )?"
                                r"fast|almost sold out", re.I),
}
LIVE_CLAIM = re.compile(r"\b(we'?re|we are) live\b|\blive (right )?now\b|joining (us )?live|\bstarting soon\b|\bthis is live\b|"
                        r"\blive with (me|us)\b|\bhere live\b", re.I)
NOT_FAULT = re.compile(r"not your fault", re.I)
BUYER_NAMES = re.compile(r"read (out )?(the )?(full )?names of (the )?(buyers|people who (bought|joined))", re.I)
ALLOWED_CLASSES = set("ABCDEH")          # X is an illustration, never proof; U unconfirmed; R retired
NEEDS_TYPICAL = set("BDHE")
OBJ_SYNONYMS = {"time": ("time", "busy"), "money": ("money", "afford", "cost", "price"),
                "confidence": ("confidence", "confident", "can i do", "technical", "too old", "skill"),
                "spouse": ("spouse", "partner", "husband", "wife")}
OFFER_KINDS = {"offer", "qa", "close", "transition", "promise"}


def norm_money(num, mult=None):
    v = float(num.replace(",", ""))
    if mult:
        v *= 1_000_000 if mult.lower().startswith("m") else 1000
    return f"{v:.2f}".rstrip("0").rstrip(".")


def figures(text):
    out = set()
    for a, m, b in MONEY.findall(text or ""):
        out.add(norm_money(a, m) if a else norm_money(b))
    return out


def dates(text):
    return {(next(i for i, m in enumerate(MONTHS) if m.startswith(mo.lower()[:3])), int(d)) for mo, d in DATE.findall(text or "")}


def payments(text):
    return {WORDNUM.get(n.lower(), n) for n in PAYMENTS.findall(text or "")}


def places(text):
    return {a or b for a, b in PLACES.findall(text or "")}


def strings(x):
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for v in x.values() for s in strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in strings(v)]
    return []


def seg_text(s):
    keys = ("title", "say", "chat_prompt", "notes", "slides", "loop")
    return "\n".join(t for k in keys for t in strings(s.get(k)))


def norm(t):
    t = t.lower().replace("’", "'").replace("‘", "'")
    t = re.sub(r"n't\b", " not", t)
    t = re.sub(r"'s\b", " is", t)
    t = re.sub(r"'re\b", " are", t)
    t = re.sub(r"'ll\b", " will", t)
    t = re.sub(r"'ve\b", " have", t)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def split_items(text):
    """One field's items: quoted text when there is any, otherwise split on ; , ·"""
    q = re.findall(r"[\"“]([^\"”]{3,})[\"”]", text)
    if q:
        return q
    return [x for x in re.split(r"[;,·]", text) if len(norm(x).split()) >= 2]


def bf_list(text, label):
    """Items under a field label such as 'Retired lines' or 'Never-say' in the Business File."""
    out, on = [], False
    for ln in text.splitlines():
        if re.search(label, ln, re.I):
            on = True
            rest = re.split(r":\*?\*?", ln, maxsplit=1)
            if len(rest) > 1 and norm(rest[1]):
                out += split_items(rest[1])
            continue
        if not on:
            continue
        if not ln.strip():
            continue  # a blank line under the label does not end the list
        if re.match(r"\s*(#|[-*]\s+\*\*|\*\*)", ln) or re.match(r"[-*]\s+\*\*", ln):
            on = False  # the next field or section
            continue
        m = re.match(r"\s*[-*]\s+(.*)", ln)
        if m:
            item = m.group(1).strip()
            if item not in ("—", "-") and len(norm(item).split()) >= 2:
                out += split_items(item) if re.search(r"[\"“]", item) else [item]
            continue
        on = False
    return out


def parse_proof_bank(text):
    """{P-NN: {class, permission, scope}} from a table with a header row, or heading-per-story entries."""
    bank, cols, cur = {}, None, None
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip().strip("*").strip() for c in s.strip("|").split("|")]
            low = [c.lower() for c in cells]
            if "id" in low and (any(c in low for c in ("origin", "class")) or "permission" in low):
                cols = {k: next((i for i, c in enumerate(low) if c in names), None)
                        for k, names in (("id", ("id",)), ("class", ("origin", "class")),
                                         ("permission", ("permission", "consent")), ("scope", ("scope",)))}
                continue
            if cols and cells and re.fullmatch(r"P-\d+", cells[cols["id"]] if cols["id"] is not None and cols["id"] < len(cells) else ""):
                g = lambda k: cells[cols[k]] if cols.get(k) is not None and cols[k] < len(cells) else ""
                bank[g("id")] = {"class": g("class").upper()[:1], "permission": g("permission").lower(), "scope": g("scope").lower() or None}
            continue
        h = re.match(r"\s*#{1,4}\s*(P-\d+)\b", ln) or re.match(r"\s*(?:id:\s*)(P-\d+)\b", ln, re.I)
        if h:
            cur = h.group(1)
            bank.setdefault(cur, {"class": "", "permission": "", "scope": None})
            m = re.search(r"\b(?:class|origin)\s*[:\s]\s*([A-Z])\b", ln, re.I)
            if m:
                bank[cur]["class"] = m.group(1).upper()
            continue
        if cur:
            m = re.match(r"\s*[-*]?\s*\**(class|origin|permission|consent|scope)\**\s*:\s*(.*)", ln, re.I)
            if m:
                k = {"origin": "class", "consent": "permission"}.get(m.group(1).lower(), m.group(1).lower())
                v = m.group(2).strip()
                bank[cur][k] = v.upper()[:1] if k == "class" else v.lower()
            elif re.match(r"\s*#", ln):
                cur = None
    return bank


def deck_text(path):
    with zipfile.ZipFile(path) as z:
        return "\n".join(re.sub(r"<[^>]+>", " ", " ".join(re.findall(r"<a:t>(.*?)</a:t>", z.read(n).decode("utf8", "replace"))))
                         for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))


# ---------------------------------------------------------------- close.md, one reader for every command

CLOSE_SHAPE = """close.md is read one element per line, each line starting with its name:

- **Close mode:** checkout
- **Door 1: The Pricing Program** for owners ready to raise one price. $1,997 in full, or 4 payments of $549 ($2,196 total). Checkout: https://...
- Backup payment link (moderator only): https://...
- **Guarantee (signed off 2026-11-20):** ...
- **Deadline:** enrolment closes January 9, 2027 at midnight Pacific
  (with no deadline: - **Deadline:** none; follow-up ends January 20)

Close mode is checkout, call or both. Two other shapes are read the same way: a heading with its value on the
next line ("## Deadline", then "January 9, 2027 at midnight Pacific"), and a table with two columns, the element
and its value ("| Deadline | January 9, 2027 |"). A table with more columns is not read. What attendees may see
can go under a "## For attendees" heading: the one-pager then copies only that part."""
CLOSE_SHAPE_SHORT = ("Write one element per line, each starting with its name (\"- **Close mode:** checkout\", "
                     "\"- **Deadline:** January 9, 2027\" or \"- **Deadline:** none\"); a heading with its value on the next "
                     "line, or a two-column table of element and value, is read the same way. "
                     "Run webinar_check.py lint --close close.md to see what is read.")
DEADLINE_NAME = r"(?:deadline|enrol?l?ment closes|cart closes|doors close)"
CLOSE_DEADLINE_AT = re.compile(r"(" + DEADLINE_NAME + r")\b(?:\s*\([^)]*\))?\**\s*[:\-–—]?\s*\**(.*)$", re.I)
NO_DEADLINE_AT = re.compile(r"(no deadline)\b\**\s*[:;,.\-–—]?\s*\**(.*)$", re.I)
CLOSE_LABEL = re.compile(r"(?P<label>[A-Za-z][^:|]{0,70}?)\s*\**\s*:(?=\s|\*|$)\**\s*(?P<value>.*)$")
CLOSE_INTERNAL = (  # elements the attendee one-pager never carries
    ("close_mode", re.compile(r"close mode\b", re.I)),
    ("backup", re.compile(r"(?:backup|back-up|fallback|second (?:checkout|payment))\b", re.I)),
    ("signoff", re.compile(r"(?:signed[- ]off|sign[- ]?off|approved by)\b", re.I)),
    ("note", re.compile(r"(?:(?:internal|moderator|team|private|host)(?:[ -]only)?[ ]?)?notes?\b|"
                        r"(?:internal|moderator|team)(?:[ -]only)?$|for the (?:moderator|team)\b", re.I)),
)
CLOSE_MARKED = re.compile(r"moderator only|\(internal\)|internal only", re.I)
CLOSE_HEADER_WORDS = {"", "element", "elements", "field", "item", "name", "what", "key", "part", "value", "values", "detail",
                      "details", "description", "setting", "answer"}
URL = re.compile(r"https?://[^\s)>|]+|\bwww\.[^\s)>|]+", re.I)
SIGNOFF_PAREN = re.compile(r"\s*\((?:as )?signed off[^)]*\)", re.I)
SIGNOFF_TAIL = re.compile(r"\s*[,;]\s*(?:as )?signed off\b[^.;|]*", re.I)
SIGNOFF_AS = re.compile(r"\s*,?\s*as signed off\b", re.I)
UNSAFE_WORDS = re.compile(r"\bsigned[- ]off\b|\bsign-?off\b|\bclose mode\b|moderator only|\(internal\)|internal only", re.I)
BACKUP_WORD = re.compile(r"\b(?:backup|back-up|fallback)\b", re.I)


def _bare(s):
    """A line or a cell without its bullet and its bold or code marks."""
    s = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?", "", s)
    return re.sub(r"^[*_`\s]+|[*_`\s]+$", "", s)


def _close_kind(label):
    """close_mode, backup, signoff, note (all internal), deadline, or other."""
    lab = re.sub(r"\s*\([^)]*\)", "", label).strip()
    for kind, rx in CLOSE_INTERNAL:
        if rx.match(lab):
            return kind
    if re.match(DEADLINE_NAME + r"\b|no deadline\b", lab, re.I):
        return "deadline"
    return "other"


def _close_labelled(line):
    """(name, value) when the line is "Name: value" (or starts with a deadline name), else None."""
    b = _bare(line)
    m = NO_DEADLINE_AT.match(b)
    if m:
        return "Deadline", ("none; " + _bare(m.group(2))).rstrip("; ")
    m = CLOSE_DEADLINE_AT.match(b)
    if m:
        return m.group(1), _bare(m.group(2))
    m = CLOSE_LABEL.match(b)
    if m:
        lab = _bare(m.group("label"))
        if lab and len(lab.split()) <= 8 and not re.search(r"[.!?]\s", lab) and not re.match(r"https?$", lab, re.I):
            return lab, _bare(m.group("value"))
    return None


def close_mode_of(value):
    """checkout, call or both from the Close mode value; None when it says something else."""
    v = (value or "").lower()
    co, ca = bool(re.search(r"\bcheckout\b|\bcart\b", v)), bool(re.search(r"\bcalls?\b|\bapplications?\b|\bbooking\b", v))
    if re.search(r"\bboth\b", v) or (co and ca):
        return "both"
    return "checkout" if co else "call" if ca else None


def _deadline_state(value):
    v = (value or "").strip().strip("*").strip()
    if not v:
        return "empty"
    if re.match(r"(none|no deadline|n/?a)\b", v, re.I) or v in ("—", "-", "–"):
        return "none"
    if re.search(r"\bpending\b", v, re.I):
        return "pending"
    return "set"


def read_close(raw):
    """Read close.md in any of its three accepted shapes into the same elements.

    Returns {"ok", "problems", "elements", "items", "mode", "deadline_state" (set, none, pending), "deadline",
    "pending", "shapes", "attendee_part", "text"}. "ok" is False when the file would not be read correctly:
    "problems" then says, in plain words, what could not be read. PENDING elements are reported, not refused."""
    text = re.sub(r"<!--.*?-->", "", raw or "", flags=re.S)
    text = re.sub(r"\A\s*---[ \t]*\r?\n(?=[A-Za-z_][\w-]*:).*?\r?\n---[ \t]*(?:\r?\n|\Z)", "", text, flags=re.S)  # a vault note's frontmatter
    lines = text.splitlines()
    items, problems = [], []
    internal_level = attendee_level = None
    attendee_part = False
    waiting = None  # a heading still waiting for its value on the next non-blank line

    def add(kind, n, raw_line, **kw):
        it = {"type": kind, "line": n + 1, "raw": raw_line, "internal": internal_level is not None,
              "attendee": attendee_level is not None}
        it.update(kw)
        if kind == "element":
            it["kind"] = _close_kind(it["name"])
            it["internal"] = it["internal"] or it["kind"] in ("close_mode", "backup", "signoff", "note") or bool(CLOSE_MARKED.search(raw_line))
        elif kind == "free":
            b = _bare(raw_line)
            it["internal"] = (it["internal"] or bool(CLOSE_MARKED.search(raw_line))
                              or any(rx.match(b) for k, rx in CLOSE_INTERNAL if k != "note"))
        items.append(it)
        return it

    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            add("blank", i, "")
            i += 1
            continue
        h = re.match(r"\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$", ln)
        if h:
            level, title = len(h.group(1)), _bare(h.group(2))
            if internal_level is not None and level <= internal_level:
                internal_level = None
            if attendee_level is not None and level <= attendee_level:
                attendee_level = None
            waiting = None
            if level == 1:
                add("title", i, ln)
            elif re.fullmatch(r"for (?:the )?attendees", title.rstrip(":"), re.I):
                add("attendee_heading", i, ln)
                attendee_level, attendee_part = level, True
            else:
                lab = _close_labelled(title)
                if lab:  # "## Deadline: January 9"
                    add("element", i, ln, name=lab[0], value=lab[1], shape="line")
                else:
                    kind = _close_kind(title)
                    if kind in ("close_mode", "backup", "signoff", "note"):
                        internal_level = level  # everything under an internal heading stays internal
                    waiting = add("heading", i, ln, name=title, kind=kind)
            i += 1
            continue
        if s.startswith("|"):
            j, rows = i, []
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [_bare(c) for c in lines[j].strip().strip("|").split("|")]
                rows.append((j, lines[j], cells, all(re.fullmatch(r":?-{1,}:?", c.strip()) for c in lines[j].strip().strip("|").split("|"))))
                j += 1
            data = [r for r in rows if not r[3]]
            widths = sorted({len(r[2]) for r in data})
            if widths != [2]:
                head = " | ".join(data[0][2]) if data else ""
                problems.append(f"the table at line {i + 1} has {widths[-1] if widths else 0} column{'s' if not widths or widths[-1] != 1 else ''}"
                                f" ({head[:80]}): with more or fewer than two columns there is no telling which one "
                                "holds the value. Use two columns, the element and its value, or one element per line")
                for r in rows:
                    add("table_unread", r[0], r[1])
            else:
                for k, r in enumerate(rows):
                    if r[3]:
                        add("table_frame", r[0], r[1])
                        continue
                    is_head = (k == 0 and len(rows) > 1 and rows[1][3] and _close_kind(r[2][0]) == "other"
                               and (r[2][0].lower() in CLOSE_HEADER_WORDS or r[2][1].lower() in CLOSE_HEADER_WORDS))
                    if is_head:
                        add("table_frame", r[0], r[1])
                    else:
                        add("element", r[0], r[1], name=r[2][0], value=r[2][1], shape="table")
            waiting = None
            i = j
            continue
        lab = _close_labelled(ln)
        if lab:
            add("element", i, ln, name=lab[0], value=lab[1], shape="line")
        elif waiting is not None:  # the heading's value
            waiting.update(type="element", value=_bare(ln), shape="heading")
            waiting["internal"] = waiting["internal"] or bool(CLOSE_MARKED.search(ln))
            add("value", i, ln, internal=None)
            items[-1]["internal"] = waiting["internal"]
        else:
            add("free", i, ln)
        waiting = None
        i += 1

    elements = [it for it in items if it["type"] == "element"]
    empty_heads = [it for it in items if it["type"] == "heading"]
    pending = [ln.strip() for ln in lines if re.search(r"\bpending\b", ln, re.I)]
    mode = deadline = None
    deadline_state = "missing"
    if not elements and not problems:
        problems.append("nothing in it reads as an element (a name and its value)")
    elif elements or not problems:
        # close mode
        modes = [e for e in elements if e["kind"] == "close_mode"]
        if not modes:
            hd = next((h_ for h_ in empty_heads if h_["kind"] == "close_mode"), None)
            problems.append(f"the heading \"{hd['name']}\" (line {hd['line']}) has no value on the line under it" if hd else
                            "no Close mode element (checkout, call or both)")
        else:
            vals = {close_mode_of(e["value"]) for e in modes if not re.search(r"\bpending\b", e["value"], re.I)}
            if None in vals:
                bad = next(e for e in modes if close_mode_of(e["value"]) is None and not re.search(r"\bpending\b", e["value"], re.I))
                problems.append(f"Close mode says {bad['value']!r} (line {bad['line']}): it must be checkout, call or both")
            elif len(vals) > 1:
                problems.append("Close mode is written more than once with different values (" +
                                ", ".join(f"line {e['line']}: {e['value']}" for e in modes) + ")")
            elif vals:
                mode = vals.pop()
        # deadline
        dls = [e for e in elements if e["kind"] == "deadline"]
        if not dls:
            hd = next((h_ for h_ in empty_heads if h_["kind"] == "deadline"), None)
            problems.append(f"the heading \"{hd['name']}\" (line {hd['line']}) has no value on the line under it" if hd else
                            "no Deadline element (write the deadline, or \"Deadline: none\" when there is none)")
        else:
            states = [(_deadline_state(e["value"]), e) for e in dls]
            st0, e0 = states[0]
            if st0 == "empty":
                problems.append(f"{e0['name']} (line {e0['line']}) has no value: write the deadline, or \"none\"")
            else:
                clash = None
                for st_, e in states[1:]:
                    if {st0, st_} == {"set", "none"} or (st0 == st_ == "set" and dates(e0["value"]) and dates(e["value"])
                                                         and not dates(e0["value"]) & dates(e["value"])):
                        clash = e
                        break
                if clash:
                    problems.append(f"the deadline is written more than once and the lines disagree (line {e0['line']}: "
                                    f"{e0['value'][:50]!r}; line {clash['line']}: {clash['value'][:50]!r})")
                else:
                    deadline_state = st0
                    deadline = e0["value"].strip().strip("*").strip() if st0 in ("set", "none") else None
        # the offer itself, by close mode
        shown = [e for e in elements if not e["internal"] and e["kind"] != "deadline"]
        frees = [it for it in items if it["type"] in ("free", "value") and not it["internal"]]
        shown_txt = "\n".join(it["raw"] for it in shown + frees)
        if mode in ("checkout", "both") and not figures(shown_txt) and not pending:
            problems.append(f"Close mode is {mode} but no price was found outside the internal lines "
                            "(write each door with its price, for example \"- **Door 1: The Program** $1,997\")")
        elif mode == "call" and not shown and not pending:
            problems.append("Close mode is call but no door was found: say what the call or application is, and who it is for")
    return {"ok": not problems, "problems": problems, "elements": elements, "items": items, "mode": mode,
            "deadline_state": deadline_state, "deadline": deadline, "pending": pending,
            "shapes": sorted({e["shape"] for e in elements}), "attendee_part": attendee_part, "text": text}


def load_close(path):
    """read_close() on a file; a file that cannot be opened comes back as not ok, with the reason."""
    try:
        raw = Path(path).read_text()
    except Exception as e:
        return {"ok": False, "problems": [f"cannot read {path}: {e}"], "elements": [], "items": [], "mode": None,
                "deadline_state": "missing", "deadline": None, "pending": [], "shapes": [], "attendee_part": False,
                "text": "", "unreadable": True}
    return read_close(raw)


def close_refusal(rc, short=False):
    """The plain message for a close.md that would not be read correctly."""
    return ("close.md was not read: " + "; ".join(rc["problems"]) + "." +
            (" " + CLOSE_SHAPE_SHORT if short else "\n\n" + CLOSE_SHAPE))


def close_onepager(rc):
    """What attendees may see, from a close.md read_close() accepted: (lines, left_out, problems).

    The "## For attendees" part when there is one, otherwise everything. Either way without the close mode, backup
    links, sign-off notes, internal notes and anything marked "moderator only" or "(internal)". "problems" is not
    empty when a line cannot be told safe from internal: nothing is then published."""
    src = [it for it in rc["items"] if it["attendee"]] if rc["attendee_part"] else rc["items"]
    keep, left, problems = [], [], []
    for it in src:
        t = it["type"]
        if t in ("title", "attendee_heading", "table_frame"):
            if t == "title":
                left.append(it["raw"])
            continue
        if t == "blank":
            keep.append("")
            continue
        if it["internal"] or t == "table_unread":
            left.append(it["raw"])
            continue
        out = f"- **{it['name']}:** {it['value']}" if t == "element" and it["shape"] == "table" else it["raw"]
        out = SIGNOFF_AS.sub("", SIGNOFF_TAIL.sub("", SIGNOFF_PAREN.sub("", out)))
        keep.append(out.rstrip())
    hidden = {u.rstrip(".,;") for it in rc["items"] if it["internal"] for u in URL.findall(it["raw"])}
    for ln in keep:
        if UNSAFE_WORDS.search(ln):
            problems.append(f"this line mixes an internal note with attendee wording: {ln.strip()[:120]!r}")
        elif (BACKUP_WORD.search(ln) and URL.search(ln)) or any(u.rstrip(".,;") in hidden for u in URL.findall(ln)):
            problems.append(f"this line carries a backup or internal link: {ln.strip()[:120]!r}")
    if not any(ln.strip() for ln in keep):
        problems.append("the \"## For attendees\" part is empty" if rc["attendee_part"] else "nothing is left for attendees to read")
    while keep and not keep[0].strip():
        keep.pop(0)
    while keep and not keep[-1].strip():
        keep.pop()
    return keep, left, problems


def describe_close(rc):
    """The elements as read, in plain words, one per line."""
    out = []
    for e in rc["elements"]:
        tag = {"close_mode": "internal", "backup": "internal", "signoff": "internal", "note": "internal"}.get(e["kind"]) or \
              ("internal" if e["internal"] else "")
        out.append(f"  {e['name']}: {e['value'] or '(no value)'}" + (f"  [{tag}: kept off the one-pager]" if tag else ""))
    return out


def run_lint(a):
    """lint --close close.md: what the scripts read from close.md; exit 1 when it would not be read correctly."""
    rc = load_close(a.close)
    keep, left, unsafe = close_onepager(rc) if rc["ok"] else ([], [], [])
    ok = rc["ok"] and not unsafe
    if a.json:
        print(json.dumps({"ok": ok, "problems": rc["problems"] + unsafe, "close_mode": rc["mode"],
                          "deadline": rc["deadline"], "deadline_state": rc["deadline_state"], "shapes": rc["shapes"],
                          "elements": [{"name": e["name"], "value": e["value"], "internal": e["internal"], "line": e["line"]}
                                       for e in rc["elements"]], "pending": rc["pending"], "one_pager": keep}, indent=2))
        sys.exit(0 if ok else 2 if rc.get("unreadable") else 1)
    if rc.get("unreadable"):
        print(rc["problems"][0])
        sys.exit(2)
    if rc["elements"]:
        print(f"Read from {a.close} ({len(rc['elements'])} elements):")
        print("\n".join(describe_close(rc)))
        print()
    if not rc["ok"]:
        print("NOT READ CORRECTLY. " + close_refusal(rc))
        sys.exit(1)
    print("Close mode: " + (rc["mode"] or "still PENDING"))
    print("Deadline: " + {"set": rc["deadline"] or "", "none": "none (" + (rc["deadline"] or "none") + ")",
                          "pending": "still PENDING"}[rc["deadline_state"]])
    if unsafe:
        print("\nNOT SAFE TO SHOW ATTENDEES. " + "; ".join(unsafe) + ".\nPut each internal note on a line of its own that "
              "starts with Backup, Close mode, Signed off or Notes, or put the attendee wording under a \"## For attendees\" heading.")
        sys.exit(1)
    print(f"\nThe one-pager would show attendees these {sum(1 for x in keep if x.strip())} lines"
          + (" (the \"## For attendees\" part):" if rc["attendee_part"] else ":"))
    print("\n".join("  " + x for x in keep if x.strip()))
    if rc["pending"]:
        print(f"\n{len(rc['pending'])} line(s) still PENDING: the check holds and the one-pager is not written until the "
              "member settles them.")
    print("\nOK: close.md reads correctly.")
    sys.exit(0)


def run(a):
    try:
        spec = json.loads(Path(a.spec).read_text())
        segs = spec["segments"]
        assert isinstance(segs, list) and segs
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"cannot read {a.spec}: {e}"}))
        sys.exit(2)
    items = []

    def item(cid, ok, detail, level="critical"):
        items.append({"id": cid, "level": level, "ok": bool(ok), "detail": detail})

    rec = bool(spec.get("recorded"))
    L = spec.get("length_min") or 60
    close_kind = spec.get("close", "checkout")
    early_day = spec.get("format") == "bootcamp" and (spec.get("day") or 3) < 3
    body = [s for s in segs if s.get("kind") != "lobby"]
    st, t = {}, 0
    for s in body:
        st[s.get("id")] = t
        t += s.get("min", 0)
    top = "\n".join(strings({k: spec.get(k) for k in ("title", "promise", "big_idea", "not_covering", "beliefs")}))
    qa_txt = "\n".join(strings(spec.get("qa_bank")))
    all_txt = "\n".join([top, qa_txt] + [seg_text(s) for s in segs])
    dk_txt = page_txt = ""
    if a.deck:
        try:
            dk_txt = deck_text(a.deck)
        except Exception as e:
            item("deck_font_min", False, f"cannot read the deck {a.deck}: {e}")
    if a.page:
        try:
            page_txt = Path(a.page).read_text()
        except Exception as e:
            item("page_discloses", False, f"cannot read {a.page}: {e}")
    everything = "\n".join([all_txt, dk_txt, page_txt])

    # placeholders
    ph = [s for s in strings(spec) if PLACEHOLDER.search(s)]
    item("placeholders_filled", not ph, "nothing left to write" if not ph else f"{len(ph)} placeholder(s) left, e.g. {ph[0][:80]!r}")

    # length and the hard stop (an early bootcamp day may end on its recap)
    last = body[-1].get("kind") if body else None
    ends = ("close", "recap") if early_day else ("close",)
    ok = t <= L and last in ends
    item("length_fits", ok, f"{t} of {L} minutes, ending on the {last}" if ok else
         (f"the blocks add up to {t} minutes, over the {L} promised" if t > L else
          "the last block is not the close (the hard stop)" + (" or the recap" if early_day else "")))

    # offer disclosed on the agenda
    prom = next((s for s in segs if s.get("kind") == "promise"), None)
    ptxt = seg_text(prom) if prom else ""
    said = bool(re.search(r"\boffer\b|how (i|we) can help|invit|\bcall\b" if close_kind != "checkout" else
                          r"\boffer\b|how (i|we) can help|invit", ptxt, re.I))
    ok = bool(spec.get("offer_disclosed")) and said
    item("offer_disclosed", ok, "the agenda says there will be an offer" if ok else
         "the promise and agenda block must say plainly that there will be an offer (and offer_disclosed: true)")

    nc = [x for x in (spec.get("not_covering") or []) if str(x).strip()]
    item("objections_named", len(nc) >= 3, f"{len(nc)} objections set aside on the agenda" if len(nc) >= 3 else
         f"only {len(nc)} objections on the agenda; name three to five real ones")
    bl = [b for b in (spec.get("beliefs") or []) if str(b.get("false", "")).strip() and str(b.get("true", "")).strip()]
    item("three_beliefs", len(bl) == 3, "three beliefs, each false and true" if len(bl) == 3 else f"{len(bl)} complete beliefs; the talk needs three")

    # loops
    bad = []
    for s in segs:
        if s.get("kind") != "teach":
            continue
        lp = s.get("loop") or {}
        if not str(lp.get("question", "")).strip() or not str(lp.get("answer", "")).strip():
            bad.append(f"{s.get('id')}: no loop question and answer")
        m = OPEN_LOOP.search(seg_text(s))
        if m:
            bad.append(f"{s.get('id')}: leaves the loop open ({m.group(0)!r})")
    item("loops_closed", not bad, "every teaching block closes its own loop" if not bad else "; ".join(bad))

    # the offer against close.md: money, dates, payment counts, places; PENDING
    close_txt = ""
    if a.close:
        try:
            close_txt = re.sub(r"<!--.*?-->", "", Path(a.close).read_text(), flags=re.S)
        except Exception as e:
            item("offer_matches_close", False, f"cannot read {a.close}: {e}")
    offer_txt = "\n".join([top, qa_txt, dk_txt, page_txt] + [seg_text(s) for s in segs if s.get("kind") in OFFER_KINDS])
    other = [(s.get("id"), seg_text(s)) for s in segs if s.get("kind") not in OFFER_KINDS]
    if a.close and close_txt:
        prob = []
        if not any(s.get("kind") == "offer" for s in segs) and not early_day:
            prob.append("no offer block")
        pend = [ln.strip() for ln in close_txt.splitlines() if re.search(r"\bpending\b", ln, re.I)]
        if pend:
            prob.append(f"close.md still has {len(pend)} PENDING element(s): {pend[0][:70]!r}")
        allowed = figures(close_txt)
        stray = sorted(figures(offer_txt) - allowed, key=float)
        if stray:
            prob.append("figures not in close.md: " + ", ".join("$" + x for x in stray[:6]))
        if MONEY_WORDS.search(offer_txt):
            prob.append(f"a price written in words ({MONEY_WORDS.search(offer_txt).group(0)!r}): write it as close.md has it")
        early = [f"{sid} ({', '.join('$' + x for x in sorted(figures(tx) & allowed, key=float))})"
                 for sid, tx in other if figures(tx) & allowed]
        if early:
            prob.append("a price from close.md said before the offer, in " + "; ".join(early))
        try:
            own = {(int(spec["date"][5:7]) - 1, int(spec["date"][8:10]))}
        except (KeyError, ValueError, TypeError):
            own = set()
        sd = dates(everything) - dates(close_txt) - own
        if sd:
            prob.append("dates not in close.md: " + ", ".join(f"{MONTHS[m_].capitalize()} {d_}" for m_, d_ in sorted(sd)))
        sp_ = payments(everything) - payments(close_txt)
        if sp_:
            prob.append("payment counts not in close.md: " + ", ".join(f"{n} payments" for n in sorted(sp_)))
        pl = places(everything) - places(close_txt)
        if pl:
            prob.append("place counts not in close.md: " + ", ".join(sorted(pl)))
        item("offer_matches_close", not prob, "every price, date, payment count and place count matches close.md" if not prob
             else "; ".join(prob))
    elif not a.close:
        item("offer_matches_close", False, "give --close launches/<slug>/close.md: the offer is checked against it word for word")

    # deadline
    has_dl, dl_val = close_deadline(close_txt)
    dl_hits = [m.group(0) for m in DEADLINE.finditer(everything)
               if not HONEST_WINDOW.search(everything[max(0, m.start() - 60): m.end() + 40])]
    rel = [m.group(0) for m in RELATIVE_DAY.finditer(everything)
           if DEADLINE.search(everything[max(0, m.start() - 50): m.end() + 50])]
    prob = []
    if dl_hits and not has_dl:
        prob.append(f"the talk says {dl_hits[0]!r} but close.md has no deadline" + (f" (it says {dl_val!r})" if dl_val else ""))
    if rel and has_dl:
        prob.append(f"say the deadline as a date, as close.md has it ({dl_val[:60]!r}), not {rel[0]!r}")
    item("deadline_real", not prob, ("the deadline is the one in close.md" if dl_hits else "no deadline mentioned") if not prob
         else "; ".join(prob))

    # proof
    bank = {}
    if a.proof:
        try:
            bank = parse_proof_bank(Path(a.proof).read_text())
        except Exception as e:
            item("proof_classified", False, f"cannot read {a.proof}: {e}")
    pb, n_proof = [], 0
    for s in segs:
        pl_ = s.get("proof") or []
        if s.get("kind") in ("guest", "proof") and not pl_:
            pb.append(f"{s.get('id')}: a {s.get('kind')} block with no proof ID")
        for p in pl_:
            n_proof += 1
            pid, cl = str(p.get("id", "")), str(p.get("class", "")).upper()
            if not re.fullmatch(r"P-\d+", pid):
                pb.append(f"{s.get('id')}: proof without a P-NN ID")
                continue
            if cl not in ALLOWED_CLASSES:
                pb.append(f"{pid}: class {cl or '(none)'} cannot be used as proof (X is an illustration, U unconfirmed, R retired)")
            if cl == "D" and "paid" not in str(p.get("label", "")).lower():
                pb.append(f"{pid}: a paid-program result (D) needs label \"paid-program result\" and is introduced as one")
            if cl in NEEDS_TYPICAL and not str(p.get("typical", "")).strip():
                pb.append(f"{pid}: a class {cl} story needs the typical result beside it")
            if a.proof:
                e = bank.get(pid)
                if not e:
                    pb.append(f"{pid}: not in the proof bank" + ("" if bank else " (no P-NN entries found in it: cite the Proof "
                                                                                 "Engine's IDs with their class and permission)"))
                    continue
                if not e["class"] or not e["permission"]:
                    pb.append(f"{pid}: the proof bank gives no {'class' if not e['class'] else 'permission'} for it")
                if e["class"] and cl and e["class"] != cl:
                    pb.append(f"{pid}: class {cl} here but {e['class']} in the proof bank")
                if e["permission"] and not re.match(r"(named|anonymous)\b", e["permission"]):
                    pb.append(f"{pid}: permission is {e['permission']}")
                if e["scope"] and e["scope"] not in ("—", "-") and "event" not in e["scope"]:
                    pb.append(f"{pid}: its scope ({e['scope']}) does not include events")
    if n_proof and not a.proof:
        pb.append("give --proof launches/<slug>/proof-bank.md so each ID is checked")
    item("proof_classified", not pb, (f"{n_proof} proof stor{'y' if n_proof == 1 else 'ies'}, each with an ID, an allowed class "
                                      "and its permission" if n_proof else "no proof stories (the member's own story and the "
                                      "method shown live)") if not pb else "; ".join(pb))

    # earnings and performance figures outside the offer (the promise and title included)
    eb = []
    for sid, tx, sg in [("title/promise", top, {})] + [(s.get("id"), seg_text(s), s) for s in segs
                                                         if s.get("kind") not in ("offer", "qa", "close", "lobby")]:
        if (MONEY.search(tx) or PCT.search(tx)) and EARN.search(tx):
            if not (sg.get("typical") or any(str(p.get("typical", "")).strip() for p in sg.get("proof") or [])):
                eb.append(sid)
    item("earnings_typical", not eb, "no earnings figure without the typical result" if not eb else
         f"earnings or growth figures without the typical result in: {', '.join(map(str, eb))}")

    # retired lines and never-say claims
    if a.business_file:
        try:
            bft = Path(a.business_file).read_text()
            ret = bf_list(bft, r"Retired lines") + bf_list(bft, r"Never-say")
            hay = norm(everything)
            hit = [r for r in ret if norm(r) and norm(r) in hay]
            item("retired_lines", not hit, f"none of {len(ret)} retired or never-say lines used" if not hit else
                 "uses retired or never-say lines: " + "; ".join(h[:60] for h in hit))
        except Exception as e:
            item("retired_lines", False, f"cannot read {a.business_file}: {e}")
    else:
        item("retired_lines", False, "give --business-file so §1 Retired lines and §18 Never-say are checked")

    # refused tactics
    hits = [f"{code}: {rx.search(everything).group(0)!r}" for code, rx in REFUSED.items() if rx.search(everything)]
    if rec and LIVE_CLAIM.search(everything):
        hits.append(f"live_claim on a recording: {LIVE_CLAIM.search(everything).group(0)!r}")
    item("refused_tactics", not hits, "none of the refused tactics" if not hits else "; ".join(hits) +
         (" (a cap of places is said as the cap, \"12 places\"; the moderator gives the live count from the checkout)"
          if any(h.startswith("fake_scarcity") for h in hits) else ""))

    # recording notice
    spoken = lambda s: "\n".join(strings({k: s.get(k) for k in ("say", "notes", "chat_prompt", "slides")}))
    early = "\n".join(spoken(s) for s in body if st.get(s.get("id"), 99) < 5)
    if rec:
        ok = bool(re.search(r"\brecording of\b|\bthis is a recording\b|\brecorded (session|version|earlier)\b", early, re.I))
        item("recording_notice", ok, "labelled as recorded in the opening" if ok else
             "a recorded version must say in its opening that it is a recording of a session run live")
    else:
        ok = bool(re.search(r"\brecord", early, re.I))
        item("recording_notice", ok, "the recording is announced in the first minutes" if ok else
             "say in the first five minutes that the session is recorded (some US states need everyone's consent)")

    # the registration page
    if a.page and page_txt:
        prob = []
        if not re.search(r"\boffer\b", page_txt, re.I):
            prob.append("it does not say there will be an offer at the end")
        if rec and not re.search(r"\brecorded\b|\brecording\b", page_txt, re.I):
            prob.append("a recorded version must say so on the page")
        if not rec and not re.search(r"\brecord", page_txt, re.I):
            prob.append("it does not say the session is recorded")
        item("page_discloses", not prob, "the page says there is an offer and that it is recorded" if not prob else "; ".join(prob))

    # Q&A bank
    have = {}
    for q in spec.get("qa_bank") or []:
        ans = str(q.get("answer", "")).strip()
        if not ans or PLACEHOLDER.search(ans):
            continue
        o = (str(q.get("objection", "")) + " " + str(q.get("question", ""))).lower()
        for k, syn in OBJ_SYNONYMS.items():
            if any(w in o for w in syn):
                have[k] = True
    miss = [k for k in OBJ_SYNONYMS if k not in have]
    item("qa_bank_covers", not miss, "time, money, confidence and the spouse are answered" if not miss else
         "the Q&A bank has no written answer for: " + ", ".join(miss))

    # moderator
    roles = spec.get("roles") or {}
    mod, host = str(roles.get("moderator", "")).strip(), str(roles.get("host", "")).strip()
    ok = bool(mod) and not PLACEHOLDER.search(mod) and not re.fullmatch(r"\[.*\]", mod) and (rec or mod.lower() != host.lower())
    item("moderator_named", ok, f"moderator: {mod}" if ok else
         ("the presenter cannot also moderate; name someone else" if mod and mod.lower() == host.lower() else
          "name the moderator (a spouse, an assistant or a member of the cohort)"))

    # deck
    if a.deck and dk_txt:
        rep = slide_builder.inspect(a.deck)
        sp = rep["smallest_pt"]
        lc = rep["lowest_contrast"]
        item("deck_font_min", sp is None or sp >= slide_builder.MIN_PT,
             f"smallest type {sp}pt" if sp else "type sizes not set in the slides: check by eye")
        item("deck_contrast_min", lc is None or lc >= slide_builder.MIN_CONTRAST,
             f"lowest contrast {lc}:1" if lc else "colours not set in the slides: check by eye")
        sh = [f"slide {s['slide']}: {p['what']}" for s in rep["slides"] for p in s["problems"] if p["level"] == "should"]
        item("deck_font_target", not any("pt" in x for x in sh), "; ".join(x for x in sh if "pt" in x) or "type at target sizes", "advisory")
        item("deck_contrast_target", not any("contrast" in x for x in sh), "; ".join(x for x in sh if "contrast" in x) or "contrast at 7:1 or more", "advisory")
        item("deck_words", not any("words" in x for x in sh), "; ".join(x for x in sh if "words" in x) or "one idea a slide", "advisory")

    # advisories
    nochat = [s.get("id") for s in body if s.get("kind") in ("agreement", "teach") and not str(s.get("chat_prompt", "")).strip()]
    item("chat_prompts", not nochat, "a chat prompt in the opening and in every teaching block" if not nochat else
         "no chat prompt in: " + ", ".join(map(str, nochat)), "advisory")
    off = next((s for s in body if s.get("kind") == "offer"), None)
    if off or not early_day:
        item("offer_asks", bool(off) and (off.get("asks") or 0) >= 3, "the offer is asked for three times" if off and
             (off.get("asks") or 0) >= 3 else "ask for the offer three times (\"asks\": 3), with the link on screen and in the chat",
             "advisory")
    story = next((s for s in body if s.get("kind") == "story"), None)
    item("story_length", not story or story.get("min", 0) <= max(8, L // 8), "the story is short and resolved" if not story or
         story.get("min", 0) <= max(8, L // 8) else f"the story runs {story.get('min')} minutes; resolve it faster", "advisory")
    if off:
        om = st.get(off.get("id"), 0)
        item("offer_by_minute", om <= L * 0.75, f"the offer starts at minute {om}" if om <= L * 0.75 else
             f"the offer starts at minute {om} of {L}; little time left for questions", "advisory")
    item("not_your_fault", not NOT_FAULT.search(everything), "no \"it's not your fault\"" if not NOT_FAULT.search(everything) else
         "\"it's not your fault\" is overused; agree with where they are, then change the rules around it", "advisory")
    item("buyer_names", not BUYER_NAMES.search(everything), "no buyers' names read out" if not BUYER_NAMES.search(everything) else
         "first names only, with permission, or \"people are joining\"", "advisory")

    hold = [i for i in items if i["level"] == "critical" and not i["ok"]]
    adv = [i for i in items if i["level"] == "advisory" and not i["ok"]]
    res = {"result": "HOLD" if hold else "GO", "version": spec.get("version", 1), "recorded": rec,
           "critical_open": [i["id"] for i in hold], "advisory_open": [i["id"] for i in adv], "items": items,
           "say": (f"HOLD: {len(hold)} critical item{'s' if len(hold) != 1 else ''} open: " + ", ".join(i["id"] for i in hold))
           if hold else ("GO: every critical item passes." + (f" {len(adv)} advisory item(s) worth fixing." if adv else ""))}
    if a.out:
        md = [f"# Webinar check: {spec.get('title')} (version {spec.get('version', 1)})", "", f"**{res['say']}**", "",
              "| Item | Level | Result | Detail |", "|---|---|---|---|"]
        for i in items:
            md.append(f"| `{i['id']}` | {i['level']} | {'PASS' if i['ok'] else ('HOLD' if i['level'] == 'critical' else 'WATCH')} | "
                      f"{i['detail'].replace('|', '/')} |")
        md += ["", "The script catches words, not intent: read every block for the same things said another way."]
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text("\n".join(md) + "\n")
    print(json.dumps(res, indent=2))
    sys.exit(1 if hold else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Webinar Builder: the go-live check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--spec", required=True)
    c.add_argument("--close")
    c.add_argument("--proof")
    c.add_argument("--business-file")
    c.add_argument("--page")
    c.add_argument("--deck")
    c.add_argument("--out")
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
