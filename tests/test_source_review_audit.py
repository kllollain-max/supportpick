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


    def test_unchanged_hold_stays_held_and_editorial_counts_are_separate(self):
        a=row('service')
        registry={'guides':[guide(a)], 'holds':{'service':{'observedSourceHash':material_hash(a)}}}
        original=copy.deepcopy((a,registry))
        report=audit({'service':a},{},registry,{},NOW)
        self.assertEqual((report['registeredEntries'],report['active'],report['reviewRequired']),(1,0,1))
        self.assertEqual((report['holdEntries'],report['holdReviewRequired']),(1,0))
        self.assertEqual(report['holds'][0]['reason'],'held_source_unchanged')
        self.assertEqual(report['holds'][0]['status'],'held')
        self.assertEqual((a,registry),original)

    def test_changed_hold_requires_review_with_only_proven_field_differences(self):
        old=row('service');new={**old,'selection':'현재 공식 기준으로 갱신된 조건'}
        registry={'holds':{'service':{'observedSourceHash':material_hash(old)}}}
        original=copy.deepcopy((old,new,registry))
        report=audit({'service':new},{'service':old},registry,{},NOW)
        item=report['holds'][0]
        self.assertEqual((report['registeredEntries'],report['reviewRequired']),(0,0))
        self.assertEqual(report['holdReviewRequired'],1)
        self.assertEqual(item['reason'],'held_source_material_changed')
        self.assertEqual(item['changedFields'],['selection'])
        self.assertEqual(item['fieldComparisonBasis'],'previous_source_matches_observed_hold_hash')
        self.assertEqual(item['status'],'held')
        for previous in ({},{'service':new}):
            item=audit({'service':new},previous,registry,{},NOW)['holds'][0]
            self.assertEqual(item['changedFields'],[])
            self.assertEqual(item['fieldComparisonBasis'],'unavailable')
        self.assertEqual((old,new,registry),original)

    def test_missing_and_unrecorded_hold_baselines_are_not_silently_renewed(self):
        a=row('service')
        for baseline in (None,'',42,'x'*64,'A'*64):
            entry={} if baseline is None else {'observedSourceHash':baseline}
            registry={'holds':{'service':entry}}
            original=copy.deepcopy(registry)
            report=audit({'service':a},{'service':a},registry,{},NOW)
            self.assertEqual(report['holds'][0]['reason'],'hold_baseline_unavailable')
            self.assertEqual(report['holdReviewRequired'],1)
            self.assertEqual(registry,original)
        registry={'holds':{'service':{'observedSourceHash':material_hash(a)}}}
        item=audit({}, {'service':a},registry,{},NOW)['holds'][0]
        self.assertEqual(item['reason'],'not_in_current_source')
        self.assertEqual(item['status'],'held')
        self.assertEqual(item['changedFields'],[])

    def test_hold_timestamps_do_not_trigger_material_change_or_clear_hold(self):
        a=row('service');new={**a,'sourceUpdatedAt':{'list':'20261118090000','detail':'2026-11-18'}}
        registry={'holds':{'service':{'observedSourceHash':material_hash(a)}}}
        item=audit({'service':new},{'service':a},registry,{},NOW)['holds'][0]
        self.assertEqual(item['reason'],'held_source_unchanged')
        self.assertEqual(item['status'],'held')

    def test_existing_legacy_holds_are_visible_without_inventing_baselines(self):
        root=Path(__file__).resolve().parents[1]
        registry=json.loads((root/'guides.json').read_text())
        report=audit({}, {},registry,{},NOW)
        self.assertEqual(report['holdEntries'],len(registry['holds']))
        self.assertEqual({x['benefitId'] for x in report['holds']},set(registry['holds']))
        self.assertTrue(all(x['status']=='held' for x in report['holds']))
        self.assertTrue(all(x['reason']=='not_in_current_source' for x in report['holds']))


if __name__=='__main__':unittest.main()
