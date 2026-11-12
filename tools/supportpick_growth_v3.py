"""V3 editorial priority helpers. No network calls or publishing side effects.

Only verified dates and explicit source fields are scored. Missing evidence
never becomes a fabricated benefit, eligibility decision or deadline.
"""
from datetime import date, datetime

CATEGORIES = ("청년", "취업", "육아", "주거", "의료", "에너지", "생활", "돌봄")


def editorial_priority(row, today):
    """Sort key: known approaching deadline, reader utility, clarity, stable ID.

    This is an advisory ordering for unreserved candidates, not a replacement
    for the publisher's reviewed queue, existing ledger or source verification.
    """
    if isinstance(today, datetime):
        today = today.date()
    if not isinstance(today, date):
        raise ValueError("date_required")
    end = row.get("endDate")
    days = None
    if isinstance(end, str) and end:
        try:
            days = (date.fromisoformat(end[:10]) - today).days
        except ValueError:
            pass
    if days is not None and days < 0:
        raise ValueError("expired_candidate_not_publishable")
    deadline_band = 0 if days is not None and days <= 14 else 1
    category = " ".join(str(row.get(k) or "") for k in ("category", "title", "summary"))
    utility = 0 if any(k in category for k in CATEGORIES) else 1
    clarity = sum(not bool(row.get(k)) for k in ("target", "method", "summary"))
    return (deadline_band, days if deadline_band == 0 else 999999,
            utility, clarity, str(row.get("id") or ""))


def safe_ratio(numerator, denominator):
    """Return None for unavailable/zero denominator; never substitute zero."""
    if type(numerator) not in (int, float) or type(denominator) not in (int, float):
        return None
    if numerator < 0 or denominator <= 0:
        return None
    return numerator / denominator * 100
