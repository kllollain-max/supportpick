import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from collect_full import period
from content_quality import conditions, audit


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


if __name__=='__main__':unittest.main()
