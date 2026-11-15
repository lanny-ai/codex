#!/usr/bin/env python3
"""Speaking Engine: the check every pitch, follow-up, bio and one-sheet passes before a host sees it.

  pitch_check.py check --file speaking/pitches/draft.txt --kind pitch|followup|bio|talk|one-sheet
                       [--stage ST-003] [--business-file BUILDROOM_BUSINESS_FILE.md] [--folder speaking]

A host checks what a speaker claims. So the rule is the member's own facts or nothing:

  FIX   placeholder text · a figure that is not in the member's intake, talks, proof bank or Business
        File (the stage's own facts are allowed) · a status claim the member's material does not
        contain ("award-winning", "best-selling", "as seen on", "keynote speaker", "certified",
        "guarantee") · a quotation that is not in the proof bank · a retired line or never-say claim ·
        pressure ("act now", "last chance") · far too long for a host to read · a pitch that names
        neither the host nor the event, offers no talk that is on file, or asks for nothing · an em or
        en dash
  WATCH over the working length · opens on the speaker instead of the host's audience · an attachment
        (send a link) · more than two links · no easy way for the host to say no · long sentences ·
        no Business File found, so retired lines and never-say claims were not checked
Exit 0 when CLEAN, 1 on FIX, 2 on a usage error. JSON on stdout.

What a script cannot check: whether a credential is true, whether the host is the right person, and
whether the talk is any good. The member confirms the first, the vetting the second, a rehearsal the third.
"""
import argparse, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import speaklib as sl  # noqa: E402

# working length, and the length past which a busy host stops reading (words)
LIMITS = {"pitch": (150, 220), "followup": (70, 110), "bio": (100, 150), "talk": (120, 180), "one-sheet": (450, 650)}
PRESSURE = re.compile(r"\b(?:act now|last chance|limited time|only \d+ (?:spots?|seats?|places?) left|don't miss out|"
                      r"before it'?s too late|offer (?:ends|expires))\b", re.I)
QUOTE = re.compile(r'"([^"]{25,400})"')
NO_OUT = re.compile(r"\b(?:no (?:problem|worries|pressure) (?:if|either way)|if (?:it'?s|this is|that'?s) not (?:a|the right) fit|"
                    r"either way|feel free to say no|just say so|happy to hear a no|if not, no)\b", re.I)
SELF_OPEN = re.compile(r"^\s*(?:hi|hello|dear)?[^.!?\n]{0,40}[,.!]?\s*(?:my name is|i am|i'm|i have been|i've been|i would like|i'd like)\b", re.I)
STOP = set("the and for with from your club group association society chapter annual conference summit podcast show meeting "
           "luncheon lunch breakfast business chamber commerce network networking event events local national of in at".split())


def distinctive(*names):
    out = set()
    for n in names:
        out |= {w for w in re.findall(r"[a-z][a-z'-]{2,}", sl.plain(n or "").lower()) if w not in STOP}
    return out


def check(a):
    f = Path(a.file)
    if not f.is_file():
        return {"ok": False, "error": f"file not found: {a.file}"}, 2
    text = sl.plain(sl.read_text(f)).strip()
    bf = sl.find_business_file(a)
    data = sl.read_json(sl.folder(a) / "pipeline.json", {"profile": {}, "talks": [], "stages": []})
    known = sl.known_text(a, bf)
    nums = sl.number_sets(known)
    stage = None
    if a.stage:
        stage = next((s for s in data["stages"] if str(s.get("id", "")).lower() == a.stage.lower()), None)
        if stage is None:
            return {"ok": False, "error": f"no stage {a.stage}"}, 2
    items = []

    def add(level, cid, msg, fix=""):
        items.append({"level": level, "id": cid, "message": msg, "fix": fix})
    n = sl.words(text)
    if n == 0:
        return {"ok": False, "error": "the file is empty"}, 2
    work, hard = LIMITS[a.kind]
    if n > hard:
        add("FIX", "too_long", f"{n} words; a {a.kind} over {hard} is not read", f"cut to about {work}: one talk, one ask")
    elif n > work:
        add("WATCH", "long", f"{n} words; aim for about {work}", "cut the part about the speaker before the part about the room")
    ph = sorted({m.group(0) for m in sl.PLACEHOLDER.finditer(text)})
    if ph:
        add("FIX", "placeholders", "placeholder text: " + ", ".join(ph[:5]), "fill it from the member's own facts, or take the line out")
    if any(d in text for d in sl.DASHES):
        add("FIX", "dashes", "an em or en dash", "use a comma, a period or a colon")
    allow = []
    if stage:
        allow = [str(stage.get(k) or "") for k in ("name", "host", "audience", "when", "deadline", "note", "recurring")]
        allow += [f"{stage.get('size')} people", f"{stage.get('size')} members", f"{stage.get('size')} attendees"] if stage.get("size") else []
        bk = stage.get("booking") or {}
        allow += [str(bk.get("terms") or ""), f"${bk.get('fee')}" if bk.get("fee") else ""]
    lengths = " ".join(f"{m} minutes {m} minute" for t in data["talks"] for m in t.get("lengths", []))
    unknown = sl.unsourced_numbers(re.sub(r"\b(\d+)[- ]minutes?\b", " ", text), nums, allow + [lengths])
    if unknown:
        add("FIX", "unsourced_numbers", "figures the member did not give: " + ", ".join(unknown[:8])
            + (f" (+{len(unknown) - 8} more)" if len(unknown) > 8 else ""),
            "use only numbers from the member's intake, proof bank or Business File; a host may check them")
    claims = sl.unsupported_claims(text, known)
    if claims:
        add("FIX", "unsupported_claims", "claims the member's own material does not contain: " + ", ".join(claims[:6]),
            "ask the member whether it is true and where it is recorded; if it is, add it to the credentials answer first")
    kn = nums["text"]
    bad_quotes = [q for q in QUOTE.findall(text) if re.sub(r"\s+", " ", q.lower()).strip(" .,!?") not in kn
                  and not any(re.sub(r"\s+", " ", sl.plain(t["title"]).lower()) in q.lower() for t in data["talks"])]
    if bad_quotes:
        add("FIX", "unsourced_quote", "a quotation that is not in the proof bank or the member's file: \""
            + bad_quotes[0][:70] + "…\"", "a testimonial comes from the Proof Engine's bank with its permission, word for word, or it is left out")
    low = re.sub(r"\s+", " ", text.lower())
    for kind, line in sl.banned_lines(bf):
        if re.sub(r"\s+", " ", line.lower()) in low:
            add("FIX", "banned_line", f"{kind} in the Business File: \"{line[:70]}\"", "take it out")
    pr = sorted({m.group(0).lower() for m in PRESSURE.finditer(text)})
    if pr:
        add("FIX", "pressure", "pressure wording: " + ", ".join(pr[:4]), "a host is doing the member a favour by reading; ask plainly")
    if a.kind in ("pitch", "followup"):
        if "?" not in text:
            add("FIX", "no_ask", "it asks for nothing", "end on one question the host can answer in a line")
        if stage:
            want = distinctive(stage["name"], stage["host"])
            if want and not (want & distinctive(text)):
                add("FIX", "not_about_them", f"it names neither {stage['name']} nor {stage['host']}",
                    "say which meeting or event this is for; a pitch that could go to anyone goes nowhere")
        if a.kind == "pitch":
            titles = [sl.plain(t["title"]).lower() for t in data["talks"]]
            if not titles:
                add("FIX", "no_talk", "no talk is on file to offer", "speak_pipeline.py talk add …")
            elif not any(t in low for t in titles):
                add("FIX", "no_talk", "it does not offer a talk that is on file, by its title", "offer one talk, by name, with what the room leaves able to do")
        if SELF_OPEN.search(text):
            add("WATCH", "opens_on_speaker", "it opens on the speaker", "open on their members and the problem the talk solves for them")
        if re.search(r"\battach(?:ed|ment|ing)\b", text, re.I):
            add("WATCH", "attachment", "it mentions an attachment", "send a link to the one-sheet; first emails with attachments are often filtered")
        if len(re.findall(r"https?://", text)) > 2:
            add("WATCH", "links", "more than two links", "one link to the one-sheet is enough")
        if a.kind == "pitch" and not NO_OUT.search(text):
            add("WATCH", "no_easy_no", "there is no easy way for the host to say no",
                "add a line such as \"If it is not a fit this year, just say so.\" It gets more answers, and it is the polite thing")
    long_s = [s for s in sl.sentences(text) if sl.words(s) > 32]
    if long_s:
        add("WATCH", "long_sentences", f"{len(long_s)} sentence(s) over 32 words", "split them; a host reads this on a phone")
    if not bf:
        add("WATCH", "no_business_file", "no Business File was found, so retired lines and never-say claims were not checked",
            "run again with --business-file BUILDROOM_BUSINESS_FILE.md")
    fixes = [i for i in items if i["level"] == "FIX"]
    return {"ok": not fixes, "verdict": "CLEAN" if not fixes else "FIX", "kind": a.kind, "words": n, "fix": len(fixes),
            "watch": len(items) - len(fixes), "items": items, "stage": stage["id"] if stage else "",
            "limits": "a script cannot tell whether a credential is true, whether this is the person who books speakers, "
                      "or whether the talk is good"}, 0 if not fixes else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--file", required=True); c.add_argument("--kind", required=True, choices=sorted(LIMITS))
    c.add_argument("--stage"); c.add_argument("--business-file"); c.add_argument("--folder")
    a = ap.parse_args()
    out, code = check(a)
    sl.emit(out, code)


if __name__ == "__main__":
    main()
