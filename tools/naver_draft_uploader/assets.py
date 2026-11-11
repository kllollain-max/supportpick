from __future__ import annotations

from pathlib import Path


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


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
        if p.stat().st_size <= 0:
            problems.append(f"image_{index}:empty")
        if p.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            problems.append(f"image_{index}:unsupported_format")

    return problems
