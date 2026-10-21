# Screenshot every page tab of the running Power BI Desktop via UI Automation (~4 min for 43 pages).
# Usage: powershell -File scripts/desktop/sweep.ps1 [-OutDir <dir>]
#        default OutDir = %TEMP%\pbi_sweep_<timestamp>. Desktop must be open with the report loaded.
# Pattern origin: gotcha #143 (rendered sweep after any model-wide font/layout change).
param([string]$OutDir = "$env:TEMP\pbi_sweep_$(Get-Date -Format yyyyMMdd_HHmmss)")
$out = $OutDir; New-Item -ItemType Directory -Force $out | Out-Null
Add-Type -AssemblyName UIAutomationClient; Add-Type -AssemblyName UIAutomationTypes
$proc = Get-Process PBIDesktop -ErrorAction Stop | Select-Object -First 1
$root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
$tabs = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::TabItem -and $_.Current.ClassName -like "section*" }
$i = 0
foreach ($t in $tabs) {
    $i++
    $name = $t.Current.Name
    try { $t.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select() } catch { "skip $name"; continue }
    Start-Sleep -Milliseconds 3500
    $safe = ($name -replace '[^A-Za-z0-9]+', '_').Trim('_')
    $file = "$out\{0:D2}_{1}.png" -f $i, $safe
    & (Join-Path $PSScriptRoot "pbi_screenshot.ps1") -OutputPath $file | Out-Null
    "{0:D2} {1}" -f $i, $name
}
"output: $out"
