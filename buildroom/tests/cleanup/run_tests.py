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
    for spot in (".claude/skills", ".codex/skills", ".agents/skills", "skills"):
        for n in ("buildroom-os", "buildroom-offer-page-copy"):
            tool(w / spot, n)
    for spot in (".claude/skills", ".codex/skills", ".agents/skills"):
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
    for rel in ("Offer_Page.md", "discovery/ledger.json", "backups/BUILDROOM_BUSINESS_FILE-2026-11-01.md", "VAULT.md", "tools/Rent_Calculator.html"):
        (w / rel).parent.mkdir(parents=True, exist_ok=True)
        (w / rel).write_text("mine")
    zip_guide = (ROOT / "rollout/universal/CLAUDE.md").read_text()
    (w / "CLAUDE.md").write_text(zip_guide)
    (w / "AGENTS.md").write_text(zip_guide)
    sha = hashlib.sha256(bf.read_bytes()).hexdigest()
    before = tree(tmp)

    # ---- dry run changes nothing ------------------------------------------------------------
    code, out = run(home, "--folder", w, "--home")
    check("dry run: finds the zip copies in the folder and the whole-computer install", code == 0 and "Found 11 old local copies" in out, out)
    check("dry run: changes nothing and says so", tree(tmp) == before and "Nothing has been changed" in out and "Nothing is deleted" in out)
    code, out = run(home, "--folder", w)
    check("without --home it only looks in the folder", "Found 8 old local copies" in out)

    # ---- apply --------------------------------------------------------------------------------
    code, out = run(home, "--folder", w, "--home", "--apply")
    dest = w / "backups" / f"old-buildroom-tools-{date.today().isoformat()}"
    check("apply: moves all eleven and reports it", code == 0 and "Moved 11 to" in out, out)
    check("apply: Codex's folders are covered, in the folder and for the whole computer",
          (dest / "this-folder/agents-skills/buildroom-os/SKILL.md").exists() and (dest / "this-folder/codex-skills/buildroom-os/SKILL.md").exists()
          and (dest / "whole-computer/agents-skills/buildroom-os/SKILL.md").exists() and not list((w / ".agents/skills").glob("buildroom-*"))
          and not list((home / ".agents/skills").glob("buildroom-*")) and not list((home / ".codex/skills").glob("buildroom-*")))
    for g in ("CLAUDE.md", "AGENTS.md"):
        now = (w / g).read_text()
        check(f"apply: {g} gains one line saying the tools come from the connector, and keeps everything else",
              now.startswith("> **Build Room tools now come from the Build Room OS connector.**") and now.endswith(zip_guide) and now.count("\n") == zip_guide.count("\n") + 2)
        check(f"apply: the original {g} is kept in the backup", (dest / "this-folder" / g).read_text() == zip_guide)
    check("apply: says the two instruction files were noted", "Added a note to CLAUDE.md and AGENTS.md" in out)
    check("apply: no Build Room tool is left where Claude or Codex would find it",
          not any((d / s).glob("buildroom-*/SKILL.md") and list((d / s).glob("buildroom-os")) for d, ss in ((w, (".claude/skills", ".codex/skills", "skills")), (home, (".claude/skills", ".codex/skills"))) for s in ss))
    check("apply: every copy is in the backup folder, whole, sorted by where it came from",
          (dest / "this-folder/claude-skills/buildroom-os/references/a.md").read_text() == "ref"
          and (dest / "this-folder/skills/buildroom-offer-page-copy/SKILL.md").exists()
          and (dest / "whole-computer/codex-skills/buildroom-os/SKILL.md").exists())
    check("apply: the Business File is byte for byte the same, and the script says so", hashlib.sha256(bf.read_bytes()).hexdigest() == sha and "BUILDROOM_BUSINESS_FILE.md: not touched." in out)
    check("apply: the member's own work, old backups and other files are untouched",
          all((w / r).read_text() == "mine" for r in ("Offer_Page.md", "discovery/ledger.json", "backups/BUILDROOM_BUSINESS_FILE-2026-11-01.md", "VAULT.md", "tools/Rent_Calculator.html")))
    check("apply: skills that are not Build Room tools stay put", (home / ".claude/skills/my-own-skill/SKILL.md").exists() and (w / ".claude/skills/not-buildroom/SKILL.md").exists())
    check("apply: a folder that only looks like a tool is left alone", (w / "skills/buildroom-notes/ideas.md").read_text() == "my notes, not a tool" and (w / "skills/buildroom-fake/SKILL.md").exists())
    check("apply: nothing was deleted (same files, new places, plus the two kept originals)", len(tree(tmp)) == len(before) + 2)
    check("apply: says how to undo", "To undo, move the folders back" in out)
    code, out = run(home, "--folder", w, "--home", "--apply")
    check("apply: running it again finds nothing and does nothing", code == 0 and "Nothing to do" in out
          and (w / "AGENTS.md").read_text().count("Build Room tools now come from") == 1)
    w4 = tmp / "home/Mine"
    tool(w4 / ".agents/skills", "buildroom-os")
    (w4 / "AGENTS.md").write_text("# My own project rules\nBe kind.\n")
    code, out = run(home, "--folder", w4, "--apply")
    check("apply: an AGENTS.md the member wrote themselves is never edited", code == 0 and (w4 / "AGENTS.md").read_text() == "# My own project rules\nBe kind.\n" and "Added a note" not in out)

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
    check("connector: says its version is the current one and wins over a local copy", "the current version of every Build Room session" in ins and "instead of any local skill named buildroom-*" in ins)
    check("connector: tells Claude to check once, ask once, and move the copies for the member", "Once per conversation" in ins and "ask the member once" in ins and "move the old copies into a backup folder for them" in ins)
    check("connector: never delete, never touch the Business File, silent when there is nothing", "Never delete them" in ins and "never touch the Business File" in ins and "say nothing about it" in ins)
    check("connector: names every place Claude and Codex look for tools", all(x in ins for x in (".claude/skills", ".codex/skills", ".agents/skills", "skills in the working folder", "home folder")))
    first = ins[:512]
    check("connector: the first 512 characters stand alone (Codex leans on them)", all(x in first for x in (
        "buildroom_list_sessions", "buildroom_start_session", "instead of any local skill named buildroom-*", "older copy", "stays on their computer", "never send it here")), first)
    ref = (ROOT / "skills/buildroom-os/references/connector-cleanup.md").read_text()
    check("procedure: one plain question that promises nothing is deleted or touched", "nothing is deleted. OK to do that?" in ref and "Your Business File and everything you have made stay exactly where they are" in ref)
    check("procedure: a no is respected and not asked again", "do not ask again in this conversation" in ref and "One ask. Never nag." in ref)
    check("procedure: nothing to check in a regular chat", "In a regular chat there are no local copies" in ref)
    check("procedure: the connector's version is used either way", "use the connector's" in ref and "even if a local skill of the same name has already loaded" in ref)
    check("procedure: no long dashes", "—" not in ref and "–" not in ref)
    check("procedure: covers Codex by name, its folders and its permission prompt", "Codex in a terminal, the IDE extension or the desktop app" in ref
          and "Codex looks in `.codex` and `.agents`" in ref and "Codex asks before writing outside the working folder" in ref and "no Python on this computer" in ref)
    check("procedure: the one-line note in CLAUDE.md and AGENTS.md is explained", "adds one line to the top of the zip's own `CLAUDE.md` and `AGENTS.md`" in ref)
    check("navigator: points to the procedure", "references/connector-cleanup.md" in (ROOT / "skills/buildroom-os/SKILL.md").read_text())
    check("start page: tells zip members they need do nothing but say yes", "Claude or Codex offers to move the old copies into a backup folder. Say yes." in (ROOT / "connector/start.html").read_text())

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
