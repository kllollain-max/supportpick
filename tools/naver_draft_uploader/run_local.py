from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from config import UploaderConfig
from local_playwright_adapter import LocalPlaywrightNaverAdapter
from runner import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--config", default="config.local.json")
    parser.add_argument("--workdir", default=".naver-draft-runtime")
    parser.add_argument("--profile-dir", default=os.environ.get("NAVER_BROWSER_PROFILE", ".naver-browser-profile"))
    parser.add_argument("--channel", default=os.environ.get("NAVER_BROWSER_CHANNEL", "chrome"))
    args = parser.parse_args()

    cfg = UploaderConfig.load(args.config)
    problems = cfg.validate()
    if problems:
        print(json.dumps({"status": "CONFIG_INVALID", "problems": problems}, ensure_ascii=False))
        return 2
    if not cfg.enabled:
        print(json.dumps({"status": "DISABLED"}, ensure_ascii=False))
        return 3

    adapter = LocalPlaywrightNaverAdapter(
        user_data_dir=args.profile_dir,
        browser_channel=args.channel,
        headless=False,
    ).start()
    try:
        code, state = run(Path(args.manifest), Path(args.workdir), adapter)
        print(json.dumps({"status": state}, ensure_ascii=False))
        return code
    finally:
        adapter.stop()


if __name__ == "__main__":
    raise SystemExit(main())
