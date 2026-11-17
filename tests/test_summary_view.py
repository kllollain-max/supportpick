import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_detail_pages import row, BASE, NOW
from content_quality import audit, summary_view
from detail_pages import write_details, benefit_path
from benefit_analysis import related_analysis


class SummarySourceViewTests(unittest.TestCase):
    def test_placeholder_views_keep_source_data_and_field_meaning(self):
        for placeholder in ['상동 ', '-', '', '해당 없음']:
            a = row()
            a.update(summary=placeholder, target='기초생활보장 수급자 등 교육취약계층 학생', documents='해당없음')
            original = copy.deepcopy(a)
            self.assertEqual(summary_view(a), {'text': a['target'], 'label': '지원대상 원문 일부'})
            self.assertIn('placeholder_summary_review', audit({a['id']: a})['reviewCandidates'][a['id']])
            self.assertEqual(a, original)

    def test_normal_summary_or_missing_target_never_gets_invented_copy(self):
        a = row()
        self.assertEqual(summary_view(a), {'text': a['summary'], 'label': ''})
        a.update(summary='-', target='상동', targetPreview='')
        self.assertEqual(summary_view(a), {'text': '', 'label': ''})
        a['target'] = 'x' * 200
        self.assertEqual(summary_view(a)['text'], 'x' * 180 + '…')

    def test_static_excerpt_is_attributed_escaped_and_absent_from_held_page(self):
        with tempfile.TemporaryDirectory() as temp:
            a = row(); a.update(summary='상동 ', target='대상 <script>unsafe</script>')
            original = copy.deepcopy(a)
            out = Path(temp)
            write_details(out, {a['id']: a}, {}, BASE, {}, {}, 'success', NOW)
            html = (out / benefit_path(a['id']) / 'index.html').read_text()
            self.assertIn('지원대상 원문 일부: 대상 &lt;script&gt;unsafe&lt;/script&gt;', html)
            self.assertNotIn('<script>unsafe</script>', html)
            write_details(out, {a['id']: a}, {}, BASE,
                          {'holds': {a['id']: {'reason': '현행 금액 확인'}}}, {}, 'success', NOW)
            held = (out / benefit_path(a['id']) / 'index.html').read_text()
            self.assertNotIn('unsafe', held)
            self.assertNotIn('지원대상 원문 일부', held)
            self.assertEqual(a, original)

    def test_specific_birth_amount_conflict_is_held_without_holding_other_records(self):
        registry = json.loads((Path(__file__).resolve().parents[1] / 'guides.json').read_text())
        hold = registry['holds']['305000000113']
        self.assertEqual(hold['url'], 'https://www.ddm.go.kr/www/contents.do?key=756')
        self.assertEqual(len(hold['observedSourceHash']), 64)
        for sid in ['135200005015', '319000000130', '442000000135']:
            self.assertNotIn(sid, registry['holds'])
        for sid in ['135200005015', '305000000113', '319000000130', '442000000135']:
            self.assertIn('first-meeting-vs-parent-benefit-2026.html', related_analysis(sid))
