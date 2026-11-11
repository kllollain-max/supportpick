import json
import tempfile
import unittest
from pathlib import Path

from state_machine import DraftLock, Manifest, validate_pre_save


class DraftUploaderSafetyTests(unittest.TestCase):
    def manifest(self):
        return Manifest(
            content_id="supportpick-20261111-001",
            title="테스트 지원금 신청방법",
            body_text="첫 문단\n핵심 안내\n다른 생활 지원 제도는 지원금픽 링크에서 확인하세요.\nhttps://kllollain-max.github.io/supportpick/",
            images=[{"path":"a.png","slot":"hero"}],
            cta_text="다른 생활 지원 제도는 지원금픽 링크에서 확인하세요.",
            cta_url="https://kllollain-max.github.io/supportpick/",
        )

    def test_pre_save_rejects_missing_cta(self):
        m = self.manifest()
        problems = validate_pre_save(m.title, "첫 문단", m, 1)
        self.assertIn("cta_text_missing", problems)
        self.assertIn("cta_url_missing", problems)

    def test_lock_blocks_parallel_runner(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "naver_draft_lock.json"
            m = self.manifest()
            first = DraftLock(p)
            first.acquire(job_id="j1", manifest=m, runner_id="r1", state="PRECHECK")
            with self.assertRaisesRegex(RuntimeError, "LOCKED"):
                DraftLock(p).acquire(job_id="j2", manifest=m, runner_id="r2", state="PRECHECK")
            first.release()

    def test_stale_save_clicked_lock_is_not_discarded(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "naver_draft_lock.json"
            p.write_text(json.dumps({
                "heartbeat": 1,
                "state": "SAVE_CLICKED",
                "content_id": "supportpick-20261111-001"
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SAVE_STATUS_UNKNOWN"):
                DraftLock(p, stale_after_s=1).acquire(
                    job_id="j2", manifest=self.manifest(), runner_id="r2", state="PRECHECK"
                )


if __name__ == "__main__":
    unittest.main()
