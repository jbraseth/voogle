#!/usr/bin/env bash
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

# Run linting in Docker container
# Usage: ./scripts/lint.sh [--fix]
#
# Options:
#   --fix    Auto-fix issues where possible
#
# Examples:
#   ./scripts/lint.sh          # Check for issues
#   ./scripts/lint.sh --fix    # Auto-fix issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

FIX_FLAG=""
if [[ "$1" == "--fix" ]]; then
    FIX_FLAG="--fix"
    shift
fi

echo "Building test image (used for linting)..."
docker build -t voogle-test -f tests/dockerfile .

echo "Running ruff..."
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace/backend \
    voogle-test ruff check $FIX_FLAG .

echo "Running pyright..."
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace/backend \
    voogle-test pyright src/

echo "All linting checks passed!"
