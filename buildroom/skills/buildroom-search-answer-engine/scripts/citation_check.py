#!/usr/bin/env python3
"""Monthly citation check for the Search & Answer Engine.

Builds the month's prompt list (customer-style questions plus "best X in [city]" style asks),
records what each engine answered when the member ran the prompt logged out, and reports the
share of prompts where the business was cited or named, by engine, against last month.

Stdlib only. Run from the folder that holds the Business File (or the vault root):

  python3 citation_check.py plan --business "Ruiz Advisory" --category "bookkeeper" --city "Boise" [--audience "small construction firms"] [--n 12] [--month 2026-11]
  python3 citation_check.py log P-03 --engine chatgpt --result own --url https://example.com/answers/x [--variant b] [--run 2] [--competitor "Acme Books"] [--month 2026-11]
  python3 citation_check.py report [--month 2026-11] [--md]
  python3 citation_check.py prompts [--month 2026-11]      # the checklist to run, as markdown

Engines: google-ai (AI Overview or AI Mode), chatgpt, perplexity, gemini, copilot.
Results: own (the website cited or linked) · profile (the Business Profile or Maps listing shown) ·
named (the business named, no link) · directory (a directory page about the business cited) ·
competitor (another business shown, not this one) · none (no business shown, or an answer that named nobody).

Each prompt has two wordings (a and b). Answers vary run to run, so a prompt can be logged more
than once per engine (--run 1, 2, 3); the report counts a prompt as "seen" when any run showed the
business, and reports consistency as the share of runs that did.

Exit code 0 on success, 2 on a usage or data error.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True

ENGINES = ("google-ai", "chatgpt", "perplexity", "gemini", "copilot")
RESULTS = ("own", "profile", "named", "directory", "competitor", "none")
SEEN = ("own", "profile", "named", "directory")
DEFAULT_N = 12


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


def load_questions(folder):
    p = Path(folder) / "questions.json"
    if not p.exists():
        return []
    try:
        qs = json.loads(p.read_text(encoding="utf-8")).get("questions", [])
    except json.JSONDecodeError:
        return []
    order = {"published": 0, "ready": 1, "drafting": 2, "queued": 3}
    return sorted([q for q in qs if q.get("status") in order], key=lambda q: (order[q["status"]], q.get("id", "")))


def paraphrase(q):
    """A second wording a real customer might type. Simple, deterministic rewrites."""
    t = q.strip().rstrip("?")
    low = t.lower()
    if low.startswith("how much does"):
        return "What's the typical price for" + t[len("How much does"):].replace(" cost", "") + "?"
    if low.startswith("how do i"):
        return "What's the best way to" + t[len("How do I"):] + "?"
    if low.startswith("what is"):
        return "Can you explain" + t[len("What is"):] + " in plain terms?"
    if low.startswith("should i"):
        return "Is it worth it to" + t[len("Should I"):] + "?"
    if low.startswith("why"):
        return "What's the reason" + t[3:] + "?"
    if low.startswith("can "):
        return "Is it possible that" + t[3:] + "?"
    return "I'm trying to work out: " + t[0].lower() + t[1:] + ". What should I know?"


def category_prompts(business, category, city, audience):
    cat = category.strip().lower()
    out = []
    if city:
        out += [
            ("category", f"Who is a good {cat} in {city}?", f"Best {cat} near {city}: who would you recommend?"),
            ("category", f"How do I choose a {cat} in {city}?", f"What should I look for when hiring a {cat} in {city}?"),
            ("category", f"How much does a {cat} cost in {city}?", f"Typical {cat} prices around {city}?"),
        ]
    if audience:
        out += [("category", f"Who is the best {cat} for {audience}?", f"Recommend a {cat} that works with {audience}.")]
    else:
        out += [("category", f"Who is a good {cat} for a small business?", f"Recommend a {cat} for a small business owner.")]
    out += [("brand", f"Is {business} any good?", f"{business} reviews: what do people say?"),
            ("brand", f"What does {business} do?", f"Tell me about {business}.")]
    return out


def cmd_plan(a):
    month = a.month or this_month()
    p = month_path(a.folder, month)
    if p.exists() and not a.force:
        die(f"{p} already exists for {month} (use --force to rebuild; logged results would be lost)")
    prompts = []
    for kind, text, alt in category_prompts(a.business, a.category, a.city, a.audience):
        prompts.append({"kind": kind, "a": text, "b": alt})
    for q in load_questions(a.folder):
        prompts.append({"kind": "question", "a": q["question"], "b": paraphrase(q["question"]), "question_id": q.get("id", ""), "status": q.get("status", "")})
        if len(prompts) >= a.n:
            break
    if len(prompts) < a.n:
        extra = category_prompts(a.business, a.category, a.city, a.audience)
        for kind, text, alt in extra[len(prompts):]:
            prompts.append({"kind": kind, "a": text, "b": alt})
    prompts = prompts[: a.n]
    for i, pr in enumerate(prompts, 1):
        pr["id"] = f"P-{i:02d}"
    data = {"month": month, "business": a.business, "category": a.category, "city": a.city, "audience": a.audience,
            "engines": list(ENGINES), "prompts": prompts, "results": [], "created": date.today().isoformat()}
    save(data, p)
    print(json.dumps({"ok": True, "month": month, "file": str(p), "prompts": len(prompts),
                      "how": "Log out of every account (or use a private window). For each prompt, run wording a, then b, on each engine. "
                             "Log what you saw with `log`. Two runs on different days catch the variation; three is better."},
                     indent=2, ensure_ascii=False))


def cmd_prompts(a):
    month = a.month or this_month()
    data, _ = load_month(a.folder, month)
    lines = [f"# Citation check · {data['business']} · {month}", "",
             "Logged out, private window. For each line: run wording **a**, then **b**, on each engine. Note: own site cited · profile shown · "
             "named only · a directory page · a competitor · nobody. Log each with `citation_check.py log P-NN --engine … --result …`.", "",
             "| ID | Kind | Wording a | Wording b | " + " | ".join(ENGINES) + " |", "|---|---|---|---|" + "---|" * len(ENGINES)]
    for pr in data["prompts"]:
        lines.append(f"| {pr['id']} | {pr['kind']} | {pr['a']} | {pr['b']} | " + " | ".join("" for _ in ENGINES) + " |")
    lines += ["", "Engines: google-ai = the AI Overview or AI Mode on Google (also note whether the Business Profile appears in the local pack) · "
              "chatgpt · perplexity · gemini · copilot.", ""]
    out = Path(a.folder) / "checks" / f"{month}-prompts.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(out)}, indent=2))


def cmd_log(a):
    month = a.month or this_month()
    data, p = load_month(a.folder, month)
    if a.engine not in ENGINES:
        die(f"--engine must be one of {', '.join(ENGINES)}")
    if a.result not in RESULTS:
        die(f"--result must be one of {', '.join(RESULTS)}")
    if not any(pr["id"] == a.prompt for pr in data["prompts"]):
        die(f"{a.prompt} is not in this month's plan")
    if a.variant not in ("a", "b"):
        die("--variant must be a or b")
    entry = {"prompt": a.prompt, "variant": a.variant, "run": a.run, "engine": a.engine, "result": a.result,
             "url": a.url or "", "competitor": a.competitor or "", "note": a.note or "", "date": a.date or date.today().isoformat()}
    data["results"] = [r for r in data["results"] if not (r["prompt"] == a.prompt and r["variant"] == a.variant and r["run"] == a.run and r["engine"] == a.engine)]
    data["results"].append(entry)
    save(data, p)
    print(json.dumps({"ok": True, "logged": entry, "results_so_far": len(data["results"])}, indent=2, ensure_ascii=False))


def summarise(data):
    prompts = {pr["id"]: pr for pr in data["prompts"]}
    by_engine = {}
    for e in ENGINES:
        rs = [r for r in data["results"] if r["engine"] == e]
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
    tried_all = {r["prompt"] for r in data["results"]}
    seen_all = {r["prompt"] for r in data["results"] if r["result"] in SEEN}
    never = sorted(pid for pid in tried_all if pid not in seen_all)
    return {"month": data["month"], "prompts": len(prompts), "prompts_tried": len(tried_all), "prompts_seen": len(seen_all),
            "share_seen": round(len(seen_all) / len(tried_all), 2) if tried_all else None, "by_engine": by_engine, "by_kind": by_kind,
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
        rep["previous"] = {"month": ps["month"], "share_seen": ps["share_seen"],
                           "by_engine": {e: ps["by_engine"][e]["share_seen"] for e in ENGINES}}
        if rep["share_seen"] is not None and ps["share_seen"] is not None:
            rep["change"] = round(rep["share_seen"] - ps["share_seen"], 2)
    rep["reading"] = ("Answers vary run to run; a prompt counts as seen if any run showed you, and consistency says how often. "
                      "Judge the trend over three months, not one. Category prompts are the ones that bring strangers; "
                      "brand prompts should always find you; question prompts test the answer pages.")
    if a.md:
        share = "" if rep["share_seen"] is None else f"{rep['share_seen']:.0%}"
        prev_share = ""
        if rep.get("previous") and rep["previous"]["share_seen"] is not None:
            prev_share = f" · last month {rep['previous']['share_seen']:.0%}"
        lines = [f"# Citation check · {data['business']} · {month}", "",
                 f"Prompts tried: {rep['prompts_tried']} of {rep['prompts']} · Seen in {rep['prompts_seen']} ({share}){prev_share}", "",
                 "| Engine | Tried | Seen | Share | Consistency | Own site | Profile | Named | Directory | Competitor only | Nobody |",
                 "|---|---|---|---|---|---|---|---|---|---|---|"]
        for e in ENGINES:
            b = rep["by_engine"][e]
            sh = "" if b["share_seen"] is None else f"{b['share_seen']:.0%}"
            co = "" if b["consistency"] is None else f"{b['consistency']:.0%}"
            lines.append(f"| {e} | {b['prompts_tried']} | {b['prompts_seen']} | {sh} | {co} | {b['own_site']} | {b['profile']} | {b['named']} | {b['directory']} | {b['competitor_only']} | {b['nobody']} |")
        lines += ["", "| Kind | Prompts | Tried | Seen |", "|---|---|---|---|"]
        for k, v in rep["by_kind"].items():
            lines.append(f"| {k} | {v['prompts']} | {v['tried']} | {v['seen']} |")
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
    s = sub.add_parser("plan"); s.add_argument("--business", required=True); s.add_argument("--category", required=True)
    s.add_argument("--city", default=""); s.add_argument("--audience", default=""); s.add_argument("--n", type=int, default=DEFAULT_N)
    s.add_argument("--month", default=""); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_plan)
    s = sub.add_parser("prompts"); s.add_argument("--month", default=""); s.set_defaults(f=cmd_prompts)
    s = sub.add_parser("log"); s.add_argument("prompt"); s.add_argument("--engine", required=True); s.add_argument("--result", required=True)
    s.add_argument("--variant", default="a"); s.add_argument("--run", type=int, default=1); s.add_argument("--url", default="")
    s.add_argument("--competitor", default=""); s.add_argument("--note", default=""); s.add_argument("--date", default=""); s.add_argument("--month", default=""); s.set_defaults(f=cmd_log)
    s = sub.add_parser("report"); s.add_argument("--month", default=""); s.add_argument("--md", action="store_true"); s.set_defaults(f=cmd_report)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
