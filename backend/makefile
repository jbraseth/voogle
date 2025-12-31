# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

help:
	@echo "voogle - podcast search engine - backend Python project     "
	@echo "                                                            "
	@echo "Available targets:                                          "
	@echo "    - help: show this help message                          "
	@echo "    - start: run the back-end                               "
	@echo "    - test: run pytest (excluding e2e)                      "
	@echo "    - test-all: run all tests including e2e                 "
	@echo "    - lint: run ruff linter                                 "
	@echo "    - lint-fix: run ruff with auto-fix                      "
	@echo "    - type-check: run pyright type checker                  "
	@echo "    - gen-migrations: generate new migrations               "
	@echo "    - migrate: apply all migrations                         "
	@echo "    - install-dev: install package with dev dependencies    "

start:
	@echo "running voogle (locally) in port 8080..."
	uvicorn src.voogle.main:app --reload --host 0.0.0.0 --port 8080

test:
	cd .. && pytest tests/ -v --ignore=tests/e2e

test-all:
	cd .. && pytest tests/ -v

lint:
	ruff check .

lint-fix:
	ruff check . --fix

type-check:
	pyright src/

gen-migrations:
	@read -p "Enter summary message for the migration:" msg; \
	alembic revision --autogenerate -m "$$msg"

migrate:
	alembic upgrade head

install-dev:
	pip install -e .[dev]
