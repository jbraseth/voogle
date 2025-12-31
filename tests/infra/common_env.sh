#!/bin/bash
# Common environment variables for test scripts
# Source this file in scripts that need consistent environment setup

# Get project root relative to this file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Local environment variables
export ENVIRONMENT=test
export VOOGLE_ENVIRONMENT=test
export PYTHONPATH="$PROJECT_ROOT/tests:$PROJECT_ROOT/backend/src"

# Docker environment variables to pass to containers
export DOCKER_ENV="\
-e ENVIRONMENT=test \
-e VOOGLE_ENVIRONMENT=test \
-e VOOGLE_DATA_DIR=/tmp/voogle-test \
-e PYTHONPATH=/app/tests \
"
