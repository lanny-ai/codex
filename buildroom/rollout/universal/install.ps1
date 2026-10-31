# Build Room OS — optional global install for Claude Code and Codex (Windows PowerShell).
# Copies the skills in .\skills into ~\.claude\skills and ~\.codex\skills so they work in every project.
# Safe to re-run: replaces only folders named buildroom-*. Touches nothing else.
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = Join-Path $Here "skills"
if (-not (Test-Path $Src)) { Write-Host "No skills\ folder next to this script. Unzip BuildRoom_OS.zip fully first."; exit 1 }

foreach ($Target in @((Join-Path $env:USERPROFILE ".claude\skills"), (Join-Path $env:USERPROFILE ".codex\skills"))) {
  New-Item -ItemType Directory -Force -Path $Target | Out-Null
  $n = 0
  Get-ChildItem -Path $Src -Directory -Filter "buildroom-*" | ForEach-Object {
    $Dest = Join-Path $Target $_.Name
    if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
    Copy-Item -Recurse -Path $_.FullName -Destination $Dest
    $n++
  }
  Write-Host "Installed $n Build Room skills into $Target"
}
Write-Host ""
Write-Host "Done. Open Claude Code or Codex anywhere and say: I'm new to the Build Room - set me up."
Write-Host "Your Business File stays in this folder: $(Join-Path $Here 'BUILDROOM_BUSINESS_FILE.md')"
