# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Router for serving local media files."""
import os

import fastapi
from fastapi.responses import FileResponse

from voogle import settings

router = fastapi.APIRouter(prefix="/local", tags=["local"])


@router.get(
    "/{channel}/{filename:path}",
    summary="Serve local media files",
    response_class=FileResponse,
)
async def serve_local_media(channel: str, filename: str) -> FileResponse:
    """Serve a local media file from the media folder.

    Args:
        channel: The channel folder name (slugified channel identifier)
        filename: The filename within the channel folder

    Returns:
        The media file as a FileResponse

    Raises:
        HTTPException 404: If the file doesn't exist or path traversal detected
    """
    media_folder = settings.settings.media_folder
    requested_path = media_folder / channel / filename

    # Resolve to absolute path and verify it's within media folder
    # This prevents path traversal attacks (e.g., ../../../etc/passwd)
    try:
        resolved = requested_path.resolve(strict=False)
        media_resolved = media_folder.resolve(strict=False)
    except (OSError, ValueError) as err:
        raise fastapi.HTTPException(
            status_code=404, detail="File not found"
        ) from err

    if not str(resolved).startswith(str(media_resolved) + os.sep):
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    if not resolved.is_file():
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=resolved,
        media_type=_get_media_type(resolved.suffix),
        filename=resolved.name,
    )


def _get_media_type(suffix: str) -> str:
    """Return appropriate media type for common media file extensions."""
    media_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".pdf": "application/pdf",
    }
    return media_types.get(suffix.lower(), "application/octet-stream")
