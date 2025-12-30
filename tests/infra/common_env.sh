#!/bin/bash
# Common environment variables for Docker Compose commands
# Source this file in scripts that need consistent environment setup

# Docker environment variables to pass to containers
export DOCKER_ENV="\
-e ENVIRONMENT=test \
-e PYTHONPATH=/app/tests:/backend/src \
"
