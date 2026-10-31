#!/usr/bin/env python3
"""Monthly citation check for the Search & Answer Engine.

Builds the month's prompt list (customer-style questions plus "who is a good X" asks), records what
each engine answered when the member ran the prompt logged out, and reports the share of prompts
where the business was cited or named, by engine, against last month.

Sized for an owner with an afternoon a month, not an agency: ten prompts, two wordings, three
engines (Google's AI, ChatGPT, Perplexity) by default, two runs on different days. `--all-engines`
adds Gemini and Copilot (worth a quarterly look). Stdlib only. Run from the folder that holds the
Business File; `--folder` may go before or after the command.

  python3 citation_check.py plan --business "Ruiz Advisory" --category "bookkeeper" [--city "Boise"] [--audience "small construction firms"] [--n 10] [--all-engines] [--month 2026-11]
  python3 citation_check.py prompts [--month 2026-11]                       # the checklist to run and fill in, as markdown
  python3 citation_check.py reword P-03 --b "What's a fair price for a clean-up?"   # replace a wording the member would not type
  python3 citation_check.py log P-03 --engine chatgpt --result own [--url …] [--variant b] [--run 2] [--competitor "Acme Books"]
  python3 citation_check.py log --from search/checks/2026-11-prompts.md    # read the filled-in checklist instead of one log per cell
  python3 citation_check.py report [--month 2026-11] [--md]

Engines: google-ai (the AI Overview or AI Mode on Google), chatgpt, perplexity, gemini, copilot.
Results: own (the website cited or linked) · profile (the Business Profile or Maps listing shown) ·
named (the business named, no link) · directory (a directory page about the business cited) ·
competitor (another business shown, not this one) · none (no business shown, or nobody named).

In the checklist, a cell holds the result for wording a, or `a/b` for both (e.g. `profile/none`);
a second run goes in a second copy of the row or a second `--run`. Answers vary run to run, so a
prompt counts as "seen" when any run showed the business; consistency is the share of runs that did.
The headline share counts category and question prompts only; brand prompts (which should always
find you) are reported separately.

Exit code 0 on success, 2 on a usage or data error.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True

ALL_ENGINES = ("google-ai", "chatgpt", "perplexity", "gemini", "copilot")
DEFAULT_ENGINES = ("google-ai", "chatgpt", "perplexity")
RESULTS = ("own", "profile", "named", "directory", "competitor", "none")
SEEN = ("own", "profile", "named", "directory")
DEFAULT_N = 10
WEIGHTS = {"demand": 0.25, "value": 0.25, "gap": 0.20, "answerable": 0.20, "fresh": 0.10}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def this_month():
    return date.today().strftime("%Y-%m")


def prev_month(m):
    y, mm = int(m[:4]), int(m[5:7])
    return f"{y - 1}-12" if mm == 1 else f"{y}-{mm - 1:02d}"


def month_path(folder, month):
    return Path(folder) / "checks" / f"{month}.json"


def load_month(folder, month, must=True):
    p = month_path(folder, month)
    if not p.exists():
        if must:
            die(f"{p} not found; run `plan --month {month}` first")
        return None, p
    try:
        return json.loads(p.read_text(encoding="utf-8")), p
    except json.JSONDecodeError as e:
        die(f"{p} is not valid JSON: {e}")


def save(data, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = date.today().isoformat()
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def qscore(q):
    s = q.get("scores") or {}
    return sum(float(s.get(k, 0)) * w for k, w in WEIGHTS.items())


def load_questions(folder):
    p = Path(folder) / "questions.json"
    if not p.exists():
        return []
    try:
        qs = json.loads(p.read_text(encoding="utf-8")).get("questions", [])
    except json.JSONDecodeError:
        return []
    order = {"published": 0, "ready": 1, "drafting": 2, "queued": 3}
    return sorted([q for q in qs if q.get("status") in order], key=lambda q: (order[q["status"]], -qscore(q), q.get("id", "")))


def an(word):
    return ("an " if word[:1].lower() in "aeiou" else "a ") + word


def paraphrase(q):
    """A second wording a real customer might type."""
    t = q.strip().rstrip("?").strip()
    low = t.lower()
    m = re.match(r"how much does it cost to (.+)", low)
    if m:
        return "What's the typical price to " + t[len("How much does it cost to "):] + "?"
    m = re.match(r"how much does (.+?) cost(.*)", low)
    if m:
        rest = t[len("How much does "):]
        subj = rest[: len(m.group(1))]
        tail = rest[len(m.group(1)) + len(" cost"):]
        return "What's the typical price for " + subj + tail + "?"
    m = re.match(r"how much (?:is|are) (.+)", low)
    if m:
        return "What does " + t[len("How much is "):] + " usually cost?"
    if low.startswith("how do i "):
        return "What's the best way to " + t[len("How do I "):] + "?"
    if low.startswith("how long does "):
        return "What's the usual time for " + t[len("How long does "):].replace(" take", "") + "?"
    if low.startswith("what is "):
        return "Can you explain " + t[len("What is "):] + " in plain terms?"
    if low.startswith("should i "):
        return "Is it worth it to " + t[len("Should I "):] + "?"
    m = re.match(r"why (?:does|do|is|are|did) (.+)", low)
    if m:
        return "What's the reason " + t[len(t) - len(m.group(1)):] + "?"
    if low.startswith("can "):
        return "Is it possible that " + t[4:] + "?"
    m = re.match(r"(.+?) vs\.? (.+?)(?::| -|,)\s*(.*)", t, re.I)
    if m:
        return f"{m.group(1)} or {m.group(2)}: which do I need?"
    if " vs " in low:
        a, b = re.split(r"\s+vs\.?\s+", t, maxsplit=1, flags=re.I)
        return f"{a} or {b}: which do I need?"
    return "I'm trying to work out: " + t[0].lower() + t[1:] + ". What should I know?"


def category_prompts(business, category, city, audience):
    cat = category.strip().lower()
    where = f" in {city}" if city else ""
    near = f" near {city}" if city else ""
    out = [
        ("category", f"Who is a good {cat}{where}?", f"Best {cat}{near}: who would you recommend?"),
        ("category", f"How do I choose {an(cat)}{where}?", f"What should I look for when hiring {an(cat)}{where}?"),
        ("category", f"How much does {an(cat)} cost{where}?", f"Typical {cat} prices{where}?"),
    ]
    if audience:
        out.append(("category", f"Who is the best {cat} for {audience}?", f"Recommend {an(cat)} that works with {audience}."))
    else:
        out.append(("category", f"Who is a good {cat} for a small business?", f"Recommend {an(cat)} for a small business owner."))
    if not city:
        out.append(("category", f"Who is a good {cat} that works remotely?", f"Recommend an online {cat}."))
    out += [("brand", f"Is {business} any good?", f"{business} reviews: what do people say?"),
            ("brand", f"What does {business} do?", f"Tell me about {business}.")]
    return out


def cmd_plan(a):
    month = a.month or this_month()
    p = month_path(a.folder, month)
    if p.exists() and not a.force:
        die(f"{p} already exists for {month} (use --force to rebuild; logged results would be lost)")
    cats = category_prompts(a.business, a.category, a.city, a.audience)
    brand = [c for c in cats if c[0] == "brand"]
    cats = [c for c in cats if c[0] == "category"]
    prompts = [{"kind": k, "a": t, "b": alt} for k, t, alt in cats]
    for q in load_questions(a.folder):
        if len(prompts) >= a.n:
            break
        prompts.append({"kind": "question", "a": q["question"], "b": paraphrase(q["question"]), "question_id": q.get("id", ""),
                        "status": q.get("status", ""), "score": round(qscore(q), 1)})
    prompts += [{"kind": k, "a": t, "b": alt} for k, t, alt in brand]
    for i, pr in enumerate(prompts, 1):
        pr["id"] = f"P-{i:02d}"
    engines = list(ALL_ENGINES) if a.all_engines else list(DEFAULT_ENGINES)
    data = {"month": month, "business": a.business, "category": a.category, "city": a.city, "audience": a.audience,
            "engines": engines, "prompts": prompts, "results": [], "created": date.today().isoformat()}
    save(data, p)
    out = {"ok": True, "month": month, "file": str(p), "prompts": len(prompts), "engines": engines,
           "how": "Log out of every account (or use a private window). Run wording a, then b, on each engine; write what you saw in the checklist "
                  "(`prompts` writes it), then `log --from` it. Two runs on different days catch the variation."}
    if len(prompts) - len(brand) < 8:
        out["warning"] = f"only {len(prompts) - len(brand)} customer prompts; add questions to the map (`question_map.py add`) and rebuild with --force"
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_prompts(a):
    month = a.month or this_month()
    data, _ = load_month(a.folder, month)
    engines = data.get("engines", list(DEFAULT_ENGINES))
    lines = [f"# Citation check · {data['business']} · {month}", "",
             "Logged out, private window. For each line: run wording **a**, then **b**, on each engine. In each engine's cell write what you saw: "
             "`own` (your website cited) · `profile` (your Business Profile or Maps listing) · `named` (named, no link) · `directory` (a directory page about you) · "
             "`competitor` (someone else) · `none` (nobody). One word is for wording a; `a/b` gives both, e.g. `profile/none`. "
             "Then `citation_check.py log --from` this file.", "",
             "| ID | Kind | Wording a | Wording b | " + " | ".join(engines) + " |", "|---|---|---|---|" + "---|" * len(engines)]
    for pr in data["prompts"]:
        lines.append(f"| {pr['id']} | {pr['kind']} | {pr['a']} | {pr['b']} | " + " | ".join("" for _ in engines) + " |")
    lines += ["", "google-ai = the AI Overview or AI Mode on Google (note too whether your profile shows in the local pack) · chatgpt · perplexity"
              + (" · gemini · copilot" if len(engines) > 3 else " (gemini and copilot: quarterly, `plan --all-engines`)") + ".", ""]
    out = Path(a.folder) / "checks" / f"{month}-prompts.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(out)}, indent=2))


def cmd_reword(a):
    month = a.month or this_month()
    data, p = load_month(a.folder, month)
    pr = next((x for x in data["prompts"] if x["id"] == a.prompt), None)
    if not pr:
        die(f"{a.prompt} is not in this month's plan")
    if a.a:
        pr["a"] = a.a
    if a.b:
        pr["b"] = a.b
    save(data, p)
    print(json.dumps({"ok": True, "prompt": pr}, indent=2, ensure_ascii=False))


def add_result(data, prompt, engine, result, variant="a", run=1, url="", competitor="", note="", when=""):
    if engine not in ALL_ENGINES:
        die(f"engine must be one of {', '.join(ALL_ENGINES)}")
    if result not in RESULTS:
        die(f"result must be one of {', '.join(RESULTS)}")
    if not any(pr["id"] == prompt for pr in data["prompts"]):
        die(f"{prompt} is not in this month's plan")
    if variant not in ("a", "b"):
        die("variant must be a or b")
    if run < 1:
        die("run must be 1 or more")
    entry = {"prompt": prompt, "variant": variant, "run": run, "engine": engine, "result": result,
             "url": url or "", "competitor": competitor or "", "note": note or "", "date": when or date.today().isoformat()}
    data["results"] = [r for r in data["results"] if not (r["prompt"] == prompt and r["variant"] == variant and r["run"] == run and r["engine"] == engine)]
    data["results"].append(entry)
    return entry


def cmd_log(a):
    month = a.month or this_month()
    data, p = load_month(a.folder, month)
    if a.date:
        try:
            date.fromisoformat(a.date)
        except ValueError:
            die("--date must be YYYY-MM-DD")
    if a.from_file:
        src = Path(a.from_file)
        if not src.exists():
            die(f"{src} not found")
        engines, added, problems, seen_rows = [], 0, [], {}
        for line in src.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] == "ID":
                engines = cells[4:]
                continue
            if not cells or not re.fullmatch(r"P-\d+", cells[0]) or not engines:
                continue
            pid = cells[0]
            seen_rows[pid] = seen_rows.get(pid, 0) + 1
            run = a.run if seen_rows[pid] == 1 else a.run + seen_rows[pid] - 1
            for eng, cell in zip(engines, cells[4:]):
                if not cell:
                    continue
                parts = [x.strip().lower() for x in cell.split("/")]
                for variant, res in zip(("a", "b"), parts):
                    if res not in RESULTS:
                        problems.append(f"{pid} {eng} wording {variant}: '{res}' is not one of {', '.join(RESULTS)}")
                        continue
                    add_result(data, pid, eng, res, variant, run, when=a.date)
                    added += 1
        save(data, p)
        print(json.dumps({"ok": not problems, "logged": added, "problems": problems, "results_so_far": len(data["results"])}, indent=2, ensure_ascii=False))
        return
    if not a.prompt or not a.engine or not a.result:
        die("log needs a prompt, --engine and --result (or --from FILE)")
    entry = add_result(data, a.prompt, a.engine, a.result, a.variant, a.run, a.url, a.competitor, a.note, a.date)
    save(data, p)
    print(json.dumps({"ok": True, "logged": entry, "results_so_far": len(data["results"])}, indent=2, ensure_ascii=False))


def summarise(data):
    prompts = {pr["id"]: pr for pr in data["prompts"]}
    customer = {pid for pid, pr in prompts.items() if pr["kind"] != "brand"}
    engines = data.get("engines", list(DEFAULT_ENGINES))
    used = sorted({r["engine"] for r in data["results"]} | set(engines), key=lambda e: ALL_ENGINES.index(e))
    by_engine = {}
    for e in used:
        rs = [r for r in data["results"] if r["engine"] == e and r["prompt"] in customer]
        seen_prompts = {r["prompt"] for r in rs if r["result"] in SEEN}
        tried_prompts = {r["prompt"] for r in rs}
        runs_seen = sum(1 for r in rs if r["result"] in SEEN)
        by_engine[e] = {"prompts_tried": len(tried_prompts), "prompts_seen": len(seen_prompts),
                        "share_seen": round(len(seen_prompts) / len(tried_prompts), 2) if tried_prompts else None,
                        "consistency": round(runs_seen / len(rs), 2) if rs else None,
                        "own_site": sum(1 for r in rs if r["result"] == "own"), "profile": sum(1 for r in rs if r["result"] == "profile"),
                        "named": sum(1 for r in rs if r["result"] == "named"), "directory": sum(1 for r in rs if r["result"] == "directory"),
                        "competitor_only": sum(1 for r in rs if r["result"] == "competitor"), "nobody": sum(1 for r in rs if r["result"] == "none")}
    comps = {}
    for r in data["results"]:
        if r.get("competitor"):
            comps[r["competitor"]] = comps.get(r["competitor"], 0) + 1
    by_kind = {}
    for kind in ("category", "question", "brand"):
        ids = {pid for pid, pr in prompts.items() if pr["kind"] == kind}
        rs = [r for r in data["results"] if r["prompt"] in ids]
        tried = {r["prompt"] for r in rs}
        seen = {r["prompt"] for r in rs if r["result"] in SEEN}
        by_kind[kind] = {"prompts": len(ids), "tried": len(tried), "seen": len(seen)}
    tried_all = {r["prompt"] for r in data["results"] if r["prompt"] in customer}
    seen_all = {r["prompt"] for r in data["results"] if r["prompt"] in customer and r["result"] in SEEN}
    brand_ids = {pid for pid in prompts if pid not in customer}
    brand_tried = {r["prompt"] for r in data["results"] if r["prompt"] in brand_ids}
    brand_seen = {r["prompt"] for r in data["results"] if r["prompt"] in brand_ids and r["result"] in SEEN}
    brand_wrong = sorted(brand_tried - brand_seen)
    never = sorted(pid for pid in tried_all if pid not in seen_all)
    return {"month": data["month"], "customer_prompts": len(customer), "prompts_tried": len(tried_all), "prompts_seen": len(seen_all),
            "share_seen": round(len(seen_all) / len(tried_all), 2) if tried_all else None, "by_engine": by_engine, "by_kind": by_kind,
            "brand": {"tried": len(brand_tried), "seen": len(brand_seen), "not_found": brand_wrong},
            "competitors": sorted(comps.items(), key=lambda kv: -kv[1])[:5],
            "never_seen": [{"id": pid, "prompt": prompts[pid]["a"], "kind": prompts[pid]["kind"]} for pid in never],
            "results_logged": len(data["results"])}


def cmd_report(a):
    month = a.month or this_month()
    data, _ = load_month(a.folder, month)
    rep = summarise(data)
    prev, _ = load_month(a.folder, prev_month(month), must=False)
    if prev:
        ps = summarise(prev)
        rep["previous"] = {"month": ps["month"], "share_seen": ps["share_seen"], "by_engine": {e: v["share_seen"] for e, v in ps["by_engine"].items()}}
        if rep["share_seen"] is not None and ps["share_seen"] is not None:
            rep["change"] = round(rep["share_seen"] - ps["share_seen"], 2)
    rep["reading"] = ("The headline share is customer prompts only (category and question); brand prompts should always find you and are listed "
                      "separately so a wrong fact gets fixed at its source. Answers vary run to run; a prompt counts as seen if any run showed you, "
                      "and consistency says how often. Judge the trend over three months, not one. Category prompts bring strangers and move slowest.")
    if a.md:
        share = "" if rep["share_seen"] is None else f"{rep['share_seen']:.0%}"
        prev_share = ""
        if rep.get("previous") and rep["previous"]["share_seen"] is not None:
            prev_share = f" · last month {rep['previous']['share_seen']:.0%}"
        lines = [f"# Citation check · {data['business']} · {month}", "",
                 f"Customer prompts tried: {rep['prompts_tried']} of {rep['customer_prompts']} · Seen in {rep['prompts_seen']} ({share}){prev_share} · "
                 f"Brand prompts found you in {rep['brand']['seen']} of {rep['brand']['tried']}", "",
                 "| Engine | Tried | Seen | Share | Consistency | Own site | Profile | Named | Directory | Competitor only | Nobody |",
                 "|---|---|---|---|---|---|---|---|---|---|---|"]
        for e, b in rep["by_engine"].items():
            sh = "" if b["share_seen"] is None else f"{b['share_seen']:.0%}"
            co = "" if b["consistency"] is None else f"{b['consistency']:.0%}"
            lines.append(f"| {e} | {b['prompts_tried']} | {b['prompts_seen']} | {sh} | {co} | {b['own_site']} | {b['profile']} | {b['named']} | {b['directory']} | {b['competitor_only']} | {b['nobody']} |")
        lines += ["", "| Kind | Prompts | Tried | Seen |", "|---|---|---|---|"]
        for k, v in rep["by_kind"].items():
            lines.append(f"| {k} | {v['prompts']} | {v['tried']} | {v['seen']} |")
        if rep["brand"]["not_found"]:
            lines += ["", "Brand prompts that did not find you (fix the profile, the About page or a listing this week): " + ", ".join(rep["brand"]["not_found"])]
        if rep["competitors"]:
            lines += ["", "Competitors shown most: " + ", ".join(f"{n} ({c})" for n, c in rep["competitors"])]
        if rep["never_seen"]:
            lines += ["", "## Never seen (work these next)", ""] + [f"- {x['id']} ({x['kind']}): {x['prompt']}" for x in rep["never_seen"]]
        lines += ["", rep["reading"], ""]
        out = Path(a.folder) / "checks" / f"{month}-report.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        rep["wrote"] = str(out)
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default="search")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, f):
        s = sub.add_parser(name)
        s.add_argument("--folder", dest="folder_sub", default=None)
        s.add_argument("--month", default="")
        s.set_defaults(f=f)
        return s
    s = sp("plan", cmd_plan); s.add_argument("--business", required=True); s.add_argument("--category", required=True)
    s.add_argument("--city", default=""); s.add_argument("--audience", default=""); s.add_argument("--n", type=int, default=DEFAULT_N)
    s.add_argument("--all-engines", action="store_true"); s.add_argument("--force", action="store_true")
    sp("prompts", cmd_prompts)
    s = sp("reword", cmd_reword); s.add_argument("prompt"); s.add_argument("--a", default=""); s.add_argument("--b", default="")
    s = sp("log", cmd_log); s.add_argument("prompt", nargs="?", default=""); s.add_argument("--engine", default=""); s.add_argument("--result", default="")
    s.add_argument("--variant", default="a"); s.add_argument("--run", type=int, default=1); s.add_argument("--url", default="")
    s.add_argument("--competitor", default=""); s.add_argument("--note", default=""); s.add_argument("--date", default=""); s.add_argument("--from", dest="from_file", default="")
    s = sp("report", cmd_report); s.add_argument("--md", action="store_true")
    a = ap.parse_args(argv)
    if getattr(a, "folder_sub", None):
        a.folder = a.folder_sub
    a.f(a)


if __name__ == "__main__":
    main()
