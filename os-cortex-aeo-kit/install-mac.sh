#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI was not found. Install or update the ChatGPT desktop/Codex app, then try again."
  exit 1
fi
codex plugin marketplace add "$ROOT"
echo "OS Cortex AEO marketplace added. Restart ChatGPT desktop, open Plugins, select OS Cortex AEO Systems, and install OS Cortex AEO Publisher."
