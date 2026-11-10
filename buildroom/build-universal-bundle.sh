#!/usr/bin/env bash
# Build the drag-and-drop install folder for Claude Code AND Codex.
# Usage: bash build-universal-bundle.sh   (emits dist/BuildRoom_OS.zip)
#
# Layout of the zip (one top-level folder, BuildRoom_OS/):
#   START-HERE.md                  install steps for every tool
#   CLAUDE.md / AGENTS.md          project instructions (Claude Code reads CLAUDE.md, Codex reads AGENTS.md)
#   .claude/skills/<skill>/        project-scoped skills for Claude Code   (auto-discovered)
#   .codex/skills/<skill>/         project-scoped skills for Codex         (auto-discovered)
#   skills/<skill>/                the same skills, visible; install.sh copies these globally
#   install.sh / install.ps1       optional: copy skills into ~/.claude/skills and ~/.codex/skills
#   update.sh / update.ps1         update an existing Build Room folder; never touches the Business File
#   tools/*.html                   Rent Calculator, Brainstorm Board, Business File Viewer, Quick Start
#   BuildRoom_OS_Say_These_Words.pdf  the printable trigger-phrase guide
#   templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md  the blank Business File. The zip never carries
#                                  BUILDROOM_BUSINESS_FILE.md itself, so unzipping a release over a
#                                  member's folder can never replace their filled-in file.
set -euo pipefail
cd "$(dirname "$0")"

bash build-skills.sh dist >/dev/null

STAGE_ROOT="dist/.universal-stage"
STAGE="$STAGE_ROOT/BuildRoom_OS"
rm -rf "./${STAGE_ROOT:?}"; mkdir -p "$STAGE"

# skills: visible copy + the two auto-discovered locations
mkdir -p "$STAGE/skills" "$STAGE/.claude/skills" "$STAGE/.codex/skills"
for d in skills/*/; do
  name="$(basename "$d")"
  cp -R "$d" "$STAGE/skills/$name"
done
cp -R "$STAGE/skills/." "$STAGE/.claude/skills/"
cp -R "$STAGE/skills/." "$STAGE/.codex/skills/"


# tools
mkdir -p "$STAGE/tools"
cp rollout/Rent_Calculator.html rollout/Brainstorm_Board.html rollout/Business_File_Viewer.html rollout/BuildRoom_OS_Quick_Start.html "$STAGE/tools/"
cp rollout/BuildRoom_OS_Say_These_Words.pdf "$STAGE/"

# member file + docs
mkdir -p "$STAGE/templates"
cp templates/BUILDROOM_BUSINESS_FILE.md "$STAGE/templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md"
cp rollout/universal/START-HERE.md "$STAGE/"
cp rollout/universal/CLAUDE.md "$STAGE/CLAUDE.md"
cp rollout/universal/CLAUDE.md "$STAGE/AGENTS.md"
cp rollout/universal/install.sh rollout/universal/install.ps1 rollout/universal/update.sh rollout/universal/update.ps1 "$STAGE/"
chmod +x "$STAGE/install.sh" "$STAGE/update.sh"
# Safety: the member's own file must never be in a release.
if [ -e "$STAGE/BUILDROOM_BUSINESS_FILE.md" ]; then echo "ERROR: BUILDROOM_BUSINESS_FILE.md must not be in the zip" >&2; exit 1; fi

OUT="dist/BuildRoom_OS.zip"
rm -f "$OUT"
(cd "$STAGE_ROOT" && zip -qr "../$(basename "$OUT")" BuildRoom_OS)
rm -rf "./${STAGE_ROOT:?}"
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | awk 'NR>3 && NF==4 {print $4}' | grep -v '/$' | sed 's|^BuildRoom_OS/||' | grep -v '^\.claude/\|^\.codex/\|^skills/' | sort
