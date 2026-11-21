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
  li_prospect.py comment --post "what their post says, in the member's words" --text "the comment"
                                                    check a comment written before a connection request
  li_prospect.py reply --text "what they wrote back"   what kind of reply it is, and the honest way to answer it
  li_prospect.py brief CONVERSATION.json            a one-page brief for a booked call, in the person's own words

CONVERSATION.json: what was actually sent and received, typed or pasted by the member.
  {"name": "Dana Ruiz", "role": "Owner", "company": "Ruiz Dental", "url": "...", "hook": "what the member noticed",
   "messages": [{"from": "me", "stage": "open", "text": "..."}, {"from": "them", "text": "..."}], "call": "2026-12-02 10:00"}

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
STAGES = ("open", "situation", "problem", "cost", "want", "invite", "booked")
GENERIC_TITLES = {"owner", "founder", "ceo", "partner", "director", "manager", "president", "principal", "consultant"}
HOOKS = ("post", "comment", "new-role", "launch", "about", "shared", "none")
SIGNAL = {"post": "sig:posted-problem", "comment": "sig:commented-peer-post", "new-role": "sig:new-role", "launch": "sig:launch",
          "about": "sig:fit", "shared": "sig:fit", "none": "sig:fit"}
PITCH = re.compile(r"\b(i help|we help|i work with|i do \w+ for|we do \w+ for|my (program|offer|services?|course|company|firm)|our (program|services?|team)|book (a|some) (call|time)|"
                   r"schedule a (call|time|chat)|my calendar|free (call|consult\w*|audit|session|review|trial)|demo|discount|pric(e|ing)|sign up|limited (spots?|time|offer)|"
                   r"spots? (left|available)|proposal|clients? like you|worth a (quick )?(chat|call)|open to a (quick )?(chat|call)|quick (chat|call)|hop on|jump on|pick your brain)\b", re.I)
# A promise of what the member will do for them. Never in a message, with or without a number.
PROMISE = re.compile(r"\b(i|we) (can|could|will|'ll) (cut|save|reduce|lower|bring|get|grow|increase|boost|fix|double|improve|sort)\b|\bwe get\b|\b(save|saving|saved) (you|thousands|hundreds|money)\b|"
                     r"\b(cut|reduce|lower|fix) your\b|\b\d+\s?(percent|per cent)\b|\b(ten|fifteen|twenty|thirty|forty|fifty) (percent|per cent)\b|\bright down\b", re.I)
# A problem assumed about them. An opener may only say this if they said it themselves.
ASSUMES = re.compile(r"\b(struggling|messy|a mess|too high|too low|failing|falling behind|out of (her|his|their|your) depth|overwhelmed|drowning|in trouble|a headache|nightmare)\b", re.I)
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
    for w in p.get("problem_words") or []:
        if len(str(w).split()) > 4:
            out.append(f"problem_words: “{w}” is too long to search for. Two to four words a client would type")
    for k in ("titles", "keywords", "exclude", "locations", "industries", "seniority", "partners", "problem_words"):
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
        print(f'   "{kw}"' if len(str(kw).split()) <= 3 else f"   {kw}")
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
    partners = [x.lower() for x in p.get("partners") or []]
    rows, refer = [], []
    for r in csv.DictReader(raw[start:]):
        pos, co = (r.get("Position") or "").strip(), (r.get("Company") or "").strip()
        text = f"{pos} {co}".lower()
        if not pos or any(x in text for x in skip):
            continue
        title, topic = any(x in pos.lower() for x in want), any(x in text for x in near)
        if title and not topic and all(x in GENERIC_TITLES for x in want if x in pos.lower()):
            title = False    # "Owner" alone matches every plumber and florist
        if partners and any(x in text for x in partners):
            refer.append((f"{r.get('First Name', '').strip()} {r.get('Last Name', '').strip()}".strip(), pos, co, (r.get("URL") or "").strip()))
            continue
        if title or topic:
            rows.append((0 if title and topic else 1 if title else 2, f"{r.get('First Name', '').strip()} {r.get('Last Name', '').strip()}".strip(), pos, co, (r.get("URL") or "").strip(), (r.get("Connected On") or "").strip()))
    rows.sort()
    if refer:
        print(f"{len(refer)} of your connections already serve the same clients and could refer you. One of them can be worth many strangers:\n")
        for name, pos, co, url in refer[:a.max]:
            print(f"- {name} · {pos} at {co}\n  {url}")
        print()
    if not rows:
        print("Nobody in your connections matches the ideal client. That is common: go on to step 2 of the searches.")
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
    if PROMISE.search(text):
        out.append(f"promises a result ({PROMISE.search(text).group(0)}). No message says what the member will do for them, with or without a number")
    for m in ASSUMES.finditer(text):
        if m.group(0).lower() not in hook.lower():
            out.append(f"assumes a problem they did not state ({m.group(0)}). Ask; do not tell them what is wrong")
            break
    nums = lambda t: {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?%?", t)}  # noqa: E731
    extra = sorted(nums(text) - nums(hook))
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
    probs = opener_problems(a.kind, a.text, a.hook, a.premium) + never_problems(a.text, never_lines(a.business_file))
    for x in probs:
        print("FIX  " + x)
    print(f"{len(a.text.strip())} characters. {len(probs)} to fix." + ("" if probs else " The member reads it, changes anything that is not how they talk, and sends it themselves."))
    sys.exit(1 if probs else 0)


def suppressed(pipeline):
    """Hashes of people who asked not to be contacted, from the pipeline file. Empty when there is no file."""
    if not pipeline:
        return None, set()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("li_pipeline", Path(__file__).resolve().parent / "li_pipeline.py")
        pm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pm)
        return pm, {x["hash"] for x in json.loads(Path(pipeline).read_text(encoding="utf-8")).get("suppressed", [])}
    except (OSError, ValueError, KeyError) as e:
        die(f"Cannot read the pipeline file: {e}")


def never_lines(business_file):
    """What the member refuses to claim and the lines they retired, from §1 of their Business File."""
    if not business_file:
        return []
    try:
        text = Path(business_file).read_text(encoding="utf-8")
    except OSError as e:
        die(f"Cannot read the Business File: {e}")
    out = []
    for label in ("Never claim or promise", "Retired lines"):
        m = re.search(r"^- \*\*" + label + r"(?::\*\*|\*\*(?:\s*\([^)]*\))?:?)[ \t]*(.*)$", text, re.M)
        if m and m.group(1).strip() not in ("", "—", "-"):
            out += [x.strip(" .\"“”") for x in re.split(r";", re.sub(r"\([^)]*\)", " ", m.group(1))) if len(x.strip(" .\"“”")) >= 4]
    return out


def never_problems(text, lines):
    out = []
    got = distinctive(text) | {w for w in re.findall(r"[a-z]{3,4}", str(text).lower()) if w in ("tax", "roi", "cure", "debt", "rank", "sale", "cash")}
    for line in lines:
        keys = distinctive(line) | {w for w in re.findall(r"[a-z]{3,4}", line.lower()) if w in ("tax", "roi", "cure", "debt", "rank", "sale", "cash")}
        if keys and len(keys & got) >= (1 if len(keys) <= 2 else 2):
            out.append(f"comes close to something the member refuses to say (“{line}”). Take it out")
    return out


def prospect_problems(d, premium=False, pipeline=None, business_file=None):
    out = []
    pm, barred = suppressed(pipeline)
    never = never_lines(business_file)
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
        elif pm and (pm.url_hashes(url) & barred):
            out.append(f"{tag}: asked not to be contacted. Take them out of the file; they are never approached again")
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
                if op.get("kind") == "DM" and not p.get("connected") and not op.get("after_accept"):
                    out.append(f"{tag}: a first message can only go to someone already connected. Send a blank request now and mark the opener \"after_accept\": true, or use a connection note (C2)")
                out += [f"{tag}: opener {x}" for x in opener_problems(op.get("kind"), op.get("text"), note, premium) + never_problems(op.get("text"), never)]
    return out


def cmd_check(a):
    d = load(a.file)
    probs = prospect_problems(d, a.premium, a.pipeline, a.business_file)
    for x in probs:
        print("FIX  " + x)
    ps = d.get("prospects") if isinstance(d, dict) and isinstance(d.get("prospects"), list) else []
    notes = sum(1 for p in ps if isinstance(p, dict) and isinstance(p.get("opener"), dict) and p["opener"].get("kind") == "C2")
    if notes > 3 and not a.premium:
        print(f"LOOK  {notes} connection notes. A free account gets only a few personalised notes a month: keep them for the best three and send the rest blank")
    fits = {f: sum(1 for p in ps if isinstance(p, dict) and p.get("fit") == f) for f in "ABC"}
    print(f"{len(ps)} prospects (A {fits['A']}, B {fits['B']}, C {fits['C']}). {len(probs)} to fix."
          + ("" if probs else " The check reads for pitches, promises and invented details. It cannot judge tone or truth: the member reads every line before sending."))
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
    "booked": ("They said yes. Make the next step easy, answer anything they asked, and stop.",
               ["Give the booking link, or two times if there is no link. If they asked the price, say it straight in one sentence, with the member's real figure.",
                "\"Glad it would help. Here is my calendar: [link]. To answer your question, it is [the real price].\"",
                "\"Glad it would help. I have no booking page, so would Tuesday at 10 or Thursday at 2 suit you?\""]),
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
    print("RULES  One question. Under 400 characters. Use their words back to them." + (" The link and the price are allowed now; a promise of results never is." if a.stage == "booked" else " No pitch, no link, no price."))
    print("       These are shapes, not scripts: write it the way the member talks, about what this person actually said.")
    if a.stage == "invite" and a.exchanges < 2:
        print(f"WAIT   Only {a.exchanges} real exchange(s) so far. An invitation this early reads as a pitch. Ask one more question first.")
    if a.stage == "booked":
        print("THEN   Log the call (li_pipeline.py move <id> call-booked), then: li_prospect.py brief, and the Sales Conversations session.")
    elif a.stage == "invite":
        print("THEN   When they say yes, move to: booked.")
    else:
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
    if stage == "booked":
        if q > 1:
            out.append(f"{q} questions. One at most: they have said yes, so make the next step easy")
        if PROMISE.search(text):
            out.append(f"promises a result ({PROMISE.search(text).group(0)}). Take it out")
        if len(text) > DM_MAX:
            out.append(f"{len(text)} characters; keep it under {DM_MAX}")
        return out
    if q != 1:
        out.append(f"{q} questions. One question, so they know exactly what to answer")
    if PRESSURE.search(text):
        out.append(f"pressure ({PRESSURE.search(text).group(0)}). Take it out")
    if PROMISE.search(text):
        out.append(f"promises a result ({PROMISE.search(text).group(0)}). Say what the member does, never what they will get")
    if FLATTERY.search(text):
        out.append(f"filler ({FLATTERY.search(text).group(0)}). Say something specific instead")
    if re.search(r"\$\s?\d|\d\s?%|\b\d+x\b", text) and not they_asked:
        out.append("carries a price or a figure. Give a price only when they ask for it (then add --they-asked), and only the member's real one")
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
            out.append("the booking link goes in the next message, after they say yes (stage: booked)")
    return out


def cmd_say(a):
    probs = say_problems(a.stage, a.text, a.exchanges, a.they_asked) + never_problems(a.text, never_lines(a.business_file))
    for x in probs:
        print("FIX  " + x)
    print(f"{len(a.text.strip())} characters. {len(probs)} to fix." + ("" if probs else " The member edits it into their own voice and sends it themselves."))
    sys.exit(1 if probs else 0)


def comment_problems(post, text):
    out = []
    text, post = str(text or "").strip(), str(post or "").strip()
    if not text:
        return ["empty"]
    if not post:
        out.append("no post: a comment is written about what the post says. Have the member say what it was about")
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    if not 2 <= len(sentences) <= 4:
        out.append(f"{len(sentences)} sentence(s). Two to four: one specific idea, not a reaction and not an essay")
    if len(text) > 600:
        out.append(f"{len(text)} characters; keep a comment under 600")
    if post and not (distinctive(text) & distinctive(post)):
        out.append("does not pick up anything the post says. Name the specific point you are adding to")
    if re.match(r"\s*(great|nice|love|awesome|amazing|so true|well said|100%|this!|agreed?\b[.!]?$)", text, re.I) or FLATTERY.search(text):
        out.append("opens with praise. Start with the idea")
    if PITCH.search(text) or re.search(r"\b(dm me|message me|reach out|check out my|link in)\b", text, re.I):
        out.append("pitches or asks them to get in touch. A comment adds to their post and stops there")
    if LINK.search(text):
        out.append("carries a link")
    if re.search(r"\b(my|our) clients?\b|\bwe (saw|got|achieved)\b|\d\s?%|\$\s?\d", text, re.I):
        out.append("claims a client result or a figure. Not in a public comment, unless it is proof the member has permission to use")
    if text.count("?") > 1:
        out.append("more than one question")
    return out


def cmd_comment(a):
    probs = comment_problems(a.post, a.text)
    for x in probs:
        print("FIX  " + x)
    print(f"{len(a.text.strip())} characters. {len(probs)} to fix." + ("" if probs else " The member edits it and posts it themselves. Send the connection request a day or two later."))
    sys.exit(1 if probs else 0)


# What people actually write back, and the honest way to answer each. First match wins, so the firm ones come first.
REPLIES = [
    ("stop", r"\b(not interested|no thanks|no thank you|stop (messag|contact)|don'?t (message|contact|email)|do not (message|contact)|remove me|unsubscribe|leave me alone|please stop)\b",
     "They said no.", "Do not answer, or at most one line: \"Understood, I will not message again.\" Then li_pipeline.py forget <id>.",
     "Never ask why, never try once more, never add them back.", None),
    ("price", r"\b(how much|what do you charge|what('?s| is) (the|your) (price|cost|fee|rate)|pricing|your rates?|what does it cost)\b",
     "They asked the price. That is interest, and a fair question.",
     "Answer it straight, in one sentence, with the member's real price or range from their Business File. Then one question back, or the call if it has been earned.",
     "Never dodge it (\"it depends, let's hop on a call\"), and never quote a number the member has not confirmed.", "invite"),
    ("what_do_you_do", r"\b(what (do|is it) you do|what('?s| is) (this|that) about|what are you (selling|offering)|are you selling|is this a (sales|pitch)|why (are you|did you) (messag|reach|ask))\b",
     "They want to know who they are talking to.",
     "One honest sentence on what the member does and for whom, in the member's own words. Then say why you asked, and go back to their situation with one question.",
     "Never deny that you sell something. Never answer with a paragraph.", None),
    ("send_info", r"\b(send (me|over|across) (some |more |the )?(info|information|details|something|a link|your (site|website))|do you have (a|any) (website|brochure|link|info)|where can i (read|learn|see) more)\b",
     "Often a polite way to end it, sometimes real.",
     "Offer one specific thing and ask what would make it useful: \"Happy to. So I send the right thing, is it [their situation, in their words] you are trying to sort out?\"",
     "Never send a brochure and wait. Never send three links.", None),
    ("have_someone", r"\b(already have|we have (a|an|someone)|got (a|an|someone)|we use|working with (a|an|someone)|in[- ]house|my (accountant|bookkeeper|agency|guy|team) (does|handles))\b",
     "They have someone. That is information, not a wall.",
     "Respect it, and ask one genuine question about how it is going: \"Glad you are covered. How is that working for [the specific thing they mentioned]?\" If the answer is \"fine\", wish them well and move them to nurture.",
     "Never run down who they use.", "situation"),
    ("not_now", r"\b(not (right )?now|not at the moment|maybe later|next (year|quarter|month)|too busy|bad time|in a few months|circle back|down the (road|line))\b",
     "Timing, not a no.",
     "Take it at face value and ask when: \"No problem. Would it be useful if I checked back in [the month they named], or shall I leave it with you?\" Log the date and do not message before it.",
     "Never push for the call now.", None),
    ("who_are_you", r"\b(do i know you|have we met|who (are|is) (you|this)|how did you find me|where did you get)\b",
     "They are checking you are real.",
     "Say plainly how you came across them (the post, the search, the shared connection) and who you are, in two sentences. Then one easy question, or none.",
     "Never be vague about how you found them.", "open"),
    ("referred_on", r"\b(talk to|speak (to|with)|reach out to|contact|ask) (my|our) (\w+ ){0,2}(manager|partner|assistant|director|team|wife|husband|colleague)\b",
     "They pointed you to someone else.",
     "Thank them, ask one thing that will help that conversation, and ask if you may use their name. The new person is added by the member, by hand, as a referral.",
     "Never message the other person as if invited unless they said you could.", None),
]


def cmd_reply(a):
    text = str(a.text or "").strip()
    if not text:
        die("Give what they wrote (--text).")
    for kind, pattern, means, do, never, stage in REPLIES:
        if re.search(pattern, text, re.I):
            print(f"KIND   {kind}")
            print(f"MEANS  {means}")
            print(f"DO     {do}")
            print(f"NEVER  {never}")
            if stage:
                print(f"THEN   Carry on from stage: {stage}  (li_prospect.py next --stage {stage})")
            print("LOG    li_pipeline.py reply <id>" if kind != "stop" else "LOG    li_pipeline.py forget <id>")
            return
    q = "?" in text
    print("KIND   an answer" + (" with a question of their own" if q else ""))
    print("MEANS  They are in the conversation. Read what they actually said before anything else.")
    print("DO     " + ("Answer their question first, in one or two honest sentences. Then your one question." if q else "Pick up their own words and ask the next question. If the answer was thin, ask them to say more before moving on."))
    print("NEVER  Skip past what they said to get to your point.")
    print("LOG    li_pipeline.py reply <id>, then li_prospect.py next --stage <the stage you are at>")


def cmd_brief(a):
    c = load(a.file)
    msgs = c.get("messages") if isinstance(c, dict) else None
    if not isinstance(msgs, list) or not any(isinstance(m, dict) and m.get("from") == "them" and str(m.get("text", "")).strip() for m in msgs):
        die("Nothing they said is in the file yet. A brief is built from their own replies.")
    said, stage, asked = {s: [] for s in STAGES}, "open", []
    for m in msgs:
        if not isinstance(m, dict):
            continue
        t = str(m.get("text", "")).strip()
        if m.get("from") == "me":
            stage = m.get("stage") if m.get("stage") in STAGES else stage
        elif m.get("from") == "them" and t:
            said[stage].append(t)
            asked += [q.strip() for q in re.findall(r"[^.!?]*\?", t) if q.strip()]
    head = {"open": "How it started", "situation": "Their situation today", "problem": "What is not working", "cost": "What it is costing them", "want": "What they want instead", "invite": "What they said about a call"}
    out = [f"# Before your call with {c.get('name', 'them')}", "",
           " · ".join(x for x in (str(c.get("role", "")), str(c.get("company", "")), ("call: " + str(c["call"])) if c.get("call") else "") if x), ""]
    if c.get("hook"):
        out += [f"**What you first noticed:** {c['hook']}", ""]
    out += ["Everything in quotation marks is what they wrote to you, word for word. Private: it is for this call, not for a post or a page.", ""]
    for s in STAGES:
        if said[s]:
            out += [f"## {head[s]}", ""] + [f"> “{t}”" for t in said[s]] + [""]
    if asked:
        out += ["## What they asked you", "", "Have a straight answer ready for each.", ""] + [f"- {q}" for q in dict.fromkeys(asked)] + [""]
    missing = [head[s] for s in ("situation", "problem", "cost", "want") if not said[s]]
    if missing:
        out += ["## Not covered yet", "", "They have not told you these. Ask on the call; do not assume.", ""] + [f"- {m}" for m in missing] + [""]
    out += ["## On the call", "", "- Start from their words above, not from your offer.", "- Ask what has changed since you last wrote.",
            "- Nothing here is a promise of what you can do for them. Say only what is true.", ""]
    print("\n".join(out))


def cmd_handoff(a):
    d = load(a.file)
    probs = prospect_problems(d, a.premium, a.pipeline)
    if probs:
        die(f"{len(probs)} thing(s) to fix first. Run: li_prospect.py check")
    q = lambda v: '"' + str(v).replace('"', "'") + '"'  # noqa: E731
    print("Log each person you decide to approach, then follow li_pipeline.py today. Nothing is sent by either tool.")
    print("If there is no pipeline file yet, create it first: li_pipeline.py settings --premium yes|no\n")
    left = [p["name"] for p in d["prospects"] if p.get("fit") == "C"]
    if left:
        print("Left out, a poor fit (C): " + ", ".join(left) + "\n")
    for p in d["prospects"]:
        if p.get("fit") == "C":
            continue
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
    p = sub.add_parser("check"); p.add_argument("file"); p.add_argument("--premium", action="store_true"); p.add_argument("--pipeline"); p.add_argument("--business-file"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("opener"); p.add_argument("--kind", required=True); p.add_argument("--hook", default=""); p.add_argument("--text", required=True)
    p.add_argument("--premium", action="store_true"); p.add_argument("--business-file"); p.set_defaults(fn=cmd_opener)
    p = sub.add_parser("next"); p.add_argument("--stage", required=True, choices=STAGES); p.add_argument("--exchanges", type=int, default=0); p.set_defaults(fn=cmd_next)
    p = sub.add_parser("say"); p.add_argument("--stage", required=True, choices=STAGES); p.add_argument("--text", required=True)
    p.add_argument("--exchanges", type=int, default=0); p.add_argument("--they-asked", action="store_true"); p.add_argument("--business-file"); p.set_defaults(fn=cmd_say)
    p = sub.add_parser("handoff"); p.add_argument("file"); p.add_argument("--premium", action="store_true"); p.add_argument("--pipeline"); p.set_defaults(fn=cmd_handoff)
    p = sub.add_parser("comment"); p.add_argument("--post", default=""); p.add_argument("--text", required=True); p.set_defaults(fn=cmd_comment)
    p = sub.add_parser("reply"); p.add_argument("--text", required=True); p.set_defaults(fn=cmd_reply)
    p = sub.add_parser("brief"); p.add_argument("file"); p.set_defaults(fn=cmd_brief)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
