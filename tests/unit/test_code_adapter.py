# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for CodeAdapter content adapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.code import (
    BOUNDARY_NODE_TYPES,
    DEFAULT_IGNORE_PATTERNS,
    LANGUAGE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    TREESITTER_LANGUAGES,
    CodeAdapter,
    CodeConfig,
    CodeSymbol,
    _detect_language,
    _get_git_branch,
    _get_git_ref,
    _parse_gitignore,
    _should_ignore,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import CodeLocation

pytestmark = pytest.mark.unit


class TestCodeAdapterInit:
    """Tests for CodeAdapter initialization."""

    @pytest.mark.description("CodeAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = CodeAdapter()
        assert adapter._config.respect_gitignore is True
        assert adapter._config.max_file_size == 1024 * 1024
        assert adapter._config.include_comments is True
        assert adapter._config.preserve_git_ref is True
        assert adapter._config.chunk_by_symbol is True
        assert adapter._config.fallback_line_chunking == 50

    @pytest.mark.description("CodeAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = CodeConfig(
            respect_gitignore=False,
            max_file_size=512 * 1024,
            include_comments=False,
            preserve_git_ref=False,
            chunk_by_symbol=False,
            fallback_line_chunking=100,
        )
        adapter = CodeAdapter(config=config)
        assert adapter._config.respect_gitignore is False
        assert adapter._config.max_file_size == 512 * 1024
        assert adapter._config.include_comments is False
        assert adapter._config.preserve_git_ref is False
        assert adapter._config.chunk_by_symbol is False
        assert adapter._config.fallback_line_chunking == 100


class TestCodeAdapterSupportedTypes:
    """Tests for CodeAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns TEXT only")
    def test_supported_types(self) -> None:
        adapter = CodeAdapter()
        assert adapter.supported_types == frozenset({ContentType.TEXT})


class TestCodeAdapterSupports:
    """Tests for CodeAdapter.supports method."""

    @pytest.mark.description("supports returns True for Python files")
    def test_supports_python(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=py_file,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for JavaScript files")
    def test_supports_javascript(self, tmp_path: Path) -> None:
        js_file = tmp_path / "test.js"
        js_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=js_file,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for TypeScript files")
    def test_supports_typescript(self, tmp_path: Path) -> None:
        ts_file = tmp_path / "test.ts"
        ts_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=ts_file,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for Go files")
    def test_supports_go(self, tmp_path: Path) -> None:
        go_file = tmp_path / "test.go"
        go_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=go_file,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for Rust files")
    def test_supports_rust(self, tmp_path: Path) -> None:
        rs_file = tmp_path / "test.rs"
        rs_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=rs_file,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-TEXT content type")
    def test_rejects_non_text_type(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=py_file,
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for unsupported extensions")
    def test_rejects_unsupported_extension(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=txt_file,
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns True for directories with code files")
    def test_supports_directory_with_code(self, tmp_path: Path) -> None:
        py_file = tmp_path / "src" / "main.py"
        py_file.parent.mkdir(parents=True)
        py_file.touch()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for git repositories")
    def test_supports_git_repo(self, tmp_path: Path) -> None:
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False when path is None")
    def test_rejects_none_path(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://github.com/example/repo",
        )
        assert adapter.supports(source) is False


class TestCodeAdapterExtract:
    """Tests for CodeAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing path")
    @pytest.mark.asyncio
    async def test_extract_missing_path_raises(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/nonexistent/file.py"),
        )
        with pytest.raises(ValueError, match="Path not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks with CodeLocation")
    @pytest.mark.asyncio
    async def test_extract_yields_chunks(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    return 'world'\n")

        adapter = CodeAdapter(config=CodeConfig(
            chunk_by_symbol=False,  # Use line-based for this test
            preserve_git_ref=False,
        ))
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        assert "def hello" in chunks[0].text
        assert isinstance(chunks[0].location, CodeLocation)
        assert chunks[0].location.file_path == "test.py"
        assert chunks[0].metadata["language"] == "python"

    @pytest.mark.description("extract respects gitignore patterns")
    @pytest.mark.asyncio
    async def test_extract_respects_gitignore(self, tmp_path: Path) -> None:
        # Create a repository structure
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("ignored/\n")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass\n")
        (tmp_path / "ignored").mkdir()
        (tmp_path / "ignored" / "skip.py").write_text("def skip(): pass\n")

        adapter = CodeAdapter(config=CodeConfig(
            respect_gitignore=True,
            chunk_by_symbol=False,
            preserve_git_ref=False,
        ))
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        # Should only have chunks from src/main.py
        file_paths = [c.location.file_path for c in chunks if c.location]
        assert any("main.py" in fp for fp in file_paths)
        assert not any("skip.py" in fp for fp in file_paths)

    @pytest.mark.description("extract processes directory recursively")
    @pytest.mark.asyncio
    async def test_extract_recursive(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "lib").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass\n")
        (tmp_path / "src" / "lib" / "utils.py").write_text("def util(): pass\n")

        adapter = CodeAdapter(config=CodeConfig(
            chunk_by_symbol=False,
            preserve_git_ref=False,
        ))
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        file_paths = [c.location.file_path for c in chunks if c.location]
        assert any("main.py" in fp for fp in file_paths)
        assert any("utils.py" in fp for fp in file_paths)


class TestCodeAdapterChunk:
    """Tests for CodeAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/repo"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines raw chunks into text chunks")
    def test_chunk_combines_chunks(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/repo"),
        )

        raw_chunks = [
            RawChunk(
                text="def hello():\n    return 'world'",
                location=CodeLocation(file_path="test.py", start_line=1, end_line=2),
                metadata={"language": "python"},
            )
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) >= 1
        assert "def hello" in result[0].text
        assert result[0].source_id == "test"
        assert result[0].source_type == ContentType.TEXT

    @pytest.mark.description("chunk preserves CodeLocation from raw chunks")
    def test_chunk_preserves_locations(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/repo"),
        )

        raw_chunks = [
            RawChunk(
                text="fn main() {}",
                location=CodeLocation(file_path="main.rs", start_line=1, end_line=1),
                metadata={"language": "rust"},
            )
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) == 1
        assert isinstance(result[0].location, CodeLocation)
        assert result[0].location.file_path == "main.rs"
        assert result[0].location.start_line == 1

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = CodeAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/repo"),
        )

        # Create chunks from different files to force multiple output chunks
        raw_chunks = [
            RawChunk(
                text="code " * 50,
                location=CodeLocation(file_path="file1.py", start_line=1, end_line=10),
                metadata={"language": "python", "file_path": "file1.py"},
            ),
            RawChunk(
                text="more " * 50,
                location=CodeLocation(file_path="file2.py", start_line=1, end_line=10),
                metadata={"language": "python", "file_path": "file2.py"},
            ),
        ]

        config = ChunkConfig(target_words=40, overlap_words=5, preserve_sentences=False)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestCodeAdapterGetLocation:
    """Tests for CodeAdapter.get_location method."""

    @pytest.mark.description("get_location returns chunk location")
    def test_get_location_returns_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = CodeAdapter()
        location = CodeLocation(file_path="test.py", start_line=10, end_line=20)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = CodeAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.TEXT,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestCodeAdapterGetDeepLink:
    """Tests for CodeAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates line URL")
    def test_get_deep_link_with_lines(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = CodeAdapter()
        location = CodeLocation(file_path="src/main.py", start_line=10, end_line=20)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://github.com/example/repo")
        assert result is not None
        assert "src/main.py" in result
        assert "L10" in result
        assert "L20" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = CodeAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.TEXT,
        )

        result = adapter.get_deep_link(chunk, "https://github.com/example/repo")
        assert result is None


class TestCodeConfig:
    """Tests for CodeConfig dataclass."""

    @pytest.mark.description("CodeConfig has correct defaults")
    def test_default_values(self) -> None:
        config = CodeConfig()
        assert config.respect_gitignore is True
        assert config.additional_ignore_patterns == frozenset()
        assert config.max_file_size == 1024 * 1024
        assert config.include_comments is True
        assert config.preserve_git_ref is True
        assert config.chunk_by_symbol is True
        assert config.fallback_line_chunking == 50

    @pytest.mark.description("CodeConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = CodeConfig(
            respect_gitignore=False,
            additional_ignore_patterns=frozenset({"*.test.py"}),
            max_file_size=2 * 1024 * 1024,
            include_comments=False,
            preserve_git_ref=False,
            chunk_by_symbol=False,
            fallback_line_chunking=100,
        )
        assert config.respect_gitignore is False
        assert "*.test.py" in config.additional_ignore_patterns
        assert config.max_file_size == 2 * 1024 * 1024
        assert config.include_comments is False
        assert config.preserve_git_ref is False
        assert config.chunk_by_symbol is False
        assert config.fallback_line_chunking == 100


class TestCodeSymbol:
    """Tests for CodeSymbol dataclass."""

    @pytest.mark.description("CodeSymbol stores symbol information")
    def test_code_symbol(self) -> None:
        symbol = CodeSymbol(
            name="hello",
            kind="function_definition",
            start_line=1,
            end_line=5,
            text="def hello():\n    pass",
        )
        assert symbol.name == "hello"
        assert symbol.kind == "function_definition"
        assert symbol.start_line == 1
        assert symbol.end_line == 5
        assert "def hello" in symbol.text


class TestLanguageConstants:
    """Tests for language-related constants."""

    @pytest.mark.description("LANGUAGE_EXTENSIONS covers Python")
    def test_python_extensions(self) -> None:
        assert ".py" in LANGUAGE_EXTENSIONS["python"]
        assert ".pyi" in LANGUAGE_EXTENSIONS["python"]

    @pytest.mark.description("LANGUAGE_EXTENSIONS covers JavaScript")
    def test_javascript_extensions(self) -> None:
        assert ".js" in LANGUAGE_EXTENSIONS["javascript"]
        assert ".mjs" in LANGUAGE_EXTENSIONS["javascript"]

    @pytest.mark.description("LANGUAGE_EXTENSIONS covers TypeScript")
    def test_typescript_extensions(self) -> None:
        assert ".ts" in LANGUAGE_EXTENSIONS["typescript"]
        assert ".tsx" in LANGUAGE_EXTENSIONS["typescript"]

    @pytest.mark.description("LANGUAGE_EXTENSIONS covers Go")
    def test_go_extensions(self) -> None:
        assert ".go" in LANGUAGE_EXTENSIONS["go"]

    @pytest.mark.description("LANGUAGE_EXTENSIONS covers Rust")
    def test_rust_extensions(self) -> None:
        assert ".rs" in LANGUAGE_EXTENSIONS["rust"]

    @pytest.mark.description("SUPPORTED_EXTENSIONS is union of all language extensions")
    def test_supported_extensions(self) -> None:
        assert ".py" in SUPPORTED_EXTENSIONS
        assert ".js" in SUPPORTED_EXTENSIONS
        assert ".ts" in SUPPORTED_EXTENSIONS
        assert ".go" in SUPPORTED_EXTENSIONS
        assert ".rs" in SUPPORTED_EXTENSIONS

    @pytest.mark.description("TREESITTER_LANGUAGES maps to grammar names")
    def test_treesitter_languages(self) -> None:
        assert TREESITTER_LANGUAGES["python"] == "python"
        assert TREESITTER_LANGUAGES["javascript"] == "javascript"
        assert TREESITTER_LANGUAGES["typescript"] == "typescript"
        assert TREESITTER_LANGUAGES["go"] == "go"
        assert TREESITTER_LANGUAGES["rust"] == "rust"

    @pytest.mark.description("BOUNDARY_NODE_TYPES has entries for all languages")
    def test_boundary_node_types(self) -> None:
        assert "function_definition" in BOUNDARY_NODE_TYPES["python"]
        assert "class_definition" in BOUNDARY_NODE_TYPES["python"]
        assert "function_declaration" in BOUNDARY_NODE_TYPES["javascript"]
        assert "function_declaration" in BOUNDARY_NODE_TYPES["typescript"]
        assert "function_declaration" in BOUNDARY_NODE_TYPES["go"]
        assert "function_item" in BOUNDARY_NODE_TYPES["rust"]


class TestIgnorePatterns:
    """Tests for ignore pattern handling."""

    @pytest.mark.description("DEFAULT_IGNORE_PATTERNS includes common patterns")
    def test_default_ignore_patterns(self) -> None:
        assert ".git" in DEFAULT_IGNORE_PATTERNS
        assert "node_modules" in DEFAULT_IGNORE_PATTERNS
        assert "__pycache__" in DEFAULT_IGNORE_PATTERNS
        assert ".venv" in DEFAULT_IGNORE_PATTERNS

    @pytest.mark.description("_should_ignore matches filename patterns")
    def test_should_ignore_filename(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.pyc"
        assert _should_ignore(test_file, tmp_path, {"*.pyc"}) is True

    @pytest.mark.description("_should_ignore matches directory patterns")
    def test_should_ignore_directory(self, tmp_path: Path) -> None:
        test_file = tmp_path / "node_modules" / "package" / "index.js"
        # Note: fnmatch won't match partial paths without **
        assert _should_ignore(test_file, tmp_path, {"node_modules/*"}) is True

    @pytest.mark.description("_should_ignore returns False for non-matching files")
    def test_should_not_ignore(self, tmp_path: Path) -> None:
        test_file = tmp_path / "src" / "main.py"
        assert _should_ignore(test_file, tmp_path, {"*.pyc"}) is False


class TestGitignoreParsing:
    """Tests for gitignore file parsing."""

    @pytest.mark.description("_parse_gitignore extracts patterns")
    def test_parse_gitignore(self, tmp_path: Path) -> None:
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__\n# Comment\n\nbuild/\n")

        patterns = _parse_gitignore(gitignore)

        assert "*.pyc" in patterns
        assert "__pycache__" in patterns
        assert "build/" in patterns
        assert "# Comment" not in patterns

    @pytest.mark.description("_parse_gitignore returns empty for missing file")
    def test_parse_gitignore_missing(self, tmp_path: Path) -> None:
        gitignore = tmp_path / ".gitignore"
        patterns = _parse_gitignore(gitignore)
        assert patterns == set()

    @pytest.mark.description("_parse_gitignore skips negation patterns")
    def test_parse_gitignore_negation(self, tmp_path: Path) -> None:
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n!important.pyc\n")

        patterns = _parse_gitignore(gitignore)

        assert "*.pyc" in patterns
        assert "!important.pyc" not in patterns


class TestLanguageDetection:
    """Tests for language detection."""

    @pytest.mark.description("_detect_language identifies Python")
    def test_detect_python(self) -> None:
        assert _detect_language(Path("test.py")) == "python"
        assert _detect_language(Path("test.pyi")) == "python"

    @pytest.mark.description("_detect_language identifies JavaScript")
    def test_detect_javascript(self) -> None:
        assert _detect_language(Path("test.js")) == "javascript"
        assert _detect_language(Path("test.mjs")) == "javascript"

    @pytest.mark.description("_detect_language identifies TypeScript")
    def test_detect_typescript(self) -> None:
        assert _detect_language(Path("test.ts")) == "typescript"
        assert _detect_language(Path("test.tsx")) == "typescript"

    @pytest.mark.description("_detect_language identifies Go")
    def test_detect_go(self) -> None:
        assert _detect_language(Path("main.go")) == "go"

    @pytest.mark.description("_detect_language identifies Rust")
    def test_detect_rust(self) -> None:
        assert _detect_language(Path("main.rs")) == "rust"

    @pytest.mark.description("_detect_language returns None for unknown")
    def test_detect_unknown(self) -> None:
        assert _detect_language(Path("test.txt")) is None
        assert _detect_language(Path("test.java")) is None


class TestGitHelpers:
    """Tests for git helper functions."""

    @pytest.mark.description("_get_git_ref returns commit hash")
    def test_get_git_ref(self, tmp_path: Path) -> None:
        # Mock subprocess to avoid requiring git
        with patch("voogle.adapters.code.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="abc123def456\n",
            )
            result = _get_git_ref(tmp_path)
            assert result == "abc123def456"

    @pytest.mark.description("_get_git_ref returns None on error")
    def test_get_git_ref_error(self, tmp_path: Path) -> None:
        with patch("voogle.adapters.code.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = _get_git_ref(tmp_path)
            assert result is None

    @pytest.mark.description("_get_git_branch returns branch name")
    def test_get_git_branch(self, tmp_path: Path) -> None:
        with patch("voogle.adapters.code.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="main\n",
            )
            result = _get_git_branch(tmp_path)
            assert result == "main"

    @pytest.mark.description("_get_git_branch returns None for detached HEAD")
    def test_get_git_branch_detached(self, tmp_path: Path) -> None:
        with patch("voogle.adapters.code.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="HEAD\n",
            )
            result = _get_git_branch(tmp_path)
            assert result is None
