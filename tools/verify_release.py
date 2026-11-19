"""Validate every advertised static URL; optionally verify the actual public release."""
import argparse
import hashlib
import json
import re
import time
import threading
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET

BASE = 'https://kllollain-max.github.io/supportpick/'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


class PublicRequestPacer:
    """Share a ten-request/second ceiling and server cooldown across workers."""
    def __init__(self, clock=None, sleep=None):
        self.clock = clock or time.monotonic
        self.sleep = sleep or time.sleep
        self.lock = threading.Lock()
        self.next_request = self.cool_until = 0
        self.episodes = 0
        self.stopped = False

    def wait(self):
        while True:
            with self.lock:
                if self.stopped:
                    return False
                now = self.clock()
                delay = max(self.next_request, self.cool_until) - now
                if delay <= 0:
                    self.next_request = now + 0.1
                    return True
            self.sleep(min(delay, 1))

    def limited(self, headers):
        raw = (headers or {}).get('Retry-After', '')
        try:
            delay = max(0, int(raw))
        except (ValueError, TypeError):
            try:
                date = parsedate_to_datetime(raw)
                delay = max(0, (date - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError, OverflowError):
                delay = 0
        with self.lock:
            now = self.clock()
            if now >= self.cool_until:
                self.episodes += 1
                if self.episodes > 3:
                    self.stopped = True
                    return
                print(json.dumps({'publicRateLimit': 'cooldown', 'episode': self.episodes,
                                  'seconds': max(delay, 60 * 2 ** (self.episodes - 1))}), flush=True)
            self.cool_until = max(self.cool_until, now + max(delay, 60 * 2 ** (self.episodes - 1)))


def open_public(request, pacer):
    """Use the same cooldown for manifest, sitemap, robots and 404 probes."""
    for attempt in range(4):
        if not pacer.wait():
            raise ValueError('public_request_limit_stopped')
        try:
            return urlopen(request, timeout=30)
        except HTTPError as error:
            if error.code == 429:
                pacer.limited(error.headers)
                if attempt < 3:
                    continue
            elif error.code in (408,500,502,503,504) and attempt == 0:
                time.sleep(1)
                continue
            raise


class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1 = 0; self.meta = {}; self.canonical = []
        self.jsonld = []; self.active = None; self.buffer = ''; self.robots = []
        self.title = ''; self.title_count = 0; self.in_title = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.title_count += 1; self.in_title = True
        if tag == 'h1': self.h1 += 1
        if tag == 'meta': self.meta[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'meta' and a.get('name', '').lower() in {'robots', 'googlebot'}:
            self.robots.append(a.get('content', '').lower())
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.active = True; self.buffer = ''
    def handle_data(self, value):
        if self.active: self.buffer += value
        if self.in_title: self.title += value
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.active:
            self.jsonld.append(json.loads(self.buffer)); self.active = None


def inspect(html, url):
    doc = Document(); doc.feed(html)
    if doc.title_count != 1 or not doc.title.strip(): raise ValueError('invalid_title:' + url)
    if doc.canonical != [url]: raise ValueError('canonical_mismatch:' + url)
    if doc.meta.get('robots') != 'index,follow': raise ValueError('not_indexable:' + url)
    if any({'noindex', 'none'} & set(re.split(r'[\s,]+', value)) for value in doc.robots):
        raise ValueError('conflicting_noindex:' + url)
    if not doc.meta.get('description') or not doc.meta.get('og:title'): raise ValueError('missing_metadata:' + url)
    if doc.h1 != 1: raise ValueError('invalid_h1:' + url)
    if '/benefits/' in url and '/page/' not in url and url != BASE + 'benefits/':
        breadcrumbs = [d for d in doc.jsonld if d.get('@type') == 'BreadcrumbList']
        if len(breadcrumbs) != 1: raise ValueError('missing_breadcrumbs:' + url)
        trail = breadcrumbs[0]['itemListElement']
        if [x['position'] for x in trail] != [1, 2, 3] or trail[-1]['item'] != url:
            raise ValueError('invalid_breadcrumbs:' + url)
    return doc


def local_urls(output):
    entries = ET.parse(output / 'sitemap.xml').findall('s:url', NS)
    urls = [e.find('s:loc', NS).text for e in entries]
    if len(urls) != len(set(urls)) or not urls: raise ValueError('sitemap_duplicate_or_empty')
    for url in urls:
        if not url.startswith(BASE) or urlsplit(url).query or urlsplit(url).fragment:
            raise ValueError('unsafe_sitemap_url')
    return urls


def verify(output):
    output = Path(output); urls = local_urls(output)
    report = json.loads((output / 'search-report.json').read_text())
    titles = {}
    for url in urls:
        name = unquote(url[len(BASE):])
        target = output / (name + 'index.html' if not name or name.endswith('/') else name)
        if not target.is_file(): raise ValueError('sitemap_target_missing')
        doc = inspect(target.read_text(), url)
        key = re.sub(r'\s+', ' ', doc.title).strip().casefold()
        if key in titles: raise ValueError('duplicate_document_title:' + titles[key] + ':' + url)
        titles[key] = url
    for sid in report['heldReasons']:
        html = (output / 'benefits' / sid / 'index.html').read_text()
        if 'content="noindex,follow"' not in html or BASE + 'benefits/' + sid + '/' in urls:
            raise ValueError('held_page_advertised')
    return {'sitemapUrls': len(urls), 'validatedUrls': len(urls), 'uniqueTitles': len(titles),
            **{k: report[k] for k in ('detailPages', 'indexableDetails', 'heldDetails', 'reviewedGuides', 'blogLinks', 'directoryPages', 'retiredPages')}}


def fetch_html(entry, url_set, pacer=None):
    url, name, digest = entry
    if pacer and not pacer.wait():
        return url, 'request_limit_scan_stopped', False
    try:
        with urlopen(Request(url, headers={'User-Agent': 'SupportPick-Release-Verification/1.0'}), timeout=30) as response:
            raw = response.read()
            if response.status != 200:
                return url, 'http_' + str(response.status), response.status in (408,429,500,502,503,504)
            if hashlib.sha256(raw).hexdigest() != digest:
                return url, 'content_hash_mismatch', False
            if url in url_set:
                values = response.headers.get_all('X-Robots-Tag', []) if hasattr(response, 'headers') else []
                if any({'noindex', 'none'} & set(re.split(r'[\s,]+', value.lower())) for value in values):
                    return url, 'header_noindex', False
                inspect(raw.decode('utf-8'), url)
            return url, None, False
    except HTTPError as error:
        if error.code == 429 and pacer:
            pacer.limited(error.headers)
        return url, str(error), error.code in (408,429,500,502,503,504)
    except (URLError, TimeoutError) as error:
        return url, str(error)[:180], True
    except Exception as error:
        return url, str(error)[:180], False


def verify_targets(targets, url_set, workers, pacer=None):
    pacer = pacer or PublicRequestPacer()
    failures=[];passed=0;by_url={entry[0]:entry for entry in targets}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs=[pool.submit(fetch_html,entry,url_set,pacer) for entry in targets]
        for future in as_completed(jobs):
            url,error,retryable=future.result()
            if error:failures.append({'url':url,'error':error,'retryable':retryable})
            else:passed+=1
            if (passed+len(failures))%500==0:
                print(json.dumps({'checked':passed+len(failures),'total':len(targets),'failed':len(failures)}),flush=True)
    initial_failures=len(failures);remaining=[];recovered=[]
    # Retry each transient transport/service response once, sequentially, after
    # the full pass. Missing pages, metadata and content mismatches remain errors.
    for failure in failures:
        if failure['retryable']:
            url,error,_=fetch_html(by_url[failure['url']],url_set,pacer)
            if error is None:
                passed+=1;recovered.append({'url':url,'initialError':failure['error'],'retryHttp':200})
                continue
            failure['retryError']=error
        remaining.append({k:v for k,v in failure.items() if k!='retryable'})
    return {'passed':passed,'failed':len(remaining),'initialFailures':initial_failures,
            'maxRequestsPerSecond':10,'rateLimitEpisodes':pacer.episodes,
            'stoppedForRateLimit':pacer.stopped,
            'recoveredAfterRetry':recovered,'failures':remaining}


def read_public_manifest(pacer=None):
    request = Request(BASE + 'site-manifest.json', headers={'Cache-Control': 'no-cache'})
    with (open_public(request,pacer) if pacer else urlopen(request,timeout=30)) as response:
        return json.load(response)


def wait_for_public_manifest(local, expected_revision, expected_generation, pacer=None):
    revision = expected_revision or local['sourceRevision']
    generation = expected_generation or local['generation']
    if (local['sourceRevision'], local['generation']) != (revision, generation):
        raise ValueError('local_release_expectation_mismatch')

    for attempt in (1, 2):
        public = read_public_manifest(pacer) if pacer else read_public_manifest()
        observed = (public['sourceRevision'], public['generation'])
        print(json.dumps({'manifestAttempt': attempt,
                          'expectedRevision': revision, 'expectedGeneration': generation,
                          'observedRevision': observed[0], 'observedGeneration': observed[1]}), flush=True)
        if observed == (revision, generation):
            if public['files'] != local['files']:
                raise ValueError('public_manifest_files_mismatch')
            return public
        if attempt == 1:
            # Pages may acknowledge deployment before the public edge serves it.
            # Wait once before starting the crawl, without retrying page errors.
            time.sleep(30)
    reason = 'public_revision_mismatch' if observed[0] != revision else 'public_generation_mismatch'
    print(json.dumps({'publicReleaseVerification': 'blocked', 'reason': reason,
                      'expectedRevision': revision, 'expectedGeneration': generation,
                      'observedRevision': observed[0], 'observedGeneration': observed[1],
                      'manifestAttempts': 2}), flush=True)
    raise ValueError(reason)


def live_check(output, workers=6, expected_revision=None, expected_generation=None):
    output = Path(output)
    local = json.loads((output / 'site-manifest.json').read_text())
    pacer = PublicRequestPacer()
    expected = wait_for_public_manifest(local, expected_revision, expected_generation,pacer)
    for name in ('app.js','core.js','detail.js','styles.css'):
        if expected['files'].get(name)!=local['files'].get(name):
            raise ValueError('public_application_code_mismatch:'+name)
    with open_public(BASE+'sitemap.xml',pacer) as response:
        raw=response.read()
    if hashlib.sha256(raw).hexdigest()!=expected['files']['sitemap.xml']:
        raise ValueError('public_sitemap_hash_mismatch')
    urls=[e.text for e in ET.fromstring(raw).findall('s:url/s:loc',NS)]
    if len(urls)!=len(set(urls)) or any(not u.startswith(BASE) for u in urls):
        raise ValueError('unsafe_public_sitemap')
    # Include held pages: direct sharing must keep working, while indexing remains withheld.
    targets = [(BASE + name.removesuffix('index.html'), name, sha)
               for name, sha in expected['files'].items() if name.endswith('.html') and name != '404.html'
               and re.fullmatch(r'[A-Za-z0-9_/-]+\.html',name) and '..' not in name]
    checked=verify_targets(targets,set(urls),workers,pacer)
    # Do not add requests after a persistent limit, or lose the completed scan
    # report to a later robots/404 request. A blocked scan must stay a failure.
    if checked['stoppedForRateLimit']:
        return {'publicHtmlChecked':len(targets),'sitemapUrls':len(urls),
                'generation':expected['generation'],'sourceRevision':expected['sourceRevision'],
                'missingUrlHttp':None,'robots':{'status':'not_checked_after_rate_limit'},**checked}
    missing=BASE+'benefits/__supportpick_missing_release_check__/'
    try:
        with open_public(missing,pacer) as response:
            raise ValueError('missing_page_not_404')
    except HTTPError as error:
        if error.code!=404: raise
        if '페이지를 찾을 수 없습니다' not in error.read().decode('utf-8'):
            raise ValueError('custom_404_not_present')
    robots_url='https://kllollain-max.github.io/robots.txt'
    try:
        with open_public(robots_url,pacer) as response:
            robot=RobotFileParser();robot.parse(response.read().decode('utf-8').splitlines())
            if any(not robot.can_fetch(bot,BASE+'benefits/149200000026/') for bot in ('Googlebot','Yeti')):
                raise ValueError('root_robots_blocks_crawling')
            robots={'http':response.status,'crawlAllowed':True,'scope':'host_root'}
    except HTTPError as error:
        if error.code!=404:raise
        robots={'http':404,'crawlAllowed':True,'scope':'host_root','note':'Absent robots file; no robots prohibition.'}
    return {'publicHtmlChecked': len(targets), 'sitemapUrls':len(urls), 'generation':expected['generation'],
            'sourceRevision':expected.get('sourceRevision'),'robots':robots,'missingUrlHttp':404,**checked}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True); parser.add_argument('--live', action='store_true')
    parser.add_argument('--workers', type=int, default=6); parser.add_argument('--report')
    parser.add_argument('--expect-sha')
    parser.add_argument('--expect-generation')
    args = parser.parse_args()
    try:
        result = live_check(args.output, args.workers,args.expect_sha,args.expect_generation) if args.live else verify(args.output)
    except Exception as error:
        result = {'failed':1,'verificationError':str(error),
                  'publicReleaseVerification':'incomplete' if args.live else 'failed'}
    if args.report: Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('failed'): raise SystemExit(1)
