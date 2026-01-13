# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Durability module for content preservation and fallback mechanisms.

This module provides utilities for ensuring content availability over time,
including web content snapshotting, Archive.org Wayback Machine integration
for recovering broken URLs, and location validation for fragment health monitoring.
"""

from voogle.durability.archive import ArchiveFallback
from voogle.durability.snapshot import SnapshotService
from voogle.durability.validation import (
    BrokenLocationReport,
    LocationStatus,
    LocationValidator,
    ValidationConfig,
    ValidationResult,
    run_scheduled_validation,
)

__all__ = [
    "ArchiveFallback",
    "BrokenLocationReport",
    "LocationStatus",
    "LocationValidator",
    "SnapshotService",
    "ValidationConfig",
    "ValidationResult",
    "run_scheduled_validation",
]
