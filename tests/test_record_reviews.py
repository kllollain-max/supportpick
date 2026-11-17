import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from record_reviews import approved_distinctions, scope_hash
from content_quality import audit, review_queue
from savings_voucher_analysis import RECORD_ARTICLES

NOW = datetime(2026, 11, 18, tzinfo=timezone.utc)


class RecordReviewTests(unittest.TestCase):
    def setUp(self):
        self.rows = {sid: {'id':sid, 'title':'같은 이름', 'organization':'같은 기관',
            'target':'서로 다른 대상 '+sid, 'support':support, 'method':'방문',
            'period':'기관별 상이', 'documents':'기관 확인', 'contact':'창구 '+sid,
            'officialUrl':'https://plus.gov.kr/', 'summary':'지원 내용 안내',
            'sourceUpdatedAt':{'list':'20260101','detail':'2026-01-01'}}
            for sid,support in [('A','지원 A'),('B','지원 B')]}
        self.entry = {'ids':['A','B'], 'decision':'keep_separate_source_records',
            'reason':'서로 다른 대상·금액을 제공한 원본 유지',
            'reviewedAt':'2026-11-17T00:00:00Z', 'validUntil':'2026-12-01T00:00:00Z',
            'sourceScopeHashes':{sid:scope_hash(r) for sid,r in self.rows.items()},
            'evidence':[{'url':'https://plus.gov.kr/','note':'공식 수집 자료 대조'}]}

    def approved(self, entry=None, rows=None, groups=None):
        return approved_distinctions(rows or self.rows, groups or [['A','B']],
            {'version':1,'groups':[entry or self.entry]}, NOW)

    def test_valid_decision_preserves_every_source_and_all_existing_holds(self):
        rows=copy.deepcopy(self.rows)
        q=review_queue(self.rows,audit(self.rows),{'heldReasons':{'A':['기존 보류 유지']},'guideIds':[]},
            NOW,{'version':1,'groups':[self.entry]})
        byid={r['id']:r for r in q['items']}
        self.assertEqual(self.rows,rows)
        self.assertEqual(set(byid),{'A','B'})
        self.assertEqual(byid['A']['reviewState'],'기존 공개 보류 재확인')
        self.assertEqual(byid['B']['reviewState'],'수정 대기')
        self.assertEqual(byid['B']['sameNameAgencyIds'],['A','B'])
        self.assertEqual(q['reviewedSeparateSourceGroups'],1)
        self.assertFalse(q['automaticDeletion'])
        self.assertFalse(q['automaticIndexingChange'])

    def test_any_material_scope_change_reopens_group_review(self):
        for field in ('title','organization','target','support','period','method','documents','contact','officialUrl'):
            rows=copy.deepcopy(self.rows);rows['A'][field]+=' 변경'
            self.assertEqual(self.approved(rows=rows),{},field)

    def test_expired_future_or_unzoned_decisions_do_not_suppress_review(self):
        for field,value in [('validUntil','2026-11-18T00:00:00Z'),
            ('reviewedAt','2026-11-19T00:00:00Z'),('reviewedAt','2026-11-17T00:00:00'),
            ('validUntil','2027-12-01T00:00:00Z')]:
            entry={**self.entry,field:value}
            self.assertEqual(self.approved(entry),{},field)

    def test_group_membership_or_untrusted_evidence_requires_review(self):
        self.assertEqual(self.approved(groups=[['A','B','C']]),{})
        for url in ['javascript:alert(1)','https://example.com/','http://plus.gov.kr/']:
            entry={**self.entry,'evidence':[{'url':url,'note':'자료'}]}
            self.assertEqual(self.approved(entry),{})

    def test_missing_decision_keeps_original_duplicate_candidate(self):
        q=review_queue(self.rows,audit(self.rows),{'heldReasons':{},'guideIds':[]},NOW)
        self.assertTrue(all(r['reviewState']=='통합 검토' for r in q['items']))
        self.assertEqual(q['reviewedSeparateSourceGroups'],0)

    def test_real_registry_is_limited_to_exact_two_sources(self):
        root=Path(__file__).resolve().parents[1]
        registry=json.loads((root/'record-reviews.json').read_text())
        self.assertEqual(len(registry['groups']),1)
        self.assertEqual(set(registry['groups'][0]['ids']),{'646000000145','629000000182'})
        self.assertIn('646000000145',json.loads((root/'guides.json').read_text())['holds'])

    def test_analysis_separates_raw_api_from_current_local_notice_and_conditional_math(self):
        articles={a[0]:a for a in RECORD_ARTICLES}
        voucher=articles['women-farmer-voucher-records-2026'][3]
        savings=articles['youth-savings-contribution-2026'][3]
        self.assertIn('현행 자격 확정표 아님',voucher)
        self.assertIn('다른 지역에 이 기준을 확대하지 않습니다',voucher)
        self.assertIn('추가 모집을 확인한 안내가 아니며',voucher)
        self.assertIn('정부가 60만원을 붙여준다는 뜻',savings)
        self.assertIn('1,800만원',savings)
        self.assertIn('이 접수 기간은 현재 경과했습니다',savings)
        self.assertIn('가상 예시',savings)


if __name__=='__main__':
    unittest.main()
