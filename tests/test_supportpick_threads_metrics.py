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

    def test_late_count_has_actual_elapsed_and_is_not_exact_24h(self):
        r = snapshot('post1', '2026-11-15T03:39:17.940068Z',
                     '2026-11-16T05:47:50Z', {'views': 0})
        self.assertEqual(r['window_hours'], 24)
        self.assertGreater(r['elapsed_hours'], 26)
        self.assertEqual(r['timing'], 'late_available_check')
        self.assertFalse(r['within_target_tolerance'])
        self.assertTrue(r['not_backcalculated'])
        self.assertEqual(r['metrics']['views'], 0)
        self.assertIsNone(r['metrics']['likes'])

    def test_170_hour_count_is_only_seven_day_never_24h_or_72h(self):
        r = snapshot('post1', '2026-11-10T00:00:00Z',
                     '2026-11-17T02:00:00Z', {'views': 200})
        self.assertEqual(r['window_hours'], 168)
        self.assertEqual(r['elapsed_hours'], 170)
        self.assertEqual(r['metrics']['views'], 200)


if __name__ == "__main__":
    unittest.main()

