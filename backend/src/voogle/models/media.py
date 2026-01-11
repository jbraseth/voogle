# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Media-related models. The main two media entities are Episode (a
specific media item, a podcast episode) and Channel (a collection of
related episodes).

"""
import enum
from typing import Optional

import ormar

from voogle.models import base


class ChannelKind(enum.Enum):
    podcast = "podcast"
    local = "local"
    bibleproject = "bibleproject"


class Language(enum.Enum):
    es = "es"
    en = "en"
    unknown = ""


class Channel(base.CoreModel):
    """A collection of related episodes. Table channels
    The field feed (that contains the feed url) is unique.
    """

    ormar_config = ormar.OrmarConfig(
        tablename="channels",
        constraints=[ormar.UniqueColumns("feed")],
    )

    title = ormar.String(max_length=250)
    feed = ormar.String(max_length=250)
    kind = ormar.String(max_length=20, choices=list(ChannelKind))
    language = ormar.String(max_length=3, choices=list(Language))
    description = ormar.Text()
    url = ormar.String(max_length=250)
    local_folder = ormar.String(max_length=250)
    image = ormar.String(max_length=500)


class Episode(base.CoreModel):
    """A specific media item, usually a podcast episode.
    DB table episodes. Table episodes

    An episode always belongs to a Channel. If the channel is removed,
    all its episodes will be automatically removed too.

    The field url is unique.
    """

    ormar_config = ormar.OrmarConfig(
        tablename="episodes",
        constraints=[ormar.UniqueColumns("url")],
    )

    channel: Optional[Channel] = ormar.ForeignKey(
        Channel,
        related_name="episodes",
        ondelete=ormar.ReferentialAction.CASCADE,
    )
    title = ormar.String(max_length=250)
    description = ormar.Text()
    date = ormar.DateTime(timezone=True, nullable=True)
    guid = ormar.Text()  # episode guid at origin
    url = ormar.Text()
    episode = ormar.Integer(default=-1)
    season = ormar.Integer(default=-1)
    duration = ormar.Integer(default=-1)
    # whether transcriptions are available for the episode
    transcribed = ormar.Boolean(default=False)
    # whether embeddings are available for the episode
    embeddings = ormar.Boolean(default=False)
    # Mux video playback ID (for BibleProject courses)
    mux_playback_id = ormar.String(max_length=100, nullable=True)

    @property
    def stream_url(self) -> str | None:
        """Get HLS stream URL from Mux playback ID."""
        if self.mux_playback_id:
            return f"https://stream.mux.com/{self.mux_playback_id}.m3u8"
        return None
