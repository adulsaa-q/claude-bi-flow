<#
.SYNOPSIS
  One-shot setup of the BI + AI flow for Claude Code (no admin rights needed).

.DESCRIPTION
  1. checks prerequisites (git, python, uv or pipx, claude)
  2. installs pbi-cli (Power BI CLI) and its 13 Power BI skills
  3. copies this repo's skills\ into ~\.claude\skills (existing ones are backed up, never silently overwritten)
  4. adds the team rules block to ~\.claude\CLAUDE.md (between markers, safe to re-run)
  5. installs the recommended Claude Code plugins

  Safe to run twice. Use -DryRun first to see every action without changing anything.

.PARAMETER DryRun       Print actions, change nothing.
.PARAMETER Force        Replace skills that already exist and differ (a backup is still made).
.PARAMETER ClaudeHome   Target config dir. Default ~\.claude (override for testing).
.PARAMETER SkipPbiCli   Do not install pbi-cli / its skills.
.PARAMETER SkipPlugins  Do not install Claude Code plugins.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$ClaudeHome = (Join-Path $env:USERPROFILE '.claude'),
    [switch]$SkipPbiCli,
    [switch]$SkipPlugins
)

$ErrorActionPreference = 'Stop'
$repo = $PSScriptRoot
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$results = [System.Collections.Generic.List[object]]::new()

function Step($name, $status, $detail = '') {
    $results.Add([pscustomobject]@{ Step = $name; Status = $status; Detail = $detail })
    $color = switch ($status) { 'OK' { 'Green' } 'SKIP' { 'DarkGray' } 'WARN' { 'Yellow' } 'DRY' { 'Cyan' } default { 'Red' } }
    Write-Host ("[{0,-4}] {1} {2}" -f $status, $name, $detail) -ForegroundColor $color
}
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# --- 1. prerequisites ------------------------------------------------------------------
foreach ($c in 'git', 'python', 'claude') {
    if (Have $c) { Step "prereq: $c" 'OK' } else { Step "prereq: $c" 'FAIL' 'not on PATH - install it first (see SETUP.md)' }
}
$installer = if (Have 'uv') { 'uv' } elseif (Have 'pipx') { 'pipx' } else { $null }
if ($installer) { Step 'prereq: uv or pipx' 'OK' $installer } else { Step 'prereq: uv or pipx' 'FAIL' 'install uv (https://docs.astral.sh/uv/) - user scope, no admin' }
if ($results | Where-Object Status -eq 'FAIL') {
    Write-Host "`nFix the FAIL items above, then run install.ps1 again." -ForegroundColor Red
    exit 1
}

# --- 2. pbi-cli + Power BI skills --------------------------------------------------------
if ($SkipPbiCli) {
    Step 'pbi-cli' 'SKIP' '-SkipPbiCli'
} elseif (Have 'pbi') {
    Step 'pbi-cli' 'SKIP' ("already installed: " + ((pbi --version 2>&1) -join ' '))
} elseif ($DryRun) {
    Step 'pbi-cli' 'DRY' "$installer install pbi-cli-tool"
} else {
    if ($installer -eq 'uv') { uv tool install pbi-cli-tool } else { pipx install pbi-cli-tool }
    if ($LASTEXITCODE -ne 0) { Step 'pbi-cli' 'FAIL' 'install command failed' } else { Step 'pbi-cli' 'OK' 'open a NEW terminal so pbi is on PATH' }
}
if (-not $SkipPbiCli) {
    if ($DryRun) { Step 'pbi-cli skills' 'DRY' 'pbi-cli skills install' }
    elseif (Have 'pbi-cli') { pbi-cli skills install | Out-Null; Step 'pbi-cli skills' 'OK' '13 power-bi-* skills' }
    else { Step 'pbi-cli skills' 'WARN' 'pbi-cli not on PATH yet - open a new terminal and run: pbi-cli skills install' }
}

# --- 3. copy this repo's skills -----------------------------------------------------------
$skillsDst = Join-Path $ClaudeHome 'skills'
$backupDir = Join-Path $ClaudeHome "skills-backup-$stamp"
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $skillsDst | Out-Null }

function Get-TreeHash($dir) {
    $files = Get-ChildItem $dir -Recurse -File | Sort-Object FullName
    $h = $files | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash + $_.FullName.Substring($dir.Length) }
    ($h -join '|')
}

foreach ($src in Get-ChildItem (Join-Path $repo 'skills') -Directory) {
    $dst = Join-Path $skillsDst $src.Name
    if (-not (Test-Path $dst)) {
        if ($DryRun) { Step "skill: $($src.Name)" 'DRY' 'copy (new)' }
        else { Copy-Item $src.FullName $dst -Recurse; Step "skill: $($src.Name)" 'OK' 'copied (new)' }
        continue
    }
    if ((Get-TreeHash $src.FullName) -eq (Get-TreeHash $dst)) { Step "skill: $($src.Name)" 'SKIP' 'identical'; continue }
    if (-not $Force) { Step "skill: $($src.Name)" 'WARN' 'exists and differs - kept yours. Re-run with -Force to replace (backup is made)'; continue }
    if ($DryRun) { Step "skill: $($src.Name)" 'DRY' "replace, backup to $backupDir"; continue }
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Move-Item $dst (Join-Path $backupDir $src.Name)
    Copy-Item $src.FullName $dst -Recurse
    Step "skill: $($src.Name)" 'OK' "replaced, old copy in $backupDir"
}

# --- 4. team rules block in global CLAUDE.md ------------------------------------------------
$claudeMd = Join-Path $ClaudeHome 'CLAUDE.md'
$begin = '<!-- claude-bi-flow:begin -->'
$end = '<!-- claude-bi-flow:end -->'
$block = $begin + "`n" + (Get-Content (Join-Path $repo 'global\CLAUDE.team.md') -Raw).TrimEnd() + "`n" + $end
$current = if (Test-Path $claudeMd) { Get-Content $claudeMd -Raw } else { '' }
$pattern = [regex]::Escape($begin) + '(?s).*?' + [regex]::Escape($end)
$new = if ($current -match $pattern) { [regex]::Replace($current, $pattern, [System.Text.RegularExpressions.MatchEvaluator] { param($m) $block }) }
       else { ($current.TrimEnd() + "`n`n" + $block + "`n").TrimStart() }
if ($new -eq $current) { Step 'global CLAUDE.md' 'SKIP' 'team block already current' }
elseif ($DryRun) { Step 'global CLAUDE.md' 'DRY' "write team block into $claudeMd" }
else {
    if (Test-Path $claudeMd) { Copy-Item $claudeMd "$claudeMd.bak-$stamp" }
    New-Item -ItemType Directory -Force -Path $ClaudeHome | Out-Null
    [System.IO.File]::WriteAllText($claudeMd, $new, [System.Text.UTF8Encoding]::new($false))
    Step 'global CLAUDE.md' 'OK' 'team block written (your own text outside the markers is untouched)'
}

# --- 5. plugins ---------------------------------------------------------------------------------
if ($SkipPlugins) { Step 'plugins' 'SKIP' '-SkipPlugins' }
else {
    foreach ($p in (Get-Content (Join-Path $repo 'plugins.txt') | Where-Object { $_ -and $_ -notmatch '^\s*#' })) {
        if ($DryRun) { Step "plugin: $p" 'DRY' "claude plugin install $p" }
        else {
            $out = claude plugin install $p 2>&1
            if ($LASTEXITCODE -eq 0) { Step "plugin: $p" 'OK' } else { Step "plugin: $p" 'WARN' (($out | Select-Object -Last 1) -join '') }
        }
    }
}

Write-Host "`n--- summary ---"
$results | Group-Object Status | ForEach-Object { "{0,-5} {1}" -f $_.Name, $_.Count } | Out-Host
Write-Host "`nNext: open a NEW terminal, then run  .\doctor.ps1  to verify. Restart Claude Code to load new skills."
if ($results | Where-Object Status -eq 'FAIL') { exit 1 }
