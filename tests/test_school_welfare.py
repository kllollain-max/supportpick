import copy
import tempfile
import unittest
from pathlib import Path
from application_guides import write_guides
from detail_pages import write_details
from test_detail_pages import BASE, NOW, row


class SchoolWelfareTests(unittest.TestCase):
    def test_placeholder_source_survives_with_editorial_connection(self):
        a=row('SD0000015525');a.update(title='교육복지 우선 지원',summary='-',
            target='경북 교육취약계층 학생',targetPreview='경북 교육취약계층 학생',
            method='사업학교별로 참여 학생 모집 시 신청',documents='해당없음')
        original=copy.deepcopy(a)
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);result=write_details(out,{a['id']:a},{},BASE,{'guides':[]},{},'success',NOW)
            text=(out/'benefits/SD0000015525/index.html').read_text()
            self.assertIn('지원대상 원문 일부: 경북 교육취약계층 학생',text)
            self.assertIn('사업학교별로 참여 학생 모집 시 신청',text)
            self.assertIn('../../guides/school-welfare-vs-education-benefit-2026.html',text)
            self.assertNotIn('noindex,follow',text)
            self.assertEqual(result['report']['heldDetails'],0)
        self.assertEqual(a,original)

    def test_new_guide_is_dated_without_nonexistent_detail_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);dates=dict(write_guides(out,BASE,{}))
            text=(out/'guides/school-welfare-vs-education-benefit-2026.html').read_text()
            self.assertNotIn('href="../benefits/SD0000015525/"',text)
            self.assertIn('전국 학생 개인의 선정 기준이 아닙니다',text)
            self.assertIn('이 질문 메모는 지원금픽의 준비 예시이며 공식 필수 서류 목록이 아닙니다',text)
            self.assertEqual(dates['guides/school-welfare-vs-education-benefit-2026.html'],'2026-11-19')
            self.assertEqual(dates['guides/housing-benefit-2026.html'],'2026-11-17')


if __name__=='__main__':unittest.main()
