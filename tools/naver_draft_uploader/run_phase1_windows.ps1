$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$config = Join-Path $root "config.local.json"
$manifest = Join-Path $root "phase1_candidate.json"
$workdir = Join-Path $root ".naver-draft-runtime"
$profile = Join-Path $root ".naver-browser-profile"

python "$root\run_local.py" "$manifest" --config "$config" --workdir "$workdir" --profile-dir "$profile" --channel chrome
exit $LASTEXITCODE
