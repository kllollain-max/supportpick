import copy
import json
import tempfile
import unittest
from pathlib import Path
from application_guides import write_guides
from detail_pages import write_details, material_hash
from source_review_audit import audit
from test_detail_pages import BASE, NOW, row

class DidimdolTests(unittest.TestCase):
    def test_new_source_baseline_keeps_old_loan_conditions_hidden(self):
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        a=row('B55140800003');a['support']='OUTDATED_LOAN_CAP_AND_RATE';a['selection']='OUTDATED_LOAN_ELIGIBILITY'
        registry['holds'][a['id']]['observedSourceHash']=material_hash(a)
        original=copy.deepcopy((a,registry))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);result=write_details(out,{a['id']:a},{},BASE,registry,{},'success',NOW)
            text=(out/'benefits/B55140800003/index.html').read_text()
            self.assertNotIn('OUTDATED_LOAN_CAP_AND_RATE',text)
            self.assertNotIn('OUTDATED_LOAN_ELIGIBILITY',text)
            self.assertIn('noindex,follow',text)
            self.assertIn('../../guides/didimdol-cap-collateral-and-closing-2026.html',text)
            self.assertEqual(result['report']['heldDetails'],1)
        item=next(x for x in audit({a['id']:a},{},registry,{},NOW)['holds'] if x['benefitId']==a['id'])
        self.assertEqual((item['reason'],item['status']),('held_source_unchanged','held'))
        self.assertEqual((a,registry),original)

    def test_dated_guide_does_not_invent_links_or_refresh_other_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);dates=dict(write_guides(out,BASE,{}))
            text=(out/'guides/didimdol-cap-collateral-and-closing-2026.html').read_text()
            self.assertNotIn('href="../benefits/B55140800003/"',text)
            self.assertEqual(dates['guides/didimdol-cap-collateral-and-closing-2026.html'],'2026-11-19')
            self.assertEqual(dates['guides/youth-housing-account-announcement-tax-conversion-2026.html'],'2026-11-18')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')

if __name__=='__main__':unittest.main()
