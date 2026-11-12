"""SupportPick Threads v3 read-only performance snapshots.

No API calls, posting, or ledger mutations. Import verified numeric observations
from a separate authorized collector; unknown fields remain null.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from statistics import median

METRICS = ("views", "likes", "comments", "reposts", "shares", "saves",
           "profile_visits", "new_followers", "site_visits")
WINDOWS = (24, 72, 168)


def snapshot(post_id, published_at, observed_at, values):
    if not isinstance(post_id, str) or not post_id.strip():
        raise ValueError("post_id_required")
    published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    if published.tzinfo is None or observed.tzinfo is None or observed < published:
        raise ValueError("valid_aware_timestamps_required")
    hours = (observed - published).total_seconds() / 3600
    due = [w for w in WINDOWS if hours >= w]
    if not due:
        raise ValueError("snapshot_not_due")
    if not isinstance(values, dict):
        raise ValueError("metrics_object_required")
    result = {}
    for key in METRICS:
        value = values.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid_metric_" + key)
        result[key] = value
    return {"post_id": post_id, "published_at": published.isoformat(),
            "observed_at": observed.isoformat(), "window_hours": max(due),
            "metrics": result}


def rate(numerator, denominator):
    if type(numerator) is not int or type(denominator) is not int or denominator <= 0:
        return None
    return round(100 * numerator / denominator, 4)


def summarize(records):
    views = [r["metrics"]["views"] for r in records
             if type(r["metrics"].get("views")) is int]
    result = {"count": len(records), "view_median": median(views) if views else None}
    for metric in ("likes", "comments", "reposts", "shares", "saves"):
        pairs = [(r["metrics"].get(metric), r["metrics"].get("views")) for r in records]
        valid = [(a, b) for a, b in pairs if type(a) is int and type(b) is int and b > 0]
        result[metric + "_rate"] = rate(sum(a for a, _ in valid), sum(b for _, b in valid)) if valid else None
    followers = [(r["metrics"].get("new_followers"), r["metrics"].get("profile_visits")) for r in records]
    valid = [(a, b) for a, b in followers if type(a) is int and type(b) is int and b > 0]
    result["follower_conversion_rate"] = rate(sum(a for a, _ in valid), sum(b for _, b in valid)) if valid else None
    return result
