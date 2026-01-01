# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Resource models for non-audio artifacts like PDFs, slide decks, etc.

Resources are linked to channels (courses) and optionally to specific episodes
(sessions). Unlike episodes, resources are not transcribed - they have their
own extraction pipeline for text content.
"""
import enum
from typing import Optional

import ormar

from voogle.models import base
from voogle.models.media import Channel, Episode


class ResourceKind(enum.Enum):
    """Type of resource artifact."""

    PDF = "pdf"
    # Future: SLIDE_DECK = "slide_deck", VIDEO = "video", etc.


class Resource(base.CoreModel):
    """A downloadable resource linked to a channel (course) or specific episode (session).

    Resources are non-audio artifacts like PDFs, slide decks, or supplemental materials.
    Unlike episodes, resources are not transcribed - they have their own extraction pipeline.

    Table: resources
    """

    ormar_config = ormar.OrmarConfig(
        tablename="resources",
        constraints=[ormar.UniqueColumns("guid")],
    )

    # Relationships - resource is always linked to a channel, optionally to an episode
    channel: Optional[Channel] = ormar.ForeignKey(
        Channel,
        related_name="resources",
        ondelete=ormar.ReferentialAction.CASCADE,
    )
    episode: Optional[Episode] = ormar.ForeignKey(
        Episode,
        related_name="resources",
        ondelete=ormar.ReferentialAction.SET_NULL,
        nullable=True,
    )

    # Identity
    guid = ormar.Text()  # e.g., "bibleproject:htrtb:s1:pdf"
    kind = ormar.String(max_length=20, choices=list(ResourceKind))

    # Metadata
    title = ormar.String(max_length=250)
    description = ormar.Text(default="")

    # URLs - original and local
    original_url = ormar.Text()  # Where we fetched it from
    local_path = ormar.Text(default="")  # Relative path in media folder (empty if not downloaded)

    # File metadata
    file_size_bytes = ormar.Integer(default=0)
    mime_type = ormar.String(max_length=100, default="application/pdf")

    # Processing status (for future D2-follow-up)
    extracted = ormar.Boolean(default=False)  # Text extracted?
    embeddings = ormar.Boolean(default=False)  # Embeddings calculated?
