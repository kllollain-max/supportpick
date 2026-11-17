import sys
import unittest
import json
import os
import tempfile
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from supportpick_threads_snapshots import due_records, main


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

    def test_real_missing_post_survives_run_delayed_past_two_hours(self):
        # Nov16 runs at03:33Z and05:47Z straddled the old03:39Z~05:39Z window.
        published = '2026-11-15T12:39:17.940068+09:00'
        row = {'status': 'published', 'verified': True,
               'main_id': '18122947907049313', 'published_at': published}
        now = datetime.fromisoformat('2026-11-16T05:47:50+00:00')
        self.assertEqual(due_records({'records': [row]}, now, {}),
                         [('18122947907049313', published)])
        for status in ('measured_official_api', 'unmeasured_official_read_path_unavailable'):
            obs = {'18122947907049313:24h': {'status': status}}
            self.assertEqual(due_records({'records': [row]}, now, obs), [])

    def test_latest_window_only_no_prior_window_backfill(self):
        now = datetime(2026, 11, 17, 8, tzinfo=timezone.utc)
        published = (now - timedelta(hours=170)).isoformat()
        row = {'status': 'published', 'verified': True,
               'main_id': '18122947907049313', 'published_at': published}
        self.assertEqual(len(due_records({'records': [row]}, now, {'18122947907049313:24h': {}})), 1)
        self.assertEqual(due_records({'records': [row]}, now, {'18122947907049313:168h': {}}), [])
        row['published_at'] = (now - timedelta(days=29)).isoformat()
        self.assertEqual(due_records({'records': [row]}, now, {}), [])

    def test_main_reads_durable_keys_without_mutating_state_or_audit(self):
        now = datetime(2026, 11, 17, 8, tzinfo=timezone.utc)
        published = (now - timedelta(hours=53)).isoformat()
        row = {'status': 'published', 'verified': True,
               'main_id': '18122947907049313', 'published_at': published}
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / 'state.json'; audit = Path(d) / 'audit.json'
            state.write_text(json.dumps({'records': [row]}))
            audit.write_text(json.dumps({'reach_policy': {'measurement': {'observations_by_id_window': {}}}}))
            prior = (state.read_bytes(), audit.read_bytes())
            env = {'SUPPORTPICK_THREADS_STATE_FILE': str(state),
                   'SUPPORTPICK_THREADS_MAINTENANCE_FILE': str(audit),
                   'SUPPORTPICK_THREADS_ACCESS_TOKEN': 'unit-test-only'}
            cwd = os.getcwd()
            try:
                os.chdir(d)
                with patch.dict(os.environ, env), patch('supportpick_threads_snapshots.datetime', wraps=datetime) as clock, patch('supportpick_threads_snapshots.collect', return_value={'views': 14}) as read:
                    clock.now.return_value = now
                    main()
                    read.assert_called_once_with(row['main_id'], 'unit-test-only')
                out = json.loads(Path('threads-insights-snapshots.json').read_text())
                self.assertEqual(out['records'][0]['elapsed_hours'], 53)
                self.assertFalse(out['records'][0]['within_target_tolerance'])
                self.assertEqual((state.read_bytes(), audit.read_bytes()), prior)
                audit.unlink()
                with patch.dict(os.environ, env), patch('supportpick_threads_snapshots.collect') as read:
                    with self.assertRaises(FileNotFoundError):
                        main()
                    read.assert_not_called()
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()

