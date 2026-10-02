#!/usr/bin/env bash
# Build Room OS — optional global install for Claude Code and Codex (Mac / Linux).
# Copies the skills in ./skills into ~/.claude/skills and ~/.codex/skills so they work in every project.
# Safe to re-run: replaces only folders named buildroom-*. Touches nothing else.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/skills"
[ -d "$SRC" ] || { echo "No skills/ folder next to this script. Unzip BuildRoom_OS.zip fully first."; exit 1; }

for TARGET in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  mkdir -p "$TARGET"
  n=0
  for d in "$SRC"/buildroom-*/; do
    name="$(basename "$d")"
    rm -rf "${TARGET:?}/${name:?}"
    cp -R "$d" "$TARGET/$name"
    n=$((n+1))
  done
  echo "Installed $n Build Room skills into $TARGET"
done

echo
echo "Done. Open Claude Code or Codex anywhere and say: I'm new to the Build Room — set me up."
echo "Your Business File stays in this folder: $HERE/BUILDROOM_BUSINESS_FILE.md"
