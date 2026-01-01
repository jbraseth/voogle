#!/usr/bin/python3.12
"""
Deterministic port assignment for parallel Voogle development.

This is the SINGLE SOURCE OF TRUTH for port assignments. It derives ports
from the project directory name, enabling multiple copies to run simultaneously
without conflicts.

Port Scheme:
  - Base: frontend=8080, api=8081, management=8580, qdrant=6333
  - Each "voogle-copyN" adds offset of N*10
  - Non-standard names use hash-based offset (0-90 range)

Examples:
  voogle       -> frontend:8080, api:8081, management:8580, qdrant:6333
  voogle-copy1 -> frontend:8090, api:8091, management:8590, qdrant:6343
  voogle-copy2 -> frontend:8100, api:8101, management:8600, qdrant:6353
  voogle-copy3 -> frontend:8110, api:8111, management:8610, qdrant:6363

Usage:
  # Shell: export environment variables
  eval $(python infra/dev-ports.py)
  docker compose up

  # Python: import and use
  from infra.dev_ports import get_ports
  ports = get_ports()

  # Show ports without exporting
  python infra/dev-ports.py --show
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Ports(NamedTuple):
    """Port assignments for a Voogle development instance."""

    frontend: int
    api: int
    management: int
    qdrant: int

    def to_env_vars(self) -> dict[str, str]:
        """Return as environment variable dict for docker-compose."""
        return {
            "VOOGLE_FRONTEND_PORT": str(self.frontend),
            "VITE_API_PORT": str(self.api),
            "VOOGLE_MANAGEMENT_PORT": str(self.management),
            "VOOGLE_QDRANT_PORT": str(self.qdrant),
        }

    def to_manifest(self) -> dict[str, str | int]:
        """Return as manifest.json content for E2E tests."""
        return {
            "management_url": f"http://localhost:{self.management}",
            "frontend_url": f"http://localhost:{self.frontend}",
            "api_url": f"http://localhost:{self.api}",
            "qdrant_port": self.qdrant,
            "admin_username": "voogle-admin",
            "admin_password": "*audio*search*engine",
        }


# Base ports (no offset)
BASE_FRONTEND = 8080
BASE_API = 8081
BASE_MANAGEMENT = 8580
BASE_QDRANT = 6333


def _get_project_root() -> Path:
    """Find project root by looking for CLAUDE.md marker."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    # Fallback to parent of infra/
    return Path(__file__).resolve().parent.parent


def _extract_copy_number(dirname: str) -> int | None:
    """Extract copy number from directory name like 'voogle-copy3'."""
    match = re.search(r"voogle-copy(\d+)", dirname, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _hash_to_offset(dirname: str) -> int:
    """Generate deterministic offset (0-9) from directory name hash."""
    h = hashlib.md5(dirname.encode()).hexdigest()
    return (int(h[:8], 16) % 10) * 10


def get_offset(project_root: Path | None = None) -> int:
    """
    Get port offset based on project directory name.

    Returns offset in range [0, 90] that's added to base ports.
    """
    if project_root is None:
        project_root = _get_project_root()

    dirname = project_root.name.lower()

    # Check for explicit copy number
    copy_num = _extract_copy_number(dirname)
    if copy_num is not None:
        return copy_num * 10

    # Base voogle directory (no copy suffix)
    if dirname == "voogle":
        return 0

    # Non-standard name: use hash-based offset
    return _hash_to_offset(dirname)


def get_ports(project_root: Path | None = None) -> Ports:
    """Get port assignments for this project instance."""
    offset = get_offset(project_root)
    return Ports(
        frontend=BASE_FRONTEND + offset,
        api=BASE_API + offset,
        management=BASE_MANAGEMENT + offset,
        qdrant=BASE_QDRANT + offset,
    )


def print_shell_exports(ports: Ports) -> None:
    """Print shell export commands for eval."""
    for name, value in ports.to_env_vars().items():
        print(f"export {name}={value}")


def print_human_readable(ports: Ports, project_root: Path) -> None:
    """Print human-readable port information."""
    offset = get_offset(project_root)
    print(f"Project: {project_root.name}")
    print(f"Offset:  {offset}")
    print()
    print("Ports:")
    print(f"  Frontend:   http://localhost:{ports.frontend}")
    print(f"  API:        http://localhost:{ports.api}")
    print(f"  Management: http://localhost:{ports.management}")
    print(f"  Qdrant:     http://localhost:{ports.qdrant}")


def main() -> None:
    """CLI entrypoint."""
    project_root = _get_project_root()
    ports = get_ports(project_root)

    if "--show" in sys.argv or "-s" in sys.argv:
        print_human_readable(ports, project_root)
    elif "--json" in sys.argv:
        import json

        print(json.dumps(ports.to_manifest(), indent=2))
    elif "--env-file" in sys.argv:
        # Output in .env file format
        for name, value in ports.to_env_vars().items():
            print(f"{name}={value}")
    else:
        # Default: shell export format for eval
        print_shell_exports(ports)


if __name__ == "__main__":
    main()
