import copy
import json
import tempfile
import unittest
from pathlib import Path

from application_guides import write_guides
from detail_pages import write_details, material_hash
from source_review_audit import audit
from test_detail_pages import BASE, NOW, row


class RentalGuaranteeTests(unittest.TestCase):
    def test_new_review_evidence_does_not_release_held_source_or_expose_raw_conditions(self):
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        a=row('161300000103');a['support']='UNRESOLVED_GUARANTEE_BODY'
        a['selection']='UNRESOLVED_GUARANTEE_CONDITIONS';original=copy.deepcopy((a,registry))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            result=write_details(output,{a['id']:a},{},BASE,registry,{},'success',NOW)
            html=(output/'benefits/161300000103/index.html').read_text()
            self.assertNotIn('UNRESOLVED_GUARANTEE_BODY',html)
            self.assertNotIn('UNRESOLVED_GUARANTEE_CONDITIONS',html)
            self.assertIn('noindex,follow',html)
            self.assertIn('../../guides/rental-guarantee-fee-cap-and-dates-2026.html',html)
            self.assertEqual(result['report']['heldDetails'],1)
        self.assertEqual((a,registry),original)
        # Recording a reviewed baseline is not permission to publish the record.
        baseline=copy.deepcopy(registry);baseline['holds'][a['id']]['observedSourceHash']=material_hash(a)
        item=next(x for x in audit({a['id']:a},{},baseline,{},NOW)['holds'] if x['benefitId']==a['id'])
        self.assertEqual(item['reason'],'held_source_unchanged')
        self.assertEqual(item['status'],'held')

    def test_authored_comparison_preserves_distinct_dates_and_avoids_missing_detail_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);dates=dict(write_guides(output,BASE,{}))
            html=(output/'guides/rental-guarantee-fee-cap-and-dates-2026.html').read_text()
            self.assertEqual(dates['guides/rental-guarantee-fee-cap-and-dates-2026.html'],'2026-11-18')
            self.assertIn('이전 사업 신청자',html)
            self.assertIn('이전 보증 가입자',html)
            self.assertIn('225,000원',html)
            self.assertIn('실제 지급 판정 아님',html)
            self.assertIn('어느 한 페이지의 표현을 전국 공통 기준으로 확정하지 않았습니다',html)
            self.assertNotIn('href="../benefits/161300000103/"',html)
            self.assertEqual(dates['guides/maternal-service-application-use-refund-2026.html'],'2026-11-18')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')


if __name__=='__main__':unittest.main()
