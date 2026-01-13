# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for ImageAdapter content adapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.image import (
    IMAGE_EXTENSIONS,
    ImageAdapter,
    ImageConfig,
    _is_image_url,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import ImageRegionLocation

pytestmark = pytest.mark.unit


class TestImageAdapterInit:
    """Tests for ImageAdapter initialization."""

    @pytest.mark.description("ImageAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = ImageAdapter()
        assert adapter._config.model_name == "openai/clip-vit-base-patch32"
        assert adapter._config.device == "cpu"
        assert adapter._config.enable_ocr is False
        assert adapter._config.extract_exif is True
        assert adapter._config.generate_thumbnail is False

    @pytest.mark.description("ImageAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = ImageConfig(
            model_name="openai/clip-vit-large-patch14",
            device="cuda",
            enable_ocr=True,
            ocr_language="deu",
            extract_exif=False,
            generate_thumbnail=True,
            thumbnail_size=(512, 512),
        )
        adapter = ImageAdapter(config=config)
        assert adapter._config.model_name == "openai/clip-vit-large-patch14"
        assert adapter._config.device == "cuda"
        assert adapter._config.enable_ocr is True
        assert adapter._config.ocr_language == "deu"
        assert adapter._config.extract_exif is False
        assert adapter._config.generate_thumbnail is True


class TestImageAdapterSupportedTypes:
    """Tests for ImageAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns DOCUMENT only")
    def test_supported_types(self) -> None:
        adapter = ImageAdapter()
        assert adapter.supported_types == frozenset({ContentType.DOCUMENT})


class TestImageAdapterSupports:
    """Tests for ImageAdapter.supports method."""

    @pytest.mark.description("supports returns True for JPEG files")
    def test_supports_jpeg(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpg"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for JPEG files with .jpeg extension")
    def test_supports_jpeg_ext(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpeg"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for PNG files")
    def test_supports_png(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.png"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for WebP files")
    def test_supports_webp(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.webp"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for GIF files")
    def test_supports_gif(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.gif"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-document content type")
    def test_rejects_non_document_type(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for unsupported extension")
    def test_rejects_unsupported_extension(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.bmp"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports works with URL sources")
    def test_supports_url_source(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/image.png",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for image MIME type")
    def test_supports_mime_type(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/image",
            metadata={"mime_type": "image/png"},
        )
        assert adapter.supports(source) is True


class TestImageAdapterExtract:
    """Tests for ImageAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/nonexistent/image.jpg"),
        )
        with pytest.raises(ValueError, match="Image file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks with image description")
    @pytest.mark.asyncio
    async def test_extract_yields_description(self, tmp_path: Path) -> None:
        # Create a mock image file
        image_file = tmp_path / "test.jpg"

        # Create mock PIL Image
        mock_image = MagicMock()
        mock_image.size = (800, 600)
        mock_image.mode = "RGB"
        mock_image.format = "JPEG"
        mock_image._getexif.return_value = None

        mock_pil = MagicMock()
        mock_pil.open.return_value.__enter__ = MagicMock(return_value=mock_image)
        mock_pil.open.return_value.__exit__ = MagicMock(return_value=False)
        mock_pil.open.return_value = mock_image

        # Disable features that require real image
        config = ImageConfig(extract_exif=False, enable_ocr=False)
        adapter = ImageAdapter(config=config)

        # Create a minimal valid image
        image_file.write_bytes(b'\xff\xd8\xff\xe0')  # Minimal JPEG header

        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=image_file,
        )

        with patch("voogle.adapters.image._get_pil", return_value=mock_pil):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) >= 1
        # Find description chunk
        desc_chunks = [c for c in chunks if c.metadata.get("chunk_type") == "description"]
        assert len(desc_chunks) == 1
        assert "landscape" in desc_chunks[0].text.lower()
        assert isinstance(desc_chunks[0].location, ImageRegionLocation)

    @pytest.mark.description("extract extracts EXIF metadata when enabled")
    @pytest.mark.asyncio
    async def test_extract_exif(self, tmp_path: Path) -> None:
        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b'\xff\xd8\xff\xe0')

        # Create a mock Exif object that behaves like PIL's Exif
        mock_exif = MagicMock()
        mock_exif.items.return_value = [
            (271, "Canon"),  # Make
            (272, "Canon EOS 5D"),  # Model
            (306, "2024:01:15 10:30:00"),  # DateTime
        ]
        mock_exif.__bool__ = lambda self: True

        mock_image = MagicMock()
        mock_image.size = (800, 600)
        mock_image.mode = "RGB"
        mock_image.format = "JPEG"
        mock_image.getexif.return_value = mock_exif

        mock_pil = MagicMock()
        mock_pil.open.return_value = mock_image

        config = ImageConfig(extract_exif=True, enable_ocr=False)
        adapter = ImageAdapter(config=config)
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=image_file,
        )

        with patch("voogle.adapters.image._get_pil", return_value=mock_pil):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        # Should have at least description chunk
        assert isinstance(chunks, list)
        assert len(chunks) >= 1


class TestImageAdapterChunk:
    """Tests for ImageAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpg"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk converts RawChunks to TextChunks")
    def test_chunk_converts_raw_chunks(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpg"),
        )

        raw_chunks = [
            RawChunk(
                text="Image description text",
                location=ImageRegionLocation(x=0, y=0, width=100, height=100),
                metadata={"chunk_type": "description"},
            )
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) == 1
        assert result[0].text == "Image description text"
        assert result[0].source_id == "test"
        assert result[0].source_type == ContentType.DOCUMENT
        assert isinstance(result[0].location, ImageRegionLocation)

    @pytest.mark.description("chunk assigns sequential indices")
    def test_chunk_sequence_indices(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpg"),
        )

        raw_chunks = [
            RawChunk(
                text="First chunk",
                location=ImageRegionLocation(x=0, y=0, width=50, height=50),
                metadata={"chunk_type": "ocr"},
            ),
            RawChunk(
                text="Second chunk",
                location=ImageRegionLocation(x=50, y=50, width=50, height=50),
                metadata={"chunk_type": "ocr"},
            ),
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) == 2
        assert result[0].sequence_index == 0
        assert result[1].sequence_index == 1

    @pytest.mark.description("chunk skips empty text chunks")
    def test_chunk_skips_empty(self) -> None:
        adapter = ImageAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/image.jpg"),
        )

        raw_chunks = [
            RawChunk(
                text="Valid text",
                location=ImageRegionLocation(x=0, y=0, width=100, height=100),
                metadata={"chunk_type": "description"},
            ),
            RawChunk(
                text="   ",  # Whitespace only
                location=ImageRegionLocation(x=0, y=0, width=100, height=100),
                metadata={"chunk_type": "ocr"},
            ),
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) == 1
        assert result[0].text == "Valid text"


class TestImageAdapterGetLocation:
    """Tests for ImageAdapter.get_location method."""

    @pytest.mark.description("get_location returns ImageRegionLocation")
    def test_get_location_returns_region(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = ImageAdapter()
        location = ImageRegionLocation(x=10, y=20, width=30, height=40)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = ImageAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestImageAdapterGetDeepLink:
    """Tests for ImageAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates IIIF-style URL")
    def test_get_deep_link_with_region(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = ImageAdapter()
        location = ImageRegionLocation(x=10.5, y=20.5, width=30.0, height=40.0)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/image.jpg")
        assert result is not None
        assert "xywh=percent:" in result
        assert "10.5" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = ImageAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/image.jpg")
        assert result is None


class TestImageConfig:
    """Tests for ImageConfig dataclass."""

    @pytest.mark.description("ImageConfig has correct defaults")
    def test_default_values(self) -> None:
        config = ImageConfig()
        assert config.model_name == "openai/clip-vit-base-patch32"
        assert config.device == "cpu"
        assert config.enable_ocr is False
        assert config.ocr_language == "eng"
        assert config.extract_exif is True
        assert config.generate_thumbnail is False
        assert config.thumbnail_size == (256, 256)
        assert config.thumbnail_dir is None
        assert config.preprocess_resize is None
        assert config.extract_regions is False
        assert config.region_min_area == 5.0

    @pytest.mark.description("ImageConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = ImageConfig(
            model_name="openai/clip-vit-large-patch14",
            device="cuda",
            enable_ocr=True,
            ocr_language="fra",
            extract_exif=False,
            generate_thumbnail=True,
            thumbnail_size=(512, 512),
            thumbnail_dir=Path("/thumbnails"),
            preprocess_resize=(224, 224),
            extract_regions=True,
            region_min_area=10.0,
        )
        assert config.model_name == "openai/clip-vit-large-patch14"
        assert config.device == "cuda"
        assert config.enable_ocr is True
        assert config.ocr_language == "fra"
        assert config.extract_exif is False
        assert config.generate_thumbnail is True
        assert config.thumbnail_size == (512, 512)
        assert config.thumbnail_dir == Path("/thumbnails")
        assert config.preprocess_resize == (224, 224)
        assert config.extract_regions is True
        assert config.region_min_area == 10.0


class TestImageExtensions:
    """Tests for IMAGE_EXTENSIONS constant."""

    @pytest.mark.description("IMAGE_EXTENSIONS contains required formats")
    def test_required_formats(self) -> None:
        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".jpeg" in IMAGE_EXTENSIONS
        assert ".png" in IMAGE_EXTENSIONS
        assert ".webp" in IMAGE_EXTENSIONS
        assert ".gif" in IMAGE_EXTENSIONS

    @pytest.mark.description("IMAGE_EXTENSIONS is frozen")
    def test_is_frozen(self) -> None:
        assert isinstance(IMAGE_EXTENSIONS, frozenset)


class TestImageUrlDetection:
    """Tests for _is_image_url helper function."""

    @pytest.mark.description("detects JPEG URLs")
    def test_jpeg_url(self) -> None:
        assert _is_image_url("https://example.com/photo.jpg") is True
        assert _is_image_url("https://example.com/photo.jpeg") is True

    @pytest.mark.description("detects PNG URLs")
    def test_png_url(self) -> None:
        assert _is_image_url("https://example.com/image.png") is True

    @pytest.mark.description("detects WebP URLs")
    def test_webp_url(self) -> None:
        assert _is_image_url("https://example.com/image.webp") is True

    @pytest.mark.description("detects GIF URLs")
    def test_gif_url(self) -> None:
        assert _is_image_url("https://example.com/animation.gif") is True

    @pytest.mark.description("rejects non-image URLs")
    def test_non_image_url(self) -> None:
        assert _is_image_url("https://example.com/video.mp4") is False
        assert _is_image_url("https://example.com/document.pdf") is False
        assert _is_image_url("https://example.com/page.html") is False
