"""Evidence-limited decisions about source records; never rewrite the source."""
import hashlib
import json
from datetime import datetime
from collect_full import safe_url, valid_id

SCOPE_FIELDS = ('title', 'organization', 'target', 'support', 'period',
                'method', 'documents', 'contact', 'officialUrl')


def scope_hash(row):
    return hashlib.sha256(json.dumps({k: row.get(k) for k in SCOPE_FIELDS},
        ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def approved_distinctions(rows, groups, registry, current):
    """Accept only unchanged, unexpired groups with official evidence.

    A keep-separate decision does not verify current eligibility or remove a hold.
    Changed source fields, group membership or time return the group to review.
    """
    if registry.get('version') != 1 or not isinstance(registry.get('groups'), list):
        raise ValueError('invalid_record_review_registry')
    result = {}
    candidates = {frozenset(group) for group in groups}
    for entry in registry['groups']:
        ids = entry.get('ids', [])
        if (not isinstance(ids, list) or len(ids) < 2
                or any(not isinstance(sid, str) or not valid_id(sid) for sid in ids)
                or len(set(ids)) != len(ids)):
            raise ValueError('invalid_record_review_ids')
        if any(sid in result for sid in ids):
            raise ValueError('overlapping_record_reviews')
        try:
            checked = datetime.fromisoformat(entry['reviewedAt'].replace('Z', '+00:00'))
            until = datetime.fromisoformat(entry['validUntil'].replace('Z', '+00:00'))
            times_ok = (checked.tzinfo is not None and until.tzinfo is not None
                        and checked <= current < until
                        and 0 < (until - checked).total_seconds() <= 30 * 86400)
        except (KeyError, ValueError, TypeError, AttributeError):
            times_ok = False
        references = entry.get('evidence', [])
        hashes = entry.get('sourceScopeHashes', {})
        if (entry.get('decision') != 'keep_separate_source_records' or not entry.get('reason')
                or not times_ok or frozenset(ids) not in candidates
                or not isinstance(hashes, dict) or set(hashes) != set(ids)
                or any(sid not in rows or scope_hash(rows[sid]) != hashes[sid] for sid in ids)
                or not references or any(not safe_url(ref.get('url')) or not ref.get('note') for ref in references)):
            continue
        decision = {k: entry[k] for k in ('decision', 'reason', 'reviewedAt', 'validUntil', 'evidence')}
        decision['ids'] = ids
        for sid in ids:
            result[sid] = decision
    return result
