#!/usr/bin/env bash
# Build Room OS: update an existing Build Room folder to this release (Mac / Linux).
#
#   bash update.sh "/path/to/your/existing/BuildRoom_OS"
#
# Run it from the NEW release folder you just unzipped. It never touches your Business File
# or anything you made: it replaces only the toolkit (the buildroom-* skills, tools/, CLAUDE.md,
# AGENTS.md, START-HERE.md, the guide, the scripts, templates/). Everything it replaces is copied
# to backups/ first, and it checks your Business File is byte-for-byte the same afterwards.
set -euo pipefail

say() { printf '%s\n' "$*"; }
fail() { say "STOPPED: $*"; say "Nothing in your folder was changed."; exit 1; }

hash_of() {  # prints a sha256 of the file, or "none"
  [ -f "$1" ] || { echo none; return; }
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; fi
}

SRC="$(cd "$(dirname "$0")" && pwd -P)"
[ $# -eq 1 ] || fail 'Give the path of your existing Build Room folder, in quotes: bash update.sh "/path/to/BuildRoom_OS"'
[ -d "$1" ] || fail "No folder at: $1"
TARGET="$(cd "$1" && pwd -P)"

[ -d "$SRC/skills/buildroom-os" ] || fail "This script must run from a complete, unzipped Build Room OS release."
[ "$SRC" != "$TARGET" ] || fail "That is this release folder. Give the path of your OLD Build Room folder, the one with your Business File in it."
case "$TARGET/" in "$SRC"/*) fail "Your old folder is inside the new release folder. Unzip the release somewhere else first." ;; esac
case "$SRC/" in "$TARGET"/*) fail "The new release was unzipped inside your old folder. Unzip it somewhere else (your Downloads folder) first." ;; esac
if [ ! -f "$TARGET/BUILDROOM_BUSINESS_FILE.md" ] && [ ! -d "$TARGET/.claude/skills/buildroom-os" ] && [ ! -d "$TARGET/skills/buildroom-os" ]; then
  fail "That does not look like a Build Room folder (no Business File and no Build Room skills in it)."
fi

BF="$TARGET/BUILDROOM_BUSINESS_FILE.md"
BEFORE="$(hash_of "$BF")"
STAMP="$(date +%Y-%m-%d-%H%M%S)"
BACKUP="$TARGET/backups/update-$STAMP"
i=2; while [ -e "$BACKUP" ]; do BACKUP="$TARGET/backups/update-$STAMP-$i"; i=$((i+1)); done
mkdir -p "$BACKUP"

# 1. Back up the Business File first, always.
[ -f "$BF" ] && cp -p "$BF" "$BACKUP/BUILDROOM_BUSINESS_FILE.md"

# 2. Back up, then replace, each toolkit item. Nothing outside this list is ever written.
replace() {  # replace <relative path>
  local rel="$1"
  [ -e "$SRC/$rel" ] || return 0
  if [ -e "$TARGET/$rel" ]; then
    mkdir -p "$BACKUP/$(dirname "$rel")"
    cp -Rp "$TARGET/$rel" "$BACKUP/$rel"
    rm -rf "${TARGET:?}/${rel:?}"
  fi
  mkdir -p "$TARGET/$(dirname "$rel")"
  cp -R "$SRC/$rel" "$TARGET/$rel"
}

n=0
for loc in skills .claude/skills .codex/skills; do
  [ -d "$SRC/$loc" ] || continue
  for d in "$SRC/$loc"/buildroom-*/; do
    replace "$loc/$(basename "$d")"
    [ "$loc" = skills ] && n=$((n+1))
  done
done
for f in tools/Rent_Calculator.html tools/Brainstorm_Board.html tools/Business_File_Viewer.html tools/BuildRoom_OS_Quick_Start.html \
         CLAUDE.md AGENTS.md START-HERE.md BuildRoom_OS_Say_These_Words.pdf install.sh install.ps1 update.sh update.ps1 \
         templates/BUILDROOM_BUSINESS_FILE_TEMPLATE.md; do
  replace "$f"
done
[ -f "$TARGET/install.sh" ] && chmod +x "$TARGET/install.sh"
[ -f "$TARGET/update.sh" ] && chmod +x "$TARGET/update.sh"

# 3. Prove the Business File was not touched.
AFTER="$(hash_of "$BF")"
if [ "$BEFORE" != "$AFTER" ]; then
  [ -f "$BACKUP/BUILDROOM_BUSINESS_FILE.md" ] && cp -p "$BACKUP/BUILDROOM_BUSINESS_FILE.md" "$BF"
  say "WARNING: your Business File changed during the update, so it was restored from $BACKUP."
  exit 1
fi

say "Updated $n Build Room skills in: $TARGET"
say "Everything replaced was saved first in: $BACKUP"
if [ "$BEFORE" = none ]; then
  say "There is no Business File in that folder yet. Your first session creates it."
else
  say "Your Business File was not touched (checked byte for byte)."
fi
say "Your own files (deliverables, launches/, search/, proof/, projects/, .env) were not touched."
say "Open Claude Code or Codex in that folder and say: what changed in Build Room OS?"
