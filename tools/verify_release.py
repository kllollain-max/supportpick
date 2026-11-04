"""Validate every advertised static URL; optionally verify the actual public release."""
import argparse
import hashlib
import json
import re
from publication import wait_manifest, verify_data_release, read_public, PublicationError
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


class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1 = 0; self.meta = {}; self.canonical = []
        self.jsonld = []; self.active = None; self.buffer = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if tag == 'meta': self.meta[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.active = True; self.buffer = ''
    def handle_data(self, value):
        if self.active: self.buffer += value
    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            self.jsonld.append(json.loads(self.buffer)); self.active = None


def inspect(html, url):
    doc = Document(); doc.feed(html)
    if doc.canonical != [url]: raise ValueError('canonical_mismatch:' + url)
    if doc.meta.get('robots') != 'index,follow': raise ValueError('not_indexable:' + url)
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
    for url in urls:
        name = unquote(url[len(BASE):])
        target = output / (name + 'index.html' if not name or name.endswith('/') else name)
        if not target.is_file(): raise ValueError('sitemap_target_missing')
        inspect(target.read_text(), url)
    for sid in report['heldReasons']:
        html = (output / 'benefits' / sid / 'index.html').read_text()
        if 'content="noindex,follow"' not in html or BASE + 'benefits/' + sid + '/' in urls:
            raise ValueError('held_page_advertised')
    return {'sitemapUrls': len(urls), 'validatedUrls': len(urls),
            **{k: report[k] for k in ('detailPages', 'indexableDetails', 'heldDetails', 'reviewedGuides', 'blogLinks', 'directoryPages', 'retiredPages')}}


def fetch_html(entry, url_set):
    url, name, digest = entry
    try:
        with urlopen(Request(url, headers={'User-Agent': 'SupportPick-Release-Verification/1.0'}), timeout=30) as response:
            raw = response.read()
            if response.status != 200:
                return url, 'http_' + str(response.status), response.status in (408,429,500,502,503,504)
            if hashlib.sha256(raw).hexdigest() != digest:
                return url, 'content_hash_mismatch', False
            if url in url_set:
                inspect(raw.decode('utf-8'), url)
            return url, None, False
    except HTTPError as error:
        return url, str(error), error.code in (408,429,500,502,503,504)
    except (URLError, TimeoutError) as error:
        return url, str(error)[:180], True
    except Exception as error:
        return url, str(error)[:180], False


def verify_targets(targets, url_set, workers):
    failures=[];passed=0;by_url={entry[0]:entry for entry in targets}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs=[pool.submit(fetch_html,entry,url_set) for entry in targets]
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
            url,error,_=fetch_html(by_url[failure['url']],url_set)
            if error is None:
                passed+=1;recovered.append({'url':url,'initialError':failure['error'],'retryHttp':200})
                continue
            failure['retryError']=error
        remaining.append({k:v for k,v in failure.items() if k!='retryable'})
    return {'passed':passed,'failed':len(remaining),'initialFailures':initial_failures,
            'recoveredAfterRetry':recovered,'failures':remaining}


def live_check(output, workers=6, expected_revision=None, expected_generation=None):
    output = Path(output)
    local = json.loads((output / 'site-manifest.json').read_text())
    if expected_revision and local.get('sourceRevision')!=expected_revision: raise ValueError('local_revision_expectation_mismatch')
    if expected_generation and local.get('generation')!=expected_generation: raise ValueError('local_generation_expectation_mismatch')
    expected,observations=wait_manifest(local)
    consistency=verify_data_release(expected)
    for name in ('app.js','core.js','detail.js','styles.css'):
        if expected['files'].get(name)!=local['files'].get(name):
            raise ValueError('public_application_code_mismatch:'+name)
    with urlopen(BASE+'sitemap.xml',timeout=30) as response:
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
    checked=verify_targets(targets,set(urls),workers)
    missing=BASE+'benefits/__supportpick_missing_release_check__/'
    try:
        with urlopen(missing,timeout=30) as response:
            raise ValueError('missing_page_not_404')
    except HTTPError as error:
        if error.code!=404: raise
        if '페이지를 찾을 수 없습니다' not in error.read().decode('utf-8'):
            raise ValueError('custom_404_not_present')
    robots_url='https://kllollain-max.github.io/robots.txt'
    try:
        with urlopen(robots_url,timeout=30) as response:
            robot=RobotFileParser();robot.parse(response.read().decode('utf-8').splitlines())
            if any(not robot.can_fetch(bot,BASE+'benefits/149200000026/') for bot in ('Googlebot','Yeti')):
                raise ValueError('root_robots_blocks_crawling')
            robots={'http':response.status,'crawlAllowed':True,'scope':'host_root'}
    except HTTPError as error:
        if error.code!=404:raise
        robots={'http':404,'crawlAllowed':True,'scope':'host_root','note':'Absent robots file; no robots prohibition.'}
    final=json.loads(read_public('site-manifest.json'))
    if final!=expected:raise PublicationError('public_release_changed_during_check',{'stage':'final_barrier','failed':1})
    return {'publicationObservations':observations,'dataConsistency':consistency,'publicHtmlChecked': len(targets), 'sitemapUrls':len(urls), 'generation':expected['generation'],
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
    except PublicationError as error:
        result={'error':str(error),**error.report}
        if args.report:
            Path(args.report).parent.mkdir(parents=True,exist_ok=True);Path(args.report).write_text(json.dumps(result,ensure_ascii=False,indent=2))
        print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(1)
    if args.report: Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('failed'): raise SystemExit(1)
