import json,sys,tempfile,unittest,copy
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from detail_pages import write_details,material_hash,editorial_modified
from test_detail_pages import row,BASE
NOW=datetime(2026,11,27,tzinfo=timezone.utc)
class EditorialDates(unittest.TestCase):
 def test_modified_faq_changes_lastmod_without_renewing_source_review(self):
  registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
  for sid,day in [('171000000005','2026-11-27'),('WII000000310','2026-11-26')]:
   with self.subTest(sid=sid),tempfile.TemporaryDirectory()as tmp:
    g=copy.deepcopy(next(x for x in registry['guides']if x['benefitId']==sid));a=row(sid);g['sourceHash']=material_hash(a)
    original=(g['reviewedAt'],g['validUntil']);out=Path(tmp)
    result=write_details(out,{sid:a},{},BASE,{'guides':[g]}, {},'success',NOW)
    self.assertIn(('benefits/'+sid+'/',day),result['entries'])
    self.assertEqual((g['reviewedAt'],g['validUntil']),original)
    html=(out/'benefits'/sid/'index.html').read_text()
    if sid=='171000000005':self.assertIn('사고보험금 청구서류',html);self.assertIn('PYIMIM0001.do',html)
    g['validUntil']='2026-11-26T00:00:00+00:00'
    expired=write_details(out,{sid:a},{},BASE,{'guides':[g]}, {},'success',NOW)
    self.assertNotIn(sid,expired['report']['guideIds'])
    self.assertNotIn('사고보험금 청구서류',(out/'benefits'/sid/'index.html').read_text())
 def test_invalid_future_or_missing_editorial_date_is_not_a_lastmod(self):
  for value in [None,'','2026-99-01','2026-11-28','2026-11-27T00:00:00Z',123]:
   with self.subTest(value=value):self.assertIsNone(editorial_modified({'contentModifiedAt':value},NOW))
