# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Core domain models for Voogle.

This module exports the foundational data structures used throughout the
application for representing searchable content.
"""
from voogle.core.corpus import Corpus
from voogle.core.fragment import ContentType, Fragment, LocationConfidence
from voogle.core.location import (
    CodeLocation,
    ElementSelectorLocation,
    ImageRegionLocation,
    Location,
    LocationType,
    PageBboxLocation,
    SlideLocation,
    TimestampLocation,
)

__all__ = [
    "CodeLocation",
    "ContentType",
    "Corpus",
    "ElementSelectorLocation",
    "Fragment",
    "ImageRegionLocation",
    "Location",
    "LocationConfidence",
    "LocationType",
    "PageBboxLocation",
    "SlideLocation",
    "TimestampLocation",
]
