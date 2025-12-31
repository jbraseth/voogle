# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Schemas for local assistant endpoint."""

from pydantic import BaseModel


class SourceCitation(BaseModel):
    """A source citation from a search result fragment."""

    index: int  # [1], [2], etc.
    episode_title: str
    channel_title: str
    start_secs: float
    end_secs: float
    text: str
    media_url: str


class LocalAnswerResponse(BaseModel):
    """Response from the local assistant endpoint."""

    answer: str  # The CLI-generated answer
    sources: list[SourceCitation]
    cli_used: str  # "claude" or "codex"
    query: str  # Original query for reference
