"""Explain dropped editorial bindings without renewing hashes or changing originals."""
import json
from collections import Counter
from datetime import datetime, timezone

from detail_pages import (MATERIAL_FIELDS, blog_source_key, matching_blog, material_hash,
                          quality_reasons, reviewed_guide, KST)

BLOG_FIELDS = ('id', 'title', 'organization', 'region', 'period', 'summary',
               'sourceUpdatedAt.list', 'sourceUpdatedAt.detail')


def audit(rows, previous, guides, blogs, current=None):
    current = current or datetime.now(timezone.utc)
    entries = []
    for kind, registry, key in [('guide', guides, 'guides'), ('blog', blogs, 'articles')]:
        counts = Counter(x.get('benefitId') for x in registry.get(key, []))
        for entry in registry.get(key, []):
            sid = entry.get('benefitId')
            row = rows.get(sid)
            item = {'kind': kind, 'benefitId': sid, 'status': 'review_required', 'reason': '',
                    'changedFields': [], 'fieldComparisonBasis': 'unavailable'}
            if counts[sid] != 1:
                item['reason'] = 'ambiguous_registration'
            elif row is None:
                item['reason'] = 'not_in_current_source'
            elif quality_reasons(row, guides):
                item['reason'] = 'source_on_hold'
            elif kind == 'guide' and entry.get('sourceHash') != material_hash(row):
                item['reason'] = 'source_material_changed'
                old = previous.get(sid)
                if old is not None and material_hash(old) == entry.get('sourceHash'):
                    item['changedFields'] = [k for k in MATERIAL_FIELDS if old.get(k) != row.get(k)]
                    item['fieldComparisonBasis'] = 'previous_source_matches_reviewed_hash'
            elif kind == 'blog' and entry.get('sourceKey') != blog_source_key(row):
                item['reason'] = 'source_binding_changed'
                try:
                    old, new = json.loads(entry['sourceKey']), json.loads(blog_source_key(row))
                    if not isinstance(old, list) or len(old) != len(BLOG_FIELDS):
                        raise ValueError('invalid_source_key')
                    item['changedFields'] = [k for k, a, b in zip(BLOG_FIELDS, old, new) if a != b]
                    item['fieldComparisonBasis'] = 'registered_source_key'
                except (ValueError, TypeError, KeyError):
                    item['fieldComparisonBasis'] = 'invalid_registered_source_key'
            elif ((kind == 'guide' and reviewed_guide(row, guides, current) is not None)
                  or (kind == 'blog' and matching_blog(row, blogs, current) is not None)):
                item.update(status='active', reason='matched_current_source')
            else:
                item['reason'] = 'review_expired_or_invalid'
            entries.append(item)
    registered_ids = {x['benefitId'] for x in entries}
    return {'version': 1, 'asOf': current.astimezone(KST).date().isoformat(), 'sourceRecords': len(rows),
            'registeredEntries': len(entries),
            'sourceRecordsWithoutRegisteredEditorial': len(set(rows) - registered_ids),
            'active': sum(x['status'] == 'active' for x in entries),
            'reviewRequired': sum(x['status'] != 'active' for x in entries), 'entries': entries,
            'notes': ['Only registered guides/blogs are checked; this is not a site-wide quality verdict.',
                      'Read-only comparison; no hash, date, publication, source or indexing changes.',
                      'Changed fields alone do not establish that editorial text is incorrect.',
                      'Missing historical baseline is reported rather than inferred.']}
