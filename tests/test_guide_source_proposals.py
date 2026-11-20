"""Review-only source proposal guard: no claiming fresh reviews or intake."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

class GuideSourceProposalsTests(unittest.TestCase):
    def test_only_known_missing_sources_and_official_hosts(self):
        p=json.loads((ROOT/"review-only/guide-source-proposals-20261109.json").read_text(encoding="utf-8"))
        guides=json.loads((ROOT/"guides.json").read_text(encoding="utf-8"))["guides"]
        self.assertIs(p["reviewOnly"],True)
        self.assertEqual({x["benefitId"] for x in p["proposals"]},{"171000000005","SD0000016138"})
        guide_ids={x["benefitId"] for x in guides}
        for row in p["proposals"]:
            self.assertIn(row["benefitId"],guide_ids)
            self.assertIs(row["intakeOpenVerified"],False)
            self.assertTrue(row["proposedSource"]["note"].strip())
            u=urlsplit(row["proposedSource"]["url"])
            self.assertEqual(u.scheme,"https")
            self.assertIn(u.hostname,{"m.epostlife.go.kr","www.mohw.go.kr"})
            self.assertNotIn("validUntil",row)
            self.assertNotIn("status",row)
    def test_original_public_guides_remain_unmodified(self):
        guides=json.loads((ROOT/"guides.json").read_text(encoding="utf-8"))["guides"]
        subset=[g for g in guides if g["benefitId"] in {"171000000005","SD0000016138"}]
        self.assertEqual(len(subset),2)
        self.assertTrue(all(len(x["sourceReviews"])==1 for x in subset))
        self.assertTrue(all(x["validUntil"].startswith("2026-11-18") for x in subset))

if __name__=="__main__":
    unittest.main()
