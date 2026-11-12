"""Select published verified Threads posts due for read-only 24h/72h/7d snapshots."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from supportpick_threads_insights import collect
from supportpick_threads_metrics import snapshot

WINDOWS = (24, 72, 168)


def due_records(state, now):
    result = []
    for row in state.get("records", []):
        if row.get("status") != "published" or row.get("verified") is not True:
            continue
        post_id, published = row.get("main_id"), row.get("published_at")
        if not isinstance(post_id, str) or not isinstance(published, str):
            continue
        try:
            at = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if at.tzinfo is None:
                continue
            hours = (now - at).total_seconds() / 3600
        except ValueError:
            continue
        if any(w <= hours <= w + 2 for w in WINDOWS):
            result.append((post_id, published))
    return result


def main():
    now = datetime.now(timezone.utc)
    state = json.loads(Path(os.environ.get("SUPPORTPICK_THREADS_STATE_FILE", "threads-state.json")).read_text())
    token = os.environ.get("SUPPORTPICK_THREADS_ACCESS_TOKEN", "")
    output = []
    for post_id, published in due_records(state, now):
        try:
            metrics = collect(post_id, token)
            output.append(snapshot(post_id, published, now.isoformat(), metrics))
        except (RuntimeError, ValueError):
            output.append({"post_id": post_id, "status": "unavailable",
                           "observed_at": now.isoformat(), "metrics": None})
    Path("threads-insights-snapshots.json").write_text(
        json.dumps({"observed_at": now.isoformat(), "records": output},
                   ensure_ascii=False, indent=2) + "\n")
    print(f"Read-only snapshots: due={len(output)} success={sum('window_hours' in x for x in output)}")


if __name__ == "__main__":
    main()
