#!/usr/bin/env bash
# Build installable .skill files for every Build Room skill.
# Usage: bash build-skills.sh [output-dir]   (default: ./dist)
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-dist}"
mkdir -p "$OUT"

# Skills that carry the shared media toolkit (ledger, generation adapter, provider sign-up).
MEDIA_SKILLS="buildroom-ad-studio buildroom-video-director"

# A shared file edited inside a skill (newer than the shared source and different from it)
# would be silently overwritten below. Refuse instead, and say where the edit belongs.
for s in $MEDIA_SKILLS; do
  [ -d "skills/$s" ] || continue
  for src in shared/media/*; do
    f="$(basename "$src")"
    case "$f" in *.py|*.mjs) dest="skills/$s/scripts/$f" ;; *) dest="skills/$s/references/$f" ;; esac
    if [ -f "$dest" ] && ! cmp -s "$src" "$dest" && [ "$dest" -nt "$src" ]; then
      echo "ERROR $dest was edited in the skill. Move the change into $src (the shared source), then rebuild." >&2
      exit 1
    fi
  done
done

find skills -name __pycache__ -type d -prune -exec rm -rf {} +

for dir in skills/*/; do
  name="$(basename "$dir")"
  # Refuse to package unreviewed scaffolds from generate-skill.py.
  if grep -rq "TODO-REVIEW" "$dir"; then
    echo "SKIP  $name — unresolved TODO-REVIEW markers (draft scaffold, not packaged)"
    continue
  fi
  # Sync the shared protocol and business-file template into the skill,
  # so every installer carries the canonical copies.
  cp shared/business-file-protocol.md "$dir/references/business-file-protocol.md"
  cp templates/BUILDROOM_BUSINESS_FILE.md "$dir/references/business-file-template.md"
  case " $MEDIA_SKILLS " in
    *" $name "*)
      mkdir -p "$dir/scripts" "$dir/references"
      for src in shared/media/*; do
        f="$(basename "$src")"
        case "$f" in *.py|*.mjs) cp "$src" "$dir/scripts/$f" ;; *) cp "$src" "$dir/references/$f" ;; esac
      done ;;
  esac
  # Package: a .skill is a zip whose top-level folder is the skill name.
  rm -f "$OUT/$name.skill"
  (cd skills && zip -q -r "../$OUT/$name.skill" "$name")
  echo "built $OUT/$name.skill ($(du -h "$OUT/$name.skill" | cut -f1))"
done

echo "Done. Skills synced; .skill zips in dist/ are for inspection only (members install the universal zip)."
