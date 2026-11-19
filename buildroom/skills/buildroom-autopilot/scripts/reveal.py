#!/usr/bin/env python3
"""The Foundation Reveal: the member's ideal client, offer and positioning on one page they can review.

  reveal.py check FOUNDATION.json            every line says where it came from; nothing guessed is shown as a quote
  reveal.py build FOUNDATION.json OUT.html   the review page (one file, works offline, prints cleanly)
  reveal.py text FOUNDATION.json             the same content as plain markdown, for a chat with no files

Every value in the JSON is {"v": "...", "basis": "confirmed" | "files" | "drafted", "source": "..."}.
  confirmed  the member said so
  files      found in the member's own files or public pages (source required)
  drafted    written by the session for the member to check

Standard library only. It reads one JSON file and writes one HTML file. Nothing else.
"""
import html, json, sys
from pathlib import Path

BASIS = {"confirmed": "Confirmed by you", "files": "From your files", "drafted": "Drafted for you"}

# (key, label, kind)  kind: text | list | quotes
AVATAR = [("name", "Name we gave them", "text"), ("profile", "Who they are", "text"),
          ("job_functional", "What they are trying to get done", "text"), ("job_emotional", "How they want to feel", "text"),
          ("job_identity", "Who they want to be", "text"),
          ("language", "In their own words", "quotes"),
          ("pain_surface", "What they complain about", "text"), ("pain_emotional", "What it costs them", "text"),
          ("pain_identity", "What they tell themselves", "text"),
          ("dream_90", "In 90 days", "text"), ("dream_year", "In a year", "text"),
          ("force_push", "What pushes them to change", "text"), ("force_pull", "What pulls them toward you", "text"),
          ("force_anxiety", "What worries them about switching", "text"), ("force_habit", "What keeps them where they are", "text"),
          ("trigger", "What makes them act now", "text"),
          ("objections_spoken", "What they say when they hesitate", "list"), ("objections_unspoken", "What they do not say", "list"),
          ("negative", "Who this is not for", "text")]
OFFER = [("name", "Offer name", "text"), ("promise", "The promise", "text"), ("structure", "How it runs", "text"),
         ("phases", "The journey", "list"), ("deliverables", "What they receive", "list"),
         ("value", "Value of everything included", "text"), ("investment", "Investment", "text"),
         ("guarantee", "Guarantee", "text"), ("pitch", "The 60-second pitch", "text"), ("belief", "The one belief", "text"),
         ("urgency", "Why now", "text")]
POSITIONING = [("statement", "Positioning statement", "text"), ("value_prop", "Value in one sentence", "text"), ("tagline", "Tagline", "text"),
               ("alternative", "What they would do without you", "text"), ("category", "What they would call it", "text"),
               ("differentiator", "What makes you different", "text"), ("villain", "What is wrong with how your space works", "text"),
               ("for_you", "For you if", "list"), ("not_for_you", "Not for you if", "list"), ("advantage", "Your unfair advantage", "text")]
PARTS = [("avatar", "Your ideal client", AVATAR), ("offer", "Your offer", OFFER), ("positioning", "Where you stand", POSITIONING)]
# Without these the page is not worth showing.
REQUIRED = [("avatar", "profile"), ("offer", "promise"), ("positioning", "differentiator")]
# Facts, not judgement. These are confirmed or found, or they are left out. Never drafted.
FACTS = {("offer", "investment"), ("offer", "value"), ("offer", "guarantee"), ("offer", "urgency")}


def load(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the foundation file: {e}")
    if not isinstance(d, dict):
        sys.exit("The foundation file must be a JSON object.")
    return d


def items(d, part, key, kind):
    """A field as a list of {v, basis, source} items. Empty when the field is missing or blank."""
    raw = (d.get(part) or {}).get(key) if isinstance(d.get(part), dict) else None
    if raw is None:
        return []
    seq = raw if isinstance(raw, list) else [raw]
    return [x for x in seq if not (isinstance(x, dict) and not str(x.get("v", "")).strip())]


def problems(d):
    out = []
    if not str(d.get("business", "")).strip():
        out.append("business: the business name is missing")
    for part, _title, fields in PARTS:
        if not isinstance(d.get(part), dict):
            out.append(f"{part}: missing")
            continue
        known = {k for k, _l, _k in fields}
        for k in d[part]:
            if k not in known:
                out.append(f"{part}.{k}: not a field this page knows")
        for key, _label, kind in fields:
            raw = d[part].get(key)
            if kind == "text" and isinstance(raw, list):
                out.append(f"{part}.{key}: takes one value, not a list")
            for i, x in enumerate(items(d, part, key, kind)):
                where = f"{part}.{key}" + (f"[{i + 1}]" if kind != "text" else "")
                if not isinstance(x, dict):
                    out.append(f'{where}: must be {{"v": ..., "basis": ...}}, so the page can say where it came from')
                    continue
                if x.get("basis") not in BASIS:
                    out.append(f"{where}: basis must be confirmed, files or drafted")
                elif x["basis"] == "files" and not str(x.get("source", "")).strip():
                    out.append(f"{where}: 'files' needs the source it came from")
                if (part, key) in FACTS and x.get("basis") == "drafted":
                    out.append(f"{where}: a price, a value, a guarantee or a deadline is a fact. Confirm it or leave it out; never draft it")
                if kind == "quotes" and x.get("basis") == "drafted":
                    out.append(f"{where}: a drafted line is not a client's words. Move it out of 'language', or give its real source")
                if kind == "quotes" and x.get("basis") in ("confirmed", "files") and not str(x.get("source", "")).strip():
                    out.append(f"{where}: a client quote needs who said it or where it was found")
    for part, key in REQUIRED:
        if isinstance(d.get(part), dict) and not items(d, part, key, "text"):
            out.append(f"{part}.{key}: needed before the page is worth showing")
    return out


def counts(d):
    c = {b: 0 for b in BASIS}
    for part, _t, fields in PARTS:
        for key, _l, kind in fields:
            for x in items(d, part, key, kind):
                if isinstance(x, dict) and x.get("basis") in c:
                    c[x["basis"]] += 1
    return c


def open_fields(d):
    return [(title, label) for part, title, fields in PARTS for key, label, kind in fields if not items(d, part, key, kind)]


E = html.escape


def badge(x):
    b = x["basis"]
    tip = BASIS[b] + (": " + str(x["source"]) if x.get("source") else "")
    return f'<span class="b {b}" title="{E(tip)}">{E(BASIS[b])}</span>'


def val(d, part, key):
    xs = items(d, part, key, "text")
    return xs[0] if xs else None


def block(d, part, key, label, cls="fld"):
    x = val(d, part, key)
    if not x:
        return ""
    return f'<div class="{cls}"><div class="k">{E(label)} {badge(x)}</div><p>{E(str(x["v"]))}</p></div>'


def lst(d, part, key, label, ordered=False):
    xs = items(d, part, key, "list")
    if not xs:
        return ""
    tag = "ol" if ordered else "ul"
    lis = "".join(f'<li>{E(str(x["v"]))} {badge(x)}</li>' for x in xs)
    return f'<div class="fld"><div class="k">{E(label)}</div><{tag}>{lis}</{tag}></div>'


def initials(name):
    parts = [p for p in str(name).replace("-", " ").split() if p[:1].isalpha()]
    return ("".join(p[0] for p in parts[:2]) or "?").upper()


CSS = """
:root{--navy:#0b1020;--ink:#0f1424;--ink2:#2b3247;--mute:#667089;--line:#e2e6ef;--panel:#f5f6fa;--paper:#fff;
--gold1:#ffe7a3;--gold2:#ffb547;--orange:#f97316;--cyan:#4fe3ff;--ok:#0f7a4d;--okbg:#e7f6ee;--blue:#1d4ed8;--bluebg:#e8efff;--amber:#92400e;--amberbg:#fff1d6;
--sans:"Inter","SF Pro Text",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--display:"Inter Tight","SF Pro Display",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
*{box-sizing:border-box}html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--panel);color:var(--ink);font:18px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
:focus-visible{outline:3px solid var(--cyan);outline-offset:2px}
.cover{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:64px 0 56px}
.cover:before{content:"";position:absolute;inset:0;background:radial-gradient(900px 520px at 88% -8%,rgba(249,115,22,.36),transparent 62%),radial-gradient(760px 520px at -6% 108%,rgba(79,227,255,.16),transparent 60%)}
.cover>*{position:relative}
.eyebrow{font:700 13px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
h1{font:800 clamp(38px,6.4vw,72px)/1.02 var(--display);letter-spacing:-.03em;margin:16px 0 14px}
h1 em{font-style:normal;background:linear-gradient(180deg,var(--gold1),var(--gold2) 50%,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.cover p{font-size:clamp(18px,2.1vw,21px);color:#cdd4ea;max-width:700px;margin:0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.14);border-radius:16px;overflow:hidden;margin-top:34px}
.stat{background:rgba(11,16,32,.74);padding:20px 22px}
.stat b{display:block;font:800 40px/1 var(--display)}.stat span{display:block;font-size:15px;color:#aab3cf;margin-top:8px}
.stat.c b{color:#7be3ac}.stat.f b{color:#9db8ff}.stat.d b{color:var(--gold2)}
.edge{height:6px;background:linear-gradient(90deg,var(--orange),var(--gold2),var(--gold1))}
.how{margin:28px 0 0;padding:18px 20px;border-radius:14px;background:#fff;border:1px solid var(--line);font-size:16.5px;color:var(--ink2)}
.b{display:inline-block;vertical-align:middle;font:700 11.5px/1 var(--sans);letter-spacing:.06em;text-transform:uppercase;padding:5px 8px;border-radius:999px;white-space:nowrap}
.b.confirmed{color:var(--ok);background:var(--okbg)}.b.files{color:var(--blue);background:var(--bluebg)}.b.drafted{color:var(--amber);background:var(--amberbg)}
section.part{padding:56px 0 8px}
.num{font:800 14px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--orange)}
h2{font:800 clamp(30px,4.4vw,46px)/1.05 var(--display);letter-spacing:-.025em;margin:10px 0 22px}
h3{font:800 20px/1.2 var(--display);margin:0 0 12px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:18px;box-shadow:0 1px 2px rgba(15,20,36,.06),0 10px 34px rgba(15,20,36,.08);padding:28px;margin-bottom:20px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid2>.card{margin:0}
.k{font:700 12.5px/1.5 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin-bottom:4px}
.fld{margin:0 0 18px}.fld:last-child{margin-bottom:0}.fld p{margin:0;color:var(--ink)}
ul,ol{margin:0;padding-left:22px}li{margin:7px 0}
.who{display:flex;gap:22px;align-items:center}
.mono{flex:none;width:104px;height:104px;border-radius:50%;display:grid;place-items:center;font:800 38px/1 var(--display);color:#1a1206;background:linear-gradient(180deg,var(--gold1),var(--gold2) 55%,var(--orange));box-shadow:0 12px 30px rgba(249,115,22,.3)}
.who .nm{font:800 clamp(28px,4vw,40px)/1.05 var(--display);letter-spacing:-.02em}
.who .pf{font:400 20px/1.45 var(--serif);color:var(--ink2);margin-top:8px}
.quotes{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
blockquote{margin:0;padding:22px 24px;border-radius:16px;background:var(--navy);color:#fff;font:400 21px/1.4 var(--serif);position:relative}
blockquote:before{content:"\\201C";position:absolute;top:-6px;left:14px;font:800 72px/1 var(--serif);color:var(--gold2);opacity:.55}
blockquote span.t{position:relative;display:block;padding-top:16px}
blockquote cite{display:block;margin-top:12px;font:600 13.5px/1.4 var(--sans);font-style:normal;color:#aab3cf}
.stack>div{padding:18px 22px;border-radius:14px;margin-bottom:10px;color:#fff}
.stack>div:nth-child(1){background:#33406e}.stack>div:nth-child(2){background:#232d57;margin-left:22px}.stack>div:nth-child(3){background:var(--navy);margin-left:44px}
.stack .k{color:#aab3cf}.stack p{margin:0;color:#fff}
.hero{background:var(--navy);color:#fff;border:0;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;inset:0;background:radial-gradient(620px 320px at 100% 0,rgba(249,115,22,.36),transparent 65%)}
.hero>*{position:relative}.hero .k{color:#aab3cf}
.hero .big{font:800 clamp(26px,3.8vw,40px)/1.15 var(--display);letter-spacing:-.02em;margin:6px 0 0;color:#fff}
.hero .nm{font:700 15px/1 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--gold2);margin-bottom:14px}
.steps{list-style:none;padding:0;margin:0;counter-reset:s}
.steps li{counter-increment:s;position:relative;padding:0 0 20px 54px;margin:0}
.steps li:before{content:counter(s);position:absolute;left:0;top:-2px;width:36px;height:36px;border-radius:50%;display:grid;place-items:center;font:800 16px/1 var(--display);color:#1a1206;background:linear-gradient(180deg,var(--gold1),var(--gold2) 55%,var(--orange))}
.steps li:after{content:"";position:absolute;left:17px;top:38px;bottom:2px;width:2px;background:var(--line)}
.steps li:last-child{padding-bottom:0}.steps li:last-child:after{display:none}
.money{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.money>div{background:#fff;padding:20px 22px}.money p{font:800 30px/1.1 var(--display);margin:4px 0 0}
.seal{border:2px solid var(--gold2);background:#fffaf0}
.pitch p{font:400 21px/1.6 var(--serif);color:var(--ink)}
.yes h3{color:var(--ok)}.no h3{color:#9a3412}
.open{background:#fff7ec;border-color:#f6d9b5}.open p{margin:0 0 6px;color:#5a3a12}
.review{border:2px solid var(--navy)}
.rv{display:grid;gap:14px}
.rv fieldset{border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:0}
.rv legend{font:800 18px/1 var(--display);padding:0 8px}
.rv label{display:inline-flex;align-items:center;gap:8px;margin-right:22px;font-weight:600;cursor:pointer}
.rv input[type=radio]{width:20px;height:20px;accent-color:var(--orange)}
.rv textarea{display:block;width:100%;margin-top:12px;font:16.5px/1.5 var(--sans);padding:12px 14px;border:1px solid var(--line);border-radius:10px;min-height:76px;color:var(--ink)}
.btn{appearance:none;border:0;cursor:pointer;font:700 17px/1 var(--sans);padding:16px 24px;border-radius:999px;color:#1a1206;background:linear-gradient(180deg,var(--gold1),var(--gold2) 55%,var(--orange));box-shadow:0 8px 24px rgba(249,115,22,.3)}
.btn.alt{background:var(--navy);color:#fff;box-shadow:none}
#out{white-space:pre-wrap;font:15px/1.5 ui-monospace,Menlo,Consolas,monospace;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;margin-top:14px;display:none}
footer{padding:34px 0 46px;color:var(--mute);font-size:15px}
@media (max-width:760px){body{font-size:17px}.wrap{padding:0 16px}.grid2,.quotes,.stats,.money{grid-template-columns:1fr}.who{flex-direction:column;align-items:flex-start}
.stack>div:nth-child(2){margin-left:10px}.stack>div:nth-child(3){margin-left:20px}.card{padding:22px 18px}.cover{padding:44px 0 40px}}
@media print{body{background:#fff;font-size:11pt}.cover,.hero,blockquote,.stack>div{-webkit-print-color-adjust:exact;print-color-adjust:exact}.review,.noprint{display:none}.card,blockquote{break-inside:avoid;box-shadow:none}section.part{padding-top:24px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

JS = """
const $=s=>document.querySelector(s);
function gather(){let t='My review of the foundation\\n';
 document.querySelectorAll('.rv fieldset').forEach(f=>{const c=f.querySelector('input:checked'),n=f.querySelector('textarea').value.trim();
  t+='\\n'+f.dataset.part+': '+(c?c.value:'not reviewed yet')+(n?'\\n  '+n.replace(/\\n/g,'\\n  '):'');});return t+'\\n';}
$('#copy').addEventListener('click',async()=>{const t=gather(),o=$('#out');o.textContent=t;o.style.display='block';
 try{await navigator.clipboard.writeText(t);$('#copy').textContent='Copied. Paste it into the chat.';}catch(e){$('#copy').textContent='Select the text below and copy it';}});
$('#print').addEventListener('click',()=>window.print());
"""


def build(d):
    c = counts(d)
    name = val(d, "avatar", "name")
    profile = val(d, "avatar", "profile")
    biz = str(d["business"])
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
         f'<title>Your foundation · {E(biz)}</title><style>{CSS}</style></head><body>']
    o.append(f'<header class="cover"><div class="wrap"><div class="eyebrow">Build Room OS · Foundation review</div>'
             f'<h1>{E(biz)}:<br><em>who you serve, what you sell, where you stand.</em></h1>'
             f'<p>Everything later is built on these three. Read them, change anything that is not you, then say go.'
             + (f' Prepared {E(str(d["date"]))}.' if d.get("date") else "") + '</p>'
             f'<div class="stats"><div class="stat c"><b>{c["confirmed"]}</b><span>lines confirmed by you</span></div>'
             f'<div class="stat f"><b>{c["files"]}</b><span>lines from your own files and pages</span></div>'
             f'<div class="stat d"><b>{c["drafted"]}</b><span>lines drafted for you to check</span></div></div></div></header><div class="edge"></div>')
    o.append('<main class="wrap"><div class="how"><b>How to read this.</b> Every line carries a tag. '
             '<span class="b confirmed">Confirmed by you</span> is your own word. <span class="b files">From your files</span> was found in your documents or public pages; hover to see where. '
             '<span class="b drafted">Drafted for you</span> was written for you and is the part to check hardest.</div>')

    # ---- 1. the ideal client
    o.append('<section class="part" id="avatar"><div class="num">Part one</div><h2>Your ideal client</h2>')
    if name or profile:
        o.append('<div class="card who">' + (f'<div class="mono" aria-hidden="true">{E(initials(name["v"]))}</div>' if name else "") + '<div>'
                 + (f'<div class="nm">{E(str(name["v"]))} {badge(name)}</div>' if name else "")
                 + (f'<div class="pf">{E(str(profile["v"]))} {badge(profile)}</div>' if profile else "") + '</div></div>')
    qs = items(d, "avatar", "language", "quotes")
    if qs:
        o.append('<h3>In their own words</h3><div class="quotes">' + "".join(
            f'<blockquote><span class="t">{E(str(q["v"]))}</span><cite>{E(str(q.get("source", "")))} {badge(q)}</cite></blockquote>' for q in qs) + '</div><div style="height:20px"></div>')
    pains = [block(d, "avatar", k, l, "") for k, l in (("pain_surface", "What they complain about"), ("pain_emotional", "What it costs them"), ("pain_identity", "What they tell themselves"))]
    if any(pains):
        o.append('<div class="card"><h3>What keeps them stuck</h3><div class="stack">' + "".join(pains) + '</div></div>')
    job = "".join(block(d, "avatar", k, l) for k, l in (("job_functional", "What they are trying to get done"), ("job_emotional", "How they want to feel"), ("job_identity", "Who they want to be")))
    dream = "".join(block(d, "avatar", k, l) for k, l in (("dream_90", "In 90 days"), ("dream_year", "In a year")))
    if job or dream:
        o.append('<div class="grid2">' + (f'<div class="card"><h3>What they are really hiring you for</h3>{job}</div>' if job else "")
                 + (f'<div class="card"><h3>What they want</h3>{dream}</div>' if dream else "") + '</div><div style="height:20px"></div>')
    move = "".join(block(d, "avatar", k, l) for k, l in (("force_push", "What pushes them to change"), ("force_pull", "What pulls them toward you"), ("trigger", "What makes them act now")))
    stall = "".join(block(d, "avatar", k, l) for k, l in (("force_anxiety", "What worries them about switching"), ("force_habit", "What keeps them where they are")))
    stall += lst(d, "avatar", "objections_spoken", "What they say when they hesitate") + lst(d, "avatar", "objections_unspoken", "What they do not say")
    if move or stall:
        o.append('<div class="grid2">' + (f'<div class="card yes"><h3>Why they move</h3>{move}</div>' if move else "")
                 + (f'<div class="card no"><h3>Why they stall</h3>{stall}</div>' if stall else "") + '</div><div style="height:20px"></div>')
    neg = block(d, "avatar", "negative", "Who this is not for")
    if neg:
        o.append(f'<div class="card">{neg}</div>')
    o.append('</section>')

    # ---- 2. the offer
    o.append('<section class="part" id="offer"><div class="num">Part two</div><h2>Your offer</h2>')
    oname, promise = val(d, "offer", "name"), val(d, "offer", "promise")
    o.append('<div class="card hero">' + (f'<div class="nm">{E(str(oname["v"]))} {badge(oname)}</div>' if oname else "")
             + f'<div class="k">The promise {badge(promise)}</div><p class="big">{E(str(promise["v"]))}</p></div>')
    ph = items(d, "offer", "phases", "list")
    left = block(d, "offer", "structure", "How it runs")
    if ph:
        left += '<div class="fld"><div class="k">The journey</div><ol class="steps">' + "".join(f'<li>{E(str(x["v"]))} {badge(x)}</li>' for x in ph) + '</ol></div>'
    right = lst(d, "offer", "deliverables", "What they receive")
    if left or right:
        o.append('<div class="grid2">' + (f'<div class="card">{left}</div>' if left else "") + (f'<div class="card">{right}</div>' if right else "") + '</div><div style="height:20px"></div>')
    v, inv = val(d, "offer", "value"), val(d, "offer", "investment")
    if v or inv:
        o.append('<div class="money">' + "".join(f'<div><div class="k">{E(l)} {badge(x)}</div><p>{E(str(x["v"]))}</p></div>'
                                                  for l, x in (("Value of everything included", v), ("Investment", inv)) if x) + '</div><div style="height:20px"></div>')
    g = block(d, "offer", "guarantee", "Guarantee")
    if g:
        o.append(f'<div class="card seal">{g}</div>')
    p = block(d, "offer", "pitch", "The 60-second pitch")
    if p:
        o.append(f'<div class="card pitch">{p}</div>')
    tail = block(d, "offer", "belief", "The one belief") + block(d, "offer", "urgency", "Why now")
    if tail:
        o.append(f'<div class="card">{tail}</div>')
    o.append('</section>')

    # ---- 3. positioning
    o.append('<section class="part" id="positioning"><div class="num">Part three</div><h2>Where you stand</h2>')
    st, df = val(d, "positioning", "statement"), val(d, "positioning", "differentiator")
    lead, lead_label = (st, "Positioning statement") if st else (df, "What makes you different")
    tg = val(d, "positioning", "tagline")
    o.append('<div class="card hero">' + (f'<div class="nm">{E(str(tg["v"]))} {badge(tg)}</div>' if tg else "")
             + f'<div class="k">{lead_label} {badge(lead)}</div><p class="big">{E(str(lead["v"]))}</p></div>')
    a = block(d, "positioning", "value_prop", "Value in one sentence") + (block(d, "positioning", "differentiator", "What makes you different") if st else "") \
        + block(d, "positioning", "advantage", "Your unfair advantage")
    b = block(d, "positioning", "alternative", "What they would do without you") + block(d, "positioning", "category", "What they would call it") \
        + block(d, "positioning", "villain", "What is wrong with how your space works")
    if a or b:
        o.append('<div class="grid2">' + (f'<div class="card">{a}</div>' if a else "") + (f'<div class="card">{b}</div>' if b else "") + '</div><div style="height:20px"></div>')
    fy, nfy = items(d, "positioning", "for_you", "list"), items(d, "positioning", "not_for_you", "list")
    if fy or nfy:
        mk = lambda xs: "<ul>" + "".join(f'<li>{E(str(x["v"]))} {badge(x)}</li>' for x in xs) + "</ul>"  # noqa: E731
        o.append('<div class="grid2">' + (f'<div class="card yes"><h3>For you if</h3>{mk(fy)}</div>' if fy else "")
                 + (f'<div class="card no"><h3>Not for you if</h3>{mk(nfy)}</div>' if nfy else "") + '</div><div style="height:20px"></div>')
    o.append('</section>')

    op = open_fields(d)
    if op:
        o.append('<section class="part"><div class="card open"><h3>Still open</h3><p>Nothing reliable was found for these, so they were left blank instead of guessed. Add any you can in your review.</p><p><b>'
                 + E("; ".join(f"{t}: {l}" for t, l in op)) + '</b></p></div></section>')

    o.append('<section class="part"><div class="card review"><h2 style="font-size:32px;margin-top:0">Your review</h2>'
             '<p style="margin-top:0">Mark each part, add what to change, then copy your review and paste it into the chat. Nothing goes further until you say so.</p><div class="rv">')
    for part, title, _f in PARTS:
        o.append(f'<fieldset data-part="{E(title)}"><legend>{E(title)}</legend>'
                 f'<label><input type="radio" name="{part}" value="Looks right"> Looks right</label>'
                 f'<label><input type="radio" name="{part}" value="Change this"> Change this</label>'
                 f'<textarea aria-label="What to change in {E(title)}" placeholder="What should change? Your own words are best."></textarea></fieldset>')
    o.append('</div><p style="margin:18px 0 0"><button class="btn" id="copy" type="button">Copy my review</button> '
             '<button class="btn alt noprint" id="print" type="button">Print or save as PDF</button></p><div id="out" aria-live="polite"></div></div></section>')
    o.append(f'</main><footer class="wrap">Build Room OS, from AI Momentum Labs. This page is a draft for your review and lives on your computer. '
             f'It describes your business as it was found and drafted. It does not promise results.</footer><script>{JS}</script></body></html>')
    return "".join(o)


def text(d):
    c = counts(d)
    out = [f"# Your foundation: {d['business']}", "",
           f"{c['confirmed']} lines confirmed by you, {c['files']} from your files and pages, {c['drafted']} drafted for you to check.",
           "Tags: [you] your own word · [files] found in your documents or pages · [draft] written for you, check it hardest.", ""]
    tag = {"confirmed": "[you]", "files": "[files]", "drafted": "[draft]"}
    for part, title, fields in PARTS:
        out += [f"## {title}", ""]
        for key, label, kind in fields:
            xs = items(d, part, key, kind)
            if not xs:
                continue
            if kind == "text":
                out.append(f"- **{label}:** {xs[0]['v']} {tag[xs[0]['basis']]}")
            else:
                out.append(f"- **{label}:**")
                for x in xs:
                    q = f"“{x['v']}” ({x.get('source', '')})" if kind == "quotes" else str(x["v"])
                    out.append(f"  - {q} {tag[x['basis']]}")
        out.append("")
    op = open_fields(d)
    if op:
        out += ["## Still open", "", "Left blank instead of guessed: " + "; ".join(f"{t}: {l}" for t, l in op) + ".", ""]
    out += ["## Your review", "", "For each of the three parts, tell me: looks right, or what to change. Nothing goes further until you say so."]
    return "\n".join(out)


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0] not in ("check", "build", "text") or (a[0] == "build" and len(a) != 3):
        sys.exit(__doc__)
    d = load(a[1])
    probs = problems(d)
    if a[0] == "check" or probs:
        for p in probs:
            print("FIX  " + p)
        if a[0] == "check":
            c = counts(d)
            print(f"{c['confirmed']} confirmed, {c['files']} from files, {c['drafted']} drafted, {len(open_fields(d))} still open. {len(probs)} to fix.")
        sys.exit(1 if probs else 0)
    if a[0] == "text":
        print(text(d))
        return
    out = Path(a[2])
    if out.suffix.lower() != ".html":
        sys.exit("The output file must end in .html")
    out.write_text(build(d), encoding="utf-8")
    print(f"Wrote {out}. Open it in a browser.")


if __name__ == "__main__":
    main()
