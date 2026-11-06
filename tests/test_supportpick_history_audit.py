"""Read-only reconciliation must not turn incomplete media evidence into success."""
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_threads as t


def fixtures():
    records, rows = [], []
    for index, hour in enumerate((8, 12)):
        pid = str(1001 + index)
        text = '검수된 지원금 안내 ' + pid + '\n\n' + t.CTA
        records.append({'benefit_id': 'benefit-' + pid, 'slot': f'2026-11-06T{hour:02}:00:00+09:00',
                        'run_id': pid, 'status': 'published', 'verified': True, 'main_id': pid,
                        'writer_schema': 'supportpick.writer.v1', 'texts': [text],
                        'image_url': 'https://example.invalid/approved.png' if index else None,
                        'published_at': f'2026-11-06T{hour:02}:00:01+09:00'})
        rows.append({'id': pid, 'text': text,
                     'timestamp': f'2026-11-06T{hour - 9:02}:40:51+0000' if hour >= 9 else '2026-11-05T23:40:51+0000',
                     'permalink': 'https://www.threads.com/@hid_1004/post/post' + pid,
                     'media_type': 'IMAGE' if index else 'TEXT_POST',
                     'media_url': 'https://cdn.example.invalid/photo?signature=private-signed-value' if index else None})
    return ({'version': 1, 'brand': 'supportpick', 'username': 'hid_1004', 'records': records},
            {'data': list(reversed(rows)), 'paging': {'next': 'https://example.invalid/?access_token=private-token'}})


class ReadStore:
    def __init__(self, state):
        self.state = copy.deepcopy(state)
        self.reads = 0

    def read(self):
        self.reads += 1
        return 'abc123', self.state

    def save(self, *args):
        raise AssertionError('A history audit must never write the ledger')


class ReadAPI:
    def __init__(self, recent):
        self.recent, self.calls = recent, []

    def verify_account(self, uid):
        self.calls.append(('verify_account', uid))
        if uid != '1004':
            raise ValueError('wrong_threads_account')

    def call(self, method, path, params=None):
        if method != 'GET' or path != '/me/threads':
            raise AssertionError('Only the fixed history GET is allowed')
        self.calls.append((method, path, params))
        return copy.deepcopy(self.recent)

    def post(self, *args, **kwargs):
        raise AssertionError('A history audit must never post')


class HistoryAuditTests(unittest.TestCase):
    def setUp(self):
        self.state, self.recent = fixtures()

    def audit(self):
        return t.audit_recent_publications(self.state, self.recent)

    def test_get_only_reconciles_ledger_order_and_remote_time_without_exposing_signed_urls(self):
        before = copy.deepcopy(self.state)
        store, api = ReadStore(self.state), ReadAPI(self.recent)
        result = t.check_account_history(store, api, '1004')
        audit = result['publication_audit']
        self.assertEqual(audit['status'], 'verified')
        self.assertEqual(audit['chronological_order'], 'verified')
        self.assertEqual([r['id'] for r in audit['records']], ['1001', '1002'])
        self.assertEqual(audit['records'][0]['media_type'], 'TEXT_POST')
        self.assertTrue(audit['records'][1]['has_media_url'])
        self.assertEqual(audit['records'][1]['remote_published_at'], '2026-11-06T12:40:51+09:00')
        self.assertNotEqual(audit['records'][1]['remote_published_at'], self.state['records'][1]['published_at'])
        self.assertFalse(result['published'])
        self.assertEqual(api.calls[1][2]['fields'], 'id,text,permalink,timestamp,media_type,media_url')
        self.assertEqual(store.reads, 1)
        self.assertEqual(store.state, before)
        self.assertEqual(self.state, before)
        for private in ('private-signed-value', 'private-token', 'cdn.example.invalid', 'paging'):
            self.assertNotIn(private, json.dumps(result))

    def test_media_mismatch_is_not_verified(self):
        self.recent['data'][0]['media_type'] = 'TEXT_POST'
        result = self.audit()
        self.assertEqual(result['status'], 'mismatch')
        self.assertIn('media_type_mismatch', result['records'][1]['reasons'])

    def test_missing_remote_id_is_incomplete_even_when_no_more_history_is_advertised(self):
        self.recent['data'] = self.recent['data'][:1]
        self.recent.pop('paging')
        result = self.audit()
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(result['records'][0]['reasons'], ['missing_from_recent_history'])
        self.assertIsNone(result['records'][0]['remote_published_at'])

    def test_missing_image_url_and_timestamp_cannot_use_ledger_values_as_fallback(self):
        self.recent['data'][0].pop('media_url')
        self.recent['data'][0].pop('timestamp')
        result = self.audit()
        self.assertEqual(result['status'], 'incomplete')
        self.assertIn('image_media_url_missing_or_invalid', result['records'][1]['reasons'])
        self.assertIsNone(result['records'][1]['remote_published_at'])

    def test_outgoing_text_type_is_not_mistaken_for_remote_text_post_type(self):
        self.recent['data'][1]['media_type'] = 'TEXT'
        self.assertEqual(self.audit()['status'], 'mismatch')

    def test_api_list_order_does_not_override_timestamp_order(self):
        self.recent['data'][0]['timestamp'] = '2026-11-05T22:00:00+0000'
        result = self.audit()
        self.assertEqual(result['chronological_order'], 'mismatch')
        self.assertEqual(result['status'], 'mismatch')

    def test_duplicate_ids_and_equal_timestamps_are_incomplete(self):
        self.recent['data'].append(copy.deepcopy(self.recent['data'][0]))
        self.assertEqual(self.audit()['status'], 'incomplete')
        self.recent['data'].pop()
        self.recent['data'][0]['timestamp'] = self.recent['data'][1]['timestamp']
        self.assertEqual(self.audit()['chronological_order'], 'incomplete')

    def test_text_mismatch_and_untrusted_permalink_are_not_accepted_or_echoed(self):
        self.recent['data'][0]['text'] += ' changed'
        self.recent['data'][0]['permalink'] = 'https://private.example.invalid/?token=do-not-print'
        result = self.audit()
        self.assertEqual(result['status'], 'mismatch')
        self.assertIsNone(result['records'][1]['permalink'])
        self.assertNotIn('do-not-print', json.dumps(result))

    def test_known_public_permalink_drops_query_and_fragment(self):
        self.recent['data'][0]['permalink'] += '?token=private-value#private-fragment'
        result = self.audit()
        self.assertEqual(result['status'], 'verified')
        self.assertNotIn('private-', json.dumps(result))

    def test_malformed_url_fields_and_history_are_controlled_failures(self):
        for value in (123, {'private-token': 'do-not-print'}, ['private-url']):
            with self.subTest(value=type(value).__name__):
                self.recent['data'][0]['media_url'] = value
                self.recent['data'][0]['permalink'] = value
                result = self.audit()
                self.assertEqual(result['status'], 'incomplete')
                self.assertNotIn('do-not-print', json.dumps(result))
        for response in ({}, {'data': {}}, {'data': [None]}):
            with self.assertRaisesRegex(ValueError, '^threads_history_invalid_response$'):
                t.audit_recent_publications(self.state, response)

    def test_pending_and_empty_history_are_not_reported_as_completed(self):
        self.state['records'][1]['status'] = 'pending'
        self.assertEqual(self.audit()['status'], 'incomplete')
        self.state['records'] = []
        self.assertEqual(self.audit()['status'], 'incomplete')

    def test_wrong_account_stops_before_reading_the_ledger_or_history(self):
        store, api = ReadStore(self.state), ReadAPI(self.recent)
        with self.assertRaisesRegex(ValueError, 'wrong_threads_account'):
            t.check_account_history(store, api, 'other')
        self.assertEqual(store.reads, 0)
        self.assertEqual(len(api.calls), 1)

    def test_cli_preserves_detailed_incomplete_report_and_exits_nonzero_without_mutation(self):
        self.recent['data'] = []
        store, api = ReadStore(self.state), ReadAPI(self.recent)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                'SUPPORTPICK_THREADS_USER_ID': '1004', 'GITHUB_STEP_SUMMARY': ''}), \
                patch.object(t, 'Ledger', return_value=store), patch.object(t, 'Threads', return_value=api), \
                patch.object(sys, 'argv', ['supportpick_threads.py', 'check-account']), redirect_stdout(io.StringIO()):
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                with self.assertRaises(SystemExit) as raised:
                    t.main()
                self.assertEqual(raised.exception.code, 1)
                report = json.loads(Path('threads-result.json').read_text())
                self.assertEqual(report['status'], 'publication_audit_incomplete')
                self.assertTrue(report['account_verified'])
                self.assertFalse(report['published'])
                self.assertEqual(report['publication_audit']['verified_records'], 0)
            finally:
                os.chdir(old_cwd)


if __name__ == '__main__':
    unittest.main()
