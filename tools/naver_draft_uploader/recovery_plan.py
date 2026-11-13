from __future__ import annotations

import json
from pathlib import Path

SAVE_SENSITIVE = {"SAVE_INTENT", "SAVE_CLICKED", "SAVE_STATUS_UNKNOWN"}


def recovery_action(state_payload: dict) -> str:
    state = state_payload.get("state")

    if state in SAVE_SENSITIVE:
        return "SEARCH_EXISTING_DRAFT_FIRST"

    if state in {"DRAFT_FOUND", "REOPENED", "CONTENT_VERIFIED"}:
        return "REOPEN_EXISTING_DRAFT_AND_VERIFY"

    if state in {"TITLE_DONE", "BODY_DONE", "IMAGE_DONE", "FORMAT_DONE", "PRE_SAVE_VALIDATED"}:
        return "INSPECT_CURRENT_EDITOR_BEFORE_RESUME"

    if state in {"MANUAL_AUTH_REQUIRED", "FOREIGN_DRAFT_DETECTED", "MANUAL_REVIEW_REQUIRED"}:
        return "STOP_FOR_MANUAL_REVIEW"

    if state == "VERIFIED":
        return "NO_ACTION"

    return "SAFE_PRECHECK_BEFORE_RETRY"


def write_recovery_receipt(state_path: str | Path, output_path: str | Path) -> dict:
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    receipt = {
        "content_id": state.get("content_id"),
        "state": state.get("state"),
        "action": recovery_action(state),
        "rule": "existing draft lookup always precedes new input when save outcome may be unknown",
    }
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    return receipt
