import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_detail_pages import row, BASE, NOW
from test_collection import Client
from collect_full import collect
from refresh import install_candidate
from build import build
from application_guides import write_guides
from culture_pension_analysis import source_advisory
from detail_pages import write_details, benefit_path


class CulturePensionSourceTests(unittest.TestCase):
    def test_only_the_observed_typo_gets_a_correction_link_and_source_stays_intact(self):
        a = row('648000001107'); a['method'] = '온라인 www.mnurri.kr 안내'
        original = copy.deepcopy(a)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            result = write_details(output, {a['id']: a}, {}, BASE, {}, {}, 'success', NOW)
            html = (output / benefit_path(a['id']) / 'index.html').read_text()
            self.assertIn('신청 주소 확인:', html)
            self.assertIn('https://www.mnuri.kr/munhwa/cardIssueGuide.do', html)
            self.assertIn('온라인 www.mnurri.kr 안내', html)
            self.assertEqual(result['report']['heldDetails'], 0)
        self.assertEqual(a, original)
        self.assertEqual(source_advisory({**a, 'method': '온라인 www.mnuri.kr 안내'}), '')
        self.assertEqual(source_advisory({**a, 'id': 'OTHER'}), '')

    def test_a_historical_period_is_not_rewritten_or_treated_as_a_new_hold(self):
        a = row('B55151000066')
        a.update(period='2025.02.03~2025.11.28', summary='2025년 기준 14만 원', support='2025년 기준 14만 원')
        original = copy.deepcopy(a)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            result = write_details(output, {a['id']: a}, {}, BASE, {}, {}, 'success', NOW)
            html = (output / benefit_path(a['id']) / 'index.html').read_text()
            self.assertIn('지난 연도 자료:', html)
            self.assertIn('2025년 기준 14만 원', html)
            self.assertEqual(result['report']['heldDetails'], 0)
        self.assertEqual(a, original)
        self.assertEqual(source_advisory({**a, 'period': '2026.2.2.~2026.11.30.'}), '')

    def test_related_source_order_does_not_depend_on_input_dictionary_order(self):
        a, b = row('137100000236'), row('648000001107')
        with tempfile.TemporaryDirectory() as temp:
            roots = [Path(temp) / 'one', Path(temp) / 'two']
            for root in roots:
                for sid in [a['id'], b['id']]:
                    p = root / benefit_path(sid); p.mkdir(parents=True); (p / 'index.html').write_text('existing')
            write_guides(roots[0], BASE, {a['id']: a, b['id']: b})
            write_guides(roots[1], BASE, {b['id']: b, a['id']: a})
            self.assertEqual((roots[0] / 'guides/culture-card-deadlines-2026.html').read_bytes(),
                             (roots[1] / 'guides/culture-card-deadlines-2026.html').read_bytes())

    def test_same_snapshot_has_identical_public_files_when_shard_enumeration_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collect(Client(), root / 'run', 'stable-source-test')
            install_candidate(root / 'run', root / 'state')
            build(root / 'one', root / 'state', public_base=BASE)
            original = Path.glob
            def reverse(path, pattern):
                values = list(original(path, pattern))
                return iter(reversed(values))
            with patch.object(Path, 'glob', reverse):
                build(root / 'two', root / 'state', public_base=BASE)
            first = json.loads((root / 'one/site-manifest.json').read_text())
            second = json.loads((root / 'two/site-manifest.json').read_text())
            self.assertEqual(first['files'], second['files'])
            self.assertEqual(first['contentFingerprint'], second['contentFingerprint'])
