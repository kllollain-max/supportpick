import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from supportpick_threads_metrics import snapshot, summarize


class MetricsTests(unittest.TestCase):
    def test_unknown_is_not_zero(self):
        r = snapshot("post1", "2026-11-10T00:00:00+00:00",
                     "2026-11-11T00:00:00+00:00", {"views": 100, "likes": 4})
        self.assertIsNone(r["metrics"]["shares"])
        self.assertEqual(r["window_hours"], 24)
        self.assertEqual(summarize([r])["likes_rate"], 4)
        self.assertIsNone(summarize([r])["shares_rate"])

    def test_no_early_snapshot(self):
        with self.assertRaises(ValueError):
            snapshot("post1", "2026-11-10T00:00:00Z",
                     "2026-11-10T01:00:00Z", {})

    def test_invalid_metrics(self):
        with self.assertRaises(ValueError):
            snapshot("post1", "2026-11-10T00:00:00Z",
                     "2026-11-11T00:00:00Z", {"views": -1})


if __name__ == "__main__":
    unittest.main()
