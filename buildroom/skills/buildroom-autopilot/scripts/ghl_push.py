#!/usr/bin/env python3
"""GoHighLevel push: write a member's approved values into the custom values of their own GoHighLevel sub-account.

  ghl_push.py plan autopilot/ghl          what would change in the account. Reads the account; changes nothing.
  ghl_push.py push autopilot/ghl --yes    creates or updates each value, waits, reads the account back and reports.

The folder is the one `ghl_values.py export` wrote: it holds custom_values.json. Run `plan` first, show the member,
and run `push` only on their go-ahead.

What it touches: custom values whose names start with br_ and are on the snapshot's list. It never deletes a value,
never touches a value it did not name, and never sends an email, publishes a page or switches a workflow on.

Where the token comes from: GHL_TOKEN and GHL_LOCATION_ID, from the environment or from a .env file (--env, default
.env in the current folder). The token is never taken as a command-line argument and is never printed.
It goes online to GoHighLevel's API (services.leadconnectorhq.com) and nowhere else. Standard library only.
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIST = HERE.parent / "references" / "ghl-placeholders.json"
API = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28"
# "YOUR NAME", "YOUR-LINK": a blank left in capitals. The ordinary word "your" is not one, so that part is case-sensitive.
LEFTOVER = re.compile(r"\[needs you|\[draft\]|\[reviewed draft\]|\[file:|\[hypothesis\]|\{\{|\}\}|\bTBD\b|lorem ipsum|(?-i:\bYOUR[- ][A-Z])", re.I)


def spec():
    try:
        d = json.loads(LIST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read the list of values ({LIST}): {e}")
    return d, {p["key"]: p for p in d["placeholders"]}


def read_env(path):
    out = {}
    p = Path(path)
    if p.is_file():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
            if m and not line.lstrip().startswith("#"):
                out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


def account(a):
    env = read_env(a.env)
    token = os.environ.get("GHL_TOKEN") or env.get("GHL_TOKEN")
    loc = os.environ.get("GHL_LOCATION_ID") or env.get("GHL_LOCATION_ID")
    if not token or not loc:
        sys.exit("No GoHighLevel connection found. This needs GHL_TOKEN and GHL_LOCATION_ID, in the environment or in the .env file "
                 f"({a.env}). The member adds them themselves; never ask them to paste a token into the chat.")
    if not re.fullmatch(r"[A-Za-z0-9]{10,40}", loc):
        sys.exit("GHL_LOCATION_ID does not look like a location id (the string after /location/ in the account's web address).")
    return token, loc, (os.environ.get("GHL_API_BASE") or env.get("GHL_API_BASE") or API).rstrip("/")


class Refused(Exception):
    pass


def call(base, token, method, path, body=None, tries=4):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(tries):
        req = urllib.request.Request(base + path, data=data, method=method, headers={
            "Authorization": "Bearer " + token, "Version": VERSION, "Accept": "application/json", "Content-Type": "application/json",
            "User-Agent": "BuildRoomOS-push/1"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(2 + 3 * attempt)
                continue
            try:
                msg = json.loads(text).get("message", text)
            except ValueError:
                msg = text
            raise Refused(f"{e.code}: {msg}")
        except (urllib.error.URLError, OSError) as e:
            if attempt == tries - 1:
                raise Refused(f"could not reach GoHighLevel: {e}")
            time.sleep(2 + 3 * attempt)
    raise Refused("GoHighLevel kept answering 'too busy'. Wait a minute and run it again; values already written stay written.")


def plain(msg):
    """A refusal in words a member can act on."""
    if msg.startswith("401") or "Invalid" in msg and "token" in msg.lower():
        return "GoHighLevel did not accept the token. It may have been rotated or deleted: the member makes a new one and saves it again."
    if msg.startswith("403") and "location" in msg.lower():
        return "This token belongs to a different sub-account than GHL_LOCATION_ID names. Check both were taken from the same account."
    if msg.startswith("403") or "scope" in msg.lower():
        return "The token is not allowed to do this. It needs View and Edit Custom Values (and View Locations). The member edits the integration's scopes."
    return msg


def load_values(folder):
    f = Path(folder) / "custom_values.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except OSError:
        sys.exit(f"No custom_values.json in {folder}. Run ghl_values.py export first.")
    except ValueError as e:
        sys.exit(f"custom_values.json is not valid JSON: {e}")
    if not isinstance(d.get("values"), dict):
        sys.exit("custom_values.json has no values. Run ghl_values.py export again.")
    return d


def problems(d, known):
    """The file is checked again here, because it may have been edited since it was exported."""
    out = []
    for key, v in d["values"].items():
        p = known.get(key)
        if not p:
            out.append(f"{key}: not a value the snapshot has")
        elif not isinstance(v, str) or not v.strip():
            out.append(f"{key}: empty. A value is left out, not sent empty")
        elif p.get("max") and len(v) > p["max"]:
            out.append(f"{key}: {len(v)} characters, and the page element holds {p['max']}")
        elif LEFTOVER.search(v):
            out.append(f"{key}: still carries a tag or a blank to fill ({LEFTOVER.search(v).group(0)})")
        elif p["type"] == "url" and not re.fullmatch(r"https://\S+\.\S+", v):
            out.append(f"{key}: needs a full https:// link")
    return out


def existing(base, token, loc):
    got = call(base, token, "GET", f"/locations/{loc}/customValues").get("customValues") or []
    return {x.get("name"): x for x in got if isinstance(x, dict)}


def make_plan(d, known, have):
    create, update, same = [], [], []
    for key in known:                                     # the snapshot's own order
        if key not in d["values"]:
            continue
        v = d["values"][key]
        cur = have.get(key)
        if not cur:
            create.append(key)
        elif (cur.get("value") or "") != v:
            update.append(key)
        else:
            same.append(key)
    return create, update, same


def describe(d, sp, known, have, create, update, same, loc_name):
    lines = [f"Account: {loc_name}.", f"Values in the file: {len(d['values'])} of {len(known)}. " + ("Every must-have is there." if d.get("complete") else "The file is marked NOT complete: a must-have is missing.")]
    ours = [n for n in have if isinstance(n, str) and n.startswith(sp["prefix"])]
    acct_ver = (have.get(sp["version_key"]) or {}).get("value")
    if not ours:
        lines.append("LOOK  This account has no Build Room values yet, so the Build Room snapshot is probably not loaded. The values can be written, "
                     "but no page, email or form will show them until the snapshot is in the account.")
    elif acct_ver and str(acct_ver) != str(d.get("snapshot_version")):
        lines.append(f"LOOK  The account's snapshot is version {acct_ver} and this file was made for version {d.get('snapshot_version')}. Check with the host before pushing.")
    lines.append(f"Would create {len(create)}, update {len(update)}, leave {len(same)} as they are. Nothing is deleted.")
    for key in update:
        old = (have[key].get("value") or "").replace("\n", " ")
        new = d["values"][key].replace("\n", " ")
        lines.append(f"  change  {known[key]['label']} ({key})\n          now:  {old[:110]}{'…' if len(old) > 110 else ''}\n          to:   {new[:110]}{'…' if len(new) > 110 else ''}")
    for key in create:
        new = d["values"][key].replace("\n", " ")
        lines.append(f"  add     {known[key]['label']} ({key}): {new[:110]}{'…' if len(new) > 110 else ''}")
    left = [n for n in ours if n not in d["values"] and n != sp["version_key"]]
    if left:
        lines.append(f"Already in the account and not in this file ({len(left)}): left exactly as they are.")
    return lines


def setup(a):
    sp, known = spec()
    d = load_values(a.folder)
    probs = problems(d, known)
    if probs:
        for x in probs:
            print("FIX  " + x)
        sys.exit(f"{len(probs)} thing(s) to fix in custom_values.json. Fix the values, run ghl_values.py check and export again, then come back.")
    token, loc, base = account(a)
    try:
        info = call(base, token, "GET", f"/locations/{loc}")
        have = existing(base, token, loc)
    except Refused as e:
        sys.exit("Stopped: " + plain(str(e)))
    name = ((info.get("location") or info).get("name") or "unnamed account") + f" ({loc})"
    return sp, known, d, token, loc, base, have, name


def cmd_plan(a):
    sp, known, d, _t, _l, _b, have, name = setup(a)
    create, update, same = make_plan(d, known, have)
    print("\n".join(describe(d, sp, known, have, create, update, same, name)))
    print("\nNothing was changed. Show this to the member. On their go-ahead: ghl_push.py push " + str(a.folder) + " --yes")


def cmd_push(a):
    sp, known, d, token, loc, base, have, name = setup(a)
    if not d.get("complete") and not a.partial:
        sys.exit("The file is marked not complete: a must-have value is missing, so a page would show a blank. Get the missing values from the member, "
                 "or, if they want what is ready pushed now, run again with --partial.")
    create, update, same = make_plan(d, known, have)
    if not a.yes:
        print("\n".join(describe(d, sp, known, have, create, update, same, name)))
        sys.exit("\nNothing was changed. This writes into the member's live account: run it with --yes only after they have seen the plan and said go.")
    done, failed = [], []
    for key in create + update:
        body = {"name": key, "value": d["values"][key]}
        try:
            if key in have:
                call(base, token, "PUT", f"/locations/{loc}/customValues/{have[key]['id']}", body)
            else:
                call(base, token, "POST", f"/locations/{loc}/customValues", body)
            done.append(key)
        except Refused as e:
            failed.append((key, plain(str(e))))
            if str(e).startswith(("401", "403")):
                break                                    # the token is the problem; every further call would fail the same way
        time.sleep(a.pause)
    # GoHighLevel's list lags a few seconds behind a write, so read back patiently before calling anything missing.
    wrong = list(done)
    for wait in (3, 5, 8, 12):
        if not wrong:
            break
        time.sleep(wait * (0 if a.pause == 0 else 1))
        try:
            now = existing(base, token, loc)
        except Refused:
            continue
        wrong = [k for k in done if (now.get(k) or {}).get("value") != d["values"][k]]
    confirmed = [k for k in done if k not in wrong]
    report = {"account": name, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "snapshot_version": d.get("snapshot_version"),
              "complete_file": bool(d.get("complete")), "created": [k for k in create if k in confirmed], "updated": [k for k in update if k in confirmed],
              "unchanged": same, "not_confirmed": wrong, "failed": [{"key": k, "why": w} for k, w in failed]}
    out = Path(a.folder)
    (out / "push_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    md = ["# GoHighLevel push: what happened", "", f"Account: {name}. {report['at']}.", "",
          f"**{len(confirmed)} value{'' if len(confirmed) == 1 else 's'} written and read back from the account.** {len(same)} already right and not touched. Nothing was deleted.", ""]
    if failed:
        md += ["## Not written", ""] + [f"- **{known[k]['label']}** (`{k}`): {w}" for k, w in failed] + [""]
    if wrong:
        md += ["## Written, but the account did not show it when read back", "", "Open the account's custom values and look at these by hand:", ""] + [f"- **{known[k]['label']}** (`{k}`)" for k in wrong] + [""]
    md += ["## What this did not do", "", "- It did not publish a page, send an email or switch a workflow on.", "- It did not touch any value outside the Build Room list.", "",
           "## What only you can do", "", "- Open each page in the account and read it with your values in place.", "- Connect your domain and your sending address.",
           "- Set your calendar hours.", "- Send yourself a test before you turn any workflow on.", ""]
    (out / "GHL_Push_Report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(confirmed)} written and confirmed, {len(same)} already right, {len(wrong)} not confirmed, {len(failed)} failed. Report: {out / 'GHL_Push_Report.md'}")
    for k, w in failed:
        print(f"FAILED  {k}: {w}")
    sys.exit(1 if failed or wrong else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("plan", cmd_plan), ("push", cmd_push)):
        p = sub.add_parser(name)
        p.add_argument("folder")
        p.add_argument("--env", default=".env")
        if name == "push":
            p.add_argument("--yes", action="store_true", help="the member has seen the plan and said go")
            p.add_argument("--partial", action="store_true", help="push what is ready although a must-have is missing; the member's choice")
            p.add_argument("--pause", type=float, default=0.15, help=argparse.SUPPRESS)
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
