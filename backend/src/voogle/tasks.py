# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main voogle data tasks"""

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

import qdrant_client
from qdrant_client.models import FieldCondition, Filter, MatchValue

from voogle import collection, embedding, job_manager, models, settings, transcription, utils, vector
from voogle.chunking import DEFAULT_CONFIG, ChunkingConfig, load_chunking_config

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
        job_manager.enqueue_with_retry(
            transcription.transcribe_episode,
            episode,
            job_timeout="600m",
            description=f"Transcribe: {episode.title}",
        )
    return total


async def store_episode_embeddings(
    episode: models.Episode,
    provider: embedding.EmbeddingsProvider,
    client: qdrant_client.QdrantClient,
    collection_name: str,
    chunking_config: ChunkingConfig = DEFAULT_CONFIG,
) -> None:
    """Obtain embeddings for a given episode and store them in the vector database.

    Args:
        episode: Episode to process.
        provider: Embeddings provider.
        client: Qdrant client.
        collection_name: Target collection name.
        chunking_config: Chunking configuration for fragmentation.
    """
    title = str(episode.title)
    logger.info(f"storing embeddings for episode {title}: {episode.pk}")
    utils.log_event("event_store_start", title)
    try:
        embeddings, fragments = await embedding.episode_embeddings(
            episode, provider, chunking_config
        )
        await vector.add_episode(
            episode, client, embeddings, collection_name, fragments, provider
        )
        utils.log_event("event_store_end", title)
    except Exception:
        # Fail loud: log error but let exception propagate
        logger.error(
            f"failed to store embeddings for episode {episode.pk}",
            exc_info=True,
            extra={"episode_id": episode.pk, "episode_title": title},
        )
        raise  # Don't swallow!
    return


async def store_episodes_embeddings() -> None:
    """Store pending episodes embeddings in the vector database."""
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
    ).select_related("channel").all()
    logger.info(f"there are {len(episodes)} pending episodes...")
    random.shuffle(episodes)

    for episode in episodes:
        # Load per-channel chunking config
        channel_id = str(episode.channel.pk) if episode.channel else None
        chunking_config = load_chunking_config(channel_id)
        await store_episode_embeddings(
            episode, provider, client, collection_name, chunking_config
        )
    return


async def reindex_channel(
    channel: models.Channel,
    experiment_name: str,
    chunking_config: ChunkingConfig,
) -> int:
    """Re-index all episodes from a channel into an experiment collection.

    Args:
        channel: Channel to re-index.
        experiment_name: Name for the experiment collection.
        chunking_config: Chunking configuration to use.

    Returns:
        Number of episodes indexed.
    """
    provider = embedding.get_embeddings_provider()
    provider_name = settings.settings.embeddings_provider
    collection_name = vector.get_experiment_collection_name(experiment_name, provider_name)

    logger.info(
        f"re-indexing channel {channel.pk} into collection={collection_name} "
        f"with config={chunking_config}"
    )

    client = vector.get_configured_client()
    vector.create_collection(client, collection_name, provider.get_embedding_dimension())

    episodes = await models.Episode.objects.filter(
        channel=channel, transcribed=True
    ).all()
    logger.info(f"re-indexing {len(episodes)} episodes...")

    for episode in episodes:
        embeddings, fragments = await embedding.episode_embeddings(
            episode, provider, chunking_config
        )
        # Use upsert directly since we're creating a fresh collection
        client.upsert(
            collection_name=collection_name,
            points=[
                qdrant_client.models.PointStruct(
                    id=str(random.getrandbits(128)),
                    vector=emb.tolist(),
                    payload=vector._gen_metadata(fragment, episode, provider),
                )
                for emb, fragment in zip(embeddings, fragments)
            ],
        )

    logger.info(f"re-indexed {len(episodes)} episodes into {collection_name}")
    return len(episodes)


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


def search_collection(
    text: str,
    collection_name: str,
    num_results: int,
) -> list[vector.QueryResponse]:
    """Search a specific collection (used for A/B comparison)."""
    provider = embedding.get_embeddings_provider()
    return vector.search(
        vector.get_configured_client(),
        embedding.text2embedding(text, provider),
        collection_name,
        num_results,
    )


def search_for_visualization(
    text: str, num_results: int, channel: Optional[str] = None
) -> tuple[embedding.Embeddings, list[vector.SearchResultWithVector]]:
    """Search and return results with embeddings for 2D visualization.

    Args:
        text: Query text.
        num_results: Number of results to return.
        channel: Optional channel filter.

    Returns:
        Tuple of (query_embedding, search_results_with_vectors).
    """
    provider = embedding.get_embeddings_provider()
    provider_name = settings.settings.embeddings_provider
    collection_name = vector.get_collection_name(provider_name)

    query_embedding = embedding.text2embedding(text, provider)

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

    results = vector.search_with_vectors(
        vector.get_configured_client(),
        query_embedding,
        collection_name,
        num_results,
        query_filter=query_filter,
    )

    return query_embedding, results


async def rebuild_channel_embeddings(
    channel: models.Channel,
    provider: embedding.EmbeddingsProvider,
) -> int:
    """Rebuild embeddings for all episodes in a channel with metadata.

    Deletes existing points for the channel and re-indexes with full metadata
    (embedding_model, embedding_provider, embedded_at).

    Args:
        channel: Channel to rebuild.
        provider: Embeddings provider to use.

    Returns:
        Number of episodes rebuilt.
    """
    collection_name = vector.get_collection_name(provider.provider_name)

    logger.info(
        f"rebuilding channel {channel.pk} embeddings in collection={collection_name} "
        f"with provider={provider.provider_name}, model={provider.model_name}"
    )

    client = vector.get_configured_client()
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    # Delete existing points for this channel
    client.delete(
        collection_name=collection_name,
        points_selector=qdrant_client.models.FilterSelector(
            filter=qdrant_client.models.Filter(
                must=[
                    qdrant_client.models.FieldCondition(
                        key="channel",
                        match=qdrant_client.models.MatchValue(value=channel.pk),
                    )
                ]
            )
        ),
    )

    # Re-index episodes
    episodes = await models.Episode.objects.filter(
        channel=channel, transcribed=True
    ).all()

    for episode in episodes:
        chunking_config = load_chunking_config(str(channel.pk))
        embeddings, fragments = await embedding.episode_embeddings(
            episode, provider, chunking_config
        )
        # Use upsert with deterministic IDs for idempotent retries
        client.upsert(
            collection_name=collection_name,
            points=[
                qdrant_client.models.PointStruct(
                    id=vector.generate_point_id(str(episode.pk), fragment.start_idx),
                    vector=emb.tolist(),
                    payload=vector._gen_metadata(fragment, episode, provider),
                )
                for emb, fragment in zip(embeddings, fragments)
            ],
        )
        # Update embeddings flag
        episode.embeddings = True
        await episode.update()

    logger.info(f"rebuilt {len(episodes)} episodes for channel {channel.pk}")
    return len(episodes)


async def check_embedding_metadata() -> int:
    """Count fragments missing embedding metadata fields.

    Scrolls through all points in the configured collection and counts
    those missing 'embedding_model', 'embedding_provider', or 'embedded_at'.

    Returns:
        Count of fragments missing metadata.
    """
    client = vector.get_configured_client()
    provider_name = settings.settings.embeddings_provider
    collection_name = vector.get_collection_name(provider_name)

    logger.info(f"checking metadata in collection={collection_name}")

    # Check if collection exists
    if not client.collection_exists(collection_name):
        logger.warning(f"collection {collection_name} does not exist")
        return 0

    missing_count = 0
    offset = None

    while True:
        results, offset = client.scroll(
            collection_name=collection_name,
            limit=1000,
            offset=offset,
            with_payload=True,
        )

        if not results:
            break

        for point in results:
            payload = point.payload or {}
            if not all(
                k in payload
                for k in ("embedding_model", "embedding_provider", "embedded_at")
            ):
                missing_count += 1

        if offset is None:
            break

    logger.info(f"found {missing_count} fragments missing metadata")
    return missing_count
