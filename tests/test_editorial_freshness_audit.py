import unittest
from datetime import date
from tools.editorial_freshness_audit import audit

def guide(valid='2026-12-01'):
    return {'benefitId':'A1','status':'reviewed','validUntil':valid+'T00:00:00+00:00'}

def article(valid='2026-12-01', verified=True):
    return {'benefitId':'B1','status':'published','publicationVerified':verified,
            'url':'https://m.blog.naver.com/bible_el/123',
            'validUntil':valid+'T00:00:00+00:00'}

class EditorialFreshnessTests(unittest.TestCase):
    def test_fresh_and_due(self):
        r=audit({'guides':[guide('2026-11-11')]},{'articles':[article()]},date(2026,11,9))
        self.assertEqual(r['status_counts']['review_due_soon'],1)
        self.assertEqual(r['status_counts']['fresh_review'],1)
        self.assertEqual(r['review_window_days'],3)
    def test_a_new_fourteen_day_review_is_not_immediately_due(self):
        g={'guides':[guide('2026-11-23')]}
        before=repr(g)
        r=audit(g,{'articles':[]},date(2026,11,9))
        self.assertEqual(r['upcoming_review_count'],0)
        self.assertEqual(repr(g),before)
        self.assertEqual(audit(g,{'articles':[]},date(2026,11,9),14)['upcoming_review_count'],1)
    def test_due_window_includes_the_boundary_and_retains_expired_reviews(self):
        r=audit({'guides':[guide('2026-11-12'),guide('2026-11-13'),guide('2026-11-08')]},
                {'articles':[]},date(2026,11,9))
        self.assertEqual(r['status_counts'],{'review_due_soon':1,'fresh_review':1,'expired_review':1})
        for window in (-1,91):
            with self.assertRaises(ValueError):audit({'guides':[]},{'articles':[]},date(2026,11,9),window)
    def test_expired_and_unknown(self):
        r=audit({'guides':[guide('2026-10-01'),{'benefitId':'A2','status':'reviewed'}]},
                {'articles':[]},date(2026,11,9))
        self.assertEqual(r['urgent_review_count'],2)
    def test_unverified_blog_does_not_count_as_fresh(self):
        r=audit({'guides':[]},{'articles':[article(verified=False)]},date(2026,11,9))
        self.assertEqual(r['status_counts']['publication_not_verified'],1)
    def test_invalid_source_fails(self):
        with self.assertRaises(ValueError):
            audit({'guides':{}},{'articles':[]},date(2026,11,9))
if __name__=='__main__': unittest.main()
