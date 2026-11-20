import unittest
from datetime import date
from tools.benefit_review_queue import build_queue

def guide(sid, valid="2026-11-18T09:00:00Z", independent=True):
    refs=[{"url":"https://plus.gov.kr/a?svcId="+sid}]
    if independent: refs.append({"url":"https://www.mohw.go.kr/a"})
    return {"benefitId":sid,"validUntil":valid,"status":"reviewed",
            "sourceReviews":refs,"faq":[{"question":"q","answer":"a"}]}
def article(sid, valid="2026-11-18T09:00:00Z"):
    return {"benefitId":sid,"validUntil":valid,"status":"published",
            "url":"https://m.blog.naver.com/example/100","publicationVerified":True}

class ReviewQueueTests(unittest.TestCase):
    def test_missing_agency_source_prioritized(self):
        r=build_queue({"guides":[guide("171000000005",independent=False),guide("X")]},
                      {"articles":[article("135200000115")]},date(2026,11,9))
        self.assertEqual(r["records"],3)
        self.assertEqual(r["source_gap_records"],1)
        self.assertEqual(r["items"][0]["benefit_id"],"171000000005")
        self.assertEqual(r["blog_body_not_observed_on_20261109"],1)
        self.assertTrue(all(not item["renewal_authorized"] and
                       not item["full_text_review_confirmed"] and
                       not item["intake_open_verified"] for item in r["items"]))
    def test_historical_public_read_does_not_approve_a_review(self):
        r=build_queue({"guides":[]},{"articles":[article("137100000236")]},date(2026,11,9))
        self.assertTrue(r["items"][0]["body_observed_on_20261109"])
        self.assertFalse(r["items"][0]["full_text_review_confirmed"])
    def test_expired_reviews_still_queued(self):
        r=build_queue({"guides":[guide("X","2026-11-01T00:00:00Z")]},
                      {"articles":[]},date(2026,11,9))
        self.assertEqual(r["items"][0]["existing_review_status"],"expired_review")
    def test_malformed_input_fail_closed(self):
        with self.assertRaises(ValueError):
            build_queue({"guides":{}},{"articles":[]},date(2026,11,9))

if __name__=="__main__":
    unittest.main()
