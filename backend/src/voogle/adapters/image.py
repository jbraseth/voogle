# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Image content adapter with CLIP/SigLIP embeddings and optional OCR.

This module provides an ImageAdapter that implements the ContentAdapter interface
for image content. It supports image preprocessing, CLIP/SigLIP embedding generation,
OCR text extraction, EXIF metadata extraction, thumbnail generation,
and JPEG/PNG/WebP/GIF formats.
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
from voogle.core.location import ImageRegionLocation, Location

if TYPE_CHECKING:
    from PIL import Image as PILImage

logger = logging.getLogger(__name__)


# Supported image file extensions
IMAGE_EXTENSIONS: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})

# Default CLIP/SigLIP model for embedding generation
DEFAULT_MODEL: str = "openai/clip-vit-base-patch32"

# Default device for inference
DEFAULT_DEVICE: str = "cpu"

# Default thumbnail size
DEFAULT_THUMBNAIL_SIZE: tuple[int, int] = (256, 256)


@dataclass
class ImageConfig:
    """Configuration for image processing.

    Attributes:
        model_name: CLIP/SigLIP model to use for embedding generation.
        device: Device to run inference on (cpu, cuda, auto).
        enable_ocr: Enable OCR text extraction from images.
        ocr_language: Language for OCR (e.g., 'eng', 'deu').
        extract_exif: Enable EXIF metadata extraction.
        generate_thumbnail: Enable thumbnail generation.
        thumbnail_size: Size of generated thumbnails (width, height).
        thumbnail_dir: Directory to store thumbnails. Uses temp dir if None.
        preprocess_resize: Target size for preprocessing images (width, height).
        extract_regions: Enable region-based content extraction.
        region_min_area: Minimum region area (percentage of image) to extract.
    """

    model_name: str = DEFAULT_MODEL
    device: str = DEFAULT_DEVICE
    enable_ocr: bool = False
    ocr_language: str = "eng"
    extract_exif: bool = True
    generate_thumbnail: bool = False
    thumbnail_size: tuple[int, int] = DEFAULT_THUMBNAIL_SIZE
    thumbnail_dir: Path | None = None
    preprocess_resize: tuple[int, int] | None = None
    extract_regions: bool = False
    region_min_area: float = 5.0


@dataclass
class ExtractedRegion:
    """Represents an extracted region from an image.

    Attributes:
        x: Left edge of region (0-100, percentage of image width).
        y: Top edge of region (0-100, percentage of image height).
        width: Width of region (0-100, percentage of image width).
        height: Height of region (0-100, percentage of image height).
        text: Extracted text from the region, if any.
        confidence: Confidence score for the extraction.
        metadata: Additional region metadata.
    """

    x: float
    y: float
    width: float
    height: float
    text: str | None = None
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


def _get_pil() -> Any:
    """Lazy import of PIL module.

    Returns:
        The PIL.Image module.

    Raises:
        ImportError: If Pillow is not installed.
    """
    try:
        from PIL import Image
        return Image
    except ImportError as e:
        raise ImportError(
            "Pillow is required for image processing. "
            "Install with: pip install 'voogle[image]' or pip install Pillow"
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
            "Install with: pip install 'voogle[image]' or pip install pytesseract"
        ) from e


def _get_transformers() -> tuple[Any, Any]:
    """Lazy import of transformers CLIP components.

    Returns:
        Tuple of (CLIPProcessor, CLIPModel) classes.

    Raises:
        ImportError: If transformers is not installed.
    """
    try:
        from transformers import CLIPModel, CLIPProcessor
        return CLIPProcessor, CLIPModel
    except ImportError as e:
        raise ImportError(
            "transformers is required for CLIP/SigLIP embeddings. "
            "Install with: pip install 'voogle[image]' or pip install transformers"
        ) from e


@functools.cache
def _get_clip_model(
    model_name: str = DEFAULT_MODEL,
    device: str = DEFAULT_DEVICE,
) -> tuple[Any, Any]:
    """Get or create a cached CLIP model and processor instance.

    Args:
        model_name: CLIP/SigLIP model to load.
        device: Device to run inference on.

    Returns:
        Tuple of (processor, model) instances.
    """
    CLIPProcessor, CLIPModel = _get_transformers()

    logger.info(
        "Loading CLIP model: %s (device=%s)",
        model_name,
        device,
    )
    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name)

    if device != "cpu":
        model = model.to(device)

    return processor, model


def _is_image_url(url: str) -> bool:
    """Check if the URL appears to be an image URL.

    Args:
        url: URL to check.

    Returns:
        True if the URL appears to be an image URL.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path_lower = parsed.path.lower()

    for ext in IMAGE_EXTENSIONS:
        if path_lower.endswith(ext):
            return True

    return False


class ImageAdapter(ContentAdapter):
    """Content adapter for image files with CLIP/SigLIP embeddings and optional OCR.

    Supports JPEG, PNG, WebP, and GIF formats. Provides:
    - Image preprocessing and normalization
    - CLIP/SigLIP embedding generation for semantic search
    - Optional OCR text extraction
    - EXIF metadata extraction
    - Thumbnail generation
    - ImageRegionLocation for region-based deep linking

    Example:
        >>> adapter = ImageAdapter()
        >>> source = ContentSource(
        ...     source_id="image-123",
        ...     source_type=ContentType.DOCUMENT,
        ...     path=Path("/data/photo.jpg"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: ImageConfig | None = None) -> None:
        """Initialize the image adapter.

        Args:
            config: Image processing configuration. Uses defaults if not provided.
        """
        self._config = config or ImageConfig()

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.DOCUMENT (for images).
        """
        return frozenset({ContentType.DOCUMENT})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is an image with a supported file extension.
        """
        if source.source_type != ContentType.DOCUMENT:
            return False

        # Check file extension if path is available
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in IMAGE_EXTENSIONS

        # Check URL for image extension
        if source.url is not None:
            if _is_image_url(source.url):
                return True

            # Check MIME type in metadata as fallback
            mime_type = source.metadata.get("mime_type", "")
            return mime_type.startswith("image/")

        return False

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract content from an image.

        Extracts text via OCR (if enabled), EXIF metadata, and generates
        descriptive content for semantic search.

        Args:
            source: The image source to process.

        Yields:
            RawChunk instances with extracted text and metadata.

        Raises:
            ValueError: If the source is not supported or file not found.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        image_path = self._resolve_image_path(source)

        logger.info("Starting image processing of %s", image_path)

        PIL_Image = _get_pil()
        image = PIL_Image.open(image_path)

        try:
            # Preprocess image if configured
            if self._config.preprocess_resize:
                image = self._preprocess_image(image)

            # Extract EXIF metadata
            if self._config.extract_exif:
                exif_chunk = self._extract_exif(image, source)
                if exif_chunk:
                    yield exif_chunk

            # Extract OCR text
            if self._config.enable_ocr:
                async for chunk in self._extract_ocr(image, source):
                    yield chunk

            # Generate thumbnail if enabled
            if self._config.generate_thumbnail:
                self._generate_thumbnail(image, source)

            # Generate image description/embedding text
            description_chunk = await self._generate_description(image, source)
            if description_chunk:
                yield description_chunk

            logger.info("Completed image processing of %s", image_path)

        finally:
            image.close()

    def _resolve_image_path(self, source: ContentSource) -> Path:
        """Resolve the image file path.

        Args:
            source: The content source.

        Returns:
            Path to the local image file.

        Raises:
            ValueError: If the image cannot be resolved.
        """
        if source.path is not None:
            if not source.path.exists():
                raise ValueError(f"Image file not found: {source.path}")
            return source.path

        if source.url is None:
            raise ValueError(f"Image source {source.source_id} requires a path or URL")

        raise ValueError(
            f"Image source {source.source_id} requires a local file path "
            "(remote URLs not yet supported)"
        )

    def _preprocess_image(self, image: "PILImage.Image") -> "PILImage.Image":
        """Preprocess image for analysis.

        Args:
            image: PIL Image object.

        Returns:
            Preprocessed PIL Image.
        """
        if self._config.preprocess_resize:
            # Use LANCZOS for high-quality downscaling
            PIL_Image = _get_pil()
            image = image.resize(
                self._config.preprocess_resize,
                PIL_Image.Resampling.LANCZOS,
            )

        # Convert to RGB if necessary (for CLIP compatibility)
        if image.mode != "RGB":
            image = image.convert("RGB")

        return image

    def _extract_exif(
        self,
        image: "PILImage.Image",
        source: ContentSource,
    ) -> RawChunk | None:
        """Extract EXIF metadata from image.

        Args:
            image: PIL Image object.
            source: The content source.

        Returns:
            RawChunk with EXIF metadata, or None if no metadata found.
        """
        try:
            exif_data = image.getexif()
            if not exif_data:
                return None

            # Map EXIF tag IDs to human-readable names
            from PIL.ExifTags import TAGS

            exif_dict: dict[str, Any] = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                # Skip binary data
                if isinstance(value, bytes):
                    continue
                exif_dict[tag_name] = str(value)

            if not exif_dict:
                return None

            # Create searchable text from EXIF data
            text_parts = []
            important_fields = [
                "DateTime",
                "DateTimeOriginal",
                "Make",
                "Model",
                "ImageDescription",
                "Artist",
                "Copyright",
                "GPSInfo",
            ]
            for field in important_fields:
                if field in exif_dict:
                    text_parts.append(f"{field}: {exif_dict[field]}")

            if not text_parts:
                return None

            text = " | ".join(text_parts)

            # Full image location (entire image)
            location = ImageRegionLocation(
                x=0.0,
                y=0.0,
                width=100.0,
                height=100.0,
            )

            return RawChunk(
                text=text,
                location=location,
                metadata={
                    "chunk_type": "exif",
                    "exif_data": exif_dict,
                },
            )

        except Exception as e:
            logger.warning("Failed to extract EXIF from %s: %s", source.source_id, e)
            return None

    async def _extract_ocr(
        self,
        image: "PILImage.Image",
        source: ContentSource,
    ) -> AsyncIterator[RawChunk]:
        """Extract text from image using OCR.

        Args:
            image: PIL Image object.
            source: The content source.

        Yields:
            RawChunk instances with OCR-extracted text.
        """
        try:
            pytesseract = _get_pytesseract()

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Get OCR text with bounding boxes
            ocr_data = pytesseract.image_to_data(
                image,
                lang=self._config.ocr_language,
                output_type=pytesseract.Output.DICT,
            )

            # Group words into lines/blocks
            image_width, image_height = image.size
            current_text: list[str] = []
            current_block = -1
            block_boxes: list[tuple[int, int, int, int]] = []

            n_boxes = len(ocr_data["text"])
            for i in range(n_boxes):
                text = ocr_data["text"][i].strip()
                conf = int(ocr_data["conf"][i])
                block_num = ocr_data["block_num"][i]

                # Skip low confidence or empty text
                if conf < 30 or not text:
                    continue

                # If we're in a new block, yield the previous one
                if block_num != current_block and current_text:
                    yield self._create_ocr_chunk(
                        current_text, block_boxes, image_width, image_height
                    )
                    current_text = []
                    block_boxes = []

                current_block = block_num
                current_text.append(text)
                block_boxes.append((
                    ocr_data["left"][i],
                    ocr_data["top"][i],
                    ocr_data["width"][i],
                    ocr_data["height"][i],
                ))

            # Yield final block
            if current_text:
                yield self._create_ocr_chunk(
                    current_text, block_boxes, image_width, image_height
                )

        except Exception as e:
            logger.warning("OCR failed for %s: %s", source.source_id, e)

    def _create_ocr_chunk(
        self,
        words: list[str],
        boxes: list[tuple[int, int, int, int]],
        image_width: int,
        image_height: int,
    ) -> RawChunk:
        """Create a RawChunk from OCR data.

        Args:
            words: List of extracted words.
            boxes: List of bounding boxes (x, y, width, height) in pixels.
            image_width: Image width in pixels.
            image_height: Image height in pixels.

        Returns:
            RawChunk with OCR text and region location.
        """
        text = " ".join(words)

        # Calculate bounding box that contains all word boxes
        if boxes:
            min_x = min(b[0] for b in boxes)
            min_y = min(b[1] for b in boxes)
            max_x = max(b[0] + b[2] for b in boxes)
            max_y = max(b[1] + b[3] for b in boxes)

            # Convert to percentages
            x_pct = (min_x / image_width) * 100
            y_pct = (min_y / image_height) * 100
            width_pct = ((max_x - min_x) / image_width) * 100
            height_pct = ((max_y - min_y) / image_height) * 100

            location = ImageRegionLocation(
                x=x_pct,
                y=y_pct,
                width=width_pct,
                height=height_pct,
            )
        else:
            location = ImageRegionLocation(
                x=0.0, y=0.0, width=100.0, height=100.0
            )

        return RawChunk(
            text=text,
            location=location,
            metadata={"chunk_type": "ocr"},
        )

    def _generate_thumbnail(
        self,
        image: "PILImage.Image",
        source: ContentSource,
    ) -> Path | None:
        """Generate a thumbnail for the image.

        Args:
            image: PIL Image object.
            source: The content source.

        Returns:
            Path to the generated thumbnail, or None if failed.
        """
        try:
            thumbnail_dir = self._config.thumbnail_dir or Path(tempfile.gettempdir())
            thumbnail_dir.mkdir(parents=True, exist_ok=True)

            hash_suffix = hashlib.md5(source.source_id.encode()).hexdigest()[:8]
            thumbnail_name = f"thumb_{hash_suffix}.jpg"
            thumbnail_path = thumbnail_dir / thumbnail_name

            # Create thumbnail (modifies image in-place, so we copy)
            thumb = image.copy()
            thumb.thumbnail(self._config.thumbnail_size)

            # Convert to RGB for JPEG
            if thumb.mode != "RGB":
                thumb = thumb.convert("RGB")

            thumb.save(thumbnail_path, "JPEG", quality=85)
            logger.debug("Generated thumbnail: %s", thumbnail_path)

            return thumbnail_path

        except Exception as e:
            logger.warning("Thumbnail generation failed for %s: %s", source.source_id, e)
            return None

    async def _generate_description(
        self,
        image: "PILImage.Image",
        source: ContentSource,
    ) -> RawChunk | None:
        """Generate a text description for semantic search.

        For CLIP-based search, we generate a simple description based on
        image properties. The actual CLIP embedding is generated separately
        during indexing.

        Args:
            image: PIL Image object.
            source: The content source.

        Returns:
            RawChunk with image description.
        """
        # Build description from image properties
        parts = []

        # Image dimensions
        width, height = image.size
        if width > height:
            orientation = "landscape"
        elif height > width:
            orientation = "portrait"
        else:
            orientation = "square"
        parts.append(f"{orientation} image")

        # Image mode/type
        if image.mode == "RGBA":
            parts.append("with transparency")
        elif image.mode == "L":
            parts.append("grayscale")

        # Image format
        if image.format:
            parts.append(f"{image.format} format")

        # Resolution info
        parts.append(f"{width}x{height} pixels")

        # Check for animation (GIF)
        try:
            n_frames = getattr(image, "n_frames", 1)
            if n_frames > 1:
                parts.append(f"animated with {n_frames} frames")
        except Exception:
            pass

        text = " ".join(parts)

        # Full image location
        location = ImageRegionLocation(
            x=0.0,
            y=0.0,
            width=100.0,
            height=100.0,
        )

        return RawChunk(
            text=text,
            location=location,
            metadata={
                "chunk_type": "description",
                "width": width,
                "height": height,
                "mode": image.mode,
                "format": image.format,
            },
        )

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw image chunks into text chunks for embedding.

        For images, each RawChunk typically becomes a single TextChunk
        since image content is usually not divisible like text.

        Args:
            raw_chunks: List of RawChunk instances from extraction.
            source: The source these chunks came from.
            config: Chunking configuration. Uses defaults if not provided.

        Returns:
            List of TextChunk instances ready for embedding.
        """
        if not raw_chunks:
            return []

        text_chunks: list[TextChunk] = []

        for i, raw_chunk in enumerate(raw_chunks):
            # Normalize text
            text = self._normalize_text(raw_chunk.text)
            if not text:
                continue

            text_chunks.append(
                TextChunk(
                    text=text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=raw_chunk.location,
                    sequence_index=i,
                    metadata=dict(raw_chunk.metadata),
                )
            )

        return text_chunks

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

    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            ImageRegionLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a URL with IIIF-style region parameters for navigating
        directly to a specific region in an image viewer.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the image content.

        Returns:
            URL with region parameters for navigation, or None if
            no location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
