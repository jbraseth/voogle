# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Import BibleProject courses as Channels with Episodes.

Reads metadata from research repository and creates proper Voogle records.
"""

from __future__ import annotations

import json
from pathlib import Path

from voogle.db import database
from voogle.models import Channel, Episode

RESEARCH_METADATA = Path("/home/hs-dev/projects/bibleproject-research/data/metadata")


async def import_bibleproject_data(metadata_path: Path | None = None) -> None:
    """Import all BibleProject courses as Channels with Episodes.

    Args:
        metadata_path: Optional path to metadata directory.
            Defaults to RESEARCH_METADATA.
    """
    metadata_dir = metadata_path or RESEARCH_METADATA

    if not metadata_dir.exists():
        print(f"Metadata directory not found: {metadata_dir}")
        return

    # Connect to database
    if not database.is_connected:
        await database.connect()

    for course_dir in sorted(metadata_dir.iterdir()):
        if not course_dir.is_dir():
            continue

        course_name = course_dir.name  # e.g., "ephesians"

        # Create or get Channel
        # Use feed as unique identifier since it has a unique constraint
        feed_url = f"bibleproject:{course_name}"
        existing = await Channel.objects.filter(feed=feed_url).get_or_none()

        if existing:
            channel = existing
        else:
            channel = await Channel.objects.create(
                title=course_name.replace("-", " ").title(),
                feed=feed_url,
                kind="bibleproject",
                language="en",
                description=f"BibleProject {course_name.replace('-', ' ').title()} course",
                url=f"https://bibleproject.com/classroom/{course_name}",
                local_folder="",
                image="",
            )

        # Create Episodes from session metadata
        episodes_created = 0
        for session_file in sorted(course_dir.glob("*.json")):
            metadata = json.loads(session_file.read_text())

            session_id = metadata.get("session_id", session_file.stem)
            title = metadata.get("session_title", f"Session {session_id}")
            session_url = metadata.get("session_url", "")

            # Use first mux_playback_id (primary video)
            mux_ids = metadata.get("mux_playback_ids", [])
            mux_playback_id = mux_ids[0] if mux_ids else None

            # Check if episode already exists (by url unique constraint)
            existing_ep = await Episode.objects.filter(url=session_url).get_or_none()
            if existing_ep:
                # Update existing episode with mux_playback_id if not set
                if not existing_ep.mux_playback_id and mux_playback_id:
                    await existing_ep.update(mux_playback_id=mux_playback_id)
            else:
                await Episode.objects.create(
                    channel=channel,
                    title=title,
                    description="",
                    guid=f"bibleproject:{course_name}:{session_id}",
                    url=session_url,
                    mux_playback_id=mux_playback_id,
                )
                episodes_created += 1

        print(f"Imported {course_name}: {episodes_created} new episodes")
