"""Narrow, expiring source-reviewed schedules; never infer hours from API dates."""
import re
from datetime import datetime, timezone
from html import escape
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')
FIELDS = ('scope', 'applicationStart', 'applicationEnd', 'followupLabel', 'followupEnd',
          'sourceUrl', 'reviewedAt', 'validUntil')


def instant(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})', value):
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def checked(value, current=None):
    current = current or datetime.now(timezone.utc)
    if not isinstance(value, dict):
        return None
    if any(not isinstance(value.get(k), str) or not value[k].strip() or len(value[k]) > 100
           for k in ('scope', 'followupLabel')):
        return None
    try:
        u = urlsplit(value.get('sourceUrl', ''))
        if u.scheme != 'https' or u.hostname != 'www.kosaf.go.kr' or u.username or u.password or u.port:
            return None
    except ValueError:
        return None
    start, end, followup, reviewed, until = [instant(value.get(k)) for k in
        ('applicationStart', 'applicationEnd', 'followupEnd', 'reviewedAt', 'validUntil')]
    if (not all((start, end, followup, reviewed, until)) or not start < end <= followup
            or not reviewed <= current < until or (until - reviewed).total_seconds() > 30 * 86400):
        return None
    return {k: value[k] for k in FIELDS}


def state(value, current):
    schedule = checked(value, current)
    if not schedule:
        return None
    if current >= instant(schedule['applicationEnd']):
        return 'ended'
    return 'upcoming' if current < instant(schedule['applicationStart']) else 'dated'


def label(value, current):
    return {'ended': '공식 안내상 해당 차수 신청 마감',
            'upcoming': '공식 안내상 해당 차수 신청 전',
            'dated': '해당 차수 일정 · 실제 접수 확인'}.get(state(value, current))


def render(value, current):
    s = checked(value, current)
    if not s:
        return ''
    stamp = lambda key: instant(s[key]).astimezone(KST).strftime('%Y.%m.%d %H:%M KST')
    return ('<section class="detail-block verified-schedule" data-schedule-until="'
            + escape(s['validUntil'], quote=True) + '"><h2>공식 공고와 대조한 차수 일정</h2><p>'
            + escape(s['scope']) + '</p><dl class="card-meta"><dt>신청 시작</dt><dd>' + stamp('applicationStart')
            + '</dd><dt>신청 마감</dt><dd>' + stamp('applicationEnd') + '</dd><dt>'
            + escape(s['followupLabel']) + ' 마감</dt><dd>' + stamp('followupEnd')
            + '</dd></dl><p>후속 절차의 기한은 새 신청의 연장 기한이 아닙니다. 학교·은행의 수납 일정이나 개인별 보완 기한은 별도 확인하세요. 다른 학기·차수에는 적용하지 않습니다.</p>'
            + '<p>대조 확인: ' + stamp('reviewedAt') + ' · <a href="' + escape(s['sourceUrl'], quote=True)
            + '" target="_blank" rel="noopener noreferrer">한국장학재단 해당 일정 ↗</a></p></section>')
