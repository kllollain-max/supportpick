"""Validate reviewed SupportPick drafts before the publisher reserves a slot.

This module does not generate text, send requests, change a queue or post to
Threads. The writer follows the checked-in master prompt and supplies evidence;
these deterministic guards bind that review to the actual source, slot and asset.
They are not a substitute for reading the official source and reviewing its facts.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = 'social/supportpick-writer-master-prompt.txt'
QUEUE_PATH = 'social/threads-writer-queue.json'
QUEUE_SCHEMA = 'supportpick.queue.v1'
WRITER_SCHEMA = 'supportpick.writer.v1'
USERNAME = 'hid_1004'
CTA = '자세한 사항은 프로필링크 확인'
COUNT_METHOD = 'python_len_including_spaces_and_newlines'
KST = ZoneInfo('Asia/Seoul')
PATTERNS = frozenset(f'P{i}' for i in range(1, 10))
MAX_AGE = timedelta(hours=24)

# Include the collector's actual full-detail fields, not only its card summary.
# A new source generation or changed popularity must not invalidate unchanged
# reviewed facts; changed amounts, units, conditions and source text must do so.
FACT_FIELDS = (
    'id', 'title', 'organization', 'officialUrl', 'summary', 'target',
    'targetPreview', 'method', 'period', 'periodKind', 'startDate', 'endDate',
    'region', 'regionBasis', 'regionEvidence', 'category', 'audience',
    'support', 'supportType', 'supportTypes', 'selection', 'documents',
    'contact', 'applicationUrl', 'supportDetails', 'selectionCriteria',
    'sourceConflicts',
)
RAW_VOLATILE = frozenset(('조회수', '수정일시', 'checkedAt', 'generation'))
ACCESS_METHODS = frozenset(('OPENED_OFFICIAL', 'PROVIDED_OFFICIAL_TEXT', 'UPSTREAM_VERIFIED'))

TEXT_LINK = re.compile(
    r'(?:[a-z][a-z0-9+.-]*://|www\.|mailto:|tel:)[^\s<>]*'
    r'|(?:[a-z0-9-]+\.)+(?:[a-z]{2,63}|xn--[a-z0-9-]+)(?:[/?#][^\s<>]*)?'
    r'|(?:[가-힣a-z0-9-]+\.)+한국(?:[/?#][^\s<>]*)?', re.IGNORECASE)
IMAGE_URL = re.compile(
    r'https://raw\.githubusercontent\.com/kllollain-max/supportpick/main/'
    r'social/images/[A-Za-z0-9_-]+\.(?:jpg|jpeg|png)')
ENGAGEMENT = re.compile(
    r'(?:댓글|공유|팔로우|좋아요|저장)(?:을|를|로|도|하고|해|하|해두|해놓|눌러|남겨|부탁)'
    r'.{0,18}(?:세요|줘|주세요|부탁|드려|해요)'
    r'|(?:DM|디엠)(?:으로|을|를|주|보내|받|드릴|드려)'
    r'|(?:댓글|공유|팔로우|좋아요|저장)(?:해요|해주세요|하세요|부탁|해두세요|해놓으세요)',
    re.IGNORECASE)
GUARANTEES = re.compile(
    r'무조건(?:받|지급|입금|선정)|신청만하면(?:입금|지급|받)'
    r'|모르면나만손해|정부가숨기는돈|아무도모르는지원금'
    r'|(?:청년이면|여성이면|자영업자면|누구나|전국민)(?:모두|다)(?:받|지급|입금)')


def _fail(reason):
    # Do not echo source text, URLs, requests or credentials in failure reports.
    raise ValueError(reason)


def _stamp(value, reason='writer_timestamp_invalid'):
    try:
        if not isinstance(value, str) or not value:
            _fail(reason)
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            _fail(reason)
        return parsed.astimezone(KST)
    except (TypeError, ValueError, OverflowError):
        _fail(reason)


def _now(value):
    if not isinstance(value, datetime) or value.tzinfo is None:
        _fail('writer_aware_now_required')
    return value.astimezone(KST)


def _json_bytes(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, OverflowError):
        _fail('writer_source_not_json')


def source_fingerprint(row):
    """Hash all published factual fields and the original Gov24 detail records."""
    if not isinstance(row, dict) or not isinstance(row.get('id'), str):
        _fail('writer_source_invalid')
    payload = {key: row.get(key) for key in FACT_FIELDS}
    raw = row.get('rawSource')
    if raw is not None and not isinstance(raw, dict):
        _fail('writer_source_invalid')
    payload['rawSource'] = {}
    for name in ('serviceList', 'serviceDetail', 'supportConditions'):
        source = (raw or {}).get(name)
        if source is not None and not isinstance(source, dict):
            _fail('writer_source_invalid')
        payload['rawSource'][name] = (
            {key: value for key, value in source.items() if key not in RAW_VOLATILE}
            if source is not None else None)
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


def prompt_sha256(prompt_path=None):
    path = Path(prompt_path) if prompt_path is not None else ROOT / PROMPT_PATH
    try:
        content = path.read_bytes()
    except OSError:
        _fail('writer_master_prompt_unavailable')
    if not content.strip():
        _fail('writer_master_prompt_unavailable')
    return hashlib.sha256(content).hexdigest()


def _normalized(text):
    normalized = unicodedata.normalize('NFKC', text)
    return ''.join(c for c in normalized if unicodedata.category(c) != 'Cf')


def opening(text):
    """Return the actual first nonempty line for the history record."""
    return next((line.strip() for line in str(text or '').splitlines() if line.strip()), '')


def normalized_opening(text):
    return re.sub(r'[^\w가-힣]', '', _normalized(opening(text)).casefold())


def require_publication_text(text):
    if not isinstance(text, str) or not text or text != text.strip():
        _fail('writer_post_text_required')
    if len(text) > 500:
        _fail('writer_post_over_500_characters')
    if text.count(CTA) != 1 or text.splitlines()[-1] != CTA:
        _fail('writer_exact_final_cta_required')
    visible = _normalized(text)
    # Inspect both normal text and common address evasions. Removing whitespace
    # only for this check also detects "p l u s . g o v . k r" without altering
    # the actual post or its reviewed hash.
    address_check = re.sub(r'[\[({]\s*(?:\.|dot|점)\s*[\])}]', '.', visible,
                           flags=re.IGNORECASE)
    address_check = re.sub(r'(?<=[A-Za-z0-9])\s*(?:점|dot)\s*(?=[A-Za-z0-9])',
                           '.', address_check, flags=re.IGNORECASE)
    compact = re.sub(r'\s+', '', address_check)
    if (TEXT_LINK.search(visible) or TEXT_LINK.search(compact)
            or re.search(r'[가-힣]+\s*점\s*(?:컴|넷|케이알|씨오엠|com|net|org|kr|co|io)(?:\b|/|\s|$)',
                         visible, re.IGNORECASE)):
        _fail('writer_link_free_publication_required')
    if re.search(r'#[\w가-힣]', visible):
        _fail('writer_hashtags_disabled')
    action_text = re.sub(r'\s+', '', visible[:-len(CTA)])
    if ENGAGEMENT.search(action_text):
        _fail('writer_additional_engagement_request')
    if GUARANTEES.search(action_text):
        _fail('writer_unsupported_guarantee')


def _pattern(value):
    if not isinstance(value, str) or value not in PATTERNS:
        _fail('writer_pattern_required')
    return value


def _record_pattern(record):
    if record.get('pattern'):
        return record['pattern']
    meta = record.get('writer')
    if isinstance(meta, dict):
        review = meta.get('review')
        return meta.get('pattern') or (review.get('pattern') if isinstance(review, dict) else None)
    return None  # Legacy records remain readable; their pattern is not invented.


def _record_text(record):
    texts = record.get('texts')
    if isinstance(texts, list) and texts and isinstance(texts[0], str):
        return texts[0]
    return record.get('post_text') or ''


def queue_entry(queue, slot, prompt_path=None):
    """Return one unambiguous slot entry; no fallback to old composed text."""
    if (not isinstance(queue, dict) or queue.get('schema_version') != QUEUE_SCHEMA
            or queue.get('brand') != 'supportpick' or queue.get('username') != USERNAME
            or not isinstance(queue.get('entries'), list)):
        _fail('writer_queue_invalid')
    digest = prompt_sha256(prompt_path)
    if queue.get('prompt_sha256') != digest:
        _fail('writer_prompt_hash_mismatch')
    wanted = _stamp(slot, 'writer_slot_invalid')
    found, slots = [], set()
    for entry in queue['entries']:
        if (not isinstance(entry, dict) or not isinstance(entry.get('benefit_id'), str)
                or not entry['benefit_id'] or not isinstance(entry.get('writer'), dict)):
            _fail('writer_queue_entry_invalid')
        instant = _stamp(entry.get('slot'), 'writer_slot_invalid')
        if instant in slots:
            _fail('writer_duplicate_queue_slot')
        slots.add(instant)
        if instant == wanted:
            found.append(entry)
    if len(found) != 1:
        _fail('writer_ready_slot_missing')
    return found[0]


def _valid_ref(value):
    if not isinstance(value, str) or not value.strip():
        return False
    if '://' not in value:
        return True  # A supplied official document name is a valid source ref.
    try:
        url = urlsplit(value)
        return (url.scheme == 'https' and bool(url.hostname) and not url.username
                and not url.password and url.port in (None, 443))
    except ValueError:
        return False


def _evidence(review, row, prepared, now, expected_image):
    evidence = review.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        _fail('writer_evidence_required')
    factual, image_review = [], []
    for item in evidence:
        if (not isinstance(item, dict) or not isinstance(item.get('access_method'), str)
                or item['access_method'] not in ACCESS_METHODS
                or not _valid_ref(item.get('source_ref'))
                or not isinstance(item.get('claims_supported'), list)
                or not item['claims_supported']
                or any(not isinstance(c, str) or not c.strip() for c in item['claims_supported'])):
            _fail('writer_evidence_unverified')
        when = _stamp(item.get('verified_at'), 'writer_evidence_timestamp_required')
        if not timedelta(0) <= now - when <= MAX_AGE or when > prepared:
            _fail('writer_evidence_stale_or_future')
        if expected_image and item['source_ref'] == expected_image:
            image_review.append(item)
            continue
        same_reference = item['source_ref'] in (row.get('officialUrl'), row.get('applicationUrl'))
        same_document = (item.get('source_id') == row['id']
                         and '://' not in item['source_ref']
                         and item['access_method'] in ('PROVIDED_OFFICIAL_TEXT', 'UPSTREAM_VERIFIED'))
        # A department's current notice often has a different URL from Gov24's
        # record. Bind that explicitly opened notice to the same program ID.
        # This checks the declared binding and HTTPS shape; official ownership
        # and the notice's facts still have to be reviewed by the writer.
        opened_program_notice = (item.get('source_id') == row['id']
                                 and item['access_method'] == 'OPENED_OFFICIAL'
                                 and item['source_ref'].startswith('https://'))
        if same_reference or same_document or opened_program_notice:
            factual.append(item)
    if not factual:
        _fail('writer_source_evidence_not_bound')
    if expected_image and not image_review:
        _fail('writer_image_review_evidence_required')
    return factual


def _boundary(value):
    if value in (None, ''):
        return None
    if not isinstance(value, str):
        _fail('writer_source_period_invalid')
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            return date.fromisoformat(value)
        return _stamp(value, 'writer_source_period_invalid')
    except ValueError:
        _fail('writer_source_period_invalid')


def _is_before(instant, bound):
    return instant < bound if isinstance(bound, datetime) else instant.date() < bound


def _is_after(instant, bound):
    return instant >= bound if isinstance(bound, datetime) else instant.date() > bound


def _availability(review, row, now, slot, factual):
    status = review.get('application_status')
    if status not in ('OPEN', 'ALWAYS', 'UPCOMING'):
        _fail('writer_application_not_publishable')
    start, end = _boundary(row.get('startDate')), _boundary(row.get('endDate'))
    reference_time = max(now, slot)
    if end is not None and _is_after(reference_time, end):
        _fail('writer_application_closed_before_publication')
    future = start is not None and _is_before(reference_time, start)
    if status == 'UPCOMING':
        if not future:
            _fail('writer_upcoming_start_required')
        if re.search(r'지금\s*신청|현재\s*접수\s*중|오늘부터\s*신청', review.get('_post_text', '')):
            _fail('writer_upcoming_claims_open')
    elif future:
        _fail('writer_application_not_open_yet')
    if status == 'ALWAYS':
        ongoing = row.get('periodKind') == 'ongoing' or re.search(r'상시|연중|수시', str(row.get('period') or ''))
        # A separately opened, current official notice can resolve a sparse API
        # period field. It must be declared in the actual evidence, not inferred
        # merely from a PASS flag or an existing source URL.
        clarified = any(e['access_method'] == 'OPENED_OFFICIAL'
                        and any(re.search(r'상시|연중|수시', c) for c in e['claims_supported'])
                        for e in factual)
        if not ongoing and not clarified:
            _fail('writer_always_status_needs_evidence')
    if status == 'OPEN' and end is None and row.get('periodKind') != 'ongoing':
        confirmed = any(e['access_method'] == 'OPENED_OFFICIAL'
                        and any(re.search(r'접수\s*중|신청\s*가능|이용\s*가능|운영\s*중', c)
                                for c in e['claims_supported']) for e in factual)
        if not confirmed:
            _fail('writer_open_status_needs_evidence')


def _media(entry, writer, checks, expected_image):
    media = writer.get('media')
    if not isinstance(media, dict):
        _fail('writer_media_required')
    if expected_image is None:
        if (media.get('turn') != 'TEXT' or media.get('asset_id') is not None
                or media.get('check') != 'NOT_REQUIRED' or checks.get('media') != 'NOT_REQUIRED'
                or entry.get('asset_sha256') is not None):
            _fail('writer_text_media_mismatch')
        if re.search(r'(?:사진|이미지)(?:을|를)?\s*보면|이미지에\s*정리', writer['post_text']):
            _fail('writer_text_depends_on_image')
        return None
    if (not isinstance(expected_image, str) or not IMAGE_URL.fullmatch(expected_image)
            or media.get('turn') != 'IMAGE' or media.get('asset_id') != expected_image
            or media.get('check') != 'MATCHED' or checks.get('media') != 'PASS'
            or not isinstance(media.get('alt_text'), str) or not media['alt_text'].strip()):
        _fail('writer_image_media_mismatch')
    image_path = ROOT / 'social/images' / expected_image.rsplit('/', 1)[-1]
    try:
        actual_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
    except OSError:
        _fail('writer_image_asset_unavailable')
    if entry.get('asset_sha256') != actual_hash:
        _fail('writer_image_asset_hash_mismatch')
    return actual_hash


def _diversity(queue, entry, records, slot, text, pattern):
    day = slot.date()
    occupied = {}
    for record in records:
        when = _stamp(record.get('slot'), 'writer_history_slot_invalid')
        if when.date() != day:
            continue
        occupied[when] = (record.get('benefit_id'), _record_pattern(record))
    for other in queue['entries']:
        if other is entry or other['writer'].get('status') != 'READY':
            continue
        when = _stamp(other['slot'], 'writer_slot_invalid')
        if when.date() != day:
            continue
        other_review = other['writer'].get('review')
        if not isinstance(other_review, dict):
            _fail('writer_review_required')
        other_pattern = _pattern(other_review.get('pattern'))
        if when in occupied:
            # A retained queue entry for an already published slot is historical.
            if occupied[when][0] != other['benefit_id']:
                _fail('writer_queue_history_slot_conflict')
            continue
        occupied[when] = (other['benefit_id'], other_pattern)
    if any(existing_pattern == pattern for _, existing_pattern in occupied.values()):
        _fail('writer_same_day_pattern_repeated')
    known_patterns = [p for _, p in occupied.values() if p is not None]
    if any(not isinstance(p, str) or p not in PATTERNS for p in known_patterns):
        _fail('writer_history_pattern_invalid')
    if len(known_patterns) != len(set(known_patterns)):
        _fail('writer_same_day_pattern_repeated')
    if len(occupied) >= 4:
        _fail('writer_daily_slot_limit')
    current_opening = normalized_opening(text)
    history = [_record_text(record) for record in records[-20:]]
    history += [other['writer'].get('post_text') or '' for other in queue['entries']
                if other is not entry and other['writer'].get('status') == 'READY'
                and _stamp(other['slot']).date() == day]
    if current_opening and any(normalized_opening(previous) == current_opening for previous in history):
        _fail('writer_opening_repeated')


def validate_ready_entry(queue, eligible, records, now, slot, expected_image, prompt_path=None):
    """Return ``(source_row, writer_output, ledger_metadata)`` or fail closed.

    ``eligible`` must come from the existing fresh-source candidate filter.
    ``expected_image`` must come from the existing rotation for this entry's
    selected row and the current durable publication ledger. Neither is chosen
    by the writer. The returned original text is never silently rewritten.
    """
    now = _now(now)
    planned = _stamp(slot, 'writer_slot_invalid')
    entry = queue_entry(queue, slot, prompt_path)
    if not planned <= now < planned + timedelta(hours=2):
        _fail('writer_outside_publication_slot')
    if not isinstance(eligible, list) or not isinstance(records, list):
        _fail('writer_source_or_history_invalid')
    writer = entry['writer']
    if writer.get('schema_version') != WRITER_SCHEMA or writer.get('status') != 'READY':
        _fail('writer_not_ready')
    candidates = [r for r in eligible if isinstance(r, dict) and r.get('id') == entry['benefit_id']]
    if len(candidates) != 1:
        _fail('writer_candidate_no_longer_eligible')
    row = candidates[0]
    if any(not isinstance(record, dict) for record in records):
        _fail('writer_source_or_history_invalid')
    if any(record.get('benefit_id') == row['id'] for record in records):
        _fail('writer_benefit_already_reserved')
    if any(_stamp(record.get('slot'), 'writer_history_slot_invalid') == planned for record in records):
        _fail('writer_slot_already_reserved')
    if any(other is not entry and other['benefit_id'] == row['id']
           and other['writer'].get('status') == 'READY' for other in queue['entries']):
        _fail('writer_benefit_queued_twice')
    if writer.get('selected_program_id') != row['id']:
        _fail('writer_program_id_mismatch')
    actual_fingerprint = source_fingerprint(row)
    if entry.get('source_fingerprint') != actual_fingerprint:
        _fail('writer_source_changed_requires_review')
    if not isinstance(entry.get('source_generation'), str) or not entry['source_generation']:
        _fail('writer_source_generation_required')
    prepared = _stamp(entry.get('prepared_at'))
    expires = _stamp(entry.get('expires_at'))
    if not prepared <= now < expires or not timedelta(0) < expires - prepared <= MAX_AGE:
        _fail('writer_draft_expired_or_future')
    text = writer.get('post_text')
    require_publication_text(text)
    if writer.get('draft_text') is not None or writer.get('reply_texts') != []:
        _fail('writer_single_final_post_required')
    review = writer.get('review')
    if not isinstance(review, dict):
        _fail('writer_review_required')
    if _stamp(review.get('planned_at'), 'writer_planned_at_required') != planned:
        _fail('writer_planned_slot_mismatch')
    pattern = _pattern(review.get('pattern'))
    checks = review.get('checks')
    if (not isinstance(checks, dict) or any(checks.get(key) != 'PASS' for key in
            ('facts', 'current_status', 'eligibility_and_units', 'cta_and_no_links', 'length'))):
        _fail('writer_required_check_not_passed')
    if type(review.get('char_count')) is not int or review['char_count'] != len(text):
        _fail('writer_character_count_mismatch')
    if not isinstance(review.get('count_method'), str) or not review['count_method'].strip():
        _fail('writer_character_count_method_required')
    if review.get('missing_info') != [] or review.get('hold_reasons') != []:
        _fail('writer_unresolved_review_items')
    if not isinstance(review.get('warnings'), list) or any(not isinstance(x, str) for x in review['warnings']):
        _fail('writer_review_warnings_invalid')
    if any(not isinstance(review.get(key), str) or not review[key].strip()
           for key in ('reader', 'central_message', 'selection_reason')):
        _fail('writer_editorial_review_required')
    if review.get('interest_basis') not in ('OBSERVED_METRICS', 'ESTIMATED'):
        _fail('writer_interest_basis_required')
    if review['interest_basis'] == 'OBSERVED_METRICS':
        listing = (row.get('rawSource') or {}).get('serviceList') or {}
        views = listing.get('조회수')
        valid_views = type(views) is int and 0 <= views <= 10**18
        if isinstance(views, str) and len(views.strip()) <= 30:
            value = views.strip()
            valid_views = bool(re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', value))
            valid_views = valid_views and int(value.replace(',', '')) <= 10**18
        if listing.get('서비스ID') != row['id'] or not valid_views:
            _fail('writer_observed_metric_missing')
    if review.get('duplicate_check') not in ('CHECKED', 'NO_HISTORY', 'NEW_INFORMATION'):
        _fail('writer_duplicate_check_failed')
    if records and review['duplicate_check'] == 'NO_HISTORY':
        _fail('writer_available_history_not_reviewed')
    factual = _evidence(review, row, prepared, now, expected_image)
    _availability({**review, '_post_text': text}, row, now, planned, factual)
    asset_hash = _media(entry, writer, checks, expected_image)
    history = writer.get('next_history_record')
    if (not isinstance(history, dict) or history.get('program_id') != row['id']
            or history.get('pattern') != pattern
            or history.get('media_turn') != ('IMAGE' if expected_image else 'TEXT')
            or normalized_opening(history.get('opening')) != normalized_opening(text)
            or not isinstance(history.get('structure'), str) or not history['structure'].strip()):
        _fail('writer_next_history_mismatch')
    _diversity(queue, entry, records, planned, text, pattern)
    metadata = {
        'schema_version': WRITER_SCHEMA, 'pattern': pattern,
        'prompt_sha256': queue['prompt_sha256'], 'source_fingerprint': actual_fingerprint,
        'source_generation': entry['source_generation'], 'prepared_at': entry['prepared_at'],
        'expires_at': entry['expires_at'], 'application_status': review['application_status'],
        'opening': opening(text), 'structure': history['structure'],
        'media_turn': writer['media']['turn'], 'asset_sha256': asset_hash,
        'char_count': len(text), 'count_method': COUNT_METHOD,
        'evidence': review['evidence'], 'checks': checks,
    }
    return row, writer, metadata
