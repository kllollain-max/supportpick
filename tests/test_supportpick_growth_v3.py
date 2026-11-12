import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from supportpick_growth_v3 import editorial_priority, safe_ratio


class GrowthV3Tests(unittest.TestCase):
    def test_deadline_priority(self):
        today = date(2026, 11, 12)
        near = {"id": "a", "endDate": "2026-11-15", "title": "청년 지원"}
        later = {"id": "b", "endDate": "2026-12-31", "title": "청년 지원"}
        self.assertLess(editorial_priority(near, today), editorial_priority(later, today))

    def test_expired_is_rejected(self):
        with self.assertRaises(ValueError):
            editorial_priority({"id": "x", "endDate": "2026-11-01"}, date(2026, 11, 12))

    def test_unknown_metrics_not_zero(self):
        self.assertIsNone(safe_ratio(None, 100))
        self.assertIsNone(safe_ratio(1, 0))
        self.assertEqual(safe_ratio(2, 100), 2)


if __name__ == "__main__":
    unittest.main()
