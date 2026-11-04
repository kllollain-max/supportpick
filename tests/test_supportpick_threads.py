import copy
import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_threads as t

NOW = datetime(2026, 11, 4, 8, 15, tzinfo=t.KST)

def empty():
    return {'version': 1, 'brand': 'supportpick', 'username': 'hid_1004', 'records': []}

def feed():
    return {'isSample': False, 'updatedAt': NOW.isoformat(), 'generation': 'test', 'items': [{
        'id': 'benefit1', 'title': '생활지원', 'organization': '공공기관', 'summary': '생활 지원 안내',
        'target': '세부 소득·거주 조건 충족 가구', 'method': '공식 창구에서 안내 확인',
        'period': '원문 확인', 'category': '생활안정', 'checkedAt': NOW.isoformat(),
        'officialUrl': 'https://plus.gov.kr/benefit', 'sourceConflicts': []}]}

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
        return t.publish(data or feed(), self.store, self.api, now, '0 23 * * *', '123', '1004', assets)
    def test_complete_main_and_two_replies(self):
        result = self.run_publish()
        self.assertTrue(result['published'])
        self.assertEqual([x[1] for x in self.api.calls], [None, '1001', '1001'])
        self.assertEqual(self.store.state['records'][0]['status'], 'published')
        self.assertTrue(all(x[0].endswith(t.CTA) for x in self.api.calls))
        self.assertIn('프로필링크', self.api.calls[2][0])
    def test_same_slot_cannot_post_twice(self):
        self.run_publish()
        with self.assertRaisesRegex(RuntimeError, 'slot_already_reserved'): self.run_publish()
        self.assertEqual(len(self.api.calls), 3)
    def test_post_ambiguity_blocks_future_slots(self):
        self.api.fail_at = 1
        with self.assertRaises(RuntimeError): self.run_publish()
        with self.assertRaisesRegex(RuntimeError, 'unresolved'): self.run_publish(now=NOW + timedelta(days=1))
        self.assertEqual(len(self.api.calls), 1)
    def test_reply_ambiguity_preserves_main_receipt(self):
        self.api.fail_at = 2
        with self.assertRaises(RuntimeError): self.run_publish()
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
    def test_content_no_open_claim_and_whole_links(self):
        row = feed()['items'][0]
        row['publishedBlogUrl'] = 'https://blog.naver.com/bible_el/123456'
        texts = t.compose(row)
        self.assertTrue(all(len(x) <= 500 for x in texts))
        self.assertIn('현재 접수를 보장하지 않습니다', texts[1])
        self.assertIn(row['officialUrl'], texts[1])
        self.assertTrue(all(x.endswith('자세한 사항은 프로필링크 확인') for x in texts))
        self.assertTrue(all('blog.naver.com' not in x and t.SITE not in x for x in texts))
        self.assertIn(row['title'], texts[2])
        row['officialUrl'] += 'a' * 600
        with self.assertRaises(ValueError): t.compose(row)
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
        with self.assertRaises(RuntimeError) as error: t.Threads('secret-token', opener=fail).call('GET','/me')
        self.assertNotIn('secret-token', str(error.exception))
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
        result = t.publish(feed(), self.store, self.api, NOW, 'manual', '123', '1004')
        self.assertTrue(result['published'])
        self.assertEqual(self.store.state['records'][0]['slot'], NOW.replace(second=0, microsecond=0).isoformat())
        with self.assertRaisesRegex(RuntimeError, 'slot_already_reserved'):
            t.publish(feed(), self.store, self.api, NOW, 'manual', '124', '1004')
        self.assertEqual(len(self.api.calls), 3)

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
        with self.assertRaises(RuntimeError): self.run_publish()
        self.api.verify_fail = False
        result = t.resume_publication(self.store, self.api, NOW, '1004', '124', '1001')
        self.assertTrue(result['resumed'])
        self.assertEqual(len(self.store.state['records']), 1)
        self.assertEqual([c[1] for c in self.api.calls], [None, '1001', '1001'])
        self.assertEqual(self.store.state['records'][0]['status'], 'published')

    def test_resume_cannot_clear_an_ambiguous_reply_without_receipt(self):
        self.api.fail_at = 2
        with self.assertRaises(RuntimeError): self.run_publish()
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
        result = t.publish(f, store, api, NOW, '0 23 * * *', '123', '1004')
        self.assertEqual(result['benefit_id'], 'high')
        self.assertEqual(store.state['records'][0]['selection']['views'], 2345)
        self.assertEqual(result['selection']['basis'], '보조금24 누적 조회수')
        self.assertIn('실시간 검색량', result['selection']['note'])

if __name__ == '__main__': unittest.main()
