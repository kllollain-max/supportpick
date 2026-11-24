import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from detail_pages import write_details,benefit_path
from test_detail_pages import row,BASE,NOW
from verify_release import Document
ROOT=Path(__file__).resolve().parents[1]

class ConfirmedRetiredBatchTests(unittest.TestCase):
    def test_proven_missing_pages_are_noindex_but_returning_sources_are_normal(self):
        registry=json.loads((ROOT/'guides.json').read_text())
        proof=json.loads((ROOT/'review-only/confirmed-retired-batch-20261125.json').read_text())
        ids=[x['id']for x in proof['records']]
        self.assertTrue(ids);self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(set(ids).issubset(registry['retiredIds']))
        self.assertTrue(set(proof['existingRetiredIdsPreserved']).issubset(registry['retiredIds']))
        with tempfile.TemporaryDirectory()as tmp:
            out=Path(tmp);absent=write_details(out,{}, {},BASE,registry,{},'success',NOW)
            for sid in ids:
                with self.subTest(phase='missing',id=sid):
                    self.assertEqual(next(x for x in proof['records']if x['id']==sid)['http'],404)
                    self.assertEqual(len(next(x for x in proof['records']if x['id']==sid)['oldSha256']),64)
                    path=benefit_path(sid);doc=Document();doc.feed((out/path/'index.html').read_text())
                    self.assertEqual(doc.robots,['noindex,follow'])
                    self.assertEqual(doc.canonical,[BASE+path]);self.assertEqual(doc.h1,1)
                    self.assertTrue(doc.title and doc.meta['description'])
                    self.assertNotIn(path,[x[0]for x in absent['entries']])
            rows={sid:{**row(sid),'title':'자료 복귀 회귀검사 '+sid}for sid in ids}
            returned=write_details(out,rows,{},BASE,registry,{},'success',NOW)
            for sid in ids:
                with self.subTest(phase='returned',id=sid):
                    path=benefit_path(sid);html=(out/path/'index.html').read_text()
                    self.assertNotIn('현재 공식 목록에서 확인되지 않는',html)
                    self.assertIn(path,[x[0]for x in returned['entries']])
                    self.assertIn('content="index,follow"',html)
