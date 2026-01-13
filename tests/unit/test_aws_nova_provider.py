# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for AWSNovaProvider.

These tests verify the AWS Nova Bedrock provider implementation without
requiring actual AWS credentials or network access. Most tests mock the
Bedrock API calls to ensure fast, reliable unit testing.
"""

import json
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.embedding.provider import ContentModality, EmbeddingResult
from voogle.embedding.aws_nova import (
    AWS_NOVA_ENABLED_ENV,
    DEFAULT_DIMENSIONS,
    DEFAULT_MAX_BATCH_SIZE,
    DEFAULT_MAX_REQUESTS_PER_MINUTE,
    DEFAULT_MAX_TOKENS_PER_MINUTE,
    DEFAULT_MODEL_ID,
    DEFAULT_REGION,
    SUPPORTED_DIMENSIONS,
    AWSNovaProvider,
    CostTracker,
    RateLimitState,
    is_aws_nova_enabled,
)


class TestFeatureFlag:
    """Tests for the feature flag functionality."""

    def test_feature_disabled_by_default(self) -> None:
        """Feature is disabled when env var is not set."""
        with patch.dict("os.environ", {}, clear=True):
            assert is_aws_nova_enabled() is False

    def test_feature_enabled_with_true(self) -> None:
        """Feature is enabled with 'true' value."""
        with patch.dict("os.environ", {AWS_NOVA_ENABLED_ENV: "true"}):
            assert is_aws_nova_enabled() is True

    def test_feature_enabled_with_one(self) -> None:
        """Feature is enabled with '1' value."""
        with patch.dict("os.environ", {AWS_NOVA_ENABLED_ENV: "1"}):
            assert is_aws_nova_enabled() is True

    def test_feature_enabled_with_yes(self) -> None:
        """Feature is enabled with 'yes' value."""
        with patch.dict("os.environ", {AWS_NOVA_ENABLED_ENV: "yes"}):
            assert is_aws_nova_enabled() is True

    def test_feature_disabled_with_false(self) -> None:
        """Feature is disabled with 'false' value."""
        with patch.dict("os.environ", {AWS_NOVA_ENABLED_ENV: "false"}):
            assert is_aws_nova_enabled() is False


class TestCostTracker:
    """Tests for the CostTracker class."""

    def test_initial_values(self) -> None:
        """Tracker starts with zero values."""
        tracker = CostTracker()
        assert tracker.total_tokens == 0
        assert tracker.total_images == 0
        assert tracker.total_audio_seconds == 0.0
        assert tracker.total_video_seconds == 0.0

    def test_add_tokens(self) -> None:
        """Tokens can be added to tracker."""
        tracker = CostTracker()
        tracker.add_tokens(100)
        tracker.add_tokens(50)
        assert tracker.total_tokens == 150

    def test_add_image(self) -> None:
        """Images can be counted."""
        tracker = CostTracker()
        tracker.add_image()
        tracker.add_image()
        assert tracker.total_images == 2

    def test_add_audio_seconds(self) -> None:
        """Audio seconds can be tracked."""
        tracker = CostTracker()
        tracker.add_audio_seconds(10.5)
        tracker.add_audio_seconds(5.5)
        assert tracker.total_audio_seconds == 16.0

    def test_add_video_seconds(self) -> None:
        """Video seconds can be tracked."""
        tracker = CostTracker()
        tracker.add_video_seconds(30.0)
        tracker.add_video_seconds(15.0)
        assert tracker.total_video_seconds == 45.0


class TestRateLimitState:
    """Tests for the RateLimitState class."""

    def test_initial_values(self) -> None:
        """Rate limit state starts with zero values."""
        state = RateLimitState()
        assert state.tokens_used == 0
        assert state.requests_made == 0
        assert state.window_start == 0.0

    def test_lock_initialized(self) -> None:
        """Lock is automatically initialized."""
        state = RateLimitState()
        assert state.lock is not None


class TestAWSNovaProviderInit:
    """Tests for AWSNovaProvider initialization."""

    def test_default_initialization(self) -> None:
        """Provider can be initialized with defaults."""
        provider = AWSNovaProvider()
        assert provider._dimensions == DEFAULT_DIMENSIONS
        assert provider._max_tokens_per_minute == DEFAULT_MAX_TOKENS_PER_MINUTE
        assert provider._max_requests_per_minute == DEFAULT_MAX_REQUESTS_PER_MINUTE
        assert provider._batch_size == DEFAULT_MAX_BATCH_SIZE

    def test_custom_region(self) -> None:
        """Provider can be initialized with custom region."""
        provider = AWSNovaProvider(region_name="us-west-2")
        assert provider._region_name == "us-west-2"

    def test_region_from_env(self) -> None:
        """Provider uses AWS_DEFAULT_REGION env var."""
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "eu-west-1"}):
            provider = AWSNovaProvider()
            assert provider._region_name == "eu-west-1"

    def test_custom_dimensions_256(self) -> None:
        """Provider accepts 256 dimensions."""
        provider = AWSNovaProvider(dimensions=256)
        assert provider._dimensions == 256

    def test_custom_dimensions_384(self) -> None:
        """Provider accepts 384 dimensions."""
        provider = AWSNovaProvider(dimensions=384)
        assert provider._dimensions == 384

    def test_custom_dimensions_1024(self) -> None:
        """Provider accepts 1024 dimensions."""
        provider = AWSNovaProvider(dimensions=1024)
        assert provider._dimensions == 1024

    def test_custom_dimensions_3072(self) -> None:
        """Provider accepts 3072 dimensions."""
        provider = AWSNovaProvider(dimensions=3072)
        assert provider._dimensions == 3072

    def test_invalid_dimensions_raises(self) -> None:
        """Invalid dimensions raises ValueError."""
        with pytest.raises(ValueError, match="dimensions must be one of"):
            AWSNovaProvider(dimensions=512)

    def test_region_property(self) -> None:
        """region_name property returns configured region."""
        provider = AWSNovaProvider(region_name="ap-northeast-1")
        assert provider.region_name == "ap-northeast-1"

    def test_dimensions_property(self) -> None:
        """dimensions property returns configured dimensions."""
        provider = AWSNovaProvider(dimensions=384)
        assert provider.dimensions == 384


class TestMetadata:
    """Tests for provider metadata."""

    def test_metadata_provider_id(self) -> None:
        """Metadata returns correct provider ID."""
        provider = AWSNovaProvider()
        assert provider.metadata.provider_id == "aws-nova"

    def test_metadata_model_id(self) -> None:
        """Metadata returns correct model ID."""
        provider = AWSNovaProvider()
        assert provider.metadata.model_id == DEFAULT_MODEL_ID

    def test_metadata_dimensions(self) -> None:
        """Metadata returns configured dimensions."""
        provider = AWSNovaProvider(dimensions=384)
        assert provider.metadata.dimensions == 384

    def test_metadata_batch_size(self) -> None:
        """Metadata returns configured batch size."""
        provider = AWSNovaProvider(batch_size=20)
        assert provider.metadata.max_batch_size == 20

    def test_supported_modalities(self) -> None:
        """Provider supports all four modalities."""
        provider = AWSNovaProvider()
        expected = frozenset([
            ContentModality.TEXT,
            ContentModality.IMAGE,
            ContentModality.AUDIO,
            ContentModality.VIDEO,
        ])
        assert provider.metadata.supported_modalities == expected

    def test_cost_info_present(self) -> None:
        """Metadata includes cost information."""
        provider = AWSNovaProvider()
        cost_info = provider.metadata.cost_info
        assert cost_info is not None
        assert cost_info.cost_per_token is not None
        assert cost_info.cost_per_image is not None


class TestEmbedText:
    """Tests for text embedding."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Bedrock client."""
        mock = MagicMock()
        mock_response = {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * DEFAULT_DIMENSIONS
            }).encode())
        }
        mock.invoke_model.return_value = mock_response
        return mock

    def test_embed_text_returns_result(self, mock_client: MagicMock) -> None:
        """embed_text returns valid EmbeddingResult."""
        provider = AWSNovaProvider()
        provider._client = mock_client

        result = provider.embed_text("hello world")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == DEFAULT_DIMENSIONS
        assert result.dimensions == DEFAULT_DIMENSIONS
        assert result.model_id == DEFAULT_MODEL_ID

    def test_embed_text_empty_raises(self) -> None:
        """embed_text with empty string raises ValueError."""
        provider = AWSNovaProvider()
        with pytest.raises(ValueError, match="text cannot be empty"):
            provider.embed_text("")

    def test_embed_text_tracks_tokens(self, mock_client: MagicMock) -> None:
        """embed_text tracks token usage."""
        provider = AWSNovaProvider()
        provider._client = mock_client

        provider.embed_text("hello world test")

        assert provider.cost_tracker.total_tokens > 0

    def test_embed_text_with_custom_dimensions(self, mock_client: MagicMock) -> None:
        """embed_text works with custom dimensions."""
        mock_response = {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * 384
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response

        provider = AWSNovaProvider(dimensions=384)
        provider._client = mock_client

        result = provider.embed_text("test")

        assert len(result.vector) == 384
        assert result.dimensions == 384


class TestEmbedImage:
    """Tests for image embedding."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Bedrock client."""
        mock = MagicMock()
        mock_response = {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * DEFAULT_DIMENSIONS
            }).encode())
        }
        mock.invoke_model.return_value = mock_response
        return mock

    def test_embed_image_from_bytes(self, mock_client: MagicMock) -> None:
        """embed_image works with raw bytes."""
        provider = AWSNovaProvider()
        provider._client = mock_client

        result = provider.embed_image(b"fake image data")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == DEFAULT_DIMENSIONS

    def test_embed_image_from_path(
        self, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        """embed_image works with file path."""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")

        provider = AWSNovaProvider()
        provider._client = mock_client

        result = provider.embed_image(image_path)

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == DEFAULT_DIMENSIONS

    def test_embed_image_path_not_found(self) -> None:
        """embed_image raises FileNotFoundError for missing file."""
        provider = AWSNovaProvider()
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_image(Path("/nonexistent/image.jpg"))

    def test_embed_image_tracks_count(self) -> None:
        """embed_image increments image counter."""
        mock = MagicMock()
        # Use side_effect to return fresh BytesIO for each call
        mock.invoke_model.side_effect = lambda **kwargs: {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * DEFAULT_DIMENSIONS
            }).encode())
        }

        provider = AWSNovaProvider()
        provider._client = mock

        provider.embed_image(b"image1")
        provider.embed_image(b"image2")

        assert provider.cost_tracker.total_images == 2


class TestEmbedAudio:
    """Tests for audio embedding."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Bedrock client."""
        mock = MagicMock()
        mock_response = {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * DEFAULT_DIMENSIONS
            }).encode())
        }
        mock.invoke_model.return_value = mock_response
        return mock

    def test_embed_audio_from_bytes(self, mock_client: MagicMock) -> None:
        """embed_audio works with raw bytes."""
        provider = AWSNovaProvider()
        provider._client = mock_client

        result = provider.embed_audio(b"fake audio data")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == DEFAULT_DIMENSIONS

    def test_embed_audio_from_path(
        self, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        """embed_audio works with file path."""
        audio_path = tmp_path / "test.wav"
        audio_path.write_bytes(b"fake audio data")

        provider = AWSNovaProvider()
        provider._client = mock_client

        result = provider.embed_audio(audio_path)

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == DEFAULT_DIMENSIONS

    def test_embed_audio_path_not_found(self) -> None:
        """embed_audio raises FileNotFoundError for missing file."""
        provider = AWSNovaProvider()
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_audio(Path("/nonexistent/audio.wav"))

    def test_embed_audio_tracks_seconds(self, mock_client: MagicMock) -> None:
        """embed_audio tracks audio duration."""
        provider = AWSNovaProvider()
        provider._client = mock_client

        provider.embed_audio(b"fake audio data" * 1000)

        assert provider.cost_tracker.total_audio_seconds > 0


class TestEmbedVideo:
    """Tests for video embedding."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Bedrock client."""
        mock = MagicMock()
        mock_response = {
            "body": BytesIO(json.dumps({
                "embedding": [0.1] * DEFAULT_DIMENSIONS
            }).encode())
        }
        mock.invoke_model.return_value = mock_response
        return mock

    def test_embed_video_path_not_found(self) -> None:
        """embed_video raises FileNotFoundError for missing file."""
        provider = AWSNovaProvider()
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            provider.embed_video(Path("/nonexistent/video.mp4"))

    def test_embed_video_no_frames_raises(
        self, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        """embed_video raises RuntimeError when no frames extracted."""
        video_path = tmp_path / "test.mp4"
        video_path.write_bytes(b"fake video data")

        provider = AWSNovaProvider()
        provider._client = mock_client

        # Without opencv, no frames will be extracted
        with patch.dict("sys.modules", {"cv2": None}):
            with pytest.raises(RuntimeError, match="No frames could be extracted"):
                provider.embed_video(video_path)


class TestAverageEmbeddings:
    """Tests for embedding averaging."""

    def test_average_single_embedding(self) -> None:
        """Averaging single embedding returns normalized copy."""
        provider = AWSNovaProvider()
        embeddings = [[1.0, 0.0, 0.0]]

        result = provider._average_embeddings(embeddings)

        assert len(result) == 3
        # Should be normalized to unit length
        norm = sum(v * v for v in result) ** 0.5
        assert abs(norm - 1.0) < 0.01

    def test_average_multiple_embeddings(self) -> None:
        """Averaging multiple embeddings works correctly."""
        provider = AWSNovaProvider()
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]

        result = provider._average_embeddings(embeddings)

        assert len(result) == 3
        # Average of [1,0,0] and [0,1,0] should be proportional to [0.5, 0.5, 0]
        assert result[0] > 0
        assert result[1] > 0
        assert abs(result[2]) < 0.01

    def test_average_empty_raises(self) -> None:
        """Averaging empty list raises ValueError."""
        provider = AWSNovaProvider()
        with pytest.raises(ValueError, match="Cannot average empty"):
            provider._average_embeddings([])


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limit_resets_after_window(self) -> None:
        """Rate limit counters reset after window expires."""
        provider = AWSNovaProvider()
        provider._rate_limit.window_start = 0.0  # Start in the past
        provider._rate_limit.requests_made = 100

        # Next check should reset the window
        provider._check_rate_limit(tokens=10)

        assert provider._rate_limit.requests_made == 1

    def test_rate_limit_tracks_requests(self) -> None:
        """Rate limit tracks request count."""
        provider = AWSNovaProvider()

        provider._check_rate_limit(tokens=10)
        provider._check_rate_limit(tokens=20)

        assert provider._rate_limit.requests_made == 2
        assert provider._rate_limit.tokens_used == 30


class TestMediaPathResolution:
    """Tests for media path resolution helpers."""

    def test_resolve_bytes_returns_bytes(self) -> None:
        """_resolve_media_bytes returns bytes unchanged."""
        provider = AWSNovaProvider()
        data = b"test data"

        result = provider._resolve_media_bytes(data)

        assert result == data

    def test_resolve_path_returns_file_bytes(self, tmp_path: Path) -> None:
        """_resolve_media_bytes reads file contents."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"file content")

        provider = AWSNovaProvider()
        result = provider._resolve_media_bytes(file_path)

        assert result == b"file content"

    def test_resolve_bytes_path_not_found(self) -> None:
        """_resolve_media_bytes raises for missing path."""
        provider = AWSNovaProvider()
        with pytest.raises(FileNotFoundError):
            provider._resolve_media_bytes(Path("/nonexistent"))

    def test_resolve_media_path_from_bytes(self) -> None:
        """_resolve_media_path creates temp file for bytes."""
        provider = AWSNovaProvider()
        data = b"test data"

        result = provider._resolve_media_path(data, suffix=".wav")

        assert result.exists()
        assert result.read_bytes() == data
        assert result.suffix == ".wav"

        # Clean up
        result.unlink()

    def test_resolve_media_path_from_path(self, tmp_path: Path) -> None:
        """_resolve_media_path returns existing path unchanged."""
        file_path = tmp_path / "test.jpg"
        file_path.write_bytes(b"test")

        provider = AWSNovaProvider()
        result = provider._resolve_media_path(file_path, suffix=".jpg")

        assert result == file_path

    def test_cleanup_removes_temp_file(self) -> None:
        """_cleanup_temp_file removes temp file created from bytes."""
        provider = AWSNovaProvider()
        data = b"test data"

        resolved = provider._resolve_media_path(data, suffix=".tmp")
        assert resolved.exists()

        provider._cleanup_temp_file(data, resolved)
        assert not resolved.exists()

    def test_cleanup_preserves_original_file(self, tmp_path: Path) -> None:
        """_cleanup_temp_file preserves original file paths."""
        file_path = tmp_path / "original.jpg"
        file_path.write_bytes(b"test")

        provider = AWSNovaProvider()
        provider._cleanup_temp_file(file_path, file_path)

        # Original file should still exist
        assert file_path.exists()


class TestCostEstimation:
    """Tests for cost estimation."""

    def test_get_estimated_cost_initial(self) -> None:
        """Initial cost estimate is zero."""
        provider = AWSNovaProvider()
        assert provider.get_estimated_cost() == 0.0

    def test_get_estimated_cost_after_usage(self) -> None:
        """Cost estimate increases with usage."""
        provider = AWSNovaProvider()
        provider._cost_tracker.add_tokens(1000)
        provider._cost_tracker.add_image()

        cost = provider.get_estimated_cost()
        assert cost > 0


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_config(self) -> None:
        """__repr__ contains configuration details."""
        provider = AWSNovaProvider(
            region_name="us-west-2",
            dimensions=384,
            max_tokens_per_minute=30000,
            max_requests_per_minute=50,
        )
        repr_str = repr(provider)

        assert "AWSNovaProvider" in repr_str
        assert "us-west-2" in repr_str
        assert "384" in repr_str
        assert "30000" in repr_str
        assert "50" in repr_str


class TestImportError:
    """Tests for missing dependency handling."""

    def test_boto3_import_error(self) -> None:
        """Helpful error message when boto3 not installed."""
        with patch.dict("sys.modules", {"boto3": None}):
            # Clear the cache to force reimport
            from voogle.embedding import aws_nova
            aws_nova._get_bedrock_client.cache_clear()

            provider = AWSNovaProvider()

            with pytest.raises(ImportError, match="boto3"):
                _ = provider._bedrock_client
