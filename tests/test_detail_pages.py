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
                          matching_blog, source_date, write_details, editorial_html, render_benefit)
from collect_full import period
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
    def test_closed_round_shows_followup_and_removes_old_application_action(self):
        current = datetime(2026, 11, 24, tzinfo=timezone.utc)
        cases = (
            ('142100000062', '2025.09.15~2025.12.31', '디지털 온누리상품권 앱'),
            ('611000000127', '2025.6.11.(수) 10:00 ~ 6. 24.(화)18:00', '마이페이지'),
            ('135200005013', '2026.05.04~2026.05.20', '자립역량교육 이수 시간'),
            ('GES000000110', '2026-2학기 신청기간 : 2026.7.1.~2026.11.17.', '전환대출의 마감은 별도였습니다'),
            ('611000019611', '2025.02.24~2025.11.30', '서울시 2026년 신청·이용 안내'),
            ('626000000633', '2026.8.18.~8.24.', '마이페이지'),
            ('628000000155', '2026년 3월 30일(월) 09:00 ~ 5월 29일(금) 16:00', '인천청년포털 사업안내'),
            ('O00388400004', '연 1회 / 2025.07.15~2025.08.25', '강원인재원 2026년 최종 선발결과'),
            ('419100000007', '2026.05.01~2026.06.19', '분기별로 모아두세요'),
            ('648000001022', '2026. 7. 23.(목) ~ 2026. 9. 6.(일)', '지원 대상 이자와 접수 기간'),
            ('641000000180', '2025.11.14.까지', '여성청소년 생리용품 전용몰'),
            ('653000000012', '2026-06-01~2026-08-31', '확정 수정 공고'),
            ('628000000748', '2026. 5. 4. ~ 5. 15.', '가입 완료 여부'),
            ('154300000012', '2026. 7. 2. ~ 8. 13.', '확정된 지급 마릿수'),
            ('370000000129', '2026.03.03~2026.06.30', '2026년 12월 1일'),
            ('328000000152', '2026. 3. 18. ~ 4. 30.', '마지막 활동과 정산 일정'),
            ('129000000008', '2025. 4. 1. ~ 2026. 3. 31.', '마감일에 등기로 보냈다면 접수와 심의 상태를 구분해 확인하세요'),
            ('305000000167', '2025.08.06~2025.09.05', '취업 교육을 찾는다면 공고 제목과 대상부터 확인하세요'),
            ('318000000132', '2026.03.03. ~ 2026.03.13.', '이미 받은 바우처를 쓴다면 결제 전에 세 가지를 확인하세요'),
            ('328000000143', '2026.04.20~2026.05.10', '이미 신청했다면 선정 안내와 정산 상태를 확인하세요'),
            ('398000000296', '2023.02.13~2023.12.20', '올해 체육복을 사기 전에 학교에 지원 여부를 확인하세요'),
            ('419100000009', '2026.03.03~2026.03.27', '신청한 회차의 결과 공고를 열어보세요'),
            ('559000000439', '2025.02.01~2025.11.30', '2026년 접수 기간과 실제 촬영 일정을 따로 확인하세요'),
            ('628000000129', '2026.  3. 3. ~ 3. 18.', '선정과 예비선정은 첨부파일을 따로 확인하세요'),
            ('641000000111', '2026.8.18. ~ 2026.9.18.', '배송이 아직 안 왔다면 선정과 배송 주소부터 확인하세요'),
            ('648000001117', '2025.11.05~2025.12.11', '모집 공고의 사업연도와 접수연도를 함께 확인하세요'),
        )
        for sid, dates, followup in cases:
            with self.subTest(sid=sid):
                archived = {**row(sid), 'period': dates, **period(dates)}
                html = render_benefit(archived, None, None, [], [], BASE, current, 'success')
                self.assertIn('id="closed-application"', html)
                self.assertIn(followup, html)
                self.assertNotIn('공식 신청 창구', html)

                new_dates = '2026.11.01~2026.12.31'
                new_round = {**archived, 'period': new_dates, **period(new_dates)}
                html = render_benefit(new_round, None, None, [], [], BASE, current, 'success')
                self.assertNotIn('id="closed-application"', html)
                self.assertIn('공식 신청 창구', html)

    def test_loan_notice_waits_until_conversion_execution_ends(self):
        dates = '2026-2학기 신청기간 : 2026.7.1.~2026.11.17.'
        loan = {**row('GES000000110'), 'period': dates, **period(dates)}
        current = datetime(2026, 11, 19, 6, tzinfo=timezone.utc)
        html = render_benefit(loan, None, None, [], [], BASE, current, 'success')
        self.assertNotIn('id="closed-application"', html)
        self.assertIn('기존 신청 링크 · 현재 접수 여부 확인', html)

    def test_past_listed_period_marks_existing_link_and_keeps_its_destination(self):
        dates = '2026.10.01~2026.11.03'
        expired = {**row(), 'period': dates, **period(dates)}
        html = render_benefit(expired, None, None, [], [], BASE, NOW, 'success')
        self.assertNotIn('공식 신청 창구', html)
        self.assertIn('href="https://apply.go.kr/" target="_blank" rel="noopener noreferrer">기존 신청 링크 · 현재 접수 여부 확인', html)

    def test_api_only_detail_does_not_manufacture_a_repeated_preparation_essay(self):
        a=row()
        self.assertEqual(editorial_html(a,None),'')
        a['documents']=''
        text=editorial_html(a,None)
        self.assertIn('구비서류 항목이 제공되지 않았습니다',text)
        self.assertNotIn('지원금픽 자체 해설',text)
        self.assertNotIn('의 소관 지역 표기는',text)

    def test_confirmed_outdated_source_links_to_current_explanation_without_republishing_old_facts(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp); a=row('135200000120')
            a['summary']='OUTDATED_SUMMARY';a['support']='OUTDATED_PAYMENT'
            result=write_details(output,{a['id']:a},{},BASE,
                                 {'holds':{a['id']:{'reason':'Official age and regional amount changed',
                                                   'url':'https://www.mohw.go.kr/menu.es?mid=a10711030100'}}},
                                 {},'success',NOW)
            html=(output/benefit_path(a['id'])/'index.html').read_text()
            self.assertNotIn('OUTDATED_SUMMARY',html)
            self.assertNotIn('OUTDATED_PAYMENT',html)
            self.assertIn('../../guides/child-allowance-2026.html',html)
            self.assertEqual(result['report']['indexableDetails'],0)
            self.assertEqual(a['support'],'OUTDATED_PAYMENT')

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
