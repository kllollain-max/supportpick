"""Public-page metadata and a sitemap of real, independently served pages."""
import json
import re
from html import escape
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

PUBLIC_PAGES = ('index.html', 'about.html', 'privacy.html')
DESCRIPTIONS = {
    'about.html': '지원금픽의 공식 정보 출처, 보조금24 자료 범위, 맞춤 혜택의 의미와 이용 방법을 안내합니다.',
    'privacy.html': '지원금픽의 브라우저 기록 보관, 저장한 혜택과 신청 메모의 백업·복원, 개인정보 취급 범위를 안내합니다.',
}
VERIFICATION_NAMES = {'google': 'google-site-verification', 'naver': 'naver-site-verification'}


class PageHead(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ''
        self.description = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = attrs.get('content', '')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def read_verifications(path):
    if path.is_symlink():
        raise ValueError('unsafe_search_verification_source')
    if not path.exists():
        return {}
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or set(value) - set(VERIFICATION_NAMES):
        raise ValueError('invalid_search_verification_config')
    result = {}
    for provider, token in value.items():
        if token is None:
            continue
        if not isinstance(token, str) or not re.fullmatch(r'[A-Za-z0-9_-]{16,256}', token):
            raise ValueError('invalid_search_verification_token')
        result[VERIFICATION_NAMES[provider]] = token
    return result


def public_metadata(source, page, base, verifications):
    head = PageHead()
    head.feed(source.split('</head>', 1)[0])
    description = head.description or DESCRIPTIONS.get(page, '')
    if not head.title.strip() or not description:
        raise ValueError('missing_public_page_metadata')
    canonical = base + ('' if page == 'index.html' else page)
    image = base + 'supportpick-badge.png'
    tags = [f'<link rel="canonical" href="{escape(canonical, quote=True)}">']
    if not head.description:
        tags.append(f'<meta name="description" content="{escape(description, quote=True)}">')
    values = {
        'og:type': 'website', 'og:locale': 'ko_KR', 'og:site_name': '지원금픽',
        'og:title': head.title.strip(), 'og:description': description,
        'og:url': canonical, 'og:image': image, 'og:image:type': 'image/png',
        'og:image:width': '1254', 'og:image:height': '1254',
        'og:image:alt': '지원금픽 · 정부지원금·환급금·생활혜택 안내',
    }
    tags += [f'<meta property="{key}" content="{escape(value, quote=True)}">' for key, value in values.items()]
    twitter = {'twitter:card': 'summary', 'twitter:title': head.title.strip(),
               'twitter:description': description, 'twitter:image': image,
               'twitter:image:alt': values['og:image:alt']}
    tags += [f'<meta name="{key}" content="{escape(value, quote=True)}">' for key, value in twitter.items()]
    if page == 'index.html':
        tags += [f'<meta name="{name}" content="{escape(token, quote=True)}">' for name, token in verifications.items()]
        structured = {'@context': 'https://schema.org', '@type': 'WebSite',
                      'name': '지원금픽', 'url': base, 'inLanguage': 'ko-KR',
                      'description': description}
        payload = json.dumps(structured, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
        tags.append('<script type="application/ld+json">' + payload + '</script>')
    if source.count('</head>') != 1:
        raise ValueError('invalid_public_head')
    return source.replace('</head>', '\n' + '\n'.join(tags) + '\n</head>')


def write_sitemap(output, base):
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    root = ET.Element(f'{{{namespace}}}urlset')
    for page in PUBLIC_PAGES:
        if not (output / page).is_file():
            raise ValueError('sitemap_target_missing')
        entry = ET.SubElement(root, f'{{{namespace}}}url')
        ET.SubElement(entry, f'{{{namespace}}}loc').text = base + ('' if page == 'index.html' else page)
    ET.ElementTree(root).write(output / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
