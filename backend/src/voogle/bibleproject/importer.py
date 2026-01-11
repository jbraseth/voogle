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

    Handles the research data structure:
      source_dir/metadata/{course}/     -> session JSONs
      source_dir/transcripts/{course}/  -> VTT files
      source_dir/slides/{course}/       -> slide JSONs
      source_dir/assets/assets.json     -> global assets manifest

    Args:
        course_slug: Identifier for the course (e.g., "abraham")
        source_dir: Path to the source research data directory
        target_dir: Path to the target Voogle data directory

    Returns:
        ImportResult with details about what was imported
    """
    result = ImportResult(course_slug=course_slug, success=False)

    # Research data structure paths
    metadata_dir = source_dir / "metadata" / course_slug
    transcripts_dir = source_dir / "transcripts" / course_slug
    slides_dir = source_dir / "slides" / course_slug
    assets_file = source_dir / "assets" / "assets.json"

    # Check if course exists in any of the expected locations
    if not any([metadata_dir.exists(), transcripts_dir.exists(), slides_dir.exists()]):
        result.errors.append(f"Course not found in source: {course_slug}")
        return result

    # Target directory for this course
    course_target = target_dir / "local" / "bibleproject" / course_slug
    course_target.mkdir(parents=True, exist_ok=True)

    # Step 1: Read metadata JSONs and generate adapter config
    if metadata_dir.exists():
        sessions = []
        for meta_file in sorted(metadata_dir.glob("*.json")):
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                sessions.append({
                    "session_id": meta_file.stem,
                    "session_title": meta.get("session_title", meta_file.stem),
                    "mux_id": meta.get("mux_playback_ids", [None])[0],
                    "pdf_url": meta.get("pdf_url"),
                })
            except (json.JSONDecodeError, OSError) as e:
                result.errors.append(f"Failed to read {meta_file.name}: {e}")

        # Write adapter config
        adapter_config = {
            "course_slug": course_slug,
            "course_title": course_slug.replace("-", " ").title(),
            "sessions": sessions,
        }
        config_path = course_target / "config.json"
        config_path.write_text(json.dumps(adapter_config, indent=2), encoding="utf-8")

    # Step 2: Convert VTT files to CSV
    if transcripts_dir.exists():
        csv_dir = course_target / "transcripts"
        csv_dir.mkdir(parents=True, exist_ok=True)
        for vtt_file in sorted(transcripts_dir.glob("*.vtt")):
            csv_file = csv_dir / (vtt_file.stem + ".csv")
            try:
                convert_vtt_to_csv(vtt_file, csv_file)
                result.vtt_files_converted += 1
            except (ValueError, OSError) as e:
                result.errors.append(f"Failed to convert {vtt_file.name}: {e}")

    # Step 3: Copy slides
    if slides_dir.exists():
        target_slides_dir = course_target / "slides"
        target_slides_dir.mkdir(parents=True, exist_ok=True)
        for slide_file in sorted(slides_dir.glob("*.json")):
            try:
                shutil.copy2(slide_file, target_slides_dir / slide_file.name)
                result.slides_copied += 1
            except OSError as e:
                result.errors.append(f"Failed to copy slide {slide_file.name}: {e}")

    # Step 4: Copy global assets.json (once per import, to bibleproject root)
    bp_root = target_dir / "local" / "bibleproject"
    target_assets = bp_root / "assets.json"
    if assets_file.exists() and not target_assets.exists():
        try:
            shutil.copy2(assets_file, target_assets)
            result.assets_copied = True
        except OSError as e:
            result.errors.append(f"Failed to copy assets.json: {e}")

    result.success = len(result.errors) == 0
    return result


def import_all_courses(source_dir: Path, target_dir: Path) -> list[ImportResult]:
    """Import all courses from a source directory.

    Discovers courses from the metadata/ subdirectory structure.

    Args:
        source_dir: Path to the source research data directory
        target_dir: Path to the target Voogle data directory

    Returns:
        List of ImportResult for each course found
    """
    results: list[ImportResult] = []

    if not source_dir.exists():
        return results

    # Find all course slugs from metadata directory
    metadata_root = source_dir / "metadata"
    if not metadata_root.exists():
        return results

    for item in sorted(metadata_root.iterdir()):
        if item.is_dir():
            result = import_course(item.name, source_dir, target_dir)
            results.append(result)

    return results
