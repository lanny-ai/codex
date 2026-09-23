#!/usr/bin/env bash
# Build the drag-and-drop install folder for Claude Code AND Codex (plus Cowork .skill files).
# Usage: bash build-universal-bundle.sh   (emits dist/BuildRoom_OS.zip)
#
# Layout of the zip (one top-level folder, BuildRoom_OS/):
#   START-HERE.md                  install steps for every tool
#   CLAUDE.md / AGENTS.md          project instructions (Claude Code reads CLAUDE.md, Codex reads AGENTS.md)
#   .claude/skills/<skill>/        project-scoped skills for Claude Code   (auto-discovered)
#   .codex/skills/<skill>/         project-scoped skills for Codex         (auto-discovered)
#   skills/<skill>/                the same skills, visible; install.sh copies these globally
#   install.sh / install.ps1       optional: copy skills into ~/.claude/skills and ~/.codex/skills
#   cowork/*.skill                 packaged skills for Claude Cowork / claude.ai upload
#   tools/*.html                   Rent Calculator, Brainstorm Board, Quick Start
#   BUILDROOM_BUSINESS_FILE.md     the member's Business File — lives in this folder
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

# Cowork packages
mkdir -p "$STAGE/cowork"; cp dist/*.skill "$STAGE/cowork/"

# tools
mkdir -p "$STAGE/tools"
cp rollout/Rent_Calculator.html rollout/Brainstorm_Board.html rollout/BuildRoom_OS_Quick_Start.html "$STAGE/tools/"

# member file + docs
cp templates/BUILDROOM_BUSINESS_FILE.md "$STAGE/"
cp rollout/universal/START-HERE.md "$STAGE/"
cp rollout/universal/CLAUDE.md "$STAGE/CLAUDE.md"
cp rollout/universal/CLAUDE.md "$STAGE/AGENTS.md"
cp rollout/universal/install.sh rollout/universal/install.ps1 "$STAGE/"
chmod +x "$STAGE/install.sh"

OUT="dist/BuildRoom_OS.zip"
rm -f "$OUT"
(cd "$STAGE_ROOT" && zip -qr "../$(basename "$OUT")" BuildRoom_OS)
rm -rf "./${STAGE_ROOT:?}"
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | awk 'NR>3 && NF==4 {print $4}' | grep -v '/$' | sed 's|^BuildRoom_OS/||' | grep -v '^\.claude/\|^\.codex/\|^skills/' | sort
