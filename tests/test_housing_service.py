import copy
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from test_detail_pages import row, BASE, NOW
from detail_pages import material_hash, reviewed_guide, safe_reference, write_details, benefit_path
from application_guides import write_guides
from benefit_analysis import related_analysis


class HousingServicePreparationTests(unittest.TestCase):
    def test_service_reference_remains_bound_to_exact_host_source_hash_and_validity(self):
        a = row('WII000000310')
        g = {'benefitId': a['id'], 'sourceHash': material_hash(a), 'status': 'reviewed',
             'reviewedAt': (NOW - timedelta(days=1)).isoformat(),
             'validUntil': (NOW + timedelta(days=14)).isoformat(), 'summary': '상담과 연계',
             'checks': ['진단', '상담', '연계'], 'steps': ['문의', '상담', '점검'],
             'sourceReviews': [{'url': 'https://csa.nps.or.kr/ohkb/gdnc/UHKB0301M0.do',
                                'note': '공식 서비스 이용 안내'}]}
        self.assertIs(reviewed_guide(a, {'guides': [g]}, NOW), g)
        self.assertIsNone(reviewed_guide({**a, 'support': 'changed'}, {'guides': [g]}, NOW))
        self.assertIsNone(reviewed_guide(a, {'guides': [g]}, NOW + timedelta(days=14)))
        for url in ['https://csa.nps.or.kr.evil.example/', 'https://other.nps.or.kr/',
                    'http://csa.nps.or.kr/', 'https://csa.nps.or.kr:8443/',
                    'https://user:pass@csa.nps.or.kr/']:
            self.assertFalse(safe_reference(url), url)

    def test_optional_local_detail_links_preserve_records_and_are_not_manufactured(self):
        rows = {sid: row(sid) for sid in ['999000000024', 'SD0000016138']}
        for a in rows.values():
            a['period'] = '접수기관 별 상이'
            a['title'] = '서로 다른 서비스 ' + a['id']
            a['support'] = '서비스별 지원 내용 ' + a['id']
        original = copy.deepcopy(rows)
        slugs = {'999000000024': 'long-term-lease-notice-checklist-2026',
                 'SD0000016138': 'local-social-service-application-vs-use-2026'}
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_guides(output, BASE, {})
            for sid, slug in slugs.items():
                self.assertNotIn('../benefits/' + sid + '/', (output / 'guides' / (slug + '.html')).read_text())
            result = write_details(output, rows, {}, BASE, {}, {}, 'success', NOW)
            write_guides(output, BASE, rows)
            self.assertEqual(result['report']['heldDetails'], 0)
            for sid, slug in slugs.items():
                detail = (output / benefit_path(sid) / 'index.html').read_text()
                self.assertIn('접수기관 별 상이', detail)
                self.assertIn('content="index,follow"', detail)
                self.assertIn('../../guides/' + slug + '.html', detail)
                self.assertIn('../benefits/' + sid + '/', (output / 'guides' / (slug + '.html')).read_text())
        self.assertEqual(rows, original)
        self.assertIn('winter-bills-vs-home-improvement-2026.html', related_analysis('424000000006'))
        self.assertEqual(related_analysis('OTHER'), '')


if __name__ == '__main__':
    unittest.main()
