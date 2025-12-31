# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Media-related schemas."""
from typing import Optional

from pydantic import BaseModel

from voogle import transcription
from voogle.models.media import Channel, Episode

ChannelOut = Channel.get_pydantic(exclude={"pk", "episodes"})


class ChannelIn(BaseModel):
    """Information needed to create a new channel"""

    feed_url: str


EpisodeIn = Episode.get_pydantic(exclude={"pk", "id", "created_at"})
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
    media_url: str


class VisualizationPoint(BaseModel):
    """A single point in the 2D embedding visualization."""

    x: float
    y: float
    fragment_id: str
    label: str
    preview: str
    score: float
    result_index: int


class QueryPoint(BaseModel):
    """The query point in the 2D visualization."""

    x: float
    y: float
    label: str = "Your search"


class VisualizationResponse(BaseModel):
    """Response for query visualization endpoint."""

    points: list[VisualizationPoint]
    query_point: QueryPoint
    min_results_required: int = 2
