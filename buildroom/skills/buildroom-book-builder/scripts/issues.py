#!/usr/bin/env python3
"""AI Momentum Labs Book Builder: the issue register.

Every problem anyone finds (the developmental memo, the independent review, the fact audit, a
simulated reader, a real reader, the copyedit, the regression check) becomes one row with a
location, the evidence, a severity and a status. A memo that names a problem is not a fix:
the row stays open until an edition resolves it and a check confirms it.

Severity
  P0  harmful misinformation, a privacy or permission breach, a materially false claim
  P1  a broken central argument, unusable instructions, readers repeatedly missing the promised method
  P2  repetition, pacing, weak examples, inconsistent terms
  P3  cosmetic preferences and minor phrasing

Usage
  issues.py add     --book B --severity P1 --source memo|review|facts|simulated|human|copyedit|regression|author
                    --location "C04-P012" --issue "…" --evidence "…" [--fix "…"] [--readers R-01,R-03]
                    [--depends I-003] [--author-question "…"]
  issues.py list    --book B [--open] [--severity P0,P1] [--source human]
  issues.py resolve --book B --id I-007 --edition v2 --note "rewrote the steps; added the missing example"
  issues.py accept  --book B --id I-012 --by member --reason "…"       (P2 and P3 only; a P0 or P1 is fixed, not accepted)
  issues.py verify  --book B --id I-007 --result resolved|partial|unresolved|cannot-verify --edition v2 [--note "…"]
  issues.py reopen  --book B --id I-007 --note "…"
  issues.py summary --book B
Every command prints JSON. Exit 1 on a refusal.
"""
import argparse, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import booklib as bl  # noqa: E402

SEVERITIES = ("P0", "P1", "P2", "P3")
SOURCES = ("memo", "review", "facts", "simulated", "human", "copyedit", "regression", "author")
RESULTS = ("resolved", "partial", "unresolved", "cannot-verify")
BLOCKING = ("P0", "P1")


def path(book):
    return Path(book) / "edit" / "issues.json"


def load(book):
    bl.load_book(book)
    return bl.read_json(path(book), {"issues": []})


def find(d, iid):
    for i in d["issues"]:
        if i["id"].lower() == iid.lower():
            return i
    bl.refuse(f"no issue {iid}")


def is_open(i):
    return i["status"] in ("open", "fixed, not verified")


def cmd_add(a):
    d = load(a.book)
    if not a.issue.strip() or not a.evidence.strip() or not a.location.strip():
        bl.refuse("an issue needs a location, what is wrong, and the evidence")
    readers = [x.strip().upper() for x in (a.readers or "").split(",") if x.strip()]
    if a.source == "human" and not readers:
        bl.refuse("an issue from a real reader names the reader code(s) (--readers R-01)")
    iid = f"I-{len(d['issues']) + 1:03d}"
    d["issues"].append({"id": iid, "severity": a.severity, "source": a.source, "location": a.location.strip(),
                        "issue": a.issue.strip(), "evidence": a.evidence.strip(), "fix": (a.fix or "").strip(),
                        "readers": readers, "depends": [x.strip().upper() for x in (a.depends or "").split(",") if x.strip()],
                        "author_question": (a.author_question or "").strip(), "status": "open", "added": bl.today(),
                        "history": [{"status": "open", "date": bl.today()}]})
    bl.write_json(path(a.book), d)
    return {"ok": True, "id": iid, "open": sum(1 for i in d["issues"] if is_open(i))}


def cmd_list(a):
    d = load(a.book)
    rows = d["issues"]
    if a.open:
        rows = [i for i in rows if is_open(i)]
    if a.severity:
        want = {s.strip().upper() for s in a.severity.split(",")}
        rows = [i for i in rows if i["severity"] in want]
    if a.source:
        rows = [i for i in rows if i["source"] == a.source]
    return {"ok": True, "count": len(rows), "issues": rows}


def change(a, status, **extra):
    d = load(a.book)
    i = find(d, a.id)
    i["status"] = status
    i.update(extra)
    i["history"].append({"status": status, "date": bl.today(), **{k: v for k, v in extra.items() if v}})
    bl.write_json(path(a.book), d)
    return {"ok": True, "id": i["id"], "status": status, "severity": i["severity"]}


def cmd_resolve(a):
    data = bl.load_book(a.book)
    if a.edition and bl.slugify(a.edition) not in [e["label"] for e in data.get("editions", [])]:
        bl.refuse(f"no edition {a.edition}; freeze it first (manuscript.py edition)")
    return change(a, "fixed, not verified", edition=a.edition, note=a.note)


def cmd_accept(a):
    d = load(a.book)
    i = find(d, a.id)
    if i["severity"] in BLOCKING:
        bl.refuse(f"{i['id']} is {i['severity']}: it is fixed, not accepted. If it was graded too high, say why and "
                  "add it again at the right severity.")
    if a.by not in ("member", "editor") or not a.reason.strip():
        bl.refuse("an accepted issue records who accepted it (member or editor) and why")
    return change(a, "accepted", by=a.by, reason=a.reason.strip())


def cmd_verify(a):
    d = load(a.book)
    i = find(d, a.id)
    if i["status"] not in ("fixed, not verified", "resolved", "open"):
        bl.refuse(f"{i['id']} is {i['status']}")
    status = {"resolved": "resolved", "partial": "open", "unresolved": "open", "cannot-verify": "fixed, not verified"}[a.result]
    return change(a, status, verified=a.result, edition=a.edition, note=a.note)


def cmd_reopen(a):
    return change(a, "open", note=a.note)


def summary(d):
    out = {"total": len(d["issues"]), "open": {}, "by_source": {}, "blocking": [], "accepted": [], "unverified": []}
    for i in d["issues"]:
        out["by_source"][i["source"]] = out["by_source"].get(i["source"], 0) + 1
        if is_open(i):
            out["open"][i["severity"]] = out["open"].get(i["severity"], 0) + 1
            if i["severity"] in BLOCKING:
                out["blocking"].append(f"{i['id']} {i['severity']} {i['location']}: {i['issue'][:80]}")
        if i["status"] == "fixed, not verified":
            out["unverified"].append(i["id"])
        if i["status"] == "accepted":
            out["accepted"].append(i["id"])
    out["author_questions"] = [f"{i['id']}: {i['author_question']}" for i in d["issues"] if i["author_question"] and is_open(i)]
    return out


def cmd_summary(a):
    return {"ok": True, **summary(load(a.book))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name):
        x = sub.add_parser(name)
        x.add_argument("--book", required=True)
        return x
    x = p("add"); x.add_argument("--severity", choices=SEVERITIES, required=True)
    x.add_argument("--source", choices=SOURCES, required=True); x.add_argument("--location", required=True)
    x.add_argument("--issue", required=True); x.add_argument("--evidence", required=True); x.add_argument("--fix")
    x.add_argument("--readers"); x.add_argument("--depends"); x.add_argument("--author-question")
    x = p("list"); x.add_argument("--open", action="store_true"); x.add_argument("--severity"); x.add_argument("--source")
    x = p("resolve"); x.add_argument("--id", required=True); x.add_argument("--edition", required=True); x.add_argument("--note", required=True)
    x = p("accept"); x.add_argument("--id", required=True); x.add_argument("--by", required=True); x.add_argument("--reason", required=True)
    x = p("verify"); x.add_argument("--id", required=True); x.add_argument("--result", choices=RESULTS, required=True)
    x.add_argument("--edition", required=True); x.add_argument("--note")
    x = p("reopen"); x.add_argument("--id", required=True); x.add_argument("--note", required=True)
    p("summary")
    a = ap.parse_args()
    out = globals()["cmd_" + a.cmd](a)
    bl.emit(out, 0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
