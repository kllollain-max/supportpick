import copy, json, re, tempfile, unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
from detail_pages import write_details
from search_metadata import write_sitemap
from verify_release import Document,inspect,verify
from test_detail_pages import BASE,row

NOW=datetime(2026,11,19,7,tzinfo=timezone.utc)

class IdentityTitleTests(unittest.TestCase):
    def test_same_names_show_source_agencies_and_only_affected_metadata_dates_change(self):
        a=row('one');a.update(title='같은 지원사업',organization='첫 기관 & 지원')
        b=row('two');b.update(title='같은  지원사업',organization='둘째 기관')
        c=row('other');c['title']='다른 단독 사업';original=copy.deepcopy((a,b,c))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);r=write_details(out,{x['id']:x for x in (a,b,c)},{},BASE,{'guides':[]},{},'success',NOW)
            titles=[]
            for x in (a,b,c):
                s=(out/'benefits'/x['id']/'index.html').read_text();d=Document();d.feed(s);titles.append(d.title)
                if x is not c:self.assertIn(x['organization'],d.title);self.assertEqual(d.meta['og:title'],d.title)
            self.assertEqual(len(set(titles)),3)
            dates=dict(r['entries']);self.assertEqual(dates['benefits/one/'],'2026-11-19');self.assertEqual(dates['benefits/other/'],'2026-11-17')
        self.assertEqual((a,b,c),original)

    def test_repeated_name_and_agency_use_ids_without_releasing_held_content(self):
        a=row('one');b=row('two');a['title']=b['title']='동일명 사업';b['support']='다른 차수 내용'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);r=write_details(out,{'one':a,'two':b},{},BASE,{'guides':[],'holds':{'two':{'reason':'확인 중'}}},{},'success',NOW)
            texts=[(out/'benefits'/sid/'index.html').read_text() for sid in ['one','two']]
            self.assertIn('자료 one',texts[0]);self.assertIn('자료 two',texts[1]);self.assertIn('내용 확인 필요',texts[1])
            self.assertIn('noindex,follow',texts[1]);self.assertNotIn('다른 차수 내용',texts[1]);self.assertEqual(r['report']['heldDetails'],1)

    def test_verifier_rejects_duplicate_titles_even_when_canonicals_are_different(self):
        a=row('one');a['title']='첫 사업';b=row('two');b['title']='둘째 사업'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);r=write_details(out,{'one':a,'two':b},{},BASE,{'guides':[]},{},'success',NOW)
            (out/'search-report.json').write_text(json.dumps(r['report']))
            with patch('search_metadata.PUBLIC_PAGES', []):
                write_sitemap(out,BASE,r['entries'])
            result=verify(out);self.assertEqual(result['uniqueTitles'],result['sitemapUrls'])
            first=Document();first.feed((out/'benefits/one/index.html').read_text())
            p=out/'benefits/two/index.html';p.write_text(re.sub(r'<title>.*?</title>','<title>'+first.title+'</title>',p.read_text(),count=1))
            with self.assertRaisesRegex(ValueError,'duplicate_document_title'):verify(out)

    def test_empty_and_multiple_title_elements_are_not_valid_documents(self):
        url=BASE+'about.html';head='<link rel="canonical" href="'+url+'"><meta name="robots" content="index,follow"><meta name="description" content="안내"><meta property="og:title" content="안내">'
        for title in ['', '<title> </title>','<title>하나</title><title>둘</title>']:
            with self.assertRaisesRegex(ValueError,'invalid_title'):inspect('<html><head>'+head+title+'</head><body><h1>안내</h1></body></html>',url)
