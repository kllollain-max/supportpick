import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from application_guides import write_guides
from benefit_analysis import related_analysis,coverage_report,ARTICLE_REVIEW_DATES
from youth_employment_analysis import SLUG
from test_detail_pages import row,BASE,NOW
from detail_pages import write_details
from verify_release import inspect

class YouthEmploymentGuideTests(unittest.TestCase):
    def test_static_two_way_discovery_and_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);a=row('149200005016');a['title']='청년일자리도약장려금'
            r=write_details(out,{a['id']:a},{},BASE,{}, {},'success',NOW)
            entries=write_guides(out,BASE,{a['id']:a})
            path='guides/'+SLUG+'.html';html=(out/path).read_text()
            inspect(html,BASE+path)
            self.assertIn((path,'2026-11-25'),entries)
            self.assertIn('href="../benefits/149200005016/"',html)
            self.assertIn('../../'+path,(out/'benefits/149200005016/index.html').read_text())
            self.assertIn('149200005016',coverage_report(r['report'],{a['id']:a})['analysisLinkedBenefitIds'])
    def test_other_service_is_not_relabelled_as_hiring_incentive(self):
        self.assertEqual(related_analysis('UNRELATED',row('UNRELATED')),'')
        self.assertNotIn(SLUG,related_analysis('149200000026',row('149200000026')))
    def test_verified_date_is_specific_to_new_article(self):
        self.assertEqual(ARTICLE_REVIEW_DATES[SLUG],'2026-11-25')
        self.assertEqual(ARTICLE_REVIEW_DATES['training-card-vs-employment-support-2026'],'2026-11-24')
