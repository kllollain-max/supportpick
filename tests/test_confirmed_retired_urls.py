import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from detail_pages import write_details,benefit_path
from test_detail_pages import row,BASE,NOW

class ConfirmedRetiredTests(unittest.TestCase):
    def test_every_confirmed_address_survives_missing_snapshots_and_normal_return(self):
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        for sid in ['478100000037','497000000103','O00027400003','628000000176']:
            with self.subTest(id=sid),tempfile.TemporaryDirectory()as tmp:
                out=Path(tmp);missing=write_details(out,{}, {},BASE,registry,{},'success',NOW)
                path=benefit_path(sid);html=(out/path/'index.html').read_text()
                self.assertIn('content="noindex,follow"',html)
                self.assertNotIn(path,[x[0]for x in missing['entries']])
                returned=write_details(out,{sid:row(sid)}, {},BASE,registry,{},'success',NOW)
                self.assertIn(path,[x[0]for x in returned['entries']])
                self.assertNotIn('현재 공식 목록에서 확인되지 않는',(out/path/'index.html').read_text())
                self.assertIn('content="index,follow"',(out/path/'index.html').read_text())
