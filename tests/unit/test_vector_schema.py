# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for the vector schema module."""

import pytest
from qdrant_client import models

from voogle.vector_schema import (
    CollectionConfig,
    VectorConfig,
    VectorName,
    get_collection_config,
    get_vector_name_for_modality,
    DEFAULT_IMAGE_DIM,
    DEFAULT_MULTIMODAL_DIM,
    DEFAULT_TEXT_DENSE_DIM,
)


class TestVectorName:
    """Tests for VectorName enum."""

    def test_vector_names_are_strings(self):
        """VectorName values should be valid string identifiers."""
        assert VectorName.TEXT_DENSE.value == "text_dense"
        assert VectorName.TEXT_SPARSE.value == "text_sparse"
        assert VectorName.IMAGE.value == "image"
        assert VectorName.MULTIMODAL.value == "multimodal"

    def test_all_vector_names_defined(self):
        """All expected vector names should be defined."""
        expected = {"text_dense", "text_sparse", "image", "multimodal"}
        actual = {v.value for v in VectorName}
        assert actual == expected


class TestVectorConfig:
    """Tests for VectorConfig dataclass."""

    def test_default_config(self):
        """VectorConfig should use sensible defaults."""
        config = VectorConfig(
            name=VectorName.TEXT_DENSE,
            size=384,
        )
        assert config.name == VectorName.TEXT_DENSE
        assert config.size == 384
        assert config.distance == models.Distance.COSINE
        assert config.is_sparse is False
        assert config.quantization is None

    def test_sparse_config(self):
        """VectorConfig should support sparse vectors."""
        config = VectorConfig(
            name=VectorName.TEXT_SPARSE,
            size=30522,
            is_sparse=True,
        )
        assert config.is_sparse is True

    def test_immutable(self):
        """VectorConfig should be immutable (frozen dataclass)."""
        config = VectorConfig(name=VectorName.TEXT_DENSE, size=384)
        with pytest.raises(AttributeError):
            config.size = 512  # type: ignore[misc]


class TestCollectionConfig:
    """Tests for CollectionConfig dataclass."""

    def test_default_factory(self):
        """CollectionConfig should initialize with empty defaults."""
        config = CollectionConfig()
        assert config.vectors_config == {}
        assert config.payload_schema == {}
        assert config.quantization_config is None
        assert config.on_disk_payload is False
        assert config.replication_factor == 1
        assert config.write_consistency_factor == 1


class TestGetCollectionConfig:
    """Tests for get_collection_config function."""

    def test_returns_collection_config(self):
        """get_collection_config should return a CollectionConfig."""
        config = get_collection_config()
        assert isinstance(config, CollectionConfig)

    def test_has_named_vectors(self):
        """Config should have all required named vectors."""
        config = get_collection_config()
        expected_vectors = {"text_dense", "text_sparse", "image", "multimodal"}
        assert set(config.vectors_config.keys()) == expected_vectors

    def test_text_dense_config(self):
        """text_dense vector should use default dimensions and COSINE distance."""
        config = get_collection_config()
        text_dense = config.vectors_config["text_dense"]
        assert isinstance(text_dense, models.VectorParams)
        assert text_dense.size == DEFAULT_TEXT_DENSE_DIM
        assert text_dense.distance == models.Distance.COSINE

    def test_text_sparse_config(self):
        """text_sparse vector should be configured as sparse."""
        config = get_collection_config()
        text_sparse = config.vectors_config["text_sparse"]
        assert isinstance(text_sparse, models.SparseVectorParams)

    def test_image_config(self):
        """image vector should use default dimensions."""
        config = get_collection_config()
        image = config.vectors_config["image"]
        assert isinstance(image, models.VectorParams)
        assert image.size == DEFAULT_IMAGE_DIM

    def test_multimodal_config(self):
        """multimodal vector should use default dimensions."""
        config = get_collection_config()
        multimodal = config.vectors_config["multimodal"]
        assert isinstance(multimodal, models.VectorParams)
        assert multimodal.size == DEFAULT_MULTIMODAL_DIM

    def test_custom_dimensions(self):
        """Config should accept custom dimensions."""
        config = get_collection_config(
            text_dense_dim=768,
            image_dim=1024,
            multimodal_dim=2048,
        )
        assert config.vectors_config["text_dense"].size == 768  # type: ignore[union-attr]
        assert config.vectors_config["image"].size == 1024  # type: ignore[union-attr]
        assert config.vectors_config["multimodal"].size == 2048  # type: ignore[union-attr]

    def test_quantization_enabled_by_default(self):
        """Quantization should be enabled by default."""
        config = get_collection_config()
        assert config.quantization_config is not None
        assert isinstance(config.quantization_config, models.ScalarQuantization)

    def test_quantization_can_be_disabled(self):
        """Quantization should be disableable."""
        config = get_collection_config(enable_quantization=False)
        assert config.quantization_config is None

    def test_payload_schema_has_fragment_fields(self):
        """Payload schema should include Fragment fields."""
        config = get_collection_config()
        schema = config.payload_schema
        assert "fragment_id" in schema
        assert "text" in schema
        assert "source_id" in schema
        assert "source_type" in schema
        assert "deep_link" in schema

    def test_payload_schema_has_location_fields(self):
        """Payload schema should include Location type fields."""
        config = get_collection_config()
        schema = config.payload_schema
        # Location discriminator
        assert "location_type" in schema
        # TimestampLocation
        assert "start_time" in schema
        assert "end_time" in schema
        # PageBboxLocation
        assert "page" in schema
        # CodeLocation
        assert "file_path" in schema
        assert "start_line" in schema
        # SlideLocation
        assert "slide_number" in schema

    def test_payload_schema_has_legacy_fields(self):
        """Payload schema should include legacy episode/channel fields."""
        config = get_collection_config()
        schema = config.payload_schema
        assert "episode" in schema
        assert "channel" in schema
        assert "start_secs" in schema
        assert "end_secs" in schema

    def test_payload_schema_has_embedding_metadata(self):
        """Payload schema should include embedding metadata fields."""
        config = get_collection_config()
        schema = config.payload_schema
        assert "embedding_model" in schema
        assert "embedding_provider" in schema
        assert "embedded_at" in schema

    def test_payload_schema_has_partition_fields(self):
        """Payload schema should include partitioning fields."""
        config = get_collection_config()
        schema = config.payload_schema
        assert "corpus_id" in schema
        assert "partition" in schema


class TestGetVectorNameForModality:
    """Tests for get_vector_name_for_modality function."""

    def test_text_modality(self):
        """Text modality should map to TEXT_DENSE."""
        assert get_vector_name_for_modality("text") == VectorName.TEXT_DENSE

    def test_image_modality(self):
        """Image modality should map to IMAGE."""
        assert get_vector_name_for_modality("image") == VectorName.IMAGE

    def test_audio_modality(self):
        """Audio modality should map to MULTIMODAL."""
        assert get_vector_name_for_modality("audio") == VectorName.MULTIMODAL

    def test_video_modality(self):
        """Video modality should map to MULTIMODAL."""
        assert get_vector_name_for_modality("video") == VectorName.MULTIMODAL

    def test_unsupported_modality_raises(self):
        """Unsupported modalities should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported modality"):
            get_vector_name_for_modality("unknown")


class TestDefaultDimensions:
    """Tests for default dimension constants."""

    def test_text_dense_dimension(self):
        """Text dense dimension should match common sentence-transformers."""
        assert DEFAULT_TEXT_DENSE_DIM == 384

    def test_image_dimension(self):
        """Image dimension should match CLIP ViT-B/32."""
        assert DEFAULT_IMAGE_DIM == 512

    def test_multimodal_dimension(self):
        """Multimodal dimension should match CLIP joint space."""
        assert DEFAULT_MULTIMODAL_DIM == 512
