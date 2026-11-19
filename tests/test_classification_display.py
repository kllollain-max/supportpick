import copy
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from detail_pages import write_details
from test_detail_pages import BASE,row
from test_support_display import checked

NOW=datetime(2026,11,19,2,tzinfo=timezone.utc)

class ClassificationDisplayTests(unittest.TestCase):
    def test_difference_is_qualified_at_the_top_and_attributed_values_survive(self):
        a=row('different');a['sourceConflicts']=['지원유형'];a['sourceDifferences']={'지원유형':{'list':'현금||<img src=x>','detail':'서비스(돌봄)'}}
        b=row('normal');b['title']='다른 정상 사업';original=copy.deepcopy((a,b))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);r=write_details(out,{a['id']:a,b['id']:b},{},BASE,{'guides':[]},{},'success',NOW)
            text=(out/'benefits/different/index.html').read_text()
            self.assertIn('<dt>지원방식</dt><dd>목록·상세 분류 차이 · 원문 확인',text)
            self.assertIn('href="#source-differences"',text);self.assertIn('id="source-differences"',text)
            self.assertIn('현금||&lt;img src=x&gt;',text);self.assertNotIn('<img src=x>',text)
            dates=dict(r['entries']);self.assertEqual(dates['benefits/different/'],'2026-11-19')
            self.assertEqual(dates['benefits/normal/'],'2026-11-17')
        self.assertEqual((a,b),original)

    def test_held_facts_stay_hidden_and_reviewed_display_keeps_precedence(self):
        a=row('different');a['sourceConflicts']=['지원유형'];a['sourceDifferences']={'지원유형':{'list':'현금','detail':'서비스'}}
        # An explicit, source-bound display review remains authoritative on the page.
        g=checked(a);g.update(reviewedAt=(NOW-timedelta(days=1)).isoformat(),validUntil=(NOW+timedelta(days=14)).isoformat())
        g['supportDisplay']['text']='대조한 지급 경로'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            write_details(out,{a['id']:a},{},BASE,{'guides':[g]},{},'success',NOW)
            self.assertIn('<dt>지원방식</dt><dd>대조한 지급 경로',(out/'benefits/different/index.html').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);write_details(out,{a['id']:a},{},BASE,{'guides':[],'holds':{a['id']:{'reason':'공식 확인 필요'}}},{},'success',NOW)
            text=(out/'benefits/different/index.html').read_text();self.assertNotIn('<dt>지원방식</dt>',text);self.assertNotIn('id="source-differences"',text)

    def test_flag_without_source_pair_does_not_create_a_broken_anchor(self):
        a=row('different');a['sourceConflicts']=['지원유형']
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);write_details(out,{a['id']:a},{},BASE,{'guides':[]},{},'success',NOW)
            text=(out/'benefits/different/index.html').read_text();self.assertIn('목록·상세 분류 차이',text);self.assertNotIn('href="#source-differences"',text)
