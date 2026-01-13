# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for Corpus dataclass and CorpusService."""
from datetime import datetime

import pytest

from voogle.core import ContentType, Corpus
from voogle.services.corpus_service import CorpusService

pytestmark = pytest.mark.unit


class TestCorpus:
    """Tests for Corpus dataclass."""

    @pytest.mark.description("Corpus with all required fields creates successfully")
    def test_create_with_required_fields(self) -> None:
        corpus = Corpus(
            id="test",
            name="Test Corpus",
            description="desc",
            content_types=[],
            settings={},
            document_count=0,
        )
        assert corpus.id == "test"
        assert corpus.name == "Test Corpus"
        assert corpus.description == "desc"
        assert corpus.content_types == []
        assert corpus.settings == {}
        assert corpus.document_count == 0
        assert isinstance(corpus.created_at, datetime)
        assert isinstance(corpus.updated_at, datetime)

    @pytest.mark.description("Corpus with content types creates successfully")
    def test_create_with_content_types(self) -> None:
        corpus = Corpus(
            id="test",
            name="Media Corpus",
            description="Audio and video content",
            content_types=[ContentType.AUDIO, ContentType.VIDEO],
            settings={"max_size": 1000},
            document_count=42,
        )
        assert ContentType.AUDIO in corpus.content_types
        assert ContentType.VIDEO in corpus.content_types
        assert corpus.settings == {"max_size": 1000}
        assert corpus.document_count == 42

    @pytest.mark.description("Corpus with empty id raises ValueError")
    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValueError, match="id cannot be empty"):
            Corpus(
                id="",
                name="Test",
                description="desc",
                content_types=[],
                settings={},
                document_count=0,
            )

    @pytest.mark.description("Corpus with empty name raises ValueError")
    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name cannot be empty"):
            Corpus(
                id="test",
                name="",
                description="desc",
                content_types=[],
                settings={},
                document_count=0,
            )

    @pytest.mark.description("Corpus with negative document_count raises ValueError")
    def test_negative_document_count_raises(self) -> None:
        with pytest.raises(ValueError, match="document_count must be >= 0"):
            Corpus(
                id="test",
                name="Test",
                description="desc",
                content_types=[],
                settings={},
                document_count=-1,
            )

    @pytest.mark.description("Corpus has string representation")
    def test_str_representation(self) -> None:
        corpus = Corpus(
            id="test",
            name="Test Corpus",
            description="desc",
            content_types=[],
            settings={},
            document_count=0,
        )
        result = str(corpus)
        assert "test" in result
        assert "Test Corpus" in result


class TestCorpusService:
    """Tests for CorpusService CRUD operations."""

    @pytest.mark.description("CorpusService create adds a new corpus")
    def test_create(self) -> None:
        service = CorpusService()
        corpus = service.create(
            id="test-1",
            name="Test Corpus",
            description="A test corpus",
        )
        assert corpus.id == "test-1"
        assert corpus.name == "Test Corpus"
        assert corpus.description == "A test corpus"
        assert corpus.content_types == []
        assert corpus.settings == {}
        assert corpus.document_count == 0

    @pytest.mark.description("CorpusService create with duplicate id raises ValueError")
    def test_create_duplicate_raises(self) -> None:
        service = CorpusService()
        service.create(id="test-1", name="First")
        with pytest.raises(ValueError, match="already exists"):
            service.create(id="test-1", name="Second")

    @pytest.mark.description("CorpusService get retrieves existing corpus")
    def test_get(self) -> None:
        service = CorpusService()
        service.create(id="test-1", name="Test")
        corpus = service.get("test-1")
        assert corpus is not None
        assert corpus.id == "test-1"

    @pytest.mark.description("CorpusService get returns None for non-existent corpus")
    def test_get_not_found(self) -> None:
        service = CorpusService()
        corpus = service.get("nonexistent")
        assert corpus is None

    @pytest.mark.description("CorpusService list_all returns all corpora")
    def test_list_all(self) -> None:
        service = CorpusService()
        service.create(id="test-1", name="First")
        service.create(id="test-2", name="Second")
        corpora = service.list_all()
        assert len(corpora) == 2
        ids = [c.id for c in corpora]
        assert "test-1" in ids
        assert "test-2" in ids

    @pytest.mark.description("CorpusService list_all returns empty list when no corpora")
    def test_list_all_empty(self) -> None:
        service = CorpusService()
        corpora = service.list_all()
        assert corpora == []

    @pytest.mark.description("CorpusService update modifies existing corpus")
    def test_update(self) -> None:
        service = CorpusService()
        service.create(id="test-1", name="Original")
        updated = service.update("test-1", name="Updated", document_count=10)
        assert updated is not None
        assert updated.name == "Updated"
        assert updated.document_count == 10

    @pytest.mark.description("CorpusService update returns None for non-existent corpus")
    def test_update_not_found(self) -> None:
        service = CorpusService()
        updated = service.update("nonexistent", name="New Name")
        assert updated is None

    @pytest.mark.description("CorpusService delete removes existing corpus")
    def test_delete(self) -> None:
        service = CorpusService()
        service.create(id="test-1", name="Test")
        assert service.delete("test-1") is True
        assert service.get("test-1") is None

    @pytest.mark.description("CorpusService delete returns False for non-existent corpus")
    def test_delete_not_found(self) -> None:
        service = CorpusService()
        assert service.delete("nonexistent") is False
