import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from collect_full import period
from content_quality import conditions, audit, reading_gaps, review_queue
from datetime import datetime,timezone


class SourceQualityTests(unittest.TestCase):
    def test_shared_year_single_range_is_parsed_but_ambiguous_rounds_are_not(self):
        for text in ['2026. 7.1.(수)~11.17.(화)', '2026년 7월 15일 10:00~7월 30일 17:00']:
            self.assertEqual(period(text)['endDate'], '2026-11-17' if '11.17' in text else '2026-07-30')
        for text in ['7.1.~11.17.', '2026.12.20.~1.10.', '2026.2.31.~3.10.', '2026.1.1.~2.1. / 3.1.~4.1.', '1차 2026.1.1.~2.1. 2차 3.1.~4.1.']:
            self.assertIsNone(period(text)['endDate'])

    def test_conditions_only_use_official_fields_and_valid_age_pair(self):
        row={'title':'청년 1인가구', 'rawSource':{'supportConditions':{'JA0110':18,'JA0111':39,'JA0404':'Y','JA0403':'N'}}}
        self.assertEqual(conditions(row),{'ageMin':18,'ageMax':39,'households':['1인가구']})
        for age in [True,'18',-1,250,None]:
            row['rawSource']['supportConditions']['JA0110']=age
            self.assertIsNone(conditions(row)['ageMin'])
        self.assertEqual(conditions({'title':'청년 1인가구'})['households'],[])

    def test_quality_report_does_not_mutate_or_remove_originals(self):
        rows={'A':{'title':'짧은 안내','organization':'기관','period':'공고 시','sourceUpdatedAt':{}}}
        original=copy.deepcopy(rows)
        result=audit(rows)
        self.assertEqual(rows,original)
        self.assertIn('missing_support',result['reviewCandidates']['A'])
        self.assertFalse(result['automaticDeletion'])
        self.assertFalse(result['automaticIndexingChange'])

    def test_reading_notes_only_describe_missing_or_ambiguous_source_fields(self):
        r={'selection':'중복 조건은 공고 확인','documents':'신분증','contact':'기관','period':'상시신청'}
        self.assertEqual(reading_gaps(r),[])
        r['selection']='';r['target']='지원대상 본문에 실제 선정 조건이 제공됨'
        self.assertEqual(reading_gaps(r),[])
        r['documents']='';r['period']='5.1.~5.31.'
        gaps=reading_gaps(r)
        self.assertEqual(len(gaps),2)
        self.assertTrue(any('구비서류' in x for x in gaps))
        self.assertTrue(any('신청기간' in x for x in gaps))
        self.assertFalse(any('선정기준' in x or '문의처' in x for x in gaps))

    def test_full_review_queue_keeps_all_ids_and_never_treats_view_counts_as_quality(self):
        def r(sid,views):
            return {'id':sid,'title':sid,'organization':'기관','target':'대상','support':'내용',
                    'method':'방문','documents':'서류','contact':'문의','summary':'기관이 제공한 대상과 지원내용을 구분하여 읽는 충분한 길이의 자료 설명입니다',
                    'period':'상시신청','officialUrl':'https://plus.gov.kr/',
                    'sourceUpdatedAt':{'list':'20260101','detail':'2026-01-01'},
                    'rawSource':{'serviceList':{'조회수':views}}}
        rows={sid:r(sid,views) for sid,views in [('HELD',1),('DUP1',10),('DUP2',20),('GAP',5),('FULL',999999)]}
        rows['GAP']['documents']='';rows['DUP1']['title']=rows['DUP2']['title']='같은 이름'
        original=copy.deepcopy(rows)
        q=review_queue(rows,audit(rows),{'heldReasons':{'HELD':['개별 공식 사실 확인']},'guideIds':[]},datetime(2026,11,17,tzinfo=timezone.utc))
        self.assertEqual(rows,original)
        self.assertEqual({x['id'] for x in q['items']},set(rows))
        self.assertEqual([x['id'] for x in q['items']],['HELD','DUP2','DUP1','GAP','FULL'])
        self.assertEqual(q['items'][-1]['reviewState'],'추가 가치 검토')
        self.assertFalse(q['automaticIndexingChange'])
        self.assertFalse(q['automaticMerge'])


if __name__=='__main__':unittest.main()
