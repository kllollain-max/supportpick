import copy,tempfile,unittest
from pathlib import Path
from application_guides import write_guides
from detail_pages import write_details
from influenza_analysis import influenza_advisory
from test_detail_pages import BASE,NOW,row

class InfluenzaAnalysisTests(unittest.TestCase):
    def test_source_discrepancy_notice_preserves_data_and_retires_with_old_token(self):
        p=row('135200000115');p['support']='기준일2025.6.30까지 총1회';original=copy.deepcopy(p)
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);result=write_details(out,{p['id']:p},{},BASE,{'guides':[]},{},'success',NOW)
            text=(out/'benefits'/p['id']/'index.html').read_text()
            self.assertIn('influenza-source-advisory',text);self.assertIn('기준일2025.6.30까지 총1회',text)
            self.assertIn('../../guides/influenza-season-vs-dose-history-2026.html',text)
            self.assertEqual(result['report']['heldDetails'],0)
        self.assertEqual(p,original)
        p['support']='2026.6.30';self.assertEqual(influenza_advisory(p),'')
        p['id']='other';p['support']='2025.6.30';self.assertEqual(influenza_advisory(p),'')
        self.assertEqual(influenza_advisory({}),'')
        self.assertEqual(influenza_advisory({'id':'135200000115','support':None}),'')

    def test_season_and_individual_dose_limits_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);dates=dict(write_guides(out,BASE,{}));s=(out/'guides/influenza-season-vs-dose-history-2026.html').read_text()
            for token in ['2025.6.30.','2026.6.30.','2026.9.21.~2027.4.30.','2026.10.6.~2027.4.30.','2026.10.12.~2027.4.30.','2026.10.15.~2027.4.30.','예진의사','생후6개월','2020~2021절기','아무 병원에서나','건강·임신·접종 이력 자료']:self.assertIn(token,s)
            self.assertEqual(s.count('<table>'),2)
            self.assertNotIn('href="../benefits/135200000115/"',s)
            self.assertEqual(dates['guides/influenza-season-vs-dose-history-2026.html'],'2026-11-19')
            self.assertEqual(dates['guides/energy-voucher-2026.html'],'2026-11-17')
