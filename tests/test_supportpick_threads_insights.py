import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from supportpick_threads_insights import collect


class FakeResponse:
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, *args): return self.data
    def __init__(self, obj): self.data = json.dumps(obj).encode()


class InsightsTests(unittest.TestCase):
    def test_partial_fields_stay_unknown(self):
        def opener(req, timeout):
            self.assertEqual(req.get_method(), "GET")
            self.assertNotIn("token-secret", req.full_url)
            return FakeResponse({"data": [{"name": "views", "values": [{"value": 150}]},
                                           {"name": "replies", "values": [{"value": 3}]}]})
        result = collect("123456789", "token-secret", opener)
        self.assertEqual(result["views"], 150)
        self.assertEqual(result["comments"], 3)
        self.assertIsNone(result["saves"])

    def test_bad_id_rejected(self):
        with self.assertRaises(ValueError):
            collect("../me", "token")


if __name__ == "__main__":
    unittest.main()
