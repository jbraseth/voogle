# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

help:
	@echo "voogle - podcast search engine - backend Python project     "
	@echo "                                                            "
	@echo "Available targets:                                          "
	@echo "    - help: show this help message                          "
	@echo "    - start: run the back-end                               "
	@echo "    - gen-migrations: generate new migrations               "
	@echo "    - migrate: apply all migrations                         "

start:
	@echo "running voogle (locally) in port 8080..."
	uvicorn src.voogle.main:app --reload --host 0.0.0.0 --port 8080


gen-migrations:
	@read -p "Enter summary message for the migration:" msg; \
	alembic revision --autogenerate -m "$$msg"

migrate:
	alembic upgrade head
