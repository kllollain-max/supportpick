$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$config = Join-Path $root "config.local.json"
$profile = Join-Path $root ".naver-browser-profile"

python "$root\precheck_local.py" --config "$config" --profile-dir "$profile" --channel chrome
exit $LASTEXITCODE
