# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""LanguageBind embedding provider implementation.

Implements the EmbeddingProvider interface using the LanguageBind model for unified
text, image, audio, and video embeddings. LanguageBind produces aligned embeddings
across all four modalities in a shared 768-dimensional space.

Usage:
    from voogle.embedding.languagebind import LanguageBindProvider

    # Default configuration
    provider = LanguageBindProvider()

    # With GPU and custom settings
    provider = LanguageBindProvider(
        device="cuda",
        cache_dir="/path/to/models",
        video_num_frames=8,
        audio_segment_seconds=10.0,
    )

    # Embed different modalities
    text_result = provider.embed_text("A dog playing in the park")
    image_result = provider.embed_image("/path/to/image.jpg")
    audio_result = provider.embed_audio("/path/to/audio.wav")
    video_result = provider.embed_video("/path/to/video.mp4")
"""

from __future__ import annotations

import functools
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from voogle.embedding.provider import (
    ContentModality,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)

logger = logging.getLogger(__name__)

# LanguageBind model identifiers
DEFAULT_MODEL_ID = "LanguageBind/LanguageBind_Image"
LANGUAGEBIND_DIMENSIONS = 768

# Default configurations
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/languagebind")
DEFAULT_VIDEO_NUM_FRAMES = 8
DEFAULT_AUDIO_SEGMENT_SECONDS = 10.0
DEFAULT_BATCH_SIZE = 8


def _get_device(device: str | None) -> str:
    """Determine the device to use.

    Args:
        device: Explicit device string or None for auto-detection.

    Returns:
        Device string ('cuda' or 'cpu').
    """
    if device is not None:
        return device
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


@functools.cache
def _load_languagebind_models(
    device: str, cache_dir: str
) -> dict[str, Any]:
    """Load and cache LanguageBind models.

    Loads all modality-specific models (image, video, audio) and the shared
    text tokenizer. Models are downloaded on first use and cached.

    Args:
        device: Device to load models on ('cpu' or 'cuda').
        cache_dir: Directory to cache downloaded models.

    Returns:
        Dictionary containing loaded models and processors.
    """
    try:
        from languagebind import (
            LanguageBind,
            LanguageBindAudioProcessor,
            LanguageBindImageProcessor,
            LanguageBindVideoProcessor,
            to_device,
        )
        from transformers import CLIPTokenizer
    except ImportError as e:
        raise ImportError(
            "LanguageBind requires the 'languagebind' package. "
            "Install it with: pip install languagebind"
        ) from e

    logger.info(f"Loading LanguageBind models (device={device}, cache_dir={cache_dir})")

    # Define clip type for each modality
    clip_types = {
        "video": "LanguageBind_Video_FT",
        "audio": "LanguageBind_Audio_FT",
        "image": "LanguageBind_Image",
    }

    # Load the unified model
    model = LanguageBind(clip_type=clip_types, cache_dir=cache_dir)
    model = model.eval()
    model = to_device(model, device)

    # Load tokenizer for text
    tokenizer = CLIPTokenizer.from_pretrained(
        "LanguageBind/LanguageBind_Image",
        cache_dir=cache_dir,
    )

    # Load processors for each modality
    processors = {
        "image": LanguageBindImageProcessor(model.modality_config["image"]),
        "video": LanguageBindVideoProcessor(model.modality_config["video"]),
        "audio": LanguageBindAudioProcessor(model.modality_config["audio"]),
    }

    return {
        "model": model,
        "tokenizer": tokenizer,
        "processors": processors,
        "device": device,
    }


class LanguageBindProvider(EmbeddingProvider):
    """Embedding provider using LanguageBind for multimodal embeddings.

    LanguageBind produces aligned embeddings for text, image, audio, and video
    content in a shared 768-dimensional space. This enables cross-modal retrieval
    (e.g., finding images that match a text query).

    The provider handles:
    - Model download and caching to specified directory
    - GPU memory management with configurable device
    - Frame sampling for videos (configurable number of frames)
    - Audio segment handling (recommended 10 seconds)

    Attributes:
        device: The compute device being used.
        cache_dir: Directory where models are cached.
    """

    def __init__(
        self,
        device: str | None = None,
        cache_dir: str | None = None,
        video_num_frames: int = DEFAULT_VIDEO_NUM_FRAMES,
        audio_segment_seconds: float = DEFAULT_AUDIO_SEGMENT_SECONDS,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Initialize the LanguageBind provider.

        Args:
            device: Compute device to use. Options:
                   - None: Auto-select (GPU if available, else CPU)
                   - 'cpu': Force CPU
                   - 'cuda': Use default CUDA device
                   - 'cuda:0', 'cuda:1': Use specific CUDA device
            cache_dir: Directory to cache downloaded models. Defaults to
                      ~/.cache/languagebind
            video_num_frames: Number of frames to sample from videos.
                             More frames = better quality but more memory.
            audio_segment_seconds: Length of audio segments to process.
                                  10 seconds is recommended for best results.
            batch_size: Maximum batch size for batch operations.
        """
        self._device = _get_device(device)
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._video_num_frames = video_num_frames
        self._audio_segment_seconds = audio_segment_seconds
        self._batch_size = batch_size
        self._models: dict[str, Any] | None = None

    @property
    def _loaded_models(self) -> dict[str, Any]:
        """Lazy-load models on first use."""
        if self._models is None:
            self._models = _load_languagebind_models(self._device, self._cache_dir)
        return self._models

    @property
    def supported_modalities(self) -> frozenset[ContentModality]:
        """Return the set of supported modalities."""
        return frozenset([
            ContentModality.TEXT,
            ContentModality.IMAGE,
            ContentModality.AUDIO,
            ContentModality.VIDEO,
        ])

    @property
    def metadata(self) -> ProviderMetadata:
        """Return metadata describing this provider's capabilities."""
        return ProviderMetadata(
            provider_id="languagebind",
            model_id=DEFAULT_MODEL_ID,
            supported_modalities=self.supported_modalities,
            dimensions=LANGUAGEBIND_DIMENSIONS,
            max_batch_size=self._batch_size,
            description="Unified multimodal embeddings for text, image, audio, and video",
        )

    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text.

        Args:
            text: The text content to embed.

        Returns:
            EmbeddingResult containing the 768-dimensional embedding vector.

        Raises:
            ValueError: If the text is empty.
        """
        if not text:
            raise ValueError("text cannot be empty")

        models = self._loaded_models
        model = models["model"]
        tokenizer = models["tokenizer"]
        device = models["device"]

        # Tokenize the text
        inputs = tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=77,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate embedding
        import torch
        with torch.no_grad():
            # Use the language encoder directly
            text_embeds = model.get_text_features(inputs)
            # Normalize
            text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
            embedding = text_embeds[0].cpu().numpy().tolist()

        return EmbeddingResult(
            vector=embedding,
            dimensions=LANGUAGEBIND_DIMENSIONS,
            model_id=DEFAULT_MODEL_ID,
        )

    def embed_image(self, image: bytes | Path) -> EmbeddingResult:
        """Generate an embedding for the given image.

        Args:
            image: Either raw image bytes or a path to an image file.

        Returns:
            EmbeddingResult containing the 768-dimensional embedding vector.

        Raises:
            FileNotFoundError: If image is a path that doesn't exist.
            ValueError: If the image cannot be processed.
        """
        image_path = self._resolve_media_path(image, suffix=".jpg")

        models = self._loaded_models
        model = models["model"]
        processor = models["processors"]["image"]
        device = models["device"]

        # Process the image
        inputs = processor([str(image_path)], return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate embedding
        import torch
        with torch.no_grad():
            image_embeds = model.get_image_features(inputs)
            image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
            embedding = image_embeds[0].cpu().numpy().tolist()

        # Clean up temp file if created
        self._cleanup_temp_file(image, image_path)

        return EmbeddingResult(
            vector=embedding,
            dimensions=LANGUAGEBIND_DIMENSIONS,
            model_id=DEFAULT_MODEL_ID,
        )

    def embed_audio(self, audio: bytes | Path) -> EmbeddingResult:
        """Generate an embedding for the given audio.

        Audio is processed in segments. For best results, provide audio clips
        around 10 seconds in length. Longer audio will be truncated.

        Args:
            audio: Either raw audio bytes or a path to an audio file.

        Returns:
            EmbeddingResult containing the 768-dimensional embedding vector.

        Raises:
            FileNotFoundError: If audio is a path that doesn't exist.
            ValueError: If the audio cannot be processed.
        """
        audio_path = self._resolve_media_path(audio, suffix=".wav")

        models = self._loaded_models
        model = models["model"]
        processor = models["processors"]["audio"]
        device = models["device"]

        # Process the audio
        inputs = processor([str(audio_path)], return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate embedding
        import torch
        with torch.no_grad():
            audio_embeds = model.get_audio_features(inputs)
            audio_embeds = audio_embeds / audio_embeds.norm(dim=-1, keepdim=True)
            embedding = audio_embeds[0].cpu().numpy().tolist()

        # Clean up temp file if created
        self._cleanup_temp_file(audio, audio_path)

        return EmbeddingResult(
            vector=embedding,
            dimensions=LANGUAGEBIND_DIMENSIONS,
            model_id=DEFAULT_MODEL_ID,
        )

    def embed_video(self, video: bytes | Path) -> EmbeddingResult:
        """Generate an embedding for the given video.

        Videos are processed by sampling a configurable number of frames
        (default 8) uniformly across the video duration.

        Args:
            video: Either raw video bytes or a path to a video file.

        Returns:
            EmbeddingResult containing the 768-dimensional embedding vector.

        Raises:
            FileNotFoundError: If video is a path that doesn't exist.
            ValueError: If the video cannot be processed.
        """
        video_path = self._resolve_media_path(video, suffix=".mp4")

        models = self._loaded_models
        model = models["model"]
        processor = models["processors"]["video"]
        device = models["device"]

        # Process the video
        inputs = processor(
            [str(video_path)],
            return_tensors="pt",
            num_frames=self._video_num_frames,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate embedding
        import torch
        with torch.no_grad():
            video_embeds = model.get_video_features(inputs)
            video_embeds = video_embeds / video_embeds.norm(dim=-1, keepdim=True)
            embedding = video_embeds[0].cpu().numpy().tolist()

        # Clean up temp file if created
        self._cleanup_temp_file(video, video_path)

        return EmbeddingResult(
            vector=embedding,
            dimensions=LANGUAGEBIND_DIMENSIONS,
            model_id=DEFAULT_MODEL_ID,
        )

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
            # Write bytes to temp file
            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            Path(temp_path).write_bytes(media)
            return Path(temp_path)
        else:
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

    @property
    def device(self) -> str:
        """Return the device the models are loaded on."""
        return self._device

    @property
    def cache_dir(self) -> str:
        """Return the model cache directory."""
        return self._cache_dir

    def __repr__(self) -> str:
        """Return string representation of the provider."""
        return (
            f"LanguageBindProvider("
            f"device={self._device!r}, "
            f"cache_dir={self._cache_dir!r}, "
            f"video_num_frames={self._video_num_frames}, "
            f"audio_segment_seconds={self._audio_segment_seconds})"
        )
