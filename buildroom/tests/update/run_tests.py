#!/usr/bin/env python3
"""Safety tests: a release update never touches a member's Business File or their own files,
and the Continuity System never writes the Business File.

Usage:  python3 buildroom/tests/update/run_tests.py
"""
import sys
sys.dont_write_bytecode = True  # noqa: E402  (no __pycache__ anywhere under buildroom/)
import hashlib, os, re, shutil, subprocess, tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]          # buildroom/
UNI = ROOT / "rollout" / "universal"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"   [{detail}]"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree(folder, skip=("backups",)):
    """Map of relative path -> sha256 for every file under folder, skipping top-level names in skip."""
    out = {}
    for p in sorted(Path(folder).rglob("*")):
        rel = p.relative_to(folder)
        if rel.parts[0] in skip or not p.is_file():
            continue
        out[str(rel)] = sha(p)
    return out


def stage_release(dest):
    """A release folder laid out exactly as build-universal-bundle.sh lays out the zip."""
    r = Path(dest) / "BuildRoom_OS"
    for loc in ("skills", ".claude/skills", ".codex/skills"):
        (r / loc).mkdir(parents=True)
        for d in sorted((ROOT / "skills").iterdir()):
            if d.is_dir():
                shutil.copytree(d, r / loc / d.name, ignore=shutil.ignore_patterns("__pycache__"))
    (r / "tools").mkdir()
    for f in ("Rent_Calculator.html", "Brainstorm_Board.html", "Business_File_Viewer.html", "BuildRoom_OS_Quick_Start.html"):
        shutil.copy(ROOT / "rollout" / f, r / "tools" / f)
    shutil.copy(ROOT / "rollout" / "BuildRoom_OS_Say_These_Words.pdf", r)
    (r / "templates").mkdir()
    shutil.copy(ROOT / "templates" / "BUILDROOM_BUSINESS_FILE.md", r / "templates" / "BUILDROOM_BUSINESS_FILE_TEMPLATE.md")
    for f in ("START-HERE.md", "install.sh", "install.ps1", "update.sh", "update.ps1"):
        shutil.copy(UNI / f, r / f)
    shutil.copy(UNI / "CLAUDE.md", r / "CLAUDE.md")
    shutil.copy(UNI / "CLAUDE.md", r / "AGENTS.md")
    return r


FILLED = """# Build Room Business File

**Owner:** Test Owner
**Business:** Example Advisory
**File version:** 1.4
**Last updated:** 2026-10-01 by Signature Offer

## 1. Business Snapshot
- **What we do:** bookkeeping clean-ups for small firms (member hand edit, keep)
## 8. Session Log
| 2026-09-01 | Signature Offer | offer | complete | 5 | |
"""


def make_member_folder(dest, with_bf=True, name="My Build Room"):
    """An existing member folder from an older release, with their own work in it."""
    m = Path(dest) / name
    for loc in ("skills", ".claude/skills", ".codex/skills"):
        (m / loc / "buildroom-os").mkdir(parents=True)
        (m / loc / "buildroom-os" / "SKILL.md").write_text("old navigator\n")
        (m / loc / "buildroom-video-engine").mkdir()          # a skill since retired upstream
        (m / loc / "buildroom-video-engine" / "SKILL.md").write_text("retired skill\n")
    (m / ".claude/skills/my-own-skill").mkdir()
    (m / ".claude/skills/my-own-skill/SKILL.md").write_text("the member's own skill\n")
    if with_bf:
        (m / "BUILDROOM_BUSINESS_FILE.md").write_text(FILLED)
    (m / "CLAUDE.md").write_text("old instructions\n")
    (m / "Offer_Page.md").write_text("the member's offer page\n")
    for rel, body in (("launches/2026-10-camp/close.md", "close\n"), ("search/questions.json", "{}\n"),
                      ("proof/bank.md", "proof\n"), ("projects/book/continuity/STATE.md", "# STATE: book\n"),
                      ("ads/2026-10/kit.md", "ads\n"), (".env", "KIE_API_KEY=not-a-real-key\n")):
        (m / rel).parent.mkdir(parents=True, exist_ok=True)
        (m / rel).write_text(body)
    return m


def run_update(release, target):
    return subprocess.run(["bash", str(release / "update.sh"), str(target)], capture_output=True, text=True)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="br update test "))   # a space in the path on purpose
    try:
        # ---- the zip itself ------------------------------------------------------------
        bundle = (ROOT / "build-universal-bundle.sh").read_text()
        check("zip: the blank file ships only as templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md",
              'templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md"' in bundle and 'cp templates/BUILDROOM_BUSINESS_FILE.md "$STAGE/"' not in bundle)
        check("zip: the build refuses if BUILDROOM_BUSINESS_FILE.md is ever in the zip",
              'BUILDROOM_BUSINESS_FILE.md must not be in the zip' in bundle)
        check("zip: update.sh and update.ps1 ship in the zip", "rollout/universal/update.sh rollout/universal/update.ps1" in bundle)
        rel = ROOT / "rollout" / "releases"
        newest = sorted(rel.glob("BuildRoom_OS_*.zip"))[-1]
        names = subprocess.run(["unzip", "-Z1", str(newest)], capture_output=True, text=True).stdout.split()
        check(f"zip: the newest release ({newest.name}) carries no BUILDROOM_BUSINESS_FILE.md",
              "BuildRoom_OS/BUILDROOM_BUSINESS_FILE.md" not in names, newest.name)

        release = stage_release(tmp / "Downloads")
        check("staged release has no Business File at its top level", not (release / "BUILDROOM_BUSINESS_FILE.md").exists())

        # ---- a normal update ------------------------------------------------------------
        m = make_member_folder(tmp / "Documents")
        before = tree(m)
        bf_before = sha(m / "BUILDROOM_BUSINESS_FILE.md")
        p = run_update(release, m)
        check("update: exits 0", p.returncode == 0, p.stdout + p.stderr)
        check("update: Business File byte-for-byte unchanged", sha(m / "BUILDROOM_BUSINESS_FILE.md") == bf_before)
        check("update: says the Business File was not touched", "Your Business File was not touched" in p.stdout, p.stdout)
        after = tree(m)
        mine = [k for k in before if not re.match(r"(skills|\.claude/skills|\.codex/skills)/buildroom-|CLAUDE\.md$|AGENTS\.md$", k)]
        changed = [k for k in mine if after.get(k) != before[k]]
        check("update: every member file (offer page, launches, search, proof, projects, ads, .env, own skill) unchanged",
              not changed and len(mine) >= 9, changed)
        check("update: the member's own skill is untouched", (m / ".claude/skills/my-own-skill/SKILL.md").read_text() == "the member's own skill\n")
        check("update: Build Room skills replaced with the release's",
              sha(m / ".claude/skills/buildroom-os/SKILL.md") == sha(ROOT / "skills/buildroom-os/SKILL.md")
              and sha(m / ".codex/skills/buildroom-continuity/SKILL.md") == sha(ROOT / "skills/buildroom-continuity/SKILL.md"))
        check("update: a skill retired upstream is left in place, not deleted", (m / "skills/buildroom-video-engine/SKILL.md").exists())
        check("update: CLAUDE.md and AGENTS.md replaced", sha(m / "CLAUDE.md") == sha(UNI / "CLAUDE.md") and sha(m / "AGENTS.md") == sha(UNI / "CLAUDE.md"))
        check("update: the template arrives in templates/, not as a Business File",
              (m / "templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md").exists())
        backups = sorted((m / "backups").iterdir())
        b = backups[0] if backups else None
        check("update: one backup folder made", len(backups) == 1, backups)
        check("update: backup holds the Business File and everything replaced",
              b and sha(b / "BUILDROOM_BUSINESS_FILE.md") == bf_before and (b / "CLAUDE.md").read_text() == "old instructions\n"
              and (b / ".claude/skills/buildroom-os/SKILL.md").read_text() == "old navigator\n", b)
        check("update: scripts left executable", os.access(m / "update.sh", os.X_OK) and os.access(m / "install.sh", os.X_OK))

        p2 = run_update(release, m)
        check("update twice: exits 0, Business File still unchanged, a second backup folder",
              p2.returncode == 0 and sha(m / "BUILDROOM_BUSINESS_FILE.md") == bf_before and len(list((m / "backups").iterdir())) == 2,
              p2.stdout + p2.stderr)

        # ---- a folder with no Business File yet --------------------------------------
        fresh = make_member_folder(tmp / "Fresh", with_bf=False)
        p = run_update(release, fresh)
        check("update without a Business File: exits 0 and does not create one",
              p.returncode == 0 and not (fresh / "BUILDROOM_BUSINESS_FILE.md").exists() and "first session creates it" in p.stdout, p.stdout + p.stderr)

        # ---- refusals: nothing written --------------------------------------------------
        def refused(args, label):
            q = subprocess.run(["bash", str(release / "update.sh"), *args], capture_output=True, text=True)
            check(f"refuses {label}: exit 1 and says nothing changed", q.returncode == 1 and "Nothing in your folder was changed" in q.stdout, q.stdout)
        refused([], "with no folder given")
        refused([str(tmp / "nope")], "a folder that does not exist")
        refused([str(release)], "the release folder itself")
        empty = tmp / "Empty"; empty.mkdir()
        refused([str(empty)], "a folder that is not a Build Room folder")
        check("refusal leaves no backups/ behind", not (empty / "backups").exists())
        inner = make_member_folder(release, name="Old Inside")
        refused([str(inner)], "an old folder inside the release")
        outer = make_member_folder(tmp / "Outer")
        rel_in = stage_release(outer / "Downloads")
        q = run_update(rel_in, outer)
        check("refuses a release unzipped inside the old folder", q.returncode == 1 and "unzipped inside your old folder" in q.stdout, q.stdout)

        # ---- the Windows script mirrors the Mac one ---------------------------------
        sh, ps = (UNI / "update.sh").read_text(), (UNI / "update.ps1").read_text()
        sh_files = set(re.findall(r"(?:tools/|templates/)?[\w.-]+\.(?:html|md|pdf|sh|ps1)", sh.split("for f in", 1)[1].split("; do", 1)[0]))
        ps_files = {f.replace("\\", "/") for f in re.findall(r'"([^"]+\.(?:html|md|pdf|sh|ps1))"', ps.split("foreach ($f in", 1)[1].split(")) {", 1)[0])}
        check("update.ps1 replaces exactly the same files as update.sh", sh_files == ps_files and len(sh_files) == 13, (sh_files ^ ps_files))
        check("neither script ever lists the Business File as something to replace",
              "BUILDROOM_BUSINESS_FILE.md" not in sh.split("for f in", 1)[1].split("; do", 1)[0]
              and "BUILDROOM_BUSINESS_FILE.md" not in ps.split("foreach ($f in", 1)[1].split(")) {", 1)[0])
        check("update.ps1 hashes the Business File before and after and restores on a mismatch",
              ps.count("Get-Sha $Bf") == 2 and "restored from" in ps and "Get-FileHash" in ps)
        check("update.ps1 refuses the same four cases", all(s in ps for s in ("That is this release folder", "inside the new release folder",
              "unzipped inside your old folder", "does not look like a Build Room folder")))

        # ---- instructions and protocol ---------------------------------------------
        claude = (UNI / "CLAUDE.md").read_text()
        check("CLAUDE.md: never replace, reset or re-create an existing Business File", "Never replace, reset or re-create an existing Business File" in claude)
        check("CLAUDE.md: a missing file is created from templates/", "templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md" in claude)
        check("CLAUDE.md: updates only through update.sh / update.ps1", "Updating Build Room OS" in claude and "update.ps1" in claude)
        start = (UNI / "START-HERE.md").read_text()
        check("START-HERE: an Updating section that says not to unzip over the folder",
              "## Updating to a new release" in start and "not by unzipping over this folder" in start)
        proto = (ROOT / "shared/business-file-protocol.md").read_text()
        check("protocol: Never lose what is there (start from the current file, never the template)",
              "## Never lose what is there" in proto and "never from the blank template" in proto)
        copies = list((ROOT / "skills").glob("*/references/business-file-protocol.md"))
        check("protocol: every skill carries the same copy", copies and all(sha(c) == sha(ROOT / "shared/business-file-protocol.md") for c in copies))

        # ---- the Continuity System ----------------------------------------------------
        cs = ROOT / "skills/buildroom-continuity"
        skill = (cs / "SKILL.md").read_text()
        check("continuity: SKILL.md never writes the Business File", "Never write to the Business File" in skill and "never writes it" in skill)
        check("continuity: files live in continuity/, under projects/<name>/ in the Build Room folder",
              "projects/<short-name>/" in skill and "`continuity/` folder" in skill)
        check("continuity: never overwrites an existing file", "Never overwrite a file that already exists" in skill)
        check("continuity: credited to Jenn", "Jenn" in skill)
        for f in ("project-template.md", "state-template.md", "decisions-template.md", "two-tools.md",
                  "business-file-protocol.md", "business-file-template.md"):
            check(f"continuity: references/{f} present", (cs / "references" / f).exists())
        named = set(re.findall(r"references/([\w.-]+\.md)", skill))
        check("continuity: every reference named in SKILL.md exists", all((cs / "references" / n).exists() for n in named), named)
        desc = re.search(r"description: \|\n  (.+)\n", skill).group(1)
        check("continuity: description 200 to 1,024 characters with its phrases", 200 <= len(desc) <= 1024
              and "set up the continuity system for this project" in desc and "pick up where we left off" in desc, len(desc))
        check("continuity: no em dashes in the skill", not any("—" in p.read_text() for p in [cs / "SKILL.md"] + [cs / "references" / f for f in ("project-template.md", "state-template.md", "decisions-template.md", "two-tools.md")]))
        check("continuity: listed in CLAUDE.md", "`buildroom-continuity`" in claude)
        for s in ("buildroom-finish-it", "buildroom-build-it"):
            check(f"{s}: logs decisions into continuity/DECISIONS.md when present", "continuity/DECISIONS.md" in (ROOT / "skills" / s / "SKILL.md").read_text())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(RESULTS)
    print(f"\n{passed}/{len(RESULTS)} checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
