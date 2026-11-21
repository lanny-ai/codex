#!/usr/bin/env python3
"""Draft check: reads every draft an Autopilot run wrote and refuses what must not be in it.

  drafts.py check --dir autopilot [--business-file FILE] [--ledger LEDGER.json]

FIX lines stop the handover (handover.py runs this check and will not build the Your Build page until they are gone):
  - a line the member retired, in the Business File or at the start of the run
  - a client's words used without permission recorded as yes, in copy a stranger reads (the offer page,
    the funnel emails, the opt-in page, outreach). In notes written for the member it is a LOOK line instead
  - a price, percentage or multiple that nobody confirmed, or a count of clients, births, years and the like
  - words in quotation marks given to someone ("...," said one mother) that match no real quote on record
  - a sentence that offers a guarantee or refund the member does not have, or without their exact wording
  - "double" or "triple" as a promise of an outcome
  - a draft with no "Draft by Autopilot" line at the top

LOOK lines do not stop anything. They are sentences that share a word with something the member refuses to claim,
or that make a general claim about what clients get. A script cannot judge meaning, so read each one and reword
it if it comes close. No LOOK lines is not a clean bill: the session still reads every draft against the rules.

It reads run.json, foundation.json, the drafts, and the Business File and ledger when they are there.
It writes nothing. Standard library only.
"""
import argparse, json, re, sys
from pathlib import Path

MONEY = re.compile(r"[$€£]\s?\d[\d,.]*|\d[\d,.]*\s?%|\b\d+(?:\.\d+)?x\b", re.I)
# A sentence that offers a guarantee, as opposed to a heading or a note that names the subject.
GUARANTEE_OFFER = re.compile(r"\b(we|i|you are|you'?re|it is|it'?s|is|are|fully|100%)\s+guarantee[ds]?\b|\bguaranteed\b|\bguarantee (that|you|your|it|a|the)\b"
                             r"|money[- ]back|\bor (your|a full) (money|refund)\b|\b(full|your) refund\b|\brefund(ed)? (if|you|your|in full)\b"
                             r"|\b(will|we|i|we'll|i'll) refund\b", re.I)
# A count of people or years is a fact about the member: "over 50 births", "200 clients", "15 years".
COUNT = re.compile(r"\b(\d[\d,]*)\+?\s+(?:\w+\s+)?(births?|clients?|customers?|years?|students?|members?|families|projects?|businesses|studios?|practices|patients?|owners?)\b", re.I)
# Words in quotation marks that are handed to someone: "...," said one mother.
ATTRIBUTED = re.compile(r"[\"“]([^\"”]{15,})[\"”][,.]?\s*(?:said|says|wrote|writes|told|shared)\b|[\"“]([^\"”]{15,})[\"”]\s*[-–—]\s*[A-Z]")
# A general claim about what clients get. Not refused, because it may be the member's own honest view. Listed to be read.
GENERAL_CLAIM = re.compile(r"\b(most|many|all|every|typical(ly)?)\b[^.]{0,40}\b(clients?|customers?|parents|members|students|owners|people|practices|studios)\b[^.]{0,60}"
                           r"\b(get|gets|see|sees|have|has|are|feel|report|save|earn|grow|need|needs)\b|\b(less|more) likely\b", re.I)
OUTCOME = re.compile(r"\b(doubl(e|ed|es|ing)|tripl(e|ed|es|ing))\b", re.I)
# Drafts whose words reach a stranger. In the others a client's words are notes for the member.
PUBLIC = ("offer-page-copy", "funnel-map", "lead-capture", "leadgen")
PRIVATE_MARK = re.compile(r"not for public|not to be used publicly|do not quote|not to be quoted|permission not", re.I)
NEGATED = re.compile(r"\b(no|not|never|none|without|don'?t|do not|isn'?t|won'?t|cannot|can'?t|nor)\b", re.I)
NONE = re.compile(r"\s*((none|no|nothing|n/?a|not yet)( yet| really)?[\s.!]*$|i don'?t (know|have)\b|don'?t (know|have)\b|skip\b)", re.I)
HEADER = "draft by autopilot"
STOP = set("""about above after again against always anything because before being below between cannot claim claims could
doing during every everyone first other others promise promised promises should their there these thing things those through
under until where which while would yours business client clients people result results never anyone""".split())


def squash(v):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", str(v).lower())).strip()


def fig(m):
    return re.sub(r"[\s,]", "", m).rstrip(".").lower()


def counts(text):
    return {m.group(1).replace(",", "") + " " + m.group(2).lower().rstrip("s") for m in COUNT.finditer(str(text))}


def figures(text):
    return {fig(m) for m in MONEY.findall(str(text))} | counts(text)


def negated(raw, m):
    """Is the matched word itself denied? Only a negation in the same clause, just before it, counts:
    "there is no guarantee" is; "if you are not happy, I will refund you" is not."""
    clause = re.split(r"[,;:.!?]", raw[:m.start()])[-1]
    return bool(NEGATED.search(clause[-45:]) or re.search(r"\b(dropped|removed|retired|stopped|no longer|used to|old|former)\b", clause[-45:], re.I))


def parse_retired(line):
    out = []
    for entry in re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", str(line)).split(";"):
        quoted = re.findall(r"[\"“]([^\"”]{4,})[\"”]", entry)
        if not quoted:
            bare = re.sub(r"^(the )?(name|phrase|line|words?|claim|offer|tagline)\s+", "", entry.strip(" .—-"), flags=re.I).strip()
            quoted = [bare] if len(bare) >= 4 and not re.match(r"(none|n/?a|nothing)\b", bare, re.I) else []
        out += [x.strip() for x in quoted if not x.strip().lower().startswith("e.g")]
    return out


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def bf_field(text, label):
    m = re.search(r"^- \*\*" + re.escape(label) + r"(?::\*\*|\*\*(?:\s*\([^)]*\))?:?)[ \t]*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return "" if v in ("", "—", "-") else v


def rules(folder, business_file=None, ledger=None):
    """Everything the drafts are held to, gathered from what the member said and what was found."""
    folder = Path(folder)
    run = read_json(folder / "run.json") or {}
    dec = {x.get("key"): str(x.get("value", "")) for x in run.get("decisions", []) if isinstance(x, dict)}
    retired = parse_retired(dec.get("retired", "")) if not NONE.match(dec.get("retired", "")) else []
    never = [dec["never_claim"]] if dec.get("never_claim") and not NONE.match(dec["never_claim"]) else []
    guarantee = dec.get("guarantee")
    known = set()
    for v in dec.values():
        known |= figures(v)
    if business_file and Path(business_file).is_file():
        text = Path(business_file).read_text(encoding="utf-8")
        retired += parse_retired(bf_field(text, "Retired lines"))
        if bf_field(text, "Never claim or promise"):
            never.append(bf_field(text, "Never claim or promise"))
        if guarantee is None and bf_field(text, "Guarantee"):
            guarantee = bf_field(text, "Guarantee")
        known |= figures(text)
    fnd = read_json(folder / "foundation.json") or {}
    fquotes = []
    for part in fnd.values() if isinstance(fnd, dict) else []:
        for key, v in (part.items() if isinstance(part, dict) else []):
            for x in (v if isinstance(v, list) else [v]):
                if isinstance(x, dict) and x.get("basis") in ("confirmed", "files"):
                    known |= figures(x.get("v", ""))
                    if key == "language":
                        fquotes.append(str(x.get("v", "")))
    barred, allowed, real_quotes = [], [], []
    led = read_json(ledger) if ledger else None
    for f in (led or {}).get("findings", []) if isinstance(led, dict) else []:
        if not isinstance(f, dict) or not isinstance(f.get("source"), dict):
            continue
        words = str(f.get("quote") or "")
        if words:
            real_quotes.append(words)
        if f.get("field") == "x.proof" and not f.get("absent"):
            # A real figure is not an invented one, whoever may quote it. Whether the words may be used is checked apart.
            known |= figures(str(f.get("value", "")) + " " + words)
            if f.get("permission") == "yes":
                allowed.append(words or str(f.get("value", "")))
            elif len(squash(words)) >= 12:
                barred.append(words)
            continue
        if f.get("field") == "2.language" and f.get("permission") == "no" and len(squash(words)) >= 12:
            barred.append(words)
            continue
        if f.get("stale") or f.get("retired") or f["source"].get("kind") == "hypothesis" or f.get("confidence") == "inferred":
            continue
        known |= figures(str(f.get("value", "")) + " " + words)
    seen, uniq = set(), []
    for r in retired:
        if squash(r) and squash(r) not in seen:
            seen.add(squash(r))
            uniq.append(r)
    return {"run": run, "retired": uniq, "never": never, "guarantee": guarantee, "figures": known, "barred": barred, "allowed": allowed, "quotes": real_quotes + fquotes}


def key_words(entry):
    return {w[:6] for w in re.findall(r"[a-z]{5,}", str(entry).lower()) if w not in STOP}


def check_text(name, text, r, public=True):
    fixes, looks = [], []
    lines = text.splitlines()
    first = next((l for l in lines if l.strip()), "")
    if HEADER not in first.lower():
        fixes.append(f"{name}: the first line must say it is a draft (\"Draft by Autopilot on [date]. Nothing here is published. Check it before you use it.\")")
    whole = squash(text)
    wording = squash(r["guarantee"]) if r["guarantee"] and not NONE.match(r["guarantee"]) and not re.match(r"\s*none\b", r["guarantee"], re.I) else ""
    for line in r["retired"]:
        if squash(line) in whole:
            fixes.append(f"{name}: uses a line the member retired (“{line}”). Take it out")
    for words in r["barred"]:
        if squash(words) not in whole:
            continue
        head = squash(words)[:30]
        marked = any(head in squash(l) and PRIVATE_MARK.search(l) for l in lines)
        if public:
            fixes.append(f"{name}: uses a client's words without permission recorded as yes (“{words[:70]}”). Take them out, or mark the spot [needs you: a result you have permission to use]")
        elif not marked:
            looks.append(f"{name}: quotes a client without permission recorded as yes (“{words[:70]}”). Fine in notes for the member; say \"not for public quoting\" beside it")
    allowed = [squash(a) for a in r["allowed"] if squash(a)]
    never = [(e.strip(), key_words(e)) for entry in r["never"] for e in entry.split(";") if e.strip()]
    for n, raw in enumerate(lines, 1):
        s = squash(raw)
        if not s or "needs you" in s:
            continue
        where = f"{name}:{n}"
        permitted = any(a in s or s in a for a in allowed)
        new = sorted({m.strip() for m in MONEY.findall(raw) if fig(m) not in r["figures"]} | {c for c in counts(raw) if c not in r["figures"]})
        if new and not permitted:
            fixes.append(f"{where}: a figure nobody confirmed ({', '.join(new)}). Take it out, or mark it [needs you: ...]: {raw.strip()[:110]}")
        if not permitted:
            g = next((m for m in GUARANTEE_OFFER.finditer(raw) if not negated(raw, m)), None)
            o = next((m for m in OUTCOME.finditer(raw) if not negated(raw, m)), None)
            if g and (not wording or wording not in whole):
                fixes.append(f"{where}: offers a guarantee or refund, and " + ("the member's exact wording is nowhere in the draft" if wording else "the member has "
                             + ("none" if r["guarantee"] else "not confirmed one")) + f": {raw.strip()[:110]}")
            elif o:
                fixes.append(f"{where}: reads as a promise of an outcome (double, triple). That is the member's to write: {raw.strip()[:110]}")
            for m in ATTRIBUTED.finditer(raw):
                q = squash(m.group(1) or m.group(2))
                if not any(q in squash(k) or squash(k) in q for k in r["quotes"] if squash(k)):
                    fixes.append(f"{where}: words in quotation marks given to someone, with no real source for them. A client's words are copied from where they said them, or left out: {raw.strip()[:110]}")
        tokens = {w[:6] for w in re.findall(r"[a-z]{5,}", raw.lower())}
        hit = False
        for entry, keys in never:
            # A short rule ("any medical outcome") is matched on one shared word; a longer one needs two.
            if keys and len(keys & tokens) >= (1 if len(keys) <= 3 else 2):
                looks.append(f"{where}: read this against what the member refuses to claim (“{entry}”): {raw.strip()[:110]}")
                hit = True
                break
        if public and not hit and not permitted and GENERAL_CLAIM.search(raw) and not NEGATED.search(raw):
            looks.append(f"{where}: a general claim about what clients get. Keep it only if the member said it; a draft does not make it true: {raw.strip()[:110]}")
    return fixes, looks


def problems(folder, business_file=None, ledger=None):
    folder = Path(folder)
    if ledger is None and (folder.parent / "discovery" / "ledger.json").is_file():
        ledger = folder.parent / "discovery" / "ledger.json"
    if business_file is None and (folder.parent / "BUILDROOM_BUSINESS_FILE.md").is_file():
        business_file = folder.parent / "BUILDROOM_BUSINESS_FILE.md"
    r = rules(folder, business_file, ledger)
    fixes, looks = [], []
    files = sorted((folder / "drafts").glob("*.md")) if (folder / "drafts").is_dir() else []
    owner = {Path(str(o)).name: s.get("slug") for s in (r["run"].get("steps", []) if isinstance(r["run"], dict) else []) for o in s.get("outputs") or []}
    for p in files:
        # A draft no step claims is treated as public, the stricter reading.
        f, l = check_text(f"drafts/{p.name}", p.read_text(encoding="utf-8", errors="replace"), r, owner.get(p.name, PUBLIC[0]) in PUBLIC)
        fixes += f
        looks += l
    return fixes, looks, len(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("--dir", required=True, help="the autopilot folder that holds run.json and drafts/")
    p.add_argument("--business-file")
    p.add_argument("--ledger")
    a = ap.parse_args()
    fixes, looks, n = problems(a.dir, a.business_file, a.ledger)
    for x in fixes:
        print("FIX  " + x)
    for x in looks:
        print("LOOK  " + x)
    print(f"{n} draft{'' if n == 1 else 's'} read. {len(fixes)} to fix, {len(looks)} to look at.")
    sys.exit(1 if fixes else 0)


if __name__ == "__main__":
    main()
