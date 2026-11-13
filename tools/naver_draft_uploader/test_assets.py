import tempfile
import unittest
from pathlib import Path

from assets import validate_image_assets


class AssetTests(unittest.TestCase):
    def test_unmaterialized_library_image_is_blocked(self):
        problems = validate_image_assets([
            {"source_file_id": "file-1", "path": None}
        ])
        self.assertIn("image_0:not_materialized", problems)

    def test_local_nonempty_png_passes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.png"
            p.write_bytes(b"png")
            self.assertEqual([], validate_image_assets([
                {"source_file_id": "file-1", "path": str(p)}
            ]))

    def test_duplicate_source_is_blocked(self):
        problems = validate_image_assets([
            {"source_file_id": "file-1", "path": None},
            {"source_file_id": "file-1", "path": None},
        ])
        self.assertIn("image_1:duplicate_source", problems)


if __name__ == "__main__":
    unittest.main()
