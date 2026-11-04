"""Static benefit documents from validated source editions, without client rendering."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo

from collect_full import safe_url, valid_id
from search_metadata import public_metadata

KST = ZoneInfo('Asia/Seoul')
TEMPLATE_MODIFIED = '2026-11-04'
PAGE_SIZE = 100
MATERIAL_FIELDS = ('id', 'title', 'organization', 'category', 'region', 'regionBasis',
                   'summary', 'target', 'selection', 'support', 'period', 'periodKind',
                   'startDate', 'endDate', 'method', 'documents', 'contact',
                   'officialUrl', 'applicationUrl', 'supportType', 'sourceConflicts')
CRITICAL_CONFLICTS = {'서비스명', '소관기관명', '지원대상', '지원내용', '신청기한'}


def payload(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def material_hash(row):
    return hashlib.sha256(payload({k: row.get(k) for k in MATERIAL_FIELDS}).encode()).hexdigest()


def benefit_path(sid):
    if not valid_id(sid) or sid in {'__proto__', 'prototype', 'constructor'}:
        raise ValueError('unsafe_benefit_id')
    return 'benefits/' + quote(sid, safe='') + '/'


def source_date(row):
    values = row.get('sourceUpdatedAt') or {}
    if not isinstance(values, dict):
        values = {'source': values}
    dates = []
    for value in values.values():
        raw = str(value or '')
        for fmt in ('%Y%m%d%H%M%S', '%Y-%m-%d', '%Y%m%d'):
            try:
                date = datetime.strptime(raw, fmt).date()
                if date <= datetime.now(KST).date():
                    dates.append(date.isoformat())
                break
            except ValueError:
                continue
    return max(dates) if dates else None


def view_count(row):
    value = row.get('rawSource', {}).get('serviceList', {}).get('조회수')
    if type(value) is int and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r'\d{1,15}', value):
        return int(value)
    return None


def popularity(row):
    count = view_count(row)
    return (count is None, -(count or 0), row.get('endDate') or '9999', row['id'])


def status(row, current):
    today = current.astimezone(KST).date().isoformat()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', row.get('endDate') or '') and row['endDate'] < today:
        return '안내 기한 경과 · 새 공고 확인'
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', row.get('startDate') or '') and row['startDate'] > today:
        return '안내 기간 전 · 접수일 확인'
    if row.get('periodKind') == 'ongoing':
        return '상시 안내 · 실제 접수 확인'
    if row.get('periodKind') == 'budget_limited':
        return '예산 소진 여부 확인'
    return '신청 가능 여부 확인 필요'


def time_value(value):
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(KST)
    except (ValueError, TypeError):
        return None


def stamp(value):
    parsed = time_value(value)
    return parsed.strftime('%Y.%m.%d %H:%M KST') if parsed else '미제공'


def reviewed_guide(row, registry, current):
    entries = [g for g in registry.get('guides', []) if g.get('benefitId') == row['id']]
    if len(entries) != 1:
        return None
    g = entries[0]
    reviewed, until = time_value(g.get('reviewedAt')), time_value(g.get('validUntil'))
    if (g.get('status') != 'reviewed' or g.get('sourceHash') != material_hash(row)
            or not reviewed or not until or not reviewed <= current < until
            or (until - reviewed).days > 30):
        return None
    if not g.get('summary') or len(g.get('checks', [])) < 3 or len(g.get('steps', [])) < 3:
        return None
    reviews = g.get('sourceReviews', [])
    if not reviews or any(not safe_reference(x.get('url', '')) or not x.get('note') for x in reviews):
        return None
    return g


def safe_reference(value):
    try:
        u = urlsplit(value)
        return (u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password
                and not u.port and (safe_url(value) or u.hostname in {
                    'www.gbuspb.kr', 'www.mnuri.kr', 'www.energyv.or.kr',
                    'www.kosaf.go.kr', 'www.hf.go.kr', 'www.khug.or.kr', 'www.nps.or.kr',
                    'fowi.or.kr', 'www.fowi.or.kr', 'www.safedriving.or.kr',
                    'www.energy.or.kr', 'min24.energy.or.kr'}))
    except ValueError:
        return False


def matching_blog(row, registry, current):
    s = row.get('sourceUpdatedAt') or {}
    key = json.dumps([row['id'], row['title'], row['organization'], row['region'], row['period'],
                      row['summary'], s.get('list') or '', s.get('detail') or ''],
                     ensure_ascii=False, separators=(',', ':'))
    found = []
    for article in registry.get('articles', []):
        checked, observed, until = (time_value(article.get(k)) for k in
                                   ('verifiedAt', 'publicationObservedAt', 'validUntil'))
        observed = time_value(article.get('publishedAt')) or observed
        scope = article.get('scope', {})
        u = urlsplit(article.get('url', ''))
        conflicts = row.get('sourceConflicts', [])
        actual = row.get('sourceDifferences', {})
        review = article.get('reviewedSourceDifferences', {})
        differences_ok = (not conflicts and not actual and not review) or (
            set(conflicts) == {'지원유형'} and set(actual) == {'지원유형'}
            and actual == review)
        if (differences_ok and article.get('status') == 'published'
                and article.get('publicationVerified') is True and article.get('benefitId') == row['id']
                and article.get('sourceKey') == key and scope.get('year') == current.astimezone(KST).year
                and scope.get('region') == row['region'] and str(scope.get('round', '')).strip()
                and checked and observed and until and observed <= checked <= current < until
                and (current - checked).total_seconds() <= 30 * 86400
                and (until - checked).total_seconds() <= 30 * 86400
                and u.scheme == 'https' and u.hostname in {'blog.naver.com', 'm.blog.naver.com'}
                and not u.username and not u.password and not u.port and not u.query and not u.fragment
                and re.fullmatch(r'/bible_el/\d+', u.path)):
            found.append(article)
    return found[0] if len(found) == 1 else None


def quality_reasons(row, registry):
    reasons = []
    if any(not str(row.get(k) or '').strip() for k in ('title', 'organization', 'target', 'support', 'method')):
        reasons.append('공식 핵심 정보 미제공')
    if not safe_url(row.get('officialUrl')):
        reasons.append('지원사업 공식 상세 링크 미확인')
    if CRITICAL_CONFLICTS.intersection(row.get('sourceConflicts', [])):
        reasons.append('공식 목록·상세의 대상·내용·기간 표기 불일치')
    review = registry.get('holds', {}).get(row['id'])
    if review:
        reasons.append(review['reason'])
    return reasons


def header(prefix):
    return (f'<header class="header"><a class="brand" href="{prefix}" aria-label="지원금픽 처음으로">'
            f'<img class="brand-badge" src="{prefix}supportpick-badge.png" width="48" height="48" alt="">'
            '<span><strong>지원금픽<span class="brand-dot">.</span></strong>'
            '<small>한눈에 보는 생활혜택</small></span></a>'
            f'<a class="quiet" href="{prefix}?tab=apps">내 신청</a></header>')


def footer(prefix):
    return (f'<footer><div><strong>지원금픽.</strong><p>정부기관이 운영하는 사이트가 아닙니다.</p></div>'
            '<div><p>정보 확인과 준비 기록을 돕습니다. 신청·선정은 공식 기관에서 진행합니다.</p>'
            f'<a href="{prefix}about.html">소개·출처</a> · <a href="{prefix}privacy.html">개인정보처리방침</a> · '
            f'<a href="{prefix}terms.html">서비스 이용안내</a> · <a href="{prefix}contact.html">문의·정정</a></div></footer>')


def shell(title, description, body, path, prefix, base, indexable=True, structured=None, record=None):
    robots = 'index,follow' if base and indexable else 'noindex,follow' if base else 'noindex,nofollow'
    data = ''
    if structured:
        data += '<script type="application/ld+json">' + payload(structured).replace('<', '\\u003c') + '</script>'
    if record:
        data += '<script id="benefit-record" type="application/json">' + payload(record).replace('<', '\\u003c') + '</script>'
        data += f'<script src="{prefix}core.js" defer></script><script src="{prefix}detail.js" defer></script>'
    result = (f'<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
              f'<meta name="robots" content="{robots}"><title>{escape(title)}</title>'
              f'<meta name="description" content="{escape(description, quote=True)}">'
              f'<link rel="icon" href="{prefix}supportpick-badge.png"><link rel="stylesheet" href="{prefix}careerpick-base.css">'
              f'<link rel="stylesheet" href="{prefix}styles.css">{data}</head><body>'
              '<a class="skip" href="#main">본문 바로가기</a>'
              + '<div class="site-shell">' + header(prefix) + '<main id="main" class="static-benefit">'
              + body + '</main>' + footer(prefix) + '</div></body></html>')
    return public_metadata(result, path, base, {}) if base else result


def list_items(values):
    return ''.join('<li>' + escape(str(value)) + '</li>' for value in values)


def section(title, text, label='공식 API 안내'):
    return (f'<section class="detail-block"><span class="source-label">{escape(label)}</span>'
            f'<h2>{escape(title)}</h2><p class="source-text">{escape(str(text or "공식 자료 미제공 · 담당기관 확인 필요"))}</p></section>')


def editorial_html(row, guide):
    if guide:
        faqs = ''.join('<details><summary>' + escape(faq['question']) + '</summary><p>'
                       + escape(faq['answer']) + '</p></details>' for faq in guide.get('faq', []))
        references = ''.join('<li><a href="' + escape(x['url'], quote=True)
                             + '" target="_blank" rel="noopener noreferrer">' + escape(x['title'])
                             + ' ↗</a><p>' + escape(x['note']) + '</p></li>' for x in guide['sourceReviews'])
        return ('<section class="detail-block own-guide"><span class="source-label">지원금픽 자체 해설</span>'
                '<h2>신청 전에 이렇게 확인하세요</h2><p>' + escape(guide['summary'])
                + '</p><h3>먼저 점검할 조건</h3><ul>' + list_items(guide['checks'])
                + '</ul><h3>준비하는 순서</h3><ol>' + list_items(guide['steps'])
                + '</ol><h3>자주 묻는 질문</h3>' + faqs
                + '<h3>대조한 공식 안내</h3><ul class="reference-list">' + references
                + '</ul><p class="source-meta">AI 초안·공식자료 대조 ' + escape(stamp(guide['reviewedAt']))
                + ' · 공식 API 본문과 아래 자료를 대조한 준비 안내입니다. 운영자의 사람 검토 완료는 별도 확인이 필요합니다. 개인의 자격·선정·현재 접수를 확정하지 않습니다.</p></section>')
    checks = []
    if '융자' in row.get('supportType', '') or '대출' in row['title']:
        checks.append('지원방식에 대출·융자가 포함된 안내입니다. 수령액만 보지 말고 이자, 상환 방식과 심사 조건을 공식 창구에서 함께 확인하세요.')
    if row.get('regionBasis') == 'agency_jurisdiction':
        checks.append(row['organization'] + '의 소관 지역 표기는 거주 자격 판정이 아닙니다. 신청인의 주민등록지와 사업의 거주기간 조건을 대조하세요.')
    else:
        checks.append('지역 제한을 이 페이지의 기관명만으로 판단하지 마세요. 지원대상 원문에서 주소지·사업장 소재지·세대 기준을 확인하세요.')
    if row.get('periodKind') == 'ongoing':
        checks.append('상시 안내라도 담당 창구의 예산·차수·접수 상황은 달라질 수 있습니다. 서류를 발급하기 전에 현재 접수 중인지 문의하세요.')
    else:
        checks.append('신청기간이 연도·차수별로 달라질 수 있습니다. 위 기간을 현재 모집으로 단정하지 말고 공식 공고의 신청 시작·마감일을 확인하세요.')
    checks.append('아래 구비서류에서 본인에게 해당하는 증빙과 발급 기준일을 확인하고, 미제공 항목은 담당기관에 확인한 뒤 준비하세요.')
    return ('<section class="detail-block own-guide"><span class="source-label">지원금픽 준비 안내</span>'
            '<h2>' + escape(row['title']) + ' 확인 순서</h2><ul>' + list_items(checks)
            + '</ul><p>공식 안내에서 조건과 서류를 확인한 뒤 관심 저장을 해두세요. 내 신청에는 준비·접수·결과를 직접 기록할 수 있으며 공식 접수가 자동으로 이루어지지는 않습니다.</p></section>')


def render_benefit(row, guide, blog, reasons, related, base, current, feed_status):
    path = benefit_path(row['id'])
    title = row['title'] + ' | 신청대상·지원내용·신청방법 - 지원금픽'
    summary = re.sub(r'\s+', ' ', row.get('summary', '')).strip()
    description = (row['title'] + ': ' + row['organization'] + ' 안내. ' + summary)[:155]
    crumbs = ('<nav class="breadcrumbs" aria-label="현재 위치"><a href="../../">홈</a><span>›</span>'
              '<a href="../">혜택 전체</a><span>›</span><span>' + escape(row['title']) + '</span></nav>')
    actions = (f'<a class="primary" href="{escape(safe_url(row.get("officialUrl")) or "https://plus.gov.kr/", quote=True)}" '
               'target="_blank" rel="noopener noreferrer">정부24 공식 안내 확인 ↗</a>'
               '<button class="quiet" data-save disabled>☆ 관심 저장</button>'
               '<button class="quiet" data-track disabled>내 신청에 기록</button>')
    if safe_url(row.get('applicationUrl')):
        actions += ('<a class="quiet" href="' + escape(row['applicationUrl'], quote=True)
                    + '" target="_blank" rel="noopener noreferrer">공식 신청 창구 ↗</a>')
    body = crumbs + '<div class="warning" id="record-warning" role="alert" hidden></div>'
    body += '<div class="warning" id="freshness-warning" role="status" hidden></div>'
    if feed_status != 'success':
        body += '<p class="warning">최근 수집 상태를 확인해야 합니다. 마지막 정상 자료를 보존해 표시하고 있습니다.</p>'
    if reasons:
        body += '<aside class="warning"><strong>내용 확인 필요</strong><ul>' + list_items(reasons) + '</ul><p>검증을 마칠 때까지 상세 본문과 검색 등록을 보류했습니다.</p></aside>'
        # A failed content review is a public holding notice, never an indexable
        # document or a warning wrapped around potentially obsolete financial facts.
        body += ('<article class="detail-header"><h1>' + escape(row['title']) + '</h1><p>'
                 + escape(row['organization']) + '</p><p>현재 적용 조건을 검증 중이어서 상세 본문 공개를 보류했습니다. '
                 '신청 조건·금액·기간은 담당기관의 최신 공식 안내에서 확인하세요.</p>'
                 '<span class="badge" id="period-status">내용 확인 필요</span><div class="detail-actions">'
                 + actions + '</div></article>')
        reference=row.get('_holdReference')
        if reference and safe_reference(reference):
            body += '<section class="detail-block"><h2>최신 공식 안내 확인</h2><a href="' + escape(reference,quote=True) + '" target="_blank" rel="noopener noreferrer">대조한 담당기관 안내 ↗</a></section>'
        record={k:row.get(k) for k in ('id','title','checkedAt')};record['base']='../../'
        return shell(row['title']+' | 내용 확인 필요 - 지원금픽',
                     row['organization']+'의 지원정보를 확인 중입니다. 최신 공식 안내를 확인하세요.',
                     body,path,'../../',base,False,record=record)
    body += (f'<article class="detail-header"><span class="category-badge">{escape(row["category"])}</span> '
             f'<span class="badge" id="period-status">{escape(status(row, current))}</span>'
             f'<h1>{escape(row["title"])}</h1><p class="organization">{escape(row["organization"])}</p>'
             f'<p>{escape(summary)}</p><dl class="card-meta"><dt>신청기간</dt><dd>{escape(row["period"])}</dd>'
             f'<dt>지원방식</dt><dd>{escape(row["supportType"])}</dd><dt>자료조회</dt><dd>{escape(stamp(row.get("checkedAt")))}</dd></dl>'
             '<p class="context-note">공식 API 안내와 지원금픽의 준비 해설을 구분해 제공합니다. API 조회 성공은 현재 접수·개인 자격 확인을 뜻하지 않습니다.</p>'
             '<div class="detail-actions">' + actions + '</div>'
             '<noscript><p class="context-note">핵심 안내는 JavaScript 없이 읽을 수 있습니다. 관심 저장·내 신청 기록은 JavaScript를 켜거나 홈에서 이용하세요.</p></noscript></article>')
    body += editorial_html(row, guide)
    for heading, key in [('지원대상', 'target'), ('선정기준·세부 자격', 'selection'), ('지원내용·금액', 'support'),
                         ('신청방법', 'method'), ('준비서류', 'documents'), ('문의처', 'contact')]:
        body += section(heading, row.get(key))
    differences = row.get('sourceDifferences', {})
    if differences:
        body += '<section class="detail-block"><h2>공식 목록·상세 표기 차이</h2><p>원본 값이 다릅니다. 적용 기준은 담당기관의 최신 원문에서 확인하세요.</p>'
        for name, values in differences.items():
            body += '<h3>' + escape(name) + '</h3><p class="source-text">목록: ' + escape(str(values.get('list') or '미제공')) + '\n\n상세: ' + escape(str(values.get('detail') or '미제공')) + '</p>'
        body += '</section>'
    body += ('<section class="detail-block"><h2>정보 출처와 확인 범위</h2><p>보조금24 OpenAPI · 서비스 ID '
             + escape(row['id']) + '</p><p>공식 출처 수정일: ' + escape(source_date(row) or '미제공')
             + '<br>API 자료 조회: ' + escape(stamp(row.get('checkedAt')))
             + '</p><p>조회 시각과 내용 수정일은 다릅니다. 신청기간이 불명확하거나 예산 소진 여부가 제공되지 않으면 확인이 필요합니다.</p>'
             '<p><a href="../../contact.html">오류·변경 사항 알려주기</a></p></section>')
    if related:
        body += '<section class="detail-block"><h2>함께 확인할 지원정보</h2><p>같은 분야·소관기관의 정보이며 중복 수급 가능 여부를 뜻하지 않습니다.</p><ul>'
        body += ''.join('<li><a href="../' + quote(x['id'], safe='') + '/">' + escape(x['title']) + '</a> · ' + escape(x['organization']) + '</li>' for x in related)
        body += '</ul></section>'
    # Keep exact matching and expiry rules used by the existing blog automation.
    if blog:
        body += (f'<section class="detail-block editorial-block" data-blog-until="{escape(blog["validUntil"], quote=True)}">'
                 '<h2>관련 네이버 블로그 해설</h2><p>' + escape(blog.get('scopeNote') or '')
                 + '</p><a class="editorial-link" href="' + escape(blog['url'], quote=True)
                 + '" target="_blank" rel="noopener noreferrer">' + escape(blog['title']) + ' ↗</a></section>')
    structured = None
    if base:
        structured = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '지원금픽', 'item': base},
            {'@type': 'ListItem', 'position': 2, 'name': '혜택 전체', 'item': base + 'benefits/'},
            {'@type': 'ListItem', 'position': 3, 'name': row['title'], 'item': base + path}]}
    record = {k: row.get(k) for k in ('id', 'title', 'checkedAt', 'periodKind', 'startDate', 'endDate')}
    record['base'] = '../../'
    return shell(title, description, body, path, '../../', base, not reasons, structured, record)


def write_details(output, rows, previous, base, registry, blogs, feed_status, current=None):
    current = current or datetime.now(timezone.utc)
    sorted_rows = sorted(rows.values(), key=popularity)
    categories = defaultdict(list)
    quality = {}
    for row in sorted_rows:
        categories[row['category']].append(row)
        quality[row['id']] = quality_reasons(row, registry)
    eligible_categories = {key: [r for r in group if not quality[r['id']]] for key, group in categories.items()}
    # Exact duplicates are held rather than advertised as independent editorial content.
    fingerprints = Counter(payload({k: r.get(k) for k in ('title', 'organization', 'target', 'support', 'method', 'period')}) for r in sorted_rows)
    entries, held, guides, blog_count = [], {}, [], 0
    paths = set()
    for row in sorted_rows:
        path = benefit_path(row['id'])
        if path.casefold() in paths:
            raise ValueError('benefit_path_collision')
        paths.add(path.casefold())
        reasons = list(quality[row['id']])
        fp = payload({k: row.get(k) for k in ('title', 'organization', 'target', 'support', 'method', 'period')})
        if fingerprints[fp] > 1:
            reasons.append('같은 기관·대상·내용의 중복 자료 확인 필요')
        guide = reviewed_guide(row, registry, current)
        blog = matching_blog(row, blogs, current)
        related = []
        for candidate in eligible_categories[row['category']]:
            if candidate['id'] != row['id']:
                related.append(candidate)
            if len(related) == 4:
                break
        target = output / path / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        display={**row,'_holdReference':registry.get('holds',{}).get(row['id'],{}).get('url')}
        target.write_text(render_benefit(display, guide, blog, reasons, related, base, current, feed_status), encoding='utf-8')
        if reasons:
            held[row['id']] = reasons
        elif base:
            modified = max(filter(None, [TEMPLATE_MODIFIED, source_date(row), guide['reviewedAt'][:10] if guide else None]))
            if row['id'] in previous and material_hash(previous[row['id']])!=material_hash(row) and source_date(previous[row['id']])==source_date(row):
                modified=None  # Content changed, but the authority did not supply a new modification time.
            entries.append((path, modified))
        if guide and not reasons:
            guides.append(row['id'])
        blog_count += bool(blog)
    retired = sorted(set(previous) - set(rows))
    for sid in retired:
        path = benefit_path(sid)
        target = output / path / 'index.html'; target.parent.mkdir(parents=True, exist_ok=True)
        text = '<article class="detail-block"><h1>현재 공식 목록에서 확인되지 않는 지원정보</h1><p>' + escape(previous[sid]['title']) + '</p><p>이전 공유 주소를 보존했습니다. 현재 모집·폐지 여부는 담당기관에서 확인하세요. 저장·신청 기록은 삭제하지 않았습니다.</p><a href="../../">현재 지원정보 검색</a></article>'
        target.write_text(shell('현재 자료 확인 필요 | 지원금픽', '이전 지원정보의 현재 공식 안내를 확인하세요.', text, path, '../../', base, False), encoding='utf-8')
    listed = [r for r in sorted_rows if r['id'] not in held]
    total_pages = max(1, math.ceil(len(listed) / PAGE_SIZE))
    for page in range(1, total_pages + 1):
        path = 'benefits/' if page == 1 else f'benefits/page/{page}/'
        prefix = '../' if page == 1 else '../../../'
        group = listed[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
        body = f'<article class="detail-block"><h1>지원금·생활혜택 전체 안내 {page} / {total_pages}</h1><p>공식 API의 실제 누적 조회수 순입니다. 조회수가 제공되지 않은 자료는 뒤에 표시하며 실시간 인기 순위나 신청 가능 여부를 뜻하지 않습니다.</p><p><a href="{prefix}">검색·맞춤·저장 기능으로 찾기</a></p><ul class="benefit-directory">'
        body += ''.join('<li><a href="' + prefix + benefit_path(r['id']) + '">' + escape(r['title']) + '</a><span>' + escape(r['organization']) + '</span></li>' for r in group)
        body += '</ul><nav class="pagination" aria-label="지원정보 목록 페이지">'
        for number, label in [(page - 1, '← 이전'), (page + 1, '다음 →')]:
            if 1 <= number <= total_pages:
                dest = 'benefits/' if number == 1 else f'benefits/page/{number}/'
                body += f'<a class="quiet" href="{prefix}{dest}">{label}</a>'
        body += '</nav></article>'
        target = output / path / 'index.html'; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(shell(f'지원금·생활혜택 전체 {page}페이지 | 지원금픽', f'지원금픽의 공식 지원정보 목록 {page}페이지. 기관과 사업명을 확인하고 상세 안내로 이동하세요.', body, path, prefix, base), encoding='utf-8')
        if base:
            entries.append((path, None))  # Popularity order is not an authoritative content modification date.
    popular = [rows[sid] for sid in guides]
    # Prefer reviewed explanations in the small server-rendered homepage discovery area.
    home_rows = (popular + [r for r in listed if r not in popular])[:20]
    home_links = '<section id="staticDiscovery" class="detail-block"><span class="eyebrow">BENEFIT GUIDES</span><h2>많이 찾는 지원정보와 신청 준비 해설</h2><p>공식 누적 조회수가 높은 정보부터 확인하세요. 실제 접수 여부는 사업별 공식 창구에서 확인해야 합니다.</p><ul class="discovery-links">'
    home_links += ''.join('<li><a href="' + benefit_path(r['id']) + '">' + escape(r['title']) + '</a></li>' for r in home_rows)
    home_links += '</ul><a class="editorial-link" href="benefits/">지원정보 전체 목록 →</a></section>'
    return {'entries': entries, 'home': home_links, 'report': {
        'detailPages': len(rows), 'indexableDetails': len(rows) - len(held),
        'heldDetails': len(held), 'reviewedGuides': len(guides), 'guideIds': guides,
        'blogLinks': blog_count, 'directoryPages': total_pages, 'retiredPages': len(retired),
        'heldReasons': held, 'rankingBasis': 'rawSource.serviceList.조회수',
        'sourceGeneration': next(iter(rows.values())).get('generation') if rows else None}}
