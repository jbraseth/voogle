# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Durability module for content preservation and fallback mechanisms.

This module provides utilities for ensuring content availability over time,
including Archive.org Wayback Machine integration for recovering broken URLs.
"""

from voogle.durability.archive import ArchiveFallback

__all__ = ["ArchiveFallback"]
