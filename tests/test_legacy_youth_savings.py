import copy
import json
import tempfile
import unittest
from pathlib import Path

from application_guides import write_guides
from detail_pages import write_details, material_hash
from source_review_audit import audit
from test_detail_pages import BASE, NOW, row


class LegacyYouthSavingsTests(unittest.TestCase):
    def test_new_review_evidence_does_not_release_held_source_or_expose_raw_conditions(self):
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        a=row('SD0000011848');a['support']='LEGACY_YOUTH_SAVINGS_BODY'
        a['selection']='LEGACY_YOUTH_SAVINGS_CONDITIONS';original=copy.deepcopy((a,registry))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            result=write_details(output,{a['id']:a},{},BASE,registry,{},'success',NOW)
            html=(output/'benefits/SD0000011848/index.html').read_text()
            self.assertNotIn('LEGACY_YOUTH_SAVINGS_BODY',html)
            self.assertNotIn('LEGACY_YOUTH_SAVINGS_CONDITIONS',html)
            self.assertIn('noindex,follow',html)
            self.assertIn('../../guides/youth-mutual-aid-closed-enrollment-maturity-2026.html',html)
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
            html=(output/'guides/youth-mutual-aid-closed-enrollment-maturity-2026.html').read_text()
            self.assertEqual(dates['guides/youth-mutual-aid-closed-enrollment-maturity-2026.html'],'2026-11-18')
            self.assertIn('2024년부터 신규지원 중단',html)
            self.assertIn('2023년 가입 유형의 합계',html)
            self.assertIn('접수일로부터7일 이내',html)
            self.assertIn('지급청구서 접수 다음날부터7영업일 이내',html)
            self.assertIn('15영업일 이내(신청일·공휴일 제외)',html)
            self.assertIn('임의 입금하지 않도록',html)
            self.assertNotIn('href="../benefits/SD0000011848/"',html)
            self.assertEqual(dates['guides/maternal-service-application-use-refund-2026.html'],'2026-11-18')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')


if __name__=='__main__':unittest.main()
