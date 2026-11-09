"""Read-only freshness audit for reviewed SupportPick editorial facts and links.

Does not change editorial status, source snapshots, or advertising.
"""
import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

def parse_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        instant = datetime.fromisoformat(value.replace('Z','+00:00'))
        if instant.tzinfo is None:
            return None
        return instant.astimezone(ZoneInfo('Asia/Seoul')).date()
    except ValueError:
        return None

def audit(guides, editorials, today, window=14):
    if not isinstance(guides, dict) or not isinstance(guides.get('guides'), list):
        raise ValueError('invalid_guides')
    if not isinstance(editorials, dict) or not isinstance(editorials.get('articles'), list):
        raise ValueError('invalid_editorials')
    if not isinstance(today, date) or not isinstance(window, int) or not 0 <= window <= 90:
        raise ValueError('invalid_parameters')
    rows = []
    for kind, source, identifier in [('guide', guides['guides'], 'benefitId'),
                                     ('article', editorials['articles'], 'benefitId')]:
        for item in source:
            if not isinstance(item, dict):
                rows.append({'kind': kind, 'benefit_id': None, 'status': 'invalid_record'})
                continue
            bid = item.get(identifier)
            valid = parse_date(item.get('validUntil'))
            if not isinstance(bid, str) or not bid:
                state = 'missing_benefit_id'
            elif not valid:
                state = 'unknown_validity'
            elif valid < today:
                state = 'expired_review'
            elif valid <= today + timedelta(days=window):
                state = 'review_due_soon'
            else:
                state = 'fresh_review'
            if kind == 'article':
                url = item.get('url', '')
                u = urlsplit(url if isinstance(url,str) else '')
                if (u.scheme != 'https' or u.hostname not in ('m.blog.naver.com','blog.naver.com')
                        or item.get('publicationVerified') is not True or item.get('status') != 'published'):
                    state = 'publication_not_verified'
            elif item.get('status') != 'reviewed':
                state = 'not_reviewed'
            rows.append({'kind':kind,'benefit_id':bid,'status':state,
                         'valid_until':valid.isoformat() if valid else None})
    counts={}
    for item in rows: counts[item['status']]=counts.get(item['status'],0)+1
    urgent={'expired_review','unknown_validity','publication_not_verified','missing_benefit_id','invalid_record'}
    return {'as_of':today.isoformat(),'items':len(rows),'status_counts':counts,
            'urgent_review_count':sum(item['status'] in urgent for item in rows),
            'upcoming_review_count':counts.get('review_due_soon',0),
            'review_rows':[item for item in rows if item['status'] != 'fresh_review'],
            'notes':['Source review validity is not proof of currently open applications',
                     'Blog publication verification is distinct from official benefit facts',
                     'Review-only output: no editing, publishing, indexing or advertising changes']}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--guides',default='guides.json')
    parser.add_argument('--editorials',default='editorials.json')
    parser.add_argument('--out',default='review-only/editorial-freshness.json')
    parser.add_argument('--as-of',default=datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat())
    args=parser.parse_args()
    report=audit(json.loads(Path(args.guides).read_text(encoding='utf-8')),
                 json.loads(Path(args.editorials).read_text(encoding='utf-8')),
                 date.fromisoformat(args.as_of))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='review_rows'},ensure_ascii=False))

if __name__=='__main__':
    main()
