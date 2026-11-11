import json
import tempfile
import unittest
from pathlib import Path

from runner import DryRunAdapter, run


class RunnerTests(unittest.TestCase):
    def write_manifest(self, d):
        p = Path(d) / "manifest.json"
        p.write_text(json.dumps({
            "content_id": "supportpick-20261111-001",
            "title": "지원금픽 테스트",
            "body_text": "첫 문단\n핵심 문장\n다른 생활 지원 제도는 지원금픽 링크에서 확인하세요.\nhttps://kllollain-max.github.io/supportpick/",
            "images": [],
            "cta_text": "다른 생활 지원 제도는 지원금픽 링크에서 확인하세요.",
            "cta_url": "https://kllollain-max.github.io/supportpick/"
        }, ensure_ascii=False), encoding="utf-8")
        return p

    def test_dry_run_reaches_verified(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = self.write_manifest(d)
            code, state = run(manifest, Path(d) / "runtime", DryRunAdapter({}))
            self.assertEqual(0, code)
            self.assertEqual("VERIFIED", state)

    def test_save_unknown_never_restarts_as_new_content(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = self.write_manifest(d)
            code, state = run(manifest, Path(d) / "runtime", DryRunAdapter({"save_unknown": True}))
            self.assertEqual(2, code)
            self.assertEqual("SAVE_STATUS_UNKNOWN", state)
            state_file = Path(d) / "runtime" / "state" / "supportpick-20261111-001.json"
            payload = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual("SAVE_STATUS_UNKNOWN", payload["state"])

    def test_foreign_editor_content_stops_before_input(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = self.write_manifest(d)
            code, state = run(manifest, Path(d) / "runtime", DryRunAdapter({"existing_foreign_draft": True}))
            self.assertEqual(2, code)
            self.assertEqual("FOREIGN_DRAFT_DETECTED", state)


if __name__ == "__main__":
    unittest.main()
