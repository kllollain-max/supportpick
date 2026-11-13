"""Fail closed on high-impact benefit identity confusion in editorial review.

Only validates read-only review metadata and current guide identity. This test does
not extend review expiry dates, turn on benefit intake, or publish any changes.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "benefit-fact-review-20261109.md"
GUIDES = ROOT / "guides.json"

class BenefitReviewIdentityTests(unittest.TestCase):
    def test_maternity_grant_is_not_spouse_paternity_leave(self):
        text = REVIEW.read_text(encoding="utf-8")
        guides = json.loads(GUIDES.read_text(encoding="utf-8"))["guides"]
        item = next(g for g in guides if g.get("benefitId") == "WII000001460")
        self.assertIn("### 출산전후(유산·사산)휴가 급여 (\x60WII000001460\x60)", text)
        self.assertNotIn("### 배우자 출산휴가급여 (\x60WII000001460\x60)", text)
        self.assertIn("유산·사산휴가", " ".join(item.get("checks", [])))
        self.assertIn("회사", " ".join(item.get("steps", [])))
        self.assertIn("SI00000407", text)
        self.assertNotIn("SI00000395", text)

    def test_review_only_never_renews_live_expiry(self):
        guides = json.loads(GUIDES.read_text(encoding="utf-8"))["guides"]
        self.assertEqual(len(guides), 20)
        self.assertTrue(all(g.get("validUntil", "").startswith("2026-11-18") for g in guides))
        self.assertEqual(len({g["benefitId"] for g in guides}), 20)

if __name__ == "__main__":
    unittest.main()
