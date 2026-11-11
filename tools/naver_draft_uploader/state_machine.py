from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional
import hashlib
import json
import os
import time


class State(str, Enum):
    CONTENT_READY = "CONTENT_READY"
    NAVER_QUEUE = "NAVER_QUEUE"
    LOCK_ACQUIRED = "LOCK_ACQUIRED"
    PRECHECK = "PRECHECK"
    EDITOR_OPEN = "EDITOR_OPEN"
    TITLE_DONE = "TITLE_DONE"
    BODY_DONE = "BODY_DONE"
    IMAGE_DONE = "IMAGE_DONE"
    FORMAT_DONE = "FORMAT_DONE"
    PRE_SAVE_VALIDATED = "PRE_SAVE_VALIDATED"
    SAVE_INTENT = "SAVE_INTENT"
    SAVE_CLICKED = "SAVE_CLICKED"
    DRAFT_FOUND = "DRAFT_FOUND"
    REOPENED = "REOPENED"
    CONTENT_VERIFIED = "CONTENT_VERIFIED"
    VERIFIED = "VERIFIED"

    SAVE_STATUS_UNKNOWN = "SAVE_STATUS_UNKNOWN"
    RETRY_PENDING = "RETRY_PENDING"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    MANUAL_AUTH_REQUIRED = "MANUAL_AUTH_REQUIRED"
    EXISTING_UNVERIFIED_DRAFT = "EXISTING_UNVERIFIED_DRAFT"
    FOREIGN_DRAFT_DETECTED = "FOREIGN_DRAFT_DETECTED"


ERROR_CODES = {
    "LOCKED", "LOGIN_REQUIRED", "MANUAL_AUTH_REQUIRED", "NAVER_RESTRICTED",
    "NETWORK_UNSTABLE", "BROWSER_START_FAILED", "BROWSER_RECOVERY_FAILED",
    "BROWSER_TARGET_MISSING", "EDITOR_NOT_READY", "TITLE_INPUT_FAILED",
    "BODY_INPUT_FAILED", "IMAGE_UPLOAD_FAILED", "FORMAT_FAILED",
    "PRE_SAVE_VALIDATION_FAILED", "SAVE_CLICK_FAILED", "SAVE_STATUS_UNKNOWN",
    "DRAFT_NOT_FOUND", "REOPEN_FAILED", "CONTENT_MISMATCH",
    "DUPLICATE_DRAFT_FOUND", "FOREIGN_DRAFT_DETECTED", "RETRY_PENDING",
    "MANUAL_REVIEW_REQUIRED", "VERIFIED",
}


@dataclass
class Manifest:
    content_id: str
    title: str
    body_text: str
    images: list[dict]
    cta_text: str
    cta_url: str
    created_at: Optional[str] = None

    @property
    def title_hash(self) -> str:
        return hashlib.sha256(self.title.strip().encode("utf-8")).hexdigest()

    @property
    def body_hash(self) -> str:
        normalized = "\n".join(line.rstrip() for line in self.body_text.replace("\r\n", "\n").split("\n")).strip()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass
class RunRecord:
    job_id: str
    content_id: str
    title: str
    state_before: str
    state_after: str
    start_time: float
    end_time: Optional[float] = None
    browser: Optional[str] = None
    browser_version: Optional[str] = None
    retry_count: int = 0
    editor_detected: bool = False
    title_done: bool = False
    body_done: bool = False
    image_expected: int = 0
    image_uploaded: int = 0
    save_clicked: bool = False
    draft_found: bool = False
    reopened: bool = False
    verified: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    recovery_action: Optional[str] = None


def load_manifest(path: str | Path) -> Manifest:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"content_id", "title", "body_text", "images", "cta_text", "cta_url"}
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"manifest missing fields: {missing}")
    m = Manifest(**raw)
    if not m.content_id.startswith("supportpick-"):
        raise ValueError("invalid SupportPick content_id")
    if m.cta_text.strip() not in m.body_text:
        raise ValueError("approved SupportPick CTA missing from body")
    if m.cta_url.strip() not in m.body_text:
        raise ValueError("SupportPick CTA URL missing from body")
    return m


def append_jsonl(path: str | Path, payload: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class DraftLock:
    def __init__(self, path: str | Path, stale_after_s: int = 1800):
        self.path = Path(path)
        self.stale_after_s = stale_after_s
        self.owned = False

    def acquire(self, *, job_id: str, manifest: Manifest, runner_id: str, state: str) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()
        if self.path.exists():
            current = json.loads(self.path.read_text(encoding="utf-8"))
            hb = float(current.get("heartbeat", current.get("acquired_at", 0)))
            if now - hb <= self.stale_after_s:
                raise RuntimeError("LOCKED")
            # A stale lock is never silently discarded when a save may have happened.
            if current.get("state") in {"SAVE_INTENT", "SAVE_CLICKED", "SAVE_STATUS_UNKNOWN"}:
                raise RuntimeError("SAVE_STATUS_UNKNOWN")

        payload = {
            "job_id": job_id,
            "content_id": manifest.content_id,
            "title_hash": manifest.title_hash,
            "acquired_at": now,
            "heartbeat": now,
            "runner_id": runner_id,
            "state": state,
        }
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        finally:
            os.close(fd)
        self.owned = True
        return payload

    def heartbeat(self, state: str) -> None:
        if not self.owned:
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload["heartbeat"] = time.time()
        payload["state"] = state
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def release(self) -> None:
        if self.owned and self.path.exists():
            self.path.unlink()
        self.owned = False


def checkpoint(path: str | Path, manifest: Manifest, state: State, **extra) -> None:
    payload = {
        "content_id": manifest.content_id,
        "title_hash": manifest.title_hash,
        "body_hash": manifest.body_hash,
        "state": state.value,
        "updated_at": time.time(),
        **extra,
    }
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def validate_pre_save(title: str, body: str, expected: Manifest, image_uploaded: int) -> list[str]:
    problems = []
    if not title.strip():
        problems.append("title_missing")
    if title.strip() != expected.title.strip():
        problems.append("title_mismatch")
    body_norm = body.strip()
    if not body_norm:
        problems.append("body_missing")
    if expected.cta_text not in body_norm:
        problems.append("cta_text_missing")
    if expected.cta_url not in body_norm:
        problems.append("cta_url_missing")

    expected_len = max(1, len(expected.body_text.strip()))
    actual_len = len(body_norm)
    if actual_len < expected_len * 0.80:
        problems.append("body_too_short")
    if image_uploaded < len(expected.images):
        problems.append("image_count_short")
    return problems
