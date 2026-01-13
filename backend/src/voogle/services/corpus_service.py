# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""CRUD operations for Corpus entities.

Provides service-layer operations for creating, reading, updating, and
deleting Corpus instances.
"""
from datetime import datetime
from typing import Any

from voogle.core.corpus import Corpus
from voogle.core.fragment import ContentType


class CorpusService:
    """Service for managing Corpus CRUD operations.

    Provides an in-memory repository for Corpus entities. This implementation
    can be extended to use a persistent database backend.
    """

    def __init__(self) -> None:
        """Initialize the corpus service with an empty repository."""
        self._corpora: dict[str, Corpus] = {}

    def create(
        self,
        id: str,
        name: str,
        description: str = "",
        content_types: list[ContentType] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Corpus:
        """Create a new corpus.

        Args:
            id: Unique identifier for the corpus.
            name: Human-readable name.
            description: Optional description of contents.
            content_types: List of allowed content types.
            settings: Corpus-level configuration.

        Returns:
            The newly created Corpus.

        Raises:
            ValueError: If a corpus with the given id already exists.
        """
        if id in self._corpora:
            raise ValueError(f"Corpus with id '{id}' already exists")

        now = datetime.now()
        corpus = Corpus(
            id=id,
            name=name,
            description=description,
            content_types=content_types or [],
            settings=settings or {},
            document_count=0,
            created_at=now,
            updated_at=now,
        )
        self._corpora[id] = corpus
        return corpus

    def get(self, id: str) -> Corpus | None:
        """Retrieve a corpus by id.

        Args:
            id: The unique identifier of the corpus.

        Returns:
            The Corpus if found, None otherwise.
        """
        return self._corpora.get(id)

    def list_all(self) -> list[Corpus]:
        """List all corpora.

        Returns:
            A list of all Corpus instances.
        """
        return list(self._corpora.values())

    def update(
        self,
        id: str,
        name: str | None = None,
        description: str | None = None,
        content_types: list[ContentType] | None = None,
        settings: dict[str, Any] | None = None,
        document_count: int | None = None,
    ) -> Corpus | None:
        """Update an existing corpus.

        Args:
            id: The unique identifier of the corpus to update.
            name: New name (if provided).
            description: New description (if provided).
            content_types: New content types list (if provided).
            settings: New settings dict (if provided).
            document_count: New document count (if provided).

        Returns:
            The updated Corpus if found, None otherwise.
        """
        corpus = self._corpora.get(id)
        if corpus is None:
            return None

        # Create updated corpus with new values
        updated = Corpus(
            id=corpus.id,
            name=name if name is not None else corpus.name,
            description=description if description is not None else corpus.description,
            content_types=content_types if content_types is not None else corpus.content_types,
            settings=settings if settings is not None else corpus.settings,
            document_count=document_count if document_count is not None else corpus.document_count,
            created_at=corpus.created_at,
            updated_at=datetime.now(),
        )
        self._corpora[id] = updated
        return updated

    def delete(self, id: str) -> bool:
        """Delete a corpus by id.

        Args:
            id: The unique identifier of the corpus to delete.

        Returns:
            True if the corpus was deleted, False if not found.
        """
        if id in self._corpora:
            del self._corpora[id]
            return True
        return False
