# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Audio content adapter for transcribing audio files using Whisper.

This module provides an AudioAdapter that implements the ContentAdapter interface
for audio content. It uses faster-whisper for transcription and optionally
supports word-level timestamps via WhisperX alignment.
"""
import functools
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import Location, TimestampLocation

if TYPE_CHECKING:
    from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


# Supported audio file extensions
AUDIO_EXTENSIONS: frozenset[str] = frozenset({".mp3", ".wav", ".flac", ".m4a"})

# Default Whisper model for transcription
DEFAULT_MODEL: str = "small"

# Default device and compute type for Whisper
DEFAULT_DEVICE: str = "cpu"
DEFAULT_COMPUTE_TYPE: str = "int8"


@dataclass
class TranscriptionConfig:
    """Configuration for audio transcription.

    Attributes:
        model_name: Whisper model to use (tiny, base, small, medium, large).
        device: Device to run inference on (cpu, cuda, auto).
        compute_type: Compute type for inference (int8, float16, float32).
        word_timestamps: Enable word-level timestamps via WhisperX alignment.
        language: Optional language hint for transcription.
        initial_prompt: Optional prompt to guide transcription.
    """

    model_name: str = DEFAULT_MODEL
    device: str = DEFAULT_DEVICE
    compute_type: str = DEFAULT_COMPUTE_TYPE
    word_timestamps: bool = False
    language: str | None = None
    initial_prompt: str | None = None


@functools.cache
def _get_model(
    model_name: str = DEFAULT_MODEL,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE_TYPE,
) -> "WhisperModel":
    """Get or create a cached Whisper model instance.

    Args:
        model_name: Whisper model to load.
        device: Device to run inference on.
        compute_type: Compute type for inference.

    Returns:
        Cached WhisperModel instance.
    """
    # Lazy import - only needed when actually transcribing
    from faster_whisper import WhisperModel as _WhisperModel

    logger.info(
        "Loading Whisper model: %s (device=%s, compute=%s)",
        model_name,
        device,
        compute_type,
    )
    return _WhisperModel(model_name, device=device, compute_type=compute_type)


class AudioAdapter(ContentAdapter):
    """Content adapter for audio files using Whisper transcription.

    Supports MP3, WAV, FLAC, and M4A audio formats. Uses faster-whisper
    for transcription with optional word-level timestamps.

    Example:
        >>> adapter = AudioAdapter()
        >>> source = ContentSource(
        ...     source_id="podcast-123",
        ...     source_type=ContentType.AUDIO,
        ...     path=Path("/data/episode.mp3"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: TranscriptionConfig | None = None) -> None:
        """Initialize the audio adapter.

        Args:
            config: Transcription configuration. Uses defaults if not provided.
        """
        self._config = config or TranscriptionConfig()

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.AUDIO.
        """
        return frozenset({ContentType.AUDIO})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is audio with a supported file extension.
        """
        if source.source_type != ContentType.AUDIO:
            return False

        # Check file extension if path is available
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in AUDIO_EXTENSIONS

        # Check URL extension or MIME type
        if source.url is not None:
            # Try to extract extension from URL path (not domain)
            from urllib.parse import urlparse

            parsed = urlparse(source.url)
            url_path = parsed.path
            if "." in url_path:
                suffix = "." + url_path.rsplit(".", 1)[-1].lower()
                if suffix in AUDIO_EXTENSIONS:
                    return True

            # Check MIME type in metadata as fallback
            mime_type = source.metadata.get("mime_type", "")
            return mime_type.startswith("audio/")

        return False

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract transcription chunks from an audio file.

        Transcribes the audio using Whisper and yields RawChunk instances
        with text and timestamp locations. If word_timestamps is enabled,
        provides word-level timing; otherwise uses segment-level timing.

        Args:
            source: The audio source to transcribe.

        Yields:
            RawChunk instances with transcribed text and TimestampLocation.

        Raises:
            ValueError: If the source is not supported or file not found.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        if source.path is None:
            raise ValueError(
                f"Audio source {source.source_id} requires a local file path"
            )

        if not source.path.exists():
            raise ValueError(f"Audio file not found: {source.path}")

        logger.info("Starting transcription of %s", source.path)

        # Get or create the Whisper model
        model = _get_model(
            self._config.model_name,
            self._config.device,
            self._config.compute_type,
        )

        # Build transcription kwargs
        transcribe_kwargs: dict[str, Any] = {
            "word_timestamps": self._config.word_timestamps,
        }
        if self._config.language:
            transcribe_kwargs["language"] = self._config.language
        if self._config.initial_prompt:
            transcribe_kwargs["initial_prompt"] = self._config.initial_prompt

        # Transcribe the audio
        segments, info = model.transcribe(str(source.path), **transcribe_kwargs)

        logger.debug(
            "Detected language: %s (probability: %.2f)",
            info.language,
            info.language_probability,
        )

        # Yield chunks based on timestamp mode
        if self._config.word_timestamps:
            async for chunk in self._extract_word_level(segments, info):
                yield chunk
        else:
            async for chunk in self._extract_segment_level(segments, info):
                yield chunk

        logger.info("Completed transcription of %s", source.path)

    async def _extract_segment_level(
        self,
        segments: Any,
        info: Any,
    ) -> AsyncIterator[RawChunk]:
        """Extract chunks at segment level (sentence/phrase boundaries).

        Args:
            segments: Iterator of transcription segments from faster-whisper.
            info: Transcription info from faster-whisper.

        Yields:
            RawChunk instances with segment-level timestamps.
        """
        for segment in segments:
            text = segment.text.strip()
            if not text:
                continue

            location = TimestampLocation(
                start_time=segment.start,
                end_time=segment.end,
            )

            # Note: avg_logprob is a log probability, not suitable for confidence
            # We store it in metadata instead
            metadata: dict[str, Any] = {"language": info.language}
            if hasattr(segment, "id"):
                metadata["segment_id"] = segment.id
            if hasattr(segment, "avg_logprob"):
                metadata["avg_logprob"] = segment.avg_logprob

            yield RawChunk(
                text=text,
                location=location,
                metadata=metadata,
            )

    async def _extract_word_level(
        self,
        segments: Any,
        info: Any,
    ) -> AsyncIterator[RawChunk]:
        """Extract chunks at word level with precise timestamps.

        When word_timestamps is enabled, this extracts each word with
        its individual start/end time.

        Args:
            segments: Iterator of transcription segments from faster-whisper.
            info: Transcription info from faster-whisper.

        Yields:
            RawChunk instances with word-level timestamps.
        """
        for segment in segments:
            if not hasattr(segment, "words") or not segment.words:
                # Fall back to segment-level if no word info
                text = segment.text.strip()
                if text:
                    yield RawChunk(
                        text=text,
                        location=TimestampLocation(
                            start_time=segment.start,
                            end_time=segment.end,
                        ),
                        metadata={"language": info.language},
                    )
                continue

            for word in segment.words:
                text = word.word.strip()
                if not text:
                    continue

                location = TimestampLocation(
                    start_time=word.start,
                    end_time=word.end,
                )

                yield RawChunk(
                    text=text,
                    location=location,
                    confidence=word.probability if hasattr(word, "probability") else None,
                    metadata={
                        "language": info.language,
                        "segment_id": segment.id if hasattr(segment, "id") else None,
                    },
                )

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw transcription chunks into text chunks for embedding.

        Combines adjacent transcription segments into chunks of approximately
        target_words words, preserving timestamp information for deep linking.

        Args:
            raw_chunks: List of RawChunk instances from extraction.
            source: The source these chunks came from.
            config: Chunking configuration. Uses defaults if not provided.

        Returns:
            List of TextChunk instances ready for embedding.
        """
        if not raw_chunks:
            return []

        cfg = config or ChunkConfig()
        text_chunks: list[TextChunk] = []

        # Accumulate words/segments into chunks
        current_words: list[str] = []
        current_start: float | None = None
        current_end: float | None = None
        sequence_index = 0

        for raw_chunk in raw_chunks:
            words = raw_chunk.text.split()

            # Update timestamps
            if raw_chunk.location and isinstance(raw_chunk.location, TimestampLocation):
                if current_start is None:
                    current_start = raw_chunk.location.start_time
                current_end = raw_chunk.location.end_time

            current_words.extend(words)

            # Check if we've reached the target word count
            if len(current_words) >= cfg.target_words:
                # Create chunk with current accumulated content
                text = " ".join(current_words)
                location = None
                if current_start is not None:
                    location = TimestampLocation(
                        start_time=current_start,
                        end_time=current_end,
                    )

                text_chunks.append(
                    TextChunk(
                        text=text,
                        source_id=source.source_id,
                        source_type=source.source_type,
                        location=location,
                        sequence_index=sequence_index,
                    )
                )
                sequence_index += 1

                # Handle overlap: keep last overlap_words for context
                if cfg.overlap_words > 0 and len(current_words) > cfg.overlap_words:
                    overlap_words = current_words[-cfg.overlap_words:]
                    current_words = overlap_words
                    # Preserve the end timestamp as new start
                    current_start = current_end
                else:
                    current_words = []
                    current_start = None
                    current_end = None

        # Don't forget the final chunk
        if current_words:
            text = " ".join(current_words)
            location = None
            if current_start is not None:
                location = TimestampLocation(
                    start_time=current_start,
                    end_time=current_end,
                )

            text_chunks.append(
                TextChunk(
                    text=text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=location,
                    sequence_index=sequence_index,
                )
            )

        return text_chunks

    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            TimestampLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a URL with timestamp fragment to jump directly to the
        position in the audio/video player.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the audio content.

        Returns:
            URL with timestamp parameter (e.g., ?t=120.5), or None if
            no timestamp location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
