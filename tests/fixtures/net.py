# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""HTTP client fixtures for testing.

NOTE: Imports are done inside fixtures to avoid loading the full ML stack
at module import time. This allows E2E tests (which use Playwright against
running services) to skip the heavy torch/sentence-transformers import chain.
"""

import pytest
from starlette.testclient import TestClient


@pytest.fixture(name="client")
def fixture_client() -> TestClient:
    """Create a test client for direct API testing."""
    from voogle import main

    return TestClient(main.app)


@pytest.fixture(name="auth_client")
async def fixture_auth_client() -> TestClient:
    """Create an authenticated test client for direct API testing."""
    from voogle import auth, main, models
    from voogle.settings import settings

    client = TestClient(main.app)
    await models.users.User.objects.create(
        email="test@acme.com",
        username=settings.admin_username,
        hashed_password=auth.get_password_hash("examplepassword"),
        admin=True,
    )
    login_data = {
        "username": settings.admin_username,
        "password": "examplepassword",
    }
    response = client.post("/users/token/", data=login_data).json()
    token = response["access_token"]
    return TestClient(main.app, headers={"Authorization": f"Bearer {token}"})
