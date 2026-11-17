import copy
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from test_detail_pages import row, BASE, NOW
from detail_pages import material_hash, reviewed_guide, safe_reference, write_details, benefit_path
from benefit_analysis import related_analysis
from application_guides import write_guides
from winter_energy_analysis import EFFICIENCY


class WinterPreparationRegressionTests(unittest.TestCase):
    def test_new_primary_reference_retains_hash_expiry_and_url_security_guards(self):
        a = row('424000000006')
        g = {'benefitId': a['id'], 'sourceHash': material_hash(a), 'status': 'reviewed',
             'reviewedAt': (NOW - timedelta(days=1)).isoformat(),
             'validUntil': (NOW + timedelta(days=14)).isoformat(),
             'summary': '주택 공사 확인', 'checks': ['가구', '주택', '기간'],
             'steps': ['문의', '조사', '시공'],
             'sourceReviews': [{'url': EFFICIENCY, 'note': '2026년 난방 안내 확인'}]}
        self.assertIs(reviewed_guide(a, {'guides': [g]}, NOW), g)
        self.assertIsNone(reviewed_guide({**a, 'period': '새 모집기간'}, {'guides': [g]}, NOW))
        self.assertIsNone(reviewed_guide(a, {'guides': [g]}, NOW + timedelta(days=14)))
        for url in ['https://www.e-policy.or.kr.evil.example/', 'https://other.e-policy.or.kr/',
                    'http://www.e-policy.or.kr/', 'https://www.e-policy.or.kr:8443/',
                    'https://user:pass@www.e-policy.or.kr/']:
            self.assertFalse(safe_reference(url), url)

    def test_comparison_preserves_raw_period_and_existing_benefit_article_links(self):
        a = row('424000000006')
        a.update(period='접수기관 별 상이', support='단열·창호·보일러 등 현물 지원')
        original = copy.deepcopy(a)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = write_details(out, {a['id']: a}, {}, BASE, {}, {}, 'success', NOW)
            write_guides(out, BASE, {a['id']: a})
            detail = (out / benefit_path(a['id']) / 'index.html').read_text()
            guide = (out / 'guides/winter-bills-vs-home-improvement-2026.html').read_text()
            self.assertIn('접수기관 별 상이', detail)
            self.assertIn('winter-bills-vs-home-improvement-2026.html', detail)
            self.assertEqual(result['report']['heldDetails'], 0)
            self.assertIn('content="index,follow"', detail)
            self.assertIn('9월 11일 18시', guide)
            self.assertIn('다른 지역의 마감으로 일반화', guide)
            self.assertIn('../benefits/424000000006/', guide)
            self.assertIn('동절기 연료비', guide)
            self.assertIn('생계지원', guide)
        self.assertEqual(a, original)
        self.assertIn('energy-voucher-2026.html', related_analysis('B55353000001'))
        self.assertIn('emergency-vs-livelihood-2026.html', related_analysis('135200005003'))
        self.assertEqual(related_analysis('OTHER'), '')


if __name__ == '__main__':
    unittest.main()
