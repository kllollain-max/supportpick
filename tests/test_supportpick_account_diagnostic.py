"""Account diagnostics remain bounded, read-only, and safe to publish as logs."""
import io
import json
import sys
import tempfile
import unittest
import urllib.parse
import urllib.request
import urllib.response
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import supportpick_threads_account_diagnostic as d


TOKEN = 'FAKE_SECRET_TOKEN_NEVER_OUTPUT'
USER_ID = '7712345678900066'
ENV = {'SUPPORTPICK_THREADS_ACCESS_TOKEN': TOKEN,
       'SUPPORTPICK_THREADS_USER_ID': USER_ID}
NOW = 1800000000
ACCOUNT = {'id': USER_ID, 'username': 'hid_1004'}


class Response(io.BytesIO):
    def __init__(self, payload, status=200):
        super().__init__(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
        self.status = status
        self.read_sizes = []

    def getcode(self):
        return self.status

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class ScriptedOpener:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        if timeout != d.REQUEST_TIMEOUT:
            raise AssertionError('fixed_timeout_required')
        if not self.outcomes:
            raise AssertionError('unexpected_extra_request')
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome if isinstance(outcome, Response) else Response(outcome)


def failure(status=400, fields=None):
    error = {'code': 200, 'message': TOKEN, 'type': TOKEN, 'fbtrace_id': TOKEN}
    error.update(fields or {})
    return HTTPError('https://example.invalid/?access_token=' + TOKEN,
                     status, TOKEN, {'Location': 'https://example.invalid/' + TOKEN},
                     io.BytesIO(json.dumps({'error': error, 'private': USER_ID}).encode()))


def inspected(**overrides):
    data = {'is_valid': True, 'user_id': USER_ID,
            'scopes': ['threads_basic', 'threads_content_publish'],
            'expires_at': NOW + 3600, 'data_access_expires_at': NOW + 7200}
    data.update(overrides)
    return {'data': data}


class AccountDiagnosticTests(unittest.TestCase):
    def test_failed_baseline_compares_four_get_variants_then_self_debug(self):
        opener = ScriptedOpener([failure() for _ in range(4)] + [inspected()])
        report = d.diagnose(ENV, opener, NOW)
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(report['classification'], 'no_verified_account_path')
        self.assertEqual(report['request_count'], 5)
        self.assertEqual(report['debug_selection_basis'], 'official_sample_host_account_unverified')
        self.assertEqual(report['token_debug']['probe'], 'com_query_debug')
        self.assertTrue(report['token_debug']['is_valid'])
        self.assertTrue(report['token_debug']['threads_basic'])
        self.assertTrue(report['token_debug']['threads_content_publish'])
        self.assertEqual(report['token_debug']['expires'], 'unexpired')
        parsed = []
        for request in opener.requests:
            self.assertEqual(request.get_method(), 'GET')
            self.assertIsNone(request.data)
            parts = urllib.parse.urlsplit(request.full_url)
            query = urllib.parse.parse_qs(parts.query)
            self.assertEqual(parts.scheme, 'https')
            self.assertIn(parts.hostname, ('graph.threads.net', 'graph.threads.com'))
            self.assertIn(parts.path, ('/v1.0/me', '/v1.0/debug_token'))
            self.assertEqual(request.get_header('Content-type'), 'application/x-www-form-urlencoded')
            if 'access_token' in query:
                self.assertEqual(query['access_token'], [TOKEN])
                self.assertIsNone(request.get_header('Authorization'))
            else:
                self.assertEqual(request.get_header('Authorization'), 'Bearer ' + TOKEN)
            if parts.path == '/v1.0/me':
                self.assertEqual(query['fields'], ['id,username'])
                self.assertNotIn('input_token', query)
            else:
                self.assertEqual(query['input_token'], [TOKEN])
            parsed.append((parts.hostname, parts.path, 'access_token' in query))
        self.assertEqual(len(set(parsed)), 5)

    def test_verified_original_skips_all_alternatives(self):
        opener = ScriptedOpener([ACCOUNT, inspected()])
        report = d.diagnose(ENV, opener, NOW)
        self.assertEqual(report['request_count'], 2)
        self.assertEqual(report['classification'], 'original_path_verified')
        self.assertTrue(report['original_path_verified'])
        self.assertEqual(report['verified_alternatives'], [])
        self.assertEqual(report['token_debug']['probe'], 'net_query_debug')
        self.assertEqual(report['debug_selection_basis'], 'verified_account_host_official_query_auth')

    def test_alternative_success_is_distinguished_from_baseline_success(self):
        for index, expected_probe, debug_probe in ((1, 'com_bearer_me', 'com_query_debug'),
                                                    (2, 'net_query_me', 'net_query_debug'),
                                                    (3, 'com_query_me', 'com_query_debug')):
            with self.subTest(probe=expected_probe):
                outcomes = [ACCOUNT if i == index else failure() for i in range(4)]
                opener = ScriptedOpener(outcomes + [inspected()])
                report = d.diagnose(ENV, opener, NOW)
                self.assertEqual(report['classification'], 'original_failed_alternative_verified')
                self.assertFalse(report['original_path_verified'])
                self.assertEqual(report['verified_alternatives'], [expected_probe])
                self.assertEqual(report['token_debug']['probe'], debug_probe)
                self.assertEqual(report['request_count'], 5)

    def test_permission_code_alone_does_not_claim_invalid_or_expired_token(self):
        report = d.diagnose(ENV, ScriptedOpener([failure() for _ in range(5)]), NOW)
        debug = report['token_debug']
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(debug['api_code'], 200)
        self.assertIsNone(debug['is_valid'])
        self.assertIsNone(debug['threads_basic'])
        self.assertIsNone(debug['threads_content_publish'])
        self.assertIsNone(debug['user_id_matches'])
        self.assertEqual(debug['expires'], 'unknown')

    def test_wrong_account_stops_without_inspection_or_alternative_success(self):
        for account in ({'id': '999999', 'username': 'hid_1004'},
                        {'id': USER_ID, 'username': TOKEN}):
            with self.subTest(account_field=list(account)):
                opener = ScriptedOpener([failure(), account])
                report = d.diagnose(ENV, opener, NOW)
                self.assertEqual(report['classification'], 'account_mismatch')
                self.assertEqual(report['request_count'], 2)
                self.assertEqual(report['verified_alternatives'], [])
                self.assertIsNone(report['token_debug'])
                self.assertNotIn(TOKEN, json.dumps(report))

    def test_missing_account_fields_and_http_200_error_are_not_success(self):
        for payload in ({'id': USER_ID}, {'username': 'hid_1004'}, {},
                        {'id': USER_ID, 'username': 'hid_1004', 'error': {'code': 200}}):
            with self.subTest(keys=list(payload)):
                client = d.DiagnosticClient(TOKEN, USER_ID, ScriptedOpener([payload]), NOW)
                result = client.read(d.PROBES[0])
                self.assertNotEqual(result['status'], 'account_verified')

    def test_temporary_http_and_transport_failures_stop_without_retries(self):
        errors = [failure(status) for status in (408, 429, 500, 502, 503, 504)]
        errors += [URLError(TOKEN), TimeoutError(TOKEN), OSError(TOKEN)]
        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                opener = ScriptedOpener([error])
                report = d.diagnose(ENV, opener, NOW)
                self.assertEqual(report['classification'], 'inconclusive_temporary_failure')
                self.assertEqual(report['request_count'], 1)
                self.assertEqual(len(opener.requests), 1)
                self.assertIsNone(report['token_debug'])

    def test_debug_scope_validity_and_expiry_require_correct_types(self):
        for data in ({}, {'is_valid': 1, 'scopes': TOKEN, 'expires_at': True},
                     {'is_valid': 'true', 'scopes': ['threads_basic', 1], 'expires_at': '1'}):
            with self.subTest(keys=list(data)):
                client = d.DiagnosticClient(TOKEN, USER_ID, ScriptedOpener([{'data': data}]), NOW)
                result = client.read(d.PROBES[3], 'debug_token')
                self.assertIsNone(result['is_valid'])
                self.assertIsNone(result['threads_basic'])
                self.assertIsNone(result['threads_content_publish'])
                self.assertEqual(result['expires'], 'unknown')
        client = d.DiagnosticClient(TOKEN, USER_ID,
                                    ScriptedOpener([inspected(scopes=[], expires_at=0)]), NOW)
        result = client.read(d.PROBES[3], 'debug_token')
        self.assertFalse(result['threads_basic'])
        self.assertFalse(result['threads_content_publish'])
        self.assertEqual(result['expires'], 'not_set')

    def test_explicit_token_invalid_expired_missing_scope_and_wrong_id_are_preserved(self):
        opener = ScriptedOpener([failure() for _ in range(4)] + [inspected(
            is_valid=False, user_id='999999', scopes=['threads_basic'], expires_at=NOW - 1)])
        report = d.diagnose(ENV, opener, NOW)
        self.assertEqual(report['classification'], 'account_mismatch')
        debug = report['token_debug']
        self.assertFalse(debug['is_valid'])
        self.assertFalse(debug['user_id_matches'])
        self.assertTrue(debug['threads_basic'])
        self.assertFalse(debug['threads_content_publish'])
        self.assertEqual(debug['expires'], 'expired')

    def test_only_bounded_integer_error_codes_are_emitted(self):
        for value in (TOKEN, '190', True, 1.5, -1, 2**40, [], {}):
            with self.subTest(value_type=type(value).__name__):
                opener = ScriptedOpener([failure(fields={'code': value, 'error_subcode': value})])
                result = d.DiagnosticClient(TOKEN, USER_ID, opener, NOW).read(d.PROBES[0])
                self.assertIsNone(result['api_code'])
                self.assertIsNone(result['api_subcode'])
        opener = ScriptedOpener([failure(fields={'code': 190, 'error_subcode': 463})])
        result = d.DiagnosticClient(TOKEN, USER_ID, opener, NOW).read(d.PROBES[0])
        self.assertEqual((result['api_code'], result['api_subcode']), (190, 463))

    def test_response_read_is_limited_and_truncated_json_is_not_trusted(self):
        body = Response({'error': {'message': TOKEN * 1000, 'code': 190}}, status=400)
        result = d.DiagnosticClient(TOKEN, USER_ID, ScriptedOpener([body]), NOW).read(d.PROBES[0])
        self.assertEqual(body.read_sizes, [16 * 1024])
        self.assertIsNone(result['api_code'])

    def test_all_redirect_types_are_blocked_before_second_transport_request(self):
        class FakeHttps(urllib.request.HTTPSHandler):
            def __init__(self, status):
                super().__init__()
                self.status = status
                self.requests = []

            def https_open(self, request):
                self.requests.append(request)
                headers = Message()
                headers['Location'] = 'https://example.invalid/?access_token=' + TOKEN
                response = urllib.response.addinfourl(io.BytesIO(TOKEN.encode()), headers,
                                                     request.full_url, self.status)
                response.msg = TOKEN
                return response

        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                transport = FakeHttps(status)
                opener = urllib.request.build_opener(d.RefuseRedirects(), transport)
                result = d.DiagnosticClient(TOKEN, USER_ID, opener, NOW).read(d.PROBES[3])
                self.assertEqual(result['status'], 'redirect_blocked')
                self.assertEqual(result['http_status'], status)
                self.assertEqual(len(transport.requests), 1)
                self.assertNotIn(TOKEN, json.dumps(result))
                self.assertNotIn('example.invalid', json.dumps(result))

    def test_request_budget_and_fixed_paths_cannot_be_expanded(self):
        opener = ScriptedOpener([failure() for _ in range(5)])
        client = d.DiagnosticClient(TOKEN, USER_ID, opener, NOW)
        for _ in range(5):
            client.read(d.PROBES[0])
        with self.assertRaisesRegex(ValueError, '^diagnostic_request_budget_exhausted$'):
            client.read(d.PROBES[0])
        self.assertEqual(len(opener.requests), 5)
        for probe, resource in ((d.Probe('unknown', 'example.invalid', 'query'), 'me'),
                                (d.PROBES[0], 'threads'), (d.PROBES[0], 'refresh_access_token'),
                                (d.PROBES[0], 'debug_token')):
            with self.assertRaises(ValueError):
                client.read(probe, resource)
        self.assertEqual(len(opener.requests), 5)

    def test_configuration_failure_makes_no_network_request(self):
        for env in ({}, {**ENV, 'SUPPORTPICK_THREADS_ACCESS_TOKEN': TOKEN + '\n'},
                    {**ENV, 'SUPPORTPICK_THREADS_USER_ID': TOKEN}):
            opener = ScriptedOpener([])
            report = d.diagnose(env, opener, NOW)
            self.assertEqual(report['status'], 'configuration_incomplete')
            self.assertEqual(report['request_count'], 0)
            self.assertEqual(opener.requests, [])
            self.assertNotIn(TOKEN, json.dumps(report))

    def test_report_stdout_stderr_and_step_summary_never_include_private_values(self):
        private_name = 'PRIVATE_DISPLAY_NAME_NEVER_OUTPUT'
        private_application = 'PRIVATE_APPLICATION_NEVER_OUTPUT'
        opener = ScriptedOpener([failure(fields={'error_subcode': 463}) for _ in range(4)]
                                + [inspected(name=private_name, application=private_application,
                                             arbitrary={'token': TOKEN, 'url': TOKEN},
                                             scopes=['threads_basic', TOKEN])])
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            summary_path = Path(tmp) / 'step-summary.md'
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = d.main({**ENV, 'GITHUB_STEP_SUMMARY': str(summary_path)},
                              opener, tmp, NOW)
            report_text = (Path(tmp) / d.REPORT_NAME).read_text()
            summary_text = summary_path.read_text()
            output = report_text + summary_text + stdout.getvalue() + stderr.getvalue()
            self.assertEqual(code, 0)
            for private in (TOKEN, USER_ID, 'hid_1004', private_name, private_application,
                            'example.invalid', 'https://', str(NOW + 3600)):
                self.assertNotIn(private, output)
            self.assertIn('| net_bearer_me | http_error | 400 | 200 | 463 |', summary_text)
            self.assertIn('| com_query_debug | token_inspected | 200 |', summary_text)
            self.assertEqual(set(p.name for p in Path(tmp).iterdir()),
                             {d.REPORT_NAME, 'step-summary.md'})

    def test_unexpected_client_exception_is_sanitized_and_exits_nonzero(self):
        opener = ScriptedOpener([ValueError('https://example.invalid/' + TOKEN)])
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = d.main(ENV, opener, tmp, NOW)
            report = json.loads((Path(tmp) / d.REPORT_NAME).read_text())
            self.assertEqual(code, 1)
            self.assertEqual(report['status'], 'internal_error')
            self.assertEqual(report['request_count'], 1)
            self.assertNotIn(TOKEN, json.dumps(report) + stdout.getvalue() + stderr.getvalue())
            self.assertEqual(len(opener.requests), 1)

    def test_report_write_exception_never_prints_path_or_raw_exception(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(Path, 'write_text', side_effect=OSError(TOKEN)):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = d.main({}, ScriptedOpener([]), '/unused', NOW)
        self.assertEqual(code, 1)
        self.assertNotIn(TOKEN, stdout.getvalue() + stderr.getvalue())
        self.assertNotIn('/unused', stdout.getvalue() + stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
