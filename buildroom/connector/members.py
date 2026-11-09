#!/usr/bin/env python3
"""Manage the pilot member list for the Build Room connector.

    python3 members.py add someone@example.com [--until 2026-12-31] [--name "First name"]
    python3 members.py list
    python3 members.py lapse someone@example.com      # access stops on their next request
    python3 members.py reactivate someone@example.com [--until YYYY-MM-DD]
    python3 members.py new-key someone@example.com    # replaces a lost or shared key
    python3 members.py remove someone@example.com

A new access key is printed once and never stored: members.json keeps only its sha256.
Give the member their connector link and key privately. members.json is not committed.
"""
import argparse, hashlib, json, secrets, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    p = Path(path)
    if not p.exists():
        return {"source": "allowlist", "grace_days": 7, "members": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save(path, data):
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(p)
    try:
        p.chmod(0o600)
    except OSError:
        pass


def find(data, email):
    e = email.strip().lower()
    for m in data["members"]:
        if m["email"] == e:
            return m
    return None


def new_key():
    return "br_" + secrets.token_urlsafe(24)


def show_key(email, key, base_url):
    print(f"\nAccess key for {email} (shown once, not stored):\n  {key}\n")
    print("Claude Code:")
    print(f'  claude mcp add --transport http buildroom {base_url}/mcp --header "Authorization: Bearer {key}"')
    print("Claude desktop or claude.ai: Settings > Connectors > Add custom connector, URL:")
    print(f"  {base_url}/mcp/{key}")


def valid_date(s):
    date.fromisoformat(s)
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--members", default=str(HERE / "members.json"))
    ap.add_argument("--base-url", default="https://YOUR-CONNECTOR-HOST")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("email"); a.add_argument("--until", type=valid_date); a.add_argument("--name", default="")
    sub.add_parser("list")
    for c in ("lapse", "remove", "new-key"):
        sub.add_parser(c).add_argument("email")
    r = sub.add_parser("reactivate"); r.add_argument("email"); r.add_argument("--until", type=valid_date)
    args = ap.parse_args(argv)
    data = load(args.members)

    if args.cmd == "list":
        if not data["members"]:
            print("No members yet.")
        for m in data["members"]:
            print(f"{m['email']:<40} {m['status']:<8} until {m.get('current_until') or '-':<10} added {m['added']}")
        return 0

    email = args.email.strip().lower()
    if "@" not in email:
        print("That does not look like an email address."); return 1
    m = find(data, email)

    if args.cmd == "add":
        if m:
            print(f"{email} is already on the list ({m['status']}). Use reactivate or new-key."); return 1
        key = new_key()
        data["members"].append({"email": email, "name": args.name, "key_sha256": hashlib.sha256(key.encode()).hexdigest(),
                                "status": "active", "current_until": args.until, "added": date.today().isoformat()})
        save(args.members, data); show_key(email, key, args.base_url); return 0
    if not m:
        print(f"{email} is not on the list."); return 1
    if args.cmd == "lapse":
        m["status"] = "lapsed"; save(args.members, data); print(f"{email}: lapsed. Access stops on their next request."); return 0
    if args.cmd == "reactivate":
        m["status"] = "active"
        if args.until:
            m["current_until"] = args.until
        save(args.members, data); print(f"{email}: active again, same key."); return 0
    if args.cmd == "new-key":
        key = new_key(); m["key_sha256"] = hashlib.sha256(key.encode()).hexdigest()
        save(args.members, data); print("The old key stops working now."); show_key(email, key, args.base_url); return 0
    if args.cmd == "remove":
        data["members"] = [x for x in data["members"] if x["email"] != email]
        save(args.members, data); print(f"{email}: removed."); return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
