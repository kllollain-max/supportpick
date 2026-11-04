"""SupportPick publisher. Preview by default; CAS ledger precedes every POST.

Adapted from CareerPick's account guard, four KST slots, reservation-before-send
and ambiguous-send hold. Recruitment filters/history are intentionally not copied.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
KST = ZoneInfo('Asia/Seoul')
SITE = 'https://kllollain-max.github.io/supportpick/'
PROFILE_LINK = SITE + '?utm_source=threads&utm_medium=social&utm_content=link_in_bio'
CTA = '자세한 사항은 프로필링크 확인'
USERNAME = 'hid_1004'
REPO = 'kllollain-max/supportpick'
STATE_BRANCH = 'supportpick-threads-state'
CRONS = {'0 23 * * *': 8, '0 3 * * *': 12, '0 7 * * *': 16, '0 11 * * *': 20}


def stamp(value):
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('aware_timestamp_required')
    return dt.astimezone(KST)


def fresh(value, now):
    try:
        return timedelta(0) <= now - stamp(value) <= timedelta(hours=24)
    except (TypeError, ValueError):
        return False


def official_url(value):
    try:
        u = urllib.parse.urlsplit(value)
        host = u.hostname or ''
        return u.scheme == 'https' and not u.username and not u.password and u.port in (None, 443) and (host.endswith('.go.kr') or host in ('plus.gov.kr', 'www.gov.kr'))
    except (ValueError, TypeError):
        return False


def image_url(value):
    # Only deliberately supplied, already published SupportPick images.
    try:
        u = urllib.parse.urlsplit(value)
        return (u.scheme == 'https' and not u.username and not u.password and u.port in (None, 443)
                and u.hostname == 'raw.githubusercontent.com'
                and re.fullmatch(r'/kllollain-max/supportpick/main/social/images/[A-Za-z0-9_-]+\.(jpg|jpeg|png)', u.path)
                and not u.query and not u.fragment)
    except (TypeError, ValueError):
        return False


def excerpt(value, limit):
    text = re.sub(r'\s+', ' ', str(value or '')).strip()
    return text if len(text) <= limit else text[:limit - 1] + '…'


TEXT_LINK = re.compile(
    r'(?:[a-z][a-z0-9+.-]*://|www\.|mailto:|tel:)[^\s<>]*'
    r'|(?:[a-z0-9-]+\.)+(?:[a-z]{2,63}|xn--[a-z0-9-]+)(?:[/?#][^\s<>]*)?'
    r'|(?:[가-힣a-z0-9-]+\.)+한국(?:[/?#][^\s<>]*)?', re.IGNORECASE)


def post_excerpt(value, limit):
    # Remove addresses before truncation so an incomplete URL cannot leak.
    # Official raw sources and ledger provenance are preserved separately.
    return excerpt(TEXT_LINK.sub('', str(value or '')), limit)


def require_link_free(text):
    if TEXT_LINK.search(text):
        raise ValueError('link_free_publication_required')


def load_feed(state):
    from refresh import read_current, verify_snapshot
    pointer, snapshot = read_current(state)
    if not pointer:
        raise ValueError('complete_collection_required')
    feed = verify_snapshot(snapshot)
    if feed.get('isSample') is not False:
        raise ValueError('sample_not_publishable')
    details = {}
    for path in (snapshot / 'details' / feed['generation']).glob('*.json'):
        shard = json.loads(path.read_text())
        if shard.get('generation') != feed['generation']:
            raise ValueError('detail_generation_mismatch')
        details.update(shard['items'])
    if set(details) != {i['id'] for i in feed['items']}:
        raise ValueError('detail_join_incomplete')
    return {**feed, 'items': [details[i['id']] for i in feed['items']]}


def popularity_views(row):
    """Use Gov24's actual cumulative views, never infer demand from the title."""
    raw = row.get('rawSource')
    source = raw.get('serviceList') if isinstance(raw, dict) else None
    if not isinstance(source, dict) or source.get('서비스ID') != row.get('id'):
        return None
    value = source.get('조회수')
    if type(value) is int:
        return value if 0 <= value <= 10**18 else None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) > 30 or not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', value):
        return None
    number = int(value.replace(',', ''))
    return number if number <= 10**18 else None


def priority_key(row):
    views = popularity_views(row)
    return (views is None, -(views or 0), row.get('endDate') or '9999', row['id'])


def selection_info(row):
    return {'policy': 'gov24_views_desc_v1', 'basis': '보조금24 누적 조회수',
            'views': popularity_views(row), 'source_checked_at': row.get('checkedAt'),
            'note': '실시간 검색량·신청자 수가 아닌 공식 API 누적 조회수 기준'}


def candidates(feed, ledger, now):
    if feed.get('isSample') is not False or not fresh(feed.get('updatedAt') or feed.get('collectionSucceededAt'), now):
        return []
    blocked = {r['benefit_id'] for r in ledger['records']}
    found, seen = [], set()
    for row in feed.get('items', []):
        sid = str(row.get('id') or '')
        if not sid or sid in blocked or sid in seen or row.get('sourceConflicts'):
            continue
        if not fresh(row.get('checkedAt'), now) or not official_url(row.get('officialUrl')):
            continue
        if not all(row.get(k) for k in ('title', 'organization', 'summary', 'target', 'method')):
            continue
        try:
            if row.get('endDate') and datetime.fromisoformat(row['endDate']).date() < now.date():
                continue
            if row.get('startDate') and datetime.fromisoformat(row['startDate']).date() > now.date():
                continue
        except (ValueError, TypeError):
            continue
        if re.search(r'취\s*소|철\s*회|종\s*료', row['title']):
            continue
        seen.add(sid)
        found.append(row)
    return sorted(found, key=priority_key)


def compose(row):
    # No benefit amounts or eligibility decisions are inferred from summaries.
    main = '\n\n'.join([
        '📌 ' + post_excerpt(row['title'], 65),
        post_excerpt(row['summary'], 110),
        '기관: ' + post_excerpt(row['organization'], 35),
        '대상·기간·신청방법은 답글에 정리했어요.\n신청 가능 여부와 세부 조건은 공식 원문을 확인하세요.',
        '#지원금픽 #' + re.sub(r'[^가-힣A-Za-z0-9_]', '', post_excerpt(row.get('category') or '생활혜택', 15)),
        CTA])
    detail = '\n\n'.join([
        '대상 요약: ' + post_excerpt(row['target'], 100),
        '원문 기간: ' + post_excerpt(row.get('period') or '공식 안내 확인', 55),
        '신청방법 요약: ' + post_excerpt(row['method'], 85),
        '※ 자격 충족·선정·현재 접수를 보장하지 않습니다.\n공식 원문과 세부 조건은 프로필링크에서 확인하세요.',
        CTA])
    # The profile link is the conversion route; do not divert readers to the blog.
    links = '\n\n'.join([
        '프로필링크에서 지원금픽을 열고 아래 혜택명을 검색해 보세요.',
        '🔎 ' + post_excerpt(row['title'], 65),
        '대상·신청방법을 확인하고 관심 혜택을 저장해 신청 준비를 관리할 수 있어요.',
        CTA])
    for text in (main, detail, links):
        require_link_free(text)
    if any(len(x) > 500 for x in (main, detail, links)):
        raise ValueError('post_or_reply_over_500_characters')
    return main, detail, links


def current_slot(now, cron):
    if cron == 'manual':
        return now.replace(second=0, microsecond=0).isoformat()
    if cron not in CRONS:
        raise ValueError('known_scheduled_slot_required')
    slot = now.replace(hour=CRONS[cron], minute=0, second=0, microsecond=0)
    if not slot <= now < slot + timedelta(hours=2):
        raise ValueError('missed_slot_not_backfilled')
    return slot.isoformat()


def publication_context(env):
    if env.get('SUPPORTPICK_THREADS_ENABLED') != 'true' or env.get('SUPPORTPICK_THREADS_CUTOVER_READY') != 'true':
        raise ValueError('supportpick_publishing_not_enabled')
    if env.get('GITHUB_REPOSITORY') != REPO or env.get('GITHUB_REF') != 'refs/heads/main':
        raise ValueError('approved_main_context_required')
    if env.get('GITHUB_RUN_ATTEMPT') != '1':
        raise ValueError('publication_reruns_blocked')
    if env.get('GITHUB_EVENT_NAME') == 'schedule':
        cron = env.get('SUPPORTPICK_THREADS_CRON', '')
        if cron not in CRONS:
            raise ValueError('known_scheduled_slot_required')
        return cron
    if env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch' and env.get('SUPPORTPICK_THREADS_MANUAL_MODE') in ('publish-one-now', 'resume-pending'):
        return 'manual'
    raise ValueError('explicit_publication_context_required')


def validate_ledger(state):
    if (not isinstance(state, dict) or state.get('version') != 1 or state.get('brand') != 'supportpick'
            or state.get('username') != USERNAME or not isinstance(state.get('records'), list)):
        raise ValueError('wrong_or_corrupt_ledger')
    slots, ids = set(), set()
    for r in state['records']:
        if (not isinstance(r, dict) or r.get('status') not in ('pending', 'published')
                or not r.get('benefit_id') or not r.get('slot') or not r.get('run_id')
                or r['slot'] in slots or r['benefit_id'] in ids):
            raise ValueError('invalid_ledger_record')
        stamp(r['slot'])
        if r['status'] == 'published' and (r.get('verified') is not True or not all(str(r.get(k, '')).isdigit() for k in ('main_id', 'detail_id', 'links_id'))):
            raise ValueError('incomplete_published_receipt')
        slots.add(r['slot']); ids.add(r['benefit_id'])
    return state


class Ledger:
    """GitHub Contents GET + SHA guarded PUT; never reset or create on a 404."""
    def __init__(self, token, opener=urllib.request.urlopen):
        self.token, self.opener = token, opener
        if not token:
            raise ValueError('missing_ledger_credential')

    def request(self, method, payload=None):
        url = 'https://api.github.com/repos/' + REPO + '/contents/social/threads-state.json'
        if method == 'GET':
            url += '?ref=' + STATE_BRANCH
        req = urllib.request.Request(url, method=method,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'X-GitHub-Api-Version': '2022-11-28'})
        try:
            with self.opener(req, timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise RuntimeError('ledger_unavailable_or_conflict_do_not_retry_send') from None

    def read(self):
        data = self.request('GET')
        return data['sha'], validate_ledger(json.loads(base64.b64decode(data['content'])))

    def save(self, sha, state):
        validate_ledger(state)
        data = self.request('PUT', {'message': 'Record SupportPick Threads state', 'branch': STATE_BRANCH,
            'sha': sha, 'content': base64.b64encode(json.dumps(state, ensure_ascii=False).encode()).decode()})
        new_sha = data.get('content', {}).get('sha')
        if not new_sha:
            raise RuntimeError('ledger_write_unconfirmed')
        return new_sha


class Threads:
    def __init__(self, token, opener=urllib.request.urlopen, pause=time.sleep):
        if not token:
            raise ValueError('missing_supportpick_threads_token')
        self.token, self.opener, self.pause = token, opener, pause

    def call(self, method, path, params=None):
        query = urllib.parse.urlencode(params or {})
        url = 'https://graph.threads.net/v1.0' + path
        data = None
        if method == 'GET' and query:
            url += '?' + query
        elif method == 'POST':
            data = query.encode()
        req = urllib.request.Request(url, method=method, data=data, headers={
            'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/x-www-form-urlencoded'})
        try:
            with self.opener(req, timeout=30) as response:
                result = json.load(response)
            if not isinstance(result, dict) or result.get('error'):
                raise ValueError()
            return result
        except (urllib.error.URLError, OSError, TimeoutError, ValueError):
            raise RuntimeError('threads_request_failed_or_ambiguous_no_automatic_retry') from None

    def verify_account(self, expected_id):
        me = self.call('GET', '/me', {'fields': 'id,username'})
        uid = str(me.get('id', ''))
        if not expected_id.isdigit() or uid != expected_id or me.get('username', '').casefold() != USERNAME:
            raise ValueError('wrong_threads_account')
        return uid

    def post(self, text, parent=None, image=None):
        args = {'media_type': 'IMAGE' if image else 'TEXT', 'text': text}
        if image:
            args['image_url'] = image
        if parent:
            args['reply_to_id'] = parent
        cid = str(self.call('POST', '/me/threads', args).get('id', ''))
        if not cid.isdigit():
            raise RuntimeError('container_id_missing')
        # Poll read-only status; POSTs are never retried after ambiguity.
        for _ in range(5):
            self.pause(30)
            status = self.call('GET', '/' + cid, {'fields': 'status'}).get('status')
            if status == 'FINISHED':
                break
            if status != 'IN_PROGRESS':
                raise RuntimeError('container_not_publishable')
        else:
            raise RuntimeError('container_not_ready')
        pid = str(self.call('POST', '/me/threads_publish', {'creation_id': cid}).get('id', ''))
        if not pid.isdigit():
            raise RuntimeError('post_receipt_missing')
        # Receipt is intentionally emitted before durable write for reconciliation.
        print('Threads receipt:', pid, flush=True)
        return pid

    def verify(self, pid, text):
        # Threads converts the first brand hashtag to a topic and omits its '#'
        # in returned text. Only this observed transformation is permitted;
        # every other character (including the CTA) must still match exactly.
        expected = {text, text.replace('\n\n#지원금픽 ', '\n\n지원금픽 ', 1)}
        for attempt in range(3):
            row = self.call('GET', '/' + pid, {'fields': 'id,text,permalink'})
            if str(row.get('id')) == pid and row.get('text') in expected and row.get('permalink'):
                return row['permalink']
            if attempt < 2:
                self.pause(2)
        raise RuntimeError('published_post_verification_failed')


def complete_record(store, api, sha, state, record, now):
    keys = ('main_id', 'detail_id', 'links_id')
    stage = record.get('stage', '')
    # Inspect the original stage before changing it. A missing receipt after a
    # sending stage is ambiguous and must never be retried, even during resume.
    for key in keys:
        if stage == key + '_sending' and not record.get(key):
            raise RuntimeError('ambiguous_send_missing_receipt_do_not_resume')
    for index, key in enumerate(keys):
        pid = record.get(key)
        if not pid:
            # Legacy pending content must never be rewritten or sent with links.
            require_link_free(record['texts'][index])
            record['stage'] = key + '_sending'
            sha = store.save(sha, state)
            pid = api.post(record['texts'][index], parent=record.get('main_id') if index else None,
                           image=record.get('image_url') if index == 0 else None)
            record[key] = pid
            sha = store.save(sha, state)
        record[key + '_url'] = api.verify(pid, record['texts'][index])
        record['stage'] = key + '_verified'
        sha = store.save(sha, state)
    record.update(status='published', verified=True, published_at=now.isoformat(), stage='complete')
    store.save(sha, state)
    return {'status': 'published', 'published': True, 'benefit_id': record['benefit_id'],
            'url': record['main_id_url'], 'replies': 2, 'selection': record.get('selection')}


def resume_publication(store, api, now, expected_id, run_id, expected_main_id):
    if not run_id.isdigit() or not expected_main_id.isdigit():
        raise ValueError('explicit_existing_main_receipt_required')
    api.verify_account(expected_id)
    sha, state = store.read()
    validate_ledger(state)
    pending = [r for r in state['records'] if r['status'] == 'pending']
    if len(pending) != 1 or pending[0].get('main_id') != expected_main_id:
        raise ValueError('exactly_one_matching_pending_receipt_required')
    record = pending[0]
    if stamp(record['slot']).date() != now.date() or not fresh(record.get('checked_at'), now):
        raise ValueError('resume_requires_same_day_fresh_source')
    texts = record.get('texts')
    if (not isinstance(texts, list) or len(texts) != 3
            or any(not isinstance(t, str) or len(t) > 500 for t in texts)
            or record.get('content_hash') != hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest()):
        raise ValueError('pending_content_hash_mismatch')
    # Existing reservations count toward the daily cap; resume never appends one.
    result = complete_record(store, api, sha, state, record, now)
    return {**result, 'resumed': True, 'recovery_run_id': run_id}


def publish(feed, store, api, now, cron, run_id, expected_id, assets=None):
    slot = current_slot(now, cron)
    if not run_id.isdigit():
        raise ValueError('github_run_id_required')
    api.verify_account(expected_id)
    sha, state = store.read()
    validate_ledger(state)
    rows = state['records']
    if any(r['status'] != 'published' for r in rows):
        raise RuntimeError('unresolved_publication_reconcile_before_next_post')
    if any(r['slot'] == slot for r in rows):
        raise RuntimeError('slot_already_reserved')
    if sum(stamp(r['slot']).date() == now.date() for r in rows) >= 4:
        raise RuntimeError('daily_limit_reached')
    eligible = candidates(feed, state, now)
    if not eligible:
        return {'status': 'skipped', 'reason': 'no_fresh_eligible_benefit', 'published': False}
    row = copy.deepcopy(eligible[0])
    asset = (assets or {}).get(row['id'], {})
    texts = compose(row)
    image = asset.get('imageUrl') if len(rows) % 2 == 1 else None
    if image and not image_url(image):
        raise ValueError('unapproved_image_url')
    record = {'benefit_id': row['id'], 'slot': slot, 'run_id': run_id, 'status': 'pending',
              'texts': list(texts), 'image_url': image, 'generation': feed.get('generation'),
              'official_url': row['officialUrl'], 'checked_at': row['checkedAt'],
              'selection': selection_info(row)}
    record['content_hash'] = hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest()
    rows.append(record)
    sha = store.save(sha, state)  # CAS durable reservation before first side effect.
    return complete_record(store, api, sha, state, record, now)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('preview', 'publish', 'check-account', 'resume'))
    parser.add_argument('--state', default='collection-state')
    args = parser.parse_args()
    now = datetime.now(KST)
    if args.command == 'check-account':
        api = Threads(os.environ.get('SUPPORTPICK_THREADS_ACCESS_TOKEN', ''))
        api.verify_account(os.environ.get('SUPPORTPICK_THREADS_USER_ID', ''))
        recent = api.call('GET', '/me/threads', {'fields': 'id,text,permalink,timestamp', 'limit': 100})
        result = {'status': 'account_verified', 'username': USERNAME, 'published': False,
                  'profile_link_target': PROFILE_LINK, 'recent_posts': recent.get('data', []),
                  'more_history': bool(recent.get('paging', {}).get('next'))}
    elif args.command == 'resume':
        publication_context(os.environ)
        if os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch' or os.environ.get('SUPPORTPICK_THREADS_MANUAL_MODE') != 'resume-pending':
            raise ValueError('explicit_manual_resume_required')
        result = resume_publication(Ledger(os.environ.get('GITHUB_TOKEN', '')),
            Threads(os.environ.get('SUPPORTPICK_THREADS_ACCESS_TOKEN', '')), now,
            os.environ.get('SUPPORTPICK_THREADS_USER_ID', ''), os.environ.get('GITHUB_RUN_ID', ''),
            os.environ.get('SUPPORTPICK_THREADS_RESUME_MAIN_ID', ''))
    else:
        feed = load_feed(args.state)
        if args.command == 'preview':
            state = {'version': 1, 'brand': 'supportpick', 'username': USERNAME, 'records': []}
            eligible = candidates(feed, state, now)
            result = {'status': 'preview', 'published': False, 'eligible': len(eligible),
                      'profile_link_target': PROFILE_LINK, 'cta': CTA,
                      'selection': selection_info(eligible[0]) if eligible else None,
                      'priority_preview': [{'benefit_id': r['id'], 'title': r['title'],
                                            **selection_info(r)} for r in eligible[:5]],
                      'posts': list(compose(eligible[0])) if eligible else []}
        else:
            cron = publication_context(os.environ)
            assets = json.loads((ROOT / 'social/assets.json').read_text())
            result = publish(feed, Ledger(os.environ.get('GITHUB_TOKEN', '')),
                Threads(os.environ.get('SUPPORTPICK_THREADS_ACCESS_TOKEN', '')), now,
                cron, os.environ.get('GITHUB_RUN_ID', ''),
                os.environ.get('SUPPORTPICK_THREADS_USER_ID', ''), assets)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    Path('threads-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
            out.write('## 지원금픽 Threads 결과\n\n```json\n' + json.dumps(result, ensure_ascii=False, indent=2) + '\n```\n')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, KeyError, TypeError) as exc:
        # Error messages are controlled; no HTTP request objects or tokens printed.
        result = {'status': 'failed', 'published': 'unconfirmed', 'reason': str(exc)[:140],
                  'action': 'Inspect durable ledger and remote posts before retrying.'}
        Path('threads-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit(1) from None

