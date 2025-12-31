# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""YouTube playlist source adapter for Voogle.

This adapter reads playlist configurations from JSON files and generates
RSS feeds that can be consumed by Voogle's collection pipeline.

The full implementation (scan, sync_media, emit_rss) is available in
the feat/17-youtube-playlist-adapter branch.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from voogle.sources import ConfigurationError, FeedGenerationError, LocalFeed

logger = logging.getLogger(__name__)


class YouTubeAdapter:
    """Adapter for generating RSS feeds from YouTube playlist configurations.

    Configuration format (data/local/youtube/playlist-name.json):
    {
        "playlist_id": "PLxxxxxxxxxxxxxxx",
        "playlist_url": "https://www.youtube.com/playlist?list=PLxxxxxxx",
        "title": "Playlist Name",
        "description": "Description",
        "language": "en"
    }
    """

    def __init__(self, config_dir: Path, output_dir: Path) -> None:
        self._config_dir = config_dir
        self._output_dir = output_dir

    @property
    def adapter_id(self) -> str:
        return "youtube"

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def generate_feeds(self) -> list[LocalFeed]:
        """Generate RSS feeds from all YouTube playlist configs.

        Returns:
            List of LocalFeed objects for each generated feed

        Raises:
            ConfigurationError: If config is invalid
            FeedGenerationError: If feed generation fails
        """
        feeds: list[LocalFeed] = []

        if not self._config_dir.exists():
            logger.info(f"Config directory does not exist: {self._config_dir}")
            return feeds

        config_files = list(self._config_dir.glob("*.json"))
        if not config_files:
            logger.info(f"No config files found in {self._config_dir}")
            return feeds

        self._output_dir.mkdir(parents=True, exist_ok=True)

        for config_file in config_files:
            try:
                feed = self._generate_single_feed(config_file)
                feeds.append(feed)
            except Exception as e:
                raise FeedGenerationError(
                    f"Failed to generate feed from {config_file.name}: {e}"
                ) from e

        return feeds

    def _generate_single_feed(self, config_file: Path) -> LocalFeed:
        """Generate RSS feed from a single config file."""
        # Read config
        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_file}: {e}") from e

        # Validate required fields
        self._validate_config(config, config_file.name)

        # Determine output path
        feed_filename = f"{config_file.stem}.xml"
        feed_path = self._output_dir / feed_filename

        # Generate RSS XML
        playlist_id = config.get("playlist_id", config_file.stem)
        rss_xml = self._build_rss_xml(config)

        # Write feed file
        with open(feed_path, "w", encoding="utf-8") as f:
            f.write(rss_xml)

        # Return LocalFeed reference
        channel_url = f"local://youtube/{playlist_id}"
        return LocalFeed(
            path=feed_path.absolute(),
            source_id=self.adapter_id,
            channel_url=channel_url,
        )

    def _validate_config(self, config: dict, filename: str) -> None:
        """Validate config has required fields."""
        required = ["title"]
        missing = [f for f in required if f not in config]
        if missing:
            raise ConfigurationError(
                f"Config {filename} missing required fields: {missing}"
            )

    def _build_rss_xml(self, config: dict) -> str:
        """Build RSS 2.0 XML from config data.

        Note: This generates a minimal RSS feed from config metadata.
        For a full feed with episodes, use the scan() + emit_rss() workflow
        from the youtube_playlist module.
        """
        import xml.etree.ElementTree as ET

        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")

        ET.SubElement(channel, "title").text = config["title"]
        ET.SubElement(channel, "description").text = config.get(
            "description", config["title"]
        )
        ET.SubElement(channel, "language").text = config.get("language", "en")

        playlist_url = config.get(
            "playlist_url",
            f"https://www.youtube.com/playlist?list={config.get('playlist_id', '')}",
        )
        ET.SubElement(channel, "link").text = playlist_url

        # Episodes would be added here by the full workflow
        # For now, this creates a valid but empty channel feed

        return ET.tostring(rss, encoding="unicode", xml_declaration=True)
