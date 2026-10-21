# Close Power BI Desktop gracefully WITHOUT saving (handles the Save? dialog via UI Automation).
Add-Type -AssemblyName UIAutomationClient; Add-Type -AssemblyName UIAutomationTypes; Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System; using System.Runtime.InteropServices;
public class PbiFg { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
'@
$proc = Get-Process PBIDesktop -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) { "not running"; return }
[PbiFg]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$proc.CloseMainWindow() | Out-Null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 700
    if ($proc.HasExited) { "closed (no dialog)"; return }
    try {
        $root = [System.Windows.Automation.AutomationElement]::FromHandle((Get-Process PBIDesktop | Select-Object -First 1).MainWindowHandle)
        $btns = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))
        foreach ($b in $btns) {
            if ($b.Current.Name -match "^Don.?t save$|^Don't Save$") {
                "dialog: clicking '" + $b.Current.Name + "'"
                $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
                Start-Sleep 3
                if ((Get-Process PBIDesktop -ErrorAction SilentlyContinue) -eq $null) { "closed without saving"; return }
            }
        }
    } catch {}
}
"still running - check for a dialog"; Get-Process PBIDesktop -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle
