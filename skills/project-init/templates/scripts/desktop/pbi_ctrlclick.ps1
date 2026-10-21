# Ctrl+click at screen coords inside Power BI Desktop (edit-mode button activation), then screenshot.
param([int]$X, [int]$Y, [string]$OutputPath, [int]$SettleMs = 2500, [switch]$NoCtrl)
Add-Type @'
using System; using System.Runtime.InteropServices;
public class PbiInput {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte k, byte s, uint f, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
}
'@
$proc = Get-Process PBIDesktop | Select-Object -First 1
[PbiInput]::ShowWindow($proc.MainWindowHandle, 9) | Out-Null
[PbiInput]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 400
[PbiInput]::SetCursorPos($X, $Y) | Out-Null
Start-Sleep -Milliseconds 200
if (-not $NoCtrl) { [PbiInput]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero) }
Start-Sleep -Milliseconds 100
[PbiInput]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)      # left down
Start-Sleep -Milliseconds 80
[PbiInput]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)      # left up
Start-Sleep -Milliseconds 100
if (-not $NoCtrl) { [PbiInput]::keybd_event(0x11, 0, 0x0002, [UIntPtr]::Zero) }
Start-Sleep -Milliseconds $SettleMs
if ($OutputPath) { & (Join-Path $PSScriptRoot "pbi_screenshot.ps1") -OutputPath $OutputPath | Out-Null; "Saved: $OutputPath" }
