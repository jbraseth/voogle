# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""AWS Nova Bedrock embedding provider implementation.

Implements the EmbeddingProvider interface using AWS Bedrock's Amazon Nova
multimodal embedding model for enterprise-grade text, image, audio, and video
embeddings.

Usage:
    from voogle.embedding.aws_nova import AWSNovaProvider

    # Default configuration (uses 1024 dimensions)
    provider = AWSNovaProvider()

    # With custom settings
    provider = AWSNovaProvider(
        region_name="us-west-2",
        dimensions=384,
        max_tokens_per_minute=60000,
    )

    # Embed different modalities
    text_result = provider.embed_text("A dog playing in the park")
    image_result = provider.embed_image("/path/to/image.jpg")
    audio_result = provider.embed_audio("/path/to/audio.wav")
    video_result = provider.embed_video("/path/to/video.mp4")

AWS Nova Embedding Model:
    - Model ID: amazon.nova-embed-v1
    - Supported dimensions: 256, 384, 1024, 3072 (default: 1024)
    - Multimodal: text, images
    - Audio/video via transcription or frame extraction
"""

from __future__ import annotations

import base64
import functools
import logging
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

from voogle.embedding.provider import (
    ContentModality,
    CostInfo,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)

logger = logging.getLogger(__name__)

# AWS Nova model configuration
DEFAULT_MODEL_ID = "amazon.nova-embed-v1"
SUPPORTED_DIMENSIONS = frozenset([256, 384, 1024, 3072])
DEFAULT_DIMENSIONS = 1024
DEFAULT_REGION = "us-east-1"
DEFAULT_MAX_BATCH_SIZE = 10

# Rate limiting defaults
DEFAULT_MAX_TOKENS_PER_MINUTE = 60000
DEFAULT_MAX_REQUESTS_PER_MINUTE = 100

# Cost estimates (per 1000 tokens/images) - approximate as of 2025
DEFAULT_COST_PER_1K_TOKENS = 0.00002
DEFAULT_COST_PER_IMAGE = 0.0001

# Video/Audio processing defaults
DEFAULT_VIDEO_FRAME_INTERVAL_SECONDS = 1.0
DEFAULT_AUDIO_CHUNK_SECONDS = 30.0
DEFAULT_MAX_FRAMES_PER_VIDEO = 60

# Feature flag
AWS_NOVA_ENABLED_ENV = "AWS_NOVA_EMBEDDING_ENABLED"


@dataclass
class RateLimitState:
    """Thread-safe rate limiting state."""

    tokens_used: int = 0
    requests_made: int = 0
    window_start: float = 0.0
    lock: threading.Lock = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize the lock."""
        if self.lock is None:
            object.__setattr__(self, "lock", threading.Lock())


@dataclass
class CostTracker:
    """Tracks cumulative costs for the provider."""

    total_tokens: int = 0
    total_images: int = 0
    total_audio_seconds: float = 0.0
    total_video_seconds: float = 0.0
    lock: threading.Lock = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize the lock."""
        if self.lock is None:
            object.__setattr__(self, "lock", threading.Lock())

    def add_tokens(self, count: int) -> None:
        """Add token count to tracker."""
        with self.lock:
            self.total_tokens += count

    def add_image(self) -> None:
        """Increment image count."""
        with self.lock:
            self.total_images += 1

    def add_audio_seconds(self, seconds: float) -> None:
        """Add audio seconds to tracker."""
        with self.lock:
            self.total_audio_seconds += seconds

    def add_video_seconds(self, seconds: float) -> None:
        """Add video seconds to tracker."""
        with self.lock:
            self.total_video_seconds += seconds

    def get_estimated_cost(self, cost_info: CostInfo) -> float:
        """Calculate estimated total cost."""
        with self.lock:
            cost = 0.0
            if cost_info.cost_per_token:
                cost += self.total_tokens * cost_info.cost_per_token
            if cost_info.cost_per_image:
                cost += self.total_images * cost_info.cost_per_image
            if cost_info.cost_per_second_audio:
                cost += self.total_audio_seconds * cost_info.cost_per_second_audio
            if cost_info.cost_per_second_video:
                cost += self.total_video_seconds * cost_info.cost_per_second_video
            return cost


def is_aws_nova_enabled() -> bool:
    """Check if AWS Nova provider is enabled via feature flag.

    Returns:
        True if the AWS_NOVA_EMBEDDING_ENABLED env var is set to 'true' or '1'.
    """
    value = os.environ.get(AWS_NOVA_ENABLED_ENV, "").lower()
    return value in ("true", "1", "yes", "on")


@functools.cache
def _get_bedrock_client(region_name: str) -> Any:
    """Get or create a Bedrock runtime client.

    Args:
        region_name: AWS region for the Bedrock service.

    Returns:
        boto3 Bedrock runtime client.

    Raises:
        ImportError: If boto3 is not installed.
    """
    try:
        import boto3
    except ImportError as e:
        raise ImportError(
            "AWS Nova provider requires the 'boto3' package. "
            "Install it with: pip install boto3"
        ) from e

    logger.info(f"Creating Bedrock client for region: {region_name}")
    return boto3.client("bedrock-runtime", region_name=region_name)


class AWSNovaProvider(EmbeddingProvider):
    """Embedding provider using AWS Bedrock's Amazon Nova model.

    Amazon Nova provides enterprise-grade multimodal embeddings supporting
    text and images natively, with audio and video support via preprocessing
    (transcription and frame extraction).

    Features:
        - Configurable dimensions: 256, 384, 1024, or 3072
        - Thread-safe rate limiting
        - Cost tracking for billing estimates
        - Video segmentation (frame extraction at intervals)
        - Audio support via transcription
        - Feature flag for controlled rollout

    Attributes:
        region_name: AWS region where Bedrock is accessed.
        dimensions: Embedding vector dimensionality.
        cost_tracker: Cumulative cost tracking.
    """

    def __init__(
        self,
        region_name: str | None = None,
        dimensions: int = DEFAULT_DIMENSIONS,
        max_tokens_per_minute: int = DEFAULT_MAX_TOKENS_PER_MINUTE,
        max_requests_per_minute: int = DEFAULT_MAX_REQUESTS_PER_MINUTE,
        video_frame_interval: float = DEFAULT_VIDEO_FRAME_INTERVAL_SECONDS,
        audio_chunk_seconds: float = DEFAULT_AUDIO_CHUNK_SECONDS,
        max_frames_per_video: int = DEFAULT_MAX_FRAMES_PER_VIDEO,
        batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    ) -> None:
        """Initialize the AWS Nova provider.

        Args:
            region_name: AWS region for Bedrock. Defaults to us-east-1 or
                        AWS_DEFAULT_REGION env var.
            dimensions: Embedding dimensionality. Must be one of:
                       256, 384, 1024, or 3072. Default is 1024.
            max_tokens_per_minute: Rate limit for tokens per minute.
            max_requests_per_minute: Rate limit for requests per minute.
            video_frame_interval: Seconds between video frame extractions.
            audio_chunk_seconds: Length of audio chunks for processing.
            max_frames_per_video: Maximum frames to extract from a video.
            batch_size: Maximum batch size for batch operations.

        Raises:
            ValueError: If dimensions is not a supported value.
        """
        if dimensions not in SUPPORTED_DIMENSIONS:
            raise ValueError(
                f"dimensions must be one of {sorted(SUPPORTED_DIMENSIONS)}, "
                f"got {dimensions}"
            )

        self._region_name = region_name or os.environ.get(
            "AWS_DEFAULT_REGION", DEFAULT_REGION
        )
        self._dimensions = dimensions
        self._max_tokens_per_minute = max_tokens_per_minute
        self._max_requests_per_minute = max_requests_per_minute
        self._video_frame_interval = video_frame_interval
        self._audio_chunk_seconds = audio_chunk_seconds
        self._max_frames_per_video = max_frames_per_video
        self._batch_size = batch_size

        # Initialize rate limiting and cost tracking
        self._rate_limit = RateLimitState()
        self._cost_tracker = CostTracker()
        self._client: Any | None = None

    @property
    def _bedrock_client(self) -> Any:
        """Lazy-load Bedrock client on first use."""
        if self._client is None:
            self._client = _get_bedrock_client(self._region_name)
        return self._client

    @property
    def metadata(self) -> ProviderMetadata:
        """Return metadata describing this provider's capabilities."""
        return ProviderMetadata(
            provider_id="aws-nova",
            model_id=DEFAULT_MODEL_ID,
            supported_modalities=frozenset([
                ContentModality.TEXT,
                ContentModality.IMAGE,
                ContentModality.AUDIO,
                ContentModality.VIDEO,
            ]),
            dimensions=self._dimensions,
            max_batch_size=self._batch_size,
            cost_info=CostInfo(
                cost_per_token=DEFAULT_COST_PER_1K_TOKENS / 1000,
                cost_per_image=DEFAULT_COST_PER_IMAGE,
                cost_per_second_audio=0.00005,  # Approximate transcription cost
                cost_per_second_video=0.0001,   # Approximate frame extraction cost
            ),
            description="AWS Bedrock Nova multimodal embeddings with configurable dimensions",
        )

    @property
    def region_name(self) -> str:
        """Return the AWS region being used."""
        return self._region_name

    @property
    def dimensions(self) -> int:
        """Return the configured embedding dimensions."""
        return self._dimensions

    @property
    def cost_tracker(self) -> CostTracker:
        """Return the cost tracker for monitoring usage."""
        return self._cost_tracker

    def _check_rate_limit(self, tokens: int = 0) -> None:
        """Check and enforce rate limits.

        Args:
            tokens: Number of tokens this request will consume.

        Raises:
            RuntimeError: If rate limit would be exceeded and cannot wait.
        """
        with self._rate_limit.lock:
            current_time = time.time()

            # Reset window if needed (1 minute window)
            if current_time - self._rate_limit.window_start >= 60.0:
                self._rate_limit.window_start = current_time
                self._rate_limit.tokens_used = 0
                self._rate_limit.requests_made = 0

            # Check limits
            if self._rate_limit.requests_made >= self._max_requests_per_minute:
                wait_time = 60.0 - (current_time - self._rate_limit.window_start)
                if wait_time > 0:
                    logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                    self._rate_limit.window_start = time.time()
                    self._rate_limit.tokens_used = 0
                    self._rate_limit.requests_made = 0

            if self._rate_limit.tokens_used + tokens > self._max_tokens_per_minute:
                wait_time = 60.0 - (current_time - self._rate_limit.window_start)
                if wait_time > 0:
                    logger.warning(f"Token limit reached, waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                    self._rate_limit.window_start = time.time()
                    self._rate_limit.tokens_used = 0
                    self._rate_limit.requests_made = 0

            # Update counters
            self._rate_limit.tokens_used += tokens
            self._rate_limit.requests_made += 1

    def _invoke_model(
        self,
        input_text: str | None = None,
        input_image: str | None = None,
    ) -> list[float]:
        """Invoke the Nova embedding model.

        Args:
            input_text: Text content to embed.
            input_image: Base64-encoded image data.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            RuntimeError: If the API call fails.
        """
        import json

        # Estimate tokens (rough approximation)
        estimated_tokens = len(input_text.split()) * 2 if input_text else 100
        self._check_rate_limit(estimated_tokens)

        # Build request body
        body: dict[str, Any] = {
            "inputText": input_text or "",
            "dimensions": self._dimensions,
            "normalize": True,
        }

        if input_image:
            body["inputImage"] = input_image

        try:
            response = self._bedrock_client.invoke_model(
                modelId=DEFAULT_MODEL_ID,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            response_body = json.loads(response["body"].read())
            embedding = response_body.get("embedding", [])

            # Track costs
            if input_text:
                self._cost_tracker.add_tokens(estimated_tokens)
            if input_image:
                self._cost_tracker.add_image()

            return embedding

        except Exception as e:
            logger.error(f"Failed to invoke Nova model: {e}")
            raise RuntimeError(f"AWS Nova embedding failed: {e}") from e

    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text.

        Args:
            text: The text content to embed.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            ValueError: If the text is empty.
            RuntimeError: If the API call fails.
        """
        if not text:
            raise ValueError("text cannot be empty")

        embedding = self._invoke_model(input_text=text)

        return EmbeddingResult(
            vector=embedding,
            dimensions=self._dimensions,
            model_id=DEFAULT_MODEL_ID,
            tokens_used=len(text.split()) * 2,  # Rough estimate
        )

    def embed_image(self, image: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given image.

        Args:
            image: Either raw image bytes or a path to an image file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            FileNotFoundError: If image is a path that doesn't exist.
            RuntimeError: If the API call fails.
        """
        image_bytes = self._resolve_media_bytes(image)
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        embedding = self._invoke_model(input_image=image_b64)

        return EmbeddingResult(
            vector=embedding,
            dimensions=self._dimensions,
            model_id=DEFAULT_MODEL_ID,
        )

    def embed_audio(self, audio: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given audio.

        Audio is processed by transcribing to text using AWS Transcribe or
        a local transcription service, then embedding the transcription.

        Args:
            audio: Either raw audio bytes or a path to an audio file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            FileNotFoundError: If audio is a path that doesn't exist.
            RuntimeError: If transcription or embedding fails.
        """
        audio_path = self._resolve_media_path(audio, suffix=".wav")

        try:
            # Transcribe audio to text
            transcription = self._transcribe_audio(audio_path)

            if not transcription:
                # Fall back to a placeholder embedding if transcription is empty
                transcription = "[audio content]"

            # Track audio duration (estimate based on file size)
            audio_seconds = len(self._resolve_media_bytes(audio)) / 16000  # Rough estimate
            self._cost_tracker.add_audio_seconds(audio_seconds)

            # Embed the transcription
            return self.embed_text(transcription)

        finally:
            self._cleanup_temp_file(audio, audio_path)

    def embed_video(self, video: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given video.

        Videos are processed by extracting frames at regular intervals,
        embedding each frame, and averaging the embeddings.

        Args:
            video: Either raw video bytes or a path to a video file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            FileNotFoundError: If video is a path that doesn't exist.
            RuntimeError: If frame extraction or embedding fails.
        """
        video_path = self._resolve_media_path(video, suffix=".mp4")

        try:
            # Extract frames from video
            frames = self._extract_video_frames(video_path)

            if not frames:
                raise RuntimeError("No frames could be extracted from video")

            # Embed each frame and average
            embeddings: list[list[float]] = []
            for frame_bytes in frames:
                frame_b64 = base64.b64encode(frame_bytes).decode("utf-8")
                embedding = self._invoke_model(input_image=frame_b64)
                embeddings.append(embedding)

            # Average the embeddings
            averaged = self._average_embeddings(embeddings)

            # Track video duration (estimate based on frame count)
            video_seconds = len(frames) * self._video_frame_interval
            self._cost_tracker.add_video_seconds(video_seconds)

            return EmbeddingResult(
                vector=averaged,
                dimensions=self._dimensions,
                model_id=DEFAULT_MODEL_ID,
            )

        finally:
            self._cleanup_temp_file(video, video_path)

    def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio file to text.

        Uses a simple placeholder implementation. In production, this would
        integrate with AWS Transcribe or Whisper.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Transcription text.
        """
        # Placeholder - in production, integrate with AWS Transcribe or Whisper
        # For now, return a placeholder indicating audio content
        logger.info(f"Transcribing audio: {audio_path}")

        try:
            # Try to use faster-whisper if available
            from faster_whisper import WhisperModel

            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(audio_path))
            transcription = " ".join(segment.text for segment in segments)
            return transcription.strip()
        except ImportError:
            logger.warning("faster-whisper not available, using placeholder")
            return f"[Audio content from {audio_path.name}]"

    def _extract_video_frames(self, video_path: Path) -> list[bytes]:
        """Extract frames from video at regular intervals.

        Args:
            video_path: Path to the video file.

        Returns:
            List of frame images as JPEG bytes.
        """
        logger.info(f"Extracting frames from video: {video_path}")

        try:
            import cv2
        except ImportError:
            logger.warning("opencv-python not available, returning empty frames")
            return []

        frames: list[bytes] = []
        cap = cv2.VideoCapture(str(video_path))

        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_interval = int(fps * self._video_frame_interval)
            frame_count = 0

            while len(frames) < self._max_frames_per_video:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode(".jpg", frame)
                    frames.append(buffer.tobytes())

                frame_count += 1
        finally:
            cap.release()

        logger.info(f"Extracted {len(frames)} frames from video")
        return frames

    def _average_embeddings(self, embeddings: list[list[float]]) -> list[float]:
        """Average multiple embeddings into one.

        Args:
            embeddings: List of embedding vectors.

        Returns:
            Averaged embedding vector (normalized).
        """
        if not embeddings:
            raise ValueError("Cannot average empty embeddings list")

        n = len(embeddings)
        dim = len(embeddings[0])

        averaged = [0.0] * dim
        for emb in embeddings:
            for i, val in enumerate(emb):
                averaged[i] += val

        # Average
        averaged = [v / n for v in averaged]

        # Normalize
        norm = sum(v * v for v in averaged) ** 0.5
        if norm > 0:
            averaged = [v / norm for v in averaged]

        return averaged

    def _resolve_media_bytes(self, media: bytes | Path) -> bytes:
        """Resolve media input to bytes.

        Args:
            media: Raw bytes or path to media file.

        Returns:
            Media content as bytes.

        Raises:
            FileNotFoundError: If path doesn't exist.
        """
        if isinstance(media, bytes):
            return media

        path = Path(media)
        if not path.exists():
            raise FileNotFoundError(f"Media file not found: {path}")
        return path.read_bytes()

    def _resolve_media_path(self, media: bytes | Path, suffix: str) -> Path:
        """Resolve media input to a file path.

        If media is bytes, writes to a temporary file. If media is a Path,
        validates it exists.

        Args:
            media: Raw bytes or path to media file.
            suffix: File suffix for temp files (e.g., '.jpg', '.wav').

        Returns:
            Path to the media file.

        Raises:
            FileNotFoundError: If path doesn't exist.
        """
        if isinstance(media, bytes):
            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            Path(temp_path).write_bytes(media)
            return Path(temp_path)

        path = Path(media)
        if not path.exists():
            raise FileNotFoundError(f"Media file not found: {path}")
        return path

    def _cleanup_temp_file(self, original: bytes | Path, resolved: Path) -> None:
        """Clean up temporary file if one was created.

        Args:
            original: Original input (bytes or Path).
            resolved: Resolved path that may be a temp file.
        """
        if isinstance(original, bytes):
            try:
                resolved.unlink()
            except OSError:
                pass

    def get_estimated_cost(self) -> float:
        """Get the estimated total cost based on usage.

        Returns:
            Estimated cost in USD.
        """
        cost_info = self.metadata.cost_info
        if cost_info is None:
            return 0.0
        return self._cost_tracker.get_estimated_cost(cost_info)

    def __repr__(self) -> str:
        """Return string representation of the provider."""
        return (
            f"AWSNovaProvider("
            f"region_name={self._region_name!r}, "
            f"dimensions={self._dimensions}, "
            f"max_tokens_per_minute={self._max_tokens_per_minute}, "
            f"max_requests_per_minute={self._max_requests_per_minute})"
        )
