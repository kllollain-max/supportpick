"""Offline ZIP integrity and safety tests for SupportPick runtime backups."""
import hashlib
import json
import tempfile
import unittest
import zipfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_supportpick_backup import verify_zip

def encode(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False).encode()

def make_archive(path, *, corrupt=False, missing=False, duplicate=False):
    entries = {}
    for serial in (100, 101):
        generation = f'gov24-{serial}-1'
        prefix = f'snapshots/{generation}'
        feed = encode({'generation': generation, 'items': [{'id': 'x'}]})
        data_path = f'{prefix}/data.json'
        entries[data_path] = feed
        manifest = {'version': 1, 'generation': generation,
                    'files': {'data.json': hashlib.sha256(feed).hexdigest()}}
        entries[f'{prefix}/manifest.json'] = encode(manifest)
    current = 'gov24-101-1'
    entries['current.json'] = encode({'generation': current, 'version': 1,
        'count': 1, 'path': 'snapshots/' + current,
        'manifestSha256': hashlib.sha256(entries[f'snapshots/{current}/manifest.json']).hexdigest()})
    if corrupt:
        entries[f'snapshots/{current}/data.json'] = b'corrupted'
    if missing:
        del entries[f'snapshots/{current}/data.json']
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries.items():
            archive.writestr(name, value)
        if duplicate:
            archive.writestr('current.json', entries['current.json'])

class BackupZipTests(unittest.TestCase):
    def check(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'backup.zip'
            make_archive(path, **kwargs)
            return verify_zip(path)
    def test_valid_two_generations(self):
        result = self.check()
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['verified_files'], 2)
        self.assertEqual(result['items'], 1)
    def test_corruption_rejected(self):
        with self.assertRaisesRegex(ValueError, 'snapshot_digest_mismatch'):
            self.check(corrupt=True)
    def test_missing_manifest_file_rejected(self):
        with self.assertRaisesRegex(ValueError, 'manifest_file_set_mismatch'):
            self.check(missing=True)
    def test_duplicate_entries_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsafe_archive_entry'):
            self.check(duplicate=True)

if __name__ == '__main__':
    unittest.main()
