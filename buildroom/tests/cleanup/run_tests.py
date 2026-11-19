#!/usr/bin/env python3
"""Moving old zip copies of the tools aside so the connector's versions are the only ones used.

Usage:  python3 buildroom/tests/cleanup/run_tests.py
"""
import hashlib, os, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/buildroom-os/scripts/retire_local_copies.py"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))


def run(home, *args):
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def tool(d, name):
    (d / name / "references").mkdir(parents=True)
    (d / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: x\n---\n# old\n")
    (d / name / "references/a.md").write_text("ref")


def tree(d):
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())


def main():
    tmp = Path(tempfile.mkdtemp())
    home, w = tmp / "home", tmp / "home/Documents/BuildRoom_OS"
    w.mkdir(parents=True)
    for spot in (".claude/skills", ".codex/skills", "skills"):
        for n in ("buildroom-os", "buildroom-offer-page-copy"):
            tool(w / spot, n)
    for spot in (".claude/skills", ".codex/skills"):
        tool(home / spot, "buildroom-os")
        tool(home / spot, "my-own-skill")
    (w / ".claude/skills/not-buildroom").mkdir()
    (w / ".claude/skills/not-buildroom/SKILL.md").write_text("---\nname: not-buildroom\n---\n")
    (w / "skills/buildroom-notes").mkdir()
    (w / "skills/buildroom-notes/ideas.md").write_text("my notes, not a tool")
    (w / "skills/buildroom-fake").mkdir()
    (w / "skills/buildroom-fake/SKILL.md").write_text("---\nname: something-else\n---\n")
    bf = w / "BUILDROOM_BUSINESS_FILE.md"
    bf.write_text("# My business\n- **What I do:** coaching\n")
    for rel in ("Offer_Page.md", "discovery/ledger.json", "backups/BUILDROOM_BUSINESS_FILE-2026-11-01.md", "CLAUDE.md", "tools/Rent_Calculator.html"):
        (w / rel).parent.mkdir(parents=True, exist_ok=True)
        (w / rel).write_text("mine")
    sha = hashlib.sha256(bf.read_bytes()).hexdigest()
    before = tree(tmp)

    # ---- dry run changes nothing ------------------------------------------------------------
    code, out = run(home, "--folder", w, "--home")
    check("dry run: finds the zip copies in the folder and the whole-computer install", code == 0 and "Found 8 old local copies" in out, out)
    check("dry run: changes nothing and says so", tree(tmp) == before and "Nothing has been changed" in out and "Nothing is deleted" in out)
    code, out = run(home, "--folder", w)
    check("without --home it only looks in the folder", "Found 6 old local copies" in out)

    # ---- apply --------------------------------------------------------------------------------
    code, out = run(home, "--folder", w, "--home", "--apply")
    dest = w / "backups" / f"old-buildroom-tools-{date.today().isoformat()}"
    check("apply: moves all eight and reports it", code == 0 and "Moved 8 to" in out, out)
    check("apply: no Build Room tool is left where Claude or Codex would find it",
          not any((d / s).glob("buildroom-*/SKILL.md") and list((d / s).glob("buildroom-os")) for d, ss in ((w, (".claude/skills", ".codex/skills", "skills")), (home, (".claude/skills", ".codex/skills"))) for s in ss))
    check("apply: every copy is in the backup folder, whole, sorted by where it came from",
          (dest / "this-folder/claude-skills/buildroom-os/references/a.md").read_text() == "ref"
          and (dest / "this-folder/skills/buildroom-offer-page-copy/SKILL.md").exists()
          and (dest / "whole-computer/codex-skills/buildroom-os/SKILL.md").exists())
    check("apply: the Business File is byte for byte the same, and the script says so", hashlib.sha256(bf.read_bytes()).hexdigest() == sha and "BUILDROOM_BUSINESS_FILE.md: not touched." in out)
    check("apply: the member's own work, old backups and other files are untouched",
          all((w / r).read_text() == "mine" for r in ("Offer_Page.md", "discovery/ledger.json", "backups/BUILDROOM_BUSINESS_FILE-2026-11-01.md", "CLAUDE.md", "tools/Rent_Calculator.html")))
    check("apply: skills that are not Build Room tools stay put", (home / ".claude/skills/my-own-skill/SKILL.md").exists() and (w / ".claude/skills/not-buildroom/SKILL.md").exists())
    check("apply: a folder that only looks like a tool is left alone", (w / "skills/buildroom-notes/ideas.md").read_text() == "my notes, not a tool" and (w / "skills/buildroom-fake/SKILL.md").exists())
    check("apply: nothing was deleted (same files, new places)", len(tree(tmp)) == len(before))
    check("apply: says how to undo", "To undo, move the folders back" in out)
    code, out = run(home, "--folder", w, "--home", "--apply")
    check("apply: running it again finds nothing and does nothing", code == 0 and "Nothing to do" in out)

    # ---- edges -----------------------------------------------------------------------------------
    w2 = tmp / "home/Other"
    (w2 / ".claude/skills").mkdir(parents=True)
    real = tmp / "elsewhere/buildroom-os"
    tool(tmp / "elsewhere", "buildroom-os")
    os.symlink(real, w2 / ".claude/skills/buildroom-os")
    code, out = run(home, "--folder", w2)
    check("a linked folder is never followed or moved", "Nothing to do" in out and real.exists())
    check("a missing folder is refused", run(home, "--folder", tmp / "nope")[0] != 0)
    w3 = tmp / "home/NoFile"
    tool(w3 / "skills", "buildroom-os")
    code, out = run(home, "--folder", w3, "--apply")
    check("a folder with no Business File still works and says there is none", code == 0 and "none in this folder" in out)
    src = SCRIPT.read_text()
    check("script: never deletes, never goes online", not any(x in src for x in ("rmtree", ".unlink(", "os.remove", "urllib", "requests", "socket")))

    # ---- the instructions that make Claude do it for the member ---------------------------------
    sys.path.insert(0, str(ROOT / "connector"))
    import server
    ins = server.INSTRUCTIONS
    check("connector: says its version is the current one and wins over a local copy", "always holds the current version" in ins and "use this one" in ins)
    check("connector: tells Claude to check once, ask once, and move the copies for the member", "Once per conversation" in ins and "ask the member once" in ins and "move the old copies into a backup folder for them" in ins)
    check("connector: never delete, never touch the Business File, silent when there is nothing", "Never delete them" in ins and "never touch the Business File" in ins and "say nothing about it" in ins)
    check("connector: names all five places the zip put tools", all(x in ins for x in (".claude/skills", ".codex/skills", "skills in the working folder", "home folder")))
    ref = (ROOT / "skills/buildroom-os/references/connector-cleanup.md").read_text()
    check("procedure: one plain question that promises nothing is deleted or touched", "nothing is deleted. OK to do that?" in ref and "Your Business File and everything you have made stay exactly where they are" in ref)
    check("procedure: a no is respected and not asked again", "do not ask again in this conversation" in ref and "One ask. Never nag." in ref)
    check("procedure: nothing to check in a regular chat", "In a regular chat there are no local copies" in ref)
    check("procedure: the connector's version is used either way", "use the connector's" in ref and "even if a local skill of the same name has already loaded" in ref)
    check("procedure: no long dashes", "—" not in ref and "–" not in ref)
    check("navigator: points to the procedure", "references/connector-cleanup.md" in (ROOT / "skills/buildroom-os/SKILL.md").read_text())
    check("start page: tells zip members they need do nothing but say yes", "Claude offers to move the old copies into a backup folder. Say yes." in (ROOT / "connector/start.html").read_text())

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
