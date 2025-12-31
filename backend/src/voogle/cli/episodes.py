# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Perform episode-related tasks

Some of them need a running Redis and RQ worker.

"""
import argparse
import asyncio
import logging

from voogle import collection, embedding, models, tasks
from voogle.chunking import ChunkingConfig

logger = logging.getLogger(__name__)


async def _main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Update all channels from their feeds",
    )

    parser.add_argument(
        "--transcribe-days",
        action="store",
        type=int,
        default=-1,
        help="Transcribe pending episodes from this amount of days",
    )

    parser.add_argument(
        "--transcribe-channel",
        action="store",
        type=str,
        default=None,
        help="Transcribe pending episodes from this specific channel",
    )

    parser.add_argument(
        "--store",
        action="store_true",
        default=False,
        help="Store pending episodes in the vector database",
    )

    parser.add_argument(
        "--reindex-channel",
        action="store",
        type=str,
        default=None,
        help="Re-index a channel into an experiment collection",
    )

    parser.add_argument(
        "--experiment",
        action="store",
        type=str,
        default=None,
        help="Experiment name for the collection (required with --reindex-channel)",
    )

    parser.add_argument(
        "--chunk-size",
        action="store",
        type=int,
        default=40,
        help="Chunk size in words for experiment (default: 40)",
    )

    parser.add_argument(
        "--chunk-overlap",
        action="store",
        type=int,
        default=0,
        help="Chunk overlap in words for experiment (default: 0)",
    )

    parser.add_argument(
        "--min-chunk-length",
        action="store",
        type=int,
        default=10,
        help="Minimum chunk length in words for experiment (default: 10)",
    )

    parser.add_argument(
        "--rebuild-embeddings",
        action="store_true",
        default=False,
        help="Rebuild embeddings for a channel with new metadata",
    )

    parser.add_argument(
        "--provider",
        action="store",
        type=str,
        choices=["local", "openai"],
        default=None,
        help="Override embeddings provider (default: use settings)",
    )

    parser.add_argument(
        "--check-metadata",
        action="store_true",
        default=False,
        help="Check Qdrant for fragments missing embedding metadata",
    )

    args = parser.parse_args()
    if args.update:
        logger.info("updating channels form an background task")
        await collection.add_default_channels()
        await tasks.update_channels()
    if args.transcribe_days > 0:
        await tasks.transcribe_episodes(args.transcribe_days)
    if args.transcribe_channel:
        num_days = args.transcribe_days if args.transcribe_days > 0 else 3650
        await tasks.transcribe_episodes(
            num_days,
            await models.Channel.objects.get(id=args.transcribe_channel),
            random_order=False,
        )
    if args.store:
        await tasks.store_episodes_embeddings()

    if args.reindex_channel and not args.rebuild_embeddings:
        # Experiment reindexing (requires --experiment)
        if not args.experiment:
            parser.error("--experiment is required with --reindex-channel")
        channel = await models.Channel.objects.get(id=args.reindex_channel)
        config = ChunkingConfig(
            chunk_size_words=args.chunk_size,
            chunk_overlap_words=args.chunk_overlap,
            min_chunk_length_words=args.min_chunk_length,
        )
        count = await tasks.reindex_channel(channel, args.experiment, config)
        logger.info(f"re-indexed {count} episodes into experiment '{args.experiment}'")

    if args.rebuild_embeddings:
        if not args.reindex_channel:
            parser.error("--rebuild-embeddings requires --reindex-channel to specify the channel")
        channel = await models.Channel.objects.get(id=args.reindex_channel)

        # Use explicit provider if given, otherwise use default
        if args.provider:
            provider = embedding.get_embeddings_provider_by_name(args.provider)
        else:
            provider = embedding.get_embeddings_provider()

        count = await tasks.rebuild_channel_embeddings(channel, provider)
        logger.info(
            f"rebuilt {count} episodes with provider={provider.provider_name}, "
            f"model={provider.model_name}"
        )

    if args.check_metadata:
        count = await tasks.check_embedding_metadata()
        if count > 0:
            logger.warning(f"{count} fragments missing embedding metadata")
        else:
            logger.info("all fragments have embedding metadata")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
