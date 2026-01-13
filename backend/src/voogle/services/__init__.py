# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Services layer for Voogle business logic."""

from voogle.services.corpus_service import CorpusService
from voogle.services.expansion import (
    ContextExpander,
    ContextFragment,
    ExpandedFragment,
    ExpansionConfig,
)
from voogle.services.search import (
    SearchMode,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SearchService,
)

__all__ = [
    "ContextExpander",
    "ContextFragment",
    "CorpusService",
    "ExpandedFragment",
    "ExpansionConfig",
    "SearchMode",
    "SearchQuery",
    "SearchResponse",
    "SearchResult",
    "SearchService",
]
