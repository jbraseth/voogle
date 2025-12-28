#!/bin/bash
# Run tests in Docker using dedicated test image
# Ensures full stack (backend + frontend) is running for e2e tests
# Usage: ./test.sh [pytest args]
# Examples:
#   ./test.sh -v
#   ./test.sh -k test_vector -v
#   ./test.sh --cov=src/voogle --cov-report=html

set -e

cd "$(dirname "$0")"

# Use both compose files (base + test override)
COMPOSE_FILES="-f compose.yml -f compose.test.yml"

# Build test image quietly (only show output on error)
docker compose $COMPOSE_FILES build test >/dev/null 2>&1 || docker compose $COMPOSE_FILES build test

# Start services (using --no-recreate to avoid conflicts with existing containers)
# This makes the script fast and idempotent - won't touch already-running containers
echo "Ensuring services are running..."
docker compose $COMPOSE_FILES up -d --no-recreate --remove-orphans \
  redis qdrant backend frontend >/dev/null 2>&1 || true

# Run tests with provided args
PYTEST_ARGS="${*:--v}"

echo "Running tests..."
docker compose $COMPOSE_FILES run --rm test \
  -c "ENVIRONMENT=test pytest $PYTEST_ARGS" 2>&1 | grep -v "^voogle_"

# Note: We don't stop services - they may be used by other processes
