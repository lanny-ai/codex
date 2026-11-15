#!/usr/bin/env python3
"""Speaking Engine: the member's speaking profile, their talks, and the pipeline of stages.

Everything lives in speaking/ beside the Business File. A "stage" is one real place the member could
speak: a group, an event, a podcast, a summit. No stage is ever added without where it was found and
the date it was seen there, and none is pitched until it has been vetted for the bad deals aimed at
new speakers.

Usage (run from the folder that holds the Business File; --folder defaults to ./speaking)
  speak_pipeline.py init
  speak_pipeline.py prefill [--business-file F]          what the Business File already answers, and what to ask
  speak_pipeline.py intake                               which of the 17 questions are answered
  speak_pipeline.py confirm --all | --keys a,b --by member          the member confirms what was drafted from the file
  speak_pipeline.py answer --key audience --text-file a.txt [--from "§2"] [--draft] [--append]
                        (use a file or single quotes: inside double quotes the shell eats dollar amounts)
  speak_pipeline.py ready                                the profile is enough to look for stages (core answers in)
  speak_pipeline.py talk add --title "…" --promise "…" --takeaway "…" --takeaway "…" --takeaway "…"
                             --for "who it is for" [--length 20,45] [--format talk]
  speak_pipeline.py talk list
  speak_pipeline.py add --name "…" --host "…" --kind local|association|conference|corporate|podcast|summit|webinar|other
                        --source "https://… or: member knows it" --seen 2026-11-14 --audience "who is in the room"
                        [--size 60] [--when 2027-03-12 | --recurring "second Tuesday"] [--deadline 2027-01-15]
                        [--contact-role "program chair"] [--pays yes|no|unknown] [--selling allowed|not allowed|unknown]
                        [--note "…"]
  speak_pipeline.py vet --id ST-003 --audience 1-5 --decider 1-5 --timing 1-5 --offer 1-5
                        [--flag pay_to_speak …] [--checked "what was looked at"] [--accept-risk --by member --reason "…"]
  speak_pipeline.py flags                                the red flags and what each means
  speak_pipeline.py list [--status found] [--kind local]
  speak_pipeline.py rank                                 vetted stages, best fit first
  speak_pipeline.py pitch --id ST-003 --channel email|form|linkedin|phone|in person [--text-file pitch.txt] [--talk 1]
  speak_pipeline.py follow --id ST-003 [--text-file f.txt]        (two follow-ups at most, a week apart)
  speak_pipeline.py reply --id ST-003 --outcome yes|no|maybe|later [--note "…"] [--ask-again 2027-06-01]
  speak_pipeline.py book --id ST-003 --when 2027-03-12 [--fee 0] [--terms "…"] [--selling allowed|not allowed]
  speak_pipeline.py deliver --id ST-003 [--attended 40] [--leads 6] [--note "…"]
  speak_pipeline.py after --id ST-003 [--clients 1] [--thanked] [--testimonial-asked] [--referral-asked] [--note "…"]
  speak_pipeline.py debrief --id ST-003 --well "…" --improve "…" [--reaction "…"] [--confidence 1-10]
  speak_pipeline.py goal [--talks-per-month 2] [--clients-per-quarter 3] [--fee-income-year 0]
  speak_pipeline.py drop --id ST-003 --reason "…"
  speak_pipeline.py today                                what is due: follow-ups, deadlines, events coming, thank-yous
  speak_pipeline.py report                               the scorecard, with every rate shown as a count
  speak_pipeline.py plan [--weeks 12] [--start 2026-11-16]         a dated week-by-week plan
Every command takes --folder and --today YYYY-MM-DD (to log something after the fact). JSON on stdout;
exit 1 on a refusal.
"""
import argparse, re, sys
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import speaklib as sl  # noqa: E402

FOLLOW_GAP = 7          # days between touches
MAX_FOLLOWS = 2
MIN_SAMPLE = 10         # pitches before a reply rate means anything
WEIGHTS = {"audience": 3, "decider": 2, "timing": 1, "offer": 2}


# ---------------------------------------------------------------- profile
def cmd_init(a):
    f = sl.folder(a)
    existed = (f / "pipeline.json").exists()
    data = sl.load(a, create=True)
    for sub in ("pitches", "one-sheet", "notes"):
        (f / sub).mkdir(parents=True, exist_ok=True)
    sl.save(a, data)
    return {"ok": True, "folder": str(f), "created": not existed,
            "next": "speak_pipeline.py intake, then answer what the Business File does not already hold"}


def intake_rows(data):
    rows = []
    for key, q, helper in sl.QUESTIONS:
        v = data["profile"].get(key) or {}
        rows.append({"key": key, "question": q, "helper": helper, "answered": bool(str(v.get("text", "")).strip()),
                     "draft": bool(v.get("draft")),
                     "from": v.get("from", ""), "may_be_in_file": sl.FROM_FILE.get(key, "")})
    return rows


def cmd_prefill(a):
    """What the Business File already holds for the speaking profile and the kit. The session drafts from
    these sections, in the member's words, and shows the member one summary to confirm."""
    data = sl.load(a)
    bf = sl.find_business_file(a)
    if not bf:
        sl.refuse("no Business File found here; give --business-file, or run the intake by asking")
    secs = sl.file_sections(bf)
    answered = {r["key"] for r in intake_rows(data) if r["answered"]}

    def src(nums):
        return [{"section": f"§{n}", "title": secs[n]["title"], "status": secs[n]["status"] or "unknown",
                 "text": secs[n]["body"][:a.chars]} for n in nums if n in secs and secs[n]["filled"]]
    draft, ask = [], []
    for key, q, helper in sl.QUESTIONS:
        if key in answered:
            continue
        found = src(sl.DRAFT_FROM.get(key, ()))
        (draft if found else ask).append({"key": key, "question": q, **({"from": found} if found else {"helper": helper})})
    kit = {k: src(v) for k, v in sl.KIT_FROM.items()}
    prov = sorted({f"§{n}" for n in (1, 2, 3, 4, 17, 18) if n in secs and secs[n]["status"] in ("provisional", "in progress")})
    return {"ok": True, "business_file": bf, "draft_from_file": draft, "ask_the_member": ask,
            "kit_sources": kit, "provisional_sections": prov,
            "missing_sections": [f"§{n}" for n in (1, 2, 3, 4, 17, 18) if n not in secs or not secs[n]["filled"]],
            "how": ["write each draft answer in the member's own words from the text shown, then record it with "
                    "`answer --key … --text-file … --from \"§N\" --draft`",
                    "draft one to three talks, the bio and the one-sheet from kit_sources the same way",
                    "show the member ONE summary of every draft and ask what is wrong; fix it; then `confirm --all` "
                    "(or `confirm --keys a,b`)",
                    "ask only the questions under ask_the_member, one at a time"],
            "rule": "a draft uses only what the file says. Where the file is thin, ask; never fill a gap"}


def cmd_confirm(a):
    data = sl.load(a)
    if a.by != "member":
        sl.refuse("only the member confirms what was drafted from their file (--by member)")
    keys = sl.QUESTION_KEYS if a.all else [k.strip() for k in (a.keys or "").split(",") if k.strip()]
    bad = [k for k in keys if k not in sl.QUESTION_KEYS]
    if bad or not keys:
        sl.refuse("--keys is a comma list of question keys, or use --all" + (f"; unknown: {', '.join(bad)}" if bad else ""))
    done = []
    for k in keys:
        v = data["profile"].get(k)
        if isinstance(v, dict) and str(v.get("text", "")).strip() and v.get("draft"):
            v["draft"] = False
            v["confirmed"] = str(sl.day(a))
            done.append(k)
    sl.save(a, data)
    left = [k for k, v in data["profile"].items() if isinstance(v, dict) and v.get("draft")]
    return {"ok": True, "confirmed": done, "still_draft": left}


def cmd_intake(a):
    data = sl.load(a)
    rows = intake_rows(data)
    done = [r["key"] for r in rows if r["answered"]]
    return {"ok": True, "answered": len(done), "of": len(rows), "missing": [r for r in rows if not r["answered"]],
            "core_missing": [k for k in sl.CORE if k not in done],
            "note": "ask one question at a time; the member can say 'skip'; long spoken answers are the best ones"}


def cmd_answer(a):
    data = sl.load(a)
    if a.key not in sl.QUESTION_KEYS:
        sl.refuse(f"unknown key {a.key}; keys: {', '.join(sl.QUESTION_KEYS)}")
    text = sl.arg_text(a.text, a.text_file)
    if not text:
        sl.refuse("the answer is empty (--text '…' or --text-file path)")
    old = str((data["profile"].get(a.key) or {}).get("text", ""))
    if a.append and old:
        text = old + "\n\n" + text
    if a.draft and not getattr(a, "from"):
        sl.refuse("a draft says which section it was drafted from (--from \"§2\")")
    data["profile"][a.key] = {"text": text, "from": getattr(a, "from") or "member", "date": str(sl.day(a)),
                              "draft": bool(a.draft)}
    sl.save(a, data)
    md = ["# Speaking profile", ""]
    for key, q, _ in sl.QUESTIONS:
        md += [f"## {q}", "", str((data["profile"].get(key) or {}).get("text", "")) or "_not answered yet_", ""]
    sl.write_atomic(sl.folder(a) / "profile.md", "\n".join(md))
    warn = []
    if old and not a.append:
        warn.append("this replaced the earlier answer; use --append to add to it instead")
    if sl.eaten_dollars(text):
        warn.append("a figure here starts with a comma (" + ", ".join(sl.eaten_dollars(text)[:3]) + "): the shell probably "
                    "swallowed a dollar amount. Put the answer in a file and use --text-file")
    return {"ok": True, "key": a.key, "answered": sum(1 for r in intake_rows(data) if r["answered"]), "draft": bool(a.draft),
            "warnings": warn}


def cmd_ready(a):
    data = sl.load(a)
    done = [r["key"] for r in intake_rows(data) if r["answered"]]
    missing = [k for k in sl.CORE if k not in done]
    if missing:
        sl.refuse("not enough to look for stages yet; still needed: " + ", ".join(missing))
    drafts = [r["key"] for r in intake_rows(data) if r["draft"]]
    if drafts:
        sl.refuse("these answers were drafted from the Business File and the member has not confirmed them: "
                  + ", ".join(drafts) + ". Show the member the summary, fix what is wrong, then confirm --all --by member")
    if not any(k in done for k in ("regions", "mode", "reach")):
        sl.refuse("say where: answer regions, mode (virtual or in person) or reach, so the search has a place to look")
    data["profile_ready"] = str(sl.day(a))
    sl.save(a, data)
    return {"ok": True, "ready": True, "answered": len(done),
            "thin": [k for k in ("credentials", "hosts", "paid", "availability") if k not in done]}


def cmd_talk(a):
    data = sl.load(a)
    if a.action == "list":
        return {"ok": True, "talks": data["talks"]}
    if not (a.title and a.promise and getattr(a, "for")):
        sl.refuse("a talk needs --title, --promise (what the room leaves able to do) and --for (who it is for)")
    takes = [t.strip() for t in (a.takeaway or []) if t.strip()]
    if len(takes) != 3:
        sl.refuse(f"a talk has three takeaways a host can print; got {len(takes)}")
    for label, t in (("title", a.title), ("promise", a.promise)):
        if any(d in t for d in sl.DASHES):
            sl.refuse(f"no em or en dashes in the {label}")
    if sl.words(a.title) > 12:
        sl.refuse("the title is over twelve words; a host has to fit it on a flyer")
    try:
        lengths = [int(x) for x in str(a.length or "20,45").split(",") if x.strip()]
    except ValueError:
        sl.refuse("--length is minutes, comma separated: 20,45")
    n = len(data["talks"]) + 1
    data["talks"].append({"n": n, "title": a.title.strip(), "promise": a.promise.strip(), "takeaways": takes,
                          "for": getattr(a, "for").strip(), "lengths": lengths, "format": a.format or "talk",
                          "added": str(sl.day(a))})
    sl.save(a, data)
    return {"ok": True, "talk": n, "talks": len(data["talks"]),
            "warnings": ["three talks is plenty; hosts book the speaker with one clear topic"] if n > 3 else []}


# ---------------------------------------------------------------- stages
def cmd_add(a):
    data = sl.load(a)
    if not data.get("profile_ready"):
        sl.refuse("the speaking profile is not ready (speak_pipeline.py ready): stages are chosen to fit it")
    src = (a.source or "").strip()
    if not (re.match(r"https?://\S+\.\S+", src) or re.match(r"(?i)member (knows|has)", src)):
        sl.refuse("--source is the page the stage was found on (https://…), or 'member knows it: how'. "
                  "A stage with no source is not added: never list one from memory")
    seen = sl.parse_date(a.seen, "--seen")
    if seen > sl.day(a):
        sl.refuse("--seen is the day the source was looked at; it cannot be in the future")
    if not (a.name and a.host and a.audience):
        sl.refuse("a stage needs --name, --host (who runs it) and --audience (who is in the room)")
    if a.kind not in sl.KINDS:
        sl.refuse(f"--kind is one of {', '.join(sl.KINDS)}")
    key = re.sub(r"[^a-z0-9]+", " ", f"{a.name} {a.host}".lower()).strip()
    for s in data["stages"]:
        if s.get("key") == key and s["status"] not in ("dropped",):
            sl.refuse(f"{s['id']} is already this stage ({s['name']})")
    when = str(sl.parse_date(a.when, "--when")) if a.when else ""
    deadline = str(sl.parse_date(a.deadline, "--deadline")) if a.deadline else ""
    data["last_id"] = int(data.get("last_id", 0)) + 1
    sid = f"ST-{data['last_id']:03d}"
    data["stages"].append({
        "id": sid, "key": key, "name": a.name.strip(), "host": a.host.strip(), "kind": a.kind, "source": src,
        "seen": str(seen), "audience": a.audience.strip(), "size": a.size, "when": when,
        "recurring": (a.recurring or "").strip(), "deadline": deadline, "contact_role": (a.contact_role or "").strip(),
        "pays": a.pays or "unknown", "selling": a.selling or "unknown", "note": (a.note or "").strip(),
        "status": "found", "vet": None, "touches": [], "history": [{"status": "found", "date": str(sl.day(a))}]})
    sl.save(a, data)
    warn = []
    if (sl.day(a) - seen).days > 60:
        warn.append("the source was seen more than 60 days ago: look again before pitching; contacts and dates change")
    if deadline and sl.parse_date(deadline) < sl.day(a):
        warn.append("the deadline has passed: note the next cycle with --recurring, or ask the host when it opens")
    return {"ok": True, "id": sid, "status": "found", "warnings": warn,
            "privacy": "a contact's name and email stay in the member's own address book or CRM; only the role goes here",
            "next": f"speak_pipeline.py vet --id {sid} …"}


def move(a, data, s, status, **extra):
    s["status"] = status
    s["history"].append({"status": status, "date": str(sl.day(a)), **{k: v for k, v in extra.items() if v not in (None, "")}})
    sl.save(a, data)


def cmd_flags(a):
    return {"ok": True, "red_flags": sl.RED_FLAGS,
            "rule": "a stage with a red flag is not pitched unless the member, told plainly what the flag means, accepts it"}


def cmd_vet(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] not in ("found", "vetted"):
        sl.refuse(f"{s['id']} is already {s['status']}")
    scores = {}
    for k in WEIGHTS:
        v = getattr(a, k)
        if v is None or not 1 <= v <= 5:
            sl.refuse(f"--{k} is a whole number from 1 to 5 (audience fit, how clear the decision-maker is, "
                      "whether the timing works, how much room there is to offer something)")
        scores[k] = v
    flags = sorted(set(a.flag or []))
    bad = [f for f in flags if f not in sl.RED_FLAGS]
    if bad:
        sl.refuse(f"unknown flag(s) {', '.join(bad)}; speak_pipeline.py flags lists them")
    if not (a.checked or "").strip():
        sl.refuse("--checked says what was looked at (the host's site, past agendas, who attended, the terms): "
                  "a stage is not vetted from its own invitation alone")
    accepted = None
    if flags:
        if a.accept_risk:
            if a.by != "member" or not (a.reason or "").strip():
                sl.refuse("only the member accepts a red flag (--accept-risk --by member --reason \"…\")")
            accepted = {"by": "member", "reason": a.reason.strip(), "date": str(sl.day(a))}
    fit = round(sum(scores[k] * w for k, w in WEIGHTS.items()) / sum(WEIGHTS.values()), 2)
    s["vet"] = {"scores": scores, "fit": fit, "flags": flags, "checked": a.checked.strip(), "accepted": accepted,
                "date": str(sl.day(a))}
    ok = not flags or accepted is not None
    if ok:
        move(a, data, s, "vetted", fit=fit)
    else:
        sl.save(a, data)
    return {"ok": True, "id": s["id"], "fit": fit, "status": s["status"], "flags": {f: sl.RED_FLAGS[f] for f in flags},
            "pitchable": ok,
            "note": "" if ok else "red flags stand: tell the member what each means; most such offers are best dropped "
                                  f"(speak_pipeline.py drop --id {s['id']} --reason …)",
            "warnings": ["audience fit is 2 or less: a full room of the wrong people brings no clients"] if scores["audience"] <= 2 else []}


def public(s):
    keep = ("id", "name", "host", "kind", "audience", "size", "when", "recurring", "deadline", "pays", "selling",
            "status", "source", "seen")
    out = {k: s.get(k) for k in keep}
    out["fit"] = (s.get("vet") or {}).get("fit")
    out["flags"] = (s.get("vet") or {}).get("flags", [])
    out["touches"] = len(s.get("touches") or [])
    return out


def cmd_list(a):
    data = sl.load(a)
    rows = [s for s in data["stages"] if (not a.status or s["status"] == a.status) and (not a.kind or s["kind"] == a.kind)]
    return {"ok": True, "count": len(rows), "stages": [public(s) for s in rows]}


def cmd_rank(a):
    data = sl.load(a)
    rows = [s for s in data["stages"] if s["status"] == "vetted"]
    rows.sort(key=lambda s: (-(s["vet"] or {}).get("fit", 0), s.get("deadline") or "9999"))
    return {"ok": True, "count": len(rows), "stages": [public(s) for s in rows],
            "note": "fit is audience ×3, decision-maker ×2, room to offer ×2, timing ×1, out of 5. It ranks; it does not predict."}


def last_touch(s):
    return sl.parse_date(s["touches"][-1]["date"]) if s.get("touches") else None


def checked(a, s, kind):
    """A message that is filed has passed the check a host would put it through. Nothing with a FIX is filed."""
    import pitch_check
    from types import SimpleNamespace
    out, code = pitch_check.check(SimpleNamespace(file=a.text_file, kind=kind, stage=s["id"], folder=a.folder,
                                                  business_file=getattr(a, "business_file", None)))
    if code == 2:
        sl.refuse(out.get("error", "the message could not be checked"))
    if code:
        fixes = [i["message"] for i in out["items"] if i["level"] == "FIX"]
        sl.refuse(f"the {kind} does not pass pitch_check.py ({len(fixes)} to fix): " + "; ".join(fixes[:4])
                  + ("; …" if len(fixes) > 4 else "") + ". Fix it, then record it")


def cmd_pitch(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] == "found":
        sl.refuse(f"{s['id']} has not been vetted (speak_pipeline.py vet): no pitch goes to a stage nobody checked")
    if s["status"] != "vetted":
        sl.refuse(f"{s['id']} is {s['status']}; a first pitch goes to a vetted stage (use follow for a follow-up)")
    if not data["talks"]:
        sl.refuse("no talk on file (speak_pipeline.py talk add): a pitch offers one specific talk")
    talk = a.talk or 1
    if not 1 <= talk <= len(data["talks"]):
        sl.refuse(f"--talk is 1 to {len(data['talks'])}")
    saved = ""
    if a.text_file:
        checked(a, s, "pitch")
        text = sl.arg_text(None, a.text_file)
        saved = f"pitches/{s['id']}-1.txt"
        sl.write_atomic(sl.folder(a) / saved, text + "\n")
    s["touches"].append({"n": 1, "date": str(sl.day(a)), "channel": a.channel, "talk": talk, "file": saved})
    move(a, data, s, "pitched", channel=a.channel)
    due = sl.day(a) + timedelta(days=FOLLOW_GAP)
    return {"ok": True, "id": s["id"], "status": "pitched", "follow_up_due": str(due),
            "note": "the member sends it themselves, from their own address; this only records that they did"}


def cmd_follow(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] != "pitched":
        sl.refuse(f"{s['id']} is {s['status']}; a follow-up goes to a stage that was pitched and has not answered")
    follows = len(s["touches"]) - 1
    if follows >= MAX_FOLLOWS:
        sl.refuse(f"{s['id']} has had {MAX_FOLLOWS} follow-ups. Stop: a third reads as pestering. Mark it later "
                  f"(speak_pipeline.py reply --id {s['id']} --outcome later --ask-again <date>) or drop it")
    gap = (sl.day(a) - last_touch(s)).days
    if gap < FOLLOW_GAP:
        sl.refuse(f"the last message went {gap} day(s) ago; wait {FOLLOW_GAP} between touches")
    saved = ""
    n = len(s["touches"]) + 1
    if a.text_file:
        checked(a, s, "followup")
        saved = f"pitches/{s['id']}-{n}.txt"
        sl.write_atomic(sl.folder(a) / saved, sl.arg_text(None, a.text_file) + "\n")
    s["touches"].append({"n": n, "date": str(sl.day(a)), "channel": s["touches"][-1]["channel"], "file": saved})
    sl.save(a, data)
    left = MAX_FOLLOWS - (n - 1)
    return {"ok": True, "id": s["id"], "touch": n, "follow_ups_left": left,
            "next_due": str(sl.day(a) + timedelta(days=FOLLOW_GAP)) if left else "none: this was the last one"}


def cmd_reply(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] not in ("pitched", "replied"):
        sl.refuse(f"{s['id']} is {s['status']}")
    again = str(sl.parse_date(a.ask_again, "--ask-again")) if a.ask_again else ""
    if a.outcome == "later" and not again:
        sl.refuse("'later' needs --ask-again YYYY-MM-DD, so it comes back on that day and not before")
    s["reply"] = {"outcome": a.outcome, "date": str(sl.day(a)), "note": (a.note or "").strip(), "ask_again": again}
    move(a, data, s, "declined" if a.outcome == "no" else "replied", outcome=a.outcome)
    nxt = {"yes": f"confirm the date and terms in writing, then speak_pipeline.py book --id {s['id']} …",
           "maybe": "answer what they asked, once; then wait for them",
           "later": f"it comes back in 'today' on {again}",
           "no": "thank them, once. A no to this talk is not a no forever; note anything they said about next year"}[a.outcome]
    return {"ok": True, "id": s["id"], "status": s["status"], "next": nxt}


def cmd_book(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] not in ("replied", "pitched", "vetted"):
        sl.refuse(f"{s['id']} is {s['status']}")
    when = sl.parse_date(a.when, "--when")
    if a.fee is not None and a.fee < 0:
        sl.refuse("--fee is 0 or more")
    s["booking"] = {"when": str(when), "fee": a.fee, "terms": (a.terms or "").strip(),
                    "selling": a.selling or s.get("selling", "unknown"), "booked_on": str(sl.day(a))}
    s["when"] = str(when)
    if a.selling:
        s["selling"] = a.selling
    move(a, data, s, "booked", when=str(when))
    warn = []
    if not s["booking"]["terms"]:
        warn.append("nothing is recorded about the terms: get the date, length, fee or none, travel, recording and "
                    "whether an offer is allowed in writing, even as one email")
    if s["booking"]["selling"] == "unknown":
        warn.append("ask the host what may be offered from the stage; many forbid a sales pitch and allow a free resource")
    return {"ok": True, "id": s["id"], "status": "booked", "when": str(when), "warnings": warn,
            "next": "for the full talk: the Webinar Builder (\"Build my webinar\"); for the page a free resource lives on: Lead Capture"}


def cmd_deliver(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] != "booked":
        sl.refuse(f"{s['id']} is {s['status']}; only a booked stage is delivered")
    for k in ("attended", "leads"):
        v = getattr(a, k)
        if v is not None and v < 0:
            sl.refuse(f"--{k} is 0 or more")
    s["delivery"] = {"date": str(sl.day(a)), "attended": a.attended, "leads": a.leads, "note": (a.note or "").strip()}
    move(a, data, s, "delivered")
    return {"ok": True, "id": s["id"], "status": "delivered",
            "next": "within two days: thank the host, send what was promised to the room, ask the host for a line "
                    "the member may quote and who else they should speak to (speak_pipeline.py after …)",
            "note": "leads are people who asked for the resource or a conversation, counted, never estimated"}


def cmd_after(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] not in ("delivered", "followed_up"):
        sl.refuse(f"{s['id']} is {s['status']}")
    aft = s.setdefault("after", {"thanked": False, "testimonial_asked": False, "referral_asked": False, "clients": 0, "notes": []})
    aft["thanked"] = aft["thanked"] or bool(a.thanked)
    aft["testimonial_asked"] = aft["testimonial_asked"] or bool(a.testimonial_asked)
    aft["referral_asked"] = aft["referral_asked"] or bool(a.referral_asked)
    if a.clients is not None:
        if a.clients < 0:
            sl.refuse("--clients is 0 or more")
        aft["clients"] = a.clients
    if a.note:
        aft["notes"].append({"date": str(sl.day(a)), "note": a.note.strip()})
    if aft["thanked"]:
        move(a, data, s, "followed_up")
    else:
        sl.save(a, data)
    todo = [label for key, label in (("thanked", "thank the host"), ("testimonial_asked", "ask the host for a line to quote "
            "(the Proof Engine records the permission)"), ("referral_asked", "ask who else should hear this talk")) if not aft[key]]
    return {"ok": True, "id": s["id"], "status": s["status"], "still_to_do": todo, "clients": aft["clients"]}


def cmd_debrief(a):
    """Three questions after a talk: how the room reacted, what went well, what to change next time."""
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if s["status"] not in ("delivered", "followed_up"):
        sl.refuse(f"{s['id']} is {s['status']}; a debrief follows a talk that was given")
    well, improve = sl.arg_text(a.well, None), sl.arg_text(a.improve, None)
    if not well or not improve:
        sl.refuse("a debrief has what went well (--well) and one thing to change next time (--improve), in the member's words")
    if a.confidence is not None and not 1 <= a.confidence <= 10:
        sl.refuse("--confidence is 1 to 10")
    s["debrief"] = {"date": str(sl.day(a)), "reaction": (a.reaction or "").strip(), "well": well, "improve": improve,
                    "confidence": a.confidence}
    sl.save(a, data)
    return {"ok": True, "id": s["id"], "next_time": improve,
            "note": "one change per talk. It is read back before the next booked date"}


def cmd_goal(a):
    data = sl.load(a)
    g = data.setdefault("goal", {})
    for k in ("talks_per_month", "clients_per_quarter", "fee_income_year"):
        v = getattr(a, k)
        if v is not None:
            if v < 0:
                sl.refuse(f"--{k.replace('_', '-')} is 0 or more")
            g[k] = v
    if not g:
        sl.refuse("set at least one: --talks-per-month, --clients-per-quarter, --fee-income-year")
    g["set"] = str(sl.day(a))
    sl.save(a, data)
    return {"ok": True, "goal": g,
            "note": "the member's own target, for pacing. It is not a forecast: hosts decide who is booked, and when"}


def cmd_drop(a):
    data = sl.load(a)
    s = sl.find_stage(data, a.id)
    if not (a.reason or "").strip():
        sl.refuse("--reason says why, so the same stage is not found and chased again")
    if s["status"] in ("delivered", "followed_up"):
        sl.refuse(f"{s['id']} was delivered; it stays in the record")
    s["drop_reason"] = a.reason.strip()
    move(a, data, s, "dropped", reason=a.reason.strip())
    return {"ok": True, "id": s["id"], "status": "dropped"}


# ---------------------------------------------------------------- what is due, and how it is going
def cmd_today(a):
    data = sl.load(a)
    now = sl.day(a)
    due = []
    for s in data["stages"]:
        st = s["status"]
        if st == "found":
            due.append((2, s, "vet it, or drop it"))
        elif st == "vetted":
            dl = s.get("deadline")
            if dl and sl.parse_date(dl) < now:
                due.append((3, s, f"the deadline passed on {dl}: ask when the next round opens, or drop it"))
            elif dl and (sl.parse_date(dl) - now).days <= 14:
                due.append((0, s, f"pitch now: the deadline is {dl}"))
            else:
                due.append((2, s, "pitch it"))
        elif st == "pitched":
            follows = len(s["touches"]) - 1
            gap = (now - last_touch(s)).days
            if follows < MAX_FOLLOWS and gap >= FOLLOW_GAP:
                due.append((1, s, f"follow up (number {follows + 1} of {MAX_FOLLOWS}); the last message went {gap} days ago"))
            elif follows >= MAX_FOLLOWS and gap >= FOLLOW_GAP * 2:
                due.append((3, s, "no answer after two follow-ups: mark it later with a date, or drop it"))
        elif st == "replied":
            r = s.get("reply") or {}
            if r.get("outcome") == "later" and r.get("ask_again") and sl.parse_date(r["ask_again"]) <= now:
                due.append((1, s, "they said later, and later is now: one short note"))
            elif r.get("outcome") == "yes":
                due.append((0, s, "they said yes: confirm the date and terms in writing, then book it"))
        elif st == "booked":
            days = (sl.parse_date(s["booking"]["when"]) - now).days
            if days < 0:
                due.append((0, s, "the date has passed: record how it went (deliver)"))
            elif days <= 14:
                tip = next((x["debrief"]["improve"] for x in sorted((y for y in data["stages"] if y.get("debrief")),
                            key=lambda y: y["debrief"]["date"], reverse=True)), "")
                due.append((0, s, f"in {days} day(s): confirm the room, the time, the microphone, what may be offered, "
                            "and have the resource page ready" + (f". Last time you said you would change: {tip}" if tip else "")))
        elif st == "delivered":
            due.append((0, s, "thank the host and send what was promised to the room, within two days"))
        elif st == "followed_up":
            aft = s.get("after") or {}
            if not aft.get("testimonial_asked") or not aft.get("referral_asked"):
                due.append((2, s, "ask the host for a line to quote and who else should hear the talk"))
            if not s.get("debrief"):
                due.append((2, s, "three questions on how it went (debrief), while it is fresh"))
    due.sort(key=lambda x: (x[0], x[1].get("deadline") or x[1].get("when") or "9999"))
    return {"ok": True, "date": str(now), "due": [{"id": s["id"], "name": s["name"], "status": s["status"], "do": what}
                                                   for _, s, what in due[:a.limit]],
            "more": max(0, len(due) - a.limit),
            "note": "ten minutes a day beats a long session once a month; the member sends every message themselves"}


def cmd_report(a):
    data = sl.load(a)
    st = data["stages"]
    count = lambda *names: sum(1 for s in st if s["status"] in names)  # noqa: E731
    pitched = [s for s in st if s.get("touches")]
    answered = [s for s in pitched if s.get("reply")]
    yes = [s for s in pitched if s.get("booking")]
    done = [s for s in st if s.get("delivery")]
    att = sum((s["delivery"].get("attended") or 0) for s in done)
    leads = sum((s["delivery"].get("leads") or 0) for s in done)
    clients = sum(((s.get("after") or {}).get("clients") or 0) for s in done)
    fees = sum((s["booking"].get("fee") or 0) for s in yes)
    by_kind = {}
    for s in pitched:
        k = by_kind.setdefault(s["kind"], {"pitched": 0, "booked": 0})
        k["pitched"] += 1
        k["booked"] += 1 if s.get("booking") else 0
    enough = len(pitched) >= MIN_SAMPLE
    now = sl.day(a)
    goal = data.get("goal") or {}
    month_ago, quarter_ago, year_ago = now - timedelta(days=30), now - timedelta(days=91), now - timedelta(days=365)
    recent = lambda s, since: sl.parse_date(s["delivery"]["date"]) >= since  # noqa: E731
    against = {}
    if goal.get("talks_per_month") is not None:
        against["talks"] = f"{sum(1 for s in done if recent(s, month_ago))} given in the last 30 days; the goal is {goal['talks_per_month']:g} a month"
    if goal.get("clients_per_quarter") is not None:
        got = sum(((s.get("after") or {}).get("clients") or 0) for s in done if recent(s, quarter_ago))
        against["clients"] = f"{got} from talks in the last 91 days; the goal is {goal['clients_per_quarter']:g} a quarter"
    if goal.get("fee_income_year") is not None:
        got = sum((s["booking"].get("fee") or 0) for s in done if s.get("booking") and recent(s, year_ago))
        against["fees"] = f"{got:,.0f} in fees from talks given in the last year; the goal is {goal['fee_income_year']:,.0f}"
    last = max((s for s in done if s.get("debrief")), key=lambda s: s["debrief"]["date"], default=None)
    return {"ok": True, "date": str(sl.day(a)),
            "stages": {"found": count("found"), "vetted": count("vetted"), "pitched": len(pitched), "answered": len(answered),
                       "booked": len(yes), "delivered": len(done), "declined": count("declined"), "dropped": count("dropped")},
            "replies": f"{len(answered)} of {len(pitched)} pitches answered",
            "bookings": f"{len(yes)} of {len(pitched)} pitches booked",
            "from_the_stage": {"talks_given": len(done), "people_in_rooms": att, "leads": leads, "clients": clients,
                               "fees": fees},
            "by_kind": by_kind,
            "against_the_goal": against,
            "change_next_time": (f"{last['debrief']['improve']} (from {last['name']}, {last['debrief']['date']})" if last else ""),
            "read": ("enough pitches to see a pattern: do more of the kind that books" if enough else
                     f"{len(pitched)} pitch(es) so far; under {MIN_SAMPLE} it is too few to judge a rate. Keep the count going"),
            "weakest_step": weakest(len(st), count("found"), len(pitched), len(answered), len(yes), len(done), leads) if enough else "",
            "note": "counts, not estimates. A rate is always shown with its two numbers"}


def weakest(total, found, pitched, answered, booked, done, leads):
    if found > pitched:
        return "more stages found than pitched: vet and pitch what is already on the list before finding more"
    if pitched and answered * 4 < pitched:
        return "few pitches are answered: check the pitch names the host's audience and offers one specific talk, and that it went to the person who chooses speakers"
    if answered and booked * 3 < answered:
        return "answers are not turning into bookings: ask what they need to say yes (a shorter length, a date, a sample)"
    if done and not leads:
        return "talks are given and nobody asks for more: the free resource and how the room asks for it need work"
    return "no single weak step stands out"


def cmd_plan(a):
    data = sl.load(a)
    start = sl.parse_date(a.start, "--start") if a.start else sl.day(a)
    start += timedelta(days=(7 - start.weekday()) % 7)            # the next Monday, or today if it is one
    if not 4 <= a.weeks <= 26:
        sl.refuse("--weeks is 4 to 26")
    has_talk = bool(data["talks"])
    weeks = []
    for i in range(a.weeks):
        mon = start + timedelta(weeks=i)
        if i == 0:
            todo = (["finish the speaking profile"] if not data.get("profile_ready") else []) + \
                   (["settle one talk: title, promise, three takeaways"] if not has_talk else []) + \
                   ["write the bio and the one-sheet", "find and vet five local or warm stages"]
        elif i == 1:
            todo = ["pitch three vetted stages", "find and vet five more", "say the talk out loud, once, timed"]
        elif i % 4 == 0:
            todo = ["read the scorecard (report) and change one thing", "pitch three", "follow up what is due",
                    "ask a past host who else should hear the talk"]
        else:
            todo = ["pitch three", "follow up what is due", "find and vet three more"]
        weeks.append({"week": i + 1, "monday": str(mon), "do": todo})
    md = ["# Speaking plan", "", f"From {start} for {a.weeks} weeks. Ten minutes a day (`today`), one longer sitting a week.", ""]
    for w in weeks:
        md += [f"## Week {w['week']}: {w['monday']}", ""] + [f"- [ ] {t}" for t in w["do"]] + [""]
    md += ["A booked date changes the plan: the two weeks before it go to the talk, the room and the resource page.", ""]
    sl.write_atomic(sl.folder(a) / "plan.md", "\n".join(md))
    return {"ok": True, "plan": str(sl.folder(a) / "plan.md"), "weeks": weeks[:4], "of": a.weeks,
            "note": "the plan sets a pace the member can keep. It does not promise a booking by a date: hosts decide that"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--folder"); x.add_argument("--today")
        return x
    p("init"); p("intake"); p("ready"); p("flags"); p("rank")
    x = p("answer"); x.add_argument("--key", required=True); x.add_argument("--text"); x.add_argument("--text-file")
    x.add_argument("--from"); x.add_argument("--append", action="store_true"); x.add_argument("--draft", action="store_true")
    x = p("prefill"); x.add_argument("--business-file"); x.add_argument("--chars", type=int, default=1500)
    x = p("confirm"); x.add_argument("--keys"); x.add_argument("--all", action="store_true"); x.add_argument("--by", required=True)
    x = p("talk"); x.add_argument("action", choices=["add", "list"]); x.add_argument("--title"); x.add_argument("--promise")
    x.add_argument("--takeaway", action="append"); x.add_argument("--for"); x.add_argument("--length"); x.add_argument("--format")
    x = p("add"); x.add_argument("--name"); x.add_argument("--host"); x.add_argument("--kind", required=True)
    x.add_argument("--source", required=True); x.add_argument("--seen", required=True); x.add_argument("--audience")
    x.add_argument("--size", type=int); x.add_argument("--when"); x.add_argument("--recurring"); x.add_argument("--deadline")
    x.add_argument("--contact-role"); x.add_argument("--pays", choices=["yes", "no", "unknown"])
    x.add_argument("--selling", choices=["allowed", "not allowed", "unknown"]); x.add_argument("--note")
    x = p("vet"); x.add_argument("--id", required=True)
    for k in WEIGHTS:
        x.add_argument("--" + k, type=int)
    x.add_argument("--flag", action="append"); x.add_argument("--checked"); x.add_argument("--accept-risk", action="store_true")
    x.add_argument("--by"); x.add_argument("--reason")
    x = p("list"); x.add_argument("--status", choices=sl.STATUSES); x.add_argument("--kind", choices=sl.KINDS)
    x = p("pitch"); x.add_argument("--id", required=True)
    x.add_argument("--channel", required=True, choices=["email", "form", "linkedin", "phone", "in person"])
    x.add_argument("--text-file"); x.add_argument("--talk", type=int); x.add_argument("--business-file")
    x = p("follow"); x.add_argument("--id", required=True); x.add_argument("--text-file"); x.add_argument("--business-file")
    x = p("reply"); x.add_argument("--id", required=True); x.add_argument("--outcome", required=True, choices=["yes", "no", "maybe", "later"])
    x.add_argument("--note"); x.add_argument("--ask-again")
    x = p("book"); x.add_argument("--id", required=True); x.add_argument("--when", required=True); x.add_argument("--fee", type=float)
    x.add_argument("--terms"); x.add_argument("--selling", choices=["allowed", "not allowed"])
    x = p("deliver"); x.add_argument("--id", required=True); x.add_argument("--attended", type=int); x.add_argument("--leads", type=int)
    x.add_argument("--note")
    x = p("after"); x.add_argument("--id", required=True); x.add_argument("--clients", type=int); x.add_argument("--thanked", action="store_true")
    x.add_argument("--testimonial-asked", action="store_true"); x.add_argument("--referral-asked", action="store_true"); x.add_argument("--note")
    x = p("debrief"); x.add_argument("--id", required=True); x.add_argument("--reaction"); x.add_argument("--well")
    x.add_argument("--improve"); x.add_argument("--confidence", type=int)
    x = p("goal"); x.add_argument("--talks-per-month", type=float); x.add_argument("--clients-per-quarter", type=float)
    x.add_argument("--fee-income-year", type=float)
    x = p("drop"); x.add_argument("--id", required=True); x.add_argument("--reason")
    x = p("today"); x.add_argument("--limit", type=int, default=10)
    p("report")
    x = p("plan"); x.add_argument("--weeks", type=int, default=12); x.add_argument("--start")
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    sl.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
