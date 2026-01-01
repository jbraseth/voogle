# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Manifest reader for test configuration.

Auto-derives port configuration from project directory name, enabling
parallel development across multiple repo copies without conflicts.

Priority:
1. Environment variables (VOOGLE_FRONTEND_PORT, VITE_API_PORT, etc.)
2. manifest.json file (if exists)
3. Auto-derived from directory name via infra/dev-ports.py logic
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Add infra/ to path for importing dev-ports
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "infra"))

from dev_ports import get_ports  # noqa: E402


class ManifestReader:
    """Read test configuration from manifest or auto-derive from ports."""

    MANIFEST_FILENAME = "manifest.json"

    def __init__(self, manifest_dir: str | Path) -> None:
        self.__manifest_dir = Path(manifest_dir)
        self.__manifest_content = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load manifest from env vars, file, or auto-derive from ports."""
        # Priority 1: Environment variables override everything
        env_manifest = self._from_env_vars()
        if env_manifest:
            return env_manifest

        # Priority 2: manifest.json file if it exists
        manifest_path = self.__manifest_dir / self.MANIFEST_FILENAME
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                return json.loads(f.read())

        # Priority 3: Auto-derive from project directory name
        return get_ports(_PROJECT_ROOT).to_manifest()

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
                "management_url": f"http://localhost:{management_port or '8501'}",
                "admin_username": os.environ.get("ADMIN_USERNAME", "voogle-admin"),
                "admin_password": os.environ.get(
                    "ADMIN_PASSWORD", "*audio*search*engine"
                ),
            }
        return None

    def get_if_exists_in_manifest(self, k: str) -> dict[str, Any] | str | None:
        return self.__manifest_content.get(k)
