# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Router for resource management (PDFs, documents, etc.)."""
import logging
import uuid
from typing import Optional

import fastapi

from voogle import auth
from voogle.models import resource as resource_model
from voogle.models import users
from voogle.schemas import resource as resource_schemas

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/media", tags=["media"])


def _build_download_url(local_path: str) -> Optional[str]:
    """Build the download URL for a resource if it has a local path."""
    if not local_path:
        return None
    return f"/local/{local_path}"


async def _transform_resource(
    item: resource_model.Resource,
) -> resource_schemas.ResourceWithDownloadUrl:
    """Transform a Resource model to ResourceWithDownloadUrl schema."""
    channel_id_str = None
    episode_id_str = None
    if item.channel:
        channel = await item.channel.load()
        channel_id_str = str(channel.id)
    if item.episode:
        episode = await item.episode.load()
        episode_id_str = str(episode.id)

    return resource_schemas.ResourceWithDownloadUrl(
        id=str(item.id),
        kind=item.kind,
        title=item.title,
        description=item.description,
        original_url=item.original_url,
        local_path=item.local_path,
        file_size_bytes=item.file_size_bytes,
        mime_type=item.mime_type,
        extracted=item.extracted,
        embeddings=item.embeddings,
        download_url=_build_download_url(item.local_path),
        channel_id=channel_id_str,
        episode_id=episode_id_str,
    )


@router.get(
    "/resource",
    summary="Get the list of resources",
    response_model=resource_schemas.ResourcePage,
)
async def resources(
    channel_id: Optional[uuid.UUID] = None,
    episode_id: Optional[uuid.UUID] = None,
    kind: Optional[str] = None,
    extracted: Optional[bool] = None,
    embeddings: Optional[bool] = None,
    title__icontains: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    admin: users.User = fastapi.Depends(auth.get_current_admin_user),
) -> resource_schemas.ResourcePage:
    """Return a list of resources with optional filters.

    Can filter by:
    - channel_id: Only resources for a specific channel
    - episode_id: Only resources linked to a specific episode
    - kind: Resource type (e.g., "pdf")
    - extracted: Whether text has been extracted
    - embeddings: Whether embeddings have been calculated
    - title__icontains: Title search (case-insensitive)
    """
    qs = resource_model.Resource.objects

    if channel_id:
        qs = qs.filter(channel__id=channel_id)
    if episode_id:
        qs = qs.filter(episode__id=episode_id)
    if kind:
        qs = qs.filter(kind=kind)
    if extracted is not None:
        qs = qs.filter(extracted=extracted)
    if embeddings is not None:
        qs = qs.filter(embeddings=embeddings)
    if title__icontains:
        qs = qs.filter(title__icontains=title__icontains)

    # Get total count
    total = await qs.count()

    # Get paginated items
    offset = (page - 1) * size
    items = await qs.offset(offset).limit(size).all()

    # Transform items to include download_url
    items_with_url = [await _transform_resource(item) for item in items]

    # Calculate pages
    pages = (total + size - 1) // size if size > 0 else 0

    return resource_schemas.ResourcePage(
        items=items_with_url,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/resource/{resource_id}",
    summary="Get a single resource by its ID",
    response_model=resource_schemas.ResourceWithDownloadUrl,
)
async def get_resource(
    resource_id: uuid.UUID,
    admin: users.User = fastapi.Depends(auth.get_current_admin_user),
) -> resource_schemas.ResourceWithDownloadUrl:
    """Get a single resource by its UUID."""
    item = await resource_model.Resource.objects.get(id=resource_id)

    channel_id_str = None
    episode_id_str = None
    if item.channel:
        channel = await item.channel.load()
        channel_id_str = str(channel.id)
    if item.episode:
        episode = await item.episode.load()
        episode_id_str = str(episode.id)

    return resource_schemas.ResourceWithDownloadUrl(
        id=str(item.id),
        kind=item.kind,
        title=item.title,
        description=item.description,
        original_url=item.original_url,
        local_path=item.local_path,
        file_size_bytes=item.file_size_bytes,
        mime_type=item.mime_type,
        extracted=item.extracted,
        embeddings=item.embeddings,
        download_url=_build_download_url(item.local_path),
        channel_id=channel_id_str,
        episode_id=episode_id_str,
    )


@router.delete("/resource/{resource_id}", summary="Delete a resource by its ID")
async def delete_resource(
    resource_id: uuid.UUID,
    admin: users.User = fastapi.Depends(auth.get_current_admin_user),
) -> dict:
    """Delete a resource by its UUID."""
    item = await resource_model.Resource.objects.get(id=resource_id)
    return {"deleted_rows": await item.delete()}
