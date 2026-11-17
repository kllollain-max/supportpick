import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from restore_pages_artifact import restore, verify_origin

SHA = 'a' * 40


class PublishedArtifactTests(unittest.TestCase):
    def archive(self, folder, extra=None, bad_hash=False, source=SHA):
        archive = folder / 'artifact.tar'
        body = b'<h1>published</h1>'
        manifest = {'sourceRevision': source, 'generation': 'one', 'files': {
            'index.html': 'b' * 64 if bad_hash else hashlib.sha256(body).hexdigest()}}
        with tarfile.open(archive, 'w') as bundle:
            for name, data in [('index.html', body), ('site-manifest.json', json.dumps(manifest).encode())]:
                entry = tarfile.TarInfo('./' + name); entry.size = len(data)
                bundle.addfile(entry, io.BytesIO(data))
            if extra:
                bundle.addfile(extra, io.BytesIO(b'x') if extra.isfile() else None)
        return archive

    def test_exact_published_bytes_are_restored_without_a_rebuild(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); archive = self.archive(folder)
            self.assertEqual(restore(archive, folder / 'dist', SHA)['verifiedFiles'], 2)
            self.assertEqual((folder / 'dist/index.html').read_bytes(), b'<h1>published</h1>')

    def test_changed_bytes_wrong_source_and_nonempty_output_are_rejected(self):
        for bad_hash, source in [(True, SHA), (False, 'c' * 40)]:
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                with self.assertRaises(ValueError):
                    restore(self.archive(folder, bad_hash=bad_hash, source=source), folder / 'dist', SHA)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); (folder / 'keep').write_text('original')
            with self.assertRaisesRegex(ValueError, 'output_not_empty'):
                restore(self.archive(folder), folder, SHA)
            self.assertEqual((folder / 'keep').read_text(), 'original')

    def test_paths_links_and_duplicate_files_cannot_escape_or_replace_data(self):
        for name, kind in [('../escape', tarfile.REGTYPE), ('/escape', tarfile.REGTYPE),
                           ('linked', tarfile.SYMTYPE), ('hard', tarfile.LNKTYPE), ('index.html', tarfile.REGTYPE)]:
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp); entry = tarfile.TarInfo(name); entry.type = kind
                if kind == tarfile.REGTYPE: entry.size = 1
                else: entry.linkname = '../escape'
                with self.assertRaises(ValueError):
                    restore(self.archive(folder, extra=entry), folder / 'dist', SHA)
                self.assertFalse((folder / 'escape').exists())

    def test_failed_post_publish_check_does_not_mean_unpublished_or_authorize_other_runs(self):
        run = {'head_sha': SHA, 'path': '.github/workflows/deploy-approved.yml', 'conclusion': 'failure'}
        jobs = {'jobs': [{'steps': [{'name': 'Run actions/deploy-pages@v4', 'conclusion': 'success'}]}]}
        verify_origin(run, jobs, SHA)
        for changed_run, changed_jobs in [({**run, 'head_sha': 'c' * 40}, jobs),
                                          ({**run, 'path': 'other.yml'}, jobs), (run, {'jobs': []})]:
            with self.assertRaises(ValueError): verify_origin(changed_run, changed_jobs, SHA)
