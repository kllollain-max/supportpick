import copy,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from application_guides import write_guides
from content_quality import malformed_amounts,audit
from detail_pages import write_details
from test_detail_pages import BASE,row

class AmountReadingTests(unittest.TestCase):
    def test_comma_candidates_preserve_values_and_do_not_infer_correct_amount(self):
        for text,expected in [('9,00만원 / 5,00만원 / 1,00만원',['9,00','5,00','1,00']),('19,2500원 / 10,00만원',['19,2500','10,00']),('1,000원 1,500만원 15,000,000원 1.5억원 30만원',[]),('2026,11,19 신청 1,2명',[]),(None,[])]:
            p=row();p['support']=text;before=copy.deepcopy(p)
            self.assertEqual(malformed_amounts(p),expected);self.assertEqual(p,before)

    def test_quality_signal_is_review_only_without_new_indexing_restrictions(self):
        p=row('477000000110');p.update(title='출산장려금 지원',organization='전북특별자치도 순창군',support='9,00만원(30만원 x 30개월)')
        original=copy.deepcopy(p);q=audit({p['id']:p});self.assertEqual(q['checks']['amount_comma_needs_check'],1)
        self.assertFalse(q['automaticIndexingChange']);self.assertFalse(q['automaticDeletion'])
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);r=write_details(out,{p['id']:p},{},BASE,{'guides':[]},{},'success',datetime(2026,11,19,tzinfo=timezone.utc))
            s=(out/'benefits/477000000110/index.html').read_text()
            self.assertIn('9,00만원(30만원 x 30개월)',s);self.assertIn('amount-source-notice',s)
            self.assertIn('../../guides/sunchang-birth-total-vs-installments-2026.html',s)
            self.assertEqual(r['report']['heldDetails'],0);self.assertNotIn('noindex,follow',s)
        self.assertEqual(p,original)

    def test_held_body_does_not_expose_malformed_amount(self):
        p=row('held');p['support']='9,00만원'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);write_details(out,{'held':p},{},BASE,{'guides':[],'holds':{'held':{'reason':'확인 중'}}},{},'success')
            s=(out/'benefits/held/index.html').read_text();self.assertNotIn('9,00만원',s);self.assertNotIn('amount-source-notice',s)

    def test_authored_guide_distinguishes_units_and_source_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);dates=dict(write_guides(out,BASE,{}));s=(out/'guides/sunchang-birth-total-vs-installments-2026.html').read_text()
            self.assertIn('100 + (30 × 30) + (100 × 5) = 1,500만원',s)
            self.assertIn('넷째아이상',s);self.assertIn('다섯째 이상',s)
            self.assertNotIn('href="../benefits/477000000110/"',s)
            self.assertEqual(dates['guides/sunchang-birth-total-vs-installments-2026.html'],'2026-11-19')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')
