# Navigate Power BI Desktop to a page tab by (partial) name using UI Automation, then screenshot.
param(
    [Parameter(Mandatory)][string]$PageName,
    [string]$OutputPath,
    [switch]$ListOnly
)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$proc = Get-Process PBIDesktop -ErrorAction Stop | Select-Object -First 1
$root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)
$tabs = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::TabItem -and $_.Current.ClassName -like "section*" }
if ($ListOnly) { $tabs | ForEach-Object { $_.Current.Name }; return }
$target = $null
foreach ($t in $tabs) { if ($t.Current.Name -like "*$PageName*") { $target = $t; break } }
if (-not $target) { Write-Error "Tab not found: $PageName"; $tabs | ForEach-Object { $_.Current.Name }; return }
try {
    $sel = $target.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
    $sel.Select()
} catch {
    try { $target.SetFocus(); [System.Windows.Forms.SendKeys]::SendWait(" ") } catch {}
}
Start-Sleep -Milliseconds 2500
"Selected: " + $target.Current.Name
if ($OutputPath) { & (Join-Path $PSScriptRoot "pbi_screenshot.ps1") -OutputPath $OutputPath | Out-Null; "Saved: $OutputPath" }
