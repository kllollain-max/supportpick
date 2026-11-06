import copy
import json
import sys
import unittest
from urllib.error import HTTPError
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_threads as t
import supportpick_writer as w

NOW = datetime(2026, 11, 4, 8, 15, tzinfo=t.KST)

def empty():
    return {'version': 1, 'brand': 'supportpick', 'username': 'hid_1004', 'records': []}

def urls_for_tests():
    return json.loads((t.ROOT / 'social/assets.json').read_text())['_rotation']

def feed():
    return {'isSample': False, 'updatedAt': NOW.isoformat(), 'generation': 'test', 'items': [{
        'id': 'benefit1', 'title': '생활지원', 'organization': '공공기관', 'summary': '생활 지원 안내',
        'target': '세부 소득·거주 조건 충족 가구', 'method': '공식 창구에서 안내 확인',
        'period': '원문 확인', 'category': '생활안정', 'checkedAt': NOW.isoformat(),
        'officialUrl': 'https://plus.gov.kr/benefit', 'sourceConflicts': []}]}


def reviewed_queue(data, state, now=NOW, cron='0 23 * * *', assets=None):
    queue = {'schema_version': w.QUEUE_SCHEMA, 'brand': 'supportpick', 'username': t.USERNAME,
             'prompt_sha256': w.prompt_sha256(), 'entries': []}
    rows = t.candidates(data, state, now)
    if not rows:
        return queue
    row = rows[0]; slot = t.current_slot(now, cron)
    image = t.select_image(row, state['records'], assets or {})
    used = {r.get('writer', {}).get('pattern') for r in state['records'] if t.stamp(r['slot']).date() == now.date()}
    pattern = next(p for p in ['P1', 'P5', 'P6', 'P8', 'P3', 'P4', 'P9'] if p not in used)
    text = row['title'] + ' 조건을 살펴봐요 (' + row['id'] + ').\n\n' + row['summary'] + '\n대상과 신청 조건을 함께 확인할 수 있어요.\n\n' + t.CTA
    prepared = now - timedelta(minutes=1)
    evidence = [{'source_id': row['id'], 'source_ref': row['officialUrl'],
                 'access_method': 'OPENED_OFFICIAL', 'verified_at': prepared.isoformat(),
                 'claims_supported': ['합성 검사 원문의 대상·상시 신청 가능·지원 내용 대조']}]
    if image:
        evidence.append({'source_id': 'image-review', 'source_ref': image,
                         'access_method': 'UPSTREAM_VERIFIED', 'verified_at': prepared.isoformat(),
                         'claims_supported': ['합성 검수: 실제 체크아웃 이미지 해시와 브랜드 문구 일치']})
    writer = {'schema_version': w.WRITER_SCHEMA, 'status': 'READY', 'selected_program_id': row['id'],
              'post_text': text, 'draft_text': None, 'reply_texts': [],
              'media': {'turn': 'IMAGE' if image else 'TEXT', 'asset_id': image,
                        'check': 'MATCHED' if image else 'NOT_REQUIRED',
                        'image_copy': None, 'alt_text': '지원금픽 브랜드 안내 그림' if image else None},
              'review': {'planned_at': slot, 'application_status': 'ALWAYS', 'reader': '합성 검사 대상',
                         'central_message': row['summary'], 'pattern': pattern, 'selection_reason': '공식 누적 조회수 우선',
                         'interest_basis': 'OBSERVED_METRICS' if t.popularity_views(row) is not None else 'ESTIMATED',
                         'duplicate_check': 'CHECKED', 'evidence': evidence,
                         'checks': {**{k: 'PASS' for k in ('facts','current_status','eligibility_and_units','cta_and_no_links','length')},
                                    'media': 'PASS' if image else 'NOT_REQUIRED'},
                         'char_count': len(text), 'count_method': w.COUNT_METHOD,
                         'missing_info': [], 'hold_reasons': [], 'warnings': []},
              'next_history_record': {'program_id': row['id'], 'pattern': pattern,
                                      'media_turn': 'IMAGE' if image else 'TEXT',
                                      'opening': w.opening(text), 'structure': '조건 안내 후 핵심 설명'}}
    entry = {'slot': slot, 'benefit_id': row['id'], 'source_fingerprint': w.source_fingerprint(row),
             'source_generation': data['generation'], 'prepared_at': prepared.isoformat(),
             'expires_at': (prepared + timedelta(hours=24)).isoformat(), 'writer': writer}
    if image:
        entry['asset_sha256'] = t.hashlib.sha256((t.ROOT / 'social/images' / image.rsplit('/',1)[1]).read_bytes()).hexdigest()
    queue['entries'].append(entry)
    return queue

class Store:
    def __init__(self):
        self.state, self.version, self.fail_save = empty(), 1, None
    def read(self):
        return str(self.version), copy.deepcopy(self.state)
    def save(self, sha, state):
        if self.fail_save == self.version or sha != str(self.version):
            raise RuntimeError('CAS failed')
        t.validate_ledger(state)
        self.state = copy.deepcopy(state)
        self.version += 1
        return str(self.version)

class API:
    def __init__(self, store):
        self.store, self.calls, self.fail_at, self.verify_fail = store, [], None, False
    def verify_account(self, uid):
        if uid != '1004':
            raise ValueError('wrong account')
    def post(self, text, parent=None, image=None):
        # Verify every API mutation was preceded by a durable sending stage.
        assert self.store.state['records'][-1]['stage'].endswith('_sending')
        self.calls.append((text, parent, image))
        if len(self.calls) == self.fail_at:
            raise RuntimeError('ambiguous request')
        return str(1000 + len(self.calls))
    def verify(self, pid, text):
        if self.verify_fail:
            raise RuntimeError('verify failed')
        return 'https://www.threads.com/@hid_1004/post/' + pid

class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(); self.api = API(self.store)
    def run_publish(self, data=None, now=NOW, assets=None):
        data = data or feed()
        return t.publish(data, self.store, self.api, now, '0 23 * * *', '123', '1004', assets,
                         reviewed_queue(data, self.store.state, now, assets=assets))
    def run_legacy(self):
        # Existing reservations are fixtures, never created by the new publisher.
        row = feed()['items'][0]; texts = list(t.compose(row))
        record = {'benefit_id': row['id'], 'slot': t.current_slot(NOW, '0 23 * * *'),
                  'run_id': '123', 'status': 'pending', 'texts': texts,
                  'checked_at': row['checkedAt'], 'image_url': None,
                  'content_hash': t.hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest()}
        state = copy.deepcopy(self.store.state); state['records'].append(record)
        sha = self.store.save(str(self.store.version), state)
        return t.complete_record(self.store, self.api, sha, state, record, NOW)
    def test_complete_single_reviewed_post_without_replies(self):
        result = self.run_publish()
        self.assertTrue(result['published'])
        self.assertEqual([x[1] for x in self.api.calls], [None])
        self.assertEqual(self.store.state['records'][0]['status'], 'published')
        self.assertTrue(all(x[0].endswith(t.CTA) for x in self.api.calls))
        self.assertEqual(result['replies'], 0)
        self.assertEqual(self.store.state['records'][0]['writer_schema'], w.WRITER_SCHEMA)
    def test_same_slot_cannot_post_twice(self):
        self.run_publish()
        with self.assertRaisesRegex(RuntimeError, 'slot_already_reserved'): self.run_publish()
        self.assertEqual(len(self.api.calls), 1)
    def test_post_ambiguity_blocks_future_slots(self):
        self.api.fail_at = 1
        with self.assertRaises(RuntimeError): self.run_publish()
        with self.assertRaisesRegex(RuntimeError, 'unresolved'): self.run_publish(now=NOW + timedelta(days=1))
        self.assertEqual(len(self.api.calls), 1)
    def test_reply_ambiguity_preserves_main_receipt(self):
        self.api.fail_at = 2
        with self.assertRaises(RuntimeError): self.run_legacy()
        r = self.store.state['records'][0]
        self.assertEqual(r['main_id'], '1001'); self.assertEqual(r['status'], 'pending')
        with self.assertRaisesRegex(RuntimeError, 'unresolved'): self.run_publish(now=NOW + timedelta(days=1))
    def test_reservation_CAS_failure_prevents_api_mutation(self):
        self.store.fail_save = 1
        with self.assertRaises(RuntimeError): self.run_publish()
        self.assertEqual(self.api.calls, [])
    def test_receipt_persistence_failure_blocks_retry(self):
        self.store.fail_save = 3
        with self.assertRaises(RuntimeError): self.run_publish()
        self.assertEqual(len(self.api.calls), 1)
        self.assertEqual(self.store.state['records'][0]['stage'], 'main_id_sending')
        with self.assertRaisesRegex(RuntimeError, 'unresolved'): self.run_publish(now=NOW + timedelta(days=1))
    def test_failed_remote_verification_is_not_success(self):
        self.api.verify_fail = True
        with self.assertRaises(RuntimeError): self.run_publish()
        self.assertEqual(self.store.state['records'][0]['status'], 'pending')
    def test_wrong_account_cannot_reserve_or_post(self):
        with self.assertRaises(ValueError): t.publish(feed(), self.store, self.api, NOW, '0 23 * * *', '123', 'wrong')
        self.assertEqual(self.store.state['records'], []); self.assertEqual(self.api.calls, [])

    def test_missing_writer_never_falls_back_to_legacy_template(self):
        with self.assertRaisesRegex(ValueError, 'writer_queue_required'):
            t.publish(feed(), self.store, self.api, NOW, '0 23 * * *', '123', '1004')
        self.assertEqual(self.api.calls, [])
        self.assertEqual(self.store.state['records'], [])

    def test_missing_image_does_not_turn_an_image_slot_into_text(self):
        with self.assertRaisesRegex(ValueError, 'approved_image_required'):
            t.select_image(feed()['items'][0], [{}], {})
    def test_expired_sample_future_conflict_and_stale_data_rejected(self):
        for field, value in [('endDate','2026-11-03'), ('startDate','2026-11-05'),
                             ('sourceConflicts',['지원대상']), ('checkedAt','2026-10-01T00:00:00+09:00'),
                             ('officialUrl','https://plus.gov.kr.evil.test/')]:
            with self.subTest(field=field):
                f = feed(); f['items'][0][field] = value
                self.assertEqual(t.candidates(f, empty(), NOW), [])
        for key, value in [('isSample',True), ('updatedAt','2026-10-01T00:00:00+09:00')]:
            f = feed(); f[key] = value; self.assertEqual(t.candidates(f, empty(), NOW), [])
    def test_no_candidate_is_skip_not_published(self):
        f = feed(); f['items'] = []
        self.assertEqual(self.run_publish(f)['status'], 'skipped')
        self.assertEqual(self.api.calls, [])
    def test_missed_or_unknown_slot_rejected(self):
        for now, cron in [(NOW + timedelta(hours=2),'0 23 * * *'), (NOW,'unknown')]:
            with self.assertRaises(ValueError): t.current_slot(now, cron)

    def test_prepublication_recovery_reuses_original_slot_and_blocks_duplicate(self):
        env = {'SUPPORTPICK_THREADS_ENABLED':'true', 'SUPPORTPICK_THREADS_CUTOVER_READY':'true',
               'GITHUB_REPOSITORY':t.REPO, 'GITHUB_REF':'refs/heads/main', 'GITHUB_RUN_ATTEMPT':'1',
               'GITHUB_EVENT_NAME':'workflow_dispatch', 'SUPPORTPICK_THREADS_MANUAL_MODE':'resume-unreserved-slot',
               'SUPPORTPICK_THREADS_RECOVERY_CRON':'0 23 * * *'}
        cron = t.publication_context(env)
        self.run_publish()
        with self.assertRaisesRegex(RuntimeError, 'slot_already_reserved'):
            t.publish(feed(), self.store, self.api, NOW+timedelta(minutes=10), cron, '124', '1004')
        self.assertEqual(len(self.api.calls), 1)
        with self.assertRaisesRegex(ValueError, 'missed_slot_not_backfilled'):
            t.current_slot(NOW+timedelta(hours=2), cron)
        with self.assertRaises(ValueError):
            t.publication_context({**env, 'GITHUB_RUN_ATTEMPT':'2'})
    def test_content_has_no_links_and_retains_profile_cta(self):
        row = feed()['items'][0]
        row['publishedBlogUrl'] = 'https://blog.naver.com/bible_el/123456'
        texts = t.compose(row)
        self.assertTrue(all(len(x) <= 500 for x in texts))
        self.assertIn('현재 접수를 보장하지 않습니다', texts[1])
        self.assertTrue(all(not t.TEXT_LINK.search(x) for x in texts))
        self.assertTrue(all(x.endswith('자세한 사항은 프로필링크 확인') for x in texts))
        self.assertTrue(all('blog.naver.com' not in x and t.SITE not in x for x in texts))
        self.assertIn(row['title'], texts[2])
        row['officialUrl'] += 'a' * 600
        self.assertEqual(t.compose(row), texts)

    def test_source_addresses_removed_before_truncation_without_changing_source(self):
        for address in ['https://plus.gov.kr/' + 'a' * 700, 'HTTP://example.com/a',
                        'www.gov.kr/path', 'plus.gov.kr/path', 'https://t.co/abc',
                        'ftp://example.com/a', '정책.한국/신청']:
            with self.subTest(address=address[:35]):
                row = feed()['items'][0]
                for key in ['title', 'summary', 'organization', 'target', 'period', 'method', 'category']:
                    row[key] = '안내 ' + address + ' 조건 확인'
                original = copy.deepcopy(row)
                texts = t.compose(row)
                self.assertTrue(all(not t.TEXT_LINK.search(x) for x in texts))
                self.assertTrue(all(x.endswith(t.CTA) for x in texts))
                self.assertNotIn('example.com', '\n'.join(texts))
                self.assertEqual(row, original)

    def test_published_metadata_keeps_official_source_but_sent_texts_have_no_links(self):
        self.run_publish()
        self.assertEqual(self.store.state['records'][0]['official_url'], feed()['items'][0]['officialUrl'])
        self.assertTrue(all(not t.TEXT_LINK.search(call[0]) for call in self.api.calls))

    def test_image_rotation_alternates_and_preserves_exact_reserved_image(self):
        urls = ['https://raw.githubusercontent.com/kllollain-max/supportpick/main/social/images/benefit-guide-1.png',
                'https://raw.githubusercontent.com/kllollain-max/supportpick/main/social/images/benefit-guide-2.png']
        assets = {'_rotation': urls}
        expected = [None, urls[0], None, urls[1]]
        for index, hour in enumerate([8, 12, 16, 20]):
            f = feed(); f['items'][0]['id'] = 'benefit' + str(index)
            cron = next(c for c,h in t.CRONS.items() if h == hour)
            now = NOW.replace(hour=hour)
            t.publish(f, self.store, self.api, now, cron, '123', '1004', assets,
                      reviewed_queue(f, self.store.state, now, cron, assets))
            self.assertEqual(self.store.state['records'][-1]['image_url'], expected[index])
        self.assertEqual([c[2] for c in self.api.calls], expected)
        self.assertEqual(t.select_image(feed()['items'][0], [{'image_url':u} for u in expected] + [{}], assets), urls[0])

    def test_unapproved_rotation_blocks_before_reservation_or_post(self):
        self.run_publish()
        f = feed(); f['items'][0]['id'] = 'second'
        before = copy.deepcopy(self.store.state)
        with self.assertRaisesRegex(ValueError, 'unapproved_image_rotation'):
            t.publish(f, self.store, self.api, NOW.replace(hour=12), '0 3 * * *', '124', '1004',
                      {'_rotation':['https://evil.test/image.png']},
                      reviewed_queue(f, self.store.state, NOW.replace(hour=12), '0 3 * * *', {'_rotation': urls_for_tests()}))
        self.assertEqual(self.store.state, before)
        self.assertEqual(len(self.api.calls), 1)

    def test_resume_keeps_reserved_image_when_rotation_changes(self):
        self.store.state['records'].append({'benefit_id':'old', 'slot':NOW.replace(hour=7).isoformat(),
            'run_id':'122', 'status':'published', 'verified':True, 'main_id':'9','detail_id':'8','links_id':'7'})
        image = 'https://raw.githubusercontent.com/kllollain-max/supportpick/main/social/images/benefit-guide-1.png'
        self.api.verify_fail = True
        with self.assertRaises(RuntimeError): self.run_publish(assets={'_rotation':[image]})
        self.api.verify_fail = False
        t.resume_publication(self.store,self.api,NOW,'1004','124','1001')
        self.assertEqual(self.store.state['records'][-1]['image_url'], image)
        self.assertEqual([c[2] for c in self.api.calls], [image])

    def test_legacy_pending_link_is_held_without_rewriting_or_sending(self):
        self.api.verify_fail = True
        with self.assertRaises(RuntimeError): self.run_legacy()
        self.api.verify_fail = False
        record = self.store.state['records'][0]
        record['texts'][1] += '\nhttps://plus.gov.kr/benefit'
        record['content_hash'] = t.hashlib.sha256(json.dumps(record['texts'], ensure_ascii=False).encode()).hexdigest()
        original_texts = copy.deepcopy(record['texts'])
        with self.assertRaisesRegex(ValueError, 'link_free_publication_required'):
            t.resume_publication(self.store, self.api, NOW, '1004', '124', '1001')
        self.assertEqual(len(self.api.calls), 1)
        self.assertEqual(self.store.state['records'][0]['texts'], original_texts)
        self.assertEqual(self.store.state['records'][0]['status'], 'pending')
    def test_social_links_and_images_cannot_point_to_other_accounts(self):
        row = feed()['items'][0]; row['publishedBlogUrl'] = 'https://blog.naver.com/other/123'
        self.assertNotIn('/other/', t.compose(row)[2])
        self.assertTrue(t.image_url('https://raw.githubusercontent.com/kllollain-max/supportpick/main/social/images/test.jpg'))
        self.assertFalse(t.image_url('https://raw.githubusercontent.com/kllollain-max/careerpick/main/social/images/test.jpg'))
    def test_corrupt_or_cross_brand_ledger_is_not_reset(self):
        for state in [{}, {**empty(), 'brand':'careerpick'}, {**empty(), 'records':[{'status':'published'}]}]:
            with self.assertRaises(ValueError): t.validate_ledger(state)
    def test_credential_not_sent_to_arbitrary_host(self):
        self.assertFalse(t.official_url('https://user:password@plus.gov.kr/'))
        self.assertFalse(t.official_url('http://plus.gov.kr/'))
        self.assertFalse(t.official_url('https://plus.gov.kr:8443/'))
    def test_wrong_remote_username_is_rejected(self):
        class Wrong(t.Threads):
            def call(self, *args): return {'id':'1004','username':'hid_119'}
        with self.assertRaises(ValueError): Wrong('fake').verify_account('1004')
    def test_HTTP_error_is_sanitized(self):
        def fail(*args, **kw): raise OSError('secret-token')
        with self.assertRaises(RuntimeError) as error: t.Threads('secret-token', opener=fail, pause=lambda _:None).call('GET','/me')
        self.assertNotIn('secret-token', str(error.exception))
    def test_account_read_status_is_reported_without_exposing_request(self):
        def fail(request, **kwargs):
            raise HTTPError(request.full_url, 401, 'secret-token', {}, None)

        api = t.Threads('secret-token', opener=fail)
        with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_401$'):
            api.verify_account('123')
        with self.assertRaisesRegex(RuntimeError, '^threads_request_failed_or_ambiguous_no_automatic_retry$'):
            api.call('POST', '/me/threads')

    def test_four_slot_daily_cap(self):
        for h in (8, 12, 16, 20):
            slot = NOW.replace(hour=h, minute=0).isoformat()
            self.store.state['records'].append({'benefit_id':str(h), 'slot':slot, 'run_id':str(h),
                'status':'published','verified':True,'main_id':'1','detail_id':'2','links_id':'3'})
        # A fifth new slot is disallowed independently from the repeated-slot guard.
        self.store.state['records'][0]['slot'] = NOW.replace(hour=7, minute=0).isoformat()
        with self.assertRaisesRegex(RuntimeError, 'daily_limit'): self.run_publish()
    def test_missing_state_never_initializes_itself(self):
        def missing(*args, **kw): raise OSError('404')
        with self.assertRaisesRegex(RuntimeError, 'ledger_unavailable'): t.Ledger('fake', opener=missing).read()

    def test_manual_publication_uses_current_minute_and_same_daily_cap(self):
        result = t.publish(feed(), self.store, self.api, NOW, 'manual', '123', '1004',
                           writer_queue=reviewed_queue(feed(), self.store.state, NOW, 'manual'))
        self.assertTrue(result['published'])
        self.assertEqual(self.store.state['records'][0]['slot'], NOW.replace(second=0, microsecond=0).isoformat())
        with self.assertRaisesRegex(RuntimeError, 'slot_already_reserved'):
            t.publish(feed(), self.store, self.api, NOW, 'manual', '124', '1004')
        self.assertEqual(len(self.api.calls), 1)

    def test_explicit_manual_mode_main_repo_and_first_attempt_required(self):
        env = {'SUPPORTPICK_THREADS_ENABLED':'true', 'SUPPORTPICK_THREADS_CUTOVER_READY':'true',
               'GITHUB_REPOSITORY': t.REPO, 'GITHUB_REF':'refs/heads/main',
               'GITHUB_RUN_ATTEMPT':'1', 'GITHUB_EVENT_NAME':'workflow_dispatch',
               'SUPPORTPICK_THREADS_MANUAL_MODE':'publish-one-now'}
        self.assertEqual(t.publication_context(env), 'manual')
        for k,v in [('SUPPORTPICK_THREADS_ENABLED','false'), ('SUPPORTPICK_THREADS_CUTOVER_READY','false'),
                    ('GITHUB_REPOSITORY','kllollain-max/careerpick'), ('GITHUB_REF','refs/heads/feature'),
                    ('GITHUB_RUN_ATTEMPT','2'), ('GITHUB_EVENT_NAME','pull_request'),
                    ('SUPPORTPICK_THREADS_MANUAL_MODE','preview'), ('SUPPORTPICK_THREADS_MANUAL_MODE','check-account')]:
            with self.subTest(k=k, v=v), self.assertRaises(ValueError):
                t.publication_context({**env, k:v})
        scheduled = {**env, 'GITHUB_EVENT_NAME':'schedule', 'SUPPORTPICK_THREADS_CRON':'0 23 * * *'}
        self.assertEqual(t.publication_context(scheduled), '0 23 * * *')
        with self.assertRaises(ValueError): t.publication_context({**scheduled, 'SUPPORTPICK_THREADS_CRON':'unknown'})

    def test_resume_verifies_existing_main_and_only_posts_missing_replies(self):
        self.api.verify_fail = True
        with self.assertRaises(RuntimeError): self.run_legacy()
        self.api.verify_fail = False
        result = t.resume_publication(self.store, self.api, NOW, '1004', '124', '1001')
        self.assertTrue(result['resumed'])
        self.assertEqual(len(self.store.state['records']), 1)
        self.assertEqual([c[1] for c in self.api.calls], [None, '1001', '1001'])
        self.assertEqual(self.store.state['records'][0]['status'], 'published')

    def test_resume_cannot_clear_an_ambiguous_reply_without_receipt(self):
        self.api.fail_at = 2
        with self.assertRaises(RuntimeError): self.run_legacy()
        original = copy.deepcopy(self.store.state)
        with self.assertRaisesRegex(RuntimeError, 'ambiguous_send'):
            t.resume_publication(self.store, self.api, NOW, '1004', '124', '1001')
        self.assertEqual(len(self.api.calls), 2)
        self.assertEqual(original, self.store.state)

    def test_resume_rejects_wrong_id_stale_source_and_content_tampering(self):
        self.api.verify_fail = True
        with self.assertRaises(RuntimeError): self.run_publish()
        self.api.verify_fail = False
        for main_id, now in [('9999', NOW), ('1001', NOW + timedelta(days=1))]:
            with self.assertRaises(ValueError):
                t.resume_publication(self.store, self.api, now, '1004', '124', main_id)
        self.store.state['records'][0]['texts'][0] += 'altered'
        with self.assertRaisesRegex(ValueError, 'content_hash'):
            t.resume_publication(self.store, self.api, NOW, '1004', '124', '1001')
        self.assertEqual(len(self.api.calls), 1)

    def test_only_observed_brand_topic_hash_transformation_is_accepted(self):
        text = t.compose(feed()['items'][0])[0]
        class ReadAPI(t.Threads):
            def call(self, method, path, params=None):
                self.asserted_method = method
                return self.result
        api = ReadAPI('fake', pause=lambda _: None)
        api.result = {'id':'1001', 'text':text.replace('\n\n#지원금픽 ', '\n\n지원금픽 ', 1),
                      'permalink':'https://www.threads.com/@hid_1004/post/test'}
        self.assertTrue(api.verify('1001', text))
        self.assertEqual(api.asserted_method, 'GET')
        for changed in [api.result['text'].replace(t.CTA, '다른 안내'),
                        api.result['text'].replace('#생활안정', '생활안정'),
                        api.result['text'] + 'changed']:
            api.result['text'] = changed
            with self.assertRaisesRegex(RuntimeError, 'verification_failed'):
                api.verify('1001', text)

    def test_id_and_permalink_still_required_after_topic_normalization(self):
        text = t.compose(feed()['items'][0])[0]
        class ReadAPI(t.Threads):
            def call(self, *args): return self.result
        api = ReadAPI('fake', pause=lambda _: None)
        for result in [{'id':'wrong', 'text':text, 'permalink':'url'}, {'id':'1001', 'text':text}]:
            api.result = result
            with self.assertRaises(RuntimeError): api.verify('1001', text)

class PopularityTests(unittest.TestCase):
    def row(self, sid, views, **extra):
        row = copy.deepcopy(feed()['items'][0])
        row.update(id=sid, **extra)
        row['rawSource'] = {'serviceList': {'서비스ID': sid, '조회수': views}}
        return row

    def test_actual_views_take_priority_over_deadline(self):
        f = feed()
        f['items'] = [self.row('low', '100', endDate='2026-11-05'),
                      self.row('popular', '50,000', endDate='2026-12-01')]
        self.assertEqual([r['id'] for r in t.candidates(f, empty(), NOW)], ['popular', 'low'])

    def test_editorial_choice_requires_reasons_for_every_higher_view_candidate(self):
        high, low = self.row('high', 1000), self.row('low', 100)
        with self.assertRaisesRegex(ValueError, 'higher_priority'):
            t.reviewed_selection(low, [high, low], {})
        info = t.reviewed_selection(low, [high, low], {'selection_notes': [
            {'benefit_id': 'high', 'decision': 'HOLD', 'reason': '현재 공식 접수상태 확인 불가'}]})
        self.assertEqual(info['candidate_rank'], 2)
        self.assertEqual(info['higher_ranked_exclusions'][0]['views'], 1000)

    def test_equal_views_use_deadline_then_stable_id(self):
        f = feed(); f['items'] = [self.row('z', 100), self.row('b', '100', endDate='2026-11-05'),
                                 self.row('a', 100, endDate='2026-11-05')]
        self.assertEqual([r['id'] for r in t.candidates(f, empty(), NOW)], ['a', 'b', 'z'])

    def test_missing_invalid_and_wrong_service_counts_are_not_invented(self):
        for value in [None, '', True, -1, 1.5, 'NaN', '1,2', '-100', '1e6', '9'*100]:
            with self.subTest(value=value): self.assertIsNone(t.popularity_views(self.row('x', value)))
        bad = self.row('x', 9999); bad['rawSource']['serviceList']['서비스ID'] = 'other'
        self.assertIsNone(t.popularity_views(bad))
        f = feed(); f['items'] = [self.row('unknown', None), self.row('zero', 0)]
        self.assertEqual([r['id'] for r in t.candidates(f, empty(), NOW)], ['zero', 'unknown'])

    def test_popular_expired_conflicted_and_already_posted_still_excluded(self):
        f = feed(); f['items'] = [self.row('expired', 9999, endDate='2026-11-03'),
             self.row('conflict', 9999, sourceConflicts=['target']), self.row('posted', 9999),
             self.row('valid', 10)]
        ledger = empty(); ledger['records'] = [{'benefit_id':'posted'}]
        self.assertEqual([r['id'] for r in t.candidates(f, ledger, NOW)], ['valid'])

    def test_published_selection_retains_actual_views_and_basis(self):
        f = feed(); f['items'] = [self.row('low', 1), self.row('high', '2,345')]
        store = Store(); api = API(store)
        result = t.publish(f, store, api, NOW, '0 23 * * *', '123', '1004',
                           writer_queue=reviewed_queue(f, store.state))
        self.assertEqual(result['benefit_id'], 'high')
        self.assertEqual(store.state['records'][0]['selection']['views'], 2345)
        self.assertEqual(result['selection']['basis'], '보조금24 누적 조회수')
        self.assertIn('실시간 검색량', result['selection']['note'])

if __name__ == '__main__': unittest.main()

