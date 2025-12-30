#!/usr/bin/env python3
"""Reset embeddings for development/testing.

This script:
1. Clears the embeddings flag in the database (sets embeddings = False)
2. Deletes the Qdrant vector collection
3. Allows re-indexing with different models or configurations

Usage:
    # In Docker:
    docker exec voogle_worker_1 python scripts/reset_embeddings.py

    # Native:
    python backend/scripts/reset_embeddings.py
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voogle.models.media import Episode
from voogle.settings import settings
from voogle.vector import get_client


async def reset_embeddings() -> None:
    """Clear embeddings from database and vector store."""
    print("🔄 Resetting embeddings...")
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.data_dir}")

    # 1. Clear embeddings flag in database
    print("\n1️⃣ Clearing embeddings flags in database...")
    episodes = await Episode.objects.all()
    total = len(episodes)
    updated = 0

    for episode in episodes:
        if episode.embeddings:
            episode.embeddings = False
            await episode.update()
            updated += 1

    print(f"   ✓ Reset {updated}/{total} episodes")

    # 2. Delete Qdrant collection
    print("\n2️⃣ Deleting Qdrant vector collection...")
    try:
        client = get_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if "vectordb" in collection_names:
            client.delete_collection("vectordb")
            print("   ✓ Deleted 'vectordb' collection")
        else:
            print("   (i) No 'vectordb' collection found (already clean)")
    except Exception as e:
        print(f"   ⚠ Warning: Could not delete Qdrant collection: {e}")

    print("\n✅ Embeddings reset complete!")
    print("   You can now re-index with: voogle-episodes --store")


if __name__ == "__main__":
    asyncio.run(reset_embeddings())
