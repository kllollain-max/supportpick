"""Guard editorial provenance, expiry and human-review separation."""
import json,unittest
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
class ContentReviewTests(unittest.TestCase):
 def test_new_ai_review_cannot_extend_validity_or_claim_human_review(self):
  registry=json.loads((ROOT/'guides.json').read_text());selection=registry['improvementReview']['selected']
  self.assertEqual(len(selection),10);self.assertEqual(len({x['benefitId'] for x in selection}),10)
  self.assertFalse(registry['improvementReview']['validityExtended'])
  for entry in selection:
   guide=next(g for g in registry['guides'] if g['benefitId']==entry['benefitId'])
   self.assertEqual(guide['humanReview'],{'status':'pending','reviewer':None,'reviewedAt':None})
   self.assertEqual(guide['validUntil'],entry['validUntilUnchanged'])
   self.assertEqual(guide['aiReview']['sourceHash'],guide['sourceHash'])
   self.assertGreaterEqual(datetime.fromisoformat(guide['aiReview']['at']),datetime.fromisoformat(guide['reviewedAt']))
   self.assertIs(type(entry['officialViews']),int)
