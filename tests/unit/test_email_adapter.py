# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for EmailAdapter content adapter."""
from pathlib import Path
from email.message import EmailMessage

import pytest

from voogle.adapters.email import (
    EMAIL_EXTENSIONS,
    EmailAdapter,
    EmailConfig,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import EmailThreadLocation

pytestmark = pytest.mark.unit


class TestEmailAdapterInit:
    """Tests for EmailAdapter initialization."""

    @pytest.mark.description("EmailAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = EmailAdapter()
        assert adapter._config.extract_html is True
        assert adapter._config.extract_attachments is True
        assert adapter._config.include_headers is True
        assert adapter._config.reconstruct_threads is True
        assert adapter._config.header_fields == ("From", "To", "Subject", "Date")

    @pytest.mark.description("EmailAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = EmailConfig(
            extract_html=False,
            extract_attachments=False,
            include_headers=False,
            reconstruct_threads=False,
            header_fields=("From", "Subject"),
        )
        adapter = EmailAdapter(config=config)
        assert adapter._config.extract_html is False
        assert adapter._config.extract_attachments is False
        assert adapter._config.include_headers is False
        assert adapter._config.reconstruct_threads is False
        assert adapter._config.header_fields == ("From", "Subject")


class TestEmailAdapterSupportedTypes:
    """Tests for EmailAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns EMAIL only")
    def test_supported_types(self) -> None:
        adapter = EmailAdapter()
        assert adapter.supported_types == frozenset({ContentType.EMAIL})


class TestEmailAdapterSupports:
    """Tests for EmailAdapter.supports method."""

    @pytest.mark.description("supports returns True for EML files")
    def test_supports_eml(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.eml"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for MBOX files")
    def test_supports_mbox(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/mailbox.mbox"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for uppercase extensions")
    def test_supports_uppercase_extension(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.EML"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-email content type")
    def test_rejects_non_email_type(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for non-email file")
    def test_rejects_non_email_file(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/document.pdf"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports works with URL sources")
    def test_supports_url_source(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            url="https://example.com/message.eml",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for message/rfc822 MIME type")
    def test_supports_rfc822_mime_type(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            url="https://example.com/download",
            metadata={"mime_type": "message/rfc822"},
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for application/mbox MIME type")
    def test_supports_mbox_mime_type(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            url="https://example.com/download",
            metadata={"mime_type": "application/mbox"},
        )
        assert adapter.supports(source) is True


class TestEmailAdapterExtract:
    """Tests for EmailAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for URL-only source")
    @pytest.mark.asyncio
    async def test_extract_url_only_raises(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            url="https://example.com/message.eml",
        )
        with pytest.raises(ValueError, match="requires a local file path"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/nonexistent/message.eml"),
        )
        with pytest.raises(ValueError, match="Email file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks from EML file")
    @pytest.mark.asyncio
    async def test_extract_eml_yields_chunks(self, tmp_path: Path) -> None:
        # Create a simple EML file
        eml_file = tmp_path / "test.eml"
        eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <test123@example.com>
Content-Type: text/plain; charset="utf-8"

Hello, this is a test email body.
"""
        eml_file.write_bytes(eml_content)

        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=eml_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        assert "test email body" in chunks[0].text.lower()
        assert isinstance(chunks[0].location, EmailThreadLocation)
        assert "test123@example.com" in chunks[0].location.message_id

    @pytest.mark.description("extract includes configured headers")
    @pytest.mark.asyncio
    async def test_extract_includes_headers(self, tmp_path: Path) -> None:
        eml_file = tmp_path / "test.eml"
        eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: Important Message
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <msg1@example.com>
Content-Type: text/plain; charset="utf-8"

Body text here.
"""
        eml_file.write_bytes(eml_content)

        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=eml_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        text = chunks[0].text
        assert "From:" in text
        assert "sender@example.com" in text
        assert "Subject:" in text
        assert "Important Message" in text

    @pytest.mark.description("extract without headers when disabled")
    @pytest.mark.asyncio
    async def test_extract_without_headers(self, tmp_path: Path) -> None:
        eml_file = tmp_path / "test.eml"
        eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Message-ID: <msg1@example.com>
Content-Type: text/plain; charset="utf-8"

Body text only.
"""
        eml_file.write_bytes(eml_content)

        config = EmailConfig(include_headers=False)
        adapter = EmailAdapter(config=config)
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=eml_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        text = chunks[0].text
        assert "From:" not in text
        assert "Body text only" in text


class TestEmailAdapterMbox:
    """Tests for MBOX file extraction."""

    @pytest.mark.description("extract yields multiple chunks from MBOX")
    @pytest.mark.asyncio
    async def test_extract_mbox_multiple_messages(self, tmp_path: Path) -> None:
        mbox_file = tmp_path / "test.mbox"
        mbox_content = b"""From sender@example.com Mon Jan  1 12:00:00 2024
From: sender@example.com
To: recipient@example.com
Subject: First Message
Message-ID: <first@example.com>
Content-Type: text/plain; charset="utf-8"

First message body.

From other@example.com Mon Jan  2 12:00:00 2024
From: other@example.com
To: recipient@example.com
Subject: Second Message
Message-ID: <second@example.com>
Content-Type: text/plain; charset="utf-8"

Second message body.

"""
        mbox_file.write_bytes(mbox_content)

        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=mbox_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 2
        texts = [c.text.lower() for c in chunks]
        assert any("first message" in t for t in texts)
        assert any("second message" in t for t in texts)


class TestEmailAdapterThreadReconstruction:
    """Tests for email thread reconstruction."""

    @pytest.mark.description("extract reconstructs threads from References")
    @pytest.mark.asyncio
    async def test_thread_reconstruction(self, tmp_path: Path) -> None:
        mbox_file = tmp_path / "thread.mbox"
        mbox_content = b"""From sender@example.com Mon Jan  1 12:00:00 2024
From: sender@example.com
To: recipient@example.com
Subject: Original Thread
Message-ID: <original@example.com>
Date: Mon, 1 Jan 2024 12:00:00 +0000
Content-Type: text/plain; charset="utf-8"

Original message.

From recipient@example.com Mon Jan  2 12:00:00 2024
From: recipient@example.com
To: sender@example.com
Subject: Re: Original Thread
Message-ID: <reply@example.com>
References: <original@example.com>
In-Reply-To: <original@example.com>
Date: Tue, 2 Jan 2024 12:00:00 +0000
Content-Type: text/plain; charset="utf-8"

Reply message.

"""
        mbox_file.write_bytes(mbox_content)

        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=mbox_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 2

        # Both should be in the same thread
        thread_ids = {c.location.thread_id for c in chunks if isinstance(c.location, EmailThreadLocation)}
        assert len(thread_ids) == 1

        # Check positions
        positions = {c.location.thread_position for c in chunks if isinstance(c.location, EmailThreadLocation)}
        assert positions == {1, 2}


class TestEmailAdapterHtmlExtraction:
    """Tests for HTML body extraction."""

    @pytest.mark.description("extract converts HTML to plain text")
    @pytest.mark.asyncio
    async def test_extract_html_body(self, tmp_path: Path) -> None:
        eml_file = tmp_path / "html.eml"
        eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: HTML Email
Message-ID: <html@example.com>
Content-Type: text/html; charset="utf-8"

<html><body><p>Hello <b>world</b>!</p><script>alert('bad')</script></body></html>
"""
        eml_file.write_bytes(eml_content)

        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=eml_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        text = chunks[0].text.lower()
        assert "hello" in text
        assert "world" in text
        assert "<script>" not in text
        assert "alert" not in text


class TestEmailAdapterChunk:
    """Tests for EmailAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.eml"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines words into target-sized chunks")
    def test_chunk_combines_words(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.eml"),
        )

        # Create raw chunks with more than target words
        words = "one two three four five six seven eight nine ten " * 5  # 50 words
        raw_chunks = [
            RawChunk(
                text=words,
                location=EmailThreadLocation(message_id="<test@example.com>"),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert all(chunk.source_id == "test" for chunk in result)
        assert all(chunk.source_type == ContentType.EMAIL for chunk in result)

    @pytest.mark.description("chunk preserves email locations from raw chunks")
    def test_chunk_preserves_locations(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.eml"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=EmailThreadLocation(
                    message_id="<specific@example.com>",
                    thread_id="abc123",
                    thread_position=3,
                ),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert result[0].location is not None
        assert isinstance(result[0].location, EmailThreadLocation)
        assert result[0].location.message_id == "<specific@example.com>"
        assert result[0].location.thread_position == 3

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = EmailAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.EMAIL,
            path=Path("/data/message.eml"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 100,
                location=EmailThreadLocation(message_id="<test@example.com>"),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestEmailAdapterGetLocation:
    """Tests for EmailAdapter.get_location method."""

    @pytest.mark.description("get_location returns chunk location")
    def test_get_location_returns_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = EmailAdapter()
        location = EmailThreadLocation(
            message_id="<test@example.com>",
            thread_id="abc123",
            thread_position=2,
        )
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.EMAIL,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = EmailAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.EMAIL,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestEmailAdapterGetDeepLink:
    """Tests for EmailAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates message-id URL")
    def test_get_deep_link_with_message_id(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = EmailAdapter()
        location = EmailThreadLocation(
            message_id="<test123@example.com>",
            thread_id="abc123",
        )
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.EMAIL,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://mail.example.com/archive")
        assert result is not None
        assert "message-id=test123@example.com" in result
        assert "thread=abc123" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = EmailAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.EMAIL,
        )

        result = adapter.get_deep_link(chunk, "https://mail.example.com/archive")
        assert result is None


class TestEmailConfig:
    """Tests for EmailConfig dataclass."""

    @pytest.mark.description("EmailConfig has correct defaults")
    def test_default_values(self) -> None:
        config = EmailConfig()
        assert config.extract_html is True
        assert config.extract_attachments is True
        assert config.include_headers is True
        assert config.reconstruct_threads is True
        assert config.header_fields == ("From", "To", "Subject", "Date")

    @pytest.mark.description("EmailConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = EmailConfig(
            extract_html=False,
            extract_attachments=False,
            include_headers=False,
            reconstruct_threads=False,
            header_fields=("From", "Subject", "X-Custom"),
        )
        assert config.extract_html is False
        assert config.extract_attachments is False
        assert config.include_headers is False
        assert config.reconstruct_threads is False
        assert config.header_fields == ("From", "Subject", "X-Custom")


class TestEmailExtensions:
    """Tests for EMAIL_EXTENSIONS constant."""

    @pytest.mark.description("EMAIL_EXTENSIONS contains .eml")
    def test_contains_eml(self) -> None:
        assert ".eml" in EMAIL_EXTENSIONS

    @pytest.mark.description("EMAIL_EXTENSIONS contains .mbox")
    def test_contains_mbox(self) -> None:
        assert ".mbox" in EMAIL_EXTENSIONS

    @pytest.mark.description("EMAIL_EXTENSIONS is frozen")
    def test_is_frozen(self) -> None:
        assert isinstance(EMAIL_EXTENSIONS, frozenset)


class TestEmailThreadLocation:
    """Tests for EmailThreadLocation dataclass."""

    @pytest.mark.description("EmailThreadLocation validates message_id")
    def test_requires_message_id(self) -> None:
        with pytest.raises(ValueError, match="message_id must not be empty"):
            EmailThreadLocation(message_id="")

    @pytest.mark.description("EmailThreadLocation validates thread_position")
    def test_validates_thread_position(self) -> None:
        with pytest.raises(ValueError, match="thread_position must be >= 1"):
            EmailThreadLocation(message_id="<test@example.com>", thread_position=0)

    @pytest.mark.description("EmailThreadLocation validates total_in_thread")
    def test_validates_total_in_thread(self) -> None:
        with pytest.raises(ValueError, match="total_in_thread must be >= 1"):
            EmailThreadLocation(
                message_id="<test@example.com>",
                total_in_thread=0,
            )

    @pytest.mark.description("EmailThreadLocation validates position <= total")
    def test_validates_position_less_than_total(self) -> None:
        with pytest.raises(ValueError, match="thread_position cannot exceed"):
            EmailThreadLocation(
                message_id="<test@example.com>",
                thread_position=5,
                total_in_thread=3,
            )

    @pytest.mark.description("EmailThreadLocation generates deep link")
    def test_to_deep_link(self) -> None:
        location = EmailThreadLocation(
            message_id="<test@example.com>",
            thread_id="abc123",
        )
        link = location.to_deep_link("https://mail.example.com")
        assert "message-id=test@example.com" in link
        assert "thread=abc123" in link
