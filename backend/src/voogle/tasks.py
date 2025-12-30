# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main voogle data tasks"""

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

import qdrant_client
import sentence_transformers
from qdrant_client.models import FieldCondition, Filter, MatchValue

from voogle import collection, embedding, models, settings, transcription, utils, vector

logger = logging.getLogger(__name__)


async def update_channels() -> int:
    """Read feeds from all the channels in the db and update their
    episodes. Return the number of new episodes added.

    """
    logger.info("updating all channels")
    utils.log_event("event_update_start", "")
    total = 0
    for ch in await models.Channel.objects.all():
        ch_info = f"channel {ch.id}-{ch.title}"
        logger.info(f"updating {ch_info} ")
        try:
            added = await collection.update_channel(ch)
            logger.info(f"new episodes added to {ch_info}: {added}")
            total += added
        except Exception:
            logger.error(f"error while reading channel {ch_info}", exc_info=True)
    utils.log_event("event_update_end", "")
    logger.info(f"finished channels update after creating {total}")
    return total


async def transcribe_episodes(
    num_days: int, channel: Optional[models.Channel] = None, random_order: bool = True
) -> int:
    """Transcribe episodes, in a random order, from the last num_days
    days. Return the total number of episodes transcribed.

    """
    channel_info = f"channel {channel.pk}: {channel.title}" if channel else ""
    logger.info(f"transcribing episodes from last {num_days} days. {channel_info}")
    qs = models.Episode.objects.filter(
        transcribed=False,
        date__gt=datetime.now(timezone.utc) - timedelta(days=num_days),
    )
    if channel:
        qs = qs.filter(channel=channel)
    episodes = await qs.all()
    total = len(episodes)
    logger.info(f"{total} episodes are going to be transcribed in an async task")
    if random_order:
        random.shuffle(episodes)
    for episode in episodes:
        settings.queue.enqueue(
            transcription.transcribe_episode, episode, job_timeout="600m"
        )
    return total


async def store_episode_embeddings(
    episode: models.Episode,
    provider: embedding.EmbeddingsProvider,
    client: qdrant_client.QdrantClient,
    collection_name: str,
) -> None:
    """Obtain embeddings for a given episode and store them in the
    vector database.
    """
    title = str(episode.title)
    logger.info(f"storing embeddings for episode {title}: {episode.pk}")
    utils.log_event("event_store_start", title)
    try:
        embeddings, fragments = await embedding.episode_embeddings(
            episode, provider, embedding.DEFAULT_FRAGMENT_WORDS
        )
        await vector.add_episode(episode, client, embeddings, collection_name, fragments)
        utils.log_event("event_store_end", title)
    except Exception as e:
        # Fail loud: log error but let exception propagate
        logger.error(
            f"failed to store embeddings for episode {episode.pk}",
            exc_info=True,
            extra={"episode_id": episode.pk, "episode_title": title},
        )
        raise  # Don't swallow!
    return


async def store_episodes_embeddings() -> None:
    """Store pending episodes embeddings in the vector database"""
    logger.info("storing all pending episodes in vector database")

    # Get provider and collection config
    provider = embedding.get_embeddings_provider()
    provider_name = settings.settings.embeddings_provider
    collection_name = vector.get_collection_name(provider_name)

    logger.info(f"using provider={provider_name}, collection={collection_name}")

    # Setup vector database
    client = vector.get_configured_client()
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    # Process episodes
    episodes = await models.Episode.objects.filter(
        transcribed=True, embeddings=False
    ).all()
    logger.info(f"there are {len(episodes)} pending episodes...")
    random.shuffle(episodes)

    for episode in episodes:
        await store_episode_embeddings(episode, provider, client, collection_name)
    return


def search(
    text: str, num_results: int, channel: Optional[str] = None
) -> list[vector.QueryResponse]:
    """Main query function. Use semantic search to find content
    related to the given text in all the vector database.

    """
    provider = embedding.get_embeddings_provider()
    provider_name = settings.settings.embeddings_provider
    collection_name = vector.get_collection_name(provider_name)

    logger.info(f"searching with provider={provider_name}, collection={collection_name}")

    query_filter = None
    if channel:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="channel",
                    match=MatchValue(value=channel),
                )
            ]
        )

    return vector.search(
        vector.get_configured_client(),
        embedding.text2embedding(text, provider),
        collection_name,
        num_results,
        query_filter=query_filter,
    )
