# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Vector database (Qdrant) fixtures for tests.

IMPORTANT: This module provides E2E test fixtures for seeding Qdrant with
embeddings. The fixtures are designed to work with dynamically created
database records rather than hardcoded IDs.

Episode and channel IDs are fetched from the test environment's database
at runtime, ensuring tests work correctly in fresh Docker environments.
"""

from pathlib import Path

import httpx
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


def _get_episode_channel_ids(
    api_url: str,
    credentials: tuple[str, str],
) -> list[tuple[int, int]]:
    """Fetch (episode_id, channel_id) pairs from the API.

    This replaces hardcoded IDs with dynamic lookup, ensuring tests work
    with any database state.

    Returns:
        List of (episode_id, channel_id) tuples.
    """
    username, password = credentials

    with httpx.Client(base_url=api_url, follow_redirects=True) as client:
        # Authenticate
        response = client.post(
            "/users/token", data={"username": username, "password": password}
        )
        if response.status_code != 200:
            # No auth or failed - try without auth
            return []

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get episodes
        response = client.get("/media/episode", headers=headers)
        if response.status_code != 200:
            return []

        episodes_data = response.json()
        items = episodes_data.get("items", [])

        pairs = []
        for ep in items:
            ep_id = ep.get("id")
            ch_id = ep.get("channel", {}).get("id") if isinstance(ep.get("channel"), dict) else ep.get("channel")
            if ep_id and ch_id:
                pairs.append((ep_id, ch_id))

        return pairs


@pytest.fixture(scope="session", name="e2e_seed_data")
def fixture_e2e_seed_data(
    e2e_qdrant_client: qdrant_client.QdrantClient,
    golf_csv_path: Path,
    jobs_csv_path: Path,
    api_url: str,
    voogle_credentials: tuple[str, str],
) -> None:
    """Seed test data with embeddings into the real Qdrant for E2E tests.

    This fixture dynamically determines episode and channel IDs from the API
    rather than using hardcoded values. This ensures tests work correctly in
    fresh Docker environments.

    Seeds embeddings for:
    - Golf podcast content (first available episode)
    - Steve Jobs speech content (second available episode if exists)

    If no episodes exist in the database, the fixture silently succeeds
    (allowing the e2e tests to skip or fail with appropriate messages).
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

    # Get episode/channel IDs dynamically from the API
    ep_ch_pairs = _get_episode_channel_ids(api_url, voogle_credentials)

    # Prepare seeding data based on available episodes
    # Map CSV files to episodes dynamically
    csv_configs = [
        (golf_csv_path, 900000),  # Golf CSV with id offset 900000
        (jobs_csv_path, 910000),  # Jobs CSV with id offset 910000
    ]

    all_points = []
    for idx, (csv_path, id_offset) in enumerate(csv_configs):
        # Use episode from API if available, otherwise use fallback IDs
        if idx < len(ep_ch_pairs):
            episode_id, channel_id = ep_ch_pairs[idx]
        else:
            # Fallback for environments without API data
            # These are unlikely to match real DB but allow seeding to complete
            episode_id = 1 + idx
            channel_id = 1 + idx

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

    if all_points:
        e2e_qdrant_client.upsert(collection_name=collection_name, points=all_points)
        print(f"Seeded {len(all_points)} embeddings into Qdrant (golf + jobs)")
    else:
        print("No points to seed - CSV files may be empty")
