import copy
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from application_guides import write_guides
from detail_pages import blog_source_key, material_hash
from source_review_audit import audit
from test_detail_pages import BASE, NOW, row


def guide(a):
    return dict(benefitId=a['id'], status='reviewed', sourceHash=material_hash(a),
                reviewedAt=(NOW-timedelta(days=1)).isoformat(), validUntil=(NOW+timedelta(days=14)).isoformat(),
                summary='준비 안내', checks=['대상','금액','기간'], steps=['확인','접수','결과'],
                sourceReviews=[dict(url='https://www.moel.go.kr/',title='공식 안내',note='대조')])


class SourceReviewAuditTests(unittest.TestCase):
    def test_source_change_is_explained_only_with_a_proven_previous_baseline(self):
        old=row('service');new={**old,'support':'변경된 실제 지원 조건'};reg={'guides':[guide(old)]}
        original=copy.deepcopy((old,new,reg))
        r=audit({'service':new},{'service':old},reg,{},NOW)
        self.assertEqual(r['reviewRequired'],1)
        self.assertEqual(r['entries'][0]['changedFields'],['support'])
        self.assertEqual(r['entries'][0]['reason'],'source_material_changed')
        r=audit({'service':new},{},reg,{},NOW)
        self.assertEqual(r['entries'][0]['changedFields'],[])
        self.assertEqual(r['entries'][0]['fieldComparisonBasis'],'unavailable')
        self.assertEqual((old,new,reg),original)

    def test_timestamp_only_blog_key_change_is_reported_without_renewal(self):
        a=row('service');b={**a,'sourceUpdatedAt':{'list':'20261118090000','detail':'2026-11-18'}}
        article={'benefitId':'service','sourceKey':blog_source_key(a)}
        r=audit({'service':b},{},{},{'articles':[article]},NOW)
        self.assertEqual(r['entries'][0]['changedFields'],['sourceUpdatedAt.list','sourceUpdatedAt.detail'])
        self.assertEqual(r['entries'][0]['reason'],'source_binding_changed')
        self.assertEqual(article['sourceKey'],blog_source_key(a))

    def test_missing_ambiguous_expired_and_held_are_distinct(self):
        a=row('service');g=guide(a);registry={'guides':[g]}
        self.assertEqual(audit({}, {},registry,{},NOW)['entries'][0]['reason'],'not_in_current_source')
        self.assertEqual(audit({'service':a},{},{'guides':[g,g]}, {},NOW)['entries'][0]['reason'],'ambiguous_registration')
        self.assertEqual(audit({'service':a},{},registry,{},NOW+timedelta(days=15))['entries'][0]['reason'],'review_expired_or_invalid')
        held={**registry,'holds':{'service':{'reason':'공식 근거 검토'}}}
        self.assertEqual(audit({'service':a},{},held,{},NOW)['entries'][0]['reason'],'source_on_hold')
        self.assertEqual(audit({'service':a},{},registry,{},NOW)['active'],1)

    def test_only_rechecked_article_date_changes_and_publication_proof_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);entries=dict(write_guides(output,BASE,{}))
            self.assertEqual(entries['guides/leave-benefit-claim-checklist-2026.html'],'2026-11-18')
            self.assertEqual(entries['guides/scholarships-vs-student-loan-steps-2026.html'],'2026-11-17')
            html=(output/'guides/leave-benefit-claim-checklist-2026.html').read_text()
            self.assertIn('임신 중 배우자 돌봄과 급여 신청',html)
            self.assertIn('news_seq=19964',html)
        root=Path(__file__).resolve().parents[1]
        for a in json.loads((root/'editorials.json').read_text())['articles']:
            if 'bindingRecovery' in a:
                self.assertEqual(a['bindingRecovery']['changedFields'],['sourceUpdatedAt.list','sourceUpdatedAt.detail'])
                self.assertIn('publicationObservedAt',a)
                self.assertTrue(a['recheckEvidence']['officialLinksMatched'])


if __name__=='__main__':unittest.main()
