import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benefit_analysis import coverage_report, related_analysis


class ContentValueEvidenceTests(unittest.TestCase):
    def test_coverage_does_not_treat_a_related_article_as_a_review_of_every_detail(self):
        report = coverage_report({'indexableDetails': 100, 'guideIds': ['B55353000001'],
                                  'heldReasons': {}}, {'B55353000001': {}})
        self.assertEqual(report['detailsWithoutMatchedPreparationGuide'], 99)
        self.assertEqual(report['analysisLinkedBenefitIds'], ['B55353000001'])
        self.assertEqual(report['siteWideContentValueReview'], 'incomplete')
        self.assertFalse(report['resubmissionRecommended'])

    def test_missing_and_held_records_do_not_inflate_article_coverage(self):
        report = coverage_report({'indexableDetails': 0, 'guideIds': [],
                                  'heldReasons': {'135200005003': ['verify source']}},
                                 {'135200005003': {}})
        self.assertEqual(report['analysisLinkedBenefitIds'], [])

    def test_unrelated_benefits_are_not_given_a_template_article_link(self):
        self.assertEqual(related_analysis('UNRELATED'), '')
        self.assertIn('emergency-vs-livelihood-2026.html', related_analysis('135200005003'))
        self.assertNotIn('energy-voucher-2026.html', related_analysis('135200005003'))
