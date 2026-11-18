import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_detail_pages import BASE, NOW, row
from application_guides import write_guides
from detail_pages import write_details


class MaternalServiceTests(unittest.TestCase):
    def test_confirmed_stale_deadline_is_held_without_deleting_original_or_other_rows(self):
        original=row('PTR000050390');original['selection']='OLD_DEADLINE_BODY_SENTINEL'
        saved=copy.deepcopy(original);other=row('unrelated');other['title']='무관한 지원사업'
        registry=json.loads((Path(__file__).resolve().parents[1]/'guides.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            result=write_details(output,{original['id']:original,other['id']:other},{},BASE,registry,{},'success',NOW)
            html=(output/'benefits/PTR000050390/index.html').read_text()
            self.assertNotIn('OLD_DEADLINE_BODY_SENTINEL',html)
            self.assertIn('noindex,follow',html)
            self.assertIn('https://www.mohw.go.kr/menu.es?mid=a10711020100',html)
            self.assertIn('../../guides/maternal-service-application-use-refund-2026.html',html)
            self.assertEqual(result['report']['heldDetails'],1)
            self.assertIn('index,follow',(output/'benefits/unrelated/index.html').read_text())
            self.assertEqual(original,saved)

    def test_current_article_separates_clocks_and_links_only_existing_detail_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            dates=dict(write_guides(output,BASE,{}))
            html=(output/'guides/maternal-service-application-use-refund-2026.html').read_text()
            self.assertEqual(dates['guides/maternal-service-application-use-refund-2026.html'],'2026-11-18')
            self.assertIn('출산일로부터60일까지',html)
            self.assertIn('원칙적으로 출산일로부터90일 이내',html)
            self.assertIn('종료 후60일 이내',html)
            self.assertIn('https://129.go.kr/faq/faq03.do',html)
            self.assertNotIn('href="../benefits/PTR000050390/"',html)
