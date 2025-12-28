# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.


def test_version(client) -> None:
    response = client.get("/app/version/").json()
    assert len(response["version"].split(".")) == 3
    assert response["version"] != "0.0.0"
