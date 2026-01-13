# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Code repository content adapter with Tree-sitter AST parsing.

This module provides a CodeAdapter that implements the ContentAdapter interface
for source code repositories. It uses Tree-sitter for AST parsing to extract
function and class boundaries, supporting Python, JavaScript, TypeScript, Go,
and Rust.
"""
import fnmatch
import logging
import os
import re
import subprocess
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import CodeLocation, Location

logger = logging.getLogger(__name__)


# Supported programming languages and their file extensions
LANGUAGE_EXTENSIONS: dict[str, frozenset[str]] = {
    "python": frozenset({".py", ".pyi", ".pyw"}),
    "javascript": frozenset({".js", ".mjs", ".cjs"}),
    "typescript": frozenset({".ts", ".tsx", ".mts", ".cts"}),
    "go": frozenset({".go"}),
    "rust": frozenset({".rs"}),
}

# All supported extensions as a flat set
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset().union(
    *LANGUAGE_EXTENSIONS.values()
)

# Tree-sitter grammar names for each language
TREESITTER_LANGUAGES: dict[str, str] = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "go": "go",
    "rust": "rust",
}

# AST node types that represent semantic boundaries per language
BOUNDARY_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({
        "function_definition",
        "async_function_definition",
        "class_definition",
        "decorated_definition",
    }),
    "javascript": frozenset({
        "function_declaration",
        "function_expression",
        "arrow_function",
        "class_declaration",
        "method_definition",
    }),
    "typescript": frozenset({
        "function_declaration",
        "function_expression",
        "arrow_function",
        "class_declaration",
        "method_definition",
        "interface_declaration",
        "type_alias_declaration",
    }),
    "go": frozenset({
        "function_declaration",
        "method_declaration",
        "type_declaration",
    }),
    "rust": frozenset({
        "function_item",
        "impl_item",
        "struct_item",
        "enum_item",
        "trait_item",
        "mod_item",
    }),
}

# Default gitignore patterns (common patterns to always ignore)
DEFAULT_IGNORE_PATTERNS: frozenset[str] = frozenset({
    ".git",
    ".git/*",
    "**/.git",
    "**/.git/*",
    "node_modules",
    "node_modules/*",
    "**/node_modules",
    "**/node_modules/*",
    "__pycache__",
    "__pycache__/*",
    "**/__pycache__",
    "**/__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".venv",
    ".venv/*",
    "**/.venv",
    "**/.venv/*",
    "venv",
    "venv/*",
    "**/venv",
    "**/venv/*",
    ".env",
    "*.min.js",
    "*.min.css",
    "dist",
    "dist/*",
    "**/dist",
    "**/dist/*",
    "build",
    "build/*",
    "**/build",
    "**/build/*",
    "target",
    "target/*",
    "**/target",
    "**/target/*",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.egg-info",
    ".coverage",
    "coverage",
    "htmlcov",
    ".idea",
    ".vscode",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "poetry.lock",
})


@dataclass
class CodeConfig:
    """Configuration for code extraction.

    Attributes:
        respect_gitignore: Whether to respect .gitignore files.
        additional_ignore_patterns: Extra patterns to ignore.
        max_file_size: Maximum file size in bytes to process.
        include_comments: Whether to include comments in chunks.
        preserve_git_ref: Whether to preserve git ref for source tracking.
        chunk_by_symbol: Whether to chunk by function/class boundaries.
        fallback_line_chunking: Line count for fallback chunking when AST unavailable.
    """

    respect_gitignore: bool = True
    additional_ignore_patterns: frozenset[str] = field(default_factory=frozenset)
    max_file_size: int = 1024 * 1024  # 1MB default
    include_comments: bool = True
    preserve_git_ref: bool = True
    chunk_by_symbol: bool = True
    fallback_line_chunking: int = 50


def _get_treesitter() -> Any:
    """Lazy import of tree_sitter module.

    Returns:
        The tree_sitter module.

    Raises:
        ImportError: If tree-sitter is not installed.
    """
    try:
        import tree_sitter
        return tree_sitter
    except ImportError as e:
        raise ImportError(
            "tree-sitter is required for code processing. "
            "Install with: pip install 'voogle[code]' or pip install tree-sitter"
        ) from e


def _get_treesitter_language(language: str) -> Any:
    """Get tree-sitter language parser.

    Args:
        language: The programming language name.

    Returns:
        Tree-sitter Language object for the given language.

    Raises:
        ImportError: If the language grammar is not installed.
    """
    grammar_name = TREESITTER_LANGUAGES.get(language)
    if grammar_name is None:
        raise ImportError(f"Unsupported language: {language}")

    try:
        if language == "python":
            import tree_sitter_python
            return tree_sitter_python.language()
        elif language == "javascript":
            import tree_sitter_javascript
            return tree_sitter_javascript.language()
        elif language == "typescript":
            import tree_sitter_typescript
            return tree_sitter_typescript.language_typescript()
        elif language == "go":
            import tree_sitter_go
            return tree_sitter_go.language()
        elif language == "rust":
            import tree_sitter_rust
            return tree_sitter_rust.language()
        else:
            raise ImportError(f"Unsupported language: {language}")
    except ImportError as e:
        raise ImportError(
            f"tree-sitter grammar for {language} is not installed. "
            f"Install with: pip install tree-sitter-{grammar_name}"
        ) from e


def _detect_language(file_path: Path) -> str | None:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the source file.

    Returns:
        Language name string, or None if not supported.
    """
    suffix = file_path.suffix.lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if suffix in extensions:
            return language
    return None


def _should_ignore(
    file_path: Path,
    root_path: Path,
    ignore_patterns: set[str],
) -> bool:
    """Check if a file should be ignored based on patterns.

    Args:
        file_path: Path to check.
        root_path: Root directory for relative path calculation.
        ignore_patterns: Set of gitignore-style patterns.

    Returns:
        True if the file should be ignored.
    """
    try:
        relative_path = file_path.relative_to(root_path)
    except ValueError:
        relative_path = file_path

    relative_str = str(relative_path)
    relative_posix = relative_str.replace(os.sep, "/")
    name = file_path.name

    # Get all path parts for directory matching
    parts = relative_path.parts

    for pattern in ignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            dir_pattern = pattern[:-1]  # Remove trailing slash
            # Check if any parent directory matches
            for part in parts[:-1]:  # Exclude filename itself
                if fnmatch.fnmatch(part, dir_pattern):
                    return True
            # Also check full directory paths
            for i in range(len(parts) - 1):
                partial_path = "/".join(parts[:i + 1])
                if fnmatch.fnmatch(partial_path, dir_pattern):
                    return True
            continue

        # Check against filename
        if fnmatch.fnmatch(name, pattern):
            return True
        # Check against relative path
        if fnmatch.fnmatch(relative_str, pattern):
            return True
        # Check against path with forward slashes
        if fnmatch.fnmatch(relative_posix, pattern):
            return True
        # Check if any directory component matches
        for part in parts[:-1]:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False


def _parse_gitignore(gitignore_path: Path) -> set[str]:
    """Parse a .gitignore file and return patterns.

    Args:
        gitignore_path: Path to .gitignore file.

    Returns:
        Set of ignore patterns.
    """
    patterns: set[str] = set()

    if not gitignore_path.exists():
        return patterns

    try:
        content = gitignore_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Handle negation (we don't support it, just skip)
            if line.startswith("!"):
                continue
            patterns.add(line)
    except Exception as e:
        logger.warning("Failed to parse .gitignore at %s: %s", gitignore_path, e)

    return patterns


def _get_git_ref(repo_path: Path) -> str | None:
    """Get the current git ref (commit hash or branch name).

    Args:
        repo_path: Path to the git repository.

    Returns:
        Git ref string, or None if not a git repo or error.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # Short hash
    except Exception as e:
        logger.debug("Failed to get git ref: %s", e)

    return None


def _get_git_branch(repo_path: Path) -> str | None:
    """Get the current git branch name.

    Args:
        repo_path: Path to the git repository.

    Returns:
        Branch name string, or None if not on a branch or error.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip() != "HEAD":
            return result.stdout.strip()
    except Exception as e:
        logger.debug("Failed to get git branch: %s", e)

    return None


@dataclass(frozen=True)
class CodeSymbol:
    """Represents a code symbol (function, class, etc.) extracted from AST.

    Attributes:
        name: Symbol name.
        kind: Symbol kind (function, class, method, etc.).
        start_line: 1-indexed start line.
        end_line: 1-indexed end line.
        text: The source code text for this symbol.
    """

    name: str
    kind: str
    start_line: int
    end_line: int
    text: str


class CodeAdapter(ContentAdapter):
    """Content adapter for source code repositories using Tree-sitter AST parsing.

    Extracts code with function/class boundary chunking, supporting Python,
    JavaScript, TypeScript, Go, and Rust. Respects .gitignore files and
    preserves git ref information.

    Example:
        >>> adapter = CodeAdapter()
        >>> source = ContentSource(
        ...     source_id="repo-123",
        ...     source_type=ContentType.TEXT,
        ...     path=Path("/path/to/repo"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: CodeConfig | None = None) -> None:
        """Initialize the code adapter.

        Args:
            config: Code extraction configuration. Uses defaults if not provided.
        """
        self._config = config or CodeConfig()
        self._parser_cache: dict[str, Any] = {}

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.TEXT (code is text content).
        """
        return frozenset({ContentType.TEXT})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is a code repository or supported code file.
        """
        if source.source_type != ContentType.TEXT:
            return False

        if source.path is None:
            return False

        # Support both directories (repositories) and individual files
        if source.path.is_dir():
            # Check if it looks like a code repository
            return self._is_code_repository(source.path)

        # Check if it's a supported code file
        return source.path.suffix.lower() in SUPPORTED_EXTENSIONS

    def _is_code_repository(self, path: Path) -> bool:
        """Check if a directory appears to be a code repository.

        Args:
            path: Directory path to check.

        Returns:
            True if the directory contains code files.
        """
        # Check for common code repo indicators
        if (path / ".git").exists():
            return True

        # Check if any supported code files exist
        for ext in SUPPORTED_EXTENSIONS:
            try:
                next(path.rglob(f"*{ext}"))
                return True
            except StopIteration:
                continue

        return False

    def _get_ignore_patterns(self, root_path: Path) -> set[str]:
        """Get all ignore patterns for a repository.

        Args:
            root_path: Root directory of the repository.

        Returns:
            Set of all ignore patterns to apply.
        """
        patterns: set[str] = set(DEFAULT_IGNORE_PATTERNS)

        if self._config.respect_gitignore:
            # Parse root .gitignore
            gitignore_path = root_path / ".gitignore"
            patterns.update(_parse_gitignore(gitignore_path))

        # Add custom patterns
        patterns.update(self._config.additional_ignore_patterns)

        return patterns

    def _get_parser(self, language: str) -> Any:
        """Get or create a Tree-sitter parser for a language.

        Args:
            language: Programming language name.

        Returns:
            Tree-sitter Parser object.

        Raises:
            ImportError: If tree-sitter or language grammar not available.
        """
        if language in self._parser_cache:
            return self._parser_cache[language]

        tree_sitter = _get_treesitter()
        lang = _get_treesitter_language(language)

        parser = tree_sitter.Parser(lang)
        self._parser_cache[language] = parser

        return parser

    def _extract_symbols(
        self,
        source_code: bytes,
        language: str,
    ) -> list[CodeSymbol]:
        """Extract code symbols using Tree-sitter AST parsing.

        Args:
            source_code: The source code as bytes.
            language: Programming language name.

        Returns:
            List of extracted CodeSymbol objects.
        """
        try:
            parser = self._get_parser(language)
        except ImportError as e:
            logger.debug("Tree-sitter not available, falling back: %s", e)
            return []

        tree = parser.parse(source_code)
        symbols: list[CodeSymbol] = []
        boundary_types = BOUNDARY_NODE_TYPES.get(language, frozenset())

        def extract_node(node: Any) -> None:
            if node.type in boundary_types:
                # Extract symbol name
                name = self._get_symbol_name(node, language)
                if name:
                    start_line = node.start_point[0] + 1  # Convert to 1-indexed
                    end_line = node.end_point[0] + 1
                    text = source_code[node.start_byte:node.end_byte].decode(
                        "utf-8", errors="replace"
                    )

                    symbols.append(CodeSymbol(
                        name=name,
                        kind=node.type,
                        start_line=start_line,
                        end_line=end_line,
                        text=text,
                    ))

            # Recurse into children
            for child in node.children:
                extract_node(child)

        extract_node(tree.root_node)

        return symbols

    def _get_symbol_name(self, node: Any, language: str) -> str | None:
        """Extract the name of a symbol from an AST node.

        Args:
            node: Tree-sitter AST node.
            language: Programming language name (reserved for language-specific handling).

        Returns:
            Symbol name string, or None if not found.
        """
        # Look for name/identifier child nodes
        # language param is reserved for future language-specific handling
        _ = language
        name_field_names = ["name", "identifier"]

        for child in node.children:
            if child.type in ("identifier", "name", "type_identifier"):
                return child.text.decode("utf-8", errors="replace")

        # Try named children
        for field_name in name_field_names:
            try:
                name_node = node.child_by_field_name(field_name)
                if name_node:
                    return name_node.text.decode("utf-8", errors="replace")
            except Exception:
                pass

        return None

    def _chunk_by_lines(
        self,
        source_code: str,
        lines_per_chunk: int,
    ) -> list[tuple[str, int, int]]:
        """Fallback chunking by line count.

        Args:
            source_code: Source code text.
            lines_per_chunk: Number of lines per chunk.

        Returns:
            List of (text, start_line, end_line) tuples.
        """
        lines = source_code.splitlines(keepends=True)
        chunks: list[tuple[str, int, int]] = []

        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i:i + lines_per_chunk]
            text = "".join(chunk_lines).strip()
            if text:
                start_line = i + 1  # 1-indexed
                end_line = min(i + lines_per_chunk, len(lines))
                chunks.append((text, start_line, end_line))

        return chunks

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract code chunks from a source code repository or file.

        Parses source code using Tree-sitter to extract function and class
        boundaries. Falls back to line-based chunking if AST parsing fails.

        Args:
            source: The code source to extract from.

        Yields:
            RawChunk instances with extracted code and CodeLocation.

        Raises:
            ValueError: If the source is not supported.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        if source.path is None:
            raise ValueError(
                f"Code source {source.source_id} requires a local file path"
            )

        if not source.path.exists():
            raise ValueError(f"Path not found: {source.path}")

        # Get git information if enabled
        git_ref = None
        git_branch = None
        root_path = source.path if source.path.is_dir() else source.path.parent

        if self._config.preserve_git_ref:
            git_ref = _get_git_ref(root_path)
            git_branch = _get_git_branch(root_path)

        # Get ignore patterns
        ignore_patterns = self._get_ignore_patterns(root_path)

        if source.path.is_dir():
            # Process entire repository
            logger.info("Starting code extraction of repository %s", source.path)
            async for chunk in self._extract_directory(
                source.path, ignore_patterns, git_ref, git_branch
            ):
                yield chunk
        else:
            # Process single file
            logger.info("Starting code extraction of file %s", source.path)
            async for chunk in self._extract_file(
                source.path, source.path.parent, git_ref, git_branch
            ):
                yield chunk

        logger.info("Completed code extraction of %s", source.path)

    async def _extract_directory(
        self,
        directory: Path,
        ignore_patterns: set[str],
        git_ref: str | None,
        git_branch: str | None,
    ) -> AsyncIterator[RawChunk]:
        """Extract code from all files in a directory.

        Args:
            directory: Directory to extract from.
            ignore_patterns: Patterns for files to ignore.
            git_ref: Git commit ref for metadata.
            git_branch: Git branch name for metadata.

        Yields:
            RawChunk instances from all code files.
        """
        for file_path in directory.rglob("*"):
            # Skip non-files
            if not file_path.is_file():
                continue

            # Skip unsupported extensions
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Skip ignored files
            if _should_ignore(file_path, directory, ignore_patterns):
                logger.debug("Ignoring %s", file_path)
                continue

            # Skip files that are too large
            try:
                if file_path.stat().st_size > self._config.max_file_size:
                    logger.debug("Skipping large file %s", file_path)
                    continue
            except OSError:
                continue

            async for chunk in self._extract_file(
                file_path, directory, git_ref, git_branch
            ):
                yield chunk

    async def _extract_file(
        self,
        file_path: Path,
        root_path: Path,
        git_ref: str | None,
        git_branch: str | None,
    ) -> AsyncIterator[RawChunk]:
        """Extract code from a single file.

        Args:
            file_path: Path to the source file.
            root_path: Root directory for relative path calculation.
            git_ref: Git commit ref for metadata.
            git_branch: Git branch name for metadata.

        Yields:
            RawChunk instances from the file.
        """
        language = _detect_language(file_path)
        if language is None:
            logger.debug("Unknown language for %s", file_path)
            return

        try:
            source_bytes = file_path.read_bytes()
            source_code = source_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.warning("Failed to read %s: %s", file_path, e)
            return

        # Calculate relative path for location
        try:
            relative_path = str(file_path.relative_to(root_path))
        except ValueError:
            relative_path = file_path.name

        # Build base metadata
        base_metadata: dict[str, Any] = {
            "language": language,
            "file_path": relative_path,
        }
        if git_ref:
            base_metadata["git_ref"] = git_ref
        if git_branch:
            base_metadata["git_branch"] = git_branch

        # Try AST-based extraction if enabled
        if self._config.chunk_by_symbol:
            symbols = self._extract_symbols(source_bytes, language)

            if symbols:
                for symbol in symbols:
                    location = CodeLocation(
                        file_path=relative_path,
                        start_line=symbol.start_line,
                        end_line=symbol.end_line,
                    )

                    metadata = dict(base_metadata)
                    metadata["symbol_name"] = symbol.name
                    metadata["symbol_kind"] = symbol.kind

                    yield RawChunk(
                        text=self._normalize_code(symbol.text),
                        location=location,
                        metadata=metadata,
                    )
                return

        # Fall back to line-based chunking
        logger.debug("Using line-based chunking for %s", file_path)
        chunks = self._chunk_by_lines(
            source_code,
            self._config.fallback_line_chunking,
        )

        for text, start_line, end_line in chunks:
            location = CodeLocation(
                file_path=relative_path,
                start_line=start_line,
                end_line=end_line,
            )

            yield RawChunk(
                text=self._normalize_code(text),
                location=location,
                metadata=dict(base_metadata),
            )

    def _normalize_code(self, text: str) -> str:
        """Normalize code text for embedding.

        Args:
            text: Raw code text.

        Returns:
            Normalized code text.
        """
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip trailing whitespace from lines
        text = "\n".join(line.rstrip() for line in text.splitlines())
        return text.strip()

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw code chunks into text chunks for embedding.

        For code, chunks are typically already at the right granularity
        (function/class level), so this mainly handles combining very
        small chunks if needed.

        Args:
            raw_chunks: List of RawChunk instances from extraction.
            source: The source these chunks came from.
            config: Chunking configuration. Uses defaults if not provided.

        Returns:
            List of TextChunk instances ready for embedding.
        """
        if not raw_chunks:
            return []

        cfg = config or ChunkConfig(
            target_words=100,  # Higher for code
            max_words=200,
            overlap_words=10,
            preserve_sentences=False,
        )

        text_chunks: list[TextChunk] = []
        sequence_index = 0

        # Group chunks by file for potential merging
        current_words: list[str] = []
        current_location: CodeLocation | None = None
        current_file: str | None = None
        current_metadata: dict[str, Any] = {}

        for raw_chunk in raw_chunks:
            # Get file path from location or metadata
            chunk_file = None
            if isinstance(raw_chunk.location, CodeLocation):
                chunk_file = raw_chunk.location.file_path
            elif "file_path" in raw_chunk.metadata:
                chunk_file = raw_chunk.metadata["file_path"]

            # If we're switching files or current is full, emit chunk
            if current_file and (
                chunk_file != current_file or len(current_words) >= cfg.target_words
            ):
                if current_words:
                    text = " ".join(current_words)
                    text_chunks.append(
                        TextChunk(
                            text=text,
                            source_id=source.source_id,
                            source_type=source.source_type,
                            location=current_location,
                            sequence_index=sequence_index,
                            metadata=current_metadata,
                        )
                    )
                    sequence_index += 1
                    current_words = []
                    current_location = None
                    current_metadata = {}

            # Update current file
            current_file = chunk_file

            # Accumulate words
            words = raw_chunk.text.split()
            if current_location is None and isinstance(raw_chunk.location, CodeLocation):
                current_location = raw_chunk.location
                current_metadata = dict(raw_chunk.metadata)

            current_words.extend(words)

        # Emit final chunk
        if current_words:
            text = " ".join(current_words)
            text_chunks.append(
                TextChunk(
                    text=text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=current_location,
                    sequence_index=sequence_index,
                    metadata=current_metadata,
                )
            )

        return text_chunks

    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            CodeLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a GitHub-style URL with file path and line numbers.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the code repository.

        Returns:
            URL with line number fragment (e.g., /file.py#L10-L20),
            or None if no location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
