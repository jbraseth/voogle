# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Vector database (Qdrant) fixtures for tests."""

from pathlib import Path

import pytest
import qdrant_client
from voogle import embedding, vector


@pytest.fixture(scope="session", name="e2e_qdrant_client")
def fixture_e2e_qdrant_client() -> qdrant_client.QdrantClient:
    """Connect to the real Qdrant service for E2E tests."""
    return vector.get_client(host="localhost", port=6333)


def _parse_csv_fragments(csv_path: Path, limit: int = 10) -> list[tuple[float, float, str]]:
    """Parse transcription CSV and return (start, end, text) tuples."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Test file not found: {csv_path}")

    fragments = []
    with open(csv_path) as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 3:
                start = float(parts[0])
                end = float(parts[1])
                text = parts[2]
                fragments.append((start, end, text))

    if not fragments:
        raise ValueError(f"No fragments found in {csv_path}")

    return fragments[:limit]


@pytest.fixture(scope="session", name="e2e_seed_data")
def fixture_e2e_seed_data(
    e2e_qdrant_client: qdrant_client.QdrantClient,
    golf_csv_path: Path,
    jobs_csv_path: Path,
    api_url: str,
    voogle_credentials: tuple[str, str],
) -> None:
    """Seed test data with embeddings into the real Qdrant for E2E tests.

    Seeds two channels:
    - Golf podcast (episode 489, channel 2) - for podcast channel tests
    - Steve Jobs speech (episode 3073, channel 4) - for local channel tests
    """
    collection_name = "vectordb"  # Local embeddings collection

    # Check if already seeded
    try:
        info = e2e_qdrant_client.get_collection(collection_name)
        if info.points_count > 0:
            return
    except Exception:
        pass

    # Get embeddings provider (local)
    provider = embedding.get_embeddings_provider()

    # Ensure collection exists
    vector.ensure_collection(e2e_qdrant_client, collection_name, provider.get_embedding_dimension())

    # Define channels to seed: (csv_path, episode_id, channel_id, id_offset)
    channels_to_seed = [
        (golf_csv_path, 489, 2, 900000),    # Golf podcast
        (jobs_csv_path, 3073, 4, 910000),   # Steve Jobs local speech
    ]

    all_points = []
    for csv_path, episode_id, channel_id, id_offset in channels_to_seed:
        fragments = _parse_csv_fragments(csv_path)
        texts = [text for _, _, text in fragments]
        embeddings = provider.encode_texts(texts)

        for i, ((start, end, text), emb) in enumerate(zip(fragments, embeddings)):
            all_points.append(
                qdrant_client.models.PointStruct(
                    id=id_offset + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "episode": episode_id,
                        "channel": channel_id,
                        "text": text,
                        "start_secs": int(start),
                        "end_secs": int(end),
                    },
                )
            )

    e2e_qdrant_client.upsert(collection_name=collection_name, points=all_points)
    print(f"Seeded {len(all_points)} embeddings into Qdrant (golf + jobs)")
