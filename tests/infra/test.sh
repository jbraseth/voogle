#!/bin/bash
# Run tests in Docker using dedicated test image
# Works with existing running services - non-destructive
# Usage: ./test.sh [pytest args]
# Examples:
#   ./test.sh -v
#   ./test.sh -k test_vector -v
#   ./test.sh --ignore=tests/e2e -v
#   ./test.sh --cov=src/voogle --cov-report=html
#
# Test artifacts are always saved to tests/test_results/:
#   - test-results.xml (JUnit XML report)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOTDIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SCRIPT_DIR"

# Source common environment variables
source ./common_env.sh

# Use both compose files (base + test override)
COMPOSE_FILES="-f ../../infra/development/compose.yml -f compose.test.yml"

# Ensure test results directory exists (absolute path)
mkdir -p "$ROOTDIR/tests/test_results"

# Default pytest args with JUnit XML output (absolute path inside container maps to /app)
DEFAULT_ARGS="--junit-xml=/app/tests/test_results/test-results.xml"

# If user provided args, append them; otherwise use -v as default
if [ $# -eq 0 ]; then
    PYTEST_ARGS="$DEFAULT_ARGS -v"
else
    PYTEST_ARGS="$DEFAULT_ARGS $*"
fi

echo "Running tests..."
echo "  JUnit XML: $ROOTDIR/tests/test_results/test-results.xml"
echo ""

docker compose $COMPOSE_FILES run --rm --no-deps \
  $DOCKER_ENV \
  test -c "pytest $PYTEST_ARGS"
