import sys,unittest
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from eligibility import application_period,application_status,navigation
class PeriodTests(unittest.TestCase):
 def state(self,text,now):return application_status(application_period(text),datetime.fromisoformat(now))
 def test_kst_deadline_day_and_next_day(self):
  text='2026.11.01 ~ 2026.11.05'
  self.assertEqual(self.state(text,'2026-11-05T14:59:59+00:00'),'접수 중')
  self.assertEqual(self.state(text,'2026-11-05T15:00:00+00:00'),'접수 종료')
 def test_explicit_time_and_future(self):
  text='2026.11.05 09:00 ~ 2026.11.05 18:00'
  self.assertEqual(self.state(text,'2026-11-05T08:59:00+09:00'),'접수 예정')
  self.assertEqual(self.state(text,'2026-11-05T18:00:00+09:00'),'접수 중')
  self.assertEqual(self.state(text,'2026-11-05T18:00:01+09:00'),'접수 종료')
 def test_unknown_invalid_budget_and_single_deadline(self):
  for text in ['', '11월 1일~11월 5일','2026.11.05까지','2026.02.30 ~ 2026.03.01','2026.12.01~2026.01.01','상시 신청(예산 소진 시 마감)','수시 모집']:
   self.assertEqual(self.state(text,'2026-11-05T12:00:00+09:00'),'확인 필요',text)
 def test_multiple_rounds_preserved_and_shorthand_year(self):
  text='1차: 2026. 10. 1.~10. 5.\n2차: 2026.11.01~11.17.'
  p=application_period(text);self.assertEqual(len(p['applicationPeriods']),2)
  self.assertEqual(application_status(p,datetime.fromisoformat('2026-11-05T12:00:00+09:00')),'접수 중')
  self.assertEqual(self.state(text+'\n3차: 일정 미정','2026-11-05T12:00:00+09:00'),'확인 필요')
 def test_explicit_ongoing_only(self):
  self.assertEqual(self.state('연중 상시 신청','2026-11-05T12:00:00+09:00'),'상시 신청')
 def test_agency_never_creates_residence_condition(self):
  r=navigation({'region':'서울','regionBasis':'agency_jurisdiction','organization':'서울시','target':'청년 구직자','selection':'소득 기준 원문 확인'})
  self.assertEqual(r['agencyRegion'],'서울');self.assertEqual(r['eligibilityRegions'],[])
  self.assertEqual([t['label'] for t in r['targetGroups']],['청년','구직자'])
 def test_explicit_residence_and_business_evidence(self):
  r=navigation({'target':'강원특별자치도 춘천시에 주민등록을 두고 거주하는 학생'})
  self.assertEqual(r['eligibilityRegions'][0]['regions'],['강원'])
  self.assertEqual(r['eligibilityRegions'][0]['cities'],['춘천시'])
  self.assertEqual(navigation({'target':'경기도에 소재한 사업장'})['eligibilityRegions'][0]['basis'],'business')
 def test_alternative_or_exclusion_never_becomes_rejection(self):
  for text in ['서울 또는 경기도에 거주','거주 지역과 관계없이 전국 신청','서울시 거주자 제외']:
   self.assertEqual(navigation({'target':text})['eligibilityRegionStatus'],'needs_check')
 def test_repeated_same_condition_does_not_change_explicit_to_uncertain(self):
  r=navigation({'target':'강원특별자치도 춘천시에 거주','selection':'강원특별자치도 춘천시에 거주'})
  self.assertEqual(r['eligibilityRegionStatus'],'explicit');self.assertEqual(len(r['eligibilityRegions']),1)
