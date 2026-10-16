#!/usr/bin/env python3
"""LinkedIn Engine weekly scorecard: the member's own numbers, read from their own exports.

Reads LinkedIn's creator analytics export (.xlsx: Analytics → Export, the member downloads it) and
the pipeline log (li_pipeline.py), plus the few numbers LinkedIn shows but does not export, typed by
the member. Writes one markdown scorecard a week with last week beside it, a four-week trend, the
starter targets and a plain diagnosis. Never contacts LinkedIn.

Usage
  li_scorecard.py inspect export.xlsx                  show the sheets and the columns found (check a new export)
  li_scorecard.py week --pipeline linkedin/pipeline.json [--xlsx export.xlsx] [--manual manual.json]
                       [--from YYYY-MM-DD] [--out linkedin/scorecards/]

manual.json (what LinkedIn shows on screen but does not export; all optional)
  {"profile_viewers": 41, "saves": 12, "sends": 3, "followers_from_posts": 9, "profile_views_from_posts": 30,
   "ai_slop_flags": 0}

The export's layout has changed over time, so the reader looks for columns by name (impressions,
members reached, engagements, new followers, post URL, date) on any sheet rather than by position.
Standard library only.
"""
import argparse, datetime as dt, json, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import li_pipeline  # noqa: E402

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
TARGETS = [("posts", "Posts", "3", 3, None), ("comments", "Substantive comments on others' posts", "25–50", 25, None),
           ("invites", "Connection requests sent", "30–60", 30, 80), ("acceptance_rate", "Acceptance", "≥ 40%", .40, None),
           ("dms_started", "Warm-signal DMs started", "10–15", 10, None), ("reply_rate", "Reply rate on warm DMs", "≥ 25%", .25, None),
           ("replies", "Real conversations", "3–5", 3, None), ("calls_booked", "Calls booked", "1–2", 1, None)]


# ---------------- xlsx (stdlib) ----------------

def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path):
    """{sheet name: [[cell values]]}; numbers as float, dates left as Excel serials or strings."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels}
    out = {}
    for sh in wb.find("m:sheets", NS):
        rid = sh.get(f"{{{NS['r']}}}id")
        t = target[rid].lstrip("/")
        t = t if t.startswith("xl/") else "xl/" + t
        rows = []
        for row in ET.fromstring(z.read(t)).iter(f"{{{NS['m']}}}row"):
            vals = []
            for c in row.findall("m:c", NS):
                i = col_index(c.get("r")) if c.get("r") else len(vals)
                while len(vals) < i:
                    vals.append(None)
                v = c.find("m:v", NS); typ = c.get("t")
                if typ == "s" and v is not None:
                    val = shared[int(v.text)]
                elif typ == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
                elif v is not None:
                    try:
                        val = float(v.text)
                    except ValueError:
                        val = v.text
                else:
                    val = None
                vals.append(val)
            rows.append(vals)
        out[sh.get("name")] = rows
    return out


def norm(h):
    return re.sub(r"[^a-z]+", " ", str(h or "").lower()).strip()


def to_date(v):
    if isinstance(v, float):
        return dt.date(1899, 12, 30) + dt.timedelta(days=int(v))
    s = str(v or "").strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def tables(sheets):
    """Find header rows (a row with two or more text cells, one naming a metric) and the rows under them."""
    found = []
    for name, rows in sheets.items():
        for i, row in enumerate(rows):
            heads = [norm(x) for x in row]
            if sum(1 for h in heads if h) >= 2 and any(k in h for h in heads for k in ("impression", "follower", "engagement", "members reached")):
                body = []
                for r in rows[i + 1:]:
                    if not any(x not in (None, "") for x in r):
                        break
                    body.append(r)
                found.append({"sheet": name, "header": heads, "rows": body})
    return found


def kv_pairs(sheets):
    """Label/value rows like 'Impressions | 12,345' (summary sheets)."""
    out = {}
    for name, rows in sheets.items():
        for r in rows:
            cells = [x for x in r if x not in (None, "")]
            if len(cells) == 2 and isinstance(cells[0], str) and num(cells[1]) is not None:
                out.setdefault(norm(cells[0]), num(cells[1]))
    return out


def metrics_from_xlsx(path, start, end):
    sheets = read_xlsx(path)
    m = {"source": Path(path).name, "impressions": None, "members_reached": None, "engagements": None,
         "new_followers": None, "top_posts": []}
    for t in tables(sheets):
        h = t["header"]
        di = next((i for i, x in enumerate(h) if x == "date" or x.endswith(" date")), None)
        url = next((i for i, x in enumerate(h) if "url" in x or "link" in x), None)
        def col(*keys):
            return next((i for i, x in enumerate(h) if any(x == k or x.startswith(k) for k in keys)), None)
        if di is not None and url is None:  # a daily table: sum the rows in the week
            for key, idx in (("impressions", col("impressions")), ("engagements", col("engagements")),
                             ("new_followers", col("new followers")), ("members_reached", col("members reached", "unique"))):
                if idx is None:
                    continue
                tot = 0.0; seen = False
                for r in t["rows"]:
                    d = to_date(r[di]) if di < len(r) else None
                    if d and start <= d < end and idx < len(r) and num(r[idx]) is not None:
                        tot += num(r[idx]); seen = True
                if seen:
                    m[key] = (m[key] or 0) + tot
        elif url is not None:  # per-post table
            imp, eng = col("impressions"), col("engagements")
            pdi = next((i for i, x in enumerate(h) if "date" in x), None)
            for r in t["rows"]:
                d = to_date(r[pdi]) if pdi is not None and pdi < len(r) else None
                if d and not (start <= d < end):
                    continue
                if url < len(r) and r[url]:
                    m["top_posts"].append({"url": r[url], "impressions": num(r[imp]) if imp is not None and imp < len(r) else None,
                                           "engagements": num(r[eng]) if eng is not None and eng < len(r) else None})
    kv = kv_pairs(sheets)
    for key, labels in (("impressions", ("impressions",)), ("members_reached", ("members reached",)),
                        ("new_followers", ("new followers",))):
        if m[key] is None:
            m[key] = next((kv[k] for k in kv if k in labels), None)
    m["top_posts"] = sorted(m["top_posts"], key=lambda p: -(p["impressions"] or 0))[:5]
    return m


# ---------------- scorecard ----------------

def pct(v):
    return "—" if v is None else f"{v * 100:.0f}%"


def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float) and v < 1 and v > 0:
        return pct(v)
    return f"{v:,.0f}" if isinstance(v, (int, float)) else str(v)


def diagnose(c, li, manual, prev):
    notes = []
    pv = manual.get("profile_viewers")
    if c["comments"] < 25:
        notes.append("**Comments are the cheapest lever.** Fewer than 25 substantive comments this week: do the daily 10 minutes on tiers A and B before anything else.")
    if pv is not None and prev and prev.get("manual", {}).get("profile_viewers") and pv < prev["manual"]["profile_viewers"]:
        notes.append("**Profile viewers fell.** Check comment volume and that this week's posts stayed on the pillars.")
    if c["invites"] and c["acceptance_rate"] is not None and c["acceptance_rate"] < .30:
        notes.append("**Acceptance under 30%.** Either the requests are going to cold people (send to warm signals first) or the profile is not converting (headline and banner).")
    if c["dms_started"] >= 5 and (c["reply_rate"] or 0) < .20:
        notes.append("**Few replies.** Messages may be too long, about the member, or missing the signal. Shorter, signal first, one question.")
    if c["replies"] >= 3 and c["calls_booked"] == 0:
        notes.append("**Conversations but no calls.** Ask (D5) after two real exchanges, and make the call low-stakes: 20 minutes to map options.")
    if c["calls_held"] >= 2 and c["won"] == 0 and c["proposals"] == 0:
        notes.append("**Calls but no proposals.** The offer or the call itself is the bottleneck: run Sales Conversations (\"Help me with my sales call\").")
    if c["posts"] < 2:
        notes.append("**Fewer than two posts.** Consistency beats volume: three a week from the calendar, captured in one 20-minute session.")
    if li and li.get("impressions") and prev and prev.get("linkedin", {}).get("impressions"):
        ch = li["impressions"] / prev["linkedin"]["impressions"] - 1
        if ch < -.4:
            notes.append(f"**Impressions down {abs(ch):.0%} on last week.** Normal swings are large; judge reach over four weeks, and look at who engaged, not how many.")
    if manual.get("ai_slop_flags"):
        notes.append("**A reader flagged a post as AI-like.** Rebuild drafts from the member's own words; cut the AI tells (content-system.md §6).")
    return notes or ["On track this week. Keep the routine; review the four-week trend before changing anything."]


def cmd_week(a):
    data = li_pipeline.load(a.pipeline)
    start = dt.date.fromisoformat(a.start) if a.start else dt.date.today() - dt.timedelta(days=dt.date.today().weekday() + 7)
    end = start + dt.timedelta(days=7)
    c = li_pipeline.week_counts(data, start)
    li = metrics_from_xlsx(a.xlsx, start, end) if a.xlsx else None
    manual = json.loads(Path(a.manual).read_text(encoding="utf-8")) if a.manual else {}
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    iso = start.isocalendar()
    stem = f"{iso[0]}-W{iso[1]:02d}"
    prev_path = out / f"{(start - dt.timedelta(days=7)).isocalendar()[0]}-W{(start - dt.timedelta(days=7)).isocalendar()[1]:02d}.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else None
    history = sorted(out.glob("*-W*.json"))[-3:]
    rec = {"week": stem, "from": c["from"], "to": c["to"], "pipeline": c, "linkedin": li, "manual": manual}
    (out / f"{stem}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    pc = (prev or {}).get("pipeline", {})
    md = [f"# LinkedIn scorecard · {stem} ({c['from']} to {c['to']})", "",
          "## What you did (inputs)", "", "| | This week | Last week | Starter target |", "|---|---|---|---|"]
    for key, label, target, lo, hi in TARGETS:
        v = c.get(key)
        flag = "" if v is None else (" ⚠️" if (hi and v > hi) else (" ✅" if v >= lo else ""))
        md.append(f"| {label} | {fmt(v)}{flag} | {fmt(pc.get(key))} | {target} |")
    md += ["", f"Posts by format: {c['posts_by_format'] or '—'} · by pillar: {c['posts_by_pillar'] or '—'}",
           f"Warm signals logged: {c['signals']} {c['signals_by_type'] or ''}", "",
           "## What came back (outputs)", "", "| | This week | Last week |", "|---|---|---|"]
    pl = (prev or {}).get("linkedin") or {}
    pm = (prev or {}).get("manual") or {}
    rows = [("Impressions (LinkedIn export)", (li or {}).get("impressions"), pl.get("impressions")),
            ("Members reached", (li or {}).get("members_reached"), pl.get("members_reached")),
            ("Engagements", (li or {}).get("engagements"), pl.get("engagements")),
            ("New followers", (li or {}).get("new_followers"), pl.get("new_followers")),
            ("Profile viewers (typed)", manual.get("profile_viewers"), pm.get("profile_viewers")),
            ("Saves + sends (typed)", (manual.get("saves") or 0) + (manual.get("sends") or 0) if manual else None,
             (pm.get("saves") or 0) + (pm.get("sends") or 0) if pm else None),
            ("Followers gained from posts (typed)", manual.get("followers_from_posts"), pm.get("followers_from_posts")),
            ("Conversations", c["replies"], pc.get("replies")), ("Calls booked", c["calls_booked"], pc.get("calls_booked")),
            ("Calls held", c["calls_held"], pc.get("calls_held")), ("Proposals", c["proposals"], pc.get("proposals")),
            ("Clients won (value)", f"{c['won']} ({c['won_value']:,.0f})", f"{pc.get('won', '—')} ({pc.get('won_value', 0) or 0:,.0f})" if pc else "—")]
    md += [f"| {k} | {fmt(v)} | {fmt(w)} |" for k, v, w in rows]
    if li and li["top_posts"]:
        md += ["", "Top posts this week (impressions): " + "; ".join(f"{p['url']} ({fmt(p['impressions'])})" for p in li["top_posts"][:3])]
    if not li:
        md += ["", "_No LinkedIn export this week: Analytics → Export (past 7 days), then run again with --xlsx._"]
    if history:
        md += ["", "## Four-week trend", "", "| Week | Posts | Comments | DMs | Conversations | Calls | Impressions |", "|---|---|---|---|---|---|---|"]
        for h in [json.loads(p.read_text(encoding="utf-8")) for p in history]:
            pp = h["pipeline"]
            md.append(f"| {h['week']} | {pp['posts']} | {pp['comments']} | {pp['dms_started']} | {pp['replies']} | {pp['calls_booked']} | {fmt((h.get('linkedin') or {}).get('impressions'))} |")
    md += ["", "## Diagnosis", "", *[f"- {n}" for n in diagnose(c, li, manual, prev)], "",
           "_Targets are a Build Room starting point, not research; after four weeks your own numbers replace them. "
           "Judge content by who engaged and the conversations it started, not by impressions alone._"]
    (out / f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"scorecard {out / (stem + '.md')}")
    return 0


def cmd_inspect(a):
    sheets = read_xlsx(a.xlsx)
    for name, rows in sheets.items():
        print(f"sheet {name!r}: {len(rows)} rows")
    for t in tables(sheets):
        print(f"  table on {t['sheet']!r}: columns {[h for h in t['header'] if h]} · {len(t['rows'])} rows")
    kv = kv_pairs(sheets)
    if kv:
        print("  summary values:", {k: v for k, v in list(kv.items())[:12]})
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("inspect"); s.add_argument("xlsx")
    s = sub.add_parser("week"); s.add_argument("--pipeline", required=True); s.add_argument("--xlsx"); s.add_argument("--manual")
    s.add_argument("--from", dest="start"); s.add_argument("--out", default="linkedin/scorecards")
    a = ap.parse_args(argv)
    return {"inspect": cmd_inspect, "week": cmd_week}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
