$ErrorActionPreference = "Stop"

Write-Host "[SupportPick] Local Naver Draft Uploader setup"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python not found. Install Python 3.11+ first."
}

python -m pip install --upgrade pip
python -m pip install -r "$PSScriptRoot\requirements-local.txt"
python -m playwright install chromium

$configPath = Join-Path $PSScriptRoot "config.local.json"
if (-not (Test-Path $configPath)) {
@'
{
  "enabled": false,
  "allow_publish": false,
  "target_blog": "bible_el",
  "max_parallel": 1,
  "require_reopen_verification": true,
  "require_correct_account": true
}
'@ | Set-Content -Encoding UTF8 $configPath
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "1) Leave enabled=false until first manual login/precheck."
Write-Host "2) Run login_once.ps1 to open the local browser profile."
Write-Host "3) Log in to Naver manually if required."
Write-Host "4) Never enable allow_publish."
