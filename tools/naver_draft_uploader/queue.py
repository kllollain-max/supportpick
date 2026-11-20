from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time


TERMINAL_STATES = {
    "VERIFIED",
    "MANUAL_REVIEW_REQUIRED",
    "MANUAL_AUTH_REQUIRED",
    "FOREIGN_DRAFT_DETECTED",
}


@dataclass
class QueueItem:
    content_id: str
    manifest_path: str
    state: str = "NAVER_QUEUE"
    retry_count: int = 0
    first_enqueued_at: float = 0.0
    updated_at: float = 0.0

    def touch(self):
        now = time.time()
        if not self.first_enqueued_at:
            self.first_enqueued_at = now
        self.updated_at = now


class QueueStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _load_raw(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def load(self) -> list[QueueItem]:
        return [QueueItem(**row) for row in self._load_raw()]

    def save(self, items: list[QueueItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def enqueue_once(self, item: QueueItem) -> str:
        items = self.load()
        for current in items:
            if current.content_id == item.content_id:
                return "DUPLICATE_QUEUE_ITEM"
        item.touch()
        items.append(item)
        self.save(items)
        return "ENQUEUED"

    def next_runnable(self) -> QueueItem | None:
        for item in self.load():
            if item.state not in TERMINAL_STATES:
                return item
        return None

    def update_state(self, content_id: str, state: str, retry_increment: bool = False) -> None:
        items = self.load()
        found = False
        for item in items:
            if item.content_id == content_id:
                item.state = state
                if retry_increment:
                    item.retry_count += 1
                item.touch()
                found = True
                break
        if not found:
            raise KeyError(content_id)
        self.save(items)
