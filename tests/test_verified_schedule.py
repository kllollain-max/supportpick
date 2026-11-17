import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from application_guides import write_guides
from detail_pages import material_hash, reviewed_guide, schedule_metadata, status, write_details
from education_business_analysis import LOAN, SCHOLAR
import verified_schedule as S
from test_detail_pages import BASE, row

NOW = datetime(2026, 11, 17, 9, 0, tzinfo=timezone.utc)


def schedule():
    return dict(scope='2026년 2학기 일반 신청', applicationStart='2026-07-01T09:00:00+09:00',
                applicationEnd='2026-11-17T18:00:00+09:00', followupLabel='대출 실행',
                followupEnd='2026-11-18T17:00:00+09:00', sourceUrl=LOAN,
                reviewedAt='2026-11-16T12:00:00+09:00', validUntil='2026-11-30T12:00:00+09:00')


class ScheduleTests(unittest.TestCase):
    def test_kst_application_cutoff_is_not_execution_cutoff(self):
        s = schedule()
        self.assertEqual(S.state(s, NOW - timedelta(seconds=1)), 'dated')
        self.assertEqual(S.state(s, NOW), 'ended')
        self.assertEqual(S.state(s, NOW + timedelta(hours=12)), 'ended')
        a = {**row('loan'), 'verifiedSchedule': s, 'endDate': '2026-11-17'}
        self.assertEqual(status(a, NOW), '공식 안내상 해당 차수 신청 마감')
        self.assertIn('2026.11.18 17:00 KST', S.render(s, NOW))
        self.assertIn('새 신청의 연장 기한이 아닙니다', S.render(s, NOW))

    def test_invalid_expired_and_unreviewed_metadata_falls_back(self):
        s = schedule()
        self.assertIsNone(S.checked(s, S.instant(s['validUntil'])))
        self.assertIsNone(S.checked(s, S.instant(s['reviewedAt']) - timedelta(seconds=1)))
        bads = [{'sourceUrl': 'https://www.kosaf.go.kr.evil.example/'},
                {'sourceUrl': 'https://user@www.kosaf.go.kr/'},
                {'sourceUrl': 'https://www.kosaf.go.kr:8443/'},
                {'applicationEnd': '2026-11-17T18:00:00'},
                {'applicationEnd': '2026-02-30T18:00:00+09:00'},
                {'followupEnd': '2026-11-16T17:00:00+09:00'},
                {'validUntil': '2026-12-31T00:00:00+09:00'}]
        for delta in bads:
            self.assertIsNone(S.checked({**s, **delta}, NOW), delta)

    def test_only_matching_unheld_source_review_can_enrich_without_mutating(self):
        a = row('GES000000100'); original = copy.deepcopy(a)
        s = schedule()
        g = dict(benefitId=a['id'], sourceHash=material_hash(a), status='reviewed',
                 reviewedAt=s['reviewedAt'], validUntil=s['validUntil'], summary='신청과 실행 구분',
                 checks=['학기', '대출유형', '수납기한'], steps=['확인', '신청', '실행'],
                 sourceReviews=[dict(url=LOAN, title='한국장학재단 일정', note='학기별 공식 일정')],
                 applicationSchedule={k: v for k, v in s.items() if k not in ('reviewedAt','validUntil')})
        registry = {'guides': [g]}
        self.assertEqual(schedule_metadata(a, registry, NOW), s)
        self.assertIsNone(schedule_metadata({**a, 'period': '새 학기'}, registry, NOW))
        self.assertIsNone(schedule_metadata({**a, 'reviewRequired': True}, registry, NOW))
        self.assertIsNone(schedule_metadata(a, {**registry, 'holds': {a['id']: {'reason': 'verify'}}}, NOW))
        altered = copy.deepcopy(registry); altered['guides'][0]['sourceReviews'][0]['url'] = SCHOLAR
        self.assertIsNone(schedule_metadata(a, altered, NOW))
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_details(output, {a['id']: a}, {}, BASE, registry, {}, 'success', NOW)
            html = (output / 'benefits' / a['id'] / 'index.html').read_text()
            self.assertIn('공식 안내상 해당 차수 신청 마감', html)
            self.assertIn('"verifiedSchedule"', html)
            write_guides(output, BASE, {a['id']: a})
            self.assertIn('../benefits/GES000000100/', (output / 'guides/scholarships-vs-student-loan-steps-2026.html').read_text())
        self.assertEqual(a, original)

    def test_registered_guides_have_separate_scope_and_original_hashes(self):
        registry = json.loads((Path(__file__).resolve().parents[1] / 'guides.json').read_text())
        entries = [g for g in registry['guides'] if 'applicationSchedule' in g]
        self.assertEqual(len(entries), 5)
        for g in entries:
            s = g['applicationSchedule']
            self.assertIn(s['sourceUrl'], {x['url'] for x in g['sourceReviews']})
            self.assertEqual(len(g['sourceHash']), 64)
            self.assertLess(S.instant(s['applicationEnd']), S.instant(s['followupEnd']))
            if g['benefitId'].startswith('GES'):
                self.assertEqual(s['applicationEnd'], '2026-11-17T18:00:00+09:00')
            else:
                self.assertEqual(s['applicationEnd'], '2026-09-09T18:00:00+09:00')


if __name__ == '__main__':
    unittest.main()
