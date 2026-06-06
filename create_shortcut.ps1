# Run this script ONCE to create a Desktop shortcut for DeskReminder
# Right-click this file -> "Run with PowerShell"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$lnkPath  = Join-Path $desktop 'DeskReminder.lnk'
$iconPath = Join-Path $projectDir 'assets\logo.ico'
$batPath  = Join-Path $projectDir 'DeskReminder.bat'

$wsh      = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($lnkPath)

$shortcut.TargetPath       = $batPath
$shortcut.WorkingDirectory = $projectDir
$shortcut.WindowStyle      = 1
$shortcut.IconLocation     = $iconPath
$shortcut.Description      = 'DeskReminder - Desktop Reminder Widget'
$shortcut.Save()

Write-Host "✅ Desktop shortcut created at: $lnkPath" -ForegroundColor Green
