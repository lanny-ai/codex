#!/usr/bin/env python3
"""Move old local copies of the Build Room tools aside, so the connector's current versions are the only ones used.

  retire_local_copies.py [--folder DIR] [--home]            show what would be moved (changes nothing)
  retire_local_copies.py [--folder DIR] [--home] --apply    move them into DIR/backups/old-buildroom-tools-DATE/

It only moves folders named buildroom-* that hold a SKILL.md, and only from the places the zip put them:
  DIR/.claude/skills, DIR/.codex/skills, DIR/skills, and with --home: ~/.claude/skills, ~/.codex/skills.
Nothing is deleted. The Business File and everything the member made are never touched.
Standard library only.
"""
import argparse, hashlib, shutil, sys
from datetime import date
from pathlib import Path

SPOTS = (".claude/skills", ".codex/skills", "skills")
HOME_SPOTS = (".claude/skills", ".codex/skills")
BUSINESS_FILE = "BUILDROOM_BUSINESS_FILE.md"


def is_tool(p):
    if p.is_symlink() or not p.is_dir() or not p.name.startswith("buildroom-"):
        return False
    md = p / "SKILL.md"
    try:
        return md.is_file() and f"name: {p.name}" in md.read_text(encoding="utf-8", errors="replace")[:400]
    except OSError:
        return False


def find(folder, home):
    out = []
    for base, spots, label in ((folder, SPOTS, "this-folder"), (Path.home(), HOME_SPOTS if home else (), "whole-computer")):
        for spot in spots:
            d = base / spot
            if d.is_dir() and not d.is_symlink():
                out += [(p, f"{label}/{spot.replace('/', '-').lstrip('.')}") for p in sorted(d.iterdir()) if is_tool(p)]
    return out


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=".")
    ap.add_argument("--home", action="store_true", help="also look in the places the zip's installer copied tools to for the whole computer")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    folder = Path(a.folder).expanduser().resolve()
    if not folder.is_dir():
        sys.exit(f"Not a folder: {folder}")
    found = find(folder, a.home)
    if not found:
        print("No old local copies of the Build Room tools were found. Nothing to do.")
        return
    places = sorted({str(p.parent) for p, _ in found})
    print(f"Found {len(found)} old local copies of Build Room tools in:")
    for pl in places:
        print(f"  {pl}  ({sum(1 for p, _ in found if str(p.parent) == pl)})")
    dest = folder / "backups" / f"old-buildroom-tools-{date.today().isoformat()}"
    if not a.apply:
        print(f"\nNothing has been changed. With --apply they are moved to:\n  {dest}\nNothing is deleted. {BUSINESS_FILE} and your own work are not touched.")
        return
    bf = folder / BUSINESS_FILE
    before = digest(bf)
    moved, failed = 0, []
    for p, label in found:
        target = dest / label / p.name
        try:
            if target.exists():
                raise OSError("already in the backup folder")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(target))
            moved += 1
        except OSError as e:
            failed.append(f"{p}: {e}")
    if digest(bf) != before:
        sys.exit(f"STOP: {BUSINESS_FILE} changed during the move. That should be impossible. Check {bf} against your backups before doing anything else.")
    print(f"\nMoved {moved} to {dest}")
    print(f"{BUSINESS_FILE}: " + ("not touched." if before else "none in this folder."))
    if failed:
        print(f"\nCould not move {len(failed)}:")
        for f in failed:
            print(f"  {f}")
        sys.exit(1)
    print("From now on every Build Room tool comes from the connector, always the newest version.")
    print("To undo, move the folders back from the backup folder.")


if __name__ == "__main__":
    main()
