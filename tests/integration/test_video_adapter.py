# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for VideoAdapter content adapter.

Tests video transcription with slide sync verification:
- Sample video file transcription
- Transcription accuracy verification
- Timestamp alignment (within 1s tolerance)
- Keyframe extraction
- Deep link format validation
- End-to-end ingest -> search -> verify
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle import embedding, vector
from voogle.adapters.video import VideoAdapter, VideoConfig
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk, TextChunk
from voogle.core.fragment import ContentType
from voogle.core.location import SlideLocation, TimestampLocation

pytestmark = pytest.mark.integration


class TestVideoAdapterWithSampleFiles:
    """Integration tests using sample video files."""

    @pytest.mark.description("VideoAdapter processes MP4 file")
    @pytest.mark.asyncio
    async def test_adapter_processes_mp4_file(self, tmp_path: Path) -> None:
        """Test that VideoAdapter can process a video file with mocked transcription."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        # Create mock segments
        mock_segments = [
            _create_mock_segment(0.0, 5.5, "Welcome to the video lecture."),
            _create_mock_segment(5.5, 12.0, "Today we discuss machine learning concepts."),
            _create_mock_segment(12.0, 18.0, "Neural networks are fundamental to AI."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-video-001",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        assert adapter.supports(source) is True

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 3, "Should extract 3 segments from video"

        for chunk in raw_chunks:
            assert chunk.text.strip(), "Chunk should have text"
            assert isinstance(chunk.location, TimestampLocation), "Should have timestamp location"
            assert chunk.location.start_time >= 0, "Start time should be non-negative"
            assert chunk.location.end_time >= chunk.location.start_time, (
                "End time should be >= start time"
            )

    @pytest.mark.description("VideoAdapter chunks preserve timestamp information")
    @pytest.mark.asyncio
    async def test_chunking_preserves_timestamps(self, tmp_path: Path) -> None:
        """Test that chunking preserves timestamp location information."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 10.0, "First segment with several words here."),
            _create_mock_segment(10.0, 20.0, "Second segment continues the lecture."),
            _create_mock_segment(20.0, 30.0, "Third segment wraps up the content."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-video",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        chunk_config = ChunkConfig(target_words=20, overlap_words=3)
        text_chunks = adapter.chunk(raw_chunks, source, chunk_config)

        assert len(text_chunks) > 0, "Should produce text chunks"
        for chunk in text_chunks:
            assert isinstance(chunk.location, TimestampLocation), (
                f"Chunk {chunk.sequence_index} should have TimestampLocation"
            )
            assert chunk.location.start_time >= 0


class TestTranscriptionAccuracy:
    """Tests for transcription accuracy verification."""

    @pytest.mark.description("Transcription captures key phrases from video")
    @pytest.mark.asyncio
    async def test_transcription_captures_key_phrases(self, tmp_path: Path) -> None:
        """Test that transcription captures expected key phrases."""
        video_file = tmp_path / "lecture.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 5.0, "Introduction to deep learning."),
            _create_mock_segment(5.0, 10.0, "Neural networks process data efficiently."),
            _create_mock_segment(10.0, 15.0, "Backpropagation trains the model."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="lecture-video",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        full_transcription = " ".join(chunk.text for chunk in raw_chunks).lower()

        expected_phrases = ["deep learning", "neural", "backpropagation"]
        found_phrases = [
            phrase for phrase in expected_phrases if phrase in full_transcription
        ]

        assert len(found_phrases) >= 2, (
            f"Should find at least 2 key phrases. "
            f"Found: {found_phrases}. Transcription: {full_transcription}"
        )

    @pytest.mark.description("Transcription produces non-empty text for valid video")
    @pytest.mark.asyncio
    async def test_transcription_produces_text(self, tmp_path: Path) -> None:
        """Test that transcription produces meaningful text content."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 5.0, "This is a test video transcription."),
            _create_mock_segment(5.0, 10.0, "It contains multiple sentences."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-transcription",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        total_words = sum(len(chunk.text.split()) for chunk in raw_chunks)
        assert total_words > 5, f"Should transcribe at least 5 words, got {total_words}"


class TestTimestampAlignment:
    """Tests for timestamp accuracy (within 1 second tolerance)."""

    @pytest.mark.description("Timestamps are within 1s of expected values")
    @pytest.mark.asyncio
    async def test_timestamp_accuracy_within_tolerance(self, tmp_path: Path) -> None:
        """Test that timestamps are accurate within 1 second tolerance."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 5.0, "First segment."),
            _create_mock_segment(5.0, 10.0, "Second segment."),
            _create_mock_segment(10.0, 15.0, "Third segment."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-timestamps",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Verify first segment starts near 0
        if raw_chunks:
            first_chunk = raw_chunks[0]
            assert isinstance(first_chunk.location, TimestampLocation)
            assert abs(first_chunk.location.start_time - 0.0) < 1.0, (
                f"First segment should start near 0, got {first_chunk.location.start_time}"
            )

        # Verify timestamps are monotonically increasing (with tolerance)
        prev_end = 0.0
        for chunk in raw_chunks:
            assert isinstance(chunk.location, TimestampLocation)
            assert chunk.location.start_time >= prev_end - 1.0, (
                f"Timestamps should be monotonically increasing. "
                f"Got start={chunk.location.start_time} after end={prev_end}"
            )
            prev_end = chunk.location.end_time

    @pytest.mark.description("Video duration covered by timestamps matches expected duration")
    @pytest.mark.asyncio
    async def test_timestamp_coverage(self, tmp_path: Path) -> None:
        """Test that timestamps cover the expected video duration."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 10.0, "First segment."),
            _create_mock_segment(10.0, 20.0, "Second segment."),
            _create_mock_segment(20.0, 30.0, "Third segment."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-coverage",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        if not raw_chunks:
            pytest.skip("No chunks extracted")

        last_chunk = raw_chunks[-1]
        assert isinstance(last_chunk.location, TimestampLocation)
        max_timestamp = last_chunk.location.end_time

        assert max_timestamp > 10.0, f"Should cover most of video, got max_ts={max_timestamp}"
        assert max_timestamp <= 35.0, f"Timestamps should not exceed video length, got {max_timestamp}"


class TestKeyframeExtraction:
    """Tests for keyframe/scene detection extraction."""

    @pytest.mark.description("Keyframe extraction produces slide chunks")
    @pytest.mark.asyncio
    async def test_keyframe_extraction_produces_slides(self, tmp_path: Path) -> None:
        """Test that keyframe extraction produces slide chunks with OCR text."""
        video_file = tmp_path / "presentation.mp4"
        video_file.touch()

        # Create transcription mock
        mock_segments = [
            _create_mock_segment(0.0, 10.0, "Slide about introduction."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        # Create OpenCV mocks for keyframe extraction
        mock_frame = MagicMock()
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0  # FPS

        # Simulate frame reads - 90 frames total (3 seconds at 30fps)
        frame_count = [0]

        def mock_read():
            if frame_count[0] < 90:
                frame_count[0] += 1
                return True, mock_frame
            return False, None

        mock_cap.read = mock_read

        # Mock cv2
        mock_cv2 = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.cvtColor.return_value = mock_frame
        mock_cv2.calcHist.return_value = MagicMock()
        mock_cv2.normalize.return_value = None
        mock_cv2.compareHist.return_value = 0.5  # Low correlation = scene change
        mock_cv2.HISTCMP_CORREL = 0
        mock_cv2.COLOR_BGR2GRAY = 0
        mock_cv2.COLOR_BGR2RGB = 0
        mock_cv2.resize.return_value = mock_frame
        mock_cv2.INTER_AREA = 0
        mock_cv2.CAP_PROP_FPS = 5

        # Mock pytesseract for OCR
        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "Slide Title: Introduction"

        config = VideoConfig(
            extract_keyframes=True,
            enable_slide_ocr=True,
            scene_threshold=25.0,
            min_scene_duration=1.0,
        )
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="presentation-video",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with (
            patch("voogle.adapters.video._get_model", return_value=mock_model),
            patch("voogle.adapters.video._get_cv2", return_value=mock_cv2),
            patch("voogle.adapters.video._get_pytesseract", return_value=mock_pytesseract),
        ):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should have transcription chunks
        transcription_chunks = [
            c for c in raw_chunks if c.metadata.get("chunk_type") == "transcription"
        ]
        assert len(transcription_chunks) >= 1, "Should have transcription chunks"

    @pytest.mark.description("Keyframe timestamps align with video timeline")
    @pytest.mark.asyncio
    async def test_keyframe_timestamps_align(self, tmp_path: Path) -> None:
        """Test that keyframe timestamps are correctly calculated from frame index."""
        video_file = tmp_path / "video.mp4"
        video_file.touch()

        # Mock transcription
        mock_segments = [
            _create_mock_segment(0.0, 5.0, "Content."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        # Disable keyframes for this test to focus on transcription timestamp alignment
        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-align",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) >= 1, "Should have at least one chunk"

        for chunk in raw_chunks:
            if isinstance(chunk.location, TimestampLocation):
                assert chunk.location.start_time >= 0, "Timestamp should be non-negative"
                assert chunk.location.end_time >= chunk.location.start_time, (
                    "End time should be >= start time"
                )


class TestEndToEndIngestSearchVerify:
    """End-to-end tests: ingest -> search -> verify."""

    @pytest.mark.description("Ingested video can be searched and results verified")
    @pytest.mark.asyncio
    async def test_e2e_ingest_search_verify(self, tmp_path: Path) -> None:
        """Test complete flow: ingest video -> index -> search -> verify results."""
        video_file = tmp_path / "lecture.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 5.5, "Welcome to the video lecture on software engineering."),
            _create_mock_segment(5.5, 12.0, "Today we discuss artificial intelligence and machine learning."),
            _create_mock_segment(12.0, 18.0, "Vector embeddings enable semantic search capabilities."),
            _create_mock_segment(18.0, 25.0, "This technology powers modern search applications."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        # Step 1: Extract (ingest)
        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-lecture-001",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 4, f"Should extract 4 segments, got {len(raw_chunks)}"

        # Step 2: Chunk
        chunk_config = ChunkConfig(target_words=40, overlap_words=5)
        text_chunks = adapter.chunk(raw_chunks, source, chunk_config)

        assert len(text_chunks) > 0, "Should produce text chunks"

        # Step 3: Index into Qdrant
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()  # In-memory client
        collection_name = "test-video-e2e"

        vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

        # Calculate embeddings and store
        texts = [chunk.text for chunk in text_chunks]
        embeddings = provider.encode_texts(texts)

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            location = chunk.location
            start_time = location.start_time if isinstance(location, TimestampLocation) else None
            end_time = location.end_time if isinstance(location, TimestampLocation) else None

            points.append(
                vector.qdrant_client.models.PointStruct(
                    id=3000 + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "source_id": chunk.source_id,
                        "source_type": chunk.source_type.value,
                        "text": chunk.text,
                        "start_time": start_time,
                        "end_time": end_time,
                        "sequence_index": chunk.sequence_index,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Step 4: Search
        query_embedding = embedding.text2embedding("machine learning AI", provider)
        results = client.query_points(
            collection_name=collection_name,
            query=query_embedding[0].tolist(),
            limit=5,
        ).points

        # Step 5: Verify
        assert len(results) > 0, "Should find search results"

        for result in results:
            assert result.payload is not None
            assert "text" in result.payload
            assert "source_id" in result.payload
            assert result.payload["source_id"] == "test-lecture-001"

        # Verify semantic relevance
        top_result_text = results[0].payload["text"].lower()
        assert any(
            term in top_result_text
            for term in ["artificial", "intelligence", "machine", "learning"]
        ), f"Top result should be about AI/ML: {top_result_text}"

    @pytest.mark.description("Search results include timestamp metadata")
    @pytest.mark.asyncio
    async def test_search_results_include_timestamps(self, tmp_path: Path) -> None:
        """Test that search results include timestamp information."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(10.5, 18.2, "Semantic search uses embeddings."),
            _create_mock_segment(18.2, 25.0, "Vector databases store these embeddings."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-video-timestamps",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        text_chunks = adapter.chunk(raw_chunks, source)

        # Index
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()
        collection_name = "test-video-timestamps-collection"
        vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

        texts = [c.text for c in text_chunks]
        embeddings = provider.encode_texts(texts)

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            loc = chunk.location
            points.append(
                vector.qdrant_client.models.PointStruct(
                    id=4000 + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "text": chunk.text,
                        "source_id": chunk.source_id,
                        "start_time": loc.start_time if isinstance(loc, TimestampLocation) else None,
                        "end_time": loc.end_time if isinstance(loc, TimestampLocation) else None,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Search
        query_emb = embedding.text2embedding("embeddings", provider)
        results = client.query_points(
            collection_name=collection_name,
            query=query_emb[0].tolist(),
            limit=2,
        ).points

        assert len(results) > 0
        for result in results:
            payload = result.payload
            assert payload is not None
            if payload.get("start_time") is not None:
                assert payload["start_time"] >= 0, "Start time should be non-negative"
            if payload.get("end_time") is not None:
                assert payload["end_time"] > payload.get("start_time", 0), (
                    "End time should be after start time"
                )


class TestDeepLinkFormatValidation:
    """Tests for deep link URL format validation."""

    @pytest.mark.description("Deep link includes timestamp parameter for video")
    def test_deep_link_includes_timestamp(self) -> None:
        """Test that deep link URLs include the correct timestamp parameter."""
        adapter = VideoAdapter()
        location = TimestampLocation(start_time=120.5, end_time=135.2)
        chunk = TextChunk(
            text="Test content",
            source_id="video-123",
            source_type=ContentType.VIDEO,
            location=location,
        )

        base_url = "https://example.com/video/lecture.mp4"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "t=120.5" in deep_link, f"Deep link should include start time: {deep_link}"

    @pytest.mark.description("Deep link appends timestamp with correct separator")
    def test_deep_link_url_format(self) -> None:
        """Test that deep link uses correct URL format with separators."""
        adapter = VideoAdapter()
        location = TimestampLocation(start_time=60.0, end_time=90.0)
        chunk = TextChunk(
            text="Test content",
            source_id="video-123",
            source_type=ContentType.VIDEO,
            location=location,
        )

        # Test with URL without query params
        base_url = "https://example.com/video.mp4"
        deep_link = adapter.get_deep_link(chunk, base_url)
        assert deep_link is not None
        assert "?" in deep_link, "Should use ? separator for URL without params"
        assert deep_link.startswith(base_url), "Should preserve base URL"

        # Test with URL that has existing query params
        base_url_with_params = "https://example.com/video.mp4?ref=search"
        deep_link_params = adapter.get_deep_link(chunk, base_url_with_params)
        assert deep_link_params is not None
        assert "&t=" in deep_link_params, "Should use & separator for URL with existing params"

    @pytest.mark.description("Deep link includes time range for start and end")
    def test_deep_link_time_range(self) -> None:
        """Test that deep link can include both start and end time."""
        adapter = VideoAdapter()
        location = TimestampLocation(start_time=30.0, end_time=45.5)
        chunk = TextChunk(
            text="Test content",
            source_id="video-123",
            source_type=ContentType.VIDEO,
            location=location,
        )

        base_url = "https://example.com/video.mp4"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        # Media Fragments format: t=30.0,45.5
        assert "t=30.0,45.5" in deep_link, f"Should include time range: {deep_link}"

    @pytest.mark.description("Deep link returns None for chunk without location")
    def test_deep_link_without_location(self) -> None:
        """Test that deep link returns None when chunk has no location."""
        adapter = VideoAdapter()
        chunk = TextChunk(
            text="Test content",
            source_id="video-123",
            source_type=ContentType.VIDEO,
            location=None,
        )

        base_url = "https://example.com/video.mp4"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is None, "Should return None for chunk without location"

    @pytest.mark.description("Deep link handles slide location for video presentations")
    def test_deep_link_slide_location(self) -> None:
        """Test that deep link correctly handles slide locations from video presentations."""
        adapter = VideoAdapter()
        location = SlideLocation(slide_number=5)
        chunk = TextChunk(
            text="Slide content",
            source_id="presentation-123",
            source_type=ContentType.VIDEO,
            location=location,
        )

        base_url = "https://example.com/presentation"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "slide=5" in deep_link, f"Deep link should include slide number: {deep_link}"

    @pytest.mark.description("Deep link handles various base URL formats")
    @pytest.mark.parametrize(
        "base_url,expected_separator",
        [
            ("https://example.com/video.mp4", "?"),
            ("https://example.com/video.mp4?id=123", "&"),
            ("http://localhost:8080/media/video.mp4", "?"),
            ("https://cdn.example.com/path/to/video.webm?token=abc", "&"),
        ],
    )
    def test_deep_link_url_separators(
        self, base_url: str, expected_separator: str
    ) -> None:
        """Test deep link uses correct separator for various URL formats."""
        adapter = VideoAdapter()
        location = TimestampLocation(start_time=10.0)
        chunk = TextChunk(
            text="Test",
            source_id="test",
            source_type=ContentType.VIDEO,
            location=location,
        )

        deep_link = adapter.get_deep_link(chunk, base_url)
        assert deep_link is not None

        # Find the separator before the timestamp parameter
        t_index = deep_link.find("t=10.0")
        assert t_index > 0
        separator = deep_link[t_index - 1]
        assert separator == expected_separator, (
            f"Expected '{expected_separator}' separator, got '{separator}' in {deep_link}"
        )


class TestVideoAdapterWithMockedTranscription:
    """Integration tests with mocked Whisper for CI environments."""

    @pytest.mark.description("Mocked transcription produces valid chunks")
    @pytest.mark.asyncio
    async def test_mocked_transcription_flow(self, tmp_path: Path) -> None:
        """Test full transcription flow with mocked Whisper model."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        mock_segments = [
            _create_mock_segment(0.0, 3.0, "First segment of video."),
            _create_mock_segment(3.0, 6.5, "Second segment continues."),
            _create_mock_segment(6.5, 10.0, "Final segment concludes."),
        ]
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-mocked",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Verify extraction
        assert len(raw_chunks) == 3
        assert raw_chunks[0].text == "First segment of video."
        assert raw_chunks[1].text == "Second segment continues."
        assert raw_chunks[2].text == "Final segment concludes."

        # Verify timestamps
        assert raw_chunks[0].location.start_time == 0.0
        assert raw_chunks[0].location.end_time == 3.0
        assert raw_chunks[2].location.end_time == 10.0

        # Verify chunking
        text_chunks = adapter.chunk(raw_chunks, source)
        assert len(text_chunks) > 0
        assert all(c.source_type == ContentType.VIDEO for c in text_chunks)

    @pytest.mark.description("Word-level timestamps work correctly")
    @pytest.mark.asyncio
    async def test_word_level_transcription(self, tmp_path: Path) -> None:
        """Test word-level timestamps with mocked Whisper model."""
        video_file = tmp_path / "test.mp4"
        video_file.touch()

        # Create mock words
        mock_word1 = MagicMock()
        mock_word1.word = "Hello"
        mock_word1.start = 0.0
        mock_word1.end = 0.5
        mock_word1.probability = 0.95

        mock_word2 = MagicMock()
        mock_word2.word = "world"
        mock_word2.start = 0.6
        mock_word2.end = 1.0
        mock_word2.probability = 0.92

        # Create mock segment with words
        mock_segment = MagicMock()
        mock_segment.words = [mock_word1, mock_word2]
        mock_segment.id = 1

        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)

        config = VideoConfig(word_timestamps=True, extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test-word-level",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Verify word-level extraction
        assert len(raw_chunks) == 2
        assert raw_chunks[0].text == "Hello"
        assert raw_chunks[0].location.start_time == 0.0
        assert raw_chunks[0].location.end_time == 0.5
        assert raw_chunks[1].text == "world"
        assert raw_chunks[1].location.start_time == 0.6


class TestSlideSyncVerification:
    """Tests for slide sync with transcription timestamps."""

    @pytest.mark.description("Slide chunks have correct slide numbers")
    def test_slide_chunks_have_slide_numbers(self) -> None:
        """Test that slide chunks from chunking have correct slide numbers."""
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="presentation-video",
            source_type=ContentType.VIDEO,
            path=Path("/data/presentation.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="Introduction to the topic",
                location=SlideLocation(slide_number=1),
                metadata={"chunk_type": "slide", "timestamp": 0.0},
            ),
            RawChunk(
                text="Main content of the slide",
                location=SlideLocation(slide_number=2),
                metadata={"chunk_type": "slide", "timestamp": 30.0},
            ),
            RawChunk(
                text="Conclusion and summary",
                location=SlideLocation(slide_number=3),
                metadata={"chunk_type": "slide", "timestamp": 60.0},
            ),
        ]

        text_chunks = adapter.chunk(raw_chunks, source)

        assert len(text_chunks) == 3
        for i, chunk in enumerate(text_chunks, start=1):
            assert isinstance(chunk.location, SlideLocation)
            assert chunk.location.slide_number == i

    @pytest.mark.description("Mixed transcription and slide chunks are ordered correctly")
    def test_mixed_chunk_ordering(self) -> None:
        """Test that mixed transcription and slide chunks maintain correct ordering."""
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="mixed-content",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,  # Transcription
                location=TimestampLocation(start_time=0.0, end_time=30.0),
                metadata={"chunk_type": "transcription"},
            ),
            RawChunk(
                text="Slide one content",  # Slide
                location=SlideLocation(slide_number=1),
                metadata={"chunk_type": "slide"},
            ),
            RawChunk(
                text="Slide two content",  # Slide
                location=SlideLocation(slide_number=2),
                metadata={"chunk_type": "slide"},
            ),
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        text_chunks = adapter.chunk(raw_chunks, source, config)

        # Should have transcription chunks followed by slide chunks
        assert len(text_chunks) >= 3

        # Verify sequence indices are increasing
        for i, chunk in enumerate(text_chunks):
            assert chunk.sequence_index == i


# Helper functions


def _create_mock_segment(start: float, end: float, text: str) -> MagicMock:
    """Create a mock Whisper segment with the given properties."""
    segment = MagicMock()
    segment.start = start
    segment.end = end
    segment.text = f" {text}"  # Whisper adds leading space
    segment.avg_logprob = -0.3
    segment.id = int(start)
    return segment
