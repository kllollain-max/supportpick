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
        r=audit({'guides':[guide('2026-11-15')]},{'articles':[article()]},date(2026,11,9))
        self.assertEqual(r['status_counts']['review_due_soon'],1)
        self.assertEqual(r['status_counts']['fresh_review'],1)
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
