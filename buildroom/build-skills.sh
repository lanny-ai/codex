#!/usr/bin/env bash
# Build installable .skill files for every Build Room skill.
# Usage: bash build-skills.sh [output-dir]   (default: ./dist)
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-dist}"
mkdir -p "$OUT"

for dir in skills/*/; do
  name="$(basename "$dir")"
  # Sync the shared protocol and business-file template into the skill,
  # so every installer carries the canonical copies.
  cp shared/business-file-protocol.md "$dir/references/business-file-protocol.md"
  cp templates/BUILDROOM_BUSINESS_FILE.md "$dir/references/business-file-template.md"
  # Package: a .skill is a zip whose top-level folder is the skill name.
  rm -f "$OUT/$name.skill"
  (cd skills && zip -q -r "../$OUT/$name.skill" "$name")
  echo "built $OUT/$name.skill ($(du -h "$OUT/$name.skill" | cut -f1))"
done

echo "Done. Install via Claude Cowork: Settings -> Skills -> Upload Skill."
