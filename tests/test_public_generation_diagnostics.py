"""Offline tests: mismatched public releases must be diagnosed and rejected."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch
from tools import verify_release as release

class PublicGenerationDiagnosticsTests(unittest.TestCase):
    def test_generation_mismatch_is_reported_and_rejected(self):
        local = {'sourceRevision': 'a' * 40, 'generation': 'expected', 'files': {}}
        remote = {'sourceRevision': 'a' * 40, 'generation': 'stale', 'files': {}}
        output = io.StringIO()
        with patch.object(release, 'read_public_manifest', return_value=remote) as fetch, patch.object(release.time, 'sleep') as sleep, contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(ValueError, 'public_generation_mismatch'):
                release.wait_for_public_manifest(local, local['sourceRevision'], local['generation'])
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(30)
        lines = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(lines[-1]['reason'], 'public_generation_mismatch')
        self.assertEqual(lines[-1]['expectedGeneration'], 'expected')
        self.assertEqual(lines[-1]['observedGeneration'], 'stale')

    def test_revision_mismatch_is_reported_and_rejected(self):
        local = {'sourceRevision': 'a' * 40, 'generation': 'expected', 'files': {}}
        remote = {'sourceRevision': 'b' * 40, 'generation': 'expected', 'files': {}}
        with patch.object(release, 'read_public_manifest', return_value=remote), patch.object(release.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(ValueError, 'public_revision_mismatch'):
                release.wait_for_public_manifest(local, local['sourceRevision'], local['generation'])
        self.assertEqual(json.loads(output.getvalue().splitlines()[-1])['reason'], 'public_revision_mismatch')

if __name__ == '__main__':
    unittest.main()
