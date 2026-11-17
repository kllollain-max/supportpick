import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from application_guides import write_guides
from benefit_analysis import related_analysis
from detail_pages import material_hash, matching_blog, reviewed_guide, safe_reference, write_details
from test_detail_pages import BASE, NOW, row

ROOT = Path(__file__).resolve().parents[1]


class ClaimPreparationTests(unittest.TestCase):
    def test_insurance_reference_keeps_scheme_and_integrity_guards(self):
        a = row('171000000005')
        g = {'benefitId': a['id'], 'sourceHash': material_hash(a), 'status': 'reviewed',
             'reviewedAt': (NOW - timedelta(days=1)).isoformat(),
             'validUntil': (NOW + timedelta(days=14)).isoformat(), 'summary': '보험료와 보험금 구분',
             'checks': ['상품', '기간', '지급제한'], 'steps': ['확인', '신청', '결과'],
             'sourceReviews': [{'url': 'https://www.epostlife.go.kr/resources/js/biz/ip/gs/pdf/yoyak_P510062_202504.pdf',
                                'note': '본인 계약 적용 상품 확인'}]}
        self.assertIs(reviewed_guide(a, {'guides': [g]}, NOW), g)
        self.assertIsNone(reviewed_guide({**a, 'documents': 'changed'}, {'guides': [g]}, NOW))
        self.assertIsNone(reviewed_guide(a, {'guides': [g]}, NOW + timedelta(days=14)))
        for url in ['https://www.epostlife.go.kr.evil.example/', 'https://epostlife.example/',
                    'http://www.epostlife.go.kr/', 'https://www.epostlife.go.kr:8443/',
                    'https://user:pass@www.epostlife.go.kr/']:
            self.assertFalse(safe_reference(url), url)

    def test_new_comparisons_link_existing_records_without_creating_missing_details(self):
        slugs = {'999000000008': 'leave-benefit-claim-checklist-2026',
                 'WII000001460': 'leave-benefit-claim-checklist-2026',
                 'SD0000015536': 'unemployment-benefit-vs-pension-credit-2026',
                 'B55201500004': 'unemployment-benefit-vs-pension-credit-2026'}
        rows = {sid: {**row(sid), 'title': '서로 다른 지원 ' + sid, 'support': '지원 내용 ' + sid} for sid in slugs}
        original = copy.deepcopy(rows)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_guides(output, BASE, {})
            for sid, slug in slugs.items():
                self.assertNotIn('../benefits/' + sid + '/', (output / 'guides' / (slug + '.html')).read_text())
            report = write_details(output, rows, {}, BASE, {}, {}, 'success', NOW)
            write_guides(output, BASE, rows)
            self.assertEqual(report['report']['heldDetails'], 0)
            for sid, slug in slugs.items():
                self.assertIn('../../guides/' + slug + '.html', (output / 'benefits' / sid / 'index.html').read_text())
                self.assertIn('../benefits/' + sid + '/', (output / 'guides' / (slug + '.html')).read_text())
        self.assertEqual(rows, original)
        self.assertEqual(related_analysis('MISSING'), '')

    def test_rechecked_blog_preserves_publication_date_and_stops_at_its_review_deadline(self):
        for article in json.loads((ROOT / 'editorials.json').read_text())['articles']:
            values = json.loads(article['sourceKey'])
            a = row(article['benefitId'])
            for key, value in zip(('id', 'title', 'organization', 'region', 'period', 'summary'), values[:6]):
                a[key] = value
            a['sourceUpdatedAt'] = {'list': values[6], 'detail': values[7]}
            differences = article.get('reviewedSourceDifferences', {})
            a['sourceConflicts'] = list(differences)
            a['sourceDifferences'] = differences
            observed = datetime.fromisoformat(article['publicationObservedAt'].replace('Z', '+00:00'))
            verified = datetime.fromisoformat(article['verifiedAt'])
            until = datetime.fromisoformat(article['validUntil'])
            self.assertLess(observed, verified)
            self.assertIs(matching_blog(a, {'articles': [article]}, verified + timedelta(minutes=1)), article)
            self.assertIsNone(matching_blog(a, {'articles': [article]}, until))
            changed = {**a, 'period': a['period'] + ' changed'}
            self.assertIsNone(matching_blog(changed, {'articles': [article]}, verified + timedelta(minutes=1)))
            self.assertEqual(article['recheckEvidence']['http'], 200)
            self.assertTrue(article['recheckEvidence']['titleMatched'])
            self.assertEqual(len(article['recheckEvidence']['bodyTextSha256']), 64)

    def test_time_scoped_blog_review_does_not_outlive_its_application_deadline(self):
        caps = {'105100000001': '2026-12-01T23:59:59+09:00',
                '137100000236': '2026-11-30T18:00:00+09:00',
                '641000000138': '2026-12-01T18:00:00+09:00'}
        for article in json.loads((ROOT / 'editorials.json').read_text())['articles']:
            if article['benefitId'] in caps:
                self.assertLessEqual(datetime.fromisoformat(article['validUntil']),
                                     datetime.fromisoformat(caps[article['benefitId']]))


if __name__ == '__main__':
    unittest.main()
