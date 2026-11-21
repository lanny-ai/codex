#!/usr/bin/env python3
"""LinkedIn Prospector: find people who match the member's ideal client, write an opening line from what
the member noticed about each one, and guide the conversation one question at a time.

Local only. It never opens LinkedIn, never searches, never sends, and never copies profile text. The member
runs every search and sends every message by hand, and tells this tool what they saw.

  li_prospect.py searches PLAN.json                 the searches to run, from the ideal client, and where to paste them
  li_prospect.py network PLAN.json Connections.csv [--max 40]
                                                    people the member is ALREADY connected to who match (start here)
  li_prospect.py check PROSPECTS.json [--premium]   every prospect has a real reason to fit and an honest opener
  li_prospect.py opener --kind C2|DM --hook "what you noticed" --text "the line" [--premium]
  li_prospect.py next --stage open|situation|problem|cost|want|invite [--exchanges N]
                                                    what the next message is for, and how to ask it
  li_prospect.py say --stage STAGE --text "the reply you drafted" [--exchanges N] [--they-asked]
                                                    check a drafted reply before the member sends it
  li_prospect.py handoff PROSPECTS.json             the li_pipeline.py lines that log each prospect

PLAN.json, written by the session from the member's ideal client (Business File section 2):
  {"titles": ["Practice owner", "Owner dentist"], "keywords": ["dental"], "exclude": ["student", "recruiter"],
   "locations": ["Colorado"], "industries": ["Dentists"], "company_size": "2 to 50", "seniority": ["Owner", "Partner"]}

PROSPECTS.json: at most 20 at a time, each one a person the member looked at themselves.
  {"prospects": [{"name": "Dana Ruiz", "url": "https://www.linkedin.com/in/danaruiz", "role": "Owner", "company": "Ruiz Dental",
     "fit": "A", "why": ["Owner of a two-location dental practice"], "connected": false,
     "hook": {"kind": "post", "note": "Posted on Nov 18 about hiring a second hygienist", "link": "https://www.linkedin.com/posts/..."},
     "opener": {"kind": "C2", "text": "..."}}]}
  hook kinds: post, comment, new-role, launch, about, shared, none. With "none" there is nothing to personalise:
  the approach is a blank request (C1) and no opener is written.

Standard library only. Exit code 1 when something must be fixed.
"""
import argparse, csv, json, re, sys
from pathlib import Path

MAX_BATCH = 20
NOTE_FREE, NOTE_PREMIUM, DM_MAX, HOOK_MAX = 200, 300, 400, 200
STAGES = ("open", "situation", "problem", "cost", "want", "invite")
HOOKS = ("post", "comment", "new-role", "launch", "about", "shared", "none")
SIGNAL = {"post": "sig:posted-problem", "comment": "sig:commented-peer-post", "new-role": "sig:new-role", "launch": "sig:launch",
          "about": "sig:fit", "shared": "sig:fit", "none": "sig:fit"}
PITCH = re.compile(r"\b(i help|we help|i work with|my (program|offer|services?|course|company|firm)|our (program|services?|team)|book a (call|time)|schedule|"
                   r"calendar|free (call|consult\w*|audit|session|review|trial)|demo|discount|pric(e|ing)|sign up|spots?|limited|proposal|clients? like you)\b", re.I)
LINK = re.compile(r"https?://|www\.|\b\w+\.(com|co|io|net|org)\b", re.I)
FLATTERY = re.compile(r"\b(love(d)? your|impress(ed|ive)|amazing|awesome|incredible|inspir(ing|ed)|great (profile|post|work|content)|fantastic|huge fan|"
                      r"came across your profile|hope (this|you) (finds|are))\b", re.I)
PRESSURE = re.compile(r"\b(act now|last chance|don'?t miss|only \d+|today only|guarantee[ds]?|risk[- ]free|you need to|you must|you should really)\b", re.I)
EASY_NO = re.compile(r"\b(if not|no (problem|worries|pressure)|either way|totally fine|not a fit|feel free to say no|happy to leave it)\b", re.I)
COMMON = set("""about after again also been before being could does from have here into just more most much only other over same should some such than that
their them then there these they this those through very were what when where which while will with would your yours curious noticed thanks
thank hello there really think thought wondering wanted things something anything still today recently posted post comment""".split())


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"Cannot read {path}: {e}")


def quoted(xs):
    xs = [str(x).strip() for x in xs or [] if str(x).strip()]
    return "(" + " OR ".join(f'"{x}"' if " " in x else x for x in xs) + ")" if len(xs) > 1 else (f'"{xs[0]}"' if xs and " " in xs[0] else (xs[0] if xs else ""))


def plan_problems(p):
    out = []
    if not isinstance(p, dict):
        return ["the plan must be an object"]
    if not 1 <= len(p.get("titles") or []) <= 8:
        out.append("titles: give 1 to 8 job titles the ideal client actually uses about themselves")
    for k in ("titles", "keywords", "exclude", "locations", "industries", "seniority"):
        if k in p and not (isinstance(p[k], list) and all(isinstance(x, str) and x.strip() for x in p[k])):
            out.append(f"{k}: a list of plain words")
    if not (p.get("keywords") or p.get("industries")):
        out.append("keywords or industries: without one of them a title search returns everyone with that title")
    return out


def cmd_searches(a):
    p = load(a.plan)
    probs = plan_problems(p)
    if probs:
        for x in probs:
            print("FIX  " + x)
        sys.exit(1)
    t, k, ex = quoted(p["titles"]), quoted(p.get("keywords")), quoted(p.get("exclude"))
    boolean = " AND ".join(x for x in (t, k) if x) + (f" NOT {ex}" if ex else "")
    print("Run these yourself, on LinkedIn, in this order. Nothing here searches for you.\n")
    print("1. YOUR OWN NETWORK FIRST. People who already know you answer far more often than strangers.")
    print("   Export your connections (Settings, Data privacy, Get a copy of your data, Connections), then: li_prospect.py network PLAN.json Connections.csv\n")
    print("2. LINKEDIN SEARCH (free). Paste into the search bar, choose People, then set the filters:")
    print(f"   {boolean}")
    print("   Filters: Connections = 2nd" + (f" · Locations = {', '.join(p['locations'])}" if p.get("locations") else "")
          + (f" · Industry = {', '.join(p['industries'])}" if p.get("industries") else ""))
    print("   The free search runs out each month. Look at 10 to 20 people in a sitting, not a hundred.\n")
    print("3. PEOPLE WHO ARE TALKING ABOUT THE PROBLEM. Search Posts (not People) for the words your clients use, filter to Past week:")
    for kw in (p.get("problem_words") or p.get("keywords") or [])[:4]:
        print(f'   "{kw}"')
    print("   Someone who posted about the problem last week is worth ten who only match a title.\n")
    print("4. SALES NAVIGATOR (only if you already have it). Lead filters:")
    print(f"   Current job title = {', '.join(p['titles'])}" + (f" · Seniority = {', '.join(p['seniority'])}" if p.get("seniority") else "")
          + (f" · Geography = {', '.join(p['locations'])}" if p.get("locations") else "") + (f" · Industry = {', '.join(p['industries'])}" if p.get("industries") else "")
          + (f" · Company headcount = {p['company_size']}" if p.get("company_size") else ""))
    print("   Spotlights: Changed jobs in the last 90 days, Posted on LinkedIn in the last 30 days. Save the search so it alerts you.\n")
    print(f"For each person worth a message, open their profile yourself and note ONE real thing you noticed. Bring back at most {MAX_BATCH} at a time.")


def cmd_network(a):
    p = load(a.plan)
    probs = plan_problems(p)
    if probs:
        die("Fix the plan first: " + "; ".join(probs))
    try:
        raw = Path(a.csv).read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError as e:
        die(f"Cannot read {a.csv}: {e}")
    start = next((i for i, l in enumerate(raw) if l.lower().startswith("first name")), None)
    if start is None:
        die("That does not look like LinkedIn's Connections.csv (no 'First Name' header row).")
    want = [x.lower() for x in p["titles"]]
    near = [x.lower() for x in (p.get("keywords") or []) + (p.get("industries") or [])]
    skip = [x.lower() for x in p.get("exclude") or []]
    rows = []
    for r in csv.DictReader(raw[start:]):
        pos, co = (r.get("Position") or "").strip(), (r.get("Company") or "").strip()
        text = f"{pos} {co}".lower()
        if not pos or any(x in text for x in skip):
            continue
        title, topic = any(x in pos.lower() for x in want), any(x in text for x in near)
        if title or topic:
            rows.append((0 if title and topic else 1 if title else 2, f"{r.get('First Name', '').strip()} {r.get('Last Name', '').strip()}".strip(), pos, co, (r.get("URL") or "").strip(), (r.get("Connected On") or "").strip()))
    rows.sort()
    if not rows:
        print("Nobody in your connections matches the plan. That is common: go on to step 2 of the searches.")
        return
    print(f"{len(rows)} of your own connections match. The closest {min(len(rows), a.max)}:\n")
    for rank, name, pos, co, url, on in rows[:a.max]:
        print(f"- {name} · {pos} at {co} · connected {on or 'date unknown'} · {['title and topic', 'title', 'topic'][rank]}\n  {url}")
    print("\nThese people already accepted you. Open each profile yourself, note one real thing, and start there. Nothing is saved from this list.")


def distinctive(text):
    return {re.sub(r"(ings?|ed|es|s)$", "", w) for w in re.findall(r"[a-z]{5,}", str(text).lower()) if w not in COMMON}


def opener_problems(kind, text, hook, premium=False):
    out = []
    text, hook = str(text or "").strip(), str(hook or "").strip()
    limit = (NOTE_PREMIUM if premium else NOTE_FREE) if kind == "C2" else DM_MAX
    if kind not in ("C2", "DM"):
        return ["kind: C2 (a note on a connection request) or DM (the first message after they accept)"]
    if not text:
        return ["empty. With nothing real to say, send a blank request instead"]
    if not hook:
        out.append("no hook: an opener is written from one real thing the member noticed. With none, send a blank request (C1)")
    if len(text) > limit:
        out.append(f"{len(text)} characters; " + (f"a connection note holds {limit}" if kind == "C2" else f"keep a first message under {limit}"))
    if hook and not (distinctive(text) & distinctive(hook)):
        out.append("does not mention what the member noticed. Name it plainly, in a few words, so the person knows this was written to them")
    if PITCH.search(text):
        out.append(f"pitches ({PITCH.search(text).group(0)}). The first line is about them. What the member sells comes later, when they ask or the problem is clear")
    if LINK.search(text):
        out.append("carries a link. No link in a first line")
    if FLATTERY.search(text):
        out.append(f"opens like every other message ({FLATTERY.search(text).group(0)}). Say the specific thing, not a compliment")
    if PRESSURE.search(text):
        out.append(f"pressure ({PRESSURE.search(text).group(0)}). Take it out")
    extra = sorted(set(re.findall(r"\d[\d,.]*%?", text)) - set(re.findall(r"\d[\d,.]*%?", hook)))
    if extra:
        out.append(f"carries a number that is not in what the member noticed ({', '.join(extra)}). No invented detail")
    q = text.count("?")
    if kind == "DM" and q != 1:
        out.append(f"{q} questions. A first message asks exactly one, and it is easy to answer")
    if kind == "C2" and q > 1:
        out.append("more than one question in a connection note")
    me, you = len(re.findall(r"\b(i|i'm|i've|my|we|our)\b", text, re.I)), len(re.findall(r"\b(you|your|you're|you've)\b", text, re.I))
    if me > you + 1:
        out.append(f"more about the member than about them ({me} I/my/we to {you} you/your). Turn it round")
    return out


def cmd_opener(a):
    probs = opener_problems(a.kind, a.text, a.hook, a.premium)
    for x in probs:
        print("FIX  " + x)
    print(f"{len(a.text.strip())} characters. {len(probs)} to fix." + ("" if probs else " The member reads it, changes anything that is not how they talk, and sends it themselves."))
    sys.exit(1 if probs else 0)


def prospect_problems(d, premium=False):
    out = []
    ps = d.get("prospects") if isinstance(d, dict) else None
    if not isinstance(ps, list) or not ps:
        return ['the file must be {"prospects": [...]} with at least one person']
    if len(ps) > MAX_BATCH:
        out.append(f"{len(ps)} prospects. Work at most {MAX_BATCH} at a time: the best ones, looked at properly")
    seen = set()
    for i, p in enumerate(ps, 1):
        tag = f"{p.get('name') or 'prospect ' + str(i)}"
        if not isinstance(p, dict):
            out.append(f"prospect {i}: not an object")
            continue
        for k in ("name", "role", "company"):
            if not str(p.get(k, "")).strip():
                out.append(f"{tag}: {k} is missing (as the person shows it on their profile)")
        url = str(p.get("url", "")).strip().lower()
        if not re.match(r"https?://([a-z]+\.)?linkedin\.com/in/[^/?#\s]+", url):
            out.append(f"{tag}: needs their public profile link (linkedin.com/in/...)")
        elif url.rstrip("/") in seen:
            out.append(f"{tag}: listed twice")
        seen.add(url.rstrip("/"))
        if p.get("fit") not in ("A", "B", "C"):
            out.append(f"{tag}: fit is A, B or C")
        why = [str(w) for w in p.get("why") or [] if str(w).strip()]
        facts = (str(p.get("role", "")) + " " + str(p.get("company", "")) + " " + str((p.get("hook") or {}).get("note", ""))).lower()
        if not why:
            out.append(f"{tag}: say why they fit the ideal client, from what the profile shows")
        elif not any(distinctive(w) & distinctive(facts) for w in why):
            out.append(f"{tag}: the reason to fit does not rest on their role, company or what you noticed. A fit is something you can see, not a feeling")
        h = p.get("hook") if isinstance(p.get("hook"), dict) else {}
        kind, note = h.get("kind"), str(h.get("note", "")).strip()
        if kind not in HOOKS:
            out.append(f"{tag}: hook kind is one of {', '.join(HOOKS)}")
        elif kind != "none":
            if not note:
                out.append(f"{tag}: the hook needs one line on what the member noticed")
            elif len(note) > HOOK_MAX:
                out.append(f"{tag}: the hook is {len(note)} characters. One line in the member's own words, not copied profile text")
            if kind in ("post", "comment", "launch") and not re.match(r"https?://\S+", str(h.get("link", ""))):
                out.append(f"{tag}: a {kind} hook needs the link to it, so the member can check it before writing")
        op = p.get("opener")
        if kind == "none":
            if op:
                out.append(f"{tag}: nothing was noticed, so there is nothing to personalise. Send a blank request and write no opener")
        elif op is not None:
            if not isinstance(op, dict):
                out.append(f"{tag}: opener must be {{\"kind\": \"C2\" or \"DM\", \"text\": \"...\"}}")
            else:
                if op.get("kind") == "DM" and not p.get("connected"):
                    out.append(f"{tag}: a first message can only go to someone already connected. Use a connection note (C2) or a blank request")
                out += [f"{tag}: opener {x}" for x in opener_problems(op.get("kind"), op.get("text"), note, premium)]
    return out


def cmd_check(a):
    d = load(a.file)
    probs = prospect_problems(d, a.premium)
    for x in probs:
        print("FIX  " + x)
    ps = d.get("prospects") if isinstance(d, dict) and isinstance(d.get("prospects"), list) else []
    notes = sum(1 for p in ps if isinstance(p, dict) and isinstance(p.get("opener"), dict) and p["opener"].get("kind") == "C2")
    if notes > 3 and not a.premium:
        print(f"LOOK  {notes} connection notes. A free account gets only a few personalised notes a month: keep them for the best three and send the rest blank")
    fits = {f: sum(1 for p in ps if isinstance(p, dict) and p.get("fit") == f) for f in "ABC"}
    print(f"{len(ps)} prospects (A {fits['A']}, B {fits['B']}, C {fits['C']}). {len(probs)} to fix.")
    sys.exit(1 if probs else 0)


# What each message in a conversation is for. One question at a time; the member never pitches until invited to.
PATH = {
    "open": ("Start a conversation about them. Nothing about the member.",
             ["Name the one thing you noticed, then ask one easy question about it.",
              "\"You mentioned [what they posted]. Is that something you are in the middle of, or more a thought for later?\"",
              "\"Saw you [new role / launch]. What is taking most of your attention in the first few months?\""]),
    "situation": ("Understand how things are for them today. Facts, not feelings yet.",
                  ["Ask how they handle the thing now, who does it, how long it has been that way.",
                   "\"How are you handling [the thing] at the moment?\"",
                   "\"Who looks after that today, you or someone on the team?\""]),
    "problem": ("Find out what is not working, in their words. Do not name the problem for them.",
                ["Ask what they would change, or what is harder than it should be. Then ask them to say more.",
                 "\"What would you change about how that works now, if you could?\"",
                 "\"When you say [their word], what does that look like on a normal week?\""]),
    "cost": ("Let them say what it costs to leave it as it is. Never tell them the cost yourself.",
             ["Ask what happens if nothing changes, or what it has already meant for them.",
              "\"What happens if that stays the way it is for another six months?\"",
              "\"Has that had a knock-on effect anywhere else?\""]),
    "want": ("Hear what they want instead, and why now.",
             ["Ask what better would look like, and what has stopped them getting there.",
              "\"What would you want it to look like instead?\"",
              "\"What has got in the way of sorting it out before now?\""]),
    "invite": ("Ask whether a short call would be useful. Their problem in their words, an easy way to say no.",
               ["Only after two or more real exchanges, and only once they have described a problem themselves.",
                "\"It sounds like [their problem, in their words]. That is the kind of thing I work on. Would a short call to map your options be useful? If not, no problem at all.\"",
                "The booking link goes in the NEXT message, after they say yes."]),
}


def cmd_next(a):
    aim, lines = PATH[a.stage]
    i = STAGES.index(a.stage)
    print(f"STAGE  {a.stage} ({i + 1} of {len(STAGES)})")
    print(f"AIM    {aim}")
    print(f"HOW    {lines[0]}")
    for l in lines[1:]:
        print(f"LIKE   {l}")
    print("RULES  One question. Under 400 characters. Use their words back to them. No pitch, no link, no price.")
    print("       These are shapes, not scripts: write it the way the member talks, about what this person actually said.")
    if a.stage == "invite" and a.exchanges < 2:
        print(f"WAIT   Only {a.exchanges} real exchange(s) so far. An invitation this early reads as a pitch. Ask one more question first.")
    if a.stage != "invite":
        print(f"THEN   When they answer, move to: {STAGES[i + 1]}. Skip a stage only if they have already answered it unasked.")
    print("STOP   If they have not replied: one follow-up that adds something, then one that lets them off the hook, then stop.")
    print("       If they say no or ask not to be contacted, that is the end. Log it (li_pipeline.py forget) and never message them again.")


def say_problems(stage, text, exchanges=0, they_asked=False):
    out = []
    text = str(text or "").strip()
    if not text:
        return ["empty"]
    if len(text) > DM_MAX:
        out.append(f"{len(text)} characters; keep a message under {DM_MAX}. Long messages get skimmed")
    q = text.count("?")
    if q != 1:
        out.append(f"{q} questions. One question, so they know exactly what to answer")
    if PRESSURE.search(text):
        out.append(f"pressure ({PRESSURE.search(text).group(0)}). Take it out")
    if FLATTERY.search(text):
        out.append(f"filler ({FLATTERY.search(text).group(0)}). Say something specific instead")
    if re.search(r"\$\s?\d|\d\s?%|\b\d+x\b", text):
        out.append("carries a price or a figure. Numbers belong on the call, and only real ones")
    if stage != "invite":
        if PITCH.search(text) and not they_asked:
            out.append(f"pitches ({PITCH.search(text).group(0)}) before they have asked. Stay on their situation; the member's work comes up when they ask or at the invitation")
        if LINK.search(text) and not they_asked:
            out.append("carries a link before they asked for one")
        if re.search(r"\b(you (need|should|must|have to)|the problem is|your problem|what you need)\b", text, re.I):
            out.append("tells them what their problem is. Ask, and let them say it")
    else:
        if exchanges < 2:
            out.append(f"an invitation after {exchanges} real exchange(s). Wait for two, and for them to have described a problem themselves")
        if not EASY_NO.search(text):
            out.append("no easy way to say no. Add one (\"If not, no problem at all\")")
        if LINK.search(text):
            out.append("the booking link goes in the next message, after they say yes")
    return out


def cmd_say(a):
    probs = say_problems(a.stage, a.text, a.exchanges, a.they_asked)
    for x in probs:
        print("FIX  " + x)
    print(f"{len(a.text.strip())} characters. {len(probs)} to fix." + ("" if probs else " The member edits it into their own voice and sends it themselves."))
    sys.exit(1 if probs else 0)


def cmd_handoff(a):
    d = load(a.file)
    probs = prospect_problems(d, a.premium)
    if probs:
        die(f"{len(probs)} thing(s) to fix first. Run: li_prospect.py check")
    q = lambda v: '"' + str(v).replace('"', "'") + '"'  # noqa: E731
    print("Log each person you decide to approach, then follow li_pipeline.py today. Nothing is sent by either tool.\n")
    for p in d["prospects"]:
        h = p["hook"]
        line = (f"li_pipeline.py add --name {q(p['name'])} --url {p['url']} --role {q(p['role'])} --company {q(p['company'])} "
                f"--signal {SIGNAL[h['kind']]} --fit {p['fit']}" + (" --connected" if p.get("connected") else "")
                + (f" --link {h['link']}" if h.get("link") else "") + (f" --note {q(h['note'])}" if h.get("note") else ""))
        print(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("searches"); p.add_argument("plan"); p.set_defaults(fn=cmd_searches)
    p = sub.add_parser("network"); p.add_argument("plan"); p.add_argument("csv"); p.add_argument("--max", type=int, default=40); p.set_defaults(fn=cmd_network)
    p = sub.add_parser("check"); p.add_argument("file"); p.add_argument("--premium", action="store_true"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("opener"); p.add_argument("--kind", required=True); p.add_argument("--hook", default=""); p.add_argument("--text", required=True)
    p.add_argument("--premium", action="store_true"); p.set_defaults(fn=cmd_opener)
    p = sub.add_parser("next"); p.add_argument("--stage", required=True, choices=STAGES); p.add_argument("--exchanges", type=int, default=0); p.set_defaults(fn=cmd_next)
    p = sub.add_parser("say"); p.add_argument("--stage", required=True, choices=STAGES); p.add_argument("--text", required=True)
    p.add_argument("--exchanges", type=int, default=0); p.add_argument("--they-asked", action="store_true"); p.set_defaults(fn=cmd_say)
    p = sub.add_parser("handoff"); p.add_argument("file"); p.add_argument("--premium", action="store_true"); p.set_defaults(fn=cmd_handoff)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
