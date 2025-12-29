# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Manifest reader for test configuration."""

import json
from pathlib import Path
from typing import Any


class ManifestReader:
    """Read test configuration from manifest.json."""

    MANIFEST_FILENAME = "manifest.json"

    def __init__(self, manifest_dir: str | Path):
        self.__manifest_dir = Path(manifest_dir)
        manifest_path = self.__manifest_dir / self.MANIFEST_FILENAME

        with open(manifest_path, encoding="utf-8") as f:
            self.__manifest_content = json.loads(f.read())

    def get_if_exists_in_manifest(self, k: str) -> Any:
        return self.__manifest_content.get(k)
