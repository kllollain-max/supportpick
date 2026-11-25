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
from refresh import install_candidate, read_current
from search_metadata import PageHead, public_metadata, read_verifications, version_local_assets
from test_collection import Client, rows

BASE = 'https://kllollain-max.github.io/supportpick/'


class SearchMetadataTests(unittest.TestCase):
    def test_confirmed_demo_is_hidden_but_its_url_and_source_are_preserved(self):
        demo_id = '174100000034'
        data = rows(2)
        data[0].update({'서비스ID': demo_id, '서비스명': '온라인 신청 시연 테스트(운영)',
                        '지원내용': '운영 시연용 데이터'})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collect(Client(data=data), root / 'run', 'demo-test')
            install_candidate(root / 'run', root / 'state')
            _, original = read_current(root / 'state')
            out = root / 'public'
            result = build(out, root / 'state', public_base=BASE)

            self.assertEqual(result['benefits'], 1)
            self.assertIn(demo_id, (original / 'data.json').read_text())
            public_feed = json.loads((out / 'data.json').read_text())
            self.assertEqual([record['id'] for record in public_feed['items']], ['B00001'])
            bootstrap_script = (out / 'data-bootstrap.js').read_text()
            self.assertNotIn(demo_id, bootstrap_script)
            bootstrap = json.loads(bootstrap_script.removeprefix('window.SUPPORTPICK_DATA = ').strip().removesuffix(';'))
            catalog = json.loads((out / bootstrap['catalogUrl']).read_text())
            self.assertEqual(bootstrap['sourceCount'], len(catalog['items']))
            self.assertEqual(catalog, public_feed)
            self.assertNotIn(demo_id, (out / 'sitemap.xml').read_text())
            for shard in (out / 'details').rglob('*.json'):
                self.assertNotIn(demo_id, json.loads(shard.read_text())['items'])
            detail = (out / 'benefits' / demo_id / 'index.html').read_text()
            self.assertIn('content="noindex,follow"', detail)
            self.assertIn('온라인 신청 시연용 테스트로 확인했습니다', detail)
            self.assertNotIn('운영 시연용 데이터', detail)

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
                                         BASE + 'terms.html', BASE + 'contact.html', BASE + 'benefits/',
                                         *[BASE+'guides/'+slug+'.html' for slug in ['youth-hiring-participation-vs-payment-2026','training-card-vs-employment-support-2026','veterans-vehicle-inspection-discount-2026','influenza-season-vs-dose-history-2026','busan-child-care-fee-vs-copayment-2026','jeungpyeong-insurance-contract-vs-claim-2026','sunchang-birth-total-vs-installments-2026','school-welfare-vs-education-benefit-2026','didimdol-cap-collateral-and-closing-2026','youth-housing-account-announcement-tax-conversion-2026','youth-mutual-aid-closed-enrollment-maturity-2026','rental-guarantee-fee-cap-and-dates-2026','incheon-pregnancy-transport-vs-postpartum-2026','incheon-child-dream-birth-year-2026','maternal-service-application-use-refund-2026','find-and-verify','compare-benefits','application-checklist','deadlines-and-updates','energy-voucher-2026','emergency-vs-livelihood-2026','child-allowance-2026','housing-benefit-2026','earned-income-credit-late-2026','women-farmer-voucher-records-2026','youth-savings-contribution-2026','first-meeting-vs-parent-benefit-2026','culture-card-deadlines-2026','basic-pension-amounts-2026','forest-voucher-application-vs-use-2026','gyeonggi-child-transport-cap-2026','winter-bills-vs-home-improvement-2026','scholarships-vs-student-loan-steps-2026','small-business-loan-vs-guarantee-2026','leave-benefit-claim-checklist-2026', 'unemployment-benefit-vs-pension-credit-2026', 'long-term-lease-notice-checklist-2026','local-social-service-application-vs-use-2026']]})
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
            youth_hiring_path = 'guides/youth-hiring-participation-vs-payment-2026.html'
            self.assertEqual(text.count(f'href="{youth_hiring_path}"'), 1)
            self.assertIn(BASE + youth_hiring_path, urls)
            veterans_path = 'guides/veterans-vehicle-inspection-discount-2026.html'
            self.assertIn(f'href="{veterans_path}"', text)
            veterans = (root / 'public' / veterans_path).read_text()
            self.assertIn('수검 후 60일 이내이며 환불 요청 시점에 전산조회가 가능할 것', veterans)
            self.assertIn('공식 자료 대조: 2026-11-21', veterans)
            payload = text.split('<script type="application/ld+json">')[1].split('</script>')[0]
            self.assertEqual(json.loads(payload)['url'], BASE)
            manifest = json.loads((root / 'public/site-manifest.json').read_text())
            self.assertIn('sitemap.xml', manifest['files'])
            self.assertFalse((root / 'public/search-verification.json').exists())
            self.assertFalse((root / 'public/robots.txt').exists())
            self.assertTrue((root / 'public/supportpick-badge.png').is_file())
            # Every generated depth must resolve the same consent-controlled assets.
            for page in (root / 'public').rglob('*.html'):
                html=page.read_text()
                if page.name in ('404.html','offline.html'):
                    self.assertNotIn('naver-analytics.js',html)
                    continue
                self.assertEqual(html.count('naver-analytics.js?v='),1,str(page))
                self.assertEqual(html.count('naver-analytics.css?v='),1,str(page))
                self.assertNotIn('wcslog.js',html)
            self.assertIn('naver-analytics.js',manifest['files'])
            self.assertIn('naver-analytics.css',manifest['files'])
            detail=next((root / 'public/benefits').glob('*/index.html')).read_text()
            self.assertIn('src="../../naver-analytics.js?v=',detail)

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
            self.assertNotIn('naver-analytics.js',text)

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

    def test_deployed_assets_change_url_when_bytes_change_and_navigation_is_untouched(self):
        html='<link href="../../styles.css" rel="stylesheet"><script src="../../app.js"></script><a href="../OTHER/">다른 혜택</a><a href="https://official.go.kr/file.js">공식</a><link rel="canonical" href="https://kllollain-max.github.io/supportpick/benefits/ID/">'
        first=version_local_assets(html,'benefits/ID/index.html',{'styles.css':'a'*64,'app.js':'b'*64})
        second=version_local_assets(html,'benefits/ID/index.html',{'styles.css':'c'*64,'app.js':'b'*64})
        self.assertIn('../../styles.css?v='+'a'*16,first)
        self.assertIn('../../styles.css?v='+'c'*16,second)
        self.assertIn('../../app.js?v='+'b'*16,second)
        self.assertIn('href="../OTHER/"',second)
        self.assertIn('https://official.go.kr/file.js"',second)
        self.assertIn('href="https://kllollain-max.github.io/supportpick/benefits/ID/"',second)
        self.assertEqual(version_local_assets(first,'benefits/ID/index.html',{'styles.css':'a'*64,'app.js':'b'*64}),first)

    def test_asset_queries_and_fragments_are_preserved_and_versions_are_not_duplicated(self):
        result=version_local_assets('<script src="../../app.js?mode=a&amp;v=old#part"></script>',
                                    'benefits/ID/index.html',{'app.js':'f'*64})
        self.assertIn('?mode=a&amp;v='+'f'*16+'#part',result)
        self.assertEqual(result.count('v='),1)


if __name__ == '__main__':
    unittest.main()
