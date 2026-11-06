"""No-network regressions for draft/source/media binding before a Threads POST."""
import copy
import hashlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_writer as w

NOW = datetime(2026, 11, 6, 12, 15, tzinfo=w.KST)
SLOT = NOW.replace(minute=0).isoformat()
IMAGE = ('https://raw.githubusercontent.com/kllollain-max/supportpick/'
         'main/social/images/benefit-guide-1.png')
POST = ('난방비가 부담스러운 춘천 가구라면\n'
        '생활지원 바우처의 거주·소득 조건부터 확인해 보세요.\n\n'
        '춘천시에 주민등록을 두고 소득 기준을 충족하는 가구가 대상이에요. '
        '선정된 가구에 연 1회 최대 10만원의 난방 바우처를 지원해요. '
        '현금 지급이 아니며 지정된 난방비 결제에 사용할 수 있어요.\n\n'
        '상시 신청을 받지만 자격 심사 후 지원 여부가 정해져요. '
        '거주지 주민센터에서 신청 조건과 절차를 확인할 수 있어요.\n\n' + w.CTA)


def source_row(sid='benefit1'):
    return {
        'id': sid, 'title': '춘천 생활지원 바우처', 'organization': '춘천시',
        'summary': '선정된 저소득 가구의 난방비 지원',
        'target': '춘천시 주민등록 가구 중 소득 기준 충족 가구',
        'support': '선정된 가구에 연 1회 최대 10만원의 난방 바우처 지원',
        'supportType': '이용권', 'supportTypes': ['이용권'],
        'method': '거주지 주민센터 방문 신청', 'selection': '자격 심사 후 선정',
        'documents': '공식 안내에서 구비서류 확인', 'region': '강원',
        'regionBasis': 'agency_jurisdiction', 'regionEvidence': '춘천시',
        'period': '상시신청', 'periodKind': 'ongoing', 'startDate': None, 'endDate': None,
        'category': '생활안정', 'officialUrl': 'https://plus.gov.kr/benefit/benefit1',
        'sourceConflicts': [], 'checkedAt': NOW.isoformat(), 'generation': 'source-1',
        'rawSource': {
            'serviceList': {'서비스ID': sid, '서비스명': '춘천 생활지원 바우처', '조회수': 5000},
            'serviceDetail': {'서비스ID': sid, '지원내용': '연 1회 최대 10만원', '신청기한': '상시신청'},
            'supportConditions': {'서비스ID': sid, '소득': '조건 충족 가구'},
        },
    }


def ready_queue(row, prompt_path, now=NOW, slot=SLOT, pattern='P5', image=None, asset_bytes=None):
    prepared = now - timedelta(minutes=5)
    reviewed = now - timedelta(minutes=10)
    evidence = [{
        'source_id': row['id'], 'source_ref': row['officialUrl'],
        'access_method': 'PROVIDED_OFFICIAL_TEXT', 'verified_at': reviewed.isoformat(),
        'claims_supported': [row['target'], row.get('support') or row['summary'], row['period'], row['method']],
    }]
    if image:
        evidence.append({
            'source_id': 'benefit-guide-1', 'source_ref': image,
            'access_method': 'UPSTREAM_VERIFIED', 'verified_at': reviewed.isoformat(),
            'claims_supported': ['지원금픽 일반 혜택 안내 이미지이며 특정 금액이나 기한을 표시하지 않음'],
        })
    writer = {
        'schema_version': w.WRITER_SCHEMA, 'status': 'READY', 'selected_program_id': row['id'],
        'post_text': POST, 'draft_text': None, 'reply_texts': [],
        'media': {'turn': 'IMAGE' if image else 'TEXT', 'asset_id': image,
                  'check': 'MATCHED' if image else 'NOT_REQUIRED', 'image_copy': None,
                  'alt_text': '지원금픽 생활혜택 안내 카드' if image else None},
        'review': {
            'planned_at': slot, 'application_status': 'ALWAYS', 'reader': '춘천 저소득 가구',
            'central_message': '거주·소득 조건을 확인하고 난방 바우처를 준비할 수 있어요.',
            'pattern': pattern, 'selection_reason': '검증 가능한 혜택 중 보조금24 누적 조회수가 높은 후보',
            'interest_basis': 'OBSERVED_METRICS', 'duplicate_check': 'CHECKED', 'evidence': evidence,
            'checks': {'facts': 'PASS', 'current_status': 'PASS', 'eligibility_and_units': 'PASS',
                       'cta_and_no_links': 'PASS', 'length': 'PASS',
                       'media': 'PASS' if image else 'NOT_REQUIRED'},
            'char_count': len(POST), 'count_method': w.COUNT_METHOD,
            'missing_info': [], 'hold_reasons': [], 'warnings': [],
        },
        'next_history_record': {'program_id': row['id'], 'notice_version': None, 'pattern': pattern,
                                'opening': w.opening(POST), 'structure': '생활 상황 → 자격 → 바우처와 신청 조건',
                                'media_turn': 'IMAGE' if image else 'TEXT'},
    }
    entry = {'slot': slot, 'benefit_id': row['id'], 'source_fingerprint': w.source_fingerprint(row),
             'source_generation': 'source-1', 'prepared_at': prepared.isoformat(),
             'expires_at': (prepared + timedelta(hours=6)).isoformat(), 'writer': writer}
    if image:
        entry['asset_sha256'] = hashlib.sha256(asset_bytes or b'reviewed asset').hexdigest()
    return {'schema_version': w.QUEUE_SCHEMA, 'brand': 'supportpick', 'username': 'hid_1004',
            'prompt_sha256': w.prompt_sha256(prompt_path), 'entries': [entry]}


class WriterValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prompt = self.root / 'prompt.txt'
        self.prompt.write_text('지원금픽 master prompt test fixture', encoding='utf-8')
        self.asset = self.root / 'social/images/benefit-guide-1.png'
        self.asset.parent.mkdir(parents=True)
        self.asset.write_bytes(b'reviewed asset')
        self.root_patch = patch.object(w, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.row = source_row()
        self.queue = ready_queue(self.row, self.prompt)

    @property
    def entry(self):
        return self.queue['entries'][0]

    @property
    def writer(self):
        return self.entry['writer']

    def validate(self, records=None, image=None, now=NOW, eligible=None, slot=SLOT):
        return w.validate_ready_entry(self.queue, [self.row] if eligible is None else eligible,
                                      records or [], now, slot, image, self.prompt)

    def text(self, new):
        self.writer['post_text'] = new
        self.writer['review']['char_count'] = len(new)
        self.writer['next_history_record']['opening'] = w.opening(new)

    def sync_fingerprint(self):
        self.entry['source_fingerprint'] = w.source_fingerprint(self.row)

    def history(self, pattern='P1', day=0, hour=8, text='돌봄 서비스 신청을 준비 중인가요?'):
        return [{'benefit_id': 'earlier', 'slot': (NOW + timedelta(days=day)).replace(hour=hour, minute=0).isoformat(),
                 'status': 'published', 'writer': {'pattern': pattern}, 'texts': [text]}]

    def add_future(self, pattern='P6', hour=16, sid='future', text='신청 전 준비할 순서가 있어요.'):
        other_row = source_row(sid)
        slot = NOW.replace(hour=hour, minute=0).isoformat()
        other = ready_queue(other_row, self.prompt, slot=slot, pattern=pattern)['entries'][0]
        other['writer']['post_text'] = text + '\n\n' + w.CTA
        other['writer']['review']['char_count'] = len(other['writer']['post_text'])
        other['writer']['next_history_record']['opening'] = text
        self.queue['entries'].append(other)
        return other

    def test_ready_text_is_returned_verbatim_and_bound_to_prompt_and_source(self):
        before = copy.deepcopy(self.queue)
        row, writer, meta = self.validate()
        self.assertIs(row, self.row)
        self.assertIs(writer, self.writer)
        self.assertEqual(writer['post_text'], POST)
        self.assertEqual(meta['pattern'], 'P5')
        self.assertEqual(meta['prompt_sha256'], w.prompt_sha256(self.prompt))
        self.assertEqual(meta['source_fingerprint'], w.source_fingerprint(self.row))
        self.assertEqual(meta['char_count'], len(POST))
        self.assertEqual(self.queue, before)

    def test_status_never_promotes_draft_hold_or_skip_to_post(self):
        for status in ('DRAFT', 'HOLD', 'SKIP', None):
            with self.subTest(status=status):
                self.writer['status'] = status
                with self.assertRaisesRegex(ValueError, 'writer_not_ready'):
                    self.validate()

    def test_wrong_schema_brand_account_or_prompt_fails_closed(self):
        for key, value in [('schema_version', 'careerpick.queue.v1'), ('brand', 'careerpick'),
                           ('username', 'hid_119'), ('prompt_sha256', 'wrong')]:
            with self.subTest(key=key):
                original = self.queue[key]
                self.queue[key] = value
                with self.assertRaisesRegex(ValueError, 'writer_queue_invalid|writer_prompt_hash_mismatch'):
                    self.validate()
                self.queue[key] = original
        self.prompt.write_text('changed actual master prompt', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'writer_prompt_hash_mismatch'):
            self.validate()

    def test_missing_prompt_is_not_treated_as_empty_approval(self):
        self.prompt.unlink()
        with self.assertRaisesRegex(ValueError, 'writer_master_prompt_unavailable'):
            self.validate()

    def test_missing_and_duplicate_slots_are_not_selected_heuristically(self):
        original = copy.deepcopy(self.entry)
        self.queue['entries'] = []
        with self.assertRaisesRegex(ValueError, 'writer_ready_slot_missing'):
            self.validate()
        self.queue['entries'] = [original, copy.deepcopy(original)]
        self.queue['entries'][1]['slot'] = '2026-11-06T03:00:00Z'
        with self.assertRaisesRegex(ValueError, 'writer_duplicate_queue_slot'):
            self.validate()

    def test_equivalent_timezone_slot_is_same_instant(self):
        self.entry['slot'] = '2026-11-06T03:00:00Z'
        self.writer['review']['planned_at'] = '2026-11-06T03:00:00Z'
        self.validate()

    def test_stale_future_and_oversized_lifetime_drafts_are_held(self):
        original = copy.deepcopy(self.entry)
        changes = [
            {'expires_at': NOW.isoformat()},
            {'prepared_at': (NOW + timedelta(seconds=1)).isoformat()},
            {'expires_at': (NOW + timedelta(days=2)).isoformat()},
            {'prepared_at': '2026-11-06T12:00:00'},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.queue['entries'][0] = copy.deepcopy(original)
                self.entry.update(change)
                with self.assertRaisesRegex(ValueError, 'writer_draft_expired_or_future|writer_timestamp_invalid'):
                    self.validate()

    def test_source_change_requires_new_review_but_refresh_and_views_do_not(self):
        original_hash = w.source_fingerprint(self.row)
        self.row['generation'] = 'next-source'
        self.row['checkedAt'] = NOW.isoformat()
        self.row['rawSource']['serviceList']['조회수'] = 6000
        self.row['rawSource']['serviceDetail']['수정일시'] = '20261106120000'
        self.assertEqual(w.source_fingerprint(self.row), original_hash)
        self.validate()
        self.row['support'] = '매월 10만원 지원'
        with self.assertRaisesRegex(ValueError, 'writer_source_changed_requires_review'):
            self.validate()

    def test_raw_conditions_and_factual_listing_changes_invalidate_review(self):
        for endpoint, field in [('serviceDetail', '지원내용'), ('supportConditions', '소득'),
                                ('serviceList', '서비스명')]:
            with self.subTest(endpoint=endpoint):
                original = copy.deepcopy(self.row)
                self.row['rawSource'][endpoint][field] = 'changed condition'
                with self.assertRaisesRegex(ValueError, 'writer_source_changed_requires_review'):
                    self.validate()
                self.row = original

    def test_candidate_disappearance_or_ambiguous_id_is_not_reselected(self):
        for eligible in ([], [copy.deepcopy(self.row), copy.deepcopy(self.row)]):
            with self.subTest(count=len(eligible)):
                with self.assertRaisesRegex(ValueError, 'writer_candidate_no_longer_eligible'):
                    self.validate(eligible=eligible)
        self.writer['selected_program_id'] = 'different'
        with self.assertRaisesRegex(ValueError, 'writer_program_id_mismatch'):
            self.validate()

    def test_existing_benefit_or_slot_cannot_be_reused(self):
        records = self.history()
        records[0]['benefit_id'] = self.row['id']
        with self.assertRaisesRegex(ValueError, 'writer_benefit_already_reserved'):
            self.validate(records=records)
        records[0]['benefit_id'] = 'other'
        records[0]['slot'] = SLOT
        with self.assertRaisesRegex(ValueError, 'writer_slot_already_reserved'):
            self.validate(records=records)

    def test_same_benefit_in_two_future_slots_is_rejected(self):
        self.add_future(sid=self.row['id'])
        with self.assertRaisesRegex(ValueError, 'writer_benefit_queued_twice'):
            self.validate()

    def test_exact_last_line_single_cta_is_required(self):
        for text in [POST.replace(w.CTA, ''), POST + '\n끝', w.CTA + '\n' + POST, POST + '\n']:
            with self.subTest(text=text[-20:]):
                self.text(text)
                with self.assertRaisesRegex(ValueError, 'writer_exact_final_cta_required|writer_post_text_required'):
                    self.validate()

    def test_length_is_measured_including_cta_spaces_and_newlines(self):
        self.writer['review']['char_count'] -= 1
        with self.assertRaisesRegex(ValueError, 'writer_character_count_mismatch'):
            self.validate()
        self.text('가' * 500 + '\n' + w.CTA)
        with self.assertRaisesRegex(ValueError, 'writer_post_over_500_characters'):
            self.validate()

    def test_no_reply_or_draft_text_is_accidentally_published(self):
        self.writer['reply_texts'] = ['추가 조건']
        with self.assertRaisesRegex(ValueError, 'writer_single_final_post_required'):
            self.validate()
        self.writer['reply_texts'] = []
        self.writer['draft_text'] = 'still a draft'
        with self.assertRaisesRegex(ValueError, 'writer_single_final_post_required'):
            self.validate()

    def test_links_and_common_obfuscations_are_rejected_without_rewriting(self):
        addresses = ['https://plus.gov.kr', 'www.gov.kr', 'plus.gov.kr/path', 't.co/x',
                     'plus . gov . kr', 'p l u s . g o v . k r', 'plus 점 gov 점 kr',
                     'plus[dot]gov[dot]kr', 'plus(dot)gov(dot)kr', '네이버 점 컴', '네이버 점 com',
                     'https://g\u200bov.kr', 'ｈｔｔｐｓ：／／gov.kr', 'hxxps://gov.kr']
        for address in addresses:
            with self.subTest(address=address):
                text = '공식 안내 ' + address + '\n\n' + w.CTA
                self.text(text)
                with self.assertRaisesRegex(ValueError, 'writer_link_free_publication_required'):
                    self.validate()
                self.assertEqual(self.writer['post_text'], text)

    def test_numeric_dates_and_units_are_not_mistaken_for_web_addresses(self):
        self.text('신청기간은 2026.11.6.까지예요. 가구당 연 최대 3.5만원이에요.\n\n' + w.CTA)
        self.validate()

    def test_extra_engagement_hashtags_and_guarantees_are_rejected(self):
        cases = [('조건을 댓글로 알려주세요.', 'writer_additional_engagement_request'),
                 ('주변에 공유해주세요.', 'writer_additional_engagement_request'),
                 ('팔로우하고 혜택 챙겨보세요.', 'writer_additional_engagement_request'),
                 ('#지원금픽 안내예요.', 'writer_hashtags_disabled'),
                 ('신청만 하면 입금돼요.', 'writer_unsupported_guarantee'),
                 ('무조건 받는 지원금이에요.', 'writer_unsupported_guarantee')]
        for text, reason in cases:
            with self.subTest(text=text):
                self.text(text + '\n\n' + w.CTA)
                with self.assertRaisesRegex(ValueError, reason):
                    self.validate()

    def test_required_reviews_cannot_be_not_checked(self):
        for key in ('facts', 'current_status', 'eligibility_and_units', 'cta_and_no_links', 'length'):
            with self.subTest(key=key):
                self.writer['review']['checks'][key] = 'NOT_CHECKED'
                with self.assertRaisesRegex(ValueError, 'writer_required_check_not_passed'):
                    self.validate()
                self.writer['review']['checks'][key] = 'PASS'
        self.writer['review']['hold_reasons'] = ['current status needs verification']
        with self.assertRaisesRegex(ValueError, 'writer_unresolved_review_items'):
            self.validate()

    def test_source_evidence_is_required_and_bound_to_selected_program(self):
        original = copy.deepcopy(self.writer['review']['evidence'])
        self.writer['review']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'writer_evidence_required'):
            self.validate()
        self.writer['review']['evidence'] = original
        evidence = self.writer['review']['evidence'][0]
        evidence['source_ref'] = 'https://unrelated.example.test'
        with self.assertRaisesRegex(ValueError, 'writer_source_evidence_not_bound'):
            self.validate()
        evidence['source_ref'] = self.row['officialUrl']
        evidence['access_method'] = 'UNVERIFIED'
        with self.assertRaisesRegex(ValueError, 'writer_evidence_unverified'):
            self.validate()

    def test_named_provided_official_text_can_be_bound_without_inventing_page_open(self):
        evidence = self.writer['review']['evidence'][0]
        evidence['source_ref'] = '보조금24 serviceDetail의 해당 서비스 공식 원문'
        self.validate()
        self.assertEqual(evidence['access_method'], 'PROVIDED_OFFICIAL_TEXT')

    def test_malformed_evidence_type_has_controlled_failure(self):
        self.writer['review']['evidence'][0]['access_method'] = ['OPENED_OFFICIAL']
        with self.assertRaisesRegex(ValueError, '^writer_evidence_unverified$'):
            self.validate()

    def test_separate_opened_official_notice_can_clarify_current_status(self):
        self.row['period'] = '기관에 확인'
        self.row['periodKind'] = 'needs_check'
        self.sync_fingerprint()
        evidence = self.writer['review']['evidence'][0]
        evidence['access_method'] = 'OPENED_OFFICIAL'
        evidence['source_ref'] = 'https://www.chuncheon.go.kr/benefits/current-notice'
        evidence['claims_supported'].append('해당 지원사업은 현재 상시 신청이 가능함')
        self.validate()
        evidence['source_id'] = 'different-program'
        with self.assertRaisesRegex(ValueError, 'writer_source_evidence_not_bound'):
            self.validate()

    def test_plain_http_or_credentialed_notice_cannot_be_evidence(self):
        evidence = self.writer['review']['evidence'][0]
        evidence['access_method'] = 'OPENED_OFFICIAL'
        for url in ['http://www.chuncheon.go.kr/notice', 'https://user:password@www.chuncheon.go.kr/notice']:
            with self.subTest(url=url):
                evidence['source_ref'] = url
                with self.assertRaisesRegex(ValueError, 'writer_evidence_unverified'):
                    self.validate()

    def test_stale_future_and_empty_claim_evidence_are_rejected(self):
        evidence = self.writer['review']['evidence'][0]
        for when in [NOW - timedelta(hours=25), NOW + timedelta(seconds=1), NOW]:
            with self.subTest(when=when):
                evidence['verified_at'] = when.isoformat()
                with self.assertRaisesRegex(ValueError, 'writer_evidence_stale_or_future'):
                    self.validate()
        evidence['verified_at'] = (NOW - timedelta(minutes=10)).isoformat()
        evidence['claims_supported'] = []
        with self.assertRaisesRegex(ValueError, 'writer_evidence_unverified'):
            self.validate()

    def test_unknown_closed_and_suspended_status_are_never_ready(self):
        for status in ('UNKNOWN', 'CLOSED', 'SUSPENDED'):
            with self.subTest(status=status):
                self.writer['review']['application_status'] = status
                with self.assertRaisesRegex(ValueError, 'writer_application_not_publishable'):
                    self.validate()

    def test_known_dates_are_rechecked_at_actual_publication_time(self):
        self.row['endDate'] = '2026-11-06T12:05:00+09:00'
        self.sync_fingerprint()
        with self.assertRaisesRegex(ValueError, 'writer_application_closed_before_publication'):
            self.validate()
        self.row['endDate'] = '2026-11-06'
        self.sync_fingerprint()
        self.validate()  # A source supplying only a date does not invent 18:00.
        self.row['endDate'] = '2026-11-05'
        self.sync_fingerprint()
        with self.assertRaisesRegex(ValueError, 'writer_application_closed_before_publication'):
            self.validate()

    def test_future_start_cannot_claim_current_application(self):
        self.row['startDate'] = '2026-11-07'
        self.sync_fingerprint()
        with self.assertRaisesRegex(ValueError, 'writer_application_not_open_yet'):
            self.validate()
        self.writer['review']['application_status'] = 'UPCOMING'
        self.text('11월 7일 접수가 시작돼요. 준비 조건을 확인해 보세요.\n\n' + w.CTA)
        self.validate()
        self.text('11월 7일 시작해요. 지금 신청하세요.\n\n' + w.CTA)
        with self.assertRaisesRegex(ValueError, 'writer_upcoming_claims_open'):
            self.validate()

    def test_undetermined_period_cannot_be_misclassified_from_pass_flags(self):
        self.row['period'] = '접수기관 별 상이'
        self.row['periodKind'] = 'needs_check'
        self.sync_fingerprint()
        with self.assertRaisesRegex(ValueError, 'writer_always_status_needs_evidence'):
            self.validate()
        self.writer['review']['application_status'] = 'OPEN'
        with self.assertRaisesRegex(ValueError, 'writer_open_status_needs_evidence'):
            self.validate()
        evidence = self.writer['review']['evidence'][0]
        evidence['access_method'] = 'OPENED_OFFICIAL'
        evidence['claims_supported'].append('게시 시점에 해당 사업의 신청 가능 상태를 공식 페이지에서 확인')
        self.validate()

    def test_same_day_pattern_is_distinct_from_published_and_queued_posts(self):
        with self.assertRaisesRegex(ValueError, 'writer_same_day_pattern_repeated'):
            self.validate(records=self.history(pattern='P5'))
        self.validate(records=self.history(pattern='P5', day=-1))
        self.add_future(pattern='P5')
        with self.assertRaisesRegex(ValueError, 'writer_same_day_pattern_repeated'):
            self.validate()

    def test_bad_pattern_names_cannot_evade_daily_diversity(self):
        for value in ('P5 체크', 'p5', 'checklist', ['P5']):
            with self.subTest(value=value):
                self.writer['review']['pattern'] = value
                with self.assertRaisesRegex(ValueError, 'writer_pattern_required'):
                    self.validate()

    def test_other_queued_slots_must_also_have_different_patterns(self):
        self.add_future(pattern='P6', hour=16, sid='future1')
        self.add_future(pattern='P6', hour=20, sid='future2', text='다음 단계 준비를 살펴보세요.')
        with self.assertRaisesRegex(ValueError, 'writer_same_day_pattern_repeated'):
            self.validate()

    def test_repeated_opening_is_rejected_even_with_new_pattern_and_emoji(self):
        repeated = '📌 ' + w.opening(POST).replace(' ', '  ') + '!'
        with self.assertRaisesRegex(ValueError, 'writer_opening_repeated'):
            self.validate(records=self.history(text=repeated))
        self.add_future(text=w.opening(POST))
        with self.assertRaisesRegex(ValueError, 'writer_opening_repeated'):
            self.validate()

    def test_legacy_history_is_readable_without_inventing_its_pattern(self):
        records = self.history()
        records[0].pop('writer')
        self.validate(records=records)
        self.writer['review']['duplicate_check'] = 'NO_HISTORY'
        with self.assertRaisesRegex(ValueError, 'writer_available_history_not_reviewed'):
            self.validate(records=records)

    def test_history_proposal_matches_actual_text_pattern_and_media(self):
        original = copy.deepcopy(self.writer['next_history_record'])
        for key, value in [('program_id', 'wrong'), ('pattern', 'P1'), ('media_turn', 'IMAGE'),
                           ('opening', 'an unposted opening'), ('structure', '')]:
            with self.subTest(key=key):
                self.writer['next_history_record'] = {**original, key: value}
                with self.assertRaisesRegex(ValueError, 'writer_next_history_mismatch'):
                    self.validate()

    def test_verified_image_is_bound_to_actual_bytes_and_not_only_matched_flag(self):
        self.queue = ready_queue(self.row, self.prompt, image=IMAGE)
        _, _, meta = self.validate(image=IMAGE)
        self.assertEqual(meta['asset_sha256'], hashlib.sha256(b'reviewed asset').hexdigest())
        self.asset.write_bytes(b'different image at same URL')
        with self.assertRaisesRegex(ValueError, 'writer_image_asset_hash_mismatch'):
            self.validate(image=IMAGE)

    def test_image_without_asset_review_is_held_and_not_switched_to_text(self):
        self.queue = ready_queue(self.row, self.prompt, image=IMAGE)
        self.writer['review']['evidence'].pop()
        with self.assertRaisesRegex(ValueError, 'writer_image_review_evidence_required'):
            self.validate(image=IMAGE)
        with self.assertRaisesRegex(ValueError, 'writer_text_media_mismatch'):
            self.validate(image=None)

    def test_wrong_image_url_and_asset_hash_are_rejected(self):
        self.queue = ready_queue(self.row, self.prompt, image=IMAGE)
        self.writer['media']['asset_id'] = IMAGE.replace('supportpick', 'careerpick')
        with self.assertRaisesRegex(ValueError, 'writer_image_media_mismatch'):
            self.validate(image=IMAGE)
        self.writer['media']['asset_id'] = IMAGE
        self.entry.pop('asset_sha256')
        with self.assertRaisesRegex(ValueError, 'writer_image_asset_hash_mismatch'):
            self.validate(image=IMAGE)

    def test_text_turn_cannot_depend_on_missing_image(self):
        self.text('이미지에 정리했어요. 조건을 살펴보세요.\n\n' + w.CTA)
        with self.assertRaisesRegex(ValueError, 'writer_text_depends_on_image'):
            self.validate()

    def test_observed_interest_requires_actual_metric(self):
        self.row['rawSource']['serviceList']['조회수'] = 'unknown'
        self.sync_fingerprint()
        with self.assertRaisesRegex(ValueError, 'writer_observed_metric_missing'):
            self.validate()
        self.writer['review']['interest_basis'] = 'ESTIMATED'
        self.validate()

    def test_future_and_missed_slot_cannot_be_published_with_valid_content(self):
        for now in (NOW.replace(hour=11), NOW.replace(hour=14, minute=0)):
            with self.subTest(now=now):
                with self.assertRaisesRegex(ValueError, 'writer_outside_publication_slot'):
                    self.validate(now=now)


if __name__ == '__main__':
    unittest.main()
