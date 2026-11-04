"""Skip identical same-day releases while retaining every validated raw generation.

Published query timestamps stay truthful: a skipped release keeps the previous
public generation and its actual query time. Daily rebuilds, source facts,
verification/hold changes, failure status and code changes always publish.
"""
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = 'https://kllollain-max.github.io/supportpick/'
LIMIT = 3 * 1024 * 1024

def fingerprint(root, feed, rows, previous, status, search, static, current=None):
    root = Path(root)
    current = current or datetime.now(timezone.utc)
    def row(value):
        return {k: v for k, v in value.items() if k not in ('generation', 'checkedAt', 'dataCollectedAt')}
    source = {k: v for k, v in feed.items() if k not in ('items', 'generation', 'detailBase', 'updatedAt', 'collectionSucceededAt')}
    source['items'] = sorted((row(item) for item in feed['items']), key=lambda item: item['id'])
    paths = sorted(set(static) | {'guides.json', 'editorials.json', 'search-verification.json'} |
                   {str(p.relative_to(root)) for p in (root / 'tools').glob('*.py')})
    files = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in paths}
    value = {'version': 1, 'kstDay': current.astimezone(ZoneInfo('Asia/Seoul')).date().isoformat(),
             'files': files, 'source': source,
             'details': {sid: row(value) for sid, value in rows.items()},
             'previous': {sid: row(value) for sid, value in previous.items()},
             'status': {k: v for k, v in status.items() if k not in ('generation', 'lastAttemptAt', 'lastSuccessAt', 'published')},
             'search': {k: v for k, v in search.items() if k != 'sourceGeneration'}}
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()

def fetch(path):
    request = Request(BASE + path, headers={'User-Agent': 'SupportPick-Release-Check/1.0'})
    with urlopen(request, timeout=15) as response:
        if response.status != 200 or response.url != BASE + path:
            raise ValueError('public_probe_response_mismatch')
        raw = response.read(LIMIT + 1)
        if len(raw) > LIMIT: raise ValueError('public_probe_too_large')
        return raw

def decide(candidate, loader=fetch):
    decision = {'publish': True, 'reason': 'no_matching_verified_public_release',
                'candidateGeneration': candidate['generation'],
                'candidateSourceRevision': candidate['sourceRevision'], 'probes': []}
    expected = candidate.get('contentFingerprint')
    if not re.fullmatch(r'[a-f0-9]{64}', expected or ''):
        raise ValueError('candidate_fingerprint_missing')
    try:
        remote = json.loads(loader('site-manifest.json'))
        decision['observedPublic'] = {k: remote.get(k) for k in ('sourceRevision', 'generation', 'contentFingerprint')}
        if remote.get('contentFingerprint') != expected: return decision
        files = remote.get('files', {})
        details = sorted(p for p in files if re.fullmatch(r'benefits/[A-Za-z0-9_-]{1,80}/index\.html', p))
        if not details: raise ValueError('public_detail_probe_missing')
        for path in ('index.html', 'sitemap.xml', 'status.json', details[0]):
            digest = files.get(path)
            if not re.fullmatch(r'[a-f0-9]{64}', digest or ''): raise ValueError('public_hash_missing')
            actual = hashlib.sha256(loader(path)).hexdigest()
            decision['probes'].append({'path': path, 'hashMatches': actual == digest})
            if actual != digest: raise ValueError('public_hash_mismatch')
        decision.update(publish=False, reason='same_day_content_unchanged_public_generation_retained')
    except Exception as error:
        # An uncertain probe never authorizes skipping. Normal build/verification
        # and deployment gates still apply; the last good site is not removed.
        decision['reason'] = 'publish_required_' + type(error).__name__
    return decision

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('dist'))
    parser.add_argument('--report', type=Path, default=Path('output/publish-decision.json'))
    args = parser.parse_args()
    result = decide(json.loads((args.output / 'site-manifest.json').read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            stream.write('publish=' + str(result['publish']).lower() + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
