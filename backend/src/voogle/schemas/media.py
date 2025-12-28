# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

""" Media-related schemas.

"""
from typing import Optional

from pydantic import BaseModel
from voogle import transcription
from voogle.models.base import CoreModel
from voogle.models.media import Channel, Episode

ChannelOut = Channel.get_pydantic(exclude={"pk", "episodes"})


class ChannelIn(BaseModel):
    """Information needed to create a new channel"""

    feed_url: str


EpisodeIn = Episode.get_pydantic(exclude=set(CoreModel.model_fields.keys()))
EpisodeOut = Episode.get_pydantic(exclude={"pk", "channel"})


class Transcription(BaseModel):
    count: int
    offset: int
    transcription: transcription.Transcription


class QueryResponse(BaseModel):
    """Response to a query"""

    text: str
    similarity: float
    episode: Optional["EpisodeOut"]  # type: ignore[misc]
    channel: Optional["ChannelOut"]  # type: ignore[misc]
    start: float
