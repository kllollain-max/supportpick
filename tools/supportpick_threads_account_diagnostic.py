"""Bounded, read-only Threads account diagnostics; never change publisher state.

Meta's official sample uses graph.threads.com and query authentication, while
its Postman collection uses graph.threads.net and the same profile fields:
https://github.com/fbsamples/threads_api/blob/main/src/index.js
https://github.com/fbsamples/threads_api/blob/main/postman/threads-api.postman_collection.json

Compare one variable at a time with the publisher's net/Bearer request. These
observations do not prove a permanent root cause or change publication settings.
The official sample also inspects a user token with that same token, so the
optional self-debug GET needs no app secret or additional permissions.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

MAX_REQUESTS = 5
MAX_RESPONSE_BYTES = 16 * 1024
REQUEST_TIMEOUT = 10
REPORT_NAME = 'threads-account-diagnostic.json'
EXPECTED_USERNAME = 'hid_1004'
TEMPORARY_HTTP_STATUSES = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class Probe:
    name: str
    host: str
    authentication: str


PROBES = (
    Probe('net_bearer_me', 'net', 'bearer'),
    Probe('com_bearer_me', 'com', 'bearer'),
    Probe('net_query_me', 'net', 'query'),
    Probe('com_query_me', 'com', 'query'),
)


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never forward a token, including to another otherwise trusted host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def safe_integer(value, lower=0, upper=2**31 - 1):
    return value if type(value) is int and lower <= value <= upper else None


def read_object(response):
    try:
        raw = response.read(MAX_RESPONSE_BYTES)
        if len(raw) >= MAX_RESPONSE_BYTES:
            return None
        result = json.loads(raw)
        return result if isinstance(result, dict) else None
    except Exception:
        # JSON/transport exceptions can contain the response or token-bearing URL.
        return None


def id_matches(value, expected_id):
    if type(value) is int and 0 <= value <= 10**64:
        value = str(value)
    if isinstance(value, str) and re.fullmatch(r'[0-9]{1,64}', value):
        return value == expected_id
    return None


def expiry_state(value, now):
    if type(value) is not int or value < 0:
        return 'unknown'
    if value == 0:
        # A zero timestamp must not be mistaken for an expired credential.
        return 'not_set'
    return 'expired' if value <= now else 'unexpired'


class DiagnosticClient:
    def __init__(self, token, expected_id, opener=None, now=None):
        self._token = token
        self._expected_id = expected_id
        self._opener = opener or urllib.request.build_opener(RefuseRedirects())
        self._now = time.time() if now is None else now
        self.request_count = 0

    def read(self, probe, resource='me'):
        # There is deliberately no API for arbitrary URLs, paths, or methods.
        if probe not in PROBES or resource not in ('me', 'debug_token'):
            raise ValueError('fixed_diagnostic_probe_required')
        if resource == 'debug_token' and probe.authentication != 'query':
            raise ValueError('official_self_debug_query_auth_required')
        if self.request_count >= MAX_REQUESTS:
            raise ValueError('diagnostic_request_budget_exhausted')
        name = probe.name if resource == 'me' else probe.host + '_query_debug'
        result = {'probe': name, 'status': 'internal_error', 'http_status': None,
                  'api_code': None, 'api_subcode': None}
        if resource == 'me':
            result.update(account_id_matches=None, account_username_matches=None)
        else:
            result.update(is_valid=None, user_id_matches=None, threads_basic=None,
                          threads_content_publish=None, expires='unknown',
                          data_access_expires='unknown')
        try:
            params = ({'fields': 'id,username'} if resource == 'me'
                      else {'input_token': self._token})
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            if probe.authentication == 'query':
                params['access_token'] = self._token
            else:
                headers['Authorization'] = 'Bearer ' + self._token
            # All destination components are fixed and HTTPS; input_token and
            # access_token never reach output, exception strings, or artifacts.
            url = ('https://graph.threads.' + probe.host + '/v1.0/' + resource
                   + '?' + urllib.parse.urlencode(params))
            request = urllib.request.Request(url, headers=headers, method='GET')
            self.request_count += 1
            try:
                with self._opener.open(request, timeout=REQUEST_TIMEOUT) as response:
                    result['http_status'] = safe_integer(response.getcode(), 100, 599)
                    if result['http_status'] is not None and 300 <= result['http_status'] < 400:
                        result['status'] = 'redirect_blocked'
                        return result
                    payload = read_object(response)
            except urllib.error.HTTPError as error:
                result['http_status'] = safe_integer(error.code, 100, 599)
                try:
                    if result['http_status'] is not None and 300 <= result['http_status'] < 400:
                        result['status'] = 'redirect_blocked'
                        return result
                    payload = read_object(error)
                finally:
                    error.close()
            except (urllib.error.URLError, OSError):
                result['status'] = 'transport_error'
                return result

            error = payload.get('error') if isinstance(payload, dict) else None
            if isinstance(error, dict):
                result['api_code'] = safe_integer(error.get('code'))
                result['api_subcode'] = safe_integer(error.get('error_subcode'))
            http_status = result['http_status']
            if http_status is None:
                result['status'] = 'invalid_response'
            elif not 200 <= http_status < 300:
                result['status'] = 'http_error'
            elif not isinstance(payload, dict):
                result['status'] = 'invalid_response'
            elif 'error' in payload:
                result['status'] = 'api_error'
            elif resource == 'me':
                result['account_id_matches'] = id_matches(payload.get('id'), self._expected_id)
                username = payload.get('username')
                if isinstance(username, str) and username:
                    result['account_username_matches'] = username.casefold() == EXPECTED_USERNAME
                matches = (result['account_id_matches'], result['account_username_matches'])
                result['status'] = ('account_verified' if matches == (True, True)
                                    else 'account_mismatch' if False in matches
                                    else 'invalid_response')
            else:
                data = payload.get('data')
                if not isinstance(data, dict):
                    result['status'] = 'invalid_response'
                    return result
                result['status'] = 'token_inspected'
                valid = data.get('is_valid')
                result['is_valid'] = valid if type(valid) is bool else None
                result['user_id_matches'] = id_matches(data.get('user_id'), self._expected_id)
                scopes = data.get('scopes')
                if isinstance(scopes, list) and all(isinstance(scope, str) for scope in scopes):
                    for scope in ('threads_basic', 'threads_content_publish'):
                        result[scope] = scope in scopes
                result['expires'] = expiry_state(data.get('expires_at'), self._now)
                result['data_access_expires'] = expiry_state(data.get('data_access_expires_at'), self._now)
            return result
        except Exception:
            # Suppress raw URLs, messages, headers, and chained exceptions even
            # for unexpected client failures. The caller exits nonzero safely.
            result['status'] = 'internal_error'
            return result


def diagnose(env, opener=None, now=None):
    report = {'schema_version': 1, 'read_only': True, 'status': 'complete',
              'classification': 'no_verified_account_path', 'request_count': 0,
              'request_limit': MAX_REQUESTS, 'original_path_verified': None,
              'verified_alternatives': [], 'probes': [], 'token_debug': None,
              'debug_selection_basis': 'not_requested'}
    token = env.get('SUPPORTPICK_THREADS_ACCESS_TOKEN', '')
    expected_id = env.get('SUPPORTPICK_THREADS_USER_ID', '')
    if (not isinstance(token, str) or not token or len(token) > 16384
            or any(ord(char) < 33 or ord(char) > 126 for char in token)
            or not isinstance(expected_id, str)
            or not re.fullmatch(r'[0-9]{1,64}', expected_id)):
        report.update(status='configuration_incomplete', classification='not_run')
        return report

    client = DiagnosticClient(token, expected_id, opener=opener, now=now)
    stopped = False
    for probe in PROBES:
        result = client.read(probe)
        report['probes'].append(result)
        if result['status'] == 'internal_error':
            report.update(status='internal_error', classification='diagnostic_incomplete')
            stopped = True
        elif result['status'] == 'account_mismatch':
            report['classification'] = 'account_mismatch'
            stopped = True
        elif (result['http_status'] in TEMPORARY_HTTP_STATUSES
              or result['status'] == 'transport_error'):
            report['classification'] = 'inconclusive_temporary_failure'
            stopped = True
        if stopped or (probe == PROBES[0] and result['status'] == 'account_verified'):
            break

    report['original_path_verified'] = report['probes'][0]['status'] == 'account_verified'
    verified = [p for p in report['probes'] if p['status'] == 'account_verified']
    report['verified_alternatives'] = [p['probe'] for p in verified if p['probe'] != PROBES[0].name]
    if not stopped:
        if report['original_path_verified']:
            report['classification'] = 'original_path_verified'
        elif verified:
            report['classification'] = 'original_failed_alternative_verified'
        if verified:
            host = next(p.host for p in PROBES if p.name == verified[0]['probe'])
            report['debug_selection_basis'] = 'verified_account_host_official_query_auth'
        else:
            host = 'com'
            report['debug_selection_basis'] = 'official_sample_host_account_unverified'
        debug_probe = next(p for p in PROBES if p.host == host and p.authentication == 'query')
        debug = client.read(debug_probe, 'debug_token')
        report['token_debug'] = debug
        if debug['status'] == 'internal_error':
            report.update(status='internal_error', classification='diagnostic_incomplete')
        elif debug.get('user_id_matches') is False:
            report['classification'] = 'account_mismatch'
    report['request_count'] = client.request_count
    return report


def summary(report):
    # Every value below was reconstructed from fixed labels, integers or booleans.
    lines = ['## Threads account diagnostic (read only)', '',
             '- Result: ' + report['classification'],
             '- GET requests: ' + str(report['request_count']) + '/' + str(MAX_REQUESTS),
             '- Original path verified: ' + json.dumps(report['original_path_verified']),
             '- Verified alternatives: ' + (', '.join(report['verified_alternatives']) or 'none'),
             '- Self-debug selection: ' + report['debug_selection_basis']]
    lines.extend(['', '| Probe | Result | HTTP | Code | Subcode | ID matches | Username matches |',
                  '| --- | --- | --- | --- | --- | --- | --- |'])
    rows = report['probes'] + ([report['token_debug']] if report['token_debug'] else [])
    for row in rows:
        values = [row['probe'], row['status'], json.dumps(row['http_status']),
                  json.dumps(row['api_code']), json.dumps(row['api_subcode']),
                  json.dumps(row.get('account_id_matches', row.get('user_id_matches'))),
                  json.dumps(row.get('account_username_matches'))]
        lines.append('| ' + ' | '.join(values) + ' |')
    debug = report['token_debug']
    if debug:
        lines.extend(['', '- Self-debug result: ' + debug['status'],
                      '- Token valid: ' + json.dumps(debug['is_valid']),
                      '- Token account matches: ' + json.dumps(debug['user_id_matches']),
                      '- Required scopes: threads_basic=' + json.dumps(debug['threads_basic'])
                      + ', threads_content_publish=' + json.dumps(debug['threads_content_publish']),
                      '- Token expiry: ' + debug['expires'],
                      '- Data access expiry: ' + debug['data_access_expires']])
    lines.extend(['', 'Alternative success records an observed difference; it does not change the publisher.',
                  'A failed self-debug request leaves token validity and permissions unknown.', ''])
    return '\n'.join(lines)


def main(env=None, opener=None, output_dir=None, now=None):
    env = os.environ if env is None else env
    try:
        report = diagnose(env, opener=opener, now=now)
        rendered = summary(report)
        output = (Path.cwd() if output_dir is None else Path(output_dir)) / REPORT_NAME
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        summary_file = env.get('GITHUB_STEP_SUMMARY')
        if summary_file:
            with open(summary_file, 'a', encoding='utf-8') as stream:
                stream.write(rendered)
        print(rendered)
        return 0 if report['status'] == 'complete' else 1
    except Exception:
        print('Threads account diagnostic could not complete: internal_error.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
