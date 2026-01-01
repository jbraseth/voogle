# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Resource-related schemas."""
from typing import Optional

from pydantic import BaseModel

from voogle.models.resource import Resource

ResourceOut = Resource.get_pydantic(exclude={"pk", "channel", "episode"})


class ResourceWithDownloadUrl(BaseModel):
    """Resource with computed download URL."""

    id: str
    kind: str
    title: str
    description: str
    original_url: str
    local_path: str
    file_size_bytes: int
    mime_type: str
    extracted: bool
    embeddings: bool
    download_url: Optional[str] = None  # /local/{channel}/{resources/filename.pdf}
    channel_id: Optional[str] = None
    episode_id: Optional[str] = None


class ResourcePage(BaseModel):
    """Paginated response for resources."""

    items: list[ResourceWithDownloadUrl]
    total: int
    page: int
    size: int
    pages: int
