import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from detail_pages import write_details
from test_detail_pages import row,BASE,NOW
class RetirementQuestions(unittest.TestCase):
 def test_questions_render_without_extending_review(self):
  registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
  guide=next(x for x in registry['guides']if x['benefitId']=='WII000000310')
  self.assertEqual(guide['validUntil'],'2026-12-01T08:18:48.889696+00:00')
  self.assertEqual(guide['reviewedAt'],'2026-11-17T08:18:48.889696+00:00')
  a=row('WII000000310');a['title']='노후준비서비스제공'
  from detail_pages import material_hash
  from datetime import datetime,timezone
  guide['sourceHash']=material_hash(a)
  with tempfile.TemporaryDirectory()as tmp:
   out=Path(tmp)
   write_details(out,{a['id']:a},{},BASE,{'guides':[guide]}, {},'success',datetime(2026,11,26,tzinfo=timezone.utc))
   html=(out/'benefits'/a['id']/'index.html').read_text()
   self.assertIn('개인 강의를 듣고 싶은데',html)
   self.assertIn('종합재무설계는 처음 접수하면',html)
   self.assertIn('UHKB0601M0.do',html)
   self.assertNotIn('연금 수급 확정으로 기록합니다',html)
