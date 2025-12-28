# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import logging

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.ormar import paginate

from voogle import auth
from voogle.models import analytics, media, users
from voogle.schemas import analytics as analytics_schemas

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/query-history",
    summary="Individual user queries",
    response_model=Page[analytics_schemas.QueryOut],
)
async def _queries(
    admin: users.User = Depends(auth.get_current_admin_user),
) -> Page[analytics_schemas.QueryOut]:  # type: ignore[valid-type]
    qs = analytics.Query.objects.order_by("-created_at")
    return await paginate(qs)


@router.get(
    "/media-count",
    summary="Analytics about number of channels and episodes in the app",
    response_model=analytics_schemas.MediaAnalytics,
)
async def _media() -> analytics_schemas.MediaAnalytics:
    dbchannels = await media.Channel.objects.order_by("title").all()
    channels = []
    for channel in dbchannels:
        eps = channel.episodes
        # Extract string values from enum fields and cast BaseField to str
        kind_str = str(channel.kind) if channel.kind else ""
        channels.append(
            analytics_schemas.ChannelAnalytics(
                title=str(channel.title),
                kind=kind_str,
                description=str(channel.description),
                image=str(channel.image),
                url=str(channel.url),
                total_episodes=await eps.count(),
                available_episodes=await eps.filter(embeddings=True).count(),
            )
        )
    return analytics_schemas.MediaAnalytics(
        total_channels=len(dbchannels), channels=channels
    )
