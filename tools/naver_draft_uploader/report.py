from __future__ import annotations

from pathlib import Path
import json
import time


def build_report(*, manifest: dict, state: dict, browser: str | None = None,
                 browser_version: str | None = None) -> dict:
    final_state = state.get("state")
    return {
        "kind": "supportpick_naver_draft_report_v1",
        "content_id": manifest.get("content_id"),
        "title": manifest.get("title"),
        "browser": browser,
        "browser_version": browser_version,
        "title_input": bool(state.get("title_done") or final_state in {
            "TITLE_DONE","BODY_DONE","IMAGE_DONE","FORMAT_DONE","PRE_SAVE_VALIDATED",
            "SAVE_INTENT","SAVE_CLICKED","DRAFT_FOUND","REOPENED","CONTENT_VERIFIED","VERIFIED"
        }),
        "body_input": bool(state.get("body_done") or final_state in {
            "BODY_DONE","IMAGE_DONE","FORMAT_DONE","PRE_SAVE_VALIDATED",
            "SAVE_INTENT","SAVE_CLICKED","DRAFT_FOUND","REOPENED","CONTENT_VERIFIED","VERIFIED"
        }),
        "image_expected": len(manifest.get("images", [])),
        "image_uploaded": int(state.get("image_uploaded", state.get("verification", {}).get("image_count", 0))),
        "save_clicked": final_state in {
            "SAVE_CLICKED","DRAFT_FOUND","REOPENED","CONTENT_VERIFIED","VERIFIED"
        },
        "draft_found": final_state in {"DRAFT_FOUND","REOPENED","CONTENT_VERIFIED","VERIFIED"},
        "reopened": final_state in {"REOPENED","CONTENT_VERIFIED","VERIFIED"},
        "verified": final_state == "VERIFIED",
        "error_code": state.get("error_code"),
        "error_message": state.get("error_message"),
        "final_state": final_state,
        "reported_at": time.time(),
    }


def write_report(manifest_path: str | Path, state_path: str | Path, output_path: str | Path,
                 browser: str | None = None, browser_version: str | None = None) -> dict:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    report = build_report(
        manifest=manifest,
        state=state,
        browser=browser,
        browser_version=browser_version,
    )
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
