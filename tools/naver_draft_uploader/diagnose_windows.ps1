$ErrorActionPreference = "Continue"

Write-Host "=== SupportPick Local Naver Uploader Diagnostics ==="

Write-Host ""
Write-Host "[1] Python"
python --version

Write-Host ""
Write-Host "[2] Playwright package"
python -c "import playwright; print('playwright import OK')"

Write-Host ""
Write-Host "[3] Chrome"
$chromeCandidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$foundChrome = $false
foreach ($c in $chromeCandidates) {
  if (Test-Path $c) {
    Write-Host "Chrome found: $c"
    $foundChrome = $true
    break
  }
}
if (-not $foundChrome) { Write-Host "Chrome not found in common locations" }

Write-Host ""
Write-Host "[4] Local config"
$config = Join-Path $PSScriptRoot "config.local.json"
if (Test-Path $config) { Get-Content $config } else { Write-Host "config.local.json not found" }

Write-Host ""
Write-Host "[5] Browser profile"
$profile = Join-Path $PSScriptRoot ".naver-browser-profile"
if (Test-Path $profile) { Write-Host "Profile exists: $profile" } else { Write-Host "Profile not created yet" }

Write-Host ""
Write-Host "[6] Phase-1 manifest"
$manifest = Join-Path $PSScriptRoot "phase1_candidate.json"
if (Test-Path $manifest) { Write-Host "Manifest exists" } else { Write-Host "Manifest missing" }

Write-Host ""
Write-Host "Diagnostics complete."
