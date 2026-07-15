$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
  Write-Error "Codex CLI was not found. Install or update the ChatGPT desktop/Codex app, then try again."
}
codex plugin marketplace add $Root
Write-Host "OS Cortex AEO marketplace added. Restart ChatGPT desktop, open Plugins, select OS Cortex AEO Systems, and install OS Cortex AEO Publisher."
