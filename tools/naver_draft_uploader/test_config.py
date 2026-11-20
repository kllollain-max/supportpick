import unittest

from config import UploaderConfig


class ConfigTests(unittest.TestCase):
    def test_default_is_disabled_and_safe(self):
        cfg = UploaderConfig()
        self.assertFalse(cfg.enabled)
        self.assertFalse(cfg.allow_publish)
        self.assertEqual([], cfg.validate())

    def test_publish_enablement_is_rejected(self):
        cfg = UploaderConfig(allow_publish=True)
        self.assertIn("auto_publish_must_remain_disabled", cfg.validate())

    def test_parallel_execution_is_rejected(self):
        cfg = UploaderConfig(max_parallel=2)
        self.assertIn("parallelism_must_be_one", cfg.validate())


if __name__ == "__main__":
    unittest.main()
