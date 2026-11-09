"""Review-only corrections: reject accidental application/publish approvals."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

class OfficialGuideCorrectionTests(unittest.TestCase):
    def test_two_proposals_have_verified_scope_and_no_approval(self):
        p=json.loads((ROOT/"review-only/official-guide-corrections-20261109.json").read_text(encoding="utf-8"))
        self.assertTrue(p["reviewOnly"])
        self.assertEqual({x["benefitId"] for x in p["entries"]},{"140000000176","WII000001460"})
        for row in p["entries"]:
            for k in ("intakeOpenVerified","personalEligibilityVerified",
                      "publicationApproved","validUntilRenewalApproved"):
                self.assertIs(row[k],False)
            self.assertTrue(row["evidence"])
            self.assertTrue(all(urlsplit(url).scheme=="https" for url in row["evidence"]))
    def test_maternity_policy_link_not_spouse_leave(self):
        p=json.loads((ROOT/"review-only/official-guide-corrections-20261109.json").read_text(encoding="utf-8"))
        item=next(x for x in p["entries"] if x["benefitId"]=="WII000001460")
        self.assertIn("SI00000406",item["proposedLink"])
        self.assertNotIn("SI00000395",item["proposedLink"])
        self.assertIn("유산",item["proposedLinkTitle"])
    def test_forest_voucher_has_past_intake_and_future_usage(self):
        p=json.loads((ROOT/"review-only/official-guide-corrections-20261109.json").read_text(encoding="utf-8"))
        item=next(x for x in p["entries"] if x["benefitId"]=="140000000176")
        self.assertIn("1월 30일에 종료",item["proposedNotice"])
        self.assertIn("11월 30일까지 사용",item["proposedNotice"])
        self.assertNotIn("지금 신청",item["proposedNotice"])
    def test_current_public_guide_data_never_modified(self):
        guides=json.loads((ROOT/"guides.json").read_text(encoding="utf-8"))["guides"]
        for sid in ("140000000176","WII000001460"):
            record=next(g for g in guides if g["benefitId"]==sid)
            self.assertTrue(record["validUntil"].startswith("2026-11-18"))
        self.assertIn("SI00000407",str(next(g for g in guides if g["benefitId"]=="WII000001460")["sourceReviews"]))

if __name__=="__main__":unittest.main()
