#!/usr/bin/env bash
# Build the member-facing install bundle: all skills + quick start + README + blank Business File.
# Usage: bash build-rollout-bundle.sh   (emits dist/BuildRoom_OS_Complete_Install_Bundle.zip)
set -euo pipefail
cd "$(dirname "$0")"

bash build-skills.sh dist

STAGE="dist/.bundle-stage"
rm -rf "$STAGE"; mkdir -p "$STAGE"
cp dist/*.skill "$STAGE/"
cp rollout/BuildRoom_OS_Quick_Start.html "$STAGE/"
cp rollout/MEMBER-README.md "$STAGE/README.md"
cp templates/BUILDROOM_BUSINESS_FILE.md "$STAGE/"

OUT="dist/BuildRoom_OS_Complete_Install_Bundle.zip"
rm -f "$OUT"
(cd "$STAGE" && zip -q "../$(basename "$OUT")" ./*)
rm -rf "$STAGE"
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | awk 'NR>3 && NF==4 {print "  " $4}'
