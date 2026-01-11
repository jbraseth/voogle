# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for assets module."""

import json
from pathlib import Path

import pytest

from voogle.bibleproject.assets import AssetInfo, load_assets_manifest, resolve_slide_assets

pytestmark = pytest.mark.unit


class TestAssetInfo:
    """Tests for AssetInfo dataclass."""

    @pytest.mark.description("AssetInfo stores all fields correctly")
    def test_all_fields(self) -> None:
        asset = AssetInfo(
            arc_id="arc://image/abc123",
            asset_type="image",
            src="https://example.com/image.jpg",
            alt="An example image",
            caption="Figure 1",
            title="Example Image",
        )
        assert asset.arc_id == "arc://image/abc123"
        assert asset.asset_type == "image"
        assert asset.src == "https://example.com/image.jpg"
        assert asset.alt == "An example image"
        assert asset.caption == "Figure 1"
        assert asset.title == "Example Image"

    @pytest.mark.description("AssetInfo allows empty optional fields")
    def test_empty_fields(self) -> None:
        asset = AssetInfo(
            arc_id="arc://image/xyz",
            asset_type="image",
            src="https://example.com/img.png",
            alt="",
            caption="",
            title="",
        )
        assert asset.alt == ""
        assert asset.caption == ""
        assert asset.title == ""


class TestLoadAssetsManifest:
    """Tests for load_assets_manifest function."""

    @pytest.mark.description("Loads valid manifest file")
    def test_valid_manifest(self, tmp_path: Path) -> None:
        manifest_data = {
            "assets": [
                {
                    "arc_id": "arc://image/001",
                    "asset_type": "image",
                    "src": "https://cdn.example.com/001.jpg",
                    "alt": "First image",
                    "caption": "Caption 1",
                    "title": "Image 1",
                },
                {
                    "arc_id": "arc://image/002",
                    "asset_type": "image",
                    "src": "https://cdn.example.com/002.jpg",
                    "alt": "Second image",
                    "caption": "",
                    "title": "",
                },
            ]
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 2
        assert "arc://image/001" in result
        assert "arc://image/002" in result
        assert result["arc://image/001"].src == "https://cdn.example.com/001.jpg"
        assert result["arc://image/001"].alt == "First image"

    @pytest.mark.description("Handles missing optional fields")
    def test_missing_optional_fields(self, tmp_path: Path) -> None:
        manifest_data = {
            "assets": [
                {
                    "arc_id": "arc://image/minimal",
                    "src": "https://example.com/img.jpg",
                }
            ]
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 1
        asset = result["arc://image/minimal"]
        assert asset.asset_type == "unknown"
        assert asset.alt == ""
        assert asset.caption == ""
        assert asset.title == ""

    @pytest.mark.description("Skips entries without arc_id")
    def test_missing_arc_id(self, tmp_path: Path) -> None:
        manifest_data = {
            "assets": [
                {"src": "https://example.com/no-id.jpg"},
                {"arc_id": "arc://valid", "src": "https://example.com/valid.jpg"},
            ]
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 1
        assert "arc://valid" in result

    @pytest.mark.description("Handles empty assets list")
    def test_empty_assets(self, tmp_path: Path) -> None:
        manifest_data = {"assets": []}
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 0

    @pytest.mark.description("Handles missing assets key")
    def test_missing_assets_key(self, tmp_path: Path) -> None:
        manifest_data = {"other": "data"}
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 0

    @pytest.mark.description("Raises ValueError for non-object root")
    def test_invalid_root_type(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('["array", "not", "object"]')

        with pytest.raises(ValueError, match="expected object"):
            load_assets_manifest(manifest_path)

    @pytest.mark.description("Raises ValueError for non-list assets")
    def test_invalid_assets_type(self, tmp_path: Path) -> None:
        manifest_data = {"assets": "not-a-list"}
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ValueError, match="must be a list"):
            load_assets_manifest(manifest_path)

    @pytest.mark.description("Skips non-dict entries in assets list")
    def test_non_dict_entries(self, tmp_path: Path) -> None:
        manifest_data = {
            "assets": [
                "string-entry",
                123,
                {"arc_id": "arc://valid", "src": "https://example.com/valid.jpg"},
            ]
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_assets_manifest(manifest_path)

        assert len(result) == 1


class TestResolveSlideAssets:
    """Tests for resolve_slide_assets function."""

    @pytest.fixture
    def sample_manifest(self) -> dict[str, AssetInfo]:
        return {
            "arc://image/001": AssetInfo(
                arc_id="arc://image/001",
                asset_type="image",
                src="https://cdn.example.com/001.jpg",
                alt="Image 1 alt",
                caption="Image 1 caption",
                title="Image 1 title",
            ),
            "arc://image/002": AssetInfo(
                arc_id="arc://image/002",
                asset_type="image",
                src="https://cdn.example.com/002.jpg",
                alt="Image 2 alt",
                caption="Image 2 caption",
                title="Image 2 title",
            ),
        }

    @pytest.mark.description("Resolves top-level arc_id")
    def test_top_level_arc_id(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {"arc_id": "arc://image/001", "text": "Slide text"}

        result = resolve_slide_assets(slide, sample_manifest)

        assert result["arc_id"] == "arc://image/001"
        assert result["text"] == "Slide text"
        assert "resolved_asset" in result
        assert result["resolved_asset"]["src"] == "https://cdn.example.com/001.jpg"
        assert result["resolved_asset"]["alt"] == "Image 1 alt"

    @pytest.mark.description("Resolves nested image object")
    def test_nested_image(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {
            "image": {"arc_id": "arc://image/001"},
            "text": "Slide with image",
        }

        result = resolve_slide_assets(slide, sample_manifest)

        assert result["image"]["src"] == "https://cdn.example.com/001.jpg"
        assert result["image"]["alt"] == "Image 1 alt"

    @pytest.mark.description("Preserves existing image attributes")
    def test_preserves_existing_attrs(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {
            "image": {
                "arc_id": "arc://image/001",
                "alt": "Custom alt",
                "custom_field": "preserved",
            }
        }

        result = resolve_slide_assets(slide, sample_manifest)

        assert result["image"]["src"] == "https://cdn.example.com/001.jpg"
        assert result["image"]["alt"] == "Custom alt"  # Preserved
        assert result["image"]["custom_field"] == "preserved"

    @pytest.mark.description("Resolves assets array")
    def test_assets_array(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {
            "assets": [
                {"arc_id": "arc://image/001"},
                {"arc_id": "arc://image/002"},
            ]
        }

        result = resolve_slide_assets(slide, sample_manifest)

        assert len(result["assets"]) == 2
        assert result["assets"][0]["src"] == "https://cdn.example.com/001.jpg"
        assert result["assets"][1]["src"] == "https://cdn.example.com/002.jpg"

    @pytest.mark.description("Handles unresolved arc_id in top-level")
    def test_unresolved_top_level(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {"arc_id": "arc://image/unknown"}

        result = resolve_slide_assets(slide, sample_manifest)

        assert result["arc_id"] == "arc://image/unknown"
        assert "resolved_asset" not in result

    @pytest.mark.description("Handles unresolved arc_id in image")
    def test_unresolved_image(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {"image": {"arc_id": "arc://image/unknown"}}

        result = resolve_slide_assets(slide, sample_manifest)

        assert result["image"]["arc_id"] == "arc://image/unknown"
        assert "src" not in result["image"]

    @pytest.mark.description("Handles unresolved arc_id in assets array")
    def test_unresolved_in_array(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {
            "assets": [
                {"arc_id": "arc://image/001"},
                {"arc_id": "arc://image/unknown"},
            ]
        }

        result = resolve_slide_assets(slide, sample_manifest)

        assert len(result["assets"]) == 2
        assert result["assets"][0]["src"] == "https://cdn.example.com/001.jpg"
        assert "src" not in result["assets"][1]

    @pytest.mark.description("Handles slide without arc_id references")
    def test_no_arc_refs(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {"text": "Plain slide", "other": "data"}

        result = resolve_slide_assets(slide, sample_manifest)

        assert result == {"text": "Plain slide", "other": "data"}

    @pytest.mark.description("Does not mutate original slide")
    def test_no_mutation(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {"arc_id": "arc://image/001", "text": "Original"}
        original_slide = {"arc_id": "arc://image/001", "text": "Original"}

        resolve_slide_assets(slide, sample_manifest)

        assert slide == original_slide

    @pytest.mark.description("Handles mixed valid and invalid entries in assets array")
    def test_mixed_array_entries(self, sample_manifest: dict[str, AssetInfo]) -> None:
        slide = {
            "assets": [
                {"arc_id": "arc://image/001"},
                {"src": "direct-url.jpg"},  # No arc_id
                "string-entry",  # Invalid type
            ]
        }

        result = resolve_slide_assets(slide, sample_manifest)

        assert len(result["assets"]) == 3
        assert result["assets"][0]["src"] == "https://cdn.example.com/001.jpg"
        assert result["assets"][1] == {"src": "direct-url.jpg"}
        assert result["assets"][2] == "string-entry"

    @pytest.mark.description("Handles empty manifest")
    def test_empty_manifest(self) -> None:
        slide = {"arc_id": "arc://image/001"}
        manifest: dict[str, AssetInfo] = {}

        result = resolve_slide_assets(slide, manifest)

        assert result["arc_id"] == "arc://image/001"
        assert "resolved_asset" not in result
