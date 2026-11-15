#!/usr/bin/env python3
"""Company Blueprint: the functions a business needs, the positions that own them, what each position is
measured by, and which hat the owner hands off first.

  blueprint.py init
  blueprint.py prefill [--business-file F]            what the Business File already holds
  blueprint.py aim --key primary_aim|objective|owner_role --text-file F [--from "§17" --draft]
  blueprint.py confirm --all | --keys a,b  --by member
  blueprint.py function add --key sales --name "Sales" --covered-by owner [--hours 6 --only-owner 2 --documented 3]
  blueprint.py function list | remove --key K
  blueprint.py position add --title … --function sales --reports-to POS-01|none --held-by owner --mission …
                            --accountability … (3 to 7) --may … --needs-approval … [--sop … --gets-from … --gives-to …
                            --daily … --weekly … --monthly … --review weekly|monthly|quarterly]
  blueprint.py position list | remove --id POS-02 | hold --id POS-02 --held-by "operations assistant"
  blueprint.py kpi add --position POS-02 --name … --purpose … --kind leading|lagging --formula … --source … --period week
                       [--numerator … --denominator …] [--baseline 0.22 --baseline-basis "CRM, last quarter"]
                       [--target 0.3 --target-basis "member decision" --direction up] [--trigger-below 0.2 | --trigger-above N] [--sop …]
  blueprint.py kpi list | remove --id KPI-03
  blueprint.py check                                   GO or FIX: is every outcome owned, measured and teachable?
  blueprint.py handoff                                 which hat to hand off first, from the member's own hours
  blueprint.py maturity                                a five-step read of how owner-dependent the business is
  blueprint.py review --kpi KPI-03 --value 0.18 [--cause data|target|system|training|resources|person --ruled-out …] [--note …]
  blueprint.py render                                  org chart, a contract per position, KPI definitions, scorecard
  blueprint.py report

Every command takes --folder (default ./blueprint) and --today YYYY-MM-DD. JSON on stdout; exit 0 ok, 1 refused.

The rule: the member's own facts or nothing. A baseline is a number the member read off their own records,
or it is "not measured yet". A target has a basis the member states. No benchmark, salary, head count or
result is invented. A position contract here is an operating agreement about a role, never an employment
contract; pay, hours, classification and termination are for the member's HR or legal adviser.
"""
import argparse, json, os, re, sys, tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
SCHEMA = 1
AIM_KEYS = {
    "primary_aim": ("What do you want your life to look like, and what must the business do to support it?",
                    "Time, money, how involved you want to stay. Your own words; there is no right answer.", (17, 1)),
    "objective": ("Where is the business going in the next one to three years?",
                  "Revenue, clients, team, how much of it runs without you. Numbers only if they are yours.", (1, 3, 6)),
    "owner_role": ("Which work do you want to keep doing yourself, and which do you want off your plate?",
                   "The work you love, the work only you can do today, and the work that wears you out.", (17, 10)),
}
STARTER_FUNCTIONS = [("leadership", "Leadership and direction"), ("marketing", "Marketing"), ("sales", "Sales"),
                     ("delivery", "Delivery"), ("client-care", "Client care"), ("finance", "Finance and admin"),
                     ("people", "People and training")]
PERIODS = ("day", "week", "month", "quarter", "year")
BASES = ("member history", "member decision", "contract or law")
CAUSES = ("data", "target", "system", "training", "resources", "person")
VAGUE = re.compile(r"^(?:help|assist|support|handle|deal with|work on|be responsible for (?:helping|assisting)|"
                   r"responsible for (?:helping|assisting)|do|manage things|take care of)\b|\b(?:as needed|etc\.?|and so on|various|"
                   r"miscellaneous|other duties)\b", re.I)
VANITY = re.compile(r"\b(?:emails? sent|calls? made|dials|impressions|followers|likes|posts? published|hours (?:worked|logged|trained)|"
                    r"training hours|meetings? held|sops? (?:written|completed)|page views)\b", re.I)
SURVEILLANCE = re.compile(r"\b(?:keystrokes?|screen ?time|screenshots?|mouse (?:movement|activity)|webcam|location tracking|gps tracking|"
                          r"idle time|browser history|private messages?)\b", re.I)
CONTACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
DASHES = ("—", "–")


# ------------------------------------------------------------------ plumbing
def emit(obj, code=0):
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    sys.exit(code)


def refuse(msg, **extra):
    emit({"ok": False, "error": msg, **extra}, 1)


def read_text(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def write_atomic(path, text):
    p = Path(path)
    if p.is_symlink() or (p.exists() and not p.is_file()):
        refuse(f"{p} is not an ordinary file, so it will not be replaced")
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".tmp-", suffix=p.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def words(t):
    return len(re.findall(r"[^\W_][\w'-]*", t or ""))


def parse_date(s, what="date"):
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        refuse(f"{what} must be YYYY-MM-DD, not '{s}'")


def day(a):
    return parse_date(a.today, "--today") if getattr(a, "today", None) else date.today()


def finite(s):
    v = float(s)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("not a finite number")
    return v


def folder(a):
    return Path(getattr(a, "folder", None) or "blueprint")


DEFAULT = {"schema": SCHEMA, "aim": {}, "functions": [], "positions": [], "kpis": [], "reviews": [], "handed": [],
           "last_pos": 0, "last_kpi": 0}


def load(a, create=False):
    p = folder(a) / "blueprint.json"
    if not p.exists():
        if not create:
            refuse(f"no blueprint folder at {folder(a)}; run: blueprint.py init")
        return json.loads(json.dumps(DEFAULT))
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        refuse(f"blueprint.json is not valid JSON: {e}")
    if not isinstance(d, dict):
        refuse("blueprint.json should hold a JSON object")
    for k, v in DEFAULT.items():
        if k not in d or (isinstance(v, (list, dict)) and not isinstance(d[k], type(v))):
            d[k] = json.loads(json.dumps(v))
    return d


def save(a, d):
    d["updated"] = str(date.today())
    write_atomic(folder(a) / "blueprint.json", json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def text_arg(a, what="--text"):
    if getattr(a, "text_file", None):
        if not Path(a.text_file).is_file():
            refuse(f"file not found: {a.text_file}")
        return read_text(a.text_file).strip()
    return (getattr(a, "text", None) or "").strip()


def clean(label, value, need=True):
    v = (value or "").strip()
    if need and not v:
        refuse(f"--{label} is needed")
    if any(x in v for x in DASHES):
        refuse(f"no em or en dashes in --{label}; use a comma, a colon or a full stop")
    if CONTACT.search(v):
        refuse(f"--{label} holds an email address; name the role, not a person's contact details")
    return v


def find_business_file(a):
    if getattr(a, "business_file", None):
        if not Path(a.business_file).is_file():
            refuse(f"file not found: {a.business_file}")
        return a.business_file
    for cand in (Path("BUILDROOM_BUSINESS_FILE.md"), folder(a).resolve().parent / "BUILDROOM_BUSINESS_FILE.md"):
        if cand.is_file():
            return str(cand)
    return None


def file_sections(bf):
    out, cur = {}, None
    if not bf:
        return out
    for line in read_text(bf).splitlines():
        m = re.match(r"##\s+(\d+)\.\s+(.*)", line)
        if m:
            cur = int(m.group(1))
            out[cur] = {"title": m.group(2).strip(), "status": "", "lines": []}
            continue
        if cur is None:
            continue
        st = re.search(r"\*\*Status:\*\*\s*([A-Za-z ]+?)\s*(?:·|$)", line)
        if st:
            out[cur]["status"] = st.group(1).strip().lower()
            continue
        t = line.strip()
        if not t or t.startswith(("_Built by", "---", "|---")) or re.fullmatch(r"\|[\s|]*\|", t):
            continue
        f = re.match(r"[-*]\s+\*\*[^*]+\*\*(?:\s*\([^)]*\))?\s*:?\s*(.*)", t)
        if f is not None and f.group(1).strip() in ("", "—", "-", "[ ]"):
            continue
        out[cur]["lines"].append(t)
    for s in out.values():
        s["body"] = "\n".join(s.pop("lines"))
        s["filled"] = words(s["body"]) >= 8 and s["status"] != "not started"
    return out


def pos(d, pid):
    for p in d["positions"]:
        if str(p.get("id", "")).lower() == str(pid).lower():
            return p
    refuse(f"no position {pid}; blueprint.py position list")


def is_owner(who):
    return bool(re.search(r"\b(?:owner|founder|me|myself|i)\b", str(who or ""), re.I))


# ------------------------------------------------------------------ commands
def cmd_init(a):
    f = folder(a)
    existed = (f / "blueprint.json").exists()
    d = load(a, create=True)
    (f / "positions").mkdir(parents=True, exist_ok=True)
    save(a, d)
    return {"ok": True, "folder": str(f), "created": not existed,
            "starter_functions": [{"key": k, "name": n} for k, n in STARTER_FUNCTIONS],
            "next": "blueprint.py prefill, then the three aim questions, then the functions"}


def cmd_prefill(a):
    d = load(a)
    bf = find_business_file(a)
    if not bf:
        refuse("no Business File found here; give --business-file, or ask the member each question")
    secs = file_sections(bf)

    def src(nums):
        return [{"section": f"§{n}", "title": secs[n]["title"], "status": secs[n]["status"] or "unknown", "text": secs[n]["body"][:1500]}
                for n in nums if n in secs and secs[n]["filled"]]
    draft, ask = [], []
    for key, (q, helper, nums) in AIM_KEYS.items():
        if str((d["aim"].get(key) or {}).get("text", "")).strip():
            continue
        found = src(nums)
        (draft if found else ask).append({"key": key, "question": q, **({"from": found} if found else {"helper": helper})})
    return {"ok": True, "business_file": bf, "draft_from_file": draft, "ask_the_member": ask,
            "already_built": {"sops": src((9,)), "role_and_hiring": src((10,)), "training": src((11,)), "weekly_ops": src((12,)),
                              "offer_and_delivery": src((3, 6))},
            "missing_sections": [f"§{n}" for n in (1, 3, 9, 10, 11, 12, 17) if n not in secs or not secs[n]["filled"]],
            "rule": "a draft uses only what the file says and is shown to the member to confirm. Hours, baselines and "
                    "targets are never drafted: only the member has them"}


def cmd_aim(a):
    d = load(a)
    if a.key not in AIM_KEYS:
        refuse(f"--key is one of {', '.join(AIM_KEYS)}")
    text = text_arg(a)
    if not text:
        refuse("the answer is empty (--text '…' or --text-file path)")
    src = (getattr(a, "from") or "member").strip()
    d["aim"][a.key] = {"text": text, "from": src, "draft": bool(a.draft) or src.lower() != "member", "date": str(day(a))}
    save(a, d)
    return {"ok": True, "key": a.key, "draft": d["aim"][a.key]["draft"],
            "missing": [k for k in AIM_KEYS if not str((d["aim"].get(k) or {}).get("text", "")).strip()]}


def cmd_confirm(a):
    d = load(a)
    if a.by != "member":
        refuse("only the member confirms what was drafted from their file (--by member)")
    keys = list(AIM_KEYS) if a.all else [k.strip() for k in (a.keys or "").split(",") if k.strip()]
    if not keys or any(k not in AIM_KEYS for k in keys):
        refuse("--keys is a comma list of aim keys, or use --all")
    done = []
    for k in keys:
        v = d["aim"].get(k)
        if isinstance(v, dict) and v.get("draft") and str(v.get("text", "")).strip():
            v["draft"] = False
            v["confirmed"] = str(day(a))
            done.append(k)
    save(a, d)
    return {"ok": True, "confirmed": done, "still_draft": [k for k, v in d["aim"].items() if isinstance(v, dict) and v.get("draft")]}


def cmd_function(a):
    d = load(a)
    if a.action == "list":
        return {"ok": True, "functions": d["functions"], "starter_functions": [{"key": k, "name": n} for k, n in STARTER_FUNCTIONS]}
    key = re.sub(r"[^a-z0-9]+", "-", (a.key or "").lower()).strip("-")
    if not key:
        refuse("--key is a short name for the function (sales, delivery, client-care)")
    if a.action == "remove":
        if any(p["function"] == key for p in d["positions"]):
            refuse(f"a position still owns {key}; remove or move the position first")
        n = len(d["functions"])
        d["functions"] = [f for f in d["functions"] if f["key"] != key]
        save(a, d)
        return {"ok": True, "removed": n - len(d["functions"])}
    name, by = clean("name", a.name), clean("covered-by", a.covered_by)
    for label, v, lo, hi in (("hours", a.hours, 0, 100), ("only-owner", a.only_owner, 1, 5), ("documented", a.documented, 1, 5)):
        if v is not None and not lo <= v <= hi:
            refuse(f"--{label} is {lo} to {hi}")
    row = {"key": key, "name": name, "covered_by": by, "hours": a.hours, "only_owner": a.only_owner, "documented": a.documented,
           "note": clean("note", a.note, need=False), "date": str(day(a))}
    old = next((f for f in d["functions"] if f["key"] == key), None)
    if old:
        old.update({k: v for k, v in row.items() if v not in (None, "")})
    else:
        d["functions"].append(row)
    save(a, d)
    warn = []
    if is_owner(by) and a.hours is None:
        warn.append("ask the member how many hours a week this takes them; the hand-off ranking needs their number, not a guess")
    return {"ok": True, "function": key, "functions": len(d["functions"]), "updated": bool(old), "warnings": warn}


def cmd_position(a):
    d = load(a)
    if a.action == "list":
        return {"ok": True, "positions": d["positions"]}
    if a.action == "remove":
        p = pos(d, a.id)
        if any(q.get("reports_to") == p["id"] for q in d["positions"]):
            refuse(f"another position reports to {p['id']}; change that first")
        d["positions"] = [q for q in d["positions"] if q["id"] != p["id"]]
        d["kpis"] = [k for k in d["kpis"] if k["position"] != p["id"]]
        save(a, d)
        return {"ok": True, "removed": p["id"], "note": "its KPIs went with it"}
    if a.action == "hold":
        p = pos(d, a.id)
        who = clean("held-by", a.held_by)
        was = p.get("held_by", "")
        p["held_by"] = who
        if is_owner(was) and not is_owner(who):
            d["handed"].append({"position": p["id"], "to": who, "date": str(day(a))})
        same = [q for q in d["positions"] if q["function"] == p["function"]]
        if not any(p.get("reports_to") == q["id"] for q in same):          # the position that answers for the function
            for f in d["functions"]:
                if f["key"] == p["function"]:
                    f["covered_by"] = who
        save(a, d)
        return {"ok": True, "id": p["id"], "held_by": who, "handed_off": is_owner(was) and not is_owner(who),
                "next": "walk the new holder through the contract, its SOPs and its scorecard; both acknowledge it (Training Docs builds the training)"}
    title, mission = clean("title", a.title), clean("mission", a.mission)
    fn = (a.function or "").strip().lower()
    if not any(f["key"] == fn for f in d["functions"]):
        refuse(f"--function must be one on file ({', '.join(f['key'] for f in d['functions']) or 'none yet: function add'})")
    if any(p["title"].lower() == title.lower() for p in d["positions"]):
        refuse("a position with this title is already on file (position list; position remove --id …)")
    rt = (a.reports_to or "").strip()
    if rt.lower() in ("", "none", "nobody"):
        if any(not p.get("reports_to") for p in d["positions"]):
            refuse("one position sits at the top; this one needs --reports-to POS-NN")
        rt = ""
    else:
        rt = pos(d, rt)["id"]
    if words(mission) < 8 or VAGUE.search(mission):
        refuse("the mission says why the position exists and what result it produces, in a sentence of eight words or more")
    acc = [clean("accountability", x) for x in (a.accountability or [])]
    if not 3 <= len(acc) <= 7:
        refuse(f"a position has three to seven accountabilities; got {len(acc)}. More than seven is two positions")
    weak = [x for x in acc if VAGUE.search(x) or words(x) < 6]
    if weak:
        refuse("these read as tasks or vague help, not results the position owns: " + " | ".join(weak) +
               ". Write the outcome and how anyone would know it happened, e.g. \"Every new enquiry gets a reply within one working day\"")
    may = [clean("may", x) for x in (a.may or [])]
    appr = [clean("needs-approval", x) for x in (a.needs_approval or [])]
    if not may or (rt and not appr):
        refuse("say what the position may decide alone (--may) and what needs approval (--needs-approval), at least one of each: "
               "a role with no authority sends every decision back to the owner")
    d["last_pos"] = int(d.get("last_pos", 0)) + 1
    pid = f"POS-{d['last_pos']:02d}"
    lst = lambda xs, label: [clean(label, x) for x in (xs or [])]  # noqa: E731
    d["positions"].append({
        "id": pid, "title": title, "function": fn, "reports_to": rt, "held_by": clean("held-by", a.held_by), "mission": mission,
        "accountabilities": acc, "may": may, "needs_approval": appr, "sops": lst(a.sop, "sop"),
        "gets_from": lst(a.gets_from, "gets-from"), "gives_to": lst(a.gives_to, "gives-to"),
        "daily": lst(a.daily, "daily"), "weekly": lst(a.weekly, "weekly"), "monthly": lst(a.monthly, "monthly"),
        "review": a.review or "monthly", "version": 1, "added": str(day(a))})
    save(a, d)
    warn = []
    bf = find_business_file(a)
    sop_text = (file_sections(bf).get(9, {}).get("body", "") if bf else "").lower()
    missing = [s for s in d["positions"][-1]["sops"] if s.lower() not in sop_text]
    if not d["positions"][-1]["sops"]:
        warn.append("no SOP is linked: a position nobody can be trained into stays with whoever holds it today")
    elif missing:
        warn.append("not found in §9 of the Business File: " + ", ".join(missing) + ". The SOP Creator writes them")
    return {"ok": True, "id": pid, "positions": len(d["positions"]), "warnings": warn, "next": f"blueprint.py kpi add --position {pid} …"}


def cmd_kpi(a):
    d = load(a)
    if a.action == "list":
        return {"ok": True, "kpis": d["kpis"]}
    if a.action == "remove":
        n = len(d["kpis"])
        d["kpis"] = [k for k in d["kpis"] if k["id"].lower() != str(a.id).lower()]
        if len(d["kpis"]) == n:
            refuse(f"no KPI {a.id}")
        save(a, d)
        return {"ok": True, "removed": a.id}
    p = pos(d, a.position)
    name, purpose, formula, source = clean("name", a.name), clean("purpose", a.purpose), clean("formula", a.formula), clean("source", a.source)
    blob = " ".join([name, purpose, formula, source])
    if SURVEILLANCE.search(blob):
        refuse("this measures a person being watched, not a result. It is not recorded here; monitoring staff is a legal question "
               "for the member's HR or legal adviser, and it does not show whether the work is good")
    if a.kind not in ("leading", "lagging"):
        refuse("--kind is leading (an activity that should move a result) or lagging (the result itself)")
    if a.period not in PERIODS:
        refuse(f"--period is one of {', '.join(PERIODS)}")
    if len([k for k in d["kpis"] if k["position"] == p["id"]]) >= 5:
        refuse(f"{p['id']} already has five KPIs. A sixth means nobody looks at any of them: remove one first")
    rate = bool(re.search(r"/|%|\brate\b|\bper\b|÷|\bratio\b", formula + " " + name, re.I))
    num, den = clean("numerator", a.numerator, need=False), clean("denominator", a.denominator, need=False)
    if rate and not (num and den):
        refuse("a rate needs --numerator and --denominator, each saying exactly which records count: two people must get the same number")
    if words(formula) < 3:
        refuse("--formula says how the number is worked out, in words anyone on the team could follow")
    if (a.baseline is None) != (not (a.baseline_basis or "").strip()):
        refuse("a baseline comes with where it was read from (--baseline 0.22 --baseline-basis \"CRM, July to September\"). "
               "If nobody has measured it, give neither: it is recorded as not measured yet")
    if a.target is not None:
        if a.target_basis not in BASES:
            refuse(f"a target needs --target-basis: one of {', '.join(BASES)}. A target from an industry list or from this tool is not a basis")
        if a.direction not in ("up", "down"):
            refuse("--direction says whether higher (up) or lower (down) is better")
    elif a.target_basis:
        refuse("--target-basis was given with no --target")
    if a.trigger_below is not None and a.trigger_above is not None:
        refuse("give --trigger-below or --trigger-above, not both")
    d["last_kpi"] = int(d.get("last_kpi", 0)) + 1
    kid = f"KPI-{d['last_kpi']:02d}"
    d["kpis"].append({
        "id": kid, "position": p["id"], "name": name, "purpose": purpose, "kind": a.kind, "formula": formula, "numerator": num,
        "denominator": den, "source": source, "period": a.period, "baseline": a.baseline,
        "baseline_basis": clean("baseline-basis", a.baseline_basis, need=False), "target": a.target, "target_basis": a.target_basis or "",
        "direction": a.direction or "", "trigger_below": a.trigger_below, "trigger_above": a.trigger_above,
        "sops": [clean("sop", x) for x in (a.sop or [])], "version": 1, "added": str(day(a))})
    save(a, d)
    warn = []
    if VANITY.search(name + " " + formula):
        warn.append("this counts activity, not a result. Keep it only beside a measure of what the activity produced")
    if a.baseline is None:
        warn.append("not measured yet: measure it for a full period before setting a target")
    elif a.target is None:
        warn.append("no target yet: that is fine. Set one when the member has decided what good looks like")
    if a.trigger_below is None and a.trigger_above is None:
        warn.append("no trigger: say at what number someone looks into it, so a bad week is noticed")
    if a.kind == "leading":
        warn.append("a leading measure is a guess that it moves the result. Check that against the member's own numbers after a quarter")
    return {"ok": True, "id": kid, "position": p["id"], "warnings": warn}


def checks(d, bf=None):
    fix, watch = [], []
    aim_missing = [k for k in AIM_KEYS if not str((d["aim"].get(k) or {}).get("text", "")).strip()]
    if aim_missing:
        fix.append("the aim is not answered: " + ", ".join(aim_missing))
    drafts = [k for k, v in d["aim"].items() if isinstance(v, dict) and v.get("draft")]
    if drafts:
        fix.append("drafted from the Business File and not confirmed by the member: " + ", ".join(drafts))
    if len(d["functions"]) < 3:
        fix.append("fewer than three functions are listed: every business has at least getting clients, serving them and handling the money")
    tops = [p for p in d["positions"] if not p.get("reports_to")]
    if d["positions"] and len(tops) != 1:
        fix.append(f"{len(tops)} positions sit at the top; there is one")
    for f in d["functions"]:
        owners = [p for p in d["positions"] if p["function"] == f["key"]]
        heads = [p for p in owners if not any(p.get("reports_to") == q["id"] for q in owners)]
        if not owners:
            fix.append(f"nobody is accountable for {f['name']}: add the position, even if the owner holds it today")
        elif len(heads) > 1:
            fix.append(f"{f['name']} has {len(heads)} positions with nobody above them inside it ({', '.join(p['id'] for p in heads)}): "
                       "one of them is accountable for the function; the others report to it")
    sop_text = (file_sections(bf).get(9, {}).get("body", "") if bf else "").lower()
    for p in d["positions"]:
        ks = [k for k in d["kpis"] if k["position"] == p["id"]]
        if not ks:
            fix.append(f"{p['id']} {p['title']} has no measure: add one to three KPIs")
        elif all(k["kind"] == "leading" for k in ks):
            watch.append(f"{p['id']} is measured only by activity; add the result it is there to produce")
        if not p.get("sops"):
            watch.append(f"{p['id']} {p['title']} links to no SOP, so nobody else can be trained into it")
        elif bf:
            miss = [s for s in p["sops"] if s.lower() not in sop_text]
            if miss:
                watch.append(f"{p['id']}: not in §9 yet: {', '.join(miss)}")
        if not p.get("gets_from") and not p.get("gives_to") and len(d["positions"]) > 1:
            watch.append(f"{p['id']} has no hand-offs recorded: say what it receives and what it passes on")
    for k in d["kpis"]:
        if not any(p["id"] == k["position"] for p in d["positions"]):
            fix.append(f"{k['id']} belongs to a position that is gone")
        if k.get("target") is not None and k.get("baseline") is None:
            watch.append(f"{k['id']} has a target and no baseline: nobody knows how far away the target is")
    held = [p for p in d["positions"] if is_owner(p.get("held_by"))]
    if d["positions"] and len(held) == len(d["positions"]):
        watch.append(f"the owner holds all {len(held)} positions. That is normal at the start: blueprint.py handoff says which to pass on first")
    if not bf:
        watch.append("no Business File was found, so SOP links were not checked against §9")
    return fix, watch


def cmd_check(a):
    d = load(a)
    fix, watch = checks(d, find_business_file(a))
    return {"ok": not fix, "verdict": "GO" if not fix else "FIX", "fix": fix, "watch": watch,
            "counts": {"functions": len(d["functions"]), "positions": len(d["positions"]), "kpis": len(d["kpis"])},
            "limits": "a script cannot tell whether a mission is the right one, whether a target is fair, or whether a person can do "
                      "the work. The member decides those"}


def cmd_handoff(a):
    d = load(a)
    rows, unknown = [], []
    for f in d["functions"]:
        if not is_owner(f.get("covered_by")):
            continue
        if None in (f.get("hours"), f.get("only_owner"), f.get("documented")):
            unknown.append(f["name"])
            continue
        score = round(f["hours"] * (6 - f["only_owner"]) * f["documented"] / 25, 1)
        first = ("write it down first: the SOP Creator, one procedure at a time" if f["documented"] <= 2 else
                 "say what makes it owner-only, and whether that is skill, trust or habit" if f["only_owner"] >= 4 else
                 "ready to hand off: a position contract, its SOPs, a scorecard, then training")
        rows.append({"function": f["name"], "key": f["key"], "hours_a_week": f["hours"], "only_owner": f["only_owner"],
                     "documented": f["documented"], "score": score, "first_step": first})
    rows.sort(key=lambda r: -r["score"])
    if not rows and not unknown:
        refuse("no function is recorded as covered by the owner; function add --covered-by owner --hours … --only-owner … --documented …")
    return {"ok": True, "rank": rows, "hours_named": sum(r["hours_a_week"] for r in rows), "not_ranked": unknown,
            "how": "hours a week × how little it needs the owner (1 only the owner, 5 anyone trained) × how written down it is, "
                   "all three from the member",
            "note": "it ranks; it does not predict. Hours are the member's own estimate, and handing work off takes time before it saves any"}


def cmd_maturity(a):
    d = load(a)
    fix, _ = checks(d, find_business_file(a))
    fns = d["functions"]
    covered = sum(1 for f in fns if any(p["function"] == f["key"] for p in d["positions"]))
    now = day(a)
    weeks = {parse_date(r["date"]).isocalendar()[:2] for r in d["reviews"] if (now - parse_date(r["date"])).days <= 60}
    handed_ok = []
    for h in d["handed"]:
        p = next((p for p in d["positions"] if p["id"] == h["position"]), None)
        if p and not is_owner(p.get("held_by")):
            ids = {k["id"] for k in d["kpis"] if k["position"] == p["id"]}
            if sum(1 for r in d["reviews"] if r["kpi"] in ids and r["date"] >= h["date"]) >= 4:
                handed_ok.append(p["id"])
    if not fns or covered * 2 < len(fns):
        level, nxt = 1, "list the functions and add a position for each, even where the owner holds it"
    elif fix:
        level, nxt = 2, "clear what `check` lists under fix"
    elif len(weeks) < 4:
        level, nxt = 3, "review the numbers on a rhythm: four different weeks of `review` in sixty days"
    elif not handed_ok:
        level, nxt = 4, "hand one position to someone else (position hold) and review its numbers four times"
    else:
        level, nxt = 5, "repeat with the next position on the hand-off list"
    names = {1: "In the owner's head", 2: "Partly written down", 3: "Defined", 4: "Managed", 5: "Runs without the owner in that role"}
    return {"ok": True, "level": level, "name": names[level], "next": nxt,
            "evidence": {"functions": len(fns), "functions_with_a_position": covered, "check_fixes": len(fix),
                         "weeks_reviewed_in_60_days": len(weeks), "positions_handed_off_and_reviewed": handed_ok},
            "note": "a five-step read made for Build Room OS from what is on file here. It is not an industry standard or a score of the business"}


def cmd_review(a):
    d = load(a)
    k = next((k for k in d["kpis"] if k["id"].lower() == str(a.kpi).lower()), None)
    if not k:
        refuse(f"no KPI {a.kpi}; blueprint.py kpi list")
    breach = (k.get("trigger_below") is not None and a.value < k["trigger_below"]) or \
             (k.get("trigger_above") is not None and a.value > k["trigger_above"])
    cause = a.cause or ""
    if cause and cause not in CAUSES:
        refuse(f"--cause is one of {', '.join(CAUSES)}")
    if cause == "person" and words(a.ruled_out or "") < 8:
        refuse("before a result is put down to a person, say what was ruled out (--ruled-out): that the number is right, the target fair, "
               "the procedure workable, the training done and the time and tools there. Most misses are one of those")
    d["reviews"].append({"date": str(day(a)), "kpi": k["id"], "value": a.value, "breach": breach, "cause": cause,
                         "ruled_out": clean("ruled-out", a.ruled_out, need=False), "note": clean("note", a.note, need=False)})
    save(a, d)
    out = {"ok": True, "kpi": k["id"], "name": k["name"], "value": a.value, "trigger_crossed": breach}
    if k.get("target") is not None:
        out["against_target"] = f"{a.value:g} against a target of {k['target']:g} ({'higher' if k['direction'] == 'up' else 'lower'} is better)"
    if breach and not cause:
        out["look_into_it"] = ["Is the number right? Check the source and the definition.", "Is the target or trigger fair for this period?",
                               "Did the procedure work as written, or is the procedure the problem?",
                               "Was the person trained on it, and shown how?", "Did they have the time, tools and information?",
                               "Only then: is it the person? That is a conversation, never a score."]
        out["next"] = "record what it was: blueprint.py review … --cause …"
    out["note"] = "one number is a prompt for a conversation. No decision about a person's job is made from this file"
    return out


def md_list(xs, empty="_none recorded_"):
    return [f"- {x}" for x in xs] or [empty]


def cmd_render(a):
    d = load(a)
    fix, watch = checks(d, find_business_file(a))
    if not d["positions"]:
        refuse("no positions to render yet")
    f = folder(a)
    by_id = {p["id"]: p for p in d["positions"]}
    fn_name = {x["key"]: x["name"] for x in d["functions"]}
    top = next((p for p in d["positions"] if not p.get("reports_to")), d["positions"][0])
    tree = []

    def walk(p, depth, seen):
        if p["id"] in seen:
            return
        seen.add(p["id"])
        tree.append(f"{'  ' * depth}- **{p['title']}** ({p['id']}) · {fn_name.get(p['function'], p['function'])} · held by {p['held_by']}")
        for q in d["positions"]:
            if q.get("reports_to") == p["id"]:
                walk(q, depth + 1, seen)
    seen = set()
    walk(top, 0, seen)
    for p in d["positions"]:
        walk(p, 0, seen)
    mer = ["```mermaid", "graph TD"] + [f"  {p['id'].replace('-', '')}[\"{p['title']}<br/>{p['held_by']}\"]" for p in d["positions"]] + \
          [f"  {p['reports_to'].replace('-', '')} --> {p['id'].replace('-', '')}" for p in d["positions"] if p.get("reports_to") in by_id] + ["```"]
    chart = ["# Accountability chart", "", f"Updated {day(a)}. A position is a seat, not a person: one person can hold several.", ""] + tree + [""] + mer + \
            ["", "## Functions", ""] + [f"- **{x['name']}**: covered today by {x['covered_by']}" for x in d["functions"]] + [""]
    write_atomic(f / "org-chart.md", "\n".join(chart))
    files = ["org-chart.md"]
    for p in d["positions"]:
        ks = [k for k in d["kpis"] if k["position"] == p["id"]]
        boss = by_id.get(p.get("reports_to"), {}).get("title", "nobody: this is the top position")
        reports = [q["title"] for q in d["positions"] if q.get("reports_to") == p["id"]]
        md = [f"# Position contract: {p['title']}", "",
              f"**Position:** {p['id']} · **Function:** {fn_name.get(p['function'], p['function'])} · **Reports to:** {boss} · "
              f"**Direct reports:** {', '.join(reports) or 'none'}",
              f"**Held by:** {p['held_by']} · **Version:** {p.get('version', 1)} · **Written:** {p.get('added', '')} · **Reviewed:** {p['review']}", "",
              "> This is an operating agreement about a role: what it is for and how anyone would know it is going well. It is not an "
              "employment contract. Pay, hours, classification and anything about ending employment belong in documents reviewed by an "
              "HR or legal adviser where the person works.", "",
              "## Why this position exists", "", p["mission"], "", "## What it is accountable for", ""] + md_list(p["accountabilities"]) + \
             ["", "## How it is measured", ""]
        if ks:
            md += ["| Measure | How it is worked out | Where the number comes from | How often | Baseline | Target | Looked into when |", "|---|---|---|---|---|---|---|"]
            for k in ks:
                base = f"{k['baseline']:g} ({k['baseline_basis']})" if k.get("baseline") is not None else "not measured yet"
                tgt = f"{k['target']:g} ({k['target_basis']})" if k.get("target") is not None else "not set"
                trig = (f"below {k['trigger_below']:g}" if k.get("trigger_below") is not None else
                        f"above {k['trigger_above']:g}" if k.get("trigger_above") is not None else "not set")
                md.append(f"| {k['name']} ({k['id']}) | {k['formula']} | {k['source']} | each {k['period']} | {base} | {tgt} | {trig} |")
        else:
            md.append("_No measure yet._")
        md += ["", "## The rhythm of the work", ""]
        for label in ("daily", "weekly", "monthly"):
            if p.get(label):
                md += [f"**{label.capitalize()}**"] + md_list(p[label]) + [""]
        if not any(p.get(x) for x in ("daily", "weekly", "monthly")):
            md += ["_Not recorded yet._", ""]
        md += ["## What it may decide alone", ""] + md_list(p["may"]) + ["", "## What needs approval first", ""] + md_list(p["needs_approval"]) + \
              ["", "## Procedures it runs", ""] + md_list(p.get("sops", []), "_None linked yet. Until there is one, this work cannot be taught._") + \
              ["", "## Hand-offs", "", "**Receives from**"] + md_list(p.get("gets_from", [])) + ["", "**Passes on to**"] + md_list(p.get("gives_to", [])) + \
              ["", "## Making it better", "",
               "When a procedure does not work as written, the holder says so to the person they report to, with what happened and what "
               "they would change. The procedure is fixed; the workaround is not kept quiet.", "",
               "## Read and understood", "", "Holder: ____________________  Date: __________", "",
               "Reports to: ____________________  Date: __________", ""]
        name = re.sub(r"[^a-z0-9]+", "-", p["title"].lower()).strip("-") or p["id"].lower()
        write_atomic(f / "positions" / f"{p['id'].lower()}-{name}.md", "\n".join(md))
        files.append(f"positions/{p['id'].lower()}-{name}.md")
    kd = ["# KPI definitions", "", "One definition per measure, so two people working it out get the same number.", ""]
    for k in d["kpis"]:
        kd += [f"## {k['id']}: {k['name']}", "", f"- **Belongs to:** {by_id.get(k['position'], {}).get('title', k['position'])}",
               f"- **Why it matters:** {k['purpose']}", f"- **Kind:** {k['kind']}", f"- **How it is worked out:** {k['formula']}"]
        if k.get("numerator"):
            kd += [f"- **Counted on top:** {k['numerator']}", f"- **Counted underneath:** {k['denominator']}"]
        kd += [f"- **Source:** {k['source']}", f"- **Period:** {k['period']}",
               "- **Baseline:** " + (f"{k['baseline']:g}, {k['baseline_basis']}" if k.get("baseline") is not None else "not measured yet"),
               "- **Target:** " + (f"{k['target']:g} ({k['target_basis']}; {'higher' if k['direction'] == 'up' else 'lower'} is better)"
                                   if k.get("target") is not None else "not set"),
               "- **Related procedures:** " + (", ".join(k.get("sops") or []) or "none linked"), ""]
    write_atomic(f / "kpis.md", "\n".join(kd))
    last = {}
    for r in d["reviews"]:
        last[r["kpi"]] = r
    sc = ["# Scorecard", "", f"As of {day(a)}. The latest number the member recorded for each measure.", "",
          "| Position | Measure | Latest | On | Target | Looked into? |", "|---|---|---|---|---|---|"]
    for k in d["kpis"]:
        r = last.get(k["id"])
        looked = ("yes: " + (r["cause"] or "cause not recorded yet")) if r and r.get("breach") else "no"
        sc.append(" | ".join(["| " + by_id.get(k["position"], {}).get("title", k["position"]), k["name"],
                              f"{r['value']:g}" if r else "not recorded", r["date"] if r else "",
                              f"{k['target']:g}" if k.get("target") is not None else "not set", looked + " |"]))
    write_atomic(f / "scorecard.md", "\n".join(sc) + "\n")
    return {"ok": True, "written": files + ["kpis.md", "scorecard.md"], "folder": str(f), "check": "GO" if not fix else "FIX",
            "fix": fix, "watch": watch,
            "note": "drafts for the member to read and change. A position contract is not an employment contract"}


def cmd_report(a):
    d = load(a)
    fix, watch = checks(d, find_business_file(a))
    held = [p for p in d["positions"] if is_owner(p.get("held_by"))]
    crossed = [r for r in d["reviews"] if r.get("breach") and not r.get("cause")]
    return {"ok": True, "date": str(day(a)),
            "counts": {"functions": len(d["functions"]), "positions": len(d["positions"]), "held_by_the_owner": len(held),
                       "handed_off": len(d["handed"]), "kpis": len(d["kpis"]),
                       "kpis_not_measured_yet": sum(1 for k in d["kpis"] if k.get("baseline") is None), "reviews": len(d["reviews"])},
            "check": "GO" if not fix else "FIX", "fix": fix[:6], "watch": watch[:6],
            "to_look_into": [f"{r['kpi']} on {r['date']}: {r['value']:g}" for r in crossed][:6],
            "note": "counts of what is on file. Nothing here is a forecast"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--folder"); x.add_argument("--today"); x.add_argument("--business-file")
        return x
    for n in ("init", "prefill", "check", "handoff", "maturity", "render", "report"):
        p(n)
    x = p("aim"); x.add_argument("--key", required=True); x.add_argument("--text"); x.add_argument("--text-file")
    x.add_argument("--from"); x.add_argument("--draft", action="store_true")
    x = p("confirm"); x.add_argument("--keys"); x.add_argument("--all", action="store_true"); x.add_argument("--by", required=True)
    x = p("function"); x.add_argument("action", choices=["add", "list", "remove"]); x.add_argument("--key"); x.add_argument("--name")
    x.add_argument("--covered-by"); x.add_argument("--hours", type=finite); x.add_argument("--only-owner", type=int)
    x.add_argument("--documented", type=int); x.add_argument("--note")
    x = p("position"); x.add_argument("action", choices=["add", "list", "remove", "hold"]); x.add_argument("--id")
    for flag in ("title", "function", "reports-to", "held-by", "mission"):
        x.add_argument("--" + flag)
    for flag in ("accountability", "may", "needs-approval", "sop", "gets-from", "gives-to", "daily", "weekly", "monthly"):
        x.add_argument("--" + flag, action="append")
    x.add_argument("--review", choices=["weekly", "monthly", "quarterly"])
    x = p("kpi"); x.add_argument("action", choices=["add", "list", "remove"]); x.add_argument("--id"); x.add_argument("--position")
    for flag in ("name", "purpose", "kind", "formula", "numerator", "denominator", "source", "period", "baseline-basis", "target-basis", "direction"):
        x.add_argument("--" + flag)
    for flag in ("baseline", "target", "trigger-below", "trigger-above"):
        x.add_argument("--" + flag, type=finite)
    x.add_argument("--sop", action="append")
    x = p("review"); x.add_argument("--kpi", required=True); x.add_argument("--value", type=finite, required=True)
    x.add_argument("--cause"); x.add_argument("--ruled-out"); x.add_argument("--note")
    a = ap.parse_args()
    try:
        out = globals()["cmd_" + a.cmd](a)
    except (KeyError, AttributeError, TypeError, IndexError) as e:
        refuse(f"blueprint.json is missing something the tool wrote ({type(e).__name__}: {e}); it was probably edited by hand. "
               "Restore it from a backup, or fix that entry")
    emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
