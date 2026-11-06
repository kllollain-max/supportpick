"""Guard editorial provenance and later source corrections during integration."""

import json
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContentReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "guides.json").read_text())
        cls.guides = {guide["benefitId"]: guide for guide in cls.registry["guides"]}

    def test_new_ai_review_cannot_extend_validity_or_claim_human_review(self):
        selection = self.registry["improvementReview"]["selected"]
        self.assertEqual(len(selection), 10)
        self.assertEqual(len({entry["benefitId"] for entry in selection}), 10)
        self.assertFalse(self.registry["improvementReview"]["validityExtended"])
        for entry in selection:
            with self.subTest(benefit_id=entry["benefitId"]):
                guide = self.guides[entry["benefitId"]]
                self.assertEqual(
                    guide["humanReview"],
                    {"status": "pending", "reviewer": None, "reviewedAt": None},
                )
                self.assertEqual(guide["validUntil"], entry["validUntilUnchanged"])
                self.assertEqual(guide["aiReview"]["sourceHash"], guide["sourceHash"])
                self.assertGreaterEqual(
                    datetime.fromisoformat(guide["aiReview"]["at"]),
                    datetime.fromisoformat(guide["reviewedAt"]),
                )
                self.assertIs(type(entry["officialViews"]), int)

    def test_integration_preserves_later_source_corrections(self):
        """An older guide enhancement must not erase already verified corrections."""
        earned_income = self.guides["105100000001"]
        deadline = next(
            item["answer"] for item in earned_income["faq"]
            if item["question"] == "일반 신청기간이 지났으면 모든 신청이 끝난 건가요?"
        )
        self.assertIn("2025년 귀속", deadline)
        self.assertIn("2026년 6월 1일", deadline)
        self.assertIn("2026년 12월 1일", deadline)
        deadline_sources = [
            source for source in earned_income["sourceReviews"]
            if "nttSn=1355806" in source["url"]
        ]
        self.assertEqual(len(deadline_sources), 1)
        influenza = self.guides["135200000115"]
        self.assertIn("보조금24 원문과 질병관리청 안내가 다릅니다", influenza["summary"])
        correction = next(
            item["answer"] for item in influenza["faq"]
            if item["question"] == "어린이 2회 접종 기준일이 서로 다르면 무엇을 확인하나요?"
        )
        self.assertIn("2026년 6월 30일", correction)
        self.assertIn("2025년 6월 30일", correction)

    def test_integration_preserves_preparation_faq_from_both_branches(self):
        questions = {item["question"] for item in self.guides["149200000026"]["faq"]}
        self.assertIn("카드 발급 전에 훈련과정을 어떻게 비교해 두면 좋을까요?", questions)
        self.assertIn("훈련을 먼저 결제한 뒤 카드로 모두 돌려받을 수 있나요?", questions)
