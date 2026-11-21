#!/usr/bin/env python3
"""Your Build: one page that hands a finished Autopilot run to the member.

  handover.py build --dir autopilot OUT.html [--business NAME]

It reads autopilot/run.json (written by autopilot.py) and lists what was drafted with a link to each document,
what each draft still needs from the member, what could not be drafted, and the sessions that need the member,
each with the sentence that starts it. One self-contained file. It works offline and prints cleanly.

Standard library only. It reads run.json and writes one HTML file. Nothing else.
"""
import argparse, html, importlib.util, json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("autopilot_keeper", HERE / "autopilot.py")
keeper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(keeper)
TOOL = keeper.TOOL

# What each drafted piece is for, in a line the member would say.
FOR = {
    "audience-insight": "The words your clients use in public, with where each was found.",
    "ideal-client-avatar": "Who you serve, in enough detail to write to one person.",
    "signature-offer": "What you sell: the promise, the journey, the price and the pitch.",
    "positioning-messaging": "Where you stand, and why someone picks you.",
    "offer-deep-dive": "Your offer pressure-tested: value, guarantee and the numbers behind it.",
    "offer-page-copy": "The page that does the selling when you are not in the room.",
    "funnel-map": "The path from stranger to client, with the emails written.",
    "lead-capture": "The opt-in page, the free resource and its delivery.",
    "sales-script": "What to ask on the call, and what to say when they hesitate.",
    "decision-machine": "The follow-up for every yes and every no.",
    "leadgen": "The outreach, referral and warm-network scripts.",
    "linkedin": "Your profile and your first posts, in your words.",
    "search-answer-engine": "Your Google profile fixes and your first answer page.",
}
E = html.escape

CSS = """
:root{--navy:#0b1020;--ink:#0f1424;--ink2:#2b3247;--mute:#667089;--line:#e2e6ef;--panel:#f5f6fa;--paper:#fff;
--gold1:#ffe7a3;--gold2:#ffb547;--orange:#f97316;--cyan:#4fe3ff;--ok:#0f7a4d;--okbg:#e7f6ee;--amber:#92400e;--amberbg:#fff1d6;--link:#b4530a;
--sans:"Inter","SF Pro Text",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--display:"Inter Tight","SF Pro Display",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--panel);color:var(--ink);font:18px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
a{color:var(--link);font-weight:700}:focus-visible{outline:3px solid var(--cyan);outline-offset:2px}
.cover{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:60px 0 52px}
.cover:before{content:"";position:absolute;inset:0;background:radial-gradient(900px 520px at 88% -8%,rgba(249,115,22,.36),transparent 62%),radial-gradient(760px 520px at -6% 108%,rgba(79,227,255,.16),transparent 60%)}
.cover>*{position:relative}
.eyebrow{font:700 13px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
h1{font:800 clamp(38px,6.2vw,68px)/1.03 var(--display);letter-spacing:-.03em;margin:16px 0 14px}
h1 em{font-style:normal;background:linear-gradient(180deg,var(--gold1),var(--gold2) 50%,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.cover p{font-size:clamp(18px,2.1vw,21px);color:#cdd4ea;max-width:720px;margin:0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.14);border-radius:16px;overflow:hidden;margin-top:32px}
.stat{background:rgba(11,16,32,.74);padding:20px 22px}
.stat b{display:block;font:800 40px/1 var(--display)}.stat span{display:block;font-size:15px;color:#aab3cf;margin-top:8px}
.stat.a b{color:#7be3ac}.stat.b b{color:var(--gold2)}.stat.c b{color:#9db8ff}
.edge{height:6px;background:linear-gradient(90deg,var(--orange),var(--gold2),var(--gold1))}
section{padding:48px 0 4px}
.num{font:800 14px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--orange)}
h2{font:800 clamp(28px,4vw,40px)/1.08 var(--display);letter-spacing:-.025em;margin:10px 0 8px}
.sub{color:var(--mute);margin:0 0 22px;max-width:760px}
h3{font:800 21px/1.2 var(--display);margin:0 0 4px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:18px;box-shadow:0 1px 2px rgba(15,20,36,.06),0 10px 34px rgba(15,20,36,.08);padding:26px;margin-bottom:18px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid>.card{margin:0}
.for{color:var(--ink2);margin:0 0 14px}
.k{font:700 12.5px/1.5 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin:14px 0 6px}
ul{margin:0;padding:0;list-style:none}
.files li{margin:6px 0;padding-left:26px;position:relative;word-break:break-word}
.files li:before{content:"";position:absolute;left:6px;top:.62em;width:8px;height:8px;border-radius:50%;background:var(--orange)}
.todo li{margin:8px 0}
.todo label{display:flex;gap:10px;align-items:flex-start;cursor:pointer}
.todo input{flex:none;width:20px;height:20px;margin-top:4px;accent-color:var(--orange)}
.todo input:checked+span{color:var(--mute);text-decoration:line-through}
.first{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.first .card{margin:0}
.n{display:inline-grid;place-items:center;width:38px;height:38px;border-radius:50%;font:800 17px/1 var(--display);color:#1a1206;background:linear-gradient(180deg,var(--gold1),var(--gold2) 55%,var(--orange));margin-bottom:12px}
.hero{background:var(--navy);color:#fff;border:0;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;inset:0;background:radial-gradient(620px 320px at 100% 0,rgba(249,115,22,.36),transparent 65%)}
.hero>*{position:relative}.hero p{color:#cdd4ea;margin:6px 0 0}.hero a{color:var(--gold2)}
.warn{background:#fff7ec;border-color:#f6d9b5}.warn p{margin:6px 0 0;color:#5a3a12}
.say{appearance:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;text-align:left;border:1px solid #d8deee;background:linear-gradient(180deg,#f8f9fd,#eef1f9);border-radius:12px;padding:11px 14px;font:600 16px/1.3 var(--sans);color:var(--navy);margin-top:12px}
.say small{flex:none;font:700 12px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}.say.done small{color:var(--ok)}
.why{color:var(--ink2);margin:0;font-size:16.5px}
.bar{height:10px;border-radius:999px;background:var(--line);overflow:hidden;margin-top:10px}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--orange),var(--gold2))}
#left{font-weight:700}
footer{padding:34px 0 46px;color:var(--mute);font-size:15px}
.btn{appearance:none;border:0;cursor:pointer;font:700 16px/1 var(--sans);padding:14px 20px;border-radius:999px;color:#fff;background:var(--navy)}
@media (max-width:760px){body{font-size:17px}.wrap{padding:0 16px}.grid,.stats,.first{grid-template-columns:1fr}.card{padding:22px 18px}.cover{padding:44px 0 40px}}
@media print{body{background:#fff;font-size:11pt}.cover,.hero{-webkit-print-color-adjust:exact;print-color-adjust:exact}.noprint,.say small{display:none}.card{break-inside:avoid;box-shadow:none}section{padding-top:22px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

JS = """
const KEY='br-your-build-'+document.title;
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const boxes=[...document.querySelectorAll('.todo input')];
function tally(){const left=boxes.filter(b=>!b.checked).length,el=document.getElementById('left');
 if(el){el.textContent=left===0?'All done.':left+' of '+boxes.length+' still to do';document.getElementById('fill').style.width=(boxes.length?100*(boxes.length-left)/boxes.length:0)+'%';}}
boxes.forEach(b=>{b.checked=!!saved[b.id];b.addEventListener('change',()=>{saved[b.id]=b.checked;try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}tally();});});tally();
document.addEventListener('click',async e=>{const b=e.target.closest('.say');if(!b)return;try{await navigator.clipboard.writeText(b.dataset.say)}catch(err){return}
 const s=b.querySelector('small');b.classList.add('done');s.textContent='Copied';setTimeout(()=>{b.classList.remove('done');s.textContent='Copy'},1600);});
const p=document.getElementById('print');if(p)p.addEventListener('click',()=>window.print());
"""


def business_name(folder):
    try:
        m = re.search(r"^\*\*Business:\*\*[ \t]*(.+)$", (folder / "BUILDROOM_BUSINESS_FILE.md").read_text(encoding="utf-8"), re.M)
    except OSError:
        return ""
    v = m.group(1).strip() if m else ""
    return "" if re.fullmatch(r"\[.*\]", v) else v


def file_item(out, folder, page_dir):
    """A link when the file is really there, plain text when it is not. Never a link out of the member's folder."""
    name = str(out)
    try:
        target = (folder / name).resolve()
        inside = target.is_file() and (folder.resolve() in target.parents)
    except (OSError, ValueError):
        inside = False
    if inside:
        rel = os.path.relpath(target, page_dir.resolve()).replace(os.sep, "/")
        return f'<li><a href="{E(rel, quote=True)}">{E(name)}</a></li>'
    return f'<li>{E(name)} <span style="color:var(--mute)">(not found where it was saved)</span></li>'


def say(phrase):
    return f'<button class="say" type="button" data-say="{E(phrase, quote=True)}"><span>&ldquo;{E(phrase)}&rdquo;</span><small>Copy</small></button>'


def build(run, folder, page_dir, business):
    steps = run.get("steps", [])
    by = {st: [s for s in steps if s.get("status") == st] for st in ("drafted", "partial", "blocked", "skipped", "pending")}
    made = [s for s in steps if s.get("status") in ("drafted", "partial")]
    gaps = sum(len(s.get("gaps") or []) for s in made)
    top = [e for e in keeper.rollup(run) if len(e["in"]) > 1][:5]
    needs = [t for t in keeper.TOOLS if t[3] == "needs_you"]
    approved = run.get("approved")
    title = f"Your Build · {business}" if business else "Your Build"
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><style>{CSS}</style></head><body>']
    lead = f"{E(business)}:<br>" if business else ""
    done_line = "Here is everything that was drafted, where it is saved, and what still needs you." if not by["pending"] \
        else "The run is not finished. Here is what is drafted so far. Say “Run autopilot” to carry on."
    o.append(f'<header class="cover"><div class="wrap"><div class="eyebrow">Build Room OS · Your Build</div>'
             f'<h1>{lead}<em>your first build, drafted.</em></h1><p>{E(done_line)} Started {E(str(run.get("started", "")))}.</p>'
             f'<div class="stats"><div class="stat a"><b>{len(made)}</b><span>pieces drafted for you' + (f', {len(by["partial"])} of them only in part' if by["partial"] else "") + '</span></div>'
             f'<div class="stat b"><b>{gaps}</b><span>things in them that still need you</span></div>'
             f'<div class="stat c"><b>{len(needs)}</b><span>sessions waiting for you to start</span></div></div></div></header><div class="edge"></div><main class="wrap">')

    o.append('<section><div class="num">Start here</div><h2>What to do first</h2><p class="sub">Everything on this page is a draft. Nothing was published, sent or paid for. It becomes real when you have checked it.</p>'
             '<div class="first"><div class="card"><span class="n">1</span><h3>Read the drafts</h3><p class="why">Open each one below and fix anything that does not sound like you. Lines marked [draft] were written for you.</p></div>'
             '<div class="card"><span class="n">2</span><h3>Fill what needs you</h3><p class="why">Each draft lists what is still missing. Tick them off here as you go. Your ticks are remembered on this computer.</p></div>'
             '<div class="card"><span class="n">3</span><h3>Publish what you have checked</h3><p class="why">Only you can put a page live or send an email. Do it one piece at a time.</p></div></div>')
    if top:
        o.append('<div class="card hero" style="margin-top:18px"><h3>Answer these first</h3><p>They are asked for in more than one draft, so each answer improves several at once.</p><ul style="margin-top:12px;list-style:disc;padding-left:22px">'
                 + "".join(f'<li style="margin:6px 0">{E(e["text"])} <span style="color:#aab3cf">({E(", ".join(e["in"]))})</span></li>' for e in top) + '</ul></div>')
    if gaps:
        o.append('<div class="card" style="margin-top:18px"><span id="left"></span><div class="bar"><i id="fill" style="width:0"></i></div></div>')
    o.append('</section>')

    reveal = folder / "autopilot" / "Foundation_Reveal.html"
    if approved or reveal.is_file() or any(x["slug"] in keeper.MUST for x in made):
        link = f' <a href="{E(os.path.relpath(reveal.resolve(), page_dir.resolve()).replace(os.sep, "/"), quote=True)}">Open your foundation page</a>.' if reveal.is_file() else ""
        when = f"You approved it on {E(str(approved.get('date', '')))}: “{E(str(approved.get('words', '')))}”" if approved else "It has not been approved yet, so nothing after it has run."
        o.append(f'<section><div class="card hero"><h3>Your foundation: who you serve, what you sell, where you stand</h3><p>{when}{link}</p></div></section>')

    if made:
        o.append('<section><div class="num">Drafted for you</div><h2>Your drafts</h2><p class="sub">In the order they were built. Each one reads what came before it.</p><div class="grid">')
        n = 0
        for s in made:
            slug = s["slug"]
            part = s.get("status") == "partial"
            o.append(f'<div class="card"><h3>{E(TOOL[slug][1])}' + (' <span style="font-weight:600;color:var(--amber);font-size:16px">· Partly drafted</span>' if part else "")
                     + f'</h3><p class="for">{E(FOR.get(slug, ""))}</p>')
            if s.get("outputs"):
                o.append('<div class="k">Saved as</div><ul class="files">' + "".join(file_item(x, folder, page_dir) for x in s["outputs"]) + '</ul>')
            if s.get("gaps"):
                o.append('<div class="k">Still needs you</div><ul class="todo">')
                for g in s["gaps"]:
                    n += 1
                    o.append(f'<li><label><input type="checkbox" id="g{n}"><span>{E(str(g))}</span></label></li>')
                o.append('</ul>')
            if s.get("note"):
                o.append(f'<div class="k">{"What was and was not drafted" if part else "Note"}</div><p class="why">{E(str(s["note"]))}</p>')
            o.append('</div>')
        o.append('</div></section>')

    rest = [("Could not be drafted", by["blocked"], True), ("Left out", by["skipped"], False), ("Not reached yet", by["pending"], False)]
    if any(xs for _t, xs, _p in rest):
        o.append('<section><div class="num">Not drafted</div><h2>What was not drafted, and why</h2>')
        for label, xs, with_phrase in rest:
            for s in xs:
                slug = s["slug"]
                why = s.get("note") or ("The run stopped before this step." if label == "Not reached yet" else "")
                o.append(f'<div class="card warn"><h3>{E(TOOL[slug][1])} <span style="font-weight:600;color:var(--amber);font-size:16px">· {E(label)}</span></h3><p>{E(str(why))}</p>'
                         + (say(TOOL[slug][2]) if with_phrase else "") + '</div>')
        o.append('</section>')

    o.append('<section><div class="num">Yours to start</div><h2>Sessions that need you</h2><p class="sub">These depend on something only you have, so Autopilot left them alone. Not all of them will fit your business; pick what does. Each starts with one sentence. Press it to copy, then paste it into Claude or Codex.</p><div class="grid">')
    for _slug, name, phrase, _mode, why in needs:
        o.append(f'<div class="card"><h3>{E(name)}</h3><p class="why">Not run because {E(why)}.</p>{say(phrase)}</div>')
    o.append('</div></section>')

    o.append('<section class="noprint"><button class="btn" id="print" type="button">Print or save as PDF</button></section>')
    o.append(f'</main><footer class="wrap">Build Room OS, from AI Momentum Labs. This page lists drafts on your own computer. Nothing here was published, sent or paid for, '
             f'and nothing on it promises results.</footer><script>{JS}</script></body></html>')
    return "".join(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("--dir", required=True, help="the autopilot folder that holds run.json")
    p.add_argument("out")
    p.add_argument("--business")
    a = ap.parse_args()
    run = keeper.load(a.dir)
    unknown = [s.get("slug") for s in run.get("steps", []) if s.get("slug") not in TOOL]
    if unknown:
        sys.exit("run.json names steps this version does not know: " + ", ".join(map(str, unknown)))
    out = Path(a.out)
    if out.suffix.lower() != ".html":
        sys.exit("The output file must end in .html")
    folder = Path(a.dir).resolve().parent
    business = (a.business or business_name(folder)).strip()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(run, folder, out.parent, business), encoding="utf-8")
    print(f"Wrote {out}. Open it in a browser.")


if __name__ == "__main__":
    main()
