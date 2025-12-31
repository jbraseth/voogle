# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Search CLI for querying and comparing collections."""
import argparse
import logging

from voogle import settings, tasks, vector

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Voogle collections",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "query",
        type=str,
        help="Search query text",
    )

    parser.add_argument(
        "--compare",
        action="store",
        type=str,
        default=None,
        help="Compare collections (comma-separated, e.g., 'default,experiment_60word')",
    )

    parser.add_argument(
        "--num-results",
        "-n",
        action="store",
        type=int,
        default=5,
        help="Number of results per collection (default: 5)",
    )

    args = parser.parse_args()

    if args.compare:
        _compare_collections(args.query, args.compare.split(","), args.num_results)
    else:
        _search_default(args.query, args.num_results)


def _search_default(query: str, num_results: int) -> None:
    """Search the default collection."""
    results = tasks.search(query, num_results)
    print(f"\nResults for: '{query}'\n{'=' * 60}")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r.score:.3f}] Episode {r.episode} @ {r.start_secs:.0f}s")
        print(f"   {r.text[:100]}...")
        print()


def _compare_collections(query: str, collection_names: list[str], num_results: int) -> None:
    """Compare search results across multiple collections."""
    provider_name = settings.settings.embeddings_provider
    base_collection = vector.get_collection_name(provider_name)

    print(f"\nComparing collections for query: '{query}'")
    print("=" * 80)

    for name in collection_names:
        if name == "default":
            collection_name = base_collection
            display_name = f"default ({base_collection})"
        else:
            collection_name = vector.get_experiment_collection_name(name, provider_name)
            display_name = f"{name} ({collection_name})"

        print(f"\n--- Collection: {display_name} ---")
        try:
            results = tasks.search_collection(query, collection_name, num_results)
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r.score:.3f}] Episode {r.episode} @ {r.start_secs:.0f}s")
                print(f"   {r.text[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
