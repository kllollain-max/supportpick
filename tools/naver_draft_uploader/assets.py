from __future__ import annotations

from pathlib import Path
import hashlib


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_image_assets(images: list[dict]) -> list[str]:
    problems = []
    seen = set()

    for index, image in enumerate(images):
        source_file_id = image.get("source_file_id")
        path_value = image.get("path")

        if source_file_id and source_file_id in seen:
            problems.append(f"image_{index}:duplicate_source")
        if source_file_id:
            seen.add(source_file_id)

        if not path_value:
            problems.append(f"image_{index}:not_materialized")
            continue

        p = Path(path_value)
        if not p.exists():
            problems.append(f"image_{index}:missing")
            continue
        if not p.is_file():
            problems.append(f"image_{index}:not_file")
            continue

        size = p.stat().st_size
        if size <= 0:
            problems.append(f"image_{index}:empty")
        if p.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            problems.append(f"image_{index}:unsupported_format")

        expected_size = image.get("size_bytes")
        if expected_size is not None and size != int(expected_size):
            problems.append(f"image_{index}:size_mismatch")

        expected_sha = image.get("sha256")
        if expected_sha and _sha256(p) != expected_sha:
            problems.append(f"image_{index}:sha256_mismatch")

    return problems
