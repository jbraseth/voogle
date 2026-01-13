# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Video content adapter with transcription, keyframe extraction, and slide OCR.

This module provides a VideoAdapter that implements the ContentAdapter interface
for video content. It supports video transcription with timestamps, keyframe
extraction via scene detection, optional slide OCR, thumbnail generation,
and YouTube/MP4/WebM formats.
"""
import functools
import hashlib
import logging
import re
import tempfile
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import Location, SlideLocation, TimestampLocation

if TYPE_CHECKING:
    from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


# Supported video file extensions
VIDEO_EXTENSIONS: frozenset[str] = frozenset({".mp4", ".webm", ".mkv", ".avi", ".mov"})

# Default Whisper model for transcription
DEFAULT_MODEL: str = "small"

# Default device and compute type for Whisper
DEFAULT_DEVICE: str = "cpu"
DEFAULT_COMPUTE_TYPE: str = "int8"

# Default scene detection threshold (lower = more sensitive)
DEFAULT_SCENE_THRESHOLD: float = 30.0

# Default minimum scene duration in seconds
DEFAULT_MIN_SCENE_DURATION: float = 2.0


@dataclass
class VideoConfig:
    """Configuration for video processing.

    Attributes:
        model_name: Whisper model to use (tiny, base, small, medium, large).
        device: Device to run inference on (cpu, cuda, auto).
        compute_type: Compute type for inference (int8, float16, float32).
        word_timestamps: Enable word-level timestamps via WhisperX alignment.
        language: Optional language hint for transcription.
        initial_prompt: Optional prompt to guide transcription.
        extract_keyframes: Enable keyframe/scene detection.
        scene_threshold: Threshold for scene change detection (0-100).
        min_scene_duration: Minimum duration between keyframes in seconds.
        enable_slide_ocr: Enable OCR on detected slides/keyframes.
        ocr_language: Language for OCR (e.g., 'eng', 'deu').
        generate_thumbnails: Enable thumbnail generation for scenes.
        thumbnail_size: Size of generated thumbnails (width, height).
        thumbnail_dir: Directory to store thumbnails. Uses temp dir if None.
    """

    model_name: str = DEFAULT_MODEL
    device: str = DEFAULT_DEVICE
    compute_type: str = DEFAULT_COMPUTE_TYPE
    word_timestamps: bool = False
    language: str | None = None
    initial_prompt: str | None = None
    extract_keyframes: bool = True
    scene_threshold: float = DEFAULT_SCENE_THRESHOLD
    min_scene_duration: float = DEFAULT_MIN_SCENE_DURATION
    enable_slide_ocr: bool = False
    ocr_language: str = "eng"
    generate_thumbnails: bool = False
    thumbnail_size: tuple[int, int] = (320, 180)
    thumbnail_dir: Path | None = None


@dataclass
class Keyframe:
    """Represents a detected keyframe/scene in the video.

    Attributes:
        timestamp: Time position in seconds.
        frame_index: Frame number in the video.
        image_path: Path to the extracted frame image, if saved.
        ocr_text: OCR-extracted text from the frame, if enabled.
        thumbnail_path: Path to the thumbnail, if generated.
        scene_score: Scene detection confidence score.
    """

    timestamp: float
    frame_index: int = 0
    image_path: Path | None = None
    ocr_text: str | None = None
    thumbnail_path: Path | None = None
    scene_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


def _get_cv2() -> Any:
    """Lazy import of OpenCV module.

    Returns:
        The cv2 module from OpenCV.

    Raises:
        ImportError: If OpenCV is not installed.
    """
    try:
        import cv2
        return cv2
    except ImportError as e:
        raise ImportError(
            "OpenCV is required for video processing. "
            "Install with: pip install 'voogle[video]' or pip install opencv-python"
        ) from e


def _get_pytesseract() -> Any:
    """Lazy import of pytesseract module.

    Returns:
        The pytesseract module.

    Raises:
        ImportError: If pytesseract is not installed.
    """
    try:
        import pytesseract
        return pytesseract
    except ImportError as e:
        raise ImportError(
            "pytesseract is required for OCR. "
            "Install with: pip install 'voogle[video]' or pip install pytesseract"
        ) from e


def _get_yt_dlp() -> Any:
    """Lazy import of yt-dlp module.

    Returns:
        The yt_dlp module.

    Raises:
        ImportError: If yt-dlp is not installed.
    """
    try:
        import yt_dlp
        return yt_dlp
    except ImportError as e:
        raise ImportError(
            "yt-dlp is required for YouTube video processing. "
            "Install with: pip install 'voogle[video]' or pip install yt-dlp"
        ) from e


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


def _is_youtube_url(url: str) -> bool:
    """Check if the URL is a YouTube video URL.

    Args:
        url: URL to check.

    Returns:
        True if the URL is a YouTube video URL.
    """
    youtube_patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"(?:https?://)?(?:www\.)?youtu\.be/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+",
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)


class VideoAdapter(ContentAdapter):
    """Content adapter for video files with transcription and keyframe extraction.

    Supports MP4, WebM, MKV, AVI, MOV, and YouTube URLs. Provides:
    - Video transcription using Whisper
    - Keyframe extraction via scene detection
    - Optional slide OCR on keyframes
    - Thumbnail generation
    - TimestampLocation and SlideLocation for deep linking

    Example:
        >>> adapter = VideoAdapter()
        >>> source = ContentSource(
        ...     source_id="video-123",
        ...     source_type=ContentType.VIDEO,
        ...     path=Path("/data/lecture.mp4"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: VideoConfig | None = None) -> None:
        """Initialize the video adapter.

        Args:
            config: Video processing configuration. Uses defaults if not provided.
        """
        self._config = config or VideoConfig()

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.VIDEO.
        """
        return frozenset({ContentType.VIDEO})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is video with a supported file extension or YouTube URL.
        """
        if source.source_type != ContentType.VIDEO:
            return False

        # Check file extension if path is available
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in VIDEO_EXTENSIONS

        # Check URL for YouTube or video extension
        if source.url is not None:
            # Check for YouTube URL
            if _is_youtube_url(source.url):
                return True

            # Try to extract extension from URL path
            from urllib.parse import urlparse

            parsed = urlparse(source.url)
            url_path = parsed.path
            if "." in url_path:
                suffix = "." + url_path.rsplit(".", 1)[-1].lower()
                if suffix in VIDEO_EXTENSIONS:
                    return True

            # Check MIME type in metadata as fallback
            mime_type = source.metadata.get("mime_type", "")
            return mime_type.startswith("video/")

        return False

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract transcription and keyframe chunks from a video.

        Transcribes the video audio using Whisper and optionally extracts
        keyframes with scene detection and OCR.

        Args:
            source: The video source to process.

        Yields:
            RawChunk instances with transcribed text and/or slide content.

        Raises:
            ValueError: If the source is not supported or file not found.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        video_path = await self._resolve_video_path(source)

        try:
            logger.info("Starting video processing of %s", video_path)

            # Extract transcription
            async for chunk in self._extract_transcription(video_path, source):
                yield chunk

            # Extract keyframes if enabled
            if self._config.extract_keyframes:
                async for chunk in self._extract_keyframes(video_path, source):
                    yield chunk

            logger.info("Completed video processing of %s", video_path)

        finally:
            # Clean up downloaded video if it was from YouTube
            if source.url and _is_youtube_url(source.url) and source.path is None:
                if video_path.exists():
                    video_path.unlink()
                    logger.debug("Cleaned up temporary video file: %s", video_path)

    async def _resolve_video_path(self, source: ContentSource) -> Path:
        """Resolve the video file path, downloading if necessary.

        Args:
            source: The content source.

        Returns:
            Path to the local video file.

        Raises:
            ValueError: If the video cannot be resolved.
        """
        if source.path is not None:
            if not source.path.exists():
                raise ValueError(f"Video file not found: {source.path}")
            return source.path

        if source.url is None:
            raise ValueError(f"Video source {source.source_id} requires a path or URL")

        # Download YouTube video
        if _is_youtube_url(source.url):
            return await self._download_youtube(source.url, source.source_id)

        raise ValueError(
            f"Video source {source.source_id} requires a local file path "
            "(remote non-YouTube URLs not yet supported)"
        )

    async def _download_youtube(self, url: str, source_id: str) -> Path:
        """Download a YouTube video to a temporary file.

        Args:
            url: YouTube video URL.
            source_id: Source identifier for naming.

        Returns:
            Path to the downloaded video file.
        """
        yt_dlp = _get_yt_dlp()

        # Create a unique filename based on source_id
        hash_suffix = hashlib.md5(source_id.encode()).hexdigest()[:8]
        temp_dir = Path(tempfile.gettempdir())
        output_template = str(temp_dir / f"voogle_yt_{hash_suffix}.%(ext)s")

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        logger.info("Downloading YouTube video: %s", url)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the actual downloaded filename
            if info and "requested_downloads" in info:
                filepath = info["requested_downloads"][0]["filepath"]
            else:
                # Fallback: look for the file
                filepath = output_template.replace("%(ext)s", "mp4")

        video_path = Path(filepath)
        if not video_path.exists():
            raise ValueError(f"Failed to download YouTube video: {url}")

        logger.info("Downloaded YouTube video to: %s", video_path)
        return video_path

    async def _extract_transcription(
        self,
        video_path: Path,
        source: ContentSource,
    ) -> AsyncIterator[RawChunk]:
        """Extract transcription from video audio.

        Args:
            video_path: Path to the video file.
            source: The content source.

        Yields:
            RawChunk instances with transcribed text and timestamps.
        """
        logger.info("Starting transcription of %s", video_path)

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

        # Transcribe the video (Whisper can process video files directly)
        segments, info = model.transcribe(str(video_path), **transcribe_kwargs)

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

        logger.info("Completed transcription of %s", video_path)

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

            metadata: dict[str, Any] = {
                "language": info.language,
                "chunk_type": "transcription",
            }
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
                        metadata={"language": info.language, "chunk_type": "transcription"},
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
                        "chunk_type": "transcription",
                    },
                )

    async def _extract_keyframes(
        self,
        video_path: Path,
        source: ContentSource,
    ) -> AsyncIterator[RawChunk]:
        """Extract keyframes using scene detection.

        Args:
            video_path: Path to the video file.
            source: The content source.

        Yields:
            RawChunk instances for detected keyframes/slides with OCR text.
        """
        cv2 = _get_cv2()

        logger.info("Starting keyframe extraction from %s", video_path)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error("Failed to open video file: %s", video_path)
            return

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30.0  # Fallback default

            min_frames_between = int(fps * self._config.min_scene_duration)

            prev_hist = None
            frame_index = 0
            last_keyframe_index = -min_frames_between  # Allow first frame as keyframe
            slide_number = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert to grayscale for histogram comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist)

                if prev_hist is not None:
                    # Calculate histogram correlation
                    correlation = cv2.compareHist(
                        prev_hist, hist, cv2.HISTCMP_CORREL
                    )
                    # Convert correlation to a "difference" score (0-100 scale)
                    diff_score = (1 - correlation) * 100

                    # Check for scene change
                    if (
                        diff_score >= self._config.scene_threshold
                        and (frame_index - last_keyframe_index) >= min_frames_between
                    ):
                        timestamp = frame_index / fps
                        slide_number += 1

                        keyframe = await self._process_keyframe(
                            frame,
                            timestamp,
                            frame_index,
                            slide_number,
                            diff_score,
                            source,
                        )

                        # Only yield if we have OCR text or if OCR is disabled
                        if keyframe.ocr_text or not self._config.enable_slide_ocr:
                            chunk = self._keyframe_to_chunk(keyframe, slide_number)
                            if chunk:
                                yield chunk

                        last_keyframe_index = frame_index

                prev_hist = hist
                frame_index += 1

            logger.info(
                "Extracted %d keyframes from %s",
                slide_number,
                video_path,
            )

        finally:
            cap.release()

    async def _process_keyframe(
        self,
        frame: Any,
        timestamp: float,
        frame_index: int,
        slide_number: int,
        scene_score: float,
        source: ContentSource,
    ) -> Keyframe:
        """Process a detected keyframe.

        Args:
            frame: OpenCV frame (numpy array).
            timestamp: Time position in seconds.
            frame_index: Frame number.
            slide_number: Sequential slide number.
            scene_score: Scene detection confidence.
            source: The content source.

        Returns:
            Processed Keyframe with optional OCR text and thumbnail.
        """
        cv2 = _get_cv2()

        keyframe = Keyframe(
            timestamp=timestamp,
            frame_index=frame_index,
            scene_score=scene_score,
        )

        # Generate thumbnail if enabled
        if self._config.generate_thumbnails:
            thumbnail_dir = self._config.thumbnail_dir or Path(tempfile.gettempdir())
            thumbnail_dir.mkdir(parents=True, exist_ok=True)

            thumbnail_name = f"{source.source_id}_slide_{slide_number:04d}.jpg"
            thumbnail_path = thumbnail_dir / thumbnail_name

            # Resize frame for thumbnail
            resized = cv2.resize(
                frame,
                self._config.thumbnail_size,
                interpolation=cv2.INTER_AREA,
            )
            cv2.imwrite(str(thumbnail_path), resized)
            keyframe.thumbnail_path = thumbnail_path
            keyframe.metadata["thumbnail_path"] = str(thumbnail_path)

        # Perform OCR if enabled
        if self._config.enable_slide_ocr:
            try:
                pytesseract = _get_pytesseract()
                # Convert BGR to RGB for pytesseract
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ocr_text = pytesseract.image_to_string(
                    rgb_frame,
                    lang=self._config.ocr_language,
                )
                # Clean up OCR text
                ocr_text = self._normalize_text(ocr_text)
                if ocr_text:
                    keyframe.ocr_text = ocr_text
            except Exception as e:
                logger.warning("OCR failed for frame at %s: %s", timestamp, e)

        return keyframe

    def _keyframe_to_chunk(
        self,
        keyframe: Keyframe,
        slide_number: int,
    ) -> RawChunk | None:
        """Convert a keyframe to a RawChunk.

        Args:
            keyframe: The processed keyframe.
            slide_number: Sequential slide number.

        Returns:
            RawChunk with slide location, or None if no text available.
        """
        if not keyframe.ocr_text:
            return None

        location = SlideLocation(
            slide_number=slide_number,
        )

        metadata: dict[str, Any] = {
            "chunk_type": "slide",
            "timestamp": keyframe.timestamp,
            "frame_index": keyframe.frame_index,
            "scene_score": keyframe.scene_score,
        }
        if keyframe.thumbnail_path:
            metadata["thumbnail_path"] = str(keyframe.thumbnail_path)

        return RawChunk(
            text=keyframe.ocr_text,
            location=location,
            metadata=metadata,
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text.

        Args:
            text: Raw extracted text.

        Returns:
            Normalized text with cleaned whitespace.
        """
        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw video chunks into text chunks for embedding.

        Combines adjacent transcription segments into chunks of approximately
        target_words words. Slide chunks are kept separate.

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

        # Separate transcription and slide chunks
        transcription_chunks = [
            c for c in raw_chunks
            if c.metadata.get("chunk_type") == "transcription"
        ]
        slide_chunks = [
            c for c in raw_chunks
            if c.metadata.get("chunk_type") == "slide"
        ]

        # Process transcription chunks (combine based on word count)
        text_chunks.extend(
            self._chunk_transcription(transcription_chunks, source, cfg)
        )

        # Process slide chunks (keep separate, they're already distinct)
        sequence_start = len(text_chunks)
        text_chunks.extend(
            self._chunk_slides(slide_chunks, source, sequence_start)
        )

        return text_chunks

    def _chunk_transcription(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig,
    ) -> list[TextChunk]:
        """Chunk transcription segments based on word count.

        Args:
            raw_chunks: List of transcription RawChunks.
            source: The content source.
            config: Chunking configuration.

        Returns:
            List of TextChunk instances.
        """
        if not raw_chunks:
            return []

        text_chunks: list[TextChunk] = []
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
            if len(current_words) >= config.target_words:
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
                        metadata={"chunk_type": "transcription"},
                    )
                )
                sequence_index += 1

                # Handle overlap
                if config.overlap_words > 0 and len(current_words) > config.overlap_words:
                    current_words = current_words[-config.overlap_words:]
                    current_start = current_end
                else:
                    current_words = []
                    current_start = None
                    current_end = None

        # Final chunk
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
                    metadata={"chunk_type": "transcription"},
                )
            )

        return text_chunks

    def _chunk_slides(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        sequence_start: int,
    ) -> list[TextChunk]:
        """Convert slide chunks to TextChunks.

        Slides are kept as individual chunks since they represent
        distinct visual content.

        Args:
            raw_chunks: List of slide RawChunks.
            source: The content source.
            sequence_start: Starting sequence index.

        Returns:
            List of TextChunk instances.
        """
        text_chunks: list[TextChunk] = []

        for i, raw_chunk in enumerate(raw_chunks):
            text_chunks.append(
                TextChunk(
                    text=raw_chunk.text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=raw_chunk.location,
                    sequence_index=sequence_start + i,
                    metadata=dict(raw_chunk.metadata),
                )
            )

        return text_chunks

    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            TimestampLocation or SlideLocation for the chunk,
            or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a URL with timestamp or slide fragment to navigate
        directly to the position in the video player or slide view.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the video content.

        Returns:
            URL with appropriate parameter for navigation, or None if
            no location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
