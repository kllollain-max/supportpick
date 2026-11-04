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
        self.assertIn(t.SITE, self.api.calls[2][0]); self.assertIn('#benefit=benefit1', self.api.calls[2][0]); self.assertNotIn(t.BLOG, self.api.calls[2][0])
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
        self.assertIn(row['officialUrl'], texts[1]); self.assertIn('#benefit=benefit1', texts[2]); self.assertNotIn(row['publishedBlogUrl'], texts[2])
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

if __name__ == '__main__': unittest.main()
