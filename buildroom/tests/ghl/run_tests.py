#!/usr/bin/env python3
"""GoHighLevel snapshot: the build spec and the placeholder list Build Room OS reads must agree.

Usage:  python3 buildroom/tests/ghl/run_tests.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "rollout/ghl-snapshot"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def main():
    j = json.loads((D / "placeholders.json").read_text())
    spec = (D / "SNAPSHOT-SPEC.md").read_text()
    ps = j["placeholders"]
    keys = [p["key"] for p in ps]
    check("list: every key is unique, lower case, and starts with br_", len(keys) == len(set(keys)) and all(re.fullmatch(r"br_[a-z0-9_]+", k) for k in keys))
    check("list: every entry has a group, a label, a source and a known type",
          all(p.get("group") and p.get("label") and p.get("source") and p.get("type") in ("text", "long", "url", "email") and isinstance(p.get("required"), bool)
              and isinstance(p.get("fact"), bool) for p in ps))
    in_spec = set(re.findall(r"^\| `(br_[a-z0-9_]+)` \|", spec, re.M))
    check("spec and list name exactly the same custom values", in_spec == set(keys), f"only in spec {sorted(in_spec - set(keys))[:5]}, only in list {sorted(set(keys) - in_spec)[:5]}")
    check("spec states the same count as the list", f"The {len(ps)} in the tables below" in spec)
    check("spec and list carry the same version, and the version key is not a fillable value",
          f"_Version {j['version']} " in spec and j["version_key"] == "br_snapshot_version" and "br_snapshot_version" not in keys and f"set to `{j['version']}`" in spec)
    facts = {p["key"] for p in ps if p["fact"]}
    must_be_facts = {k for k in keys if re.search(r"price|value$|guarantee|urgency|proof|call_length|magnet_url|offer_structure|business_name|owner_", k)}
    check("list: prices, value, guarantee, urgency, proof, links and names are facts, never drafted", must_be_facts <= facts, sorted(must_be_facts - facts))
    check("list: no drafted-by-nature copy is locked as a fact", not any(re.search(r"headline|hook|bullet|button|faq|_body$|_subject$", k) for k in facts), sorted(facts))
    row = {m.group(1): (m.group(2).strip(), m.group(3).strip()) for m in re.finditer(r"^\| `(br_[a-z0-9_]+)` \|[^|]*\|[^|]*\| ([^|]*)\| ([^|]*)\|$", spec, re.M)}
    check("spec: the must-have and fact columns match the list", all(row[p["key"]] == ("yes" if p["required"] else "", "yes" if p["fact"] else "") for p in ps))
    check("list: required values come before optional ones in every numbered run",
          all(not (b["required"] and not a["required"]) for a, b in zip(ps, ps[1:])
              if re.sub(r"\d+$", "", a["key"]) == re.sub(r"\d+$", "", b["key"]) and a["key"] != b["key"]))
    emails = sorted({re.sub(r"_(subject|preview|body)$", "", k) for k in keys if k.startswith("br_em_")})
    check("list: every email has a subject and a body", len(emails) == 14 and all(e + "_subject" in keys and e + "_body" in keys for e in emails), emails)
    check("spec: fourteen templates and six workflows, all left in draft", "Fourteen email templates" in spec and "Six workflows, all left in Draft" in spec and spec.count("| `BR WF") == 6)
    check("spec: an empty optional email is never sent", "must not send" in spec)
    check("spec: no text messages, no payment, nothing published", "No SMS anywhere." in spec and "Taking payment" in spec and "publishes nothing" in spec)
    check("spec: says plainly that it is unproven and lists what to verify", "Nothing in this spec has been run against a real GoHighLevel account." in spec and spec.count("\n") > 100
          and len(re.findall(r"^\d\. ", spec[spec.index("## To verify in a test account"):spec.index("## Checking the snapshot")], re.M)) == 8)
    check("spec: a fact is never drafted, and blanks are reported", "A fact is never drafted." in spec and "left empty and reported" in spec)
    check("spec: Build Room OS refuses to push without the must-haves or a matching version", "Refuses to push if a \"must have\" value is missing" in spec and "stops if it is missing or does not match" in spec)
    check("spec: no long dashes", "—" not in spec and "–" not in spec)
    check("spec: no key, link or account detail of any member", not re.search(r"pit-[a-z0-9]|eyJ[A-Za-z0-9]|locationId=|@gmail|@yahoo", spec))
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
