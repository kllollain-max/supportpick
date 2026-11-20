from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class PhaseResult:
    content_id: str
    state: str
    duplicate_detected: bool = False
    data_loss: bool = False
    foreign_overwrite: bool = False


def load_results(path: str | Path) -> list[PhaseResult]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [PhaseResult(**item) for item in raw]


def can_promote(results: list[PhaseResult], phase: int) -> tuple[bool, list[str]]:
    expected = {1: 1, 2: 3, 3: 5}
    required = expected.get(phase)
    if required is None:
        return False, ["unknown_phase"]

    problems = []
    if len(results) != required:
        problems.append(f"expected_{required}_results")

    if len({r.content_id for r in results}) != len(results):
        problems.append("duplicate_content_id")

    for r in results:
        if r.state != "VERIFIED":
            problems.append(f"{r.content_id}:not_verified")
        if r.duplicate_detected:
            problems.append(f"{r.content_id}:duplicate_detected")
        if r.data_loss:
            problems.append(f"{r.content_id}:data_loss")
        if r.foreign_overwrite:
            problems.append(f"{r.content_id}:foreign_overwrite")

    return not problems, problems


def next_phase(current_phase: int, results: list[PhaseResult]) -> int | None:
    ok, _ = can_promote(results, current_phase)
    if not ok:
        return None
    return {1: 2, 2: 3, 3: 4}.get(current_phase)
