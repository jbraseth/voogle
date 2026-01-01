# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest
from starlette.testclient import TestClient
from voogle import models

pytestmark = pytest.mark.integration


@pytest.mark.description("Lists resources via API and validates response structure")
def test_list_resources(resource: models.Resource, auth_client: TestClient) -> None:
    """Test listing resources via the API."""
    _unused = resource  # Ensure fixture creates the resource
    response = auth_client.get("/media/resource").json()
    assert response["total"] == 1
    assert len(response["items"]) == 1
    item = response["items"][0]
    assert item["id"]
    assert item["title"] == "Test PDF Resource"
    assert item["kind"] == "pdf"
    assert item["mime_type"] == "application/pdf"
    assert item["download_url"] == "/local/test-channel/resources/test-pdf.pdf"
    assert "pk" not in item


@pytest.mark.description("Filters resources by channel ID")
async def test_filter_resources_by_channel(
    resource: models.Resource, auth_client: TestClient
) -> None:
    """Test filtering resources by channel_id."""
    # Get channel ID
    channel = await resource.channel.load()
    channel_id = str(channel.id)

    # Filter by channel
    response = auth_client.get(f"/media/resource?channel_id={channel_id}").json()
    assert response["total"] == 1
    assert response["items"][0]["channel_id"] == channel_id

    # Filter by non-existent channel
    response = auth_client.get(
        "/media/resource?channel_id=00000000-0000-0000-0000-000000000000"
    ).json()
    assert response["total"] == 0


@pytest.mark.description("Filters resources by kind (PDF)")
def test_filter_resources_by_kind(
    resource: models.Resource, auth_client: TestClient
) -> None:
    """Test filtering resources by kind."""
    _unused = resource
    response = auth_client.get("/media/resource?kind=pdf").json()
    assert response["total"] == 1

    # Non-existent kind returns empty
    response = auth_client.get("/media/resource?kind=video").json()
    assert response["total"] == 0


@pytest.mark.description("Gets a single resource by ID")
def test_get_resource_by_id(
    resource: models.Resource, auth_client: TestClient
) -> None:
    """Test getting a single resource by its ID."""
    resource_id = str(resource.id)
    response = auth_client.get(f"/media/resource/{resource_id}").json()
    assert response["id"] == resource_id
    assert response["title"] == "Test PDF Resource"
    assert response["download_url"] == "/local/test-channel/resources/test-pdf.pdf"


@pytest.mark.description("Deletes a resource by ID")
def test_delete_resource(resource: models.Resource, auth_client: TestClient) -> None:
    """Test deleting a resource by its ID."""
    resource_id = str(resource.id)
    response = auth_client.delete(f"/media/resource/{resource_id}").json()
    assert response["deleted_rows"] == 1

    # Verify it's gone
    response = auth_client.get("/media/resource").json()
    assert response["total"] == 0


@pytest.mark.description("Resource with episode has episode_id in response")
async def test_resource_with_episode(
    resource_with_episode: models.Resource, auth_client: TestClient
) -> None:
    """Test that resources linked to episodes include episode_id."""
    _unused = resource_with_episode
    response = auth_client.get("/media/resource").json()
    assert response["total"] == 1
    item = response["items"][0]
    assert item["episode_id"] is not None
    assert item["channel_id"] is not None


@pytest.mark.description("Resource download URL is null when local_path is empty")
async def test_resource_no_local_path(
    channel: models.media.Channel, auth_client: TestClient
) -> None:
    """Test that download_url is null when local_path is empty."""
    # Create resource without local_path
    resource = await models.Resource.objects.create(
        channel=channel,
        guid="test-resource-no-local",
        kind=models.ResourceKind.PDF.value,
        title="Remote PDF",
        description="A PDF that hasn't been downloaded",
        original_url="https://example.com/remote.pdf",
        local_path="",  # Empty - not downloaded
        file_size_bytes=0,
        mime_type="application/pdf",
    )

    response = auth_client.get(f"/media/resource/{resource.id}").json()
    assert response["download_url"] is None
    assert response["original_url"] == "https://example.com/remote.pdf"
