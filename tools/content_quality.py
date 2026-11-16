"""Read-only source checks. Preserve raw snapshots and report review candidates."""
import re
from collections import Counter, defaultdict
from collect_full import safe_url, period

HOUSEHOLDS = {'JA0401': '다문화가족', 'JA0402': '북한이탈주민',
              'JA0403': '한부모·조손가정', 'JA0404': '1인가구',
              'JA0411': '다자녀가구', 'JA0412': '무주택세대',
              'JA0413': '신규전입', 'JA0414': '확대가족'}


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
