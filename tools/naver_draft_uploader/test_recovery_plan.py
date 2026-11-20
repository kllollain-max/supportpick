import unittest

from recovery_plan import recovery_action


class RecoveryPlanTests(unittest.TestCase):
    def test_save_unknown_always_searches_existing_draft(self):
        self.assertEqual(
            "SEARCH_EXISTING_DRAFT_FIRST",
            recovery_action({"state": "SAVE_STATUS_UNKNOWN"})
        )

    def test_save_clicked_always_searches_existing_draft(self):
        self.assertEqual(
            "SEARCH_EXISTING_DRAFT_FIRST",
            recovery_action({"state": "SAVE_CLICKED"})
        )

    def test_verified_needs_no_action(self):
        self.assertEqual("NO_ACTION", recovery_action({"state": "VERIFIED"}))


if __name__ == "__main__":
    unittest.main()
