help:
	@echo "Voogle Infrastructure                                      "
	@echo "\nAvailable targets for development: "
	@echo " - make dev-build: build Docker images in development mode        "
	@echo " - make dev-run: start all services in development mode    "
	@echo "\nAvailable targets for production: "
	@echo " - make prod-build: build Docker images in production mode        "
	@echo " - make prod-run: start all services in production mode    "


test-env-dev:
	@echo "checking if .env exists in ./development, you should have created it"
	test -s ./development/.env

test-env-prod:
	@echo "checking if .env exists in ./production, you should have created it"
	test -s ./production/.env

dev-build: test-env-dev
	cd development/ && docker compose build

dev-rebuild: test-env-dev
	cd development/ && docker compose build --no-cache

dev-run: test-env-dev
	cd development/ && docker compose up

prod-build: test-env-prod
	cd production/ && docker compose build --no-cache

prod-run: test-env-prod
	cd production/ && docker compose up
