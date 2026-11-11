from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

from state_machine import DraftLock, State, append_jsonl, checkpoint, load_manifest, validate_pre_save


TERMINAL_FAILURES = {
    "MANUAL_AUTH_REQUIRED",
    "FOREIGN_DRAFT_DETECTED",
    "MANUAL_REVIEW_REQUIRED",
    "SAVE_STATUS_UNKNOWN",
}


class AdapterError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class NaverAdapter:
    """
    Browser adapter contract.

    This file deliberately contains no site-specific selector automation yet.
    The real adapter must obey the safety contract and may only be enabled
    after Phase-1 authenticated browser access is available for verification.
    """

    def precheck(self):
        raise NotImplementedError

    def open_editor(self):
        raise NotImplementedError

    def read_editor_snapshot(self):
        raise NotImplementedError

    def set_title(self, title: str):
        raise NotImplementedError

    def set_body_plain_text(self, body: str):
        raise NotImplementedError

    def upload_images(self, images: list[dict]) -> int:
        raise NotImplementedError

    def apply_minimal_formatting(self):
        raise NotImplementedError

    def click_temporary_save(self):
        raise NotImplementedError

    def locate_saved_draft(self, *, title: str, content_id: str):
        raise NotImplementedError

    def reopen_draft(self, draft):
        raise NotImplementedError

    def verify_reopened_content(self, manifest):
        raise NotImplementedError


class DryRunAdapter(NaverAdapter):
    def __init__(self, fixture: dict):
        self.fixture = fixture
        self.title = ""
        self.body = ""
        self.images = 0
        self.saved = False

    def precheck(self):
        code = self.fixture.get("precheck_error")
        if code:
            raise AdapterError(code, code)
        return {"account_ok": True, "blog_ok": True}

    def open_editor(self):
        if self.fixture.get("existing_foreign_draft"):
            raise AdapterError("FOREIGN_DRAFT_DETECTED", "unexpected content already in editor")
        return True

    def read_editor_snapshot(self):
        return {"title": self.title, "body": self.body, "image_count": self.images}

    def set_title(self, title: str):
        self.title = title if not self.fixture.get("title_corrupt") else title[:-1]
        return self.title

    def set_body_plain_text(self, body: str):
        self.body = body if not self.fixture.get("body_truncate") else body[: max(1, len(body)//3)]
        return self.body

    def upload_images(self, images: list[dict]) -> int:
        expected = len(images)
        self.images = expected - 1 if self.fixture.get("image_short") and expected else expected
        return self.images

    def apply_minimal_formatting(self):
        return True

    def click_temporary_save(self):
        if self.fixture.get("save_unknown"):
            raise AdapterError("SAVE_STATUS_UNKNOWN", "save request outcome unknown")
        self.saved = True
        return True

    def locate_saved_draft(self, *, title: str, content_id: str):
        if self.fixture.get("draft_not_found"):
            raise AdapterError("DRAFT_NOT_FOUND", "draft not found after save")
        return {"draft_id": "dry-run-1", "title": title, "content_id": content_id}

    def reopen_draft(self, draft):
        if self.fixture.get("reopen_fail"):
            raise AdapterError("REOPEN_FAILED", "failed to reopen")
        return True

    def verify_reopened_content(self, manifest):
        if self.fixture.get("content_mismatch"):
            raise AdapterError("CONTENT_MISMATCH", "reopened content mismatch")
        return {
            "title_ok": self.title == manifest.title,
            "body_ok": self.body == manifest.body_text,
            "image_count": self.images,
        }


def run(manifest_path: Path, workdir: Path, adapter: NaverAdapter):
    manifest = load_manifest(manifest_path)
    job_id = f"naver-{manifest.content_id}-{uuid.uuid4().hex[:8]}"
    runner_id = os.environ.get("RUNNER_ID", "local")
    state_path = workdir / "state" / f"{manifest.content_id}.json"
    ledger = workdir / "ledger.jsonl"
    lock = DraftLock(workdir / "naver_draft_lock.json")

    current = State.CONTENT_READY
    append_jsonl(ledger, {"job_id": job_id, "content_id": manifest.content_id, "event": current.value, "ts": time.time()})

    try:
        lock.acquire(job_id=job_id, manifest=manifest, runner_id=runner_id, state=State.LOCK_ACQUIRED.value)
        current = State.LOCK_ACQUIRED
        checkpoint(state_path, manifest, current)

        adapter.precheck()
        current = State.PRECHECK
        checkpoint(state_path, manifest, current)
        lock.heartbeat(current.value)

        adapter.open_editor()
        current = State.EDITOR_OPEN
        checkpoint(state_path, manifest, current)
        lock.heartbeat(current.value)

        snap = adapter.read_editor_snapshot()
        if (snap.get("title") or "").strip() or (snap.get("body") or "").strip() or int(snap.get("image_count", 0)):
            raise AdapterError("FOREIGN_DRAFT_DETECTED", "editor not empty before input")

        actual_title = adapter.set_title(manifest.title)
        if actual_title.strip() != manifest.title.strip():
            raise AdapterError("TITLE_INPUT_FAILED", "title readback mismatch")
        current = State.TITLE_DONE
        checkpoint(state_path, manifest, current)

        actual_body = adapter.set_body_plain_text(manifest.body_text)
        if len(actual_body.strip()) < max(1, int(len(manifest.body_text.strip()) * .80)):
            raise AdapterError("BODY_INPUT_FAILED", "body readback too short")
        current = State.BODY_DONE
        checkpoint(state_path, manifest, current)

        image_uploaded = adapter.upload_images(manifest.images)
        if image_uploaded < len(manifest.images):
            raise AdapterError("IMAGE_UPLOAD_FAILED", "uploaded image count short")
        current = State.IMAGE_DONE
        checkpoint(state_path, manifest, current, image_uploaded=image_uploaded)

        adapter.apply_minimal_formatting()
        current = State.FORMAT_DONE
        checkpoint(state_path, manifest, current)

        problems = validate_pre_save(actual_title, actual_body, manifest, image_uploaded)
        if problems:
            raise AdapterError("PRE_SAVE_VALIDATION_FAILED", ",".join(problems))
        current = State.PRE_SAVE_VALIDATED
        checkpoint(state_path, manifest, current)

        current = State.SAVE_INTENT
        checkpoint(state_path, manifest, current)
        lock.heartbeat(current.value)

        adapter.click_temporary_save()
        current = State.SAVE_CLICKED
        checkpoint(state_path, manifest, current)
        lock.heartbeat(current.value)

        draft = adapter.locate_saved_draft(title=manifest.title, content_id=manifest.content_id)
        current = State.DRAFT_FOUND
        checkpoint(state_path, manifest, current, draft=draft)

        adapter.reopen_draft(draft)
        current = State.REOPENED
        checkpoint(state_path, manifest, current)

        verify = adapter.verify_reopened_content(manifest)
        if not verify.get("title_ok") or not verify.get("body_ok") or int(verify.get("image_count", 0)) < len(manifest.images):
            raise AdapterError("CONTENT_MISMATCH", json.dumps(verify, ensure_ascii=False))
        current = State.CONTENT_VERIFIED
        checkpoint(state_path, manifest, current, verification=verify)

        current = State.VERIFIED
        checkpoint(state_path, manifest, current, verification=verify)
        append_jsonl(ledger, {"job_id": job_id, "content_id": manifest.content_id, "event": current.value, "ts": time.time()})
        return 0, current.value

    except AdapterError as e:
        terminal = e.code if e.code in TERMINAL_FAILURES else "RETRY_PENDING"
        checkpoint(state_path, manifest, State(terminal) if terminal in State._value2member_map_ else State.RETRY_PENDING,
                   error_code=e.code, error_message=str(e))
        append_jsonl(ledger, {"job_id": job_id, "content_id": manifest.content_id, "event": terminal,
                              "error_code": e.code, "error_message": str(e), "ts": time.time()})
        return 2, terminal

    except RuntimeError as e:
        code = str(e)
        if code == "SAVE_STATUS_UNKNOWN":
            state = State.SAVE_STATUS_UNKNOWN
            terminal = state.value
        elif code == "LOCKED":
            terminal = "SKIPPED_LOCKED"
            append_jsonl(ledger, {"job_id": job_id, "content_id": manifest.content_id, "event": terminal, "ts": time.time()})
            return 4, terminal
        else:
            state = State.RETRY_PENDING
            terminal = state.value
            code = "RETRY_PENDING"

        checkpoint(state_path, manifest, state, error_code=code, error_message=str(e))
        append_jsonl(ledger, {"job_id": job_id, "content_id": manifest.content_id, "event": terminal,
                              "error_code": code, "error_message": str(e), "ts": time.time()})
        return 2, terminal

    finally:
        lock.release()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--workdir", default=".naver-draft-runtime")
    parser.add_argument("--dry-run-fixture")
    args = parser.parse_args()

    if not args.dry_run_fixture:
        print("Real browser adapter is intentionally disabled until authenticated Phase-1 access is available.", file=sys.stderr)
        return 3

    fixture = json.loads(Path(args.dry_run_fixture).read_text(encoding="utf-8"))
    code, state = run(Path(args.manifest), Path(args.workdir), DryRunAdapter(fixture))
    print(state)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
