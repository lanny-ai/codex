#!/usr/bin/env python3
"""Your business on one page: the page a member gets at the end of their first session.

  onepage.py check LEDGER.json [--words WORDS.json] [--business-file FILE]
  onepage.py build LEDGER.json OUT.html [--words WORDS.json] [--business-file FILE] [--next "sentence to say next"]

The page shows what the member said, in their own words, from the ledger's member and Business File findings.
Nothing found on a page or in a file, and nothing guessed, is shown as theirs.

WORDS.json is optional: three ways to say what they do, written by the session from the member's words only.
  {"sentence": "...", "paragraph": "...", "bio": "..."}
They are shown as drafted, never as the member's words, and are refused if they carry a number the member
did not give, a guarantee or a promise of an outcome, or a line the member retired. A bio is refused unless
the member has given their background or their story.

One self-contained file. It works offline and prints cleanly. Standard library only.
"""
import html, importlib.util, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("discover_helper", HERE / "discover.py")
dz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dz)
E = html.escape

FIGURE = re.compile(r"[$€£]\s?\d[\d,.]*|\d[\d,.]*\s?(?:%|percent\b|per cent\b)|\b\d+(?:\.\d+)?x\b|\b\d[\d,]*\b", re.I)
PROMISE = re.compile(r"\b(guarantee[ds]?|money[- ]back|refund(s|ed)?|doubl(e|ed|es|ing)(?![- ]?(check|book|click|sided))|tripl(e|ed|es|ing))\b", re.I)
LIMITS = {"sentence": 220, "paragraph": 700, "bio": 600}
LABELS = {"sentence": ("In one sentence", "For an introduction, a bio line or the top of a page."),
          "paragraph": ("In one paragraph", "For an About section or the opening of an email."),
          "bio": ("A short bio", "For a profile, a speaker page or a guest post.")}
HEAD = ("1.what_i_do", "1.who_i_serve", "1.core_result")
# The ledger's labels are written for the session. These are written for the member.
PLAIN = {"3.deliverables": "What a client receives", "2.pains": "What they struggle with", "2.profile": "My best client", "2.dream": "What they want",
         "2.trigger": "What makes them act", "2.objections": "Why they hesitate", "2.negative": "Who I turn away", "3.structure": "How the work runs",
         "1.price": "Price", "1.booking": "How someone books", "x.credentials": "My background", "x.story": "Why I started", "1.lead_sources": "How people find me",
         "3.promise": "My promise", "4.alternative": "What they would do without me", "3.typical_result": "A typical result", "3.offer_name": "My offer", "1.tools": "Tools"}


def label(key):
    return PLAIN.get(key, dz.FIELD[key][2])


def own(d, key):
    return [f for f in dz.by_field(d).get(key, []) if dz.kind(f) in dz.OWN and not f.get("stale")]


def said(d):
    """Everything the member has said, as one text, for checking that a draft adds no number of its own."""
    return " ".join(str(f.get("value", "")) + " " + str(f.get("quote", "")) for fs in dz.by_field(d).values() for f in fs if dz.kind(f) in dz.OWN and not f.get("stale"))


def word_problems(d, words, retired=()):
    out = []
    if not isinstance(words, dict):
        return ['the words file must be an object: {"sentence": ..., "paragraph": ..., "bio": ...}']
    known = {re.sub(r"[\s,]", "", m).lower().rstrip(".") for m in FIGURE.findall(said(d))}
    for k, v in words.items():
        if k not in LIMITS:
            out.append(f"{k}: not one of sentence, paragraph, bio")
            continue
        v = str(v).strip()
        if not v:
            out.append(f"{k}: empty. Leave it out instead")
            continue
        if len(v) > LIMITS[k]:
            out.append(f"{k}: {len(v)} characters; keep it under {LIMITS[k]}")
        new = sorted({m for m in FIGURE.findall(v) if re.sub(r"[\s,]", "", m).lower().rstrip(".") not in known})
        if new:
            out.append(f"{k}: carries a number the member did not give ({', '.join(new)})")
        if PROMISE.search(v):
            out.append(f"{k}: reads as a guarantee or a promise of an outcome. That is the member's to write")
        if re.search(r"[\"“][^\"”]{12,}[\"”]", v):
            out.append(f"{k}: no quotation marks. Nobody's words are quoted here")
        if "[" in v or "{{" in v:
            out.append(f"{k}: still carries a blank to fill. Write it without, or leave it out")
        for line in retired:
            if dz.norm(line) and dz.norm(line) in dz.norm(v):
                out.append(f"{k}: carries a retired line (“{line}”)")
    if "bio" in words and not (own(d, "x.credentials") or own(d, "x.story")):
        out.append("bio: the member has not given their background or their story, so there is nothing to write a bio from")
    if words and not all(own(d, k) for k in HEAD):
        out.append("words: what they do, who they serve and the result must all be the member's own word first")
    return out


CSS = """
:root{--navy:#0b1020;--ink:#0f1424;--ink2:#2b3247;--mute:#667089;--line:#e2e6ef;--panel:#f5f6fa;--gold1:#ffe7a3;--gold2:#ffb547;--orange:#f97316;--cyan:#4fe3ff;--amber:#92400e;--amberbg:#fff1d6;
--sans:"Inter","SF Pro Text",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--display:"Inter Tight","SF Pro Display",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--panel);color:var(--ink);font:18px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:980px;margin:0 auto;padding:0 24px}
:focus-visible{outline:3px solid var(--cyan);outline-offset:2px}
.cover{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:60px 0 52px}
.cover:before{content:"";position:absolute;inset:0;background:radial-gradient(900px 520px at 88% -8%,rgba(249,115,22,.36),transparent 62%),radial-gradient(760px 520px at -6% 108%,rgba(79,227,255,.16),transparent 60%)}
.cover>*{position:relative}
.eyebrow{font:700 13px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
h1{font:800 clamp(36px,6vw,66px)/1.03 var(--display);letter-spacing:-.03em;margin:16px 0 14px}
h1 em{font-style:normal;background:linear-gradient(180deg,var(--gold1),var(--gold2) 50%,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.cover p{font-size:clamp(18px,2.1vw,21px);color:#cdd4ea;max-width:680px;margin:0}
.edge{height:6px;background:linear-gradient(90deg,var(--orange),var(--gold2),var(--gold1))}
.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:-34px;position:relative}
.big{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px 24px;box-shadow:0 14px 34px rgba(11,16,32,.10)}
.big .k,.k{font:700 12.5px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.big p{font:500 21px/1.4 var(--serif);margin:12px 0 0;color:var(--ink)}
section{padding:44px 0 0}
h2{font:800 clamp(26px,3.6vw,36px)/1.1 var(--display);letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--mute);margin:0 0 20px;font-size:17px;max-width:700px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px 22px}
.card p{margin:10px 0 0}.card ul{margin:10px 0 0;padding-left:20px}.card li{margin:4px 0}
.say3{display:grid;gap:16px}
.way{background:#fff;border:1px solid var(--line);border-left:6px solid var(--gold2);border-radius:16px;padding:20px 24px}
.way .t{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.way h3{font:800 20px/1.2 var(--display);margin:0}
.tag{font:700 11.5px/1 var(--sans);letter-spacing:.06em;text-transform:uppercase;padding:5px 8px;border-radius:999px;color:var(--amber);background:var(--amberbg)}
.way .for{color:var(--mute);font-size:15.5px;margin:4px 0 0}
.way p.w{font:500 20px/1.5 var(--serif);margin:12px 0 0}
.copy,.btn{appearance:none;cursor:pointer;border:1px solid #d8deee;background:linear-gradient(180deg,#f8f9fd,#eef1f9);border-radius:10px;padding:9px 14px;font:600 15px/1 var(--sans);color:var(--navy);margin-top:14px;min-height:40px}
.open{background:#fff;border:1px dashed #c9d0e2;border-radius:16px;padding:20px 22px;color:var(--ink2)}
.next{background:var(--navy);color:#fff;border-radius:18px;padding:26px 28px}
.next h2{color:#fff}.next p{color:#cdd4ea;margin:6px 0 0}
.phrase{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:16px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:12px;padding:12px 16px;font:600 19px/1.3 var(--sans)}
.phrase .copy{margin:0}
.meter{height:10px;border-radius:999px;background:#e2e6ef;overflow:hidden;margin:12px 0 8px}.meter i{display:block;height:100%;background:linear-gradient(90deg,var(--orange),var(--gold2))}
footer{color:var(--mute);font-size:15px;padding:40px 0 56px}
@media(max-width:760px){.trio,.grid{grid-template-columns:1fr}.trio{margin-top:-22px}body{font-size:17px}}
@media print{body{background:#fff;font-size:11pt}.cover{-webkit-print-color-adjust:exact;print-color-adjust:exact}.noprint,.copy{display:none}.card,.way,.big{break-inside:avoid;box-shadow:none}section{padding-top:22px}}
"""
JS = """
document.querySelectorAll("[data-copy]").forEach(function(b){b.addEventListener("click",function(){var t=document.getElementById(b.getAttribute("data-copy")).textContent;
navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent="Copied";setTimeout(function(){b.textContent=o},1500)})})});
var p=document.getElementById("print");if(p)p.addEventListener("click",function(){window.print()});
"""


def build(d, words=None, next_phrase=""):
    name = str(d.get("subject") or "Your business")
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(name)} on one page</title><style>{CSS}</style></head><body>']
    o.append(f'<header class="cover"><div class="wrap"><div class="eyebrow">Build Room OS · Your business on one page</div><h1>{E(name)},<br><em>in your own words.</em></h1>'
             f'<p>Everything here is what you said, as you said it. Nothing was added and nothing was polished.{" As of " + E(str(d["date"])) + "." if d.get("date") else ""}</p></div></header><div class="edge"></div><main class="wrap">')
    head = [(dz.FIELD[k][2].replace(" I deliver", ""), dz.best(own(d, k))["value"]) for k in HEAD if own(d, k)]
    if head:
        o.append('<div class="trio">' + "".join(f'<div class="big"><div class="k">{E(l)}</div><p>{E(str(v))}</p></div>' for l, v in head) + '</div>')
    if words:
        o.append('<section><h2>Three ways to say what you do</h2><p class="sub">Written from your words above, with nothing added. They are drafts: change anything that does not sound like you.</p><div class="say3">')
        for k in ("sentence", "paragraph", "bio"):
            if words.get(k):
                o.append(f'<div class="way"><div class="t"><h3>{LABELS[k][0]}</h3><span class="tag">Drafted for you</span></div><p class="for">{LABELS[k][1]}</p>'
                         f'<p class="w" id="w-{k}">{E(str(words[k]).strip())}</p><button class="copy" type="button" data-copy="w-{k}">Copy</button></div>')
        o.append('</div></section>')
    shown = set(HEAD)
    for title, keys in dz.INTERVIEW:
        cards = []
        for key in keys:
            if key in HEAD:
                continue
            fs = own(d, key)
            if not fs:
                continue
            shown.add(key)
            mine = lambda f: " (my wording; you said it looks right)" if f.get("guess_ok") else ""  # noqa: E731
            vals = list(dict.fromkeys(str(f["value"]) + mine(f) for f in (fs if dz.FIELD[key][4] else [dz.best(fs)])))
            body = f"<p>{E(vals[0])}</p>" if len(vals) == 1 else "<ul>" + "".join(f"<li>{E(v)}</li>" for v in vals) + "</ul>"
            cards.append(f'<div class="card"><div class="k">{E(label(key))}</div>{body}</div>')
        if cards:
            o.append(f'<section><h2>{E(title)}</h2><div class="grid">{"".join(cards)}</div></section>')
    todo = [label(k) for _t, keys in dz.INTERVIEW for k in keys if k not in shown]
    if todo:
        o.append('<section><h2>Still open</h2><p class="sub">Yours to answer when you are ready. Nothing was guessed to fill these.</p><div class="open">' + E(", ".join(todo)) + '.</div></section>')
    pct, _weak = dz.score(d)
    o.append(f'<section><h2>How much is known so far</h2><div class="card"><div class="meter"><i style="width:{max(2, min(100, pct))}%"></i></div>'
             f'<p style="margin:0"><b>{pct} out of 100.</b> A guide to how much your sessions have to work from. It is not a score for your business, and it promises nothing.</p></div></section>')
    if next_phrase:
        o.append(f'<section><div class="next"><h2>What to do next</h2><p>One step. Say this in a new chat:</p><div class="phrase"><span id="nx">{E(next_phrase)}</span>'
                 '<button class="copy noprint" type="button" data-copy="nx">Copy</button></div></div></section>')
    o.append('<section class="noprint"><button class="btn" id="print" type="button">Print or save as PDF</button></section>')
    o.append(f'</main><footer class="wrap">Build Room OS, from AI Momentum Labs. This page is a file on your own computer. Nothing on it was published or sent, and nothing on it promises results.</footer><script>{JS}</script></body></html>')
    return "".join(o)


def main():
    a = sys.argv[1:]
    opt = {}
    for flag in ("--words", "--business-file", "--next"):
        if flag in a:
            k = a.index(flag)
            if k + 1 >= len(a):
                sys.exit(__doc__)
            opt[flag] = a[k + 1]
            del a[k:k + 2]
    if len(a) < 2 or a[0] not in ("check", "build") or (a[0] == "build" and len(a) != 3):
        sys.exit(__doc__)
    d = dz.load(a[1])
    retired = dz.retired_lines(opt["--business-file"]) if opt.get("--business-file") else []
    probs = [f"ledger: {p}" for p in dz.problems(d, retired)]
    words = None
    if opt.get("--words"):
        try:
            words = json.loads(Path(opt["--words"]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.exit(f"Cannot read the words file: {e}")
        probs += word_problems(d, words, retired)
    if not any(own(d, k) for k in HEAD):
        probs.append("nothing here is the member's own word yet. Ask the first questions before building a page")
    if a[0] == "check" or probs:
        for p in probs:
            print("FIX  " + p)
        if a[0] == "check":
            print(f"{len(probs)} to fix.")
        sys.exit(1 if probs else 0)
    out = Path(a[2])
    if out.suffix.lower() != ".html":
        sys.exit("The output file must end in .html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(d, words, opt.get("--next", "")), encoding="utf-8")
    print(f"Wrote {out}. Open it in a browser.")


if __name__ == "__main__":
    main()
