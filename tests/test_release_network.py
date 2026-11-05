import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_release import verify_targets, inspect

URL='https://kllollain-max.github.io/supportpick/about.html'
BODY=('<html><head><link rel="canonical" href="'+URL+'"><meta name="robots" content="index,follow">'
      '<meta name="description" content="안내"><meta property="og:title" content="안내">'
      '</head><body><h1>안내</h1></body></html>').encode()


class Response:
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return BODY


class PublicNetworkVerification(unittest.TestCase):
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
