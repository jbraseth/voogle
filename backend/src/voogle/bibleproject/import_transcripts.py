# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Import BibleProject VTT transcripts into Voogle."""

from dataclasses import dataclass, field
from pathlib import Path

from voogle import storage
from voogle.bibleproject.vtt_converter import convert_vtt_to_csv
from voogle.db import database
from voogle.models import Episode


@dataclass
class ImportResult:
    success_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)


async def import_all_transcripts(transcripts_dir: Path) -> ImportResult:
    """Import all VTT transcripts from research repo."""
    result = ImportResult()

    if not database.is_connected:
        await database.connect()

    for course_dir in sorted(transcripts_dir.iterdir()):
        if not course_dir.is_dir():
            continue

        course_name = course_dir.name

        for vtt_file in sorted(course_dir.glob("*.vtt")):
            session_id = vtt_file.stem
            guid = f"bibleproject:{course_name}:{session_id}"

            # Find episode
            episode = await Episode.objects.filter(guid=guid).get_or_none()
            if not episode:
                result.errors.append(f"Episode not found: {guid}")
                result.error_count += 1
                continue

            # Get target CSV path
            csv_path = await storage.transcription_file(episode)
            csv_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                # Convert VTT to CSV
                convert_vtt_to_csv(vtt_file, csv_path)

                # Mark episode as transcribed
                await episode.update(transcribed=True)
                result.success_count += 1
                print(f"Imported: {guid}")
            except Exception as e:
                result.errors.append(f"Failed {guid}: {e}")
                result.error_count += 1

    return result
