# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""BibleProject data importer.

Imports BibleProject research data into Voogle's expected structure by:
1. Reading metadata JSONs from source directory
2. Converting VTT transcripts to CSV format
3. Copying slides and asset manifests
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from voogle.bibleproject.vtt_converter import convert_vtt_to_csv


@dataclass
class ImportResult:
    """Result of importing a course.

    Attributes:
        course_slug: The identifier of the imported course
        success: Whether the import completed successfully
        vtt_files_converted: Number of VTT files converted to CSV
        slides_copied: Number of slide files copied
        assets_copied: Whether assets.json was copied
        errors: List of error messages encountered during import
    """

    course_slug: str
    success: bool
    vtt_files_converted: int = 0
    slides_copied: int = 0
    assets_copied: bool = False
    errors: list[str] = field(default_factory=list)


def import_course(course_slug: str, source_dir: Path, target_dir: Path) -> ImportResult:
    """Import a single course from source to target directory.

    Steps:
    1. Read metadata JSONs from source
    2. Generate adapter config
    3. Convert VTT files to CSV
    4. Copy slides
    5. Copy assets.json

    Args:
        course_slug: Identifier for the course (e.g., "intro-to-bible")
        source_dir: Path to the source research data directory
        target_dir: Path to the target Voogle data directory

    Returns:
        ImportResult with details about what was imported
    """
    result = ImportResult(course_slug=course_slug, success=False)
    course_source = source_dir / course_slug
    course_target = target_dir / course_slug

    if not course_source.exists():
        result.errors.append(f"Source directory not found: {course_source}")
        return result

    # Create target directory
    course_target.mkdir(parents=True, exist_ok=True)

    # Step 1 & 2: Read metadata and generate adapter config
    metadata_file = course_source / "metadata.json"
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            # Write adapter config to target
            adapter_config = {
                "course_slug": course_slug,
                "title": metadata.get("title", course_slug),
                "description": metadata.get("description", ""),
                "source": "bibleproject",
            }
            config_path = course_target / "adapter_config.json"
            config_path.write_text(json.dumps(adapter_config, indent=2), encoding="utf-8")
        except (json.JSONDecodeError, OSError) as e:
            result.errors.append(f"Failed to process metadata: {e}")

    # Step 3: Convert VTT files to CSV
    vtt_dir = course_source / "transcripts"
    if vtt_dir.exists():
        csv_dir = course_target / "transcripts"
        csv_dir.mkdir(parents=True, exist_ok=True)
        for vtt_file in vtt_dir.glob("*.vtt"):
            csv_file = csv_dir / (vtt_file.stem + ".csv")
            try:
                convert_vtt_to_csv(vtt_file, csv_file)
                result.vtt_files_converted += 1
            except (ValueError, OSError) as e:
                result.errors.append(f"Failed to convert {vtt_file.name}: {e}")

    # Step 4: Copy slides
    slides_dir = course_source / "slides"
    if slides_dir.exists():
        target_slides_dir = course_target / "slides"
        target_slides_dir.mkdir(parents=True, exist_ok=True)
        for slide_file in slides_dir.iterdir():
            if slide_file.is_file():
                try:
                    shutil.copy2(slide_file, target_slides_dir / slide_file.name)
                    result.slides_copied += 1
                except OSError as e:
                    result.errors.append(f"Failed to copy slide {slide_file.name}: {e}")

    # Step 5: Copy assets.json
    assets_file = course_source / "assets.json"
    if assets_file.exists():
        try:
            shutil.copy2(assets_file, course_target / "assets.json")
            result.assets_copied = True
        except OSError as e:
            result.errors.append(f"Failed to copy assets.json: {e}")

    result.success = len(result.errors) == 0
    return result


def import_all_courses(source_dir: Path, target_dir: Path) -> list[ImportResult]:
    """Import all courses from a source directory.

    Discovers all course directories in source_dir and imports each one.

    Args:
        source_dir: Path to the source research data directory containing course subdirectories
        target_dir: Path to the target Voogle data directory

    Returns:
        List of ImportResult for each course found
    """
    results: list[ImportResult] = []

    if not source_dir.exists():
        return results

    # Find all course directories (directories that contain either metadata.json or transcripts/)
    for item in sorted(source_dir.iterdir()):
        if not item.is_dir():
            continue

        # Check if this looks like a course directory
        has_metadata = (item / "metadata.json").exists()
        has_transcripts = (item / "transcripts").exists()
        has_slides = (item / "slides").exists()
        has_assets = (item / "assets.json").exists()

        if has_metadata or has_transcripts or has_slides or has_assets:
            result = import_course(item.name, source_dir, target_dir)
            results.append(result)

    return results
