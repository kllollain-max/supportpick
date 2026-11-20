from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class UploaderConfig:
    enabled: bool = False
    allow_publish: bool = False
    target_blog: str = "bible_el"
    max_parallel: int = 1
    require_reopen_verification: bool = True
    require_correct_account: bool = True

    @classmethod
    def load(cls, path: str | Path) -> "UploaderConfig":
        p = Path(path)
        if not p.exists():
            return cls()
        raw = json.loads(p.read_text(encoding="utf-8"))
        return cls(**raw)

    def validate(self) -> list[str]:
        problems = []
        if self.allow_publish:
            problems.append("auto_publish_must_remain_disabled")
        if self.target_blog != "bible_el":
            problems.append("wrong_target_blog")
        if self.max_parallel != 1:
            problems.append("parallelism_must_be_one")
        if not self.require_reopen_verification:
            problems.append("reopen_verification_required")
        if not self.require_correct_account:
            problems.append("account_verification_required")
        return problems
