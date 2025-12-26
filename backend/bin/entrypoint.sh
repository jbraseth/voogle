#!/usr/bin/env bash

echo "Voogle initialization..."
alembic upgrade head  # run migrations on sqlite database
voogle-management --create-admin # create, if needed, the admin user
exec "$@" # run the CMD passed as command-line arguments
