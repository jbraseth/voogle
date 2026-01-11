# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Asset resolution utilities for BibleProject slides.

Handles loading asset manifests and resolving arc_id references to URLs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AssetInfo:
    """Information about a slide asset.

    Attributes:
        arc_id: Unique identifier for the asset (e.g., "arc://image/abc123")
        asset_type: Type of asset (e.g., "image", "video")
        src: Source URL for the asset
        alt: Alternative text for accessibility
        caption: Caption text for the asset
        title: Title of the asset
    """

    arc_id: str
    asset_type: str
    src: str
    alt: str
    caption: str
    title: str


def load_assets_manifest(path: Path) -> dict[str, AssetInfo]:
    """Load an assets manifest file and return a dictionary mapping arc_id to AssetInfo.

    The manifest is a JSON file with an "assets" array, where each entry has:
    - arc_id: The unique identifier
    - asset_type: Type of asset
    - src: Source URL
    - alt: Alt text (optional)
    - caption: Caption (optional)
    - title: Title (optional)

    Args:
        path: Path to the manifest JSON file

    Returns:
        Dictionary mapping arc_id to AssetInfo

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If manifest format is invalid
    """
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid manifest format: expected object, got {type(data).__name__}")

    assets_list = data.get("assets", [])
    if not isinstance(assets_list, list):
        raise ValueError("Invalid manifest format: 'assets' must be a list")

    manifest: dict[str, AssetInfo] = {}
    for item in assets_list:
        if not isinstance(item, dict):
            continue

        arc_id = item.get("arc_id", "")
        if not arc_id:
            continue

        asset_info = AssetInfo(
            arc_id=arc_id,
            asset_type=item.get("asset_type", "unknown"),
            src=item.get("src", ""),
            alt=item.get("alt", ""),
            caption=item.get("caption", ""),
            title=item.get("title", ""),
        )
        manifest[arc_id] = asset_info

    return manifest


def resolve_slide_assets(slide: dict, manifest: dict[str, AssetInfo]) -> dict:
    """Resolve arc_id references in a slide to actual URLs.

    Looks for arc_id references in the slide structure and replaces them
    with the corresponding AssetInfo data from the manifest.

    The function handles:
    - Top-level "arc_id" field
    - Nested "image" objects with "arc_id"
    - Nested "assets" arrays with "arc_id" entries

    Args:
        slide: A slide dictionary that may contain arc_id references
        manifest: Dictionary mapping arc_id to AssetInfo

    Returns:
        A new slide dictionary with arc_id references resolved to URLs.
        Unresolved arc_ids are left as-is.
    """
    result = slide.copy()

    # Resolve top-level arc_id
    if "arc_id" in result:
        arc_id = result["arc_id"]
        if arc_id in manifest:
            asset = manifest[arc_id]
            result["resolved_asset"] = {
                "src": asset.src,
                "alt": asset.alt,
                "caption": asset.caption,
                "title": asset.title,
                "asset_type": asset.asset_type,
            }

    # Resolve nested image object
    if "image" in result and isinstance(result["image"], dict):
        image = result["image"].copy()
        if "arc_id" in image:
            arc_id = image["arc_id"]
            if arc_id in manifest:
                asset = manifest[arc_id]
                image["src"] = asset.src
                image["alt"] = image.get("alt") or asset.alt
                image["caption"] = image.get("caption") or asset.caption
                image["title"] = image.get("title") or asset.title
        result["image"] = image

    # Resolve assets array
    if "assets" in result and isinstance(result["assets"], list):
        resolved_assets = []
        for asset_ref in result["assets"]:
            if isinstance(asset_ref, dict) and "arc_id" in asset_ref:
                arc_id = asset_ref["arc_id"]
                if arc_id in manifest:
                    asset = manifest[arc_id]
                    resolved_asset = asset_ref.copy()
                    resolved_asset["src"] = asset.src
                    resolved_asset["alt"] = resolved_asset.get("alt") or asset.alt
                    resolved_asset["caption"] = resolved_asset.get("caption") or asset.caption
                    resolved_asset["title"] = resolved_asset.get("title") or asset.title
                    resolved_asset["asset_type"] = asset.asset_type
                    resolved_assets.append(resolved_asset)
                else:
                    resolved_assets.append(asset_ref)
            else:
                resolved_assets.append(asset_ref)
        result["assets"] = resolved_assets

    return result
