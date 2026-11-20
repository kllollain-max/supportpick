"""Disabled legacy write entry point. Read-only preparation has its own launcher."""
import json


def main():
    print(json.dumps({
        "status": "LIVE_ADAPTER_NOT_READY",
        "write_performed": False,
        "save_performed": False,
        "verified": False,
        "next_step": "Use windows_starter/01_SETUP.cmd, 02_LOGIN.cmd, then 03_INSPECT.cmd. Do not enable the uploader yet."
    }, ensure_ascii=False))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
