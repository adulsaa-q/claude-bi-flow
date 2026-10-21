<#
.SYNOPSIS
  Capture a real screenshot of the running Power BI Desktop window.

.NOTES
  Power BI Desktop's report canvas is GPU/WebView-rendered, so the usual
  PrintWindow API returns a blank canvas. This uses CopyFromScreen instead,
  which requires the window to actually be on screen and in the foreground.

  Side effect: briefly steals focus to bring Power BI Desktop to the front,
  then restores whatever window had focus before the call. Expect a
  ~0.5-1 second flash on screen - this cannot be done fully silently with
  this technique. Use it deliberately (e.g. to verify a visual/theme change),
  not on every small edit.

.PARAMETER OutputPath
  Where to save the PNG. Defaults to a timestamped temp file.

.PARAMETER ProcessName
  Process to capture. Defaults to PBIDesktop.
#>
param(
    [string]$OutputPath = "$env:TEMP\pbi_screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png",
    [string]$ProcessName = "PBIDesktop",
    [switch]$CheckDependencies
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
if (-not ('PbiWinCap' -as [type])) {
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class PbiWinCap {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
}
if ($CheckDependencies) { "Screenshot dependencies OK ($($PSVersionTable.PSEdition))"; return }

$processes = @(Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)
if ($processes.Count -gt 1) { throw "Multiple $ProcessName processes; select one before capturing." }
$proc = $processes | Select-Object -First 1
if (-not $proc) {
    throw "$ProcessName is not running."
}

$previousForeground = [PbiWinCap]::GetForegroundWindow()
$hwnd = $proc.MainWindowHandle

[PbiWinCap]::ShowWindow($hwnd, 9) | Out-Null   # SW_RESTORE, in case minimized
[PbiWinCap]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 400

try {
    $rect = New-Object PbiWinCap+RECT
    [PbiWinCap]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    $bmp = New-Object System.Drawing.Bitmap $width, $height
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)
    $gfx.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size $width, $height))
    $bmp.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $gfx.Dispose()
    $bmp.Dispose()
}
finally {
    [PbiWinCap]::SetForegroundWindow($previousForeground) | Out-Null
}

Write-Output $OutputPath
