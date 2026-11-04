import copy
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import release_policy as policy

class ReleasePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); (self.root / 'tools').mkdir()
        for name in ('index.html', 'guides.json', 'editorials.json', 'search-verification.json', 'tools/build.py'):
            (self.root / name).write_text('{}')
        self.row = {'id': 'B1', 'title': '혜택', 'support': '공식 금액', 'checkedAt': '2026-11-04T09:00:00+09:00',
                    'dataCollectedAt': 'morning', 'generation': 'g1', 'factsVerifiedAt': None,
                    'sourceUpdatedAt': {'detail': '20261103'}, 'rawSource': {'serviceList': {'조회수': 10}}}
        self.args = {'feed': {'generation': 'g1', 'detailBase': 'details/g1/', 'updatedAt': 'morning',
                             'collectionSucceededAt': 'morning', 'items': [copy.deepcopy(self.row)]},
                     'rows': {'B1': copy.deepcopy(self.row)}, 'previous': {'B1': copy.deepcopy(self.row)},
                     'status': {'status': 'success', 'generation': 'g1', 'lastSuccessAt': 'morning'},
                     'search': {'sourceGeneration': 'g1', 'reviewedGuides': 1},
                     'static': ['index.html'], 'current': datetime(2026, 11, 4, 0, tzinfo=timezone.utc)}
    def signature(self, args=None): return policy.fingerprint(self.root, **(args or self.args))
    def test_collection_clocks_and_generation_only_do_not_redeploy(self):
        changed = copy.deepcopy(self.args)
        for item in (changed['feed'], *changed['feed']['items'], *changed['rows'].values(), *changed['previous'].values(), changed['status'], changed['search']):
            for key in ('generation', 'sourceGeneration', 'checkedAt', 'dataCollectedAt', 'updatedAt', 'collectionSucceededAt', 'lastSuccessAt'):
                if key in item: item[key] = 'new-query-time-or-generation'
        changed['feed']['detailBase'] = 'details/g2/'
        self.assertEqual(self.signature(), self.signature(changed))
    def test_changed_official_facts_views_and_verification_always_publish(self):
        for key, value in [('support', '변경된 공식 금액'), ('period', '다른 기한'),
                           ('target', '다른 대상'), ('sourceUpdatedAt', {'detail': '20261104'}),
                           ('factsVerifiedAt', '2026-11-04'), ('rawSource', {'serviceList': {'조회수': 11}})]:
            changed = copy.deepcopy(self.args); changed['rows']['B1'][key] = value
            with self.subTest(key=key): self.assertNotEqual(self.signature(), self.signature(changed))
    def test_new_day_failure_holds_and_retired_ids_always_publish(self):
        alternatives = []
        for key, value in [('current', datetime(2026, 11, 5, 0, tzinfo=timezone.utc)),
                           ('status', {'status': 'failed', 'errorCode': 'api_failure'}),
                           ('search', {'sourceGeneration': 'g1', 'reviewedGuides': 0}),
                           ('previous', {})]:
            changed = copy.deepcopy(self.args); changed[key] = value; alternatives.append(changed)
        for changed in alternatives: self.assertNotEqual(self.signature(), self.signature(changed))
    def test_code_or_asset_change_publishes(self):
        previous = self.signature(); (self.root / 'index.html').write_text('changed')
        self.assertNotEqual(previous, self.signature())
        previous = self.signature(); (self.root / 'tools/build.py').write_text('changed')
        self.assertNotEqual(previous, self.signature())
    def remote(self, matching=True, broken=False):
        body = b'previous verified public bytes'
        files = {p: hashlib.sha256(body).hexdigest() for p in ('index.html', 'sitemap.xml', 'status.json', 'benefits/B1/index.html')}
        manifest = {'contentFingerprint': 'a' * 64 if matching else 'b' * 64, 'generation': 'older-public',
                    'sourceRevision': 'older-code', 'files': files}
        def loader(path):
            if path == 'site-manifest.json': return json.dumps(manifest).encode()
            return b'corrupted' if broken and path == 'sitemap.xml' else body
        return loader
    def test_matching_healthy_release_retains_actual_public_generation(self):
        result = policy.decide({'contentFingerprint': 'a' * 64, 'generation': 'new-raw', 'sourceRevision': 'new-code'}, self.remote())
        self.assertFalse(result['publish']); self.assertEqual(len(result['probes']), 4)
        self.assertEqual(result['observedPublic']['generation'], 'older-public')
        self.assertEqual(result['candidateGeneration'], 'new-raw')
    def test_changed_missing_corrupt_or_unreachable_public_release_never_skips(self):
        candidate = {'contentFingerprint': 'a' * 64, 'generation': 'g2', 'sourceRevision': 'code'}
        def offline(path): raise TimeoutError()
        for loader in (self.remote(False), self.remote(broken=True), lambda p: b'{}', offline):
            self.assertTrue(policy.decide(candidate, loader)['publish'])
    def test_invalid_candidate_cannot_silently_skip(self):
        with self.assertRaises(ValueError): policy.decide({'generation': 'g2', 'sourceRevision': 'code'})

if __name__ == '__main__': unittest.main()
