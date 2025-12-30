#!/usr/bin/env bash
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

# Run tests in Docker container
# Usage: ./scripts/test.sh [pytest args...]
#
# Examples:
#   ./scripts/test.sh                    # Run all tests
#   ./scripts/test.sh -v                 # Verbose output
#   ./scripts/test.sh tests/test_api.py  # Run specific test file
#   ./scripts/test.sh -k "test_search"   # Run tests matching pattern

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Building test image..."
docker build -t voogle-test -f tests/dockerfile .

echo "Running tests..."
docker run --rm \
    -e VOOGLE_ENVIRONMENT=test \
    -e VOOGLE_DATA_DIR=/tmp/voogle-test \
    voogle-test pytest "$@"
