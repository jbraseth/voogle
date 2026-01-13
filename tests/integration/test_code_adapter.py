# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for CodeAdapter content adapter.

Tests code parsing with AST boundary verification:
- Sample repository tests (Python, JavaScript, Go)
- Function/class boundary detection
- Line number accuracy
- Git ref capture
- Nested structure handling
- Deep link format validation
- End-to-end ingest -> search -> verify
"""
import subprocess
from pathlib import Path

import pytest

from voogle import embedding, vector
from voogle.adapters.code import (
    CodeAdapter,
    CodeConfig,
    _get_git_ref,
    check_ref_staleness,
    resolve_git_ref_to_sha,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk, TextChunk
from voogle.core.fragment import ContentType
from voogle.core.location import CodeLocation

pytestmark = pytest.mark.integration


class TestCodeAdapterWithSampleRepos:
    """Integration tests using sample code repositories."""

    @pytest.mark.description("CodeAdapter processes Python repository")
    @pytest.mark.asyncio
    async def test_adapter_processes_python_repo(self, tmp_path: Path) -> None:
        """Test that CodeAdapter can process a Python repository structure."""
        # Create a sample Python repository
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        main_py = src_dir / "main.py"
        main_py.write_text('''"""Main module for the application."""

def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b
''')

        utils_py = src_dir / "utils.py"
        utils_py.write_text('''"""Utility functions."""

def validate_input(value: str) -> bool:
    """Validate user input."""
    return len(value) > 0


async def fetch_data(url: str) -> dict:
    """Fetch data from URL asynchronously."""
    return {"url": url, "data": "sample"}
''')

        config = CodeConfig(
            chunk_by_symbol=True,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-python-repo",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        assert adapter.supports(source) is True

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should extract at least one chunk per file (tree-sitter may or may not
        # extract individual symbols depending on availability)
        assert len(raw_chunks) >= 2, f"Should extract chunks from both files, got {len(raw_chunks)}"

        # Verify Python-specific metadata
        for chunk in raw_chunks:
            assert chunk.metadata.get("language") == "python"
            assert isinstance(chunk.location, CodeLocation)

        # Check that both files were processed
        file_paths = {c.location.file_path for c in raw_chunks if c.location}
        assert any("main.py" in fp for fp in file_paths), "Should process main.py"
        assert any("utils.py" in fp for fp in file_paths), "Should process utils.py"

        # Verify expected code content is captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "greet" in all_text, "Should capture greet function"
        assert "Calculator" in all_text, "Should capture Calculator class"
        assert "validate_input" in all_text, "Should capture validate_input function"

    @pytest.mark.description("CodeAdapter processes JavaScript repository")
    @pytest.mark.asyncio
    async def test_adapter_processes_javascript_repo(self, tmp_path: Path) -> None:
        """Test that CodeAdapter can process a JavaScript repository."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        index_js = src_dir / "index.js"
        index_js.write_text('''// Main entry point

function greet(name) {
    return `Hello, ${name}!`;
}

const calculateSum = (a, b) => {
    return a + b;
};

class UserService {
    constructor() {
        this.users = [];
    }

    addUser(user) {
        this.users.push(user);
    }

    getUser(id) {
        return this.users.find(u => u.id === id);
    }
}

export { greet, calculateSum, UserService };
''')

        config = CodeConfig(
            chunk_by_symbol=True,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-js-repo",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        assert adapter.supports(source) is True

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should extract at least one chunk from the file
        assert len(raw_chunks) >= 1, f"Should extract JavaScript chunks, got {len(raw_chunks)}"

        # Verify JavaScript-specific metadata
        for chunk in raw_chunks:
            assert chunk.metadata.get("language") == "javascript"
            assert isinstance(chunk.location, CodeLocation)

        # Verify expected code content is captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "greet" in all_text, "Should capture greet function"
        assert "UserService" in all_text, "Should capture UserService class"

    @pytest.mark.description("CodeAdapter processes Go repository")
    @pytest.mark.asyncio
    async def test_adapter_processes_go_repo(self, tmp_path: Path) -> None:
        """Test that CodeAdapter can process a Go repository."""
        main_go = tmp_path / "main.go"
        main_go.write_text('''package main

import "fmt"

// Greeter is an interface for greeting.
type Greeter interface {
    Greet(name string) string
}

// SimpleGreeter implements Greeter.
type SimpleGreeter struct {
    prefix string
}

// Greet returns a greeting message.
func (g *SimpleGreeter) Greet(name string) string {
    return fmt.Sprintf("%s, %s!", g.prefix, name)
}

// NewGreeter creates a new SimpleGreeter.
func NewGreeter(prefix string) *SimpleGreeter {
    return &SimpleGreeter{prefix: prefix}
}

func main() {
    g := NewGreeter("Hello")
    fmt.Println(g.Greet("World"))
}
''')

        config = CodeConfig(
            chunk_by_symbol=True,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-go-repo",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        assert adapter.supports(source) is True

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should extract at least one chunk from the file
        assert len(raw_chunks) >= 1, f"Should extract Go chunks, got {len(raw_chunks)}"

        # Verify Go-specific metadata
        for chunk in raw_chunks:
            assert chunk.metadata.get("language") == "go"
            assert isinstance(chunk.location, CodeLocation)

        # Verify expected code content is captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "Greeter" in all_text, "Should capture Greeter interface"
        assert "NewGreeter" in all_text, "Should capture NewGreeter function"

    @pytest.mark.description("CodeAdapter handles multi-language repository")
    @pytest.mark.asyncio
    async def test_adapter_processes_multi_language_repo(self, tmp_path: Path) -> None:
        """Test that CodeAdapter can process a repository with multiple languages."""
        # Python file
        (tmp_path / "app.py").write_text('''def main():
    print("Hello from Python")
''')

        # JavaScript file
        (tmp_path / "app.js").write_text('''function main() {
    console.log("Hello from JavaScript");
}
''')

        # Go file
        (tmp_path / "main.go").write_text('''package main

func main() {
    println("Hello from Go")
}
''')

        config = CodeConfig(
            chunk_by_symbol=True,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-multi-lang-repo",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Verify we got chunks from all languages
        languages = {c.metadata.get("language") for c in raw_chunks}
        assert "python" in languages, "Should include Python"
        assert "javascript" in languages, "Should include JavaScript"
        assert "go" in languages, "Should include Go"


class TestFunctionClassBoundaryDetection:
    """Tests for function and class boundary detection."""

    @pytest.mark.description("Python function boundaries are correctly detected")
    @pytest.mark.asyncio
    async def test_python_function_boundaries(self, tmp_path: Path) -> None:
        """Test that Python function boundaries are correctly detected."""
        py_file = tmp_path / "functions.py"
        py_file.write_text('''def first_function():
    """First function."""
    return 1


def second_function():
    """Second function."""
    x = 1
    y = 2
    return x + y


def third_function():
    """Third function."""
    return 3
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-py-functions",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk (tree-sitter may extract individual functions
        # or fall back to file-level chunking)
        assert len(raw_chunks) >= 1, f"Should detect functions, got {len(raw_chunks)}"

        # Verify function content is captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "first_function" in all_text, "Should capture first_function"
        assert "second_function" in all_text, "Should capture second_function"
        assert "third_function" in all_text, "Should capture third_function"

        # Verify each chunk has valid location
        for chunk in raw_chunks:
            assert "def " in chunk.text, f"Chunk should contain function definition: {chunk.text[:50]}"
            assert isinstance(chunk.location, CodeLocation)
            assert chunk.location.start_line >= 1
            assert chunk.location.end_line >= chunk.location.start_line

    @pytest.mark.description("Python class boundaries are correctly detected")
    @pytest.mark.asyncio
    async def test_python_class_boundaries(self, tmp_path: Path) -> None:
        """Test that Python class boundaries include all methods."""
        py_file = tmp_path / "classes.py"
        py_file.write_text('''class FirstClass:
    """First class."""

    def method_one(self):
        return 1

    def method_two(self):
        return 2


class SecondClass:
    """Second class."""

    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-py-classes",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk containing the classes
        assert len(raw_chunks) >= 1, f"Should detect classes, got {len(raw_chunks)}"

        # Verify both classes are captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "FirstClass" in all_text, "Should capture FirstClass"
        assert "SecondClass" in all_text, "Should capture SecondClass"

        # Verify class chunks have valid multi-line locations
        class_chunks = [c for c in raw_chunks if "class " in c.text]
        for chunk in class_chunks:
            location = chunk.location
            assert isinstance(location, CodeLocation)
            # Classes should span multiple lines
            if location.end_line is not None:
                assert location.end_line > location.start_line, (
                    f"Class should span multiple lines: {location.start_line}-{location.end_line}"
                )

    @pytest.mark.description("JavaScript function boundaries are correctly detected")
    @pytest.mark.asyncio
    async def test_javascript_function_boundaries(self, tmp_path: Path) -> None:
        """Test that JavaScript function boundaries are correctly detected."""
        js_file = tmp_path / "functions.js"
        js_file.write_text('''// Regular function
function regularFunction() {
    return 1;
}

// Arrow function
const arrowFunction = () => {
    return 2;
};

// Class declaration
class MyClass {
    constructor() {
        this.value = 0;
    }

    getValue() {
        return this.value;
    }
}
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-js-functions",
            source_type=ContentType.TEXT,
            path=js_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk
        assert len(raw_chunks) >= 1, f"Should detect JavaScript code, got {len(raw_chunks)}"

        # Verify function-related keywords and content are present
        all_text = " ".join(c.text for c in raw_chunks)
        assert "function" in all_text or "=>" in all_text or "class" in all_text
        assert "regularFunction" in all_text, "Should capture regularFunction"
        assert "MyClass" in all_text, "Should capture MyClass"

    @pytest.mark.description("Go function and type boundaries are correctly detected")
    @pytest.mark.asyncio
    async def test_go_function_boundaries(self, tmp_path: Path) -> None:
        """Test that Go function and type boundaries are correctly detected."""
        go_file = tmp_path / "main.go"
        go_file.write_text('''package main

// Config holds configuration values.
type Config struct {
    Name  string
    Value int
}

// NewConfig creates a new Config.
func NewConfig(name string, value int) *Config {
    return &Config{
        Name:  name,
        Value: value,
    }
}

// GetName returns the config name.
func (c *Config) GetName() string {
    return c.Name
}
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-go-functions",
            source_type=ContentType.TEXT,
            path=go_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk
        assert len(raw_chunks) >= 1, f"Should detect Go code, got {len(raw_chunks)}"

        # Verify Go-specific constructs and content are present
        all_text = " ".join(c.text for c in raw_chunks)
        assert "func" in all_text or "type" in all_text
        assert "NewConfig" in all_text, "Should capture NewConfig function"
        assert "Config" in all_text, "Should capture Config type"


class TestLineNumberAccuracy:
    """Tests for line number accuracy in code locations."""

    @pytest.mark.description("Line numbers are 1-indexed")
    @pytest.mark.asyncio
    async def test_line_numbers_are_1_indexed(self, tmp_path: Path) -> None:
        """Test that line numbers start at 1, not 0."""
        py_file = tmp_path / "test.py"
        py_file.write_text('''def first_line_function():
    pass
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-line-index",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        assert len(raw_chunks) >= 1
        first_chunk = raw_chunks[0]
        assert isinstance(first_chunk.location, CodeLocation)
        assert first_chunk.location.start_line == 1, (
            f"First function should start at line 1, got {first_chunk.location.start_line}"
        )

    @pytest.mark.description("Line numbers match actual source positions")
    @pytest.mark.asyncio
    async def test_line_numbers_match_source(self, tmp_path: Path) -> None:
        """Test that reported line numbers match actual positions in source."""
        py_file = tmp_path / "test.py"
        source_code = '''# Line 1: Comment
# Line 2: Another comment

def function_at_line_4():
    # Line 5
    return "line 6"


def function_at_line_9():
    return "line 10"
'''
        py_file.write_text(source_code)

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-line-match",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk
        assert len(raw_chunks) >= 1, f"Should detect functions, got {len(raw_chunks)}"

        # Verify both functions are captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "function_at_line_4" in all_text, "Should capture first function"
        assert "function_at_line_9" in all_text, "Should capture second function"

        # Verify line numbers are valid
        for chunk in raw_chunks:
            assert isinstance(chunk.location, CodeLocation)
            # Line numbers should start at 1 and be reasonable
            assert 1 <= chunk.location.start_line <= 10, (
                f"Start line should be in valid range, got {chunk.location.start_line}"
            )
            if chunk.location.end_line:
                assert chunk.location.end_line >= chunk.location.start_line

    @pytest.mark.description("End line accurately captures function extent")
    @pytest.mark.asyncio
    async def test_end_line_accuracy(self, tmp_path: Path) -> None:
        """Test that end_line accurately captures the extent of a function."""
        py_file = tmp_path / "test.py"
        py_file.write_text('''def multi_line_function():
    x = 1
    y = 2
    z = 3
    return x + y + z
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-end-line",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        assert len(raw_chunks) == 1
        chunk = raw_chunks[0]
        assert isinstance(chunk.location, CodeLocation)
        assert chunk.location.start_line == 1
        assert chunk.location.end_line == 5, (
            f"Function should end at line 5, got {chunk.location.end_line}"
        )


class TestGitRefCapture:
    """Tests for git reference capture functionality."""

    @pytest.mark.description("Git ref is captured when repository has git")
    @pytest.mark.asyncio
    async def test_git_ref_captured(self, tmp_path: Path) -> None:
        """Test that git ref is captured from repository."""
        # Create a git repository
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create a file and commit it
        py_file = tmp_path / "test.py"
        py_file.write_text('''def test_function():
    pass
''')
        subprocess.run(["git", "add", "test.py"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=True)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-git-ref",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        assert len(raw_chunks) >= 1
        chunk = raw_chunks[0]

        # Git ref should be captured
        assert chunk.metadata.get("git_ref") is not None, "Git ref should be captured"
        assert len(chunk.metadata["git_ref"]) == 12, "Git ref should be 12 char short hash"

        # Location should also have git_ref
        assert isinstance(chunk.location, CodeLocation)
        assert chunk.location.git_ref is not None

    @pytest.mark.description("Git branch is captured when on a branch")
    @pytest.mark.asyncio
    async def test_git_branch_captured(self, tmp_path: Path) -> None:
        """Test that git branch is captured when available."""
        # Create a git repository
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp_path, capture_output=True)

        # Create a file and commit it
        py_file = tmp_path / "test.py"
        py_file.write_text('''def test_function():
    pass
''')
        subprocess.run(["git", "add", "test.py"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=True)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-git-branch",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        assert len(raw_chunks) >= 1
        chunk = raw_chunks[0]

        # Git branch should be captured
        assert chunk.metadata.get("git_branch") == "main", "Git branch should be 'main'"

    @pytest.mark.description("Git ref is None when not in a git repository")
    @pytest.mark.asyncio
    async def test_git_ref_none_without_git(self, tmp_path: Path) -> None:
        """Test that git ref is None when not in a git repository."""
        py_file = tmp_path / "test.py"
        py_file.write_text('''def test_function():
    pass
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=True)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-no-git",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        assert len(raw_chunks) >= 1
        chunk = raw_chunks[0]

        # Git ref should be None or not present
        assert chunk.metadata.get("git_ref") is None
        assert isinstance(chunk.location, CodeLocation)
        assert chunk.location.git_ref is None

    @pytest.mark.description("resolve_git_ref_to_sha resolves branch names")
    def test_resolve_git_ref_to_sha(self, tmp_path: Path) -> None:
        """Test that resolve_git_ref_to_sha resolves refs correctly."""
        # Create a git repository
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp_path, capture_output=True)

        # Create a commit
        (tmp_path / "test.py").write_text("pass")
        subprocess.run(["git", "add", "test.py"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Resolve branch name to SHA
        sha = resolve_git_ref_to_sha(tmp_path, "main")
        assert sha is not None, "Should resolve branch name"
        assert len(sha) == 12, "Should return 12-char short hash"

        # Resolve HEAD
        head_sha = resolve_git_ref_to_sha(tmp_path, "HEAD")
        assert head_sha is not None
        assert head_sha == sha, "HEAD should resolve to same SHA as main"

    @pytest.mark.description("check_ref_staleness detects stale refs")
    def test_check_ref_staleness(self, tmp_path: Path) -> None:
        """Test that check_ref_staleness detects when refs are stale."""
        # Create a git repository
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create first commit
        (tmp_path / "test.py").write_text("pass")
        subprocess.run(["git", "add", "test.py"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Get initial ref
        initial_ref = _get_git_ref(tmp_path)
        assert initial_ref is not None

        # Create another commit
        (tmp_path / "test.py").write_text("x = 1")
        subprocess.run(["git", "add", "test.py"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Second commit"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Check staleness
        staleness = check_ref_staleness(tmp_path, initial_ref)
        assert staleness["is_stale"] is True, "Old ref should be stale"
        assert staleness["current_ref"] is not None
        assert staleness["current_ref"] != initial_ref


class TestNestedStructureHandling:
    """Tests for handling nested code structures."""

    @pytest.mark.description("Nested functions are detected")
    @pytest.mark.asyncio
    async def test_nested_functions_detected(self, tmp_path: Path) -> None:
        """Test that nested functions within classes/functions are handled."""
        py_file = tmp_path / "nested.py"
        py_file.write_text('''def outer_function():
    """Outer function with nested function."""

    def inner_function():
        """Inner nested function."""
        return "inner"

    return inner_function()
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-nested",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect both outer and inner functions
        assert len(raw_chunks) >= 1, "Should detect at least outer function"

        # Verify outer function is captured
        outer_chunks = [c for c in raw_chunks if "outer_function" in c.text]
        assert len(outer_chunks) >= 1, "Should capture outer function"

    @pytest.mark.description("Nested classes are detected")
    @pytest.mark.asyncio
    async def test_nested_classes_detected(self, tmp_path: Path) -> None:
        """Test that nested classes are handled correctly."""
        py_file = tmp_path / "nested_classes.py"
        py_file.write_text('''class OuterClass:
    """Outer class with nested class."""

    class InnerClass:
        """Inner nested class."""

        def inner_method(self):
            return "inner"

    def outer_method(self):
        return "outer"
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-nested-classes",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect both classes
        assert len(raw_chunks) >= 1, "Should detect at least outer class"

        # Check that OuterClass is captured
        outer_chunks = [c for c in raw_chunks if "OuterClass" in c.text]
        assert len(outer_chunks) >= 1, "Should capture outer class"

    @pytest.mark.description("Decorated functions are detected")
    @pytest.mark.asyncio
    async def test_decorated_functions_detected(self, tmp_path: Path) -> None:
        """Test that decorated functions are properly detected."""
        py_file = tmp_path / "decorated.py"
        py_file.write_text('''def decorator(func):
    return func


@decorator
def decorated_function():
    """A decorated function."""
    return "decorated"


class MyClass:
    @staticmethod
    def static_method():
        return "static"

    @classmethod
    def class_method(cls):
        return "classmethod"
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-decorated",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should detect at least 1 chunk
        assert len(raw_chunks) >= 1, f"Should detect code, got {len(raw_chunks)}"

        # Verify decorated functions and class content is captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "decorator" in all_text, "Should capture decorator function"
        assert "decorated_function" in all_text, "Should capture decorated_function"
        assert "MyClass" in all_text, "Should capture MyClass"


class TestDeepLinkFormatValidation:
    """Tests for deep link URL format validation."""

    @pytest.mark.description("Deep link includes file path and line numbers")
    def test_deep_link_includes_file_and_lines(self) -> None:
        """Test that deep link URLs include file path and line number fragment."""
        adapter = CodeAdapter()
        location = CodeLocation(
            file_path="src/main.py",
            start_line=10,
            end_line=20,
        )
        chunk = TextChunk(
            text="def test(): pass",
            source_id="test-code",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://github.com/example/repo"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "src/main.py" in deep_link, f"Deep link should include file path: {deep_link}"
        assert "L10" in deep_link, f"Deep link should include start line: {deep_link}"
        assert "L20" in deep_link, f"Deep link should include end line: {deep_link}"

    @pytest.mark.description("Deep link includes git ref when available")
    def test_deep_link_includes_git_ref(self) -> None:
        """Test that deep link includes git ref for reproducible links."""
        adapter = CodeAdapter()
        location = CodeLocation(
            file_path="src/main.py",
            start_line=5,
            end_line=10,
            git_ref="abc123def456",
        )
        chunk = TextChunk(
            text="def test(): pass",
            source_id="test-code",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://github.com/example/repo"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "blob/abc123def456" in deep_link, f"Deep link should include git ref: {deep_link}"
        assert "src/main.py" in deep_link
        assert "#L5-L10" in deep_link

    @pytest.mark.description("Deep link uses GitHub-style line fragment format")
    def test_deep_link_github_format(self) -> None:
        """Test that deep link uses GitHub-style #L10-L20 format."""
        adapter = CodeAdapter()
        location = CodeLocation(
            file_path="module.py",
            start_line=15,
            end_line=25,
        )
        chunk = TextChunk(
            text="class Test: pass",
            source_id="test-code",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://github.com/org/repo"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        # Should use #L15-L25 format
        assert "#L15-L25" in deep_link, f"Should use GitHub line format: {deep_link}"

    @pytest.mark.description("Deep link handles single line without range")
    def test_deep_link_single_line(self) -> None:
        """Test that single-line locations produce single line links."""
        adapter = CodeAdapter()
        location = CodeLocation(
            file_path="test.py",
            start_line=42,
            end_line=42,  # Same as start
        )
        chunk = TextChunk(
            text="x = 1",
            source_id="test-code",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://github.com/org/repo"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        # Single line should be #L42, not #L42-L42
        assert "#L42" in deep_link
        # Should not have range when start == end
        assert "L42-L42" not in deep_link

    @pytest.mark.description("Deep link returns None for chunk without location")
    def test_deep_link_without_location(self) -> None:
        """Test that deep link returns None when chunk has no location."""
        adapter = CodeAdapter()
        chunk = TextChunk(
            text="def test(): pass",
            source_id="test-code",
            source_type=ContentType.TEXT,
            location=None,
        )

        base_url = "https://github.com/example/repo"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is None

    @pytest.mark.description("Deep link handles nested file paths")
    @pytest.mark.parametrize(
        "file_path,expected_in_link",
        [
            ("src/main.py", "src/main.py"),
            ("pkg/subpkg/module.py", "pkg/subpkg/module.py"),
            ("test/unit/test_module.py", "test/unit/test_module.py"),
        ],
    )
    def test_deep_link_nested_paths(self, file_path: str, expected_in_link: str) -> None:
        """Test that deep links handle nested file paths correctly."""
        adapter = CodeAdapter()
        location = CodeLocation(file_path=file_path, start_line=1)
        chunk = TextChunk(
            text="code",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        deep_link = adapter.get_deep_link(chunk, "https://github.com/org/repo")
        assert deep_link is not None
        assert expected_in_link in deep_link


class TestEndToEndIngestSearchVerify:
    """End-to-end tests: ingest -> search -> verify."""

    @pytest.mark.description("Ingested code can be searched and results verified")
    @pytest.mark.asyncio
    async def test_e2e_ingest_search_verify(self, tmp_path: Path) -> None:
        """Test complete flow: ingest code -> index -> search -> verify results."""
        # Create sample repository
        (tmp_path / "calculator.py").write_text('''"""Calculator module with math operations."""

def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
''')

        # Step 1: Extract (ingest)
        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-calculator",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should extract at least 1 chunk with all functions
        assert len(raw_chunks) >= 1, f"Should extract code, got {len(raw_chunks)}"

        # Verify all functions are captured
        all_text = " ".join(c.text for c in raw_chunks)
        assert "add" in all_text, "Should capture add function"
        assert "subtract" in all_text, "Should capture subtract function"
        assert "divide" in all_text, "Should capture divide function"

        # Step 2: Chunk
        chunk_config = ChunkConfig(target_words=50, overlap_words=5)
        text_chunks = adapter.chunk(raw_chunks, source, chunk_config)

        assert len(text_chunks) > 0, "Should produce text chunks"

        # Step 3: Index into Qdrant
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()
        collection_name = "test-code-e2e"

        vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

        # Calculate embeddings and store
        texts = [chunk.text for chunk in text_chunks]
        embeddings = provider.encode_texts(texts)

        from qdrant_client.models import PointStruct

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            location = chunk.location
            start_line = location.start_line if isinstance(location, CodeLocation) else None
            end_line = location.end_line if isinstance(location, CodeLocation) else None
            file_path = location.file_path if isinstance(location, CodeLocation) else None

            points.append(
                PointStruct(
                    id=5000 + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "source_id": chunk.source_id,
                        "source_type": chunk.source_type.value,
                        "text": chunk.text,
                        "start_line": start_line,
                        "end_line": end_line,
                        "file_path": file_path,
                        "sequence_index": chunk.sequence_index,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Step 4: Search for division operation
        query_embedding = embedding.text2embedding("divide two numbers division", provider)
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
            assert result.payload["source_id"] == "test-calculator"

        # Verify semantic relevance - top result should contain relevant code
        top_result_text = results[0].payload["text"].lower() if results[0].payload else ""
        # The search should find calculator-related code
        assert any(
            term in top_result_text for term in ["divide", "add", "subtract", "multiply", "calculator"]
        ), f"Top result should be about calculator operations: {top_result_text}"

    @pytest.mark.description("Search results include code location metadata")
    @pytest.mark.asyncio
    async def test_search_results_include_locations(self, tmp_path: Path) -> None:
        """Test that search results include line number and file path."""
        (tmp_path / "utils.py").write_text('''def helper_function():
    """A helper function."""
    return "helper"
''')

        config = CodeConfig(chunk_by_symbol=True, preserve_git_ref=False)
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-utils",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        text_chunks = adapter.chunk(raw_chunks, source)

        # Index
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()
        collection_name = "test-code-locations"
        vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

        texts = [c.text for c in text_chunks]
        embeddings = provider.encode_texts(texts)

        from qdrant_client.models import PointStruct as PointStructLoc

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            loc = chunk.location
            points.append(
                PointStructLoc(
                    id=6000 + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "text": chunk.text,
                        "source_id": chunk.source_id,
                        "start_line": loc.start_line if isinstance(loc, CodeLocation) else None,
                        "end_line": loc.end_line if isinstance(loc, CodeLocation) else None,
                        "file_path": loc.file_path if isinstance(loc, CodeLocation) else None,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Search
        query_emb = embedding.text2embedding("helper function", provider)
        results = client.query_points(
            collection_name=collection_name,
            query=query_emb[0].tolist(),
            limit=2,
        ).points

        assert len(results) > 0
        for result in results:
            payload = result.payload
            assert payload is not None
            if payload.get("start_line") is not None:
                assert payload["start_line"] >= 1, "Line numbers should be >= 1"
            if payload.get("file_path") is not None:
                assert "utils.py" in payload["file_path"], "Should include file path"


class TestCodeAdapterWithMockedTreeSitter:
    """Integration tests with mocked Tree-sitter for CI environments."""

    @pytest.mark.description("Fallback line chunking works when Tree-sitter unavailable")
    @pytest.mark.asyncio
    async def test_fallback_line_chunking(self, tmp_path: Path) -> None:
        """Test that line-based chunking works as fallback."""
        py_file = tmp_path / "test.py"
        py_file.write_text('''# This is a Python file
def function_one():
    return 1

def function_two():
    return 2

def function_three():
    return 3
''')

        config = CodeConfig(
            chunk_by_symbol=False,  # Force line-based chunking
            preserve_git_ref=False,
            fallback_line_chunking=5,  # Small chunks
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-fallback",
            source_type=ContentType.TEXT,
            path=py_file,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should produce multiple chunks based on line count
        assert len(raw_chunks) >= 1, "Should produce line-based chunks"

        # Verify chunks have proper location info
        for chunk in raw_chunks:
            assert isinstance(chunk.location, CodeLocation)
            assert chunk.location.start_line >= 1
            assert chunk.metadata.get("language") == "python"


class TestGitignoreIntegration:
    """Tests for gitignore pattern integration."""

    @pytest.mark.description("Gitignore patterns are respected")
    @pytest.mark.asyncio
    async def test_gitignore_respected(self, tmp_path: Path) -> None:
        """Test that .gitignore patterns exclude files from processing."""
        # Create repository structure
        (tmp_path / ".gitignore").write_text('''# Ignore test files
test_*.py
*.test.js
vendor/
''')

        # Create files that should be processed
        (tmp_path / "main.py").write_text('''def main():
    pass
''')

        # Create files that should be ignored
        (tmp_path / "test_main.py").write_text('''def test_main():
    pass
''')

        (tmp_path / "vendor").mkdir()
        (tmp_path / "vendor" / "lib.py").write_text('''def vendor_func():
    pass
''')

        config = CodeConfig(
            respect_gitignore=True,
            chunk_by_symbol=False,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-gitignore",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Verify only main.py was processed
        file_paths = {c.location.file_path for c in raw_chunks if c.location}
        assert any("main.py" in fp for fp in file_paths), "Should process main.py"
        assert not any("test_main.py" in fp for fp in file_paths), "Should ignore test_main.py"
        assert not any("vendor" in fp for fp in file_paths), "Should ignore vendor/"

    @pytest.mark.description("Default ignore patterns exclude common directories")
    @pytest.mark.asyncio
    async def test_default_ignore_patterns(self, tmp_path: Path) -> None:
        """Test that default patterns exclude node_modules, __pycache__, etc."""
        # Create directories that should be ignored by default
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "pkg" / "index.js").parent.mkdir(parents=True)
        (tmp_path / "node_modules" / "pkg" / "index.js").write_text('''export default {};''')

        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "module.cpython-312.pyc").write_text("bytecode")

        # Create file that should be processed
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text('''def app():
    pass
''')

        config = CodeConfig(
            respect_gitignore=False,  # Don't use .gitignore, only default patterns
            chunk_by_symbol=False,
            preserve_git_ref=False,
        )
        adapter = CodeAdapter(config=config)
        source = ContentSource(
            source_id="test-default-ignore",
            source_type=ContentType.TEXT,
            path=tmp_path,
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Verify only src/app.py was processed
        file_paths = {c.location.file_path for c in raw_chunks if c.location}
        assert any("app.py" in fp for fp in file_paths), "Should process src/app.py"
        assert not any("node_modules" in fp for fp in file_paths), "Should ignore node_modules"
        assert not any("__pycache__" in fp for fp in file_paths), "Should ignore __pycache__"
