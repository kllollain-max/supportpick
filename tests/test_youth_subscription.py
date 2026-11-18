import copy
import json
import tempfile
import unittest
from pathlib import Path

from application_guides import write_guides
from detail_pages import write_details, material_hash
from source_review_audit import audit
from test_detail_pages import BASE, NOW, row


class YouthSubscriptionTests(unittest.TestCase):
    def test_reviewed_source_remains_held_and_raw_financial_conditions_stay_hidden(self):
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        a=row('161300000088');a['support']='OLD_ACCOUNT_RATE_BODY';a['selection']='OLD_ACCOUNT_INCOME_BODY'
        registry['holds'][a['id']]['observedSourceHash']=material_hash(a)
        original=copy.deepcopy((a,registry))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            result=write_details(output,{a['id']:a},{},BASE,registry,{},'success',NOW)
            text=(output/'benefits/161300000088/index.html').read_text()
            self.assertNotIn('OLD_ACCOUNT_RATE_BODY',text)
            self.assertNotIn('OLD_ACCOUNT_INCOME_BODY',text)
            self.assertIn('noindex,follow',text)
            self.assertIn('../../guides/youth-housing-account-announcement-tax-conversion-2026.html',text)
            self.assertEqual(result['report']['heldDetails'],1)
        item=next(x for x in audit({a['id']:a},{},registry,{},NOW)['holds'] if x['benefitId']==a['id'])
        self.assertEqual((item['reason'],item['status']),('held_source_unchanged','held'))
        self.assertEqual((a,registry),original)

    def test_new_guide_has_no_nonexistent_detail_link_and_does_not_retimestamp_old_guides(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);dates=dict(write_guides(output,BASE,{}))
            text=(output/'guides/youth-housing-account-announcement-tax-conversion-2026.html').read_text()
            self.assertNotIn('href="../benefits/161300000088/"',text)
            self.assertEqual(dates['guides/youth-housing-account-announcement-tax-conversion-2026.html'],'2026-11-18')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')


if __name__=='__main__':unittest.main()
