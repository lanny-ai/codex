#!/usr/bin/env python3
"""LinkedIn Engine weekly scorecard: the member's own numbers, read from their own exports.

Reads LinkedIn's creator analytics export (.xlsx: Analytics → Export, the member downloads it) and
the pipeline log (li_pipeline.py), plus the few numbers LinkedIn shows but does not export, typed by
the member. Writes one markdown scorecard a week with last week beside it, a four-week trend, the
starter targets and a plain diagnosis. Never contacts LinkedIn.

Usage
  li_scorecard.py inspect export.xlsx                  show the sheets, the columns and the export's own date range
  li_scorecard.py week [--pipeline linkedin/pipeline.json] [--xlsx export.xlsx] [--manual manual.json]
                       [--from YYYY-MM-DD | --date YYYY-MM-DD] [--out linkedin/scorecards/] [--allow-mismatch]
                       [--no-pipeline]

The week: --from gives its Monday; otherwise it is the last complete Monday–Sunday week before today
(or before --date), the same default as li_pipeline.py week. Export LinkedIn's analytics with a custom
range of exactly that Monday to Sunday: the reader reads the export's own range (DISCOVERY, "Overall
Performance  MM/DD/YYYY - MM/DD/YYYY") and refuses an export that does not cover the scorecard week
(exit 2; --allow-mismatch writes the card anyway, with the mismatch shown). The summary values (members
reached) are used only when the range is exactly the week.

A missing pipeline file is refused (exit 2): no card is written. --no-pipeline writes an export-only
card, marked at the top, with every pipeline number blank; its JSON carries "no_pipeline": true and is
left out of the four-week trend and of next week's "last week" pipeline column.

Targets (a Build Room starting point): posts 3 · substantive comments 25 · warm signals answered within
48 h: all (share of the week's new records, sig:known excluded, whose first touch came within 2 days of
the signal; below 80% is flagged) · acceptance ≥ 40% · reply rate ≥ 25% · real conversations 3–5 ·
calls booked 1–2. Information only (no target): warm-signal DMs started, and connection requests
(flagged above 50 a week). Acceptance is measured on the requests the member sent two weeks earlier
(the Monday–Sunday week two weeks before, so every request is at least 14 days old by this Sunday),
accepted by this Sunday; when there were none it shows n/a and is not diagnosed. The diagnosis shows
the top 3 problems, the first as "Change this one thing this week:".

manual.json (what LinkedIn shows on screen but does not export; all optional; any other key is warned)
  {"profile_viewers": 41, "saves": 12, "sends": 3, "followers_from_posts": 9, "profile_views_from_posts": 30}
  valid keys: profile_viewers, saves, sends, followers_from_posts, profile_views_from_posts

The export's layout has changed over time, so the reader looks for columns by name (impressions,
members reached, engagements, new followers, post URL, date) on any sheet rather than by position.
Standard library only.
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (keeps __pycache__ out of the installed skill folder)
import argparse, datetime as dt, json, re, zipfile  # noqa: E402
from pathlib import Path  # noqa: E402
from xml.etree import ElementTree as ET  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import li_pipeline  # noqa: E402

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
# key, label, target text, met (✅ at or above), low (a shortfall below), high (⚠️ above), flag (⚠️ below)
TARGETS = [("posts", "Posts", "3", 3, 3, None, None),
           ("comments", "Substantive comments on others' posts", "25 (5 a weekday)", 25, 25, None, None),
           ("signals_answered_rate", "Warm signals answered within 48 h", "all (100%)", 1.0, .80, None, .80),
           ("dms_started", "Warm-signal DMs started", "information", None, None, None, None),
           ("invites", "Connection requests sent", "information (⚠️ above 50)", None, None, 50, None),
           ("acceptance_rate", "Acceptance (requests sent 2 weeks earlier)", "≥ 40%", .40, .40, None, None),
           ("reply_rate", "Reply rate on warm DMs", "≥ 25%", .25, .25, None, None),
           ("conversations", "Real conversations (2+ replies)", "3–5", 3, 3, None, None),
           ("calls_booked", "Calls booked", "1–2", 1, 1, None, None)]
RATES = {"acceptance_rate", "reply_rate", "signals_answered_rate"}
MANUAL_KEYS = ["profile_viewers", "saves", "sends", "followers_from_posts", "profile_views_from_posts"]
PERIOD = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{1,2}/\d{4})")


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
    """Label/value rows like 'Impressions | 12,345' (summary sheets). Daily rows (a date and a number) are not labels."""
    out = {}
    for name, rows in sheets.items():
        for r in rows:
            cells = [x for x in r if x not in (None, "")]
            if len(cells) == 2 and isinstance(cells[0], str) and num(cells[1]) is not None:
                if not norm(cells[0]) or to_date(cells[0]):
                    continue
                out.setdefault(norm(cells[0]), num(cells[1]))
    return out


def export_period(sheets):
    """The export's own date range ("Overall Performance | 10/12/2026 - 10/18/2026"), DISCOVERY first; (from, to) or None."""
    for name in sorted(sheets, key=lambda n: norm(n) != "discovery"):
        for r in sheets[name]:
            for x in r:
                mt = PERIOD.search(str(x or ""))
                if mt:
                    a, b = to_date(mt.group(1)), to_date(mt.group(2))
                    if a and b:
                        return a, b
    return None


def metrics_from_xlsx(path, start, end):
    sheets = read_xlsx(path)
    m = {"source": Path(path).name, "impressions": None, "members_reached": None, "engagements": None,
         "new_followers": None, "top_posts": [], "period": None, "period_matches": None, "warnings": []}
    per = export_period(sheets)
    if per:
        m["period"] = [per[0].isoformat(), per[1].isoformat()]
        m["period_matches"] = per == (start, end - dt.timedelta(days=1))
    posts = {}
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
        elif url is not None:  # per-post tables; TOP POSTS holds two side by side (by engagements, by impressions)
            segs, cur = [], []
            for i, x in enumerate(h + [""]):
                if x:
                    cur.append(i)
                elif cur:
                    segs.append(cur); cur = []
            for seg in segs:
                sh = {h[i]: i for i in seg}
                u = next((i for k, i in sh.items() if "url" in k or "link" in k), None)
                if u is None:
                    continue
                pdi = next((i for k, i in sh.items() if "date" in k), None)
                for k, i in sh.items():
                    metric = "impressions" if k.startswith("impressions") else "engagements" if k.startswith("engagements") else None
                    if not metric:
                        continue
                    for r in t["rows"]:
                        if u >= len(r) or not r[u]:
                            continue
                        d = to_date(r[pdi]) if pdi is not None and pdi < len(r) else None
                        if d and not (start <= d < end):
                            continue
                        post = posts.setdefault(r[u], {"url": r[u], "date": d.isoformat() if d else None, "impressions": None, "engagements": None})
                        if i < len(r) and num(r[i]) is not None:
                            post[metric] = num(r[i])
    kv = kv_pairs(sheets)
    # summary values cover the export's whole range: use them only when that range is exactly this week
    if m["period_matches"]:
        for key, labels in (("impressions", ("impressions",)), ("members_reached", ("members reached",)),
                            ("new_followers", ("new followers",))):
            if m[key] is None:
                m[key] = next((kv[k] for k in kv if k in labels), None)
    elif any(k in kv for k in ("members reached",)):
        m["warnings"].append("members reached left out: the export's summary covers "
                             + (f"{m['period'][0]} to {m['period'][1]}" if m["period"] else "an unknown range")
                             + ", not this week (export a custom Monday–Sunday range to get it)")
    if m["members_reached"] is not None and m["impressions"] is not None and m["members_reached"] > m["impressions"]:
        m["warnings"].append(f"impossible numbers: members reached ({m['members_reached']:,.0f}) is more than impressions "
                             f"({m['impressions']:,.0f}); the export and the week do not line up. Re-export the exact week")
    # TOP POSTS is LinkedIn's sample of the top 50, not every post: use it to see what worked, not as totals.
    m["top_posts"] = sorted(posts.values(), key=lambda p: -(p["impressions"] or 0))[:5]
    return m


# ---------------- scorecard ----------------

def pct(v):
    return "—" if v is None else f"{v * 100:.0f}%"


def fmt(v, key=None):
    """Rates are formatted by key (1.0 → 100%), never guessed from the value."""
    if v is None:
        return "—"
    if key in RATES:
        return pct(v)
    return f"{v:,.0f}" if isinstance(v, (int, float)) else str(v)


def shortfalls(c):
    """One plain line for each starter target the week missed: too much cold volume first (account safety),
    then the cheapest lever first."""
    t = {k: (label, target, lo, hi) for k, label, target, met, lo, hi, flag in TARGETS}
    n = lambda k: c.get(k) or 0
    lines = {
        "comments": f"**Comments are the cheapest lever.** {n('comments')} substantive comments against {t['comments'][1]}: "
                    "do the daily 10 minutes on tiers A and B before anything else.",
        "posts": f"**{n('posts')} post(s) against 3.** Consistency beats volume: three a week from the calendar, "
                 "captured in one 20-minute session.",
        "signals_answered_rate": f"**{pct(c.get('signals_answered_rate'))} of this week's warm signals answered within 48 hours "
                                 "(target: all).** Every logged signal earns a first move (a request or a first message) "
                                 "within 48 hours: work the today list's signals waiting before anything else.",
        "acceptance_rate": ("**Acceptance under 30%** on the requests sent two weeks earlier. Either the requests are going "
                            "to cold people (send to warm signals first) or the profile is not converting (headline and banner).")
                           if (c.get("acceptance_rate") or 0) < .30 else
                           f"**Acceptance {pct(c.get('acceptance_rate'))} against ≥ 40%** (requests sent two weeks earlier). "
                           "Send to warm signals first, and check the headline and banner say who you help.",
        "reply_rate": f"**Few replies ({pct(c.get('reply_rate'))} against ≥ 25%).** Messages may be too long, about you, "
                      "or missing the signal. Shorter, signal first, one question.",
        "conversations": f"**{n('conversations')} real conversations against {t['conversations'][1]}.** A real conversation "
                         "is two or more replies from them: answer each reply with one more question (D6) before anything else.",
        "calls_booked": ("**Conversations but no calls.** Ask (D5) after two real exchanges, and make the call low-stakes: "
                         "a short call to map their options.") if n("conversations") >= 3 else
                        "**No calls booked.** Calls come from real conversations: build those first, then ask (D5).",
    }
    out = []
    if c.get("invites") is not None and c["invites"] > t["invites"][3]:
        out.append(f"**{c['invites']:,.0f} connection requests sent: above {t['invites'][3]} a week.** Cold volume costs the "
                   "account more than it earns; slow down and send to warm signals only.")
    for k in ("comments", "posts", "signals_answered_rate", "acceptance_rate", "reply_rate", "conversations", "calls_booked"):
        lo = t[k][2]
        v = c.get(k)
        if v is None:      # n/a: nothing to measure (a rate with nothing to divide by) is never a problem
            continue
        if v < lo:
            out.append(lines[k])
    return out


def problems(c, li, manual, prev):
    """Every problem this week, most important first: the target shortfalls, then the other signs."""
    notes = shortfalls(c)
    pv = manual.get("profile_viewers")
    if pv is not None and prev and (prev.get("manual") or {}).get("profile_viewers") and pv < prev["manual"]["profile_viewers"]:
        notes.append("**Profile viewers fell.** Check comment volume and that this week's posts stayed on the pillars.")
    if (c.get("calls_held") or 0) >= 2 and not c.get("won") and not c.get("proposals"):
        notes.append("**Calls but no proposals.** The offer or the call itself is the bottleneck: run Sales Conversations (\"Help me with my sales call\").")
    if li and li.get("impressions") and prev and (prev.get("linkedin") or {}).get("impressions"):
        ch = li["impressions"] / prev["linkedin"]["impressions"] - 1
        if ch < -.4:
            notes.append(f"**Impressions down {abs(ch):.0%} on last week.** Normal swings are large; judge reach over four weeks, and look at who engaged, not how many.")
    return notes


def diagnose(c, li, manual, prev):
    """The top 3 problems, the first labelled as the one change for the week; "On track" only when every target is met."""
    notes = problems(c, li, manual, prev)
    if not notes:
        return ["On track this week: every starter target met. Keep the routine; review the four-week trend before changing anything."]
    top = notes[:3]
    return ["Change this one thing this week: " + top[0]] + ["Also below target: " + x for x in top[1:]]


def wk(d):
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def refused(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    return 2


def a_date(s):
    """A YYYY-MM-DD date, or None (the caller refuses cleanly)."""
    try:
        return dt.date.fromisoformat(str(s).strip())
    except ValueError:
        return None


def read_manual(path, alerts):
    """manual.json: the typed numbers. Unknown keys are warned with the valid ones; None when unreadable."""
    try:
        manual = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"cannot read {path} ({e}); it must be JSON like {{\"profile_viewers\": 41}}"
    if not isinstance(manual, dict):
        return None, f"{path} must be a JSON object like {{\"profile_viewers\": 41}}"
    bad = [k for k in manual if k not in MANUAL_KEYS]
    if bad:
        alerts.append(f"{path}: unknown key(s) {', '.join(bad)} ignored; the valid keys are {', '.join(MANUAL_KEYS)}")
    nonnum = [k for k in MANUAL_KEYS if k in manual and not isinstance(manual[k], (int, float))]
    if nonnum:
        alerts.append(f"{path}: {', '.join(nonnum)} must be numbers; ignored")
    return {k: v for k, v in manual.items() if k in MANUAL_KEYS and k not in nonnum}, None


def cmd_week(a):
    on = a_date(a.date) if a.date else dt.date.today()
    if on is None:
        return refused(f"--date must be a real date as YYYY-MM-DD (got {a.date!r})")
    start = a_date(a.start) if a.start else li_pipeline.last_full_week(on)
    if start is None:
        return refused(f"--from must be a real date as YYYY-MM-DD (got {a.start!r})")
    end = start + dt.timedelta(days=7)
    alerts = []
    no_pipeline = bool(a.no_pipeline)
    if no_pipeline:
        data = li_pipeline.new_pipeline()
        alerts.append("no pipeline: this card is from the LinkedIn export only. Every pipeline number is blank, and the "
                      "week is left out of the four-week trend")
    else:
        try:
            data = li_pipeline.load(a.pipeline)
        except FileNotFoundError:
            return refused(f"no pipeline file at {a.pipeline}; no scorecard written. Pass --pipeline with the member's "
                           "file (or create it with li_pipeline.py settings), or --no-pipeline for an export-only card "
                           "(marked, and left out of the trend).")
        except SystemExit:   # li_pipeline refused an unreadable file and printed why
            return 2
    c = li_pipeline.week_counts(data, start)
    if no_pipeline:   # blank, not zero: nothing was measured
        c = {k: (None if isinstance(v, (int, float)) or k in ("acceptance_rate", "reply_rate", "signals_answered_rate") else v)
             for k, v in c.items()}
        c["posts_by_format"] = c["posts_by_pillar"] = c["signals_by_type"] = {}
    try:
        li = metrics_from_xlsx(a.xlsx, start, end) if a.xlsx else None
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        return refused(f"cannot read {a.xlsx} as an .xlsx export ({e})")
    if li:
        per = li["period"]
        covers = per and dt.date.fromisoformat(per[0]) <= start and dt.date.fromisoformat(per[1]) >= end - dt.timedelta(days=1)
        if per and not covers:
            msg = (f"the export covers {per[0]} to {per[1]}, but this scorecard is for {c['from']} to {c['to']}. "
                   f"Export again with a custom range {c['from']} to {c['to']}, or run with --from {per[0]} if that is the week you mean.")
            if not a.allow_mismatch:
                return refused(msg)
            alerts.append("export range does not match: " + msg)
        elif not per:
            alerts.append("the export's date range was not found (DISCOVERY, Overall Performance): check it covers this week")
        alerts += li["warnings"]
    manual = {}
    if a.manual:
        manual, err = read_manual(a.manual, alerts)
        if err:
            return refused(err)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = wk(start)
    prev_path = out / f"{wk(start - dt.timedelta(days=7))}.json"
    try:
        prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else None
    except ValueError:
        prev = None
        alerts.append(f"last week's {prev_path.name} is not readable JSON: the last-week column is blank")
    rec = {"week": stem, "from": c["from"], "to": c["to"], "pipeline": c, "linkedin": li, "manual": manual, "alerts": alerts,
           **({"no_pipeline": True} if no_pipeline else {})}
    (out / f"{stem}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")

    def readable(p):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    # the trend: this week and the three before it (never later weeks, when an old week is rerun); export-only
    # weeks (no pipeline) are left out
    history = [h for h in (readable(p) for p in sorted(out.glob("*-W*.json")) if p.stem <= stem)
               if h and not h.get("no_pipeline")][-4:]
    pc = {} if (prev or {}).get("no_pipeline") else (prev or {}).get("pipeline", {})
    blank = lambda v: "—" if v is None else v
    md = [f"# LinkedIn scorecard · {stem} ({c['from']} to {c['to']})" + (" · NO PIPELINE (export only)" if no_pipeline else ""), ""]
    if alerts:
        md += [f"> ⚠️ **{x[0].upper() + x[1:]}**" for x in alerts] + [""]
    md += ["## What you did (inputs)", "", "| | This week | Last week | Starter target |", "|---|---|---|---|"]
    for key, label, target, met, lo, hi, low_flag in TARGETS:
        v = c.get(key)
        if v is None:
            shown = "n/a" if key in RATES and not no_pipeline else "—"
            flag = ""
        else:
            shown = fmt(v, key)
            flag = (" ⚠️" if (hi is not None and v > hi) or (low_flag is not None and v < low_flag)
                    else " ✅" if met is not None and v >= met else "")
        md.append(f"| {label} | {shown}{flag} | {fmt(pc.get(key), key)} | {target} |")
    if not no_pipeline:
        md += ["", f"Acceptance (requests sent 2 weeks earlier): your own requests sent {c['cohort_from']} to {c['cohort_to']} "
                   f"({c['cohort_sent']} people, every one at least 14 days old by {c['to']}), accepted by {c['to']}: "
                   f"{c['cohort_accepted']}" + ("" if c["cohort_sent"] else " (n/a: none sent that week)")
                   + f". Inbound requests and cold requests logged with log-requests are not counted. "
                   f"Sent this week: {c['invited']} people in the pipeline + {c['cold_requests']} cold.",
               f"Warm signals answered within 48 h: {c['signals_answered']} of {c['signals_timed']} records added this week "
               "(first touch within 2 days of the signal; sig:known not timed).",
               f"Posts by format: {c['posts_by_format'] or '—'} · by pillar: {c['posts_by_pillar'] or '—'}",
               f"Warm signals logged: {c['signals']} {c['signals_by_type'] or ''}"]
    md += ["", "## What came back (outputs)", "", "| | This week | Last week |", "|---|---|---|"]
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
            ("Profile views from posts (typed)", manual.get("profile_views_from_posts"), pm.get("profile_views_from_posts")),
            ("Replies (people who replied)", c["replies"], pc.get("replies")),
            ("Real conversations (2+ replies)", c["conversations"], pc.get("conversations")),
            ("Calls booked", c["calls_booked"], pc.get("calls_booked")),
            ("Calls held", c["calls_held"], pc.get("calls_held")), ("Proposals", c["proposals"], pc.get("proposals")),
            ("Clients won (value)", f"{c['won']} ({c['won_value']:,.0f})" if c["won"] is not None else None,
             f"{pc.get('won', '—')} ({pc.get('won_value', 0) or 0:,.0f})" if pc else "—")]
    md += [f"| {k} | {fmt(v)} | {fmt(w)} |" for k, v, w in rows]
    if li and li["period"]:
        md += ["", f"LinkedIn export range: {li['period'][0]} to {li['period'][1]}" + ("" if li["period_matches"] else " (not exactly this week)")]
    if li and li["top_posts"]:
        md += ["", "Top posts this week (impressions): " + "; ".join(f"{p['url']} ({fmt(p['impressions'])})" for p in li["top_posts"][:3])]
    if not li:
        md += ["", f"_No LinkedIn export this week: Analytics → Export with a custom range {c['from']} to {c['to']}, then run again with --xlsx._"]
    if history:
        md += ["", "## Four-week trend", "", "| Week | Posts | Comments | DMs | Real conversations | Calls | Impressions |", "|---|---|---|---|---|---|---|"]
        for h in history:
            pp = h["pipeline"]
            md.append(f"| {h['week']} | {pp['posts']} | {pp['comments']} | {pp['dms_started']} | {pp.get('conversations', pp.get('replies', 0))} "
                      f"| {pp['calls_booked']} | {fmt((h.get('linkedin') or {}).get('impressions'))} |")
    probs = problems(c, li, manual, prev)
    md += ["", "## Diagnosis", "", *[f"- {n}" for n in diagnose(c, li, manual, prev)]]
    if len(probs) > 3:
        md += ["", f"_{len(probs) - 3} more below target (see the table). Fix the first one before the rest._"]
    md += ["",
           "_Targets are a Build Room starting point, not research; after four weeks your own numbers replace them. "
           "Judge content by who engaged and the conversations it started, not by impressions alone._"]
    (out / f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for x in alerts:
        print(f"WARNING: {x}", file=sys.stderr)
    print(f"scorecard {out / (stem + '.md')}")
    return 0


def cmd_inspect(a):
    try:
        sheets = read_xlsx(a.xlsx)
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        return refused(f"cannot read {a.xlsx} as an .xlsx export ({e})")
    for name, rows in sheets.items():
        print(f"sheet {name!r}: {len(rows)} rows")
    for t in tables(sheets):
        print(f"  table on {t['sheet']!r}: columns {[h for h in t['header'] if h]} · {len(t['rows'])} rows")
    kv = kv_pairs(sheets)
    if kv:
        print("  summary values:", {k: v for k, v in list(kv.items())[:12]})
    per = export_period(sheets)
    print(f"  export range: {per[0].isoformat()} to {per[1].isoformat()}" if per else "  export range: not found")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("inspect"); s.add_argument("xlsx")
    s = sub.add_parser("week"); s.add_argument("--pipeline", default=li_pipeline.DEFAULT_PATH); s.add_argument("--xlsx"); s.add_argument("--manual")
    s.add_argument("--from", "--start", dest="start"); s.add_argument("--date"); s.add_argument("--out", default="linkedin/scorecards")
    s.add_argument("--allow-mismatch", action="store_true", help="write the card even when the export's range is not the week")
    s.add_argument("--no-pipeline", action="store_true",
                   help="write an export-only card (marked; left out of the trend) when there is no pipeline file")
    s.epilog = "manual.json valid keys: " + ", ".join(MANUAL_KEYS)
    a = ap.parse_args(argv)
    return {"inspect": cmd_inspect, "week": cmd_week}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
