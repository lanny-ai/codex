#!/usr/bin/env python3
"""Question map for the Search & Answer Engine.

Keeps `search/questions.json` (one record per question a customer asks) and renders
`search/question-map.md`. Scores each question with the founder's weights (demand 25%,
value to the business 25%, citation gap 20%, answerable 20%, freshness 10%), picks the next
one to answer, and records what was published where.

Stdlib only. Run from the folder that holds the Business File (or the vault root). `--folder`
may go before or after the command:

  python3 question_map.py init [--folder search] [--business "Ruiz Advisory"]
  python3 question_map.py add "How much does X cost?" --intent cost --cluster pricing --source "sales calls" --rate 4,5,3,5,2
  python3 question_map.py add "Bookkeeping clean-up" --intent service --cluster clean-up      # one page per service
  python3 question_map.py import questions.txt [--source "Search Console"]
  python3 question_map.py score [--top 10]
  python3 question_map.py next [--intent cost]
  python3 question_map.py set Q-03 --status published --url https://example.com/answers/x
  python3 question_map.py list [--status queued]
  python3 question_map.py md

`--rate d,v,g,a,f` takes five marks from 1 to 5 (demand, value to the business, citation gap,
answerable from the member's own experience or good sources, freshness). 1 = 20, 5 = 100.
`next` picks the service page first when none is published, then the highest score; the member
is in the loop on every page, so there is no fixed page-type order.
Exit code 0 on success, 1 when `next` finds nothing eligible, 2 on a usage or data error.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True

WEIGHTS = {"demand": 0.25, "value": 0.25, "gap": 0.20, "answerable": 0.20, "fresh": 0.10}
INTENTS = ("service", "definition", "how-to", "cost", "compare", "objection", "local", "diagnostic", "other")
STATUSES = ("queued", "drafting", "ready", "published", "hold", "retired")
MIN_ANSWERABLE = 60
HYPOTHESIS_CAP = 40       # a question tagged [hypothesis] is nobody's words yet; it cannot be chosen until a real person asked it
STOP = {"a", "an", "the", "is", "are", "do", "does", "how", "what", "why", "when", "which", "can", "i", "my",
        "to", "for", "of", "in", "on", "and", "or", "it", "be", "should", "much", "with", "me", "you", "your"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def today():
    return date.today().isoformat()


def slugify(text, limit=60):
    t = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    ws = [w for w in t.split() if w not in STOP] or t.split()
    slug = "-".join(ws)
    if len(slug) > limit:
        slug = slug[:limit].rsplit("-", 1)[0]
    return slug.strip("-") or "question"


def load(folder):
    p = Path(folder) / "questions.json"
    if not p.exists():
        die(f"{p} not found; run `init` first")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{p} is not valid JSON: {e}")
    data.setdefault("questions", [])
    return data, p


def save(data, p):
    data["updated"] = today()
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_id(data):
    nums = [int(q["id"].split("-")[1]) for q in data["questions"] if re.fullmatch(r"Q-\d+", q.get("id", ""))]
    return f"Q-{(max(nums) + 1) if nums else 1:02d}"


def parse_rate(text):
    if not text:
        return None
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 5:
        die("--rate needs five marks from 1 to 5: demand,value,gap,answerable,fresh")
    out = {}
    for key, part in zip(WEIGHTS, parts):
        try:
            mark = int(part)
        except ValueError:
            die(f"--rate: '{part}' is not a whole number from 1 to 5")
        if not 1 <= mark <= 5:
            die(f"--rate: {mark} is outside 1 to 5")
        out[key] = mark * 20
    return out


def score(q):
    s = q.get("scores") or {}
    return round(sum(float(s.get(k, 0)) * w for k, w in WEIGHTS.items()), 1)


def eligible(q):
    return q.get("status") == "queued" and float((q.get("scores") or {}).get("answerable", 0)) >= MIN_ANSWERABLE


def normalise(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def find_duplicate(data, question, slug):
    norm = normalise(question)
    for q in data["questions"]:
        if normalise(q["question"]) == norm or q.get("slug") == slug:
            return q
    return None


def apply_hypothesis(q):
    if "hypothesis" in (q.get("source") or "").lower() or "[hypothesis]" in q["question"].lower():
        q["scores"]["answerable"] = min(q["scores"]["answerable"], HYPOTHESIS_CAP)
        q["notes"] = (q.get("notes", "") + " [hypothesis: not a real person's question yet; confirm it before answering]").strip()


def add_question(data, question, intent, cluster, source, rates, notes=""):
    question = " ".join(question.replace("﻿", "").split())
    if not question:
        die("the question is empty")
    if intent not in INTENTS:
        die(f"--intent must be one of {', '.join(INTENTS)}")
    slug = slugify(question)
    dup = find_duplicate(data, question, slug)
    if dup:
        return dup, False
    q = {
        "id": next_id(data),
        "question": question,
        "slug": slug,
        "cluster": cluster or "general",
        "intent": intent,
        "source": source or "member",
        "scores": rates or {k: 60 for k in WEIGHTS},
        "rated": bool(rates),
        "status": "queued",
        "added": today(),
        "published_url": "",
        "published_on": "",
        "updated_on": "",
        "notes": notes,
    }
    apply_hypothesis(q)
    data["questions"].append(q)
    return q, True


def cmd_init(a):
    folder = Path(a.folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "answers").mkdir(exist_ok=True)
    (folder / "checks").mkdir(exist_ok=True)
    p = folder / "questions.json"
    if p.exists() and not a.force:
        die(f"{p} already exists (use --force to start over)")
    data = {"business": a.business or "", "created": today(), "updated": today(), "questions": []}
    save(data, p)
    print(json.dumps({"ok": True, "folder": str(folder), "file": str(p)}, indent=2))


def cmd_add(a):
    data, p = load(a.folder)
    q, created = add_question(data, a.question, a.intent, a.cluster, a.source, parse_rate(a.rate), a.notes or "")
    if created:
        save(data, p)
    print(json.dumps({"ok": True, "created": created, "question": q, "score": score(q),
                      "note": "" if created else f"already in the map as {q['id']}"}, indent=2, ensure_ascii=False))


def cmd_import(a):
    data, p = load(a.folder)
    src = Path(a.file)
    if not src.exists():
        die(f"{src} not found")
    added, skipped, notes = [], [], []
    for raw in src.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip().lstrip("-*• ").strip()
        if not line or line.startswith("#"):
            continue
        cluster, intent = a.cluster, a.intent
        if "|" in line:
            parts = [x.strip() for x in line.split("|")]
            line = parts[0]
            if len(parts) > 1 and parts[1]:
                cluster = parts[1]
            if len(parts) > 2 and parts[2]:
                if parts[2] in INTENTS:
                    intent = parts[2]
                else:
                    notes.append(f"'{parts[2]}' is not an intent ({', '.join(INTENTS)}); '{line[:40]}' filed as {intent}")
        q, created = add_question(data, line, intent, cluster, a.source, None)
        (added if created else skipped).append(q["id"] + " " + q["question"])
    save(data, p)
    print(json.dumps({"ok": True, "added": added, "skipped_duplicates": skipped, "notes": notes,
                      "note": "imported questions are unrated (60 each); rate them with `set Q-NN --rate d,v,g,a,f` before `next`"},
                     indent=2, ensure_ascii=False))


def ranked(data):
    return sorted(data["questions"], key=lambda q: (-score(q), q["id"]))


def cmd_score(a):
    data, _ = load(a.folder)
    rows = [q for q in ranked(data) if q["status"] in ("queued", "drafting", "ready")][: a.top]
    print(json.dumps({"ok": True, "weights": WEIGHTS, "min_answerable": MIN_ANSWERABLE,
                      "ranked": [{"id": q["id"], "score": score(q), "eligible": eligible(q), "rated": q.get("rated", False),
                                  "intent": q["intent"], "cluster": q["cluster"], "question": q["question"]} for q in rows]},
                     indent=2, ensure_ascii=False))


def pick_next(data, intent=""):
    published = [q for q in data["questions"] if q["status"] == "published"]
    pool = [q for q in ranked(data) if eligible(q)]
    if intent:
        pool = [q for q in pool if q["intent"] == intent]
        if not pool:
            return None, f"no eligible {intent} question"
        return pool[0], f"highest score among eligible {intent} questions (asked for)"
    if not pool:
        return None, "no eligible question: every queued question is either rated below 60 for answerable, on hold, or already drafted"
    if not any(q["intent"] == "service" for q in published):
        services = [q for q in pool if q["intent"] == "service"]
        if services:
            return services[0], "the service page comes first: one page per service is the best-supported page type for local search and AI answers"
    return pool[0], "highest score among eligible questions (buying intent counts most: cost, how to choose, vs, is it worth it)"


def cmd_next(a):
    data, _ = load(a.folder)
    q, reason = pick_next(data, a.intent)
    out = {"ok": q is not None, "reason": reason}
    if q:
        out["next"] = {"id": q["id"], "question": q["question"], "slug": q["slug"], "intent": q["intent"],
                       "cluster": q["cluster"], "score": score(q), "scores": q["scores"], "source": q["source"]}
        out["draft_file"] = f"{a.folder}/answers/{q['slug']}.md"
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if not q:
        sys.exit(1)


def cmd_set(a):
    data, p = load(a.folder)
    q = next((x for x in data["questions"] if x["id"] == a.id), None)
    if not q:
        die(f"{a.id} is not in the map")
    if a.status:
        if a.status not in STATUSES:
            die(f"--status must be one of {', '.join(STATUSES)}")
        if a.status == "published" and not (a.url or q.get("published_url")):
            die("a published question needs --url")
        q["status"] = a.status
        if a.status == "published":
            q["published_on"] = q.get("published_on") or today()
            q["updated_on"] = today()
    if a.url:
        q["published_url"] = a.url
    if a.slug:
        if q["status"] == "published":
            die("this question is published; its slug and URL stay as they are (publish a new page for a new address)")
        q["slug"] = slugify(a.slug) if " " in a.slug else a.slug
    if a.cluster:
        q["cluster"] = a.cluster
    if a.intent:
        if a.intent not in INTENTS:
            die(f"--intent must be one of {', '.join(INTENTS)}")
        q["intent"] = a.intent
    if a.rate:
        q["scores"] = parse_rate(a.rate)
        q["rated"] = True
        apply_hypothesis(q)
    if a.notes is not None:
        q["notes"] = a.notes
    if a.updated:
        q["updated_on"] = today()
    save(data, p)
    print(json.dumps({"ok": True, "question": q, "score": score(q)}, indent=2, ensure_ascii=False))


def cmd_list(a):
    data, _ = load(a.folder)
    rows = [q for q in ranked(data) if not a.status or q["status"] == a.status]
    print(json.dumps({"ok": True, "count": len(rows),
                      "questions": [{"id": q["id"], "status": q["status"], "score": score(q), "intent": q["intent"],
                                     "cluster": q["cluster"], "question": q["question"], "url": q.get("published_url", "")}
                                    for q in rows]}, indent=2, ensure_ascii=False))


def render_md(data):
    qs = data["questions"]
    by = {s: [q for q in qs if q["status"] == s] for s in STATUSES}
    nxt, reason = pick_next(data)
    lines = [f"# Question map{(' · ' + data['business']) if data.get('business') else ''}", "",
             f"Updated: {data.get('updated', today())} · Mapped: {len(qs)} · Published: {len(by['published'])} · "
             f"Queued: {len(by['queued'])} · Drafting or ready: {len(by['drafting']) + len(by['ready'])} · "
             f"On hold: {len(by['hold'])} · Retired: {len(by['retired'])}", ""]
    lines += [f"**Next to answer:** {nxt['id']} · {nxt['question']} ({reason})" if nxt else f"**Next to answer:** none ({reason})", ""]
    lines += ["## Ranked", "", "| ID | Score | Status | Intent | Cluster | Question | Source | Published |", "|---|---|---|---|---|---|---|---|"]
    for q in ranked(data):
        if q["status"] == "retired":
            continue
        lines.append(f"| {q['id']} | {score(q)}{'' if q.get('rated') else ' (unrated)'} | {q['status']} | {q['intent']} | {q['cluster']} | "
                     f"{q['question']} | {q['source']} | {q.get('published_url') or '—'} |")
    clusters = sorted({q["cluster"] for q in qs})
    if clusters:
        lines += ["", "## Clusters (each becomes a hub page once it has three published answers)", ""]
        for c in clusters:
            pub = [q for q in by["published"] if q["cluster"] == c]
            tot = [q for q in qs if q["cluster"] == c and q["status"] != "retired"]
            lines.append(f"- **{c}**: {len(pub)} published of {len(tot)}" + (" · hub ready" if len(pub) >= 3 else ""))
    if by["retired"]:
        lines += ["", "## Retired (never re-added)", ""] + [f"- {q['id']} {q['question']}" for q in by["retired"]]
    lines += ["", "Scores: demand 25% · value to the business 25% · citation gap 20% · answerable 20% · freshness 10%. "
              f"A question needs answerable ≥ {MIN_ANSWERABLE} to be chosen.", ""]
    return "\n".join(lines)


def cmd_md(a):
    data, p = load(a.folder)
    out = Path(a.folder) / "question-map.md"
    out.write_text(render_md(data), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(out)}, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default="search", help="the search folder (default: search)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, f):
        s = sub.add_parser(name)
        s.add_argument("--folder", dest="folder_sub", default=None)
        s.set_defaults(f=f)
        return s
    s = sp("init", cmd_init); s.add_argument("--business", default=""); s.add_argument("--force", action="store_true")
    s = sp("add", cmd_add); s.add_argument("question"); s.add_argument("--intent", default="other", choices=INTENTS)
    s.add_argument("--cluster", default=""); s.add_argument("--source", default=""); s.add_argument("--rate", default=""); s.add_argument("--notes", default="")
    s = sp("import", cmd_import); s.add_argument("file"); s.add_argument("--source", default="import")
    s.add_argument("--cluster", default=""); s.add_argument("--intent", default="other", choices=INTENTS)
    s = sp("score", cmd_score); s.add_argument("--top", type=int, default=15)
    s = sp("next", cmd_next); s.add_argument("--intent", default="")
    s = sp("set", cmd_set); s.add_argument("id"); s.add_argument("--status", default=""); s.add_argument("--url", default="")
    s.add_argument("--slug", default=""); s.add_argument("--cluster", default=""); s.add_argument("--intent", default="")
    s.add_argument("--rate", default=""); s.add_argument("--notes", default=None); s.add_argument("--updated", action="store_true")
    s = sp("list", cmd_list); s.add_argument("--status", default="")
    sp("md", cmd_md)
    a = ap.parse_args(argv)
    if getattr(a, "folder_sub", None):
        a.folder = a.folder_sub
    a.f(a)


if __name__ == "__main__":
    main()
