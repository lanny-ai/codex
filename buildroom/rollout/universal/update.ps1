# Build Room OS: update an existing Build Room folder to this release (Windows PowerShell).
#
#   powershell -ExecutionPolicy Bypass -File update.ps1 "C:\path\to\your\existing\BuildRoom_OS"
#
# Run it from the NEW release folder you just unzipped. It never touches your Business File
# or anything you made: it replaces only the toolkit (the buildroom-* skills, tools\, CLAUDE.md,
# AGENTS.md, START-HERE.md, the guide, the scripts, templates\). Everything it replaces is copied
# to backups\ first, and it checks your Business File is byte-for-byte the same afterwards.
param([string]$Existing)
$ErrorActionPreference = "Stop"

function Stop-Update($msg) { Write-Host "STOPPED: $msg"; Write-Host "Nothing in your folder was changed."; exit 1 }
function Get-Sha($path) { if (Test-Path -LiteralPath $path -PathType Leaf) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { "none" } }

$Src = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path.TrimEnd('\')
if (-not $Existing) { Stop-Update 'Give the path of your existing Build Room folder, in quotes: update.ps1 "C:\path\to\BuildRoom_OS"' }
if (-not (Test-Path -LiteralPath $Existing -PathType Container)) { Stop-Update "No folder at: $Existing" }
$Target = (Resolve-Path -LiteralPath $Existing).Path.TrimEnd('\')

if (-not (Test-Path -LiteralPath (Join-Path $Src "skills\buildroom-os"))) { Stop-Update "This script must run from a complete, unzipped Build Room OS release." }
if ($Src -ieq $Target) { Stop-Update "That is this release folder. Give the path of your OLD Build Room folder, the one with your Business File in it." }
if (($Target + '\').StartsWith($Src + '\', [StringComparison]::OrdinalIgnoreCase)) { Stop-Update "Your old folder is inside the new release folder. Unzip the release somewhere else first." }
if (($Src + '\').StartsWith($Target + '\', [StringComparison]::OrdinalIgnoreCase)) { Stop-Update "The new release was unzipped inside your old folder. Unzip it somewhere else (your Downloads folder) first." }
$Bf = Join-Path $Target "BUILDROOM_BUSINESS_FILE.md"
if (-not (Test-Path -LiteralPath $Bf) -and -not (Test-Path -LiteralPath (Join-Path $Target ".claude\skills\buildroom-os")) -and -not (Test-Path -LiteralPath (Join-Path $Target "skills\buildroom-os"))) {
  Stop-Update "That does not look like a Build Room folder (no Business File and no Build Room skills in it)."
}

$Before = Get-Sha $Bf
$Stamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
$Backup = Join-Path $Target ("backups\update-" + $Stamp)
$i = 2
while (Test-Path -LiteralPath $Backup) { $Backup = Join-Path $Target ("backups\update-" + $Stamp + "-" + $i); $i++ }
New-Item -ItemType Directory -Force -Path $Backup | Out-Null

# 1. Back up the Business File first, always.
if (Test-Path -LiteralPath $Bf) { Copy-Item -LiteralPath $Bf -Destination (Join-Path $Backup "BUILDROOM_BUSINESS_FILE.md") }

# 2. Back up, then replace, each toolkit item. Nothing outside this list is ever written.
function Update-Item($rel) {
  $from = Join-Path $Src $rel
  if (-not (Test-Path -LiteralPath $from)) { return }
  $to = Join-Path $Target $rel
  if (Test-Path -LiteralPath $to) {
    $bak = Join-Path $Backup $rel
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $bak) | Out-Null
    Copy-Item -LiteralPath $to -Destination $bak -Recurse
    Remove-Item -LiteralPath $to -Recurse -Force
  }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $to) | Out-Null
  Copy-Item -LiteralPath $from -Destination $to -Recurse
}

$n = 0
foreach ($loc in @("skills", ".claude\skills", ".codex\skills")) {
  $dir = Join-Path $Src $loc
  if (-not (Test-Path -LiteralPath $dir)) { continue }
  Get-ChildItem -LiteralPath $dir -Directory -Filter "buildroom-*" -Force | ForEach-Object {
    Update-Item (Join-Path $loc $_.Name)
    if ($loc -eq "skills") { $n++ }
  }
}
foreach ($f in @("tools\Rent_Calculator.html", "tools\Brainstorm_Board.html", "tools\Business_File_Viewer.html", "tools\BuildRoom_OS_Quick_Start.html",
                 "CLAUDE.md", "AGENTS.md", "START-HERE.md", "BuildRoom_OS_Say_These_Words.pdf", "install.sh", "install.ps1", "update.sh", "update.ps1",
                 "templates\BUILDROOM_BUSINESS_FILE_TEMPLATE.md")) {
  Update-Item $f
}

# 3. Prove the Business File was not touched.
$After = Get-Sha $Bf
if ($Before -ne $After) {
  $saved = Join-Path $Backup "BUILDROOM_BUSINESS_FILE.md"
  if (Test-Path -LiteralPath $saved) { Copy-Item -LiteralPath $saved -Destination $Bf -Force }
  Write-Host "WARNING: your Business File changed during the update, so it was restored from $Backup."
  exit 1
}

Write-Host "Updated $n Build Room skills in: $Target"
Write-Host "Everything replaced was saved first in: $Backup"
if ($Before -eq "none") { Write-Host "There is no Business File in that folder yet. Your first session creates it." } else { Write-Host "Your Business File was not touched (checked byte for byte)." }
Write-Host "Your own files (deliverables, launches\, search\, proof\, projects\, .env) were not touched."
Write-Host "Open Claude Code or Codex in that folder and say: what changed in Build Room OS?"
