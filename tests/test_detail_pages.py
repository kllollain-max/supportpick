import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from detail_pages import (benefit_path, material_hash, popularity, reviewed_guide,
                          matching_blog, source_date, write_details)
from search_metadata import write_sitemap
from build import Links

BASE = 'https://kllollain-max.github.io/supportpick/'
NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)


def row(sid='TEST_1'):
    return {'id': sid, 'title': '지원금 <안내>', 'organization': '공식 기관',
            'category': '생활안정', 'region': '확인 필요', 'regionBasis': 'not_provided',
            'summary': '지원 조건을 확인하는 안내', 'target': '조건이 있는 대상',
            'support': '공식 지원 내용', 'selection': '공식 기준', 'method': '공식 창구 방문',
            'documents': '신분증', 'contact': '담당기관', 'period': '상시신청',
            'periodKind': 'ongoing', 'startDate': None, 'endDate': None,
            'officialUrl': 'https://plus.gov.kr/detail?id=' + sid,
            'applicationUrl': 'https://apply.go.kr/', 'supportType': '현금',
            'sourceConflicts': [], 'sourceDifferences': {},
            'checkedAt': '2026-11-04T10:00:00+09:00',
            'sourceUpdatedAt': {'list': '20260701101213', 'detail': '2026-07-01'},
            'rawSource': {'serviceList': {'조회수': '123'}}}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, value):
        self.parts.append(value)


class StaticDetailTests(unittest.TestCase):
    def test_core_information_is_in_initial_html_with_unique_canonical_breadcrumb_and_local_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            a, b = row(), row('TEST_2')
            b['title'] = '다른 지원금'
            result = write_details(output, {a['id']: a, b['id']: b}, {}, BASE,
                                   {'guides': []}, {'articles': []}, 'success', NOW)
            self.assertEqual(result['report']['indexableDetails'], 2)
            html = (output / benefit_path(a['id']) / 'index.html').read_text()
            self.assertIn('<h1>지원금 &lt;안내&gt;</h1>', html)
            self.assertIn('조건이 있는 대상', html)
            self.assertIn('공식 지원 내용', html)
            self.assertIn('공식 창구 방문', html)
            self.assertIn('신분증', html)
            self.assertNotIn('data.js', html)
            self.assertIn('href="' + BASE + benefit_path(a['id']) + '"', html)
            self.assertIn('href="../TEST_2/"', html)
            data = json.loads(html.split('<script type="application/ld+json">')[1].split('</script>')[0])
            self.assertEqual(data['itemListElement'][-1]['item'], BASE + benefit_path(a['id']))
            self.assertEqual([x['position'] for x in data['itemListElement']], [1, 2, 3])
            self.assertEqual(html.count('rel="canonical"'), 1)
            text = Text(); text.feed(html)
            self.assertIn('공식 지원 내용', ''.join(text.parts))

    def test_unsafe_and_colliding_ids_cannot_escape_the_output(self):
        for value in ['../bad', '..', 'a/b', '%2e', 'a?b', '__proto__', '']:
            with self.assertRaises(ValueError):
                benefit_path(value)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'path_collision'):
                write_details(Path(temp), {'A': row('A'), 'a': row('a')}, {}, BASE,
                              {}, {}, 'success', NOW)

    def test_changed_source_or_expired_or_ambiguous_editorial_is_never_presented_as_reviewed(self):
        a = row()
        g = {'benefitId': a['id'], 'sourceHash': material_hash(a), 'status': 'reviewed',
             'reviewedAt': (NOW - timedelta(days=1)).isoformat(),
             'validUntil': (NOW + timedelta(days=1)).isoformat(), 'summary': '해설',
             'checks': ['a', 'b', 'c'], 'steps': ['a', 'b', 'c'],
             'sourceReviews': [{'url': a['officialUrl'], 'note': 'source checked'}]}
        self.assertIsNotNone(reviewed_guide(a, {'guides': [g]}, NOW))
        b = copy.deepcopy(a); b['support'] = 'changed amount'
        self.assertIsNone(reviewed_guide(b, {'guides': [g]}, NOW))
        b = copy.deepcopy(a); b['checkedAt'] = '2026-11-04T20:00:00+09:00'
        self.assertIsNotNone(reviewed_guide(b, {'guides': [g]}, NOW))
        self.assertIsNone(reviewed_guide(a, {'guides': [g, g]}, NOW))
        self.assertIsNone(reviewed_guide(a, {'guides': [g]}, NOW + timedelta(days=3)))

    def test_ranking_uses_actual_counts_zero_before_missing_and_never_invents_popularity(self):
        high, zero, missing = row('HIGH'), row('ZERO'), row('MISSING')
        zero['rawSource']['serviceList']['조회수'] = '0'
        missing['rawSource']['serviceList']['조회수'] = 'unknown'
        self.assertEqual([x['id'] for x in sorted([missing, zero, high], key=popularity)],
                         ['HIGH', 'ZERO', 'MISSING'])

    def test_invalid_or_conflicting_or_duplicate_content_is_excluded_from_sitemap(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            rows = {sid: row(sid) for sid in ['GOOD', 'BAD', 'DUP1', 'DUP2']}
            rows['GOOD']['title'] = '독립 안내'
            rows['BAD']['sourceConflicts'] = ['신청기한']
            result = write_details(output, rows, {}, BASE, {}, {}, 'success', NOW)
            self.assertEqual(result['report']['indexableDetails'], 1)
            self.assertEqual(result['report']['heldDetails'], 3)
            self.assertNotIn('benefits/BAD/', [x[0] for x in result['entries']])
            html = (output / 'benefits/BAD/index.html').read_text()
            self.assertIn('content="noindex,follow"', html)
            self.assertIn('내용 확인 필요', html)

    def test_missing_previous_service_keeps_noindex_notice_and_does_not_claim_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            result = write_details(output, {}, {'OLD': row('OLD')}, BASE, {}, {}, 'failed', NOW)
            html = (output / 'benefits/OLD/index.html').read_text()
            self.assertIn('noindex,follow', html)
            self.assertIn('현재 모집·폐지 여부는 담당기관에서 확인', html)
            self.assertEqual(result['report']['retiredPages'], 1)
            self.assertFalse(any(x[0] == 'benefits/OLD/' for x in result['entries']))

    def test_failed_review_withholds_facts_and_does_not_emit_unsafe_official_link(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp);a=row()
            a['officialUrl']='javascript:alert(1)'
            a['support']='DO_NOT_PUBLISH_OBSOLETE_AMOUNT'
            result=write_details(output,{a['id']:a},{},BASE,{}, {},'success',NOW)
            html=(output/benefit_path(a['id'])/'index.html').read_text()
            self.assertIn('상세 본문 공개를 보류',html)
            self.assertNotIn('DO_NOT_PUBLISH_OBSOLETE_AMOUNT',html)
            self.assertNotIn('javascript:',html)
            self.assertEqual(result['report']['heldDetails'],1)

    def test_lastmod_does_not_use_query_time_or_nonexistent_source_date(self):
        a = row()
        self.assertEqual(source_date(a), '2026-07-01')
        a['checkedAt'] = '2026-11-04T23:00:00+09:00'
        self.assertEqual(source_date(a), '2026-07-01')
        a['sourceUpdatedAt'] = {'list': '20260230120000'}
        self.assertIsNone(source_date(a))

    def test_nested_asset_resolution_allows_internal_parent_links_but_rejects_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            page = output / 'benefits/ID/index.html'; page.parent.mkdir(parents=True); page.write_text('ok')
            (output / 'core.js').write_text('ok')
            Links(output, page).feed('<script src="../../core.js"></script>')
            with self.assertRaises(ValueError):
                Links(output, page).feed('<script src="../../../secret.js"></script>')

    def test_preview_details_remain_noindex_without_public_canonical(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp); a = row()
            result = write_details(output, {a['id']: a}, {}, None, {}, {}, 'success', NOW)
            html = (output / benefit_path(a['id']) / 'index.html').read_text()
            self.assertIn('content="noindex,nofollow"', html)
            self.assertNotIn('rel="canonical"', html)
            self.assertEqual(result['entries'], [])

    def test_blog_matching_rejects_drafts_changed_source_and_expired_links(self):
        a = row()
        key = json.dumps([a['id'], a['title'], a['organization'], a['region'], a['period'],
                          a['summary'], a['sourceUpdatedAt']['list'], a['sourceUpdatedAt']['detail']],
                         ensure_ascii=False, separators=(',', ':'))
        article = {'benefitId': a['id'], 'status': 'published', 'publicationVerified': True,
                   'url': 'https://m.blog.naver.com/bible_el/12345', 'sourceKey': key,
                   'scope': {'year': 2026, 'region': a['region'], 'round': '2026'},
                   'publicationObservedAt': '2026-11-03T10:00:00Z', 'verifiedAt': '2026-11-03T10:00:00Z',
                   'validUntil': '2026-11-10T10:00:00Z'}
        self.assertIsNotNone(matching_blog(a, {'articles': [article]}, NOW))
        for field, value in [('status', 'draft'), ('publicationVerified', False),
                             ('sourceKey', 'different'), ('url', 'https://evil.example/bible_el/12345'),
                             ('validUntil', '2026-11-01T10:00:00Z')]:
            changed = {**article, field: value}
            self.assertIsNone(matching_blog(a, {'articles': [changed]}, NOW))


if __name__ == '__main__':
    unittest.main()
