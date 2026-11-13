$ErrorActionPreference = "Stop"

$profile = Join-Path $PSScriptRoot ".naver-browser-profile"
$script = @"
from playwright.sync_api import sync_playwright
from pathlib import Path
p = sync_playwright().start()
profile = r'''$profile'''
Path(profile).mkdir(parents=True, exist_ok=True)
ctx = p.chromium.launch_persistent_context(profile, channel="chrome", headless=False)
page = ctx.pages[0] if ctx.pages else ctx.new_page()
page.goto("https://blog.naver.com/bible_el")
print("Naver browser opened. Log in manually if needed. Close the browser window when finished.")
page.wait_for_timeout(600000)
ctx.close()
p.stop()
"@

python -c $script
