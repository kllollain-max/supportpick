import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build import build
from collect_full import collect
from refresh import install_candidate
from test_collection import Client

class AppFeatureBuildTests(unittest.TestCase):
    def test_manifest_and_real_icons_are_isolated_from_careerpick(self):
        manifest = json.loads((ROOT / 'manifest.webmanifest').read_text())
        self.assertEqual(manifest['scope'], '/supportpick/')
        self.assertEqual(manifest['id'], '/supportpick/')
        self.assertEqual(manifest['start_url'], '/supportpick/?src=app')
        self.assertEqual(manifest['display'], 'standalone')
        for icon in manifest['icons']:
            raw = (ROOT / icon['src']).read_bytes()
            self.assertEqual(raw[:8], b'\x89PNG\r\n\x1a\n')
            width, height = struct.unpack('>II', raw[16:24])
            self.assertEqual(icon['sizes'], f'{width}x{height}')
        self.assertEqual({icon['sizes'] for icon in manifest['icons']}, {'192x192', '512x512'})

    def test_public_details_have_share_install_and_worker_keeps_facts_out_of_offline_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collect(Client(), root / 'run', 'app-features-test')
            install_candidate(root / 'run', root / 'state')
            result = build(root / 'public', root / 'state', public_base='https://kllollain-max.github.io/supportpick/')
            files = json.loads((root / 'public/site-manifest.json').read_text())['files']
            for path in ['manifest.webmanifest','app-features.js','sw.js','offline.html','app-icon-180.png','app-icon-192.png','app-icon-512.png']:
                self.assertIn(path, files)
            home = (root / 'public/index.html').read_text()
            self.assertIn('data-share-site', home)
            self.assertIn('data-install-app', home)
            self.assertIn('rel="manifest"', home)
            details = list((root / 'public/benefits').glob('*/index.html'))
            self.assertEqual(len(details), result['detailPages'])
            for path in details:
                text = path.read_text()
                self.assertIn('data-share-benefit', text)
                self.assertIn('data-save', text)
                self.assertIn('data-track', text)
                self.assertIn('../../manifest.webmanifest', text)
                self.assertIn('../../app-features.js?v=', text)
            offline = (root / 'public/offline.html').read_text()
            self.assertIn('content="noindex,follow"', offline)
            self.assertNotIn('offline.html', (root / 'public/sitemap.xml').read_text())
            worker = (root / 'public/sw.js').read_text()
            self.assertNotIn('__SHELL_HASH__', worker)
            self.assertIn("key.startsWith('supportpick-shell-')", worker)
            self.assertNotIn('data.json', worker)
            self.assertNotIn('localStorage', worker)
            self.assertNotIn('indexedDB', worker)
            self.assertIn("event.request.mode !== 'navigate'", worker)
            self.assertIn('status: 503', worker)

if __name__ == '__main__':
    unittest.main()
