from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass
class DraftCandidate:
    draft_id: str
    title: str
    saved_at: float
    first_text: str
    key_text: str
    cta_text: str
    image_count: int


def score_candidate(expected_title: str, first_text: str, key_text: str, cta_text: str,
                    expected_images: int, expected_saved_at: float, candidate: DraftCandidate) -> float:
    title_score = SequenceMatcher(None, expected_title.strip(), candidate.title.strip()).ratio()
    first_score = SequenceMatcher(None, first_text.strip(), candidate.first_text.strip()).ratio()
    key_score = SequenceMatcher(None, key_text.strip(), candidate.key_text.strip()).ratio()
    cta_score = 1.0 if cta_text.strip() and cta_text.strip() in candidate.cta_text else 0.0
    image_score = 1.0 if candidate.image_count == expected_images else max(0.0, 1 - abs(candidate.image_count - expected_images) * .25)
    age_seconds = abs(candidate.saved_at - expected_saved_at)
    time_score = max(0.0, 1.0 - age_seconds / 7200.0)
    return (
        title_score * .35 +
        first_score * .20 +
        key_score * .15 +
        cta_score * .10 +
        image_score * .10 +
        time_score * .10
    )


def find_recoverable_draft(candidates: Iterable[DraftCandidate], **expected):
    ranked = sorted(
        ((score_candidate(candidate=c, **expected), c) for c in candidates),
        key=lambda x: x[0],
        reverse=True,
    )
    if not ranked:
        return None, "DRAFT_NOT_FOUND"
    best_score, best = ranked[0]
    if best_score >= 0.88:
        return best, "DRAFT_RECOVERED"
    if best_score >= 0.72:
        return best, "MANUAL_REVIEW_REQUIRED"
    return None, "DRAFT_NOT_FOUND"
