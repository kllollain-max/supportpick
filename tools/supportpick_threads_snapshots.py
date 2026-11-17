"""Select published verified Threads posts due for read-only 24h/72h/7d snapshots."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from supportpick_threads_insights import collect
from supportpick_threads_metrics import snapshot

WINDOWS = (24, 72, 168)


def due_records(state, now, observations=None):
    observations = observations if observations is not None else {}
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
        # A delayed scheduled run must not silently lose its latest milestone.
        # Never relabel today's cumulative count as an earlier missed window.
        due = [w for w in WINDOWS if w <= hours]
        if (due and hours <= 28 * 24
                and post_id + ':' + str(max(due)) + 'h' not in observations):
            result.append((post_id, published))
    return result


def main():
    now = datetime.now(timezone.utc)
    state = json.loads(Path(os.environ.get("SUPPORTPICK_THREADS_STATE_FILE", "threads-state.json")).read_text())
    # Read the same fetched state-branch generation. Missing/malformed audit
    # input fails before any API read; first observations are never overwritten.
    maintenance = json.loads(Path(os.environ.get(
        "SUPPORTPICK_THREADS_MAINTENANCE_FILE", "threads-maintenance.json")).read_text())
    observations = maintenance['reach_policy']['measurement']['observations_by_id_window']
    if not isinstance(observations, dict):
        raise ValueError('snapshot_observation_ledger_required')
    token = os.environ.get("SUPPORTPICK_THREADS_ACCESS_TOKEN", "")
    output = []
    for post_id, published in due_records(state, now, observations):
        try:
            metrics = collect(post_id, token)
            output.append(snapshot(post_id, published, now.isoformat(), metrics))
        except (RuntimeError, ValueError):
            hours = (now - datetime.fromisoformat(published.replace('Z', '+00:00'))).total_seconds() / 3600
            output.append({"post_id": post_id, "status": "unavailable",
                           "published_at": published, "window_hours": max(w for w in WINDOWS if w <= hours),
                           "elapsed_hours": hours, "observed_at": now.isoformat(), "metrics": None})
    Path("threads-insights-snapshots.json").write_text(
        json.dumps({"observed_at": now.isoformat(), "records": output},
                   ensure_ascii=False, indent=2) + "\n")
    print(f"Read-only snapshots: due={len(output)} success={sum(isinstance(x.get('metrics'), dict) for x in output)}")


if __name__ == "__main__":
    main()

