import copy
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from test_detail_pages import row, BASE, NOW
from detail_pages import write_details, benefit_path, material_hash, reviewed_guide, safe_reference
from forest_transport_analysis import source_advisory, FOREST_NOTICE


class ForestSourceReadingTests(unittest.TestCase):
    def test_annual_reminder_gets_year_specific_context_without_rewriting_or_holding(self):
        a=row('140000000176');a.update(period='매년 12월 신청시기 알림',support='1인당 연 10만원')
        original=copy.deepcopy(a)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            result=write_details(output,{a['id']:a},{},BASE,{}, {}, 'success',NOW)
            html=(output/benefit_path(a['id'])/'index.html').read_text()
            self.assertIn('신청과 사용기한 구분:',html)
            self.assertIn('매년 12월 신청시기 알림',html)
            self.assertIn(FOREST_NOTICE.replace('&','&amp;'),html)
            self.assertEqual(result['report']['heldDetails'],0)
            self.assertIn('content="index,follow"',html)
        self.assertEqual(a,original)
        self.assertEqual(source_advisory({**a,'period':'2027.1.4.~2027.1.29.'}),'')
        self.assertEqual(source_advisory({**a,'id':'OTHER'}),'')

    def test_official_forest_references_retain_source_and_expiry_guards(self):
        a=row('140000000176')
        g={'benefitId':a['id'],'sourceHash':material_hash(a),'status':'reviewed',
           'reviewedAt':(NOW-timedelta(days=1)).isoformat(),'validUntil':(NOW+timedelta(days=14)).isoformat(),
           'summary':'시설과 결제 확인','checks':['대상','시설','기간'],'steps':['선정','예약','결제'],
           'sourceReviews':[{'url':'https://forestcard.or.kr/main/main.do','note':'공식 이용권 안내'},
                            {'url':'https://www.forestcard.or.kr/mobile/useInfo/mobileUseUtilizeList.do?menuId=1110100','note':'사용가능 기관'}]}
        registry={'guides':[g]}
        self.assertIs(reviewed_guide(a,registry,NOW),g)
        self.assertIsNone(reviewed_guide(a,registry,NOW+timedelta(days=14)))
        self.assertIsNone(reviewed_guide({**a,'support':'새 조건'},registry,NOW))
        for link in ['https://forestcard.or.kr.example.com/','https://other.forestcard.or.kr/',
                     'http://forestcard.or.kr/','https://forestcard.or.kr:8443/',
                     'https://user:password@forestcard.or.kr/']:
            self.assertFalse(safe_reference(link))


if __name__=='__main__':unittest.main()
