<#
Offline lint of the whole .pbip — model (Tabular Editor 2 Best Practice Analyzer) + report (fab-inspector).
Neither needs Power BI Desktop open; both read the on-disk PBIP tree. Added 2026-09-17 (FLOW_AUDIT P3).

Usage:  powershell -File scripts/lint_pbip.ps1 [-Model] [-Report] [-Full] [-UpdateBaseline] [-OutDir <dir>]
   (no switch = both)  -Full prints every BPA line instead of the summary.
Exit code = number of NEW signal findings: BPA violations in the "signal" categories (DAX Expressions +
Error Prevention) that are not in scripts/lint-rules/signal-baseline.txt, plus fab-inspector errors above
the baselined error count. Without a baseline file every signal finding counts. 255 = a lint engine or
rule file was unavailable / produced incomplete output (never a clean result).
-UpdateBaseline rewrites the baseline from the current run (review the diff before committing it).
A baselined row is KNOWN, not accepted: owners and triage live in knowledge/PENDING_DECISIONS.md.

Tools (user-local, no admin):
  TE2   %LOCALAPPDATA%\Programs\TabularEditor2\TabularEditor.exe  (+ BPARules-Microsoft.json next to it,
        from https://raw.githubusercontent.com/microsoft/Analysis-Services/master/BestPracticeRules/BPARules.json)
  fab   %LOCALAPPDATA%\Programs\fab-inspector\win-x64\CLI\PBIRInspectorCLI.exe (+ ..\..\Base-rules.json,
        release https://github.com/NatVanG/fab-inspector/releases, needs .NET 8 runtime)
Project-specific rule files, if ever written, go in scripts/lint-rules/ and are passed instead of the defaults.

Known accepted noise (do not chase): BPA "Visible objects with no description" (~1,200), "format string"
(~200, mostly other teams' measures), fab-inspector "Ensure charts use theme colours" (~43 pages — the report
hard-codes its palette on purpose, AGENTS.md Design Guidelines).
#>
param([switch]$Model, [switch]$Report, [switch]$Full, [switch]$UpdateBaseline, [string]$OutDir = "$env:TEMP\pbip_lint",
      [string]$ToolRoot = "$env:LOCALAPPDATA\Programs")
$ErrorActionPreference = "Stop"
trap { Write-Host "LINT ERROR (not a clean result): $_"; exit 255 }
if (-not $Model -and -not $Report) { $Model = $true; $Report = $true }
$root = Split-Path -Parent $PSScriptRoot
# Follow project references; save-as filenames need not match artifact folder names.
$projects = @(Get-ChildItem $root -Recurse -Depth 2 -Filter *.pbip)
if ($projects.Count -ne 1) { throw "Expected exactly one .pbip under $root; found $($projects.Count)" }
$pbip = $projects[0]
$project = Get-Content -Raw $pbip.FullName | ConvertFrom-Json
$reports = @($project.artifacts | Where-Object { $_.report.path })
if ($reports.Count -ne 1) { throw "Expected one report reference in $($pbip.FullName)" }
$rp = [IO.Path]::GetFullPath((Join-Path $pbip.DirectoryName $reports[0].report.path))
$definition = Get-Content -Raw (Join-Path $rp 'definition.pbir') | ConvertFrom-Json
if ($Model) {
    if (-not $definition.datasetReference.byPath.path) { throw "Model lint requires a local datasetReference.byPath" }
    $sm = Join-Path ([IO.Path]::GetFullPath((Join-Path $rp $definition.datasetReference.byPath.path))) 'definition'
    if (-not (Test-Path $sm -PathType Container)) { throw "Missing model definition: $sm" }
}
Write-Host "pbip: $($pbip.FullName)"
New-Item -ItemType Directory -Force $OutDir | Out-Null
$signal = 0
$sigRows = @()
$fabErrors = 0

if ($Model) {
    $te = "$ToolRoot\TabularEditor2\TabularEditor.exe"
    $rules = "$ToolRoot\TabularEditor2\BPARules-Microsoft.json"
    $custom = Join-Path $root "scripts\lint-rules\bpa.json"
    if (Test-Path $custom) { $rules = $custom }
    if (-not (Test-Path $te) -or -not (Test-Path $rules)) { throw "Model lint unavailable: executable or rules missing ($te, $rules)" }
    else {
        $out = Join-Path $OutDir "bpa.txt"
        & $te $sm -A $rules 2>&1 | Out-File -Encoding utf8 $out
        $engineExit = $LASTEXITCODE
        $lines = Get-Content $out
        if (-not ($lines -match 'Running Best Practice Analyzer') -or -not ($lines[-1] -match '^=+$')) {
            throw "Model lint did not produce a complete BPA result; see $out"
        }
        $viol = $lines | Where-Object { $_ -match 'violates rule "\[(.+?)\] (.+?)"' }
        # TE2 returns 1 for BPA violations too; require completed output to distinguish failure.
        if ($engineExit -notin @(0, 1) -or ($engineExit -eq 1 -and @($viol).Count -eq 0) -or
            ($lines -match '^\s*(Error:|Exception|Unhandled)')) {
            throw "Model lint failed (exit $engineExit); see $out"
        }
        Write-Host "== Model BPA (Tabular Editor 2, $($viol.Count) violations, log: $out) =="
        $viol | ForEach-Object { ($_ -replace '.*violates rule "\[(.+?)\] (.+?)".*', '$1 | $2') } |
            Group-Object | Sort-Object Count -Descending | ForEach-Object { "{0,5}  {1}" -f $_.Count, $_.Name }
        $sig = $viol | Where-Object { $_ -match '\[(DAX Expressions|Error Prevention)\]' }
        $signal += $sig.Count
        $sigRows = @($sig | ForEach-Object { ($_ -replace ' violates rule ', ' | ').Trim() })
        Write-Host "`n-- signal rows (DAX Expressions / Error Prevention): $($sig.Count)"
        if ($Full) { $viol } else { $sig | ForEach-Object { "   " + ($_ -replace ' violates rule ', ' | ') } }
    }
}

if ($Report) {
    $fab = "$ToolRoot\fab-inspector\win-x64\CLI\PBIRInspectorCLI.exe"
    $rules = "$ToolRoot\fab-inspector\Base-rules.json"
    $custom = Join-Path $root "scripts\lint-rules\fab.json"
    if (Test-Path $custom) { $rules = $custom }
    if (-not (Test-Path $fab) -or -not (Test-Path $rules)) { throw "Report lint unavailable: executable or rules missing ($fab, $rules)" }
    else {
        $out = Join-Path $OutDir "fab.txt"
        & $fab -fabricitem $rp -rules $rules -formats Console,JSON -output $OutDir 2>&1 | Out-File -Encoding utf8 $out
        if ($LASTEXITCODE -ne 0) { throw "Report lint failed (exit $LASTEXITCODE); see $out" }
        $lines = Get-Content $out
        $summary = $lines | Where-Object { $_ -match 'Test run summary' }
        Write-Host "`n== Report lint (fab-inspector) == $summary  (log: $out)"
        $lines | Where-Object { $_ -match 'Rule "(.+?)" FAILED' } |
            ForEach-Object { ($_ -replace '.*Rule "(.+?)" FAILED.*', '$1') } |
            Group-Object | Sort-Object Count -Descending | ForEach-Object { "{0,5}  {1}" -f $_.Count, $_.Name }
        if ($summary -match '(\d+) errors') { $fabErrors = [int]$Matches[1]; $signal += $fabErrors }
        else { throw "Report lint produced no usable summary; see $out" }
        if ($Full) { $lines | Where-Object { $_ -match 'FAILED' } }
    }
}

Write-Host "`nsignal total: $signal"
$baselinePath = Join-Path $root "scripts\lint-rules\signal-baseline.txt"
if ($UpdateBaseline) {
    if (-not ($Model -and $Report)) { throw "-UpdateBaseline needs a full run (model + report)" }
    $body = @("# Known lint signal findings - KNOWN, not accepted. Owners/triage: knowledge/PENDING_DECISIONS.md",
              "# Regenerate: powershell -File scripts/lint_pbip.ps1 -UpdateBaseline  (review the diff before committing)",
              "fab-errors: $fabErrors") + ($sigRows | Sort-Object)
    New-Item -ItemType Directory -Force (Split-Path $baselinePath) | Out-Null
    [IO.File]::WriteAllLines($baselinePath, [string[]]$body, (New-Object Text.UTF8Encoding $false))
    Write-Host "baseline written: $baselinePath ($($sigRows.Count) rows, fab errors $fabErrors)"
    exit 0
}
if (-not (Test-Path $baselinePath)) { Write-Host "no baseline file: every signal finding counts"; exit $signal }
$base = @(Get-Content $baselinePath -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith('#') })
$baseFab = [int](($base | Where-Object { $_ -match '^fab-errors: (\d+)$' } | Select-Object -First 1) -replace '\D', '')
$known = @{}; $base | Where-Object { $_ -notmatch '^fab-errors:' } | ForEach-Object { $known[$_] = 1 + [int]$known[$_] }
$new = @()
if ($Model) {
    foreach ($row in $sigRows) { if ($known[$row] -gt 0) { $known[$row]-- } else { $new += $row } }
    $resolved = @($known.GetEnumerator() | Where-Object { $_.Value -gt 0 } | ForEach-Object { $_.Key })
    Write-Host "baseline: $($sigRows.Count - $new.Count) known signal rows, $($resolved.Count) resolved since baseline"
    $resolved | ForEach-Object { "   resolved: $_" }
}
$newFab = if ($Report) { [Math]::Max(0, $fabErrors - $baseFab) } else { 0 }
if ($new.Count -or $newFab) {
    Write-Host "`n!! NEW signal findings not in baseline: $($new.Count) model, $newFab report errors"
    $new | ForEach-Object { "   NEW: $_" }
} else { Write-Host "no new signal findings versus baseline" }
exit ($new.Count + $newFab)
