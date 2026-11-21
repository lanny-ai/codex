#!/usr/bin/env python3
"""GoHighLevel values: turn a finished Autopilot run into the filled-in list of custom values for the
Build Room OS snapshot. It prepares a file. It does not connect to GoHighLevel and it sends nothing.

  ghl_values.py template [--group NAME]                 the worksheet: every value, where it comes from, its limit
  ghl_values.py check  --dir autopilot VALUES.json      nothing drafted where a fact belongs, nothing too long, nothing barred
  ghl_values.py export --dir autopilot VALUES.json OUT_DIR   writes custom_values.json, custom_values.csv and a review sheet

VALUES.json is written by the session from the member's approved drafts:
  {"br_optin_headline": {"v": "...", "basis": "drafted"}, "br_offer_price": {"v": "$4,800", "basis": "confirmed"}, ...}
  basis: confirmed (the member's own word), files (from their current files), drafted or reviewed (written for them).
A value that is not known is left out. It is never filled with a guess or a placeholder.

The list of values is references/ghl-placeholders.json, the same list the snapshot is built from.
Standard library only.
"""
import argparse, csv, importlib.util, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIST = HERE.parent / "references" / "ghl-placeholders.json"
_spec = importlib.util.spec_from_file_location("autopilot_drafts", HERE / "drafts.py")
drafts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drafts)
BASIS = ("confirmed", "files", "drafted", "reviewed")
LEFTOVER = re.compile(r"\[needs you|\[draft\]|\[reviewed draft\]|\[file:|\[hypothesis\]|\{\{|\}\}|\bTBD\b|lorem ipsum|YOUR[- ]", re.I)


def spec():
    try:
        d = json.loads(LIST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the list of values ({LIST}): {e}")
    return d, d["placeholders"]


def load_values(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the values file: {e}")
    if not isinstance(d, dict):
        sys.exit('The values file must be an object: {"br_key": {"v": "...", "basis": "..."}}')
    return d


def text_of(x):
    return str(x.get("v", "")).strip() if isinstance(x, dict) else ""


def problems(values, folder):
    _d, ps = spec()
    known = {p["key"]: p for p in ps}
    r = drafts.rules(folder, *_beside(folder))
    out = []
    for key, x in values.items():
        p = known.get(key)
        if not p:
            out.append(f"{key}: not a value the snapshot has")
            continue
        if not isinstance(x, dict) or x.get("basis") not in BASIS:
            out.append(f'{key}: must be {{"v": ..., "basis": confirmed | files | drafted | reviewed}}')
            continue
        v = text_of(x)
        if not v:
            out.append(f"{key}: empty. Leave a value out instead of sending an empty one")
            continue
        if p["fact"] and x["basis"] not in ("confirmed", "files"):
            out.append(f"{key} ({p['label']}): this is a fact. It comes from the member or their files, or it is left out. Never drafted")
        if p.get("max") and len(v) > p["max"]:
            out.append(f"{key}: {len(v)} characters, and the page element holds {p['max']}")
        if p["type"] == "url" and not re.fullmatch(r"https://\S+\.\S+", v):
            out.append(f"{key}: needs a full https:// link")
        if p["type"] != "long" and p["type"] != "email" and "\n" in v:
            out.append(f"{key}: one line only")
        if LEFTOVER.search(v):
            out.append(f"{key}: still carries a tag or a blank to fill ({LEFTOVER.search(v).group(0)}). A value goes in clean, or it is left out")
        # The same rules the drafts are held to. Every value here reaches a stranger.
        fixes, _looks = drafts.check_text(key, "Draft by Autopilot\n" + v, r, public=True)
        out += [re.sub(r"^" + re.escape(key) + r"(:\d+)?", key, f) for f in fixes]
    return out


def _beside(folder):
    folder = Path(folder)
    bf = folder.parent / "BUILDROOM_BUSINESS_FILE.md"
    led = folder.parent / "discovery" / "ledger.json"
    return (bf if bf.is_file() else None, led if led.is_file() else None)


def looks(values, folder):
    r = drafts.rules(folder, *_beside(folder))
    out = []
    for key, x in values.items():
        if isinstance(x, dict):
            out += drafts.check_text(key, "Draft by Autopilot\n" + text_of(x), r, public=True)[1]
    return [re.sub(r":\d+:", ":", l, count=1) for l in out]


def missing(values):
    _d, ps = spec()
    req = [p for p in ps if p["required"] and p["key"] not in values]
    opt = [p for p in ps if not p["required"] and p["key"] not in values]
    return req, opt


def cmd_template(a):
    d, ps = spec()
    groups = []
    for p in ps:
        if p["group"] not in groups:
            groups.append(p["group"])
    if a.group and a.group not in groups:
        sys.exit("Unknown group. One of: " + "; ".join(groups))
    print(f"Build Room OS snapshot {d['version']}: {len(ps)} custom values. Fill what the member's approved drafts and their own word support. Leave the rest out.\n")
    for g in groups:
        if a.group and g != a.group:
            continue
        print(f"## {g}")
        for p in ps:
            if p["group"] == g:
                tags = ["must have" if p["required"] else "optional", "FACT: member or files only" if p["fact"] else "copy", p["type"] + (f", up to {p['max']}" if p.get("max") else "")]
                print(f"  {p['key']}: {p['label']}  [{'; '.join(tags)}]  from: {p['source']}")
        print()


def cmd_check(a):
    values = load_values(a.values)
    probs = problems(values, a.dir)
    for x in probs:
        print("FIX  " + x)
    for x in looks(values, a.dir):
        print("LOOK  " + x)
    req, opt = missing(values)
    if req:
        print(f"\nMust-have values still missing ({len(req)}). The snapshot will not be filled until the member supplies these:")
        for p in req:
            print(f"  - {p['key']}: {p['label']} (from: {p['source']})")
    print(f"\n{len(values)} values given, {len(probs)} to fix, {len(req)} must-haves missing, {len(opt)} optional left out.")
    sys.exit(1 if probs else 0)


def cmd_export(a):
    d, ps = spec()
    values = load_values(a.values)
    probs = problems(values, a.dir)
    if probs:
        for x in probs:
            print("FIX  " + x, file=sys.stderr)
        sys.exit(f"{len(probs)} thing(s) to fix before anything is exported. Run: ghl_values.py check")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    req, opt = missing(values)
    flat = {p["key"]: text_of(values[p["key"]]) for p in ps if p["key"] in values}
    (out / "custom_values.json").write_text(json.dumps({"snapshot_version": d["version"], "complete": not req, "values": flat}, indent=1, ensure_ascii=False), encoding="utf-8")
    with (out / "custom_values.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "merge_tag", "group", "label", "value"])
        for p in ps:
            if p["key"] in values:
                w.writerow([p["key"], d["merge_tag"].replace("KEY", p["key"]), p["group"], p["label"], flat[p["key"]]])
    tag = {"confirmed": "yours", "files": "from your files", "drafted": "drafted for you", "reviewed": "drafted, approved by you"}
    md = ["# Your GoHighLevel values: review sheet", "",
          f"For the Build Room OS snapshot, version {d['version']}. This is a file on your computer. Nothing has been sent to GoHighLevel, and nothing is published.", "",
          f"**{len(flat)} of {len(ps)} values are filled.** " + ("Every must-have is there." if not req else f"{len(req)} must-have values are still missing, so the snapshot is not ready to fill yet."), "",
          "Read every line before it goes anywhere. Lines marked \"drafted for you\" are not your words until you have checked them.", ""]
    if req:
        md += ["## Still needed from you", ""] + [f"- **{p['label']}** ({p['group']}). Comes from: {p['source']}." for p in req] + [""]
    group = None
    for p in ps:
        if p["key"] not in values:
            continue
        if p["group"] != group:
            group = p["group"]
            md += [f"## {group}", ""]
        md += [f"**{p['label']}** · {tag[values[p['key']]['basis']]} · `{p['key']}`", "", "> " + flat[p["key"]].replace("\n", "\n> "), ""]
    if opt:
        md += ["## Left empty", "", "These are optional. For each one, remove its section from the page or leave its email switched off:", ""]
        md += [f"- {p['group']}: {p['label']}" for p in opt] + [""]
    md += ["## What only you can do", "", "- Connect your domain and your sending address.", "- Set your calendar hours.", "- Send yourself a test before turning any workflow on.", ""]
    (out / "GHL_Values_Review.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote custom_values.json, custom_values.csv and GHL_Values_Review.md to {out}.")
    print(f"{len(flat)} of {len(ps)} values filled. " + ("Every must-have is there." if not req else f"{len(req)} must-haves missing: the file is marked not complete."))
    for x in looks(values, a.dir):
        print("LOOK  " + x)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("template"); p.add_argument("--group"); p.set_defaults(fn=cmd_template)
    p = sub.add_parser("check"); p.add_argument("--dir", required=True); p.add_argument("values"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("export"); p.add_argument("--dir", required=True); p.add_argument("values"); p.add_argument("out"); p.set_defaults(fn=cmd_export)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
