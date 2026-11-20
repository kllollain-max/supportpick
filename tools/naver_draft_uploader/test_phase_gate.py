import unittest

from phase_gate import PhaseResult, can_promote, next_phase


class PhaseGateTests(unittest.TestCase):
    def test_phase1_requires_exactly_one_verified(self):
        ok, problems = can_promote([PhaseResult("supportpick-1", "VERIFIED")], 1)
        self.assertTrue(ok)
        self.assertEqual([], problems)
        self.assertEqual(2, next_phase(1, [PhaseResult("supportpick-1", "VERIFIED")]))

    def test_phase2_blocks_any_non_verified_item(self):
        results = [
            PhaseResult("supportpick-1", "VERIFIED"),
            PhaseResult("supportpick-2", "RETRY_PENDING"),
            PhaseResult("supportpick-3", "VERIFIED"),
        ]
        ok, problems = can_promote(results, 2)
        self.assertFalse(ok)
        self.assertTrue(any("not_verified" in p for p in problems))

    def test_phase3_blocks_duplicate_or_data_loss(self):
        results = [
            PhaseResult(f"supportpick-{i}", "VERIFIED") for i in range(5)
        ]
        results[2].duplicate_detected = True
        ok, problems = can_promote(results, 3)
        self.assertFalse(ok)
        self.assertIn("supportpick-2:duplicate_detected", problems)


if __name__ == "__main__":
    unittest.main()
