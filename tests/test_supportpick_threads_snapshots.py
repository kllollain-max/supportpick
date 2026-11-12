import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from supportpick_threads_snapshots import due_records


class ScheduledSnapshotsTests(unittest.TestCase):
    def test_only_verified_published_due(self):
        now = datetime(2026, 11, 13, 6, tzinfo=timezone.utc)
        due = (now - timedelta(hours=24, minutes=20)).isoformat()
        state = {"records": [
            {"status": "published", "verified": True, "main_id": "18061100522563998", "published_at": due},
            {"status": "pending", "verified": True, "main_id": "18061100522563999", "published_at": due},
            {"status": "published", "verified": False, "main_id": "18061100522563997", "published_at": due},
            {"status": "published", "verified": True, "main_id": "18061100522563996",
             "published_at": (now - timedelta(hours=20)).isoformat()}]}
        self.assertEqual(due_records(state, now), [("18061100522563998", due)])


if __name__ == "__main__":
    unittest.main()
