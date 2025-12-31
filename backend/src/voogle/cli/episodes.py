# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Perform episode-related tasks

Some of them need a running Redis and RQ worker.

"""
import argparse
import asyncio
import logging

from voogle import collection, models, tasks
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

    if args.reindex_channel:
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


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
