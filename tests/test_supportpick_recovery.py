"""Transient reads recover without repeating a Threads mutation."""
import io
import json
import sys
import traceback
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_threads as t


class ScriptedOpener:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def __call__(self, request, **kwargs):
        self.requests.append((request.get_method(), request.full_url))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        if isinstance(outcome, bytes):
            return io.BytesIO(outcome)
        return io.BytesIO(json.dumps(outcome).encode())


def http_error(code, headers=None):
    return HTTPError('https://graph.threads.net/v1.0/me', code,
                     'secret-token-in-server-message', headers or {},
                     io.BytesIO(b'secret-token-in-response-body'))


class ReadRetryTests(unittest.TestCase):
    def make_api(self, outcomes):
        opener = ScriptedOpener(outcomes)
        pauses = []
        api = t.Threads('secret-token', opener=opener, pause=pauses.append)
        return api, opener, pauses

    def test_transient_http_read_recovers_with_one_retry(self):
        for code in (408, 429, 500, 502, 503, 504):
            with self.subTest(code=code):
                api, opener, pauses = self.make_api([
                    http_error(code), {'id': '1004', 'username': 'hid_1004'}])
                self.assertEqual(api.verify_account('1004'), '1004')
                self.assertEqual(len(opener.requests), 2)
                self.assertEqual(pauses, [2])
                self.assertTrue(all(method == 'GET' for method, _ in opener.requests))

    def test_exhausted_http_reads_have_three_total_attempts(self):
        api, opener, pauses = self.make_api([http_error(503) for _ in range(3)])
        with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_503$') as error:
            api.verify_account('1004')
        self.assertEqual(len(opener.requests), 3)
        self.assertEqual(pauses, [2, 5])
        self.assertNotIn('secret-token', str(error.exception))

    def test_transport_read_can_recover(self):
        for error in (URLError('secret-token'), TimeoutError('secret-token'), OSError('secret-token')):
            with self.subTest(kind=type(error).__name__):
                api, opener, pauses = self.make_api([error, {'id': '1004'}])
                self.assertEqual(api.call('GET', '/1004'), {'id': '1004'})
                self.assertEqual(len(opener.requests), 2)
                self.assertEqual(pauses, [2])

    def test_exhausted_transport_reads_keep_sanitized_account_diagnostic(self):
        api, opener, pauses = self.make_api([URLError('secret-token') for _ in range(3)])
        with self.assertRaisesRegex(RuntimeError, '^threads_account_read_transport_failure$'):
            api.verify_account('1004')
        self.assertEqual(len(opener.requests), 3)
        self.assertEqual(pauses, [2, 5])

    def test_permanent_http_errors_do_not_retry(self):
        for code in (400, 401, 403, 404):
            with self.subTest(code=code):
                api, opener, pauses = self.make_api([http_error(code)])
                with self.assertRaisesRegex(RuntimeError, f'^threads_account_read_http_{code}$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_oauth_codes_are_reported_without_message_or_credential_leak(self):
        secret = 'FAKE_SECRET_TOKEN_DO_NOT_PRINT'
        body = json.dumps({'error': {
            'code': 190, 'error_subcode': 463,
            'type': 'OAuthException',
            'message': 'Access token expired: ' + secret,
            'url': 'https://example.invalid/?access_token=' + secret,
            'fbtrace_id': secret}}).encode()
        error = HTTPError('https://example.invalid/?access_token=' + secret,
                          400, secret, {}, io.BytesIO(body))
        api, opener, pauses = self.make_api([error])
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                api.verify_account('1004')
            except RuntimeError as failure:
                reason = str(failure)
                rendered = traceback.format_exc()
            else:
                self.fail('OAuth failure must remain a failure')
        self.assertEqual(reason, 'threads_account_read_http_400_code_190_subcode_463')
        self.assertNotIn(secret, rendered + stdout.getvalue() + stderr.getvalue())
        self.assertNotIn('OAuthException', rendered)
        self.assertNotIn('example.invalid', rendered)
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(pauses, [])

    def test_independent_numeric_error_fields_are_allowed(self):
        for fields, suffix in (({'code': 190}, '_code_190'),
                               ({'error_subcode': 463}, '_subcode_463'),
                               ({}, '')):
            with self.subTest(fields=fields):
                error = HTTPError('https://graph.threads.net/v1.0/me', 400,
                                  'private-message', {},
                                  io.BytesIO(json.dumps({'error': fields}).encode()))
                api, opener, pauses = self.make_api([error])
                with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_400' + suffix + '$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_non_integer_and_out_of_range_error_codes_are_ignored(self):
        for value in ('190', 'secret-token', True, 190.5, -1, 2**40, [], {}):
            with self.subTest(value_type=type(value).__name__):
                body = json.dumps({'error': {'code': value, 'error_subcode': value}}).encode()
                error = HTTPError('https://graph.threads.net/v1.0/me', 400,
                                  'secret-token', {}, io.BytesIO(body))
                api, opener, pauses = self.make_api([error])
                with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_400$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_http_error_body_read_is_limited_to_sixteen_kib(self):
        class TrackedBody(io.BytesIO):
            def __init__(self, value):
                super().__init__(value)
                self.read_sizes = []

            def read(self, size=-1):
                self.read_sizes.append(size)
                return super().read(size)

        body = TrackedBody(json.dumps({'error': {
            'message': 'secret-token' * 2000, 'code': 190, 'error_subcode': 463}}).encode())
        error = HTTPError('https://graph.threads.net/v1.0/me', 400, 'secret-token', {}, body)
        api, opener, pauses = self.make_api([error])
        with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_400$'):
            api.verify_account('1004')
        self.assertEqual(body.read_sizes, [16 * 1024])
        self.assertEqual(body.tell(), 16 * 1024)
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(pauses, [])

    def test_unreadable_or_non_object_error_body_keeps_http_diagnostic(self):
        for body in (b'', b'not-json secret-token', b'[]', b'{"error": "secret-token"}'):
            with self.subTest(body_type=body[:8]):
                error = HTTPError('https://graph.threads.net/v1.0/me', 401,
                                  'secret-token', {}, io.BytesIO(body))
                api, opener, pauses = self.make_api([error])
                with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_401$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_post_error_body_is_not_read_for_diagnostics(self):
        body = io.BytesIO(json.dumps({'error': {'code': 190, 'error_subcode': 463}}).encode())
        error = HTTPError('https://graph.threads.net/v1.0/me/threads', 400,
                          'secret-token', {}, body)
        api, opener, pauses = self.make_api([error])
        with self.assertRaisesRegex(RuntimeError, '^threads_request_failed_or_ambiguous_no_automatic_retry$'):
            api.call('POST', '/me/threads')
        self.assertEqual(body.tell(), 0)
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(pauses, [])

    def test_invalid_and_semantic_responses_do_not_retry(self):
        for response in (b'not-json secret-token', [], {'error': {'message': 'secret-token'}}):
            with self.subTest(response_type=type(response).__name__):
                api, opener, pauses = self.make_api([response])
                with self.assertRaisesRegex(RuntimeError, '^threads_account_read_invalid_response$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_post_http_errors_never_retry_either_mutation_endpoint(self):
        for path in ('/me/threads', '/me/threads_publish'):
            for code in (408, 429, 500, 502, 503, 504):
                with self.subTest(path=path, code=code):
                    api, opener, pauses = self.make_api([http_error(code, {'Retry-After': '2'})])
                    with self.assertRaisesRegex(RuntimeError, '^threads_request_failed_or_ambiguous_no_automatic_retry$'):
                        api.call('POST', path, {'creation_id': '100'})
                    self.assertEqual(len(opener.requests), 1)
                    self.assertEqual(pauses, [])

    def test_post_transport_errors_never_retry(self):
        for path in ('/me/threads', '/me/threads_publish'):
            for error in (URLError('secret-token'), TimeoutError('secret-token'), OSError('secret-token')):
                with self.subTest(path=path, kind=type(error).__name__):
                    api, opener, pauses = self.make_api([error])
                    with self.assertRaisesRegex(RuntimeError, '^threads_request_failed_or_ambiguous_no_automatic_retry$'):
                        api.call('POST', path)
                    self.assertEqual(len(opener.requests), 1)
                    self.assertEqual(pauses, [])

    def test_short_retry_after_is_honored_without_shortening_backoff(self):
        for retry_after, expected_delay in (('9', 9), ('0', 2)):
            with self.subTest(retry_after=retry_after):
                api, opener, pauses = self.make_api([
                    http_error(429, {'Retry-After': retry_after}), {'id': '1004'}])
                self.assertEqual(api.call('GET', '/1004'), {'id': '1004'})
                self.assertEqual(len(opener.requests), 2)
                self.assertEqual(pauses, [expected_delay])

    def test_long_or_invalid_retry_after_is_not_clamped_or_retried(self):
        for retry_after in ('31', '120', '-1', 'not-a-date', ''):
            with self.subTest(retry_after=retry_after):
                api, opener, pauses = self.make_api([http_error(429, {'Retry-After': retry_after})])
                with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_429$'):
                    api.verify_account('1004')
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])

    def test_retry_after_http_date_is_honored(self):
        now = datetime(2026, 11, 6, 10, 0, tzinfo=t.KST)
        api, opener, pauses = self.make_api([
            http_error(503, {'Retry-After': 'Fri, 06 Nov 2026 01:00:09 GMT'}), {'id': '1004'}])
        with patch.object(t, 'datetime') as clock:
            clock.now.return_value = now
            self.assertEqual(api.call('GET', '/1004'), {'id': '1004'})
        self.assertEqual(len(opener.requests), 2)
        self.assertEqual(pauses, [9])

    def test_retry_after_long_http_date_stays_on_hold(self):
        now = datetime(2026, 11, 6, 10, 0, tzinfo=t.KST)
        api, opener, pauses = self.make_api([
            http_error(503, {'Retry-After': 'Fri, 06 Nov 2026 01:02:00 GMT'})])
        with patch.object(t, 'datetime') as clock:
            clock.now.return_value = now
            with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_503$'):
                api.verify_account('1004')
        self.assertEqual(len(opener.requests), 1)
        self.assertEqual(pauses, [])

    def test_post_receipt_verification_read_can_retry_without_republishing(self):
        text = '확인된 지원 안내\n\n' + t.CTA
        api, opener, pauses = self.make_api([
            http_error(503), {'id': '1004', 'text': text,
                              'permalink': 'https://www.threads.com/@hid_1004/post/verified'}])
        self.assertEqual(api.verify('1004', text),
                         'https://www.threads.com/@hid_1004/post/verified')
        self.assertEqual([method for method, _ in opener.requests], ['GET', 'GET'])
        self.assertEqual(pauses, [2])

    def test_exhausted_account_read_cannot_write_ledger_or_post(self):
        now = datetime(2026, 11, 6, 8, 15, tzinfo=t.KST)
        api, opener, pauses = self.make_api([http_error(503) for _ in range(3)])
        store = Mock()
        with self.assertRaisesRegex(RuntimeError, '^threads_account_read_http_503$'):
            t.publish({}, store, api, now, '0 23 * * *', '123', '1004')
        store.save.assert_not_called()
        self.assertEqual(len(opener.requests), 3)
        self.assertTrue(all(method == 'GET' for method, _ in opener.requests))
        self.assertEqual(pauses, [2, 5])

    def test_wrong_account_cannot_reserve_or_post(self):
        now = datetime(2026, 11, 6, 8, 15, tzinfo=t.KST)
        for account in ({'id': '9999', 'username': 'hid_1004'},
                        {'id': '1004', 'username': 'another_account'}):
            with self.subTest(account=account):
                api, opener, pauses = self.make_api([account])
                store = Mock()
                with self.assertRaisesRegex(ValueError, '^wrong_threads_account$'):
                    t.publish({}, store, api, now, '0 23 * * *', '123', '1004')
                store.save.assert_not_called()
                self.assertEqual(len(opener.requests), 1)
                self.assertEqual(pauses, [])


if __name__ == '__main__':
    unittest.main()
