#!/usr/bin/env python3
"""Today on LinkedIn: one page of the few things to do by hand today, each with the words ready to copy.

  li_today.py check TODAY.json [--pipeline linkedin/pipeline.json] [--premium]
  li_today.py build TODAY.json OUT.html [--pipeline linkedin/pipeline.json] [--premium]

TODAY.json is written by the session from the pipeline's daily list and the prospect file:
  {"date": "2026-11-24", "items": [
     {"name": "Dana Ruiz", "url": "https://www.linkedin.com/in/danaruiz", "role": "Owner", "company": "Ruiz Dental",
      "do": "comment" | "request" | "note" | "message" | "reply" | "follow-up" | "invite",
      "why": "Posted on Nov 18 about hiring a second hygienist",        what the member noticed, or what they last said
      "stage": "open",                                                   for message, reply and invite
      "exchanges": 2, "they_asked": false,                               for reply and invite
      "text": "the words to send"}]}                                     not for a blank request

The page will not build while any line would be refused by li_prospect.py: a pitch, a link, flattery or an invented
detail in an opener; more than one question; an early invitation. It also refuses more than 20 requests or 15 messages
in a day, and anyone who asked not to be contacted (when given the pipeline file).

It sends nothing and opens nothing. The member presses a button to open a profile, copies the words, and sends them.
One self-contained file. Standard library only.
"""
import html, importlib.util, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lp = _load("li_prospect")
E = html.escape
DO = {"comment": ("Comment on their post", "Open the post, paste, edit, post. Send the request in a day or two."),
      "request": ("Send a blank connection request", "Open the profile, press Connect, send without a note."),
      "note": ("Send a connection request with this note", "Open the profile, press Connect, Add a note, paste, edit, send."),
      "message": ("Send this first message", "Open the profile, press Message, paste, edit, send."),
      "reply": ("Reply to them", "Open the conversation, paste, edit, send."),
      "follow-up": ("Send this follow-up", "Open the conversation, paste, edit, send. After the second follow-up, stop."),
      "invite": ("Invite them to a call", "Open the conversation, paste, edit, send. The booking link goes in your next message, after they say yes.")}
MAX_REQUESTS, MAX_MESSAGES = 20, 15


def problems(d, pipeline=None, premium=False):
    out = []
    items = d.get("items") if isinstance(d, dict) else None
    if not isinstance(items, list) or not items:
        return ['the file must be {"date": ..., "items": [...]} with at least one thing to do']
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("date", ""))):
        out.append("date: YYYY-MM-DD")
    barred = set()
    if pipeline:
        try:
            pm = _load("li_pipeline")
            barred = {s["hash"] for s in json.loads(Path(pipeline).read_text(encoding="utf-8")).get("suppressed", [])}
        except (OSError, ValueError, KeyError) as e:
            out.append(f"cannot read the pipeline file ({e})")
            pm = None
    for i, it in enumerate(items, 1):
        if not isinstance(it, dict):
            out.append(f"item {i}: not an object")
            continue
        tag = str(it.get("name") or f"item {i}")
        do = it.get("do")
        if do not in DO:
            out.append(f"{tag}: do is one of {', '.join(DO)}")
            continue
        url = str(it.get("url", "")).strip()
        if not re.match(r"https://([a-z]+\.)?linkedin\.com/(in|posts|feed)/\S+", url, re.I):
            out.append(f"{tag}: needs the link to open (their profile, or the post for a comment)")
        elif pipeline and barred and pm and (pm.url_hashes(url) & barred):
            out.append(f"{tag}: asked not to be contacted. Take them off the list")
        if not str(it.get("name", "")).strip():
            out.append(f"item {i}: name is missing")
        text, why = str(it.get("text", "")).strip(), str(it.get("why", "")).strip()
        if do == "request":
            if text:
                out.append(f"{tag}: a blank request has no text")
            continue
        if not text:
            out.append(f"{tag}: no words to send")
            continue
        if do == "comment":
            out += [f"{tag}: {x}" for x in lp.comment_problems(why, text)]
        elif do in ("note", "message") and it.get("stage", "open") == "open":
            out += [f"{tag}: {x}" for x in lp.opener_problems("C2" if do == "note" else "DM", text, why, premium)]
        elif do == "follow-up":
            if len(text) > lp.DM_MAX:
                out.append(f"{tag}: {len(text)} characters; keep it under {lp.DM_MAX}")
            if lp.PITCH.search(text) or lp.PRESSURE.search(text) or lp.LINK.search(text):
                out.append(f"{tag}: a follow-up adds one useful thought or lets them off the hook. No pitch, no link, no pressure")
            if re.search(r"\b(just (bumping|following up|checking in)|circling back|any thoughts)\b", text, re.I):
                out.append(f"{tag}: \"just following up\" adds nothing. Give one new thought, or let them off the hook")
        else:
            stage = "invite" if do == "invite" else it.get("stage")
            if stage not in lp.STAGES:
                out.append(f"{tag}: stage is one of {', '.join(lp.STAGES)}")
            else:
                out += [f"{tag}: {x}" for x in lp.say_problems(stage, text, int(it.get("exchanges") or 0), bool(it.get("they_asked")))]
    n_req = sum(1 for it in items if isinstance(it, dict) and it.get("do") in ("request", "note"))
    n_msg = sum(1 for it in items if isinstance(it, dict) and it.get("do") in ("message", "reply", "follow-up", "invite"))
    if n_req > MAX_REQUESTS:
        out.append(f"{n_req} connection requests in one day. Keep it to {MAX_REQUESTS}; LinkedIn stops invitations for a week when you hit its limit")
    if n_msg > MAX_MESSAGES:
        out.append(f"{n_msg} messages in one sitting. Keep it to {MAX_MESSAGES}, written properly")
    if sum(1 for it in items if isinstance(it, dict) and it.get("do") == "note") > 3 and not premium:
        out.append("more than three connection notes. A free account gets only a few a month: keep notes for the best three and send the rest blank")
    return out


CSS = """
:root{--navy:#0b1020;--ink:#0f1424;--ink2:#2b3247;--mute:#667089;--line:#e2e6ef;--panel:#f5f6fa;--gold1:#ffe7a3;--gold2:#ffb547;--orange:#f97316;--cyan:#4fe3ff;--ok:#0f7a4d;--okbg:#e7f6ee;
--sans:"Inter","SF Pro Text",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--display:"Inter Tight","SF Pro Display",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
*{box-sizing:border-box}body{margin:0;background:var(--panel);color:var(--ink);font:18px/1.55 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}:focus-visible{outline:3px solid var(--cyan);outline-offset:2px}
.cover{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:44px 0 36px}
.cover:before{content:"";position:absolute;inset:0;background:radial-gradient(800px 460px at 90% -10%,rgba(249,115,22,.36),transparent 62%)}.cover>*{position:relative}
.eyebrow{font:700 13px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
h1{font:800 clamp(32px,5.6vw,54px)/1.05 var(--display);letter-spacing:-.03em;margin:14px 0 10px}
h1 em{font-style:normal;background:linear-gradient(180deg,var(--gold1),var(--gold2) 50%,var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
.cover p{color:#cdd4ea;margin:0;max-width:620px}.edge{height:6px;background:linear-gradient(90deg,var(--orange),var(--gold2),var(--gold1))}
.bar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:10px 0;font:600 16px/1.3 var(--sans)}
.bar .wrap{display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap}.meter{flex:1;min-width:140px;height:8px;border-radius:999px;background:var(--line);overflow:hidden}.meter i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--orange),var(--gold2));transition:width .2s}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 22px;margin:18px 0;box-shadow:0 8px 22px rgba(11,16,32,.06)}
.card.done{opacity:.55}.top{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}
.who b{font:800 21px/1.2 var(--display)}.who span{display:block;color:var(--mute);font-size:16px}
.do{font:700 13px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--orange);margin-top:14px}
.why{color:var(--ink2);font-size:16.5px;margin:6px 0 0}.words{font:500 19px/1.5 var(--serif);background:#fbf7ee;border-left:5px solid var(--gold2);border-radius:0 12px 12px 0;padding:12px 16px;margin:12px 0 0;white-space:pre-wrap}
.how{color:var(--mute);font-size:15.5px;margin:10px 0 0}.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;align-items:center}
.btn{appearance:none;cursor:pointer;display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:12px;font:700 16px/1 var(--sans);text-decoration:none;border:1px solid #d8deee;background:linear-gradient(180deg,#f8f9fd,#eef1f9);color:var(--navy)}
.btn.go{border:0;color:#1a1206;background:linear-gradient(180deg,var(--gold1),var(--gold2) 55%,var(--orange))}
label.tick{display:inline-flex;align-items:center;gap:8px;font:600 16px/1 var(--sans);min-height:44px;cursor:pointer}label.tick input{width:22px;height:22px}
.then{font-size:15px;color:var(--mute);margin-top:10px}
.note{background:#fff;border:1px dashed #c9d0e2;border-radius:14px;padding:16px 18px;color:var(--ink2);font-size:16.5px;margin:22px 0}
footer{color:var(--mute);font-size:15px;padding:18px 0 48px}
@media print{.bar,.btn,label.tick{display:none}.card{break-inside:avoid;box-shadow:none}.cover{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""
JS = """
var KEY="li-today-"+document.body.getAttribute("data-date"),done={};try{done=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function paint(){var n=0,all=document.querySelectorAll(".card");all.forEach(function(c){var on=!!done[c.id];c.classList.toggle("done",on);c.querySelector("input").checked=on;if(on)n++});
document.getElementById("count").textContent=n+" of "+all.length+" done";document.getElementById("fill").style.width=(all.length?100*n/all.length:0)+"%"}
document.querySelectorAll(".card input").forEach(function(i){i.addEventListener("change",function(){done[i.closest(".card").id]=i.checked;try{localStorage.setItem(KEY,JSON.stringify(done))}catch(e){}paint()})});
document.querySelectorAll("[data-copy]").forEach(function(b){b.addEventListener("click",function(){navigator.clipboard.writeText(document.getElementById(b.getAttribute("data-copy")).textContent).then(function(){var o=b.textContent;b.textContent="Copied";setTimeout(function(){b.textContent=o},1500)})})});
paint();
"""


def build(d):
    items = d["items"]
    mins = max(5, round(sum({"request": 0.5, "comment": 2}.get(it["do"], 1.5) for it in items)))
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Today on LinkedIn · {E(str(d["date"]))}</title><style>{CSS}</style></head><body data-date="{E(str(d["date"]))}">']
    o.append(f'<header class="cover"><div class="wrap"><div class="eyebrow">Build Room OS · LinkedIn · {E(str(d["date"]))}</div><h1>Today: <em>{len(items)} {"person" if len(items) == 1 else "people"}.</em></h1>'
             f'<p>About {mins} minutes. Open, copy, make it sound like you, send. You do every step yourself, which is what keeps your account safe.</p></div></header><div class="edge"></div>'
             '<div class="bar"><div class="wrap"><span id="count"></span><span class="meter"><i id="fill"></i></span></div></div><main class="wrap">')
    for i, it in enumerate(items, 1):
        title, how = DO[it["do"]]
        sub = " · ".join(x for x in (str(it.get("role", "")).strip(), str(it.get("company", "")).strip()) if x)
        text = str(it.get("text", "")).strip()
        o.append(f'<div class="card" id="c{i}"><div class="top"><div class="who"><b>{E(str(it["name"]))}</b>' + (f'<span>{E(sub)}</span>' if sub else "") + '</div>'
                 f'<label class="tick"><input type="checkbox" aria-label="Done: {E(str(it["name"]))}"> Done</label></div>'
                 f'<div class="do">{E(title)}</div>' + (f'<p class="why">{E(str(it["why"]))}</p>' if it.get("why") else "")
                 + (f'<p class="words" id="w{i}">{E(text)}</p>' if text else "") + f'<p class="how">{E(how)}</p><div class="row">'
                 f'<a class="btn go" href="{E(str(it["url"]), quote=True)}" target="_blank" rel="noopener noreferrer">Open on LinkedIn</a>'
                 + (f'<button class="btn" type="button" data-copy="w{i}">Copy the words</button>' if text else "") + '</div>'
                 + f'<div class="then">When it is done, tell Claude: “{E({"comment": "Commented on", "request": "Sent a request to", "note": "Sent a request to"}.get(it["do"], "Sent to"))} {E(str(it["name"]))}.”</div></div>')
    o.append('<div class="note"><b>When someone replies,</b> paste what they wrote to Claude and ask what to say next. If anyone says no or asks you to stop, that is final: tell Claude and they come off the list for good.</div>')
    o.append(f'</main><footer class="wrap">Build Room OS, from AI Momentum Labs. This page is a file on your own computer. It sends nothing and opens nothing by itself, and nothing on it promises replies, calls or clients.</footer><script>{JS}</script></body></html>')
    return "".join(o)


def main():
    a = sys.argv[1:]
    premium = "--premium" in a
    a = [x for x in a if x != "--premium"]
    pipeline = None
    if "--pipeline" in a:
        k = a.index("--pipeline")
        if k + 1 >= len(a):
            sys.exit(__doc__)
        pipeline = a[k + 1]
        del a[k:k + 2]
    if len(a) < 2 or a[0] not in ("check", "build") or (a[0] == "build" and len(a) != 3):
        sys.exit(__doc__)
    try:
        d = json.loads(Path(a[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read {a[1]}: {e}")
    probs = problems(d, pipeline, premium)
    if a[0] == "check" or probs:
        for p in probs:
            print("FIX  " + p)
        if a[0] == "check":
            print(f"{len(d.get('items') or []) if isinstance(d, dict) else 0} things to do. {len(probs)} to fix.")
        sys.exit(1 if probs else 0)
    out = Path(a[2])
    if out.suffix.lower() != ".html":
        sys.exit("The output file must end in .html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(d), encoding="utf-8")
    print(f"Wrote {out}. Tell the member to open it by double-clicking the file.")


if __name__ == "__main__":
    main()
