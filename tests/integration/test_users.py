# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest

from starlette.testclient import TestClient
from voogle.settings import settings

pytestmark = pytest.mark.integration


@pytest.mark.description("Tests user signup with validation and login with JWT token generation")
def test_signup_login(client: TestClient) -> None:
    data = {
        "username": "johndoe",
        "email": "johndoe@acme.com",
        "password": "iamjohndoe",
    }
    response = client.post("/users/signup/", json=data).json()
    assert response["id"]
    assert "pk" not in response
    assert response["created_at"]
    for k in ["username", "email"]:
        assert response[k] == data[k]
    assert "password" not in response
    assert "hashed_password" not in response

    bad_email_data = {
        "username": "johndoe2",
        "email": "foo.com",
        "password": "iamjohndoe",
    }
    response = client.post("/users/signup/", json=bad_email_data)
    assert response.status_code == 400

    bad_password_data = {
        "username": "johndoe3",
        "email": "foo@acme.com",
        "password": "foo",
    }
    response = client.post("/users/signup/", json=bad_password_data)
    assert response.status_code == 400

    login_data = {"username": "johndoe", "password": "iamjohndoe"}
    response = client.post("/users/token/", data=login_data).json()
    assert "access_token" in response
    assert "token_type" in response

    bad_login_data = {"username": "johndoe", "password": "iamjohndoe2"}
    response = client.post("/users/token/", data=bad_login_data)
    assert response.status_code == 401


@pytest.mark.description("Validates /users/me endpoint returns authenticated user data and rejects unauthenticated requests")
async def test_me(client: TestClient, auth_client: TestClient) -> None:
    response = auth_client.get("/users/me/").json()
    assert response["username"] == settings.admin_username
    assert "pk" not in response

    response = client.get("/users/me/").json()
    assert response["detail"] == "Not authenticated"
