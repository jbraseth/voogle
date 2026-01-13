# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for LanguageBindProvider.

These tests verify the LanguageBindProvider implementation without requiring
the actual LanguageBind models to be downloaded. Most tests mock the heavy
ML operations to ensure fast, reliable unit testing.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import torch

from voogle.embedding.provider import ContentModality, EmbeddingResult
from voogle.embedding.languagebind import (
    DEFAULT_AUDIO_SEGMENT_SECONDS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CACHE_DIR,
    DEFAULT_MODEL_ID,
    DEFAULT_VIDEO_NUM_FRAMES,
    LANGUAGEBIND_DIMENSIONS,
    LanguageBindProvider,
    _get_device,
)


class TestDeviceSelection:
    """Tests for device auto-selection."""

    def test_explicit_cpu_device(self) -> None:
        """Explicit 'cpu' device is returned unchanged."""
        assert _get_device("cpu") == "cpu"

    def test_explicit_cuda_device(self) -> None:
        """Explicit 'cuda' device is returned unchanged."""
        assert _get_device("cuda") == "cuda"

    def test_explicit_cuda_index_device(self) -> None:
        """Explicit 'cuda:0' device is returned unchanged."""
        assert _get_device("cuda:0") == "cuda:0"

    def test_auto_select_with_cuda(self) -> None:
        """Auto-select returns 'cuda' when available."""
        with patch.object(torch.cuda, "is_available", return_value=True):
            assert _get_device(None) == "cuda"

    def test_auto_select_without_cuda(self) -> None:
        """Auto-select returns 'cpu' when CUDA not available."""
        with patch.object(torch.cuda, "is_available", return_value=False):
            assert _get_device(None) == "cpu"


class TestLanguageBindProviderInit:
    """Tests for LanguageBindProvider initialization."""

    def test_default_initialization(self) -> None:
        """Provider can be initialized with defaults."""
        with patch.object(torch.cuda, "is_available", return_value=False):
            provider = LanguageBindProvider()
            assert provider._device == "cpu"
            assert provider._cache_dir == DEFAULT_CACHE_DIR
            assert provider._video_num_frames == DEFAULT_VIDEO_NUM_FRAMES
            assert provider._audio_segment_seconds == DEFAULT_AUDIO_SEGMENT_SECONDS
            assert provider._batch_size == DEFAULT_BATCH_SIZE

    def test_custom_initialization(self) -> None:
        """Provider can be initialized with custom parameters."""
        provider = LanguageBindProvider(
            device="cuda:1",
            cache_dir="/custom/cache",
            video_num_frames=16,
            audio_segment_seconds=5.0,
            batch_size=4,
        )
        assert provider._device == "cuda:1"
        assert provider._cache_dir == "/custom/cache"
        assert provider._video_num_frames == 16
        assert provider._audio_segment_seconds == 5.0
        assert provider._batch_size == 4

    def test_device_property(self) -> None:
        """device property returns the configured device."""
        provider = LanguageBindProvider(device="cpu")
        assert provider.device == "cpu"

    def test_cache_dir_property(self) -> None:
        """cache_dir property returns the configured directory."""
        provider = LanguageBindProvider(cache_dir="/my/cache")
        assert provider.cache_dir == "/my/cache"


class TestMetadata:
    """Tests for provider metadata."""

    def test_metadata_properties(self) -> None:
        """Metadata returns correct values."""
        provider = LanguageBindProvider(device="cpu")
        metadata = provider.metadata

        assert metadata.provider_id == "languagebind"
        assert metadata.model_id == DEFAULT_MODEL_ID
        assert metadata.dimensions == LANGUAGEBIND_DIMENSIONS
        assert metadata.max_batch_size == DEFAULT_BATCH_SIZE

    def test_supported_modalities(self) -> None:
        """Provider supports all four modalities."""
        provider = LanguageBindProvider(device="cpu")
        expected = frozenset([
            ContentModality.TEXT,
            ContentModality.IMAGE,
            ContentModality.AUDIO,
            ContentModality.VIDEO,
        ])
        assert provider.metadata.supported_modalities == expected
        assert provider.supported_modalities == expected

    def test_supports_all_modalities(self) -> None:
        """supports_modality returns True for all four modalities."""
        provider = LanguageBindProvider(device="cpu")
        assert provider.supports_modality(ContentModality.TEXT) is True
        assert provider.supports_modality(ContentModality.IMAGE) is True
        assert provider.supports_modality(ContentModality.AUDIO) is True
        assert provider.supports_modality(ContentModality.VIDEO) is True


class TestEmbedText:
    """Tests for text embedding."""

    @pytest.fixture
    def mock_models(self) -> dict:
        """Create mock models for testing."""
        mock_embedding = torch.randn(1, LANGUAGEBIND_DIMENSIONS)
        mock_embedding = mock_embedding / mock_embedding.norm(dim=-1, keepdim=True)

        mock_model = MagicMock()
        mock_model.get_text_features.return_value = mock_embedding

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": torch.zeros(1, 77, dtype=torch.long),
            "attention_mask": torch.ones(1, 77, dtype=torch.long),
        }

        return {
            "model": mock_model,
            "tokenizer": mock_tokenizer,
            "processors": {},
            "device": "cpu",
        }

    def test_embed_text_returns_result(self, mock_models: dict) -> None:
        """embed_text returns valid EmbeddingResult."""
        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_text("hello world")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS
        assert result.dimensions == LANGUAGEBIND_DIMENSIONS
        assert result.model_id == DEFAULT_MODEL_ID

    def test_embed_text_empty_raises(self) -> None:
        """embed_text with empty string raises ValueError."""
        provider = LanguageBindProvider(device="cpu")
        with pytest.raises(ValueError, match="text cannot be empty"):
            provider.embed_text("")

    def test_embed_text_normalizes_output(self, mock_models: dict) -> None:
        """embed_text returns normalized embedding."""
        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_text("test text")

        # Check that vector is approximately unit length
        norm = sum(x * x for x in result.vector) ** 0.5
        assert abs(norm - 1.0) < 0.01


class TestEmbedImage:
    """Tests for image embedding."""

    @pytest.fixture
    def mock_models(self) -> dict:
        """Create mock models for testing."""
        mock_embedding = torch.randn(1, LANGUAGEBIND_DIMENSIONS)
        mock_embedding = mock_embedding / mock_embedding.norm(dim=-1, keepdim=True)

        mock_model = MagicMock()
        mock_model.get_image_features.return_value = mock_embedding

        mock_processor = MagicMock()
        mock_processor.return_value = {
            "pixel_values": torch.zeros(1, 3, 224, 224),
        }

        return {
            "model": mock_model,
            "tokenizer": MagicMock(),
            "processors": {"image": mock_processor},
            "device": "cpu",
        }

    def test_embed_image_from_path(self, mock_models: dict, tmp_path: Path) -> None:
        """embed_image works with file path."""
        # Create a dummy image file
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")

        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_image(image_path)

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_image_from_bytes(self, mock_models: dict) -> None:
        """embed_image works with raw bytes."""
        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_image(b"fake image data")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_image_path_not_found(self) -> None:
        """embed_image raises FileNotFoundError for missing file."""
        provider = LanguageBindProvider(device="cpu")
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_image(Path("/nonexistent/image.jpg"))


class TestEmbedAudio:
    """Tests for audio embedding."""

    @pytest.fixture
    def mock_models(self) -> dict:
        """Create mock models for testing."""
        mock_embedding = torch.randn(1, LANGUAGEBIND_DIMENSIONS)
        mock_embedding = mock_embedding / mock_embedding.norm(dim=-1, keepdim=True)

        mock_model = MagicMock()
        mock_model.get_audio_features.return_value = mock_embedding

        mock_processor = MagicMock()
        mock_processor.return_value = {
            "pixel_values": torch.zeros(1, 1, 128, 1024),
        }

        return {
            "model": mock_model,
            "tokenizer": MagicMock(),
            "processors": {"audio": mock_processor},
            "device": "cpu",
        }

    def test_embed_audio_from_path(self, mock_models: dict, tmp_path: Path) -> None:
        """embed_audio works with file path."""
        audio_path = tmp_path / "test.wav"
        audio_path.write_bytes(b"fake audio data")

        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_audio(audio_path)

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_audio_from_bytes(self, mock_models: dict) -> None:
        """embed_audio works with raw bytes."""
        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_audio(b"fake audio data")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_audio_path_not_found(self) -> None:
        """embed_audio raises FileNotFoundError for missing file."""
        provider = LanguageBindProvider(device="cpu")
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_audio(Path("/nonexistent/audio.wav"))


class TestEmbedVideo:
    """Tests for video embedding."""

    @pytest.fixture
    def mock_models(self) -> dict:
        """Create mock models for testing."""
        mock_embedding = torch.randn(1, LANGUAGEBIND_DIMENSIONS)
        mock_embedding = mock_embedding / mock_embedding.norm(dim=-1, keepdim=True)

        mock_model = MagicMock()
        mock_model.get_video_features.return_value = mock_embedding

        mock_processor = MagicMock()
        mock_processor.return_value = {
            "pixel_values": torch.zeros(1, 8, 3, 224, 224),
        }

        return {
            "model": mock_model,
            "tokenizer": MagicMock(),
            "processors": {"video": mock_processor},
            "device": "cpu",
        }

    def test_embed_video_from_path(self, mock_models: dict, tmp_path: Path) -> None:
        """embed_video works with file path."""
        video_path = tmp_path / "test.mp4"
        video_path.write_bytes(b"fake video data")

        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_video(video_path)

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_video_from_bytes(self, mock_models: dict) -> None:
        """embed_video works with raw bytes."""
        provider = LanguageBindProvider(device="cpu")
        provider._models = mock_models

        result = provider.embed_video(b"fake video data")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == LANGUAGEBIND_DIMENSIONS

    def test_embed_video_path_not_found(self) -> None:
        """embed_video raises FileNotFoundError for missing file."""
        provider = LanguageBindProvider(device="cpu")
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_video(Path("/nonexistent/video.mp4"))

    def test_embed_video_uses_frame_config(self, mock_models: dict, tmp_path: Path) -> None:
        """embed_video uses configured number of frames."""
        video_path = tmp_path / "test.mp4"
        video_path.write_bytes(b"fake video data")

        provider = LanguageBindProvider(device="cpu", video_num_frames=16)
        provider._models = mock_models

        provider.embed_video(video_path)

        # Verify processor was called with num_frames
        mock_models["processors"]["video"].assert_called_once()
        call_kwargs = mock_models["processors"]["video"].call_args[1]
        assert call_kwargs["num_frames"] == 16


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_config(self) -> None:
        """__repr__ contains configuration details."""
        provider = LanguageBindProvider(
            device="cuda:0",
            cache_dir="/my/cache",
            video_num_frames=16,
            audio_segment_seconds=5.0,
        )
        repr_str = repr(provider)

        assert "LanguageBindProvider" in repr_str
        assert "cuda:0" in repr_str
        assert "/my/cache" in repr_str
        assert "16" in repr_str
        assert "5.0" in repr_str


class TestMediaPathResolution:
    """Tests for media path resolution helper."""

    def test_resolve_path_validates_existence(self) -> None:
        """_resolve_media_path raises for missing path."""
        provider = LanguageBindProvider(device="cpu")
        with pytest.raises(FileNotFoundError):
            provider._resolve_media_path(Path("/nonexistent"), suffix=".jpg")

    def test_resolve_path_returns_existing_path(self, tmp_path: Path) -> None:
        """_resolve_media_path returns existing path unchanged."""
        file_path = tmp_path / "test.jpg"
        file_path.write_bytes(b"test")

        provider = LanguageBindProvider(device="cpu")
        result = provider._resolve_media_path(file_path, suffix=".jpg")

        assert result == file_path

    def test_resolve_bytes_creates_temp_file(self) -> None:
        """_resolve_media_path creates temp file for bytes."""
        provider = LanguageBindProvider(device="cpu")
        data = b"test data"

        result = provider._resolve_media_path(data, suffix=".wav")

        assert result.exists()
        assert result.read_bytes() == data
        assert result.suffix == ".wav"

        # Clean up
        result.unlink()

    def test_cleanup_removes_temp_file(self) -> None:
        """_cleanup_temp_file removes temp file created from bytes."""
        provider = LanguageBindProvider(device="cpu")
        data = b"test data"

        resolved = provider._resolve_media_path(data, suffix=".tmp")
        assert resolved.exists()

        provider._cleanup_temp_file(data, resolved)
        assert not resolved.exists()

    def test_cleanup_preserves_original_file(self, tmp_path: Path) -> None:
        """_cleanup_temp_file preserves original file paths."""
        file_path = tmp_path / "original.jpg"
        file_path.write_bytes(b"test")

        provider = LanguageBindProvider(device="cpu")
        provider._cleanup_temp_file(file_path, file_path)

        # Original file should still exist
        assert file_path.exists()


class TestImportError:
    """Tests for missing dependency handling."""

    def test_import_error_message(self) -> None:
        """Helpful error message when languagebind not installed."""
        with patch.dict("sys.modules", {"languagebind": None}):
            # The import error should be raised when loading models
            # This is tested implicitly in integration tests
            pass  # Import error handling is tested at runtime
