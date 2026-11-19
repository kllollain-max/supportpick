import copy,tempfile,unittest
from pathlib import Path
from application_guides import write_guides
from detail_pages import write_details
from reviewed_amount_analysis import review_advisory
from test_detail_pages import BASE,NOW,row

class ReviewedAmountsTests(unittest.TestCase):
    def test_advisories_are_tied_to_observed_sources_without_changing_values(self):
        for sid,token,slug in [('626000000649','1,6000','busan-child-care-fee-vs-copayment-2026'),('557000000250','10,00','jeungpyeong-insurance-contract-vs-claim-2026'),('875000000016','19,2500','school-welfare-vs-education-benefit-2026')]:
            p=row(sid);p['support']=token+'원';original=copy.deepcopy(p)
            with tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp);r=write_details(out,{sid:p},{},BASE,{'guides':[]},{},'success',NOW)
                text=(out/'benefits'/sid/'index.html').read_text()
                self.assertIn('reviewed-amount-advisory',text);self.assertIn('../../guides/'+slug+'.html',text)
                if sid=='875000000016':self.assertIn('.html#education-informatization',text)
                self.assertIn(token+'원',text);self.assertEqual(r['report']['heldDetails'],0)
            self.assertEqual(p,original)
            p['support']='공식 자료 변경 후 금액';self.assertEqual(review_advisory(p),'')
            p['support']='10,000천원 16,000원 19,250원';self.assertEqual(review_advisory(p),'')
            p['id']='other';p['support']=token+'원';self.assertEqual(review_advisory(p),'')

    def test_guides_explain_unresolved_boundaries_and_no_phantom_detail_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);dates=dict(write_guides(out,BASE,{}))
            b=(out/'guides/busan-child-care-fee-vs-copayment-2026.html').read_text()
            self.assertIn('올바른 비율이나 청구액을 결정한 것이 아닙니다',b)
            self.assertIn('16,000 × 4 = 64,000원',b);self.assertNotIn('href="../benefits/626000000649/"',b)
            j=(out/'guides/jeungpyeong-insurance-contract-vs-claim-2026.html').read_text()
            self.assertIn('2026.2.1.~2027.1.31.',j);self.assertIn('2026.5.21.~2027.5.20.',j)
            self.assertIn('5,000원',j);self.assertIn('500만원',j)
            s=(out/'guides/school-welfare-vs-education-benefit-2026.html').read_text()
            self.assertIn('17,600 + 1,650 = 19,250원',s);self.assertIn('경북 수집 원문의 정정액',s)
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')

    def test_empty_or_non_text_sources_do_not_trigger_advisories(self):
        self.assertEqual(review_advisory({}),'')
        self.assertEqual(review_advisory({'id':'626000000649','support':None}),'')
