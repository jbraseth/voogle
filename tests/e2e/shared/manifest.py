# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Manifest reader for test configuration.

Reads test configuration from environment variables, manifest.json, or defaults.
"""

import json
import os
from pathlib import Path
from typing import Any

# Default ports for development
DEFAULT_FRONTEND_PORT = 8080
DEFAULT_API_PORT = 8081
DEFAULT_MANAGEMENT_PORT = 8580


class ManifestReader:
    """Read test configuration from manifest or defaults."""

    MANIFEST_FILENAME = "manifest.json"

    def __init__(self, manifest_dir: str | Path) -> None:
        self.__manifest_dir = Path(manifest_dir)
        self.__manifest_content = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load manifest from env vars, file, or use defaults."""
        # Priority 1: Environment variables override everything
        env_manifest = self._from_env_vars()
        if env_manifest:
            return env_manifest

        # Priority 2: manifest.json file if it exists
        manifest_path = self.__manifest_dir / self.MANIFEST_FILENAME
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                return json.loads(f.read())

        # Priority 3: Default ports
        return self._default_manifest()

    def _default_manifest(self) -> dict[str, Any]:
        """Return default manifest with standard development ports."""
        return {
            "frontend_url": f"http://localhost:{DEFAULT_FRONTEND_PORT}",
            "api_url": f"http://localhost:{DEFAULT_API_PORT}",
            "management_url": f"http://localhost:{DEFAULT_MANAGEMENT_PORT}",
            "admin_username": "voogle-admin",
            "admin_password": "*audio*search*engine",
        }

    def _from_env_vars(self) -> dict[str, Any] | None:
        """Build manifest from environment variables if set."""
        frontend_port = os.environ.get("VOOGLE_FRONTEND_PORT")
        api_port = os.environ.get("VITE_API_PORT")
        management_port = os.environ.get("VOOGLE_MANAGEMENT_PORT")

        # Only use env vars if at least the main ports are set
        if frontend_port and api_port:
            return {
                "frontend_url": f"http://localhost:{frontend_port}",
                "api_url": f"http://localhost:{api_port}",
                "management_url": f"http://localhost:{management_port or DEFAULT_MANAGEMENT_PORT}",
                "admin_username": os.environ.get("ADMIN_USERNAME", "voogle-admin"),
                "admin_password": os.environ.get(
                    "ADMIN_PASSWORD", "*audio*search*engine"
                ),
            }
        return None

    def get_if_exists_in_manifest(self, k: str) -> dict[str, Any] | str | None:
        return self.__manifest_content.get(k)
