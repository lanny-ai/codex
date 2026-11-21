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
    # ---- the values file: from a finished Autopilot run to a file ready to load ------------------
    import subprocess, tempfile
    SKA = D.parent.parent / "skills/buildroom-autopilot"
    GV, AP = SKA / "scripts/ghl_values.py", SKA / "scripts/autopilot.py"
    run = lambda *a: (lambda p: (p.returncode, p.stdout + p.stderr))(subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True))  # noqa: E731
    check("values: the skill carries the same list the snapshot is built from", (SKA / "references/ghl-placeholders.json").read_text() == (D / "placeholders.json").read_text())
    code, out = run(GV, "template")
    check("values: the worksheet lists every value with its limit and whether it is a fact", code == 0 and all(k + ":" in out for k in keys) and "FACT: member or files only" in out and f"{len(ps)} custom values" in out)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        A = t / "autopilot"
        (A / "drafts").mkdir(parents=True)
        tpl = (D.parent.parent / "templates/BUILDROOM_BUSINESS_FILE.md").read_text()
        (t / "BUILDROOM_BUSINESS_FILE.md").write_text(tpl.replace("- **Current price / price range:**", "- **Current price / price range:** $4,800")
            .replace("separated by semicolons):", "separated by semicolons): “Featured in Ceramics Monthly”"))
        run(AP, "plan", "--dir", A, "--readiness", "80", "--no-web")
        run(AP, "decide", "--dir", A, "--key", "guarantee", "--value", "none")
        vf = t / "values.json"
        c, d_, f_ = (lambda v: {"v": v, "basis": "confirmed"}), (lambda v: {"v": v, "basis": "drafted"}), (lambda v: {"v": v, "basis": "files"})
        good = {"br_business_name": c("Kiln & Co"), "br_owner_name": c("Marcus Bell"), "br_owner_first_name": c("Marcus"), "br_optin_headline": d_("Classes that fill"),
                "br_offer_price": c("$4,800")} if "br_offer_price" in keys else {"br_business_name": c("Kiln & Co"), "br_optin_headline": d_("Classes that fill")}
        def chk(v):
            vf.write_text(json.dumps(v))
            return run(GV, "check", "--dir", A, vf)
        code, out = chk(good)
        check("values: honest values pass, and the must-haves still missing are listed", code == 0 and "0 to fix" in out and "Must-have values still missing" in out and "br_magnet_url" in out, out[-400:])
        fact_key = next(p["key"] for p in ps if p["fact"] and p["type"] == "text" and p["key"] not in good)
        check("values: a fact is never drafted", "this is a fact" in chk({**good, fact_key: d_("Something plausible")})[1])
        check("values: an unknown key, an empty value and a leftover blank are refused", all(x in chk({**good, "br_made_up": d_("x"), "br_optin_subheadline": d_(" "), "br_optin_hook": d_("Book here: [needs you: a booking link]")})[1]
              for x in ("not a value the snapshot has", "Leave a value out", "still carries a tag or a blank")))
        check("values: a value longer than its page element is refused", "the page element holds 120" in chk({**good, "br_optin_headline": d_("x" * 121)})[1])
        check("values: a link must be a full https link", "full https:// link" in chk({**good, "br_magnet_url": c("mysite.com/guide")})[1])
        out = chk({**good, "br_optin_hook": d_("As featured in Ceramics Monthly. Most studios add $12,000. Results guaranteed.")})[1]
        check("values: a retired line, a figure nobody confirmed and a guarantee the member does not have are refused", "retired" in out and "$12,000" in out and "offers a guarantee" in out, out)
        vf.write_text(json.dumps({**good, "br_optin_hook": d_("We double your enrollment.")}))
        code, out = run(GV, "export", "--dir", A, vf, t / "out")
        check("export: nothing is written while something must be fixed", code != 0 and not (t / "out").exists(), out)
        vf.write_text(json.dumps(good))
        code, out = run(GV, "export", "--dir", A, vf, t / "out")
        cv = json.loads((t / "out/custom_values.json").read_text())
        sheet = (t / "out/GHL_Values_Review.md").read_text()
        check("export: writes the values, a csv with merge tags, and a review sheet", code == 0 and cv["values"]["br_business_name"] == "Kiln & Co" and cv["snapshot_version"] == j["version"]
              and "{{ custom_values.br_optin_headline }}" in (t / "out/custom_values.csv").read_text())
        check("export: a file with a must-have missing says it is not complete", cv["complete"] is False and "must-have values are still missing" in sheet and "## Still needed from you" in sheet)
        check("export: the sheet tags every line and says nothing was sent", "drafted for you" in sheet and "· yours ·" in sheet and "Nothing has been sent to GoHighLevel" in sheet and "## Left empty" in sheet
              and "—" not in sheet and "–" not in sheet)
    gsrc = GV.read_text()
    check("values: standard library only, and it connects to nothing", not any(x in gsrc for x in ("requests", "urllib", "socket", "http.client", "subprocess")))
    gref = (SKA / "references/ghl-values.md").read_text()
    check("skill: only on request, after the handover, and nothing is sent", "Prepare my GoHighLevel values" in (SKA / "SKILL.md").read_text() and "It does not connect to GoHighLevel" in gref
          and "A fact is never drafted." in gref and "Never fill a must-have to make the file complete." in gref and "—" not in gref and "–" not in gref)
    check("spec: says which steps are built and which are not", "are not built yet" in spec and "ghl_values.py" in spec)
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
