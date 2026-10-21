<#
.SYNOPSIS  Verify the BI + AI flow is installed and usable. Read-only; changes nothing.
.PARAMETER ClaudeHome  Config dir to inspect. Default ~\.claude
#>
param([string]$ClaudeHome = (Join-Path $env:USERPROFILE '.claude'))

$repo = $PSScriptRoot
$bad = 0
function Check($name, [bool]$ok, $detail = '', [switch]$Optional) {
    $s = if ($ok) { 'PASS' } elseif ($Optional) { 'OPT ' } else { 'FAIL'; $script:bad++ }
    $c = if ($ok) { 'Green' } elseif ($Optional) { 'Yellow' } else { 'Red' }
    Write-Host ("[{0}] {1} {2}" -f $s, $name, $detail) -ForegroundColor $c
}
function Ver($cmd, $arg = '--version') { try { ((& $cmd $arg 2>&1) | Select-Object -First 1) -join '' } catch { '' } }

Write-Host '== tools =='
foreach ($t in 'git', 'python', 'uv', 'claude', 'pbi') {
    $has = [bool](Get-Command $t -ErrorAction SilentlyContinue)
    Check $t $has $(if ($has) { Ver $t } else { 'missing' }) -Optional:($t -eq 'uv')
}
$pv = Ver python
Check 'python >= 3.11' ($pv -match 'Python 3\.(1[1-9]|[2-9]\d)') $pv
foreach ($t in 'sqlcmd', 'dscmd', 'duckdb', 'gh') {
    $has = [bool](Get-Command $t -ErrorAction SilentlyContinue)
    Check "$t (optional)" $has '' -Optional
}
$te2 = Join-Path $env:LOCALAPPDATA 'Programs\TabularEditor2\TabularEditor.exe'
Check 'Tabular Editor 2 (optional, offline BPA lint)' (Test-Path $te2) $te2 -Optional

Write-Host "`n== skills in $ClaudeHome\skills =="
$expected = @(Get-ChildItem (Join-Path $repo 'skills') -Directory | ForEach-Object Name) +
            @('power-bi-dax', 'power-bi-modeling', 'power-bi-report', 'power-bi-visuals', 'power-bi-pages', 'power-bi-themes',
              'power-bi-filters', 'power-bi-deployment', 'power-bi-docs', 'power-bi-diagnostics', 'power-bi-partitions',
              'power-bi-security', 'power-bi-custom-visuals')
foreach ($s in $expected) {
    $p = Join-Path $ClaudeHome "skills\$s\SKILL.md"
    Check "skill $s" (Test-Path $p)
}

Write-Host "`n== global rules =="
$md = Join-Path $ClaudeHome 'CLAUDE.md'
Check 'CLAUDE.md has team block' ((Test-Path $md) -and ((Get-Content $md -Raw) -match 'claude-bi-flow:begin'))

Write-Host "`n== plugins =="
if (Get-Command claude -ErrorAction SilentlyContinue) {
    $list = (claude plugin list 2>&1) -join "`n"
    foreach ($p in (Get-Content (Join-Path $repo 'plugins.txt') | Where-Object { $_ -and $_ -notmatch '^\s*#' })) {
        $n = $p.Split('@')[0]
        Check "plugin $n" ($list -match [regex]::Escape($n))
    }
}

Write-Host ''
if ($bad) { Write-Host "$bad required check(s) failed - see SETUP.md troubleshooting." -ForegroundColor Red; exit 1 }
Write-Host 'All required checks passed.' -ForegroundColor Green
