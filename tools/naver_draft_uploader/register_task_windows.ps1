param(
  [string]$TaskName = "SupportPick Naver Draft Uploader",
  [string]$Time = "10:30"
)

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$runner = Join-Path $root "run_phase1_windows.ps1"

if (-not (Test-Path $runner)) {
  throw "Runner not found: $runner"
}

$parts = $Time.Split(":")
if ($parts.Count -ne 2) {
  throw "Time must be HH:MM"
}

$hour = [int]$parts[0]
$minute = [int]$parts[1]

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.AddHours($hour).AddMinutes($minute))
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "SupportPick Naver draft-only uploader. Publish remains disabled." -Force

Write-Host "Registered: $TaskName at $Time"
Write-Host "Important: do not use scheduler until Phase 1 -> 3 -> 5 verification is complete."
