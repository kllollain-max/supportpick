"""Read-only source/history preparation and queue preview for the AI writer.

The model reads the checked-in master prompt and writes a reviewed JSON queue.
This module never invents prose, publishes a post, or changes an existing ledger.
"""
from __future__ import annotations
import copy
import hashlib
from datetime import timedelta

import supportpick_threads as t
import supportpick_writer as w


def planned_slots(now, records, limit=4):
    used = {r['slot'] for r in records}
    slots = []
    for day in (now, now + timedelta(days=1)):
        for hour in sorted(t.CRONS.values()):
            value = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            if now <= value < now + timedelta(hours=24) and value.isoformat() not in used:
                slots.append(value.isoformat())
    return slots[:limit]


def build_input(feed, state, now, assets):
    rows = t.candidates(feed, state, now)
    history = state['records'][-20:]
    projected = copy.deepcopy(state['records'])
    slots = []
    for index, slot in enumerate(planned_slots(now, projected)):
        sample = rows[index] if len(rows) > index else {'id': ''}
        image = t.select_image(sample, projected, assets)
        slots.append({'slot': slot, 'media_turn': 'IMAGE' if image else 'TEXT',
                      'expected_image': image,
                      'note': 'Recompute from actual successful ledger before preparation and publication.'})
        projected.append({'slot': slot, 'image_url': image})
    return {
        'schema_version': 'supportpick.writer-input.v1', 'status': 'writer_input', 'published': False,
        'brand': 'supportpick', 'username': t.USERNAME, 'generated_at': now.isoformat(),
        'prompt_path': w.PROMPT_PATH,
        'prompt_sha256': hashlib.sha256((t.ROOT / w.PROMPT_PATH).read_bytes()).hexdigest(),
        'source_generation': feed['generation'], 'cta': t.CTA,
        'hard_character_limit': 500, 'reply_count': 0, 'same_day_distinct_patterns': True,
        'slots': slots, 'history': history, 'eligible_count': len(rows),
        'candidate_priority': [{'id': r['id'], 'title': r['title'], **t.selection_info(r)} for r in rows[:30]],
        'candidate_facts': [{'source_fingerprint': w.source_fingerprint(r), 'row': r} for r in rows[:12]],
        'instructions': ['Read the entire master prompt before writing.',
                         'Verify current official eligibility, amounts and application state.',
                         'Collection timestamps alone do not prove that applications are open.',
                         'Record why higher-ranked candidates cannot be verified.',
                         'Reserve four different valid patterns per KST date; never fabricate urgency.',
                         'Write the queue with a fresh blob SHA; never modify publication records.',
                         'Recompute future media turns if an earlier slot was not published.']}


def preview_queue(feed, state, queue, now, assets):
    projected = copy.deepcopy(state['records'])
    entries = sorted(queue.get('entries', []), key=lambda e: e.get('slot', ''))
    results = []
    for entry in entries:
        slot = entry.get('slot', '')
        if any(r['slot'] == slot for r in projected):
            continue
        if t.stamp(slot) + timedelta(hours=2) <= now:
            continue
        eligible = t.candidates(feed, {'records': projected}, now)
        row = next((r for r in eligible if r['id'] == entry.get('benefit_id')), None)
        try:
            if row is None:
                raise ValueError('reviewed_benefit_no_longer_eligible')
            image = t.select_image(row, projected, assets)
            validation_time = max(now, t.stamp(slot))
            row, draft, metadata = w.validate_ready_entry(queue, eligible, projected, validation_time, slot, image)
            selection = t.reviewed_selection(row, eligible, queue)
            results.append({'slot': slot, 'benefit_id': row['id'], 'status': 'READY',
                            'pattern': metadata['pattern'], 'media_turn': draft['media']['turn'], 'selection': selection,
                            'post_text': draft['post_text'], 'char_count': len(draft['post_text']),
                            'validation_time': validation_time.isoformat(),
                            'source_recheck_required_at_publish': True})
            projected.append({'slot': slot, 'benefit_id': row['id'], 'image_url': image,
                              'writer': metadata, 'texts': [draft['post_text']]})
        except (ValueError, RuntimeError) as exc:
            results.append({'slot': slot, 'benefit_id': entry.get('benefit_id'),
                            'status': 'HOLD', 'reason': str(exc)})
    return {'status': 'preview', 'published': False, 'source_generation': feed['generation'],
            'ready': sum(r['status'] == 'READY' for r in results), 'drafts': results}
