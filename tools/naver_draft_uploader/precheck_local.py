from __future__ import annotations

import argparse
import json
import os

from config import UploaderConfig
from local_playwright_adapter import LocalPlaywrightNaverAdapter
from runner import AdapterError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.local.json")
    parser.add_argument("--profile-dir", default=os.environ.get("NAVER_BROWSER_PROFILE", ".naver-browser-profile"))
    parser.add_argument("--channel", default=os.environ.get("NAVER_BROWSER_CHANNEL", "chrome"))
    args = parser.parse_args()

    cfg = UploaderConfig.load(args.config)
    problems = cfg.validate()
    if problems:
        print(json.dumps({"status":"CONFIG_INVALID","problems":problems}, ensure_ascii=False))
        return 2

    adapter = LocalPlaywrightNaverAdapter(
        user_data_dir=args.profile_dir,
        browser_channel=args.channel,
        headless=False,
    ).start()

    try:
        result = adapter.precheck()
        print(json.dumps({
            "status":"PRECHECK_OK",
            "target_blog":cfg.target_blog,
            "allow_publish":cfg.allow_publish,
            "account_ok":bool(result.get("account_ok")),
            "blog_ok":bool(result.get("blog_ok")),
        }, ensure_ascii=False))
        return 0
    except AdapterError as exc:
        print(json.dumps({
            "status":"PRECHECK_FAILED",
            "error_code":exc.code,
            "error_message":str(exc),
        }, ensure_ascii=False))
        return 3
    finally:
        adapter.stop()


if __name__ == "__main__":
    raise SystemExit(main())
