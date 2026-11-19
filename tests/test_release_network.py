import hashlib
import json
from contextlib import redirect_stdout
from io import StringIO
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_release import verify_targets, inspect, wait_for_public_manifest, PublicRequestPacer, open_public

URL='https://kllollain-max.github.io/supportpick/about.html'
BODY=('<html><head><link rel="canonical" href="'+URL+'"><meta name="robots" content="index,follow">'
      '<title>안내</title><meta name="description" content="안내"><meta property="og:title" content="안내">'
      '</head><body><h1>안내</h1></body></html>').encode()


class Response:
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return BODY


class PublicNetworkVerification(unittest.TestCase):
    def fake_pacer(self):
        now=[0.0]
        def sleep(seconds):now[0]+=seconds
        return PublicRequestPacer(clock=lambda:now[0],sleep=sleep),now

    def test_request_starts_are_spaced_and_share_a_server_cooldown(self):
        pacer,now=self.fake_pacer()
        self.assertTrue(pacer.wait());self.assertEqual(now[0],0)
        self.assertTrue(pacer.wait());self.assertAlmostEqual(now[0],0.1)
        with redirect_stdout(StringIO()):pacer.limited({'Retry-After':'120'})
        self.assertTrue(pacer.wait());self.assertGreaterEqual(now[0],120.1)

    def test_repeated_limits_stop_requests_instead_of_draining_a_large_queue(self):
        pacer,now=self.fake_pacer()
        with redirect_stdout(StringIO()):
            for _ in range(3):
                pacer.limited({});self.assertTrue(pacer.wait())
            pacer.limited({})
        self.assertTrue(pacer.stopped)
        with patch('verify_release.urlopen') as fetch:
            report=verify_targets(self.target(),{URL},1,pacer)
        fetch.assert_not_called()
        self.assertEqual(report['failed'],1)
        self.assertTrue(report['stoppedForRateLimit'])

    def test_429_recovery_waits_then_still_checks_the_actual_body(self):
        pacer,now=self.fake_pacer()
        with patch('verify_release.urlopen',side_effect=[HTTPError(URL,429,'slow down',{'Retry-After':'90'},None),Response()]),redirect_stdout(StringIO()):
            report=verify_targets(self.target(),{URL},1,pacer)
        self.assertGreaterEqual(now[0],90)
        self.assertEqual(report['passed'],1)
        self.assertEqual(report['rateLimitEpisodes'],1)
        self.assertEqual(report['failed'],0)

    def test_retry_after_http_date_and_invalid_nonfinite_values_are_bounded(self):
        from datetime import datetime, timezone
        pacer,now=self.fake_pacer()
        with patch('verify_release.datetime') as date,redirect_stdout(StringIO()):
            date.now.return_value=datetime(2026,11,17,0,0,tzinfo=timezone.utc)
            pacer.limited({'Retry-After':'Tue, 17 Nov 2026 00:02:00 GMT'})
        self.assertTrue(pacer.wait());self.assertGreaterEqual(now[0],120)
        for value in ['inf','NaN','invalid']:
            pacer,now=self.fake_pacer()
            with redirect_stdout(StringIO()):pacer.limited({'Retry-After':value})
            self.assertTrue(pacer.wait());self.assertEqual(now[0],60)

    def test_auxiliary_404_probe_obeys_limits_and_preserves_the_real_404(self):
        pacer,now=self.fake_pacer()
        with patch('verify_release.urlopen',side_effect=[HTTPError(URL,429,'slow down',{},None),HTTPError(URL,404,'missing',{},None)]) as fetch,redirect_stdout(StringIO()),self.assertRaises(HTTPError) as error:
            open_public(URL,pacer)
        self.assertEqual(error.exception.code,404)
        self.assertEqual(fetch.call_count,2)
        self.assertGreaterEqual(now[0],60)

    def test_bot_specific_and_duplicate_meta_cannot_hide_noindex(self):
        for name, value in [('googlebot', 'noindex'), ('Googlebot', 'NONE'), ('robots', 'none')]:
            text = BODY.decode().replace('</head>', '<meta name="'+name+'" content="'+value+'"></head>')
            # A later permissive tag must not erase an earlier restriction.
            text = text.replace('</head>', '<meta name="robots" content="index,follow"></head>')
            with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, 'conflicting_noindex'):
                inspect(text, URL)

    def test_header_noindex_is_failed_without_retry(self):
        from email.message import Message
        for value, blocked in [('noindex', True), ('googlebot: none', True), ('max-image-preview:none', False)]:
            response = Response(); response.headers = Message()
            response.headers.add_header('X-Robots-Tag', value)
            with patch('verify_release.urlopen', return_value=response) as fetch:
                report = verify_targets(self.target(), {URL}, 1)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(report['failed'], int(blocked))

    def target(self,digest=None):
        return [(URL,'about.html',digest or hashlib.sha256(BODY).hexdigest())]

    def test_one_transient_503_can_recover_only_after_a_real_successful_content_check(self):
        with patch('verify_release.urlopen',side_effect=[HTTPError(URL,503,'temporary',{},None),Response()]) as fetch:
            report=verify_targets(self.target(),{URL},1)
        self.assertEqual(fetch.call_count,2)
        self.assertEqual(report['initialFailures'],1)
        self.assertEqual(report['failed'],0)
        self.assertEqual(report['passed'],1)
        self.assertEqual(report['recoveredAfterRetry'][0]['retryHttp'],200)

    def test_persistent_503_stays_failed_and_missing_404_is_not_retried(self):
        for code,calls in [(503,2),(404,1)]:
            with patch('verify_release.urlopen',side_effect=HTTPError(URL,code,'error',{},None)) as fetch:
                report=verify_targets(self.target(),{URL},1)
            self.assertEqual(fetch.call_count,calls)
            self.assertEqual(report['failed'],1)
            self.assertEqual(report['passed'],0)

    def test_content_mismatch_is_never_retried_or_hidden_by_a_success_status(self):
        with patch('verify_release.urlopen',return_value=Response()) as fetch:
            report=verify_targets(self.target('wrong_digest'),{URL},1)
        self.assertEqual(fetch.call_count,1)
        self.assertEqual(report['failed'],1)
        self.assertEqual(report['failures'][0]['error'],'content_hash_mismatch')

    def test_old_public_generation_can_converge_before_crawl(self):
        expected = {'sourceRevision': 'source', 'generation': 'new', 'files': {'index.html': 'hash'}}
        stale = {**expected, 'generation': 'old'}
        output = StringIO()
        with patch('verify_release.read_public_manifest', side_effect=[stale, expected]) as fetch, \
                patch('verify_release.time.sleep') as pause, redirect_stdout(output):
            self.assertEqual(wait_for_public_manifest(expected, 'source', 'new'), expected)
        self.assertEqual(fetch.call_count, 2)
        pause.assert_called_once_with(30)
        self.assertEqual([json.loads(line)['observedGeneration'] for line in output.getvalue().splitlines()],
                         ['old', 'new'])

    def test_stale_generation_and_same_generation_file_mismatch_stay_failures(self):
        expected = {'sourceRevision': 'source', 'generation': 'new', 'files': {'index.html': 'hash'}}
        for public, error, calls in [
            ({**expected, 'generation': 'old'}, 'public_generation_mismatch', 2),
            ({**expected, 'files': {'index.html': 'wrong'}}, 'public_manifest_files_mismatch', 1),
        ]:
            with self.subTest(error=error), patch('verify_release.read_public_manifest', return_value=public) as fetch, \
                    patch('verify_release.time.sleep'), redirect_stdout(StringIO()), \
                    self.assertRaisesRegex(ValueError, error):
                wait_for_public_manifest(expected, 'source', 'new')
            self.assertEqual(fetch.call_count, calls)
