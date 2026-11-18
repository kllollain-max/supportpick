import copy
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from test_detail_pages import BASE, NOW, row
from detail_pages import material_hash, support_display, write_details


def checked(a):
    return dict(benefitId=a['id'], status='reviewed', sourceHash=material_hash(a),
                reviewedAt=(NOW-timedelta(days=1)).isoformat(),
                validUntil=(NOW+timedelta(days=14)).isoformat(),
                summary='공식 자료 대조', checks=['대상','금액','기간'], steps=['확인','접수','결과'],
                sourceReviews=[dict(url='https://www.incheon.go.kr/',title='시청 안내',note='지급 경로 대조')],
                supportDisplay=dict(text='기본 포인트 · 조건부 현금 경로',sourceUrl='https://www.incheon.go.kr/'))


class SupportDisplayTests(unittest.TestCase):
    def test_clarification_renders_but_raw_classification_is_preserved(self):
        a=row('local');original=copy.deepcopy(a);g=checked(a)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            write_details(output,{'local':a},{},BASE,{'guides':[g]},{},'success',NOW)
            html=(output/'benefits/local/index.html').read_text()
            self.assertIn('<dt>지원방식</dt><dd>기본 포인트 · 조건부 현금 경로',html)
            self.assertIn('href="https://www.incheon.go.kr/"',html)
            self.assertEqual(a,original)
            self.assertEqual(a['supportType'],'현금')

    def test_changed_source_or_expired_review_cannot_keep_override(self):
        a=row('local');g=checked(a)
        self.assertIsNotNone(support_display(a,g,NOW))
        self.assertIsNone(support_display({**a,'support':'지급 조건 변경'},g,NOW))
        self.assertIsNone(support_display(a,g,NOW+timedelta(days=15)))
        self.assertIsNone(support_display(a,None,NOW))

    def test_override_requires_a_reviewed_source_and_a_short_single_line(self):
        a=row('local');g=checked(a)
        for bad in [dict(text='현금 확정',sourceUrl='https://other.go.kr/'),
                    dict(text='분류',sourceUrl={}),dict(text='여러\n줄',sourceUrl='https://www.incheon.go.kr/'),
                    dict(text='x'*101,sourceUrl='https://www.incheon.go.kr/')]:
            self.assertIsNone(support_display(a,{**g,'supportDisplay':bad},NOW))

    def test_label_is_escaped_and_held_facts_are_not_exposed(self):
        a=row('local');g=checked(a);g['supportDisplay']['text']='<img src=x>'
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            write_details(output,{'local':a},{},BASE,{'guides':[g]},{},'success',NOW)
            html=(output/'benefits/local/index.html').read_text()
            self.assertIn('&lt;img src=x&gt;',html)
            self.assertNotIn('<img src=x>',html)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            write_details(output,{'local':a},{},BASE,{'guides':[g],'holds':{'local':{'reason':'공식 확인 필요'}}},{},'success',NOW)
            html=(output/'benefits/local/index.html').read_text()
            self.assertNotIn('&lt;img src=x&gt;',html)
            self.assertNotIn('<dt>지원방식</dt>',html)
