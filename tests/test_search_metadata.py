import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build import build
from collect_full import collect
from refresh import install_candidate
from search_metadata import PageHead, public_metadata, read_verifications
from test_collection import Client

BASE = 'https://kllollain-max.github.io/supportpick/'


class SearchMetadataTests(unittest.TestCase):
    def test_public_build_has_unique_page_metadata_and_only_real_sitemap_urls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collect(Client(), root / 'run', 'search-test')
            install_candidate(root / 'run', root / 'state')
            with patch('build.read_verifications', return_value={}):
                result = build(root / 'public', root / 'state', public_base=BASE)
            self.assertEqual(result['benefits'], 103)
            tree = ET.parse(root / 'public/sitemap.xml')
            urls = [x.text for x in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            # Fixture rows omit application methods, so detail indexing is correctly held.
            self.assertEqual(set(urls), {BASE, BASE + 'about.html', BASE + 'privacy.html',
                                         BASE + 'terms.html', BASE + 'contact.html', BASE + 'benefits/'})
            for name, url in [('index.html', BASE), ('about.html', BASE + 'about.html'), ('privacy.html', BASE + 'privacy.html')]:
                text = (root / 'public' / name).read_text()
                self.assertEqual(text.count('rel="canonical"'), 1)
                self.assertIn(f'href="{url}"', text)
                self.assertIn(f'property="og:url" content="{url}"', text)
                self.assertIn('content="index,follow"', text)
                head = PageHead(); head.feed(text.split('</head>')[0])
                self.assertTrue(head.description)
                self.assertIn('property="og:title" content="' + head.title, text)
                self.assertNotIn('site-verification', text)
            text = (root / 'public/index.html').read_text()
            payload = text.split('<script type="application/ld+json">')[1].split('</script>')[0]
            self.assertEqual(json.loads(payload)['url'], BASE)
            manifest = json.loads((root / 'public/site-manifest.json').read_text())
            self.assertIn('sitemap.xml', manifest['files'])
            self.assertFalse((root / 'public/search-verification.json').exists())
            self.assertFalse((root / 'public/robots.txt').exists())
            self.assertTrue((root / 'public/supportpick-badge.png').is_file())

    def test_preview_is_noindex_and_does_not_advertise_a_public_sitemap(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collect(Client(), root / 'run', 'preview-test')
            install_candidate(root / 'run', root / 'state')
            build(root / 'preview', root / 'state')
            text = (root / 'preview/index.html').read_text()
            self.assertIn('content="noindex,nofollow"', text)
            self.assertNotIn('rel="canonical"', text)
            self.assertNotIn('property="og:url"', text)
            self.assertFalse((root / 'preview/sitemap.xml').exists())

    def test_verification_tokens_are_optional_validated_and_homepage_only(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / 'verification.json'
            config.write_text(json.dumps({'google': None, 'naver': None}))
            self.assertEqual(read_verifications(config), {})
            config.write_text(json.dumps({'google': 'TEST_ONLY_Verification_1234567890', 'naver': None}))
            values = read_verifications(config)
            source = '<html><head><title>지원금픽</title><meta name="description" content="안내"></head><body></body></html>'
            self.assertIn('google-site-verification', public_metadata(source, 'index.html', BASE, values))
            self.assertNotIn('google-site-verification', public_metadata(source, 'about.html', BASE, values))
            for bad in ['"><script>alert(1)</script>', '', True, 'token with space']:
                config.write_text(json.dumps({'google': bad}))
                with self.assertRaisesRegex(ValueError, 'invalid_search_verification_token'):
                    read_verifications(config)

    def test_titles_and_descriptions_cannot_escape_generated_metadata_or_jsonld(self):
        source = '<html><head><title>지원금 &amp; 혜택</title><meta name="description" content="&quot;&gt;&lt;script&gt;test&lt;/script&gt;"></head><body></body></html>'
        result = public_metadata(source, 'index.html', BASE, {})
        self.assertIn('property="og:title" content="지원금 &amp; 혜택"', result)
        payload = result.split('<script type="application/ld+json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(payload)['description'], '"><script>test</script>')
        self.assertNotIn('<script>', payload)


if __name__ == '__main__':
    unittest.main()
