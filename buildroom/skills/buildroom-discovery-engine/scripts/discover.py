#!/usr/bin/env python3
"""Deep Discovery helper: the findings ledger for a member's own business.

It never reads the contents of a member's files and never goes online. It lists file names so the member
can agree what gets read, then checks, compares and prints what the session wrote into the ledger.

  discover.py inventory FOLDER [--exclude NAME ...] [--max N] [--json]
  discover.py check LEDGER.json          every finding has a source and an honest confidence
  discover.py conflicts LEDGER.json      findings that disagree with each other
  discover.py gaps LEDGER.json [--cap N] the few questions worth asking, most important first
  discover.py ready LEDGER.json          readiness score: a guide, not a measurement
  discover.py page LEDGER.json           the "What I found" page, as markdown

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
    ("1.tools", 1, "Tools", 3, True, "Which tools do you use for email, your CRM, your website and automation?"),
    ("2.profile", 2, "Best client, in one line", 9, False, "Describe your best client in one line: who they are and the situation they are in."),
    ("2.pains", 2, "Pains", 9, True, "What is your best client struggling with when they come to you?"),
    ("2.dream", 2, "Dream state", 7, False, "What does your client want life or business to look like after working with you?"),
    ("2.trigger", 2, "Buying trigger", 6, False, "What usually happens that makes a client decide to act now?"),
    ("2.objections", 2, "Objections", 7, True, "What do people say, or think, when they hesitate to buy?"),
    ("2.negative", 2, "Who I do not serve", 4, False, "Who do you turn away, and why?"),
    ("2.language", 2, "Client words (exact phrases)", 8, True, "What exact words do your clients use to describe the problem? A phrase or two is enough."),
    ("3.offer_name", 3, "Offer name", 6, False, "What is your main offer called?"),
    ("3.promise", 3, "Core promise", 9, False, "What do you promise a client, in one sentence?"),
    ("3.structure", 3, "How the engagement runs", 6, False, "How long does the work run, and in what format?"),
    ("3.deliverables", 3, "Deliverables", 6, True, "What does a client actually receive?"),
    ("3.guarantee", 3, "Guarantee", 7, False, "Do you offer a guarantee? If so, what is the exact wording?"),
    ("4.alternative", 4, "What clients would do without me", 6, False, "If you did not exist, what would your best client do instead?"),
    ("4.category", 4, "Market category", 5, False, "What would a client call the kind of thing you sell?"),
    ("4.differentiator", 4, "What makes me different", 8, False, "What do you do differently from the others your clients could choose?"),
    ("x.story", 0, "Origin story", 5, False, "Why did you start this business?"),
    ("x.voice", 0, "Voice samples (my own writing or talking)", 7, True, "Can you point me to something you wrote or said that sounds most like you?"),
    ("x.proof", 0, "Proof (real client results)", 8, True, "What is one real result a client got? Numbers if you have them."),
]
FIELD = {f[0]: f for f in FIELDS}
SECTIONS = {1: "Business Snapshot", 2: "Ideal Client", 3: "Offer", 4: "Positioning", 0: "Voice, proof and story"}
KINDS = ("file", "web", "member", "hypothesis")
CONF = {"confirmed": 1.0, "likely": 0.7, "inferred": 0.25}
# Fields that must be at least "likely" before a straight run through the build sessions is worth offering.
CORE = ("1.what_i_do", "1.who_i_serve", "1.core_result", "3.promise")
READY_AT = 70

READABLE = {".md", ".markdown", ".txt", ".docx", ".doc", ".pdf", ".rtf", ".csv", ".html", ".htm", ".pptx", ".vtt", ".srt"}
SKIP_DIRS = {"node_modules", "backups", "__pycache__", "venv"}
SENSITIVE = re.compile(r"(passw|secret|credential|\.env|api[-_ ]?key|token|\btax|bank|statement|passport|\bssn\b|social[-_ ]security|"
                       r"medical|health|payroll|salary|divorce|\bwill\b|license[-_ ]?scan|\bid[-_ ]?card)", re.I)
RELEVANT = [(r"offer|program|package|pricing|price|proposal|sales[-_ ]?page", 5), (r"client|customer|avatar|ica|audience|persona", 5),
            (r"testimonial|review|case[-_ ]?stud|result|win", 5), (r"about|bio|story|mission|values|compass", 4),
            (r"transcript|call|interview|podcast|webinar|talk|speech", 4), (r"position|messag|brand|voice|copy|email|newsletter|post", 3),
            (r"funnel|lead|marketing|plan|strategy|business", 2), (r"sop|process|onboard|faq", 2)]


def norm(v):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s$%.]", " ", str(v).lower())).strip(" .")


def numbers(v):
    return sorted({n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", str(v))})


def same(field, a, b):
    """Two values say the same thing. Prices compare on their numbers, everything else on its words."""
    if field == "1.price" and (numbers(a) or numbers(b)):
        return numbers(a) == numbers(b)
    return norm(a) == norm(b)


def origin(src):
    """What counts as one independent source: a website (by host) or a single file."""
    ref = str(src.get("ref", "")).strip().lower()
    if src.get("kind") == "web":
        m = re.match(r"https?://([^/]+)", ref)
        return "web:" + (m.group(1)[4:] if m and m.group(1).startswith("www.") else m.group(1) if m else ref)
    return f"{src.get('kind')}:{ref}"


def load(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the ledger: {e}")
    if not isinstance(d, dict) or not isinstance(d.get("findings"), list):
        sys.exit('The ledger must be an object with a "findings" list.')
    return d


def problems(d):
    out, seen = [], set()
    fs = d["findings"]
    for i, f in enumerate(fs):
        tag = f"finding {f.get('id', i + 1)}"
        if not isinstance(f, dict):
            out.append(f"{tag}: not an object")
            continue
        if f.get("id") in seen:
            out.append(f"{tag}: id used twice")
        seen.add(f.get("id"))
        if f.get("field") not in FIELD:
            out.append(f"{tag}: unknown field {f.get('field')!r}")
        if not str(f.get("value", "")).strip():
            out.append(f"{tag}: no value")
        src = f.get("source") if isinstance(f.get("source"), dict) else {}
        kind, ref = src.get("kind"), str(src.get("ref", "")).strip()
        if kind not in KINDS:
            out.append(f"{tag}: source kind must be one of {', '.join(KINDS)}")
        elif kind == "web" and not re.match(r"https?://\S+\.\S+", ref):
            out.append(f"{tag}: a web source needs its full address")
        elif kind == "file" and not ref:
            out.append(f"{tag}: a file source needs the file's path")
        elif kind == "hypothesis" and not ref:
            out.append(f"{tag}: a hypothesis needs a note on what it was reasoned from")
        conf = f.get("confidence")
        if conf not in CONF:
            out.append(f"{tag}: confidence must be confirmed, likely or inferred")
        elif kind == "hypothesis" and conf != "inferred":
            out.append(f"{tag}: a hypothesis can only be 'inferred'")
        elif conf == "confirmed" and kind in ("file", "web"):
            others = {origin(g["source"]) for g in fs if isinstance(g, dict) and g is not f and g.get("field") == f.get("field")
                      and isinstance(g.get("source"), dict) and g["source"].get("kind") in ("file", "web", "member")
                      and same(f.get("field"), g.get("value"), f.get("value"))} - {origin(src)}
            if not others:
                out.append(f"{tag}: 'confirmed' needs the member's word or a second independent source; one source is 'likely'")
        if f.get("field") in ("2.language", "x.voice", "x.proof") and kind in ("file", "web") and not str(f.get("quote", "")).strip():
            out.append(f"{tag}: client words, voice samples and proof need the exact quote")
    scope = d.get("scope")
    if not (isinstance(scope, dict) and isinstance(scope.get("agreed"), str) and scope["agreed"].strip()):
        out.append('scope: record when the member agreed what could be read ("scope": {"agreed": "date and what they said"})')
    return out


def by_field(d):
    out = {}
    for f in d["findings"]:
        if isinstance(f, dict) and f.get("field") in FIELD:
            out.setdefault(f["field"], []).append(f)
    return out


def find_conflicts(d):
    """Single-answer fields where real sources disagree and the member has not settled it."""
    out = []
    for key, fs in by_field(d).items():
        if FIELD[key][4]:
            continue
        if any(f["source"].get("kind") == "member" for f in fs if isinstance(f.get("source"), dict)):
            continue
        real = [f for f in fs if isinstance(f.get("source"), dict) and f["source"].get("kind") in ("file", "web")]
        groups = []
        for f in real:
            for g in groups:
                if same(key, g[0]["value"], f["value"]):
                    g.append(f)
                    break
            else:
                groups.append([f])
        if len(groups) > 1:
            out.append((key, groups))
    return out


def best(fs):
    """The strongest finding for a field: the member's word first, then confidence."""
    return max(fs, key=lambda f: (f["source"].get("kind") == "member", CONF.get(f.get("confidence"), 0)))


def credit(d):
    conflicted = {k for k, _ in find_conflicts(d)}
    out = {}
    for key, fs in by_field(d).items():
        ok = [f for f in fs if isinstance(f.get("source"), dict) and f.get("confidence") in CONF]
        if ok:
            c = CONF[best(ok)["confidence"]]
            out[key] = min(c, CONF["inferred"]) if key in conflicted else c
    return out


def gap_list(d, cap):
    cr, bf = credit(d), by_field(d)
    conflicted = dict(find_conflicts(d))
    rows = []
    for key, _sec, label, weight, _multi, question in FIELDS:
        if key in conflicted:
            opts = " or ".join(f"“{g[0]['value']}” ({src_text(g[0])})" for g in conflicted[key])
            rows.append((0, -weight, key, f"{label}: I found {opts}. Which is right today?"))
        elif cr.get(key, 0) < CONF["likely"]:
            known = bf.get(key)
            if known:
                b = best(known)
                rows.append((1 if key in CORE else 2, -weight, key, f"{label}: my best guess is “{b['value']}” ({src_text(b)}). Is that right? If not: {question}"))
            else:
                rows.append((1 if key in CORE else 2, -weight, key, question))
    rows.sort()
    return rows[:cap], rows[cap:]


def score(d):
    cr = credit(d)
    total = sum(f[3] for f in FIELDS)
    pct = round(100 * sum(f[3] * cr.get(f[0], 0) for f in FIELDS) / total)
    weak = [FIELD[k][2] for k in CORE if cr.get(k, 0) < CONF["likely"]]
    return pct, weak


def src_text(f):
    s = f.get("source", {})
    kind, ref = s.get("kind"), str(s.get("ref", ""))
    return {"member": "you told me", "hypothesis": f"my guess, from {ref}", "web": ref, "file": f"your file {ref}"}.get(kind, ref)


def cmd_inventory(a):
    root = Path(a.folder).expanduser()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    excl = {e.lower().strip("/") for e in a.exclude}
    rows, skipped, sensitive = [], 0, []
    for dp, dns, fns in os.walk(root):
        rel_dir = Path(dp).relative_to(root)
        dns[:] = [x for x in dns if not x.startswith(".") and x.lower() not in SKIP_DIRS and x.lower() not in excl
                  and str(rel_dir / x).lower() not in excl]
        for fn in fns:
            p = Path(dp) / fn
            rel = str(p.relative_to(root))
            if fn.startswith(".") or p.suffix.lower() not in READABLE or p.is_symlink():
                skipped += 1
                continue
            if SENSITIVE.search(rel):
                sensitive.append(rel)
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            rel_score = sum(w for pat, w in RELEVANT if re.search(pat, rel, re.I))
            rows.append({"path": rel, "kb": round(st.st_size / 1024, 1), "modified": time.strftime("%Y-%m-%d", time.localtime(st.st_mtime)),
                         "relevance": rel_score})
    rows.sort(key=lambda r: (-r["relevance"], -int(r["modified"].replace("-", ""))))
    shown = rows[:a.max]
    if a.json:
        print(json.dumps({"folder": str(root), "files": shown, "more": len(rows) - len(shown), "sensitive_not_listed_for_reading": sorted(sensitive),
                          "other_files_skipped": skipped}, indent=1))
        return
    print(f"Folder: {root}\nFiles I could read: {len(rows)} (showing {len(shown)}, most useful first). Nothing has been opened yet.\n")
    for r in shown:
        print(f"  {r['modified']}  {r['kb']:>8} KB  {r['path']}")
    if len(rows) > len(shown):
        print(f"\n  ... and {len(rows) - len(shown)} more.")
    if sensitive:
        print(f"\nLooks private, so I will NOT read these unless you tell me to ({len(sensitive)}):")
        for s in sorted(sensitive)[:25]:
            print(f"  {s}")
    print(f"\nOther files skipped (hidden, or a type I do not read): {skipped}")
    print("Tell me any folder or file to leave out before I read anything.")


def cmd_check(a):
    d = load(a.ledger)
    probs = problems(d)
    for p in probs:
        print("FIX  " + p)
    print(f"{len(d['findings'])} findings, {len(probs)} to fix.")
    sys.exit(1 if probs else 0)


def cmd_conflicts(a):
    d = load(a.ledger)
    cs = find_conflicts(d)
    if not cs:
        print("No disagreements between sources.")
        return
    for key, groups in cs:
        print(f"{FIELD[key][2]}:")
        for g in groups:
            print(f"  “{g[0]['value']}”  from " + "; ".join(src_text(f) + (f" ({f['source']['date']})" if f["source"].get("date") else "") for f in g))
    print(f"\n{len(cs)} to ask the member about. Never pick one yourself.")


def cmd_gaps(a):
    d = load(a.ledger)
    ask, later = gap_list(d, a.cap)
    if not ask:
        print("Nothing to ask. Every field has at least a likely answer.")
        return
    print(f"Ask these {len(ask)}, in this order, one at a time. The member may skip any.\n")
    for i, (_, _, _key, q) in enumerate(ask, 1):
        print(f"{i}. {q}")
    if later:
        print(f"\nLeft for the build sessions, not asked now ({len(later)}): " + ", ".join(FIELD[k][2] for _, _, k, _ in later))


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
        print("Not ready yet for a straight run through the build sessions.")
        if weak:
            print("These must be known first: " + ", ".join(weak) + ".")
        ask, _ = gap_list(d, 5)
        if ask:
            print("Answering these would help most:")
            for _, _, _key, q in ask:
                print(f"  - {q}")
    sys.exit(0 if ready else 2)


def cmd_page(a):
    d = load(a.ledger)
    bf, conflicted = by_field(d), dict(find_conflicts(d))
    pct, weak = score(d)
    out = [f"# What I found about {d.get('subject') or 'your business'}", ""]
    if d.get("date"):
        out += [f"_Researched {d['date']}. Correct anything that is wrong. Your word always wins._", ""]
    scope = d.get("scope") or {}
    if scope.get("read"):
        out += ["**What I read:** " + "; ".join(map(str, scope["read"])), ""]
    if scope.get("excluded"):
        out += ["**What I left alone, as you asked:** " + "; ".join(map(str, scope["excluded"])), ""]
    for sec in (1, 2, 3, 4, 0):
        lines = []
        for key, s, label, _w, multi, _q in FIELDS:
            if s != sec or key not in bf or key in conflicted:
                continue
            fs = sorted(bf[key], key=lambda f: -CONF.get(f.get("confidence"), 0))
            for f in (fs if multi else [best(fs)]):
                text = f"“{f['quote']}”" if multi and f.get("quote") else f["value"]
                lines.append(f"- **{label}:** {text}  \n  _{f.get('confidence')} · {src_text(f)}_")
        if lines:
            out += [f"## {SECTIONS[sec]}", ""] + lines + [""]
    if conflicted:
        out += ["## Things that disagree", "", "Your sources say different things here. Tell me which is right today.", ""]
        for key, groups in conflicted.items():
            out.append(f"- **{FIELD[key][2]}:** " + " **or** ".join(f"“{g[0]['value']}” ({src_text(g[0])})" for g in groups))
        out.append("")
    missing = [f[2] for f in FIELDS if f[0] not in bf]
    if missing:
        out += ["## What I could not find", "", ", ".join(missing) + ".", ""]
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
    for name, fn in (("check", cmd_check), ("conflicts", cmd_conflicts), ("ready", cmd_ready), ("page", cmd_page)):
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
