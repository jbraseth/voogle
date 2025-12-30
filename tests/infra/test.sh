#!/bin/bash
# Run tests in Docker using dedicated test image
# Works with existing running services - non-destructive
# Usage: ./test.sh [pytest args]
# Examples:
#   ./test.sh -v
#   ./test.sh -k test_vector -v
#   ./test.sh -m e2e -v
#   ./test.sh --cov=src/voogle --cov-report=html
#
# Test artifacts are always saved to tests/test_results/:
#   - test-results.xml (JUnit XML report)
#   - videos/ (Playwright video recordings on failure)
#   - traces/ (Playwright trace files on failure)

set -e

cd "$(dirname "$0")"

# Source common environment variables
source ./common_env.sh

# Use both compose files (base + test override)
COMPOSE_FILES="-f ../../infra/development/compose.yml -f compose.test.yml"

# Ensure test results directories exist
mkdir -p ../test_results/videos
mkdir -p ../test_results/traces

# Default pytest args with JUnit XML output, video and tracing on failure
# These can be overridden by passing explicit args
DEFAULT_ARGS="--junit-xml=tests/test_results/test-results.xml"
DEFAULT_ARGS="$DEFAULT_ARGS --video=retain-on-failure"
DEFAULT_ARGS="$DEFAULT_ARGS --tracing=retain-on-failure"

# If user provided args, append them; otherwise use -v as default
if [ $# -eq 0 ]; then
    PYTEST_ARGS="$DEFAULT_ARGS -v"
else
    PYTEST_ARGS="$DEFAULT_ARGS $*"
fi

echo "Running tests..."
echo "  JUnit XML: tests/test_results/test-results.xml"
echo "  Videos: tests/test_results/videos/ (on failure)"
echo "  Traces: tests/test_results/traces/ (on failure)"
echo ""

docker compose $COMPOSE_FILES run --rm --no-deps \
  $DOCKER_ENV \
  test -c "pytest $PYTEST_ARGS"
