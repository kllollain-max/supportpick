"""Read-only source checks. Preserve raw snapshots and report review candidates."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict
from collect_full import safe_url, period

HOUSEHOLDS = {'JA0401': '다문화가족', 'JA0402': '북한이탈주민',
              'JA0403': '한부모·조손가정', 'JA0404': '1인가구',
              'JA0411': '다자녀가구', 'JA0412': '무주택세대',
              'JA0413': '신규전입', 'JA0414': '확대가족'}

SUMMARY_PLACEHOLDERS = {'', '-', '상동', '위와동일', '상기와동일', '없음', '해당없음'}


def summary_view(row, withheld=False):
    """Use an attributed source excerpt for an unusable summary; never rewrite data."""
    if withheld:
        return {'text': '', 'label': ''}
    summary = re.sub(r'\s+', ' ', str(row.get('summary') or '')).strip()
    if re.sub(r'\s+', '', summary) not in SUMMARY_PLACEHOLDERS:
        return {'text': summary, 'label': ''}
    for field in ('targetPreview', 'target'):
        target = re.sub(r'\s+', ' ', str(row.get(field) or '')).strip()
        if re.sub(r'\s+', '', target) not in SUMMARY_PLACEHOLDERS:
            return {'text': target[:180] + ('…' if len(target) > 180 else ''),
                    'label': '지원대상 원문 일부'}
    return {'text': '', 'label': ''}


def conditions(row):
    """Expose API flags, never infer eligibility from names or narrative text."""
    source = row.get('rawSource', {}).get('supportConditions', {})
    lower, upper = source.get('JA0110'), source.get('JA0111')
    valid = (type(lower) is int and type(upper) is int
             and 0 <= lower <= upper <= 200)
    return {'ageMin': lower if valid else None, 'ageMax': upper if valid else None,
            'households': [label for code, label in HOUSEHOLDS.items() if source.get(code) == 'Y']}


def audit(rows):
    issues, counts, groups = {}, Counter(), defaultdict(list)
    for sid, row in rows.items():
        reasons = []
        for field in ('title', 'organization', 'target', 'support', 'method', 'documents', 'contact'):
            if not str(row.get(field) or '').strip():
                reasons.append('missing_' + field)
        if not safe_url(row.get('officialUrl')):
            reasons.append('official_link_needs_check')
        if row.get('sourceConflicts'):
            reasons.append('source_conflict')
        parsed = period(row.get('period', ''))
        if parsed['periodKind'] in ('needs_check', 'not_provided'):
            reasons.append('period_needs_check')
        if any(not row.get('sourceUpdatedAt', {}).get(k) for k in ('list', 'detail')):
            reasons.append('source_modified_date_missing')
        if len(str(row.get('summary') or '').strip()) < 20:
            reasons.append('short_summary_review')
        if re.sub(r'\s+', '', str(row.get('summary') or '')) in SUMMARY_PLACEHOLDERS:
            reasons.append('placeholder_summary_review')
        if not re.search(r'중복|동시|타\s*사업|다른\s*사업', row.get('selection', '') + row.get('target', '') + row.get('support', '')):
            reasons.append('duplicate_receipt_rule_not_structured')
        groups[(row.get('title', '').strip(), row.get('organization', '').strip())].append(sid)
        if reasons:
            issues[sid] = reasons
            counts.update(reasons)
    duplicates = [ids for ids in groups.values() if len(ids) > 1]
    return {'version': 1, 'total': len(rows), 'checks': dict(counts),
            'reviewCandidates': issues, 'sameNameAgencyGroups': duplicates,
            'sourcePreserved': True, 'automaticDeletion': False,
            'automaticIndexingChange': False,
            'linkCheckScope': 'scheme and government hostname only; HTTP availability requires a live check',
            'factCheckScope': 'missing fields, source conflicts and date syntax; financial facts require official review'}


def reading_gaps(row):
    """Only observed gaps; a complete record gets no generated filler paragraph."""
    gaps=[]
    # Eligibility can be fully described in target without a separate selection field.
    for key,label in [('documents','구비서류'),('contact','문의처')]:
        if not str(row.get(key) or '').strip():
            gaps.append('공식 연결자료에 '+label+' 항목이 제공되지 않았습니다. 필요한 내용은 공식 공고·담당기관에서 확인하세요.')
    if period(row.get('period',''))['periodKind'] in ('needs_check','not_provided'):
        gaps.append('신청기간을 하나의 명확한 날짜 구간으로 확인할 수 없습니다. 아래 원문에서 연도·차수를 대조하세요.')
    if row.get('sourceConflicts'):
        gaps.append('공식 목록과 상세의 일부 항목이 다릅니다. 아래 원본 표기 차이를 확인하세요.')
    return gaps


def review_queue(rows, quality, search, current=None, decisions=None):
    """Operational triage of all records. Never deletes, merges or changes robots."""
    current=current or datetime.now(ZoneInfo('Asia/Seoul'))
    today=current.astimezone(ZoneInfo('Asia/Seoul')).date().isoformat()
    from record_reviews import approved_distinctions
    reviewed=approved_distinctions(rows,quality['sameNameAgencyGroups'],decisions or {'version':1,'groups':[]},current)
    grouped={sid:group for group in quality['sameNameAgencyGroups'] for sid in group}
    held=search['heldReasons']; matched=set(search['guideIds']);items=[];counts=Counter()
    for sid,row in rows.items():
        flags=list(quality['reviewCandidates'].get(sid,[])); parsed=period(row.get('period',''))
        if parsed.get('endDate') and parsed['endDate']<today:flags.append('explicit_period_ended')
        # Lack of an editorial connection is a review scope, never a poor-quality verdict.
        if sid not in matched:flags.append('no_matched_preparation_guide')
        if sid in held:
            state,priority='기존 공개 보류 재확인',0
        elif sid in grouped and sid not in reviewed:
            state,priority='통합 검토',1
        elif any(x not in ('no_matched_preparation_guide','duplicate_receipt_rule_not_structured') for x in flags):
            state,priority='수정 대기',2
        else:
            state,priority='추가 가치 검토',3
        raw=row.get('rawSource',{}).get('serviceList',{}).get('조회수')
        views=int(raw) if isinstance(raw,(int,str)) and not isinstance(raw,bool) and re.fullmatch(r'\d{1,15}',str(raw)) else None
        items.append({'id':sid,'title':row.get('title'),'organization':row.get('organization'),
                      'reviewState':state,'priority':priority,'observedFlags':flags,
                      'existingPublicationHold':sid in held,'holdReasons':held.get(sid,[]),
                      'sameNameAgencyIds':grouped.get(sid,[]),'officialCumulativeViews':views,
                      'sourceRecordDecision':reviewed.get(sid),
                      'sourceModifiedAt':row.get('sourceUpdatedAt'),'apiFetchedAt':row.get('checkedAt'),
                      'officialUrl':row.get('officialUrl')})
        counts[state]+=1
    items.sort(key=lambda x:(x['priority'],x['officialCumulativeViews'] is None,-(x['officialCumulativeViews'] or 0),x['id']))
    return {'asOf':today,'total':len(items),'stateCounts':dict(counts),'items':items,
            'priorityBasis':'Existing holds, unresolved possible duplicate groups, observed gaps; actual API cumulative views within each group.',
            'reviewedSeparateSourceGroups':len({tuple(sorted(d['ids'])) for d in reviewed.values()}),
            'automaticDeletion':False,'automaticIndexingChange':False,'automaticMerge':False,
            'limitations':['Candidate states do not establish low value or factual accuracy.',
                          'An ended date does not establish that a replacement round exists.',
                          'Missing concurrent-benefit wording is not evidence of prohibition or permission.',
                          'Index exclusion candidates require individual evidence; this queue adds no exclusions.']}
