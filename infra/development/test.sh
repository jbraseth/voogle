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

# Build test image (suppress unless error)
docker compose $COMPOSE_FILES build test >/dev/null 2>&1 || docker compose $COMPOSE_FILES build test

# Ensure full stack is running (for e2e tests)
# Start in dependency order: redis -> qdrant -> backend -> frontend
for service in redis qdrant backend frontend; do
    if ! docker ps --format '{{.Names}}' | grep -q "voogle_${service}_1"; then
        docker compose -f compose.yml up -d --no-recreate $service >/dev/null 2>&1
    fi
done

# Wait for backend to be healthy
echo "Waiting for services to be ready..."
timeout 60 bash -c 'until docker exec voogle_backend_1 curl -sf http://localhost:80/app/version >/dev/null 2>&1; do sleep 1; done' || {
    echo "Backend failed to start"
    exit 1
}

# Run tests with provided args
PYTEST_ARGS="${*:--v}"

docker compose $COMPOSE_FILES run --rm test \
  -c "ENVIRONMENT=test pytest $PYTEST_ARGS" 2>&1 | grep -v "^voogle_"

# Note: We don't stop services - they may be used by other processes
