# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest
from starlette.testclient import TestClient
from voogle.routers import media

pytestmark = pytest.mark.integration


@pytest.mark.description(
    "Stores 100 queries and validates paginated query history retrieval"
)
async def test_queries(auth_client: TestClient) -> None:
    for i in range(100):
        await media.store_user_query(f"User searched for {i}")
    response = auth_client.get("/analytics/query-history?page=1&size=21").json()
    assert response["total"] == 100
    assert len(response["items"]) == 21
